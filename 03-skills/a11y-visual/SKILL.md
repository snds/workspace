---
name: a11y-visual
description: >
  Visual impairments, blindness, low vision, color vision deficiency, screen reader
  design, focus indicators, and alt text. Spoke skill in the lead-accessibility-architect
  network. Use this skill whenever the conversation touches: color contrast, color
  blindness, deuteranopia, protanopia, tritanopia, achromatopsia, low vision, legal
  blindness, total blindness, screen reader, NVDA, JAWS, VoiceOver, TalkBack, alt text,
  image descriptions, skip navigation, heading hierarchy, reading order, focus indicator,
  focus visibility, WCAG 1.4.3, WCAG 1.4.11, WCAG 2.4.7, WCAG 2.4.11, APCA, color
  contrast ratio, non-text contrast, text alternatives, decorative images, form labels,
  link text, accessible name, screen reader markup, ARIA labels, landmark regions,
  semantic HTML, low vision design, zoom support, text scaling, relative units, reflow,
  color as information.
aliases: [a11y-visual]
triggers: [contrast, color contrast, color blindness, color vision deficiency, cvd, wcag, apca, focus indicator, screen reader, alt text, legibility, non-text contrast, low vision, color as information]
tier: cross-cutting
domain: accessibility
spec_version: "2.0"
---

# a11y-visual

Specialist lens for visual impairments, color vision deficiency, screen reader design,
and focus visibility. Part of the `lead-accessibility-architect` skill network.

---

## Domain Boundary

This skill owns **visual disability design** — color, contrast, screen reader markup,
reading order, focus states, and alt text.

- **Legal standards and audit methodology** → `a11y-legal-compliance`
- **AT internals (how screen readers work)** → `a11y-assistive-tech`
- **Font selection and text sizing** → `lead-type-designer`
- **Color palette design within accessibility constraints** → `uid-color-for-ui` (with this spoke as authority)

---

## Visual Impairment Spectrum

Visual impairment is not binary. Each point on the spectrum requires different
design responses:

| Classification | Description | Design Priority |
|---------------|-------------|-----------------|
| Total blindness | No light perception (<3% of visually impaired) | Screen reader support, semantic structure |
| Legal blindness | Visual acuity ≤20/200 or field <20°, significant functional limitation | Screen reader + zoom support, high contrast |
| Low vision | Functional vision with accommodation (most of the 253M) | Zoom, contrast, text sizing, clear layout |
| Color vision deficiency | Normal acuity, impaired color discrimination (~8% of males) | Color-independent information encoding |
| Age-related changes | Reduced contrast sensitivity, yellowing lens (affects nearly everyone 60+) | Contrast, text size, reduced blue sensitivity |

**Anti-pattern**: Designing only for total blindness. The vast majority of visually
impaired users have low vision — they see content, but struggle with low contrast,
small text, and cluttered layouts. Screen reader testing is necessary but not
sufficient.

---

## Color Vision Deficiency (CVD)

~8% of males and ~0.5% of females have some form of CVD. In a product with
10,000 male users, ~800 have CVD. This is not an edge case.

### CVD Types

| Type | Prevalence | Impairment | Failure Mode |
|------|-----------|-----------|--------------|
| Deuteranopia / Deuteranomaly | ~6% of males | Reduced green sensitivity | Red and green are indistinguishable |
| Protanopia / Protanomaly | ~2% of males | Reduced red sensitivity | Red appears very dark; red/green confusion |
| Tritanopia / Tritanomaly | Very rare | Reduced blue sensitivity | Blue/yellow confusion |
| Achromatopsia | Very rare | No color discrimination | Design must work in grayscale |

Deuteranopia and protanopia together account for nearly all CVD. The critical
failure: **using red and green alone to communicate opposite meanings** (error/success,
required/optional, on/off). This is the most common CVD failure in UI design.

### CVD Design Rules

