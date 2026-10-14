"""MCP server: equity-scout as tools for any MCP-capable model (stdio transport).

    scout mcp                     or    python -m scout.mcp_server

The model on top writes the spec; the deterministic validator, screen and ranker in the
middle decide; the data vendor underneath is whatever built the snapshot. The tools only
call existing code paths (scout.mcp_tools) and never ask a model to compute a number.
Works with the official MCP Python SDK 1.x (FastMCP) and 2.x (MCPServer).
Needs the optional extra: `uv sync --extra mcp` (or `pip install "equity-scout[mcp]"`).
"""

from __future__ import annotations

from typing import Any

from . import mcp_tools as t

INSTALL_HINT = ("the MCP server needs the optional 'mcp' extra: run `uv sync --extra mcp` "
                "(or `pip install \"equity-scout[mcp]\"`)")

TOOL_NAMES = ("list_fields", "validate_spec", "run_screen", "explain", "loop_report")


def build_server():
    try:  # mcp 2.x renamed FastMCP to MCPServer; the decorator API is the same
        from mcp.server.mcpserver import MCPServer as Server
    except ImportError:
        try:
            from mcp.server.fastmcp import FastMCP as Server
        except ImportError as e:  # pragma: no cover - exercised only without the extra
            raise SystemExit(INSTALL_HINT) from e

    mcp = Server(
        "equity-scout",
        instructions=(
            "Screen US stocks from a plain-English idea. Call list_fields, write a spec using only those "
            "fields (ratios are decimals: 0.10 = 10%), check it with validate_spec, then run_screen. "
            "Do not compute or adjust numbers yourself; report what the tools return. explain returns "
            "only recorded, quote-verified explanations. This is research on a dated snapshot, not trading."),
    )

    @mcp.tool()
    def list_fields() -> dict[str, Any]:
        """The whitelisted screen fields (name, kind, units, description, whether the latest snapshot
        has it), the allowed operators, universe keys (sectors, industry groups, themes) and the spec
        shape. Read this before writing a spec."""
        return t.list_fields()

    @mcp.tool()
    def validate_spec(spec: dict[str, Any]) -> dict[str, Any]:
        """Check a screen spec against the whitelist. Returns ok=true with the normalised spec, or
        ok=false with every problem and its reason. Fix the problems and call again."""
        return t.validate_spec(spec)

    @mcp.tool()
    def run_screen(spec: dict[str, Any], as_of: str | None = None) -> dict[str, Any]:
        """Run a spec on a committed snapshot (as_of YYYY-MM-DD, default the latest). Returns the
        funnel (per step: entered, passed, failed, no_data), the survivor count, and the top_n ranked
        names with the computed values. Invalid specs and fields the snapshot lacks are refused with
        reasons."""
        return t.run_screen_tool(spec, as_of)

    @mcp.tool()
    def explain(symbol: str, run_id: str | None = None) -> dict[str, Any]:
        """Recorded cited explanation(s) for a ticker: thesis and bear-case claims, each with its
        verbatim-verified quote and source URL. Searches all recorded runs unless run_id is given.
        Never writes new text; says so when nothing is recorded."""
        return t.explain_tool(symbol, run_id)

    @mcp.tool()
    def loop_report(run_id: str = "loop-2026-10-12") -> dict[str, Any]:
        """The recorded learning-loop summary: each hypothesis, its discovery metrics, decision and
        reason, whether out-of-sample was opened, and whether the hash-chained ledger is intact.
        Also available: loop-2026-10-12-llm (proposals written by a model)."""
        return t.loop_report(run_id)

    return mcp


def main() -> None:
    build_server().run(transport="stdio")


if __name__ == "__main__":
    main()
