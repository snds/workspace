"""`wsx loadset <utterance>` — ordered skill paths a cold agent should load.

Never ingest `skills.registry.json`. Match the utterance against each skill's own
declared triggers and print paths. Hubs before spokes. Empty match is honest, not a dump.
"""
from __future__ import annotations

from pathlib import Path

from . import core


def match(root: Path, utterance: str, limit: int = 8) -> list:
    """Return [{name, path, kind, hits}] ordered hub-first, then by hit count."""
    text = (utterance or "").strip().lower()
    if not text:
        return []
    scored = []
    for name, sk in core.iter_skills(root):
        fm, _ = core.parse_frontmatter(sk)
        trg = core.skill_triggers(fm)
        hits = [t for t in trg if t and t in text]
        if not hits:
            continue
        rel = str(sk.relative_to(root))
        kind = str(fm.get("kind") or "spoke")
        scored.append({
            "name": name,
            "path": rel,
            "kind": kind,
            "hits": hits,
            "n": len(hits),
        })
    scored.sort(key=lambda r: (0 if r["kind"] == "hub" else 1, -r["n"], r["name"]))
    return scored[:limit]


def run(root: Path, utterance: str) -> int:
    rows = match(root, utterance)
    if not rows:
        print("wsx loadset — no skill triggers matched. Do not ingest the registry.")
        print("  Try a more specific phrase, or `wsx skill list`.")
        return 0
    print(f"wsx loadset — {len(rows)} skill(s) for: {utterance.strip()!r}\n")
    print("  Load these (hubs first). Do not open skills.registry.json.\n")
    for r in rows:
        mark = "hub" if r["kind"] == "hub" else "spoke"
        print(f"  [{mark:5}] {r['path']}  ({', '.join(r['hits'])})")
    return 0
