---
name: motion-choreography
description: >
  Multi-element animation sequencing — stagger, overlapping action, timing
  relationships, narrative arc, entrance and exit choreography, and reduced-motion
  alternatives that preserve temporal structure. Use this skill whenever the
  conversation touches: stagger, stagger direction, sequencing multiple elements,
  timing relationships between elements, animation narrative arc, entrance
  sequence, exit sequence, list animation, hero animation, overlapping transitions,
  choreographed onboarding, complex animation sequences, or any question about
  how multiple elements animate in relation to each other.
aliases: [motion-choreography]
tier: spoke
domain: design
hub: lead-motion-designer
prerequisites: [lead-motion-designer]
spec_version: "2.0"
---

# Motion Choreography

Specialist lens for multi-element animation sequences — the timing relationships,
spatial logic, and narrative structure that make groups of elements move as a
coherent whole. Part of the lead-motion-designer skill network.

---

## Domain Boundary

This skill owns **timing relationships between multiple animated elements**.

- **How a single element should move** → `motion-transitions`
- **Why the easing feels wrong** → `motion-principles`
- **Implementation of sequences** → `motion-tooling` (GSAP timeline, Framer Motion variants)
- **Performance of complex sequences** → `motion-performance`
- **Reduced-motion for individual elements** → `motion-accessibility`

---

## Choreography vs. Individual Animation

When a single element animates, the design decisions are: what does it do,
how does it move (easing), and how long does it take.

When multiple elements animate, the timing relationships between them become
a parallel design problem of equal importance. A set of elements with perfect
individual motion but poor choreography will feel wrong — mechanical, random,
or incoherent.

Choreography asks: *In what order do elements move, by how much do they overlap,
which element leads, which follow, and what does the sequence communicate
about the relationship between the elements?*

---

## Core Concepts

### Stagger

Stagger is a delay between the start of successive elements in a group. It
creates the perception that the elements are connected — moving as a group
with internal momentum rather than all firing simultaneously.

**Stagger value**: The delay between each successive element's animation start.
- Too small (< 20ms): indistinguishable from simultaneous
- Good range (30–80ms): perceptible sequence without feeling slow
- Too large (> 120ms): elements feel unrelated; the user waits for each one

**The formula**: Total visual duration of a staggered group = (individual element duration) + (stagger × (n-1) elements)

```
Example: 8 items, 250ms duration, 50ms stagger
Total visual duration = 250 + (50 × 7) = 600ms
```

This is why stagger values must be small — they compound.

### Stagger Direction

The direction of stagger communicates spatial relationships:

| Direction | Reads as | Use When |
|-----------|---------|---------|
| Top-to-bottom | "Falling into place" or "loading from top" | Vertical lists, feed content, table rows |
| Bottom-to-top | "Rising up" | Less common; upward reveal metaphor |
| Left-to-right | "Reading order" entrance | Horizontal content, cards in a row |
| Right-to-left | Exit direction for LTR content | Dismissing items in reading order |
| From-center | "Expanding outward" | Centered layouts, radial menus |
| Random | "Organic" arrival | Particle-like effects, very expressive contexts only |

Choose direction based on the spatial logic of the content, not aesthetic preference.
A vertical list staggering left-to-right reads as wrong because the elements'
physical relationship is vertical.

### Overlapping Action

Overlapping action is the choreographic application of Disney's principle 5:
elements begin their animation before previous elements have completed theirs.

Without overlap: A → (pause) → B → (pause) → C — mechanical, slow
With overlap: A → B starts while A is midway → C starts while B is midway

```
Time:  0    200   400   600ms
A:     [====]
B:           [====]
C:                 [====]
vs.
A:     [=====]
B:        [=====]
C:           [=====]
```

Overlap creates fluidity — the group feels like it moves with forward momentum
rather than step-by-step. Stagger with overlap is more natural than stagger
without overlap (which can feel like a ticking clock).

**Overlap amount**: Typically 20–40% of element duration.
- 250ms duration, 40% overlap = 100ms between starts
- The stagger delay is the gap between starts, so stagger = 100ms in this example
  (which is on the high end — the elements should have enough visual distinctness
  that users perceive the sequence)

---

## Duration Scaling with Complexity

The more elements in a sequence, the more important it is to keep individual
element durations short:

| Sequence Type | Element Duration | Stagger | Max Total |
|--------------|-----------------|---------|---------|
| List entrance (3–5 items) | 200ms | 50ms | ~400ms |
| List entrance (6–12 items) | 150ms | 40ms | ~600ms |
| Dashboard section load | 200ms | 60ms | ~600ms |
| Hero/onboarding sequence | 300ms | 80ms | ~800ms |
| Complex marketing intro | 400ms | 80–100ms | 1000ms |

**Rule**: If the total visual duration of a choreographed sequence exceeds
1 second for a UI context, it's too slow. Shorten individual durations before
reducing stagger.

---

## Narrative Arc

A well-designed animation sequence tells a story with structure:
- **Setup**: What exists before the action
- **Action**: What changes
- **Resolution**: The new stable state

Complex entrance animations benefit from thinking in narrative terms:

### Example: Dashboard Section Loading

```
0ms:    Background/skeleton present (already there)
50ms:   Section header slides in — establishes the container
150ms:  First row of data fades up — "content is here"
200ms:  Second row follows — continues the rhythm
250ms:  Third row follows
...
500ms:  All rows visible — resolution, stable state
600ms:  Status indicators pulse once — "everything loaded"
```

The narrative: the shell arrives, the content fills in, the system signals completion.
Each stage communicates something specific about what's happening.

### Establishing the Lead Element

In any choreographed sequence, one element should move first and most prominently.
This is the **lead element** — it sets the rhythm and directs attention to the
most important part of the content.

**Rules for lead element selection**:
1. The most important piece of information for the user should lead
2. The largest or highest-hierarchy element typically leads
3. Headers lead body content; titles lead metadata; primary actions lead secondary

Everything else follows the lead element. If everything moves simultaneously,
there is no lead — the eye has nowhere to go.

---

## Entrance Choreography Patterns

### Vertical List Entrance

The most common pattern in enterprise UI.

```javascript
// GSAP
gsap.from('.list-item', {
  y: 16,
  opacity: 0,
  duration: 0.2,
  ease: 'power2.out',
  stagger: { amount: 0.3, from: 'start' }  // total stagger budget = 300ms
});

// Framer Motion
const variants = {
  hidden: { opacity: 0, y: 12 },
  visible: (i) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.04, duration: 0.2, ease: [0, 0, 0.2, 1] }
  })
};
```

**Distance**: The y-offset (or x-offset for horizontal) should be small — 8–20px.
Large distances (> 40px) look like the element is traveling from far away rather
than snapping into place. The motion should suggest "settling," not "arriving."

### Card Grid Entrance

```javascript
// Stagger from top-left, reading order
gsap.from('.card', {
  opacity: 0,
  y: 16,
  duration: 0.2,
  stagger: {
    amount: 0.4,
    grid: [rows, columns],  // stagger across a grid
    from: 'start'
  }
});
```

Grid stagger allows elements to cascade in reading order across a 2D layout
rather than purely top-to-bottom.

### Hero / Page Header Sequence

A page header entrance with multiple elements:

```javascript
const tl = gsap.timeline();

tl
  .from('.breadcrumb', { y: -8, opacity: 0, duration: 0.2 })
  .from('.page-title', { y: 12, opacity: 0, duration: 0.25 }, '-=0.05')
  .from('.page-subtitle', { y: 8, opacity: 0, duration: 0.2 }, '-=0.1')
  .from('.action-bar', { y: 8, opacity: 0, duration: 0.2 }, '-=0.1');

// Total: ~600ms visual duration, 4 elements
```

---

## Exit Choreography

Exit choreography is as important as entrance — but often neglected.
The spatial logic of an exit should be the reverse of the entrance spatial logic.

### Principles

1. **Exit reverses entrance direction**: If the element entered from the top,
   it exits to the top (or stays in place and fades — fade is always safe as exit)
2. **Lead element exits last**: The most important element entered first and exits
   last — it anchors the scene at both ends
3. **Exit is faster than entrance**: Exits use ease-in (accelerating away) at
   shorter durations — the user made a decision; don't hold them
4. **Exit stagger reverses**: Bottom-to-top exit for top-to-bottom entrance (last
   in, first out)

### Exit Duration Rule

Exit durations should be 60–75% of entrance durations:
- 250ms entrance → 175ms exit
- 200ms entrance → 125–150ms exit

### Example: Drawer Exit

```javascript
// List items exit bottom-to-top (reverse of top-to-bottom entrance)
gsap.to('.list-item', {
  y: -8,
  opacity: 0,
  duration: 0.15,
  ease: 'power2.in',
  stagger: { amount: 0.2, from: 'end' }  // from: 'end' reverses direction
});
```

