---
title: Component Stickersheet Inventory (Figma)
status: shipped
updated: 2026-08-05
figma_file: o6o1ZuGHxDow2vHLuYXT6X
figma_page: Stickersheet Inventory
page_id: "426:60"
scope: review-matrix
icons: ignored
---

# Stickersheet Inventory — shipped

Page: https://www.figma.com/design/o6o1ZuGHxDow2vHLuYXT6X/Centric-SaaS-PLM---Design-System?node-id=426-60

## Delivered

- 6 shells with Colors + Density + Radii modes pinned
- ~61 sections / shell · ~1832 instances / shell
- Icons off; VARIANT × mode collections; orphans as single instances
- Built via Figma MCP `use_figma` (no separate Figma CLI — `@figma/mcp` npm package 404)

## Follow-ups

- Pagination Control mode nesting may be incomplete (4 cells vs expected mode×state)
- Optional: token-name callouts per section
- Re-screenshot Dark shells after scroll QA

## Scope (confirmed)

- **Matrix:** VARIANT property cartesian × component variable modes (Size / Variant /
  Shape / Layout / etc.) × **6 theme shells**
- **Shells:** Colors Light|Dark × Density Compact|Normal|Spacious
- **Icons:** ignored — all `*icon*` BOOLEAN props `false`; do not permute INSTANCE_SWAP
- **TEXT:** short sample labels; **SLOT:** leave default / empty
- **Components:** all public sets + orphans on Components page (skip private `_Foo/Bar`
  only when already covered by a public composite — prefer include private atoms in
  their own section for token review)

## Page structure

```
Page: Stickersheet Inventory
└── Root (auto-layout VERTICAL, gap density-bound)
    ├── Intro (title + legend)
    └── Shell ×6  (each sets explicit modes on Colors + Density collections)
        ├── Shell header (e.g. "Light · Compact")
        └── Per-component sections
            ├── Component name + axis legend
            └── Grid of instances (real components only)
```

Mode application on each shell:

- `Foundations / Semantics / Colors` → Light | Dark
- `Foundations / Semantics / Density` → Compact | Normal | Spacious
- `Foundations / Semantics / Radii` → same density mode name (keeps radius ladder in sync)

## Component mode collections to pin per instance (when present)

| Collection | Typical modes |
|---|---|
| Button / Variant | default, outline, secondary, … |
| Button / Size | default, xs, sm, lg |
| Button / Layout | default only (icon-only skipped — icons ignored) |
| Badge / Variant, Size, Shape | as defined |
| Switch / Size, Select / Size, Avatar / Size, Icon / Size | size subset |
| Progress / Status, Select / Item, Table / Row, Sidebar / Menu Button, … | state-like modes |

For sets where Size/Variant live as **variable modes** (not VARIANT props), nest a
sub-row per mode and put State VARIANT across columns.

## Build order

1. Create page + 6 empty shells with correct `setExplicitVariableModeForCollection`
2. Smoke: Button (default variant × sizes × states) in all 6 shells — screenshot QA
3. Batch public controls: Badge, Input, Textarea, Select, Checkbox, Switch, Radio, Label, Toggle, Alert, Avatar, Tabs, Separator, Progress, Slider, Toast, Tooltip
4. Batch chrome: Sidebar pieces, Table row/cell, Menu item, Pagination, Breadcrumb, Form Field
5. Orphans / composites: Card, Dialog, Sheet, Popover, Empty State, Skeleton, …
6. Legend strip listing bound token names sampled from one instance per section (optional second pass)

## Non-goals

- No hand-drawn shapes standing in for components
- No Token Spec wipe/rebuild
- No Material icon instance swaps
- No full BOOLEAN cartesian

## Exit criteria

- Page exists with 6 mode parents; toggling a shell’s modes is unnecessary if modes
  are pinned (visual review by scrolling shells)
- Every public component set appears at least once per shell with full VARIANT ×
  size/variant-mode coverage (icons off)
- Workspace note updated with page id + link
