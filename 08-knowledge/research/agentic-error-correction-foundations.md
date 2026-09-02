---
tags: [research, agents, reliability, verification, error-correction, loops, second-brain]
created: 2026-08-26
updated: 2026-08-26
status: working
confidence: medium
sources:
  - "Madaan et al., Self-Refine (NeurIPS 2023)"
  - "Shinn et al., Reflexion (NeurIPS 2023)"
  - "Gou et al., CRITIC: Tool-Interactive Critiquing (ICLR 2024)"
  - "Song et al., Mind the Gap: generation-verification gap (ICLR 2025 Oral)"
  - "Sample More, Reflect Less (arXiv 2607.28576, 2026)"
  - "Reliability without Validity, LLM-as-judge evaluation (arXiv 2606.19544, 2026)"
  - "Anthropic, Building verification loops in Claude Code with skills (2026-07-22)"
  - "Liang et al., Multi-Agent Debate / Degeneration-of-Thought (EMNLP 2024)"
  - "Du et al., Improving Factuality through Multiagent Debate (2023)"
  - "Pitre, Use AI to Need Less AI (via [[component-contracts-and-schemas]])"
related_skills: [failure-mode-premortem, visual-qa-toolkit, native-visual-eval, visual-reference-replication, open-agent-engine, workspace-bootstrap]
related_projects: [19-workspace-brain, 20-lcars-generative-interface]
relations:
  builds-on:
    - "[[contracts-first-delivery]]"
    - "[[silent-degradation-in-fenced-layers]]"
    - "[[adversarial-verify-label-volatility]]"
    - "[[visual-reference-replication-findings]]"
    - "[[visual-failure-mode-ledger]]"
    - "[[component-contracts-and-schemas]]"
    - "[[knowledge-vault-design]]"
    - "[[agent-work-queue-boundaries]]"
  exemplifies:
    - "[[13-domain-rigor-stack]]"
    - "[[06-qa-operating-model]]"
    - "[[11-anticipatory-failure-analysis]]"
  relates-to:
    - "[[agentic-ds-context-model]]"
---

# Agentic error correction: foundations for a second brain that refuses surprise

## For future agent
- **TL;DR:** Same-model self-critique is not error correction. Correction starts when an *independent* layer can refuse. Mechanical close landed 2026-08-26: #06 detector check, embedded prove/validate, negative fixtures, observable routing skips, `/optimize` seven-surface ECC. Do not build a parallel agent framework.
- **Key claims:**
  - *Timeless:* unexpected results cannot be fully removed from a stochastic generator. The reachable property is: surprises are detectable, non-silent, and non-repeatable.
  - *Timeless:* the governing quantity is the generation-verification gap. If the critic is the same class of model as the author, the loop mostly restyles the first answer.
  - *Timeless:* authority belongs to whatever layer can refuse deterministically (schema, test, SSIM, validator), not to whoever instructs loudest (`AGENTS.md` prose).
  - *Dated (as of 2026-08):* at equal token cost, extra samples beat Self-Refine / Reflexion rewrite loops on the sizes tested; Reflexion can silently never fire if the model judges itself correct.
  - *Dated (this vault):* we already observed the same failure family: VLM-as-measurement, Spirit-as-done, label volatility, silent degradation, tests-green ≠ Literal match.
  - *Pointer:* operational home is `07-projects/19-workspace-brain/`; do not invent a parallel brain.
- **As of:** 2026-08 · **Status:** working (field survey + workspace mapping; not yet a skill or framework)

---

## 0. Honesty bound

The ask is to reduce, then ultimately remove, unexpected results from every workstream.

**Removal is not a reachable property** of an LLM second brain. The model samples. Context is incomplete. Hooks drop. Triggers under-fire. A VLM will narrate pixels it did not measure. Declaring "zero surprise" as a done-gate licenses the exact failure this vault already named: completeness theater.

The reachable contract, stated as a falsifiable bar:

