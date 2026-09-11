# PERPLEXITY.md — Perplexity adapter

_Thin adapter over [AGENTS.md](AGENTS.md). Same contract, read order, skill loading, and
handoff as every other surface. Perplexity is not a fork and Claude is not privileged._

## How Perplexity executes the contract

1. Follow **AGENTS.md Canonical read order** (lookup registry `load_chains`, JSON routes,
   matched knowledge only — do not ingest the whole registry or `_INDEX.md`).
2. Resolve the [context profile](02-shared-references/delivery-playbooks/00-context-profiles.md)
   before any repo action.
3. Route skills via [trigger-routes.json](02-shared-references/trigger-routes.json) then
   registry triggers. Invoke [close-out](03-skills/close-out/SKILL.md) then
   [self-improve](03-skills/self-improve/SKILL.md) after producing.
4. Continuity: read the project's `SESSION-STATE.md` **Live handoff**. Perplexity often
   cannot write the vault — **surface the handoff text for Sean to paste**; do not invent
   a session-log-append protocol this contract does not have.

## Do not

- Treat Claude files (`CLAUDE.md`, `.claude/`) as a higher-rank contract.
- Duplicate folder semantics, doctrine, or write-quality gates here.
- Ingest `skills.registry.json` or `trigger-routes.md` end-to-end.

Other adapters: [CLAUDE.md](CLAUDE.md) · [CURSOR.md](CURSOR.md).
