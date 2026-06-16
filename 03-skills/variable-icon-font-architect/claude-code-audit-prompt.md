# Variable Icon Font Project — Fresh-Eyes Audit

## Context Loading (do this first, in order)

1. Read the hub skill for this project:
   `03-skills/variable-icon-font-architect/SKILL.md`

2. From the hub's Spoke Manifest table, load these spokes (the audit spans all domains):
   - `lead-technical-digital-artist/SKILL.md` (pipeline architecture)
   - `lead-icon-artist/SKILL.md` (design methodology)
   - `lead-vector-designer/SKILL.md` (path construction)
   All at the same path root: `03-skills/`

3. Do NOT load the math spokes yet — load them only if the audit surfaces
   specific math-level questions (interpolation artifacts, curve quality,
   optical correction formulas).

4. Scan the project working directory for existing pipeline code, SVG assets,
   font build scripts, config files, and any prior audit artifacts. List what
   you find before proceeding.

## The Task

Examine the CentricSymbols/OmniSymbols variable icon font project with fresh eyes.
Review the approaches, methodology, technical stack, toolsets, and assets
against the standard set by Google's Material Symbols — the same problem
space, the same design constraints.

Produce a structured audit covering:

**Issues** — things that are broken, incorrect, or will cause downstream
problems (interpolation failures, pipeline bugs, spec violations)

**Optimizations** — things that work but could be better (build performance,
node reduction opportunities, SVG prep workflow)

**Rethinks** — architectural or methodological choices worth reconsidering
(master strategy, axis derivation approach, delivery format)

**Ideas** — opportunities not yet explored (automation, quality gates,
visual regression testing, LLM-assisted fill generation)

Organize findings into a phased implementation plan. The goal: generate a
variable icon font that meets or beats Google Material Symbols in visual
fidelity, technical integrity, and aesthetic rigor.

Reference the CentricSymbols v0.3 spec and any project artifacts you find
in the working directory. If you need deeper math analysis on any finding,
load the relevant math spoke at that point.
