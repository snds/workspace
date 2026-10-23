---
type: decision
description: The design-skill rearchitecture's routing rules apply to every domain — every hub with spokes declares its `area`, every spoke carries triggers of its own (from its description's own asks), and no trigger is an everyday word. Measured by Synapse's routing suite (`sy routing test`); 129 hub-prose-only spokes became 0 on 2026-10-23.
created: 2026-10-23
confidence: high
relations:
  builds-on: ["[[decision-design-skill-architecture]]", "[[decision-skill-prefixes]]"]
  relates-to: ["[[skill-frontmatter]]", "[[skill-areas]]"]
---

## For future agent
- **TL;DR:** Sean, 2026-10-23: the design rearchitecture's changes "would be good to apply against all
  domains". When you add a spoke, give it its own triggers. Take them from the asks its description
  lists, never single everyday words. When you add a hub, give it an `area` no other hub claims.
  Check with `sy routing test <workspace>` (Synapse) or `workspace-harness.py`'s skill-reachability.
- **As of:** 2026-10 · **Status:** current

## The rules (every domain)

1. **Every spoke is reachable by its own words.** A spoke without triggers is reached only if an
   agent reads its hub and picks it. The router, the harness compiler and surfaces without the
   descriptions in context can't.
2. **Every hub with spokes declares its `area`, and one hub per area** (`build-area-index.py` fails
   otherwise).
3. **No trigger is an everyday word.** `battery`, `pasta`, `shot`, `framing` and `blocking` fired on
   ordinary sentences; a trigger names the domain's thing (`battery drain`, `pasta methodology`,
   `shot framing`).
4. **One prefix, one domain** ([[decision-skill-prefixes]]).

## Measured (2026-10-23)

Hub-prose-only spokes 129 → 0; areas 15 → 31 of 31 hubs with spokes; quoted description asks that
reach their skill 33% → 49%; everyday sentences that fire a skill 2 of 60 → 0 of 82; routing cases
143/143. Report:
[routing-architecture-all-domains](../../07-projects/19-workspace-brain/reports/routing-architecture-all-domains_v1.0_2026-10-23.md).

## Open (Sean's call)
Foundations first across chains (Synapse D133, 515 answers); trimming the 20 hubs over 1,500 words;
whether short quoted asks become triggers.
