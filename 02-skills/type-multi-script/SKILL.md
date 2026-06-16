---
name: type-multi-script
description: >
  Non-Latin script type design and multilingual typography. Use this skill
  whenever the conversation involves: designing or selecting type for Arabic,
  Hebrew, Devanagari, Bengali, Tamil, or other Indic scripts; CJK (Chinese,
  Japanese, Korean) typography; right-to-left layout; Arabic contextual joining
  forms; Devanagari conjunct consonants and the shirorekha; multilingual type
  families (designing Latin and non-Latin to coexist); Unicode bidirectional
  algorithm; vertical typesetting for CJK; multilingual product typography;
  testing type with non-Latin languages; or any question about text type that
  extends beyond the Latin alphabet. Spoke of `lead-type-designer`.
---

# Type Multi-Script Design

Specialist lens for non-Latin scripts, multilingual type design, and
script-specific design considerations. Part of the `lead-type-designer` network.

---

## Domain Boundary

This skill covers **text type design and selection for non-Latin scripts** and
**multilingual type families**.

- **Latin letterform construction** → `type-letterform-construction`
- **Arabic/Indic OpenType features (shaping engine)** → `type-opentype-text` (general) + `variable-icon-font-architect`/`opentype-layout-engineering` (for table-level detail)
- **Python-based multi-script font pipeline** → `variable-icon-font-architect`/`fonttools-ufo-internals`
- **Right-to-left UI layout** → `lead-ui-designer`/`uid-type-for-screens`

---

## Script Diversity Overview

Typography is not Latin typography. The Latin script accounts for a minority of
the world's writing — many of the most widely-spoken languages use other scripts
with deeply different design traditions, construction requirements, and rendering
complexity.

| Script family | Writing direction | Notable features | Key languages |
|---|---|---|---|
| Latin, Greek, Cyrillic | Left-to-right | Shared design conventions; same family can often share masters | Most European languages, Russian, etc. |
| Arabic | Right-to-left | Cursive connecting; 4 contextual forms per letter | Arabic, Persian, Urdu |
| Hebrew | Right-to-left | Consonantal alphabet; unpointed vs. pointed | Hebrew, Yiddish |
| Devanagari | Left-to-right | Abugida; conjunct consonants; headline bar | Hindi, Sanskrit, Marathi, Nepali |
| Bengali, Tamil, Telugu, Kannada | Left-to-right | Abugida variants; complex conjuncts | Bengali, Tamil, Telugu, Kannada |
| CJK | Left-to-right (also vertical) | Logographic; tens of thousands of glyphs; Han unification | Chinese, Japanese, Korean |

---

## Latin + Greek + Cyrillic Extension

These three scripts share enough structural history that a single type family
often covers all three. They are the closest neighbors in type design practice.

### Design considerations

- **Optical size coordination**: Latin, Greek, and Cyrillic text set at the same
  point size should produce the same visual density and x-height — this requires
  deliberate calibration, not mechanical scaling
- **Character sharing**: Some letterforms appear in multiple scripts with identical
  glyph shapes but different Unicode codepoints (e.g., Cyrillic 'а' and Latin 'a'
  may share a glyph in a harmonized family)
- **Script-specific details**: Greek has specific letterforms (ξ, ψ, etc.) that
  require dedicated design attention; Cyrillic has letters with no Latin equivalent
  that must harmonize with the overall design system of the face

---

## Arabic Type Design

Arabic is one of the most complex scripts in type design. Every aspect of the
Latin assumptions — left-to-right, discrete letters, context-independent forms —
is inverted or complicated.

### Fundamental Properties

- **Cursive and connected**: Arabic is a cursive script — most letters connect to
  adjacent letters in a word. There are no individual discrete letters in set text
  the way there are in Latin (no equivalent of typing individual letterforms).
- **Right-to-left directionality**: Text flows right-to-left; Unicode bidirectional
  algorithm handles mixed LTR/RTL text.
- **Four contextual forms**: Each letter has up to four forms depending on its
  position in the word:
  - **Isolated**: Letter appears alone
  - **Initial**: Letter at the start of a word (connects to following letter on left)
  - **Medial**: Letter in the middle of a word (connects on both sides)
  - **Final**: Letter at the end of a word (connects to preceding letter on right)
  These are encoded as OpenType features using `init`, `medi`, `fina`, `isol` lookups.

### Arabic Calligraphic Traditions

