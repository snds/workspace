# Prepared patches (Sean applies)

`dispatcher-w2-0.patch` (W2-0): `.claude/hooks/dispatcher.py` routes prompts through `prompt_route.route_payload` (the one H7 matcher), archives its dead matcher copy to `_archive/dispatcher-matcher-2026-09/` with an `ARCHIVE-LOG.md` row, and at SessionEnd defers every repo other than the workspace to `ws closure plan` (H23). Behaviour is otherwise unchanged; the dispatcher self-test passes on the patched copy.
Agents cannot write `.claude/hooks/`, so Sean applies it from the workspace root: `git apply --check 00-bootstrap/patches/dispatcher-w2-0.patch && git apply 00-bootstrap/patches/dispatcher-w2-0.patch`.
If `_archive/ARCHIVE-LOG.md` has moved on since, use `git apply --3way`. Then run `python3 .claude/hooks/dispatcher.py --self-test` and commit.
