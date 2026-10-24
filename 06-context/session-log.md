# Session Log — Sean Sands
_Authoritative source: this file (06-context/session-log.md)_
_Written by any agent at session end — the git checkout is the source of truth._
_Entries: newest first._

---

## How This Works

**Any agent reads this at boot** to surface pending items and last session context.
**Any agent writes to this** at session end — no manual paste needed; git is the source of truth.
**Reconciliation** ("reconcile sessions") merges blocks from concurrent sessions
into a single update, then writes the result here automatically.

Keep entries concise. This is a handoff log, not a journal.

---

## Session Entries

> _Older entries archived to [session-log-archive.md](session-log-archive.md) to keep this file cheap to read. Ask to see it only if you need history._










































### 2026-10-22 — Synapse: the harness compiler (Stage H items 18–20)

SessionID: 2026-10-22-cloud-w6fan1
--- SESSION BLOCK ---
Date: 2026-10-22
Machine: cloud (remote session)
Surface: Claude Code (web)
Agent: Claude Opus 5.5
Project(s): 26-synapse
Summary: At Sean's ask, defined, planned and built the harness compiler: a role (job, role or domain mix) picks its harnesses, every supply gap becomes a requirement, and each is filled cheapest first (wire an existing file, else a draft in the workspace's own learned conventions at the role's level, with a research brief). It predicts supply after and writes nothing. Plan 10 + Stage H items 18–23 + D124–D129; items 18–20 built with tests HC0–HC6; PR snds/synapse#2. On the live vault the design-system lead role takes research.finding from 1/6 to 6/6 via a lead-research hub that links the existing research skills.
Pending: Sean's go on items 21–23 and D124–D129; accept or change the research fill; decide on a component-spec harness.
--- END BLOCK ---

### 2026-10-22 — Research network for any field (framework #19, lead-research)

SessionID: 2026-10-22-cloud-w6fan1-c
--- SESSION BLOCK ---
Date: 2026-10-22
Machine: cloud (remote session)
Surface: Claude Code (web)
Agent: Claude Opus 5.5
Project(s): 26-synapse, workspace
Summary: On Sean's go, filled the research gap the harness compiler found, widened to every field: framework #19 (Research Operating Model, depth tiers D0–D4 with propose-more-or-less, field profiles, done-gates, retro into the workspace), research-foundations → lead-research → 11 spokes, two research notes, a quotes reference, and research-check.py as L3. dc-research superseded by decision-research-network. research.finding on the live vault went from 1/6 to 6/6. Healed rule_of_three.py's command-hub exemption. Sean approved D124–D129.
Pending: Sean's review of the vault PR; first real research ask; compiler items 22–23 in snds/synapse.
--- END BLOCK ---

### 2026-10-22 — Synapse: compiler merged; accepting plans (item 21)

SessionID: 2026-10-22-cloud-w6fan1-b
--- SESSION BLOCK ---
Date: 2026-10-22
Machine: cloud (remote session)
Surface: Claude Code (web)
Agent: Claude Opus 5.5
Project(s): 26-synapse
Summary: On Sean's "merge then continue", merged snds/synapse#2 and snds/workspace#26, then built Stage H item 21: `sy harness accept` saves a supply plan as proposals, one per requirement, applied with `sy apply` and undone with `sy undo`. HC7 passes; on a copy of the live vault the 7 proposals bring all three harnesses to full supply and undo to a clean tree. PR snds/synapse#3. The vault itself was not written.
Pending: Sean's go to accept the research fill in the vault; the reference track's agent posture and spend (item 22); a component-spec harness (item 23); D124–D129.
--- END BLOCK ---

SessionID: 2026-10-23-cloud-w6fan1-q

## 2026-10-23 — Visual QA trial (D144) · Claude Opus 5.5 / Claude Code / cloud (remote session)

- **Asked:** trust in visual QA must come from real usage: test prompts for Legion and for CDS/Centric work, run by Sean, with a provisional approval that requires reviewing the outputs together; the Harnesses screen is a good start, reviewed in depth later; merge open work and continue.
- **Done:** merged snds/synapse#13 and snds/workspace#37. Wrote `07-projects/26-synapse/visual-qa-trial.md`: gated prompts on LCARS SYS47, Legion, Unicron and the Harnesses screen, engine-only prompts, a joint-review protocol and log. D144 records the provisional approval. Made the trial runnable: `vqa capture --theme --app --build` and `vqa evidence` (the gate's evidence folder), a bad cuespec exits 2, a failed prove names its failing cues, and `sy harness trust-tool --revoke` plus the app's Revoke.
- **Walls:** no CDS or Centric prompts. Vault content never goes into employer surfaces, and employer outputs can't come back here. Unicron stands in for the same kinds of QA effort (trial §7).
- **Baton:** 26-synapse Live handoff rewritten; the old Last and Next action moved word for word to `history/2026-10.md`.
- **Next:** Sean trusts the engine on the Personal MBP, runs the trial and logs his verdicts first; then a joint-review session on that Mac.

SessionID: 2026-10-23-cloud-w6fan1-p

## 2026-10-23 — Stage H decisions approved · Claude Opus 5.5 / Claude Code / cloud (remote session)

- **Asked:** "12 approved. 118-123 look good. Is there something I need to review re visual qa?"
- **Done:** merged snds/synapse#12 and snds/workspace#36; D118–D123 recorded as approved (snds/synapse#13). Explained the visual QA trust decision: nothing to review until Sean chooses to trust the vqa tool.
- **Baton:** 26-synapse Live handoff rewritten; the old Last and Next action moved word for word to `history/2026-10.md`.
- **Next:** Sean trusts the vqa tool when ready; says whether cuespecs need his review.

SessionID: 2026-10-23-cloud-w6fan1-o

## 2026-10-23 — Review context for harness changes · Claude Opus 5.5 / Claude Code / cloud (remote session)

