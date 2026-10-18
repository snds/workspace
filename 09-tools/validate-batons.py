#!/usr/bin/env python3
"""
validate-batons.py

Checks every baton against the memory-tier convention ([[decision-memory-tiers]], D98), so an
agent on any surface — with or without the workspace app — keeps it:

  fail  the long-term tier isn't linked: a month file without its back-link, a baton without its
        pointer, or a stale history/README.md (fix: python3 09-tools/build-history-index.py)
  fail  a baton points to history/README.md but no month files sit beside it
  fail  a tracked baton's history files are git-ignored (they'd exist on one machine only;
        allowlist the history/ folder in .gitignore beside the baton's own line)
  warn  a baton over 12 KB, with its biggest parts: move older history to history/YYYY-MM.md
        word for word (the app does this by itself), then trim the Live handoff by hand
  warn  a baton with no Live handoff heading

Batons are 07-projects/<p>/SESSION-STATE.md and scoped ones deeper in a project
(docs/<thread>/SESSION-STATE.md), never inside .claude/, history/ or _archive/.

--lossless checks a move you just made: every word of each baton you changed, and of its month
files, as they are in HEAD, is still in the working tree's baton plus month files. Use it after
splitting a baton by hand. (A Live handoff rewrite drops words on purpose; don't run it for that.)

Usage:
    python3 09-tools/validate-batons.py                 # the checks; exit 1 on a fail
    python3 09-tools/validate-batons.py --strict-size   # a baton over 12 KB fails too
    python3 09-tools/validate-batons.py --lossless [07-projects/x/SESSION-STATE.md ...]
    python3 09-tools/validate-batons.py --self-test
"""

from __future__ import annotations

import argparse
import collections
import importlib.util
import re
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
LIMIT = 12 * 1024
SKIP = {".claude", ".git", "node_modules", "history", "_archive", ".smart-env"}
MONTH = re.compile(r"^\d{4}-\d{2}\.md$")


def load_index_tool(workspace: Path):
    """build-history-index.py, pointed at `workspace` (the self-test uses a temporary one)."""
    spec = importlib.util.spec_from_file_location("build_history_index", TOOLS / "build-history-index.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.WORKSPACE, mod.PROJECTS = workspace, workspace / "07-projects"
    return mod


def batons(workspace: Path) -> list[Path]:
    out = []
    projects = workspace / "07-projects"
    if not projects.is_dir():
        return out
    for b in projects.rglob("SESSION-STATE.md"):
        if not any(p in SKIP for p in b.relative_to(projects).parts[:-1]):
            out.append(b)
    return sorted(out)


def months(baton: Path) -> list[Path]:
    hist = baton.parent / "history"
    return sorted(p for p in hist.iterdir() if MONTH.match(p.name)) if hist.is_dir() else []


def biggest(text: str) -> list[tuple[str, int]]:
    """The three biggest `##`/`###` sections over 1 KB, history aside. As in the app's report, a
    section that holds a part bigger than half of itself gives way to that part."""
    heads = [(m.start(), len(m.group(1)), m.group(2).strip()) for m in re.finditer(r"^(#{2,3}) (.+)$", text, re.M)]
    spans = []
    for i, (at, level, name) in enumerate(heads):
        if level == 2 and "history" in name.lower():
            continue
        end = next((a for a, l, _ in heads[i + 1:] if l <= level), len(text))
        spans.append((name[:48], at, end))
    holds_most = lambda s: any(o[1] > s[1] and o[2] <= s[2] and (o[2] - o[1]) * 2 > s[2] - s[1] for o in spans)
    sizes = [(n, len(text[a:e].encode())) for n, a, e in spans if not holds_most((n, a, e))]
    return sorted((s for s in sizes if s[1] >= 1024), key=lambda s: -s[1])[:3]


def git(workspace: Path, *args: str, stdin: str = "") -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(workspace), *args], input=stdin, capture_output=True, text=True)


def check(workspace: Path, strict_size: bool = False) -> tuple[list[str], list[str]]:
    fails, warns = [], []
    rel = lambda p: str(p.relative_to(workspace))
    index_tool = load_index_tool(workspace)
    for path in index_tool.plan():
        fails.append(f"{rel(path)}: the long-term tier's links are stale; run python3 09-tools/build-history-index.py")
    found = batons(workspace)
    tracked = set(git(workspace, "ls-files", "--", "07-projects").stdout.splitlines())
    for b in found:
        text = b.read_text(encoding="utf-8", errors="replace")
        ms = months(b)
        if "](history/README.md)" in text and not ms:
            fails.append(f"{rel(b)}: points to history/README.md, but no month files sit beside it")
        if rel(b) in tracked and ms:
            hist = [rel(m) for m in ms] + [rel(b.parent / "history" / "README.md")]
            ignored = git(workspace, "check-ignore", "--no-index", "--stdin", stdin="\n".join(hist) + "\n").stdout.split()
            if ignored:
                fails.append(f"{rel(b)}: tracked, but {len(ignored)} of its history files are git-ignored "
                             f"(e.g. {ignored[0]}); allowlist its history/ folder in .gitignore")
        size = len(text.encode())
        if size > LIMIT:
            parts = ", ".join(f"“{n}” {s / 1024:.1f} KB" for n, s in biggest(text))
            msg = (f"{rel(b)}: {size / 1024:.1f} KB, over the 12 KB a quick read allows"
                   + (f" (biggest: {parts})" if parts else "")
                   + "; move older history to history/YYYY-MM.md word for word, then trim the Live handoff")
            (fails if strict_size else warns).append(msg)
        if not re.search(r"^#{1,6} .*live handoff", text, re.I | re.M):
            warns.append(f"{rel(b)}: no Live handoff heading (01-frameworks/_session-state-template.md)")
    return fails, warns


