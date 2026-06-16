---
name: uid-visual-critique
description: >
  Aesthetic evaluation frameworks, visual QA methodology, and style consistency
  audits for digital interfaces. Use this skill when the conversation touches:
  critiquing a screen design, visual hierarchy evaluation, the blur test, gestalt
  analysis of a layout, tonal range audits, type consistency audits, color
  discipline audits, density audits, brand consistency evaluation, the five-second
  test for visual communication, evaluating whether a design "looks right," or
  any structured quality evaluation of visual design output. This spoke provides
  the frameworks for making aesthetic judgment precise, communicable, and
  actionable. Part of the lead-ui-designer hub skill network.
---

# UID: Visual Critique

Specialist spoke for aesthetic evaluation and visual quality assessment.
Part of the `lead-ui-designer` hub skill network.

---

## Domain Boundary

This spoke owns **structured aesthetic evaluation**: frameworks for analyzing
visual design output and making judgment communicable and actionable.

- **Design system compliance checks (tokens, components, patterns)** → `ds-advisor`
- **Accessibility criteria in visual evaluation** → `lead-accessibility-architect`
- **Usability/behavior evaluation of components** → `lead-ux-designer` / `ux-design-systems`
- **Semiotic and rhetorical analysis depth** → `gd-visual-communication`

---

## Operating Principle

"I'll know it when I see it" is not a professional critique standard. Aesthetic
quality can be named, described, and evaluated using frameworks. A skilled visual
designer can explain precisely why something looks wrong and specify what change
would fix it.

This spoke provides those frameworks. Use them explicitly when critiquing or
evaluating design output — not as a checklist, but as lenses that each reveal
different aspects of visual quality.

A critique that can't be acted on has no value. Every observation should
conclude with a specific change.

---

## Fast Tests (Run These First)

Three quick diagnostics that reveal the most common problems before formal analysis.

### The Blur Test

**How**: Squint at the screen until it blurs, or apply a 4–6px gaussian blur.

**What it reveals**:
- **Does hierarchy still read?** After blurring, can you tell which element is
  primary, secondary, tertiary? If the hierarchy disappears when you remove detail,
  it was built on decoration rather than structure.
- **Where does the eye land first?** The first element that resolves through the
  blur should be the most important element on the screen. If it's the navigation
  chrome, a decorative illustration, or a status badge — hierarchy is wrong.
- **Are there unintended focal points?** Elements you didn't intend to be dominant
  often reveal themselves in the blur view (overweight borders, saturated background
  sections, heavy shadow use).
- **Icon set weight**: Apply to an icon grid — all icons should reduce to
  approximately the same gray value. Outliers need weight adjustment.

**This is the fastest and most valuable visual test.** Run it first, always.

### The Brand Test

**How**: Strip all text from the screen. Show only the visual chrome, colors,
surfaces, and icons.

**What it reveals**:
- Does this screen look like it belongs to this product? Is the visual language
  coherent with the style guide?
- Could you distinguish this product from a competitor's by visual language alone?
- Unbranded elements are design debt — they look like they were built by a
  different team (because they often were).

**Common failure**: A product with a distinctive brand color and icon style that
has a data table with generic column headers, default-browser-style borders, and
unstyled form inputs — the table is "in" the product but not "of" it.

### The Five-Second Test (Visual Version)

**How**: Show the screen for 5 seconds, then hide it. Ask: what did you notice first?

**What it reveals**:
- The answer should match the information hierarchy intent. The first thing noticed
  should be the most important thing on the screen.
- If the first thing noticed is navigation, decoration, or a badge status — the
  primary content does not have sufficient visual dominance.
- Useful for confirming that visual hierarchy decisions work in practice, not
  just in careful analysis.

---

## Gestalt Critique

The Gestalt principles describe how the human visual system automatically organizes
visual information. Critiquing against them reveals structural problems that feel
"off" but are hard to name without the vocabulary.

### Proximity

**Question**: Are related elements close together? Are unrelated elements separated?

**Diagnostic**: Identify all element groups on the screen. For each group, measure
the gap between elements inside the group vs. the gap between groups. If those gaps
are equal or similar, grouping is not working.

