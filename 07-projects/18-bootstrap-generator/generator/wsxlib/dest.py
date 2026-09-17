"""Destination map + harvest — where generated files live.

Vendor panels (canvases, Artifacts, HTML previews) are not durable. The original
is a file on a path the person named. This module is the mechanical hand:

  * `context/destinations.yaml` — the seam (shape, never a cloned slug table)
  * `wsx dest add|list|bind`
  * `wsx artifact ingest` — secret-scan, never overwrite (version bump)
  * `wsx canvas harvest [--check]` — Cursor dual-home when that folder exists

Walls are by `scope` + `wall` (vault | external), not employer org names.
Never auto-commit a dest that is a different git remote.
"""
from __future__ import annotations

import datetime as dt
import shutil
import subprocess
from pathlib import Path

from . import core, layout, secretscan, yamlio

SCOPES = ("personal", "work", "other")
WALLS = ("vault", "external")
KINDS = ("canvas", "artifact", "html", "file")
_CURSOR_PROJECTS = Path.home() / ".cursor" / "projects"


def _map_path(root: Path) -> Path:
    # Consumed / adapted vaults keep the dest map in `.wsx/` so dest add never
    # invents a parallel `06-context/` on someone else's layout.
    if (root / ".wsx" / "dialect.json").exists() or (root / ".wsx" / "adapter.json").exists():
        return root / ".wsx" / "destinations.yaml"
    return layout.of(root).dir("context") / "destinations.yaml"


def empty_map(root: Path) -> dict:
    """Neutral default: vault dest, no binds. 05-artifacts stays optional on disk."""
    dia = layout.dialect(root)
    guesses = dia.get("dest_guesses") or []
    if guesses:
        dests = {}
        for g in guesses:
            name = str(g.get("name") or "vault")
            dests[name] = {
                "path": str(g.get("path") or "."),
                "scope": str(g.get("scope") or "personal"),
                "kinds": list(KINDS),
                "wall": str(g.get("wall") or "vault"),
            }
        default = str(dia.get("dest_default") or next(iter(dests)))
        return {"default": default, "dests": dests, "binds": {}}
    art = layout.of(root).name("artifacts")
    return {
        "default": "vault",
        "dests": {
            "vault": {
                "path": f"{art}/active",
                "scope": "personal",
                "kinds": list(KINDS),
                "wall": "vault",
            }
        },
        "binds": {},
    }


def load(root: Path) -> dict:
    p = _map_path(root)
    if not p.exists():
        return empty_map(root)
    data = yamlio.loads(p.read_text(encoding="utf-8")) or {}
    base = empty_map(root)
    dests = dict(base["dests"])
    dests.update(data.get("dests") or {})
    binds = dict(data.get("binds") or {})
    return {
        "default": str(data.get("default") or base["default"]),
        "dests": dests,
        "binds": binds,
    }


def save(root: Path, data: dict) -> Path:
    p = _map_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    body = (
        "# Destination map — where generated files live. Shape, not a dump of any\n"
        "# one person's folders. Edit with `wsx dest add` / `wsx dest bind`.\n"
        "# Do not paste this table into always-on adapters.\n\n"
        + yamlio.dumps(data) + "\n"
    )
    p.write_text(body, encoding="utf-8")
    return p


def ensure_map(root: Path) -> dict:
    p = _map_path(root)
    if not p.exists():
        data = empty_map(root)
        save(root, data)
        return data
    return load(root)


def _resolve_dest_path(root: Path, rec: dict) -> Path:
    raw = str(rec.get("path") or "").strip()
    if not raw:
        raise SystemExit("error: dest has no path")
    p = Path(raw).expanduser()
    if not p.is_absolute():
        p = (root / p).resolve()
    else:
        p = p.resolve()
    return p


