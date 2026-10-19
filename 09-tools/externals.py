#!/usr/bin/env python3
"""externals.py — install, update, run, verify and remove external tool repos for this workspace.

An *external* is someone else's repo or package (an MCP server, a CLI, a skill pack) that this
workspace uses but does not own. The one home of what is installed is the tracked manifest
`02-shared-references/externals.json`; spec: `02-shared-references/externals-spec.md`.

Where things live (AGENTS.md: repos and codebases never live inside the portable workspace):
  code      <projects_root>/_externals/<id>/        per device, never tracked (WS_EXTERNALS_HOME overrides)
  link      <workspace>/.externals/<id>  ->  the package root above (git-ignored, per device)
  wiring    .mcp.json, .cursor/mcp.json, .claude/skills/<n>, .agents/skills/<n>   tracked, written by
            add/update/remove only, so every machine and surface gets the same wiring from git

Kinds:
  npm   a published package pinned to an exact version + registry integrity (sha512)
  git   a repo pinned to an exact commit; `update` fetches and moves the checkout in place

  externals.py list [--json]
  externals.py add ID (--npm PKG[@VER] | --git URL [--ref REF]) [--bin NAME] [--run CMD...]
                     [--mcp "ARGS"] [--skill NAME=PATH ...] [--upstream URL] [--purpose TEXT] [--yes]
  externals.py install [ID|--all] [--yes]           fetch the pinned version on this device
  externals.py update ID [--to VER|REF] [--force] [--yes]
  externals.py rollback ID [--yes]                  back to the copy the last update replaced
  externals.py remove ID --reason TEXT [--force] [--yes]
  externals.py exec ID [-- ARGS...]                  run it (stdio passes through; MCP hosts use this)
  externals.py status [ID] [--json]                  this device: installed vs pinned
  externals.py check [--json]                        tracked wiring matches the manifest (CI; no network)
  externals.py verify ID [--json] [--quick]          live parity: identical inside and outside the workspace
  externals.py --self-test                           offline: a fake git upstream and a local npm tarball

Mutating commands print the plan and change nothing without --yes. Every command takes --json and
prints one object {"ok", "action", "id", "plan", "applied", "warnings", "error"} (the Synapse contract).

Exit codes: 0 ok · 1 failed (or verify found a difference) · 2 usage · 3 not installed / nothing to do ·
4 refused (local changes, integrity mismatch, unknown id).
"""
from __future__ import annotations

import argparse
import base64
import concurrent.futures as cf
import datetime as dt
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import threading
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MANIFEST_REL = "02-shared-references/externals.json"
ALLOWLIST_REL = "02-shared-references/skill-wrapper-allowlist.json"
LINK_DIR = ".externals"
STATE_FILE = ".ws-external.json"          # inside each install dir; per device, never tracked
MCP_HOSTS = {"claude-code": ".mcp.json", "cursor": ".cursor/mcp.json"}
SKILL_HOSTS = (".claude/skills", ".agents/skills")
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,40}$")
SPEC_VERSION = "1.0"


class Refused(Exception):
    """A precondition failed (exit 4)."""


class Usage(Exception):
    """Bad arguments (exit 2)."""


class NotInstalled(Exception):
    """Nothing on this device to act on (exit 3)."""


# --------------------------------------------------------------------------- paths

def ext_home() -> Path:
    env = os.environ.get("WS_EXTERNALS_HOME")
    if env:
        return Path(env).expanduser()
    try:
        sys.path.insert(0, str(HERE))
        import profile_resolve  # noqa: E402  (stdlib-only sibling)
        return profile_resolve.projects_root(root=ROOT) / "_externals"
    except Exception:  # noqa: BLE001 — a missing devices table still has a sane default
        return Path.home() / "Projects" / "_externals"
    finally:
        if sys.path and sys.path[0] == str(HERE):
            sys.path.pop(0)


class Ctx:
    """Everything a command touches, so the self-test can point it at a temporary tree."""

    def __init__(self, root: Path = ROOT, home: Optional[Path] = None,
                 npm_resolver: Optional[Callable[[str, str], Dict[str, str]]] = None):
        self.root = Path(root)
        self.home = Path(home) if home else ext_home()
        self.npm_resolver = npm_resolver or npm_resolve

    @property
    def manifest_path(self) -> Path:
        return self.root / MANIFEST_REL

    def install_dir(self, xid: str) -> Path:
        return self.home / xid

    def link(self, xid: str) -> Path:
        return self.root / LINK_DIR / xid

    def pkg_root(self, xid: str, entry: dict) -> Path:
        d = self.install_dir(xid)
        return d / "node_modules" / entry["package"] if entry["kind"] == "npm" else d


# --------------------------------------------------------------------------- manifest

def load_manifest(ctx: Ctx) -> dict:
    if not ctx.manifest_path.exists():
        return {"spec_version": SPEC_VERSION, "doc": MANIFEST_DOC, "externals": {}, "removed": []}
    return json.loads(ctx.manifest_path.read_text(encoding="utf-8"))


MANIFEST_DOC = ("Externals: other people's repos and packages this workspace uses. One entry per id; "
                "written by 09-tools/externals.py (add/update/remove), never by hand. "
                "Spec: 02-shared-references/externals-spec.md.")


def save_manifest(ctx: Ctx, m: dict) -> None:
    m["externals"] = dict(sorted(m.get("externals", {}).items()))
    atomic_write(ctx.manifest_path, json.dumps(m, indent=2, ensure_ascii=False) + "\n")


def get_entry(m: dict, xid: str) -> dict:
    e = m.get("externals", {}).get(xid)
    if e is None:
        raise Refused(f"unknown external '{xid}' (not in {MANIFEST_REL})")
    return e


def validate_entry(xid: str, e: dict) -> List[str]:
    errs = []
    if not ID_RE.match(xid):
        errs.append(f"{xid}: id must match {ID_RE.pattern}")
    kind = e.get("kind")
    if kind == "npm":
        for k in ("package", "version", "integrity"):
            if not e.get(k):
                errs.append(f"{xid}: npm entry needs '{k}'")
        if e.get("integrity") and not str(e["integrity"]).startswith("sha512-"):
            errs.append(f"{xid}: integrity must be a sha512 SRI string")
    elif kind == "git":
        for k in ("repo", "commit"):
            if not e.get(k):
                errs.append(f"{xid}: git entry needs '{k}'")
        if e.get("commit") and not re.fullmatch(r"[0-9a-f]{40}", e["commit"]):
            errs.append(f"{xid}: commit must be a full 40-character sha")
    else:
        errs.append(f"{xid}: kind must be npm or git")
    if kind == "git" and e.get("mcp") and not e.get("run"):
        errs.append(f"{xid}: a git entry with mcp needs 'run'")
    for s in e.get("skills", []):
        if not s.get("name") or not s.get("path") or ".." in Path(s["path"]).parts:
            errs.append(f"{xid}: skill needs a name and a path inside the package")
    mcp = e.get("mcp")
    if mcp is not None:
        if not isinstance(mcp.get("args", []), list):
            errs.append(f"{xid}: mcp.args must be a list")
        for h in mcp.get("hosts", []):
            if h not in MCP_HOSTS:
                errs.append(f"{xid}: unknown mcp host '{h}' (known: {', '.join(MCP_HOSTS)})")
    return errs


# --------------------------------------------------------------------------- small io

def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(tmp, path)


