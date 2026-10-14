---
title: Mechanization review — where agents still write and judge by hand, and what scripts should do instead
version: "1.0"
date: 2026-10-13
surface: Claude Opus 5.5 + Claude Code (Mac desktop app), Work MacBook Pro
sha: 33ece99
status: proposed — no changes made yet; IDs M1–M25 and B1–B10 are new
companion: workspace-automation-review_v1.0_2026-09-11.md, automation-second-wave_v1.0_2026-09-15.md
---

# Mechanization review — 2026-10-13

## Answer first

The read side of the harness is already well guarded. The token lane in
`09-tools/workspace-harness.py --tokens` passes every budget, and the two earlier reviews closed
their read-cost items (A1–A9, C1, C2).

The cost has moved to the **write side**, which nothing measures yet. Agents still:

- re-type text that a hook already produced,
- hand-write files that are pure functions of git and frontmatter,
- run validators one by one and read their raw output,
- rewrite growing "baton" files every session,
- read about 160k tokens of files before an `/optimize` audit judges anything.

The five changes with the best return, in order:

1. **One session-close script (M1, M2).** The agent hands it about ten short fields as JSON. The
   script writes the fragment, the handoff stamps, the pending-item anchors, the registry dates,
   the evidence lines, the commit and the push. Estimated per session-end: reading drops from
   ~5–13k tokens to ~1k, tool calls from 10–15 to 1–2, and written output from ~1–4k tokens to
   ~0.1–0.3k.
2. **Hooks that act instead of instruct (M5–M8).** Show the session card to Sean directly instead
   of having the agent re-type it. Run the generators and validators quietly at the end of a turn.
   Cut the per-prompt routing text roughly in half.
3. **Generate the hand-kept indexes (M9–M13).** That covers the memory index, the knowledge index
   and hints, the artifact registry, the tools README and about ten smaller lists. Each one today is
   written by an agent and then checked by a validator against a source it could be built from.
4. **Probe-first audits (M14–M19).** `/optimize` becomes one JSON run plus targeted reads.
   Recurring audit findings become detectors.
5. **A skill scaffold and leaner hubs (M20–M24).** One spoke today means hand-editing 4–14 files.
   Every spoke load also re-reads 7–9 KB of hub routing text it no longer needs.

Ten bugs turned up along the way (B1–B10). Several of them create agent work themselves. For
example, B1 is very likely why the session card keeps reporting "uncommitted work".

The meta-fix is **M25: give the harness a write-cost lane**, so these gains cannot quietly
regress, the same way the token lane protects read cost.

---

## 1. How this was measured

Six passes:

- **Five read-only surveys:** session lifecycle, maintenance workflows, hand-kept indexes, hooks,
  and the skill corpus.
- **A git churn pass** over the 487 commits since 2026-08-01.

Every headline number below was re-run in this session before it was written down.

**Evidence-grade legend** (standard: `02-shared-references/delivery-playbooks/05-validation-harness.md`):

- `VERIFIED` means measured by a command named inline, re-runnable as written.
- `INFERRED` means an estimate built from measured sizes, using bytes ÷ 4 ≈ tokens, or from a
  sample. The sample is named.

| Claim | Grade | Measured by |
|---|---|---|
| Read budgets all pass. The session floor is 15,054 tokens. The banned-ingest cost is 92,184. | VERIFIED | `python3 09-tools/workspace-harness.py --tokens` |
| `/optimize` Step 1 reads ~638 KB ≈ 159k tokens | VERIFIED | `cat` of the Step 1 file list (optimize/SKILL.md:41-59) piped to `wc -c` |
| The busiest file is `19-workspace-brain/SESSION-STATE.md`: 75 commits since Aug 1, then session-log at 65 | VERIFIED | `git log --since=2026-08-01 --name-only` → `uniq -c` |
| Baton files: 107.5 KB (planet-lab), 70.3 KB (bootstrap-generator), 29.5 KB (workspace-brain) | VERIFIED | `wc -c 07-projects/**/SESSION-STATE.md` |
| No tool extracts only the Live handoff block | VERIFIED | `grep -ln "Live handoff" 09-tools/*.py .claude/hooks/dispatcher.py` → none |
| Routing text is injected on ~94% of prompts, with a mean of 1,163 chars, and a 369-char footer makes up 29% of the bytes | INFERRED | survey sample: 248 real prompts across 19 workspace transcripts |
| All 46 tracked tools have docstrings; 8 tracked `.py` tools have no README section | VERIFIED | `ast.get_docstring` vs README `##` headings |
| 10 stale `.touched` files (Jul 30 – Sep 24) are still read by the auto-commit | VERIFIED | `ls 06-context/sessions/*.touched`, dispatcher.py:1384-1395 |
| "shadegraph" routes to nothing | VERIFIED | `python3 09-tools/prompt_route.py --utterance "open the shadegraph project"` |
| A spoke load re-reads 7–9 KB of hub routing prose | INFERRED | survey byte count of Spoke Network, Cross-Hub and Domain Boundary sections across 309 SKILL.md files |

