---
name: visual-qa-toolkit
description: Augmented-perception visual QA toolkit for design system and UI craft audits. Use when evaluating a screenshot or design export against measurable craft dimensions — alignment, spacing, contrast (WCAG 2.x), color palette drift (delta-E), visual diff (SSIM), color-vision simulation, icon consistency, typography scale, grid compliance, or component state differentiation. Trigger when: the user uploads a screenshot and asks for an audit/review; a design-to-code comparison is needed; icon or component set consistency is being evaluated; accessibility verification is in scope; visual regression checks are required; or the user wants measurable findings beyond visual inspection. Trigger on phrases like "audit this screen," "check the contrast," "compare design vs. implementation," "are these icons consistent," "is this on the spacing scale," "visual diff," or "color-blindness check." Do NOT trigger for: code-level linting, Figma authoring work (use `design-engineer`), Figma plugin development, or tasks that don't involve measuring an image.
aliases: [visual-qa-toolkit]
tier: cross-cutting
domain: quality
hub: lead-visual-qa
spec_version: "2.0"
---

# Visual QA Toolkit

A toolkit of ten focused Python scripts plus an orchestrator for instrumented
visual QA of UI screenshots, design exports, and icon/component sets.

This is the implementation of "augmented perception" from the Last-Mile Craft
Framework — it replaces Claude's baseline visual inspection (which is unreliable
for pixel-level measurements) with deterministic, verifiable analysis that
produces annotated images and structured findings.

## When to use this skill

Load this skill when the session involves measuring an image against a design
standard or baseline. The ten checks cover:

| Check | What it measures |
|---|---|
| `alignment` | Element edge alignment against cluster medians |
| `spacing` | Gaps between elements against a configured scale |
| `contrast` | WCAG 2.x contrast ratios for text regions |
| `color_extraction` | Sampled colors vs. a token palette (CIE76 Δe) |
| `visual_diff` | SSIM + pixel diff between two images |
| `color_vision` | Deutan/protan/tritan simulation + color-pair collapse detection |
| `icon_consistency` | Bounding box, weight, stroke outliers across an icon set |
| `typography` | Cap-height approximation vs. type scale |
| `grid_overlay` | Visualization tool — overlays column grid, baseline, rulers |
| `state_comparison` | Pairwise SSIM between default/hover/focus/active/disabled |

## Invocation protocol — inputs come from the user, not from filesystem hunting

The toolkit is project-agnostic by design. It operates on paths the user provides:
a screenshot path, a folder path (for icon sets or state screenshots), a reference
image (for `visual_diff`), a palette JSON (for `color_extraction`), and a config file.
It has no knowledge of any specific project, design system, or token export — configs
carry all project-specific context.

When Claude runs the toolkit on behalf of a user, the protocol is:

1. **Ask for the screenshot or folder to audit.** Don't assume a default location.
   If the user has uploaded an image to the session, use that path. Otherwise ask
   — don't hunt the filesystem.
2. **Ask which config to use.** Options: `configs/default.yaml`, one of the shipped
   tuning examples, or a project-specific config at a path the user provides.
3. **Ask whether a palette file is available** if `color_extraction` is in scope.
   The toolkit has no built-in palette knowledge; `palette_path` must come from
   the user or be explicitly skipped.
4. **Ask for a reference image** if `visual_diff` is enabled. No auto-discovery
   of reference paths.
5. **Ask for an icon folder or state folder** if those checks are enabled.

Never hunt the user's filesystem for project-specific artifacts (token exports,
reference screenshots, icon exports, palette JSONs, brand guidelines, etc.).
Those live wherever the user puts them; the toolkit's job is to accept paths
and run checks. Project-specific conventions, tokens, and palettes belong in
the project's own skill or context — not in the toolkit.

**Shortcut for repeated use:** if the user already has a project context file
(see "Project context files" below), most of this protocol collapses to "load
context + confirm/ask for any deltas." The context file carries the project's
standard paths; CLI args handle per-run variations.

## How to invoke

There are two invocation modes depending on where the work lives.

### Mode A — Claude runs the suite in-session

When images are uploaded or reachable from the chat, invoke the suite inside
the Claude container. Scripts are copied from the skill folder into `/home/claude`
at session start, then executed:

```bash
cd /home/claude/visual-qa-toolkit
python qa-suite.py \
  --input /mnt/user-data/uploads/screenshot.png \
  --config configs/default.yaml \
  --output ./qa-out
```

After the run, read `qa-out/qa_report.md` and synthesize findings for the user.
Key principle: scripts write full output to disk; Claude reads only the
consolidated report unless a specific finding needs the annotated image to
explain.

### Mode B — Sean runs the suite locally

When work is batch, local-only, or when in-session execution would be
prohibitively expensive, Sean runs the suite on his machine and pastes the
consolidated report back into the session. The SKILL.md documents both modes
so the handoff is smooth either way.

