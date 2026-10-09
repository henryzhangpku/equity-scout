"""Backtest a screen on point-in-time monthly panels. Pure code; the model plays no part.

Each month-end rebalance: apply the screen (universe filters, sectors, conditions) to that date's
panel, rank as the spec says, hold the top N equal-weight until the next month end. Returns come
from adjusted closes; a name with no bar on the next rebalance date exits at its last close before
it (and is noted). Costs are charged on turnover: sum of |weight change| x cost per side.

Benchmarks: SPY, and the equal-weight universe (the screen's universe filters only, no
conditions), so you can see whether the conditions added anything.

Gates (fixed): the monthly excess return over SPY must be positive (a) on average after costs,
(b) in the first half and (c) the second half of the months, (d) with the single best month
removed, (e) at double costs; and there must be at least MIN_MONTHS evaluable months (MIN_NAMES+
names held). Verdict: "Edge on this history" / "No edge" / "Not enough data".
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

from .panels import PANEL_DIR, PANEL_FILE
from .screen import rank, run_screen, universe_steps, with_sectors
from .spec import FIELDS, Spec, SpecError

COST_BPS = 10.0
DEFAULT_TOP_N = 10
MIN_MONTHS = 18
MIN_NAMES = 3


@dataclass
class Panels:
    dates: list
    symbols: np.ndarray
    fields: list
    values: np.ndarray
    close_at: np.ndarray
    last_close: np.ndarray
    last_date: np.ndarray
    in_universe: np.ndarray
    names: np.ndarray
    sic: np.ndarray
    spy_close: np.ndarray
    check_date: list
    check_values: np.ndarray
    check_universe: np.ndarray

    def frame(self, di: int, check: bool = False) -> pd.DataFrame:
        """The panel on rebalance di (or the check slice) as a features frame, universe rows only."""
        vals = self.check_values[0] if check else self.values[di]
        uni = self.check_universe[0] if check else self.in_universe[di]
        df = pd.DataFrame(vals[uni].astype(np.float64), columns=self.fields)
        df.insert(0, "symbol", self.symbols[uni])
        df.insert(1, "name", self.names[uni])
        df["sic"] = self.sic[uni]
        b = df["sma50_above_sma200"]
        df["sma50_above_sma200"] = [None if (x != x) else bool(x) for x in b]
        df["_n"] = np.nonzero(uni)[0]
        return df


@lru_cache(maxsize=2)
def load_panels(path: str | None = None) -> Panels:
    p = Path(path) if path else PANEL_DIR / PANEL_FILE
    z = np.load(p, allow_pickle=False)
    return Panels(dates=[str(d) for d in z["dates"]], symbols=z["symbols"], fields=[str(f) for f in z["fields"]],
                  values=z["values"], close_at=z["close_at"], last_close=z["last_close"], last_date=z["last_date"],
                  in_universe=z["in_universe"], names=z["names"], sic=z["sic"], spy_close=z["spy_close"],
                  check_date=[str(d) for d in z["check_date"]], check_values=z["check_values"],
                  check_universe=z["check_universe"])


def universe_only(df: pd.DataFrame, spec: Spec) -> pd.DataFrame:
    d = with_sectors(df)
    for _, fn in universe_steps(spec):
        passed, _ = fn(d)
        d = d[passed.to_numpy()]
    return d


def period_returns(P: Panels, di: int, cols: list[int]) -> tuple[np.ndarray, list[str]]:
    """Return from rebalance di to di+1 for panel columns `cols`; exits at the last close if a name stopped."""
    entry = P.close_at[di, cols]
    nxt = P.close_at[di + 1, cols]
    exitp = np.where(np.isfinite(nxt), nxt, P.last_close[di + 1, cols])
    stopped = [str(P.symbols[c]) for c, x in zip(cols, nxt) if not np.isfinite(x)]
    r = exitp / entry - 1.0
    return np.where(np.isfinite(r), r, 0.0), stopped


def turnover(prev_w: dict, prev_r: dict, new_w: dict) -> float:
    """Sum of |new weight - drifted old weight| over all names (buys + sells), drift from last period's returns."""
    if prev_w:
        gross = sum(w * (1 + prev_r.get(k, 0.0)) for k, w in prev_w.items())
        drift = {k: w * (1 + prev_r.get(k, 0.0)) / gross for k, w in prev_w.items()} if gross > 0 else {}
    else:
        drift = {}
    keys = set(drift) | set(new_w)
    return float(sum(abs(new_w.get(k, 0.0) - drift.get(k, 0.0)) for k in keys))


