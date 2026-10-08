"""Polite, cached HTTP for public data sources.

Every raw response body is stored under .cache/raw/<source>/<sha256(key)>.<ext>
so a rerun never re-downloads, and a manifest row (url, key, bytes, sha256,
fetched_at) is appended for auditability. Auth headers are passed separately and
never written to the cache key, the manifest or logs.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from .config import CACHE, SEC_USER_AGENT

_lock = threading.Lock()
_last_call: dict[str, float] = {}

# minimum seconds between calls per host
_MIN_INTERVAL = {
    "data.sec.gov": 0.125,  # SEC fair-access: < 10 requests/second
    "www.sec.gov": 0.125,
    "api.finra.org": 0.1,
    "data.alpaca.markets": 0.31,  # 200 req/min on the free data plan
    "api.alpaca.markets": 0.31,
}


def _throttle(host: str) -> None:
    gap = _MIN_INTERVAL.get(host, 0.2)
    with _lock:
        now = time.monotonic()
        wait = _last_call.get(host, 0.0) + gap - now
        if wait > 0:
            time.sleep(wait)
        _last_call[host] = time.monotonic()


def _manifest(source: str, row: dict) -> None:
    p = CACHE / "manifest.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    with _lock, p.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"source": source, **row}) + "\n")


def cache_path(source: str, key: str, ext: str = "json.gz") -> Path:
    h = hashlib.sha256(key.encode()).hexdigest()[:32]
    return CACHE / "raw" / source / f"{h}.{ext}"


def fetch(
    url: str,
    *,
    source: str,
    params: dict | None = None,
    headers: dict | None = None,
    method: str = "GET",
    json_body: dict | None = None,
    cache_key: str | None = None,
    refresh: bool = False,
    retries: int = 4,
    allow_404: bool = False,
) -> bytes | None:
    """Fetch bytes with disk cache. Returns None on 404 when allow_404."""
    key = cache_key or (method + " " + url + " " + json.dumps(params or {}, sort_keys=True)
                        + " " + json.dumps(json_body or {}, sort_keys=True))
    path = cache_path(source, key)
    miss = path.with_suffix(".404")
    if not refresh:
        if path.exists():
            return gzip.decompress(path.read_bytes())
        if allow_404 and miss.exists():
            return None
    hdrs = {"User-Agent": SEC_USER_AGENT, "Accept-Encoding": "gzip, deflate"}
    hdrs.update(headers or {})
    host = url.split("/")[2]
    err: Exception | None = None
    for attempt in range(retries):
        _throttle(host)
        try:
            r = requests.request(method, url, params=params, headers=hdrs, json=json_body, timeout=90)
        except requests.RequestException as e:  # network blip: back off and retry
            err = e
            time.sleep(2 ** attempt)
            continue
        if r.status_code == 404 and allow_404:
            miss.parent.mkdir(parents=True, exist_ok=True)
            miss.write_text(url)
            return None
        if r.status_code in (429, 500, 502, 503, 504):
            err = RuntimeError(f"HTTP {r.status_code} for {url}")
            time.sleep(2 ** (attempt + 1))
            continue
        if r.status_code == 204:
            r._content = b""
        elif r.status_code != 200:
            raise RuntimeError(f"HTTP {r.status_code} for {url}: {r.text[:200]}")
        body = r.content
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(gzip.compress(body, compresslevel=6))
        _manifest(source, {
            "url": url, "key_sha": path.stem.split(".")[0], "bytes": len(body),
            "sha256": hashlib.sha256(body).hexdigest(),
            "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })
        return body
    raise RuntimeError(f"giving up on {url}: {err}")


def fetch_json(url: str, **kw):
    b = fetch(url, **kw)
    return None if b is None else json.loads(b)
