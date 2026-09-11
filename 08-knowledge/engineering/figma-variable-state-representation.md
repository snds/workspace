---
tags: [figma-plugin, figma-variables, design-tokens, cva, state-representation, engineering]
created: 2026-05-23
updated: 2026-09-03
status: validated
confidence: high
sources: [session-log 2026-05-23, figma-repo-sync-plugin Bundles 11.3.49–70]
related_skills: [figma-plugin-dev, design-engineer, ds-advisor]
related_projects: [figma-repo-sync-plugin]
---

# Figma variable resolution + CVA variant×state representation

Hard-won mechanics from landing the state-representation pattern in
figma-repo-sync-plugin (Bundles 11.3.49–70). Complements [[figma-plugin-patterns]].
Full spec: `07-projects/09-figma-repo-sync-plugin/docs/2026-05-23-state-representation-decision-tree.md`.

## Figma variable mechanics (validated constraints)

1. **Modes are a mutually-exclusive vertical slice per collection.** Changing a
   collection's mode swaps the value each variable resolves to. There is no
   "multiplexing" — it's the standard, valid design-system pattern (Uber et al.).
   A single paint binds ONE variable resolved through ONE collection's mode.

2. **A color can be a function of `variant` OR `state` via modes — not both.**
   Two mode-axes can't drive the same paint. When a component has BOTH variant
   and visual states, make exactly ONE axis **physical** (real Figma component
   variants); the other stays modes. Make the SMALLER axis physical to minimize
   component count — usually states (fewer than variants).

3. **Layer opacity IS variable-bindable; paint/color-var opacity is not (yet) via
   MCP/`use_figma`.** `node.setBoundVariable('opacity', floatVar)` works; FLOAT
   values are **0–100**. The 2026-09-03 UI can bind a number var to a color
   variable’s opacity and to fill opacity without detaching — Plugin/MCP writes
   still reject that (see [[figma-opacity-variables]]). This **refutes** the
   2026-05 claim that opacity cannot be bound at all. For `/N` (e.g.
   `bg-primary/80`) until paint-opacity writes ship: bake alpha into a COLOR
   token (Radix A-steps / `interaction/*`) or use a normalized **state-layer**.

4. **`resolvedVariableModes` + `resolveForConsumer(node)` are the AUTHORITATIVE
   resolution.** A pin-heuristic that walks `node→ancestor→page` for
   `explicitVariableModes` gives FALSE positives because page-level pins don't
   propagate into instance interiors the way you'd assume. To know what Figma
   actually resolves, ask Figma — don't reimplement its resolver.

5. **Selection Colors `(?)` ≠ broken binding.** A `(?)` next to a variable in
   multi-selection means it **resolves to >1 distinct value across the
   selection** (expected for a Light/Dark or per-variant token selected en
   masse). Verify with the per-node resolution APIs before "fixing" it.

## The black-default trap (root cause of a long (?) chase)

A resolver that returns opaque black `{0,0,0,1}` on every failure path is
poison: it (a) bakes plausible-looking black under otherwise-correct bindings
and (b) makes genuine failures indistinguishable from a real black token. Fixes:
seed the literal from the token's known hex; emit a LOUD sentinel (hot magenta)
+ warn on true unresolvable; and make mode lookups degrade (requested mode →
collection default → first populated mode) so a cross-collection modeId can't
fall straight to the failure default.

## The state-representation pattern (decision B — normalized state-layer)

- **Axes:** `variant` + `size` → modes; `state` + `type` (icon-slot structural)
  → physical component variants. Full `Type × State` matrix, no ceiling.
- **State visuals = overlay nodes**, not rebound base fills (base stays pristine):
  - hover/focus/pressed → a `[state-layer]` overlay: fill bound to the variant's
    `foreground` (on-color, mode-driven → self-adapting contrast + free dark
    mode), node opacity uniform per state (hover 12 / focus 24 / pressed 32%).
  - focus + error → a dedicated `[ring]` STROKE overlay: parent-matched,
    offset outward, pinned all sides — ONE consistent ring model everywhere.
  - disabled → 50% whole-element layer opacity. error → border rebind +
    destructive ring.
- **State-layer color = `foreground`** beats white/black (degenerate; needs
  luminance branching) and tier tints (need per-variant tokens + dark inversion).
- **Why an overlay can't fully port shadcn's `/80` hovers:** `/80` = the fill
  itself goes translucent (page shows through); an opaque overlay can't
  reproduce that. The normalized state-layer is a deliberate *reinterpretation*
  of source hover values, not a faithful transliteration — an accepted DS call.

## Variable naming (DX affordance)

Grouped `<slot>/<state>` with an EXPLICIT `default` (`background/default`,
`background/hover`, `ring/focus`) so `/` renders collapsible folders in the
variables panel. The `default` segment is a **structural affordance, not a
code-derived name** (the resting state has no Tailwind modifier) — this MUST be
documented for engineers in the in-Figma + Storybook docs, or they'll wonder why
`default` exists.

## Single-source-of-truth + migration seam

Derive the parse-time literal palette FROM the foundation token table (one
place to edit) rather than hand-duplicating. Leave a documented single swap
point so an authoritative generated palette (OKLCh + APCA `palette.generated.css`)
can later slot in without touching consumers — but coordinate the actual
migration (values diff + binding-preservation + non-breaking path) with the
owning engineers, don't unilaterally adopt a generated source.

## Meta-lesson

When the canvas disagrees with a heuristic-based scanner, trust the canvas and
make the scanner authoritative — never declare "clean" on a heuristic the user
can visibly contradict. (Cost a few wasted "all clear" claims before switching
to `resolveForConsumer`.)
