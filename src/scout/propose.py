"""Proposers for the learning loop. A proposer sees only the discovery view of the ledger
(loop.public_view) and returns one signal spec, or None to stop. Code validates whatever it returns.

    scripted  deterministic and reproducible: RSI overbought, RSI oversold, RSI divergence, each of
              them with a MACD cross and with the MACD histogram sign, then the best branch so far
              (by discovery t-stat) refined once.
    llm       the language model reads the discovery ledger and proposes the next spec as JSON;
              prompts and responses are cached in llm_cache/ like every other model call.
"""

from __future__ import annotations

import copy
import json

from .loop import FEATURES, HOLDS, MAX_CONDITIONS, MAX_WITHIN, LoopStop


def _c(feature, op, value, within=1):
    return {"feature": feature, "op": op, "value": value, "within": within}


OB, OS = _c("rsi14", ">", 70), _c("rsi14", "<", 30)
BEAR, BULL = _c("rsi_bear_div", "==", True), _c("rsi_bull_div", "==", True)
X_DN, X_UP = _c("macd_cross_down", "==", True), _c("macd_cross_up", "==", True)
H_NEG, H_POS = _c("macd_hist", "<", 0), _c("macd_hist", ">", 0)


def _spec(sid, why, long=(), short=(), hold=10, tf="D"):
    return {"id": sid, "rationale": why, "timeframe": tf, "hold_days": hold, "long": list(long), "short": list(short)}


def _within(c, w):
    return {**c, "within": w}


SCRIPT = [
    _spec("rsi_overbought", "Overbought names mean-revert: short when daily RSI is above 70.", short=[OB]),
    _spec("rsi_oversold", "Oversold names bounce: long when daily RSI is below 30.", long=[OS]),
    _spec("rsi_divergence", "Momentum fading against price: short bearish divergences, buy bullish ones.",
          long=[BULL], short=[BEAR]),
    _spec("overbought_macd_cross", "Overbought, then MACD rolls over: RSI above 70 in the last 5 bars and MACD "
                                   "crossing below its signal today.", short=[_within(OB, 5), X_DN]),
    _spec("oversold_macd_cross", "Oversold, then MACD turns up: RSI below 30 in the last 5 bars and MACD crossing "
                                 "above its signal today.", long=[_within(OS, 5), X_UP]),
    _spec("divergence_macd_cross", "Divergence confirmed by a MACD cross within 5 bars.",
          long=[_within(BULL, 5), X_UP], short=[_within(BEAR, 5), X_DN]),
    _spec("overbought_macd_state", "Overbought with MACD already below its signal.", short=[OB, H_NEG]),
    _spec("oversold_macd_state", "Oversold with MACD already above its signal.", long=[OS, H_POS]),
    _spec("divergence_macd_state", "Divergence with the MACD histogram on the same side.",
          long=[BULL, H_POS], short=[BEAR, H_NEG]),
]


def refine(spec: dict) -> dict:
    """One refinement of a branch: tighten RSI thresholds by 5 points; with no RSI threshold, hold 20 days
    (or 5 if it already held 20)."""
    s = copy.deepcopy(spec)
    tightened = False
    for side in ("long", "short"):
        for c in s[side]:
            if c["feature"] == "rsi14":
                c["value"] = float(c["value"]) + (5 if c["op"] == ">" else -5)
                tightened = True
    if not tightened:
        s["hold_days"] = 20 if s["hold_days"] != 20 else 5
    s["id"] = (spec["id"] + "_refined")[:60]
    s["rationale"] = (f"Refine the best branch so far ({spec['id']}): "
                      + ("RSI thresholds 5 points tighter." if tightened else f"hold {s['hold_days']} days."))
    return s


class Scripted:
    name = "scripted"

    def __call__(self, history: list[dict], step: int, K: int):
        if step <= len(SCRIPT):
            return copy.deepcopy(SCRIPT[step - 1])
        if step == len(SCRIPT) + 1:
            tested = [h for h in history if h["discovery"] and h["discovery"]["t_stat"] is not None]
            if not tested:
                return None
            best = max(tested, key=lambda h: (h["discovery"]["t_stat"], -h["step"]))
            return refine(best["spec"])
        return None


SYSTEM = f"""You propose trading-signal hypotheses for a fixed evaluator. You never see out-of-sample results;
you see only discovery-period results of earlier attempts. Every attempt counts against a fixed budget and
raises the bar for all of them (Bonferroni), so propose ideas that are distinct and well motivated.

Return ONE JSON object and nothing else:
{{"id": "snake_case_name", "rationale": "one sentence", "timeframe": "D" or "W", "hold_days": one of {list(HOLDS)},
  "long": [conditions], "short": [conditions]}}
A condition is {{"feature": name, "op": op, "value": value, "within": 1-{MAX_WITHIN}}} ("within" = true on any of the
last N bars of that timeframe). At most {MAX_CONDITIONS} conditions per side; at least one side non-empty.
Features (computed on daily or weekly closes):
""" + "\n".join(
    f"  {k}: {v['label']}; " + ("op '==' with true/false" if v["kind"] == "bool" else
                                ("op '<' or '>' with 0 only" if k == "macd_hist" else "op '<' or '>' with 0-100"))
    for k, v in FEATURES.items()) + """
A signal on bar t's close enters at the next close and is held hold_days sessions. Long earns the forward
return minus the universe mean; short earns the negative. Costs are charged. Do not repeat a tested spec."""


class LLMProposer:
    name = "llm"

    def __init__(self, llm):
        self.llm = llm
        self.name = f"llm ({llm.provider}/{llm.model})"
        self.messages_seen: list[list[dict]] = []

    def __call__(self, history: list[dict], step: int, K: int):
        from .llm import ReplayMiss, parse_json
        user = {"step": step, "budget_K": K, "steps_left_including_this": K - step + 1,
                "history": [{k: h[k] for k in ("step", "status", "spec", "proposal_problems", "discovery",
                                               "discovery_pass", "discovery_reason")} for h in history]}
        msgs = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": json.dumps(user, sort_keys=True)}]
        self.messages_seen.append(msgs)
        try:
            text = self.llm.complete(msgs, json_mode=True, temperature=0.0, max_tokens=8000, tag=f"loop step {step}")
        except ReplayMiss as e:
            raise LoopStop(f"LLM unavailable ({e})") from e
        try:
            return parse_json(text)
        except (json.JSONDecodeError, IndexError, ValueError):
            return {"unparseable_response": text[:200]}
