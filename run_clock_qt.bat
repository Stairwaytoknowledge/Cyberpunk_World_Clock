@echo off
:: World Clock Widget (PyQt6 Version with Real Blur Effects)
:: Double-click this file to start the widget

cd /d "%~dp0"
python main_qt.py

:: If there's an error, pause to see the message
if errorlevel 1 pause
