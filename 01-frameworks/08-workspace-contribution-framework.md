# 08 — Workspace Contribution Framework

_Answers: **How, when, where, what, and why** do I edit or add to this workspace — at every layer?_

This is the governance spine for changing the workspace itself. It is **LLM-agnostic**: any agent
(or human) follows it identically. It sits above the skills and is portable — it assumes only a git
checkout and a filesystem. Read it before writing anything that isn't a project deliverable.

The one rule that precedes all others: **consult the routing map first**
([[workspace-ontology]] → "where does this belong?"). Most contribution mistakes are *placement*
mistakes — the right content in the wrong layer. Get the layer right, then follow that layer's rules
below.

---

## Universal principles (the WHY)

1. **Git is the source of truth.** Every change is a reviewable diff. No hidden state, no
   out-of-band sync. If it matters, it's committed.
2. **Additive over destructive.** Prefer adding/extending to replacing. Never delete — **archive**
   with provenance (see §Archive). Renames are destructive (they break loader paths + wikilinks):
   avoid; add `aliases` instead.
3. **One source, generated views.** Where a machine-readable artifact exists (`skills.registry.json`),
   the human-authored side (frontmatter) is canonical and the artifact is generated. Never hand-edit
   a generated file.
4. **Portable-first.** Nothing you add may require one vendor, device, or cloud drive. If a mechanism
   only works in one tool, it belongs in that tool's adapter, not the shared layers.
5. **Smallest correct change.** Right altitude, right layer, minimal blast radius, reviewable in one sitting.
6. **Token frugality (a #1 priority).** The workspace must never cost more tokens than the value it adds.
   Structure state so it's read cheaply — bounded, append-only logs that **archive** rather than grow (never
   a whole growing file); load skills only on trigger. Be especially terse in **auto-loaded** files (the
   contract, `CLAUDE.md`, `.cursor` rules): every line there is a recurring per-session cost, so earn it.

---

## Write-quality gates (every write, every agent)

**Any capable agent may write here — not just Claude.** Open participation is safe because correctness is
enforced by deterministic validation + CI, not by model identity. Every write — by any model, on any surface,
including a mid-task dynamic model swap in Cursor — must clear four gates:

1. **Quality** — meets or exceeds the workspace documentation standard: complete (no stubs/TODOs/unfilled
   template tokens), in the file's established structure + voice, valid frontmatter. (Frameworks 05 + 06.)
2. **Intent integrity (no loss)** — understand the file's intent before editing; afterward, verify no data,
   context, or intent was silently dropped. Preserve meaning unless deliberately superseding (gate 4).
3. **Cross-link continuity** — a change to one file updates **every** related/cross-linked file (frontmatter
   edges, `## Related`, foundations, MOCs, knowledge refs, prose), then regenerates + passes the validators.
   A change that orphans a reference is incomplete.
4. **No zombies — archive-or-regenerate** — the *only* sanctioned path for intent loss: if a change is so
   dramatic the old file no longer makes sense, archive it with provenance, generate the replacement, and
   repoint all cross-links. Never leave an orphaned, superseded-but-live, half-updated, or stub file.

Run before commit (CI mirrors these): `build-related.py` → `build-registry.py` → `validate-integrity.py`
→ `validate-links.py` → `validate-workspace.py`. Gate 2 is partly semantic — the authoring agent + PR review
own it; the rest is machine-checked. Mirrored, compressed, in [[AGENTS]] → "Write-quality gates".

**Why `build-related` runs first.** It rewrites the `## Related` block *inside* SKILL.md files;
`build-registry` records a content hash per skill. Build the registry first and any file `build-related`
subsequently touches carries a stale hash, so the committed registry is already drifted — CI fails with
`registry-drift` and `capability-validator` even though the chain was "run as documented". The coupling is
one-directional (`build-related` writes what `build-registry` reads), so ordering alone closes it. If a
future generator also mutates SKILL.md content, it belongs *before* `build-registry` too — or the chain
needs a run-to-fixpoint loop. Discovered 2026-07-20 when a Related-block refresh to `found-color`,
`infod-encoding-theory` and `ux-component-library` drifted exactly those three hashes.

