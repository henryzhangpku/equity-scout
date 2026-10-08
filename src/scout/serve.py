"""`scout serve`: a local web app for live demos (standard library only).

    GET  /                       the app page (src/scout/web/app.html)
    GET  /static/<file>          shared assets from docs/ (style.css, ui.js, favicon.svg)
    GET  /api/status             snapshot date, which keys are present, recorded runs
    POST /api/translate          {observation} -> validated spec, or the refusals
    POST /api/validate           {spec} -> validated spec, or the refusals
    POST /api/run                {spec} -> {job}; the pipeline runs in a background thread
    POST /api/replay             {run} -> {job}; streams a recorded run, no network
    GET  /api/jobs/<id>/events   Server-Sent Events: status, screen, explaining, explanation, done, error
    POST /api/record             {job} -> appends that run's top names to the pick ledger (only on request)

Keys come from the environment exactly as for the CLI and never reach the page.
--offline answers only from recorded material: the LLM cache, documents saved
with the recorded runs, no news fetch. That is also the fallback when the
network or the model fails during a demo.
"""

from __future__ import annotations

import json
import mimetypes
import re
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .config import ROOT, RUNS, secret
from .data.base import Document
from .llm import LLM, PROVIDERS
from .pipeline import SNAPSHOTS, execute, load_features, slug
from .spec import FIELDS, SpecError, validate
from .translate import translate

WEB = Path(__file__).resolve().parent / "web"
STATIC_OK = {"style.css", "ui.js", "favicon.svg"}
LLM_TIMEOUT_S = 180


class RecordedLibrary:
    """DocumentSource for --offline: the documents saved with any recorded run, by symbol."""

    def __init__(self, runs_dir: Path):
        self.docs: dict[str, list[tuple[Path, dict]]] = {}
        for rj in sorted(runs_dir.glob("*/run.json")):
            rec = json.loads(rj.read_text(encoding="utf-8"))
            for ex in rec["explanations"]:
                self.docs.setdefault(ex["symbol"], [(rj.parent, m) for m in ex["documents"]])

    def earnings_documents(self, symbol: str, cik: int, as_of: date) -> list[Document]:
        out = []
        for run_dir, m in self.docs.get(symbol, []):
            text = (run_dir / "docs" / f"{m['doc_id']}.txt").read_text(encoding="utf-8")
            out.append(Document(doc_id=m["doc_id"], kind=m["kind"], title=m["title"], url=m["url"],
                                filed=m["filed"], text=text, full_length=m["chars_total"]))
        return out


@dataclass
class Job:
    id: str
    kind: str
    events: list = field(default_factory=list)
    done: bool = False
    record: dict | None = None
    recorded_entry: dict | None = None
    cond: threading.Condition = field(default_factory=threading.Condition)
    started: float = field(default_factory=time.time)

    def emit(self, kind: str, payload) -> None:
        with self.cond:
            self.events.append({"event": kind, "data": payload, "t": round(time.time() - self.started, 1)})
            if kind in ("done", "error"):
                self.done = True
            self.cond.notify_all()


