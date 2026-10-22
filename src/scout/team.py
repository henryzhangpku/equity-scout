"""The investor team: many independent investors vote, a fixed scorer keeps their record, and they
bring ideas of their own. The model proposes; code decides.

A single chat can play "value investor, then momentum trader", but it is one model in one conversation,
so the views stay correlated. Here each investor (src/scout/roster.json) is a config row:

* a style, a data diet (the only fields it is shown, so investors see different information), and either
  a model prompt (kind "llm", one separate call per investor) or a fixed rule (kind "code", no model);
* a vote per name: conviction in [-1, +1] (0 = abstain) with reasons. Every reason must name a field from
  that investor's diet and repeat its value exactly as shown, and every number in the reason must be one of
  the values shown; code deletes any reason that fails, and a vote with no surviving reason becomes an
  abstention. Code investors vote by their rule: a name that passes gets a conviction from its rank.

Two modes on one engine:

* Mode 1, an idea is tested: after a screen, each investor votes on the top names; `tally` counts the
  votes, weights each investor by its record, and counts investors whose past votes move together
  (copycats, correlation >= COPYCAT_CORR) as one voice.
* Mode 2, the team brings ideas: each proposing investor writes one screen in its style; code validates
  it, screens today's snapshot and backtests it (backtest.for_run, the same gates as every screen). Only
  an idea with an edge on that history is accepted; the team then votes on its names, and `brief` writes
  the morning brief with the accepted ideas and every rejected one with its reason.

Record: every vote goes into runs/votes.jsonl and every proposal into runs/proposals.jsonl, both
hash-chained (track.append_entry). `scorecards` marks each vote to market once its horizon has passed:
hit rate on excess return over SPY, mean conviction-weighted excess, t-stat and rank IC. An investor's
weight comes from that forward record once it has MIN_SCORED matured votes; before that a code investor
starts from its rule's backtest, and a model investor starts at 1.0 with "no record yet".
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .config import RUNS
from .llm import LLM, ReplayMiss, parse_json
from .narrative import numbers_in
from .report import fmt
from .screen import describe, rank, run_screen
from .spec import FIELDS, Spec, SpecError, schema_for_prompt, validate
from .track import append_entry, read_ledger, verify_chain

ROSTER = Path(__file__).with_name("roster.json")
VOTES = RUNS / "votes.jsonl"
PROPOSALS = RUNS / "proposals.jsonl"
SCORECARDS = RUNS / "scorecards.json"

MIN_SCORED = 10          # matured votes before the forward record sets an investor's weight
COPYCAT_CORR = 0.8       # past convictions this correlated: the two investors count as one voice
MIN_OVERLAP = 8          # shared votes needed before a correlation is trusted
MAX_LATE_DAYS = 3        # a vote recorded more than this many days after its as-of date is never scored
LEAN = 0.25              # weighted conviction needed for the team to lean one way
MIN_VOICES = 2           # independent voices needed before the team is said to lean either way
MAX_REASONS = 3
EDGE = "Edge on this history"


@dataclass(frozen=True)
class Investor:
    id: str
    name: str
    kind: str                  # llm | code
    style: str
    horizon_days: int
    proposes: bool
    fields: tuple = ()
    rule: dict | None = None

    def rule_spec(self) -> Spec:
        return validate(self.rule)


def load_roster(path: Path | None = None) -> list[Investor]:
    d = json.loads((path or ROSTER).read_text(encoding="utf-8"))
    out, problems, seen = [], [], set()
    for r in d["investors"]:
        inv = Investor(id=r["id"], name=r["name"], kind=r["kind"], style=r["style"],
                       horizon_days=int(r["horizon_days"]), proposes=bool(r.get("proposes")),
                       fields=tuple(r.get("fields", ())), rule=r.get("rule"))
        if inv.id in seen:
            problems.append(f"{inv.id}: duplicate id")
        seen.add(inv.id)
        if inv.kind not in ("llm", "code"):
            problems.append(f"{inv.id}: kind must be llm or code")
        if inv.kind == "llm" and not inv.fields:
            problems.append(f"{inv.id}: a model investor needs a data diet (fields)")
        problems += [f"{inv.id}: unknown field {f!r}" for f in inv.fields if f not in FIELDS]
        if inv.kind == "code":
            try:
                inv.rule_spec()
            except (SpecError, TypeError) as e:
                problems.append(f"{inv.id}: rule does not validate: {e}")
        out.append(inv)
    if problems:
        raise ValueError("roster is invalid: " + "; ".join(problems))
    return out


def roster_version(path: Path | None = None) -> str:
    return hashlib.sha256((path or ROSTER).read_bytes()).hexdigest()[:12]


def _value(field: str, v):
    """A snapshot value as a clean Python scalar (None when missing)."""
    if isinstance(v, np.generic):
        v = v.item()
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        return None
    if field in FIELDS and FIELDS[field].kind == "bool" and not isinstance(v, bool):
        return str(v).lower() == "true"
    return v


def shown(inv: Investor, row: dict) -> dict[str, str]:
    """What this investor is shown for one name: its diet only, formatted exactly as the report shows it."""
    return {f: fmt(f, _value(f, row.get(f))) for f in inv.fields}


# ---------------------------------------------------------------- mode 1: votes

VOTE_SYSTEM = """You are one investor on a team. Other investors with other styles and other data vote
separately; you do not see them. Your style:

