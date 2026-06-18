# visual-qa-toolkit

Augmented-perception visual QA for UI craft audits. Ten focused Python scripts
plus an orchestrator that produces a consolidated markdown report with annotated
image references.

## Requirements

- Python 3.9+ (tested on 3.9 and 3.12)
- Deps: Pillow, NumPy, OpenCV, scikit-image, matplotlib, PyYAML

## Install

Pick one — `--user` is simplest, venv is more isolated.

### Option A — user install (recommended)

```bash
python3 -m pip install --user -r requirements.txt
```

Works on modern macOS (3.12+) where bare `pip install` is blocked by PEP 668.
Packages go to `~/Library/Python/<version>/lib/python/site-packages/` and are
available to any Python script on the machine.

### Option B — virtual environment

Keep the venv outside the workspace checkout (e.g. `~/.venvs/`) so you don't version ~200MB of wheels:

```bash
python3 -m venv ~/.venvs/visual-qa-toolkit
source ~/.venvs/visual-qa-toolkit/bin/activate
pip install -r requirements.txt
```

Reactivate with `source ~/.venvs/visual-qa-toolkit/bin/activate` at the start
of each session.

## Quickstart

```bash
# Run the full suite on a screenshot
python3 qa-suite.py \
  --input ~/screenshots/page.png \
  --config configs/default.yaml \
  --output ~/qa-out

# Run a specific check
python3 -m scripts.qa_contrast \
  --input ~/screenshots/page.png \
  --config configs/default.yaml \
  --output ~/qa-out

# Run a subset via the suite (shares consolidated reporting)
python3 qa-suite.py \
  --input ~/screenshots/page.png \
  --config configs/default.yaml \
  --output ~/qa-out \
  --only alignment,contrast,color_vision

# Use a project context file to bundle defaults (see below)
python3 qa-suite.py --context ~/projects/myproj/.visual-qa-context.yaml

# Context supplies defaults; CLI overrides --input for this run
python3 qa-suite.py --context ~/proj/.ctx.yaml --input ~/today-screen.png
```

## What you get

- `qa_report.md` — one consolidated report. Start here.
- `qa_report.json` — same data, machine-readable.
- `<check>_report.md` — detailed per-check findings.
- Annotated images (`<check>_annotated.png`, `*_heatmap.png`,
  `*_comparison.png`, etc.) — the "see the ruler lines" artifacts.

## The ten checks

| Script | Input | Measures |
|---|---|---|
| `qa_alignment.py` | Image | Element edge alignment |
| `qa_spacing.py` | Image | Gaps between elements vs. a scale |
| `qa_contrast.py` | Image | WCAG 2.x contrast for text regions |
| `qa_color_extraction.py` | Image | Sampled colors vs. token palette (Δe) |
| `qa_visual_diff.py` | Image + reference | SSIM + pixel diff |
| `qa_color_vision.py` | Image | CVD simulation + color pair collapse |
| `qa_icon_consistency.py` | Folder | Bbox / weight / stroke outliers |
| `qa_typography.py` | Image | Cap-height vs. type scale |
| `qa_grid_overlay.py` | Image | Grid + baseline + ruler overlay (viz only) |
| `qa_state_comparison.py` | Folder | Pairwise SSIM between states |

## Invocation modes

**Claude in-session** — When you upload a screenshot and ask for an audit,
Claude picks a config, runs the suite, reads the consolidated report, and
discusses findings with you. Claude pulls individual annotated images only
for findings worth deeper discussion.

**Local** — Run the suite yourself for batch work, regression, or when the
images aren't easily reachable from the chat. Paste the consolidated report
back into the session for discussion.

## Configs

Three starter configs ship with the toolkit:

- `configs/default.yaml` — generic, safe starting point
- `configs/centric.yaml` — **tuning example** showing tight enterprise tolerances
- `configs/legion.yaml` — **tuning example** showing looser game-UI tolerances

The two named configs are illustrative examples only — they carry no
project-specific baked-in assumptions. For a real project, author a dedicated
config at a path you control and pass it via `--config`. See `SKILL.md` for the
full pattern.

## Project context files (optional)

For repeated use against the same project, a context file bundles defaults and
config overrides in one YAML doc. Pass it with `--context`; other CLI args
override its defaults.

```yaml
# ~/projects/myproj/.visual-qa-context.yaml
project: My Project

defaults:
  input: ~/screenshots/latest.png
  config: ./qa-config.yaml
  output: ~/qa-reports/myproj/

check_overrides:
  color_extraction:
    palette_path: ~/exports/primitives.json
  contrast:
    standard: WCAG_AAA
```

Run:

```bash
python3 qa-suite.py --context ~/projects/myproj/.visual-qa-context.yaml
```

See `SKILL.md` → "Project context files" for full schema and precedence rules.
`tests/example-context.yaml` is a working reference.

## Exit codes

- `0` — no critical or high-severity findings
- `1` — at least one high-severity finding
- `2` — at least one critical finding

Useful for CI integration — wire the exit code into a pre-merge gate when
visual diff is run against a design-export reference.

## Limits to hold honestly

- Measurements are deterministic; judgment about whether they *matter* is
  not. Treat findings as signal for review, not verdicts.
- Auto-detected text regions are MSER-based heuristics. For precision, pass
  explicit `text_regions` in the config.
- Typography cap-height estimation is approximate (±1–2 px). Fine for
  flagging obvious scale violations; not a substitute for design-token
  comparison.
- Image alignment/registration for `visual_diff` is not attempted. Both
  images must be the same size and pixel-aligned.
- Color-vision simulation uses Machado/Oliveira/Fernandes approximation
  matrices. Industry standard, but not a substitute for user testing.

## Extending

Each check script is self-contained — a `run()` function returning a
`ReportWriter`, plus a CLI entry point. To add a new check:

1. Add a new `qa_<name>.py` in `scripts/` that imports from `_common`.
2. Register it in `qa-suite.py`'s `CHECKS` list with the right input mode.
3. Add a config section to the shipped configs.
4. Document it in `SKILL.md`.

Shared utilities (`_common.py`) cover config loading, image I/O, element
detection, WCAG/Δe math, annotation, and report writing. Use them rather
than reimplementing — consistency across scripts is the point.
