---
tags: [shared-reference, automation, recipe, opt-in]
created: 2026-07-23
status: active
---

# Nightly Maintenance Recipe (opt-in)

_A documented, **opt-in** scheduled-agent routine that keeps the vault healthy without manual
effort. Not wired on by default — Sean enables it deliberately (per-machine, or as a cloud
routine). Borrowed from `obsidian-second-brain`'s nightly close-day pattern during the
bootstrap-generator feedback pass (2026-07-23)._

## For future agent
- **TL;DR:** an optional cron/routine that folds sessions, heals the graph, rebuilds indexes, and
  commits — so a fresh morning session opens on a clean, current vault.
- **As of:** 2026-09 · **Status:** current (opt-in; not enabled by default)

## What it does (in order)

**Executable form: `python3 09-tools/nightly.py`** (`--dry-run` to see the plan, `--commit` to
commit mechanical updates). The steps below are the doctrine that entrypoint implements —
read them to change the recipe, run the CLI to execute it. Still nothing scheduled.

**Regeneration is one command:** `python3 09-tools/nightly.py --phases rebuild`. It runs the
generator fixpoint in order — build-registry → build-related → build-registry again (skipped
when build-related wrote nothing) → build-trigger-routes — so no agent hand-sequences it.

| Flag | What it does |
|---|---|
| `--phases fold,rebuild,verify,watch,commit` | Choose phases (default: all but `commit`). `commit` = `--commit`. |
| `--check` | Generators in `--check` mode. Writes nothing; exit 1 on drift. |
| `--scope all\|staged\|session:SID\|range:R` | What counts as "yours". A written path with unstaged edits outside the scope is **foreign**: exit 4, never staged. |
| `--budget S` · `--step-timeout S` | Total and per-step limits (per step 15 s; verify 180 s). A timeout or spent budget is SKIPPED, exit 3, never green. |
| `--json` | One entry per step with `written[]` (from sha256 snapshots), plus `written`, `foreign`, `status`, `fix`. |
| `--lane pre-commit` | Stateless git-hook lane: checks the staged index; on drift prints exactly two fix lines. Installed by Sean in wave 1 (H18), not before. |
| `--self-test` | Fixtures: fixpoint, scope, foreign edits, timeouts, budget, X1 replay, timed SessionEnd. |

Exit codes: 0 clean · 1 FAIL/drift · 2 could not run · 3 SKIPPED · 4 refused. `commit` refuses
unless the run is clean, and stages only the paths the run wrote. The Claude SessionEnd hook
uses the same command (`--phases rebuild --scope session:<sid> --json --budget B`) as a
budgeted accelerator (≤ 55 s total); CI stays the backstop for every surface.

1. **Fold sessions** — `python3 09-tools/compact-sessions.py` (merge `06-context/sessions/` fragments
   into the log; idempotent, conflict-free across machines).
2. **Graph hygiene** — `python3 09-tools/vault-health.py` (report orphans, `#stale`/aging claims,
   dangling typed edges) + `python3 09-tools/validate-links.py` (skill graph). Surface findings; do
   **not** auto-fix content — that needs judgment (`/health` with sign-off).
3. **Rebuild indexes** — `python3 09-tools/nightly.py --phases rebuild` (the fixpoint above), then
   `evaluate-skill-routing.py` → `validate-integrity.py` →
   `validate-links.py` → `validate-workspace.py` (the standard chain; see framework #08).
3b. **DS source freshness (optional)** — `python3 09-tools/ds-source-watch.py --check`. If P1,
   leave a pointer; do **not** `--fetch` from nightly (network + judgment).
3c. **First-wave detectors** — `python3 09-tools/skill-loadset.py --self-test` →
   `python3 09-tools/close-out-dispatch.py --check` →
   `python3 09-tools/validate-layer0-schema.py --check` →
   `python3 09-tools/session-status.py --check` →
   `python3 09-tools/check-secrets.py`. Report; do not invent skills.
4. **Commit + sync** — if clean, commit the mechanical updates and push (the session/auto-commit model
   already does this; the routine just guarantees a daily floor).

## How to enable

- **Cloud routine:** use the `/schedule` skill to create a daily cron agent that runs the steps above
  and posts a short digest (what it folded, what `vault-health` flagged). Keep it **report-first** —
  it should *never* auto-edit note content or auto-resolve `#stale` claims; those are `/health` +
  sign-off. Safe to automate: compaction, index rebuilds, commits.
- **Local:** a launchd/cron job invoking the same steps, gated on the machine being the canonical one.

## Guardrails

- **Report, don't rewrite notes.** Automation folds/rebuilds/commits; it does not make epistemic judgments
  (refuting a claim, archiving an orphan). Those wait for `/health` + judgment. Mechanical P0
  graph heals (rebuild indexes, registry) are already in step 3. Inventing skills is **not**
  nightly's job — that is [[self-improve]] during ordinary sessions.
  The judgment-heavy cousin is `/optimize` (seven-surface system ECC). This recipe does not
  replace it.
- **Respect the walls.** Never touch `06-context/personal.md` beyond git; never push employer content.
- **Idempotent + non-lossy.** Every step is safe to re-run; nothing here deletes a note (archive-only).
