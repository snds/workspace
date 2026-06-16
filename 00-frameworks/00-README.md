# Frameworks — Overview and Navigation

_Workspace: `00-frameworks/`_
_Last updated: 2026-06-08_

Seven top-level operating documents that govern how design, collaboration, research, craft, QA, and integration decisions get made across all projects. They sit above any project-specific skill or context. Not project-gated. Not domain-gated. They're the portable layer that stays consistent even when the specific work shifts.

This README is the orientation layer. Load it when you need to know which framework applies, or when you're working in a token-constrained context and want the compressed summary without loading all seven full documents.

---

## The seven frameworks

| # | Framework | Answers |
|---|---|---|
| 01 | **Aesthetic Lens** | Why does this feel right? |
| 02 | **UI/UX Operational Framework** | How do we systematically decide about hierarchy, interaction, and metaphor? |
| 03 | **Collaboration and Critique Framework** | How do we work together? |
| 04 | **Research and Evidence Framework** | What do we know, and how do we know it? |
| 05 | **Last-Mile Craft Framework** | How do we finish well? |
| 06 | **QA Operating Model** | How do we frame QA outcomes against target-user expectations on first delivery? |
| 07 | **Integration & Review Framework** | How do we land work so it merges cleanly and reviews well? |

---

## Recommended reading order

**First pass (all six).** Read in numerical order. They build on each other — Aesthetic Lens sets the philosophical ground, UI/UX lays operational structure on top, Collaboration and Research govern how the work gets produced and justified, Last-Mile governs the finishing layer that ties it all together, and the QA Operating Model frames every audit / review / iteration outcome against target-user expectations.

**By context (once familiar).** Load only what's relevant:

| Working on… | Load at minimum |
|---|---|
| Creative direction, aesthetic reasoning, visual identity | 01 |
| IA, interaction decisions, pattern choice, expertise design | 01, 02 |
| Design system work, component audit, triage | 01, 02, 05, 06 |
| Difficult conversation, pushback, shared disagreement memory | 03 |
| Evidence threshold, confidence tier, advocacy calibration | 04 |
| Design review, visual QA, handoff, finishing audit | 01, 02, 05, 06 |
| Iteration, refinement, clean-up, alignment work | 06 (always), then 05 |
| Game art direction (Legion) | 01, 05 |
| Icon / variable font system | 01, 05 |
| Architectural or interior reference | 01, 05 |
| Branching, PRs, merging, multi-branch consolidation | 07 |
| Full design-engineered delivery | all seven |

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
- Critical-eye pre-output gate before every report: target-user check, coverage check, composition-before-footprint check, reference check, honesty check, skill check.
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

---

## How they interconnect

The seven frameworks are layered, not parallel. They're listed in the order they compose:

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

---

## Also in this folder

- `_migration-audit-notes_2026-04-21.md` — Preservation-biased token-optimization audit from the migration session. Tracks what was cut, what was considered but preserved, and why. Useful reference if future passes need to see the editing rationale.

## Related workspace docs

- `../01-shared-references/epistemic-standards.md` — core epistemic obligations (surface assumptions, verify sources, name alternatives). Load when beginning non-trivial reasoning.
- `../01-shared-references/artifact-standards.md` — deliverable obligations (naming, versioning, no overwrites). Load when producing or receiving any file.
- `../02-skills/` — the tactical execution layer. Frameworks hold the principles; skills do the work. See each framework's "Relationship to existing skills" section for the specific mapping.

---

## Notes for LLMs loading this README

**Token budget guidance.** The seven frameworks total ~1,700 lines of markdown. This README runs ~250 lines and captures the core conviction and operating habits of each. If you have the budget for the full set, load the full set. If you're constrained, load this README plus whichever specific framework is most relevant to the task at hand. For QA / audit / review / iteration work, always load #06 in addition. For branching, PR, or consolidation work, load #07.

**When the README isn't enough.** The compressed summaries preserve the *what* but not the *why* — the examples, the canon references, the tier descriptions with thresholds, the principle-to-check translations. Any serious reasoning task in the framework's domain should load the full document.

**Updates.** Framework numbering is stable (01–07). Any future framework additions should extend the sequence (08, 09, etc.) or, if a restructure is warranted, be handled as a fresh migration session with full reference audit. Trigger migration work with *"Let's execute a framework migration"* — that flags the scope explicitly.

**Operational state.** This folder is static reference. Operational continuity between sessions lives in per-project `SESSION-STATE.md` files (see framework 05's Operational State section for the spec) and in `../06-context/session-log.md` for cross-project session logs.
