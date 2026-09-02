# Workspace one-click bootstrap — Windows PowerShell.
#
# From-scratch grab: ensures git/python (winget), clones the workspace into a PERMANENT
# location, runs the installer, and opens Obsidian. The repo is PUBLIC, so no auth is
# needed to grab it (you only need auth to push later — `gh auth login`).
#
# Run any of:
#   iwr -useb https://raw.githubusercontent.com/snds/workspace/main/00-bootstrap/setup/bootstrap.ps1 | iex
#   .\bootstrap.ps1                       # clones to ~\Projects\Workspace
#   .\bootstrap.ps1 -Target C:\path       # custom target
#
# Overrides (env): CLAUDE_WORKSPACE_REPO, CLAUDE_WORKSPACE_DIR, CLAUDE_WORKSPACE_BRANCH

param(
    [string]$Target = $(if ($env:CLAUDE_WORKSPACE_DIR) { $env:CLAUDE_WORKSPACE_DIR } else { Join-Path $HOME "Projects\Workspace" })
)

$ErrorActionPreference = "Stop"

$RepoUrl = if ($env:CLAUDE_WORKSPACE_REPO) { $env:CLAUDE_WORKSPACE_REPO } else { "https://github.com/snds/workspace.git" }
$Branch  = if ($env:CLAUDE_WORKSPACE_BRANCH) { $env:CLAUDE_WORKSPACE_BRANCH } else { "main" }

function Say($m)  { Write-Host "`n$m" -ForegroundColor White }
function Info($m) { Write-Host "  - $m" }
function Ok($m)   { Write-Host "  $([char]0x2713) $m" -ForegroundColor Green }

# 1. Ensure winget + git.
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "winget not found. Install 'App Installer' from the Microsoft Store, then re-run." -ForegroundColor Red
    exit 1
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Say "Installing Git…"
    winget install --id Git.Git -e --silent --accept-package-agreements --accept-source-agreements
}

Say "Workspace -> $Target"
Info "repo:   $RepoUrl"
Info "branch: $Branch"

# 2. Grab. Three cases, all non-destructive.
if (Test-Path (Join-Path $Target ".git")) {
    # (a) Already a checkout — update.
    Info "Existing checkout found - updating."
    git -C $Target remote set-url origin $RepoUrl 2>$null; if ($LASTEXITCODE -ne 0) { git -C $Target remote add origin $RepoUrl }
    git -C $Target fetch origin $Branch
    git -C $Target checkout $Branch 2>$null; if ($LASTEXITCODE -ne 0) { git -C $Target checkout -b $Branch --track "origin/$Branch" }
    git -C $Target pull --rebase origin $Branch
    Ok "Updated to latest origin/$Branch"
}
elseif ((Test-Path $Target) -and (Get-ChildItem -Force $Target | Select-Object -First 1)) {
    # (b) Folder exists, non-empty, but NOT a git repo — adopt without touching files.
    Info "Folder is non-empty with no .git - adopting it as the checkout (non-destructive)."
    git -C $Target init -q
    git -C $Target symbolic-ref HEAD "refs/heads/$Branch"
    git -C $Target remote add origin $RepoUrl 2>$null; if ($LASTEXITCODE -ne 0) { git -C $Target remote set-url origin $RepoUrl }
    git -C $Target fetch origin $Branch
    git -C $Target reset "origin/$Branch"
    git -C $Target branch --set-upstream-to="origin/$Branch" $Branch 2>$null
    Ok "Adopted. Review: git -C `"$Target`" status"
}
else {
    # (c) Fresh clone.
    Info "Cloning fresh…"
    New-Item -ItemType Directory -Path (Split-Path $Target -Parent) -Force | Out-Null
    git clone --branch $Branch $RepoUrl $Target
    Ok "Cloned to $Target"
}

# 3. Run the installer (ensures Python first).
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Say "Installing Python…"
    winget install --id Python.Python.3.12 -e --silent --accept-package-agreements --accept-source-agreements
}
if (Get-Command python -ErrorAction SilentlyContinue) {
    Say "Running setup…"
    $env:CLAUDE_WORKSPACE_REPO = $RepoUrl
    python (Join-Path $Target "00-bootstrap\setup\setup.py")
} else {
    Write-Host "  python not found on PATH — open a new terminal and run: python `"$Target\00-bootstrap\setup\setup.py`"" -ForegroundColor Yellow
}

# 4. Open the vault in Obsidian.
$obsidian = Get-Command obsidian -ErrorAction SilentlyContinue
if ($obsidian) { Start-Process obsidian } else { Start-Process explorer.exe $Target }

Say "Done -> $Target"
Write-Host "  Next: open it in Obsidian (Open folder as vault) and run 'claude' from a terminal there."
