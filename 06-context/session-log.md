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


---

### 2026-09-04 — ShadeGraph: research + scaffold a node-based shader design tool

SessionID: 2026-09-04-voyager-sg21a
--- SESSION BLOCK ---
Date: 2026-09-04
Machine: Personal MacBook Pro
Surface: Claude Desktop (Code tab)
Project(s): 21-shadegraph (new) · 13-legion (integration target)
Summary: Researched vgpu.sh + the Codrops "Prism with vgpu" article + industry node-based shader editors (Unreal Material Layers, Unity Shader Graph, Substance, Blender node-preview, Nuke viewer-per-node, litegraph/ComfyUI, React Flow). Traced Legion's real shader architecture (GLSL chunks + uniforms + per-archetype lab-store — already a de-facto node system). Chose the stack, scaffolded a standalone tool repo, and wrote a comprehensive design plan.
Artifacts:
  - ~/Projects/ShadeGraph/ — new standalone repo (commit 50abc6a): model/compiler/nodes/preview contracts, React app shell, Legion adapter plan
  - 07-projects/21-shadegraph/docs/DESIGN-PLAN.md — research synthesis, stack decision, data model, phased roadmap
  - 07-projects/21-shadegraph/{SESSION-STATE.md, README.md}
Decisions:
  - Stack: React + React Flow 12 (editor shell) + one shared Three/WebGPU preview renderer + pluggable compiler. Rationale: preview fidelity ⟂ node-editor framework — fidelity is owned by compiler+renderer (previews run the real target program), scale by keeping GPU work off the DOM. litegraph/canvas is the documented escape hatch.
  - Compiler targets both backends from day one: glsl-es (drives Legion now) + wgsl/tsl (WebGPU/vgpu future).
  - Home: standalone repo ~/Projects/ShadeGraph (snds/*, own git); vault 21-shadegraph holds docs/baton only (portable-first, like Legion).
  - Vault folder allowlisted in .gitignore (docs-only) so the design plan syncs cross-device.
  - **Workspace project-tracking policy clarified (Sean):** project CONTEXT (reference/guidance/intent/curated media/docs) is tracked for BOTH personal and work projects; NEVER tracked = company/app code or checked-out repos (live in their own repos: centric-ui, prototype, ~/Projects/*) and sensitive customer data (never in the workspace at all — kept with the employer repo). The gate is content-type (context vs code/repo/customer-data), not personal-vs-employer. Encoded as exclude patterns in .gitignore under "07-projects tracking policy".
Evidence:
  - ShadeGraph initial commit @ ~/Projects/ShadeGraph (git log 50abc6a, tree clean) — verified
Pending added:
  - ShadeGraph Phase 1 (graph MVP): pnpm install, wire React Flow shell to store, starter node set + inspector + JSON save/load
  - Resolve 4 open design calls (name; state lib; WGSL-via-emitters vs TSL-as-IR; Legion live-bridge vs export-only) — DESIGN-PLAN §11
Project status changes:
  - 21-shadegraph: (new) → Building (Phase 0 scaffold + design plan complete)
Migration done this session (vault content → correct homes):
  - 03-omni: relocated ~/Projects/Workspace/07-projects/03-omni → ~/Projects/omni; fresh git; new PRIVATE repo github.com/snds/omni (pushed, commit 22c3527). Vault folder now a tracked context pointer stub (allowlisted). node_modules/target excluded.
  - 13-legion/Video (455MB Homeworld 2 frame reference) → moved to ~/Desktop/Legion-Reference-Media/Video (staging). Tracked pointer added: 06-context/external-media-registry.md. Legion vault folder 462MB→6.9MB. Awaiting Sean's durable large-format storage destination.
  - 12-MCS: empty on this (personal) machine + target employer repo unreachable from snds account. Content/access live on the WORK laptop. Queued as cross-device action: playbook in 07-projects/12-MCS/SESSION-STATE.md (SESSION-STATE tracked; folder body deliberately NOT `**`-allowlisted so work-laptop customer data can't leak into the workspace repo) + pending item ^pc-44 (machine-gated, work laptop). Sean authorized PR+commit+merge to saas-plm-analysis (doc-only employer repo).
  - ShadeGraph: PUBLIC repo created + pushed → github.com/snds/shadegraph.
Next:
  - Phase 1 per DESIGN-PLAN §10 — begin graph MVP in ~/Projects/ShadeGraph
  - [WORK LAPTOP] execute ^pc-44 — MCS → saas-plm-analysis migration (see 12-MCS SESSION-STATE).
  - Remaining backfill (deferred, per-folder triage): 02-centricPLM + 11-lexical-react-native hold employer code checkouts; relocate/scrub before any tracking. Other personal folders (04,08,09,14,15) can be triaged + allowlisted for context. Update 08-knowledge/cross-domain/workspace-infrastructure.md tracking table when done.
--- END BLOCK ---


---
SessionID: claude-web-2026-09-03-model-routing
Agent: Claude Sonnet 4.6
Surface: claude.ai (web)
Machine: Voyager-2.local
Date: 2026-09-03
Branch: main
Commit: 23788ee
---

## Summary

Local LLM setup and workspace model routing infrastructure session.

## What happened

- Debugged Ollama setup on M3 Max (36GB): EOF on model pulls traced to invalid
  tag names from third-party guides (not a connectivity or disk issue); resolved
  by using `ollama run gemma4` without explicit tag suffix
- Mapped open-source model recommendations to specific work contexts (DS work,
  code, reasoning, comms, Legion creative) across the local Ollama roster
- Created `02-shared-references/model-routing.md` — new canonical shared reference
  covering Ollama, Claude, Cursor, and Codex surfaces; native-first model roster
  per surface; work context → model map; effort tiers 1–4; speed signals
- Added 13 trigger phrases to `trigger-routes.json` for model selection vocabulary
  (which model, pick a model, best model for, model routing, ollama model, local
  model, cursor model, codex model, grok or claude, effort tier, etc.)
- Regenerated `trigger-routes.md` via `build-trigger-routes.py`
- Confirmed dispatcher.py loads trigger-routes.json dynamically — no hook changes needed
- Confirmed Cursor brain.mdc already reads trigger-routes.md at session start — no rule changes needed
- All validators green (validate-links, validate-capabilities, validate-workspace)
- Committed and pushed to github.com/snds/workspace main (23788ee)

## Pending

- No new pending items from this session
- GitHub MCP not surfaced in claude.ai session despite being installed; used git
  via Desktop Commander instead — consider verifying GitHub MCP connector state

## Notes

Filesystem MCP (read/write at /Users/snds/Projects) + Desktop Commander both
available this session — used both successfully. Web surface confirmed write-capable
via Desktop Commander when workspace is on local disk.


### 2026-09-03 — Looney consolidation + dump-folder cleanup

SessionID: 2026-09-03-voyager-b7191a1
--- SESSION BLOCK ---
Date: 2026-09-03
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 01-mediaservices
Summary: Closed the Aug 26 Looney Tunes thread. Quality adjudication + consolidation put the show in one Sonarr folder (1,062 files). The Orville, Firefly, and 12 Monkeys dump twins were resolved the same way. 16 empty leftover folders were deleted. One incident: 184 intended Looney upgrades were destroyed after ffmpeg `.part` writes failed and a graveyard sweep ran anyway.
Artifacts:
  - Unraid `/mnt/user/appdata/media-sentinel/loudness/` — adjudication-report, consolidation journal/manifest, lost-upgrades.json, three-report, cleanup-journal, looney/orville profiles
  - MediaSentinel grouping/parse + tests (year-seasons, S00 specials, yearless-into-sole-year merge)
  - `07-projects/01-mediaservices/SESSION-STATE.md`
Decisions:
  - Winners go to the Sonarr-managed folder; dump/orphan folders delete only when empty of video
  - Temp ffmpeg outputs must set `-f`; destructive sweeps gate on zero errors
  - Review pair decisions before deleting losers (broken once on Orville S01, outcome still defensible)
Pending added:
  - Optional Sonarr re-grab of 184 lost Looney upgrades
  - Firefly E03/E11 Italian-only; E10 may be mislabeled (Objects in Space / War Stories)
Pending resolved:
  - User decision on Looney loudness path (dedupe-to-managed executed)
  - Duplicate dump folders for Looney, Orville, Firefly, 12 Monkeys
  - Empty leftover folder sweep
Project status changes:
  - 01-mediaservices: Aug 26 server work complete; next is `personal:SEA-34` (Desktop Pokémon → Unraid)
Next:
  - `personal:SEA-34` — copy Desktop Pokémon pack to Unraid; set TheTVDB (DVD); do not leave Horizons in 1997 Season 20
--- END BLOCK ---


### 2026-09-03 — Library CUT delete + Desktop Pokémon organize

SessionID: 2026-09-03-voyager-mslib1
--- SESSION BLOCK ---
Date: 2026-09-03
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 01-mediaservices
Summary: Closed a long MediaSentinel / Unraid library thread. Library-wide English-watchable duplicate ranking produced 2,327 CUT videos; Sean authorized live delete of those losers plus their sidecars only. Plex TV and Emby TV were scanned. Desktop ColdFusion Pokémon pack was reorganized in place to TVDB DVD seasons; it was not copied to Unraid.
Artifacts:
  - 07-projects/01-mediaservices/canvases/duplicate-scan-outcome.canvas.tsx — scan 20260816T214110-ab8d81
  - 07-projects/01-mediaservices/canvases/authoritative-delete-list.canvas.tsx — 2,327 CUT list
  - Unraid `/mnt/user/appdata/media-sentinel/exports/` — delete lists + result JSON
  - Desktop ColdFusion Pokémon pack — 1,299 videos renamed into show/season folders
  - 08-knowledge/engineering/pokemon-tvdb-dvd-vs-aired.md — DVD vs aired + production-number trap
Decisions:
  - Delete CUT extras only; keep KEEP / PRESERVE / singletons; companions of the losing video only
  - Unlink on disk (space back), not same-fs quarantine, after explicit authorization
  - Do not whisper-overwrite MST3K S6+ community `.en.srt`; copy sidecars onto tracked obfuscated files instead
  - ColdFusion `02x28`-style codes are production numbers; map Pokémon via folder context + TVDB DVD
  - Plex/Emby must use TheTVDB (DVD) for Pokémon (1997) {tvdb-76703}; default aired now maps S20 to Horizons
Evidence:
  - 2,327 videos + 5,369 sidecars unlinked; 0 listed videos remaining; 917.7 GiB @ Unraid `/mnt/user/data/media/tv` — verified
  - Plex TV section 1 refresh HTTP 200; Emby TV Recursive ValidationOnly HTTP 204 — verified
  - 1,299 Desktop Pokémon videos moved/renamed; leftover non-video only — verified
Pending added:
  - `personal:SEA-34` land organized Desktop Pokémon pack on Unraid with TVDB DVD order
Pending resolved:
  - Authoritative CUT list for run `20260816T214110-ab8d81`
  - User-authorized delete of that list + TV library scans
  - Desktop Pokémon pack season/folder organize
Project status changes:
  - 01-mediaservices: Aug 16–17 library reclaim done; Aug 26 Looney/Orville/Firefly/12 Monkeys outcome unchanged; Desktop Pokémon ready to copy
Next:
  - `personal:SEA-34` — copy Desktop Pokémon pack to Unraid and set TVDB DVD order
  - Optional leftovers stay in SESSION-STATE (Sonarr Looney upgrades, Firefly E03/E11/E10, Bazarr missing-sub keepers, MST3K S04E01 sidecar)
--- END BLOCK ---


### 2026-09-03 — LCARS pack catalog + live T3 compose

SessionID: 2026-09-03-voyager-t3ds1
--- SESSION BLOCK ---
Date: 2026-09-03
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 20-lcars-generative-interface
Summary: Built a pack catalog (primitive → variant → component → content group → layout) and recomposed the live T3 demo from composers. App landed on `main` as `e691dec` (not pushed). S-SYS47-01 Literal stays a separate switch.
Artifacts:
  - github.com/snds/LCARS `e691dec` — `src/catalog/system/` + `docs/COMPONENT-SYSTEM.md` + composed `live-t3`
  - vault `07-projects/20-lcars-generative-interface/docs/content-groups.md` — `support.controls` + variants note
Decisions:
  - Work in vectors / grammar, not per-pixel plate overlay
  - Pills are controls; spine is bars; aesthetic is barcode + hairline
  - 8px inside a family, 24px between content groups
  - T1/T4 stay recipes; T2 stays on the SYS47 literal path
  - Do not construct chrome from `public/northstars/S-SYS47-01/*.png`
Evidence:
  - App commit `e691dec` @ github.com/snds/LCARS main (local, not pushed) — verified
  - Scene emit `generate-display-svg.py --check` 122 live primitives — verified
  - vitest 65/65 @ LCARS — verified
  - Agent Todo `personal:SEA-33` @ linear.app/snds — verified
  - Ledger heartbeat `sean-cursor` @ personal:SEA-6 comment `1d0d5fc1` — blocked (approval pending)
Pending added:
  - `personal:SEA-33` review structured live T3 against the pack catalog
Pending resolved:
  - Live T3 was a flat primitive bag; now composed from the pack catalog
Project status changes:
  - 20-lcars-generative-interface: live generative path has a named catalog; Literal path unchanged
Next:
  - `personal:SEA-33` — review `?surface=live` against the pack catalog
  - Push app `e691dec` only if Sean asks
--- END BLOCK ---

### 2026-09-03 — Onori rails absorb + LCARS off-system lint

SessionID: 2026-09-03-voyager-onori1
--- SESSION BLOCK ---
Date: 2026-09-03
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 19-workspace-brain, 20-lcars-generative-interface
Summary: Assessed Sanity/Onori design-system-evals (not previously in vault). Absorbed transferable rails: isolation (`assistance off`), pack recipes, product-repo lint. Generalized LCARS capture into workspace `vqa capture`; retired `prove_sys47.py`. Added reusable `09-tools/eslint-off-system` and wired LCARS `npm run lint`.
Artifacts:
  - 08-knowledge/design/agent-output-rails.md — Onori method without cloning the tester
  - 03-skills/visual-prove-engine/scripts/capture.py + capture.mjs — project-agnostic URL→PNG+manifest
  - 09-tools/eslint-off-system/ — shared no-raw-hex + no-arbitrary-tailwind rules
  - github.com/snds/LCARS `a133bb4` — off-system ESLint + TOKENS-wired schematics + capture wrapper
  - workspace `8024215` — Onori absorb commit (ahead of origin until this session-end push)
Decisions:
  - Do not clone sanity-labs/design-system-agent-tester; workspace path is capture→prove→score
  - Isolation law: docs/catalog proves record `--assistance off`; assistance on is shipping not score
  - ESLint lives in product repos; vault owns reusable rules + doctrine only
  - Pack wrappers may pass URL/out; they must not reimplement the capture manifest
Pending added:
  - centric-ui / Davinci off-token Tailwind lint (employer PR path)
Pending resolved:
  - Sanity design-system-evals source assessment gap
  - LCARS had no ESLint / off-system gate
Project status changes:
  - 19-workspace-brain: agent-output rails + vqa capture + eslint-off-system landed
  - 20-lcars-generative-interface: capture via workspace vqa; `npm run lint` green (65 tests)
Next:
  - `personal:SEA-33` — review `?surface=live` against the pack catalog (from prior fragment)
  - Optional: centric-ui off-token Tailwind lint via employer PR path
  - Push LCARS `a133bb4` only if Sean asks (app already ahead)
--- END BLOCK ---


### 2026-09-03 — ATSMATRIX GitHub org review, skip

SessionID: 2026-09-03-voyager-c0aba2
--- SESSION BLOCK ---
Date: 2026-09-03
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 19-workspace-brain
Summary: Reviewed all 11 public repos under github.com/anyel1to (ATSMATRIX). Account is a two-week demo mill of GitHub Pages canvases. Sean agreed skip; nothing adopted.
Decisions:
  - Do not clone, skill, or knowledge-entry the ATSMATRIX set unless Sean later asks for a fake-agent-demo pattern note
  - AGENT RING architecture prose overlaps existing doctrine (state not transcripts, second reader, receipt before ship); our open-agent-engine / mission-fit / error-correction stack already owns it
  - Canvas HUDs with Math.random plus LangGraph/CrewAI name-drops are visuals, not harnesses
Next:
  - No Agent Todo from this review
  - Separate session: LCARS live-primitive visual review (not this thread)
--- END BLOCK ---


### 2026-09-02 — Open Engine enroll, visual-qa prove, branch prune

SessionID: 2026-09-02-voyager-oe9k2
--- SESSION BLOCK ---
Date: 2026-09-02
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 19-workspace-brain
Summary: Enrolled Open Engine personal lane on this Cursor (`linear-personal` → `hello@snds.design` / `linear.app/snds`). Loaded imaging+game then visual-qa packs; ran prove path (no Legion feature work). `vqa calibrate` 48/48 after fixing relative `--output` double-join (`7a40df5`). LCARS S-SYS47-01 v4 re-prove 16/16 measured, 4 named uncued residuals. Pruned merged leftover branches on personal `snds/*` clones.
Artifacts:
  - 05-artifacts/active/vqa-calibrate_v1.0_2026-09-02.md — planted-defect calibrate 48/48 (gitignored local)
  - 06-context/open-engine/personal.md — Stage 2 2026-09-02 + status operational
Decisions:
  - Domain pack is job-context constitution load, not a replay of git housekeeping
  - Visual-qa prove this session, not Legion Continuum
  - Relative `--output` on `vqa calibrate` must resolve; interact must not re-prefix existing paths
  - Prune only ancestry-merged (or squash leftover of a merged PR) personal branches; keep unique unmerged work
Evidence:
  - Open Engine personal lane @ Cursor `linear-personal` / linear.app/snds Stage 2 — verified
  - vqa calibrate 48/48 @ vqa/1.1 after relative-output fix — verified
  - LCARS S-SYS47-01 v4 `vqa prove` 16/16 measured, capture verified — verified
  - Patch `7a40df5` @ github.com/snds/workspace main — verified
  - Branch prune @ snds/workspace, davinci, legion, LCARS — verified
  - Ledger heartbeat `sean-cursor` @ personal:SEA-6 comment `1d0d5fc1` — verified
Pending resolved:
  - Open Engine personal lane not-registered on Voyager-2.local Cursor (doctor now `ok`)
Project status changes:
  - 19-workspace-brain: Open Engine personal lane operational on this machine; visual-qa pack exercised
Next:
  - Pick new work. Do not start Legion Continuum in a housekeeping thread.
  - Optional leftovers (not filed): Davinci `feat/three-way-contract` post-merge beacon commit; Davinci `chore/sync-design-system-*`; Legion `feat/scale-unification` (closed PR #149)
  - Engine: no new Agent Todo (existing ^pc-NN queue stands). First Cursor ledger comment is `sean-cursor` on personal:SEA-6.
--- END BLOCK ---


### 2026-09-02 — Legion Continuum commit, PR #17 merge, copilot integrity skip

SessionID: 2026-09-02-voyager-k8m2n
--- SESSION BLOCK ---
Date: 2026-09-02
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 13-legion (Legion repo), 19-workspace-brain
Summary: Committed remaining Legion Continuum WIP (unified accept harness, per-archetype lab store, rocky QA). Resolved workspace PR #17 conflicts (mode-first §8e + QA adversarial default as #7); GitHub merged it. Skipped vendored `copilot/` example wikilinks in integrity so vault notes stay gated.
Artifacts:
  - Legion `064e363` — feat(planet): unified accept harness, per-archetype lab store, rocky Continuum QA
  - Legion `4bee94c` — docs/canvases Continuum + fly-to-surface (prior in this thread)
  - Workspace PR #17 merged `9221e54` — §8e + QA #6 system-context + #7 adversarial
  - Workspace `b62058d` — validate-integrity skips `copilot/` only
Decisions:
  - Legion capture dumps (`refs/`, `.tmp-*`) stay local; gitignored
  - Integrity skip is `copilot/` only — not `.claude/skills/` wrappers, not `03-skills/` / `08-knowledge/`
  - PR #17 took current `project-context` / `session-log` from main (June pending list would have overwritten `^pc-NN`)
  - `compact-sessions.py` now strips leftover archive-pointer blockquotes so they do not stack
Evidence:
  - Legion Continuum WIP @ github.com/snds/legion `064e363` on main — verified
  - Workspace PR #17 @ github.com/snds/workspace `9221e54` — verified
  - Integrity skip @ github.com/snds/workspace `b62058d` on main — verified
Pending added: none
Pending resolved: none
Next:
  - Register Open Engine personal lane on Voyager-2.local (`python3 00-bootstrap/doctor/linear-lanes.py`)
  - Refresh Obsidian graph (orphans off)
  - Domain pack on real work, or `python3 09-tools/ds-source-watch.py --fetch`, or `vqa prove`
--- END BLOCK ---


### 2026-09-02 — Domain constitutions, graph crosslinking, Cursor canvas externalize

SessionID: 2026-09-02-voyager-g4x9k2
--- SESSION BLOCK ---
Date: 2026-09-02
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 19-workspace-brain, 20-lcars-generative-interface, 01-mediaservices (canvas copies only)
Summary: Generalized DS constitution rigor to other job contexts (`domain-constitution/1.0`, 10 YAML packs). Fixed Obsidian graph islands that were Dataview-without-edges plus colliding stems (not a missing ontology). Copied 8 Cursor canvases from `~/.cursor/projects/` into git-tracked `07-projects/…/canvases/` and wired `cursor-externalize.py` into session-end so this runs every Cursor close.
Artifacts:
  - 02-shared-references/domain-constitutions/ (spec, domains.yaml, 10 dc-*.yaml, index)
  - 08-knowledge/cross-domain/agentic-domain-constitutions.md
  - 09-tools/cursor-externalize.py
  - 07-projects/19-workspace-brain/canvases/ (domain-constitutions, ds-agentic-ontology, perception-critique-stack, skill-hub-rigor-audit)
  - 07-projects/20-lcars-generative-interface/canvases/lcars-replication-gap.canvas.tsx
  - 07-projects/01-mediaservices/canvases/ (looney-tunes-loudness, duplicate-scan-outcome, authoritative-delete-list)
Decisions:
  - Cursor live canvases stay in `~/.cursor/projects/` (IDE compile path); vault copies are the portable source of truth.
  - Legion canvases belong in the Legion repo, not snds/workspace. Copied to Legion/docs/canvases/ on disk; not committed there.
  - Do not star-link Copilot, .superpowers, or vendored command trees into the Obsidian graph.
Pending added: none
Pending resolved: none
Next:
  - Refresh Obsidian graph (orphans off). Remaining islands should be vendor/Copilot/artifact.
  - Optional: commit Legion `docs/canvases/` in the Legion repo.
  - Use a domain pack on real work, or `python3 09-tools/ds-source-watch.py --fetch`, or `vqa prove`.
  - Open Engine personal lane still not-registered on this machine (`python3 00-bootstrap/doctor/linear-lanes.py`).
--- END BLOCK ---


### 2026-09-02 — Ontology and knowledge graphs for agents

SessionID: 2026-09-02-voyager-ontkg
--- SESSION BLOCK ---
Date: 2026-09-02
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 19-workspace-brain (teaching; no project files changed)
Summary: Explained ontology (shared types and legal relations) vs knowledge graph (typed facts in that vocabulary), and how agents use classify → traverse → constrain → write-back instead of dumping similar text. Mapped the same split onto this vault: workspace-ontology + skill frontmatter as schema; registry load_chains, routing map, and epistemic `relations:` as the graphs; retrieval finds candidates, types decide what may act.
Decisions:
  - Career-ops trigger on the letter `i` treated as a misfire; did not load job-search skills
Next:
  - Sean picks a follow-up if wanted: walk one vault decision through the graph; contrast ontology+graph vs RAG/skills/memory; or sketch a domain graph (PLM / LCARS / tokens) on top of the workspace ontology
--- END BLOCK ---

### 2026-09-02 — Prove-engine merge close + DSDS persist

SessionID: 2026-09-02-voyager-e4f1a
--- SESSION BLOCK ---
Date: 2026-09-02
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.6
Project(s): 19-workspace-brain, 20-lcars-generative-interface
Summary: Closed the prove-engine thread (vqa/1.1 altitudes A–G, play-prove, /optimize, LCARS uncued residuals) already merged to main as 0f4228a. Persisted the 2026-09-01 project-independent DSDS constitution + ds-source-watch landing that was still sitting staged. Folded the 2026-08-26 Looney Tunes fragment into session-log.
Artifacts:
  - 03-skills/visual-prove-engine/ vqa/1.1 + 03-skills/play-prove/ (on main via 54a2efe / 0f4228a)
  - 02-shared-references/dsds/dsds-constitution.md + workspace-ds-constitution.dsds.yaml
  - 02-shared-references/idempotent-design-decisions.md + 03-skills/ds-source-watch/ + 09-tools/ds-source-watch.py
Decisions:
  - Personal-solo merge to main, not a PR; SWF dumps stay untracked
  - DS constitution is project-independent; projects extend it, they do not fork it
Evidence:
  - prove-engine merge @ github.com/snds/workspace main 0f4228a — verified
Pending resolved:
  - Prove-engine course corrections 1–12 + /optimize landed on origin/main
Next:
  - Run `python3 09-tools/ds-source-watch.py --fetch` when the first snapshot should be judged
  - LCARS: add measured cues for the four named uncued residuals, then build to them
--- END BLOCK ---


### 2026-08-26 — Looney Tunes loudness analysis + full subtitle coverage

SessionID: 2026-08-26-voyager-b7191a1
--- SESSION BLOCK ---
Date: 2026-08-26
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Claude Fable 5
Project(s): 01-mediaservices
Summary: Measured EBU R128 loudness for all 2,919 Looney Tunes files plus watched reference titles; derived a -21.9 LUFS reference target and a -6.6 dB best nominal gain for the set Plex actually plays. Found the real problem is spread, not level: Plex prefers the unmanaged dump folder for 1,035 of 1,064 episodes (15.1 dB p10-p90 spread) while the Sonarr-managed twins are already leveled (1.7 dB spread, nominal -7.4 dB). Separately closed the subtitle gap on played copies: 781 sidecars placed (721 copied from managed twins, 46 extracted from embedded tracks, 14 subgen/whisper), final audit 1,064/1,064 covered, 0 uncovered.
Artifacts:
  - Server /mnt/user/appdata/media-sentinel/loudness/ — results.jsonl (2,919 measurements), summary.json, gains.csv (per-file clip-safe gains), plex-preferred.json (episode → played file map), subtitle-sync-journal.txt (781-line delete-list of every sidecar placed)
  - Canvas looney-tunes-loudness.canvas.tsx (Cursor, MediaSentinel project) — full analysis
  - MediaSentinel repo scratch/loudness-scan.py + scratch/loudness-analyze.py (gitignored scratch)
Decisions:
  - Loudness fix recommendation: point Plex at the managed copies (MediaSentinel dedupe path) then apply one nominal gain of -7.4 dB, instead of per-file gain edits on 1,871 dump files
  - Subtitle quality order enforced: human sidecar > extracted embedded > whisper; nothing overwritten, every placement journaled for reversal
  - subgen used only for the 14 episodes with no human-made source anywhere
Pending added:
  - User decision: adopt dedupe-to-managed recommendation vs per-file gains from gains.csv
  - If dedupe chosen: run MediaSentinel duplicate adjudication on the two Looney Tunes folders
Pending resolved:
  - (none from prior baton)
Next:
  - Await user's pick on the loudness remediation path; gains.csv is ready either way
Git: MediaSentinel repo untouched (scratch/ + docs/ only, uncommitted); workspace this commit
--- END BLOCK ---

### 2026-08-11 — cui ViewToolbar bg-card consistency

SessionID: 2026-08-11-work-a7c2e1
--- SESSION BLOCK ---
Date: 2026-08-11
Machine: Work MacBook Pro
Surface: Cursor
Project(s): centric-ui (employer)
Summary: Materials ViewToolbar used bg-background (darker) via single-toolbar flag; switched all collection toolbars to bg-card to match Material Colours / Samples. Pushed follow-up commit to PR #284.
Evidence:
  - PR updated @ https://github.com/cpes-software/centric-ui/pull/284 — verified
Next:
  - Review/merge https://github.com/cpes-software/centric-ui/pull/284
--- END BLOCK ---


### 2026-08-11 — cui data-table landing parity + sticky actions

SessionID: 2026-08-11-work-40891f
--- SESSION BLOCK ---
Date: 2026-08-11
Machine: Work MacBook Pro
Surface: Cursor
Project(s): centric-ui (employer)
Summary: Finished Materials landing table parity work in `@centric/data-table`: decoupled sticky row actions into spacer + float host (fixes stacked hover wash), restored package header border/pad, wired landing density to global Compact/Normal/Spacious, stripped fighting landing CSS. Opened PR.
Evidence:
  - PR opened @ https://github.com/cpes-software/centric-ui/pull/284 — verified
Decisions:
  - Sticky actions: in-flow spacer (wash + width) + zero-width sticky float host (pill only)
  - Landing tables follow global app density; non-landing BO tables keep view-config density
  - Header separator/height owned by package, not Materials recipe; radii deferred post density-merge
Next:
  - Review/merge https://github.com/cpes-software/centric-ui/pull/284
  - After merge: revisit table shell radii if still off vs demo
--- END BLOCK ---


### 2026-08-11 — Local centric-service stack for UI API auth

SessionID: 2026-08-11-work-localstack
--- SESSION BLOCK ---
Date: 2026-08-11
Agent: Cursor Grok 4.5
Surface: Cursor
Machine: Work MacBook Pro (CS-K746DRWXY1)
Project(s): centric-ui (employer), centric-service
Artifacts:
  - ~/Projects/cpes-software/centric-service — cloned
  - ~/Projects/cpes-software/platform-golden-verticals — cloned (sibling for volume-mode flavours)
  - centric-ui `.env.local` / `.env.compose.local` — local compose creds (`DUMMY-123`, provisioner `cpes-record-service`)
  - centric-ui `vite.config.ts` — `server.host: true` (IPv4+IPv6; fixes ERR_CONNECTION_REFUSED -102)
  - Colima Docker runtime (20GB / 6 CPU) — Docker Desktop cask install blocked on sudo
Decisions:
  - Local stack path (Leanne): compose + `npm run dev`, not Cursor-hosted server.
  - Local Keycloak user `test`/`test` (realm VMS, org test-org) is fine for FE work.
  - Flavour provisioner unauthorized was wrong API identity (`cpes-admin-portal`+cloud key); use `cpes-record-service`+`DUMMY-123` locally.
Pending added:
  - Colima memory pressure: Keycloak OOM (exit 137) → nginx 502; may need to stop LocalStack/OpenSearch-dashboards when idle.
  - Golden provisioner poller can hang after JWT expiry (`status=unknown`); volume-mode sibling checkout is the reliable local source.
  - `gh auth` token invalid on this machine; GHCR pull still needs PAT/`gh auth login` if not building `centric-service:local`.
Pending resolved:
  - Unauthorized API / no local backend — stack up; login + provisioner identity fixed for local compose.
Next:
  - Keep UI via terminal: `cd ~/Projects/cpes-software/centric-ui && npm run dev` (agents' nohup sessions die).
  - If Keycloak 502 again: `docker start keycloak` (or compose up keycloak) after OOM.
  - Optional: trim compose services / bump Colima RAM further to stop Keycloak OOMs.
--- END BLOCK ---


### 2026-08-10 — Harness-map cycle closed + CI triage

SessionID: 2026-08-10-work-hmclose
--- SESSION BLOCK ---
Date: 2026-08-10
Machine: Work MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.5
Project(s): 19-workspace-brain
Summary: Closed the harness-map cycle — applied #1–#3+#6, accepted #4/#5/#7/#8 standing; triaged email CI failures (INDEX/MEMORY orphans, fixed by #1); main green and pushed through `6b92c1a`.
Artifacts:
  - 07-projects/19-workspace-brain/reports/harness-map_v1.0_2026-08-07.md — map + stamp + applied/accepted dispositions
  - 07-projects/19-workspace-brain/reports/harness-map.stamp — first real stamp (2026-08-07)
  - 06-context/project-context-detail.md — graduated pending substance
  - 06-context/project-registry.md — Active Projects narratives (load later)
  - 09-tools/check-unattended-runner-gate.py — unattended runner hard gate
Decisions:
  - Apply harness-map #1–#3+#6; leave #4 Keep, #5/#8 Probation, #7 Load later/Keep as standing (Sean ack).
  - Retest #5 on next plugin publish; revisit #8 ~2026-09-07.
Evidence:
  - workspace CI all green after apply @ github.com/snds/workspace actions on e2d28eb — verified
  - prior workspace-integrity failures (runs 31190694022, 31191199865) = INDEX/MEMORY orphans — verified fixed by #1
Pending added: (none)
Pending resolved:
  - Harness-map first-run + stamp (was next action on baton)
Project status changes:
  - 19-workspace-brain: harness-map cycle closed; baton points at optional mission-fit + probation retests
Next:
  - Optional: mission-fit on one unreliable “done”
  - Retest harness-map #5 on next build-local-skill-plugin publish
  - Revisit harness-map #8 (~2026-09-07)
  - Still open from prior baton: ^pc-07 / ^pc-11 homes; lane ambiguity ^pc-30 / ^pc-41
--- END BLOCK ---


### 2026-08-05 — Layer-1 vault retrieve + dispatcher fallback

SessionID: 2026-08-05-voyager-5d6242
--- SESSION BLOCK ---
Date: 2026-08-05
Machine: Personal MacBook Pro
Surface: Cursor
Agent: Cursor Grok 4.5
Project(s): 19-workspace-brain
Summary: Shipped Layer-1 lexical vault retrieval (`09-tools/vault-retrieve.py`, stdlib FTS5) and wired it as a capped Claude dispatcher fallback when Layer 0 under-fires; Cursor gets CLI-on-demand only.
Artifacts:
  - 09-tools/vault-retrieve.py — FTS index/rebuild/query + graph expand; machine-local `.claude/state/vault-retrieve/`
  - .claude/hooks/dispatcher.py — SessionStart index refresh; UserPromptSubmit lexical tier (min 2 Layer-0 targets, cap 2, `--cached`)
Decisions:
  - Triggers stay primary; lexical is gap-fill only (not a peer flood on every prompt)
  - Index personal vault layers only — no `07-projects/` / employer surfaces
  - Cursor has no prompt-hook equivalent → document CLI; do not fake a dispatcher tier there
Pending added:
  - Optional: golden-set eval of trigger misses vs lexical baseline
  - Optional: dense/embedding path as capability-registry entry with degrade→lexical
Pending resolved:
  - (none from prior baton; this session was additive tooling)
Next:
  - Prove lexical fallback in a live Claude Code session (SessionStart rebuild + under-fire inject)
  - Optionally design dense Layer 2 only after golden-set shows lexical gaps worth the capability
  - Prior baton still open: review personal:SEA-11; decide personal:SEA-32
Git: 55b9f2a (feature) + this session commit
--- END BLOCK ---


### 2026-08-03 — Domain rigor stack hardening

SessionID: 2026-08-03-voyager-r7k2
--- SESSION BLOCK ---
Date: 2026-08-03
Machine: Personal MacBook Pro
Surface: Cursor
Project(s): Workspace (skill hubs / domain rigor)
Summary: Encoded five-layer domain rigor stack (#13) and shipped L1–L5 hardening across hubs/spokes outside the parallel photoreal session; measurement toolkits + reciprocity/capability follow-ups landed.
Artifacts:
  - 01-frameworks/13-domain-rigor-stack.md — reusable L1–L5 contribution mechanism
  - 01-frameworks/14-engineering-operating-model.md — eng L1 gates
  - 01-frameworks/15-analysis-operating-model.md — analysis L1 gates
  - 01-frameworks/16-security-operating-model.md — security L1 gates
  - 03-skills/a11y-audit-toolkit + fe-perf-harness — break measurement monoculture
  - Command hubs: eng, arch-guild, process-plugins, design-system-ops; career hub = job-search-strategist
Decisions:
  - Domain rigor is a five-layer stack (ops model → command hub → measurement → load chain → multi-voice + doctrine precedence), not UI/UX-only.
  - Plugin skills defer to AGENTS.md / frameworks; frontmatter `defers_to` + `rigor_role` are first-class.
  - Contested photoreal/3D/game surface (Framework #12, img-photoreal*, legion-*, 08-knowledge/research|game-dev) owned by parallel session — do not collide.
  - Career: hub = job-search-strategist; spokes wrap ~/.agents/skills mirrors.
Pending resolved:
  - Specialist/rigor gap evaluation across Workspace hubs (execute comprehensively, including former leave-alones).
  - Measurement monoculture: a11y toolkit, FE perf harness, /qa lenses motion|dataviz|type|security.
Next:
  - Spot-check career routing docs vs hub = job-search-strategist if a session touches job search.
  - Use Framework #13 as the gate when adding or hardening any new domain skill cluster.
--- END BLOCK ---


### 2026-08-03 — Realtime photoreal rigor stack (#12)

SessionID: 2026-08-03-voyager-b505c2
--- SESSION BLOCK ---
Date: 2026-08-03
Machine: Personal MacBook Pro
Surface: Cursor
Project(s): Workspace (skills/frameworks); Legion (consumer contracts only)
Artifacts:
  - 01-frameworks/12-realtime-photoreal-operational-framework.md — triple done-gate + movie-level northstar ops
  - 03-skills/realtime-visual-craft/ — Impeccable-shaped command hub + RENDER/BUDGET/NORTHSTAR templates
  - 03-skills/render-qa-toolkit/ — frame/motion/still measurement suite (Legion ?perfcapture config)
  - 03-skills/interactive-capture-eval/, visual-qa-photoreal-rendering/, rendering-guild/ — motion capture + photoreal QA + guild
  - 03-skills/{dynamic-gi,shadow-quality,virtual-texturing,bake-orchestration,gpu-capture,adapter-*}/ — AAA spokes + engine adapters
  - Legion RENDER.md / BUDGET.md / NORTHSTAR.md + docs/render-acceptance-harness.md — project consumer contracts
Decisions:
  - Multi-engine principles with thin Unreal/Unity adapters (1B); full rigor stack in one program (2B)
  - Legion is test platform only — skills stay in Workspace
  - Evaluation requires still grid + flythrough frame-by-frame + measured ms; low-res/still-only verdicts banned
  - Movie-level fidelity gated by named NORTHSTAR stills/videos/game examples
Pending resolved:
  - Workspace photoreal connective tissue (framework #12 + command hub + measurement + guild + adapters)
  - Legion contracts landed on main (dcd9abb)
Next:
  - Run a live Legion acceptance pass on official poses + flythroughs in native Chrome (not IDE-browser alone)
  - Sign concrete northstar file paths into Legion NORTHSTAR.md as captures are approved
  - Optional: register Open Agent Engine personal lane when MCP is available (skipped this session — not-registered)
--- END BLOCK ---
---

### 2026-08-04 — Token Spec page (Figma ↔ code)

SessionID: 2026-08-04-token-spec-page
--- SESSION BLOCK ---
Date: 2026-08-04
Agent: Composer
Surface: Cursor
Machine: Work MacBook Pro
Project(s): Centric SaaS PLM — Figma DS (`o6o1ZuGHxDow2vHLuYXT6X`); centric-ui tokens read-only
Summary: Built a **Token Spec** page in the DS file from live Figma variables, paired each
  semantic token with its centric-ui `--sem-*` (when mapped), flagged raw/alias deviations,
  and tagged representable-but-missing tokens on both sides.
Artifacts:
  - Figma page `Token Spec` (id `405:1679`, index 2 after Cover separator)
  - `08-knowledge/design/token-spec-page.md`
  - `08-knowledge/design/token-spec-figma-vs-code.json`
Decisions / findings:
  - 74 semantic colors: 40 MATCH · 6 DEVIATE · 28 FIGMA-ONLY
  - Deviations concentrated on selected/sidebar chrome: Figma uses `interaction/*` opacity
    overlays + `action/primary` foregrounds; code still uses solid `blue-5` / `blue-11` and
    zinc sidebar accent.
  - Density + `interaction/*` + `status/caution*` are Figma-ahead (no code counterparts).
  - Missing in Figma (representable): `--header-h`, `--shadow-cds-drop-{1,2,3}`.
  - (Superseded 2026-08-05) Radii now density-modeled with `xxs`.
Next:
  - Optionally sync code selected/sidebar to Figma interaction model, or document intentional lag.
  - Add effect variables for CDS drop shadows if Figma should own them.
--- END SESSION BLOCK ---

### 2026-08-05 — Added prototype library comparison
Summary: Rebuilt Token Spec as three-way (Figma ↔ centric-ui ↔ saas-plm-prototype).
  Density + radii call out Normal-axis offset (Figma Normal = Proto Compact).
  Proto-only density tokens tagged MISSING IN FIGMA.

### 2026-08-05 — Align Figma density/radii to prototype
Summary: Figma Density + Radii updated to prototype values; missing density
  tokens added; proto gained padding-x/sm twin, radius-none,
  radius-full. Token Spec rebuilt (18 density MATCH). Later: Radii
  density-modeled + `radius/xxs`; centric-ui density port.
