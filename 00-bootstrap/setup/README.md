# Claude Workspace — Installer

Cross-platform installer for a fresh machine. Brings up Claude Code, Obsidian,
Google Drive for Desktop, Git + gh, and the Claude Workspace vault config.
Idempotent — safe to re-run.

## Two ways to run

### 1. Already have the repo cloned locally (recommended path)

Double-click one of:
- **macOS:** `setup.command`
- **Windows:** `setup.bat`

If that fails, open a terminal in the `setup/` directory and run:
- **macOS/Linux:** `python3 setup.py`
- **Windows:** `python setup.py`

### 2. Fresh machine — nothing installed yet

Use the one-liner bootstrap. It clones the repo to a temp directory and runs the installer.

**macOS / Linux:**
```bash
export CLAUDE_WORKSPACE_REPO="git@github.com:snds/claude-workspace-system.git"
curl -fsSL https://raw.githubusercontent.com/snds/claude-workspace-system/main/00-bootstrap/setup/bootstrap.sh | bash
```

**Windows PowerShell:**
```powershell
$env:CLAUDE_WORKSPACE_REPO="git@github.com:snds/claude-workspace-system.git"
iwr https://raw.githubusercontent.com/snds/claude-workspace-system/main/00-bootstrap/setup/bootstrap.ps1 | iex
```

The script clones the workspace repo, installs tooling, and wires Obsidian.

## What it installs

| Tool | macOS | Windows | Linux |
|---|---|---|---|
| Homebrew | — | n/a | n/a |
| winget App Installer | n/a | via MS Store (manual) | n/a |
| Git + GitHub CLI | brew | winget | manual (apt/dnf) |
| Claude Code | brew cask | winget | curl \| bash |
| Obsidian | brew cask | winget | manual (AppImage) |
| Google Drive for Desktop | brew cask | winget | not applicable (use rclone) |
| Python 3.12 | ships w/ macOS | winget | ships w/ distro |
| Obsidian plugins | GitHub releases | GitHub releases | GitHub releases |

## What it configures

- Claude Code reads `.claude/settings.json` hooks automatically when you run `claude` in the vault.
- Obsidian vault config (`.obsidian/`) ships with the repo — plugins, hotkeys, theme, graph settings.
- Community plugins are downloaded from their GitHub releases and placed in `.obsidian/plugins/`.
- Hostname is mapped to a machine label (adds to the known map, or prompts for a new one).

## Manual steps after install

1. **Sign into Google Drive for Desktop** with `hello@snds.design`. The installer can't do this.
2. **Open Obsidian** → "Open folder as vault" → select the Claude Workspace path.
3. Obsidian will prompt about community plugins — **enable them** (the installer already downloaded the files; Obsidian just needs your consent).
4. **Set up GitHub identity (macOS, two-account):** `bash 00-bootstrap/setup/setup-identity.sh`. Generates personal + work SSH keys, writes `~/.ssh/config` aliases (`github.com` → snds, `github-work` → sean-sands-centric), and optionally installs `~/.gitconfig` with directory-routed identity. See `08-knowledge/cross-domain/workspace-infrastructure.md` for the full pattern.
5. **First session:** `cd` to the workspace and run `claude`. Type "hello" — you should see workspace context auto-load from the SessionStart hook.

## Idempotency

Running the installer again:
- Skips installed tools
- Pulls latest from the Git remote
- Re-downloads plugins only if missing
- Won't overwrite custom settings you've tweaked

## Troubleshooting

**"winget not found" on Windows.** Install "App Installer" from the Microsoft Store, then re-run.

**Drive folder not found.** The installer waits up to 5 minutes. If your Drive sign-in is incomplete, finish it, then re-run.

**Plugin install fails.** GitHub may rate-limit unauthenticated API calls. Run `gh auth login` first, then re-run the installer — it will use gh's credentials automatically if present.

**"Python not found" on Windows after winget install.** Open a new terminal (PATH refresh needed), then re-run. Or use the `setup.bat` wrapper, which handles this.
