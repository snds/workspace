---
type: decision
description: saas-plm-prototype is Olga+Sean's design iteration sandbox — never strip screens because centric-ui already has an equivalent; consume the DS, then lift net-new into centric-ui.
created: 2026-08-12
confidence: high
relations:
  builds-on:
    - "[[decision-externalize-everything-to-workspace]]"
---

## For future agent
- **TL;DR:** Prototype screens stay. The only semi-destructive proto work is swapping local design-system copies for `@centric/*`. Remaining proto-only components get catalogued, authored in centric-ui, then consumed back.
- **As of:** 2026-09-17 · **Status:** current

## Context — what forced a choice

The prototype→centric-ui migration recipes (`MIGRATION-PER-UNIT-DETAIL.md`) say DELETE proto copies of error-boundary, sidebar, media modals, detail chrome, Materials/Styles shells, etc., because centric-ui already ships RecordPage / GalleryWidget / AppErrorBoundary. Agents treated that as work to do *in the prototype repo*. Sean corrected this on 2026-08-12.

## Decision — what we chose

`saas-plm-prototype` stays a full, runnable design sandbox for Olga and Sean. We do **not** remove pages, shells, or feature chrome from it just because the product app already has an analogue.

The **only** semi-destructive work in the prototype is replacing local design-system copies with `@centric/ui` / `@centric/tokens` / `@centric/data-table` as dependencies (thin `export *` re-exports when APIs match). That is migrate/replace of the DS, not deletion of product UX.

The two repos have different jobs:

1. **Prototype** — iterate on product UX quickly. Keep the screens.
2. **centric-ui** — design-system write surface. Proto **consumes** `@centric/*` so the two look and behave the same.
3. **Lift** — remaining proto-only components/composites are **catalogued**, authored or composed in centric-ui, then proto consumes them. Do not leave them as a permanent second DS.

## Rationale — why, and what we rejected

Rejected: “centric-ui already has RecordPage, so delete proto MaterialsDetailView.” That confuses *product destination* with *design sandbox*. The separate proto repo exists so design can move faster than the product app. Stripping it because the product caught up destroys the iteration loop.

Rejected equally: treating leftover proto components as “leave them forever.” If it is shared UI, it belongs in centric-ui, then the prototype consumes it.

Accepted: DS consume was the allowed replace. Next is catalogue → lift into centric-ui → consume.

## Consequences — what this commits us to

- Ignore DELETE-the-proto-file recipes when the file is a screen, shell, or feature chrome.
- Do still replace local *design-system leaves* with `export * from "@centric/ui/…"` when APIs match.
- Any remaining component that should be in the DS gets a catalogue entry and a lift plan (centric-ui first, proto consumes). Snapshot 2026-08-12 below; refresh when a lift lands.

### Catalogue — still to land in / consume from centric-ui (refresh 2026-09-17)

**Consumed on proto `main` (2026-08-13):**
TypeTag / `statusTone` (#46). StatusPill, IconTooltip, CellIconButton, InfoHint, PaneCloseButton (#48). ChipMultiSelect + RichOptionList (#49; cui #297 `selectionMode`). Tailwind vendor `@source` (#50). `SplitPreviewLayout` + `ConsumerPreviewPane` wrap (#51).

**Stay local in proto (host extras / API mismatch):**
`SplitPreviewPane` chrome — quote compare needs `fullscreen`, `headerActions`, `bodyClassName`; package pane does not have them. `SplitDragHandle`. sheet, tabs, dialog, toggle-group, dropdown-menu (`asChild` vs `render`), popover (`anchor` + `asChild`), sonner.

**Lift into `@centric/ui` (shared composites proto invented):**
`SplitPreviewPane` fullscreen extras, searchable SingleSelect (or reuse cui SearchableSelect).

**Lift into centric-ui app/features (product patterns, not package primitives):**
CellComments, PrintColourAnnotator, CountrySelect, PartnerFacilityPicker, WhereUsedTable, FilterBar, InlineEdit, FormField, LandingGalleryCard, BulkSelect, UploadDropzone, CompositionBuilder, RequestStageStepper.

**Stay in the prototype (screens / one-offs, not DS):**
Materials/Styles/Partners/Colours page shells, side sheets, PreviewBodies, SourcingPanel, StubWorkspace, Header/Sidebar as proto chrome, token-lab specimens, compare matrices.