---

## 2. Bugs found along the way (fix first — small, and each one creates agent work)

| ID | Bug | Where | Effect on agents | Fix |
|---|---|---|---|---|
| **B1** | Stale touch files are never pruned. The auto-commit reads every `*.touched` with no age limit and skips every path they list. That includes `project-context.md`, `AGENTS.md`, `MEMORY.md` and the workspace-brain baton. | `.claude/hooks/dispatcher.py:1384-1395`; `closure.py:674-676` uses an idle window, so the two disagree | Edits stay uncommitted. That feeds the 4 "uncommitted work" notices on today's card and the session-end Step 7.5 prompts. | Apply closure's `IDLE_S` window in `_other_session_claims`, and prune old touch files at SessionStart |
| **B2** | Blank lines pile up in the session log. Each archive pass leaves one more. There are 38 today. | `compact-sessions.py:191-200` | Small read cost on every boot | Strip the surrounding newlines when the pointer is replaced |
| **B3** | The search-index refresh is allowed 60 s inside a SessionStart hook that is killed at 30 s | `dispatcher.py:1164` vs `.claude/settings.json:11` | On a slow rebuild the whole card is lost | Run the refresh in the background, or cap it at ~10 s |
| **B4** | Seven docs give the rebuild order backwards (build-related before build-registry) | `13-domain-rigor-stack.md:113`, `08-…framework.md:137`, `close-out/SKILL.md:110`, `self-improve/SKILL.md:43`, `skill-placement/SKILL.md:39`, `.github/PULL_REQUEST_TEMPLATE.md:33`, `.github/CONVENTIONS.md:69` | Agents hand-run four commands in the wrong order | Replace each with `python3 09-tools/nightly.py --phases rebuild`, as `_SKILLS.md:62` already does |
| **B5** | Project `triggers:` in README frontmatter never reach the router | `07-projects/*/README.md`; `prompt_route.py` | "shadegraph" and 3 of 4 subatomic triggers fall through to search guesses | Derive project routes from README frontmatter (part of M13) |
| **B6** | The two "heads" injected at SessionStart contain no data. The session-log head stops at `## Session Entries`, and the project-context head is all preamble. | `dispatcher.py:942-943` | ~2,000 chars per session for nothing | Inject the first entry and the first pending items, or drop both |
| **B7** | The harness counts knowledge `trigger_words` frontmatter as a route, but the router never reads it | `workspace-harness.py:462-485` vs `prompt_route.py:216-243` | The harness can report green for an entry the router cannot reach | Pick one source; M10 resolves it |
| **B8** | Rules contradict each other | `CLAUDE.md:82` says read `_INDEX.md` before domain work, while the hook says never ingest it. `CLAUDE.md:39` says the hook loads the read-order files, but it loads none of them. | Agents read files they were told not to | Fix the adapter text in the same change as M5 |
| **B9** | Prose has drifted from facts | `new-project/SKILL.md:38` "all eleven" frameworks (actual: 18); `_CHEATSHEET.md` "5 slash commands"; `today/SKILL.md` daily-note path does not match the real folder; `artifact-registry.md:90-93` lists a file archived 2026-06-16 | Agents act on wrong counts and paths | Fix now. M15's restated-count detector stops the recurrence. |
| **B10** | The Cursor subagent stop hook sends a `followup_message`, which auto-starts a new agent turn. The stated policy forbids this. | `.cursor/hooks/cursor-subagent-stop.sh` vs `ws_hook.py:1071-1074` | An extra agent turn after every subagent in Cursor | Make it a notice, not a follow-up |

