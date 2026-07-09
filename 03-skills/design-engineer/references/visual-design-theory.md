# Visual Design Theory

Foundational principles that inform every design decision — from token values
to component anatomy to page composition. Load this spoke when reasoning about
*why* a visual choice works, not just *what* the choice is.

This is not a textbook. It's a working reference for applying theory to design
system decisions, component evaluation, and visual quality assessment.

---

## Table of Contents

1. Gestalt principles — perception and grouping
2. Visual hierarchy — directing attention
3. Color theory — relationships, contrast, meaning
4. Typography — structure, readability, rhythm
5. Spacing and rhythm — the invisible structure
6. Applying theory to design system decisions

---

## 1. Gestalt Principles

Gestalt describes how humans perceive grouped elements as unified wholes rather
than individual parts. These principles are the perceptual foundation of every
layout, component, and composition decision.

### Proximity

Elements near each other are perceived as related. Distance creates separation.

**DS application:** Spacing tokens encode proximity relationships. The gap
between a label and its input (tight = related) should be smaller than the gap
between two form groups (loose = separate concern). If spacing tokens don't
encode this distinction, designers will override them — that's a system failure,
not a designer failure.

### Similarity

Elements that share visual properties (color, shape, size, weight) are perceived
as belonging to the same group.

**DS application:** Consistent token application creates similarity. All primary
actions share the same color token → they read as a group. When one button uses
a hardcoded hex instead of the action token, it breaks similarity and reads as
a different thing — even if the values are identical today. Tokens enforce
perceptual grouping at scale.

### Continuity

The eye follows smooth paths. Elements arranged along a line or curve are
perceived as related and flowing in a direction.

**DS application:** Alignment grids, auto layout flow direction, and reading
order all leverage continuity. A form with inconsistent left-edge alignment
forces the eye to jump — each jump is cognitive load. Consistent alignment
tokens (padding, margin) maintain continuity across components.

### Closure

The brain completes incomplete shapes. Partial boundaries are perceived as
whole forms.

**DS application:** Card components don't need borders on all four sides to
read as cards — a background fill, shadow, or even consistent padding creates
closure. Over-bordering is a common DS anti-pattern: adding strokes "for
clarity" when the existing spatial relationships already create closure.

### Figure-ground

Elements are perceived as either foreground (figure) or background (ground).
The relationship between them creates depth and focus.

**DS application:** Elevation tokens (shadow, z-index) establish figure-ground.
Modals are figure; the overlay is ground. Popovers float above their trigger.
When elevation tokens are inconsistent, elements compete for the same perceptual
layer and the interface feels flat or confusing.

### Common region

Elements within a shared boundary are perceived as grouped, even without
proximity or similarity.

**DS application:** This is why card components, fieldsets, and section frames
work. A border or background change creates a perceptual container. In Figma,
this maps directly to frames with fills or strokes that group child elements.

---

## 2. Visual Hierarchy

Hierarchy directs the eye through a composition in order of importance. Every
screen has a reading order — the designer's job is to make it intentional.

### Tools for establishing hierarchy

**Size:** Larger elements are seen first. Headings > body > captions. Type
scale tokens should create clear size steps — if two adjacent steps are too
close (14px and 15px), they fail to create hierarchy.

**Weight:** Bolder elements draw attention. Use weight for emphasis within a
size tier. Two weights (regular and medium/semibold) are usually sufficient
within a component — more than that creates noise.

**Color/contrast:** High-contrast elements dominate. Primary actions use strong
color on neutral backgrounds. Muted text recedes. Semantic color tokens
(action, text-primary, text-secondary, text-tertiary) are hierarchy tokens
disguised as color tokens.

**Position:** Top-left dominates in LTR layouts (F-pattern and Z-pattern
scanning). Primary actions belong where the eye naturally lands. This shifts
in RTL contexts — design systems serving multiple languages need layout
direction awareness.

**Whitespace:** Generous space around an element elevates its importance.
Crowded elements compete for attention. Strategic use of space tokens (padding,
margin) creates breathing room that signals importance.

### Hierarchy failures to flag

- Two elements competing for primary attention (two equally strong CTAs).
- Body text and labels at the same size/weight (hierarchy collapse).
- Icon and text at equal visual weight — one should lead.
- Dense layouts with uniform spacing — everything reads as equally important.

---

## 3. Color Theory

### Perceptual color: why the model matters

Traditional color models (RGB, HSL, hex) describe colors in terms of how
screens produce them — not how humans perceive them. This creates real
problems for design system work: HSL's "lightness" axis is not perceptually
uniform. Two colors at the same HSL lightness can appear drastically different
in perceived brightness depending on hue (yellow appears much lighter than
blue at the same L value). This makes it impossible to build perceptually
even ramps, predict contrast, or generate reliable dark mode inversions by
manipulating HSL values mathematically.

