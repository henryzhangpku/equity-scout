"""The bars request never asks for the newest 15 minutes of SIP data."""
from datetime import date, datetime, timezone

from scout.data.alpaca import _sip_safe_end


def test_past_day_is_sent_as_a_plain_date():
    now = datetime(2026, 10, 21, 18, 0, tzinfo=timezone.utc)
    assert _sip_safe_end(date(2026, 10, 20), now) == "2026-10-20"


def test_today_is_clamped_to_sixteen_minutes_ago():
    now = datetime(2026, 10, 21, 18, 0, tzinfo=timezone.utc)
    assert _sip_safe_end(date(2026, 10, 21), now) == "2026-10-21T17:44:00Z"


def test_a_future_end_is_clamped_too():
    now = datetime(2026, 10, 21, 18, 0, tzinfo=timezone.utc)
    assert _sip_safe_end(date(2026, 10, 25), now) == "2026-10-21T17:44:00Z"