- **Asked:** "D143 approved, merge and continue".
- **Done:** merged snds/synapse#11 and snds/workspace#35; D143 recorded as approved. Built plan 12 §3 items 3–4 in snds/synapse#12: harness proposals show what changes, where they relax the gate, and which recent runs they'd change (replayed without saving); `sy harness accept` shows its proposals' context.
- **Baton:** 26-synapse Live handoff rewritten; the old Last and Next action moved word for word to `history/2026-10.md`.
- **Next:** Sean reviews #12; trusts the vqa tool when ready.

SessionID: 2026-10-23-cloud-w6fan1-n

## 2026-10-23 — Workspace tools as harness checks · Claude Opus 5.5 / Claude Code / cloud (remote session)

- **Asked:** "D141/D142 approved, merge and continue".
- **Done:** merged snds/synapse#10 and snds/workspace#34; D141 and D142 recorded as approved. Built item 8's workspace half in snds/synapse#11: a check with no built-in binds to a workspace tool that implements it, once a person trusts it at its hash (`sy harness trust-tool`, or Trust in the Harnesses screen). Added `03-skills/visual-prove-engine/vqa.tool.json` binding the visual prove engine to `vqa.literal-diff` and `vqa.planted-defect`.
- **Decided / proposed:** D143 (workspace tools decide checks once trusted at their hash).
- **Baton:** 26-synapse Live handoff rewritten; the old Last and Next action moved word for word to `history/2026-10.md`.
- **Next:** Sean reviews #11, confirms or changes D143, and trusts the vqa tool when ready.

SessionID: 2026-10-23-cloud-w6fan1-m

## 2026-10-23 — Stage H, H3: surfaces and the Harnesses screen · Claude Opus 5.5 / Claude Code / cloud (remote session)

- **Asked:** "merge and continue. D139/D140 are approved."
- **Done:** merged snds/synapse#9 and snds/workspace#33; D139 and D140 recorded as approved. Built H3, items 13–14, in snds/synapse#10: Claude Code's stop hook, the harness MCP server, the rules-block line, `sy harness ci` and its recipe, `sy harness surfaces` (which apps can block, `--setup`), the service's `harnesses` and `harness_decide`, and the app's Harnesses place. HE10 passes; app typecheck, tests, DS ratchet and a11y pass.
- **Decided / proposed:** D141 (the stop hook blocks only a failed ship run), D142 (hook and MCP entries shown, not written, until Stage 5; signing waits on the device key).
- **Baton:** 26-synapse Live handoff rewritten; the old Last and Next action moved word for word to `history/2026-10.md`.
- **Next:** Sean reviews #10 and confirms or changes D141–D142. H4 needs Stage 5; H5 rides with Stage 3's track.

SessionID: 2026-10-23-cloud-w6fan1-l

## 2026-10-23 — Stage H, H2: the gate · Claude Opus 5.5 / Claude Code / cloud (remote session)

- **Asked:** "#8 and #32 are ok. Confirmed. Go for H2".
- **Done:** merged snds/synapse#8 and snds/workspace#32; D138 recorded as confirmed. Built H2, items 8–12, in snds/synapse#9: 12 built-in checks with planted defects, `sy harness gate` (retry cap, escape hatch, modes, run records), the tamper wall, `sy harness propose` (§4.1 fields, reach, self-interest, flags, the daily cap), `decide`, `runs`, `checks`, and the stage's security review. HE6–HE9 pass.
- **Decided / proposed:** D139 (workspace harnesses at `harnesses/<id>.json`, reviewed when an applied proposal wrote them), D140 (person decisions only at a terminal or in the app).
- **Baton:** 26-synapse Live handoff rewritten; the old Last and Next action moved word for word to `history/2026-10.md`.
- **Next:** Sean reviews #9, confirms or changes D139–D140, and says go for H3.

SessionID: 2026-10-23-cloud-w6fan1-k

## 2026-10-23 — Stage H, H1: resolve, the brief, coverage, the lint · Claude Opus 5.5 / Claude Code / cloud (remote session)

- **Asked:** "Go on Stage H, start H1".
- **Done:** merged snds/synapse#7 and snds/workspace#31 once green (Sean's "merge when green"). Built H1, items 5–7, in snds/synapse#8: `sy harness resolve` (plan keyed by harness hash, index content hash and task), `sy harness brief` (Levels 1–3), `sy harness coverage`, `sy harness lint`. HE2–HE5 pass; the live vault resolves 93% of the three starters' supply.
- **Decided / proposed:** D138 (proposed): the brief's load set is the task's plus the harness hub's chain.
- **Baton:** 26-synapse Live handoff rewritten; the old Last and Next action and the baton's older History lines moved word for word to `history/2026-10.md`.
- **Next:** Sean reviews #8, confirms or changes D138 and D118–D123, and says go for H2.

SessionID: 2026-10-23-cloud-w6fan1-j

## 2026-10-23 — Accepted routing exceptions · Claude Opus 5.5 / Claude Code / cloud (remote session)

