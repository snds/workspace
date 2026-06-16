---
name: motion-principles
description: >
  Disney's 12 animation principles adapted for digital UI — where they translate
  directly and where they must be modified. Easing vocabulary for interface motion:
  when to use each curve, spring physics, cubic-bezier construction. Use this skill
  whenever the conversation touches: easing selection, timing feel, spring physics,
  why an animation feels wrong, squash and stretch in UI, anticipation in interactions,
  staging attention with motion, ease-in vs ease-out confusion, overshoot and settle,
  arc motion, secondary action, timing relative to element weight/size, follow-through,
  or any question about the underlying principles that govern how motion communicates.
aliases: [motion-principles]
tier: spoke
domain: design
hub: lead-motion-designer
prerequisites: [lead-motion-designer]
spec_version: "2.0"
---

# Motion Principles

Specialist lens for the foundational principles governing motion in digital
interfaces. Part of the lead-motion-designer skill network.

---

## Domain Boundary

This skill owns **why motion feels the way it does** — the principles and easing
vocabulary that make animation feel right or wrong.

- **Which transition to use for a specific interaction** → `motion-transitions`
- **Sequencing multiple elements** → `motion-choreography`
- **Performance of the chosen approach** → `motion-performance`
- **Implementation in a specific library** → `motion-tooling`

---

## Disney's 12 Principles — Applied to UI

The 12 principles were formalized by Frank Thomas and Ollie Johnston for character
animation. They describe how physical objects behave under forces. UI elements are
not characters, and UI motion is not narrative — but the principles describe how
human perception processes movement, which makes them applicable whenever interface
elements move.

The adaptation requires judgment: some principles translate almost directly, some
require significant modification, and one (exaggeration) is almost entirely
contextual.

---

### 1. Squash and Stretch

**Original**: Conveys weight, mass, and elasticity. A bouncing ball squashes on
impact and stretches in flight.

**UI adaptation**: Literal squash and stretch (deforming elements) looks cartoonish
in enterprise interfaces. The principle translates as:

- **Spring physics**: An element that overshoots its target position and settles
  back conveys the same sense of elasticity without deforming geometry
- **Subtle scale-in**: An element that grows from 95% to 100% as it enters suggests
  it arrived with force — the scale is the "stretch" moment
- **When to use**: Confirmation states (a button that subtly scales up on press),
  bounce-settle on drop targets, drawer handles with spring resistance
- **When not to use**: Data tables, form fields, navigation — anything in a primary
  workflow where users need to read, not feel

**Easing connection**: Spring easing (see Easing Vocabulary section) is the
mechanical implementation of squash-and-stretch in UI.

---

### 2. Anticipation

**Original**: Before a major action, a small setup motion primes the viewer. A
character bends their knees before jumping.

**UI adaptation**: Anticipation in UI should be subtle and fast — it's a signal,
not a performance.

- **Button depression**: A button that scales down 2–3% on mousedown before
  triggering its action signals that the input was received
- **Loading indicator before content**: A skeleton screen that appears immediately
  on navigation primes the user for content before the data arrives
- **Drawer handle pre-motion**: A slight movement before a drawer opens suggests
  the element is about to change
- **Duration guideline**: Anticipation beats should be 50–100ms — long enough to
  register, too fast to feel slow
- **Failure mode**: Anticipation that takes longer than the action itself feels like
  lag, not personality

---

### 3. Staging

**Original**: Compose the scene so the audience's eye goes to the most important
element. One clear read at a time.

**UI adaptation**: This principle has the highest direct applicability to UI.

- **Entrance animation only on the primary element**: When a dialog opens, the
  dialog itself animates in. The backdrop dims. The 12 form fields inside do not
  each animate individually — that fragments attention without serving the user
- **Directing attention at the right moment**: An error message that shakes draws
  the eye; a success checkmark that draws itself confirms without demanding
- **Motion as attention direction**: In an onboarding sequence, motion directs the
  user through the UI in the intended reading order
- **Failure mode**: Animating every element on a page load is the opposite of
  staging — it creates visual noise with no focal point
