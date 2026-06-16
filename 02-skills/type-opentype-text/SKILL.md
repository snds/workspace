---
name: type-opentype-text
description: >
  OpenType features for text typefaces — ligatures, figure styles, alternate
  characters, contextual forms, and their correct application in design systems
  and CSS. Use this skill whenever the conversation involves: standard ligatures
  (fi, fl), figure styles (tabular lining, oldstyle, proportional), small caps
  (smcp), case-sensitive forms (case), disambiguation alternates (cv01, cv02,
  0/O/l/I/1 disambiguation), fractions (frac), contextual alternates (calt),
  which OpenType features belong in design system text style tokens, how to
  enable OpenType features in CSS (font-feature-settings), which features should
  be on by default, or why a font feature is or is not working. Spoke of
  `lead-type-designer`. For icon font GSUB/CALT/liga in pictographic glyph
  contexts, use `variable-icon-font-architect`/`opentype-layout-engineering`.
---

# Type OpenType Features for Text

Specialist lens for OpenType features in text typefaces and their correct
application. Part of the `lead-type-designer` skill network.

---

## Domain Boundary

This skill covers **OpenType features for text typefaces** — the functional
extensions beyond basic letterforms that improve readability, typographic
quality, and information clarity.

- **Icon font GSUB/GPOS/CALT**: → `variable-icon-font-architect`/`opentype-layout-engineering`
- **OpenType table construction (the .fea file, GSUB table structure)**: → `variable-icon-font-architect`/`opentype-layout-engineering`
- **Font pipeline compilation**: → `variable-icon-font-architect`/`fonttools-ufo-internals`
- **Design system text tokens**: → `ds-advisor` (this skill provides the feature knowledge; ds-advisor handles the token architecture)

---

## Ligatures

Ligatures are single glyphs that replace a sequence of characters to improve
visual harmony and prevent awkward collisions.

### Standard Ligatures (liga)

**Status: ON by default.** Should be enabled in all text styles.

The essential text ligatures:
- **fi** — the dot of 'i' collides with the terminal or top of 'f'; replaced by a unified glyph
- **fl** — similar to fi; 'f' top and 'l' ascender create a collision
- **ffi** — triple collision resolved
- **ffl** — triple collision resolved
- **ft** — some designs; the crossbar of 't' can collide with the f terminal
- **fb, fh, fj, fk** — found in some type families; collision prevention

**Note**: In many modern sans-serif typefaces, the 'f' has a curved terminal that
naturally clears the following dotted letter — ligatures may not be needed. In
serif and humanist faces with an overhanging 'f' terminal, liga is critical.

**CSS**: `font-feature-settings: 'liga' 1` (also implicit in `font-variant-ligatures: common-ligatures`)

### Discretionary Ligatures (dlig)

**Status: OFF by default.** Opt-in for decorative use.

Historical or stylistic ligatures that are not functionally required:
- **ct** — calligraphic flourish
- **st** — archaic connecting form
- **Th** — uppercase-lowercase connection
- **sp, si, sl** — found in some calligraphic faces

Use only in display contexts where a more ornate or historical register is
intended. Do not enable in body text — disrupts reading rhythm.

**CSS**: `font-feature-settings: 'dlig' 1`

---

## Figure Styles

Figures have four variants that combine into pairs. Understanding all four and
when each is correct is fundamental to typographic quality — especially in UI
and data contexts.

### The Two Dimensions

**Height**:
- **Lining figures (lnum)**: All figures align to the cap line and baseline — same height as capital letters. Authoritative, formal, tabular-ready.
- **Oldstyle figures (onum)**: Figures of varying heights — some ascend (6, 8), some descend (3, 4, 5, 7, 9), most sit at x-height (0, 1, 2). Better integrated with lowercase text; more humanist and informal. Also called "text figures" or "ranging figures."

**Width**:
- **Proportional figures (pnum)**: Each figure has its natural, proportional width. Better for flowing text where figures appear within words or sentences.
- **Tabular figures (tnum)**: All figures have identical advance widths. Critical for any numeric data that stacks vertically — ensures columns align precisely.

### The Four Combinations

| Combination | Feature code | Use case |
|---|---|---|
| Proportional oldstyle | `pnum onum` | Body text with occasional numbers; literary, editorial |
| Tabular lining | `tnum lnum` | **Financial tables, data grids, price lists** — use this everywhere numbers stack |
| Proportional lining | `lnum` (default in many fonts) | All-caps contexts, headings, formal presentation |
| Tabular oldstyle | `tnum onum` | Rare; running text tables where oldstyle is preferred |

