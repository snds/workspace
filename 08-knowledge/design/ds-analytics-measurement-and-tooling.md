---
tags: [design-systems, analytics, adoption, metrics, governance, open-source, tooling]
created: 2026-09-23
updated: 2026-09-23
status: working
confidence: medium
sources:
  - "Web research 2026-09-23 (two research passes; URLs inline; [search-only] = snippet, not fetched)"
  - "03-skills/design-system-ops/knowledge-notes/adoption-measurement.md (existing principles)"
related_skills: [ds-advisor, design-system-ops, adoption-report, ds-bi-platforms, pm-metrics-analytics]
related_projects: []
relations:
  builds-on: ["[[ds-ops-governance-notes]]", "[[nathan-curtis-ds-ops-substack]]"]
  relates-to: ["[[ai-and-design-systems]]", "[[contracts-first-delivery]]"]
---

# Design-system analytics — methods, practices, open-source tooling

## For future agent

- **TL;DR:** Measure a design system with **snapshots emitted by the same code that gates CI**
  (lint ratchets, AST scans, version pins), stored as time series, shown per team. Add Figma library
  analytics (Enterprise-only API, 1-year window, so snapshot it from day one). Add runtime "rendered
  coverage" only when static data stops answering the question. The best-fit fully open-source
  stack is **CI JSON → Postgres or DuckDB → (dbt Core) → Apache Superset**. Superset is the only
  mainstream open-source BI tool whose SSO, row-level security and alerts are not behind a paywall.
- **Key claims:**
  - *Timeless:* Import counts overstate adoption. Mature teams moved to rendered or visual coverage (Mews, Preply, Uber).
  - *Timeless:* A metric must come with its enforcement. Lint rules are both the sensor and the guardrail. Codemods turn a metric into a burn-down.
  - *Timeless:* Drift is a signal about the system, not a list of teams doing it wrong ([[ds-ops-governance-notes]]).
  - *Dated 2026-09:* Licenses to watch: Snowplow is SLULA (not open source for commercial production), RudderStack is ELv2, PostHog `ee/` is proprietary and its self-host is hobby-only, Metabase OSS paywalls SAML and row-level permissions, Grafana paywalls SAML and fine-grained RBAC. dbt Core v2 was relicensed to Apache-2.0 on 2026-06-01. OpenTelemetry graduated from CNCF 2026-05.
- **As of:** 2026-09 · **Status:** current. Re-verify licenses before adopting anything (they change).

For how to *report* adoption (coverage vs adoption, the definition worksheet, maturity stages), use the
existing skill [[adoption-report]] and `design-system-ops/knowledge-notes/adoption-measurement.md`.
This note covers what they don't: **instrumentation, data sources, change mechanics, and tool choice.**

---

## 1. What to measure

A metric only counts if someone can act on it. Group metrics by the decision each one supports:

| Family | Metric | Decision it drives | Primary source |
|---|---|---|---|
| **Debt** | Token or tier-leak violations per repo, per rule, per directory | Where to send codemods or pairing help | Lint in CI (ESLint, Stylelint) |
| **Currency** | Consumer's pinned version vs latest (commits or days behind, majors behind) | Release cadence and support policy | Lockfile or pin file; Renovate dashboard |
| **Consumption** | DS component instances vs raw HTML or local look-alikes (the "custom ratio") | What to build next and which snowflakes to fold in | AST scan (react-scanner, ts-morph) |
| **Correct use** | Overrides such as `className` or style on DS components, spread props, detaches | Whether components fit their real use cases | AST scan; Figma detaches |
| **Design** | Weekly insertions and detaches per component, per team | Where Figma and code have drifted apart | Figma Library Analytics |
| **Rendered** | Share of DOM elements (or pixels) in production that are DS | Real adoption as users actually see it | Runtime attribute sampling |
| **Engagement** | Contributions, docs searches, support threads | Where docs are missing and who contributes | Git, docs analytics, chat |
| **Outcome** | Time to build, a11y defects, visual-parity bugs | The ROI case | Studies; issue tracker |

Published reference points:
- **Figma "Design Systems 104" (Feb 2025).**
  - Vanguard: design updates 50% faster.
  - athenahealth: about 100k insertions per month.
  - Source: https://www.figma.com/blog/design-systems-104-making-metrics-matter/
