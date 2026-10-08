"""Point-in-time fundamentals from XBRL facts.

Rules (all deterministic, all unit-tested):

* Visibility: a fact is usable on `as_of` only if `filed <= as_of`.
* Restatements: when several filings report the same (concept, start, end), the
  latest one filed on or before `as_of` wins; later restatements are invisible.
* Quarterly values: a 3-month fact if reported; otherwise derived from
  year-to-date facts sharing a fiscal-year start (Q2 = 6M - 3M, Q3 = 9M - 6M,
  Q4 = FY - 9M). Cash-flow items are mostly reported year-to-date, so this is
  what makes TTM free cash flow computable.
* TTM: the sum of four consecutive quarters (gaps of 75-105 days).
* Staleness: if the latest visible quarter ended more than STALE_DAYS before
  `as_of`, every fundamental is left missing rather than reused.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

from .data.sec import CONCEPTS

STALE_DAYS = 220
MIN_SHARES = 100_000          # fewer reported shares is a scaling or share-class tagging error
MIN_PRICE_TO_SALES = 0.01     # below this the share count, not the market, is wrong
NAN = float("nan")


def visible(facts: pd.DataFrame, as_of: date | str) -> pd.DataFrame:
    """Facts public on `as_of`: filed on or before that date."""
    a = as_of if isinstance(as_of, str) else as_of.isoformat()
    return facts[facts["filed"] <= a]


def _dedupe_latest_filed(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    return (df.sort_values(["filed", "accn"]).drop_duplicates(keys, keep="last"))


def item_facts(facts: pd.DataFrame, item: str) -> pd.DataFrame:
    """Facts for one item: primary concept (most recent period end; ties by
    preference order), gaps filled from the other concepts in preference order."""
    df = facts[facts["item"] == item]
    if df.empty:
        return df
    order = [c for _, c, _ in CONCEPTS[item]]
    latest = df.groupby("concept")["end"].max()
    primary = sorted(latest.index, key=lambda c: (-pd.Timestamp(latest[c]).value, order.index(c)))[0]
    ranked = [primary] + [c for c in order if c != primary]
    rank = {c: i for i, c in enumerate(ranked)}
    df = df.assign(_r=df["concept"].map(rank))
    keys = ["start", "end"] if df["start"].notna().any() else ["end"]
    df = _dedupe_latest_filed(df, ["concept"] + keys)
    df = df.sort_values("_r").drop_duplicates(keys, keep="first")
    return df.drop(columns="_r").sort_values("end").reset_index(drop=True)


def _ranked_concepts(df: pd.DataFrame, item: str) -> list[str]:
    order = [c for _, c, _ in CONCEPTS[item]]
    latest = df.groupby("concept")["end"].max()
    primary = sorted(latest.index, key=lambda c: (-pd.Timestamp(latest[c]).value, order.index(c)))[0]
    return [primary] + [c for c in order if c != primary and c in latest.index]


def item_quarterly(facts: pd.DataFrame, item: str) -> pd.DataFrame:
    """Quarterly series for one item. Quarters are derived within a single concept
    (never 9M of one tag minus 6M of another); the primary concept's quarters win
    and other concepts only fill quarters it does not have."""
    df = facts[facts["item"] == item]
    if df.empty:
        return quarterly(df)
    merged = None
    for c in _ranked_concepts(df, item):
        q = quarterly(_dedupe_latest_filed(df[df["concept"] == c], ["start", "end"]))
        if merged is None:
            merged = q
        elif not q.empty:
            merged = pd.concat([merged, q[~q["end"].isin(merged["end"])]], ignore_index=True)
    return merged.sort_values("end").reset_index(drop=True)


def _days(a: str, b: str) -> int:
    return (pd.Timestamp(b) - pd.Timestamp(a)).days


def _nq(days: int) -> int | None:
    for n, (lo, hi) in {1: (80, 100), 2: (170, 195), 3: (260, 290), 4: (350, 380)}.items():
        if lo <= days <= hi:
            return n
    return None


def quarterly(df: pd.DataFrame) -> pd.DataFrame:
    """Quarterly (3-month) values from duration facts of one item.

    Returns columns end, val, filed, derived (bool), sorted by end.
    """
    if df.empty or df["start"].isna().all():
        return pd.DataFrame(columns=["end", "val", "filed", "derived"])
    d = df.dropna(subset=["start"]).copy()
    d["nq"] = [_nq(_days(s, e)) for s, e in zip(d["start"], d["end"])]
    d = d.dropna(subset=["nq"])
    by_se = {(s, e): (v, f) for s, e, v, f in zip(d["start"], d["end"], d["val"], d["filed"])}
    out = {}
    for _, r in d.sort_values("end").iterrows():
        e, s, n = r["end"], r["start"], int(r["nq"])
        if n == 1:
            out[e] = (r["val"], r["filed"], False)
            continue
        if e in out and not out[e][2]:
            continue  # a directly reported quarter beats a derived one
        # find the year-to-date fact one quarter shorter with the same fiscal start
        for (s2, e2), (v2, f2) in by_se.items():
            if s2 == s and _nq(_days(s2, e2)) == n - 1 and 75 <= _days(e2, e) <= 105:
                out.setdefault(e, (r["val"] - v2, max(r["filed"], f2), True))
                break
    q = pd.DataFrame([(e, v, f, dv) for e, (v, f, dv) in out.items()],
                     columns=["end", "val", "filed", "derived"])
    return q.sort_values("end").reset_index(drop=True)


def ttm_at(q: pd.DataFrame, i: int) -> float:
    """Sum of quarters i-3..i if they are consecutive, else NaN."""
    if i < 3:
        return NAN
    w = q.iloc[i - 3:i + 1]
    ends = list(w["end"])
    if all(75 <= _days(a, b) <= 105 for a, b in zip(ends, ends[1:])):
        return float(w["val"].sum())
    return NAN


def year_ago_index(q: pd.DataFrame, i: int) -> int | None:
    e = q["end"].iloc[i]
    for j in range(i - 1, -1, -1):
        if 350 <= _days(q["end"].iloc[j], e) <= 380:
            return j
    return None


def latest_instant(df: pd.DataFrame) -> tuple[float, str | None, str | None, str | None]:
    """Most recent point-in-time balance: (val, period end, filed, concept)."""
    if df.empty:
        return NAN, None, None, None
    d = df.sort_values(["end", "filed"])
    r = d.iloc[-1]
    return float(r["val"]), r["end"], r["filed"], r["concept"]


def _growth(a: float, b: float) -> float:
    return a / b - 1.0 if (b and b > 0 and np.isfinite(a) and np.isfinite(b)) else NAN


def pick_shares(f: pd.DataFrame, as_of: str) -> tuple[float, str | None, str | None, str | None]:
    """Shares outstanding as of `as_of`.

    Prefer a point-in-time count (cover page, then balance sheet). Multi-class
    issuers often tag only one class without a dimension, which shows up as a
    point count far below the weighted-average basic count (which covers all
    classes); then the weighted average is used. Counts under MIN_SHARES or
    older than 400 days are rejected as tagging errors.
    """
    sh = item_facts(f, "shares")
    sh = sh[(sh["val"] >= MIN_SHARES) & (sh["end"] >= (pd.Timestamp(as_of) - pd.Timedelta(days=400)).date().isoformat())]
    wavg = sh[sh["concept"] == "WeightedAverageNumberOfSharesOutstandingBasic"]
    point = sh[sh["concept"] != "WeightedAverageNumberOfSharesOutstandingBasic"]
    p = latest_instant(point)
    w = latest_instant(wavg)
    if np.isfinite(p[0]) and not (np.isfinite(w[0]) and p[0] < 0.5 * w[0]):
        return p
    if np.isfinite(w[0]):
        return w
    return NAN, None, None, None


@dataclass
class Fundamentals:
    values: dict
    provenance: dict


def compute(facts: pd.DataFrame, as_of: date | str, price: float) -> Fundamentals:
    """All fundamental fields for one company as of `as_of` at `price`."""
    a = as_of if isinstance(as_of, str) else as_of.isoformat()
    f = visible(facts, a)
    v: dict = {}
    prov: dict = {}

    rev_q = item_quarterly(f, "revenue")
    stale = rev_q.empty or _days(rev_q["end"].iloc[-1], a) > STALE_DAYS
    if not rev_q.empty:
        prov["revenue_period_end"] = rev_q["end"].iloc[-1]
        prov["revenue_filed"] = rev_q["filed"].iloc[-1]
    prov["stale"] = bool(stale)

    def ttm_item(item: str) -> float:
        q = item_quarterly(f, item)
        if q.empty or rev_q.empty:
            return NAN
        # align on the revenue quarter so margins compare like with like
        hit = q.index[q["end"] == rev_q["end"].iloc[-1]]
        return ttm_at(q, int(hit[0])) if len(hit) else NAN

    if stale:
        for k in ["revenue_ttm", "revenue_growth_yoy", "revenue_growth_q_yoy", "revenue_growth_accel",
                  "gross_margin", "operating_margin", "net_margin", "fcf_ttm", "fcf_margin", "fcf_yield",
                  "net_debt", "ev", "ev_to_sales"]:
            v[k] = NAN
    else:
        i = len(rev_q) - 1
        rev_ttm = ttm_at(rev_q, i)
        v["revenue_ttm"] = rev_ttm
        j = year_ago_index(rev_q, i)
        v["revenue_growth_yoy"] = _growth(rev_ttm, ttm_at(rev_q, j)) if j is not None else NAN
        g_now = _growth(rev_q["val"].iloc[i], rev_q["val"].iloc[j]) if j is not None else NAN
        v["revenue_growth_q_yoy"] = g_now
        g_prev = NAN
        if i >= 1:
            j2 = year_ago_index(rev_q, i - 1)
            if j2 is not None and 75 <= _days(rev_q["end"].iloc[i - 1], rev_q["end"].iloc[i]) <= 105:
                g_prev = _growth(rev_q["val"].iloc[i - 1], rev_q["val"].iloc[j2])
        v["revenue_growth_q_yoy_prev"] = g_prev
        v["revenue_growth_accel"] = g_now - g_prev if np.isfinite(g_now) and np.isfinite(g_prev) else NAN

        gp = ttm_item("gross_profit")
        if not np.isfinite(gp):
            cor = ttm_item("cost_of_revenue")
            gp = rev_ttm - cor if np.isfinite(cor) else NAN
        ok = np.isfinite(rev_ttm) and rev_ttm > 0
        v["gross_margin"] = gp / rev_ttm if ok and np.isfinite(gp) else NAN
        oi = ttm_item("operating_income")
        v["operating_margin"] = oi / rev_ttm if ok and np.isfinite(oi) else NAN
        ni = ttm_item("net_income")
        v["net_income_ttm"] = ni
        v["net_margin"] = ni / rev_ttm if ok and np.isfinite(ni) else NAN
        cfo, capex = ttm_item("cfo"), ttm_item("capex")
        v["cfo_ttm"] = cfo
        v["capex_ttm"] = capex
        fcf = cfo - capex if np.isfinite(cfo) and np.isfinite(capex) else NAN
        v["fcf_ttm"] = fcf
        v["fcf_margin"] = fcf / rev_ttm if ok and np.isfinite(fcf) else NAN

    shares, s_end, s_filed, s_concept = pick_shares(f, a)
    prov["shares_as_of"], prov["shares_filed"], prov["shares_concept"] = s_end, s_filed, s_concept
    v["shares_out"] = shares
    mcap = shares * price if np.isfinite(shares) and shares > 0 and np.isfinite(price) else NAN
    rev_ok = np.isfinite(v.get("revenue_ttm", NAN)) and v.get("revenue_ttm", 0) > 0
    if np.isfinite(mcap) and rev_ok and mcap / v["revenue_ttm"] < MIN_PRICE_TO_SALES:
        # e.g. a Class A share count times a Class B price: an impossible valuation is a data error
        prov["market_cap_rejected"] = f"price/sales {mcap / v['revenue_ttm']:.2g} < {MIN_PRICE_TO_SALES}"
        mcap = NAN
    v["market_cap"] = mcap
    if not stale:
        cash = np.nansum([latest_instant(item_facts(f, "cash"))[0],
                          latest_instant(item_facts(f, "st_investments"))[0]])
        lt, _, _, lt_concept = latest_instant(item_facts(f, "lt_debt"))
        debt_parts = [lt]
        if lt_concept != "LongTermDebt":  # the other tags exclude the current portion
            debt_parts.append(latest_instant(item_facts(f, "lt_debt_current"))[0])
        debt_parts.append(latest_instant(item_facts(f, "st_debt"))[0])
        debt = float(np.nansum(debt_parts))
        v["total_debt"] = debt
        v["cash_and_st_investments"] = float(cash)
        v["net_debt"] = debt - float(cash)
        v["ev"] = mcap + v["net_debt"] if np.isfinite(mcap) else NAN
        v["ev_to_sales"] = v["ev"] / rev_ttm if np.isfinite(v["ev"]) and ok else NAN
        v["fcf_yield"] = v["fcf_ttm"] / mcap if np.isfinite(mcap) and mcap > 0 else NAN
    return Fundamentals(values=v, provenance=prov)
