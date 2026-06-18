---
tags: [workspace, infrastructure, claude-code, obsidian, git, drive, ssh, github, multi-identity, sync-monitoring]
created: 2026-04-28
updated: 2026-06-17
status: stable
confidence: high
sources: [session-log 2026-04-23, session-log 2026-04-25, session-log 2026-04-27, session-log 2026-05-07]
related_skills: [workspace-bootstrap]
related_projects: [00-obsidian]
---

# Workspace Infrastructure — Accumulated Learnings

How the Claude Workspace system was built, why it was built that way, and what we learned building it. This is the "why" behind the setup — the skills tell you how to use it.

> **Status (2026-06-17): migrated off Google Drive.** The workspace is now a plain git checkout — git is the sync layer and the source of truth, with Obsidian as a vault reader (see [CLAUDE.md](../../CLAUDE.md) → Paths and memory `decision-portable-workspace-refactor`). Sections below that describe Google Drive sync, `My Drive` paths, or the legacy `claude-workspace-system` repo are retained as **historical learnings from the Drive era**, not current operations. Do not look to Google Drive for any workspace state, context, or sync.

---

## The Core Topology (and Why It's This Way)

The workspace has several consumers reading the same filesystem: **Obsidian**, **Claude Code**, and other agents (Cursor, a generic MCP client). The architectural decision was to use the **filesystem as the contract** — no API bridge, just plain files that git syncs across machines.

**Why this works:** git syncs the tracked files to all machines. Claude Code reads/writes local files; Obsidian reads the same vault; any other agent reads the same ordinary files. No translation layer needed.

**The critical insight about deployment location:** The integration's deployed files (CLAUDE.md, `.claude/`, `.obsidian/`, MOCs) live at the **workspace root** — not inside a project subfolder. This is because:
- Claude Code finds CLAUDE.md by walking parents from the CWD
- Obsidian identifies a vault by the presence of `.obsidian/`
- Git wants `.gitignore` next to `.git/`

Early sessions put these in `07-projects/00-obsidian/` thinking that was "the project." That was wrong. The project folder holds design/state docs only. The integration deploys to the root, same as any installable tool.

---

## Git Sync Strategy

Git is the single sync + source-of-truth layer (Drive is no longer in the picture — see the status banner above). What crosses machines is exactly what git tracks; everything else is machine-local:

| Layer | System | What It Covers |
|-------|--------|---------------|
| Version control + cross-machine sync | Git → GitHub | CLAUDE.md, .claude/, .obsidian/, 00-bootstrap/, 01-frameworks/, 02-shared-references/, 03-skills/, 04-preferences/, 06-context/, MOCs, whitelisted 07-projects/ |
| Machine-local (not synced) | .gitignore | 05-artifacts/, most of 07-projects/, .claude/state/, daily notes |

**The .gitignore strategy:** Uses `*` (ignore everything) then explicit `!directory/` whitelist entries. This means adding a new section to git requires explicitly adding it to the whitelist. The gitignore IS the source of truth — the session-end dispatcher uses `git add -A` safely because of this.

---

## The Drive Desync Problem (and the Fix)

**The bug:** Google Drive's stat-cache can lie to git. After Drive syncs files, git's index sometimes shows phantom modified/deleted entries for files that weren't touched. `git add -A` in that state would commit fictitious deletions and corrupt main.

**Detection:** Count deletions in `git status`. If above `STALE_DELETION_THRESHOLD = 5`, assume the working tree is out of sync with HEAD. Fall back to staging only a safe-paths allowlist.

**The fix (defense-in-depth):**
1. `_classify_worktree_state()` in dispatcher.py detects phantom entries + excessive deletion count
2. `_content_hash_stage()` uses `git hash-object` + `update-index --cacheinfo` to bypass stat-cache when staging allowlisted files
3. A desync notice is written to `.claude/state/desync-notice.md` and surfaced at next SessionStart
4. `core.checkStat=minimal` + `core.trustctime=false` set as belt-and-suspenders
5. Worktrees created by Claude inside the Drive folder are auto-cleaned after their branch merges into main

