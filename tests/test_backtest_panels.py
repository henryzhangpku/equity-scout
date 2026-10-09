"""Backtests on the committed panels: parity with the live screen, the endpoint, saved site results."""

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scout import llm as llm_mod
from scout.backtest import load_panels, run
from scout.screen import rank, run_screen
from scout.serve import App, HostedConfig, make_handler
from scout.spec import validate

ROOT = Path(__file__).resolve().parents[1]
RUNS = sorted(p.parent for p in (ROOT / "runs").glob("*/run.json"))


@pytest.fixture(scope="module")
def P():
    return load_panels()


def test_panels_span(P):
    assert len(P.dates) >= 24 and P.dates[0] <= "2024-01-31"
    assert P.values.shape[0] == len(P.dates) and P.values.shape[1] == len(P.symbols)


def test_check_slice_matches_live_screen_on_snapshot_date(P):
    """The panel pipeline, run on the snapshot date, gives the same screens as the live snapshot."""
    assert P.check_date == ["2026-10-08"]
    panel = P.frame(0, check=True)
    feats = pd.read_csv(ROOT / "data" / "snapshots" / "2026-10-08" / "features.csv.gz", low_memory=False)
    assert set(panel["symbol"]) == set(feats["symbol"])
    for rd in RUNS:
        spec = validate(json.loads((rd / "run.json").read_text(encoding="utf-8"))["spec"])
        f1, s1 = run_screen(feats, spec)
        f2, s2 = run_screen(panel, spec)
        assert [x["n_pass"] for x in f1] == [x["n_pass"] for x in f2], rd.name
        assert list(rank(s1, spec)["symbol"])[:10] == list(rank(s2, spec)["symbol"])[:10], rd.name


def test_run_on_real_panels_is_well_formed(P):
    spec = validate(json.loads((ROOT / "runs" / "chip-oversold-volume" / "run.json").read_text(encoding="utf-8"))["spec"])
    r = run(spec, P)
    assert r["params"]["n_months"] == len(P.dates) - 1 == len(r["months"]) == len(r["curve"])
    assert r["verdict"] in ("Edge on this history", "No edge", "Not enough data")
    assert {g["id"] for g in r["gates"]} == {"floor", "a", "b", "c", "d", "e"}
    json.dumps(r, allow_nan=False)  # valid JSON for browsers
    for m in r["months"]:
        assert m["n"] <= spec.top_n and abs(m["net"] - (m["gross"] - m["cost"])) < 1e-12


def test_saved_site_backtests_match_engine(P):
    text = (ROOT / "docs" / "data" / "backtests.js").read_text(encoding="utf-8")
    saved = json.loads(text[text.index("=") + 1:].rstrip().rstrip(";"))
    for name in ["c-oversold-volume", "chip-consumer-brands"]:
        spec = validate(json.loads((ROOT / "runs" / name / "run.json").read_text(encoding="utf-8"))["spec"])
        assert saved[name]["verdict"] == run(spec, P)["verdict"]


@pytest.fixture()
def server(tmp_path, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network call")
    monkeypatch.setattr(llm_mod.requests, "post", boom)
    monkeypatch.setattr("scout.http.requests.request", boom)
    app = App(offline=True, cfg=HostedConfig(hosted=True, backtest_per_ip_per_hour=2), live_dir=tmp_path / "live",
              log_stream=open(tmp_path / "log.txt", "w"))
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
    httpd.daemon_threads = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown(); httpd.server_close()


def post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={
        "Content-Type": "application/json", "Origin": "https://henryzhangpku.github.io"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test_backtest_endpoint_and_limit(server):
    spec = json.loads((ROOT / "runs" / "chip-consumer-brands" / "run.json").read_text(encoding="utf-8"))["spec"]
    code, r = post(server + "/api/backtest", {"spec": spec})
    assert code == 200 and r["ok"] and r["verdict"] and len(r["curve"]) == r["params"]["n_months"]
    code, r = post(server + "/api/backtest", {"spec": {"observation": "x", "conditions": [], "rank": []}})
    assert r.get("refused")
    code, _ = post(server + "/api/backtest", {"spec": spec})
    assert code == 200
    code, r = post(server + "/api/backtest", {"spec": spec})
    assert code == 429 and "backtests in the last hour" in r["error"]
    with urllib.request.urlopen(server + "/api/health", timeout=30) as h:
        info = json.loads(h.read())["backtest"]
    assert info["available"] and info["n_rebalances"] >= 24
