---
name: fe-i18n
description: >
  Internationalization and localization engineering for frontend applications at
  staff/principal IC level. Use this skill whenever the conversation touches:
  i18n vs. l10n distinction, BCP 47 locale identifiers, ICU message format
  (plural categories, select pattern, nested messages), MessageFormat 2 (MF2),
  JavaScript Intl API (DateTimeFormat, NumberFormat, RelativeTimeFormat,
  ListFormat, Collator, PluralRules), Intl polyfills (@formatjs), RTL layout
  (CSS Logical Properties, dir attribute, BiDi algorithm, icon mirroring rules),
  font support for CJK or Arabic/Hebrew scripts, Unicode range subsetting,
  translation workflow (string extraction, key naming, translation management
  systems), pseudo-localization testing, locale-sensitive date/time/number
  formatting, IANA timezone database, Temporal API, or UTC storage with locale
  display. Libraries: react-intl, vue-i18n, angular/localize, i18next.
  Not for: backend locale-aware API design (be-api-design), typography system
  design for multi-script (type-multi-script), or screen reader language
  metadata (a11y-auditory).
hub: lead-frontend-engineer
aliases: [fe-i18n]
tier: spoke
domain: engineering
prerequisites: [lead-frontend-engineer]
spec_version: "2.0"
---

# Fe: i18n

Specialist lens for internationalization and localization engineering in frontend
applications. Part of the frontend engineering skill network.

---

## Domain Boundary

This skill owns: **i18n architecture, ICU message format, JavaScript Intl API,
RTL layout, multilingual font support, translation workflow, pseudo-localization
testing, and locale-sensitive data formatting**.

- Locale-aware API design (accepting `Accept-Language`, returning locale data) → `be-api-design`
- Multi-script typography design decisions → `type-multi-script`
- Screen reader language attribute behavior → `a11y-auditory`
- Component architecture that i18n slots into → `fe-component-architecture`

---

## i18n Architecture

### i18n vs. l10n

- **i18n (internationalization)**: making software capable of supporting any locale.
  Engineering concern. Done once, done at architecture time, cannot be retrofitted
  without significant rework.
- **l10n (localization)**: adapting software to a specific locale — translations,
  date formats, currency display, imagery. Repeated per locale.

**Why i18n must be baked in from the start**: every hardcoded string, every
date formatted with `.toLocaleDateString()` without a locale argument, every
left-aligned layout with `margin-left` is an i18n debt item. Retrofitting i18n
into a large codebase is one of the most painful refactors in frontend engineering.
The rule: never ship a string literal in UI code; never format a date without a
locale.

### The Locale Identifier System — BCP 47

Format: `language[-script][-region][-extensions]`

```
en          — English (no region or script specified)
en-US       — English, United States
en-GB       — English, United Kingdom
zh-Hans     — Chinese, Simplified script
zh-Hant     — Chinese, Traditional script
zh-Hans-CN  — Chinese, Simplified, China
zh-Hant-TW  — Chinese, Traditional, Taiwan
ar-SA       — Arabic, Saudi Arabia
pt-BR       — Portuguese, Brazil
pt-PT       — Portuguese, Portugal
sr-Cyrl     — Serbian, Cyrillic script
sr-Latn     — Serbian, Latin script
```

Use BCP 47 tags everywhere: in HTML `lang` attribute, in `Intl` constructors, in
translation file naming, in HTTP `Accept-Language` headers. Never invent your
own locale identifier format.

---

## ICU Message Format

ICU MessageFormat is the standard for expressing translatable strings that include
variable data, pluralization, and gender agreement. It is the lingua franca of i18n
libraries — react-intl, vue-i18n (v9+), i18next-icu, and angular/localize all
support it.

### Plural Categories

CLDR (Common Locale Data Repository) defines six plural categories: `zero`, `one`,
`two`, `few`, `many`, `other`. Which categories a language uses:

| Language | Categories used |
|----------|----------------|
| English | `one` (n=1), `other` (everything else) |
| French | `one` (n=0,1), `other` |
| Russian | `one` (n=1,21,31…), `few` (n=2-4,22-24…), `many` (n=5-20…), `other` |
| Arabic | `zero`, `one`, `two`, `few` (3-10), `many` (11-99), `other` |
| Japanese | `other` (no plural distinction) |
| Welsh | All six categories |

ICU plural syntax:

```
{count, plural,
  =0    {No items}
  one   {# item}
  other {# items}
}
```

The `#` is replaced by the formatted count value. `=0` is an exact match override —
it takes priority over the `zero` category, which is useful for "No items" vs.
"0 items" phrasing.

### Cardinal vs. Ordinal Plurals

Cardinal: how many (1 item, 2 items). `{n, plural, ...}`

Ordinal: which position (1st, 2nd, 3rd). `{n, selectordinal, one {#st} two {#nd} few {#rd} other {#th}}`

Ordinal categories differ by language — English has `one/two/few/other`, French
has different ordinals. Always use `selectordinal` for ranked positions, never
hardcode English ordinal suffixes.

### Select Pattern — Gender and Grammatical Agreement

```
{gender, select,
  male   {He updated his profile.}
  female {She updated her profile.}
  other  {They updated their profile.}
}
```

`select` works for any discrete string-keyed selection, not just gender. Use it
for any case where the translation varies by a category that isn't a number.

### Nested ICU Messages

```
{count, plural,
  one   {{gender, select,
    male   {He added # item to his cart.}
    female {She added # item to her cart.}
    other  {They added # item to their cart.}
  }}
  other {{gender, select,
    male   {He added # items to his cart.}
    female {She added # items to her cart.}
    other  {They added # items to their cart.}
  }}
}
```

Nesting works but creates translator cognitive load. Keep nesting to two levels
maximum. When a message requires more, consider restructuring the UX copy.

### MessageFormat 2 (MF2)

The successor to ICU MessageFormat, currently in CLDR finalization and gaining
library support. Key changes:

```
// MF2 syntax (different from ICU)
.input {$count :number}
.match $count
1   {{You have {$count} message.}}
*   {{You have {$count} messages.}}
```

MF2 is cleaner, more extensible, and handles bidirectional text embedding better.
Not yet supported across all major i18n libraries as of 2026, but track adoption
in react-intl and i18next — it will be the migration target.

### Library Support

| Library | Framework | ICU support | MF2 |
|---------|-----------|------------|-----|
| react-intl (@formatjs) | React | Full | Experimental |
| vue-i18n v9+ | Vue 3 | Full | Roadmap |
| angular/localize | Angular | Full (compile-time) | Roadmap |
| i18next + i18next-icu | Framework-agnostic | Via plugin | Planned |

---

## JavaScript Intl API

The `Intl` namespace provides locale-sensitive formatting without a library
dependency. Use it for all date, number, and list formatting. Never format
dates or numbers via string concatenation.

### `Intl.DateTimeFormat`

```javascript
// Basic usage — locale-sensitive date
new Intl.DateTimeFormat('en-US', { dateStyle: 'long' }).format(new Date())
// → "April 28, 2026"

new Intl.DateTimeFormat('de-DE', { dateStyle: 'long' }).format(new Date())
// → "28. April 2026"

// Fine-grained control
new Intl.DateTimeFormat('ja-JP', {
  year: 'numeric', month: 'long', day: 'numeric',
  hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Tokyo'
}).format(new Date())
// → "2026年4月28日 14:23"

// timeZone is required for server-rendered dates — never omit it
```

### `Intl.NumberFormat`

```javascript
// Currency
new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(1234.5)
// → "$1,234.50"

new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(1234.5)
// → "1.234,50 €"

// Percentage
new Intl.NumberFormat('en-US', { style: 'percent', maximumFractionDigits: 1 }).format(0.856)
// → "85.6%"

// Compact notation
new Intl.NumberFormat('en-US', { notation: 'compact' }).format(1500000)
// → "1.5M"
```