- **Asked:** "D136 - confirmed. Yes, allow for exceptions that can be noted and accepted by the routing scripts."
- **Done:** Synapse D137 (snds/synapse#7): `routing-exceptions.jsonl` read by `sy routing test` and `sy routing hubs`. Vault: `02-shared-references/routing-exceptions.jsonl` with 10 exceptions (2 by Sean, 8 from Claude's hub review, reported to Sean).

SessionID: 2026-10-23-cloud-w6fan1-i

## 2026-10-23 — Review context on every proposal · Claude Opus 5.5 / Claude Code / cloud (remote session)

- **Asked:** "Merge when green and continue."
- **Done:** merged snds/synapse#6 and snds/workspace#30. Synapse snds/synapse#7: `sy_route::review::context` (D136) on every proposal; Health's fix view shows "What to weigh" or the one-line reason; `sy propose` and fact changes print it.

SessionID: 2026-10-23-cloud-w6fan1-h

## 2026-10-23 — Review context; D135 approved · Claude Opus 5.5 / Claude Code / cloud (remote session)

- **Asked:** "D135 is good." Changes for review should bring the lateral context they need, and the system should judge when they need none (not a hard requirement).
- **Done:** preference "Changes for review: bring the context they need" in `04-preferences/user-preferences.md`; Synapse plan 12 (D136 proposed); `sy routing hubs` gives each movable section a judged context (evidence, loads, referrers, governing notes, or "no context needed" and why).

SessionID: 2026-10-23-cloud-w6fan1-g

## 2026-10-23 — Hub depth review, mechanical (`sy routing hubs`) · Claude Opus 5.5 / Claude Code / cloud (remote session)

- **Asked:** review hubs for spoke depth, and make it mechanical and reusable for Synapse.
- **Done (Synapse):** `sy routing hubs` (plan 11 §7, D135 proposed): each hub section sorted into routing / contract / standard / duplicate / territory / homeless by shingles and TF-IDF against its spokes and foundations; notes in `sy routing test`; calibrated on the pre-2026-10-22 vault (finds `ds-advisor`'s visual principles); a planted-kinds test.
- **Done (vault):** `material-symbols-project`'s Figma icon-positioning technique moved word for word to `references/figma-icon-positioning.md` (hub 1,159 → 671 words); other flags reviewed and kept; report decision 2 updated.
- **Learned:** the 20 big hubs are big with hub material (spoke tables, principles, #13's protocol); word count alone is a weak signal. Method and philosophy sections are the tool's false positives.

SessionID: 2026-10-23-cloud-w6fan1-f

## 2026-10-23 — D133: foundations first across chains · Claude Opus 5.5 / Claude Code / cloud (remote session)

- **Asked:** "Merge any PRs. D133 ok"; plus two questions answered in chat (hubs over 1,500 words; descriptions as shortcuts).
- **Done:** merged snds/workspace#29 and snds/synapse#5. `09-tools/skill-loadset.py` now puts every foundation ahead of any hub or spoke after merging chains (stable partition; suggestions and lenses keep the merge order), with a self-test; Synapse's router does the same (snds/synapse D133).
- **Measured:** Python and Rust agree on 627/627 checked requests; late-foundation answers 515 → 0; routing cases 143/143.

SessionID: 2026-10-23-cloud-w6fan1-e

## 2026-10-23 — The routing suite; routing rules applied to every domain · Claude Opus 5.5 / Claude Code / cloud (remote session)

- **Asked:** "create a comprehensive testing suite for the router that would work for any potential routing … apply against all domains."
- **Done (Synapse, snds/synapse#5):** `sy routing test <workspace>` (plan 11): cases written from the workspace (own triggers bare and in carriers, quoted description asks, chains, reach), an everyday-sentence corpus, metamorphic variants, trigger lint, architecture lints, the owner's cases, token and time budgets; both dialects. 14 planted defects, 25 generated workspaces, T2 clean. D130–D134 proposed; metric 21.
- **Done (vault, stacked on snds/workspace#29):** `area` on 16 more hubs (31 of 31); own triggers for 129 hub-prose-only spokes from their descriptions' asks (about 780); everyday-word triggers fixed in `mobile-platform-craft`, `sec-threat-modeling`, `img-cinematography`; frontmatter spec: spokes carry triggers.
- **Measured:** hub-prose-only 129 → 0; description recall 33% → 49%; noise 0 of 82; cases 143/143; p95 tokens 13,181 → 13,387.
- **Decisions:** [[decision-routing-every-domain]]. Open for Sean: D133 (foundations across chains), thin hubs, quoted asks as triggers.

SessionID: 2026-10-22-cloud-w6fan1-d

## 2026-10-22 — Design skills rearchitected; data science is `dsci-` · Claude Opus 5.5 / Claude Code / cloud (remote session)

- **Asked:** "merge both and rearchitect, ds as hub, use dsci- for data science … Yes move ux-design-systems under the main design-systems hub."
- **Done:** merged snds/workspace#28 and snds/synapse#4. Renamed the ten data-science spokes `ds-*` → `dsci-*` and repointed every reference. `ds` is the one design-system hub (`area: design-system`); `ds-advisor`, `design-system-ops`, `token-architecture`, `ai-design-systems`, `canonical-docs-voice`, `ds-source-watch`, `ds-generation-pipeline` (with `gen-manifest` merged in) and the employer UI spokes moved under it; `ux-design-systems` → `ds-component-spec`; `design-engineer` a lens. Folded `ux-information-architecture`, `ux-data-visualization` and `ux-accessibility` into `ia-*`, `infod-*` and `a11y-*` (archived with provenance). Stated doctrine vs implementation for type and motion. Hubs declare `area:`; new generator `build-area-index.py` → `skill-areas.md`, wired into the rebuild and the harness. 19 routing cases added (`dsa-*`).
- **Measured:** routing battery 2/19 → 19/19; token ask 2,983 words loaded (was ~7,250); `sy harness compile` for `design-system-lead`: component-spec supply 75% before the plan, no new spokes.
- **Decisions:** [[decision-skill-prefixes]], [[decision-design-skill-architecture]].
- **Next:** Sean reviews the PR; Claude gives the trigger-less spokes in `skill-areas.md` their own triggers.

### 2026-10-19 — Externals: REA wired into the workspace; install/update/remove method; Synapse D108

SessionID: 2026-10-19-vm-rea7x
HostSession: session_01CGohZdEWWv7C43mgUDsJQv
--- SESSION BLOCK ---
Date: 2026-10-19
Machine: vm (cloud container)
Surface: Claude Code
Project(s): workspace infrastructure; 26-synapse (coordination only, no baton edits)
Artifacts:
  - 09-tools/externals.py — install, update in place, rollback, remove, exec, status, check, verify for externals
  - 02-shared-references/externals.json — the manifest; REA (rea-agents 6.7.0) pinned by version + sha512
  - 02-shared-references/externals-spec.md — rules, lifecycle, parity proof, app contract (Synapse)
  - 09-tools/externals.tool.json — runs for a tool runner (status, check, verify-rea, self-test)
  - .mcp.json, .cursor/mcp.json, .claude/skills + .agents/skills/reverse-engineer-anything — REA wiring
  - 06-context/memory/decision-externals.md — the decision
Decisions:
  - Sean chose option B: REA lives in the workspace (tracked wiring), not per-machine config
  - Externals code lives in <projects_root>/_externals/<id>, never in the vault; wiring is tracked
  - Synapse drives externals.py --json rather than reimplementing it (Synapse D108); every write is a reviewed plan (--expect-plan)
Evidence:
  - PR merged @ snds/workspace#24 (merge 7dbc757), CI 6/6 green on head 88b1ba8 — verified
  - externals.py verify rea 11/11 (1,775 files, 161 CLI probes, 207-tool MCP catalog identical inside vs outside) @ this container — verified
  - Synapse side (installer skips manifest names; Health ignores external wiring) @ snds/synapse 102218b — unverified (reported by the Synapse session)
Pending added:
  - On each Mac: `python3 09-tools/externals.py install --all --yes`, then approve the `rea` project MCP server once in Claude Code
Next:
  - Sean: run the install on each Mac (until then the server starts through npx at the same pin)
  - Harness reds in cloud containers (shallow clone: rule-of-three, TestRuleOfThree; TestOverlay; sandbox SKIPs) reproduce on the base commit — not from this change
--- END BLOCK ---

### 2026-10-15 — Lockdown research dossier and project scaffold

SessionID: 2026-10-15-vm-lockdn1
--- SESSION BLOCK ---
Date: 2026-10-15
Machine: cloud VM (Claude Code on the web)
Surface: Claude Code (cloud session)
Agent: Claude Opus 5.5, then Claude Fable 5.1 after a mid-session model switch
Project(s): 28-lockdown (new)
Summary: Sean asked for a feature-for-feature replication plan for 1Password, Bitwarden, Proton Pass, and Vaultwarden, plus Apple Passwords and other ecosystems, with the extra idea of signing in through vendors' own systems (Steam QR, Adobe, Battle.net). Ran four parallel research agents, then a verify-and-synthesise workflow: three gap sweeps (missed competitors, novel features, more login bridges), eight skeptical fact-checkers over 45 claims, a 201-feature matrix across 9 products, an 11,600-word brief, and a critic pass that reconciled both against the fact-check. Built a report page with a filterable matrix and published it (https://claude.ai/artifact/PT8FzNxTVLzrUr3AdVWHry). Pushed the research as the first commit on snds/lockdown main (e6d9248; the repo was empty, so no PR). Scaffolded 07-projects/28-lockdown (28 because 27 is the machine-local unraidTheme) and registered it in project-context, project-registry, _PROJECTS, and .gitignore.
Key findings: being an OS passkey provider gives cross-device QR sign-in for free on iOS (Apple staff confirmed) and on Android 14+; Steam QR approval is feasible via a tolerated reverse-engineered protocol and only authenticator removal costs the 15-day hold; Battle.net and Adobe should use passkeys; TV device-code activation (RFC 8628) is the legitimate generalisation; the security bar is the ETH Zurich hostile-server model.
Corrections from the fact-check: Proton Pass SSH agent has shipped; Apple's AI password change slipped past iOS 27.0; 1Password Mac AutoFill is GA since 2026-08-11; Windows passkey plug-ins were announced for 1Password and Bitwarden the same day.
Open: Sean's three decisions (positioning, Steam bridge, team size). close-out-dispatch found no command hub for this prompt (SKIP, not verified).
--- END BLOCK ---

### 2026-10-14 — Doctor fixes, /optimize audit applied, trigger review

SessionID: 2026-10-14-work-optrev
HostSession: 3931acbb-a691-4c1f-b44a-eab73c9a54ee
--- SESSION BLOCK ---
Date: 2026-10-14
Machine: Work MacBook Pro
Surface: Claude Code
Agent: Claude Opus 5.5
Project(s): 19-workspace-brain (workspace infrastructure); pending lines for 13-legion, 24-mailbird, 25-fontface
Summary: Verified Sean's pin / git-hooks / overlay v6 install, fixed two doctor gaps, ran /optimize (53 findings), applied every fix through five parallel passes, then narrowed 22 bare-word triggers. Enterprise is active again.
Artifacts:
  - d3c4788 — doctor: the session-start hook heals from workspace sessions; `--check` splits no-login / API-unreachable / refused-token
  - a799ef7 + 0e02416 — routing: filler-phrase lint in every source; 25 bare-word triggers narrowed; 119/119 routing cases
  - 2e655db — /optimize audit-log entry (P0 4 · P1 22 · P2 27)
  - d47c37f, 28d0e7b, 2f149d9, af219b4, 1108a00 — all audit fixes (routing + skill merges, contract shrink, maps, tools, context)
  - 06-context/memory/fact-claude-code-sandbox-limits.md — sandbox blocks api.github.com, ps, xcrun cache
  - 07-projects/19-workspace-brain/notes/zero-vector-rollout-checklist.md — exported from the claude.ai artifact
Decisions:
  - Enterprise (Sean's personal Windows desktop) is back in use; every Windows / Enterprise mention stays (Sean).
  - Merging the two mechanization branches stays Sean's call (^pc-51).
  - MEMORY.md stays on-demand; adding it to the start read breaks the 17,000 session-floor budget.
  - The employer-substance baseline pools session-log.md + session-log-archive.md, so compaction cannot trip H25.
Evidence:
  - Install round + re-pin `1108a00` + doctor heal @ ~/.config/snds-workspace and ~/.claude (`workspace-doctor.sh --check`) — verified
  - Full harness @ `workspace-harness.py` outside the sandbox — verified (PASS, 0 failing)
  - Workspace pushes @ github.com/snds/workspace (main...origin/main; pre-push gate green) — verified
Pending added:
  - ^pc-51 merge the mechanization branches; ^pc-52 save PlanetCompiler phase 6; ^pc-53 Enterprise machine layer; ^pc-54 DSDS 0.20 → 0.22
Pending resolved:
  - ^pc-16 superseded; ^pc-04 pruned (SEA-11 closed); ^pc-12(d) Meridian collapse
Project status changes:
  - Enterprise PC: retired → active (machine layer not installed)
  - 04-unraidTheme → 27-unraidTheme (machine-local)
Next:
  - Sean: rebase + merge `worktree-b-fixes-b1-b10` and merge `claude/kind-diffie-41820e`, then re-pin (^pc-51)
  - Sean: one Centric push from Claude closes ^pc-50 + ^pc-09; DSDS decision (^pc-54); Enterprise install route (^pc-53)
  - Open Agent Engine filing skipped: the personal Linear lane MCP did not connect this session; ^pc-51–^pc-54 have no issues yet
--- END BLOCK ---

### 2026-10-14 — Fontface renumbered 24 → 25; its baton now syncs through git

SessionID: 2026-10-14-work-mbp-renum25
--- SESSION BLOCK ---
Date: 2026-10-14
Machine: Work MacBook Pro
Surface: Claude Code (desktop) · side session of the GitHub-route landing session
Agent: Claude Opus 5.5
Project(s): 25-fontface, 24-mailbird (index only)
Summary: Two projects held number 24. Mailbird (2026-10-13) was already on GitHub; Fontface
(2026-10-12) was older but had never been committed, because `.gitignore` had no allow-entry for
its folder. Sean chose: Mailbird keeps 24, Fontface moves to 25 (same rule as 22: whoever reaches
GitHub first keeps the number), and Fontface's baton is now tracked like 21–24. The folder was
untracked, so it moved with a plain `mv`, not `git mv`; Mailbird did not change at all.
Decisions: project numbers go to whoever reaches origin first (now applied twice: 22, 25).
Changed: 07-projects/25-fontface/{README,SESSION-STATE}.md (renamed from 24-fontface, now tracked),
.gitignore (allow-entry), _PROJECTS.md, 06-context/project-registry.md, 06-context/project-context.md.
Verification: no `24-fontface` references remain except the history note. validate-integrity went
from 3 errors (the untracked Fontface links) to 0. nightly rebuild wrote 0 files.
Incident: a sibling session's accidental `git reset --hard` at 07:37 PDT wiped the three index
edits. The Fontface files and .gitignore were restored by that session; the three index edits were
rebuilt from this session's transcript (the staged Fontface lines plus the 25 renumber). Nothing lost.
Pending: none for the renumber.
--- END BLOCK ---

### 2026-10-13 — Walls: one GitHub route for every surface; file edits are their own class

SessionID: 2026-10-14-work-mbp-ghroute
--- SESSION BLOCK ---
Date: 2026-10-13 (landed 2026-10-14)
Machine: Work MacBook Pro
Surface: Claude Code (desktop) · session cb042892-48fa-4e0e-864c-1fec1fe4e8fd
Agent: Claude Opus 5.5
Project(s): 19-workspace-brain (walls)
Summary: Sean was blocked switching GitHub accounts, fighting the gates, and unable to comment,
open issues or merge. Diagnosis: six stacked gate layers. Claude's gh knew only `snds`; gh cannot
verify TLS or read the keychain inside Claude Code's sandbox; P31 denied plain file edits on an
employer default branch; the auto-mode profile named ~/fontface as the only trusted repo; and
GitHub never lets Sean approve his own PRs, which Claude opens as him. Built (Sean chose "Build all
four", merge after a GitHub rule change): 09-tools/gh_route.py (pinned) routes every GitHub login by
repo owner for git (bin/git-credential-ws) and gh (bin/gh, linked as ~/.local/bin/gh); overlay v6;
the lanes include carries the route and sends routed owners' SSH forms over HTTPS; file writes are
class `edit` (never branch-checked); commit and push on default stay denied. Merged origin/main and
pushed main (7 stuck local commits went up).
Decisions: decision-claude-employer-surface amendment 2026-10-13. The employer insteadOf lives only in
the lanes include, not the tracked overlay (H25 employer-substance). No admin-override merges.
Changed: 09-tools/{gh_route,git_lanes,wall_guard,profile_resolve,pr-desk,test-validators}.py,
00-bootstrap/doctor/{pin_lib,installers,render_shims}.py, 00-bootstrap/dist/{gh,git-credential-ws,
claude-overlay.env,git/lanes/ws-lanes.inc}, devices.json, surfaces.json, action-policy.json (+fixture),
fixtures (wall_guard, git_lanes, identity), .gitignore, the decision note.
Verification: pin checks 7/7 (profile_resolve 406/406 outside the sandbox), installers 72/72,
git_lanes 67/67, render_shims 67/67, affected test-validators classes green, ruff clean,
employer-substance clean. Harness red only on pre-existing items (evidence-grades census from the
mechanization review) and sandbox-environment timeouts (nightly 74/74 outside the sandbox).
Pending: Sean runs --install-pin, --install-git-hooks, --install-claude-overlay (in that order) and
starts a fresh session; updates the auto-mode profile and /sandbox (gh, git) himself; changes GitHub
rules on the two merge-list repos. Then ^pc-09 and ^pc-50 can close after one real Centric push.
Incident: a stray `git reset` during landing unstaged other sessions' work on main; restored exactly
from the landing stash's index tree (no content lost). Two projects share number 24 (mailbird, fontface).
--- END BLOCK ---

### 2026-10-13 — Mailbird (working name): research + Phase 0 foundation

SessionID: 2026-10-13-cloud-mb24
--- SESSION BLOCK ---
Date: 2026-10-13
Machine: Claude cloud session (no local device)
Surface: Claude Code (web) · session_0144yFcMoSfdF3X1gnyuaC76
Agent: Claude Opus 5.5
Project(s): 24-mailbird (github.com/snds/Mailbird, personal-solo, public)
Summary: Started a cross-platform PIM super app with mail, calendar, contacts, and notes.
Research covered competitors and protocols. The OSS license audit verified every dependency. Then
the scaffold went up: a React + shadcn (Base UI, Nova) mobile-first shell, 3-tier tokens, Material
Symbols through a local shadcn transform, a Tauri 2 shell, and a Rust capability matrix. It is in
PR #1.
Decisions: the Material Symbols variable font is drawn inside an <svg>, which keeps shadcn's svg
selectors and the live axes. Icon axes are @property tokens. Tauri 2 everywhere, with Capacitor as
the mobile fallback. Mail stays on the device to limit Google CASA scope. Notes are Markdown + Yjs,
with import instead of sync for Keep and Apple Notes.
Changed: 07-projects/24-mailbird/{README,SESSION-STATE}.md, _PROJECTS.md.
Verification: in the code repo, lint, build, cargo test (4), and cargo check of the shell pass.
Phone, tablet, and desktop screenshots checked.
Pending: product rename (name collides with Mailbird, Inc.); Tauri mobile spike.
--- END BLOCK ---

### 2026-10-08 — Emphasis Engine: native examples for 12 design systems + knowledge survey

SessionID: 2026-10-08-cloud-ee7n4t
--- SESSION BLOCK ---
Date: 2026-10-08
Machine: Claude cloud session (no local device)
Surface: Claude (claude.ai, cloud workspace) · session_013599uzq7Yw95BjZS2GJFrB
Agent: Claude Opus 5.5
Project(s): emphasis-engine (github.com/snds/emphasis-engine, personal-solo)
Summary: Built native example pages for 12 design systems in Emphasis Engine. Each one uses the
system's own components and guidelines and lives on its own iframe page. The app sends the solved
theme by postMessage, and a service worker precaches every page. Earlier the same day: a
Photos-style phone editor, with a tick scrubber, color strips, a bottom dock and sheets. Recorded
what theming each system taught us as knowledge entries, plus ranked ideas for the Centric design
system.
Decisions: info must never alias brand. Component tokens must be var() references. The kit's
restore never overwrites provider-written variables.
Changed: 08-knowledge/design/ds-native-theming-survey.md (hub), ds-native-<13 systems>.md,
centric-ds-ideas-from-ds-survey.md, 08-knowledge/_INDEX.md, 02-shared-references/knowledge-hints.json.
Verification: vault-health clean; validate-integrity, validate-links, build-related, check-secrets
(incl. employer-substance baseline), validate-workspace, and the dispatcher self-test all pass.
Later the same session: fixed the profile bugs at the root, in the probe and generator. Generated
profiles are now probed from the native pages. Each trace is confirmed by a second sentinel pass.
Scoped stock values are read from the declaring rule, and status names beat chroma (selectors
count). Ant Design and Coinbase CDS take the solved values in their theme objects. The lessons are
in the survey entry's "Probing a design system from outside" section.
Pending: none for this thread.
--- END BLOCK ---

### 2026-10-06 — Claude becomes an employer-approved surface

SessionID: 2026-10-06-work-mbp-cl7e01
--- SESSION BLOCK ---
Date: 2026-10-06
Machine: Work MacBook Pro
Surface: Claude Desktop / Cowork (linked to this computer; tests run in a cloud copy with git 2.54)
Agent: Claude Opus 5.5
Project(s): 19-workspace-brain
Summary: Centric moved its agent tooling to Claude. Retired the "every Claude surface is personal-only"
rule. Claude now follows the same device and identity model as Cursor and Codex, and Centric repos
run under centric-engineering (branch → PR → human review). Kept the walls: personal content never
lands in an employer repo (I1 at the floor and in the guard, now for Claude too); conduct binds Claude
through P30–P32 and a new floor rule that refuses employer default-branch, unreadable-default and
non-branch pushes (I2); credentials stay scoped per repo (snds over HTTPS with Claude's gh; Centric over
the github-work SSH alias and the device-default gh).
Decisions: [[decision-claude-employer-surface]] (new; supersedes the Claude exception in
[[feedback-credential-scoping]], whose old text is quoted in its History). Sean said the Claude login
account is not an identity key: a personal account may do Centric work when the content stays in
Centric repos and project folders. Work devices = Work MBP only (default). No employer content in
personal claude.ai memory, Projects or artifacts (default).
Changed: action-policy (P11–P14 retired, P30–P33 cover claude, P21 scoped to third-party/unknown),
devices (IR1 personal repos only, I2 all-agent branch rule), profile_resolve (identity, floor, cached
HEAD reads), wall_guard (R3 for Claude; off-device R1 denies; R7 notice), render_shims (no transport
block; employer identity include; work-device permissions), installers, session-status, closure,
intent-run, beacons and every dist beacon, docs, and the wall_guard, identity, closure, git-lane and
action-policy fixtures. New wall_guard cases prove a personal identity into an employer repo is still
denied (R3) for Claude.
Verification: nightly --phases rebuild OK; workspace-harness all lanes PASS (44 quality gates,
connections, tokens) with git 2.54, where the hook-level floor fixtures run instead of skipping.
Committed separately first: the in-flight plain-language change (ec31408).
Next: ^pc-50 — reinstall the Claude overlay on each Mac, re-paste BEACON.md into the claude.ai profile,
--install-pin; Centric HTTPS fallback for Claude; prove Claude Code prompt routes in an employer cwd.
--- END BLOCK ---

### 2026-09-30 — Catalogue leftover primitives

SessionID: 2026-09-30-work-n8p4
HostSession: 96ff1652-9409-4c69-925c-b886a0451f97
--- SESSION BLOCK ---
Date: 2026-09-30
Machine: Work MacBook Pro
Surface: Cursor
Project(s): employer repo (see H25)
Summary: Closed leftover catalogue docs work. Substance stays on the employer tracker.
Evidence:
  - employer pull request merge and CI success read back from the tracker — verified
Pending resolved:
  - Remaining shipped primitives get docs pages and Storybook entries.
Next:
  - Continue remaining waves when asked. Do not bump the host pin.
Employer repos (H25 limits):
  - emp-58e872c4 — branch-pr
--- END BLOCK ---

### 2026-09-30 — close employer session

SessionID: 2026-09-30-work-mbp-k4m9
HostSession: e99647e9-a32b-43b0-a19e-9300741158c6
--- SESSION BLOCK ---
Date: 2026-09-30
Machine: Work MacBook Pro
Surface: Cursor
Project(s): employer repo (see H25)
Summary: Closed the session. Substance stays on the employer tracker.
Evidence:
  - merge and issue-close receipts read back from the employer tracker — verified
Next:
  - Human review of the open employer pull request
Employer repos (H25 limits):
  - emp-fa196873 — branch-pr
--- END BLOCK ---

### 2026-09-29 — Intent declarations for human review

SessionID: 2026-09-29-work-k4m2
HostSession: 66dadf59-2524-4185-96e1-822e497b1286
--- SESSION BLOCK ---
Date: 2026-09-29
Machine: Work MacBook Pro
Surface: Cursor
Project(s): workspace-brain
Summary: Two employer intent declarations were opened for human review. One has since merged; the other was closed without merging. Approval text still waits on a human commit, because an agent trailer blocks that line. A one-time inventory of workspace-derived files was printed in chat only.
Evidence:
  - Intent declaration merge state read back from the hosting forge — verified
Decisions:
  - Approval text is recorded only after a human merge, and not by an agent commit.
Pending added:
  - Record approval on the merged intent file with a human commit. Decide whether the closed declaration should be reopened.
Next:
  - Human commit for the approval line. Human decision on the closed declaration.
Employer repos (H25 limits):
  - emp-f0d5b1d5 — branch-pr
  - emp-95addf9e — branch-pr
--- END BLOCK ---

### 2026-09-27 — PlanetCompiler living roadmap
SessionID: 01a08bae-ad4a-7dc1-bfb2-f6d79fdd25fe-roadmap

--- SESSION BLOCK ---
Date: 2026-09-27
Agent: Codex
Surface: Codex desktop
Machine: Personal MacBook Pro
Project(s): PlanetCompiler

Created a stable offline HTML roadmap and editable Markdown source in PlanetCompiler at Sean's request. Preserved the full eleven-step plan, six milestones, acceptance gates and 109 checklist entries. Added maintenance instructions to the local AGENTS, README and canonical handoff so future implementation/review checkpoints update the same artifact. Milestone A remains in progress; no production acceptance was inferred. No background automation was created.

Continuation: Sean directed execution through the roadmap. Added exact resident component reuse and stage/age timing telemetry. Retained all 384 actual components on repeat pose. Five-route cadence 119.76/s; camera gaps improved markedly. Preserved a 45 ms outlier, two non-reproducing repeats, and a lifecycle harness setup failure corrected in a separate passing 53-check run. Core Debug/Release 12/12 pass; seven route records verify and ten scheduling corruptions fail. Updated the living roadmap with two scoped tested tasks; milestone A is still open. Full evidence is PlanetCompiler/evidence/phase-6/reuse/.

Paths: PlanetCompiler/roadmap.html; PlanetCompiler/docs/ROADMAP.md; PlanetCompiler/scripts/build-roadmap.py. Canonical handoff: 07-projects/13-legion/docs/planet-lab-independent/SESSION-STATE.md.
--- END BLOCK ---

### 2026-09-26 — PlanetCompiler true-scale landmark fixture
SessionID: 01a08bae-ad4a-7dc1-bfb2-f6d79fdd25fe-phase6

--- SESSION BLOCK ---
Date: 2026-09-26
Agent: Codex
Surface: Codex desktop
Machine: Personal MacBook Pro
Project(s): PlanetCompiler; independent Planet Lab scoped handoff

Summary: Sean authorized planetary scale with surface reference details. Implemented a complete Earth-radius synthetic cube-sphere with adaptive patch-local geometry, continent/ridge/rolling references, north crater island and distance bands. Native controls reach orbit, approach, low pass, face edge and opposite side. Legion unchanged.

Evidence: Debug and Release pass 12/12 portable suites. Native seven-pose run passes 53/53 checks, including running archive fingerprint and observed pending-stop restoration. Reviewed seven original images; crater is recognizable but markings alias and some local views have weak contrast. No independent adversarial or human phase-six acceptance. Complete final source/binary/artifact hashes are in `evidence/phase-6/manifest.json`.

Correction: Unreal initially skipped relinking a modified external library. Preserved the stale capture run, added archive-dependent compile identity and runtime hash, rebuilt and reverified.

Continuous flights: Added five bounded 20-second routes and actual viewport render-thread callback timestamps. Weighted cadence 119.30/s at 2027 × 1090; worst interval 32.56 ms. This is not GPU presentation FPS. Five real route records verify; twelve planted corruptions fail. A separate six-image descent is excluded from timing. Native build passed. New evidence/source/binary manifest lives in `evidence/phase-6/flight/`; baseline manifest remains historical.

Runtime: Unreal remains open at the crater low view, localhost MCP 8765. New report: http://127.0.0.1:8771/flight/proofboard.html. Prior evidence remains unchanged.

Limits/next: Instrument preparation/upload/publication delay and assess visible detail transitions. Low flights replaced terrain 22 times/20 seconds; camera-to-committed-preparation distance reached 7.26 km at the corner, not a certified geometry error. Collision, streaming/cache, GPU presentation, continuous visual and photographic/geological acceptance remain open.

Commit blocker: The user refreshed ownership cache, but no-remote PlanetCompiler remains unknown. ws-lanes still refuses commit. Requested human-terminal `python3 ~/Projects/workspace/09-tools/profile_resolve.py owners set PlanetCompiler personal`; resolver requires human TTY. No bypass. Stage flight changes together with the already-staged baseline before retrying local commit. Last project commit cdb16a4; no remote.

Handoff: `07-projects/13-legion/docs/planet-lab-independent/SESSION-STATE.md`.
--- END BLOCK ---

### 2026-09-24 — Subatomic token-audit: adversarial review, fixes, PR #20

SessionID: 2026-09-24-work-sub9r2
--- SESSION BLOCK ---
Date: 2026-09-24
Machine: Work MacBook Pro
Surface: Claude Code (desktop app) · Claude Opus 5.5
Project(s): 23-subatomic-design-tokens-course
Artifacts:
  - 09-tools/token-audit.py — 31 reviewed defects + 7 fix-introduced regressions fixed; new TA024; a self-test case per defect
  - 08-knowledge/cross-domain/process-rigor-gaps.md — protocol #6: lint 09-tools scripts locally with ruff (CI-only); review new L3 detectors adversarially
Decisions:
  - Sean asked to commit, open a PR, and merge. The work had already been auto-committed to main as 3daed0f with no review, so the PR carried an adversarial review instead.
  - TA018 is judged per component stylesheet, overriding the review's per-rule walker. Real-data calibration showed per-rule checking flags correct demo CSS.
  - Campaign themes get the sub-brand cosmetic allowlist in code. The docs already said so; the code didn't.
Evidence:
  - PR merged with all 4 CI checks passing @ github.com/snds/workspace/pull/20 → e763ed5 — verified
  - Two Agent Todo issues filed @ Linear personal lane (SEA-35, SEA-36) — verified
Pending added:
  - personal:SEA-35 — token-audit value-level Figma↔code parity
  - personal:SEA-36 — Figma variable scope / publish-set probe
Next:
  - Sean to pick a real (personal) token source for token-audit's first non-demo run. Employer repos only by copying the tool in, per the independence contract.
  - Self-improve backlog, carried from 2026-09-23: prompt-hook lexical misroutes on design-token prose (mvp, light, aliasing, distribution, integration, dependency)
--- END BLOCK ---

### 2026-09-24 — Codex environment probe recorded

SessionID: 2026-09-24-personal-mbp-cdx8f2
--- SESSION BLOCK ---
Date: 2026-09-24
Machine: Personal MacBook Pro
Surface: Codex desktop
Agent: GPT-6 / Codex
Project(s): no project home — session-log only
Summary: Ran the requested environment probe with recording enabled; command exited 0 and the saved record was read back.
Artifacts:
  - 02-shared-references/probes/codex@personal-mbp.json — recorded Codex environment probe; detection remains unverified with a host-family conflict.
Evidence:
  - Probe record creation and JSON read-back @ 02-shared-references/probes/codex@personal-mbp.json — verified; this does not verify host identity.
Notes:
  - Shared session compaction ran during closeout; existing other-session records and unrelated working files remain outside this session's commit.
  - Close-out dispatcher passed harness self-test, connections/token checks, surface trajectories, and vault health.
--- END BLOCK ---

### 2026-09-24 — Env probe record (cursor)

SessionID: 2026-09-24-voyager-q4n8c
--- NANO BLOCK ---
Date: 2026-09-24
Machine: Personal MacBook Pro
Surface: Cursor
Ran `ws hook probe-env --host cursor --via terminal --record` → wrote 02-shared-references/probes/cursor@personal-mbp.json (acting_host cursor via env, verified:true, no conflict). Hook probe status not-installed. No decisions.
--- END BLOCK ---

### 2026-09-24 — Env probe record (claude-code)

SessionID: 2026-09-24-voyager-p7e2k
--- NANO BLOCK ---
Date: 2026-09-24
Machine: Personal MacBook Pro
Surface: Claude Desktop / Cowork (Code tab)
Ran `ws hook probe-env --host claude-code --via terminal --record` → wrote 02-shared-references/probes/claude-code@personal-mbp.json (acting_host claude-code via ancestry, verified:false, no conflict). No decisions.
--- END BLOCK ---

### 2026-09-24 — Zero-Vector wave 0: G4e, promotion batch, re-pins

SessionID: 2026-09-24-work-zv4e
--- SESSION BLOCK ---
Date: 2026-09-24
Machine: Work MacBook Pro
Surface: Claude Code
Agent: Claude Opus 5.5
Project(s): 19-workspace-brain (Zero-Vector wave 0)
Summary: G4e confirmed and closed; G5c dry-run clean; surfaces.json promotion batch; two bug fixes found on the way (ws_hook probe merge, pin_lib nested arming); re-pinned twice, now at 918a329.
Artifacts:
  - 02-shared-references/surfaces.json — claude-code H2/H19 and cursor H19 to enforced-partial; H17/H22 refs verified; codex H19 held back; H17-R7 text
  - 02-shared-references/probes/claude-code@work-mbp.json — re-taken from the agent shell after G4e (overlay v5 present)
  - 09-tools/ws_hook.py — env-only probe record keeps payload-derived detection (+2 self-test cases)
  - 09-tools/prune-our-branches.py — one scan per git common dir (+4 self-test cases)
  - 00-bootstrap/doctor/pin_lib.py — armed guard counts nesting depth (+1 self-test case)
Decisions:
  - Sean: G4e done; run the promotion batch ahead of the G5c apply
  - claude-code H19 promoted to enforced-partial, not enforced (hook core registered only for probes in wave 0)
  - G5c apply not manufactured: no merged-PR branch of ours exists on this device
Evidence:
  - v5 overlay + floor live (`git hook list pre-push` = ws-claude-wall; TestClaudeFloor OK) @ Work MBP Claude session — verified
  - G5c dry-run: vetted, exit 0, zero deletions, credential classes gh:default-account and https:github.com+gh:default-account @ control/receipts.jsonl — verified
  - pin at 918a329 with install-log entry and backup; prune vetted-status = vetted @ ~/.config/snds-workspace — verified
  - harness 36/36 outside the Bash sandbox @ 09-tools/workspace-harness.py — verified
Pending resolved:
  - G4e (Sean); surfaces.json promotion batch; H17-R7 text; prune dedupe; re-pin
Next:
  - G5c apply once a merged-PR branch of ours exists (e.g. cds #50's head after it merges)
  - Personal MBP G3d and G4d
  - Sean: doctor drift (~/.cursor/hooks.json, 4 retired cursor-* scripts, launchd timer, 1 un-acked audit MISS)
  - Follow-up: keep one env_probe per `via` in tracked probe records (finding #2)
--- END BLOCK ---
