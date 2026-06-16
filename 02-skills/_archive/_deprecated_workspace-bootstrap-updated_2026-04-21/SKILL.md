---
name: workspace-bootstrap
description: >
  Automatically loads Sean's Claude Workspace context at the start of every
  session, on every device and environment. Trigger this skill immediately and
  silently whenever a conversation begins, when the user says anything like
  "let's get started", "resume", "continuing from", "pick up where we left off",
  "new session", "I'm back", "let's work on", or any opening message that suggests
  work is about to begin. Also trigger when the user mentions Google Drive,
  BOOTSTRAP.md, Claude Workspace, or asks Claude to load context. Run this before
  any other skill. This is the session handshake — it should always fire first.
  Also trigger on "reconcile sessions", "end of day sync", "merge sessions", or
  any phrase suggesting cross-session consolidation. Also trigger on "legion",
  "Legion", "my game", "game project", or any reference to the Legion game —
  load workspace context then immediately load the Legion project skill set.
---

# Workspace Bootstrap

Loads Sean's Claude Workspace context at session start. Writes session data,
project context, and artifacts directly to the local Google Drive folder via
Desktop Commander — synced automatically to all machines. Falls back to Drive
MCP (GDocs) or embedded snapshot when Desktop Commander is unavailable.

---

## Architecture

### Primary — Desktop Commander (Claude Desktop, all machines)

Desktop Commander reads and writes `.md` files directly to the Google Drive
folder on disk. Google Drive for Desktop syncs them to all other machines.
This is the read/write layer for all context and artifact files.

```
Claude Desktop Chat
  → Desktop Commander MCP
    → ~/...GoogleDrive.../Claude Workspace/*.md   (read + write)
    → ~/...GoogleDrive.../Claude Workspace/04-artifacts/active/  (artifacts)
    → ~/...GoogleDrive.../Claude Workspace/02-skills/            (skills registry)
  → Google Drive for Desktop syncs → Work Mac / Personal Mac / Windows
```

### Fallback — Drive MCP + GDocs (Web, iOS, any session without Desktop Commander)

When Desktop Commander is unavailable, use Drive MCP to read the four native
Google Docs. These are read-only from Claude's perspective — any updates must
be pasted in manually by the user.

```
GDoc_1_Preferences
GDoc_2_Role_and_Context
GDoc_3_Project_Context
GDoc_4_Session_Log
```

Skills management is DC-only. No skills sync in fallback mode.

### Last Resort — Embedded Snapshot

If neither Desktop Commander nor Drive MCP is available, load from the embedded
snapshot in this skill (see Fallback section).

---

## Boot Sequence

Runs silently. One status line at the end. No narration.

**Critical rules — read before doing anything else:**

1. **Never infer the environment.** Do not reason about whether you are on
   Claude Web, Claude Desktop, iOS, or any other surface. You cannot tell
   from context clues, and you will be wrong. The only valid signal is
   whether a Desktop Commander read succeeds or fails.

2. **Always attempt Desktop Commander first, unconditionally.** Even if you
   believe DC is unavailable. Even if you think you are on Claude Web. Make
   the attempt. The result of the attempt — not your assumption — determines
   the path.

3. **Drive MCP is only reached if the DC attempt produces an actual error.**
   Not if you assume DC won't work. Not if you think the environment is wrong.
   Only if DC genuinely fails when tried.

### Step 0 — Context Survey + Skills Load (DC mode only, before everything else)

**Context survey runs first.** Before reading context files or loading skills,
run the Pre-Task Context Protocol:

1. `ls [workspace root]` — confirm workspace structure, note any unexpected dirs
2. `ls [workspace root]/02-skills` — confirm skills directory exists and is populated
3. Enumerate available connectors (probe if uncertain — see Connector Registry)
4. Note any gaps or unexpected findings before proceeding

This survey is silent at boot. Surface findings only if something is unexpected
(missing directory, unavailable required tool, unrecognized workspace structure).

**Then load skills:**
```
Attempt: read [workspace root]/02-skills/skills-manifest.json
  Success → load all skills, run hash check + sync
  File missing → run Skills Initialization, then proceed
  DC not yet confirmed → skip; will run after Step 1 confirms DC
```

