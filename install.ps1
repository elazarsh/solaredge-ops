#Requires -Version 5.1
<#
.SYNOPSIS
    מתקין את SolarEdge Ops — כלי ניטור והתראות למתקני SolarEdge.
.DESCRIPTION
    הסקריפט:
      1. בודק אם Python 3.11+ מותקן; מתקין אותו דרך winget אם לא.
      2. יוצר סביבה וירטואלית ומתקין את כל התלויות.
      3. יוצר קיצורי דרך בשולחן העבודה ובתפריט התחל.
      4. (אופציונלי) מגדיר משימה ב-Task Scheduler להרצה אוטומטית.
      5. פותח את ה-Dashboard בדפדפן לקינפוג ראשוני.
.NOTES
    יש להריץ כמשתמש רגיל (לא כ-Administrator) — הסקריפט מבקש
    הרשאות רק לחלקים שצריכים אותן.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ── צבעים לקונסול ──────────────────────────────────────────────
function Write-Step   { param($msg) Write-Host "`n  ◆ $msg" -ForegroundColor Cyan }
function Write-OK     { param($msg) Write-Host "    ✓ $msg" -ForegroundColor Green }
function Write-Warn   { param($msg) Write-Host "    ⚠ $msg" -ForegroundColor Yellow }
function Write-Err    { param($msg) Write-Host "    ✗ $msg" -ForegroundColor Red }
function Write-Banner {
    Write-Host ""
    Write-Host "  ╔═══════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "  ║        SolarEdge Ops — Installer          ║" -ForegroundColor Yellow
    Write-Host "  ║   ניטור, התראות ודיווח למתקני סולארי     ║" -ForegroundColor Yellow
    Write-Host "  ╚═══════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""
}

# ── נתיבים ──────────────────────────────────────────────────────
$installDir  = Join-Path $env:LOCALAPPDATA "SolarEdgeOps"
$venvDir     = Join-Path $installDir ".venv"
$configFile  = Join-Path $installDir "config.yaml"
$sourceDir   = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktop     = [Environment]::GetFolderPath("Desktop")
$startMenu   = Join-Path ([Environment]::GetFolderPath("StartMenu")) "Programs\SolarEdge Ops"

# ────────────────────────────────────────────────────────────────
Write-Banner

# ── שלב 1: בדיקת / התקנת Python ────────────────────────────────
Write-Step "בודק Python..."

$pyExe = $null
foreach ($candidate in @("python", "python3", "py")) {
    try {
        $ver = & $candidate --version 2>&1
        if ($ver -match "Python (\d+)\.(\d+)") {
            $major = [int]$Matches[1]; $minor = [int]$Matches[2]
            if ($major -ge 3 -and $minor -ge 11) {
                $pyExe = (Get-Command $candidate -ErrorAction SilentlyContinue).Source
                Write-OK "נמצא $ver"
                break
            }
        }
    } catch {}
}

if (-not $pyExe) {
    Write-Warn "Python 3.11+ לא נמצא — מתקין דרך winget..."
    try {
        winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements --silent
        # רענן PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                    [System.Environment]::GetEnvironmentVariable("Path", "User")
        $pyExe = (Get-Command python -ErrorAction Stop).Source
        Write-OK "Python הותקן: $pyExe"
    } catch {
        Write-Err "ההתקנה נכשלה. הורד Python ידנית מ: https://python.org/downloads"
        exit 1
    }
}

# ── שלב 2: העתקת קבצים ──────────────────────────────────────────
Write-Step "מעתיק קבצים אל $installDir ..."
if (-not (Test-Path $installDir)) { New-Item -ItemType Directory -Path $installDir -Force | Out-Null }

# העתק הכל חוץ מ-.venv, __pycache__, state.db, config.yaml קיים
$exclude = @('.venv', '__pycache__', '*.pyc', 'state.db', '*.egg-info', '.pytest_cache', '.git', 'dist')
Get-ChildItem -Path $sourceDir | Where-Object {
    $name = $_.Name
    -not ($exclude | Where-Object { $name -like $_ })
} | ForEach-Object {
    Copy-Item $_.FullName -Destination $installDir -Recurse -Force
}
Write-OK "קבצים הועתקו"

# ── שלב 3: סביבה וירטואלית + תלויות ────────────────────────────
Write-Step "יוצר סביבה וירטואלית..."
if (-not (Test-Path $venvDir)) {
    & $pyExe -m venv $venvDir
}
$pip    = Join-Path $venvDir "Scripts\pip.exe"
$python = Join-Path $venvDir "Scripts\python.exe"

