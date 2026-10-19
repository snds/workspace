---
title: Externals Spec
spec_version: "1.0"
status: canonical
aliases: [externals-spec, externals, external repos]
---

# Externals Spec

An **external** is someone else's repo or package that this workspace uses but does not own: an MCP
server, a CLI, a skill pack. This page is the contract for adding one, keeping it current, running it, and
taking it out again. Any agent, the Synapse app, or a person can follow it. The tool that carries it out is
`09-tools/externals.py` (stdlib Python, no dependencies).

The first external is **REA** (`rea-agents`, a reverse-engineering MCP server and CLI). Its capability entry
is `rea-mcp` in [[capability-registry]].

## The rules

1. **One home for what is installed.** `02-shared-references/externals.json` (tracked) lists every external
   and its exact pin. Only `externals.py` writes it. The one hand-authored field is an entry's `verify`
   block (the parity probes, below).
2. **Pins are exact.** An npm external pins a version *and* its registry integrity (sha512). A git external
   pins a full 40-character commit. A fetch that doesn't hash to the pin is refused. That covers a
   republished version or a tampered download.
3. **Code never lives in the portable workspace** ([[AGENTS]] → Core rules). It goes to
   `<projects_root>/_externals/<id>/`. `projects_root` comes from `devices.json`, for example `~/Projects`;
   `WS_EXTERNALS_HOME` overrides it. The workspace sees it through `.externals/<id>`, a git-ignored link
   to the package root on each device.
4. **Wiring is tracked; code is not.** The MCP entries (`.mcp.json` for Claude Code, `.cursor/mcp.json` for
   Cursor) and the skill links (`.claude/skills/<name>` and `.agents/skills/<name>`) are written when an
   external is added, updated, or removed. They reach every machine through git. A machine without the
   code still starts the MCP server, through `npx` at the same pin.
5. **Nothing changes without `--yes`, and only the reviewed plan is applied.** Every command that writes
   prints its plan first: the resolved pin, each operation, and the exact change to every tracked file.
   `--expect-plan <plan_sha256>` refuses if anything changed since the review. That includes a new
   upstream release or a tracked file edited in between.
6. **One writer at a time.** A second writing run on the same device, such as the app and an agent at
   once, is refused with `busy`. A lock left by a process that no longer exists is taken over.
7. **Skill names don't collide.** `--skill` refuses a name that a workspace skill (`03-skills/<name>`),
   another external, or any existing entry in `.claude/skills` or `.agents/skills` already uses.
8. **Local work is never lost silently.** `update` and `remove` refuse when a git external has edits,
   untracked files, stashes, or commits that exist only on this device. `--force` overrides.
9. **Removal keeps provenance.** A removed entry moves to `removed` in the manifest, with its date and the
   reason. The code folder is deleted, since it can be fetched again from the upstream.

## Lifecycle

| Step | Command | What happens |
|---|---|---|
| Add | `externals.py add ID --npm PKG@VER` or `--git URL --ref REF`, plus `--mcp "ARGS"`, `--skill NAME=PATH`, `--bin`, `--run` | Resolves the exact pin, fetches into a staging folder, verifies it, swaps it in, writes the manifest and the wiring |
| Install (each device) | `externals.py install --all --yes` | Fetches every pinned external that's missing here and repairs wiring drift. Idempotent |
| Update from upstream | `externals.py update ID [--to VER\|REF] --yes` | npm: stages the new version and keeps the old one as `<id>.prev`. git: `fetch`, then moves the checkout to the new commit **in place** and rebuilds; a failed build checks the old commit back out. Re-pins the manifest |
| Roll back | `externals.py rollback ID --yes` | Returns to the copy or commit the last update replaced |
| Remove | `externals.py remove ID --reason "…" --yes` | Unwires the MCP entries and skill links, deletes the code and the link, records provenance |
| Run | `externals.py exec ID -- ARGS` | Runs the pinned copy with stdio passed through. Falls back to `npx PKG@VER` with a note on stderr, never stdout, since MCP uses stdout |
| This device | `externals.py status [ID]` | Pinned vs installed: `ok`, `missing`, or `drift` |
| Tracked wiring | `externals.py check` | CI gate, no network: the wiring matches the manifest, and a removed external left nothing behind |
| Parity | `externals.py verify ID [--quick]` | Live proof that the workspace copy behaves exactly like the upstream (next section) |

## Parity: "works identically from inside the workspace"

`verify` compares the workspace copy, launched the way a host launches it, against a clean reference
install outside the workspace. For REA it checks:

1. The registry integrity, the lockfile integrity, and the registry tarball all hash to the pin.
2. Every file in the installed package is byte-identical to the registry tarball (1,775 files).
3. Each linked skill resolves to the upstream skill byte for byte, in both `.claude/skills` and `.agents/skills`.
4. Every CLI command's `--help`, plus `--version`, `--help`, `--llms`, `setup --help`, `capabilities`, and two
   real analyses of a fixture app give the same exit code, stdout, and stderr inside and outside the
   workspace. That's 161 probes. Install paths and wall-clock timestamps are the only things normalized.