1. **Never use color as the only differentiator** — always pair with:
   - Shape or icon (✓ vs ✗ rather than green vs red)
   - Pattern (fill pattern vs solid in charts)
   - Label or text (explicit state name)
   - Position (consistent placement of positive/negative states)
   - Border or thickness

2. **Test with a CVD simulation tool** at every design review:
   - Figma: Stark plugin or built-in accessibility checker
   - Browser: Chrome DevTools → Rendering → Emulate vision deficiencies
   - macOS: Accessibility → Display → Color Filters

3. **Colorblind-safe palette patterns**:
   - Blue/orange is a highly robust pair — legible under all common CVD types
   - Avoid red/green as primary semantic pair
   - If you must use red, pair with a shape indicator, never rely on the color alone
   - Tableau, ColorBrewer, and Viz Palette provide CVD-verified data visualization palettes

4. **Charts and data visualization**: Hue alone is insufficient for encoding categorical
   data when there are more than 2-3 categories. Use hue + saturation + lightness variation,
   or supplement with direct labels, patterns, or dashed vs. solid lines.

---

## Contrast Standards

### WCAG Contrast Ratios (Current Legal Standard)

Contrast ratio is calculated from relative luminance (W3C formula). Range is 1:1 (no contrast)
to 21:1 (black on white).

| Content | Minimum (AA) | Enhanced (AAA) |
|---------|-------------|----------------|
| Normal text (<18pt / <14pt bold) | 4.5:1 | 7:1 |
| Large text (≥18pt / ≥14pt bold) | 3:1 | 4.5:1 |
| UI components (borders, icons) | 3:1 | — |
| Focus indicators | 3:1 minimum area (WCAG 2.2) | — |
| Decorative elements | No requirement | — |
| Disabled states | No requirement | — |

**WCAG 1.4.3** (text contrast) and **WCAG 1.4.11** (non-text contrast) are the
two most commonly failed contrast criteria. Non-text contrast at 3:1 covers:
form input borders, icon-only buttons, focus rings, and active chart elements.

### APCA (Accessible Perceptual Contrast Algorithm)

APCA is the proposed replacement for WCAG's contrast ratio in WCAG 3.0. It is
significantly more accurate at predicting whether text is actually readable:

- WCAG 1.4.3 passes 18px white text on a medium-blue background — APCA correctly
  flags this as insufficient for normal-weight body text
- WCAG 1.4.3 fails a light-gray large heading on white — APCA correctly identifies
  it as acceptable for display sizes
- APCA is asymmetric: light text on dark vs. dark text on light have different
  perceptual weight curves

**Current recommendation**: Meet WCAG 1.4.3 (required) and verify with APCA (best
practice). Use Lc (lightness contrast) ≥ 60 for body text, ≥ 45 for large/bold text,
≥ 30 for UI elements as APCA starting targets.

**Tier note (2026-07-08)**: the values above are the accessibility FLOOR — the bare
minimum any delivered artifact must meet. Working *targets* for comfortable reading sit
higher: see the APCA threshold table in `design-engineer/references/visual-design-theory.md`
(Lc 75 preferred body, Lc 90 small/critical text — the "happy middle," barring real
concerns). Stricter targets in [[radix-derived-color-system]] (~Lc 90 body) are
Radix-scale-specific and apply only to Radix-derived palettes.

**Tools**: APCA Contrast Calculator (apcalc.github.io), Polypane, Stark.

### Common Contrast Anti-Patterns

- Placeholder text with insufficient contrast (often fails 4.5:1 because "it's not
  real text" — WCAG doesn't make this exception for users)
- Disabled state text that's too light (exempted from contrast requirements, but
  if content conveys meaningful information, consider higher contrast anyway)
- Focus indicators that rely only on a thin outline on a background that has
  only 1.5:1 contrast with the outline color
- Icon-only buttons without 3:1 contrast between the icon and its background
- Border-radius reducing the visible border width, causing a previously compliant
  border to fail 3:1 at the rounded corners

---

## Low Vision Design

Low vision users are the majority of visually impaired users. They often use
magnification, custom fonts, high contrast modes, or system display settings
rather than screen readers.

