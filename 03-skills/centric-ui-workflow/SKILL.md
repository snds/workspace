---
name: centric-ui-workflow
description: >
  GitHub workflow, architecture patterns, and design-engineer conventions for
  the centric-ui repository (Centric VMS UI). Use this skill whenever the
  conversation involves: branch creation or naming for centric-ui, opening or
  reviewing pull requests in this repo, running the quality gate, understanding
  where to place new features or components, shadcn/ui or Tailwind CSS 4 usage
  in this codebase, working with the Orval-generated API layer, navigating the
  feature module structure, or releasing/deploying a new version. Trigger on
  "centric-ui", "VMS UI", "make a PR", "branch for", "where does this go",
  "which feature folder", "codegen", or "deploy a release" in the context of
  this project. Spoke of the `design-engineer` hub — load in addition to it,
  not instead of it.
aliases: [centric-ui-workflow]
spec_version: "2.0"
tier: spoke
domain: design
hub: design-engineer
prerequisites: [design-engineer]
---

# Centric UI — Design-Engineer Workflow

Spoke skill for the `design-engineer` hub. Covers the GitHub workflow, codebase
conventions, and design-engineer-specific patterns for the `centric-ui` repo
(React 19 SPA for Centric VMS — a multi-tenant Vendor Management System).

Always load the `design-engineer` hub alongside this skill. This spoke adds
repo-specific depth; the hub provides the design+engineering dual-lens mindset.

---

## Domain Boundary

This skill owns **repo workflow and design-engineer conventions for centric-ui**.

- **General design-engineer lens** → `design-engineer` (hub skill)
- **GitHub safety layer, why-behind-the-rules, dismissable guardrails** → `github-guardrails`
- **shadcn/ui CLI, theming, component customization** → `fw-shadcn`
- **Tailwind CSS 4 @theme, CSS-first config** → `fw-tailwind-css`
- **Icon/variable font work (CentricSymbols)** → `variable-icon-font-architect`

---

## Project at a Glance

| Attribute | Value |
|-----------|-------|
| **Type** | React 19 SPA — no SSR |
| **Router** | React Router v7 (SPA mode) |
| **Styling** | Tailwind CSS 4 + shadcn/ui |
| **State** | TanStack Query v5 (server state only) |
| **Build** | Vite 7 |
| **Package manager** | npm (`npm ci`, never yarn or pnpm) |
| **TypeScript** | Strict mode, TS 6 |
| **Testing** | Vitest + happy-dom + MSW |
| **API** | Orval-generated TanStack Query hooks |
| **Auth** | Keycloak OIDC PKCE |
| **Repo root** | `centric-ui/` within `cpes-software` monorepo |

The app is schema-driven: business object types are defined at runtime via the
Schema Registry, not hardcoded. Every feature that deals with data operates
through this dynamic schema + record model.

---

## GitHub Workflow

### Branch naming

```
<type>/<ticket-or-scope>-<short-kebab-description>
```

| Type | When |
|------|------|
| `feat` | New user-facing functionality |
| `fix` | Bug or regression fix |
| `refactor` | Code restructuring, no behavior change |
| `docs` | Documentation-only changes |
| `chore` | Maintenance, tooling, dependency updates |
| `test` | Tests only |

**Examples:**
```
feat/views-filter-panel
fix/bo-inline-edit-null-guard
refactor/schema-canvas-layout
chore/deps-tanstack-query-5-71
docs/local-setup-plm-seed
```

Always branch from `main`. Keep one branch per change — no mixing unrelated work.
Rebase or merge `main` frequently to keep diffs small.

### Pull request process

1. **Open early as a draft** while work is in progress.
2. **Narrow scope** — avoid mixing unrelated changes in a single PR.
3. **Description must include**: intent, impact, and validation steps.
4. **Request review** only when the branch is fully ready.
5. **After approval, the PR author merges** — never the approver.
6. **Re-request review** if you push additional commits post-approval.

### Commit message format

```
type(scope): summary in lowercase imperative

feat(views): add filter panel to table widget
fix(auth): guard against null tenant in requestContextStore
chore(deps): bump tanstack query to 5.71.0
```