@dataclass
class App:
    offline: bool = False
    as_of: str | None = None
    runs_dir: Path = RUNS
    live_dir: Path = RUNS / "live"
    ledger: Path | None = None
    replay_delay: float = 0.4
    jobs: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.as_of:
            snaps = sorted(p.name for p in SNAPSHOTS.glob("*") if (p / "features.csv.gz").exists())
            self.as_of = snaps[-1]
        _, self.manifest = load_features(self.as_of)

    def llm(self) -> LLM:
        return LLM(provider="deepseek", offline=self.offline, timeout=LLM_TIMEOUT_S)

    def recorded_runs(self) -> list[dict]:
        out = []
        for rj in sorted(self.runs_dir.glob("*/run.json")):
            rec = json.loads(rj.read_text(encoding="utf-8"))
            out.append({"id": rj.parent.name, "observation": rec["observation"], "as_of": rec["as_of"]})
        return out

    def status(self) -> dict:
        return {"as_of": self.as_of, "data": {k: self.manifest.get(k) for k in
                                               ("last_price_date", "universe_rule", "n_companies",
                                                "short_interest_settlement")},
                "offline": self.offline, "model": PROVIDERS["deepseek"]["model"],
                "keys": {"deepseek": bool(secret("DEEPSEEK_API_KEY")),
                         "alpaca": bool(secret("ALPACA_API_KEY") and secret("ALPACA_API_SECRET"))},
                "runs": self.recorded_runs(),
                "fields": {f.name: {"kind": f.kind, "desc": f.desc} for f in FIELDS.values()}}

    def si_ok(self) -> bool:
        return self.manifest.get("short_interest_settlement") is not None

    # ---- jobs ----
    def new_job(self, kind: str) -> Job:
        j = Job(id=uuid.uuid4().hex[:12], kind=kind)
        self.jobs[j.id] = j
        return j

    def start_run(self, spec_dict: dict, attempts: list | None) -> Job:
        spec = validate(spec_dict, short_interest_available=self.si_ok())
        job = self.new_job("run")

        def work():
            try:
                job.emit("status", {"stage": "screening", "message": f"Screening {self.manifest['n_companies']} "
                                    f"companies on the {self.as_of} snapshot"})
                stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                kw = {}
                if not self.offline and not (secret("ALPACA_API_KEY") and secret("ALPACA_API_SECRET")):
                    kw["news_source"] = None
                    job.emit("status", {"stage": "screening", "message": "Alpaca keys missing: explanations will use "
                                                                         "SEC filings only, no news"})
                if self.offline:
                    kw = {"docs_source": RecordedLibrary(self.runs_dir), "news_source": None}
                res = execute(spec, attempts or [], self.as_of, self.llm(), log=lambda *_: None,
                              run_dir=self.live_dir / f"{stamp}-{slug(spec.observation)}",
                              on_event=lambda k, p: job.emit(k, p), tolerate_errors=True, **kw)
                job.record = res.record
                job.emit("done", {"run_dir": str(res.run_dir.relative_to(ROOT)) if res.run_dir.is_relative_to(ROOT)
                                  else str(res.run_dir), "recordable": True})
            except Exception as e:  # noqa: BLE001
                job.emit("error", {"message": f"{type(e).__name__}: {str(e)[:300]}",
                                   "hint": "Try 'Replay a recorded run', or start with --offline."})

        threading.Thread(target=work, daemon=True).start()
        return job

    def start_replay(self, run_id: str) -> Job:
        p = self.runs_dir / run_id / "run.json"
        if not re.fullmatch(r"[a-z0-9-]+", run_id or "") or not p.exists():
            raise FileNotFoundError(f"no recorded run '{run_id}'")
        rec = json.loads(p.read_text(encoding="utf-8"))
        job = self.new_job("replay")

        def work():
            job.emit("status", {"stage": "replay", "message": f"Replaying recorded run {run_id} (as of {rec['as_of']}); "
                                                             "no network, nothing recomputed"})
            job.emit("spec", rec["spec"])
            time.sleep(self.replay_delay)
            job.emit("screen", {"funnel": rec["funnel"], "ranked": rec["ranked"], "top_n": rec["top_n"],
                                "as_of": rec["as_of"], "data": rec["data"]})
            for i, ex in enumerate(rec["explanations"]):
                job.emit("explaining", {"symbol": ex["symbol"], "i": i + 1, "n": len(rec["explanations"])})
                time.sleep(self.replay_delay)
                job.emit("explanation", ex)
            job.emit("done", {"run_dir": f"runs/{run_id}", "recordable": False})

        threading.Thread(target=work, daemon=True).start()
        return job

    def record(self, job_id: str) -> dict:
        from . import track
        job = self.jobs.get(job_id)
        if not job or job.kind != "run" or not job.done or not job.record:
            raise ValueError("only a finished live run can be recorded")
        if job.recorded_entry:
            return job.recorded_entry
        rec = job.record
        picks = [{"symbol": r["symbol"], "rank": r["rank"], "entry_close": r["close"]} for r in rec["ranked"][:rec["top_n"]]]
        bench = {k: v for k, v in (rec["data"].get("benchmark_closes") or {}).items() if k in ("SPY", "SMH")}
        kw = {"path": self.ledger} if self.ledger else {}
        run_id = "live-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + "-" + slug(rec["observation"], 4)
        job.recorded_entry = track.append_picks(run_id, rec["as_of"], rec["observation"], picks, bench, **kw)
        return job.recorded_entry


