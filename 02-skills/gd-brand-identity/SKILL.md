---
name: gd-brand-identity
description: >
  Brand identity design — mark construction, identity systems, and standards.
  Use this skill whenever the conversation touches: logo design, wordmark,
  lettermark, pictorial mark, abstract mark, combination mark, emblem, mark
  geometry, proportion systems for logos, optical corrections in mark design,
  identity systems, brand standards documentation, clear space, minimum sizes,
  prohibited uses, color specifications (Pantone/CMYK/RGB/HEX), brand
  architecture (monolithic, endorsed, pluralistic), brand in digital products,
  dark mode brand behavior, brand token architecture, or any question about
  how a brand identity is constructed, extended, or documented.
---

# GD — Brand Identity

Specialist lens for brand identity design and identity systems. Part of the
Lead Graphic Designer skill network.

---

## Domain Boundary

This skill owns **brand identity decisions** — the construction and extension
of visual identity as a complete system.

- **Color specifications and print color** → `gd-color-theory` + `gd-print-production`
- **Typography within brand identity** → `gd-typography`
- **Product visual language derived from brand** → `lead-ui-designer` / `uid-visual-system`
- **Brand color as design system tokens** → `ds-advisor` (this skill is upstream source)
- **Custom typeface commission** → `lead-type-designer`

---

## Logo Design Typology

A logo is not a single thing. The term covers several structural categories,
each with different construction principles and appropriate use cases.

### Wordmark
The brand name set in a distinctive typeface, often with custom modifications.
*Examples: Google, FedEx, Coca-Cola, IBM*

- **Strengths**: directly communicates the brand name; highest name recognition
  value; requires no separate icon to learn
- **Weaknesses**: requires at minimum 2–3 characters to be legible at small sizes;
  does not abstract to an app icon or favicon without modification
- **Construction requirements**: custom tracking and kerning (never auto-kerning);
  optical corrections on specific letter pairs; possible customization of
  individual characters to distinguish from the off-the-shelf typeface

### Lettermark (Monogram)
One or more initials set distinctively.
*Examples: IBM, LV (Louis Vuitton), HP, HBO*

- **Strengths**: works at small sizes; strong recognition once established
- **Weaknesses**: requires significant brand exposure to establish; meaningless
  to new audiences
- **Construction requirements**: interlock or spacing of letters must be designed
  (not just placed adjacently); the relationship between letterforms IS the design

### Pictorial Mark
A recognizable image (object, animal, person) used as a brand identifier.
*Examples: Apple, Twitter/X (bird era), World Wildlife Fund, Shell*

- **Strengths**: can communicate brand values directly through the depicted subject;
  works without language (globally legible)
- **Weaknesses**: the pictorial choice carries all its connotations — a poorly
  chosen subject brings the wrong associations; realistic images age poorly
- **Construction requirements**: simplification to essential form (a pictorial
  mark must read at 16×16px); silhouette must be distinctive at small sizes

### Abstract Mark
A non-representational form designed to carry brand associations through shape,
color, and feeling rather than through literal depiction.
*Examples: Nike Swoosh, Pepsi globe, Adidas three stripes, Chase octagon*

- **Strengths**: carries no pre-existing connotations; can be owned completely;
  highly versatile
- **Weaknesses**: meaning must be entirely constructed through use; no inherent
  communicative content — you cannot explain what it means without telling a story
- **Construction requirements**: geometric precision (usually derived from a
  consistent geometric system); must be distinguishable in all sizes and at
  any rotation used

### Combination Mark
A wordmark and pictorial or abstract mark used together, with provisions for
using either element independently.
*Examples: Starbucks, Amazon, Lacoste, Nike (in full lockup)*

- **The standard professional choice**: provides flexibility across applications
  while building both name and symbol recognition simultaneously
- **Construction requirements**: the relationship between wordmark and symbol
  must be designed (size ratio, spatial relationship, alignment baseline)

### Emblem
Mark and name integrated into a single inseparable form, typically badge-shaped.
*Examples: BMW, Harley-Davidson, Harvard crest, athletic team logos*

- **Strengths**: powerful sense of authority and heritage; high badge value
- **Weaknesses**: not flexible; cannot separate mark from name; does not work
  at very small sizes; feels traditional (which is either an asset or a liability)

---

## Mark Construction

### Geometry as Meaning Carrier

Simple geometric forms carry consistent perceptual meanings:
- **Circle**: wholeness, continuity, protection, inclusivity, movement
- **Square/rectangle**: stability, reliability, strength, structure, equality
- **Triangle (pointing up)**: ascent, achievement, dynamism, direction
- **Triangle (pointing down)**: precarity, inversion, disruption
- **Organic curves**: approachability, humanness, naturalness

**The designer's task:** select the geometry that carries the intended meaning,
then construct the mark from that geometric system. A health technology brand
might use circles (continuity, care) and organic curves (humanity). A financial
technology brand might use squares and precise angles (stability, structure).

### Proportion Systems

