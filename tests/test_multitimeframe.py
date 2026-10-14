"""Multi-timeframe technicals: weekly resampling, MACD crosses, weekly RSI, 20-day volume.

Every expected value is worked out by hand in the comments. The sentence these fields exist for:
"RSI under 30 on the daily, MACD crossing above its signal on the weekly, and volume above its
20-day average".
"""

import numpy as np
import pandas as pd
import pytest

from scout import indicators as I
from scout.backtest import Panels, run as backtest_run
from scout.screen import run_screen
from scout.spec import FIELDS, MTF_FIELDS, SpecError, schema_for_prompt, validate
from scout.translate import system_prompt

SENTENCE = ("RSI under 30 on the daily, MACD crossing above its signal on the weekly, "
            "and volume above its 20-day average")
MTF_SPEC = {
    "observation": SENTENCE,
    "conditions": [
        {"field": "rsi14", "op": "<", "value": 30, "why": "RSI under 30 on the daily"},
        {"field": "macd_cross_up_w", "op": "==", "value": True, "why": "MACD crossing above its signal on the weekly"},
        {"field": "volume_ratio_20d", "op": ">", "value": 1, "why": "volume above its 20-day average"},
    ],
    "rank": [{"field": "rsi14", "direction": "asc", "weight": 1}],
    "top_n": 5,
}


def _weekly_days(weekly_closes, last_week_days=5, noise=999.0):
    """Business days Mon-Fri for each week; only the last session of each week carries the weekly
    close, the other sessions carry `noise`, so a wrong resample shows up immediately."""
    dates, closes = [], []
    start = pd.Timestamp("2025-01-06")  # a Monday
    for w, wc in enumerate(weekly_closes):
        n = last_week_days if w == len(weekly_closes) - 1 else 5
        for d in range(n):
            dates.append((start + pd.Timedelta(weeks=w, days=d)).strftime("%Y-%m-%d"))
            closes.append(wc if d == n - 1 else noise)
    return dates, pd.Series(closes)


def test_weekly_close_takes_last_session_and_keeps_partial_week():
    # Mon 28 Sep .. Fri 2 Oct, then Mon 5 .. Wed 7 Oct (as-of on a Wednesday)
    dates = ["2026-09-28", "2026-09-29", "2026-09-30", "2026-10-01", "2026-10-02",
             "2026-10-05", "2026-10-06", "2026-10-07"]
    w = I.weekly_close(dates, pd.Series([1, 2, 3, 4, 5, 6, 7, 8], dtype=float))
    assert list(w.index) == ["2026-10-02", "2026-10-07"]
    assert list(w) == [5.0, 8.0]                     # Friday close; partial week ends at the as-of bar


def test_weekly_close_holiday_friday_uses_thursday():
    dates = ["2026-11-23", "2026-11-24", "2026-11-25", "2026-11-26",   # Fri 27 Nov missing
             "2026-11-30"]
    w = I.weekly_close(dates, pd.Series([10, 11, 12, 13, 20], dtype=float))
    assert list(w.index) == ["2026-11-26", "2026-11-30"]
    assert list(w) == [13.0, 20.0]


def test_weekly_close_is_point_in_time():
    # truncating at a date gives exactly the weekly bars knowable on that date
    dates, c = _weekly_days([10.0, 11.0, 12.0])
    full = I.weekly_close(dates, c)
    cut = I.weekly_close(dates[:12], c.iloc[:12])    # Tuesday of week 3
    assert list(full) == [10.0, 11.0, 12.0]
    assert list(cut) == [10.0, 11.0, 999.0]          # the partial week ends at Tuesday
    assert cut.index[-1] == dates[11]


def test_crossed_above():
    assert I.crossed_above(pd.Series([-1.0, 0.5])) is True
    assert I.crossed_above(pd.Series([0.0, 0.5])) is True    # from exactly zero counts
    assert I.crossed_above(pd.Series([0.5, 1.0])) is False   # already above: not a cross
    assert I.crossed_above(pd.Series([-1.0, -0.5])) is False
    assert I.crossed_above(pd.Series([0.5, -0.5])) is False  # crossing down
    assert I.crossed_above(pd.Series([np.nan, 1.0])) is None
    assert I.crossed_above(pd.Series([1.0])) is None