### `Intl.RelativeTimeFormat`

```javascript
const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });
rtf.format(-1, 'day')  // → "yesterday"
rtf.format(-3, 'hour') // → "3 hours ago"
rtf.format(2, 'day')   // → "in 2 days"
```

### `Intl.ListFormat`

```javascript
new Intl.ListFormat('en', { style: 'long', type: 'conjunction' })
  .format(['Alice', 'Bob', 'Carol'])
// → "Alice, Bob, and Carol"

new Intl.ListFormat('zh', { style: 'long', type: 'conjunction' })
  .format(['Alice', 'Bob', 'Carol'])
// → "Alice、Bob和Carol"  ← Chinese list separator
```

### `Intl.Collator`

```javascript
// Locale-sensitive string sorting — not .sort() with string comparison
const collator = new Intl.Collator('de', { sensitivity: 'base' });
['Ü', 'u', 'ü', 'U'].sort(collator.compare)
// German: treats ü/u as equivalent for sorting; English would not
```

### `Intl.PluralRules` for Custom Pluralization

```javascript
const pr = new Intl.PluralRules('ar');
pr.select(0)  // → "zero"
pr.select(1)  // → "one"
pr.select(2)  // → "two"
pr.select(5)  // → "few"
pr.select(15) // → "many"
pr.select(100)// → "other"
```

### Polyfill Situation

`Intl` is well-supported in modern browsers but some APIs are missing in older
environments. The `@formatjs` package family provides ponyfills that match the
spec exactly:

```
@formatjs/intl-relativetimeformat   — RelativeTimeFormat for Safari < 14
@formatjs/intl-listformat           — ListFormat for older Safari
@formatjs/intl-numberformat         — Full NumberFormat for Safari < 14.1
@formatjs/intl-datetimeformat       — DateTimeFormat with full options support
```

Load polyfills conditionally:

```javascript
if (!Intl.RelativeTimeFormat) {
  await import('@formatjs/intl-relativetimeformat/polyfill');
  await import('@formatjs/intl-relativetimeformat/locale-data/en');
}
```

---

## RTL Layout

### CSS Logical Properties — The Right Way to Write Layout

Never write directional properties (`margin-left`, `padding-right`, `border-left`,
`left`, `right`, `text-align: left`) in components. Always use logical properties:

| Physical (avoid) | Logical (use) | Meaning |
|-----------------|--------------|---------|
| `margin-left` | `margin-inline-start` | Leading edge of inline axis |
| `margin-right` | `margin-inline-end` | Trailing edge of inline axis |
| `padding-top` | `padding-block-start` | Leading edge of block axis |
| `padding-bottom` | `padding-block-end` | Trailing edge of block axis |
| `border-left` | `border-inline-start` | Leading border |
| `width` | `inline-size` | Size along inline axis |
| `height` | `block-size` | Size along block axis |
| `top` | `inset-block-start` | Block-axis position |
| `left` | `inset-inline-start` | Inline-axis position |
| `text-align: left` | `text-align: start` | Start of inline axis |
| `float: left` | `float: inline-start` | Float to inline start |

In LTR contexts, `inline-start` = left. In RTL contexts, `inline-start` = right.
CSS Logical Properties handle the flip automatically without any JS.

Browser support: excellent in all modern browsers. Use a PostCSS plugin to
transform logical properties for IE11 if still required.

### `dir` Attribute

```html
<!-- Document level — sets the base direction for the entire page -->
<html lang="ar" dir="rtl">

<!-- Component level — useful for mixed-direction content -->
<blockquote dir="rtl" lang="ar">...</blockquote>

<!-- Override direction for a specific element -->
<span dir="ltr">https://example.com</span>  <!-- URLs should be LTR even in RTL pages -->
```

