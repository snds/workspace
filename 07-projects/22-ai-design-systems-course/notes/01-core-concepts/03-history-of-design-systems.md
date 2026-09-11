---
title: History of design systems
section: "Chapter 1: AI & Design Systems Core Concepts"
source: https://courses.bradfrost.com/courses/take/ai-design-systems-course/lessons/74085190-history-of-design-systems
duration: ~9m37s
status: noted
as-of: 2026-09-10
---

# History of design systems

Brad’s through-line: UI production went from **copy-paste / dotted-line references** to **solid-line dependencies**. The system is the connected graph, not the sticker sheet.

## Arc (as they tell it)

| Era | What changed |
|---|---|
| Early web / GeoCities | HTML/CSS only; handmade pages |
| 1996 *Creating Killer Websites* | Photoshop-sliced comps → code. Design file and production file become a *relationship* |
| Brand + multiple sites | Style guides → Photoshop → coded sites (still translation, not a dependency) |
| Web 2.0 / jQuery / Ajax | Interactive apps; more PSDs, more sites |
| 2007 iPhone | Native apps join the estate; still hanging off brand guides |
| 2010 Sketch + RWD (Marcotte) | Multi-viewport explosion |
| ~2009–2012 | Modular CSS/UI: Natalie Downe pattern portfolios, Nathan Curtis *Modular Web Design*, BEM, OOCSS, SMACSS; Bootstrap as a reaction to the pain |
| Angular / React | JS components; more surfaces to design for |
| 2013 Atomic Design + Pattern Lab | Hierarchical UI; Brad’s own stake in the ground |
| 2015 ES modules | First **solid line**: a component library can be an actual dependency of an app, not a reference |
| Cross-stack pain | One React library doesn’t serve Vue/other stacks; copy or reimplement |
| 2016–17 Figma (+ Sketch libraries) | Design-side components; solid lines in the design file too |
| Mid-2010s realization | Design assets + code + docs are all describing **one** collection of reusable UI — the org’s blueprint |
| Tokens (Jina) | Primitives that fan out to web, native, docs |
| Storybook | Code library becomes a connected surface |
| Web components | Presentational UI that can serve any web stack — more solid lines |
| Figma wins / Zeroheight / Supernova | Fewer tools, more connected docs |
| Child systems / “recipes” | Downstream product-specific systems. The happy-path architecture. **“Not exactly.”** (setup for what’s hard) |

## The actual claim

A design system is not a kit. It is the moment the org’s design, code, and documentation stop being parallel copy-paste jobs and become **one connected blueprint with real dependencies**. Tokens, web components, and library features are how the dotted lines turn solid.

## For Sean

This is Frost’s origin story for why bidirectional Figma↔code and token pipelines matter. Centric’s Vue + React + RN + Angular estate is exactly the “one React library can’t serve the org” problem he names — web components / headless as the proposed simplification. Don’t import web components as a conclusion yet; note it as *their* historical answer and test it against the later inspection stations and Centric constraints.
