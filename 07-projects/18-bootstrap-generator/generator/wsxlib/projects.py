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

import shutil
from pathlib import Path

from . import core, layout, moc


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


def _board_md(title: str, slug: str, pjdir: str = "projects") -> str:
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
        f'TASK FROM "{pjdir}/{slug}" WHERE contains(tags, "#status/doing")',
        "```",
        "- [ ] _(a task in progress)_ #status/doing",
        "",
        "## To do",
        "```dataview",
        f'TASK FROM "{pjdir}/{slug}" WHERE contains(tags, "#status/todo")',
        "```",
        "- [ ] _(a queued task)_ #status/todo",
        "",
        "## Done",
        "```dataview",
        f'TASK FROM "{pjdir}/{slug}" WHERE contains(tags, "#status/done")',
        "```",
        "- [x] _(a finished task)_ #status/done",
        "",
    ]) + "\n"


def new(root: Path, name: str, title: str = "") -> int:
    slug = _slug(name)
    pj = layout.of(root).name("projects")
    pdir = root / pj / slug
    if pdir.exists():
        raise SystemExit(f"error: project '{slug}' already exists ({pdir.relative_to(root)})")
    disp = title or name.strip() or slug
    (pdir / "notes").mkdir(parents=True, exist_ok=True)
    (pdir / "PROJECT.md").write_text(_project_md(disp, slug, core.today()), encoding="utf-8")
    (pdir / "board.md").write_text(_board_md(disp, slug, pj), encoding="utf-8")
    (pdir / "notes" / "README.md").write_text(_NOTES_README, encoding="utf-8")
    moc.write_mocs(root)  # relink HOME + projects index
    print(f"✓ project '{slug}' created  ({pj}/{slug}/)")
    print("  documentation only — point PROJECT.md at the code repo; don't copy code in.")
    print(f"  fill in PROJECT.md, then it shows up in {pj}/_INDEX.md and HOME.md.")
    return 0


# ------------------------------------------------------------------- adopt ---
# Directories/files we never scan into or copy from — build noise + secret-bearing files.
_SCAN_SKIP_DIRS = {".git", "node_modules", "dist", "build", "target", ".venv",
                   "__pycache__", ".next", ".turbo", "vendor", ".idea", ".vscode"}
_SECRET_HINTS = (".env", ".pem", ".key", ".p12", ".pfx", "id_rsa", "id_ed25519",
                 ".keystore", ".secret")
_DOC_EXT = {".md", ".markdown", ".txt", ".rst", ".adoc", ".pdf", ".doc", ".docx"}
_LANG_EXT = {".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
             ".jsx": "JavaScript", ".rs": "Rust", ".go": "Go", ".java": "Java",
             ".kt": "Kotlin", ".rb": "Ruby", ".php": "PHP", ".swift": "Swift",
             ".c": "C", ".cpp": "C++", ".cs": "C#", ".sh": "Shell", ".css": "CSS",
             ".html": "HTML", ".vue": "Vue", ".svelte": "Svelte"}
_ADOPT_START = "<!-- wsx:adopt:start -->"
_ADOPT_END = "<!-- wsx:adopt:end -->"


def _looks_secret(name: str) -> bool:
    low = name.lower()
    return any(h in low for h in _SECRET_HINTS)


def _git_info(src: Path) -> dict:
    if not (src / ".git").exists():
        return {"is_repo": False, "remote": "", "branch": ""}
    r = core.git(src, "remote", "get-url", "origin", check=False, capture=True)
    b = core.git(src, "rev-parse", "--abbrev-ref", "HEAD", check=False, capture=True)
    return {"is_repo": True, "remote": (r.stdout or "").strip(),
            "branch": (b.stdout or "").strip()}


def _scan_source(src: Path) -> dict:
    """Read-only scan: README, language mix, doc files (outside build/vcs noise)."""
    readme, langs, docs = "", {}, []
    for p in src.rglob("*"):
        parts = p.relative_to(src).parts
        if any(seg in _SCAN_SKIP_DIRS for seg in parts):
            continue
        if not p.is_file():
            continue
        ext = p.suffix.lower()
        if p.name.lower().startswith("readme") and not readme:
            readme = str(p.relative_to(src))
        if ext in _LANG_EXT:
            langs[_LANG_EXT[ext]] = langs.get(_LANG_EXT[ext], 0) + 1
        elif ext in _DOC_EXT and not _looks_secret(p.name):
            docs.append(str(p.relative_to(src)))
    stack = ", ".join(f"{k} ({v})" for k, v in
                      sorted(langs.items(), key=lambda kv: -kv[1])[:4]) or "(not detected)"
    return {"readme": readme, "stack": stack, "docs": sorted(docs)}