The solution is to work in a perceptually uniform color space and convert
to display formats (sRGB hex, RGBA) only at the output stage.

### Oklab and Oklch — the working color space

**Oklab** (Björn Ottosson, 2020) is a perceptually uniform color space
designed so that equal numeric changes correspond to equal perceived visual
changes. It uses three components: L (perceptual lightness, 0–1), a (green–red
opponent axis), and b (blue–yellow opponent axis).

**Oklch** is the cylindrical form of Oklab — same perceptual foundation but
expressed as L (lightness), C (chroma/saturation intensity), and H (hue angle
in degrees). This is the more intuitive form for design work because it maps
to how designers think about color: "I want the same hue, but lighter" or
"I want to reduce saturation without shifting the hue."

```
Oklch components:
  L  (0–1)    Perceptual lightness. 0 = black, 1 = white.
               Unlike HSL, equal L steps produce equal perceived brightness
               steps across all hues.
  C  (0–0.4+) Chroma. 0 = achromatic (grey). Higher = more vivid.
               The maximum depends on the hue and the display gamut.
  H  (0–360°) Hue angle. Perceptually uniform — rotating H produces
               visually even hue shifts without the lightness jumps
               that plague HSL.
```

**Why Oklch over HSL for DS work:**
- Building token ramps: stepping L in equal increments produces visually
  even lightness scales across every hue. No manual tweaking needed.
- Dark mode generation: inverting or shifting L produces predictable results
  because lightness perception is linear in this space.
- Chroma control: reducing C desaturates without hue shifts. HSL's S axis
  introduces hue drift at low saturation.
- Palette generation: colors at the same L value across different hues will
  appear equally light — critical for building multi-hue palettes that read
  as a cohesive set.

### The Figma gap and the conversion pipeline

Figma does not natively support Oklch as of March 2026. Figma's color picker,
variables, and styles operate in sRGB (hex, RGBA). This means:

**Design workflow:**
1. Author colors in Oklch using external tools (oklch.com, Evil Martians'
   OKLCH Color Picker, the Polychrom Figma plugin for APCA contrast checking,
   or the Prism/AVA Palettes plugins for ramp generation).
2. Convert to sRGB hex for Figma consumption. Oklch values that fall within
   the sRGB gamut convert losslessly. Values outside sRGB gamut are clipped
   to the nearest displayable color — be aware of this at high chroma values.
3. Store the Oklch source values in token documentation or token JSON
   alongside the hex output. The Oklch value is the source of truth; the hex
   is the derived output.
4. When CSS supports `oklch()` in the target browsers (Chrome 111+,
   Safari 15.4+, Firefox 113+ — ~93% global support as of 2026), export
   tokens as `oklch()` values directly. Tailwind CSS v4 already uses Oklch
   as its default color space.

**Token architecture implication:** The 3-tier token model still applies.
Primitives are authored in Oklch and converted to hex for Figma. Semantic and
component tiers alias the primitives as before. The color space is a property
of the primitive tier — downstream tiers don't need to know about it.

### Color relationships in Oklch

The classical color relationships (complementary, analogous, triadic,
split-complementary) still apply — they describe geometric relationships on
the hue wheel. In Oklch these relationships are more reliable because the
hue axis is perceptually uniform: a 180° complement actually looks like
a perceptual opposite, not an arbitrary mathematical one.

**Complementary** (H ± 180°): Maximum perceptual contrast in hue. Use
sparingly at high chroma — the combination vibrates optically.

**Analogous** (H ± 30–60°): Harmonious, low tension. Reliable for multi-hue
DS palettes because Oklch's even hue spacing means analogous colors genuinely
look related.

**Triadic** (H ± 120°): Balanced variety. Useful for data visualization
palettes where categorical distinction matters.

**Split-complementary** (H ± 150–160°): Contrast without the full intensity
of a pure complement. Good for accent-on-neutral patterns.

### Contrast and accessibility — APCA

#### The problem with WCAG 2.x contrast ratios

WCAG 2.x contrast (SC 1.4.3 / 1.4.6) uses relative luminance ratios that
are perceptually non-uniform. This produces two categories of error:

**False passes:** Color pairs that meet the 4.5:1 ratio but are difficult
to read in practice — especially dark-on-dark combinations where the WCAG 2
math overstates contrast. Dark mode interfaces are the most common victim.

**False fails:** Readable color pairs that technically fail the ratio —
for example, white text on a saturated blue button. The text is large, bold,
and brief. It reads fine. WCAG says no.