- **Figma (2019):** designers were 34% faster at *best case* ("maximum" in Figma's words). https://www.figma.com/blog/measuring-the-value-of-design-systems/
- **Sparkbox and IBM Carbon:** a simple form took 47% less time to build, but the study had only n=8 developers. The same study's accessibility results were mixed. https://sparkbox.com/foundry/design_system_roi_impact_of_design_systems_business_value_carbon_design_system
- **Treat every ROI number as a ceiling, not a forecast.**

**Gaps in published evidence (as of 2026-09):**
- No public benchmark for "% of consumers on the latest major".
- No public benchmark for time to adopt a release.
- No public comparison of accessibility defect rates in DS vs non-DS production UI.

If you measure these, you are producing new evidence, not checking against a norm.

## 2. Four adoption definitions — pick one and keep it

1. **Imports.**
   - Method: scan for imports and instances (react-scanner, Omlet, MetaMask `design-system-metrics`).
   - Strength: cheap.
   - Weakness: overstates adoption, because components get wrapped and overridden.
   - Users: Productboard, Brevo, Twilio Paste.
2. **Design-layer ratio.**
   - Method: DS layers ÷ all layers in Figma files marked for handoff.
   - Users: Pinterest FigStats. https://www.figma.com/blog/how-pinterests-design-systems-team-measures-adoption/
3. **Rendered-element ratio.**
   - Method: a Babel plugin stamps `data-ds-element`. A 10-second DOM sample in production computes DS elements ÷ all elements, which goes to observability.
   - Users: Mews, which reports 53–60% and rising. https://developers.mews.com/design-system-adoption-metric-building/
4. **Visual (pixel) coverage.**
   - Method: in the browser, weighted by component type.
   - Users: Preply (open source, https://github.com/preply/design-system-visual-coverage). Uber runs a view-tree scan and takes the mode across sessions. https://www.uber.com/blog/design-system-at-scale/

Start at 1. Add 3 only when leadership asks what users actually see. Definitions 3 and 4 are runtime
telemetry, so they need a privacy review. Count elements only, never content. Gate collection with
feature flags.

## 3. Turning measurement into change

The pattern that works is **sense → gate → fix → show**:

- **Sense and gate with the same code.** Lint rules act both as metrics and as enforcement.
  - Atlassian: `ensure-design-token-usage` and `no-deprecated-design-token-usage`, auto-fixable.
  - Shopify: stylelint-polaris, with 40+ rules grouped so they can measure coverage.
  - Gestalt: `no-spread-props`, which exists so that metrics and codemods stay accurate.
  - This is the same law as this vault's steel curtain ([[ai-and-design-systems]]).
- **Ratchet, don't big-bang.** Freeze today's violation count as a baseline. Fail CI if it grows. Lower it as files migrate.
  - Polaris's migrator adds `stylelint-disable` comments to existing violations so the rule can be turned on immediately.
- **Fix with codemods.** Gestalt ships a codemod with every breaking release. Atlassian has `codemod-cli`. With no codemod, a deprecation will not finish ([[ds-ops-governance-notes]] anti-zombie rule).
- **Show it where people already look.**
  - Productboard runs scheduled CI across 200+ projects and publishes a daily Looker dashboard company-wide.
  - Brevo runs react-scanner into Metabase every two weeks.
  - Uber files automatic Jira tickets to the owning managers.
  - Backstage Tech Insights puts scorecards on each service page. **[unverified]** I found no public case of a DS team doing this.
- **Frame it kindly.** Uber's rule: "assume people have good intentions". Degradation is a missing guardrail. Leaderboards used to shame teams backfire. Clusters of drift are roadmap input.

## 4. Data sources — mechanics and limits

- **Figma Library Analytics.**
  - The UI is on Organization and Enterprise plans. The REST API is **Enterprise-only**, needs scope `library_analytics:read`, and is rate-limited at Tier 3.
  - Endpoints: `/v1/analytics/libraries/:key/{component|style|variable}/{actions|usages}`.
    - `actions` returns weekly inserts and detaches, grouped by asset or team.
    - `usages` returns current instances, grouped by asset or file.
    - Source: https://developers.figma.com/docs/rest-api/library-analytics-endpoints
  - History is about 1 year, so **snapshot weekly into your own store**.
  - What it doesn't count: drafts, nested instances, or inserts that came from duplicating a file.
  - Detaches can be intentional (templates), so ask *why*, not just how many.
  - Without Enterprise, you would have to walk files with the file REST API (Pinterest built FigStats before the analytics API existed).
- **AST scans.** react-scanner, ts-morph, or Omlet's CLI. They are blind to spread props and to dynamic components, so enforce the rules that keep them accurate.
- **Telemetry inside the package.** IBM `@ibm/telemetry-js` collects at install time, CI-only, with SHA-256 hashing and an opt-out environment variable (https://github.com/ibm-telemetry/telemetry-js). This works, but on-by-default collection causes friction with enterprise consumers.
- **npm downloads.** A vanity number on its own (Twilio found this out). Use it only for trend direction.

## 5. Open-source analytics tools (verified 2026-09-23)

| Role | Pick | License / governance | Enterprise features free? | Notes |
|---|---|---|---|---|
| BI and dashboards | **Apache Superset** 6.1 | Apache-2.0 / ASF | **Yes**: SAML, OIDC, LDAP, row-level security on by default (6.0+), alerts and webhooks | Heavier to run; less friendly UX for designers |
| BI (friendlier) | Metabase v0.63 | AGPL-3.0 / vendor | No: SAML, OIDC, JWT, row and column permissions and audit are Pro/Enterprise | Fastest self-serve |
| Time-series and alerts | Grafana 13 | AGPL-3.0 / vendor | Partly: OIDC and alerting free; SAML, fine-grained RBAC, audit and reports paid | Weak at tabular drill-down |
| dbt-native BI | Lightdash | MIT plus proprietary `ee/` | Mostly no (enterprise SSO, embedding, custom roles) | Worth it only if metrics live in dbt |
| BI-as-code | Evidence Core | MIT / vendor | No auth; put it behind your own proxy | Good for a quarterly report kept in a repo |
| Transform | dbt Core | Apache-2.0 (v2 relicensed 2026-06-01) | — | Builds `usage_daily` and `migration_status` |
| Store (small) | DuckDB 1.5 / Postgres | MIT (DuckDB Foundation) / PostgreSQL | — | DuckDB is single-writer |
| Store (events) | ClickHouse 26.8 LTS | Apache-2.0 / vendor | Row policies in SQL | HA takes real ops work |
| Runtime capture | OpenTelemetry | Apache-2.0 / CNCF graduated | — | Browser RUM is still less mature; sample |
| Scorecards | Backstage + Tech Insights | Apache-2.0 / CNCF incubating | Open-source plugin is basic; Soundcheck is paid | Only if Backstage already runs |
| Semantic layer | Cube Core | Apache-2.0 / MIT | Access-policy UI is Cloud-only | Only once there are 3+ consumers |

Avoid for this job:
- **Snowplow** (SLULA) and **RudderStack** (ELv2): source-available, not open source.
- **PostHog self-host:** hobby Docker Compose only, no support, Kubernetes sunset.
- **Redash:** maintenance mode.
- **Web analytics tools** (Matomo, Plausible, Umami): wrong data model. They count pageviews, not components, versions or repos.

**Reference stacks:**
- **A. Snapshot-first (default).**
  - Pipeline: CI emits JSON per repo per commit, plus weekly Figma and npm pulls. These go to Postgres (or DuckDB/Parquet), optionally through dbt Core, into Superset.
  - Volume: millions of rows, not billions.
- **B. Plus runtime telemetry.**
  - Pipeline: an OpenTelemetry browser SDK (or a small beacon) sends to the Collector, then ClickHouse. Superset handles drill-down; Grafana OSS handles alerting.
- **C. Plus governance surface.** Backstage Tech Insights reads the latest snapshot for per-repo scorecards. Superset stays the place for trends.

## 6. Pitfalls

1. **Import counts inflate adoption.** Text and color styles alone ≠ compliance (Uber).
2. **Visual coverage overweights large containers.** Mews rejected it for that reason; Preply weights by component type.
3. **Figma counts are noisy.** Pinterest filtered to handoff pages and recently edited files out of 1,853.
4. **Legacy UI counts the same as new UI.** Report "new surface" separately from "legacy surface".
5. **Goodhart's law.** Once adoption is a target, wrappers, re-export shims and spread props inflate it. Keep a correct-use measure next to every count (PJ Onori).
6. **Privacy.** Runtime sampling must count structure, not content. Collection in the package should be opt-in, or at least disclosed.
7. **Measurement is still rare.** 16% tracked metrics in 2022 (Sparkbox), and zeroheight 2025 calls the tooling "fractured". A small, consistent pipeline is ahead of most of the industry.

## Related
- [[adoption-report]] — report format and adoption definitions (use for output)
- [[ds-ops-governance-notes]] — drift as signal; deprecation anti-zombie rule
- [[nathan-curtis-ds-ops-substack]] — ops framing; Curtis OKR measurement (https://eightshapes.com/articles/measuring-design-system-success/, [search-only])
- [[ai-and-design-systems]] — steel curtain: determinism at the gate
