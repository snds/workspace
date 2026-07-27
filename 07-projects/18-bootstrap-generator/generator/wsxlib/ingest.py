"""`wsx ingest` — consent-gated ingestion of OUTSIDE content into the workspace.

Nothing enters tracked files or git without explicit, per-source approval. The pipeline is
deliberately gated at two points (you name a source; you pass `--apply`) and secret-scanned
in between, so a public workspace can absorb a person's scattered notes/projects WITHOUT ever
staging a credential.

  wsx ingest discover            read-only: WHERE content could come from (cloud-sync,
                                 Documents, Desktop, home, note vaults). Copies nothing.
  wsx ingest <path>              stage ONE source: read-only copy of its docs to
                                 .wsx/quarantine/ingest/<name>/, secret-scan, classify, PLAN.
                                 Nothing promoted.
  wsx ingest <path> --apply      after review, promote the SAFE, classified docs into the
                                 vault (knowledge/ · frameworks/ candidates). Secret-bearing
                                 files are NEVER promoted. Project folders are PROPOSED
                                 (reference-in-place `project adopt`), never copied. No commit.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from . import bridges, core, layout, projects, scan, secretscan

# code / vcs / build dirs mark a "project" (referenced in place, never ingested as docs).
_PROJECT_MARKERS = {".git", "package.json", "pyproject.toml", "Cargo.toml", "go.mod",
                    "pom.xml", "build.gradle", "Gemfile", "requirements.txt", "composer.json"}
_DOC_EXT = {".md", ".markdown", ".txt", ".rst", ".adoc"}
_SKIP = {".git", "node_modules", "dist", "build", "target", ".venv", "__pycache__",
         ".next", ".turbo", "vendor", ".idea", ".vscode", ".obsidian", "_archive"}
_FRAMEWORK_HINTS = ("principle", "guideline", "standard", "framework", "convention",
                    "playbook", "philosophy", "manifesto", "best practice", "my approach",
                    "how i ", "rules of", "operating model", "ways of working")


def _looks_project(d: Path) -> bool:
    try:
        names = {p.name for p in d.iterdir()}
    except OSError:
        return False
    if names & _PROJECT_MARKERS:
        return True
    code = sum(1 for p in d.rglob("*") if p.is_file()
               and p.suffix.lower() in projects._LANG_EXT and
               not any(s in p.relative_to(d).parts for s in _SKIP))
    return code >= 3


def _classify_doc(path: Path, text: str) -> str:
    hay = (path.name + "\n" + text[:600]).lower()
    if any(h in hay for h in _FRAMEWORK_HINTS):
        return "framework-candidate"
    return "knowledge"


def quarantine(root: Path) -> Path:
    return bridges.quarantine_dir(root) / "ingest"


# ------------------------------------------------------------------ discover ---
def _toplevel_summary(r: Path, cap: int = 300) -> tuple:
    """TOP-LEVEL only (no recursion) — one bounded scandir, so a cloud/hydrating folder can
    never hang discovery. Returns (top-level *.md count, subfolder count). `wsx ingest <path>`
    is where the real (opt-in) deep scan happens, on a folder the person explicitly chose."""
    import os
    docs = subs = seen = 0
    try:
        with os.scandir(r) as it:
            for e in it:
                seen += 1
                if seen > cap:
                    break
                try:
                    if e.is_dir(follow_symlinks=False):
                        if not e.name.startswith("."):
                            subs += 1
                    elif e.name.endswith(".md"):
                        docs += 1
                except OSError:
                    continue
    except OSError:
        return 0, 0
    return docs, subs


def _is_cloud(r: Path) -> bool:
    return "CloudStorage" in str(r) or "Mobile Documents" in str(r) or r.name in (
        "Dropbox", "OneDrive", "Google Drive", "GoogleDrive")


def discover(root: Path) -> int:
    print("wsx ingest discover — where your content could come from (read-only; nothing copied)\n")
    # HOME itself is too broad (→ ~/Library etc.); its note-likely subdirs + cloud-sync roots
    # are already in _search_roots. We only read the TOP level here — no deep crawl — so even
    # an online-only cloud folder can't stall this.
    roots = [r for r in scan._search_roots() if r != Path.home()]
    if not roots:
        print("  (no common content locations found.)")
        return 0
    for r in roots:
        docs, subs = _toplevel_summary(r)
        tag = "  (cloud-synced)" if _is_cloud(r) else ""
        print(f"  {scan._tilde(r):48} {docs:>4} md · {subs:3} folders (top level){tag}")
    print("\n  Pick one and stage it (read-only, secret-scanned):  wsx ingest <path>")
    print("  Only LOCALLY-SYNCED files are seen — wsx never touches the network.")
    return 0


# -------------------------------------------------------------------- stage ---
def _gather(src: Path):
    """Yield (kind, path). kind ∈ {project, doc}. Top-level project dirs are referenced in
    place; docs anywhere else are candidates for quarantine+scan."""
    project_dirs = []
    for p in sorted(src.iterdir()):
        if p.is_dir() and p.name not in _SKIP and _looks_project(p):
            project_dirs.append(p)
            yield "project", p
    proj_set = set(project_dirs)
    for p in sorted(src.rglob("*")):
        if not p.is_file():
            continue
        parts = p.relative_to(src).parts
        if any(s in parts for s in _SKIP):
            continue
        if any(pd in p.parents for pd in proj_set):
            continue  # inside a project → referenced, not ingested as a loose doc
        if p.suffix.lower() in _DOC_EXT:
            yield "doc", p


def stage(root: Path, path: str, apply: bool = False) -> int:
    src = Path(path).expanduser().resolve()
    if not src.is_dir():
        raise SystemExit(f"error: {src} is not a directory. `wsx ingest <folder>`.")
    if root == src or root in src.parents:
        raise SystemExit("error: that path is inside the workspace — nothing to ingest.")
    lay = layout.of(root)
    qroot = quarantine(root) / (projects._slug(src.name))
    plan = {"projects": [], "knowledge": [], "framework": [], "blocked": [], "skipped": []}

    for kind, p in _gather(src):
        if kind == "project":
            plan["projects"].append(p)
            continue
        # doc: copy to quarantine (read-only), then secret-scan the quarantined copy
        rel = p.relative_to(src)
        qf = qroot / rel
        qf.parent.mkdir(parents=True, exist_ok=True)
        try:
            if qf.exists():
                qf.chmod(0o644)   # a prior stage left it read-only — allow the refresh
            shutil.copy2(p, qf)
            qf.chmod(0o444)
        except OSError:
            plan["skipped"].append((rel, "unreadable"))
            continue
        findings = secretscan.scan_file(qf)
        if secretscan.blocked(findings):
            plan["blocked"].append((rel, secretscan.summarize(findings)))
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            plan["skipped"].append((rel, "not text"))
            continue
        cat = _classify_doc(p, text)
        review = " ⚠ has public-IP(s) — review" if findings else ""
        (plan["framework"] if cat == "framework-candidate" else plan["knowledge"]).append(
            (rel, p, review))

    _print_plan(src, qroot, root, plan, apply)

    if apply:
        return _apply(root, lay, src, plan)
    return 0


def _print_plan(src, qroot, root, plan, apply):
    print(f"wsx ingest — {'APPLYING' if apply else 'PLAN (dry-run — nothing promoted)'} for {src}\n")
    print(f"  staged (read-only) under {qroot.relative_to(root)}/  — gitignored, not in the vault.\n")
    if plan["blocked"]:
        print(f"  🔒 BLOCKED — {len(plan['blocked'])} file(s) contain secrets; NEVER promoted "
              "(they stay quarantined):")
        for rel, kinds in plan["blocked"][:20]:
            print(f"      · {rel}  [{kinds}]")
        print()
    if plan["projects"]:
        print(f"  📁 PROJECTS — {len(plan['projects'])} folder(s) → proposed as reference-in-place "
              "(code NOT copied in):")
        for p in plan["projects"][:20]:
            print(f"      · {p}   →   wsx project adopt \"{p}\"")
        print()
    if plan["knowledge"]:
        print(f"  🧠 KNOWLEDGE — {len(plan['knowledge'])} doc(s) → knowledge/:")
        for rel, _p, review in plan["knowledge"][:20]:
            print(f"      · {rel}{review}")
        print()
    if plan["framework"]:
        print(f"  🧭 FRAMEWORK CANDIDATES — {len(plan['framework'])} doc(s) → frameworks/ (review + integrate):")
        for rel, _p, review in plan["framework"][:20]:
            print(f"      · {rel}{review}")
        print()
    if plan["skipped"]:
        print(f"  · skipped {len(plan['skipped'])} unreadable/non-text file(s).\n")
    if not apply:
        promotable = len(plan["knowledge"]) + len(plan["framework"])
        print(f"  → {promotable} doc(s) are promotable. Review the plan, then re-run with --apply.")
        if plan["projects"]:
            print("    Adopt project folders yourself with the `wsx project adopt` lines above.")


def _promote(dst: Path, src_file: Path, rel, origin: str) -> bool:
    if dst.exists():
        return False  # idempotent — don't overwrite / re-import
    try:
        body = src_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(f"> _Ingested by `wsx ingest` from `{origin}` on {core.today()} — "
                   "secret-scanned; **review before relying on it**._\n\n" + body,
                   encoding="utf-8")
    return True


def _write_ingested_index(d: Path, label: str) -> None:
    """A tiny index so promoted docs are reachable (not orphans) + easy to review/triage."""
    if not d.is_dir():
        return
    docs = sorted(p.name for p in d.glob("*.md") if p.name != "_INDEX.md")
    if not docs:
        return
    lines = [f"# Ingested {label} — review & triage", "",
             "_Docs pulled in by `wsx ingest` (secret-scanned). Review each, then either fold it",
             "into a real note/skill/framework or `wsx archive` it. Back to [[HOME]]._", ""]
    lines += [f"- [{n[:-3]}]({n})" for n in docs]
    (d / "_INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _apply(root, lay, src, plan) -> int:
    from . import moc
    # Ingested docs land in an `ingested/` subdir so they never collide with (or masquerade
    # as) the person's own scaffold/authored files, and are visibly marked as needing review.
    kdir = lay.dir("knowledge") / "ingested"
    fdir = lay.dir("frameworks") / "ingested"
    n = 0
    for rel, p, _review in plan["knowledge"]:
        if _promote(kdir / (projects._slug(Path(rel).stem) + ".md"), p, rel, str(src)):
            n += 1
    for rel, p, _review in plan["framework"]:
        if _promote(fdir / (projects._slug(Path(rel).stem) + ".md"), p, rel, str(src)):
            n += 1
    for d, label in ((kdir, "knowledge"), (fdir, "framework candidates")):
        _write_ingested_index(d, label)
    moc.write_mocs(root)
    print(f"\n✓ promoted {n} secret-free doc(s) into the vault (with provenance + a review banner).")
    print(f"  BLOCKED files stayed in quarantine ({len(plan['blocked'])}). Project folders were NOT")
    print("  copied — adopt them with the `wsx project adopt` lines above when ready.")
    print("  Nothing was committed — review the additions, then `wsx sync`.")
    return 0


def run(root: Path, path: str = "", apply: bool = False) -> int:
    if not path or path == "discover":
        return discover(root)
    return stage(root, path, apply=apply)