### Text Scaling

**WCAG 1.4.4 Resize Text**: Text must be resizable to 200% without loss of content
or function. This means:

- Use relative units (`rem`, `em`, `%`, `vw`) for text sizes, not `px`
- Never set `max-height` on content containers that could clip text when scaled
- Avoid `overflow: hidden` on containers that hold text
- Test by setting browser default font size to 24px (equivalent to 150% browser zoom)
  and verifying all text, layout, and interactive elements remain functional

**WCAG 1.4.10 Reflow**: Content must be presentable in a single column at 320px
viewport width (equivalent to 400% browser zoom on 1280px) without requiring
horizontal scrolling. This is the 400% zoom test.

Exceptions: complex data tables, maps, diagrams where spatial layout is intrinsic.
But even these need an alternative if they contain functional information.

### Typography for Low Vision

- Minimum body text size: 16px equivalent (1rem at browser default); 14px is the
  WCAG lower bound for "large text" — use 16px as the practical floor
- Line height: 1.5× line-height for body text minimum (WCAG 1.4.12 Text Spacing)
- Letter spacing: avoid tight tracking; WCAG 1.4.12 requires the design to tolerate
  0.12em letter spacing without content loss
- Paragraph spacing: 2× font size minimum (WCAG 1.4.12)
- Font selection: high x-height, clear letterform differentiation (b/d/p/q, 1/I/l/0/O),
  open apertures — route to `lead-type-designer` for specific font recommendations

### WCAG 1.4.12 Text Spacing

Content must not lose functionality when the user overrides:
- Line height to 1.5× font size
- Letter spacing to 0.12em
- Word spacing to 0.16em
- Paragraph spacing to 2× font size

This is a layout test, not a visual design preference. Containers that clip
text, tooltips that collapse, or overlapping elements when text spacing is forced
are WCAG 1.4.12 failures.

---

## Screen Reader Design

Screen readers are the primary AT for blind users and many low vision users.
Design decisions that affect screen reader users include reading order, semantic
structure, and text alternatives.

### Reading Order

The DOM order determines screen reader reading order. Visual layout ≠ DOM order
when CSS positioning, flexbox `order`, or grid placement are used.

**Rule**: The logical reading order must match DOM order. Never rely on `tabindex`
manipulation or CSS visual ordering to fix a broken DOM order — fix the DOM.

**Common failure**: A visual design where sidebar content appears before main content
in the DOM for layout reasons, but the screen reader announces sidebar (navigation,
ads, related content) before the main content the user came for.

### Heading Hierarchy

Screen reader users navigate by heading (H key in NVDA, JAWS). Heading hierarchy
communicates document structure:

- One `<h1>` per page (the page title or primary purpose)
- Do not skip heading levels (no `<h1>` followed immediately by `<h3>`)
- Headings must reflect actual content hierarchy — don't use `<h2>` because of its
  visual styling; apply the heading level that reflects the information architecture
- Visual-only headings (dividers styled to look like section titles) must be marked
  up as actual heading elements

**Anti-pattern**: Using heading elements purely for their default visual styling
(large bold text) rather than their semantic meaning. Style any element with CSS.

### Skip Navigation

WCAG 2.4.1: A mechanism must exist to bypass blocks of content that are repeated
across pages. The most common implementation:

```html
<a href="#main-content" class="skip-link">Skip to main content</a>
```

The link is typically visually hidden until focused (`:focus-within` shows it).
It must be the first focusable element on the page. The target `#main-content`
must actually exist as an anchor.

### Landmark Regions

ARIA landmarks allow screen reader users to navigate directly to regions of the
page (R key in NVDA/JAWS cycles through landmarks):

| Role | HTML Element | Use |
|------|-------------|-----|
| `banner` | `<header>` | Site header (once per page) |
| `navigation` | `<nav>` | Navigation regions |
| `main` | `<main>` | Primary content |
| `complementary` | `<aside>` | Secondary/supporting content |
| `contentinfo` | `<footer>` | Site footer (once per page) |
| `search` | `role="search"` | Search form |
| `form` | `<form aria-label>` | Named forms |

