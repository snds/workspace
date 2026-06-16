---
name: fw-vue
description: >
  Vue.js framework patterns for design system implementation — Composition API,
  SFC structure, reactive state, provide/inject for theming, and cross-framework
  component alignment with React. Use this skill whenever the conversation involves
  Vue.js components in a design system context, Vue 3 Composition API patterns,
  SFC (Single File Component) architecture, Vue-specific token consumption,
  provide/inject for theme propagation, or ensuring parity between Vue and React
  implementations of design system components. If the user mentions "Vue",
  "Vue 3", ".vue files", Composition API, or is working on a DS that targets
  Vue — use this skill.
pinned_version: "3.5.30"
pinned_date: "2026-03-26"
changelog_url: "https://github.com/vuejs/core/releases"
---

# Vue.js — Framework Skill

## Version Check (run on every load)

1. Web search for `Vue.js latest release`.
2. Compare against `pinned_version: 3.5.30` (v3.6 beta in progress).
3. Flag if newer stable version. Proceed with current knowledge.

---

## DS-Relevant Vue Patterns

### Component structure (SFC)

```vue
<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
});

const classes = computed(() => [
  'btn',
  `btn--${props.variant}`,
  `btn--${props.size}`,
  { 'btn--disabled': props.disabled },
]);
</script>

<template>
  <button :class="classes" :disabled="disabled">
    <slot />
  </button>
</template>

<style scoped>
.btn { /* token-driven styles */ }
</style>
```

### Token consumption via provide/inject

```typescript
// Theme provider
import { provide, reactive } from 'vue';
const theme = reactive({
  colors: { primary: 'var(--color-primary)' },
  spacing: { md: 'var(--spacing-md)' },
});
provide('ds-theme', theme);

// Component consumer
import { inject } from 'vue';
const theme = inject('ds-theme');
```

### Slots = Figma slots

Vue's named slots map directly to Figma slot concepts:

```vue
<template>
  <div class="card">
    <slot name="header" />
    <slot />  <!-- default slot -->
    <slot name="footer" />
  </div>
</template>
```

### v-bind in CSS (scoped token binding)

```vue
<style scoped>
.btn {
  background-color: v-bind('theme.colors.primary');
  padding: v-bind('theme.spacing.md');
}
</style>
```

---

## React ↔ Vue Parity Mapping

| React | Vue | Notes |
|---|---|---|
| `props` | `defineProps()` | TypeScript generics in both |
| `children` | Default `<slot />` | |
| Named slots (render props) | Named `<slot name="x" />` | |
| `useState` | `ref()` / `reactive()` | |
| `useEffect` | `watchEffect()` / `onMounted()` | |
| `useContext` | `provide()` / `inject()` | |
| `forwardRef` | `defineExpose()` | |
| `className` | `:class` | Object/array syntax supported |

---

## Design-Engineer Integration

Spoke of `design-engineer`. When building DS components for Vue:
1. Start from the React reference implementation
2. Map props, slots, and composition patterns per the table above
3. Ensure token consumption is identical (CSS custom properties)
4. Test keyboard and a11y behavior parity
