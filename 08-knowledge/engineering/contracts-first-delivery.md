---
tags: [engineering, contracts, observability, delivery, validation, error-handling]
created: 2026-08-03
updated: 2026-08-03
status: working
confidence: medium
sources: [08-knowledge/engineering/silent-degradation-in-fenced-layers.md, 08-knowledge/engineering/centric-ui-local-against-cloud-dev.md, 01-frameworks/14-engineering-operating-model.md, 02-shared-references/delivery-playbooks/05-validation-harness.md, 01-frameworks/06-qa-operating-model.md]
related_skills: [eng-foundations, be-api-design, be-integration-patterns, fe-api-integration, devops-observability, lead-frontend-engineer, lead-backend-engineer]
related_projects: []
relations:
  builds-on: ["[[silent-degradation-in-fenced-layers]]", "[[centric-ui-local-against-cloud-dev]]"]
  exemplifies: ["[[14-engineering-operating-model]]"]
  relates-to: ["[[experiment-validity-baseline]]", "[[threat-model-before-controls]]", "[[workflow-patterns]]"]
---

# Contracts-first delivery: name the contract in plain english before writing the code

## For future agent
- **TL;DR:** the vault evidence behind [[14-engineering-operating-model]]'s contracts-first
  conviction, generalized from two hard-won entries here. Every boundary (an API, a cache, a fenced
  layer, a config surface) has a **contract**; the expensive bugs in this workspace's history were a
  contract that was real but unwritten, so a violation looked like normal behavior. Write it first,
  in plain english, and make each violation *observably distinct* from success.
- **Key claims:**
  - *Timeless:* if a failure and an empty-but-healthy result are represented identically, the system
    has no way to tell you it broke, and neither do you.
  - *Timeless:* validation **order** is part of an interface contract, and its status codes leak
    which boundary rejected you. Reading the code is often faster than reading the docs.
  - *Timeless:* a cache key must contain every parameter that governs the value, or invalidation
    must be explicit. There is no third option that is merely a bit risky.
  - *Pointer:* the delivery format for code-heavy work is the Proofboard
    (`02-shared-references/delivery-playbooks/05-validation-harness.md`).
- **As of:** 2026-08 · **Status:** current (synthesis of two validated entries; the synthesis itself
  is not yet independently validated)

---

## Why this note exists

Two entries in this vault, from unrelated work, describe the same underlying failure from opposite
ends. [[silent-degradation-in-fenced-layers]] found it three times in one session: a layer that
degrades to nothing erases the difference between "genuinely nothing" and "the mechanism failed."
[[centric-ui-local-against-cloud-dev]] found the mirror image: a 401 that always meant one specific
thing, and an error string ("Unauthorized API path") that meant something narrower and more useful
than it appeared. In both cases the contract existed, was load-bearing, and was nowhere written down.

This note names the shared rule so the next boundary gets it up front. It is `working` because the
two source entries are validated but this generalization has not yet been tested on new work.
[[14-engineering-operating-model]] holds the framework-level ordering and done-gates; this note holds
the specific evidence and the failure shapes to watch for.

---

## 1. Write the contract before the implementation

Before the first line at a boundary, state in plain english:

- **Inputs:** what must be true of them, and what happens when it is not.
- **Outputs:** the success shape, and the distinct shape of each failure class.
- **Empty vs. broken:** how a caller distinguishes "there is legitimately no data" from "the
  mechanism failed." If they are the same value, the contract is wrong.
- **Ordering:** which check runs first, and therefore which error a caller sees when several are
  violated at once.

This is the same artifact the Proofboard asks for at delivery time, so writing it first costs
nothing and pays twice.

## 2. Fenced layers need a side channel for *why*

Any layer with a `try`/timeout/fallback around it is a fence: it converts a failure into a
degraded-but-continuing result. That is often correct. What is never correct is having no way to
learn *that* it fired.

- Give the fence a counter, a `last_error`, or a one-time stderr note. Cheap, and it is the
  difference between a five-minute diagnosis and a five-hour one.
- Classify **fatal vs. per-item** before collapsing anything. Credit exhaustion and "this one record
  genuinely has no match" must not produce the same value, because the first invalidates the whole
  run and the second is normal.
- Never monitor a progress counter you did not verify against the real output artifact. A counter
  can measure the cheap phase and look healthy while the expensive phase does nothing.

## 3. Trust the code's validation order over the documentation

From real diagnosis: when several auth-ish layers guard a request, the order in which they reject
determines what the caller sees, and that mapping is more reliable evidence than any written guide.
The practical form:

- Establish the order once (which layer rejects with which code), then read every failure through it.
  A given code then has exactly one meaning instead of three candidate ones.
- Take error **text** literally and narrowly. "Not authorized for this path" is a permissions fact
  about a valid path, not evidence the path is wrong. Guessing wide sends you rewriting correct code.
- Documented example values in a repository are frequently the local or default case, not the one
  your environment uses. Read the real value from the running system when you can.

## 4. Every governing parameter is in the cache key

If a value depends on a parameter, that parameter is in the key, or invalidation is explicit and
written down. A key missing a governing parameter produces a stale hit that is indistinguishable
from a correct one, which puts it in the same family as the silent-degradation failures above: wrong
answer, no error, nowhere to look.

## 5. Prove it at the boundary, in the reader's language

Code-heavy work ships with a Proofboard: the contract in plain english, show-me evidence that it
holds, and sandboxed sample data the reviewer can re-run. The reviewer should be able to verify the
claim without reading the implementation. This is the pre-output gate from
[[06-qa-operating-model]], and for a boundary it means demonstrating the failure paths, not only the
happy one. A demo that shows only success has not exercised the part of the contract that gets
people paged.

## The diagnostic habit underneath all four

Diagnose before hardening. Both source entries record the same sequence: the instinct was to add
defenses, and the actual finding was that the mechanism was fine and the *observability* was
missing. Confirm which of the two you have before writing the fix, or you will harden a working
system and leave the real defect in place.
