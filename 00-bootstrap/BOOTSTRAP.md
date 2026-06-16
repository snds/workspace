# Claude Workspace — Bootstrap Reference
**Owner:** Sean Sands (hello@snds.design)
**Last updated:** 2026-03-06
**Drive folder:** Claude Workspace (root)

---

## What This Is

This Google Drive folder is the single source of truth for all work done with
Claude across every environment: claude.ai web, Claude Cowork, Claude Code,
Claude iOS, VS Code/Cursor with Claude extensions.

When starting any session, point Claude here. Everything needed to resume context,
apply standards, reinstall skills, and find prior artifacts is in this folder.

---

## Folder Structure

```
Claude Workspace/
├── 00-bootstrap/
│   └── BOOTSTRAP.md          ← You are here. Start every session here.
│
├── 01-shared-references/
│   ├── epistemic-standards.md   ← Assumption checking, evidence standards
│   └── artifact-standards.md   ← Naming, versioning, delivery conventions
│
├── 02-skills/
│   ├── ds-advisor/           ← Design systems advisor (primary work skill)
│   ├── figma-plugin/
│   ├── figma-plugin-dev/
│   ├── google-fonts-scraper/
│   ├── google-fonts-web-scraping/
│   ├── material-symbols-project/
│   ├── material-symbols-suite/
│   ├── material-symbols-svg-export/
│   ├── python-cross-platform-gui/
│   └── svg-font-extraction/
│   (Each folder contains: SKILL.md + a .skill package for installation)
│
├── 03-preferences/
│   └── user-preferences.md   ← Prompting style, tone, domain expertise levels
│
├── 04-artifacts/
│   ├── active/               ← Current working artifacts (named per convention)
│   └── archive/              ← Superseded versions — never deleted
│
└── 05-version-registers/
    └── (per-project version register files)
```

---

## How to Start a Session

### On claude.ai web or Cowork
Say: *"Read my bootstrap doc in Google Drive under Claude Workspace."*
Claude will find this file and resume with full context.

### On Claude Code (VS Code / Cursor)
1. Open `~/.claude/CLAUDE.md` — your persistent instruction file for Claude Code.
2. Paste the **Claude Code Bootstrap Block** from the bottom of this file.
3. Claude Code reads `CLAUDE.md` automatically on every session.

### On Claude iOS
The Google Drive connector works on iOS. Say:
*"Check my Claude Workspace bootstrap doc in Google Drive."*
Skills can't be installed on iOS, but shared references and preferences are readable.

---

## How Skills Work Per Environment

Skills are instructions Claude loads to handle specific tasks well. The *content*
lives here in Drive. The *installation* is environment-specific.

| Environment | Install method | Source |
|---|---|---|
| claude.ai web | Upload `.skill` file via Settings → Skills | `02-skills/[name]/` |
| Claude Cowork | Same as web | `02-skills/[name]/` |
| Claude Desktop (Chat) | Same as web | `02-skills/[name]/` |
| Claude Code | Paste SKILL.md content into `~/.claude/CLAUDE.md` | `02-skills/[name]/SKILL.md` |
| Claude iOS | Not installable — reference content verbally | Read from Drive on request |

When a skill is updated, the new version is saved here first. Re-install from here.

---

## Filesystem Access Per Environment

| Environment | Read/Write workspace? | How |
|---|---|---|
| Claude Code | ✅ Full | bash tool, native |
| Cowork | ✅ Full | bash tool, native |
| Claude Desktop (Chat) | ✅ Full | filesystem MCP — one-time setup (see below) |
| claude.ai web | ❌ Read-only | Drive MCP connector |
| Claude iOS | ❌ Read-only | Drive MCP connector |

### Claude Desktop — One-Time Filesystem Setup

