@echo off
REM Double-clickable Windows installer for Claude Workspace.
REM Bootstraps Python via winget if missing, then runs setup.py.

cd /d "%~dp0"

echo.
echo Claude Workspace installer (Windows)
echo ====================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
  echo Python not found. Installing via winget...
  winget install --id Python.Python.3.12 -e --silent --accept-package-agreements --accept-source-agreements
  if %errorlevel% neq 0 (
    echo.
    echo Failed to install Python via winget.
    echo Install manually from https://python.org/downloads and re-run this installer.
    pause
    exit /b 1
  )
  REM Refresh PATH for the current session
  call refreshenv.cmd >nul 2>&1
)

python setup.py
echo.
pause
