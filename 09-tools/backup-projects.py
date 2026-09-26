#!/usr/bin/env python3
"""backup-projects — find project folders with no git repo and back them up to new private GitHub repos.

Walks the projects root (default: the device's projects_root, e.g. ~/Projects) and lists the
folders that are not a git repo, are not inside one, hold at least one real file, and have no
git repo below them (a "leaf project"). A folder that holds repos among its descendants is a
container: it is never a candidate itself; its non-repo children are walked instead. Hidden
folders, dependency and build folders, and the workspace checkout are skipped.

Safety, in order:
  1. Only positively personal folders are touched. The device must be declared in devices.json
     with a personal default identity whose GitHub account is a personal owner in
     context-remotes.json (that account is the repo owner, `snds` on Sean's devices). A folder is
     skipped (not personal) when its path matches an employer path glob, its PROJECT.md declares
     a stricter profile, or a folder between it and the projects root also holds a repo that
     profile_resolve does not resolve as positively personal (employer or unknown owner), or an
     employer checkout from the checkout cache. When unsure, it is skipped.
  2. The default run is a dry run: it prints the plan and writes nothing.
  3. Repos are private. `--public NAME[,NAME...]` makes only the named folders public.
  4. A folder is blocked (with the reason) when it holds a secret-shaped file (.env*, *.pem,
     *.key, id_rsa*, *.p12, credentials JSON and similar), content that check-secrets.py's
     secret patterns match, or any file over 50 MB. A public folder is also scanned with
     check-secrets' employer-substance rules and blocked on any hit.
  5. A default .gitignore is written only where the folder has none.
  6. `--apply` needs a human at a terminal (profile_resolve.agent_check); it asks y/N per repo.
  7. Per repo: git init -b main, add, commit under the device's personal identity, then
     `gh repo create OWNER/NAME --private|--public --source DIR --push`. An existing GitHub repo
     of that name is skipped: nothing is ever pushed to an existing repo.
  8. Nothing is deleted or moved. A folder that became a repo is no longer a candidate.

Usage:
  python3 09-tools/backup-projects.py [--root DIR] [--public NAME[,NAME...]] [--json]
  python3 09-tools/backup-projects.py --apply [--only NAME[,NAME...]] [--public NAME[,NAME...]] [--root DIR]
  python3 09-tools/backup-projects.py --self-test

NAME is a folder's path relative to the root, its folder name, or its planned repo name.
`--tables-root DIR` and `--hostname H` are for tests only (a synthetic workspace root with the
declared tables, and the hostname to resolve the device from); `--hostname` needs `--tables-root`.

Exit codes: 0 ok · 1 an apply step failed · 2 usage (unknown or ambiguous NAME) · 4 refused.
Stdlib only; python3 3.9+.
"""

from __future__ import annotations

import argparse
import fnmatch
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent

PRUNE_DIRS = frozenset({"node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".cache"})
JUNK_FILES = frozenset({".DS_Store", "Thumbs.db", "desktop.ini", "Icon\r"})
MAX_FILE_BYTES = 50 * 1024 * 1024
SCAN_MAX_BYTES = 2_000_000
DEFAULT_GITIGNORE = "\n".join([
    "# Written by backup-projects.py (the folder had no .gitignore)",
    "node_modules/",
    ".venv/",
    "venv/",
    "__pycache__/",
    ".DS_Store",
    "dist/",
    "build/",
    ".env*",
    "*.log",
    "",
])
# Secret-shaped file names (matched case-insensitively against the file name).
SECRET_NAME_GLOBS = (
    ".env", ".env.*", "*.pem", "*.key", "id_rsa*", "id_dsa*", "id_ecdsa*", "id_ed25519*", "*.p12", "*.pfx",
    "*.jks", "*.keystore", "credentials.json", "*credentials*.json", "client_secret*.json",
    "*service-account*.json", "*service_account*.json", ".netrc", ".pypirc",
)
SECRET_NAME_ALLOW_SUFFIXES = (".example",)
COMMIT_MESSAGE = "Initial backup of {folder} (backup-projects.py)"

# Test seam, as in intent-run: None means ask profile_resolve.agent_check().
_HUMAN_OVERRIDE: Optional[bool] = None


# --------------------------------------------------------------------------- modules


def _load(stem: str) -> Any:
    name = stem.replace("-", "_")
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, TOOLS / f"{stem}.py")
    if spec is None or spec.loader is None:
        raise ImportError(stem)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _pr() -> Any:
    return _load("profile_resolve")


def _cs() -> Any:
    return _load("check-secrets")


# --------------------------------------------------------------------------- discovery


def _is_repo(d: Path) -> bool:
    try:
        return (d / ".git").exists() or _pr()._is_bare_repo(d)
    except OSError:
        return True  # unreadable: treat as not ours to touch


def _child_dirs(d: Path) -> List[Path]:
    out = []
    try:
        entries = sorted(os.scandir(d), key=lambda e: e.name)
    except OSError:
        return out
    for e in entries:
        if e.name.startswith(".") or e.name in PRUNE_DIRS:
            continue
        try:
            if e.is_dir(follow_symlinks=False):
                out.append(Path(e.path))
        except OSError:
            continue
    return out


def _loose_files(d: Path) -> int:
    n = 0
    try:
        for e in os.scandir(d):
            if e.name not in JUNK_FILES and e.is_file(follow_symlinks=False):
                n += 1
    except OSError:
        pass
    return n


class Walker:
    """Memoized: which git repos sit below a directory (never descending into a repo)."""

    def __init__(self, tables_root: Optional[Path]) -> None:
        self.tables_root = tables_root
        self._below: Dict[str, List[Path]] = {}

    def is_repo(self, d: Path) -> bool:
        if _is_repo(d):
            return True
        try:
            return _pr().is_workspace_checkout(d, root=self.tables_root)
        except Exception:  # noqa: BLE001
            return False

    def repos_below(self, d: Path) -> List[Path]:
        key = str(d)
        if key not in self._below:
            found: List[Path] = []
            for c in _child_dirs(d):
                if self.is_repo(c):
                    found.append(c)
                else:
                    found.extend(self.repos_below(c))
            self._below[key] = found
        return self._below[key]


def _has_real_file(d: Path) -> bool:
    for top, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x not in PRUNE_DIRS and x != ".git"]
        for f in files:
            if f not in JUNK_FILES and not os.path.islink(os.path.join(top, f)):
                return True
    return False


