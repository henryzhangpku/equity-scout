"""Data-layer interfaces.

Each layer is a small Protocol so a licensed source can replace the free one
without touching the screen, ranking or narrative code:

    PriceSource         Alpaca daily bars        -> Bloomberg BQL / LSEG / Capital IQ pricing
    FundamentalSource   SEC XBRL companyfacts    -> BQL fundamentals / Capital IQ financials
    ShortInterestSource FINRA consolidated SI    -> licensed SI / securities-lending data
    DocumentSource      EDGAR 8-K ex.99.1, MD&A  -> same filings via a document store
    TranscriptSource    (none free)              -> licensed earnings-call transcripts

All sources are point-in-time: callers pass `as_of` and must not receive
anything that was not public on that date.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Protocol

import pandas as pd


@dataclass(frozen=True)
class Security:
    symbol: str
    name: str
    exchange: str
    cik: int | None = None


class PriceSource(Protocol):
    def universe(self) -> list[Security]: ...

    def daily_bars(self, symbols: list[str], start: date, end: date) -> pd.DataFrame:
        """Long frame: date, symbol, open, high, low, close, volume (adjusted)."""
        ...


class FundamentalSource(Protocol):
    def facts(self, cik: int) -> pd.DataFrame:
        """Long frame of facts: concept, unit, start, end, val, fy, fp, form, filed, accn."""
        ...

    def profile(self, cik: int) -> dict:
        """sic, sicDescription, name, tickers, recent filings."""
        ...


class ShortInterestSource(Protocol):
    available: bool

    def latest(self, as_of: date) -> pd.DataFrame:
        """symbol, settlement_date, visible_from, short_shares, days_to_cover, avg_daily_volume."""
        ...


@dataclass
class Document:
    doc_id: str          # stable id used in citations, e.g. "AAPL-8K-0000320193-26-000071-ex99"
    kind: str            # "earnings_release" | "mdna" | "transcript"
    title: str
    url: str             # canonical SEC URL, shown next to every citation
    filed: str           # YYYY-MM-DD
    text: str = field(repr=False)
    full_length: int | None = None   # set when `text` is a stored excerpt of a longer original


class DocumentSource(Protocol):
    def earnings_documents(self, symbol: str, cik: int, as_of: date) -> list[Document]: ...


class TranscriptSource(Protocol):
    available: bool

    def transcripts(self, symbol: str, as_of: date) -> list[Document]: ...


class NoTranscripts:
    """Earnings-call transcripts are not available from a free, redistributable source.

    The interface exists so a licensed feed can drop in; until then the narrative
    engine is told explicitly that no call transcript was consulted.
    """

    available = False
    reason = "earnings-call transcripts are licensed content; no free source is used"

    def transcripts(self, symbol: str, as_of: date) -> list[Document]:
        return []
