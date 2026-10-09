"""Point-in-time monthly panels for backtests (`scout build-panels`).

For every month-end rebalance date, the full feature set as it was knowable on that date:

* price fields from bars up to and including that date only (indicators are computed on each
  symbol's full series and sampled at the date; every indicator is backward-looking, so no bar
  after the date can enter);
* fundamentals from SEC facts filed on or before the date (the same `fundamentals.compute`
  used for the live snapshot, called with that as-of date and that day's close);
* short interest from the latest FINRA settlement visible on the date (settlement + 8 business days);
* the universe rule applied as of the date (price >= $1, 50-day dollar volume >= $1M, a bar on the date).

Survivorship: the candidate list is today's universe. Companies that delisted before today are
missing from free data, which flatters history. Every backtest result says so.

Stored as one compressed NumPy archive: values[date, company, field] (float32, NaN = missing),
plus the close on every rebalance date (and the last close before it, for names that stopped
trading) used for holding-period returns.
"""

from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from . import fundamentals as F
from . import indicators as I
from .config import CACHE, DATA_DIR
from .data.finra import FinraShortInterest, visible_from
from .data.sec import SecData, extract_facts
from .snapshot import BENCHMARKS, MIN_ADV, MIN_PRICE
from .spec import FIELDS

PANEL_DIR = DATA_DIR / "panels"
PANEL_FILE = "panels.npz"
TECH_FIELDS = [f for f in FIELDS if FIELDS[f].group == "technical" or f == "avg_dollar_volume_50d"]
FUND_FIELDS = ["revenue_ttm", "revenue_growth_yoy", "revenue_growth_q_yoy", "revenue_growth_accel", "gross_margin",
               "operating_margin", "net_margin", "net_income_ttm", "fcf_ttm", "fcf_margin", "fcf_yield", "net_debt",
               "ev_to_sales", "market_cap", "ev"]
# every whitelisted field except relative strength vs the sector ETFs (XL*), which would add 44 columns
# and ~25 MB; a backtest that needs one of those is refused with a clear message
PANEL_FIELDS = [f for f in FIELDS if not (f.startswith("rs_") and "_vs_xl" in f)]


def _log(m: str) -> None:
    print(m, file=sys.stderr, flush=True)


def month_end_dates(trading_days: list[str], start: str, end: str) -> list[str]:
    """Last trading day of each calendar month in [start, end] (only complete months)."""
    s = pd.Series(pd.to_datetime(trading_days)).sort_values()
    s = s[(s >= pd.Timestamp(start)) & (s <= pd.Timestamp(end))]
    last = s.groupby(s.dt.to_period("M")).max()
    out = [d.date().isoformat() for d in last]
    final = s.max()
    if out and pd.Timestamp(out[-1]) == final and final < final + pd.offsets.BMonthEnd(0):
        out = out[:-1]  # data stops before the month is over: not a month end
    return out


def series_features(g: pd.DataFrame, bench: dict[str, pd.Series]) -> pd.DataFrame:
    """Every technical field for every date of one symbol's history (backward-looking only).
    Matches indicators.snapshot evaluated on the series truncated at each date."""
    g = g.sort_values("date")
    dates = list(g["date"])
    c = g["close"].astype(float).reset_index(drop=True)
    v = g["volume"].astype(float).reset_index(drop=True)
    out = pd.DataFrame(index=range(len(c)))
    out["close"] = c
    for n in (20, 50, 200):
        s = I.sma(c, n)
        out[f"sma{n}"] = s
        out[f"pct_vs_sma{n}"] = c / s - 1.0
    a, b = out["sma50"], out["sma200"]
    out["sma50_above_sma200"] = np.where(a.notna() & b.notna(), (a > b).astype(float), np.nan)
    out["rsi14"] = I.rsi(c, 14)
    m = I.macd(c)
    out["macd"], out["macd_signal"], out["macd_hist"] = m["macd"], m["signal"], m["hist"]
    for mth, k in I.MONTH_DAYS.items():
        out[f"mom_{mth}m"] = I.momentum(c, k)
    out["volume_ratio_50d"] = I.volume_ratio(v)
    out["drawdown_52w"] = I.drawdown_from_high(c)
    out["avg_dollar_volume_50d"] = (c * v).rolling(50, min_periods=50).mean()
    for name, bs in bench.items():
        bv = bs.reindex(dates).to_numpy(dtype=float)
        for mth in (1, 3, 6, 12):
            k = I.MONTH_DAYS[mth]
            br = np.full(len(c), np.nan)
            if len(c) > k:
                br[k:] = bv[k:] / bv[:-k] - 1.0
            out[f"rs_{mth}m_vs_{name}"] = out[f"mom_{mth}m"] - br
    out["date"] = dates
    return out.set_index("date")


def _fund_job(job: tuple) -> tuple[int, dict]:
    """(company index, {date: values}) for one company across all rebalance dates (process worker)."""
    i, cik, prices = job
    sec = SecData()
    try:
        facts = extract_facts(sec.raw_facts(cik))
    except Exception:  # noqa: BLE001 - a missing filer is a gap, not a failure
        return i, {}
    res = {}
    for d, px in prices.items():
        try:
            res[d] = F.compute(facts, d, px).values
        except Exception:  # noqa: BLE001
            res[d] = {}
    return i, res