Also noted, lower priority:

- Three dispatcher helpers are defined but never called (`dispatcher.py:469, 506, 532`). One of
  them would run the routing evaluator automatically, while `session-status.py:530-534` asks the
  agent to run it instead.
- Nine hubs lack `prerequisites`, which breaks rule 1 of framework 13.
- `03-skills/figma-api-pipeline/` has no `SKILL.md`, which breaks rule 5.

---

## 3. Recommendations

Effort: **S** is under half a day, **M** is one to two sessions, **L** is a multi-session wave.

### Wave 1 — Session close (the largest per-session writing)

| ID | Change | What the agent stops doing | Est. saving | Effort |
|---|---|---|---|---|
| **M1** | **`09-tools/session-close.py`** (or `closure.py close`), driven by a JSON of judgment fields: `{title, summary, decisions[], next[], pending_add[], pending_resolve[], handoff{…}, evidence[], new_artifacts{}, knowledge}`. Most of the pieces already exist: `workspace_mcp.t_session_end` (fragment header), `profile_resolve` (surface and device), the touch ledger and session baseline (`ws_hook.py:350-372`), `receipts.jsonl` (evidence), `closure.plan`, `prune-our-branches.py`, and `nightly.py`. | Probing the surface, picking the fragment filename and IDs, assigning the next `^pc-NN`, typing dates, editing registry dates, copying exit codes into an Evidence line, running the rebuild, a blanket `git add -A`, the per-file orphan audit, and typing the confirm line | Per session-end: read ~5–13k → ~1k; tool calls 10–15 → 1–2; written ~1–4k → ~0.1–0.3k tokens (INFERRED) | L |
| **M2** | **Baton schema.** The Live handoff becomes a fenced YAML block of six judgment fields: focus, next, open decisions, blocked on, do-not-touch, TL;DR. The script writes the stamps, Last action, Agent thread, Environment and VCS state (or drops them, since the card computes them live). History becomes one auto-appended line that links the fragment. Add `baton.py show <project>`, which prints only the handoff. `session-status.py` reads `focus` from the YAML, which fixes the stale project titles on the card. | Rewriting a 2–11 KB handoff every session, which in practice has become a journal (fontface: commit SHAs, test counts and lessons); writing the same "next" in five places | ~1.5–2.8k → ~0.2–0.3k tokens written per handoff update; entry read drops from up to 27k tokens (planet-lab) to the block alone (INFERRED) | M |
| **M3** | **Reconcile becomes a fold.** Once fragments carry `pending_add` / `pending_resolve` IDs, merging is set arithmetic, and only true conflicts reach Sean. Delete reconcile Steps 2–5. They hand-edit `session-log.md` and delete `^pc` items, and both actions contradict standing rules. | Hand-merging blocks | Rare workflow (last used 2026-07-09); this is mostly a correctness fix | S |
| **M4** | Give `side-chat-handback.py` a `write` subcommand that fills in frontmatter, the on-disk list and the consume boilerplate. Make `today` a script, or retire it into the card. | Typing ~440-token inbox files, ~150 tokens of which are a file list | Small, but frequent in Cursor | S |

### Wave 2 — Hooks that act instead of instruct

