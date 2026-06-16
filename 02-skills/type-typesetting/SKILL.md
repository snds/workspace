---
name: type-typesetting
description: >
  Manual and digital typesetting — professional InDesign typesetting, CSS
  typesetting for the web, rag control, baseline grid, widows and orphans,
  optical margin alignment, paragraph composition, hierarchical typesetting,
  micro-typography. Use this skill whenever the conversation involves: setting
  body text professionally, rag control, InDesign paragraph composer vs.
  single-line composer, optical margin alignment, baseline grid and how type
  snaps to it, widows and orphans, justified text settings, hyphenation settings,
  hierarchical typesetting (headline → deck → subhead → body → caption),
  CSS font-feature-settings for typesetting, text-wrap: balance for headlines,
  optical alignment in layout, or any question about making text read beautifully
  on the page or screen. Spoke of `lead-type-designer`.
---

# Type Typesetting

Specialist lens for professional typesetting — the art of setting type for
reading on page or screen. Part of the `lead-type-designer` skill network.

---

## Domain Boundary

This skill covers **typesetting** — taking the type designer's output and
setting it for reading. The distinction from type design: type design makes
the font; typesetting deploys it.

- **The typeface being set** → `type-letterform-construction`, `type-spacing-metrics`
- **OpenType features to enable** → `type-opentype-text`
- **Grid that typesetting sits within** → `lead-graphic-designer`/`gd-grid-and-layout`
- **IA hierarchy expressed as typographic hierarchy** → `lead-ux-designer`/`ux-information-architecture`
- **DS text style tokens** → `ds-advisor`

---

## Typesetting Philosophy

Typesetting is the art of making text disappear.

Not literally — the text is visible. But skilled typesetting makes the reader
unaware of the typography itself. The type does not call attention to itself; it
delivers its content cleanly, invisibly, without friction. When typesetting
fails, the reader notices: they see a clumsy word break, a widow, a paragraph that
looks tight while the next looks loose, a headline whose rag makes it look
like three stacked labels. When it succeeds, the reader reads.

---

## InDesign Professional Typesetting

InDesign is the primary professional typesetting environment for print and
high-quality editorial. Its tools go far beyond what CSS provides.

### Paragraph Composer vs. Single-Line Composer

**Always use the Paragraph Composer for body text.**

- **Single-line composer** (Photoshop default, InDesign default for new frames):
  Evaluates each line independently — decides the best break for this line without
  regard for what comes next. Fast, predictable, often produces ugly rags and
  excessive hyphenation.

- **Paragraph Composer**: Evaluates all lines in a paragraph simultaneously and
  finds the globally optimal combination of line breaks, hyphenation, and word
  spacing. Produces far smoother rags, fewer hyphens, and better overall paragraph
  texture. The result is visibly superior.

**Why this matters**: A paragraph set with the single-line composer will have
individual lines that look good in isolation but create an uneven rag across
the paragraph. The paragraph composer treats the paragraph as a unit — the
correct level of abstraction for body text.

**How to set**: Paragraph panel menu → Adobe Paragraph Composer

### Justification Settings

**Justified text** (aligned both left and right) requires careful tuning to
avoid rivers and gaps.

In InDesign's Justification dialog:

| Setting | Conservative range | Rationale |
|---|---|---|
| Word spacing: min/desired/max | 80% / 100% / 120% | Allow some compression and expansion, but not extreme |
| Letter spacing: min/desired/max | -3% / 0% / 3% | Slight letter-spacing flexibility improves justification quality |
| Glyph scaling: min/desired/max | 99% / 100% / 101% | Imperceptible glyph stretch as last resort |

**Rivers**: Vertical chains of word spaces that read as white streaks through
a column. Caused by over-wide word spacing, especially in narrow measures.
The paragraph composer reduces rivers; restrictive justification settings prevent them.
Reducing measure to the correct width (55–75 characters) is the structural fix.

### Optical Margin Alignment

Punctuation and soft strokes (serifs, thin stems) that fall at the text boundary
create an optically uneven edge even when mathematically aligned.

**Optical margin alignment** (InDesign: Story panel → Optical Margin Alignment)
extends punctuation (hyphens, commas, periods, quotation marks), small letter
strokes, and parts of curved forms slightly outside the text frame. The result is
a visually straighter edge.

**When to use**: Always on carefully typeset editorial body text, especially
justified text. Hanging punctuation outside the column margin is the mark of
professional typesetting.

**CSS equivalent**: `hanging-punctuation: first last` — limited but useful.

### Hyphenation Settings

Hyphenation is necessary for justified text and valuable for ragged text to prevent
very long lines. Settings to tune:

| Setting | Recommendation |
|---|---|
| Minimum word length | 5–6 characters — don't hyphenate short words |
| Minimum before | 2–3 characters — don't hyphenate after just 2 letters |
| Minimum after | 3 characters — don't leave 2-letter fragments |
| Hyphen limit (consecutive lines) | 2–3 — the "hyphenation ladder"; more than 3 consecutive hyphens looks bad |
| Capitalize words | Off — don't hyphenate proper nouns |
| Last word | Off — don't hyphenate the last word in a paragraph |

**Discretionary hyphens**: Insert manually (⌘-Shift-Hyphen / Ctrl-Shift-Hyphen)
at semantically appropriate break points to guide the composer without forcing
breaks elsewhere.

**Non-breaking hyphens**: Use for compound words that should never break across
lines (well-known, co-founder).

---

## Rag Control

The **rag** is the irregular edge of a ragged-right text block. Good rag is a
design element; bad rag looks accidental.

### What Good Rag Looks Like

- **Gently irregular**: The line ends should vary slightly but avoid dramatic steps
- **No two consecutive very short lines**: Creates a staircase effect
- **No very long line followed by a very short line**: Creates a notch
- **No lines that end at almost the same length**: Creates a nearly flush edge that
  looks like a failed justification attempt
- **No lines ending with a preposition or conjunction at small size**: Grammatically
  odd endings create reading speed bumps

### How to Improve Rag

In InDesign:
1. Identify problem lines (too short, too long, staircase patterns)
2. Insert **discretionary line breaks** (Shift-Return) at natural phrase boundaries
3. Track the paragraph very slightly (+0–3 units) to redistribute word spacing
4. Adjust copyfitting if the text is flexible

**Do not**: Use hard returns (Return/Enter) inside a paragraph to force rag — this
creates fragile typography that breaks if the text changes or the frame is resized.

### Rag and Hyphenation Interaction

Excessive hyphenation often indicates a rag problem — the composer is hyphenating
to fill lines that could be broken differently. Adjusting the Justification settings
or using the Paragraph Composer usually reduces hyphenation while also improving rag.

---

## Widows and Orphans

**Orphan**: The first line of a paragraph isolated at the **bottom** of a column
or page, separated from the rest of the paragraph.

**Widow**: The last line of a paragraph (often a short fragment) isolated at the
**top** of a column or page.

Both are typographic errors. Both interrupt reading flow by forcing the eye to
jump to a new column or page to find the continuation.

### Fixes

1. **Copyfitting**: Add or remove words, rewrite the last sentence to produce a
   different line count — the cleanest fix
2. **Tracking adjustment**: Slightly track the preceding paragraph (±3–5 units)
   to pull the widow back or push it to join its paragraph
3. **InDesign automatic options**: Paragraph panel → Keep Options: Keep Lines
   Together, Keep with Next, Keep first/last N lines — enable for all body text

**InDesign settings for production**:
- Keep Options: Keep 2 lines at start; Keep 2 lines at end
- "Keep with Next": Enable for headlines and subheads (prevents orphan headline at column bottom)

---

## Baseline Grid

The baseline grid creates **vertical rhythm** — all body text lines, across all
columns and all pages, aligning to the same underlying grid. When baseline grid
is correct, text columns share a consistent vertical cadence.

### Setting Up the Baseline Grid

- **Grid interval = body text leading**: If body text is 10pt on 14pt leading, set
  the grid to 14pt
- **Headlines and captions**: Snap to the grid or to multiples of the grid; a
  headline might sit on every 3rd grid line while body text sits on every line

### Grid and Hierarchy

In a hierarchical typesetting system:

| Element | Grid relationship |
|---|---|
| Body text | Aligns to every baseline grid line |
| Captions | Align to every baseline grid line (typically smaller type, more leading) |
| Subheads | Align to every grid line or every 2nd; "Keep With Next" ensures body text below also aligns |
| Section headings | Align to multiples; allow a grid-aligned spacer above |
| Headlines | Align to multiples; may not strictly snap at large sizes |

**Anti-pattern**: Enabling "Align to Baseline Grid" on all paragraph styles
without setting all styles' leading to multiples of the grid. The result is
forced leading changes that override carefully set leading values.

---

## Hierarchical Typesetting

Typographic hierarchy is the visual expression of information hierarchy. Every
level has a defined relationship to the others.

### The Hierarchy Stack

