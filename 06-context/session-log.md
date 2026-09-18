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










### 2026-09-17 — Phosphor consume (cds #46 / proto #84)

SessionID: 2026-09-17-work-ph84
--- SESSION BLOCK ---
Date: 2026-09-17
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 19-workspace-brain; employer cds (#46); saas-plm-prototype (#84)
Summary: Dual-set Icon landed on cds `main`. Proto consume PR is merge-ready: header Phosphor toggle, Vite 8 CSR resolve, lint-ds semantic tokens. Not merged. Harvested later-breakers into [[cds-host-consume-order]].
Decisions:
  - Catalog names stay Material ligatures; `set` is renderer only.
  - `cds-exports-check` does not catch named exports on an existing subpath, nor Rolldown CSR maps.
  - New proto files must author semantic color tokens; copying a baseline leak still fails the ratchet.
Evidence:
  - cds #46 MERGED @ https://github.com/cpes-software/cds/pull/46 — verified
  - proto #84 MERGEABLE CLEAN @ https://github.com/cpes-software/saas-plm-prototype/pull/84 — verified
  - proto #84 not merged — verified
Pending resolved:
  - Dual-set Icon on cds `main`
  - Proto consume PR opened and CI green
Next:
  - Human merge of proto #84 if wanted. Do not agent-merge.
--- END BLOCK ---

### 2026-09-17 — late close: cui PR 312 quality gate

SessionID: 2026-09-17-work-pr312
--- SESSION BLOCK ---
Date: 2026-09-17
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 02-centricPLM (centric-ui advisory)
Summary: Closed an Aug 18 Cursor thread on cui [#312](https://github.com/cpes-software/centric-ui/pull/312) Quality gate. Knip `unused` failed: `@xyflow/react` is imported by FlowCanvas but marked optional in `packages/ui/package.json`. Typecheck, lint, format, duplicates, and tests passed. Verdict then was do-not-merge. PR later merged 2026-08-18 with the check still red. No employer code written this close.
Decisions:
  - Optional peer + unconditional import is a real knip fail, not a flake.
  - Employer merge stays human-owned; this thread does not reopen #312.
Evidence:
  - Quality gate `unused` @ https://github.com/cpes-software/centric-ui/actions/runs/31852905498 — verified
  - PR 312 MERGED 2026-08-18T14:31:38Z with Quality gate still FAILURE — verified
Next:
  - Resume only if Sean asks. Live baton stays lint:ds / cui #398.
--- END BLOCK ---

### 2026-09-17 — leftover cds consume closed (#77 / #78)

SessionID: 2026-09-17-work-cds78
--- SESSION BLOCK ---
Date: 2026-09-17
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 19-workspace-brain; employer saas-plm-prototype (#77, #78); cds (#35)
Summary: Closed the leftover consume thread. cds #35 landed Toaster / `./sonner` / SplitDragHandle / ChipMultiSelect. Proto #77 merged host chrome without later commits; #78 cherry-picked the leftovers onto `main` (`adac92b`). Gate `cds-exports-check` is on proto `main`. Merge-before-late-push drops follow-ups the same way squash does. Workspace plan-ahead skill already on vault `main`.
Decisions:
  - Overlay ≠ Pages `main`; print numbered order + first later-breaker before dual-repo consume.
  - centric-ui consume of host-chrome APIs is a later pass — do not start until Sean names it.
Evidence:
  - proto #78 MERGED @ https://github.com/cpes-software/saas-plm-prototype/pull/78 (`adac92b`, 2026-09-11) — verified
  - proto #77 leftovers on `origin/main` @ `adac92b` ancestor — verified
Pending resolved:
  - cds #35 then proto re-export Toaster / SplitDragHandle / ChipMultiSelect
  - Pages gate so overlay-ahead cannot hide missing `main` exports
Next:
  - centric-ui host-chrome consume only if Sean names it (employer proto HANDOVER).
--- END BLOCK ---

### 2026-09-17 — collaborative canvas rec (employer ui)

SessionID: 2026-09-17-work-cvrec
--- SESSION BLOCK ---
Date: 2026-09-17
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 02-centricPLM (centric-ui advisory)
Summary: Closed an Aug 19 Cursor thread on a license-free collaborative canvas for PLM (review, whiteboard, vision board, print markup, optional 3D). Recommendation only — no employer code, PR, or spike. No employer architecture written into this vault.
Decisions:
  - Embed the MIT editor; do not buy a vendor workspace product as the PLM canvas.
  - Own a session/room plus pluggable surfaces; do not search for one library that also does 3D.
  - Keep domain markup and 3D as separate surfaces. License-key SDKs are out while “no license” holds.
Next:
  - Resume only if Sean asks. No c8 issue filed (movement-only; no employer home for an unsolicited rec).
--- END BLOCK ---

### 2026-09-17 — Supplier Portal polish session close (proto)

SessionID: 2026-09-17-work-supplier-portal-close
--- SESSION BLOCK ---
Date: 2026-09-17
Agent: Cursor Composer
Surface: Cursor
Machine: Work MacBook Pro (CS-K746DRWXY1)
Project(s): saas-plm-prototype (cpes-software)
Summary: Closed a resumed Supplier Portal polish thread. Work already on proto `main` via merged PRs #14–#16 (Aug 2026): single-company portal, My Home insights/welcome, LandingDataTable landings, seeded POs, host Header → Supplier Portal Demo, portal avatar email links, demo hash **push** for Back/Forward. No new uncommitted portal work from this baton; checkout was on `feat/page-composer-model` (untracked `canvases/` left alone).
Decisions:
  - Portal demo is Performance Fabrics only (no company switcher).
  - Waiting On: Needs you / Awaiting buyer. Complete cards: Completed on + success hover.
  - Demo navigations push `location.hash` (not `replaceState`) for Back/Forward.
Artifacts:
  - https://github.com/cpes-software/saas-plm-prototype/pull/14 (merged)
  - https://github.com/cpes-software/saas-plm-prototype/pull/15 (merged)
  - https://github.com/cpes-software/saas-plm-prototype/pull/16 (merged)
Pending added:
  - Optional: Sean Miro board catalog for further portal gaps (offered; board not sent).
Next:
  - If continuing portal: send Miro share/export, or pick next surface from proto HANDOVER.
  - Unrelated: `feat/page-composer-model` + untracked `canvases/` — separate thread.
--- END BLOCK ---

### 2026-09-17 — centric-ui workflowAuthor PR #282 closeout

SessionID: 2026-09-17-work-wf282
--- SESSION BLOCK ---
Date: 2026-09-17
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.5
Project(s): 02-centricPLM (centric-ui workflowAuthor), saas-plm-prototype (pickup context only)
Summary: Picked up Aug workflow-authoring thread; rebased `feat/workflow-author-typed-step-editors` onto main (clean); fixed Technical-mode test gating; marked PR #282 ready; Prettier quality-gate fix pushed. PR is MERGED (2026-08-14) with green checks. Logged durable auth fact: cloud Unauthorized API ≠ GH PAT.
Decisions:
  - Technical mode off by default; JSON rails / raw step JSON / Export opt-in; Common vs Advanced palette.
  - Cloud API identity lives in `.env.local` as `VITE_API_KEY` + `VITE_SERVICE_NAME` — not a GitHub PAT.
Evidence:
  - PR #282 merged @ https://github.com/cpes-software/centric-ui/pull/282 (sha 06672954) — verified
Pending resolved:
  - Finish / land workflowAuthor typed editors + Technical mode (PR #282)
Next:
  - Optional wedges still open if product wants them: richer Call beyond HTTP; typed `for` / `fork` / `listen`.
  - Earlier same-day baton (Figma Icons spot-check / library publish) still pending Sean review — see 02-centricPLM Live handoff.
--- END BLOCK ---

### 2026-09-17 — centric-ui draft PRs (#87 / #179)

SessionID: 2026-09-17-work-cui-drafts
--- SESSION BLOCK ---
Date: 2026-09-17
Agent: Cursor Grok 4.5
Surface: Cursor
Machine: Work MacBook Pro
Project(s): centric-ui (cpes-software; employer)
Summary: Triaged open drafts; promoted #87 (caution Badge/Button) after rebase onto main dropping redundant app.css (tokens already from #225); reviewed #225 gate as inherited main red; resolved #179 merge conflicts keeping main density + VITE_DEV_BACKEND_URL and retaining cloud-Keycloak→:3000 auto-bind.
Artifacts:
  - https://github.com/cpes-software/centric-ui/pull/87 — ready; +3 Badge/Button only
  - https://github.com/cpes-software/centric-ui/pull/179 — MERGEABLE after conflict resolve
Decisions:
  - #87 app.css hunk dropped — caution tokens already on main via #225; Alert caution via #119.
  - #179 keeps main density + serviceProxy; unique value is port-3000 auto-bind + env docs.
  - #225 quality-gate red was shared main outage, not the token PR.
Pending added: (none — pc-06 progressed in place)
Pending resolved: (none fully closed)
Next:
  - Human review/merge #87 and #179; assign Alex on #179.
  - #88 harness still draft — rebase after #87 if still wanted.
--- END BLOCK ---

### 2026-09-17 — wsx Path B picker + Windows handoff zip

SessionID: 2026-09-17-work-wsxpc
--- SESSION BLOCK ---
Date: 2026-09-17
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 18-bootstrap-generator
Summary: Path B launcher now auto-detects folder-capable apps, ranks a platform default (Cursor on Windows/Linux, Claude Code on Mac), emits all adapters, and can open the generator folder with a paste-ready prompt. Built per-OS zips; Windows copy placed on Desktop for PC colleague testing.
Artifacts:
  - wsx-generator-windows.zip — 267 KB handoff on Desktop (also dist/; gitignored)
Decisions:
  - Interview still starts from the generator folder, not the new workspace dest.
  - Windows ranking prefers Cursor.exe under %LOCALAPPDATA% even when `cursor` is not on PATH.
  - VS Code is offered only if it can actually launch (config-only ~/.vscode is skipped).
Evidence:
  - Desktop zip @ /Users/sean.sands/Desktop/wsx-generator-windows.zip — verified (267 KB, 17 Sep 10:39)
  - Linear Agent Todo for colleague test @ linear-personal — blocked (MCP needsAuth)
Next:
  - Colleague tests start.bat on PC; expect Cursor default + paste prompt.
  - Colleague/Olga full wsx path when asked — 07-projects/18-bootstrap-generator/SESSION-STATE.md.
--- END BLOCK ---

### 2026-09-17 — Guided Setup Other-chat wrap-up (employer proto)

SessionID: 2026-09-17-work-gs-other-chat
--- SESSION BLOCK ---
Date: 2026-09-17
Agent: Cursor Grok 4.6
Surface: Cursor
Machine: Work MacBook Pro
Project(s): employer saas-plm-prototype (centric-engineering)
Summary: Closed an Aug 20 Other-chat pass on `feat/guided-setup-live`. Wrap-ups now render as markdown, stay conversational, close with Continue instead of “shall we?”, and name the next card or rail step. Shipped as `5ac6a09` and opened [PR #56](https://github.com/cpes-software/saas-plm-prototype/pull/56). No employer detail written into this vault.
Decisions:
  - Other-chat wrap-up copy is next-screen aware (sub-step title in-group; rail label when crossing groups).
  - Employer delivery stays branch → PR → human review; this session did not merge.
Next:
  - Human review of https://github.com/cpes-software/saas-plm-prototype/pull/56
--- END BLOCK ---

### 2026-09-17 — session-end (Figma catalog thread + wsx Path B launcher)

SessionID: 2026-09-17-work-k7m2
--- SESSION BLOCK ---
Date: 2026-09-17
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 02-centricPLM, 18-bootstrap-generator, 19-workspace-brain
Summary: Closed the 2026-09-16 Figma catalog thread (overlap reflow, modes-for-variants, Text Styles iff no Size/Density — already on `main`). Folded leftover `wsx` Path B work: `launch.py` detects folder-capable apps, offers to open the generator folder, emits all adapters; `scan.py` gains folder-capable/open helpers; README Path B + Linux.
Decisions:
  - CDS `apps/docs/AGENTS.md` / `CLAUDE.md` left untracked (employer repo, `centric-engineering` — no auto-commit).
  - Interview still starts from the generator folder, not the new workspace dest.
Next:
  - Colleague/Olga `wsx` path when asked.
--- END BLOCK ---

### 2026-09-17 — Figma Icons page pack + section A–Z

SessionID: 2026-09-17-work-figma-icons
--- SESSION BLOCK ---
Date: 2026-09-17
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.5
Project(s): 02-centricPLM
Summary: On Centric SaaS PLM DS Figma (`o6o1ZuGHxDow2vHLuYXT6X` Icons page `4:2`), packed icons into the existing 12-col grid (80×72, origin 32,64) after erroneous icon deletions left gaps, then ordered all 27 category sections A–Z left-to-right. Earlier in this thread (Aug): field-overlay/control-radius parity plan + Proto #18 / cui #225 / #179 PRs — treat as prior history; this baton is Icons hygiene done.
Decisions:
  - Icons within a section sort A–Z then pack row-major; section width hugs used columns (`40 + cols*80`).
  - Section gutter stays 96px; do not invent a new Icons layout system.
Evidence:
  - Figma Icons page verified: 0 grid gaps, 27 sections alphabetical (action…travel)
Next:
  - Sean visual spot-check of Icons page in Figma; publish library if needed.
  - Code parity backlog remains in `08-knowledge/design/figma-to-code-parity-plan-2026-08-06.md` (P1+ still open where not already landed).
--- END BLOCK ---

### 2026-09-17 — CDS shadcn consume waves on cds main

SessionID: 2026-09-17-work-shadcn-consume
--- SESSION BLOCK ---
Date: 2026-09-17
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 02-centricPLM
Summary: Consumed leftover shadcn UI into `@centric/ui` on cds (Calendar/DatePicker wave, then Combobox/menus wave). #44 stacked onto a feature base after #43 merged, so Combobox never hit `main` until cherry-pick #45.
Decisions:
  - DatePicker is Popover + Calendar; no shadcn DatePicker root. Density cells; Material Symbols `Icon`; no local focus rings; no Lucide.
  - Do not replace Progress/Toaster or CDS `Field`/`EmptyState`/Sheet. Drawer is the swipe bottom sheet only.
  - Stacked PRs that merge after the base is on `main` must be re-landed onto `main` (cherry-pick), not treated as done.
Evidence:
  - cds #43 + #45 merged @ https://github.com/cpes-software/cds — verified (`origin/main` `4dfb957`, CI green)
  - #44 merged to `feat/consume-shadcn-calendar-datepicker`, not `main` — verified via `gh pr view 44`
Project status changes:
  - 02-centricPLM: shadcn UI consume complete on cds `main` except skip-list (Field collision, EmptyState, chart, carousel, chat kit).
Next:
  - Hosts import new `@centric/ui` subpaths from cds `main` (calendar, date-picker, combobox, input-group, drawer, input-otp, menubar, navigation-menu, item, direction, plus wave-1 primitives).
  - Skip-list stays unless Sean asks. Restore cds stash `wip icon font host load` if still wanted.
--- END BLOCK ---

### 2026-09-17 — Brand-soft tokens landed on cds main

SessionID: 2026-09-17-work-pr42
--- SESSION BLOCK ---
Date: 2026-09-17
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): cds (cpes-software/cds); 02-centricPLM
Summary: After Sean published the Figma library, the brand-soft map was committed off origin/main as `feat/primary-soft-tokens` (`2a12726`) and opened as cds [#42](https://github.com/cpes-software/cds/pull/42). That PR is merged (2026-09-16). The original cds checkout's other WIP was left alone. cds HEAD in this window is now `feat/land-shadcn-combobox-on-main`.
Decisions:
  - Token commit was isolated from charting/docs WIP via a worktree so PR 30's merged branch was not reused.
Evidence:
  - cds [#42](https://github.com/cpes-software/cds/pull/42) merged @ GitHub — verified
  - Figma library publish — verified (Sean)
Pending resolved:
  - Commit/PR cds primary-soft mapping
  - Publish the SaaS PLM Figma library (this wave)
Next:
  - Wave 1 leftover still out: ChipMultiSelect, TypeTag, OutlinedValueChips
  - Do not mix combobox-land WIP with token follow-ups
--- END BLOCK ---

### 2026-09-16 — CDS Figma catalog reflow + construction rules

SessionID: 2026-09-16-work-figma-catalog
--- SESSION BLOCK ---
Date: 2026-09-16
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 02-centricPLM, 19-workspace-brain
Summary: Un-collided new catalog sections in Centric SaaS PLM Figma (`o6o1ZuGHxDow2vHLuYXT6X`); rebuilt Filter Chip / Spinner / Step Glyph / Chart Frame / Flow Canvas with subcomponents and style axes as modes. Text-style sweep applied then fully reverted. Construction rule: Text Styles iff the component has no Size/Density type axis — those modes own `fontSize`.
Decisions:
  - Catalog SECTION ownership + AABB reflow is rule 20 ([[figma-ds-surface-authoring]]); generate cannot skip [[figma-modes-for-variants]].
  - Text Styles do not apply when Size or Density drives type (rule 21). Verified: a style dual-binds then replaces `Button / Size`.`fontSize`.
  - Table / Data Table stays out of this Figma file.
Pending added:
Pending resolved:
Project status changes:
  - 02-centricPLM: Figma catalog overlap + modes land in the file; vault rules on `main` (`d414136`…`f6090f9`). Publish still manual (^pc-18).
Next:
  - Publish the centric-ui Figma library (Sean, Assets panel).
  - Continue Base UI / docs / Storybook parity on CDS as needed; Table later.
--- END BLOCK ---

### 2026-09-15 — portable session-status card closed; doctor MISSes acked

SessionID: 2026-09-15-work-ssack
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 19-workspace-brain
Summary: Closed the leftover 2026-09-11 Cursor thread that shipped `session-status.py` (`46d207a`) so every LLM emits Claude's notices + all projects + pending card. Acknowledged 3 bootstrap MISSes on this Work MBP (`workspace-doctor.sh --ack`); `session-status.py --check` now reports 0 notices. Layer 0 no longer treats "make sure" as produce. Did not rewrite Live handoff — later 2026-09-15 sessions already own lint:ds / brand-soft.
Decisions:
  - Session-start card is `09-tools/session-status.py` on every surface; continuations skip it. [[decision-session-status-card]]
  - Doctor ACK is machine-local (`~/.claude/ws-state/ack-mark`), not a git write.
Pending added:
Pending resolved:
Next:
  - Next new Cursor session on this machine should show 0 MISS notices on the boot card.
--- END BLOCK ---

### 2026-09-15 — Brand-soft tokens: Figma and code share one map

SessionID: 2026-09-15-work-cdsmap
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): cds (cpes-software/cds); Figma SaaS PLM DS; 02-centricPLM
Summary: Closed the Wave 1 semantic/component token map. Figma `action/primary/soft*` and `Object Chip / Color` publish WEB `var(--sem-primary-soft*)`; cds consumes Tailwind `bg-primary-soft` / `text-primary-soft-foreground` / `border-primary-soft-border`. Data Summary hover stays `interaction/primary/hover`. Nested Chip Cluster instance overrides needed a second rebind. cds uncommitted; Figma library unpublished.
Decisions:
  - Brand-soft = Blue/3 fill, Blue/11 text, Blue/6 border — same recipe as status-soft, brand hue. Not info-soft cyan.
  - Component Color collections alias semantics. Code does not mint `--object-chip-*` CSS vars.
  - Labelled-value hover wash is the interaction overlay, not the chip fill.
  - Rebind nested instance paint overrides; main-set rebind does not clear them.
Evidence:
  - Figma Compact Rest + Editable Hover variable defs @ o6o1ZuGHxDow2vHLuYXT6X — verified
  - cds ObjectChip / DataSummary / LockedField / ChipCluster tests 31/31 — verified
  - Figma library publish — unverified (Sean, manual)
  - cds commit/PR — unverified (not asked; employer repo)
Pending added:
  - Publish the SaaS PLM Figma library after Wave 1 rebind
  - When asked: commit/PR cds primary-soft mapping
Pending resolved:
  - Wave 1 Figma paints no longer bind Color/Blue primitives on Object Chip, Chip Cluster, Data Summary hover
Next:
  - Sean publish Figma library
  - Commit/PR cds token work only if Sean asks
  - Wave 1 leftover stays out: ChipMultiSelect, TypeTag, OutlinedValueChips
--- END BLOCK ---

### 2026-09-15 — CDS Material Symbols Icon; proto consume; cui next

SessionID: 2026-09-15-work-mbp-cds-icons
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): cpes-software/cds, saas-plm-prototype
Context profile: centric-engineering

Summary: Implemented CDS `Icon` as Material Symbols ligatures (`name`, `size`, `filled`; axes from `iconAxes`). Dropped Lucide in CDS. Proto replaced Lucide with `@centric/ui/icon`. Hosts that still pass `Icon={Component}` keep compiling.

Decisions:
- Ligature `name` is the CDS path. `IconGlyph` still accepts a `className` slot so Lucide hosts type-check without bringing `lucide-react` back.
- Glyph text sits in an inner `aria-hidden` span so it is not the control name.
- Preferred / close / mill / style metaphors: `keep`, `close`/`delete`, `apartment`, `checkroom`.
- centric-ui waits until CDS + proto are on main; that is now true. Remaining work is cui tickets.

Artifacts:
- cds #39 merged — Icon + drop Lucide
- cds #40 merged — host slots + accname
- saas-plm-prototype #80 merged — proto consume

Pending added:
- centric-ui consume `@centric/ui/icon` (Sean’s cui tickets — review + merge)
- Optional: palette accordion nested `<button>`; light-mode / toast / BOM icon pass

Next:
- Review and merge the cui tickets. Nothing else blocks this icon program.
--- END BLOCK ---

### 2026-09-15 — Unattended runner: decided not to build it; guard stays

SessionID: 2026-09-15-work-mbp-runner-decision
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Sean asked whether to delete the unattended runner and its tasks as an orphaned
artifact that reports stale. Checked before answering: nothing reports it stale (0 notices,
vault-health clean across 170 notes), there is no timer, no cron entry, no launchd agent, and
no queue item. The only artifact is `09-tools/check-unattended-runner-gate.py`.

Recommendation given and taken: keep the gate, close the question. The gate is a lock, not a
feature — it refuses unsafe unattended runs and is silent otherwise. The risk it blocks does
not depend on a runner existing, because `/schedule`, the `CronCreate` tool and any headless
`claude -p` run can reach an unattended path by accident. Deleting a lock because the door is
unused is backwards. It also costs nothing at rest: `09-tools/` is not auto-loaded, so zero
tokens per session.

The actual irritant was one baton line reading "authorized-but-unbuilt", which looks like a
pending task for something nobody intends to do. Replaced with a decided line pointing at
[[decision-no-unattended-runner]], which also records what a safe first version would look
like if the answer ever changes: one lane, tools removed rather than granted, and only
tickets Sean wrote himself.
--- END BLOCK ---

### 2026-09-15 — Plain language is now a standing requirement

SessionID: 2026-09-15-work-mbp-plain-language
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Sean said an explanation went over his head and asked for plain language as a
durable rule, giving ADHD and autism as the reason.

Recorded in two places. `04-preferences/user-preferences.md` → Response Style holds the full
rule: it outranks every other style note in that file, plain does not mean shallow (keep the
depth, change the packaging), and it lists concrete do/avoid items plus the worked example
that caused it. `06-context/CRITICAL_FACTS.md` carries a three-line version, because that
file loads on every session and this applies to every reply.

The failure it came from, kept as the example: an explanation of the unattended runner used
`--allowed-tools`, `--strict-mcp-config`, "prompt-injection path" and "lane-scoped" with no
definitions, stacked four abstract numbered points, and never said the simple thing first —
that it reads job tickets and does the work on its own, and is switched off because a ticket
could tell it to do something harmful.

Session floor went 14,778 → 15,480, still inside the 17,000 budget. Worth the tokens: it is
an accessibility requirement, not a style tweak.
--- END BLOCK ---

### 2026-09-15 — Record the shared-git-index hazard (and a coverage gap it exposed)

SessionID: 2026-09-15-work-mbp-index-hazard
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Tree settled (Cursor's @shadcn/lint work landed, 22 harness gates green, no
divergence), so the hazard deferred earlier is now recorded. Extended
[[multi-session-workspace-resilience]] rather than minting a new entry — it already owns
git/concurrency and had a Key diagnostic lessons section.

The hazard: two agents in one working tree share `.git/index`, so `git add <mine>` followed
by `git commit` commits whatever the other agent staged in between — the commit takes the
whole index, not your paths. Hit for real this session: a commit swept in two files
belonging to the concurrent Cursor session under a message asserting it held only my work.
Recovery is `git reset --soft HEAD~1` → `git restore --staged <theirs>` → re-commit. The fix
is a pathspec-limited commit, `git commit -- <paths>`, which ignores index state.

Worth separating: the fragment model prevents merge conflicts between disjoint FILES; it does
nothing about a shared INDEX. Different layers, and only the first had been solved.

Measured a coverage gap in the documented mitigation while writing it up. Point 3 of that
entry says a PostToolUse hook records edited paths so session-end stages only those. True,
but it records only `Edit|Write|MultiEdit|NotebookEdit` — anything written through Bash
(heredoc, sed, `python3 -`) is invisible. This session's touch file held 8 paths against 67
the commits actually changed, because auto-mode routes most writes through Bash. And it runs
at session-end only, so a manual mid-session commit bypasses it entirely. Both limits are now
stated in the entry instead of being implied protection.

Also added: Layer 1 cannot see what you just wrote. `vault-retrieve.py`'s FTS index rebuilds
at SessionStart and in `nightly.py`, so a mid-session entry is invisible to the lexical
fallback until `--rebuild`. Found by checking my own work — the natural phrasing "why did git
commit take files I did not add" produced a visible Layer-0 miss with two wrong lexical hits;
after rebuild the new entry is the #1 hit. Verified all three phrasings now reach it: two via
Layer 0 triggers, one via Layer 1.

Committed with `git commit -- <paths>`, which is the practice the entry now prescribes.

22 harness gates green, vault-health 0/0 across 170 notes, ruff clean.
--- END BLOCK ---

### 2026-09-15 — Close the scoped-commit gap, verify the Open Engine, retire Windows

SessionID: 2026-09-15-work-mbp-fixes-and-engine-verify
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Cleared the outstanding items.

**Scoped-commit gap closed (the fix, not just the note).** `handle_stop` now snapshots
`git status --porcelain` once per turn and appends newly-dirty paths to the session touch
file, so Bash-written files are attributed too — previously only Edit/Write tool paths were
recorded (8 of 67 this session), which is what dropped session-end into the blanket
`git add -A` that swept a concurrent session's work. And `_stage_session_scope` now subtracts
`_other_session_claims()` — the union of every other live session's touch file — so a path
another session has declared is never staged here even if it went dirty on our watch. Three
tests added; 52/52 pass. Snapshot files are gitignored. The residual race is stated in the
entry rather than hidden, and the manual-commit caveat still stands.

**Open Engine verified — the test that had never run.** Label-filtered `list_issues` on the
personal lane: 30 issues, and all 23 anchor→issue mappings in `open-engine/personal.md`
resolve. **Zero orphaned pointers.** The other 7 are engine infra (SEA-5/6/7/8) plus three
created after the migration.

**The migration was already done; the baton was stale.** It happened 2026-07-30, substance
graduated to `project-context-detail.md` 2026-08-07, and `project-context.md` is now 93 lines
/ 12.4 KB costing 560 tokens at session start (head-30) — not the ~61 KB the stale entry
implied. The five unmigrated items are deliberate refusals (three `c8` with no valid pointer,
two lane-ambiguous), not backlog. Corrected in SESSION-STATE.

**Rec 13 closed.** Its Work-MBP half was already installed — verified `~/.cursor/hooks.json`
carries `beforeSubmitPrompt` → `cursor-prompt-route.sh`. Its Windows half is dropped: Sean is
selling the desktop. Windows retired across `fact-machine-layer-installs`, the CLAUDE.md
machine-label map (auto-loaded, so one line lighter), and the two queue items it scoped —
`^pc-03` (machine-layer installs: no Windows install route needed, and none should be built)
and `^pc-39` (author email: Personal MBP only).

**Bootstrap MISSes acknowledged.** All three dated 2026-07-29, two in an employer repo, one in
a bare `~/Projects` — seven weeks of a notice firing every session start, which is the
detector-everyone-ignores failure mode. `workspace-doctor --ack`; notices down to one.

**Reported, not actioned — deliberately.** `^pc-04`/SEA-11 is fully done in the vault but sits
in `Agent Review` on the board. Review→Done is the supervisor's transition, and this session
has spent its length insisting a machine should not claim done on judgment. `^pc-13`/SEA-15
correctly stays open: its Perplexity-Space half is genuinely unfinished.

22 harness gates green, 52/52 negative fixtures, ruff clean.
--- END BLOCK ---

### 2026-09-15 — vault CI green after Layer-0 brain-root fix

SessionID: 2026-09-15-work-n3p8r
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6 / Cursor / Work MBP
Project(s): 19-workspace-brain
Summary: Follow-up after lint:ds session-end — committed leftover canonical-docs housekeeping, then fixed GitHub Actions workspace-integrity (Cursor trajectory self-test empty because `resolve_brain_root` ignored cwd/CLAUDE_PROJECT_DIR). HEAD `9178aaf` integrity + fixtures green.
Artifacts: none new (CI + docs already on main)
Decisions:
  - `resolve_brain_root` must consider CLAUDE_PROJECT_DIR, cwd, and parents so a clean GHA checkout of snds/workspace routes without ~/.claude/workspace-brain-path
  - Layer-0 handback routes must not name gitignored `06-context/side-chat-inbox.md` (clone-invisible; harness now treats gitignored paths as missing)
Pending resolved:
  - canonical-docs-voice leftover (title-description + YAML block-list triggers) committed as `c69baef`
  - workspace-integrity Cursor trajectory self-test on Actions — fixed `9178aaf`, confirmed green
Evidence:
  - workspace-integrity success @ https://github.com/snds/workspace/actions/runs/34994953678 — verified
  - validator-fixtures success @ https://github.com/snds/workspace/actions/runs/34994953629 — verified
Next:
  - Human review of cui #398; after merge remove centric-ui-lint-ds
  - Later: wave 2 shadcn rules; CDS theme reset; proto pre-commit lint:ds; ratchet paydown
--- END BLOCK ---

### 2026-09-15 — lint:ds overlay land + session-end

SessionID: 2026-09-15-work-k7m2q
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6 / Cursor / Work MBP
Project(s): 19-workspace-brain; cds; centric-ui; saas-plm-prototype
Summary: Stand up `09-tools/shadcn-lint/` as an independent product-repo lint service; install `lint:ds` on cds (baseline 0), proto (ratchet 5410, merged), cui (ratchet 988, in review). Outstanding-item lists are numbered and unblocked-first.
Artifacts:
  - 09-tools/shadcn-lint/ — overlay + probe + host configs + ratchet (whitelisted in .gitignore)
  - 08-knowledge/engineering/shadcn-lint-token-tiers.md
  - 06-context/memory/decision-shadcn-lint-independent-service.md
Decisions:
  - Overlay-first; do not fold @shadcn/lint into vault CI or eslint-off-system
  - Wave 1 errors = no-raw-colors + ds-lint/no-tier-leakage only
  - CDS packages baseline 0; cui/proto ratchet existing debt
  - Theme reset is a later product-CSS PR
Evidence:
  - cds #41 merged @ https://github.com/cpes-software/cds/pull/41 — verified
  - proto #81 merged; Pages on main succeeded @ https://github.com/cpes-software/saas-plm-prototype/pull/81 — verified
  - vault overlay `51e7859` + merge `f446cbb` pushed to snds/workspace main — verified
  - cui #398 CI green, REVIEW_REQUIRED @ https://github.com/cpes-software/centric-ui/pull/398 — verified
Deferred commits:
  - 03-skills/canonical-docs-voice/SKILL.md — pending, not this overlay (stash: canonical-docs leftover)
  - 08-knowledge/design/canonical-documentation.md — pending, not this overlay
Next:
  - Human review of cui #398; after merge remove centric-ui-lint-ds
  - Later: wave 2 shadcn rules; CDS theme reset; proto pre-commit lint:ds; ratchet paydown
--- END BLOCK ---

# Shapr3D MCP setup

SessionID: 2026-09-14-shapr3d-mcp-setup
Date: 2026-09-14
Agent · Surface · Machine: GPT-6 · Codex desktop · Work MacBook Pro
Context profile: personal-solo, explicitly declared by Sean.
Project home: temporary name `Projects/shapr3d-personal`; final project concept/name pending reference. No numbered vault project allocated yet.

## Live handoff

- Installed Alfredoalv13/shapr3d-mcp revision `88fcefe` in the sibling Projects checkout with frozen uv dependencies.
- Registered `shapr3d` globally using the Codex CLI; read-back confirms enabled. Project config alone was not loaded by this parent task. Native tool refresh requires restart; real MCP client connection tested successfully.
- All 30 upstream tests pass. Generated test plate STEP + STL; independent mesh topology, 60 × 40 × 8 mm bounds, and analytic volume checks pass (0.00205% volume error).
- Sean installed and launched Shapr3D during the session. The server app bridge opened the STL; Computer Use observed the imported plate with four holes and captured the app window.
- Evidence and portable setup notes: `Projects/shapr3d-personal/README.md`, `validation.json`, `models/shapr3d_stl_import.png`, and reproducible smoke script.
- Upstream executes unrestricted Python. Screenshot tool falls back to entire display; prefer app-targeted Computer Use. STEP is editable-solid interchange, without feature history; STL is a mesh.
- Next: receive visual reference and dimensions; establish final project identity, create versioned models, and inspect in Shapr3D. STEP app import and app-side measurements remain unverified.
- No employer repository modified. No conceptual design work started.

# Custom desk reference intake

SessionID: 2026-09-14-custom-desk-references
Date: 2026-09-14
Agent · Surface · Machine: GPT-6 · Codex desktop · Work MacBook Pro
Context profile: personal-solo.

## Live handoff

- Sean is designing a custom desk, desktop first. Primary Pinterest form plus upper platform atop main desktop like Aero; exclude Hex Desk side extensions.
- Source references and decisions are in `Projects/shapr3d-personal/DESIGN-BRIEF.md`.
- Native Shapr3D MCP tools now callable. Imported `HEXADesk-Main.SLDPRT` successfully in Shapr3D. Exported STEP copied from Documents to project models as `hexadesk_main_reference.step`; MCP reads one solid, 2046.458 × 895.562 mm plan, 25.4 mm thickness (source Y-up).
- Original SolidWorks files preserved in project reference directory. Shelf part and complete assembly remain untested.
- Pinterest sign-in required in the in-app browser; asked Sean to sign in. Primary pin image and board not yet visually assessed. Asked for dimensions and platform equipment.
- Next: complete reference review, inspect shelf, agree dimensions, then desktop/platform study. No custom design generated yet.

# Custom desk dimensions and mounting concept

SessionID: 2026-09-14-custom-desk-materials
Date: 2026-09-14
Agent · Surface · Machine: GPT-6 · Codex desktop · Work MacBook Pro
Context profile: personal-solo.

## Live handoff

- Sean confirmed 71.93 × 29.92 inches overall desktop envelope, hardwood likely American walnut, thickness open. Magnetic ferrous underside for 3D-printed dock/KVM/accessory cradles; organization shelf with probable laptop arm; black straight and custom curved T-slot rail idea for LG ultrawide and Audioengine speakers.
- Pinterest access now works. Visually inspected both specific pins and board overview. Sustema main form has an angled wraparound outline and central seating recess. Do not claim whole-board review or generated fidelity.
- Updated `Projects/shapr3d-personal/DESIGN-BRIEF.md` with source links, proposed construction logic, verified/provisional hardware envelopes, and explicit unknowns. `desktop-parameters.json` records exact footprint and null values for undecided dimensions.
- Full rectangular 1 mm steel sheet estimated 24 lb; smaller panels proposed, not approved. Wood-movement allowances needed. Magnet capacity requires physical stack testing. Structural rail must not rely on thin sheet for arm loads.
- Live Humanscale M21BJTBC configurator shows black 8-inch/8-inch links, standard tilt, 100 mm VESA and clamp; successor M2 Pro wording. Notebook holder not selected. Native SolidWorks import and STEP conversion verified in prior entry.
- Asked whether standing or fixed base, and slim versus substantial edge. Answers pending. No custom geometry generated or final thickness selected.
- Next: use answers to develop desktop/platform layout, then fit equipment with actual revision/adapter/cable clearances. Curved rail fabrication and load ratings remain unverified. No purchase or supplier communication performed.

# Custom desk base and rail research

SessionID: 2026-09-15-custom-desk-base-rail
Agent · Surface · Machine: GPT / Codex desktop / Sean's Mac
Context: personal-solo

Sean confirms existing Humanscale laptop holder and clearance work; do not reopen that question. Prefer complete Aero standing-base reuse, but documented replacements are acceptable. Custom longitudinally bent black T-slot rail is selected in principle; investigate specifications and pricing rather than segmented alternatives. Smaller thin steel panels are accepted, with broad flexible coverage for frequently changing magnetic modules.

Working files remain outside the portable workspace in Projects/shapr3d-personal. Updated DESIGN-BRIEF.md and desktop-parameters.json; added BASE-AND-RAIL-PLAN.md. Downloaded and visually reviewed relevant Aero assembly drawings in reference/aero-es71-assembly.pdf: bolted complete base appears reusable, but mounting dimensions and revision-specific payload remain unverified. DeskHaus Apex Pro provides a documented fallback ($925 observed configuration, advertised 600 lb lifting capacity); actual interface fit remains pending. Alubend advertises one-off extrusion bending; prepared quotation requirements, no supplier contacted or custom price obtained.

Next: desktop/platform concept with provisional thickness and shelf dimensions, steel coverage zones and frame clearance. Thickness, recess, shelf dimensions and rail radius remain open. No new custom desk CAD produced in this research pass. MCP installation/test and native SolidWorks-to-STEP reference conversion were completed in prior sessions.





### 2026-09-15 — A8 third node: R2's premise demonstrated, `wght` settled as a true positive

SessionID: 2026-09-15-work-mbp-probe-wght
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Third live node, probed to settle whether the raw variable-font weight axis (`wght`)
was a true positive or an artifact of Figma echoing a resolved axis. Settled: true positive,
and the same data proves R2's underlying premise.

The decisive evidence is a natural experiment, not an argument. A 15px focus-ring radius
appears in node 1 as the BARE property `radiusRing: 15`, with no focus-ring token anywhere in
that node's map; it appears in node 3 as the TOKEN `focus-ring-radius/md: 15`, with no bare
key. One concept, one value, two nodes — bare where unbound, token where bound. If bare keys
were echoes of bound properties, node 3 would show both; it shows one. So a bare key can be
trusted to mean unbound, which is the assumption R2 rests on and had not previously been
tested.

Applied to `wght`: node 1 reports 400 while its only weight token is `font-weight/medium: 500`;
node 2 reports 461 against tokens 500 and 600. Neither value exists as a token in its own map,
so neither can be an echo. Node 3 reports 400 alongside `font-weight/normal: 400`, which is
coincidence — 400 is Regular. Likely cause worth naming: the `ligature/*` entries show this
file uses variable ICON fonts, which carry their own `wght` axis; `var(--icon-size)` is bound
and the icon weight axis is not, which also explains node 2's otherwise odd 461.

Also confirmed on node 3: the rebuilt property-name discriminator holds — `foreground` passes,
and the Figma-only construction tokens (`Day/top-left` and siblings, sanctioned by doctrine
rule 0) pass as tokens. No metadata was supplied for this node and the probe correctly
reported `verified: R1, R2` only, declining to claim R3 rather than implying a clean tree.

Three nodes now: node 1 eight R2 hits, node 2 one, node 3 five. R1 clean on all three — the
hard gate has not over-fired once on real production work.

CONCURRENCY: the Cursor `@shadcn/lint` work is still in-flight and uncommitted in this tree,
with its routing fixture red and `trigger-routes.md` drifted. This commit again contains only
the probe files.
--- END BLOCK ---

### 2026-09-15 — A8 over-fire test: a second node rebuilt the R2 discriminator

SessionID: 2026-09-15-work-mbp-probe-overfire
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Sean asked for a second node specifically to check whether R2 over-fires. It did,
immediately, and the fix is the more valuable half of A8.

The separator-based discriminator flagged `foreground` — a real single-word semantic token,
sitting among `surface/popover` and `chrome/border/subtle` with a `var(--sem-muted-foreground)`
CSS twin. Flagging it would have told a designer to bind something already bound.

Three attempts, each failing on live data the previous one had not seen: "a token has a
slash" flagged doctrine's own `space-0` / `radius-none` / `border-width-0`; "a token has a
separator" flagged `foreground`; the rule that holds is **"the key names a Figma/CSS
property"**. Token names are unbounded and system-specific; property names are a closed,
stable set. Keying on the open set was the error, and the tell was in the first node all
along — it was full of bound fills and produced no colour-valued bare key, because unbound
values only ever surface under a property name.

After the rebuild: node 2 reports 1 hit (was 2), node 1 still reports 8 (unchanged).
Precision up, detection unweakened.

R3 also gained live vocabulary: real trees use `symbol` / `instance` / `slot` / `frame` /
`text`, and a `slot` nested inside an instance must not reset instance context or every icon
vector in a composed overlay would be flagged. Pinned by self-test.

Open, stated: both nodes report a raw variable-font weight axis (`wght`) at different values
while named weight tokens exist in the file. Consistent and probably genuine — if Figma
merely echoed a resolved axis, node 2's would match its bound weight token, and it does not.
Not rounded up to certain.

Generalised into [[decision-capture-and-assess-split]]: when writing a discriminator,
enumerate the closed set, never the open one.

CONCURRENCY NOTE: a Cursor session (Grok 4.6) landed `@shadcn/lint` work in this same tree
mid-session — new routes, knowledge-hints, `_INDEX`, `09-tools/shadcn-lint/`, and a baton
rewrite. Its `shadcn-lint-service` routing fixture is currently RED and `trigger-routes.md`
has drift; both belong to that in-flight work, not to this. This commit deliberately contains
only the probe files, so their work is left untouched in the tree for them to finish. I
corrected one stale line in their baton rewrite (it still said the probe had only seen
synthetic fixtures).
--- END BLOCK ---
