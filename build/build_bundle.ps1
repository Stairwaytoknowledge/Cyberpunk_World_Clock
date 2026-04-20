<#
    Builds a fully self-contained World Clock release.

    Output:  dist\WorldClock-<version>\
        runtime\                        <- embeddable Python + PyQt6 + tzdata
        src\, assets\, main_qt.py       <- the app
        Install.bat, Launch.vbs, Uninstall.bat, README.md

    Users download a zip of that folder, extract, double-click Install.bat.
    Install.bat does NOT need internet, Python, or winget - everything the
    app needs is already inside the folder.

    Usage:
        powershell -ExecutionPolicy Bypass -File build\build_bundle.ps1 -Version v1.0.0
#>
[CmdletBinding()]
param(
    [string]$Version       = "v0.0.0-dev",
    [string]$PythonVersion = "3.12.7"
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $root

$stage   = Join-Path $root "dist\WorldClock-$Version"
$runtime = Join-Path $stage "runtime"

Write-Host "[1/6] Cleaning $stage" -ForegroundColor Cyan
if (Test-Path $stage) { Remove-Item -Recurse -Force $stage }
New-Item -ItemType Directory -Force -Path $runtime | Out-Null

Write-Host "[2/6] Downloading embeddable Python $PythonVersion" -ForegroundColor Cyan
$zip = Join-Path $env:TEMP "python-embed-$PythonVersion.zip"
if (-not (Test-Path $zip)) {
    Invoke-WebRequest -UseBasicParsing `
        -Uri "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip" `
        -OutFile $zip
}
Expand-Archive -Path $zip -DestinationPath $runtime -Force

Write-Host "[3/6] Enabling site-packages and parent-dir import in embeddable layout" -ForegroundColor Cyan
# Embeddable Python's _pth file ENTIRELY replaces sys.path. We need to:
#   1. Keep the stdlib zip and runtime root (`.`) on the path.
#   2. Enable Lib\site-packages so our pip-installed wheels are importable.
#   3. Add `..` so `import src.clock_widget_qt` works - the app's source
#      lives one level up from the runtime folder.
#   4. `import site` re-enables sitecustomize hooks PyQt6 ships with.
$pth = Get-ChildItem $runtime -Filter "python*._pth" | Select-Object -First 1
@"
$($pth.BaseName).zip
.
..
Lib\site-packages

import site
"@ | Set-Content -Path $pth.FullName -Encoding ASCII

Write-Host "[4/6] Bootstrapping pip and installing dependencies" -ForegroundColor Cyan
$getPip = Join-Path $env:TEMP "get-pip.py"
if (-not (Test-Path $getPip)) {
    Invoke-WebRequest -UseBasicParsing -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $getPip
}
& "$runtime\python.exe" $getPip --no-warn-script-location | Out-Host
& "$runtime\python.exe" -m pip install --no-warn-script-location -r (Join-Path $root "requirements.txt") | Out-Host

Write-Host "[5/6] Pruning Qt modules the app does not use (saves ~140 MB)" -ForegroundColor Cyan
# The app only imports QtCore / QtGui / QtWidgets. Strip everything else.
$qt6 = Join-Path $runtime "Lib\site-packages\PyQt6\Qt6"
foreach ($d in @("qml","qsci","translations")) {
    $p = Join-Path $qt6 $d
    if (Test-Path $p) { Remove-Item -Recurse -Force $p }
}
$plugins = Join-Path $qt6 "plugins"
foreach ($d in @("assetimporters","multimedia","generic","networkinformation","position","printsupport","qmltooling","sceneparsers","sensors","sqldrivers","tls","webview")) {
    $p = Join-Path $plugins $d
    if (Test-Path $p) { Remove-Item -Recurse -Force $p }
}
# Keep only the DLLs Core/Gui/Widgets actually need at runtime.
$keep = '^(Qt6Core|Qt6Gui|Qt6Widgets|Qt6Network|Qt6Svg|Qt6DBus|Qt6OpenGL|libcrypto|libssl|libGLESv2|libEGL|d3dcompiler_47|opengl32sw|MSVCP140|VCRUNTIME140|concrt140|api-ms-).*\.dll$'
Get-ChildItem (Join-Path $qt6 "bin") -Filter *.dll | Where-Object { $_.Name -notmatch $keep } | Remove-Item -Force
# Drop pip/wheel - not needed at runtime.
foreach ($pat in @("pip", "pip-*.dist-info", "wheel", "wheel-*.dist-info")) {
    Get-ChildItem (Join-Path $runtime "Lib\site-packages") -Filter $pat -Force -ErrorAction SilentlyContinue |
        ForEach-Object { Remove-Item -Recurse -Force $_.FullName }
}
# Drop *.pyc / __pycache__ - they will be regenerated on first run if needed.
Get-ChildItem $runtime -Recurse -Force -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem $runtime -Recurse -Force -Filter "*.pyc"        | Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host "[6/6] Copying app files" -ForegroundColor Cyan
foreach ($f in @("Install.bat","Uninstall.bat","Launch.vbs","main_qt.py","README.md")) {
    Copy-Item (Join-Path $root $f) $stage
}
Copy-Item -Recurse (Join-Path $root "src")    $stage
Copy-Item -Recurse (Join-Path $root "assets") $stage

# Strip the developer-only contents of build/ from the user-facing bundle.
# (build/ scripts are kept in the GitHub source tree, not in the release zip.)

$sizeMB = [math]::Round((Get-ChildItem $stage -Recurse -File | Measure-Object Length -Sum).Sum / 1MB, 1)
Write-Host ""
Write-Host "Built: $stage  ($sizeMB MB)" -ForegroundColor Green
Write-Host "Next: Compress-Archive `"$stage\*`" `"$stage.zip`""
