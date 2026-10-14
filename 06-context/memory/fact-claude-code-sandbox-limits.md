---
type: fact
description: What Claude Code's Bash sandbox blocks on the Work MBP — api.github.com, ps, xcrun's git cache — and how to work with it without bypassing the walls.
created: 2026-10-14
confidence: high
relations: { relates-to: ["[[feedback-credential-scoping]]", "[[fact-machine-layer-installs]]"] }
---

## For future agent
- **TL;DR:** Inside Claude Code's Bash sandbox, `gh` reports a bad token because the network filter blocks `api.github.com`; the login is fine. `ps` is denied and git runs slowly, so some harness gates fail or time out in the sandbox and pass outside it.

## The limits (Work MacBook Pro, Claude Code desktop, verified 2026-10-14)

- **`api.github.com` is blocked; `github.com` is allowed.** `gh auth status` prints "The token in keyring is invalid". The keychain is reachable inside the sandbox (`gh auth token` and `security find-generic-password` both work). Git over HTTPS to `github.com` works (`git ls-remote`, fetch, push). The `allowed_domains` command option did not unblock `api.github.com` in this session. Run `gh` calls that need the API outside the sandbox.
- **The doctor knows this.** Since `d3c4788`, `workspace-doctor.sh --check` says "Claude gh login not verified: this shell cannot reach api.github.com" when a login is stored but the API is unreachable. It no longer tells Sean to run `gh auth login`.
- **`ps` is denied.** Process-ancestry checks SKIP inside the sandbox (`profile_resolve.py --self-test` shows 3 SKIPPED; outside it, 406/406).
- **git's xcrun launcher cannot write its cache.** Every git call is slow and prints a warning, so long suites time out: `test-validators.py` hit the harness's 1,200 s limit inside the sandbox and passed outside it in ~870 s. `nightly.py --self-test` went 72/74 → 74/74 outside. The harness prints both causes as `! environment:` notes.
- **The wall guard refuses the shortcuts.** A PATH-prepended git (the harness's own suggested workaround) is refused as a hook or config bypass (R6 P05), and so is setting `GH_CONFIG_DIR=` on a command (R6). Both are deliberate. Do not work around them.

## How to apply
- When a gate fails only with those environment notes, re-run that gate outside the sandbox and report both results. A pass inside the sandbox is not required.
- Never treat the sandboxed `gh` message as a real login problem. Check with `gh auth status` outside the sandbox first.
- Writes to `~/.claude/` (CLAUDE.md, hooks, settings) are also sandbox-protected. The doctor heals them from its own session-start run or a human `workspace-doctor.sh` run, not from an agent's Bash.
