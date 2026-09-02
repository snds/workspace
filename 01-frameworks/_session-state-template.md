# SESSION-STATE.md — Template Specification

_Location: `01-frameworks/_session-state-template.md`_
_Specified by: Last-Mile Craft Framework, "Operational state" section_

---

## Purpose

Per-project operational continuity between sessions. Each active project maintains its own `SESSION-STATE.md` at the root of the project folder. The workspace-bootstrap skill loads this file automatically when a session resumes the project, eliminating the cost of re-establishing environment context through conversation.

**Explicit boundary.** This file captures operational state — what was running, where we paused, what's connected. It does NOT capture conversation history (that's `06-context/session-log.md`), design decisions (project docs or the Collaboration framework's shared archive), or code (versioned elsewhere).

**Rule of thumb.** If it would change if Sean moved to a different machine, or if a new Claude session wouldn't know it without being told — it belongs here. If it's information about the work itself, it belongs elsewhere.

---

## File structure

Two sections. The first is atomically rewritten each update (no stale fields accumulate). The second is append-only history.

```markdown
# SESSION-STATE — [Project Name]

_Last updated: [YYYY-MM-DD HH:MM] — [update reason: rolling | checkpoint | wrap-up]_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton — any agent reads this FIRST, updates it on every handoff)
> This is the cross-agent continuity record. Per [[AGENTS]] → "Multi-agent continuity & handoff", any
> agent (Claude, Cursor, Perplexity, a local model, a human) picks up *exactly here*. Keep it current,
> not just at session end. Rewrite atomically — no stale fields.

- **TL;DR (for future agent)**: [one line — what this project is + where it stands right now]
- **Current focus**: [the one thing being worked on right now]
- **Working set**: [files/areas currently in play — where the next agent should look]
- **Last action**: [what was just done] — by [Agent · Surface · Machine]
- **Next action**: [the immediate next step, concrete enough to execute cold]
- **Open decisions**: [anything awaiting a call — and the options on the table]
- **Blocked on**: [external dependency, approval, the user's input — or "nothing"]
- **In-flight / do-not-touch**: [uncommitted edits, half-done refactors another agent should not clobber]
- **Agent thread**: [last few handoffs, newest first — e.g. `Claude/Claude Code → Cursor (2026-06-16): wired registry; next = cross-links`]

### Environment
- **Context profile**: [`personal-solo` | `centric-engineering` | `centric-design` (+ `visibility: public` if applicable) — declared per `02-shared-references/delivery-playbooks/00-context-profiles.md`; governs repo conduct, delivery voice, and evidence target]
- **Machine**: [e.g. `seansands.local` (work Mac) | `Voyager-2.local` (personal Mac) | `Enterprise` (Windows desktop)]
- **OS context**: [e.g. macOS 14.4 / Windows 11 / Bazzite 40]
- **Workspace root**: [the git checkout root — the directory containing `AGENTS.md`]
- **Project root**: [absolute path to this project on this machine]

### Active servers and processes
- **Dev server**: [e.g. `vite` on port 5173 — running | not running]
- **Build process**: [e.g. `tsc --watch` — running | not running]
- **Test runner**: [e.g. `vitest --watch` — running | not running]
- **Other**: [database, backend, mock server, etc.]

### VCS state
- **Branch**: [e.g. `feature/icon-font-pipeline`]
- **Last commit**: [short SHA — commit message snippet]
- **Uncommitted changes**: [yes/no — if yes, note what area]
- **Test state at last check**: [passing | failing | not run]

### Active tooling / MCP bridges
- **Filesystem access**: [native (Claude Code) | filesystem MCP]
- **Playwright MCP**: [live | not connected | not applicable]
- **Figma MCP**: [live | not connected | not applicable]
- **Other MCP connections**: [list as relevant]
- **Note any connection issues** discovered this session.

### Configuration in use
- **Config files active**: [list — e.g., `qa-config.json`, `tokens-v3.2.json`]
- **Design token version**: [if applicable]
- **Framework config**: [specific to this project — e.g., Three.js r128 pinned, Python 3.11 via uv, etc.]

### Open work and paused threads
- **Currently in progress**: [one-line description]
- **Pending questions**: [things that need Sean's input to move forward]
- **Blocked on**: [external dependencies, approvals, hardware, etc.]
- **What's needed to resume**: [terse sentence so future-Sean doesn't rebuild context from memory]

### Known state of external dependencies
- **Staging environment**: [URL or version, if applicable]
- **API versions**: [production / staging / mock]
- **Asset pipeline**: [state of builds, exports, etc.]

---

## Session history (append-only)

_Newest first. Each entry is a checkpoint — silent rolling updates aren't logged here; only explicit checkpoints and wrap-ups._

### [YYYY-MM-DD HH:MM] — [wrap-up | checkpoint]

**Focus this session**: [one sentence — what was the work]
**Machine**: [which machine]
**Duration**: [approximate — optional]
**Stopped because**: [natural break | blocked on X | end of available time | Sean signaled done]

**Accomplishments**:
- [Key things done this session]

**Decisions made** (if any):
- [Only significant ones that don't live in project docs or shared archive]

**Next resumption needs**:
- [What future-Sean needs to know to pick up]

---

### [prior session entry...]

```

---

## Update cadence

Three update modes, handled by the workspace-bootstrap skill:

1. **Silent rolling updates during the session.** When Sean or Claude starts a dev server, switches branches, invokes a new tool, or changes configuration — Claude appends the change to the "Current state" section. No flow interruption. These updates don't create session history entries.

2. **Automatic checkpoint after meaningful pause.** After approximately 30 minutes of inactivity (configurable per-project via `BOOTSTRAP.md` if needed), Claude proactively writes a checkpoint entry in session history. This captures state in case the session is effectively ending.

3. **Explicit wrap-up checkpoint.** When Sean signals *"we're done"*, *"let's stop here"*, *"end of day"*, or similar — or Claude infers a clean stopping point — Claude writes a final *wrap-up* entry with crisp resumption context.

The "Current state" section is rewritten atomically on every update (silent or checkpoint). The "Session history" section is append-only, newest first.

---

## Integration with workspace-bootstrap

### At session start

When the bootstrap skill resolves which project is active (from explicit user mention or from session-log's last entry), it reads that project's `SESSION-STATE.md` and surfaces the "Current state" section + the most recent session-history entry. This gives Claude operational context without requiring Sean to re-explain what was running, which machine, etc.

Surface example at boot:

```
✓ Workspace loaded [DC] — resuming 14-variable-icon-font-generator
   Last session: 2026-04-20 wrap-up on Voyager-2.local
   State: on branch `feature/masters-v0.3`, uncommitted wght-axis work
   Needed to resume: decide on GRAD axis derivation approach
```

### During the session

Claude watches for signals that operational state has changed and appends silently:

- Starting/stopping dev servers.
- Switching branches or committing.
- Connecting/disconnecting MCP bridges.
- Changing active configs.
- User explicitly flagging a paused thread.

Claude does not ask permission for silent updates. They're maintenance, not decisions.

### At session end

Claude writes a wrap-up entry when Sean signals stop or when 30 min of inactivity passes. Entry includes Focus, Machine, Accomplishments, Decisions (if any), and Next resumption needs.

---

## Seeding a new project

For a project that doesn't yet have a `SESSION-STATE.md`:

1. Copy this template into `[project-folder]/SESSION-STATE.md`.
2. Fill in the "Current state" section with what's actually known at the time of seeding.
3. Add a seeding entry to session history: *"Seeded by [who] on [date]. Initial state reflects [what]."*

After that, the bootstrap skill takes over maintenance.

---

## What goes where — quick reference

| Information type | Where it lives |
|---|---|
| What was running, which machine, paused thread | **SESSION-STATE.md** (this file, per project) |
| What we did this session | Partial overlap — brief summary here, full log in `06-context/session-log.md` |
| Design decisions and rationale | Project docs or DDRs (governed by ds-advisor / design-engineer skills) |
| Cross-project outcomes / disagreements | Collaboration framework's shared archive |
| Code content, branch history, commit messages | Git — don't duplicate here |
| Framework principles | `01-frameworks/` — not project-specific |
| User preferences, role, project summaries | `06-context/*.md` |

The division of labor is worth enforcing. If every session-state file also contains design rationale and code notes, it becomes the one place everyone looks for everything — and that's exactly the bloat this file's narrow scope prevents.