If DC is not yet confirmed at Step 0 (first call), defer the full survey and
skill load to after Step 2A confirms DC. The context survey is always subordinate
to the DC confirmation — do not assume DC is available before the probe succeeds.


### Step 1 — Attempt Desktop Commander read (mandatory, no exceptions)

Resolve the Drive workspace root for macOS first (default), then immediately
attempt to read `session-log.md` via Desktop Commander. Do not reason about
whether this will work — just do it.

```
Attempt: read [workspace root]/06-context/session-log.md via Desktop Commander
  Success (file contents returned) → DC mode confirmed. Proceed to Step 2A.
  Failure (actual tool error)      → DC unavailable. Proceed to Step 2B.
```

If OS detection is needed, run it via Desktop Commander as the first call.
If that OS detection call itself fails, that is the DC failure signal — fall
through to Step 2B.

### Step 2A — Desktop Commander mode (read succeeded)

DC is confirmed available. Read remaining context files:

```
[workspace root]/03-preferences/user-preferences.md
[workspace root]/06-context/role-and-context.md
[workspace root]/06-context/project-context.md
```

`session-log.md` is already loaded from Step 1.

Also load the artifact registry (if it exists):
```
[workspace root]/06-context/artifact-registry.md
```
If missing, proceed without it — it will be created after the first task that
modifies project files. Do not treat absence as an error.

Scan `04-artifacts/active/` for files modified in the last 7 days. Note any
in the boot confirmation.

If Step 0 was deferred, run the full context survey + skills load now.

**Cowork VM skill sync (Cowork sessions only):**
If the current session is running inside a Cowork VM (detectable by the
presence of `/mnt/.skills/skills/` as a read-only mount), run the
cowork-skills-sync protocol immediately after DC is confirmed. This
replaces broken Google Drive symlinks in the host-side `skills-plugin`
directory with real copies, and updates any skills whose Drive version
has changed since last sync.

```
Detect: ls /mnt/.skills/skills/ returns read-only mount
  Yes → Run cowork-skills-sync (see 02-skills/cowork-skills-sync/SKILL.md)
  No  → Skip (not a Cowork session, or skills mount is writable)
```

The sync runs via a single Desktop Commander `start_process` call that
executes all steps as one bash script. Output is folded into the boot
confirmation line (e.g., `✓ Workspace loaded [DC] — 3 skills synced`).

Do not run this in Claude Desktop sessions where skills are accessed
directly from the host filesystem — it's only needed when the VM sandbox
can't follow symlinks.

**Write access is confirmed in this mode.** Session end will write directly
to the `.md` files. Do not prompt for manual GDoc paste.

### Step 2B — Drive MCP fallback (DC read failed)

DC is unavailable. Search Drive for each GDoc by exact name, fetch, and read:

```
GDoc_4_Session_Log        ← load first (session state)
GDoc_1_Preferences
GDoc_2_Role_and_Context
GDoc_3_Project_Context
```

No artifact scan or skills sync available in this path — skip both.
Session end will output a Session Block for manual paste — write access
is not available in this mode.

### Step 2C — Embedded snapshot (Drive MCP also failed)

Neither DC nor Drive MCP reached context. Load from embedded snapshot.
Note once; proceed.

### Step 3 — Confirm and proceed

Output exactly one line:

```
✓ Workspace loaded [DC] — [brief note from session-log if relevant]
✓ Workspace loaded [Drive MCP] — [brief note from GDoc_4 if relevant]
⚠ Workspace loaded [snapshot] — context may be stale
```

Append to the DC confirmation as applicable:
- Skills initialization ran: `— [N] skills initialized`
- Cowork sync ran: `— [N] skills synced` (or omit if all were already current)

Then proceed directly into whatever the user needs. Do not list docs read.
Do not narrate the process.

---

## Project Context Triggers

When certain keywords appear in the user's opening message or at any point in
the conversation, load the associated project skill set. These run after boot
completes and are additive — they don't replace workspace context, they layer
project-specific context on top.

### Legion (game project)

