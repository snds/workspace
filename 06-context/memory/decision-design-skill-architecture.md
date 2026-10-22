---
type: decision
description: Design, UX and design-system skills consolidated to one home per subspecialty — `ds` is the only design-system hub (ds-advisor, design-system-ops, the generation skills and the component-spec spoke under it), design-engineer is a lens, and the UX duplicates of IA, data visualization and accessibility were folded into their specialist hubs. Hubs declare `area:`; spokes carry their own triggers.
created: 2026-10-22
confidence: high
relations:
  builds-on: ["[[13-domain-rigor-stack]]", "[[skill-frontmatter]]"]
  relates-to: ["[[ds]]", "[[ds-component-spec]]", "[[design-engineer]]", "[[lead-ux-designer]]", "[[decision-skill-prefixes]]"]
---

## For future agent
- **TL;DR:** Sean, 2026-10-22: "merge both and rearchitect, ds as hub … Yes move ux-design-systems
  under the main design-systems hub." Every design subspecialty has exactly one home, reached by
  its own triggers. Find it in `02-shared-references/skill-areas.md` (generated). Don't add a second
  hub to an area — `build-area-index.py --check` fails on a contested area.
- **As of:** 2026-10 · **Status:** current

## What changed

| Before | After |
|---|---|
| Six design-system hubs (`ds`, `ds-advisor`, `design-system-ops`, `design-engineer`, `ds-generation-pipeline`, `gen-manifest`) | `ds` is the hub (`area: design-system`). `ds-advisor` (strategy, triage, DDRs), `design-system-ops` (command spoke), `ds-generation-pipeline` (now holding the generation manifest), `token-architecture`, `ai-design-systems`, `canonical-docs-voice`, `ds-source-watch` and the two employer UI spokes sit under it |
| `ux-design-systems` under `lead-ux-designer` | `ds-component-spec` under `ds` (alias kept); it supplies the component-spec harness's anatomy, variant-state and prop-API criteria |
| `design-engineer` a hub | A cross-cutting lens (design × code); its Figma triggers moved to `figma` |
| `ux-information-architecture`, `ux-data-visualization`, `ux-accessibility` | Folded into `ia-*`, `infod-*` and `a11y-*` (aliases on `ia-navigation-systems`, `infod-dashboard-patterns`, `a11y-motor-physical`); originals archived |
| `ds-advisor` 6,743 words, carrying general visual foundations | 4,158 words; the visual-foundations section moved word for word to `ds-advisor/references/visual-foundations.md` |
| `type` / `motion` vs. their lead hubs, unstated | `type` and `motion` are the implementation command hubs; `lead-type-designer` and `lead-motion-designer` own doctrine |

## Measured
- Routing battery of 19 subspecialty asks (`skill-routing-cases.jsonl`, ids `dsa-*`): 2 of 19 reached
  their owner before, 19 of 19 after.
- Words loaded for a token-architecture ask: about 7,250 before (design-foundations + ds-advisor),
  2,983 after (design-foundations + ds + token-architecture).

## Why
The overlap assessment
([report](../../07-projects/19-workspace-brain/reports/design-skill-architecture_v1.0_2026-10-22.md))
found subspecialties present but unreachable: spokes without triggers, broad hubs claiming the
words first, and no hub declaring the area, so the harness compiler had to guess.
