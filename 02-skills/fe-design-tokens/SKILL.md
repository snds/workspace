---
name: fe-design-tokens
description: >
  Design token pipeline engineering — the implementation layer between token
  architecture (ds-advisor) and component consumption (fe-component-architecture).
  Use this skill whenever the conversation touches: Figma Variables to Style
  Dictionary pipeline, platform output generation (CSS custom properties, JS/TS,
  Android XML, iOS Swift), Style Dictionary configuration and custom transforms,
  DTCG (Design Token Community Group) format ($value, $type, $description,
  $extensions), Figma Variable modes as token themes, Figma Tokens or Token
  Studio export, Figma REST API for token sync, CSS custom property cascading
  and component-scope vs. :root scope, @layer specificity management, JavaScript
  token consumption for animation, Emotion/styled-components theme object shape,
  Tailwind config extension from token JSON, light/dark theme switching via CSS
  custom properties, color-scheme property, FOUC prevention, token semantic
  versioning, deprecation patterns, or changelog generation from token diffs.
  Not for: token architecture design decisions and naming strategy (ds-advisor),
  component implementation that consumes tokens (fe-component-architecture),
  or visual design system decisions (lead-ui-designer).
hub: lead-frontend-engineer
aliases: [fe-design-tokens]
tier: spoke
domain: engineering
prerequisites: [lead-frontend-engineer]
spec_version: "2.0"
---

# Fe: Design Tokens

Specialist lens for design token pipeline engineering — the build system and
consumption layer between design tooling and code. Part of the frontend engineering
skill network.

---

## Domain Boundary

This skill owns: **token pipeline architecture, Style Dictionary configuration,
DTCG format, Figma Variables sync, CSS custom property consumption patterns,
theme switching, and token governance**.

- Token architecture: naming, tier structure, semantic meaning → `ds-advisor`
- Component implementation that consumes tokens → `fe-component-architecture`
- Visual design system design → `lead-ui-designer`
- Design engineering integration work → `design-engineer`

---

## Token Pipeline Architecture

### The Full Chain

```
Figma Variables
      ↓  (export via plugin or REST API)
Raw token JSON (DTCG format)
      ↓  (Style Dictionary build step)
Platform outputs:
  ├── CSS custom properties    (web)
  ├── ES module / TypeScript   (web, JS consumers)
  ├── Android XML              (Android)
  └── iOS Swift enum           (iOS)
```

Tokens are a build artifact. The source of truth is the Figma Variables definition
(or the checked-in JSON if Figma is not the source). Platform outputs are generated,
never hand-edited.

### Why a Build Step is Required

Raw token JSON contains semantic aliases — a token's value is a reference to
another token, not a raw value:

```json
{
  "color": {
    "button": {
      "background": {
        "$value": "{color.brand.primary.500}",
        "$type": "color"
      }
    }
  }
}
```

The build step:
1. **Resolves aliases** — replaces references with concrete values (or CSS custom
   property references, depending on platform config)
2. **Transforms values** — converts hex colors to HSL, pixel values to rem,
   milliseconds to seconds (platform-specific)
3. **Formats output** — generates correctly-formatted platform code
4. **Tree-shakes** — omits unused tokens if configured (reduces CSS payload)

### Token Pipeline as CI Artifact

Tokens must be version-controlled and pipeline-generated:

```yaml
# GitHub Actions: tokens build step in CI
- name: Build design tokens
  run: npm run tokens:build
  
- name: Assert no uncommitted token changes
  run: git diff --exit-code src/tokens/  # fails if build output changed without commit
```

The "designers update Figma, developers notice at the next design review" workflow
is a process smell. The correct model: Figma publish → webhook or polling → PR
opened against the token JSON → CI builds → review → merge → tokens deploy with
the next release.

---

## Style Dictionary Deep Dive

### Configuration Structure

```javascript
// style-dictionary.config.js
import StyleDictionary from 'style-dictionary';

const config = {
  source: ['tokens/**/*.json'],     // glob for input token files
  platforms: {
    css: {
      transformGroup: 'css',        // built-in transform group
      buildPath: 'dist/tokens/',
      files: [{
        destination: 'tokens.css',
        format: 'css/variables',    // built-in formatter
        options: {
          selector: ':root',        // default scope
          outputReferences: true,   // emit CSS var() references, not resolved values
        }
      }]
    },
    js: {
      transformGroup: 'js',
      buildPath: 'dist/tokens/',
      files: [{
        destination: 'tokens.js',
        format: 'javascript/es6',
      }]
    },
    ts: {
      transformGroup: 'js',
      buildPath: 'dist/tokens/',
      files: [{
        destination: 'tokens.d.ts',
        format: 'typescript/es6-declarations',
      }]
    }
  }
};

const sd = new StyleDictionary(config);
await sd.buildAllPlatforms();
```

