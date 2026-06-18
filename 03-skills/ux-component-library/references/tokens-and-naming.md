# Tokens & Naming — taxonomy grammar and purposeful naming

> How to **name and structure tokens** (and, by extension, components and props). Distilled from Nathan Curtis (*Reimagining a Token Taxonomy*, *Naming Tokens in Design Systems*, *Purposeful vs Aesthetic Naming*) + the W3C DTCG format. Companion to framework **§3 (the layered model)** and **§8c (visual-design dimensions)**.

---

## 1. The three tiers

| Tier | aka | Holds | Example |
|---|---|---|---|
| **Generic** | primitive / option | raw values | `$esds-color-neutral-42`, `$esds-space-2-x` (=32px) |
| **Semantic** | alias / decision | intent, points at a primitive | `$esds-color-feedback-error`, `$esds-font-size-heading-1` |
| **Component** | local | a component's own decisions | `$esds-input-left-icon-color-fill` |

**Aliasing:** semantic tokens reference generics (`ui-controls-color-text-error = color-feedback-error`). **Promotion rule:** start a token *inside* a component; promote it to semantic/global **only after repeated reuse** — never globalize prematurely.

## 2. The naming grammar

Assemble a token name left-to-right from four group-levels; include **only the levels needed** to express purposeful intent.

```
[NAMESPACE]        [OBJECT]              [BASE]                       [MODIFIER]
 System            Component-group       Category                     Variant
 Theme             Component             Concept                      State
 Domain            Element               Property                     Scale
                                                                      Mode
```

| Group | Sub-level | Example values |
|---|---|---|
| **Namespace** | System / Theme / Domain | `esds`,`slds` (≤5 chars) / `ocean`,`sands` / `consumer`,`retail` |
| **Object** | Component-group / Component / Element | `forms` / `input`,`button`,`tooltip` / `left-icon`,`notch` |
| **Base** | Category / Concept / Property | `color`,`space`,`size`,`font`,`elevation`,`time` / `feedback`,`action`,`heading` / `text`,`background`,`border`,`size`,`weight` |
| **Modifier** | Variant / State / Scale / Mode | `primary`,`success`,`error` / `default`,`hover`,`focus`,`disabled` / `1–5`,`50/100/900`,`s/m/l/xl` / `light`,`dark`,`on-light` |

**Worked decompositions:**
```
$esds-color-neutral-42                                  = System + Category + Concept + Scale
$esds-space-1-x                                         = System + Category + Scale
$esds-color-feedback-background-error                   = System + Category + Concept + Property + Variant
$esds-input-left-icon-color-fill                        = System + Component + Element + Category + Property
$esds-color-action-background-secondary-hover-on-light  = System + Category + Concept + Property + Variant + State + Mode
```

**Theme ≠ Mode.** `theme` (brand: ocean/sands) and `mode` (light/dark) are *orthogonal* axes — the reimagined taxonomy adds both (plus the `concept` level) precisely so dark mode + multi-brand stop fighting a shallow naming scheme.

## 3. Purposeful vs aesthetic naming

- **Purposeful (semantic):** self-documenting intent — `error`, `success`, `primary`, `new`.
- **Aesthetic (appearance):** literal visuals — `red`, `green`, `1X`.

**Decision rule (context-dependent, default to purpose):**
- **Favor purposeful** when components are *composed*, have *limited/known* use cases, or need *cross-context consistency* (e.g. `Alert` variant = `error`).
- **Consider aesthetic** when components are *atomic*, *decorative*, or need *visual variety* (e.g. a `Badge` color).

**The hard rule — never merge both into one enum.** No `variant: "error" | "red" | "success" | "green"`. It causes cognitive paralysis and fragmented consistency. *"Don't go there."*

**Why purpose wins long-term:** self-documenting · consistent across contexts · durable across redesigns/brand refreshes · accessibility baked in. *"Aesthetic props offer short-term flexibility but often lead to long-term debt; semantic investments pay off as systems grow."* The canonical failure: one brand `red` reused for brand identity, a sale indicator, AND an error — ambiguous the moment all three appear together. Split by purpose: `color-brand` / `color-commerce-sale` / `color-feedback-error`.

## 4. Nine authoring principles (use as lint rules)

1. Avoid homonyms (`type` vs `text`). 2. Homogeneity *within* a concept, heterogeneity *between* concepts. 3. Choose flexibility vs specificity deliberately. 4. Start within (local), then promote. 5. Don't globalize prematurely. 6. **Theme ≠ Mode.** 7. Decide explicit vs truncated defaults (include `on-light` or omit consistently). 8. Include or exclude modifying terms (readability vs brevity). 9. **Completeness:** include only the levels needed to distinguish purposeful intent.

## 5. The DTCG format (the machine substrate)

- A token is any object with `$value`; a group is one without. Reserved `$`-keys: `$value`, `$type`, `$description`, `$extensions`, `$deprecated`.
- **Types:** primitives (`color`, `dimension`, `fontFamily`, `fontWeight`, `duration`, `cubicBezier`, `number`) + composites (`typography`, `shadow`, `border`, `transition`, `gradient`, `strokeStyle`).
- **Aliases:** `{group.token}` dot-path; chained ok, circular invalid.
- `$type` inherits down groups. Names must not start with `$` or contain `{ } .`; case-sensitive.

```json
{ "color": { "$type": "color",
    "blue-600": { "$value": "#2D76D4" },
    "action": { "primary": { "$value": "{color.blue-600}", "$description": "Primary CTAs and links" } } } }
```

This is what makes a token round-trip: **DTCG `tokens.json` ⇄ Figma variables ⇄ Tailwind theme ⇄ `DESIGN.md` frontmatter.**

## 6. Worked example — Centric C8 PLM's two-tier system

C8 PLM (the Phase-3 `DESIGN.md` example) runs exactly this model, shadcn/Radix-lineage:

- **Primitive (palette):** `--cds-blues-blue600: #2D76D4`, `--cds-grays-gray300`, `--cds-spacing-16: 16px`, `--cds-radius-medium: 8px`. Static; same value in every theme.
- **Semantic (intent):** `--sem-primary`, `--sem-destructive`, `--sem-muted`, `--sem-border`, `--sem-ring`, each with a `*-foreground` pair. Maps to one primitive in light mode, another in dark.
- **The contract:** *components consume only the semantic layer.* "Hardcoding a hex or reaching for a primitive inside a component bypasses dark mode and breaks the theming contract." Concept→hue map worth noting: blue = primary/info, green = success, red = danger, orange = warning, yellow = caution, cyan = secondary info, **purple = beta/AI/experimental**, pink = reserved/marketing.

The lesson for any system: **primitives are aesthetic-named (`blue-600`); semantic tokens are purpose-named (`primary`, `destructive`); components only ever touch the purpose layer.**

## 7. Relationships
- **Up:** framework [[09-component-and-pattern-framework]] §3 (tiers), §8c (which dimensions a component resolves).
- **Across:** `component-authoring.md` (the `default`/`variants` blocks reference these tokens); `ai-ready-design-systems.md` (DESIGN.md frontmatter *is* a token export; "reasonable-English" naming for agents).
