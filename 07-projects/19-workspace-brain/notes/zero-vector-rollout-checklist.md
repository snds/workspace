---
title: Zero-Vector rollout checklist (vault copy)
date: 2026-10-14
status: wave 3 open; waves 0–2 closed (wave 1 closed 2026-09-25, f95d992; wave 2 closed 2026-09-26)
related:
  - "[[zero-vector-harness-plan_2026-09-22]]"
---

# Zero-Vector rollout checklist — vault copy (2026-10-14)

This is now the record of every Zero-Vector harness step, by wave. It was exported on 2026-10-14
(/optimize) from the claude.ai artifact database that held it before (collections `steps`, `waves`,
`meta/status`; last updated there 2026-09-26). The artifact is not durable
([[decision-vendor-surface-artifacts]]), so update **this file**, not the artifact.

**How to update:** when a step closes, move its row from "Open steps" into its wave's table with
the done date and the commit (or decision) that closed it. Add new steps as rows in "Open steps".

**Public-vault rule:** this repo is public ([[decision-public-residual-detail]]). Rows stay at class
level: no machine posture (per-device installs, accounts, connector rosters), no employer repo or PR
names, no bypass recipes. Fuller per-step detail stays in the held wave specs
(`.claude/state/held/INTENT-wave*-2026-09.md`, Work MBP).

Plan and decisions: [[zero-vector-harness-plan_2026-09-22]]. `02-shared-references/surfaces.json`
`current_wave` is the machine-readable wave pointer (2 as of 2026-10-14).

## Open steps

| Step | Wave | Status | Owner | Device | What closes it |
|---|---|---|---|---|---|
| W1-window | Ongoing | review due | Sean | Either | The 14-day report-only window ran 2026-09-25 → 2026-10-09. Run `wall_guard.py report --days 14` on both Macs, then decide which rules enforce. R2 flips per host only with zero false denies. No review recorded as of 2026-10-14. |
| OPT-IN | Wave 3 | waiting on W1-window | Sean | — | Per Mac: which report-only rules enforce, whether the push gate blocks, whether write scope can block. Closes or re-dates the nine wave-3 parity waivers. |
| W3-V | Wave 3 | todo | Claude | — | Wave 3 exit gate: blocking only by opt-in; 30 days with no charged-red push reaching `main`; H14 baseline; H12/H13 shipped or recorded not triggered (done); no silent budget raises; parity with no expired waiver. Then bump `current_wave` in `surfaces.json`. |
| W2-on1 | Ongoing | ongoing | Claude | Both | Compliance counts per agent: closes once Claude Code, Cursor and Codex have each made workspace commits and `close-out-dispatch --compliance` shows a receipt/trailer join per agent (Codex transcripts are an honest skip). Terminal commits already count as human. |
| W2-on2 | Ongoing | ongoing | Claude | Both | Gate suffixes identical across agents, live: closes when a Cursor and a Codex commit in the workspace show the same `[gate:…]` line for the same tree. Tests already prove it. |
| W2-probes | Ongoing | watch | Sean | Either | Codex hook-event probe done 2026-09-26 (`791a8ef`, fix `9bc5ecb`). Cursor CLI payload capture still open, only if `cursor-agent` is used. |
| X1 | Ongoing | watch | Sean | Work MBP | Re-probe Codex after Codex updates, to confirm it still does not import Claude's settings env. |
| X2 | Ongoing | todo | Sean | Work MBP | Set a stable LocalHostName (L-06); then Claude declares it in `devices.json`. |
| X3 | Ongoing | todo | Sean | Work MBP | Enroll or deliberately skip the repos the doctor flags for cloud beacons (see ^pc-02). |

## Closed steps

### Plan — Research, plan v1.1 and approval (closed)

| Step | Title | Owner | Done | Ref |
|---|---|---|---|---|
| P1 | Zero-Vector research and harness plan v1.1 | Claude | 2026-09-22 | plan note |
| P2 | Wave 0 approved | Sean | 2026-09-22 | decision |
| P3 | Exposure decision | Sean | 2026-09-22 | ^pc-47 |

### Wave 0 — Declare, probe, pin and encode the action policy before any new gate (closed)

