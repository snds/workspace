---
tags: [engineering, cds, pages, overlay, exports, consume]
created: 2026-09-11
updated: 2026-09-22
status: working
confidence: high
sources: [saas-plm-prototype Pages build on PR 77, cds PR 34 squash, cds PR 35, cds PR 46, proto PR 84]
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
  proto-consume. Squash-merges and merge-before-late-push both drop unpicked follow-up commits.
- **Key claims:**
  - *Timeless:* `@centric/ui/X` requires `package.json` `exports["./X"]` on the SHA CI clones.
  - *Timeless:* `ds-pin` overlay-ahead is a *note*, not a Pages contract.
  - *Timeless:* The host process is the **consume kit** (old name: federalization). Canonical agent hub is employer `cds/docs/consume-kit/` — do not copy it here.
  - *Dated 2026-09-11:* Toaster / `./sonner` and `SplitDragHandle` were the breakers on proto #77
    after cds #34 squash. cds #35 landed the exports. Proto #77 merged before later commits;
    #78 cherry-picked consume + `cds-exports-check` onto `main` (`adac92b`). Merge-before-late-push
    drops follow-ups the same way squash does.
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

## Later breakers after the export exists (2026-09-17)

- **Named export ≠ new subpath.** `IconSetProvider` from existing `./icon` passes `cds-exports-check`.
  Pages can still fail for other reasons.
- **Vite 8 / Rolldown CSR maps.** Phosphor's `./dist/csr/*` → `*.es.js` export is applied by Node,
  not by Rolldown. Host needs a resolve plugin. Proto `main` now has `phosphorCsrResolve()`.
- **`lint-ds` ratchet on new files.** Copying `text-neutral-*` / `text-blue-600` from an existing
  header control still raises the frozen count. Author new files in semantic tokens.
- **In-tree `_cds` vs sibling overlay.** Pages clones cds inside the proto workspace (`_cds`), so
  walk-up from data-table finds proto `node_modules`. A sibling worktree without `node_modules`
  fails `@centric/ui/fn` locally even when CI would pass.
- **Parallel main.** The CSR resolve landed on proto `main` while #84 was open. Merge `origin/main`
  before treating a green feature branch as mergeable.

## Host paint that is a CDS default (2026-09-21)

Proto #87 Pages `build` failed: the host imported `DisclosureChevron` from
`@centric/ui/DetailSection`, and that name is not on cds `main` (`cf55fb3`).
Proto `6bcd04e` restored a host `expand_more` so Pages can build. The chevron
is still not a CDS control.

Two overrides in that PR are parent defaults:

- `SheetContent` ships `gap-4` and an uncolored side border. Proto
  `ui/sheet.tsx` forces `gap-0 border-border`.
- `DetailSection` uses a 24px primary well, and the trigger pins the glyph
  to the corner. The proto draws a second 28px muted well with the glyph
  centered. A new named export belongs on the existing `./DetailSection`
  subpath, and it must be that centered control. Exporting the old icon as
  `DisclosureChevron` repeats the break.

Proto consume waits until those defaults are on cds `main`.

## See also

Host ButtonGroup / split-CTA paint is not an export-order problem. Inventory for cui
federalization: [[cds-host-buttongroup-realign]].

The host-level process (CDS as parent, not ShadCN) is the **consume kit** in
employer `cds/docs/consume-kit/` (plan file still named
`docs/plans/cds-host-federalization.md`). A proto instantiation lives in that
host as `docs/consume/`. Do not paste either here.

Which *repo* owns a visual or behavior fix (parent package vs host recipe) is
[[ds-parent-owns-shared-defects]] — a different gate from this pin/export order.
