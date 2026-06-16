---
name: lead-visual-qa
description: >
  Visual quality assurance lead with broad cross-domain expertise. Use this
  skill whenever the conversation involves: reviewing screenshots, video
  playback, interactive visuals, generated outputs, developed UI, rendered
  scenes, or any visual artifact against a reference, standard, or intent.
  Trigger on: "does this look right", visual review, visual audit, visual
  polish, comparing output to reference, checking against brand or style
  guidelines, spotting visual artifacts, reviewing weight/color/spacing/
  proportion/balance, evaluating aesthetic fidelity, determining if a scene
  "reads" correctly, checking if a UI feels polished, reviewing typography
  hierarchy, assessing visual harmony, reviewing animation or motion quality,
  flagging visual regressions, or any situation where an expectation has been
  set and the output needs to be evaluated against it. Also trigger when other
  skills produce visual output (icons, 3D renders, UI components, game assets,
  architectural renders, generated imagery) as a natural final-step review.
  Hub skill — routes to visual-qa-graphic-design, visual-qa-ux-design,
  visual-qa-ui-design, visual-qa-accessibility, visual-qa-usability,
  visual-qa-game-design, visual-qa-architecture, visual-qa-interior-design.
---

# Lead Visual QA

Cross-domain visual quality assurance lead. This skill evaluates whether
visual output achieves its intent — not whether it is a literal copy of a
reference, but whether the right *delta* exists between the output and the
expectation set by reference material, best practices, design standards,
or stated artistic intent.

---

## The Fidelity Contract

Before any evaluation begins, the fidelity contract must be established.
It defines *how close is close enough* and shapes what counts as a defect.

| Contract Type | Definition | Examples |
|---------------|------------|---------|
| **Literal** | Output must reproduce the reference with maximum fidelity within the technical constraints of the medium | Brand asset pixel-faithful rendering, production-ready comp matching an approved design, font glyph matching source SVG |
| **Spirit** | Output should capture the aesthetic intent, feel, and language of the reference without being a copy | Scene inspired by a style reference, generated image in the style of a mood board, design system components that embody a brand without being templates |
| **Standard** | Output should conform to established professional conventions for the domain without a specific reference | Accessible color contrast, WCAG-compliant UI, typographically sound layout, architecturally plausible structure |
| **Intent** | Output should serve the stated purpose effectively — evaluated by functional outcome, not visual closeness | Icon legibility at target size, wayfinding clarity in a space, game HUD readability under play conditions |

These contracts are not mutually exclusive and often stack. A UI component
might need to satisfy **literal** (matches the approved comp), **standard**
(WCAG AA contrast), and **intent** (users can complete the action) simultaneously.

---

## Delta Analysis Framework

The evaluation model. Apply this structure to every visual review.

### 1. Establish Context
- What is being evaluated (type of artifact, medium, output pipeline)?
- What fidelity contract applies?
- What reference material exists (comps, mood boards, style guides, prior art, standards docs)?
- What was the stated intent or goal?

### 2. Identify Evaluation Dimensions
Select from the dimensions below based on artifact type and fidelity contract.

| Dimension | What to Evaluate |
|-----------|-----------------|
| **Composition** | Visual weight distribution, balance (symmetric/asymmetric/radial), negative space, focal hierarchy |
| **Proportion & Scale** | Object-to-object ratios, scale relative to context, spatial relationships |
| **Color** | Palette adherence, value contrast, saturation levels, color temperature consistency, color harmony vs reference |
| **Typography** | Hierarchy, weight/style/size relationships, tracking, leading, alignment, legibility |
| **Spacing & Rhythm** | Padding, margin, grid alignment, visual cadence, density |
| **Form & Geometry** | Shape accuracy, optical corrections (overshoot, weight compensation), curve quality |
| **Texture & Material** | Surface accuracy, PBR correctness, pattern fidelity, material reads at target viewing distance |
| **Lighting** | Direction consistency, intensity, shadow softness, ambient vs direct balance, mood |
| **Motion** | Timing, easing, weight, anticipation/follow-through, arc quality |
| **Coherence** | Internal consistency — does the artifact read as a unified whole? |
| **Context Fit** | Does the output fit within its intended environment (app context, scene context, print context)? |

### 3. Score the Delta

For each dimension with a deviation:

| Severity | Definition |
|----------|-----------|
| **Critical** | The artifact fails its primary purpose or is visually broken — a reasonable viewer would immediately notice something is wrong |
| **Major** | Meaningfully below expectation in a prominent dimension — affects quality perception but artifact is still functional |
| **Minor** | Subtle deviation — visible on close inspection, affects craftsmanship rating but not general impression |
| **Cosmetic** | Polish-level variation — imperceptible at standard viewing, only detectable under production QA scrutiny |

### 4. Prioritize and Report

Structure findings as:
- **What** is wrong (describe precisely, with location reference if applicable)
- **Why** it's wrong relative to the fidelity contract
- **How severe** (Critical / Major / Minor / Cosmetic)
- **What to do** (specific remediation recommendation)

Cluster findings by dimension and severity, not by location, unless a single
region of the artifact has multiple co-located issues.

---

## Reading Visual Output

### Optical vs Geometric Correctness

Many visual "errors" are correct by measurement but wrong to the eye. Conversely,
some things that measure incorrectly look perfectly right. **The eye is the
primary validator.** Rules and measurements are guides.

- **Optical center** sits slightly above geometric center — a rectangle with
  content centered at the exact midpoint looks bottom-heavy
- **Equal-weight strokes** look uneven when one is horizontal and one diagonal
  (diagonal appears thinner — compensate by making it heavier)
- **Adjacent pure colors** at full saturation vibrate — the eye reads this as
  poor quality even though the colors are technically "correct"
- **Symmetric designs** often need deliberate asymmetric adjustments to feel
  balanced due to the optical weight of specific shapes

### Visual Balance Vocabulary

When reporting balance issues, use precise language:

- **Top-heavy**: Visual mass sits above optical center
- **Left-justified**: Visual weight pulls to the left in a layout that reads as centered
- **Color dominant**: One element commands disproportionate attention due to color
- **Typographic tension**: Type and image/shape are competing for hierarchy rather than cooperating
- **Orphaned element**: An isolated item that lacks visual relationship with its neighbors
- **Dead zone**: Region that contributes no visual information but consumes canvas space
- **Crowded corner**: Too much detail compressed into one quadrant of the composition

### Reference Material Analysis

When evaluating against reference material:

1. **Look at the reference first, before the output** — establish the mental model independently
2. **Identify the defining characteristics** of the reference that are non-negotiable (what makes it feel like itself)
3. **Identify the adaptable characteristics** (secondary traits that may reasonably vary)
4. **Overlay mentally or side-by-side** — notice what registers first as "different"
5. **Describe the delta in experiential terms first** ("it feels heavier / colder / less refined") before translating to technical terms ("higher saturation / cooler color temperature / tighter letter spacing")

---

## Measurement Companion: `visual-qa-toolkit`

This skill's evaluation is primarily heuristic — fidelity contracts, delta
analysis, experiential-then-technical descriptions. For dimensions that can
be *measured* rather than *asserted*, there is a complementary measurement
skill: **`visual-qa-toolkit`**. It runs instrumented Python scripts against
screenshots and produces structured findings with annotated images.

Use the toolkit when delta analysis surfaces dimensions that warrant verification
with numbers instead of claims:

| Dimension (from Delta Analysis) | Measurable via `visual-qa-toolkit` |
|---|---|
| Composition / balance | `alignment` (edge clustering), `spacing` (gap distribution) |
| Color — palette adherence | `color_extraction` (Δe against a palette JSON) |
| Color — contrast / accessibility | `contrast` (WCAG AA/AAA) |
| Color — CVD information loss | `color_vision` (deutan/protan/tritan simulation) |
| Typography — scale adherence | `typography` (cap-height vs. type scale) |
| Spacing & Rhythm | `spacing` (gap vs. scale), `grid_overlay` (visualization) |
| Form & Geometry — icon sets | `icon_consistency` (bbox, weight, stroke outliers) |
| State coherence / differentiation | `state_comparison` (pairwise SSIM between states) |
| Coherence vs. reference | `visual_diff` (SSIM + pixel diff) |

### When to invoke the toolkit

- After heuristic evaluation identifies a dimension where a measurement would
  be more credible than an assertion ("I think the contrast is low" → run
  `contrast` and report the actual ratio).
- For pre-handoff or pre-release audits where evidence matters more than
  impression.
- For accessibility pre-checks where WCAG thresholds are non-negotiable.
- For visual regression comparisons where design-export vs. implementation
  drift needs to be quantified.

### When *not* to invoke the toolkit