Write-Step "מתקין חבילות..."
& $pip install -q -r (Join-Path $installDir "requirements.txt")
Write-OK "חבילות הותקנו"

# ── שלב 4: קינפוג ראשוני ────────────────────────────────────────
Write-Step "בודק קובץ קינפוג..."
if (-not (Test-Path $configFile)) {
    Copy-Item (Join-Path $installDir "config.example.yaml") $configFile
    Write-Warn "נוצר config.yaml מהתבנית — תצטרך להגדיר API key ב-Dashboard"
} else {
    Write-OK "config.yaml קיים — לא הוחלף"
}

# ── שלב 5: קיצורי דרך ───────────────────────────────────────────
Write-Step "יוצר קיצורי דרך..."

$WshShell = New-Object -ComObject WScript.Shell

function New-Shortcut {
    param($linkPath, $target, $args, $icon, $desc)
    $sc = $WshShell.CreateShortcut($linkPath)
    $sc.TargetPath      = $target
    $sc.Arguments       = $args
    $sc.WorkingDirectory= $installDir
    if ($icon) { $sc.IconLocation = $icon }
    $sc.Description     = $desc
    $sc.Save()
}

if (-not (Test-Path $startMenu)) { New-Item -ItemType Directory $startMenu -Force | Out-Null }

$dashLaunch = Join-Path $installDir "start-dashboard.bat"
$checkLaunch= Join-Path $installDir "run-check.bat"

# קיצור Dashboard
foreach ($dest in @($desktop, $startMenu)) {
    New-Shortcut `
        -linkPath (Join-Path $dest "SolarEdge Ops — Dashboard.lnk") `
        -target   $dashLaunch `
        -args     "" `
        -icon     "shell32.dll,14" `
        -desc     "פתח את לוח הבקרה של SolarEdge Ops"
}
# קיצור Check
New-Shortcut `
    -linkPath (Join-Path $startMenu "SolarEdge Ops — בדיקה ידנית.lnk") `
    -target   $checkLaunch `
    -args     "" `
    -icon     "shell32.dll,48" `
    -desc     "הרץ בדיקת מתקנים ידנית"

Write-OK "קיצורי דרך נוצרו בשולחן העבודה ובתפריט התחל"

# ── שלב 6: Task Scheduler (אופציונלי) ───────────────────────────
Write-Step "הגדרת הרצה אוטומטית..."
$answer = Read-Host "    האם להגדיר משימה אוטומטית שתרוץ כל 30 דק' בין 06:00-19:00? (y/N)"
if ($answer -match "^[Yy]") {
    $taskName   = "SolarEdgeOps-Check"
    $taskAction = New-ScheduledTaskAction -Execute $checkLaunch -WorkingDirectory $installDir
    $taskTriggers = @()
    # כל 30 דקות בין 06:00 ל-19:00
    foreach ($hour in 6..18) {
        foreach ($min in @(0, 30)) {
            $t = New-ScheduledTaskTrigger -Daily -At ("{0:D2}:{1:D2}" -f $hour,$min)
            $taskTriggers += $t
        }
    }
    $taskSettings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 5) -StartWhenAvailable

    try {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
        Register-ScheduledTask -TaskName $taskName `
            -Action $taskAction -Trigger $taskTriggers -Settings $taskSettings `
            -Description "SolarEdge Ops — בדיקת מתקנים כל 30 דקות" -RunLevel Limited
        Write-OK "משימה '$taskName' נרשמה ב-Task Scheduler"
    } catch {
        Write-Warn "לא הצלחתי לרשום משימה: $_"
        Write-Warn "ניתן לעשות זאת ידנית דרך Task Scheduler"
    }
} else {
    Write-Warn "דולג — ניתן להוסיף ידנית דרך Task Scheduler בהמשך"
}

# ── סיום ────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  ════════════════════════════════════════════" -ForegroundColor Green
Write-Host "   ✓  ההתקנה הושלמה!" -ForegroundColor Green
Write-Host "   ✓  תיקיית התקנה: $installDir" -ForegroundColor Green
Write-Host "   ✓  קיצור 'SolarEdge Ops — Dashboard' בשולחן העבודה" -ForegroundColor Green
Write-Host "  ════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""

$openNow = Read-Host "  פתח את ה-Dashboard עכשיו להגדרה ראשונית? (Y/n)"
if ($openNow -notmatch "^[Nn]") {
    Start-Process $dashLaunch
}
