---
name: fw-carbon
description: >
  IBM Carbon Design System — component library, token architecture, CSS Grid layout,
  and design language for enterprise applications. Use this skill whenever the
  conversation involves Carbon Design System components, Carbon tokens, Carbon's
  2× grid system, Carbon for React/Vue/Angular/Web Components, or analyzing/referencing
  Carbon as a design system exemplar. Also trigger when discussing enterprise DS
  patterns that Carbon implements well (data tables, notifications, shell/navigation),
  or when the target stack uses Carbon. If the user mentions "Carbon", "IBM Carbon",
  "@carbon/react", Carbon tokens, or the 2× grid — use this skill.
pinned_version: "11 (v12 in progress)"
pinned_date: "2026-03-26"
changelog_url: "https://github.com/carbon-design-system/carbon/releases"
---

# IBM Carbon Design System — Framework Skill

## Version Check (run on every load)

1. Web search for `IBM Carbon design system latest release`.
2. Compare against `pinned_version: 11`.
3. Flag if v12 has shipped. Proceed with current knowledge.

---

## Architecture

Carbon is a multi-framework design system with:
- **Carbon React** (`@carbon/react`) — Primary implementation
- **Carbon Web Components** (`@carbon/web-components`) — Framework-agnostic
- **Carbon Vue** (community maintained)
- **Carbon Angular** (community maintained)

### Token structure

Carbon uses a 3-tier token model matching the `global → semantic → component` pattern:

```
Global:     $spacing-05 (1.25rem), $blue-60 (#0f62fe)
Semantic:   $interactive-01, $text-primary, $layer-01
Component:  $button-primary, $input-border
```

### 2× Grid System

Carbon's layout uses an 8px base unit ("2×" = 2 × 4px sub-grid):

- **Mini unit**: 8px (2 × 4px)
- **Columns**: 16-column grid (wide), 12-column (narrow)
- **Gutters**: 32px (wide), 16px (narrow), 0px (condensed)
- **Margins**: Responsive per breakpoint

### Key component patterns worth studying

| Pattern | Why it's notable |
|---|---|
| **DataTable** | Sortable, selectable, expandable, batchable — covers every enterprise table need |
| **UIShell** | Header + side nav + content — canonical enterprise shell |
| **Notifications** | Inline, toast, actionable — comprehensive notification taxonomy |
| **Modal** | Passive, transactional, danger — clear modal intent classification |
| **Forms** | Fluid vs fixed width inputs, validation messaging patterns |

### Theming

Carbon supports 4 built-in themes: White, G10 (gray-10), G90, G100 (dark).
Themes are applied via CSS custom properties and can be scoped to regions of the page.

```scss
@use '@carbon/react/scss/themes';
@use '@carbon/react/scss/theme' with (
  $theme: themes.$g100
);
```

---

## Design-Engineer Integration

Spoke of `design-engineer`. Carbon is a reference exemplar for enterprise DS:
- Study its component taxonomy for coverage gaps in your own system
- Reference its token naming for cross-system alignment
- Use its accessibility patterns (Carbon follows WCAG 2.1 AA)
