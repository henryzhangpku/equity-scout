"""English observation -> screen spec. The model proposes; `spec.validate` decides."""

from __future__ import annotations

import json

from .llm import LLM, parse_json
from .spec import MAX_TOP_N, Spec, SpecError, schema_for_prompt, validate

_TEMPLATE = """You translate an investment observation written in plain English into a JSON screen
specification for a deterministic stock screener. You do not pick stocks and you do not
compute anything: code will run the screen exactly as you specify it.

Output ONE JSON object with exactly these keys:
  "version": 1,
  "observation": the user's text verbatim,
  "universe": optional keys market_cap_min, market_cap_max (USD), min_price (USD),
              min_avg_dollar_volume (USD), industries (list), exclude_industries (list),
  "conditions": list of {{"field", "op", "value" OR "ref", "why"}},
  "rank": list of {{"field", "direction": "asc"|"desc", "weight"}} (desc = higher is better),
  "top_n": integer 1-{MAX_TOP_N} (default 5),
  "unmapped": list of {{"text", "reason"}} for every part of the observation that the
              fields below cannot express,
  "notes": one or two sentences on interpretation choices.

Rules:
- Use only the fields and industry groups listed below. Never invent a field.
- op is one of < <= > >= between ==. "between" takes value [low, high]. "==" is only
  for boolean fields. Use "ref" to compare two fields of the same kind,
  e.g. {{"field": "close", "op": ">", "ref": "sma50"}}.
- Ratios are decimals: 10% is 0.10, a 20% pullback is drawdown_52w <= -0.20.
- "why" quotes or paraphrases the words of the observation that the condition encodes.
- If the observation asks for something these fields cannot measure (a theme, analyst
  revisions, insider buying, guidance, sentiment, an index the fields do not cover),
  put it in "unmapped" with the reason. Do not approximate silently. If you use an
  imperfect proxy, say so in "notes" and still list the original idea in "unmapped".
- Prefer few, faithful conditions over many. Rank by what the observation emphasises.

{schema}
"""

PROMPT_VERSION = 2  # 1 = recordings before sectors existed (frozen); 2 = adds sectors / industry groups


def system_prompt(version: int = PROMPT_VERSION) -> str:
    text = _TEMPLATE.replace("{{", "{").replace("}}", "}").replace("{MAX_TOP_N}", str(MAX_TOP_N))
    if version >= 2:
        text = text.replace("min_avg_dollar_volume (USD), industries (list), exclude_industries (list),",
                            "min_avg_dollar_volume (USD), sectors (list), industry_groups (list),\n"
                            "              industries (list), exclude_industries (list), themes (list),")
    return text.replace("{schema}", schema_for_prompt(version))


SYSTEM = system_prompt()


def translate(observation: str, llm: LLM, short_interest_available: bool = True,
              prompt_version: int = PROMPT_VERSION) -> tuple[Spec, list[dict]]:
    """Return (validated spec, transcript of attempts)."""
    messages = [{"role": "system", "content": system_prompt(prompt_version)}, {"role": "user", "content": observation}]
    attempts = []
    for attempt in range(2):
        raw = llm.complete(messages, tag=f"translate#{attempt}")
        try:
            d = parse_json(raw)
        except json.JSONDecodeError as e:
            attempts.append({"response": raw, "problems": [f"not valid JSON: {e}"]})
            problems = [f"not valid JSON: {e}"]
        else:
            if isinstance(d, dict):
                d["observation"] = observation  # the user's words, never the model's paraphrase
            try:
                spec = validate(d, short_interest_available=short_interest_available)
                attempts.append({"response": raw, "problems": []})
                return spec, attempts
            except SpecError as e:
                problems = e.problems
                attempts.append({"response": raw, "problems": problems})
        messages = messages + [
            {"role": "assistant", "content": raw},
            {"role": "user", "content": "The screener refused that spec:\n- " + "\n- ".join(problems)
             + "\nReturn a corrected JSON spec. Move anything you cannot express into 'unmapped'."},
        ]
    raise SpecError(["the model did not produce a valid spec after a correction round"]
                    + attempts[-1]["problems"])
