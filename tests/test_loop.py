"""The learning loop: evaluator math, multiple-testing correction, no look-ahead, ledger, CLI."""

import json

import numpy as np
import pandas as pd
import pytest

from scout import indicators as I
from scout import loop as L
from scout import propose as P
from scout.cli import main
from scout.track import read_ledger, verify_chain

# business days spanning the fixed split (discovery ends 2024-12-31, OOS from 2025-01-01)
DATES = [d.strftime("%Y-%m-%d") for d in pd.bdate_range("2021-06-01", "2026-06-30")]


def walk(n_names=40, seed=0, vol=0.02, boost=0.0, hold=10, dates=DATES, events=None):
    """Random-walk closes. With boost > 0, every time a name's daily RSI(14) (Wilder, computed online
    exactly as indicators.rsi does) closes below 30 on bar t, its returns from t+1 to t+1+hold get
    +boost per day: a planted, real edge for 'long when RSI < 30, hold `hold` days'."""
    rng = np.random.default_rng(seed)
    T = len(dates)
    C = np.empty((T, n_names))
    for j in range(n_names):
        c = np.empty(T)
        c[0] = 50.0
        extra = np.zeros(T + hold + 2)
        ag = al = None
        gains, losses = [], []
        for t in range(1, T):
            r = rng.normal(0, vol) + extra[t]
            c[t] = c[t - 1] * (1 + r)
            d = c[t] - c[t - 1]
            g, l = max(d, 0.0), max(-d, 0.0)
            if ag is None:
                gains.append(g); losses.append(l)
                if len(gains) == 14:
                    ag, al = np.mean(gains), np.mean(losses)
                else:
                    continue
            else:
                ag, al = (ag * 13 + g) / 14, (al * 13 + l) / 14
            rsi = 100.0 if al == 0 and ag > 0 else (50.0 if al == 0 else 100 - 100 / (1 + ag / al))
            if events is not None and rsi < 30:
                events.append((t, j))
            if boost and rsi < 30:
                extra[t + 2:t + 2 + hold] = boost   # returns of bars t+2..t+1+hold: entry close t+1 to exit t+1+hold
        C[:, j] = c
    return C


def lab_from(C, dates=DATES):
    return L.Lab(L.LoopData(dates=list(dates), symbols=np.array([f"S{j}" for j in range(C.shape[1])]), close=C))


OVERSOLD = {"id": "oversold", "timeframe": "D", "hold_days": 10, "long": [{"feature": "rsi14", "op": "<", "value": 30}]}


def test_online_rsi_in_the_generator_matches_indicators():
    ev = []
    C = walk(n_names=3, seed=3, boost=0.004, events=ev)
    # the planted events are exactly the bars indicators.rsi marks as < 30
    want = {(int(t), j) for j in range(3) for t in np.nonzero(I.rsi(pd.Series(C[:, j]), 14).to_numpy() < 30)[0]}
    assert ev and set(ev) == want


def test_forward_return_and_baseline_by_hand():
    dates = DATES[:6]
    C = np.array([[10, 20], [11, 20], [12, 22], [13, 22], [12, 24], [12, 24]], dtype=float)
    lab = lab_from(C, dates)
    R, B = lab.forward(2)
    # signal on bar 0 enters at bar 1's close, exits at bar 3: 13/11 - 1 and 22/20 - 1
    assert R[0, 0] == pytest.approx(13 / 11 - 1) and R[0, 1] == pytest.approx(22 / 20 - 1)
    assert B[0] == pytest.approx(((13 / 11 - 1) + (22 / 20 - 1)) / 2)
    assert np.isnan(R[3:]).all()                    # bar 3 would need bar 6


def test_block_stats_by_hand():
    x = np.array([0.01, 0.03, 0.02, 0.04])
    t, sh = L.block_stats(x, 10)
    m = 0.025
    u = x - m
    g0, g1 = (u @ u) / 4, (u[1:] @ u[:-1]) / 4
    assert t == pytest.approx(m / np.sqrt((g0 + g1) / 4))
    assert sh == pytest.approx(m / x.std(ddof=1) * np.sqrt(25.2))