def run(cmd: List[str], cwd: Optional[Path] = None, env: Optional[dict] = None, timeout: float = 900,
        check: bool = True, input_text: Optional[str] = None) -> subprocess.CompletedProcess:
    exe = shutil.which(cmd[0]) or cmd[0]   # Windows: npm/npx are .cmd shims
    p = subprocess.run([exe] + cmd[1:], cwd=str(cwd) if cwd else None, env=env, timeout=timeout,
                       capture_output=True, text=True, input=input_text)
    if check and p.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} failed ({p.returncode}): {(p.stderr or p.stdout).strip()[-800:]}")
    return p


def rmtree(p: Path) -> None:
    if p.is_symlink() or p.is_file():
        p.unlink()
    elif p.exists():
        def _onerr(fn, path, _exc):  # read-only files (git objects on Windows)
            os.chmod(path, 0o700)
            fn(path)
        shutil.rmtree(p, onerror=_onerr)


def today() -> str:
    return dt.date.today().isoformat()


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sri_sha512(path: Path) -> str:
    h = hashlib.sha512()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return "sha512-" + base64.b64encode(h.digest()).decode()


# --------------------------------------------------------------------------- npm

def npm_resolve(package: str, spec: str) -> Dict[str, str]:
    """Registry lookup: exact version + integrity for PACKAGE@SPEC ('latest' when SPEC is empty)."""
    p = run(["npm", "view", f"{package}@{spec or 'latest'}", "version", "dist.integrity", "--json"], timeout=120)
    data = json.loads(p.stdout)
    if isinstance(data, list):         # a range matched several versions: take the newest
        data = data[-1]
    return {"version": data["version"], "integrity": data["dist.integrity"], "spec": f"{package}@{data['version']}"}


def npm_install(ctx: Ctx, xid: str, e: dict, dest: Path) -> dict:
    res = ctx.npm_resolver(e["package"], e["version"])
    if res["version"] != e["version"] or res["integrity"] != e["integrity"]:
        raise Refused(f"{xid}: registry says {e['package']}@{res['version']} {res['integrity'][:24]}…, "
                      f"manifest pins {e['version']} {e['integrity'][:24]}… — refusing (republished or tampered)")
    dest.mkdir(parents=True, exist_ok=True)
    cmd = ["npm", "install", "--prefix", str(dest), "--no-audit", "--no-fund", "--loglevel=error", res["spec"]]
    if e.get("ignore_scripts"):
        cmd.insert(2, "--ignore-scripts")
    run(cmd, timeout=1200)
    lock = json.loads((dest / "package-lock.json").read_text(encoding="utf-8"))
    node = lock.get("packages", {}).get(f"node_modules/{e['package']}", {})
    got = node.get("integrity")
    if got != e["integrity"]:
        raise Refused(f"{xid}: installed integrity {got} != pinned {e['integrity']}")
    pj = json.loads((dest / "node_modules" / e["package"] / "package.json").read_text(encoding="utf-8"))
    if pj.get("version") != e["version"]:
        raise Refused(f"{xid}: installed version {pj.get('version')} != pinned {e['version']}")
    return {"version": e["version"], "integrity": got}


# --------------------------------------------------------------------------- git

def git(args: List[str], cwd: Path, timeout: float = 600, check: bool = True) -> str:
    return run(["git"] + args, cwd=cwd, timeout=timeout, check=check).stdout.strip()


def git_resolve(repo_dir: Path, ref: str) -> str:
    for cand in (f"refs/tags/{ref}^{{commit}}", f"refs/remotes/origin/{ref}^{{commit}}", f"{ref}^{{commit}}"):
        p = run(["git", "rev-parse", "--verify", "--quiet", cand], cwd=repo_dir, check=False)
        if p.returncode == 0 and p.stdout.strip():
            return p.stdout.strip()
    raise Refused(f"ref '{ref}' not found in {repo_dir}")


def git_local_changes(repo_dir: Path) -> List[str]:
    """Edits, untracked files and commits that exist only here. Updating or removing would lose them."""
    out = []
    st = git(["status", "--porcelain"], repo_dir)
    if st:
        out.append(f"uncommitted changes:\n{st}")
    ahead = git(["log", "--oneline", "HEAD", "--not", "--remotes", "--tags"], repo_dir, check=False)
    if ahead:
        out.append(f"commits not on the upstream:\n{ahead}")
    stash = git(["stash", "list"], repo_dir, check=False)
    if stash:
        out.append(f"stashes:\n{stash}")
    return out


def git_build(e: dict, repo_dir: Path) -> None:
    for step in e.get("build", []):
        run([s.replace("{root}", str(repo_dir)) for s in step], cwd=repo_dir, timeout=3600)


def git_install(ctx: Ctx, xid: str, e: dict, dest: Path) -> dict:
    run(["git", "clone", "--quiet", "--no-checkout", e["repo"], str(dest)], timeout=1800)
    git(["checkout", "--quiet", "--detach", e["commit"]], dest)
    with open(dest / ".git" / "info" / "exclude", "a", encoding="utf-8") as f:
        f.write(f"\n{STATE_FILE}\n")  # our per-device state file is not a local change
    if git(["rev-parse", "HEAD"], dest) != e["commit"]:
        raise Refused(f"{xid}: checkout is not at the pinned commit")
    git_build(e, dest)
    return {"commit": e["commit"]}


# --------------------------------------------------------------------------- install state

def read_state(ctx: Ctx, xid: str) -> Optional[dict]:
    f = ctx.install_dir(xid) / STATE_FILE
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def pin_of(e: dict) -> str:
    return e["version"] if e["kind"] == "npm" else e["commit"]


def installed_pin(ctx: Ctx, xid: str, e: dict) -> Optional[str]:
    st = read_state(ctx, xid)
    if not st:
        return None
    return st.get("version") if e["kind"] == "npm" else st.get("commit")


def make_link(ctx: Ctx, xid: str, e: dict) -> None:
    link, target = ctx.link(xid), ctx.pkg_root(xid, e)
    link.parent.mkdir(parents=True, exist_ok=True)
    if link.is_symlink():
        if Path(os.readlink(link)) == target:
            return
        link.unlink()
    elif link.exists():
        raise Refused(f"{link} exists and is not our link; move it aside")
    try:
        os.symlink(str(target), str(link), target_is_directory=True)
    except OSError:
        if os.name == "nt":  # no symlink privilege: a junction needs none
            subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], check=True, capture_output=True)
        else:
            raise


def do_fetch(ctx: Ctx, xid: str, e: dict) -> dict:
    """Fetch the pinned version into a staging dir, verify it, then swap it in (old copy kept as .prev)."""
    final = ctx.install_dir(xid)
    ctx.home.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".staging-{xid}-", dir=str(ctx.home)))
    try:
        if e["kind"] == "npm":
            rmtree(staging)
            info = npm_install(ctx, xid, e, staging)
        else:
            rmtree(staging)
            info = git_install(ctx, xid, e, staging)
        info.update({"id": xid, "kind": e["kind"], "installed_at": now(), "spec_version": SPEC_VERSION})
        atomic_write(staging / STATE_FILE, json.dumps(info, indent=2) + "\n")
        prev = final.with_name(final.name + ".prev")
        if final.exists():
            rmtree(prev)
            os.replace(final, prev)
        os.replace(staging, final)
    except BaseException:
        rmtree(staging)
        raise
    make_link(ctx, xid, e)
    return info


# --------------------------------------------------------------------------- tracked wiring

