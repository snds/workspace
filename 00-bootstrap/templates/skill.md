---
name: <% tp.file.title.toLowerCase().replace(/ /g, "-") %>
description: >
  One or two sentences. What this skill is and the triggers it should fire on —
  this prose is how an agent decides to load the skill. Keep the trigger language rich.
aliases: [<% tp.file.title.toLowerCase().replace(/ /g, "-") %>]
triggers: [keyword, another phrase, task shape]
tier: spoke          # foundation | hub | spoke | cross-cutting
domain: design       # design | engineering | product | data | game | ...
hub: <parent-hub>    # spokes only — creates the spoke→hub load edge
prerequisites: [<parent-hub>]   # hard "load before me" edges; 0–2; resolver walks transitively
related: []          # soft cross-refs; suggested, never auto-loaded
governed_by: []      # cross-cutting lenses applied after this skill (e.g. a11y-visual)
defers_to: []        # optional — doctrine winners on conflict (framework-13, qa, …)
rigor_role: load-chain  # optional — operating-model | command-hub | measurement | load-chain | multi-voice
surfaces: ["*"]
spec_version: "2.2"
---

# <% tp.file.title %>

> **Domain Rigor:** before shipping this skill, clear [[13-domain-rigor-stack]] acceptance
> checklist (L1–L5). Prefer connective tissue over volume. Hubs need `prerequisites`.
> Wrappers declare `defers_to` so plugins cannot override workspace doctrine.

## Purpose
What problem this solves. Why it exists separate from other skills. For a spoke, state the one
line: "Foundations: [[<foundation>]]. This spoke covers <medium>-specific application only."
Name which rigor layer this primarily realizes (L2 command, L3 measurement, L4 spoke, …).

## When to use
Specific triggers, keywords, or task shapes that warrant loading this skill.

## When NOT to use
Things this skill is near but shouldn't cover. Defer to [[other-skill]] for those.

## Behavior
Step-by-step what the skill does when loaded. For hubs: include **Execution protocol**,
**done-gates**, and **absolute bans** (L2). For measurement skills: name audit vs critique (L3).

## Outputs
What the agent produces when executing this skill. Name evidence artifacts (reports, contracts).

## Defers-to
<!-- Required for plugin wrappers / overlapping owners. Else delete this section. -->
- Workspace doctrine wins: [[13-domain-rigor-stack]] · [[framework or hub]]
- Plugin/base depth (if any): `<plugin skill path or name>` — technique only

## Related
<!-- Typed wikilinks (basenames, resolved via aliases). Reciprocity is mandatory + CI-checked.
     Vocab: foundation · hub · spoke · applies-in · governed-by · peer · encodes-into.
     Only `foundation →` carries load precedence; the rest are navigational. -->
- foundation → [[<foundation>]]
- hub → [[<parent-hub>]]
- peer ↔ [[<sibling-skill>]]
