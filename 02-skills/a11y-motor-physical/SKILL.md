---
name: a11y-motor-physical
description: >
  Motor and physical impairments — keyboard navigation, switch access, voice control,
  pointer alternatives, touch targets, and tremor accommodation. Spoke skill in the
  lead-accessibility-architect network. Use this skill whenever the conversation
  touches: keyboard navigation, keyboard-only access, focus traps, tab order, focus
  management, skip links, motor impairment, paralysis, tremor, Parkinson's, limited
  dexterity, amputation, repetitive strain, one-handed use, switch access, switch
  scanning, voice control, Dragon NaturallySpeaking, Voice Control macOS, Voice Control
  iOS, accessible name, label in name, target size, touch target, minimum click area,
  pointer precision, drag and drop alternatives, single pointer, WCAG 2.1.1, WCAG
  2.1.2, WCAG 2.4.3, WCAG 2.5.3, WCAG 2.5.7, WCAG 2.5.8, keyboard shortcut, sticky
  keys, dwell activation, eye tracking pointer.
aliases: [a11y-motor-physical]
tier: cross-cutting
domain: accessibility
hub: lead-accessibility-architect
spec_version: "2.0"
---

# a11y-motor-physical

Specialist lens for motor and physical impairments: keyboard navigation, switch
access, voice control, and pointer alternatives. Part of the `lead-accessibility-architect`
skill network.

---

## Domain Boundary

This skill owns **motor/physical disability design** — keyboard navigation, voice control,
switch access, target sizing, and pointer accommodation.

- **AT internals (how screen readers, switch software, Dragon work)** → `a11y-assistive-tech`
- **ARIA implementation for keyboard patterns** → `a11y-assistive-tech` + `fe-accessibility`
- **Legal requirements for keyboard access** → `a11y-legal-compliance`

---

## Motor Impairment Spectrum

Motor impairments vary enormously in their interaction implications:

| Type | Examples | Interaction Impact |
|------|---------|-------------------|
| Paralysis | Quadriplegia, hemiplegia | May use only switch, eye tracking, or sip-and-puff |
| Tremor | Parkinson's disease, essential tremor | Imprecise pointer control, accidental activations |
| Limited dexterity | Cerebral palsy, muscular dystrophy | Reduced fine motor control, keyboard preferred |
| Amputation | Limb difference, finger amputation | One-handed keyboard, custom grip devices |
| Repetitive strain | RSI, carpal tunnel, tennis elbow | Painful mouse use; keyboard-first preference |
| Temporary impairment | Broken arm, post-surgical | Same as permanent — design solutions transfer |
| Situational | Baby in arms, crowded transit, device in one hand | Same interaction needs as temporary impairment |

**The design implications of tremor are distinct from paralysis**. A user with tremor
may use a mouse but cannot hit small targets reliably. A user with quadriplegia may
use a switch but not a mouse at all. Both need accessible keyboard patterns, but for
different reasons.

---

## Keyboard Navigation

**WCAG 2.1.1 Keyboard**: All functionality available with a mouse must also be
available with keyboard alone — not just "can it be navigated to" but "can all
actions be completed."

### What This Actually Means

Every action that is possible with a mouse is possible with keyboard:
- Click a button → Enter or Space on a `<button>`
- Open a dropdown → Enter or Space, arrow keys to navigate, Enter/Space to select, Escape to dismiss
- Drag to reorder → Keyboard-based alternative (arrow key to move, cut/paste, or explicit move controls)
- Hover to reveal → Equivalent revealed on focus (tooltips, overflow menus)
- Right-click context menu → Keyboard shortcut or Menu key equivalent

**The test**: Hide the mouse. Can you complete every primary task using only Tab,
Shift-Tab, arrow keys, Enter, Space, and Escape? If not, there's a keyboard
accessibility failure.

### Tab Order

**WCAG 2.4.3 Focus Order**: The tab order must preserve meaning and operability.
This means:

- Tab order follows the logical reading/task order
- Never use `tabindex` values greater than 0 to reorder focus — they create a maintenance
  nightmare and break the predictable tab sequence
- `tabindex="0"` adds an element to the natural DOM order (use for custom interactive elements)
- `tabindex="-1"` removes from tab order but allows programmatic focus (use for focus
  management in dynamic content)
- Fix reading order issues in the DOM, not with `tabindex` values

**Common failures**:
- Modal dialogs that don't trap focus — keyboard users can Tab out of the dialog into
  the dimmed background content
- Sticky headers or floating action buttons that appear in the wrong tab order position
  relative to visual layout
- CSS grid/flexbox reordering (`order: -1`) that places visual content before the DOM
  content, causing a mismatch between visual and keyboard tab order

### Focus Traps (the Good Kind)

**WCAG 2.1.2 No Keyboard Trap**: Users must always be able to navigate away from
any component using standard keys. This is about preventing *unwanted* focus traps.

However, focus traps are **correct and required** in certain contexts:
- Modal dialogs: focus must be trapped within the dialog while it is open
- Drawers/side panels opened as modal overlays: same rule
- Date picker popups with complex keyboard interaction

The correct pattern for modal focus traps:
1. When the modal opens, move focus to the first focusable element within it
2. Tab/Shift-Tab cycle only within the modal's focusable elements
3. Escape closes the modal and returns focus to the triggering element
4. Background content has `aria-hidden="true"` and `inert` when modal is open

### Keyboard Shortcuts

**WCAG 2.1.4 Character Key Shortcuts**: Single-key and combination shortcuts that use
only printable characters (letters, numbers, punctuation) must provide a mechanism to:
- Turn them off entirely, or
- Remap them to a combination including a modifier key (Ctrl, Alt, Shift), or
- Be active only when the relevant component has focus

**Why this matters**: Screen reader users and voice control users frequently press
single keys to navigate. A web app with `j`/`k` shortcuts for next/previous will
conflict with NVDA's or JAWS's navigation keys. Dragon users speaking individual
letters to dictate will accidentally trigger single-character shortcuts.

---

## Switch Access

Switch access is used by people with severe motor impairments who cannot reliably
operate a keyboard or mouse. Users activate a switch (or switches) to navigate
and select content.

### Switch Scanning Models

| Model | Mechanism | User Population |
|-------|----------|----------------|
| Single-switch scanning | The page automatically cycles through interactive elements; user activates switch to select the highlighted item | Quadriplegia, significant limited dexterity |
| Two-switch scanning | One switch advances to the next item; one switch activates selection | Same, slightly faster |
| Step scanning | Each switch press moves forward one step | Similar to two-switch |

### Design Implications for Switch Users

Every additional interactive element increases the number of steps to reach the
target. This creates a direct tradeoff: a "rich" UI with many interactive elements
is a slow, fatiguing nightmare for switch users.

**Design principles for switch access**:

1. **Minimize interactive elements per view** — every "helpful" shortcut link, icon
   button, and contextual action adds scanning steps. Ruthlessly audit for redundant
   interactive elements.

2. **Group scanning requires landmarks** — switch scanning software (iOS Switch
   Control, Android Switch Access) supports group scanning: first navigate to a
   region (landmark), then scan within it. Landmark regions (`<nav>`, `<main>`,
   `<aside>`) enable this two-phase navigation and dramatically reduce scan steps.

3. **Logical order matters more** — for switch users, the logical scan order is
   the only order. Visual shortcuts (jump to key content) are irrelevant if they
   don't exist in the DOM.

4. **Every interactive element must be reachable** — no interactive element should
   be excluded from the scan sequence. Custom JS components that don't receive focus
   are invisible to switch users.

5. **Long forms are severe burdens** — a 20-field form requires potentially 20+ scan
   cycles just to navigate through fields. Break long forms into steps; support
   save-and-return; autofill wherever possible.

---

## Voice Control

Dragon NaturallySpeaking (Windows), Voice Control (macOS/iOS), and Switch Access
(voice mode, Android) allow users to operate their computer entirely by voice.

