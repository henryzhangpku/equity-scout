"""scout: plain-English observation -> screen -> ranked names -> cited explanations.

    scout run "<observation>" [--as-of YYYY-MM-DD] [--top 5] [--yes] [--offline] [--provider deepseek|kimi]
    scout spec "<observation>"            translate only, print the validated spec
    scout replay runs/<run>               rerun a recorded run offline and check it reproduces
    scout track                           mark every recorded pick sheet to market vs SPY and SMH
    scout build --as-of YYYY-MM-DD        fetch data and build the feature snapshot
    scout site                            export recorded runs for the static site in docs/
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path

from .llm import LLM
from .pipeline import SNAPSHOTS, RecordedDocuments, execute, load_features
from .report import fmt, table_columns
from .spec import SpecError, validate
from .translate import translate


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
        spec, attempts = translate(a.observation, llm, short_interest_available=si_ok)
    except SpecError as e:
        print("Refused: the spec did not validate.")
        for p in e.problems:
            print("  -", p)
        sys.exit(2)
    _print_spec(spec)
    if not a.yes and sys.stdin.isatty():
        if input("\nRun this screen? [Y/n] ").strip().lower() in ("n", "no"):
            sys.exit(0)
    res = execute(spec, attempts, as_of, llm, top_n=a.top,
                  run_dir=Path(a.out) if a.out else None, record_picks=not a.no_ledger)
    _print_result(res.record)
    print(f"\nSaved: {res.run_dir / 'run.json'} and report.md")


def cmd_spec(a) -> None:
    as_of = a.as_of or _latest_snapshot()
    _, manifest = load_features(as_of)
    try:
        spec, _ = translate(a.observation, LLM(provider=a.provider, offline=a.offline),
                            short_interest_available=manifest.get("short_interest_settlement") is not None)
    except SpecError as e:
        print("Refused:\n  - " + "\n  - ".join(e.problems))
        sys.exit(2)
    _print_spec(spec)


def replay(run_dir: Path) -> tuple[dict, dict]:
    """Re-execute a recorded run with no network: LLM from llm_cache, documents from
    the run folder, features from the committed snapshot. Returns (old, new)."""
    old = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    llm = LLM(provider=old["llm"]["provider"], model=old["llm"]["model"], offline=True)
    spec, attempts = translate(old["observation"], llm)
    tmp = run_dir.parent / f".replay-{run_dir.name}"
    try:
        new = execute(spec, attempts, old["as_of"], llm, docs_source=RecordedDocuments(run_dir),
                      news_source=None, run_dir=tmp, top_n=old["top_n"], log=lambda *_: None).record
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return old, new


def comparable(rec: dict) -> dict:
    return {k: v for k, v in rec.items() if k not in ("generated_at",)}


def cmd_replay(a) -> None:
    old, new = replay(Path(a.run_dir))
    if comparable(old) == comparable(new):
        print(f"replay identical: spec, funnel, {len(new['ranked'])} ranked rows, "
              f"{len(new['explanations'])} explanations reproduced offline")
    else:
        diff = [k for k in comparable(old) if old.get(k) != new.get(k)]
        print("replay DIFFERS in:", diff)
        sys.exit(1)


def cmd_build(a) -> None:
    from . import snapshot
    p = snapshot.build(date.fromisoformat(a.as_of))
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
        if name == "run":
            p.add_argument("--top", type=int)
            p.add_argument("--yes", action="store_true", help="do not ask before running the spec")
            p.add_argument("--out")
            p.add_argument("--no-ledger", action="store_true", help="do not append the picks to runs/picks.jsonl")
    p = sub.add_parser("replay")
    p.add_argument("run_dir")
    p = sub.add_parser("build")
    p.add_argument("--as-of", required=True)
    sub.add_parser("site")
    sub.add_parser("track")
    a = ap.parse_args(argv)
    {"run": cmd_run, "spec": cmd_spec, "replay": cmd_replay, "build": cmd_build, "site": cmd_site,
     "track": cmd_track}[a.cmd](a)


if __name__ == "__main__":
    main()
