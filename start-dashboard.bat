@echo off
chcp 65001 >nul
setlocal

:: מוצא את תיקיית ההתקנה (שם נמצא הקובץ הזה)
set "INSTALL_DIR=%~dp0"
set "VENV_PYTHON=%INSTALL_DIR%.venv\Scripts\python.exe"
set "CONFIG=%INSTALL_DIR%config.yaml"
set "PORT=5000"
set "URL=http://localhost:%PORT%"

:: בדיקה שהסביבה הוירטואלית קיימת
if not exist "%VENV_PYTHON%" (
    echo ⚠ הסביבה הוירטואלית לא נמצאה — הרץ את install.ps1 תחילה.
    pause
    exit /b 1
)

:: פותח את הדפדפן לאחר 2 שניות (נותן לשרת לעלות)
start "" /b cmd /c "timeout /t 2 >nul && start %URL%"

echo.
echo  ╔══════════════════════════════════════╗
echo  ║      SolarEdge Ops — Dashboard       ║
echo  ╚══════════════════════════════════════╝
echo.
echo   פותח ב-%URL%
echo   לסגירה: לחץ Ctrl+C בחלון זה
echo.

:: מפעיל את שרת ה-Web
"%VENV_PYTHON%" -m solaredge_ops.cli --config "%CONFIG%" web --port %PORT%

pause
