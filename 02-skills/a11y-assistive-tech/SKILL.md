---
name: a11y-assistive-tech
description: >
  Screen reader internals, AT testing protocols, switch scanning, eye tracking, voice
  control internals, and AT market landscape. Spoke skill in the lead-accessibility-architect
  network. Use this skill whenever the conversation touches: screen reader, NVDA,
  JAWS, VoiceOver, TalkBack, Narrator, screen reader testing, AT testing protocol,
  browse mode, application mode, forms mode, ARIA roles, ARIA states, ARIA properties,
  aria-live, aria-atomic, aria-relevant, aria-label, aria-labelledby, aria-describedby,
  aria-expanded, aria-haspopup, aria-selected, aria-checked, role="button", role="dialog",
  role="alert", role="status", role="log", focus management, live regions, landmark
  navigation, heading navigation, virtual cursor, reading mode, switch access, switch
  scanning, iOS Switch Control, Android Switch Access, eye tracking, Tobii, dwell
  selection, Dragon NaturallySpeaking, Dragon accessibility, Voice Control macOS,
  AT market share, WebAIM screen reader survey, browser pairing, NVDA Firefox, JAWS
  Chrome, VoiceOver Safari, ARIA Authoring Practices Guide, APG, widget patterns.
---

# a11y-assistive-tech

Specialist lens for assistive technology internals, ARIA implementation, and AT
testing protocols. Part of the `lead-accessibility-architect` skill network.

---

## Domain Boundary

This skill owns **AT internals and ARIA implementation** — how screen readers interpret
markup, how switch access scans, how voice control activates elements, and how to
test with AT.

- **Design decisions that AT depends on** → other a11y spokes (this spoke handles the
  implementation; spokes like `a11y-visual` and `a11y-motor-physical` handle design)
- **Legal requirements for AT support** → `a11y-legal-compliance`
- **Frontend implementation** → `fe-accessibility`

---

## Screen Reader Market Landscape

Screen reader market share is dominated by a small number of applications. Data from
WebAIM Screen Reader User Survey (most recent: 2024).

| Screen Reader | Platform | Cost | Primary Use | Market Share (Primary) |
|--------------|---------|------|------------|----------------------|
| JAWS | Windows | ~$1,100/yr | Enterprise/corporate | ~53% |
| NVDA | Windows | Free (open source) | Broad | ~31% |
| VoiceOver | macOS, iOS | Free (built-in) | Apple users | ~9% macOS, dominant iOS |
| TalkBack | Android | Free (built-in) | Android mobile | Standard for Android |
| Narrator | Windows | Free (built-in) | Windows users | ~7% |
| Orca | Linux | Free (built-in) | Linux | Minority |

**Browser pairing is critical**. Screen reader behavior varies significantly by
browser. Test with the correct pairings:

| Screen Reader | Best Browser | Notes |
|--------------|-------------|-------|
| NVDA | Firefox | Best compatibility; Chrome also acceptable |
| JAWS | Chrome | Best compatibility; Edge acceptable |
| VoiceOver (macOS) | Safari | Required; Chrome on macOS has reduced VoiceOver support |
| VoiceOver (iOS) | Safari | Only testing browser for iOS AT |
| TalkBack | Chrome | Standard pairing |
| Narrator | Edge | Best pairing |

Testing with only VoiceOver+Safari will miss issues that affect 80% of screen reader users.
A minimum test coverage includes NVDA+Firefox, JAWS+Chrome (if enterprise), VoiceOver+Safari.

---

## Screen Reader Interaction Models

### Browse Mode / Reading Mode (Virtual Cursor)

In browse mode, the screen reader creates a "virtual" representation of the page
and the user navigates it with the arrow keys — independently of keyboard focus.
This is the default mode when navigating most web content.

- Arrow keys: move through all text and elements sequentially
- Single-key shortcuts: H (headings), 1-6 (heading levels), B (buttons), F (form fields),
  L (lists), T (tables), I (images), G (graphics), R (regions/landmarks), etc.
- These single-key navigation shortcuts are why WCAG 2.1.4 (Character Key Shortcuts) matters:
  web app single-character shortcuts conflict with SR navigation

### Forms Mode / Application Mode

When users Tab to a form field or enter an element with `role="application"`,
NVDA and JAWS automatically switch to forms mode:
- Arrow keys now move between form fields, not through page content
- Characters are typed into fields rather than triggering navigation shortcuts
- Screen readers announce field labels, types, and current values

**Common failure**: A rich text editor, custom widget, or ARIA live region uses
`role="application"` when it shouldn't, trapping the user in forms mode and
disabling navigation shortcuts. `role="application"` should be used only for
truly application-like widgets (like a drawing canvas), never for content regions.

