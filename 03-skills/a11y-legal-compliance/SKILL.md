---
name: a11y-legal-compliance
description: >
  WCAG 2.1/2.2/3.0, ADA, EN 301 549, EAA, Section 508, accessibility audit methodology,
  VPAT, ACR, and conformance reporting. Spoke skill in the lead-accessibility-architect
  network. Use this skill whenever the conversation touches: WCAG, WCAG 2.1, WCAG 2.2,
  WCAG 3.0, ADA, Americans with Disabilities Act, Section 508, EN 301 549, EAA,
  European Accessibility Act, EU Web Accessibility Directive, UK Equality Act, AODA,
  accessibility law, legal compliance, accessibility audit, VPAT, Voluntary Product
  Accessibility Template, ACR, Accessibility Conformance Report, conformance testing,
  accessibility statement, Level A, Level AA, Level AAA, POUR, perceivable, operable,
  understandable, robust, success criteria, axe-core, WAVE, Lighthouse, audit methodology,
  remediation priority, accessibility testing, screen reader testing, zoom testing,
  color blindness simulation, legal risk, Title II, Title III, Rehabilitation Act,
  Directive 2016/2102.
aliases: [a11y-legal-compliance]
tier: cross-cutting
domain: accessibility
hub: lead-accessibility-architect
spec_version: "2.0"
---

# a11y-legal-compliance

Specialist lens for accessibility legal requirements, standards, audit methodology,
and conformance reporting. Part of the `lead-accessibility-architect` skill network.

---

## Domain Boundary

This skill owns **legal and standards compliance** — WCAG, ADA, Section 508, EN 301 549,
EAA, audit methodology, and conformance reporting.

- **What the standards require at the design level** → other a11y spokes (this spoke
  contextualizes the legal requirement; the disability-specific spokes provide the
  design solution)
- **ARIA implementation** → `a11y-assistive-tech` + `fe-accessibility`

---

## WCAG Structure

WCAG (Web Content Accessibility Guidelines) is the universal reference standard for
digital accessibility. Published by W3C. Current ratified versions: 2.0 (2008),
2.1 (2018), 2.2 (2023). WCAG 3.0 is in development.

### POUR Principles

All WCAG success criteria fall under four principles:

**Perceivable** — users can perceive content (it's not invisible to all their senses):
- Text alternatives for non-text content
- Captions and transcripts for time-based media
- Content adaptable to different presentations without losing meaning
- Content distinguishable (sufficient contrast, not purely visual)

**Operable** — users can operate the interface:
- All functionality keyboard accessible
- Sufficient time to complete tasks
- No content that causes seizures or physical reactions
- Navigation aids (skip links, headings, page titles)
- Input modalities beyond keyboard (pointer, touch, voice)

**Understandable** — users can understand content and interface:
- Text is readable (language identified, unusual words explained)
- Content is predictable (consistent navigation, expected behavior)
- Users are helped to avoid and correct mistakes (error identification, suggestions)

**Robust** — content interpreted reliably by ATs:
- Compatible with current and future ATs
- Status messages communicated programmatically

### Conformance Levels

| Level | Meaning | Common Requirement |
|-------|---------|-------------------|
| A | Minimum — without this, some users are completely blocked | WCAG A is a hard floor |
| AA | Standard — the level required by most laws and enterprise contracts | Target for all production work |
| AAA | Enhanced — not required as full conformance (not all content can achieve it) | Apply where achievable and valuable |

Most legal requirements specify **WCAG 2.1 AA** or **WCAG 2.2 AA** as the standard.

---

## WCAG 2.1 (2018)

WCAG 2.1 added 17 new success criteria to WCAG 2.0, addressing mobile accessibility
and improvements for low vision and cognitive/learning disabilities.

### Key WCAG 2.1 Additions (AA level)

| SC | Name | Summary |
|----|------|---------|
| 1.3.4 | Orientation | Content not locked to portrait or landscape |
| 1.3.5 | Identify Input Purpose | Autocomplete attributes on personal data fields |
| 1.4.10 | Reflow | Content presentable at 320px width without horizontal scroll |
| 1.4.11 | Non-text Contrast | 3:1 for UI components and graphical objects |
| 1.4.12 | Text Spacing | No content loss when text spacing overridden |
| 1.4.13 | Content on Hover or Focus | Hoverable, dismissible, persistent hover content |
| 2.5.1 | Pointer Gestures | Multi-point gestures have single-pointer alternative |
| 2.5.2 | Pointer Cancellation | Prevent accidental activation on up-event |
| 2.5.3 | Label in Name | Accessible name includes visible text |
| 2.5.4 | Motion Actuation | Functionality with device motion has UI alternative |
| 4.1.3 | Status Messages | Status messages programmatically determinable |

1.4.10 (Reflow) and 1.4.11 (Non-text Contrast) are the most commonly failed WCAG 2.1 criteria.

---

## WCAG 2.2 (2023)

WCAG 2.2 added 9 new success criteria (and removed 1: 4.1.1 Parsing, now obsolete
given modern browser HTML error correction). Most new criteria are AA level.

### Key WCAG 2.2 Additions (AA level)

| SC | Name | Summary | Spoke for Design Depth |
|----|------|---------|----------------------|
| 2.4.11 | Focus Appearance (Minimum) | Focus indicator must meet perimeter and contrast requirements | `a11y-visual` |
| 2.4.12 | Focus Appearance (Enhanced) | Stricter focus appearance requirements | `a11y-visual` |
| 2.4.13 | Focus Appearance (renamed) | — | — |
| 2.5.7 | Dragging Movements | Dragging must have single-pointer alternative | `a11y-motor-physical` |
| 2.5.8 | Target Size (Minimum) | 24×24 CSS px minimum for activation area | `a11y-motor-physical` |
| 3.2.6 | Consistent Help | Help mechanisms in same relative position | `a11y-cognitive` |
| 3.3.7 | Redundant Entry | Don't require re-entry of previously provided info | `a11y-cognitive` |
| 3.3.8 | Accessible Authentication (Minimum) | No cognitive function test in auth unless alternative | `a11y-cognitive` |
| 3.3.9 | Accessible Authentication (Enhanced) | No cognitive function test in auth | `a11y-cognitive` |

**3.3.8 Accessible Authentication** is highly significant: CAPTCHAs that require
transcribing distorted text or solving puzzles are WCAG 2.2 AA failures unless an
alternative authentication method is available. Email magic links, passkeys, and
OAuth are compliant alternatives.

### Removed: 4.1.1 Parsing

WCAG 2.2 removed 4.1.1 Parsing from AA conformance (moved to obsolete). Modern
browsers auto-correct HTML errors in ways that make this criterion inconsistently
testable. Focus shifted to AT compatibility testing (4.1.2 and 4.1.3).

---

## WCAG 3.0 (In Development)

WCAG 3.0 is a major restructuring of the accessibility standard. Not yet ratified
or legally required, but directionally important:

- **New conformance model**: Bronze/Silver/Gold based on scope of coverage and testing,
  rather than the binary pass/fail of A/AA/AAA
- **APCA for contrast**: Accessible Perceptual Contrast Algorithm (more accurate than
  WCAG 2.x ratio formula) proposed as the contrast calculation method
- **Outcomes-based testing**: Success criteria tied to actual user outcomes rather
  than implementation requirements
- **Timeline**: Still in development as of 2025; expected to coexist with WCAG 2.x
  for many years

**Current recommendation**: Design to WCAG 2.2 AA; adopt APCA as supplementary
contrast verification; monitor WCAG 3.0 drafts for emerging best practices.

---

## Legal Frameworks

### United States

**ADA (Americans with Disabilities Act)**:
- Title II: State and local government entities — WCAG 2.1 AA required by rule (2024)
- Title III: Public accommodations and commercial facilities — extensive case law
  applies ADA to commercial websites; no rule-making has specified a technical standard
  but courts have repeatedly applied WCAG 2.1 AA as the de facto standard
- Key case precedent: Robles v. Domino's Pizza (9th Circuit, 2019) — ADA applies
  to websites and apps as places of public accommodation

**Section 508 (Rehabilitation Act)**:
- Applies to federal agencies and their contractors
- Requires WCAG 2.1 AA for web content and electronic documents (2018 refresh)
- Critical for any company selling software to the US federal government
- Requires a VPAT (see below) for procurement

**Risk landscape**: ADA Title III website litigation has grown significantly since 2018.
Companies with consumer-facing web properties are active targets. The presence of an
accessibility statement and evidence of active remediation effort mitigates risk.

### European Union

**EU Web Accessibility Directive (Directive 2016/2102)**:
- Applies to public sector bodies in EU member states
- Requires WCAG 2.1 AA (referenced through EN 301 549)
- Requires an Accessibility Statement

**European Accessibility Act (EAA) / Directive 2019/882**:
- Extends accessibility requirements to the **private sector** for key product/service categories
- Effective: June 28, 2025 for most products
- Covered: e-commerce, banking, e-books, transport services, audiovisual media services,
  electronic communications, operating systems, ATMs, ticketing machines
- Requirement: EN 301 549 compliance (which references WCAG 2.1 AA for web content)
- For companies selling into EU markets: this is not optional and the deadline has passed

**EN 301 549**:
- European harmonized standard for ICT accessibility
- Broader than WCAG — covers hardware, software, documents, and services
- Web content requirements reference WCAG 2.1; updated periodically
- The standard referenced by both the Web Accessibility Directive and the EAA

### United Kingdom

**UK Equality Act 2010**:
- "Service providers" (including website operators providing services) must not
  discriminate against disabled people
- No explicit technical standard, but WCAG 2.1 AA is the accepted benchmark
- UK Government uses WCAG 2.2 AA for public sector (updated 2024)
- Post-Brexit, EU EAA does not apply; UK is developing its own equivalent

### Canada

**AODA (Accessibility for Ontarians with Disabilities Act)**:
- Applies to organizations with 50+ employees in Ontario
- Web accessibility standard: WCAG 2.0 AA (still on 2.0; likely to update)
- Other provinces have varying requirements

---

## Accessibility Audit Methodology

An accessibility audit is a systematic evaluation of a product's compliance and usability
for people with disabilities. A rigorous audit has three phases:

### Phase 1: Automated Scanning

Tools: axe-core (via axe DevTools, Deque), WAVE (WebAIM), Lighthouse (Google), ARC Toolkit.

Automated scanning finds approximately 30–40% of WCAG issues. The issues it finds reliably:
- Missing `alt` attributes (not whether alt text is good)
- Color contrast failures for static text
- Missing form labels
- Empty or missing page title
- Duplicate IDs
- Missing language attribute
- Inaccessible form elements (missing `for`/`id` pairing)

The issues automated scanning cannot find:
- Alt text accuracy (present but wrong)
- Reading order logic
- Heading hierarchy correctness
- Whether keyboard navigation flows make sense
- Whether ARIA is used correctly in context
- Focus management adequacy
- Screen reader announcement quality

**Automated scanning is necessary but never sufficient.** Report automated scan
results with explicit caveat that they represent a fraction of issues.

### Phase 2: Manual Testing

**Keyboard-only testing**:
1. Disconnect or disable the mouse
2. Navigate the full product using only Tab, Shift-Tab, arrow keys, Enter, Space, Escape
3. Verify: all functionality accessible; tab order logical; no focus traps; focus
   visible at all times; modal focus management correct

**Screen reader testing** (minimum combinations):
- NVDA + Firefox (Windows) — free; widely used
- JAWS + Chrome (Windows) — enterprise standard; requires license (30-day trial available)
- VoiceOver + Safari (macOS) — required for Apple App Store accessibility
- VoiceOver + Safari (iOS) — required for mobile accessibility

For each screen reader test: navigate by headings, navigate by landmarks, navigate
by links list, fill and submit forms, interact with dynamic content (modals, live
regions, SPAs).

**Zoom testing**:
- 200% browser zoom: no content loss, no horizontal scrolling on normal content
- 400% browser zoom: reflow test (WCAG 1.4.10) — content in single column without
  horizontal scroll

**Color blindness simulation**:
- Chrome DevTools: Rendering → Emulate vision deficiencies
- Figma: Stark plugin
- Check: information not lost under deuteranopia, protanopia simulations

### Phase 3: User Testing

The only way to discover the ~60% of issues not caught by automated and manual testing.

- Minimum 3-5 participants per disability type
- Include users with different AT configurations (NVDA + Firefox is different from
  VoiceOver + Safari)
- Use task-based testing protocol, not think-aloud of the full interface
- Recruit from disability-specific communities; do not use internal staff as proxies

**Prioritization of findings**:

| Severity | Definition | Urgency |
|----------|-----------|---------|
| Critical | Blocks task completion entirely — user cannot proceed | Fix before ship |
| Major | Significantly impairs task completion — user can proceed but with significant difficulty or workaround | Fix in next sprint |
| Minor | Creates inconvenience or inefficiency but task is completable | Backlog with commitment |

---

## VPAT and Accessibility Conformance Reports

### VPAT (Voluntary Product Accessibility Template)

A VPAT is a document that describes how a product meets Section 508 and/or WCAG
requirements. It is used in US federal government procurement and increasingly
in enterprise B2B contracts.

VPAT versions:
- VPAT 2.5 (current): covers Section 508 Refresh (2018), WCAG 2.1, EN 301 549
- Available at itic.org/policy/accessibility/vpat

### ACR (Accessibility Conformance Report)

A completed VPAT is called an ACR. The ACR must be:
- Authored by someone with genuine accessibility expertise (not a marketing document)
- Based on actual testing, not aspirational claims
- Specific: each criterion marked as "Supports", "Partially Supports", "Does Not Support",
  or "Not Applicable" with a Remarks column explaining partial support and known issues
- Dated and versioned — ACRs go stale as products are updated

**Common VPAT failure**: Marking everything as "Supports" without testing. Enterprise
procurement teams are becoming more sophisticated; a VPAT that ignores known issues
creates legal exposure.

### Accessibility Statement

A public accessibility statement should include:
- The accessibility standard being targeted (WCAG 2.1/2.2 AA)
- Known limitations and a timeline for remediation
- A contact mechanism for users to report accessibility issues
- Date of last evaluation

---

## Quality Checklist for Compliance Readiness

### Pre-Audit

- [ ] Automated scan (axe-core or WAVE) run across all primary templates
- [ ] Keyboard-only navigation test completed for all primary flows
- [ ] Screen reader test with at least NVDA+Firefox and VoiceOver+Safari
- [ ] 200% and 400% zoom test completed
- [ ] Color blindness simulation run on all key views

### Audit Findings Management

- [ ] All findings classified Critical/Major/Minor
- [ ] Critical issues triaged before ship
- [ ] Remediation plan for Major issues within defined timeline
- [ ] Minor issues in accessibility backlog

### Documentation

- [ ] Accessibility statement published and accurate
- [ ] VPAT/ACR prepared if enterprise sales require it
- [ ] VPAT marked with actual test dates and real findings (not "Supports" for untested criteria)
- [ ] Accessibility testing included in definition of done for new components

---

## Cross-Links

| Skill | Relationship |
|-------|-------------|
| `ds-advisor` | Design system components must include accessibility requirements as first-class specification properties |
| `lead-ux-designer` | Accessibility requirements belong in acceptance criteria; audit findings route to UX as product debt |
| `a11y-assistive-tech` | AT testing protocol used in audit phase 2; axe-core as automated scanning engine |
| `a11y-visual` | WCAG 1.4.x design depth for visual criteria; this spoke owns the legal standard context |
| `a11y-motor-physical` | WCAG 2.1.x / 2.4.x / 2.5.x design depth; this spoke owns the legal standard context |
| `a11y-cognitive` | WCAG 3.2.6 / 3.3.7 / 3.3.8 / 3.3.9 COGA criteria; this spoke owns the legal standard context |
| `lead-accessibility-architect` | Hub — routes to this spoke for legal requirements, compliance audit, WCAG criteria, VPAT, and conformance reporting |

## Related
- hub → [[lead-accessibility-architect]]