def discover(root: Path, walker: Walker) -> dict:
    """{candidates, repos, containers, loose, empty}. The root itself is always a container."""
    out: Dict[str, List[Any]] = {"candidates": [], "repos": [], "containers": [], "loose": [], "empty": []}

    def visit(d: Path, is_root: bool) -> None:
        if not is_root and walker.is_repo(d):
            out["repos"].append(d)
            return
        if not is_root and not walker.repos_below(d):
            if _has_real_file(d):
                out["candidates"].append(d)
            else:
                out["empty"].append(d)
            return
        out["containers"].append(d)
        n = _loose_files(d)
        if n and not is_root:
            out["loose"].append((d, n))
        for c in _child_dirs(d):
            visit(c, False)

    visit(root, True)
    return out


# --------------------------------------------------------------------------- classification


class Context:
    """Device, owner and tables: the facts every per-folder decision is made from."""

    def __init__(self, *, tables_root: Optional[Path], hostname: Optional[str], scan_root: Path,
                 home: Optional[Path] = None) -> None:
        pr = _pr()
        self.tables_root = tables_root
        self.scan_root = scan_root
        self.home = home
        self.fatal: Optional[str] = None
        self.device_id = "unknown"
        self.owner: Optional[str] = None
        self.identity: Optional[dict] = None
        self.globs: List[str] = []
        self.conduct: List[str] = []
        self._repo_cls: Dict[str, Tuple[bool, str]] = {}
        try:
            dev_t = pr.load_table("devices", root=tables_root)
            cr = pr.load_table("context-remotes", root=tables_root)
        except pr.TableError as exc:
            self.fatal = f"declared tables unavailable ({exc})"
            return
        self.globs = [str(g) for g in cr.get("employer_path_globs") or []]
        self.conduct = list(cr.get("conduct_order") or [])
        row = pr._resolve_device(hostname, tables_root, None)["row"]
        if row is None:
            self.fatal = "this device is not declared in devices.json"
            return
        self.device_id = str(row.get("id"))
        ident = pr._identities(dev_t).get(str(row.get("default_identity")))
        if not ident or ident.get("class") != "personal":
            self.fatal = f"device {self.device_id} has no personal default identity"
            return
        accounts = [a for a in ident.get("accounts") or [] if isinstance(a, str) and a]
        if not accounts:
            self.fatal = f"identity {ident.get('id')} declares no GitHub account"
            return
        if pr._owner_row_class(cr, "github.com", accounts[0])[0] != "personal":
            self.fatal = f"account {accounts[0]} is not a personal owner in context-remotes.json"
            return
        self.owner = accounts[0]
        self.identity = ident
        pr_root = pr.projects_root(root=tables_root, home=home, hostname=hostname)
        self.base = pr_root if pr._is_under(pr._real(scan_root), pr._real(pr_root)) else scan_root
        self.projects_root = pr_root
        try:
            self.detection = pr.detect_surface(root=tables_root)
        except Exception:  # noqa: BLE001
            self.detection = {"family_for_walls": "unknown-agent", "agent_possible": True}
        cache = pr._load_cache(None, home)
        self.cache_employer = [Path(c["path"]) for c in (cache or {}).get("checkouts") or []
                               if isinstance(c, dict) and isinstance(c.get("path"), str)
                               and c.get("owner_class") == "employer"]

    def repo_verdict(self, repo: Path) -> Tuple[bool, str]:
        """(ok_neighbour, owner_class). OK means positively personal or a third-party clone."""
        key = str(repo)
        if key not in self._repo_cls:
            try:
                res = _pr().repo_resolve(key, root=self.tables_root, home=self.home, detection=self.detection)
                cls = str(res.get("owner_class"))
                ok = bool(res.get("positively_personal")) or cls == "third-party"
            except Exception:  # noqa: BLE001
                ok, cls = False, "unknown"
            self._repo_cls[key] = (ok, cls)
        return self._repo_cls[key]