Types: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`.
Scope = the feature folder name or the subsystem affected.

---

## Quality Gate

**Run before requesting review. Reviewers must also run this before merging.**

```bash
npm run check:quality   # Full gate: lint + types + format + knip + jscpd + react-doctor
npm run test            # Vitest unit tests
```

Never substitute individual commands for `check:quality`. The gate includes:
- **eslint** — linting with import sorting
- **tsc** — strict TypeScript + route typegen
- **prettier** — code formatting
- **knip** — unused imports/exports detection
- **jscpd** — duplicate code detection
- **react-doctor** — React anti-patterns

Optional (use when touching the build artifact):
```bash
npm run build           # Verify production build succeeds
```

---

## CI/CD Pipeline

Deploys are triggered in two ways:

1. **Manual dispatch** — `workflow_dispatch` in GitHub Actions
2. **Semantic version tag push** — tag format `X.Y.Z` (e.g., `1.4.2`)
   - Release candidates (`1.4.2rc1`) are **skipped** automatically

On trigger, GitHub Actions:
1. Builds the React app with Vite (env vars injected as `VITE_*` build args)
2. Builds a Docker image
3. Pushes to `ghcr.io/cpes-software/centric-ui`
4. Tags: `{version}` + `latest`

**To release a new version:**
```bash
git tag 1.4.2
git push origin 1.4.2
```

The Keycloak URLs, API key, and service name are GitHub Actions Variables
(`vars.VITE_*`) — not secrets committed to the repo.

---

## Project Structure — Where Things Go

```
app/
  routes.ts              ← All route definitions (one flat file)
  root.tsx               ← App root + providers (QueryClient, AuthProvider)
  routes/                ← Thin route shells only: React.lazy + Suspense + ProtectedRoute
  features/              ← ALL feature logic lives here
    {featureName}/
      index.ts           ← Barrel export — external callers import through here only
      components/        ← Feature-scoped components
      hooks/             ← Feature-scoped hooks
      queryOptions.ts    ← TanStack Query options for this feature
      types.ts           ← Feature-scoped TypeScript types
  components/
    ui/                  ← shadcn/ui primitives (DO NOT add feature code here)
    layout/              ← App shell: Header, Sidebar
  api/
    generated/           ← Orval output — DO NOT EDIT MANUALLY
    custom-fetch.ts      ← Orval mutator: service routing + response unwrapping
  lib/
    apiClient.ts         ← apiGet, apiPost, apiMakeRawRequest
    queryClient.ts       ← TanStack Query defaults
  config/
    env.ts               ← Zod-validated env vars
    api.ts               ← Service base URLs
    routes.ts            ← Type-safe route path constants
```

### Feature boundary rules

- **No cross-feature imports** except through barrel exports (`index.ts`)
- ESLint enforces this — it will fail if you import internal paths across features
- Feature-specific query logic → `features/{name}/queryOptions.ts`
- **Do not** add feature code to `app/hooks/`, `app/components/{feature}/`, or `app/lib/`
- New route? Add it to `app/routes.ts` and export `meta()` from the route component

### Route shells — the correct pattern

```tsx
// app/routes/myFeature.tsx
import { lazy, Suspense } from "react";
import { ProtectedRoute } from "~/components/ProtectedRoute";

const MyFeaturePage = lazy(() => import("~/features/myFeature").then(m => ({ default: m.MyFeaturePage })));

export function meta() {
  return [{ title: "My Feature - Centric VMS" }];
}

export default function MyFeatureRoute() {
  return (
    <ProtectedRoute>
      <Suspense fallback={null}>
        <MyFeaturePage />
      </Suspense>
    </ProtectedRoute>
  );
}
```

---

## Design-Engineer Patterns

### UI components: shadcn/ui + Tailwind CSS 4

- Primitives live in `app/components/ui/` (shadcn/ui community)
- Install new shadcn components via `npx shadcn@latest add <component>`
  (MCP config in `.mcp.json` enables this)
- Tailwind CSS 4: use CSS-first config, `@theme` block, and CSS custom properties
- `@container` + `@sm:` / `@lg:` for component-local responsiveness — preferred
  over `useResizeObserver` for layout breakpoints

### Native browser APIs — always prefer these

| Task | Use this | Not this |
|------|---------|---------|
| Modals / dialogs | `NativeDialog` + `useNativeDialogState` (`~/components/ui/native-dialog.tsx`) | `useState(open)` + third-party dialog |
| Component responsiveness | CSS `@container` + Tailwind `@sm:` | `useResizeObserver` |
| State-driven UI swaps | `startViewTransition()` (`~/lib/viewTransitions.ts`) | Direct state mutation |
| Auto-growing textareas | `field-sizing: content` (`field-sizing-content` utility) | JS resize handlers |
| Accessible ID generation | `useId()` | Manual string IDs |
| Determinate progress | Native `<progress>` | Custom div + width hack |

> **Popover exception**: Native Popover API needs CSS anchor positioning (not
> stable in Safari < 26). Keep `@base-ui/react/popover` for placement.

Always respect `prefers-reduced-motion`. The app-level CSS rule kills
`::view-transition-*` under reduced motion — new transitions must also bail.

### Data fetching — mandatory rules

- **TanStack Query for ALL server state.** No `useEffect`-based fetching.
- Guard queries: `enabled: !!tenantId` (prevents unauthenticated requests)
- Use Orval-generated hooks for simple CRUD
- Wrap generated fetch functions in `queryOptions` for custom logic
- **Never manually edit `app/api/generated/`** — run `npm run codegen` after
  any backend OpenAPI spec change

### API client pattern

```
React component
  → TanStack Query hook (caching, deduplication)
    → Orval-generated API function
      → customFetch (service routing + envelope unwrap)
        → apiMakeRawRequest (auth headers + timeout + 401 retry)
          → fetch()
