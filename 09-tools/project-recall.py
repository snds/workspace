#!/usr/bin/env python3
"""
project-recall.py

One project's context in three tiers ([[decision-memory-tiers]]), so an agent asked about
anything older than "lately" looks everywhere before saying there's no record.

  current    the baton's Live handoff
  recent     the baton's history section; session-log.md blocks and unfolded fragments naming it
  long-term  history/YYYY-MM.md; session-log-archive.md blocks naming it; project-context-detail
             sections naming it
  record     the baton's git history, back to the project's first commit

Without words it prints where each tier lives and how much is there. With words it searches
every tier and ranks what it finds: more of the words first, then current before recent before
long-term, then newest. It reads only the project you name (no global index), so an employer
project never lands in a shared one.

Usage:
    python3 09-tools/project-recall.py 29-unicron
    python3 09-tools/project-recall.py unicron "contrast misses"
    python3 09-tools/project-recall.py 29 "release" --tier long --limit 5
    python3 09-tools/project-recall.py 29 "tokens" --json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
PROJECTS = WORKSPACE / "07-projects"
CONTEXT = WORKSPACE / "06-context"
TIERS = ["current", "recent", "long-term", "record"]


@dataclass
class Unit:
    tier: str
    date: str
    title: str
    text: str
    source: str


def find_project(name: str) -> Path:
    """A project folder by its full name, its number, or a word in its name."""
    folders = [p for p in PROJECTS.iterdir() if p.is_dir() and (p / "SESSION-STATE.md").is_file()]
    for test in (lambda p: p.name == name,
                 lambda p: p.name.split("-", 1)[0] == name.zfill(2),
                 lambda p: name.lower() in p.name.lower()):
        hits = [p for p in folders if test(p)]
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            raise SystemExit(f"'{name}' matches {', '.join(sorted(h.name for h in hits))}; name one")
    raise SystemExit(f"no project matches '{name}' (a folder in 07-projects with a SESSION-STATE.md)")


def rel(p: Path) -> str:
    return str(p.relative_to(WORKSPACE))


def date_in(s: str) -> str:
    m = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", s)
    return m.group(1) if m else ""


def h3_blocks(text: str) -> list[tuple[str, str]]:
    """(heading, body) for each `### …` block, ending at the next heading of level 1–3."""
    out, head, body = [], None, []
    for line in text.splitlines():
        if re.match(r"^#{1,3} ", line):
            if head is not None:
                out.append((head, "\n".join(body).strip()))
                head, body = None, []
            if line.startswith("### "):
                head = line[4:].strip()
            continue
        if head is not None:
            body.append(line)
    if head is not None:
        out.append((head, "\n".join(body).strip()))
    return out


def section(text: str, heading_has: str, level: int) -> str:
    """The text under the first heading at `level` that contains `heading_has`, to the next at or above it."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6}) ", line)
        if m and len(m.group(1)) == level and heading_has in line.lower():
            out = []
            for l in lines[i + 1:]:
                n = re.match(r"^(#{1,6}) ", l)
                if n and len(n.group(1)) <= level:
                    break
                out.append(l)
            return "\n".join(out)
    return ""


def bullets(text: str) -> list[str]:
    """Top-level bullets with their continuation lines."""
    out, cur = [], None
    for line in text.splitlines():
        if line.startswith("- "):
            if cur is not None:
                out.append("\n".join(cur))
            cur = [line]
        elif cur is not None and (line.startswith((" ", "\t")) or (line.strip() and not line.startswith("#"))):
            cur.append(line)
        elif cur is not None:
            out.append("\n".join(cur))
            cur = None
    if cur is not None:
        out.append("\n".join(cur))
    return out


def label(b: str) -> str:
    m = re.match(r"^- \*\*(.+?)\*\*", b)
    return m.group(1).strip(" :") if m else b[2:60]