def mcp_entry(xid: str, e: dict) -> dict:
    # Relative script path: MCP hosts start project servers in the workspace root.
    return {"command": "python3", "args": ["09-tools/externals.py", "exec", xid, "--"] + list(e["mcp"].get("args", []))}


def wiring(m: dict) -> Tuple[Dict[str, Dict[str, dict]], Dict[str, str], List[dict]]:
    """What the tracked files must hold: per-host MCP entries, skill links, allowlist rows."""
    mcp: Dict[str, Dict[str, dict]] = {h: {} for h in MCP_HOSTS}
    links: Dict[str, str] = {}
    allow: List[dict] = []
    for xid, e in m.get("externals", {}).items():
        if e.get("mcp"):
            for h in e["mcp"].get("hosts", ["claude-code"]):
                mcp[h][e["mcp"].get("name", xid)] = mcp_entry(xid, e)
        for s in e.get("skills", []):
            for host in SKILL_HOSTS:
                rel = f"{host}/{s['name']}"
                links[rel] = os.path.join("..", "..", LINK_DIR, xid, *Path(s["path"]).parts)
                allow.append({"path": rel, "reason": f"external: symlink to the '{xid}' external's own skill "
                              f"(02-shared-references/externals.json, 09-tools/externals.py); the upstream owns the body"})
    return mcp, links, allow


def owned_names(m: dict) -> Dict[str, set]:
    """Every MCP name and skill link any manifest entry (live or removed) has ever claimed."""
    names = {h: set() for h in MCP_HOSTS}
    skills = set()
    entries = list(m.get("externals", {}).items()) + [(r["id"], r["entry"]) for r in m.get("removed", [])]
    for xid, e in entries:
        if e.get("mcp"):
            for h in e["mcp"].get("hosts", ["claude-code"]):
                names[h].add(e["mcp"].get("name", xid))
        for s in e.get("skills", []):
            for host in SKILL_HOSTS:
                skills.add(f"{host}/{s['name']}")
    return {"mcp": names, "skills": skills}


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def write_allowlist(ctx: Ctx, rows: List[dict], owned: set) -> bool:
    """Keep every row we don't own, byte for byte in the file's one-row-per-line layout."""
    path = ctx.root / ALLOWLIST_REL
    data = read_json(path, {"doc": "", "entries": []})
    kept = [r for r in data.get("entries", []) if r["path"] not in owned]
    entries = kept + rows
    lines = ",\n".join("    " + json.dumps(r, ensure_ascii=False) for r in entries)
    text = "{\n  \"doc\": " + json.dumps(data.get("doc", ""), ensure_ascii=False) + ",\n  \"entries\": [\n" + lines + "\n  ]\n}\n"
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    atomic_write(path, text)
    return True


def apply_wiring(ctx: Ctx, m: dict) -> List[str]:
    """Make the tracked files match the manifest. Touches only names an external owns."""
    changed = []
    mcp, links, allow = wiring(m)
    owned = owned_names(m)
    for host, rel in MCP_HOSTS.items():
        path = ctx.root / rel
        data = read_json(path, None)
        if data is None and not mcp[host]:
            continue
        data = data or {}
        servers = data.setdefault("mcpServers", {})
        before = json.dumps(data, sort_keys=True)
        for name in owned["mcp"][host]:
            if name not in mcp[host]:
                servers.pop(name, None)
        servers.update(mcp[host])
        if json.dumps(data, sort_keys=True) != before or not path.exists():
            atomic_write(path, json.dumps(data, indent=2) + "\n")
            changed.append(rel)
    for rel in sorted(owned["skills"]):
        p = ctx.root / rel
        want = links.get(rel)
        have = os.readlink(p) if p.is_symlink() else None
        if want == have:
            continue
        if p.exists() and not p.is_symlink():
            raise Refused(f"{rel} exists and is not a symlink an external owns; move it aside")
        if p.is_symlink():
            p.unlink()
        if want:
            p.parent.mkdir(parents=True, exist_ok=True)
            os.symlink(want, str(p), target_is_directory=True)
        changed.append(rel)
    if write_allowlist(ctx, allow, owned["skills"]):
        changed.append(ALLOWLIST_REL)
    return changed


def check_wiring(ctx: Ctx, m: dict) -> List[str]:
    errs = []
    for xid, e in m.get("externals", {}).items():
        errs += validate_entry(xid, e)
    mcp, links, allow = wiring(m)
    owned = owned_names(m)
    for host, rel in MCP_HOSTS.items():
        servers = (read_json(ctx.root / rel, {}) or {}).get("mcpServers", {})
        for name, want in mcp[host].items():
            if servers.get(name) != want:
                errs.append(f"{rel}: mcpServers.{name} does not match the manifest (run externals.py install --all --yes)")
        for name in owned["mcp"][host] - set(mcp[host]):
            if name in servers:
                errs.append(f"{rel}: mcpServers.{name} belongs to a removed external")
    for rel in owned["skills"]:
        p = ctx.root / rel
        want = links.get(rel)
        have = os.readlink(p) if p.is_symlink() else None
        if want != have:
            errs.append(f"{rel}: expected {'symlink -> ' + want if want else 'absent'}, found {have or ('a file' if p.exists() else 'nothing')}")
    rows = {r["path"] for r in read_json(ctx.root / ALLOWLIST_REL, {"entries": []}).get("entries", [])}
    for r in allow:
        if r["path"] not in rows:
            errs.append(f"{ALLOWLIST_REL}: missing row for {r['path']}")
    for rel in owned["skills"] - set(links):
        if rel in rows:
            errs.append(f"{ALLOWLIST_REL}: stale row for removed {rel}")
    return errs


# --------------------------------------------------------------------------- commands

class Result(dict):
    def __init__(self, action: str, xid: Optional[str] = None):
        super().__init__(ok=True, action=action, id=xid, plan=[], applied=[], warnings=[], error=None)


def cmd_add(ctx: Ctx, a, r: Result) -> int:
    m = load_manifest(ctx)
    if a.id in m["externals"]:
        raise Refused(f"'{a.id}' is already in the manifest; use update")
    if a.npm:
        pkg, _, spec = a.npm.rpartition("@") if a.npm.count("@") > (1 if a.npm.startswith("@") else 0) else (a.npm, "", "")
        res = ctx.npm_resolver(pkg, spec)
        e = {"kind": "npm", "package": pkg, "version": res["version"], "integrity": res["integrity"]}
        if a.bin:
            e["bin"] = a.bin
    elif a.git:
        e = {"kind": "git", "repo": a.git, "ref": a.ref or "HEAD"}
        with tempfile.TemporaryDirectory() as td:
            run(["git", "clone", "--quiet", "--no-checkout", a.git, td], timeout=1800)
            e["commit"] = git_resolve(Path(td), a.ref or "HEAD")
        if a.run:
            e["run"] = shlex.split(a.run)
    else:
        raise Usage("add needs --npm or --git")
    if a.ignore_scripts:
        e["ignore_scripts"] = True
    if a.upstream:
        e["upstream"] = a.upstream
    if a.purpose:
        e["purpose"] = a.purpose
    if a.mcp is not None:
        e["mcp"] = {"name": a.mcp_name or a.id, "args": shlex.split(a.mcp), "hosts": a.mcp_host or ["claude-code", "cursor"]}
    if a.skill:
        e["skills"] = [{"name": s.split("=", 1)[0], "path": s.split("=", 1)[1]} for s in a.skill]
    e["added"] = today()
    errs = validate_entry(a.id, e)
    if errs:
        raise Usage("; ".join(errs))
    r["plan"] = [f"pin {a.id} at {pin_of(e)} in {MANIFEST_REL}", f"fetch into {ctx.install_dir(a.id)}",
                 f"link {LINK_DIR}/{a.id}"] + [f"wire {x}" for x in plan_wiring_targets(a.id, e)]
    r["entry"] = e
    if not a.yes:
        return 0
    do_fetch(ctx, a.id, e)
    r["applied"].append(f"installed {pin_of(e)}")
    m["externals"][a.id] = e
    save_manifest(ctx, m)
    r["applied"].append(MANIFEST_REL)
    r["applied"] += apply_wiring(ctx, m)
    return 0


