"""Hosted mode (SCOUT_HOSTED=1): JSON API, CORS allowlist, caps and limits, kill switch, no leaks."""

import io
import json
import threading
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from scout import llm as llm_mod
from scout.serve import App, Guard, HostedConfig, make_handler

ROOT = Path(__file__).resolve().parents[1]
REC_C = json.loads((ROOT / "runs" / "c-oversold-volume" / "run.json").read_text(encoding="utf-8"))
PAGES = "https://henryzhangpku.github.io"
SENTINELS = ["sk-SENTINEL-deepseek-0001", "PKSENTINELALPACA", "SENTINELSECRETalpaca99"]


def start(tmp_path, monkeypatch, **cfg_kw):
    def boom(*a, **k):
        raise AssertionError("network call in hosted test")
    monkeypatch.setattr(llm_mod.requests, "post", boom)
    monkeypatch.setattr("scout.http.requests.request", boom)
    monkeypatch.setenv("DEEPSEEK_API_KEY", SENTINELS[0])
    monkeypatch.setenv("ALPACA_API_KEY", SENTINELS[1])
    monkeypatch.setenv("ALPACA_API_SECRET", SENTINELS[2])
    cfg = HostedConfig(hosted=True, **cfg_kw)
    logs = io.StringIO()
    app = App(offline=True, cfg=cfg, live_dir=tmp_path / "live", ledger=tmp_path / "picks.jsonl",
              replay_delay=0, log_stream=logs)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(app))
    httpd.daemon_threads = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}", app, logs


@pytest.fixture()
def hosted(tmp_path, monkeypatch):
    httpd, base, app, logs = start(tmp_path, monkeypatch)
    yield base, app, logs
    httpd.shutdown()
    httpd.server_close()


SEEN = []  # every response body, scanned for secrets at the end of each test


def call(method, url, body=None, origin=PAGES, ip="203.0.113.7"):
    headers = {"X-Forwarded-For": f"{ip}, 10.0.0.1"}
    if origin:
        headers["Origin"] = origin
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw, code, hdrs = r.read(), r.status, r.headers
    except urllib.error.HTTPError as e:
        raw, code, hdrs = e.read(), e.code, e.headers
    text = raw.decode("utf-8", "replace")
    SEEN.append(text + str(dict(hdrs)))
    try:
        return code, (json.loads(text) if text else {}), hdrs
    except json.JSONDecodeError:
        return code, {"_raw": text}, hdrs


@pytest.fixture(autouse=True)
def no_secret_in_any_response():
    SEEN.clear()
    yield
    for body in SEEN:
        for s in SENTINELS:
            assert s not in body, "a key leaked into a response"


