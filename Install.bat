@echo off
rem ============================================================
rem  World Clock - one-click installer (self-contained)
rem
rem  No internet, no Python install, no dependencies.
rem  Everything World Clock needs is already inside this folder.
rem
rem  All this script does:
rem    1. Verify the bundled runtime is present
rem    2. Drop a "World Clock" shortcut on your Desktop
rem    3. Optionally add it to Startup
rem    4. Optionally launch it now
rem ============================================================

setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ===== World Clock Installer =====
echo.

if not exist "runtime\pythonw.exe" (
    echo  ! This installer expects a self-contained build.
    echo    Did you extract the entire WorldClock-vX.Y.Z folder?
    echo    The folder must contain a "runtime" subfolder with pythonw.exe.
    echo.
    pause & exit /b 1
)

rem ---- Resolve the REAL Desktop / Startup folders ----
rem  On many machines (OneDrive-backed profiles, custom shell folders) the
rem  paths %USERPROFILE%\Desktop and %APPDATA%\...\Startup do not exist -
rem  the actual locations are reported by SHGetFolderPath.
for /f "usebackq delims=" %%D in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Desktop')"`) do set "DESKTOP=%%D"
for /f "usebackq delims=" %%D in (`powershell -NoProfile -Command "[Environment]::GetFolderPath('Startup')"`) do set "STARTUP=%%D"

set "VBS=%~dp0Launch.vbs"
set "ICON=%~dp0assets\icon.ico"
set "SHORTCUT=%DESKTOP%\World Clock.lnk"

echo Creating Desktop shortcut: %SHORTCUT%
powershell -NoProfile -Command ^
  "$s = (New-Object -ComObject WScript.Shell).CreateShortcut('%SHORTCUT%');" ^
  "$s.TargetPath = 'wscript.exe';" ^
  "$s.Arguments  = '\"%VBS%\"';" ^
  "$s.WorkingDirectory = '%~dp0';" ^
  "$s.IconLocation = '%ICON%,0';" ^
  "$s.Description  = 'World Clock - desktop widget';" ^
  "$s.Save()"

if not exist "%SHORTCUT%" (
    echo  ! Could not create the Desktop shortcut.
    echo    Make sure your account can write to %DESKTOP%.
    pause & exit /b 1
)

echo.
choice /C YN /N /M "Launch World Clock when Windows starts? [Y/N] "
if errorlevel 2 goto skip_autostart
copy /Y "%SHORTCUT%" "%STARTUP%\World Clock.lnk" >nul
echo  - Added to Startup folder.
:skip_autostart

echo.
choice /C YN /N /M "Launch World Clock right now? [Y/N] "
if errorlevel 2 goto skip_launch
start "" wscript.exe "%VBS%"
:skip_launch

echo.
echo ============================================================
echo  Done.  Double-click "World Clock" on your Desktop any time.
echo  To remove, run Uninstall.bat in this folder.
echo ============================================================
echo.
pause
endlocal
exit /b 0
