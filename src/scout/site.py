"""Export recorded runs to docs/data/runs.js for the static site (no build step).

The site reads `window.SCOUT_RUNS`, so it also works when opened from disk.
"""

from __future__ import annotations

import json

from .config import ROOT, RUNS
from .report import table_columns
from .spec import FIELDS

SITE_RUNS = ["a-midcap-pullback", "b-ai-infra-laggards", "c-oversold-volume"]


def export() -> None:
    out = []
    for name in SITE_RUNS:
        p = RUNS / name / "run.json"
        if not p.exists():
            print(f"skip {name}: no run.json")
            continue
        rec = json.loads(p.read_text(encoding="utf-8"))
        cols = table_columns(rec)
        out.append({
            "id": name,
            "as_of": rec["as_of"],
            "generated_at": rec["generated_at"],
            "llm": rec["llm"],
            "data": rec["data"],
            "observation": rec["observation"],
            "spec": rec["spec"],
            "attempts": len(rec["translation_attempts"]),
            "funnel": rec["funnel"],
            "columns": cols,
            "ranked": [{c: r.get(c) for c in cols} for r in rec["ranked"][:15]],
            "n_ranked": len(rec["ranked"]),
            "top_n": rec["top_n"],
            "explanations": rec["explanations"],
            "limits": rec["limits"],
        })
    dst = ROOT / "docs" / "data" / "runs.js"
    dst.parent.mkdir(parents=True, exist_ok=True)
    tracking = {}
    tp = RUNS / "tracking.json"
    if tp.exists():
        tracking = json.loads(tp.read_text(encoding="utf-8"))
    fields = {f.name: {"kind": f.kind, "desc": f.desc} for f in FIELDS.values()}
    dst.write_text("window.SCOUT_FIELDS = " + json.dumps(fields) + ";\n"
                   + "window.SCOUT_TRACKING = " + json.dumps(tracking, indent=1) + ";\n"
                   + "window.SCOUT_RUNS = " + json.dumps(out, ensure_ascii=False, indent=1) + ";\n",
                   encoding="utf-8")
    print(f"wrote {dst} ({len(out)} runs)")
    export_try()


# ---------- "Try your own": schema and snapshot for the browser ----------

SNAPSHOT_DIGITS = 10  # significant digits kept in the browser snapshot (parity-tested against the recorded runs)
SNAPSHOT_TEXT_COLS = ["symbol", "name", "sic_desc"]
SNAPSHOT_EXTRA_NUM = ["sic", "cik"]


def schema_payload(as_of: str, manifest: dict) -> dict:
    from .llm import PROVIDERS
    from .spec import (COND_KEYS, INDUSTRIES, MAX_TOP_N, OPS, RANK_KEYS, THEMES, TOP_KEYS, UNIVERSE_KEYS)
    from .translate import SYSTEM
    return {
        "fields": {f.name: {"group": f.group, "kind": f.kind, "desc": f.desc} for f in FIELDS.values()},
        "ops": sorted(OPS), "top_keys": sorted(TOP_KEYS), "universe_keys": sorted(UNIVERSE_KEYS),
        "cond_keys": sorted(COND_KEYS), "rank_keys": sorted(RANK_KEYS), "max_top_n": MAX_TOP_N,
        "industries": {k: [d, sorted(c)] for k, (d, c) in INDUSTRIES.items()},
        "themes": {k: [d, sorted(s)] for k, (d, s) in THEMES.items()},
        "translate_system_prompt": SYSTEM,
        "model": PROVIDERS["deepseek"]["model"],
        "as_of": as_of,
        "short_interest_available": manifest.get("short_interest_settlement") is not None,
        "data": {k: manifest[k] for k in ("as_of", "last_price_date", "universe_rule", "n_companies",
                                          "short_interest_settlement")},
    }


def _num_or_none(v, digits: int):
    import math
    if v is None:
        return None
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    if math.isnan(x) or math.isinf(x):
        return None
    return float(f"{x:.{digits}g}")


def snapshot_payload(features) -> dict:
    """Columnar snapshot: every whitelisted field plus identifiers, NaN -> null."""
    import pandas as pd
    cols = {}
    for c in SNAPSHOT_TEXT_COLS:
        cols[c] = [None if pd.isna(v) else str(v) for v in features[c]]
    for c in SNAPSHOT_EXTRA_NUM:
        cols[c] = [_num_or_none(v, 12) for v in features[c]]
    for name, f in FIELDS.items():
        if f.kind == "bool":
            cols[name] = [None if pd.isna(v) else str(v).lower() == "true" for v in features[name]]
        else:
            cols[name] = [_num_or_none(v, SNAPSHOT_DIGITS) for v in features[name]]
    return {"n": len(features), "columns": cols}


def snapshot_frame(payload: dict):
    """The browser snapshot back as a DataFrame (what the JS screen sees), for parity tests."""
    import pandas as pd
    df = pd.DataFrame(payload["columns"])
    for name, f in FIELDS.items():
        if f.kind != "bool":
            df[name] = pd.to_numeric(df[name], errors="coerce").astype(float)
    df["sic"] = pd.to_numeric(df["sic"], errors="coerce")
    return df


def export_try(as_of: str | None = None) -> None:
    from .pipeline import SNAPSHOTS, load_features
    as_of = as_of or sorted(p.name for p in SNAPSHOTS.glob("*") if (p / "features.csv.gz").exists())[-1]
    features, manifest = load_features(as_of)
    data = ROOT / "docs" / "data"
    (data / "schema.js").write_text("window.SCOUT_SCHEMA = " + json.dumps(schema_payload(as_of, manifest), ensure_ascii=False)
                                    + ";\n", encoding="utf-8", newline="\n")
    snap = snapshot_payload(features)
    p = data / f"snapshot-{as_of}.js"
    p.write_text("window.SCOUT_SNAPSHOT = " + json.dumps(snap, separators=(",", ":"), ensure_ascii=False) + ";\n",
                 encoding="utf-8", newline="\n")
    print(f"wrote {p} ({p.stat().st_size / 1e6:.2f} MB, {snap['n']} companies) and schema.js")
