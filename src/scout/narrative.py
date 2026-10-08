"""Cited explanations. The model writes; code checks every citation.

A claim survives only if
  1. it names a document that was actually given to the model,
  2. its quote appears verbatim in that document (after normalising whitespace,
     curly quotes and dash characters only; no case folding, no fuzzy match),
  3. the quote is 6-80 words (long enough to be specific, short enough to be a quote),
  4. every number written in the claim also appears in its quote.
Anything else is stripped and listed with the reason. If fewer than
MIN_THESIS_CLAIMS thesis claims survive, the verdict is "not enough evidence".
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field

from .data.base import Document
from .llm import LLM, parse_json

MIN_THESIS_CLAIMS = 2
DOC_CHAR_LIMIT = {"earnings_release": 24_000, "mdna": 40_000, "transcript": 40_000}

_TYPO = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-",
                       "—": "-", "‒": "-", "−": "-", " ": " ", " ": " ", " ": " "})


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.translate(_TYPO)).strip()


_NUM = re.compile(r"\d[\d,]*(?:\.\d+)?")


def numbers_in(s: str) -> set[str]:
    return {n.replace(",", "").rstrip(".") for n in _NUM.findall(s)}


@dataclass
class Claim:
    claim: str
    quote: str
    doc_id: str
    ok: bool = False
    reason: str = ""
    url: str = ""


@dataclass
class Explanation:
    symbol: str
    verdict: str                      # "explained" | "not enough evidence"
    thesis: list[Claim] = field(default_factory=list)
    bear_case: list[Claim] = field(default_factory=list)
    stripped: list[Claim] = field(default_factory=list)
    documents: list[dict] = field(default_factory=list)
    model_status: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


def check_claim(c: Claim, docs: dict[str, str]) -> Claim:
    """Validate one claim against the texts the model was shown (doc_id -> text)."""
    if c.doc_id not in docs:
        c.ok, c.reason = False, f"cites unknown document '{c.doc_id}'"
        return c
    q = normalize(c.quote)
    words = len(q.split())
    if words < 6 or words > 80:
        c.ok, c.reason = False, f"quote is {words} words (must be 6-80)"
        return c
    if q not in normalize(docs[c.doc_id]):
        c.ok, c.reason = False, "quote not found verbatim in the cited document"
        return c
    missing = numbers_in(c.claim) - numbers_in(q)
    if missing:
        c.ok, c.reason = False, f"claim states numbers not in its quote: {sorted(missing)}"
        return c
    c.ok, c.reason = True, ""
    return c


def shown_text(d: Document) -> str:
    lim = DOC_CHAR_LIMIT.get(d.kind, 30_000)
    return d.text[:lim]


SYSTEM = """You are an equity research analyst. A deterministic screen has flagged a stock as a
possible dislocation: its price behaviour and its reported fundamentals point in different
directions. You receive the computed numbers (exact, from code) and excerpts of the company's
own recent SEC filings. Explain what in the filings might account for the dislocation, and give
the bear case.

Hard rules:
- Every claim must carry a quote copied EXACTLY, character for character, from one of the
  documents provided, plus that document's doc_id. 6 to 60 words per quote. Code verifies
  each quote by exact string match and deletes any claim whose quote is not found.
- Do not use outside knowledge, news, price targets or anything not in the documents.
- Any number in a claim must appear in its quote. Put the computed screen numbers aside;
  they are context only.
- If the documents do not explain the dislocation, say so: return few or no thesis claims
  and set "evidence" to "thin". Never guess.
- 2 to 4 thesis claims, 1 to 3 bear-case claims, each claim one sentence.

Return JSON: {"thesis": [{"claim": str, "quote": str, "doc_id": str}],
              "bear_case": [{"claim": str, "quote": str, "doc_id": str}],
              "evidence": "sufficient" | "thin"}"""


def _fmt(v) -> str:
    if isinstance(v, float):
        return f"{v:.4g}"
    return str(v)


def explain(symbol: str, name: str, metrics: dict, why_flagged: list[str], docs: list[Document],
            llm: LLM, transcripts_note: str) -> Explanation:
    texts = {d.doc_id: shown_text(d) for d in docs}
    meta = [{"doc_id": d.doc_id, "kind": d.kind, "title": d.title, "url": d.url, "filed": d.filed,
             "chars_total": len(d.text), "chars_shown": len(texts[d.doc_id])} for d in docs]
    if not docs:
        return Explanation(symbol=symbol, verdict="not enough evidence", documents=meta,
                           model_status="no earnings documents found on EDGAR for this as-of date")
    body = [f"Company: {name} ({symbol})",
            "Why the screen flagged it: " + "; ".join(why_flagged),
            "Computed metrics: " + json.dumps({k: _fmt(v) for k, v in metrics.items()}),
            f"Note: {transcripts_note}.", ""]
    for d in docs:
        t = texts[d.doc_id]
        trunc = " (truncated)" if len(t) < len(d.text) else ""
        body.append(f"=== doc_id: {d.doc_id} | {d.title}{trunc} ===\n{t}\n")
    messages = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": "\n".join(body)}]
    raw = llm.complete(messages, tag=f"explain {symbol}", max_tokens=3000)
    ex = Explanation(symbol=symbol, verdict="not enough evidence", documents=meta)
    try:
        j = parse_json(raw)
    except json.JSONDecodeError:
        ex.model_status = "model output was not valid JSON; nothing kept"
        return ex
    urls = {d.doc_id: d.url for d in docs}
    for part in ("thesis", "bear_case"):
        for item in j.get(part, []) or []:
            if not isinstance(item, dict):
                continue
            c = check_claim(Claim(claim=str(item.get("claim", "")), quote=str(item.get("quote", "")),
                                  doc_id=str(item.get("doc_id", ""))), texts)
            c.url = urls.get(c.doc_id, "")
            (getattr(ex, part) if c.ok else ex.stripped).append(c)
    ex.model_status = f"model said evidence: {j.get('evidence', 'unspecified')}"
    if len(ex.thesis) >= MIN_THESIS_CLAIMS and j.get("evidence") != "thin":
        ex.verdict = "explained"
    return ex