def words(text: str) -> collections.Counter:
    return collections.Counter(w.lower() for w in re.findall(r"\w+", text))


def lossless(workspace: Path, only: list[str]) -> list[str]:
    """Words a baton move lost against HEAD, per baton changed (or named)."""
    if only:
        targets = [workspace / p for p in only]
    else:
        changed = git(workspace, "diff", "--name-only", "HEAD", "--", "07-projects").stdout.splitlines()
        targets = [workspace / p for p in changed if p.endswith("SESSION-STATE.md")]
    problems = []
    for b in targets:
        r = str(b.relative_to(workspace))
        head = git(workspace, "show", f"HEAD:{r}").stdout
        hist = str(b.parent.relative_to(workspace) / "history")
        head_months = [p for p in git(workspace, "ls-tree", "--name-only", "HEAD", f"{hist}/").stdout.split()
                       if MONTH.match(Path(p).name)]
        for m in head_months:
            head += git(workspace, "show", f"HEAD:{m}").stdout
        now = b.read_text(encoding="utf-8", errors="replace") if b.is_file() else ""
        now += "".join(m.read_text(encoding="utf-8", errors="replace") for m in months(b))
        missing = words(head) - words(now)
        if missing:
            top = ", ".join(w for w, _ in missing.most_common(8))
            problems.append(f"{r}: {sum(missing.values())} words from HEAD are gone (e.g. {top})")
    return problems


def self_test() -> int:
    with tempfile.TemporaryDirectory() as d:
        ws = Path(d)
        git(ws, "init", "-q")
        (ws / ".gitignore").write_text("*\n!.gitignore\n!07-projects/\n!07-projects/a/\n!07-projects/a/SESSION-STATE.md\n"
                                       "!07-projects/b/\n!07-projects/b/**\n")
        a = ws / "07-projects/a"
        (a / "history").mkdir(parents=True)
        entries = "".join(f"### 2026-09-{n:02} — e{n}\n\nwords{n}\n\n" for n in range(1, 4))
        (a / "SESSION-STATE.md").write_text("# A\n\n### Live handoff\n\n- **Next action**: x\n\n## Session history\n\n" + entries)
        (a / "history" / "2026-08.md").write_text("# History, 2026-08\n\n### 2026-08-01 — old\n\nold words\n")
        (ws / "07-projects/b").mkdir(parents=True)
        (ws / "07-projects/b/SESSION-STATE.md").write_text("# B\n\nno handoff\n" + "x" * (LIMIT + 10) + "\n")
        git(ws, "add", "-A")
        git(ws, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "seed")
        fails, warns = check(ws)
        assert any("links are stale" in f for f in fails), fails
        assert any("git-ignored" in f for f in fails), fails
        assert any("07-projects/b/SESSION-STATE.md: " in w and "over the 12 KB" in w for w in warns), warns
        assert any("no Live handoff" in w for w in warns), warns
        assert any("over the 12 KB" in f for f in check(ws, strict_size=True)[0])
        tool = load_index_tool(ws)
        for path, text in tool.plan().items():
            path.write_text(text, encoding="utf-8")
        assert not any("links are stale" in f for f in check(ws)[0]), check(ws)[0]
        # A move that keeps every word passes; one that drops an entry doesn't.
        baton = a / "SESSION-STATE.md"
        text = baton.read_text()
        moved = "### 2026-09-01 — e1\n\nwords1\n\n"
        baton.write_text(text.replace(moved, ""))
        assert lossless(ws, ["07-projects/a/SESSION-STATE.md"]), "a dropped entry is caught"
        m = a / "history" / "2026-09.md"
        m.write_text("# History, 2026-09\n\n" + moved)
        assert lossless(ws, ["07-projects/a/SESSION-STATE.md"]) == [], "a move that keeps every word passes"
        (a / "history" / "2026-09.md").unlink()
        (a / "history" / "2026-08.md").unlink()
        assert any("no month files" in f for f in check(ws)[0])
    print("validate-batons self-test: ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--strict-size", action="store_true", help="a baton over 12 KB fails")
    parser.add_argument("--lossless", nargs="*", metavar="BATON", help="words lost against HEAD by a baton move")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    workspace = TOOLS.parent
    if args.lossless is not None:
        problems = lossless(workspace, args.lossless)
        for p in problems:
            print(f"✗ {p}", file=sys.stderr)
        print("batons lossless: " + ("FAIL" if problems else "ok — every word from HEAD is still there"))
        return 1 if problems else 0
    fails, warns = check(workspace, args.strict_size)
    for w in warns:
        print(f"⚠ {w}")
    for f in fails:
        print(f"✗ {f}", file=sys.stderr)
    n = len(batons(workspace))
    print(f"batons: {n} checked, {len(fails)} failing, {len(warns)} warning")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
