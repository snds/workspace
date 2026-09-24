# Claude Adapter — Claude Code / Desktop

@AGENTS.md

_This is the **Claude adapter** over the universal contract in [AGENTS.md](AGENTS.md). It describes
only how Claude executes that contract (hooks, slash commands, the session-start ritual). The contract
itself — folder semantics, read order, the skill loading algorithm, the routing map — lives in
AGENTS.md and is not duplicated here. Auto-loaded into every Claude Code session run from this directory._

---

## What this is

The workspace is Sean's cross-device, **portable** design + engineering environment. The git checkout
is the source of truth; the plain filesystem is the I/O layer. The same files serve several readers:

- **Obsidian** reads this folder as a vault — notes, MOCs, graph, templates.
- **Claude Code** (you) runs from here — loads context at session start, writes changes back.
- **Any other agent** (Cursor, Perplexity, a generic MCP client) enters via [AGENTS.md](AGENTS.md).

Whatever Obsidian sees, you see. Whatever you write, Obsidian sees on next focus. Nothing here requires
Google Drive or a vendor-specific file bridge — read and write ordinary files; git is the sync layer.

---

## Context — load these before acting

When starting a non-trivial task, read (in this order):

0. **[06-context/CRITICAL_FACTS.md](06-context/CRITICAL_FACTS.md)** — read FIRST: the tiny always-loaded hot cache of facts never to re-derive (who/where/the walls/freshness)
1. **[06-context/role-and-context.md](06-context/role-and-context.md)** — who Sean is, his work, specializations
2. **[06-context/project-context.md](06-context/project-context.md)** — pending stubs + `^pc-NN` (authoritative queue); long substance in `project-context-detail.md`; project narratives in `project-registry.md` (load on demand)
3. **[06-context/session-log.md](06-context/session-log.md)** — recent session entries, newest-first
4. **[06-context/artifact-registry.md](06-context/artifact-registry.md)** — structural index of known
   files. **Query it, never read it** (~6.9k tokens): `python3 09-tools/artifact-find.py "<terms>"`,
   `--path <fragment>`, or `--list` for the whole map at ~575. Still WRITE to it at session-end.
5. **[04-preferences/user-preferences.md](04-preferences/user-preferences.md)** — communication style, tone

The `SessionStart` hook loads these automatically. If the hook didn't fire (e.g., you were
invoked headless), read them explicitly before answering substantive questions.

---

## Session-start ritual (mandatory)

> **Cursor users:** `.cursor/rules/brain.mdc` is the Cursor-canonical override for this ritual. If both are loaded, follow `brain.mdc`. The format below is the Claude Code / Claude Desktop reference.

**Before responding to the user's first message in a new session,** emit the session-start
card. Prefer the injected `session-status.py` block from SessionStart. If the hook missed,
run `python3 09-tools/session-status.py --surface "Claude Code" --via project-hook/startup`
and print it. Do not invent a shorter summary.

The shape (notices above the ✓ line, all SESSION-STATE projects, pending count) is owned by
`09-tools/session-status.py`. Claude-only extras still apply:

- **Engine line:** one label-filtered `list_issues` per provisioned lane. Omit when every
  queue is empty or MCP is absent. Orphaned `Agent Working` claims: surface and ask.
- Worktree: if branch starts with `claude/`, append `· worktree: <name>` on the Git line.

Rules:
- **The first line is the machine-ABI ritual token** (`[workspace: LOADED · …]`).
- Do not skip the card because the user "just" asked something simple.
- After the ritual block, respond to the user's message normally.

This ritual is how Sean sees open work and what needs improvement on every surface, not only Claude.

**Surface posture:** Claude Code is **dispatch-heavy** (hooks inject context; slash skills
route work). Cursor is more **steer-heavy**. Prefer the posture the surface exposes — don't
fight it with always-on specialist method. See [[nate-jones-harness-enrichments]] §11 and
[[harness-map]].

---

## Frameworks, skills, knowledge, conventions (one home)

Standing law and folder semantics live in **[AGENTS.md](AGENTS.md)** — do not restate them here
(harness-map rec #3). Load on demand:

- Frameworks → [01-frameworks/00-README.md](01-frameworks/00-README.md) (+ `/framework-check`)
- Delivery / Proofboard / context profiles → [02-shared-references/delivery-playbooks/](02-shared-references/delivery-playbooks/)
- Skill routing → `python3 09-tools/skill-loadset.py "<utterance>"` (never ingest the registry)
- Knowledge → [08-knowledge/_INDEX.md](08-knowledge/_INDEX.md) before domain work
- QA always-load → framework #06 before audit/review/critique/refine work

### `.claude/skills/` — Claude Code slash workflows only

- `/today` · `/handback` · `/session-end` · `/reconcile` · `/new-project`
- `/framework-check` · `/optimize` · `/health` · `/harness-map` · `/mission-fit`

### Claude-only gates

- **Figma write gate:** first `use_figma` per session → PreToolUse design-judgment inject, then retry.
- **Machine labels** (session blocks): from `02-shared-references/devices.json` (macOS-only fleet).

## Paths + lifecycle (Claude execution)

- **Root:** nearest ancestor with `AGENTS.md`. **Remote:** `snds/workspace`.
- **Start** — SessionStart injects context; resume via project **Live handoff**.
- **End** — `/session-end` fragment + baton; see [.claude/skills/session-end/SKILL.md](.claude/skills/session-end/SKILL.md).
- Continuity contract: [AGENTS.md](AGENTS.md) → Multi-agent continuity & handoff.
