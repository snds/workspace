# PERPLEXITY.md — Perplexity adapter

_Thin adapter over [AGENTS.md](AGENTS.md). Same contract, read order, skill loading, and
handoff as every other surface. Perplexity is not a fork and Claude is not privileged._

## How Perplexity executes the contract

1. Follow **AGENTS.md Canonical read order**. On a new session, emit
   `python3 09-tools/session-status.py --surface Perplexity` first (or RULES-ONLY + pasted pending).
   Compute the load set with `python3 09-tools/skill-loadset.py "…"` — do not ingest the registry.
2. Resolve the [context profile](02-shared-references/delivery-playbooks/00-context-profiles.md)
   before any repo action.
3. Route skills via [trigger-routes.json](02-shared-references/trigger-routes.json) then
   the loadset CLI. After producing, run
   `python3 09-tools/close-out-dispatch.py --from-prompt "…" --run` then
   [close-out](03-skills/close-out/SKILL.md) / [self-improve](03-skills/self-improve/SKILL.md).
   SKIP ≠ verified.
4. Continuity: read the project's `SESSION-STATE.md` **Live handoff**. Perplexity often
   cannot write the vault — **surface the handoff text for Sean to paste**; do not invent
   a session-log-append protocol this contract does not have. Canvas/Artifact/HTML panels
   are not durable — emit a copy-ready block plus a suggested vault path.

## Do not

- Treat Claude files (`CLAUDE.md`, `.claude/`) as a higher-rank contract.
- Duplicate folder semantics, doctrine, or write-quality gates here.
- Ingest `skills.registry.json` or `trigger-routes.md` end-to-end.

Other adapters: [CLAUDE.md](CLAUDE.md) · [CURSOR.md](CURSOR.md).
