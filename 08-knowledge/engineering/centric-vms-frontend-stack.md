---
tags: [centric, vms, react, vite, nextjs, fumadocs, storybook, tailwind, eslint, knowledge]
created: 2026-04-29
updated: 2026-04-29
status: working
confidence: high
sources: [session-log 2026-04-29, cpes-software/centric-ui, cpes-software/ds-docs]
related_skills: [lead-frontend-engineer, design-engineer, ds-advisor]
related_projects: [centric-vms-design-system]
---

# Centric VMS Frontend Stack — Quirks Worth Remembering

Direct learnings from setting up Storybook on `cpes-software/centric-ui` and standing up the companion docs site at `cpes-software/ds-docs`. Each item below is a real gotcha discovered through PR-blocking failures, not speculation.

---

## Two-tool documentation setup

The DS uses **two repos** that intentionally divide labor:

| Tool | Where | Answers |
|---|---|---|
| Storybook 10 | [cpes-software/centric-ui](https://github.com/cpes-software/centric-ui) `.storybook/` + `*.stories.tsx` | "What does this component do? What are its props? Does it pass a11y?" |
| Fumadocs site | [cpes-software/ds-docs](https://github.com/cpes-software/ds-docs) `content/docs/` | "When should I use this? What's the design intent? How do I compose it?" |

The narrative site embeds Storybook stories via a custom `<StorybookEmbed id="..." />` MDX component (iframe pointed at `${NEXT_PUBLIC_STORYBOOK_URL}/iframe.html?id=...&viewMode=story&globals=theme:...`). This pattern was chosen after evaluating Fumadocs Story (the bundled alternative) — it covers ~10–15% of Storybook's surface (no play functions, no a11y addon, no Chromatic, no decorators, no doc blocks, no per-story URLs), so replacement isn't viable.

**When to recommend this pattern:** any DS team that wants curated narrative docs alongside a robust component playground without rebuilding playground machinery in MDX.

---

## ESLint 10 + `eslint-config-next@16` — incompatible

ESLint 10 (released ~Oct 2025) removed several legacy APIs that older lint plugins still call:

- `scopeManager.addGlobals` — used by `eslint/lib/languages/js/source-code/source-code.js`
- `contextOrFilename.getFilename` — used by `eslint-config-next`'s bundled `eslint-plugin-react`

**Symptom:** lint runs throw `TypeError: scopeManager.addGlobals is not a function` or `TypeError: contextOrFilename.getFilename is not a function` and exit non-zero. Looks like an internal ESLint crash, but it's actually a transitive plugin mismatch.

**Fix:** pin `eslint` to `^9.39.3` (or whatever 9.x your `eslint-config-next` was tested against). Both Fumadocs's create-next-app scaffold and many fresh Next projects pull in 10.x by default — the pin is necessary until `eslint-config-next` is updated.

```json
"eslint": "^9.39.3"
```

centric-ui already has this pin baked in. ds-docs needed manual correction after scaffolding.

---

## Fumadocs `<Tabs>` is uncontrolled by design

Fumadocs's `Tabs` wrapper at `fumadocs-ui/components/tabs` deliberately **omits `value` and `onValueChange`** in favour of an uncontrolled `groupId`-based sync model (cross-page tab persistence by group identity). The TS type signature is:

```ts
interface TabsProps extends Omit<ComponentProps<typeof Tabs$1>, 'value' | 'onValueChange'> { ... }
```

The internal primitive at `fumadocs-ui/components/ui/tabs` ALSO destructures and discards these props.

**Symptom:** if you try to pass `value={...}` and `onValueChange={...}`, dev mode silently accepts it (TS isn't strict enough during HMR) but `next build` fails with `Property 'value' does not exist on type 'IntrinsicAttributes & TabsProps'`.

**Fix:** when you genuinely need controlled tabs (e.g. binding to a global persisted state like a doc-mode toggle), use `@radix-ui/react-tabs` directly. It's already a transitive dependency of Fumadocs, so it's in `node_modules`. Wrap the Radix primitives in your own thin styling layer.

The ds-docs `ContentTabs` component does exactly this for its Design / Code split.

---

## Tailwind 4 `@theme inline` bakes literal values

If you declare a token via:

```css
@theme inline {
  --color-cds-gray-100: #f5f6fa;
}
```

Tailwind generates utilities (`bg-cds-gray-100` etc.) using the **literal value** at build time, not as a CSS variable reference. So a runtime override like:

```css
.dark {
  --color-cds-gray-100: #1a1d24;
}
```

has **no effect on the utility** — the dark value is never read.

**Symptom:** centric-ui's `html, body { @apply bg-cds-gray-100 }` always renders the light value, even with `<html class="dark">`. Latent bug in centric-ui (CDS gray utilities are theme-blind).

**Fix:**
- For tokens that should be theme-aware, use `@theme {}` (without `inline`) which keeps the variable indirection, OR
- Reference a separate CSS variable explicitly: `--color-foo: var(--my-token);` where `--my-token` is overridden in `.dark`.
- Only use `@theme inline { ... }` for tokens that are intentionally theme-blind (brand-fixed colors).

The semantic tokens (`--sem-*` family) work correctly because they're declared via the var-reference pattern, not as inline literals.

---

## Storybook iframe theme sync via `preview-head.html`

To make embedded Storybook stories render with the correct theme when the docs site is in dark mode, the docs site appends `?globals=theme:dark|light` to the iframe URL. For Storybook to honor this on first paint (before `withThemeByClassName` decorator hydrates), inject a tiny script in `.storybook/preview-head.html` that reads the URL globals param and applies `.dark` synchronously:

```html
<script>
  (function () {
    try {
      var params = new URLSearchParams(window.location.search);
      var globals = params.get("globals") || "";
      if (/(?:^|[,;])theme:dark(?:[,;]|$)/.test(globals)) {
        document.documentElement.classList.add("dark");
      }
    } catch (_) {}
  })();
</script>
```

Plus a CSS override for the body background, because of the `@theme inline` quirk above:

```html
<style>
  html.dark, html.dark body {
    background-color: var(--sem-background, #111318);
    color: var(--sem-foreground, #e4e8f0);
  }
</style>
```

Without the CSS override, the iframe applies `.dark` to `<html>` but the `bg-cds-gray-100` utility on `body` still renders the light hex value, producing a light-on-dark bug.

---

## `useSyncExternalStore` for localStorage subscription

The naive pattern for hydration-safe localStorage state:

```tsx
const [mode, setMode] = useState(DEFAULT);
useEffect(() => {
  const stored = localStorage.getItem(KEY);
  if (stored) setMode(stored);
}, []);
```

Triggers ESLint's `react-hooks/set-state-in-effect` rule (cascading-render anti-pattern in React 19+). The idiomatic React replacement:

```tsx
const mode = useSyncExternalStore(
  (cb) => {
    window.addEventListener("storage", cb);
    window.addEventListener("my-custom-update-event", cb);
    return () => {
      window.removeEventListener("storage", cb);
      window.removeEventListener("my-custom-update-event", cb);
    };
  },
  () => (localStorage.getItem(KEY) as DocMode) ?? DEFAULT,  // client snapshot
  () => DEFAULT,                                            // server snapshot
);
```

Setter dispatches the custom event so same-tab subscribers update (the native `storage` event only fires for OTHER tabs):

```tsx
const setMode = useCallback((next) => {
  localStorage.setItem(KEY, next);
  window.dispatchEvent(new Event("my-custom-update-event"));
}, []);
```

ds-docs's `DocModeProvider` uses this pattern. SSR uses `DEFAULT`, post-hydration the client snapshot reflects localStorage, no setState cascade.

---

## next-themes `resolvedTheme === undefined` as the hydration check

Don't roll your own `mounted` state to gate next-themes-dependent rendering:

```tsx
// ❌ Triggers react-hooks/set-state-in-effect
const [mounted, setMounted] = useState(false);
useEffect(() => setMounted(true), []);
const theme = mounted && resolvedTheme === "dark" ? "dark" : "light";
```

`next-themes` already exposes `resolvedTheme === undefined` as the pre-hydration signal:

```tsx
// ✅ No useState, no useEffect
const { resolvedTheme } = useTheme();
const ready = resolvedTheme !== undefined;
const theme = ready && resolvedTheme === "dark" ? "dark" : "light";
```

Same behaviour, no lint violation.

---

## Branch protection on a solo private repo

For a brand-new private repo with one contributor, the team-ready posture works:

- Require PR + 1 review + linear history + conversation resolution
- Force-push and deletion blocked
- `enforce_admins: false` so the user (admin) can bypass review while solo

When collaborators arrive, just remove the bypass. No restructuring required. The CI check name (`lint, types, build` in the workflow file) becomes the value to add as a required status check via `gh api repos/{owner}/{repo}/branches/main/protection` once CI has its first green run.

---

## Cross-references

- Cross-session memory at `~/.claude/projects/-Users-sean-sands-projects-cpes-software/memory/` holds project context: `project_centric_ui.md` (stack), `project_ds_docs.md` (two-tool setup), `project_ds_docs_admin_todos.md` (open admin items).
- Global memory at `~/.claude/CLAUDE.md` holds operating principles (verification-is-mine; always-link-references).
