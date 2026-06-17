---
name: reference-video-review
description: >
  Turn reference footage into reviewable evidence — fetch a video (yt-dlp), extract triage frames
  and clips (ffmpeg), and review them through motion / 3D / craft lenses to drive visual decisions.
  The disciplined way to answer "make it look like that" when the target is a video. Spoke of the
  visual-QA toolkit. Triggers: reference video, extract frames, ffmpeg, yt-dlp, triage frames,
  frame extraction, video reference, screen recording review, motion reference, fly-through reference.
aliases: [reference-video-review]
triggers: [reference video, extract frames, ffmpeg, yt-dlp, triage frames, frame extraction, video reference, screen recording review, motion reference, flythrough reference, storyboard from video]
tier: spoke
hub: visual-qa-toolkit
domain: quality
requires: [ffmpeg, yt-dlp]
spec_version: "2.1"
---

# Reference Video Review

When the visual target lives in a video — a fly-through, a competitor's interaction, a film shot —
the way to act on it is to **decompose it into frames you can actually study**, not to eyeball it
once. This is the video arm of [[visual-qa-toolkit]]; the still-image review lens is the
[last-mile craft framework](01-frameworks/05-last-mile-craft-framework.md).

> **Tool dependency — preflight first.** Requires `ffmpeg` (hard) + `yt-dlp` (only to fetch remote
> video) — see [[capability-registry]]. Probe `command -v ffmpeg`. If missing, there's no portable
> fallback for frame extraction — surface `brew install ffmpeg yt-dlp` (or the platform equivalent)
> and stop. If the user supplies a local file, skip yt-dlp. See [[AGENTS]] → "Capability preflight".

## The method (proven on real work)
This is exactly how the Legion galaxy pass found its 7 structural rewrites ([[threejs-galaxy-visualization]] #6):
1. **Get the video local** — `yt-dlp <url>` (or use the user's file).
2. **Extract triage frames** — `ffmpeg -i in.mp4 -vf fps=1/2 frame_%03d.png` (or an N-step even sample
   across the duration). Pull more frames around the moments that matter.
3. **Review through three lenses at once** — **motion design** (camera dynamics, easing, transition
   rhythm), **3D / engine** (LOD, particles, volumetrics, performance), **craft / effects** (geometry,
   occlusion, lighting). The *cross-product* of lenses surfaces gaps a single lens misses.
4. **Turn observations into a build list**, not vibes — each frame → a concrete, checkable decision.

## When to use
- "Make the galaxy fly-through feel like this clip" → frames → camera/easing/LOD decisions ([[game-scale-traversal]]).
- Competitor interaction teardown (the moving counterpart to [[web-automation]]).
- Extracting a storyboard / key poses from motion reference for [[img-cinematography]] work.

## Discipline
Sample enough frames to be fair to the reference (one screenshot lies); name what each frame proves;
keep the extracted frames as artifacts so the review is reproducible.

## Related
- hub → [[visual-qa-toolkit]]
