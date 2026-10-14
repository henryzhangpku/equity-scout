"""MCP tool layer: called directly, no network, no MCP client. The registration test needs the
optional 'mcp' extra and is skipped without it."""

import asyncio
import json

import pytest

from scout import mcp_tools as t
from scout.config import RUNS

RECORDED = json.loads((RUNS / "chip-ai-laggards" / "run.json").read_text(encoding="utf-8"))


def test_list_fields_covers_whitelist_and_flags_snapshot_gaps():
    from scout.spec import FIELDS, MTF_FIELDS
    out = t.list_fields()
    names = {f["name"] for f in out["fields"]}
    assert names == set(FIELDS)
    assert out["latest_snapshot"] == t.snapshots()[-1]
    by = {f["name"]: f for f in out["fields"]}
    assert by["drawdown_52w"]["units"].startswith("decimal ratio")
    assert by["drawdown_52w"]["in_latest_snapshot"] is True
    if out["latest_snapshot"] == "2026-10-08":  # built before the multi-timeframe fields existed
        assert all(by[f]["in_latest_snapshot"] is False for f in MTF_FIELDS)


def test_valid_spec_reproduces_the_recorded_screen():
    assert t.validate_spec(RECORDED["spec"])["ok"] is True
    out = t.run_screen_tool(RECORDED["spec"], as_of=RECORDED["as_of"])
    assert out["ok"] is True
    assert [(f["entered"], f["passed"], f["failed"], f["no_data"]) for f in out["funnel"]] == \
        [(f["n_in"], f["n_pass"], f["n_fail"], f["n_missing"]) for f in RECORDED["funnel"]]
    assert [r["symbol"] for r in out["top"]] == [r["symbol"] for r in RECORDED["ranked"][:RECORDED["spec"]["top_n"]]]
    assert out["top"][0]["revenue_growth_accel"] == pytest.approx(RECORDED["ranked"][0]["revenue_growth_accel"])
    for a, b in zip(out["funnel"], out["funnel"][1:]):
        assert b["entered"] == a["passed"]


def test_invalid_spec_is_refused_with_reasons():
    bad = {"observation": "cheap stocks", "conditions": [{"field": "pe_ratio", "op": "<", "value": 15},
                                                          {"field": "drawdown_52w", "op": "<", "value": -30}],
           "rank": [{"field": "market_cap", "direction": "up"}]}
    v = t.validate_spec(bad)
    assert v["ok"] is False
    joined = " | ".join(v["problems"])
    assert "pe_ratio" in joined and "looks like a percent" in joined and "direction" in joined
    r = t.run_screen_tool(bad)
    assert r["ok"] is False and r["refused"] == "invalid spec" and r["problems"] == v["problems"]


def test_field_missing_from_snapshot_is_refused():
    from scout.spec import MTF_FIELDS
    as_of = t.snapshots()[-1]
    cols = t._snapshot_columns(as_of)
    absent = [f for f in MTF_FIELDS if f not in cols and f in ("rsi14_w", "macd_hist_w")]
    if not absent:
        pytest.skip("latest snapshot already has the multi-timeframe fields")
    spec = {"observation": "weekly oversold", "conditions": [{"field": absent[0], "op": "<", "value": 30}],
            "rank": [{"field": "rsi14", "direction": "asc"}]}
    r = t.run_screen_tool(spec)
    assert r["ok"] is False and r["refused"] == "field not in snapshot"
    assert absent[0] in r["problems"][0]


def test_unknown_snapshot_date_is_refused():
    r = t.run_screen_tool(RECORDED["spec"], as_of="1999-01-01")
    assert r["ok"] is False and "available" in r["problems"][0]


def test_explain_returns_recorded_verified_claims_only():
    ex = next(e for e in RECORDED["explanations"] if e["verdict"] == "explained")
    out = t.explain_tool(ex["symbol"].lower(), run_id="chip-ai-laggards")
    assert out["ok"] is True and len(out["explanations"]) == 1
    got = out["explanations"][0]
    assert got["verdict"] == "explained"
    assert [c["quote"] for c in got["thesis"]] == [c["quote"] for c in ex["thesis"] if c["ok"]]
    assert all(c["url"].startswith("http") for c in got["thesis"] + got["bear_case"])


def test_explain_without_a_recording_says_so():
    out = t.explain_tool("ZZZZ")
    assert out["ok"] is False and out["explanations"] == []
    assert "no recorded explanation" in out["problems"][0]
    assert t.explain_tool("AVGO", run_id="../../etc")["ok"] is False


def test_loop_report_matches_the_recorded_summary():
    out = t.loop_report()
    s = json.loads((RUNS / "loop-2026-10-12" / "summary.json").read_text(encoding="utf-8"))
    assert out["ok"] is True and out["ledger_chain_intact"] is True
    assert out["tried"] == s["tried"] and out["promoted"] == s["promoted"]
    assert [x["decision"] for x in out["steps"]] == [x["decision"] for x in s["steps"]]
    assert all(x["hypothesis"] for x in out["steps"])
    assert all(x["out_of_sample_opened"] is False for x in out["steps"]) == (not s["oos_opened"])
    assert t.loop_report("nope")["ok"] is False


def test_server_registers_exactly_these_tools():
    pytest.importorskip("mcp")
    from scout.mcp_server import TOOL_NAMES, build_server
    server = build_server()
    tools = asyncio.run(server.list_tools())
    assert sorted(x.name for x in tools) == sorted(TOOL_NAMES)
    assert all(x.description for x in tools)