def test_weekly_macd_cross_by_hand():
    # 35 flat weeks at 100, then 110: every EMA is 100 up to the last week, so hist = 0 the week before.
    # Last week: EMA12 = 100 + 10 * 2/13, EMA26 = 100 + 10 * 2/27, MACD = 10 * (2/13 - 2/27) = 280/351;
    # signal = 0.2 * MACD (alpha 2/10, previous signal 0); hist = 0.8 * MACD = 224/351 = 0.638177...
    dates, c = _weekly_days([100.0] * 35 + [110.0], last_week_days=3)
    f = I.weekly_fields(dates, c)
    assert f["macd_hist_w"] == pytest.approx(224 / 351, abs=1e-12)
    assert f["macd_cross_up_w"] is True
    dates, c = _weekly_days([100.0] * 35 + [90.0])
    f = I.weekly_fields(dates, c)
    assert f["macd_hist_w"] == pytest.approx(-224 / 351, abs=1e-12)
    assert f["macd_cross_up_w"] is False


def test_weekly_macd_needs_35_weeks():
    dates, c = _weekly_days([100.0] * 33 + [110.0])  # 34 weeks
    f = I.weekly_fields(dates, c)
    assert np.isnan(f["macd_hist_w"]) and f["macd_cross_up_w"] is None


def test_weekly_rsi_by_hand():
    # weekly closes 1..14 then 13: 14 changes = thirteen +1 and one -1.
    # avg gain 13/14, avg loss 1/14, RS = 13, RSI = 100 - 100/14 = 92.857...
    dates, c = _weekly_days([float(x) for x in range(1, 15)] + [13.0])
    f = I.weekly_fields(dates, c)
    assert f["rsi14_w"] == pytest.approx(100 - 100 / 14, abs=1e-12)
    dates, c = _weekly_days([float(x) for x in range(1, 15)])          # only 14 weeks: no RSI(14)
    assert np.isnan(I.weekly_fields(dates, c)["rsi14_w"])


def test_daily_macd_cross_and_volume_20d_in_snapshot():
    # 60 flat sessions at 50 then 55: same algebra as the weekly case on daily bars
    n = 61
    dates = pd.bdate_range("2026-01-01", periods=n).strftime("%Y-%m-%d")
    close = pd.Series([50.0] * (n - 1) + [55.0])
    volume = pd.Series([100.0] * (n - 1) + [300.0])
    s = I.snapshot(pd.DataFrame({"date": dates, "close": close, "volume": volume}))
    assert s["macd_hist"] == pytest.approx(0.8 * 5 * (2 / 13 - 2 / 27), abs=1e-12)
    assert s["macd_cross_up"] is True
    assert s["volume_ratio_20d"] == pytest.approx(3.0)      # 300 / mean of the prior 20 sessions (100)
    assert s["volume_ratio_50d"] == pytest.approx(3.0)
    for k in ("rsi14_w", "macd_hist_w", "macd_cross_up_w"):
        assert k in s
    assert s["macd_cross_up_w"] is None                     # 13 weeks of history: not enough


def test_volume_ratio_20d_window():
    v = pd.Series([float(x) for x in range(1, 22)])          # 1..20 then 21
    assert I.volume_ratio(v, 20).iloc[-1] == pytest.approx(21 / 10.5)   # mean(1..20) = 10.5


def test_sentence_maps_to_a_valid_spec():
    spec = validate(MTF_SPEC)
    assert [c["field"] for c in spec.conditions] == ["rsi14", "macd_cross_up_w", "volume_ratio_20d"]
    assert FIELDS["macd_cross_up_w"].kind == "bool" and FIELDS["volume_ratio_20d"].kind == "number"


def test_weekly_rsi_range_checked():
    bad = dict(MTF_SPEC, conditions=[{"field": "rsi14_w", "op": "<", "value": 130}])
    with pytest.raises(SpecError, match="rsi14_w thresholds must be within 0-100"):
        validate(bad)


def _frame():
    rows = [  # symbol, rsi14, weekly cross, volume ratio 20d
        ("AAA", 25.0, True, 1.5),     # passes all three
        ("BBB", 28.0, True, 0.8),     # volume too low
        ("CCC", 40.0, True, 2.0),     # RSI too high
        ("DDD", 20.0, False, 3.0),    # no weekly cross
        ("EEE", 22.0, None, 1.2),     # weekly MACD unknown -> missing
        ("FFF", 15.0, True, 1.1),     # passes
    ]
    return pd.DataFrame({"symbol": [r[0] for r in rows], "name": [r[0] for r in rows],
                         "sic": 3674, "market_cap": 1e10, "close": 10.0, "avg_dollar_volume_50d": 1e7,
                         "rsi14": [r[1] for r in rows], "macd_cross_up_w": [r[2] for r in rows],
                         "volume_ratio_20d": [r[3] for r in rows]})


