@echo off
rem ============================================================
rem  Creates a clickable "World Clock.lnk" in this folder, with
rem  the clock icon, pointing at Launch.vbs so there is no console
rem  flash on launch.
rem
rem  Run this ONCE after cloning the repo. Afterwards, just
rem  double-click the "World Clock" icon any time to run the app.
rem
rem  End users who install via the release zip do NOT need this -
rem  Install.bat already puts a shortcut on their Desktop.
rem ============================================================

setlocal
cd /d "%~dp0"

if not exist "assets\icon.ico" (
    echo Icon not found.  Run the icon generator once:
    echo     python build\generate_icons.py
    pause & exit /b 1
)

set "SHORTCUT=%~dp0World Clock.lnk"

powershell -NoProfile -Command ^
  "$s = (New-Object -ComObject WScript.Shell).CreateShortcut('%SHORTCUT%');" ^
  "$s.TargetPath = 'wscript.exe';" ^
  "$s.Arguments  = '\"%~dp0Launch.vbs\"';" ^
  "$s.WorkingDirectory = '%~dp0';" ^
  "$s.IconLocation = '%~dp0assets\icon.ico,0';" ^
  "$s.Description  = 'World Clock - desktop widget';" ^
  "$s.Save()"

if exist "%SHORTCUT%" (
    echo.
    echo Created: "%SHORTCUT%"
    echo.
    echo Double-click the "World Clock" icon in this folder any time
    echo to launch the widget.
) else (
    echo.
    echo Could not create the shortcut.
)
echo.
pause
endlocal
exit /b 0
