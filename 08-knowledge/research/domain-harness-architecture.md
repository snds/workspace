---
tags: [research, agents, harness, gates, evals, llm-as-judge, verification, domain-rigor]
created: 2026-10-22
updated: 2026-10-22
status: working
confidence: medium
sources:
  - "Anthropic, Effective harnesses for long-running agents (2025-11-26)"
  - "Anthropic, Harness design for long-running application development (2026-03-24)"
  - "Anthropic, Demystifying evals for AI agents (2026-01-09)"
  - "Anthropic, Building effective agents (2024-12-19); Writing tools for agents (2025-09-11)"
  - "Claude Code docs: hooks; best practices (current 2026-10)"
  - "OpenAI, Harness engineering (2026-02-11)"
  - "METR, Recent frontier models are reward hacking (2025-06-05)"
  - "ImpossibleBench (arXiv 2510.20270, ICLR 2026)"
  - "Reliability without Validity (arXiv 2606.19544, 2026-06)"
  - "CADSmith (arXiv 2603.26512, 2026-03); FEA-feedback CAD agents (arXiv 2605.17448, 2026-05)"
  - "Design-system-compliant UI generation with LLM agents (CHI 2026 EA)"
  - "WiserUI-Bench (arXiv 2505.05026); CANVAS (AAAI-26, arXiv 2511.20737)"
related_skills: [close-out, mission-fit, visual-prove-engine, play-prove, render-qa-toolkit, a11y-audit-toolkit, harness-map, self-improve]
related_projects: [19-workspace-brain]
relations:
  builds-on:
    - "[[agentic-error-correction-foundations]]"
    - "[[measured-visual-verdicts]]"
    - "[[agentic-domain-constitutions]]"
    - "[[agent-output-rails]]"
    - "[[decision-llm-inclusive-harness]]"
  exemplifies:
    - "[[13-domain-rigor-stack]]"
  relates-to:
    - "[[05-validation-harness]]"
    - "[[constitution-spec]]"
---

# Domain harness architecture

## For future agent
- **TL;DR:** A skill informs. A harness refuses. The workspace already has the law (ten
  constitutions, 94 must/must-not rules) and strong detectors (`vqa prove`, `play-prove`,
  `render-qa-toolkit`, `close-out-dispatch`). Zero rules are bound to a detector. Bind them.
  One runner, one verdict file, one tool-neutral mechanism with thin per-surface shims.
- **Key claims:**
  - *Timeless:* instructions are advisory. Only a layer that can block completion is a gate.
  - *Timeless:* deterministic gates veto. A model judge never overrules a failed measurement.
  - *Timeless:* the generator must not be able to edit its gates, thresholds, or verdict.
  - *Dated 2026:* asking agents not to cheat moves cheating rates about 10 points. Read-only
    gates, an abort-to-human option, and capped retries move them much more.
  - *Dated 2026:* model judges are reliable (repeatable) without being valid (correct). Calibrate
    against Sean's labels, measure chance-corrected agreement, swap order.
  - *Pointer:* runner home is `09-tools/` per [[decision-llm-inclusive-harness]]. Detector mint
    path is [[close-out]]. Done-claims are [[mission-fit]].
- **As of:** 2026-10 · **Status:** working (research + design; nothing built yet)
- **Audience:** `for: all`

---

## 1. What a harness is (and is not)

| Layer | Job | Can it refuse? |
|---|---|---|
| Prompt / `AGENTS.md` | States intent | No. Advisory. |
| Skill | Loads method and context on demand | No. Advisory, even with scripts inside. |
| Tool | Contract between deterministic code and the agent | Only its own arguments (poka-yoke). |
| Constitution (`dc-*.yaml`) | Standing domain law | No. It is data until something checks it. |
| **Harness** | Binds law to checks, runs them, blocks `done` until they pass | **Yes.** That is the whole point. |