- **The 1-thing rule**: At any moment, only one thing should be moving unless
  the elements have an explicit choreographic relationship (see `motion-choreography`)

---

### 4. Straight Ahead vs. Pose-to-Pose

**Original**: "Straight ahead" animators draw every frame in sequence; "pose-to-pose"
animators define key poses and fill in between. Each produces a different quality.

**UI adaptation**: This maps directly to implementation choices.

| Approach | Animation Equivalent | Qualities | When to Use |
|----------|---------------------|-----------|-------------|
| Straight ahead | Physics-based / spring animation | Emergent, organic, hard to time-sync | Draggable elements, elastic UI, physics-feel interactions |
| Pose-to-pose | Keyframe-based animation | Predictable, easy to sequence, controllable | Choreographed sequences, onboarding, loading states |

- **Physics-based** (spring): The animation runs until forces equilibrate — duration
  isn't specified, behavior is. Feels alive, hard to sync with other elements.
- **Keyframe-based** (duration + easing): The animation runs for exactly N ms — easy
  to sequence, consistent timing. Feels designed, can feel mechanical if easing is wrong.
- Most UI work uses keyframe-based; spring physics is reserved for elements that
  need tactile, physical feel (drag handles, swipe interactions, elastic lists)

---

### 5. Follow-Through and Overlapping Action

**Original**: After the primary action stops, secondary elements continue briefly.
A character's coat continues moving after they stop walking.

**UI adaptation**:

- **Trailing elements in a list stagger**: When a list animates in, each row
  follows the one before it — the list "arrives" with momentum
- **Scroll momentum**: Physics-based scroll deceleration rather than instant stop
- **Element groups with internal motion**: An icon with a secondary element (a
  badge, an indicator) that settles a beat after the primary icon
- **Stagger as follow-through**: A parent container animates in, then its children
  follow — the children are "carried" by the parent's arrival
- Cross-reference `motion-choreography` for timing the overlap correctly

---

### 6. Slow In and Slow Out (Easing)

**Original**: Natural objects accelerate from rest and decelerate to rest. Pure
linear motion is mechanical and unnatural.

**UI adaptation**: See the full Easing Vocabulary section below. This principle is
the foundation of all interface easing decisions.

The core rule for UI:
- **Elements entering the viewport** were already in motion before they appeared —
  use **ease-out** (start fast, decelerate to rest)
- **Elements leaving the viewport** decelerate to a stop in the distance —
  use **ease-in** (start slow, accelerate out)
- **Elements repositioning on-screen** were at rest, move, and stop — use
  **ease-in-out** (slow at both ends)

---

### 7. Arcs

**Original**: Natural motion follows curved paths, not straight lines. A thrown
object arcs; a character's hand traces an arc.

**UI adaptation**:

- **Dialog appearance**: A dialog that scales from 95% to 100% while also shifting
  slightly upward traces an arc-like path — more natural than pure scale
- **Tooltip positioning**: Tooltips that animate from their anchor point along a
  slight arc feel placed rather than teleported
- **Floating elements**: Floating action buttons, toast notifications, and other
  elements that move to new positions should follow slight arcs
- **In practice**: Arcs in UI are usually implemented as combined transform
  animations (translate + scale simultaneously) rather than actual curved paths —
  the arc is implied by the combination of motions
- **When to skip**: Simple slide transitions (drawers, panels) don't need arc
  motion — the straight line is correct for elements that move along a constrained
  axis

---

### 8. Secondary Action

**Original**: A secondary motion that reinforces the primary action without
competing with it. A character thinking might drum their fingers.

**UI adaptation**:

- **Icon micro-animation during primary action**: A send button whose paper-plane
  icon briefly animates while the form submits — the secondary animation confirms
  the action without being the action
- **Loading spinner during content replacement**: The spinner confirms that work
  is happening while the primary action (content loading) is the real event
- **Status indicator pulse**: A "live" indicator that subtly pulses — secondary
  to whatever the user is actually doing
