# Workspace Audit Log

_Authoritative record of `/optimize` runs against the brain._
_Newest entry first. Append-only._
_The dispatcher reads the most recent date from this file to decide whether to surface a "stale audit" notice (threshold: 14 days)._

---

## Entry format

```markdown
## YYYY-MM-DD — {Machine label}

**Scope:** {what was reviewed — e.g., "full" or "frameworks + skills only"}
**Findings:** {N total — P0: {n}, P1: {n}, P2: {n}}

**P0 (workflow-breaking):**
- {one-liner per issue}

**P1 (friction):**
- {one-liner per issue}

**P2 (polish):**
- {one-liner per issue}

**Fixes applied this run:**
- {what was actually changed; omit if nothing was applied}

**Carried forward:**
- {issues left for a later session}
```

---

## Entries

## 2026-10-14 — Work MacBook Pro

**Scope:** full seven-surface ECC. `workspace-harness.py` (44 quality gates, 12 connection checks, token budgets), `ds-source-watch --check`, then three parallel read-only judgment passes (contract/frameworks/MOCs · context/pending/handoffs · skills/hooks/routing). `audit_skip` honored. Employer folders not read. Same session also shipped two requested doctor fixes (below).
**Findings:** 53 total — P0: 4, P1: 22, P2: 27

**P0 (workflow-breaking):**
- `legion-project` trigger `the game` (article + noun) loaded Legion on "the game starts at 7, block my calendar".
- Curated route `what should i use for` (all filler words) sent "…for the hero image background" to model routing.
- `ux-research-synthesis` trigger `who is this for` (all filler words; found by the new lint).
- `19-workspace-brain` baton says the mechanization review has "Nothing applied yet", but 18 commits sit unmerged: `worktree-b-fixes-b1-b10` (16; now conflicts with main in `validate-evidence-grades.py` + `user-preferences.md`, since main redid two fixes as `aa8d6e1`/`6f69724`) and `claude/kind-diffie-41820e` (2, M25 writes lane; merges clean).

