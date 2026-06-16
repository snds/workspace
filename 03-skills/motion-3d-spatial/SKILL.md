---
name: motion-3d-spatial
description: >
  3D reasoning in 2D frames — CSS perspective transforms, depth layers, card flip
  patterns, parallax, and spatial relationships in flat interfaces. Use this skill
  whenever the conversation touches: CSS 3D transforms, perspective, perspective-origin,
  transform-style: preserve-3d, rotateX/Y/Z, translateZ, card flip animation,
  backface-visibility, parallax effects, depth layers, scroll-linked 3D, three.js
  in interfaces, WebGL for UI, spatial transitions, modal rise, depth hierarchy in
  flat design, Z-axis motion, or any question involving depth, perspective, or
  three-dimensional reasoning in a 2D screen context.
aliases: [motion-3d-spatial]
tier: spoke
domain: design
hub: lead-motion-designer
prerequisites: [lead-motion-designer]
spec_version: "2.0"
---

# Motion 3D Spatial

Specialist lens for three-dimensional reasoning in flat digital interfaces —
from CSS perspective transforms to WebGL, and the spatial reasoning principles
that inform better flat animation. Part of the lead-motion-designer skill network.

---

## Domain Boundary

This skill owns **depth, perspective, and Z-axis motion** in digital interfaces.

- **Performance cost of 3D transforms** → `motion-performance`
- **Which transition type to use for a specific element** → `motion-transitions`
- **Disney principle 11 (Solid Drawing) foundations** → `motion-principles`
- **Accessibility: parallax reduced-motion alternatives** → `motion-accessibility`
- **Three.js or WebGL implementation** — this skill covers design and approach;
  for implementation engineering, cross-reference `fe-performance`

---

## Why 3D Reasoning Improves 2D Motion

The most important principle in this skill is that you don't need to use 3D
effects to benefit from 3D thinking.

Every flat interface has an implied Z-axis. Modals are "above" the page surface.
Dropdowns "hover" over the content. Drawers slide in "from behind" the edge.
Tooltips float "in front of" their anchor. The Z-stack exists whether you render
it in 3D or not.

When a motion designer understands how objects behave in three-dimensional space —
how perspective foreshortens distant objects, how near objects occlude far ones,
how something travels through depth — their flat animations become more physically
plausible. The modal that scales from 95% to 100% on enter makes sense because
it's simulating travel from a point slightly further from the viewer toward the
viewer. The drawer that slides in from the edge makes sense because it was "behind"
the edge.

3D reasoning answers: *Where does this element "live" when it's not visible?*
Knowing that answer produces transitions that feel spatially coherent rather than
arbitrary.

---

## The Interface Spatial Model

Before applying any 3D effects, establish the interface's spatial model — a
consistent mental map of where elements exist in the Z-stack.

### Surface Metaphor (Material Design influenced)

Think of the interface as a physical surface with objects at varying elevations:

| Layer | Elevation | Motion Behavior |
|-------|-----------|-----------------|
| Base surface | Z=0 | Static; page background |
| Cards / content | Z=1–2 | Lift on hover (subtle shadow + scale) |
| Persistent panels | Z=4–8 | Slide in from edges; at consistent elevation |
| Modals / dialogs | Z=24 | Rise from below (scale-in), cast shadow |
| Tooltips / popovers | Z=32+ | Appear in front; minimal motion |
| Overlays / scrim | Z=16–20 | Backdrop behind modal |

The elevation model defines which elements can occlude others, the direction of
shadow casting, and how elements should move relative to each other.

**Consistency requirement**: Once established, the spatial model must be applied
consistently. A modal that "rises" (scale-in) in one part of the app should
"rise" everywhere. A drawer that slides from the right is always at the same
elevation. Spatial inconsistency destroys the spatial model the user is building.

---

## CSS 3D Transforms — Technical Vocabulary

### The Key Properties

```css
/* Establishes the perspective depth — lower values = more dramatic */
perspective: 800px;          /* Set on the parent */

/* Origin of the perspective vanishing point */
perspective-origin: 50% 50%; /* Default: center */

/* Makes children maintain their 3D positions */
transform-style: preserve-3d;

/* The transforms on the child element */
transform: rotateX(20deg) rotateY(15deg) translateZ(40px);

/* Controls whether the back face shows when rotated > 90deg */
backface-visibility: hidden;  /* Use on front/back faces of flipping cards */
```

### Perspective Values — Character Guide

Perspective is the simulated distance from the viewer to the Z=0 plane:

| Perspective Value | Visual Effect | Use Context |
|------------------|---------------|-------------|
| 100–200px | Very dramatic — extreme foreshortening | Intentional perspective art, not UI |
| 300–500px | Pronounced — visible distortion | Expressive card flips, hero sequences |
| 600–900px | Moderate — subtle but noticeable | Card hover effects, interactive 3D |
| 1000–1500px | Subtle — near-flat with slight depth | Parallax layers, depth cues |
| 2000px+ | Nearly invisible — barely different from flat | Gentle depth suggestion only |

