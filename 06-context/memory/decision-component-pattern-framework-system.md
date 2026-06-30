---
type: decision
description: Why the 5-layer component & pattern framework system was built, and where its outputs live
created: 2026-06-30
confidence: high
---

The **5-layer interconnected component & pattern "context system"** was built (all phases complete
2026-06-17), organized by Diana Wolosin's intent model — *"Context is not documentation. Context is
intent."* This record captures the rationale and the canonical homes of the outputs; the durable
*content* lives in those outputs, not here.

**The five layers and where they live:**
1. **Framework (hub)** — `01-frameworks/09-component-and-pattern-framework.md`. The durable "why":
   universal 18-facet component schema, 9-category taxonomy, decision trees, compose-together model,
   cross-cutting laws (citable rationale from M3/Carbon/Apple/APG/Refactoring UI/Laws of UX),
   naming-divergence, lineages, the AI-legible layer, and the **DESIGN.md gap-detection +
   self-prompting protocol** (§12a). Indexed in `01-frameworks/00-README.md` + `_FRAMEWORKS.md`.
2. **Skill (procedure)** — evolved `03-skills/ux-component-library/` (NOT a new skill);
   `spec_version: 2.1`, `framework:` set; + references `component-authoring.md`,
   `tokens-and-naming.md`, `ai-ready-design-systems.md`.
3. **MCP (per-component data)** — the existing `ux-components` server (lookup/recommend/compare/
   smart_query).
4. **DESIGN.md (portable visual identity)** — Google's YAML-tokens-+-prose format; worked example
   authored from REAL Centric C8 PLM tokens at `c8-plm/DESIGN.md` (lints 0 errors). Annotated
   template in skill ref `ai-ready-design-systems.md` §3.
5. **AGENTS.md + lint (enforcement)** — `02-shared-references/ds-agents-binding.md` (copy-paste
   block); `c8-plm/AGENTS.md` is the tailored instance.

**Why this shape.** Atlassian's field test of DESIGN.md showed it wins for portable visual
identity/theming but loses to MCP+skills for production (all-at-once load, size-forces-omission,
re-implementation-over-integration). So DESIGN.md stays lean (visual identity only); component depth
lives in framework + on-demand MCP + skill. **Decisions (2026-06-17):** framework-first sequence;
evolve the existing skill rather than add one; C8 PLM as the DESIGN.md example; framework self-prompts
a DESIGN.md when a project starts UI work with no visual-identity anchor.

**A2UI** evaluated and integrated via 5 seams (catalog from taxonomy · MCP as catalog source/runtime ·
DESIGN.md→renderer CSS vars · skill validates · naming-map); documented in framework §11a + skill ref
§6; catalog projection at `02-shared-references/a2ui/canonical-catalog.json`.

**Optional next (not done):** A/B-evaluate a C8 screen via the AI-as-user loop; build a renderer
mapping the catalog variants → CDS components + `--sem-*` tokens.

(Migrated from local Claude-Code memory `component-pattern-framework-system`; the project itself is
complete, so it lives as a decision record rather than active project state. See
[[decision-externalize-everything-to-workspace]].)
