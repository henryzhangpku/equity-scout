"""Paths and secret loading.

Secrets are read from the process environment first and, on Windows, fall back
to the per-user environment block in the registry (HKCU\\Environment), which is
where User env vars live when a shell was started before they were set. Values
are never printed, logged or written to disk by this package.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = Path(os.environ.get("SCOUT_CACHE", ROOT / ".cache"))
RUNS = ROOT / "runs"
LLM_CACHE = ROOT / "llm_cache"

SEC_USER_AGENT = "equity-scout research demo heng.henry.zhang@gmail.com"


def secret(name: str) -> str | None:
    """Return a secret by env var name, or None if unset. Never logs the value."""
    val = os.environ.get(name)
    if val:
        return val.strip()
    if sys.platform == "win32":
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
                val, _ = winreg.QueryValueEx(k, name)
                return str(val).strip() or None
        except OSError:
            return None
    return None
