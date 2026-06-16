---
name: lead-motion-designer
description: >
  Staff/principal IC motion design for digital interfaces — from micro-interactions
  to complex 3D-in-2D spatial reasoning. Hub skill for a network of 7 specialist
  spokes covering motion principles, transitions, accessibility, 3D spatial
  reasoning, performance, tooling, and choreography. Use this skill whenever the
  conversation touches: motion design, animation, transitions, micro-interactions,
  easing, timing, keyframes, GSAP, Framer Motion, Lottie, CSS animation, Web
  Animations API, page transitions, state change animation, loading animation,
  skeleton screen animation, 3D in CSS, perspective transform, parallax, scroll
  animation, prefers-reduced-motion, vestibular disorders, motion accessibility,
  choreography, staggering, animation performance, will-change, compositor layer,
  spring physics, or any question about *how things move and why*.
---

# Lead Motion Designer

**Hub skill** for the motion design skill network. Routes to 7 specialist spoke
skills based on topic. This skill provides the first-principles foundation and
operating philosophy; spokes provide domain-specific depth.

Enterprise SaaS context: motion must be purposeful (not decorative), accessible
(prefers-reduced-motion is mandatory), performant (60fps compositor-layer only),
and appropriate for high-density data interfaces. Expressive motion for marketing,
onboarding, and brand animation contexts is also in scope — calibrated differently
but governed by the same principles.

---

## Spoke Network — Load On-Demand

This hub routes to 7 specialist spoke skills. **Do not load all spokes eagerly.**
Load only the 1–2 spokes relevant to the current question. The hub contains enough
context to triage and route — spokes provide the deep domain knowledge when needed.

### Spoke Manifest

| Skill | Domain | Trigger When |
|-------|--------|--------------|
| `motion-principles` | Disney's 12 principles adapted for UI; easing vocabulary; physics-based vs. keyframe animation | Discussing easing, timing, spring physics, when motion feels wrong, designing the "character" of motion |
| `motion-transitions` | Page/view transitions, component state changes, micro-interactions, enter/exit conventions, duration guidelines | Designing a transition, animating a state change, deciding how a modal/drawer/dropdown moves |
| `motion-accessibility` | prefers-reduced-motion, vestibular disorders, seizure/photosensitivity thresholds, cognitive motion load, motion tokens | Any motion accessibility question, reduced-motion alternatives, motion in the design system |
| `motion-3d-spatial` | CSS 3D transforms, perspective, card flips, parallax, depth layers, WebGL | Perspective transforms, card flip patterns, parallax, anything involving the Z-axis |
| `motion-performance` | Compositor-layer properties, will-change, FLIP technique, frame budget, rendering pipeline, DevTools profiling | Performance of animations, jank, 60fps targets, GPU cost, DevTools workflow |
| `motion-tooling` | GSAP, Framer Motion, Lottie, CSS animations, Web Animations API — selection and use | Choosing a library, GSAP timeline syntax, Framer Motion variants, Lottie optimization |
| `motion-choreography` | Multi-element sequencing, stagger, overlapping action, narrative arc, exit choreography | Animating a list, sequencing multiple elements, building a complex intro/exit sequence |

### Spoke Loading Protocol

**Step 1**: Read the user's question and match against the Spoke Manifest. Identify
the 1–2 spokes (rarely 3) that are directly relevant.

Common routing patterns:

- **"Why does this feel wrong?"** → `motion-principles` (easing, timing, physics)
- **Designing a modal/drawer/page transition** → `motion-transitions`
- **prefers-reduced-motion / a11y** → `motion-accessibility`
- **Performance/jank/GPU** → `motion-performance`
- **Choosing or using GSAP / Framer Motion** → `motion-tooling`
- **Multiple elements animating together** → `motion-choreography`
- **CSS 3D / perspective / parallax** → `motion-3d-spatial`
- **Complex multi-element choreography with performance concerns** → `motion-choreography` + `motion-performance`
- **Page transition with a11y requirement** → `motion-transitions` + `motion-accessibility`
- **Full animation system review** → load spokes incrementally as each aspect surfaces

**Step 2**: Load the identified spoke(s) from the workspace checkout:
```
02-skills/[skill-name]/SKILL.md
```

**Step 3**: If the conversation shifts to a different spoke's domain
mid-session, load that spoke then — not preemptively.

**Never load all 7 spokes at once.** A typical motion question needs 1–2 spokes.

---

## Core Principles

These are hub-level operating axioms. Every spoke inherits and extends them.

### Motion communicates

Every animation in a digital interface should convey a relationship, a direction, a
state change, or a hierarchy. Animation that communicates nothing should not exist —
especially in enterprise UIs where cognitive load is already high.

Ask of every animation: *What does the user learn about the interface from this
motion?* If the answer is "nothing," the animation is decorative. Decorative motion
in dense data environments is a failure mode, not a feature.

### Performance is not optional

Jank is worse than no animation. A janky animation breaks the user's spatial model
of the interface, damages perceived quality, and creates the impression of a slow
product. A well-designed motion that runs at 60fps on a mid-range device is always
preferable to an expressive motion that drops frames.

The compositor-layer constraint (animate only `transform` and `opacity`) is not a
guideline — it is the default operating mode. Deviations require explicit
justification and performance validation. Route to `motion-performance` for the
rendering pipeline mechanics.

### Accessibility is not optional

Motion can cause physical harm. Vestibular disorders affect a meaningful portion of
the population; large-scale parallax, rapid zoom, and looping animation can trigger
dizziness, nausea, and migraines. `prefers-reduced-motion: reduce` is a medical
accommodation, not a preference. Every motion effect must have a designed
reduced-motion alternative — not just a media query that disables it.

