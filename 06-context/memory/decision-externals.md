---
type: decision
description: Other people's repos and packages enter the workspace only as pinned externals (09-tools/externals.py); code lives outside the vault, wiring is tracked, and every write is a reviewed plan
created: 2026-10-19
confidence: high
relations:
  builds-on: ["[[decision-externalize-everything-to-workspace]]", "[[decision-portable-workspace-refactor]]"]
  relates-to: ["[[externals-spec]]", "[[capability-registry]]"]
---

## For future agent
- **TL;DR:** To use someone else's MCP server, CLI, or skill pack here, run `python3 09-tools/externals.py add …`. Don't run its own `setup`, `npm i -g`, or a hand-edited `.mcp.json`. The manifest `02-shared-references/externals.json` pins it exactly. The code lives in `<projects_root>/_externals/<id>`, and git carries the wiring (`.mcp.json`, `.cursor/mcp.json`, skill links) to every machine. On a new device: `python3 09-tools/externals.py install --all --yes`. REA (`rea-agents`) is the first external. The Synapse app drives the same tool (its D108).
- **As of:** 2026-10 · **Status:** current

## Context — what forced a choice
Sean asked to install REA with its own `npx rea-agents setup`. That writes to `~/.claude.json` and `~/.claude/skills`. Those are per-machine and invisible to other surfaces, and in a cloud container they're gone when the session ends. That breaks [[decision-externalize-everything-to-workspace]]. Copying the code into the vault would break the rule that repos never live in the portable workspace ([[AGENTS]] → Core rules). He also wanted one method for installing, updating in place, and removing such repos, and wanted it in Synapse.

## Decision — what we chose
- **One manifest, exact pins.** An npm external pins a version and its sha512 integrity. A git external pins a full commit, plus `ref`, the branch or tag `update` follows (pinning a commit follows the default branch). A fetch that doesn't hash to the pin is refused.
- **Code outside, wiring inside.** The code goes to `<projects_root>/_externals/<id>`, linked at `.externals/<id>` (git-ignored). The tracked wiring is written only from the manifest. A device without the code still starts the MCP server through `npx` at the same pin.
- **Reviewed plans.** A dry run lists each operation, the diff for every tracked file, the resolved pin, and `plan_sha256`. `--yes --expect-plan` applies only that plan. One writer per device (`busy`). Local work in a git external is never overwritten without `--force`. A removal keeps its entry under `removed`, with the reason.
- **Parity is proven, not assumed.** `externals.py verify <id>` compares the workspace launch against a clean install outside the workspace. For REA: 1,775 files, 161 CLI probes, and the 207-tool MCP catalog came out identical, with nothing written into the workspace.

## Rationale — why, and what we rejected
(1) Run the vendor's own setup per machine. It's private, per-device state with no review or removal record, and it's lost in cloud containers. (2) Vendor the code into the vault. That breaks the portable-workspace rule and bloats git. (3) Hand-edit `.mcp.json`. That leaves no pin, no integrity check, and no removal path. (4) Reimplement the lifecycle in Synapse. Two copies of supply-chain code double the failure modes, so Synapse drives this tool instead (Synapse D108).

## Consequences — what this commits us to
`externals.py check` and `--self-test` run in the harness and in `workspace-integrity.yml`. A changed manifest or wiring file triggers the `externals` diff class. Project MCP servers still need Claude Code's one-time approval per machine (left on deliberately). On Windows, the skill links are symlinks, with the same limit as the Copilot pack's. An npm external is the published package; the upstream's dev scripts come only with a `--git` external that has `build` steps.
