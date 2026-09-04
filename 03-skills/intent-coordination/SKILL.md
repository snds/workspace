---
name: intent-coordination
description: >
  Large-scale agent coordination against designed intent. Use when Sean says
  living spec, coordinate agents, agent orchestration, intent coordination,
  intentapp, fan out implementors, isolated worktree, or when two or more
  agents/worktrees would otherwise share only a chat thread. Coordinator drafts
  a living spec, human approves, implementors run in isolated git worktrees in
  dependency waves, an independent verifier checks the spec. Does not require
  the Intent Mac app. Open Engine stays movement-only; mission-fit owns done.
aliases: [intent-coordination, living-spec, agent-orchestration]
triggers:
  - living spec
  - intent coordination
  - intentapp
  - intentapp.dev
  - coordinate agents
  - agent orchestration
  - coordinator agent
  - implementor wave
  - isolated worktree
tier: cross-cutting
domain: workspace
related: [open-agent-engine, mission-fit, harness-map, workspace-bootstrap, side-chat-handback, vgpu-webgpu, web-3d-extensions]
governed_by: []
defers_to: [framework-17, framework-06, framework-08]
rigor_role: command-hub
surfaces: ["*"]
spec_version: "2.2"
---

# Intent coordination

L2 command surface for [[17-intent-coordination-operating-model]]. Foundations of
continuity remain [[AGENTS]] + Live handoff. This skill is how a parent agent
**fans work out and brings it back to the northstar**.

Standing project home for vault work: `07-projects/19-workspace-brain/` Live handoff.

## When to use

- Two or more agents, worktrees, or parallel writers
- Multi-file outcome that would rot in chat
- Sean names living spec / orchestration / intentapp / coordinate agents

## When NOT to use

- Single-agent, single-file, short work: still name the outcome; skip a new spec file
- Queue/claim/ledger mechanics → [[open-agent-engine]]
- Harness inventory → [[harness-map]]
- "Is this `done`?" as a five-check audit → [[mission-fit]] (call it as the verifier)
- Prompt-craft for production LLM products → [[ds-prompt-engineering]]

## Execution protocol

1. **Intent.** Outcome language. Context profile. Lane if tracking. Northstar pointer.
2. **Spec.** Copy [[intent-spec]] from `00-bootstrap/templates/intent-spec.md` into the
   owning tree. Fill checklist with **measurements**, not adjectives. Stop for approval
   unless the spec already records approval or Sean ordered execute-from-this-brief.
3. **Isolate.** `python3 09-tools/intent-run.py gate` then `worktree add <id>` (one
   writable git worktree per implementor). If Intent.app is running, `intent-run.py doctor`
   / `daemon` talk to bundled `intentd` (UDS). GUI worktrees and this runner must not
   share one dirty tree. `install-app` / `open-app` remain optional.
4. **Waves.** `intent-run.py ready` lists implementors whose deps are verified.
   Hold the rest. Load specialist skills via registry `load_chains`. A 3D wave is ordinary
   conversation with a spec: name `vgpu-webgpu` / `web-3d-extensions` / an adapter on the
   implementor line. MCP preflight happens in that worktree when the verb needs the live
   tool; research and checklist authoring do not wait on MCP.
5. **Verify.** `intent-run.py verify` prints checklist measures; `--run` executes
   them. Different evidence access than the author. Apply [[mission-fit]] for
   consequential `done`. Domain L3 as named (`vqa`, validators, CI).
6. **Land.** [#07](../../01-frameworks/07-integration-and-review-framework.md) + profile
   (no auto-commit / self-merge on `centric-engineering`). Point Live handoff at the spec.

## Done-gates

- [ ] Outcome and northstar are on the spec (or Live handoff, if spec was not required)
- [ ] Profile declared
- [ ] If a living spec was required: file exists, approved, implementors did not start early
- [ ] Isolation held (no shared dirty tree among writers)
- [ ] Verifier used the checklist; waivers are named
- [ ] Open Engine issues, if any, are pointers only

## Absolute bans

See framework #17. Short form: no chat-as-spec, no author-as-sole-verifier, no vendor
app required, no substance in Linear, no two writers on one worktree, no guessed profile.

## Outputs

- `docs/INTENT.md` (or `INTENT-<wave>.md`) in the owning tree
- Wave receipts: worktree paths, verifier commands, Open Engine ids qualified `lane:ID`
- Live handoff: current focus = spec path + next wave

## Defers-to

- Workspace doctrine: [[17-intent-coordination-operating-model]] · [[06-qa-operating-model]] · [[08-workspace-contribution-framework]]
- Intent / Augment product: optional desktop app (`intent-run.py install-app` from
  `intent-hq/cloudlands-releases`). Technique only. Protocol is the spec file + `intent-run.py`.

## Related
- peer ↔ [[open-agent-engine]]
- peer ↔ [[mission-fit]]
- peer ↔ [[harness-map]]
- peer ↔ [[workspace-bootstrap]]
- peer ↔ [[side-chat-handback]]
- peer ↔ [[vgpu-webgpu]]
- peer ↔ [[web-3d-extensions]]
