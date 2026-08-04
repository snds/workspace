---
name: visual-qa-type
description: >-
  Rendered-text QA lens — judgment on how type actually renders in a built artifact, at the
  letterform, metrics, and text-setting level. Use when the complaint is about the text itself
  rather than the layout around it: "the font looks wrong", "the text jumps when the page
  loads", "why is this bold so heavy", "these numbers don't line up", "the heading is breaking
  badly", "review the typography of this page", "the quotes look wrong", "the letter-spacing is
  off", "this truncation loses the label", "the type renders muddy at this size". Covers font
  loading and fallback metric mismatch (FOUT/FOIT/CLS), synthetic bold and oblique, optical
  size and variable-axis misuse, hinting and anti-aliasing at small sizes, tracking by size and
  case, numeral style (tabular vs proportional, lining vs oldstyle), OpenType feature state,
  rag/orphans/widows/hyphenation, wrapping and truncation behavior, punctuation and dash
  quality, case abuse, mixed-script fallback, and baseline alignment in mixed-size runs. Spoke
  of lead-visual-qa. Do NOT use for: type-scale or hierarchy decisions and pairing (the /type
  hub, uid-type-for-screens), editorial/brand typographic composition
  (visual-qa-graphic-design), component-level label hierarchy in a UI (visual-qa-ui-design),
  font-file/designspace engineering (type-spacing-metrics, lead-type-designer), or minimum
  readable sizes as a WCAG concern (visual-qa-accessibility).
aliases: [visual-qa-type]
triggers: [typography review, type qa, rendered type, font loading shift, fout, foit, synthetic bold, tabular figures, text truncation review, hyphenation review, punctuation quality]
tier: cross-cutting
domain: quality
hub: lead-visual-qa
related: [uid-type-for-screens, type-spacing-metrics, visual-qa-toolkit, qa]
rigor_role: multi-voice
surfaces: ["*"]
spec_version: "2.2"
---

# Visual QA — Type

The judgment lens for **rendered text craft**: what a type designer notices when looking at a
shipped screen. Not the scale, not the hierarchy, not the brand voice — the letterforms,
metrics, features, and setting as the browser or app actually drew them.

## Why this exists next to the other two type lenses

Typography QA was already split across two spokes, and both stop before the level this one
starts at. Check this table before using this skill — if the finding belongs to a neighbor, file
it there.

| The finding is about | Lens |
|---|---|
| Which size/weight a label should be; hierarchy and density inside a component | [[visual-qa-ui-design]] (Typography QA, interface context) |
| Editorial composition: measure, leading rhythm, paragraph spacing, brand expression | [[visual-qa-graphic-design]] (Typography QA) |
| The scale's ratio, pairing choice, or token values | the `/type` hub · [[uid-type-for-screens]] |
| Minimum legible size, spacing overrides, zoom survival as WCAG criteria | [[visual-qa-accessibility]] |
| Font-file internals: spacing/kerning tables, designspace, hinting authored in the font | [[type-spacing-metrics]] · [[lead-type-designer]] |
| **How the text rendered here**: faux bold, swap shift, bad rag, wrong numerals, dumb quotes | **this lens** |

Rule of thumb: if fixing it means changing a **token or a size**, it belongs to the neighbors.
If fixing it means changing **how the font is loaded, which face is used, which feature is on,
or how the string breaks**, it belongs here.

## Measurement companions

| Claim | Measure with |
|---|---|
| Rendered cap-heights against the intended type scale | [[visual-qa-toolkit]] `qa_typography` |
| Layout shift between fallback and webfont | Capture both states and diff — [[visual-qa-toolkit]] `qa_visual_diff` (SSIM) |
| Text contrast at the rendered weight (thin type fails contrast that thick type passes) | [[visual-qa-toolkit]] `qa_contrast` |
| Font metrics and spacing behavior of the file itself | [[type-spacing-metrics]] |
| Whether truncated/hidden text is still programmatically available | [[a11y-audit-toolkit]] |

Native resolution is a precondition: anti-aliasing, hinting, faux-bold smear, and 1px baseline
misalignment are invisible in a downsampled screenshot. Capture per [[native-visual-eval]] and
state the pixels judged at.

## Font loading and face selection

- **Swap shift (CLS)** — a fallback with different metrics reflows text when the webfont lands.
  Judge the transition, not just the end state: check for `size-adjust` /
  `ascent-override` metric matching, `font-display` choice, and whether the shift is visible on
  a throttled connection. A jumping headline is a defect even if the final render is perfect.
- **Invisible text (FOIT)** — `font-display: block` with a slow font means unreadable content
  during load. On a data-dense app, that is a functional failure.
- **Synthetic bold / oblique** — when the requested weight or italic doesn't exist in the loaded
  face, the renderer smears or shears it. Symptoms: mushy heavy weights, uneven stroke contrast,
  italics with no true italic letterforms (single-storey `a`, real `f` descender). Always a
  finding: load the real face or use a weight that exists.
