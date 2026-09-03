---
tags: [design, motion, illustration, svg, film-ui, display-graphics]
created: 2026-09-02
updated: 2026-09-02
status: working
confidence: high
sources:
  - "Todd Marks / Images On Screen — Star Trek Picard demo reel v2 (youtube JiAeZfBbPHk, 2024). Audio reviewed; pixel frames blocked by YouTube 403."
  - "Andrew Jarvis — Picard S2 LCARS look-dev experiments (youtube Pj3Q6w-Epc4, 2023). Uploader description; no captions."
  - "Mike + Denise Okuda — Inside the Roddenberry Archive Ep. 2 (youtube 6DJDJri-aPI). Full English captions reviewed."
  - "Twisted Media / Maxon — Creating Effects to Connect Star Trek’s Past and Present (2022-06-21)"
  - "Warp Factor Trek — Playback Supervisor Todd Marks on Star Trek: Picard (2024-03-17)"
  - "Variety / IndieWire / SlashFilm — Picard Enterprise-D / LCARS playback reporting (2023)"
  - "AWN — Crushing the User Interface Designs of Oblivion (GMunk / Navarro Parker)"
  - "CGW — Oblivion 3D motion graphics; Intelligence Gathered (Sony / GMunk)"
  - "Pushing Pixels — Visual effects of TRON: Legacy and beyond (GMunk, 2011)"
  - "GSAP MorphSVG docs; Codrops SVG mask + ScrollTrigger (2026)"
  - "Motion (motion.dev) docs + AI Kit README (2026-09). Library formerly Framer Motion."
  - "LottieFiles/motion-design-skill; emilkowalski/skills animate; iart-ai/motion-design-skills; designrique/ai-graphic-design-skill (method only, not vendored)."
  - "skiln.co/mcp/ai-illustration → awesome-genmedia/skills categories/education/ai-illustration (method only)."
related_skills: [motion-graphic-systems, gd-display-graphics, gd-generation-tooling, lead-motion-designer, lead-graphic-designer, motion, visual-qa-motion, reference-video-review, visual-reference-replication]
related_projects: [20-lcars-generative-interface, 19-workspace-brain]
relations:
  builds-on:
    - "[[domain-constitutions]]"
    - "[[agentic-domain-constitutions]]"
  relates-to:
    - "[[visual-reference-replication-findings]]"
    - "[[measured-visual-verdicts]]"
---

# Display graphic motion systems

Testimony: Picard playback + Okuda archive + GMunk film UI + SVG technique
research. This note keeps the **transferable law**. LCARS is the hard exam,
not the scope.

## For future agent
- **TL;DR:** name a **register** (product chrome / graphic system / diegetic
  film UI / look-dev) before applying motion tokens. Compose the still so it
  reads at distance, then animate the few layers that earn motion. SVG:
  transform first, mask/stroke for reveal and draw, morph only when meaning
  changes.
- **Key claims:**
  - *Timeless:* a frame must communicate out of focus. Organization is the
    design; labels are layers.
  - *Timeless:* internal consistency over absolute consistency. If the
    system works this week, it works next week (Okuda / Roddenberry).
  - *Timeless:* "technology unchained" means the system does not overwhelm.
    Busy every-cell motion is a failed brief, in film or product.
  - *Timeless:* material (gel+backlight, OLED, hologram, live SVG) is part
    of the drawing. Do not paste a film grade onto a product canvas.
  - *Timeless:* practical playback when actors must see the graphic; post
    holograms are a different register. Record rejected look-dev.
  - *Timeless:* Illustrator → After Effects for 2D graphic motion; escalate
    to 3D only when the brief is volumetric (GMunk). Tool follows register.
  - *Dated 2023–24:* Picard S2/S3 chose OLED playback over Jarvis's seamless
    holo-black look-dev so original designers and TNG grammar could stay in.
  - *Pointer:* skills [[motion-graphic-systems]] and [[gd-display-graphics]].
    Literal clones still go through [[visual-reference-replication]].
    Emit live SVG via [[gd-generation-tooling]]; flattened plates measure,
    they do not construct.
- **As of:** 2026-09 · **Status:** current (doctrine; pixel-frame pass of
  the three videos still open)
- **Audience:** `for: agent`

---

## The gap this closes

Workspace motion skills were written for product chrome (200ms ease-out,
compositor only, no decoration). Workspace illustration skills were written
for icons, photos, and brand marks. Display graphics (HUDs, schematics,
playback panels) sit in the hole between those two. They look "decorative"
to the chrome constitution and "not an icon" to the vector hub. They are
neither. They are a **graphic system that lives in time**.

## Register (do not skip)

