---
type: reference
description: The saas-plm-analysis/knowledge-discovery repo — Centric's cross-role knowledge base for the new SaaS PLM platform; where it lives locally and how to navigate it
created: 2026-07-20
confidence: high
---

**`github.com/saas-plm-analysis/knowledge-discovery`** (private, org-owned) — "the core knowledge base for
the new saas-plm product encapsulating analysis and specification for the platform." Cloned locally to
**`<Projects>/saas-plm-analysis/knowledge-discovery`** (org-named parent dir, matching the
`cpes-software/` convention). ~503 MB on disk; `main`. Employer work — Centric credentials only, per
[[feedback-credential-scoping]].

**Read its own contract before working in it.** The repo is agent-aware and carries its own map:

- `AGENTS.md` — the machine-oriented map: domain taxonomy (legacy C8 extraction → target SaaS
  configuration, per business domain), content-type guide, task routing.
- `README.md` — human entry point + the ownership table.
- `INDEX.md` **in each directory (62 of them)** — the repo's stated rule is to open the local `INDEX.md`
  before loading many leaf files. Follow that; it is the repo's own answer to context bloat.
- `.cursor/rules/` (8) — `navigate`, `writing-style`, `configuration-agent`, `extraction-agent`,
  `monolith-analysis-methodology`, `monolith-process-evaluation`, `cost-quality-routing`,
  `problem-brief-way-of-working`.
- `.cursor/skills/` (4) — `confluence-publish`, `convert-html-docs`, `jira-sync-requirements`,
  `regenerate-index-stubs`.

**Layout / ownership** — `core/` (domain analysis + data models; everyone reads, Engineering writes) ·
`product/` (PM; by far the largest at ~247 MB) · `ux/` · `ui/` (component specs, design system) ·
`engineering/` (architecture) · `strategy/` (vision, cross-team specs, ADRs) · `ai-knowledge/`
(machine-consumed: patterns, legacy→new mappings, golden examples, decision log) · `flavours/`
(`saas-plm-base/` target configuration) · `Monolith Customer Configs/`.

**Relationship to this workspace:** it is a *peer* knowledge base, not a subset — Centric-owned, covering
the SaaS PLM product across PM/UX/UI/Engineering. This workspace stays the personal operating layer; that
repo is the employer domain source of truth. Keep the separation both ways per the standing rule: no
workspace content into employer repos, no employer content pasted into personal surfaces. The natural
overlap is the `ui/design-system/` and `ux/` material against Sean's Centric DS work — cross-read, don't
copy. Related: the `centric-ui` / VMS design-system thread in `06-context/project-context.md`.
