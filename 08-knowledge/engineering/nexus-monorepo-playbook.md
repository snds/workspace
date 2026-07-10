---
tags: [engineering, monorepo, docusaurus, storybook, github-pages, pnpm, typescript, tailwind]
created: 2026-07-09
updated: 2026-07-09
status: stable
confidence: high
sources: [machine-local ~/.claude/CLAUDE.md (pre-beacon, migrated FX-15), nexus repo]
related_skills: [design-engineer]
related_projects: [15-DavinciRemake]
---

# Nexus monorepo playbook — DS + docs + Pages gotchas already solved

_Migrated 2026-07-09 from the machine-local `~/.claude/CLAUDE.md` (FX-15). Companion to
[[davinci-ds-boilerplate]] — that entry says WHAT to build; this one carries the hard-won
technical fixes._

- **pnpm strictness:** transitive deps used directly must be explicit. Storybook needs
  `@storybook/react`, `@storybook/manager-api`, `@storybook/theming`. Docusaurus swizzles using
  `@docusaurus/theme-common/internal` need `@docusaurus/theme-common` as a direct dep.
- **Docusaurus dogfood pipeline:** a plugin with `configureWebpack` adding `resolve.alias` to
  `@nexus/*` source + `resolve.extensionAlias { ".js": [".tsx",".ts",".js"] }` (workspace uses ESM
  `.js` specifiers); `configurePostCss` pushing `tailwindcss` + `autoprefixer`; a tailwind config
  with `corePlugins.preflight: false` (don't reset Infima) scanning `packages/ui/src`; import tokens
  CSS + `@tailwind` in `custom.css`; Material Symbols via `stylesheets`. Bind the FULL Infima
  variable set to DS tokens — **but at matching specificity**: Infima ships its dark defaults under
  `html[data-theme="dark"]` (0,1,1), so a bare `[data-theme="dark"]` (0,1,0) LOSES and the chrome
  silently falls back to Infima's neutral grays (#1b1b1d) instead of the cool DS neutrals. Always
  bind under `html[data-theme="dark"]`. Verify the *computed* `--ifm-background-color` resolves to
  `hsl(var(--nx-bg))`, not a gray hex — a passing build hides this. Swizzle `Navbar/Content` +
  `Footer`; build a DS landing in `src/pages`. Set `markdown.format: 'md'` so existing `.md` with
  `{}`/`<>` don't break MDX.
- **shadcn defaults carry skeuomorphic shadows.** The pristine shadcn Button ships a Tailwind
  `shadow`/`shadow-sm` drop shadow — a raised-chip look at odds with a flat, surface-color elevation
  model. Don't hand-edit the L1 base; flatten via the theme layer by zeroing **only** `--tw-shadow`
  on `[data-slot="button"]` (in `shadcn-bridge.css`, so it reaches demo + docs + Storybook) — this
  keeps the focus-visible ring, which composes into `--tw-ring-shadow`, intact. Leave floating
  overlays (Popover/Dialog/Tooltip/Menu) their `shadow-lg/2xl` — those genuinely float.
- **Preflight-off ⇒ native button bevel (the *real* "skeuomorphic" tell).** When the docs Tailwind
  runs `corePlugins.preflight:false` (to not reset Infima), a bare `<button>` loses Preflight's
  `border:0 solid` reset and falls back to the UA `2px outset` bevel — a raised 3D edge that only
  appears in the docs (the Vite app has preflight on, so it looks flat). Don't chase it as a shadow:
  inspect computed `border` — `outset` is the giveaway. Fix in the theme layer scoped to the DS:
  force `border-style:solid` at high specificity (kills the bevel) + `border-width:0` at low
  specificity (so the `outline` variant's `.border` 1px still wins). General lesson: a Tailwind
  utility class is specificity (0,1,0) and can lose to later equal-specificity rules OR to absent
  Preflight — when overriding utilities, raise specificity (e.g. doubled attribute selector) and
  verify the **computed** value in the actual surface, never just "the rule is in the bundle."
- **Storybook:** static build is relocatable (relative assets) → host under any subpath. Theme the
  MANAGER chrome via `@storybook/theming` `create()` with inlined DS token values (manager is a
  separate app; tokens.css isn't loaded there). Preview themed via tokens.css + a tailwind config
  with the shadcn color mappings. The CSF3 `story-types` shim is runtime-compatible; interactive
  stories use `@storybook/react` types for `render`.
- **GitHub Pages:** parameterize each Vite `base` via `BASE_PATH` env. Deploy job: build each
  surface, assemble into `_site` (+ `.nojekyll`), `actions/configure|upload-pages-artifact|deploy-pages`
  with `pages: write` + `id-token: write`. Enable Pages once: `gh api -X POST repos/<o>/<r>/pages
  -f build_type=workflow`.
- **TS strict (`exactOptionalPropertyTypes`, `noUncheckedIndexedAccess`):** coerce optional booleans
  with `Boolean(x)`; pass optional props via conditional spread `{...(x?{x}:{})}`; annotate inline
  tuple arrays as `[string,string][]`. CSS-var string for `fontWeight` needs a cast.
- **Repo hygiene / IP:** never commit third-party proprietary reference (e.g. competitor screenshots,
  `design-source/`) to a PUBLIC repo — copyright + bloat; gitignore it, plus build output, `.claude/`,
  `storybook-static/`, `.docusaurus/`.
- **Preview automation:** React Flow / Radix open on the pointer sequence, not synthetic `.click()`;
  dispatch `pointerdown`+`pointerup`(+`click`). Re-fit/HMR can swallow clicks — settle, then act.

## Related

- [[davinci-ds-boilerplate]] — the boilerplate/dogfooding/token/docs standards this supports
- [[centric-vms-frontend-stack]] — related Storybook/Tailwind quirks from centric-ui work
