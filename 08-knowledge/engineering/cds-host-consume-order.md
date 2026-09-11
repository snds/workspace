---
tags: [engineering, cds, pages, overlay, exports, consume]
created: 2026-09-11
updated: 2026-09-11
status: working
confidence: high
sources: [saas-plm-prototype Pages build on PR 77, cds PR 34 squash, cds PR 35]
related_skills: [plan-ahead]
related_projects: []
relations:
  builds-on: ["[[centric-ui-local-against-cloud-dev]]", "[[contracts-first-delivery]]"]
---

# CDS host consume order: overlay ≠ Pages `main`

## For future agent
- **TL;DR:** Pages CI vendors **cds `main`**. A local `vendor/cds` symlink to an overlay worktree can
  export paths `main` does not. Vite then succeeds and Pages fails with
  `"./X" is not exported … from package @centric/ui`. Land the export on cds `main` first, then
  proto-consume. Squash-merges drop unpicked follow-up commits.
- **Key claims:**
  - *Timeless:* `@centric/ui/X` requires `package.json` `exports["./X"]` on the SHA CI clones.
  - *Timeless:* `ds-pin` overlay-ahead is a *note*, not a Pages contract.
  - *Dated 2026-09-11:* Toaster / `./sonner` and `SplitDragHandle` were the breakers on proto #77
    after cds #34 squash. Follow-up is cds #35. Proto keeps local Toaster + handle until that
    merges. Proto `scripts/cds-exports-check.mjs` is the gate (`npm run build` + `ds:check`).
- **As of:** 2026-09 · **Status:** current

---

## What failed

Proto re-exported `@centric/ui/sonner`. Local overlay had `./sonner`. cds `main` after #34 squash
did not. Pages `build` job cloned `main` → Rolldown error. Local `npm run build` could not see it.

## Order that holds

1. cds PR onto `main` (exports map + files)
2. Confirm `git show origin/main:packages/ui/package.json` has `./X`
3. Proto `export *` / wrap
4. Proto build (now runs `cds-exports-check`)

Do not invert 3 and 1 because the laptop looks green.

## What the pin check does not catch

`scripts/ds-pin.mjs` allows overlay **ahead** of the pin (co-dev). Ahead-with-unmerged-exports is
exactly the Pages trap. The new check compares **imports vs `origin/main` exports**, not SHAs.
