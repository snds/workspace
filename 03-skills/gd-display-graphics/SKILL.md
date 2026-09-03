---
name: gd-display-graphics
description: >
  Technical and display illustration for interfaces that ARE the graphic:
  HUD / schematic / control-surface / playback / diegetic panels, not icons
  and not photographic art direction. Use when the conversation touches:
  display graphics, technical illustration, HUD illustration, schematic
  illustration, control surface graphic, film UI illustration, playback
  graphic, okudagram, diegetic interface graphic, instrument panel graphic,
  status rail illustration, vector UI illustration, family similarity across
  signs and panels, reads-at-distance graphic systems. Not for icon metaphor
  (lead-icon-artist), path interpolation for fonts (lead-vector-designer),
  photo/illustration style briefs (gd-image-composition), or how the graphic
  moves (motion-graphic-systems).
aliases: [gd-display-graphics]
triggers:
  - display graphics
  - technical illustration
  - hud illustration
  - schematic illustration
  - control surface graphic
  - film ui illustration
  - playback graphic
  - diegetic interface graphic
  - instrument panel graphic
  - vector ui illustration
tier: spoke
domain: design
hub: lead-graphic-designer
prerequisites: [lead-graphic-designer]
related: [gd-image-composition, gd-generation-tooling, motion-graphic-systems, lead-vector-designer, visual-qa-graphic-design]
defers_to: [framework-01, lead-graphic-designer]
rigor_role: load-chain
surfaces: ["*"]
spec_version: "2.2"
---

# GD — Display Graphics

Specialist lens for **display illustration**: graphics whose job is to look
like a working instrument, schematic, or in-world interface. Foundations:
[[design-foundations]]. Hub: [[lead-graphic-designer]]. This spoke is
medium-specific application of graphic first principles to that job.

L4 spoke. Motion of the same graphic is [[motion-graphic-systems]]. Literal
recreation of a named still is [[visual-reference-replication]].

## Domain boundary

| Question | Owner |
|---|---|
| Photo / editorial / scientific / textbook illustration | [[gd-image-composition]] |
| Icon metaphor at 24px | [[lead-icon-artist]] |
| Bezier / interpolation-safe paths | [[lead-vector-designer]] |
| How the display *moves* | [[motion-graphic-systems]] |
| What the display *is* (grammar, hierarchy, family) | **this spoke** |
| Pixel-accurate clone of a northstar | [[visual-reference-replication]] |
| Emit the still as live SVG (not plate cutouts) | [[gd-generation-tooling]] |

An icon is a hyper-simplified composition. A display graphic is a **system
of compositions** that must still read as one family when the camera is wide,
soft, or blocked by an actor.

## The communication job

Illustration here explains, orients, or identifies. Style is in service of
that job ([[dc-illustration]]). Typical jobs:

- **Instrument:** status, mode, alarm. Color and enclosure carry state.
- **Schematic:** spatial relationship (ship cutaway, network, anatomy).
- **Control surface:** affordance clusters that look operable.
- **Wayfinding in-world:** door signs, panel IDs, labels that share a family.
- **Playback / film UI:** the same jobs, authored for camera distance.

If you cannot name the job, you are decorating.

## Reads at distance

Okuda, on TNG panel design (Roddenberry archive walkthrough `6DJDJri-aPI`):
even in a wide shot, out of focus, or behind an actor, the organization must
stay obvious. That is the acceptance test for this spoke.

**Contrast**

- **Bad:** Hairline labels, eight type sizes, and a unique corner treatment
  on every module. Reads as noise at 20% scale.
- **Good:** Two or three enclosure types, one type family, color used as
  role not as variety. The silhouette of the system is recognizable in a
  squint.
- **Why:** Family similarity across door signs, informational signs, and
  panel IDs is what made LCARS read as a world, not a sticker sheet.

Production implication: design the **squint silhouette** first, then add
labels the camera will never read. Those labels still need a rule (see
Label layers).

## Family, not a kit of parts

A display language is a small set of legal shapes and joins, reused.

- Name the legal silhouettes (bar, pill, elbow, rail, callout, schematic
  line). Illegal shapes are refuse cases for that pack.
- Keep joins and radii on a ladder. One "special" radius per screen is a
  leak.
- Color is role (structure / value / alert / annotation), not decoration.
- Repeat the same ID block, timestamp, and status cluster so the eye learns
  the grammar.

