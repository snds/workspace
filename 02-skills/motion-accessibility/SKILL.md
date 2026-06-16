---
name: motion-accessibility
description: >
  Motion accessibility for digital interfaces — vestibular disorders, seizure and
  photosensitivity thresholds, cognitive motion load, prefers-reduced-motion
  implementation, and motion tokens in design systems. Use this skill whenever the
  conversation touches: prefers-reduced-motion, reduced-motion alternatives,
  vestibular disorders, motion sickness from UI, parallax accessibility, looping
  animation accessibility, autoplay video/animation, WCAG 2.3.1 (flicker/seizure),
  cognitive motion load, motion in design systems, motion tokens, a11y for
  animation, reduced motion testing, or any question about making motion safe and
  inclusive.
aliases: [motion-accessibility]
tier: spoke
domain: design
hub: lead-motion-designer
prerequisites: [lead-motion-designer]
spec_version: "2.0"
---

# Motion Accessibility

Specialist lens for designing motion that is safe, inclusive, and appropriately
restrained. Part of the lead-motion-designer skill network.

---

## Domain Boundary

This skill owns **motion safety and accommodation** — designing motion that
doesn't cause harm and that communicates effectively in reduced-motion contexts.

- **Designing reduced-motion alternatives** — this skill (the alternatives are
  a motion design problem, not just a CSS toggle)
- **Implementation of prefers-reduced-motion in specific frameworks** → `fe-accessibility`
- **Motion tokens in the design system** — this skill + `ds-advisor`
- **WCAG compliance for other a11y dimensions** → `lead-accessibility-architect`
- **Cognitive accessibility beyond motion** → `a11y-neurodiversity`

---

## The Stakes

Motion can cause physical harm. This is not a design edge case — it is a
medical reality affecting a population large enough to constitute a significant
fraction of any product's user base.

The three categories of harm from motion in digital interfaces:
1. **Vestibular dysfunction**: Dizziness, nausea, headaches, vomiting triggered
   by spatial motion effects (parallax, zoom, rotation, scroll-linked animation)
2. **Seizure / photosensitive epilepsy**: Seizures triggered by rapid flashing
   or high-contrast alternation
3. **Cognitive overload**: Fragmented attention, increased error rate, and anxiety
   from ambient, continuous, or excessive simultaneous motion

None of these are fringe concerns. Vestibular disorders affect a meaningful portion
of the adult population in varying severity. Designing without reduced-motion
accommodation is a choice to exclude and potentially harm those users.

---

## Vestibular Disorders

### What They Are

The vestibular system (inner ear + brain) processes spatial orientation, balance,
and self-motion. When the vestibular system receives signals that conflict with
visual motion, it produces symptoms: dizziness, vertigo, nausea, headaches,
disorientation, visual disturbance.

In digital interfaces, this conflict arises when the screen presents large-scale
motion — parallax scrolling, full-screen zoom effects, sweeping camera-style
transitions, auto-scrolling content, rapid spatial movement.

### Triggers in UI

High-risk motion patterns for vestibular dysfunction:

| Pattern | Risk Level | Why |
|---------|-----------|-----|
| Parallax scrolling (multi-layer) | High | Persistent, large-scale, scroll-linked spatial conflict |
| Full-screen zoom/scale transitions | High | Rapid spatial disorientation |
| Auto-scrolling content | High | Motion user didn't initiate |
| Looping / ambient animation in the background | Medium-High | Persistent peripheral motion |
| Rapid transitions (< 200ms for large elements) | Medium | Too fast for vestibular system to adapt |
| Rotation (spin animations) | Medium | Spatial disorientation |
| Diagonal motion | Low-Medium | Less natural than horizontal/vertical |

Low-risk patterns that are generally safe:
- Fade (opacity only)
- Small-scale transforms (< 5% scale change)
- Short, purposeful, user-triggered transitions
- Color changes

### WCAG 2.3.3 — Animation from Interactions (AAA)

*"For any motion animation triggered by interaction, the user can disable the
motion animation unless the animation is essential to the functionality or the
information being conveyed."*

