---
type: decision
description: A skill-name prefix means one domain. `ds-` always means design system; data science uses `dsci-` (ten spokes renamed 2026-10-22). Any future collision on a short prefix is resolved the same way — the established meaning keeps the short prefix, the other domain takes a longer, unambiguous one.
created: 2026-10-22
confidence: high
relations:
  relates-to: ["[[ds]]", "[[lead-data-scientist]]", "[[skill-frontmatter]]", "[[decision-design-skill-architecture]]"]
---

## For future agent
- **TL;DR:** Sean, 2026-10-22: "use dsci- for data science to remove the "ds-" collision. ds- should
  ALWAYS refer to design systems. If other "DS" domains materialize, refer to "dsci-" as guidance for
  how to setup skill prefixes." Before naming a new spoke, check the prefix isn't already another
  domain's. `ds-*` is design system; `dsci-*` is data science.
- **As of:** 2026-10 · **Status:** current

## The rule

1. **One prefix, one domain.** A spoke's prefix names its domain (`ia-`, `infod-`, `a11y-`, `uid-`,
   `ds-`, `dsci-`, `fe-`, `be-` …). Two domains never share one.
2. **The established meaning keeps the short prefix.** The newer or less central domain takes a
   longer prefix that can't be misread: data science became `dsci-` because `ds` is the
   design-system hub's own name and Sean's practice is design systems.
3. **Template for the next collision:** short form + the first letters of the second word
   (`dsci-` = data science). E.g. a future "PM" collision (product management vs. project
   management) would keep `pm-` for the established one and give the other `pjm-`.
4. **Renames are reviewed and complete.** Move the directory, set `name:`, repoint every path and
   wikilink outside `_archive/` and history, regenerate, and pass the validators. Do not keep the
   colliding old name as an alias — that would keep the collision alive in search and links.

## What changed (2026-10-22)

`ds-ml-engineering`, `ds-experimentation`, `ds-product-analytics`, `ds-nlp-llm`, `ds-forecasting`,
`ds-data-engineering`, `ds-executive-storytelling`, `ds-prompt-engineering`, `ds-bi-platforms` and
`ds-data-governance` became `dsci-*` (hub `lead-data-scientist` unchanged). The prose abbreviation
"DS" for data science in those skills became "DSci". History and archived files keep the old names
as written.

## Why
The compiler's first component-spec plan proposed `ds-anatomy`, `ds-variants` and
`ds-component-api`, which would have deepened the collision; the overlap assessment
([report](../../07-projects/19-workspace-brain/reports/design-skill-architecture_v1.0_2026-10-22.md))
found `ds-` split between two domains. Sean chose a rename over a new design-system prefix.
