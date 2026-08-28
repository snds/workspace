---
title: Visual replication requirements (Literal)
status: active
date: 2026-08-09
project: "[[20-lcars-generative-interface]]"
---

# Visual replication requirements

These are **project law** for any work that claims to recreate Okudagram / LCARS surfaces from Sean's reference library. They complement SPEC.md (product architecture) and `docs/program-thesis.md` (why LCARS is the proof case). They do not replace the constitution validator.

## Program intent (do not narrow this to pixel cloning)

The goal is **systemic, programmatic** recreation: concept, context, intent, and aesthetic — expressed as measured Construction IR → legal Scene IR → deterministic renderer. LCARS is pack #1. The method must stay pack-swappable so other aesthetics/systems can load later without rewriting the pipeline.

Literal still-match is **necessary** for the proof. It is not sufficient alone: the recreation must land in the generative IR/catalog path, not a throwaway CSS replica.

## Contract

1. Default fidelity for named recreation work is **Literal** (`NORTHSTAR.md`).
2. Spirit evaluation (lead-visual-qa) may inform generative *recipes* after Literal grammar exists. It may not certify a recreation pass.
3. "Looks better," "tests green," and "captures the vibe" are not done criteria.

## Composite reference library

Drive LCARS EXEs→SWFs, `1701_D_Mk4.ai`, video loops, wallpaper stills, and sibling captures are taken **in composite** to guide implementation (shape grammar, motion cadence, density, content-group topology). They are **not** revised directives that replace or override the active northstar / Construction IR.

- **S-SYS47-01 remains Literal authority** unless Sean explicitly renames the northstar.
- Use the library to make Scene IR / catalog work closer to the references; do **not** silently rewrite cue-matrix acceptance from SWF, AI, or alternate video.
- Galaxy-class AI / Flash MSD panels **≠** Enterprise-E System47 still-match. Different ship/class/composition; grammar transfer only.

## Mandatory artifacts before coding a recreation

| Artifact | Location |
|---|---|
| Named northstar row | `NORTHSTAR.md` |
| Native PNG of reference (and later of build) | `docs/construction/captures/` (git-LFS or local-only; do not invent) |
| Construction IR | `docs/construction/<S-ID>.ir.json` |
| Cue matrix | `docs/construction/<S-ID>.cues.md` |

Schema: `03-skills/visual-reference-replication/reference/construction-ir.md`

## Hard stops

Stop the implementation thread if:

- Coding starts without IR + cue matrix for the active S-ID
- Colors, radii, gutters, or type sizes are taken from VLM prose / memory instead of probes
- Placeholder assets are unlabeled
- APCA / density / token edits change northstar fills without an ADR
- Prove step is skipped
- A "matched" screen exists only as one-off CSS that Scene IR / catalog cannot emit (fails programmatic ladder step 2)

## Prove gate (Literal)

1. Native side-by-side: full frame + elbow join + gutter + type crop
2. Instrumented checks via `visual-qa-toolkit` (or documented equivalent): alignment, spacing, color_extraction, visual_diff as applicable
3. Verdict language only: **Matches Literal** | **Partial** (list unmet cues) | **Fail**
4. For program ladder step 2: name the Scene IR / catalog primitives that emit the match

## Generative system relationship

- Literal recreation teaches the **construction grammar** the Scene IR and renderers must express.
- Once a northstar is Matches Literal, distill reusable primitives (elbow, spine segment, gutter constant, schematic viewport) into the catalog — do not keep one-off CSS that cannot be IR-driven.
- MockPlanner / recipes must emit assemblies that can hit the same grammar; they must not invent a parallel soft aesthetic.
- System-specific rules stay in the **LCARS pack** (constitution, tokens, catalog, project cursor rules). Pipeline skills stay system-agnostic.

## Skill load order for recreation sessions

1. Project `SESSION-STATE.md` Live handoff + `NORTHSTAR.md` + `docs/program-thesis.md`
2. `visual-reference-replication`
3. `native-visual-eval` → `visual-qa-toolkit` → (video) `reference-video-review`
4. `design-engineer` only after IR exists

## Gap ledger pointers

Workspace knowledge: `08-knowledge/cross-domain/visual-failure-mode-ledger.md` rows **C-03…C-08**, **Z-04**, **Z-05**.