### Graph & freshness conventions (knowledge/memory notes)

Two lightweight conventions keep the **epistemic** graph (knowledge entries + `memory/` — distinct
from the skill `## Related` graph) connected and trustworthy. Full spec:
[[vault-graph-conventions]] and [[epistemic-standards]] §2.

- **Typed edges** — a `relations:` frontmatter map (`builds-on` / `relates-to` / `contradicts` /
  `refutes` / `exemplifies`) on knowledge/decision notes. `refutes` is how a superseded claim gets
  *marked* superseded, not silently left live. (Skills keep their own richer `## Related` graph — don't cross them.)
- **Freshness** — every durable claim is *timeless* / *dated* (`as of YYYY-MM`) / *pointer*; past-horizon
  or unverifiable → `#stale`.
- **Retrieval preamble** — durable notes open with a `## For future agent` block (TL;DR + key claims + as-of).
- **Check it:** `/health` (→ `09-tools/vault-health.py`) reports orphans, `#stale`/aging claims, and
  dangling typed edges. Run it periodically and inside `/optimize`; it can be automated via the
  opt-in [[nightly-maintenance-recipe]].

---

## The routing map (the WHERE)

Canonical copy + rationale in [[workspace-ontology]]. Compressed here for quick reference:

| The thing is… | Layer | 
|---|---|
| Active project state / pending work | `06-context/project-context.md` + project `SESSION-STATE.md` |
| What happened this session | `06-context/session-log.md` |
| A durable, non-project fact about Sean's world / the working relationship | `06-context/memory/` |
| A stable, deliberately set behavioral default | `04-preferences/user-preferences.md` |
| A validated domain insight learned from real work | `08-knowledge/<domain>/` |
| A reusable "when X, do Y" capability | `03-skills/<name>/SKILL.md` |
| A cross-cutting method / lens / operating model | `01-frameworks/` |
| A durable standard / spec / vocabulary | `02-shared-references/` |
| Why a structural choice was made | `06-context/memory/` (`type: decision`) |
| A generated deliverable | `05-artifacts/` |
| Something being retired | `_archive/` + `ARCHIVE-LOG.md` |

---

## Per-layer rules (the WHAT, WHEN, HOW)

Each layer: what belongs · when to add vs. extend · what never goes here · the mechanics.

### `00-bootstrap/` — orientation + setup
- **Belongs:** how the workspace is set up and entered; installer + adapters' setup docs.
- **Add vs. extend:** extend existing docs; a new bootstrap doc only for a genuinely new entry path.
- **Never:** vendor-specific assumptions baked in as universal; Drive/mount path logic (root is resolved by the `AGENTS.md` marker).
- **How:** plain markdown; keep it thin and link out.

### `01-frameworks/` — operating models (this layer)
- **Belongs:** portable, domain-agnostic methods that govern *how* work is done or decided.
- **Add vs. extend:** a **new framework only if 3+ areas consume it** and no existing framework fits. Otherwise extend one. Register it in `00-README.md` and update the count.
- **Never:** domain how-to (that's a skill); one-off project rules (project-local).
- **How:** number it; add to the README table + reading order.

### `02-shared-references/` — standards + vocabulary
- **Belongs:** durable specs, standards, the ontology/routing map, the frontmatter spec.
- **Add vs. extend:** extend a standard in place; a new file for a genuinely new standard.
- **Never:** anything that changes frequently (that's context/memory).
- **How:** additive; if it defines vocabulary, link it from [[workspace-ontology]].

### `03-skills/` — capabilities
- **Belongs:** reusable "when X, do Y." One concern per skill.
- **Add vs. extend:** extend an existing skill if the need is within its domain; add a spoke under the
  right hub if it's a new specialty; add a foundation **only** when 3+ sibling hubs re-derive a shared
  principle. Decide tier (`foundation`/`hub`/`spoke`/`cross-cutting`) up front.
- **Never:** rename a `SKILL.md` file/dir (add `aliases`); duplicate a skill per agent (extend
  frontmatter); restate in a spoke the principle its foundation owns.
- **How:** author from `00-bootstrap/templates/skill.md` (frontmatter v2 + typed `## Related`); then
  `python3 09-tools/build-registry.py`; ensure cross-links are reciprocal. CI gates both.
- **External tools:** if a skill needs an MCP server or CLI, declare `requires: [<capability-id>]` and
  register the capability in `02-shared-references/capability-registry.md` (detection + install +
  fallback). Don't hard-code tool paths or install steps in the skill. The agent **preflights** the
  capability before use ([[AGENTS]] → "Capability preflight") and degrades/blocks/routes if it's
  absent on the current surface — so the skill stays portable across surfaces that may or may not have
  the tool. `09-tools/validate-capabilities.py` enforces the contract (no dangling ids, reciprocity).

### `04-preferences/` — behavioral defaults
- **Belongs:** stable, deliberately chosen defaults — tone, format, terminology, conventions.
- **When:** **only on an explicit user signal** ("from now on…", "I prefer…"). Never infer a preference from a single instance.
- **Never:** situational guidance/corrections (that's `memory`, `type: feedback`); project facts.
- **How:** edit `user-preferences.md`; keep entries terse and rule-shaped.

### `06-context/` — operational state
- **Belongs:** `role-and-context` (who Sean is), `project-context` (active projects + pending),
  `session-log` (append-only history), `artifact-registry` (structural file index), `relational-context`.
- **When:** project/session state changes; at session end.
- **Never:** durable non-project facts (→ `memory/`); domain insight (→ `knowledge`).
- **How:** append session blocks newest-first; keep `project-context` the authoritative pending list.

### `06-context/memory/` — durable non-project memory (see §Memory)
### `08-knowledge/` — learned domain insight
- **Belongs:** "here's what we found out about X from real work" — validated patterns, working theories, research synthesis. Domain-scoped.
- **When:** a session produces a durable insight that will matter again. Propose writing it.
- **Never:** how-to procedures (that's a skill); volatile state.
- **How:** entry in the right domain folder + register in `_INDEX.md`; cross-link with wikilinks.

### `07-projects/` — project workspaces
- **Belongs:** per-project deliverables, local context, `SESSION-STATE.md`.
- **Never:** workspace-global policy (push that up to frameworks/shared-references).
- **How:** scaffold via the project template; keep local context local.
- **Workspace-work project home (2026-07-09):** sessions whose *subject is the workspace
  itself* (validation, fix, migration, infrastructure sessions) use the standing
  `07-projects/19-workspace-brain/` — SESSION-STATE + Live handoff like any project — or
  explicitly declare "no project home — session-log only" in their first checkpoint.
  Workspace sessions without either have no continuity carrier between agents.

### `05-artifacts/` — generated outputs
- **How:** versioned `context_descriptor_vN.N_YYYY-MM-DD.ext`; never overwrite — increment.

### `09-tools/` — automation
- **Belongs:** portable, stdlib-first scripts/generators/validators.
- **Never:** a tool that only one vendor can run as a shared dependency.

### Root files + MOCs + adapters
- Root `_*.md` are Obsidian navigation (MOCs) — keep link-only, Dataview-driven. `AGENTS.md` is the
  universal contract (edit deliberately). `CLAUDE.md`/`CURSOR.md`/`PERPLEXITY.md` are **thin adapters**
  — only how that tool executes the contract; never logic the contract lacks.

---

## Memory protocol (`06-context/memory/`)

Durable facts about Sean's world and the working relationship that aren't project state, aren't domain
how-to, and aren't a deliberate preference. Generalizes the agent-voiced `relational-context.md` into a
typed, portable store any agent reads and writes.

- **When to store:** the fact is **durable** (true across sessions), **non-project**, and **not
  derivable** from the repo or git history. If re-reading the repo would tell you, don't store it.
- **What NOT to store:** project status (→ `project-context`), session events (→ `session-log`), domain
  patterns (→ `knowledge`), deliberate behavioral defaults (→ `preferences`).
- **How:** one fact per file in `06-context/memory/`, frontmatter `type` (`fact`|`feedback`|`reference`|
  `decision`), `description`, `created`, `confidence`; body holds the fact and links related memories
  with `[[ ]]`. Add a one-line pointer to `MEMORY.md` (the index loaded at session start). Template:
  `06-context/memory/_template.md`.
- **Before adding:** check `MEMORY.md` for an existing entry to extend rather than duplicate. Delete
  (archive) memories that turn out wrong.

---

## Archive protocol (`_archive/`)

Nothing is deleted. Retiring a file means moving it to `_archive/` **with provenance**, so a future
reader knows why it's gone and where the live version is.

1. **Move** the file into `_archive/` (mirror its original path under `_archive/` when helpful).
2. **Frontmatter** on the archived file: `archived: <YYYY-MM-DD>`, `reason:`, `superseded_by:` (path or
   `[[link]]`, or `none`), `original_path:`.
3. **Ledger:** append one row to `_archive/ARCHIVE-LOG.md`:
   `original_path → archive_path · date · reason · superseded_by`.
4. **Tombstone:** if external files or links may still point at the original path, leave a 2-line stub
   there: `> Archived <date> → see [[canonical]]`. Otherwise omit.

CI (`archive-provenance`) fails if a file under `_archive/` has no matching `ARCHIVE-LOG.md` entry.

---

## Portable session protocol (tool-neutral)

How any agent opens and closes a working session here, with **no dependency on tool hooks**. A tool
adapter (e.g. a Claude hook) may automate this, but the protocol is the contract.

**Session start — read (and inherit the thread), frugally:**
1. `llms.txt` → `AGENTS.md` (contract) → `03-skills/skills.registry.json` (skill graph).
2. `06-context/`: `role-and-context`, `project-context` (head), **head of `session-log`** (it's bounded;
   old blocks are in `session-log-archive.md`, read only on demand), `memory/MEMORY.md`. Never read a whole
   growing log — token frugality is a #1 priority.
3. The active project's `SESSION-STATE.md` — **read the Live handoff block first**; you now hold the same
   context the previous agent had. Identify yourself (Agent · Surface · Machine) for attribution.

**During — work the shared state.** Compute the skill load set via the precedence algorithm (`AGENTS.md`).
Keep the active project's **Live handoff block current** as focus/working-set/decisions change — it is the
baton. Record durable insights/facts in the moment (knowledge/memory), not just at the end.

**On handoff / pause (mid-project, not just at the end) — pass the baton:**
1. Rewrite the **Live handoff block** atomically: current focus, working set, last action (attributed),
   next action, open decisions, blocked-on, in-flight/do-not-touch; prepend an Agent-thread line.
2. Write a session block as a **fragment** (`06-context/sessions/<id>.md` with a `SessionID:` line) if
   meaningful work landed — not a direct append to `session-log.md`. Compaction folds it in.
3. Commit so the next agent — on any tool — inherits an unbroken thread. This is what makes a multi-agent
   project one contract instead of N. See [[AGENTS]] → "Multi-agent continuity & handoff".

**Session end — write:**
1. Write your session block as a **fragment** in `06-context/sessions/` (a disjoint file per session,
   stamped Agent · Surface · Machine, with a `SessionID:` line). Disjoint fragments never collide across
   concurrent sessions/machines/surfaces; compaction folds them into `session-log.md` and archives old
   blocks. **Do not hand-edit `session-log.md`** (append-only, `merge=union`, bounded by archival).
2. Apply any project status / pending changes to `06-context/project-context.md`.
3. Update the active project's `SESSION-STATE.md` (incl. the Live handoff block).
4. If a generated artifact changed (frontmatter edited), regenerate `skills.registry.json` + Related blocks.
5. Commit + push reviewable diffs.

**Concurrent agents.** If two agents touched the same project in parallel, run the reconcile protocol to
merge their session blocks + handoff state into one thread; flag genuine conflicts rather than overwriting.

---

## When in doubt

- Unsure which layer? → routing map, then ask the user only if still ambiguous.
- Unsure add vs. extend? → extend, unless it's a genuinely new concern.
- Unsure whether to keep something? → archive with provenance; never delete.
- Unsure if it's portable? → if it needs one tool, put it in that tool's adapter, not a shared layer.
