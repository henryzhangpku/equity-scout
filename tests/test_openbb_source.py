"""OpenBB price adapter against a fake `obb` object (no network, no openbb package needed)."""

import sys
from datetime import date

import pandas as pd
import pytest

from scout import cli
from scout.data.openbb_source import COLUMNS, OpenBBPrices, SourceUnavailable, load_obb
from scout.snapshot import price_source


class FakeResult:
    def __init__(self, df):
        self.df = df

    def to_df(self):
        return self.df.copy()


class FakePrice:
    """Mimics obb.equity.price.historical with yfinance: date index, a symbol column for
    multi-symbol requests, and closes already adjusted when adjustment='splits_and_dividends'."""

    def __init__(self, raw: dict, extra_days: int = 2):
        self.raw, self.extra_days, self.calls = raw, extra_days, []

    def historical(self, symbol, start_date, end_date, interval, adjustment, provider):
        self.calls.append({"symbol": symbol, "start": start_date, "end": end_date, "interval": interval,
                           "adjustment": adjustment, "provider": provider})
        syms = symbol.split(",")
        if "BAD" in syms:
            raise RuntimeError("No results found for BAD")
        frames = []
        for s in syms:
            df = self.raw[s].copy()
            # a careless provider: also sends bars past end_date (the adapter must drop them)
            keep = pd.to_datetime(df["date"]) <= pd.Timestamp(end_date) + pd.Timedelta(days=self.extra_days)
            df = df[keep & (pd.to_datetime(df["date"]) >= pd.Timestamp(start_date))]
            if adjustment == "splits_and_dividends":
                for c in ("open", "high", "low", "close"):
                    df[c] = df[c] * df["adj_factor"]
                df["volume"] = df["volume"] / df["adj_factor"]
            if len(syms) > 1:
                df["symbol"] = s
            frames.append(df.drop(columns="adj_factor"))
        out = pd.concat(frames)
        out["date"] = pd.to_datetime(out["date"]).dt.date
        return FakeResult(out.set_index("date"))


class FakeEquity:
    def __init__(self, price, search_rows):
        self.price, self._rows = price, search_rows

    def search(self, query, provider):
        assert provider == "sec"
        return FakeResult(pd.DataFrame(self._rows))


class FakeObb:
    def __init__(self, raw, search_rows=()):
        self.equity = FakeEquity(FakePrice(raw), list(search_rows))


def _raw(sym_px: dict) -> dict:
    days = pd.bdate_range("2026-09-28", "2026-10-09")
    out = {}
    for s, base in sym_px.items():
        n = len(days)
        out[s] = pd.DataFrame({
            "date": days, "open": base, "high": base + 1.0, "low": base - 1.0, "close": [base + i for i in range(n)],
            "volume": 1000.0, "adj_factor": 0.5, "split_ratio": 0.0, "dividend": 0.0,
        })
    return out


@pytest.fixture
def fake():
    return FakeObb(_raw({"AAA": 10.0, "BRK-B": 100.0, "CCC": 50.0}))


def test_frame_shape_and_columns(fake):
    src = OpenBBPrices("2026-10-08", obb=fake)
    df = src.daily_bars(["AAA", "BRK.B"], date(2026, 9, 28), date(2026, 10, 8))
    assert list(df.columns) == COLUMNS == ["date", "symbol", "open", "high", "low", "close", "volume"]
    assert df["date"].map(type).eq(str).all()
    assert df["date"].iloc[0] == "2026-09-28"
    # sorted by symbol then date, like AlpacaPrices
    assert list(df["symbol"].unique()) == ["AAA", "BRK.B"]
    assert df.groupby("symbol")["date"].apply(lambda d: d.is_monotonic_increasing).all()
    assert len(df) == 2 * 9  # 9 sessions from 28 Sep to 8 Oct inclusive