| ID | Change | What the agent stops doing | Est. saving | Effort |
|---|---|---|---|---|
| **M5** | **Card to Sean, ritual line to the agent.** SessionStart sends the card as `systemMessage`, which Sean sees, and keeps only the ritual line plus agent-actionable notices in `additionalContext`. Drop the two empty heads (B6). The hook runs the closure sweep itself and reports one line instead of four "run: ws closure plan" lines. Update `CLAUDE.md:44-65` and `AGENTS.md:134-142` in the same change. | Re-typing a ~35-line card; it is told to do so in six places | ~700 output + ~500 input tokens per session (INFERRED). **Check first:** how a 35-line `systemMessage` renders in the desktop app, and whether Cursor has an equivalent. | S |
| **M6** | **Stop-hook regeneration and verify.** If the turn touched a generator input (SKILL.md, trigger-routes.json, knowledge-hints.json, `_INDEX.md`), run `nightly.py --phases rebuild --scope session:<sid>`, then `--phases verify --from-diff --fast`. Silent on success, one line on failure. The generators take ~0.2–0.3 s each. Also read `.workspace/state/last-gate.json` to skip re-runs on an unchanged tree. | The hand loop of edit → rebuild → harness → read output → fix (survey sample: 269 harness calls with ~204k chars of output read back across 19 transcripts) | Removes most validator round-trips; the size depends on the session (INFERRED) | M |
| **M7** | **Routing diet.** Say the fixed footer once per session (−29% of routing bytes). Drop lexical-only injections, or require a score threshold (38% of injections). Don't re-inject a target already sent this session (`figma` fired 50 times). Inject a path, not a 583–821-char template. Remove or phrase-qualify the generic one-word triggers (`harness` ×71, `review`, `audit`, `lens`, `vector`, `warning`, `invalid`). Replace the "run close-out-dispatch" follow-through line with M6. Teach `evaluate-skill-routing.py` to score injection size and false positives, and add negative cases (5 of 54 today). | Reading ~14k chars of routing text per session, and complying with off-topic "read X BEFORE acting" lines (1–4 reads of 5–40 KB each) | Roughly half of the per-prompt routing text (INFERRED) | M |
| **M8** | **State each rule once.** Turn off the every-15-prompts heartbeat on Claude Code, since the beacon is already in the system prompt and survives compaction. Collapse the ritual rule from six statements to one. Keep the read order in one place that `workspace_mcp.py:81` and `workspace-harness.py:931` both read. | Re-reading the same rules 3–6 times per session | Small per prompt, but steady | S |

### Wave 3 — Generate the hand-kept indexes

Each file below is written by an agent and then checked by a validator against a source it could be
built from. Inverting that removes both the writing and the validator's reason to exist.

| ID | File | Generate from | Commits since Aug 1 | Effort |
|---|---|---|---|---|
| **M9** | `06-context/memory/MEMORY.md` | Each memory's `type` and `description` frontmatter. Fix one file without them first (`feedback-cross-surface-token-aligned.md`). | 29 | S |
| **M10** | `08-knowledge/_INDEX.md` and 94 of 138 `knowledge-hints.json` entries | Move each index line into its entry's frontmatter as `description` and `triggers` (a one-time migration of 102 entries), then generate both. Resolves B7. | 40 + 16 | M |
| **M11** | `06-context/artifact-registry.md` | Tracked paths: Last modified from `git log -1`, Purpose from the README, frontmatter or docstring. A small hand-written sidecar for the 9 gitignored local-only artifacts. Removes session-end Step 4. | 17 | M |
| **M12** | `09-tools/README.md` (669 lines) | Each tool's module docstring and usage block, plus a short hand-written intro | 37 | S |
| **M13** | Smaller generators, each S: <br>• capability `powers` from skills' `requires:` (the inverse, like `governs` today) <br>• peers declared once in frontmatter, with `build-related.py` emitting both sides (220 hand-written peer lines) <br>• an `archive.py` that does `git mv` plus a stamped ARCHIVE-LOG row (no archive script exists) <br>• `_SKILLS` / `_PROJECTS` / `_FRAMEWORKS` lists and counts ("eighteen" is typed in 10 places) <br>• hub Spoke Manifests in generated markers (they have drifted: lead-frontend-engineer lists 15 of 26 spokes) <br>• CI `paths:` filters from `DIFF_CLASSES` <br>• project routes from README `triggers:` (fixes B5) <br>• thin adapters from one template plus `surfaces.json` fields | Respective sources | — | S each |

Delete the hand-typed `_Last updated:` lines in `project-context.md`, `artifact-registry.md`,
`SURFACES.md` and the batons. All of them already lag behind git, which holds the true date.

### Wave 4 — Probe-first audits

