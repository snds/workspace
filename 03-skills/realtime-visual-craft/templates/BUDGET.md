# BUDGET.md — Frame Budget Contract

> Allocate pass costs **before** adding look. Numbers from harness JSON, not FPS-counter vibes.
> Companion: `RENDER.md` · doctrine: `realtime-render-performance` · framework #12.

---

## Targets

| Metric | Target | Floor / notes |
|---|---|---|
| Display refresh | (e.g. 60 / 120 / 144 Hz) | Uncapped by default |
| FPS floor | **60** | Worst frame, not average |
| Real GPU budget @ 60 Hz | ~14–15 ms | After ~1.5–2 ms browser overhead |
| Input-to-photon | (project target) | Co-equal with FPS |
| Optional user frame cap | ☐ Off by default | Settings only; never hard-wire low |

**Weakest supported GPU** (design floor against this):

-

---

## Pass allocation

Fill planned ms **before** implementing. Update with measured ms after `budget`.

| Pass / system | Planned ms | Measured ms (pose) | Measured ms (flythrough) | Notes / release valve |
|---|---|---|---|---|
| Geometry / cull | | | | |
| Opaque / GBuffer | | | | |
| Shadows | | | | |
| Lighting / GI | | | | |
| Atmosphere / volumetrics | | | | |
| Transparent / particles | | | | |
| Post (bloom, tonemap, TAA…) | | | | |
| UI / compose | | | | |
| **Headroom** | | | | DRS / quality tiers |
| **Total** | | | | Must fit real budget |

---

## Official measurement points

| ID | Pose or path | Harness command / URL | Artifact path |
|---|---|---|---|
| M01 | | | |
| M02 | | | |

---

## Release valves (ordered)

Cheapest first. Name what each costs in look:

1. Dynamic resolution / internal scale
2. Shadow cascade / resolution cut
3. GI / probe update rate
4. Volumetric step count / resolution
5. Post quality (bloom mips, TAA samples)
6. …

**Never:** silently drop a northstar-critical cue to hit the number without updating `NORTHSTAR.md` / fidelity contract.

---

## Regressions log

| Date | Change | Worst-frame before → after | Action |
|---|---|---|---|
| | | | |
