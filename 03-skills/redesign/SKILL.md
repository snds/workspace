---
name: redesign
description: >-
  End-to-end site/app redesign hub — extract an existing site's structure, set creative
  direction, prototype, and migrate to a fresh build. Use for whole-surface redesign and
  presales/client uplift work: "redesign this site", "modernize this landing page",
  "extract and rebuild", "uplift this page", "prototype a new direction for X",
  "design-forward rebuild". Also the explicit entry point for the `/redesign` operation
  grammar (`/redesign <verb> <target> [--modifiers]`). Wraps the adobe stardust pipeline
  (extract → direct → prototype → migrate → uplift) and impeccable's generative + live
  in-browser variant loop. Canonical owner of *generative redesign at surface scale*.
  Not for judging/measuring an existing interface (use /qa), not for a single-component
  build (use design-engineer / /figma), not for motion-only implementation (use /motion),
  and not for system token decisions (use /ds). This hub CREATES; /qa JUDGES.
user-invocable: true
argument-hint: "[extract|direct|prototype|migrate|uplift] [target: url|path|figma|page] [--live] [--style bolder|quieter|...] [--out <path>] [--dry]"
license: Apache-2.0
metadata:
  hub: true
  family: redesign
  poc: false
  version: 0.1.0
aliases: [redesign]
spec_version: "2.0"
tier: hub
domain: design
prerequisites: [design-foundations]
---

# /redesign — End-to-End Redesign Hub

The surface-scale creative hub. Where `/qa` judges and `/ds` decides, `/redesign`
**creates** — taking an existing site or page and carrying it through extraction,
direction, prototyping, and migration to a new build. It is a **wrapper** (three-way-contract
wrapper layer): it owns trigger vocabulary and verb dispatch, then delegates the depth to
the **adobe stardust pipeline** and **impeccable** (generative + live in-browser iteration).
It never duplicates a base's knowledge or reimplements impeccable's protocols.

## Operation grammar

```
/redesign <verb> <target> [--modifiers]
```

- **verb** — stardust's native pipeline verbs (below). Omitted → `uplift` (the one-shot).
- **target** — a URL, a local path, a Figma link, or `page` (the current preview).
- **modifiers** — `--live` (impeccable browser bridge), `--style <op>` (style operation), `--out`, `--dry`.

> **Domain-specific verbs, deliberately.** Unlike the other hubs, `/redesign` keeps
> stardust's own pipeline verbs rather than the canonical spine — because that pipeline
> *is* its grammar. Flagged in `invokable-operations-spec_v0.2` as the intentional exception.

### Verbs (stardust pipeline)

| Verb | Meaning | Default base route |
|---|---|---|
| `extract` | Pull an existing site's structure, content, and design signals | stardust `extract` (+ `distill`) |
| `direct` | Set creative direction — mood, references, art direction for the rebuild | stardust `direct` + `lead-art-director` |
| `prototype` | Generate a working prototype of the new direction | stardust `prototype` (+ impeccable generate) |
| `migrate` | Convert the existing build toward the new system/stack | stardust `migrate` / `prepare-migration` |
| `uplift` | One-shot: the whole pipeline end-to-end on a target (default verb) | stardust `uplift` |

### Modifiers

- `--live` — use **impeccable's browser bridge** for live, in-page work (see below). Run the poll as a **background task** (long timeout); the harness notifies on completion — never block the shell.
- `--style bolder|quieter|animate|colorize|typeset|delight|overdrive|…` — an impeccable style operation applied during `prototype`/`uplift`. (These ride as `--style`, not as separate verbs — same convention as `/qa polish --style`.)
- `--out <path>` — where extracted assets / prototypes / migration specs land.
- `--dry` — report the pipeline stages + bases that would run, without executing.

## Live mode (`--live`) — impeccable bridge, preserved & extensible

For live-page work, `/redesign … --live` uses impeccable's browser integration rather than
a static capture. **Two surfaces (do not bypass or reimplement these — the hub routes to them):**

1. **Passive detection** — the impeccable Chrome **DevTools extension** (MV3; content-script
   anti-pattern detector + service-worker port routing) detects UI anti-patterns on any page.
   Consumed as one input to `extract`/`direct`.
2. **Active iteration** — impeccable's **`live` mode** (local helper HTTP server with its own
   `serverPort`/`serverToken`; `live.mjs` / `live-poll.mjs` / `live-accept.mjs` / `live-resume.mjs`
   / `live-complete.mjs`; `/live.js`, SSE, `/poll`). The user selects an element in-browser and
   picks an action; the agent generates 3 variants, hot-swaps via HMR, and `--reply`s. Events:
   `generate · steer · accept · discard · exit`.

> **Hard preservation note (stocktake Finding 3).** Never strip or rewrite impeccable's
> `live`/extension wiring. This hub *routes to* the helper's poll/SSE protocol as the
> **base**.
> **Expansion seam:** additional workspace spokes (`visual-qa-accessibility`,
> `uid-visual-critique`, token-audit, `/qa`, `/ds`) can subscribe to the same `/poll`
> event stream so a selected element is evaluated/acted on by the right spoke — the hub
> **multiplexes spokes onto impeccable's bridge** via a thin wrapper. Build incrementally;
> keep the helper protocol intact.

## Disambiguation — who owns what (the precision contract)

`/redesign` is the canonical owner of **generative redesign at surface scale**. Defer when:

- **Judging/measuring an existing interface** (audit, contrast, "what's wrong") → `/qa`. `/qa` *judges*; `/redesign` *creates*. (`/qa polish … --live` also hands its live creative step to impeccable — same bridge, judge-side entry.)
- **A single component's build** → `design-engineer` / `/figma`.
- **System token/anatomy decisions** → `/ds`.
- **Motion-only implementation** → `/motion`.

When ambiguous ("make this better"), name the fork once: *judge/measure* (`/qa`) vs
*regenerate the surface* (stay in `/redesign`).

## Output

For `extract`, return the structure/content/signal inventory + asset paths. For
`direct`, the direction brief (mood, references, art-direction notes). For
`prototype`/`uplift`, the working prototype + where it lives + a follow-up `/qa audit`
recommendation to judge the result. For `migrate`, the migration spec/steps.

## Execution protocol

1. **Parse** verb/target/modifiers; default `uplift`.
2. **`--dry`?** Report the stardust stages + impeccable usage and stop.
3. **`--live`?** Start impeccable's live helper and run the poll as a **background task** (long timeout). Do not block.
4. **Acquire** the target (URL fetch / path scan / Figma export / live page).
5. **Run** the stardust stage(s); apply `--style` operations via impeccable where relevant. Preserve the live bridge end-to-end.
6. **Emit** the stage output.
7. **Hand off**: judge the result → `/qa`; productionize a single component → `design-engineer` / `/figma`; system token decisions → `/ds`.

## POC scope note

Sibling to `/qa`, cloned from the same wrapper shape per `invokable-operations-spec_v0.2`;
it is the Phase-E plugin wrapper over the adobe **stardust** pipeline + **impeccable**.
Thin by design — stardust and impeccable hold the depth; this hub carries the routing and
preserves the live/extension bridge.

## Related
- foundation → [[design-foundations]]
