---
tags: [design-systems, consume, parent, host, cds, overlay]
created: 2026-09-22
updated: 2026-09-22
status: working
confidence: high
sources: [cds consume-kit, proto ImageLightbox / Combobox padding, 2026-09-22 lightbox + focus + field-px]
related_skills: [ds-advisor, plan-ahead, design-engineer]
related_projects: [02-centricPLM]
relations:
  builds-on: ["[[cds-host-consume-order]]", "[[abstraction-hides-its-dependencies]]"]
  relates-to: ["[[ai-and-design-systems]]", "[[contracts-first-delivery]]"]
---

# Parent owns shared component defects

## For future agent
- **TL;DR:** Before any component edit, name the **target layer**: parent design system or consuming host. Paint, geometry, focus, and tokens that every product will see belong in the parent. A host-only patch leaves the next app with the same bug.
- **Key claims:**
  - *Timeless:* Speak the layer in the first sentence (`parent (CDS)` / `host (proto)` / `host (cui)`). Do not start a dual-repo change without that label.
  - *Timeless:* Shared defect → parent package (wrap, token, lateral). Host gets a **recipe** or a **Pages-safe hold**, not a second primitive.
  - *Timeless:* Host-only when the job is domain policy, one-product chrome, or a hold until the parent SHA is on `main`.
  - *Timeless:* Landing order is still parent `main` then host consume ([[cds-host-consume-order]]). Layer-ownership and pin-order are two gates, not one.
- **As of:** 2026-09 · **Status:** current
- **Audience:** for: all

---

## Say it out loud

| You are changing… | Say | Repo |
|---|---|---|
| Default look or behavior when a host omits extras | **Parent** | The DS package (`@centric/ui`, tokens, stories, Fumadocs) |
| A recipe that composes public wraps (one product) | **Host** | The app (`proto`, `centric-ui`, later kit) |
| A new path/prop the host will import | **Parent first**, then host after `main` | Two PRs; do not invert |
| A hold so Pages still builds | **Host hold** | Local copy / `showCloseButton={false}` until parent merges |

If you cannot name the layer, you are not ready to write.

## Parent (every consumer)

Fix here when the bug would reproduce in any host that uses the wrap:

- Field geometry (radius, `--input-px`, compounded InputGroup padding)
- Focus chrome (one indicator; option highlight ≠ second field ring)
- Overlay chrome (lightbox gutter and close)
- Token and `FIELD_CONTROL` defaults
- Additive public API (`variant`, slot, export)

Dual path still applies: Storybook / docs + package in the same parent change.

## Host (this product only)

Stay here when:

- The job is domain policy (allow-create, record-trail mapping, filter rules)
- Chrome is route- or product-specific
- The parent API is not on `main` yet — keep a **hold**, do not import the new path

A host `className` that undoes a parent default is a parent gap. File it on the parent; do not let the override become the real primitive.

## Dated instance (2026-09-22)

These landed in **CDS**, not proto, so cui and later kits inherit them:

- Lightbox close 8px outside the media (`--dialog-lightbox-close-inset`), 16px from the viewport (`--dialog-lightbox-pad`), using the `icon-sm` ghost button
- Combobox/Select option outline quieted (field outline stays)
- InputGroup shell owns `--input-px`; inner input and addon are `px-0`

Proto only kept a Pages-safe lightbox X until that Dialog change is on CDS `main`.

## See also

Employer process (do not paste here): `cds/docs/consume-kit/`. Pin/export order: [[cds-host-consume-order]].
