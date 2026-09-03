---
title: LCARS content groups and frame topologies
status: active
date: 2026-08-09
project: "[[20-lcars-generative-interface]]"
---

# Content groups and frame topologies

Shape primitives (`pill` / `bar` / `elbow`) answer *what a piece looks like*.  
**Content groups** answer *what a region is for*.  
**Frame topologies** answer *how the elbows/spines organize the page*.

Compose: pick a topology → place content groups → fill groups with legal shapes.

Sources: S-SYS47-01 (System47 MSD), Sean’s `sovereign_msd.mp4` (dual opposing spines), footer aesthetic detail crop, bridge-console patterns from the LCARS reference library.

---

## Frame topologies

### T1 — Bridge curve-spine

One dominant curve spine rises from a **left or right** vertical rail and runs to the **opposing top corner**. Controls and segments live **inside the vertical stem**. Main content sits in the open field the curve encloses.

Typical: ops / helm / tactical wall panels.

### T2 — MSD dual opposing spines (opposition conjunction)

Two curve spines meet or face each other at the **top center**, then run outward and often drop. The black gap between them frames a **focal viewport** (ship cutaway / MSD). Nested elbows may bracket left/right utility bays.

Examples: System47 Enterprise-E Schematics; `sovereign_msd.mp4` (U.S.S. ENTERPRISE ↔ SOVEREIGN CLASS).

### T3 — Classic left-rail + header elbow

Vertical left spine of stacked segments + top elbow into a header rail; content column to the right. Common TNG desk panels; our early generative shell approximated this only.

### T4 — Dense multi-panel mosaic

Several smaller framed panes (engineering wall). Treat as a **composition of T1–T3** cells, not a new shape language.

---

## Content groups (semantic regions)

Use these ids in Construction IR / Scene IR. They are **jobs**, not CSS class names.

| ID | Job | Typical contents | Motion |
|---|---|---|---|
| `identity.header` | Who / what console | Ship name, class, SYSTEM id, registry (NCC-…) | Locked |
| `frame.spine` | Structural chrome | Elbows, rails, stacked segments | Locked (except segment flip) |
| `focal.viewport` | Primary visual context | Ship MSD, sensor volume, medical scan | Asset may scrub/scan; chrome locked |
| `callout.layer` | Point into the focal | Connection **splines** + labels (`HOLODECK 3 / DECK 19`) | Splines may draw in; labels settle |
| `support.bay` | Processing beside/under the curve | **data-processing numerics** in the elbow pocket | Greeble tick on numerics |
| `support.controls` | Action cluster | Pill variants only (`action`, `numeric`, …). Not spine chrome. | Segment flip / static |
| `focal.title` | Name the focal subject | `MAIN DEFLECTOR DISH / TORPEDO LAUNCHER` | Locked |
| `footer.supplement` | Minimized accessible processes | More node blocks/pills, status chips | Tick / segment flip |
| `footer.minimap` | Orientation chip | Small silhouette / alt view | Optional slow idle |
| `chrome.aesthetic` | Passive density without lore duty | Stepped bars, hairline splines, barcode slices, gradients | Usually static |

### Data-processing numerics (support + footer)

Strings like `422 123`, `5 987 7886 1907`, `VER 2.5.01`, `41.791` read as **processing node IDs / subagent IDs / version tags**, not as user-facing metrics that must be “true.” They:

- Fill density and convey “system busy”
- May tick or reshuffle under motion doctrine
- Must still use legal shapes (pill or sharp bar), measured gutters, and northstar color samples

Do not invent fake charts when the northstar only shows these nodes.

### Aesthetic chrome (`chrome.aesthetic`)

Footer/detail strips may include stepped gradient bars, parallel hairlines, and mute segment clusters **with little or no diegetic definition** (“passive lore”). They still need a **structural** definition in the IR (segment heights, gutter, gradient direction) so the renderer can emit them — but recipes should not invent deep meaning for them.

Reference crop: `docs/construction/captures/S-SYS47-01_footer_aesthetic_detail.png`.

---

## MSD layout recipe (T2)

Reading order for System47 / Sovereign MSD:

```
identity.header L ── opposition ── identity.header R
         │                              │
         └── frame.spine (dual elbows) ─┘
                      │
              focal.viewport (schematic)
                      │
              callout.layer (splines + deck labels)
                      │
    support.bay (pills + numerics) · focal.title
                      │
     footer.supplement · footer.minimap · chrome.aesthetic
```

**Support bay** sits in the curve / mid band: left-side buttons + processing numerics; **focal.title** names what the viewport is showing.  
**Footer** is supplementary: more minimized processes + schematic minimap + optional aesthetic bar detail.

---

## Bridge layout recipe (T1)

```
frame.spine (vertical stem with embedded controls)
        └── curves to identity.header / top rail
focal.viewport + optional callout.layer in the open field
footer.supplement optional
```

---

## Mapping to Scene IR

| Content group | Scene IR (sys47.literal T2) | Notes |
|---|---|---|
| `identity.header` | region `identity.header` + opposing elbows | Dual SYSTEM 47 / NCC labels |
| `frame.spine` | elbows with `variant: 'opposing'` | Constant-thickness SVG paths |
| `focal.viewport` | region `focal.viewport` + schematic | Northstar asset preferred |
| `callout.layer` | still baked into raster / TBD overlay | Spline module next |
| `support.bay` | region `support.bay` (`kind: mode`) | Processing-node numerics |
| `support.controls` | live T3 `controlCluster` | Pill variants; not used on sys47.literal yet |
| `focal.title` | schematic `title` prop | May become own region later |
| `footer.supplement` | region `footer.supplement` | Minimized process blocks |
| `footer.minimap` | region `footer.minimap` | Silhouette crop |
| `chrome.aesthetic` | region `chrome.aesthetic` + `aestheticBar` | Passive stepped chrome |

`topology: 'T2'` on Scene IR drives grid + skips T3 header greeble.

Do not force T2 MSD into T3 left-rail shell. Topology is part of Literal fidelity.

---

## Construction IR extension (fields)

On each module / region, prefer:

```json
{ "contentGroup": "support.bay", "topology": "T2", "role": "processing-node" }
```

Roles for numerics: `processing-node` | `version-tag` | `control` | `status` | `aesthetic`.

---

## Variants (pack, 2026-09-02)

App catalog: `docs/COMPONENT-SYSTEM.md` + `src/catalog/system/`.

Pills are **controls**, not structure. Variants in the live T3: `action` / `action.short` / `action.wide` / `numeric` / `status.time` / `title.capsule`. Curves: `frame.tl|tr|bl|br`, `opposing` (T2), `nested` (pocket). Bars: `block`, `sliver`, `instrument`, `step`. Aesthetic chrome is a barcode + hairline that repeats the same breaks (SYS47 footer).

Spacing: 8px inside a family, 24px between content groups. Equal 8px everywhere fails the squint test.

## Related

- Shape primitives → app `docs/SHAPE-PRIMITIVES.md`
- Component / variant catalog → app `docs/COMPONENT-SYSTEM.md`
- Program thesis → `docs/program-thesis.md` (Intent axis = content groups)
- Northstar S-SYS47-01 → T2 MSD
- Sovereign alternate → `docs/construction/captures/sovereign-msd/`