**The upstream bug:** `ensure_local_gitdir()` was stomping per-worktree gitdir pointers by looking for `.git` files containing `/worktrees/` — this broke linked worktrees. Fixed by adding that path check.

---

## Hook Dispatcher Architecture

All Claude Code lifecycle events route through a single Python file: `.claude/hooks/dispatcher.py`.

**Events handled:**
- `SessionStart` — loads context (project-context.md + session-log.md), runs worktree cleanup, surfaces notices
- `UserPromptSubmit` — trigger-word routing (loads relevant skills/context for "legion", "centric", "icon font", etc.)
- `Stop` — stages session-log changes
- `SessionEnd` — safety-check then `git add -A`, commit, push

**Python binary strategy:** The dispatcher must be called with `python3` (not `python`) because macOS typically doesn't have a bare `python` binary. Windows uses a `python3.bat` shim installed by the setup script. `.claude/settings.json` calls `python3` explicitly.

**stdlib-only constraint:** The dispatcher uses only Python standard library modules (no pip installs). This ensures it works on any machine without environment setup.

---

## Multi-Machine Context

Multiple machines, all consuming the same git-synced workspace:

| Hostname | Label | OS |
|----------|-------|----|
| `Voyager-2.local` | Personal MacBook Pro | macOS |
| `seansands.local` | Work MacBook Pro | macOS |
| `CS-KQ23N94M0W` | Work MacBook Pro (loaner) | macOS |
| `CS-K746DRWXY1` | Work MacBook Pro (main, going forward) | macOS |
| `Enterprise` | Windows Desktop | Windows 11 |

Git identity is repo-local: `snds` / `570874+snds@users.noreply.github.com`. This keeps the workspace commits separate from work-machine git defaults and preserves email privacy in the public commit log.

---

## Session Lifecycle Pattern

```
SessionStart → load context → surface pending + notices
  ↓
Work → use tools freely, update context files as state changes
  ↓
SessionEnd (/session-end) → write session block → safety-check → git add -A → commit → push
```

**Reconciliation:** When work happens across multiple machines in the same day, `/reconcile` merges the session blocks from each machine's session log into a single chronological entry.

---

## What to Remember When Resuming Infrastructure Work

- The dispatcher is the single point of configuration for all hook behavior. Read it before touching hooks.
- The `.gitignore` whitelist is the definitive list of what's tracked in git. Add new sections there first, then they'll be picked up by `git add -A`.
- The `STALE_DELETION_THRESHOLD = 5` heuristic is a judgment call — if it's too sensitive (false positives), raise it; if it's too permissive (missed desyncs), lower it.
- Off-Drive worktrees (`~/.claude-worktrees/`) are never auto-cleaned — only Drive-resident worktrees with fully-merged branches get cleaned.

---

## Drive Sync Monitoring (macOS Migration Pattern)

When a fresh machine is added (new laptop, loaner swap, reset device), Google Drive for Desktop streams the entire workspace down on demand. During this phase, Obsidian hangs on vault open because every `stat()` on a placeholder file triggers a File Provider RPC. You need a way to know when sync is "done enough" to safely use the workspace.

**The signal: macOS `UF_DATALESS` chflag (`0x40000000`).** Drive for Desktop sets this flag on every file it has metadata for but hasn't downloaded content for ("placeholders"). When dataless count → 0 and on-disk size has stopped growing, sync is complete.

**Detection:**
- Shell: `find . -type f -flags +dataless`
- Python: `os.scandir() + entry.stat().st_flags & 0x40000000`

**Performance trap.** A bash audit that does multiple separate `find` traversals (one per metric — count, dataless count, apparent size, on-disk size) does NOT finish in 10+ minutes during heavy sync. Each traversal serially stat()s every file. The fix is a single Python `os.scandir()` walk that accumulates all metrics in one pass. Even then, expect ~30-40 min per scan on a 125K-file workspace mid-sync.

