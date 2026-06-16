---
name: visual-qa-ux-design
description: >
  UX design visual QA specialist. Use this skill for reviewing: user flows,
  navigation patterns, information architecture as expressed visually,
  wireframes, low-to-high fidelity prototypes, journey maps, screen sequences,
  interaction design patterns, onboarding flows, empty states, error states,
  loading states, modal and overlay patterns, progressive disclosure, content
  hierarchy at the experience level (not just screen level), wayfinding within
  products, multi-step task flows, cross-platform experience consistency.
  Also trigger when evaluating whether a visual design creates the right
  mental model, communicates the right affordances, or supports the user in
  understanding what to do next — the experience layer, not just the
  component layer. Spoke of lead-visual-qa.
aliases: [visual-qa-ux-design]
tier: cross-cutting
domain: quality
hub: lead-visual-qa
spec_version: "2.0"
---

# Visual QA — UX Design

UX design quality assurance specialist. Evaluates the experience layer of visual
design: flows, wayfinding, information architecture, mental model alignment, and
the visual language that guides users through a product. Spoke of `lead-visual-qa`.

---

## Domain Boundary

This skill owns the **experience design evaluation lens**.

- **Component aesthetics, spacing, design system compliance** → `visual-qa-ui-design`
- **Accessibility compliance** → `visual-qa-accessibility`
- **Whether users can efficiently complete tasks** → `visual-qa-usability`
- **Brand and graphic craft** → `visual-qa-graphic-design`

UX and UI QA overlap intentionally — a poorly designed experience often manifests
as a visual problem, and a visual problem often creates an experience failure.
Apply both lenses when the artifact is a screen-based product.

---

## Navigation and Information Architecture QA

### Visual Hierarchy as Navigation

Navigation is most often a visual QA failure before it's a content or IA failure.
Evaluate:

- **Is the primary navigation visually distinct from secondary and tertiary nav?**
  Users scan for navigation structure before reading labels. If primary and secondary
  nav use the same visual weight, users are forced to read everything to find their place.
- **Is the active/current location visually differentiated?**
  Active states should be immediately obvious — not a subtle color shift, but a clear
  visual distinction (weight, underline, fill, background)
- **Does the visual treatment of nav items communicate their behavior?**
  Expandable items should look expandable (chevron, caret). Tab navigation should
  look tab-like. Links should look like links.

### Wayfinding Evaluation

At any point in a flow, the user should be able to answer three questions visually:
1. **Where am I?** — Current location is clear
2. **Where can I go?** — Available paths are visible and differentiated
3. **Where did I come from?** — Back/breadcrumb path is clear

Flag when any of these questions cannot be answered by scanning the screen without
reading all text.

### Progressive Disclosure

- Does the design reveal information in the right sequence?
- Are advanced or rare options visually subordinated to primary actions?
- Is density appropriate — does the user see enough to understand the space without
  being overwhelmed by all possible options at once?
- Do expanding/collapsing sections correctly signal what's inside before expanding?

---

## Flow Evaluation

### State Coverage

A complete UX visual design covers all meaningful states. Flag missing states as
critical gaps. Required states for most interactive screens:

| State | Description |
|-------|-------------|
| **Default/Rest** | The "nothing has happened yet" state |
| **Loading** | Awaiting data or processing |
| **Populated** | With realistic content (not "Lorem ipsum" stand-ins) |
| **Empty** | No data — what does the user see and what do they do? |
| **Error** | System or user error — recovery path must be visible |
| **Partial** | Some data exists but the target state isn't reached (e.g., incomplete profile) |
| **Edge case** | Long names, unusual content, maximum item count |

### Transition Visibility

When evaluating a flow (sequence of screens or states):
- Are transitions between states designed, or assumed?
- Can the user see how they arrived at the current state?
- Is the relationship between screens visually legible (child screen vs. peer screen vs. overlay)?

### Action Hierarchy

Every screen should have a clear answer to: **what is the user expected to do?**

