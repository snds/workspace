---
type: decision
description: Documentation must show the thing with live components or a labeled schematic, not a text dump
created: 2026-09-14
confidence: high
relations:
  builds-on: ["[[davinci-ds-boilerplate]]"]
  relates-to: ["[[plain-language]]", "[[decision-pattern-uniqueness]]", "[[canonical-documentation]]"]
---

## For future agent

- **TL;DR:** A definition without a picture is unfinished. Use live shipping components; if the pattern does not ship yet, a labeled schematic of those primitives. Never a table of names as the example. Method: [[visual-first-documentation]]. **As of:** 2026-09-14 · **Status:** current

## Context

Pattern pages on CDS (composition, page templates, not catalogued) shipped as tables and callouts. Design-system docs are already text-heavy. Sean asked that every definition get a live example, and that this become standing for any documentation — not a one-off polish of those pages.

## Decision

Show first. Caption second. Highest honest rung on the live → composition → labeled schematic → Storybook-jump ladder. Do not screenshot host product into system docs. Do not draw a parallel kit when a real component exists.

## Rationale

A senior DS reader scans pictures to tell jobs apart. Prose cannot carry uniqueness. Iframes and code fences fail that scan. Rejected: "the table is the spec" and "Storybook embed counts as the example."

## Consequences

Agents write the picture before the paragraph. New docs pages do not merge as text-only. Pattern uniqueness and plain language still govern the labels on those pictures.
