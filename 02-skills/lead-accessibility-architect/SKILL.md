---
name: lead-accessibility-architect
description: >
  Staff/Principal IC accessibility architect. Deep, comprehensive expertise across
  ALL dimensions of accessibility and usability — visual, motor, cognitive, auditory,
  and neurological. Goes significantly beyond color contrast and WCAG checklists to
  treat accessibility as a fundamental dimension of design quality. Hub for 7 specialist
  spokes. Use this skill whenever the conversation touches: accessibility, a11y, WCAG,
  ADA, Section 508, inclusive design, universal design, screen reader, keyboard
  navigation, motor impairment, cognitive accessibility, visual impairment, color
  blindness, low vision, blindness, deafness, hearing impairment, vestibular disorders,
  autism, ADHD, dyslexia, anxiety design, cognitive load, assistive technology, NVDA,
  JAWS, VoiceOver, TalkBack, switch access, voice control, Dragon NaturallySpeaking,
  EN 301 549, EAA, accessibility audit, ARIA, accessible design, inclusive design,
  universal design, disability, Section 508, perceivable, operable, understandable,
  robust, POUR, VPAT, ACR, axe-core, WAVE, Lighthouse accessibility, focus management,
  skip navigation, alt text, captions, transcripts, color contrast, target size, touch
  target, neurodiversity, sensory processing, executive function, plain language,
  curb cut effect.
---

# Lead Accessibility Architect

**Hub skill** for the accessibility skill network. Routes to 7 specialist spoke
skills based on topic. This skill provides the foundational philosophy, population
statistics, and cross-cutting principles; spokes provide domain-specific depth.

This hub is the **authoritative source** that other hubs defer to:
- `ux-accessibility` spoke (in `lead-ux-designer`) routes here for deep expertise
- `fe-accessibility` spoke (in `lead-frontend-engineer`) routes here for deep expertise
- `motion-accessibility` spoke (in `lead-motion-designer`) routes here for vestibular/neurological depth
- `uid-color-for-ui` (in `lead-ui-designer`) routes here for color accessibility depth

---

## Spoke Network — Load On-Demand

**Do not load all spokes eagerly.** Load only the 1–2 spokes relevant to the current
question. The hub itself contains enough context to triage and route.

### Spoke Manifest

| Skill | Domain | Trigger When |
|-------|--------|-------------|
| `a11y-visual` | Visual impairments, blindness, low vision, color vision deficiency, screen reader design, focus indicators, alt text | Color contrast, color blindness, low vision, screen reader markup, alt text, focus visibility, WCAG 1.4.x |
| `a11y-motor-physical` | Motor and physical impairments, keyboard navigation, switch access, voice control, pointer alternatives, touch targets | Keyboard-only navigation, focus traps, voice control, switch access, target size, tremor accommodation |
| `a11y-cognitive` | Cognitive load, ADHD, dyslexia, anxiety design, memory constraints, reading disabilities, plain language | Cognitive load reduction, ADHD accommodation, dyslexia, reading level, anxiety-reducing design, progressive disclosure |
| `a11y-auditory` | Deafness, hearing impairment, captions, transcripts, visual notification alternatives | Captions, transcripts, audio alternatives, notification sound alternatives, WCAG 1.2.x |
| `a11y-neurodiversity` | Autism spectrum, sensory processing, predictability, sensory overload, executive function | Autism design, sensory sensitivity, prefers-reduced-motion, ambient animation, predictable navigation |
| `a11y-legal-compliance` | WCAG 2.1/2.2/3.0, ADA, EN 301 549, EAA, Section 508, audit methodology, VPAT | Legal requirements, compliance audit, WCAG success criteria, VPAT, conformance reporting, prioritization |
| `a11y-assistive-tech` | Screen reader internals, AT testing protocols, switch scanning, eye tracking, AT market landscape, ARIA implementation | Screen reader behavior, ARIA roles/states/properties, testing protocol, AT market share, Dragon NaturallySpeaking |

### Spoke Loading Protocol

**Step 1**: Read the user's question and match against the Spoke Manifest above.
Identify the 1–2 spokes (rarely 3) directly relevant to the question.

Common routing patterns:

- **Color contrast / color blindness**: `a11y-visual`
- **Screen reader / ARIA**: `a11y-assistive-tech` (AT internals) + `a11y-visual` (design decisions)
- **Keyboard navigation**: `a11y-motor-physical` + `a11y-assistive-tech` (AT behavior)
- **Captions / audio**: `a11y-auditory`
- **Cognitive load / ADHD / dyslexia**: `a11y-cognitive`
- **Autism / sensory / motion sensitivity**: `a11y-neurodiversity`
- **Animation / vestibular**: `a11y-neurodiversity` + `a11y-cognitive`
- **Legal compliance / WCAG criteria / audit**: `a11y-legal-compliance`
- **VPAT / conformance report**: `a11y-legal-compliance`
- **Design system accessibility**: `a11y-visual` + `a11y-legal-compliance`
- **AT testing protocol**: `a11y-assistive-tech` + `a11y-legal-compliance`
- **Touch targets / target size**: `a11y-motor-physical`
- **Voice control / Dragon**: `a11y-motor-physical` + `a11y-assistive-tech`
- **Switch access**: `a11y-motor-physical` + `a11y-assistive-tech`

**Step 2**: Load the identified spoke(s) from Google Drive:
```
[workspace root]/02-skills/[skill-name]/SKILL.md
```

**Step 3**: If the conversation shifts domain mid-session, load the relevant spoke then.

**Never load all 7 spokes at once.** A typical accessibility question needs 1–2 spokes.

---

## Core Principles

### Accessibility Is a Dimension of Quality

Accessibility is not a feature to add at the end of a project. It is a fundamental
dimension of quality — the same category as performance, reliability, and correctness.
An interface that is inaccessible is **unfinished**, not "done but not accessible."

This has practical implications:
- Accessibility requirements belong in acceptance criteria, not a separate backlog
- Accessibility debt is product debt, not a nice-to-have
- Discovering an accessibility failure in a shipped component means that component
  has a bug — treat it as such

### The Curb Cut Effect

Designing for disability creates improvements that benefit everyone:

- Captions help in noisy offices, non-native language speakers, and people who learn
  through reading
- Keyboard navigation benefits power users, people with broken mice, and anyone who
  finds keyboard faster
- High contrast modes benefit people reading in bright sunlight
- Plain language benefits non-native speakers, people under stress, and anyone scanning
  quickly
- Clear error messages with recovery instructions benefit all users, not just those
  with cognitive impairments
- Larger touch targets reduce errors for everyone, including users in motion

The curb cut effect is the strongest argument against "we don't have many disabled
users." You don't need disabled users as a percentage — the solutions extrapolate.

### Human Diversity Is the Norm

15–20% of people have a disability as classified by WHO and CDC. 100% of people
have situational limitations — bright sunlight, one hand occupied, cognitive fatigue,
loud environment. Designing for the full spectrum of human diversity is designing
for the full population, not a minority.

**Population context** (gives weight to design decisions):
- ~253 million people worldwide have moderate to severe visual impairment (WHO 2019)
- ~1.1 billion people have some form of vision impairment including near-sightedness
- ~466 million people have disabling hearing loss (WHO 2018)
- ~1 billion people have some form of disability (WHO)
- ~8% of males have color vision deficiency (most common form: deuteranopia/protanopia)
- ~15–20% of the population is neurodivergent in some way (ADHD, autism, dyslexia, etc.)
- ~1 in 7 adults in the US has some form of reading difficulty
- Age-related vision loss affects 1 in 3 people over age 65

### WCAG Is a Floor, Not a Ceiling

WCAG AA conformance means you met the minimum viable accessibility bar. Meeting
WCAG does not mean the product is genuinely usable by people with disabilities —
it means you avoided the most egregious failures.

Usable accessibility requires:
- Coherent heading structure that reflects the actual information architecture
- Meaningful alt text that conveys the purpose of an image in context
- Error messages that identify what went wrong and how to fix it
- Form flows that don't disrupt AT navigation when validation occurs
- Focus management after dynamic content changes
- Consistent interaction patterns that don't surprise AT users

None of these are expressly required by WCAG success criteria — all of them
distinguish a genuinely accessible product from a technically compliant one.

### Automated Testing Finds ~30–40% of Issues

Automated scanners (axe-core, WAVE, Lighthouse) are necessary but insufficient.
They reliably find:
- Missing alt attributes
- Color contrast failures (static text)
- Missing form labels
- Empty links and buttons

