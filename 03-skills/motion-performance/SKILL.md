---
name: motion-performance
description: >
  Animation performance engineering — 60fps, compositor-layer promotion, will-change,
  GPU acceleration, frame budget, rendering pipeline, FLIP technique, DevTools
  profiling. Use this skill whenever the conversation touches: animation performance,
  jank, dropped frames, 60fps, compositor layer, will-change, GPU memory, rendering
  pipeline (style/layout/paint/composite), animating width/height vs transform,
  FLIP animation technique, requestAnimationFrame, layout thrashing, forced
  synchronous layout, DevTools Performance panel, Layer panel, paint flashing,
  frame budget, 120fps/ProMotion, Web Animations API vs CSS vs GSAP performance,
  or any question about why an animation is slow and how to fix it.
aliases: [motion-performance]
tier: spoke
domain: design
hub: lead-motion-designer
prerequisites: [lead-motion-designer]
spec_version: "2.0"
---

# Motion Performance

Specialist lens for animation performance engineering — the rendering pipeline,
compositor-layer optimization, and tooling to diagnose and fix animation jank.
Part of the lead-motion-designer skill network.

---

## Domain Boundary

This skill owns **why animation is fast or slow and how to make it faster**.

- **Which animation to design** → `motion-transitions` or `motion-choreography`
- **Why the motion feels wrong (not slow)** → `motion-principles`
- **Library-specific performance characteristics** → `motion-tooling`
- **3D transform GPU cost** → this skill + `motion-3d-spatial`
- **Full web performance engineering beyond animation** → `fe-performance`

---

## The Rendering Pipeline

The browser renders every frame by running some or all of these stages:

```
Styles → Layout → Paint → Composite
```

Each stage has a cost. Animations that trigger only the last stage (Composite) are
the cheapest. Animations that trigger Layout (the most expensive stage) on every
frame are the most likely to cause jank.

### Stage Costs

| Stage | What it does | Relative Cost | Triggers |
|-------|-------------|---------------|---------|
| **Style** | Recalculates CSS property values | Low | Any CSS change |
| **Layout** | Calculates geometry (size, position) | High | Box model changes |
| **Paint** | Rasterizes pixels into layers | Medium | Visual appearance changes |
| **Composite** | Assembles painted layers | Very Low | Transform, opacity |

**The key insight**: If you can confine an animation to the Composite stage,
the browser never recalculates layout or repaints — it just repositions or
resamples already-rendered pixels. This is what enables 60fps.

---

## Compositor-Only Properties

Only two CSS properties trigger compositing without paint or layout:

1. **`transform`** — translate, scale, rotate, skew, translateZ, matrix
2. **`opacity`** — 0 to 1 transparency

**Everything else triggers paint or layout.** This is the single most important
rule in animation performance.

### Properties That Trigger Layout (Never Animate)

These properties change the element's box model, forcing the browser to recalculate
geometry for the element and potentially its siblings, children, and parent:

```css
/* Never animate these */
width, height
top, right, bottom, left    (with position: absolute/fixed)
margin, padding
border-width
font-size
line-height
```

### Properties That Trigger Paint (Avoid Animating)

These change pixel appearance but not geometry. Paint is cheaper than layout
but more expensive than composite:

```css
/* Avoid animating these */
background-color            (exceptions: color transitions that can be optimized)
border-color
color
box-shadow
border-radius               (triggers paint; can be expensive in some contexts)
```

**Exception for background-color**: Modern browsers can sometimes handle simple
color transitions efficiently. Short (< 200ms) color transitions as feedback
(button press, state change) are generally acceptable. Continuous animating color
is not.

### The Translation Rule

Moving an element from point A to point B:

```css
/* WRONG — triggers layout on every frame */
.element {
  transition: left 300ms;
}
.element.moved {
  left: 200px;
}

/* CORRECT — compositor only */
.element {
  transition: transform 300ms ease-out;
}
.element.moved {
  transform: translateX(200px);
}
```

The visual result is identical. The performance difference is significant.

---

## will-change

`will-change` hints to the browser that an element will be animated, allowing
it to promote the element to a compositor layer before the animation begins.

Without `will-change`, when an animation starts, the browser must perform a
"layer promotion" operation — this can cause a visible hitch at animation start.
`will-change` eliminates this hitch by pre-promoting.

```css
/* Promote before hover triggers animation */
.card {
  will-change: transform;  /* Browser creates a new compositor layer */
}

/* Promote for all elements in a list about to animate */
.list-item {
  will-change: transform, opacity;
}
```

### The Cost

Every compositor layer requires **GPU memory**. GPU memory is limited, and
promoting too many elements is worse for overall performance than the layer
promotion hitch it was trying to avoid.

**Rules for will-change**:
- Apply it to elements that will be animated imminently — not as a global rule
- Remove it after the animation completes if the animation is not frequent
- If using JavaScript animation, add `will-change` before starting the animation
  and remove it in the `onComplete` callback