def test_requests_adjusted_daily_bars_keyless(fake):
    src = OpenBBPrices("2026-10-08", obb=fake)
    df = src.daily_bars(["AAA"], date(2026, 9, 28), date(2026, 10, 8))
    call = fake.equity.price.calls[0]
    assert call == {"symbol": "AAA", "start": "2026-09-28", "end": "2026-10-08", "interval": "1d",
                    "adjustment": "splits_and_dividends", "provider": "yfinance"}
    # raw first close 10.0, adjustment factor 0.5 -> 5.0; volume 1000 / 0.5 = 2000
    first = df.iloc[0]
    assert (first["open"], first["high"], first["low"], first["close"], first["volume"]) == (5.0, 5.5, 4.5, 5.0, 2000.0)


def test_symbol_mapping_and_filtering(fake):
    src = OpenBBPrices("2026-10-08", obb=fake)
    df = src.daily_bars(["BRK.B", "CCC"], date(2026, 9, 28), date(2026, 10, 8))
    assert fake.equity.price.calls[0]["symbol"] == "BRK-B,CCC"   # Yahoo notation on the wire
    assert set(df["symbol"]) == {"BRK.B", "CCC"}                  # caller notation back
    assert "AAA" not in set(df["symbol"])


def test_no_bars_after_end(fake):
    src = OpenBBPrices("2026-10-08", obb=fake)
    end = date(2026, 10, 7)
    df = src.daily_bars(["AAA", "CCC"], date(2026, 9, 28), end)
    assert df["date"].max() == "2026-10-07"
    assert (df["date"] <= end.isoformat()).all()


def test_bad_symbol_does_not_sink_the_batch(fake):
    fake.equity.price.raw["BAD"] = fake.equity.price.raw["AAA"]
    src = OpenBBPrices("2026-10-08", obb=fake)
    df = src.daily_bars(["AAA", "BAD", "CCC"], date(2026, 9, 28), date(2026, 10, 8))
    assert set(df["symbol"]) == {"AAA", "CCC"}
    assert src.failed == ["BAD"]


def test_empty_result_has_the_columns():
    class Empty(FakeObb):
        def __init__(self):
            super().__init__({})
            self.equity.price.historical = lambda **kw: FakeResult(pd.DataFrame())
    df = OpenBBPrices("x", obb=Empty()).daily_bars(["ZZZ"], date(2026, 1, 1), date(2026, 2, 1))
    assert list(df.columns) == COLUMNS and df.empty


def test_universe_from_sec_search():
    rows = [{"symbol": "aaa", "name": "Aaa Inc", "cik": "0000000001"}, {"symbol": "BBB", "name": "Bbb Corp", "cik": 2},
            {"symbol": "AAA", "name": "dup", "cik": 1}, {"symbol": "", "name": "blank", "cik": 3}]
    u = OpenBBPrices("x", obb=FakeObb({}, rows)).universe()
    assert [(s.symbol, s.name, s.cik) for s in u] == [("AAA", "Aaa Inc", 1), ("BBB", "Bbb Corp", 2)]


def test_missing_openbb_is_a_clear_error(monkeypatch):
    monkeypatch.setitem(sys.modules, "openbb", None)   # import openbb -> ImportError
    with pytest.raises(SourceUnavailable, match="uv sync --extra openbb"):
        load_obb()
    with pytest.raises(SourceUnavailable):
        price_source("openbb", "2026-10-08")


def test_cli_build_openbb_without_package_exits_cleanly(monkeypatch, capsys):
    monkeypatch.setitem(sys.modules, "openbb", None)
    with pytest.raises(SystemExit) as e:
        cli.main(["build", "--as-of", "2026-10-08", "--prices", "openbb"])
    msg = str(e.value.code)
    assert msg.startswith("scout build: OpenBB is not installed")
    assert "uv sync --extra openbb" in msg and "Traceback" not in msg


def test_unknown_price_source_refused():
    with pytest.raises(ValueError, match="alpaca or openbb"):
        price_source("terminal", "2026-10-08")
    with pytest.raises(SystemExit):
        cli.main(["build", "--as-of", "2026-10-08", "--prices", "terminal"])