- For perceptual off-ness that isn't geometric — the bookmark-icon case where
  a mathematically centered glyph reads as visually off. Heuristic evaluation
  is the right tool here.
- For motion and interaction feel — the toolkit evaluates static images.
- For experiential judgments (does it feel considered / awkward / confident).
  Those stay with this skill.

### Toolkit invocation is input-driven

The toolkit is project-agnostic. It accepts paths: screenshot, folder (icon set
or state set), reference image, palette JSON, config file. It has no knowledge
of specific projects or design systems — configs carry all project context.
Always ask the user for the relevant paths; never hunt the filesystem for
project-specific artifacts.

See `visual-qa-toolkit/SKILL.md` for full invocation details, per-check inputs,
config structure, and output conventions.

---

## Spoke Routing Table

| Spoke Skill | Domain | Route When |
|-------------|--------|-----------|
| `visual-qa-graphic-design` | Typography, layout, branding | Evaluating print collateral, brand assets, editorial design, logos, posters, motion graphics identity |
| `visual-qa-ux-design` | User flows, information architecture, experience | Reviewing wireframes, prototypes, user journeys, navigation patterns, information hierarchy at experience level |
| `visual-qa-ui-design` | Components, screens, design systems | Evaluating screen designs, component libraries, spacing/alignment, platform convention compliance, interactive states |
| `visual-qa-accessibility` | Contrast, target size, cognitive load | Any evaluation touching inclusion, WCAG compliance, readable typography for all users, sensory/motor accessibility |
| `visual-qa-usability` | Task completion, learnability, error prevention | Reviewing whether a visual design enables users to accomplish their goals efficiently and without frustration |
| `visual-qa-game-design` | Art style, HUD, level readability, game feel | Evaluating game UI, in-world visuals, level art composition, animation, visual feedback for game mechanics |
| `visual-qa-architecture` | Scale, proportion, material, site context | Reviewing architectural renders, exterior/structural visualizations, building proportions, material accuracy |
| `visual-qa-interior-design` | Space, furnishing, lighting, material, style | Reviewing interior renders, space planning, finish accuracy, lighting simulation, furniture proportion |

### Multi-spoke escalation

When an artifact spans multiple domains:
1. Apply the hub's general review first to establish the critical/major findings
2. Route to the most relevant single spoke for deep-dive if findings cluster
3. Route to multiple spokes sequentially if the artifact is genuinely multi-domain (e.g., a game UI that needs both `visual-qa-ui-design` and `visual-qa-game-design`)

---

## Cross-skill Auto-link Protocol

This skill is a natural final-step reviewer for visual output produced by:

- `lead-icon-artist` → review completed icons and set consistency
- `lead-vector-designer` → review path quality and optical correctness of vector output
- `variable-icon-font-architect` → review generated weight masters for visual artifacts
- `lead-art-director` → review rendered output against artistic direction references
- `lead-technical-digital-artist` → review pipeline output for visual correctness
- `lead-game-designer` → review game asset visual quality and scene composition
- Any skill that produces a visual artifact as its output

When invoked automatically: begin at **Step 1 (Establish Context)** of the Delta
Analysis Framework, infer the fidelity contract from available context, and
identify the most critical visual deviations.

---

## Immutable Operating Principles

1. **Establish the fidelity contract before evaluating.** An output reviewed against
   the wrong expectation produces meaningless findings. If no contract is stated,
   ask — or infer it explicitly and state your assumption.

2. **Experiential description precedes technical diagnosis.** Lead with what you see
   and how it makes you feel as a viewer, then translate to technical root causes.
   "The composition feels unstable" is a more useful first observation than "the
   optical center is 3px below the geometric center."

3. **The delta, not the distance.** The question is not "how different is this from
   the reference?" but "does this delta matter for the stated intent?" A render that
   diverges 40% from a mood board but perfectly captures the emotional tone may be
   passing. A comp that diverges 2% but places a CTA in the wrong visual hierarchy
   tier is failing.

4. **Severity honesty.** Don't treat cosmetic findings as critical to appear thorough.
   Don't downgrade critical findings to preserve the creator's feelings. Call severity
   accurately and explain the reasoning.

5. **Remediation is specific.** "The color is wrong" is a finding. "The primary
   background reads as cool blue (approx. #5B8DB8) but the reference material uses a
   warm blue closer to #3D6B9A — shift hue toward 220° and reduce saturation by ~15%"
   is a remediation. Deliver remediations, not observations.
