"""Shared pytest fixtures.

Why we need a fixture for QApplication:
  Qt refuses to create widgets without a running QApplication, but it
  ALSO refuses to create a second one in the same process. A session-
  scoped fixture is the only reliable way to share one across tests.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Let the tests import `src.*` and `main_qt` whether pytest is run from
# the repo root or from tests/.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Qt on headless CI (no display) needs the offscreen platform plugin.
# Setting this env var BEFORE QApplication is imported is mandatory.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="session")
def qapp():
    """Module-wide QApplication so widget tests can instantiate widgets."""
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication(sys.argv)
    yield app
    # Don't call app.quit() - pytest will exit the process anyway and
    # Qt cleanup is flaky across test runners.
