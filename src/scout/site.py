"""Export recorded runs to docs/data/runs.js for the static site (no build step).

The site reads `window.SCOUT_RUNS`, so it also works when opened from disk.
"""

from __future__ import annotations

import json

from .config import ROOT, RUNS
from .report import table_columns
from .spec import BENCH_PLAIN, FIELDS, LABELS

SITE_RUNS = ["a-midcap-pullback", "b-ai-infra-laggards", "c-oversold-volume"]
# one-click examples: (run folder, chip label); each folder is a full recorded run (spec, funnel, explanations)
SITE_CHIPS = [
    ("chip-consumer-brands", "Quality consumer brands down 30%+ with strong free cash flow"),
    ("chip-quality-drawdown", "Profitable names over $2B, down 30%+ and still growing"),
    ("chip-ai-laggards", "AI suppliers lagging the chip index while revenue accelerates"),
    ("chip-oversold-volume", "Oversold large caps on heavy volume"),
    ("chip-cash-rich-lows", "Cash-rich small caps down 40%+ from their highs"),
    ("chip-short-squeeze-setup", "Heavily shorted, profitable, back above the 50-day average"),
    ("chip-growth-momentum", "Fast growers over $2B beating the S&P 500"),
]


def export_chips() -> tuple[list, dict]:
    meta, ex = [], {}
    for name, label in SITE_CHIPS:
        p = RUNS / name / "run.json"
        if not p.exists():
            print(f"skip chip {name}: no run.json")
            continue
        rec = json.loads(p.read_text(encoding="utf-8"))
        meta.append({"id": name, "label": label, "observation": rec["observation"], "spec": rec["spec"],
                     "generated": rec["generated_at"][:10], "as_of": rec["as_of"], "model": rec["llm"]["model"]})
        ex[name] = rec["explanations"]
    return meta, ex


def _sector_lookup():
    from .pipeline import SNAPSHOTS, load_features
    from .sectors import classify
    as_of = sorted(p.name for p in SNAPSHOTS.glob("*") if (p / "features.csv.gz").exists())[-1]
    f, _ = load_features(as_of)
    return {sym: classify(sic, sym) for sym, sic in zip(f["symbol"], f["sic"])}


def _with_sector(rows: list[dict], look: dict) -> list[dict]:
    out = []
    for r in rows:
        sec, grp = look.get(r.get("symbol"), (None, None))
        out.append({**r, "sector": r.get("sector", sec), "industry_group": r.get("industry_group", grp)})
    return out


def _breakdown(rows: list[dict]) -> list[dict]:
    from collections import Counter
    c = Counter((r.get("sector") or "No sector") for r in rows)
    return [{"sector": k, "n": v} for k, v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))]


def export() -> None:
    look = _sector_lookup()
    out = []
    for name in SITE_RUNS:
        p = RUNS / name / "run.json"
        if not p.exists():
            print(f"skip {name}: no run.json")
            continue
        rec = json.loads(p.read_text(encoding="utf-8"))
        cols = table_columns(rec)
        cols = cols[:3] + ["sector"] + cols[3:]
        rows = _with_sector(rec["ranked"], look)
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
            "ranked": [{c: r.get(c) for c in cols} for r in rows[:15]],
            "sector_breakdown": rec.get("sector_breakdown") or _breakdown(rows),
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
    fields = {f.name: {"kind": f.kind, "desc": f.desc, "label": LABELS[f.name]} for f in FIELDS.values()}
    chips, chip_ex = export_chips()
    (dst.parent / "chips-ex.js").write_text("window.SCOUT_CHIP_EX = " + json.dumps(chip_ex, ensure_ascii=False) + ";\n",
                                           encoding="utf-8", newline="\n")
    dst.write_text("window.SCOUT_FIELDS = " + json.dumps(fields) + ";\n"
                   + "window.SCOUT_TRACKING = " + json.dumps(tracking, indent=1) + ";\n"
                   + "window.SCOUT_BENCH = " + json.dumps(BENCH_PLAIN) + ";\n"
                   + "window.SCOUT_CHIPS = " + json.dumps(chips, ensure_ascii=False) + ";\n"
                   + "window.SCOUT_RUNS = " + json.dumps(out, ensure_ascii=False, indent=1) + ";\n",
                   encoding="utf-8", newline="\n")
    print(f"wrote {dst} ({len(out)} runs)")
    export_try()


# ---------- "Try your own": schema and snapshot for the browser ----------

SNAPSHOT_DIGITS = 10  # significant digits kept in the browser snapshot (parity-tested against the recorded runs)
SNAPSHOT_TEXT_COLS = ["symbol", "name", "sic_desc"]
SNAPSHOT_EXTRA_NUM = ["sic", "cik"]


