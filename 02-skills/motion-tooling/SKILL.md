---
name: motion-tooling
description: >
  Animation library selection and usage — GSAP, Framer Motion, Lottie, CSS
  animations, Web Animations API. Use this skill whenever the conversation touches:
  choosing an animation library, GSAP timeline syntax, GSAP ScrollTrigger, GSAP
  Flip plugin, Framer Motion motion components, AnimatePresence, Framer Motion
  variants, Framer Motion layout prop, Framer Motion gestures, Lottie JSON format,
  dotLottie, Lottie optimization, After Effects Bodymovin export, CSS transition
  vs CSS animation vs WAAPI, requestAnimationFrame patterns, or any question about
  implementing animation in code.
aliases: [motion-tooling]
tier: spoke
domain: design
hub: lead-motion-designer
prerequisites: [lead-motion-designer]
spec_version: "2.0"
---

# Motion Tooling

Specialist lens for animation library selection, configuration, and usage in
digital interfaces. Part of the lead-motion-designer skill network.

---

## Domain Boundary

This skill owns **which tool to use and how to use it** for animation implementation.

- **Performance characteristics of the chosen approach** → `motion-performance`
- **Which animation to implement** → `motion-transitions` or `motion-choreography`
- **Why the animation feels wrong** → `motion-principles`
- **Accessibility: reduced-motion alternatives in each library** → `motion-accessibility`

---

## Choosing the Right Tool

The single most important question before reaching for a library: **Do I need one?**

CSS animations and the Web Animations API handle the majority of interface
animation needs. Libraries add weight, complexity, and dependencies. Use a
library when native capabilities are genuinely insufficient.

### Decision Matrix

| Need | Tool |
|------|------|
| Simple state-driven transitions (hover, focus, class toggle) | CSS Transitions |
| Looping or multi-step declarative animation | CSS Keyframes |
| Programmatic control with CSS-level performance, no library | Web Animations API |
| Complex React choreography, layout animation, gestures | Framer Motion |
| Complex sequencing, ScrollTrigger, SVG morphing, non-React | GSAP |
| Illustrative / brand animation from After Effects | Lottie |
| Marketing site with heavy scroll narrative | GSAP + ScrollTrigger |
| Drag physics, spring interactions in React | Framer Motion |
| Very lightweight, no library budget | CSS + WAAPI |

---

## CSS Transitions

The simplest and often best tool for state-driven animation.

```css
.button {
  background-color: var(--color-primary);
  transform: scale(1);
  /* Always specify easing and duration explicitly */
  transition: background-color 150ms ease-out,
              transform 100ms ease-out;
}

.button:hover {
  background-color: var(--color-primary-hover);
  transform: scale(1.02);
}

.button:active {
  transform: scale(0.97);
  transition-duration: 75ms;  /* Active state is faster — immediate feedback */
}
```

### Best For
- Hover/focus/active state changes
- Simple show/hide (with `opacity` and `visibility` or `display` workarounds)
- Color, shadow, border-radius changes
- Any two-state transition driven by class or attribute changes

