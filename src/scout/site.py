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
