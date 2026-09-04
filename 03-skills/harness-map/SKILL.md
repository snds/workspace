---
name: harness-map
description: >
  Map the AI harness around this workspace before cleaning or upgrading anything —
  instructions, skills, triggers, always-on rules, tools, permissions, validators,
  hooks, and receipts — then propose Keep / One home / Load later / Turn into check /
  Probation / Retire dispositions. Read-only first: nothing moves until Sean approves
  numbered changes. Run when Sean says "map the harness", "harness map", "clean my
  harness", "AI harness audit", "what's shaping the agent", or before a model/surface
  upgrade when the setup feels heavier than a fresh chat. Companion to mission-fit
  (jobs vs setup). Adapted from Nate B. Jones' Clean My AI Harness for this portable
  multi-surface workspace.
aliases: [harness-map, clean-my-ai-harness, ai-harness-audit]
triggers:
  - harness map
  - map the harness
  - clean my harness
  - clean my ai harness
  - ai harness audit
  - what's shaping the agent
  - harness audit
  - harness crud
tier: cross-cutting
domain: workspace
related: [mission-fit, workspace-bootstrap, open-agent-engine, side-chat-handback, intent-coordination]
surfaces: ["*"]
spec_version: "2.0"
---

# Harness map — see the setup before you clean it

A **harness** is everything wrapped around the model that this workspace (and the
current surface) can configure: contracts, always-on rules, skills, triggers, memory,
tools, permissions, hooks, validators, and checks. It shapes answers before the next
prompt. It does **not** include hidden vendor system prompts you cannot inspect.

This skill makes that setup **visible in one report**, separates what **protects**
the work from what creates **drag**, and proposes changes with explicit dispositions.
**The first run changes nothing.**

Standing project home for harness work: `07-projects/19-workspace-brain/` — read its
**Live handoff** when this skill runs as the session's main work.