### Built-in Transforms

Transforms mutate a token's `name`, `value`, or `attributes`. They are applied
in order within a transform group.

| Transform | What it does |
|-----------|-------------|
| `attribute/cti` | Adds `category/type/item` attribute from the token's position in the object hierarchy |
| `name/cti/kebab` | Generates a kebab-case name from the CTI path |
| `name/cti/camel` | Generates a camelCase name from the CTI path |
| `color/css` | Passes color values through (CSS already handles hex/hsl) |
| `color/rgb` | Converts color to rgb() format |
| `color/hsl` | Converts color to hsl() format |
| `size/rem` | Converts pixel values to rem (assumes 16px root) |
| `size/px` | Converts dimension numbers to px string |
| `time/seconds` | Converts ms to seconds for CSS transitions |

### Custom Transforms

```javascript
// Custom transform: add a --ds- prefix to all token names
StyleDictionary.registerTransform({
  name: 'name/ds-prefix',
  type: 'name',
  transform: (token) => `ds-${token.name}`
});

// Custom transform: convert opacity tokens to decimal
StyleDictionary.registerTransform({
  name: 'value/opacity-decimal',
  type: 'value',
  filter: (token) => token.$type === 'number' && token.path.includes('opacity'),
  transform: (token) => token.$value / 100
});
```

### Transform Groups

A transform group is a named array of transforms applied in sequence to a platform.
The built-in `css` transform group includes: `attribute/cti`, `name/cti/kebab`,
`time/seconds`, `content/icon`, `size/rem`, `color/css`.

Define custom groups for specific output requirements:

```javascript
StyleDictionary.registerTransformGroup({
  name: 'css-with-prefix',
  transforms: ['attribute/cti', 'name/ds-prefix', 'color/css', 'size/rem']
});
```

### Formatters

Built-in formatters for common output formats:

| Formatter | Output |
|-----------|--------|
| `css/variables` | `:root { --color-brand-500: #3b82f6; }` |
| `javascript/es6` | `export const ColorBrand500 = '#3b82f6';` |
| `typescript/es6-declarations` | `export declare const ColorBrand500: string;` |
| `scss/variables` | `$color-brand-500: #3b82f6;` |
| `json/flat` | `{ "color-brand-500": "#3b82f6" }` |
| `android/resources` | Android XML resource file |
| `ios-swift/class.swift` | Swift class with token constants |

Custom formatter for a Tailwind-compatible JSON:

```javascript
StyleDictionary.registerFormat({
  name: 'json/tailwind',
  format: ({ dictionary }) => {
    const tokens = {};
    dictionary.allTokens.forEach(token => {
      // Build nested object from token path
      let current = tokens;
      token.path.forEach((segment, i) => {
        if (i === token.path.length - 1) {
          current[segment] = token.value;
        } else {
          current[segment] = current[segment] || {};
          current = current[segment];
        }
      });
    });
    return JSON.stringify(tokens, null, 2);
  }
});
```

### Composite Tokens and Value References

`outputReferences: true` preserves the alias chain in CSS output:

```css
/* outputReferences: false — all values resolved */
:root {
  --color-brand-primary: #3b82f6;
  --color-button-background: #3b82f6;  /* value, not reference */
}

/* outputReferences: true — references preserved */
:root {
  --color-brand-primary: #3b82f6;
  --color-button-background: var(--color-brand-primary);  /* alias maintained */
}
```

Prefer `outputReferences: true` for CSS — it preserves semantic relationships
and enables theme overriding at the variable level.

### The `$value` / `$type` Distinction — DTCG Format

Style Dictionary v4+ natively supports DTCG format using `$value` and `$type`.
Earlier versions used `value` (no `$`) and required the `attribute/cti` transform
to infer type from object hierarchy.

```json
// DTCG (v4+ native, recommended)
{
  "color": {
    "brand": {
      "primary": {
        "$value": "#3b82f6",
        "$type": "color",
        "$description": "Primary brand color — use for primary actions"
      }
    }
  }
}
```

