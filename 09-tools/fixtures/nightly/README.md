# nightly / dispatcher fixtures (H1)

Hermetic fixtures for `09-tools/nightly.py --self-test` and
`.claude/hooks/dispatcher.py --self-test`. Nothing here touches the real vault, the real
HOME or any machine config: every case builds temp repos, sets a temp `HOME`, strips host
markers and `GIT_*` variables, and puts stub `launchctl`/`gh`/`osascript`/`claude` first on
`PATH` (the stubs must never be called, `claude` excepted).

| File | Purpose |
|---|---|
| `nightly_fixture_lib.py` | Shared helpers: hermetic env, temp vault built from the real generators, lane hook dir, contract-shaped fake `ws_hook` / `profile_resolve` sources |
| `selftest_nightly.py` | Fixpoint order, written paths per step, session scope, foreign edits (exit 4), step timeout and budget (SKIPPED, exit 3), the pre-commit lane with the X1 replay under four marker sets, and the timed SessionEnd accelerator (≤ 55 s, push to a local bare remote) |
| `selftest_dispatcher.py` | Deferral on verified non-Claude hosts only, unknown events exit 0, baseline wiring, the sibling `<root>.intent-*` worktree guard, no commit on `intent/*`, device labels from `devices.json`, no legacy hostname map |
| `payloads/*.json` | T5's own copies of host-shaped hook payloads (Claude Code, Cursor, VS Code). After integration, `TestDispatcherDefer` loads the shared golden payloads under `09-tools/fixtures/ws_hook/payloads/` |

The fake resolver modules exist only as source text written into temp repos. They export
through a registration table, so no tracked file carries a second definition of a
contract helper.
