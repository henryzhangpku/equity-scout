"""scout serve endpoints, offline: recorded LLM cache, saved documents, network disabled."""

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from scout import llm as llm_mod
from scout import track
from scout.serve import App, make_handler

ROOT = Path(__file__).resolve().parents[1]
REC_C = json.loads((ROOT / "runs" / "c-oversold-volume" / "run.json").read_text(encoding="utf-8"))


@pytest.fixture()
def server(tmp_path, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("network call during offline serve test")
    monkeypatch.setattr(llm_mod.requests, "post", boom)
    monkeypatch.setattr("scout.http.requests.request", boom)
    monkeypatch.setattr(llm_mod, "secret", lambda name: None)
    monkeypatch.setattr("scout.serve.secret", lambda name: None)
    app = App(offline=True, live_dir=tmp_path / "live", ledger=tmp_path / "picks.jsonl", replay_delay=0)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
    httpd.daemon_threads = True
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}", app
    httpd.shutdown()
    httpd.server_close()


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.status, r.headers.get("Content-Type"), r.read()


def post(url, body):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def events(base, job):
    out = []
    with urllib.request.urlopen(f"{base}/api/jobs/{job}/events", timeout=60) as r:
        assert r.headers.get("Content-Type").startswith("text/event-stream")
        for raw in r:
            line = raw.decode().strip()
            if line.startswith("data: "):
                ev = json.loads(line[6:])
                out.append(ev)
                if ev["event"] in ("done", "error"):
                    break
    return out


def test_page_and_static(server):
    base, _ = server
    code, ctype, body = get(base + "/")
    assert code == 200 and ctype.startswith("text/html") and b"Propose a screen spec" in body
    assert get(base + "/static/ui.js")[0] == 200
    with pytest.raises(urllib.error.HTTPError):
        get(base + "/static/../pyproject.toml")


def test_status(server):
    base, app = server
    s = json.loads(get(base + "/api/status")[2])
    assert s["as_of"] == "2026-10-08" and s["offline"] is True
    assert s["keys"] == {"deepseek": False, "alpaca": False}
    assert {r["id"] for r in s["runs"]} >= {"a-midcap-pullback", "b-ai-infra-laggards", "c-oversold-volume"}
    assert "rsi14" in s["fields"]


def test_translate_from_recorded_cache(server):
    base, _ = server
    code, r = post(base + "/api/translate", {"observation": REC_C["observation"]})
    assert code == 200 and r["ok"]
    assert r["spec"] == REC_C["spec"]


def test_translate_cache_miss_is_a_clean_error(server):
    base, _ = server
    code, r = post(base + "/api/translate", {"observation": "an observation nobody recorded"})
    assert code == 502 and not r["ok"] and "ReplayMiss" in r["error"] and "replay" in r["hint"]


def test_validate_refusal(server):
    base, _ = server
    code, r = post(base + "/api/validate", {"spec": {"observation": "x", "conditions": [{"field": "nope", "op": ">", "value": 1}],
                                                     "rank": [{"field": "rsi14", "direction": "asc"}]}})
    assert code == 200 and r["refused"] and "unknown field 'nope'" in r["problems"][0]


def test_run_streams_and_matches_recorded(server):
    base, app = server
    code, r = post(base + "/api/run", {"spec": REC_C["spec"], "attempts": REC_C["translation_attempts"]})
    assert code == 200 and r["ok"]
    evs = events(base, r["job"])
    kinds = [e["event"] for e in evs]
    assert kinds[-1] == "done", evs[-1]
    screen = next(e["data"] for e in evs if e["event"] == "screen")
    assert screen["funnel"] == REC_C["funnel"]
    assert [x["symbol"] for x in screen["ranked"]] == [x["symbol"] for x in REC_C["ranked"]]
    exs = [e["data"] for e in evs if e["event"] == "explanation"]
    assert exs == REC_C["explanations"]
    assert kinds.index("screen") < kinds.index("explanation")

    # nothing is recorded until asked
    assert not app.ledger.exists()
    code, rec = post(base + "/api/record", {"job": r["job"]})
    assert code == 200 and rec["seq"] == 0
    entries = track.read_ledger(app.ledger)
    assert track.verify_chain(entries) == []
    assert [p["symbol"] for p in entries[0]["picks"]] == ["BX", "SBUX"]
    # recording twice does not append twice
    post(base + "/api/record", {"job": r["job"]})
    assert len(track.read_ledger(app.ledger)) == 1


def test_run_refuses_invalid_spec(server):
    base, _ = server
    code, r = post(base + "/api/run", {"spec": {"observation": "x", "conditions": [], "rank": []}})
    assert code == 200 and r["refused"] and not r["ok"]


def test_replay_and_replay_not_recordable(server):
    base, app = server
    code, r = post(base + "/api/replay", {"run": "b-ai-infra-laggards"})
    assert code == 200
    evs = events(base, r["job"])
    rec = json.loads((ROOT / "runs" / "b-ai-infra-laggards" / "run.json").read_text(encoding="utf-8"))
    assert next(e["data"] for e in evs if e["event"] == "screen")["funnel"] == rec["funnel"]
    assert [e["data"]["symbol"] for e in evs if e["event"] == "explanation"] == ["AVGO", "AAOI", "AMAT", "COHR", "AMKR"]
    assert evs[-1]["data"]["recordable"] is False
    code, rr = post(base + "/api/record", {"job": r["job"]})
    assert code == 400 and not app.ledger.exists()
    assert post(base + "/api/replay", {"run": "../etc"})[0] == 404


def test_unknown_job_and_route(server):
    base, _ = server
    with pytest.raises(urllib.error.HTTPError):
        get(base + "/api/jobs/000000000000/events")
    assert post(base + "/api/nope", {})[0] == 404
