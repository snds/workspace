#!/usr/bin/env python3
"""Fold per-session fragments into 06-context/session-log.md — idempotently.

Sessions write their block to 06-context/sessions/<id>.md (disjoint files → no
merge conflicts across machines/sessions/surfaces). This tool prepends any
not-yet-folded fragment into the canonical session-log.md (newest-first) and
removes the folded fragment.

Idempotent + self-healing:
  * dedupe key is the `SessionID:` marker (falls back to the block's `### header`
    line). A fragment whose id is already present in the log is skipped, never
    double-folded — so running twice, or on two machines, converges.
  * it PREPENDS new blocks only; it never reparses/rewrites the legacy 200 KB of
    history, so it can't mangle old blocks of varying format.
  * exit 0 always (a maintenance tool must never break a session); prints a summary.

Usage:  python3 09-tools/compact-sessions.py [--check] [--quiet]
        --check : report what would fold, change nothing (exit 1 if pending)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


def find_workspace(start: Path) -> Path | None:
    p = start.resolve()
    for cand in [p, *p.parents]:
        if (cand / "AGENTS.md").exists():
            return cand
    return None


ENTRIES_MARKER = "## Session Entries"
SID_RE = re.compile(r"^SessionID:\s*(\S+)", re.MULTILINE)
HEADER_RE = re.compile(r"^###\s+(.+)$", re.MULTILINE)
DATE_RE = re.compile(r"^Date:\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE)


def _key(text: str) -> str:
    """Stable dedupe key for a fragment/block: SessionID if present, else the
    first `### header` line, else a hash of the content."""
    m = SID_RE.search(text)
    if m:
        return "sid:" + m.group(1)
    h = HEADER_RE.search(text)
    if h:
        return "hdr:" + h.group(1).strip()
    import hashlib
    return "sha:" + hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _date(text: str) -> str:
    m = DATE_RE.search(text)
    return m.group(1) if m else "0000-00-00"


def compact(root: Path, check: bool = False, quiet: bool = False) -> int:
    log_path = root / "06-context" / "session-log.md"
    frag_dir = root / "06-context" / "sessions"
    if not log_path.exists() or not frag_dir.is_dir():
        return 0

    log = log_path.read_text(encoding="utf-8")
    fragments = sorted(p for p in frag_dir.glob("*.md") if p.name != "README.md")
    if not fragments:
        # No fragments to fold, but still bound the live log if it has grown large.
        archived = _archive_old_blocks(log_path)
        if not quiet:
            print("compact: no fragments to fold."
                  + (f" Archived {archived} old block(s) → session-log-archive.md." if archived else ""))
        return 0

    new, already = [], []
    for f in fragments:
        text = f.read_text(encoding="utf-8").strip()
        if not text:
            f.unlink()  # empty fragment — drop it
            continue
        key = _key(text)
        marker = key.split(":", 1)[1]
        # Already folded if the SessionID/header already appears in the log body.
        if marker and marker in log:
            already.append(f)
        else:
            new.append((f, text, key))

    if check:
        for f, _t, k in new:
            print(f"  would fold: {f.name}  [{k}]")
        print(f"compact --check: {len(new)} pending, {len(already)} already folded.")
        return 1 if new else 0

    if new:
        # newest-first: sort by Date desc, then filename
        new.sort(key=lambda t: (_date(t[1]), t[0].name), reverse=True)
        block_text = "\n\n".join(t[1] for t in new) + "\n\n"
        idx = log.find(ENTRIES_MARKER)
        if idx == -1:
            # no marker — append a section rather than lose content
            log = log.rstrip() + f"\n\n{ENTRIES_MARKER}\n\n---\n\n" + block_text
        else:
            # insert after the first "---" separator following the marker
            sep = log.find("\n---", idx)
            insert_at = (log.find("\n", sep + 1) + 1) if sep != -1 else (idx + len(ENTRIES_MARKER) + 1)
            log = log[:insert_at] + "\n" + block_text + log[insert_at:]
        log_path.write_text(log, encoding="utf-8")

    # Remove folded fragments (content now lives in the log + git history).
    for f, _t, _k in new:
        f.unlink()
    for f in already:
        f.unlink()

    archived = _archive_old_blocks(log_path)

    if not quiet:
        msg = (f"compact: folded {len(new)} new, dropped {len(already)} already-folded "
               f"fragment(s) into session-log.md.")
        if archived:
            msg += f" Archived {archived} old block(s) → session-log-archive.md (token-frugal)."
        print(msg)
    return 0


# Token frugality: keep the LIVE session-log small so it's cheap to read. Older
# blocks move to session-log-archive.md (read only on explicit demand). Bounds the
# live log at O(1) instead of O(sessions). ~48 KB ≈ 12k tokens of the newest work.
LIVE_BUDGET_BYTES = 48000
BLOCK_SPLIT = _re_block = __import__("re").compile(r"(?=\n### )")


def _archive_old_blocks(log_path: Path) -> int:
    """Move the oldest session blocks out of the live log into a sibling archive once
    the live log exceeds the budget. Content-preserving (blocks are moved verbatim),
    idempotent (a within-budget log is a no-op)."""
    text = log_path.read_text(encoding="utf-8")
    idx = text.find(ENTRIES_MARKER)
    if idx == -1:
        return 0
    # Split the entries region into (head-before-marker+marker, body-of-blocks).
    body_start = idx + len(ENTRIES_MARKER)
    head, body = text[:body_start], text[body_start:]
    if len(body.encode("utf-8")) <= LIVE_BUDGET_BYTES:
        return 0
    # Peel a leading separator (e.g. "\n\n---\n\n") that precedes the first `### `.
    first = body.find("\n### ")
    if first == -1:
        return 0
    lead, blocks_text = body[:first], body[first:]
    blocks = [b for b in BLOCK_SPLIT.split(blocks_text) if b.strip()]
    # Keep newest blocks (top) until the budget; archive the rest (older, bottom).
    kept, kept_bytes, cut = [], 0, []
    for b in blocks:
        if not cut and kept_bytes + len(b.encode("utf-8")) <= LIVE_BUDGET_BYTES:
            kept.append(b); kept_bytes += len(b.encode("utf-8"))
        else:
            cut.append(b)
    if not cut:
        return 0
    # Live log: head + pointer + lead + kept blocks.
    archive_path = log_path.with_name("session-log-archive.md")
    pointer = ("\n\n> _Older entries archived to " "[session-log-archive.md](session-log-archive.md)"
               " to keep this file cheap to read. Ask to see it only if you need history._\n")
    log_path.write_text(head + pointer + lead + "".join(kept), encoding="utf-8")
    # Archive: prepend the freshly-cut batch (stays newest-first overall).
    prior = archive_path.read_text(encoding="utf-8") if archive_path.exists() else (
        "# Session Log — Archive\n\n_Older session blocks, moved out of session-log.md "
        "to keep the live log token-cheap. Newest archived first._\n\n## Session Entries\n")
    ap_idx = prior.find(ENTRIES_MARKER)
    if ap_idx == -1:
        prior = prior.rstrip() + f"\n\n{ENTRIES_MARKER}\n"
        ap_idx = prior.find(ENTRIES_MARKER)
    at = ap_idx + len(ENTRIES_MARKER)
    archive_path.write_text(prior[:at] + "\n" + "".join(cut) + prior[at:], encoding="utf-8")
    return len(cut)


def main() -> int:
    args = set(sys.argv[1:])
    root = find_workspace(Path.cwd())
    if root is None:
        # tool lives at <root>/09-tools/ — resolve from its own location as fallback
        root = Path(__file__).resolve().parent.parent
        if not (root / "AGENTS.md").exists():
            sys.stderr.write("compact-sessions: workspace root not found\n")
            return 0
    try:
        return compact(root, check="--check" in args, quiet="--quiet" in args)
    except Exception as e:  # never break a session over log maintenance
        sys.stderr.write(f"compact-sessions: non-fatal error — {e}\n")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