```bash
cd "02-skills/visual-qa-toolkit"
python qa-suite.py --input ~/screenshots/page.png --config configs/default.yaml --output ~/qa-out
```

## Invocation pattern — individual script

When only one check is needed, call the script directly:

```bash
python -m scripts.qa_contrast --input screenshot.png --config configs/default.yaml --output ./qa-out
```

Or via the suite's `--only` flag to share the consolidated-report infrastructure:

```bash
python qa-suite.py --input screenshot.png --config configs/default.yaml --output ./qa-out --only contrast,alignment
```

## Input requirements per check

| Check | Input | Notes |
|---|---|---|
| alignment, spacing, contrast, color_extraction, visual_diff, color_vision, typography, grid_overlay | single image file | PNG preferred for crisp UI; PNG/JPG both accepted |
| visual_diff | two images (`--input` + `--reference`) | Must be identical dimensions |
| icon_consistency | folder of icons (PNG) | Each icon should be a separate file |
| state_comparison | folder of state screenshots | File stems become state names (e.g., `hover.png` → `hover`) |

The suite's `--folder-for` flag lets you combine image-input and folder-input
checks in a single invocation:

```bash
python qa-suite.py --input screenshot.png --folder-for ./icon-exports --config configs/default.yaml --output ./qa-out
```

## Config structure

Configs are YAML. Each check has its own section; omit a section to use script
defaults. Set `enabled_checks` at the top level to run only a subset; omit it
to run all enabled sections.

**Three configs ship with the toolkit:**

- `configs/default.yaml` — safe starting point with generic tolerances. Use this
  for any project, or as a base when authoring a new project-specific config.
- `configs/centric.yaml` — **tuning example** showing tight enterprise-style
  tolerances (dense data UIs, 4-based spacing, strict WCAG). Named after the
  Centric PLM reference project but has no Centric-specific baked-in assumptions;
  it's an illustration of how to calibrate for a dense-enterprise context.
- `configs/legion.yaml` — **tuning example** showing looser game-UI tolerances
  (bigger spacing scale, looser alignment, stricter color-vision). Named after
  the Legion game project but similarly just an illustration of game-UI
  calibration.

**For a specific project**, author a dedicated config that:

1. Starts from `configs/default.yaml` or the nearest shipped example.
2. Lives *with the project* (in a project folder or a project-specific skill) —
   not in the toolkit's `configs/` folder.
3. References a palette export path and any other project-specific inputs via
   paths the user controls.
4. Is passed via `--config /path/to/project-config.yaml` at invocation time.

The toolkit has no awareness of specific projects — configs carry all
project-specific context. This keeps the toolkit portable across any project,
design system, or aesthetic.

## Project context files (optional)

For repeated use against the same project, a **context file** bundles per-project
defaults and config overrides into a single portable YAML document. The toolkit
stays project-agnostic; the context file carries all project-specific knowledge
and is passed explicitly via `--context`.

This is purely a convenience layer — everything a context file does can be done
with CLI args. Use context files when the same arg set would otherwise be typed
repeatedly (daily audits, CI, standalone local runs without an LLM in the loop).

### Precedence

```
CLI args  >  context.defaults  >  config file  >  script defaults
context.check_overrides is deep-merged INTO the loaded config
```

CLI args always win. Any arg not passed on the CLI falls back to the context's
`defaults` block. The config file is still the base source of truth for per-check
tuning; `check_overrides` in the context are merged on top of it.

### Schema

```yaml
project: My Project Name          # optional label, echoed in reports

defaults:                          # optional — CLI arg defaults
  input: ~/screenshots/latest.png
  config: ./project-config.yaml
  output: ~/qa-reports/myproj/
  reference: ~/design-exports/page.png
  folder_for: ~/design-exports/icons/
  only: alignment,contrast         # string: comma-separated check names

check_overrides:                   # optional — merged INTO the config
  color_extraction:
    palette_path: ~/design-exports/primitives.json
  contrast:
    standard: WCAG_AAA
    text_regions:
      - {bbox: [40, 80, 200, 24], label: page_title}
```

### Path resolution inside context files

- **In `defaults`:** tilde (`~`) expanded, and relative paths resolved against
  the context file's own directory. This keeps context files portable — move
  the project folder, the context still works.
- **In `check_overrides`:** tilde expanded only. Use absolute paths for anything
  else to keep behavior predictable.

### Invocation examples

```bash
# Context supplies everything
python3 qa-suite.py --context ~/projects/myproj/.visual-qa-context.yaml

# Context supplies defaults; CLI overrides --input for today's run
python3 qa-suite.py --context ~/proj/.ctx.yaml --input ~/today-screen.png

# Subset via --only, using context for input/config/output
python3 qa-suite.py --context ~/proj/.ctx.yaml --only contrast,color_vision
```

### Where to put context files

Anywhere the user controls — typically inside the project folder itself:

- `~/projects/<project>/.visual-qa-context.yaml`
- `~/projects/<project>/qa/context.yaml`
- Inside a project-specific skill's folder