- **Constraint**: Secondary action must not compete with the primary. If the user
  needs to read something, don't animate near it. If the primary action is
  visually dramatic (a page transition), suppress secondary animations.

---

### 9. Timing

**Original**: The number of frames determines the speed of the action — fast is
light/small/excited, slow is heavy/large/deliberate.

**UI adaptation**: Duration should reflect perceived physical properties of the
element.

| Element Type | Duration Range | Why |
|-------------|---------------|-----|
| Micro-interaction (button, toggle) | 100–200ms | Light, immediate feedback |
| Component state change | 200–300ms | Medium weight, in-context change |
| Panel/drawer/sheet | 250–350ms | Large element, physical weight |
| Page/view transition | 300–400ms | Maximum weight for UI transition |
| Complex choreography | Up to 600ms total | Multi-element sequence |

- **Larger = slower**: A full-screen modal moves more slowly than a tooltip
- **Further = longer**: An element traveling a greater distance takes longer
- **Never justify long duration with complexity**: A 1-second UI transition is
  always a failure — complexity should be handled with choreography (overlapping
  actions that overlap in time), not by increasing total duration
- **Failure mode**: "Premium" = slow. This is false. Fast, tight, purposeful
  motion reads as high quality. Slow motion reads as sluggish.

---

### 10. Exaggeration

**Original**: Push movements beyond reality for expressiveness. A take can go
further than real life.

**UI adaptation**: Exaggeration has narrow application in enterprise UI.

**Where it belongs**:
- Empty states (no data, first use, completion celebrations)
- Onboarding sequences
- Success/celebration moments (confetti, achievement unlocks)
- Brand animation in marketing contexts
- Error states where a slightly overdone reaction clarifies severity

**Where it does not belong**:
- Primary navigation
- Data tables or lists
- Form interactions
- Any workflow where the user is in a task-execution mode

**Calibration**: In enterprise SaaS, "exaggeration" might mean a 10% overshoot on
a spring animation — not a cartoon bounce. Context governs the threshold.

---

### 11. Solid Drawing

**Original**: Even in 2D animation, the animator understands the 3D form of what
they're drawing. Spatial awareness produces consistent volume.

**UI adaptation**: The highest-level concept with the broadest application.

- **Know where elements live in the Z-stack**: Before animating a transition,
  establish the spatial model — is this element in front of or behind its destination?
  Does it travel toward or away from the viewer?
- **Spatial consistency across the interface**: If modals rise toward the viewer,
  they should all rise from the same conceptual surface. If drawers slide in from
  an edge, the edge should correspond to the navigation structure.
- **Implied depth informs motion direction**: An element at a higher elevation
  (above the surface) should cast a shadow and move differently than a surface-level
  element
- Cross-reference `motion-3d-spatial` for the technical implementation of spatial
  reasoning in flat interfaces

---

### 12. Appeal

**Original**: Movement should be satisfying to watch. Character must have appeal.

**UI adaptation**: The most subjective principle — but not unmeasurable.

- **Spring physics over stepped easing**: Physical spring behavior feels
  satisfying; cubic-bezier approximations that miss the physics feel flat
- **Coherent easing language**: All elements in the same product moving with the
  same easing family feels intentional; mismatched easing feels like nobody was in
  charge
- **Timing precision**: A 200ms transition with perfectly tuned easing reads as
  more "premium" than a 300ms transition with generic ease-in-out
- **The test**: Does the UI feel satisfying to use? Are transitions noticed only
  when they're absent? If users comment on the animation (positively), it's too
  much. If they comment on the feel (positively), it's exactly right.

---

## Easing Vocabulary for UI

The easing curve is the most important single decision in any animation. Wrong
easing makes technically correct motion feel wrong.

### Core Curves

