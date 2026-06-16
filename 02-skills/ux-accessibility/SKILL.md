---
name: ux-accessibility
description: >
  Inclusive design and accessibility at the design layer — WCAG design requirements,
  cognitive load reduction, keyboard navigation design, focus management, color and
  contrast decisions, error state accessibility, and prefers-reduced-motion design.
  Use this skill when working on: WCAG success criteria that affect design decisions,
  designing focus states and keyboard navigation order, form accessibility (labels,
  instructions, error identification), designing for screen readers at the design spec
  layer, cognitive load reduction through consistent patterns and progressive disclosure,
  colorblind-safe color palettes, color contrast testing in component context, designing
  skip navigation, focus trap behavior for modals and dialogs, and any question about
  making a design inclusive. Also trigger on: "is this accessible", "what's the
  contrast requirement for X", "how do I design the focus state", "how do I handle
  keyboard navigation in this widget", "what's the accessible name for this", "does
  this error message meet WCAG", "what about reduced motion", or any question where
  inclusion and accessibility affect design decisions. WCAG implementation in code
  lives in `fe-accessibility` — this spoke owns the design decisions.
aliases: [ux-accessibility]
tier: spoke
domain: design
hub: lead-ux-designer
prerequisites: [lead-ux-designer]
spec_version: "2.0"
---

# UX — Accessibility

Spoke skill in the `lead-ux-designer` network. Owns accessibility at the design
decision layer: WCAG criteria that generate design requirements, inclusive design
principles, focus state design, cognitive load reduction, and color/contrast decisions.

Does not own: ARIA implementation in code (→ `fe-accessibility`), token system contrast
guarantees (→ `ds-advisor`), component ARIA roles as implementation detail (cross-reference
`fe-accessibility` for ARIA implementation once the design intent is specified here).

---

## Accessibility as a Design Quality Signal

Accessible design is not a compliance checklist — it is a measure of whether the design
communicates its intent to all users through all channels. When a design fails for
assistive technology users, it typically also fails for:
- Users with low contrast sensitivity (aging users in bright environments)
- Users with motor impairments who cannot use a mouse
- Users operating in noisy environments who can't hear audio cues
- Users under cognitive load who benefit from clear hierarchy and consistent patterns

The inference: accessible design is often better design for everyone. Accessibility
debt and UX debt are the same debt.

**Enterprise context**: In government procurement, healthcare, and regulated financial
sectors, WCAG 2.1 AA compliance is a contractual requirement. Section 508 (US federal),
EN 301 549 (EU), and equivalent regional regulations are hard requirements, not
recommendations. Design decisions that violate these standards are not design trade-offs
— they are product defects.

Treat accessibility as a first-class design requirement. Not a final-pass review.
Not a separate workstream. Embedded in every design decision from the start.

---

## WCAG Design-Layer Requirements

WCAG 2.2 has 78 success criteria. Not all of them are design decisions — many are
implementation decisions. These are the criteria that generate specific design requirements:

### Perceivable

**1.4.1 Use of Color (A)**
Color alone cannot convey information. Every information state communicated by color
must also be communicated by a second channel: shape, pattern, text label, icon, or
position.

Examples of failures:
- A required field marked only with a red border (no asterisk, no "required" label)
- An error state indicated only by a red icon with no text message
- A "positive/negative" data value encoded only by green/red color with no sign (+/−)

Examples of fixes:
- Required field: red border + asterisk + "Required" label on the field
- Error state: red border + error icon + error message text
- Positive/negative values: color + sign (+ or −) prefix

**1.4.3 Contrast Minimum (AA)**
- Normal text: 4.5:1 contrast ratio against background
- Large text (≥18pt/24px regular or ≥14pt/18.6px bold): 3:1 contrast ratio
- Decorative text (purely visual, no information content): no requirement

Test contrast on the actual background colors components will be rendered on —
not in isolation. A dark text token that passes on a white surface may fail on
a secondary surface color. Test every combination.

**1.4.11 Non-text Contrast (AA)**
Interactive element boundaries and meaningful graphics: 3:1 against adjacent colors.