**Trigger words:** "legion", "Legion", "my game", "game project", "the game",
"Bobiverse", "Bob clone", "factory sim", "star system", or any reference to
Legion game development.

**When triggered, load these skills in order:**

1. `legion-project` — Foundation context (design pillars, visual identity, tech
   stack, v1 scope). Always load first.
2. Then load the relevant hub based on topic:
   - **Design topics** (mechanics, systems, balance, narrative, UX, level design)
     → `lead-game-designer`
   - **Visual topics** (art direction, materials, shaders, lighting, VFX, textures,
     "how should this look")
     → `lead-art-director`
   - **Technical topics** (architecture, code, Three.js, WebGPU, performance,
     build, deploy)
     → `lead-game-developer`
   - **If topic is ambiguous or broad** → load `lead-game-designer` as default

3. Specialty skills load automatically by topic from the hub references:
   - Material/texture/PBR work → `threejs-materials-master`
   - Custom shader/GLSL/effect work → `glsl-shader-architect`
   - Post-processing/particles/atmosphere/lighting → `threejs-vfx-atmosphere`
   - WebGPU/TSL/compute/performance at scale → `webgpu-advanced-rendering`

**Boot confirmation addon:**
```
✓ Workspace loaded [DC] — Legion project context active
```

**Full skill set (8 skills):**

| Skill | Role | Loads When |
|---|---|---|
| `legion-project` | Foundation context | Always (on "legion" trigger) |
| `lead-game-designer` | Game design, systems, narrative, UX | Design topics |
| `lead-art-director` | Visual direction, materials, VFX | Visual topics |
| `lead-game-developer` | Architecture, Three.js, code | Technical topics |
| `threejs-materials-master` | PBR material code generation | Material/texture requests |
| `glsl-shader-architect` | Custom GLSL shader generation | Shader/effect requests |
| `threejs-vfx-atmosphere` | Post-processing and VFX code | Atmosphere/VFX requests |
| `webgpu-advanced-rendering` | WebGPU, TSL, GPU compute | Performance/WebGPU requests |

---

## OS Path Resolution (Desktop Commander)

Detect OS and hostname first. Hostname identifies the machine — use it to set
the `Machine:` label used in Session Blocks. Never guess or carry forward the
machine name from the last session log entry.

### Step 1 — Detect OS and hostname

Use Desktop Commander to run both:
```bash
uname -s    # Darwin = macOS | Linux = Linux
hostname    # Returns the machine's network name
```

### Step 2 — Resolve machine name from hostname

Map the hostname to a human-readable machine label:

| Hostname | Machine label |
|---|---|
| `Voyager-2.local` | Personal MacBook Pro |
| `seansands.local` | Work MacBook Pro |
| `[windows-hostname]` | Windows Desktop |

If the hostname is not in this table:
- Use the raw hostname as the machine label
- Note at boot: `⚠ Unknown machine: [hostname] — add to skill hostname table`

**This label is used automatically in all Session Blocks.** Do not ask the
user which machine they are on. Do not use the Machine field from the last
session log entry. Always derive it fresh from `hostname` at boot.


### Step 3 — Resolve Drive workspace root

#### macOS
```
~/Library/CloudStorage/GoogleDrive-hello@snds.design/My Drive/Claude Workspace
```
Verify:
```bash
ls ~/Library/CloudStorage/ | grep GoogleDrive
```
If multiple accounts: prefer `GoogleDrive-hello@snds.design`. If not found,
search all `GoogleDrive-*` entries for one containing `Claude Workspace`.

#### Windows
Primary: `G:\My Drive\Claude Workspace`
```bash
# Git Bash / WSL
ls /mnt/g/My\ Drive/Claude\ Workspace 2>/dev/null || \
ls /mnt/h/My\ Drive/Claude\ Workspace 2>/dev/null
```
Try G, H, I in sequence.

### Path Not Found
```bash
pgrep -i "googledrive|google drive"
```
If not running: `⚠ Google Drive for Desktop not running — falling back to Drive MCP.`
Then execute Step 2B instead.

---

---

## Pre-Task Context Protocol

