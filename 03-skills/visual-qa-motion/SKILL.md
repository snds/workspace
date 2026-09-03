---
name: visual-qa-motion
description: >-
  Motion QA lens — judgment on an animation or transition that already exists, across three
  axes: jank (does it run smoothly), accessibility (is it safe and respectful of user
  preferences), and feel (is the timing, easing, and choreography right). Use when reviewing
  motion rather than building it: "does this animation feel right", "this transition is janky",
  "review the page transition", "is this motion accessible", "the modal animation feels slow",
  "audit the scroll animation", "why does this stutter", "critique this micro-interaction",
  "does this respect reduced motion". Covers frame-budget and compositing failures,
  scroll-linked jank, prefers-reduced-motion coverage, vestibular and flash risk, motion as
  sole feedback, focus behavior during transitions, duration and easing appropriateness,
  weight/inertia, choreography and stagger, interruption and reversal handling, and entrance vs
  exit asymmetry. Spoke of lead-visual-qa. Do NOT use for: implementing or re-targeting an
  animation (the /motion hub and its library skills), authoring motion principles and
  choreography from scratch (motion-principles, motion-choreography), deep runtime performance
  profiling technique (motion-performance), vestibular/neurological policy depth
  (motion-accessibility, a11y-neurodiversity), or page-load performance budgets
  (fe-perf-harness).
aliases: [visual-qa-motion]
triggers: [motion qa, motion review, animation review, animation audit, jank review, janky animation, transition review, reduced motion qa, reduced motion audit, animation feel, motion critique, stutter, dropped frames review]
tier: cross-cutting
domain: quality
hub: lead-visual-qa
related: [motion-performance, motion-accessibility, motion-principles, motion-graphic-systems, motion-programmatic-video, qa]
rigor_role: multi-voice
surfaces: ["*"]
spec_version: "2.2"
---

# Visual QA — Motion

The judgment lens for motion that already runs. Static QA cannot see it: a screenshot has no
timing, no easing, no dropped frames. This lens exists because "the animation feels off" is one
of the most common review comments and one of the least often turned into a specific,
actionable finding.

Three axes, judged in this order — **jank**, then **accessibility**, then **feel**. Smoothness
and safety are pass/fail; feel is craft, and arguing about easing on an animation that drops
frames wastes everyone's time.

## Domain boundary

| Question | Owner |
|---|---|
| Build / re-target this animation in a library | the `/motion` hub → its library skills |
| What should the motion express (direction, brand, art direction) | [[lead-motion-designer]] |
| Principles and choreography from first principles | [[motion-principles]] · [[motion-choreography]] · [[motion-transitions]] |
| How to profile and fix runtime cost in depth | [[motion-performance]] |
| Vestibular / neurological / sensory policy depth | [[motion-accessibility]] · [[a11y-neurodiversity]] |
| Page load speed and weight budgets | [[fe-perf-harness]] |
| Is this existing motion smooth, safe, and right | **this lens** |

## Evidence protocol (motion QA needs a recording)

Do not judge motion from a description or a still. Establish the evidence first and state it in
the report:

1. **Capture the motion** — screen recording at the display's native resolution and a stated
   frame rate; note device, browser, and whether the machine was throttled.
2. **Step it frame by frame** — [[reference-video-review]] extracts frames (`ffmpeg`) so timing
   and easing become measurable instead of remembered.
3. **Trace the runtime** — DevTools Performance panel: frame durations, long tasks, layout and
   paint events, and which properties actually animated. [[motion-performance]] owns the
   technique.
4. **Toggle the preference** — re-run with OS reduce-motion enabled. This is a separate artifact
   and must be reviewed as one.
5. **State the conditions judged** — "60Hz, 4× CPU throttle, Chrome 1440×900 native" is a
   finding's evidence; "felt slow on my laptop" is not.

## Axis 1 — jank (pass/fail)

| Failure | Signal | Verdict |
|---|---|---|
| Animating layout properties (`width`, `height`, `top`, `left`, `margin`) | Layout + paint on every frame in the trace | blocker |
| Animating without compositing where it matters (no `transform`/`opacity` path) | Paint-heavy frames | major |
| Frames over budget (> ~16.7ms at 60Hz; > ~8.3ms at 120Hz) | Long-frame markers in the trace | blocker if visible stutter |
| Layout thrash inside a scroll or rAF handler (read-write-read) | Forced synchronous layout warnings | blocker |
| Scroll-linked animation not on a compositor-friendly path | Jitter or lag behind the finger/wheel | major |
| Animation starting before its assets/fonts land | Visible pop or reflow mid-animation | major |
| Too many simultaneously animating elements | Frame cost scales with element count | major |
| Animation running while off-screen or in a hidden tab | Wasted battery, contributes to jank elsewhere | minor |
| Motion competing with a heavy main-thread task (data fetch, grid render) | Animation freezes then jumps | major |

A dropped-frame problem is a **performance defect**, not a taste question. Report the frame
evidence and hand the fix to [[motion-performance]] / [[fe-performance]].

## Axis 2 — accessibility (pass/fail)

- **`prefers-reduced-motion` coverage is not optional.** Every large-region movement, parallax,
  auto-playing loop, and scroll-hijack needs a reduced variant. Reduced does not mean *removed*:
  keep a cross-fade or an instant state change so causality survives.
