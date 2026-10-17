---
type: decision
description: Contrast is judged by APCA first, everywhere; WCAG 2.x is the fallback floor and the standard conformance claims cite. Automated checks gate on APCA Bronze (apca-check on the reference apca-w3) and report WCAG alongside.
created: 2026-10-17
confidence: high
relations:
  builds-on: ["[[radix-derived-color-system]]"]
  relates-to: ["[[a11y-visual]]", "[[a11y-audit-toolkit]]", "[[a11y-legal-compliance]]", "[[uid-color-for-ui]]", "[[accessibility-beyond-wcag-baseline]]"]
---

## For future agent
- **TL;DR:** **APCA is primary; WCAG 2.x is the fallback** (Sean, 2026-10-17), in every
  context. Design and judge text contrast by APCA Lc. Use WCAG only where an APCA target
  can't be met, and as the floor that conformance reports and laws cite.
- **Floors and targets:** floor = [[a11y-visual]] (Lc 60 body, 45 large or bold, 30 UI);
  APCA Bronze for small text (Lc 75 under 16px); working target = the design-engineer
  threshold table (Lc 75 body, 90 small); Radix-derived palettes hold the stricter
  [[radix-derived-color-system]] bar.
- **Automated checks:** axe-core has no APCA rule (its `color-contrast` is WCAG's ratio).
  `apca-check` (Stack Exchange, MIT) adds APCA Bronze and Silver+ rules to axe, built on the
  reference `apca-w3`. Gate on Bronze; report WCAG `color-contrast` as the fallback and
  Silver+ as the target. Neither covers non-text contrast; that stays with the visual review.
- **By element kind (Emphasis Engine's method, adopted in Unicron 2026-10-17, snds/unicron#27):**
  measure every pair a component paints, through its own opacity and mixes, and hold it to its
  kind's floor: reading text Lc 75 (APCA Bronze, under 16px), labels on fills and tints Lc 60,
  solids Lc 30, control borders and focus 3:1 as drawn (no calibrated APCA target for 1px lines).
  A role points at the weakest ramp step that clears every recipe it paints.
- **As of:** 2026-10 · **Status:** current

## Context — what forced a choice
The workspace said it two ways. [[radix-derived-color-system]] and framework #06 already put APCA
first, while [[a11y-visual]], [[a11y-legal-compliance]] and [[ux-accessibility]] said "meet WCAG,
verify with APCA". The first APCA run on the desktop app (snds/synapse, Stage 2 S10) showed why it
matters: WCAG passed every element, while 365 fell under APCA's minimum. Most were dark-mode muted
text that WCAG rates 7.7:1 but reads at Lc 49-52 at 11-14px.

## Decision — what we chose
- APCA first in design, review and automated gates. WCAG 2.x second, as the fallback.
- **Legal conformance is unchanged:** VPATs, ACRs and the laws behind them (ADA, Section 508, the
  EAA via EN 301 549) cite WCAG 2.x. Where a deliverable needs a conformance claim, WCAG 2.x AA must
  still pass, and the claim cites it. APCA being primary never lowers that floor.
- **Licenses:** the reference `apca-w3` is under a "Limited W3 License": it's for checking web
  content against accessibility guidelines; its constants must not change; commercial
  integrations must allow an audit; other uses fall under the AGPL. `colorparsley`, its
  dependency, is AGPL v3. Use both as dev-time checks. Shipping APCA inside a product needs a
  closer reading first. Don't port the code into this public repository without that reading.

## Consequences
- The vault's pixel contrast tool (`visual-qa-toolkit/scripts/qa_contrast.py`) measures WCAG only;
  adding APCA is on the backlog ([[project-context]], Pending Items), under the license note above.
- Fix a contrast failure at the semantic role (a different ramp step), never by mutating the
  primitive ([[accessibility-beyond-wcag-baseline]]).
