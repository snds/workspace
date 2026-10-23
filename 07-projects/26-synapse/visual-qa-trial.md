# Visual QA trial — prompts and joint review

_Written 2026-10-23 on Sean's ask. Status: **running under D144** ([decisions](https://github.com/snds/synapse/blob/main/docs/plan/decisions.md#d144)). Visual QA is provisionally approved: the visual prove engine (`vqa`) may decide two checks in the Synapse gate while Sean and Claude review its real outputs together. Full approval waits for that review. Baton: [SESSION-STATE.md](SESSION-STATE.md)._

**In short:** run the prompts below yourself, on the Personal MBP, against work you know. Record your own verdict before you read the agent's. Then open a review session with Claude and go through each run. Each disagreement becomes a fix to the engine, a cuespec, a harness or a skill. If the engine ever passes something you can see is wrong, revoke it at once.

---

## 1. What is on trial

The harness is `visual-qa.literal`. It has six criteria. Two of them, c2 and c4, are what you're deciding to trust:

| Criterion | Level | Who decides it during the trial |
|---|---|---|
| c1 The capture names its app, build, viewport, theme and time | must | The gate's built-in check |
| c2 Every region matches the reference within a threshold scouted from the reference | must | **`vqa` (`vqa.literal-diff`)** once you trust it |
| c3 Text in the capture reads the same as in the reference | must | You. There is no OCR tool yet |
| c4 The check catches every defect planted in a copy of the reference | must | **`vqa` (`vqa.planted-defect`)** once you trust it |
| c5 No difference is waved through as expected without your sign-off | must-not | You |
| c6 Captures cover light and dark, at the narrowest and widest widths | should (reports only) | The gate's built-in check |

**Out of scope here.** Motion, 3D geometry and interaction have no harness yet. The engine can still measure them (`vqa motion`, `vqa geometry`, `vqa interact`). The engine-only prompts (§5) try those parts with no gate, so we learn whether each needs a harness.

## 2. Setup, once

1. **Get the tools.** Run `cd ~/Projects/synapse && git pull && cargo build -p sy`, then `cd ~/Projects/workspace && git pull`. You need the vault from 2026-10-23 or later, which has `vqa evidence` and `--theme`.
2. **Check the engine.** Run `python3 ~/Projects/workspace/03-skills/visual-prove-engine/vqa.py doctor`. Captures need Playwright. Then run `vqa.py calibrate`: it should say `calibrated` (48 of 48).
3. **Read what you're trusting.** That's `03-skills/visual-prove-engine/vqa.tool.json` and `vqa.py`.
4. **Trust it.** Run `sy harness trust-tool ~/Projects/workspace vqa` at your terminal, or press Trust under Workspace checks on the Harnesses screen. This is the provisional approval in practice. Any edit to the tool untrusts it until you trust it again.
5. **Know how to stop.** `sy harness trust-tool ~/Projects/workspace vqa --revoke`, or Revoke on the same screen, sends both checks back to you at once.
6. **Evidence goes to `~/Projects/vqa-trial/<prompt id>/`.** That folder is outside every repo, so no project's code or history changes.

## 3. The run block (paste it under every gated prompt)

> Work under the Synapse harness `visual-qa.literal`, in ship mode. Change no product code.
> 1. Build the cuespec from the reference only. Scout its targets with the engine's own probes, never from the build. Record how in `_provenance`, with `assistance: "off"`.
> 2. Capture the build with `vqa capture <url> -o <file>.png --theme light|dark --app <app> --build <commit or version> --assistance off`. Take light and dark at the narrowest and widest widths the surface supports. If the surface has only one theme, say so and capture what exists.
> 3. Assemble the evidence: `vqa evidence ~/Projects/vqa-trial/<ID> <first capture> <the rest> --cuespec <cuespec> --supported-widths <narrowest>,<widest>`. The first capture is the one proved.
> 4. Gate it: `sy harness gate ~/Projects/workspace visual-qa.literal --evidence ~/Projects/vqa-trial/<ID> --task "<the prompt's first sentence>" --mode ship`.
> 5. After the first gate, don't edit the cuespec or the harness. If you think either is wrong, propose the change (`sy harness propose`) and say why.
> 6. Stop at the verdict. Write `REPORT.md` in the evidence folder with:
>    - the verdict exactly as the gate printed it;
>    - what you would fix first;
>    - anything you saw that no cue measured.

## 4. Gated prompts

Run these in order. The first two have known answers, so they test the engine before you rely on it.

