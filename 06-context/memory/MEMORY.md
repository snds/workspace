# Memory — Index

Durable, **non-project** facts about Sean's world and the working relationship. Loaded at session start.
One line per memory. For when/how/why to write here, see [[08-workspace-contribution-framework]]
(Memory protocol); for what belongs here vs. knowledge / context / preferences, see the routing map in
[[workspace-ontology]].

Types: `fact` (durable non-project truths) · `feedback` (accumulated working guidance) ·
`reference` (external pointers) · `decision` (why a structural choice was made).
New entry: copy `_template.md`, fill it in, add a line below.

## Entries

- [[fact-workspace-repos]] — `fact` · the two workspace repos; `snds/workspace` is canonical going forward.
- [[fact-machine-layer-installs]] — `fact` · per-machine install state of the bootstrap-v2 hooks/doctor layer (Personal MBP ✅ 2026-07-09; both Work MBPs + Windows pending).
- [[fact-unraid-server]] — `fact` · Sean's Unraid home server: how to reach it (LAN / key / sandbox) + what runs on it.
- [[feedback-infra-ip-disclosure]] — `feedback` · internal/LAN IPs OK to record; external/WAN IP never (the real attack surface).
- [[feedback-credential-scoping]] — `feedback` · on the Centric laptop every repo action uses Centric credentials — including the personal workspace repo, where the Centric account is a contributor; never override repo-local git config.
- [[decision-portable-workspace-refactor]] — `decision` · why the workspace became portable, git-native, LLM-agnostic.
- [[decision-externalize-everything-to-workspace]] — `decision` · standing directive: all durable content lives in the workspace (or the platform Projects dir), never in an agent's private memory; encoded as an AGENTS.md Core rule for cross-surface reach.
- [[decision-component-pattern-framework-system]] — `decision` · why the 5-layer component & pattern context system was built (framework #09 + skill + MCP + DESIGN.md + AGENTS binding) and where its outputs live.
- [[decision-bootstrap-v2-guarantee]] — `decision` · the workspace handshake is guaranteed by deterministic harness layers (hooks + beacon + audit + launchd doctor), not model discretion; ritual token is frozen ABI.
- [[decision-commercial-data-licensing]] — `decision` · default to commercially-licensable data/asset sources for all projects; non-commercial sources (e.g. Gaia DR3) only when uniquely needed — isolate, mark, reconcile later.
- [[relational-context]] — `feedback` · the working-relationship texture, in the agent's voice, carried across sessions (lives at `../relational-context.md`).
