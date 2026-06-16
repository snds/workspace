# Claude Workspace + Obsidian — Setup & Architecture

_Last updated: 2026-04-23_

Second-brain pattern from [Mibii's article](https://dev.to/mibii/claude-code-obsidian-build-a-second-brain-that-actually-thinks-d61),
adapted to an existing multi-project Claude Workspace.

## What this is

One folder on disk serves **three consumers** simultaneously:

- **Obsidian** — note-taking UI, graph view, templates, plugin ecosystem
- **Claude Code** — CLI that reads `CLAUDE.md` + `.claude/` config from the vault root
- **Claude Desktop** — reads the same files via Desktop Commander MCP

All three see the same filesystem. No sync bridge, no API layer. Filesystem is the contract.

## Directory map (post-install)

```
Claude Workspace/                          ← Obsidian vault root = Claude Code working dir
├── CLAUDE.md                              ← Claude Code context; auto-loaded per session
├── _HOME.md _PROJECTS.md _SKILLS.md ...   ← MOCs (Maps of Content) for Obsidian nav
│
├── .claude/                               ← Claude Code config — NOT visible in Obsidian
│   ├── settings.json                      ← hook config (SessionStart/End, Stop, UserPrompt)
│   ├── hooks/
│   │   └── dispatcher.py                  ← single cross-platform hook dispatcher
│   └── skills/
│       ├── today/SKILL.md                 ← /today
│       ├── session-end/SKILL.md           ← /session-end
│       ├── reconcile/SKILL.md             ← /reconcile
│       ├── new-project/SKILL.md           ← /new-project
│       └── framework-check/SKILL.md       ← /framework-check
│
├── .obsidian/                             ← Vault config — NOT visible in Obsidian
│   ├── app.json                           ← core preferences
│   ├── appearance.json                    ← theme
│   ├── core-plugins.json                  ← enabled core plugins
│   ├── community-plugins.json             ← enabled community plugins
│   ├── plugins-manifest.json              ← setup.py uses this to install plugins
│   ├── hotkeys.json                       ← custom shortcuts
│   ├── graph.json                         ← graph view defaults + color groups
│   └── plugins/                           ← plugin files (not in Git — installed fresh per machine)
│
├── 00-bootstrap/                          ← installer + integration docs + Obsidian templates
│   ├── OBSIDIAN-SETUP.md                  ← this file
│   ├── BOOTSTRAP.md                       ← original 2026-03 workspace bootstrap
│   ├── workspace-manifest.json            ← workspace metadata
│   ├── setup/                             ← cross-platform installer (setup.py + wrappers)
│   └── templates/                         ← Templater templates for new notes
├── 00-frameworks/                         ← 5 operating frameworks
├── 01-shared-references/                  ← standards
├── 02-skills/                             ← 60+ Claude Desktop skills
├── 03-preferences/                        ← user prefs
├── 04-artifacts/                          ← deliverables (ignored by Git)
├── 05-version-registers/                  ← (ignored by Git)
├── 06-context/                            ← authoritative context
├── 07-projects/                           ← project folders (mostly ignored by Git)
│   └── 00-obsidian/                       ← THIS integration as a project (tracked in Git)
└── 09-tools/                              ← (ignored by Git)
```

## How the three consumers see it

### Obsidian
- Opens the root as a vault
- Ignores `.claude/`, `.obsidian/`, `04-artifacts/archive/`, etc. (see `userIgnoreFilters` in `.obsidian/app.json`)
- Renders MOCs with live Dataview queries
- Obsidian Git plugin auto-commits + pushes every 15 min

### Claude Code
- You `cd` into the workspace and run `claude`
- `CLAUDE.md` loads automatically on session start
- `SessionStart` hook injects `06-context/*` + hostname + date into the session
- Slash commands `/today`, `/session-end`, etc. are auto-discovered from `.claude/skills/`
- `SessionEnd` hook commits and pushes any uncommitted changes

### Claude Desktop
- `workspace-bootstrap` skill reads the same files via Desktop Commander
- Skills mount at `02-skills/` synced via `skills-manifest.json` hash check
- Unchanged by this setup — continues to work as before

## The hands-off parts

| Mechanism | What it does | When it fires |
|---|---|---|
| `SessionStart` hook | Loads context (role, project, session log heads, hostname) | Start of every `claude` invocation |
| `UserPromptSubmit` hook | Scans for trigger words (`legion`, `centric`, etc.); surfaces relevant skills | Every user message |
| `Stop` hook | Stages session-log.md if it changed | After every assistant response |
| `SessionEnd` hook | Commits all system-layer changes, pushes to GitHub | End of session |
| Obsidian Git plugin | Auto-commits + pushes vault changes made in Obsidian | Every 15 min |
| Dataview queries | Keep MOCs current — new projects/skills appear automatically | On file focus |
| `skills-manifest.json` | Hash check on boot; syncs changed skills to mount | Claude Desktop boot |

You don't manage context. You don't curate the MOCs. You don't remember to commit. The system maintains itself.

## What you still do manually

- **Write the session block** — `/session-end` drafts it from session state, but Claude has to know what you decided. You can just tell it "wrap up" and it'll handle the rest.
- **Resolve conflicts** — if two machines touched the same file, git surfaces the conflict; you decide.
- **Add trigger words for new projects** — the dispatcher has a `TRIGGER_WORDS` map; the `/new-project` skill offers to update it.
- **Occasional cleanup** — stale projects, deprecated skills. Not automated by design.

## Sync topology

- **Filesystem sync:** Google Drive for Desktop. Handles all files, including binaries in `04-artifacts/` and `07-projects/`.
- **Version control:** Git, repo `claude-workspace-system` on GitHub. Tracks only the system layer — context, frameworks, skills, preferences, bootstrap, vault config, CLAUDE.md, MOCs. See `.gitignore` for the whitelist.
- **Two layers, not redundant.** Drive is the broad sync; Git is the scoped history layer. If Drive ever corrupts a file, Git is the recovery.

## Slash commands (Claude Code)

Run from any Claude Code session inside the vault:

- `/today` — daily note workflow
- `/session-end` — write session block, commit, push
- `/reconcile` — merge multiple machines' session blocks for the day
- `/new-project` — scaffold a new project under `07-projects/`
- `/framework-check` — critique current work through the five frameworks

See `.claude/skills/*/SKILL.md` for each one's full protocol.

## New-machine setup

1. Install Google Drive for Desktop, sign in as `hello@snds.design`. Wait for sync.
2. Download [`setup.bat`](setup/setup.bat) (Windows) or [`setup.command`](setup/setup.command) (macOS) from `00-bootstrap/setup/` in the repo.
3. Double-click it.
4. Follow prompts; the installer handles Claude Code, Obsidian, Git, gh, and plugins.
5. `cd` to the workspace and run `claude` to verify.
6. **Per-machine: relocate `.git/` off Drive (see "Git store lives off Drive" below).** This MUST be done on every machine — the `.git` pointer file is per-machine; it's intentionally NOT in the Drive-synced workspace.

Or run the one-liner bootstrap — see [setup/README.md](setup/README.md).

## Git store lives off Drive (per-machine setup)

**Why:** Google Drive (Stream mode on Windows, equivalent behavior on macOS) injects `desktop.ini` / `.DS_Store` files into every folder it touches, including every subdirectory of `.git/`. Git's auto-gc and fetch operations choke on these files (`fatal: bad object refs/desktop.ini`). The clean fix is to keep the working tree on Drive (so Obsidian, Drive sync, and everything else still work) but move git's metadata to a local-only path.

**One-time setup per machine** (run from the workspace root):

```bash
# 1. Pick a local-only path for the git store
#    Windows:  C:\Users\<you>\.git-stores\claude-workspace-system
#    macOS:    ~/.git-stores/claude-workspace-system

# 2. Move .git/ contents to that path
mkdir -p "<local-path>"
cp -r .git/. "<local-path>/"

# 3. Clean Drive-injected junk from the new location
find "<local-path>" -name "desktop.ini" -delete   # Windows
find "<local-path>" -name ".DS_Store" -delete     # macOS

# 4. Verify the new git store works
git --git-dir="<local-path>" log --oneline -3

# 5. Replace .git/ on Drive with a one-line pointer file
rm -rf .git
printf "gitdir: <local-path>\n" > .git

# 6. Verify from workspace root
git status        # should be clean
git fetch origin  # should succeed without errors
```

After this, all git commands work normally from the workspace root — they read the `.git` pointer file and follow it to the real store. The `.git` pointer file IS Drive-synced, but it's just text; Drive can't pollute it.

**Side benefit:** git operations are noticeably faster (local NTFS/APFS instead of Drive's streamed filesystem).

**Reversal:** if you ever need to undo, `mv <local-path>/* .git/` and delete the pointer file.

### Auto-fix: dispatcher rewrites the pointer per-machine

The `.git` pointer file at the workspace root IS Drive-synced, so each machine's pointer overwrites the previous machine's whenever Drive syncs. The Claude Code SessionStart hook (`.claude/hooks/dispatcher.py` → `ensure_local_gitdir()`) self-heals this on every boot:

- If the pointer's content already matches `~/.git-stores/claude-workspace-system` for the current user, no-op.
- Otherwise, if the local store exists, rewrite the pointer to match. Logs `[session-start] rewrote .git pointer → …` to stderr.
- If the local store is missing, log a warning pointing at this section and leave the pointer alone (user hasn't done one-time setup yet).

You can override the default store location with the `CLAUDE_WORKSPACE_GIT_STORE` env var (set in your shell profile or `.claude/settings.json` `env` block) if you want it somewhere other than `~/.git-stores/claude-workspace-system`.

After one-time per-machine setup, you should never need to think about the pointer again — it self-corrects on every Claude Code session start.

## Troubleshooting

### Hooks aren't firing
- Verify `.claude/settings.json` is present and valid JSON
- Verify Python is on PATH: `python --version` or `python3 --version`
- Check hook logs: Claude Code's `/hooks` command shows the current hook config
- Manually test: `python .claude/hooks/dispatcher.py session-start < /dev/null`

### Obsidian doesn't see installed plugins
- Open Settings → Community plugins → "Turn on community plugins"
- Plugins listed in `community-plugins.json` will be enabled; the files in `.obsidian/plugins/` will be loaded
- If a plugin is missing, re-run `python 00-bootstrap/setup/setup.py` — it re-downloads missing plugins

### Git refuses to push
- `gh auth login` — authenticate the GitHub CLI
- `gh auth setup-git` — wire gh into git credential helper
- Verify remote: `git remote -v`

### `fatal: bad object refs/desktop.ini` or `error: failed to perform geometric repack`
- Drive injected `desktop.ini` files into `.git/` subdirectories (or `.DS_Store` on macOS).
- Means this machine's `.git/` is still on Drive — needs the per-machine relocation. See "Git store lives off Drive" above.
- If you've already done the relocation and still see this: a `desktop.ini` snuck into the local store somehow. Run `find <local-git-store> -name "desktop.ini" -delete` (or `.DS_Store` on macOS) and re-try.

### Drive shows `file (1).md` duplicates
- Drive silent-conflict. Find both files, keep the right content, delete the other.
- This is why Git exists as a secondary layer — check `git log` for the real history.