def test_screen_funnel_on_hand_built_universe():
    funnel, surv = run_screen(_frame(), validate(MTF_SPEC))
    steps = [(s["n_in"], s["n_pass"], s["n_fail"], s["n_missing"]) for s in funnel[1:]]
    assert steps == [(6, 5, 1, 0),      # rsi14 < 30 drops CCC
                     (5, 3, 1, 1),      # weekly cross: DDD fails, EEE missing
                     (3, 2, 1, 0)]      # volume ratio > 1 drops BBB
    assert sorted(surv["symbol"]) == ["AAA", "FFF"]


def test_old_snapshot_without_the_column_is_refused_clearly():
    old = _frame().drop(columns=["macd_cross_up_w", "volume_ratio_20d"])
    with pytest.raises(SpecError) as e:
        run_screen(old, validate(MTF_SPEC))
    assert e.value.problems == [
        f"'{f}' is not in this feature snapshot (it was built before the field existed); "
        "rebuild the snapshot with `scout build` to screen on it" for f in ["macd_cross_up_w", "volume_ratio_20d"]]


def test_backtest_refuses_fields_not_in_panels():
    P = Panels(dates=["2026-01-30", "2026-02-27"], symbols=np.array(["AAA"]), fields=["rsi14"],
               values=np.zeros((2, 1, 1), dtype=np.float32), close_at=None, last_close=None, last_date=None,
               in_universe=None, names=None, sic=None, spy_close=None, check_date=[], check_values=None,
               check_universe=None)
    with pytest.raises(SpecError, match="multi-timeframe fields were added after the panels were built"):
        backtest_run(validate(MTF_SPEC), P)


def test_recorded_prompt_versions_do_not_mention_new_fields():
    # versions 1 and 2 are the exact texts the recordings hash; the new fields appear only in version 3
    for v in (1, 2):
        text = system_prompt(v)
        assert not any(f in text for f in MTF_FIELDS) and "TIMEFRAMES" not in text
    v3 = schema_for_prompt(3)
    assert all(f in v3 for f in MTF_FIELDS) and "TIMEFRAMES" in v3


# ---------- the committed 2026-10-08 snapshot, with the fields added from its own cached bars ----------

def _with_rsi_below(level):
    spec = {**MTF_SPEC, "conditions": [dict(c) for c in MTF_SPEC["conditions"]]}
    spec["conditions"][0]["value"] = level
    return spec


def test_added_fields_leave_the_cited_snapshot_files_untouched():
    import hashlib
    import json
    from scout.pipeline import ADDED_FEATURES, ADDED_MANIFEST, SNAPSHOTS
    d = SNAPSHOTS / "2026-10-08"
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()  # noqa: E731
    added, manifest = json.loads((d / ADDED_MANIFEST).read_text()), json.loads((d / "manifest.json").read_text())
    assert added["source"]["features.csv.gz"] == manifest["files"]["features.csv.gz"]
    assert sha(d / "features.csv.gz") == manifest["files"]["features.csv.gz"]["sha256"]  # what the recorded runs cite
    assert sha(d / ADDED_FEATURES) == added["files"][ADDED_FEATURES]["sha256"]
    assert added["fields"] == list(MTF_FIELDS)


def test_mtf_spec_runs_on_the_snapshot():
    from scout import mcp_tools as t
    from scout.pipeline import load_features
    features, _ = load_features("2026-10-08")
    assert all(f in features.columns for f in MTF_FIELDS) and len(features) == 3827
    out = t.run_screen_tool(MTF_SPEC, as_of="2026-10-08")
    assert out["ok"] is True
    assert [(f["entered"], f["passed"], f["failed"], f["no_data"]) for f in out["funnel"]] == \
        [(3827, 3827, 0, 0), (3827, 333, 3494, 0), (333, 0, 323, 10), (0, 0, 0, 0)]
    loose = t.run_screen_tool(_with_rsi_below(45), as_of="2026-10-08")
    assert [f["passed"] for f in loose["funnel"]] == [3827, 1986, 5, 3]
    assert [r["symbol"] for r in loose["top"]] == ["VXX", "ERII", "SOC"]


def test_cli_screen_prints_the_same_funnel(tmp_path, capsys):
    import json
    from scout.cli import main
    p = tmp_path / "spec.json"
    p.write_text(json.dumps(_with_rsi_below(45)))
    main(["screen", str(p), "--as-of", "2026-10-08"])
    out = capsys.readouterr().out
    assert "rsi14 < 45" in out and "Ranked survivors (3)" in out
    assert [line.split()[1] for line in out.splitlines() if line.strip()[:1].isdigit()] == ["VXX", "ERII", "SOC"]
