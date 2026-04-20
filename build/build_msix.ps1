<#
    Builds dist\WorldClock.msix for Microsoft Store submission.

    Prerequisites (one-time):
      * Python 3.10+ on PATH
      * Windows 10/11 SDK installed (provides makeappx.exe / signtool.exe)
        Download: https://developer.microsoft.com/windows/downloads/windows-sdk/

    Run:
        powershell -ExecutionPolicy Bypass -File build\build_msix.ps1 -Version 1.0.0.0

    Output:
        dist\WorldClock.msix    <- upload this to Partner Center

    The Store re-signs uploaded MSIX packages, so you do NOT need to sign
    the package yourself for submission. Pass -Sign only if you want a
    locally-signed copy for sideload testing on your own machine.
#>
[CmdletBinding()]
param(
    [string]$Version = "1.0.0.0",
    [switch]$Sign,
    [string]$Cert  = "build\testcert.pfx",
    [string]$CertPassword
)

$ErrorActionPreference = "Stop"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $root

if ($Version -notmatch '^\d+\.\d+\.\d+\.0$') {
    throw "Version must be 4-part with last segment 0 (e.g. 1.0.0.0). Got: $Version"
}

Write-Host "[1/5] Installing build dependencies..." -ForegroundColor Cyan
python -m pip install --quiet -r requirements.txt
python -m pip install --quiet -r requirements-build.txt

Write-Host "[2/5] Generating icons + Store tiles..." -ForegroundColor Cyan
python build\generate_icons.py

Write-Host "[3/5] Running PyInstaller (--onedir)..." -ForegroundColor Cyan
python -m PyInstaller --clean --noconfirm build\WorldClock_onedir.spec

$stage = Join-Path $root "dist\WorldClock"
if (-not (Test-Path $stage)) { throw "PyInstaller output missing: $stage" }

Write-Host "[4/5] Staging MSIX payload..." -ForegroundColor Cyan
# Drop the manifest (with version substituted) into the stage root.
$manifestSrc = Join-Path $root "build\AppxManifest.xml"
$manifestDst = Join-Path $stage "AppxManifest.xml"
(Get-Content $manifestSrc -Raw) -replace 'Version="1\.0\.0\.0"', "Version=`"$Version`"" |
    Set-Content -Path $manifestDst -Encoding UTF8

# Tile assets must live next to the manifest at the paths declared in it.
$tileDst = Join-Path $stage "assets\store"
New-Item -ItemType Directory -Force -Path $tileDst | Out-Null
Copy-Item -Force (Join-Path $root "assets\store\*.png") $tileDst

# Sanity check the manifest still has placeholders that MUST be replaced.
$manifestText = Get-Content $manifestDst -Raw
$placeholders = @("PACKAGE_IDENTITY_NAME","PUBLISHER_ID","PUBLISHER_DISPLAY_NAME")
$missing = $placeholders | Where-Object { $manifestText -match $_ }
if ($missing) {
    Write-Warning "AppxManifest.xml still contains placeholders: $($missing -join ', ')"
    Write-Warning "Edit build\AppxManifest.xml with the values from Partner Center before submitting."
}

Write-Host "[5/5] Locating Windows SDK tools..." -ForegroundColor Cyan
$sdkRoot = "${env:ProgramFiles(x86)}\Windows Kits\10\bin"
$makeappx = Get-ChildItem -Path $sdkRoot -Recurse -Filter makeappx.exe -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -match 'x64' } |
            Sort-Object FullName -Descending | Select-Object -First 1
if (-not $makeappx) {
    throw "makeappx.exe not found under $sdkRoot.  Install the Windows 10/11 SDK."
}

$out = Join-Path $root "dist\WorldClock.msix"
if (Test-Path $out) { Remove-Item $out }
& $makeappx.FullName pack /d $stage /p $out /overwrite | Out-Host
Write-Host "Built: $out" -ForegroundColor Green

if ($Sign) {
    if (-not (Test-Path $Cert)) {
        throw "Sign requested but certificate not found: $Cert"
    }
    $signtool = Get-ChildItem -Path $sdkRoot -Recurse -Filter signtool.exe -ErrorAction SilentlyContinue |
                Where-Object { $_.FullName -match 'x64' } |
                Sort-Object FullName -Descending | Select-Object -First 1
    if (-not $signtool) { throw "signtool.exe not found." }
    $signArgs = @('sign','/fd','SHA256','/a','/f',$Cert)
    if ($CertPassword) { $signArgs += @('/p', $CertPassword) }
    $signArgs += $out
    & $signtool.FullName @signArgs | Out-Host
}

Write-Host ""
Write-Host "Next: upload dist\WorldClock.msix to Microsoft Partner Center." -ForegroundColor Yellow
Write-Host "See STORE_SUBMISSION.md for the full walkthrough."
