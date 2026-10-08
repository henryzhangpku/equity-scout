"""The browser port (docs/scout-core.js) must agree with the Python screen exactly.

Runs under Node. Checks, for every recorded run:
  * the JS funnel on the shipped browser snapshot equals the recorded funnel,
  * the JS ranking (order and scores) equals the recorded ranking,
  * Python's run_screen/rank on the same browser snapshot agrees too,
and that the JS validator returns the same refusals as spec.validate.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from scout.screen import rank, run_screen
from scout.site import snapshot_frame
from scout.spec import SpecError, validate

ROOT = Path(__file__).resolve().parents[1]
RUNS = sorted(p.parent for p in (ROOT / "runs").glob("*/run.json"))
SNAP_JS = sorted((ROOT / "docs" / "data").glob("snapshot-*.js"))[-1]
NODE = shutil.which("node")


def node(payload: dict) -> dict:
    assert NODE, "Node.js is required for the browser parity tests (https://nodejs.org)"
    r = subprocess.run([NODE, str(ROOT / "tests" / "js" / "run_core.js")], input=json.dumps(payload),
                       capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout)


@pytest.fixture(scope="module")
def recorded():
    return [json.loads((d / "run.json").read_text(encoding="utf-8")) for d in RUNS]


@pytest.fixture(scope="module")
def js_screens(recorded):
    return node({"specs": [r["spec"] for r in recorded], "snapshot": SNAP_JS.name})["screens"]


@pytest.fixture(scope="module")
def browser_frame():
    text = SNAP_JS.read_text(encoding="utf-8")
    payload = json.loads(text[text.index("=") + 1:].rstrip().rstrip(";"))
    return snapshot_frame(payload)


def test_three_recorded_runs_present(recorded):
    assert len(recorded) >= 3


def test_js_funnel_matches_recorded(recorded, js_screens):
    for rec, js in zip(recorded, js_screens):
        assert js["funnel"] == rec["funnel"], rec["observation"]


def test_js_ranking_matches_recorded(recorded, js_screens):
    for rec, js in zip(recorded, js_screens):
        assert [r["symbol"] for r in js["ranked"]] == [r["symbol"] for r in rec["ranked"]]
        for a, b in zip(js["ranked"], rec["ranked"]):
            assert a["rank"] == b["rank"]
            assert a["score"] == pytest.approx(b["score"], abs=1e-12)


def test_python_on_browser_snapshot_matches_js(recorded, js_screens, browser_frame):
    for rec, js in zip(recorded, js_screens):
        spec = validate(rec["spec"])
        funnel, surv = run_screen(browser_frame, spec)
        ranked = rank(surv, spec)
        assert funnel == js["funnel"]
        assert list(ranked["symbol"]) == [r["symbol"] for r in js["ranked"]]


INVALID = [
    {"observation": "x", "conditions": [{"field": "analyst_revisions", "op": ">", "value": 0}],
     "rank": [{"field": "rsi14", "direction": "asc"}]},
    {"observation": "x", "sector_weights": {}, "conditions": [{"field": "rsi14", "op": "!=", "value": 3}], "rank": []},
    {"observation": "x", "universe": {"industries": ["ai_infrastructure"], "themes": ["quantum"], "min_price": -1},
     "conditions": [{"field": "revenue_growth_yoy", "op": ">", "value": 25}],
     "rank": [{"field": "sma50_above_sma200", "direction": "up", "weight": 0}]},
    {"observation": "x", "universe": {"market_cap_min": 2e10, "market_cap_max": 2e9},
     "conditions": [{"field": "close", "op": ">", "ref": "rsi14"}, {"field": "close", "op": ">", "value": 3, "ref": "sma50"},
                    {"field": "sma50_above_sma200", "op": ">", "value": 0}, {"field": "rsi14", "op": "between", "value": [50, 30]},
                    {"field": "rsi14", "op": "<", "value": 130}, {"field": "rsi14", "op": "<", "value": 30, "lookback": 5}],
     "rank": [{"field": "rsi14", "direction": "asc"}], "top_n": 99, "unmapped": ["insider buying"]},
    {"observation": "x", "conditions": [{"field": "short_pct_shares_out", "op": ">", "value": 0.1}],
     "rank": [{"field": "days_to_cover", "direction": "desc"}], "_si": False},
    {"observation": "  ok  ", "universe": {"themes": ["neoclouds"], "market_cap_min": 1e9},
     "conditions": [{"field": "rsi14", "op": "between", "value": [20, 40]},
                    {"field": "sma50_above_sma200", "op": "==", "value": True}],
     "rank": [{"field": "rsi14", "direction": "asc", "weight": 2}],
     "unmapped": [{"text": "insider buying", "reason": "no ownership data"}]},
    "not an object",
]


def test_validator_parity():
    cases = []
    for d in INVALID:
        si = True
        if isinstance(d, dict) and "_si" in d:
            d = {k: v for k, v in d.items() if k != "_si"}
            si = False
        cases.append((d, si))
    js = node({"validate": [{"spec": d, "short_interest_available": si} for d, si in cases]})["validations"]
    for (d, si), j in zip(cases, js):
        try:
            s = validate(d, short_interest_available=si) if isinstance(d, dict) else validate(d)
            assert j["ok"], j
            assert j["spec"] == s.to_dict()
        except SpecError as e:
            assert not j["ok"]
            assert j["problems"] == e.problems


def test_number_formatting_parity():
    from scout.screen import _fmt_value
    cases = [("drawdown_52w", -0.2), ("revenue_growth_yoy", 0.1), ("market_cap", 2e9), ("market_cap", 2e10),
             ("market_cap", 7.5e8), ("avg_dollar_volume_50d", 1234567.0), ("rsi14", 35), ("rsi14", 33.333333),
             ("volume_ratio_50d", 1.5), ("ev_to_sales", 1234567.89), ("ev_to_sales", 0.0001234),
             ("mom_3m", 0.125), ("mom_3m", -0.0049), ("fcf_ttm", 0), ("close", 5)]
    js = node({"format": [list(c) for c in cases]})["formats"]
    assert js == [_fmt_value(f, v) for f, v in cases]
