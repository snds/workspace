---
name: mission-fit
description: >
  Check whether this workspace harness can finish a real job — outcome, access,
  quality, evidence, supervision — before trusting an agent "done". Catches false
  success (completion claimed while world state disagrees). Run when Sean says
  "mission fit", "false success", "can this agent finish", "audit this job",
  "trust done", or after harness-map when a recurring job has already made him
  check behind the agent. Read-only first; blocked beats plausible substitute.
  Adapted from Nate B. Jones' Mission Fit companion to Clean My AI Harness.
aliases: [mission-fit, false-success-check, agent-done-check]
triggers:
  - mission fit
  - mission-fit
  - false success
  - false-success
  - can this agent finish
  - trust done
  - audit this job
  - agent lied
  - blocked not done
tier: cross-cutting
domain: workspace
related: [harness-map, open-agent-engine, workspace-bootstrap]
surfaces: ["*"]
spec_version: "2.0"
---

# Mission fit — jobs vs harness, before you trust `done`

[[harness-map]] shows what **shapes** the agent. This skill checks whether that setup
can finish the **jobs you actually give it** — with the right access, quality bar,
proof, and supervision.

**An agent does not pass because it sounds finished.** It passes when the real outcome
can be verified in the system that owns the change.

Standing project home: `07-projects/19-workspace-brain/` — read **Live handoff** when
this is the session's main work.

