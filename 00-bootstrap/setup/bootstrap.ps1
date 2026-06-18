# One-liner bootstrap for Windows PowerShell.
# Usage:
#   $env:CLAUDE_WORKSPACE_REPO="git@github.com:snds/workspace.git"
#   iwr https://raw.githubusercontent.com/snds/workspace/main/00-bootstrap/setup/bootstrap.ps1 | iex

$ErrorActionPreference = "Stop"

if (-not $env:CLAUDE_WORKSPACE_REPO) {
    Write-Host "Set CLAUDE_WORKSPACE_REPO to your private repo URL before running:" -ForegroundColor Yellow
    Write-Host '  $env:CLAUDE_WORKSPACE_REPO="git@github.com:snds/workspace.git"'
    Write-Host "  iwr https://raw.githubusercontent.com/snds/workspace/main/00-bootstrap/setup/bootstrap.ps1 | iex"
    exit 1
}

# Ensure winget is available
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "winget not found. Install 'App Installer' from the Microsoft Store, then re-run." -ForegroundColor Red
    exit 1
}

# Ensure Git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Git..." -ForegroundColor Cyan
    winget install --id Git.Git -e --silent --accept-package-agreements --accept-source-agreements
}

# Ensure Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Python..." -ForegroundColor Cyan
    winget install --id Python.Python.3.12 -e --silent --accept-package-agreements --accept-source-agreements
}

$tmpDir = Join-Path $env:TEMP "claude-workspace-bootstrap-$([guid]::NewGuid().ToString('N'))"
New-Item -ItemType Directory -Path $tmpDir -Force | Out-Null

try {
    Write-Host "Cloning $env:CLAUDE_WORKSPACE_REPO to temp..." -ForegroundColor Cyan
    git clone --depth 1 $env:CLAUDE_WORKSPACE_REPO "$tmpDir\workspace"
    Set-Location "$tmpDir\workspace"
    python 00-bootstrap\setup\setup.py
} finally {
    Set-Location $env:USERPROFILE
    Remove-Item -Path $tmpDir -Recurse -Force -ErrorAction SilentlyContinue
}
