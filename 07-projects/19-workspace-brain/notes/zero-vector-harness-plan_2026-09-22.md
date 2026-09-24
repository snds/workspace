---
title: Zero-Vector-informed harness plan (v1.1, LLM- and device-inclusive)
date: 2026-09-22
status: wave 0 closed on the Work MBP except the G5c apply; wave 1 started 2026-09-24 (items not needing a decision)
related: [[zero-vector-design-methodology]]
---

# Zero-Vector-informed harness plan — v1.1 (2026-09-22)

Standing home: this project.
- Methodology synthesis: `08-knowledge/cross-domain/zero-vector-design-methodology.md`.
- v1.0 detail (public): `reports/zero-vector-harness-detail_v1.0_2026-09-22.md`.
- **v1.1 detail and surface research are held locally, not committed.** They are at
  `.claude/state/held/`, on the Work MBP only. The vault repo is **public**, and those documents
  map agent-surface gaps and employer-wall mechanics. Only a copy rewritten to class level (F-14),
  with the recipes and machine posture removed and read by Sean, may be published. Passing the
  employer-substance scan alone is not enough (^pc-47, [[decision-public-residual-detail]]).

## Sean's decisions (2026-09-22) — binding

1. **Wave 0 is approved**, on the condition that everything is **LLM-inclusive as a first-class
   concept**. The minimum surfaces are Claude Code, Claude Chat, Cursor and Codex, and as many
   others as feasible. See [[decision-llm-inclusive-harness]].
2. **Device-inclusive.** It must work on both the Work MBP and the Personal MBP. Repos are keyed by
   remote slug and resolved per device, and nothing hardcodes a path.
3. **Project intent lives in each repo** as `PROJECT.md`, with a pointer from the repo's
   `AGENTS.md`. Projects without a repo keep their intent in the vault. `centric-ui` inherits
   `saas-plm-prototype`'s intent. See [[decision-project-intent-in-repo]].
4. **Identity is (surface family, device).** Every Claude surface is **personal-only** (`snds`) on
   every device, with no substantive employer work, but housekeeping is allowed with receipts.
   Cursor and Codex are the **employer-approved** surfaces, with full harness access including
   mapping and recon. Every other surface follows the device. See [[feedback-credential-scoping]].
5. **The guard is workspace-owned and LLM-agnostic.** One decision function works over declared
   tables, and every host reaches it through a generated shim.

## Sean's decisions (2026-09-23) — binding

Wave 0 is published. These answers close its open items.

1. **The heal path gets pinned in wave 1.** Today the doctor refreshes the Claude-only injectors (the hook
   scripts and the user `CLAUDE.md`) from the checkout, not from the pinned copy, and its session-start
   and scheduled runs use the checkout's doctor. Until wave 1 that is a declared residual.
2. **The Claude git floor keeps blocking** the vetted branch-prune push when it cannot read the
   process table, for example inside Claude Code's Bash sandbox. That one command runs with the
   sandbox off.
3. **Employer email domain:** `centricsoftware.com`. Sean will say if the employer changes.
4. **Three H25 parts move to wave 1**, because each needs a wave-1 component: the limits on
   fragments from employer-touched sessions (H23), the Cursor/Codex inventory of workspace-derived
   files in employer repos (H4), and the static Claude deny rules for employer vault folders (H15).

5. **Gap detail follows the repo's visibility** (walls F-14). This vault is public, so a known gap
   is written at class level with a stable ID, and the recipe and machine posture stay held. The
   H17 coverage row now cites H17-R1 to H17-R10. See [[decision-public-residual-detail]].
6. **Context profiles name no single agent** (D6). `00-context-profiles.md` now says the declared
   facts are "cited by the agent", not "cited by Claude".
7. **The work email address in three tracked files is handled with wave 1** (the H25 scrub). The
   two setup files will read it from a local, untracked file, and the employer-substance scan
   starts counting that domain (^pc-47).

## Bottom line

