"""The investor team: checked votes, counted voices, a scored record, ideas that must survive a backtest."""

import json

import numpy as np
import pandas as pd
import pytest

from scout import team as T
from scout.spec import FIELDS


class FakeLLM:
    """Answers by tag: `answers[tag]` is a dict (returned as JSON) or a callable(messages) -> dict."""
    provider, model = "fake", "fake-1"

    def __init__(self, answers):
        self.answers, self.calls = answers, []

    def complete(self, messages, *, json_mode=True, temperature=0.0, max_tokens=8000, tag=""):
        self.calls.append((tag, messages))
        a = self.answers.get(tag, {})
        return json.dumps(a(messages) if callable(a) else a)


VALUE = T.Investor(id="v", name="Value", kind="llm", style="cheap on cash flow", horizon_days=5, proposes=True,
                   fields=("fcf_yield", "net_debt"))
MOMO = T.Investor(id="m", name="Momentum", kind="llm", style="trend", horizon_days=5, proposes=False,
                  fields=("mom_12m",))
RULE = T.Investor(id="r", name="Rule", kind="code", style="rule", horizon_days=5, proposes=True,
                  rule={"observation": "fcf yield over 5%", "conditions": [{"field": "fcf_yield", "op": ">", "value": 0.05}],
                        "rank": [{"field": "fcf_yield", "direction": "desc"}], "top_n": 2})


def features():
    cols = {f: np.nan for f in FIELDS}
    rows = []
    for sym, fy, mom in (("AAA", 0.09, 0.30), ("BBB", 0.06, -0.20), ("CCC", 0.01, 0.50)):
        r = dict(cols, symbol=sym, name=sym + " Inc", close=10.0, market_cap=5e9, fcf_yield=fy, mom_12m=mom,
                 net_debt=-1e8, avg_dollar_volume_50d=5e7, sic=3674)
        rows.append(r)
    return pd.DataFrame(rows)


def rows():
    return features().to_dict(orient="records")


def test_the_shipped_roster_validates_and_every_rule_is_backtestable():
    roster = T.load_roster()
    assert len(roster) >= 8 and {i.kind for i in roster} == {"llm", "code"}
    from scout.backtest import load_panels
    import os
    if os.path.exists("data/panels/panels.npz"):
        P = load_panels()
        for i in roster:
            if i.kind == "code":
                assert set(f for c in i.rule_spec().conditions for f in [c["field"]]) <= set(P.fields)


def test_each_investor_sees_only_its_own_data_and_bad_reasons_are_deleted():
    llm = FakeLLM({"vote v": {"votes": [
        {"symbol": "AAA", "conviction": 0.8, "reasons": [
            {"field": "fcf_yield", "value": "+9.0%", "point": "A +9.0% cash yield is a margin of safety."},
            {"field": "mom_12m", "value": "+30.0%", "point": "Not in my data."},            # outside the diet
            {"field": "fcf_yield", "value": "+12.0%", "point": "Wrong value."},              # value mismatch
            {"field": "net_debt", "value": "$-100M", "point": "Net cash of 250 million."}]},  # invented number
        {"symbol": "BBB", "conviction": 0.5, "reasons": [{"field": "fcf_yield", "value": "+1.0%", "point": "x"}]},
    ]}})
    votes = T.llm_votes(VALUE, rows(), llm)
    shown_to_model = json.loads(llm.calls[0][1][1]["content"])
    assert set(shown_to_model["stocks"][0]["data"]) == {"fcf_yield", "net_debt"}   # its diet, nothing else
    a, b, c = votes
    assert a["conviction"] == 0.8 and len(a["reasons"]) == 1 and len(a["stripped"]) == 3
    assert b["conviction"] == 0.0 and b["status"] == "abstain: no reason passed the check"
    assert c["symbol"] == "CCC" and c["status"] == "abstain: no vote returned"


def test_rule_investor_votes_by_its_rule():
    v = {x["symbol"]: x for x in T.code_votes(RULE, features(), ["AAA", "BBB", "CCC"])}
    assert v["AAA"]["conviction"] == 1.0 and v["BBB"]["conviction"] == 0.5 and v["CCC"]["conviction"] == 0.0
    assert v["CCC"]["status"] == "abstain: outside the rule"