**Workspace-specific patterns from the 2026-05-07 migration:**
- 99.98% of pending placeholders concentrated in `07-projects/` (the project content). System layer (`01-frameworks`, `03-skills`, `06-context`, dotfiles) syncs fast.
- Bytes complete long before files complete — Drive prioritizes large files first, leaving the long tail of small files for last. Watch *file* count, not byte progress, as the gating signal.
- Drive strips macOS executable bits in transit on at least some script files (`dispatcher.py` mode `100755` → `100644`). After sync, `chmod +x` any tracked scripts that need it. Diff-detect with `git diff --raw` to see mode changes.

**Tooling:** `~/drive-sync-tools/{drive-audit,drive-monitor}.py` (planned: move into `08-tools/`). Single-pass scan, top-level breakdown, monitor auto-exits when 0 placeholders + on-disk size stable for 2 ticks.

---

## Multi-Identity GitHub on a Single Machine

When a machine needs to interact with two GitHub accounts — e.g., a Centric-issued work laptop that handles both personal repos (Claude Workspace pushes to `snds`) and Centric work repos (`sean-sands-centric` account, cpes-software org access) — the clean separation pattern has four layers:

**Layer 1 — One SSH key per account.** Not per repo, not per machine.
```
~/.ssh/id_ed25519_personal  → auths to GitHub user `snds`
~/.ssh/id_ed25519_work      → auths to GitHub user `sean-sands-centric`
```
Each pubkey gets pasted into its respective GitHub account's Settings → SSH keys.

**Layer 2 — SSH host aliases.** `~/.ssh/config` makes `github.com` and a virtual `github-work` route through different keys:
```
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_personal
  IdentitiesOnly yes

Host github-work
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_work
  IdentitiesOnly yes
```
Personal clones use `git@github.com:snds/...`, work clones use `git@github-work:cpes-software/...`. The hostname `github-work` is fictional — only SSH knows about it; GitHub sees both as `github.com` connections, distinguished by which key authenticates.

**Layer 3 — No global git identity.** Two ways to scope identity per repo:
- Repo-local config (explicit, what the workspace already does): `git config user.email ...` after each clone
- Directory-based (automatic, planned for future repos): `~/.gitconfig` with `[includeIf "gitdir:~/work/"]` and `[includeIf "gitdir:~/personal/"]` blocks pulling in `~/.gitconfig.work` / `~/.gitconfig.personal`

**Layer 4 — Workspace as anchored personal context.** The Claude Workspace can run from any laptop (Drive-synced) but always commits as personal:
- gitdir at `~/.git-stores/claude-workspace-system/` (per-machine, not synced)
- Repo-local: `snds` / `570874+snds@users.noreply.github.com`
- Remote URL routes through `github.com` alias = personal SSH key
- Result: even when used from a Centric work laptop, every commit is unambiguously personal — no risk of work email leaking into the public-ish snds repo log.

**Workspace clone procedure (fresh machine).** `.git` in the workspace is a pointer file — `gitdir: ~/.git-stores/claude-workspace-system`. To populate that gitdir without re-downloading the working tree (Drive already has it):
```
git clone --no-checkout \
  --separate-git-dir=~/.git-stores/claude-workspace-system \
  git@github.com:snds/claude-workspace-system.git \
  /tmp/cw-init

git --git-dir=~/.git-stores/claude-workspace-system \
  config core.worktree "/Users/.../My Drive/Claude Workspace"
rm -rf /tmp/cw-init

cd "/Users/.../My Drive/Claude Workspace"
git reset --mixed HEAD   # populate index from HEAD; --no-checkout left it empty
git config user.name "snds"
git config user.email "570874+snds@users.noreply.github.com"
```
After `git reset --mixed`, expect a small set of legitimate diffs (work from other machines that hasn't been pushed yet, plus the occasional Drive-stripped exec bit). These belong to Step 7.5 of `/session-end`, not to be auto-committed.