Marks constructed from mathematically defined proportions feel resolved —
they do not require justification for why elements are sized as they are.

**Golden ratio proportions:**
- Element width to height at φ:1 (≈1.618:1)
- Spacing between elements as 1/φ of the element size

**Root rectangle proportions:**
- Mark contained within a √2 rectangle (≈1.414:1) — self-similar when halved
- Elements subdivided using the same root-rectangle logic

**Grid-based construction:**
- Divide the mark space into a consistent grid (e.g., 10×10 or 12×12 units)
- All elements snap to grid intersections
- Curves are arcs of circles whose centers are at grid intersections

**The practical requirement:** any mark delivered to production must be
accompanied by a construction guide showing the geometric underpinning.
This is both a quality demonstration and an operational requirement — it
enables precise redrawing at any scale.

### Optical Corrections in Mark Design

Mathematical precision does not produce optical equality. The same corrections
required in typography apply to logo construction:

**Circles appear smaller than squares at the same dimension.** A circle
contained within a square bounding box reads as smaller. Circles must
be drawn slightly larger than squares to appear the same size. In mark design:
if the mark includes both circular and rectilinear forms, the circle must
extend beyond the strict geometric boundary of the rectilinear element.

**Pointed vertices appear to disappear at small sizes.** A triangle's
point needs either a slight curve or a deliberate thickening near the
tip to read at small reproduction sizes. Acute angles collapse when printed
small or embroidered.

**Horizontal and vertical strokes of equal weight do not appear equal.**
Horizontal strokes appear heavier than vertical strokes at the same geometric
width. Compensate by drawing horizontals approximately 5% thinner.

**Visual center is above mathematical center.** A mark centered mathematically
in its container feels low. Shift the optical center upward by 2–4% to
correct this.

---

## Identity Systems

A logo mark is the nucleus of an identity, not the whole. A complete identity
system provides all the elements needed to communicate consistently across
every application.

### System Components

**Color palette**: Primary brand colors (1–2 dominant), secondary palette
(3–5 supporting), neutral palette (2–4 grays and off-whites). Each color
specified in all four modes: Pantone, CMYK, RGB, and HEX.

**Typography**: One or two typefaces assigned to specific roles (display,
body, UI, caption). Usage rules specifying which typeface appears where.
Specify complete technical details: name, source/license, weights in use,
tracking rules, hierarchy rules.

**Imagery style**: Photographic treatment (color grade, crop style, subject
matter guidelines), illustration style (flat/line/textured/painterly),
iconography style (line weight, corner radius, visual language). These are
the hardest components to document and the most common source of brand drift.

**Layout principles**: Column grid(s), margin standards, logo placement rules,
proportional frameworks. If the brand uses a recurring compositional approach
(asymmetric, centered, bleed-heavy), document it explicitly.

**Tone of voice** (sometimes shared with brand strategy, not just visual design):
the written voice that accompanies visual decisions. Typography choices and
voice register must be consistent — a brand that sets type in a geometric sans
with strict spacing but writes in casual, warm language creates a mixed message.

### Identity Application Priority

The system must specify how all components combine across each application:
business card, letterhead, digital advertising, social media profile, website,
signage, merchandise, vehicle livery, etc. Each application has different
constraints (size, reproduction method, substrate); the identity must flex
without losing coherence.

---

## Brand Standards Documentation

Brand standards (brand guidelines, identity manual) are the authoritative record
of how the identity must be used.

### Essential Contents

**Mark and variants**: primary lockup, responsive variants (simplified versions
for small sizes), standalone symbol, standalone wordmark, all approved proportional
combinations.

**Color specifications**: every brand color in Pantone (coated + uncoated),
CMYK (coated), CMYK (uncoated), RGB, HEX, and OKLCH if the system is being
built to modern standards. Never only specify hex.