### X1 — LCARS SYS47: three builds with known answers
- **QA effort:** literal match against a reference you've already judged. Earlier scores were v2 0.50, v3 0.81 and v4 1.0. The engine once refuted a false "pass" here.
- **Prompt:** "Re-run the LCARS SYS47 construction check through the gate. The reference is `07-projects/20-lcars-generative-interface/docs/construction/captures/S-SYS47-01.png` and the cuespec `S-SYS47-01.cuespec.json` beside it. Gate builds v2, v3 and v4 (`captures/S-SYS47-01_build_v*.png`) as three runs, X1-v2, X1-v3 and X1-v4. These are stills: write each capture's manifest with `--theme dark --app lcars --build v2|v3|v4`, reusing v4's existing manifest fields." Then paste the run block.
- **Watch for:**
  - v2 and v3 should fail c2, and v4 should pass it.
  - Do you still agree v4 looks right? A v4 pass you disagree with is the first course correction.
  - c6 will report that only dark exists. That's expected; note it.

### L4 — Legion blind planted defects
- **QA effort:** do the detectors catch defects in real imagery, not just synthetic fixtures? This is the strongest single trust test.
- **You prepare it, the agent doesn't:**
  - Take two galaxy-map captures from https://snds.github.io/legion/ at one width.
  - Copy one, and plant two to four defects in an image editor. Ideas: nudge a HUD panel 3–4 px, shift a label color slightly, delete one label, soften a border.
  - Write down what you planted. Don't share it.
  - Hand over the untouched capture as the reference and the edited one as the build.
- **Prompt:** "The folder `~/Projects/vqa-trial/L4-input/` holds a reference capture and a build capture of Legion's galaxy map. Find every difference that matters. Scout the cuespec from the reference only." Then paste the run block.
- **Watch for:**
  - Every planted defect should show as a failing cue.
  - A defect it misses is the most important finding of the trial: it becomes a new planted case in `vqa calibrate`, then a detector fix.
  - A false fire on an untouched region matters too.

### L1 — Planet Lab orbital view against its northstars (expected to fail)
- **QA effort:** an honest fail on a 3D scene. Planet Lab's own review says FAIL: coarse coast geometry, contour-like banding and moiré, synthetic city footprints.
- **Prompt:** "Visually check the Independent Planet Lab's orbital view against its northstar references. Read `~/Projects/Legion/planet-lab/docs/VISUAL-REVIEW.md` first. Start the preview on port 5188 and capture the fixed orbital poses at 1920×1080, balanced quality. Take the latest accepted capture in `evidence/revision-2/` as the reference only if `VISUAL-REVIEW.md` names it as one; otherwise use the northstars it names. The scene has one theme." Then paste the run block.
- **Watch for:**
  - The gate should fail c2, and the failing cues should line up with the faults `VISUAL-REVIEW.md` already lists.
  - **A pass here is a red flag.** Revoke and bring it to the review.
  - WebGL in headless Chromium may render through software. Check that the manifest names its renderer.

### L3 — Galaxy map HUD: deployed build against your local one
- **QA effort:** regression. The deployed site is the reference and your local checkout is the build. HUD text is read by you (c3).
- **Prompt:** "Check that my local Legion galaxy map matches the deployed one at https://snds.github.io/legion/. Run the local build from `~/Projects/Legion` (don't change it; if the working tree has changes, use them as they are and say so). Compare the default view and one zoomed-in system view, at the narrowest and widest widths the HUD supports." Then paste the run block.
- **Watch for:**
  - With no changes in the build, c2 should pass. If it doesn't, either something really differs or the engine is noisy. Both are worth knowing.
  - Read the HUD labels yourself and record c3 on the Harnesses screen.

### U1 — Unicron Button: the full state matrix
- **QA effort:** component state matrix (variants × states), light and dark, narrow and wide. This is the everyday design-system check.
- **Prompt:** "Visually check Unicron's Button in the playground against its reference: every variant in default, hover, focus-visible, active and disabled, light and dark. Use the Figma library frame if there is one, otherwise the documented reference image in `~/Projects/unicron`. Hover, focus and active states need the playground's forced-state view or a per-state capture; say which you used." Then paste the run block.
- **Watch for:**
  - Focus rings and disabled contrast are where references and builds most often drift. Did the cues cover them?
  - Anything "uncued" in the report is a gap in the cuespec. It isn't a pass.

