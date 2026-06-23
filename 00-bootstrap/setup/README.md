# Workspace — Installer

Optional, cross-platform installer for a fresh machine. Brings up Claude Code, Obsidian, Git + gh,
and the workspace vault config. **None of it is required to work in the checkout** — the workspace is a
plain git clone; the installer only adds convenience. Idempotent — safe to re-run.

## Two ways to run

### 1. Already cloned the repo (recommended)

Double-click `setup.command` (macOS) or `setup.bat` (Windows). If that fails, open a terminal in the
`setup/` directory and run `python3 setup.py` (macOS/Linux) or `python setup.py` (Windows). The script
resolves the workspace root as the checkout it lives in (the tree containing `AGENTS.md`).

### 2. Fresh machine — nothing installed yet

The repo is **public**, so grabbing it needs no login. Everything clones into a permanent
checkout at `~/Projects/Workspace` by default (override with the `CLAUDE_WORKSPACE_DIR` env var).

**One-click (download one file, double-click):**

- **macOS** — download [`bootstrap.command`](bootstrap.command) and double-click. First run,
  macOS Gatekeeper may block it: right-click → **Open** → **Open** (or `xattr -d com.apple.quarantine bootstrap.command`).
- **Windows** — download [`bootstrap.bat`](bootstrap.bat) and double-click. First run, SmartScreen
  may warn: **More info** → **Run anyway**.
- **Linux** — use the one-liner below (double-click behavior is desktop-dependent).

**One-liner (terminal):**

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/snds/workspace/main/00-bootstrap/setup/bootstrap.sh | bash
```
```powershell
# Windows PowerShell
iwr -useb https://raw.githubusercontent.com/snds/workspace/main/00-bootstrap/setup/bootstrap.ps1 | iex
```

Each one grabs the repo into a permanent checkout, installs tooling, wires Obsidian, and opens the
vault — non-destructively (if the folder already exists it updates instead of clobbering). You only
need auth to **push** changes later: run `gh auth login` once.

## What it installs

| Tool | macOS | Windows | Linux |
|---|---|---|---|
| Homebrew | — | n/a | n/a |
| winget App Installer | n/a | via MS Store (manual) | n/a |
| Git + GitHub CLI | brew | winget | manual (apt/dnf) |
| Claude Code | brew cask | winget | curl \| bash |
| Obsidian | brew cask | winget | manual (AppImage) |
| Python 3.12 | ships w/ macOS | winget | ships w/ distro |
| Obsidian plugins | GitHub releases | GitHub releases | GitHub releases |

## What it configures

- Claude Code reads `.claude/settings.json` hooks automatically when you run `claude` in the checkout.
- Obsidian vault config (`.obsidian/`) ships with the repo — plugins, hotkeys, theme, graph settings.
- Community plugins are downloaded from their GitHub releases into `.obsidian/plugins/`.
- Hostname is mapped to a machine label.

## Manual steps after install

1. **Open Obsidian** → "Open folder as vault" → select the checkout.
2. Obsidian prompts about community plugins — **enable them** (the installer already downloaded the files).
3. **GitHub identity (macOS, two-account):** `bash 00-bootstrap/setup/setup-identity.sh` — generates SSH keys
   and writes `~/.ssh/config` aliases (`github.com` → snds, `github-work` → sean-sands-centric). See
   `08-knowledge/cross-domain/workspace-infrastructure.md`.
4. **First session:** `cd` to the checkout and run `claude`.

## Idempotency

Re-running skips installed tools, pulls latest from git, re-downloads plugins only if missing, and
won't overwrite settings you've tweaked.

## Troubleshooting

- **"winget not found" (Windows):** install "App Installer" from the Microsoft Store, then re-run.
- **Plugin install fails:** GitHub may rate-limit unauthenticated API calls — `gh auth login` first, then re-run.
- **"Python not found" (Windows) after winget install:** open a new terminal (PATH refresh), then re-run.
