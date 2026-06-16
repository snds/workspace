---
name: framework-check
description: Runs current work through the five operating frameworks (Aesthetic Lens, UI/UX Operational, Collaboration & Critique, Research & Evidence, Last-Mile Craft) as a structured critique pass. Invoked as /framework-check.
---

# /framework-check — Multi-framework critique

Takes the current work-in-progress (the thing Sean is asking about, or the most
recent artifact) and runs it through all five frameworks. Each produces a short
critique — what the framework values, what it sees here, what it flags.

## Trigger phrases

`/framework-check`, "run through the frameworks", "framework critique",
"what do the frameworks say".

## Protocol

### Step 1 — Identify the target

If Sean has named a target (a file, a decision, a component), use that.
Otherwise: infer from the most recent artifact or the current conversation topic.
Confirm the target before critiquing.

### Step 2 — Load frameworks

Read (or verify already loaded):
- `00-frameworks/01-aesthetic-lens.md`
- `00-frameworks/02-ui-ux-operational-framework.md`
- `00-frameworks/03-collaboration-and-critique-framework.md`
- `00-frameworks/04-research-and-evidence-framework.md`
- `00-frameworks/05-last-mile-craft-framework.md`

(If any is missing, flag it and continue with the rest.)

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

- **Keep it short.** Five one-paragraph critiques + one cross-tension paragraph +
  one next-action line. The whole thing should fit on a screen.
- **Avoid hedging.** If a framework has nothing useful to say about the target,
  say "No specific flag — target is outside this framework's scope." Don't
  manufacture critique to fill space.
- **Cite framework sections** when the critique draws on a specific part.
  Example: "(04-research-and-evidence-framework.md §Median Persona)".
