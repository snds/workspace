---
title: Harness map — workspace core + Cursor
version: 1.0
date: 2026-08-07
surface: Cursor + workspace-core
branch: main
sha: 97bb259
agent: Cursor Grok 4.5
status: map-only — no clean applied
---

# Harness map — 2026-08-07

## 1. Boundary + evidence grades

| Field | Value |
|---|---|
| Workspace root | nearest `AGENTS.md` → `~/Projects/workspace` |
| Branch @ sha | `main` @ `97bb259` |
| Surface edition | **Workspace core** + **Cursor** |
| Model | Cursor Grok 4.5 |
| Machine | Work MBP (`CS-K746DRWXY1`) |
| Date | 2026-08-07 |

**Evidence-grade legend:** `VERIFIED` · `USER_REPORTED` · `INFERRED` · `INACCESSIBLE` · `NOT_EXPOSED` · `NOT_APPLICABLE`

This run is **read-only**. No deletions, merges, or always-on edits were applied.

---

## 2. System map

### Always-on / early load

| Control | Path / mechanism | Size (approx) | Grade |
|---|---|---|---|
| Universal contract | `AGENTS.md` | ~25 KB (~6k tok) | `VERIFIED` |
| Claude adapter (also injected into Cursor via always-applied workspace rules) | `CLAUDE.md` | ~22 KB | `VERIFIED` |
| Cursor brain | `.cursor/rules/brain.mdc` (`alwaysApply: true`) | ~3 KB | `VERIFIED` |
| Write gates rule | `.cursor/rules/01-agent-controller.mdc` (`alwaysApply: true`) | ~1 KB | `VERIFIED` |
| Filesystem protocol | `.cursor/rules/02-workspace-filesystem.mdc` (globs, not always-on) | ~1.5 KB | `VERIFIED` |
| Cursor adapter doc | `CURSOR.md` | ~4.5 KB | `VERIFIED` |
| Home beacon | `~/AGENTS.md` (workspace-doctor managed) | ~1.5 KB | `VERIFIED` |
| Hot facts | `06-context/CRITICAL_FACTS.md` | ~2 KB | `VERIFIED` |
| Role | `06-context/role-and-context.md` | ~3 KB | `VERIFIED` |
| Pending / projects | `06-context/project-context.md` | **~61 KB** | `VERIFIED` |
| Session log (post-compaction) | `06-context/session-log.md` | ~44 KB | `VERIFIED` |
| Memory index | `06-context/memory/MEMORY.md` | ~4 KB | `VERIFIED` |
| Cursor User Rules | Settings / rules UI | — | `INACCESSIBLE` as files; content **observed** this session via injection (`USER_REPORTED`/`VERIFIED` hybrid) |
| Vendor system prompt | Cursor product | — | `NOT_EXPOSED` |

**Cursor hooks** (`.cursor/hooks.json`) — `VERIFIED`:

- `preCompact` → `cursor-reassert.sh`
- `sessionEnd` → `cursor-sessionend.sh`
- `subagentStop` → `cursor-subagent-stop.sh`

**Claude Code hooks** (sibling surface; not executed this run) — `VERIFIED` present: `.claude/hooks/dispatcher.py` (SessionStart / UserPromptSubmit, incl. harness-map staleness Notice @ 30d).

### Routed load

| Control | Observation | Grade |
|---|---|---|
| Skill registry | **283** skills (39 cross-cutting · 22 foundation · 47 hub · 175 spoke) | `VERIFIED` |
| Description budget | ~194k chars across SKILL.md descriptions (avg ~684) | `VERIFIED` |
| Load chains | Precomputed in `skills.registry.json` | `VERIFIED` |
| Curated routes | `02-shared-references/trigger-routes.md` (~25 KB generated) | `VERIFIED` |
| Shared triggers | 78 phrase triggers map to >1 skill (mild; top are short domain words like `contrast`, `composition`) | `VERIFIED` |
| Cursor Task agents | `.cursor/agents/` — 5 wrappers (design-engineer, ds-advisor, lead-ui/ux, workspace-bootstrap) | `VERIFIED` |
| Claude slash skills | `.claude/skills/` — today, session-end, optimize, harness-map, mission-fit, … | `VERIFIED` |
| New on-demand skills | `harness-map`, `mission-fit` | `VERIFIED` |
| Knowledge INDEX | `08-knowledge/_INDEX.md` — routing via Triggers lists | `VERIFIED` |
| Layer-1 retrieve | `09-tools/vault-retrieve.py` (Claude dispatcher fallback; Cursor on-demand) | `VERIFIED` |

