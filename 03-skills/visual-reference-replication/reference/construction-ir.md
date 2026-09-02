# Construction IR — transcription schema

Machine-oriented structure extracted from a **named** UI/visual reference before implementation. Units: CSS px at the study capture scale (state the scale: e.g. `ref 1920×1080, study @1x`).

## Top level

```json
{
  "northstarId": "S-01",
  "sourcePath": "absolute/or/vault-relative path",
  "capture": { "width": 1920, "height": 1080, "dpr": 1, "format": "png" },
  "gutterPx": 4,
  "background": { "hex": "#000000", "lab": [0, 0, 0], "sample": [10, 10] },
  "frame": [],
  "segments": [],
  "modules": [],
  "typeSpecimens": [],
  "assets": [],
  "motion": [],
  "openQuestions": []
}
```

## Frame nodes

Each node is a structural chrome piece (spine, elbow, rail, void):

| Field | Meaning |
|---|---|
| `id` | Stable id (`spine.left`, `elbow.tl`, `rail.header`) |
| `kind` | `spine` \| `elbow` \| `rail` \| `void` \| `band` |
| `bbox` | `[x, y, w, h]` |
| `thickness` | Constant stroke/bar thickness if applicable |
| `radii` | `{ tl, tr, br, bl }` outer; note inner corner is usually 0 for LCARS elbows |
| `joins` | ids this piece abuts |
| `fillSample` | `{ hex, lab, xy }` from pixel probe |

**Elbow rule:** record outer radius and bar thickness separately. A CSS `border-radius` on a rectangle is **not** automatically a constant-thickness L; if the ref is a true elbow, the IR must say `geometry: "constant-thickness-arc"`.

## Segments

Clickable/decorative blocks on spines/rails:

| Field | Meaning |
|---|---|
| `id` | e.g. `rail.left.seg.03` |
| `parent` | frame id |
| `bbox` | |
| `fillSample` | |
| `label` | exact string or `null` |
| `labelAlign` | `start` \| `end` \| `center` |
| `role` | `nav` \| `status` \| `greeble` \| `alert` |

## Content modules

| Field | Meaning |
|---|---|
| `id` | |
| `kind` | `schematic` \| `gauge` \| `readout` \| `prose` \| `viewport` \| `pillCluster` \| … |
| `bbox` | |
| `z` | stacking order |
| `props` | kind-specific (meter value, title, callouts[]) |

## Typography specimens

Probe real glyphs in-ref:

| Field | Meaning |
|---|---|
| `text` | exact sample |
| `approxSizePx` | measured cap-height × scale factor |
| `case` | `upper` \| `mixed` |
| `weight` | |
| `tracking` | relative if measurable |
| `colorSample` | |

## Assets

| Field | Meaning |
|---|---|
| `id` | |
| `type` | `svg-trace` \| `raster` \| `r3f` |
| `sourceCrop` | `[x,y,w,h]` in reference |
| `status` | `traced` \| `placeholder` |

Placeholders must remain labeled until traced.

## Motion cues (from video)

| Field | Meaning |
|---|---|
| `target` | IR id |
| `behavior` | `segmentFlip` \| `greebleTick` \| `scanSweep` \| `gaugeSettle` \| `assetRotate` \| … |
| `periodMs` | |
| `locked` | siblings that must **not** move |

## Sampling discipline

1. Sample fills from the **interior** of a flat region, not anti-aliased edges.
2. Prefer Lab for Δe compares; store hex only as convenience.
3. Measure gutters as the black run between two filled edges at ≥2 places; if they disagree, record both and resolve before implement.
4. Never copy colors from a prior project token sheet until Δe-checked against **this** northstar.

## Output artifact location

Prefer: `07-projects/<project>/docs/construction/<northstarId>.ir.json`  
plus a human cue matrix markdown sibling.