| Style | Characteristics | Use context |
|---|---|---|
| Naskh | Upright, clear, legible; the basis for most digital Arabic text type | Books, newspapers, UI, body text |
| Nastaliq | Diagonal cascading rhythm; elegant, highly calligraphic | Persian/Urdu formal and literary contexts |
| Kufi | Geometric, angular; based on early manuscript angular scripts | Display, branding, architectural contexts |
| Ruq'ah | Informal, fast, cursive | Handwriting, informal notes |

**Design practice**: Most Arabic text type follows the Naskh tradition. Nastaliq
requires a completely different font engineering approach (it involves extreme
vertical displacement between letters) and is rarely implemented in full for
UI contexts.

### Proportions and Weight

Arabic type has its own proportional system distinct from Latin:
- **Baseline behavior**: Arabic letters do not all sit on the same baseline; their
  vertical positions relative to the baseline vary by letterform
- **Dot placement**: Many Arabic letters are differentiated only by the number and
  position of dots above or below; dots are critical identity features and must be
  carefully sized and positioned
- **Weight calibration**: Arabic strokes have their own contrast system; a harmonized
  Arabic/Latin family must calibrate stroke weights so both appear at the same
  "color" (visual weight) on the page

### Multilingual Arabic+Latin Families

When designing a type family to serve both Arabic and Latin:
- **Optical size alignment**: Arabic at the same point size must match the visual
  scale of the Latin; x-height doesn't apply but overall cap-height-equivalent
  alignment is needed
- **Weight harmony**: Arabic and Latin bold must feel equally bold when juxtaposed
- **Spacing**: Arabic and Latin spacing systems are independent but must produce
  similar typographic color

---

## Hebrew Type Design

### Fundamental Properties

- **Consonantal alphabet** (abjad): Hebrew is written in consonants; vowel marks
  (niqqud) are written as diacritics that appear above or below consonants but
  are usually omitted in modern text
- **Right-to-left**: Like Arabic; Unicode bidirectional algorithm applies
- **Square script** (Ashkenazi tradition): The dominant modern printed form;
  letters have a blocky, geometric quality
- **Block letters, no cursive connection**: Unlike Arabic, standard Hebrew letters
  are not joined — they are individual glyphs, like Latin

### Design traditions

- **Square/block script**: Used in all printed Hebrew (newspapers, books, UI)
- **Cursive Hebrew**: Separate tradition used in handwriting; rarely encountered in type design for UI

### Diacritics (niqqud)

Niqqud are vowel pointing diacritics placed below, above, or within consonants.
Complete niqqud support is required for:
- Children's books and educational materials
- Biblical and liturgical texts
- Some formal documents

Modern digital Hebrew without niqqud is standard for most UI and editorial contexts.

---

## Devanagari Type Design

Used for Hindi, Sanskrit, Marathi, Nepali, and dozens of other Indian languages.
One of the most complex scripts in type design due to conjunct consonant formation.

### Fundamental Properties

- **Abugida**: Each consonant carries an inherent vowel ('a'); other vowels are
  written as diacritical additions to the consonant glyph
- **Left-to-right directionality**
- **Headline bar (shirorekha)**: The horizontal bar running along the top of
  Devanagari letterforms is its most distinctive structural feature; letters hang
  below the shirorekha; words are often visually unified by the continuous bar

### Conjunct Consonants

When two or more consonants appear together without an intervening vowel, they
form a **conjunct** — a ligature that combines the consonants into a single
visual unit. Some conjuncts are formed by modifying one consonant (half-forms),
others by stacking the consonants vertically.

- A complete Devanagari typeface may require hundreds to thousands of conjunct forms
- Conjunct formation is handled by OpenType `half`, `vatu`, `pres`, `blws`, and other
  shaping features that are mandatory for correct rendering
- The shaping engine (HarfBuzz) handles conjunct selection automatically once the
  font provides the correct glyphs and feature lookups
- Missing conjuncts result in broken rendering — individual consonants appear
  instead of the combined form, which is typographically incorrect

### Design considerations

- **Vertical density**: Devanagari has more vertical complexity than Latin; the
  space above and below the headline bar must accommodate vowel marks and other
  diacritics
- **Harmonizing with Latin**: A Devanagari/Latin type family must align optical
  metrics; the Devanagari baseline is typically aligned with the Latin baseline,
  and the shirorekha is typically near the Latin cap height
- **X-height equivalent**: Devanagari doesn't have an x-height in the Latin sense,
  but the body of the letter (below the shirorekha, above the baseline) plays a
  similar role