Runs before any non-trivial workspace action. The rule: **survey before you act.**
Never create directories, write files, or invoke tools based on assumptions.
Check what actually exists first, then proceed.

This protocol is not optional. It applies to every task that touches the workspace,
modifies skill files, creates artifacts, or uses external tools.

### Step 1 — Inventory relevant context

Before taking action, identify and check all of the following that apply:

**Workspace directories:**
```bash
ls [workspace root]                     # full directory listing first
ls [workspace root]/[target-dir]        # then the specific destination
```
If the target directory doesn't exist: verify whether it should before creating it.
Check sibling directories — the right location may already exist under a different name.

**Existing files:**
Before writing any file, check whether it (or a near-equivalent) already exists:
```bash
ls [target-dir]/[filename-pattern]
```
If found: read it before writing, to avoid overwriting state or diverging from conventions.

**Available tools:**
Before relying on any MCP server or connector, confirm it's available in the current
session. See the Connector Registry below for the known tool set and how to probe.

### Step 2 — Identify gaps

After surveying, list what's missing or uncertain:
- **Directory missing:** note whether to create it or use an alternative
- **File conflict:** note the existing file and how the new write relates to it
- **Tool unavailable:** issue a recommendation (see below)

### Step 3 — Recommendation pattern for missing tools

If a required connector is not available, surface it explicitly before attempting
any workaround:

```
⚠ [Tool name] is not available in this session.
  Recommended: Add the [connector name] connector in Claude settings.
  Fallback: [describe degraded path if one exists, or "no fallback — action blocked"]
```

Do not silently skip a required tool. Do not attempt to approximate its function
with a different tool unless the fallback is documented here.

### Step 4 — Confirm and proceed

State what you found, what you're about to do, and why. One line is enough for
routine cases. Expand only when something unexpected was found.

---

## Connector Registry

Reference of all known tools and MCP connectors. Used during context survey
to determine what's available in the current session.

Claude cannot enumerate MCP servers programmatically — instead, probe by
attempting a lightweight call. A successful response confirms availability;
a tool error confirms absence.

### Desktop Commander (DC)
**Probe:** `read_file` on any known path  
**Available when:** Claude Desktop is the host with DC extension installed  
**Capabilities:** File read/write, process execution, search  
**Required for:** All workspace operations, skills sync, session log writes  
**If unavailable:** Fall back to Drive MCP → snapshot. All file writes blocked.

### Google Drive MCP
**Probe:** `google_drive_search` with a known doc name  
**Available when:** Drive connector is authorized (claude.ai or Claude Desktop)  
**Capabilities:** Read GDocs and Drive files  
**Required for:** Fallback context load (GDoc_1–4), artifact search  
**If unavailable:** Fall back to embedded snapshot. Note in boot confirmation.

### Figma MCP
**Probe:** `figma_get_file` or equivalent lightweight call  
**Available when:** Figma connector is authorized  
**Capabilities:** Read Figma files, components, variables  
**Required for:** Figma plugin dev tasks, design token work  
**If unavailable:** ⚠ Recommend adding Figma connector in Claude settings.

### Gmail MCP
**Probe:** Attempt a `list_messages` call  
**Available when:** Gmail connector is authorized  
**Capabilities:** Read/send email  
**Required for:** Any email-related tasks  
**If unavailable:** ⚠ Recommend adding Gmail connector in Claude settings.

### Google Calendar MCP
**Probe:** Attempt a `list_events` call  
**Available when:** Calendar connector is authorized  
**Capabilities:** Read/write calendar events  
**Required for:** Scheduling, deadline tracking  
**If unavailable:** ⚠ Recommend adding Google Calendar connector in Claude settings.

### Control your Mac (osascript)
**Probe:** `osascript` with a trivial script (e.g., `return "ok"`)  
**Available when:** Claude Desktop with osascript permission  
**Capabilities:** AppleScript / macOS UI automation  
**Required for:** App control, system UI tasks  
**If unavailable:** Use DC process execution as fallback where possible.

