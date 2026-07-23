"""`wsx project` — per-project DOCUMENTATION folders (not the codebase or assets).

A project folder here holds the *context* an AI needs to help with a project: what
it is, where the code lives (a pointer — repo URL/path), the current handoff state,
decisions, and freeform notes. The code, builds, and binary assets stay in the
project's own repo; this keeps the workspace token-cheap and a clean git citizen.

`projects/<name>/`
  PROJECT.md      overview + code location + live handoff + decisions
  notes/          freeform notes, specs, research (markdown)
"""
from __future__ import annotations

from pathlib import Path

from . import core, moc


def _slug(name: str) -> str:
    keep = "-".join(name.strip().lower().split())
    return "".join(c for c in keep if c.isalnum() or c in "-_") or "project"


def _project_md(title: str, slug: str, date: str) -> str:
    return "\n".join([
        f"# {title}",
        "",
        "_Project **documentation & context** — not the codebase. The code, builds, and",
        "assets live in the project's own repo; this folder is what the AI reads to help._",
        "",
        "## For future agent",
        "- **TL;DR:** _(what this project is + where it stands, in one line.)_",
        "- **Key claims:** _(the load-bearing facts — each timeless / dated / pointer.)_",
        f"- **As of:** {date} · **Status:** current",
        "",
        "## Overview",
        "",
        "_(one paragraph: what this project is, who it's for, and its current goal.)_",
        "",
        "## Where the code lives",
        "",
        "- **Repo / path:** _(git URL or local path — a POINTER, not the code itself)_",
        "- **Stack:** _(languages, frameworks, notable services)_",
        "- **How to run:** _(the one command, or a link to the repo's README)_",
        "",
        "## Live handoff (keep this current)",
        "",
        "- **Status:** _(what state the project is in right now)_",
        "- **In progress:** _(what's actively being worked)_",
        "- **Next:** _(the very next action)_",
        "- **Blocked on:** _(nothing / what)_",
        "",
        "## Decisions",
        "",
        "_(dated, one line each — the choices worth remembering and why.)_",
        "",
        "## Pending",
        "",
        "- [ ] _(open items specific to this project)_",
        "",
        "## Notes & board",
        "",
        f"- **Board:** [board.md](board.md) — tasks by `#status/*` (Dataview-ready).",
        f"- **Notes:** `notes/` — specs, research, and longer notes.",
        "",
    ]) + "\n"


_NOTES_README = ("# Notes\n\n_Freeform project notes, specs, and research (markdown). "
                 "Documentation only — no code or binary assets (those live in the "
                 "project's own repo).\n")


def _board_md(title: str, slug: str) -> str:
    """A lightweight kanban. Uses Dataview if the plugin is installed; otherwise the
    plain checklists below are a perfectly good fallback (no plugin required)."""
    return "\n".join([
        f"# {title} — board",
        "",
        "_Task board for this project. Tag tasks with `#status/todo`, `#status/doing`,",
        "or `#status/done`. If you have the **Dataview** community plugin, the queries",
        "below auto-populate; if not, the plain checklists are the source of truth._",
        "",
        "## Doing",
        "```dataview",
        f'TASK FROM "projects/{slug}" WHERE contains(tags, "#status/doing")',
        "```",
        "- [ ] _(a task in progress)_ #status/doing",
        "",
        "## To do",
        "```dataview",
        f'TASK FROM "projects/{slug}" WHERE contains(tags, "#status/todo")',
        "```",
        "- [ ] _(a queued task)_ #status/todo",
        "",
        "## Done",
        "```dataview",
        f'TASK FROM "projects/{slug}" WHERE contains(tags, "#status/done")',
        "```",
        "- [x] _(a finished task)_ #status/done",
        "",
    ]) + "\n"


def new(root: Path, name: str, title: str = "") -> int:
    slug = _slug(name)
    pdir = root / "projects" / slug
    if pdir.exists():
        raise SystemExit(f"error: project '{slug}' already exists ({pdir.relative_to(root)})")
    disp = title or name.strip() or slug
    (pdir / "notes").mkdir(parents=True, exist_ok=True)
    (pdir / "PROJECT.md").write_text(_project_md(disp, slug, core.today()), encoding="utf-8")
    (pdir / "board.md").write_text(_board_md(disp, slug), encoding="utf-8")
    (pdir / "notes" / "README.md").write_text(_NOTES_README, encoding="utf-8")
    moc.write_mocs(root)  # relink HOME + projects index
    print(f"✓ project '{slug}' created  (projects/{slug}/)")
    print("  documentation only — point PROJECT.md at the code repo; don't copy code in.")
    print("  fill in PROJECT.md, then it shows up in projects/_INDEX.md and HOME.md.")
    return 0


def list_projects(root: Path) -> int:
    pdir = root / "projects"
    found = []
    if pdir.is_dir():
        for d in sorted(pdir.iterdir()):
            if d.is_dir() and not d.name.startswith((".", "_")):
                found.append(d.name)
    if not found:
        print('(no projects yet — create one: wsx project new "My Project")')
        return 0
    print(f"{len(found)} project(s):")
    for n in found:
        print(f"  └─ {n}  (projects/{n}/PROJECT.md)")
    return 0