{style}

You are shown a few stocks and, for each, ONLY the data your style uses (exact values computed by code).
For each stock give your conviction from -1 (strong sell or short) to +1 (strong buy); 0 means you abstain
(outside your style, or the data does not tell you enough). Abstaining is better than guessing.

Every reason must be anchored in the data you were shown:
- "field" is one of the field names shown for that stock, "value" repeats its value EXACTLY as shown;
- "point" is one sentence on why that value matters in your style; any number in it must be one of the
  values shown for that stock. Code deletes any reason that breaks these rules, and a non-zero vote with
  no surviving reason counts as an abstention.
- At most 3 reasons per stock. Use no outside knowledge about the companies.

Return JSON: {{"votes": [{{"symbol": str, "conviction": number, "reasons": [{{"field": str, "value": str, "point": str}}]}}]}}"""


def _check_reason(r, data: dict[str, str]) -> tuple[dict | None, str]:
    if not isinstance(r, dict):
        return None, "not an object"
    f, v, point = str(r.get("field", "")), str(r.get("value", "")), str(r.get("point", "")).strip()
    if f not in data:
        return None, f"field {f!r} is not in this investor's data"
    if v.strip() != data[f]:
        return None, f"value {v!r} does not match the computed {data[f]!r}"
    if not point:
        return None, "no point made"
    # the values shown, plus the numbers in the field names themselves ("52-week", "50-day", "RSI 14")
    allowed = set().union(*(numbers_in(x) for x in data.values()), *(numbers_in(k) for k in data))
    extra = numbers_in(point) - allowed
    if extra:
        return None, f"states numbers not in its data: {sorted(extra)}"
    return {"field": f, "value": data[f], "point": point}, ""


def llm_votes(inv: Investor, rows: list[dict], llm: LLM) -> list[dict]:
    """One model call for this investor over all the names; every reason checked by code."""
    data = {r["symbol"]: shown(inv, r) for r in rows}
    user = {"stocks": [{"symbol": r["symbol"], "name": r.get("name") or "", "data": data[r["symbol"]]} for r in rows]}
    msgs = [{"role": "system", "content": VOTE_SYSTEM.format(style=inv.style)},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)}]
    base = {"investor": inv.id, "kind": inv.kind, "horizon_days": inv.horizon_days}
    missing = "abstain: no vote returned"
    try:
        raw = llm.complete(msgs, json_mode=True, temperature=0.0, max_tokens=16000, tag=f"vote {inv.id}")
        if not raw.strip():
            missing = "abstain: the model returned an empty answer"
        got = parse_json(raw)
        items = got.get("votes", []) if isinstance(got, dict) else []
    except ReplayMiss as e:
        return [{**base, "symbol": s, "conviction": 0.0, "reasons": [], "stripped": [],
                 "status": f"abstain: model unavailable ({str(e)[:80]})"} for s in data]
    except (json.JSONDecodeError, ValueError, IndexError):
        items = []
        missing = missing if missing != "abstain: no vote returned" else "abstain: the model's answer was not valid JSON"
    by_sym = {str(v.get("symbol", "")).upper(): v for v in items if isinstance(v, dict)}
    out = []
    for sym, d in data.items():
        v = by_sym.get(sym.upper())
        if v is None:
            out.append({**base, "symbol": sym, "conviction": 0.0, "reasons": [], "stripped": [], "status": missing})
            continue
        try:
            c = float(v.get("conviction", 0))
            c = max(-1.0, min(1.0, c)) if math.isfinite(c) else 0.0
        except (TypeError, ValueError):
            c = 0.0
        kept, stripped = [], []
        for r in v.get("reasons") or []:
            ok, why = _check_reason(r, d)
            if ok and len(kept) >= MAX_REASONS:
                ok, why = None, f"more than {MAX_REASONS} reasons"
            (kept.append(ok) if ok else stripped.append({"reason": r, "why": why}))
        status = "voted" if c else "abstain"
        if c and not kept:
            c, status = 0.0, "abstain: no reason passed the check"
        out.append({**base, "symbol": sym, "conviction": round(c, 3), "reasons": kept, "stripped": stripped,
                    "status": status})
    return out


def code_votes(inv: Investor, features: pd.DataFrame, symbols: list[str]) -> list[dict]:
    """A rule investor: a name that passes its rule gets conviction 1.0 (best ranked) down to 0.5."""
    spec = inv.rule_spec()
    _, surv = run_screen(features, spec)
    ranked = rank(surv, spec).reset_index(drop=True)
    pos = {s: i for i, s in enumerate(ranked["symbol"])}
    n = max(len(ranked) - 1, 1)
    base = {"investor": inv.id, "kind": inv.kind, "horizon_days": inv.horizon_days, "stripped": []}
    out = []
    for s in symbols:
        if s not in pos:
            out.append({**base, "symbol": s, "conviction": 0.0, "reasons": [], "status": "abstain: outside the rule"})
            continue
        row = ranked.iloc[pos[s]]
        reasons = [{"field": c["field"], "value": fmt(c["field"], _value(c["field"], row.get(c["field"]))),
                    "point": f"passes the rule: {describe(c)}"} for c in spec.conditions]
        out.append({**base, "symbol": s, "conviction": round(1.0 - 0.5 * pos[s] / n, 3),
                    "reasons": reasons, "status": f"voted: rank {pos[s] + 1} of {len(ranked)} under the rule"})
    return out


def team_votes(rows: list[dict], features: pd.DataFrame, llm: LLM | None, roster: list[Investor]) -> list[dict]:
    """Every investor votes on every row, each separately. Model investors are skipped without an LLM."""
    from concurrent.futures import ThreadPoolExecutor
    symbols = [r["symbol"] for r in rows]
    model_investors = [i for i in roster if i.kind == "llm"] if llm is not None else []
    with ThreadPoolExecutor(max_workers=max(1, min(8, len(model_investors)))) as pool:
        pending = {i.id: pool.submit(llm_votes, i, rows, llm) for i in model_investors}  # separate calls, in parallel
        votes = []
        for inv in roster:
            if inv.kind == "code":
                votes += code_votes(inv, features, symbols)
            elif inv.id in pending:
                votes += pending[inv.id].result()
    return votes


def tally(votes: list[dict], weights: dict[str, float] | None = None,
          clusters: dict[str, str] | None = None) -> list[dict]:
    """Per name: the counted votes, each investor weighted by its record, copycats sharing one voice."""
    weights, clusters = weights or {}, clusters or {}
    by_sym: dict[str, list[dict]] = {}
    for v in votes:
        by_sym.setdefault(v["symbol"], []).append(v)
    out = []
    for sym, vs in by_sym.items():
        active = [v for v in vs if v["conviction"]]
        size: dict[str, int] = {}
        for v in active:
            k = clusters.get(v["investor"], v["investor"])
            size[k] = size.get(k, 0) + 1
        num = den = 0.0
        for v in active:
            ew = weights.get(v["investor"], 1.0) / size[clusters.get(v["investor"], v["investor"])]
            num += ew * v["conviction"]
            den += ew
        wc = num / den if den else 0.0
        n_for = sum(1 for v in active if v["conviction"] > 0)
        n_against = sum(1 for v in active if v["conviction"] < 0)
        minority = min(n_for, n_against)
        split = minority >= 2 and minority / (n_for + n_against) >= 1 / 3   # a real disagreement, not one dissenter
        if split:
            verdict = "split"
        elif len(size) < MIN_VOICES:
            verdict = "one voice only" if size else "no votes"
        elif wc >= LEAN and n_for > n_against:
            verdict = "team for"
        elif wc <= -LEAN and n_against > n_for:
            verdict = "team against"
        else:
            verdict = "no consensus"
        out.append({"symbol": sym, "verdict": verdict, "weighted_conviction": round(wc, 3),
                    "mean_conviction": round(float(np.mean([v["conviction"] for v in active])), 3) if active else 0.0,
                    "for": n_for, "against": n_against, "abstain": len(vs) - len(active),
                    "independent_voices": len(size), "split": split})
    return sorted(out, key=lambda t: (-t["weighted_conviction"], t["symbol"]))


def vote_and_tally(rows: list[dict], features: pd.DataFrame, llm: LLM | None,
                   roster: list[Investor] | None = None) -> dict:
    roster = roster or load_roster()
    votes = team_votes(rows, features, llm, roster)
    w, c, src = current_weights(roster)
    return {"roster_version": roster_version(), "investors": [{"id": i.id, "name": i.name, "kind": i.kind}
                                                              for i in roster if i.kind == "code" or llm is not None],
            "weights": w, "weights_source": src, "votes": votes, "tally": tally(votes, w, c)}


def record_votes(run_id: str, as_of: str, mode: str, observation: str, team: dict, rows: list[dict],
                 spy_close: float | None, path: Path = VOTES) -> dict:
    close = {r["symbol"]: r.get("close") for r in rows}
    body = {"run_id": run_id, "as_of": as_of, "mode": mode, "observation": observation,
            "roster_version": team["roster_version"], "spy_close": spy_close,
            "votes": [{"investor": v["investor"], "symbol": v["symbol"], "conviction": v["conviction"],
                       "horizon_days": v["horizon_days"], "entry_close": close.get(v["symbol"])}
                      for v in team["votes"] if v["conviction"]]}
    return append_entry(path, body, what="vote ledger")


# ---------------------------------------------------------------- record: scorecards

def mark_votes(entries: list[dict], closes: pd.DataFrame) -> list[dict]:
    """Matured votes: conviction, excess return over SPY across the investor's horizon (trading days)."""
    piv = closes.pivot_table(index="date", columns="symbol", values="close").sort_index()
    piv.index = piv.index.astype(str)
    out = []
    for e in entries:
        hist = piv[piv.index >= e["as_of"]]
        if hist.empty or hist.index[0] != e["as_of"] or "SPY" not in hist:
            continue
        late = (date.fromisoformat(e["recorded_at"][:10]) - date.fromisoformat(e["as_of"])).days
        if late > MAX_LATE_DAYS:
            continue  # a vote cast after prices moved past its as-of date would be scored with hindsight
        for v in e["votes"]:
            h = int(v["horizon_days"])
            if len(hist) - 1 < h or v["symbol"] not in hist:
                continue
            p0, p1 = hist[v["symbol"]].iloc[0], hist[v["symbol"]].iloc[h]
            s0, s1 = hist["SPY"].iloc[0], hist["SPY"].iloc[h]
            if not all(np.isfinite(x) and x > 0 for x in (p0, p1, s0, s1)):
                continue
            excess = float(p1 / p0 - s1 / s0)
            out.append({"seq": e["seq"], "as_of": e["as_of"], "investor": v["investor"], "symbol": v["symbol"],
                        "conviction": float(v["conviction"]), "excess": excess,
                        "exit_date": str(hist.index[h])})
    return out


