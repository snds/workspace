---
tags: [accessibility, a11y, wcag, contrast, keyboard, cognitive, enterprise]
created: 2026-08-03
updated: 2026-08-03
status: working
confidence: medium
sources: [03-skills/lead-accessibility-architect/SKILL.md, 03-skills/a11y-visual/SKILL.md, 01-frameworks/10-perception-integrity.md, 08-knowledge/design/radix-derived-color-system.md, 08-knowledge/design/enterprise-saas-design-patterns.md]
related_skills: [lead-accessibility-architect, a11y-visual, a11y-cognitive, a11y-motor-physical, a11y-neurodiversity, ux-accessibility, fe-accessibility, uid-color-for-ui]
related_projects: []
relations:
  builds-on: ["[[radix-derived-color-system]]"]
  relates-to: ["[[a11y-measurement-vs-judgment]]", "[[enterprise-saas-design-patterns]]", "[[figma-ds-surface-authoring]]"]
---

# Accessibility baseline: WCAG is the floor, and the automated pass is a small part of it

## For future agent
- **TL;DR:** the workspace position on what an accessibility claim requires. WCAG conformance is a
  **compliance floor**, not a definition of usable. Automated tooling covers a minority of real
  barriers, so the manual baseline (keyboard path, screen reader, zoom and reflow, motion) is
  mandatory before saying "accessible."
- **Key claims:**
  - *Timeless:* an automated scan proves the absence of a specific class of defect, not the presence
    of accessibility. Passing axe with a keyboard trap on the primary flow is a failing screen.
  - *Timeless:* contrast policy belongs at the semantic and governance layer, not in the primitive
    ramp. Bending primitives to satisfy a contrast target destroys their reusability.
  - *Timeless:* judging focus rings, contrast, or small-text legibility from a downsampled
    screenshot is not evaluation. Capture at native resolution and state the pixels judged at.
  - *Pointer:* population statistics, the five dimensions, and spoke routing live in
    [[lead-accessibility-architect]].
- **As of:** 2026-08 · **Status:** current (seeded baseline; the color-layer claim rests on prior
  validated work, the rest is doctrine)

---

## Why this note exists

Accessibility was covered by a deep skill network with nothing in the vault, so each engagement
restarted from first principles and re-litigated the same three arguments (is WCAG enough, is the
scan enough, whose layer owns contrast). This note settles them on the workspace's terms.

[[a11y-measurement-vs-judgment]] is the companion routing note: which toolkit measures what, and why
an axe-clean result is not an accessibility verdict. This note is the substance behind that split.

---

## Five dimensions, not one

Accessibility work drifts toward the visual because it is the easiest to measure. The dimensions
that actually generate support tickets are spread across all five: **visual, motor, cognitive,
auditory, neurological**. Two consequences:

- A review that only checked contrast and alt text has checked one dimension of five and should say
  so rather than reporting a clean pass.
- Cognitive load, error recovery, and time pressure are accessibility concerns, not separate UX
  polish. A form that fails on a mistyped value and clears itself excludes people, and no contrast
  ratio will surface it.

## The manual baseline

Before any accessibility claim, do all four. None of them require tooling beyond a browser:

1. **Keyboard-only path** through the primary task. Focus visible at every stop, order matching
   visual order, no trap, and no control reachable only by pointer.
2. **Screen reader pass** on that same path. Names, roles, and state announced; dynamic changes
   announced once rather than never or continuously.
3. **Zoom and reflow** to 200% and a narrow viewport. Content reflows without horizontal scrolling
   and without truncating meaning.
4. **Motion and timing.** Reduced-motion respected; nothing essential conveyed only by animation;
   no unavoidable timeout on a task requiring reading.

An automated scan runs alongside this, not instead of it. Its value is regression detection on the
mechanical rules, which is real and worth wiring into CI.

## Contrast belongs to the semantic layer

This is the one claim here backed by validated prior work. From [[radix-derived-color-system]]: the
working architecture treats a perceptual contrast model (APCA) as **governance over semantic
tokens**, not as a reason to mutate the primitive ramp. Consequences that keep coming up:

- Fix a contrast failure by choosing a different step for the semantic role, not by darkening the
  primitive. Darkening the primitive fixes one pairing and silently shifts every other consumer.
- Text roles, solid-fill roles, and border roles have different targets and should not be checked
  against one universal number.
- Route foundations-first when this comes up: [[design-foundations]] then [[found-color]] then
  [[a11y-visual]] then [[uid-color-for-ui]], and only then the target system's own tokens.
- Native CSS `contrast-color()` is a pairing helper onto those semantic text tokens. It is not
  an accessibility claim and it does not replace APCA. See [[uid-color-for-ui]].

## Perception integrity applies here too

[[10-perception-integrity]] is usually invoked for rendering work, but its rule is load-bearing for
accessibility review: **do not judge fine visual detail from a downsampled image.** Focus-ring
thickness, 1px borders, disabled-state contrast, and small-text legibility all disappear or change
character under downsampling, which means a review done on a scaled screenshot can pass a screen
that fails on the device. Capture at native resolution and state the resolution judged at.

## Enterprise density is the hard case

The recurring context here is dense enterprise and PLM interfaces, where the hardest accessibility
surface is the data table (see [[enterprise-saas-design-patterns]] for the pattern catalog):

- Header association, cell semantics, and sort state have to be programmatically determinable, not
  just visually apparent.
- Grid keyboard navigation is a different model from tab order, and mixing the two produces a table
  that is technically operable and practically unusable.
- Row-level actions hidden until hover are pointer-only affordances unless they are also reachable
  and discoverable by keyboard.
- Status conveyed by a color-only cell fails both color-vision and screen-reader users, and it is
  the single most common defect in this pattern family.

## How to report a finding

Name the barrier and who it excludes, then the success criterion if one applies, then what goes
**beyond** the criterion when the minimum is not enough. Where an improvement helps everyone (the
curb-cut effect), say so, because that is what gets it prioritized. Deliver remediations rather than
observations: "add a visible focus style at 3:1 against the adjacent surface" rather than "focus is
unclear."
