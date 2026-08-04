---
name: fe-perf-harness
description: >-
  The performance measurement harness for frontend work — how to actually run Lighthouse /
  Lighthouse CI and Core Web Vitals budgets in a pipeline, what a budget number means, how to
  read a lab result without fooling yourself, and what to do when no runner is available. Use
  when the request is about the *measurement apparatus* rather than the optimization itself:
  "add a Lighthouse check to CI", "set up Lighthouse CI", "what should our performance budget
  be", "why does the LCP number move between runs", "gate the PR on bundle size / CWV",
  "lhci autorun", "assert a Lighthouse report", "performance budget failing the build",
  "lab vs field data", "CrUX vs Lighthouse". Spoke of lead-frontend-engineer. Ships
  scripts/fe_perf_budget.py — a stdlib-only budget assertion CLI that takes Lighthouse JSON
  (single run, several runs, or an LHCI directory), asserts category scores, timing metrics,
  and transfer sizes, and exits non-zero on failure. Do NOT use for diagnosing or fixing a
  regression (that is fe-performance), perceived-performance/loading-state design
  (ux-performance-perception), animation frame budgets (motion-performance), or backend TTFB
  and caching (be-caching-performance).
aliases: [fe-perf-harness]
triggers: [lighthouse ci, lhci, performance budget, web vitals ci, core web vitals gate, perf budget, bundle size budget, lab vs field, crux, performance regression gate]
tier: spoke
domain: engineering
hub: lead-frontend-engineer
prerequisites: [lead-frontend-engineer]
requires: [lighthouse]
surfaces: ["*"]
spec_version: "2.1"
---

# fe-perf-harness

The apparatus, not the craft. [[fe-performance]] holds the knowledge of *why* a page is slow
and how to make it fast; this spoke holds the **measurement rig**: how a number gets produced,
how much to trust it, how it becomes a gate, and how the gate degrades when the runner is
missing. Performance without a harness is opinion; a harness without judgment is a red build
nobody can act on.

| Concern | Skill |
|---|---|
| Why is LCP slow, what do I change | [[fe-performance]] |
| How do I measure it repeatably and gate on it | `fe-perf-harness` (this skill) |
| Where the check lives in the pipeline, alongside other CI gates | [[fe-testing]] |
| Does the *waiting* feel fast (skeletons, optimistic UI) | [[ux-performance-perception]] |
| Animation smoothness, frame budget, jank | [[motion-performance]] · [[visual-qa-motion]] |
| Server response time, CDN, caching headers | [[be-caching-performance]] |

## What a budget actually means

A budget is a **falsifiable claim about a specific route on specific hardware**, not a global
quality score. Four things must be pinned or the number means nothing:

1. **Which route** — the marketing home page and an authenticated 5,000-row table have nothing
   in common. Budget per route archetype.
2. **Lab or field** — Lighthouse is *lab* (one synthetic run, throttled, cold). CrUX and the
   `web-vitals` library are *field* (real users, real devices, 75th percentile). Lab catches
   regressions before merge; field tells you what users actually got. Neither substitutes.
3. **The throttling preset and device profile** — mobile emulation with 4× CPU slowdown is a
   different measurement than desktop. Changing the preset invalidates the history.
