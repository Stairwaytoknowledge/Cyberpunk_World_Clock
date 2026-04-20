"""End-to-end smoke tests for the PyQt6 widget.

These tests are what the old release.yml smoke step did inline: they
construct the widget, process paint events, and fail loudly if Qt
reports a fatal message. Kept in pytest so they run on every push, not
only on tag pushes, and so contributors get immediate local feedback
via `pytest`.

Runs headless via QT_QPA_PLATFORM=offscreen (set in conftest.py).
"""
from __future__ import annotations

import os
from typing import List

import pytest
from PyQt6.QtCore import QTimer, QtMsgType, qInstallMessageHandler
from PyQt6.QtGui import QPixmap, QPainter

from src.clock_widget_qt import MAX_CITIES, MIN_CITIES, ClockWidgetQt


# ---- Helpers -------------------------------------------------------------


def _fatal_collector() -> List[str]:
    """Install a Qt message handler that collects fatal messages into a
    list. Returning the list lets the test assert it is empty.

    Using a closure here (rather than a bare list that gets garbage-
    collected) is important because Qt keeps the callback on the C++
    side, so `bucket` must stay reachable for the lifetime of the
    QApplication.
    """
    bucket: List[str] = []

    def handler(mode, context, message):
        if mode == QtMsgType.QtFatalMsg:
            bucket.append(str(message))

    qInstallMessageHandler(handler)
    return bucket


# ---- Tests ---------------------------------------------------------------


def test_widget_constructs_with_default_cities(qapp):
    fatal = _fatal_collector()
    w = ClockWidgetQt()
    assert len(w.cities) == MIN_CITIES
    # Size is fixed by setup_window
    assert w.width() == 920
    assert w.height() == 110
    w.close()
    assert fatal == [], f"Qt fatal during construction: {fatal}"


def test_widget_paints_without_fatal(qapp):
    """Constructing is not enough - paintEvent runs only on show().
    A bug like the old QPoint-vs-QPointF mismatch would only fire here."""
    fatal = _fatal_collector()
    w = ClockWidgetQt()
    w.show()
    w.lower()
    # Force the event loop to dispatch paint events
    qapp.processEvents()
    qapp.processEvents()
    # Render explicitly to provoke another paint
    pm = QPixmap(w.size())
    painter = QPainter(pm)
    w.render(painter)
    painter.end()
    w.close()
    assert fatal == [], f"Qt fatal during paint: {fatal}"


@pytest.mark.parametrize("n", [4, 5, 6])
def test_widget_supports_4_to_6_cities(qapp, n):
    fatal = _fatal_collector()
    w = ClockWidgetQt()
    # Grow to n without invoking the modal picker dialog.
    while len(w.cities) < n:
        w.cities.append({"name": "Dubai", "timezone": "Asia/Dubai"})
    w._rebuild_clock_row()
    w.update_clocks()
    w.show()
    w.lower()
    qapp.processEvents()
    assert len(w.clock_labels) == n
    w.close()
    assert fatal == [], f"Qt fatal at {n} cities: {fatal}"


def test_widget_clamps_overflowing_city_count(qapp, monkeypatch):
    """A hand-edited config with 12 cities must not blow up the layout;
    the widget clamps to MAX_CITIES."""
    from src import clock_widget_qt as mod

    big_cfg = {
        "cities": [{"name": f"C{i}", "timezone": "UTC"} for i in range(12)],
        "window_position": {"x": None, "y": None},
        "opacity": 0.92,
        "always_on_top": False,
    }
    monkeypatch.setattr(mod.ConfigManager, "load_config", lambda self: big_cfg)
    w = ClockWidgetQt()
    assert len(w.cities) == MAX_CITIES
    w.close()


def test_widget_pads_short_city_count(qapp, monkeypatch):
    """Likewise, a 2-city config must be padded up to MIN_CITIES so the
    layout never has an empty slot."""
    from src import clock_widget_qt as mod

    short_cfg = {
        "cities": [{"name": "A", "timezone": "UTC"}],
        "window_position": {"x": None, "y": None},
        "opacity": 0.92,
        "always_on_top": False,
    }
    monkeypatch.setattr(mod.ConfigManager, "load_config", lambda self: short_cfg)
    w = ClockWidgetQt()
    assert len(w.cities) >= MIN_CITIES
    w.close()


def test_update_clocks_fills_time_strings(qapp):
    fatal = _fatal_collector()
    w = ClockWidgetQt()
    w.update_clocks()
    # Each slot should have an HH:MM:SS-shaped label now
    for slot in w.clock_labels:
        text = slot.time_label.text()
        assert len(text) == 8 and text[2] == ":" and text[5] == ":"
    w.close()
    assert fatal == []


def test_bundled_font_loads(qapp):
    """If assets/fonts/Orbitron-*.ttf exists it must register with Qt;
    otherwise the widget still renders but falls back to a system font."""
    from PyQt6.QtGui import QFontDatabase

    from src.clock_widget_qt import _load_bundled_font

    _load_bundled_font()
    families = QFontDatabase.families()
    # In the release bundle and dev checkout Orbitron should be present.
    # If someone strips assets/fonts we don't want to fail the whole
    # test suite - just skip this assertion.
    if not os.path.exists("assets/fonts/Orbitron-VariableFont_wght.ttf"):
        pytest.skip("Orbitron not in checkout (assets/fonts/ stripped)")
    assert "Orbitron" in families
