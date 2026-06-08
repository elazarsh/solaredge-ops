#Requires -Version 5.1
# Build a distributable zip of SolarEdge Ops
param(
    [string]$Version = "1.0.0"
)

$root    = Split-Path -Parent $MyInvocation.MyCommand.Path
$distDir = Join-Path $root "dist"
$zipName = "solaredge-ops-$Version-installer.zip"
$zipPath = Join-Path $distDir $zipName

$exclude = @('.git','.venv','__pycache__','*.pyc','*.egg-info',
             '.pytest_cache','state.db','config.yaml','config-demo.yaml',
             'dist','build-dist.ps1','.claude')

Write-Host ""
Write-Host "  SolarEdge Ops -- Build Distributor v$Version" -ForegroundColor Cyan
Write-Host "  -------------------------------------------" -ForegroundColor Cyan

if (Test-Path $distDir) { Remove-Item $distDir -Recurse -Force }
New-Item -ItemType Directory $distDir | Out-Null

$tmpDir = Join-Path $distDir "tmp\solaredge-ops"
New-Item -ItemType Directory $tmpDir -Force | Out-Null

function Copy-Selective($src, $dst) {
    foreach ($item in Get-ChildItem -Path $src) {
        $skip = $false
        foreach ($pat in $exclude) { if ($item.Name -like $pat) { $skip = $true; break } }
        if ($skip) { continue }
        if ($item.PSIsContainer) {
            $sub = Join-Path $dst $item.Name
            New-Item -ItemType Directory $sub -Force | Out-Null
            Copy-Selective $item.FullName $sub
        } else {
            Copy-Item $item.FullName $dst -Force
        }
    }
}

Write-Host "  Collecting files..." -ForegroundColor Gray
Copy-Selective $root $tmpDir

Write-Host "  Creating $zipName ..." -ForegroundColor Gray
Compress-Archive -Path (Join-Path $distDir "tmp\*") -DestinationPath $zipPath -Force
Remove-Item (Join-Path $distDir "tmp") -Recurse -Force

$sizeMB = [math]::Round((Get-Item $zipPath).Length / 1MB, 2)

Write-Host ""
Write-Host "  OK  Created: $zipPath  ($sizeMB MB)" -ForegroundColor Green
Write-Host ""
Write-Host "  User instructions:" -ForegroundColor Yellow
Write-Host "    1. Download and extract $zipName"
Write-Host "    2. Open PowerShell in the extracted folder"
Write-Host "    3. Run:  .\install.ps1"
Write-Host "    4. Follow prompts, then configure via the Dashboard"
Write-Host ""
