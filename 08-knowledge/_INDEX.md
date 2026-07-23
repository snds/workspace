---
tags: [knowledge-vault, index]
created: 2026-04-28
updated: 2026-07-08
---

# Knowledge Vault — Index

Navigable index of all entries in `08-knowledge/`. Updated by Claude at the end of sessions
when new entries are written. Entries are grouped by domain, then listed alphabetically.

---

## Design

- [[radix-derived-color-system]] — Validated color-foundation architecture: Radix as source of truth + Tailwind-name compat aliases (nearest-OKLCh-L) + APCA-as-governance (not primitive mutation) + brand-aware semantic hue collision-avoidance + accent(hover, step 4) vs selected(active, step 5). Triggers: `color tokens`, `palette generator`, `radix colors`, `apca`, `accent token`, `brand color`, `semantic colors` (2026-06-02)
- [[figma-ds-surface-authoring]] — Durable DS Figma authoring conventions for any surface/overlay: build-from-real-components (props-first), 14 surface/overlay construction rules (edge-to-edge separators, spacing-token binding incl. half-steps, absolute-positioned in-parent popovers, icon↔label match, no double padding, slot fill/hug, mode-first variants, total tokenization, floating-element constraints), and code→Figma transliteration judgment calls (focus uses `ring` token; otherwise code-faithful). Triggers: `figma authoring`, `surface authoring`, `overlay`, `popover`, `separator`, `mode-first`, `tokenize`, `transliteration`, `focus token` (2026-06-30)
- [[centric-plm-design-system]] — DS strategy, token architecture, data table scope, Ark UI decision, cross-framework approach (2026-04-28)
- [[davinci-ds-boilerplate]] — Portfolio demo-rebuild standards migrated from machine-local memory (FX-15): the nexus pnpm+turbo four-surface boilerplate, dogfooding definition (chrome literally uses the DS), the Radix 12-step token CONTRACT (text 11/12 · solids 9/10 · borders 6–8 + CI guards), and the canonical DS docs IA (Carbon/Atlassian/Polaris-grade). Triggers: `davinci`, `nexus`, `dogfooding`, `portfolio demo`, `docs ia`, `12-step contract` (2026-07-09)
- [[centricsymbols-icon-font]] — Variable icon font architecture: 4 axes, Figma authoring constraints, pipeline, COLRv1 (2026-04-28)
- [[enterprise-saas-design-patterns]] — **Master operational reference**: 28-pattern catalog from 2026-05-12 Mobbin audit; cross-pattern primitive spine (StatusPill, Drawer, TypedFieldEditor, ActivityItem, RelationChip, Stepper, PropertiesRail, KeyboardShortcutMenu + 7 AI-provenance primitives); when-to-build-X decision routing; token vocabulary (density / status / cell-state / drawer-size); AI provenance discipline checklist; anti-patterns. **Auto-load on enterprise SaaS layout work** — triggers: `data table`, `record detail`, `bulk edit`, `saved view`, `filter chip`, `drawer`, `side panel`, `approval workflow`, `audit trail`, `csv import`, `inbox`, `notifications`, `cell anatomy`, `record lifecycle`, `diff view`, `record comparison`, `tree table`, `BOM`, `ai summary`, `provenance`, `enterprise saas`, `PLM layout`. (2026-05-12)
- [[meridian-ds-prototype]] — Personal DS prototype: token system, component state coverage, ARIA audit, WCAG results (2026-04-28)

## Engineering

