---
name: fw-css-modules
description: >
  CSS Modules and Vanilla Extract — zero-runtime CSS strategies for design system
  components. Use this skill whenever the conversation involves CSS Modules (locally
  scoped CSS class names), Vanilla Extract (type-safe CSS-in-TypeScript), zero-runtime
  styling approaches, strict CSP environments, or choosing between utility-first
  (Tailwind) and module-based CSS for DS components. Also trigger when discussing
  CSS architecture for design systems that can't use Tailwind, need strict isolation,
  or target multiple frameworks. If the user mentions "CSS Modules", ".module.css",
  "Vanilla Extract", "@vanilla-extract/css", "zero-runtime CSS", or "scoped CSS" —
  use this skill.
pinned_version: "vanilla-extract@1.20.0"
pinned_date: "2026-03-26"
changelog_url: "https://github.com/vanilla-extract-css/vanilla-extract/releases"
---

# CSS Modules & Vanilla Extract — Framework Skill

## Version Check (run on every load)

1. Web search for `vanilla-extract css latest release` (CSS Modules is spec-level, no version).
2. Compare against `pinned_version: vanilla-extract@1.20.0`.
3. Flag if newer. Proceed.

---

## CSS Modules

### Core concept
Locally scoped CSS class names. Each `.module.css` file generates unique class names at
build time, preventing style collisions.

```css
/* Button.module.css */
.root {
  background: var(--color-primary);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
}
.disabled { opacity: 0.5; }
```

```tsx
import styles from './Button.module.css';

<button className={`${styles.root} ${disabled ? styles.disabled : ''}`}>
  {children}
</button>
```

### DS advantages
- **Zero runtime** — no JS bundle cost for styles
- **Strict CSP** — no inline styles injected
- **Framework-agnostic** — works with React, Vue, Svelte, Angular
- **Token consumption** — uses CSS custom properties (same as any CSS)

### DS disadvantages
- No type safety for class names
- No built-in variant/compound variant management
- Manual composition of conditional classes

---

## Vanilla Extract

### Core concept
Type-safe CSS-in-TypeScript with zero runtime. Styles are authored in `.css.ts` files and
compiled to static CSS at build time.

```typescript
// Button.css.ts
import { style, styleVariants } from '@vanilla-extract/css';
import { recipe } from '@vanilla-extract/recipes';

export const button = recipe({
  base: {
    borderRadius: vars.radius.md,
    fontWeight: 600,
    transition: 'all 200ms ease',
  },
  variants: {
    variant: {
      primary: { background: vars.color.primary, color: vars.color.onPrimary },
      secondary: { background: vars.color.secondary, color: vars.color.onSecondary },
      ghost: { background: 'transparent', color: vars.color.primary },
    },
    size: {
      sm: { padding: `${vars.spacing.xs} ${vars.spacing.sm}`, fontSize: vars.fontSize.sm },
      md: { padding: `${vars.spacing.sm} ${vars.spacing.md}`, fontSize: vars.fontSize.base },
      lg: { padding: `${vars.spacing.md} ${vars.spacing.lg}`, fontSize: vars.fontSize.lg },
    },
  },
  defaultVariants: { variant: 'primary', size: 'md' },
});
```

### Key packages

| Package | Purpose |
|---|---|
| `@vanilla-extract/css` | Core — `style()`, `globalStyle()`, `createTheme()` |
| `@vanilla-extract/recipes` | CVA-like variant management |
| `@vanilla-extract/sprinkles` | Tailwind-like utility generation (type-safe) |
| `@vanilla-extract/dynamic` | Runtime theme switching |

### Theme contract (design tokens)

```typescript
import { createThemeContract, createTheme } from '@vanilla-extract/css';

// Define the shape (contract)
export const vars = createThemeContract({
  color: { primary: null, onPrimary: null, surface: null },
  spacing: { xs: null, sm: null, md: null, lg: null },
  radius: { sm: null, md: null, lg: null },
});

// Implement themes
export const lightTheme = createTheme(vars, {
  color: { primary: '#0050f0', onPrimary: '#ffffff', surface: '#fafafa' },
  spacing: { xs: '0.25rem', sm: '0.5rem', md: '1rem', lg: '1.5rem' },
  radius: { sm: '0.375rem', md: '0.5rem', lg: '0.75rem' },
});

export const darkTheme = createTheme(vars, {
  color: { primary: '#3d8aff', onPrimary: '#0d1520', surface: '#111111' },
  // ... same shape, different values
});
```

### DS advantages
- **Full type safety** — TypeScript errors if token doesn't exist
- **Zero runtime** — compiles to static CSS
- **Theme contracts** — enforce token shape across themes
- **Recipes** — built-in CVA-equivalent for variants

---

## When to Use Which

| Scenario | Recommendation |
|---|---|
| Tailwind-based project | Use Tailwind (not this skill) |
| Type-safe tokens required | Vanilla Extract |
| Strict CSP, no tooling | CSS Modules |
| Multi-framework DS | CSS Modules (most portable) |
| Complex variant logic | Vanilla Extract recipes |
| Legacy codebase integration | CSS Modules |

---

## Design-Engineer Integration

Spoke of `design-engineer`. Use alongside:
- **fw-radix-colors** — Radix Colors as CSS custom properties consumed by CSS Modules
- **fw-radix-primitives** — Headless components styled via CSS Modules or Vanilla Extract
