"""Pick ledger: append-only hash chain and mark-to-market arithmetic."""

import json

import pandas as pd
import pytest

from scout import track as T


def ledger(tmp_path, n=2):
    p = tmp_path / "picks.jsonl"
    for i in range(n):
        T.append_picks(f"run{i}", "2026-01-02", "obs", [{"symbol": "AAA", "rank": 1, "entry_close": 10.0},
                                                         {"symbol": "BBB", "rank": 2, "entry_close": 20.0}],
                       {"SPY": 100.0, "SMH": 50.0}, path=p)
    return p


def test_chain_intact(tmp_path):
    p = ledger(tmp_path)
    e = T.read_ledger(p)
    assert [x["seq"] for x in e] == [0, 1]
    assert e[0]["prev_hash"] == T.GENESIS and e[1]["prev_hash"] == e[0]["hash"]
    assert T.verify_chain(e) == []


def test_edit_breaks_chain(tmp_path):
    p = ledger(tmp_path)
    lines = p.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["picks"][0]["entry_close"] = 9.0   # quietly improve the entry price
    lines[0] = json.dumps(first)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    problems = T.verify_chain(T.read_ledger(p))
    assert any("entry 0" in x and "hash" in x for x in problems)


def test_deleting_an_entry_breaks_chain(tmp_path):
    p = ledger(tmp_path, n=3)
    lines = p.read_text(encoding="utf-8").splitlines()
    p.write_text(lines[0] + "\n" + lines[2] + "\n", encoding="utf-8")
    assert T.verify_chain(T.read_ledger(p))


def test_refuses_to_append_to_corrupt_ledger(tmp_path):
    p = ledger(tmp_path)
    p.write_text(p.read_text(encoding="utf-8").replace('"run0"', '"runX"'), encoding="utf-8")
    with pytest.raises(RuntimeError, match="corrupt"):
        T.append_picks("run9", "2026-01-02", "obs", [], {}, path=p)


def test_mark_to_market_arithmetic(tmp_path):
    e = T.read_ledger(ledger(tmp_path, n=1))
    closes = pd.DataFrame([
        ("2026-01-02", "AAA", 10.0), ("2026-01-05", "AAA", 11.0), ("2026-01-06", "AAA", 12.0),
        ("2026-01-02", "BBB", 20.0), ("2026-01-05", "BBB", 19.0), ("2026-01-06", "BBB", 18.0),
        ("2026-01-02", "SPY", 100.0), ("2026-01-05", "SPY", 101.0), ("2026-01-06", "SPY", 102.0),
        ("2026-01-02", "SMH", 50.0), ("2026-01-05", "SMH", 50.0), ("2026-01-06", "SMH", 49.0),
        ("2025-12-31", "SPY", 99.0),
    ], columns=["date", "symbol", "close"])
    m = T.mark(e, closes, "2026-01-06")[0]
    assert m["trading_days"] == 2 and m["marked_to"] == "2026-01-06"
    assert [p["return"] for p in m["picks"]] == pytest.approx([0.20, -0.10])
    assert m["basket_return"] == pytest.approx(0.05)          # equal weight (0.20 - 0.10) / 2
    assert m["benchmarks"]["SPY"] == pytest.approx(0.02)
    assert m["basket_vs"]["SPY"] == pytest.approx(0.03)
    assert m["basket_vs"]["SMH"] == pytest.approx(0.05 + 0.02)