**Default for most UI work**: 800–1000px. This provides depth suggestion without
distortion that reads as a "3D effect."

### Understanding rotateX vs rotateY vs rotateZ

```
rotateX: tips top/bottom away from or toward the viewer (forward/back lean)
rotateY: spins left/right around the vertical axis (the natural card flip)
rotateZ: rotates in the plane of the screen (2D rotation)
```

Card flips typically use `rotateY`. A "page flip" effect uses `rotateY`. A
"spin to reveal" uses `rotateY`. Use `rotateX` for "folding" effects or
fold-in transitions.

### translateZ vs scale

Both can simulate depth, but they behave differently:

- **translateZ**: Moves the element along the Z-axis; with perspective set,
  the element appears larger (Z positive = toward viewer) or smaller (Z negative
  = away from viewer). The size change is perspective-accurate.
- **scale**: Simply scales the element in screen space. No perspective math.

For genuine 3D effects, `translateZ` in a perspective context is more physically
accurate. For UI elevation metaphors (like a card lift), `scale` + `box-shadow`
change is simpler, more performant, and visually equivalent.

---

## Card Flip Patterns

The card flip is the most common explicit 3D effect in UI — a common pattern for
reveal interactions, onboarding cards, two-sided information panels.

### Basic Card Flip

```html
<div class="card-scene">
  <div class="card">
    <div class="card-face card-front">Front content</div>
    <div class="card-face card-back">Back content</div>
  </div>
</div>
```

```css
.card-scene {
  perspective: 800px;
  width: 300px;
  height: 200px;
}

.card {
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
  transition: transform 500ms cubic-bezier(0.4, 0, 0.2, 1);
}

.card.flipped {
  transform: rotateY(180deg);
}

.card-face {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden; /* Safari */
}

.card-back {
  transform: rotateY(180deg);
}
```

### Flip Axis Decisions

| Axis | Effect | Use When |
|------|--------|---------|
| `rotateY(180deg)` | Horizontal flip (book-page spin) | Left/right reveal; most common |
| `rotateX(180deg)` | Vertical flip (top-to-bottom) | Up/down reveal; calendar flip |
| Diagonal | Off-axis rotation | Expressive; use sparingly |

### Easing for Physical Plausibility

- Pure ease-in-out produces a mechanical flip
- Spring easing (slight decelerate at 90° pause, accelerate through to 180°)
  produces a more physical card-turning feel
- A subtle pause at 90° (where the card is edge-on) mimics real physics

### Accessibility

Card flip must have a `prefers-reduced-motion` alternative:
```css
@media (prefers-reduced-motion: reduce) {
  .card { transition: none; }
  .card.flipped .card-front { opacity: 0; }
  .card.flipped .card-back { opacity: 1; }
}
```

---

## Parallax

Parallax creates depth by moving foreground layers faster than background layers.
It's the most commonly misused depth effect — often applied for aesthetics without
spatial purpose, and frequently triggering vestibular symptoms.

### The Physics

In real life, nearby objects appear to move faster than distant objects relative
to the viewer's motion. Parallax recreates this at different movement rates:

```css
.foreground { transform: translateY(calc(var(--scroll-y) * -0.8)); }  /* fast */
.midground  { transform: translateY(calc(var(--scroll-y) * -0.4)); }  /* medium */
.background { transform: translateY(calc(var(--scroll-y) * -0.1)); }  /* slow */
```

### When It's Appropriate

Parallax is appropriate for:
- Marketing / landing pages where the depth effect is itself the experience
- Hero sections and splash screens
- Onboarding flows where depth adds to the narrative

Parallax is **not appropriate** for:
- Data tables, dashboards, or any workflow screen
- Navigation elements
- Any context where the user is in task-execution mode

### CSS Parallax (No JavaScript)

A performant CSS-only parallax technique uses `perspective` on the scroll container:

```css
.scroll-container {
  perspective: 1px;
  overflow-y: scroll;
  height: 100vh;
}

.parallax-layer {
  transform-origin: center center 0;
}

.layer-back {
  transform: translateZ(-2px) scale(3);   /* appears further; scaled to fill */
}

.layer-front {
  transform: translateZ(0);              /* baseline */
}
```

This approach is compositor-only and doesn't require JavaScript. Limitation: the
`scale()` compensation calculation must be precise.

### Reduced-Motion Alternative

All parallax must have a static alternative:
```css
@media (prefers-reduced-motion: reduce) {
  .parallax-layer {
    transform: none !important;
  }
}
```

Under reduced-motion: layers render at their natural position, stacked normally.
The depth is implied by z-index and visual style rather than motion.

---

## Depth Layers for Visual Hierarchy

Even without explicit 3D transforms, depth layers can communicate hierarchy through
visual treatment (not motion):