| Level | Role | Typical size relationship |
|---|---|---|
| Headline | Primary entry point | 3–5× body |
| Deck/Standfirst | Bridging context | 1.5–2× body |
| Subhead (section) | Navigation within body | 1.2–1.5× body; differentiated by weight or style |
| Body text | Primary reading surface | Base size |
| Pull quote | Emphasis within reading | 1.2–1.5× body; differentiated by style |
| Caption | Secondary annotation | 0.8–0.9× body |
| Label/Tag | Navigation, categorization | 0.7–0.9× body; often all-caps + tracked |

**Key principle**: **Typographic hierarchy IS IA hierarchy in visual form.** The
type system and the information architecture are the same structure expressed in
different media. A three-level heading hierarchy with body text and captions maps
directly to an IA with primary, secondary, and tertiary navigation, content, and
annotation levels. Route to `lead-ux-designer`/`ux-information-architecture` when
the typographic hierarchy is unclear — the source of truth is the IA.

---

## Web Typesetting — CSS

### Core CSS for Professional Typesetting

```css
/* Foundational text rendering */
body {
  font-kerning: normal;
  font-variant-ligatures: common-ligatures;
  text-rendering: optimizeLegibility;  /* Enables kerning + ligatures in some browsers */
  -webkit-font-smoothing: antialiased;  /* macOS: subpixel → grayscale AA */
}

/* Rag control for headings */
h1, h2, h3 {
  text-wrap: balance;  /* Balances line lengths in short multi-line headings */
}

/* Body text — prevent extreme rag */
p {
  text-wrap: pretty;  /* Avoids orphaned words on last line (progressive enhancement) */
}

/* Hyphenation — body text only */
p, li, td {
  hyphens: auto;
  hyphenate-limit-chars: 6 2 3;  /* Min word / before / after */
  hyphenate-limit-lines: 2;      /* Max consecutive hyphenated lines */
}

/* Widows and orphans */
p {
  orphans: 2;
  widows: 2;
}

/* Optical margin alignment approximation */
blockquote, .pull-quote {
  hanging-punctuation: first last;
}

/* Tabular numeric styles */
.data-cell, .price, .stat {
  font-variant-numeric: tabular-nums lining-nums;
  font-feature-settings: 'tnum' 1, 'lnum' 1;
}
```

### What CSS Can't Do (Yet)

- **Paragraph Composer equivalent**: CSS has no multi-line rag optimization; each
  line is broken independently. `text-wrap: pretty` is an approximation.
- **Rag control**: Manual rag control in CSS requires `<wbr>` tags or JavaScript
  line-break injection — not practical for CMS content
- **Optical margin alignment**: `hanging-punctuation` only works for the first and
  last characters of a block, not inline punctuation throughout

---

## Anti-Patterns and Failure Modes

| Anti-pattern | Symptom | Fix |
|---|---|---|
| Single-line composer for body text | Uneven rag, excessive hyphenation, rivers | Switch to Paragraph Composer |
| Hard returns to fix rag | Rag breaks if text changes or frame resizes | Use discretionary line breaks or copyfitting |
| No baseline grid | Text columns don't share vertical rhythm | Set baseline grid = body leading |
| Widows/orphans unaddressed | Fragment lines at column top/bottom | Keep Options: 2 lines at start/end; copyfit |
| Justified text with no tuning | Rivers, uneven word spacing | Tune Justification settings; use Paragraph Composer |
| No `text-wrap: balance` on headings | Headlines with one word on the last line | Add CSS `text-wrap: balance` to all heading levels |
| Missing hyphenation on web body text | Extreme rag on narrow columns | Enable `hyphens: auto` with appropriate limits |
| Hierarchy that doesn't match IA | Visual structure confuses navigation | Audit the IA and rebuild type hierarchy to match |

---

## Cross-Links

- `type-spacing-metrics` — leading (line-height) is a typesetting decision with origins in the spacing system; correct leading values come from metrics knowledge
- `type-opentype-text` — enabling the right OpenType features is part of professional typesetting; liga, tnum, smcp, case should be specified at the paragraph style level
- `type-classification-history` — knowing the register and historical context of the face being set informs setting decisions (Bodoni needs more leading; humanist faces tolerate tighter tracking)
- `lead-graphic-designer`/`gd-grid-and-layout` — typesetting sits within a grid; baseline grid theory is foundational
- `ds-advisor` — typesetting knowledge translates into DS text style token design; the typographic system (scale + leading + tracking + measure) should be designed as a coordinated set
- `lead-ux-designer`/`ux-information-architecture` — typographic hierarchy is the visual form of IA hierarchy; the two should be designed in parallel
- `lead-ux-designer`/`ux-interaction-design` — reading flow, cognitive load, and text legibility are user experience decisions grounded in typesetting quality
