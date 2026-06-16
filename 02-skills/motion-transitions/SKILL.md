---
name: motion-transitions
description: >
  Page and view transitions, component state change animations, micro-interactions,
  enter/exit conventions, and duration guidelines for digital interfaces. Use this
  skill whenever the conversation touches: page transitions, view transitions,
  shared element transitions, modal open/close animation, drawer slide, dropdown
  animation, tooltip animation, component state changes (show/hide, expand/collapse,
  enable/disable, loading/loaded, error/success), skeleton-to-content transitions,
  micro-interaction design, enter/exit direction conventions, transition duration
  selection, or any question about how a specific UI element or view should move.
---

# Motion Transitions

Specialist lens for interface transitions — the vocabulary of how UI elements enter,
exit, change state, and communicate spatial relationships through motion.
Part of the lead-motion-designer skill network.

---

## Domain Boundary

This skill owns **which transition to use and why** for specific UI contexts.

- **Why the chosen easing feels right or wrong** → `motion-principles`
- **Sequencing multiple elements in a transition** → `motion-choreography`
- **Performance of transition implementation** → `motion-performance`
- **Accessibility: prefers-reduced-motion alternatives** → `motion-accessibility`
- **Implementation library** → `motion-tooling`

---

## Transition Hierarchy

Transitions operate at four scopes. The scope determines the appropriate scale of
motion, duration, and choreographic complexity.

| Scope | Examples | Duration Range | Complexity |
|-------|----------|---------------|------------|
| **Page/view** | Route changes, wizard steps, tab views | 300–400ms | High — shared elements, directional logic |
| **Section** | Expanding panels, split-view changes, layout shifts | 250–350ms | Medium — layout-aware |
| **Component** | Modal, drawer, dropdown, tooltip, popover | 200–300ms | Low-medium — enter/exit pair |
| **Micro-interaction** | Button press, toggle, checkbox, form feedback | 100–200ms | Low — immediate feedback |

**Escalation rule**: If a transition feels too slow at the recommended duration,
the motion is probably wrong — not the duration. Increase duration only when
element mass or visual complexity genuinely demands it.

---

## Page and View Transitions

### Spatial Model

Before choosing a page transition, establish the spatial model of the application:
where do pages "live" relative to each other? Users build spatial memory from
consistent directional transitions — the app feels like a place they can navigate.

**Common spatial models**:

- **Hierarchical (drill-down)**: Parent → child navigates forward (slides left /
  scales up); child → parent navigates back (slides right / scales down). The
  child page "lives" inside the parent.
- **Sequential (tabs, wizard steps)**: Steps navigate in a linear order; left-to-right
  for forward, right-to-left for back. Or use a progress-aware direction.
- **Sibling (peer views)**: Flat navigation between pages of equal hierarchy; fade
  or scale-in works well; no strong directional convention required.
- **Modal/overlay (contextual)**: The new view overlays the current context; it
  comes from below (rises) or from an edge; dismissal reverses the direction.

**Consistency requirement**: Establish the model once, apply it everywhere. A
back navigation that slides from the wrong direction breaks the spatial model and
causes disorientation.

### Transition Types

#### Fade
- **Communicates**: Temporal — the old state ends, the new state begins; no spatial
  relationship
- **Use when**: Sibling views with no meaningful spatial relationship; most
  flexible default
- **Duration**: 200–300ms; overlay-dissolve at 150–200ms
- **Failure mode**: Using fade for hierarchical navigation loses the spatial
  relationship the user built

#### Slide (with directional convention)
- **Communicates**: Spatial — the new view comes from the direction it "lives"
- **Variants**: Horizontal slide (hierarchical nav), vertical slide (modal sheet
  from bottom, notification from top), directional (matches swipe gesture)
- **Use when**: Navigation with strong spatial metaphor; gesture-driven interfaces
- **Duration**: 300–350ms for full-screen; 250ms for partial panels
- **Failure mode**: Using slide without establishing a consistent directional model;
  the direction feels arbitrary

#### Scale (push / expand)
- **Communicates**: The new view expands from a source element or from a focal
  point; the user "enters" something
- **Use when**: Drill-down from a card or list item; the new view is "inside"
  the previous element
- **Direction**: Scale from the position of the triggering element (shared element
  transition origin)
- **Duration**: 300–400ms; requires ease-out (arriving with velocity)
- **Failure mode**: Scale without a source element origin feels like the view
  appears from nowhere