4. **Which percentile / how many runs** — a single lab run is noise. Take the median of 3-5
   (LHCI's `numberOfRuns`), which is what `fe_perf_budget.py` asserts when given several reports.

### Reference thresholds

Core Web Vitals "good" thresholds are field-data targets at the 75th percentile. They are a
**starting point** for lab budgets, not the same thing as them.

| Metric | Good | Needs work | Poor | Notes |
|---|---|---|---|---|
| LCP (Largest Contentful Paint) | ≤ 2.5s | ≤ 4.0s | > 4.0s | Field CWV; the load-speed proxy |
| INP (Interaction to Next Paint) | ≤ 200ms | ≤ 500ms | > 500ms | Field CWV; replaced FID. Lighthouse lab uses TBT as its proxy |
| CLS (Cumulative Layout Shift) | ≤ 0.1 | ≤ 0.25 | > 0.25 | Field CWV; unitless |
| TBT (Total Blocking Time) | ≤ 200ms | ≤ 600ms | > 600ms | Lab-only main-thread proxy for INP |
| TTFB | ≤ 800ms | ≤ 1.8s | > 1.8s | Mostly a backend/CDN number — route to `be-caching-performance` |

For enterprise B2B, the honest budget is often *worse* than the public "good" thresholds on
first load (large authenticated shells, heavy grids) and *stricter* on interaction (power users
spend hours in the app). Budget what matters for the cohort, then ratchet.

## Running the harness

### Local one-shot

```bash
# Produce a report (needs the lighthouse capability — see the degrade path below)
lighthouse https://app.example.com/orders --output=json --output-path=./lhr.json --quiet

# Assert it against a budget (stdlib only — no Node needed for this step)
python3 03-skills/fe-perf-harness/scripts/fe_perf_budget.py \
  --report ./lhr.json \
  --budget 03-skills/fe-perf-harness/configs/default.budget.json
```

### Lighthouse CI (the pipeline shape)

`lighthouserc.json` at the repo root, with the median of several runs and reports kept on disk:

```json
{
  "ci": {
    "collect": {
      "url": ["http://localhost:4173/orders"],
      "startServerCommand": "npm run preview",
      "numberOfRuns": 5,
      "settings": { "preset": "desktop" }
    },
    "upload": { "target": "filesystem", "outputDir": ".lighthouseci" }
  }
}
```

```bash
npx lhci autorun                     # collect N runs into .lighthouseci/
python3 03-skills/fe-perf-harness/scripts/fe_perf_budget.py \
  --report .lighthouseci/ --budget budgets/orders.json --out ./perf-out
```

Passing the directory makes the harness read every `lhr-*.json` and assert the **median**, so
one unlucky run cannot fail the build and one lucky run cannot hide a regression.

LHCI's own `assert` block can enforce thresholds too. Use this script instead when you want the
`/qa` report shape, the warn band, explicit INCONCLUSIVE handling, or budget assertion decoupled
from the collection step (for example asserting a report produced by a hosted runner or exported
from the PageSpeed Insights API).

### Budget file

`configs/default.budget.json` is the starting point. Three families, all optional:

| Key | Direction | Meaning |
|---|---|---|
| `categories` | minimum | Lighthouse category score 0-1 (`performance`, `accessibility`, `best-practices`, `seo`) |
| `metrics` | maximum | Audit `numericValue` — `largest-contentful-paint`, `total-blocking-time`, `cumulative-layout-shift`, `first-contentful-paint`, `speed-index`, `server-response-time`, `interaction-to-next-paint`, `interactive` (ms, except CLS) |
| `resource_sizes_kb` | maximum | Transfer size in KiB per resource type from the `resource-summary` audit (`script`, `stylesheet`, `font`, `image`, `total`) |
| `warn_margin_pct` | — | How close to a limit still warns (default 10%) |

The **warn band** is the point of the harness: a value inside the budget but within
`warn_margin_pct` of the limit reports `warn`. It is passing today and will break on the next
change, which is exactly when a team can still act cheaply. `--strict` promotes warnings to
failures for repos that want no headroom erosion.

### Script interface

| Flag | Meaning |
|---|---|
| `--report <path>` | Lighthouse JSON file, or a directory of `lhr-*.json`. Repeatable; several reports → median |
| `--budget <path>` | Budget JSON (above) |
| `--format markdown\|json` | stdout shape; markdown is the shared `/qa` report |
| `--out <dir>` | Also writes `perf_budget.md` + `perf_budget.json` |
| `--strict` | Treat `warn` as `fail` |

| Exit code | Meaning | CI reading |
|---|---|---|
| 0 | Every assertion passed (warnings allowed unless `--strict`) | Green |
| 1 | At least one assertion failed | Fail the build |
| 2 | INCONCLUSIVE — a budgeted metric is absent from the report | Fix the measurement; an absent metric is not a pass |
| 3 | Usage/input error (missing report, unreadable budget) | Fix the invocation |

Nested reports are handled: an `lhr`, `report`, or `lighthouseResult` wrapper (LHCI filesystem
target, PSI API response) is unwrapped automatically.

## Degrade path (no Lighthouse on this surface)

`lighthouse` is declared via [[capability-registry]] and its fallback is `degrade`, never a
silent pass. In order of preference:

1. **Assert a report produced elsewhere.** The assertion step is stdlib-only, so CI (or a
   teammate, or the PageSpeed Insights API) can produce the JSON and this script still gates on
   it. This is the primary degrade path and it loses nothing.
2. **Field data instead of lab data.** If the URL is public, CrUX gives 28-day rolling
   field CWV; the `web-vitals` library gives your own RUM. Slower feedback, more truthful.
3. **Browser DevTools by hand.** Performance panel trace + Coverage for unused bytes. Not
   gateable, fine for diagnosis — hand off to [[fe-performance]].
4. **State the gap.** If none of the above is available, say the budget was **not** verified.
   A "looks fine" is not a measurement, and `fe_perf_budget.py` deliberately has no mode that
   invents one.

## Gating policy (how not to make CI hated)

- **Median of 3-5 runs**, never one. Lab variance on a busy CI runner is large.
- **Warn before fail.** Ship the harness in warn-only mode for a sprint, learn the real
  variance, then set the failing threshold just above it.
- **Ratchet, don't relax.** When a run comes in comfortably under budget, lower the budget to
  lock the gain. Raising a budget to make a red build green converts a signal into decoration —
  if you must do it, record why in the budget file next to the number.
- **Budget the routes that matter**, a handful, not every page. A gate that takes 15 minutes
  gets disabled.
- **Separate the accessibility gate.** Lighthouse's accessibility category is a coarse
  by-product here; real structural a11y auditing belongs to [[a11y-audit-toolkit]], which drives
  axe-core directly and normalizes findings.
- **Pin the environment.** Same preset, same throttling, same Lighthouse major version — record
  it in the repo so a version bump is a deliberate re-baseline, not a mystery regression.

## Honest limits

- **Lab ≠ field.** A green lab budget with poor CrUX numbers means the lab profile does not
  match the users' hardware and network. Believe the field.
- **Synthetic runs miss the authenticated reality.** Budgets on a logged-out shell say nothing
  about a 5,000-row grid. Get the runner past auth (`extra_args` / LHCI Puppeteer script) or
  budget a route archetype you can actually load.
- **Scores are not linear.** A Lighthouse performance score is a weighted blend; chasing the
  number instead of a specific metric leads to fake wins. Budget metrics primarily, the score
  secondarily.
- **INP is hard to gate in lab.** Lighthouse reports TBT as a proxy; genuine INP needs field
  data or a scripted interaction. Do not claim an INP gate you don't have.
- **This harness measures load and weight, not smoothness.** Animation jank is
  [[motion-performance]] plus [[visual-qa-motion]]; a page can pass every budget here and still
  feel bad.

## File layout

```
fe-perf-harness/
├── SKILL.md                        # This file
├── scripts/
│   └── fe_perf_budget.py           # Stdlib budget assertion CLI (median-aware)
└── configs/
    └── default.budget.json         # Starting budget; copy next to the project and tune
```

## Related
- hub → [[lead-frontend-engineer]]
- peer ↔ [[fe-performance]] · [[a11y-audit-toolkit]]