- [[centric-plm-codebase]] — Confirmed Centric 8 tech stack, dual frontend (Dojo/React), analysis project structure (2026-04-28)
- [[centric-plm-frontend-stack]] — CDS file: link quirks: TS2786 React types mismatch, tsconfig paths fix, circular interface fix, full DataTable API surface map (2026-05-05)
- [[centric-vms-frontend-stack]] — Quirks discovered shipping centric-ui Storybook + ds-docs Fumadocs site: ESLint 10/Next compat, Fumadocs Tabs uncontrolled by design, Tailwind 4 `@theme inline` baking, useSyncExternalStore pattern, Storybook iframe theme sync (2026-04-29)
- [[centric-ui-local-against-cloud-dev]] — Running centric-ui locally against the CLOUD dev backend. **Key rule: a 401 from a BE call is always the `x-api-key`, never the token or tenant** (validation order is api-key→401, tenant→403, Bearer passthrough) — and "Unauthorized API path" means the key isn't authorized for that path, NOT that the path is wrong. Three traps: the documented API key is the local-compose one (read the real one from the deployed app's own request headers); `resolveServiceBaseUrl` hard-returns "" in DEV so the Vite proxy table alone decides routing, and record/schema-registry/workflow are still localhost-only; Keycloak's `react` client accepts only `localhost:3000` while vite defaults to 8082 and the example file says 5173. Also: workflow-service has no cloud host (000, not 401). Triggers: `cloud dev`, `env.local`, `x-api-key`, `Unauthorized API path`, `redirect_uri`, `vite proxy`, `ECONNREFUSED 9011`, `9012`, `centric-ui local`, `sidebar empty`, `keycloak realm VMS` (2026-07-20)
- [[claude-code-hooks-contract]] — Claude Code hook payload contract: `hookEventName` must equal the event or the payload is SILENTLY dropped; PreToolUse deny-with-reason as a deterministic model-injection point; SessionStart `source` (compact/resume) re-injection; regex matchers for MCP tools. Triggers: `hookEventName`, `pretooluse`, `userpromptsubmit`, `sessionstart hook`, `additionalcontext`, `hook payload`, `hooks contract`, `hook didn't fire`, `claude hooks`, `hook dispatcher` (2026-07-09)
- [[claude-code-mcp-scope]] — `claude mcp add` defaults to local (cwd-scoped) — use `--scope user` for global. Three scopes explained; diagnosis recipe; OAuth-on-first-call for HTTP transports; restart-required behavior (2026-05-12)
- [[claude-code-skills-vs-slash-commands]] — Skills are model-invocable everywhere but only locally-installed ones show in the `/` menu; cloud/Cowork bundles (`anthropic-skills:*`) don't. How to wrap a skills dir as a local plugin/marketplace so it surfaces as `/<plugin>:<skill>` (plugin.json has no skills-path field → must copy under `skills/`; keep outside Drive; restart required) (2026-06-02)
- [[figma-plugin-patterns]] — Hard-won Figma plugin patterns from the figma-repo-sync-plugin Bundles 5–7: layoutSizingHorizontal/Vertical=FILL beats layoutAlign=STRETCH, three-tier upsert for persistent artifacts, Tailwind /N opacity parsing requires color-class gate, multiply opacity on paint not variable, createFrame()'s 100×100 seed requires resize(1,1) kickstart — **plus migrated Figma-API gotchas (§15–17): MS-icon min/max-width (rescale not resize), SectionNode parent-relative coords, use_figma MCP is headless** (2026-05-11, ext. 2026-06-30)
- [[figma-cli-authoring]] — Figma-CLI (Yolo/CDP) authoring: connecting (the "Full Disk Access" error is a red herring — Bash sandbox is the real blocker), branch targeting via `FIGMA_TARGET_TITLE` (+ the speed-daemon bypass + the flaky-render trap), self-invoking async IIFE for cross-path eval, verify/screenshot fallbacks, parallelize-analysis/serialize-mutation, creating SLOTs without `figma.createSlot`, creating variables, depth-aware section relayout, exclude SECTION chrome from token sweeps, glyph swap + mode-first application, probe-before-fixing render-ambiguous findings. Triggers: `figma-cli`, `figma cli`, `CDP`, `branch targeting`, `yolo`, `figma daemon`, `figma eval` (2026-06-30)
- [[figma-tailwind-token-pipeline]] — Cross-project mechanics from the generator-driven Radix→Figma migration: (1) Tailwind v4 unlayered `:root` overrides `@layer theme` so a palette's VALUES swap wholesale without touching utilities (verify via `@tailwindcss/node` compile); (2) Figma `Variable.consumers` returns 0 even for bound vars → audit usage via alias-refs / node-walk, not consumers; (3) CSS = full dev compat, Figma = design-surface subset only (shades/alpha CSS-only; shade→step binding); (4) one theme-control point (flat primitives + themed semantics) beats two; (5) self-healing migration — retire-by-name, sweepUnseeded, split-brain resolve, O(n) index to avoid the 1700-var O(n²) hang. Triggers: `tailwind`, `design tokens`, `figma variables`, `palette`, `css cascade`, `token pipeline`, `Variable.consumers`, `@theme` (2026-06-04)
- [[figma-variable-state-representation]] — Figma variable resolution mechanics + the CVA variant×state→Figma pattern (Bundles 11.3.49–70): modes are a vertical slice (one axis physical when variant+state collide); opacity can't be mode-driven → normalized state-layer (Decision B); `resolvedVariableModes`/`resolveForConsumer` are the authoritative resolver (pin-heuristics give false positives); Selection Colors `(?)` ≠ broken binding (multi-value cosmetic); the black-default resolver trap; grouped `<slot>/<state>` naming + explicit `default` affordance; single-source-of-truth + palette-generator migration seam (2026-05-23)
- [[nexus-monorepo-playbook]] — Solved gotchas for the DS+docs+Pages monorepo (migrated FX-15): pnpm strictness, Docusaurus dogfood pipeline (Infima specificity trap), shadcn shadow flattening, preflight-off button bevel, Storybook manager theming, GitHub Pages multi-surface deploy, TS-strict coercions, repo IP hygiene. Triggers: `docusaurus`, `storybook theming`, `github pages`, `preflight`, `swizzle`, `pnpm` (2026-07-09)
- [[silent-degradation-in-fenced-layers]] — A fence that degrades to `None`/absent/default erases the difference between "genuinely nothing" and "the mechanism failed" — a broken layer looks identical to a healthy-but-empty one, no error anywhere. Found 3× in one MediaSentinel session: swallowed timeout = no data, `except Exception: return None` making credit-exhaustion = "no guest found" (94 silent Nones), cache key omitting a governing param = stale hit; plus a progress counter that measured the cheap phase. Rules: give fenced layers a side channel for *why* (counter/last_error/one-time stderr); classify fatal vs per-item before collapsing; a cache value's every governing param is in the key or invalidation is explicit; monitor the real output artifact, never a counter you didn't verify. Triggers: `silent failure`, `except Exception`, `return None`, `graceful degradation`, `advisory layer`, `cache key`, `stale cache`, `swallowed error`, `observability`, `progress counter` (2026-07-22)