def _adoption_block(src: Path, gi: dict, scan: dict, imported: list, date: str) -> str:
    loc = gi["remote"] or str(src)
    lines = [_ADOPT_START,
             "## Adoption record (generated — regenerated on re-adopt)",
             "",
             f"- **Adopted:** {date} · **Source:** `{src}`",
             f"- **Code lives at:** {loc}"
             + (f"  ·  branch `{gi['branch']}`" if gi.get("branch") else ""),
             f"- **Type:** {'git repository (referenced in place — files NOT copied in)' if gi['is_repo'] else 'plain folder'}",
             f"- **Stack:** {scan['stack']}",
             f"- **README:** {('`' + scan['readme'] + '`') if scan['readme'] else '(none found)'}",
             ""]
    if scan["docs"]:
        lines.append(f"- **Documentation found ({len(scan['docs'])})** — referenced at their real "
                     "location (use `--import-docs` to copy a plain folder's docs into `notes/`):")
        for d in scan["docs"][:20]:
            lines.append(f"    - `{d}`")
        if len(scan["docs"]) > 20:
            lines.append(f"    - …and {len(scan['docs']) - 20} more")
    if imported:
        lines.append(f"- **Imported into `notes/` ({len(imported)}):** "
                     + ", ".join(f"`{n}`" for n in imported[:12])
                     + (" …" if len(imported) > 12 else ""))
    lines.append(_ADOPT_END)
    return "\n".join(lines) + "\n"


def _upsert_adoption(project_md: Path, block: str) -> None:
    """Insert or replace the marker-delimited adoption block, preserving everything else."""
    import re
    text = project_md.read_text(encoding="utf-8")
    pat = re.compile(re.escape(_ADOPT_START) + r".*?" + re.escape(_ADOPT_END), re.DOTALL)
    if pat.search(text):
        text = pat.sub(lambda _m: block.rstrip("\n"), text)
    else:
        text = text.rstrip() + "\n\n" + block
    project_md.write_text(text, encoding="utf-8")


def adopt(root: Path, path: str, move: bool = False, import_docs: bool = False,
          title: str = "") -> int:
    src = Path(path).expanduser().resolve()
    if not src.is_dir():
        raise SystemExit(f"error: {src} is not a directory. `wsx project adopt <path-to-project>`.")
    if src == root or root in src.parents or src in root.parents:
        # Adopting the vault itself, or a dir containing it, would be circular.
        if src == root:
            raise SystemExit("error: that's the workspace itself — nothing to adopt.")
    slug = _slug(title or src.name)
    lay = layout.of(root)
    pj = lay.name("projects")
    pdir = root / pj / slug
    disp = title or src.name

    # --move: git-aware physical relocation so the CODE sits BESIDE the vault (never inside
    # it — the vault stays a clean, token-cheap git citizen). Moving the whole folder keeps
    # its own .git intact. Refuse if the destination is taken.
    if move:
        dest = root.parent / slug
        if dest.exists():
            raise SystemExit(f"error: --move target already exists: {dest}")
        shutil.move(str(src), str(dest))
        print(f"  ✓ moved {src}  ->  {dest}  (code now lives beside the vault)")
        src = dest

    gi = _git_info(src)
    scan = _scan_source(src)

    first = not pdir.exists()
    (pdir / "notes").mkdir(parents=True, exist_ok=True)
    if first:
        (pdir / "PROJECT.md").write_text(_project_md(disp, slug, core.today()), encoding="utf-8")
        (pdir / "board.md").write_text(_board_md(disp, slug, pj), encoding="utf-8")
        (pdir / "notes" / "README.md").write_text(_NOTES_README, encoding="utf-8")

    # Docs routing. A git repo is REFERENCED ONLY — never copy its tracked content into the
    # (public) vault: that's the reference-in-place principle AND the employer/public-repo
    # wall. Copying loose docs is offered only for a PLAIN folder, and skips secret-like files.
    imported = []
    if import_docs:
        if gi["is_repo"]:
            print("  ⚠ --import-docs ignored: the source is a git repository. Repo content stays")
            print("    in the repo (referenced here); copying it into a public vault could cross")
            print("    the employer/public wall. Reference-in-place is used instead.")
        else:
            notes_dir = pdir / "notes"
            for rel in scan["docs"]:
                sp = src / rel
                if _looks_secret(sp.name):
                    continue
                dst = notes_dir / Path(rel).name
                if dst.exists():
                    continue  # idempotent: don't re-copy / overwrite
                try:
                    dst.write_text(
                        f"> _Imported by `wsx project adopt` from `{sp}` on {core.today()}._\n\n"
                        + sp.read_text(encoding="utf-8"), encoding="utf-8")
                    imported.append(Path(rel).name)
                except (OSError, UnicodeDecodeError):
                    continue  # binary/unreadable docs (pdf/docx) are referenced, not copied

    _upsert_adoption(pdir / "PROJECT.md", _adoption_block(src, gi, scan, imported, core.today()))
    moc.write_mocs(root)

    verb = "adopted" if first else "re-adopted (refreshed)"
    print(f"✓ {verb} '{slug}'  ({pj}/{slug}/PROJECT.md)")
    print(f"  code referenced in place at: {gi['remote'] or src}"
          + (f"  ·  branch {gi['branch']}" if gi.get("branch") else ""))
    if gi["is_repo"]:
        print("  (git repo — its files are NOT copied into the vault; the vault only points at it.)")
    if scan["docs"] and not imported and not gi["is_repo"]:
        print(f"  {len(scan['docs'])} doc(s) found — referenced. Add --import-docs to copy them into notes/.")
    print(f"  fill in PROJECT.md's overview + handoff; it now shows in {pj}/_INDEX.md and HOME.md.")
    return 0


def list_projects(root: Path) -> int:
    pdir = layout.of(root).dir("projects")
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
