@echo off
title AURA Luxury Gold Jewellery Shopping Platform
color 0E
echo =========================================================================
echo                   AURA GOLD JEWELLERY SHOPPING PLATFORM
echo =========================================================================
echo.
cd /d "%~dp0"

IF EXIST "venv\Scripts\python.exe" (
    set "PY_EXE=venv\Scripts\python.exe"
) ELSE IF EXIST "C:\Users\ASUS\AppData\Local\Programs\Python\Python37\python.exe" (
    set "PY_EXE=C:\Users\ASUS\AppData\Local\Programs\Python\Python37\python.exe"
) ELSE (
    set "PY_EXE=python"
)

echo Using Python: %PY_EXE%
echo Starting Django Development Server on http://127.0.0.1:8000/ ...
echo.
echo Demo Accounts:
echo   - Admin Portal:     Username: admin    / Password: Admin@123
echo   - Customer Account: Username: customer / Password: Customer@123
echo.
echo Press Ctrl+C in this console window to stop the server anytime.
echo =========================================================================
echo.

"%PY_EXE%" manage.py runserver 127.0.0.1:8000
pause