| Curve | CSS Function | When | Never |
|-------|-------------|------|-------|
| **linear** | `linear` | Loading progress bars (mechanical accuracy required) | Any UI element with implied mass |
| **ease-out** | `cubic-bezier(0, 0, 0.2, 1)` | **All entrances** — element arrives from off-screen or from zero | Exits |
| **ease-in** | `cubic-bezier(0.4, 0, 1, 1)` | **All exits** — element departs, accelerates away | Entrances |
| **ease-in-out** | `cubic-bezier(0.4, 0, 0.2, 1)` | **Repositioning** — element moves from one on-screen position to another | Entrances or exits |
| **standard** | `cubic-bezier(0.2, 0, 0, 1)` | Default for most UI transitions (Material Design standard) | — |

### Why ease-out for entrances?

Elements entering from off-screen were already moving before they appeared. They
arrive with velocity and decelerate to rest. This is physically consistent.

An ease-in entrance (starting slow, ending fast) makes no physical sense: the
element accelerates as it arrives, as if it's pushing through the screen. It feels
wrong because it is physically wrong.

### Spring Physics

Spring easing is not a cubic-bezier — it's a physics simulation. Behavior is
defined by:

- **Stiffness** (spring constant, k): How resistant the spring is. High stiffness
  = fast, tight, little overshoot. Low stiffness = slow, loose, more overshoot.
- **Damping** (friction): How quickly energy dissipates. Underdamped = oscillates
  (bouncy). Critically damped = settles without overshoot. Overdamped = slow
  settle.
- **Mass**: The simulated mass of the element. Higher mass = slower response.

**Spring presets for UI contexts**:

| Context | Stiffness | Damping | Character |
|---------|-----------|---------|-----------|
| Snappy confirmation (button press) | High (300–500) | High (30–40) | Fast, minimal overshoot |
| Drawer/sheet open | Medium (200–280) | Medium (25–30) | Physical feel, settles cleanly |
| Elastic dismiss (swipe to delete) | Low (100–150) | Low (15–20) | Bouncy, tactile |
| Repositioning | High (350) | High (35) | Fast, purpose-driven |

Spring libraries: Framer Motion (`spring` transition type), react-spring, GSAP
Elastic ease, CSS spring (limited support). See `motion-tooling`.

### Custom Cubic-Bezier Construction

When standard curves aren't right, construct a custom cubic-bezier:

The curve is defined by two control points: `(x1, y1)` and `(x2, y2)`.

- `x` values: timing (when along the duration the change happens)
- `y` values: progression (how much of the change has happened)
- Both axes: 0 = start, 1 = end
- `y` values can exceed 0–1 to create overshoot

**Construction tool**: cubic-bezier.com — visual editor, copy CSS output.

**Reading a cubic-bezier**: If the curve starts steep and flattens → ease-out
(fast start, decelerating). If the curve starts flat and steepens → ease-in
(accelerating). If it's S-shaped → ease-in-out.

---

## Failure Modes

- **Linear easing on everything**: The default in many libraries; produces
  mechanical, robotic motion
- **Ease-in on entrances**: Physically wrong, feels like the element is fighting
  its way onto screen
- **Same easing for enter and exit**: Enter and exit are opposite physical events;
  they should use opposite curves
- **Over-springing**: Excessive bounce on enterprise UI elements draws attention
  to the spring rather than the content; reserve for tactile/physical contexts
- **Duration longer than necessary**: Every extra 50ms on a common interaction is
  multiplied by how many times per session the user triggers it
- **Ignoring the easing library**: Using whatever default the framework provides
  instead of choosing based on context

---

## Cross-Links

- `motion-choreography` — applying timing principles to multi-element sequences
- `motion-transitions` — selecting the right transition type for specific contexts
- `motion-3d-spatial` — solid drawing principle and spatial reasoning in depth
- `motion-tooling` — spring physics library implementations
- `gd-visual-communication` — visual weight and direction as design foundations
  that motion principles extend into time

---

## References

- Frank Thomas & Ollie Johnston, *The Illusion of Life: Disney Animation* (1981)
- Rachel Nabors, *Web Animation at Work* (A Book Apart)
- Val Head, *Designing Interface Animation*
- Pasquale D'Silva, "Transitional Interfaces" (Medium, 2013)
- Google Material Design Motion documentation
- cubic-bezier.com (Lea Verou)
