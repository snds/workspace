# Resolved 2026-04-27

All seven loose `02-skills/*.md` files in this archive batch have been resolved. Five were strict duplicates of their dir SKILL.md siblings. Two carried unique content; that content was migrated into the dir SKILL.md before the loose file was archived.

## Migrations performed

### `figma-ds-generation-pipeline.md` → merged into `02-skills/figma-ds-generation-pipeline/SKILL.md`

Added a new **"Step 0: Stack Selection (Required)"** section to Pre-Pipeline Setup, plus two follow-on subsections:
- **Radix Base Color Architecture** — full 38-scale (914-variable) primitive spec with batch execution order
- **Radix Semantic Scale Binding Map** — role-to-scale table (primary/destructive/success/warning/info/accent → Radix scales, steps 3-12) + per-role token pattern + gray-bound and alpha-bound semantic tokens + the "semantics never hold raw RGB" rule

External reference at `02-skills/design-engineer/SKILL.md:283` updated: replaced `ds-stack-router skill ... Lives at ~/.claude/skills/ds-stack-router/` with a pointer to the pipeline SKILL's new Step 0 section.

### `figma-style-binding.md` → merged into `02-skills/figma-style-binding/SKILL.md`

Appended four new sections after the existing immutability content:
- **Effect Style Creation and Binding** — `setBoundVariableForEffect` pattern + bindable fields (color, radius, spread, offset.x, offset.y)
- **Node Property Variable Binding** — `setBoundVariable()` pattern + full bindable-field reference (layout, appearance, typography, text-style fields)
- **Gradient Variable Binding (Manual)** — workaround for gradient stops since `setBoundVariableForPaint` only supports SolidPaint
- **Debugging Variable Bindings** — `node.boundVariables`, `variable.resolveForConsumer(node)`, font loading error table

## Why these are still here

Kept as historical reference only. The live SKILL.md files are now authoritative. No action needed.