def _spearman(a: list[float], b: list[float]) -> float | None:
    if len(a) < 3:
        return None
    ra, rb = pd.Series(a).rank().to_numpy(), pd.Series(b).rank().to_numpy()
    if ra.std() == 0 or rb.std() == 0:
        return None
    return float(np.corrcoef(ra, rb)[0, 1])


def record_stats(marks: list[dict]) -> dict[str, dict]:
    """Per investor: n, hit rate (direction right on excess), mean and t of conviction x excess, mean IC."""
    by: dict[str, list[dict]] = {}
    for m in marks:
        by.setdefault(m["investor"], []).append(m)
    out = {}
    for inv, ms in by.items():
        x = np.array([m["conviction"] * m["excess"] for m in ms])
        hits = [np.sign(m["conviction"]) == np.sign(m["excess"]) for m in ms if m["excess"]]
        sd = float(x.std(ddof=1)) if len(x) > 1 else 0.0
        ics = []
        for seq in sorted({m["seq"] for m in ms}):
            g = [m for m in ms if m["seq"] == seq]
            ic = _spearman([m["conviction"] for m in g], [m["excess"] for m in g])
            if ic is not None:
                ics.append(ic)
        out[inv] = {"n": len(ms), "hit_rate": float(np.mean(hits)) if hits else None,
                    "mean_signed_excess": float(x.mean()),
                    "t_stat": float(x.mean() / (sd / math.sqrt(len(x)))) if sd > 0 else None,
                    "mean_ic": float(np.mean(ics)) if ics else None, "n_ic_dates": len(ics)}
    return out


