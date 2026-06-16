---
tags: [claude-code, mcp, engineering, cli]
created: 2026-05-12
updated: 2026-05-12
status: stable
confidence: high
sources: [session 2026-05-12 — Mobbin MCP setup]
related_skills: [workspace-bootstrap]
related_projects: []
---

# `claude mcp add` Scope Behavior

A non-obvious default in the Claude Code CLI that bites anyone setting up MCP
servers without explicitly specifying scope.

## The trap

`claude mcp add` **defaults to `--scope local`**, which is project-scoped to the
**current working directory**, not globally available. Vendor-provided install
snippets almost never include the scope flag — they just say:

```bash
claude mcp add <name> --transport http <url>
```

Run that from `~/` and the MCP only loads when Claude Code is started from `~/`.
Run it from inside a project and the MCP only loads in that project.

## The three scopes

| Scope | Storage | Loads when |
|---|---|---|
| `local` (default) | `~/.claude.json` under `projects.{cwd}.mcpServers` | Claude Code is started from that exact directory |
| `project` | `.mcp.json` in the project root (checked into git) | Claude Code is started anywhere inside that project (or below) |
| `user` | `~/.claude.json` top-level `mcpServers` | Every Claude Code session, every directory |

## Diagnose

If you ran `claude mcp add <name> ...` and `/mcp` or `claude mcp list` doesn't
show the server, it landed in some other project's local scope:

```bash
# What's user-scoped?
python3 -c "import json; print(list(json.load(open('$HOME/.claude.json')).get('mcpServers',{}).keys()))"

# What's local-scoped per project?
python3 << 'EOF'
import json
d = json.load(open('/Users/$USER/.claude.json'))
for path, cfg in d.get('projects', {}).items():
    if cfg.get('mcpServers'):
        print(f"{path}: {list(cfg['mcpServers'].keys())}")
EOF
```

## Fix (move local → user)

```bash
claude mcp remove <name>                                    # remove local-scoped registration
claude mcp add --transport http --scope user <name> <url>   # re-add globally
```

`claude mcp remove` only operates in the current scope's context. If the
registration is in a different project's local scope (e.g. you added it from
`~/` but you're now elsewhere), `remove` returns "no server found." In that
case, edit `~/.claude.json` directly: delete the entry from
`projects.{path}.mcpServers` (always back up `~/.claude.json` first).

## After moving scope: restart required

**`claude mcp add` writes config only — it does not hot-reload the running
session.** Tools are discovered at session start, so the new MCP doesn't
become available until you fully quit Claude Code (`Cmd+Q` on macOS desktop
app — not just `/clear`) and reopen.

## HTTP-transport MCPs: OAuth on first call

For `--transport http` servers (e.g. Mobbin, Sentry), the first tool call after
restart triggers an OAuth flow — browser pops, you authenticate with the
service, callback returns. The token caches in the user's MCP credential store.
`claude mcp add` itself does not run OAuth; it just registers the URL.

## Verification sequence

After fixing scope + restarting:

1. `claude mcp list` — server appears with `✓ Connected` or pending-auth state.
2. In a Claude Code session: `/mcp` — same confirmation.
3. First tool call (e.g. `mcp__<name>__<tool>`) triggers OAuth if needed.
4. Subsequent calls use the cached token.

## Cross-cutting implication

For Sean's workspace setup, where Claude Code sessions run from many
directories (workspace root, worktrees under `.claude/worktrees/`, project
folders under `07-projects/`), **MCPs should almost always be `--scope user`**.
The exception: project-specific MCPs that should travel with a particular
project's git repo — use `--scope project` and check `.mcp.json` into VCS.