---

## DTCG Format

The Design Token Community Group format is the emerging standard for interoperable
token files. Tool support is growing across Figma, Style Dictionary, Theo, and TMS integrations.

### Token Schema

```json
{
  "token-name": {
    "$value": "...",          // required — the token's value
    "$type": "...",           // recommended — determines how value is interpreted
    "$description": "...",    // optional — human-readable documentation
    "$extensions": {          // optional — tool-specific metadata
      "com.figma": {
        "hiddenFromPublishing": false,
        "scopes": ["ALL_FILLS"]
      }
    }
  }
}
```

### Token Types

| Type | Value format | Example |
|------|-------------|---------|
| `color` | CSS color string | `"#3b82f6"`, `"hsl(217, 91%, 60%)"` |
| `dimension` | Number + unit | `"16px"`, `"1rem"`, `"4pt"` |
| `fontFamily` | String or array | `"Inter"`, `["Inter", "sans-serif"]` |
| `fontWeight` | Number or keyword | `700`, `"bold"` |
| `duration` | Number + unit | `"200ms"`, `"0.2s"` |
| `cubicBezier` | Array of 4 numbers | `[0.4, 0, 0.2, 1]` |
| `number` | Bare number | `1.5`, `16` |
| `boolean` | Boolean | `true`, `false` |
| `string` | Bare string | `"uppercase"` |
| `strokeStyle` | String or object | `"solid"`, `{ "dashArray": ["2px", "4px"], "lineCap": "round" }` |
| `border` | Composite object | `{ "color": "{color.border}", "width": "1px", "style": "solid" }` |
| `transition` | Composite object | `{ "duration": "200ms", "delay": "0ms", "timingFunction": [0.4,0,0.2,1] }` |
| `shadow` | Composite object | `{ "color": "...", "offsetX": "0", "offsetY": "4px", "blur": "8px", "spread": "0" }` |
| `gradient` | Array of stops | `[{ "color": "{color.brand}", "position": 0 }, ...]` |
| `typography` | Composite object | `{ "fontFamily": "...", "fontSize": "...", "fontWeight": ..., "lineHeight": "..." }` |

### Why DTCG Matters

Tool interoperability: a token file in DTCG format can be consumed by Style
Dictionary, Tokens Studio, Theo, and (increasingly) Figma itself without
conversion. Without a standard, each tool had its own format, requiring
translation layers.

---

## Figma Variables to Tokens

### Figma Variables API

Figma Variables are exposed via the REST API at:

```
GET https://api.figma.com/v1/files/:file_key/variables/local
```

Returns all variable collections, modes, and variable values. Each variable has:
- `id`, `name`, `key` — identifiers
- `variableCollectionId` — which collection (e.g., "Color", "Spacing")
- `resolvedType` — `COLOR`, `FLOAT`, `STRING`, `BOOLEAN`
- `valuesByMode` — values keyed by mode ID (light/dark, brand A/brand B)

### Variable Modes as Token Themes

Figma Variable modes map directly to token themes:

| Figma Variable Collection | Figma Modes | Token themes |
|--------------------------|------------|-------------|
| Color | Light, Dark | `light`, `dark` |
| Brand | Default, Cobalt, Slate | `default`, `cobalt`, `slate` |
| Density | Comfortable, Compact | `comfortable`, `compact` |

Each mode produces a separate set of CSS custom property overrides:

```css
:root { --color-background: #ffffff; }          /* light (default) */
[data-theme="dark"] { --color-background: #0f172a; }
[data-brand="cobalt"] { --color-brand-primary: #1d4ed8; }
[data-density="compact"] { --spacing-component-md: 8px; }
```

### Export Plugins vs. REST API

| Method | Pros | Cons |
|--------|------|------|
| Token Studio (Figma plugin) | Designer-initiated, battle-tested | Manual export, plugin dependency |
| Figma Tokens (plugin) | Wide adoption, GitHub sync | Plugin dependency |
| Official Figma REST API | No plugin required, automatable | Requires mapping to DTCG yourself |

For a production pipeline, the REST API is preferred — it enables fully automated
sync via a GitHub Action that polls for Figma file changes (via `GET /files/:key`
`lastModified` timestamp) and opens a PR automatically.

### Figma-to-Git Synchronization

