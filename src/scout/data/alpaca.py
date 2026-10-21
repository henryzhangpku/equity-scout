"""Alpaca market data: US equity universe and daily adjusted bars.

Read-only use of the assets and market-data endpoints. No orders, no account
endpoints. Keys come from ALPACA_API_KEY / ALPACA_API_SECRET.
"""

from __future__ import annotations

import json
import os
from datetime import date, datetime, timedelta, timezone

import pandas as pd

from ..config import secret
from ..http import fetch_json
from .base import Security

MAJOR_EXCHANGES = {"NYSE", "NASDAQ", "AMEX", "ARCA", "BATS"}
# The asset list comes from the PAPER trading host by default, so the service
# runs on a paper key and never holds a live-account key (a live key could
# trade if it leaked). Bars come from the market-data host, which accepts paper
# keys. ALPACA_ASSETS_URL overrides it.
ASSETS_URL = os.environ.get("ALPACA_ASSETS_URL", "https://paper-api.alpaca.markets/v2/assets")
BARS_URL = "https://data.alpaca.markets/v2/stocks/bars"


def _sip_safe_end(end: date, now: datetime | None = None) -> str:
    """The bars request's end: the requested day, but never inside the last
    16 minutes. Plans without real-time SIP refuse the newest 15 minutes, and a
    paper key may not carry the live account's data plan; daily bars do not need
    today's last quarter hour."""
    now = now or datetime.now(timezone.utc)
    limit = now - timedelta(minutes=16)
    day_end = datetime.combine(end, datetime.max.time(), tzinfo=timezone.utc)
    if day_end <= limit:
        return end.isoformat()
    return limit.strftime("%Y-%m-%dT%H:%M:%SZ")


def _headers() -> dict:
    k, s = secret("ALPACA_API_KEY"), secret("ALPACA_API_SECRET")
    if not (k and s):
        raise RuntimeError("ALPACA_API_KEY / ALPACA_API_SECRET not set (needed only to refresh price data)")
    return {"APCA-API-KEY-ID": k, "APCA-API-SECRET-KEY": s}


class AlpacaPrices:
    """PriceSource backed by Alpaca (SIP feed, split+dividend adjusted)."""

    def __init__(self, snapshot: str):
        # snapshot tag pins the cache, e.g. the as-of date, so reruns are identical
        self.snapshot = snapshot

    def universe(self) -> list[Security]:
        assets = fetch_json(
            ASSETS_URL, source="alpaca", params={"status": "active", "asset_class": "us_equity"},
            headers=_headers(), cache_key=f"assets {self.snapshot}",
        )
        out = []
        for a in assets:
            if a.get("tradable") and a.get("exchange") in MAJOR_EXCHANGES:
                out.append(Security(symbol=a["symbol"], name=a.get("name", ""), exchange=a["exchange"]))
        return sorted(out, key=lambda s: s.symbol)

    def daily_bars(self, symbols: list[str], start: date, end: date, chunk: int = 100) -> pd.DataFrame:
        frames = []
        end_param = _sip_safe_end(end)
        for i in range(0, len(symbols), chunk):
            batch = symbols[i:i + chunk]
            token = None
            page = 0
            while True:
                params = {
                    "symbols": ",".join(batch), "timeframe": "1Day",
                    "start": start.isoformat(), "end": end_param,
                    "adjustment": "all", "feed": "sip", "limit": 10000,
                }
                if token:
                    params["page_token"] = token
                key = f"bars {self.snapshot} {start} {end} {json.dumps(batch)} p{page}"
                j = fetch_json(BARS_URL, source="alpaca", params=params, headers=_headers(), cache_key=key)
                for sym, bars in (j.get("bars") or {}).items():
                    if bars:
                        df = pd.DataFrame(bars)
                        df["symbol"] = sym
                        frames.append(df)
                token = j.get("next_page_token")
                page += 1
                if not token:
                    break
        if not frames:
            return pd.DataFrame(columns=["date", "symbol", "open", "high", "low", "close", "volume"])
        df = pd.concat(frames, ignore_index=True)
        df["date"] = pd.to_datetime(df["t"]).dt.tz_convert("America/New_York").dt.date.astype(str)
        df = df.rename(columns={"o": "open", "h": "high", "l": "low", "c": "close", "v": "volume"})
        return df[["date", "symbol", "open", "high", "low", "close", "volume"]].sort_values(["symbol", "date"])