def stats(r: list[float]) -> dict:
    a = np.array(r, dtype=float)
    if len(a) == 0:
        return {"cagr": None, "vol": None, "sharpe": None, "max_drawdown": None, "total": None}
    curve = np.cumprod(1 + a)
    peak = np.maximum.accumulate(curve)
    sd = a.std(ddof=1) if len(a) > 1 else float("nan")
    return {"total": float(curve[-1] - 1), "cagr": float(curve[-1] ** (12 / len(a)) - 1),
            "vol": float(sd * math.sqrt(12)) if np.isfinite(sd) else None,
            "sharpe": float(a.mean() / sd * math.sqrt(12)) if np.isfinite(sd) and sd > 0 else None,
            "max_drawdown": float((curve / peak - 1).min())}


def gates(excess: list[float], excess_2x: list[float], n_eval: int) -> tuple[str, list[dict]]:
    e = np.array(excess, dtype=float)
    e2 = np.array(excess_2x, dtype=float)
    h = len(e) // 2
    best_removed = np.delete(e, int(np.argmax(e))) if len(e) > 1 else e
    g = [
        {"id": "floor", "label": f"At least {MIN_MONTHS} months holding {MIN_NAMES}+ names",
         "value": n_eval, "pass": n_eval >= MIN_MONTHS},
        {"id": "a", "label": "Average monthly excess over SPY after costs > 0", "value": _m(e), "pass": bool(_m(e) > 0)},
        {"id": "b", "label": "First half of the months > 0", "value": _m(e[:h]), "pass": _m(e[:h]) > 0},
        {"id": "c", "label": "Second half of the months > 0", "value": _m(e[h:]), "pass": _m(e[h:]) > 0},
        {"id": "d", "label": "Still > 0 with the single best month removed", "value": _m(best_removed),
         "pass": _m(best_removed) > 0},
        {"id": "e", "label": "Still > 0 at double costs", "value": _m(e2), "pass": _m(e2) > 0},
    ]
    if not g[0]["pass"]:
        verdict = "Not enough data"
    elif all(x["pass"] for x in g[1:]):
        verdict = "Edge on this history"
    else:
        verdict = "No edge"
    return verdict, g


def _m(x) -> float:
    x = np.asarray(x, dtype=float)
    return float(x.mean()) if len(x) else float("nan")