def not_personal_reason(cand: Path, ctx: Context, walker: Walker) -> Optional[str]:
    """None when the folder is positively personal; otherwise why not (fail-closed)."""
    pr = _pr()
    if ctx.fatal:
        return ctx.fatal
    real = pr._real(cand)
    for base in {str(ctx.scan_root), str(ctx.base), str(ctx.projects_root)}:
        g = pr._glob_hit(real, pr._real(base), ctx.globs)
        if g:
            return f"path matches employer glob {g!r}"
    if ctx.conduct:
        prof = pr._project_md_profile(cand, ctx.conduct)
        if prof and prof != ctx.conduct[0]:
            return f"PROJECT.md declares {prof}"
    base = pr._real(ctx.base)
    anc = real.parent
    while pr._is_under(anc, base) and pr._cf(anc) != pr._cf(base):
        for emp in ctx.cache_employer:
            if pr._is_under(pr._real(emp), anc):
                return f"{_rel(anc, ctx.scan_root)} also holds employer checkout {emp.name} (checkout cache)"
        for repo in walker.repos_below(anc):
            ok, cls = ctx.repo_verdict(repo)
            if not ok:
                return f"{_rel(anc, ctx.scan_root)} also holds repo {_rel(repo, ctx.scan_root)} ({cls} owner)"
        anc = anc.parent
    return None


# --------------------------------------------------------------------------- scans


def _rel(p: Path, base: Path) -> str:
    try:
        r = Path(os.path.realpath(p)).relative_to(os.path.realpath(base)).as_posix()
        return r or "."
    except ValueError:
        return str(p)


def repo_name(folder: str) -> str:
    n = re.sub(r"[^a-z0-9._-]+", "-", folder.lower())
    n = re.sub(r"-{2,}", "-", n).strip("-.")
    return n[:100]


def committed_files(d: Path, *, has_gitignore: bool, scratch: Path,
                    env: Optional[dict] = None) -> Optional[List[str]]:
    """Relative paths `git add -A` would stage once the default .gitignore (if any) is in place.

    `scratch` holds a throwaway bare git dir, made once per plan; the project folder is only read."""
    gd = scratch / "g"
    e = dict(os.environ if env is None else env)
    try:
        if not gd.exists():
            subprocess.run(["git", "init", "-q", "--bare", str(gd)], env=e, capture_output=True, check=True,
                           timeout=30)
        extra = []
        if not has_gitignore:
            ex = scratch / "exclude"
            ex.write_text(DEFAULT_GITIGNORE, encoding="utf-8")
            extra = [f"--exclude-from={ex}"]
        r = subprocess.run(["git", f"--git-dir={gd}", f"--work-tree={d}", "ls-files", "-o",
                            "--exclude-standard", *extra, "-z"], cwd=str(d), env=e, capture_output=True,
                           timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    return [p for p in r.stdout.decode("utf-8", "replace").split("\0") if p]


def _secret_name(name: str) -> bool:
    low = name.lower()
    if low.endswith(SECRET_NAME_ALLOW_SUFFIXES):
        return False
    return any(fnmatch.fnmatchcase(low, g) for g in SECRET_NAME_GLOBS)


def _walk_files(d: Path) -> List[str]:
    out = []
    for top, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x not in PRUNE_DIRS and x != ".git"]
        for f in files:
            out.append(os.path.relpath(os.path.join(top, f), d))
    return out