#### Shared Element Transition
- **Communicates**: This is the same element, transformed — continuity across
  a context change
- **Mechanism**: A card's image/title morphs into the hero image/title on the
  detail view; the element provides a through-line of identity
- **Use when**: List/detail patterns where the relationship between the list item
  and the detail view should be explicit
- **Implementation**: The element animates position, size, and shape while the
  rest of the content cross-fades. FLIP technique or View Transitions API.
  See `motion-performance` (FLIP) and `motion-tooling` (implementation).
- **Failure mode**: Using shared element for elements that don't have a meaningful
  identity relationship; feels gimmicky without semantic purpose

### CSS View Transitions API

The native browser API for page transitions in single-page and multi-page apps.

```css
::view-transition-old(root) { animation: fade-out 200ms ease-in; }
::view-transition-new(root) { animation: fade-in 200ms ease-out; }

/* Named shared element */
.hero-image { view-transition-name: hero; }
```

- Supported in Chrome/Edge 111+; Safari 18+; Firefox partial
- For named elements, the browser automatically cross-fades and morphs position/size
- Opt-in per-element; no named transition = default fade

---

## Component Transitions

### Modal / Dialog

The modal represents the highest elevation in the layer stack — it appears above
everything and demands focus.

**Enter**: Scale from 95% to 100% + fade in (0 → 1 opacity). Duration: 200–250ms.
Ease-out. The backdrop fades in simultaneously at a slightly longer duration (250–300ms)
to feel like it settles slightly after the modal arrives.

**Exit**: Scale down to 95% + fade out. Duration: 150–200ms. Ease-in (accelerate
away). Exit is faster than enter — the user has dismissed; don't keep them waiting.

**Vertical origin variant**: On mobile, full-sheet modals slide up from the bottom
edge. Enter: translateY from 100% to 0 + fade. Exit: translateY back to 100%.

**Failure modes**:
- Scale > 5% looks cartoonish in enterprise contexts
- Same duration for enter and exit (exit should be faster)
- Animating content inside the modal as it enters (content fragmentation)

### Drawer / Side Panel

Drawers originate from an edge and slide in. The edge should correspond to the
navigational structure (left for primary navigation, right for contextual panels).

**Enter**: TranslateX from the edge (100% for right drawer, -100% for left) to 0.
Ease-out. Duration: 250–300ms. Backdrop (if any) fades in simultaneously.

**Exit**: TranslateX back to edge. Ease-in. Duration: 200–250ms.