| Step | Title | Owner | Done | Ref |
|---|---|---|---|---|
| T1 | H16 + H19: surface registry and neutral hook core | Claude | 2026-09-23 |  |
| T2 | H2: declared resolver | Claude | 2026-09-23 |  |
| T3 | H24: installer discipline and pinned lib | Claude | 2026-09-23 |  |
| T4 | H25: employer-substance scan | Claude | 2026-09-23 |  |
| T5 | H1: regeneration sequencer and heal | Claude | 2026-09-23 |  |
| T6 | H3: intent-run hardening | Claude | 2026-09-23 |  |
| T7 | H22: action policy and vetted scripts | Claude | 2026-09-23 |  |
| T8 | H17: identity overlay and Claude git floor | Claude | 2026-09-23 |  |
| T9 | Integration | Claude | 2026-09-23 |  |
| T10 | Verification (walls, LLM/device, tests) | Claude | 2026-09-23 |  |
| T11 | Fix round | Claude | 2026-09-23 |  |
| G1 | Surface coverage green for every component on the four required surfaces | Claude | 2026-09-24 |  |
| G2 | One effective hook registration per surface and event | Claude | 2026-09-24 |  |
| G2b | Claude Code and Codex boot output unchanged with and without a pin | Claude | 2026-09-24 |  |
| G3a | Probe tooling ready (probe-env, hook probe, promote with redaction) | Claude | 2026-09-24 |  |
| G3b | Work MBP probe records for Claude Code, Cursor, Codex, VS Code | Sean | 2026-09-24 |  |
| G3c | Env-import question answered for the Work MBP hosts | Sean | 2026-09-24 |  |
| G3d | Personal MBP probe records | Sean | 2026-09-24 |  |
| G4a | Rendered overlay registers the floor and survives repo-local overrides | Claude | 2026-09-24 |  |
| G4b | Identity fixture passes on the Work MBP | Claude | 2026-09-24 |  |
| G4c | Work MBP git capabilities recorded | Claude | 2026-09-24 |  |
| G4d | Personal MBP identity fixture and git capabilities | Sean | 2026-09-24 |  |
| G4e | v5 overlay installed on the Work MBP; floor on pre-push in a Claude session | Sean | 2026-09-24 |  |
| G5a | Policy corpus denies model-composed employer deletes and hook bypasses | Claude | 2026-09-24 |  |
| G5b | Floor blocks model-composed employer deletes and personal identities | Claude | 2026-09-24 |  |
| G5c | Vetted prune: one dry-run and one apply from a Claude session, with receipts | Sean | 2026-09-24 |  |
| G6 | Installer and pin fixtures green | Claude | 2026-09-24 |  |
| G7a | Employer-substance baseline committed and not exceeded | Claude | 2026-09-24 |  |
| G7b | Exposure decision recorded | Sean | 2026-09-24 |  |
| G7c | D1 publication decision recorded before the first push | Sean | 2026-09-24 |  |
| G8 | Registry, related and trigger-route generators all check clean | Claude | 2026-09-24 |  |
| G9 | Always-loaded files within their byte ceilings | Claude | 2026-09-24 |  |
| G10 | Every merge stays inside its task's write set | Claude | 2026-09-24 |  |
| F1 | Pin library: nested arming no longer drops the outer guard | Claude | 2026-09-24 | `918a329` |
| F2 | Probe records keep one env probe per kind of run | Claude | 2026-09-24 | `02e29e1` |
| F3 | Installer refuses the overlay on git without config-hook support | Claude | 2026-09-24 | `40299c8` |
| F4 | Installer refuses the overlay when another host imports Claude's settings env | Claude | 2026-09-24 | `ae64ba1` |
| F5 | Coverage promotions (claude-code H2/H19/H17/H22, cursor H19) | Claude | 2026-09-24 | `14125b9` |

### Wave 1 — Universal floors and honest entry points (closed)