def plan_wiring_targets(xid: str, e: dict) -> List[str]:
    out = []
    if e.get("mcp"):
        out += [MCP_HOSTS[h] + f" mcpServers.{e['mcp'].get('name', xid)}" for h in e["mcp"].get("hosts", [])]
    for s in e.get("skills", []):
        out += [f"{h}/{s['name']} -> {LINK_DIR}/{xid}/{s['path']}" for h in SKILL_HOSTS]
    return out


def cmd_install(ctx: Ctx, a, r: Result) -> int:
    m = load_manifest(ctx)
    ids = list(m["externals"]) if a.all or not a.id else [a.id]
    todo = []
    for xid in ids:
        e = get_entry(m, xid)
        if installed_pin(ctx, xid, e) == pin_of(e) and ctx.pkg_root(xid, e).exists():
            make_link(ctx, xid, e) if a.yes else None
            continue
        todo.append(xid)
        r["plan"].append(f"fetch {xid} {pin_of(e)} into {ctx.install_dir(xid)}")
    wiring_drift = check_wiring(ctx, m)
    if wiring_drift:
        r["plan"].append("repair tracked wiring: " + "; ".join(wiring_drift))
    if not a.yes:
        return 0 if (todo or wiring_drift) else 3
    for xid in todo:
        do_fetch(ctx, xid, m["externals"][xid])
        r["applied"].append(f"installed {xid}")
    r["applied"] += apply_wiring(ctx, m)
    return 0


def cmd_update(ctx: Ctx, a, r: Result) -> int:
    m = load_manifest(ctx)
    e = dict(get_entry(m, a.id))
    old = pin_of(e)
    if e["kind"] == "npm":
        res = ctx.npm_resolver(e["package"], a.to or "latest")
        new = dict(e, version=res["version"], integrity=res["integrity"])
    else:
        d = ctx.install_dir(a.id)
        if not (d / ".git").exists():
            raise NotInstalled(f"{a.id} is not installed on this device; run install first")
        changes = git_local_changes(d)
        if changes and not a.force:
            raise Refused(f"{a.id} has local work an update could lose (--force to override):\n" + "\n".join(changes))
        git(["fetch", "--quiet", "--tags", "--force", "origin"], d, timeout=1800)
        ref = a.to or e.get("ref") or "HEAD"
        if ref == "HEAD":
            ref = git(["rev-parse", "--abbrev-ref", "origin/HEAD"], d).split("/", 1)[-1]
        new = dict(e, ref=ref, commit=git_resolve(d, ref))
    r["from"], r["to"] = old, pin_of(new)
    if pin_of(new) == old and installed_pin(ctx, a.id, e) == old:
        r["plan"].append(f"{a.id} is already at {old}")
        return 3
    r["plan"].append(f"move {a.id} {old} -> {pin_of(new)}" + (" in place (git checkout)" if e["kind"] == "git" else " (staged, old copy kept for rollback)"))
    if not a.yes:
        return 0
    if e["kind"] == "git":
        d = ctx.install_dir(a.id)
        before = git(["rev-parse", "HEAD"], d)
        git(["checkout", "--quiet", "--detach", new["commit"]] + (["--force"] if a.force else []), d)
        try:
            git_build(new, d)
        except Exception:
            git(["checkout", "--quiet", "--detach", before], d)
            raise
        st = read_state(ctx, a.id) or {}
        st.update({"commit": new["commit"], "previous_commit": before, "installed_at": now()})
        atomic_write(d / STATE_FILE, json.dumps(st, indent=2) + "\n")
    else:
        do_fetch(ctx, a.id, new)
    new["updated"] = today()
    m["externals"][a.id] = new
    save_manifest(ctx, m)
    r["applied"] += [f"{a.id} at {pin_of(new)}", MANIFEST_REL] + apply_wiring(ctx, m)
    return 0


def cmd_rollback(ctx: Ctx, a, r: Result) -> int:
    m = load_manifest(ctx)
    e = get_entry(m, a.id)
    d = ctx.install_dir(a.id)
    st = read_state(ctx, a.id) or {}
    if e["kind"] == "git":
        prev = st.get("previous_commit")
        if not prev:
            raise NotInstalled(f"{a.id}: no previous commit recorded")
        r["plan"].append(f"checkout {prev} in place and pin it")
        if not a.yes:
            return 0
        git(["checkout", "--quiet", "--detach", prev], d)
        git_build(e, d)
        st.update({"commit": prev, "previous_commit": e["commit"], "installed_at": now()})
        atomic_write(d / STATE_FILE, json.dumps(st, indent=2) + "\n")
        new = dict(e, commit=prev)
    else:
        prevdir = d.with_name(d.name + ".prev")
        pst = read_state(ctx, a.id + ".prev") if prevdir.exists() else None
        if not pst:
            raise NotInstalled(f"{a.id}: no previous copy kept")
        r["plan"].append(f"swap back to {pst['version']} and pin it")
        if not a.yes:
            return 0
        tmp = d.with_name(d.name + ".swap")
        os.replace(d, tmp)
        os.replace(prevdir, d)
        os.replace(tmp, prevdir)
        new = dict(e, version=pst["version"], integrity=pst["integrity"])
    new["updated"] = today()
    m["externals"][a.id] = new
    save_manifest(ctx, m)
    make_link(ctx, a.id, new)
    r["applied"] += [f"{a.id} at {pin_of(new)}", MANIFEST_REL] + apply_wiring(ctx, m)
    return 0


def cmd_remove(ctx: Ctx, a, r: Result) -> int:
    if not a.reason:
        raise Usage("remove needs --reason (kept with the removed entry as provenance)")
    m = load_manifest(ctx)
    e = get_entry(m, a.id)
    d = ctx.install_dir(a.id)
    if e["kind"] == "git" and (d / ".git").exists():
        changes = git_local_changes(d)
        if changes and not a.force:
            raise Refused(f"{a.id} has local work removal would delete (--force to override):\n" + "\n".join(changes))
    r["plan"] = [f"unwire {x}" for x in plan_wiring_targets(a.id, e)] + [
        f"delete {d} (re-fetchable from {e.get('upstream') or e.get('repo') or e.get('package')})",
        f"unlink {LINK_DIR}/{a.id}", f"move the entry to 'removed' in {MANIFEST_REL} with the reason"]
    if not a.yes:
        return 0
    del m["externals"][a.id]
    m.setdefault("removed", []).append({"id": a.id, "removed": today(), "reason": a.reason, "entry": e})
    save_manifest(ctx, m)
    r["applied"] += [MANIFEST_REL] + apply_wiring(ctx, m)
    link = ctx.link(a.id)
    if link.is_symlink() or link.exists():
        rmtree(link)
    for p in (d, d.with_name(d.name + ".prev")):
        rmtree(p)
    r["applied"].append(f"deleted {d}")
    return 0


