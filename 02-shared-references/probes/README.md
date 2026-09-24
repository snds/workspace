---
title: Host probe records
tags: [shared-reference, harness, probes]
created: 2026-09-22
status: active
---

# Host probe records

Each file here records what one host actually does on one device, as evidence for the coverage
entries in `02-shared-references/surfaces.json`. A coverage `verified_by` ref of the form
`probe:<surface>@<device>` resolves to `<surface>@<device>.json` in this folder, and
`render_shims.py --check` treats a missing file as an error (never as a pending warning).

## How a file gets here

Probes are human-run. No agent installs probe hooks or promotes records.

1. Sean installs the pin and the probe registrations for one host in a plain terminal
   (`workspace-doctor.sh --install-pin`, then `--install-shims=<host> --probe`). The rendered
   probe fragments live in `00-bootstrap/dist/probe/`.
2. Sean triggers the host. Each probe hook runs
   `ws-hook --host auto --event <event> --probe`, which writes one redacted record under
   `~/.config/snds-workspace/telemetry/probes/` and returns the host's no-op output.
3. In the host's own terminal, and through `run_in_terminal` where the host has it, Sean runs
   `ws hook probe-env --host <host> --via terminal|run_in_terminal`. With `--record` it merges the
   terminal record into the tracked file directly.
4. `ws hook probe-promote --host <host>` merges the newest records for that host into
   `<host>@<device>.json`. It exits 1 and writes nothing when any value fails redaction.
5. Sean reviews the diff and commits it.

## Record shape

| Key | Meaning |
|---|---|
| `surface`, `device`, `declared_host` | the host and device the file describes |
| `hook_probe.status` | `recorded`, `untrusted` (the host has not trusted the hooks yet) or `not-installed` |
| `hook_probe.events` | per event: payload key names, env marker names, env presence |
| `env_probe` | the latest terminal record: `via`, env marker names, allowlisted env values, env presence |
| `env_probes` | every terminal record kept, one per `via` (`terminal`, `run_in_terminal`, `agent-shell` when no `via` was given), so one kind of run never overwrites another; the overlay installer reads all of them |
| `env_presence` | whether `WS_CLAUDE_OVERLAY`, `WS_SURFACE_FAMILY`, `GIT_CONFIG_COUNT`, `GH_CONFIG_DIR` and `CLAUDE_ENV_FILE` are set; this answers the env-import question for Cursor and VS Code |
| `ancestry_comm` | process-name basenames from the hook up to the host |
| `detected` | what host detection concluded, and whether it was verified |
| `detection_mismatch` | true when the detected host differs from the declared host |
| `git_version` | the device's git version when the record was taken |

`git@<device>.json` files come from `profile_resolve.py gitcaps --record` and hold only the git
version and the hasconfig and config-hook capabilities.

## Redaction rules

Every string value must match `^[A-Za-z0-9_.:+ ()-]{0,80}$`. So no value can hold `/`, `@` or
`~`. Records also never hold a hostname, a user name, a session id, a path, or an env value
outside `probe_env_value_allowlist` in `surfaces.json`. Env variables appear by name only.
`probe-promote` enforces all of this before it writes.
