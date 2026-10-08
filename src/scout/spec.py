"""The screen specification: a typed, whitelisted contract between model and code.

The language model's only job upstream of the screen is to fill this structure.
`validate()` checks every key, field, operator, unit and threshold; anything
outside the whitelist is refused with an explanation. Nothing is silently
dropped: an invalid spec stops the run, and parts of the observation the model
says it could not express are carried to the report as `unmapped`.

All ratios are decimals: 0.10 means 10%. Money is in US dollars.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

SPEC_VERSION = 1


@dataclass(frozen=True)
class Field:
    name: str
    group: str        # size | technical | fundamental | short_interest
    kind: str         # usd | ratio | number | bool | days
    desc: str


def _fields() -> dict[str, Field]:
    fs = [
        Field("market_cap", "size", "usd", "price x latest shares outstanding (SEC cover page), as of the run date"),
        Field("ev", "size", "usd", "enterprise value = market cap + total debt - cash and short-term investments"),
        Field("close", "technical", "usd", "last adjusted close"),
        Field("avg_dollar_volume_50d", "size", "usd", "mean of close x volume over the last 50 sessions"),
        Field("sma20", "technical", "usd", "20-day simple moving average of close"),
        Field("sma50", "technical", "usd", "50-day simple moving average of close"),
        Field("sma200", "technical", "usd", "200-day simple moving average of close"),
        Field("pct_vs_sma20", "technical", "ratio", "close / SMA20 - 1"),
        Field("pct_vs_sma50", "technical", "ratio", "close / SMA50 - 1"),
        Field("pct_vs_sma200", "technical", "ratio", "close / SMA200 - 1"),
        Field("sma50_above_sma200", "technical", "bool", "true when SMA50 > SMA200 (golden-cross structure)"),
        Field("rsi14", "technical", "number", "Wilder RSI(14), 0-100"),
        Field("macd", "technical", "number", "MACD line, EMA12 - EMA26 of close"),
        Field("macd_signal", "technical", "number", "EMA9 of the MACD line"),
        Field("macd_hist", "technical", "number", "MACD - signal; > 0 means MACD above its signal"),
        Field("volume_ratio_50d", "technical", "number", "today's volume / mean volume of the prior 50 sessions"),
        Field("drawdown_52w", "technical", "ratio", "close / 52-week (252-session) high close - 1; -0.20 = 20% below the high"),
    ]
    for m in (1, 3, 6, 12):
        fs.append(Field(f"mom_{m}m", "technical", "ratio", f"{m}-month price return ({ {1: 21, 3: 63, 6: 126, 12: 252}[m] } sessions)"))
    for b, label in BENCHMARK_LABELS.items():
        for m in (1, 3, 6, 12):
            fs.append(Field(f"rs_{m}m_vs_{b}", "technical", "ratio",
                            f"{m}-month return minus {label} {m}-month return (negative = lagging)"))
    fs += [
        Field("revenue_ttm", "fundamental", "usd", "trailing-twelve-month revenue (sum of last 4 fiscal quarters)"),
        Field("revenue_growth_yoy", "fundamental", "ratio", "TTM revenue vs TTM revenue one year earlier - 1"),
        Field("revenue_growth_q_yoy", "fundamental", "ratio", "latest fiscal quarter revenue vs same quarter a year earlier - 1"),
        Field("revenue_growth_accel", "fundamental", "ratio",
              "latest quarter YoY growth minus prior quarter YoY growth; > 0 means growth is accelerating"),
        Field("gross_margin", "fundamental", "ratio", "TTM gross profit / TTM revenue"),
        Field("operating_margin", "fundamental", "ratio", "TTM operating income / TTM revenue"),
        Field("net_margin", "fundamental", "ratio", "TTM net income / TTM revenue"),
        Field("net_income_ttm", "fundamental", "usd", "TTM net income; > 0 means profitable on a GAAP basis"),
        Field("fcf_ttm", "fundamental", "usd", "TTM free cash flow = operating cash flow - capital expenditure"),
        Field("fcf_margin", "fundamental", "ratio", "TTM FCF / TTM revenue"),
        Field("fcf_yield", "fundamental", "ratio", "TTM FCF / market cap"),
        Field("net_debt", "fundamental", "usd", "total debt - cash and short-term investments (negative = net cash)"),
        Field("ev_to_sales", "fundamental", "number", "EV / TTM revenue"),
        Field("short_pct_shares_out", "short_interest", "ratio",
              "FINRA short interest / shares outstanding (not float: float is not in free data)"),
        Field("days_to_cover", "short_interest", "days", "FINRA days to cover (short shares / average daily volume)"),
    ]
    return {f.name: f for f in fs}


BENCHMARK_LABELS = {
    "spy": "SPY (S&P 500)", "qqq": "QQQ (Nasdaq-100)", "iwm": "IWM (Russell 2000)",
    "smh": "SMH (semiconductor ETF, MVIS US Listed Semiconductor 25)",
    "soxx": "SOXX (semiconductor ETF, NYSE Semiconductor Index)",
    "xlk": "XLK (technology)", "xlf": "XLF (financials)", "xle": "XLE (energy)", "xlv": "XLV (health care)",
    "xli": "XLI (industrials)", "xlu": "XLU (utilities)", "xly": "XLY (consumer discretionary)",
    "xlp": "XLP (consumer staples)", "xlb": "XLB (materials)", "xlre": "XLRE (real estate)",
    "xlc": "XLC (communication services)",
}
FIELDS = _fields()

# Industry groups are fixed sets of SEC SIC codes. SIC is coarse: it cannot, for
# example, separate data-center REITs from other REITs. The report says so.
INDUSTRIES: dict[str, tuple[str, set[int]]] = {
    "semiconductors": ("SIC 3674 semiconductors and related devices", {3674}),
    "semiconductor_equipment": ("SIC 3559 special industry machinery (includes wafer-fab equipment)", {3559}),
    "electronic_components": ("SIC 3672/3677/3678/3679 circuit boards, connectors, components", {3672, 3677, 3678, 3679}),
    "computer_hardware": ("SIC 3570-3577 computers, storage, peripherals", {3570, 3571, 3572, 3575, 3576, 3577}),
    "networking_comm_equipment": ("SIC 3576/3661/3663/3669 networking and communications equipment",
                                  {3576, 3661, 3663, 3669}),
    "electrical_power_equipment": ("SIC 3600-3629, 3690-3699 electrical equipment, transformers, switchgear",
                                   set(range(3600, 3630)) | set(range(3690, 3700))),
    "electric_power_producers": ("SIC 4911/4931/4991 electric utilities and independent power producers",
                                 {4911, 4931, 4991}),
    "reits": ("SIC 6798 real estate investment trusts (all REITs; SIC cannot isolate data-center REITs)", {6798}),
    "data_processing_hosting": ("SIC 7374 computer processing, data preparation, hosting", {7374}),
    "software": ("SIC 7370-7373 software and computer services", {7370, 7371, 7372, 7373}),
    "pharma_biotech": ("SIC 2833-2836 drugs and biologicals", {2833, 2834, 2835, 2836}),
    "medical_devices": ("SIC 3841-3851 medical instruments and supplies", set(range(3841, 3852))),
    "banks": ("SIC 6021-6036 banks and savings institutions", set(range(6021, 6037))),
    "insurance": ("SIC 6311-6411 insurance carriers and agents", set(range(6311, 6412))),
    "oil_gas": ("SIC 1311/1381/1382/1389/2911/4922-4924 oil and gas", {1311, 1381, 1382, 1389, 2911, 4922, 4923, 4924}),
    "aerospace_defense": ("SIC 3720-3729, 3760-3769, 3812 aerospace and defense",
                          set(range(3720, 3730)) | set(range(3760, 3770)) | {3812}),
    "retail": ("SIC 5200-5999 retail trade", set(range(5200, 6000))),
    "industrial_machinery": ("SIC 3510-3569 industrial machinery", set(range(3510, 3570)) - {3559}),
}

# Curated theme baskets: fixed ticker lists, defined and reviewed in code (never by the model),
# for themes SIC cannot isolate. A licensed deployment would use a vendor theme classification.
THEMES: dict[str, tuple[str, set[str]]] = {
    "data_center_reits": ("curated: REITs whose business is data centers", {"EQIX", "DLR"}),
    "neoclouds": ("curated: GPU cloud / AI-compute providers", {"CRWV", "NBIS", "IREN", "APLD"}),
}

OPS = {"<", "<=", ">", ">=", "between", "=="}
UNIVERSE_KEYS = {"market_cap_min", "market_cap_max", "min_price", "min_avg_dollar_volume",
                 "industries", "exclude_industries", "themes"}
TOP_KEYS = {"version", "observation", "universe", "conditions", "rank", "top_n", "unmapped", "notes"}
COND_KEYS = {"field", "op", "value", "ref", "why"}
RANK_KEYS = {"field", "direction", "weight"}
MAX_TOP_N = 10


class SpecError(ValueError):
    def __init__(self, problems: list[str]):
        super().__init__("; ".join(problems))
        self.problems = problems


@dataclass
class Spec:
    observation: str
    universe: dict
    conditions: list[dict]
    rank: list[dict]
    top_n: int = 5
    unmapped: list[dict] = field(default_factory=list)
    notes: str = ""
    version: int = SPEC_VERSION

    def to_dict(self) -> dict:
        return {"version": self.version, "observation": self.observation, "universe": self.universe,
                "conditions": self.conditions, "rank": self.rank, "top_n": self.top_n,
                "unmapped": self.unmapped, "notes": self.notes}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


def _num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and x == x and abs(x) != float("inf")


def validate(d: dict, short_interest_available: bool = True) -> Spec:
    """Return a Spec or raise SpecError listing every problem found."""
    p: list[str] = []
    if not isinstance(d, dict):
        raise SpecError(["spec must be a JSON object"])
    for k in d:
        if k not in TOP_KEYS:
            p.append(f"unknown top-level key '{k}' (allowed: {sorted(TOP_KEYS)})")
    obs = d.get("observation")
    if not isinstance(obs, str) or not obs.strip():
        p.append("'observation' must be the user's text")

    u = d.get("universe") or {}
    if not isinstance(u, dict):
        p.append("'universe' must be an object")
        u = {}
    for k, v in u.items():
        if k not in UNIVERSE_KEYS:
            p.append(f"unknown universe key '{k}' (allowed: {sorted(UNIVERSE_KEYS)})")
        elif k in ("industries", "exclude_industries", "themes"):
            allowed = THEMES if k == "themes" else INDUSTRIES
            label = "theme basket" if k == "themes" else "industry group"
            if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
                p.append(f"universe.{k} must be a list of {label} names")
            else:
                for x in v:
                    if x not in allowed:
                        p.append(f"unknown {label} '{x}' (allowed: {sorted(allowed)})")
        elif not _num(v) or v < 0:
            p.append(f"universe.{k} must be a non-negative number, got {v!r}")
    if _num(u.get("market_cap_min")) and _num(u.get("market_cap_max")) and u["market_cap_min"] >= u["market_cap_max"]:
        p.append("universe.market_cap_min must be below market_cap_max")

    conds = d.get("conditions")
    if not isinstance(conds, list) or not conds:
        p.append("'conditions' must be a non-empty list")
        conds = []
    for i, c in enumerate(conds):
        where = f"conditions[{i}]"
        if not isinstance(c, dict):
            p.append(f"{where} must be an object")
            continue
        for k in c:
            if k not in COND_KEYS:
                p.append(f"{where}: unknown key '{k}' (allowed: {sorted(COND_KEYS)})")
        f = c.get("field")
        if f not in FIELDS:
            p.append(f"{where}: unknown field {f!r}; it is not in the whitelist of computed fields")
            continue
        fd = FIELDS[f]
        if fd.group == "short_interest" and not short_interest_available:
            p.append(f"{where}: '{f}' refused: short interest unavailable in free data")
            continue
        op = c.get("op")
        if op not in OPS:
            p.append(f"{where}: operator {op!r} not allowed (allowed: {sorted(OPS)})")
            continue
        has_val, has_ref = "value" in c, "ref" in c
        if has_val == has_ref:
            p.append(f"{where}: give exactly one of 'value' (a threshold) or 'ref' (another field)")
            continue
        if fd.kind == "bool":
            if op != "==" or not isinstance(c.get("value"), bool):
                p.append(f"{where}: '{f}' is boolean; use op '==' with value true/false")
            continue
        if op == "==":
            p.append(f"{where}: '==' is only for boolean fields")
            continue
        if has_ref:
            r = c["ref"]
            if r not in FIELDS:
                p.append(f"{where}: unknown ref field {r!r}")
            elif FIELDS[r].kind != fd.kind:
                p.append(f"{where}: cannot compare '{f}' ({fd.kind}) with '{r}' ({FIELDS[r].kind})")
            elif op == "between":
                p.append(f"{where}: 'between' needs a [low, high] value, not a ref")
            continue
        v = c["value"]
        if op == "between":
            if not (isinstance(v, list) and len(v) == 2 and all(_num(x) for x in v) and v[0] < v[1]):
                p.append(f"{where}: 'between' needs value [low, high] with low < high")
                continue
            vals = v
        elif not _num(v):
            p.append(f"{where}: value must be a number, got {v!r}")
            continue
        else:
            vals = [v]
        for x in vals:
            if fd.kind == "ratio" and abs(x) > 20:
                p.append(f"{where}: {f} is a decimal ratio (0.10 = 10%); {x} looks like a percent")
            if f == "rsi14" and not 0 <= x <= 100:
                p.append(f"{where}: rsi14 thresholds must be within 0-100")

    rank = d.get("rank")
    if not isinstance(rank, list) or not rank:
        p.append("'rank' must be a non-empty list of {field, direction, weight}")
        rank = []
    for i, r in enumerate(rank):
        where = f"rank[{i}]"
        if not isinstance(r, dict):
            p.append(f"{where} must be an object")
            continue
        for k in r:
            if k not in RANK_KEYS:
                p.append(f"{where}: unknown key '{k}'")
        if r.get("field") not in FIELDS or FIELDS[r["field"]].kind == "bool":
            p.append(f"{where}: field {r.get('field')!r} is not a rankable whitelisted field")
        elif FIELDS[r["field"]].group == "short_interest" and not short_interest_available:
            p.append(f"{where}: '{r['field']}' refused: short interest unavailable in free data")
        if r.get("direction") not in ("asc", "desc"):
            p.append(f"{where}: direction must be 'asc' or 'desc'")
        w = r.get("weight", 1)
        if not _num(w) or w <= 0:
            p.append(f"{where}: weight must be a positive number")

    top_n = d.get("top_n", 5)
    if not isinstance(top_n, int) or isinstance(top_n, bool) or not 1 <= top_n <= MAX_TOP_N:
        p.append(f"top_n must be an integer 1-{MAX_TOP_N}")

    unm = d.get("unmapped", []) or []
    if not isinstance(unm, list) or not all(isinstance(x, dict) and "text" in x and "reason" in x for x in unm):
        p.append("'unmapped' must be a list of {text, reason}")
        unm = []

    if p:
        raise SpecError(p)
    return Spec(observation=obs.strip(), universe=u, conditions=conds,
                rank=[{"field": r["field"], "direction": r["direction"], "weight": r.get("weight", 1)} for r in rank],
                top_n=top_n, unmapped=unm, notes=str(d.get("notes", "")))


def schema_for_prompt() -> str:
    """Compact human-readable schema handed to the model."""
    lines = ["FIELDS (name | kind | meaning):"]
    for f in FIELDS.values():
        if f.name.startswith("rs_") and not f.name.endswith(("_spy", "_smh")) and not f.name.startswith("rs_3m"):
            continue  # keep the prompt short; the pattern is stated below
        lines.append(f"  {f.name} | {f.kind} | {f.desc}")
    lines.append("  rs_{1,3,6,12}m_vs_{" + ",".join(BENCHMARK_LABELS) + "} | ratio | "
                 "relative return vs that benchmark ETF (" + "; ".join(f"{k}={v}" for k, v in BENCHMARK_LABELS.items()) + ")")
    lines.append("INDUSTRY GROUPS (universe.industries / universe.exclude_industries):")
    for k, (desc, _) in INDUSTRIES.items():
        lines.append(f"  {k}: {desc}")
    lines.append("THEME BASKETS (universe.themes; a name qualifies if it is in ANY listed industry group OR theme):")
    for k, (desc, syms) in THEMES.items():
        lines.append(f"  {k}: {desc} ({', '.join(sorted(syms))})")
    return "\n".join(lines)
