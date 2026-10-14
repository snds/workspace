# SESSION-STATE — Switchyard

_Last updated: 2026-10-14 — checkpoint (plan set drafted)_

---

## Current state (rewritten atomically — no stale fields)

### 🤝 Live handoff (the baton)

- **TL;DR (for future agent)**: Switchyard is a planned Mac + Windows background app that routes the right login (git, `gh`, SSH, CLIs, agent MCP) per project from rules. Planning only; nothing built.
- **Current focus**: Sean reviews the plan set in `plan/` and answers the three open questions in the README.
- **Working set**: `07-projects/26-switchyard/plan/*.md` (source). `05-artifacts/active/switchyard-plan_v1.0_2026-10-14.html` (generated readable copy).
- **Last action**: Wrote the plan set: overview, systems, integrations, how it works, security, Vaultwarden, implementation plan, commercial path and decision log. Published the readable copy. By Claude Opus 5.5 · Claude Code · Work MBP.
- **Next action**: After Sean's go, run Phase 0. Create `~/Projects/switchyard` and `snds/switchyard`, move `plan/` to `docs/`, set up CI and signing, and run spikes SP1–SP6 (see `plan/06-implementation-plan.md`). Track V1 (deploy Vaultwarden) can start at any time.
- **Open decisions**: Windows PC personal-only? Meaning of "account thresholds" (assumed: per-account limits). Employer IT policy check before Phase 2 on the Work MBP.
- **Blocked on**: Sean's review.
- **In-flight / do-not-touch**: none.
- **Agent thread**: Claude/Claude Code (2026-10-14): feasibility, then one-page proposal, then full plan set.

### Environment
- **Context profile**: `personal-solo`
- **Machine**: Work MacBook Pro (planning only; the code will be personal and live in `~/Projects/switchyard`)
- **Workspace root**: the checkout containing `AGENTS.md`
- **Project root**: `07-projects/26-switchyard/` (vault); repo not created

### VCS state
- **Branch**: workspace `main` (vault docs only)
- **Repo**: none yet

---

## History (append-only)

- **2026-10-14** — Project created. Feasibility review, then a one-page proposal (artifact `switchyard-proposal_v1.0`). Sean chose Vaultwarden on Unraid over 1Password, required Windows and both personal and employer identities, and set a product-grade security bar with an optional commercial path (GUI workspace generator over `wsx`). Plan set written in `plan/`.
