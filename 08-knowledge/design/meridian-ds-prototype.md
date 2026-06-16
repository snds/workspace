---
tags: [design-system, meridian, prototype, react, tokens, ARIA, components]
created: 2026-04-28
updated: 2026-04-28
status: stable
confidence: high
sources: [artifact-registry 2026-03-08]
related_skills: [design-engineer, fe-component-architecture, fe-accessibility]
related_projects: []
---

# Meridian Design System Prototype — Accumulated Learnings

What exists in the Meridian DS prototype (as of 2026-03-08) and what decisions were made during its build. Meridian is a personal/exploratory design system — not Centric's system.

---

## What Was Built

Three prototype files plus supporting specs and audits, all in `04-artifacts/active/files/meridian-ds/`:

| File | Purpose | Size |
|------|---------|------|
| `app-shell-prototype-v0.1.jsx` | Full app shell — 7 views, search, modals, responsive | ~7,500 lines |
| `setup-wizard-prototype-v0.1.jsx` | 6-step onboarding wizard | ~1,846 lines |
| `meridian-design-system-v0.1.jsx` | Foundation reference component library + theme gallery | ~1,175 lines |
| `theme-tokens.css` | CSS custom properties for dual-theme (dark/light) | ~744 lines |
| `tailwind.config.js` | Tailwind consuming CSS custom properties | ~276 lines |

---

## Token Architecture

**Three-tier token system implemented:**
- **Primitives:** `brand` (teal 50–950), `neutral` (slate 0–950)
- **Semantic tokens:** `surface`, `border`, `text`, `interactive`, `status`, `provenance`, `overlay`, `quality`, `brand3p`
- **Component tokens:** Expressed as Tailwind utility classes that resolve via CSS custom properties

**Surface context system:** `surfaceCtx()` function returns context-aware color values for 9 distinct surface contexts:
- `default`, `accentSubtle`, `accentSolid`, `brandSubtle`, `brandSolid`, `grapeSubtle`, `grapeSolid`, `successSubtle`, `errorSubtle`, `warningSubtle`

This system allows any component to adapt its colors based on the surface it's rendered on. Critical for card-in-card nesting and tinted section backgrounds.

**Theme implementation:** CSS custom properties in `:root` (dark default) + `[data-theme="light"]` overrides + `@media (prefers-color-scheme: light)` system fallback.

---

## Component State Coverage (What Was Specified)

From the DDR (Design Decision Record) pass in DS-2026-001 through DS-2026-009:

| Component | States covered |
|-----------|---------------|
| Button | hover, active, disabled, loading |
| Input | error, disabled |
| Select | error, disabled |
| Card | selected |
| SettingToggle | disabled |
| NavItem | disabled |
| Toggle (setup wizard) | disabled |

**Loading state implementation:** CSS `@keyframes` spinner injected inline — no external animation library.

---

## ARIA Coverage

All 14 interactive components in the app-shell prototype received a full ARIA pass (DS-2026-007):
- `role=` attributes where native semantics don't apply
- `aria-*` properties (aria-expanded, aria-modal, aria-labelledby, aria-checked, etc.)
- Keyboard handlers (Escape for modals, Enter/Space for buttons, roving tabindex for nav)
- Focus management (focus trap in ModalShell, focus ring via injected CSS)

Notable patterns:
- **SegmentedControl:** `role=tablist/tab` + `aria-selected` + roving tabIndex
- **SearchBar:** `aria-autocomplete=list` + `aria-expanded` + ⌘K shortcut
- **ModalShell:** `role=dialog` + `aria-modal` + `aria-labelledby` + Escape key + focus trap + exit animation
- **Toast:** `role=alert/status` + `aria-live` + `aria-atomic`

---

## Badge Scale Decision

**Decision (DS-2026-005):** Normalized to 5-tier badge scale (`xs/sm/md/lg/xl`) + 2-tier chip scale (`md/lg`). Three components were explicitly exempted from the badge scale with annotation (RatingBadge, ProfileSourceBadge, and one other).

**Why a separate chip tier:** Chips have interactive affordances (selection, dismissal) that badges don't. Treating them as badges creates incorrect touch target and density expectations.

---

## WCAG Audit Results

- **96 color pairings tested**
- **78 pass** AA
- **8 failures** — all remediated (see `wcag-audit-v0.1.md`)
- **6 intentionally substandard** — documented exceptions (decorative elements, disabled states with adjacent labels)
- **Key fix:** `text.tertiary` dark mode contrast bumped from `#78859a` → `#8892a4` (4.6:1 on raised surfaces)

**Lesson:** Run the WCAG audit before finalizing dark/light token pairs, not after. Fixing contrast values late requires touching both the CSS custom properties and verifying no visual regressions across all 9 surface contexts.

---

## Responsive Strategy

`useResponsive()` / `useRsp()` hook consuming `ResponsiveContext` with `BREAKPOINTS` config. Bottom tab bar for mobile-only navigation. The app shell uses conditional rendering at breakpoints rather than CSS-only responsive design — this was necessary because the navigation structure (sidebar vs. bottom tabs) is structurally different, not just visually different.