**Critical rule for design systems**: Any text style that displays numeric data
in a tabular or column context **must** enable `tnum lnum`. This includes:
price columns, data tables, stat cards, numeric dashboards, financial summaries.

**Anti-pattern**: Using default (proportional) figures in a data table. Numbers
will not align vertically even when they appear to be the same size, because the
advance widths vary. The column appears to wobble.

**CSS**: `font-feature-settings: 'tnum' 1, 'lnum' 1`

---

## Small Caps (smcp, c2sc)

### What Small Caps Are

Genuine drawn small caps are **not scaled-down capitals**. They are letterforms
designed at the x-height with proportional stroke weights that match the lowercase
at that size. Mechanically scaled-down caps have too-thin strokes and too-tight
spacing — they look like mistakes.

- **smcp**: Replaces lowercase letters with small caps — `a, b, c` → SC forms
- **c2sc**: Replaces capital letters with small caps — `A, B, C` → SC forms
- Often used together: `smcp c2sc` converts all letters to small caps

### When to Use Small Caps

- Section labels and subheadings in editorial/book typography
- Acronyms and abbreviations within body text (NASA, HTML, WHO — small capped in running text)
- All-caps titles set in small caps instead of full caps for elegance
- First word or first few characters of a chapter (drop-cap lead-in)

**DS context**: Design system label and tag components that use all-caps text
benefit from genuine small caps when the typeface provides them. The result is
more refined than all-caps full-size text.

**CSS**: `font-variant-caps: small-caps` or `font-feature-settings: 'smcp' 1`

---

## Case-Sensitive Forms (case)

Punctuation and symbols are designed to sit in context with lowercase text.
When set in all-caps, many symbols appear to hang too low:

- Parentheses `()` and brackets `[]` — designed to align with lowercase ascenders/descenders
- En dash, em dash — vertical position assumes mixed case context
- Hyphens, slashes, mathematical operators

**case feature**: Substitutes vertically centered versions of these symbols for
all-caps settings. The symbols are raised to optically center within the cap height.

**DS context**: Enable `case` in any text style where content is all-caps — button
labels, navigation items, badge text, uppercase tags. Without it, parentheses in
all-caps labels appear to hang below the baseline.

**CSS**: `font-feature-settings: 'case' 1` (typically combined with uppercase text)

---

## Character Variants (cvXX)

Character variants provide alternate designs for individual characters. Most
commonly used for **disambiguation** — distinguishing visually similar characters
that can cause reading errors:

| Characters | Problem | CV feature |
|---|---|---|
| 0, O | Zero vs. uppercase O | `cv01` (slashed zero or dotted zero) |
| I, l, 1 | Capital I, lowercase l, numeral 1 | `cv02` (seriffed I, distinctive l, etc.) |
| i, j (without dots) | May resemble l in sans-serif | Varies by font |

### DS Context for Disambiguation

In data-dense UI contexts — financial applications, developer tools, data grids,
analytics dashboards — ambiguous characters cause real errors. A slashed zero
(`cv01`) in a financial account number prevents misreading '0' as 'O'. A distinctive
'I' vs. 'l' vs. '1' in a code or ID context prevents transcription errors.

**Design system recommendation**: Create a separate `data` or `code` text style
variant with disambiguation alternates enabled by default. Do not enable them for
editorial body text (where slashed zeros look technical and out of place).

**CSS**: `font-feature-settings: 'cv01' 1, 'cv02' 1`

**Accessibility implication**: Disambiguation variants are a functional accessibility
decision for users with visual impairment, dyslexia, or cognitive processing
differences. Route to `lead-accessibility-architect`/`a11y-visual` for the full
accessibility case.

---

## Contextual Alternates (calt)

CALT substitutes glyph variants based on surrounding characters — the glyph
changes depending on what comes before or after it.

### Text type uses of calt

- **Connecting forms**: Some calligraphic and script typefaces use calt to connect
  adjacent letters naturally
- **Contextual swashes**: Terminal swashes that appear only at word-end positions
- **Alternate 'a'**: Some humanist faces substitute a one-story 'a' in italic contexts
- **Stylistic connections**: Alternate 'g', 'y', 'f' when followed by specific letters

**Status**: Typically ON by default when a font includes calt.

**CSS**: `font-feature-settings: 'calt' 1` (browsers often enable by default)

---

## Fractions (frac)

The `frac` feature converts a slash-separated digit sequence into a typographic
fraction with superior numerator and inferior denominator:

`1/2` → `½` (properly formatted, not a precomposed character)