### Mode Transitions

Users may not realize they've entered forms mode or need to return to browse mode.
NVDA/JAWS announce mode changes, but users can get disoriented.

**Design implication**: Components that function as interactive widgets but also
contain navigable content (like a rich table with sorting, filtering, and inline
editing) need careful ARIA role selection to support both browse and forms mode
navigation appropriately.

---

## ARIA Fundamentals

ARIA (Accessible Rich Internet Applications) is a set of HTML attributes that
supplement native HTML semantics to describe the role, state, and properties of
custom interactive elements.

### The First Rule of ARIA

**Use native HTML elements first.** If a native element exists that provides the
required semantics (e.g., `<button>`, `<input type="checkbox">`, `<select>`), use it.
ARIA is for when no native element exists or when semantics need to be augmented.

A `<button>` is better than `<div role="button" tabindex="0">`. The native button:
- Has keyboard handling built-in (Enter and Space activate it)
- Is in the tab order by default
- Has proper browser focus management
- Communicates its role without ARIA

Bad ARIA is worse than no ARIA. Incorrect roles, missing state updates, or
inconsistent use can actively mislead AT users.

### ARIA Roles

Roles describe the type of element. They establish what the element is and what
interaction patterns it supports:

| Category | Example Roles | Notes |
|----------|--------------|-------|
| Widget roles | `button`, `checkbox`, `combobox`, `dialog`, `menu`, `menuitem`, `option`, `radio`, `slider`, `switch`, `tab`, `tabpanel`, `treeitem` | Require associated keyboard interaction patterns |
| Structure roles | `heading`, `list`, `listitem`, `table`, `row`, `cell`, `columnheader`, `rowheader` | Semantic structure |
| Landmark roles | `banner`, `complementary`, `contentinfo`, `form`, `main`, `navigation`, `region`, `search` | Page navigation regions |
| Live region roles | `alert`, `status`, `log`, `marquee`, `timer` | Dynamic content announcements |

Landmark roles are supported by native HTML elements: `<header>` = `banner`,
`<nav>` = `navigation`, `<main>` = `main`, `<footer>` = `contentinfo`, `<aside>` =
`complementary`. Prefer the HTML elements.

### ARIA States and Properties

States communicate current condition (can change); properties communicate
configuration (less likely to change):

| Attribute | Type | Communicates |
|-----------|------|-------------|
| `aria-expanded` | State | Whether a disclosure, accordion, dropdown is open or closed |
| `aria-selected` | State | Whether a tab, option, treeitem is selected |
| `aria-checked` | State | Whether a checkbox/radio/switch is checked |
| `aria-disabled` | State | Whether an element is disabled |
| `aria-hidden` | State | Whether an element is hidden from AT (but visible on screen) |
| `aria-invalid` | State | Whether a form field has an error |
| `aria-pressed` | State | Whether a toggle button is pressed |
| `aria-current` | State | Indicates the current item in a set (e.g., current page in nav) |
| `aria-label` | Property | Provides accessible name when visible text is insufficient |
| `aria-labelledby` | Property | Associates accessible name from another element's text |
| `aria-describedby` | Property | Associates additional description from another element |
| `aria-haspopup` | Property | Indicates the element opens a popup (menu, listbox, dialog) |
| `aria-controls` | Property | Identifies the element this control manages |
| `aria-owns` | Property | Identifies owned elements when DOM structure can't reflect it |

**Critical**: States must be updated in JavaScript when the component state changes.
An accordion with `aria-expanded="false"` that doesn't update to `aria-expanded="true"`
when opened tells the screen reader the accordion is still closed.

### Accessible Name Computation

The accessible name is what screen readers announce when an element receives focus.
The browser computes it using the following priority order:

1. `aria-labelledby` (references text of another element)
2. `aria-label` (explicit string)
3. Native label: `<label for="id">`, `<button>text content</button>`, `<img alt="...">`,
   `<input title="...">`