- **Vestibular risk** — motion sweeping more than roughly a quarter of the viewport, zooming,
  spinning, or parallax at speed can cause nausea and dizziness. WCAG 2.3.3 is the floor.
- **Flash safety** — nothing may flash more than 3 times per second in a large region (WCAG
  2.3.1, Level A). This includes "clever" loading shimmers and error pulses.
- **Autoplay is stoppable** — any motion lasting more than 5 seconds needs a pause/stop
  affordance (WCAG 2.2.2).
- **Motion is never the only channel** — if a state change is communicated only by movement, it
  does not exist for a user with reduced motion enabled or for anyone who looked away. Pair it
  with text, icon, or color plus one non-color cue.
- **Focus behavior across transitions** — focus must land somewhere sensible when a panel or
  route animates in, must not be lost to an unmounted node, and the focus ring must not be
  clipped or dragged by a transform.
- **Duration under cognitive load** — long or repeated motion in a task the user performs
  dozens of times a day becomes an obstacle. Enterprise power users pay the animation cost
  every time.
- **Announcement timing** — content that animates in and is announced by a live region should
  not be announced twice, and should not be announced before it exists.

## Axis 3 — feel (craft judgment)

Reference durations, not rules. They are starting points for a critique, and the artifact's own
context can justify departures; what a finding must never be is "it feels wrong" with nothing
attached.

| Motion | Typical range | Notes |
|---|---|---|
| Micro-interaction (hover, toggle, checkbox) | 100-200ms | Must feel instantaneous; above ~250ms it feels sluggish |
| Small element (dropdown, tooltip, snackbar) | 150-250ms | Enter slightly slower than exit |
| Medium surface (modal, drawer, panel) | 200-350ms | Larger travel earns more time |
| Full page / route transition | 300-500ms | Beyond ~500ms the user is waiting, not being oriented |
| Attention-directing (highlight, count-up) | 400-800ms | Only for something that genuinely deserves the interruption |

What to judge:

- **Easing intent** — `ease-out` for entrances (fast in, settle), `ease-in` for exits, spring
  or overshoot only where physicality is the point. Linear reads mechanical except for
  continuous motion (spinners, marquees). Symmetric `ease-in-out` on a UI entrance is the most
  common mistake.
- **Weight and inertia** — a large surface that moves like a small one feels weightless; a
  small control with heavy easing feels sticky. Mass should be consistent across the product.
- **Choreography** — related elements move as a group, unrelated ones don't; stagger is small
  (~20-50ms) and serves reading order rather than showing off. Everything moving at once reads
  as chaos; everything moving in sequence reads as slow.
- **Continuity and orientation** — the element that persists across a transition should be
  traceable (shared-element continuity). Motion should tell the user where they came from and
  where things went, not merely decorate the change.
- **Interruption and reversal** — a control clicked twice quickly, a hover that leaves
  mid-animation, a drawer dismissed while opening: motion should reverse or retarget from its
  current position, never snap or queue.
- **Settle** — no residual bounce on functional UI, no visible sub-pixel drift at the end, no
  1px jump when a transform resolves to a layout position.
- **Entrance vs exit asymmetry** — exits are usually faster; a slow exit makes the product feel
  like it is arguing with the user.
- **Purpose** — every animation should answer "what does this help the user understand?" Motion
  that only announces its own presence is the finding.

## QA checklist — motion

**Jank**
- [ ] Only compositor-friendly properties animate on the hot path
- [ ] Frame trace shows no long frames during the animation
- [ ] No forced synchronous layout inside scroll / rAF handlers
- [ ] Scroll-linked motion tracks input without lag
- [ ] Off-screen and hidden-tab animation is paused

**Accessibility**
- [ ] Every large-region motion has a reduced-motion variant (and was tested with it on)
- [ ] No large-area zoom/spin/parallax without an alternative
- [ ] Nothing flashes more than 3×/second
- [ ] Motion over 5s can be paused or stopped
- [ ] No state communicated by motion alone
- [ ] Focus lands correctly and stays visible through the transition

**Feel**
- [ ] Durations are in a defensible range for the surface size
- [ ] Easing matches direction (out for entrance, in for exit)
- [ ] Weight is consistent with the element's size and the product's language
- [ ] Stagger serves reading order; groups move together
- [ ] Interruption reverses/retargets rather than snapping or queueing
- [ ] Motion settles cleanly with no residual drift or 1px jump
- [ ] Each animation has a stated purpose
- [ ] Register named (product chrome vs graphic system vs diegetic). Idle loops
      belong only where "live instrument" is the job ([[motion-graphic-systems]])

## Report shape

Return the shared `/qa` format, with the evidence field carrying real measurements (frame
times, dropped-frame count, measured duration in ms from frame stepping, reduced-motion
coverage). Route fixes: jank to [[motion-performance]] / [[fe-performance]], reduced-motion and
vestibular work to [[motion-accessibility]], timing and choreography values to
[[motion-principles]] / [[motion-choreography]], and the implementation itself to the `/motion`
hub's library skills.

## Related
- hub → [[lead-visual-qa]]
- peer ↔ [[motion-performance]] · [[motion-accessibility]] · [[qa]]
- peer ↔ [[motion-graphic-systems]]
- peer ↔ [[motion-programmatic-video]]