### Limitations
- No sequencing (elements can't wait for each other)
- No programmatic pause/reverse/control
- No physics/spring
- Hard to handle appear/disappear gracefully (display: none issue)

### The display: none Problem

```css
/* Problem: transition doesn't work from display: none */
.panel { display: none; opacity: 0; }
.panel.open { display: block; opacity: 1; } /* snaps open */

/* Solution 1: visibility + opacity */
.panel {
  visibility: hidden;
  opacity: 0;
  transition: opacity 200ms ease-out, visibility 0s 200ms; /* visibility delay = duration */
}
.panel.open {
  visibility: visible;
  opacity: 1;
  transition: opacity 200ms ease-out, visibility 0s; /* no delay on open */
}

/* Solution 2: @starting-style (Chrome 117+, Firefox 129+) */
.panel { opacity: 1; transition: opacity 200ms ease-out; display: block; }
@starting-style { .panel { opacity: 0; } }
```

---

## CSS Keyframe Animations

Multi-step and looping animations defined declaratively.

```css
@keyframes skeleton-pulse {
  0%   { opacity: 1; }
  50%  { opacity: 0.5; }
  100% { opacity: 1; }
}

.skeleton {
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

/* Respect reduced-motion */
@media (prefers-reduced-motion: reduce) {
  .skeleton { animation: none; }
}
```

### Best For
- Loading/skeleton shimmer animations
- Looping indicators (spinners)
- Entrance animations applied once via class addition
- Declarative multi-step sequences

### Limitations
- No fine-grained JS control
- Awkward to sequence with other animations (manual delay calculation)
- No physics

---

## Web Animations API (WAAPI)

The native browser programmatic animation API. The best choice when you need
JS control without a library.

### Basic Usage

```javascript
const animation = element.animate(
  [
    { transform: 'translateY(16px)', opacity: 0 },
    { transform: 'translateY(0)',    opacity: 1 }
  ],
  {
    duration: 250,
    easing: 'cubic-bezier(0, 0, 0.2, 1)',
    fill: 'forwards',   // keeps end state; use 'none' + explicit CSS for cleaner state
    delay: 0
  }
);

// Control
animation.pause();
animation.play();
animation.reverse();
animation.cancel();

// Wait for completion
await animation.finished;
```

### KeyframeEffect for Reuse

```javascript
const enterEffect = new KeyframeEffect(
  null,  // null target for reuse
  [
    { opacity: 0, transform: 'translateY(8px)' },
    { opacity: 1, transform: 'translateY(0)' }
  ],
  { duration: 200, easing: 'ease-out', fill: 'forwards' }
);

// Apply to specific element
const effect = new KeyframeEffect(element, enterEffect);
new Animation(effect, document.timeline).play();
```

### Best For
- Programmatic animation without a React dependency
- Sequences in vanilla JS apps
- When you want CSS-level performance with full JS control
- Stagger implementations in vanilla JS

### Limitations
- No built-in spring physics
- No timeline sequencing (use promises/await chains)
- No automatic FLIP
- Spring requires a polyfill or manual implementation

---

## GSAP (GreenSock Animation Platform)

The industry standard for complex, sequenced, non-trivial animation outside
React-component contexts.

### Core Concepts

```javascript
import gsap from 'gsap';

// Basic tweens
gsap.to(element, { x: 100, opacity: 1, duration: 0.3, ease: 'power2.out' });
gsap.from(element, { y: 20, opacity: 0, duration: 0.25 });
gsap.fromTo(element,
  { x: -50, opacity: 0 },
  { x: 0,   opacity: 1, duration: 0.3, ease: 'power2.out' }
);
```

### Timeline — The Power Feature

```javascript
const tl = gsap.timeline({ defaults: { ease: 'power2.out', duration: 0.3 } });

tl
  .from('.header', { y: -20, opacity: 0 })
  .from('.nav-items', { y: -10, opacity: 0, stagger: 0.05 }, '-=0.15')  // 0.15s overlap
  .from('.hero-text', { y: 30, opacity: 0 }, '-=0.1')
  .from('.cta-button', { scale: 0.9, opacity: 0 }, '<+=0.1');  // relative to previous start
```

**Position parameter syntax**:
- `'>='` — after previous animation ends (default)
- `'<'` — at start of previous animation (overlap = start-sync)
- `'-=0.15'` — 0.15s before previous animation ends (overlap)
- `'+=0.1'` — 0.1s after previous animation ends (gap)
- `'label'` — at a named label
- `0.5` — at absolute time 0.5s in the timeline

### Easing Library

```javascript
// GSAP ease naming
ease: 'power1.out'   // gentle ease-out
ease: 'power2.out'   // moderate ease-out (good default)
ease: 'power3.out'   // strong ease-out
ease: 'power4.out'   // very strong ease-out
ease: 'back.out(1.4)'  // overshoot — 1.4 is the back amount
ease: 'elastic.out(1, 0.3)'  // spring-like oscillation
ease: 'expo.out'     // exponential — very fast start, long tail
ease: 'circ.out'     // circular — smooth, professional
ease: 'none'         // linear
```

### ScrollTrigger

The definitive scroll-linked animation plugin.

```javascript
import ScrollTrigger from 'gsap/ScrollTrigger';
gsap.registerPlugin(ScrollTrigger);

gsap.from('.section', {
  scrollTrigger: {
    trigger: '.section',
    start: 'top 80%',     // when section's top hits 80% down the viewport
    end: 'bottom 20%',
    toggleActions: 'play none none reverse', // enter, leave, re-enter, re-leave
    // scrub: true,         // tie animation progress to scroll position (smooth)
    // pin: true,           // pin trigger element during animation
    markers: false,         // development only — shows trigger points
  },
  y: 40,
  opacity: 0,
  duration: 0.4
});
```

`toggleActions` options: `'play'`, `'pause'`, `'resume'`, `'reset'`, `'restart'`,
`'complete'`, `'reverse'`, `'none'`

### GSAP Flip Plugin

```javascript
import Flip from 'gsap/Flip';
gsap.registerPlugin(Flip);

// Capture state before DOM change
const state = Flip.getState('.animated-elements');

// Make DOM changes
grid.classList.toggle('expanded');

// Animate from captured state to new state
Flip.from(state, {
  duration: 0.4,
  ease: 'power1.inOut',
  stagger: 0.04
});
```

### MorphSVG / DrawSVG (Club GreenSock)

```javascript
// SVG path morphing — source and target must have same number of points,
// or MorphSVG handles the conversion automatically
gsap.to('#source-path', { morphSVG: '#target-path', duration: 0.5 });

// Stroke drawing animation
gsap.from('#checkmark', { drawSVG: '0%', duration: 0.4, ease: 'power2.out' });
```

### License

- Core GSAP + ScrollTrigger + Flip: free (all use cases including commercial)
- MorphSVG, DrawSVG, SplitText, etc.: Club GreenSock license required for commercial use

### Best For
- Complex multi-element choreography (marketing, onboarding, splash)
- Scroll-linked animation
- SVG animation
- Non-React or framework-agnostic projects
- Any project needing a timeline-based animation system

---

## Framer Motion (React)

The canonical React animation library — designed for React's component model
with excellent layout animation and gesture support.

### Basic Motion Components

```jsx
import { motion, AnimatePresence } from 'framer-motion';

// Entrance / state animation
<motion.div
  initial={{ opacity: 0, y: 16 }}
  animate={{ opacity: 1, y: 0 }}
  exit={{ opacity: 0, y: -8 }}
  transition={{ duration: 0.25, ease: [0, 0, 0.2, 1] }}
>
  Content
</motion.div>
```

### AnimatePresence — Unmount Animation

```jsx
import { AnimatePresence, motion } from 'framer-motion';

<AnimatePresence>
  {isVisible && (
    <motion.div
      key="panel"
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.96 }}
      transition={{ duration: 0.2 }}
    >
      Panel content
    </motion.div>
  )}
</AnimatePresence>
```

Without `AnimatePresence`, `exit` animations don't run — the element unmounts
immediately. `AnimatePresence` keeps the element in the DOM until its exit
animation completes.

### Variants — Shared Animation State

```jsx
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1
    }
  }
};

const itemVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0 }
};

<motion.ul variants={containerVariants} initial="hidden" animate="visible">
  {items.map(item => (
    <motion.li key={item.id} variants={itemVariants}>
      {item.label}
    </motion.li>
  ))}
</motion.ul>
```

Variants propagate down the component tree automatically — child components
animate when the parent's variant state changes.

### Layout Animations — The Killer Feature

```jsx
// Automatic FLIP animation for layout changes
<motion.div layout>
  {expanded && <ExpandedContent />}
</motion.div>

// List reordering — every item with layout prop animates to its new position
{items.map(item => (
  <motion.div key={item.id} layout>
    {item.label}
  </motion.div>
))}

// Shared layout between different components (e.g., list item → detail view)
<motion.div layoutId="hero-image">
  <img src={image} />
</motion.div>
```

`layout` uses FLIP internally. `layoutId` connects elements across mounts/unmounts
for shared element transitions.

### Gestures

```jsx
<motion.div
  drag="x"
  dragConstraints={{ left: -100, right: 100 }}
  dragElastic={0.2}
  whileHover={{ scale: 1.02 }}
  whileTap={{ scale: 0.97 }}
  whileDrag={{ cursor: 'grabbing' }}
>
  Draggable item
</motion.div>
```

### useReducedMotion

```jsx
import { useReducedMotion } from 'framer-motion';

function AnimatedPanel() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <motion.div
      initial={{ opacity: 0, y: shouldReduceMotion ? 0 : 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0 }}
    >
      Content
    </motion.div>
  );
}
```

### Spring Transition

```jsx
<motion.div
  animate={{ x: 100 }}
  transition={{
    type: 'spring',
    stiffness: 300,   // spring constant — higher = stiffer, faster
    damping: 30,      // friction — higher = less overshoot
    mass: 1           // simulated mass — higher = slower response
  }}
/>
```

### Performance Notes

- `layout` prop on large lists recalculates all sibling positions — expensive
  on lists > 50 items; consider virtualization
- Motion values (`useMotionValue`, `useTransform`) enable performant scroll-linked
  animations without re-renders
- `MotionConfig` can set global defaults and reduced-motion behavior at the app level

---

## Lottie

Lottie plays JSON animations exported from After Effects or vector animation tools.
The format encodes vector animation data; the Lottie runtime renders it on a
canvas or SVG element.

### When to Use Lottie

| Good use | Poor use |
|----------|---------|
| Complex illustrative animations | Real-time interactive animation |
| Brand / marketing animations | Frequently triggered UI animations |
| Onboarding sequences | Animations that need to respond to gestures |
| Achievement / celebration moments | High-frequency microinteractions |

### File Format

- **JSON (classic)**: Verbose, large files. Still the most compatible format.
- **dotLottie (.lottie)**: Binary container format. 2–10× smaller. Preferred.

### Optimization

1. Reduce layer count in After Effects before export
2. Remove unused layers and compositions
3. Avoid blending modes (multiply, screen) — expensive to render
4. Avoid rasterized layers (use vector throughout)
5. Use LottieFiles optimizer or lottiegen tool
6. Consider using dotLottie for production

### React Implementation

```jsx
import Lottie from 'lottie-react';
import animationData from './animation.json';

<Lottie
  animationData={animationData}
  loop={false}
  autoplay={true}
  style={{ width: 200, height: 200 }}
/>
```

### Reduced Motion with Lottie

```jsx
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

<Lottie
  animationData={animationData}
  autoplay={!prefersReducedMotion}
  loop={!prefersReducedMotion}
  // Under reduced-motion: show first frame statically
/>
```

### After Effects → Lottie Workflow

1. Design animation in After Effects using vector layers
2. Export via Bodymovin (AE plugin) or LottieFiles plugin
3. Preview and validate at lottiefiles.com
4. Optimize with LottieFiles optimizer
5. Convert to dotLottie format for production

---

## Failure Modes

- **Adding GSAP or Framer Motion for a hover transition**: Two lines of CSS
  transition would have done the same thing with zero dependency cost
- **Lottie for interactive UI animation**: The Lottie runtime runs ahead of
  any user interaction; it can't respond to gestures or dynamic state
- **Framer Motion `layout` on a virtualized list**: FLIP calculations on
  all sibling elements; defeats the purpose of virtualization
- **GSAP for a React app without careful integration**: GSAP manipulates the
  DOM directly; React reconciliation can conflict; use refs properly
- **Missing AnimatePresence**: Exit animations silently don't run; common
  debugging trap for Framer Motion newcomers
- **Lottie files that weren't optimized**: A 2MB Lottie file for a 50px icon
  micro-interaction; runtime rendering cost that exceeds CSS equivalent

---

## Cross-Links

- `motion-performance` — performance characteristics of each tool; compositor
  layer promotion; when each library triggers layout
- `motion-choreography` — GSAP timeline as the implementation layer for
  choreography sequences; Framer Motion variants for React choreography
- `motion-accessibility` — `useReducedMotion` hook; per-library reduced-motion
  patterns
- `fe-component-architecture` — React integration patterns for Framer Motion;
  GSAP ref management in components

---

## References

- GSAP documentation (greensock.com/docs)
- GSAP ScrollTrigger documentation
- Framer Motion documentation (framer.com/motion)
- Lottie documentation (airbnb.io/lottie)
- LottieFiles (lottiefiles.com) — preview, optimize, share
- Web Animations API — MDN documentation
- dotLottie specification (dotlottie.io)