| ID | Change | What the agent stops doing | Est. saving | Effort |
|---|---|---|---|---|
| **M14** | **`/optimize` probe-first.** Step 1 becomes `workspace-harness.py --json` plus `nightly.py --check --json` plus the new probes in M15. The agent opens only the files a probe flags, and uses `artifact-find.py` instead of reading the 40 KB registry whole. Add `--json` to the validators, because the harness keeps only each gate's last line, so warnings never reach JSON. | A 159k-token fixed read (VERIFIED), ~14 hand-run probe commands, and diffing two files "in full" by eye in Step 4a | ~159k → ~20–30k tokens per run (INFERRED) | M |
| **M15** | **Turn recurring audit findings into detectors.** These have recurred across 2–4 audits: <br>• stale batons (more than 30 days; 10 today) <br>• pending items older than 60 days or undated (33 of 46 undated) <br>• resolved `[x]` items still listed as pending (4 today) <br>• restated counts (add rules to the existing `RESTATED_FACTS`) <br>• hubs without `prerequisites` <br>• skill folders without `SKILL.md` <br>• an `audit_skip` flag that some tool actually honours <br>Then generate the audit-log entry from the probe JSON, so the agent adds only verdict lines. Have a small parser feed `rule_of_three.jsonl` from the audit log; it has no rows since 2026-09-26. | Re-deriving the same findings by reading, and hand-writing 30–65-line audit entries | 2–6 KB written per audit → a few lines | M |
| **M16** | The "audit is stale" nudge on the card fires when a cheap probe goes red, not only on calendar age | Starting a ~160k-token audit when nothing has drifted | One avoided full audit per false nudge | S |
| **M17** | **Close-out SKIP classes run when they can.** Add a conditional step that runs when `--artifact` is passed or the tool is on PATH: `vqa.py prove/motion/mesh`, `token-audit.py --config`, the read-only CI check-runs lookup (already in `session-status.py:256-271`), and a threat-model shape check. Retire `intent-run-doctor`; its own note says it is not a detector. | Honest-skip prose where a detector could actually run (15 SKIP steps) | Quality gain more than token gain | M |
| **M18** | `/harness-map` system-map tables and stamp generated from registry and harness JSON. Stop listing the banned-ingest files (the 253 KB registry and the 64 KB routes) as inspect targets. | ~25 rows of counted tables and the stamp, by hand | ~140-line report → judgment sections only | S |
| **M19** | `/framework-check` prints only the selected lenses' summaries from `00-README.md`, with lenses gated by changed paths the way close-out maps diff classes | Always reading the core six frameworks (~31k tokens) plus the README | ~41k → ~5–10k tokens per run (INFERRED) | S |

### Wave 5 — Skill authoring and the skill corpus