def exec_argv(ctx: Ctx, xid: str, e: dict, args: List[str]) -> Tuple[List[str], Optional[str]]:
    """The argv `exec` runs, and a stderr note when it falls back to the upstream launcher."""
    root = ctx.pkg_root(xid, e)
    ok = installed_pin(ctx, xid, e) == pin_of(e) and root.exists()
    if e["kind"] == "npm":
        if ok:
            pj = json.loads((root / "package.json").read_text(encoding="utf-8"))
            bins = pj.get("bin") if isinstance(pj.get("bin"), dict) else {pj["name"].split("/")[-1]: pj.get("bin")}
            name = e.get("bin") or next(iter(bins))
            node = shutil.which("node") or "node"
            # npx runs node_modules/.bin/<bin>; use the same path so argv[1] (and anything reporting it) matches
            shim = ctx.install_dir(xid) / "node_modules" / ".bin" / name
            script = shim if os.name != "nt" and shim.is_symlink() else root / bins[name]
            return [node, str(script)] + args, None
        npx = shutil.which("npx") or "npx"
        note = (f"externals: {xid} {e['version']} is not installed on this device "
                f"(run: python3 09-tools/externals.py install {xid} --yes); using npx")
        cmd = [npx, "-y", f"{e['package']}@{e['version']}"]
        if e.get("bin") and e["bin"] != e["package"].split("/")[-1]:
            cmd = [npx, "-y", "-p", f"{e['package']}@{e['version']}", e["bin"]]
        return cmd + args, note
    if not ok:
        raise NotInstalled(f"{xid} is not installed at {e['commit'][:12]} on this device "
                           f"(run: python3 09-tools/externals.py install {xid} --yes)")
    return [s.replace("{root}", str(root)) for s in e["run"]] + args, None


def cmd_exec(ctx: Ctx, xid: str, args: List[str]) -> int:
    m = load_manifest(ctx)
    e = get_entry(m, xid)
    argv, note = exec_argv(ctx, xid, e, args)
    if note:
        sys.stderr.write(note + "\n")     # never stdout: MCP speaks JSON-RPC there
    try:
        if os.name == "nt":
            return subprocess.call(argv)
        sys.stdout.flush()
        os.execvp(argv[0], argv)
    except FileNotFoundError:
        sys.stderr.write(f"externals exec: {argv[0]} not found on PATH\n")
        return 127
    return 0  # unreachable


def cmd_status(ctx: Ctx, a, r: Result) -> int:
    m = load_manifest(ctx)
    rows = []
    for xid, e in m["externals"].items():
        if a.id and xid != a.id:
            continue
        have = installed_pin(ctx, xid, e)
        link = ctx.link(xid)
        rows.append({"id": xid, "kind": e["kind"], "pinned": pin_of(e), "installed": have,
                     "state": "ok" if have == pin_of(e) else ("missing" if have is None else "drift"),
                     "path": str(ctx.install_dir(xid)), "link_ok": link.exists()})
    r["externals"] = rows
    return 0 if all(x["state"] == "ok" for x in rows) else 3


def cmd_check(ctx: Ctx, a, r: Result) -> int:
    m = load_manifest(ctx)
    errs = check_wiring(ctx, m)
    r["errors"] = errs
    r["ok"] = not errs
    return 1 if errs else 0


# --------------------------------------------------------------------------- verify (live parity)

ISO_TIME = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?")


def _normalize(text: str, subs: List[Tuple[str, str]]) -> str:
    """Install paths and wall-clock stamps differ between any two runs; nothing else may."""
    for a, b in sorted(subs, key=lambda x: -len(x[0])):
        if a:
            text = text.replace(a, b)
    return ISO_TIME.sub("<TIME>", text)


class McpClient:
    """Minimal newline-delimited JSON-RPC over stdio: enough to list what a server offers."""

    def __init__(self, argv: List[str], cwd: Path, env: dict):
        self.p = subprocess.Popen(argv, cwd=str(cwd), env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, bufsize=1)
        self.n = 0
        self.err: List[str] = []
        threading.Thread(target=lambda: self.err.extend(self.p.stderr), daemon=True).start()

    def call(self, method: str, params: Optional[dict] = None, timeout: float = 120) -> dict:
        self.n += 1
        msg = {"jsonrpc": "2.0", "id": self.n, "method": method, "params": params or {}}
        self.p.stdin.write(json.dumps(msg) + "\n")
        self.p.stdin.flush()
        box: List[dict] = []

        def _read():
            for line in self.p.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except ValueError:
                    box.append({"_nonjson_stdout": line})
                    return
                if obj.get("id") == self.n:
                    box.append(obj)
                    return
        t = threading.Thread(target=_read, daemon=True)
        t.start()
        t.join(timeout)
        if not box:
            raise RuntimeError(f"MCP {method}: no reply in {timeout}s; stderr: {''.join(self.err)[-600:]}")
        return box[0]

    def notify(self, method: str) -> None:
        self.p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": method}) + "\n")
        self.p.stdin.flush()

    def close(self) -> None:
        try:
            self.p.stdin.close()
            self.p.wait(10)
        except Exception:  # noqa: BLE001
            self.p.kill()