The v1.0 substance survives: the heal sequencer, one profile resolver, one spec parser, the
findings register, owned write-sets, and gates computed from the diff. What changes is **where
things are enforced**. Research on the current vendor docs and on this Mac's logs showed that
vendor-hook enforcement does not transfer between surfaces:
- Cursor's `sessionEnd` failed in 98 of 147 logged runs.
- Cursor's prompt-time hooks cannot inject context. The route hook returned context 232 times, and
  none of it reached a transcript.
- Codex's hooks here are configured but untrusted, and its SessionEnd is capped at about 3 s.
- Claude Chat and cloud agents run none of the local config.

So v1.1 implements every behaviour once, in workspace-owned stdlib code and declared tables:
`surfaces.json`, `devices.json`, `context-remotes.json`, `action-policy.json` and
`vetted-scripts.json`. It generates the per-host shims from those tables, and it claims
enforcement only at the lowest tier that actually blocks.

## Enforcement tiers (strongest reach last)

| Tier | What | Blocks? |
|---|---|---|
| T0 contract text | `AGENTS.md` + adapters, `llms.txt`, paste pack | no |
| T1 always-on rules | beacons, `.cursor/rules`, Codex global `AGENTS.md` | no |
| T2 prompt/session hooks | context injection where a host supports it | not used to block |
| T3 tool-time shims | Claude `PreToolUse`, Cursor `beforeShellExecution`, Codex `PreToolUse` (once trusted), generated static belts | yes, on hooked hosts |
| T4 git boundary | a Claude git floor (in the overlay) and global config-based hooks (git ≥ 2.54), which every local committer passes | yes (a human can bypass them) |
| T5 server side | CI + a force-push/deletion ruleset on the workspace | CI detects; the ruleset blocks |
| T6 credential scope | the personal account holds no employer grants; the Claude GitHub App and connectors are personal-only | yes (the server refuses access) |

## Surface coverage at a glance

| Surface | Strongest enforcement it can run | Honest limit |
|---|---|---|
| Claude Code (local) | T3 PreToolUse + T4 Claude floor | A documented minimal launch mode skips hooks; whether it also drops the overlay env is unknown; the G3b probe window could not run it on this sign-in (H17-R7, held) |
| Claude Code (cloud) | Committed repo hooks + T5 | None of the local config applies |
| Claude Chat (web/mobile) | T5 + T6 only | No local enforcement at all |
| Claude Chat (desktop/Cowork) | MCP server write tools (H21) + T5 | Cowork's hook behaviour is unverified |
| Cursor (IDE) | T3 user hooks + T4 lanes | Prompt injection is dropped; sessionEnd is unreliable |
| Cursor (cloud) | Committed repo hooks + T5 | Platform identity |
| Codex (desktop/CLI) | T3 once hooks are trusted, execpolicy belts, T4 lanes | Trust is pinned per definition hash; 32 KiB AGENTS.md cap |
| Codex (cloud) | T5 | Low-confidence docs |
| Gemini, Copilot, Windsurf, Warp, Aider, others | T3 where hooks exist, T4, T5 | Unverified until installed and probed |

## Wave 1 status (2026-09-24)

Sean approved planning wave 1 and starting every item that neither waits on a decision nor on G5c.
The full spec is held locally (`INTENT-wave1-2026-09.md`), like wave 0's.

- **Started:** the work email address leaves tracked files (^pc-47; setup scripts read it from a
  machine-local file); the seven minor wave 0 follow-ups (fail-closed hardening and test pins); the
  H6 entry-point measurement and a proposed AGENTS.md cut list (report only).
- **Waiting on Sean's decisions:** which AGENTS.md cuts land (H6 lands first); which git lanes install
  where (H18); whether any host detection may lower the walls (H15, including the Copilot label);
  the Claude-only env-file channel design (D4, which the Personal MBP overlay needs); the
  employer-substance baseline for the employer mail domain; moving the heal scripts to report class
  (D11, with H20).
