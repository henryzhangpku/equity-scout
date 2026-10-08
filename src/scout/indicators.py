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
"""

from __future__ import annotations

import numpy as np
import pandas as pd

MONTH_DAYS = {1: 21, 3: 63, 6: 126, 12: 252}


def sma(close: pd.Series, n: int) -> pd.Series:
    return close.rolling(n, min_periods=n).mean()


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
    out["sma50_above_sma200"] = (bool(out["sma50"] > out["sma200"])
                                 if np.isfinite(out["sma50"]) and np.isfinite(out["sma200"]) else None)
    out["rsi14"] = float(rsi(c, 14).iloc[last])
    m = macd(c)
    out["macd"], out["macd_signal"], out["macd_hist"] = (float(m[k].iloc[last]) for k in ("macd", "signal", "hist"))
    for mth, k in MONTH_DAYS.items():
        out[f"mom_{mth}m"] = float(momentum(c, k).iloc[last]) if len(c) > k else np.nan
    out["volume_ratio_50d"] = float(volume_ratio(v).iloc[last])
    out["drawdown_52w"] = float(drawdown_from_high(c).iloc[last]) if len(c) >= 252 else np.nan
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
