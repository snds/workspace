---
name: a11y-audit-toolkit
description: >-
  Instrumented accessibility audit toolkit — the structural (DOM/semantics/ARIA) measurement
  arm of accessibility work, the counterpart to visual-qa-toolkit's pixel measurement. Use when
  the request is to *audit* a page, view, story, or built artifact against WCAG rather than to
  reason about accessibility in the abstract: "run an accessibility audit", "axe this page",
  "pa11y", "Lighthouse accessibility score", "are there WCAG violations", "check ARIA / roles /
  labels / accessible names", "keyboard and focus-order audit", "accessibility CI gate",
  "VPAT evidence", "what's failing before we ship". Runs axe-core, pa11y, or Lighthouse's
  accessibility category — whichever is installed, in that preference order — and normalizes
  every runner's output into one finding schema (id, severity, rule, selector, message, wcag)
  with the shared /qa report shape and CI-usable exit codes. With no runner present it degrades
  honestly: a WCAG-oriented MANUAL_CHECKLIST plus stdlib static HTML checks, exit code 2, and no
  claim of automated evidence. Do NOT use for: color-contrast or color-vision measurement of a
  screenshot (that is visual-qa-toolkit), accessibility *judgment* on a design that isn't built
  yet (visual-qa-accessibility), implementation fixes (fe-accessibility), or conformance/VPAT
  reporting strategy (a11y-legal-compliance).
aliases: [a11y-audit-toolkit]
triggers: [accessibility audit, a11y audit, axe, axe-core, pa11y, lighthouse accessibility, wcag violations, aria audit, accessible name, keyboard audit, focus order audit, screen reader audit, vpat evidence, accessibility ci]
tier: cross-cutting
domain: accessibility
hub: lead-accessibility-architect
requires: [axe-cli, pa11y, lighthouse]
surfaces: ["*"]
spec_version: "2.1"
---

# a11y Audit Toolkit

A stdlib-first Python CLI plus config that turns "is this accessible?" into a measured,
repeatable, runner-agnostic audit — and that degrades into an honest checklist instead of
silence when no runner is installed.

This is the **structural** measurement arm of accessibility: the machine-checkable half of
WCAG that lives in the DOM (names, roles, states, labels, landmarks, heading structure,
frame titles, focus order hazards, zoom blocking). It exists because accessibility had no
measurement surface in this workspace — contrast and color-vision were measured by
[[visual-qa-toolkit]] and everything else was asserted from a lens skill. Measured findings
end arguments; asserted ones don't.

> **Automated rules find roughly 30-40% of real accessibility defects.** Exit code 0 means
> "no machine-detectable violation," never "accessible." The remaining 60-70% is the manual
> checklist, the assistive-technology pass, and the judgment lenses. Never report a clean
> run as an accessibility pass.

## Audit vs critique — which half you are in

The `/qa` verb distinction applies here exactly as it does for visual work, and this toolkit
sits entirely on the `audit` side:

| | `audit` (this toolkit) | `critique` (the lens skills) |
|---|---|---|
| Question | Does the artifact violate a stated rule? | Is this genuinely usable by disabled people? |
| Standard | WCAG 2.2 A/AA/AAA success criteria, runner rule sets | POUR, cognitive load, curb-cut reasoning, AT reality |
| Output | Findings with rule id, selector, WCAG criterion, severity | Judgment with population impact and a design change |
| Owner | `a11y-audit-toolkit` (+ `fe-accessibility` for fixes) | [[visual-qa-accessibility]] · [[lead-accessibility-architect]] spokes |
| Failure mode | False confidence — passing rules while excluding users | Unfalsifiable claims — "this feels inaccessible" |

Run the audit first (it is cheap and produces evidence), then critique what the audit
cannot see. An audit that isn't followed by a critique is the monoculture this toolkit
is meant to break, not extend.

## When to use this vs. `visual-qa-toolkit`

Both are measurement toolkits; they measure different substrates and **do not overlap**.

| Question | Toolkit | Why |
|---|---|---|
| Contrast ratio of text, borders, focus rings, chart series | [[visual-qa-toolkit]] (`qa_contrast`) | Measured from pixels — works on screenshots, Figma exports, and renders with no DOM |
| Does information survive deuteranopia / protanopia / tritanopia | [[visual-qa-toolkit]] (`qa_color_vision`) | Same: a pixel simulation, not a DOM property |
| Accessible name, role, state of a control | `a11y-audit-toolkit` | Only exists in the DOM/accessibility tree |
| Labels, landmarks, heading order, frame titles, duplicate ids | `a11y-audit-toolkit` | Structure, not appearance |
| Zoom/reflow blockers in markup (`user-scalable=no`) | `a11y-audit-toolkit` | Markup-level |
| Whether the *design* (not the build) is accessible | Neither — [[visual-qa-accessibility]] | Nothing to instrument yet |

Rule of thumb: **pixels → `visual-qa-toolkit`; DOM → `a11y-audit-toolkit`; intent → the lens.**
A pre-ship accessibility audit usually runs both and merges findings into one `/qa` report.

## Runners and the degrade ladder