def run(spec: Spec, P: Panels | None = None, cost_bps: float = COST_BPS, top_n: int | None = None) -> dict:
    P = P or load_panels()
    n_hold = top_n or spec.top_n or DEFAULT_TOP_N
    D = len(P.dates)
    months, prev_w, prev_r, prev_w2, prev_r2 = [], {}, {}, {}, {}
    used_fields = sorted({c["field"] for c in spec.conditions} | {c["ref"] for c in spec.conditions if "ref" in c}
                         | {r["field"] for r in spec.rank})
    missing = [f for f in used_fields if f not in P.fields]
    if missing:
        raise SpecError([f"'{f}' is not stored in the historical panels (relative strength vs sector ETFs is "
                         "left out to keep them small), so this screen cannot be backtested" for f in missing])
    for di in range(D - 1):
        df = P.frame(di)
        _, surv = run_screen(df, spec)
        ranked = rank(surv, spec)
        held = ranked.head(n_hold)
        cols = [int(x) for x in held["_n"]]
        rets, stopped = period_returns(P, di, cols) if cols else (np.array([]), [])
        gross = float(rets.mean()) if cols else 0.0
        new_w = {P.symbols[c].item(): 1.0 / len(cols) for c in cols} if cols else {}
        to = turnover(prev_w, prev_r, new_w)
        uni = universe_only(df, spec)
        ucols = [int(x) for x in uni["_n"]]
        urets, _ = period_returns(P, di, ucols) if ucols else (np.array([]), [])
        spy = float(P.spy_close[di + 1] / P.spy_close[di] - 1)
        months.append({"date": P.dates[di], "to": P.dates[di + 1], "held": [P.symbols[c].item() for c in cols],
                       "n": len(cols), "n_survivors": int(len(ranked)), "gross": gross,
                       "turnover": to, "cost": to * cost_bps / 1e4, "net": gross - to * cost_bps / 1e4,
                       "net_2x": gross - to * 2 * cost_bps / 1e4, "spy": spy,
                       "universe": float(urets.mean()) if ucols else None, "n_universe": len(ucols),
                       "stopped": stopped})
        prev_w, prev_r = new_w, {P.symbols[c].item(): float(x) for c, x in zip(cols, rets)}

    ev = [m for m in months if m["n"] >= MIN_NAMES]
    verdict, g = gates([m["net"] - m["spy"] for m in ev], [m["net_2x"] - m["spy"] for m in ev], len(ev))
    curve, s, b, u = [], 1.0, 1.0, 1.0
    for m in months:
        s *= 1 + m["net"]; b *= 1 + m["spy"]; u *= 1 + (m["universe"] or 0.0)
        curve.append({"date": m["to"], "strategy": s, "spy": b, "universe": u})
    nan_share = {}
    for f in used_fields:
        j = P.fields.index(f)
        v = P.values[:, :, j][P.in_universe]
        nan_share[f] = float(np.mean(~np.isfinite(v))) if v.size else 1.0
    return finite({
        "params": {"top_n": n_hold, "cost_bps_per_side": cost_bps, "rebalance": "monthly (last trading day)",
                   "first": P.dates[0], "last": P.dates[-1], "n_months": len(months), "min_months": MIN_MONTHS,
                   "min_names": MIN_NAMES},
        "spec": spec.to_dict(), "verdict": verdict, "gates": g,
        "stats": {"strategy": stats([m["net"] for m in months]), "spy": stats([m["spy"] for m in months]),
                  "universe": stats([m["universe"] or 0.0 for m in months]),
                  "hit_rate_vs_spy": float(np.mean([m["net"] > m["spy"] for m in ev])) if ev else None,
                  "avg_names": float(np.mean([m["n"] for m in months])) if months else 0.0,
                  "avg_turnover": float(np.mean([m["turnover"] for m in months[1:]])) if len(months) > 1 else None,
                  "months_too_few": sum(1 for m in months if m["n"] < MIN_NAMES),
                  "names_stopped": sum(len(m["stopped"]) for m in months)},
        "curve": curve, "months": months, "missing_share": nan_share,
        "caveats": caveats(P, used_fields, nan_share, len(months), spec),
    })


def finite(x):
    """NaN/inf -> None everywhere, so the result is valid JSON for browsers."""
    if isinstance(x, dict):
        return {k: finite(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [finite(v) for v in x]
    if isinstance(x, (float, np.floating)):
        return float(x) if math.isfinite(x) else None
    if isinstance(x, np.integer):
        return int(x)
    if isinstance(x, np.bool_):
        return bool(x)
    return x


def caveats(P: Panels, used: list[str], nan_share: dict, n_months: int, spec: Spec | None = None) -> list[str]:
    c = []
    if spec is not None and spec.universe.get("themes"):
        c.append("Look-ahead warning: the theme baskets used here were picked in 2026, knowing which companies became "
                 "AI winners. Testing them on earlier years is biased upward, so an edge on this screen is not reliable.")
    c += [
        f"Evidence on {n_months} months ({P.dates[0]} to {P.dates[-1]}), not proof: a short history can flatter or hide an idea.",
        "Survivorship: the candidates are companies listed today; names that delisted, went bankrupt or were acquired "
        "before today are missing from free data, which flatters past returns.",
        "Point in time: each month uses only facts filed on or before that date and prices up to that date; "
        "short interest from the latest FINRA settlement visible then.",
        "The model is not used in backtests and news is not used; returns come from split- and dividend-adjusted closes, "
        "equal weight, no slippage beyond the stated cost. Benchmarks carry no costs.",
        "Sectors use today's SIC codes and overrides for every month.",
    ]
    thin = [f for f, s in nan_share.items() if s > 0.5]
    if thin:
        c.append("Mostly missing historically (fewer than half of names have a value): " + ", ".join(thin) + ".")
    if any(FIELDS[f].group == "short_interest" for f in used):
        c.append("Short interest is twice monthly and as a share of shares outstanding, not float.")
    return c
