---
tags: [knowledge-vault, index]
created: 2026-04-28
updated: 2026-06-04
---

# Knowledge Vault — Index

Navigable index of all entries in `08-knowledge/`. Updated by Claude at the end of sessions
when new entries are written. Entries are grouped by domain, then listed alphabetically.

---

## Design

- [[radix-derived-color-system]] — Validated color-foundation architecture: Radix as source of truth + Tailwind-name compat aliases (nearest-OKLCh-L) + APCA-as-governance (not primitive mutation) + brand-aware semantic hue collision-avoidance + accent(hover, step 4) vs selected(active, step 5). Triggers: `color tokens`, `palette generator`, `radix colors`, `apca`, `accent token`, `brand color`, `semantic colors` (2026-06-02)
- [[centric-plm-design-system]] — DS strategy, token architecture, data table scope, Ark UI decision, cross-framework approach (2026-04-28)
- [[centricsymbols-icon-font]] — Variable icon font architecture: 4 axes, Figma authoring constraints, pipeline, COLRv1 (2026-04-28)
- [[enterprise-saas-design-patterns]] — **Master operational reference**: 28-pattern catalog from 2026-05-12 Mobbin audit; cross-pattern primitive spine (StatusPill, Drawer, TypedFieldEditor, ActivityItem, RelationChip, Stepper, PropertiesRail, KeyboardShortcutMenu + 7 AI-provenance primitives); when-to-build-X decision routing; token vocabulary (density / status / cell-state / drawer-size); AI provenance discipline checklist; anti-patterns. **Auto-load on enterprise SaaS layout work** — triggers: `data table`, `record detail`, `bulk edit`, `saved view`, `filter chip`, `drawer`, `side panel`, `approval workflow`, `audit trail`, `csv import`, `inbox`, `notifications`, `cell anatomy`, `lifecycle`, `diff view`, `record comparison`, `tree table`, `BOM`, `ai summary`, `provenance`, `enterprise saas`, `PLM layout`. (2026-05-12)
- [[meridian-ds-prototype]] — Personal DS prototype: token system, component state coverage, ARIA audit, WCAG results (2026-04-28)

## Engineering

- [[centric-plm-codebase]] — Confirmed Centric 8 tech stack, dual frontend (Dojo/React), analysis project structure (2026-04-28)
- [[centric-plm-frontend-stack]] — CDS file: link quirks: TS2786 React types mismatch, tsconfig paths fix, circular interface fix, full DataTable API surface map (2026-05-05)
- [[centric-vms-frontend-stack]] — Quirks discovered shipping centric-ui Storybook + ds-docs Fumadocs site: ESLint 10/Next compat, Fumadocs Tabs uncontrolled by design, Tailwind 4 `@theme inline` baking, useSyncExternalStore pattern, Storybook iframe theme sync (2026-04-29)
- [[claude-code-mcp-scope]] — `claude mcp add` defaults to local (cwd-scoped) — use `--scope user` for global. Three scopes explained; diagnosis recipe; OAuth-on-first-call for HTTP transports; restart-required behavior (2026-05-12)
- [[claude-code-skills-vs-slash-commands]] — Skills are model-invocable everywhere but only locally-installed ones show in the `/` menu; cloud/Cowork bundles (`anthropic-skills:*`) don't. How to wrap a skills dir as a local plugin/marketplace so it surfaces as `/<plugin>:<skill>` (plugin.json has no skills-path field → must copy under `skills/`; keep outside Drive; restart required) (2026-06-02)
- [[figma-plugin-patterns]] — Five hard-won Figma plugin patterns from the figma-repo-sync-plugin Bundles 5–7: layoutSizingHorizontal/Vertical=FILL beats layoutAlign=STRETCH, three-tier upsert for persistent artifacts, Tailwind /N opacity parsing requires color-class gate, multiply opacity on paint not variable, createFrame()'s 100×100 seed requires resize(1,1) kickstart (2026-05-11)
- [[figma-tailwind-token-pipeline]] — Cross-project mechanics from the generator-driven Radix→Figma migration: (1) Tailwind v4 unlayered `:root` overrides `@layer theme` so a palette's VALUES swap wholesale without touching utilities (verify via `@tailwindcss/node` compile); (2) Figma `Variable.consumers` returns 0 even for bound vars → audit usage via alias-refs / node-walk, not consumers; (3) CSS = full dev compat, Figma = design-surface subset only (shades/alpha CSS-only; shade→step binding); (4) one theme-control point (flat primitives + themed semantics) beats two; (5) self-healing migration — retire-by-name, sweepUnseeded, split-brain resolve, O(n) index to avoid the 1700-var O(n²) hang. Triggers: `tailwind`, `design tokens`, `figma variables`, `palette`, `css cascade`, `token pipeline`, `Variable.consumers`, `@theme` (2026-06-04)
- [[figma-variable-state-representation]] — Figma variable resolution mechanics + the CVA variant×state→Figma pattern (Bundles 11.3.49–70): modes are a vertical slice (one axis physical when variant+state collide); opacity can't be mode-driven → normalized state-layer (Decision B); `resolvedVariableModes`/`resolveForConsumer` are the authoritative resolver (pin-heuristics give false positives); Selection Colors `(?)` ≠ broken binding (multi-value cosmetic); the black-default resolver trap; grouped `<slot>/<state>` naming + explicit `default` affordance; single-source-of-truth + palette-generator migration seam (2026-05-23)

## Data Science

_No entries yet._

## Game Dev

- [[legion-architecture]] — Legion tech stack, V1 scope, 3D asset context, skill routing, open questions (2026-04-28)
- [[threejs-galaxy-visualization]] — Five hard-won Three.js patterns from the 2026-05-11 Legion galaxy pass: userData.type for selection, per-layer pattern uniqueness for stacked-shader volume, dedicated dust planes for true occlusion, opacity ramps for seamless zoom transitions, per-object camera framing scale (2026-05-11)

## Research

_No entries yet._

## Cross-Domain

- [[figma-source-audit-patterns]] — Five source shapes; state-coverage taxonomy; recurring gaps observed in the centric-ui Figma library (sizing, variants, composition, properties, variables, indicators); per-component recommendations table (2026-05-08)
- [[figma-component-composition-from-react]] — Compound generation two-layer model (outer story-driven, inner JSX-anatomy); Figma INSTANCE constraints; variant/independent/INSTANCE_SWAP decision matrix; shadcn conventions (2026-05-07)
- [[workspace-infrastructure]] — Drive+Git layered sync, hook dispatcher, Drive desync bug + fix, multi-machine topology, sync monitoring on macOS (UF_DATALESS), multi-identity GitHub setup (2026-05-07)
- [[workflow-patterns]] — Stale-content review, 3-bucket pending structure, audit_skip, session-end habits, trigger-word loading (2026-04-28)
- [[knowledge-vault-design]] — Why three surfacing tiers exist, why entries ≠ skills, how to extend the system (2026-04-29)

---

_Add entries: create a file in the appropriate subdirectory, then add a line here._
_Format: `- [[filename]] — one-line summary (YYYY-MM-DD)`_