def test_tally_counts_copycats_once_weights_by_record_and_needs_two_voices():
    votes = [{"investor": i, "symbol": "AAA", "conviction": c} for i, c in (("a", 1.0), ("b", 1.0), ("c", -0.5))]
    plain = T.tally(votes)[0]
    assert plain["independent_voices"] == 3 and plain["weighted_conviction"] == pytest.approx(0.5)
    copy = T.tally(votes, clusters={"a": "a", "b": "a", "c": "c"})[0]   # a and b always agree: one voice
    assert copy["independent_voices"] == 2 and copy["weighted_conviction"] == pytest.approx(0.25)
    heavy = T.tally(votes, weights={"c": 5.0})[0]                        # c has the better record
    assert heavy["weighted_conviction"] < 0
    one = T.tally([{"investor": "a", "symbol": "ZZZ", "conviction": 1.0}])[0]
    assert one["verdict"] == "one voice only"
    split = T.tally([{"investor": i, "symbol": "S", "conviction": c} for i, c in
                     (("a", 1), ("b", 1), ("c", -1), ("d", -1))])[0]
    assert split["verdict"] == "split"


def test_votes_are_recorded_on_a_chain_and_scored_after_their_horizon(tmp_path):
    team = {"roster_version": "x", "votes": [
        {"investor": "v", "symbol": "AAA", "conviction": 1.0, "horizon_days": 2},
        {"investor": "v", "symbol": "BBB", "conviction": -1.0, "horizon_days": 2},
        {"investor": "m", "symbol": "AAA", "conviction": 0.0, "horizon_days": 2}]}
    path = tmp_path / "votes.jsonl"
    import datetime as dt
    d0 = dt.date.today()
    T.record_votes("run1", d0.isoformat(), "idea", "obs", team, [{"symbol": "AAA", "close": 10}, {"symbol": "BBB", "close": 10}],
                   500.0, path=path)
    entries = [json.loads(x) for x in path.read_text().splitlines()]
    assert entries[0]["prev_hash"] == "0" * 64 and len(entries[0]["votes"]) == 2   # abstentions are not recorded
    dates = [(d0 + dt.timedelta(days=k)).isoformat() for k in range(3)]
    closes = pd.DataFrame([{"date": d, "symbol": s, "close": c} for d, (a, b, spy) in
                           zip(dates, [(10, 10, 100), (11, 9, 100), (12, 8, 101)]) for s, c in (("AAA", a), ("BBB", b), ("SPY", spy))])
    marks = T.mark_votes(entries, closes)
    m = {x["symbol"]: x for x in marks}
    assert m["AAA"]["excess"] == pytest.approx(0.2 - 0.01) and m["BBB"]["excess"] == pytest.approx(-0.2 - 0.01)
    st = T.record_stats(marks)["v"]
    assert st["n"] == 2 and st["hit_rate"] == 1.0 and st["mean_ic"] == pytest.approx(1.0) or st["mean_ic"] is None
    sc = T.scorecards(roster=[VALUE, MOMO, RULE], path=path, fetch_closes=lambda *_: closes, with_history=False,
                      out=tmp_path / "sc.json")
    v = next(r for r in sc["investors"] if r["id"] == "v")
    assert sc["chain_ok"] and v["record"]["n"] == 2 and v["weight_source"] == "no record yet"   # 2 < MIN_SCORED


def test_weights_come_from_the_record_only_once_it_is_long_enough():
    assert T.weight_for({"n": 3, "t_stat": 5.0}, None) == (1.0, "no record yet")
    assert T.weight_for({"n": 40, "t_stat": 2.0}, None)[0] == 2.0
    assert T.weight_for({"n": 40, "t_stat": -4.0}, None)[0] == 0.25
    assert T.weight_for(None, {"t_stat": 1.0, "months": 44})[1] == "rule backtest (44 months)"