- **Decided by Sean (2026-09-24):** the recommended AGENTS.md cut set lands first; H18 git lanes go on
  both Macs in wave 1 and block at install; a detection discount needs verified evidence (a host hook
  payload or process ancestry), never an environment variable alone; the heal scripts keep healing,
  but only from the pinned lib. Still open: D4's design and the employer-domain baseline.
- **Non-Claude only:** the employer-repo intent PRs and the one-time inventory of workspace-derived
  files in employer repos (Cursor, Codex or Sean).

## Components (25) by wave

**Wave 0: declare, probe, pin, and encode the action policy before any new gate.**
- H16 surface registry (data)
- H19 neutral hook core (`ws_hook.py`: host detection, dedupe, budgeted start)
- H24 installer discipline and pinned execution (the unattended doctor only reports, except the
  heal of the Claude-only injectors, which reads the checkout until wave 1 pins it)
- H2 resolver keyed by remote slug and device
- H22 action-class policy, vetted scripts, receipts (prune-our-branches is the first member)
- H17 identity table + Claude overlay + git floor
- H25 employer-substance boundary for the public vault (report-only scan and baseline; three parts
  move to wave 1)
- H1 regeneration sequencer at every committer
- H3 intent-run hardening

**Wave 1: universal floors and honest entry points.**
- H6 entry-point parity and per-surface budgets. It cuts `AGENTS.md` first, because Codex headroom
  is only 336–1,851 B.
- H18 git lanes for every local committer
- H15 wall guard rendered into every hooked host, plus H25's static Claude deny rules for employer
  vault folders
- H7 routing through `ws route --stdin` on every surface
- H20 portable homes for the seven Claude-only workflows, plus pinning the Claude-only injector heal and
  the scheduled doctor run (a declared residual until then)
- H23 surface- and device-aware session closure per touched repo, plus H25's limits on fragments
  from employer-touched sessions
- H4 `PROJECT.md` intent in each repo, with inheritance, plus H25's one-time Cursor/Codex inventory
  of workspace-derived files in employer repos
- H5 intent lint, approve and verify

**Wave 2: close the loops, report-only.**
- H8 remediation spec (recon is Cursor/Codex-only for employer repos)
- H9 write-set scope
- H10 diff-computed gates and per-surface compliance
- H11 gate lanes

**Wave 3: opt-in blocking plus breadth on demand.**
- H12 research records
- H13 structure conformance
- H14 rule-of-three
- H21 workspace MCP server (it replaces the unguarded `workspace-fs`)

**First breaker:** the Claude identity overlay. It had to be fixed before anything else could stack
on it. The fix to the flaw below **landed in `0d19852`**; the rest of H17 follows the wave-0 order
(probes → pinned installers → H22 → full overlay → shared-layer guards).

## Done in this session

- **X1 heal** (`6cac460`).
- **Stamp-age clock bug** (`fc51b2d`).
- **Claude identity overlay.** v1 (`bb4cf05`) set `GIT_AUTHOR_*` unconditionally. Env outranks
  every config file, and Cursor and VS Code import Claude config, so this was an I1 risk.
  **v2 (`0d19852`)** scopes `snds` to `snds/*` remotes through `includeIf hasconfig`. That was
  verified on synthetic repos: an employer checkout keeps its own identity, and employer remotes
  stay blocked.
- **Decisions recorded:** `bb4cf05`, `f25e916`, and the credential memory, restructured.
- **Vault stays public, with scrubbing going forward** (Sean). The "private" claims are corrected
  (`d083403`).
- **Claude-only `gh` config** (overlay v3). Logging a second account into the shared `gh` config
  had made it the active account for every surface. The device default is restored (`d083403`).
- **Overlay v4: Claude's `snds/*` git traffic goes over HTTPS through the Claude `gh` helper.** The
  helper list is reset first, so a device-level credential store cannot answer before it. Verified:
  only the `gh` helper runs, and it answers as `snds`. Per-device credential detail is held.