Set `dir="rtl"` at the `<html>` level for RTL locales. Do not flip it per-component
unless you need to embed LTR content within an RTL page (URLs, code, product names
that use LTR Latin script).

### Text Bidirectionality

The Unicode Bidirectional Algorithm (BiDi) automatically handles mixed-direction
text but has edge cases:

```css
/* Force a specific direction regardless of content */
unicode-bidi: bidi-override;
direction: rtl;

/* Isolate a run's directionality from surrounding text */
unicode-bidi: isolate;

/* Expose the element's internal directionality to the surrounding context */
unicode-bidi: plaintext;
```

**BiDi edge case — punctuation in mixed text**: in a string like
"Hello (مرحبا)", the parentheses may render in an unexpected position because
the BiDi algorithm assigns their direction from context. Use Unicode directional
markers (`U+200F RIGHT-TO-LEFT MARK`, `U+200E LEFT-TO-RIGHT MARK`) sparingly to
fix rendering when the algorithm produces wrong results. Test with actual content,
not Lorem Ipsum.

### Icon Mirroring Rules

Icons must follow reading direction conventions:

| Icon type | Mirrors in RTL? | Rationale |
|-----------|----------------|-----------|
| Arrows (→, ←, forward, back) | Yes | Indicate direction of reading/movement |
| Chevrons (navigation) | Yes | Indicate directional navigation |
| List indent/outdent | Yes | Represent text structure |
| Play/pause/stop | No | Universal media control convention |
| Checkmarks | No | Status symbols, not directional |
| Warning/error | No | Status symbols |
| Magnifying glass | Yes (handle direction) | Handle is at reading-end |
| Share/send (arrow up-right) | No | Semantic meaning, not directional |
| Undo/redo | Yes | Temporal direction follows reading direction |

Apply mirroring via CSS, not by creating separate RTL icon assets:

```css
[dir="rtl"] .icon-arrow-forward {
  transform: scaleX(-1);
}
```

Or use the `icon-mirrored` convention in your icon system to mark which icons
mirror automatically.

### RTL Testing Checklist

```
[ ] All text content renders correctly in RTL
[ ] Layout mirrors: navigation, sidebars, list items, form fields
[ ] Flex/grid containers reverse correctly (or use logical properties)
[ ] No hardcoded directional CSS remains (grep for margin-left, padding-right, etc.)
[ ] Icons are correctly mirrored or correctly non-mirrored
[ ] Form elements: input text cursor is RTL, placeholder alignment is RTL
[ ] Animations that involve horizontal movement are reversed
[ ] Third-party embeds (maps, charts) have RTL mode enabled if available
[ ] Line length is appropriate (Arabic/Hebrew words are often longer)
[ ] No content overflow in RTL that doesn't occur in LTR
```

---

## Font Support for Multilingual

### CJK (Chinese, Japanese, Korean) Strategy

CJK character sets contain 20,000–80,000 codepoints. Loading a complete CJK web
font is 2–10 MB — never the right choice.

**Preferred approach**:
1. Use system font stack as the primary source for CJK glyphs
2. Supplement with a web font that covers only your actual characters (Unicode
   range subsetting via `unicode-range` descriptor in `@font-face`)

```css
@font-face {
  font-family: 'ProductFont';
  src: url('/fonts/product-latin.woff2') format('woff2');
  unicode-range: U+0000-00FF;  /* Latin Basic + Latin-1 Supplement */
}

/* System font fallback chain for CJK */
body {
  font-family: 'ProductFont',
    /* CJK system fonts */
    'Hiragino Sans', 'Hiragino Kaku Gothic ProN',  /* macOS Japanese */
    'Yu Gothic', 'Meiryo',                           /* Windows Japanese */
    'PingFang SC', 'PingFang TC',                    /* macOS Chinese */
    'Microsoft YaHei', 'Microsoft JhengHei',         /* Windows Chinese */
    'Apple SD Gothic Neo', 'Malgun Gothic',           /* Korean */
    sans-serif;
}
```