**Common failure**: A form where the gap between label and input is the same as
the gap between input and the next label. The form reads as an undifferentiated list
because proximity isn't encoding the label-input relationship.

**Fix**: Reduce the gap between label and its input by 50–60%. Increase the gap
between form field groups. The contrast between these gaps is what creates grouping.

### Similarity

**Question**: Are elements that belong to the same category visually alike?
Are elements that belong to different categories visually different?

**Diagnostic**: Group all text on the screen by its role (page title, section
header, body, label, caption, metadata). Within each role group — do all instances
use the same style? If not, similarity is broken.

**Common failure**: "Body text" at 14px in some components and 15px in others,
or some at weight 400 and others at 450. Users perceive these as different
categories even when they're meant to be the same.

**Fix**: Audit all text instances against the type scale. Non-scale values are
inconsistency unless explicitly documented as exceptions.

### Continuity

**Question**: Does the eye flow naturally through the layout? Are there alignment
breaks that interrupt scanning?

**Diagnostic**: Draw invisible lines through the screen along the left edges, top
edges, and baseline edges of key elements. Elements that should belong to the same
reading flow should align to a common axis.

**Common failure**: Three cards in a row where the card title text doesn't sit
at the same baseline. The eye tries to read across the row (continuity) but
misaligned baselines break the flow, creating cognitive friction.

**Fix**: Establish and enforce alignment axes. In Figma: use auto-layout and
alignment settings to ensure consistent baselines.

### Closure

**Question**: Do containers and regions need explicit borders to read as bounded,
or does spacing and background color create closure?

**Diagnostic**: Can you identify which elements belong together without visible
borders? If removing a border makes a card or form section fall apart visually —
the closure is dependent on decoration rather than structure.

**Insight**: In data-dense enterprise UIs, over-reliance on visible borders
creates visual noise. Background color differentiation + sufficient padding
provides closure with less visual weight than borders.

### Figure/Ground

**Question**: Is it always clear what is content (figure) and what is surface
(ground)?

**Diagnostic**: Can you immediately tell which elements are interactive and which
are structural? Can you tell which elements carry meaning and which are decorative?

**Common failure**: A lightly-tinted background on a section that could be read
as either a surface (ground) or a highlight (figure). Ambiguous figure/ground
is visually uncomfortable and often signals a color decision that's "in between"
two intentions.

**Fix**: Commit to one interpretation and make it unambiguous. Surfaces are
meaningfully different from highlights — use distinct lightness levels.

---

## Tonal Range Audit

**What it measures**: Does the design use the full value range from light to dark?
Designs without sufficient tonal range look flat and have weak hierarchy.

**Diagnostic**:
1. Desaturate the screen to grayscale
2. Assess the range from lightest to darkest element
3. Is there a full range from near-white to near-black? Or are all elements
   clustering in a narrow midrange?
4. Are the darkest elements your primary content? Are the lightest elements
   your background surfaces?

**Common failure in enterprise**: "Safe" design choices that avoid strong
contrast — everything sits between L=40% and L=85% — resulting in a design
that looks washed out and low-energy. No shadows, no dark type, no strong
hierarchy signals.

**Fix**: Ensure body text is at sufficient darkness (APCA ≥ 75 on body, ≥ 90
on small text). Ensure the darkest element on the page has genuine visual weight.
Don't avoid contrast to seem "minimal" — absence of tonal range is not minimalism,
it's poor hierarchy.

---

## Type Consistency Audit

**Purpose**: Verify that the type scale is being applied correctly and
consistently.

**Method**:
1. Audit every text instance on the screen or in the component
2. Record: size, weight, line-height, color, letter-spacing
3. Map each instance to its scale level
4. Flag: values not in the scale, inconsistent application of the same level,
   weight or size mismatches between components

**Common failures**:
- Same type level (e.g., "card title") at 16px in one component and 18px in another
- Decorative weight applications: bold text where the content doesn't warrant
  emphasis — "bold" used because it looks good, not because it signals importance
- Unscaled type: pixel values that don't correspond to any scale step
  (17px, 13px, 21px)