def _read_text(p: Path) -> Optional[str]:
    try:
        if p.is_symlink() or p.stat().st_size > SCAN_MAX_BYTES:
            return None
        data = p.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:8192]:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def blockers_for(d: Path, files: List[str], *, public: bool, emp_rules: Any, emp_err: Optional[str]) -> List[str]:
    out: List[str] = []
    names = sorted(set(files) | set(_walk_files(d)))
    for rel in names:
        base = os.path.basename(rel)
        if _secret_name(base):
            hint = " (a Keynote deck also ends in .key: move or rename it)" if base.lower().endswith(".key") else ""
            out.append(f"secret-shaped file {rel}{hint}")
        p = d / rel
        try:
            if not p.is_symlink() and p.is_file() and p.stat().st_size > MAX_FILE_BYTES:
                out.append(f"file over 50 MB: {rel} ({_human(p.stat().st_size)})")
        except OSError:
            out.append(f"unreadable: {rel}")
    cs = _cs()
    if public and emp_rules is None:
        out.append(f"public: employer-substance rules unavailable ({emp_err})")
    for rel in files:
        text = _read_text(d / rel)
        if text is None:
            continue
        for name, line in cs.findings_in_text(text):
            out.append(f"secret pattern {name} in {rel}:{line}")
        if public and emp_rules is not None:
            for line, rule in emp_rules.scan_text(text):
                out.append(f"public: employer substance ({rule}) in {rel}:{line}")
    return list(dict.fromkeys(out))


def _human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} GB"


# --------------------------------------------------------------------------- plan


def _select(tokens: List[str], entries: List[dict], flag: str) -> Tuple[set, List[str]]:
    chosen, errors = set(), []
    for tok in tokens:
        t = tok.strip().strip("/").lower()
        if not t:
            continue
        hits = [e for e in entries if t in (e["rel"].lower(), e["folder"].lower(), e["repo"].lower())]
        if not hits:
            errors.append(f"{flag}: no folder named {tok!r}")
        elif len(hits) > 1:
            errors.append(f"{flag}: {tok!r} is ambiguous ({', '.join(e['rel'] for e in hits)}); use the path")
        else:
            chosen.add(hits[0]["rel"])
    return chosen, errors


def plan(root: Path, *, public: List[str], tables_root: Optional[Path] = None, hostname: Optional[str] = None,
         home: Optional[Path] = None, env: Optional[dict] = None) -> dict:
    """Read-only. Every folder is a candidate, blocked (a candidate with blockers) or skipped."""
    root = Path(os.path.realpath(os.path.expanduser(str(root))))
    out: Dict[str, Any] = {"root": str(root), "device": None, "owner": None, "fatal": None, "errors": [],
                           "candidates": [], "skipped": [], "loose": [], "notes": []}
    if not root.is_dir():
        out["fatal"] = f"root {root} is not a directory"
        return out
    pr = _pr()
    if pr._find_top(root) is not None:
        out["fatal"] = f"root {root} is inside a git repository"
        return out
    walker = Walker(tables_root)
    ctx = Context(tables_root=tables_root, hostname=hostname, scan_root=root, home=home)
    out.update(device=ctx.device_id, owner=ctx.owner)
    if ctx.fatal:
        out["notes"].append(f"every folder is skipped: {ctx.fatal}")
    found = discover(root, walker)
    out["loose"] = [{"rel": _rel(d, root), "files": n} for d, n in found["loose"]]
    entries = []
    for cand in found["candidates"]:
        rel = _rel(cand, root)
        e = {"rel": rel, "path": str(cand), "folder": cand.name, "repo": repo_name(cand.name)}
        why = not_personal_reason(cand, ctx, walker)
        if why:
            out["skipped"].append({"rel": rel, "reason": f"not personal: {why}"})
            continue
        entries.append(e)
    pub, errs = _select(public, entries, "--public")
    out["errors"].extend(errs)
    emp_rules, emp_err = None, None
    if pub:
        try:
            emp_rules = _cs().load_emp_rules(pr, tables_root or ROOT)
        except Exception as exc:  # noqa: BLE001
            emp_err = str(exc)
    names: Dict[str, List[str]] = {}
    for e in entries:
        names.setdefault(e["repo"], []).append(e["rel"])
    with tempfile.TemporaryDirectory(prefix="backup-projects-") as scratch:
        for e in entries:
            _plan_entry(e, Path(scratch), public=e["rel"] in pub, emp_rules=emp_rules, emp_err=emp_err, env=env)
            if len(names.get(e["repo"], [])) > 1:
                others = [r for r in names[e["repo"]] if r != e["rel"]]
                e["blockers"].append(f"repo name {e['repo']} collides with {', '.join(others)}")
            out["candidates"].append(e)
    return out


def _plan_entry(e: dict, scratch: Path, *, public: bool, emp_rules: Any, emp_err: Optional[str],
                env: Optional[dict]) -> None:
    d = Path(e["path"])
    has_gi = (d / ".gitignore").is_file()
    files = committed_files(d, has_gitignore=has_gi, scratch=scratch, env=env)
    e.update(visibility="public" if public else "private", has_gitignore=has_gi,
             gitignore="existing" if has_gi else "default will be written")
    if files is None:
        e.update(files=0, size_bytes=0, blockers=["git could not list the folder's files"])
    else:
        size = 0
        for rel in files:
            try:
                size += (d / rel).lstat().st_size
            except OSError:
                pass
        e.update(files=len(files), size_bytes=size,
                 blockers=blockers_for(d, files, public=public, emp_rules=emp_rules, emp_err=emp_err))
    if not e["repo"]:
        e["blockers"].append("no usable repo name from the folder name")