- **Wrong face served** — a variable font falling back to a static instance, a subset missing
  the glyphs actually used (arrows, math, currency, accented names showing tofu), or the wrong
  family entirely on one platform. Check every platform target, not just the author's machine.
- **Optical size** — a display cut used at 14px looks fragile; a text cut used at 72px looks
  clumsy. If the family has `opsz`, verify it is actually varying (or that the right named
  instance is used).
- **Variable-axis misuse** — non-standard axis values that land between the designer's tested
  masters, `wght` interpolated where the family expects named instances, or a `wdth` axis being
  used to fake fitting a label into a box.

## Setting and text behavior

- **Tracking by size and case** — display sizes usually need slight negative tracking; small
  sizes and all-caps need positive. A single global letter-spacing applied to every size is a
  finding.
- **Numerals** — tabular, lining figures in tables and anything that updates in place (values
  must not dance); proportional in prose. Mixed numeral styles in one column is a defect. Check
  that the DS actually enables `font-variant-numeric: tabular-nums` where it claims to.
- **OpenType feature state** — expected ligatures present (and *not* present where they harm,
  e.g. in code or IDs), fractions and ordinals where used, no unintended discretionary
  ligatures, `case`-sensitive punctuation with all-caps, small caps real rather than
  scaled-down caps.
- **Rag, orphans, widows, hyphenation** — headlines breaking on the wrong word (`text-wrap:
  balance` / `pretty` exists, use it), a one-word last line in a short paragraph, hyphenation
  enabled on a language whose dictionary isn't loaded, and mid-word breaks in dense grids.
- **Wrapping and truncation** — the string every product forgets: the longest realistic value.
  Judge with real data, including long names, German compounds, and RTL. Truncation must be
  recoverable (tooltip, expansion, detail view); `overflow: hidden` with no affordance loses
  information. Two-line clamps that cut mid-sentence with no ellipsis are a defect.
- **Punctuation quality** — curly quotes and apostrophes (not `"` and `'`), correct dash by role
  (hyphen / en-dash for ranges / em-dash for breaks), real ellipsis character, non-breaking
  spaces before units and after short prepositions where the language expects it, prime marks
  for measurements rather than quotes.
- **Case abuse** — all-caps for anything longer than a short label (it destroys word shape and
  reading speed, and it breaks acronym legibility), CSS `text-transform` applied to
  user-generated content or proper nouns, small caps faked by shrinking uppercase.
- **Mixed-script and locale** — fallback faces for CJK/Arabic/Cyrillic should be intentional and
  metrically compatible; line-height that works for Latin often clips diacritics or CJK. Verify
  with a real localized string, not lorem ipsum.
- **Baseline alignment** — mixed-size runs on one line (label + value, text + icon + badge)
  should sit on a shared baseline, not be center-aligned by default; superscripts and currency
  marks should use real features rather than shrunken text.
- **Rendering artifacts** — sub-pixel positioning on transformed text, blurriness from
  fractional translate values, thin weights disappearing on dark backgrounds (optical weight
  gain), and `-webkit-font-smoothing` overrides that thin type below legibility.

## QA checklist — rendered type

**Loading and face**
- [ ] No visible layout shift when the webfont replaces the fallback (metrics matched)
- [ ] Text is never invisible during load on a throttled connection
- [ ] No synthetic bold or oblique — every used weight/style exists in the loaded face
- [ ] Correct family and subset on every platform target; no tofu in real data
- [ ] Optical-size / variable axes are set intentionally

**Numerals and features**
- [ ] Tabular lining figures in tables and live-updating values
- [ ] Numeral style consistent within a column
- [ ] Expected OpenType features on; unwanted ones off; small caps are real

**Setting**
- [ ] Tracking adjusted by size and case, not globally
- [ ] Headline breaks read well; no orphans/widows in short paragraphs
- [ ] Hyphenation appropriate for the language and column width
- [ ] Longest realistic string tested — wrap and truncation both acceptable
- [ ] Truncated text remains recoverable
- [ ] Curly quotes, correct dashes, real ellipsis, non-breaking spaces where needed
- [ ] All-caps limited to short labels; no `text-transform` on user content

**Rendering**
- [ ] Mixed-size runs share a baseline
- [ ] No blur from fractional transforms; no thin weight vanishing on dark surfaces
- [ ] Localized strings checked in at least one non-Latin script if the product ships one

## Report shape

Return the shared `/qa` format. Route fixes: loading strategy and `@font-face` work to
[[fe-design-tokens]] / [[fe-performance]] (swap shift is also a CLS finding —
[[fe-perf-harness]] can quantify it), token/scale changes to the `/type` hub, font-file issues
to [[lead-type-designer]] / [[type-spacing-metrics]], and legibility-as-accessibility findings to
[[visual-qa-accessibility]].

## Related
- hub → [[lead-visual-qa]]
- peer ↔ [[uid-type-for-screens]] · [[visual-qa-toolkit]] · [[qa]]
