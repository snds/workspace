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





















### 2026-09-23 — Zero-Vector wave 0: fix round, publish, decisions, D5

SessionID: 2026-09-23-work-4602a8
--- SESSION BLOCK ---
Date: 2026-09-22 to 2026-09-23 (one conversation; resumed as 4602a8c3 after 42c33259 compacted)
Machine: Work MacBook Pro
Surface: Claude Code (Mac desktop app) · Claude Opus 5.5
Project(s): 19-workspace-brain (Zero-Vector harness plan v1.1, wave 0)
Summary:
- Wave 0 (H16, H19, H24, H2, H22, H17, H25, H1, H3) built in intent worktrees T1–T8, verified by three
  lenses (T10), fixed in T11 (23 fixes, including the walls F-01/F-02 floor blockers). Sean published
  it: `main` fast-forwarded to `7fefad5`.
- Harness triage: three red gates were all Claude Code sandbox effects (xcrun cache unwritable, `ps`
  denied). With the real git the harness passed 35/36; profile_resolve passed 340/340 outside the
  sandbox. The harness now prints an environment note naming those fingerprints and the fix.
- Durable preference (a56782a): give Sean commands only when they are ready to run now.
- Sean's decisions: walls F-11 pinned in wave 1 (declared residual until then); tests F-07 keep
  blocking; D5 employer email domain `centricsoftware.com` (landed `6d30676`, exact match, three
  reviewers clean); D7 three H25 parts to wave 1. Recorded in `1e217b1`. F-14 recommendation given;
  waiting on Sean.
- Ten merged intent worktrees removed (branches kept). T10/T11 findings register saved to held.
- Queue: ^pc-47 gains the work-email finding (5 lines in 3 tracked files; scan does not count the
  domain yet). New ^pc-48: router fires on task notifications (X2); ritual nag false alarm on resume.
Next: Sean's F-14 call. If yes, move the H17 mechanics to a held register, rewrite `coverage.H17` at
class level, and record the visibility rule in 00-context-profiles.md, before the first `--install-pin`.
--- END BLOCK ---

### 2026-09-23 — Subatomic design-tokens course: capture, synthesis, token harness

SessionID: 2026-09-23-work-sub8f6
--- SESSION BLOCK ---
Date: 2026-09-23
Machine: Work MacBook Pro
Surface: Claude Code (desktop app) · Claude Opus 5.5
Project(s): 23-subatomic-design-tokens-course (new)
Summary: Sean logged into Brad & Ian Frost's *Subatomic: The Complete Guide To Design Tokens* in the in-app browser. The course explicitly offers downloads, and Sean approved them for this course only; project 22's no-video rule stands. Mapped all 372 items through the Thinkific player API at human pace. A paced, resumable downloader pulled 360 1080p Wistia videos, 358 course transcripts plus Wistia captions, slides, lesson notes and 7 demo repos (5.4 GB, 0 errors) into `<Projects>/subatomic-design-tokens-course/`, outside the vault. Wrote original notes for every chapter; delegated agents drafted Ch5–8 under a no-transcript contract. Graduated the doctrine:
- knowledge `design-token-architecture`, which includes a Curtis-vs-Frost disagreement table
- skill `token-architecture`, an L2 command hub under `ds-advisor`
- L3 detector `09-tools/token-audit.py`: 23 rules, self-tested, and calibrated on the course's own demo repo, where it found 3 genuine contrast failures, 1 dark-theme drift and 15 CSS literals, and fixed 5 false-positive classes
- a counter-stance note in framework #09
- cross-links in `fe-design-tokens` / `design-system-ops` / `tokens-and-naming.md`
- close-out detectors, knowledge hints, a trigger route, and routing corpus cases (52/52)
Also captured the process lesson in `08-knowledge/cross-domain/in-app-browser-bulk-capture.md`. All write-quality validators pass.
Pending:
- `token-audit.py`: value-level Figma↔code parity (TA014 checks names only)
- MCP probe for Figma variable scopes and the publish set
- Self-improve: lexical misroutes seen in prompt hooks this session. `mvp`→sci-linear-algebra, `light`→imaging-foundations, `aliasing`→native-visual-eval, `distribution`→sci-probability-stochastic, `integration`→science-foundations and `dependency`→sec-supply-chain all fired on design-token prose. Tighten those triggers and add forbid cases.
--- END BLOCK ---

### 2026-09-22 — Zero-Vector research and additive harness plan

SessionID: 2026-09-22-work-zv7h
--- SESSION BLOCK ---
Date: 2026-09-22
Machine: Work MacBook Pro
Surface: Claude Code (desktop app) · Claude Opus 5.5
Project(s): 19-workspace-brain
Summary: Researched Zero-Vector Design (site, Investiture tooling, Open Vector curriculum, Labrador) at a human reading pace. No AI or bot blocking was found. The upstream repos have no LICENSE file, so everything was synthesized clean-room. Planned an additive harness: 15 components in 4 waves, report-only first. The plan went through two multi-agent workflows (8 mappers; 3 designers, 3 judges, a synthesizer, 3 refuters, a reviser and a defect verifier). Healed the registry drift at HEAD.
Decisions:
  - Adopt ZV's patterns, not its tools or ideology. The employer walls and DS practice stand.
  - Project intent goes in a README block or PROJECT.md, not in the living coordination spec.
  - Nothing new is always-loaded, and nothing blocks before wave-2 telemetry and Sean's opt-in.