| Register | Motion job | Failure if misapplied |
|---|---|---|
| Product chrome | State change of a control | Loops feel like ads |
| Graphic system | Keep a composed instrument alive | Dead still, or every cell twitching |
| Diegetic / film UI | Read on camera; play on set | Website easing; pasted rectangles |
| Look-dev | Prove a path, then keep or kill it | Holo bloom mixed into a flat grammar |

Picard evidence: Jarvis look-dev (`Pj3Q6w-Epc4`) was holo-on-seamless-black.
Production chose playback. Marks reel (`JiAeZfBbPHk`): helm went from dead
transparency to live OLED so a press did something; the ship's back wall
became real displays; lighting behind panels had to blend with playback.
Twisted Media: S1 holograms vs S2/S3 practical; Okuda as grammar guide;
C4D + AE + Illustrator round-trip.

GMunk evidence: *TRON: Legacy* holographic density vs *Oblivion* elegant 2D
was a director brief, not a tool default. Light-table graphics were built
for in-camera 45-inch monitors. Sketch → Illustrator → After Effects;
Cinema 4D MoGraph when the graphic is 3D or audio-responsive.

## Still craft that survives time

From Okuda (`6DJDJri-aPI`):

1. **Family similarity** across signs, IDs, and panels.
2. **Reads at distance / defocus / occlusion.**
3. **Kodalith + gel + plexi + light** made cheap film look like a
   touchscreen. Complexity was not the trick.
4. **Polar motion:** spinner + gel on a static graphic. Digital cousin: a
   slow phase on a mask or gradient, not a bounce.
5. **Cell animation was rare** (Crusher DNA, flash on/off). Motion was
   expensive; they spent it where the story needed it.
6. **Label layers:** world-labels vs audience-readable. SD hid initials;
   4K does not. Literal product work inverts the "random numbers to save
   20 minutes" rule.

## SVG (product and generative)

- Default animate `transform` and `opacity`.
- Reveals: mask or `clip-path` on a finished drawing. Keep `viewBox` in
  0–100 units.
- Draws: `pathLength` + dash offset (or DrawSVG). Do not rewrite `d` per
  frame.
- Morphs: only when the *shape's meaning* changes. Pin `shapeIndex`.
- Hard bars / blinds: `shape-rendering="crispEdges"` plus a tiny overlap
  so AA does not open 1px gutters.
- Lottie/Rive: designer-authored loops, optimized, reduced-motion still
  required.
- Film delivery can be a movie. Web delivery of a live system should stay
  vector until something forces a raster.

## Catalog absorb (2026-09-02)

Marketplace packs stay outside the vault. Method that survived:

| Source | Kept | Rejected |
|---|---|---|
| LottieFiles motion-design | 1/3 travel; one personality; three layers on graphic/video only; never opacity-only on important chrome | "Always three layers" on product chrome |
| Emil Kowalski `animate` | Frequency gate; cheapest tool; never `scale(0)`; interrupt/retarget; hover pointer gating | Ease-out on exits (vault keeps ease-in) |
| iart motion-skills | Video register; stills-before-encode; title-safe + restack; one camera move | 50 social/TikTok/ecommerce packs |
| designrique ai-graphic-design | One archetype; IP path; photo-upscale trap; archive seeds | Tool-version matrices (Recraft V4, etc.) |
| [motion.dev](https://motion.dev) | Current library is Motion (`motion/react`); full `transform` under load; CSS `linear()` springs; `animateView()`; MotionScore as optional grade | Motion AI Kit as a second `/motion` doctrine; Motion UI section kits as style |
| [Skiln ai-illustration](https://skiln.co/mcp/ai-illustration) (genmedia) | Name job + audience; name the view (section / exploded / inset); generated type is not a caption | each::labs API, 562 model skills, avatars/NFT/coloring-page packs |

designskills.xyz and agenticskills.io/category/design are discovery catalogs. Impeccable and frontend-design are already wrapped. Do not install aesthetic packs into `03-skills/`.

## Generation path

Display systems are **live geometry**. Author a scene (elbow, bar, pill,
rect, sweep, rail, label, circle) and emit with
`09-tools/generate-display-svg.py`. A northstar PNG is a prove target.
Cropping it into `assetSrcset` tiles is not a graphic system.

Raster generators (Cursor image gen, Hugging Face, hosted APIs) stay on
the illustration-testimony path: job + audience + view, then overlay type.
They do not build HUD chrome.

## What this is not

- A license to animate every LCARS segment in a product table.
- A replacement for Literal IR when the brief is recreate-this-still.
- A new numbered framework. #02 + [[dc-motion]] + [[dc-illustration]] plus
  the two spokes are the stack.

## Open measurement hole

Full-resolution frame extraction of the three YouTube files failed (DASH
403 / PO token; a later sprite fetch was blocked). Doctrine above is
audio + published process + SVG literature. If local files arrive, run
[[reference-video-review]] and attach a pixel pass to this entry; do not
rewrite the law from vibes.
