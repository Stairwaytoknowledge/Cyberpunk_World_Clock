@echo off
:: World Clock Widget Launcher
:: Double-click this file to start the widget

cd /d "%~dp0"
python main.py

:: If there's an error, pause to see the message
if errorlevel 1 pause