Means: the border of an input field must have 3:1 contrast against the background
(not just the text inside it). An icon that conveys meaning must have 3:1 contrast.
A chart data line must have 3:1 contrast against its background.

**1.4.4 Resize Text (AA)**
Text must remain readable when resized to 200% without loss of content or functionality.
Design implication: don't use fixed pixel heights on text containers. Use auto-expanding
containers so that text reflow at 200% doesn't cause overflow.

**1.4.12 Text Spacing (AA)**
Content must remain readable when the user overrides: line height to 1.5×, letter
spacing to 0.12em, word spacing to 0.16em, paragraph spacing to 2em. Design implication:
test component layouts with these overrides applied. Fixed-height containers with single
lines of text will overflow when the user applies custom text spacing.

### Operable

**2.1.1 Keyboard (A)**
All functionality must be operable via keyboard. Design implication: for every
interactive element, the keyboard activation must be specified. This is a design
decision, not an implementation detail — what key activates a custom widget is part
of the interaction contract.

**2.4.3 Focus Order (A)**
Navigation via Tab must follow a logical, meaningful sequence. Design implication:
in complex layouts (multi-column forms, dashboard grids, modals), the tab order must
be explicitly specified in the design. DOM order may differ from visual order in
responsive layouts — the design spec must account for this.

In Figma: specify the tab order in the interaction annotation. Do not assume it
follows visual order, because visual order and DOM order are not always the same.

**2.4.6 Headings and Labels (AA)**
Headings describe topic or purpose. Form labels describe input purpose. Design
implication: every form field must have a visible label. "Placeholder text as label"
is an accessibility failure — placeholder text disappears when the user begins typing,
leaving the user unable to check what the field is for.

Every page section must have a descriptive heading. A dashboard with 6 sections
that have no headings (just visual separation) fails this criterion.

**2.4.7 Focus Visible (AA)**
Focus indicator must be visible. Design implication: the focus state is a design
component, not an implementation default. The browser default focus outline is often
inadequate (low contrast, visually inconsistent with the component style). Design
the focus state explicitly for every interactive component.

WCAG 2.2 adds **2.4.11 Focus Appearance (AA)**: the focus indicator must have
at minimum a 3:1 contrast ratio and 2px width. Design spec: 2px minimum, higher
contrast preferred (the default browser outline fails this in many browsers).

**2.4.4 Link Purpose (A)**
Link text must describe the destination when read in isolation or with context.
"Click here" and "Read more" fail — the destination is not conveyed.
Design implication: all link and button labels must be descriptive. In tables,
where "Edit" appears in every row, the accessible name must include the row context
("Edit [Product Name]" not just "Edit").

**2.5.3 Label in Name (A)**
The accessible name of a control must contain its visible label text. If a button
visually says "Save" but the ARIA label says "Submit form," screen readers and
voice control users are inconsistent. Design implication: visible labels and
ARIA labels must match or the accessible name must contain the visible label.

### Understandable

**3.3.1 Error Identification (A)**
If an error is detected, the error must be identified and the error must be described
in text. Design implication: error messages must be text, not just color or icon.
The error message must describe what's wrong, not just flag that something is wrong.

**3.3.2 Labels or Instructions (A)**
Labels or instructions are provided when content requires user input. Design implication:
complex inputs (date formats, password requirements, file upload constraints) need
instructions before the input — not only in the error state after a failed submit.
"Enter date as MM/DD/YYYY" must appear before the user types, not only after they type
it wrong.

---

## Cognitive Load and Inclusive Design

