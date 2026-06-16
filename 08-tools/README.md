# 08-tools/

Workspace utilities. Most of `08-tools/` is gitignored (vendor + per-machine tools); the
files listed here are explicitly whitelisted in `.gitignore` because they're useful on
every machine and worth version control.

---

## drive-audit.py

One-shot snapshot of Google Drive sync state for the workspace.

```
./08-tools/drive-audit.py
```

Reports total files, downloaded vs. placeholder ("dataless") files, apparent vs. on-disk
size, percentage remaining, and a top-level breakdown. Exits `0` when sync looks complete
(no placeholders, on-disk size matches apparent within a 10 MB tolerance) and `1` while
still syncing.

Detection uses the macOS `UF_DATALESS` chflag (`0x40000000`) that Drive for Desktop
sets on placeholder files.

## drive-monitor.py

Live monitor that loops the same scan and auto-exits when sync looks complete.

```
./08-tools/drive-monitor.py [interval_seconds]   # default 60s
```

Each tick prints a row with file count, pending placeholders, % remaining, on-disk size,
delta rates, and ETA. Auto-exits with `>>> READY` when 0 placeholders + on-disk size
stable for two consecutive ticks. Logs to `~/drive-sync-tools/logs/drive-monitor_YYYY-MM-DD.log`.

## When to use

When migrating to a new laptop and Google Drive is mid-sync, opening Obsidian or running
git operations on the workspace can hang — every `stat()` on a placeholder triggers a
File Provider RPC. Run `drive-audit.py` to confirm sync is settled before unblocking those
tools. Use `drive-monitor.py` to leave a heartbeat going until completion.

The `~/drive-sync-tools/` directory on macOS provides convenience symlinks to these
scripts plus a per-machine `logs/` dir (not synced through Drive).

See `08-knowledge/cross-domain/workspace-infrastructure.md` for background on the
detection pattern and performance characteristics during heavy sync.
