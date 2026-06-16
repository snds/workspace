---
name: centric-ui-storybook
description: >
  Storybook deployment, access, story authoring, and management for the
  centric-ui repository (React 19 + Vite 7 + Tailwind CSS 4 + shadcn/ui).
  Use this skill whenever the conversation involves: installing Storybook into
  centric-ui, configuring .storybook/ for this specific stack, writing stories
  for shadcn/ui primitives or feature components, running Storybook locally,
  deploying Storybook to GitHub Pages or Chromatic, adding Storybook scripts
  to package.json, integrating Storybook into the quality gate or CI workflow,
  or troubleshooting Storybook configuration issues in this project. Spoke of
  both the `design-engineer` hub and `centric-ui-workflow` — load alongside
  both. For generic Storybook concepts (CSF 3 syntax, addon APIs, interaction
  testing patterns) defer to `fw-storybook`.
aliases: [centric-ui-storybook]
spec_version: "2.0"
tier: spoke
domain: design
hub: design-engineer
prerequisites: [design-engineer]
---

# Centric UI — Storybook

Spoke skill for Storybook in the `centric-ui` repo. Covers the full lifecycle:
installation, configuration, local access, story conventions, and deployment.

Load `fw-storybook` for generic CSF 3 syntax and addon API reference.
Load `centric-ui-workflow` for branch naming, PR process, and quality gate.

---

## Domain Boundary

This skill owns **Storybook setup and operation within centric-ui**.

- **Generic CSF 3 / story authoring patterns** → `fw-storybook`
- **Tailwind CSS 4 config concepts** → `fw-tailwind-css`
- **shadcn/ui component API** → `fw-shadcn`
- **GitHub workflow (PR, branches, CI)** → `centric-ui-workflow`

---

## Status

Storybook is **not yet installed** in `centric-ui` as of 2026-04-15.
This skill covers both initial setup and ongoing management.

---

## Stack Constraints That Affect Setup

Two constraints make the setup non-trivial:

1. **`@react-router/dev/vite`** — The app's `vite.config.ts` includes React
   Router's Vite plugin, which registers framework-level transforms not
   meaningful to Storybook. `.storybook/main.ts` must define its own Vite
   config via `viteFinal` rather than inheriting the root config.

2. **Tailwind CSS 4 (`@tailwindcss/vite`)** — Tailwind v4 uses a Vite plugin,
   not PostCSS. The `viteFinal` config must include this plugin explicitly.
   Storybook's CSS processing will not pick up Tailwind v4 any other way.

---

## Installation

```bash
# From centric-ui/
npx storybook@latest init --type react --builder vite --skip-install
npm install --save-dev \
  @storybook/react-vite \
  @storybook/addon-docs \
  @storybook/addon-a11y \
  @storybook/addon-themes \
  @storybook/addon-interactions \
  @storybook/addon-viewport \
  @storybook/test
npm install
```

> `storybook@latest init` scaffolds `.storybook/` and adds `stories/` examples.
> Delete the `stories/` example directory after init — stories live co-located
> with components per this project's conventions.

---

## `.storybook/main.ts`

```ts
import tailwindcss from "@tailwindcss/vite";
import tsconfigPaths from "vite-tsconfig-paths";
import type { StorybookConfig } from "@storybook/react-vite";

const config: StorybookConfig = {
  stories: [
    "../app/components/ui/**/*.stories.@(ts|tsx)",
    "../app/features/**/*.stories.@(ts|tsx)",
  ],
  addons: [
    "@storybook/addon-docs",
    "@storybook/addon-a11y",
    "@storybook/addon-themes",
    "@storybook/addon-interactions",
    "@storybook/addon-viewport",
  ],
  framework: {
    name: "@storybook/react-vite",
    options: {},
  },
  viteFinal(config) {
    // Replace root vite.config.ts plugins — React Router's plugin is
    // framework-level and incompatible with Storybook's build mode.
    // Re-add only what Storybook actually needs: Tailwind v4 + path aliases.
    config.plugins = [tailwindcss(), tsconfigPaths()];
    return config;
  },
};

export default config;
```

