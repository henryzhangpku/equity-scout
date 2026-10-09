"""observation -> spec -> funnel -> ranked table -> cited explanations -> run folder."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from . import VERSION
from .config import DATA_DIR, ROOT, RUNS
from .data.base import Document, NoTranscripts
from .llm import LLM
from .narrative import explain, shown_text
from .screen import check_funnel, describe, rank, run_screen, sector_breakdown
from .sectors import MAPPING_VERSION
from .translate import PROMPT_VERSION
from .spec import FIELDS, Spec

SNAPSHOTS = DATA_DIR / "snapshots"

TABLE_FIELDS = ["symbol", "name", "sector", "industry_group", "sic_desc", "market_cap", "close", "drawdown_52w", "pct_vs_sma50",
                "mom_3m", "rsi14", "volume_ratio_50d", "revenue_growth_yoy", "revenue_growth_q_yoy",
                "revenue_growth_accel", "fcf_margin", "operating_margin", "short_pct_shares_out",
                "days_to_cover", "prov_revenue_period_end", "prov_revenue_filed"]


def load_features(as_of: str) -> tuple[pd.DataFrame, dict]:
    d = SNAPSHOTS / as_of
    if not (d / "features.csv.gz").exists():
        raise FileNotFoundError(f"no feature snapshot for {as_of}; build it with `scout build --as-of {as_of}`")
    return (pd.read_csv(d / "features.csv.gz", compression="gzip", low_memory=False),
            json.loads((d / "manifest.json").read_text()))


def slug(text: str, n: int = 6) -> str:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return "-".join(words[:n]) or "run"


def _clean(v):
    if isinstance(v, (np.floating, float)):
        return None if not np.isfinite(v) else float(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    return v


class RecordedDocuments:
    """DocumentSource that replays the exact texts a recorded run showed the model."""

    def __init__(self, run_dir: Path):
        self.dir = run_dir
        self.meta = {}
        rj = run_dir / "run.json"
        if rj.exists():
            for ex in json.loads(rj.read_text(encoding="utf-8"))["explanations"]:
                self.meta[ex["symbol"]] = ex["documents"]

    def earnings_documents(self, symbol: str, cik: int, as_of: date) -> list[Document]:
        out = []
        for m in self.meta.get(symbol, []):
            text = (self.dir / "docs" / f"{m['doc_id']}.txt").read_text(encoding="utf-8")
            out.append(Document(doc_id=m["doc_id"], kind=m["kind"], title=m["title"], url=m["url"],
                                filed=m["filed"], text=text, full_length=m["chars_total"]))
        return out


@dataclass
class RunResult:
    run_dir: Path
    record: dict


def why_flagged(row: pd.Series, spec: Spec) -> list[str]:
    out = []
    for c in spec.conditions:
        f = c["field"]
        v = row.get(f)
        if FIELDS[f].kind == "ratio" and isinstance(v, (int, float)) and np.isfinite(v):
            vs = f"{v * 100:+.1f}%"
        elif isinstance(v, float) and np.isfinite(v):
            vs = f"{v:,.4g}"
        else:
            vs = str(v)
        ref = f" (vs {c['ref']} = {row.get(c['ref']):,.4g})" if "ref" in c else ""
        out.append(f"{describe(c)}: actual {f} = {vs}{ref}")
    return out


DEFAULT = object()


def _table(ranked: pd.DataFrame, spec: Spec) -> list[dict]:
    rank_cols = ["rank", "score"] + TABLE_FIELDS + [c for c in ranked.columns if c.startswith("rank_pct_")]
    cond_cols = sorted({c["field"] for c in spec.conditions} | {c["ref"] for c in spec.conditions if "ref" in c}
                       | {r["field"] for r in spec.rank})
    cols = list(dict.fromkeys(rank_cols + cond_cols + ["cik"]))
    return [{k: _clean(v) for k, v in r.items()} for r in ranked[[c for c in cols if c in ranked.columns]]
            .to_dict(orient="records")]


def execute(spec: Spec, translation: list[dict], as_of: str, llm: LLM, docs_source=None,
            run_dir: Path | None = None, top_n: int | None = None, log=print,
            news_source=DEFAULT, record_picks: bool = False, on_event=None,
            tolerate_errors: bool = False, prompt_version: int | None = None) -> RunResult:
    """Run the screen and the narrative engine and write the run folder.

    on_event(kind, payload), if given, is called as results become available:
    "screen" (funnel + ranked table), "explaining" (symbol), "explanation" (one
    name's validated explanation). With tolerate_errors, a failure while reading
    one name's documents or calling the model becomes that name's
    "not enough evidence" card instead of aborting the run (used by scout serve).
    """
    emit = on_event or (lambda kind, payload: None)
    features, manifest = load_features(as_of)
    funnel, survivors = run_screen(features, spec)
    check_funnel(funnel)
    ranked = rank(survivors, spec)
    n = top_n or spec.top_n
    top = ranked.head(n)

    run_dir = run_dir or RUNS / f"{as_of}-{slug(spec.observation)}"
    if docs_source is None:
        from .data.edgar_docs import EdgarDocuments
        docs_source = EdgarDocuments()
    if news_source is DEFAULT:
        from .data.news import AlpacaNews
        news_source = AlpacaNews()
    transcripts = NoTranscripts()
    table = _table(ranked, spec)
    breakdown = sector_breakdown(survivors)
    emit("screen", {"funnel": funnel, "ranked": table, "top_n": n, "as_of": as_of, "data": manifest,
                    "sector_breakdown": breakdown})
    explanations = []
    shown: dict[str, str] = {}
    for i, (_, row) in enumerate(top.iterrows()):
        log(f"  reading filings for {row['symbol']} ...")
        emit("explaining", {"symbol": row["symbol"], "i": i + 1, "n": len(top)})
        try:
            docs = docs_source.earnings_documents(row["symbol"], int(row["cik"]), date.fromisoformat(as_of))
            if news_source is not None:
                docs += news_source.news(row["symbol"], date.fromisoformat(as_of))
            docs += transcripts.transcripts(row["symbol"], date.fromisoformat(as_of))
            # the prompt sees the same metrics as when the runs were recorded (sector columns are display-only)
            metrics = {k: _clean(row.get(k)) for k in TABLE_FIELDS if k not in ("symbol", "name", "sector", "industry_group")}
            ex = explain(row["symbol"], row["name"], metrics, why_flagged(row, spec), docs, llm,
                         transcripts_note=f"no earnings-call transcript was consulted ({transcripts.reason})").to_dict()
            for d in docs:
                shown[d.doc_id] = shown_text(d)
        except Exception as e:  # noqa: BLE001 - one name's failure must not end a live demo
            if not tolerate_errors:
                raise
            from .narrative import Explanation
            ex = Explanation(symbol=row["symbol"], verdict="not enough evidence",
                             model_status=f"failed: {type(e).__name__}: {str(e)[:200]}").to_dict()
        explanations.append(ex)
        emit("explanation", ex)

    record = {
        "tool": f"equity-scout {VERSION}",
        "as_of": as_of,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "data": manifest,
        "llm": {"provider": llm.provider, "model": llm.model},
        "observation": spec.observation,
        "spec": spec.to_dict(),
        "translation_attempts": translation,
        "prompt_version": prompt_version if prompt_version is not None else PROMPT_VERSION,
        "funnel": funnel,
        "ranked": table,
        "top_n": n,
        "sector_breakdown": breakdown,
        "sector_mapping_version": MAPPING_VERSION,
        "explanations": explanations,
        "limits": LIMITS,
    }
    if run_dir.exists():
        shutil.rmtree(run_dir / "docs", ignore_errors=True)
    (run_dir / "docs").mkdir(parents=True, exist_ok=True)
    for doc_id, text in shown.items():
        (run_dir / "docs" / f"{doc_id}.txt").write_text(text, encoding="utf-8")
    (run_dir / "run.json").write_text(json.dumps(record, indent=1, ensure_ascii=False), encoding="utf-8")
    from .report import markdown
    (run_dir / "report.md").write_text(markdown(record), encoding="utf-8")
    if record_picks:
        from .track import append_picks
        picks = [{"symbol": r["symbol"], "rank": r["rank"], "entry_close": r["close"]} for r in table[:n]]
        bench = {k: v for k, v in (manifest.get("benchmark_closes") or {}).items() if k in ("SPY", "SMH")}
        append_picks(run_dir.name, as_of, spec.observation, picks, bench)
    return RunResult(run_dir=run_dir, record=record)


LIMITS = [
    "Prices: Alpaca SIP daily bars, split and dividend adjusted; no intraday data used.",
    "Fundamentals: SEC XBRL companyfacts, US-GAAP filers only. Foreign private issuers (IFRS, 20-F/40-F) "
    "and companies without standard tags drop out as 'missing', they are not guessed.",
    "Market cap uses the latest cover-page share count; for multi-class issuers it can understate.",
    "Industry groups are SEC SIC codes, a coarse proxy for a theme (no GICS/BICS in free data).",
    "Short interest: FINRA consolidated short interest (twice monthly, non-commercial use); "
    "% is of shares outstanding, not float.",
    "Earnings-call transcripts are licensed content and were not used; explanations rely on the "
    "8-K earnings release, 10-Q/10-K MD&A, and news headlines and summaries (Alpaca / Benzinga), "
    "never full articles.",
    "No consensus estimates, revisions, ownership or borrow-cost data: those need a licensed source.",
]
