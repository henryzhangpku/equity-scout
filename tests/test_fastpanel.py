"""The compiled price stage of panels.build must reproduce the pandas reference exactly."""

import numpy as np
import pandas as pd
import pytest

from scout import panels as PN

pytest.importorskip("numba")


def _bars(seed: int = 1) -> tuple[pd.DataFrame, dict, list[str], list[str]]:
    rng = np.random.default_rng(seed)
    cal = pd.bdate_range("2022-01-03", periods=520).strftime("%Y-%m-%d")
    rows = []

    def add(sym, idx, close, volume):
        for i, c, v in zip(idx, close, volume):
            rows.append((cal[i], sym, c, v))

    n = len(cal)
    walk = lambda k, s=.02: 40 * np.exp(np.cumsum(rng.normal(0, s, k)))
    add("AAA", range(n), walk(n), rng.uniform(1e5, 1e6, n))
    gaps = np.sort(rng.choice(n, 430, replace=False))                      # missing sessions
    add("GAP", gaps, walk(len(gaps)), rng.uniform(1e4, 1e5, len(gaps)))
    add("SHORT", range(n - 50, n), walk(50), np.full(50, 1e6))             # < 60 bars: skipped
    add("LATE", range(300, n), walk(n - 300), rng.uniform(1e5, 1e6, n - 300))
    split = walk(n)
    split[260:] /= 5000.0                                                   # reverse-split-like collapse
    add("SPLIT", range(n), split, rng.uniform(1e5, 1e6, n))
    zv = rng.uniform(1e5, 1e6, n)
    zv[100:200] = 0.0                                                       # zero-volume stretch
    add("ZVOL", range(n), walk(n, .001), zv)
    flat = np.full(n, 10.0)                                                 # no changes: RSI 50
    add("FLAT", range(n), flat, np.full(n, 2e5))
    bars = pd.DataFrame(rows, columns=["date", "symbol", "close", "volume"]).sample(frac=1, random_state=0)
    spy = pd.Series(walk(n, .01), index=cal)
    xlk = pd.Series(walk(n, .01), index=cal).drop(cal[[150, 151, 400]])   # benchmark gaps
    bench = {"spy": spy, "xlk": xlk}
    dates = list(cal)          # every session, so each window boundary (bar 19, 59, 251, ...) is checked
    syms = ["AAA", "GAP", "SHORT", "LATE", "MISSING", "SPLIT", "ZVOL", "FLAT"]
    return bars, bench, syms, dates


def test_fast_price_fields_match_reference():
    bars, bench, syms, dates = _bars()
    fields = PN.PANEL_FIELDS
    ref = PN.price_fields(bars, syms, dates, bench, fields)
    got = PN.price_fields_fast(bars, syms, dates, bench, fields)
    names = ["values", "close_at", "last_close", "last_date", "in_universe"]
    for name, a, b in zip(names, ref, got):
        if a.dtype == object or a.dtype == bool:
            assert (a == b).all(), name
        else:
            np.testing.assert_array_equal(np.isfinite(a), np.isfinite(b), err_msg=name)
            np.testing.assert_allclose(b[np.isfinite(b)], a[np.isfinite(a)], rtol=2e-6, err_msg=name)
    v = got[0]
    assert np.isfinite(v).sum() > 1000                       # the test actually exercises the fields
    assert not np.isfinite(v[:, syms.index("SHORT")]).any()
    assert not np.isfinite(v[:, syms.index("MISSING")]).any()
    above = v[:, syms.index("FLAT"), PN.PANEL_FIELDS.index("sma50_above_sma200")]
    assert np.isfinite(above).any() and (above[np.isfinite(above)] == 0).all()   # a tie is not "above"
    g = syms.index("GAP")                                    # rebalance dates with no bar for GAP
    assert (np.isfinite(got[2][:, g]) & ~np.isfinite(got[1][:, g])).any()


def test_sector_relative_strength_is_not_stored():
    """Regression: the sector-ETF rs_*_vs_xl* fields are computed per symbol but are not panel
    fields; the price stage used to raise KeyError on them."""
    bars, bench, syms, dates = _bars()
    assert not any("_vs_xl" in f for f in PN.PANEL_FIELDS)
    PN.price_fields(bars, syms[:2], dates, bench, PN.PANEL_FIELDS)
