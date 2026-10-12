"""OpenBB Platform as a PriceSource: same long frame as AlpacaPrices, no API key.

OpenBB (https://openbb.co, PyPI `openbb`, Platform v4: `from openbb import obb`) is an
open-source data layer over many providers. This adapter uses keyless providers only:

    universe      obb.equity.search(provider="sec")            SEC company ticker list
    daily_bars    obb.equity.price.historical(provider="yfinance",
                                              adjustment="splits_and_dividends")

so a feature snapshot can be built with no data subscription at all
(`scout build --as-of ... --prices openbb`). The output matches AlpacaPrices.daily_bars
exactly: columns date (YYYY-MM-DD string), symbol, open, high, low, close, volume, split- and
dividend-adjusted, sorted by symbol then date, and never a bar after `end`. As with Alpaca's
`adjustment=all`, the adjustment is as of the day the bars are fetched: a split or dividend after
`end` rescales earlier price levels; a split leaves returns and the ratio indicators unchanged and a
dividend moves them only slightly. The snapshot stores the bars it fetched, so a rebuild is repeatable.

Fundamentals stay on SEC companyfacts (data/sec.py): free, and point-in-time because every
fact carries its `filed` date. OpenBB can serve fundamentals too, but the providers that do
(fmp, intrinio, polygon, tiingo) need a key, and their statements are not gated by filing date,
so a swap would also need a point-in-time check. The `sec` provider in OpenBB reads the same
companyfacts this package already uses.

`openbb` is an optional dependency (`uv sync --extra openbb`). It is imported only when this
source is constructed, so the rest of the package works without it.
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from .base import Security

COLUMNS = ["date", "symbol", "open", "high", "low", "close", "volume"]
INSTALL_HINT = ("OpenBB is not installed. Install the optional extra with `uv sync --extra openbb` "
                "(or `pip install 'equity-scout[openbb]'`), or use the default `--prices alpaca`.")


class SourceUnavailable(RuntimeError):
    """A selected data source cannot be used here (for example, its package is not installed)."""


def load_obb():
    """Import OpenBB lazily; raise SourceUnavailable with an install hint if it is missing."""
    try:
        from openbb import obb  # noqa: PLC0415 - optional, heavy import
    except ImportError as e:
        raise SourceUnavailable(INSTALL_HINT) from e
    return obb


def to_provider_symbol(symbol: str) -> str:
    """Alpaca / SEC share-class notation (BRK.B) -> Yahoo notation (BRK-B)."""
    return symbol.replace(".", "-").replace("/", "-")


def _frame(result) -> pd.DataFrame:
    """An OBBject (or anything with to_df / results) as a plain DataFrame with a date column."""
    if hasattr(result, "to_df"):
        df = result.to_df()
    else:
        rows = getattr(result, "results", result) or []
        df = pd.DataFrame([r.model_dump() if hasattr(r, "model_dump") else dict(r) for r in rows])
    df = df.reset_index() if "date" not in df.columns else df.reset_index(drop=True)
    return df


class OpenBBPrices:
    """PriceSource backed by OpenBB with a keyless provider (default yfinance)."""

    def __init__(self, snapshot: str, provider: str = "yfinance", universe_provider: str = "sec",
                 chunk: int = 50, obb=None):
        self.snapshot = snapshot  # kept for parity with AlpacaPrices; the snapshot caches the bars it gets
        self.provider = provider
        self.universe_provider = universe_provider
        self.chunk = chunk
        self.obb = obb if obb is not None else load_obb()
        self.failed: list[str] = []  # symbols the provider returned nothing for

    def universe(self) -> list[Security]:
        df = _frame(self.obb.equity.search(query="", provider=self.universe_provider))
        out = {}
        for r in df.to_dict("records"):
            sym = str(r.get("symbol") or "").strip().upper()
            if not sym or sym in out:
                continue
            cik = r.get("cik")
            try:
                cik = int(cik) if cik is not None and cik == cik else None
            except (TypeError, ValueError):
                cik = None
            out[sym] = Security(symbol=sym, name=str(r.get("name") or ""), exchange=str(r.get("exchange") or ""),
                                cik=cik)
        return sorted(out.values(), key=lambda s: s.symbol)

    def _fetch(self, symbols: list[str], start: date, end: date) -> pd.DataFrame:
        back = {to_provider_symbol(s): s for s in symbols}
        res = self.obb.equity.price.historical(
            symbol=",".join(back), start_date=start.isoformat(), end_date=end.isoformat(),
            interval="1d", adjustment="splits_and_dividends", provider=self.provider,
        )
        df = _frame(res)
        if df.empty:
            return df
        if "symbol" not in df.columns:
            if len(symbols) != 1:
                raise ValueError("provider returned bars without a symbol column for a multi-symbol request")
            df["symbol"] = to_provider_symbol(symbols[0])
        df["symbol"] = df["symbol"].map(lambda s: back.get(str(s)))
        return df[df["symbol"].notna()]

    def daily_bars(self, symbols: list[str], start: date, end: date) -> pd.DataFrame:
        frames = []
        for i in range(0, len(symbols), self.chunk):
            batch = symbols[i:i + self.chunk]
            try:
                frames.append(self._fetch(batch, start, end))
            except Exception:  # noqa: BLE001 - one bad ticker can fail a whole request; retry one by one
                for s in batch:
                    try:
                        frames.append(self._fetch([s], start, end))
                    except Exception:  # noqa: BLE001 - no data for this symbol is a gap, recorded below
                        self.failed.append(s)
        frames = [f for f in frames if not f.empty]
        if not frames:
            return pd.DataFrame(columns=COLUMNS)
        df = pd.concat(frames, ignore_index=True)
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        # point in time: nothing after `end` (or before `start`), whatever the provider sent
        df = df[(df["date"] >= start.isoformat()) & (df["date"] <= end.isoformat())]
        df = df.dropna(subset=["close"])
        wanted = set(symbols)
        df = df[df["symbol"].isin(wanted)]
        got = set(df["symbol"])
        self.failed += [s for s in symbols if s not in got and s not in self.failed]
        df = df.drop_duplicates(["symbol", "date"], keep="last")
        return df[COLUMNS].sort_values(["symbol", "date"]).reset_index(drop=True)