**Clear space**: the minimum protective zone around the mark, defined in
relation to a mark element (e.g., "minimum clear space = height of the X in
the wordmark"). This is the non-negotiable buffer that prevents the mark from
competing with adjacent content.

**Minimum sizes**: the smallest reproduction size at which the mark remains
legible. Provide both print (mm) and screen (px) specifications. Test these
specifications — they are easy to specify incorrectly.

**Prohibited uses**: explicit visual examples of what is not permitted.
Common prohibitions: recoloring the mark, stretching, adding effects (drop
shadow, outline, glow), rearranging elements, placing on unapproved backgrounds,
using a deprecated variant. Showing violations is more effective than
describing them.

**Typography rules**: all the typeface and usage specifications from the system
components above, with worked examples.

**Approved backgrounds**: the exact set of backgrounds on which the mark may
appear. For each background, specify which variant (positive/reverse/single-color).

---

## Brand Architecture

When an organization has multiple brands or sub-brands, the relationship between
them is a strategic decision called brand architecture.

### Monolithic (Branded House)
All products and services carry the parent brand.
*Examples: Virgin (Virgin Atlantic, Virgin Mobile, etc.), Apple (iPhone, iPad,
Mac), FedEx (FedEx Express, FedEx Ground)*

- **Strength**: every product builds the parent brand; clear, simple system
- **Weakness**: brand failures in one area affect all areas; limits personality
  differentiation by product line

### Endorsed (House of Brands with Endorsement)
Sub-brands operate independently but carry the parent's endorsement.
*Examples: Marriott (Marriott Bonvoy, Courtyard by Marriott, Ritz-Carlton by Marriott),
Nestlé (KitKat Nestlé)*

- **Strength**: sub-brands can develop distinct personalities while drawing
  credibility from the parent; failure containment
- **Weakness**: complex system to manage; parent diluted if endorsement is too
  prominent across too many diverse sub-brands

### Pluralistic (House of Brands)
Each brand operates independently with no visible parent connection.
*Examples: Procter & Gamble (Tide, Pampers, Gillette), Unilever (Dove, Axe, Ben & Jerry's)*

- **Strength**: brands can target contradictory audiences; corporate failure
  containment; maximum brand personality per product
- **Weakness**: no cross-brand equity building; expensive to maintain multiple
  full identity systems

**Selection criteria**: business goals, competitive dynamics, reputational risk
distribution, target audience overlap (or desired separation), and available
investment in brand maintenance.

---

## Brand in Digital Products

A brand designed primarily for print must be re-evaluated for screen.
This is a translation problem, not a rendering problem.

### Pixel-Rendering Constraints
- Fine details in a logo mark disappear at small screen sizes and standard
  resolution (1x). Test every mark variant at intended screen sizes before approving.
- Hairline strokes and acute angles that work in print will anti-alias into
  blurriness at 1x screen resolution. Consider a simplified "screen variant"
  for small applications (favicon, app icon, avatar).
- The standard set of mark variants must include: standard lockup, reversed
  lockup, monochrome positive, monochrome negative, and minimum-size simplified
  variant.

### Dark Mode Behavior
- A brand with a dark mark on white will need a light version on dark backgrounds.
  The reversed version is not simply "white on dark" — the color relationships
  must be re-evaluated. A brand color that reads as primary on white may not read
  as primary on a dark background at the same saturation.
- Pantone/CMYK colors specified for print will require separate RGB values for
  each brand color in dark mode context. Specify these explicitly.

### Animation Potential
- Modern digital brand identities should consider how the mark might be
  animated (for loading states, transitions, brand moments). Design the static
  mark with animation in mind — a mark with geometric structure that can be
  drawn, assembled, or transformed is more versatile than one that must simply
  appear.

---

## Anti-Patterns

- **Logo without system**: a mark delivered without color palette, typography,
  and imagery style leaves the brand identity incomplete and inconsistent
  in application.
- **Only HEX specification**: brand color specified in HEX only cannot be
  used in print. Every brand color requires Pantone, CMYK, RGB, and HEX — all four.
- **No minimum size specification**: a mark with no documented minimum size
  will be scaled down to illegibility in application.
- **No prohibited uses examples**: written prohibitions are forgotten;
  visual examples of violations are remembered.
- **RGB-only mark construction**: a mark built only in RGB will not translate
  cleanly to print. Work in CMYK+Pantone from the start for print-inclusive brands.
- **Emblem for digital-first brands**: emblem formats are detail-rich and
  fail at small sizes; avoid for brands where the primary touchpoint is app icons
  and favicons.
- **Brand architecture by accident**: sub-brand visual relationships that
  emerged organically without a defined architecture produce confused family
  hierarchies that are expensive to rationalize later.

---

## Cross-Links

- **`gd-color-theory`**: every brand color must be specified in Pantone, CMYK,
  RGB, and HEX; color model understanding is prerequisite; Pantone coated/uncoated
  behavior affects brand color consistency across substrates
- **`gd-typography`**: typeface selection for brand identity requires full
  typographic analysis (classification, historical context, technical quality)
- **`gd-print-production`**: mark delivery standards (vector files, color
  mode, PDF/EPS specifications) are print production requirements
- **`lead-ui-designer` / `uid-visual-system`**: the brand identity spec is
  the upstream source for the product visual language; brand color, typography,
  and imagery style become the starting constraints for product design
- **`ds-advisor`**: brand color specifications (Pantone/CMYK/RGB) become the
  primitive brand color tokens in a design system; brand typography choices
  constrain the DS type system; the brand color palette defines the top level
  of the token hierarchy before semantic tokens are derived from it
- **`lead-type-designer`**: custom typeface commissions for brand identity;
  the brand brief defines the type design requirements

---

## References

- Wally Olins: *The Corporate Personality* (1978); *Brand New* (2014)
- Alina Wheeler: *Designing Brand Identity* (5th edition, 2017)
- Michael Bierut: *How to Use Graphic Design to Sell Things* (2015)
- Paul Rand: *A Designer's Art* (1985); *Design, Form and Chaos* (1993)
- Pantone LLC: Pantone Matching System standards
- ISO 3098: Technical drawing — lettering (for mark specification documentation)