Elevates Claude Desktop (Chat) from read-only to full read/write — same capability
as Claude Code and Cowork. Requires Node.js (https://nodejs.org, LTS version).

**1. Open the config file in a text editor:**

macOS:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```
Windows:
```
%APPDATA%\Claude\claude_desktop_config.json
```

**2. Add the filesystem server** (use your OS path from the OS Path Reference below):

macOS:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/[your-username]/Library/CloudStorage/GoogleDrive-hello@snds.design/My Drive/Claude Workspace"
      ]
    }
  }
}
```

Windows:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "G:\\My Drive\\Claude Workspace"
      ]
    }
  }
}
```

**3. Fully quit and relaunch Claude Desktop.**
A hammer icon in the bottom-right of the chat input confirms the server is active.

Claude will ask your approval before each file operation. Access is scoped to the
Claude Workspace folder only.

---

## Shared References — Load These When Relevant

These two files are referenced by all skills. Claude should read them when:
- Starting a non-trivial problem (epistemic-standards.md)
- Producing or receiving any file (artifact-standards.md)

Direct Claude: *"Read my shared references in Claude Workspace/01-shared-references/"*

---

## Artifact Naming Quick Reference

```
[context]_[descriptor]_v[major].[minor]_[YYYY-MM-DD].[ext]

Example: ds-audit_triage-report_v2.0_2026-03-06.md
```

- Active work → `04-artifacts/active/`
- Superseded versions → `04-artifacts/archive/`
- Never delete. Never overwrite. Always increment.

---

## User Preferences Summary

Full preferences in `03-preferences/user-preferences.md`. Quick reference:

- **Role:** Principal lead product designer, design systems
- **Stack:** Centric PLM, Figma, Vue/React/Angular, enterprise SaaS
- **Expertise:** UX/DS (peer level) — video game/hardware/3D (learner level)
- **Output defaults:** Artifacts in artifact windows; direct answers first;
  no preamble; Oxford comma; US English
- **Default platform:** macOS (other platforms additive, never instead-of)
- **Evidence standard:** Cite sources with recency and relevance — both required

---

## Claude Code Bootstrap Block

Copy this into `~/.claude/CLAUDE.md` for persistent Claude Code context.
**Replace `[WORKSPACE ROOT]` with the correct path for your OS** — see the
OS Path Reference section immediately below.

```markdown
# Sean's Claude Code Context

## Workspace — Local Path (Google Drive for Desktop)
All skills, references, preferences, and artifacts live at:
[WORKSPACE ROOT]/Claude Workspace/

Read full context: [WORKSPACE ROOT]/Claude Workspace/00-bootstrap/BOOTSTRAP.md

Key paths:
- Shared references: [WORKSPACE ROOT]/Claude Workspace/01-shared-references/
- Skills:            [WORKSPACE ROOT]/Claude Workspace/02-skills/
- Preferences:       [WORKSPACE ROOT]/Claude Workspace/03-preferences/user-preferences.md
- Active artifacts:  [WORKSPACE ROOT]/Claude Workspace/04-artifacts/active/
- Archive:           [WORKSPACE ROOT]/Claude Workspace/04-artifacts/archive/
- Version registers: [WORKSPACE ROOT]/Claude Workspace/05-version-registers/

## Artifact output behavior (Claude Code only)
When producing a final artifact:
- Write directly to [WORKSPACE ROOT]/Claude Workspace/04-artifacts/active/
- Use naming convention: context_descriptor_vN.N_YYYY-MM-DD.ext
- Never overwrite — increment the version, move prior to archive/
- Changes sync automatically to Google Drive

## Shared references (read when relevant)
- [WORKSPACE ROOT]/Claude Workspace/01-shared-references/epistemic-standards.md
- [WORKSPACE ROOT]/Claude Workspace/01-shared-references/artifact-standards.md

## Core operating principles
- Question all assumptions — yours and mine — before optimizing on them
- Evidence must be recent AND relevant; cite with version/date
- Name tradeoffs explicitly; never hide deferred debt
- Default platform: macOS (others are additive)
- All artifacts: context_descriptor_vN.N_YYYY-MM-DD.ext convention
- Runnable code: always deliver as double-click zip, no terminal required

## Role & expertise
Principal lead product designer specializing in design systems.
Domain: Centric PLM (enterprise fashion/food/product SaaS).
Expert in: UX, design systems, Figma, component architecture, token systems.
Learner in: game design (visual/aesthetic), electronics, 3D modeling, graphic design.