This is graphic identity applied to instruments. It is not a component
library until [[ds-advisor]] encodes it. Do not skip the graphic resolution
and jump to tokens.

## Material is part of the drawing

TNG panels were Kodalith (high-contrast lith film) + colored gels +
backlight + plexi. The "high-tech touchscreen" was lighting and layers, not
complexity. Picard replaced dead transparencies with OLED playback and had
to **re-solve the material** (black level, off-axis, blend with practical
light).

When specifying a display graphic, name the material stack:

| Stack | What it does to the drawing |
|---|---|
| Backlit film / gel | Color is light, not ink. Edges bloom. |
| OLED / emissive | True black, high chroma. Off-axis shift. |
| Printed / reflected | Ink on substrate. No self-illumination. |
| Hologram / additive | Volume, not a plane. Different register. |
| Live SVG on a product screen | Pixels, not gels. Fake the bloom only if the brief asks. |

Do not copy a film still's grade onto a product screen without a production
path ([[dc-illustration]] refuse).

## Label layers

Okuda's practice: buttons needed labels for the *world*, knowing the
audience would not read them at intended distance. Initials and in-jokes
were safe at SD and risky at 4K.

Split labels into layers:

1. **Camera-primary:** must read at the stated distance. Few, large, role-colored.
2. **Diegetic texture:** present so the world feels labeled. May be illegible
   on purpose.
3. **Literal / product:** if this graphic is a real UI or a Literal recreation,
   every visible string is accountable. Random numbers are a film-schedule
   tactic, not a product tactic.

Okuda spent 20 minutes on fake-accurate labels only when it got the set
closer to shoot. Invert that for Literal digital work: time goes into
measured geometry and real strings, not into inventing lore.

Version crumbs (TNG `40271` as "OS version," actually a cost center) are
optional diegetic metadata. Do not invent them as if they were a spec.

## Taping and cheap functional language

Graphic tape on props and walls produced "functional" cheaply. The lesson
is not "use tape." It is: **a consistent linear language** (weight, join,
interval) reads as engineered even when the content is thin. Prefer a
disciplined line system over illustrated greeble.

## Path craft when the drawing is a display

[[lead-vector-designer]] still owns nodes and booleans. For display graphics,
font-interpolation rules (extrema for hinting, 24px grid) are secondary.
Priorities shift to:

- Minimum nodes that survive scale and mask animation.
- Consistent path direction if strokes will draw on.
- Boolean cleanliness so a mask edge does not flicker.
- `viewBox` stability so motion can use 0–100 units.

## Execution protocol

1. Name job, audience, medium, viewing distance, and material stack.
2. Draw the squint silhouette (legal shapes only).
3. Assign color roles and type roles. Two type sizes before five.
4. Place camera-primary labels. Defer texture labels.
5. If the graphic will move, hand the still to [[motion-graphic-systems]]
   with a list of layers that *may* move.
6. If Literal, stop and run [[visual-reference-replication]] instead of
   inventing.
7. Emit via [[gd-generation-tooling]]. Do not assemble the surface from
   flattened asset cutouts.

### Done-gates

- Job and viewing distance stated.
- Squint test: organization survives desaturation and downscale.
- Legal shapes named; no one-off silhouettes without a reason.
- Label layers classified (camera-primary vs texture vs Literal).
- Material stack named; film bloom not pasted onto a product canvas
  without a decision.
- Fine-detail claims made at native resolution ([[10-perception-integrity]]).

### Absolute bans

- Using illustration to hide broken IA or an unreadable UI.
- Treating a film still as a component kit.
- Unique chrome on every module "for interest."
- Shipping hairline detail that dies at the intended distance.
- Encoding a half-resolved graphic language into a DS.

## Outputs

- Grammar card: legal shapes, color roles, type roles, material.
- Squint / family proof (downscaled still).
- Label-layer map.
- Handoff to motion or to Literal IR, as the brief requires.

## Defers-to

- Workspace doctrine: [[13-domain-rigor-stack]] · [[01-aesthetic-lens]] · [[lead-graphic-designer]]
- Literal packs: [[visual-reference-replication]] wins over invented grammar

## Related
- hub → [[lead-graphic-designer]]
- peer ↔ [[gd-image-composition]] · [[gd-generation-tooling]] · [[motion-graphic-systems]] · [[lead-vector-designer]] · [[visual-qa-graphic-design]]
