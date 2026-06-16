---
name: fw-tailwind-css
description: >
  Tailwind CSS utility-first framework — v4 CSS-first configuration, @theme tokens,
  Oxide engine, container queries, dark mode strategies, and design token integration.
  Use this skill whenever the conversation involves Tailwind CSS configuration, the
  @theme directive, CSS-first token definition, Tailwind v3→v4 migration, custom
  utility creation, dark mode setup, or integrating design tokens (DTCG) with Tailwind.
  Also trigger when generating Tailwind-based theme files, discussing @apply vs utility
  patterns, or creating design system foundations that target Tailwind. If the user
  mentions "Tailwind", "tw", "@theme", utility classes, or is working with a project
  that uses Tailwind — use this skill.
pinned_version: "4.2.2"
pinned_date: "2026-03-26"
changelog_url: "https://tailwindcss.com/blog"
aliases: [fw-tailwind-css]
tier: spoke
domain: engineering
hub: lead-frontend-engineer
prerequisites: [lead-frontend-engineer]
spec_version: "2.0"
---

# Tailwind CSS — Framework Skill

## Version Check (run on every load)

Before beginning any Tailwind-related work:

1. **Web search** for `Tailwind CSS latest release` or check the blog URL above.
2. **Compare** against `pinned_version: 4.2.2`.
3. If newer, **flag** to the user with key changes. Proceed with current knowledge.
4. If current, proceed silently.

---

## Core Paradigm: CSS-First Configuration

Tailwind v4 fundamentally shifts from JavaScript config to CSS-native configuration.
The `tailwind.config.js` file is no longer required for most projects.

### v4 entry point

```css
@import "tailwindcss";

@theme {
  --color-primary: oklch(0.6 0.2 250);
  --spacing-lg: 1.5rem;
  --font-sans: "Inter", system-ui, sans-serif;
}
```

This single CSS import replaces `@tailwind base; @tailwind components; @tailwind utilities;`
from v3.

---

## @theme Directive

The `@theme` block declares design tokens that become both CSS variables and utility classes.

### Token categories

```css
@theme {
  /* Colors — generates bg-*, text-*, border-*, etc. */
  --color-primary: oklch(0.6 0.2 250);
  --color-surface: hsl(0, 0%, 100%);
  --color-on-surface: hsl(0, 0%, 10%);

  /* Spacing — generates p-*, m-*, gap-*, w-*, h-* */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Typography */
  --font-sans: "Inter", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", monospace;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;

  /* Border radius */
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);

  /* Animation */
  --duration-fast: 100ms;
  --duration-base: 200ms;
  --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);

  /* Breakpoints */
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
}
```

### Overriding entire namespaces

To replace all default colors with only your own:

```css
@theme {
  --color-*: initial;
  --color-white: #fff;
  --color-primary: oklch(0.6 0.2 250);
  --color-surface: oklch(0.98 0.005 250);
}
```

---

## Oxide Engine

Built in Rust. Replaces the PostCSS-based v3 engine.

- **Full builds**: 3.5–5× faster than v3
- **Incremental builds**: Up to 100× faster (microseconds)
- **Built-in**: @import handling, vendor prefixing, CSS nesting — no PostCSS/autoprefixer needed
- **Only dependency**: Lightning CSS

---

## Container Queries (First-Class)

No plugin needed in v4.

```html
<div class="@container">
  <div class="text-sm @sm:text-base @md:text-lg @lg:grid @lg:grid-cols-2">
    Responsive to container width
  </div>
</div>
```

Named containers: `@container/card` → `@md/card:flex`.

---

## Dark Mode Strategies

### Strategy 1: Media query (default)

```css
/* Automatic — no configuration needed */
/* Uses @media (prefers-color-scheme: dark) */
```

### Strategy 2: Class-based (manual toggle)

```css
@import "tailwindcss";
@custom-variant dark (&:is(.dark *));
```

### Strategy 3: Data attribute

```css
@import "tailwindcss";
@custom-variant dark (&:where([data-theme=dark], [data-theme=dark] *));
```

### Multi-theme support

```css
@layer base {
  .dark { --color-surface: oklch(0.15 0.01 250); }
  .theme-amber { --color-primary: oklch(0.7 0.18 80); }
  .theme-ocean { --color-primary: oklch(0.6 0.15 230); }
}
```

---

## Plugin System (v4)

JavaScript plugins replaced by CSS directives:

| v3 JS API | v4 CSS equivalent |
|---|---|
| `addUtilities()` | `@utility name { ... }` |
| `addComponents()` | `@layer components { ... }` |
| `addVariant()` | `@custom-variant name (selector)` |
| `addBase()` | `@layer base { ... }` |
| `theme()` function | CSS variables from `@theme` |

### Custom utility

```css
@utility shadow-outline {
  box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.5);
}
```

### Custom variant

```css
@custom-variant hocus (&:hover, &:focus);
```

---

## Design Token Integration (DTCG → Tailwind)

### Bridge pattern

```json
// tokens.json (DTCG format)
{
  "color": {
    "primary": { "$value": "#3f3cbb", "$type": "color" }
  },
  "spacing": {
    "md": { "$value": "1rem", "$type": "dimension" }
  }
}
```

Use Style Dictionary or a build script to generate:

```css
@theme {
  --color-primary: #3f3cbb;
  --spacing-md: 1rem;
}
```

### 3-tier token mapping

```css
/* Tier 1: Primitives (raw values) */
@theme {
  --primitive-blue-500: oklch(0.6 0.2 250);
  --primitive-gray-100: oklch(0.96 0.005 250);
}

/* Tier 2: Semantic (purpose-driven) */
@layer base {
  :root {
    --color-primary: var(--primitive-blue-500);
    --color-surface: var(--primitive-gray-100);
  }
}

/* Tier 3: Component (scoped overrides — use sparingly) */
.button {
  background-color: var(--color-primary);
}
```

---

## v3 → v4 Migration Quick Reference

| Change | v3 | v4 |
|---|---|---|
| Entry | `@tailwind base/components/utilities` | `@import "tailwindcss"` |
| Config | `tailwind.config.js` | `@theme { }` in CSS |
| Gradients | `bg-gradient-to-r` | `bg-linear-to-r` |
| Flex utils | `flex-shrink-0` | `shrink-0` |
| Dark mode | `darkMode: 'class'` in config | `@custom-variant dark (...)` |
| Plugins | JS `plugin()` | `@utility`, `@custom-variant` |
| Border color default | `gray-200` | `currentColor` |
| Ring width default | `3px` | `1px` |

---

## @apply Status

Not deprecated, but discouraged for heavy use. Prefer:

1. **Utility classes in HTML** (default approach)
2. **CSS variables with explicit CSS** for component abstractions
3. **@apply** only for simple utility combinations in `@layer components`

---

## Reference Spokes

| Spoke | When to load |
|---|---|
| `references/v4-migration-guide.md` | Full v3→v4 migration with before/after examples |
| `references/token-generation.md` | DTCG → Tailwind @theme build scripts |

---

## Design-Engineer Integration

This skill is a spoke of `design-engineer` and `ds-generation-pipeline`.
Pair with:
- **fw-shadcn** — Components consuming Tailwind tokens
- **fw-radix-colors** — Color primitive system feeding Tailwind
- **fw-radix-primitives** — Headless behaviors styled by Tailwind