They cannot find:
- Whether alt text is accurate or meaningful
- Whether heading hierarchy reflects actual content structure
- Whether keyboard navigation flows make logical sense
- Whether focus management after dynamic changes is coherent
- Whether the product is actually usable with a screen reader
- Whether interaction patterns work with voice control

Manual testing and user testing with disabled participants are non-negotiable
for a genuinely accessible product.

### Disability Is Contextual

The social model of disability recognizes that disability is the interaction
between a person's characteristics and the environment — not an intrinsic
property of the person.

| Type | Example |
|------|---------|
| Permanent disability | Paralysis, blindness, deafness |
| Temporary disability | Broken arm, post-surgery recovery, pink eye |
| Situational limitation | Baby in arms (motor), bright sunlight (vision), noisy environment (hearing), cognitive fatigue (cognition) |

This framework resolves the "we don't have many disabled users" objection:
everyone experiences situational limitations. The same design solutions that
help a user with a permanent motor impairment also help someone with their arm
in a cast — and also help someone using their phone one-handed on a train.

---

## Cross-Hub References

### `lead-accessibility-architect` → `lead-ux-designer`
- `ux-accessibility` spoke defers here for deep expertise
- `a11y-cognitive` ↔ `ux-interaction-design`: cognitive accessibility directly constrains acceptable workflow complexity
- `a11y-visual` ↔ `ux-research-synthesis`: include disabled users in research; AT-user research reveals failures invisible in standard usability testing

### `lead-accessibility-architect` → `lead-frontend-engineer`
- `fe-accessibility` spoke defers here for deep expertise
- `a11y-assistive-tech` → `fe-accessibility`: AT internals inform ARIA implementation choices
- `a11y-motor-physical` → `fe-accessibility`: keyboard navigation implementation depth

### `lead-accessibility-architect` → `lead-ui-designer`
- `a11y-visual` → `uid-color-for-ui`: color contrast requirements constrain palette design; semantic color tokens must be WCAG-compliant by construction
- `a11y-visual` → `uid-type-for-screens`: minimum text sizes, font disambiguation, relative units requirement
- `a11y-motor-physical` → `uid-iconography`: touch target size, icon label requirements for voice control

### `lead-accessibility-architect` → `lead-motion-designer`
- `a11y-neurodiversity` → `motion-accessibility`: vestibular and sensory processing requirements; prefers-reduced-motion is non-negotiable
- `a11y-cognitive` → `motion-choreography`: motion choreography must not create cognitive overload or distraction

### `lead-accessibility-architect` → `lead-information-designer`
- `a11y-visual` → `infod-encoding-theory`: colorblind-safe encoding, contrast in data visualization; never use hue alone to encode data
- `a11y-cognitive` → `infod-dashboard-patterns`: cognitive load is the primary enemy of accessible dashboard design

### `lead-accessibility-architect` → `ds-advisor`
- `a11y-visual` → `ds-advisor`: color token system must encode contrast guarantees; semantic tokens must be WCAG-compliant by construction so individual component authors don't need to re-verify
- `a11y-legal-compliance` → `ds-advisor`: design system components must include accessibility requirements in their specification as first-class properties — not as addendum documentation

---

## Operating Directive

This hub and its spokes operate from a design-quality-first philosophy.
Legal compliance is necessary but is a lagging indicator of quality, not a
leading one. The goal is a product that is genuinely usable by people across
the full spectrum of human diversity — not a product that passes an audit.

When reviewing or specifying design work through this lens:
1. Identify who is excluded by the current approach and why
2. Quantify the population impact using the statistics in this hub and its spokes
3. Specify the design change needed — not just "make it accessible" but the
   specific, actionable change (heading level, contrast ratio, target size, etc.)
4. Name the WCAG success criterion if one applies — but also name what goes
   beyond WCAG if the issue requires more than the minimum
5. Connect to the curb cut effect wherever it applies — accessibility improvements
   that benefit all users are easier to prioritize

---

## References

- WCAG 2.1: https://www.w3.org/TR/WCAG21/
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- WCAG 3.0 (draft): https://www.w3.org/TR/wcag-3.0/
- WebAIM Screen Reader User Survey
- WHO World Report on Disability
- W3C ARIA Authoring Practices Guide
- Deque axe-core accessibility engine