- **Primary action**: Visually dominant — should be one per screen or section
- **Secondary action**: Clearly subordinate to primary (lighter weight, outline, or ghost button)
- **Destructive action**: Visually separated from constructive actions; requires visual caution signaling
- **Escape/Cancel**: Always present on modal/overlay screens; visually clear

Flag when:
- Two actions appear to have equal visual weight (user must read to distinguish)
- The destructive action is visually equal to or more prominent than the constructive action
- A screen has no clear primary action (the "what do I do next?" problem)
- The primary action is below the fold without visual indication it exists

---

## Mental Model and Affordance QA

### Affordances

An affordance is a visual signal that tells the user what they can do with an element.

| Element Type | Expected Visual Affordance | Failure |
|--------------|--------------------------|---------|
| **Button** | Contained shape (filled or outlined), or clear text link treatment | Flat colored rectangle with no visual "button-ness"; or styled to look like a button but non-interactive |
| **Input field** | Box with border or underline, usually with label | No visual container; indistinguishable from static text |
| **Scrollable area** | Partial content visible at edge ("peek"), or scroll indicator | Content truncated with no hint that more exists below |
| **Draggable item** | Handle icon, cursor change on hover, spacing suggests movability | No visual drag affordance — user discovers by accident |
| **Expandable** | Chevron/caret, +/- indicator, or visually open area | Content appears complete with no indication it can expand |
| **Selectable** | Checkmark, radio dot, highlight, or border — clear selection state | Selected state visually identical to unselected |

### Mental Model Alignment

Does the design match the user's expectation of how this type of interface behaves?

- **Platform conventions**: iOS navigation patterns on an iOS app, Material Design patterns
  on Android — deliberate departures require strong justification
- **Domain conventions**: Enterprise software users expect density; consumer apps expect
  simplicity — the visual language should match domain expectations
- **Novelty tax**: Novel interaction patterns require visual teaching moments — if the
  design requires a tutorial, the affordance has failed

---

## Content Hierarchy QA

### Scanning Patterns

Users scan before they read. The design should support the natural scanning pattern
for its context:

- **F-pattern**: Common for text-heavy content — primary information in the first two
  horizontal bands and the left edge
- **Z-pattern**: Common for visual-heavy, lower-text content — eyes travel top-left →
  top-right → diagonal → bottom-left → bottom-right
- **Gutenberg**: Common for editorial — primary optical area (top-left), terminal area
  (bottom-right) are where attention concentrates

Evaluate whether the design's visual hierarchy guides the eye along the expected path,
or fights against it by placing secondary content in primary scan positions.

### Information Density

| Density Level | Use When | Failure Mode |
|---------------|----------|--------------|
| **High** | Expert users, data-heavy tools (dashboards, IDEs, spreadsheets) | Applied to consumer contexts — overwhelms; applied to sparse content — feels unfinished |
| **Medium** | General consumer products, mixed-use tools | No clear density intention — neither comfortably dense nor comfortably airy |
| **Low** | Onboarding, marketing, single-task flows | Applied to data-heavy contexts — wastes space; forces excessive scrolling |

---

## QA Checklist — UX Design

**Navigation and IA:**
- [ ] Primary navigation is visually distinct from secondary navigation
- [ ] Active/current location has an unmistakable visual state
- [ ] User can identify "where am I / where can I go / how did I get here" by scanning
- [ ] Progressive disclosure is appropriate — advanced options visually subordinated

**Flow and States:**
- [ ] All meaningful states are designed (default, loading, empty, error, populated)
- [ ] Transitions between states are designed or explicitly handled
- [ ] Flows include a clear primary action on each screen
- [ ] Destructive actions are visually distinguished from constructive actions

**Affordances and Mental Models:**
- [ ] Interactive elements look interactive; static elements do not look interactive
- [ ] Scroll affordances are visible for scrollable areas
- [ ] Expandable elements are signaled as expandable before interaction
- [ ] Platform conventions are respected or deliberately broken with visual guidance

**Content Hierarchy:**
- [ ] Visual hierarchy guides the eye along an appropriate scanning path
- [ ] Density is appropriate for the use case and audience
- [ ] Secondary content is visually subordinated to primary content
- [ ] No orphaned elements that lack visual relationship to the content structure
