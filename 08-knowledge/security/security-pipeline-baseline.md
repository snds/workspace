---
title: Security pipeline baseline
tags: [knowledge, security]
created: 2026-08-03
updated: 2026-08-03
relations:
  relates-to: [security-operating-model, be-security-posture]
---

# Security pipeline baseline

## For future agent

**TL;DR:** Threat-model → secure build → scan → monitor (#16). `be-security-posture` is implementation depth, not a substitute for the pipeline. Fail closed; no secrets in git.

**As of:** 2026-08

---

Triggers: `threat model`, `security done-gate`, `sec pipeline`
