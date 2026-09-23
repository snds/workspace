# installer fixtures (H24)

Synthetic inputs for `00-bootstrap/doctor/installers.py --self-test` and TestInstaller.
Owners, names and emails are placeholders (`pat-sample`, `example.invalid`); nothing here is
machine state. `repo/` is copied into a temporary git repo per test; the overlay test reads
the tracked `00-bootstrap/dist/settings-user-fragment.json` read-only instead of a copy.

- `render-list.json` stands in for `render_shims.py --list --json` until H16 lands.
- `settings-v1-stale.json` is a v1-style Claude overlay (holds `GIT_AUTHOR_*`).
- `probe-cursor.json` is a redacted probe record; the test flips `WS_CLAUDE_OVERLAY`.
