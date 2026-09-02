# Claude Adapter — Claude Code / Desktop

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
4. **[06-context/artifact-registry.md](06-context/artifact-registry.md)** — structural index of known files
5. **[04-preferences/user-preferences.md](04-preferences/user-preferences.md)** — communication style, tone

The `SessionStart` hook loads these automatically. If the hook didn't fire (e.g., you were
invoked headless), read them explicitly before answering substantive questions.

---

## Session-start ritual (mandatory)

> **Cursor users:** `.cursor/rules/brain.mdc` is the Cursor-canonical override for this ritual. If both are loaded, follow `brain.mdc`. The format below is the Claude Code / Claude Desktop reference.

**Before responding to the user's first message in a new session,** output a session-start summary in exactly this format. This is non-negotiable — Sean works across surfaces (Claude Code, Cursor, VS Code, iOS app), machines (Mac, Windows, Linux), and contexts (personal, Centric employer work). A consistent visible summary is how he confirms the brain loaded correctly and re-orients regardless of where he is.

Render it as a markdown block, exactly this shape, before any other response:

```
[workspace: LOADED · {branch}@{short-sha} · {YYYY-MM-DD} · via:{project-hook | user-hook | prompt-hook}/{startup | resume | compact}]
**✓ Workspace loaded** — {Machine label} · {YYYY-MM-DD HH:MM TZ}

- **Surface:** {Claude Code (Mac desktop app) | Claude Code (Windows desktop app) | Cursor | VS Code | iOS | etc. — best inference from environment}
- **Last session:** {YYYY-MM-DD} — {one-line title from session-log.md}
- **Pending:** {N} items → see [06-context/project-context.md](06-context/project-context.md)
- **Engine:** {lane} — {N hold · N queued · N claimed} · {lane} — clean   ← omit this line entirely when every lane's queue is empty
- **Active projects ({N}):**
  - **{folder-name}** ({last-updated date}) — {first-line title from latest SESSION-STATE.md entry}
  - ...
- **Git:** `{branch}` @ `{short-sha}`, {clean | N modified} {· worktree: {worktree-name} if applicable}

What's on the agenda today?
```

Rules:
- **The first line is the machine-ABI ritual token** (`[workspace: LOADED · …]`) — frozen ABI per
  memory `decision-bootstrap-v2-guarantee`; the machine layer's SessionEnd audit greps assistant
  output for `workspace: LOADED` and logs a MISS without it (FX-16, 2026-07-09). The `via:` layer
  comes from the hook that injected context (in-workspace = `project-hook`).
- Pull data from the SessionStart hook's injected context (`06-context/project-context.md` head + `06-context/session-log.md` head). If a field can't be determined, omit that line rather than guess.
- Limit "Active projects" to those with `SESSION-STATE.md` files in `07-projects/*/`. List all of them, not a curated subset.
- If the session is in a worktree (branch starts with `claude/`), append `· worktree: <name>` to the Git line so Sean knows.
- Do not editorialize, do not skip the format because the user "just" asked something simple, do not summarize differently each session. The format IS the deliverable.
- If `06-context/role-and-context.md` or related context files weren't injected by the hook (e.g., headless invocation), read them via the Read tool first, THEN output the ritual.
- After the ritual block, respond to the user's message normally.
- **If the SessionStart context contains a `## Notices` section, render those notices as bulleted warnings AT THE TOP of the ritual block (above the ✓ Workspace loaded line) so they're impossible to miss.** Notices include Claude Code version changes, stale workspace audits (`/optimize`), and a **stale harness map** (>30 days since `07-projects/19-workspace-brain/reports/harness-map.stamp` — silent if no stamp yet; suggest `/harness-map`, not a blocker).
- **Engine line:** one label-filtered `list_issues` per _provisioned_ lane (id/title/status only), counted locally. **Omit the line entirely when every queue is empty**, and omit it silently if the MCP transport is absent — a missing line must never read as "empty". Report only; never claim at session start. An issue in `Agent Working` is an **orphaned claim** — surface it and ask, never silently re-claim. Procedure: [[open-agent-engine]] → Ritual integration.

This ritual costs ~150 tokens per session start in exchange for cross-surface continuity and reliable confirmation that the brain loaded.

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
- Skill routing → [trigger-routes.md](02-shared-references/trigger-routes.md) + `03-skills/skills.registry.json`
- Knowledge → [08-knowledge/_INDEX.md](08-knowledge/_INDEX.md) before domain work
- QA always-load → framework #06 before audit/review/critique/refine work

### `.claude/skills/` — Claude Code slash workflows only

- `/today` · `/handback` · `/session-end` · `/reconcile` · `/new-project`
- `/framework-check` · `/optimize` · `/health` · `/harness-map` · `/mission-fit`

### Claude-only gates

- **Figma write gate:** first `use_figma` per session → PreToolUse design-judgment inject, then retry.
- **Machine labels** (session blocks): `Voyager-2.local`→Personal MBP · `seansands.local` /
  `CS-KQ23N94M0W` / `CS-K746DRWXY1`→Work MBP · `Enterprise`→Windows.

## Paths + lifecycle (Claude execution)

- **Root:** nearest ancestor with `AGENTS.md`. **Remote:** `snds/workspace`.
- **Start** — SessionStart injects context; resume via project **Live handoff**.
- **End** — `/session-end` fragment + baton; see [.claude/skills/session-end/SKILL.md](.claude/skills/session-end/SKILL.md).
- Continuity contract: [AGENTS.md](AGENTS.md) → Multi-agent continuity & handoff.
