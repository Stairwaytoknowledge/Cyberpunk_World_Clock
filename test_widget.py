#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify World Clock Widget functionality
"""

import sys
import io

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_imports():
    """Test that all modules import correctly."""
    print("Testing imports...")
    try:
        from src.clock_manager import ClockManager
        print("  [OK] ClockManager imported")

        from src.config_manager import ConfigManager
        print("  [OK] ConfigManager imported")

        from src.city_selector import CitySelector
        print("  [OK] CitySelector imported")

        from src.clock_widget import ClockWidget
        print("  [OK] ClockWidget imported")

        return True
    except Exception as e:
        print(f"  [FAIL] Import failed: {e}")
        return False

def test_clock_manager():
    """Test clock manager functionality."""
    print("\nTesting ClockManager...")
    try:
        from src.clock_manager import ClockManager
        cm = ClockManager()

        # Test single city
        data = cm.get_clock_data("Tokyo", "Asia/Tokyo")
        assert data["city"] == "Tokyo", "City name mismatch"
        assert data["valid"] == True, "Clock data should be valid"
        assert len(data["time"]) == 8, "Time format should be HH:MM:SS"
        assert len(data["date"]) == 5, "Date format should be DD-MM"
        print(f"  [OK] Single city test passed (Tokyo: {data['time']} {data['date']})")

        # Test multiple cities
        cities = [
            {"name": "New York", "timezone": "America/New_York"},
            {"name": "London", "timezone": "Europe/London"},
            {"name": "Tokyo", "timezone": "Asia/Tokyo"},
            {"name": "Sydney", "timezone": "Australia/Sydney"}
        ]
        all_data = cm.get_all_clock_data(cities)
        assert len(all_data) == 4, "Should return 4 clock data"
        print(f"  [OK] Multiple cities test passed ({len(all_data)} cities)")

        return True
    except Exception as e:
        print(f"  [FAIL] ClockManager test failed: {e}")
        return False

def test_config_manager():
    """Test config manager functionality."""
    print("\nTesting ConfigManager...")
    try:
        from src.config_manager import ConfigManager
        cm = ConfigManager("test_config.json")

        # Test load default
        config = cm.load_config()
        assert "cities" in config, "Config should have cities"
        assert "window_position" in config, "Config should have window_position"
        assert "opacity" in config, "Config should have opacity"
        assert "always_on_top" in config, "Config should have always_on_top"
        assert config["always_on_top"] == False, "always_on_top should be False"
        assert config["opacity"] == 0.92, "opacity should be 0.92"
        print(f"  [OK] Config load test passed (opacity: {config['opacity']})")

        # Test save
        config["test_key"] = "test_value"
        cm.save_config(config)
        print("  [OK] Config save test passed")

        # Clean up test file
        import os
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")

        return True
    except Exception as e:
        print(f"  [FAIL] ConfigManager test failed: {e}")
        return False

def test_cities_data():
    """Test cities.json data."""
    print("\nTesting cities.json...")
    try:
        import json
        with open("assets/cities.json", "r", encoding="utf-8") as f:
            cities = json.load(f)

        assert len(cities) > 100, "Should have 100+ cities"
        assert "New York" in cities, "Should include New York"
        assert "London" in cities, "Should include London"
        assert "Tokyo" in cities, "Should include Tokyo"
        assert "Sydney" in cities, "Should include Sydney"

        print(f"  [OK] Cities data valid ({len(cities)} cities available)")
        return True
    except Exception as e:
        print(f"  [FAIL] Cities data test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("="*60)
    print("World Clock Widget - Comprehensive Test Suite")
    print("="*60)

    results = []
    results.append(("Imports", test_imports()))
    results.append(("ClockManager", test_clock_manager()))
    results.append(("ConfigManager", test_config_manager()))
    results.append(("Cities Data", test_cities_data()))

    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "[PASSED]" if result else "[FAILED]"
        print(f"{name:20s}: {status}")

    print("="*60)
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed! Widget is ready to use.")
        print("\nTo run the widget:")
        print("  python main.py")
        print("  or double-click: run_clock.bat")
        return 0
    else:
        print("\n[WARNING] Some tests failed. Please review errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
