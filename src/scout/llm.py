"""Pluggable LLM client with a committed record/replay cache.

Every request (provider, model, messages, params) is hashed; the full prompt and
response are written to llm_cache/<hash>.json. On replay the cached response is
returned without a network call, so recorded runs reproduce offline with no key.

Providers speak the OpenAI-compatible chat-completions protocol:
    deepseek  https://api.deepseek.com           DEEPSEEK_API_KEY   (default)
    kimi      https://api.kimi.com/coding/v1     KIMI_API_KEY       (alternative)
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import requests

from .config import LLM_CACHE, secret

PROVIDERS = {
    "deepseek": {"base": "https://api.deepseek.com", "key": "DEEPSEEK_API_KEY", "model": "deepseek-v4-pro"},
    "kimi": {"base": "https://api.kimi.com/coding/v1", "key": "KIMI_API_KEY", "model": "kimi-for-coding"},
}


class ReplayMiss(RuntimeError):
    pass


@dataclass
class LLM:
    provider: str = os.environ.get("SCOUT_LLM", "deepseek")
    model: str | None = None
    cache_dir: Path = LLM_CACHE
    offline: bool = False  # True: never call the network, fail on a cache miss

    def __post_init__(self):
        if self.provider not in PROVIDERS:
            raise ValueError(f"unknown provider {self.provider!r}; choose from {sorted(PROVIDERS)}")
        self.model = self.model or PROVIDERS[self.provider]["model"]

    def _key(self, messages: list[dict], params: dict) -> str:
        blob = json.dumps({"provider": self.provider, "model": self.model, "messages": messages,
                           "params": params}, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(blob.encode()).hexdigest()[:24]

    def complete(self, messages: list[dict], *, json_mode: bool = True, temperature: float = 0.0,
                 max_tokens: int = 4000, tag: str = "") -> str:
        params = {"temperature": temperature, "max_tokens": max_tokens, "json_mode": json_mode}
        h = self._key(messages, params)
        path = self.cache_dir / f"{h}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))["response"]
        if self.offline:
            raise ReplayMiss(f"no recorded response for request {h} ({tag}); rerun online with "
                             f"{PROVIDERS[self.provider]['key']} set to record it")
        cfg = PROVIDERS[self.provider]
        key = secret(cfg["key"])
        if not key:
            raise ReplayMiss(f"no recorded response for request {h} and {cfg['key']} is not set")
        body = {"model": self.model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        t0 = time.time()
        for attempt in range(4):
            r = requests.post(cfg["base"] + "/chat/completions", json=body, timeout=600,
                              headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(5 * (attempt + 1))
                continue
            break
        if r.status_code != 200:
            raise RuntimeError(f"{self.provider} HTTP {r.status_code}: {r.text[:300]}")
        j = r.json()
        text = j["choices"][0]["message"]["content"] or ""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "hash": h, "tag": tag, "provider": self.provider, "model": self.model,
            "params": params, "messages": messages, "response": text,
            "usage": j.get("usage"), "latency_s": round(time.time() - t0, 2),
            "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }, indent=1, ensure_ascii=False), encoding="utf-8")
        return text


def parse_json(text: str) -> dict:
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(t)
