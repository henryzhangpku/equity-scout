"""Recent news headlines and summaries via Alpaca's news API (Benzinga wire).

Only the headline and the short summary are used and shown, never the full
article. Each item becomes its own Document so a citation links to the exact
story. Point-in-time: an item is visible only if it was published before the
as-of session's close (16:00 New York time).
"""

from __future__ import annotations

import html
from datetime import date, timedelta

import pandas as pd

from ..http import fetch_json
from .alpaca import _headers
from .base import Document

NEWS_URL = "https://data.alpaca.markets/v1beta1/news"


def _close_utc(d: date) -> str:
    ts = pd.Timestamp(f"{d.isoformat()} 16:00", tz="America/New_York").tz_convert("UTC")
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


class AlpacaNews:
    kind = "news"
    label = "news headlines and summaries (Alpaca / Benzinga), not full articles"

    def __init__(self, lookback_days: int = 30, max_items: int = 12):
        self.lookback_days = lookback_days
        self.max_items = max_items

    def news(self, symbol: str, as_of: date) -> list[Document]:
        params = {"symbols": symbol, "start": (as_of - timedelta(days=self.lookback_days)).isoformat(),
                  "end": _close_utc(as_of), "limit": 50, "sort": "desc", "include_content": "false"}
        j = fetch_json(NEWS_URL, source="alpaca_news", params=params, headers=_headers(),
                       cache_key=f"news {symbol} {as_of} {self.lookback_days}")
        out = []
        for it in (j or {}).get("news", []):
            if it.get("created_at", "") > params["end"]:
                continue
            syms = it.get("symbols") or []
            if len(syms) > 6:
                continue  # market round-ups that list many tickers say little about this one
            head = html.unescape(it.get("headline") or "").strip()
            summ = html.unescape(it.get("summary") or "").strip()
            if not head:
                continue
            day = it["created_at"][:10]
            out.append(Document(
                doc_id=f"{symbol}-news-{day}-{it['id']}", kind="news",
                title=f"{it.get('source', 'news').title()}: {head} ({day})",
                url=it.get("url") or "", filed=day,
                text=head + ("\n" + summ if summ else "")))
            if len(out) >= self.max_items:
                break
        return out
