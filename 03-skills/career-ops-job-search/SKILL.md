---
name: career-ops-job-search
description: >
  The industrialized job-search pipeline: batch offer evaluation with weighted A-F scoring,
  portal scanning across configured companies, ATS-optimized PDF CV generation, LinkedIn outreach
  drafting, deep company research, and a terminal dashboard over a single tracked pipeline file.
  Use this skill whenever the conversation touches: career-ops, job search automation, scan job
  portals, batch evaluate offers, score this offer, offer grade, application tracker, job pipeline
  status, generate CV PDF, ATS PDF, outreach message at volume, or running a job search as a
  repeatable system rather than one application at a time. Workspace wrapper: routes to the
  canonical agent skill and states the real preconditions (external repo, Node, Playwright, Go,
  Claude Code slash commands). Spoke of job-search-strategist.
aliases: [career-ops-job-search, career-ops]
triggers: [career-ops, career ops, job search automation, scan portals, portal scanner, batch evaluate, batch offers, offer scoring, offer grade, application tracker, pipeline status, generate cv pdf, ats pdf, job search dashboard, linkedin outreach, company research report]
tier: spoke
domain: career
hub: job-search-strategist
prerequisites: [job-search-strategist]
related: [job-application-optimizer]
surfaces: ["*"]
spec_version: "2.0"
---

# Career-Ops Job Search (workspace wrapper)

**This file is a routing wrapper, not the method.** Canonical depth:

```
~/.agents/skills/career-ops-job-search/SKILL.md
```

That file carries the full command reference, config schemas, scoring model, dashboard internals,
batch runner, and troubleshooting. Read it before running anything.

---

## Doctrine: wrapper owns *when*, agent skill owns *depth*

The wrapper owns routing, the preflight below, and where the pipeline's data and repo live. The
agent skill owns the operational detail. Copying that detail here would double the maintenance
surface and drift the moment upstream changes.

---

## Preflight: this one has real preconditions

Unlike its two siblings, this skill drives an external system. Confirm all of it before promising
output:

| Requirement | Why | If missing |
|---|---|---|
| The `career-ops` repo cloned locally | Everything (modes, config, pipeline TSV, dashboard) lives in it | Stop. Clone it into the platform-relative `Projects` directory, never inside this workspace. |
| `config/profile.yml` and `cv.md` filled in | The scoring model reads target role, comp range, location, and the CV to score fit against | Stop. Unconfigured scoring produces confident nonsense. |
| Node plus Playwright Chromium | PDF CV rendering | Everything except PDF generation still works. Say which half ran. |
| Go toolchain | The terminal dashboard | Read the pipeline TSV directly instead. |
| **Claude Code** | The `/career-ops …` commands are Claude Code slash commands | Not runnable on this surface. In Cursor or another client, do the equivalent work manually via the hub and [[job-application-optimizer]], and say that is what you did. Do not fake a pipeline run. |

Follow [[AGENTS]] "Capability preflight" behavior: probe, then either degrade with the gap named
or block with the install path. Never fail silently, and never report a scored result you did not
actually produce.

---

## Operation grammar

Entry points are slash commands, each backed by one file in the repo's `modes/` directory. Full
list and arguments are in the canonical skill. The shape:

```
/career-ops                  → list modes
/career-ops <URL or JD text> → full pipeline: evaluate, generate PDF, write tracker entry
/career-ops scan             → sweep configured portals for new postings
/career-ops batch            → evaluate a queue in parallel
/career-ops tracker          → pipeline status
```

Customize behavior by editing `modes/_shared.md` first: it is injected into every mode, so it is
the single place to put standing context.

---

## The scoring model is a filter, not a verdict

Offers are graded A-F from ten weighted dimensions (role fit, level, compensation, stack, company
stage, remote policy, growth, mission, interview signals, recruiter quality). Two things follow:

- **It ranks, it does not decide.** The weights encode assumptions from `profile.yml`. A B+ that
  matches the positioning from [[job-search-strategist]] can beat an A that does not. Read the
  dimension breakdown, not just the letter.
- **Garbage in, confident garbage out.** A stale `profile.yml` or `cv.md` produces grades that
  look rigorous and are not. Check both are current before trusting a batch run.

---

## Where the data lives

- **The repo**: platform-relative `Projects` directory, resolved per device. Never hardcode a
  path and never place it inside this portable workspace, per [[AGENTS]] "Externalize everything".
- **The pipeline TSV**: the repo's single source of truth for application state. It is personal
  and company-named; it stays in the repo, out of this workspace's tracked files.
- **Context profile `personal-solo`**, same as its siblings. Keep it fully separate from employer
  work.

## Related
- hub → [[job-search-strategist]]
- spoke → [[job-application-optimizer]]
- peer ↔ [[job-application-optimizer]]
