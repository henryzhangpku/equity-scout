"""The tool layer behind the MCP server: plain functions that return JSON-ready dicts.

Nothing here imports the MCP SDK, so the functions can be tested and reused without it.
Every number a tool returns is computed by the existing deterministic code (validator,
screen, ranker) or read from a recorded run; no model writes or computes anything here.
"""

from __future__ import annotations

import json
from pathlib import Path

from .config import RUNS
from .pipeline import SNAPSHOTS, _table, load_features
from .screen import check_funnel, rank, run_screen, sector_breakdown
from .spec import FIELDS, INDUSTRIES, MAX_TOP_N, SECTOR_LIST, THEMES, GROUP_NAMES, SpecError, validate
from .track import read_ledger, verify_chain

KIND_UNITS = {
    "usd": "US dollars",
    "ratio": "decimal ratio (0.10 means 10%)",
    "number": "plain number",
    "bool": "true/false (use op '==')",
    "days": "days",
}


def snapshots() -> list[str]:
    """Dates of the committed feature snapshots, oldest first."""
    return sorted(p.name for p in SNAPSHOTS.glob("*") if (p / "features.csv.gz").exists())


def _resolve_as_of(as_of: str | None) -> tuple[str | None, str | None]:
    """(as_of, problem). Only dates with a committed snapshot are accepted."""
    snaps = snapshots()
    if not snaps:
        return None, "no feature snapshot found; run `scout build --as-of YYYY-MM-DD` first"
    if as_of is None:
        return snaps[-1], None
    if as_of not in snaps:
        return None, f"no snapshot for {as_of!r}; available: {snaps}"
    return as_of, None


def _snapshot_columns(as_of: str) -> set[str]:
    import pandas as pd
    return set(pd.read_csv(SNAPSHOTS / as_of / "features.csv.gz", nrows=0).columns)


def list_fields() -> dict:
    snaps = snapshots()
    latest = snaps[-1] if snaps else None
    cols = _snapshot_columns(latest) if latest else set()
    fields = [{"name": f.name, "group": f.group, "kind": f.kind, "units": KIND_UNITS[f.kind],
               "description": f.desc, "in_latest_snapshot": f.name in cols} for f in FIELDS.values()]
    return {
        "latest_snapshot": latest,
        "snapshots": snaps,
        "fields": fields,
        "operators": ["<", "<=", ">", ">=", "between", "=="],
        "universe_keys": {
            "market_cap_min / market_cap_max / min_price / min_avg_dollar_volume": "non-negative numbers, US dollars",
            "sectors": SECTOR_LIST,
            "industry_groups": GROUP_NAMES,
            "industries / exclude_industries": {k: d for k, (d, _) in INDUSTRIES.items()},
            "themes": {k: d for k, (d, _) in THEMES.items()},
        },
        "spec_shape": {
            "observation": "the user's idea in plain English (required)",
            "universe": "object with the keys above (optional)",
            "conditions": "non-empty list of {field, op, value | ref, why}; 'between' takes value [low, high]; "
                          "'ref' compares with another field of the same kind",
            "rank": "non-empty list of {field, direction: 'asc'|'desc', weight > 0}",
            "top_n": f"integer 1-{MAX_TOP_N} (default 5)",
            "unmapped": "list of {text, reason} for parts of the idea no field can express",
            "notes": "free text on how the idea was interpreted",
        },
        "conventions": "Ratios are decimals (0.10 = 10%). Money is US dollars. Fields with "
                       "in_latest_snapshot=false are valid in a spec but the screen refuses them on that snapshot.",
    }


def _short_interest_ok(as_of: str) -> bool:
    manifest = json.loads((SNAPSHOTS / as_of / "manifest.json").read_text())
    return manifest.get("short_interest_settlement") is not None


def validate_spec(spec: dict) -> dict:
    as_of, _ = _resolve_as_of(None)
    si_ok = _short_interest_ok(as_of) if as_of else True
    try:
        s = validate(spec, short_interest_available=si_ok)
    except SpecError as e:
        return {"ok": False, "problems": e.problems}
    return {"ok": True, "problems": [], "spec": s.to_dict()}


def run_screen_tool(spec: dict, as_of: str | None = None) -> dict:
    as_of, problem = _resolve_as_of(as_of)
    if problem:
        return {"ok": False, "refused": "snapshot", "problems": [problem]}
    features, manifest = load_features(as_of)
    try:
        s = validate(spec, short_interest_available=manifest.get("short_interest_settlement") is not None)
    except SpecError as e:
        return {"ok": False, "refused": "invalid spec", "problems": e.problems}
    try:
        funnel, survivors = run_screen(features, s)
    except SpecError as e:  # a whitelisted field the snapshot was built without
        return {"ok": False, "refused": "field not in snapshot", "as_of": as_of, "problems": e.problems}
    check_funnel(funnel)
    ranked = rank(survivors, s)
    rows = _table(ranked, s)[: s.top_n]
    for r in rows:
        r.pop("cik", None)
    return {
        "ok": True,
        "as_of": as_of,
        "spec": s.to_dict(),
        "funnel": [{"step": f["step"], "kind": f["kind"], "entered": f["n_in"], "passed": f["n_pass"],
                    "failed": f["n_fail"], "no_data": f["n_missing"]} for f in funnel],
        "survivors": len(ranked),
        "sector_breakdown": sector_breakdown(survivors),
        "top": rows,
        "not_screened": s.unmapped,
        "notes": "Numbers are computed by code from the committed snapshot. Ratios are decimals. "
                 "'no_data' names lacked the value and were dropped, not guessed. score is the weighted "
                 "mean of percentile ranks (0-1). Explanations exist only for names in recorded runs; see explain.",
    }