### Say What You See

The most important voice control principle: users speak the visible label to activate
an element. "Click Sign In" — Dragon moves the cursor to the element labeled "Sign In"
and clicks it.

**WCAG 2.5.3 Label in Name**: For interactive elements with visible text labels, the
accessible name must contain the visible text. The visible text does not need to be
the entire accessible name, but the accessible name must *include* the visible text.

**Failure**:
```html
<button aria-label="Proceed to checkout">Buy now</button>
```
The user says "click Buy now" — Dragon reads the accessible name "Proceed to checkout"
and cannot match. This is a WCAG 2.5.3 failure.

**Fix**:
```html
<button aria-label="Buy now — proceed to checkout">Buy now</button>
```
Or more simply, just use the visible text as the accessible name directly.

### Icon Buttons Without Labels

Icon-only buttons are a voice control failure when they have no visible text label.
The Dragon "Show Numbers" or "Show Labels" grid mode assigns numbers to interactive
elements — but this requires users to know which number corresponds to the button
they want. It is slow and cognitively demanding.

**Design recommendation**: Provide visible text labels for all interactive elements
where feasible. When icon-only is required (constrained space), ensure:
- The accessible name (`aria-label`) precisely describes the action
- There is sufficient click target size for voice-controlled click-by-coordinate

### Voice Control Failure Patterns

- Buttons with icons and no text label (even if `aria-label` is present — the visible
  label is what voice users speak)
- Form fields with placeholder text but no `<label>` — Dragon uses placeholder as the
  speakable label, but placeholder disappears on focus
- Identical labels for different buttons ("Delete" appearing 15 times in a list) —
  Dragon can't differentiate; use "Delete [item name]" as the accessible name