def copycat_clusters(entries: list[dict], investors: list[str]) -> dict[str, str]:
    """Investors whose past convictions on the same names correlate >= COPYCAT_CORR share one cluster."""
    vec: dict[str, dict] = {i: {} for i in investors}
    for e in entries:
        for v in e["votes"]:
            if v["investor"] in vec:
                vec[v["investor"]][(e["seq"], v["symbol"])] = float(v["conviction"])
    parent = {i: i for i in investors}

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for a_i, a in enumerate(investors):
        for b in investors[a_i + 1:]:
            keys = sorted(set(vec[a]) & set(vec[b]))
            if len(keys) < MIN_OVERLAP:
                continue
            xa, xb = np.array([vec[a][k] for k in keys]), np.array([vec[b][k] for k in keys])
            if xa.std() == 0 or xb.std() == 0:
                continue
            if float(np.corrcoef(xa, xb)[0, 1]) >= COPYCAT_CORR:
                parent[find(b)] = find(a)
    return {i: find(i) for i in investors}


def rule_history(inv: Investor, P=None) -> dict | None:
    """A code investor's record before it has a forward one: its rule's monthly backtest."""
    from .backtest import run
    try:
        r = run(inv.rule_spec(), P)
    except (SpecError, FileNotFoundError):
        return None
    ex = np.array([m["net"] - m["spy"] for m in r["months"] if m["n"] > 0])
    t = float(ex.mean() / (ex.std(ddof=1) / math.sqrt(len(ex)))) if len(ex) > 2 and ex.std(ddof=1) > 0 else None
    return {"verdict": r["verdict"], "months": len(ex), "mean_monthly_excess": float(ex.mean()) if len(ex) else None,
            "t_stat": t, "first": r["params"]["first"], "last": r["params"]["last"]}


