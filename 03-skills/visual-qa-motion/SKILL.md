---
name: visual-qa-motion
description: >-
  Visual QA judgment lens for UI motion — jank, timing, reduced-motion, purposeful vs
  decorative motion. Use with /qa --lens motion. Pairs with motion-performance measurement.
aliases: [visual-qa-motion]
triggers: [motion qa, animation audit, jank review, reduced motion qa]
tier: spoke
domain: quality
hub: lead-visual-qa
prerequisites: [lead-visual-qa]
related: [motion-performance, motion-accessibility, motion-principles, qa]
rigor_role: multi-voice
surfaces: ["*"]
spec_version: "2.2"
---

# Visual QA — Motion

Judgment lens. Frame-budget measurement → [[motion-performance]] / `/motion audit`.

## Checks

- Motion serves state change or spatial continuity — not decoration alone
- Easing/duration match magnitude of change
- `prefers-reduced-motion` alternative preserves information
- No layout thrash; compositor-friendly properties preferred
- Stagger/choreography readable; not chaotic

## Related
- hub → [[lead-visual-qa]]
- peer ↔ [[motion-performance]] · [[motion-accessibility]] · [[qa]]