Google Fonts' CJK fonts (Noto Sans CJK, Source Han Sans) support dynamic subsetting
via their CSS API — the font file served to each browser contains only the glyphs
present on the rendered page.

### Arabic and Hebrew

Arabic script requires fonts that support ligatures and contextual forms — OpenType
`liga`, `calt`, `init`, `medi`, `fina` features. Most system Arabic fonts (Geeza
Pro on macOS, Arial Unicode MS on Windows) handle this correctly.

For custom brand fonts in Arabic, verify the font supports:
- All required Arabic Extended codepoints (U+0600–U+06FF, U+0750–U+077F)
- Correct glyph joining and contextual substitutions
- Kashida (tatweel, U+0640) for text justification

Hebrew is simpler (no joining forms) but requires correct handling of nikud
(vowel diacritics) if used.

### The `lang` Attribute and Rendering

The `lang` attribute affects:
- OpenType font feature selection (different ligature sets per language)
- Browser hyphenation algorithm (`hyphens: auto` requires the correct `lang`)
- Screen reader language selection
- Spell checking dictionary

```html
<p lang="zh-Hans">设计</p>  <!-- Simplified Chinese rendering -->
<p lang="zh-Hant">設計</p>  <!-- Traditional Chinese rendering -->
<!-- Same codepoints, different glyphs — only lang attribute distinguishes them -->
```

Chinese characters have different glyph forms in Simplified vs. Traditional. The
same Unicode codepoint renders differently based on `lang`. This is the Han
Unification issue — always set the `lang` attribute correctly.

---

## Translation Workflow

### String Extraction

Extract strings from source code automatically — never maintain translation files
manually.

```bash
# babel-plugin-formatjs (react-intl) — extracts from JSX
babel src/ --out-dir dist/ --extensions .tsx,.ts
# produces: lang/en.json with all message IDs and default values

# vite-plugin-i18n — for Vite + i18next
# configure in vite.config.ts, runs on build
```

### Key Naming Conventions

| Convention | Example | Tradeoff |
|-----------|---------|---------|
| **Flat** | `checkout.summary.total_label` | Simple to parse, long keys |
| **Namespaced** | `{ checkout: { summary: { total_label: '...' } } }` | Structured, easy to scope to component |
| **Semantic** | `save_button_label` | Readable, collision-prone at scale |

Recommendation: namespaced keys scoped to feature or component namespace. The
namespace prevents key collision as the codebase grows.

Never use the default English string as the key (`"Add to cart"` → key). Translators
edit the value, not the key — if the key changes, all translations are lost.

### Translation Management Systems

All three integrate with your CI/CD pipeline via CLI or webhook:

| TMS | Strength | Integration |
|-----|---------|------------|
| Phrase (formerly Phrase Strings) | Strong developer workflow, OTA delivery | GitHub App, CLI, REST API |
| Lokalise | Best-in-class UI for translators, plural editor | GitHub App, CLI, webhooks |
| Crowdin | Open-source friendly, strong community | GitHub App, CLI, in-context editor |

**Continuous localization**: translation files are pushed to the TMS on every
merge to main. Translations are pulled back via PR (automated) or on-demand.
New keys go into an "untranslated" queue in the TMS; translators work on the
queue asynchronously.

**Release-based localization**: translations are extracted and sent for translation
at release branch cut; translated files are imported before release. Simpler but
introduces localization lag.

---

## Pseudo-Localization Testing

Pseudo-localization replaces strings with transformed versions that simulate
localization problems without requiring real translations. Run it in CI.

### Transformations

```
Original: "Add to cart"
Stretched: "ÃÄÄ ŤŐ ÇÃŘŤxxxxxxxx"   ← 30-40% length increase (simulates German/Finnish)
Bracketed: "[Add to cart]"           ← identifies untranslated strings (no brackets)
Accented:  "Àdd tõ çàrt"            ← identifies encoding issues (non-ASCII fallback)
```

