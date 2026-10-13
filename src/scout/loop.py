"""A learning loop that cannot fool itself: agents propose, a fixed evaluator decides.

    propose -> evaluate on a fixed split -> correct for the number of tries -> record -> decide

The proposer (scripted or a language model, see propose.py) only writes a typed signal spec.
Everything after that is code in this module:

* Data: daily adjusted closes for a fixed universe, stored in data/loop/daily_closes.npz and
  built once from the cached Alpaca bars (`scout loop-data`). The universe is the 500 most liquid
  US operating companies by 50-day dollar volume on the last session before UNIVERSE_DATE, price
  at least $5. Survivorship: only companies still listed on 2026-10-08 are candidates.
* Split, fixed in code before any hypothesis was tried: discovery = signals whose whole holding
  period ends on or before DISCOVERY_END; out-of-sample (OOS) = signals dated on or after OOS_START.
  No discovery return touches an OOS price. OOS is opened only for a hypothesis that has already
  passed discovery, and the proposer never sees anything about OOS (not even whether it was opened).
* Signal spec: entry conditions on daily (D) or weekly (W) indicators for a long side and/or a short
  side, plus a holding period of 5, 10 or 20 trading days. A signal on the close of bar t enters at the
  close of t+1 and exits H sessions later. Weekly signals can fire only on the last session of a week,
  from completed weekly closes.
* Per event: excess = side * (forward return - universe mean forward return over the same window)
  - round-trip cost (2 x COST_BPS). The universe baseline carries no cost.
* Statistics: events are grouped into non-overlapping blocks of H sessions by signal date; each block's
  mean excess is one observation. t-stat = mean / Newey-West standard error (lag 1, because holding
  periods spill into the next block), one-sided p from the normal approximation. Sharpe-like =
  mean / sd of block means * sqrt(252 / H). Hit rate = share of events with excess > 0.
* Multiple testing: Bonferroni. The step budget K (`--max-steps`) is declared before the loop starts
  and every step counts against it, including invalid and duplicate proposals. A test passes only if
  p < ALPHA / K, with mean excess > 0 and minimum event and block counts. The same corrected bar is
  applied to discovery and to OOS. Bonferroni is conservative; that is deliberate for a loop whose
  job is to keep trying ideas.
* Decision: promote only if discovery passes and then OOS passes; otherwise reject with the reason.
  An exact repeat of an earlier spec is rejected without touching the data (dead ideas stay dead).
* Ledger: every step is appended to a hash-chained JSONL file (track.append_entry), so an edited or
  deleted attempt is detected.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

from . import indicators as I
from .config import CACHE, DATA_DIR, RUNS
from .track import append_entry, read_ledger, verify_chain

LOOP_DATA = DATA_DIR / "loop" / "daily_closes.npz"
UNIVERSE_DATE = "2022-03-01"
UNIVERSE_SIZE = 500
UNIVERSE_MIN_PRICE = 5.0

# fixed before any hypothesis was tried; never changed by the loop
DISCOVERY_END = "2024-12-31"
OOS_START = "2025-01-01"
COST_BPS = 10.0            # per side; a round trip costs 2x
ALPHA = 0.05
HOLDS = (5, 10, 20)
MIN_EVENTS = {"discovery": 50, "oos": 30}
MIN_BLOCKS = {"discovery": 20, "oos": 10}
MACD_WARMUP = 35           # bars before a MACD value is used (slow EMA 26 + signal 9)

FEATURES = {
    "rsi14": {"kind": "number", "label": "RSI(14)", "range": (0.0, 100.0)},
    "macd_hist": {"kind": "number", "label": "MACD histogram", "range": (0.0, 0.0)},
    "macd_cross_up": {"kind": "bool", "label": "MACD crosses above its signal"},
    "macd_cross_down": {"kind": "bool", "label": "MACD crosses below its signal"},
    "rsi_bear_div": {"kind": "bool", "label": "bearish RSI divergence (price higher high, RSI lower high)"},
    "rsi_bull_div": {"kind": "bool", "label": "bullish RSI divergence (price lower low, RSI higher low)"},
}
MAX_CONDITIONS = 3
MAX_WITHIN = 10


# ----------------------------------------------------------------------------------------- data

@dataclass
class LoopData:
    dates: list[str]
    symbols: np.ndarray
    close: np.ndarray            # [T, N] float, NaN = no bar
    source: str = ""
    sha256: str = ""


def save_data(path: Path, dates, symbols, close, meta: dict | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, dates=np.array(list(dates)), symbols=np.array(list(symbols)),
                        close=np.asarray(close, dtype=np.float32))
    if meta is not None:
        meta = {**meta, "sha256": file_sha256(path), "bytes": path.stat().st_size}
        path.with_suffix(".json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    return path


def file_sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_data(path: Path | str | None = None) -> LoopData:
    p = Path(path) if path else LOOP_DATA
    if not p.exists():
        raise FileNotFoundError(f"{p} not found; build it with `scout loop-data` (needs the cached daily bars)")
    z = np.load(p, allow_pickle=False)
    return LoopData(dates=[str(d) for d in z["dates"]], symbols=z["symbols"],
                    close=z["close"].astype(np.float64), source=str(p), sha256=file_sha256(p))


def build_data(prices_path: Path | None = None, out: Path | None = None) -> Path:
    """data/loop/daily_closes.npz from the cached long frame of daily bars (no network)."""
    from .snapshot import BENCHMARKS
    prices_path = prices_path or CACHE / "panels" / "prices_long.csv.gz"
    bars = pd.read_csv(prices_path, compression="gzip", usecols=["date", "symbol", "close", "volume"])
    cal = sorted(bars.loc[bars["symbol"] == "SPY", "date"].unique())
    pre = bars[(bars["date"] < UNIVERSE_DATE) & ~bars["symbol"].isin(BENCHMARKS)]
    last_session = max(d for d in cal if d < UNIVERSE_DATE)
    pre = pre.sort_values(["symbol", "date"])
    tail = pre.groupby("symbol").tail(50)
    agg = tail.assign(dv=tail["close"] * tail["volume"]).groupby("symbol").agg(
        n=("dv", "size"), adv=("dv", "mean"), last_date=("date", "max"), last_close=("close", "last"))
    ok = agg[(agg["n"] == 50) & (agg["last_date"] == last_session) & (agg["last_close"] >= UNIVERSE_MIN_PRICE)]
    syms = sorted(ok.sort_values("adv", ascending=False).head(UNIVERSE_SIZE).index)
    piv = bars[bars["symbol"].isin(syms)].pivot_table(index="date", columns="symbol", values="close")
    piv = piv.reindex(index=cal, columns=syms)
    out = out or LOOP_DATA
    meta = {"source": "Alpaca daily bars, split and dividend adjusted (cached long frame)",
            "first": cal[0], "last": cal[-1], "sessions": len(cal), "n_symbols": len(syms),
            "universe_rule": f"top {UNIVERSE_SIZE} US operating companies by 50-day average dollar volume on "
                             f"{last_session} (the last session before {UNIVERSE_DATE}), close >= "
                             f"${UNIVERSE_MIN_PRICE:g}; candidates are companies listed on 2026-10-08 (survivorship)",
            "source_sha256": file_sha256(prices_path)}
    return save_data(out, cal, syms, piv.to_numpy(dtype=float), meta)


# ------------------------------------------------------------------------------------- features

def _series_features(c: np.ndarray) -> dict[str, np.ndarray]:
    """Every whitelisted feature for one gap-free close series (float; bools as 1/0, NaN = unknown)."""
    s = pd.Series(c)
    n = len(c)
    rsi = I.rsi(s, 14).to_numpy()
    h = I.macd(s)["hist"].to_numpy().copy()
    h[:MACD_WARMUP - 1] = np.nan
    prev = np.concatenate([[np.nan], h[:-1]])
    known = np.isfinite(h) & np.isfinite(prev)
    up = np.where(known, (prev <= 0) & (h > 0), np.nan)
    down = np.where(known, (prev >= 0) & (h < 0), np.nan)
    bear, bull = I.divergence(c, rsi)
    div_known = np.isfinite(rsi)
    return {"rsi14": rsi, "macd_hist": h, "macd_cross_up": up.astype(float), "macd_cross_down": down.astype(float),
            "rsi_bear_div": np.where(div_known, bear, np.nan).astype(float),
            "rsi_bull_div": np.where(div_known, bull, np.nan).astype(float)}


def week_end_rows(dates: list[str]) -> np.ndarray:
    d = pd.to_datetime(pd.Series(dates))
    return d.groupby(d.dt.to_period("W-FRI").to_numpy()).tail(1).index.to_numpy()


@dataclass
class Lab:
    """The fixed evaluator: data, the split, precomputed features and forward returns."""

    data: LoopData
    discovery_end: str = DISCOVERY_END
    oos_start: str = OOS_START
    cost_bps: float = COST_BPS
    _feat: dict = field(default_factory=dict)
    _fwd: dict = field(default_factory=dict)

    def rows(self, tf: str) -> np.ndarray:
        return np.arange(len(self.data.dates)) if tf == "D" else week_end_rows(self.data.dates)

    def features(self, tf: str) -> dict[str, np.ndarray]:
        """{feature: [rows(tf), N]} computed per symbol on its own bars (gaps skipped), backward-looking."""
        if tf in self._feat:
            return self._feat[tf]
        rows = self.rows(tf)
        C = self.data.close[rows]
        out = {f: np.full(C.shape, np.nan) for f in FEATURES}
        for j in range(C.shape[1]):
            ok = np.isfinite(C[:, j])
            if ok.sum() < 30:
                continue
            for f, v in _series_features(C[ok, j]).items():
                out[f][ok, j] = v
        self._feat[tf] = out
        return out

    def forward(self, H: int) -> tuple[np.ndarray, np.ndarray]:
        """(R, B): R[t, i] = close[t+1+H] / close[t+1] - 1 (signal on t's close), B[t] = universe mean of R[t]."""
        if H not in self._fwd:
            C = self.data.close
            T = len(C)
            R = np.full(C.shape, np.nan)
            if T > H + 1:
                R[:T - 1 - H] = C[1 + H:] / C[1:T - H] - 1.0
            with np.errstate(all="ignore"):
                cnt = np.isfinite(R).sum(1)
                B = np.where(cnt > 0, np.nansum(R, 1) / np.maximum(cnt, 1), np.nan)
            self._fwd[H] = (R, B)
        return self._fwd[H]

    def period_rows(self, period: str, H: int) -> np.ndarray:
        """Boolean per signal row: discovery = exit date <= discovery_end; oos = signal date >= oos_start."""
        d = np.array(self.data.dates)
        T = len(d)
        m = np.zeros(T, dtype=bool)
        if period == "discovery":
            exit_idx = np.arange(T) + 1 + H
            ok = exit_idx < T
            m[ok] = d[exit_idx[ok]] <= self.discovery_end
        else:
            m = (d >= self.oos_start) & (np.arange(T) + 1 + H < T)
        return m

    def mask(self, conds: list[dict], tf: str) -> np.ndarray:
        """[T, N] True where every condition holds (each within its last `within` bars of timeframe tf)."""
        F = self.features(tf)
        rows = self.rows(tf)
        m = None
        for c in conds:
            x = F[c["feature"]]
            with np.errstate(invalid="ignore"):
                if c["op"] == ">":
                    hit = x > c["value"]
                elif c["op"] == "<":
                    hit = x < c["value"]
                else:
                    hit = x == (1.0 if c["value"] else 0.0)
            hit = hit & np.isfinite(x)
            w = c.get("within", 1)
            if w > 1:
                hit = pd.DataFrame(hit).rolling(w, min_periods=1).max().to_numpy().astype(bool)
            m = hit if m is None else (m & hit)
        full = np.zeros(self.data.close.shape, dtype=bool)
        if m is not None:
            full[rows] = m
        return full

    def evaluate(self, spec: dict, period: str) -> dict:
        H = spec["hold_days"]
        R, B = self.forward(H)
        prow = self.period_rows(period, H)
        cost = 2 * self.cost_bps / 1e4
        t_idx, ex, raw, base, sides = [], [], [], [], []
        for side, sgn in (("long", 1.0), ("short", -1.0)):
            if not spec.get(side):
                continue
            m = self.mask(spec[side], spec["timeframe"]) & prow[:, None] & np.isfinite(R)
            t, i = np.nonzero(m)
            t_idx.append(t)
            raw.append(sgn * R[t, i])
            base.append(sgn * B[t])
            ex.append(sgn * (R[t, i] - B[t]) - cost)
            sides.append(np.full(len(t), sgn))
        t = np.concatenate(t_idx) if t_idx else np.array([], dtype=int)
        e = np.concatenate(ex) if ex else np.array([])
        rows_in = np.nonzero(prow)[0]
        out = {"period": period, "n_events": int(len(e)),
               "n_long": int(sum((s > 0).sum() for s in sides)), "n_short": int(sum((s < 0).sum() for s in sides)),
               "n_blocks": 0, "hit_rate": None, "mean_return": None, "mean_baseline": None, "mean_excess": None,
               "t_stat": None, "p_value": None, "sharpe": None, "first_signal": None, "last_signal": None}
        if len(e) == 0 or len(rows_in) == 0:
            return out
        blk = (t - rows_in[0]) // H
        keys, inv = np.unique(blk, return_inverse=True)
        bm = np.bincount(inv, weights=e) / np.bincount(inv)
        out.update({"n_blocks": int(len(keys)), "hit_rate": float(np.mean(e > 0)),
                    "mean_return": float(np.mean(np.concatenate(raw))),
                    "mean_baseline": float(np.mean(np.concatenate(base))), "mean_excess": float(np.mean(e)),
                    "first_signal": self.data.dates[int(t.min())], "last_signal": self.data.dates[int(t.max())]})
        ts, sh = block_stats(bm, H)
        out["t_stat"], out["sharpe"] = ts, sh
        out["p_value"] = None if ts is None else float(1.0 - NormalDist().cdf(ts))
        return out


def block_stats(x: np.ndarray, H: int) -> tuple[float | None, float | None]:
    """(t-stat with a Newey-West lag-1 standard error, Sharpe-like annualised mean / sd) of block means."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n < 3:
        return None, None
    m = x.mean()
    u = x - m
    g0 = float(u @ u) / n
    g1 = float(u[1:] @ u[:-1]) / n
    var = (g0 + g1) / n          # Bartlett weight 1 - 1/2 on lag 1: g0 + 2 * 0.5 * g1
    if var <= 0:
        var = g0 / n
    sd = float(x.std(ddof=1))
    t = float(m / math.sqrt(var)) if var > 0 else None
    sh = float(m / sd * math.sqrt(252 / H)) if sd > 0 else None
    return t, sh


# ----------------------------------------------------------------------------------------- spec

class SpecInvalid(ValueError):
    def __init__(self, problems: list[str]):
        super().__init__("; ".join(problems))
        self.problems = problems


def validate(d) -> dict:
    """A typed, whitelisted signal spec, normalised; raises SpecInvalid listing every problem."""
    p: list[str] = []
    if not isinstance(d, dict):
        raise SpecInvalid(["the spec must be a JSON object"])
    if "unparseable_response" in d:
        raise SpecInvalid(["the proposer's response was not valid JSON"])
    allowed = {"id", "rationale", "timeframe", "hold_days", "long", "short"}
    p += [f"unknown key '{k}'" for k in d if k not in allowed]
    sid = d.get("id")
    if not isinstance(sid, str) or not re.fullmatch(r"[a-z0-9_]{1,60}", sid):
        p.append("id must be 1-60 characters of a-z, 0-9 and _")
    rat = d.get("rationale", "")
    if not isinstance(rat, str) or len(rat) > 400:
        p.append("rationale must be a string of at most 400 characters")
    tf = d.get("timeframe", "D")
    if tf not in ("D", "W"):
        p.append("timeframe must be 'D' (daily) or 'W' (weekly)")
    hold = d.get("hold_days")
    if hold not in HOLDS or isinstance(hold, bool):
        p.append(f"hold_days must be one of {list(HOLDS)}")
    sides = {}
    for side in ("long", "short"):
        conds = d.get(side, []) or []
        if not isinstance(conds, list):
            p.append(f"{side} must be a list of conditions")
            continue
        if len(conds) > MAX_CONDITIONS:
            p.append(f"{side}: at most {MAX_CONDITIONS} conditions")
        norm = []
        for k, c in enumerate(conds):
            where = f"{side}[{k}]"
            if not isinstance(c, dict):
                p.append(f"{where} must be an object")
                continue
            p += [f"{where}: unknown key '{x}'" for x in c if x not in ("feature", "op", "value", "within")]
            f = c.get("feature")
            if f not in FEATURES:
                p.append(f"{where}: unknown feature {f!r}; allowed: {sorted(FEATURES)}")
                continue
            spec_f, op, v = FEATURES[f], c.get("op"), c.get("value")
            if spec_f["kind"] == "bool":
                if op != "==" or not isinstance(v, bool):
                    p.append(f"{where}: {f} takes op '==' and value true or false")
            else:
                lo, hi = spec_f["range"]
                if op not in ("<", ">"):
                    p.append(f"{where}: {f} takes op '<' or '>'")
                if isinstance(v, bool) or not isinstance(v, (int, float)) or not (lo <= v <= hi):
                    p.append(f"{where}: {f} value must be a number in [{lo:g}, {hi:g}]"
                             + (" (the MACD histogram is in price units, so only its sign is comparable)"
                                if f == "macd_hist" else ""))
            w = c.get("within", 1)
            if isinstance(w, bool) or not isinstance(w, int) or not 1 <= w <= MAX_WITHIN:
                p.append(f"{where}: within must be an integer 1-{MAX_WITHIN} (bars)")
            norm.append({"feature": f, "op": op, "value": float(v) if spec_f["kind"] == "number"
                         and isinstance(v, (int, float)) and not isinstance(v, bool) else v, "within": w})
        sides[side] = norm
    if not sides.get("long") and not sides.get("short"):
        p.append("at least one of long or short needs a condition")
    if p:
        raise SpecInvalid(p)
    return {"id": sid, "rationale": rat, "timeframe": tf, "hold_days": hold,
            "long": sides["long"], "short": sides["short"]}


def spec_key(spec: dict) -> str:
    """Identity of a hypothesis: everything except its name and rationale."""
    core = {k: spec[k] for k in ("timeframe", "hold_days", "long", "short")}
    return hashlib.sha256(json.dumps(core, sort_keys=True).encode()).hexdigest()[:16]


def describe(spec: dict) -> str:
    def cond(c):
        f = FEATURES[c["feature"]]
        if f["kind"] == "bool":
            s = f["label"] if c["value"] else "no " + f["label"]
        else:
            s = f"{f['label']} {c['op']} {c['value']:g}"
        return s + (f" within the last {c['within']} bars" if c.get("within", 1) > 1 else "")
    tf = "daily" if spec["timeframe"] == "D" else "weekly"
    parts = [f"{side} when " + " and ".join(cond(c) for c in spec[side]) for side in ("long", "short") if spec[side]]
    return f"{'; '.join(parts)} ({tf} bars); hold {spec['hold_days']} days"


# ------------------------------------------------------------------------------------- decision

def threshold(K: int) -> float:
    return ALPHA / K


def gate(m: dict, K: int) -> tuple[bool, str]:
    period = m["period"]
    name = "discovery" if period == "discovery" else "out-of-sample"
    if m["n_events"] < MIN_EVENTS[period]:
        return False, f"{name}: too few events ({m['n_events']} < {MIN_EVENTS[period]})"
    if m["n_blocks"] < MIN_BLOCKS[period]:
        return False, f"{name}: too few independent blocks ({m['n_blocks']} < {MIN_BLOCKS[period]})"
    if m["mean_excess"] is None or m["mean_excess"] <= 0:
        return False, f"{name}: mean excess after costs is not positive ({pct(m['mean_excess'])})"
    if m["p_value"] is None or m["p_value"] >= threshold(K):
        return False, (f"{name}: t = {num(m['t_stat'])}, p = {num(m['p_value'], 4)} does not clear the corrected bar "
                       f"p < {threshold(K):.4f} ({ALPHA:g} / {K} tries)")
    return True, f"{name}: t = {num(m['t_stat'])}, p = {num(m['p_value'], 4)} < {threshold(K):.4f}"


def pct(x) -> str:
    return "n/a" if x is None else f"{x * 100:+.2f}%"


def num(x, d: int = 2) -> str:
    return "n/a" if x is None else f"{x:.{d}f}"


def public_view(entry: dict) -> dict:
    """What a proposer may see of a ledger attempt: the spec and discovery results only.
    The final decision, its reason and anything out-of-sample are withheld."""
    d = entry.get("discovery")
    keep = ("n_events", "n_long", "n_short", "n_blocks", "hit_rate", "mean_return", "mean_baseline",
            "mean_excess", "t_stat", "p_value", "sharpe")
    return {"step": entry["step"], "status": entry["status"], "spec": entry.get("spec"),
            "proposal_problems": entry.get("proposal_problems"),
            "discovery": None if d is None else {k: (round(d[k], 5) if isinstance(d[k], float) else d[k]) for k in keep},
            "discovery_pass": entry.get("discovery_pass"), "discovery_reason": entry.get("discovery_reason")}


# ----------------------------------------------------------------------------------------- loop

class LoopStop(RuntimeError):
    """The proposer cannot continue (for example, no LLM key and no recorded response)."""


def run_loop(lab: Lab, proposer, max_steps: int, ledger_path: Path, label: str = "") -> dict:
    """Run up to max_steps proposals. K = max_steps is the Bonferroni budget, fixed up front."""
    if ledger_path.exists() and read_ledger(ledger_path):
        raise RuntimeError(f"{ledger_path} already has entries; each loop run writes a fresh ledger")
    K = max_steps
    config = {"kind": "config", "label": label, "proposer": getattr(proposer, "name", "custom"),
              "budget_K": K, "alpha": ALPHA, "corrected_p": threshold(K), "correction": "Bonferroni",
              "discovery_end": lab.discovery_end, "oos_start": lab.oos_start, "cost_bps_per_side": lab.cost_bps,
              "holds": list(HOLDS), "min_events": MIN_EVENTS, "min_blocks": MIN_BLOCKS,
              "data": {"source": Path(lab.data.source).name if lab.data.source else "", "sha256": lab.data.sha256,
                       "first": lab.data.dates[0], "last": lab.data.dates[-1],
                       "sessions": len(lab.data.dates), "n_symbols": int(lab.data.close.shape[1])}}
    append_entry(ledger_path, config, what="loop ledger")
    attempts: list[dict] = []
    stop_reason = f"step budget of {K} used"
    for step in range(1, max_steps + 1):
        history = [public_view(a) for a in attempts]
        try:
            raw = proposer(history, step, K)
        except LoopStop as e:
            stop_reason = f"proposer stopped: {e}"
            break
        if raw is None:
            stop_reason = "proposer has nothing left to propose"
            break
        a = {"kind": "attempt", "step": step, "proposed": raw, "spec": None, "spec_key": None,
             "status": "tested", "proposal_problems": None, "discovery": None, "discovery_pass": None,
             "discovery_reason": None, "oos": None, "oos_opened": False, "decision": "reject", "reason": ""}
        try:
            spec = validate(raw)
        except SpecInvalid as e:
            a.update(status="invalid", proposal_problems=e.problems,
                     reason="invalid spec, data not touched: " + "; ".join(e.problems))
        else:
            a["spec"], a["spec_key"] = spec, spec_key(spec)
            a["description"] = describe(spec)
            dup = next((b for b in attempts if b["spec_key"] == a["spec_key"]), None)
            if dup is not None:
                a.update(status="duplicate", reason=f"same hypothesis as step {dup['step']} ({dup['spec']['id']}); "
                                                    "dead ideas stay dead, data not touched")
            else:
                disc = lab.evaluate(spec, "discovery")
                ok, why = gate(disc, K)
                a.update(discovery=disc, discovery_pass=ok, discovery_reason=why)
                if not ok:
                    a["reason"] = why + "; out-of-sample not opened"
                else:
                    oos = lab.evaluate(spec, "oos")
                    ok2, why2 = gate(oos, K)
                    a.update(oos=oos, oos_opened=True, oos_reason=why2)
                    if ok2:
                        a.update(decision="promote", reason=f"{why}; {why2}")
                    else:
                        a["reason"] = f"passed discovery ({why}) but failed {why2}"
        e = append_entry(ledger_path, a, what="loop ledger")
        attempts.append(e)
    return {"config": config, "attempts": attempts, "stop_reason": stop_reason}


# --------------------------------------------------------------------------------------- report

def learned(attempts: list[dict]) -> list[str]:
    """Discovery-only comparisons between branches, in plain words (what the proposer could see)."""
    by_id = {a["spec"]["id"]: a for a in attempts if a.get("discovery")}
    lines = []
    for base in ("rsi_overbought", "rsi_oversold", "rsi_divergence"):
        b = by_id.get(base)
        if not b:
            continue
        parts = []
        for suf, name in (("_macd_cross", "a MACD cross"), ("_macd_state", "the MACD histogram sign")):
            key = base.replace("rsi_", "") + suf if base != "rsi_divergence" else "divergence" + suf
            x = by_id.get(key)
            if x and x["discovery"]["t_stat"] is not None and b["discovery"]["t_stat"] is not None:
                parts.append(f"with {name} t = {x['discovery']['t_stat']:.2f} on {x['discovery']['n_events']} events, "
                             f"mean excess {pct(x['discovery']['mean_excess'])}")
        if b["discovery"]["t_stat"] is not None:
            lines.append(f"{base}: alone t = {b['discovery']['t_stat']:.2f} on {b['discovery']['n_events']} events, "
                         f"mean excess {pct(b['discovery']['mean_excess'])}" + ("; " + "; ".join(parts) if parts else ""))
    return lines


def report(result: dict) -> tuple[str, dict]:
    c, att = result["config"], result["attempts"]
    promoted = [a for a in att if a["decision"] == "promote"]
    opened = [a for a in att if a["oos_opened"]]
    L = [f"# Learning loop run: {c['label']}", "",
         f"Proposer: **{c['proposer']}**. Data: daily adjusted closes for {c['data']['n_symbols']} US companies, "
         f"{c['data']['first']} to {c['data']['last']} ({c['data']['sessions']} sessions, "
         f"sha256 {c['data']['sha256'][:12]}).",
         f"Split fixed before the first hypothesis: discovery = holding periods ending on or before "
         f"{c['discovery_end']}; out-of-sample = signals from {c['oos_start']}. Costs {c['cost_bps_per_side']:g} bps per "
         f"side. Budget K = {c['budget_K']} tries, Bonferroni: each test needs one-sided p < {c['corrected_p']:.4f}.",
         "", f"Stopped: {result['stop_reason']}. Tried {len(att)}; promoted {len(promoted)}; "
             f"out-of-sample opened for {len(opened)}.", "",
         "## Every attempt (discovery results; this is all the proposer saw)", "",
         "| Step | Hypothesis | Rule | Events | Hit rate | Signal return | Universe | Excess after costs | t | p | Sharpe-like | Decision |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for a in att:
        d = a.get("discovery") or {}
        sid = a["spec"]["id"] if a.get("spec") else "(invalid)"
        rule = a.get("description", "; ".join(a.get("proposal_problems") or []))
        L.append(f"| {a['step']} | {sid} | {rule} | {d.get('n_events', '')} | "
                 f"{pct(d.get('hit_rate')).lstrip('+') if d else ''} | {pct(d.get('mean_return')) if d else ''} | "
                 f"{pct(d.get('mean_baseline')) if d else ''} | {pct(d.get('mean_excess')) if d else ''} | "
                 f"{num(d.get('t_stat')) if d else ''} | {num(d.get('p_value'), 4) if d else ''} | "
                 f"{num(d.get('sharpe')) if d else ''} | **{a['decision']}** |")
    L += ["", "Signal return and universe are signed by side (a short earns the negative of the return), per event, "
              "before costs; excess is after a round-trip cost.", "", "## Reasons", ""]
    L += [f"{a['step']}. {a['spec']['id'] if a.get('spec') else '(invalid)'}: {a['reason']}" for a in att]
    L += ["", "## Out-of-sample (opened only for hypotheses that passed discovery)", ""]
    if not opened:
        L.append("None passed discovery, so the out-of-sample period was never opened. It stays sealed for the next idea.")
    else:
        L += ["| Step | Hypothesis | Events | Hit rate | Excess after costs | t | p | Sharpe-like | Decision |",
              "|---|---|---|---|---|---|---|---|---|"]
        for a in opened:
            o = a["oos"]
            L.append(f"| {a['step']} | {a['spec']['id']} | {o['n_events']} | {pct(o['hit_rate']).lstrip('+')} | "
                     f"{pct(o['mean_excess'])} | {num(o['t_stat'])} | {num(o['p_value'], 4)} | {num(o['sharpe'])} | "
                     f"**{a['decision']}** |")
    lr = learned(att)
    if lr:
        L += ["", "## What the loop learned (discovery only)", ""] + [f"* {x}" for x in lr]
    L += ["", "## Verdict", ""]
    if promoted:
        L.append("Promoted: " + ", ".join(f"{a['spec']['id']} ({a['description']})" for a in promoted)
                 + ". Evidence on this history, not proof.")
    else:
        L.append(f"Nothing survived. {len(att)} hypotheses were tried against a bar corrected for {c['budget_K']} tries, "
                 "and none cleared it in discovery and then out-of-sample. That is the loop doing its job: an idea that "
                 "only looks good because many were tried is rejected and recorded, so it is not tried again.")
    L += ["", "Caveats: survivorship (companies listed on 2026-10-08 only); under five years of daily history "
              "(the data starts 2021-12-01); adjusted closes, no slippage beyond the stated cost; events overlap across "
              "names on the same day, which the block statistics only partly absorb.", ""]
    summary = {"label": c["label"], "proposer": c["proposer"], "budget_K": c["budget_K"],
               "corrected_p": c["corrected_p"], "split": {"discovery_end": c["discovery_end"], "oos_start": c["oos_start"]},
               "data": c["data"], "stop_reason": result["stop_reason"], "tried": len(att),
               "promoted": [a["spec"]["id"] for a in promoted], "oos_opened": [a["spec"]["id"] for a in opened],
               "steps": [{"step": a["step"], "id": a["spec"]["id"] if a.get("spec") else None, "status": a["status"],
                          "discovery_t": (a.get("discovery") or {}).get("t_stat"),
                          "discovery_excess": (a.get("discovery") or {}).get("mean_excess"),
                          "discovery_events": (a.get("discovery") or {}).get("n_events"),
                          "oos_t": (a.get("oos") or {}).get("t_stat"), "decision": a["decision"],
                          "reason": a["reason"]} for a in att],
               "ledger_chain_ok": True}
    return "\n".join(L), summary


def write_run(result: dict, out_dir: Path) -> dict:
    md, summary = report(result)
    summary["ledger_chain_ok"] = not verify_chain(read_ledger(out_dir / "ledger.jsonl"))
    (out_dir / "report.md").write_text(md, encoding="utf-8")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    return summary


def default_out(proposer: str) -> Path:
    return RUNS / (f"loop-{date.today().isoformat()}" + ("" if proposer == "scripted" else f"-{proposer}"))