def test_planted_edge_is_promoted():
    lab = lab_from(walk(boost=0.004))
    d, o = lab.evaluate(L.validate(OVERSOLD), "discovery"), lab.evaluate(L.validate(OVERSOLD), "oos")
    assert d["mean_excess"] > 0.02 and d["p_value"] < 1e-6
    assert o["mean_excess"] > 0.02 and o["p_value"] < L.threshold(10)
    assert d["n_long"] == d["n_events"] and d["n_short"] == 0


def test_planted_edge_promoted_through_the_loop(tmp_path):
    lab = lab_from(walk(boost=0.004))
    res = L.run_loop(lab, lambda h, s, K: dict(OVERSOLD) if s == 1 else None, 10, tmp_path / "ledger.jsonl")
    a = res["attempts"][0]
    assert a["decision"] == "promote", a["reason"]
    assert a["oos_opened"] and a["oos"]["mean_excess"] > 0


NOISE_SPECS = [
    {"id": f"noise_{k}", "timeframe": tf, "hold_days": h,
     "long" if side == "long" else "short": [{"feature": "rsi14", "op": op, "value": v}]}
    for k, (tf, h, side, op, v) in enumerate(
        [(tf, h, side, op, v) for tf in ("D", "W") for h in (5, 10, 20)
         for side, op, v in (("long", "<", 30), ("short", ">", 70), ("long", "<", 40), ("short", ">", 60))])
]


def test_noise_tried_many_times_is_rejected_after_correction(tmp_path):
    lab = lab_from(walk(seed=11))
    K = len(NOISE_SPECS)
    res = L.run_loop(lab, lambda h, s, k: dict(NOISE_SPECS[s - 1]), K, tmp_path / "ledger.jsonl")
    att = res["attempts"]
    assert len(att) == K == 24
    ps = [a["discovery"]["p_value"] for a in att if a["discovery"]["p_value"] is not None]
    # at least one variant looks good on its own in discovery (p < 0.05 uncorrected) ...
    assert min(ps) < 0.05
    # ... and still nothing is promoted once the bar is corrected for 24 tries
    assert all(a["decision"] == "reject" for a in att)


def test_same_noise_without_correction_would_have_fooled_us():
    lab = lab_from(walk(seed=11))
    looks_good = [s for s in NOISE_SPECS
                  if (m := lab.evaluate(L.validate(s), "discovery"))["mean_excess"] > 0 and m["p_value"] < 0.05]
    assert looks_good                     # an uncorrected loop would have opened OOS for these
    assert all(lab.evaluate(L.validate(s), "discovery")["p_value"] >= L.threshold(len(NOISE_SPECS))
               for s in looks_good)


def test_discovery_never_uses_oos_prices():
    C = walk(seed=5)
    C2 = C.copy()
    oos = np.array(DATES) >= L.OOS_START
    C2[oos] *= np.random.default_rng(1).uniform(0.5, 1.5, size=C2[oos].shape)
    la, lb = lab_from(C), lab_from(C2)
    for s in [OVERSOLD] + NOISE_SPECS[:6] + NOISE_SPECS[12:18]:
        assert la.evaluate(L.validate(s), "discovery") == lb.evaluate(L.validate(s), "discovery")
    assert la.evaluate(L.validate(OVERSOLD), "oos") != lb.evaluate(L.validate(OVERSOLD), "oos")


