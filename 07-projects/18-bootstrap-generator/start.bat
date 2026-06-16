@echo off
REM Bootstrap Generator - the dummy-proof on-ramp for Windows.
REM Double-click this file. It creates a NEW workspace folder for you.
setlocal
cd /d "%~dp0"
set "WSX=%~dp0generator\bin\wsx"

echo ----------------------------------------------
echo   Bootstrap Generator - set up your workspace
echo ----------------------------------------------
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo Python 3 is not installed.
  echo Get it from https://www.python.org/downloads/ and check "Add Python to PATH"
  echo during install, then run this again.
  pause
  exit /b 1
)

where git >nul 2>nul
if errorlevel 1 (
  echo Note: git is not installed - your workspace won't sync or keep history.
  echo Get it free from https://desktop.github.com . Continuing without it.
  echo.
)

set "DEFAULT_DEST=%USERPROFILE%\Documents\my-workspace"
set /p "DEST=Where should your workspace live? [%DEFAULT_DEST%] "
if "%DEST%"=="" set "DEST=%DEFAULT_DEST%"
set /p "NAME=Your name (for the workspace) [you]: "
if "%NAME%"=="" set "NAME=you"

echo.
echo Creating your workspace...
python "%WSX%" init "%DEST%" --name "%NAME%"
if errorlevel 1 (
  echo.
  echo Could not create the workspace there (the folder may already exist and not be empty).
  pause
  exit /b 1
)
pushd "%DEST%" && python "%WSX%" emit claude-code >nul 2>nul & popd

echo.
echo Done. Your workspace is at:
echo     %DEST%
echo.
echo Next - pick ONE:
echo   * Browse it: open that folder in Obsidian (https://obsidian.md).
echo   * Let your AI fill it in: open the folder in your AI assistant
echo     (Claude Code, Cursor, ...) and say:   "set up my workspace"
echo.
pause
