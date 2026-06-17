---
name: visual-qa-ui-design
description: >
  UI design visual QA specialist. Use this skill for reviewing: screens and
  screen compositions, UI component visual quality, component library and design
  system adherence, spacing and alignment, grid and column systems, responsive
  layout behavior, interactive states (hover, active, focus, disabled, selected,
  error), typography in interface context (labels, buttons, headings, body,
  micro-copy), iconography in UI context (icon sizing, placement, optical
  alignment within components), color usage and token application, elevation
  and shadow systems, border-radius and shape language consistency, motion and
  transition quality, dark mode and color scheme variants, platform-specific
  conventions (iOS, Android, web, desktop), design system component deviation
  review, or any pixel-level screen quality evaluation. Sub-specialties include:
  typography QA (interface context), iconography QA (UI context), component
  state coverage, design token compliance, dark mode QA. Spoke of lead-visual-qa.
aliases: [visual-qa-ui-design]
tier: cross-cutting
domain: quality
hub: lead-visual-qa
spec_version: "2.0"
---

# Visual QA — UI Design

UI design quality assurance specialist. Evaluates the pixel-level quality of
screen-based interfaces: components, spacing, typography, iconography, states,
color, and design system compliance. Spoke of `lead-visual-qa`.

---

## Domain Boundary

This skill owns the **interface layer evaluation lens**.

- **Navigation flows and experience architecture** → `visual-qa-ux-design`
- **Whether users can complete tasks efficiently** → `visual-qa-usability`
- **Brand graphic craft, print, editorial** → `visual-qa-graphic-design`
- **WCAG compliance and inclusion criteria** → `visual-qa-accessibility`

Typography and iconography QA overlap with `visual-qa-graphic-design`. When
evaluating typography in a UI context (label alignment, component-level hierarchy,
responsive type scaling), apply the specific UI rules in this skill. When evaluating
type as a brand or editorial element, also route to `visual-qa-graphic-design`.

### Measurement companion: `visual-qa-toolkit`

This spoke defines the evaluation lens. For dimensions that can be measured
rather than asserted, invoke `visual-qa-toolkit`:

| This skill evaluates | Toolkit script |
|---|---|
| Spacing grouping and rhythm | `qa_spacing` — gap vs. configured scale |
| Edge alignment across elements | `qa_alignment` — cluster median vs. tolerance |
| Color token compliance | `qa_color_extraction` — sampled Δe vs. a palette JSON |
| Typography scale adherence | `qa_typography` — cap-height vs. type scale |
| Component state coverage | `qa_state_comparison` — pairwise SSIM between states |
| Design-vs-implementation drift | `qa_visual_diff` — SSIM + pixel diff |

Use the spoke for the heuristic pass (does this read well, are states complete,
is hierarchy working). Use the toolkit when a specific measurement would be more
credible than an assertion, or when a pre-handoff audit warrants numbers.

The toolkit is input-driven and project-agnostic. It accepts paths (screenshot,
palette JSON, reference image, folder of states) that the user provides; never
hunt the filesystem for project-specific artifacts. See `visual-qa-toolkit/SKILL.md`
for invocation details.

---

## Spacing and Alignment QA

### Grid and Column System

- **Column gutters**: Are gutters consistently sized throughout the layout?
- **Margin alignment**: Do elements align to the column grid, or float independently?
- **Baseline grid**: Do text elements sit on a consistent baseline increment
  (8px, 4px, or type-specific value)?
- **Content width**: Is content constrained to a max-width on large screens, or
  does it stretch uncomfortably across the full viewport?

### Component-Level Spacing

Most design systems use a spacing scale (multiples of 4px or 8px). Evaluate:

| Spacing Relationship | Expected Behavior | Common Failure |
|----------------------|------------------|----------------|
| Label → field | Tight binding (4–8px) — label belongs to the field it describes | Label too far from field — ambiguous ownership |
| Field → next field | Clear group separation (16–24px) — fields in a group are closer to each other than to other groups | Equal spacing between all elements — no grouping signal |
| Section → section | Larger gap (32–48px) | Sections bleed into each other |
| Element → container edge (padding) | Consistent per container type | Inconsistent padding: wider on top than sides, for example |

### Optical Alignment vs Mathematical Alignment

- **Icons in buttons**: Mathematically centered icons often appear low because text caps are shorter than descenders. Icons should align to visual cap height, not mathematical center.
- **Type in pill/badge**: Text in a rounded container usually needs +1–2px top padding to feel optically centered (baseline sits lower than cap height center)
- **Vertically stacked text**: The gap between two lines of text appears larger than the same gap between text and a non-text element — compensate when mixing

---

## Typography QA (Interface Context)

### Component Typography Hierarchy

For screens, the hierarchy must function at the component level before the page level.

| Component | Type Treatment | Common Issues |
|-----------|---------------|---------------|
| **Button label** | Medium/semibold, caps-height aligned, 13–16px | Too small at touch targets; all-caps without tracking; mismatched with surrounding text scale |
| **Form label** | Regular or medium, 12–14px, close to field | Same size as body text — no differentiation; truncated on narrow viewports |
| **Input text** | Regular, 16px minimum on mobile (prevents iOS zoom) | Below 16px on mobile fields — system zooms in |
| **Tooltip / popover** | Regular, 12–13px, max-width ~280px | Too small; more than 2–3 lines (should be microcopy, not documentation) |
| **Table cell** | Regular, 13–14px, left-aligned for strings, right-aligned for numbers | Center-aligned numbers (hard to scan); truncation with no overflow strategy |
| **Navigation label** | Medium or regular, 11–13px (tab bar) to 14–16px (main nav) | Same weight as page titles — no hierarchy between nav and content |

