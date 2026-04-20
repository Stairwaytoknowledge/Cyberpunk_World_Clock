@echo off
rem ============================================================
rem  World Clock - uninstaller
rem
rem  Removes the Desktop and Startup shortcuts and stops any
rem  running instance.  Optionally removes saved settings.
rem
rem  Leaves the install folder itself alone - delete it manually
rem  to free the ~110 MB the bundled runtime takes.
rem ============================================================

setlocal
cd /d "%~dp0"

echo.
echo ===== World Clock Uninstaller =====
echo.

rem -- Stop any running instance launched from THIS install folder.
rem    The widget runs as pythonw.exe; multiple unrelated pythonw
rem    processes may exist on the machine, so filter by ImagePath
rem    (the bundled runtime is unique to this folder).
powershell -NoProfile -Command ^
  "Get-Process pythonw -ErrorAction SilentlyContinue | Where-Object { $_.Path -like '%~dp0runtime\*' } | Stop-Process -Force -ErrorAction SilentlyContinue" >nul 2>&1

for /f "usebackq delims=" %%D in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"`) do set "DESKTOP=%%D"
for /f "usebackq delims=" %%D in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Startup')"`) do set "STARTUP=%%D"
set "DESKTOP_LNK=%DESKTOP%\World Clock.lnk"
set "STARTUP_LNK=%STARTUP%\World Clock.lnk"

if exist "%DESKTOP_LNK%" (
    del /F /Q "%DESKTOP_LNK%"
    echo  - removed Desktop shortcut
)
if exist "%STARTUP_LNK%" (
    del /F /Q "%STARTUP_LNK%"
    echo  - removed Startup shortcut
)

if not exist "config.json" goto done

echo.
choice /C YN /N /M "Also delete your saved settings (cities, window position)? [Y/N] "
if errorlevel 2 goto done
del /F /Q "config.json"
echo  - removed config.json

:done
echo.
echo Done.  To free disk space, delete this folder:
echo    %~dp0
echo.
pause
endlocal
exit /b 0