4. `title` attribute (fallback, but avoid — it's visually hidden and inconsistently supported)
5. `placeholder` — not recommended as accessible name; disappears on input

For composite elements: the accessible name is computed from the element's text
content (concatenated text of all child elements).

**Test the accessible name** using browser accessibility inspector (Firefox Accessibility
panel, Chrome Accessibility panel, Accessibility Insights).

---

## Live Regions

Live regions allow screen readers to announce dynamic content changes without
the user moving focus to the changed area.

### Live Region Roles

| Role | Politeness | Use Case |
|------|-----------|---------|
| `role="alert"` | Assertive — interrupts | Error messages, important warnings |
| `role="status"` | Polite — waits for current speech | Success messages, form save confirmations |
| `role="log"` | Polite | Chat logs, activity feeds |
| `role="timer"` | Off by default | Countdown timers (announce deliberately) |

### `aria-live` Values

| Value | Behavior |
|-------|---------|
| `assertive` | Interrupts the current announcement immediately |
| `polite` | Announces after the current speech completes |
| `off` | No announcement (default) |

`assertive` should be reserved for truly urgent information. Overusing assertive
interrupts the user's reading flow. Form validation errors appearing on submit
can be `assertive`; auto-save success messages should be `polite`.

### Live Region Implementation Gotchas

- The live region element must exist in the DOM before content is injected into it —
  injecting the live region element itself does not trigger announcement
- `aria-atomic="true"` causes the entire live region to be announced when any part
  changes; useful for status messages that need context ("Saved 3 of 5 changes")
- Empty the live region before injecting new content to ensure re-announcement
- `aria-relevant` controls what changes trigger announcement: "additions" (default),
  "removals", "text", "all" — usually leave as default

---

## Focus Management for Dynamic Interfaces

Screen reader users navigate by focus. When content changes dynamically, focus must
be managed deliberately:

| Situation | Focus Action |
|----------|-------------|
| Dialog opens | Move focus to first focusable element in dialog, or dialog container with `tabindex="-1"` |
| Dialog closes | Return focus to the element that triggered the dialog |
| Toast/notification | Do NOT move focus; use `aria-live` region instead |
| Error occurs after form submit | Move focus to first error message, or error summary |
| SPA route change | Move focus to new page's `<h1>` or `<main tabindex="-1">` |
| Inline expansion (accordion, details) | Leave focus on the trigger; content flows below |
| Modal within a flow (step 2 of 5 dialog) | Focus the modal; when closed, return to trigger |

`tabindex="-1"` makes an element programmatically focusable (via `element.focus()`)
without adding it to the natural tab order. Use it on containers (`<main>`, `<h1>`,
dialog wrapper) to receive programmatic focus.

---

## Switch Access and Scanning Internals

### iOS Switch Control

Users add switches via Bluetooth or directly via the Apple Switch Control settings.
iOS Switch Control scans items by highlighting them in sequence:

- **Item scanning**: highlights individual interactive elements one at a time
- **Point scanning**: moves crosshairs (for cases where item scanning misses elements)
- **Group scanning**: cycles through groups (apps, panels) then scans within

Testing: Enable in Settings → Accessibility → Switch Control. Can be controlled
with keyboard on simulator.

**Design implication**: App navigation bar, primary content, and sidebar are separate
scan groups if landmark structure is correct. This reduces the scan steps to reach
any target.

### Android Switch Access

Similar scanning model to iOS. Enabled in Settings → Accessibility → Switch Access.

**Two-switch scanning** is most common:
- Next switch: advance to next item
- Select switch: activate current item

Group scanning via navigation landmarks also applies.

### Web Switch Access

Web-based switch access uses the browser's focusable element sequence (same as
keyboard Tab order). No native group scanning in web — users scan through all
focusable elements in DOM order.

This makes the volume of focusable elements per view the primary UX variable
for switch users. See `a11y-motor-physical` for design-level guidance.

---

## Eye Tracking

Eye tracking allows users to control a pointer by gaze direction. Hardware: Tobii
Dynavox (dedicated AT), built-in camera (iOS AssistiveTouch face tracking, macOS
Head Pointer, Windows Eye Control).

### Dwell Selection

Most eye tracking interfaces use "dwell" — the user looks at an element for a set
duration (typically 0.5–1.5 seconds) to activate it. This has implications:
- Target must be large enough to dwell on stably (recommend ≥60×60px for eye tracking;
  44px targets are the keyboard minimum, not the eye tracking optimum)
- Closely spaced targets cause accidental activation as the gaze drifts
- Modal dialogs and overlays that appear over the target break the dwell activation
  if they appear before the full dwell duration

### Fatigue and Efficiency

Eye tracking is the most cognitively and physically fatiguing input modality. Users
report fatigue within 20-30 minutes of extended use. Design implications:
- Minimize task length for eye tracking users
- Group related controls spatially so gaze movement is minimized
- Reduce the number of interactions required to complete primary tasks

---

## Voice Control Internals

### Dragon NaturallySpeaking (Dragon Professional, Dragon Home)

Dragon NaturallySpeaking is the market leader for voice control on Windows. It works by:

1. **Speech recognition**: converting speech to text
2. **Command matching**: matching spoken phrases to action patterns
3. **Target identification**: identifying the on-screen element to act on

**Say what you see**: Users say "click [visible label]" to activate elements. Dragon
identifies the element with text matching the spoken phrase.

**Show Numbers mode**: Dragon overlays numbers on all interactive elements. Users
say "click 7" to activate the 7th element. This mode bypasses label matching but
is slow and cognitively demanding. It should not be the primary interaction model.

**MouseGrid**: Dragon shows a grid overlay and users navigate via numbers. Fallback
for elements with no accessible labels.

**Consistency requirement**: The same element must always have the same visible label.
If an element's label changes dynamically ("3 items selected" → "5 items selected"),
users whose Dragon profiles memorized the label will fail to activate it.

### macOS/iOS Voice Control

Built into macOS (10.15+) and iOS (13+). Similar "say what you see" model.

Features:
- "Show numbers": shows numbers on interactive elements
- "Show names": shows accessible names on interactive elements — this is where
  `aria-label` vs visible text mismatch becomes visible
- "Click [name]" to activate any element

Testing: Enable in System Settings → Accessibility → Voice Control.

---

## AT Testing Protocol

A complete AT testing protocol for a web product:

### Step 1: Automated Scan
- Run axe-core (axe DevTools browser extension or CI integration)
- Run WAVE (supplementary; different ruleset)
- Document all errors; triage by severity

### Step 2: Keyboard-Only Navigation
- Disconnect mouse
- Navigate all primary flows: Tab, Shift-Tab, arrows, Enter, Space, Escape
- Verify: focus visible, tab order logical, no traps, all functionality accessible

### Step 3: NVDA + Firefox
- Enable NVDA; open Firefox
- Navigate page structure: headings (H), landmarks (R), links (K)
- Complete primary user flows using screen reader conventions
- Listen for: page title announced on load, form labels announced on focus,
  error messages announced, dynamic changes announced via live regions

### Step 4: VoiceOver + Safari (macOS)
- Enable VoiceOver (Cmd+F5); open Safari
- Same navigation checks as NVDA
- VoiceOver-specific: Ctrl+Option+U for Elements menu; Ctrl+Option+Right/Left for navigation

### Step 5: VoiceOver + Safari (iOS) — if mobile
- Enable VoiceOver in Settings → Accessibility
- Swipe right to navigate; double-tap to activate
- Verify: all interactive elements reachable, labels announced, dynamic content announced

### Step 6: Zoom Testing
- Browser zoom to 200%: no content loss, no horizontal scrolling on primary views
- Browser zoom to 400%: reflow test — single column, no horizontal scrolling

### Step 7: Color Blindness Simulation
- Chrome DevTools → More tools → Rendering → Emulate vision deficiencies
- Test: deuteranopia and protanopia simulations at minimum
- Verify: all information intelligible without color differentiation

### Step 8: Contrast Verification
- Run automated contrast check (axe-core catches most)
- Manually verify: focus indicators, placeholder text, disabled states if they
  convey meaningful information

---

## Quality Checklist

- [ ] All custom interactive elements have appropriate ARIA roles
- [ ] All ARIA states updated programmatically on state change
- [ ] Accessible names computed correctly for all interactive elements (verified in browser devtools)
- [ ] Live regions correctly typed (alert vs. status) and populated after DOM insertion
- [ ] Focus managed correctly for: dialogs, modals, errors, route changes
- [ ] Browse mode navigation coherent (headings logical, landmarks present)
- [ ] Forms mode navigation coherent (fields labeled, errors announced)
- [ ] NVDA+Firefox: all primary flows completable
- [ ] VoiceOver+Safari: all primary flows completable
- [ ] Keyboard-only: all primary flows completable
- [ ] 200% zoom: no content loss
- [ ] 400% zoom: no horizontal scroll on standard views
- [ ] Color blindness simulation: all information intelligible
- [ ] All visible labels match or are contained in accessible names (voice control)

---

## Cross-Links

| Skill | Relationship |
|-------|-------------|
| `a11y-motor-physical` | Keyboard navigation design model; switch access scanning design; this spoke covers AT behavior during keyboard navigation |
| `a11y-visual` | Screen reader design decisions (alt text, reading order, heading structure) are design layer; this spoke is AT implementation layer |
| `a11y-legal-compliance` | Audit methodology framework; this spoke provides the testing protocol |
| `fe-accessibility` | Code implementation of ARIA patterns documented here |
| `lead-accessibility-architect` | Hub — routes to this spoke for AT internals, ARIA implementation, testing protocol, and Dragon NaturallySpeaking |