> **Why `viteFinal`?** Storybook merges the root `vite.config.ts` by default.
> The `reactRouter()` plugin expects a full React Router app context and will
> error in Storybook's isolated environment. `viteFinal` overrides the plugin
> list cleanly.

---

## `.storybook/preview.ts`

```ts
import "../app/app.css";
import type { Preview } from "@storybook/react";

const preview: Preview = {
  parameters: {
    backgrounds: { disable: true },   // replaced by themes addon below
    layout: "centered",
  },
  decorators: [
    // Dark mode via themes addon — mirrors app's .dark class strategy
    // Install: @storybook/addon-themes
    // withThemeByClassName from @storybook/addon-themes
  ],
};

export default preview;
```

Import `app/app.css` to pull in the `@import "tailwindcss"` entry, the
`@theme` block with CDS tokens, shadcn CSS variables, and Inter font.
Without this, shadcn/ui components render unstyled.

### Dark mode decorator

```ts
import { withThemeByClassName } from "@storybook/addon-themes";

// Add to decorators array in preview.ts:
withThemeByClassName({
  themes: { light: "", dark: "dark" },
  defaultTheme: "light",
}),
```

The app uses `.dark` class on `<html>` to activate dark mode (Tailwind
`@custom-variant dark (&:is(.dark *))`). This decorator applies the same class
to Storybook's story root.

---

## `package.json` Scripts

Add to `scripts`:

```json
{
  "storybook": "storybook dev -p 6006",
  "storybook:build": "storybook build -o storybook-static",
  "storybook:preview": "npx serve storybook-static -l 6007"
}
```

Access locally at `http://localhost:6006`.

> Do not run on the same port as the main app (8082).

---

## Local Access

```bash
npm run storybook          # Dev server with HMR at http://localhost:6006
npm run storybook:build    # Static export to storybook-static/
npm run storybook:preview  # Preview the static build at :6007
```

Storybook runs independently from the backend — no Docker Compose or Keycloak
required. Stories render components in isolation with mock data.

For stories that use TanStack Query hooks, wrap in a `QueryClientProvider`
decorator rather than hitting real API endpoints.

---

## Story Placement Conventions

Stories live **co-located** with the component they document.

| Component type | Story location |
|---------------|---------------|
| shadcn/ui primitive | `app/components/ui/button.stories.tsx` |
| Feature component (public) | `app/features/views/components/TableWidget.stories.tsx` |
| Feature component (internal) | Only if the component is worth isolated documentation |

**Do not** create a top-level `stories/` directory. The glob in `main.ts`
covers both `components/ui/` and `features/**` — stories belong next to source.

### Story title hierarchy

```
Components/Primitives/Button
Components/Primitives/Input
Components/Composites/InputGroup
Features/Views/TableWidget
Features/SchemaCanvas/NodeCard
```

Match the `design-engineer` hub's component classification:
`Primitives → Composites → Patterns → Templates`.

### What to write stories for

**Always write stories for:**
- Everything in `app/components/ui/` — these are the shared primitives
- Any component exported from a feature barrel (`index.ts`) that has visual states

**Write stories when:**
- A component has non-trivial variant/state combinations (size × emphasis × state)
- A component is used across 3+ features (likely promotion candidate)
- You're building a new shadcn/ui primitive or custom composite

**Skip stories for:**
- Route shells (`app/routes/`) — thin wrappers with no visual logic
- Internal feature utilities without visual output
- Generated API hooks (`app/api/generated/`)

---

## TanStack Query in Stories

Stories that exercise data-fetching components need a `QueryClientProvider`.
Use a decorator in the story file (not globally in `preview.ts`) to keep
the mock scope narrow:

```tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { Decorator } from "@storybook/react";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const withQuery: Decorator = (Story) => (
  <QueryClientProvider client={queryClient}>
    <Story />
  </QueryClientProvider>
);

export default {
  title: "Features/Views/TableWidget",
  component: TableWidget,
  decorators: [withQuery],
} satisfies Meta<typeof TableWidget>;
```

For components that fire real queries, use MSW (`msw-storybook-addon`) to
intercept and return fixture data. This mirrors the project's existing
Vitest + MSW pattern.

---

## Accessibility Testing

The `@storybook/addon-a11y` addon runs axe-core on every story automatically.
This is mandatory for anything in `app/components/ui/` — these primitives
are the a11y baseline for the entire app.

No extra configuration needed after addon install. The a11y panel appears in
the Storybook UI alongside Controls and Actions.

---

## Deployment: GitHub Pages (Recommended)

GitHub Pages is the natural fit for a static Storybook alongside the existing
GitHub Actions setup.

### `.github/workflows/storybook.yml`

```yaml
name: Deploy Storybook

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: true

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: "22"
          cache: "npm"

      - run: npm ci

      - run: npm run storybook:build

      - uses: actions/upload-pages-artifact@v3
        with:
          path: storybook-static

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/deploy-pages@v4
        id: deployment
```

Enable GitHub Pages in repo Settings → Pages → Source: **GitHub Actions**.

Storybook deploys on every push to `main`. Access at:
`https://cpes-software.github.io/centric-ui/`

### Adding to the deploy PR checklist

Once Storybook is deployed, add a verification step to the
`docs/collaboration-workflow.md` PR process:
- "Check the Storybook deploy preview reflects any changed components."

---

## Deployment: Chromatic (Optional — Visual Regression)

Chromatic adds visual snapshot diffing on top of the GitHub Pages deploy.
Use it when visual regression coverage becomes a priority.

```bash
npm install --save-dev chromatic
```

Add to `.github/workflows/storybook.yml` (or a separate workflow):

```yaml
- name: Publish to Chromatic
  uses: chromaui/action@v1
  with:
    projectToken: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
    buildScriptName: storybook:build
```

Store the Chromatic project token in GitHub Secrets as
`CHROMATIC_PROJECT_TOKEN`. Free tier covers up to 5,000 snapshots/month.

---

## Quality Gate Integration

Storybook is **not** part of `npm run check:quality` by default. Add it
optionally when the story suite is mature enough to be meaningful:

```json
"check:stories": "storybook build --quiet 2>&1 | grep -c ERROR || true"
```

A build-time error in Storybook (broken import, type error in a story)
is a signal worth catching in CI. Run `npm run storybook:build` in the
`storybook.yml` workflow as the build gate before deploying.

---

## `.storybook/` in `.gitignore`

Do not ignore `.storybook/`. The config directory belongs in version control.
Add the build output to `.gitignore` if it isn't already:

```
storybook-static/
```

---

## Checklist: First-Time Setup

- [ ] Install packages (`@storybook/react-vite` + addons)
- [ ] Create `.storybook/main.ts` with `viteFinal` override (Tailwind + paths)
- [ ] Create `.storybook/preview.ts` importing `../app/app.css`
- [ ] Add dark mode decorator via `withThemeByClassName`
- [ ] Add `storybook` and `storybook:build` scripts to `package.json`
- [ ] Delete scaffolded `stories/` example directory
- [ ] Write first stories for `app/components/ui/button.tsx` and `app/components/ui/input.tsx`
- [ ] Verify `npm run storybook` opens at `http://localhost:6006` with correct styling
- [ ] Create `.github/workflows/storybook.yml`
- [ ] Enable GitHub Pages in repo settings (Source: GitHub Actions)
- [ ] Add `storybook-static/` to `.gitignore`
- [ ] Open PR via `centric-ui-workflow` process: branch `chore/storybook-setup`

## Related
- hub → [[design-engineer]]
