"""Funnel arithmetic and deterministic ranking on a hand-built universe."""

import math

import pandas as pd

from scout.screen import check_funnel, rank, run_screen
from scout.spec import validate

NAN = math.nan

UNIVERSE = pd.DataFrame([
    # symbol, sic, market_cap, close, sma50, drawdown, rev growth, fcf
    dict(symbol="AAA", sic=3674, market_cap=5e9, close=50, sma50=45, drawdown_52w=-0.30, revenue_growth_yoy=0.20, fcf_ttm=1e8),
    dict(symbol="BBB", sic=3674, market_cap=8e9, close=40, sma50=42, drawdown_52w=-0.25, revenue_growth_yoy=0.15, fcf_ttm=2e8),
    dict(symbol="CCC", sic=7372, market_cap=3e9, close=20, sma50=18, drawdown_52w=-0.40, revenue_growth_yoy=NAN, fcf_ttm=5e7),
    dict(symbol="DDD", sic=7372, market_cap=1e9, close=10, sma50=9, drawdown_52w=-0.50, revenue_growth_yoy=0.30, fcf_ttm=1e7),
    dict(symbol="EEE", sic=6798, market_cap=1.5e10, close=30, sma50=25, drawdown_52w=-0.21, revenue_growth_yoy=0.12, fcf_ttm=-1e7),
    dict(symbol="FFF", sic=6798, market_cap=NAN, close=30, sma50=25, drawdown_52w=-0.35, revenue_growth_yoy=0.40, fcf_ttm=1e9),
    dict(symbol="GGG", sic=3674, market_cap=1.2e10, close=70, sma50=60, drawdown_52w=-0.22, revenue_growth_yoy=0.11, fcf_ttm=3e8),
])

SPEC = validate({
    "observation": "test",
    "universe": {"market_cap_min": 2e9, "market_cap_max": 2e10},
    "conditions": [
        {"field": "drawdown_52w", "op": "<=", "value": -0.20},
        {"field": "revenue_growth_yoy", "op": ">", "value": 0.10},
        {"field": "fcf_ttm", "op": ">", "value": 0},
        {"field": "close", "op": ">", "ref": "sma50"},
    ],
    "rank": [{"field": "drawdown_52w", "direction": "asc", "weight": 2},
             {"field": "revenue_growth_yoy", "direction": "desc", "weight": 1}],
})


def test_funnel_counts_by_hand():
    funnel, surv = run_screen(UNIVERSE, SPEC)
    check_funnel(funnel)
    steps = [(s["n_in"], s["n_pass"], s["n_fail"], s["n_missing"]) for s in funnel]
    assert steps == [
        (7, 7, 0, 0),   # universe
        (7, 5, 1, 1),   # mcap >= 2B: DDD fails (1B), FFF has no market cap
        (5, 5, 0, 0),   # mcap <= 20B
        (5, 5, 0, 0),   # drawdown <= -20%
        (5, 4, 0, 1),   # revenue growth > 10%: CCC missing
        (4, 3, 1, 0),   # FCF > 0: EEE fails
        (3, 2, 1, 0),   # close > SMA50: BBB fails (40 < 42)
    ]
    assert sorted(surv["symbol"]) == ["AAA", "GGG"]


def test_funnel_missing_counted_separately():
    funnel, _ = run_screen(UNIVERSE, SPEC)
    mc = funnel[1]
    assert mc["step"].startswith("market_cap >=")
    assert (mc["n_pass"], mc["n_fail"], mc["n_missing"]) == (5, 1, 1)  # DDD fails, FFF has no market cap


def test_rank_is_weighted_percentile_and_deterministic():
    _, surv = run_screen(UNIVERSE, SPEC)
    r = rank(surv, SPEC)
    # AAA: deeper drawdown (-30% vs -22%) -> pct 1.0 vs 0.5 on weight 2; growth 20% vs 11% -> 1.0 vs 0.5
    assert list(r["symbol"]) == ["AAA", "GGG"]
    assert r.loc[0, "score"] == 1.0
    assert r.loc[1, "score"] == 0.5
    assert list(rank(surv.iloc[::-1], SPEC)["symbol"]) == ["AAA", "GGG"]


def test_industry_filter_and_missing_sic():
    spec = validate({"observation": "semis", "universe": {"industries": ["semiconductors"]},
                     "conditions": [{"field": "drawdown_52w", "op": "<", "value": 0}],
                     "rank": [{"field": "market_cap", "direction": "desc"}]})
    u = pd.concat([UNIVERSE, pd.DataFrame([dict(symbol="HHH", sic=NAN, market_cap=1e9, drawdown_52w=-0.1)])])
    funnel, surv = run_screen(u, spec)
    check_funnel(funnel)
    assert (funnel[1]["n_pass"], funnel[1]["n_fail"], funnel[1]["n_missing"]) == (3, 4, 1)
    assert sorted(surv["symbol"]) == ["AAA", "BBB", "GGG"]


def test_bool_field_condition():
    u = pd.DataFrame([dict(symbol="A", sma50_above_sma200=True), dict(symbol="B", sma50_above_sma200=False),
                      dict(symbol="C", sma50_above_sma200=None)])
    spec = validate({"observation": "x", "conditions": [{"field": "sma50_above_sma200", "op": "==", "value": True}],
                     "rank": [{"field": "rsi14", "direction": "asc"}]})
    funnel, surv = run_screen(u.assign(rsi14=50.0), spec)
    assert list(surv["symbol"]) == ["A"]
    assert (funnel[1]["n_fail"], funnel[1]["n_missing"]) == (1, 1)