def schema_payload(as_of: str, manifest: dict) -> dict:
    from .llm import PROVIDERS
    from .spec import (COND_KEYS, INDUSTRIES, MAX_TOP_N, OPS, RANK_KEYS, THEMES, TOP_KEYS, UNIVERSE_KEYS)
    from .sectors import table as sector_table
    from .translate import SYSTEM
    return {
        "fields": {f.name: {"group": f.group, "kind": f.kind, "desc": f.desc, "label": LABELS[f.name]}
                   for f in FIELDS.values()},
        "bench_plain": BENCH_PLAIN,
        "ops": sorted(OPS), "top_keys": sorted(TOP_KEYS), "universe_keys": sorted(UNIVERSE_KEYS),
        "cond_keys": sorted(COND_KEYS), "rank_keys": sorted(RANK_KEYS), "max_top_n": MAX_TOP_N,
        "industries": {k: [d, sorted(c)] for k, (d, c) in INDUSTRIES.items()},
        "themes": {k: [d, sorted(s)] for k, (d, s) in THEMES.items()},
        "translate_system_prompt": SYSTEM,
        "sector_map": sector_table(),
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
    write_sectors_page(features)


def sector_coverage(features) -> dict:
    from collections import Counter
    from .sectors import classify
    pairs = [classify(sic, sym) for sic, sym in zip(features["sic"], features["symbol"])]
    secs = Counter(p[0] for p in pairs if p[0])
    grps = Counter(p[1] for p in pairs if p[1])
    return {"n": len(pairs), "with_sector": sum(secs.values()), "sectors": dict(secs.most_common()),
            "groups": dict(grps.most_common())}


def write_sectors_page(features) -> None:
    """docs/sectors.html: the published, versioned SIC -> sector mapping with coverage."""
    import html as H
    from .sectors import GROUPS, KNOWN_MISFITS, MAPPING_VERSION, OVERRIDES, RULES, SECTORS
    cov = sector_coverage(features)
    e = H.escape
    rows_by_group: dict[str, list[str]] = {}
    for lo, hi, sec, grp in RULES:
        rows_by_group.setdefault(grp, []).append(str(lo) if lo == hi else f"{lo}-{hi}")
    body = []
    body.append(f"<p class='lede'>Mapping version <strong>{e(MAPPING_VERSION)}</strong>. Each company's sector comes from "
                "the SIC code it reports to the SEC. Rules are applied in order, specific codes before broad ranges, so the "
                "first match wins; a short list of ticker overrides fixes large, well-known misfits. The sector names follow "
                "the familiar 11-sector convention, but this is not the licensed GICS classification.</p>")
    pct = 100 * cov["with_sector"] / cov["n"]
    body.append(f"<div class='panel'><h2>Coverage</h2><p>{cov['with_sector']:,} of {cov['n']:,} companies "
                f"({pct:.1f}%) in the 2026-10-08 universe have a sector.</p><table><thead><tr><th class='l'>Sector</th>"
                "<th>Companies</th></tr></thead><tbody>")
    for sec in SECTORS:
        body.append(f"<tr><td class='l'>{e(sec)}</td><td>{cov['sectors'].get(sec, 0):,}</td></tr>")
    body.append("</tbody></table></div>")
    body.append("<div class='panel'><h2>Sectors, industry groups and SIC codes</h2><div class='tablewrap'><table><thead><tr>"
                "<th class='l'>Sector</th><th class='l'>Industry group</th><th class='l'>SIC codes (in rule order)</th>"
                "<th>Companies</th></tr></thead><tbody>")
    for sec in SECTORS:
        for grp in [g for g in GROUPS if GROUPS[g] == sec]:
            body.append(f"<tr><td class='l'>{e(sec)}</td><td class='l'>{e(grp)}</td><td class='l wrapcell'>"
                        f"{e(', '.join(rows_by_group.get(grp, [])) or 'overrides only')}</td>"
                        f"<td>{cov['groups'].get(grp, 0):,}</td></tr>")
    body.append("</tbody></table></div></div>")
    body.append("<div class='panel'><h2>Ticker overrides</h2><p class='muted'>Only for large, well-known misfits.</p>"
                "<div class='tablewrap'><table><thead><tr><th class='l'>Ticker</th><th class='l'>Sector</th>"
                "<th class='l'>Industry group</th><th class='l'>Why</th></tr></thead><tbody>")
    for t, (sec, grp, why) in sorted(OVERRIDES.items()):
        body.append(f"<tr><td class='l'>{e(t)}</td><td class='l'>{e(sec)}</td><td class='l'>{e(grp)}</td>"
                    f"<td class='l wrapcell'>{e(why)}</td></tr>")
    body.append("</tbody></table></div></div>")
    body.append("<div class='panel'><h2>Known misfits</h2><ul>" + "".join(f"<li>{e(m)}</li>" for m in KNOWN_MISFITS) +
                "</ul><p class='muted'>Machine-readable: <code>window.SCOUT_SCHEMA.sector_map</code> in "
                "<a href='data/schema.js'>data/schema.js</a>; source: <code>src/scout/sectors.py</code>.</p></div>")
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sector Mapping</title>
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap">
<link rel="stylesheet" href="style.css"><script src="theme.js"></script>
<style>.wrapcell {{ white-space: normal; min-width: 220px; }} .tablewrap {{ max-height: none; }}</style>
</head><body>
<nav class="topnav" aria-label="Site"><div class="navin">
<a class="brand" href="index.html"><img src="favicon.svg" alt="" width="28" height="28"><span>Equity Scout</span></a>
<div class="navlinks"><a href="index.html">Home</a><a href="index.html#try">Try it</a>
<button id="theme-toggle" class="iconbtn" type="button" aria-label="Switch theme"></button></div></div></nav>
<main class="wrap" style="padding-top:40px"><h1 style="font-size:clamp(28px,4vw,42px)">Sector mapping</h1>
{''.join(body)}</main></body></html>
"""
    (ROOT / "docs" / "sectors.html").write_text(page, encoding="utf-8", newline="\n")
    print(f"wrote docs/sectors.html (coverage {cov['with_sector']}/{cov['n']})")
