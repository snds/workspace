---
name: fw-svelte
description: >
  Svelte framework patterns for design system implementation — Svelte 5 runes,
  snippet-based composition, reactive declarations, CSS scoping, and cross-framework
  component alignment. Use this skill whenever the conversation involves Svelte
  components in a design system context, Svelte 5 runes ($state, $derived, $effect),
  snippet slots, Svelte-specific token consumption, or ensuring parity between Svelte
  and React/Vue DS implementations. If the user mentions "Svelte", "SvelteKit",
  "runes", ".svelte files", or is working on a DS targeting Svelte — use this skill.
pinned_version: "5.55.0"
pinned_date: "2026-03-26"
changelog_url: "https://github.com/sveltejs/svelte/releases"
---

# Svelte — Framework Skill

## Version Check (run on every load)

1. Web search for `Svelte latest release`.
2. Compare against `pinned_version: 5.55.0`.
3. Flag if newer. Proceed with current knowledge.

---

## DS-Relevant Svelte 5 Patterns

### Component structure (runes)

```svelte
<script lang="ts">
  interface Props {
    variant?: 'primary' | 'secondary' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
    disabled?: boolean;
    children?: import('svelte').Snippet;
  }

  let {
    variant = 'primary',
    size = 'md',
    disabled = false,
    children,
  }: Props = $props();

  let classes = $derived(
    `btn btn--${variant} btn--${size} ${disabled ? 'btn--disabled' : ''}`
  );
</script>

<button class={classes} {disabled}>
  {@render children?.()}
</button>

<style>
  .btn { /* token-driven styles */ }
</style>
```

### Runes (Svelte 5 reactivity)

| Rune | Purpose | React equivalent |
|---|---|---|
| `$state()` | Reactive state | `useState()` |
| `$derived()` | Computed value | `useMemo()` |
| `$effect()` | Side effects | `useEffect()` |
| `$props()` | Component props | Props destructuring |
| `$bindable()` | Two-way bindable prop | Controlled + onChange |

### Snippets = Figma slots

Svelte 5 uses snippets (replacing slots from Svelte 4):

```svelte
<!-- Parent passes named content -->
<Card>
  {#snippet header()}
    <h2>Title</h2>
  {/snippet}
  {#snippet footer()}
    <button>Action</button>
  {/snippet}
  <p>Default body content</p>
</Card>

<!-- Card component -->
<script>
  let { header, footer, children }: Props = $props();
</script>
<div class="card">
  {@render header?.()}
  {@render children?.()}
  {@render footer?.()}
</div>
```

### CSS scoping (built-in)

Svelte scopes `<style>` blocks to the component automatically. For token consumption:

```svelte
<style>
  .btn {
    background: var(--color-primary);
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
  }
</style>
```

### Context API = theme provider

```typescript
// Provider
import { setContext } from 'svelte';
setContext('ds-theme', theme);

// Consumer
import { getContext } from 'svelte';
const theme = getContext('ds-theme');
```

---

## React ↔ Svelte Parity Mapping

| React | Svelte 5 | Notes |
|---|---|---|
| `props` | `$props()` | Destructured with defaults |
| `children` | `children` snippet | Via `$props()` |
| Named slots | Named snippets | `{#snippet name()}` |
| `useState` | `$state()` | |
| `useMemo` | `$derived()` | |
| `useEffect` | `$effect()` | |
| `useContext` | `getContext()` | |
| `className` | `class` attribute | Direct string or expression |

---

## Design-Engineer Integration

Spoke of `design-engineer`. Svelte DS components should:
1. Use Svelte 5 runes exclusively (not legacy reactive declarations)
2. Use snippets for composition (not legacy slots)
3. Consume tokens via CSS custom properties in scoped `<style>`
4. Keep components as thin wrappers over the DS token system