| ID | Change | What the agent stops doing | Est. saving | Effort |
|---|---|---|---|---|
| **M20** | **`new-skill.py <name> --hub X [--triggers …]`**. It checks the name against `03-skills` and plugin names. It writes the SKILL.md with frontmatter filled from the hub and a skeleton body. It adds the hub manifest row, reciprocal peers, and one positive and one negative routing case. It runs the rebuild, routing check and validators, then prints only the framework-13 items that need judgment. Do the same for **`new-project.py`**. Its skill is stale today: wrong framework count, an outdated entry shape, and a duplicate `04-` number already exists. | Hand-editing 4–14 files per spoke and substituting Templater tokens by hand | Most of the authoring overhead; the body stays judgment | M |
| **M21** | **Split hub routing from hub doctrine.** A spoke load should not re-read the hub's Spoke Network, Cross-Hub and Boundary sections, because routing is already done by then. Generate the manifests (M13). Merge Domain Boundary and Cross-Links, which repeat each other 86% of the time in 56 files. Move `ds-advisor`'s 18.7 KB of foundation material into `design-foundations`, which framework 13 rule 6 already requires (needs Sean's review). | Re-reading 7–9 KB of routing prose on every spoke load | ~2k tokens per spoke load under the big hubs (INFERRED) | M |
| **M22** | Replace the 15 `fw-*` "Version Check (run on every load)" web searches with a nightly `npm view <pkg> version` comparison against `pinned_version` | A web search on every framework-skill load | One search per load | S |
| **M23** | Point prose checklists at scripts that already exist: <br>• `a11y-visual` → `a11y_audit.py` <br>• `visual-qa-*` → `qa_contrast.py` / `qa_typography.py` <br>Add a Figma naming and semantic-variable lint for `figma-ds-generation-pipeline` and `figma-component-generation`. | Checking thresholds by eye | Quality gain | S–M |
| **M24** | **Plugin copies.** Rebuild the stale `snds` plugin copies. Retire duplicate `anthropic-skills:` copies of workspace skills; 20 names appear 2–3 times in every session's skill list, and one of them carries an outdated Google Drive description. Merge the near-duplicates: `google-fonts-*` ×2, `material-symbols-*` ×3, `figma-plugin` / `figma-plugin-dev`. **Archive and merge need Sean's sign-off.** | Paying for duplicate skill descriptions in every session; picking between near-twins | ~1 KB per duplicate description per session | S–M |

### Meta — keep it from regressing

| ID | Change | Effort |
|---|---|---|
| **M25** | **A write-cost lane in `workspace-harness.py`**, with ceilings that work like the token lane's: <br>• Live handoff bytes per project <br>• SESSION-STATE bytes, with history auto-archived past a ceiling <br>• SessionStart injection bytes <br>• routing injection rate and p95 size, replayed over the corpus plus negative cases <br>• the number of "run X" instructions in injected text <br>• session-end skill bytes <br>• the count of hand-kept derived files, which should only go down <br>Land it **first**, so every wave has a before-and-after number. | M |

---

## 4. What should stay judgment (do not mechanize)

- **Stays with the agent:**
  - the session's title and summary
  - the next action and open decisions
  - the *wording* of a pending item
  - the content of a knowledge entry
  - audit verdicts and which finding matters
  - lane choice for Open Engine items
- **Stays with Sean:**
  - archive, merge and consolidation of skills (the mutation policy)
  - the employer-wall decisions
- **Still refused:** R1 from the 2026-09-11 review stands. No LLM-as-judge merge gate.
  Mechanization here means deterministic scripts, not a second model grading the first.
- **Never derived from commits:** the baton's *why*. A script may fill in "what changed". Only the
  agent knows what it was for.

---

## 5. Suggested order and the first thing each step would break

1. **B1–B10** (independent, small). Nothing downstream depends on them.
2. **M25** (write-cost lane). This sets the baseline first.
3. **M9, M12** (lowest-risk generators).
   - *First later-breaker:* `validate-workspace.py check_memory` must accept a generated file. Add
     MEMORY.md to closure `GENERATED` (`closure.py:63`) and the MCP write guard.
4. **M1 + M2 together** (session close and baton). They share the JSON.
   - *First later-breaker:* `session-status.py:375-415` parses `## Session history` headings for
     the card's project titles. It must switch to the YAML `focus` in the same change.
   - Then the Cursor adapters (`CURSOR.md`, `.cursor/rules/brain.mdc`) and `workspace_mcp.py`
     `session_end` must emit the same shape.
   - A one-time converter is needed for 19 SESSION-STATE files. Two of the largest
     (planet-lab, legion) have no Live handoff block at all.
5. **M5–M8** (hooks).
   - *First later-breaker:* the adapters' ritual text (`CLAUDE.md`, `AGENTS.md`, `brain.mdc`) must
     change in the same commit.
   - The SessionEnd ritual audit only looks for `workspace: LOADED`, so it is unaffected.
6. **M10, M11, M13**: index generation.
7. **M14–M19**: audits.
8. **M20–M24**: authoring and corpus.

## 6. How we will know it worked

- **Primary metric:** tokens per session-end (read plus written) and injected chars per prompt.
  Both come from the M25 lane, plus a transcript sample.
- **Unit:** one session.
- **Expected direction:** down.
- **Minimum effect worth keeping:**
  - session-end −50%
  - routing chars −40%
  - `/optimize` −70%
- **Duration:** the 20 sessions after each wave lands.
- **Stopping rule:** revert a wave if the quality or connections lane goes red. Also revert if a
  later session has to ask Sean for something the old handoff format would have carried. That is
  intent loss, which write-quality gate 2 forbids.

## 7. Not verified here

- Whether a long `systemMessage` renders well in the desktop app (M5). Test it before changing the
  adapters.
- The routing statistics (94%, the 29% footer share, the 38% lexical-only share) come from one
  survey's 19-transcript sample, not a harness run. M7's first step is to make them a harness
  number.
- All token savings marked `INFERRED` are bytes ÷ 4 estimates from measured sizes.
