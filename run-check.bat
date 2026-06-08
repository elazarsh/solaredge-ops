@echo off
chcp 65001 >nul
setlocal

set "INSTALL_DIR=%~dp0"
set "VENV_PYTHON=%INSTALL_DIR%.venv\Scripts\python.exe"
set "CONFIG=%INSTALL_DIR%config.yaml"
set "LOG=%INSTALL_DIR%solaredge-ops.log"

if not exist "%VENV_PYTHON%" (
    echo ⚠ הסביבה הוירטואלית לא נמצאה — הרץ את install.ps1 תחילה.
    pause
    exit /b 1
)

echo [%date% %time%] מריץ בדיקת מתקנים... >> "%LOG%"
"%VENV_PYTHON%" -m solaredge_ops.cli --config "%CONFIG%" check >> "%LOG%" 2>&1
echo [%date% %time%] סיום. >> "%LOG%"

:: אם הופעל ישירות (לא מ-Task Scheduler) — הצג את הפלט
if "%1"=="" (
    echo.
    echo  בדיקה הושלמה. לפרטים:
    type "%LOG%" | findstr /v "^$" | tail
    echo.
    pause
)
