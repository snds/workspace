---
name: fw-radix-primitives
description: >
  Radix UI headless primitives — unstyled, accessible React component building blocks
  (Dialog, Popover, Tabs, Select, Dropdown, ScrollArea, etc.). Use this skill whenever
  the conversation involves Radix UI primitives, headless component patterns, compound
  component APIs, accessibility behavior implementations, focus management, keyboard
  navigation patterns inherited from Radix, or choosing between Radix and Base UI as
  a primitive layer. Also trigger when building custom components on top of Radix
  primitives, debugging Radix-specific behavior, or discussing the behavioral contract
  of headless components. If the user mentions "Radix", "@radix-ui/react-*",
  "headless components", or any Radix primitive name — use this skill.
pinned_version: "radix-ui@1.4.3"
pinned_date: "2026-03-26"
changelog_url: "https://github.com/radix-ui/primitives/releases"
---

# Radix UI Primitives — Framework Skill

## Version Check (run on every load)

1. **Web search** for `radix-ui primitives latest release`.
2. **Compare** against `pinned_version: radix-ui@1.4.3`.
3. Flag if newer. Proceed with current knowledge.

---

## Core Concept

Radix provides **unstyled, accessible, behavioral primitives** — the interaction layer
beneath visual components. They handle focus management, keyboard navigation, ARIA
attributes, and state machines. You provide all styling.

### Package migration (2026)

Radix now recommends the unified `radix-ui` package over individual `@radix-ui/react-*`
packages to prevent version conflicts:

```bash
# Recommended
npm install radix-ui

# Legacy (still works)
npm install @radix-ui/react-dialog @radix-ui/react-popover
```

---

## Available Primitives

### Overlay/Modal
- **Dialog** — Modal and non-modal dialogs with focus trap
- **AlertDialog** — Confirmation dialogs requiring explicit action
- **Popover** — Non-modal floating content anchored to trigger
- **Tooltip** — Brief informational overlay on hover/focus
- **HoverCard** — Rich content preview on hover

### Navigation
- **NavigationMenu** — Site navigation with active indicators
- **Menubar** — Application menu bar (File, Edit, View pattern)
- **DropdownMenu** — Action menu triggered by button
- **ContextMenu** — Right-click menu

### Form/Input
- **Select** — Custom select with search, groups, keyboard nav
- **Combobox** — Filterable select (multi-select in v1.4+)
- **Checkbox** — Binary + indeterminate states
- **RadioGroup** — Single selection from group
- **Switch** — Toggle control
- **Slider** — Range input with keyboard support
- **Toggle** — Pressed/unpressed state
- **ToggleGroup** — Single or multi-selection toggle set

### Layout/Content
- **Tabs** — Tabbed interface with ARIA tablist
- **Accordion** — Expandable sections (single or multiple)
- **Collapsible** — Show/hide content
- **ScrollArea** — Custom scrollbar with keyboard support
- **Separator** — Visual divider with ARIA separator role
- **AspectRatio** — Constrained aspect ratio container

### Utility
- **Label** — Accessible form label binding
- **Progress** — Determinate/indeterminate progress
- **Avatar** — Image with fallback
- **Toast** — Temporal notification

---

## Compound Component API Pattern

Radix uses a compound component pattern — composed from multiple parts:

```tsx
import * as Dialog from 'radix-ui/dialog';

<Dialog.Root>
  <Dialog.Trigger>Open</Dialog.Trigger>
  <Dialog.Portal>
    <Dialog.Overlay className="fixed inset-0 bg-black/50" />
    <Dialog.Content className="fixed top-1/2 left-1/2 ...">
      <Dialog.Title>Heading</Dialog.Title>
      <Dialog.Description>Body text</Dialog.Description>
      <Dialog.Close>×</Dialog.Close>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
```

### Key patterns across all primitives

- **Root** — State container, controlled/uncontrolled via `value`/`defaultValue` + `onValueChange`
- **Trigger** — Element that opens/activates the primitive
- **Content** — The revealed content area
- **Portal** — Renders content outside the DOM tree (for overlays)
- **Close** — Dismissal affordance

---

## Accessibility Built-Ins

Every primitive ships with:

| Feature | Implementation |
|---|---|
| **Focus trap** | Modals trap focus within content; return focus on close |
| **Keyboard nav** | Arrow keys for menus/tabs, Escape to dismiss, Enter/Space to activate |
| **ARIA roles** | Automatic role assignment (menu, dialog, tablist, etc.) |
| **ARIA states** | aria-expanded, aria-selected, aria-checked, aria-pressed |
| **Screen readers** | Live regions, announce-on-change for dynamic content |

---

## Controlled vs Uncontrolled

Every primitive supports both patterns:

```tsx
// Uncontrolled (manages own state)
<Tabs.Root defaultValue="tab1">

// Controlled (you manage state)
const [tab, setTab] = useState("tab1");
<Tabs.Root value={tab} onValueChange={setTab}>
```

---

## asChild Pattern

The `asChild` prop merges Radix behavior onto your own element:

```tsx
<Dialog.Trigger asChild>
  <Button variant="outline">Open Dialog</Button>
</Dialog.Trigger>
```

This avoids wrapping elements and preserves your component's DOM structure.

---

## Radix vs Base UI (2026 Choice)

| Aspect | Radix UI | Base UI (MUI) |
|---|---|---|
| API style | Compound components | Hook-based |
| Bundle size | Larger | Smaller |
| Ecosystem | shadcn default | shadcn `--base-ui` |
| State management | Built-in | You compose |
| Learning curve | Lower (declarative) | Higher (imperative) |

Choose Radix for declarative composition. Choose Base UI for maximum control and smaller bundles.

---

## Design-Engineer Integration

This skill is a spoke of `design-engineer` and `ds-generation-pipeline`.
Pair with:
- **fw-shadcn** — Composes styled components from Radix primitives
- **fw-tailwind-css** — Styles Radix primitives with utility classes
- **fw-radix-colors** — Provides the color tokens for state indication
