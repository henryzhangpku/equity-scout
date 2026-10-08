"""Point-in-time visibility, restatements, YTD-derived quarters and TTM."""

import math

import pandas as pd
import pytest

from scout import fundamentals as F
from scout.data.sec import FACT_COLUMNS

REV = "RevenueFromContractWithCustomerExcludingAssessedTax"


def fact(item, concept, start, end, val, filed, accn="a"):
    return dict(zip(FACT_COLUMNS, [item, concept, start, end, float(val), None, None, "10-Q", filed, accn]))


def quarters(item="revenue", concept=REV, base=100.0, step=10.0, filed_lag_days=30):
    """Eight calendar quarters 2024Q1..2025Q4 of 3-month facts, values 100..170."""
    ends = ["2024-03-31", "2024-06-30", "2024-09-30", "2024-12-31",
            "2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31"]
    starts = ["2024-01-01", "2024-04-01", "2024-07-01", "2024-10-01",
              "2025-01-01", "2025-04-01", "2025-07-01", "2025-10-01"]
    rows = []
    for i, (s, e) in enumerate(zip(starts, ends)):
        filed = (pd.Timestamp(e) + pd.Timedelta(days=filed_lag_days)).date().isoformat()
        rows.append(fact(item, concept, s, e, base + step * i, filed, accn=f"q{i}"))
    return rows


def test_fact_invisible_before_filed_date():
    df = pd.DataFrame(quarters())
    # 2025Q4 (val 170) is filed 2026-01-30
    assert "2025-12-31" not in set(F.visible(df, "2026-01-29")["end"])
    assert "2025-12-31" in set(F.visible(df, "2026-01-30")["end"])


def test_compute_ignores_facts_filed_after_as_of():
    df = pd.DataFrame(quarters())
    fu = F.compute(df, "2026-01-29", price=10.0)
    # 2025Q4 not yet filed: TTM ends 2025Q3 = 130+140+150+160
    assert fu.provenance["revenue_period_end"] == "2025-09-30"
    assert fu.values["revenue_ttm"] == 580


def test_restatement_not_visible_until_filed():
    rows = quarters()
    # 2025Q3 originally 160 filed 2025-10-30; restated to 999 in a filing on 2026-02-15
    rows.append(fact("revenue", REV, "2025-07-01", "2025-09-30", 999, "2026-02-15", accn="restated"))
    df = pd.DataFrame(rows)
    q_before = F.quarterly(F.item_facts(F.visible(df, "2026-02-01"), "revenue"))
    q_after = F.quarterly(F.item_facts(F.visible(df, "2026-02-15"), "revenue"))
    assert q_before.set_index("end").loc["2025-09-30", "val"] == 160
    assert q_after.set_index("end").loc["2025-09-30", "val"] == 999


def test_ttm_and_growth():
    df = pd.DataFrame(quarters())
    fu = F.compute(df, "2026-03-01", price=10.0)
    # TTM 2025 = 140+150+160+170 = 620; TTM 2024 = 100+110+120+130 = 460
    assert fu.values["revenue_ttm"] == 620
    assert fu.values["revenue_growth_yoy"] == pytest.approx(620 / 460 - 1)
    # latest quarter YoY 170/130 - 1; prior quarter 160/120 - 1
    assert fu.values["revenue_growth_q_yoy"] == pytest.approx(170 / 130 - 1)
    assert fu.values["revenue_growth_accel"] == pytest.approx((170 / 130 - 1) - (160 / 120 - 1))


def test_quarters_derived_from_year_to_date():
    # fiscal year = calendar 2025: 3M=100, 6M=230, 9M=360, FY=500 -> quarters 100,130,130,140
    c = "NetCashProvidedByUsedInOperatingActivities"
    rows = [
        fact("cfo", c, "2025-01-01", "2025-03-31", 100, "2025-05-01"),
        fact("cfo", c, "2025-01-01", "2025-06-30", 230, "2025-08-01"),
        fact("cfo", c, "2025-01-01", "2025-09-30", 360, "2025-11-01"),
        fact("cfo", c, "2025-01-01", "2025-12-31", 500, "2026-02-20"),
    ]
    q = F.quarterly(F.item_facts(pd.DataFrame(rows), "cfo"))
    assert list(q["val"]) == [100, 130, 130, 140]
    assert list(q["derived"]) == [False, True, True, True]
    assert F.ttm_at(q, 3) == 500
    # Q4 is derived from the 10-K, so it is visible only from the 10-K filed date
    assert q["filed"].iloc[-1] == "2026-02-20"