def mcp_snapshot(argv: List[str], cwd: Path, env: dict) -> dict:
    c = McpClient(argv, cwd, env)
    try:
        init = c.call("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                     "clientInfo": {"name": "ws-externals-verify", "version": "1"}})
        c.notify("notifications/initialized")
        snap: Dict[str, Any] = {"initialize": init.get("result", init.get("error"))}
        for method, key in (("tools/list", "tools"), ("prompts/list", "prompts"), ("resources/list", "resources"),
                            ("resources/templates/list", "resourceTemplates")):
            items, cursor = [], None
            while True:
                rep = c.call(method, {"cursor": cursor} if cursor else {})
                if "error" in rep:
                    snap[key] = {"error": rep["error"].get("code")}
                    break
                items += rep["result"].get(key, [])
                cursor = rep["result"].get("nextCursor")
                if not cursor:
                    snap[key] = sorted(items, key=lambda x: json.dumps(x, sort_keys=True))
                    break
        return snap
    finally:
        c.close()


def tree_digest(root: Path, skip: Tuple[str, ...] = ()) -> Dict[str, str]:
    out = {}
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root).as_posix()
        if p.is_file() and not any(rel == s or rel.startswith(s + "/") for s in skip):
            out[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def workspace_footprint(root: Path) -> List[str]:
    p = run(["git", "status", "--porcelain", "--ignored", "--untracked-files=all"], cwd=root, check=False)
    return sorted(l for l in p.stdout.splitlines()
                  if "/__pycache__/" not in l and ".claude/state/" not in l and "06-context/sessions/" not in l)


def cmd_verify(ctx: Ctx, a, r: Result) -> int:
    """Prove the workspace copy behaves exactly like the upstream one, run outside the workspace."""
    m = load_manifest(ctx)
    e = get_entry(m, a.id)
    if installed_pin(ctx, a.id, e) != pin_of(e):
        raise NotInstalled(f"{a.id} is not installed at its pin on this device; run install first")
    if e["kind"] != "npm":
        return verify_git(ctx, a, r, e)
    checks: List[dict] = []
    r["checks"] = checks

    def record(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"check": name, "ok": ok, "detail": detail})

    root = ctx.pkg_root(a.id, e)
    env = dict(os.environ)
    with tempfile.TemporaryDirectory(prefix="ws-ext-ref-") as td:
        td = Path(td)
        ref_cwd = td / "outside"
        ref_cwd.mkdir()
        # 1. the published bytes: registry integrity, then every file against the registry tarball
        res = ctx.npm_resolver(e["package"], e["version"])
        record("registry integrity matches the pin", res["integrity"] == e["integrity"], res["integrity"][:30])
        lock = json.loads((ctx.install_dir(a.id) / "package-lock.json").read_text(encoding="utf-8"))
        got = lock["packages"][f"node_modules/{e['package']}"].get("integrity")
        record("installed lockfile integrity matches the pin", got == e["integrity"], str(got)[:30])
        tgz = run(["npm", "pack", res["spec"], "--pack-destination", str(td), "--silent"], cwd=td).stdout.strip().splitlines()[-1]
        record("registry tarball hashes to the pin", sri_sha512(td / tgz) == e["integrity"])
        with tarfile.open(td / tgz) as tf:
            tf.extractall(td / "pkg", filter="data") if sys.version_info >= (3, 12) else tf.extractall(td / "pkg")  # noqa: S202
        want = tree_digest(td / "pkg" / "package")
        have = tree_digest(root, skip=("node_modules",))
        diff = sorted(set(want.items()) ^ set(have.items()))
        record(f"installed package files identical to the tarball ({len(want)} files)", not diff,
               "; ".join(f"{k}" for k, _ in diff[:10]))
        # 2. skills: each wired link resolves to the upstream's bytes
        for s in e.get("skills", []):
            src = td / "pkg" / "package" / s["path"]
            for host in SKILL_HOSTS:
                link = ctx.root / host / s["name"]
                ok = link.is_symlink() and link.exists() and tree_digest(link) == tree_digest(src)
                record(f"{host}/{s['name']} resolves to the upstream skill byte for byte", ok)
        # 3. a clean reference install outside the workspace (what `npx` resolves to)
        ref = td / "ref"
        npm_install(ctx, a.id, e, ref)
        ref_root = ref / "node_modules" / e["package"]
        pj = json.loads((ref_root / "package.json").read_text(encoding="utf-8"))
        bins = pj["bin"] if isinstance(pj["bin"], dict) else {pj["name"]: pj["bin"]}
        node = shutil.which("node") or "node"
        name = e.get("bin") or next(iter(bins))
        shim = ref / "node_modules" / ".bin" / name
        ref_argv = [node, str(shim if os.name != "nt" and shim.is_symlink() else ref_root / bins[name])]
        ws_argv = [sys.executable, str(ctx.root / "09-tools" / "externals.py"), "exec", a.id, "--"]
        subs = [(str(ref_root), "<PKG>"), (str(root), "<PKG>"), (str(ctx.install_dir(a.id) / "node_modules" / e["package"]), "<PKG>"),
                (str(ref / "node_modules"), "<NM>"), (str(ctx.install_dir(a.id) / "node_modules"), "<NM>"),
                (str(ref_cwd), "<CWD>"), (str(ctx.root), "<CWD>")]
        before = workspace_footprint(ctx.root)
        probes: List[List[str]] = [list(x) for x in e.get("verify", {}).get("cli", [["--version"], ["--help"]])]
        each = e.get("verify", {}).get("each_command")
        if each and not a.quick:
            p = run(ref_argv + each["list"], cwd=ref_cwd)
            for c in json.loads(p.stdout).get("commands", []):
                probes.append([c["name"]] + each.get("suffix", ["--help"]))
        fixtures = td / "fixtures"
        for name, body in e.get("verify", {}).get("fixture", {}).items():
            (fixtures / name).parent.mkdir(parents=True, exist_ok=True)
            (fixtures / name).write_text(body, encoding="utf-8")
        for f in e.get("verify", {}).get("functional", []):
            probes.append([x.replace("{fixture}", str(fixtures)) for x in f])

        def one(args: List[str]) -> Optional[str]:
            x = run(ref_argv + args, cwd=ref_cwd, env=env, check=False, timeout=300)
            y = run(ws_argv + args, cwd=ctx.root, env=env, check=False, timeout=300)
            nx = (x.returncode, _normalize(x.stdout, subs), _normalize(x.stderr, subs))
            ny = (y.returncode, _normalize(y.stdout, subs), _normalize(y.stderr, subs))
            if nx == ny:
                return None
            part = "exit code" if nx[0] != ny[0] else ("stdout" if nx[1] != ny[1] else "stderr")
            return f"{' '.join(args)}: {part} differs"

        with cf.ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 2)) as pool:
            diffs = [d for d in pool.map(one, probes) if d]
        record(f"CLI output identical inside vs outside the workspace ({len(probes)} probes: "
               f"every command's help, version, functional fixtures)", not diffs, "; ".join(diffs[:10]))
        # 4. the real upstream launcher, once: npx from a neutral folder vs our wiring
        if not a.quick:
            npx = shutil.which("npx") or "npx"
            x = run([npx, "-y", res["spec"], "--version"], cwd=ref_cwd, check=False, timeout=600)
            y = run(ws_argv + ["--version"], cwd=ctx.root, check=False)
            record("npx (upstream launcher) and the workspace launcher report the same version",
                   x.stdout.strip() == y.stdout.strip() and x.returncode == y.returncode == 0, x.stdout.strip())
        # 5. MCP: the server the host would start (from the tracked .mcp.json) vs the reference server
        if e.get("mcp"):
            entry = (read_json(ctx.root / ".mcp.json", {}).get("mcpServers", {})).get(e["mcp"].get("name", a.id))
            record(".mcp.json wires the server through externals.py exec", entry == mcp_entry(a.id, e))
            host_argv = [sys.executable if entry and entry["command"] == "python3" else entry["command"]] + entry["args"] if entry else ws_argv
            sx = mcp_snapshot(ref_argv + e["mcp"].get("args", []), ref_cwd, env)
            sy = mcp_snapshot(host_argv, ctx.root, env)
            same = _normalize(json.dumps(sx, sort_keys=True), subs) == _normalize(json.dumps(sy, sort_keys=True), subs)
            tools = sx.get("tools")
            record(f"MCP handshake and catalog identical ({len(tools) if isinstance(tools, list) else 0} tools, "
                   "prompts, resources)", same)
        # 6. running it from the workspace left no files behind in the workspace
        after = workspace_footprint(ctx.root)
        extra = sorted(set(after) - set(before))
        record("no files written into the workspace", not extra, "; ".join(extra[:10]))
    r["ok"] = all(c["ok"] for c in checks)
    return 0 if r["ok"] else 1


def verify_git(ctx: Ctx, a, r: Result, e: dict) -> int:
    """A git external: the checkout is the upstream commit with no local edits, and its probes pass."""
    d = ctx.install_dir(a.id)
    checks = [{"check": "checkout at the pinned commit", "ok": git(["rev-parse", "HEAD"], d) == e["commit"]},
              {"check": "no local changes", "ok": not git(["status", "--porcelain"], d)}]
    with tempfile.TemporaryDirectory() as td:
        for args in e.get("verify", {}).get("cli", []):
            x = run(exec_argv(ctx, a.id, e, list(args))[0], cwd=Path(td), check=False)
            y = run([sys.executable, str(ctx.root / "09-tools" / "externals.py"), "exec", a.id, "--"] + list(args),
                    cwd=ctx.root, check=False)
            checks.append({"check": f"{' '.join(args)} identical inside vs outside",
                           "ok": (x.returncode, x.stdout) == (y.returncode, y.stdout)})
    r["checks"] = checks
    r["ok"] = all(c["ok"] for c in checks)
    return 0 if r["ok"] else 1


