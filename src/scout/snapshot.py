"""Build the point-in-time feature table for one as-of date.

    universe (Alpaca, major exchanges) x SEC ticker map  ->  common stocks with a CIK
    daily bars (Alpaca SIP, adjusted)                     ->  technical fields
      (or OpenBB with a keyless provider: build(..., prices="openbb"), data/openbb_source.py)
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
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from . import fundamentals as F
from . import indicators as I
from .config import CACHE, PRICE_SOURCE
from .data.alpaca import AlpacaPrices
from .data.finra import FinraShortInterest
from .data.sec import SecData, extract_facts, periodic_filer, sic_of

BENCHMARKS = ["SPY", "QQQ", "IWM", "SMH", "SOXX", "XLK", "XLF", "XLE", "XLV", "XLI", "XLU",
              "XLY", "XLP", "XLB", "XLRE", "XLC"]
MIN_PRICE = 1.0
MIN_ADV = 1_000_000.0
HISTORY_DAYS = 800


def price_source(name: str, snapshot: str):
    """The PriceSource selected by name: 'alpaca' (default) or 'openbb' (optional extra)."""
    if name == "alpaca":
        return AlpacaPrices(snapshot)
    if name == "openbb":
        from .data.openbb_source import OpenBBPrices
        return OpenBBPrices(snapshot)
    raise ValueError(f"unknown price source {name!r} (choose alpaca or openbb)")


def snapshot_dir(as_of: date | str) -> Path:
    return CACHE / "snapshots" / str(as_of)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def build(as_of: date, workers: int = 6, prices: str | None = None) -> Path:
    prices = prices or PRICE_SOURCE
    tag = as_of.isoformat()
    alp = price_source(prices, tag)  # first, so a missing optional package fails before any download
    out = snapshot_dir(as_of)
    out.mkdir(parents=True, exist_ok=True)
    sec = SecData()

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
    prices_p = out / ("prices.csv.gz" if prices == "alpaca" else f"prices-{prices}.csv.gz")
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

    # 4. fundamentals + industry: fetch with polite threads (network), compute in processes (CPU)
    jobs = list(df[["symbol", "cik", "close"]].itertuples(index=False, name=None))
    with ThreadPoolExecutor(workers) as ex:
        for i, _ in enumerate(ex.map(lambda j: (sec.raw_facts(j[1]), sec.profile(j[1])) and None, jobs)):
            if i % 500 == 0:
                _log(f"  filings fetched {i}/{len(jobs)}")
    rows = []
    with ProcessPoolExecutor(max(1, (os.cpu_count() or 2) - 1)) as ex:
        for i, r in enumerate(ex.map(_fundamentals_row, [(s, c, px, tag) for s, c, px in jobs], chunksize=20)):
            rows.append(r)
            if i % 500 == 0:
                _log(f"  fundamentals {i}/{len(jobs)}")
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
        **({} if prices == "alpaca" else {"price_source": prices}),
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


def _fundamentals_row(job: tuple) -> dict:
    """One company's PIT fundamentals and profile, from the on-disk cache (process-pool worker)."""
    symbol, cik, close, as_of = job
    sec = SecData()
    try:
        fu = F.compute(extract_facts(sec.raw_facts(cik)), as_of, close)
        prof = sec.profile(cik)
        sic, sic_desc = sic_of(prof)
        periodic, last_form = periodic_filer(prof, date.fromisoformat(as_of))
    except Exception as e:  # one bad filer must not sink the snapshot; the gap is recorded
        return {"symbol": symbol, "prov_error": f"{type(e).__name__}: {e}"[:200]}
    return {"symbol": symbol, "sic": sic, "sic_desc": sic_desc, "periodic_filer": periodic,
            "last_periodic_form": last_form, **fu.values, **{f"prov_{k}": v for k, v in fu.provenance.items()}}