```

Use `apiGet` / `apiPost` from `~/lib/apiClient` for non-generated calls.
All requests automatically receive: `Authorization`, `x-tenant-id`,
`x-user-profile-id`, `x-api-key`, `x-cpes-service-name`.

### TypeScript conventions

- `import type { ... }` for type-only imports
- No default exports except route components (React Router convention)
- Use `~/` alias for `app/` directory
- Imports are auto-sorted by `simple-import-sort` (via eslint) — don't fight it

---

## Local Development

```bash
# Prerequisites: backend Docker Compose running (centric-service repo)
# Hosts entry required: 127.0.0.1 keycloak.local

npm ci
npm run dev              # HMR dev server at http://localhost:8082
npm run test             # Vitest
npm run check:quality    # Full lint + type + format gate
npm run codegen          # Regenerate API types from OpenAPI specs
npm run seed             # Lightweight test data
npm run plm:seed         # Production-like PLM data (~370 schemas)
```

**Always use `http://localhost:8082`** — not `http://127.0.0.1:8082`. Keycloak
PKCE is origin-specific; 127.0.0.1 breaks the auth redirect.

Default login: `test` / `test` (realm: VMS, org: test-org)

### Large-header gotcha

All `dev` scripts set `NODE_OPTIONS='--max-http-header-size=65536'`. Keycloak
tokens with many roles + group memberships exceed Node's 16 KB default header
limit. This is pre-configured in `package.json` — don't remove it.

---

## Views Feature — Special Architecture

`app/features/views/` has its own architectural conventions. Read these docs
before touching it:
- `docs/plans/2026-03-27-views-system.md` — full architecture plan
- `docs/features/09-views.md` — feature spec with native browser API list

Key conventions:
- **Two-context split**: `ViewScopeContext` (low-churn) + `ViewEditContext`
  (high-churn). Hot widgets subscribe via `useViewScopeOptional()` — not
  `useViewContext()` — to avoid re-renders on edit-mode toggles.
- **Edit callbacks**: use `latest = useRef({...})` pattern for stable identity.
  Don't add reactive deps — it re-introduces the context churn perf bug.
- **Single-widget shortcut**: exactly one widget bypasses `react-grid-layout`
  and renders at `h-full`. Adding a second widget restores RGL.
- **Layout vs. config**: layout positions → `localStorage`; semantic config →
  `x-layout-config` on the schema spec. Save flushes layout before the BE PUT.

---

## KISS Principle

This project enforces KISS explicitly:
- Prefer the simplest solution that fully solves the problem
- No premature abstractions — if it's only used once, don't extract it
- Split large changes into smaller, understandable increments
- If two approaches are valid, choose the one with fewer moving parts
- Optimize for readability and maintainability over cleverness

Three similar lines of code is better than a premature abstraction.

---

## Active Branches (as of 2026-04-15)

| Branch | Purpose |
|--------|---------|
| `main` | Primary development |
| `feature/integrate-design-system` | Design system integration in progress |
| `feature/doc-management` | Document management feature |
| `feature/ci-cd` | CI/CD improvements |

---

## Key Files Reference

| File | Purpose |
|------|---------|
| [app/routes.ts](centric-ui/app/routes.ts) | All route definitions |
| [app/root.tsx](centric-ui/app/root.tsx) | App root + providers |
| [app/lib/apiClient.ts](centric-ui/app/lib/apiClient.ts) | apiGet, apiPost, apiMakeRawRequest |
| [app/lib/queryClient.ts](centric-ui/app/lib/queryClient.ts) | TanStack Query defaults |
| [app/api/custom-fetch.ts](centric-ui/app/api/custom-fetch.ts) | Orval mutator |
| [app/config/env.ts](centric-ui/app/config/env.ts) | Zod-validated env vars |
| [app/config/routes.ts](centric-ui/app/config/routes.ts) | Type-safe route constants |
| [CLAUDE.md](centric-ui/CLAUDE.md) | AI agent conventions (always read) |
| [docs/collaboration-workflow.md](centric-ui/docs/collaboration-workflow.md) | Branch, MR, KISS rules |
| [docs/system-architecture.md](centric-ui/docs/system-architecture.md) | Backend contracts + auth flow |
| [.github/workflows/deploy.yml](centric-ui/.github/workflows/deploy.yml) | CI/CD pipeline |

---

## HITL Level

Agent configuration: `plan_only`. Generate implementation plans before execution.
Human review is required before implementation begins. Max retries per task: 3.

## Related
- hub → [[design-engineer]]