### Enforcement

| Control | Role | Grade |
|---|---|---|
| Write-quality gates | AGENTS.md + `01-agent-controller.mdc` | `VERIFIED` |
| Generators (order) | `build-related` → `build-registry` → `build-trigger-routes` | `VERIFIED` |
| Validators | `validate-integrity`, `validate-links`, `validate-capabilities`, `validate-workspace`, vault-health | `VERIFIED` |
| **Current `validate-workspace`** | **FAILED** — 9 orphans (1 memory not in MEMORY.md; 8 knowledge files not in `_INDEX.md`) | `VERIFIED` this run |
| Context-profile fail-safe | delivery-playbooks `00-context-profiles.md` | `VERIFIED` |
| Figma write gate | Claude PreToolUse (sibling surface) | `VERIFIED` path exists; `NOT_APPLICABLE` this Cursor run |
| Employer / c8 fence | standing rule + Open Engine movement-only | `VERIFIED` |

### Authority + done

| Control | Grade |
|---|---|
| May / ask / never (profiles, no auto-commit employer, Figma real components) | `VERIFIED` |
| Definition of done: Proofboard, Live handoff, Open Engine receipts, CI | `VERIFIED` |
| Session-end `Evidence:` line (consequential done) | `VERIFIED` in `/session-end` skill text |
| Unattended runner tool-scoping (`--tools` / `--disallowed-tools`) | Still open precondition — `USER_REPORTED` / baton |

### Receipts / run evidence

| Control | Grade |
|---|---|
| Live handoff (`07-projects/*/SESSION-STATE.md`) | `VERIFIED` |
| Session fragments → compact → `session-log.md` | `VERIFIED` (compaction landed this session) |
| Side-chat inbox | Mechanism `VERIFIED`; no pending inbox this turn |
| Open Engine ledger | Present; ritual prove-out still queued | `INFERRED` from baton |
| Full run map (available → eligible → shown → consulted → acted → checked → accepted) | **`NOT_EXPOSED`** on Cursor — no machine-readable eligibility trace for this chat |

---

## 3. Protect vs drag

### Protects

- Single portable contract (`AGENTS.md`) + write-quality gates + archive-not-delete.
- Registry `load_chains` + curated trigger-routes (foundation-first routing without guessing).
- Hard validators / generator order (binary contracts in machinery).
- Context profiles (employer vs personal-solo) and c8 movement-only fence.
- Thin ritual hooks for harness staleness + session-end Evidence (skills stay on-demand).
- Cursor compact/sessionEnd hooks reassert continuity.

### Drag

- **Always-on duplication:** Cursor injects `AGENTS.md` + `CLAUDE.md` + `brain.mdc` + controller + User Rules/beacon — same law restated. Correct copies still cost tokens every turn.
- **`project-context.md` (~61 KB)** still dominates early context; known ~21.6k-token session-start problem; Open Engine migration deferred.
- **Index orphans** make `validate-workspace` red — enforcement exists but the vault currently fails it (8 design knowledge files + 1 memory).
- **Skill catalog pressure:** 283 skills / ~194k description chars — fine when routed; risky if any surface dumps the full catalog into context.
- **CLAUDE.md ritual vs `brain.mdc`:** Claude format is documented as overridden on Cursor, but the full CLAUDE.md body still rides along in Cursor always-applied rules.
- **AI crud risk:** corrections that outlived failures — especially duplicated standing-law copies and unindexed knowledge residue.

---

## 4. Numbered recommendations

Approve by number before any clean. Map-only until then.

### 1 — Index orphans so workspace validation is green again
- **Disposition:** Turn into check (already is a check — restore green) + Keep the validator.
- **Owner:** `08-knowledge/_INDEX.md`, `06-context/memory/MEMORY.md`
- **Rationale:** `validate-workspace` failed this run with 9 listing errors (memory `feedback-cross-surface-token-aligned.md`; knowledge: `brand-text-vs-fill`, four density-dashboard/row notes, `figma-shadow-modes`, `interaction-state-semantics`, `stickersheet-inventory-plan`). Enforcement that permanently fails becomes noise.
- **Risk:** Low — additive index lines; may need brief blurbs.
- **Rollback:** Revert INDEX/MEMORY edits.

### 2 — Shrink session-start: head `project-context` or migrate Active → Open Engine
- **Disposition:** One home (queue substance lives in engine pointers) + Load later (full pending list only when asked).
- **Owner:** `06-context/project-context.md` + `06-context/open-engine/`
- **Rationale:** Largest verified early-load drag (~61 KB). Baton already names this; harness map confirms it as structural, not episodic.
- **Risk:** Medium — wrong migration loses pending intent; must keep `^pc-NN` anchors.
- **Rollback:** Restore project-context from git; engine issues remain movement-only.