Label duplicate landmarks with `aria-label` or `aria-labelledby`:
```html
<nav aria-label="Primary">...</nav>
<nav aria-label="Breadcrumb">...</nav>
```

### Text Alternatives

**WCAG 1.1.1 Non-text Content** — all non-text content needs a text alternative.

| Image Type | Alt Text Approach |
|-----------|------------------|
| Informative (conveys content) | Describe the information, not the image ("Chart showing Q3 revenue up 23%") |
| Functional (icon button, linked image) | Describe the function ("Open account settings") |
| Decorative | `alt=""` (empty alt, not missing) — tells screen reader to skip it |
| Complex (chart, diagram, map) | Short alt + linked/adjacent long description or data table |
| Text in image | The exact text rendered in the image |

**Common failures**:
- `alt="image"` or `alt="photo"` — describes file type, not content
- `alt="[filename].jpg"` — file name is not alt text
- Missing `alt` attribute (not the same as `alt=""`) — screen reader reads the file URL
- Icon buttons with no accessible name: `<button><svg>...</svg></button>` announces nothing

**Accessible name for icon buttons**: Use one of:
- `aria-label="Close dialog"` on the button
- `<title>Close dialog</title>` inside the SVG
- Visually hidden text: `<span class="sr-only">Close dialog</span>`

### Link Text

**WCAG 2.4.6 Headings and Labels** and **WCAG 2.4.4 Link Purpose**: Link text must
identify the destination or purpose in context.

**Failure**: "Click here", "Read more", "Learn more" — screen reader users can
navigate by link list (JAWS: `INSERT+F7`). A list of "Read more" links is meaningless
out of context.

**Fix**: Either make the link text descriptive ("Read more about WCAG 2.2") or use
`aria-label` or `aria-labelledby` to provide context: `<a href="..." aria-label="Read more about WCAG 2.2">Read more</a>`

---

## Focus Indicators

**WCAG 2.4.7 Focus Visible** (AA) and **WCAG 2.4.11 Focus Appearance** (AA, new in 2.2):

- All keyboard-focusable elements must have a visible focus indicator
- WCAG 2.4.11: The focus indicator must have a minimum perimeter of the component's
  perimeter, and the focus color must have at least 3:1 contrast against both the
  focused component and the unfocused state

**Design the focus state** as explicitly as any other interactive state (hover, active,
pressed). `outline: none` or `outline: 0` without a visible replacement is a WCAG
2.4.7 failure. Common browser default focus rings are often insufficient in custom
designs.

**Focus indicator design principles**:
- Visible without relying on color alone (shape change, added border, or fill change)
- 3:1 minimum contrast between focus indicator and its surrounding area
- Large enough to see at 200% zoom
- Consistent across all interactive components — don't design 15 different focus styles

---

## Quality Checklist

Before shipping any visual UI component:

- [ ] All text meets 4.5:1 contrast minimum; large text meets 3:1
- [ ] UI components (borders, icons, chart elements) meet 3:1
- [ ] No information conveyed by color alone — paired with shape, label, or pattern
- [ ] CVD simulation reviewed (deuteranopia simulation at minimum)
- [ ] All images have appropriate alt text (informative: descriptive; decorative: `alt=""`)
- [ ] Icon-only buttons have an accessible name (`aria-label` or visually hidden text)
- [ ] All link text is descriptive in context
- [ ] Focus indicator is visible and meets 3:1 contrast
- [ ] Heading hierarchy is logical and not skipped
- [ ] Landmark regions present and labeled if duplicated
- [ ] Skip navigation link present on page
- [ ] DOM order matches reading order
- [ ] Text uses relative units; layout tolerates 200% text size
- [ ] Layout reflowable to 320px viewport width without horizontal scrolling

---

## Related
- governs → [[gd-color-theory]] · [[uid-color-for-ui]]