## Data Science

_No entries yet._

## Game Dev

- [[legion-architecture]] — Legion tech stack, V1 scope, 3D asset context, skill routing, open questions (2026-04-28)
- [[threejs-galaxy-visualization]] — Five hard-won Three.js patterns from the 2026-05-11 Legion galaxy pass: userData.type for selection, per-layer pattern uniqueness for stacked-shader volume, dedicated dust planes for true occlusion, opacity ramps for seamless zoom transitions, per-object camera framing scale (2026-05-11)
- [[legion-galaxy-playbook]] — Prescriptive build recipe for the Legion galaxy: the skill-load chain + ordered sequence (scale architecture → star field → volumetric disc/nebulae → dust occlusion → HDR/ACES pipeline → hero bodies → flythrough camera) + 60fps perf budget. Wires the new astro/VFX/scale-traversal skills; defers gotchas to [[threejs-galaxy-visualization]]. Triggers: `galaxy`, `nebula`, `star field`, `flythrough`, `volumetric`, `scale traversal`, `legion galaxy` (2026-06-16)

## Research

_Raw research syntheses live in `research/research/` (note: double-nested dir — flagged 2026-07-08, do not move without checking Obsidian links)._

- [[glsl-shader-programming]] — GLSL shader programming reference for WebGL/Three.js (2026-06)
- [[threejs-materials-deep-dive]] — Three.js PBR materials system complete reference (2026-06)
- [[threejs-postprocessing-vfx]] — Three.js post-processing, particles, VFX pipelines (2026-06)
- [[threejs-showcases-techniques]] — Award-winning Three.js showcases + production techniques (2026-06)
- [[webgpu-tsl-deep-dive]] — WebGPU, Three.js TSL & WebGPURenderer deep dive (2026-06)