The toolkit drives whichever runner the surface has. Capability ids resolve in
[[capability-registry]] (`axe-cli`, `pa11y`, `lighthouse`) — preflight them before promising
a measured run.

| Preference | Runner | Why this order | Detection |
|---|---|---|---|
| 1 | axe-core CLI (`@axe-core/cli`) | Best signal-to-noise, stable rule ids, explicit WCAG tags, per-node selectors | `axe` on PATH, else cached `npx --no-install @axe-core/cli` |
| 2 | pa11y | Emits WCAG success-criterion codes directly — convenient for conformance/VPAT evidence | `pa11y` on PATH, else cached `npx --no-install pa11y` |
| 3 | Lighthouse (`--only-categories=accessibility`) | Often already installed for performance work; axe-backed but coarser (audit-level, no WCAG tags) | `lighthouse` on PATH, else cached `npx --no-install lighthouse` |
| — | **degraded** | No runner: MANUAL_CHECKLIST + stdlib static HTML checks, exit 2 | always available |

Behavioral guarantees:

- **Nothing is installed implicitly.** `npx --no-install` only uses an already-cached package,
  so a run never silently pulls the network.
- **A failing runner falls through** to the next one, and the failure is recorded in the
  report's `notes` — a broken runner never reads as a clean page.
- **Degraded is loud, not quiet.** Exit 2, `"mode": "degraded"`, and a note naming the install
  command for this surface.

## Invocation

```bash
cd 03-skills/a11y-audit-toolkit

# Audit a URL with the best available runner
python3 scripts/a11y_audit.py --url https://app.example.com/orders --config configs/default.yaml

# Audit a built artifact (converted to a file:// target for the runner)
python3 scripts/a11y_audit.py --html-file ./dist/index.html --out ./a11y-out

# Force a runner (fails over to degraded if it isn't installed here)
python3 scripts/a11y_audit.py --url https://app.example.com --runner pa11y --level aaa

# Skip detection entirely and emit the checklist (design review, no build yet)
python3 scripts/a11y_audit.py --html-file ./page.html --runner manual --format json

# Degraded static pass over a remote page's served HTML (one opt-in HTTP GET, pre-JS DOM only)
python3 scripts/a11y_audit.py --url https://example.com --fetch-url
```

| Flag | Meaning |
|---|---|
| `--url` / `--html-file` | The target (mutually exclusive, one required). A local file is passed to runners as a `file://` URI |
| `--config` | YAML config; defaults are used when omitted (see `configs/default.yaml`) |
| `--runner auto\|axe\|pa11y\|lighthouse\|manual` | `auto` (default) walks the preference order; a named runner degrades rather than substituting silently |
| `--level a\|aa\|aaa` | Conformance target; also filters the MANUAL_CHECKLIST |
| `--format markdown\|json` | stdout shape (default `markdown`, the `/qa` report) |
| `--out <dir>` | Also writes `a11y_report.md` + `a11y_report.json` |
| `--fetch-url` | In degraded mode only, fetch `--url` over HTTP for static checks |

**Inputs come from the user.** Ask for the URL, the built file, the auth/viewport flags the
target needs (`runner.extra_args`), and the project's config path. Never hunt the filesystem
for a project's build output or a staging URL.

## Normalized finding schema

Every runner is flattened into the same record, so findings are comparable across runners and
across machines:

```json
{
  "id": "button-name#1",
  "severity": "blocker",
  "rule": "button-name",
  "selector": "button.icon-only",
  "message": "Buttons must have discernible text",
  "wcag": ["4.1.2"],
  "source": "axe",
  "help_url": "https://dequeuniversity.com/rules/axe/4.10/button-name"
}
```

`severity` is normalized into the `/qa` vocabulary so it can be merged with visual findings:

| Runner signal | Normalized |
|---|---|
| axe `critical` / `serious` / `moderate` / `minor` | `blocker` / `major` / `minor` / `nit` |
| pa11y `error` / `warning` / `notice` | `major` / `minor` / `nit` |
| Lighthouse score 0 with audit weight ≥ 7 / score 0 / partial score | `blocker` / `major` / `minor` |
| stdlib static check (degraded) | assigned per rule; always `source: static-html` |

The wrapper JSON adds `target`, `mode` (`measured` \| `degraded`), `runner`, `level`, `fail_on`,
`counts`, `gating_findings`, `truncated_findings`, `notes`, and — in degraded mode —
`MANUAL_CHECKLIST`.

## Report shape

Markdown output is the shared `/qa` report format, so an a11y audit drops straight into a
`/qa audit … --lens a11y` run alongside toolkit measurements:

```
## QA Report — <target> · audit · lens:a11y · level:aa
Standard: WCAG 2.2 AA + best-practice rules
Method:   axe (automated rules)

### Findings  (severity: blocker | major | minor | nit)
- [blocker] button-name — Buttons must have discernible text
  Evidence: `button.icon-only` · WCAG 4.1.2 · source: axe

### Summary
blocker 1 · major 2 · minor 1 · nit 0
Mode: measured  ·  Gating severities: blocker, major  ·  Gating findings: 3

### Next
<routing: fe-accessibility for fixes, visual-qa-toolkit for contrast, visual-qa-accessibility for judgment>
```

