"""scout: plain-English observation -> screen -> ranked names -> cited explanations.

    scout run "<observation>" [--as-of YYYY-MM-DD] [--top 5] [--yes] [--offline] [--provider deepseek|kimi]
    scout spec "<observation>"            translate only, print the validated spec
    scout screen spec.json [--as-of D]    run a spec JSON on a committed snapshot: funnel + ranked names, no model
    scout replay runs/<run>               rerun a recorded run offline and check it reproduces
    scout serve [--offline] [--port 8765] local web app: observation -> spec -> confirm -> live run
    scout track                           mark every recorded pick sheet to market vs SPY and SMH
    scout build --as-of YYYY-MM-DD [--prices alpaca|openbb]   fetch data and build the feature snapshot
    scout site                            export recorded runs for the static site in docs/
    scout loop --proposer scripted|llm --max-steps N   propose, evaluate on a fixed split, correct, record, decide
    scout loop-data                       build data/loop/daily_closes.npz from the cached daily bars
    scout mcp                             MCP server over stdio: the screen as tools for any model (extra: mcp)
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path

from .config import PRICE_SOURCES
from .llm import LLM
from .pipeline import SNAPSHOTS, RecordedDocuments, execute, load_features
from .report import fmt, table_columns
from .spec import SpecError, validate
from .translate import LATEST_PROMPT_VERSION, PROMPT_VERSION, translate


def _latest_snapshot() -> str:
    snaps = sorted(p.name for p in SNAPSHOTS.glob("*") if (p / "features.csv.gz").exists())
    if not snaps:
        sys.exit("no feature snapshot found; run `scout build --as-of YYYY-MM-DD` first")
    return snaps[-1]


def _print_spec(spec) -> None:
    print("\nScreen spec (proposed by the model, validated by code):")
    print(spec.to_json())
    if spec.unmapped:
        print("\nNOT SCREENED (outside the schema):")
        for u in spec.unmapped:
            print(f"  - {u['text']}: {u['reason']}")


def _print_result(rec: dict) -> None:
    print("\nFunnel:")
    w = max(len(s["step"]) for s in rec["funnel"])
    print(f"  {'step'.ljust(w)}  {'in':>6} {'pass':>6} {'fail':>6} {'miss':>6}")
    for s in rec["funnel"]:
        print(f"  {s['step'].ljust(w)}  {s['n_in']:>6} {s['n_pass']:>6} {s['n_fail']:>6} {s['n_missing']:>6}")
    cols = [c for c in table_columns(rec) if c != "name"]
    print(f"\nRanked survivors ({len(rec['ranked'])}), top 15:")
    print("  " + " | ".join(cols))
    for r in rec["ranked"][:15]:
        print("  " + " | ".join(fmt(c, r.get(c)) for c in cols))
    if rec.get("backtest"):
        from .backtest import summary_lines
        print("\nBacktest (monthly, point-in-time, pure code):")
        print("\n".join("  " + x for x in summary_lines(rec["backtest"])))
    print("\nExplanations:")
    for ex in rec["explanations"]:
        print(f"\n  {ex['symbol']}: {ex['verdict']}  ({len(ex['thesis'])} thesis, {len(ex['bear_case'])} bear, "
              f"{len(ex['stripped'])} stripped)")
        for c in ex["thesis"]:
            print(f"    + {c['claim']}\n      \"{c['quote']}\" [{c['doc_id']}]")
        for c in ex["bear_case"]:
            print(f"    - {c['claim']}\n      \"{c['quote']}\" [{c['doc_id']}]")


def cmd_run(a) -> None:
    as_of = a.as_of or _latest_snapshot()
    llm = LLM(provider=a.provider, offline=a.offline)
    _, manifest = load_features(as_of)
    si_ok = manifest.get("short_interest_settlement") is not None
    print(f"as of {as_of}; translating with {llm.provider}/{llm.model} ...")
    try:
        spec, attempts = translate(a.observation, llm, short_interest_available=si_ok,
                                   prompt_version=a.prompt_version)
    except SpecError as e:
        print("Refused: the spec did not validate.")
        for p in e.problems:
            print("  -", p)
        sys.exit(2)
    _print_spec(spec)
    if not a.yes and sys.stdin.isatty():
        if input("\nRun this screen? [Y/n] ").strip().lower() in ("n", "no"):
            sys.exit(0)
    try:
        res = execute(spec, attempts, as_of, llm, top_n=a.top, run_dir=Path(a.out) if a.out else None,
                      record_picks=not a.no_ledger, prompt_version=a.prompt_version, backtest=True)
    except SpecError as e:
        print("Refused:\n  - " + "\n  - ".join(e.problems))
        sys.exit(2)
    _print_result(res.record)
    print(f"\nSaved: {res.run_dir / 'run.json'} and report.md")


def cmd_spec(a) -> None:
    as_of = a.as_of or _latest_snapshot()
    _, manifest = load_features(as_of)
    try:
        spec, _ = translate(a.observation, LLM(provider=a.provider, offline=a.offline),
                            short_interest_available=manifest.get("short_interest_settlement") is not None,
                            prompt_version=a.prompt_version)
    except SpecError as e:
        print("Refused:\n  - " + "\n  - ".join(e.problems))
        sys.exit(2)
    _print_spec(spec)


def replay(run_dir: Path) -> tuple[dict, dict]:
    """Re-execute a recorded run with no network: LLM from llm_cache, documents from
    the run folder, features from the committed snapshot. Returns (old, new)."""
    old = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    llm = LLM(provider=old["llm"]["provider"], model=old["llm"]["model"], offline=True)
    pv = old.get("prompt_version", 1)  # runs recorded before prompt versioning used version 1
    spec, attempts = translate(old["observation"], llm, prompt_version=pv)
    tmp = run_dir.parent / f".replay-{run_dir.name}"
    try:
        new = execute(spec, attempts, old["as_of"], llm, docs_source=RecordedDocuments(run_dir),
                      news_source=None, run_dir=tmp, top_n=old["top_n"], log=lambda *_: None,
                      prompt_version=pv).record
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return old, new


DERIVED_TOP = ("generated_at", "sector_breakdown", "sector_mapping_version")
DERIVED_ROW = ("sector", "industry_group")


def comparable(rec: dict) -> dict:
    """A run record minus timestamps and display-only fields derived from the versioned sector
    mapping (added after some runs were recorded); everything the model saw or code computed stays."""
    out = {k: v for k, v in rec.items() if k not in DERIVED_TOP}
    out["prompt_version"] = rec.get("prompt_version", 1)
    out["ranked"] = [{k: v for k, v in r.items() if k not in DERIVED_ROW} for r in rec.get("ranked", [])]
    return out


def cmd_replay(a) -> None:
    old, new = replay(Path(a.run_dir))
    if comparable(old) == comparable(new):
        print(f"replay identical: spec, funnel, {len(new['ranked'])} ranked rows, "
              f"{len(new['explanations'])} explanations reproduced offline")
    else:
        diff = [k for k in comparable(old) if old.get(k) != new.get(k)]
        print("replay DIFFERS in:", diff)
        sys.exit(1)


def resolve_as_of(text: str) -> str:
    """'today' -> the latest US trading session that has closed (New York time); else the date given."""
    if text != "today":
        return date.fromisoformat(text).isoformat()
    import numpy as np
    import pandas as pd
    now = pd.Timestamp.now(tz="America/New_York")
    d = now.date() if now.hour * 60 + now.minute >= 16 * 60 + 30 else (now - pd.Timedelta(days=1)).date()
    return str(np.busday_offset(np.datetime64(d.isoformat()), 0, roll="backward"))


def cmd_build(a) -> None:
    from . import snapshot
    from .data.openbb_source import SourceUnavailable
    a.as_of = resolve_as_of(a.as_of)
    try:
        p = snapshot.build(date.fromisoformat(a.as_of), prices=getattr(a, "prices", None))
    except SourceUnavailable as e:
        sys.exit(f"scout build: {e}")
    dst = SNAPSHOTS / a.as_of
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy(p, dst / "features.csv.gz")
    shutil.copy(p.parent / "manifest.json", dst / "manifest.json")
    print(f"snapshot -> {dst}")


def cmd_track(a) -> None:
    from .track import track
    r = track()
    if not r["chain_ok"]:
        print("pick ledger chain BROKEN:")
        for x in r["chain_problems"]:
            print("  -", x)
        sys.exit(1)
    print(f"pick ledger: {r['n_entries']} entries, hash chain intact. ({r['label']})")
    for m in r["marks"]:
        b = m["benchmarks"]
        f = lambda v: "n/a" if v is None else f"{v * 100:+.2f}%"
        print()
        print(f"  {m['run_id']}  as of {m['as_of']}, marked to {m['marked_to']} ({m['trading_days']} trading days)")
        print(f"    basket {f(m['basket_return'])}  SPY {f(b['SPY'])}  SMH {f(b['SMH'])}  "
              f"basket-SPY {f(m['basket_vs']['SPY'])}  basket-SMH {f(m['basket_vs']['SMH'])}")
        for p in m["picks"]:
            print(f"    #{p['rank']} {p['symbol']:<6} entry {p['entry_close']:.2f}  {f(p['return'])}")


def cmd_build_panels(a) -> None:
    from .panels import build
    build(start=a.start, as_of=a.as_of or _latest_snapshot())


def cmd_backtest(a) -> None:
    from .backtest import run, summary_lines
    if a.target.endswith(".json") and Path(a.target).is_file() and "run.json" not in a.target:
        d = json.loads(Path(a.target).read_text(encoding="utf-8"))
    else:
        d = json.loads((Path(a.target) / "run.json").read_text(encoding="utf-8"))["spec"]
    spec = validate(d)
    r = run(spec, cost_bps=a.cost_bps, top_n=a.top)
    print(spec.observation)
    print("\n".join(summary_lines(r)))


def cmd_loop(a) -> None:
    from .loop import Lab, default_out, load_data, run_loop, write_run
    from .propose import LLMProposer, Scripted
    if a.max_steps < 1:
        sys.exit("--max-steps must be at least 1")
    lab = Lab(load_data(a.data))
    if a.proposer == "scripted":
        proposer = Scripted()
    else:
        proposer = LLMProposer(LLM(provider=a.provider, offline=a.offline))
    out = Path(a.out) if a.out else default_out(a.proposer)
    out.mkdir(parents=True, exist_ok=True)
    res = run_loop(lab, proposer, a.max_steps, out / "ledger.jsonl", label=out.name)
    s = write_run(res, out)
    for x in s["steps"]:
        t = "n/a" if x["discovery_t"] is None else f"{x['discovery_t']:+.2f}"
        print(f"  {x['step']:>2}. {str(x['id']):<34} discovery t {t:>6}  {x['decision'].upper():<7} {x['reason']}")
    print(f"stopped: {s['stop_reason']}; tried {s['tried']}, promoted {len(s['promoted'])}"
          f"{': ' + ', '.join(s['promoted']) if s['promoted'] else ''}")
    print(f"saved: {out / 'ledger.jsonl'}, report.md, summary.json (chain {'intact' if s['ledger_chain_ok'] else 'BROKEN'})")


def cmd_loop_data(a) -> None:
    from .loop import build_data
    print(f"loop data -> {build_data(Path(a.prices) if a.prices else None)}")


def cmd_serve(a) -> None:
    from .serve import serve
    serve(port=a.port, host=a.host, offline=a.offline, as_of=a.as_of, open_browser=not a.no_browser)


def cmd_screen(a) -> None:
    from .mcp_tools import run_screen_tool
    spec = json.loads(Path(a.spec).read_text(encoding="utf-8"))
    if a.top:
        spec["top_n"] = a.top
    out = run_screen_tool(spec, as_of=a.as_of)
    if not out["ok"]:
        print(f"Refused ({out['refused']}):" + "".join("\n  - " + p for p in out["problems"]))
        sys.exit(2)
    print(f"as of {out['as_of']}")
    w = max(len(s["step"]) for s in out["funnel"])
    print(f"  {'step'.ljust(w)}  {'in':>6} {'pass':>6} {'fail':>6} {'miss':>6}")
    for s in out["funnel"]:
        print(f"  {s['step'].ljust(w)}  {s['entered']:>6} {s['passed']:>6} {s['failed']:>6} {s['no_data']:>6}")
    print(f"\nRanked survivors ({out['survivors']}), top {len(out['top'])}:")
    for r in out["top"]:
        print(f"  {r['rank']:>3}  {r['symbol']:<6} {str(r.get('name', ''))[:40]:<40} score {r['score']:.3f}")


def cmd_mcp(a) -> None:
    from .mcp_server import main as serve_mcp
    serve_mcp()


def cmd_site(a) -> None:
    from .site import export
    export()


def main(argv: list[str] | None = None) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(prog="scout", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("run", "spec"):
        p = sub.add_parser(name)
        p.add_argument("observation")
        p.add_argument("--as-of")
        p.add_argument("--provider", default="deepseek", choices=["deepseek", "kimi"])
        p.add_argument("--offline", action="store_true", help="never call the LLM; use recorded responses only")
        p.add_argument("--prompt-version", type=int, choices=[1, 2, LATEST_PROMPT_VERSION], default=PROMPT_VERSION,
                       help=f"translation prompt version (default {PROMPT_VERSION}; {LATEST_PROMPT_VERSION} adds weekly "
                            "RSI/MACD, MACD crosses and 20-day volume, and needs a snapshot built with those fields)")
        if name == "run":
            p.add_argument("--top", type=int)
            p.add_argument("--yes", action="store_true", help="do not ask before running the spec")
            p.add_argument("--out")
            p.add_argument("--no-ledger", action="store_true", help="do not append the picks to runs/picks.jsonl")
    p = sub.add_parser("screen", help="run a spec JSON file on a committed snapshot (no model, no network)")
    p.add_argument("spec")
    p.add_argument("--as-of")
    p.add_argument("--top", type=int)
    p = sub.add_parser("replay")
    p.add_argument("run_dir")
    p = sub.add_parser("build")
    p.add_argument("--as-of", required=True, help="YYYY-MM-DD, or 'today' for the latest closed session (cron-friendly)")
    p.add_argument("--prices", choices=PRICE_SOURCES, default=None,
                   help="price source: alpaca (default, needs keys) or openbb (optional extra, keyless yfinance); "
                        "default: $SCOUT_PRICES, else alpaca")
    sub.add_parser("site")
    sub.add_parser("track")
    p = sub.add_parser("build-panels", help="point-in-time monthly panels for backtests")
    p.add_argument("--start", default="2023-01-01")
    p.add_argument("--as-of")
    p = sub.add_parser("backtest", help="backtest a recorded run's spec (runs/<run>) or a spec JSON file")
    p.add_argument("target")
    p.add_argument("--cost-bps", type=float, default=10.0)
    p.add_argument("--top", type=int)
    p = sub.add_parser("serve", help="local web app for live demos")
    p.add_argument("--port", type=int, help="default: $PORT, else 8765")
    p.add_argument("--host", help="default: $HOST, else 0.0.0.0 when SCOUT_HOSTED=1, else 127.0.0.1")
    p.add_argument("--offline", action="store_true", help="recorded material only: LLM cache and saved documents")
    p.add_argument("--as-of")
    p.add_argument("--no-browser", action="store_true")
    p = sub.add_parser("loop", help="learning loop: agents propose signals, a fixed evaluator decides")
    p.add_argument("--proposer", choices=["scripted", "llm"], default="scripted")
    p.add_argument("--max-steps", type=int, default=10, help="step budget K, also the Bonferroni divisor")
    p.add_argument("--data", help="daily closes archive (default data/loop/daily_closes.npz)")
    p.add_argument("--out", help="output folder (default runs/loop-<date>[-llm])")
    p.add_argument("--provider", default="deepseek", choices=["deepseek", "kimi"])
    p.add_argument("--offline", action="store_true", help="llm mode: recorded responses only")
    p = sub.add_parser("loop-data", help="build the learning-loop daily closes from the cached bars")
    p.add_argument("--prices", help="long CSV of daily bars (default .cache/panels/prices_long.csv.gz)")
    sub.add_parser("mcp", help="MCP server over stdio (needs the optional 'mcp' extra)")
    a = ap.parse_args(argv)
    {"run": cmd_run, "spec": cmd_spec, "replay": cmd_replay, "build": cmd_build, "site": cmd_site,
     "track": cmd_track, "serve": cmd_serve, "build-panels": cmd_build_panels, "backtest": cmd_backtest,
     "loop": cmd_loop, "loop-data": cmd_loop_data, "mcp": cmd_mcp,
     "screen": cmd_screen}[a.cmd](a)


if __name__ == "__main__":
    main()
