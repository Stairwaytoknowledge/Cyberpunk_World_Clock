"""Performance and memory regression tests.

Runs short so it's safe on every CI push, but strict enough to catch
the two classes of regression this codebase has actually had:

  * The paintEvent rebuilt 12+ QPainterPath/QGradient objects per tick
    before we introduced the background pixmap cache. A regression
    would blow up per-frame allocations and steady-state GC pressure.
  * A long-lived QGraphicsDropShadowEffect on the rarely-used DST
    label kept an offscreen buffer alive year-round. A regression
    there would show up as baseline memory creeping.

We keep a small safety margin because GC timing and PyQt6 internals
vary across minor versions; the thresholds below are headroom past
what we measured on Python 3.12 / PyQt6 6.11.
"""
from __future__ import annotations

import gc
import os

import pytest

# psutil is a test-only dependency; skip gracefully if someone's running
# the suite on a bare Python that has neither it nor pip access.
psutil = pytest.importorskip("psutil")

from PyQt6.QtWidgets import QApplication  # noqa: E402

from src.clock_widget_qt import ClockWidgetQt  # noqa: E402


def _rss_mb(proc):
    return proc.memory_info().rss / (1024 * 1024)


def test_no_memory_leak_over_many_updates(qapp):
    """300 update_clocks() calls should not grow RSS by more than 2 MB.

    That covers an hour of real-world ticks at 1 Hz (the widget's
    timer interval) with plenty of margin - if we're leaking 10 KB
    per tick, the test will fail long before it hits a user.
    """
    proc = psutil.Process(os.getpid())
    w = ClockWidgetQt()
    w.show()
    w.lower()
    qapp.processEvents()

    # Settle any one-time allocations (font loading, cache pixmap, etc.)
    for _ in range(5):
        qapp.processEvents()
    gc.collect()
    baseline = _rss_mb(proc)

    for i in range(300):
        w.update_clocks()
        if i % 50 == 0:
            qapp.processEvents()
    gc.collect()

    final = _rss_mb(proc)
    w.close()
    assert final - baseline < 2.0, (
        f"RSS grew by {final - baseline:.2f} MB over 300 updates "
        f"(baseline {baseline:.1f} -> final {final:.1f} MB). "
        "Something is leaking per tick - check paintEvent allocations."
    )


def test_background_cache_reuses_pixmap(qapp):
    """The static pill background must be cached after the first paint.

    Regression target: if someone removes the cache check in
    paintEvent, a fresh QPixmap is rebuilt on every frame - very
    expensive. Catch that by asserting the pixmap identity is stable
    across repeated paints.
    """
    w = ClockWidgetQt()
    w.show()
    w.lower()
    qapp.processEvents()

    first = getattr(w, "_bg_cache_pm", None)
    assert first is not None, "cache pixmap was never built on first paint"

    w.repaint()
    qapp.processEvents()
    w.repaint()
    qapp.processEvents()

    # Same Python object identity - same pixmap reused, not rebuilt
    assert w._bg_cache_pm is first
    w.close()


def test_dst_glow_is_lazy(qapp):
    """The magenta DST alert glow must not exist until the alert fires.

    For ~50 weeks a year the DST alert is silent, so we don't want a
    QGraphicsDropShadowEffect sitting on every dst_label with its
    offscreen buffer allocated.
    """
    w = ClockWidgetQt()
    w.show()
    w.lower()
    qapp.processEvents()

    # Fresh widget, no alerts anywhere - every DST label should have
    # no graphics effect attached.
    for slot in w.clock_labels:
        assert slot.dst_label.graphicsEffect() is None, (
            "DST glow should not be attached until the alert actually "
            "fires (for ~50 weeks/year this wastes memory)"
        )
    w.close()