---

## CJK (Chinese, Japanese, Korean)

CJK typography operates at a different scale than Latin type design:

### Scale of the Problem

- A complete Chinese font may contain 20,000+ glyphs
- A complete Japanese font (including CJK unified ideographs, hiragana, katakana,
  Latin, and punctuation) may contain 10,000–20,000 glyphs
- A basic Korean font requires ~2,350 syllable blocks (KS X 1001 standard) plus
  Hangul jamo

### Han Unification

Unicode combines Chinese, Japanese, and Korean characters with the same origins
into a single CJK Unified Ideographs block. However, the same Unicode codepoint
may require different glyph forms in Chinese vs. Japanese vs. Korean contexts.
OpenType handles this via `locl` (locale-sensitive substitution) lookups.

### Vertical Typesetting

CJK text can be set vertically (top-to-bottom, right-to-left column order) — a
tradition maintained in literary, formal, and some editorial contexts. Fonts
supporting vertical typesetting require:
- **Vertical glyph alternates** (the `vert` OpenType feature): characters rotated
  or replaced with vertical-appropriate forms
- **Vertical metrics**: OpenType vertical metrics (vmtx table) for correct vertical layout

### Proportional vs. Monospaced CJK

- **Full-width (monospaced)**: Each CJK glyph occupies exactly 1em × 1em;
  Latin and numeric characters have half-width variants (0.5em)
- **Proportional**: Latin characters within CJK text can be proportionally spaced,
  improving readability for mixed CJK+Latin text

---

## Multilingual Type Families

Designing a single type family that serves multiple scripts coherently is one of
the highest-complexity challenges in type design.

### Design coordination goals

1. **Optical size alignment**: Scripts at the same point size should appear the
   same visual size — this is deliberately designed, not automatic
2. **Typographic color matching**: Stroke weights and spacing calibrated so all
   scripts produce the same visual density on the page
3. **Weight axis coordination**: The bold of each script should feel equally bold
   when placed adjacent to each other
4. **Personality coherence**: The calligraphic tradition, humanist or geometric
   quality, and stylistic character of the design should be legible across scripts

### Testing multilingual type

- **Never use Lorem Ipsum for non-Latin scripts** — it is meaningless and will not
  reveal text-rendering issues specific to that script
- Use authentic language samples — real sentences, real words
- Test with native speakers or native script readers who can identify incorrect
  conjuncts, wrong letter connections, or culturally inappropriate letterforms
- Test complex text features: joining behavior in Arabic, conjunct formation in
  Devanagari, vertical metrics in CJK, niqqud positioning in Hebrew

---

## Anti-Patterns and Failure Modes

| Anti-pattern | Symptom | Fix |
|---|---|---|
| Lorem ipsum for Arabic/Devanagari testing | Real text rendering issues undetected | Use authentic language samples |
| Missing conjuncts in Devanagari | Individual consonants shown instead of combined forms | Implement required conjunct glyphs and OpenType shaping features |
| No `locl` feature for CJK | Wrong glyph variants served to Chinese/Japanese/Korean users | Implement locale-sensitive substitution |
| Arabic font at wrong optical size | Arabic appears too large or too small alongside Latin | Calibrate Arabic optical size relative to Latin at the design level |
| Mechanical scaling of Latin for other scripts | Proportions, weight, and optical size all wrong | Redesign each script from scratch with coordination, not scaling |
| Assuming left-to-right everywhere | RTL languages rendered incorrectly, UI layout broken | Implement Unicode bidi algorithm; test all RTL text surfaces |

---

## Cross-Links

- `type-opentype-text` — script-specific OpenType features; Arabic shaping requires dramatically more OpenType complexity than Latin; Devanagari requires mandatory shaping features
- `variable-icon-font-architect`/`opentype-layout-engineering` — GSUB/GPOS table engineering for Arabic contextual forms, Devanagari shaping
- `variable-icon-font-architect`/`fonttools-ufo-internals` — Python-based multi-script font pipeline; fontTools for multi-script designspace builds
- `type-letterform-construction` — construction principles in Latin; each script has analogous construction principles specific to its calligraphic tradition
- `ds-advisor` — DS type token system must account for multilingual typography; different scripts may need different line-height tokens at the same point size
- `lead-ui-designer`/`uid-type-for-screens` — RTL layout in UI; bidirectional text; font selection for screen rendering across scripts
