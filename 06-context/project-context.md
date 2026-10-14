# Project Context — Sean Sands
_Authoritative source: this file (06-context/project-context.md)_
_Written by any agent — the git checkout is the source of truth._
_Last updated: 2026-10-14_

> **Platform note (2026-06-16):** the workspace itself was refactored to be portable, git-native, and
> LLM/surface/device-agnostic, then consolidated onto `main` at `github.com/snds/workspace` (16-PR stack,
> all five validators green). The git checkout — not Google Drive — is now the source
> of truth. Day-to-day contribution rules live in [01-frameworks/08-workspace-contribution-framework.md](01-frameworks/08-workspace-contribution-framework.md) + [AGENTS.md](../AGENTS.md). See memory `decision-portable-workspace-refactor`. The project pending items below are unchanged.

---

## Pending Items

> **⚠️ Migrated to the Open Agent Engine 2026-07-30 — do not delete items from this list.**
> Every item carries a stable Obsidian block anchor (`^pc-NN`; anchors run `^pc-01`–`^pc-53`). The
> 2026-07-30 migration covered the first 43: 38 got a Linear issue whose **only** pointer is that
> anchor (23 on the personal lane, 15 on the employer lane) and 5 were not migrated — the reasons are
> listed in the same table. Anchors added since (`^pc-44` onward) have no mapped issue. Deleting an
> anchored item orphans its issue: this file is the *substance store*, the queue holds only movement.
> The anchor↔issue mapping is in [06-context/open-engine/personal.md](open-engine/personal.md) →
> Migrated items (employer-lane mappings live in that lane's machine-local config, deliberately not
> here). One mapped issue has closed so far (`personal:SEA-11`, `^pc-04`, pruned 2026-10-14).
> **2026-08-07 harness-map #2:** long pending substance graduated to
> [project-context-detail.md](project-context-detail.md) (anchors `^pc-NN` stay on the stubs here).
> Further shrink: graduate to knowledge/artifacts, repoint Linear, *then* remove the stub.

_Triaged 2026-04-27 into three buckets: **Active** (next actions), **Deferred** (resurface on context match), **Recently resolved** (prune at next /optimize)._

### Active (next actions)

- [ ] **Roll out Claude as an employer surface on each Mac (human steps).** (Added 2026-10-06; restated 2026-10-14.) Decision: [[decision-claude-employer-surface]] (amendments 2026-10-13). Human steps, in the 2026-10-13 order, from a plain terminal: (1) `00-bootstrap/doctor/workspace-doctor.sh --install-pin`, (2) `--install-git-hooks`, (3) `--install-claude-overlay` (v6, which carries the one GitHub route `09-tools/gh_route.py`, `fd5d1ab`), then a fresh Claude session. **Sean ran all three on 2026-10-14 (verified).** The route replaces the `github-work` SSH alias for Centric pushes (^pc-09) and gives Claude the HTTPS fallback it lacked. Not confirmed: the re-paste of `00-bootstrap/dist/BEACON.md` into the claude.ai profile preferences and the re-emit of `render_shims.py --emit claude-permissions --device work-mbp`. Open: the surface-trajectory harness does not yet prove Claude Code's prompt routes in an employer-shaped folder. Open (Sean's call): personal-account Centric work falls under consumer terms, and claude.ai memory can file Centric facts. Closes with ^pc-09 after one real Centric push from Claude. ^pc-50

- [ ] **SaaS PLM prototype — DataTable contract, then the TanStack replacement.** (Added 2026-07-28.) Next: Olga reviews #13; deepen Materials lab toward the full column set post-merge; revisit the contract as acceptance checklist; WP-0 memo still unsent. Detail → [project-context-detail.md#pc-01](project-context-detail.md#pc-01). ^pc-01