def make_handler(app: App):
    class Handler(BaseHTTPRequestHandler):
        server_version = "scout"

        def log_message(self, fmt, *args):  # keep the demo terminal quiet; never logs bodies
            pass

        def _json(self, code: int, obj) -> None:
            body = json.dumps(obj, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _body(self) -> dict:
            n = int(self.headers.get("Content-Length") or 0)
            if n > 1_000_000:
                raise ValueError("request too large")
            return json.loads(self.rfile.read(n) or b"{}")

        def _file(self, path: Path, ctype: str | None = None) -> None:
            data = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", ctype or mimetypes.guess_type(path.name)[0] or "application/octet-stream")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):  # noqa: N802
            path = self.path.split("?")[0]
            if path in ("/", "/index.html"):
                return self._file(WEB / "app.html", "text/html; charset=utf-8")
            if path == "/app.js":
                return self._file(WEB / "app.js", "text/javascript; charset=utf-8")
            if path.startswith("/static/") and path[8:] in STATIC_OK:
                return self._file(ROOT / "docs" / path[8:])
            if path == "/api/status":
                return self._json(200, app.status())
            m = re.fullmatch(r"/api/jobs/([0-9a-f]{12})/events", path)
            if m:
                return self._events(m.group(1))
            self._json(404, {"error": "not found"})

        def do_POST(self):  # noqa: N802
            try:
                body = self._body()
            except (ValueError, json.JSONDecodeError) as e:
                return self._json(400, {"ok": False, "error": str(e)})
            path = self.path.split("?")[0]
            try:
                if path == "/api/translate":
                    obs = str(body.get("observation", "")).strip()
                    if not obs:
                        return self._json(400, {"ok": False, "error": "write an observation first"})
                    spec, attempts = translate(obs, app.llm(), short_interest_available=app.si_ok())
                    return self._json(200, {"ok": True, "spec": spec.to_dict(), "attempts": attempts})
                if path == "/api/validate":
                    spec = validate(body.get("spec"), short_interest_available=app.si_ok())
                    return self._json(200, {"ok": True, "spec": spec.to_dict()})
                if path == "/api/run":
                    job = app.start_run(body.get("spec"), body.get("attempts"))
                    return self._json(200, {"ok": True, "job": job.id})
                if path == "/api/replay":
                    job = app.start_replay(str(body.get("run", "")))
                    return self._json(200, {"ok": True, "job": job.id})
                if path == "/api/record":
                    e = app.record(str(body.get("job", "")))
                    return self._json(200, {"ok": True, "seq": e["seq"], "hash": e["hash"], "run_id": e["run_id"]})
            except SpecError as e:
                return self._json(200, {"ok": False, "refused": True, "problems": e.problems})
            except FileNotFoundError as e:
                return self._json(404, {"ok": False, "error": str(e)})
            except ValueError as e:
                return self._json(400, {"ok": False, "error": str(e)})
            except Exception as e:  # noqa: BLE001 - surface, do not crash the demo
                return self._json(502, {"ok": False, "error": f"{type(e).__name__}: {str(e)[:300]}",
                                        "hint": "The model or network failed. Edit the spec by hand, "
                                                "or replay a recorded run."})
            self._json(404, {"ok": False, "error": "not found"})

        def _events(self, job_id: str) -> None:
            job = app.jobs.get(job_id)
            if not job:
                return self._json(404, {"error": "no such job"})
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "close")
            self.end_headers()
            sent = 0
            try:
                while True:
                    with job.cond:
                        if sent >= len(job.events) and not job.done:
                            job.cond.wait(timeout=10)
                        batch = job.events[sent:]
                        finished = job.done
                    if not batch and not finished:  # heartbeat so the page can show elapsed time
                        batch = [{"event": "heartbeat", "data": {}, "t": round(time.time() - job.started, 1)}]
                    else:
                        sent += len(batch)
                    for ev in batch:
                        self.wfile.write(f"event: {ev['event']}\ndata: {json.dumps({**ev}, ensure_ascii=False)}\n\n"
                                         .encode())
                    self.wfile.flush()
                    if finished and sent >= len(job.events):
                        return
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                return

    return Handler


def serve(port: int = 8765, offline: bool = False, as_of: str | None = None, open_browser: bool = True) -> None:
    app = App(offline=offline, as_of=as_of)
    httpd = ThreadingHTTPServer(("127.0.0.1", port), make_handler(app))
    httpd.daemon_threads = True
    url = f"http://127.0.0.1:{httpd.server_address[1]}/"
    st = app.status()
    print(f"equity-scout local app on {url}  (snapshot {app.as_of}; "
          f"{'OFFLINE: recorded material only' if offline else 'live'}; "
          f"DeepSeek key {'found' if st['keys']['deepseek'] else 'MISSING'}, "
          f"Alpaca keys {'found' if st['keys']['alpaca'] else 'MISSING'})")
    print("Ctrl+C to stop.")
    if open_browser:
        import webbrowser
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
