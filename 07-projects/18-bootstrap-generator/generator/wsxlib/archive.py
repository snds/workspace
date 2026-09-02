"""`wsx archive` — retire a note without ever deleting it.

The rule this enforces: **never delete a note, archive it with provenance.** Deleting
silently breaks every inbound link and destroys the reason the note existed; archiving
keeps the history, keeps git blame meaningful, and leaves a trail back to the original
path. A stale note is a problem; a vanished one is a mystery.

`wsx archive context/decisions/2024-01-01-old.md --reason "superseded by X"` moves the
file to `_archive/context/decisions/…` (mirroring its original location) and stamps
provenance front matter on it. Idempotent-ish: archiving twice is refused, not doubled.
"""
from __future__ import annotations

from pathlib import Path

from . import core


def _provenance(orig_rel: str, reason: str) -> str:
    lines = [
        "---",
        "archived: true",
        f"archived_on: {core.today()}",
        f"archived_from: {orig_rel}",
    ]
    if reason:
        lines.append(f"archived_reason: {reason}")
    lines += ["---", ""]
    return "\n".join(lines)


def archive(root: Path, target: str, reason: str = "") -> int:
    src = Path(target)
    if not src.is_absolute():
        src = (root / target).resolve()
    try:
        rel = src.relative_to(root)
    except ValueError:
        raise SystemExit(f"error: {target} is not inside this workspace")
    if not src.exists() or not src.is_file():
        raise SystemExit(f"error: no such file: {rel}")
    if "_archive" in rel.parts:
        raise SystemExit(f"error: {rel} is already archived")

    dst = root / "_archive" / rel
    if dst.exists():
        raise SystemExit(f"error: an archived copy already exists at {dst.relative_to(root)}")
    dst.parent.mkdir(parents=True, exist_ok=True)

    text = src.read_text(encoding="utf-8")
    # Stamp provenance ahead of any existing front matter rather than merging into it —
    # the original file stays byte-recoverable underneath.
    dst.write_text(_provenance(str(rel), reason) + text, encoding="utf-8")
    src.unlink()

    print(f"✓ archived {rel} → _archive/{rel}")
    if reason:
        print(f"  reason: {reason}")
    print("  provenance stamped (archived_on / archived_from). Nothing was deleted.")
    # Inbound links now dangle — say so rather than let it be discovered later.
    inbound = _inbound_refs(root, src.stem)
    if inbound:
        print(f"  ⚠ {len(inbound)} note(s) still link to this — update or they'll dangle:")
        for p in inbound[:10]:
            print(f"      · {p}")
    print("  run `wsx health` to confirm the graph is still clean.")
    return 0


def _inbound_refs(root: Path, stem: str) -> list:
    """Best-effort: which canonical notes still reference this basename?"""
    from . import health as _health
    hits = []
    needle = stem.lower()
    for p in _health._iter_notes(root):
        try:
            text = p.read_text(encoding="utf-8").lower()
        except OSError:
            continue
        if f"[[{needle}" in text or f"{needle}.md" in text:
            hits.append(str(p.relative_to(root)))
    return hits