Both errors undermine trust in the guideline and lead teams to either ignore
contrast checking or over-correct in ways that harm visual design.

#### APCA — Accessible Perceptual Contrast Algorithm

APCA (Andrew Somers / Myndex) is the candidate contrast method for WCAG 3.0.
It reports contrast as an Lc (lightness contrast) value, not a ratio. The
scale runs from Lc 0 (invisible) to approximately Lc 106 (maximum). Key
thresholds:

| Lc value | Use case |
|---|---|
| Lc 15 | Perceptual invisibility for many users. Minimum for decorative thin lines. |
| Lc 30 | Minimum for non-text elements, large icons, thick borders. |
| Lc 45 | Minimum for large, bold text (≥ 24px / 700 weight). Placeholders, disabled text ceiling. |
| Lc 60 | Minimum for standard UI text (≥ 16px / 400–500 weight). Body content floor for comfortable reading. |
| Lc 75 | Preferred for body text, columns of running text. Comfortable extended reading. |
| Lc 90 | Preferred for critical body text, small text (< 16px), thin fonts. Maximum readability. |

**Tier note (2026-07-08)**: read this table as the *working target* — the "happy middle"
for design-engineering decisions, barring real concerns. The accessibility floor (bare
minimum) is [[a11y-visual]]'s Lc >= 60 body / >= 45 large-bold / >= 30 UI. The stricter
targets in [[radix-derived-color-system]] (~Lc 90 body / 75 content) are Radix-scale-specific:
the 12-step scale is tuned to reach them and Radix-generated palettes inherit them — do not
generalize them outside Radix-derived systems.

**Key APCA differences from WCAG 2.x:**
- **Polarity-aware.** Dark text on light background and light text on dark
  background produce different Lc values for the same color pair, because
  human vision perceives them differently. WCAG 2 treats them identically.
- **Accounts for font size and weight.** Thin, light-weight fonts need higher
  Lc values to remain legible. Bold text can tolerate lower contrast. WCAG 2
  ignores weight entirely.
- **Perceptually uniform.** An Lc 60 pairing looks equally readable whether
  the colors are light or dark. WCAG 2's 4.5:1 can be unreadable when both
  colors are dark.

#### Using APCA in practice

**For current compliance:** WCAG 2.2 AA (4.5:1 / 3:1) remains the legal
standard in most jurisdictions. Design for APCA Lc values AND verify WCAG 2
compliance. The `apcach` JavaScript library and the Polychrom Figma plugin
support both models simultaneously. Bridge-PCA is available as a backwards-
compatible bridge that uses APCA math but maps to WCAG 2 compliance levels.

**For forward-looking systems:** Author token contrast requirements in APCA Lc
values. These are more meaningful targets for designers: "body text must
achieve Lc 75 against its background" is clearer and more accurate than
"4.5:1 ratio." When WCAG 3 is finalized, APCA Lc targets will map directly
to the new conformance levels.

**DS application:** Contrast compliance is a token architecture concern, not
a per-instance check. If `color.text.primary` on `color.background.primary`
doesn't meet Lc 75 in every mode, the entire system fails. Build contrast
validation into the token pipeline: define the required Lc for each
text/background pairing at the semantic tier, validate at build time, and
flag violations before they reach production.

**Practical tooling:**
- Oklch.com — Author colors, see Oklch values, preview gamut boundaries.
- APCA Contrast Calculator (apcacontrast.com) — Official APCA tool.
- Polychrom (Figma plugin) — APCA contrast checking with Oklch conversion.
- apcach (JS library) — Generate APCA-compliant color pairs programmatically.
- Prism / AVA Palettes (Figma plugins) — Oklch ramp generation in Figma.

### Color meaning (cultural and contextual)

Color carries cultural meaning. In Western contexts: red = danger/stop,
green = success/go, yellow/amber = warning/caution, blue = trust/information.
These map to semantic color tokens. Don't use red for a primary action or
green for a destructive action — the semantic conflict creates cognitive
friction regardless of the label text.

**DS application:** Semantic color tokens must align with these conventions.
If the brand primary color is red, the action primary token should not inherit
it directly — destructive and primary actions need distinct signaling.

**Perception note:** Color meaning is also affected by chroma and lightness.
A highly desaturated red (low C in Oklch) reads as neutral/muted, not
alarming. A red at full chroma reads as danger. Semantic tokens should specify
not just hue but minimum chroma to ensure the intended connotation carries.

---

## 4. Typography

### The anatomy that matters for DS work

**Measure (line length):** 45–75 characters per line for body text.
Shorter for captions, longer is acceptable for data tables. Components with
text content should enforce max-width or rely on container constraints.

