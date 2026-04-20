#!/usr/bin/env python3
"""
World Clock Widget - Floating desktop widget for Windows 11
Displays time for 4 cities with automatic timezone conversion and DST support
"""

from src.clock_widget import ClockWidget

def main():
    """Main entry point for the application."""
    app = ClockWidget()
    app.run()

if __name__ == "__main__":
    main()