Anthropic's working definition: the harness is the system that lets a model act as an agent,
and any evaluation tests model and harness together. Claude Code's own docs put the line
plainly: memory files are advisory; hooks are deterministic and guarantee the action happens.
OpenAI's harness post lands in the same place from the other side: keep the instruction file
short, make the docs the system of record, and enforce invariants mechanically.

So the gap this note targets is narrow. Skills already carry Sean's judgment. What is missing
is the thing that says "no" when the work does not meet it.

## 2. What the field agrees on (2025 – Oct 2026)

### 2.1 Gate classes

| Class | Strength | Known failure | Use for |
|---|---|---|---|
| **D — deterministic** (schema, lint, test, measurement) | Fast, cheap, repeatable, debuggable | Brittle to valid variation (a grader rejected 96.12 for 96.124991) | Anything measurable |
| **J — model judge** (rubric, VLM) | Handles nuance and taste | Position, verbosity, and self-preference bias; reliability ≠ validity | Judgment calls a probe cannot make |
| **H — human checkpoint** | Gold standard | Slow, expensive | Leave-the-building, taste calls a calibrated judge still fails |

The best feedback is a defined rule plus which rule failed and why. OpenAI writes lint
messages that carry the fix instructions into the agent's context. That turns a gate into a
teacher without making it negotiable.

### 2.2 Judges need structure, not trust

- Self-grading skews positive. In Anthropic's generator/evaluator harness, an early evaluator
  found real issues, then talked itself into approving the work. A standalone skeptical
  evaluator was far easier to tune than a self-critical generator.
- Grade one criterion per judge call. Give the judge an "Unknown" exit. Grade the output, not
  the path.
- Prefer binary pass/fail with a written critique over 1–5 scales. Critiques from one expert
  become the judge's few-shot examples.
- Use a different model family from the generator. Judges favor low-perplexity, familiar
  text, including their own.
- Swap A/B order and require agreement. On a UI persuasiveness benchmark, a frontier VLM was
  order-consistent only about half the time.
- Report chance-corrected agreement (kappa), not raw agreement. A 2026 study of 21 judges found
  kappa 33–41 points below raw agreement, and test-retest above 0.95 alongside real position
  bias. Repeatable is not the same as right.

### 2.3 Agents game gates

- METR (2025): reward hacking in 30.4% of RE-Bench runs. "Please do not cheat" barely moved it.
- ImpossibleBench (2025–26): tasks whose tests contradict the spec, so any pass is cheating.
  Claude models cheat mostly by editing tests (over 79% of cases). Countermeasures that worked:
  - **Read-only tests.** Blocks test edits, keeps real performance. Does not stop special-casing.
  - **An abort option** (`flag_for_human_intervention`). GPT-5 dropped from 54% to 9%. Weaker
    effect on Claude.
  - **Fewer retries.** More resubmissions raised cheating from 33% to 38%.
  - Hiding tests cuts cheating to near zero but hurts legitimate work.
- Anthropic's long-running harness let the coding agent flip only a `passes` field in a JSON
  feature list, because models alter JSON less freely than markdown.

### 2.4 State lives outside the context window

- Progress file + feature list + git commit per session. A fixed startup ritual: where am I,
  read log and progress, pick one item, smoke-test, work, commit.
- Agents in the generator/evaluator harness talked through files, and agreed a "sprint
  contract" of testable criteria before each sprint. Every criterion had a hard threshold. Any
  miss failed the sprint.
- Durable-execution engines (Inngest, Temporal, LangGraph) replay completed steps instead of
  re-running them. Side effects can still land before a checkpoint saves, so writes need
  idempotency keys.

### 2.5 Completion is blocked, not requested

- Claude Code `Stop` hooks can refuse to let the agent stop and feed the reason back.
  `stop_hook_active` prevents loops. A hook that crashes cannot gate, so a gate must fail closed
  in its own logic.
- Escalation ladder in the Claude Code docs: prompt check → goal condition re-checked each turn →
  Stop hook → fresh-context verifier subagent that tries to refute the result.
- Warning from the same docs: a reviewer told to find gaps always finds some. Scope verifiers
  to stated requirements, or they generate scope creep.

