---
title: Context Profiles — whose work is this, and who reviews it?
status: canonical
date: 2026-07-09
tags: [context, governance, repo-conduct, identity, delivery]
---

# Context profiles — whose work is this, and who reviews it?

**Context is king.** Every downstream delivery decision — voice, medium, evidence, repo
conduct, identity — derives from facts about who owns the work and who reviews it. Those facts
are **declared here by Sean once and cited by Claude every time**; they are never guessed
per-task. A wrongly-contexted action (auto-committing to an employer repo, pushing employer
material to a public repo) is the class of mistake that can't be walked back cheaply, so this
file resolves *before* any playbook, gate, or repo action.

**Citing rule.** When Claude acts on a profile rule, it names the profile in the moment
("per `centric-engineering`: opening a PR, not merging") so every behavior audits back to a
declared fact. If reality contradicts a profile, stop and surface it — don't improvise around it.

---

## Resolution order

1. **Sean's explicit word in the ask.** Always wins, even over a declared profile.
2. **The project's declaration.** A `Context profile` line in the project's `SESSION-STATE.md`
   Environment block, or the project's entry in `06-context/project-context.md`.
3. **The repo remote.** `github.com/snds/*` → personal. `cpes-software/*` (or any
   Centric-org remote) → Centric. Mechanical and checkable — run `git remote -v` before acting.
4. **Still ambiguous → stop and ask.** This is the one place in the system where asking beats
   acting.

**Fail-safe default.** If context genuinely can't be resolved, behave as if under the most
restrictive profile — no commits, no pushes, designer voice, confidential — until told
otherwise. Wrong-and-cautious costs minutes; wrong-and-permissive costs trust.

---

## The profiles

| | `personal-solo` | `centric-engineering` | `centric-design` |
|---|---|---|---|
| **Examples** | Media Sentinel, Legion, this workspace, nexus/Davinci | centric-ui, C8, ds-docs, figma-repo-sync-plugin | PLM specs, audits, pattern docs, decks for design leadership |
| **Owner / reviewer** | Sean alone | Engineers via PR — human review mandatory | Sean's design managers |
| **Repo conduct** | Direct commits fine; session-end auto-commit fine; pushes to `main` acceptable | **No auto-commit, no self-merge, no direct pushes.** Branch → PR → human review; small dependency-ordered diffs per [[07-integration-and-review-framework]] | Usually no repo — artifact delivery per [[artifact-standards]] |
| **Evidence target** | The Proofboard ([[05-validation-harness]]) **is** the review | Dual: Proofboard for Sean pre-PR **plus** conventional engineer evidence — tests, CI green, engineer-voiced PR description | The forward test ([[01-audience-contract]]) at full strength |
| **Delivery voice** | Designer-first | Designer-first to Sean; engineer-voiced **only** inside the repo surface itself (PR descriptions, code comments, commit messages) | Designer-first, zero translation required |
| **Git identity** | Personal `snds` GitHub auth | Centric GitHub auth | n/a |
| **IP boundary** | No employer material, ever | Employer material stays inside employer repos | Confidential by default |

_Terms: **PR** (pull request) — a proposed change packaged up for someone else to review before it
can land. **CI** — the automated checks that run on every proposed change._

### Flags (cross-cutting, not extra profiles)

- **`visibility: public`** — applies to any public repo (e.g. nexus/Davinci portfolio work).
  Tightens the IP rule: no third-party proprietary reference material of any kind (competitor
  screenshots, design-source folders) — gitignore it. No secrets, no plaintext personal email
  in commit metadata where avoidable.

### Per-profile notes

**`personal-solo`.** Sean is the only human in the loop, so the verification burden falls
entirely on the validation layer: no code-heavy deliverable is done until its Proofboard exists
and Sean has clicked through it. Speed is a feature here — direct commits and session-end
auto-commits are expected behavior, not exceptions.

**`centric-engineering`.** Claude's output is an *input to someone else's review*, which
changes everything: the work must be legible to engineers on their terms (tests, small diffs,
conventional PR hygiene), and Claude never performs the merge-side of review (no self-merge,
no bypassing checks). The Proofboard still gets built — it serves Sean's own validation before
the PR opens — but it never substitutes for the evidence engineers require.

**`centric-design`.** The deliverable's readers are design leaders who will read it out to
*their* stakeholders. Two hops of readers, zero hops of translation: the artifact must carry
its own explanation.

---

## What consumes these profiles

- [[01-audience-contract]] — reader and voice are looked up from the profile.
- [[05-validation-harness]] — what "proven" means per profile (see Evidence target row).
- [[07-integration-and-review-framework]] — profile decides whether its PR gates apply at all.
- Repo actions anywhere — commit/push/merge conduct and git identity.
- The pre-delivery gate ([[02-shared-references/delivery-playbooks/README|Delivery Playbooks README]]) — question 1.

## Changing this file

Profiles are Sean's declared facts. Claude may *propose* a new profile or a correction when
reality contradicts the table (citing the contradiction), but only Sean's explicit sign-off
changes it. Additive edits only; retired profiles are archived, never deleted, per
[[08-workspace-contribution-framework]].
