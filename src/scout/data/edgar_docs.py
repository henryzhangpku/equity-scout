"""Earnings materials from EDGAR: the latest earnings press release (8-K item
2.02, exhibit 99.1) and MD&A from the latest 10-Q or 10-K, filed on or before
the as-of date. Free and public; transcripts are not (see base.NoTranscripts).
"""

from __future__ import annotations

import html
import re
from datetime import date
from html.parser import HTMLParser

from ..http import fetch
from .base import Document
from .sec import SecData, recent_filings

ARCHIVE = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc}"
BLOCK = {"p", "div", "br", "tr", "li", "h1", "h2", "h3", "h4", "h5", "h6", "table", "section", "td", "th"}
SKIP = {"script", "style", "ix:header", "head", "title"}


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
        elif tag in BLOCK:
            self.out.append("\n" if tag not in ("td", "th") else " ")

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
        elif tag in BLOCK and tag not in ("td", "th"):
            self.out.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


def html_to_text(raw: str) -> str:
    raw = re.sub(r"^.*?<TEXT>", "", raw, count=1, flags=re.S) if raw.lstrip().startswith("<DOCUMENT>") else raw
    p = _Text()
    p.feed(raw)
    t = html.unescape("".join(p.out)).replace("\xa0", " ").replace("​", "")
    t = re.sub(r"[ \t\r\f\v]+", " ", t)
    t = re.sub(r" *\n *", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def _decode(b: bytes) -> str:
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return b.decode(enc)
        except UnicodeDecodeError:
            continue
    return b.decode("utf-8", "replace")


def _archive(cik: int, accn: str) -> str:
    return ARCHIVE.format(cik=cik, acc=accn.replace("-", ""))


def exhibit_991_url(cik: int, accn: str) -> str | None:
    """Find the EX-99.1 document in a filing's index page."""
    idx = _archive(cik, accn) + f"/{accn}-index.htm"
    raw = fetch(idx, source="edgar", allow_404=True)
    if not raw:
        return None
    page = _decode(raw)
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", page, flags=re.S | re.I)
    best = None
    for r in rows:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", r, flags=re.S | re.I)
        if len(cells) < 4:
            continue
        typ = re.sub(r"<[^>]+>", "", cells[3]).strip().upper()
        href = re.search(r'href="([^"]+)"', cells[2], flags=re.I)
        if not href or not href.group(1).lower().endswith((".htm", ".html", ".txt")):
            continue
        if typ in ("EX-99.1", "EX-99.01", "EX-99"):
            best = href.group(1)
            break
        if best is None and typ.startswith("EX-99"):
            best = href.group(1)
    if not best:
        return None
    return "https://www.sec.gov" + best if best.startswith("/") else best


_MDNA_START = {
    "10-Q": r"item\s*2\s*[.:\-–—]?\s*management[’'`s ]*\s*discussion",
    "10-K": r"item\s*7\s*[.:\-–—]?\s*management[’'`s ]*\s*discussion",
}
_MDNA_END = {
    "10-Q": r"item\s*3\s*[.:\-–—]?\s*quantitative|item\s*4\s*[.:\-–—]?\s*controls",
    "10-K": r"item\s*7a\s*[.:\-–—]?\s*quantitative|item\s*8\s*[.:\-–—]?\s*financial\s+statements",
}


def extract_mdna(text: str, form: str) -> str:
    """The MD&A section: the longest span from an Item 2/7 heading to the next item.
    (The first match is usually the table of contents, which yields a tiny span.)"""
    f = "10-K" if form.startswith("10-K") else "10-Q"
    starts = [m.start() for m in re.finditer(_MDNA_START[f], text, flags=re.I)]
    ends = [m.start() for m in re.finditer(_MDNA_END[f], text, flags=re.I)]
    best = ""
    for s in starts:
        e = next((e for e in ends if e > s), None)
        span = text[s:e] if e else text[s:s + 200_000]
        if len(span) > len(best):
            best = span
    return best.strip()


class EdgarDocuments:
    """DocumentSource backed by EDGAR archives."""

    def __init__(self, sec: SecData | None = None):
        self.sec = sec or SecData()

    def earnings_documents(self, symbol: str, cik: int, as_of: date) -> list[Document]:
        filings = recent_filings(self.sec.profile(cik), as_of)
        docs: list[Document] = []
        if filings.empty:
            return docs
        er = filings[(filings["form"] == "8-K") & filings["items"].fillna("").str.contains("2.02", regex=False)]
        if not er.empty:
            r = er.iloc[0]
            url = exhibit_991_url(cik, r["accessionNumber"])
            if url:
                raw = fetch(url, source="edgar", allow_404=True)
                if raw:
                    docs.append(Document(
                        doc_id=f"{symbol}-8K-{r['filingDate']}-ex99", kind="earnings_release",
                        title=f"{symbol} 8-K earnings release (Exhibit 99.1), filed {r['filingDate']}",
                        url=url, filed=r["filingDate"], text=html_to_text(_decode(raw))))
        per = filings[filings["form"].isin(["10-Q", "10-K", "10-Q/A", "10-K/A"]) & ~filings["form"].str.endswith("/A")]
        if not per.empty:
            r = per.iloc[0]
            url = _archive(cik, r["accessionNumber"]) + "/" + r["primaryDocument"]
            raw = fetch(url, source="edgar", allow_404=True)
            if raw:
                mdna = extract_mdna(html_to_text(_decode(raw)), r["form"])
                if mdna:
                    docs.append(Document(
                        doc_id=f"{symbol}-{r['form'].replace('-', '')}-{r['filingDate']}-mdna", kind="mdna",
                        title=f"{symbol} {r['form']} for period {r['reportDate']}, MD&A, filed {r['filingDate']}",
                        url=url, filed=r["filingDate"], text=mdna))
        return docs