### Responsive Typography

- At mobile breakpoints, does display text scale down appropriately?
- Does line length stay within 45–75 characters for body text at all breakpoints?
- Does the type scale step correctly (not just shrink uniformly)?
- Does type never become the limiting factor for a minimum viewport width?

### Iconography QA (UI Context)

When reviewing icons as UI elements within an interface:

**Sizing and Optical Alignment**
- Icons used alongside text should align to the text's visual cap height, not
  its mathematical center line
- Icon size should be proportional to accompanying text: 16px icon with 14px text,
  20px icon with 16–18px text, 24px icon with 20–22px text (approximate)
- Decorative icons (no label) should not be smaller than 16×16px for interactive
  targets; non-interactive decorative icons can be smaller

**Placement and Density**
- Icons in a list or grid must have consistent spacing between icon and label
- In a toolbar or action bar: optical spacing between icons should feel even —
  icons with more visual mass may need slightly more surrounding space
- Icons should never bleed to the edge of a touch target — 4–8px padding minimum

**Icon + Label Alignment**
- The icon center (optical, not geometric) should align with the label baseline
  or cap height — test with a specific character like "A" vs. the icon edge
- When icons of different visual weight appear in the same row, they may need
  individual optical nudges to appear aligned

**Interactive Icon States**
- Hover/active state for icon-only buttons must be visually clear (background
  fill, border, or color shift) — icons without a containing button shape are
  easy to make feel unresponsive
- Disabled icon state must be distinguishable from the enabled state — typically
  lower opacity (40–60%) or a muted color variant, never the same as active

---

## Component State Coverage QA

All interactive components require a complete visual state set. Missing states
cause implementation failures and inconsistent perceived quality.

### Mandatory State Matrix

| Component | Required States |
|-----------|----------------|
| **Button** | Default, hover, active/pressed, disabled, loading (if async action) |
| **Input / Text field** | Default (empty), focused, filled, error, disabled, read-only |
| **Checkbox** | Unchecked, checked, indeterminate, disabled (each of the above) |
| **Radio** | Unselected, selected, disabled |
| **Toggle/Switch** | Off, on, disabled-off, disabled-on |
| **Dropdown/Select** | Closed, open, option-hover, selected, disabled |
| **Link** | Default, hover, visited, active, focus-visible |
| **Card** | Default, hover, selected, disabled (where applicable) |
| **Table row** | Default, hover, selected, disabled (where applicable) |

Flag any component that is missing states from this matrix. Missing disabled
states are the most common omission and create problematic patterns in implementation.

---

## Color and Design Token QA

### Token Compliance

- Are semantic tokens used consistently? (e.g., `color-bg-surface` not raw `#FFFFFF`)
- Are interactive elements using the correct interactive token chain
  (e.g., `color-interactive-default` → `color-interactive-hover` → `color-interactive-active`)?
- Are status colors (error, warning, success, info) from the semantic color layer,
  not hardcoded?

### Dark Mode / Color Scheme Variants

When evaluating a dark mode or alternate color scheme:
- Do all semantic token assignments still produce appropriate visual results?
  (e.g., a shadow that adds depth in light mode may disappear or reverse in dark mode)
- Are elevation differences still visually detectable? (In dark mode, elevation
  is often expressed by lighter surface colors rather than shadows)
- Are all text / background pairs still meeting contrast requirements?
- Do decorative elements (illustrations, images) adapt or become color scheme issues?

### Elevation and Shadow Consistency

- Are shadow values consistent with the elevation model? (More elevated = larger, softer shadow)
- Are shadows in the correct direction? (Light source is typically top/top-left)
- In dark mode: are shadows replaced with appropriate surface lightness steps?

---

## Shape Language and Radius QA

- Is the border-radius consistent across component tiers?
  (small components = tighter radius; cards/modals = larger radius; full-pill = inputs/tags/buttons?)
- Are any components using unauthorized radius values (arbitrary, not from the scale)?
- Does the radius scale create a coherent shape language — do all components feel
  like they belong to the same design system?
- Are there rounding inconsistencies between native platform components and custom ones?

---

## QA Checklist — UI Design

**Spacing and Alignment:**
- [ ] Elements align to the grid system (column and baseline)
- [ ] Spacing relationships create visual grouping signals (close = related, far = separate)
- [ ] Optical corrections applied where mathematical centering would appear wrong
- [ ] Padding is consistent within container types

**Typography:**
- [ ] Component hierarchy is readable (buttons vs. labels vs. body)
- [ ] Mobile input fields are 16px minimum
- [ ] Responsive type scaling is deliberate, not uniform shrinking
- [ ] Line length stays within 45–75 characters at all breakpoints

**Iconography:**
- [ ] Icons aligned to text cap height, not mathematical center
- [ ] Icons sized proportionally to accompanying text
- [ ] Icon touch targets have minimum 16×16px icon + adequate padding
- [ ] Interactive icon states (hover, active, disabled) are visually distinct

**Component States:**
- [ ] All interactive components have the full mandatory state matrix
- [ ] No missing disabled states
- [ ] Loading/async states are designed where the component triggers async actions
- [ ] Error states are visually distinct and include recovery affordance

**Color and Tokens:**
- [ ] Semantic tokens used throughout (no hardcoded values)
- [ ] Dark mode / alternate scheme variants verified
- [ ] Elevation model is visually coherent (shadows or surface lightness)

**Shape Language:**
- [ ] Border-radius follows the design system scale
- [ ] Radius is consistent across equivalent component tiers
- [ ] All components feel like they share the same shape language

## Related
- hub → [[lead-visual-qa]]
- peer ↔ [[vis-segmentation]]