5. `npx` (the upstream launcher) and the workspace launcher report the same version.
6. The server Claude Code starts from the tracked `.mcp.json` gives the same MCP handshake and catalog as
   the reference server: 207 tools, plus prompts and resources.
7. Running it from the workspace writes no files into the workspace.

A git external's `verify` checks that the checkout sits at the pinned commit with no local changes, and
that its `verify.cli` probes match.

`externals.py --self-test` covers the manager itself, offline. It builds a fake git upstream and a local npm
tarball, then runs add, dry run, exec, the in-place update, the refusal over local edits, rollback, a
hand-edit that `check` catches, repair, the integrity refusal, the npx fallback, and removal with
provenance. It also covers the app contract: structured plans with diffs, a stable `plan_sha256`, the
`--expect-plan` refusal, an edit made after review, `busy`, taking over a stale lock, and skill-name
collisions (41 cases). It runs in the harness and in CI (`workspace-integrity.yml`).

## Manifest entry

```json
"rea": {
  "kind": "npm",                         // or "git"
  "package": "rea-agents", "version": "6.7.0", "integrity": "sha512-…",   // npm
  // "repo": "https://…", "ref": "main", "commit": "<40 hex>", "build": [["npm","ci"]], "run": ["node","{root}/cli.mjs"],  // git
  "bin": "rea",
  "upstream": "https://github.com/morluto/rea",
  "purpose": "…",
  "mcp": {"name": "rea", "args": ["mcp"], "hosts": ["claude-code", "cursor"]},
  "skills": [{"name": "reverse-engineer-anything", "path": "skills/reverse-engineer-anything"}],
  "verify": {"cli": [["--version"]], "each_command": {"list": ["--llms","--format","json"], "suffix": ["--help"]},
             "fixture": {"app/index.js": "…"}, "functional": [["inspect", "{fixture}/app/index.js"]]},
  "added": "2026-10-19"
}
```

## Contract for apps (Synapse)

The Synapse app (project 26) drives this tool. It doesn't reimplement it (Synapse decision D108: this is
supply-chain code, and two implementations double what can go wrong). A Rust port comes only if the app
must manage externals in a workspace that doesn't carry `externals.py`, and it must pass the same
self-test cases by name. The app's Integrations screen runs the lifecycle, and its Agent apps screen shows
what each external wires into each app.

- **Envelope.** Every command takes `--json` and prints one object:
  `{"spec": "1.0", "ok", "action", "id", "plan": [...], "applied": [...], "warnings": [...], "error"}`.
  The app refuses a `spec` major version it doesn't know. `status` adds
  `externals: [{id, kind, pinned, installed, state, path, link_ok}]`, `verify` adds
  `checks: [{check, ok, detail}]`, `check` adds `errors`, and `--self-test --json` prints
  `cases: [{name, ok, detail}]`.
- **Plan.** Each `plan` entry is `{op, path, tracked, detail}`. `op` is one of `fetch`, `checkout`,
  `swap`, `write`, `link`, `unlink`, or `delete`. A tracked `write` also carries `before_sha256`
  (null when creating), `after_sha256`, `after` (the full new text), and `diff` (unified). A `link` or
  `unlink` carries `target` and `before`. The object also has `resolved`, the exact pin
  (`{version, integrity}` or `{commit}`), and `plan_sha256`.
- **Review, then apply.** A dry run (no `--yes`) is the review. To apply, the app reruns with the
  resolved pin (`--npm PKG@VERSION`, `--ref COMMIT`, or `update --to VERSION|COMMIT`) and
  `--yes --expect-plan <plan_sha256>`. If the plan differs, the run exits 4 and writes nothing. While
  applying, a tracked file that no longer matches its `before_sha256` stops the run the same way.
- **Busy.** A second writing run exits 4 with `"error": "busy"` and the holder in `detail`.
- **Exit codes:** `0` ok · `1` failed, or `verify` found a difference · `2` usage · `3` not installed or
  nothing to do · `4` refused (local changes, integrity mismatch, plan changed, busy, name in use, unknown
  id).
- **Per-device state** is `<install dir>/.ws-external.json` (`version` or `commit`, `previous_commit`,
  `installed_at`). Read it; don't write it.
- **Read-only runs** for a tool runner are listed in `09-tools/externals.tool.json`: status, check,
  verify (network), and self-test. Writing runs take arguments, so they go through the app's review.

## Limits

- **Windows:** the tracked skill links are symlinks, like the Copilot skill pack's. A checkout without
  symlink support gets text files there instead. `.externals/<id>` falls back to a junction.
- **Project MCP servers need one approval per machine** in Claude Code. That's its trust prompt for a
  `.mcp.json` server, and it is left on deliberately.
- An npm external is the *published* package, which is what its users run. The upstream repo's own
  development scripts (build, test suites) need its dev dependencies. They become available only when
  the external is added as `--git` with `build` steps.