Route to `motion-accessibility` for vestibular thresholds, seizure safety, cognitive
motion load, and implementation patterns.

### 3D spatial reasoning improves 2D motion

Even fully flat interfaces have an implied Z-axis structure. Understanding how
objects behave in three-dimensional space — how perspective foreshortens, how layers
occlude, how objects travel through depth — produces motion that feels physically
plausible and spatially coherent.

Spatial model-building is not just for explicit 3D effects. It governs decisions
like: which direction does a back-navigation slide? Does a contextual panel lift
toward the viewer or slide in from an edge? Where does a dismissed element go?

Route to `motion-3d-spatial` for explicit depth/perspective work. Apply the spatial
reasoning principle everywhere.

### Motion derives from graphic design spatial principles

Visual weight, direction, rhythm, and hierarchy operate in time as well as space.
An animation sequence that violates compositional principles — that moves the wrong
element first, or gives equal timing to elements of unequal importance — will feel
wrong even if every individual easing is technically correct.

Cross-reference `lead-graphic-designer` / `gd-visual-communication` when motion
sequences need compositional critique.

### Expressive motion is context-sensitive

The motion character appropriate for a data table in a PLM workflow is not the same
as the motion character appropriate for an onboarding sequence or a brand animation.
Enterprise core workflows: purposeful, fast, unobtrusive. Marketing/onboarding:
expressive, personality-forward, can hold attention. Both are valid; miscalibration
(enterprise UI that feels like a website, brand animation that feels clinical) is a
failure mode.

---

## Failure Modes — Hub Level

- **Decorative animation in dense UIs** — motion that serves the designer's
  enjoyment, not the user's comprehension
- **Animate-everything disease** — every element on a page entrance has its own
  animation, fragmenting attention and increasing cognitive load
- **Forgetting reduced-motion** — designing only the standard experience; the
  accommodation is an afterthought bolted on at the end
- **Animating layout properties** — `width`, `height`, `top`, `left` cause
  layout recalculation on every frame; guaranteed jank
- **Duration inflation** — transitions that take 600ms+ for a simple state change;
  the UI feels sluggish
- **Missing spatial logic** — transitions that don't reflect where elements "are"
  in the interface's spatial model; drawers that slide in from the wrong direction
- **Wrong easing for context** — linear on a UI element (robotic), ease-in on an
  entrance (the element decelerates to its starting position, which makes no sense)

---

## Cross-Hub References

### `lead-motion-designer` → `lead-graphic-designer`
- `motion-principles` ← `gd-visual-communication`: visual weight, direction, and
  spatial relationships from graphic design translate to time-based motion
- `motion-3d-spatial` ← `gd-image-composition`: compositional depth and layering
  principles apply to 3D motion
- `motion-choreography` ← `gd-grid-and-layout`: rhythm and visual organization
  principles translate to temporal sequencing

### `lead-motion-designer` → `lead-ui-designer`
- `motion-transitions` ↔ `uid-visual-system`: motion is part of the visual language;
  motion character should be defined in the visual system alongside type and color
- `motion-3d-spatial` ↔ `uid-surface-depth`: the elevation/depth model defines
  where Z-axis motion should occur and what it means
- `motion-choreography` → `uid-visual-critique`: aesthetic evaluation of motion
  sequences as a visual design discipline

### `lead-motion-designer` → `lead-ux-designer`
- `motion-transitions` ↔ `ux-interaction-design`: state change animations are
  interaction design decisions, not visual design afterthoughts
- `motion-accessibility` ↔ `ux-accessibility`: motion accessibility is a
  dimension of inclusive design
- `motion-choreography` → `ux-performance-perception`: well-designed motion
  transitions and loading sequences directly affect perceived performance

### `lead-motion-designer` → `lead-frontend-engineer`
- `motion-performance` ↔ `fe-performance`: compositor layer promotion and frame
  budget are shared engineering and design concerns
- `motion-tooling` ↔ `fe-component-architecture`: GSAP/Framer Motion integration
  patterns affect component architecture decisions
- `motion-accessibility` → `fe-accessibility`: prefers-reduced-motion
  implementation is an engineering responsibility

### `lead-motion-designer` → `lead-accessibility-architect`
- `motion-accessibility` → `a11y-neurodiversity`: vestibular disorders, cognitive
  motion load, autoplay considerations
- `motion-accessibility` → `a11y-visual`: photosensitivity and flicker thresholds
  (WCAG 2.3.1)

---

## Design-Forward Operating Directive

Motion is a design material. Like color, type, and space, it communicates before
the user consciously processes it. The felt quality of a transition — whether it
suggests confidence or hesitation, weight or weightlessness, clarity or confusion —
is a design outcome that must be intentionally shaped.

This skill network operates from the position that motion craft is inseparable from
product quality. A design system that specifies color and typography but leaves
motion to individual developer judgment will produce incoherent motion — too fast
here, too slow there, wrong easing everywhere. Motion tokens, choreography
guidelines, and reduced-motion alternatives belong in the design system as first-class
citizens alongside spacing and color.

The eye and the body are the final validators. Profiling tools confirm performance;
vestibular safety guidelines set minimum thresholds; but whether motion feels right
is a human judgment that requires rehearsal, iteration, and critique.

---

## References

- Disney's 12 Principles of Animation (Thomas & Johnston, *The Illusion of Life*)
- Dan Saffer, *Microinteractions*
- Val Head, *Designing Interface Animation*
- WCAG 2.1 Success Criterion 2.3.1 (Three Flashes or Below Threshold)
- WCAG 2.1 Success Criterion 2.3.3 (Animation from Interactions — AAA)
- Google Material Motion guidelines
- Apple Human Interface Guidelines — Motion
- GSAP documentation (greensock.com/docs)
- Framer Motion documentation (framer.com/motion)
