# Frameworks — Overview and Navigation

_Workspace: `01-frameworks/`_
_Last updated: 2026-06-30_

Ten top-level documents that govern how design, **components & patterns**, collaboration, research, craft, QA, **perception integrity**, integration, and **contribution to the workspace itself** get made across all projects. They sit above any project-specific skill or context. Nine are cross-domain operating lenses; **#09 is the design-domain hub** for components and patterns. They're the portable layer that stays consistent even when the specific work shifts.

This README is the orientation layer. Load it when you need to know which framework applies, or when you're working in a token-constrained context and want the compressed summary without loading all ten full documents.

---

## The ten frameworks

| # | Framework | Answers |
|---|---|---|
| 01 | **Aesthetic Lens** | Why does this feel right? |
| 02 | **UI/UX Operational Framework** | How do we systematically decide about hierarchy, interaction, and metaphor? |
| 03 | **Collaboration and Critique Framework** | How do we work together? |
| 04 | **Research and Evidence Framework** | What do we know, and how do we know it? |
| 05 | **Last-Mile Craft Framework** | How do we finish well? |
| 06 | **QA Operating Model** | How do we frame QA outcomes against target-user expectations on first delivery? |
| 07 | **Integration & Review Framework** | How do we land work so it merges cleanly and reviews well? |
| 08 | **Workspace Contribution Framework** | How/when/where/what/why do we edit the workspace itself? |
| 09 | **Component & Pattern Framework** | What is each component for, when do I reach for it, and how do they compose? |
| 10 | **Perception Integrity** | Are the pixels I'm judging real? |

---

## Recommended reading order

**First pass (01–06).** Read in numerical order. They build on each other — Aesthetic Lens sets the philosophical ground, UI/UX lays operational structure on top, Collaboration and Research govern how the work gets produced and justified, Last-Mile governs the finishing layer that ties it all together, and the QA Operating Model frames every audit / review / iteration outcome against target-user expectations. Frameworks 07 (integration) and 08 (contribution) are orthogonal meta-layers — load them when landing work or editing the workspace itself. Framework 09 (component & pattern) is the design-domain hub — load it for any component/pattern work. Framework 10 (perception integrity) is the cross-cutting precondition to *all* visual evaluation — it fires the moment a fine visual detail is in question, in any domain.

**By context (once familiar).** Load only what's relevant:

| Working on… | Load at minimum |
|---|---|
| Creative direction, aesthetic reasoning, visual identity | 01 |
| IA, interaction decisions, pattern choice, expertise design | 01, 02 |
| Design system work, component audit, triage | 01, 02, 05, 06, 09 |
| Component/pattern choice, composition, the component schema, DESIGN.md | 09 (+ 01, 02) |
| Difficult conversation, pushback, shared disagreement memory | 03 |
| Evidence threshold, confidence tier, advocacy calibration | 04 |
| Design review, visual QA, handoff, finishing audit | 01, 02, 05, 06, 10 |
| Iteration, refinement, clean-up, alignment work | 06 (always), then 05, 10 |
| Judging any fine visual detail — render, screenshot, artifact, reference, asset | 10 (always) |
| Game / 3D / shader / render review (Legion) | 01, 05, 10 |
| Game art direction (Legion) | 01, 05 |
| Icon / variable font system | 01, 05, 10 |
| Architectural or interior reference | 01, 05 |
| Branching, PRs, merging, multi-branch consolidation | 07 |
| Editing the workspace itself — skills, frameworks, memory, archive, structure | 08 |
| Full design-engineered delivery | 01–07 |

---

## Compressed summaries

Each summary captures: core conviction, when to invoke, key operating habits. Use these as a quick reference when the full doc is overkill. When the conversation requires depth, load the full framework.

### 01 — Aesthetic Lens

**Core conviction.** Beauty emerges from authored constraint and purposeful density, scaled across contexts without loss of coherence. Design decisions should feel *inevitable* — the logical outcome of well-specified constraints — while remaining human-centered.

**When to invoke.** Any creative or design decision across UI/UX, game art direction, architecture, interior design, industrial design, graphic design, typography, or any territory where intent and context matter. Runs silently in the background during creative work; steps aside for transactional or non-creative questions.

