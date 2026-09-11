---
tags: [figma, variables, opacity, design-tokens, mcp, plugin-api]
created: 2026-09-03
updated: 2026-09-03
status: working
confidence: high
sources:
  - Figma release notes 2026-09-03 "Control opacity at scale"
  - Figma help: Overview of variables; Create and manage variables
  - Figma MCP runtime probes on o6o1ZuGHxDow2vHLuYXT6X 2026-09-03
related_skills: [figma-variable-creation, figma-mcp-tool-usage, figma-plugin-dev, ds-advisor]
related_projects: [Centric SaaS PLM Design System]
relations:
  refutes:
    - "[[figma-variable-state-representation]]"
  relates-to:
    - "[[interaction-state-semantics]]"
    - "[[figma-ds-surface-authoring]]"
    - "[[figma-plugin-patterns]]"
---

# Figma opacity variables (layer, paint, color-variable)

## For future agent
- **TL;DR:** As of 2026-09-03 the Figma *UI* can bind a number variable to a color variable's opacity and to a fill/stroke opacity without detaching the color. Figma MCP `use_figma` (and the underlying Variables API) can bind **layer** opacity only. Paint / color-variable opacity writes are rejected. FLOAT opacity values are **0–100**, not 0–1. SaaS PLM DS now has `Opacity/*` primitives + `opacity/{disabled,scrim,hover,focus,pressed}` aliases.
- **Key claims:** MCP write path *is* `use_figma` JS in the file; `node.set` / `query().set` do not add a second binding channel. `get_variable_defs` *does* return bound layer opacity (code-syntax key → percent). Do not split Radix A-steps into opaque+opacity. Overlay Black/White ramps are the first candidates for color-var opacity once write support ships.
- **As of:** 2026-09 · **Status:** current

## What shipped in the product (2026-09-03)

Release: *Control opacity at scale*. Help center:

- Number variables apply to opacity of **color variables** and **layers** (values >100 clamp to 100%; negatives clamp to 0%).
- You can **alias a color while keeping a separate opacity** — no detach.
- Number-variable scopes in the UI include **Opacity → Of a color variable** and **Of a layer**. The Variables API still exposes a single `OPACITY` scope (`COLOR_OPACITY` / `LAYER_OPACITY` enums reject).

## Agent / MCP — what actually works (probed)

`use_figma` runs JS against the file. MCP-only extras (`node.set`, `node.query`, `screenshot`) use the same validators.

| Surface | Bind FLOAT to it? | How |
|---|---|---|
| Layer `node.opacity` | **Yes** | `node.setBoundVariable('opacity', floatVar)` |
| Paint fill/stroke opacity while color stays bound | **No** (2026-09-03) | `setBoundVariableForPaint(..., 'opacity', v)` rejected (field must be `color`). `boundVariables.opacity` unrecognized. `node.set({fills:[…]})` same. |
| Color variable opacity (alias color + number opacity) | **No** | `setValueForMode` rejects extra `opacity` / `a` keys. Variable has no `setBoundVariable`. |
| Effect opacity | **No** | Effect bindable fields: color, radius, spread, offsetX, offsetY |
| MCP `get_variable_defs` | Read-only **yes** for layer | Disabled Button returned `"--opacity-disabled": "50"` after bind |

**Scale trap:** `setValueForMode(id, 0.5)` → layer opacity ≈ 0.005. Use **50** for 50%. Confirmed: 12 → 0.12, 50 → 0.5, 100 → 1.

WEB code syntax **must** be `var(--opacity-50)` (the `var()` wrapper). Bare `--opacity-50` makes Dev Mode show raw numbers.

## How to use (layer — the working path)

```js
const opac = floats.find(v => v.name === 'opacity/disabled') // aliases Opacity/50
node.setBoundVariable('opacity', opac)
// scopes: ['OPACITY']  — never ALL_SCOPES
```

Prefer semantic aliases for intent (`opacity/disabled`, `opacity/scrim`). Snap other percents to `Opacity/{n}`.

## What not to convert

- **Radix A-steps** (`Color/{Hue}/{Light|Dark}/A1–A12`) — hue-specific alphas; they stay COLOR primitives.
- **`interaction/*` overlays** — already alias those A-steps; keep node opacity at 1 ([[interaction-state-semantics]]). `[state-layer]` paints may *read* `opacity: 0.1` as the resolved color alpha, not a second unbound field.
- **Paint opacity 0 on bound fills** — often “no fill” / transparent token, not a tokenizable alpha.

## Overlay ramps — pending write support

`Color/Overlay/Black/{5…100}` and `…/White/…` are baked RGBA, not aliases. The new UI feature is exactly “alias Black + bind `Opacity/50`.” Do not delete the Overlay tokens. Re-bind when MCP/API accepts color-variable opacity writes.

## SaaS PLM DS (o6o1ZuGHxDow2vHLuYXT6X) — applied 2026-09-03

**Created** in `Foundations / Primitives`: `Opacity/0,5,8,10,12,15,16,20,24,25,30,32,38,40,50,60,70,75,80,90,95,100` (FLOAT, scope `OPACITY`).

**Created** `Foundations / Semantics / Opacity`: `opacity/disabled`→50, `opacity/scrim`→80, `opacity/hover`→12, `opacity/focus`→24, `opacity/pressed`→32.

**Bound layer opacity on Components masters** (instances skipped): 22× `opacity/disabled`, 15× `Opacity/50` (mostly `[ring]` Focus), 8× `Opacity/20` (error rings), Radio disabled `Opacity/60`, Skeleton `Opacity/70`. Icons / Features / Layout / Token Spec / Cover / Stickersheet: no unbound non-instance layer opacities.

## Other 2026 Figma surfaces this workspace was missing

Dated; not the opacity job. Pointers only:

- **Slots GA** (2026-06-10): `component.createSlot()` exists in MCP runtime (returns `SLOT`). `figma.createSlot` is still undefined — [[figma-cli-authoring]] §6’s clone workaround is CLI-era, not the MCP path.
- **`extendLibraryCollectionByKeyAsync`** — extended collections (Enterprise).
- **TIMING / EASING** variable types; Motion namespace (`figma.motion`, `applyAnimationStyle`).
- **Shaders** as paint/effect `type: 'SHADER'`; MCP shader + generative-plugin tools.
- **Variable fonts:** `fontName.variationSettings`, `figma.getFontFamilyVariationAxes`.
- **`primaryAxisAlignItems`:** `SPACE_EVENLY` / `SPACE_AROUND`.
- **`textWrapStyle`:** `AUTO` / `BALANCE` / `PRETTY`.
- MCP extras on nodes: `query`, `set`, `screenshot`, `placeholder`.