## Exit codes (the CI gate)

| Code | Meaning | CI reading |
|---|---|---|
| 0 | A runner ran; nothing at or above `severity.fail_on` | Pass (machine-detectable rules only) |
| 1 | A runner ran; gating findings present | Fail the build |
| 2 | DEGRADED — no runner, or `--runner manual` | Do **not** pass silently: install a runner in the image, or treat the checklist as a required manual step |
| 3 | Usage/input error (missing file, unparseable config) | Fix the invocation |

In CI, treat exit 2 as a configuration defect. A pipeline that accepts exit 2 as green has an
accessibility gate that measures nothing.

## Config

`configs/default.yaml` is the safe starting point: WCAG 2.2 AA, best-practice rules on, gating
on `blocker` + `major`. It carries `level`, `include_best_practices`, `runner`
(`prefer` order, timeout, `npx_fallback`, per-runner `extra_args`), `severity.fail_on`,
`exclude` (`rules`, `selectors`), `degraded` (`static_checks`, `fetch_url`), and `report`
(`format`, `max_findings_per_rule`).

Author project configs **with the project**, not in this folder — the toolkit stays
project-agnostic, exactly like [[visual-qa-toolkit]]. Every entry under `exclude` is a
documented decision: record why the rule or selector is out of scope (third-party embed you
don't own, known DS gap already backlogged) so an exclusion never becomes invisible debt.

The config parser is a deliberate YAML **subset** (comments, scalars, nested maps, flow lists,
block lists) so the toolkit has zero install step. Unsupported syntax raises instead of being
silently ignored.

## The degraded path in detail

Two things happen when no runner is available:

1. **MANUAL_CHECKLIST** — 20 WCAG-oriented checks (`MC-01`…`MC-20`), each with its success
   criteria, the check itself, and how to perform it. Filtered by `--level`: A yields 10 items,
   AA 19, AAA all 20. It covers what automation reliably misses — reading order, keyboard
   operability and traps, focus-order sanity, name/role/state correctness, live-region
   announcement, reflow and text-spacing overrides, target size, media alternatives, an
   assistive-technology pass per platform, and zoom/forced-colors/dark-theme behavior.
2. **Static HTML checks** (stdlib `html.parser`, local file or opt-in fetch) — missing `lang`,
   zoom-blocking viewport, `img` without `alt`, unnamed links/buttons (aria-hidden subtrees
   discounted), unlabelled form controls, duplicate `id`, heading-level jumps, missing `h1`,
   `iframe` without title, positive `tabindex`, tables without `th`, missing `main` landmark.

These are **leads**, not verdicts: they see only the served markup, so anything a framework
renders client-side is invisible. `tests/fixture-page.html` is a deliberately broken page used
to verify the degraded path without any runner installed.

## Honest limits

- **Coverage** — automated rules cover roughly 30-40% of defects; no rule set judges whether
  alt text is *meaningful*, whether focus order is *logical*, or whether an AT user can finish
  the task.
- **Static analysis is markup-only** — client-rendered DOM, dialogs, menus, and post-interaction
  states are out of reach in degraded mode.
- **One state per run** — a runner audits the page as loaded. Open the dialog, expand the menu,
  submit the invalid form, then audit again; each interactive state is its own target.
- **No contrast measurement of images** — text baked into an image is invisible to a DOM
  runner. Use `visual-qa-toolkit` `qa_contrast` on a screenshot.
- **Severity is this toolkit's mapping**, not the runner's own vocabulary. When quoting a
  finding externally, quote the rule id and WCAG criterion, not just the severity word.
- **Lighthouse findings carry no WCAG tags** — the `wcag` array is empty for that runner; map
  criteria via `a11y-legal-compliance` when the output feeds a conformance report.

## Workflow integration

1. Preflight the runner capabilities; if absent, decide up front whether to install one or
   accept a degraded run (and say which in the report).
2. Run the audit against every meaningful state, not just the default page.
3. Merge with `visual-qa-toolkit` contrast/color-vision measurements into one `/qa` report.
4. Triage: route implementation fixes to `fe-accessibility`, design changes to
   `visual-qa-accessibility` / the `lead-accessibility-architect` spokes, token-level contrast
   guarantees to `ds-advisor`, and conformance/VPAT framing to `a11y-legal-compliance`.
5. Work the MANUAL_CHECKLIST for the criteria automation can't reach, and record the AT pass.
6. Wire the exit code into CI ([[fe-testing]] owns the pipeline placement) with an explicit
   policy for exit 2.

## File layout

```
a11y-audit-toolkit/
├── SKILL.md                    # This file
├── scripts/
│   └── a11y_audit.py           # The CLI: preflight → run → normalize → report
├── configs/
│   └── default.yaml            # Safe default: WCAG 2.2 AA, gate on blocker+major
└── tests/
    └── fixture-page.html       # Deliberately broken page — verifies the degraded path
```

## Related
- hub → [[lead-accessibility-architect]]
- peer ↔ [[visual-qa-toolkit]] · [[fe-perf-harness]]