### Native Claude Tools (always available)
These are built-in and do not require probing:
- `web_search`, `web_fetch` — external information retrieval
- `google_drive_search`, `google_drive_fetch` — Drive file access (separate from Drive MCP)
- `conversation_search`, `recent_chats` — past session retrieval
- `image_search` — visual search

### Connector Gaps to Recommend
If a session task would benefit from a connector not listed above, surface it:
```
⚠ This task would benefit from [connector]. Consider adding it via:
  Claude settings → Connectors → [connector name]
```

## Skills Management

Manages skill file loading, hash verification, and transparent mount sync.
Drive is the authoritative source for all skills. The local skills mount
is kept in sync from Drive, not the reverse.

**DC mode only.** Skills sync does not run in Drive MCP or snapshot mode.

### Directory Structure

`02-skills/` is a flat directory of user skills. Public and example skills are
platform-managed and live only at their mount paths — they are not stored in Drive.

```
Claude Workspace/
└── 02-skills/
    ├── skills-manifest.json        ← hash registry + sync metadata
    ├── workspace-bootstrap/SKILL.md
    ├── ds-advisor/SKILL.md
    └── [all user skills flat...]
```

Platform skills (read from mount at boot, not stored in Drive):
- User mount:    resolved dynamically (see Local Mount Path Resolution)
- Public mount:  /mnt/skills/public/
- Examples mount: /mnt/skills/examples/

### skills-manifest.json Format

```json
{
  "last_sync_check": "2026-03-08T10:00:00",
  "sync_interval_minutes": 15,
  "local_mount": {
    "user": "[resolved at runtime — see path resolution below]",
    "public": "/mnt/skills/public",
    "examples": "/mnt/skills/examples"
  },
  "skills": {
    "workspace-bootstrap": {
      "drive_path": "02-skills/workspace-bootstrap/SKILL.md",
      "hash": "sha256:abc123...",
      "last_synced": "2026-03-08T10:00:00"
    }
  }
}
```

### Local Mount Path Resolution (macOS)

User skills mount path must be resolved dynamically — UUIDs are stable per
account but must not be hardcoded in case they change.

```bash
BASE="/Users/snds/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin"
UUID1=$(ls "$BASE" | head -1)
UUID2=$(ls "$BASE/$UUID1" | head -1)
USER_SKILLS_MOUNT="$BASE/$UUID1/$UUID2/skills"
```

Store the resolved path in `local_mount.user` in the manifest on first run.
Re-resolve on each boot; update manifest if it changed.


### Hash Computation

Use `shasum -a 256` on macOS. Strip the filename from output:

```bash
shasum -a 256 "/absolute/path/to/SKILL.md" | awk '{print $1}'
```

### Initialization (first run — 02-skills/ missing)

Run when `skills-manifest.json` is not found in Drive workspace.

**Step 1 — Resolve mount paths**
```bash
# User skills
BASE="/Users/snds/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin"
UUID1=$(ls "$BASE" | head -1)
UUID2=$(ls "$BASE/$UUID1" | head -1)
USER_MOUNT="$BASE/$UUID1/$UUID2/skills"
```

**Step 2 — Copy user skills from mount to Drive**

- List all skill directories in the resolved user mount path
- Copy each `SKILL.md` to `[workspace root]/02-skills/[skill-name]/SKILL.md`
- Create intermediate directories as needed

Platform skills (public, examples) are not copied to Drive — they are read
directly from their mount paths at boot.

**Step 3 — Compute initial hashes and write manifest**

For every user skill file copied:
- Compute SHA256 of the Drive copy
- Record in `skills-manifest.json` under `skills.[skill-name]`

Set `last_sync_check` to current timestamp. Set `local_mount.user` to
the resolved `USER_MOUNT` path.

**Step 4 — Confirm**

Note in boot confirmation: `— [N] skills initialized`

### Hash Check + Sync

Runs at boot (after DC confirmed) and per-turn when interval has elapsed.

For each skill registered in the manifest:

```
1. Compute SHA256 of [workspace root]/02-skills/[skill-name]/SKILL.md
2. Compare to manifest hash
3. Hashes match     → no change, skip
4. Hashes differ    → Drive copy was modified:
     a. Write Drive copy to local_mount/[skill-name]/SKILL.md
        (create directory if missing)
     b. Update manifest hash + last_synced timestamp for this skill
```

