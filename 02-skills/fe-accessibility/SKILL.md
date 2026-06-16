---
name: fe-accessibility
description: >
  ARIA implementation, keyboard navigation patterns, screen reader testing,
  WCAG compliance in code, and focus management for enterprise SaaS frontends.
  Use this skill whenever the conversation touches: ARIA, aria-label,
  aria-labelledby, aria-describedby, aria-live, aria-expanded, aria-controls,
  aria-activedescendant, aria-selected, aria-checked, aria-disabled, aria-hidden,
  role, landmark roles, focus management, focus trap, roving tabindex,
  tabindex, skip links, focus visible, WCAG 2.1, WCAG 2.2, APCA contrast,
  color contrast, screen reader, NVDA, JAWS, VoiceOver, TalkBack, keyboard
  navigation, keyboard shortcuts, combobox ARIA, data grid ARIA, tree view
  ARIA, dialog ARIA, modal, tab panel ARIA, WAI-ARIA Authoring Practices Guide,
  APG, axe-core, jest-axe, focus indicator, outline, VPAT, accessibility
  audit, or any question about making an enterprise SaaS UI operable by all
  users including those using assistive technology.
---

# FE Accessibility

Specialist lens for ARIA implementation, keyboard navigation, and WCAG compliance
in enterprise SaaS frontends. Part of the enterprise SaaS frontend engineering
network.

---

## Domain Boundary

This skill owns **accessibility implementation** — ARIA in code, keyboard
interaction patterns, focus management, and screen reader behavior.

- **Accessibility design decisions** (focus order, label copy, interaction model) → `ux-accessibility`
- **Accessible component API design, headless UI ARIA** → `fe-component-architecture`
- **Automated accessibility testing integration** → `fe-testing`

**ARIA bugs often originate in design decisions.** Before assuming it's an
implementation problem, confirm that the interaction model was designed with
accessibility in mind. Route to `ux-accessibility` if the root cause is design.

---

## ARIA Fundamentals

### The First Rule of ARIA

> Do not use ARIA if there is a native HTML element or attribute that has the
> semantics and behavior you need.

A `<button>` has built-in keyboard activation (Enter and Space), correct role
(`button`), focusability, and screen reader announcement. A `<div role="button">
tabindex="0"` requires you to manually implement keyboard handling, and you will
forget Space activation or the `aria-disabled` state.

Use native elements. Use ARIA to extend or modify semantics when native HTML
is insufficient.

### ARIA Roles, Properties, and States

- **Role**: what the element is (`role="dialog"`, `role="combobox"`, `role="grid"`)
  — static, set at render time
- **Properties**: characteristics that don't change during a session
  (`aria-label="Close"`, `aria-haspopup="listbox"`) — or change infrequently
- **States**: current condition that changes during interaction
  (`aria-expanded`, `aria-selected`, `aria-checked`, `aria-disabled`)

States must be kept in sync with UI state. `aria-expanded="false"` on a button
that opens an open menu is worse than no ARIA at all — it actively misinforms
screen reader users.

### Naming: aria-label vs. aria-labelledby vs. aria-describedby

**Hierarchy** (applied in this order by the accessibility tree):
1. `aria-labelledby` — references another element's text as the label (preferred)
2. `aria-label` — inline string label (when no visible text exists to reference)
3. Native label (`<label for>` on form elements)
4. Element content (for interactive elements without explicit labeling)

**`aria-labelledby`** is preferred because it reuses visible text — the label
the sighted user reads is the same text announced to screen reader users,
preventing divergence:

```html
<h2 id="dialog-title">Delete Product</h2>
<div role="dialog" aria-labelledby="dialog-title" aria-modal="true">
  <!-- Screen reader announces "Delete Product, dialog" -->
</div>
```

**`aria-describedby`** provides supplementary information after the primary label.
Use for helper text, error messages, or additional context:

```html
<input
  id="email"
  type="email"
  aria-describedby="email-hint email-error"
/>
<span id="email-hint">We'll only use this for account notifications</span>
<span id="email-error" role="alert">Must be a valid email address</span>
```