This is Level AAA — aspirational, not required for baseline compliance. But the
guidance is clear: triggered motion should be suppressible. `prefers-reduced-motion`
is the practical implementation of this criterion.

---

## Seizure Safety: WCAG 2.3.1

### Three Flashes or Below Threshold (Level A — Required)

*"Web pages do not contain anything that flashes more than three times in any
one second period, or the flash is below the general flash and red flash thresholds."*

This is a hard requirement, not a guideline.

### Thresholds

The general flash threshold: a flash is a pair of opposing changes in luminance.
Violating any of these conditions is a WCAG failure:

- More than 3 flashes per second in any area of the screen
- The flashing area exceeds 25% of the viewport (or approximately 341×256 pixels
  at 1024px width)
- High contrast alternation: the transition between states has a contrast ratio
  exceeding 3:1 and involves saturated red

**Practical rules**:
- Never build animations that flash — no strobe effects, no rapid color alternation
- Loading animations with blinking cursors or pulsing indicators must stay well
  below 3Hz
- Error state "flash" feedback (highlighting a field) must be a one-time event,
  not a loop
- If in doubt, test with the Photosensitive Epilepsy Analysis Tool (PEAT)

### Red Flash

Red transitions are independently regulated — high-contrast transitions to/from
saturated red at > 3Hz are a separate WCAG failure even if the general threshold
is met. Avoid rapid red flashing entirely.

---

## prefers-reduced-motion

### The Media Query

```css
@media (prefers-reduced-motion: reduce) {
  /* reduced motion styles */
}

@media (prefers-reduced-motion: no-preference) {
  /* standard motion styles (can also be the default with this as the enhancement) */
}
```

The user sets this preference in their OS:
- macOS: System Settings → Accessibility → Display → Reduce Motion
- iOS: Settings → Accessibility → Motion → Reduce Motion
- Windows: System Settings → Accessibility → Visual Effects → Animation Effects
- Android: Settings → Accessibility → Remove Animations

### What "Reduce" Means

"Reduce" does not mean "remove all animation." It means: replace motion-heavy
animations with motion-light alternatives that communicate the same information.

The alternatives should still work. A page transition with `prefers-reduced-motion`
should still feel like a transition — it just shouldn't involve spatial movement
that triggers vestibular symptoms.

**Safe alternatives under reduced-motion**:
- Fade / opacity change (the gold standard reduced-motion alternative)
- Color change
- Very short, small-scale transforms (< 5% scale over < 150ms)
- Instant state changes with no animation (last resort — jarring, but better than harm)

**What to replace specifically**:

| Standard Motion | Reduced-Motion Alternative |
|----------------|---------------------------|
| Parallax scroll | Static layers |
| Slide page transition | Fade cross-dissolve |
| Scale + slide modal enter | Fade in |
| Spring overshoot | Linear or gentle ease, no overshoot |
| Looping background animation | Static or paused |
| Scroll-linked animation | Instant state at threshold |
| Confetti / celebration animation | Fade-in success message |

### CSS Implementation Pattern

```css
/* Default: no motion */
.dialog {
  opacity: 0;
  transition: opacity 200ms ease-out;
}
.dialog.open {
  opacity: 1;
}

/* Enhancement: motion for users who haven't opted out */
@media (prefers-reduced-motion: no-preference) {
  .dialog {
    transform: scale(0.95);
    transition: opacity 200ms ease-out, transform 200ms ease-out;
  }
  .dialog.open {
    transform: scale(1);
  }
}
```

The progressive enhancement pattern: start with opacity-only (safe default),
add motion as an enhancement for users who haven't requested reduced motion.
This inverts the common pattern (motion by default, removed on query) but produces
better baseline behavior.

### JavaScript / React Implementation

