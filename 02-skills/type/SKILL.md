---
name: type
description: >-
  Typography hub — type systems for screens and type design/letterform craft. Use when
  the user wants to define or evaluate type: build a type scale, choose/pair typefaces,
  set a typographic system (sizes, leading, measure, tracking), tune OpenType features,
  work with variable fonts, set multi-script text, or reason about letterform
  construction and spacing/metrics. Trigger on "build a type scale", "pair these
  typefaces", "set the typography system", "fix the line-height/measure", "OpenType
  features", "variable font axes", "kerning/spacing", "typeset this", "type for screens".
  Also the explicit entry point for the `/type` operation grammar
  (`/type <verb> <target> [--modifiers]`). Canonical owner of typography routing;
  delegates to the type-* skills, lead-type-designer, gd-typography, and uid-type-for-screens.
  Not for icon-font/variable-icon work (use variable-icon-font-architect), not for
  judging a rendered page's type (use /qa), and not for general DS token decisions
  (use /ds — though type tokens are shared territory; this hub owns the type-scale logic).
user-invocable: true
argument-hint: "[spec|audit|generate|document] [target: type-system|font-file|component|url|copy] [--lens scale|pairing|metrics|opentype|variable|multiscript|screen] [--out <path>] [--dry]"
license: Apache-2.0
metadata:
  hub: true
  family: typography
  poc: false
  version: 0.1.0
aliases: [type]
spec_version: "2.0"
---

# /type — Typography Hub

Two altitudes under one roof: **type systems for screens** (scale, pairing, rhythm,
readability) and **type design craft** (letterform construction, spacing/metrics,
OpenType, variable axes, multi-script). It is a **wrapper** (three-way-contract wrapper
layer): it owns trigger vocabulary, verb dispatch, and lens routing, then delegates depth
to the `type-*` family, `lead-type-designer`, `gd-typography`, and `uid-type-for-screens`.
It never duplicates a base's knowledge.

## Operation grammar

```
/type <verb> <target> [--modifiers]
```

- **verb** — a canonical Produce/Inspect verb (below). Omitted → `spec`.
- **target** — a type system, a font file, a component/URL, or a block of copy.
- **modifiers** — `--lens` (which sub-domain leads), `--out`, `--dry`.

Conversational invocation maps in: "build a type scale for the docs site" →
`/type spec type-system --lens scale`.

### Verbs (hub subset)

| Verb | Meaning here | Default base route |
|---|---|---|
| `spec` | Define a type system: scale, pairing, leading/measure/tracking, weights, responsive steps | `gd-typography` + `uid-type-for-screens` + `type-typesetting` |
| `audit` | Evaluate type against a standard — scale coherence, measure (45–75ch), hierarchy levels, contrast, readability | `uid-type-for-screens` + `type-spacing-metrics` (measured) |
| `generate` | Scaffold the artifact: CSS/token type scale, `@font-face` setup, variable-font `font-variation-settings`, OpenType feature config | `type-variable-text` · `type-opentype-text` + `fe-design-tokens` |
| `document` | Author the type docs/teaching entry (scale rationale, usage, do/don't) | `type-classification-history` for grounding + docs |

### Lens routing (`--lens`, else inferred)

| Lens | Lead base |
|---|---|
| `scale` | `gd-typography` (modular scale, ratio) + `uid-type-for-screens` |
| `pairing` | `type-classification-history` · `lead-type-designer` |
| `metrics` | `type-spacing-metrics` · `type-letterform-construction` |
| `opentype` | `type-opentype-text` |
| `variable` | `type-variable-text` (+ `math-interpolation-designspace` for axes) |
| `multiscript` | `type-multi-script` |
| `screen` | `uid-type-for-screens` (rendering, hinting, anti-aliasing, viewing context) |

## Disambiguation — who owns what (the precision contract)

`/type` is the canonical owner of **typography**. Defer when a request crosses the line:

- **Icon fonts / variable *icon* fonts / glyph construction for symbols** → `variable-icon-font-architect` (the icon-font hub). `/type` is text type, not icon glyphs.
- **Judging a rendered page's type** (contrast, hierarchy, "does this read well") → `/qa` (`--lens ui`/`graphic`).
- **System token architecture** (where type tokens live in the tier model) → `/ds`. Type tokens are shared territory; `/type` owns the *scale logic + values*, `/ds` owns the *tier placement + governance*.
- **Font sourcing/scraping** → `google-fonts-scraper` / `svg-font-extraction`.

## Shared report format

For `audit`, return the cross-hub shape (findings · severity · fix · owner · summary ·
next) with measured values (scale ratio consistency, measure in ch, distinct hierarchy
levels, body contrast). For `spec`/`generate`, return the system (scale table, pairings,
rhythm tokens) and where it's emitted.

## Execution protocol

1. **Parse** verb/target/modifiers; default `spec`; auto-`--lens` from the target/intent.
2. **`--dry`?** Report the bases + checks and stop.
3. **Route** to the lead base by lens; attach `type-spacing-metrics` for measured audits, `fe-design-tokens` when emitting a token scale.
4. **Acquire** the target (system brief / font-file metrics / rendered sample / copy).
5. **Run** the base procedure. Prefer measured (ratios, ch-measure, level counts) over eyeballed.
6. **Emit** the report; write to `--out` if given.
7. **Hand off**: token tier placement → `/ds`; rendered-type judgment → `/qa`; icon glyphs → `variable-icon-font-architect`.

## POC scope note

Sibling to `/qa`, cloned from the same wrapper shape per `invokable-operations-spec_v0.2`.
Thin by design: the `type-*` skills + `gd-typography` + `lead-type-designer` hold the depth.