---

## Reduced-Motion Choreography

When `prefers-reduced-motion` is active, the goal is to preserve the temporal
structure (the rhythm, the sequence, the narrative) while replacing movement
with opacity changes.

**The key insight**: Stagger communicates relationships even without movement.
Elements that fade in with a stagger pattern still feel like a connected group —
the timing relationship survives without the spatial motion.

```javascript
const prefersReducedMotion =
  window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// GSAP — conditional animation properties
gsap.from('.list-item', {
  opacity: 0,
  y: prefersReducedMotion ? 0 : 16,  // no y movement; keep stagger + fade
  duration: prefersReducedMotion ? 0.15 : 0.2,  // slightly shorter under reduce
  stagger: 0.04  // KEEP the stagger — it still communicates
});

// Framer Motion — conditional variants
const variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 }
  // no y, no scale — movement removed, timing preserved
};
```

**What to keep under reduced-motion**:
- Stagger timing (the sequence)
- Opacity transitions (the fade)
- Duration ratios (the rhythm)

**What to remove**:
- All translate (x, y, z movement)
- Scale
- Rotation
- Any spatial motion

---

## Offset Timing and Leading Elements

### The Offset Pattern

Not all elements start at t=0, even in a simple sequence. Defining which element
leads establishes hierarchy and directs attention.

```
Good: Header enters first at t=0, body enters at t=80ms
Effect: User reads header while body arrives — natural reading flow

Bad: Header and body enter simultaneously at t=0
Effect: Both compete for attention at the same moment
```

### Starting Time as a Design Decision

In a timeline, the starting time of each element communicates its relationship
to other elements:
- **Starting before**: This element "leads" the subsequent elements
- **Starting after**: This element "follows" — it's secondary
- **Starting simultaneously**: These elements are peers of equal importance

Use starting time to encode the information hierarchy of the content, not just
to create visual interest.

---

## Common Anti-Patterns

### The Scatter Pattern
Every element on the page has its own entrance animation with different timings
and directions. Result: visual chaos with no focal point.
Fix: Establish a lead element and a consistent stagger direction; group related
elements into single motion units.

### The Procession
Elements enter one at a time with a full pause between each. No overlapping action.
Result: slow, mechanical, feels like a slideshow.
Fix: Add overlap so the next element starts before the previous one finishes.
Stagger ≠ sequential; stagger = delayed parallel.

### The Simultaneous Slam
Every element on the page enters at exactly t=0. No stagger.
Result: a visual jump that's more like a flash than a transition.
Fix: Even 30–40ms stagger between groups (not individual elements) creates
the sense of a connected entrance without feeling slow.

### The Undesigned Exit
Dismiss button → elements snap off (no exit animation).
Fix: Exits need as much design attention as entrances. Even a 100ms fade is
better than an instant DOM removal.

### Duration Inflation for "Luxury"
"Premium" → 800ms entrance for a simple page header. Each interaction taxes
the user's patience. The perception of quality comes from easing precision and
choreographic coherence, not from slow motion.

---

## Choreography as Visual Communication

At the highest level, choreography is not about making things look nice —
it's about communicating information about relationships, hierarchy, and process
through the structure of motion in time.

A loading sequence that starts with the skeleton present → then header appears →
then data fills in communicates: the system knows the structure before it has the
data. This is a true information message delivered through motion.

A list that staggers top-to-bottom on first load communicates: these items are
ordered, they have a sequence, they were loaded in this order. The stagger
reinforces the list's own logical structure.

Good choreography makes the interface's behavior readable. Users don't consciously
notice it — but they understand the interface better because of it.

---

## Cross-Links

- `motion-principles` — follow-through, overlapping action, timing, and staging
  as the theoretical foundations of choreography
- `motion-transitions` — individual element transitions that choreography sequences
- `motion-tooling` — GSAP timeline implementation; Framer Motion variants for
  React component trees
- `motion-accessibility` — reduced-motion alternatives: preserving stagger and
  timing while removing movement
- `motion-performance` — performance of complex sequences; stagger in large lists

---

## References

- GSAP Timeline documentation (greensock.com/docs/v3/GSAP/Timeline)
- Framer Motion Variants documentation (framer.com/motion/variants)
- Frank Thomas & Ollie Johnston, *The Illusion of Life* — Overlapping Action chapter
- Val Head, *Designing Interface Animation* — sequencing and rhythm
- Google Material Motion — Choreography guidelines

## Related
- hub → [[lead-motion-designer]]