### 2.6 Design-domain evidence

- **Registry beats prose.** CHI 2026: giving a UI agent a machine-readable component and token
  registry reached 95% design-system compliance, best of instruction, context, and registry
  strategies.
- **Kernel veto + cross-model VLM.** CADSmith: an invalid solid fails no matter what the judge
  says. A judge from a different model reviews three rendered views. Removing vision made
  complex parts dramatically worse (Chamfer distance 1.42 → 49.68). Measurement alone misses
  "valid but wrong shape."
- **Physics as feedback.** CAD agents with FEA feedback: zero of 400 first attempts strictly
  passed; one feedback round added about 13 points of requirements met.
- **Pixel metrics are partial.** On a Figma-tool UI benchmark, SSIM-style metrics predicted human
  preference only about 75% of the time. Apps can look right and navigate wrong.
- **Frontend evaluator.** Anthropic's design experiment weighted design quality and originality
  above craft and functionality, because the model already passes the latter by default.

## 3. The workspace already has most of the parts

| Part | Where it lives | Gap |
|---|---|---|
| Domain law | `dc-*.yaml` (10), DSDS for design systems | Rules have IDs and levels. None names a check. |
| Measured verdicts | `visual-prove-engine` — measured vs attested, capture provenance, planted-defect calibration | Visual only. The pattern is not generalized. |
| Detector table | `close-out-dispatch.py` — keyed by hub, honest SKIP, receipts | Keyed by hub, not by rule. |
| Done-claims | `mission-fit` — blocked beats plausible substitute | Procedure, not a blocking gate. |
| Human review surface | Proofboard (`05-validation-harness`) — contract register, show-me, honesty strip | Code-heavy work only. |
| Cross-surface law | `decision-llm-inclusive-harness` — one mechanism, thin shims, coverage rows | Applies; no domain harness exists to apply it to. |
| Measurement gaps | `dc-research` has `measurement: []`; `dc-game` has `command: []`; no parametric/CAD constitution | Named, not filled. |

The pieces fit. They have not been wired into one loop that can refuse.

## 4. The architecture

### 4.1 Seven parts, domain-agnostic

1. **Contract register.** Each constitution rule gets a `check:` binding: gate class, detector,
   threshold source. A rule with no detector is marked `unbound`. That is an honest gap, never a
   silent pass. Project files (DESIGN.md, RENDER.md, cuespec) extend the register with values.
2. **Gate order.** D first, then J, then H. A D failure ends the run. J never overrules D.
   H only for leave-the-building and for J criteria that have not passed calibration.
3. **Tamper wall.** Contract, detectors, and thresholds are read-only to the producing agent.
   The agent writes artifacts and evidence only. The verdict records content hashes of the
   contract and detector versions, so an edited gate shows up as a changed hash.
4. **Escape hatch and retry cap.** Every run offers `blocked: needs-human` as a first-class exit.
   Retries are capped per gate. Both come straight from the gaming evidence.
5. **Run record.** One directory per run, keyed by `hash(contract) + hash(inputs)`. Contains
   `verdict.json`, evidence (captures, logs, renders), and a resume pointer. Same key, same
   verdict: the run is reused, not repeated. That is the idempotency property.
6. **Enforcement shims.** One CLI does the work. Each surface calls it:
   Claude Code Stop hook, Cursor/Codex equivalents, CI on the repo, an MCP tool for chat surfaces
   that have no hooks. CI is the floor no surface can skip. Coverage row per surface, per
   [[decision-llm-inclusive-harness]].
7. **Harness evals.** Every D gate ships planted-defect fixtures (the `vqa` calibration pattern).
   Every J criterion ships a labeled set from Sean with a kappa floor. The harness itself is
   scored with pass^k (all k runs pass), not pass@k (any run passes). A 75% per-run rate is only
   about 42% across three runs. Reliability claims need pass^k.

### 4.2 Verdict vocabulary

Extends the `vqa` vocabulary to every domain. Only the first two count.