def render(p: dict, *, applying: bool = False) -> str:
    lines = []
    head = "apply" if applying else "dry run (nothing written)"
    lines.append(f"backup-projects: {head} · root {p['root']} · device {p['device']} · owner {p['owner'] or '-'}")
    if p.get("fatal"):
        lines.append(f"REFUSED — {p['fatal']}")
        return "\n".join(lines)
    for n in p["notes"]:
        lines.append(f"NOTE: {n}")
    ready = [e for e in p["candidates"] if not e["blockers"]]
    blocked = [e for e in p["candidates"] if e["blockers"]]
    lines.append(f"\nReady to back up ({len(ready)}):")
    for e in ready or []:
        lines.append(f"  {e['rel']}  ->  {p['owner']}/{e['repo']} ({e['visibility']})")
        lines.append(f"      {_human(e['size_bytes'])} · {e['files']} files · .gitignore: {e['gitignore']}"
                     " · blockers: none")
    if not ready:
        lines.append("  (none)")
    lines.append(f"\nBlocked ({len(blocked)}):")
    for e in blocked:
        lines.append(f"  {e['rel']}  ->  {p['owner']}/{e['repo']} ({e['visibility']})")
        lines.append(f"      {_human(e['size_bytes'])} · {e['files']} files · .gitignore: {e['gitignore']}")
        for b in e["blockers"]:
            lines.append(f"      blocked: {b}")
    if not blocked:
        lines.append("  (none)")
    lines.append(f"\nSkipped ({len(p['skipped'])}):")
    for s in p["skipped"]:
        lines.append(f"  {s['rel']}: skipped ({s['reason']})")
    if not p["skipped"]:
        lines.append("  (none)")
    if p["loose"]:
        lines.append("\nLoose files in container folders (not backed up by this tool):")
        for x in p["loose"]:
            lines.append(f"  {x['rel']}: {x['files']} file(s)")
    if any(not e["has_gitignore"] for e in p["candidates"]):
        lines.append("\nDefault .gitignore (written only where a folder has none):")
        lines.extend("  " + ln for ln in DEFAULT_GITIGNORE.splitlines() if not ln.startswith("#"))
    for err in p["errors"]:
        lines.append(f"ERROR: {err}")
    if not applying:
        lines.append("\nNext: a human at a terminal runs  python3 09-tools/backup-projects.py --apply "
                     "[--only NAME,...] [--public NAME,...]")
    return "\n".join(lines)


# --------------------------------------------------------------------------- apply


def _run(argv: List[str], *, cwd: Optional[Path] = None, env: Optional[dict] = None) -> subprocess.CompletedProcess:
    return subprocess.run(argv, cwd=str(cwd) if cwd else None, env=dict(os.environ if env is None else env),
                          capture_output=True, text=True, timeout=600)


def _repo_exists(slug: str, env: Optional[dict]) -> Tuple[Optional[bool], str]:
    """(True, '') exists · (False, '') not found · (None, why) cannot tell (treated as a skip)."""
    try:
        r = _run(["gh", "repo", "view", slug, "--json", "name"], env=env)
    except (OSError, subprocess.SubprocessError) as exc:
        return None, f"gh unavailable ({exc.__class__.__name__})"
    if r.returncode == 0:
        return True, ""
    msg = (r.stderr or r.stdout or "").strip()
    if re.search(r"could not resolve to a repository|not found", msg, re.IGNORECASE):
        return False, ""
    return None, msg.splitlines()[0] if msg else f"gh exited {r.returncode}"


def human_verdict() -> Tuple[bool, List[str]]:
    if _HUMAN_OVERRIDE is not None:
        return _HUMAN_OVERRIDE, ([] if _HUMAN_OVERRIDE else ["test override: agent"])
    try:
        v = _pr().agent_check()
    except Exception as exc:  # noqa: BLE001
        return False, [f"undetermined: {exc.__class__.__name__}"]
    return bool(v.get("human")), list(v.get("reasons") or [])