def weight_for(stats: dict | None, history: dict | None) -> tuple[float, str]:
    if stats and stats["n"] >= MIN_SCORED and stats["t_stat"] is not None:
        return round(float(np.clip(1 + 0.5 * stats["t_stat"], 0.25, 2.0)), 3), f"forward record ({stats['n']} votes)"
    if history and history["t_stat"] is not None:
        return (round(float(np.clip(1 + 0.5 * history["t_stat"], 0.25, 2.0)), 3),
                f"rule backtest ({history['months']} months)")
    return 1.0, "no record yet"


def scorecards(roster: list[Investor] | None = None, today: date | None = None, fetch_closes=None,
               with_history: bool = True, path: Path = VOTES, out: Path | None = SCORECARDS) -> dict:
    """Verify the vote ledger, mark matured votes, and write each investor's record and weight."""
    roster = roster or load_roster()
    entries = read_ledger(path)
    problems = verify_chain(entries)
    marks = []
    if entries and not problems:
        today = today or date.today()
        if fetch_closes is None:
            from .data.alpaca import AlpacaPrices

            def fetch_closes(symbols, start, end):
                return AlpacaPrices(f"team {end}").daily_bars(symbols, start, end)
        syms = sorted({v["symbol"] for e in entries for v in e["votes"]} | {"SPY"})
        start = date.fromisoformat(min(e["as_of"] for e in entries)) - timedelta(days=5)
        marks = mark_votes(entries, fetch_closes(syms, start, today))
    stats = record_stats(marks)
    clusters = copycat_clusters(entries if not problems else [], [i.id for i in roster])
    rows = []
    for inv in roster:
        hist = rule_history(inv) if (with_history and inv.kind == "code") else None
        w, src = weight_for(stats.get(inv.id), hist)
        rows.append({"id": inv.id, "name": inv.name, "kind": inv.kind, "horizon_days": inv.horizon_days,
                     "record": stats.get(inv.id), "history": hist, "weight": w, "weight_source": src,
                     "cluster": clusters.get(inv.id, inv.id)})
    result = {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "roster_version": roster_version(), "chain_ok": not problems, "chain_problems": problems,
              "n_vote_rounds": len(entries), "n_matured_votes": len(marks), "min_scored": MIN_SCORED,
              "copycat_corr": COPYCAT_CORR, "investors": rows}
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=1), encoding="utf-8")
    return result


