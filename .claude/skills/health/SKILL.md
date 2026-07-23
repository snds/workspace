---
name: health
description: Graph hygiene for the vault. Runs the deterministic validators (vault-health.py for the epistemic/freshness layer, validate-links.py for the skill graph) and reports orphan notes, #stale + aging claims, and dangling typed edges. Faster and narrower than /optimize (which is the full brain audit). Invoked as /health or triggered by "check the graph", "vault health", "find orphans", "find stale notes".
---

# /health — vault graph hygiene

## When to invoke

- User runs `/health`, or says "check the graph", "vault health", "find orphans/stale notes"
- As a quick pre-commit or pre-`/optimize` hygiene pass
- Periodically alongside `/optimize` (health is the narrow, deterministic graph check; `/optimize`
  is the broad, judgment-heavy brain audit)

## Why this exists

The vault rots quietly: notes lose their inbound links and become unreachable; dated facts age
past their horizon; `relations:` edges point at notes that moved or were renamed. This is the
deterministic check for that decay — the input-time twin of `/optimize`. It complements, not
replaces, `validate-links.py` (which owns the **skill** `## Related` graph).

## Protocol

### Step 1 — Run the validators (deterministic; no judgment)

```bash
python3 09-tools/vault-health.py       # epistemic layer: orphans · #stale · aging · dangling relations
python3 09-tools/validate-links.py     # skill graph: dangling / reciprocity / foundation
```

`vault-health.py` scopes to `06-context/memory`, `08-knowledge`, `02-shared-references` and
exits non-zero on any **dangling typed edge** (an error); `#stale`, aging `as of` dates, and
orphans are warnings. Add `--strict` to fail on warnings too. Conventions it enforces live in
[vault-graph-conventions](../../../02-shared-references/vault-graph-conventions.md) and
[epistemic-standards](../../../02-shared-references/epistemic-standards.md) §2 (the freshness rule).

### Step 2 — Triage the findings (this is where judgment enters)

For each finding, decide the disposition — don't just relay the script output:

- **Dangling typed edge** (error) → the target was renamed/removed. Fix the `relations:` link, or
  drop it. If the target was *superseded*, the edge should probably be `refutes` pointing at the
  replacement.
- **`#stale` / aging claim** → re-verify the fact. If still true, refresh the `as of` date; if
  wrong, `refutes` it from the newer note and mark the old one `status: superseded`; if unknowable,
  archive it.
- **Orphan note** → either it genuinely belongs (add an inbound `[[wikilink]]` from the natural
  parent — a MOC, a framework, an `_INDEX`), or it's dead (move to an `_archive/` subfolder — never
  delete). A shared-reference reached only via markdown-path links from a framework is *not* an
  orphan (the script counts both link styles).

### Step 3 — Apply only with sign-off, and log

Present the triaged list; apply fixes only after Sean agrees (same discipline as `/optimize`).
Append a one-line entry to `06-context/audit-log.md`:
`YYYY-MM-DD /health — N orphans, M stale, K dangling; {what was fixed / deferred}`.

For anything out of scope to fix now, prefer a background task (`spawn_task`) over silently
carrying it forward.

## Boundary

- Health is **deterministic graph hygiene**, not a content audit. Contradictions of *meaning*,
  consolidation, and convention drift are `/optimize`'s job.
- Never delete a note — archive it. Never rewrite a claim's history — `refutes` it forward.