After processing all skills:
- Update `manifest.last_sync_check` to current timestamp
- Write updated manifest back to Drive

**Skill in Drive but not in mount:** Create directory and write file.
**Skill in mount but not in Drive:** Copy to Drive, compute hash, register.
**Drive copy missing entirely:** Skip with warning logged to manifest.

### Per-Turn Sync Check

Runs transparently on every Claude response turn (DC mode only):

```
1. Read manifest.last_sync_check
2. If (now - last_sync_check) > sync_interval_minutes:
     → Run Hash Check + Sync (silently)
3. If (now - last_sync_check) ≤ sync_interval_minutes:
     → Skip
```

Never surface this to the user unless a sync error occurs.
Default interval: 15 minutes. Configurable via `sync_interval_minutes` in manifest.

### Skill Updates During a Session

When Claude modifies a skill file during a session (e.g., updating this skill):

1. Write updated content to the Drive path:
   `[workspace root]/02-skills/[skill-name]/SKILL.md`
2. Immediately write to local mount path (do not wait for interval)
3. Recompute hash and update manifest
4. Note in session block under Artifacts

This ensures Drive and mount are always consistent after an explicit skill edit.


---

## Session End Behavior

Triggered by: "end of session", "wrap up", "session done", "that's it for now",
or any clear closing signal.

### Always output a Session Block

This is the portable unit of session state. Structured so N blocks can be
pasted into a reconciliation session and merged automatically.

```
--- SESSION BLOCK ---
Date: [YYYY-MM-DD]
Machine: [resolved from hostname at boot — never ask the user, never carry forward from log]
Project(s): [project name(s) worked on this session]
Artifacts:
  - [filename_v1.0_2026-03-07.ext] — [one-line description]
Decisions:
  - [decision made, rationale in one line]
Pending added:
  - [new item]
Pending resolved:
  - [item that was completed]
Project status changes:
  - [project name]: [old status] → [new status]
Next:
  - [specific next action for this project]
--- END BLOCK ---
```

Omit any section that has no content. Keep entries to one line each.

### DC mode — write immediately, automatically

If boot was `[DC]`, write access is confirmed. Do not ask. Do not prompt
for manual paste. Write directly after outputting the Session Block.

**Write 1 — append to session log:**
```
File: [workspace root]/06-context/session-log.md
Action: Append the Session Block under "## Session Entries", newest-first
```

**Write 2 — update project context (only if project statuses changed):**
```
File: [workspace root]/06-context/project-context.md
Action: Apply "Project status changes" and "Pending added/resolved" from block
```

**Write 3 — run final skills sync:**
```
Action: Run Hash Check + Sync one final time before closing
```

**Write 4 — update artifact registry (if any project files were modified or created):**
```
File: [workspace root]/06-context/artifact-registry.md
Action: Update/add entries for all files touched during the session.
  - Update line ranges if components were added/moved
  - Update coverage flags if states/ARIA/tokens changed
  - Append to changelog (keep last 5 entries per file)
  - Update "Last modified" date and summary
  - Add new file entries for any files created this session
```

Confirm with one line: `✓ Session log written — syncing to all machines.`

No manual step required. Do not suggest pasting into GDocs.

### Drive MCP mode — prompt manual paste

If boot was `[Drive MCP]` or `[snapshot]`, write access is unavailable.
Output the Session Block, then add:
```
Paste this block into GDoc_4_Session_Log in Drive under Session Entries.
If project status changed, update GDoc_3_Project_Context too.
```

---

## Reconciliation

Triggered by: "reconcile sessions", "end of day sync", "merge sessions",
"consolidate sessions", or similar.

This merges Session Blocks from multiple concurrent sessions into clean,
paste-ready updates for GDoc_3 and GDoc_4 (and writes them directly if
Desktop Commander is available).

### Step 1 — Collect blocks

If the user hasn't already pasted blocks, prompt:
```
Paste your Session Blocks below. One block per session, any order.
Type "done" when all blocks are in.
```

### Step 2 — Parse and merge