**Output format**: Report inconsistencies as: "[Location]: [Value] — should be [Scale level: Value]."
Do not just list problems; specify the fix.

---

## Color Discipline Audit

**Purpose**: Verify that color is being used systematically — only where it
carries meaning, from the defined palette, for the defined role.

**Method**:
1. Identify every non-neutral color on the screen
2. For each: is this a brand color, semantic color, or accent? Is it in the palette?
3. Is it being used for its defined role? (Success green on a decorative divider = wrong role)
4. Are there rogue hex values outside the palette?

**Common failures**:
- Semantic green used as an accent or decorative color: violates the signal contract
- Multiple different blues in the same interface: brand blue, link blue, info blue —
  three different values that look similar but aren't coordinated
- "Ad hoc tinting" — a background section that was tinted to differentiate it
  using a hex value that's not in the palette

**Output format**: List each off-palette or off-role color use, identify the
palette value it should be replaced with, and flag if a token is missing.

---

## Density Audit

**Purpose**: Identify whether every visual element is serving a purpose or
adding decorative complexity.

**Method**: Apply the "if I removed this, would anything be lost?" test to
every non-content visual element:
- Decorative dividers
- Background illustrations
- Border treatments
- Gradient overlays
- Multiple shadow levels
- Animated micro-interactions
- Ornamental icon uses

**Common failure**: Visual complexity added to make a screen feel "polished"
without a specific functional purpose. In data-dense enterprise UIs, decorative
complexity competes with data for attention. Every decorative element is
reducing the signal-to-noise ratio.

**Standard**: If an element doesn't carry information, create grouping, signal
state/status, or reinforce the visual hierarchy — it should be removed or
significantly reduced. This isn't minimalism as an aesthetic — it's
clarity as a design value.

---

## Structured Critique Format

When writing up a visual critique, use this format. Avoid vague language ("looks
off"). Name the principle, describe the observation, specify the fix.

```
## Visual Critique — [Screen / Component Name]

**Blur test result**: [What resolves first? Does hierarchy hold?]
**Brand test result**: [Does it look like the product?]

### Hierarchy
- [Observation] → [Fix]
- ...

### Gestalt Issues
- [Principle: Proximity/Similarity/Continuity/Closure/Figure-Ground] — [Observation] → [Fix]
- ...

### Tonal Range
- [Range assessment] → [Fix if needed]

### Type Consistency
- [Issue: location, value, should be] → [Fix]
- ...

### Color Discipline
- [Issue: location, value, role conflict] → [Fix]
- ...

### Density
- [Element, location] — [justification for removal or retention]

### Priority fixes (top 3)
1. [Most impactful change, with specific instruction]
2.
3.
```

Keep critiques actionable. A critique that identifies 15 problems is only
useful if it also identifies which 3 to fix first.

---

## Anti-Patterns in Visual Critique

**Avoid**:
- "It looks off" without naming the specific principle being violated
- Aesthetic preference framed as a principle ("I prefer more whitespace" ≠ hierarchy analysis)
- Identifying a problem without specifying a fix
- Critiquing the concept rather than the execution — unless the concept is the problem
- Piling on: identifying every possible issue when only 3–5 high-impact ones matter for this stage

**Useful framing patterns**:
- "The hierarchy breaks because [principle]. Fix: [change]."
- "This element is doing double duty: [role A] and [role B]. It should do only [one]. Fix: [change]."
- "The [component] is visually heavier than [important element]. Reduce by [change]."

---

## Cross-Links

- `gd-visual-communication` — semiotic evaluation and visual rhetoric as evaluation depth
- `ds-advisor` — design system compliance checks (tokens, components, documented patterns)
- `lead-accessibility-architect` — accessibility criteria in visual evaluation (contrast, size)
- `lead-ux-designer` / `ux-design-systems` — component and interaction pattern evaluation
- `uid-visual-system` — evaluating against the defined visual language standard
- `lead-visual-qa` / `visual-qa-ui-design` — when output is ready for a structured quality pass
- `lead-icon-artist` — icon-specific critique (visual weight, metaphor, keyline adherence)
