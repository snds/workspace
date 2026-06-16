---
name: visual-qa-accessibility
description: >
  Accessibility visual QA specialist. Use this skill for reviewing: color
  contrast ratios (WCAG AA and AAA compliance), text legibility for low-vision
  users, color-only information encoding failures, focus indicator visibility,
  touch and click target sizing, keyboard navigation visual affordances,
  motion and animation accessibility (vestibular disorders, reduced-motion),
  cognitive accessibility (reading complexity, visual noise, predictability),
  text spacing and zoom compliance, color blindness simulation, high-contrast
  mode compatibility, icon and symbol legibility without color, form error
  communication without color alone, screen reader visual structure alignment,
  accessible typography (size, weight, spacing for low-vision), and WCAG 2.1/2.2
  success criterion evaluation at the visual level. Spoke of lead-visual-qa.
aliases: [visual-qa-accessibility]
tier: cross-cutting
domain: quality
hub: lead-visual-qa
spec_version: "2.0"
---

# Visual QA — Accessibility

Accessibility quality assurance specialist. Evaluates visual designs through the
lens of inclusion: whether the design is perceivable, operable, understandable,
and robust for users across the full range of visual, motor, and cognitive
abilities. Spoke of `lead-visual-qa`.

---

## Domain Boundary

This skill owns the **accessibility evaluation lens**.

- **Component aesthetics, spacing, interaction states** → `visual-qa-ui-design`
- **User flows, wayfinding, information architecture** → `visual-qa-ux-design`
- **Whether users can complete tasks efficiently** → `visual-qa-usability`
- **Brand craft, typography quality** → `visual-qa-graphic-design`

Accessibility and usability frequently co-occur. A color contrast failure is an
accessibility defect; a confusing form flow is a usability defect. When an
artifact fails both, file findings in both domains.

### Measurement companion: `visual-qa-toolkit`

This spoke defines the accessibility evaluation lens. For dimensions that can
be measured rather than asserted, invoke `visual-qa-toolkit`:

| This skill evaluates | Toolkit script |
|---|---|
| WCAG 2.x contrast ratios (text and non-text) | `qa_contrast` — computes ratios against configured AA/AAA thresholds |
| Color-only information encoding | `qa_color_vision` — simulates deuteranopia / protanopia / tritanopia, flags color pairs that collapse under CVD |

For WCAG compliance especially, measurement is evidence. A claim that "the
contrast looks low" is weaker than "the toolkit measured 3.06:1 against an AA
body-text threshold of 4.5:1." Invoke the toolkit for pre-handoff accessibility
audits, regression checks, or any time the claim of failure would otherwise be
contested.

The toolkit accepts paths (screenshot, optional explicit text-region bboxes,
config). It has no built-in knowledge of specific projects. See
`visual-qa-toolkit/SKILL.md` for invocation details.

---

## WCAG Contrast QA

### Text Contrast — WCAG 2.1 / 2.2 Success Criteria

| Text Size | AA Minimum | AAA Target |
|-----------|-----------|-----------|
| Normal text (< 18pt / < 14pt bold) | 4.5:1 | 7:1 |
| Large text (≥ 18pt / ≥ 14pt bold) | 3:1 | 4.5:1 |
| Disabled text | No requirement | — |
| Logo / decorative | No requirement | — |

**Critical failure**: Any text-on-background combination below 4.5:1 (normal) or
3:1 (large) is a Level AA failure. Flag with severity **Critical**.

**Common traps:**
- Placeholder text in inputs is often too light (styled as "hint" but still conveys information)
- Disabled states that aren't truly decorative — if the user needs to read the
  label to understand why a field is disabled, it must still meet contrast
- Text overlaid on images or gradients: evaluate the worst-case region of the
  overlay, not the average
- Semi-transparent text: evaluate the blended result on each background it appears over

### Non-Text Contrast (WCAG 1.4.11)

Visual cues that convey meaning — not just text — must meet **3:1** against
adjacent colors:

- **Form field borders**: The border (or underline) that defines the input region vs.
  the background it sits on
- **Focus indicators**: The focus ring against both the element background and the
  page background