Adapted from Nate B. Jones' *AI Agent False Success* + Mission Fit guide
([natesnewsletter](https://natesnewsletter.substack.com/p/ai-agent-false-success));
aligned with [[05-validation-harness|Proofboard]], capability preflight in [[AGENTS]],
and [[open-agent-engine]] receipts. Not a paste of his product zip.

## Non-negotiables

1. **`done` is a claim about the world** — file exists, CI green, issue transitioned,
   Figma published, draft unsent with the *correct* attachment — not a chat closing line.
2. **The agent is never the sole witness** to consequential work. Transcript ≠ proof.
3. **Missing access → `blocked`**, never a plausible substitute that looks complete.
4. **A second agent counts only with different evidence access** — LLM-as-judge on the
   first agent's story alone is unreliable (false-success study: judges worse than a coin flip).
5. **Scale proof to consequence.** Money, external publish, delete, hard-to-reverse:
   human approval. Routine work: routine read-backs the agent can run itself.
6. **Read-only first.** Recommendations are numbered; nothing in the harness changes
   until Sean approves.

## When to run

- Explicit: "mission fit", "false success", "can this agent finish this", "trust done?"
- One recurring job that has already made Sean check behind the agent
- Before widening autonomy on a class of work (employer repo actions, Figma publish,
  mail/calendar, destructive scripts)
- After a [[harness-map]] cleanup, to verify the same jobs still stop correctly

**Prerequisite:** If no recent harness map exists for this surface, run [[harness-map]]
first (or skim its latest report) so Access/Supervision recommendations aren't guessing
at the setup.

## The question before the three checks

Before Outcome / Access / Quality / Evidence / Supervision, answer in **outcome
language** — no use of *done*, *complete*, or *successful*:

> **What should exist, and where?**

Example shape (spreadsheet → email draft):

- **Outcome:** The current spreadsheet from Downloads is attached to the correct email
  draft; the email remains unsent.
- Then run the five checks against *that* description — not against the casual ask.

If Access cannot be satisfied, status is **`blocked`** before the agent starts
(or as soon as the miss is known) — not a low-confidence `done`.

## Five checks

Every mission must clear all five. Fail any one → do not treat the run as finished.

### 1. Outcome

What must be true in the world when the job finishes? Point to artifacts, systems,
and states (branch, PR, node id, issue id, file path). Prefer the Proofboard contract
register pattern ([[05-validation-harness]]) when the work is code-heavy.

### 2. Access

Does this surface have the **tools, data, permissions, and time** the outcome requires?

- Preflight skill `requires:` / [[capability-registry]] when a skill drives a tool
- For ad-hoc missions: list each required reachability (repo, path, MCP, network,
  Figma file, tracker lane) and mark `VERIFIED` / `MISSING` / `UNKNOWN`
- **`MISSING` ⇒ `blocked`.** Upload, connect, grant, or shrink the job — do not
  substitute a lookalike source

### 3. Quality

Can Sean (or a named expert role) give this a sniff test? If not, who can?

Separate: *exists in required state* vs *fit to use*. Tests/evals encode a human
standard; they do not invent one. Keep expert review where judgment cannot honestly
reduce to a machine check (frameworks 05/06 for design-altitude work).

### 4. Evidence

What **direct read-back** from the owning system proves the outcome?

| Work | Evidence examples |
|---|---|
| Code | Diff + targeted tests + CI; not "I fixed it" |
| Figma | Node id + screenshot at native resolution; publish receipt if publish was the job |
| Tracker | Issue status + receipt comment; lane-qualified ids |
| Files | Open the path; checksum/version compare to source of truth |
| Browser | Live DOM/URL state after the action — not the plan |

Preserve the **first promotion**: the earliest jump where a narrow state became a
stronger claim without enough evidence (e.g. "attachment present" → "correct file
attached"). Trace suspicious runs backward to that jump.

### 5. Supervision

Who reads the result **before it counts as done**?

- If the answer is only the same agent: nothing is supervising — you hired a narrator
- Human approval for consequential classes (employer push, spend, publish, delete)
- Optional reviewer agent **with read-only access to the evidence**, allowed to answer
  `unknown`

## Protocol

### 1 — Choose one job + recent runs

Narrow audit. Inputs:

- One recurring job in outcome language (the pre-question)
- **3–10** recent runs (session fragments, PRs, chat summaries, Open Engine issues,
  failing anecdotes). More than ten → sample; do not tour the agent's whole life

Record context profile (`personal-solo` / `centric-engineering` / `centric-design`) —
it changes who must supervise ([[00-context-profiles]]).

### 2 — Score the five checks

For each check: `PASS` / `FAIL` / `UNKNOWN`, with evidence grade
(`VERIFIED` / `USER_REPORTED` / `INFERRED` / `NOT_EXPOSED`).

Overall mission verdict:

| Verdict | Meaning |
|---|---|
| **Fit** | All five PASS with adequate evidence |
| **Fit with gaps** | Usable if listed gaps are accepted; supervision must cover them |
| **Unfit** | One or more FAIL; do not widen autonomy |
| **Blocked** | Access (or equivalent) cannot be satisfied — honest stop |

### 3 — Name the pattern

A harness that fails a job once usually fails it the same way. Label the pattern, e.g.:

- Plausible substitute when source unreachable  
- Completion language without world read-back  
- Self-supervision (agent as sole witness)  
- Quality bar never stated  
- First promotion / state-ladder skip  
- Prose limit with no validator  

### 4 — Replay cases

Write **2–5** cheap replay cases that would have caught the failure (inputs + expected
`blocked`/`fail`/`pass`). These are the regression suite for any harness change.

### 5 — Write the report

```
05-artifacts/active/mission-fit_vN.N_YYYY-MM-DD.md
```

Optional durable copy:

```
07-projects/19-workspace-brain/reports/mission-fit_vN.N_YYYY-MM-DD.md
```

Required sections:

1. Job (outcome language) + profile + surface  
2. Five-check scorecard  
3. Pattern + first promotion (if any)  
4. Replay cases  
5. Numbered harness recommendations (dispositions from [[harness-map]] vocabulary when
   touching setup)  
6. What would make the next `done` one direct check away  

### 6 — Apply only with approval

Re-run the same replay cases after an approved change. An upgrade earns its place only
when the same work gets better **without** weakening stop conditions (`blocked`,
human gates, validators).

If claimable follow-up work should survive the chat, mint an Open Engine Agent Todo
**pointer-shaped** ([[open-agent-engine]]) — never paste the full report into the issue.

## Relationship to other skills

| Skill | Boundary |
|---|---|
| [[harness-map]] | Setup inventory + dispositions; run before or beside this |
| [[open-agent-engine]] | Queue/ledger/receipts for movement; use receipt tokens as Evidence when the job is engine work |
| Proofboard ([[05-validation-harness]]) | Delivery-time verification UI for code-heavy work — Mission Fit decides if the *mission* can be proven at all |
| Capability preflight ([[AGENTS]]) | Skill-scoped tool presence; this skill applies the same honesty to the whole mission |

## Ritual hooks (thin — this skill stays on-demand)

Always-on rituals do **not** run Mission Fit. They only:

- **Session-start Notice** — stale [[harness-map]] stamp (>30d) → suggest `/harness-map`
  when convenient (silent if no stamp yet).
- **Session-end `Evidence:` line** — if the session claimed consequential `done`
  (employer push, Figma publish, external send, destructive change, money), `/session-end`
  adds one `Evidence:` line (verified / unverified / blocked). That is continuity hygiene,
  not a five-check audit — invoke this skill when the job needs a real fit pass.

## Provenance

- Nate B. Jones — *AI Agent False Success* (2026-08-07) + Mission Fit guide  
- Evidence backdrop: arXiv [2606.09863](https://arxiv.org/abs/2606.09863) (*From Confident Closing to Silent Failure*) — false success common; LLM judges weak without state  
- Localized 2026-08-07 for `snds/workspace`: Proofboard, capability registry, Open Engine, context profiles, archive-not-delete

## Related
- peer ↔ [[harness-map]]
- peer ↔ [[open-agent-engine]]
- peer ↔ [[workspace-bootstrap]]