def test_proposals_do_not_depend_on_oos(tmp_path):
    """Same discovery data, wildly different OOS data: identical proposals, prompts and discovery views."""
    C = walk(seed=7, boost=0.003)
    C2 = C.copy()
    oos = np.array(DATES) >= L.OOS_START
    C2[oos] = C2[oos][::-1]
    runs = []
    for k, data in enumerate((C, C2)):
        r = L.run_loop(lab_from(data), P.Scripted(), 10, tmp_path / f"l{k}.jsonl")
        runs.append(r)
    assert [a["proposed"] for a in runs[0]["attempts"]] == [a["proposed"] for a in runs[1]["attempts"]]
    assert [L.public_view(a) for a in runs[0]["attempts"]] == [L.public_view(a) for a in runs[1]["attempts"]]

    class FakeLLM:
        provider, model = "fake", "fake"

        def complete(self, msgs, **kw):
            n = sum(1 for _ in self.seen)
            self.seen.append(msgs)
            return json.dumps(P.SCRIPT[n % len(P.SCRIPT)])

    prompts = []
    for k, data in enumerate((C, C2)):
        f = FakeLLM()
        f.seen = []
        L.run_loop(lab_from(data), P.LLMProposer(f), 4, tmp_path / f"m{k}.jsonl")
        prompts.append(f.seen)
    assert prompts[0] == prompts[1]


def test_public_view_hides_everything_out_of_sample(tmp_path):
    lab = lab_from(walk(boost=0.004))
    res = L.run_loop(lab, lambda h, s, K: dict(OVERSOLD) if s == 1 else None, 5, tmp_path / "l.jsonl")
    v = L.public_view(res["attempts"][0])
    text = json.dumps(v)
    assert "oos" not in text and "promote" not in text and "decision" not in v and "reason" not in v


def test_invalid_and_duplicate_proposals_are_recorded_and_count(tmp_path):
    seq = [dict(OVERSOLD), {"id": "bad", "timeframe": "D", "hold_days": 7, "long": [{"feature": "pe", "op": "<",
                                                                                      "value": 10}]},
           {**OVERSOLD, "id": "same_idea_new_name"}]
    res = L.run_loop(lab_from(walk(seed=2)), lambda h, s, K: seq[s - 1] if s <= 3 else None, 5, tmp_path / "l.jsonl")
    st = [a["status"] for a in res["attempts"]]
    assert st == ["tested", "invalid", "duplicate"]
    assert "hold_days" in res["attempts"][1]["reason"] and "unknown feature" in res["attempts"][1]["reason"]
    assert res["attempts"][2]["discovery"] is None and "step 1" in res["attempts"][2]["reason"]
    assert res["config"]["budget_K"] == 5


def test_validate_refusals():
    with pytest.raises(L.SpecInvalid) as e:
        L.validate({"id": "X Y", "timeframe": "M", "hold_days": 3, "long": [], "short": [],
                    "leverage": 3})
    msg = " ".join(e.value.problems)
    for s in ("unknown key 'leverage'", "id must be", "timeframe", "hold_days", "at least one"):
        assert s in msg
    with pytest.raises(L.SpecInvalid, match="price units"):
        L.validate({"id": "m", "hold_days": 5, "long": [{"feature": "macd_hist", "op": ">", "value": 0.5}]})
    with pytest.raises(L.SpecInvalid, match="true or false"):
        L.validate({"id": "m", "hold_days": 5, "long": [{"feature": "macd_cross_up", "op": ">", "value": 1}]})


def test_weekly_signals_fire_only_on_week_ends():
    lab = lab_from(walk(seed=4, n_names=10))
    m = lab.mask([{"feature": "rsi14", "op": ">", "value": 0, "within": 1}], "W")
    rows = set(L.week_end_rows(DATES))
    assert m.any() and all(t in rows for t in np.nonzero(m.any(1))[0])


