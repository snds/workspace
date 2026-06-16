---
name: fw-react-aria
description: >
  React Aria and Adobe React Spectrum — accessibility-first hooks and component library.
  Use this skill whenever the conversation involves React Aria hooks, Adobe Spectrum
  components, accessibility-first headless component patterns, ARIA pattern implementation,
  internationalization (i18n) in components, or choosing between React Aria and Radix UI
  as a headless primitive layer. Also trigger when building highly accessible custom
  components, discussing ARIA authoring practices, or implementing complex interaction
  patterns (drag-and-drop, virtualized lists, date pickers). If the user mentions
  "React Aria", "react-aria", "Adobe Spectrum", "useButton", "useDialog", or any
  React Aria hook — use this skill.
pinned_version: "3.47.0"
pinned_date: "2026-03-26"
changelog_url: "https://react-spectrum.adobe.com/releases/"
aliases: [fw-react-aria]
tier: spoke
domain: engineering
hub: lead-frontend-engineer
prerequisites: [lead-frontend-engineer]
spec_version: "2.0"
---

# React Aria / Adobe Spectrum — Framework Skill

## Version Check (run on every load)

1. Web search for `react-aria latest release`.
2. Compare against `pinned_version: 3.47.0`.
3. Flag if newer. Proceed with current knowledge.

---

## Core Concept

React Aria provides **hooks** (not components) that implement ARIA patterns. You compose
them into your own components with full control over rendering and styling.

React Spectrum is Adobe's styled component library built on React Aria. They're separate
concerns: React Aria = behavior, Spectrum = Adobe's visual expression.

### Hook-based vs compound component (Radix comparison)

| Aspect | React Aria | Radix UI |
|---|---|---|
| **API** | Hooks returning props | Compound components |
| **Rendering** | You render everything | Radix renders structure |
| **Control** | Maximum | High (via asChild) |
| **Bundle** | Tree-shakeable hooks | Per-primitive packages |
| **i18n** | Built-in | Not included |
| **DnD** | Built-in | Not included |

---

## Key Hook Categories

### Buttons & Links
- `useButton` — Button with press events (not click)
- `useToggleButton` — Pressed/unpressed
- `useLink` — Client-side routing integration

### Overlays
- `useDialog` — Modal/non-modal dialog
- `usePopover` — Positioned floating content
- `useTooltip` — Hover/focus information
- `useOverlayTrigger` — Manages overlay open/close state
- `useModal` — Focus containment

### Collections
- `useListBox` — Selectable list
- `useTable` — Data table with sorting, selection
- `useGridList` — Grid of selectable items
- `useTagGroup` — Tag/chip collection
- `useTree` — Hierarchical tree (v3.47+)

### Forms
- `useTextField` — Text input with validation
- `useNumberField` — Numeric input with formatting
- `useSearchField` — Search with clear
- `useCheckbox` / `useCheckboxGroup`
- `useRadioGroup`
- `useSlider` — Range input
- `useSwitch` — Toggle
- `useSelect` — Dropdown select
- `useComboBox` — Filterable select (multi-select support)
- `useDatePicker` / `useDateRangePicker`

### Navigation
- `useMenu` / `useMenuTrigger`
- `useTabs`
- `useBreadcrumbs`

---

## Usage Pattern

```tsx
import { useButton } from 'react-aria';
import { useRef } from 'react';

function Button(props) {
  const ref = useRef(null);
  const { buttonProps } = useButton(props, ref);

  return (
    <button {...buttonProps} ref={ref} className="btn">
      {props.children}
    </button>
  );
}
```

React Aria hooks return **props objects** that you spread onto your elements. This gives
you complete control over DOM structure and styling while getting accessibility for free.

---

## i18n (Built-In)

React Aria includes internationalization:

```tsx
import { I18nProvider } from 'react-aria';

<I18nProvider locale="ar-SA">
  <App />
</I18nProvider>
```

Handles: RTL, number formatting, date formatting, collation, and string translation.

---

## Design-Engineer Integration

Spoke of `design-engineer`. Use React Aria when:
- Maximum rendering control is needed
- i18n is a first-class requirement
- Complex interactions (DnD, virtualized lists, date pickers)
- You want hooks, not pre-composed components

Pair with **fw-tailwind-css** for styling and **fw-radix-colors** for the color system.