def gather(folder: Path) -> list[Unit]:
    units: list[Unit] = []
    baton_path = folder / "SESSION-STATE.md"
    baton = baton_path.read_text(encoding="utf-8", errors="replace")
    live_level = next((len(m.group(1)) for m in re.finditer(r"^(#{1,6}) .*live handoff", baton, re.I | re.M)), 3)
    for b in bullets(section(baton, "live handoff", live_level)):
        units.append(Unit("current", date_in(b.splitlines()[0]), label(b), b, rel(baton_path)))
    hist = section(baton, "history", 2)
    for head, body in h3_blocks(hist):
        units.append(Unit("recent", date_in(head), head, body, rel(baton_path)))
    for b in bullets(hist):
        if re.match(r"^- \*\*\d{4}-\d{2}-\d{2}", b):
            units.append(Unit("recent", date_in(b), b[2:100], b, rel(baton_path)))
    name = folder.name
    logs = [(CONTEXT / "session-log.md", "recent"), (CONTEXT / "session-log-archive.md", "long-term")]
    logs += [(p, "recent") for p in sorted((CONTEXT / "sessions").glob("*.md")) if p.name != "README.md"]
    for path, tier in logs:
        if not path.is_file():
            continue
        for head, body in h3_blocks(path.read_text(encoding="utf-8", errors="replace")):
            if re.search(rf"^Project(?:\(s\))?:.*\b{re.escape(name)}\b", body, re.M):
                units.append(Unit(tier, date_in(head), head, body, rel(path)))
    for month in sorted((folder / "history").glob("*.md")):
        if month.name == "README.md":
            continue
        for head, body in h3_blocks(month.read_text(encoding="utf-8", errors="replace")):
            units.append(Unit("long-term", date_in(head), head, body, rel(month)))
    detail = CONTEXT / "project-context-detail.md"
    if detail.is_file():
        words = {name.lower(), name.split("-", 1)[-1].lower()}
        text = detail.read_text(encoding="utf-8", errors="replace")
        for head, body in h3_blocks(text):
            if any(w in head.lower() for w in words):
                units.append(Unit("long-term", date_in(head), head, body, rel(detail)))
    try:
        log = subprocess.run(
            ["git", "-C", str(WORKSPACE), "log", "--follow", "--format=%aI%x1f%s", "--", rel(baton_path)],
            capture_output=True, text=True, timeout=20,
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        log = ""
    for line in log.splitlines():
        when, _, subject = line.partition("\x1f")
        units.append(Unit("record", when[:10], subject, subject, f"git log -- {rel(baton_path)}"))
    return units


def snippet(text: str, words: list[str], width: int = 180) -> str:
    flat = " ".join(text.split())
    low = flat.lower()
    at = min((low.find(w) for w in words if w in low), default=0)
    start = max(0, at - 40)
    out = flat[start:start + width]
    return ("…" if start else "") + out + ("…" if start + width < len(flat) else "")


def tier_map(folder: Path, units: list[Unit]) -> str:
    count = lambda t: sum(1 for u in units if u.tier == t)
    baton = folder / "SESSION-STATE.md"
    months = sorted(p.stem for p in (folder / "history").glob("*.md") if p.name != "README.md")
    lines = [
        f"{folder.name}: context in three tiers ([[decision-memory-tiers]])",
        f"  current    {count('current'):4} Live handoff fields      {rel(baton)} ({baton.stat().st_size / 1024:.1f} KB)",
        f"  recent     {count('recent'):4} history and session entries   the baton's history section, session-log.md, fragments",
        f"  long-term  {count('long-term'):4} entries                   "
        + (f"{rel(folder / 'history' / 'README.md')} ({', '.join(reversed(months))})" if months else "no history/ yet")
        + ", session-log-archive.md, project-context-detail.md",
        f"  record     {count('record'):4} baton commits             git log -- {rel(baton)}",
        "Search them all: python3 09-tools/project-recall.py " + folder.name + ' "<words>"',
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("project")
    parser.add_argument("words", nargs="?", default="")
    parser.add_argument("--tier", choices=["current", "recent", "long", "record", "all"], default="all")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    folder = find_project(args.project)
    units = gather(folder)
    if not args.words:
        if args.json:
            print(json.dumps({t: sum(1 for u in units if u.tier == t) for t in TIERS}))
        else:
            print(tier_map(folder, units))
        return 0
    want = "long-term" if args.tier == "long" else args.tier
    words = [w for w in re.findall(r"[a-z0-9][a-z0-9._-]*", args.words.lower()) if len(w) > 1]
    scored = []
    for u in units:
        if want != "all" and u.tier != want:
            continue
        hay = (u.title + "\n" + u.text).lower()
        hits = sum(1 for w in words if w in hay)
        if hits:
            scored.append((hits, u))
    scored.sort(key=lambda x: (-x[0], TIERS.index(x[1].tier), "".join(chr(255 - ord(c)) for c in x[1].date)))
    top = scored[: args.limit]
    if args.json:
        print(json.dumps([{**asdict(u), "matched": h, "snippet": snippet(u.text, words)} for h, u in top], indent=2))
        return 0
    if not top:
        print(f"Nothing in {folder.name}'s current, recent, long-term or record tiers mentions: {args.words}")
        return 0
    for h, u in top:
        print(f"[{u.tier}] {u.date or 'undated'} · {u.title[:90]}  ({u.source})")
        print(f"    {snippet(u.text, words)}")
    if len(scored) > len(top):
        print(f"... {len(scored) - len(top)} more (--limit)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