# --------------------------------------------------------------------------- cli

def emit(r: Result, as_json: bool) -> None:
    if as_json:
        print(json.dumps(r, indent=2))
        return
    if r.get("error"):
        print(f"externals {r['action']}: {r['error']}", file=sys.stderr)
    for line in r["plan"]:
        print(f"  plan   {line}")
    for line in r["applied"]:
        print(f"  done   {line}")
    for line in r["warnings"]:
        print(f"  warn   {line}")
    for row in r.get("externals", []):
        print(f"  {row['id']:<16} {row['kind']:<4} pinned {row['pinned'][:12]:<12} installed {str(row['installed'])[:12]:<12} {row['state']}")
    for c in r.get("checks", []):
        print(f"  {'PASS' if c['ok'] else 'FAIL'}  {c['check']}" + (f" — {c['detail']}" if c.get("detail") and not c["ok"] else ""))
    for err in r.get("errors", []):
        print(f"  error  {err}")
    if r["plan"] and not r["applied"] and r["action"] in MUTATING and not r.get("error"):
        print("  (dry run — nothing changed; pass --yes to apply)")


MUTATING = {"add", "install", "update", "rollback", "remove"}


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="externals.py", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("list")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("add")
    p.add_argument("id")
    p.add_argument("--npm")
    p.add_argument("--git")
    p.add_argument("--ref")
    p.add_argument("--bin")
    p.add_argument("--run", help="git kind: the command to run, {root} = the checkout")
    p.add_argument("--mcp", help="register an MCP server with these args (quoted string)")
    p.add_argument("--mcp-name")
    p.add_argument("--mcp-host", action="append", choices=sorted(MCP_HOSTS))
    p.add_argument("--skill", action="append", help="NAME=PATH inside the package")
    p.add_argument("--upstream")
    p.add_argument("--purpose")
    p.add_argument("--ignore-scripts", action="store_true")
    for name in ("install", "update", "rollback", "remove", "status", "verify"):
        p = sub.add_parser(name)
        p.add_argument("id", nargs="?" if name in ("install", "status") else None)
        if name == "install":
            p.add_argument("--all", action="store_true")
        if name in ("update", "remove"):
            p.add_argument("--force", action="store_true")
        if name == "update":
            p.add_argument("--to")
        if name == "remove":
            p.add_argument("--reason")
        if name == "verify":
            p.add_argument("--quick", action="store_true", help="skip per-command help and the npx probe")
        p.add_argument("--json", action="store_true")
    p = sub.add_parser("check")
    p.add_argument("--json", action="store_true")
    for p in sub.choices.values():
        if p.prog.split()[-1] in MUTATING:
            p.add_argument("--yes", action="store_true")
            if "--json" not in p._option_string_actions:
                p.add_argument("--json", action="store_true")
    return ap