def apply(p: dict, *, only: List[str], ask: Callable[[str], str] = input, env: Optional[dict] = None,
          tables_root: Optional[Path] = None, hostname: Optional[str] = None,
          out: Callable[[str], None] = print) -> int:
    human, reasons = human_verdict()
    if not human:
        out("REFUSED — --apply needs a human at a terminal (agents may run the dry run only): "
            + (", ".join(reasons) or "no human evidence"))
        return 4
    if p.get("fatal"):
        out(f"REFUSED — {p['fatal']}")
        return 4
    if p["errors"]:
        for err in p["errors"]:
            out(f"ERROR: {err}")
        return 2
    cands = p["candidates"]
    if only:
        chosen, errs = _select(only, cands, "--only")
        if errs:
            for err in errs:
                out(f"ERROR: {err}")
            return 2
        cands = [e for e in cands if e["rel"] in chosen]
    ident = Context(tables_root=tables_root, hostname=hostname, scan_root=Path(p["root"])).identity or {}
    if not ident.get("email") or not ident.get("name"):
        out("REFUSED — the personal identity has no name or email for the commit")
        return 4
    failed = 0
    for e in cands:
        slug = f"{p['owner']}/{e['repo']}"
        if e["blockers"]:
            out(f"skip {e['rel']}: blocked ({'; '.join(e['blockers'])})")
            continue
        d = Path(e["path"])
        if _is_repo(d):
            out(f"skip {e['rel']}: already a git repo")
            continue
        answer = ask(f"Create {slug} ({e['visibility'].upper()}) from {d} and push it? [y/N] ")
        if answer.strip().lower() not in ("y", "yes"):
            out(f"skip {e['rel']}: not confirmed")
            continue
        exists, why = _repo_exists(slug, env)
        if exists:
            out(f"skip {e['rel']}: {slug} already exists on GitHub (never overwritten, nothing pushed)")
            continue
        if exists is None:
            out(f"skip {e['rel']}: cannot tell whether {slug} exists ({why})")
            continue
        if not (d / ".gitignore").exists():
            (d / ".gitignore").write_text(DEFAULT_GITIGNORE, encoding="utf-8")
        steps = [
            ["git", "init", "-q", "-b", "main"],
            ["git", "add", "-A"],
            ["git", "-c", f"user.name={ident['name']}", "-c", f"user.email={ident['email']}", "commit", "-q",
             "-m", COMMIT_MESSAGE.format(folder=d.name)],
        ]
        ok = True
        for argv in steps:
            r = _run(argv, cwd=d, env=env)
            if r.returncode != 0:
                out(f"FAIL {e['rel']}: {' '.join(argv[:3])} … exited {r.returncode}: {(r.stderr or '').strip()[:300]}")
                ok = False
                break
        if not ok:
            failed += 1
            continue
        vis = "--public" if e["visibility"] == "public" else "--private"
        r = _run(["gh", "repo", "create", slug, vis, "--source", str(d), "--push"], env=env)
        if r.returncode != 0:
            failed += 1
            out(f"FAIL {e['rel']}: the local repo is committed but gh repo create failed: "
                f"{(r.stderr or '').strip()[:300]}\n     finish by hand: cd {d} && gh repo create {slug} {vis} "
                "--source . --push")
            continue
        out(f"done {e['rel']}: {slug} ({e['visibility']})")
    return 1 if failed else 0


# --------------------------------------------------------------------------- CLI


def _split(values: Optional[List[str]]) -> List[str]:
    out: List[str] = []
    for v in values or []:
        out.extend(x for x in v.split(",") if x.strip())
    return out


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="backup-projects.py", description=__doc__.split("\n", 1)[0])
    ap.add_argument("--root", help="folder to walk (default: this device's projects_root)")
    ap.add_argument("--public", action="append", metavar="NAME[,NAME...]", help="make only these repos public")
    ap.add_argument("--apply", action="store_true", help="create the repos (a human at a terminal only)")
    ap.add_argument("--only", action="append", metavar="NAME[,NAME...]", help="with --apply: only these folders")
    ap.add_argument("--json", action="store_true", help="print the dry-run plan as JSON")
    ap.add_argument("--tables-root", help=argparse.SUPPRESS)
    ap.add_argument("--hostname", help=argparse.SUPPRESS)
    ap.add_argument("--self-test", action="store_true")
    return ap


def main(argv: Optional[List[str]] = None, *, ask: Callable[[str], str] = input, env: Optional[dict] = None) -> int:
    args = _parser().parse_args(argv)
    if args.self_test:
        return self_test()
    if args.hostname and not args.tables_root:
        print("backup-projects: --hostname is for tests and needs --tables-root", file=sys.stderr)
        return 2
    if args.only and not args.apply:
        print("backup-projects: --only works with --apply", file=sys.stderr)
        return 2
    if args.apply:
        human, reasons = human_verdict()
        if not human:
            print("REFUSED — --apply needs a human at a terminal (agents may run the dry run only): "
                  + (", ".join(reasons) or "no human evidence"), file=sys.stderr)
            return 4
    tables_root = Path(args.tables_root) if args.tables_root else None
    root = Path(args.root) if args.root else _pr().projects_root(root=tables_root, hostname=args.hostname)
    p = plan(root, public=_split(args.public), tables_root=tables_root, hostname=args.hostname, env=env)
    if args.apply:
        print(render(p, applying=True))
        return apply(p, only=_split(args.only), ask=ask, env=env, tables_root=tables_root, hostname=args.hostname)
    if args.json:
        print(json.dumps(p, indent=2))
    else:
        print(render(p))
    if p.get("fatal"):
        return 4
    return 2 if p["errors"] else 0