## Cross-Domain

- [[figma-source-audit-patterns]] — Five source shapes; state-coverage taxonomy; recurring gaps observed in the centric-ui Figma library (sizing, variants, composition, properties, variables, indicators); per-component recommendations table (2026-05-08)
- [[figma-component-composition-from-react]] — Compound generation two-layer model (outer story-driven, inner JSX-anatomy); Figma INSTANCE constraints; variant/independent/INSTANCE_SWAP decision matrix; shadcn conventions (2026-05-07)
- [[workspace-infrastructure]] — Git-native workspace infrastructure: hook dispatcher (5 events, three-source tiered trigger routing), bootstrap-v2 machine layer (dist shims + doctor + beacon, per-machine installs), multi-machine topology, multi-identity GitHub; Drive-era learnings quarantined as historical (2026-07-09)
- [[workflow-patterns]] — Stale-content review, 3-bucket pending structure, audit_skip, session-end habits, trigger-word loading (2026-04-28)
- [[adversarial-verify-label-volatility]] — In a map→adversarially-verify multi-agent audit, the per-unit CONFIRMED/ADJUSTED/REFUTED label is sampling noise, not signal: two passes over identical mapped units swung 8/19/6 → 17/16/0 while every unit's rung + difficulty stayed identical. Report the stable mapped verdict ("two passes agreed on rung+difficulty; flags were refinements not reversals"), never a confirmed/adjusted count; aggregate k≥3 or gate on the correction diff for a durable pass/fail; independently hand-check load-bearing claims. Triggers: `adversarial verify`, `multi-agent audit`, `verification pass`, `confirmed adjusted refuted`, `refuted`, `judge panel`, `verify volatility`, `report the verdict` (2026-07-21)
- [[knowledge-vault-design]] — Why three surfacing tiers exist, why entries ≠ skills, how to extend the system (2026-04-29)
- [[skill-ecosystem-and-mcp-servers]] — Evaluation of skills.sh + mcpmarket.com: the three buckets (tool integrations / already-covered / genuine gaps), what we added (science math+physics, mobile, security), dedup decisions, attribution convention, recommended MCP servers (Blender for Legion, Postgres). Triggers: `mcpmarket`, `skills.sh`, `mcp server`, `blender`, `add skills`, `skill library` (2026-06-16)
- [[visual-failure-mode-ledger]] — The externalized memory behind framework #11 Anticipatory Failure Analysis + the `failure-mode-premortem` skill: technique-keyed rows (symptom · visible tell · root cause · prevention · how-to-detect · ref/tier) for how visual techniques classically fail and how to catch them in a frame. Domain-agnostic; seeded from Legion rendering; grows via the self-improving loop. Triggers: `pre-mortem`, `failure mode`, `what could go wrong`, `classic symptom`, `banding`, `dither crawl`, `bloom ring`, `acceptance criteria`, `ready for review`, `pitfall ledger` (2026-07-14)

---

_Add entries: create a file in the appropriate subdirectory, then add a line here._
_Format: `- [[filename]] — one-line summary (YYYY-MM-DD)`_