def main(argv: Optional[List[str]] = None, ctx: Optional[Ctx] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    ctx = ctx or Ctx()
    if argv[:1] == ["--self-test"]:
        return self_test()
    if argv[:1] == ["exec"]:
        if len(argv) < 2:
            print("usage: externals.py exec ID [-- ARGS...]", file=sys.stderr)
            return 2
        rest = argv[2:]
        if rest[:1] == ["--"]:
            rest = rest[1:]
        try:
            return cmd_exec(ctx, argv[1], rest)
        except (Refused, NotInstalled) as ex:
            print(f"externals exec: {ex}", file=sys.stderr)
            return 4 if isinstance(ex, Refused) else 3
    a = build_parser().parse_args(argv)
    if not a.cmd:
        print(__doc__)
        return 0
    r = Result(a.cmd, getattr(a, "id", None))
    handlers = {"add": cmd_add, "install": cmd_install, "update": cmd_update, "rollback": cmd_rollback,
                "remove": cmd_remove, "status": cmd_status, "list": cmd_status, "check": cmd_check, "verify": cmd_verify}
    if a.cmd == "list":
        a.id = None
    try:
        code = handlers[a.cmd](ctx, a, r)
    except Usage as ex:
        r.update(ok=False, error=str(ex))
        code = 2
    except Refused as ex:
        r.update(ok=False, error=str(ex))
        code = 4
    except NotInstalled as ex:
        r.update(ok=False, error=str(ex))
        code = 3
    except RuntimeError as ex:
        r.update(ok=False, error=str(ex))
        code = 1
    if a.cmd == "list":
        code = 0
    emit(r, getattr(a, "json", False))
    return code


# --------------------------------------------------------------------------- self-test

def self_test() -> int:
    """Offline end to end: a fake git upstream (install, in-place update, local-change refusal, rollback,
    remove with provenance) and a local npm tarball (install, integrity refusal, exec, wiring, remove)."""
    failures: List[str] = []

    def ok(cond: bool, what: str) -> None:
        print(f"  {'ok  ' if cond else 'FAIL'} {what}")
        if not cond:
            failures.append(what)

    with tempfile.TemporaryDirectory(prefix="ws-ext-selftest-") as td:
        td = Path(td)
        ws, home = td / "ws", td / "home"
        (ws / "02-shared-references").mkdir(parents=True)
        (ws / "09-tools").mkdir()
        shutil.copy2(__file__, ws / "09-tools" / "externals.py")
        (ws / "AGENTS.md").write_text("# test\n")
        allow = {"doc": "test allowlist", "entries": [{"path": ".claude/skills/keep-me", "reason": "unrelated row"}]}
        (ws / ALLOWLIST_REL).write_text(json.dumps(allow))
        (ws / ".mcp.json").write_text(json.dumps({"mcpServers": {"hand-made": {"command": "x"}}}))
        env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
        os.environ.update(env)
        # ---- git upstream with a skill and a runnable script
        up = td / "upstream"
        up.mkdir()
        git(["init", "--quiet", "-b", "main"], up)
        (up / "skills" / "demo").mkdir(parents=True)
        (up / "skills" / "demo" / "SKILL.md").write_text("---\nname: demo\ndescription: d\n---\nv1\n")
        (up / "tool.py").write_text("import sys; print('v1', *sys.argv[1:])\n")
        git(["add", "-A"], up)
        git(["commit", "--quiet", "-m", "v1"], up)
        git(["tag", "v1"], up)
        ctx = Ctx(root=ws, home=home)

        def call(*args: str) -> Tuple[int, dict]:
            buf: List[str] = []
            real = sys.stdout.write
            sys.stdout.write = lambda s: buf.append(s) or len(s)  # type: ignore[assignment]
            try:
                code = main(list(args) + ["--json"], ctx)
            finally:
                sys.stdout.write = real  # type: ignore[assignment]
            return code, json.loads("".join(buf) or "{}")

        code, r = call("add", "demo", "--git", str(up), "--ref", "main", "--run", "python3 {root}/tool.py",
                       "--mcp", "serve", "--skill", "demo=skills/demo")
        ok(code == 0 and not (home / "demo").exists(), "add without --yes is a dry run")
        code, r = call("add", "demo", "--git", str(up), "--ref", "main", "--run", "python3 {root}/tool.py",
                       "--mcp", "serve", "--skill", "demo=skills/demo", "--yes")
        ok(code == 0 and (home / "demo" / "tool.py").exists(), "add --yes clones the pinned commit")
        m = load_manifest(ctx)
        ok(re.fullmatch(r"[0-9a-f]{40}", m["externals"]["demo"]["commit"] or "") is not None, "manifest pins a full sha")
        mcp = json.loads((ws / ".mcp.json").read_text())["mcpServers"]
        ok("hand-made" in mcp and mcp["demo"]["args"][:3] == ["09-tools/externals.py", "exec", "demo"], ".mcp.json keeps hand-made entries and adds ours")
        ok((ws / ".cursor/mcp.json").exists(), "cursor host wired too")
        sk = ws / ".claude/skills/demo/SKILL.md"
        ok(sk.exists() and "v1" in sk.read_text(), "skill symlink resolves through .externals to the upstream file")
        rows = [x["path"] for x in json.loads((ws / ALLOWLIST_REL).read_text())["entries"]]
        ok(".claude/skills/keep-me" in rows and ".agents/skills/demo" in rows, "allowlist keeps foreign rows and adds ours")
        code, r = call("check")
        ok(code == 0, "check passes after add")
        p = run([sys.executable, str(ws / "09-tools/externals.py"), "exec", "demo", "--", "a", "b"], cwd=ws, check=False,
                env=dict(os.environ, WS_EXTERNALS_HOME=str(home)))
        ok(p.stdout.strip() == "v1 a b", "exec runs the pinned checkout with args")
        # in-place update to a new upstream commit
        (up / "tool.py").write_text("import sys; print('v2', *sys.argv[1:])\n")
        git(["commit", "--quiet", "-am", "v2"], up)
        code, r = call("update", "demo", "--yes")
        ok(code == 0 and run([sys.executable, str(ws / "09-tools/externals.py"), "exec", "demo"], cwd=ws, check=False,
                             env=dict(os.environ, WS_EXTERNALS_HOME=str(home))).stdout.strip() == "v2", "update moves the checkout in place")
        ok(load_manifest(ctx)["externals"]["demo"]["commit"] == git(["rev-parse", "HEAD"], up), "update re-pins the manifest")
        code, r = call("update", "demo", "--yes")
        ok(code == 3, "update with nothing new exits 3")
        (home / "demo" / "tool.py").write_text("local edit\n")
        (up / "x.txt").write_text("x")
        git(["add", "x.txt"], up)
        git(["commit", "--quiet", "-m", "v3"], up)
        code, r = call("update", "demo", "--yes")
        ok(code == 4 and "local work" in (r.get("error") or ""), "update refuses to clobber local edits")
        code, r = call("remove", "demo", "--reason", "t", "--yes")
        ok(code == 4 and (home / "demo").exists(), "remove refuses to delete local edits")
        git(["checkout", "--", "tool.py"], home / "demo")
        code, r = call("rollback", "demo", "--yes")
        ok(code == 0 and "v1" in run([sys.executable, str(ws / "09-tools/externals.py"), "exec", "demo"], cwd=ws, check=False,
                                     env=dict(os.environ, WS_EXTERNALS_HOME=str(home))).stdout, "rollback returns to the previous commit")
        # tamper: hand-edit the tracked wiring, check must catch it
        mcpj = json.loads((ws / ".mcp.json").read_text())
        mcpj["mcpServers"]["demo"]["args"] = ["evil"]
        (ws / ".mcp.json").write_text(json.dumps(mcpj))
        code, r = call("check")
        ok(code == 1 and any("mcpServers.demo" in x for x in r["errors"]), "check catches a hand-edited MCP entry")
        code, r = call("install", "--all", "--yes")
        code2, _ = call("check")
        ok(code == 0 and code2 == 0, "install --all repairs the wiring")
        code, r = call("remove", "demo", "--reason", "self-test", "--yes")
        m = load_manifest(ctx)
        mcp = json.loads((ws / ".mcp.json").read_text())["mcpServers"]
        ok(code == 0 and "demo" not in m["externals"] and m["removed"][-1]["reason"] == "self-test",
           "remove records provenance in 'removed'")
        ok("demo" not in mcp and "hand-made" in mcp and not (ws / ".claude/skills/demo").is_symlink()
           and not (home / "demo").exists() and not (ws / LINK_DIR / "demo").exists(), "remove unwires and deletes, keeps others")
        code, r = call("check")
        ok(code == 0, "check passes after remove")
        # ---- npm kind from a local tarball (no registry)
        if shutil.which("npm") and shutil.which("node"):
            src = td / "pkgsrc"
            (src / "skills" / "hello").mkdir(parents=True)
            (src / "package.json").write_text(json.dumps({"name": "ws-ext-hello", "version": "1.0.0",
                                                          "bin": {"hello": "bin.js"}}))
            (src / "bin.js").write_text("#!/usr/bin/env node\nconsole.log('hello', process.argv.slice(2).join(' '))\n")
            (src / "skills" / "hello" / "SKILL.md").write_text("---\nname: hello\ndescription: h\n---\n")
            tgz = src / run(["npm", "pack", "--silent"], cwd=src).stdout.strip().splitlines()[-1]
            integ = sri_sha512(tgz)
            ctx.npm_resolver = lambda pkg, spec: {"version": "1.0.0", "integrity": integ, "spec": str(tgz)}
            code, r = call("add", "hello", "--npm", "ws-ext-hello@1.0.0", "--bin", "hello", "--mcp", "",
                           "--skill", "hello=skills/hello", "--yes")
            ok(code == 0 and (home / "hello" / "node_modules" / "ws-ext-hello" / "bin.js").exists(), "npm add installs the pinned tarball")
            p = run([sys.executable, str(ws / "09-tools/externals.py"), "exec", "hello", "--", "x"], cwd=ws, check=False,
                    env=dict(os.environ, WS_EXTERNALS_HOME=str(home)))
            ok(p.stdout.strip() == "hello x", "npm exec runs the package's bin")
            ok((ws / ".agents/skills/hello/SKILL.md").exists(), "npm skill wired for .agents too")
            ctx.npm_resolver = lambda pkg, spec: {"version": "1.0.0", "integrity": "sha512-AAAA", "spec": str(tgz)}
            rmtree(home / "hello")
            code, r = call("install", "hello", "--yes")
            ok(code == 4 and "refusing" in (r.get("error") or ""), "npm install refuses an integrity mismatch")
            p = run([sys.executable, str(ws / "09-tools/externals.py"), "exec", "hello"], cwd=ws, check=False,
                    env=dict(os.environ, WS_EXTERNALS_HOME=str(home), PATH=str(td / "nopath")))
            ok("not installed" in p.stderr and p.stdout == "", "exec falls back with a stderr note, never stdout")
            ctx.npm_resolver = lambda pkg, spec: {"version": "1.0.0", "integrity": integ, "spec": str(tgz)}
            code, r = call("remove", "hello", "--reason", "self-test", "--yes")
            ok(code == 0 and not (ws / ".claude/skills/hello").is_symlink(), "npm remove unwires")
        else:
            print("  SKIP npm half: npm/node not on PATH — not a pass")
        code, r = call("check")
        ok(code == 0, "final check clean")
    print(f"externals self-test: {'PASS' if not failures else 'FAIL (' + str(len(failures)) + ')'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
