---
title: LCARS Generative Interface
type: project
status: Implementing
aliases: [20-lcars-generative-interface]
triggers: [lcars, generative lcars, okudagram, scene ir]
frameworks: [aesthetic-lens, ui-ux-operational, research-and-evidence, qa-operating-model]
created: 2026-08-07
---

# 20-lcars-generative-interface

LLM-forward adaptive console/shell that recomposes **TNG-era LCARS** surfaces from intent, role (combadge), and workflow context. Every pixel is drawn through a deterministic renderer gated by an immutable LCARS constitution. v1 is hybrid recipes + content IR; plumbing targets v2 dynamic Scene IR without escaping the rules.

- **Design spec:** [[07-projects/20-lcars-generative-interface/SPEC|SPEC]]
- **Operational state:** [[07-projects/20-lcars-generative-interface/SESSION-STATE|SESSION-STATE]]
- **Registry:** [[06-context/project-registry|project-registry]]
- **Code home:** not in this vault — platform `Projects` directory when implementation starts (per workspace ontology)
- **Cursor canvases (copies):** [[07-projects/20-lcars-generative-interface/canvases/README|canvases/]]

## For future agent

Read `SESSION-STATE.md` Live handoff first, then `SPEC.md`, then the v1 plan at `docs/superpowers/plans/2026-08-07-lcars-generative-interface-v1.md`. Do not invent chrome outside the constitution. App code lives in `~/Projects/lcars-generative-interface`, not this vault.