1. **Detectable.** A wrong result and a healthy-but-empty result are not the same value.
2. **Non-silent.** A fence, fallback, or skip emits *why* it fired.
3. **Non-repeatable as a silent class.** The first time Sean catches it, it becomes a ledger row, a validator, a cue, or a hard refuse. The second time the class is visible by construction.
4. **Overclaim banned.** If there is no independent detector for this workstream, the agent may not say "done / matches / verified" in the same voice as a workstream that has one.

That is error correction for this brain. Not "the model tries harder."

---

## 1. What "unexpected results" actually are here

Not one failure. Six families, all already evidenced in this vault.

| Family | What Sean sees | Vault evidence |
|---|---|---|
| **Invention as measurement** | Hex, radii, gutters, facts from model memory | [[visual-reference-replication-findings]] (VLM prose as spec) |
| **Wrong done-criterion** | Tests green, vibe match, "looks LCARS-ish" | Literal vs Spirit; tests-green ≠ visual done |
| **Silent skip** | Healthy empty, under-fired routing, swallowed exception | [[silent-degradation-in-fenced-layers]]; Layer-0 under-fire; hook payload drop |
| **Judge noise treated as grade** | CONFIRMED/REFUTED counts that will not reproduce | [[adversarial-verify-label-volatility]] |
| **Smoothed contract** | Artifact looks valid because an agent filled gaps | [[component-contracts-and-schemas]] LLM boundary trap |
| **Unwritten contract** | Violation looks like normal behavior | [[contracts-first-delivery]] |

A loop that does not change the *detector* for these families is decoration. Self-Refine on a vibe-matched screen still vibe-matches.

---

## 2. Field map: where the correction signal comes from

Organize the literature by **signal source**, not by paper name. That is the only split that predicts whether a loop will help this workspace.

### 2.1 Same-model self-signal (Self-Refine)

Generate → critique → revise, one model, no external world. Cheap. Helps style, format, clarity. Unreliable on hard reasoning and facts. 2026 equal-token work found rewrite loops lose to drawing another sample. Sycophantic critics can *degrade* the draft across rounds unless there is a stop rule (score worse → roll back).

**Use here:** last-mile prose polish after an independent check already passed. Never as the proof that a claim is true.

### 2.2 Environment / tool signal (CRITIC, Reflexion-with-reward, SWE loops)

The critic is a compiler, test suite, search engine, interpreter, SSIM, schema, CI job. Gou et al. (CRITIC): models struggle to self-verify without external feedback. Shinn et al. (Reflexion): convert a *failed unit test* into a verbal lesson in episodic memory. Anthropic coding agents: the high-leverage move is giving the agent tests or success criteria so the loop has a world to bounce off.

**Use here:** this is the native pattern of the workspace. Validators, `visual-qa-toolkit`, Proofboard, Construction IR, native pixels, CI. Prefer this over every other loop type.

### 2.3 Independent-model critic (debate, actor-critic, LLM-as-judge)

A second instance (or a "tit for tat" panel) critiques the first. Helps when the failure is *Degeneration-of-Thought*: once a model is confident, self-reflection cannot generate a novel thought even if the first stance is wrong (Liang et al., EMNLP 2024). Does **not** create ground truth. 2026 judge evals: raw agreement overstates chance-corrected discrimination; high test-retest can mask position bias (consistency-bias paradox); judge rankings do not transfer across benchmarks.

**Use here:** already learned. Adversarial verify labels are sampling noise. Multi-voice (`arch-guild`, `/framework-check`) is for surfacing disagreement, not for a headline score. If used as a gate: binary questions, k ≥ 3, report substance not counts, independently hand-check load-bearing claims.

### 2.4 Sampling / search (Best-of-N, self-consistency, Tree of Thoughts, LATS)

Spend the same tokens on more attempts, then pick by majority or by an *external* scorer. 2026 result: at equal cost, extra samples beat reflection rewrites on the sizes tested. Tree/MCTS wrappers help when the task is a search with a reward. They explode cost if the reward is another LLM shrug.

**Use here:** when no independent detector exists and the claim is discrete (a mapping, a classification, a cited fact). Not for Literal visual match (pixels are not a vote).

### 2.5 Human signal (andon, ledger, owner)

