---
name: ai-video-generation
description: >
  Generate video from text or images using hosted models (Veo, Seedance, Wan, and 40+ others) via
  the inference.sh belt CLI — text-to-video, image-to-video, animate-a-still, lipsync, upscaling.
  Use for marketing/social clips, explainers, product motion, and animated concepts. Account + cost
  involved — confirm before spending a call. Triggers: ai video, text to video, image to video,
  animate image, generate video, veo, seedance, wan, video generation, lipsync, b-roll, motion concept.
aliases: [ai-video-generation]
triggers: [ai video, text to video, image to video, animate image, generate video, video generation, veo, seedance, wan, lipsync, video upscale, b-roll, motion concept, ai animation]
tier: cross-cutting
domain: imaging
surfaces: ["*"]
requires: [inference-belt]
spec_version: "2.1"
---

# AI Video Generation (inference.sh)

Produce video from a prompt or a still via hosted generation models. This is the **generative**
counterpart to the rest of imaging — where [[imaging-foundations]] explains how a frame is *formed*
and [[img-cinematography]] how it's *composed*, this is how to *synthesize* motion content on demand.

> **Tool dependency — preflight first.** Requires the `inference-belt` capability ([[capability-registry]]).
> Probe `command -v belt`. If absent, there is no local fallback — surface the install
> (inference.sh CLI + `belt login`) and stop. **Always confirm with the user before running a
> generation** — each call costs money. See [[AGENTS]] → "Capability preflight".

## Choose the model to the job
- **Text-to-video** — a scene from a prompt (Veo / Seedance for fidelity; faster models for drafts).
- **Image-to-video** — animate an existing still / design frame (good for bringing a mockup to life).
- **Reference / lipsync / avatar / upscale** — pick the model that names the capability; the belt CLI
  lists what's available.

## Prompt like a cinematographer, not a search box
Borrow [[img-cinematography]] + [[img-photography]] vocabulary — **shot size, lens, camera move,
lighting, mood, pacing** — instead of vague adjectives. Specify aspect ratio and duration. Iterate
cheap (a fast model / low res) to lock composition, then spend on the final render.

## Workflow + hygiene
1. Confirm intent, model, and **estimated cost** with the user.
2. Draft → review the result honestly (artifacts, morphing, temporal flicker are the usual failures).
3. Iterate the prompt; escalate model/resolution only once the shot is right.
4. Save outputs as artifacts; note the model + prompt so a render is reproducible.

For *reviewing* reference footage rather than generating, see [[reference-video-review]].
