---
name: img-cinematography
description: >
  The camera language of moving images — shot sizes + framing, composition (rule of thirds,
  leading lines, headroom), camera movement (pan/dolly/crane/handheld), lens language,
  lighting setups (three-point, motivated, high/low key, mood), continuity (180° rule,
  eyeline), and color grading. Applies to game cameras, cutscenes, and trailers. Triggers:
  cinematography, shot, framing, composition, rule of thirds, camera movement, dolly, crane,
  three-point lighting, key light, mood lighting, color grading, 180 degree rule, shot list.
aliases: [img-cinematography]
triggers: [cinematography, shot, framing, composition, camera movement, dolly, crane, three-point lighting, key light, mood lighting, color grading, 180 degree rule, shot list, blocking]
tier: foundation
hub: imaging-foundations
domain: imaging
surfaces: ["*"]
spec_version: "2.0"
---

# Imaging — Cinematography

Where the physical camera ([[img-photography]]) becomes *storytelling*. The grammar of moving images —
applies to game cameras, cutscenes, trailers, and any in-engine "shot." Composition principle is shared with
[[found-composition]]; this is its motion-camera dialect.

## Shot language
**Shot size** carries meaning: wide/establishing (context, isolation), medium (relationship), close-up
(emotion), extreme close-up (intensity). **Angle**: low angle = power, high angle = vulnerability, eye-level =
neutral. **Framing**: headroom, lead room, the rule of thirds, leading lines, depth via foreground/mid/back.
A shot is a *choice about what the viewer feels*, not just what they see.

## Camera movement
Each move has a grammar: **pan/tilt** (reveal), **dolly/truck** (immersive, parallax), **crane/boom**
(scale, god's-eye), **handheld** (urgency, realism), **steadicam** (smooth follow), **zoom** (a lens change,
reads differently than a dolly). *Corollary:* in-engine, motivate the move and ease it — a dolly + DOF rack
focus reads cinematic; a linear lerp reads like a tech demo. Pairs with [[motion-3d-spatial]].

## Lighting for mood
Beyond physical correctness, light *directs the eye and sets tone*. **Three-point** (key/fill/rim) is the
base grammar; **motivated lighting** (every source has an in-world reason) sells realism; **high-key**
(bright, low contrast = upbeat) vs **low-key** (deep shadows, high contrast = drama/noir); **chiaroscuro**
for sculptural drama. Ratio of key:fill sets the mood. This is the artful counterpart to
[[img-photoreal-rendering]]'s physical correctness — and [[lead-art-director]]'s domain in practice.

## Continuity + grade
**Continuity** keeps space legible: the **180° rule** (don't cross the axis), consistent eyelines, screen
direction. **Color grading** unifies the look and steers emotion (teal-orange, desaturated grit, warm
nostalgia) — the final pass over a tonemapped image. For Legion: cutscene cameras, dynamic gameplay framing,
and trailer shots all draw on this.

## Related
- hub → [[imaging-foundations]]
- peer ↔ [[img-photography]] · [[img-vfx]]