When to enable:
- Recipe contexts
- Measurement specifications (woodworking, cooking, fabric)
- Technical documentation with fractional dimensions

**DS context**: Enable in body text styles for recipe/measurement content. Keep
off in data table contexts where `1/2` may be a literal string, not a fraction.

**CSS**: `font-feature-settings: 'frac' 1`

---

## Superscript and Subscript (sups, subs, ordn)

- **sups**: Drawn superscripts — mathematically proportioned for the font's weight
- **subs**: Drawn subscripts
- **ordn**: Ordinal indicators (1st, 2nd, 3rd → 1ˢᵗ, 2ⁿᵈ, 3ʳᵈ using proper ordinal forms)

**Important**: These are not the same as CSS `vertical-align: super/sub` with
scaled text. Font-level superscripts are drawn at the correct weight for the
superscript position — CSS scaling produces too-thin superscripts.

---

## OpenType Features in Design Systems

### Feature Defaults by Style Category

| DS text style | Recommended features ON | Notes |
|---|---|---|
| Body text | `liga`, `kern` | Standard; let the font do its job |
| Heading/display | `liga`, `kern`, `case` (if caps) | dlig optionally for display |
| Numeric / data | `tnum lnum`, `liga`, `kern`, `cv01` | Tabular lining + slashed zero |
| All-caps labels/buttons | `case`, `kern`, `tnum lnum` (if numeric) | case for centered punctuation |
| Code/ID display | `tnum`, `cv01`, `cv02` | Disambiguation critical |
| Small caps subheadings | `smcp c2sc`, `kern`, `tnum lnum` | Genuine SC, not fake |

### CSS Implementation

```css
/* Body text — standard */
body {
  font-feature-settings: 'liga' 1, 'kern' 1;
  font-variant-ligatures: common-ligatures;
  font-kerning: normal;
}

/* Data table — tabular lining with disambiguation */
.data-cell {
  font-feature-settings: 'tnum' 1, 'lnum' 1, 'cv01' 1;
  font-variant-numeric: tabular-nums lining-nums;
}

/* All-caps label — case-sensitive punctuation */
.label-caps {
  text-transform: uppercase;
  font-feature-settings: 'case' 1, 'kern' 1;
  letter-spacing: 0.06em;
}

/* Small caps heading */
.subheading-smallcaps {
  font-variant-caps: small-caps;
  font-feature-settings: 'smcp' 1, 'c2sc' 1, 'kern' 1;
}
```

**Modern CSS**: `font-variant-*` properties are the high-level API; `font-feature-settings`
is the low-level override for features not covered by `font-variant-*`. Prefer
`font-variant-numeric: tabular-nums lining-nums` over `font-feature-settings: 'tnum' 1, 'lnum' 1`
when browser support allows — it's more readable and survives font stack changes.

---

## Anti-Patterns and Failure Modes

| Anti-pattern | Symptom | Fix |
|---|---|---|
| Default figures in data columns | Numbers don't align vertically in tables | Enable `tnum lnum` on all numeric text styles |
| Fake small caps (CSS scale transform) | SC strokes too thin, spacing too tight | Use genuine `smcp` feature or choose a font that includes drawn small caps |
| No `case` on all-caps labels | Parentheses in button labels hang low | Enable `case` feature on uppercase text styles |
| dlig enabled in body text | Unexpected ligature substitutions disrupt reading | Disable `dlig`; it's display-only |
| Disambiguation variants on editorial body | Slashed zeros look technical in prose | Split into separate data/code style variant |
| `font-feature-settings` on body overrides everything downstream | Child elements lose feature settings | Specify features per component, not globally on body |
| No kerning specified | Headline type has obvious gaps (AV, AT) | Ensure `font-kerning: normal` and `kern` feature are active |

---

## Cross-Links

- `variable-icon-font-architect`/`opentype-layout-engineering` — OpenType table construction, .fea file syntax, GSUB substitution mechanics (shared foundational knowledge)
- `variable-icon-font-architect`/`fonttools-ufo-internals` — Python-level font table inspection when feature behavior is unexpected
- `type-spacing-metrics` — kerning is implemented as GPOS; tnum is a spacing decision as much as a feature decision
- `type-multi-script` — Arabic and Indic scripts have dramatically more complex OpenType feature requirements than Latin
- `ds-advisor` — encoding OpenType features in design system text style tokens; which features belong at the component level vs. the token level
- `lead-ui-designer`/`uid-type-for-screens` — feature availability in web fonts; font subsetting can strip features if not explicitly included
- `lead-accessibility-architect`/`a11y-visual` — disambiguation variants (cv01, cv02) as accessibility decisions
