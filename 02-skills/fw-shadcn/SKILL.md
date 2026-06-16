---
name: fw-shadcn
description: >
  shadcn/ui component library patterns, CLI, registry, theming, and customization.
  Use this skill whenever the conversation involves shadcn/ui components, the shadcn CLI
  (npx shadcn add, npx shadcn create), components.json configuration, shadcn theming
  with CSS variables, the shadcn registry system, or building/extending components that
  use the shadcn copy-paste model. Also trigger when discussing component architecture
  that combines Radix UI + Tailwind CSS through shadcn, or when generating design system
  artifacts targeting a shadcn-based stack. If the user mentions "shadcn", "shadcn/ui",
  or is working with a Next.js/Vite project that uses the shadcn component model — use
  this skill.
pinned_version: "4.0.0 (CLI v4)"
pinned_date: "2026-03-26"
changelog_url: "https://ui.shadcn.com/docs/changelog"
aliases: [fw-shadcn]
tier: spoke
domain: engineering
hub: lead-frontend-engineer
prerequisites: [lead-frontend-engineer]
spec_version: "2.0"
---

# shadcn/ui — Framework Skill

## Version Check (run on every load)

Before beginning any shadcn-related work, verify the skill's reference data is current:

1. **Web search** for `shadcn/ui changelog latest` or fetch the changelog URL above.
2. **Compare** the latest version against `pinned_version: 4.0.0 (CLI v4)`.
3. If a newer version exists, **flag it** to the user:
   > "shadcn/ui has released [version] since this skill was last updated. Key changes: [summary]. Proceeding with current knowledge — flag if you hit anything unfamiliar."
4. If the version matches, proceed silently.

---

## Core Mental Model

shadcn/ui is not an npm dependency — it's a component authoring philosophy. Components are
copied into your codebase via CLI, giving you full ownership. The architecture is a three-layer
stack:

```
┌─────────────────────────────────────────┐
│  shadcn/ui — Composed, styled components │
├─────────────────────────────────────────┤
│  Tailwind CSS — Utility-first styling    │
├─────────────────────────────────────────┤
│  Radix UI / Base UI — Headless behavior  │
└─────────────────────────────────────────┘
```

Every decision should account for all three layers. When the user asks about a shadcn
component, consider the Radix primitive underneath and the Tailwind tokens driving its
appearance.

---

## CLI Reference

### Core commands

| Command | Purpose |
|---|---|
| `npx shadcn@latest init` | Initialize project config (`components.json`) |
| `npx shadcn@latest add [name]` | Copy a component into the project |
| `npx shadcn@latest add --all` | Add every available component |
| `npx shadcn@latest create` | Interactive builder (styles, primitives, RTL) |
| `npx shadcn@latest diff [path]` | Show differences between local and registry |

### Useful flags

- `--dry-run` — Preview changes without writing files
- `--diff [path]` — Compare local component against registry
- `--view [path]` — Inspect registry payload
- `--base-ui` — Use Base UI primitives instead of Radix
- `--rtl` — Enable RTL support
- `-o, --overwrite` — Overwrite existing files
- `-s, --silent` — Suppress output

### CLI v4 (March 2026) additions

- **shadcn/skills** — AI-friendly context bundles for coding agents
- **Design System Presets** — Single code string packing colors, theme, icons, fonts, radius
- **First-class fonts** — Install and configure fonts like components
- **Expanded framework support** — Next.js, Vite, TanStack Start, React Router, Astro, Laravel

---

## components.json Schema

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "app/globals.css"
  },
  "aliases": {
    "@/components": "./components",
    "@/lib/utils": "./lib/utils"
  }
}
```

**Key fields:**
- **style**: Visual preset — `"default"`, `"vega"`, `"nova"`, `"maia"`, `"lyra"`, `"mira"`
- **rsc**: React Server Components support
- **tsx**: TypeScript output
- **tailwind.css**: Path to global CSS (where theme tokens live)
- **aliases**: Path aliases for component resolution

---

## Theming System

### CSS variable token architecture

shadcn uses semantic CSS custom properties. Every token has a background/foreground pair:

```css
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0.02 250);
  --primary: oklch(0.205 0.02 265);
  --primary-foreground: oklch(0.985 0 0);
  --secondary: oklch(0.97 0.005 250);
  --secondary-foreground: oklch(0.205 0.02 265);
  --destructive: oklch(0.577 0.245 27);
  --destructive-foreground: oklch(0.985 0 0);
  --muted: oklch(0.97 0.005 250);
  --muted-foreground: oklch(0.556 0.02 250);
  --accent: oklch(0.97 0.005 250);
  --accent-foreground: oklch(0.205 0.02 265);
  --card: oklch(1 0 0);
  --card-foreground: oklch(0.145 0.02 250);
  --popover: oklch(1 0 0);
  --popover-foreground: oklch(0.145 0.02 250);
  --border: oklch(0.922 0.005 250);
  --input: oklch(0.922 0.005 250);
  --ring: oklch(0.708 0.02 265);
}

