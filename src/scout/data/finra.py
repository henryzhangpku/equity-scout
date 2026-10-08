"""FINRA consolidated equity short interest (exchange-listed and OTC).

Source: FINRA Query API dataset otcMarket/consolidatedShortInterest. FINRA
states its data is provided for non-commercial use; this demo is research only.
A licensed deployment would swap in a commercial short-interest or
securities-lending feed through the same ShortInterestSource interface.

Point-in-time: short positions are as of a settlement date (twice monthly) and
FINRA disseminates them several business days later. We treat a settlement
date as visible only from settlement + DISSEMINATION_LAG_BDAYS business days,
a conservative approximation of FINRA's published schedule.
"""

from __future__ import annotations

import json
from datetime import date, timedelta

import numpy as np
import pandas as pd

from ..http import fetch

URL = "https://api.finra.org/data/group/otcMarket/name/consolidatedShortInterest"
DISSEMINATION_LAG_BDAYS = 8
FIELDS = ["symbolCode", "settlementDate", "currentShortPositionQuantity",
          "averageDailyVolumeQuantity", "daysToCoverQuantity", "marketClassCode"]


def visible_from(settlement: str) -> str:
    return str(np.busday_offset(np.datetime64(settlement), DISSEMINATION_LAG_BDAYS, roll="forward"))


class FinraShortInterest:
    available = True

    def __init__(self, snapshot: str):
        self.snapshot = snapshot  # pins cached responses so reruns are identical

    def _post(self, body: dict) -> list[dict]:
        raw = fetch(URL, source="finra", method="POST", json_body=body, headers={"Accept": "application/json"},
                    cache_key=f"finra {self.snapshot} {json.dumps(body, sort_keys=True)}")
        return json.loads(raw) if raw else []

    def settlement_dates(self, as_of: date, lookback_days: int = 45) -> list[str]:
        """Settlement dates with data in the lookback window. Settlement is the
        mid-month (13th-15th) or month-end (26th-31st) business day; the dataset is
        partitioned by date, so each candidate is probed with a 1-row request."""
        found = []
        for d in pd.bdate_range(as_of - timedelta(days=lookback_days), as_of):
            if 12 <= d.day <= 15 or d.day >= 26:
                ds = d.date().isoformat()
                body = {"limit": 1, "fields": ["settlementDate"],
                        "compareFilters": [{"compareType": "EQUAL", "fieldName": "settlementDate", "fieldValue": ds}]}
                if self._post(body):
                    found.append(ds)
        return found

    def settlement_rows(self, settlement: str) -> pd.DataFrame:
        rows, off = [], 0
        while True:
            body = {"limit": 5000, "offset": off, "fields": FIELDS,
                    "compareFilters": [{"compareType": "EQUAL", "fieldName": "settlementDate",
                                        "fieldValue": settlement}]}
            page = self._post(body)
            rows += page
            if len(page) < 5000:
                break
            off += 5000
        return pd.DataFrame(rows, columns=FIELDS)

    def latest(self, as_of: date) -> pd.DataFrame:
        """Short interest for the most recent settlement date visible on `as_of`."""
        ok = [d for d in self.settlement_dates(as_of) if visible_from(d) <= as_of.isoformat()]
        if not ok:
            return NoShortInterest().latest(as_of)
        s = ok[-1]
        df = self.settlement_rows(s)
        out = pd.DataFrame({
            "symbol": df["symbolCode"].str.upper(),
            "settlement_date": s,
            "visible_from": visible_from(s),
            "short_shares": pd.to_numeric(df["currentShortPositionQuantity"], errors="coerce"),
            "days_to_cover": pd.to_numeric(df["daysToCoverQuantity"], errors="coerce"),
            "avg_daily_volume": pd.to_numeric(df["averageDailyVolumeQuantity"], errors="coerce"),
        })
        return out.drop_duplicates("symbol")


class NoShortInterest:
    available = False
    reason = "short interest unavailable in free data"

    def latest(self, as_of: date) -> pd.DataFrame:
        return pd.DataFrame(columns=["symbol", "settlement_date", "visible_from", "short_shares",
                                     "days_to_cover", "avg_daily_volume"])