**Why 30-40% stretch?** German translations average 30% longer than English.
Finnish can be 40%. If your UI breaks at that length, it will break for those
locales.

### RTL Pseudo-Locale

`qps-ploc` is the Windows pseudo-locale. Most i18n libraries support a pseudo-RTL
mode that mirrors the layout for testing RTL without requiring an RTL translation.

```javascript
// i18next pseudo-locale
import i18n from 'i18next';
import pseudolocale from 'i18next-pseudo';

i18n
  .use(pseudolocale)
  .init({
    lng: 'qps-ploc',  // trigger pseudo-localization
    // ...
  });
```

### Automated Pseudo-Localization in CI

Add pseudo-locale as an E2E test target:

```yaml
# GitHub Actions CI step
- name: Pseudo-locale visual regression
  run: |
    LOCALE=qps-ploc npm run build
    npm run test:visual -- --locale=qps-ploc
```

Visual regression in pseudo-locale catches text overflow, icon mirroring failures,
and layout breaks before real translations expose them.

---

## Locale-Sensitive Data

### Date and Time

**Storage rule**: always UTC in the database. Never store a local time without a
timezone offset.

```sql
-- Correct: TIMESTAMPTZ stores UTC
created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()

-- Wrong: TIMESTAMP without timezone is an ambiguous local time
created_at TIMESTAMP  -- which timezone? unknown.
```

**Display rule**: localize at the display layer using the user's timezone preference.

```javascript
// Always pass timeZone — never let it default to the browser's system timezone
new Intl.DateTimeFormat('en-US', {
  dateStyle: 'medium',
  timeStyle: 'short',
  timeZone: user.timezone  // IANA timezone string: 'America/New_York'
}).format(new Date(event.created_at))
```

**IANA timezone database**: the canonical reference for timezone identifiers
(`America/New_York`, `Europe/Berlin`, `Asia/Tokyo`). Use IANA identifiers, never
abbreviations (PST, EST are ambiguous across regions).

**Temporal API**: the successor to `Date` in JavaScript. `Temporal.ZonedDateTime`,
`Temporal.Instant`, and `Temporal.PlainDate` provide correct timezone-aware
arithmetic. In production as of 2026 in all major browsers — prefer it over
date-fns or Moment.js for new code.

### Number Systems

Arabic-Indic numerals (`٠١٢٣٤٥٦٧٨٩`) are used in some Arabic locales instead
of European numerals. `Intl.NumberFormat` handles this automatically:

```javascript
new Intl.NumberFormat('ar-SA').format(1234)  // → "١٬٢٣٤"
new Intl.NumberFormat('ar-EG').format(1234)  // → "١٬٢٣٤" or "1,234" — depends on locale data
```

### Currency Display

```javascript
// Symbol: "$1,234.50" (en-US) vs "1.234,50 €" (de-DE)
new Intl.NumberFormat(locale, { style: 'currency', currency: 'USD' }).format(amount)

// Code: "USD 1,234.50" — unambiguous, use in international contexts
new Intl.NumberFormat(locale, { style: 'currency', currency: 'USD', currencyDisplay: 'code' }).format(amount)

// Name: "1,234.50 US dollars"
new Intl.NumberFormat(locale, { style: 'currency', currency: 'USD', currencyDisplay: 'name' }).format(amount)
```

Never hardcode currency symbols. `$` is ambiguous (USD, CAD, AUD, MXN, and others).
Use `Intl.NumberFormat` with the currency code and let it render the correct
symbol for the locale.

---

## Cross-Spoke Routing

| Topic | Route To |
|-------|----------|
| Component architecture that renders i18n strings | `fe-component-architecture` |
| Multi-script typography design (not engineering) | `type-multi-script` |
| Backend API design for locale-aware responses | `be-api-design` |
| Language metadata for screen reader accessibility | `a11y-auditory` |

## Related
- hub → [[lead-frontend-engineer]]