- **Icon-only buttons**: The icon itself (not a label) against its background
- **Active/selected states**: The indicator that communicates "this is selected"
- **Charts and data visualizations**: Lines, bars, or segments that encode information

### Focus Indicator (WCAG 2.4.7 / 2.4.11)

WCAG 2.2 Success Criterion 2.4.11 (Focus Appearance, AA) sets a minimum:
- The focus indicator must have area ≥ the perimeter of the component × 2 CSS px
- Contrast between focused and unfocused state ≥ 3:1
- Contrast of the indicator itself against the adjacent background ≥ 3:1

Evaluate:
- Is the focus indicator ever invisible (outline:none with no replacement)?
- Is the focus indicator suppressed on mouse interaction but visible on keyboard
  (partial fix — acceptable if consistent)?
- Is the indicator area large enough to be conspicuous to a user scanning the page?
- Does the indicator conflict with the component's active or selected state?

---

## Color-Only Information (WCAG 1.4.1)

Information must never be conveyed by color alone. Evaluate every instance where
color carries meaning:

| Scenario | Failure Pattern | Required Redundancy |
|----------|----------------|---------------------|
| Status indicator (error/success) | Red vs. green dot only | Icon or label must accompany color |
| Required field marking | Red asterisk only | "Required" text or pattern fill |
| Chart legend | Color swatch only | Pattern, texture, or direct labels |
| Link in body text | Only color differentiates link from non-link text | Underline, weight, or other decoration |
| Selected tab/nav item | Color highlight only | Weight, underline, or shape change |
| Disabled form field | Gray color only | Opacity + cursor change + label |

**Simulate color blindness** (Deuteranopia/Protanopia are most common) mentally
or with tools — if the color distinction collapses, the design fails.

---

## Touch and Click Target Sizing

### Minimum Target Sizes

| Platform | Minimum Target Size | WCAG 2.5.5 (AA) |
|----------|--------------------|----|
| iOS (Apple HIG) | 44×44 pt | 24×24 CSS px (WCAG 2.2) |
| Android (Material) | 48×48 dp | 24×24 CSS px (WCAG 2.2) |
| Web (touch-primary) | 44×44 px recommended | 24×24 CSS px minimum |
| Web (pointer-primary) | 24×24 px minimum | — |

**WCAG 2.5.5 (AAA)**: 44×44 CSS pixels minimum for all interactive targets.
**WCAG 2.5.8 (AA, WCAG 2.2)**: 24×24 CSS pixels, with spacing exceptions.

Evaluate:
- Icon-only buttons in toolbars — visual icon may be 16×16 but hit target must be ≥ 24×24
- Checkboxes and radio buttons — the entire label, not just the control, should be tappable
- Link text in dense paragraphs — short link phrases may not meet 24px height
- Close/dismiss buttons on modals — often undersized at 16×16 icon with no padding
- Action items in lists or tables — row tap target vs. explicit button tap target

### Spacing Between Targets

Adjacent targets that are too close cause tap errors. When two targets are smaller
than the minimum, the spacing between them must compensate (WCAG 2.5.8 exception:
if the total target + spacing = 24px in each direction, the criterion is met).

---

## Typography Accessibility

### Minimum Readable Sizes

| Context | Minimum (Low-Vision Baseline) | Notes |
|---------|------------------------------|-------|
| Body text (web) | 16px | Below 16px: iOS auto-zooms on focus; visually stressful for many users |
| Body text (mobile) | 16px | Matches OS accessibility defaults |
| Support / caption text | 12px hard minimum | 11px or below is a critical failure for legibility |
| Button labels | 14px | 13px acceptable only with medium/semibold weight |

### Text Spacing (WCAG 1.4.12)

Design must not break when users override spacing settings:
- Line height to ≥ 1.5× font size
- Letter spacing to ≥ 0.12× font size
- Word spacing to ≥ 0.16× font size
- Spacing following paragraphs to ≥ 2× font size

Evaluate whether the design has fixed-height containers, clipping overflow, or
absolute-positioned labels that would break under these overrides. Flag any
container that clips text when spacing increases.

