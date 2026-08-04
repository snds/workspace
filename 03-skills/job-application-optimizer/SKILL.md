---
name: job-application-optimizer
description: >-
  Workspace wrapper for optimizing job applications/materials. Depth at
  ~/.agents/skills/job-application-optimizer. Use for resume/tailoring/cover letters.
aliases: [job-application-optimizer]
triggers: [job application optimizer, resume tailor, cover letter]
tier: spoke
domain: career
hub: career-ops-job-search
prerequisites: [career-ops-job-search]
related: [career-ops-job-search, job-search-strategist]
defers_to: [framework-13]
rigor_role: load-chain
surfaces: ["*"]
spec_version: "2.2"
---

# Job Application Optimizer (Wrapper)

Canonical depth: `~/.agents/skills/job-application-optimizer/SKILL.md`.

## Related
- hub → [[career-ops-job-search]]
- peer ↔ [[job-search-strategist]]