### 3 — Deduplicate Cursor always-on: point, don’t paste
- **Disposition:** One home — `AGENTS.md` owns standing law; adapters are thin invoke/pointer.
- **Owner:** Cursor User Rules / always-applied injection strategy; optionally trim what Cursor injects from `CLAUDE.md` on Cursor sessions (`brain.mdc` already claims override).
- **Rationale:** Multiple correct copies of the contract are the primary token-crud surface on this edition.
- **Risk:** Medium — over-thinning can drop a gate a surface relied on.
- **Rollback:** Restore prior rule text / adapter size.

### 4 — Keep harness-map / mission-fit on-demand (do not always-load)
- **Disposition:** Keep
- **Owner:** `03-skills/harness-map`, `03-skills/mission-fit` + stamp/Notice hooks
- **Rationale:** Matches token-frugality + Nate “map before clean / don’t always-run full audit.” Stamp now exists; Notice only after >30d.
- **Risk:** None if left on-demand.
- **Rollback:** N/A

### 5 — Probation: full skill-description budget on surfaces that list all skills
- **Disposition:** Probation
- **Owner:** marketplace / plugin packaging (`build-local-skill-plugin.py`), Cursor agent skill lists
- **Rationale:** ~194k desc chars is fine for registry lookup; if a surface truncates or floods context with the catalog, quality drops without an obvious local culprit.
- **Risk:** Low to leave; measure on next plugin publish.
- **Rollback:** N/A until a change is made.

### 6 — Turn unattended-runner tool scoping into a hard check before any schedule
- **Disposition:** Turn into check
- **Owner:** Open Engine runner docs + Claude/`claude` CLI flags; baton precondition
- **Rationale:** Authority widening without tool fence = remote-execution class risk (already in knowledge `agent-work-queue-boundaries`).
- **Risk:** High if ignored; low if blocked until check exists.
- **Rollback:** Keep runners manual.

### 7 — Load later: specialist frameworks (#05–#11) stay behind QA/delivery triggers
- **Disposition:** Load later / Keep
- **Owner:** `01-frameworks/` + curated routes (`audit`/`review` → fw06, etc.)
- **Rationale:** Compact execution core is Outcome / Context / Authority / Acceptance; long protocols must not ride every Cursor turn.
- **Risk:** Low.
- **Rollback:** N/A

### 8 — Retire only after probation: duplicate trigger synonyms that add no new load_chain
- **Disposition:** Probation → possible One home in `trigger-routes.json`
- **Owner:** `02-shared-references/trigger-routes.json`
- **Rationale:** Many curated rows intentionally alias the same load (good UX). Cull only proven zero-value duplicates after a month of Notice-quiet operation — not “because long.”
- **Risk:** Medium if aggressive (missed triggers).
- **Rollback:** Restore JSON + regenerate md.

---

## 5. Explicit gaps

| Gap | Grade |
|---|---|
| Vendor Cursor system prompt / hidden ranking | `NOT_EXPOSED` |
| Machine-readable run map for this chat | `NOT_EXPOSED` |
| Exact Cursor User Rules file on disk | `INACCESSIBLE` (injected; not a workspace file) |
| Claude dispatcher runtime behavior this session | `NOT_APPLICABLE` (Cursor edition) |
| Linear Open Engine live queue counts | Not polled this run — omit rather than guess |

---

## 6. Suggested verification after approved changes

1. `python3 09-tools/build-related.py && python3 09-tools/build-registry.py && python3 09-tools/build-trigger-routes.py`
2. `python3 09-tools/validate-integrity.py && python3 09-tools/validate-links.py && python3 09-tools/validate-workspace.py`
3. Cold Cursor session: confirm ritual still shows `workspace: LOADED` and Notices behave with this stamp.
4. Optional follow-up: [[mission-fit]] on one job that recently claimed “done” without Evidence.

---

## Compact execution core (preserve)

1. **Outcome** — portable multi-agent continuity without private memory; green validators before commit.
2. **Context** — Live handoff + CRITICAL_FACTS + routed skills/knowledge (not the whole vault).
3. **Authority** — profiles; employer fence; Figma real components; ask before destructive archive.
4. **Acceptance** — validators + Proofboard/Evidence when consequential; Open Engine receipts when claimable work must survive the chat.

Specialist method stays behind triggers. Binary guarantees stay in hooks/validators.