def build(start: str = "2023-01-01", end: str | None = None, as_of: str = "2026-10-08",
          prices_path: Path | None = None, workers: int = 7) -> Path:
    t0 = time.time()
    base = pd.read_csv(DATA_DIR / "snapshots" / as_of / "features.csv.gz", low_memory=False,
                       usecols=["symbol", "cik", "name", "sic"])
    prices_path = prices_path or CACHE / "panels" / "prices_long.csv.gz"
    bars = pd.read_csv(prices_path, compression="gzip")
    trading = sorted(bars.loc[bars["symbol"] == "SPY", "date"].unique())
    end = end or trading[-1]
    rebal = month_end_dates(trading, start, end)
    # one extra slice on the live snapshot date, used only to check the panel pipeline against the snapshot
    dates = rebal + ([as_of] if as_of not in rebal and as_of in set(trading) else [])
    _log(f"panels: {len(rebal)} rebalances {rebal[0]} .. {rebal[-1]} (+ check slice {as_of}), {len(base)} companies")

    bench = {b.lower(): bars[bars["symbol"] == b].set_index("date")["close"] for b in BENCHMARKS}
    syms = list(base["symbol"])
    N, D = len(syms), len(dates)
    fidx = {f: j for j, f in enumerate(PANEL_FIELDS)}
    vals = np.full((D, N, len(PANEL_FIELDS)), np.nan, dtype=np.float32)
    close_at = np.full((D, N), np.nan)          # close on the rebalance date
    last_close = np.full((D, N), np.nan)        # last close on or before the rebalance date
    last_date = np.full((D, N), "", dtype=object)
    in_universe = np.zeros((D, N), dtype=bool)

    by_sym = {s: g for s, g in bars.groupby("symbol", sort=False)}
    for n, s in enumerate(syms):
        g = by_sym.get(s)
        if g is None or len(g) < 60:
            continue
        sf = series_features(g, bench)
        idx = sf.index
        for di, d in enumerate(dates):
            pos = idx.searchsorted(d, side="right") - 1
            if pos < 0:
                continue
            last_close[di, n] = sf["close"].iloc[pos]
            last_date[di, n] = idx[pos]
            if idx[pos] != d:
                continue  # no bar on the rebalance date: not tradable that day
            close_at[di, n] = sf["close"].iloc[pos]
            row = sf.iloc[pos]
            if pos + 1 < 60:
                continue
            for f in TECH_FIELDS:
                if f in row.index:
                    vals[di, n, fidx[f]] = row[f]
            for f in [c for c in sf.columns if c.startswith("rs_")]:
                vals[di, n, fidx[f]] = row[f]
            in_universe[di, n] = (row["close"] >= MIN_PRICE) and (row["avg_dollar_volume_50d"] >= MIN_ADV)
        if n % 500 == 0:
            _log(f"  prices {n}/{N}")

    jobs = [(n, int(base["cik"].iloc[n]), {d: float(close_at[di, n]) for di, d in enumerate(dates)
                                            if np.isfinite(close_at[di, n])}) for n in range(N)]
    with ProcessPoolExecutor(workers) as ex:
        for k, (n, res) in enumerate(ex.map(_fund_job, jobs, chunksize=8)):
            for di, d in enumerate(dates):
                for f, x in (res.get(d) or {}).items():
                    if f in fidx and x is not None and np.isfinite(x):
                        vals[di, n, fidx[f]] = x
            if k % 500 == 0:
                _log(f"  fundamentals {k}/{N}")

    # short interest: latest settlement visible on each date
    fin = FinraShortInterest(f"panels {as_of}")
    si_dates = []
    for d in dates:
        cands = [s for s in fin.settlement_dates(date.fromisoformat(d), lookback_days=40) if visible_from(s) <= d]
        si_dates.append(cands[-1] if cands else None)
    shares = vals[:, :, fidx["market_cap"]] / np.where(close_at > 0, close_at, np.nan)
    pos = {s: n for n, s in enumerate(syms)}
    for di, s in enumerate(si_dates):
        if not s:
            continue
        rows = fin.settlement_rows(s)
        for sym, q, dtc in zip(rows["symbolCode"], rows["currentShortPositionQuantity"], rows["daysToCoverQuantity"]):
            n = pos.get(str(sym).upper().replace("-", "."))
            if n is None:
                continue
            try:
                q = float(q)
            except (TypeError, ValueError):
                continue
            if np.isfinite(shares[di, n]) and shares[di, n] > 0:
                vals[di, n, fidx["short_pct_shares_out"]] = q / shares[di, n]
            try:
                vals[di, n, fidx["days_to_cover"]] = float(dtc)
            except (TypeError, ValueError):
                pass

    spy = bench["spy"]
    PANEL_DIR.mkdir(parents=True, exist_ok=True)
    out = PANEL_DIR / PANEL_FILE
    R = len(rebal)
    np.savez_compressed(out, values=vals[:R], close_at=close_at[:R], last_close=last_close[:R],
                        last_date=last_date[:R].astype("U10"), in_universe=in_universe[:R],
                        dates=np.array(rebal), symbols=np.array(syms), fields=np.array(PANEL_FIELDS),
                        names=np.array(base["name"].astype(str).tolist(), dtype=str), sic=base["sic"].to_numpy(dtype=float),
                        spy_close=np.array([spy.get(d, np.nan) for d in rebal]),
                        check_date=np.array(dates[R:]), check_values=vals[R:], check_universe=in_universe[R:])
    meta = {"dates": rebal, "n_rebalances": R, "n_companies": N, "as_of_universe": as_of,
            "short_interest_settlements": si_dates, "build_seconds": round(time.time() - t0),
            "bytes": out.stat().st_size, "fields": PANEL_FIELDS,
            "price_history": [str(bars["date"].min()), str(bars["date"].max())]}
    (PANEL_DIR / "panels.json").write_text(json.dumps(meta, indent=1))
    _log(f"panels -> {out} ({out.stat().st_size / 1e6:.1f} MB) in {meta['build_seconds']} s")
    return out
