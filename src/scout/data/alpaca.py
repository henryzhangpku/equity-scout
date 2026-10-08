"""Alpaca market data: US equity universe and daily adjusted bars.

Read-only use of the assets and market-data endpoints. No orders, no account
endpoints. Keys come from ALPACA_API_KEY / ALPACA_API_SECRET.
"""

from __future__ import annotations

import json
from datetime import date

import pandas as pd

from ..config import secret
from ..http import fetch_json
from .base import Security

MAJOR_EXCHANGES = {"NYSE", "NASDAQ", "AMEX", "ARCA", "BATS"}
ASSETS_URL = "https://api.alpaca.markets/v2/assets"
BARS_URL = "https://data.alpaca.markets/v2/stocks/bars"


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
        for i in range(0, len(symbols), chunk):
            batch = symbols[i:i + chunk]
            token = None
            page = 0
            while True:
                params = {
                    "symbols": ",".join(batch), "timeframe": "1Day",
                    "start": start.isoformat(), "end": end.isoformat(),
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
