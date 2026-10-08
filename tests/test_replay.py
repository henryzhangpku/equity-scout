"""Recorded runs reproduce offline: no network, no API key.

The LLM answers come from llm_cache/, the documents from runs/<run>/docs/, the
features from the committed snapshot in data/snapshots/. A replay must
reproduce the spec, funnel, ranked table and every validated citation exactly.
"""

from pathlib import Path

import pytest

from scout import llm as llm_mod
from scout.cli import comparable, replay
from scout.narrative import check_claim, Claim
from scout.screen import check_funnel

RUNS = sorted(p.parent for p in (Path(__file__).resolve().parents[1] / "runs").glob("*/run.json"))


def test_recorded_runs_exist():
    assert len(RUNS) >= 3


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network call during offline replay")
    monkeypatch.setattr(llm_mod.requests, "post", boom)
    monkeypatch.setattr("scout.http.requests.request", boom)
    monkeypatch.setattr(llm_mod, "secret", lambda name: None)


@pytest.mark.parametrize("run_dir", RUNS, ids=[p.name for p in RUNS])
def test_offline_replay_reproduces_run(run_dir):
    old, new = replay(run_dir)
    assert comparable(new) == comparable(old)


@pytest.mark.parametrize("run_dir", RUNS, ids=[p.name for p in RUNS])
def test_recorded_citations_are_verbatim(run_dir):
    import json
    rec = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    check_funnel(rec["funnel"])
    for ex in rec["explanations"]:
        texts = {d["doc_id"]: (run_dir / "docs" / f"{d['doc_id']}.txt").read_text(encoding="utf-8")
                 for d in ex["documents"]}
        for c in ex["thesis"] + ex["bear_case"]:
            assert check_claim(Claim(c["claim"], c["quote"], c["doc_id"]), texts).ok
        if ex["verdict"] == "explained":
            assert len(ex["thesis"]) >= 2