def test_copycats_are_detected_from_past_votes():
    entries = [{"seq": s, "votes": [{"investor": "a", "symbol": f"S{k}", "conviction": c},
                                    {"investor": "b", "symbol": f"S{k}", "conviction": c * 0.9},
                                    {"investor": "c", "symbol": f"S{k}", "conviction": [1, 1, -1, -1][k]}]}
               for s in range(3) for k, c in enumerate([1, -1, 0.5, -0.5])]
    cl = T.copycat_clusters(entries, ["a", "b", "c"])
    assert cl["a"] == cl["b"] != cl["c"]


def test_brief_accepts_only_ideas_with_an_edge_and_lists_every_rejection(tmp_path, monkeypatch):
    from scout import backtest as B
    edge = {"ok": True, "verdict": T.EDGE, "params": {"first": "2023-01-31", "last": "2026-09-30"},
            "stats": {"strategy": {"total": 0.5, "sharpe": 1.0}, "spy": {"total": 0.3}, "universe": {"total": 0.2},
                      "hit_rate_vs_spy": 0.6}, "gates": [{"label": "g", "pass": True}]}
    none = {**edge, "verdict": "No edge", "gates": [{"label": "first half > 0", "pass": False}]}
    monkeypatch.setattr(B, "for_run", lambda spec, P=None, top_n=None: edge if spec.conditions[0]["field"] == "fcf_yield" else none)
    good = {"version": 1, "observation": "Momentum idea", "conditions": [{"field": "mom_12m", "op": ">", "value": 0}],
            "rank": [{"field": "mom_12m", "direction": "desc"}], "top_n": 2}
    llm = FakeLLM({"propose v": good, "vote v": {"votes": []}, "vote m": {"votes": []}})
    b = T.brief("2026-01-02", llm, roster=[VALUE, MOMO, RULE], features=features(), manifest={},
                proposals_path=tmp_path / "p.jsonl", votes_path=tmp_path / "v.jsonl", out_dir=tmp_path / "brief")
    by = {i["investor"]: i for i in b["ideas"]}
    assert by["r"]["status"] == "accepted" and by["r"]["team"]["tally"]
    assert by["v"]["status"] == "rejected" and "No edge" in by["v"]["reason"] and "first half" in by["v"]["reason"]
    assert "m" not in by                                  # does not propose
    md = (tmp_path / "brief" / "brief.md").read_text()
    assert "## Accepted" in md and "## Tested and rejected" in md and "Momentum idea" in md
    # the same dead idea is not tested again the next day
    b2 = T.brief("2026-01-05", llm, roster=[VALUE, MOMO, RULE], features=features(), manifest={},
                 proposals_path=tmp_path / "p.jsonl", votes_path=tmp_path / "v.jsonl", out_dir=tmp_path / "brief2")
    assert {i["investor"]: i for i in b2["ideas"]}["v"]["status"] == "repeat"


def test_numbers_from_the_field_names_are_allowed_in_a_point():
    data = {"drawdown_52w": "-30.0%", "pct_vs_sma50": "+5.0%"}
    ok, _ = T._check_reason({"field": "drawdown_52w", "value": "-30.0%",
                             "point": "30.0% off the 52-week high and above the 50-day average."}, data)
    assert ok
    bad, why = T._check_reason({"field": "drawdown_52w", "value": "-30.0%", "point": "Down 45% in 2 years."}, data)
    assert bad is None and "45" in why


def test_a_refused_proposal_gets_one_correction_round():
    bad = {"version": 1, "observation": "x", "universe": {"exclude_sectors": ["Energy"]},
           "conditions": [{"field": "mom_12m", "op": ">", "value": 0}], "rank": [{"field": "mom_12m", "direction": "desc"}]}
    good = {**bad, "universe": {}}
    llm = FakeLLM({"propose v": bad, "propose v#1": good})
    spec, problems = T.propose(VALUE, llm, [])
    assert spec is not None and problems == [] and len(llm.calls) == 2
    assert "refused" in llm.calls[1][1][-1]["content"] and "exclude_sectors" in llm.calls[1][1][-1]["content"]