Cognitive load in enterprise products is often treated as inevitable ("it's complex
software"). Accessibility-oriented design challenges this assumption.

### Cognitive load types

**Intrinsic load**: the inherent complexity of the task. A PLM change order is genuinely
complex. Design cannot eliminate this — only manage it.

**Extraneous load**: complexity added by the interface. Inconsistent label placement,
unclear error messages, ambiguous icons, excessive visual noise. Design eliminates this.

**Germane load**: the cognitive work of learning new patterns. High in initial onboarding,
low for expert users. Design reduces this through consistent patterns — the user learns
a pattern once and applies it everywhere.

Accessible design minimizes extraneous load. This benefits all users, not just those
with cognitive disabilities.

### Recognition over recall

Show users their options — don't require them to remember them. Dropdown menus, visible
action buttons, autocomplete suggestions: all reduce cognitive load by showing available
options rather than requiring users to generate them from memory.

Enterprise applications are particularly guilty of expecting recall: "command palettes"
with no guidance, modal dialogs with buttons whose consequences aren't described, action
menus where every item uses jargon.

### Consistent patterns

Same action, same outcome, same location — every time. Every exception adds cognitive load.
A "Delete" button that appears on the left side of some dialogs and the right side of others
requires users to scan every dialog before acting. Consistency is not aesthetically boring —
it is cognitively efficient.

Design system consistency is an accessibility feature. When all dialogs have the same
button order (Cancel on left, primary action on right), users learn it once. When buttons
are inconsistent, users read every dialog.

### Error prevention over error recovery

Accessible design prevents errors before they occur:
- Good defaults that work correctly for the common case
- Confirmation for destructive actions (when undo isn't available)
- Undo for reversible actions (preferred over confirmation for frequently-used destructive actions)
- Input constraints that prevent invalid formats before submission

Error prevention is more accessible than error correction because it keeps the user in
flow. Recovery from errors requires re-reading, re-understanding the error, and re-executing
the action — three additional cognitive steps.

### Plain language

Enterprise interfaces are full of domain jargon and technical terminology that users from
adjacent roles don't understand. "Disposition" means something specific in PLM. "Effectivity"
means something specific in manufacturing. Labels that use domain jargon must be validated
with real users from the intended domain.

Plain language test: can a user in the target role read a form label and immediately
know what to enter without looking it up? If not, the label needs work.

---

## Keyboard Navigation Design

### Designing the tab order

Tab order must be explicitly designed in complex layouts. Rules:
- Follow reading order (left-to-right, top-to-bottom in LTR layouts)
- Group related form fields so they are tabbed through as a group
- Skip decorative elements (images, icons that have no interactive function)
- Never remove focus from a visible interactive element without providing keyboard access by other means

In multi-column dashboards: the tab order must explicitly navigate the grid in a logical
sequence. Columns that are visually parallel but semantically sequential (Step 1, Step 2,
Step 3) must be tabbed in sequence order, not in DOM order.

### Modal and dialog focus management

Modals require explicit focus management:
1. When the modal opens, focus moves to the modal (typically to the title or first
   interactive element, depending on content)
2. Tab is trapped within the modal — pressing Tab on the last interactive element wraps
   to the first; Shift+Tab on the first wraps to the last
3. When the modal closes (via button, Escape, or background click), focus returns to
   the element that triggered the modal

Design spec: annotate (1) where focus moves on open, (2) what the focus trap boundary
is, (3) where focus returns on close. This is a design decision that must be explicit —
it cannot be left to the engineer to infer.

### Skip navigation

Skip navigation links ("Skip to main content") must be present on every page. They
are typically visible only on focus — they appear when a keyboard user Tabs to the
page, allowing them to skip the repeated header/navigation.

Design spec: the skip link must be visible on focus (not permanently hidden), must
be positioned first in the tab order (before the navigation), and must move focus
directly to the main content landmark.

### Complex widget keyboard patterns

Complex interactive components — menus, trees, data grids, comboboxes, date pickers,
tabs — have specified keyboard interaction patterns in the ARIA Authoring Practices
Guide (ARIA APG). These are not suggestions — they are the patterns screen reader
users and keyboard users have learned to expect.

Key patterns to know:

| Widget | Arrow key behavior | Activation |
|--------|-------------------|-----------|
| **Menu / dropdown** | Up/Down moves through items | Enter activates; Escape closes |
| **Tablist** | Left/Right (or Up/Down) moves between tabs | Enter or Space activates |
| **Tree** | Up/Down moves through items; Left collapses, Right expands | Enter activates |
| **Data grid** | Arrow keys move between cells | Enter activates cell; Escape exits cell editing |
| **Combobox** | Up/Down moves through suggestions | Enter selects; Escape closes |
| **Date picker** | Arrow keys navigate the calendar | Enter selects date |

Design spec: annotate the keyboard interaction model for every custom widget.
Cross-reference ARIA APG for the correct pattern. Don't invent custom keyboard
interactions — keyboard users have learned the standard patterns.

---

## Color and Contrast in Design Systems

### Build contrast into the token system

Semantic color tokens should encode contrast guarantees. A `--color-text-primary` token
that is defined as "must meet 4.5:1 on the default surface" is a contract between the
token and its use contexts. Tokens that don't carry this contract depend on each designer
to manually verify contrast on every use — which fails at scale.

Route to `ds-advisor` for the token system architecture layer. The design decision here
is: for each semantic color token, what is the contrast guarantee, and on which backgrounds
does it apply?

### Test in context

Contrast ratios must be tested on the actual background color where the element appears —
not on white. A dark text token that passes 4.5:1 on white may fail on the secondary
surface color (#F0F0F0) or on a status badge background. Every color combination in
the product must be tested, not just the primary text/background pair.

Figma plugins for contrast testing: Contrast (Figma Community), Stark, Able.

### APCA (Accessible Perceptual Contrast Algorithm)

APCA is more perceptually accurate than the WCAG contrast ratio formula, particularly
for body text and large displays. APCA Lc 60 is approximately equivalent to WCAG 4.5:1
but with better correlation to actual perceptual experience at different sizes.

Use APCA alongside WCAG for body text decisions. WCAG remains the legal compliance
standard in most jurisdictions — meet it. Use APCA to calibrate decisions where the
WCAG formula produces counterintuitive results (e.g., very light text on very light
backgrounds that pass WCAG but look unreadable).

### Colorblind simulation testing

Simulate deuteranopia, protanopia, and tritanopia for every color-encoded information
state. Test in Figma with Stark or Color Blind plugin.

Required simulation points:
- Data visualization color palettes (categorical, sequential, diverging)
- Status indicators (error/warning/success/info)
- Highlighted/selected/active states in tables and lists
- Form validation states

If the information cannot be read in a colorblind simulation, the design relies on
color as the sole differentiator — a WCAG 1.4.1 violation.

---

## Designing for Motion Sensitivity

### prefers-reduced-motion

Any animation that conveys information or state change must work without motion. The
design must include an explicit no-motion state for:
- Loading spinners → static skeleton screen
- Transitions between views → instant cut (or cross-fade at reduced opacity if timing is critical)
- Progress animations → static progress bar showing current percentage
- Data loading animations (shimmer) → static grey block

CSS `prefers-reduced-motion: reduce` is respected by many animation libraries but
not all custom animations. The design spec must note which animations require
reduced-motion alternatives — this cannot be left to the engineer to infer.

### Flagging motion risk

Large-area motion (parallax, auto-playing backgrounds, full-screen transitions) and
animations with high frequency (data updating at <100ms intervals) are vestibular
disorder risks. Flag these explicitly in design specs:
- "This component uses large-area animation — a prefers-reduced-motion alternative
  is required"
- "This animation auto-plays — must respect prefers-reduced-motion"

---

## Cross-Links

- `fe-accessibility` — ARIA implementation; keyboard event handling; screen reader testing
- `ds-advisor` — token system contrast guarantees; semantic color token architecture
- `ux-design-systems` — component state coverage that includes accessible states (focus, error)
- `ux-research-synthesis` — accessibility research methods; usability testing with AT users
- `ux-interaction-design` — error message writing; form design with accessible labels and instructions

---

## References

- WCAG 2.2: https://www.w3.org/TR/WCAG22/
- ARIA Authoring Practices Guide: https://www.w3.org/WAI/ARIA/apg/
- APCA contrast algorithm: https://www.myndex.com/APCA/
- Figma plugin — Stark (contrast + colorblind simulation): https://www.figma.com/community/plugin/732603254453395948
- Inclusive Components (Heydon Pickering): https://inclusive-components.design/
- A11y Project: https://www.a11yproject.com/
- WebAIM — Screen reader testing: https://webaim.org/