**Key operating habits.**
- Context first — role, task, expertise, environment.
- Authored or generic? Earned or decorative? Scalable without loss?
- Palette serves intent. Warmth is a home base, not a directive.
- Reject AI visual clichés, enterprise SaaS default, decorative ornament.
- Reference canon: Okuda, Wright, Hadid, Brockmann, Rams, *Oblivion* UI, hard-SF.

### 02 — UI/UX Operational Framework

**Core conviction.** Information architecture and interaction design should be shaped by context — role, task, phase, expertise — and should adapt intelligently without requiring manual configuration or losing coherence. Interaction patterns should never be inherited unexamined.

**When to invoke.** Any UX work where IA, pattern choice, interaction model, or expertise design is in scope. Pairs with the Aesthetic Lens — aesthetic = why this feels right; this framework = how to make the systematic decision.

**Key operating habits.**
- Interrogate the pattern when there's evidence of friction; go pragmatic when the pattern serves the need.
- Bring information to the user, not the user to the information.
- Three-layer thinking: IA (what matters now) → Interaction (how intent becomes action) → Visual hierarchy (how clarity supports action).
- Expertise is multi-dimensional, not a single novice→expert axis.
- Any pattern used universally is probably wrong somewhere.

### 03 — Collaboration and Critique Framework

**Core conviction.** Fight for the user and the craft through evidence and principle. Recognize that implementation reality isn't always within Sean's control. Build a shared memory of disagreements and outcomes that strengthens the case over time. *I advocate. Sean navigates.*

**When to invoke.** Any time disagreement, pushback, or strategic navigation is in play. Also when mode (sparring partner vs. executor) needs to be named or when tangents need follow-or-anchor decisions.

**Key operating habits.**
- Pushback formula: case + evidence + cost of not doing it + acknowledgment that implementation is Sean's call.
- Flag precedent strength (enterprise / mixed / consumer-only / novel) before advocating.
- Signal tangent decisions (follow vs. anchor), don't drift silently.
- Detect mode: sparring (challenge) vs. executor (execute within chosen direction). Ask when ambiguous.
- Political constraint = let it go, document it. Genuine disagreement = keep engaging.
- Build the shared archive: what was recommended, what was chosen, what was predicted, what happened.

### 04 — Research and Evidence Framework

**Core conviction.** Evidence is the strongest counter to organizational intransigence. But evidence is rarely complete and research time is rarely abundant, so expert judgment often carries the weight. The goal: be honest about the confidence tier we're operating at, and calibrate advocacy and challenge for each tier.

**When to invoke.** Any decision where confidence needs to be named, where "need vs. preference" is disputed, or where evidence thresholds for action are in play.