Adapted from Nate B. Jones' *Clean My AI Harness* / harness-audit framing
([natesnewsletter](https://natesnewsletter.substack.com/p/ai-harness-audit)); localized
to [[AGENTS]], the skill registry, and multi-surface adapters — not a paste of his
Claude/Codex product zips.

## Non-negotiables

1. **Map before clean.** No deletions, merges, or always-on edits until Sean approves
   numbered recommendations.
2. **Blame the right layer.** Prefer a compact execution core + selective specialist
   load over stuffing method into every route. Richer analysis that fails delivery is
   still a fail — see the Fable compact-brief result in Nate's audit.
3. **One rule, one home, one owner.** Duplicated standing law is drag even when every
   copy is "correct."
4. **Hard requirements need hard checks.** Binary contracts (schema, word/file gates,
   permissions, validators) belong in machinery; judgment stays in prose.
5. **Coverage honesty.** Mark `INACCESSIBLE` / `NOT_EXPOSED` for vendor-hidden state.
   Never call unknown settings "clean."
6. **Archive, don't delete.** Retire via `_archive/` + `ARCHIVE-LOG.md` + repoint
   ([[AGENTS]] write-quality gates). Probation before retire when evidence is thin.

## When to run

- Explicit: "map the harness", "harness audit", "clean my harness", "what's loaded"
- Before upgrading the default model / surface when quality feels worse than a fresh chat
- When `/optimize` keeps finding the same duplication without a system-level map
- As the setup half before [[mission-fit]] (jobs vs harness)

**Not a substitute for** `/optimize` (entropy punch list) or [[open-agent-engine]]
(work movement). This skill answers: *what shapes the agent, and what should change?*

## Surface editions (same job, different hood)

Record the **active surface** in the report. Coverage differs:

| Edition | Inspect |
|---|---|
| **Workspace core** (always) | [[AGENTS]], `03-skills/skills.registry.json`, [[trigger-routes]], `01-frameworks/`, `02-shared-references/`, `06-context/` (head only for growing logs), `09-tools/validate*.py` + `build*.py`, write-quality gate chain |
| **Cursor** | `.cursor/rules/**` (`alwaysApply` especially), `.cursor/agents/`, User Rules / beacon if reachable, Cursor hooks if present |
| **Claude Code** | `CLAUDE.md`, `.claude/settings.json`, `.claude/hooks/`, `.claude/skills/` slash wrappers, SessionStart/UserPromptSubmit behavior |
| **Other** | Named adapter only (`PERPLEXITY.md`, etc.) + what that surface can actually see |

One run may cover **core + current surface**. Do not borrow another surface's receipt.

## Protocol

### 1 — Boundary + evidence grades

State: workspace root, branch@sha, surface, model if known, date.

Every claim in the map gets one grade:

| Grade | Meaning |
|---|---|
| `VERIFIED` | Read from disk / ran a tool / observed in this session |
| `USER_REPORTED` | Sean stated it; not independently checked |
| `INFERRED` | Reasonable from structure; not proven at runtime |
| `INACCESSIBLE` | Exists but this surface can't read it (permissions, private memory) |
| `NOT_EXPOSED` | Vendor/runtime state this product never shows |
| `NOT_APPLICABLE` | Wrong surface or out of scope for this edition |

### 2 — Inventory the harness (system map)

Collect, with paths and rough size where cheap:

**Always-on / early load**
- Contract + adapters: `AGENTS.md`, `CLAUDE.md`, `CURSOR.md`, `.cursor/rules/*.mdc` with `alwaysApply: true`
- Session ritual inputs: `06-context/CRITICAL_FACTS.md`, role, project-context **head**, session-log **head**, `memory/MEMORY.md`
- Beacon / doctor / hooks that fire without a user trigger

**Routed load**
- Skill catalog: count + how routing works (`triggers`, registry `load_chains`, curated [[trigger-routes]])
- Discovery pressure: total description-character budget if measurable; flag catalogs that will be truncated on surfaces with a skill-list budget
- Top always-fired or overlapping trigger clusters (sample hubs; don't read every spoke)

**Enforcement**
- Validators (`validate-integrity`, `validate-links`, `validate-capabilities`, `validate-workspace`, vault-health)
- Generators that must stay in order (`build-related` → `build-registry` → …)
- Hooks that can **stop** an action vs prose that only advises
- Proofboard / delivery-playbook gates; write-quality gates; context-profile fail-safe

**Authority + done**
- What may the agent do / never do / must ask? (profiles, Figma write gate, employer-repo rules)
- What counts as finished? (Proofboard, Live handoff, Open Engine receipts, CI)

**Receipts / run evidence**
- Session fragments, Live handoff, Open Engine ledger/receipts, audit-log
- Note whether this surface can produce a **run map** (what was available → eligible → shown → consulted → acted → checked → accepted). If not: `NOT_EXPOSED`.

### 3 — Diagnose: protect vs drag

Summarize in plain English:

- **Protects:** source-of-truth rules, authority boundaries, definition of done, hard checks, receipts
- **Drag:** duplicated ownership, early loading of specialist method, prose pretending to be enforcement, ownerless residue, corrections that outlived the failure that created them (**AI crud**)

People-facing crud test — anything that makes:

1. the right procedure harder to find,
2. the current rule harder to identify,
3. the output easier to reject, or
4. the setup harder to maintain.

### 4 — Disposition every material control

Each material control gets **exactly one** label:

| Disposition | When |
|---|---|
| **Keep** | Necessary context, truth, authority, acceptance, or a proven correction in the right place |
| **One home** | Multiple files own the same rule; pick a canonical owner; others pointer/invoke |
| **Load later** | Valuable specialist material arriving before the phase needs it |
| **Turn into check** | Yes/no guarantee a schema, hook, validator, permission, or test can enforce |
| **Probation** | Unclear help/hurt; leave active; schedule retest |
| **Retire** | Stale workaround, contradiction, ownerless residue, or fixed obsolete failure — archive path only after approval |

Invalid: "delete it because it's long." Length is not a disposition.

### 5 — Compact execution core (recommendation shape)

Any cleanup plan must preserve a small always-available core:

1. **Outcome** — what must be true when finished?
2. **Context** — facts/sources/state the model must not invent?
3. **Authority** — may / ask / never?
4. **Acceptance** — files, checks, evidence, finish line?

Specialist methods and long evaluation protocols go **behind triggers**. Binary format/limits move to validators where the surface supports them; otherwise label **advisory** until an external check exists. The model checking itself is not enforcement.

### 6 — Write the report (read-only deliverable)

Write (versioned; never overwrite):

```
05-artifacts/active/harness-map_vN.N_YYYY-MM-DD.md
```

If Sean wants it durable in-repo for workspace-brain, also copy or write:

```
07-projects/19-workspace-brain/reports/harness-map_vN.N_YYYY-MM-DD.md
```

**Stamp (required when a real map lands):** overwrite
`07-projects/19-workspace-brain/reports/harness-map.stamp` with:

```
date: YYYY-MM-DD
report: harness-map_vN.N_YYYY-MM-DD.md
surface: <surface edition>
```

Session-start Notices (Claude dispatcher + Cursor `brain.mdc`) warn when that `date:`
is **>30 days** old; **silent if the stamp is missing** (no nag before the first map).
Never invent a stamp for freshness — only write it when this protocol produced a report.

Required sections:

1. Boundary + surface edition + evidence-grade legend  
2. System map (always-on / routed / enforcement / authority / receipts)  
3. Protect vs drag (short)  
4. Numbered recommendations — each with disposition, owner path, rationale, risk, rollback  
5. Explicit gaps (`INACCESSIBLE` / `NOT_EXPOSED`)  
6. Suggested verification after any approved change (what to re-run; optional link to [[mission-fit]])

Do **not** apply patches in the same turn unless Sean approves specific recommendation numbers.

### 7 — Apply only with approval

On approval: smallest reviewable diffs; regenerate registry/related if skills change; run the write-quality validator chain before commit. Update `07-projects/19-workspace-brain/SESSION-STATE.md` Live handoff.

## Relationship to other skills

| Skill | Boundary |
|---|---|
| [[mission-fit]] | Jobs + recent runs vs this map; false-success checks |
| [[workspace-bootstrap]] | Session handshake / load protocol — does not audit harness shape |
| `/optimize` (`.claude/skills/optimize`) | Entropy punch list across the vault — use map dispositions when consolidating |
| [[open-agent-engine]] | Movement + receipts for tasks — not a harness inventory |
| [[intent-coordination]] | Living spec + `intent-run.py` waves — not a harness inventory |
| [[side-chat-handback]] | Parent continuity only |

## Ritual hooks (thin — skills stay on-demand)

Always-on rituals do **not** load this skill. They only:

- **Session-start Notice** — if `harness-map.stamp` exists and is >30 days old, suggest
  `/harness-map` (not a blocker; silent when no stamp).
- **Session-end `Evidence:` line** — one optional line on consequential `done` claims
  (see `/session-end`); full five-check audits remain [[mission-fit]] on demand.

### Control-layer appendix (when recommending autonomy widening)

Before proposing "let the agent run further," confirm the ship checklist beyond the model:
tools · data reach · permissions · quality bar · proof path · supervision · stop conditions
([[nate-jones-harness-enrichments]] §4). Missing any → disposition **Turn into check** or
**blocked**, not more prose.

## Provenance

- Nate B. Jones — *The AI Harness Audit* (2026-07-15) + Clean My AI Harness guide  
- Localized 2026-08-07 for `snds/workspace`: portable contract, registry `load_chains`, multi-surface adapters, archive-not-delete, Proofboard + Open Engine as existing enforcement/receipt layers
- Enrichments absorbed: [[nate-jones-harness-enrichments]]

## Related
- peer ↔ [[mission-fit]]
- peer ↔ [[workspace-bootstrap]]
- peer ↔ [[open-agent-engine]]
- peer ↔ [[side-chat-handback]]
- peer ↔ [[intent-coordination]]