def recorded_runs() -> dict[str, Path]:
    """run_id -> run.json for every recorded screen run under runs/ (including runs/live/)."""
    out = {}
    for p in sorted(RUNS.rglob("run.json")):
        rid = p.parent.relative_to(RUNS).as_posix()
        if not any(part.startswith(".") for part in rid.split("/")):
            out[rid] = p
    return out


def _cited(claims: list[dict]) -> list[dict]:
    return [{"claim": c["claim"], "quote": c["quote"], "doc_id": c["doc_id"], "url": c.get("url", ""),
             "source_kind": c.get("source_kind", "")} for c in claims if c.get("ok")]


def explain_tool(symbol: str, run_id: str | None = None) -> dict:
    sym = symbol.strip().upper()
    runs = recorded_runs()
    if run_id is not None:
        if run_id not in runs:
            return {"ok": False, "symbol": sym, "problems": [f"no recorded run {run_id!r}; available: {sorted(runs)}"]}
        runs = {run_id: runs[run_id]}
    found = []
    for rid, path in runs.items():
        rec = json.loads(path.read_text(encoding="utf-8"))
        for ex in rec.get("explanations", []):
            if ex.get("symbol", "").upper() != sym:
                continue
            found.append({
                "run_id": rid, "as_of": rec.get("as_of"), "observation": rec.get("observation"),
                "verdict": ex["verdict"], "thesis": _cited(ex.get("thesis", [])),
                "bear_case": _cited(ex.get("bear_case", [])),
                "stripped_claims": len(ex.get("stripped", [])),
                "documents": [{"doc_id": d["doc_id"], "kind": d.get("kind"), "title": d.get("title"),
                               "url": d.get("url"), "filed": d.get("filed")} for d in ex.get("documents", [])],
            })
    if not found:
        where = f"run {run_id!r}" if run_id else "any recorded run"
        return {"ok": False, "symbol": sym, "explanations": [],
                "problems": [f"no recorded explanation for {sym} in {where}. This server does not write new "
                             "explanations; they come only from recorded runs whose every quote was checked "
                             "verbatim against the source document."]}
    return {"ok": True, "symbol": sym, "explanations": found,
            "notes": "Each claim's quote was verified verbatim against the cited document when the run was "
                     "recorded; claims that failed the check were stripped (counted, not shown)."}


def loop_runs() -> list[str]:
    return sorted(p.parent.name for p in RUNS.glob("*/summary.json") if (p.parent / "ledger.jsonl").exists())


def loop_report(run_id: str = "loop-2026-10-12") -> dict:
    available = loop_runs()
    if run_id not in available:
        return {"ok": False, "problems": [f"no recorded loop run {run_id!r}; available: {available}"]}
    d = RUNS / run_id
    s = json.loads((d / "summary.json").read_text(encoding="utf-8"))
    ledger = read_ledger(d / "ledger.jsonl")
    attempts = {e.get("step"): e for e in ledger if e.get("kind") == "attempt"}
    steps = []
    for x in s["steps"]:
        a = attempts.get(x["step"], {})
        disc = a.get("discovery") or {}
        steps.append({
            "step": x["step"], "id": x["id"], "hypothesis": a.get("description"), "status": x["status"],
            "discovery": {"t_stat": x["discovery_t"], "mean_excess_after_costs": x["discovery_excess"],
                          "events": x["discovery_events"], "p_value": disc.get("p_value"),
                          "hit_rate": disc.get("hit_rate")},
            "out_of_sample_opened": bool(a.get("oos_opened", False)), "oos_t_stat": x["oos_t"],
            "decision": x["decision"], "reason": x["reason"],
        })
    return {
        "ok": True, "run_id": run_id, "proposer": s["proposer"], "budget_K": s["budget_K"],
        "corrected_p": s["corrected_p"], "split": s["split"], "data": s["data"],
        "stop_reason": s["stop_reason"], "tried": s["tried"], "promoted": s["promoted"],
        "out_of_sample_opened_for": s["oos_opened"],
        "ledger_chain_intact": not verify_chain(ledger),
        "steps": steps,
        "notes": "A hypothesis opens the out-of-sample period only after passing discovery at the "
                 "Bonferroni-corrected threshold; the evaluator and split are fixed in code.",
    }
