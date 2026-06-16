---
name: img-photography
description: >
  The camera as a physical instrument — the exposure triangle (aperture, shutter, ISO),
  the sensor + dynamic range, the lens (focal length, field of view, depth of field, bokeh,
  aberrations), white balance, and why HDR capture + tonemapping exist. The basis for a
  physically-based virtual camera. Triggers: exposure, aperture, f-stop, shutter speed, ISO,
  depth of field, bokeh, focal length, field of view, dynamic range, white balance, EV,
  sensor, lens, motion blur.
aliases: [img-photography]
triggers: [exposure, aperture, f-stop, shutter speed, iso, depth of field, bokeh, focal length, field of view, dynamic range, white balance, ev, sensor, lens, motion blur]
tier: foundation
hub: imaging-foundations
domain: imaging
surfaces: ["*"]
spec_version: "2.0"
---

# Imaging — Photography (the camera)

How a camera turns light into an image. A virtual camera that mimics these controls is what makes a render
read as a *photograph*, not a CG image. Builds on [[img-optics-light]].

## The exposure triangle
Three controls trade off to set how much light reaches the sensor:
- **Aperture (f-stop)** — the iris. Controls light *and* **depth of field** (wide/f-1.4 = shallow DOF,
  creamy background; narrow/f-16 = deep focus). Each stop halves/doubles light.
- **Shutter speed** — exposure *time*. Controls light *and* **motion blur** (fast freezes; slow streaks).
- **ISO** — sensor gain/sensitivity. Raises brightness *and* **noise**.
Exposure is measured in **EV (stops)**; "one stop" = 2× light. Three controls, one brightness — every photo
and every good virtual camera balances them.

## Sensor + dynamic range
The sensor has finite **dynamic range** (the ratio between the brightest and darkest it captures). Real
scenes exceed it, which is *why* HDR exists: capture/compute in high dynamic range, then **tonemap** down to
the display. Highlight roll-off and shadow detail are the signature of a real camera (and a good tonemapper —
see [[img-photoreal-rendering]]).

## The lens
- **Focal length** sets **field of view** and perspective: wide (24mm) exaggerates depth/distortion; long
  (85mm+) compresses + flatters (portrait look). The "feel" of a shot is mostly lens choice.
- **Depth of field + bokeh** — the out-of-focus rendering; shaped by aperture, focal length, distance.
- **Aberrations** (chromatic fringing, vignetting, distortion, lens flare) read as "real camera" — tasteful
  amounts sell realism; overdone, they're a cliché.

## White balance + the virtual-camera takeaway
Light has color temperature (warm tungsten ~3200K, cool daylight ~6500K); **white balance** neutralizes it.
In a 3D engine, model the camera physically: linear/HDR pipeline → exposure (EV) → tonemap → encode; add DOF,
motion blur, and subtle lens effects as post. That chain is the difference between "CG" and "shot on camera."

## Related
- hub → [[imaging-foundations]]
- peer ↔ [[img-cinematography]]