| Layer | Motion Speed (parallax) | Visual Treatment |
|-------|------------------------|------------------|
| Foreground | 100% (fastest) | Full detail, highest contrast, sharp |
| Midground | 50–70% | Primary content, standard contrast |
| Background | 10–30% | Supporting, lower contrast, slight blur |

For motion purposes: background elements should move more slowly and with less
animation weight than foreground elements. This spatial convention is a generalization
of parallax that applies even in non-parallax contexts.

---

## 3D in Flat Design

The "Material Design" and "Neumorphism" traditions both use implied depth without
explicit 3D rendering. The motion equivalent:

### Card Hover Lift
The canonical "flat 3D" interaction: a card rises slightly on hover.
```css
.card {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
  transition: transform 200ms ease-out, box-shadow 200ms ease-out;
}
.card:hover {
  transform: translateY(-4px);  /* lifts toward viewer */
  box-shadow: 0 8px 24px rgba(0,0,0,0.16);  /* shadow implies height */
}
```

The shadow change and the vertical translation together suggest the card moved
upward in Z-space — flat UI, spatial implication.

### Drawer Sliding from Edge
The drawer "was behind the edge" — it slides in from the edge it belongs to.
This is 3D spatial reasoning applied to a flat 2D slide animation. The metaphor
(something hidden behind the edge) is a 3D spatial concept expressed in 2D motion.

### Modal Rising
The modal "rises from the surface" — it was below the current view (implied Z=below)
and comes toward the viewer (scale-in from 95–97%). The scrim darkens the surface
below. Together they produce a 3D spatial metaphor in a flat 2D effect.

---

## WebGL and Three.js for Expressive 3D

When CSS 3D isn't enough — full 3D scenes, particle systems, complex geometry,
immersive backgrounds.

### When to Cross the Threshold

CSS 3D covers most interface needs. Move to WebGL/Three.js when:
- You need genuine 3D geometry (spheres, complex meshes, 3D text)
- You need particle systems (many thousands of independent elements)
- You need physically-based lighting and materials
- The effect requires GPU computation beyond compositing

### Performance Coordination

WebGL runs on a separate GPU context from the DOM compositor. Combining WebGL
with DOM UI requires careful frame budget management:

- Canvas renders happen separately from DOM paint
- Using a fullscreen WebGL canvas behind a DOM UI is common; the canvas receives
  no compositor-layer benefits from DOM properties
- Profile both the WebGL frame time AND the DOM frame time — they can both be
  expensive simultaneously
- Cross-reference `motion-performance` for frame budget and DevTools profiling

### Three.js Integration Pattern

For background/hero 3D effects behind a DOM UI:

```javascript
// The canvas sits behind the UI at z-index: -1
// DOM UI sits above at z-index: 0+
// WebGL and DOM are independent render targets

const canvas = document.getElementById('bg-canvas');
const renderer = new THREE.WebGLRenderer({ canvas, alpha: true });
// alpha: true allows transparent canvas background
```

---

## Failure Modes

- **Perspective on the wrong element**: Setting `perspective` on the animated
  element rather than its parent produces incorrect results — the perspective
  must be set on the container
- **Missing `transform-style: preserve-3d`**: Child 3D transforms flatten without
  this on the parent
- **Dramatic perspective values in enterprise UI**: 200–400px perspective in a
  workflow interface reads as a "3D effect" rather than depth suggestion; use
  900–1200px for subtle elevation metaphors
- **Parallax without reduced-motion alternative**: A high-risk vestibular trigger
  with no accommodation
- **Parallax on workflow screens**: Decorative depth on dense data UIs causes
  spatial disorientation and has no information value
- **3D effects that hurt GPU performance**: Preserve-3d on large numbers of elements
  creates many compositor layers; expensive on mid-range hardware. Cross-reference
  `motion-performance`.
- **Inconsistent spatial model**: Some modals rise from below, some fade in, some
  slide — breaks the spatial model the user was building

---

## Cross-Links

- `motion-performance` — GPU cost of 3D transforms; compositor layer proliferation
- `motion-principles` — Solid Drawing principle (principle 11): 3D reasoning as
  the theoretical foundation
- `motion-accessibility` — vestibular risk of parallax; reduced-motion alternatives
  for all 3D effects
- `motion-transitions` — applying the spatial model to transition direction decisions
- `lead-graphic-designer` / `gd-image-composition` — compositional depth and
  layering principles as the graphic design foundation of 3D spatial reasoning

---

## References

- MDN — CSS Transforms: `perspective`, `transform-style`, `backface-visibility`
- David DeSandro, "Intro to CSS 3D Transforms" (desandro.com)
- Three.js documentation (threejs.org)
- Google Web Fundamentals — Compositor-only properties
- W3C CSS Transforms Module Level 2 specification

## Related
- hub → [[lead-motion-designer]]