- Do not apply to every element on the page — this is a common cargo-cult mistake
  that degrades performance

```javascript
// Good pattern: add before, remove after
element.style.willChange = 'transform, opacity';
element.addEventListener('transitionend', () => {
  element.style.willChange = 'auto';
}, { once: true });
```

---

## Frame Budget

### 60fps Target

60fps = 1 frame every 16.67ms.

The browser requires approximately 2–4ms for its own rendering work. Your
animation code budget per frame: **~10–12ms**.

If a frame takes longer than 16.67ms, the browser drops it. The skipped frame
is visible as jank — the animation stutters rather than flowing.

### 120fps / ProMotion

High refresh rate displays (Apple ProMotion, many Android flagships) run at
120fps = 1 frame every 8.33ms.

Modern CSS animations and Web Animations API automatically adapt to the display
refresh rate. JavaScript-driven animations using `requestAnimationFrame` also
adapt since rAF fires at the display refresh rate.

However, your frame budget is now **~4–6ms** at 120fps — half of 60fps. Code
that barely makes 60fps will jank at 120fps.

### Frame Budget Visualization

```
16.67ms frame at 60fps:
├── Browser overhead: ~4ms
├── Your JS: ~6ms
├── Browser rendering: ~4ms
└── Buffer: ~2ms

8.33ms frame at 120fps:
├── Browser overhead: ~3ms
├── Your JS: ~3ms
└── Browser rendering: ~2ms ← very tight
```

---

## FLIP Technique

FLIP (First, Last, Invert, Play) is a technique for animating between two layout
states without triggering layout on every frame.

### The Problem It Solves

Some visual transitions require moving an element from one DOM position to
another — different parent, different part of the layout, completely different
dimensions. You can't animate `top`/`left` (layout triggering) and you can't
animate `transform` because you don't know the offset at animation start.

### The Four Steps

1. **First**: Record the element's starting position/size
   ```javascript
   const first = element.getBoundingClientRect();
   ```

2. **Last**: Move the element to its final position (instantly, no animation)
   ```javascript
   element.classList.add('final-state');
   const last = element.getBoundingClientRect();
   ```