def current_weights(roster: list[Investor], path: Path = SCORECARDS) -> tuple[dict, dict, str]:
    """Weights and copycat clusters from the last `scout team` scorecard, else equal weights."""
    if not path.exists():
        return {i.id: 1.0 for i in roster}, {i.id: i.id for i in roster}, "equal weights (no scorecard yet: scout team)"
    d = json.loads(path.read_text(encoding="utf-8"))
    rows = {r["id"]: r for r in d["investors"]}
    w = {i.id: float(rows[i.id]["weight"]) if i.id in rows else 1.0 for i in roster}
    c = {i.id: rows[i.id]["cluster"] if i.id in rows else i.id for i in roster}
    return w, c, f"scorecard of {d['generated_at']}"


# ---------------------------------------------------------------- mode 2: ideas

PROPOSE_SYSTEM = """You are one investor on a team that brings ideas to a portfolio manager. Your style:

{style}

Propose ONE new stock-screen idea in your style: names to BUY. Code will validate it, run it on today's
universe and backtest it on monthly point-in-time history with costs, holding the names long; most ideas are
rejected, so make it specific and well motivated. Ideas are long-only for now: even with a short bias, propose
names you would own (the backtest cannot hold a short). Do not repeat an idea you already proposed (listed
below with its result).

Output ONE JSON object: {{"version": 1, "observation": "the idea in one plain-English sentence, in your voice",
"universe": {{...optional...}}, "conditions": [{{"field", "op", "value" or "ref", "why"}}],
"rank": [{{"field", "direction": "asc"|"desc", "weight"}}], "top_n": 5-10, "unmapped": [], "notes": "one sentence"}}
Rules: only the fields below; op is one of < <= > >= between ==; ratios are decimals (10% = 0.10);
"==" only for boolean fields; at most 4 conditions. Fields named rs_*_vs_ a sector ETF (xl*) cannot be
backtested; avoid them.

{schema}"""


def spec_key(spec: Spec) -> str:
    d = spec.to_dict()
    core = {k: d[k] for k in ("universe", "conditions", "rank")}
    for c in core["conditions"]:
        c.pop("why", None)
    return hashlib.sha256(json.dumps(core, sort_keys=True).encode()).hexdigest()[:16]


def propose(inv: Investor, llm: LLM | None, past: list[dict]) -> tuple[Spec | None, list[str]]:
    """This investor's idea as a validated spec, or (None, problems). A code investor proposes its rule."""
    if inv.kind == "code":
        return inv.rule_spec(), []
    if llm is None:
        return None, ["no model configured"]
    mine = [{"observation": p["observation"], "result": p["result"]} for p in past if p["investor"] == inv.id][-10:]
    msgs = [{"role": "system", "content": PROPOSE_SYSTEM.format(style=inv.style, schema=schema_for_prompt(2))},
            {"role": "user", "content": json.dumps({"your_earlier_ideas": mine}, ensure_ascii=False)}]
    problems: list[str] = []
    for attempt in range(2):  # one correction round, like the translator
        try:
            raw = llm.complete(msgs, json_mode=True, temperature=0.0, max_tokens=16000,
                               tag=f"propose {inv.id}" + (f"#{attempt}" if attempt else ""))
        except ReplayMiss as e:
            return None, [f"model unavailable ({str(e)[:80]})"]
        try:
            return validate(parse_json(raw)), []
        except SpecError as e:
            problems = e.problems
        except (json.JSONDecodeError, ValueError, IndexError):
            problems = ["the answer was not valid JSON"]
        msgs = msgs + [{"role": "assistant", "content": raw},
                       {"role": "user", "content": "The screener refused that spec:\n- " + "\n- ".join(problems)
                        + "\nReturn a corrected JSON spec."}]
    return None, problems


def evaluate_idea(spec: Spec, features: pd.DataFrame, P=None) -> dict:
    """Screen today's snapshot, backtest on history, accept only an edge with names to hold today."""
    from .backtest import for_run
    try:
        funnel, surv = run_screen(features, spec)
    except SpecError as e:
        return {"accepted": False, "reason": "; ".join(e.problems), "backtest": None, "n_ranked": 0, "top": []}
    ranked = rank(surv, spec)
    top = ranked.head(spec.top_n)
    bt = for_run(spec, P, top_n=spec.top_n)
    if not bt.get("ok"):
        reason = "not backtested: " + ("; ".join(bt.get("problems", [])) or bt.get("error", ""))
    elif bt["verdict"] != EDGE:
        reason = f"{bt['verdict']}: failed " + "; ".join(g["label"] for g in bt["gates"] if not g["pass"])
    elif top.empty:
        reason = "edge on history, but nothing passes the screen today"
    else:
        reason = ""
    rows = [{k: _value(k, v) for k, v in r.items() if not k.startswith("_")} for r in top.to_dict(orient="records")]
    return {"accepted": not reason, "reason": reason, "funnel": funnel, "n_ranked": int(len(ranked)),
            "top": rows, "backtest": bt}


