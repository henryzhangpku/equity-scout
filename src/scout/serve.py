"""`scout serve`: the local demo app and, with SCOUT_HOSTED=1, the hosted API behind the static site.

Standard library only (http.server). Routes:

    GET  /                       the app page (src/scout/web/app.html)
    GET  /static/<file>          shared assets from docs/
    GET  /api/health             snapshot date, live/kill state, caps remaining (hosted-safe)
    GET  /api/status             local-app status (key presence, recorded runs, field labels)
    POST /api/translate          {observation} -> validated spec, or the refusals
    POST /api/validate           {spec} -> validated spec, or the refusals
    POST /api/run                {spec} -> {job, funnel, ranked, ...}; explanations continue in the background
    GET  /api/run/<id>           poll: explanations so far, pending names, done/error
    GET  /api/jobs/<id>/events   Server-Sent Events for the same job (local app)
    POST /api/replay             {run} -> {job}; streams a recorded run, no network (local only)
    POST /api/record             {job} -> append picks to the ledger (local only; disabled when hosted)

Hosted mode (SCOUT_HOSTED=1) adds: CORS limited to SCOUT_ALLOWED_ORIGINS, a per-IP hourly
limit, a global daily cap, one concurrent run per IP, an observation length limit, at most 5
names explained, a kill switch (SCOUT_KILL=1), generic error messages (upstream errors and
keys never reach a response), runs kept in a temp dir, and one JSON log line per action with
the client IP hashed. Keys come from the environment only.
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import re
import secrets as pysecrets
import sys
import tempfile
import threading
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .config import ROOT, RUNS, secret
from .data.base import Document
from .llm import LLM, PROVIDERS
from .pipeline import SNAPSHOTS, execute, load_features, slug
from .spec import FIELDS, LABELS, SpecError, validate
from .translate import translate

WEB = Path(__file__).resolve().parent / "web"
STATIC_OK = {"style.css", "ui.js", "favicon.svg", "theme.js"}
LLM_TIMEOUT_S = 180
JOB_TTL_S = 3600
DEFAULT_ORIGINS = ("https://henryzhangpku.github.io", "http://localhost", "http://127.0.0.1", "null")
GENERIC_ERROR = "The live analysis hit a problem. Try again in a minute, or pick one of the one-click examples."


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


@dataclass
class HostedConfig:
    hosted: bool = False
    daily_run_cap: int = 40
    per_ip_per_hour: int = 5
    kill: bool = False
    allowed_origins: tuple = DEFAULT_ORIGINS
    max_observation: int = 500
    max_explain: int = 5

    @classmethod
    def from_env(cls) -> "HostedConfig":
        origins = os.environ.get("SCOUT_ALLOWED_ORIGINS")
        return cls(
            hosted=os.environ.get("SCOUT_HOSTED") == "1",
            daily_run_cap=_env_int("SCOUT_DAILY_RUN_CAP", 40),
            per_ip_per_hour=_env_int("SCOUT_PER_IP_PER_HOUR", 5),
            kill=os.environ.get("SCOUT_KILL") == "1",
            allowed_origins=tuple(o.strip().rstrip("/") for o in origins.split(",") if o.strip()) if origins
            else DEFAULT_ORIGINS,
        )

    def origin_ok(self, origin: str | None) -> bool:
        if not origin:
            return False
        o = origin.rstrip("/")
        for a in self.allowed_origins:
            # "http://localhost" also allows any port on localhost
            if o == a or (a in ("http://localhost", "http://127.0.0.1") and re.fullmatch(re.escape(a) + r"(:\d+)?", o)):
                return True
        return False


class Guard:
    """Rate limits and caps. Translations get 3x the run allowance (they cost one model call)."""

    def __init__(self, cfg: HostedConfig):
        self.cfg = cfg
        self.lock = threading.Lock()
        self.day = None
        self.runs_today = 0
        self.translations_today = 0
        self.ip_runs: dict[str, deque] = defaultdict(deque)
        self.ip_tr: dict[str, deque] = defaultdict(deque)
        self.active: dict[str, str] = {}   # ip_hash -> job id

    def _roll(self) -> None:
        today = datetime.now(timezone.utc).date()
        if today != self.day:
            self.day, self.runs_today, self.translations_today = today, 0, 0

    @staticmethod
    def _recent(q: deque, now: float) -> int:
        while q and now - q[0] > 3600:
            q.popleft()
        return len(q)

    def check(self, ip: str, kind: str) -> str | None:
        """None if allowed (and counted), else a friendly reason."""
        if self.cfg.kill:
            return "Live analysis is paused right now. The one-click examples still work."
        if not self.cfg.hosted:
            return None
        now = time.time()
        with self.lock:
            self._roll()
            if kind == "run":
                if self.runs_today >= self.cfg.daily_run_cap:
                    return "Today's live analyses are used up. The one-click examples still work; live runs reset at midnight UTC."
                if self._recent(self.ip_runs[ip], now) >= self.cfg.per_ip_per_hour:
                    return f"You have run {self.cfg.per_ip_per_hour} live analyses in the last hour. Please try again later."
                if ip in self.active:
                    return "Your previous analysis is still running. Please wait for it to finish."
                self.runs_today += 1
                self.ip_runs[ip].append(now)
            else:
                if self.translations_today >= 3 * self.cfg.daily_run_cap:
                    return "Today's live translations are used up. The one-click examples still work."
                if self._recent(self.ip_tr[ip], now) >= 3 * self.cfg.per_ip_per_hour:
                    return "Too many requests in the last hour. Please try again later."
                self.translations_today += 1
                self.ip_tr[ip].append(now)
        return None

    def remaining(self, ip: str) -> dict:
        now = time.time()
        with self.lock:
            self._roll()
            return {"runs_today": max(0, self.cfg.daily_run_cap - self.runs_today),
                    "runs_this_hour_for_you": max(0, self.cfg.per_ip_per_hour - self._recent(self.ip_runs[ip], now))}


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
    ip: str = ""
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

    def first(self, kinds: tuple, timeout: float):
        deadline = time.time() + timeout
        with self.cond:
            while True:
                for e in self.events:
                    if e["event"] in kinds:
                        return e
                left = deadline - time.time()
                if left <= 0:
                    return None
                self.cond.wait(timeout=left)


@dataclass
class App:
    offline: bool = False
    as_of: str | None = None
    runs_dir: Path = RUNS
    live_dir: Path | None = None
    ledger: Path | None = None
    replay_delay: float = 0.4
    cfg: HostedConfig = field(default_factory=HostedConfig)
    jobs: dict = field(default_factory=dict)
    log_stream: object = None

    def __post_init__(self):
        self.pinned = self.as_of is not None
        self.refresh_snapshot()
        if self.live_dir is None:
            self.live_dir = Path(tempfile.mkdtemp(prefix="scout-runs-")) if self.cfg.hosted else RUNS / "live"
        self.guard = Guard(self.cfg)
        self.salt = os.environ.get("SCOUT_LOG_SALT") or pysecrets.token_hex(16)
        self.log_stream = self.log_stream or sys.stdout

    def refresh_snapshot(self) -> None:
        """Pick up a newer snapshot (e.g. written by `scout build` into SCOUT_DATA_DIR) unless pinned."""
        if not self.pinned:
            snaps = sorted(p.name for p in SNAPSHOTS.glob("*") if (p / "features.csv.gz").exists())
            self.as_of = snaps[-1]
        _, self.manifest = load_features(self.as_of)

    # ---- helpers ----
    def ip_hash(self, ip: str) -> str:
        return hashlib.sha256((self.salt + ip).encode()).hexdigest()[:16]

    def log(self, event: str, **kw) -> None:
        rec = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "event": event, **kw}
        try:
            self.log_stream.write(json.dumps(rec) + "\n")
            self.log_stream.flush()
        except Exception:  # noqa: BLE001 - logging must never break a request
            pass

    def llm(self) -> LLM:
        return LLM(provider="deepseek", offline=self.offline, timeout=LLM_TIMEOUT_S)

    def live_available(self) -> bool:
        return self.offline or bool(secret("DEEPSEEK_API_KEY"))

    def recorded_runs(self) -> list[dict]:
        out = []
        for rj in sorted(self.runs_dir.glob("*/run.json")):
            rec = json.loads(rj.read_text(encoding="utf-8"))
            out.append({"id": rj.parent.name, "observation": rec["observation"], "as_of": rec["as_of"]})
        return out

    def health(self, ip: str) -> dict:
        return {"ok": True, "service": "equity-scout", "hosted": self.cfg.hosted, "as_of": self.as_of,
                "last_price_date": self.manifest.get("last_price_date"), "n_companies": self.manifest.get("n_companies"),
                "live": self.live_available() and not self.cfg.kill, "killed": self.cfg.kill,
                "model": PROVIDERS["deepseek"]["model"], "max_explain": self.cfg.max_explain,
                "max_observation": self.cfg.max_observation, "remaining": self.guard.remaining(ip)}

    def status(self) -> dict:
        return {"as_of": self.as_of, "data": {k: self.manifest.get(k) for k in
                                               ("last_price_date", "universe_rule", "n_companies",
                                                "short_interest_settlement")},
                "offline": self.offline, "hosted": self.cfg.hosted, "model": PROVIDERS["deepseek"]["model"],
                "keys": {"deepseek": bool(secret("DEEPSEEK_API_KEY")),
                         "alpaca": bool(secret("ALPACA_API_KEY") and secret("ALPACA_API_SECRET"))},
                "runs": [] if self.cfg.hosted else self.recorded_runs(),
                "fields": {f.name: {"kind": f.kind, "desc": f.desc, "label": LABELS[f.name]} for f in FIELDS.values()}}

    def si_ok(self) -> bool:
        return self.manifest.get("short_interest_settlement") is not None

    # ---- jobs ----
    def new_job(self, kind: str, ip: str = "") -> Job:
        now = time.time()
        for k in [k for k, j in self.jobs.items() if now - j.started > JOB_TTL_S]:
            self.jobs.pop(k, None)
        j = Job(id=uuid.uuid4().hex[:12], kind=kind, ip=ip)
        self.jobs[j.id] = j
        return j

    def start_run(self, spec_dict: dict, attempts: list | None, ip: str = "local") -> Job:
        spec = validate(spec_dict, short_interest_available=self.si_ok())
        if self.cfg.hosted:
            spec.top_n = min(spec.top_n, self.cfg.max_explain)
        self.refresh_snapshot()
        job = self.new_job("run", ip)
        self.guard.active[ip] = job.id

        def work():
            t0 = time.time()
            try:
                job.emit("status", {"stage": "screening", "message": f"Screening {self.manifest['n_companies']} "
                                    f"companies on the {self.as_of} snapshot"})
                stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                kw = {}
                if not self.offline and not (secret("ALPACA_API_KEY") and secret("ALPACA_API_SECRET")):
                    kw["news_source"] = None
                    job.emit("status", {"stage": "screening", "message": "News is off (no Alpaca keys): explanations "
                                                                         "use SEC filings only"})
                if self.offline:
                    kw = {"docs_source": RecordedLibrary(self.runs_dir), "news_source": None}
                res = execute(spec, attempts or [], self.as_of, self.llm(), log=lambda *_: None,
                              run_dir=self.live_dir / f"{stamp}-{uuid.uuid4().hex[:6]}-{slug(spec.observation)}",
                              on_event=lambda k, p: job.emit(k, p), tolerate_errors=True, **kw)
                job.record = res.record
                rd = res.run_dir
                job.emit("done", {"run_dir": None if self.cfg.hosted else
                                  (str(rd.relative_to(ROOT)) if rd.is_relative_to(ROOT) else str(rd)),
                                  "recordable": not self.cfg.hosted})
                self.log("run_done", ip=ip, job=job.id, n_ranked=len(res.record["ranked"]),
                         explained=sum(e["verdict"] == "explained" for e in res.record["explanations"]),
                         seconds=round(time.time() - t0, 1))
            except Exception as e:  # noqa: BLE001
                self.log("run_error", ip=ip, job=job.id, error=type(e).__name__)
                msg = GENERIC_ERROR if self.cfg.hosted else f"{type(e).__name__}: {str(e)[:300]}"
                job.emit("error", {"message": msg, "hint": "Try an example, or replay a recorded run."})
            finally:
                if self.guard.active.get(ip) == job.id:
                    self.guard.active.pop(ip, None)

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

    def poll(self, job: Job) -> dict:
        with job.cond:
            evs = list(job.events)
        screen = next((e["data"] for e in evs if e["event"] == "screen"), None)
        exs = [e["data"] for e in evs if e["event"] == "explanation"]
        err = next((e["data"] for e in evs if e["event"] == "error"), None)
        cur = [e["data"]["symbol"] for e in evs if e["event"] == "explaining"]
        top = [r["symbol"] for r in (screen or {}).get("ranked", [])[:(screen or {}).get("top_n", 0)]]
        done_syms = {x["symbol"] for x in exs}
        return {"ok": True, "job": job.id, "done": job.done, "error": err, "explanations": exs,
                "pending": [s for s in top if s not in done_syms], "working_on": cur[-1] if cur and not job.done else None,
                "elapsed": round(time.time() - job.started, 1)}

    def record(self, job_id: str) -> dict:
        from . import track
        if self.cfg.hosted:
            raise PermissionError("recording picks is disabled on the hosted service; the ledger is kept locally")
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


def _screen_payload(screen: dict, job: Job, hosted: bool) -> dict:
    ranked = screen["ranked"]
    keep = ranked[:25] if hosted else ranked
    return {"ok": True, "job": job.id, "funnel": screen["funnel"], "ranked": keep, "n_ranked": len(ranked),
            "top_n": screen["top_n"], "as_of": screen["as_of"],
            "last_price_date": (screen.get("data") or {}).get("last_price_date")}


def make_handler(app: App):
    cfg = app.cfg

    class Handler(BaseHTTPRequestHandler):
        server_version = "scout"
        timeout = 60  # seconds to read a request; slow clients cannot hold a thread forever

        def log_message(self, fmt, *args):  # quiet; structured logs go through app.log
            pass

        # ---- plumbing ----
        def client_ip(self) -> str:
            if cfg.hosted:
                fwd = self.headers.get("X-Forwarded-For")
                if fwd:
                    return fwd.split(",")[0].strip()
            return self.client_address[0]

        def cors(self) -> None:
            origin = self.headers.get("Origin")
            if origin and cfg.origin_ok(origin):
                self.send_header("Access-Control-Allow-Origin", origin)
                self.send_header("Vary", "Origin")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.send_header("Access-Control-Max-Age", "600")

        def _json(self, code: int, obj) -> None:
            body = json.dumps(obj, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.cors()
            self.end_headers()
            self.wfile.write(body)

        def _body(self) -> dict:
            n = int(self.headers.get("Content-Length") or 0)
            if n > (64_000 if cfg.hosted else 1_000_000):
                raise ValueError("request too large")
            d = json.loads(self.rfile.read(n) or b"{}")
            if not isinstance(d, dict):
                raise ValueError("request body must be a JSON object")
            return d

        def _file(self, path: Path, ctype: str | None = None) -> None:
            data = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", ctype or mimetypes.guess_type(path.name)[0] or "application/octet-stream")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def origin_blocked(self) -> bool:
            origin = self.headers.get("Origin")
            return cfg.hosted and origin is not None and not cfg.origin_ok(origin)

        # ---- routes ----
        def do_OPTIONS(self):  # noqa: N802 - CORS preflight
            self.send_response(204 if cfg.origin_ok(self.headers.get("Origin")) else 403)
            self.cors()
            self.send_header("Content-Length", "0")
            self.end_headers()

        def do_GET(self):  # noqa: N802
            path = self.path.split("?")[0]
            if path in ("/", "/index.html"):
                return self._file(WEB / "app.html", "text/html; charset=utf-8")
            if path == "/app.js":
                return self._file(WEB / "app.js", "text/javascript; charset=utf-8")
            if path.startswith("/static/") and path[8:] in STATIC_OK:
                return self._file(ROOT / "docs" / path[8:])
            if path == "/api/health":
                return self._json(200, app.health(app.ip_hash(self.client_ip())))
            if path == "/api/status":
                return self._json(200, app.status())
            m = re.fullmatch(r"/api/run/([0-9a-f]{12})", path)
            if m:
                job = app.jobs.get(m.group(1))
                if not job:
                    return self._json(404, {"ok": False, "error": "This analysis has expired. Please run it again."})
                return self._json(200, app.poll(job))
            m = re.fullmatch(r"/api/jobs/([0-9a-f]{12})/events", path)
            if m:
                return self._events(m.group(1))
            self._json(404, {"ok": False, "error": "not found"})

        def do_POST(self):  # noqa: N802
            if self.origin_blocked():
                return self._json(403, {"ok": False, "error": "origin not allowed"})
            try:
                body = self._body()
            except (ValueError, json.JSONDecodeError) as e:
                return self._json(400, {"ok": False, "error": str(e) if not cfg.hosted else "bad request"})
            path = self.path.split("?")[0]
            ip = app.ip_hash(self.client_ip())
            try:
                if path == "/api/translate":
                    obs = str(body.get("observation", "")).strip()
                    if not obs:
                        return self._json(400, {"ok": False, "error": "Write what you are looking for first."})
                    if len(obs) > cfg.max_observation:
                        return self._json(400, {"ok": False, "error": f"Please keep it under {cfg.max_observation} characters."})
                    if not app.live_available():
                        return self._json(503, {"ok": False, "limited": True, "error": "Live analysis is not configured."})
                    why = app.guard.check(ip, "translate")
                    if why:
                        app.log("translate_limited", ip=ip)
                        return self._json(429 if not cfg.kill else 503, {"ok": False, "limited": True, "error": why})
                    t0 = time.time()
                    spec, attempts = translate(obs, app.llm(), short_interest_available=app.si_ok())
                    app.log("translate", ip=ip, chars=len(obs), seconds=round(time.time() - t0, 1),
                            conditions=len(spec.conditions), unmapped=len(spec.unmapped))
                    return self._json(200, {"ok": True, "spec": spec.to_dict(),
                                            "attempts": attempts if not cfg.hosted else len(attempts)})
                if path == "/api/validate":
                    spec = validate(body.get("spec"), short_interest_available=app.si_ok())
                    return self._json(200, {"ok": True, "spec": spec.to_dict()})
                if path == "/api/run":
                    validate(body.get("spec"), short_interest_available=app.si_ok())  # refuse before spending a run
                    if not app.live_available():
                        return self._json(503, {"ok": False, "limited": True, "error": "Live analysis is not configured."})
                    why = app.guard.check(ip, "run")
                    if why:
                        app.log("run_limited", ip=ip)
                        return self._json(429 if not cfg.kill else 503, {"ok": False, "limited": True, "error": why})
                    attempts = body.get("attempts") if not cfg.hosted else None
                    job = app.start_run(body.get("spec"), attempts if isinstance(attempts, list) else None, ip=ip)
                    app.log("run_start", ip=ip, job=job.id)
                    first = job.first(("screen", "error"), timeout=60)
                    if first is None or first["event"] == "error":
                        msg = (first or {}).get("data", {}).get("message", GENERIC_ERROR)
                        return self._json(502, {"ok": False, "error": msg, "job": job.id})
                    return self._json(200, _screen_payload(first["data"], job, cfg.hosted))
                if path == "/api/replay":
                    if cfg.hosted:
                        return self._json(404, {"ok": False, "error": "not available on the hosted service"})
                    job = app.start_replay(str(body.get("run", "")))
                    return self._json(200, {"ok": True, "job": job.id})
                if path == "/api/record":
                    e = app.record(str(body.get("job", "")))
                    return self._json(200, {"ok": True, "seq": e["seq"], "hash": e["hash"], "run_id": e["run_id"]})
            except SpecError as e:
                return self._json(200, {"ok": False, "refused": True, "problems": e.problems})
            except PermissionError as e:
                return self._json(403, {"ok": False, "error": str(e)})
            except FileNotFoundError as e:
                return self._json(404, {"ok": False, "error": str(e)})
            except ValueError as e:
                return self._json(400, {"ok": False, "error": str(e) if not cfg.hosted else "bad request"})
            except Exception as e:  # noqa: BLE001 - surface without leaking upstream detail when hosted
                app.log("error", ip=ip, path=path, error=type(e).__name__)
                if cfg.hosted:
                    return self._json(502, {"ok": False, "error": GENERIC_ERROR})
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
            self.cors()
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
                        self.wfile.write(f"event: {ev['event']}\ndata: {json.dumps(ev, ensure_ascii=False)}\n\n".encode())
                    self.wfile.flush()
                    if finished and sent >= len(job.events):
                        return
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                return

    return Handler


def serve(port: int | None = None, host: str | None = None, offline: bool = False, as_of: str | None = None,
          open_browser: bool = True) -> None:
    cfg = HostedConfig.from_env()
    port = port if port is not None else _env_int("PORT", 8765)
    host = host or os.environ.get("HOST") or ("0.0.0.0" if cfg.hosted else "127.0.0.1")
    app = App(offline=offline, as_of=as_of, cfg=cfg)
    httpd = ThreadingHTTPServer((host, port), make_handler(app))
    httpd.daemon_threads = True
    st = app.status()
    print(f"equity-scout on http://{host}:{httpd.server_address[1]}/  (snapshot {app.as_of}; "
          f"{'hosted' if cfg.hosted else 'local'}; {'OFFLINE: recorded material only' if offline else 'live'}; "
          f"DeepSeek key {'found' if st['keys']['deepseek'] else 'MISSING'}, "
          f"Alpaca keys {'found' if st['keys']['alpaca'] else 'MISSING'}"
          f"{'; KILL switch on' if cfg.kill else ''})", flush=True)
    if open_browser and not cfg.hosted:
        import webbrowser
        threading.Timer(0.5, lambda: webbrowser.open(f"http://127.0.0.1:{httpd.server_address[1]}/")).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
