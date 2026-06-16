---
name: fw-web-components
description: >
  Web Components and Lit — framework-agnostic custom elements, Shadow DOM, CSS parts,
  and the Lit library for building design system components that work everywhere. Use
  this skill whenever the conversation involves Web Components, custom elements,
  Shadow DOM, HTML templates, CSS ::part, Lit (lit.dev), or building framework-agnostic
  design system components. Also trigger when discussing cross-framework DS strategies
  where components must work in React, Vue, Angular, and vanilla HTML, or when
  evaluating Web Components as a distribution format. If the user mentions "Web
  Components", "custom elements", "Shadow DOM", "Lit", "lit-element", "::part",
  or framework-agnostic components — use this skill.
pinned_version: "Lit 3.3.2"
pinned_date: "2026-03-26"
changelog_url: "https://github.com/lit/lit/releases"
aliases: [fw-web-components]
tier: spoke
domain: engineering
hub: lead-frontend-engineer
prerequisites: [lead-frontend-engineer]
spec_version: "2.0"
---

# Web Components / Lit — Framework Skill

## Version Check (run on every load)

1. Web search for `Lit latest release`.
2. Compare against `pinned_version: Lit 3.3.2`.
3. Flag if newer. Proceed.

---

## Core Standards

Web Components are three browser standards:

### 1. Custom Elements
Define new HTML tags with JavaScript classes:

```javascript
class DsButton extends HTMLElement {
  static observedAttributes = ['variant', 'size', 'disabled'];

  connectedCallback() { this.render(); }
  attributeChangedCallback() { this.render(); }

  render() {
    this.innerHTML = `<button class="btn btn--${this.getAttribute('variant')}">
      <slot></slot>
    </button>`;
  }
}

customElements.define('ds-button', DsButton);
```

### 2. Shadow DOM
Encapsulated DOM tree with scoped styles:

```javascript
connectedCallback() {
  const shadow = this.attachShadow({ mode: 'open' });
  shadow.innerHTML = `
    <style>
      :host { display: inline-flex; }
      .btn { background: var(--color-primary); }
    </style>
    <button class="btn"><slot></slot></button>
  `;
}
```

### 3. HTML Templates & Slots
`<slot>` = content projection (Figma slot equivalent):

```html
<template id="card-template">
  <slot name="header"></slot>
  <slot></slot>  <!-- default -->
  <slot name="footer"></slot>
</template>
```

---

## Lit (Recommended DX Layer)

Lit adds reactive properties, declarative templates, and efficient updates on top
of Web Components standards:

```typescript
import { LitElement, html, css } from 'lit';
import { customElement, property } from 'lit/decorators.js';

@customElement('ds-button')
export class DsButton extends LitElement {
  static styles = css`
    :host { display: inline-flex; }
    button {
      background: var(--color-primary);
      color: var(--color-on-primary);
      padding: var(--spacing-sm) var(--spacing-md);
      border-radius: var(--radius-md);
      border: none;
      cursor: pointer;
    }
    button:hover { background: var(--color-primary-hover); }
    :host([disabled]) button { opacity: 0.5; cursor: not-allowed; }
  `;

  @property() variant: 'primary' | 'secondary' | 'ghost' = 'primary';
  @property() size: 'sm' | 'md' | 'lg' = 'md';
  @property({ type: Boolean, reflect: true }) disabled = false;

  render() {
    return html`
      <button class="btn--${this.variant} btn--${this.size}" ?disabled=${this.disabled}>
        <slot></slot>
      </button>
    `;
  }
}
```

---

## CSS Custom Properties: The Token Bridge

Web Components + CSS custom properties = framework-agnostic theming:

```css
/* Tokens defined at document level */
:root {
  --color-primary: oklch(0.6 0.2 250);
  --spacing-md: 1rem;
}

/* Component consumes tokens via Shadow DOM */
:host {
  background: var(--color-primary);
  padding: var(--spacing-md);
}
```

CSS custom properties pierce the Shadow DOM boundary. This is the key mechanism
for design system theming across Web Components.

### CSS ::part for external styling

```javascript
// Component exposes parts
render() {
  return html`<button part="button"><slot></slot></button>`;
}
```

```css
/* Consumer styles the part */
ds-button::part(button) {
  font-weight: bold;
}
```

---

## Framework Interop

| Framework | Usage |
|---|---|
| **Vanilla HTML** | `<ds-button variant="primary">Click</ds-button>` |
| **React** | Works directly; use `@lit/react` wrapper for better DX |
| **Vue** | Works directly; configure `compilerOptions.isCustomElement` |
| **Angular** | Works directly; add `CUSTOM_ELEMENTS_SCHEMA` |
| **Svelte** | Works directly |

### React wrapper (recommended)

```typescript
import { createComponent } from '@lit/react';
import { DsButton } from './ds-button.js';

export const Button = createComponent({
  tagName: 'ds-button',
  elementClass: DsButton,
  react: React,
  events: { onClick: 'click' },
});
```

---

## DS Distribution Strategy

Web Components as the canonical implementation, with framework wrappers:

```
Source of truth: Lit Web Components
  ├── React wrapper (@lit/react)
  ├── Vue wrapper (native custom element support)
  ├── Angular wrapper (CUSTOM_ELEMENTS_SCHEMA)
  └── Vanilla HTML (zero wrapper)
```

**Tradeoff**: Maximum portability, but SSR is harder and React interop has friction
around event handling and complex props.

---

## Design-Engineer Integration

Spoke of `design-engineer`. Web Components are relevant when:
- DS must work across React, Vue, Angular, and vanilla simultaneously
- Framework migration is planned (components survive the migration)
- Micro-frontend architecture requires framework-agnostic shared UI
- The DS is consumed by external teams with unknown stacks

Pair with **fw-radix-colors** for the color token system and **fw-tailwind-css** for
utility generation alongside Web Components.

## Related
- hub → [[lead-frontend-engineer]]
