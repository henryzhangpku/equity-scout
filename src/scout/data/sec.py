"""SEC EDGAR: ticker map, company profiles and XBRL facts (free, public).

Fair-access rules are respected: a descriptive User-Agent with a contact
address, fewer than 10 requests per second, and every raw response cached.

Why companyfacts and not frames for the numbers
-----------------------------------------------
The frames API (one call returns every company for one concept and period) is
the fastest cross-section, but each frame value is the *latest-filed* number for
that period and carries no `filed` date: a prior-year quarter restated in this
year's 10-Q replaces the number investors actually saw. That is look-ahead.
companyfacts keeps every filing's value with its `filed` date, so a fact can be
made visible only after it was filed. Frames are used only for a coverage
cross-check (`frames_snapshot`).
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from ..http import fetch_json

TICKERS_URL = "https://www.sec.gov/files/company_tickers_exchange.json"
FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik:010d}.json"
FRAMES_URL = "https://data.sec.gov/api/xbrl/frames/{tax}/{concept}/{unit}/{period}.json"

# Concepts we extract. Order inside a list = preference when several exist.
CONCEPTS: dict[str, list[tuple[str, str, str]]] = {
    "revenue": [
        ("us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax", "USD"),
        ("us-gaap", "Revenues", "USD"),
        ("us-gaap", "SalesRevenueNet", "USD"),
        ("us-gaap", "RevenueFromContractWithCustomerIncludingAssessedTax", "USD"),
        ("us-gaap", "RevenuesNetOfInterestExpense", "USD"),
    ],
    "cost_of_revenue": [
        ("us-gaap", "CostOfRevenue", "USD"),
        ("us-gaap", "CostOfGoodsAndServicesSold", "USD"),
        ("us-gaap", "CostOfGoodsSold", "USD"),
    ],
    "gross_profit": [("us-gaap", "GrossProfit", "USD")],
    "operating_income": [("us-gaap", "OperatingIncomeLoss", "USD")],
    "net_income": [("us-gaap", "NetIncomeLoss", "USD")],
    "cfo": [
        ("us-gaap", "NetCashProvidedByUsedInOperatingActivities", "USD"),
        ("us-gaap", "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations", "USD"),
    ],
    "capex": [
        ("us-gaap", "PaymentsToAcquirePropertyPlantAndEquipment", "USD"),
        ("us-gaap", "PaymentsToAcquireProductiveAssets", "USD"),
        ("us-gaap", "PaymentsForCapitalImprovements", "USD"),
    ],
    "cash": [
        ("us-gaap", "CashAndCashEquivalentsAtCarryingValue", "USD"),
        ("us-gaap", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", "USD"),
        ("us-gaap", "Cash", "USD"),
    ],
    "st_investments": [
        ("us-gaap", "ShortTermInvestments", "USD"),
        ("us-gaap", "MarketableSecuritiesCurrent", "USD"),
        ("us-gaap", "AvailableForSaleSecuritiesDebtSecuritiesCurrent", "USD"),
    ],
    "lt_debt": [
        ("us-gaap", "LongTermDebt", "USD"),
        ("us-gaap", "LongTermDebtNoncurrent", "USD"),
        ("us-gaap", "LongTermDebtAndCapitalLeaseObligations", "USD"),
    ],
    "lt_debt_current": [
        ("us-gaap", "LongTermDebtCurrent", "USD"),
        ("us-gaap", "LongTermDebtAndCapitalLeaseObligationsCurrent", "USD"),
    ],
    "st_debt": [
        ("us-gaap", "ShortTermBorrowings", "USD"),
        ("us-gaap", "CommercialPaper", "USD"),
    ],
    "shares": [
        ("dei", "EntityCommonStockSharesOutstanding", "shares"),
        ("us-gaap", "CommonStockSharesOutstanding", "shares"),
        # last resort for multi-class issuers whose cover-page count is only tagged per class
        ("us-gaap", "WeightedAverageNumberOfSharesOutstandingBasic", "shares"),
    ],
}

FACT_COLUMNS = ["item", "concept", "start", "end", "val", "fy", "fp", "form", "filed", "accn"]


class SecData:
    """FundamentalSource + ticker map, backed by data.sec.gov."""

    def ticker_map(self, snapshot: str) -> pd.DataFrame:
        j = fetch_json(TICKERS_URL, source="sec", cache_key=f"tickers {snapshot}")
        df = pd.DataFrame(j["data"], columns=j["fields"])
        df["ticker"] = df["ticker"].str.upper()
        return df

    def raw_facts(self, cik: int) -> dict | None:
        return fetch_json(FACTS_URL.format(cik=cik), source="sec_facts", allow_404=True)

    def profile(self, cik: int) -> dict | None:
        return fetch_json(SUBMISSIONS_URL.format(cik=cik), source="sec_subs", allow_404=True)

    def facts(self, cik: int) -> pd.DataFrame:
        return extract_facts(self.raw_facts(cik))

    def frames_snapshot(self, tax: str, concept: str, unit: str, period: str) -> pd.DataFrame:
        j = fetch_json(FRAMES_URL.format(tax=tax, concept=concept, unit=unit, period=period),
                       source="sec_frames", allow_404=True)
        return pd.DataFrame((j or {}).get("data", []))


def extract_facts(raw: dict | None) -> pd.DataFrame:
    """Flatten companyfacts JSON into one row per (item, concept, period, filing)."""
    rows = []
    if raw:
        f = raw.get("facts", {})
        for item, cands in CONCEPTS.items():
            for tax, concept, unit in cands:
                for x in f.get(tax, {}).get(concept, {}).get("units", {}).get(unit, []):
                    rows.append((item, concept, x.get("start"), x["end"], float(x["val"]), x.get("fy"),
                                 x.get("fp"), x.get("form"), x["filed"], x.get("accn")))
    return pd.DataFrame(rows, columns=FACT_COLUMNS)


def sic_of(profile: dict | None) -> tuple[int | None, str]:
    if not profile:
        return None, ""
    try:
        return int(profile.get("sic") or 0) or None, profile.get("sicDescription") or ""
    except ValueError:
        return None, ""


PERIODIC_FORMS = {"10-K", "10-Q", "10-KT", "20-F", "40-F"}


def periodic_filer(profile: dict | None, as_of: date, within_days: int = 550) -> tuple[bool, str]:
    """(files periodic reports, latest periodic form). Excludes funds that file N-CSR etc."""
    f = recent_filings(profile, as_of)
    if f.empty:
        return False, ""
    cutoff = (pd.Timestamp(as_of) - pd.Timedelta(days=within_days)).date().isoformat()
    p = f[f["form"].isin(PERIODIC_FORMS) & (f["filingDate"] >= cutoff)]
    return (not p.empty), ("" if p.empty else str(p["form"].iloc[0]))


def recent_filings(profile: dict | None, as_of: date) -> pd.DataFrame:
    """Filings visible on `as_of` (filingDate <= as_of), newest first."""
    if not profile:
        return pd.DataFrame()
    r = profile.get("filings", {}).get("recent", {})
    df = pd.DataFrame({k: r.get(k, []) for k in
                       ["accessionNumber", "filingDate", "reportDate", "form", "items", "primaryDocument"]})
    if df.empty:
        return df
    df = df[df["filingDate"] <= as_of.isoformat()]
    return df.sort_values("filingDate", ascending=False).reset_index(drop=True)