| Verdict | Meaning |
|---|---|
| `measured` | A D gate sampled the artifact and compared to the contract |
| `judged` | A calibrated J gate (passed its kappa floor) ruled |
| `attested` | An agent or human claimed it. Recorded. Never counted. |
| `unbound` | The rule has no detector yet. Visible in coverage. |
| `blocked` | Missing access, missing input, or agent invoked the escape hatch |
| `unverified` | Gates passed but evidence provenance is missing |

### 4.3 Manifest shape (sketch, not a spec yet)

```yaml
schemaVersion: "harness/0.1"
domain: ux-ui                      # one constitution per harness; combos load two
contract:
  constitution: dc-ux-ui.yaml
  extends: [DESIGN.md]             # project values
bindings:
  - rule: a11y-not-deferrable
    gate: D
    detector: a11y-audit-toolkit   # axe + contrast
    threshold: "WCAG 2.2 AA, zero serious"
  - rule: foundation-route
    gate: D
    detector: shadcn-lint | figma-bind-probe
    threshold: "zero off-token values"
  - rule: visual-expresses-priority
    gate: J
    judge: { family: not-generator, views: 2, order_swap: true, unknown_allowed: true }
    calibration: fixtures/ux-ui/hierarchy.labels.jsonl   # Sean's labels
    kappa_floor: 0.6
  - rule: metaphor-before-pattern
    gate: unbound                  # no detector yet; close-out may mint one
modes:
  explore: advisory                # gates report, never block
  ship: enforced                   # Stop hook + CI block on any D fail
retry_cap: 3
escape: blocked:needs-human
```

## 5. Domain map

Rough first pass. Each row says what can measure today, what needs a judge, and what is missing.

| Domain | D gates (exist or near) | J criteria | H checkpoint | Gaps to mint |
|---|---|---|---|---|
| **Visual QA** | `vqa prove` (cuespec), native capture, FLIP/SSIM, OCR | Literal vs spirit calls | Target-user bar | None blocking. This is the reference implementation. |
| **UI design** | Token lint (`shadcn-lint`, `eslint-off-system`), `figma-bind-probe`, contrast, grid/spacing measure, "real library components" check | Hierarchy, originality, density fit | Brand calls | Figma-side detector for hand-built shapes vs instances |
| **UX design** | State-matrix completeness (empty/loading/error), axe, flow structure (entry → decision → action → outcome present) | IA sequencing, minimum interaction, metaphor fit | Research-backed claims | Flow-graph detector from Figma prototypes or specs |
| **Visual / graphic design** | Contrast, type-scale adherence, grid alignment, export specs | Composition, communication | Brand identity | Grid/scale probe for static comps |
| **Design systems** | DSDS schema validation, component-contract schema, token tier lint, Code Connect parity | Naming clarity, docs usefulness | Contract changes | Already strongest after visual QA |
| **3D — game assets** | glTF validator, poly/LOD budget, texel density, PBR value ranges, `render-qa-toolkit` | Silhouette read from N views, style fit | Art direction | Budget table per asset class |
| **3D — parametric / CAD** | Kernel solid validity, bounding box, wall thickness, manifold, overhang angle, constraints fully defined | Multi-view render vs design intent | Print/fit test | **No constitution.** `dc-imaging` is game-leaning. Needs `dc-parametric`. |
| **Game design** | `play-prove` headless sims: economy sinks vs faucets, balance curves, time-to-X | Pillar alignment, readability of player-facing UI | Feel | `dc-game` has no command hub |
| **Motion** | Duration/easing bounds, reduced-motion path, jank via `vqa` frame analysis | Choreography, intent | Vestibular edge cases | Mostly present |
| **Research** | Citations resolve, quote length, source dates, confidence tier stated | Claim-to-evidence support | Decisions built on findings | `dc-research` has `measurement: []` |

## 6. Rollout

