"""Schema validation: valid specs pass, everything outside the whitelist is refused."""

import pytest

from scout.spec import SpecError, validate


def base(**over):
    d = {
        "version": 1,
        "observation": "mid caps down 20% still growing",
        "universe": {"market_cap_min": 2e9, "market_cap_max": 2e10},
        "conditions": [
            {"field": "drawdown_52w", "op": "<=", "value": -0.20, "why": "pulled back 20%+"},
            {"field": "close", "op": ">", "ref": "sma50"},
            {"field": "revenue_growth_yoy", "op": ">", "value": 0.10},
        ],
        "rank": [{"field": "drawdown_52w", "direction": "asc", "weight": 1}],
        "top_n": 5,
        "unmapped": [],
    }
    d.update(over)
    return d


def problems(d, **kw):
    with pytest.raises(SpecError) as e:
        validate(d, **kw)
    return " | ".join(e.value.problems)


def test_valid_spec():
    s = validate(base())
    assert s.top_n == 5 and len(s.conditions) == 3
    assert s.rank[0] == {"field": "drawdown_52w", "direction": "asc", "weight": 1}


def test_unknown_field_refused():
    d = base(conditions=[{"field": "analyst_revisions", "op": ">", "value": 0}])
    assert "unknown field 'analyst_revisions'" in problems(d)


def test_unknown_top_level_key_refused():
    assert "unknown top-level key 'sector_weights'" in problems(base(sector_weights={}))


def test_unknown_condition_key_refused():
    d = base(conditions=[{"field": "rsi14", "op": "<", "value": 30, "lookback": 5}])
    assert "unknown key 'lookback'" in problems(d)


def test_bad_operator_refused():
    assert "operator '!=' not allowed" in problems(base(conditions=[{"field": "rsi14", "op": "!=", "value": 3}]))


def test_percent_instead_of_decimal_refused():
    d = base(conditions=[{"field": "revenue_growth_yoy", "op": ">", "value": 25}])
    assert "looks like a percent" in problems(d)


def test_rsi_out_of_range_refused():
    assert "0-100" in problems(base(conditions=[{"field": "rsi14", "op": "<", "value": 130}]))


def test_value_and_ref_together_refused():
    d = base(conditions=[{"field": "close", "op": ">", "value": 3, "ref": "sma50"}])
    assert "exactly one of 'value'" in problems(d)


def test_ref_kind_mismatch_refused():
    d = base(conditions=[{"field": "close", "op": ">", "ref": "rsi14"}])
    assert "cannot compare 'close' (usd) with 'rsi14' (number)" in problems(d)


def test_bool_field_needs_equality():
    assert validate(base(conditions=[{"field": "sma50_above_sma200", "op": "==", "value": True}]))
    d = base(conditions=[{"field": "sma50_above_sma200", "op": ">", "value": 0}])
    assert "boolean" in problems(d)


def test_between():
    assert validate(base(conditions=[{"field": "rsi14", "op": "between", "value": [30, 50]}]))
    assert "low < high" in problems(base(conditions=[{"field": "rsi14", "op": "between", "value": [50, 30]}]))


def test_unknown_industry_refused():
    d = base(universe={"industries": ["ai_infrastructure"]})
    assert "unknown industry group 'ai_infrastructure'" in problems(d)


def test_market_cap_band_order():
    d = base(universe={"market_cap_min": 2e10, "market_cap_max": 2e9})
    assert "market_cap_min must be below market_cap_max" in problems(d)


def test_short_interest_refused_when_unavailable():
    d = base(conditions=[{"field": "short_pct_shares_out", "op": ">", "value": 0.1}])
    assert validate(d, short_interest_available=True)
    msg = problems(d, short_interest_available=False)
    assert "short interest unavailable in free data" in msg


def test_short_interest_rank_refused_when_unavailable():
    d = base(rank=[{"field": "days_to_cover", "direction": "desc", "weight": 1}])
    assert "short interest unavailable in free data" in problems(d, short_interest_available=False)


def test_all_problems_reported_together():
    d = base(conditions=[{"field": "nope", "op": ">", "value": 1}], top_n=99, rank=[])
    msg = problems(d)
    assert "unknown field 'nope'" in msg and "top_n" in msg and "'rank'" in msg


def test_unmapped_must_be_explained():
    assert "unmapped" in problems(base(unmapped=["insider buying"]))
    s = validate(base(unmapped=[{"text": "insider buying", "reason": "no ownership data"}]))
    assert s.unmapped[0]["text"] == "insider buying"
