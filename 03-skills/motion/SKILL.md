---
name: motion
description: >-
  Motion IMPLEMENTATION hub — turning motion intent into working library code (GSAP,
  Three.js/R3F, Motion / motion.dev, anime.js, Lottie, Rive, SVG native, Remotion,
  scroll/parallax, WebGL/3D). Use when the user wants to *build* an animation or
  effect: "implement this scroll animation", "build a heat-haze shader", "wire up
  GSAP ScrollTrigger", "make this with Motion / Framer Motion", "add a Lottie",
  "Rive state machine", "parallax with Locomotive", "R3F particle field",
  "animate this SVG mask", "draw this path", "Remotion title card". Also the
  explicit entry point for the `/motion` operation grammar
  (`/motion <verb> <target> [--modifiers]`). Canonical owner of motion *code* routing:
  it wraps the claude-design-skillstack libraries and selects the right one for the job.
  Not for motion *principles/feel* (easing choice, timing, the 12 principles — use the
  motion-* workspace skills, e.g. motion-principles/motion-choreography/motion-graphic-systems), and not for
  *judging* an existing animation (use /qa). Direction lives in the lead/principles
  skills; this hub is the implementation surface.
user-invocable: true
argument-hint: "[generate|adapt|audit|polish] [target: effect-name|component|url|page] [--lib vgpu|gsap|r3f|threejs|framer|anime|lottie|rive|pixi|locomotive|barba] [--perf] [--dry]"
license: Apache-2.0
metadata:
  hub: true
  family: motion-implementation
  poc: false
  version: 0.1.0
aliases: [motion]
spec_version: "2.0"
tier: hub
domain: design
prerequisites: [design-foundations]
---

# /motion — Motion Implementation Hub

The implementation surface for motion. The `motion-*` workspace skills hold the *theory*
(easing, the 12 principles, choreography, performance budgets); the `lead-motion-designer`
holds *direction*; this hub turns either into **working code** by routing to the right
`claude-design-skillstack` library. It is a **wrapper** (three-way-contract wrapper layer):
it owns trigger vocabulary, verb dispatch, and library selection, then delegates the depth
to the base library skills. It never duplicates a library's knowledge.

## Operation grammar

```
/motion <verb> <target> [--modifiers]
```

- **verb** — a canonical Produce/Transform/Inspect verb (below). Omitted → `generate`.
- **target** — an effect name, a component/path, a URL, or `page`.
- **modifiers** — `--lib` (force a library), `--perf` (performance lens), `--dry`.

Conversational invocation maps in: "build a heat-haze shader in three.js" →
`/motion generate heat-haze --lib threejs`.

### Verbs (hub subset)

| Verb | Meaning here | Default base route |
|---|---|---|
| `generate` | Scaffold the working animation/effect in the chosen library | the matched skillstack library skill |
| `adapt` | Re-target an existing effect to another library, breakpoint, or reduced-motion | source lib skill + `motion-accessibility` |
| `audit` | Evaluate an implementation — frame budget, layout thrash, GPU cost, `prefers-reduced-motion` | `motion-performance` + the lib skill (`--perf` implied) |
| `polish` | Refine timing/feel without changing intent (easing, stagger, settle) | `motion-principles` / `motion-choreography` for the *values*, lib skill for the code |

### Library routing (`--lib`, else inferred from the target)