**Leading (line height):** The space between baselines. Body text needs
1.4–1.6× font size. Tight leading (1.1–1.2×) works for headings where
lines are short. Token scales for line-height should provide at least three
tiers: tight (headings), normal (body), relaxed (long-form/readable).

**Tracking (letter spacing):** The space between characters. Body text
at standard sizes needs no tracking adjustment. Small text (< 12px) benefits
from slightly positive tracking. Large headings can tolerate slight negative
tracking for visual tightness.

**Typographic hierarchy:** A system needs clear, distinct steps:
- Display: page titles, hero text (24–48px)
- Heading: section titles (18–24px)
- Subheading: subsection labels (16–18px)
- Body: paragraph text (14–16px)
- Caption: supporting text, metadata (12–13px)
- Overline: labels above headings, category markers (10–12px, often uppercase
  with wide tracking)

Each step should be visually distinct from its neighbors. If squinting blurs
two levels together, the scale isn't working.

### Font selection principles

**Readability at small sizes:** The most important criterion for UI work.
Large x-height, open counters, clear distinction between similar glyphs
(I/l/1, O/0). This matters more than aesthetics.

**Weight range:** A DS needs at minimum regular (400) and medium/semibold
(500–600). If the font family doesn't have a clean medium weight, hierarchy
will depend entirely on size — which limits options.

**Monospace pairing:** Data-heavy UIs need a monospace font for numeric
alignment in tables, code references, and time/date values. Choose one that
matches the proportional font's x-height and weight.

---

## 5. Spacing and Rhythm

### The spatial scale

A well-designed spacing scale is the single most impactful token decision in a
design system. It determines how every element relates to every other element.

**Base unit:** Most systems use 4px or 8px. 4px provides more granularity
(4, 8, 12, 16, 20, 24, 32, 40, 48, 64). 8px is simpler but can feel
constraining for dense UIs. Enterprise/data-heavy applications (like PLM
software) typically need the 4px base for density flexibility.

**Geometric vs. linear:** Geometric scales (4, 8, 16, 32, 64) grow fast and
leave gaps in the middle range. Linear scales (4, 8, 12, 16, 20, 24) fill the
middle but can overwhelm with options. Most production systems are hybrid:
linear at the small end (4, 8, 12, 16) and geometric at the large end
(24, 32, 48, 64).

### Rhythm and alignment

**Vertical rhythm:** Consistent spacing between elements creates a visual
beat. When every section, card, and form group uses the same base spacing,
the page feels ordered. Breaking rhythm (one card with 16px padding, another
with 20px) creates subtle discomfort even if users can't articulate why.

**Horizontal rhythm:** Column alignment, consistent margins, and grid
adherence. Auto layout in Figma enforces horizontal rhythm per component — but
cross-component consistency requires shared spacing tokens.

**Optical adjustment:** Mathematical spacing isn't always visually correct.
A circle needs slightly more padding than a rectangle to look equally spaced.
Text with descenders (g, p, y) needs optical compensation in vertical centering.
These adjustments should be documented as intentional decisions, not dismissed
as inconsistencies.

---

## 6. Applying Theory to Design System Decisions

### When evaluating a component

Ask these questions (grounded in the theory above):

1. **Proximity:** Do the spacing tokens create correct grouping? Are related
   elements closer than unrelated ones?
2. **Similarity:** Do consistent tokens create visual grouping? Are same-purpose
   elements styled alike?
3. **Hierarchy:** Is there a clear reading order? Can you identify primary,
   secondary, and tertiary content at a glance?
4. **Contrast:** Do text/background combinations meet APCA Lc 75+ for body
   text and Lc 60+ for UI text in all modes? Do they also pass WCAG 2 AA for
   current legal compliance?
5. **Rhythm:** Are spacing values consistent with the system scale? Any rogue
   values that break the beat?
6. **Figure-ground:** Is elevation (shadow, z-index) used intentionally?
   Do overlapping elements have clear depth relationships?

### When proposing token values

Ground the proposal in theory:
- "This spacing step exists because proximity grouping requires a distinct
  gap between related and unrelated elements."
- "The color ramp is authored in Oklch with equal L steps so the lightness
  scale is perceptually even across all hues — no manual tweaking needed."
- "The ramp includes stops at L=0.35 and L=0.25 because semantic text on
  semantic background needs a stop dark enough for Lc 75+ contrast (APCA)."

### When flagging a visual problem

Name the principle being violated:
- "These two buttons compete for attention because they're both high-contrast
  on the same surface — hierarchy failure."
- "The form feels disorganized because label-to-input spacing (8px) is the
  same as group-to-group spacing (8px) — proximity failure."
- "This card reads as two separate elements because the border was removed
  but no background fill or shadow was added — closure failure."
