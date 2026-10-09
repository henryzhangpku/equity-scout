"""Backtest engine: point-in-time panels, return and cost arithmetic, gates."""

import json

import numpy as np
import pandas as pd
import pytest

from scout import backtest as B
from scout import panels as PN
from scout.spec import FIELDS, validate

FIELDS_L = list(FIELDS)


def mini_panels(closes, feature, universe=None):
    """3 symbols x D dates; `feature` = rsi14 values [D][3]; closes [D][3] (nan = no bar)."""
    D, N = len(closes), 3
    vals = np.full((D, N, len(FIELDS_L)), np.nan, dtype=np.float32)
    j = FIELDS_L.index("rsi14")
    vals[:, :, j] = np.array(feature, dtype=np.float32)
    vals[:, :, FIELDS_L.index("market_cap")] = 1e10
    close = np.array(closes, dtype=float)
    last = close.copy()
    for d in range(D):  # last close on or before d
        for n in range(N):
            if not np.isfinite(last[d, n]) and d > 0:
                last[d, n] = last[d - 1, n]
    uni = np.isfinite(close) if universe is None else np.array(universe)
    dates = [f"2024-0{d + 1}-28" for d in range(D)]
    return B.Panels(dates=dates, symbols=np.array(["AAA", "BBB", "CCC"]), fields=FIELDS_L, values=vals,
                    close_at=close, last_close=last, last_date=np.array([dates] * N).T, in_universe=uni,
                    names=np.array(["A", "B", "C"]), sic=np.array([3674.0, 3674.0, 7372.0]),
                    spy_close=np.array([100.0, 101.0, 103.02, 103.02][:D]),
                    check_date=[], check_values=vals[:0], check_universe=uni[:0])


SPEC = validate({"observation": "low rsi", "conditions": [{"field": "rsi14", "op": "<", "value": 50}],
                 "rank": [{"field": "rsi14", "direction": "asc"}], "top_n": 2})


def test_return_cost_and_turnover_arithmetic():
    closes = [[10, 20, 30], [11, 18, 33], [11, 18, 36.3]]
    rsi = [[30, 40, 60], [45, 70, 20], [10, 10, 10]]
    P = mini_panels(closes, rsi)
    r = B.run(SPEC, P, cost_bps=10)
    m0, m1 = r["months"]
    # month 0: hold AAA (rsi 30) and BBB (40): +10% and -10% -> gross 0; buy everything: turnover 1, cost 10 bps
    assert m0["held"] == ["AAA", "BBB"] and m0["gross"] == pytest.approx(0.0)
    assert m0["turnover"] == pytest.approx(1.0) and m0["net"] == pytest.approx(-0.001)
    # month 1: hold CCC (20) and AAA (45): +10% and 0% -> gross 5%
    assert m1["held"] == ["CCC", "AAA"] and m1["gross"] == pytest.approx(0.05)
    # drifted weights before rebalance: AAA .5*1.1=.55, BBB .5*.9=.45 (sum 1) -> new AAA .5, CCC .5
    assert m1["turnover"] == pytest.approx(abs(0.5 - 0.55) + 0.45 + 0.5)
    assert m1["net"] == pytest.approx(0.05 - m1["turnover"] * 0.001)
    assert m1["net_2x"] == pytest.approx(0.05 - m1["turnover"] * 0.002)
    assert m0["spy"] == pytest.approx(0.01) and m1["spy"] == pytest.approx(0.02)
    # universe benchmark (no conditions): equal weight of all three
    assert m0["universe"] == pytest.approx((0.1 - 0.1 + 0.1) / 3)
    assert r["curve"][-1]["strategy"] == pytest.approx((1 - 0.001) * (1 + m1["net"]))


def test_stopped_name_exits_at_last_close():
    closes = [[10, 20, 30], [float("nan"), 22, 30]]
    rsi = [[10, 20, 90], [10, 20, 90]]
    P = mini_panels(closes, rsi)
    m = B.run(SPEC, P)["months"][0]
    assert m["stopped"] == ["AAA"]
    assert m["gross"] == pytest.approx((0.0 + 0.1) / 2)   # AAA exits flat at its last close


def test_too_few_names_holds_cash():
    P = mini_panels([[10, 20, 30], [11, 22, 33]], [[90, 90, 90], [90, 90, 90]])
    r = B.run(SPEC, P)
    assert r["months"][0]["n"] == 0 and r["months"][0]["gross"] == 0.0
    assert r["stats"]["months_too_few"] == 1 and r["verdict"] == "Not enough data"


def test_turnover_math():
    assert B.turnover({}, {}, {"A": .5, "B": .5}) == pytest.approx(1.0)
    assert B.turnover({"A": .5, "B": .5}, {"A": 0.0, "B": 0.0}, {"A": .5, "B": .5}) == pytest.approx(0.0)
    assert B.turnover({"A": 1.0}, {"A": .2}, {"B": 1.0}) == pytest.approx(2.0)
    assert B.turnover({"A": .5, "B": .5}, {"A": 1.0, "B": 0.0}, {}) == pytest.approx(1.0)