Do **not** bundle project context files in the toolkit's own folder. The toolkit
ships with `tests/example-context.yaml` as a schema reference only.

### LLM-authored context files

An LLM (like Claude) can author a context file from a project's `SESSION-STATE.md`
or existing skill, then point the toolkit at it. This is the bridge between
LLM-mediated runs and standalone LLM-free runs: the same context file serves both.

## Outputs

Every suite run produces in the output directory:

- `qa_report.md` — the consolidated report (the primary artifact)
- `qa_report.json` — machine-readable summary of all findings
- `<check>_report.md` — per-check detailed report
- `<check>_annotated.png` and/or other visuals — reference images for findings

## Exit codes (useful for CI)

- `0` — no critical or high-severity findings
- `1` — at least one high-severity finding
- `2` — at least one critical finding

## Relationship to other skills and frameworks

- **Last-Mile Craft Framework (`00-frameworks/`)** — this toolkit is the
  "augmented perception" surface. Findings feed into the framework's
  enforcement handoff artifact.
- **`lead-visual-qa`** — the advisory hub for visual QA. Establishes the
  fidelity contract (Literal / Spirit / Standard / Intent) and the delta
  analysis framework, then routes to domain spokes. This toolkit is the
  *measurement companion* to lead-visual-qa's heuristic evaluation — when
  delta analysis surfaces dimensions that can be measured instead of asserted
  (alignment, spacing, contrast, color, state differentiation), invoke the
  toolkit to verify with numbers.
- **`visual-qa-ui-design`** — the UI-design spoke. Overlaps most directly with
  the toolkit's `alignment`, `spacing`, `contrast`, `color_extraction`,
  `typography`, and `state_comparison` checks. Use the spoke for heuristic
  evaluation and pattern-level review; use the toolkit for pixel-level
  verification.
- **`visual-qa-accessibility`** — the accessibility spoke. The toolkit's
  `contrast` and `color_vision` scripts are the measurement arm of its WCAG
  and color-independence criteria. The spoke defines the lens; the toolkit
  produces the evidence.
- **`visual-qa-usability`** — the usability spoke. The toolkit's
  `state_comparison` script measures whether interactive states are
  differentiated enough to provide feedback visibility — a concern the spoke
  flags qualitatively but can't quantify on its own.
- **`design-engineer`** — when a design-engineered deliverable is in review,
  run the toolkit first, then use `design-engineer` for triage and resolution.
- **`ds-advisor`** — toolkit findings are inputs to design system compliance
  review. A triage conversation in `ds-advisor` often follows a suite run.
- **`variable-icon-font-architect`** — `icon_consistency` can spot outliers
  in exported icon sets, but font-level geometry analysis belongs in the
  icon-font-architect skill, not here.

## Honest limits

- **Perceptual off-ness** that isn't geometric (optical centering against
  perceptual weight) shows up as "technically aligned" here even when it
  looks wrong. Human perception still matters.
- **Motion and interaction feel** — screenshots are static; nothing here
  evaluates animation or transition quality.
- **Font family/weight identification** — typography measures cap-height
  only; font identity belongs in design-vs-code comparisons or DS audits.
- **Semantic correctness** — the toolkit measures construction, not meaning.
  An icon may pass all consistency checks and still be the wrong icon for
  the job.
- **Text detection is heuristic** — auto-detected text regions are MSER
  candidates, not guaranteed-correct. For precision, specify explicit
  `text_regions` in the config.

## Workflow integration

Typical integration into a design-engineered deliverable:

1. Capture state screenshots and/or a representative page screenshot.
2. Run the suite with the project-appropriate config.
3. Review `qa_report.md`.
4. In-session: discuss findings with Claude — signal vs. noise, severity
   triage, proposed fixes. Claude pulls annotated images only for findings
   worth deeper discussion.
5. Capture decisions in the enforcement handoff artifact (per the
   Last-Mile Craft Framework).

## File layout

```
visual-qa-toolkit/
├── SKILL.md                          # This file
├── README.md                         # Human-facing overview
├── requirements.txt
├── qa-suite.py                       # Orchestrator
├── scripts/
│   ├── __init__.py
│   ├── _common.py                    # Shared utilities
│   ├── _context.py                   # Project context file loader + merge
│   ├── qa_alignment.py
│   ├── qa_spacing.py
│   ├── qa_contrast.py
│   ├── qa_color_extraction.py
│   ├── qa_visual_diff.py
│   ├── qa_color_vision.py
│   ├── qa_icon_consistency.py
│   ├── qa_typography.py
│   ├── qa_grid_overlay.py
│   └── qa_state_comparison.py
├── configs/
│   ├── default.yaml
│   ├── centric.yaml                  # tuning example
│   └── legion.yaml                   # tuning example
└── tests/
    ├── example-context.yaml          # context file schema reference
    ├── make_fixture.py               # generates synthetic test images
    └── make_additional_fixtures.py
```

## Related
- hub → [[lead-visual-qa]]