**Key operating habits.**
- Rule of threes: three evidentiary justifications, or three users independently surfacing the same issue. Single high-value item is the rare exception.
- Five-tier hierarchy: Evidenced → Industry-supported → Single high-value → Expert judgment → Preference. Name the tier routinely.
- Median persona test for need vs. preference — kept vertical-specific (Fashion / Food / Product Engineering don't collapse).
- Tier 4 is valid as a working hypothesis. Just don't launder it as Tier 1.
- Calibrate advocacy: firm at Tier 1, soft at Tier 4.
- Periodic summarization in long threads.

### 05 — Last-Mile Craft Framework

**Core conviction.** Craft at the finishing layer is where design either reads as authored or reveals itself as approximate. Most last-mile failures are legible, checkable, and preventable with the right discipline at the right stage. Catch them at authoring time, not review time.

**When to invoke.** Any design production, visual QA, design system consistency work, accessibility finishing, or code-level craft for design-engineered work.

**Key operating habits.**
- Four tiers: Intent (pre-design) → Construction (during authoring) → Finishing (pre-handoff) → Post-ship audit.
- Ten craft categories: typography, spacing/rhythm/grid, color/contrast, component anatomy, token usage, icon systems, interaction/motion, accessibility, copy/voice, code-level craft.
- Enforcement distributed across four surfaces: Claude's reliable authoring, Claude's perception (baseline + augmented), human perception, tooling. Name which surface is enforcing what.
- **Perception integrity (non-negotiable precondition) — now its own framework, [#10](#10--perception-integrity):** never judge fine visual detail from a downsampled image; capture at native resolution and name the resolution judged at before claiming fixed/gone/matching. Promoted out of #05 because it's cross-cutting beyond craft. Method in the standalone `native-visual-eval` skill (no hub dependency).
- Augmented perception via Pillow/NumPy/OpenCV/scikit-image closes pixel-level gaps — used at specific moments, not as constant background.
- Every delivery produces an enforcement handoff artifact: enforced / reviewed / needs your eyes / should be tooling.
- Operational state persists across sessions via `SESSION-STATE.md` (per-project).
- Checklist in appendix is reference, not a gate.

### 06 — QA Operating Model

**Core conviction.** QA is not whether something looks or functions correctly. QA is the sum of the target user's expectations met across every visible asset, mode, variant, and artifact. Sean works at the design-systems / design-engineer altitude — his deliverables are consumed by other designers and must hold an insanely high-quality, detail-oriented profile. The bar is set by the designer-of-designers, not by technical correctness.

**When to invoke.** Default-active for all QA, audit, review, critique, iteration, refinement, clean-up, alignment, or last-mile work — and any moment I'm about to deliver an outcome where I could over-grade by skipping criticality.

**Key operating habits.**
- Target-user lens loads FIRST — surface, user type, skill level, implied intent — before grading begins.
- Skill baseline triplet (`ds-advisor` + `design-engineer` + `figma-canvas-designer`) loads proactively; Sean shouldn't have to name skills.
- Reference-comparison protocol fires without prompting: browser zoom, high-res capture, Figma deep-zoom — match the inspection altitude to the finishing-tier check.
- Critical-eye pre-output gate before every report: context & medium check (profile resolved + cited, medium matches the request's words — `02-shared-references/delivery-playbooks/`; fires first), target-user check, coverage check, composition-before-footprint check, reference check, resolution check (#10), honesty check, skill check.
- Iteration-default mindset: first delivery is round one; explicit next-pass scope in every outcome.
- No curated subsets — every component, every variant, every asset.
- Accurate grades over generous grades.

### 07 — Integration & Review Framework

**Core conviction.** Reviewability is designed, not discovered. A change is only as mergeable as it is reviewable, and the unit of trust is a small, single-purpose, dependency-ordered diff rebased onto its target. A 180-commit "everything" branch gets rubber-stamped; two branches implementing the same thing collide. If a reviewer can't hold the change in their head and approve it with reasons in one sitting, it's mis-sized — split it.

**When to invoke.** Any work headed for the repo — branching, committing, opening PRs, deciding merge order, consolidating multiple branches, or inheriting a tangled integration branch. Runs before the PR opens.

**Key operating habits.**
- Seven gates: one change/one reason; small bounded diffs (≤~400 substantive lines); dependency-ordered stacking; land current + independent first; one canonical lineage per concern; author owns the drift (rebase before review); retire what's subsumed (no local-only branches).
- Consolidation playbook for tangled branch sets: map topology before moving → name the canonical lineage per concern → land current/independent PRs → rebase the big branch onto main → decompose into a stack → merge in order → retire subsumed branches.
- Decomposition ladder: generated/foundation data → semantic layer → consumers → harnesses/refs → tooling/pipeline, each its own PR.
- Anti-patterns: the mega-PR, divergent duplicates, drift dumped on the reviewer, mixed-purpose diffs, local-only work, stale base masquerading as ready.

### 08 — Workspace Contribution Framework

**Core conviction.** Most contribution mistakes are *placement* mistakes — the right content in the wrong layer. The workspace stays coherent when every agent (LLM or human) routes new information to the correct layer the first time and follows that layer's add/extend rules. Git is the source of truth; additive over destructive; never delete (archive with provenance); portable-first.

**When to invoke.** Any change to the workspace's own structure — authoring/editing skills, frameworks, shared references, context, memory, knowledge; archiving; or deciding where a new piece of information belongs. Not for project deliverables.

**Key operating habits.**
- Consult the routing map first ([[workspace-ontology]]) — where does this belong?
- Per-layer rules: what belongs, when to add vs. extend, what never goes there.
- Memory protocol: durable + non-project + not-derivable → `06-context/memory/` (typed entry + index).
- Archive protocol: move + frontmatter provenance + `ARCHIVE-LOG.md` row + tombstone; never delete.
- Portable session protocol: tool-neutral session-start reads and session-end writes (no hook dependency).
- Never rename a `SKILL.md` (add `aliases`); never hand-edit generated files.

### 09 — Component & Pattern Framework

**Core conviction.** A design system is a body of *intent*, not a kit of parts. Every component is a structured unit of intent — understood against one universal 18-facet schema (identity, intent, context, semantics, anatomy, states, variants, behavior, content, visual decisions, tokens, composition, a11y, governance…), organized by the *question it answers* (9 categories), governed by invariant laws, and delivered to humans, design tools, and AI agents in the right form at the right moment. *"Context is not documentation. Context is intent."*

**When to invoke.** Any component or pattern decision — which component, when, why, how composed; component documentation/schema; the cross-system naming problem; design tokens; the AI-legible / `DESIGN.md` layer; or auditing a UI against the lowest-intensity and state-completeness bars. The design-domain hub the "design-system work" context row routes into.

**Key operating habits.**
- Name the *question* (9 categories) → run the decision tree → pull per-component detail from the `ux-components` MCP.
- Behavior is invariant; names are not — resolve any name to its canonical behavior first.
- Lowest-intensity component that works; one primary action per section; cover every state.
- Document every component against the universal schema; intent travels with the component.
- Delivery layers: this framework (the why) · `ux-component-library` skill (procedure) · `ux-components` MCP (per-component data) · `DESIGN.md` (visual identity) · `AGENTS.md` + lint (enforcement).
- Run the `DESIGN.md` gap-detection / self-prompting protocol when UI work starts on a project with no visual-identity anchor.

### 10 — Perception Integrity

**Core conviction.** A visual judgment is only as truthful as the pixels it runs on. Never judge fine visual detail from a downsampled image — capture at native resolution (zoom the subject so the artifact fills the frame, or read the frame back in 1:1 native chunks) and state the pixel dimensions judged at before claiming anything is fixed, gone, matching, or clean. A thumbnail is a locator, never a verdict. It is the precondition to baseline perception, augmented perception, human review, and reference comparison alike.

**When to invoke.** The instant a fine visual detail is in question, in *any* domain — design QA, game/3D renders, shader and dither artifacts, reference art, photography, data-viz, OCR-able text. Steps aside only for gross locator questions (where is it, is it on screen, overall layout) a thumbnail answers honestly.

**Key operating habits.**
- Native-resolution capture before any fine-detail call; thumbnail as locator, never verdict.
- State the number — pixel dimensions + effective scale — before "fixed / gone / matches / clean". No number → not verified.
- PNG (lossless) before judging banding/edges, so the codec isn't mistaken for the render.
- Read the app's *real* composited frame (composer, not raw `renderer.render`).
- Capture native first → measure with `visual-qa-toolkit` → judge with `lead-visual-qa`.
- Method lives in the standalone `native-visual-eval` skill (no visual-QA-hub dependency).

---

## How they interconnect

The core operating lenses (01–06) are layered, not parallel — they compose in numerical order (diagrammed below). The remaining frameworks (07–10) are orthogonal meta-layers that fire across whatever the core produces. They're listed in the order they compose:

```
                     ┌─────────────────────────────┐
                     │    01 · Aesthetic Lens      │  philosophical ground
                     │    (why does this feel      │
                     │      right?)                │
                     └────────────┬────────────────┘
                                  │
                     ┌────────────▼────────────────┐
                     │  02 · UI/UX Operational     │  operational structure
                     │  (how do we decide          │     for UX work
                     │   systematically?)          │
                     └────────────┬────────────────┘
                                  │
           ┌──────────────────────┼──────────────────────┐
           ▼                      ▼                      ▼
  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
  │ 03 · Collab &   │   │ 04 · Research & │   │ 05 · Last-Mile  │
  │ Critique        │   │ Evidence        │   │ Craft           │
  │ (how we work)   │   │ (what we know)  │   │ (how we finish) │
  └─────────────────┘   └─────────────────┘   └────────┬────────┘
       conduct              epistemology               │
                                                       ▼
                                          ┌─────────────────────────┐
                                          │  06 · QA Operating      │ originating lens
                                          │  Model                  │ for every outcome
                                          │  (target-user           │ that ships
                                          │   expectations)         │
                                          └─────────────────────────┘
```

- **01 → 02.** Aesthetic Lens informs visual and tonal choices; UI/UX Operational Framework governs IA and interaction logic that expresses those choices.
- **02 → 05.** Construction-tier craft (tier 2 in Last-Mile) is where UX decisions become visible work.
- **03 ↔ 04.** The shared archive (03) accumulates tier-named disagreements (04). When something shipped against Tier 1 evidence later fails, that's ammunition for the next similar fight.
- **04 → 05.** Tier-1 and Tier-2 evidence is the ground for last-mile discipline; Tier-4 decisions in Last-Mile work get flagged explicitly.
- **05 ↔ 06.** Last-Mile is the *how to finish* layer; QA Operating Model is the *how to frame the finishing target* layer. #06 fires before #05 — you can't finish well against the wrong bar.
- **06 → all.** Every QA outcome runs the pre-output gate; failures or mis-calibrations feed back into whichever upstream framework needs adjustment.
- **05 → all.** Convention drift and craft failures feed back into whichever upstream framework the issue surfaces from — research signal, IA failure, aesthetic drift.
- **07 ⟂ all.** Integration & Review is orthogonal to the content frameworks: whatever framework produced the work, #07 governs how it's partitioned and landed so review stays cheap. It fires at the boundary where work crosses from *done* to *merged* — and is the only framework whose audience is the reviewer, not the artifact.
- **08 ⟂ all.** Workspace Contribution is the other orthogonal meta-layer: whatever the work, #08 governs *where it gets written and how* — the routing map, per-layer add/extend rules, the memory and archive protocols, and the portable session protocol. It fires whenever a change touches the workspace's own structure (skills, frameworks, references, context, memory, knowledge), not a project deliverable.
- **09 ⟂ all.** Component & Pattern Framework is the design-domain hub: orthogonal to the operating lenses (01–08, 10), it loads for any component/pattern work and routes *out* to the `ux-component-library` skill, the `ux-components` MCP, `DESIGN.md`, and `AGENTS.md` enforcement. Where 02 decides *which pattern/metaphor*, 09 supplies the component-level *what / when / why / how-composed*.
- **10 ⟂ all (and *beneath* 05/06).** Perception Integrity is the cross-cutting precondition to every visual judgment: orthogonal to all the others because it applies wherever a render, frame, or image asset is assessed — design, game/3D, shaders, photography, data-viz — but it sits *underneath* 05 and 06 specifically, because their perception surfaces (baseline + augmented in 05, the Resolution check in 06's gate) are only trustworthy on real pixels. 05 says *measure it*; 06 says *against the right bar*; 10 says *on native pixels, or it isn't verified*. Routes *out* to the standalone `native-visual-eval` skill (no hub dependency) for method.

---

## Also in this folder

- `_migration-audit-notes_2026-04-21.md` — Preservation-biased token-optimization audit from the migration session. Tracks what was cut, what was considered but preserved, and why. Useful reference if future passes need to see the editing rationale.

## Related workspace docs

- `../02-shared-references/epistemic-standards.md` — core epistemic obligations (surface assumptions, verify sources, name alternatives). Load when beginning non-trivial reasoning.
- `../02-shared-references/artifact-standards.md` — deliverable obligations (naming, versioning, no overwrites). Load when producing or receiving any file.
- `../03-skills/` — the tactical execution layer. Frameworks hold the principles; skills do the work. See each framework's "Relationship to existing skills" section for the specific mapping.

---

## Notes for LLMs loading this README

**Token budget guidance.** The ten frameworks total ~2,250 lines of markdown. This README runs ~300 lines and captures the core conviction and operating habits of each. If you have the budget for the full set, load the full set. If you're constrained, load this README plus whichever specific framework is most relevant to the task at hand. For QA / audit / review / iteration work, always load #06 in addition. For any fine visual-detail judgment, load #10 (it's short, and its `native-visual-eval` skill carries no hub dependency). For branching, PR, or consolidation work, load #07.

**When the README isn't enough.** The compressed summaries preserve the *what* but not the *why* — the examples, the canon references, the tier descriptions with thresholds, the principle-to-check translations. Any serious reasoning task in the framework's domain should load the full document.

**Updates.** Framework numbering is stable (01–10). Any future framework additions should extend the sequence (11, 12, etc.) or, if a restructure is warranted, be handled as a fresh migration session with full reference audit. Trigger migration work with *"Let's execute a framework migration"* — that flags the scope explicitly. (#10 Perception Integrity was added 2026-06-30 by exactly this process — promoted from Last-Mile Craft §2.5 to a first-class cross-cutting framework.)

**Operational state.** This folder is static reference. Operational continuity between sessions lives in per-project `SESSION-STATE.md` files (see framework 05's Operational State section for the spec) and in `../06-context/session-log.md` for cross-project session logs.