- Links/buttons whose text changes dynamically (e.g., "3 items selected" → "5 items
  selected") — if the user memorized the label, it may no longer match

---

## Target Size

### WCAG 2.5.8 Target Size (Minimum) — New in WCAG 2.2 (AA)

The click/tap target must be at least 24×24 CSS pixels, **or** the spacing around
smaller targets must create a 24×24 minimum activation area.

**Why 24px is still a floor, not a goal**:
- Apple Human Interface Guidelines: 44×44pt minimum touch target
- Material Design: 48×48dp minimum touch target
- WCAG 2.5.5 Target Size (Enhanced, AAA): 44×44 CSS px minimum

24px is the legal minimum under WCAG 2.2 AA. 44px is the practical design recommendation
for touch interfaces and should be the default for any interactive control that is not
constrained by exceptional circumstances.

### Target Spacing

For targets smaller than 24×24px, WCAG 2.5.8 allows the undersize if the *offset
to adjacent targets* plus the target area creates the required 24px activation space.
In practice, ensuring ≥8px spacing between all interactive elements significantly
reduces mis-click rates for users with tremor or reduced dexterity.

### Tremor Accommodation

Motor tremor (Parkinson's, essential tremor) introduces involuntary pointer movement.
Design implications:

1. **Minimum target size**: 44×44px is strongly recommended for all interactive controls
   when tremor may be present; more is better for touch

2. **Adequate inter-target spacing**: Reduce the chance that an overshoot activates
   an adjacent element — at minimum 8px, preferably 12–16px between separate targets

3. **Forgiving activation**: Drag-and-drop requires precise start/end points —
   provide keyboard alternatives for any drag interaction (WCAG 2.5.7)

4. **Undo patterns**: Accidental activations happen. Confirmation for destructive
   actions and undo capability reduce the consequence of tremor-induced errors

5. **Pointer accuracy**: High-density icon toolbars and tightly packed data table
   action columns are particularly hostile to users with tremor

### WCAG 2.5.7 Dragging Movements — New in WCAG 2.2 (AA)

All functionality that uses dragging motion must also be achievable with a single
pointer (no dragging). Provide:
- A click-to-place alternative for drag-to-reorder
- A manual entry alternative for drag sliders
- A selection alternative for drag-select

---

## Pointer Operation

**WCAG 2.5.1 Pointer Gestures**: Functionality that uses multi-point gestures (pinch,
two-finger swipe) or path-based gestures (swipe direction matters) must be operable
with a single pointer through an alternative.

**Why this matters**: Users with limited dexterity, users holding a device with one
hand, and users with hook or mouth pointer devices cannot execute multi-finger gestures.

Exceptions: gestures essential to the function (e.g., a drawing app where path matters).
For navigation: swipe-to-go-back, pinch-to-zoom in a non-essential context must have
explicit alternatives.

**WCAG 2.5.2 Pointer Cancellation**: For single-pointer actions (click, tap), at
least one of the following must be true:
- No `mousedown`/`touchstart` event fires the action (uses `mouseup`/`click`)
- Abort or undo is available
- Up-event reverses the down-event action

This prevents accidental activation — users who press down and realize they're
on the wrong target can drag off before releasing.

---

## Focus Management in Dynamic Interfaces

Motor-impaired keyboard users are particularly affected when dynamic content changes
break the focus context:

### When to Move Focus Programmatically

| Event | Correct Focus Destination |
|-------|--------------------------|
| Dialog/modal opens | First focusable element in the dialog (or the dialog container with `tabindex="-1"`) |
| Dialog/modal closes | The element that triggered the dialog |
| In-page navigation (SPA route change) | Page heading `<h1>` or main content area with `tabindex="-1"` |
| Inline error appears | The first error message, or the first field with an error |
| Expandable section opens | The section's heading or first interactive element |
| Toast/notification appears | Focus should NOT move to it unless it requires action; use `aria-live` instead |

**Failure**: A modal closes and focus returns to `<body>` — keyboard users must Tab
through the entire page to find their place again.

---

## Quality Checklist

Before shipping any interactive component or flow:

- [ ] All functionality accessible by keyboard only — Tab, arrows, Enter, Space, Escape
- [ ] Tab order follows logical reading/task order (no `tabindex > 0`)
- [ ] Modal dialogs trap focus correctly and return focus on close
- [ ] No unintended focus traps — all components navigable out of with standard keys
- [ ] Skip navigation present and functional
- [ ] Keyboard shortcuts (if any) can be turned off or remapped
- [ ] All visible label text matches or is included in accessible name (WCAG 2.5.3)
- [ ] Icon-only buttons have visible labels or descriptive aria-labels
- [ ] Touch/click targets are ≥44×44px on touch surfaces; ≥24×24px minimum (WCAG 2.5.8)
- [ ] Minimum 8px spacing between adjacent interactive targets
- [ ] Drag-and-drop has a non-drag keyboard/pointer alternative (WCAG 2.5.7)
- [ ] Multi-finger gestures have single-pointer alternatives (WCAG 2.5.1)
- [ ] Pointer activation uses up-event or provides undo (WCAG 2.5.2)
- [ ] Focus management on dynamic events (modal open/close, route change, errors)
- [ ] Long-task flows support save-and-return; don't require single-session completion

---

## Cross-Links

| Skill | Relationship |
|-------|-------------|
| `a11y-assistive-tech` | AT internals for switch scanning, Dragon internals, and keyboard mode behavior in screen readers |
| `a11y-visual` | Focus indicator design (WCAG 2.4.7 / 2.4.11) lives in visual but keyboard access is motor-physical |
| `a11y-legal-compliance` | WCAG 2.1.1, 2.1.2, 2.4.3, 2.5.1, 2.5.2, 2.5.3, 2.5.7, 2.5.8 legal standards and audit methodology |
| `uid-iconography` | Touch target size, visible label requirement for voice control compatibility |
| `fe-accessibility` | Keyboard interaction implementation — event handlers, focus traps, tab order in code |
| `lead-accessibility-architect` | Hub — routes to this spoke for keyboard navigation, switch access, voice control, target size, and tremor accommodation |