**`aria-label` pitfalls**: creates a divergence between visible and announced
text. Any change to the visible label requires updating the `aria-label` too.
Only use when there is no visible text to reference (icon buttons, close buttons).

### Live Regions

Dynamic content that changes without a page navigation must be announced to screen
reader users via live regions:

```html
<!-- Polite: waits for current announcement to finish -->
<div aria-live="polite" aria-atomic="true" class="visually-hidden">
  <!-- Toast/notification messages injected here by JS -->
</div>

<!-- Assertive: interrupts the current announcement (use sparingly) -->
<div aria-live="assertive" role="alert">
  <!-- Error messages, critical status changes -->
</div>
```

**`aria-atomic="true"`**: the entire region is read when any part changes.
Use for messages — without it, only the changed text is read, which can be
a sentence fragment.

**Common live region mistakes:**
- Injecting content into a live region before it's mounted (the region must
  exist in the DOM before content is injected — it won't catch initial mount)
- Using `assertive` for non-critical messages (interrupts the user's current
  focus and reading flow — reserve for genuine errors and alerts)
- Toasts that auto-dismiss before the screen reader finishes reading them

### Landmark Roles

Landmarks provide structural navigation for screen reader users who navigate
by landmark (`F` key in JAWS, `R` in NVDA, rotor in VoiceOver):

| Role | HTML element | Use for |
|------|-------------|---------|
| `main` | `<main>` | Primary content of the page |
| `navigation` | `<nav>` | Navigation menus — must have unique `aria-label` if multiple navs |
| `banner` | `<header>` (direct child of body) | App header |
| `contentinfo` | `<footer>` (direct child of body) | App footer |
| `complementary` | `<aside>` | Secondary content |
| `search` | `<search>` or `role="search"` | Search forms |
| `region` | `<section>` | Named section — requires `aria-label` or `aria-labelledby` |

Every page should have exactly one `main`. Multiple `nav` landmarks must each
have a unique `aria-label` (`aria-label="Primary navigation"`, `aria-label="Breadcrumb"`).

---

## Keyboard Navigation Patterns

### Focus Management

**Natural tab order**: elements receive focus in DOM source order by default.
Do not use `tabindex > 0` to manipulate this — it creates a parallel focus order
that diverges from visual layout and is a maintenance burden. Fix visual layout
instead to match the intended tab order.

`tabindex="0"`: adds a non-interactive element to the natural tab order.
`tabindex="-1"`: makes an element programmatically focusable but removes it from
the natural tab order. Essential for focus management in modals and routing.

**Programmatic focus on route change**: when a SPA route changes, focus must be
moved to signal the change to screen reader users. Options:
- Move focus to the `<h1>` of the new page
- Move focus to the top of `<main>`
- Use a "page announcement" live region

Without this, screen reader users navigating by link or keyboard are left at
the last focused element with no indication that the page changed.