**Failure modes**:
- Wrong edge (a contextual details panel sliding from the left)
- Drawer that animates past its final position and bounces back (overshoot on a
  drawer that doesn't warrant it)

### Dropdown / Menu

Dropdowns have a clear origin — they open from the element that triggered them.

**Enter**: Scale from ~90% to 100% with origin at the triggering element, + fade.
Duration: 150–200ms. Ease-out. The scale origin is the corner closest to the trigger.

**Exit**: Fade out only, no scale. Duration: 100–150ms. The scale on exit is often
imperceptible and adds unnecessary computation.

**Failure mode**: Dropdown that opens "downward" from a trigger at the bottom of
the viewport — should open upward when there's insufficient space.

### Tooltip / Popover

Tooltips have minimal motion — they are functional, not decorative.

**Enter**: Fade in from ~95% opacity over 100–150ms with a slight offset shift
(1–2px toward the viewport center). Ease-out.

**Exit**: Fade out over 75–100ms. No delay (tooltips dismiss on hover-out; any
delay feels sluggish).

**Failure mode**: Tooltip with a dramatic animation (scale, slide) that takes
150ms+ — the tooltip should feel like it was already there.

### Accordion / Expand-Collapse

**Expand**: The content area height grows from 0 to its natural height.
Cross-fade any icon (chevron rotates 180°). Duration: 200–250ms.

**Implementation note**: Animating `height` from 0 to `auto` requires a technique:
- CSS: animate `max-height` (inexact but functional), or use `grid-template-rows: 0fr → 1fr`
- JS: calculate height, set explicit pixel value, animate, then set to `auto`
- Framer Motion: `AnimatePresence` + `motion.div` handles this automatically

**Collapse**: Reverse. Duration slightly faster (175–225ms).

**Failure mode**: Using `height` animation that triggers layout on every frame —
route to `motion-performance` for the correct approach.

---

## Micro-Interactions

### Anatomy (Dan Saffer's Model)

Every micro-interaction has four components:

1. **Trigger**: What initiates the interaction (user action or system event)
2. **Rules**: What happens (the logic of the response)
3. **Feedback**: How the system communicates back to the user
4. **Loops/Modes**: How the interaction changes over time or in different states

Animation is the **feedback** component. Good micro-interaction animation is
specific to the trigger — a button press feedback is different from a form
validation feedback is different from a file upload feedback.

### Feedback Patterns by Type

#### Confirmation (action received)
- Button press: scale down 2–3% on press, spring back on release. Duration: 100ms.
- Toggle/switch: thumb slides with spring easing. Duration: 200ms.
- Checkbox/radio: fill or check animates in. Duration: 150ms.

#### Error / Invalid Input
- Shake: translateX oscillation (4 cycles of ±4px). Total duration: 300–400ms.
  Faster than it looks — each cycle is 75–100ms.
- Color transition to error state: 150ms ease-out.
- Failure mode: Shake on every keystroke in real-time validation — only on submit
  or on blur.

#### Success / Completion
- Checkmark draw: SVG stroke-dashoffset animation. Duration: 300–400ms.
- Color transition to success state: 200ms ease-out.
- Confetti/celebration: Only for true achievement milestones — not every form submit.

#### Loading
- Skeleton to content: Content fades in with slight upward shift (4–8px).
  Duration: 200–300ms. Ease-out.
- Progress indicator: Linear easing on genuine progress bars (reflects real state);
  ease-in-out on indeterminate.
- Shimmer/pulse on skeleton: 1.5–2s loop; ease-in-out; never in reduced-motion mode.

---

## Enter/Exit Direction Conventions

Consistent direction conventions build spatial memory. Break them only with intent.

| Element | Enter From | Exit To |
|---------|-----------|---------|
| Dropdown (below trigger) | Scales from trigger, opens down | Fades out |
| Dropdown (above trigger) | Scales from trigger, opens up | Fades out |
| Drawer (left nav) | Slides in from left | Slides out to left |
| Drawer (right panel) | Slides in from right | Slides out to right |
| Bottom sheet | Slides up from bottom | Slides down to bottom |
| Toast / notification | Slides in from top edge | Fades out (or slides back up) |
| Modal dialog | Scales in from center | Scales out to center |
| Tooltip | Fades + slight toward-center offset | Fades |
| Page: drill down | New page slides in from right | Previous page slides out to left |
| Page: back | Current page slides out to right | Previous page reveals from left |

---

## Duration Reference

| Context | Duration | Reasoning |
|---------|----------|-----------|
| Hover feedback (color, shadow) | 50–100ms | Immediate; longer feels laggy |
| Micro-interaction (button, toggle) | 100–200ms | Fast confirmation |
| Tooltip appear | 100–150ms | Functional; don't delay reading |
| Dropdown open | 150–200ms | Small element |
| Component state change | 200–300ms | Medium weight |
| Modal enter | 200–250ms | High elevation element |
| Drawer enter | 250–300ms | Large element, physical weight |
| Page transition | 300–400ms | Maximum scope |
| Complex choreography | Up to 600ms total | Multi-element; see choreography |
| Never | > 600ms for UI | Interaction, not narrative |

---

## Failure Modes

- **Asymmetric durations**: Exit faster than enter is correct; enter faster than
  exit feels like the UI is rushing to show you something then refusing to leave
- **No exit animation**: Elements that snap off feel broken; even a 100ms fade
  is better than instant removal
- **Directionally inconsistent transitions**: Drawer sliding from wrong edge;
  page transition direction that contradicts the navigation hierarchy
- **Content animating inside a transitioning container**: A modal whose internal
  content also animates produces visual noise; animate the container, not the content
- **Hover-state animations with no reduced-motion consideration**: Continuous or
  hover-triggered animations must have fallbacks

---

## Cross-Links

- `motion-principles` — easing selection for each transition type
- `motion-choreography` — sequencing multiple elements within a transition
- `motion-accessibility` — reduced-motion alternatives for every pattern here
- `motion-performance` — FLIP for height animations; compositor-layer compliance
- `motion-tooling` — AnimatePresence (Framer Motion), GSAP, View Transitions API
- `ux-interaction-design` — interaction design patterns that drive transition decisions

---

## References

- Dan Saffer, *Microinteractions* (O'Reilly, 2013)
- Google Material Design — Motion/Transitions
- Apple HIG — Animation
- CSS View Transitions API spec (WICG)
- Framer Motion documentation — AnimatePresence