3. **Invert**: Apply a transform that makes the element look like it's still in
   the starting position (even though it's now in the final position in the DOM)
   ```javascript
   const deltaX = first.left - last.left;
   const deltaY = first.top - last.top;
   const scaleX = first.width / last.width;
   const scaleY = first.height / last.height;
   element.style.transform = `translate(${deltaX}px, ${deltaY}px) scale(${scaleX}, ${scaleY})`;
   ```

4. **Play**: Animate the transform back to identity (no transform = the actual
   final position), which is compositor-only
   ```javascript
   requestAnimationFrame(() => {
     element.style.transition = 'transform 300ms ease-out';
     element.style.transform = 'none';
   });
   ```

### Why It Works

The browser only does layout once (step 2). The animation (step 4) is a pure
transform animation — compositor only, no layout, no paint. The user sees smooth
motion from the visual start to visual end position.

### Libraries That Implement FLIP

- **Framer Motion**: `layout` prop — the most ergonomic FLIP implementation
- **AutoAnimate**: Drop-in, zero-config FLIP for list reordering
- **GSAP Flip plugin**: `gsap.utils.flip()` with timeline integration
- **View Transitions API**: Native browser FLIP for page-level transitions

---

## Layout Thrashing

Layout thrashing (forced synchronous layout) is one of the most common causes of
animation jank in JavaScript-driven animations.

### What It Is

Reading layout properties (`offsetWidth`, `offsetHeight`, `getBoundingClientRect`,
`clientTop`, `scrollTop`, etc.) after writing to the DOM forces the browser to
immediately complete a layout calculation — synchronously, in your JavaScript frame.

If you do this repeatedly in a loop, you force many layouts per frame:

```javascript
// WRONG — layout thrashing
elements.forEach(el => {
  el.style.width = el.offsetWidth + 10 + 'px';  // read → write → read → write...
});
```

### The Fix: Batch Reads and Writes

```javascript
// CORRECT — batch all reads, then all writes
const widths = elements.map(el => el.offsetWidth);      // all reads
elements.forEach((el, i) => {
  el.style.width = widths[i] + 10 + 'px';               // all writes
});
```

Or use `requestAnimationFrame` to separate the read and write phases:

```javascript
// Reads happen at the start of a frame, writes at the start of the next
function update() {
  const width = element.offsetWidth;                     // read
  requestAnimationFrame(() => {
    element.style.transform = `translateX(${width}px)`;  // write (next frame)
  });
}
```

### FastDOM Library

For complex interactions with many read/write cycles, `fastdom` batches reads and
writes automatically:

```javascript
fastdom.measure(() => {
  const width = element.offsetWidth;
  fastdom.mutate(() => {
    element.style.transform = `translateX(${width}px)`;
  });
});
```

---

## requestAnimationFrame vs CSS vs Web Animations API

| Approach | Performance | Control | Sequencing | Use When |
|----------|------------|---------|------------|---------|
| **CSS Transitions** | Excellent (compositor) | Low | No JS control | Simple state-driven transitions; hover, focus, class toggles |
| **CSS Keyframes** | Excellent (compositor) | Low | None | Looping animations; declarative multi-step |
| **Web Animations API (WAAPI)** | Excellent (compositor) | High | Timeline | Programmatic control with CSS-level performance; sequences without a library |
| **requestAnimationFrame** | Good (requires care) | Maximum | Manual | Physics simulations, complex math-driven animation, video-sync |
| **GSAP** | Excellent (optimized rAF) | Maximum | Timeline | Complex choreography, sequences, ScrollTrigger |
| **Framer Motion** | Good–Excellent | High | Variants | React apps with layout animations and gestures |

### WAAPI — The Underused Native Option

The Web Animations API provides programmatic animation with compositor-level
performance, no library required:

```javascript
element.animate(
  [
    { transform: 'translateX(0)', opacity: 0 },
    { transform: 'translateX(0)', opacity: 1 }
  ],
  {
    duration: 300,
    easing: 'cubic-bezier(0, 0, 0.2, 1)',
    fill: 'forwards'
  }
);
```

- Returns an Animation object with `play()`, `pause()`, `reverse()`, `finish()`
- Timeline-based with `KeyframeEffect` and `AnimationTimeline`
- Supported in all modern browsers
- Compositor-optimized for `transform` and `opacity`

---

## DevTools Performance Profiling

### Chrome DevTools Workflow

1. **Open DevTools → Performance tab**
2. **Start recording**, perform the animation
3. **Stop recording**, analyze the flame chart

**What to look for**:
- **Long Tasks** (red bars > 50ms): JavaScript executing for too long per frame
- **Layout events** (purple bars marked "Layout"): How often and how long layout recalculation takes
- **Paint events** (green): Rasterization cost
- **Frames graph**: Dropped frames show as red/yellow in the frame bar

### Layer Panel

DevTools → More Tools → Layers

The Layer panel shows all active compositor layers. This is the most direct way
to audit `will-change` and 3D transform layer creation:

- Each layer has a size in bytes — GPU memory cost is visible
- Excessive layers: scroll down looking for elements that shouldn't be layers
- "Stacking context" reasons: the panel explains why each layer was created

### Rendering Panel

DevTools → More Tools → Rendering

Useful checkboxes:
- **Paint flashing**: Highlights areas that are being repainted (green flashes).
  Should be minimal during animation — large flashes indicate paint-triggering properties.
- **FPS meter**: Overlay showing current frame rate.
- **Layer borders**: Shows compositor layer boundaries directly on the page.
- **Scrolling performance issues**: Highlights elements with scroll-linked listeners
  on the main thread.

---

## GPU Memory Cost

Every compositor layer consumes GPU memory. The amount depends on:
- Element dimensions × pixel density (a 400×400 element at 2× DPR = 400×400×4 = ~640KB)
- Number of layers
- Tiling strategy

**Practical thresholds**:
- A few dozen animated layers: typically fine on modern hardware
- Hundreds of promoted layers: degrades overall performance
- `will-change: transform` on every list item in a 1000-item list: likely causes
  GPU memory pressure on mid-range devices

**The rule**: Promote only what is actively animating, and only for the duration
of the animation.

---

## Failure Modes

- **Animating layout properties**: The most common cause of 60fps failure; always
  replace with transform equivalents
- **will-change on everything**: A cargo-cult pattern that creates hundreds of
  compositor layers and exhausts GPU memory
- **Layout thrashing in animation loops**: Reading layout properties inside
  `requestAnimationFrame` callbacks that also write to the DOM
- **Not testing on mid-range hardware**: Animation that runs at 60fps on a
  MacBook Pro may drop to 30fps on a mid-range Android phone; test on both
- **Ignoring the Layer panel**: Assuming an animation is "fine" without confirming
  which layers are being created
- **Framer Motion layout animations on large lists**: The `layout` prop triggers
  FLIP calculations for the entire sibling set — on very large lists, this can be
  expensive; consider virtualizing

---

## Cross-Links

- `motion-3d-spatial` — GPU cost of CSS 3D transforms; perspective and preserve-3d
  compositor layer creation
- `motion-tooling` — library-specific performance characteristics
- `motion-transitions` — applying compositor-only properties to specific transition
  patterns (accordion height animation, etc.)
- `fe-performance` — full web performance engineering beyond animation

---

## References

- Paul Lewis & Paul Irish, "High Performance Animations" (HTML5 Rocks, archived)
- Google Web Fundamentals — Rendering Performance
- MDN — Web Animations API
- CSS Triggers (csstriggers.com) — lookup table for property rendering costs
- David Khourshid, "FLIP Your Animations" (css-tricks.com)
- Chrome DevTools — Performance Analysis Reference

## Related
- hub → [[lead-motion-designer]]
