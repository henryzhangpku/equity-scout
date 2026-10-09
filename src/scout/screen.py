"""Deterministic screen and rank. No model is involved past this point.

The funnel applies universe filters, then conditions, in the order written in
the spec. Each step records how many names entered, passed, failed the
threshold, and were dropped because the value was missing (a gap in free data
is reported as a gap, never imputed).
"""

from __future__ import annotations

import operator

import numpy as np
import pandas as pd

from .sectors import classify
from .spec import FIELDS, INDUSTRIES, THEMES, Spec

_CMP = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge}


def _fmt_value(field: str, v) -> str:
    kind = FIELDS[field].kind if field in FIELDS else "number"
    if isinstance(v, bool):
        return str(v).lower()
    if kind == "ratio":
        return f"{v * 100:+.1f}%" if abs(v) < 20 else f"{v}"
    if kind == "usd" and abs(v) >= 1e6:
        return f"${v / 1e9:,.2f}B" if abs(v) >= 1e9 else f"${v / 1e6:,.0f}M"
    return f"{v:g}"


def describe(c: dict) -> str:
    f, op = c["field"], c["op"]
    if "ref" in c:
        return f"{f} {op} {c['ref']}"
    if op == "between":
        lo, hi = c["value"]
        return f"{_fmt_value(f, lo)} <= {f} <= {_fmt_value(f, hi)}"
    return f"{f} {op} {_fmt_value(f, c['value'])}"


def _mask(df: pd.DataFrame, c: dict) -> tuple[pd.Series, pd.Series]:
    """(passed, missing) boolean masks for one condition."""
    f, op = c["field"], c["op"]
    x = df[f]
    if FIELDS[f].kind == "bool":
        x = x.map(lambda v: None if pd.isna(v) else str(v).lower() == "true")
        missing = x.isna()
        return (~missing) & (x == c["value"]), missing
    x = pd.to_numeric(x, errors="coerce")
    if "ref" in c:
        y = pd.to_numeric(df[c["ref"]], errors="coerce")
        missing = x.isna() | y.isna()
        return (~missing) & _CMP[op](x, y), missing
    missing = x.isna()
    if op == "between":
        lo, hi = c["value"]
        return (~missing) & (x >= lo) & (x <= hi), missing
    return (~missing) & _CMP[op](x, c["value"]), missing


def with_sectors(features: pd.DataFrame) -> pd.DataFrame:
    """Copy of the features with `sector` and `industry_group` from the published SIC mapping."""
    df = features.copy()
    sic = df["sic"] if "sic" in df else [None] * len(df)
    sym = df["symbol"] if "symbol" in df else [None] * len(df)
    pairs = [classify(s, y) for s, y in zip(sic, sym)]
    df["sector"] = [p[0] for p in pairs]
    df["industry_group"] = [p[1] for p in pairs]
    return df


def sector_breakdown(survivors: pd.DataFrame) -> list[dict]:
    """Survivors per sector, largest first (ties by name); names without a sector are 'No sector'."""
    s = survivors["sector"].fillna("No sector") if "sector" in survivors else pd.Series(dtype=object)
    counts = s.value_counts()
    return [{"sector": k, "n": int(v)} for k, v in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]


def universe_steps(spec: Spec) -> list[tuple[str, callable]]:
    u = spec.universe
    steps = []
    if "industries" in u or "themes" in u:
        codes = set().union(set(), *(INDUSTRIES[g][1] for g in u.get("industries", [])))
        syms = set().union(set(), *(THEMES[t][1] for t in u.get("themes", [])))
        label = " or ".join(x for x in [f"industry in {u['industries']}" if u.get("industries") else "",
                                         f"theme in {u['themes']}" if u.get("themes") else ""] if x)
        # a missing SIC only matters when SIC groups are part of the test
        steps.append((label, lambda d: (d["sic"].isin(codes) | d["symbol"].isin(syms),
                                        d["sic"].isna() & ~d["symbol"].isin(syms) & bool(codes))))
    if u.get("sectors") or u.get("industry_groups"):
        secs, grps = set(u.get("sectors", [])), set(u.get("industry_groups", []))
        label = " or ".join(x for x in [f"sector in {u['sectors']}" if u.get("sectors") else "",
                                         f"industry group in {u['industry_groups']}" if u.get("industry_groups") else ""] if x)
        steps.append((label, lambda d: (d["sector"].isin(secs) | d["industry_group"].isin(grps), d["sector"].isna())))
    if "exclude_industries" in u:
        codes_x = set().union(*(INDUSTRIES[g][1] for g in u["exclude_industries"]))
        steps.append((f"industry not in {u['exclude_industries']}",
                      lambda d: (~d["sic"].isin(codes_x) & d["sic"].notna(), d["sic"].isna())))
    for key, field, op in [("market_cap_min", "market_cap", ">="), ("market_cap_max", "market_cap", "<="),
                           ("min_price", "close", ">="), ("min_avg_dollar_volume", "avg_dollar_volume_50d", ">=")]:
        if key in u:
            c = {"field": field, "op": op, "value": u[key]}
            steps.append((describe(c), lambda d, c=c: _mask(d, c)))
    return steps


def run_screen(features: pd.DataFrame, spec: Spec) -> tuple[list[dict], pd.DataFrame]:
    """Return (funnel, survivors)."""
    df = with_sectors(features)
    funnel = [{"step": "universe (liquid US common stocks with SEC filings)", "kind": "start",
               "n_in": len(df), "n_pass": len(df), "n_fail": 0, "n_missing": 0}]
    steps = [(name, fn, "universe") for name, fn in universe_steps(spec)]
    steps += [(describe(c), (lambda d, c=c: _mask(d, c)), "condition") for c in spec.conditions]
    for name, fn, kind in steps:
        passed, missing = fn(df)
        n_in = len(df)
        n_pass, n_miss = int(passed.sum()), int((missing & ~passed).sum())
        funnel.append({"step": name, "kind": kind, "n_in": n_in, "n_pass": n_pass,
                       "n_fail": n_in - n_pass - n_miss, "n_missing": n_miss})
        df = df[passed.to_numpy()]
    return funnel, df


def rank(survivors: pd.DataFrame, spec: Spec) -> pd.DataFrame:
    """Composite score = weighted mean of percentile ranks (0-1, higher is better).

    Names missing a ranking field get the worst percentile for that key; ties
    break on market cap (desc) then symbol, so the order is fully deterministic.
    """
    df = survivors.copy()
    if df.empty:
        df["score"] = []
        return df
    total_w = sum(r["weight"] for r in spec.rank)
    score = np.zeros(len(df))
    for r in spec.rank:
        x = pd.to_numeric(df[r["field"]], errors="coerce")
        pct = x.rank(pct=True, ascending=(r["direction"] == "desc"), method="average")
        pct = pct.fillna(0.0)
        score += r["weight"] * pct.to_numpy()
        df[f"rank_pct_{r['field']}"] = pct.to_numpy()
    df["score"] = score / total_w
    df = df.sort_values(["score", "market_cap", "symbol"], ascending=[False, False, True])
    df.insert(0, "rank", range(1, len(df) + 1))
    return df.reset_index(drop=True)


def check_funnel(funnel: list[dict]) -> None:
    """Arithmetic invariants: in = pass + fail + missing; next in = this pass."""
    for a, b in zip(funnel, funnel[1:]):
        assert b["n_in"] == a["n_pass"], (a, b)
    for s in funnel:
        assert s["n_in"] == s["n_pass"] + s["n_fail"] + s["n_missing"], s
        assert min(s["n_pass"], s["n_fail"], s["n_missing"]) >= 0, s