def test_ledger_is_append_only_and_hash_chained(tmp_path):
    p = tmp_path / "l.jsonl"
    L.run_loop(lab_from(walk(seed=2)), P.Scripted(), 3, p)
    e = read_ledger(p)
    assert e[0]["kind"] == "config" and [x["seq"] for x in e] == [0, 1, 2, 3]
    assert verify_chain(e) == []
    lines = p.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[1])
    first["decision"] = "promote"                        # quietly rewrite history
    lines[1] = json.dumps(first)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert verify_chain(read_ledger(p))
    with pytest.raises(RuntimeError, match="corrupt"):
        L.append_entry(p, {"kind": "attempt"}, what="loop ledger")
    with pytest.raises(RuntimeError, match="fresh ledger"):
        L.run_loop(lab_from(walk(seed=2)), P.Scripted(), 3, p)


def test_scripted_proposer_plan_and_refinement():
    s = P.Scripted()
    ids = [s([], k, 10)["id"] for k in range(1, 10)]
    assert ids[:3] == ["rsi_overbought", "rsi_oversold", "rsi_divergence"]
    for x in ids[:9]:
        L.validate(s([], ids.index(x) + 1, 10))
    hist = [{"step": 1, "spec": L.validate(P.SCRIPT[0]), "discovery": {"t_stat": 0.5}},
            {"step": 2, "spec": L.validate(P.SCRIPT[2]), "discovery": {"t_stat": 1.5}}]
    r = s(hist, 10, 10)
    assert r["id"] == "rsi_divergence_refined" and r["hold_days"] == 20
    r2 = P.refine(L.validate(P.SCRIPT[1]))
    assert r2["long"][0]["value"] == 25.0
    assert s(hist, 11, 11) is None


def test_llm_mode_stops_gracefully_without_key(tmp_path, monkeypatch):
    from scout import llm as llm_mod
    monkeypatch.setattr(llm_mod, "secret", lambda name: None)
    res = L.run_loop(lab_from(walk(seed=2, n_names=5)),
                     P.LLMProposer(llm_mod.LLM(cache_dir=tmp_path / "cache")), 3, tmp_path / "l.jsonl")
    assert res["attempts"] == [] and "LLM unavailable" in res["stop_reason"]


def test_cli_smoke(tmp_path, capsys):
    data = L.save_data(tmp_path / "d.npz", DATES, [f"S{j}" for j in range(12)], walk(seed=9, n_names=12))
    out = tmp_path / "run"
    main(["loop", "--proposer", "scripted", "--max-steps", "4", "--data", str(data), "--out", str(out)])
    assert {p.name for p in out.iterdir()} == {"ledger.jsonl", "report.md", "summary.json"}
    s = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert s["tried"] == 4 and s["budget_K"] == 4 and s["ledger_chain_ok"]
    md = (out / "report.md").read_text(encoding="utf-8")
    assert "rsi_overbought" in md and "Bonferroni" in md
    assert "chain intact" in capsys.readouterr().out


RECORDED = sorted((L.RUNS).glob("loop-*/ledger.jsonl"))


@pytest.mark.parametrize("ledger", RECORDED, ids=[p.parent.name for p in RECORDED])
def test_recorded_loop_runs_reproduce_offline(ledger, tmp_path, monkeypatch):
    """Re-run each committed loop from the committed data (and, for llm mode, the recorded responses only):
    same proposals, same discovery and out-of-sample numbers, same decisions."""
    from scout import llm as llm_mod
    monkeypatch.setattr(llm_mod, "secret", lambda name: None)
    old = read_ledger(ledger)
    assert verify_chain(old) == []
    cfg = old[0]
    data = L.load_data()
    assert data.sha256 == cfg["data"]["sha256"]
    proposer = P.Scripted() if cfg["proposer"] == "scripted" else P.LLMProposer(llm_mod.LLM(offline=True))
    new = L.run_loop(L.Lab(data), proposer, cfg["budget_K"], tmp_path / "ledger.jsonl")
    keys = ("step", "proposed", "spec", "status", "discovery", "oos", "decision", "reason")
    assert [{k: a.get(k) for k in keys} for a in new["attempts"]] == [{k: a.get(k) for k in keys} for a in old[1:]]
