# Intent Coordination Operating Model

*Cross-cutting L1 for multi-agent work. Where [#08](08-workspace-contribution-framework.md) answers where durable state lives, [[open-agent-engine]] answers how tasks move, and [[mission-fit]] answers whether `done` is true, this framework answers **how many agents stay aligned to Sean's designed intent** instead of each guessing from a chat thread.*

Portable principles drawn from [Intent](https://intentapp.dev) (Augment, 2026 public beta) and mapped onto this workspace. The Mac app is optional tooling, never the contract.

---

## The core conviction

**The job is outcomes, not prompts.** When agents write the code, Sean operates at the altitude of designed intent: what must exist, where, and how close it must be to the northstar. Coordination happens through a **living spec** that every agent reads and updates. Chat is steering, not the source of truth.

A swarm with no shared spec is N private guesses. Same-author self-check is polish, not verification ([[agentic-error-correction-foundations]]). Isolation without a spec still collides on meaning.

---

## When this framework invokes

Load when the work involves any of:

- Two or more agents, worktrees, or parallel implementors
- A multi-file outcome that would otherwise live only in the current thread
- Explicit language: living spec, coordinate agents, agent orchestration, intent coordination, intentapp
- Fanning work after a plan, then proving it against a checklist Sean already set (Figma fidelity, NORTHSTAR, Definition of Done)

**Always, even on small work:** name the outcome in mission-fit language ("what should exist, and where?") before acting. **A living spec file** is required only at the scale above. Single-agent, single-file, short work may keep that outcome in the Live handoff block.

Do not load this as always-on session tax. Route it.

---

## The pipeline

Four ordered stages. A stage is complete when its artifact exists and its gate is satisfied, not because someone described the stage in chat.

```
intent  →  spec (approve)  →  isolate + implement (waves)  →  verify vs spec
```

### Stage 1: Intent

**Activity.** Restate designed intent in outcome language. Name the northstar (Figma, `NORTHSTAR.md`, contract, user quote). Resolve the [context profile](../02-shared-references/delivery-playbooks/00-context-profiles.md) before any repo action. Name the Open Engine lane if movement will be tracked.

**Done-gate.** Outcome, surface, and bar are written. Profile is declared, not guessed.

### Stage 2: Living spec (human-approved)

**Activity.** A coordinator drafts [[intent-spec]] (copy `00-bootstrap/templates/intent-spec.md`). The spec is the shared plan: task graph, dependencies, waves, specialist skills, evidence each task must produce. Sean (or an explicit approve rule on the spec) reviews **before** implementors write.

**Done-gate.** Spec file exists in git (project `docs/INTENT.md` or the owning repo). Approval is recorded on the spec. Implementors have not started.

### Stage 3: Isolate and implement

**Activity.** Each writable task gets its own isolation: a git worktree (or equivalent) so agents do not share a dirty tree. Hold dependents until prerequisites verify. Specialist skills load from the registry `load_chains`, not from a private prompt paste. Update the spec when reality changes (living, not a frozen brief).

**Done-gate.** No two writers on the same worktree. Waves respect `depends_on`. Spec changelog records material plan changes.

### Stage 4: Verify vs spec

**Activity.** A **verifier** with different evidence access than the author checks the spec's checklist: tests, `vqa prove`, workspace validators, mission-fit world-state, CI. Failures return to implementors with spec diffs, not a new vibe.

**Done-gate.** Every checklist item is measured, attested, or explicitly waived with owner. Author prose is not the verdict. [[mission-fit]] `done` is a claim about the world.

**L3 enforcement:** `python3 09-tools/intent-run.py` (`gate`, `ready`, `worktree add`, `verify`). The Intent desktop app (`install-app` / `open-app`) is optional GUI over the same protocol, not a substitute for the spec file.

Then land per [#07](07-integration-and-review-framework.md) and the context profile (employer: branch → PR → human review; never auto-merge).

---

## What maps onto systems we already have

| Intent product idea | Workspace home | Do not replace with |
|---|---|---|
| Living spec | [[intent-spec]] file in the owning project/repo | Chat history, Linear issue body |
| Coordinator | Parent agent + this framework + `intent-coordination` | A second queue |
| Implementors | Task/worktree agents loading domain skills | One mega-thread doing everything |
| Verifier | Independent evidence: [[mission-fit]], #06, domain L3 (`vqa`, validators, CI) | Same model restating the first answer |
| Isolated workspaces | Git worktrees (Cursor worktrees skill is technique) | Shared dirty checkout |
| Movement / claim lock | [[open-agent-engine]] (pointers + receipts only) | Spec pasted into issues |
| Continuity baton | Project Live handoff (points at the spec) | Parallel private memories |
| Designed-intent bar | #06 target-user lens + northstar / Proofboard | "Looks good" from the implementor |

---

## Absolute bans

1. **Chat as the spec.** If two agents need the plan, it is a file.
2. **Author as sole verifier** for consequential work. Transcript ≠ proof.
3. **Requiring the Intent Mac app, Augment credits, or Context Engine MCP** for the protocol to count. BYOA is the portable path; those tools may assist on a machine that has them.
4. **Substance in Open Engine issues.** Spec stays in the workspace or owning repo.
5. **Starting implementors before spec approval** on work that required a living spec.
6. **Two writers, one worktree.** Isolation is mechanical, not a request in the prompt.
7. **Guessing a context profile** so parallel agents commit under the wrong wall.

---

## Relationship to other frameworks

- **#06** — the bar on each fidelity checklist item (target user, not technical correctness).
- **#07** — how verified waves land (partition, PR, review).
- **#08** — where the spec file lives; write gates still apply.
- **#11** — premortem before the spec's task graph is approved.
- **#13** — this is the L1 for the coordination cluster; `intent-coordination` is L2.
- **#14 / #16** — engineering and security done-gates still apply inside implementor tasks.

---

## Anti-patterns

- Treating Intent's demo "hundreds of agents" as a goal. Fan-out only when the spec's graph has real independent nodes.
- Updating the spec after ship to match whatever landed (spec laundering).
- A coordinator that also implements and then "verifies" in the same turn.
- Cloning Augment's UI into this vault. We needed the protocol, not the product shell.
