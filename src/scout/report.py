"""Markdown report and terminal rendering for a run record."""

from __future__ import annotations

import json

from .spec import FIELDS


def fmt(field: str, v) -> str:
    if v is None:
        return "n/a"
    if isinstance(v, bool):
        return "yes" if v else "no"
    if isinstance(v, str):
        return v
    kind = FIELDS[field].kind if field in FIELDS else ""
    if field == "score" or field.startswith("rank_pct_"):
        return f"{v:.3f}"
    if kind == "ratio":
        return f"{v * 100:+.1f}%"
    if kind == "usd":
        if abs(v) >= 1e9:
            return f"${v / 1e9:,.1f}B"
        if abs(v) >= 1e6:
            return f"${v / 1e6:,.0f}M"
        return f"${v:,.2f}"
    if kind == "days":
        return f"{v:.1f}d"
    return f"{v:,.2f}" if isinstance(v, float) else str(v)


def funnel_lines(funnel: list[dict]) -> list[str]:
    out = ["| step | in | pass | fail | missing data |", "|---|---:|---:|---:|---:|"]
    for s in funnel:
        out.append(f"| {s['step']} | {s['n_in']} | {s['n_pass']} | {s['n_fail']} | {s['n_missing']} |")
    return out


def table_columns(rec: dict) -> list[str]:
    spec = rec["spec"]
    cols = ["rank", "symbol", "name", "score", "market_cap"]
    for c in spec["conditions"]:
        cols.append(c["field"])
        if "ref" in c:
            cols.append(c["ref"])
    for r in spec["rank"]:
        cols.append(r["field"])
    return list(dict.fromkeys(cols))


def markdown(rec: dict) -> str:
    L = [f"# Screen: {rec['observation']}", "",
         f"As of **{rec['as_of']}** (last price date {rec['data']['last_price_date']}). "
         f"Universe: {rec['data']['universe_rule']}. "
         f"Model: {rec['llm']['provider']} / {rec['llm']['model']} (translation and prose only; "
         "every filter, rank and number below is computed by code).", "",
         "## 1. Screen spec (proposed by the model, validated by code)", "", "```json",
         json.dumps(rec["spec"], indent=2), "```", ""]
    if rec["spec"].get("unmapped"):
        L += ["**Not screened: outside the schema**", ""]
        L += [f"- \"{u['text']}\": {u['reason']}" for u in rec["spec"]["unmapped"]]
        L.append("")
    L += ["## 2. Funnel", ""] + funnel_lines(rec["funnel"]) + [""]
    cols = table_columns(rec)
    L += [f"## 3. Ranked survivors ({len(rec['ranked'])})", "",
          "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rec["ranked"][:25]:
        L.append("| " + " | ".join(fmt(c, r.get(c)) for c in cols) + " |")
    if len(rec["ranked"]) > 25:
        L.append(f"\n({len(rec['ranked']) - 25} more in run.json)")
    L += ["", f"## 4. Why the dislocation might exist (top {rec['top_n']})", "",
          "Every quote below was checked by code to appear verbatim in the linked SEC document. "
          "Claims whose quotes failed the check were removed and are listed.", ""]
    for ex in rec["explanations"]:
        L += [f"### {ex['symbol']}: {ex['verdict']}", ""]
        for d in ex["documents"]:
            L.append(f"- source: [{d['title']}]({d['url']})")
        L.append("")
        if ex["thesis"]:
            L.append("**Thesis**")
            L += [f"- {c['claim']}  \n  > \"{c['quote']}\" ([{c['doc_id']}]({c['url']}))" for c in ex["thesis"]]
            L.append("")
        if ex["bear_case"]:
            L.append("**Bear case**")
            L += [f"- {c['claim']}  \n  > \"{c['quote']}\" ([{c['doc_id']}]({c['url']}))" for c in ex["bear_case"]]
            L.append("")
        if ex["stripped"]:
            L.append(f"*Stripped by the citation check ({len(ex['stripped'])}):* "
                     + "; ".join(f"\"{c['claim'][:80]}\" ({c['reason']})" for c in ex["stripped"]))
            L.append("")
        if ex.get("model_status"):
            L += [f"*{ex['model_status']}*", ""]
    L += ["## Data limits", ""] + [f"- {x}" for x in rec["limits"]] + [""]
    return "\n".join(L)
