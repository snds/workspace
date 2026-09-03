---
name: gd-generation-tooling
description: >
  How to produce illustration and display-graphic artifacts: live SVG from a
  display grammar, or raster generation only as testimony. Use when the work
  is generate svg, live svg, display grammar, illustration generation, graphic
  generation, emit a HUD, or someone reaches for flattened PNG cutouts as the
  constructed surface. Not the drawing language (gd-display-graphics), not
  photo/editorial art direction (gd-image-composition), not brand IP
  (gd-brand-identity), not Literal IR (visual-reference-replication).
aliases: [gd-generation-tooling]
triggers:
  - generate svg
  - live svg
  - display grammar
  - illustration generation
  - graphic generation
  - flattened png
  - emit hud
tier: spoke
domain: design
hub: lead-graphic-designer
prerequisites: [lead-graphic-designer]
related: [gd-display-graphics, gd-image-composition, gd-brand-identity, lead-vector-designer, visual-qa-graphic-design, visual-reference-replication, visual-prove-engine]
governed_by: [visual-qa-graphic-design]
defers_to: [lead-graphic-designer, visual-reference-replication, framework-06]
rigor_role: measurement
surfaces: ["*"]
spec_version: "2.2"
---

# GD — Generation Tooling

How a graphic is **emitted**. Foundations: [[design-foundations]]. Hub:
[[lead-graphic-designer]]. What to draw is [[gd-display-graphics]] or
[[gd-image-composition]]. This spoke is the produce path those skills drive.

L3: a scene either becomes live geometry or it is refused. Judgment after
emit is [[visual-qa-graphic-design]] (critique) and [[visual-prove-engine]]
when the brief is measured.

## Domain boundary

| Job | Owner |
|---|---|
| Grammar, family, reads-at-distance still | [[gd-display-graphics]] |
| Scientific / editorial / textbook figure | [[gd-image-composition]] |
| Mark + IP path | [[gd-brand-identity]] |
| Bezier cleanup of an approved raster | [[lead-vector-designer]] |
| Literal northstar transcription | [[visual-reference-replication]] |
| Emit live SVG / refuse cutouts / raster-as-testimony | **this spoke** |

## Two production paths

| Path | Use | Done looks like |
|---|---|---|
| **Live geometry** | HUD, schematic, instrument, diegetic panel, any graphic system that must stay editable | JSON scene → `generate-display-svg.py` → SVG with paths/rects/circles and real `<text>` |
| **Raster testimony** | Mood, editorial exploration, one illustration subject | Named job + audience + view → generator → overlay type in a layout tool → archive prompt/seed |

A northstar PNG is **measurement**, not construction. Slicing a flattened
plate (`assetSrcset`, cropped chrome, pasted tiles) is the failed path.

## Absolute bans

- Shipping flattened raster cutouts as the constructed display system.
- Using Cursor `GenerateImage`, Hugging Face image gen, or any plate collage
  to build HUD / LCARS / schematic chrome.
- Treating generated lettering as a caption. Overlay type.
- Vendoring an image API (each::labs, Midjourney, Recraft) as doctrine.
- Emitting `<image>`, `<foreignObject>`, or external `href` from this tool.

## Live geometry (default for display systems)

Legal kinds match the display-system primitive set: `elbow`, `bar`, `pill`,
`rect`, `sweep`, `rail`, `label`, `circle`. No one-off silhouettes in the
emitter. Project catalogs may refine path math; they may not add `image`. Those catalogs
are the pack-level **recipe** layer ([[agent-output-rails]]): pasteable legal
compositions. They stay in the pack. The emitter stays in `09-tools/`.

```
python3 09-tools/generate-display-svg.py --check 09-tools/fixtures/display-scene.hud-example.json
python3 09-tools/generate-display-svg.py --emit SCENE.json -o ARTIFACT.svg
python3 09-tools/generate-display-svg.py --self-test
```

Scene contract (minimum): `width`, `height`, `elements[]` with unique `id`,
`kind`, and `fill` (token name or `#hex`). Labels require `text`. Tokens are
`#hex` only. The example fixture is a generic instrument still, not a pack.

**Contrast**

| Failed emit | Required emit |
|---|---|
| Crop the northstar and tile the pieces | Name elbows / pills / labels; emit SVG |
| SVG that embeds a PNG plate | Paths + `<text>` only |
| Invented hex from a caption | Tokens from the pack / IR, then emit |

Literal briefs still transcribe Construction IR first
([[visual-reference-replication]]). This tool emits that IR. It does not
replace measurement.

## Raster testimony (illustration / mood only)

Do not run this path for a display system. If the job is a textbook figure,
editorial metaphor, or brand exploration:

1. Name job, audience, medium, and view ([[gd-image-composition]]).
2. One subject. One style. 15–40 words.
3. Confirm cost / tool with the user before a paid or hosted call.
4. Optional surfaces on this Cursor: Hugging Face image gen (degrade if
   absent); Cursor `GenerateImage` only when the user explicitly asks, never
   for charts or HUD chrome.
5. Overlay labels in the layout tool. Archive prompt + seed.
6. Identity marks still need Bezier + IP ([[gd-brand-identity]]).

Higgsfield and similar hosts stay unauthenticated unless Sean asks.

## Review loop

Generation is not a pass. After emit:

1. Squint / family check ([[gd-display-graphics]]).
2. Graphic craft critique ([[visual-qa-graphic-design]], [[06-qa-operating-model]]).
3. If Literal or "prove this build": [[visual-prove-engine]] cues, not a VLM paragraph.
4. Recursive / adversarial review (later session pattern): change the emit,
   re-measure, do not paste a flatter plate to close a cue.

## Execution protocol

1. Name the path: live geometry or raster testimony.
2. If display / HUD / schematic / pack exam: refuse cutouts; author a scene JSON.
3. `--check` the scene. Fix refusals. Then `--emit`.
4. If Literal: IR + cues already exist; this step only emits.
5. Hand the still to QA / prove. Do not call the SVG done from the CLI exit.

### Done-gates

- Path named; cutout path not used for a display system.
- Scene `--check` clean; emit has real text and no image nodes.
- Tokens come from the brief or pack, not from caption guessing on a Literal job.
- Raster jobs have job + view + archived prompt; type is overlaid.
- Review owner named (critique vs prove).

## Defers-to

- Workspace doctrine: [[13-domain-rigor-stack]] · [[lead-graphic-designer]] · [[06-qa-operating-model]]
- Literal packs: [[visual-reference-replication]] wins over invented grammar
- Drawing language: [[gd-display-graphics]] / [[gd-image-composition]]

## Related
- hub → [[lead-graphic-designer]]
- governed-by → [[visual-qa-graphic-design]]
- peer ↔ [[gd-display-graphics]]
- peer ↔ [[gd-image-composition]]
- peer ↔ [[gd-brand-identity]]
- peer ↔ [[lead-vector-designer]]
- peer ↔ [[visual-qa-graphic-design]]
- peer ↔ [[visual-reference-replication]]
- peer ↔ [[visual-prove-engine]]
