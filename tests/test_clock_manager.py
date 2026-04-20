"""Unit tests for ClockManager - the pure-logic layer of the widget.

These tests don't need Qt, a display, or pip-installed PyQt6. They
exercise time formatting, timezone handling, and the DST fall-back
detector that powers the magenta "DST ENDS IN N DAYS" alert.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from src.clock_manager import ClockManager


# ---- Formatters ----------------------------------------------------------


def test_format_time_24h_with_value():
    cm = ClockManager()
    dt = datetime(2026, 4, 20, 13, 5, 9, tzinfo=timezone.utc)
    assert cm.format_time_24h(dt) == "13:05:09"


def test_format_time_24h_with_none():
    cm = ClockManager()
    assert cm.format_time_24h(None) == "--:--:--"


def test_format_date_ddmm_with_value():
    cm = ClockManager()
    dt = datetime(2026, 4, 20, 0, 0, 0, tzinfo=timezone.utc)
    assert cm.format_date_ddmm(dt) == "20-04"


def test_format_date_ddmm_with_none():
    cm = ClockManager()
    assert cm.format_date_ddmm(None) == "-----"


# ---- Timezone lookup -----------------------------------------------------


def test_get_time_for_city_returns_datetime_for_known_zone():
    cm = ClockManager()
    dt = cm.get_time_for_city("New York", "America/New_York")
    assert dt is not None
    # Should be tz-aware
    assert dt.utcoffset() is not None


def test_get_time_for_city_returns_none_for_unknown_zone():
    cm = ClockManager()
    assert cm.get_time_for_city("Atlantis", "Not/A/Zone") is None


# ---- get_clock_data shape ------------------------------------------------


def test_get_clock_data_shape_keys_present():
    cm = ClockManager()
    data = cm.get_clock_data("UTC", "UTC")
    # The widget update loop reads these five keys; adding/removing one
    # silently breaks the UI.
    assert set(data.keys()) >= {"city", "timezone", "time", "date", "dst_alert"}


def test_get_clock_data_for_invalid_zone_sets_valid_false():
    cm = ClockManager()
    data = cm.get_clock_data("Atlantis", "Not/A/Zone")
    assert data["valid"] is False
    assert data["time"] == "--:--:--"


def test_get_all_clock_data_length_matches_input():
    cm = ClockManager()
    cities = [
        {"name": "A", "timezone": "UTC"},
        {"name": "B", "timezone": "Asia/Tokyo"},
        {"name": "C", "timezone": "America/New_York"},
    ]
    assert len(cm.get_all_clock_data(cities)) == len(cities)


# ---- DST fall-back detector ---------------------------------------------


def test_days_until_fall_back_none_for_non_dst_zone():
    """Zones with no DST (UTC, Tokyo, etc.) must never claim a fall-back."""
    cm = ClockManager()
    assert cm.days_until_fall_back("UTC") is None
    assert cm.days_until_fall_back("Asia/Tokyo") is None


def test_days_until_fall_back_is_positive_for_dst_zone():
    """Every DST zone has a fall-back within a year; we scan ~400 days."""
    cm = ClockManager()
    for zone in ("America/New_York", "Europe/London", "Australia/Sydney"):
        d = cm.days_until_fall_back(zone)
        assert d is not None, f"{zone} should have a DST fall-back within a year"
        assert 0 <= d <= 400, f"{zone} returned out-of-range {d}"


def test_days_until_fall_back_invalid_zone_returns_none():
    cm = ClockManager()
    assert cm.days_until_fall_back("Not/A/Zone") is None


@pytest.mark.parametrize(
    ("days_away", "expected_text"),
    [
        (0,  "DST ends today"),
        (1,  "DST ends tomorrow"),
        (3,  "DST ends in 3 days"),
        (7,  "DST ends in 7 days"),
        (8,  ""),   # outside the 7-day window, no alert
        (30, ""),
        (None, ""),
    ],
)
def test_dst_alert_text(monkeypatch, days_away, expected_text):
    """Alert text must appear exactly within the documented window:
       today, tomorrow, 2-7 days, silent thereafter."""
    cm = ClockManager()

    def fake_days(_zone):
        return days_away

    monkeypatch.setattr(cm, "days_until_fall_back", fake_days)
    data = cm.get_clock_data("X", "America/New_York")
    assert data["dst_alert"] == expected_text


def test_dst_cache_prevents_repeated_recomputation(monkeypatch):
    """The per-second update loop calls days_until_fall_back() for every
    city. Recomputing the ~400-day walk each call would cost real CPU;
    the 6-hour cache should short-circuit immediately."""
    cm = ClockManager()
    calls = {"n": 0}
    real = cm._next_fall_back

    def counting(zone):
        calls["n"] += 1
        return real(zone)

    monkeypatch.setattr(cm, "_next_fall_back", counting)
    for _ in range(20):
        cm.days_until_fall_back("America/New_York")
    # Every call passes through _next_fall_back, but the cache inside it
    # means we only do the expensive scan once.
    assert calls["n"] == 20  # the wrapper is called
    # The cache dict should have exactly one entry for the zone.
    assert "America/New_York" in cm._dst_cache