| Need | Library skill (base) |
|---|---|
| Scroll-driven timelines, pin/scrub | `gsap-scrolltrigger` |
| New web GPU / WGSL / canvas shader | [[vgpu-webgpu]] (`--lib vgpu`) |
| React 3D scenes (existing R3F/Three) | `react-three-fiber` (+ `threejs-webgl`, `threejs-materials-master`, `threejs-vfx-atmosphere`) |
| Raw WebGL / GLSL on a Three tree | `threejs-webgl` · `glsl-shader-architect` |
| React / JS / Vue UI motion (motion.dev) | `motion-framer` · `react-spring-physics` — import `motion/react` |
| Lightweight UI tweens | `animejs` · `animated-component-libraries` |
| Native SVG (mask, clip, stroke draw, morph) | `animejs` / GSAP (`--lib gsap`) after [[motion-graphic-systems]] names the technique |
| Vector / designer-authored | `lottie-animations` · `rive-interactive` |
| Programmatic video / kinetic title cards | [[motion-programmatic-video]] then Remotion / Motion Canvas / Manim |
| Page transitions / smooth scroll | `barba-js` · `locomotive-scroll` |
| 2D canvas / particles | `pixijs-2d` · `lightweight-3d-effects` |
| Live multi-engine demo canvas / WebXR in-world chat | [[web-3d-extensions]] (`maige-3d-mcp`) — not a ship lib |
| Engines / XR (product) | `playcanvas-engine` · `babylonjs-engine` · `aframe-webxr` |
| Authoring → web pipeline | `spline-interactive` · `blender-web-pipeline` · `substance-3d-texturing` |
| Cross-cutting integration | `web3d-integration-patterns` · `modern-web-design` · `scroll-reveal-libraries` |

## Disambiguation — who owns what (the precision contract)

`/motion` is the canonical owner of **motion code**. Defer when a request crosses the line:

- **Motion *feel/principles*** (which easing, how long, why it feels wrong, the 12 principles) → `motion-principles` / `motion-choreography` / `motion-transitions` (workspace theory skills). Graphic-system / SVG / film-UI register → `motion-graphic-systems`. Video / title-card register → `motion-programmatic-video`. This hub *consumes* their values.
- **Motion *direction*** (art direction, what the motion should express) → `lead-motion-designer` / `lead-art-director`. On a Legion topic the project + art-direction skills load organically; then drop here for the build.
- **Judging an existing animation** (is it janky, accessible, on-brand) → `/qa` (`--lens ui`/`a11y`, with `motion-performance` measurement). MotionScore is an optional extra grade, not the verdict.
- **Generative redesign / live in-browser variant iteration** → `/redesign` / `impeccable`.
- **Motion AI Kit** ([motion.dev](https://motion.dev/docs/ai-kit)) also ships a `/motion` skill and MCP (docs search, `linear()` springs, MotionScore). **This wrapper wins.** Use the kit for live API/docs and spring generation after this hub has named the library and the theory spokes have named the values. Never let the kit waive frequency gates, reduced-motion, or compositor bans.

Organic for *direction and feel*, explicit `/motion` for the *discrete build*.

## Shared report format

For `audit`, return the cross-hub shape (findings · severity · fix · owner · summary · next),
with measured values (frame time, dropped frames, reflow count, reduced-motion coverage).
For `generate`/`adapt`, return: what was built, in which library + version, the integration
points, and a perf/reduced-motion note.

## Execution protocol

1. **Parse** verb/target/modifiers; default `generate`; resolve `--lib` (inferred from the target if absent).
2. **Pull direction/feel** from the relevant `motion-*` theory skill when the request implies a quality bar (easing, stagger, choreography).
3. **`--dry`?** Report the chosen library + plan and stop.
4. **Load the matched skillstack library skill** (it carries the version check + API depth).
5. **Generate/adapt/audit** in that library. Respect `prefers-reduced-motion` and a frame budget by default.
6. **Emit** the report.
7. **Hand off**: judging → `/qa`; live in-browser iteration → `/redesign`/impeccable.

## POC scope note

Sibling to `/qa`, cloned from the same wrapper shape per `invokable-operations-spec_v0.2`;
it is the Phase-E plugin wrapper over `claude-design-skillstack`. Thin by design — the
library skills hold the depth, the `motion-*` skills hold the theory.

## Related
- foundation → [[design-foundations]]
- peer ↔ [[motion-programmatic-video]] · [[vgpu-webgpu]] · [[web-3d-extensions]]