- **Codex import hooks #1 and #2 are retired** to
  `~/.config/snds-workspace/archive/codex-import-2026-07-31/`. The snds plugin's SessionStart is kept
  until H19. Nothing is trusted in Codex yet.

## Findings about the current setup (all surface-relevant)

- **The workspace repo is public.** The vault itself calls it private (^pc-47).
- **Cursor's Layer-0 route injection never reached a transcript** (232 returns). Cursor's routing
  therefore rests on rules text, not hooks. The fix is H7/N2.
- **Workspace `AGENTS.md` (30.9 KB) plus the Codex global beacon (1.5 KB) is at Codex's 32 KiB cap,
  and truncation is silent.** The fix is H6, which cuts before any addition.
- **Codex's Claude import (2026-07-31) left untracked, drifting forks:** a stale
  `.codex/hooks/dispatcher.py`, and `.agents/skills`, 6 of 8 of which have drifted. The fix is
  retire-with-backup (Decisions needed, item 4).
- **Claude Code can reach employer-capable channels outside git (known gap WALL-C1):** a tracker
  connector with write tools, browser control, desktop control, and a terminal beside the session
  (probed 2026-09-24: it does not carry the overlay; each command sent there needs the user's approval). The git guard does not cover
  them. The employer tracker connector is limited by policy only (movement-only use,
  [[feedback-credential-scoping]]). Browser and desktop control act as whatever accounts the driven
  apps are signed into; T6 limits them only when those are personal (decision 3 is open). What
  closes it: H15 (wave 1) denies the employer connector's tools to Claude and adds an employer-host
  check for browser control driven from Claude Code; the browser profile (decision 3) covers the
  rest; desktop control has no planned close. The per-device roster is held. See Decisions needed,
  item 3.
- **The prompt router fires on background task-notification turns (X2)**, confirmed in local
  transcripts.
- **Three Claude Code installs cause false version notices** (^pc-46).

## Decisions needed before wave 0 (2026-09-22 snapshot; the full list of 24 is in the held detail)

1. **Public vault.** Keep it public and scrub going forward, or make it private (rulesets then need
   a paid plan). History rewriting is a separate, destructive choice.
2. **Overlay completion (H17).** A Claude git floor, `WS_SURFACE_FAMILY`, and a Claude-only gh
   config set by the overlay. Will you log `snds` into that gh config, or leave it empty?
3. **Employer-capable tools in Claude.** Keep, scope or remove the employer tracker connector?
   Which browser profile does Claude drive?
4. **Codex.** Trust the generated hooks and the plugin hooks, and retire the import forks?
5. **Wave-0 defaults** I'll use unless you object:
   - Claude on unknown-owner repos under `~/Projects` → deny.
   - The express override is CLI-only, 8 h by default.
   - R2 and R4 stay report-only for 14 days.
   - Neutral machine dir: `~/.config/snds-workspace/`.

## Do not build (inherited, plus v1.1 additions)

- Inherited: no parallel agent framework or second substance store, no default reflect-and-retry,
  no LLM-as-judge KPIs, no new framework or skill without rule-of-three evidence, no unattended
  runners.
- New in v1.1: no hooks or workspace files in employer repos, no tracked blocking flag, no
  doctor-set `core.hooksPath`, no unattended installs of anything that runs in employer working
  directories, and no gate that charges ambient debt.

## Method

- **v1.0.** Serial, human-paced reads of the Zero-Vector sources, then two workflows (8 and 12
  agents).
- **v1.1.** A third workflow of 10 agents:
  - 5 research agents: Claude Code and Claude Chat, Cursor, Codex, the long tail, and workspace
    lock-in. They used official docs plus read-only local config and logs, and never opened
    employer repos.
  - 1 designer.
  - 3 adversarial refuters: lock-in, walls and identity, facts.
  - 1 reviser, who applied 35 objections, partially applied 4 and rejected 1.
- The load-bearing claims were re-run by hand: repo visibility, the overlay's identity scoping, and
  `includeIf` through the environment.
