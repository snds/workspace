---
name: sec-threat-modeling
description: >
  Structured threat modeling — enumerating what can go wrong before it does. STRIDE,
  attack trees, trust boundaries + data-flow diagrams, the attacker's perspective, and
  risk ranking (likelihood × impact) to prioritize mitigations. Use at design time for any
  feature handling untrusted input, secrets, money, or PII. Triggers: threat model, STRIDE,
  attack tree, trust boundary, data flow diagram, attack surface, risk assessment, abuse case.
aliases: [sec-threat-modeling]
triggers: [threat model, stride, attack tree, trust boundary, data flow diagram, attack surface, risk assessment, abuse case]
tier: cross-cutting
hub: lead-security-architect
domain: security
surfaces: ["*"]
spec_version: "2.0"
---

# Security — Threat Modeling

Asking "what can go wrong?" systematically, at design time, when fixes are cheap. A lens applied to any
feature touching untrusted input, secrets, money, or PII.

## Map the system first
Draw the **data-flow diagram**: actors, processes, data stores, and the **trust boundaries** they cross.
Threats live at boundaries (where data moves from less-trusted to more-trusted). You can't model what you
haven't mapped.

## STRIDE — the threat taxonomy
For each element/boundary, ask: **S**poofing (identity), **T**ampering (integrity), **R**epudiation
(deniability), **I**nformation disclosure (confidentiality), **D**enial of service (availability),
**E**levation of privilege (authorization). STRIDE is a prompt set so you don't miss a category.

## Think like the attacker
Build **attack trees** (goal → sub-goals → methods) and **abuse cases** (the misuse of a feature). Assume
the attacker has your source, controls the client, and replays/forges requests. The question is never "would
someone?" but "what happens when someone does?"

## Rank + mitigate
Score by **likelihood × impact**; fix the high-risk first. Each threat maps to a mitigation (control) or an
accepted/transferred risk — documented, not implicit. Route specifics to [[sec-authn-authz]] (identity),
[[sec-appsec-owasp]] (input/output), [[sec-supply-chain]] (dependencies/secrets).

## Related
- hub → [[lead-security-architect]]
- peer ↔ [[sec-authn-authz]] · [[sec-appsec-owasp]] · [[sec-supply-chain]]
