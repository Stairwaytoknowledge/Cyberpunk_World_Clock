"""Unit tests for ConfigManager - JSON load/save with graceful degradation."""
from __future__ import annotations

import json

import pytest

from src.config_manager import ConfigManager


def test_load_returns_defaults_when_file_missing(tmp_path):
    cfg = ConfigManager(config_path=str(tmp_path / "does-not-exist.json"))
    data = cfg.load_config()
    assert len(data["cities"]) == 4
    assert data["window_position"] == {"x": None, "y": None}


def test_load_merges_with_defaults_when_partial(tmp_path):
    """A config written by an older version (missing keys) must still
    load cleanly - new keys come from the defaults."""
    p = tmp_path / "config.json"
    p.write_text(json.dumps({"cities": [{"name": "X", "timezone": "UTC"}]}))
    cfg = ConfigManager(config_path=str(p))
    data = cfg.load_config()
    assert data["cities"] == [{"name": "X", "timezone": "UTC"}]
    # Default keys filled in
    assert "window_position" in data
    assert "opacity" in data


def test_load_falls_back_to_defaults_on_corrupt_json(tmp_path):
    p = tmp_path / "config.json"
    p.write_text("{not valid json")
    cfg = ConfigManager(config_path=str(p))
    data = cfg.load_config()
    assert len(data["cities"]) == 4  # defaults


def test_save_then_load_roundtrip(tmp_path):
    p = tmp_path / "config.json"
    cfg = ConfigManager(config_path=str(p))
    original = cfg.load_config()
    original["window_position"] = {"x": 123, "y": 456}
    original["cities"].append({"name": "Dubai", "timezone": "Asia/Dubai"})
    cfg.save_config(original)
    again = cfg.load_config()
    assert again["window_position"] == {"x": 123, "y": 456}
    assert len(again["cities"]) == 5


def test_default_cities_are_a_copy_not_a_reference():
    """get_default_cities() must not expose the internal default list -
    a caller mutating the result must not affect subsequent loads."""
    cfg = ConfigManager()
    a = cfg.get_default_cities()
    a.append({"name": "Foo", "timezone": "UTC"})
    b = cfg.get_default_cities()
    assert len(b) == 4
