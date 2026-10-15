"""Technical indicators on a single price series (plain numpy/pandas).

Conventions, stated so the hand-computed tests can check them:

* SMA(n): arithmetic mean of the last n closes.
* RSI(n): Wilder's smoothing. The first average gain/loss is the simple mean of
  the first n changes; afterwards avg = (prev * (n - 1) + current) / n.
* MACD: EMA(12) - EMA(26) of close, signal = EMA(9) of MACD, EMAs seeded with
  the first value (pandas ewm adjust=False, alpha = 2 / (span + 1)).
* Momentum over k trading days: close[t] / close[t - k] - 1, with 1/3/6/12
  months = 21/63/126/252 trading days.
* Relative strength vs a benchmark over k days: stock momentum - benchmark momentum
  (percentage points of return).
* Volume ratio: today's volume / mean volume of the previous 50 sessions.
* Drawdown from 52-week high: close / max(close over last 252 sessions) - 1.
* Volume ratio (20-day): today's volume / mean volume of the previous 20 sessions.
* MACD cross up: the MACD histogram (MACD - signal) is > 0 on the last bar and
  <= 0 on the bar before it, i.e. MACD crossed above its signal on the last bar.
* Weekly bars: the last close of each calendar week, weeks ending Friday
  (pandas period W-FRI). The final week ends at the last bar given, so on a
  mid-week as-of date it is a partial week built only from sessions up to that
  date; nothing after the as-of date is used. Weekly fields end in _w and apply
  the daily formulas above to the weekly closes: rsi14_w is RSI(14) of weekly
  closes; macd_hist_w and macd_cross_up_w use MACD(12, 26, 9) of weekly closes
  and need at least MIN_WEEKLY_MACD weeks of history.
* Pivots: bar j is a pivot high when close[j] is strictly greater than every
  other close in [j - k, j + k] (a pivot low: strictly less). A pivot is only
  known at bar j + k, once the k bars after it exist; ties are not pivots.
* RSI divergence (k = 3, gap 5..60 bars between the two pivots): bearish on bar
  t when a pivot high j2 is confirmed at t (t = j2 + k), the previous pivot high
  j1 lies 5..60 bars before j2, price made a higher high (close[j2] > close[j1])
  and the oscillator a lower high (osc[j2] < osc[j1]). Bullish is the mirror on
  pivot lows: lower low in price, higher low in the oscillator. The signal is
  dated on the confirmation bar, so it never uses a bar after t.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

MONTH_DAYS = {1: 21, 3: 63, 6: 126, 12: 252}
MIN_WEEKLY_MACD = 35  # slow EMA (26) + signal EMA (9) weeks before a weekly MACD value is used


def sma(close: pd.Series, n: int) -> pd.Series:
    return close.rolling(n, min_periods=n).mean()


def above(a, b, rel: float = 1e-9):
    """a > b, with a gap inside rounding (|a - b| <= rel * |b|) counted as a tie, not above.

    A flat-priced name (a halted or acquired stock) has SMA50 == SMA200 exactly; how the two means
    round depends on the summation order, so a plain > would flip between implementations."""
    return (a - b) > rel * np.abs(b)


def ema(x: pd.Series, span: int) -> pd.Series:
    return x.ewm(span=span, adjust=False).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    c = close.to_numpy(dtype=float)
    out = np.full(len(c), np.nan)
    if len(c) <= n:
        return pd.Series(out, index=close.index)
    d = np.diff(c)
    gain, loss = np.clip(d, 0, None), np.clip(-d, 0, None)
    ag, al = gain[:n].mean(), loss[:n].mean()

    def val(g: float, l: float) -> float:
        if l == 0:
            return 100.0 if g > 0 else 50.0
        return 100.0 - 100.0 / (1.0 + g / l)

    out[n] = val(ag, al)
    for i in range(n, len(d)):
        ag = (ag * (n - 1) + gain[i]) / n
        al = (al * (n - 1) + loss[i]) / n
        out[i + 1] = val(ag, al)
    return pd.Series(out, index=close.index)


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    line = ema(close, fast) - ema(close, slow)
    sig = ema(line, signal)
    return pd.DataFrame({"macd": line, "signal": sig, "hist": line - sig})


def momentum(close: pd.Series, k: int) -> pd.Series:
    return close / close.shift(k) - 1.0


def volume_ratio(volume: pd.Series, n: int = 50) -> pd.Series:
    prior = volume.shift(1).rolling(n, min_periods=n).mean()
    return volume / prior


def weekly_close(dates, close: pd.Series) -> pd.Series:
    """Last close of each week (weeks end Friday), indexed by that session's date (YYYY-MM-DD).

    The last week may be partial: it ends at the final bar passed in, so the result
    never contains information from after that bar.
    """
    d = pd.to_datetime(pd.Series(list(dates)))
    c = pd.Series(close.to_numpy(dtype=float))
    last = c.groupby(d.dt.to_period("W-FRI").to_numpy()).tail(1).index
    return pd.Series(c.loc[last].to_numpy(), index=d.loc[last].dt.strftime("%Y-%m-%d").to_numpy())


def crossed_above(hist: pd.Series) -> bool | None:
    """True when hist goes from <= 0 on the previous bar to > 0 on the last bar; None if unknown."""
    if len(hist) < 2:
        return None
    a, b = float(hist.iloc[-2]), float(hist.iloc[-1])
    if not (np.isfinite(a) and np.isfinite(b)):
        return None
    return bool(a <= 0 < b)


def weekly_fields(dates, close: pd.Series) -> dict:
    """rsi14_w, macd_hist_w and macd_cross_up_w from weekly closes (see the module docstring)."""
    w = weekly_close(dates, close)
    out = {"rsi14_w": float(rsi(w, 14).iloc[-1]) if len(w) > 14 else np.nan,
           "macd_hist_w": np.nan, "macd_cross_up_w": None}
    if len(w) >= MIN_WEEKLY_MACD:
        h = macd(w)["hist"]
        out["macd_hist_w"] = float(h.iloc[-1])
        out["macd_cross_up_w"] = crossed_above(h)
    return out


def drawdown_from_high(close: pd.Series, n: int = 252) -> pd.Series:
    return close / close.rolling(n, min_periods=n).max() - 1.0


def snapshot(df: pd.DataFrame, bench: dict[str, pd.Series] | None = None) -> dict:
    """Latest-row technical fields for one symbol.

    df: rows for a single symbol sorted by date, columns close, volume.
    bench: benchmark close series indexed by date (same calendar as df).
    """
    c = df["close"].reset_index(drop=True).astype(float)
    v = df["volume"].reset_index(drop=True).astype(float)
    last = len(c) - 1
    out: dict = {"close": float(c.iloc[last]), "bars": len(c)}
    for n in (20, 50, 200):
        s = sma(c, n).iloc[last]
        out[f"sma{n}"] = float(s)
        out[f"pct_vs_sma{n}"] = float(c.iloc[last] / s - 1.0) if np.isfinite(s) else np.nan
    out["sma50_above_sma200"] = (bool(above(out["sma50"], out["sma200"]))
                                 if np.isfinite(out["sma50"]) and np.isfinite(out["sma200"]) else None)
    out["rsi14"] = float(rsi(c, 14).iloc[last])
    m = macd(c)
    out["macd"], out["macd_signal"], out["macd_hist"] = (float(m[k].iloc[last]) for k in ("macd", "signal", "hist"))
    for mth, k in MONTH_DAYS.items():
        out[f"mom_{mth}m"] = float(momentum(c, k).iloc[last]) if len(c) > k else np.nan
    out["volume_ratio_50d"] = float(volume_ratio(v).iloc[last])
    out["drawdown_52w"] = float(drawdown_from_high(c).iloc[last]) if len(c) >= 252 else np.nan
    out["volume_ratio_20d"] = float(volume_ratio(v, 20).iloc[last])
    out["macd_cross_up"] = crossed_above(m["hist"])
    if "date" in df:
        out.update(weekly_fields(df["date"], c))
    dv = (c * v).iloc[-50:]
    out["avg_dollar_volume_50d"] = float(dv.mean()) if len(dv) == 50 else np.nan
    if bench:
        dates = list(df["date"])
        for name, b in bench.items():
            b = b.reindex(dates)
            for mth in (1, 3, 6, 12):
                k = MONTH_DAYS[mth]
                if len(c) > k and np.isfinite(b.iloc[-1]) and np.isfinite(b.iloc[-1 - k]):
                    out[f"rs_{mth}m_vs_{name}"] = out[f"mom_{mth}m"] - float(b.iloc[-1] / b.iloc[-1 - k] - 1.0)
                else:
                    out[f"rs_{mth}m_vs_{name}"] = np.nan
    return out


def pivots(x, k: int = 3) -> tuple[np.ndarray, np.ndarray]:
    """(is_pivot_high, is_pivot_low) per bar, dated at the pivot itself (known only at j + k)."""
    a = np.asarray(x, dtype=float)
    n = len(a)
    hi, lo = np.zeros(n, dtype=bool), np.zeros(n, dtype=bool)
    if n < 2 * k + 1:
        return hi, lo
    w = np.lib.stride_tricks.sliding_window_view(a, 2 * k + 1)     # row r covers bars r .. r + 2k
    mid = w[:, k]
    rest = np.delete(w, k, axis=1)
    ok = np.isfinite(w).all(axis=1)
    hi[k:n - k] = ok & (mid > rest.max(axis=1))
    lo[k:n - k] = ok & (mid < rest.min(axis=1))
    return hi, lo


def divergence(price, osc, k: int = 3, min_gap: int = 5, max_gap: int = 60) -> tuple[np.ndarray, np.ndarray]:
    """(bearish, bullish) per bar, each True on the bar a divergence is confirmed (see module docstring)."""
    p = np.asarray(price, dtype=float)
    o = np.asarray(osc, dtype=float)
    n = len(p)
    bear, bull = np.zeros(n, dtype=bool), np.zeros(n, dtype=bool)
    hi, lo = pivots(p, k)
    for piv, out, sign in ((hi, bear, 1.0), (lo, bull, -1.0)):
        idx = np.nonzero(piv)[0]
        for a, b in zip(idx[:-1], idx[1:]):
            if not (min_gap <= b - a <= max_gap) or not (np.isfinite(o[a]) and np.isfinite(o[b])):
                continue
            # bearish: price higher high, oscillator lower high; bullish: lower low, higher low
            if sign * (p[b] - p[a]) > 0 and sign * (o[b] - o[a]) < 0:
                out[b + k] = True
    return bear, bull
