@echo off
REM Double-click to grab + set up the workspace on a fresh Windows machine.
REM
REM This is a tiny stub: it fetches the canonical bootstrap.ps1 from GitHub and runs it,
REM so it stays current and works even if downloaded on its own. The repo is PUBLIC --
REM no login needed to grab it.
REM
REM First time after downloading: SmartScreen may warn ("Windows protected your PC").
REM Click "More info" -> "Run anyway".
REM
REM Clones to %USERPROFILE%\Projects\Workspace by default.
REM Override: set CLAUDE_WORKSPACE_DIR=C:\path  before running.

echo Claude Workspace -- one-click setup (Windows)
echo =============================================
powershell -NoProfile -ExecutionPolicy Bypass -Command "iwr -useb https://raw.githubusercontent.com/snds/workspace/main/00-bootstrap/setup/bootstrap.ps1 | iex"
echo.
pause