def brief(as_of: str, llm: LLM | None, roster: list[Investor] | None = None, features: pd.DataFrame | None = None,
          manifest: dict | None = None, record: bool = True, proposals_path: Path = PROPOSALS,
          votes_path: Path = VOTES, out_dir: Path | None = None, P=None) -> dict:
    """Mode 2: every proposing investor brings one idea; only tested survivors reach the brief."""
    from .pipeline import load_features
    roster = roster or load_roster()
    if features is None:
        features, manifest = load_features(as_of)
    past = read_ledger(proposals_path)
    bad = verify_chain(past)
    if bad:
        raise RuntimeError("proposal ledger is corrupt: " + "; ".join(bad))
    seen = {p["spec_key"]: p for p in past}
    from concurrent.futures import ThreadPoolExecutor
    proposers = [i for i in roster if i.proposes]
    with ThreadPoolExecutor(max_workers=8) as pool:  # each investor writes its idea separately, in parallel
        proposed = list(pool.map(lambda i: propose(i, llm, past), proposers))
    ideas = []
    for inv, (spec, problems) in zip(proposers, proposed):
        idea = {"investor": inv.id, "investor_name": inv.name, "kind": inv.kind}
        if spec is None:
            ideas.append({**idea, "status": "invalid", "reason": "; ".join(problems)})
            continue
        key = spec_key(spec)
        prior = seen.get(key)
        if prior and prior["as_of"] == as_of:
            ideas.append({**idea, "status": "repeat", "spec": spec.to_dict(),
                          "reason": f"already tested today ({prior['result']})"})
            continue
        if prior and prior["result"] != "accepted" and inv.kind == "llm":
            ideas.append({**idea, "status": "repeat", "spec": spec.to_dict(),
                          "reason": f"dead idea: rejected on {prior['as_of']} ({prior['reason']})"})
            continue
        ev = evaluate_idea(spec, features, P)
        idea.update({"status": "accepted" if ev["accepted"] else "rejected", "reason": ev["reason"],
                     "spec": spec.to_dict(), "n_ranked": ev["n_ranked"], "top": ev["top"],
                     "backtest": _bt_summary(ev["backtest"])})
        if ev["accepted"]:
            idea["team"] = vote_and_tally(ev["top"], features, llm, roster)
        if record:
            entry = append_entry(proposals_path, {
                "as_of": as_of, "investor": inv.id, "observation": spec.observation, "spec_key": key,
                "result": idea["status"], "reason": ev["reason"],
                "verdict": (ev["backtest"] or {}).get("verdict")}, what="proposal ledger")
            seen[key] = entry
            if ev["accepted"]:
                spy = ((manifest or {}).get("benchmark_closes") or {}).get("SPY")
                record_votes(f"brief-{as_of}-{inv.id}", as_of, "proposal", spec.observation, idea["team"],
                             ev["top"], spy, path=votes_path)
        ideas.append(idea)
    result = {"as_of": as_of, "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "roster_version": roster_version(), "n_tested": sum(1 for i in ideas if i["status"] in ("accepted", "rejected")),
              "n_accepted": sum(1 for i in ideas if i["status"] == "accepted"), "ideas": ideas}
    out_dir = out_dir or RUNS / f"brief-{as_of}"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "brief.json").write_text(json.dumps(result, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    (out_dir / "brief.md").write_text(brief_markdown(result), encoding="utf-8")
    result["out_dir"] = str(out_dir)
    return result


def _bt_summary(bt: dict | None) -> dict | None:
    if not bt:
        return None
    if not bt.get("ok"):
        return {"ok": False, "problems": bt.get("problems"), "error": bt.get("error")}
    st = bt["stats"]
    return {"ok": True, "verdict": bt["verdict"], "first": bt["params"]["first"], "last": bt["params"]["last"],
            "total": st["strategy"]["total"], "spy_total": st["spy"]["total"], "universe_total": st["universe"]["total"],
            "sharpe": st["strategy"]["sharpe"], "hit_rate_vs_spy": st["hit_rate_vs_spy"],
            "gates": [{"label": g["label"], "pass": g["pass"]} for g in bt["gates"]]}


# ---------------------------------------------------------------- rendering

def _pct(v) -> str:
    return "n/a" if v is None else f"{v * 100:+.0f}%"


def team_lines(team: dict, top: int = 10) -> list[str]:
    """The tally as a markdown table plus the strongest reason on each side for each name."""
    L = [f"Weights: {team['weights_source']}. Copycats (past votes correlated >= {COPYCAT_CORR}) count as one voice.", "",
         "| name | team | weighted conviction | for | against | abstain | independent voices |",
         "|---|---|---:|---:|---:|---:|---:|"]
    for t in team["tally"][:top]:
        L.append(f"| {t['symbol']} | {t['verdict']} | {t['weighted_conviction']:+.2f} | {t['for']} | {t['against']} | "
                 f"{t['abstain']} | {t['independent_voices']} |")
    L.append("")
    names = {i["id"]: i["name"] for i in team["investors"]}
    for t in team["tally"][:top]:
        vs = [v for v in team["votes"] if v["symbol"] == t["symbol"] and v["conviction"] and v["reasons"]]
        best_for = max((v for v in vs if v["conviction"] > 0), key=lambda v: v["conviction"], default=None)
        best_against = min((v for v in vs if v["conviction"] < 0), key=lambda v: v["conviction"], default=None)
        for label, v in (("for", best_for), ("against", best_against)):
            if v:
                r = v["reasons"][0]
                L.append(f"- **{t['symbol']}** {label}, {names.get(v['investor'], v['investor'])} "
                         f"({v['conviction']:+.2f}): {r['point']} ({r['field']} = {r['value']})")
    return L


def brief_markdown(b: dict) -> str:
    L = [f"# Morning brief, {b['as_of']}", "",
         f"{b['n_tested']} ideas were tested today; {b['n_accepted']} passed every backtest gate and had names to "
         "hold. Each idea was screened on today's snapshot and backtested monthly on point-in-time history with "
         "costs, by code. With many ideas tested, some passes are luck: an accepted idea is on probation until "
         "its forward record agrees.", ""]
    acc = [i for i in b["ideas"] if i["status"] == "accepted"]
    if acc:
        L += ["## Accepted", ""]
    for i in acc:
        bt = i["backtest"]
        L += [f"### {i['spec']['observation']}", "",
              f"Proposed by **{i['investor_name']}**. {i['n_ranked']} names pass today. Backtest {bt['first']} to "
              f"{bt['last']}: screen {_pct(bt['total'])}, SPY {_pct(bt['spy_total'])}, equal-weight universe "
              f"{_pct(bt['universe_total'])}; verdict **{bt['verdict']}**.", ""]
        L += team_lines(i["team"]) + [""]
    rej = [i for i in b["ideas"] if i["status"] != "accepted"]
    if rej:
        L += ["## Tested and rejected", "", "| investor | idea | why |", "|---|---|---|"]
        for i in rej:
            obs = (i.get("spec") or {}).get("observation", "(no valid idea)")
            L.append(f"| {i['investor_name']} | {obs} | {i['reason']} |")
    return "\n".join(L) + "\n"


def scorecard_lines(sc: dict) -> list[str]:
    L = [f"Vote ledger: {sc['n_vote_rounds']} rounds, chain {'ok' if sc['chain_ok'] else 'BROKEN'}; "
         f"{sc['n_matured_votes']} votes past their horizon. Forward record sets the weight after "
         f"{sc['min_scored']} matured votes.", "",
         "| investor | kind | horizon | matured votes | hit rate | mean IC | rule backtest | weight | from |",
         "|---|---|---:|---:|---:|---:|---|---:|---|"]
    for r in sc["investors"]:
        rec, h = r["record"] or {}, r["history"]
        hist = f"{h['verdict']} ({h['months']} mo)" if h else ""
        hr = "n/a" if rec.get("hit_rate") is None else f"{rec['hit_rate'] * 100:.0f}%"
        ic = "n/a" if rec.get("mean_ic") is None else f"{rec['mean_ic']:+.2f}"
        L.append(f"| {r['name']} | {r['kind']} | {r['horizon_days']}d | {rec.get('n', 0)} | {hr} | {ic} | {hist} | "
                 f"{r['weight']:.2f} | {r['weight_source']} |")
    return L