# --------------------------------------------------------------------------- fixtures + self-test

FIXTURE_TABLES = TOOLS / "fixtures" / "identity"
FIXTURE_SURFACES = TOOLS / "fixtures" / "profile_resolve" / "surfaces.json"
PERSONAL_HOST = "host-b"   # fixture device dev-b: default identity pat (personal, account pat-sample)
EMPLOYER_HOST = "host-a"   # fixture device dev-a: default identity acme-id (employer)


def _w(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _fake_repo(top: Path, url: Optional[str]) -> Path:
    body = "[core]\n\trepositoryformatversion = 0\n"
    if url:
        body += f'[remote "origin"]\n\turl = {url}\n\tfetch = +refs/heads/*:refs/remotes/origin/*\n'
    _w(top / ".git" / "config", body)
    _w(top / "README.md", "repo\n")
    return top


def build_fixture(tmp: Path) -> Tuple[Path, Path]:
    """(tables_root, projects_root): synthetic tables (owners pat-sample personal, acme-corp employer)."""
    tables = tmp / "ws"
    pr = _pr()
    for name, src in (("devices", FIXTURE_TABLES / "devices.json"),
                      ("context-remotes", FIXTURE_TABLES / "context-remotes.json"),
                      ("surfaces", FIXTURE_SURFACES)):
        _w(tables / pr.TABLE_PATHS[name], src.read_text(encoding="utf-8"))
    _w(tables / "AGENTS.md", "# fixture workspace\n")
    root = tmp / "Projects"
    _w(root / "leaf-notes" / "notes.md", "# notes\n")
    _w(root / "leaf-notes" / "node_modules" / "pkg" / "fixture.txt", "AKIA" + "Q" * 16 + "\n")
    _w(root / "Design Ideas" / "board.txt", "ideas\n")
    _w(root / "Design Ideas" / ".gitignore", "*.tmp\n")
    _fake_repo(root / "mixed" / "tool-repo", "https://github.com/pat-sample/tool.git")
    _w(root / "mixed" / "sketches" / "a.txt", "sketch\n")
    _fake_repo(root / "inrepo", "https://github.com/pat-sample/inrepo.git")
    _w(root / "inrepo" / "sub" / "inner.txt", "inside a repo\n")
    _w(root / "acme-notes" / "n.md", "employer-named folder\n")
    _fake_repo(root / "clientwork" / "widget", "https://github.com/acme-corp/widget.git")
    _w(root / "clientwork" / "drafts" / "d.md", "next to an employer repo\n")
    _w(root / "with-env" / ".env", "TOKEN=x\n")
    _w(root / "with-env" / "app.py", "print(1)\n")
    big = root / "big-assets" / "movie.bin"
    big.parent.mkdir(parents=True, exist_ok=True)
    with open(big, "wb") as fh:
        fh.truncate(MAX_FILE_BYTES + 1024 * 1024)  # sparse
    _w(root / "keys-in-text" / "config.txt", "key = " + "AKIA" + "Z" * 16 + "\n")
    _w(root / "public-leak" / "doc.md", "see github.com/acme-corp/widget/blob/main/x.py\n")
    _w(root / "node_modules" / "x" / "index.js", "module.exports = 1\n")
    _w(root / ".hidden" / "h.txt", "hidden\n")
    (root / "empty-dir").mkdir()
    return tables, root


STUB_GH = """#!/bin/sh
echo "$*" >> "$STUB_GH_LOG"
if [ "$1 $2" = "repo view" ]; then
  for n in $STUB_GH_EXISTING; do
    if [ "$3" = "$n" ]; then echo '{"name":"x"}'; exit 0; fi
  done
  echo "GraphQL: Could not resolve to a Repository with the name '$3'." >&2
  exit 1
fi
exit 0
"""


def stub_env(tmp: Path, existing: str = "") -> Tuple[dict, Path]:
    bindir = tmp / "bin"
    bindir.mkdir(parents=True, exist_ok=True)
    gh = bindir / "gh"
    gh.write_text(STUB_GH, encoding="utf-8")
    gh.chmod(0o755)
    log = tmp / "gh.log"
    env = {"PATH": f"{bindir}{os.pathsep}{os.environ.get('PATH', '/usr/bin:/bin')}", "HOME": str(tmp / "home"),
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LANG": "C", "LC_ALL": "C",
           "GIT_TERMINAL_PROMPT": "0", "STUB_GH_LOG": str(log), "STUB_GH_EXISTING": existing}
    (tmp / "home").mkdir(exist_ok=True)
    return env, log


def self_test() -> int:
    global _HUMAN_OVERRIDE
    fails: List[str] = []

    def ok(cond: Any, label: str) -> None:
        print(("PASS " if cond else "FAIL ") + label)
        if not cond:
            fails.append(label)

    if shutil.which("git") is None:
        print("SKIP backup-projects self-test: git not on PATH")
        return 3
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        tables, root = build_fixture(tmp)
        env, log = stub_env(tmp, existing="pat-sample/design-ideas")
        before = sorted(str(x) for x in root.rglob("*"))
        p = plan(root, public=[], tables_root=tables, hostname=PERSONAL_HOST, env=env)
        cands = {e["rel"]: e for e in p["candidates"]}
        skipped = {s["rel"]: s["reason"] for s in p["skipped"]}
        ready = sorted(r for r, e in cands.items() if not e["blockers"])
        ok(ready == ["Design Ideas", "leaf-notes", "mixed/sketches", "public-leak"], f"ready list {ready}")
        ok(sorted(r for r, e in cands.items() if e["blockers"]) == ["big-assets", "keys-in-text", "with-env"],
           "blocked list")
        ok(sorted(skipped) == ["acme-notes", "clientwork/drafts"], f"skipped list {sorted(skipped)}")
        ok("employer glob" in skipped.get("acme-notes", ""), "acme-notes skipped by employer glob")
        ok("employer owner" in skipped.get("clientwork/drafts", ""), "drafts skipped beside an employer repo")
        ok(not any(r.startswith(("inrepo", "node_modules", ".hidden", "mixed/tool-repo", "empty-dir"))
                   for r in list(cands) + list(skipped)), "repos, folders in repos, hidden, node_modules excluded")
        ok(all(e["visibility"] == "private" for e in cands.values()), "private by default")
        ok(cands["Design Ideas"]["repo"] == "design-ideas", "repo name sanitised")
        ok(cands["leaf-notes"]["gitignore"] == "default will be written", "default .gitignore planned")
        ok(sorted(str(x) for x in root.rglob("*")) == before, "dry run wrote nothing")
        pp = plan(root, public=["public-leak", "leaf-notes"], tables_root=tables, hostname=PERSONAL_HOST, env=env)
        pc = {e["rel"]: e for e in pp["candidates"]}
        ok(any("employer substance" in b for b in pc["public-leak"]["blockers"]), "public: employer substance blocks")
        ok(pc["leaf-notes"]["visibility"] == "public" and not pc["leaf-notes"]["blockers"], "public by name only")
        pe = plan(root, public=[], tables_root=tables, hostname=EMPLOYER_HOST, env=env)
        ok(not pe["candidates"] and len(pe["skipped"]) == 9, "employer device: every folder skipped")
        _HUMAN_OVERRIDE = False
        try:
            rc = apply(p, only=[], ask=lambda _q: "y", env=env, tables_root=tables, hostname=PERSONAL_HOST,
                       out=lambda _s: None)
            ok(rc == 4 and not (root / "leaf-notes" / ".git").exists(), "apply refused under an agent verdict")
            _HUMAN_OVERRIDE = True
            pa = plan(root, public=["leaf-notes"], tables_root=tables, hostname=PERSONAL_HOST, env=env)
            lines: List[str] = []
            rc = apply(pa, only=["leaf-notes", "Design Ideas", "mixed/sketches"], ask=lambda _q: "y", env=env,
                       tables_root=tables, hostname=PERSONAL_HOST, out=lines.append)
            calls = log.read_text(encoding="utf-8").splitlines() if log.exists() else []
            ok(rc == 0, f"apply rc {rc}: {lines}")
            ok("repo create pat-sample/leaf-notes --public --source " + os.path.realpath(root / "leaf-notes") + " --push"
               in calls,
               "public create for the named folder")
            ok(any(c.startswith("repo create pat-sample/sketches --private") for c in calls), "private by default")
            ok(not any(c.startswith("repo create pat-sample/design-ideas") for c in calls)
               and not (root / "Design Ideas" / ".git").exists(), "existing GitHub repo skipped")
            ok((root / "leaf-notes" / ".gitignore").read_text(encoding="utf-8") == DEFAULT_GITIGNORE,
               "default .gitignore written")
            ok((root / "Design Ideas" / ".gitignore").read_text(encoding="utf-8") == "*.tmp\n",
               "existing .gitignore untouched")
            again = plan(root, public=[], tables_root=tables, hostname=PERSONAL_HOST, env=env)
            ok("leaf-notes" not in {e["rel"] for e in again["candidates"]}, "idempotent: a new repo is no candidate")
        finally:
            _HUMAN_OVERRIDE = None
    print("backup-projects self-test: " + ("OK" if not fails else f"{len(fails)} FAILED"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