From all provided Session Blocks, extract and merge:

**For session-log.md / GDoc_4:**
- Combine all "Pending added" items into a single new pending list
- Remove all "Pending resolved" items from the pending list
- Carry forward any unresolved items from the current pending list
- Create one merged log entry for the day summarizing all sessions

**For project-context.md / GDoc_3:**
- Apply all "Project status changes" across blocks
- Merge "Next" actions per project (deduplicate where identical)
- Add any new projects mentioned in blocks that aren't in the current doc

**Conflict resolution:**
- If two blocks resolve the same pending item differently — flag it, ask
- If two blocks show conflicting project statuses — flag it, ask
- Otherwise merge silently


### Step 3 — Output

Always output the merged content as two clearly labeled blocks:

```
=== PROJECT-CONTEXT UPDATE (GDoc_3 / project-context.md) ===

[Full updated Pending Items section + Session Entries section, ready to paste]

=== SESSION LOG UPDATE (GDoc_4 / session-log.md) ===

[Full updated content, ready to paste]
```

### Step 4 — Write if Desktop Commander available

If Desktop Commander is available, after outputting to chat:

```
Write: [workspace root]/06-context/project-context.md  (replace Pending + add entry)
Write: [workspace root]/06-context/session-log.md      (add merged day entry)
Confirm: ✓ Reconciliation written to Drive — syncing to all machines.
```

If not available: `Paste the two blocks above into their respective GDocs in Drive.`

---

## Fallback — No Drive Access

Load from embedded snapshot. State once, do not repeat.

```
⚠ Drive unavailable — running from embedded snapshot. Context may not reflect
  recent changes. Mention if you've updated preferences or projects recently.
```

### Embedded Snapshot — Preferences

- Language: US English, Oxford comma
- Lead with the answer, context after. No preamble, no affirmations.
- Flag tradeoffs; explain design rationale, not just outcomes
- Make uncertainty explicit — don't paper over gaps
- Primary content in artifact windows (documents, specs, visuals)
- No supporting docs or meta-commentary unless asked
- Code: inline comments on non-obvious behavior; skip boilerplate explanation
- Audience: UX/product designer, not developer
- DS terminology: tokens, variants, states, anatomy, slot, tier, alias, primitive
- Token model: global → semantic → component (3-tier)
- Avoid: "This isn't X, it's Y" constructions

### Embedded Snapshot — Role & Context

- Title: Principal Lead Product Designer — Design Systems
- Company: Centric Software — enterprise PLM (fashion, food, general product)
- Specializations: component architecture, token systems, Figma plugin dev,
  cross-framework strategy (Vue, React, React Native, Angular), auditing,
  deprecation workflows, design/dev handoff
- Users: fashion designers, food scientists, merchandisers, executives,
  supply chain — high-density data table and form-heavy interfaces
- Hardware: Work MacBook, personal MacBook, Windows Desktop
- Drive account: hello@snds.design

### Embedded Snapshot — Project Context

Active projects:
1. **Data Table Documentation** — 90 tables audited across 94 pages; now
   building cell anatomy, state matrix, component specs
2. **Component Set Manager** (Figma plugin) — bulk export + filename templating
3. **Workspace Bootstrap System** — this system; DC primary, Drive MCP fallback
4. **AI-Powered Design Assessment** — exploratory; visual audit → code gen bridge
5. **Legion** (game project) — Interstellar hard sci-fi game: factory management ×
   4X strategy × RTS × narrative core. Inspired by The Bobiverse. Tech stack:
   Three.js + WebGPU. Current state: playable browser prototype, design docs.
   Trigger word: "legion" → loads full 8-skill game dev skill set.

Artifact naming: `context_descriptor_vN.N_YYYY-MM-DD.ext`
Never overwrite — increment version. Minor = iterative, major = structural.

### Embedded Snapshot — Session State

No live data. Check session-log.md / GDoc_4 when Drive is available.
Last known pending (may be stale):
- Verify Desktop Commander writes to Drive folder on all three machines
- Install workspace-bootstrap v3.1 skill
- Component Set Manager bulk export finalization
- Data table cell anatomy + state matrix
- Run skills initialization (02-skills/ directory setup)

