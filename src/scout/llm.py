"""Pluggable LLM client with a committed record/replay cache.

Every request (provider, model, messages, params) is hashed; the full prompt and
response are written to llm_cache/<hash>.json. On replay the cached response is
returned without a network call, so recorded runs reproduce offline with no key.

Providers speak the OpenAI-compatible chat-completions protocol. SCOUT_LLM picks
one of the PROVIDERS entries below (the default entry, or an alternative); each
entry carries that provider's documented endpoint, key variable and model.
SCOUT_LLM_BASE_URL, SCOUT_LLM_API_KEY and SCOUT_LLM_MODEL override them for any
OpenAI-compatible endpoint.
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


def base_url(provider: str) -> str:
    """The endpoint for `provider`: SCOUT_LLM_BASE_URL if set, else the provider's own."""
    return (os.environ.get("SCOUT_LLM_BASE_URL") or PROVIDERS[provider]["base"]).rstrip("/")


def key_name(provider: str) -> str:
    """The variable the key is read from: SCOUT_LLM_API_KEY if set, else the provider's own."""
    return "SCOUT_LLM_API_KEY" if secret("SCOUT_LLM_API_KEY") else PROVIDERS[provider]["key"]


def api_key(provider: str) -> str | None:
    return secret(key_name(provider))


class ReplayMiss(RuntimeError):
    pass


@dataclass
class LLM:
    provider: str = os.environ.get("SCOUT_LLM", "deepseek")
    model: str | None = None
    cache_dir: Path = LLM_CACHE
    offline: bool = False  # True: never call the network, fail on a cache miss
    timeout: float = 600.0  # seconds per HTTP request

    def __post_init__(self):
        if self.provider not in PROVIDERS:
            raise ValueError(f"unknown provider {self.provider!r}; choose from {sorted(PROVIDERS)}")
        self.model = self.model or os.environ.get("SCOUT_LLM_MODEL") or PROVIDERS[self.provider]["model"]

    def _key(self, messages: list[dict], params: dict) -> str:
        blob = json.dumps({"provider": self.provider, "model": self.model, "messages": messages,
                           "params": params}, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(blob.encode()).hexdigest()[:24]

    def complete(self, messages: list[dict], *, json_mode: bool = True, temperature: float = 0.0,
                 max_tokens: int = 8000, tag: str = "") -> str:
        params = {"temperature": temperature, "max_tokens": max_tokens, "json_mode": json_mode}
        h = self._key(messages, params)
        path = self.cache_dir / f"{h}.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))["response"]
        if self.offline:
            raise ReplayMiss(f"no recorded response for request {h} ({tag}); rerun online with "
                             f"{key_name(self.provider)} set to record it")
        key = api_key(self.provider)
        if not key:
            raise ReplayMiss(f"no recorded response for request {h} and {key_name(self.provider)} is not set")
        body = {"model": self.model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        t0 = time.time()
        for attempt in range(4):
            r = requests.post(base_url(self.provider) + "/chat/completions", json=body, timeout=self.timeout,
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
