# render-qa-toolkit

Deterministic measurement for realtime / photoreal render QA. Sibling of
`visual-qa-toolkit`. Ten scripts + orchestrator for frame-budget JSON, native
tile grids, exposure/histogram, temporal shimmer, northstar match, and ledger hints.

Implements the measurement side of the **triple done-gate**: native stills +
motion frames + measured ms (`?perfcapture`).

## Requirements

- Python 3.9+
- Deps: Pillow, NumPy, OpenCV (headless), scikit-image, PyYAML
- **ffmpeg** on PATH for `qa_video_extract` only (`brew install ffmpeg`)

## Install

```bash
python3 -m pip install --user -r requirements.txt
# or
python3 -m venv ~/.venvs/render-qa-toolkit
source ~/.venvs/render-qa-toolkit/bin/activate
pip install -r requirements.txt
```

## Quickstart

```bash
# Frame budget from Legion ?perfcapture JSON
python3 qa-suite.py \
  --perf ~/captures/lab-0.8au.json \
  --config configs/legion.yaml \
  --output ~/qa-out \
  --only frame_budget,pass_attribution

# Native tile grid on a still (assert native evidence)
python3 qa-suite.py \
  --image ~/captures/pose.png \
  --config configs/legion.yaml \
  --output ~/qa-out \
  --only native_grid,histogram_hdr,false_color_exposure,ledger_detect \
  --labeled-native

# Single check
python3 -m scripts.qa_temporal_delta \
  --input ~/captures/fly-frames \
  --config configs/default.yaml \
  --output ~/qa-out
```

### Legion pose example

```
?lab=planet&perfcapture&au=0.8&w=1280&h=720&dpr=2
```

Paste `window.__perfCapture` JSON into a file you choose; pass that path as `--perf`.
Do not ask the toolkit to find capture dumps on disk.

## Checks

| Script | Input | Measures |
|---|---|---|
| `qa_frame_budget.py` | JSON (`--perf`) | Budget vs total ms + waterfall |
| `qa_pass_attribution.py` | JSON | Rank passes by ms |
| `qa_native_grid.py` | Image | 1:1 tiles; native size gates |
| `qa_histogram_hdr.py` | Image | Luminance hist + clipping |
| `qa_false_color_exposure.py` | Image | False-color overlay |
| `qa_temporal_delta.py` | Folder | Mean abs diff / shimmer |
| `qa_motion_stress.py` | Folder | Labeled stress peaks |
| `qa_reference_match.py` | Image + ref | SSIM + RGB/Lab MAD |
| `qa_video_extract.py` | Video | ffmpeg frame extract |
| `qa_ledger_detect.py` | Image | Heuristic ledger ID hints |

## Configs

- `configs/default.yaml` — generic thresholds (~14 ms real 60 fps budget)
- `configs/legion.yaml` — pose URL placeholders, flythrough notes, Legion-tuned floors

## Exit codes

- `0` — clean (no critical/high)
- `1` — high findings
- `2` — critical (including over-budget)

## See also

`SKILL.md` for the invocation protocol, triple done-gate language, and pairing with
`native-visual-eval` / `interactive-capture-eval` / `realtime-visual-craft`.