**P1 (friction):**
- Route `centric` matches "user-centric" and injects Centric PLM context + 2 employer knowledge files.
- Routes `warning` / `invalid` / `legible` load 4 colour/a11y skills on "I got a warning from npm install".
- Route `follow up` carries a CDS-specific squash note on "follow up with Dana by email".
- Science/imaging triggers fire on everyday words: basis, projection, rotation, mvp, transform, integration, constraint, dynamics, light, lens, orb.
- Six docs (incl. `00-bootstrap/templates/project-readme.md`, `new-project` SKILL) tell agents to edit dispatcher `TRIGGER_WORDS`/`KNOWLEDGE_HINTS`, which no longer exist.
- Four different session-start read orders (AGENTS, CLAUDE, fw08, brain.mdc/CURSOR); CRITICAL_FACTS "read FIRST" lives only in CLAUDE.md.
- `CLAUDE.md:39` and `CRITICAL_FACTS.md:7` claim auto-loading no hook performs.
- `AGENTS.md` sits exactly at its 26,525-byte ceiling with duplicated blocks (write-quality gates ≈ fw08; "adapters are thin" ×4; loadset rule ×3): any addition fails the harness.
- `user-preferences.md:34` "primary content in artifact windows" contradicts the externalize / vendor-artifact rule.
- `fw08:166-169` and `_CONTEXT.md:39` say append to session-log; the contract says write a fragment.
- `SURFACES.md` still says Filesystem MCP (now workspace-mcp, H21); no Codex row; `llms.txt` omits Codex.
- `AGENTS.md` project contract omits SESSION-STATE.md (the handoff protocol reads it first).
- `memory/feedback-credential-scoping.md` + `MEMORY.md:20` still describe manual gh account switching (superseded by the 10-13 gh_route).
- `^pc-50` / `^pc-09` predate the 10-13 gh route and today's v6 install (close after one Centric push from Claude).
- `19-workspace-brain` Live handoff stale since 09-24; focus still names an employer PR.
- `24-mailbird` and Emphasis Engine missing from project-context Active Projects and project-registry.
- PlanetCompiler (13-legion planet-lab) phase-6 work uncommitted 2+ weeks, no remote; blocker is Sean-side `profile_resolve.py owners set PlanetCompiler personal` (Personal MBP).
- `04-claude-figma-plugin` and `13-legion` batons untracked (no `.gitignore` allow-entry): machine-local only.
- `^pc-16` superseded (radix re-landed via #82–84); `^pc-17` next step done (#121); `^pc-03` detail still names Windows + Cursor paste; `^pc-20` path `08-tools` → `09-tools`; `^pc-14` cache version.
- `artifact-registry.md` not updated since 09-17: gh_route, pr-desk, git_lanes, wall_guard, closure, workspace_mcp, backup-projects, mechanization-review report, 24/25 project folders missing.
- `ds-source-watch` snapshot 42 days old; registry 20 sources vs snapshot 14 (needs `--fetch`).
- Session-log compaction moves employer PR links / org slugs from `session-log.md` into `session-log-archive.md`, which has its own per-file employer-substance baseline, so every such compaction trips the H25 gate (hand-cleared in `395ebdb` this morning; recurred at this session's start). Fix at the source: scrub or count the pair as one pool.

**P2 (polish):**
- Stale dates: `SURFACES.md`, `CRITICAL_FACTS.md:17` ("As of 2026-07"), `user-preferences.md:2`, `project-context.md:4` (banner still "43 items / 38 issues").
- `_FRAMEWORKS.md:40` "four-layer" lists three (carried).
- `_SKILLS.md` `LIMIT 60`; 27/47 hubs and all foundations unlinked; 15 hubs in no root MOC; `_MOC.md` orphaned yet says "start here" (carried, worse).
- `_HOME.md:8-9` adapter list omits Cursor / Perplexity / Codex (carried).
- Loadset / never-ingest rule ×3 in AGENTS.md, plus CLAUDE.md:81, llms.txt:14,54 (carried).
- `CRITICAL_FACTS.md:43` machine labels → [[CLAUDE]] (now devices.json) (carried, half fixed).
- `role-and-context.md:43` Bitbucket only; `user-preferences.md:226` MCP "not yet active" (Atlassian tools present; GitHub cpes-software) (carried).
- `team-practices-and-decisions.md` placeholders (^pc-40) (carried).
- `MEMORY.md:16`, `fact-machine-layer-installs.md:18,45` still mention Windows / loaner (carried).
- Dormant/malformed batons: 00-obsidian, 09 (no Live handoff), 14 (12 placeholders), 20, 21 (says "no commits"), 12, 18 (`_Last updated` below baton), 25 (dates, stale exec-bit lesson) (carried, grown).
- 23 stale `.dirty`/`.touched` markers in `06-context/sessions/` (fix B1 is on the unmerged branch) (carried).
- `session-log.md` blank-line run grows each compaction (fix B2 on the unmerged branch).
- `^pc-04` prunable (SEA-11 closed); `^pc-13`/`^pc-24` need Linear closes; ~29 Active items >60 days; `^pc-10` needs re-scope; `^pc-46` cites a line number; `^pc-01` stub truncated (carried, grown).
- `artifact-registry.md` dead paths (Meridian header, resolver script, Drive note) and stale sizes / "overlay v5".
- Zero-Vector checklist lives only in a claude.ai artifact DB (not durable; Cursor/Codex cannot reach it).
- `dispatcher.py:469-573` three uncalled notice functions + unused `SKILLS_REGISTRY`.
- `session-status.py:530` routing-harness notice checks the stamp exists, not `--stale` (which exits 1 today).
- `AGENTS.md:258-259` worked example drifted; `:142` `via:` values incomplete; `:126` MOC read step returns nothing outside Obsidian.
- `CURSOR.md:45` / `SURFACES.md:15` list 1 of 7 Cursor hook events.
- `_SKILLS.md` / `_HOME.md:50` Dataview over `.claude/skills` is always empty (dot-folder ignored).
- Root `README.md` links to SPEC.md / SESSION-STATE.md that live only in `18-bootstrap-generator`.
- `00-README.md` folder list incomplete; `fw05:483,518` future tense for built things; `fw02:81` dangling [[dc-motion]]; `fw08:219` says MEMORY.md is loaded.
- `_PROJECTS.md` graph index misses 6 machine-local folders; two `04-` project folders.
- `/handback` named as a command in 4 places (the wrapper is `/side-chat-handback`).
- `google-fonts-scraper` and `google-fonts-web-scraping` are two hubs for one job.
- Worktree `claude/eager-proskuriakova-63bf69` prunable (merged).
- `figma-api-router.md` merge review still pending (carried).

**Fixes applied this run:**
- Requested doctor fixes: (1) `dist/workspace-sessionstart.sh` now spawns the pinned doctor on the in-workspace path too (it returned first, so workspace sessions never healed `~/.claude/CLAUDE.md`); (2) `workspace-doctor.sh --check` splits "no stored login" / "api.github.com unreachable (sandbox network filter)" / "token refused" instead of one false "no usable snds login". Two installer self-tests added; the first fails on the old hook.
- P0 routing: `legion-project` → `[legion game, game project]`; curated `what should i use for` removed (`which model` / `pick a model` / `best model for` cover it); `ux-research-synthesis` → `who is this product for` / `who are we designing for`. Four routing cases (58/58).
- Detector: `evaluate-skill-routing.py --lint` now checks curated keys and flags filler-only / article+noun phrases in every source; `test-validators.py` plants all three shapes.
- Earlier this session (correction): `gh` "token invalid" inside Claude's sandbox is the network filter blocking api.github.com, not the keychain.
- Harness: 3 gates failed only in the sandbox (`ps` denied; xcrun cache). Outside it `nightly --self-test` 74/74 and `profile_resolve --self-test` 406/406 pass; `test-validators.py`'s one failure was the compaction overage below.
- Session-log archive: this session's compaction moved four blocks naming the employer org/repo and PR URLs; each now says "the employer DS repo" / "prototype repo" and keeps the PR number (emp-url 17→13, emp-slug 22→≤18; baseline not grown).

**Carried forward:**
- P0 baton/branches: Sean reviews and merges `worktree-b-fixes-b1-b10` (rebase over `aa8d6e1` + `6f69724`) and `claude/kind-diffie-41820e`; then re-pin.
- All P1 and P2 above (need Sean's sign-off per /optimize Step 4).
- Sean-side: re-pin + one plain doctor run to adopt the doctor fixes; `^pc-19` Figma PAT revoke (132 days); `^pc-08` SHA purge; PlanetCompiler owner declaration.
- Do not auto-enable nightly maintenance from this audit.

**Skipped (opt-out `audit_skip: true`):** `_CHEATSHEET.md`, `08-knowledge/cross-domain/workflow-patterns.md`.

**Applied later the same day (Sean: "Apply everything", keep every Windows / `Enterprise` mention):** five disjoint fix passes plus follow-ups; full harness PASS outside the sandbox (0 failing across 3 lanes).
- Routing: `centric` → `centric plm` / `centric software`; `invalid` / `warning` / `legible` → `… state` / `legible text`; `follow up` → `follow-up pr` (CDS note dropped; `plan-ahead` trigger too); science/imaging triggers qualified (`change of basis`, `rotation matrix`, `numerical integration`, `constraint solver`, `light transport`, `camera lens`, `orb features`, …; `img-photography` `lens` too); six docs repointed off dead dispatcher dicts; 82/82 routing cases; stamp current.
- Contract: AGENTS.md is the one read order (CRITICAL_FACTS first; SESSION-STATE in the project contract); CLAUDE.md / brain.mdc / CURSOR.md / fw08 point to it; false load claims fixed; duplication cut (AGENTS.md 26,525 → 24,973 bytes; claude floor 8,545 → 7,724); artifact-window rule fixed; fragment rule in fw08 + `_CONTEXT.md`; SURFACES gets workspace-mcp + a Codex row (llms.txt too); Cursor's seven hook events; `/side-chat-handback`; worked example + `via:` list fixed; Windsurf copy re-rendered. MEMORY.md stays on demand (adding it to the start read would break the 17,000 session-floor budget).
- Maps/frameworks: four-layer line; `_SKILLS.md` links every hub and foundation (no LIMIT); `_HOME` adapters + `_MOC` link; static workflow list replaces the empty Dataview; README links; 00-README / fw02 / fw05 text; `_PROJECTS` lists machine-local folders; `04-unraidTheme` → `27-unraidTheme` (+ 5 `.code-workspace` excludes).
- Skills: `google-fonts-web-scraping` merged into `google-fonts-scraper` (now a spoke of `material-symbols-project`); `figma-api-pipeline/figma-api-router.md` merged into `figma-api-router` (two claims corrected against Figma's REST docs); both archived with Step 4a notes.
- Tools: employer-substance baseline pools `session-log.md` + `session-log-archive.md` (compaction can no longer trip H25), baseline lowered (emp-url 52 → 46, emp-slug 60 → 55); session-status shows a stale routing stamp; dispatcher dead notice code archived; `ds-source-watch` re-fetched (a failed fetch no longer erases the last good hash; two source URLs fixed); merged worktree pruned.
- Context: 19-workspace-brain Live handoff rewritten (two unmerged branches recorded; b-fixes now conflicts in 7 files); Zero-Vector checklist exported to `19-workspace-brain/notes/`; credential memory follows gh_route; ^pc-50 / ^pc-09 / ^pc-16 / ^pc-17 / ^pc-01 / ^pc-02 / ^pc-10 / ^pc-46 updated, ^pc-22/23/25/26 deferred, ^pc-04 pruned (SEA-11 closed); new ^pc-51 (merge the branches), ^pc-52 (save PlanetCompiler), ^pc-53 (Enterprise machine layer); Mailbird, Emphasis Engine, Fontface lines; artifact registry refreshed; batons for 00, 09, 12, 14, 18, 20, 21, 25 fixed; 04 and 13 batons now tracked.
- Enterprise: Sean confirmed it is his personal Windows desktop and back in use. "Retired" notes in `fact-machine-layer-installs`, `role-and-context`, `open-engine/README`, `workspace-infrastructure`, `project-context-detail` and CLAUDE.md's "macOS-only fleet" now say so.
- Still open: team-practices placeholders (need Sean's answers, ^pc-40); merging the two branches (^pc-51); stale session markers and the session-log blank run (fixed on that branch); DSDS 0.20 → 0.22 migration decision (breaking upstream release found by the re-fetch).

---

## 2026-09-25 — Work MacBook Pro

**Scope:** full seven-surface ECC. Nine deterministic probes, then three parallel judgment passes (contract/frameworks/MOCs · context/pending/handoffs · skills/hooks/harness). `audit_skip` honored. Employer folders not read.
**Findings:** 25 total — P0: 2, P1: 10, P2: 13

**P0 (workflow-breaking):**
- Routing hook treated subagent hand-back (`agent-message`) turns as user turns and injected ~20 unrelated routes (X2 regression; `daa0e94` only covered `<task-notification>`).
- `^pc-19` Figma PAT still unrevoked, 113 days, in a public repo. Sean-side.

**P1 (friction):**
- `session-status.py` shows "(no state info)" for `18-bootstrap-generator`: history regex rejects `### YYYY-MM-DD HH:MM —`, fallback wants `**Current focus**:` (file has `**Current focus:**`). File also has two `_Last updated` lines.
- `project-context.md`: `^pc-45` resolved (G5c `5b37fc3`); `^pc-47` done except the branch-ruleset offer; `^pc-48` X2 half fixed (`daa0e94` + this run), resume-nag half unverified.
- `framework-check` SKILL says "eleven frameworks"; lenses #12–#18 never run.
- `OBSIDIAN-SETUP.md:45` tells agents to read `skills.registry.json` (contract says never ingest; use `skill-loadset.py`).
- `team-practices-and-decisions.md`: says "seventeen frameworks"; ~18 unfilled template placeholders (gate 1).
- `_SKILLS.md` / `_HOME.md` say 292 skills (309); `_SKILLS.md:62` cites a nonexistent "skills sync / hash registry".
- `03-skills/` root clutter: 4 symlink-as-text + 2 empty files (`obsidian-*`, `defuddle`, `json-canvas`, `find-skills`); `figma-api-pipeline/` = 7 stale duplicate copies (3 byte-identical to the resolved 2026-04-27 batch); `test-results/`.
- Trigger overlap: "design system" loads ds-advisor + design-engineer + design-system-ops + ds; generic `audit` route fires beside every audit skill; `system health` vs `vault health`.
- `role-and-context.md:46` still lists the retired Windows desktop; `13-legion` baton has no Live handoff / pointer to `planet-lab-independent` sub-handoff; `^pc-24` 04-claude-figma-plugin still has no SESSION-STATE and lists 12-MCS as deferred.
- `_archive/ARCHIVE-LOG.md` row for missing `figma-plugin-patterns 2.md`; `03-skills/_archive/` (10 files) sits outside the provenance check.

**P2 (polish):**
- Stale `_Last updated`: `OBSIDIAN-SETUP.md`, `SURFACES.md`, `team-practices-and-decisions.md`.
- `_FRAMEWORKS.md:40` "four-layer" lists three.
- `_SKILLS.md` omits ~15 hubs; Dataview capped at `LIMIT 60`.
- `_HOME.md:8-9` adapter list omits CURSOR / PERPLEXITY / Codex (link [[SURFACES]] instead).
- `AGENTS.md` repeats the skill-loadset / never-ingest rule three times (auto-loaded cost).
- `dispatcher.py:115-140` dead, drifted `KNOWLEDGE_HINTS` dict.
- `MEMORY.md:16` + `fact-machine-layer-installs.md` still mention Windows / loaner.
- `CRITICAL_FACTS.md:38` points machine labels at `[[CLAUDE]]` (now `devices.json`); employer orgs list only `c8/*`.
- `role-and-context.md:43` / `user-preferences.md:206` say Bitbucket + MCP "not yet active".
- `00-obsidian` baton dormant since 2026-04-25; `19-workspace-brain` focus line still names an employer PR.
- Stale `.dirty`/`.touched` markers in `06-context/sessions/` (oldest Jul 30) — check the new closure sweeper clears them.
- `ds-source-watch`: registry 20 sources vs snapshot 14 (23d old).
- `^pc-04`/`^pc-13` in Recently resolved since 09-02; ~12 pre-July Active items with no progress.

**Fixes applied this run:**
- P0 routing: `surfaces.json` claude-code `non_user_envelopes` + `prompt_route.py` fallback now include the subagent hand-back frame; new fixture `claude-code.agent-message.json` + X2b self-test (37/37).
- `vault-health.py` counts inbound links from `00-bootstrap/` (canonical docs live there); `SURFACES.md` now wikilinks [[trigger-routes-digest]]. Orphan warning cleared.
- All P1 (Sean: "All p1"), second commit:
  - `session-status.py` parses `### DATE HH:MM —` headings and `**Current focus:**`; self-test 82 checks. 18-bootstrap baton's stale second `_Last updated` folded into history.
  - `project-context.md`: ^pc-45 and ^pc-24 → Recently resolved; ^pc-47 cut to the branch-ruleset step, ^pc-48 cut to the resume-nag half; full text moved to `project-context-detail.md#pc-45/#pc-47`; 12-MCS dropped from ^pc-24/^pc-43.
  - `framework-check` covers all eighteen frameworks (#12–#18 as situational lenses); wrappers regenerated.
  - `OBSIDIAN-SETUP.md` → `skill-loadset.py`; `_SKILLS.md`/`_HOME.md` drift-proof skill count + real "adding a skill" step.
  - `team-practices-and-decisions.md`: frontmatter `status: draft`, scaffold callout, eighteen; framework #05 qualifier. Placeholders remain for Sean to fill (^pc-40).
  - Archived 22 files (03-skills root dead links/empties, `figma-api-pipeline/` 6 of 7, `test-results/`, `03-skills/_archive/` → `_archive/03-skills-archive/`); ARCHIVE-LOG rows + `figma-plugin-patterns 2.md` removal note (`cec76a8`). `figma-api-router.md` kept: stale-but-useful → `_archive/2026-09-25-optimize/REVIEW-NEEDED.md`.
  - `design-system-ops` trigger `system health` → `ds health` / `design system health`; two routing cases (54/54).
  - `role-and-context.md` hardware line; Legion baton pointer + sub-handoff date and 04-claude-figma-plugin baton seeded (both local-only, gitignored).

**Carried forward:**
- All P2 above (need Sean's sign-off per /optimize Step 4).
- Curated routes are never suppressed by a longer match (tested design), so "design system ops" still also loads the `design system` gate. Change only by Sean's decision.
- `figma-api-router.md` merge review (REVIEW-NEEDED).
- Hygiene with Sean: REVOKE Figma PAT (`^pc-19`); `^pc-08` SHA purge.
- Do not auto-enable nightly maintenance from this audit.

**Skipped (opt-out `audit_skip: true`):** `_CHEATSHEET.md`, `08-knowledge/cross-domain/workflow-patterns.md`.

---

## 2026-09-02 — Personal MacBook Pro

**Scope:** full seven-surface ECC. Foundation reads + `audit_skip` honored. Judgment on top of probes.
**Findings:** 9 total — P0: 1, P1: 4, P2: 4

**P0 (workflow-breaking):**
- `display-graphic-motion-systems.md` `relations:` mixed YAML packs / a skill into the epistemic graph (`dc-motion`, `dc-illustration`, `visual-reference-replication`). `vault-health` exit 1.

**P1 (friction):**
- `project-context.md` had `[x]` `^pc-04` / `^pc-13` still in Active and no Recently resolved section.
- `project-context.md` still ~36 open Active `^pc-NN` stubs; engine migration deferred. Do not delete anchors.
- Dormant `SESSION-STATE.md` batons past 30 days: `00-obsidian`, `18-bootstrap-generator`, plus seeded/idle `02-centricPLM` / `10-centric-UX-research` / `14-variable-icon-font-generator` / `16-CDS` / `09-figma-repo-sync-plugin`. Left in place.
- `^pc-19` Figma PAT revoke still open (~90 days). Sean-side hygiene; no vault edit.

**P2 (polish):**
- `_HOME.md` anatomy still said "eleven operating frameworks."
- `team-practices-and-decisions.md` still said "the five frameworks."
- `_SKILLS.md` curated hubs omitted the new motion/display spokes; count said 280+.
- `ds-source-watch --check`: snapshot 0d old; registry 18 vs snapshot 14. Left (fetch is the other skill).

**Fixes applied this run:**
- Retargeted `display-graphic-motion-systems.md` `relations:` to `[[domain-constitutions]]` + `[[visual-reference-replication-findings]]` (YAML/skill names stay in `related_skills` and body).
- Moved `^pc-04` and `^pc-13` into a Recently resolved section. Anchors kept.
- `_HOME.md`: sixteen frameworks in anatomy; skill count 292.
- `team-practices-and-decisions.md`: "sixteen frameworks" in the lede and integration heading.
- `_SKILLS.md`: 292 count + Motion / display graphics cluster.

**Carried forward:**
- 36 open Active + 5 Deferred `^pc-NN` stubs; do not delete anchors. Engine migration still deferred.
- Dormant seeded `SESSION-STATE.md` batons (left in place).
- Hygiene still with Sean: REVOKE Figma PAT (`^pc-19`); GitHub Support purge of two personal-email SHAs (`^pc-08`).
- `ds-source-watch` 18-vs-14 source gap (fetch when Sean asks).
- Doctor-sweep generalization for `* 2.md` conflict-copies (none present this run; recipe still open).
- Do not auto-enable nightly maintenance from this audit.

**Skipped (opt-out `audit_skip: true`):** `_CHEATSHEET.md`, `08-knowledge/cross-domain/workflow-patterns.md` (the skill documents the flag; the two files carry it).

---

## 2026-08-28 — Personal MacBook Pro

**Scope:** full seven-surface ECC after landing perception-critique-stack course corrections 1–12 (prove engine vqa/1.1 + play-prove). Foundation reads sampled; `audit_skip` honored.
**Findings:** 7 total — P0: 0, P1: 4, P2: 3

**P0 (workflow-breaking):**
- none. Probes green: `validate-links`, `build-registry --check`, `validate-workspace`, `vault-health`, `build-trigger-routes --check`, `test-validators.py` 10/10, write-quality chain, `validate-capabilities` 20/29, `vqa calibrate` 48/48.

**P1 (friction):**
- Open Engine personal lane `not-registered` on Voyager-2.local (session-start notice). Run `python3 00-bootstrap/doctor/linear-lanes.py` or register MCP.
- Uncompacted session fragment `06-context/sessions/2026-08-26-voyager-b7191a1.md` (Looney Tunes / MediaSentinel). Compaction is `/session-end`, not this pass.
- Dormant `SESSION-STATE.md` batons past 30 days: `00-obsidian` (2026-04-25), `18-bootstrap-generator` (2026-07-27). Not active work; left in place.
- `project-context.md` still ~41 anchored `^pc-NN` items; `_Last updated` 2026-07-30. Do not delete anchors. Engine migration of this list remains deferred.

**P2 (polish):**
- `/optimize` Step 1 still described a five-file framework core (fixed this run).
- `01-frameworks/00-README.md` token-budget line still said "twelve frameworks" after the set grew to sixteen (fixed this run).
- `CLAUDE.md` said "Eleven" frameworks while listing 01–13 and omitting 14–16 (fixed this run).

**Fixes applied this run:**
- Prove engine `vqa/1.1`: cue altitudes, FLIP, saliency, OCR, mesh, geometry, DreamSim degrade, interact critic, tracks, input-to-photon, VLM-judge protocol, capture `renderer` warning, uncued residuals.
- New sibling skill `play-prove` (altitude G).
- LCARS `S-SYS47-01.cuespec.json`: `default_altitude: A` + four named `uncued_residuals`.
- Capability registry: nvidia-flip, dreamsim, gltf-validator, tesseract, geometric-foundation-model.
- Framework #06 altitude paragraph; trigger routes; CI path includes `play-prove`.
- Corrected sixteen-vs-twelve in `00-README.md` and optimize skill read-list; `CLAUDE.md` "Eleven" → Sixteen and added #14–#16 pointers.
- Rewrote Live handoff on `19-workspace-brain` and `20-lcars-generative-interface`.

**Carried forward:**
- Open Engine personal-lane registration on this machine.
- Compact `2026-08-26-voyager-b7191a1` at next `/session-end`.
- Doctor-sweep generalization for `* 2.md` conflict-copies (open since 2026-07-08).
- Hygiene still with Sean: REVOKE Figma PAT; GitHub Support purge of two personal-email SHAs.
- Do not auto-enable nightly maintenance from this audit.

**Skipped (opt-out `audit_skip: true`):** `_CHEATSHEET.md`, `08-knowledge/cross-domain/workflow-patterns.md` (the skill documents the flag; the two files carry it).

---

## 2026-07-23 — Personal MacBook Pro

**Scope:** full (CLAUDE.md/AGENTS.md frameworks, MOCs, project-context, session-log head, `08-knowledge/_INDEX`, `workflow-patterns`, settings/hooks, filesystem drift sweeps)
**Findings:** 7 total — P0: 0, P1: 2, P2: 5

**P0 (workflow-breaking):**
- none — machinery clean: hooks/settings/launchd/beacons healthy (doctor confirmed), no tracked `.DS_Store`/`desktop.ini`, no fossils.

**P1 (friction):**
- `18-bootstrap-generator` (primary focus of the last ~week, ~26 commits) had a `SESSION-STATE.md` but no entry in project-context "Active Projects".
- `16-CDS Figma-Code Audit` likewise had a `SESSION-STATE.md` but no project-context entry.

**P2 (polish):**
- `project-context.md` `_Last updated:` stale (2026-07-15 vs real 07-23).
- Resolved-item clutter: 22 crossed-off `[x]` items across the Active + Recently-resolved buckets (three-bucket model says prune at /optimize).
- `08-knowledge/research/research/` double-nesting (carry-forward item (f), unresolved since 2026-07-08).
- `_archive/figma-plugin-patterns 2.md` — stale conflict-copy (strict older subset of `engineering/figma-plugin-patterns.md`).
- Aging open hygiene items surfaced (not drift): REVOKE Figma PAT (2026-06-04); purge two centric-ui SHAs with personal email (2026-07-20).

**Fixes applied this run:**
- Added "Portable Bootstrap Generator (`wsx`)" + "CDS Figma–Code Audit" blocks to project-context Active Projects (P1 1,2).
- Bumped `_Last updated:` → 2026-07-23 (P2 3).
- Pruned 22 resolved `[x]` pending-items → archived to `session-log-archive.md` under "Pruned resolved pending-items — 2026-07-23"; live Active bucket now 36 next-actions (P2 4).
- Flattened `research/research/` → `research/` (git mv 6 files); updated `_INDEX.md` reference; Obsidian `[[wikilinks]]` unaffected (basename-resolved) (P2 5).
- Removed the stale `_archive/figma-plugin-patterns 2.md` after diff-confirming it's a strict subset (P2 6).
- Updated the 2026-07-08 carry-forward item (e)/(f) to reflect the above.

**Carried forward:**
- Doctor-sweep generalization for `* 2.md` conflict-copies (item (e)) — one instance cleaned, the generalized sweep still open.
- Hygiene item #7 left for Sean (external services): REVOKE the Figma PAT; GitHub Support request to purge the two personal-email SHAs.

## 2026-07-09 — Structured validation session (six phases, adversarial pass)

- Scope: hooks/boot, triggers, context profiles, audience/medium playbooks, Proofboard, path efficiency.
- Verdicts: boot FAIL · triggers FAIL · resolution PASS · audience PARTIAL · medium PARTIAL · Proofboard PASS · path PARTIAL.
- Headline defects (live): parent-dir launch = silent context loss (fix built in 00-bootstrap/dist, uninstalled);
  trigger layer floods 15-line cap, knowledge hints truncated; ritual "Last session" month-stale (SESSION BLOCK
  unparsed); #06 has no audit-class trigger carrier; HEAD moved mid-session unnoticed (reconcile 066edac).
- Report: 05-artifacts/active/workspace_validation-report_v1.0_2026-07-09.md (fix list FX-1..FX-14, proposed only).
- Approved during session: Proofboard standard amendments (illustrate-don't-narrate · two-read rule · fit-check step) — pending codification (FX-9).
- Artifacts: session-lifecycle flow SVG v1.0 · artifact-name-checker v1.0+v1.1 (proofboard) · this report · version register.

**Per-FX outcomes (fix session, same day — Personal MacBook Pro, sign-off prompt `workspace_fix-session-prompt_v1.0_2026-07-09.md`):**
- FX-1 ✅ `3729472` — v2 machine layer installed (doctor); Drive-era shims retired; brain-path fixed; install-state memory fact. Live parent-dir test deferred (stale OAuth, 401) — offline handler runs green; audit-log canary verifies next real session.
- FX-2 ✅ `faa2ce9` — tiered emit (curated → knowledge → registry → index), per-tier caps 8/4/6/4, dedupe by target; knowledge hints survive (evidence in commit).
- FX-3 ✅ `faa2ce9` (dispatcher half) + `c3f4ab7` (sources) — `validation`→`field validation`/`validation state`; 10 bare-word triggers narrowed; registry regenerated clean.
- FX-4 ✅ `faa2ce9` + `3f83842` — audit/review/critique/qa pass/refine → framework #06, mandate rows emit first; mirror tables carry the row.
- FX-5 ✅ `faa2ce9` + `cf1f001` — parser reads `--- SESSION BLOCK ---` (Date/Project(s)); /session-end writes `###` headings (belt+braces). Parser tests pass incl. real log → 2026-07-09.
- FX-6 ✅ `3f83842` — `the game`/`PLM`/`variable axis`/`plugin dev` declared at owning skills; tables reconciled; single-source rule added; 4/4 routing PASS.
- FX-7 ✅ (this commit) — `Context profile:` populated in all 8 SESSION-STATEs (+ 19-workspace-brain). 14-variable-icon-font-generator is PROVISIONAL `centric-engineering` (fail-safe most-restrictive) — Sean to confirm. Note: 6 of 8 files are gitignored (machine-local by design).
- FX-8 ✅ `537effa` — AGENTS.md read order gains `_INDEX.md` + delivery-playbooks load order. Tool-neutral `trigger-routes.md` extraction DEFERRED (authority just consolidated in dispatcher; pending item).
- FX-9 ✅ `537effa` — three Sean-approved Proofboard amendments codified verbatim (two-read rule placed under Trust mechanisms; no "Quality bar" section exists).
- FX-10 ✅ `537effa` — three ontology routing rows (machine-local config · hook/adapter code · bootstrap logic).
- FX-11 ✅ (this commit) — workspace-infrastructure refreshed (post-rebuild event list + machine layer; Drive-era clone procedure quarantined HISTORICAL); hooks-contract triggers broadened (`userpromptsubmit`, `hook didn't fire`, `claude hooks`, `hook dispatcher` — bare `hooks` NOT added, would collide with React hooks; deviation per FX-3 principle); workflow-patterns gains "Re-verify HEAD at phase boundaries" + "Version register at >2 artifacts".
- FX-12 ✅ `faa2ce9` — `validation report`/`full report` → 04-documents-and-specs; verified on the P1-11 failing phrase.
- FX-13 ✅ `537effa` — project-home rule in framework #08; standing `07-projects/19-workspace-brain/` scaffolded, tracked, registered, routed.
- FX-14 ◐ Phase F — home-dir spine relocation proposed to Sean (confirm target repo); dist shim hardcoded-path fix; Work MBP/Windows installs + harness re-run added as pending items.
- FX-15 (new, guardrail 5) — pre-beacon `~/.claude/CLAUDE.md` global standards (12.6KB) backed up at `~/.claude/_retired/CLAUDE.pre-beacon-2026-07-09.md`; content not yet externalized to the workspace — pending item.

## 2026-07-08 — Work MacBook Pro (main, going forward)

**Scope:** focused — trigger/dispatch layer, foundational color/UX/a11y routing, self-healing infrastructure. Prompted by the cell-validation failure (full-chroma status backgrounds authored without the foundational color/a11y baseline). Full analysis in-session; three Explore-agent sweeps covered 01-frameworks + 02-shared-references + 04-preferences, all 246 skills, and 08-knowledge + hooks + tools.
**Findings:** 14 — P0: 4 · P1: 6 · P2: 4

**P0 (workflow-breaking):**
- `emit_context` emitted `hookEventName: null` — harness validation silently dropped ALL dispatcher context injections (SessionStart context + trigger hints). The whole deterministic context layer was dark.
- Dispatcher trigger tables hand-maintained and frozen (~April/May): registry `triggers:` (50 skills) and `_INDEX.md` trigger lists never consulted; the failing prompt matched ZERO triggers (replayed empirically).
- No `triggers:` frontmatter on ANY applied design/a11y skill (ds-advisor, design-engineer, a11y-visual, uid-color-for-ui, …) — the AGENTS.md precedence algorithm's primary key was empty for the entire design domain.
- No enforcement at the point of risk: `use_figma` writes had no design-judgment gate; frameworks/knowledge purely advisory and skippable under execution momentum.

**P1 (friction):**
- Foundational color/UX/a11y baseline exists (design-foundations → found-color → a11y-visual → uid-color-for-ui, with governs/governed_by edges) but nothing routed to it; system-specific rules ([[radix-derived-color-system]]) were the only color content surfacing.
- "Work within the target system; backlog its gaps" existed in ds-advisor (Known Gaps/DDR) but at no framework tier and at no enforcement point.
- Framework #06 pre-output gate had no accessibility check; #06 triggers only on QA-signal words, missing authoring tasks.
- Registry regeneration only enforced in GitHub CI — local auto-commit could push a stale registry.
- `08-knowledge/_INDEX.md` had no validator: 5 research entries unindexed; `figma-plugin-patterns 2.md` Drive-conflict duplicate untracked; `updated:` stale.
- Stale docs claiming dead behavior: skills-manifest.json "single source of truth", `handle_user_prompt_submit()`, "KNOWLEDGE_HINTS mirrors TRIGGER_WORDS", `08-tools/`, CLAUDE.md "SessionStart loads the skill registry".

**P2 (polish):**
- APCA body-text floor inconsistent (a11y-visual Lc 60 vs design-engineer Lc 75 vs radix entry Lc 90); CVD prevalence numbers drift across 4 skills.
- `infod-encoding-theory` re-derived OKLCH/CVD without `found-color` prerequisite.
- `sec-supply-chain` trigger `token` over-broad (collided with design-token vocabulary).
- artifact-registry line-number tables mirror gitignored files (unvalidatable).

**Fixes applied this run:**
- dispatcher.py: correct `hookEventName` per event (restores context delivery); runtime trigger matching from `skills.registry.json` + `_INDEX.md` `Triggers:` lines (word-boundary, deduped, capped); foundational vocabulary (validation/warning/status color/contrast/a11y/…) → foundations-first route; compact/resume re-orientation injection; stale-audit escalation tier (>2× threshold); once-per-session `use_figma` PreToolUse design-judgment gate (registered in settings.json); session-end registry regeneration when SKILL.md changed.
- `triggers:` declared on ds-advisor, design-engineer, figma-canvas-designer, visual-qa-toolkit, a11y-visual, uid-color-for-ui; `sec-supply-chain` `token`→`access token`; `infod-encoding-theory` +`found-color` prereq; registry regenerated (246 skills, --check green).
- Framework #06: sixth operating default "System-context fidelity" (foundations independent of any DS; resolve within the target system; token gaps → backlog, a11y never deferred) + Accessibility check added to the pre-output gate; ds-agents-binding.md mirrors the rule; CLAUDE.md routing/lifecycle text corrected.
- validate-workspace.py: KNOWLEDGE COVERAGE check added; _INDEX.md research section indexed + dated; conflict duplicate archived with ARCHIVE-LOG provenance. All validators green.

**Carried forward:**
- See the consolidated 2026-07-08 pending item in project-context.md: APCA canon reconciliation (needs sign-off), remaining a11y-skill triggers (deliberately deferred), CVD prevalence alignment, artifact-registry line tables, doctor conflict-copy sweep, research/ double-nesting.

## 2026-04-27 — Windows Desktop

## 2026-06-30 — Personal MacBook Pro

**Scope:** full (frameworks · MOCs · context · `.claude` skills · bootstrap · settings; stable docs grep-checked). Run immediately after the #10 Perception Integrity framework migration.
**Findings:** 9 — P0: 1 · P1: 4 · P2: 4
**Skipped (opt-out `audit_skip: true`):** `_CHEATSHEET.md`, `08-knowledge/cross-domain/workflow-patterns.md`, `.claude/skills/optimize/SKILL.md` (note: carries stale "5 framework files" read-list text), `06-context/session-log.md`.

**P0 (workflow-breaking):**
- `validate-workspace.py` RED — `decision-commercial-data-licensing.md` not listed in `06-context/memory/MEMORY.md`.

**P1 (friction):**
- `visual-qa-toolkit` fully built + registered but documented as "(being built)/planned" in `_SKILLS.md` + `project-context.md` (×3).
- `/framework-check` ran only 5 of 10 frameworks post-migration (ignored #06 always-load + #10 cross-cutting).
- `CLAUDE.md` self-contradicted on `/framework-check` count ("all six" vs "the five frameworks").
- New `native-visual-eval` skill (framework #10's method) absent from `_SKILLS.md` Visual QA cluster.

**P2 (polish):**
- `new-project/SKILL.md` "default: all five" frameworks → ten.
- `_HOME.md` "60+ skill library" understated (286 SKILL.md dirs).
- Framework preamble sibling-lists — reviewed, **not drift** (deliberate cumulative convention; #10 conforms).
- `_HOME` vs `_MOC` dual front-door — reviewed, **deliberate** (daily dashboard vs structural map; already cross-linked).

**Fixes applied this run:**
- P0: added `decision-commercial-data-licensing` row to `MEMORY.md` (gate now green).
- P1: flipped `visual-qa-toolkit` → built in `_SKILLS.md` + closed pending item + updated AI-Design-Assessment project summary/next in `project-context.md`; added `native-visual-eval` + `lead-visual-qa` to `_SKILLS.md` Visual QA cluster; expanded `/framework-check` to ten (six core always + four situational gated by domain) in its SKILL.md; reconciled both `CLAUDE.md` references.
- P2: `new-project` default → all ten; `_HOME` → "280+ skill library".
- All three validators green (workspace · links · integrity).

**Carried forward:**
- `/framework-check` scope expansion (5→10) was decided autonomously (six core always-run, 07–10 situational). Flagged for Sean to confirm the gating model matches intent.
- The opt-out `optimize/SKILL.md` Step-1 read list still says "the 5 framework files (01–05)" — not editable under its own `audit_skip`, but worth a manual refresh next time that skill is touched.
**Scope:** full
**Findings:** 9 — P0: 1 · P1: 5 · P2: 3

**P0 (workflow-breaking):**
- `06-context/project-context.md` "First commit pending at end of this session" stale (commit pushed 2026-04-25 per session-log).

**P1 (friction):**
- Worktree-pinned CLAUDE.md missing `/optimize` line vs root CLAUDE.md (drift).
- 7 loose `.md` files at `03-skills/` root duplicating dir SKILL.md siblings (pending since 2026-04-21).
- `03-skills/_deprecated_workspace-bootstrap-updated_2026-04-21/` still in tree 6+ days post-rename.
- `03-skills/workspace-bootstrap/workspace-bootstrap.skill` legacy ZIP package alongside SKILL.md.
- `_CHEATSHEET.md` + `Repo.md` at workspace root unmentioned in CLAUDE.md MOC list.

**P2 (polish):**
- `project-context.md` "Long-standing items" self-flagged stale; two open verifications.
- `desktop.ini` Drive-injected files scattered across system folders (gitignore confirmed: `**/desktop.ini`).
- audit-log.md had no entries; this is the first.

**Fixes applied this run:**
- P0-1: Edited project-context.md — replaced "First commit pending..." with "first commit pushed to `main` 2026-04-25"; trimmed redundant "First commit + push" from Next line.
- P1-1: Added `/optimize` bullet to worktree-pinned CLAUDE.md slash-command list.
- P1-2: Moved 5 strict-duplicate loose files (`figma-api-router.md`, `figma-component-generation.md`, `figma-error-troubleshooting.md`, `figma-mcp-tool-usage.md`, `figma-variable-creation.md`) to `03-skills/_archive/duplicates_2026-04-27/`. Verified each is a strict subset of its dir SKILL.md before archiving.
- P1-2 (flagged for review): Left `figma-ds-generation-pipeline.md` and `figma-style-binding.md` in place — both contain content NOT present in dir SKILL.md. Flag note written at `03-skills/_archive/duplicates_2026-04-27/REVIEW-NEEDED.md` documenting unique sections and suggested actions.
- P1-3: Moved `03-skills/_deprecated_workspace-bootstrap-updated_2026-04-21/` to `03-skills/_archive/`. Confirmed against live `03-skills/workspace-bootstrap/SKILL.md` — deprecated version is the older iteration the migration audit explicitly superseded.
- P1-4: Moved `workspace-bootstrap/workspace-bootstrap.skill` (ZIP package) to `03-skills/_archive/legacy-packages/`. Live SKILL.md is the authoritative source.
- P1-5: Moved `Repo.md` (single-line URL, also captured in project-context.md and CLAUDE.md) to `_archive/`. `_CHEATSHEET.md` left in place — it's a real MOC; will surface in CLAUDE.md MOC list on a future polish pass if Sean wants.
- P2-2: Verified `.gitignore` already contains `**/desktop.ini` — no action needed.
- Bake-in: Updated `.claude/skills/optimize/SKILL.md` with new Step 4a "Stale-content review (mandatory before archiving)" — codifies read-both-files / diff-for-unique-content / classify-as-{clean-duplicate, stale-but-useful, stale-contradictory} / write REVIEW-NEEDED.md flag-note workflow. This run was the first execution of that workflow.

**Carried forward (needs Sean's review):**
- `03-skills/figma-ds-generation-pipeline.md` — has `ds-stack-router` Step 0 + explicit Radix scale binding map missing from dir SKILL.md. See REVIEW-NEEDED.md.
- `03-skills/figma-style-binding.md` — has Effect Style binding, Node Property binding, gradient binding, bindable-fields reference all missing from dir SKILL.md. See REVIEW-NEEDED.md.
- `_CHEATSHEET.md` — decide whether to add to CLAUDE.md MOC list (currently lists only 5 of the 6 root MOCs).
- Long-standing items in project-context.md (Drive MCP GDocs verification on Web/iOS; Personal MacBook DC writes) — verify or move to a "deferred" sub-bucket on next eligible session.


