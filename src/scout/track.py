"""Forward tracking: append-only, hash-chained pick sheets and mark-to-market.

Every live `scout run` appends one entry to runs/picks.jsonl:

    {seq, run_id, as_of, observation, picks: [{symbol, rank, entry_close}],
     benchmarks: {SPY: close, SMH: close}, prev_hash, hash}

`hash` is the SHA-256 of the entry's canonical JSON (without `hash`), and
`prev_hash` is the previous entry's hash, so editing or deleting any past entry
breaks the chain and `verify_chain` reports where.

`scout track` marks each entry to market from fresh Alpaca closes: return since
the as-of close for every pick, the equal-weight basket, SPY and SMH. Both
closes come from the same fetch so dividend adjustments cancel. This is days of
history, not evidence of anything.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .config import RUNS

LEDGER = RUNS / "picks.jsonl"
TRACKING = RUNS / "tracking.json"
BENCH = ["SPY", "SMH"]
GENESIS = "0" * 64


def _canon(d: dict) -> str:
    return json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def entry_hash(e: dict) -> str:
    return hashlib.sha256(_canon({k: v for k, v in e.items() if k != "hash"}).encode()).hexdigest()


def read_ledger(path: Path = LEDGER) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def verify_chain(entries: list[dict]) -> list[str]:
    """Problems found; empty means the chain is intact."""
    problems, prev = [], GENESIS
    for i, e in enumerate(entries):
        if e.get("seq") != i:
            problems.append(f"entry {i}: seq is {e.get('seq')}, expected {i}")
        if e.get("prev_hash") != prev:
            problems.append(f"entry {i}: prev_hash does not match entry {i - 1}")
        if entry_hash(e) != e.get("hash"):
            problems.append(f"entry {i}: content does not match its hash (edited after writing)")
        prev = e.get("hash")
    return problems


def append_picks(run_id: str, as_of: str, observation: str, picks: list[dict], benchmarks: dict,
                 path: Path = LEDGER) -> dict:
    entries = read_ledger(path)
    bad = verify_chain(entries)
    if bad:
        raise RuntimeError("pick ledger is corrupt, refusing to append: " + "; ".join(bad))
    e = {"seq": len(entries), "run_id": run_id, "as_of": as_of, "observation": observation,
         "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
         "picks": picks, "benchmarks": benchmarks,
         "prev_hash": entries[-1]["hash"] if entries else GENESIS}
    e["hash"] = entry_hash(e)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(_canon(e) + "\n")
    return e


def mark(entries: list[dict], closes: pd.DataFrame, today: str) -> list[dict]:
    """closes: long frame date, symbol, close (one consistent adjusted fetch)."""
    piv = closes.pivot_table(index="date", columns="symbol", values="close").sort_index()
    out = []
    for e in entries:
        hist = piv[piv.index >= e["as_of"]]
        if hist.empty or hist.index[0] != e["as_of"]:
            continue
        last = hist.index[-1]
        days = len(hist) - 1

        def ret(sym: str):
            if sym not in hist or not np.isfinite(hist[sym].iloc[0]) or not np.isfinite(hist[sym].iloc[-1]):
                return None
            return float(hist[sym].iloc[-1] / hist[sym].iloc[0] - 1.0)

        rows = [{"symbol": p["symbol"], "rank": p["rank"], "entry_close": p["entry_close"],
                 "return": ret(p["symbol"])} for p in e["picks"]]
        rs = [r["return"] for r in rows if r["return"] is not None]
        basket = float(np.mean(rs)) if rs else None
        b = {s: ret(s) for s in BENCH}
        out.append({"run_id": e["run_id"], "as_of": e["as_of"], "marked_to": str(last), "trading_days": days,
                    "basket_return": basket, "benchmarks": b,
                    "basket_vs": {s: (basket - v if basket is not None and v is not None else None) for s, v in b.items()},
                    "picks": rows})
    return out


def track(today: date | None = None, fetch_closes=None) -> dict:
    """Verify the chain, mark every entry to market and write runs/tracking.json."""
    entries = read_ledger()
    problems = verify_chain(entries)
    today = today or date.today()
    if fetch_closes is None:
        from .data.alpaca import AlpacaPrices

        def fetch_closes(symbols, start, end):
            return AlpacaPrices(f"track {end}").daily_bars(symbols, start, end)
    marks = []
    if entries and not problems:
        syms = sorted({p["symbol"] for e in entries for p in e["picks"]} | set(BENCH))
        start = date.fromisoformat(min(e["as_of"] for e in entries)) - timedelta(days=5)
        closes = fetch_closes(syms, start, today)
        marks = mark(entries, closes, today.isoformat())
    result = {"generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "chain_ok": not problems, "chain_problems": problems, "n_entries": len(entries),
              "label": "since run date; days of history, not evidence", "marks": marks}
    TRACKING.write_text(json.dumps(result, indent=1), encoding="utf-8")
    return result