### Reflow (WCAG 1.4.10)

At 320px viewport width (400% zoom on 1280px desktop), all content should be
accessible without horizontal scrolling. Evaluate:

- Fixed-width components that don't reflow
- Horizontal scrolling tables (acceptable only when the data requires 2D navigation)
- Sticky sidebars or navigation that consume horizontal space at narrow widths
- Typography that doesn't wrap (overflow:nowrap on long labels)

---

## Motion and Animation Accessibility

### Vestibular Disorder Considerations (WCAG 2.3.3)

Users with vestibular disorders can experience nausea, dizziness, or disorientation
from large-scale motion. Evaluate:

| Motion Type | Risk Level | Requirement |
|-------------|-----------|-------------|
| Parallax scrolling | High | Must respect `prefers-reduced-motion` |
| Full-screen transitions (slide/zoom) | High | Must offer alternative or reduce at OS request |
| Auto-playing background animations | High | Must be stoppable; respect reduced-motion |
| Subtle state transitions (< 200ms, small distance) | Low | Acceptable without override |
| Infinite loaders / spinners | Low | Usually acceptable |

**Flag**: Any animation that moves a large region of the screen (> ~25% viewport
area) at meaningful speed and does not respect `prefers-reduced-motion: reduce`.

### Flashing Content (WCAG 2.3.1)

Flashing more than **3 times per second** in an area > ~341×256px is a Level A
failure that can trigger seizures. Flag any strobing, flashing, or rapid color
alternation patterns — even in decorative elements.

---

## Cognitive Accessibility

### Reading Complexity (WCAG 3.1.5)

- Body text should target Grade 8–9 reading level for general audiences
- Jargon, acronyms, and technical terms require definitions or tooltips
- Instruction text should follow plain language principles

### Predictability and Consistency (WCAG 3.2)

- Consistent navigation: components that appear on multiple screens should appear
  in the same position and order
- No unexpected context change on focus (keyboard navigation must not trigger navigation)
- No unexpected context change on input without warning

### Error Prevention and Recovery

Visual design must communicate errors clearly without relying on color alone:
- Error state must include an icon, label change, or border change in addition to red color
- Error messages must be proximate to the field that caused them
- Recovery path must be visible in the design — not just "something went wrong"
- Inline validation must not be destructive before the user has finished entering

---

## QA Checklist — Accessibility

**Contrast:**
- [ ] All normal text ≥ 4.5:1 contrast ratio against background
- [ ] All large text ≥ 3:1 contrast ratio against background
- [ ] All non-text UI components ≥ 3:1 (borders, icons, focus indicators)
- [ ] Text-over-image pairs evaluated at the worst-case region

**Color Independence:**
- [ ] No information conveyed by color alone (icons, labels, patterns supplement)
- [ ] Links in body text have non-color differentiation (underline or weight)
- [ ] Status indicators (error/success/warning) have redundant non-color signaling
- [ ] Design survives Deuteranopia and Protanopia simulation

**Focus and Keyboard:**
- [ ] Focus indicator is visible on all interactive elements
- [ ] Focus indicator meets WCAG 2.4.11 area and contrast requirements
- [ ] Focus order follows the visual reading order

**Target Sizing:**
- [ ] All interactive targets ≥ 24×24 CSS px (WCAG 2.2 AA minimum)
- [ ] Mobile targets ≥ 44×44 px (HIG/Material and WCAG 2.5.5 AAA)
- [ ] Adjacent targets have sufficient spacing to prevent mis-taps

**Typography:**
- [ ] Body text ≥ 16px
- [ ] No text below 12px for any communicative purpose
- [ ] Layout does not break under WCAG 1.4.12 text spacing overrides
- [ ] Design reflows at 320px viewport without horizontal scroll

**Motion:**
- [ ] Large-scale animations respect prefers-reduced-motion
- [ ] No content flashes more than 3 times per second

**Cognitive:**
- [ ] Error states include non-color signal and proximate recovery path
- [ ] Navigation and component placement is consistent across screens
- [ ] No unexpected context change on focus or simple input
