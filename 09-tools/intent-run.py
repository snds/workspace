#!/usr/bin/env python3
"""Living-spec runner — portable kernel of Intent (intentapp.dev) coordination.

Enforces approval, dependency waves, git worktree isolation, and checklist
measures. Does not spawn models. The Intent desktop app is optional (doctor /
open-app / install-app). Stdlib-only.

Usage:
  python3 09-tools/intent-run.py doctor
  python3 09-tools/intent-run.py daemon [status|workspace.list]
  python3 09-tools/intent-run.py init [--path PATH]
  python3 09-tools/intent-run.py status [--spec PATH]
  python3 09-tools/intent-run.py gate [--spec PATH]
  python3 09-tools/intent-run.py ready [--spec PATH]
  python3 09-tools/intent-run.py worktree add TASK_ID [--spec PATH] [--repo DIR]
  python3 09-tools/intent-run.py verify [--spec PATH] [--run]
  python3 09-tools/intent-run.py open-app
  python3 09-tools/intent-run.py install-app [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "00-bootstrap" / "templates" / "intent-spec.md"
RELEASES_API = (
    "https://api.github.com/repos/intent-hq/cloudlands-releases/releases/latest"
)
APP_CANDIDATES = (
    Path("/Applications/Intent.app"),
    Path.home() / "Applications" / "Intent.app",
)

MEASURE_RE = re.compile(
    r"(?:measure|cmd)\s*:\s*(.+)$", re.IGNORECASE
)
BOX_RE = re.compile(r"^[-*]\s+\[([ xX])\]\s+(.*)$")


def _split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---"):
        return {}, text
    rest = text[3:]
    end = rest.find("\n---")
    if end < 0:
        return {}, text
    raw = rest[:end]
    body = rest[end + 4 :].lstrip("\n")
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        val = val.split("#", 1)[0].strip().strip("'\"")
        meta[key.strip().lower()] = val
    return meta, body


def _parse_table(section: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    header: list[str] | None = None
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            if header and rows:
                break
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(set(c) <= set("-: ") and c for c in cells):
            continue
        if header is None:
            header = [re.sub(r"[^a-z0-9]+", "_", c.lower()).strip("_") for c in cells]
            continue
        rec = {header[i]: cells[i] if i < len(cells) else "" for i in range(len(header))}
        rows.append(rec)
    return rows


def _section(body: str, heading: str) -> str:
    pat = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.IGNORECASE | re.M)
    m = pat.search(body)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"^##\s+\S", body[start:], re.M)
    return body[start : start + nxt.start()] if nxt else body[start:]


def parse_spec(text: str) -> dict:
    meta, body = _split_frontmatter(text)
    tasks = _parse_table(_section(body, "Task graph"))
    checks: list[dict[str, str | bool]] = []
    for line in _section(body, "Fidelity / acceptance checklist").splitlines():
        bm = BOX_RE.match(line.strip())
        if not bm:
            continue
        done = bm.group(1).lower() == "x"
        rest = bm.group(2).strip()
        mm = MEASURE_RE.search(rest)
        measure = mm.group(1).strip() if mm else ""
        label = rest[: mm.start()].strip(" -–—") if mm else rest
        checks.append({"label": label, "measure": measure, "done": done})
    return {"meta": meta, "body": body, "tasks": tasks, "checks": checks}


def load_spec(path: Path) -> dict:
    return parse_spec(path.read_text(encoding="utf-8"))


def approval_ok(meta: dict[str, str]) -> bool:
    a = (meta.get("approval") or "").strip().lower()
    return a.startswith("approved") or a.startswith("waived")


def _dep_ids(raw: str) -> list[str]:
    raw = (raw or "").strip()
    if not raw or raw in ("—", "-", "n/a", "na"):
        return []
    return [p.strip() for p in re.split(r"[,;/]", raw) if p.strip() and p.strip() not in ("—", "-")]


def task_status(task: dict[str, str], meta: dict[str, str], by_id: dict[str, dict]) -> str:
    explicit = (task.get("status") or "").strip().lower()
    if explicit in ("verified", "running", "held", "blocked"):
        return explicit
    role = (task.get("role") or "").strip().lower()
    tid = (task.get("id") or "").strip()
    if role == "coordinator" or tid.upper() == "T0":
        return "verified" if approval_ok(meta) else "held"
    deps = _dep_ids(task.get("depends_on") or "")
    for d in deps:
        dt = by_id.get(d) or by_id.get(d.upper()) or by_id.get(d.lower())
        if dt is None:
            return "held"
        if task_status(dt, meta, by_id) != "verified":
            return "held"
    if role == "implementor" and not approval_ok(meta):
        return "held"
    return explicit or "ready"


def index_tasks(tasks: list[dict[str, str]]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for t in tasks:
        tid = (t.get("id") or "").strip()
        if tid:
            out[tid] = t
            out[tid.upper()] = t
    return out


def ready_implementors(spec: dict) -> list[dict[str, str]]:
    by_id = index_tasks(spec["tasks"])
    ready = []
    for t in spec["tasks"]:
        role = (t.get("role") or "").lower()
        if role != "implementor":
            continue
        if task_status(t, spec["meta"], by_id) == "ready":
            ready.append(t)
    return ready


def state_path(spec_path: Path) -> Path:
    return spec_path.with_name(spec_path.stem + ".state.json")


def load_state(spec_path: Path) -> dict:
    p = state_path(spec_path)
    if not p.exists():
        return {"worktrees": {}}
    return json.loads(p.read_text(encoding="utf-8"))


def save_state(spec_path: Path, state: dict) -> None:
    state_path(spec_path).write_text(
        json.dumps(state, indent=2) + "\n", encoding="utf-8"
    )


def find_spec(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if not p.is_file():
            raise SystemExit(f"spec not found: {p}")
        return p
    cwd = Path.cwd()
    for cand in (
        cwd / "docs" / "INTENT.md",
        cwd / "INTENT.md",
        ROOT / "07-projects" / "19-workspace-brain" / "docs" / "INTENT.md",
    ):
        if cand.is_file():
            return cand
    raise SystemExit("no INTENT.md found — pass --spec or run init")


def find_app() -> Path | None:
    for p in APP_CANDIDATES:
        if p.exists():
            return p
    return None


def git_root(start: Path) -> Path:
    r = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=start,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        raise SystemExit("not a git repo — worktrees need git")
    return Path(r.stdout.strip())


def find_intentd() -> Path | None:
    which = shutil.which("intentd")
    if which:
        return Path(which)
    app = find_app()
    if app:
        bundled = app / "Contents" / "Resources" / "intentd" / "intentd"
        if bundled.is_file():
            return bundled
    return None


def intentd_status_text(intentd: Path) -> str:
    r = subprocess.run(
        [str(intentd), "status"],
        capture_output=True,
        text=True,
        timeout=8,
    )
    out = (r.stdout or r.stderr or "").strip()
    return out or f"exit {r.returncode}"


def cmd_doctor() -> int:
    app = find_app()
    intentd = find_intentd()
    print(f"Intent.app: {app or 'absent'}")
    print(f"intentd bin: {intentd or 'absent'}")
    print(f"intent-run: {Path(__file__).resolve()}")
    print(f"template: {'ok' if TEMPLATE.is_file() else 'MISSING'} ({TEMPLATE})")
    print(f"python: {sys.version.split()[0]} · {platform.system()} {platform.machine()}")
    r = subprocess.run(["git", "--version"], capture_output=True, text=True)
    print(f"git: {r.stdout.strip() if r.returncode == 0 else 'MISSING'}")
    for bin_name in ("auggie", "claude"):
        print(f"{bin_name}: {shutil.which(bin_name) or 'absent'}")
    if intentd:
        print("--- intentd status ---")
        print(intentd_status_text(intentd))
    if app is None:
        print(
            "GUI optional. Install: python3 09-tools/intent-run.py install-app"
        )
        print("Or download: https://github.com/intent-hq/cloudlands-releases/releases/latest")
    return 0


def cmd_daemon(method: str, params: str | None) -> int:
    intentd = find_intentd()
    if intentd is None:
        print("intentd not found (is Intent.app running?)", file=sys.stderr)
        return 1
    if method == "status":
        print(intentd_status_text(intentd))
        return 0
    cmd = [str(intentd), "call", method]
    if params:
        cmd.extend(["--params", params])
    r = subprocess.run(cmd)
    return r.returncode


def cmd_init(path: str | None) -> int:
    dest = Path(path).expanduser() if path else Path.cwd() / "docs" / "INTENT.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"exists: {dest}")
        return 0
    dest.write_text(TEMPLATE.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"wrote {dest}")
    print("Fill outcome + checklist measurements, set approval, then: intent-run.py gate")
    return 0


def cmd_status(spec_path: Path) -> int:
    spec = load_spec(spec_path)
    meta = spec["meta"]
    print(f"spec: {spec_path}")
    print(f"profile: {meta.get('profile') or '(unset)'}")
    print(f"approval: {meta.get('approval') or '(unset)'} → {'ok' if approval_ok(meta) else 'BLOCKED'}")
    print(f"northstar: {meta.get('northstar') or '(unset)'}")
    by_id = index_tasks(spec["tasks"])
    print("tasks:")
    for t in spec["tasks"]:
        st = task_status(t, meta, by_id)
        print(
            f"  {t.get('id','?'):4} {st:9} {(t.get('role') or ''):12} "
            f"deps={t.get('depends_on') or '—'} isol={t.get('isolation') or ''}"
        )
    print("checklist:")
    for c in spec["checks"]:
        mark = "x" if c["done"] else " "
        meas = c["measure"] or "(no measure — not runnable)"
        print(f"  [{mark}] {c['label'][:60]} | {meas}")
    state = load_state(spec_path)
    if state.get("worktrees"):
        print("worktrees:")
        for tid, info in state["worktrees"].items():
            print(f"  {tid}: {info.get('path')} ({info.get('branch')})")
    return 0 if approval_ok(meta) else 1


def cmd_gate(spec_path: Path) -> int:
    spec = load_spec(spec_path)
    if not spec["meta"].get("profile"):
        print("BLOCKED — spec has no context profile", file=sys.stderr)
        return 1
    if not approval_ok(spec["meta"]):
        print(
            "BLOCKED — spec approval is pending. Do not start implementors.",
            file=sys.stderr,
        )
        return 1
    missing = [c["label"] for c in spec["checks"] if not c["measure"]]
    if missing:
        print(
            "WARN — checklist items with no measure (verifier cannot run them):",
            file=sys.stderr,
        )
        for lab in missing:
            print(f"  • {lab}", file=sys.stderr)
    print("ok — spec approved; implementor waves may start")
    return 0


def cmd_ready(spec_path: Path) -> int:
    spec = load_spec(spec_path)
    if cmd_gate(spec_path) != 0:
        return 1
    ready = ready_implementors(spec)
    if not ready:
        print("no implementor tasks ready (held on deps or none defined)")
        return 0
    print("ready implementors:")
    for t in ready:
        skill = t.get("skill_specialist") or t.get("skill") or ""
        print(f"  {t.get('id')} skill={skill} isol={t.get('isolation') or 'worktree'}")
    return 0


def cmd_worktree_add(spec_path: Path, task_id: str, repo: str | None) -> int:
    spec = load_spec(spec_path)
    if cmd_gate(spec_path) != 0:
        return 1
    by_id = index_tasks(spec["tasks"])
    task = by_id.get(task_id) or by_id.get(task_id.upper())
    if task is None:
        print(f"unknown task {task_id}", file=sys.stderr)
        return 1
    if task_status(task, spec["meta"], by_id) != "ready":
        print(f"task {task_id} is not ready (deps or role)", file=sys.stderr)
        return 1
    isol = (task.get("isolation") or "worktree").lower()
    if isol not in ("worktree", "git worktree"):
        print(f"task {task_id} isolation={isol} — skip worktree")
        return 0
    repo_root = git_root(Path(repo).resolve() if repo else spec_path.parent)
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", task_id)
    branch = f"intent/{slug}"
    dest = repo_root.parent / f"{repo_root.name}.intent-{slug}"
    state = load_state(spec_path)
    existing = state.get("worktrees", {}).get(task_id)
    if existing and Path(existing["path"]).exists():
        print(f"already: {existing['path']}")
        return 0
    if dest.exists():
        print(f"path exists: {dest}", file=sys.stderr)
        return 1
    subprocess.run(
        ["git", "worktree", "add", "-b", branch, str(dest)],
        cwd=repo_root,
        check=True,
    )
    state.setdefault("worktrees", {})[task_id] = {
        "path": str(dest),
        "branch": branch,
        "repo": str(repo_root),
    }
    save_state(spec_path, state)
    print(f"worktree {dest} branch {branch}")
    print("Implementor cwd is that path. Do not write in the parent dirty tree.")
    return 0


def cmd_verify(spec_path: Path, run: bool) -> int:
    spec = load_spec(spec_path)
    if not spec["checks"]:
        print("no checklist items", file=sys.stderr)
        return 1
    failed = 0
    for c in spec["checks"]:
        if not c["measure"]:
            print(f"SKIP (no measure): {c['label']}")
            failed += 1
            continue
        print(f"{'RUN' if run else 'CMD'} {c['measure']}")
        if not run:
            continue
        rc = subprocess.run(c["measure"], shell=True)
        if rc.returncode != 0:
            print(f"FAIL exit {rc.returncode}: {c['label']}", file=sys.stderr)
            failed += 1
        else:
            print(f"PASS {c['label']}")
    if not run:
        print("dry — pass --run to execute measures")
        return 0
    return 1 if failed else 0


def cmd_open_app() -> int:
    app = find_app()
    if app is None:
        print("Intent.app not installed. Run: python3 09-tools/intent-run.py install-app")
        return 1
    subprocess.run(["open", str(app)], check=False)
    print(f"opened {app}")
    return 0


def _pick_asset(assets: list[dict], system: str, machine: str) -> dict | None:
    names = [a.get("name") or "" for a in assets]
    def find(pred):
        for a in assets:
            if pred(a.get("name") or ""):
                return a
        return None

    sys_l = system.lower()
    mac = machine.lower() in ("arm64", "aarch64")
    if sys_l == "darwin":
        if mac:
            return find(lambda n: n.endswith("arm64-mac.zip") or n.endswith("arm64.dmg"))
        return find(lambda n: "mac.zip" in n or n.endswith(".dmg"))
    if sys_l == "linux":
        if mac:
            return find(lambda n: n.endswith("arm64.AppImage") or n.endswith("arm64.deb"))
        return find(lambda n: n.endswith(".AppImage") or n.endswith("amd64.deb"))
    if sys_l == "windows":
        return find(lambda n: n.endswith("Setup") is False and n.endswith(".exe") and "Setup" not in n) or find(
            lambda n: "Setup" in n and n.endswith(".exe")
        )
    _ = names
    return assets[0] if assets else None


def cmd_install_app(dry: bool) -> int:
    existing = find_app()
    if existing:
        print(f"already installed: {existing}")
        return 0
    req = urllib.request.Request(
        RELEASES_API,
        headers={"User-Agent": "snds-workspace-intent-run", "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    assets = data.get("assets") or []
    asset = _pick_asset(assets, platform.system(), platform.machine())
    if not asset:
        print("no matching release asset", file=sys.stderr)
        return 1
    url = asset["browser_download_url"]
    name = asset["name"]
    print(f"latest {data.get('tag_name')} → {name}")
    print(url)
    if dry:
        return 0
    if platform.system() != "Darwin":
        print("Non-mac: download the asset yourself (script installs .app on macOS only).")
        return 0
    dest_dir = Path.home() / "Downloads"
    dest_dir.mkdir(parents=True, exist_ok=True)
    archive = dest_dir / name
    print(f"downloading to {archive} …")
    urllib.request.urlretrieve(url, archive)
    if name.endswith(".zip"):
        with tempfile.TemporaryDirectory() as td:
            with zipfile.ZipFile(archive) as zf:
                zf.extractall(td)
            apps = list(Path(td).rglob("Intent.app"))
            if not apps:
                print("zip had no Intent.app", file=sys.stderr)
                return 1
            target = Path("/Applications/Intent.app")
            if target.exists():
                print(f"exists: {target}")
                return 0
            shutil.copytree(apps[0], target)
            print(f"installed {target}")
            subprocess.run(["open", str(target)], check=False)
            return 0
    if name.endswith(".dmg"):
        print(f"downloaded {archive} — open the dmg and drag Intent.app to Applications")
        subprocess.run(["open", str(archive)], check=False)
        return 0
    print(f"downloaded {archive}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Living-spec coordination runner")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("doctor")
    p_init = sub.add_parser("init")
    p_init.add_argument("--path")
    p_status = sub.add_parser("status")
    p_status.add_argument("--spec")
    p_gate = sub.add_parser("gate")
    p_gate.add_argument("--spec")
    p_ready = sub.add_parser("ready")
    p_ready.add_argument("--spec")
    p_wt = sub.add_parser("worktree")
    wt_sub = p_wt.add_subparsers(dest="wt_cmd", required=True)
    p_add = wt_sub.add_parser("add")
    p_add.add_argument("task_id")
    p_add.add_argument("--spec")
    p_add.add_argument("--repo")
    p_ver = sub.add_parser("verify")
    p_ver.add_argument("--spec")
    p_ver.add_argument("--run", action="store_true")
    sub.add_parser("open-app")
    p_ins = sub.add_parser("install-app")
    p_ins.add_argument("--dry-run", action="store_true")
    p_daemon = sub.add_parser("daemon")
    p_daemon.add_argument(
        "method",
        nargs="?",
        default="status",
        help="status, or a JSON-RPC method such as workspace.list",
    )
    p_daemon.add_argument("--params", default="{}", help="JSON object for intentd call")
    args = p.parse_args(argv)

    if args.cmd == "doctor":
        return cmd_doctor()
    if args.cmd == "init":
        return cmd_init(args.path)
    if args.cmd == "open-app":
        return cmd_open_app()
    if args.cmd == "install-app":
        return cmd_install_app(args.dry_run)
    if args.cmd == "daemon":
        params = None if args.method == "status" else args.params
        return cmd_daemon(args.method, params)
    spec = find_spec(getattr(args, "spec", None))
    if args.cmd == "status":
        return cmd_status(spec)
    if args.cmd == "gate":
        return cmd_gate(spec)
    if args.cmd == "ready":
        return cmd_ready(spec)
    if args.cmd == "worktree":
        return cmd_worktree_add(spec, args.task_id, args.repo)
    if args.cmd == "verify":
        return cmd_verify(spec, args.run)
    return 2


if __name__ == "__main__":
    sys.exit(main())