### U3 — Synapse Harnesses screen, dense data
- **QA effort:** a dense, text-heavy screen built on Unicron. This doubles as part of your in-depth review of the Harnesses screen.
- **Prompt:** "Visually check the Synapse app's Harnesses screen on sample data (`cd ~/Projects/synapse/app && npx vite --port 5199`, then open `/harnesses`) against a reference capture of the same screen from `main` at 2026-10-23. Light and dark, narrowest and widest window." Then paste the run block.
- **Watch for:**
  - c3 is a lot of text to read. Is reading it by hand bearable? Your answer sets the priority of a `vqa.ocr-match` tool.
  - Note anything about the screen itself for your review.

## 5. Engine-only prompts (no gate)

These try the engine's other measurements. No verdict counts. The question is whether its findings match what you see.

| ID | QA effort | Prompt (in Planet Lab or Legion; change no code) |
|---|---|---|
| L2 | Motion: stutter, teleport, flicker, banding during descent | "Record Planet Lab's continuous descent from orbit to 8 m as frames and run `vqa motion --frames`, plus `vqa perceive` on the frames where `VISUAL-REVIEW.md` reports moiré. Report every stutter, jump and flicker with its frame numbers." |
| L5 | 3D geometry across pinned views | "Capture the same Planet Lab terrain from three pinned camera poses and run `vqa geometry`. Does the landform stay consistent between views?" |
| L6 | Interaction: action → visible effect | "Write a `vqa interact` spec for the galaxy map: select a star, the system panel opens; hover a star, its label appears; press Escape, the panel closes. Capture before and after each step and verify it." |
| U2 | Theme parity and contrast | "Capture one Unicron playground page in light and dark and run `vqa compare` and `vqa perceive`. Report every element whose light and dark versions differ in more than color." |

**Watch for:** does each report match what you see when you watch it yourself? A true finding in an area no harness covers argues for a harness, such as `visual-qa.motion`. A false one argues for a detector fix first.

## 6. Joint review

**Where.** In a Claude Code session on the Personal MBP. That session can read `~/Projects/vqa-trial/` and the run records. A cloud session can't see your Mac's files. To start, say "review the visual QA trial" and point at this file.

**Your part, per run, before you read `REPORT.md`:**
1. Look at the captures in `matrix/` and the reference with your own eyes.
2. Write your verdict in the log below: pass or fail, plus what you see.
3. On the Harnesses screen, under Recent runs, decide c3 and c5 for the run.

You go first so the agent's report can't anchor what you see.

**Claude's part, together with you:**
- For each run, compare your verdict with the gate's.
- Sort every disagreement into one of these kinds:

| Kind | Meaning | What follows |
|---|---|---|
| cuespec | A target was scouted wrong, or a region wasn't cued | Fix the scouting procedure in the skill, not just this cuespec |
| detector | The engine missed a real defect or fired on a clean region | Add a planted case to `vqa calibrate` that reproduces it, then fix the detector. The edit untrusts the tool, so you trust the new version |
| harness | A criterion is wrong, missing or at the wrong level | `sy harness propose`, with the run as evidence; you apply it |
| skill | The agent captured, scouted or reported badly | Fix the skill (`visual-prove-engine`, `lead-visual-qa`) through self-improve |
| setup | Playwright, renderer or ports | Fix the steps in §2 or §3 |

- Each correction lands in the vault or the Synapse repo like any other change, and the log row links to it.

**Stop rule.** Revoke trust at once, and say so in the log, if:
- the engine passes c2 on something you can see is wrong; or
- it misses a defect you planted in L4.

Trust again only after the fix is in and the run is repeated.

**Full approval (proposed, for you to change).**
- At least six gated runs, X1 and L4 among them.
- No false pass.
- Every planted defect in L4 caught.
- Every disagreement sorted and either fixed or accepted by you.

Then D144 moves from provisional to approved.

## 7. CDS and Centric: why they're not here

You asked for prompts covering your CDS and Centric work too. The walls rule that out from this side:
- **Prompts.** Anything written in this vault is workspace content, and workspace content is never pasted into employer surfaces. That includes these prompts and the `vqa` engine itself, which lives in the vault.
- **Outputs.** CDS or Centric results can't come back here for joint review either. This session and the vault are personal.

What this trial does instead: Unicron's prompts cover the same kinds of QA effort that CDS work needs:
- U1: the component state matrix;
- U2: theme parity;
- U3: dense data screens;
- the X1 pattern, for a token or version regression.

Whether a visual QA practice should exist on the employer side is a separate question. It would have to be built from employer-side material, in an employer-approved Claude session in a Centric repo on the Work MBP (see [decision-claude-employer-surface](../../06-context/memory/decision-claude-employer-surface.md)).

## 8. Review log

| ID | Date | Run | Gate verdict | Sean's verdict (written first) | Agree? | Disagreement → kind → fix |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | No runs yet |