.dark {
  /* Same variable names, different values */
}
```

### Color format

OKLCH is the default: `oklch(lightness chroma hue)` where lightness is 0–1, chroma is 0+,
hue is 0–360°.

### Mapping to Tailwind

Tokens are exposed via `@theme` in Tailwind v4:

```css
@theme {
  --color-primary: oklch(var(--primary));
  --color-primary-foreground: oklch(var(--primary-foreground));
}
```

### Dark mode

Applied via `.dark` class on root element. All variables are redefined under `.dark` selector.
No media query required — manual control via class toggle.

---

## Registry System

The registry is shadcn's distribution mechanism for components, hooks, pages, and utilities.

### registry-item.json schema

```json
{
  "name": "my-component",
  "type": "components:ui",
  "files": [
    {
      "path": "my-component.tsx",
      "type": "component",
      "target": "components/ui/my-component.tsx"
    }
  ],
  "dependencies": ["class-variance-authority"],
  "registryDependencies": ["button"],
  "cssVars": {
    "light": { "--custom-primary": "220 90% 56%" },
    "dark": { "--custom-primary": "220 50% 40%" }
  }
}
```

**Supported item types**: `components:ui`, `utils`, `hooks`, `pages`, `fonts`, `config`, `rules`

### Custom registry hosting

Use the [registry-template](https://github.com/shadcn-ui/registry-template) repo. Reference
your registry URL in `components.json` aliases.

---

## Component Customization Patterns

### 1. CVA variant extension

Add variants to `class-variance-authority` definitions:

```tsx
const buttonVariants = cva("inline-flex items-center justify-center gap-2", {
  variants: {
    variant: {
      default: "bg-primary text-primary-foreground",
      outline: "border border-input bg-background",
      ghost: "hover:bg-accent hover:text-accent-foreground",
      // Custom addition
      brand: "bg-brand text-brand-foreground",
    },
  },
});
```

### 2. Composition (wrapper components)

```tsx
export function PrimaryButton({ children, ...props }) {
  return <Button variant="default" size="lg" {...props}>{children}</Button>;
}
```

### 3. CSS variable token overrides

Change tokens globally — every component updates:

```css
:root {
  --primary: oklch(0.6 0.2 250);
}
```

### 4. Git-tracked baseline

Always commit the unmodified shadcn component first, then make your customizations in a
separate commit. `git diff` becomes your change tracker.

---

## Accessibility (inherited from Radix)

shadcn inherits all a11y patterns from Radix UI primitives:

- **Focus management**: Auto-trap in modals, return on close
- **Keyboard nav**: Arrow keys for menus/tabs, Tab for focus order, Enter/Space for activation
- **ARIA**: Automatic roles, states, labels where structure supports it
- **Semantic HTML**: Proper heading hierarchy, button semantics, landmarks

**Your responsibility**: Provide meaningful labels, ensure color isn't the sole indicator,
test keyboard + screen reader flows.

---

## Visual Styles (December 2025+)

| Style | Character | Best for |
|---|---|---|
| **Vega** | Classic shadcn default | General-purpose |
| **Nova** | Compact, reduced padding | Dense dashboards |
| **Maia** | Soft, rounded, generous | Consumer-facing |
| **Lyra** | Boxy, sharp | Monospace / dev tools |
| **Mira** | Tight spacing | Data-heavy interfaces |

Select during init: `npx shadcn create` → choose style interactively.

---

## Primitive Layer Choice (2026)

shadcn now supports both Radix UI and Base UI as headless primitive layers:

| | Radix UI | Base UI |
|---|---|---|
| **Vendor** | WorkOS | MUI |
| **Bundle** | Larger | Smaller |
| **API style** | Compound components | Hook-based |
| **Init flag** | Default | `--base-ui` |

Choose during `npx shadcn@latest init`. Every component exists for both.

---

## Reference Spokes

| Spoke | When to load |
|---|---|
| `references/theming-deep-dive.md` | Custom theme generation, multi-brand theming, advanced OKLCH manipulation |
| `references/registry-authoring.md` | Building and hosting custom component registries |

---

## Design-Engineer Integration

This skill is a spoke of `design-engineer`. When loaded alongside:
- **fw-tailwind-css** — Covers the styling layer (tokens, @theme, utilities)
- **fw-radix-colors** — Covers the color primitive system (12-step scales, dark mode)
- **fw-radix-primitives** — Covers the headless behavior layer (Dialog, Popover, Tabs)

The full stack: Radix Colors → Radix Primitives → Tailwind CSS → shadcn/ui.

## Related
- hub → [[lead-frontend-engineer]]
