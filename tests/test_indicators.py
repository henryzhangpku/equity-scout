"""Indicators against values computed by hand (arithmetic shown in comments)."""

import numpy as np
import pandas as pd
import pytest

from scout import indicators as I


def test_sma():
    c = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=float)
    s = I.sma(c, 3)
    assert np.isnan(s.iloc[1])
    assert s.iloc[2] == pytest.approx(2.0)      # (1+2+3)/3
    assert s.iloc[-1] == pytest.approx(9.0)     # (8+9+10)/3


def test_rsi_wilder_by_hand():
    # closes 1,2,3,2,3,4,5 -> changes +1,+1,-1,+1,+1,+1
    c = pd.Series([1, 2, 3, 2, 3, 4, 5], dtype=float)
    r = I.rsi(c, 3)
    assert np.isnan(r.iloc[2])
    # first averages over 3 changes: gain (1+1+0)/3 = 2/3, loss (0+0+1)/3 = 1/3, RS = 2
    assert r.iloc[3] == pytest.approx(100 - 100 / 3)          # 66.667
    # gain (2/3*2 + 1)/3 = 7/9, loss (1/3*2 + 0)/3 = 2/9, RS = 3.5
    assert r.iloc[4] == pytest.approx(100 - 100 / 4.5)        # 77.778
    # gain (7/9*2 + 1)/3 = 23/27, loss (2/9*2)/3 = 4/27, RS = 5.75
    assert r.iloc[5] == pytest.approx(100 - 100 / 6.75)       # 85.185
    # gain (23/27*2 + 1)/3 = 73/81, loss (4/27*2)/3 = 8/81, RS = 9.125
    assert r.iloc[6] == pytest.approx(100 - 100 / 10.125)


def test_rsi_all_gains_is_100():
    r = I.rsi(pd.Series(np.arange(1, 30, dtype=float)), 14)
    assert r.iloc[-1] == 100.0


def test_ema_seeded_with_first_value():
    # alpha = 2/(3+1) = 0.5: 2 -> 0.5*4 + 0.5*2 = 3 -> 0.5*6 + 0.5*3 = 4.5
    e = I.ema(pd.Series([2.0, 4.0, 6.0]), 3)
    assert list(e) == pytest.approx([2.0, 3.0, 4.5])


def test_macd_constant_series_is_zero():
    m = I.macd(pd.Series([50.0] * 60))
    assert m["macd"].abs().max() == pytest.approx(0.0)
    assert m["hist"].iloc[-1] == pytest.approx(0.0)


def test_macd_matches_hand_emas():
    c = pd.Series([10.0, 11.0, 12.0])
    m = I.macd(c, fast=1, slow=3, signal=1)
    # EMA1 = close; EMA3 (alpha .5): 10, 10.5, 11.25 -> macd 0, 0.5, 0.75; signal(1) = macd
    assert list(m["macd"]) == pytest.approx([0.0, 0.5, 0.75])
    assert list(m["hist"]) == pytest.approx([0.0, 0.0, 0.0])


def test_momentum():
    m = I.momentum(pd.Series([100.0, 110.0, 121.0]), 2)
    assert m.iloc[-1] == pytest.approx(0.21)                  # 121/100 - 1


def test_volume_ratio_excludes_today():
    v = pd.Series([10.0, 20.0, 30.0, 60.0])
    assert I.volume_ratio(v, 2).iloc[-1] == pytest.approx(2.4)  # 60 / mean(20, 30)


def test_drawdown_from_high():
    d = I.drawdown_from_high(pd.Series([10.0, 12.0, 9.0]), 3)
    assert d.iloc[-1] == pytest.approx(-0.25)                  # 9/12 - 1


def test_snapshot_relative_strength_and_structure():
    n = 300
    dates = pd.date_range("2025-01-01", periods=n, freq="B").strftime("%Y-%m-%d")
    stock = pd.Series(np.linspace(100, 200, n))
    bench = pd.Series(np.linspace(100, 150, n), index=dates)
    df = pd.DataFrame({"date": dates, "close": stock, "volume": 1000.0})
    s = I.snapshot(df, {"spy": bench})
    k = 63
    exp_stock = stock.iloc[-1] / stock.iloc[-1 - k] - 1
    exp_bench = bench.iloc[-1] / bench.iloc[-1 - k] - 1
    assert s["mom_3m"] == pytest.approx(exp_stock)
    assert s["rs_3m_vs_spy"] == pytest.approx(exp_stock - exp_bench)
    assert s["sma50_above_sma200"] is True                     # rising line
    assert s["drawdown_52w"] == pytest.approx(0.0)             # at the high
    assert s["volume_ratio_50d"] == pytest.approx(1.0)
    assert s["sma20"] == pytest.approx(stock.iloc[-20:].mean())
