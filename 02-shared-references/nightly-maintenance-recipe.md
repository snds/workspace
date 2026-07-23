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
- **As of:** 2026-07 · **Status:** current (opt-in; not enabled by default)

## What it does (in order)

1. **Fold sessions** — `python3 09-tools/compact-sessions.py` (merge `06-context/sessions/` fragments
   into the log; idempotent, conflict-free across machines).
2. **Graph hygiene** — `python3 09-tools/vault-health.py` (report orphans, `#stale`/aging claims,
   dangling typed edges) + `python3 09-tools/validate-links.py` (skill graph). Surface findings; do
   **not** auto-fix content — that needs judgment (`/health` with sign-off).
3. **Rebuild indexes** — `build-related.py` → `build-registry.py` → `validate-integrity.py` →
   `validate-links.py` → `validate-workspace.py` (the standard chain; order matters — see framework #08).
4. **Commit + sync** — if clean, commit the mechanical updates and push (the session/auto-commit model
   already does this; the routine just guarantees a daily floor).

## How to enable

- **Cloud routine:** use the `/schedule` skill to create a daily cron agent that runs the steps above
  and posts a short digest (what it folded, what `vault-health` flagged). Keep it **report-first** —
  it should *never* auto-edit note content or auto-resolve `#stale` claims; those are `/health` +
  sign-off. Safe to automate: compaction, index rebuilds, commits.
- **Local:** a launchd/cron job invoking the same steps, gated on the machine being the canonical one.

## Guardrails

- **Report, don't rewrite.** Automation folds/rebuilds/commits; it does not make epistemic judgments
  (refuting a claim, archiving an orphan). Those wait for a human-in-the-loop `/health` pass.
- **Respect the walls.** Never touch `06-context/personal.md` beyond git; never push employer content.
- **Idempotent + non-lossy.** Every step is safe to re-run; nothing here deletes a note (archive-only).