```yaml
# Figma sync GitHub Action (runs hourly or on webhook)
name: Sync Figma Tokens
on:
  schedule:
    - cron: '0 * * * *'  # hourly polling
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Fetch Figma variables
        run: node scripts/fetch-figma-tokens.js
        env:
          FIGMA_ACCESS_TOKEN: ${{ secrets.FIGMA_ACCESS_TOKEN }}
          FIGMA_FILE_KEY: ${{ vars.FIGMA_FILE_KEY }}
      - name: Build tokens
        run: npm run tokens:build
      - name: Open PR if changed
        uses: peter-evans/create-pull-request@v6
        with:
          title: 'chore(tokens): sync from Figma'
          branch: 'auto/figma-token-sync'
          commit-message: 'chore(tokens): sync from Figma'
```

---

## Token Consumption in Components

### CSS Custom Properties — Cascading Semantics

```css
/* :root scope — global defaults */
:root {
  --color-button-background: var(--color-brand-primary-500);
  --color-button-text: var(--color-neutral-0);
  --spacing-button-padding-inline: var(--spacing-4);
}

/* Component scope — override without affecting global */
.button--ghost {
  --color-button-background: transparent;
  --color-button-text: var(--color-brand-primary-500);
}

/* Theme scope — all component tokens update at once */
[data-theme="dark"] {
  --color-brand-primary-500: #60a5fa;
}
```

The cascade is the feature — component tokens inherit from semantic tokens which
inherit from primitive tokens. A theme override at `:root` or `[data-theme]`
cascades automatically to all consuming components.

### `@layer` for Specificity Management

```css
@layer tokens, base, components, utilities;

@layer tokens {
  :root {
    --color-brand-500: #3b82f6;
  }
}

@layer components {
  .button {
    background: var(--color-brand-500);
  }
}
```

Place token definitions in the lowest-specificity layer. This ensures component
styles can reference tokens without specificity conflicts from the token definition
itself.

### JavaScript Token Consumption

Import tokens as ES module constants for values that need to be used in JavaScript
contexts (animation libraries, canvas, WebGL, dynamic calculations):

```typescript
// Generated token module
export const DurationTransitionFast = '100ms';
export const DurationTransitionBase = '200ms';
export const EasingStandard = [0.4, 0, 0.2, 1] as const;

// Usage in Framer Motion or GSAP
import { DurationTransitionBase, EasingStandard } from '@acme/tokens';

animate(element, { opacity: 1 }, {
  duration: parseInt(DurationTransitionBase) / 1000,  // ms → seconds
  ease: EasingStandard
});
```

Motion tokens — duration and easing — are the primary driver for JS token imports.
Color tokens are better handled as CSS custom properties.

### CSS-in-JS Token Consumption

For Emotion or styled-components, the theme object shape should mirror the token
hierarchy:

```typescript
// theme.ts — generated or maintained from token JSON
export const theme = {
  color: {
    brand: { primary: { 500: 'var(--color-brand-primary-500)' } },
    button: { background: 'var(--color-button-background)' }
  },
  spacing: {
    4: 'var(--spacing-4)'
  }
} as const;

// Usage in Emotion
const Button = styled.button`
  background: ${({ theme }) => theme.color.button.background};
  padding: ${({ theme }) => theme.spacing[4]};
`;
```

Prefer referencing CSS custom properties (via `var()`) in the theme object rather
than resolved values. This preserves the theme-switching capability of the CSS layer.

### Tailwind Config Extension

```javascript
// tailwind.config.js — extend from generated token JSON
import tokens from './dist/tokens/tokens.json';

/** @type {import('tailwindcss').Config} */
export default {
  theme: {
    extend: {
      colors: tokens.color,
      spacing: tokens.spacing,
      fontFamily: tokens.fontFamily,
      transitionDuration: tokens.duration,
    }
  }
};
```

Generate the Tailwind-compatible JSON via a custom Style Dictionary formatter
(see the `json/tailwind` formatter in the Style Dictionary section above). This
ensures Tailwind classes and CSS custom properties reference the same source values.

---

## Theme Switching

### CSS Custom Property Override Pattern

```css
/* Primitive tokens — no theme variation */
:root {
  --color-blue-500: #3b82f6;
  --color-blue-900: #1e3a5f;
  --color-neutral-0: #ffffff;
  --color-neutral-950: #0a0a0a;
}

/* Semantic tokens — light mode defaults */
:root {
  --color-background-surface: var(--color-neutral-0);
  --color-text-primary: var(--color-neutral-950);
}

/* Dark mode overrides — same custom property names, new values */
[data-theme="dark"] {
  --color-background-surface: var(--color-neutral-950);
  --color-text-primary: var(--color-neutral-0);
}

/* Multi-brand overrides — only brand primitives change */
[data-brand="cobalt"] {
  --color-blue-500: #1d4ed8;
}
```