```javascript
// Detect preference in JS
const prefersReducedMotion = window.matchMedia(
  '(prefers-reduced-motion: reduce)'
).matches;

// React hook
function usePrefersReducedMotion() {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  );
  useEffect(() => {
    const mql = window.matchMedia('(prefers-reduced-motion: reduce)');
    const listener = (e) => setPrefersReducedMotion(e.matches);
    mql.addEventListener('change', listener);
    return () => mql.removeEventListener('change', listener);
  }, []);
  return prefersReducedMotion;
}

// Framer Motion — built-in support
import { useReducedMotion } from 'framer-motion';
const shouldReduceMotion = useReducedMotion();
const animation = shouldReduceMotion ? { opacity: 1 } : { opacity: 1, scale: 1 };
```

---

## Cognitive Motion Load

### What It Is

Cognitive motion load is the attention and processing cost imposed by animation.
Motion automatically attracts the eye — this is a biological reflex, not a choice.
In high-density interfaces, every animation that runs demands a fraction of the
user's attention whether they want to give it or not.

Excessive simultaneous motion fragments attention, increases cognitive load, and
can cause anxiety in users with ADHD, autism spectrum conditions, or high general
cognitive load (which is most enterprise users in a task-execution context).

### Design Rules

1. **Motion should respond to user action, not run unprompted**: Ambient animation
   that runs continuously regardless of user action is a cognitive accessibility
   failure in workflow UIs. Reserve ambient motion for marketing pages, onboarding,
   and empty states.

2. **One thing moving at a time**: In core workflows, the 1-thing rule from
   `motion-principles` (Staging) is also an accessibility principle. Multiple
   elements moving simultaneously increases cognitive load.

3. **Loops stop or pause after a reasonable duration**: Looping animations that
   never stop are persistent cognitive load. WCAG 2.2.2 (Pause, Stop, Hide) requires
   that moving content that lasts more than 5 seconds can be paused, stopped, or
   hidden by the user.

4. **Autoplay is a failure in dense information environments**: Autoplay video,
   autoplay animation, and autoplaying carousels all initiate motion the user
   didn't request. This is both a vestibular risk and a cognitive load issue.

5. **Don't animate background elements during foreground tasks**: When the user is
   in a form, a modal, or a focused task, background animations should be paused
   or suppressed. Motion in the periphery during task execution is a distraction
   and a cognitive tax.

### WCAG 2.2.2 — Pause, Stop, Hide (Level A)

*"For any moving, blinking or scrolling information that (1) starts automatically,
(2) lasts more than five seconds, and (3) is presented in parallel with other content,
there is a mechanism for the user to pause, stop, or hide it."*

This is Level A — a baseline accessibility requirement, not aspirational.

---

## Autoplay

Autoplay of video or animation without user initiation is problematic on multiple
accessibility dimensions:

- **Vestibular**: Unexpected motion initiating without user action is a strong
  vestibular trigger
- **Cognitive load**: Unsolicited motion demands attention
- **WCAG 2.2.2**: Autoplay content lasting > 5 seconds requires pause/stop control
- **Screen reader interference**: Moving content can interfere with AT navigation

**Policy for interface contexts**: No autoplay animation in core workflow screens.
Autoplay may be appropriate on marketing pages, splash screens, and onboarding flows
where the animation IS the content — but must still respect `prefers-reduced-motion`.

---

## Motion Tokens in Design Systems

Motion without a design system foundation produces incoherent motion. Every component
makes its own timing and easing decisions; reduced-motion is handled inconsistently;
the product feels arbitrary.

### Token Structure

A minimal motion token system:

```
// Duration tokens
--motion-duration-instant: 0ms;        /* used under reduced-motion */
--motion-duration-fast: 100ms;         /* micro-interactions */
--motion-duration-normal: 200ms;       /* component transitions */
--motion-duration-slow: 300ms;         /* page-level transitions */
--motion-duration-complex: 500ms;      /* choreographed sequences */

// Easing tokens
--motion-easing-enter: cubic-bezier(0, 0, 0.2, 1);       /* ease-out */
--motion-easing-exit: cubic-bezier(0.4, 0, 1, 1);        /* ease-in */
--motion-easing-reposition: cubic-bezier(0.4, 0, 0.2, 1); /* ease-in-out */
--motion-easing-spring: /* library-specific spring config */;
```

### Reduced-Motion Token Layer

Each motion token should have a reduced-motion counterpart that the DS applies
automatically:

```css
@media (prefers-reduced-motion: reduce) {
  :root {
    --motion-duration-fast: 0ms;
    --motion-duration-normal: 0ms;
    --motion-duration-slow: 0ms;
    --motion-duration-complex: 0ms;
  }
}
```

This approach encodes the accommodation in the design system, not in every component.
When a component uses `var(--motion-duration-normal)`, it automatically gets 0ms
under reduced-motion without any component-level implementation.

**Richer alternative**: Instead of zeroing durations, provide a reduced-motion
duration tier that uses short opacity transitions rather than zero:

```css
@media (prefers-reduced-motion: reduce) {
  :root {
    --motion-duration-fast: 0ms;
    --motion-duration-normal: 150ms; /* fade only, not positional */
    --motion-easing-enter: linear;
    /* companion: components must also suppress transforms */
  }
}
```

This requires more careful DS engineering but produces better reduced-motion UX.
Cross-reference `ds-advisor` for design system token architecture.

---

## Testing for Motion Accessibility

### Manual Testing Checklist

- [ ] Enable `prefers-reduced-motion: reduce` in OS settings
- [ ] Walk through all primary workflows — are all animations replaced with
  appropriate alternatives? Does anything still have large-scale motion?
- [ ] Check for looping animations — do they have pause controls?
- [ ] Check for autoplay video/animation — does it stop or require user initiation?
- [ ] Verify no content flashes more than 3 times per second

### Screen Reader Considerations

Animations don't communicate to screen reader users — AT navigates the DOM, not
the visual layer. This is a secondary accessibility concern for motion, but relevant:

- Motion that hides information (text fades out) must also hide it from the DOM
- Motion that reveals information (accordion expand) must update ARIA state
  (`aria-expanded`, focus management) regardless of whether the animation runs

### Simulation Testing

There is no reliable software simulator for vestibular sensitivity — sensitivity
varies widely between individuals and depends on severity of condition, current
state (tired, stressed, or ill individuals are more sensitive), and screen size/distance.

The most reliable test: disable all positional/spatial animation yourself and evaluate
whether the interface still functions. If it does, the spatial animation was not
communicating essential information — it was decorative.

---

## Failure Modes

- **The CSS-only approach**: Slapping `@media (prefers-reduced-motion: reduce) { * { animation: none; } }`
  on the entire stylesheet. This produces jarring instant state changes for a
  population that already finds the interface challenging.
- **Reduced-motion as removal, not design**: Not designing alternatives — just
  disabling. The accommodated experience should feel intentional, not broken.
- **Forgetting JavaScript-driven animations**: CSS media queries don't automatically
  affect GSAP, Framer Motion, or rAF-based animations — must check the preference
  in JS too.
- **Motion tokens without reduced-motion tier**: Building a motion token system that
  doesn't encode the accommodation — leaves implementation to individual component
  authors.
- **Autoplay in workflow screens**: Marketing mindset bleeding into product UI.

---

## Cross-Links

- `lead-motion-designer` (hub) — core principles: accessibility is not optional
- `motion-transitions` — standard transitions that need reduced-motion alternatives
- `motion-choreography` — reduced-motion choreography: preserve timing relationships,
  replace movement with opacity
- `motion-tooling` — Framer Motion `useReducedMotion`, GSAP media query integration
- `fe-accessibility` — implementation of prefers-reduced-motion in component libraries
- `ds-advisor` — motion tokens in the design system
- `a11y-neurodiversity` — cognitive accessibility including motion load
- `a11y-visual` — photosensitivity and WCAG 2.3.1 detail

---

## References

- WCAG 2.1 SC 2.3.1 — Three Flashes or Below Threshold
- WCAG 2.1 SC 2.3.3 — Animation from Interactions (AAA)
- WCAG 2.1 SC 2.2.2 — Pause, Stop, Hide
- Vestibular Disorders Association (vestibular.org)
- A11y Project — Vestibular Disorders & Web Motion
- MDN — prefers-reduced-motion
- Josh Comeau, "Accessible Animations in React" (joshwcomeau.com)
- Framer Motion — useReducedMotion documentation