**Modals and dialogs**: on open, move focus to the first interactive element
inside the dialog (or the dialog itself if there's a title). On close, return
focus to the element that triggered the open.

### Focus Trap

For modals, drawers, and popover menus: Tab and Shift+Tab must cycle within the
dialog, not escape to the page behind it.

Implementation pattern (or use `focus-trap` npm package / Radix `<Dialog>`):

```ts
function trapFocus(element: HTMLElement) {
  const focusable = element.querySelectorAll<HTMLElement>(
    'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), ' +
    'textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
  );
  const first = focusable[0];
  const last = focusable[focusable.length - 1];

  element.addEventListener('keydown', (e) => {
    if (e.key !== 'Tab') return;
    if (e.shiftKey) {
      if (document.activeElement === first) { e.preventDefault(); last.focus(); }
    } else {
      if (document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });
}
```

### Roving Tabindex

For composite widgets (toolbars, menus, listboxes, grids, tab lists): only one
item in the group should be in the tab sequence at a time. Arrow keys navigate
within the group; Tab exits.

```ts
// Roving tabindex implementation
function RovingTabGroup({ items }) {
  const [activeIndex, setActiveIndex] = useState(0);

  function handleKeyDown(e: KeyboardEvent, index: number) {
    let next = index;
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
      next = (index + 1) % items.length;
    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
      next = (index - 1 + items.length) % items.length;
    } else if (e.key === 'Home') next = 0;
    else if (e.key === 'End') next = items.length - 1;
    else return;

    e.preventDefault();
    setActiveIndex(next);
    itemRefs[next].focus();
  }

  return items.map((item, i) => (
    <button
      key={item.id}
      tabIndex={i === activeIndex ? 0 : -1}
      onKeyDown={(e) => handleKeyDown(e, i)}
      ref={el => { itemRefs[i] = el; }}
    >
      {item.label}
    </button>
  ));
}
```

### Focus Indicators (WCAG 2.2)

WCAG 2.2 SC 2.4.11 (Focus Appearance, AA) requires focus indicators that:
- Have a perimeter around the component at least as long as the perimeter of a
  2×2 CSS px area
- Meet a 3:1 contrast ratio against adjacent colors when focused vs. unfocused

**Never `outline: none` without a replacement.** Removing focus rings without
providing a visible alternative is a WCAG failure. Design the focus indicator
in the design system; do not let component code suppress it.

### Skip Links

Skip links allow keyboard users to bypass repetitive navigation:

```html
<a href="#main-content" class="skip-link">Skip to main content</a>
<!-- visible on :focus, otherwise visually hidden but not display:none -->

<main id="main-content" tabindex="-1">
  <!-- tabindex="-1" allows programmatic focus via the skip link's href -->
</main>
```

In enterprise SaaS with complex navigation sidebars, skip links are essential.
Without them, every page navigation requires tabbing through the entire sidebar
before reaching the content.

---

## Complex Widget Patterns (WAI-ARIA APG)

### Combobox / Autocomplete

```html
<label id="fruit-label">Fruit</label>
<input
  type="text"
  role="combobox"
  aria-expanded="true"
  aria-controls="fruit-listbox"
  aria-activedescendant="fruit-option-2"
  aria-labelledby="fruit-label"
  aria-autocomplete="list"
/>
<ul
  id="fruit-listbox"
  role="listbox"
  aria-label="Fruits"
>
  <li id="fruit-option-1" role="option" aria-selected="false">Apple</li>
  <li id="fruit-option-2" role="option" aria-selected="true">Banana</li>
</ul>
```

`aria-activedescendant` points to the currently highlighted option — the input
retains focus while announcing the option as if it had focus. This is the key
pattern for maintaining keyboard-navigable lists without moving DOM focus.

### Data Grid

```html
<table role="grid" aria-rowcount="2500" aria-colcount="12">
  <thead>
    <tr role="row">
      <th role="columnheader" aria-sort="ascending">Name</th>
      <th role="columnheader" aria-sort="none">Status</th>
    </tr>
  </thead>
  <tbody>
    <tr role="row" aria-rowindex="1">
      <td role="gridcell" tabindex="-1">Product A</td>
      <td role="gridcell" tabindex="-1">Active</td>
    </tr>
  </tbody>
</table>
```

For virtualized grids: `aria-rowcount` and `aria-colcount` declare the total
size; `aria-rowindex` and `aria-colindex` declare each cell's position in the
full grid. Without these, screen reader users only know about the rendered rows.

### Dialog / Modal

```html
<div
  role="dialog"
  aria-modal="true"
  aria-labelledby="dialog-title"
  aria-describedby="dialog-description"
>
  <h2 id="dialog-title">Confirm Deletion</h2>
  <p id="dialog-description">
    This will permanently delete 3 products. This action cannot be undone.
  </p>
  <button>Cancel</button>
  <button>Delete</button>
</div>
```

`aria-modal="true"` tells screen readers to treat content behind the dialog as
inert. Combined with `inert` attribute on the background DOM in modern browsers.

### Tabs

```html
<div>
  <ul role="tablist" aria-label="Product details">
    <li role="presentation">
      <button role="tab" aria-selected="true" aria-controls="panel-overview" id="tab-overview">
        Overview
      </button>
    </li>
    <li role="presentation">
      <button role="tab" aria-selected="false" aria-controls="panel-specs" id="tab-specs" tabindex="-1">
        Specifications
      </button>
    </li>
  </ul>
  <div role="tabpanel" id="panel-overview" aria-labelledby="tab-overview">
    <!-- content -->
  </div>
  <div role="tabpanel" id="panel-specs" aria-labelledby="tab-specs" hidden>
    <!-- content -->
  </div>
</div>
```

Arrow keys navigate between tabs (roving tabindex). Activation model: automatic
(tab activates on arrow key) or manual (Enter/Space activates, arrows just move
focus). Manual is safer for tabs that trigger expensive data fetches.

---

## Screen Reader Testing Protocol

### Primary Test Matrix (Enterprise SaaS)

| Screen Reader | Browser | Why |
|--------------|---------|-----|
| NVDA + Firefox | Windows | Most common free SR, required for enterprise users |
| JAWS + Chrome | Windows | Enterprise gold standard, common in regulated industries |
| VoiceOver + Safari | macOS | Contractual requirement for Mac-using enterprise customers |
| VoiceOver + Safari (iOS) | iOS | Mobile accessibility testing |

### Testing Protocol

1. **Navigate by landmark** (`F`/`D` in JAWS, `R` in NVDA, Rotor in VoiceOver):
   can the user jump to `main`, `navigation`, and `search` directly?
2. **Navigate by heading** (`H`): does the heading hierarchy make the page
   structure navigable? (H1 → H2 → H3, no skipped levels)
3. **Navigate by form control**: are all inputs labeled? Do labels read
   correctly? Is field validation announced?
4. **Activate interactive elements**: do buttons announce their action? Do
   comboboxes announce expanded state and selected option?

### Common Screen Reader Bugs

| Bug | Root Cause | Fix |
|-----|-----------|-----|
| Icon button announced as "button" | Missing accessible name | `aria-label` on the button |
| Form field announced without label | Missing `<label>` or `aria-label` | Associate label via `for`/`id` or `aria-labelledby` |
| Dynamic content not announced | Content injected outside live region | Add content to `aria-live` container |
| Modal content announced behind dialog | Missing `aria-modal` + background not inert | `aria-modal="true"` + `inert` on background |
| Focus not managed after async load | Focus remains on trigger after content renders | `focus()` the heading or first interactive element after load |
| Combobox options not announced | `aria-activedescendant` not updating | Update `aria-activedescendant` on every arrow key press |

---

## WCAG Implementation Checklist

| SC | Level | What to check |
|----|-------|--------------|
| 1.4.3 Contrast | AA | 4.5:1 normal text, 3:1 large text (18pt or 14pt bold). Use APCA for more accurate prediction. |
| 1.4.4 Resize Text | AA | 200% browser zoom without horizontal scrolling or loss of content. CSS `px` for `font-size` fails this. Use `rem`. |
| 1.4.11 Non-text Contrast | AA | UI components and graphical objects need 3:1 against adjacent background. Focus indicators included. |
| 2.1.1 Keyboard | A | All functionality operable by keyboard. No keyboard traps except intentional modals. |
| 2.4.7 Focus Visible | AA | All keyboard-focusable elements have visible focus indicator. |
| 2.4.11 Focus Appearance | AA (WCAG 2.2) | Focus indicator minimum size and contrast requirements. |
| 3.3.1 Error Identification | A | Form errors are identified in text, not color alone. |
| 4.1.2 Name, Role, Value | A | All UI components have accessible name, correct role, and state/value announced. |
| 4.1.3 Status Messages | AA | Toasts, validation success, loading completion announced without receiving focus. |

---

## Automated Testing Integration

`axe-core` catches approximately 40% of accessibility issues automatically —
the rest require manual testing. Use automation to catch regressions, not as
a substitute for manual testing.

- `jest-axe`: component-level axe checks in unit tests
- `@axe-core/playwright`: E2E level axe checks
- Storybook a11y addon: per-story axe check in Storybook

Route to `fe-testing` for integration patterns.

---

## Cross-Links

| Topic | Route to |
|-------|----------|
| Accessibility design decisions, focus order, label copy | `ux-accessibility` |
| ARIA in headless component primitives | `fe-component-architecture` |
| jest-axe, Playwright accessibility, axe in CI | `fe-testing` |
