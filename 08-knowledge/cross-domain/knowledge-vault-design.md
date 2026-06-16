---
tags: [workspace, knowledge-vault, surfacing, dispatcher, architecture]
created: 2026-04-29
updated: 2026-04-29
status: stable
confidence: high
sources: [session-log 2026-04-29]
related_skills: [workspace-bootstrap]
related_projects: [00-obsidian]
---

# Knowledge Vault — Design Rationale

Why the vault is structured the way it is, and why three surfacing tiers are needed rather than one. This captures the design decisions that shaped `08-knowledge/` — the kind of "why" that isn't obvious from reading the files themselves.

---

## Why a Separate Vault Layer (Not Just Better Skills)

The workspace already has two content layers before the knowledge vault:
- **02-skills/** — operational how-to. "When you encounter X, do Y."
- **06-context/** — session and project state. "Here's what's active and pending."

Neither layer is the right home for accumulated domain insight. Skills are generic by design — they don't capture what we've specifically learned from Sean's actual work. Context files are ephemeral — they hold current state, not durable lessons.

The gap: **what was actually learned** from working on Centric's data tables, building CentricSymbols, debugging the Drive desync bug, designing Legion's space stations. These are insights that should inform future sessions but don't fit in a skill (too specific to Sean's context) or a session log (too ephemeral, gets buried).

`08-knowledge/` fills that gap. It's a PKM layer — personal knowledge management — sitting between skills (generic depth) and context (ephemeral state).

---

## Why Three Surfacing Tiers

A write-only vault is a graveyard. The challenge is getting entries *read* at the right moment. Three tiers are needed because they cover different failure modes:

### Tier 1: SessionStart — Index in context
**Problem solved:** "I don't know what knowledge exists."
**Mechanism:** `_INDEX.md` is injected into every session's initial context via `build_session_start_context()`. Claude sees all entry summaries before the first prompt.
**Why not just load entries directly:** Full entries loaded at boot would overwhelm context. The index (one line per entry) is lightweight — ~60 lines — and gives sufficient awareness to know *when* to load a specific entry.

### Tier 2: UserPromptSubmit — Trigger-word hints
**Problem solved:** "I know the knowledge exists but didn't remember to check before answering."
**Mechanism:** `KNOWLEDGE_HINTS` dict in `dispatcher.py` mirrors `TRIGGER_WORDS`. When a prompt contains domain keywords ("legion", "centric", "icon font"), the hook injects a per-entry reminder *before Claude responds*.
**Why it fires before Claude responds:** The `UserPromptSubmit` hook runs between the user's message and Claude's response. This is the only hook with the right timing to intercept and add context before work begins.
**Why mirrors TRIGGER_WORDS:** The same keywords that load skills are the same keywords that indicate domain work is beginning. Reusing the trigger list means no separate maintenance burden.

### Tier 3: CLAUDE.md rule — Explicit instruction
**Problem solved:** "The trigger word wasn't in the prompt but the work is clearly in a domain with a knowledge entry."
**Mechanism:** CLAUDE.md contains an explicit instruction: before substantive domain work, check the index and read the relevant entry.
**Why this is needed:** Trigger words are keyword matches — they fail when the user asks about something in an indirect way ("can you help me with the PLM work" vs. "centric"). The CLAUDE.md rule is a judgment-level instruction that covers the gap.

---

## Why Knowledge Entries Are Not Skills

The temptation when a domain insight is accumulated is to put it in the skill file for that domain. This is wrong for two reasons:

1. **Skills are generic; knowledge is specific.** `ds-advisor` covers design systems in general. The Centric PLM DS entry covers what's specifically true about *Centric's* situation — 90 tables, Vue-primary stack, Ark UI recommendation, specific Figma file keys. Mixing these would make skills context-specific and therefore wrong for any other user.

2. **Skills have different maintenance expectations.** Skills get updated when domain knowledge advances. Knowledge entries get updated when *our work* produces new evidence. The update triggers are different.

The one exception: if a pattern from a knowledge entry is validated enough to be generic advice, it should graduate into the relevant skill and the knowledge entry should reference it.

---

## Extending the System

**Adding a new knowledge entry:**
1. Create the file in the right `08-knowledge/{domain}/` subdirectory
2. Add its line to `08-knowledge/_INDEX.md`
3. Add its keyword(s) to `KNOWLEDGE_HINTS` in `dispatcher.py`
4. If there's also a skill to load, add to `TRIGGER_WORDS` too

**Adding a new domain subdirectory:**
1. Create the directory with a `_README.md` stub (just frontmatter + one-liner)
2. Add a section header to `_INDEX.md`
3. Add the directory to the `_README.md` structure list

**When an entry becomes stale:**
- Update the `updated:` date in frontmatter
- Change `status:` to `superseded` if replaced by a newer entry; link to the replacement
- Do NOT delete — stale entries are still historical context