def benchmark_closes(bars: pd.DataFrame, as_of: str) -> dict:
    b = bars[(bars["symbol"].isin(BENCHMARKS)) & (bars["date"] == as_of)]
    return {r.symbol: float(r.close) for r in b.itertuples()}


def add_technicals(as_of: date | str, dest: Path, fields: tuple[str, ...] | None = None) -> Path:
    """Add technical fields that did not exist when a snapshot was built, from the same cached bars, no network.

    The bars are the snapshot's own prices.csv.gz (its SHA-256 must equal the one in dest/manifest.json),
    the per-symbol computation is the one `build` runs, and every technical field the snapshot already has
    must be reproduced exactly before anything is written. The new columns go to a sidecar
    (pipeline.ADDED_FEATURES, with ADDED_MANIFEST) that load_features joins on symbol; features.csv.gz and
    manifest.json are not touched, so the hashes cited by recorded runs stay valid.
    """
    from .pipeline import ADDED_FEATURES, ADDED_MANIFEST
    from .spec import MTF_FIELDS
    fields = tuple(fields or MTF_FIELDS)
    tag = str(as_of)
    manifest = json.loads((dest / "manifest.json").read_text())
    prices_p = snapshot_dir(tag) / "prices.csv.gz"
    want = manifest["files"]["prices.csv.gz"]["sha256"]
    if not prices_p.exists() or sha256_file(prices_p) != want:
        raise RuntimeError(f"{prices_p} is missing or is not the file the snapshot was built from (sha256 {want})")
    feat = pd.read_csv(dest / "features.csv.gz", compression="gzip", low_memory=False, float_precision="round_trip")
    present = [f for f in fields if f in feat.columns]
    if present:
        raise RuntimeError(f"already in the snapshot: {present}")
    bars = pd.read_csv(prices_p, compression="gzip")  # read exactly as build() reads it
    bench = {b.lower(): bars[bars["symbol"] == b].set_index("date")["close"] for b in BENCHMARKS}
    groups = dict(tuple(bars.groupby("symbol", sort=False)))
    rows, checked, mismatches = [], None, []
    for r in feat.to_dict("records"):
        t = I.snapshot(groups[r["symbol"]], bench)
        checked = checked or [k for k in t if k in feat.columns]
        for k in checked:
            a, b = r[k], t[k]
            same = (pd.isna(a) and pd.isna(b)) if (pd.isna(a) or pd.isna(b)) else (
                str(a).lower() == str(b).lower() if isinstance(b, bool) else float(a) == float(b))
            if not same:
                mismatches.append((r["symbol"], k, a, b))
        rows.append({"symbol": r["symbol"], **{f: t[f] for f in fields}})
    if mismatches:
        raise RuntimeError(f"{len(mismatches)} existing values not reproduced from the cached bars, e.g. {mismatches[:3]}")
    added_p = dest / ADDED_FEATURES
    pd.DataFrame(rows, columns=["symbol", *fields]).to_csv(added_p, index=False, compression="gzip")
    (dest / ADDED_MANIFEST).write_text(json.dumps({
        "as_of": tag, "fields": list(fields), "n_companies": len(rows),
        "method": "snapshot.add_technicals: indicators.snapshot on the snapshot's own cached daily bars, no network; "
                  f"all {len(checked)} technical fields already in features.csv.gz reproduced exactly first",
        "verified_fields": checked,
        "source": {"prices.csv.gz": manifest["files"]["prices.csv.gz"],
                   "features.csv.gz": manifest["files"]["features.csv.gz"]},
        "files": {added_p.name: {"sha256": sha256_file(added_p), "bytes": added_p.stat().st_size}},
    }, indent=2) + "\n")
    _log(f"added {list(fields)} for {len(rows)} companies -> {added_p} ({len(checked)} existing fields reproduced)")
    return added_p


def load(as_of: date | str) -> tuple[pd.DataFrame, dict]:
    d = snapshot_dir(as_of)
    return (pd.read_csv(d / "features.csv.gz", compression="gzip"),
            json.loads((d / "manifest.json").read_text()))