| Step | Title | Owner | Done | Ref |
|---|---|---|---|---|
| W1-plan | Wave 1 spec written and approved to start | Claude | 2026-09-24 | held spec |
| W1-a | Work email address leaves tracked files (^pc-47) | Claude | 2026-09-24 | `a32d08a` |
| W1-b | Seven wave 0 follow-ups (fail-closed hardening and test pins) | Claude | 2026-09-24 | `68b9835` |
| W1-c | H6 measurement: entry-point budgets and AGENTS.md cut list | Claude | 2026-09-24 | held report |
| D-W1-1 | Decide the AGENTS.md cut set | Sean | 2026-09-24 | decision |
| D-W1-2 | Decide the H18 git-lane rollout | Sean | 2026-09-24 | decision |
| D-W1-3 | Decide whether detection may lower the walls | Sean | 2026-09-24 | decision |
| D-W1-6 | Decide heal-script handling (D11) | Sean | 2026-09-24 | decision |
| D-W1-4 | Decide the Claude-only env-file channel design (D4) | Sean | 2026-09-24 | decision |
| D-W1-5 | Decide the employer mail-domain baseline | Sean | 2026-09-24 | decision |
| W1-1a | H6: land the AGENTS.md cuts | Claude | 2026-09-24 | `8dcbe69` |
| W1-1b | Harness: per-gate time limit for the fixture suite | Claude | 2026-09-24 | `f15bcb5` |
| W1-1c | H6: entry-point fixes, per-family beacons, ~/Projects pointer, route digest | Claude | 2026-09-24 | `94b4b34` |
| W1-1d | H6: a generated short rule file for Windsurf | Claude | 2026-09-24 | `94b4b34` |
| W1-2 | H18: git lanes for every local committer | Claude | 2026-09-24 | `5e43959` |
| W1-2h | Install round: git lanes, wall guard and routing on both Macs | Sean | 2026-09-24 | `cf18b4c` |
| W1-3 | H15: workspace wall guard rendered into every hooked host | Claude | 2026-09-24 | `461c933` |
| W1-3h | Install the H15 shims and trust the Codex hooks | Sean | 2026-09-24 | `cf18b4c` |
| W1-4 | D4: Claude-only env-file channel | Claude | 2026-09-25 | `2b29df5` |
| W1-4w | Work MBP: move the overlay to the env-file channel (no gap) | Sean | 2026-09-25 | `493a0ab` |
| W1-4h | Install the overlay on the Personal MBP | Sean | 2026-09-25 | `af83bb4` |
| W1-5 | H7: Layer-0 routing on every surface through one matcher | Claude | 2026-09-24 | `461c933` |
| W1-1h | Install the H6 pointer files on each Mac | Sean | 2026-09-24 | `727937d` |
| W1-6 | H20: portable homes for the seven Claude-only workflows; pin the heal path | Claude | 2026-09-25 | `c338a23` |
| W1-6h | Reinstall the launchd doctor to run the pinned copy | Sean | 2026-09-25 |  |
| W1-7 | H23: surface- and device-aware session closure | Claude | 2026-09-25 | `0601673` |
| W1-7h | Re-pin and reinstall hooks for H23 + W1-10 on both Macs | Sean | 2026-09-25 |  |
| W1-8 | H4 + H5: project intent in each repo, lint and verify | Claude | 2026-09-25 | `d07fb5f` |
| W1-9 | Employer intent PRs and one-time inventory | Cursor/Codex/Sean | 2026-09-25 |  |
| W1-10 | H25 blocks with the employer mail-domain baseline | Claude | 2026-09-25 | `b1fd9ba` |
| W1-11 | Parity gate: shared parts reach every agent | Claude | 2026-09-25 | `e8cba52` |
| W1-V | Wave 1 verification and exit gate | Claude | 2026-09-25 | `53eddf2` |

### Wave 2 — Close the loops, report-only (closed)

| Step | Title | Owner | Done | Ref |
|---|---|---|---|---|
| H8 | Remediation spec | Claude | 2026-09-26 | W2-1 |
| H9 | Write-set scope as task data | Claude | 2026-09-26 | W2-3 |
| W2-plan | Wave 2 plan written | Claude | 2026-09-25 |  |
| H10 | Diff-computed gate selection and per-surface compliance | Claude | 2026-09-26 | W2-2 |
| W2-0 | Wave 1 carry-overs | Claude | 2026-09-26 | `26b937a` |
| H11 | lanes at the universal boundaries | Claude | 2026-09-26 | W2-4 |
| W2-1 | H8: remediation loop (recon, findings, packets, verdict) | Claude | 2026-09-26 | `b7b31fd` |
| W2-2 | H10: receipts, trailers, compliance per surface, CI on the card | Claude | 2026-09-26 | `b7b31fd` |
| W2-3 | H9: write scope as task data | Claude | 2026-09-26 | `b7b31fd` |
| W2-4 | H11: commit and push gates, report-only | Claude | 2026-09-26 | `b7b31fd` |
| W2-h | Install wave 2 on both Macs | Sean | 2026-09-26 |  |
| W2-5 | H8 live run on a personal project | Sean | 2026-09-26 | `0da01cf` |
| W2-fix | CI green again; harness mirrors CI; wave 2 follow-ups | Claude + Sean | 2026-09-26 | `2eaa113` |
| W2-V | Wave 2 verification and exit gate | Claude | 2026-09-26 | `2eaa113` |

### Wave 3 — Opt-in blocking plus breadth on demand (open)

| Step | Title | Owner | Done | Ref |
|---|---|---|---|---|
| W3-plan | Wave 3 plan written | Claude | 2026-09-26 |  |
| H12 | Research-record lint — decided not triggered (no consumer yet) | Sean | 2026-09-26 |  |
| H13 | Structure conformance detector — decided not triggered (no consumer yet) | Sean | 2026-09-26 |  |
| H14 | Rule-of-three instance log | Claude | 2026-09-26 | `391612d` |
| H21 | Workspace MCP server | Claude | 2026-09-26 | `b39a282` |
| W3-R4 | Stop R4 asking in folders that aren't git repos | Claude | 2026-09-26 | `854397d` |