def poll_until_done(base, job, timeout=60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        code, p, _ = call("GET", f"{base}/api/run/{job}")
        assert code == 200
        if p["done"]:
            return p
        time.sleep(0.2)
    raise AssertionError("job did not finish")


def test_health(hosted):
    base, app, _ = hosted
    code, h, hdrs = call("GET", base + "/api/health")
    assert code == 200 and h["ok"] and h["hosted"] and h["live"] and not h["killed"]
    assert h["as_of"] == "2026-10-08" and h["max_explain"] == 5
    assert h["remaining"] == {"runs_today": 40, "runs_this_hour_for_you": 5}
    assert hdrs.get("Access-Control-Allow-Origin") == PAGES


def test_cors_allowlist(hosted):
    base, _, _ = hosted
    code, _, hdrs = call("OPTIONS", base + "/api/run")
    assert code == 204 and hdrs.get("Access-Control-Allow-Origin") == PAGES
    code, _, hdrs = call("OPTIONS", base + "/api/run", origin="https://evil.example")
    assert code == 403 and hdrs.get("Access-Control-Allow-Origin") is None
    code, _, hdrs = call("GET", base + "/api/health", origin="https://evil.example")
    assert hdrs.get("Access-Control-Allow-Origin") is None
    code, r, _ = call("POST", base + "/api/translate", {"observation": "x"}, origin="https://evil.example")
    assert code == 403
    code, _, hdrs = call("GET", base + "/api/health", origin="http://localhost:8000")
    assert hdrs.get("Access-Control-Allow-Origin") == "http://localhost:8000"


def test_origin_config_from_env(monkeypatch):
    monkeypatch.setenv("SCOUT_HOSTED", "1")
    monkeypatch.setenv("SCOUT_ALLOWED_ORIGINS", "https://a.example, https://b.example/")
    monkeypatch.setenv("SCOUT_DAILY_RUN_CAP", "7")
    monkeypatch.setenv("SCOUT_PER_IP_PER_HOUR", "2")
    monkeypatch.setenv("SCOUT_KILL", "1")
    c = HostedConfig.from_env()
    assert c.hosted and c.kill and c.daily_run_cap == 7 and c.per_ip_per_hour == 2
    assert c.origin_ok("https://b.example") and not c.origin_ok(PAGES) and not c.origin_ok(None)


def test_translate_and_run_with_poll(hosted):
    base, app, logs = hosted
    code, t, _ = call("POST", base + "/api/translate", {"observation": REC_C["observation"]})
    assert code == 200 and t["ok"] and t["spec"] == REC_C["spec"] and isinstance(t["attempts"], int)
    code, r, _ = call("POST", base + "/api/run", {"spec": t["spec"]})
    assert code == 200 and r["ok"]
    assert r["funnel"] == REC_C["funnel"] and r["n_ranked"] == 2 and r["top_n"] == 5
    p = poll_until_done(base, r["job"])
    assert p["error"] is None and p["explanations"] == REC_C["explanations"] and p["pending"] == []
    log = logs.getvalue()
    assert "203.0.113.7" not in log and app.ip_hash("203.0.113.7") in log
    assert all(json.loads(line)["event"] for line in log.strip().splitlines())


def test_explain_capped_at_five(hosted):
    base, _, _ = hosted
    spec = dict(REC_C["spec"], top_n=9)
    code, r, _ = call("POST", base + "/api/run", {"spec": spec})
    assert code == 200 and r["top_n"] == 5  # capped from 9
    spec = json.loads((ROOT / "runs" / "a-midcap-pullback" / "run.json").read_text(encoding="utf-8"))["spec"]
    spec["top_n"] = 9
    code, r, _ = call("POST", base + "/api/run", {"spec": spec}, ip="198.51.100.2")
    assert code == 200 and r["top_n"] == 5 and len(r["ranked"]) <= 25 and r["n_ranked"] == 23
    poll_until_done(base, r["job"])


def test_per_ip_hourly_limit(tmp_path, monkeypatch):
    httpd, base, app, _ = start(tmp_path, monkeypatch, per_ip_per_hour=2)
    try:
        for _ in range(2):
            code, r, _ = call("POST", base + "/api/run", {"spec": REC_C["spec"]})
            assert code == 200
            poll_until_done(base, r["job"])
        code, r, _ = call("POST", base + "/api/run", {"spec": REC_C["spec"]})
        assert code == 429 and r["limited"] and "last hour" in r["error"]
        code, r, _ = call("POST", base + "/api/run", {"spec": REC_C["spec"]}, ip="192.0.2.99")
        assert code == 200
        poll_until_done(base, r["job"])
    finally:
        httpd.shutdown(); httpd.server_close()


def test_daily_cap(tmp_path, monkeypatch):
    httpd, base, app, _ = start(tmp_path, monkeypatch, daily_run_cap=1)
    try:
        code, r, _ = call("POST", base + "/api/run", {"spec": REC_C["spec"]})
        assert code == 200
        poll_until_done(base, r["job"])
        code, r, _ = call("POST", base + "/api/run", {"spec": REC_C["spec"]}, ip="192.0.2.50")
        assert code == 429 and "used up" in r["error"]
        assert call("GET", base + "/api/health")[1]["remaining"]["runs_today"] == 0
    finally:
        httpd.shutdown(); httpd.server_close()


def test_one_concurrent_run_per_ip():
    g = Guard(HostedConfig(hosted=True))
    assert g.check("ipA", "run") is None
    g.active["ipA"] = "job1"
    assert "still running" in g.check("ipA", "run")
    assert g.check("ipB", "run") is None


def test_kill_switch(tmp_path, monkeypatch):
    httpd, base, app, _ = start(tmp_path, monkeypatch, kill=True)
    try:
        h = call("GET", base + "/api/health")[1]
        assert h["killed"] and not h["live"]
        code, r, _ = call("POST", base + "/api/translate", {"observation": REC_C["observation"]})
        assert code == 503 and "paused" in r["error"]
        code, r, _ = call("POST", base + "/api/run", {"spec": REC_C["spec"]})
        assert code == 503 and "paused" in r["error"]
    finally:
        httpd.shutdown(); httpd.server_close()


def test_input_limits_and_disabled_actions(hosted):
    base, _, _ = hosted
    code, r, _ = call("POST", base + "/api/translate", {"observation": "x" * 501})
    assert code == 400 and "500" in r["error"]
    code, r, _ = call("POST", base + "/api/translate", {"observation": "  "})
    assert code == 400
    code, r, _ = call("POST", base + "/api/run", {"spec": {"observation": "x", "conditions": [], "rank": []}})
    assert r["refused"] and not r["ok"]
    code, r, _ = call("POST", base + "/api/record", {"job": "abc"})
    assert code == 403 and "disabled" in r["error"]
    assert call("POST", base + "/api/replay", {"run": "c-oversold-volume"})[0] == 404
    assert call("GET", base + "/api/run/0123456789ab")[0] == 404
    code, r, _ = call("POST", base + "/api/translate", None)
    assert code == 400


def test_upstream_errors_are_generic(hosted, monkeypatch):
    base, app, logs = hosted

    def fail(*a, **k):
        raise RuntimeError(f"upstream 401: invalid key {SENTINELS[0]} at https://api.deepseek.com")
    monkeypatch.setattr("scout.serve.translate", fail)
    code, r, _ = call("POST", base + "/api/translate", {"observation": "anything new"})
    assert code == 502 and r["error"].startswith("The live analysis hit a problem")
    assert SENTINELS[0] not in logs.getvalue()
