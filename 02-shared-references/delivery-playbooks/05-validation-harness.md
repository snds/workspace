---
title: Validation Harness — the Proofboard standard
status: canonical
date: 2026-07-09
tags: [validation, evidence, proofboard, testing, transparency, delivery]
---

# Validation harness — the Proofboard standard

**The problem this solves.** When work is code-heavy — back-of-house, data-science-heavy,
back-end-centric, or specialty work with niche context — Sean does not have the domain
knowledge to validate it by reading it, and shouldn't have to. His trusted verification method
is visual: running through flows and seeing behavior directly. The Proofboard extends that
method to work that has no UI of its own.

**Definition.** A Proofboard is a companion screen that ships with code-heavy work: every
promise the work makes is a plain-english sentence with a live pass/fail status and a
"show me" affordance, running on invented sample data so nothing real can break.

**Definition of done (binding).** For any code-heavy deliverable, *done* means **Sean verified
it without reading code**. The Proofboard is budgeted and built as part of the work, not
offered afterward. What "proven" means varies by profile ([[00-context-profiles]]):

| Profile | The Proofboard is… |
|---|---|
| `personal-solo` | **The entire review apparatus.** No board, no done. |
| `centric-engineering` | Sean's own validation before the PR opens — built **alongside**, never instead of, the tests / CI / PR quality engineers require. |
| `centric-design` | Rarely code-heavy — but any code-backed analysis feeding a leadership deliverable still gets a board, so the deliverable's claims stay verifiable. |

_Terms: **PR** (pull request) — a proposed change packaged up for someone else to review before it
can land. **CI** — the automated checks that run on every proposed change._

---

## The five principles

### 1. A plain-language contract register, agreed before building

Before code is written, Claude translates the ask into numbered, testable sentences in Sean's
vocabulary, and Sean approves the list. Everything downstream — code, tests, board — hangs off
these numbered contracts, so what gets verified is what was actually asked.

```
## Contracts — Media Sentinel watchlist (approved 2026-07-09)
1. When a new article mentions one of my watchlist terms, it appears in my
   review queue within 5 minutes.
2. Articles from blocked sources never reach the queue.
3. Dismissed articles move to the archive — nothing is ever deleted.
```

New asks mid-build become new numbered contracts, not silent scope absorption.

### 2. Show, don't assert

A green checkmark that can't be interrogated is "trust me" with extra steps. Every status has
a **"show me"** that replays the evidence as a narrated story: here's the fake input we
invented, here's what the system did with it, here's why that's what you asked for.

> 1. We invented a fake article from "Blocked Daily" — a source on your block list.
> 2. We pushed it through the exact same path real articles travel.
> 3. The queue stayed empty — the article was turned away at the source check.

**Illustrate, don't narrate** — evidence defaults to a visual (anatomy diagram, highlighted
diff, lit-up segment) with prose demoted to captions. *(Sean-approved amendment, 2026-07-09 —
validated by the artifact-name-checker v1.1 visual-first evidence pattern.)*

### 3. Non-destructive by construction

The board always runs on invented sample data in a sealed sandbox, with a permanently visible
**"safe playground — nothing real can change"** badge. For operations that *would* be
destructive (delete, send, overwrite), the board shows a dry-run preview: "here is exactly
what would have been deleted." Sean should never have to wonder whether a click is safe.

### 4. Three altitudes, caveats at the top

Every panel offers Plain english → How it works → Full detail, per the model in
[[01-audience-contract]]. The binding rule: anything that would change Sean's decision — a
limitation, a risk, an assumption — appears at the plain-english level. ELI5 never licenses
omission.

### 5. One click, no terminal

The board opens by double-click, per [[artifact-standards]] §5 (self-contained package,
`start.command` only when a local server is genuinely required). If verifying the work
requires a command line, the apparatus has already failed its target user.

---

## Trust mechanisms (what keeps the board honest)

- **The board renders the real tests.** Statuses come from the same automated checks that
  gate the code — never a hand-built parallel display, which could drift from the truth and
  become theater. This is the single biggest failure mode; guard it first.
- **A failure gallery.** The board demonstrates what red looks like (one deliberately failing
  example, narrated), so green means something and Sean can see the board is *able* to fail.
- **An honesty strip.** A permanent footer stating in plain english what the board does *not*
  check ("not checked here: speed under heavy load, real email delivery, sources behind
  logins"). An always-green board claiming total coverage is decoration, not validation.
  This is [[06-qa-operating-model]]'s honesty check made structural.
- **The two-read rule:** any board element needing a third read has failed its audience.
  *(Sean-approved amendment, 2026-07-09.)*

---

## The mechanisms menu (pick per project — not all apply)

- **Contract board** (the default home screen): one row per contract — plain sentence, status
  pill (verified / needs your eyes / failing), last-run time, "show me."
- **Narrated runs:** tests emit first-person plain-english narration of what they did,
  rendered as a story log rather than assertion output.
- **Data X-ray:** for data-heavy work — one sample record stepped through the pipeline; what
  came in, what each stage changed (highlighted), what went out, with row counts and
  "does-this-smell-right" stats in plain english.
- **Input playground:** knobs, dropdowns, and sample-data pickers wired to the real logic so
  Sean can poke the edges himself — manual flow-testing extended to code without a UI.
- **Before/after diff viewer:** for anything transforming files, data, or visuals —
  side-by-side with changes highlighted, plus an "approve as new expected result" interaction
  (visual-regression review, generalized).
- **Live probe overlay:** while Sean clicks through the real app, a side panel narrates what
  fired backstage ("saved ✓ · notification queued ✓ · nothing deleted ✓").

---

## Build procedure (how Claude constructs one)

1. **Contracts first.** Draft the numbered register from the ask; get Sean's approval before
   building. Ambiguity in a contract is resolved now, not discovered at review.
2. **Tests wear two hats.** Each contract maps to at least one automated check written to
   emit plain-english narration alongside its assertion. One source of truth, two renderings
   (CI output for machines/engineers, the board for Sean).
3. **Sandbox before features.** Stand up the invented-sample-data world first, so
   non-destructiveness is structural, not retrofitted.
4. **Board as a self-contained page** per [[artifact-standards]]: single `.html` (data
   inlined) when static output suffices; the launcher package when it must execute checks
   live. Named and versioned like any artifact.
5. **Populate the failure gallery and honesty strip** before first delivery — they are part
   of round one, not polish.
6. **Deliver with the gate.** Run the pre-delivery gate
   ([[02-shared-references/delivery-playbooks/README|Delivery Playbooks README]]); in
   `centric-engineering`, confirm the engineer-facing evidence exists independently of the board.
7. **Fit check.** On first open, ask Sean whether the board answers at a glance; run
   refinement questions; iterate as a versioned artifact. *(Sean-approved amendment,
   2026-07-09.)*

## Anti-patterns

- The board as afterthought — offered once, never updated, drifting from the code.
- Hand-authored statuses (theater) instead of rendered real checks.
- A board that requires terminal commands, environment setup, or reading logs.
- Always-green with no failure gallery and no honesty strip.
- In `centric-engineering`: the board presented to engineers as a substitute for tests.
- Glossy ELI5 — plain language achieved by dropping the caveats.