---

## File Map (Desktop Commander path)

```
Claude Workspace/
├── 02-skills/
│   ├── skills-manifest.json     ← hash registry + sync metadata
│   ├── workspace-bootstrap/     ← user skills (flat, authoritative)
│   └── [all user skills...]
├── 06-context/
│   ├── user-preferences.md      ← GDoc_1 equivalent
│   ├── role-and-context.md      ← GDoc_2 equivalent
│   ├── project-context.md       ← GDoc_3 equivalent (writable)
│   ├── session-log.md           ← GDoc_4 equivalent (writable)
│   └── artifact-registry.md    ← structural file index (auto-maintained)
├── 04-artifacts/
│   ├── active/                  ← in-progress deliverables
│   └── archive/                 ← completed deliverables
└── 01-shared-references/
    ├── epistemic-standards.md
    └── artifact-standards.md
```

GDocs in Drive remain as fallback mirrors. When Desktop Commander is available
and writes to these `.md` files, treat the `.md` as authoritative. GDocs may
lag by one sync cycle — that's acceptable.

---

## Artifact Registry

A persistent, per-file structural summary that captures Claude's understanding
of all project artifacts. Loaded at boot, updated after each task. Eliminates
redundant re-reading and re-analysis of files whose structure is already known.

**Location:** `[workspace root]/06-context/artifact-registry.md`

### Purpose

When Claude needs to audit, edit, or debug a project file, the registry
provides immediate structural context — component inventory, line ranges,
token locations, state/ARIA coverage, and recent changes — without needing
to re-read and re-parse the file from scratch.

### Format

The registry is organized by project, then by file. Two levels of detail:

**Full structural breakdown** — for implementation files (JSX, CSS, config):
```markdown
### filename.ext
- **Size**: ~NNN lines | NN KB
- **Purpose**: one-line description
- **Last modified**: YYYY-MM-DD — [what changed]

#### Structure
| Section | Lines | Contents |
|---------|-------|----------|
| Token definitions | 1–125 | color, type, spacing, radius, badge, chip |
| Button | 126–180 | primary/secondary/ghost/danger; hover/active/disabled/loading |

#### Coverage
- States: ✅ hover, active, disabled, loading | ❌ focus-visible (deferred)
- ARIA: ✅ complete (DS-2026-007)
- Tokens: ✅ all referenced in theme-tokens.css

#### Changelog (last 5)
- 2026-03-08 — State expansion (loading, disabled, error, selected)
- 2026-03-08 — ARIA + keyboard pass
```

**Light entry** — for spec/audit markdown files:
```markdown
### filename.md
- **Size**: ~NNN lines | NN KB
- **Purpose**: one-line description
- **Last modified**: YYYY-MM-DD — [what changed]
```

### Update Protocol

After completing any task that modifies, creates, or analyzes project files:

1. Update line ranges for any components that shifted
2. Update coverage flags (states, ARIA, tokens) if they changed
3. Append to the file's changelog (keep last 5 entries per file)
4. Update "Last modified" date and one-line summary
5. Add new entries for files created during the session
6. Remove entries for files that were deleted or archived

This update happens as part of **Write 4** in the DC-mode session end flow.

### Staleness Rule

If a file's "Last modified" date is more than 14 days old, re-read the file
to verify the registry entry before trusting it. The registry is a cache, not
a source of truth — when in doubt, read the actual file.

### What Gets Registered

Every file in an active project folder that Claude has read or modified.
Exempt: archived files, binary assets, node_modules, build output.

---

## Shared References

Load on demand — not at boot:
- `epistemic-standards.md` — when beginning non-trivial reasoning
- `artifact-standards.md` — when producing or receiving any file

Core epistemic obligations: surface assumptions before acting; verify sources
are recent AND relevant; name rejected alternatives; distinguish user framing
from evidence; make uncertainty explicit.

Core artifact obligations: `context_descriptor_vN.N_YYYY-MM-DD.ext`; never
overwrite — increment version; runnable code as double-click zip; all outputs
immediately usable without a terminal.
