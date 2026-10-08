"""Build the point-in-time feature table for one as-of date.

    universe (Alpaca, major exchanges) x SEC ticker map  ->  common stocks with a CIK
    daily bars (Alpaca SIP, adjusted)                     ->  technical fields
    liquidity floor (price >= $1, 50d ADV >= $1M)          ->  investable universe
    SEC companyfacts + submissions                         ->  PIT fundamentals, SIC
    FINRA short interest                                   ->  short % of shares, days to cover

Everything is cached under .cache/; the finished table is written to
.cache/snapshots/<as_of>/features.csv.gz with a manifest of SHA-256 hashes so a
run can state exactly which data it used.
"""

from __future__ import annotations

import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from . import fundamentals as F
from . import indicators as I
from .config import CACHE
from .data.alpaca import AlpacaPrices
from .data.finra import FinraShortInterest
from .data.sec import SecData, extract_facts, periodic_filer, sic_of

BENCHMARKS = ["SPY", "QQQ", "IWM", "SMH", "SOXX", "XLK", "XLF", "XLE", "XLV", "XLI", "XLU",
              "XLY", "XLP", "XLB", "XLRE", "XLC"]
MIN_PRICE = 1.0
MIN_ADV = 1_000_000.0
HISTORY_DAYS = 800


def snapshot_dir(as_of: date | str) -> Path:
    return CACHE / "snapshots" / str(as_of)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def build(as_of: date, workers: int = 6) -> Path:
    out = snapshot_dir(as_of)
    out.mkdir(parents=True, exist_ok=True)
    tag = as_of.isoformat()
    alp, sec = AlpacaPrices(tag), SecData()

    # 1. universe
    secs = alp.universe()
    tick = sec.ticker_map(tag)
    tick = tick[tick["exchange"].isin(["Nasdaq", "NYSE", "CBOE"])]
    t2c = dict(zip(tick["ticker"], tick["cik"]))
    t2n = dict(zip(tick["ticker"], tick["name"]))
    uni = []
    for s in secs:
        key = s.symbol.replace(".", "-").replace("/", "-")
        if key in t2c:
            uni.append({"symbol": s.symbol, "cik": int(t2c[key]), "name": t2n[key], "exchange": s.exchange})
    uni = pd.DataFrame(uni)
    _log(f"universe: {len(secs)} tradable on major exchanges, {len(uni)} with an SEC CIK")

    # 2. prices
    prices_p = out / "prices.csv.gz"
    if not prices_p.exists():
        syms = sorted(set(uni["symbol"]) | set(BENCHMARKS))
        bars = alp.daily_bars(syms, as_of - timedelta(days=HISTORY_DAYS), as_of)
        bars = bars[bars["date"] <= tag]
        bars.to_csv(prices_p, index=False, compression="gzip")
    bars = pd.read_csv(prices_p, compression="gzip")
    _log(f"prices: {bars['symbol'].nunique()} symbols, {len(bars)} bars, last date {bars['date'].max()}")

    # 3. technicals
    bench = {b: bars[bars["symbol"] == b].set_index("date")["close"] for b in BENCHMARKS}
    tech = {}
    last_day = bars["date"].max()
    for sym, g in bars.groupby("symbol", sort=False):
        if sym in BENCHMARKS or len(g) < 60:
            continue
        if g["date"].iloc[-1] != last_day:
            continue  # no bar on the as-of session: halted or delisted
        tech[sym] = I.snapshot(g, {b.lower(): s for b, s in bench.items()})
    tech = pd.DataFrame.from_dict(tech, orient="index")
    tech.index.name = "symbol"
    df = uni.merge(tech.reset_index(), on="symbol", how="inner")
    df = df[(df["close"] >= MIN_PRICE) & (df["avg_dollar_volume_50d"] >= MIN_ADV)]
    # one listing per company: keep the most liquid share class
    df = df.sort_values("avg_dollar_volume_50d", ascending=False).drop_duplicates("cik")
    _log(f"liquid universe: {len(df)} companies")

    # 4. fundamentals + industry
    def one(row) -> dict:
        try:
            raw = sec.raw_facts(row.cik)
            facts = extract_facts(raw)
            fu = F.compute(facts, as_of, row.close)
            prof = sec.profile(row.cik)
            sic, sic_desc = sic_of(prof)
            periodic, last_form = periodic_filer(prof, as_of)
        except Exception as e:  # one bad filer must not sink the snapshot; the gap is recorded
            return {"symbol": row.symbol, "prov_error": f"{type(e).__name__}: {e}"[:200]}
        return {"symbol": row.symbol, "sic": sic, "sic_desc": sic_desc, "periodic_filer": periodic,
                "last_periodic_form": last_form, **fu.values, **{f"prov_{k}": v for k, v in fu.provenance.items()}}

    rows = []
    with ThreadPoolExecutor(workers) as ex:
        for i, r in enumerate(ex.map(one, df.itertuples(index=False))):
            rows.append(r)
            if i % 250 == 0:
                _log(f"  fundamentals {i}/{len(df)}")
    df = df.merge(pd.DataFrame(rows), on="symbol", how="left")
    # operating companies only: must file 10-K/10-Q/20-F/40-F; commodity and crypto trusts (SIC 6221) are out
    n0 = len(df)
    df = df[(df["periodic_filer"] == True) & (df["sic"] != 6221)]  # noqa: E712
    _log(f"operating companies: {len(df)} (dropped {n0 - len(df)} funds, trusts and non-filers)")

    # 5. short interest
    si = FinraShortInterest(tag).latest(as_of)
    si["symbol"] = si["symbol"].str.replace("-", ".")
    df = df.merge(si[["symbol", "settlement_date", "short_shares", "days_to_cover"]]
                  .rename(columns={"settlement_date": "si_settlement_date"}), on="symbol", how="left")
    df["short_pct_shares_out"] = np.where(df["shares_out"] > 0, df["short_shares"] / df["shares_out"], np.nan)

    df = df.sort_values("symbol").reset_index(drop=True)
    feat_p = out / "features.csv.gz"
    df.to_csv(feat_p, index=False, compression="gzip")
    manifest = {
        "as_of": tag, "last_price_date": str(bars["date"].max()),
        "universe_rule": f"tradable US-listed (NYSE/Nasdaq/AMEX/Arca/BATS) operating companies with an SEC CIK "
                         f"and a 10-K/10-Q/20-F/40-F in the last 18 months; close >= ${MIN_PRICE:g}; "
                         f"50-day avg dollar volume >= ${MIN_ADV:,.0f}; one listing per CIK",
        "n_companies": int(len(df)),
        "short_interest_settlement": None if si.empty else str(si["settlement_date"].iloc[0]),
        "benchmark_closes": benchmark_closes(bars, tag),
        "files": {p.name: {"sha256": sha256_file(p), "bytes": p.stat().st_size} for p in (prices_p, feat_p)},
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    _log(f"features: {len(df)} rows -> {feat_p}")
    return feat_p


def benchmark_closes(bars: pd.DataFrame, as_of: str) -> dict:
    b = bars[(bars["symbol"].isin(BENCHMARKS)) & (bars["date"] == as_of)]
    return {r.symbol: float(r.close) for r in b.itertuples()}


def load(as_of: date | str) -> tuple[pd.DataFrame, dict]:
    d = snapshot_dir(as_of)
    return (pd.read_csv(d / "features.csv.gz", compression="gzip"),
            json.loads((d / "manifest.json").read_text()))