## Response style
Direct — answer first, context after. No preamble. US English, Oxford comma.
Use design system terminology freely (tokens, variants, anatomy, slots, alias, primitive).
```

---

## OS Path Reference — Find Your [WORKSPACE ROOT]

Google Drive for Desktop mounts differently on each OS. Use the section for your
OS to find the correct root path, then substitute it into `[WORKSPACE ROOT]` above.

---

### macOS

**Default mount location:**
```
~/Library/CloudStorage/GoogleDrive-[your-email]/My Drive
```

**To confirm your exact path:**
```bash
ls ~/Library/CloudStorage/
```
This lists all cloud storage mounts. Your folder will be named
`GoogleDrive-hello@snds.design` (or whichever Google account owns the Drive).

**Full example:**
```
~/Library/CloudStorage/GoogleDrive-hello@snds.design/My Drive
```

**Notes:**
- `~` expands to `/Users/[your-username]` — either form works in `CLAUDE.md`
- If you have multiple Google accounts connected, each gets its own
  `GoogleDrive-[email]` folder under `CloudStorage/`
- "Available offline" setting in Drive for Desktop makes the folder
  fully local; without it, files are fetched on demand (still works, slightly slower)

---

### Windows

**Default mount location (Drive letter — most common):**
```
G:\My Drive
```
Google Drive for Desktop maps your Drive as a virtual drive letter, defaulting
to `G:` on most systems. This is the path to use in `CLAUDE.md`.

**If G: is taken by another drive:**
Drive for Desktop will pick the next available letter (H:, I:, etc.).

**To confirm your drive letter:**
1. Open File Explorer
2. Look under "This PC" in the left sidebar
3. Find the entry labelled "Google Drive" — the letter shown is yours

**Alternative path form (if you prefer not to rely on a drive letter):**
Some installations also expose the Drive folder under the user profile:
```
%USERPROFILE%\Google Drive\My Drive
```
However, the drive letter form (`G:\My Drive`) is more reliable and should
be preferred.

**Full example:**
```
G:\My Drive
```

**In CLAUDE.md on Windows**, use forward slashes or escaped backslashes:
```
G:/My Drive/Claude Workspace/
```

**Notes:**
- Windows paths are case-insensitive, but keep the casing consistent with
  what you see in File Explorer to avoid confusion
- If using WSL (Windows Subsystem for Linux), the Windows filesystem is
  mounted at `/mnt/[driveletter]/` — so `G:` becomes `/mnt/g/My Drive`

---

### Linux

Google Drive for Desktop does **not** have a native Linux client. The practical
alternatives, in order of recommendation:

**Option 1: rclone (recommended)**
rclone is an open-source tool that mounts Google Drive as a local filesystem.
It is actively maintained, widely used, and well-documented.

Install and mount:
```bash
# Install rclone (Debian/Ubuntu)
sudo apt install rclone

# Or via the official installer (all distros)
curl https://rclone.org/install.sh | sudo bash

# Configure (interactive — follow prompts for Google Drive)
rclone config

# Mount Drive to a local directory
mkdir -p ~/GoogleDrive
rclone mount "MyDrive:" ~/GoogleDrive --vfs-cache-mode writes &
```

Your workspace root after mounting:
```
~/GoogleDrive/My Drive
```

To mount automatically on login, add the `rclone mount` command to your
`~/.bashrc`, `~/.profile`, or a systemd user service.
Reference: https://rclone.org/drive/

**Option 2: google-drive-ocamlfuse**
A FUSE-based alternative if rclone doesn't suit your setup.
```bash
sudo add-apt-repository ppa:alessandro-strada/ppa
sudo apt update && sudo apt install google-drive-ocamlfuse
mkdir -p ~/GoogleDrive
google-drive-ocamlfuse ~/GoogleDrive
```

Your workspace root after mounting:
```
~/GoogleDrive
```

Reference: https://github.com/astrada/google-drive-ocamlfuse

**Option 3: Native file manager integration**
GNOME Files (Nautilus) and KDE Dolphin both support Google Drive via GVFS.
This works for manual file access but does **not** expose a stable filesystem
path that Claude Code can reference reliably — use Options 1 or 2 for Claude Code.

**Full example (rclone):**
```
~/GoogleDrive/My Drive
```

**Notes:**
- Linux path is case-sensitive — `My Drive` must match exactly as named in Drive
- Confirm the mounted folder name with `ls ~/GoogleDrive/` after mounting
- For Claude Code specifically, rclone with `--vfs-cache-mode writes` is
  necessary to allow write operations; read-only mounts will block artifact output

---

*This file is the handshake. Any Claude instance that reads it has full context.*
