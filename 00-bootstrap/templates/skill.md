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
surfaces: ["*"]
spec_version: "2.0"
---

# <% tp.file.title %>

## Purpose
What problem this solves. Why it exists separate from other skills. For a spoke, state the one
line: "Foundations: [[<foundation>]]. This spoke covers <medium>-specific application only."

## When to use
Specific triggers, keywords, or task shapes that warrant loading this skill.

## When NOT to use
Things this skill is near but shouldn't cover. Defer to [[other-skill]] for those.

## Behavior
Step-by-step what the skill does when loaded.

## Outputs
What the agent produces when executing this skill.

## Related
<!-- Typed wikilinks (basenames, resolved via aliases). Reciprocity is mandatory + CI-checked.
     Vocab: foundation · hub · spoke · applies-in · governed-by · peer · encodes-into.
     Only `foundation →` carries load precedence; the rest are navigational. -->
- foundation → [[<foundation>]]
- hub → [[<parent-hub>]]
- peer ↔ [[<sibling-skill>]]