def _inside_vault(root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _wall_ok(root: Path, rec: dict, dest_path: Path) -> str | None:
    """Return a refuse reason, or None if the write is allowed."""
    wall = str(rec.get("wall") or "vault")
    inside = _inside_vault(root, dest_path)
    if wall == "external" and inside:
        return "wall:external dest refuses the vault — pick an outside path"
    if wall == "vault" and not inside:
        return "wall:vault dest must stay inside this workspace"
    return None


def _other_remote(root: Path, dest_path: Path) -> str | None:
    """If dest sits in a different git repo, return that repo's origin (or '(local)')."""
    vault_origin = (core.git(root, "remote", "get-url", "origin",
                             check=False, capture=True).stdout or "").strip()
    here = dest_path if dest_path.is_dir() else dest_path.parent
    probe = here if here.exists() else here.parent
    info = core.git(probe, "rev-parse", "--show-toplevel", check=False, capture=True)
    top = (info.stdout or "").strip()
    if not top:
        return None
    if Path(top).resolve() == root.resolve():
        return None
    origin = (core.git(Path(top), "remote", "get-url", "origin",
                       check=False, capture=True).stdout or "").strip()
    if origin and origin == vault_origin:
        return None
    return origin or "(local repo, no origin)"


def dest_add(root: Path, name: str, path: str, scope: str = "personal",
             kinds: str = "", wall: str = "") -> int:
    name = _slug(name)
    if not name:
        raise SystemExit("error: dest name required")
    if scope not in SCOPES:
        raise SystemExit(f"error: --scope must be one of {', '.join(SCOPES)}")
    data = ensure_map(root)
    dest_path = Path(path).expanduser()
    if not dest_path.is_absolute():
        dest_path = (root / dest_path).resolve()
    else:
        dest_path = dest_path.resolve()
    inside = _inside_vault(root, dest_path)
    wall = wall or ("vault" if inside else "external")
    if wall not in WALLS:
        raise SystemExit(f"error: --wall must be one of {', '.join(WALLS)}")
    rec = {
        "path": path,
        "scope": scope,
        "kinds": _parse_kinds(kinds),
        "wall": wall,
    }
    reason = _wall_ok(root, rec, dest_path)
    if reason:
        raise SystemExit(f"error: {reason}")
    data["dests"][name] = rec
    save(root, data)
    print(f"✓ dest '{name}' → {path}  (scope={scope}, wall={wall})")
    if not inside:
        print("  (external — files here never enter this vault)")
    _maybe_inbox(root, data)
    from . import interview
    interview.try_refresh(root)
    return 0


def dest_bind(root: Path, key: str, name: str) -> int:
    data = ensure_map(root)
    if name not in data["dests"]:
        raise SystemExit(f"error: unknown dest '{name}'. wsx dest list")
    data.setdefault("binds", {})[key] = name
    save(root, data)
    print(f"✓ bind '{key}' → dest '{name}'")
    return 0


def dest_list(root: Path) -> int:
    data = ensure_map(root)
    default = data.get("default", "vault")
    print("wsx dest — where generated files live\n")
    print(f"  default: {default}")
    for name, rec in (data.get("dests") or {}).items():
        mark = " (default)" if name == default else ""
        kinds = rec.get("kinds") or KINDS
        if isinstance(kinds, str):
            kinds = [kinds]
        print(f"  · {name}{mark}")
        print(f"      path:  {rec.get('path')}")
        print(f"      scope: {rec.get('scope')}  wall: {rec.get('wall')}")
        print(f"      kinds: {', '.join(kinds)}")
    binds = data.get("binds") or {}
    if binds:
        print("\n  binds:")
        for k, v in binds.items():
            print(f"    {k} → {v}")
    else:
        print("\n  binds: (none — `wsx dest bind <slug-or-prefix> <name>`)")
    return 0


def _parse_kinds(raw: str) -> list:
    if not raw:
        return list(KINDS)
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    bad = [p for p in parts if p not in KINDS]
    if bad:
        raise SystemExit(f"error: unknown kind(s) {', '.join(bad)}. choose: {', '.join(KINDS)}")
    return parts


def _slug(name: str) -> str:
    keep = "-".join(name.strip().lower().split())
    return "".join(c for c in keep if c.isalnum() or c in "-_") or ""


def _maybe_inbox(root: Path, data: dict) -> None:
    """Inbox exists only when the default dest is inside the vault."""
    default = data["dests"].get(data.get("default") or "vault") or {}
    if str(default.get("wall") or "vault") != "vault":
        return
    inbox = layout.of(root).dir("artifacts") / "inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    readme = inbox / "README.md"
    if not readme.exists():
        readme.write_text(
            "# Inbox\n\nDrop vendor-surface files here, then `wsx artifact ingest --inbox`.\n",
            encoding="utf-8",
        )


def _pick_dest(root: Path, data: dict, name: str = "", project: str = "") -> tuple[str, dict]:
    if name:
        rec = (data.get("dests") or {}).get(name)
        if not rec:
            raise SystemExit(f"error: unknown dest '{name}'. wsx dest list")
        return name, rec
    if project:
        # A project dest named after the slug, else default.
        rec = (data.get("dests") or {}).get(project)
        if rec:
            return project, rec
        # Fall back: project folder canvases/artifacts inside the vault.
        pj = layout.of(root).name("projects")
        rec = {
            "path": f"{pj}/{project}/artifacts",
            "scope": "personal",
            "kinds": list(KINDS),
            "wall": "vault",
        }
        return project, rec
    default = str(data.get("default") or "vault")
    rec = (data.get("dests") or {}).get(default)
    if not rec:
        raise SystemExit("error: default dest missing. wsx dest add vault --path …")
    return default, rec


def _sniff(text: str, source_name: str = "") -> str:
    suffix = Path(source_name).suffix.lower()
    if suffix in {".html", ".htm"}:
        return "html"
    if suffix in {".tsx"} or source_name.endswith(".canvas.tsx"):
        return "canvas"
    if suffix in {".md", ".markdown"}:
        return "md"
    s = text.lstrip().lower()
    if s.startswith("<!doctype html") or s.startswith("<html"):
        return "html"
    if 'from "cursor/canvas"' in text or "from 'cursor/canvas'" in text:
        return "canvas"
    return "md"


def _ext_for(kind: str) -> str:
    return {"html": "html", "canvas": "canvas.tsx", "md": "md"}.get(kind, "txt")


def _versioned(dest_dir: Path, stem: str, ext: str) -> Path:
    day = dt.date.today().isoformat()
    major, minor = 1, 0
    while True:
        cand = dest_dir / f"{stem}_v{major}.{minor}_{day}.{ext}"
        if not cand.exists():
            return cand
        minor += 1
        if minor > 99:
            major += 1
            minor = 0


def _provenance(text: str, kind: str, source: str) -> str:
    day = dt.date.today().isoformat()
    note = f"captured: {day} · source: {source} · via: wsx-artifact-ingest"
    if "via: wsx-artifact-ingest" in text:
        return text
    if kind == "html":
        return f"<!-- {note} -->\n" + text
    if kind == "canvas":
        return f"// {note}\n" + text
    if text.lstrip().startswith("---"):
        return text
    return f"---\ncaptured: {day}\nsource: {source}\nvia: wsx-artifact-ingest\n---\n\n" + text


def _write_text(root: Path, rec: dict, dest_path: Path, text: str) -> Path:
    hits = secretscan.scan_text(text)
    if secretscan.blocked(hits):
        kinds = ", ".join(sorted({h["kind"] for h in hits if h["severity"] == "block"}))
        raise SystemExit(f"error: secret scan hit ({kinds}) — not written")
    reason = _wall_ok(root, rec, dest_path)
    if reason:
        raise SystemExit(f"error: {reason}")
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    dest_path.write_text(text, encoding="utf-8")
    other = _other_remote(root, dest_path)
    if other:
        print(f"  ⚠ wrote outside this vault's git remote ({other}).")
        print("    Commit there — wsx will not auto-commit a different repo.")
    return dest_path


def _read_clipboard() -> str:
    last = "no clipboard tool"
    for cmd in (["pbpaste"], ["wl-paste"],
                ["xclip", "-selection", "clipboard", "-o"]):
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        except OSError as e:
            last = str(e)
            continue
        if proc.returncode == 0:
            return proc.stdout
        last = (proc.stderr or "").strip() or f"{cmd[0]} exit {proc.returncode}"
    raise SystemExit(f"error: clipboard read failed ({last})")


def artifact_ingest(root: Path, from_file: str = "", from_clipboard: bool = False,
                    inbox: bool = False, dest: str = "", project: str = "",
                    stem: str = "ingest") -> int:
    data = ensure_map(root)
    _maybe_inbox(root, data)
    name, rec = _pick_dest(root, data, dest, project)
    dest_dir = _resolve_dest_path(root, rec)

    sources: list[tuple[str, str]] = []  # (text, source_label)
    if from_file:
        p = Path(from_file).expanduser()
        if not p.is_file():
            raise SystemExit(f"error: not a file: {p}")
        sources.append((p.read_text(encoding="utf-8"), p.name))
    elif from_clipboard:
        sources.append((_read_clipboard(), "clipboard"))
    elif inbox:
        inbox_dir = layout.of(root).dir("artifacts") / "inbox"
        if not inbox_dir.is_dir():
            print("artifact ingest: inbox empty (no inbox dir)")
            return 0
        for f in sorted(inbox_dir.iterdir()):
            if f.name.startswith(".") or f.name.lower() in {"readme.md", ".ds_store"}:
                continue
            if not f.is_file():
                continue
            try:
                sources.append((f.read_text(encoding="utf-8"), f.name))
            except (OSError, UnicodeDecodeError):
                print(f"  ⚠ skip binary/unreadable {f.name}")
    else:
        raise SystemExit("error: pass --from-file PATH, --from-clipboard, or --inbox")

    if not sources:
        print("artifact ingest: nothing to write")
        return 0

    n = 0
    for text, label in sources:
        if not text.strip():
            print(f"  ⚠ skip empty {label}")
            continue
        kind = _sniff(text, label)
        out = _versioned(dest_dir, _slug(stem) or "ingest", _ext_for(kind))
        _write_text(root, rec, out, _provenance(text, kind, label))
        print(f"  ✓ {out.relative_to(root) if _inside_vault(root, out) else out}  [{name}/{kind}]")
        n += 1
        if inbox:
            done = layout.of(root).dir("artifacts") / "inbox" / ".done"
            done.mkdir(parents=True, exist_ok=True)
            src = layout.of(root).dir("artifacts") / "inbox" / label
            if src.exists():
                shutil.move(str(src), str(done / label))
    print(f"✓ ingested {n} file(s) → dest '{name}'")
    return 0


def _bind_match(binds: dict, slug: str, filename: str) -> str | None:
    """First matching bind wins: exact slug, then filename prefix."""
    if slug in binds:
        return binds[slug]
    for key, dest in binds.items():
        if filename.startswith(key):
            return dest
    return None


def canvas_harvest(root: Path, check: bool = False) -> int:
    """Copy Cursor-local canvases into dests from the map.

    `--check` is a clean pass if `~/.cursor/projects` is absent (CI cannot see it).
    Unmapped slugs warn; they fail `--check` only when Cursor is present.
    """
    data = ensure_map(root)
    binds = data.get("binds") or {}
    live = _CURSOR_PROJECTS
    if not live.is_dir():
        if check:
            print("canvas harvest --check: no ~/.cursor/projects (clean pass)")
        else:
            print("canvas harvest: no ~/.cursor/projects — nothing to copy")
        return 0
    if check and not binds:
        print("canvas harvest --check: no binds yet (clean pass)")
        return 0

    copied = 0
    unmapped = []
    for slug_dir in sorted(p for p in live.iterdir() if p.is_dir()):
        canvases = slug_dir / "canvases"
        if not canvases.is_dir():
            continue
        files = [f for f in canvases.iterdir()
                 if f.is_file() and not f.name.startswith(".")]
        if not files:
            continue
        for f in files:
            dest_name = _bind_match(binds, slug_dir.name, f.name)
            if not dest_name:
                unmapped.append(f"{slug_dir.name}/{f.name}")
                continue
            rec = (data.get("dests") or {}).get(dest_name)
            if not rec:
                unmapped.append(f"{slug_dir.name}/{f.name} (dest '{dest_name}' missing)")
                continue
            dest_dir = _resolve_dest_path(root, rec)
            reason = _wall_ok(root, rec, dest_dir)
            if reason:
                print(f"  ⚠ skip {f.name}: {reason}")
                continue
            dest_dir.mkdir(parents=True, exist_ok=True)
            target = dest_dir / f.name
            if target.exists() and target.read_bytes() == f.read_bytes():
                continue
            if check:
                print(f"  drift: {slug_dir.name}/{f.name} → {dest_name}")
                copied += 1
                continue
            if target.exists():
                target = _versioned(dest_dir, f.stem, f.suffix.lstrip(".") or "tsx")
            shutil.copy2(f, target)
            other = _other_remote(root, target)
            rel = target.relative_to(root) if _inside_vault(root, target) else target
            print(f"  ✓ {rel}")
            if other:
                print(f"    ⚠ different git remote ({other}) — do not auto-commit from this vault")
            copied += 1

    if unmapped:
        print(f"  ⚠ {len(unmapped)} unmapped canvas(es) — `wsx dest bind <slug-or-prefix> <name>`")
        for u in unmapped[:8]:
            print(f"      {u}")
        if len(unmapped) > 8:
            print(f"      …and {len(unmapped) - 8} more")
    if check:
        if copied or unmapped:
            print(f"canvas harvest --check: {copied} drift, {len(unmapped)} unmapped")
            return 1
        print("canvas harvest --check: clean")
        return 0
    print(f"✓ canvas harvest: {copied} copied, {len(unmapped)} unmapped")
    return 0


def harvest_on_session_end(root: Path) -> None:
    """Filesystem surfaces: harvest is a step of session end. Never fails the session.

    No-op when the person has not bound any Cursor slugs — otherwise every unmapped
    canvas in ~/.cursor would spam the close-out.
    """
    try:
        data = load(root)
        if not (data.get("binds") or {}):
            return
        canvas_harvest(root, check=False)
    except Exception as e:  # noqa: BLE001
        print(f"  ⚠ canvas harvest skipped: {e}")


# ------------------------------------------------------------------ CLI ---
def run_dest(root: Path, action: str, **kw) -> int:
    if action == "add":
        return dest_add(root, kw.get("name") or "", kw.get("path") or "",
                        scope=kw.get("scope") or "personal",
                        kinds=kw.get("kinds") or "",
                        wall=kw.get("wall") or "")
    if action == "bind":
        return dest_bind(root, kw.get("key") or "", kw.get("name") or "")
    if action == "list" or not action:
        return dest_list(root)
    raise SystemExit("error: dest expects add|list|bind")