- [ ] **Silence the two recurring beacon-enroll NOTEs (Work MBP main, `CS-K746DRWXY1`).** (Added 2026-07-28.) Half done 2026-09-26: `design-system` is recorded as a deliberate skip in the local, untracked `beacon-repos.ignore.txt`. Open: classify `open-design`. Detail → [project-context-detail.md#pc-02](project-context-detail.md#pc-02). ^pc-02
- [ ] **Machine-layer installs on remaining machines (FX-1/FX-14 carry-over).** Detail → [project-context-detail.md#pc-03](project-context-detail.md#pc-03). ^pc-03
- [ ] **Employer design-system migration (cpes-software)..** (Added 2026-07-15; **unblocked 2026-07-20**.) Detail → [project-context-detail.md#pc-05](project-context-detail.md#pc-05). ^pc-05
- [ ] **centric-ui PR #179 — assign reviewers + settle the redirect-URI question..** (Added 2026-07-20.) Conflicts resolved 2026-08-10; MERGEABLE — still needs reviewer (Alex). Detail → [project-context-detail.md#pc-06](project-context-detail.md#pc-06). ^pc-06
- [ ] **BE ask: `workflow-service` has no cloud dev hostname.** (Added 2026-07-20.) `workflow-service.internal.app.dev.centricsoftware.io` does not resolve (DNS/HTTP 000, vs 401 for services that exist). Workflow features can't work against cloud dev until BE exposes it or supplies the real host. Not a local config problem. ^pc-07
- [ ] **Purge two abandoned centric-ui SHAs carrying the personal email..** (Added 2026-07-20.) Detail → [project-context-detail.md#pc-08](project-context-detail.md#pc-08). ^pc-08
- [ ] **SSH to github.com:22 timing out on the Centric laptop.** (Added 2026-07-20.) Persisted all session; every push went over HTTPS instead. Likely corporate egress filtering. Fix if it recurs: point `Host github.com` and `Host github-work` at `ssh.github.com` port 443 in `~/.ssh/config`. **2026-09-22:** it recurred, and port 443 also timed out while HTTPS worked. Claude now uses HTTPS for `snds/*` (overlay v4). Cursor and Codex still use SSH over `github-work`. **2026-10-13:** fix built (gh_route + lanes include + overlay v6); installed 2026-10-14; close after one Centric push. ^pc-09
- [ ] **"Context is King" — workspace foundation refinements.** (Added 2026-07-09, Sean's directive; re-scoped 2026-10-14.) Mostly shipped: `profile_resolve.py` + `context-remotes.json` resolve the profile, `session-status.py` groups projects by profile, and batons carry `Context profile`. Left: context tags on memory/knowledge entries, and skills receiving the profile on load. Detail → [project-context-detail.md#pc-10](project-context-detail.md#pc-10). ^pc-10
- [ ] **C8/CDS semantic status-token gap (from the 2026-07-08 cell-validation session)..** Detail → [project-context-detail.md#pc-11](project-context-detail.md#pc-11). ^pc-11
- [ ] **Act on the 2026-07-08 workspace audit carry-forwards.** Detail → [project-context-detail.md#pc-12](project-context-detail.md#pc-12). ^pc-12
- [ ] **Load the evolved `ux-component-library` v2.1 on this + other machines.** Detail → [project-context-detail.md#pc-14](project-context-detail.md#pc-14). ^pc-14
- [ ] **C8 cell-indicators — Sean sign-offs to unblock propagation..** Detail → [project-context-detail.md#pc-15](project-context-detail.md#pc-15). ^pc-15
- [ ] **figma-repo-sync-plugin finalization (code-grounded plan, 2026-06-22).** Quick wins done (PR #121). Next: the engine pass — B2-core PR #122 onward (#124 B1 Type→booleans, #126 C lint gate, post-C fixes), awaiting team review/merge and Sean's regen of Builds 11.4.38–11.4.39. Detail → [project-context-detail.md#pc-17](project-context-detail.md#pc-17). ^pc-17
- [ ] **Publish the centric-ui Figma library.** Detail → [project-context-detail.md#pc-18](project-context-detail.md#pc-18). ^pc-18
- [ ] **REVOKE the Figma PAT** pasted during the 2026-06-04 session (Figma → Settings → Personal access tokens). It was used read-only for an attempted Variables API call (lacked the Enterprise `file_variables:read` scope) and shared in plaintext. ^pc-19
- [ ] **Install the `snds@snds-local` skill plugin on other machines.** Detail → [project-context-detail.md#pc-20](project-context-detail.md#pc-20). ^pc-20
- [ ] **Refresh `05-artifacts/active/trigger-cheatsheet_v1.0_2026-06-01.html` to v1.1.** Detail → [project-context-detail.md#pc-21](project-context-detail.md#pc-21). ^pc-21
- [ ] **Data table cell anatomy + state matrix..** Detail → [project-context-detail.md#pc-27](project-context-detail.md#pc-27). ^pc-27
- [ ] **C8 cell system — rollout decisions for Sean (added 2026-07-09):.** Detail → [project-context-detail.md#pc-28](project-context-detail.md#pc-28). ^pc-28
- [ ] **C8 cell system — follow-up builds (added 2026-07-09):.** Detail → [project-context-detail.md#pc-29](project-context-detail.md#pc-29). ^pc-29
- [ ] **Component Set Manager — bulk export finalization + filename template UI.** Figma plugin. ^pc-30
- [ ] **Open centric-ui PR #2 (component stories).** 22 component + 3 feature stories staged; held until [centric-ui#34](https://github.com/cpes-software/centric-ui/pull/34) merges so the PR diff is clean. ^pc-31
- [ ] **Mark `lint, types, build` as required status check on ds-docs `main`.** CI is green on [ds-docs#1](https://github.com/cpes-software/ds-docs/pull/1); update branch protection via `gh api repos/cpes-software/ds-docs/branches/main/protection` once that PR merges. ^pc-32
- [ ] **Add `.github/CODEOWNERS` to ds-docs.** Sean to provide the reviewer-per-path list; Claude opens a follow-up PR. ^pc-33
- [ ] **Wire up production deployment for ds-docs..** Detail → [project-context-detail.md#pc-34](project-context-detail.md#pc-34). ^pc-34
- [ ] **Section D — reference design-system deep reads..** Detail → [project-context-detail.md#pc-35](project-context-detail.md#pc-35). ^pc-35
- [ ] **Section B audit (18 adjacent enterprise SaaS patterns).** Defer until Section A graduations stabilize. Most B-patterns reuse Section A primitives, lower-urgency than Section D. ^pc-36
- [ ] **28 individual pattern entries pending graduation at `08-knowledge/design/{slug}.md`.** Graduate one-by-one as Centric work creates demand; the master entry already references their target paths and serves as their parent until materialized. ^pc-37
- [ ] **Stream C re-audit scheduled ~2027-Q3** (12-18 months). Emerging patterns C4 NL-workflow / C5 canvases / C7 true-merge will mature significantly. ^pc-38
- [ ] **▶ WORK LAPTOP ONLY — Migrate MCS research → `saas-plm-analysis` employer repo.** (Added 2026-09-04 from Personal MBP.) `12-MCS` is empty on personal + the repo is unreachable there; content + access live on the Centric work laptop. Full playbook in [07-projects/12-MCS/SESSION-STATE.md](../07-projects/12-MCS/SESSION-STATE.md). Sean authorized **PR + commit + merge** directly (doc-only employer repo). Review Olga's uploads first; place with context; then leave a workspace pointer stub. ^pc-44
- [ ] **Three Claude Code installs on the Work MBP produce false version-change notices.** (Added 2026-09-22.) `~/.local/bin/claude` is 2.1.280, Homebrew `/opt/homebrew/bin/claude` is a stale 2.1.173, and the desktop app's bundled binary is ~2.1.131. `_check_claude_version_change()` in `.claude/hooks/dispatcher.py` keeps one pin per machine, but each surface's PATH resolves a different binary, so the notice flips. Fix: key the pin by resolved binary path (or list all installs), and decide whether to remove the stale Homebrew copy. Logged as X3 in the harness plan. ^pc-46
- [ ] **`snds/workspace` is PUBLIC (kept public, scrub going forward); one step open: offer Sean the free branch ruleset (block force-push + deletion on `main`).** Done: email scrub `a32d08a`; employer-substance scan counts the work domain `78addf3`/`b1fd9ba` and runs in CI `909aaa6`; "private" claims corrected; `visibility: public` flag in 00-context-profiles. Detail → [project-context-detail.md#pc-47](project-context-detail.md#pc-47). ^pc-47
- [ ] **Prompt-hook false positive: ritual nag after resume (Claude Code).** (Added 2026-09-23. The router half, X2, is fixed: task notifications `daa0e94`, subagent hand-backs X2b `a65973c`.)
  - The ritual nag (`00-bootstrap/dist/workspace-reassert.sh`) said "never emitted" on a resumed session whose transcript already had the token in an assistant reply. It scans from a saved offset per session id; the resume path likely leaves that offset or the session id out of step. Low cost (one nag, a late ritual line), but it can train agents to ignore the nag.
  - Fix: check the scan offset on resume.

  ^pc-48
- [ ] **F-14 posture scrub, second pass.** (Added 2026-09-23.) The same rule moves the remaining
  machine-posture lines to held (quote them there first, then rewrite the public text): ^pc-09 and
  ^pc-46 in this file, two lines in the harness plan note, two parts of
  `06-context/memory/fact-machine-layer-installs.md`, the hostname block and the identity include
  path line in `06-context/memory/feedback-credential-scoping.md` (for the hostnames, a pointer to
  `devices.json` will do), two lines in
  `07-projects/19-workspace-brain/reports/zero-vector-harness-detail_v1.0_2026-09-22.md`, and the
  session history in `07-projects/19-workspace-brain/SESSION-STATE.md`. The list with line detail is
  held (`machine-posture_2026-09-23.md`). ^pc-49
- [ ] **Review and merge the mechanization branches.** (Added 2026-10-14, Sean approved.) 18 commits from the 2026-10-13 mechanization review sit unmerged. `worktree-b-fixes-b1-b10` (16 commits: fixes B1–B11 + follow-ons) must be rebased over main first: main redid two of its fixes as `aa8d6e1` and `6f69724` and has moved since (a 2026-10-14 merge-tree shows conflicts in 7 files). `claude/kind-diffie-41820e` (2 commits: M25 writes lane) merges cleanly. Then re-pin (`workspace-doctor.sh --install-pin`). Baton: [19-workspace-brain](../07-projects/19-workspace-brain/SESSION-STATE.md). ^pc-51
- [ ] **Save PlanetCompiler phase-6 work (data-loss risk).** (Added 2026-10-14, Sean approved.) Sean-side, on the Personal MBP: `python3 09-tools/profile_resolve.py owners set PlanetCompiler personal` (project ownership blocks commits until then), commit the phase-6 increment, and consider a private remote (`09-tools/backup-projects.py`). The work has sat uncommitted for 2+ weeks with no remote. Baton: [independent planet handoff](../07-projects/13-legion/docs/planet-lab-independent/SESSION-STATE.md). ^pc-52
- [ ] **Set up the machine layer on Enterprise (Windows desktop).** (Added 2026-10-14.) Sean confirmed 2026-10-14 that Enterprise, his personal Windows desktop, is back in use; it had been marked retired on 2026-09-15. `devices.json` already registers it (`eae4eb1`, identity rule IR4). The shims and the doctor are bash, so it needs a Windows install route first (Git Bash or WSL), then `--install-pin` and the rest. Record the checkout path in [[fact-machine-layer-installs]]. This reopens harness-map Rec 13's Windows half. ^pc-53

### Deferred (resurface on context match)

- [ ] **Re-privatize the workspace-repo author email.** Detail → [project-context-detail.md#pc-39](project-context-detail.md#pc-39). ^pc-39
- [ ] **Populate `team-practices-and-decisions.md`.** Fills in passively as decisions surface; not a discrete task. Scaffold lives at `01-frameworks/team-practices-and-decisions.md`. ^pc-40
- [ ] **TanStack Table inline editing reference implementation.** Live artifact for design-dev handoff. No recent traction; resurface when handoff need arises. ^pc-41
- [ ] **Greenfield PLM SaaS redesign architecture exploration.** Vite/React SPA + TanStack Query stack; monorepo direction. Exploratory; no near-term deadline. ^pc-42
- [ ] **Seed SESSION-STATE.md for 03-omni, 15-DavinciRemake.** (12-MCS has one since 2026-09-04.) Pre-seed deferred — create on demand when each project is next active. ^pc-43
- [ ] **Add `design-system-ops` to the semantic-overlap reconciliation.** (Deferred 2026-10-14: no progress since 2026-06-04.) Resurface when the next skill description-contract / overlap pass runs, or when a `design-system-ops` command collides with `/ds`. Detail → [project-context-detail.md#pc-22](project-context-detail.md#pc-22). ^pc-22
- [ ] **Document the now-complete six-hub operation-grammar surface.** (Deferred 2026-10-14: no progress since 2026-06-04.) Resurface on the next real `/qa audit` of a Storybook (the planned test-drive) or the next change to hub routing. Detail → [project-context-detail.md#pc-23](project-context-detail.md#pc-23). ^pc-23
- [ ] **Act on Opus 4.7+ skill audit findings.** (Deferred 2026-10-14: no progress since the 2026-04-21 report.) Resurface on the next skill-network audit, or when `ds-advisor` and `design-engineer` collide on a trigger. Detail → [project-context-detail.md#pc-25](project-context-detail.md#pc-25). ^pc-25
- [ ] **Add framework-layer pointers to key skills.** (Deferred 2026-10-14.) The six highest-leverage skills (`workspace-bootstrap`, `ds-advisor`, `design-engineer`, `figma-canvas-designer`, `variable-icon-font-architect`, `lead-art-director`) should reference the relevant frameworks on demand. Pattern documented in the audit report. Resurface with ^pc-25 (bundle with the audit-findings session). ^pc-26

### Recently resolved (prune at next /optimize)

Moved out of Active on 2026-09-02 (^pc-45, ^pc-24 on 2026-09-25, ^pc-16 on 2026-10-14). Anchors stay. Do not delete. Pruning: an item leaves this list only when its Linear issue is closed and its text survives in [project-context-detail.md](project-context-detail.md) under its anchor (^pc-04 pruned 2026-10-14; `personal:SEA-11` closed). ^pc-13 and ^pc-24 stay until `personal:SEA-15` and `personal:SEA-22` close.

- [x] **Review + merge the 4 centric-ui Radix color-system PRs (#64–67).** SUPERSEDED 2026-06-22 — the radix work re-landed on `main` through the merged consolidate PRs #82–#84 (see `07-projects/09-figma-repo-sync-plugin/SESSION-STATE.md`), so `feat/radix-color-system` is dead. Original: based off the dev branch `feat/figma-repo-sync-plugin`; merge order #64 tokens → #65 components → #67 harness; #66 generator independent. ^pc-16
- [x] **Seed `07-projects/04-claude-figma-plugin/SESSION-STATE.md`.** DONE 2026-09-25 (/optimize) — baton seeded, project marked dormant. Remaining seeds (03-omni, 15-DavinciRemake) stay deferred under ^pc-43. ^pc-24
- [x] **Zero-Vector harness v1.1 wave 0.** DONE 2026-09-24 — all wave 0 gates closed (G5c `5b37fc3`). Leftover: Personal MBP Claude overlay moved to wave 1 (D4). Detail → [project-context-detail.md#pc-45](project-context-detail.md#pc-45). ^pc-45
- [x] **Paste the workspace beacon: Cursor User Rules + Perplexity Space (Work MBP).** Cursor User Rules BEACON pasted 2026-07-30 (Composer / Cursor / Work MBP) + `workspace-doctor --ack-chat`. Perplexity Space remainder folded into ^pc-03 (2026-10-14). Added 2026-07-06; split 2026-07-09. ^pc-13

---

---

## Active Projects

_Narratives live in [project-registry.md](project-registry.md) (load on demand)._
_For live focus, prefer the active project's `SESSION-STATE.md` **Live handoff**._

- **Switchyard (2026-10-14, new):** Mac + Windows credential router: the right login per project for git, `gh`, SSH, CLIs and agent MCP, with tray health alerts. Planning only; plan set in `07-projects/26-switchyard/plan/`. Vaultwarden on Unraid replaces 1Password. Next: Sean's review and three open questions, then Phase 0 spikes. Live state → [26-switchyard handoff](../07-projects/26-switchyard/SESSION-STATE.md).

- **Fontface (2026-10-14):** clean-room Mac font manager replacing Typeface. Phase 1, the scan fixes from the first user test, library views + Google Fonts, settings and title bar, tags, Purchases, preview profiles and Google icon fonts are all merged; `main` = `826c574`, public at `snds/fontface`. Next: Sean's on-screen check of the build (title bar, settings, tags, sync, previews, Purchases). Live state → [25-fontface handoff](../07-projects/25-fontface/SESSION-STATE.md).

- **Mailbird, working name (2026-10-14):** open-source, ad-free PIM super app (mail, calendar, contacts, notes; mobile-first, web + Tauri shells). Code `snds/Mailbird`; PRs #1–#13 merged, Phase 9 ("connected calendar") in review as PR #14 — merge only on Sean's word. Open: the name collides with Mailbird, Inc. (ADR-0006). Live state → [24-mailbird handoff](../07-projects/24-mailbird/SESSION-STATE.md).

- **Emphasis Engine (2026-10-08, knowledge-only here):** perceptual color-system generator (theme + neutral + chart seed → full light/dark UI and data-viz palette, every swatch traced to a contrast target). Code `snds/emphasis-engine` (`~/Projects/emphasis-engine`); no vault project folder. What it taught: [[ds-native-theming-survey]]. Last session: 2026-10-08 block in `06-context/session-log.md`.

- **PlanetCompiler / independent planet experiment (2026-09-28, Personal MBP, Codex):** native phase 6 (planetary scale) in `~/Projects/PlanetCompiler`: a complete Earth-radius cube-sphere test globe with authored reference details, resident patch reuse, and measured flight routes (~119.8 render callbacks/s — not GPU presentation FPS). Current-camera step queries are integrated and tested; next is immutable starting/retirement continuity queries before changing the native staged camera-position gate. Independent visual acceptance, collision, caching and streaming stay open. The phase-6 work is uncommitted with no remote (^pc-52). Living roadmap: `PlanetCompiler/docs/ROADMAP.md`. Preserve Legion. Live state → [independent planet handoff](../07-projects/13-legion/docs/planet-lab-independent/SESSION-STATE.md).