Evidence:
  - Registry drift healed @ 6cac460: build-registry --check 0, evaluate-skill-routing 49/49 — measured by 09-tools/build-registry.py
  - Validator chain green (16 checks) plus workspace-harness --connections --tokens PASS; floors unchanged at 10,384 / 15,440 — measured by 09-tools/workspace-harness.py
  - close-out-dispatch --run rc=0 (self-improve detectors). The plan's content is judgment-checked by the adversarial panel, not detector-verified.
Next:
  - Sean decides wave 0–1 (see ^pc-45 and the plan's "Decisions needed")
  - Once wave 0 is approved: H1 heal sequencer, H3 intent-run hardening, H2 resolver plus playbook sign-off
--- END BLOCK ---

### 2026-09-22 — Overlay rhythm and Lexical consume

SessionID: 2026-09-22-work-q4n8
--- SESSION BLOCK ---
Date: 2026-09-22
Machine: Work MacBook Pro
Surface: Cursor
Project(s): Centric design system, SaaS PLM prototype
Summary: Visual QA on menus, fields, page chrome, and comments. CDS #57 and proto #91 merged. Proto #92 consumes the rich text editor now that ./rich-text-editor is on cds main.
Decisions:
  - Menu rows share one nested radius on all four corners
  - Pages must not import a CDS named export that is not on main
  - Lexical consume waited until CDS #57 merged
Evidence:
  - CDS #57 merged @ github.com/cpes-software/cds/pull/57 — verified
  - Proto #91 merged @ github.com/cpes-software/saas-plm-prototype/pull/91 — verified
  - Proto #92 opened @ github.com/cpes-software/saas-plm-prototype/pull/92 — verified
Next:
  - Watch proto #92 Pages build and merge when it is green
--- END BLOCK ---

### 2026-09-21 — cui #413 drop widget deps

--- SESSION BLOCK ---
Date: 2026-09-21
Project(s): 19-workspace-brain (centric-ui #413)
Summary: Alex was right — the host must not declare CDS widget libraries. Removed `input-otp` and `react-day-picker` on cui #413 (`022c468`) and replied on both threads. Encoded the boundary in eng-foundations, #14, #18, ds-advisor, fe-component-architecture, and [[abstraction-hides-its-dependencies]].
Shipped:
  - centric-ui `022c468` on `feat/consume-cds-shadcn-federalization` — replies https://github.com/cpes-software/centric-ui/pull/413#discussion_r4068404303 and #discussion_r4068404401
  - Knowledge [[abstraction-hides-its-dependencies]]
Left open:
  - npm still installs both as required `@centric/ui` peers (`peer: true`). Hiding that install is a CDS change (real dependency, or optional peer off the barrel). Not started. Do not bump `cds.pin`.
  - Sean reviews cds #50. Do not agent-merge.
--- END SESSION BLOCK ---

### 2026-09-21 — proto #87 Pages build, CDS split

--- SESSION BLOCK ---
Date: 2026-09-21
Agent: Grok 4.7 / Cursor
Surface: Cursor
Machine: Work MacBook Pro
Project(s): saas-plm-prototype (proto #87); cds (prompt only, repo not edited)
Summary: Proto #87 Pages build failed because `DisclosureChevron` is not exported from CDS `DetailSection`. Host chevron restored and pushed (`6bcd04e`). Sheet flush/border and the centered section chevron are CDS defaults. Paste-ready prompt left in chat for a CDS-rooted session.
Evidence:
  - Pages job https://github.com/cpes-software/saas-plm-prototype/actions/runs/35671930108/job/106570081611 — verified (missing export)
  - Local `npm run build` after `6bcd04e` — verified (`build-ok`)
  - Chevron centering on Classic blue Where Used — not verified (no browser pass)
Decisions:
  - Unblock Pages with the host `expand_more` icon. Do not invent `DisclosureChevron` on the proto.
  - CDS owns sheet `gap-0` + `border-border`, and one centered section chevron on the existing `./DetailSection` subpath.
Next:
  - Open Cursor on `/Users/sean.sands/Projects/cpes-software/cds` and paste the prompt from this chat. Branch and PR. Do not merge. Do not edit the prototype in that chat.
  - After that PR is on cds `main`, drop the proto sheet `gap-0 border-border` override and consume the centered chevron.
--- END BLOCK ---

### 2026-09-21 — cui #413 peer replies

SessionID: 2026-09-21-work-c4p13
--- SESSION BLOCK ---
Date: 2026-09-21
Machine: Work MacBook Pro
Surface: Cursor
Project(s): 19-workspace-brain (centric-ui #413)
Summary: Replied on centric-ui #413. `input-otp` and `react-day-picker` are required `@centric/ui` peers re-exported from the barrel; the app does not use them yet.
Evidence:
  - Review replies @ https://github.com/cpes-software/centric-ui/pull/413#discussion_r4068308656 and #discussion_r4068308733 — verified (gh api read-back)
Next:
  - Sean reviews cds #50. Alex has the peer explanation on cui #413. Do not agent-merge. Do not bump a host cds.pin.
--- END BLOCK ---

### 2026-09-21 — cds #50 CodeQL green

SessionID: 2026-09-21-work-k7m2
--- SESSION BLOCK ---
Date: 2026-09-21
Machine: Work MacBook Pro
Surface: Cursor
Project(s): 19-workspace-brain (cds #50)
Summary: Cleared the remaining CodeQL failure on cds #50. Polynomial CSS scans are now linear. Checks green at a346322.
Decisions:
  - Keep declaration and var() match behavior; change only the scan method.
Evidence:
  - CodeQL and CI on cds #50 @ a346322 — verified (gh pr checks)
Next:
  - Sean reviews cds #50. Do not agent-merge. Do not commit cds canvases/.
--- END BLOCK ---

### 2026-09-18 — Figma Icons family (all ligature text selected)

SessionID: 2026-09-18-work-figma-icon-family
--- SESSION BLOCK ---
Date: 2026-09-18
Agent: Cursor Grok 4.6
Surface: Cursor
Machine: Work MacBook Pro
Project(s): 02-centricPLM
Summary: Resumed the Aug 19 Icons catalog thread on Centric SaaS PLM DS Figma (`o6o1ZuGHxDow2vHLuYXT6X`, Icons page `4:2`). Plugin session still cannot load bare `Material Symbols` or `Material Symbols Outlined` (only Rounded + Sharp). Selected every ligature TEXT in every variant (8,362 nodes / 4,181 sets) so Sean can set the family in the Type panel. Fill: 1 on new Style=Filled variants is still pending after the family change.
Decisions:
  - Default family is `Material Symbols` (no Outlined/Rounded/Sharp suffix). Outlined is the default axis state; filled is FILL=1, not a second family.
  - Do not assign Rounded/Sharp as a stand-in. Plugin cannot `loadFontAsync` the target family — Type panel only.
Evidence:
  - `listAvailableFontsAsync` (1,938 families): no exact `Material Symbols`; no `Material Symbols Outlined`
  - Canvas families at select time: Outlined 4,244 · Rounded 4,100 · `Material Symbols` 18
  - Selection applied: 8,362 TEXT nodes
Pending added:
  - After family apply: select only Style=Filled TEXT on newly added icons → set Fill: 1
  - Then publish the Figma library (`^pc-18`)
Next:
  - Confirm Type panel family is `Material Symbols` on the current selection (re-select all icon TEXT if the selection dropped).
  - Ask an agent to select new-icon Style=Filled TEXT only, then set Fill: 1.
  - Spot-check Icons + publish.
--- END BLOCK ---

### 2026-09-18 — CDS ShadCN federalization instance 0 (local)

SessionID: 2026-09-18-work-cds-fed
--- SESSION BLOCK ---
Date: 2026-09-18
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): employer cds (PR #48); centric-ui chat root only
Summary: Instance 0 wrap pass is local on cds `feat/shadcn-federalization` @ `5b21ec9` (10 ahead of origin / PR #48 @ `8da550c`). True stock L0 + extras wrap + ShadCN vs CDS Storybook exists only for Button, Input, Badge. Remaining L0 files are previous CDS implementations moved under `vendor/shadcn`, not restored stock. Chat was rooted in centric-ui so every cds write prompted Allow; `move_agent_to_root` aborted. Sean takes a new chat with folder `/Users/sean.sands/Projects/cpes-software/cds`. Not pushed. Storybook on :6006 was stopped.
Decisions:
  - Keep local until Sean reviews. No push, no PR merge, no cui `cds.pin` bump.
  - Public API stays additive. Extras on the wrap, not in L0, once stock is restored.
  - Do not run `npm run shadcn:sync` until it merge-adds sibling checksums (today it rewrites the map to `tailwind.css` only).
  - Progress stays native `<progress>`; AspectRatio stays CSS `aspect-ratio`. StatusPill/TypeTag stay laterals, not Badge.
  - Resume in a CDS-rooted Cursor folder. Do not keep editing cds from a centric-ui chat.
Evidence:
  - cds `feat/shadcn-federalization` @ `5b21ec9` — 10 local commits ahead of origin — verified
  - `l0:check` 52 files; stock stories only `{button,input,badge}.shadcn.stories.tsx` — verified
  - cds PR #48 still the origin tip @ `8da550c` — not updated this session
Pending resolved:
  - Isolated wrap worktrees merged locally (button/input/badge/rest)
  - Unused modules thin-wrapped into L0 (still CDS-as-L0, not stock)
Next:
  - Open Cursor on `/Users/sean.sands/Projects/cpes-software/cds`. Restore stock L0 + extras wrap + `*.shadcn.stories.tsx` for every remaining checksum module. Then fix `shadcn:sync`. Still no push until Sean reviews.
--- END BLOCK ---

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