def test_ttm_requires_consecutive_quarters():
    rows = [r for r in quarters() if r["end"] != "2025-06-30"]  # a missing quarter
    q = F.quarterly(F.item_facts(pd.DataFrame(rows), "revenue"))
    assert math.isnan(F.ttm_at(q, len(q) - 1))


def test_fcf_ttm_from_ytd_cash_flows():
    rows = quarters()
    ends = ["2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31"]
    for item, concept, vals in [("cfo", "NetCashProvidedByUsedInOperatingActivities", [30, 70, 100, 150]),
                                ("capex", "PaymentsToAcquirePropertyPlantAndEquipment", [5, 10, 15, 20])]:
        for e, v in zip(ends, vals):
            rows.append(fact(item, concept, "2025-01-01", e, v, "2026-01-30"))
    fu = F.compute(pd.DataFrame(rows), "2026-03-01", price=10.0)
    assert fu.values["fcf_ttm"] == 150 - 20
    assert fu.values["fcf_margin"] == pytest.approx(130 / 620)


def test_stale_fundamentals_are_missing_not_reused():
    fu = F.compute(pd.DataFrame(quarters()), "2026-12-31", price=10.0)  # latest quarter a year old
    assert fu.provenance["stale"] is True
    assert math.isnan(fu.values["revenue_ttm"])
    assert math.isnan(fu.values["revenue_growth_yoy"])


def test_market_cap_uses_latest_visible_shares():
    rows = quarters()
    rows.append(fact("shares", "EntityCommonStockSharesOutstanding", None, "2025-10-20", 1e6, "2025-10-30"))
    rows.append(fact("shares", "EntityCommonStockSharesOutstanding", None, "2026-01-20", 2e6, "2026-01-30"))
    df = pd.DataFrame(rows)
    # revenue is tiny in this fixture, so scale it up to keep price/sales plausible
    df.loc[df["item"] == "revenue", "val"] *= 1e4
    assert F.compute(df, "2026-01-29", price=5.0).values["market_cap"] == 5e6
    assert F.compute(df, "2026-02-01", price=5.0).values["market_cap"] == 1e7


def _rev_scaled(mult=1e6):
    rows = quarters()
    for r in rows:
        r["val"] *= mult
    return rows


def test_tiny_share_count_is_rejected():
    rows = _rev_scaled()
    rows.append(fact("shares", "CommonStockSharesOutstanding", None, "2026-01-20", 1_891, "2026-01-30"))
    fu = F.compute(pd.DataFrame(rows), "2026-03-01", price=50.0)
    assert math.isnan(fu.values["market_cap"])


def test_multi_class_falls_back_to_weighted_average():
    rows = _rev_scaled()
    # cover page tags only Class A (1M) while EPS uses 30M basic shares across classes
    rows.append(fact("shares", "EntityCommonStockSharesOutstanding", None, "2026-01-20", 1e6, "2026-01-30"))
    rows.append(fact("shares", "WeightedAverageNumberOfSharesOutstandingBasic", "2025-10-01", "2025-12-31", 3e7,
                     "2026-01-30"))
    fu = F.compute(pd.DataFrame(rows), "2026-03-01", price=50.0)
    assert fu.values["market_cap"] == 1.5e9
    assert fu.provenance["shares_concept"] == "WeightedAverageNumberOfSharesOutstandingBasic"


def test_impossible_price_to_sales_rejects_market_cap():
    rows = _rev_scaled(1e9)                    # TTM revenue 620e9
    rows.append(fact("shares", "EntityCommonStockSharesOutstanding", None, "2026-01-20", 1e6, "2026-01-30"))
    fu = F.compute(pd.DataFrame(rows), "2026-03-01", price=500.0)   # 0.5e9 market cap, P/S 0.0008
    assert math.isnan(fu.values["market_cap"])
    assert "price/sales" in fu.provenance["market_cap_rejected"]


def test_quarters_never_derived_across_concepts():
    # 6M under one tag and 3M under another must not be subtracted from each other
    rows = [
        fact("revenue", "Revenues", "2025-01-01", "2025-03-31", 100, "2025-05-01"),
        fact("revenue", REV, "2025-01-01", "2025-06-30", 50, "2025-08-01"),
    ]
    q = F.item_quarterly(pd.DataFrame(rows), "revenue")
    assert list(q["end"]) == ["2025-03-31"]
