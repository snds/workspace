# Per-machine skills symlink resolver — install note

**What it does:** keeps `~/.claude/skills` pointed at whichever Google Drive workspace
root is actually *materialized* on this machine. Lets you mix sync modes per machine:

| Machine | Drive mode | Resolved root |
|---|---|---|
| Work MacBook | **Stream** (workspace folder set to *Available offline*) | `~/Library/CloudStorage/GoogleDrive-…/My Drive/Claude Workspace/02-skills` |
| Personal MacBook (Voyager-2) | **Mirror** | `~/My Drive/Claude Workspace/02-skills` |
| Windows Desktop (Enterprise) | **Mirror** | `G:\My Drive\Claude Workspace\02-skills` (`/g/...` under Git Bash) |

The resolver picks the first candidate whose probe file (`06-context/session-log.md`)
has **real local bytes** — existence alone isn't trusted, because a stale stream mount
lists fine while every file is a 0-byte placeholder.

Because `~/.claude/` is **machine-local (not Drive-synced)**, each machine carries its
own symlink + its own copy of this hook. One identical script, correct everywhere.

## Install on a new machine (macOS)

```sh
mkdir -p ~/.claude/hooks
cp "$HOME/My Drive/Claude Workspace/00-bootstrap/setup/resolve-skills-symlink.sh" \
   ~/.claude/hooks/resolve-skills-symlink.sh   # adjust source path if stream-mode
chmod +x ~/.claude/hooks/resolve-skills-symlink.sh
~/.claude/hooks/resolve-skills-symlink.sh       # run once to create the symlink
```

Then add the SessionStart hook to `~/.claude/settings.json` (merge, don't overwrite):

```json
{
  "hooks": {
    "SessionStart": [
      { "hooks": [ { "type": "command",
        "command": "$HOME/.claude/hooks/resolve-skills-symlink.sh" } ] }
    ]
  }
}
```

## Windows note

The script's Windows branch probes `/g/My Drive/...` and `/h/My Drive/...` (Git Bash
mount form). If the hook runs under PowerShell/cmd instead of a POSIX shell, port the
same logic to `.ps1` and register it the same way; the resolution rule is identical
(first candidate whose `06-context/session-log.md` is non-empty wins).

## Work Mac (stream + offline) checklist

In Google Drive → the `Claude Workspace` folder → **Available offline**. That keeps the
stream mount but materializes the bytes, so `[ -s ]` passes and the resolver selects the
CloudStorage path. No mirror download required.

## Safety properties

- **Idempotent:** only repoints when the target differs; silent otherwise.
- **Non-destructive:** refuses to clobber a real (non-symlink) `~/.claude/skills`.
- **Non-fatal:** if nothing is materialized (Drive offline), it exits 0 and lets
  workspace-bootstrap fall back to Drive MCP.
