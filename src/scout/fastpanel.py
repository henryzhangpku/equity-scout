"""Compiled price features for `panels.build`: every symbol at once, only the rebalance rows.

The reference is `panels.series_features` (pandas, one symbol at a time, every row). This module
computes the same fields with Numba, parallel across symbols, and evaluates them only on the rows
the panel keeps (a bar on a rebalance date, with at least 60 bars of history):

* RSI and the MACD EMAs are recursive, so each symbol's series is walked from its first bar up to
  its last kept row;
* every windowed field (SMA, momentum, volume ratio, drawdown, dollar volume) is summed directly
  over its window at the kept row, so there is no running sum to drift.

Conventions are those of `indicators` (see its module docstring). Numba is an optional dependency
(`pip install equity-scout[fast]`); `panels.build` falls back to the pandas loop without it.
"""

from __future__ import annotations

import math

import numpy as np
from numba import njit, prange

# kernel output columns, in order
KERNEL_FIELDS = ["sma20", "sma50", "sma200", "rsi14", "macd", "macd_signal", "macd_hist",
                 "mom_1m", "mom_3m", "mom_6m", "mom_12m", "volume_ratio_50d", "drawdown_52w",
                 "avg_dollar_volume_50d"]
NK = len(KERNEL_FIELDS)


@njit(cache=True, error_model="numpy")
def _window_fields(close, vol, a, i, out):
    """Windowed fields at global row i of the symbol starting at row a (columns 0-2 and 7-13)."""
    t = i - a
    if t >= 19:
        s = 0.0
        for k in range(min(t + 1, 200)):
            s += close[i - k]
            if k == 19:
                out[0] = s / 20.0
            elif k == 49:
                out[1] = s / 50.0
        if t >= 199:
            out[2] = s / 200.0
    for col, k in ((7, 21), (8, 63), (9, 126), (10, 252)):
        if t >= k:
            out[col] = close[i] / close[i - k] - 1.0
    if t >= 50:  # today's volume / mean of the previous 50 sessions
        s = 0.0
        for k in range(1, 51):
            s += vol[i - k]
        out[11] = vol[i] / (s / 50.0)
    if t >= 251:  # needs a full 252-bar window, like pandas min_periods
        hi = close[i]
        for j in range(i - 251, i):
            if close[j] > hi:
                hi = close[j]
        out[12] = close[i] / hi - 1.0
    if t >= 49:
        s = 0.0
        for k in range(50):
            s += close[i - k] * vol[i - k]
        out[13] = s / 50.0


@njit(parallel=True, cache=True, error_model="numpy")
def _kernel(close, vol, offs, want, woffs, out):
    """For symbol s (rows offs[s]:offs[s+1]) fill out[k] for each kept row want[k], k in woffs[s]:woffs[s+1]."""
    a12, a26, a9 = 2.0 / 13.0, 2.0 / 27.0, 2.0 / 10.0
    for s in prange(len(offs) - 1):
        w0, w1 = woffs[s], woffs[s + 1]
        if w1 == w0:
            continue
        a = offs[s]
        n = want[w1 - 1] - a + 1      # walk only as far as the last kept row
        k = w0
        e12 = close[a]
        e26 = close[a]
        sig = 0.0
        ag = 0.0
        al = 0.0
        for t in range(n):
            i = a + t
            c = close[i]
            # MACD: EMAs seeded with the first close, alpha = 2 / (span + 1)
            if t > 0:
                e12 = a12 * c + (1.0 - a12) * e12
                e26 = a26 * c + (1.0 - a26) * e26
            line = e12 - e26
            sig = line if t == 0 else a9 * line + (1.0 - a9) * sig
            # RSI(14), Wilder: the first average is the mean of the first 14 changes
            if t >= 1:
                d = c - close[i - 1]
                g = d if d > 0 else 0.0
                lo = -d if d < 0 else 0.0
                if t <= 14:
                    ag += g
                    al += lo
                    if t == 14:
                        ag /= 14.0
                        al /= 14.0
                else:
                    ag = (ag * 13.0 + g) / 14.0
                    al = (al * 13.0 + lo) / 14.0
            if k < w1 and want[k] == i:
                row = out[k]
                for f in range(NK):
                    row[f] = math.nan
                row[4] = line
                row[5] = sig
                row[6] = line - sig
                if t >= 14:
                    if al == 0.0:
                        row[3] = 100.0 if ag > 0 else 50.0
                    else:
                        row[3] = 100.0 - 100.0 / (1.0 + ag / al)
                _window_fields(close, vol, a, i, row)
                k += 1


def kernel_rows(close: np.ndarray, vol: np.ndarray, offs: np.ndarray, want: np.ndarray) -> np.ndarray:
    """KERNEL_FIELDS at each global row in `want` (sorted, unique). close/vol are all symbols' bars
    concatenated, each symbol's rows in date order, symbol s at offs[s]:offs[s+1]."""
    want = np.ascontiguousarray(want, dtype=np.int64)
    woffs = np.searchsorted(want, offs).astype(np.int64)
    out = np.empty((len(want), NK))
    _kernel(np.ascontiguousarray(close, dtype=np.float64), np.ascontiguousarray(vol, dtype=np.float64),
            np.ascontiguousarray(offs, dtype=np.int64), want, woffs, out)
    return out
