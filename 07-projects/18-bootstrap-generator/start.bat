@echo off
REM Bootstrap Generator - double-click on-ramp for Windows.
REM Creates a NEW workspace folder for you. If SmartScreen warns, choose
REM "More info" then "Run anyway" - normal for downloaded tools.
REM This only calls Python; no file needs to be executable.
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if not errorlevel 1 (
  python launch.py
  goto :eof
)
where py >nul 2>nul
if not errorlevel 1 (
  py launch.py
  goto :eof
)
echo Python 3 is not installed.
echo Get it from https://www.python.org/downloads/ and check "Add Python to PATH"
echo during install, then double-click this file again.
pause
