# Claude Adapter — Claude Code / Desktop

@AGENTS.md

_This is the **Claude adapter** over the universal contract in [AGENTS.md](AGENTS.md). It describes
only how Claude executes that contract (hooks, slash commands, the session-start ritual). The contract
itself — folder semantics, read order, the skill loading algorithm, the routing map — lives in
AGENTS.md and is not duplicated here. Auto-loaded into every Claude Code session run from this directory._

---

## Context — read before acting

Read order: [AGENTS.md](AGENTS.md) → Canonical read order (`06-context/CRITICAL_FACTS.md` first).
The SessionStart hooks inject only the card, the session-log and project-context heads and a
knowledge note. Read the rest of that list yourself before substantive work, and all of it when no
hook fired (e.g. headless).

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
- Skill routing → [AGENTS.md](AGENTS.md) → Skill loading precedence
- Knowledge → matched `08-knowledge/` entries only (AGENTS.md read order step 7) before domain work
- QA always-load → framework #06 before audit/review/critique/refine work

### Workflow slash commands

`/today` `/side-chat-handback` `/session-end` `/reconcile` `/new-project` `/framework-check` `/optimize`
`/health` `/harness-map` `/mission-fit`: bodies in `03-skills/<name>/`; `.claude/skills/` holds generated wrappers.

### Claude-only gates

- **Figma write gate:** first `use_figma` per session → PreToolUse design-judgment inject, then retry.
- **Machine labels** (session blocks): from `02-shared-references/devices.json` (two Macs + Windows `Enterprise`).

## Paths + lifecycle (Claude execution)

- **Start** — SessionStart injects the card + log heads; resume via the project's **Live handoff**.
- **End** — `/session-end` fragment + baton; see [03-skills/session-end/SKILL.md](03-skills/session-end/SKILL.md).
- Continuity contract: [AGENTS.md](AGENTS.md) → Multi-agent continuity & handoff.