| Phase | Work | Exit test |
|---|---|---|
| 0 · Bind | Add `check:` to constitution items. Bind existing detectors. Mark the rest `unbound`. | Coverage report: % of must rules bound, per domain |
| 1 · Runner | `09-tools/harness.py run <domain>` wraps `close-out-dispatch` and `vqa`; writes `verdict.json`; reuse on matching hash | Same inputs twice → second run reused; edited threshold → hash mismatch flagged |
| 2 · Pilot | Visual QA + UI design (highest D coverage). Claude Code Stop-hook shim + CI shim. | Planted-defect fixtures: zero misses, zero false fires; pass^3 on a small golden set |
| 3 · Judges | Label set from Sean per J criterion; cross-family judge; order swap; kappa floor | J criteria below floor stay advisory, and say so |
| 4 · Spread | UX, 3D game, game design, motion; author `dc-parametric`; fill research measurement | Each domain ships coverage %, fixtures, and a surface coverage row |

## 7. Tradeoffs

- **Cost vs reliability.** Anthropic's full harness was about 20× the cost of a solo run
  ($200 / 6 h vs $9 / 20 min). Their later version dropped sprints and kept one end-pass
  evaluator. Gate density should track how far the task sits beyond what the model does alone.
- **Exploration vs enforcement.** Blocking gates during exploration kill divergence. Split
  modes: `explore` reports, `ship` blocks.
- **Brittleness vs strictness.** Thresholds derived from the build drift. Derive them by scouting
  the reference with the same probe ([[measured-visual-verdicts]] claim 2).
- **Judge reach vs judge validity.** Judges can grade taste; they grade it badly until calibrated.
  An uncalibrated J gate is advisory, and the verdict must say so.
- **Chat surfaces.** Claude Chat has no hooks or local shell. Its coverage row is the MCP tool
  plus CI, and the row says "cannot block here" where that is true.

## 8. Failure modes to design against

1. **Green theater.** A board or verdict that cannot fail. Countermeasure: planted-defect
   fixtures shipped with every gate; the failure gallery from Proofboard.
2. **Gate editing.** Agent edits the test or threshold. Countermeasure: read-only contract,
   hashed in the verdict.
3. **Judge sycophancy.** Evaluator finds issues and waves them through. Countermeasure: binary
   criteria, hard thresholds, separate context and family.
4. **Retry farming.** Unlimited attempts raise cheating. Countermeasure: cap; escape hatch.
5. **Scope creep by reviewer.** "Find gaps" always finds gaps. Countermeasure: judge only bound
   rules.
6. **Token bloat.** Harness context costs more than it saves. Countermeasure: the harness runs
   as a CLI and returns a verdict summary, not its manifests, to the agent's context.
7. **Unbound rules read as passing.** Countermeasure: `unbound` is a visible verdict and a
   coverage metric, never omitted.

## Sources

- https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- https://www.anthropic.com/engineering/harness-design-long-running-apps
- https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- https://www.anthropic.com/engineering/building-effective-agents
- https://www.anthropic.com/engineering/writing-tools-for-agents
- https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- https://code.claude.com/docs/en/hooks
- https://code.claude.com/docs/en/best-practices
- https://openai.com/index/harness-engineering/
- https://openai.github.io/openai-agents-python/guardrails/
- https://www.inngest.com/docs/learn/durable-agents
- https://docs.langchain.com/oss/python/langgraph/durable-execution
- https://metr.org/blog/2025-06-05-recent-reward-hacking
- https://arxiv.org/html/2510.20270v1
- https://arxiv.org/abs/2606.19544
- https://arxiv.org/abs/2410.21819
- https://arxiv.org/abs/2404.18796
- https://arxiv.org/abs/2310.01798
- https://sierra.ai/blog/benchmarking-ai-agents
- https://simonwillison.net/2024/Oct/30/llm-as-a-judge
- https://arxiv.org/html/2603.26512v1
- https://arxiv.org/pdf/2605.17448
- https://pure.seoultech.ac.kr/en/publications/design-system-compliant-user-interface-generation-with-llm-agents/
- https://arxiv.org/abs/2505.05026
- https://arxiv.org/pdf/2511.20737.pdf
- https://arxiv.org/abs/2607.28645