Sean catching a bug is the most expensive detector and the only one that currently closes classes this brain did not anticipate. Framework #11's self-improving loop is this: reactive catch → ledger row → proactive check next time. Nate B. Jones' operating point matches: the bottleneck moved to handoffs, state, receipts, and review, not to a more autonomous model. Open Engine in this workspace is the movement layer for that; it must not become a second substance store.

**Use here:** already the design. Do not try to replace Sean as the last detector. Make his catches cheap to convert into mechanical detectors.

### The generation-verification gap

Song et al. (ICLR 2025) formalize GV-Gap: how much you gain by re-weighting generations with the model's *own* verification scores. Self-improvement is governed by whether verification is *more precise* than generation. Prompting a good critic into existence is the thing that does not work. You build a critic (tools, schema, tests, pixels) or you borrow the world's.

This vault said the same thing in design-system language:

> Authority belongs to whatever layer can refuse deterministically, not whatever layer instructs loudest. A model can be talked around. A schema can't.

And in contract language: if an agent smooths the artifact between validation and consumption, verification stopped there. Everything after is inference on inference.

---

## 3. Loop structures that actually close

A useful loop has four parts. Missing any one makes it a prompt.

```
contract  →  act  →  independent detect  →  repair or refuse
     ↑                                        |
     +------------ memory / ledger ------------+
```

### 3.1 Prevent (cheapest)

Write the contract before the act. Refuse when unsupported. Load the right skill/foundation *before* work, not after a bad first pass.

This workspace already: context profile, trigger routes, skill `load_chains`, Construction IR, Proofboard contracts, `#11` premortem, epistemic "question every assumption," foundations-first color/a11y.

### 3.2 Detect (the scarce resource)

Name the independent detector *before* acting. If none exists, the workstream is judgment-only (see §5).

Anthropic's skill-loop taxonomy maps cleanly onto ours:

| Anthropic shape | Workspace analog | Failure if skipped |
|---|---|---|
| Standalone `/verify` | `/qa`, `/framework-check`, `visual-qa-toolkit` | Human has to remember |
| Embedded in the producing skill | prove-gate inside `visual-reference-replication`; "run eslint before reporting" | Plugin skills overwrite; wrappers needed |
| Chained skills | `/qa` then `/ds`; `#11` then `#10` then toolkit | Habit, not contract |
| On every PR / CI | `validate-*.py`, engineering CI, Proofboard | Prompt-only gates die at session boundary |

Direction of travel: standalone → embedded → chained → CI. Do not start from CI for a check still in flux.

### 3.3 Repair (bounded)

Loop while the detector fails, with:

- **Cap** 1–3 repair rounds (style) or until tests/cues pass (environment signal).
- **Rollback** if the critic pass scores worse than the draft (anti-sycophancy).
- **No retry of the full phase** when a sub-step failed (`gen-manifest` already: identify what failed, fix that).
- **Do not let the model decide the loop is unnecessary.** Reflexion-as-specified asked the model "are you correct?" and on small models never retried once. Forced retry or an external fail signal.

### 3.4 Remember

Persist the *class*, not the chat. Ledger row, knowledge entry, cue matrix, validator fixture, ADR. Reflexion's episodic memory is the right idea with the wrong store: the store is this vault, not the model's context window.

### 3.5 Escalate (andon)

Stop the line when:

- the detector is missing and the claim is load-bearing
- k independent judges disagree on substance (not on labels)
- the change is irreversible (#14 reversibility class)
- a fenced layer failed fatally (auth, quota, empty retrieval)

"I'll just generate something" is the hallucination that grounding literature exists to refuse.

---

## 4. What this workspace already is (inventory)

This is not a greenfield agent framework. It is a partially built reliability stack with uneven mechanical teeth.

### 4.1 Input-time (prevent)

| Mechanism | Layer | Mechanical? |
|---|---|---|
| Trigger routes + skill graph `load_chains` | routing | Partial (dispatcher injects; Cursor must obey AGENTS.md) |
| Context profile resolution | delivery | Prompt-injected; fail-safe = most restrictive |
| `#11` premortem + failure-mode ledger | visual/technique | Prompt-injected; ledger is durable |
| Construction IR before code | Literal visual | Skill-mandated; agents still skip |
| Epistemic standards (freshness, assumptions) | all claims | Prompt-injected |
| Doctrine precedence (frameworks > skills > plugins) | all | Prompt-injected; wrappers own bans |

### 4.2 Output-time (detect)

| Mechanism | Detector class | Mechanical? |
|---|---|---|
| `#06` pre-output gate | judgment checklist | Prompt-injected |
| `#10` native pixels | capture discipline | Prompt-injected; toolkit is mechanical once invoked |
| `visual-qa-toolkit` SSIM / Δe / alignment | instrumented | Mechanical |
| Literal cue matrix + prove.json | instrumented + named cues | Mechanical if run |
| `validate-integrity/links/workspace/capabilities` | schema / graph | Mechanical at commit / CI |
| Proofboard | human-verifiable contract | Mechanical if built |
| Engineering tests / CI / `#14` verify stage | environment | Mechanical in employer repos; workspace is docs-first |
| Browser verification user-rule | environment | Depends on agent actually driving the app |
| `/framework-check` | LLM-on-LLM | Not independent |
| `arch-guild` multi-voice | LLM-on-LLM | Disagreement surface, not a grade |

### 4.3 Memory (non-repeatable)

| Mechanism | What it captures |
|---|---|
| Visual Failure-Mode Ledger + `#11` self-improving loop | Technique-keyed classic fails |
| `08-knowledge/` + `_INDEX` triggers + Layer-1 FTS | Durable lessons, retrieval |
| SESSION-STATE Live handoff | Continuity of *this* thread |
| Open Engine receipts | Movement, not substance |
| `#stale` / typed `refutes` | Epistemic supersession |

### 4.4 Known holes in the stack itself

- **Prompt ≠ refuse.** `AGENTS.md` can be talked around. Validators cannot.
- **Uneven detectors.** Vault writes and Literal visual have instruments. Research, planning, and most prose do not.
- **Gates degrade silently.** Hook payload drop, trigger under-fire, `except: return None`, progress counters on the cheap phase. Same family as MediaSentinel.
- **Token frugality fights loops.** Extra critique rounds are a recurring per-session cost. They must earn their tokens against an independent detector, or they are completeness theater.
- **Model-decided stop.** Agents declare done when the skill's prove-gate was never run (LCARS: green tests ≠ Matches Literal).
- **Maintenance loop now in `/optimize`.** Seven-surface system ECC (skill graph, contract, knowledge, memory, routing, validators, handoff): probes first, then judgment. Distinct from per-task loops. Nightly recipe remains opt-in cron, not a substitute.

---

## 5. Narrowing: the stack this brain should run

Do not add a parallel "agent framework." Close the loops we already named.

### 5.1 One rule

**Independent measurement, or refuse the done-claim.**

Same-model critique may still run as polish. It never upgrades a judgment-only workstream into a verified one.

### 5.2 Workstream detector registry

Every workstream names: contract artifact, independent detector, repair loop, escalate rule. If detector is "none," done-language is banned.

| Workstream | Contract | Independent detector | Repair | Escalate |
|---|---|---|---|---|
| Vault / skill graph writes | ontology + frontmatter spec | `validate-*.py` | fix, re-run | CI red |
| Literal visual | NORTHSTAR + Construction IR + cues | native crops + toolkit (SSIM/Δe/align) | IR-driven edit, re-prove | Partial/Fail verdict, never "matches" |
| UI/code in an app | Proofboard sentences + user-rule | tests + real browser path | fix failing path | cannot claim complete |
| Engineering delivery | `#14` change contract | tests, scan, SLO signal | verify stage | no rollback story → do not ship |
| Routing / retrieval | trigger-routes + registry | dispatcher smoke + `vault-retrieve --eval` | golden-set fail → reopen | under-fire must be visible, not silent skip |
| Queue / unattended | Open Engine skill + lane config | receipts; `--disallowed-tools` | do not run | dual-lane credentials = stop |
| Research / planning / prose | `#04` confidence tier + `#15` decision frame | **none by default** | sample / hand-check load-bearing claims | overclaim → refuse |

The last row is the largest remaining surprise surface. Treat it as such.

### 5.3 Judgment-only protocol (prose, research, plans)

When there is no schema or pixel metric:

1. Name the confidence tier (#04) on load-bearing claims.
2. Split claims into checkable vs judgment. Checkable ones get a grep, a citation, a number with a source, or a "I did not verify."
3. If using a second model as critic: binary questions, k ≥ 3, report mapped substance, never a CONFIRMED count.
4. Prefer another sample over a rewrite when the question is discrete.
5. Never let the critic rewrite a draft that already passed a stronger detector.

This is [[adversarial-verify-label-volatility]] + [[experiment-validity-baseline]] applied to the agent itself.

### 5.4 What not to build

- A new top-level framework on day one. Three consumers first (#08). The consumers would be: visual prove, vault validate, engineering verify. Those already have L1s (#06/#11, #08, #14). This note is the cross-cut.
- Default Self-Refine / "reflect and retry" on every turn. Equal-token evidence says spend on samples or on detectors.
- LLM-as-judge scores as session KPIs. We measured that they do not reproduce.
- Unattended runners before `--disallowed-tools` (already a hard precondition).
- A second substance store (Linear issue bodies, chat memory, a new "agent brain" folder that duplicates `08-knowledge/`).

### 5.5 Promotion path (later, not this session)

If three workstreams keep restating the same protocol, *then* author a thin cross-cutting skill (working name `agent-verification-loop`) that owns:

- detector-or-refuse
- loop cap + rollback-if-worse
- empty ≠ broken on fenced layers
- write-the-ledger-row when Sean catches a new class

Until then: this entry + the existing skills. Token frugality wins.

---

## 6. Phased next actions (for 19-workspace-brain)

Ordered by leverage, not by novelty. Items 2–6 landed 2026-08-26 (mechanical close).

1. **Keep this as the map.** Load on error-correction / verification-loop / unexpected-results vocabulary. Do not auto-load on every session.
2. **Mechanical close of detectors we already have (landed).** Literal prove is part of implement, not a later `/verify`. Vault writes: done means the relevant validators ran this session; commit/CI is the backstop.
3. **Negative fixtures for validators (landed).** `python3 09-tools/test-validators.py` plus CI `validator-fixtures.yml`.
4. **Routing skips observable (landed).** Dispatcher emits a routing-coverage note when Layer 0 under-fires on a real prompt and lexical is empty/failed. Cursor: empty retrieve is not "nothing in the vault."
5. **Judgment-only done-language (landed).** `#06` detector check: name the independent detector or refuse verified-voice.
6. **`/optimize` as system-level ECC (landed).** Seven-surface maintenance loop. Distinct from per-task loops.
7. **Only then** consider a wrapper skill, and only if (2)–(5) are still being skipped.

---

## 7. Sources (dated)

Field (as of 2026-08):

- Madaan et al., *Self-Refine*, NeurIPS 2023
- Shinn et al., *Reflexion*, NeurIPS 2023 / arXiv 2303.11366
- Gou et al., *CRITIC*, ICLR 2024
- Song, Zhang, Eisenach, Kakade, Foster, Ghai, *Mind the Gap* (GV-Gap), ICLR 2025 Oral / arXiv 2412.02674
- *Sample More, Reflect Less*, arXiv 2607.28576 (2026)
- *Reliability without Validity* (LLM-as-judge), arXiv 2606.19544 (2026)
- Anthropic, *Building verification loops in Claude Code with skills*, 2026-07-22
- Liang et al., Multi-Agent Debate / Degeneration-of-Thought, EMNLP 2024
- Du et al., Multiagent Debate for factuality, 2023
- Zhou et al., LATS (MCTS + reflection), ICML 2024

Workspace (pointers, not restated):

- [[contracts-first-delivery]] · [[silent-degradation-in-fenced-layers]] · [[adversarial-verify-label-volatility]]
- [[visual-reference-replication-findings]] · [[visual-failure-mode-ledger]]
- [[component-contracts-and-schemas]] · [[knowledge-vault-design]] · [[agent-work-queue-boundaries]]
- Frameworks #06, #10, #11, #13, #14, #15 · Proofboard `05-validation-harness.md`
- Project home: `07-projects/19-workspace-brain/`