def test_gates_on_synthetic_series():
    good = [0.01] * 24
    v, g = B.gates(good, good, 24)
    assert v == "Edge on this history" and all(x["pass"] for x in g)
    one_lucky = [-0.002] * 23 + [0.2]
    v, g = B.gates(one_lucky, one_lucky, 24)
    assert v == "No edge" and {x["id"]: x["pass"] for x in g}["d"] is False and {x["id"]: x["pass"] for x in g}["a"]
    front = [0.02] * 12 + [-0.01] * 12
    v, g = B.gates(front, front, 24)
    assert {x["id"]: x["pass"] for x in g}["c"] is False and v == "No edge"
    costly = [0.001] * 24
    v, g = B.gates(costly, [-0.001] * 24, 24)
    assert {x["id"]: x["pass"] for x in g}["e"] is False
    v, _ = B.gates(good[:10], good[:10], 10)
    assert v == "Not enough data"


def test_stats_math():
    s = B.stats([0.1, -0.1])
    assert s["total"] == pytest.approx(1.1 * 0.9 - 1)
    assert s["max_drawdown"] == pytest.approx(-0.1)
    assert s["cagr"] == pytest.approx((1.1 * 0.9) ** 6 - 1)


def test_price_after_rebalance_date_is_invisible():
    n = 300
    dates = pd.bdate_range("2023-01-02", periods=n).strftime("%Y-%m-%d")
    g = pd.DataFrame({"date": dates, "close": np.linspace(50, 80, n), "volume": 1e6})
    bench = {"spy": pd.Series(np.linspace(100, 120, n), index=dates)}
    d = dates[270]
    a = PN.series_features(g, bench).loc[d]
    g2 = g.copy()
    g2.loc[271:, "close"] = 1.0          # a crash after the date
    g2.loc[271:, "volume"] = 9e9
    b = PN.series_features(g2, bench).loc[d]
    pd.testing.assert_series_equal(a, b)


def test_series_features_match_live_snapshot_function():
    from scout import indicators as I
    n = 320
    dates = pd.bdate_range("2023-01-02", periods=n).strftime("%Y-%m-%d")
    rng = np.random.default_rng(0)
    g = pd.DataFrame({"date": dates, "close": 50 * np.exp(np.cumsum(rng.normal(0, .02, n))),
                      "volume": rng.uniform(1e5, 1e6, n)})
    bench = {"spy": pd.Series(100 * np.exp(np.cumsum(rng.normal(0, .01, n))), index=dates)}
    sf = PN.series_features(g, bench)
    snap = I.snapshot(g.iloc[:300].reset_index(drop=True), bench)
    row = sf.loc[dates[299]]
    for k in ["sma20", "sma200", "rsi14", "macd_hist", "mom_12m", "volume_ratio_50d", "drawdown_52w",
              "avg_dollar_volume_50d", "rs_3m_vs_spy", "pct_vs_sma50"]:
        assert row[k] == pytest.approx(snap[k], rel=1e-9), k
    assert bool(row["sma50_above_sma200"]) == snap["sma50_above_sma200"]


def test_fact_filed_after_rebalance_is_invisible(monkeypatch):
    def facts(val_q2_filed):
        mk = lambda s, e, v, f: {"start": s, "end": e, "val": v, "filed": f, "form": "10-Q", "accn": f}
        rows = [mk(f"{y}-{m1}", f"{y}-{m2}", 100 + i * 10, f"{y}-{m3}") for i, (y, m1, m2, m3) in enumerate([
            ("2024", "01-01", "03-31", "04-30"), ("2024", "04-01", "06-30", "07-30"), ("2024", "07-01", "09-30", "10-30"),
            ("2024", "10-01", "12-31", "01-30"), ("2025", "01-01", "03-31", "04-30")])]
        rows[3]["filed"] = "2025-01-30"
        rows.append(mk("2025-04-01", "2025-06-30", 999, val_q2_filed))
        return {"facts": {"us-gaap": {"RevenueFromContractWithCustomerExcludingAssessedTax": {"units": {"USD": rows}}}}}

    monkeypatch.setattr(PN.SecData, "raw_facts", lambda self, cik: facts("2025-07-31"))
    _, res = PN._fund_job((0, 1, {"2025-07-30": 10.0, "2025-07-31": 10.0}))
    before, after = res["2025-07-30"], res["2025-07-31"]
    assert before["revenue_ttm"] == pytest.approx(130 + 140 + 110 + 120)   # 2024Q2..2025Q1, Q2 2025 not yet filed
    assert after["revenue_ttm"] == pytest.approx(120 + 130 + 140 + 999)


def test_month_end_dates():
    days = pd.bdate_range("2024-01-01", "2024-03-15").strftime("%Y-%m-%d").tolist()
    assert PN.month_end_dates(days, "2024-01-01", "2024-03-15") == ["2024-01-31", "2024-02-29"]
