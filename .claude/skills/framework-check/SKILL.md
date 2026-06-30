---
name: framework-check
description: Runs current work through the ten operating frameworks as a structured critique pass — the six core lenses always, plus the situational lenses (Integration, Workspace Contribution, Component & Pattern, Perception Integrity) when the work touches their domain. Invoked as /framework-check.
---

# /framework-check — Multi-framework critique

Takes the current work-in-progress (the thing Sean is asking about, or the most
recent artifact) and runs it through the operating frameworks. Each produces a short
critique — what the framework values, what it sees here, what it flags.

The **six core lenses (01–06)** always run. The **four situational lenses (07–10)**
run only when the work touches their domain — otherwise they're listed once under
"Not applicable" rather than padded with manufactured critique.

## Trigger phrases

`/framework-check`, "run through the frameworks", "framework critique",
"what do the frameworks say".

## Protocol

### Step 1 — Identify the target

If Sean has named a target (a file, a decision, a component), use that.
Otherwise: infer from the most recent artifact or the current conversation topic.
Confirm the target before critiquing.

### Step 2 — Load frameworks

`01-frameworks/00-README.md` carries compressed summaries of all ten — read it first if you
need the quick version, then load the full files for the lenses in scope.

**Core lenses — always read (or verify already loaded):**
- `01-frameworks/01-aesthetic-lens.md`
- `01-frameworks/02-ui-ux-operational-framework.md`
- `01-frameworks/03-collaboration-and-critique-framework.md`
- `01-frameworks/04-research-and-evidence-framework.md`
- `01-frameworks/05-last-mile-craft-framework.md`
- `01-frameworks/06-qa-operating-model.md`

**Situational lenses — read only if the target is in their domain:**
- `01-frameworks/07-integration-and-review-framework.md` — work headed for the repo (branching, PRs, merge order, consolidation).
- `01-frameworks/08-workspace-contribution-framework.md` — the target *is* a change to the workspace itself (a skill, framework, memory, reference, MOC).
- `01-frameworks/09-component-and-pattern-framework.md` — any component/pattern decision, component docs/schema, tokens, the AI-legible / `DESIGN.md` layer.
- `01-frameworks/10-perception-integrity.md` — any judgment of fine visual detail (a render, screenshot, artifact, reference, image asset).

(If a core file is missing, flag it and continue with the rest.)

### Step 3 — Critique structure

Output exactly this structure. One paragraph per framework, not more:

```markdown
## Framework critique: {target}

### Aesthetic Lens (philosophical ground)
- **Values:** {1 line}
- **Sees here:** {1–2 sentences}
- **Flags:** {concrete issues or omissions}

### UI/UX Operational
- **Values:** ...
- **Sees here:** ...
- **Flags:** ...

### Collaboration & Critique
- **Values:** ...
- **Sees here:** ...
- **Flags:** ...

### Research & Evidence
- **Values:** ...
- **Sees here:** ...
- **Flags:** ...

### Last-Mile Craft
- **Values:** ...
- **Sees here:** ...
- **Flags:** ...

### QA Operating Model
- **Values:** ...
- **Sees here:** ...
- **Flags:** ...

## Situational lenses

{Include a block here ONLY for each situational lens (07 Integration · 08 Workspace
Contribution · 09 Component & Pattern · 10 Perception Integrity) whose domain the target
touches — same Values / Sees here / Flags shape. List the rest on a single line:
"**Not applicable:** 07 Integration, 08 Workspace Contribution (target isn't repo-bound
or a workspace edit)." If none apply, replace this whole section with that one line.}

## Cross-framework tensions

{Only include this section if frameworks disagree on something important. Name the
disagreement explicitly — "Aesthetic Lens wants X but UI/UX Operational demands Y."
If no meaningful tensions, omit this section entirely.}

## Highest-leverage next action

{One specific thing Sean could do next, based on the combined critique.
Not a list — pick the single highest-leverage item and justify in one line.}
```

### Step 4 — No writing to disk

This skill produces output only. Don't write the critique anywhere — Sean will
decide whether to save, act, or discard.

## Notes

- **Keep it short.** Six core one-paragraph critiques + only the situational lenses
  that apply + one cross-tension paragraph + one next-action line. Don't run all ten
  by reflex — the situational gating is what keeps it on one screen.
- **Avoid hedging.** If a framework has nothing useful to say about the target,
  say "No specific flag — target is outside this framework's scope." Don't
  manufacture critique to fill space.
- **Cite framework sections** when the critique draws on a specific part.
  Example: "(04-research-and-evidence-framework.md §Median Persona)".