Components reference only semantic tokens (`--color-background-surface`), never
primitives. Theme switching changes the semantic tokens; components update automatically.

### `color-scheme` Property

```css
:root {
  color-scheme: light;  /* tells the browser the page uses a light color scheme */
}

[data-theme="dark"] {
  color-scheme: dark;   /* enables correct browser-native controls (scrollbars, inputs) */
}
```

`color-scheme` affects browser-native UI elements that `color` and `background-color`
don't reach. Always set it alongside your custom property overrides.

### `prefers-color-scheme` Media Query

```css
/* System default — no JavaScript required */
@media (prefers-color-scheme: dark) {
  :root {
    --color-background-surface: var(--color-neutral-950);
    --color-text-primary: var(--color-neutral-0);
    color-scheme: dark;
  }
}
```

Use `prefers-color-scheme` as the initial baseline — it works before any JavaScript
loads. When the user selects a preference in your UI, write it to `data-theme` on
`<html>` and persist it to `localStorage`.

### FOUC Prevention

Flash of Unstyled Content occurs when theme preference is stored in localStorage
but applied after the page renders (React hydration runs client-side).

```html
<!-- Inline script in <head> — runs before first paint, no FOUC -->
<script>
  (function() {
    const theme = localStorage.getItem('theme') || 
      (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);
  })();
</script>
```

This script must be inline in `<head>`, not in an external JS file. External files
load after the DOM is painted. Next.js handles this via a custom `_document.tsx`
or the `next-themes` library which does the same thing.

---

## Token Governance and Versioning

### Semantic Versioning for Token Packages

Token packages (published to npm or an internal registry) follow semver:

| Change type | Version bump | Examples |
|------------|-------------|---------|
| **Major** | Breaking — consumers must update their code | Removing a token, renaming a token, changing a token's type |
| **Minor** | Additive — new tokens consumers can optionally adopt | New token, new theme mode, new platform output |
| **Patch** | Value change — same semantic meaning, updated raw value | Color value adjustment, spacing value refinement |

Value changes are patch, not breaking — if a component is correctly using semantic
tokens, a primitive color value changing should not require code changes.

### Deprecation Pattern

When renaming or restructuring a token, maintain the old name for one major version:

```json
{
  "color": {
    "primary": {
      "$value": "{color.brand.primary.500}",
      "$type": "color",
      "$description": "DEPRECATED: Use color.button.background instead. Removed in v4.",
      "$extensions": {
        "deprecated": true,
        "deprecatedSince": "3.0.0",
        "replacement": "color.button.background"
      }
    }
  }
}
```

In the CSS output, emit a comment on deprecated tokens:

```css
/* @deprecated: Use --color-button-background instead. Removed in v4. */
--color-primary: var(--color-brand-primary-500);
```

Automated lint rules (Stylelint custom rule) can warn on usage of deprecated
custom property names.

### Changelog Generation from Token Diffs

```bash
# Compare token JSON between releases to generate a changelog
node scripts/token-diff.js \
  --from dist/tokens.v3.json \
  --to dist/tokens.v4.json \
  --output CHANGELOG-tokens.md
```

The diff script categorizes changes:
- Added tokens → Minor
- Removed tokens → Major (breaking)
- Renamed tokens → Major (breaking)
- Value changes → Patch
- Type changes → Major (breaking)

### Automated Breaking-Change Detection

```yaml
# CI check: fail if a published token was removed without a deprecation notice
- name: Token breaking change check
  run: node scripts/token-breaking-check.js \
    --baseline dist/tokens.main.json \
    --head dist/tokens.branch.json
```

The check fails if any token present in the baseline is absent in the head
build without a corresponding deprecation entry in the previous version. This
prevents accidental breaking changes from landing silently.

---

## Cross-Spoke Routing

| Topic | Route To |
|-------|----------|
| Token architecture, naming strategy, semantic tier design | `ds-advisor` |
| Component implementation that consumes tokens | `fe-component-architecture` |
| Visual design system decisions (what tokens encode) | `lead-ui-designer` |
| Design engineering integration | `design-engineer` |
