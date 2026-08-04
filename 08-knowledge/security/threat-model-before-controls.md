---
tags: [security, threat-modeling, authn, authz, trust-boundary, secrets]
created: 2026-08-03
updated: 2026-08-03
status: working
confidence: medium
sources: [03-skills/sec-threat-modeling/SKILL.md, 03-skills/lead-security-architect/SKILL.md, 01-frameworks/16-security-operating-model.md, 08-knowledge/engineering/centric-ui-local-against-cloud-dev.md, 08-knowledge/engineering/silent-degradation-in-fenced-layers.md, AGENTS.md]
related_skills: [lead-security-architect, sec-threat-modeling, sec-authn-authz, sec-appsec-owasp, sec-supply-chain, be-security-posture, be-auth-patterns]
related_projects: []
relations:
  builds-on: ["[[centric-ui-local-against-cloud-dev]]"]
  exemplifies: ["[[16-security-operating-model]]"]
  relates-to: ["[[security-pipeline-baseline]]", "[[silent-degradation-in-fenced-layers]]", "[[contracts-first-delivery]]"]
---

# Threat model before controls: name the asset, the adversary, and the accepted risk first

## For future agent
- **TL;DR:** the reasoning behind the first stage of [[security-pipeline-baseline]]'s
  threat-model → build → scan → monitor pipeline ([[16-security-operating-model]]). Controls chosen
  before the asset and adversary are named are guesses that look like diligence. Write the **asset
  and adversary contract** first, enumerate threats per trust boundary, then choose controls, and
  **write down what you accepted**.
- **Key claims:**
  - *Timeless:* a control with no named threat cannot be evaluated, tuned, or removed, so it
    accumulates forever and nobody knows which ones are load-bearing.
  - *Timeless:* an authorization check that fails open is indistinguishable from a pass. Fail-closed,
    and make the rejection observable.
  - *Timeless:* validation order at an auth boundary is part of the contract, and the status code
    tells you which layer rejected you. Establish the order once instead of guessing per incident.
  - *Timeless:* an accepted risk that is not written down is a forgotten risk, and it will be
    rediscovered as an incident rather than as a decision.
  - *Pointer:* STRIDE per element, PASTA for architecture scope, and the `THREAT-MODEL.md` artifact
    format live in [[sec-threat-modeling]].
- **As of:** 2026-08 · **Status:** current (seeded baseline; the auth-boundary claim rests on
  validated prior diagnosis)

---

## Why this note exists

`08-knowledge/security/` was empty while the skill network was deep, which meant security
conversations began at the control layer ("should we add rate limiting", "do we need CSP") with no
stated position on what we are protecting or from whom. Answering control questions before that is
settled produces defensible-sounding decisions that cannot be revisited.

[[16-security-operating-model]] owns the pipeline and the done-gates; [[security-pipeline-baseline]]
is the one-line routing reminder. This note is the depth behind the first stage: how to write the
contract, and the specific failure shapes already observed here.

---

## The contract that comes first

Before any control is discussed, write three things:

- **Asset.** What specifically is worth protecting, in business terms. "The database" is not an
  asset; "customer PII in the orders table" is.
- **Adversary.** Who, with what access and what motivation. An opportunistic scanner, an
  authenticated tenant probing another tenant's data, and a malicious insider produce entirely
  different control sets. Choosing controls without choosing an adversary defaults to defending
  against all of them equally badly.
- **Accepted risk.** What we are knowingly not defending, and why. This is the field most often
  omitted and the one that matters most six months later.

Then enumerate threats per element and per trust boundary, rank them, and only then pick controls.
The artifact is a `THREAT-MODEL.md` next to the feature, per [[sec-threat-modeling]].

## Trust boundaries are where data changes hands

Every place data crosses from one authority to another is a boundary, and every boundary needs an
explicit validation rule. The list is longer than it first looks: client to server, service to
service, tenant to tenant, request to cache, config to runtime, dependency to build, and human to
system. A boundary with no stated rule has an implicit one, which is whatever the code happens to do.

## The auth-boundary lesson we actually learned

From real diagnosis in this workspace ([[centric-ui-local-against-cloud-dev]]): when several
auth-ish layers guard a request, the **order** in which they reject determines the observed status
code, and that mapping is the most reliable evidence available. Once established, a given code has
exactly one meaning instead of three candidates, and the diagnosis stops being guesswork.

Two generalizations worth keeping:

- **Error text is a narrow fact, not a hint.** "Not authorized for this path" is a statement about
  permissions on a valid path. Reading it broadly ("the path must be wrong") sends you rewriting
  correct code, which is how a two-minute fix becomes an afternoon.
- **Documented credentials in a repository are usually the local or default case.** Treat any
  example secret as the wrong one for your environment until proven otherwise.

## Fail closed, and make the rejection visible

This is where security meets [[silent-degradation-in-fenced-layers]]. A permission check wrapped in
a broad exception handler that returns a falsy default has been converted into an allow, or into an
invisible deny, and neither reports itself. Both are worse than an outright error.

- Fail closed on the security path. A deny that is wrong gets reported by a user in minutes; an
  allow that is wrong may never be reported.
- Give the check a side channel for *why* it denied, distinct from "there was legitimately nothing
  to authorize." Same rule as any other fenced layer, higher stakes.
- Never let a security control degrade silently under load or timeout. If it can be skipped, the
  skip is a documented accepted risk or it is a vulnerability.

## Secrets and repository hygiene

- Never commit `.env`, credentials files, tokens, or keys. If one is committed, rotate it: removing
  the file does not remove it from history.
- Real repositories and codebases live in the platform-relative `Projects` directory, resolved per
  device, never inside this portable workspace and never hardcoded, per [[AGENTS]].
- Under the `centric-engineering` context profile there is no auto-commit, no self-merge, and no
  direct push. Security findings against employer code are review artifacts that go through a human
  engineer, which is also the correct disclosure path.

## The practice's own failure modes

Threat modeling fails in predictable ways, and they are worth naming before starting: modeling at the
wrong altitude (either a diagram of the whole company or a single function), producing a threat list
nobody ranks, treating the document as a one-time deliverable rather than something re-opened when the
architecture changes, and letting "accepted risk" become an escape hatch for anything inconvenient.
[[sec-threat-modeling]] covers these; the mitigation is to keep the model small, ranked, dated, and
attached to the thing it describes.
