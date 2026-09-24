#!/usr/bin/env python3
"""Living-spec runner — portable kernel of Intent (intentapp.dev) coordination.

Enforces approval, dependency waves, git worktree isolation, and checklist
measures. Does not spawn models. The Intent desktop app is optional (doctor /
open-app / install-app). Stdlib-only.

Hardening (H3): quote-aware frontmatter comments, a '#'-free approval grammar,
escaped table pipes (\\|), a measure delimiter (` -- <key>:`), measures run with
shlex + shell=False from a pinned cwd, an allowlist in automated contexts, and a
self-tested invariant that this file never passes commit / push / merge / reset /
stash / rebase to git.

Usage:
  python3 09-tools/intent-run.py doctor
  python3 09-tools/intent-run.py daemon [status|workspace.list]
  python3 09-tools/intent-run.py init [--path PATH]
  python3 09-tools/intent-run.py status [--spec PATH]
  python3 09-tools/intent-run.py gate [--spec PATH]
  python3 09-tools/intent-run.py ready [--spec PATH]
  python3 09-tools/intent-run.py worktree add TASK_ID [--spec PATH] [--repo DIR]
  python3 09-tools/intent-run.py verify [--spec PATH] [--run] [--root DIR]
  python3 09-tools/intent-run.py scope-audit --spec PATH (--task ID --rev A..B | --wave-merges)
                                 [--ref REF] [--root DIR] [--json]
  python3 09-tools/intent-run.py open-app
  python3 09-tools/intent-run.py install-app [--dry-run]
  python3 09-tools/intent-run.py --self-test
"""
from __future__ import annotations

import argparse
import ast
import contextlib
import io
import json
import os
import platform
import posixpath
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOLS = Path(__file__).resolve().parent
TEMPLATE = ROOT / "00-bootstrap" / "templates" / "intent-spec.md"
FIXTURES = TOOLS / "fixtures" / "intent_run"
RELEASES_API = (
    "https://api.github.com/repos/intent-hq/cloudlands-releases/releases/latest"
)
APP_CANDIDATES = (
    Path("/Applications/Intent.app"),
    Path.home() / "Applications" / "Intent.app",
)

GIT_TIMEOUT = 10
MEASURE_TIMEOUT = 3600
_MEASURE_STDIO = None  # inherit; the self-test silences measure output

# A measure ends at the next ` -- <key>:` (e.g. `-- signal: …`), or at end of line.
MEASURE_RE = re.compile(
    r"(?:measure|cmd)\s*:\s*(.+?)(?:\s+--\s+[A-Za-z][\w-]*\s*:.*)?$", re.IGNORECASE
)
BOX_RE = re.compile(r"^[-*]\s+\[([ xX])\]\s+(.*)$")

APPROVAL_DATE_RE = re.compile(
    r"^approved\s+(\d{4}-\d{2}-\d{2})\s+by\s+([^\s#]+)(?:\s+([^#]*))?$", re.IGNORECASE
)
APPROVAL_PR_RE = re.compile(r"^approved\s+via\s+PR\s+#?(\d+)$", re.IGNORECASE)
WAIVED_RE = re.compile(r"^waived\s+\((.+)\)$", re.IGNORECASE)
LOST_ISSUE_COMMENT_RE = re.compile(r"^#\d+")

# Automated-context allowlist: characters that must not appear in the raw measure.
SHELL_META = frozenset(";&|`$<>")
TRACKED_SCRIPT_RE = re.compile(r"^09-tools/[^/]+\.py$")

# The no-git-write invariant (self-tested over this file's AST).
GIT_WRITE_VERBS = frozenset(("commit", "push", "merge", "reset", "stash", "rebase"))


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def _comment_start(val: str) -> int:
    """Index where a `#` comment starts in a frontmatter value, or -1.

    `#` starts a comment only when preceded by whitespace (or at the value's
    start) and outside quotes. A quote opens only at the value start or after
    whitespace, and only when a matching close quote follows.
    """
    i = 0
    n = len(val)
    while i < n:
        ch = val[i]
        prev_ws = i == 0 or val[i - 1].isspace()
        if ch in ("'", '"') and prev_ws:
            close = val.find(ch, i + 1)
            if close > i:
                i = close + 1
                continue
        if ch == "#" and prev_ws:
            return i
        i += 1
    return -1


def _strip_outer_quotes(val: str) -> str:
    if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
        inner = val[1:-1]
        if val[0] not in inner:
            return inner
    return val


def _split_frontmatter_ex(text: str) -> tuple[dict[str, str], str, dict[str, str]]:
    """Return (meta, body, comments). Comments stripped from values are recorded."""
    if not text.startswith("---"):
        return {}, text, {}
    rest = text[3:]
    end = rest.find("\n---")
    if end < 0:
        return {}, text, {}
    raw = rest[:end]
    body = rest[end + 4 :].lstrip("\n")
    meta: dict[str, str] = {}
    comments: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip().lower()
        val = val.strip()
        cut = _comment_start(val)
        if cut >= 0:
            comments[key] = val[cut:].strip()
            val = val[:cut].rstrip()
        meta[key] = _strip_outer_quotes(val)
    return meta, body, comments


def _split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    meta, body, _ = _split_frontmatter_ex(text)
    return meta, body


def _split_row(line: str) -> list[str]:
    """Split a markdown table row on unescaped pipes; `\\|` becomes a literal pipe."""
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|") and not inner.endswith("\\|"):
        inner = inner[:-1]
    cells: list[str] = []
    buf: list[str] = []
    i = 0
    while i < len(inner):
        ch = inner[i]
        if ch == "\\" and i + 1 < len(inner) and inner[i + 1] == "|":
            buf.append("|")
            i += 2
            continue
        if ch == "|":
            cells.append("".join(buf).strip())
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    cells.append("".join(buf).strip())
    return cells


def _parse_table(section: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    header: list[str] | None = None
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            if header and rows:
                break
            continue
        cells = _split_row(line)
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
    meta, body, comments = _split_frontmatter_ex(text)
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
    return {
        "meta": meta,
        "meta_comments": comments,
        "body": body,
        "tasks": tasks,
        "checks": checks,
    }


def load_spec(path: Path) -> dict:
    return parse_spec(path.read_text(encoding="utf-8"))


def approval_ok(meta: dict[str, str]) -> bool:
    a = (meta.get("approval") or "").strip().lower()
    return a.startswith("approved") or a.startswith("waived")


def approval_detail(meta: dict[str, str], comments: dict[str, str] | None = None) -> dict:
    """Parse the approval value against the grammar.

    approved YYYY-MM-DD by <name>[ <free text without #>]
    approved via PR <n>
    waived (<reason>)
    """
    value = (meta.get("approval") or "").strip()
    out: dict = {
        "value": value,
        "ok": approval_ok(meta),
        "kind": "pending",
        "grammar_ok": False,
        "date": None,
        "by": None,
        "note": None,
        "pr": None,
        "reason": None,
        "errors": [],
        "warnings": [],
    }
    m = APPROVAL_DATE_RE.match(value)
    if m:
        out.update(kind="approved", grammar_ok=True, date=m.group(1), by=m.group(2))
        out["note"] = (m.group(3) or "").strip() or None
    elif APPROVAL_PR_RE.match(value):
        out.update(kind="approved-pr", grammar_ok=True, pr=int(APPROVAL_PR_RE.match(value).group(1)))
    elif WAIVED_RE.match(value):
        out.update(kind="waived", grammar_ok=True, reason=WAIVED_RE.match(value).group(1))
    elif not value or value.lower() == "pending":
        out.update(kind="pending", grammar_ok=True)
    else:
        out["kind"] = "invalid"
        out["warnings"].append(
            "approval does not match the grammar: 'approved YYYY-MM-DD by <name>[ note]', "
            "'approved via PR <n>' or 'waived (<reason>)'"
        )
    lost = (comments or {}).get("approval") or ""
    if LOST_ISSUE_COMMENT_RE.match(lost):
        out["errors"].append(
            f"approval lost {lost.split()[0]!r} to a frontmatter comment — quote the whole "
            "value or drop the '#'"
        )
    return out


def lint_spec(spec: dict) -> list[tuple[str, str]]:
    """Findings as (level, message); level is ERROR or WARN. Informational here (H5 consumes)."""
    det = approval_detail(spec["meta"], spec.get("meta_comments"))
    out = [("ERROR", e) for e in det["errors"]]
    out += [("WARN", w) for w in det["warnings"]]
    return out


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


# ---------------------------------------------------------------------------
# Git helpers (read-only plus worktree add; see the no-git-write invariant)
# ---------------------------------------------------------------------------


def _git(args: list[str], cwd: Path, *, timeout: int = GIT_TIMEOUT) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            ["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=timeout
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return subprocess.CompletedProcess(["git", *args], 128, "", str(exc))


def git_root(start: Path) -> Path:
    r = _git(["rev-parse", "--show-toplevel"], start)
    if r.returncode != 0:
        raise SystemExit("not a git repo — worktrees need git")
    return Path(r.stdout.strip())


def _toplevel(path: Path) -> Path | None:
    d = path if path.is_dir() else path.parent
    if not d.is_dir():
        return None
    r = _git(["rev-parse", "--show-toplevel"], d)
    top = r.stdout.strip()
    if r.returncode != 0 or not top:
        return None
    return Path(top).resolve()


def resolve_verify_root(
    spec_path: Path, root: str | None = None, *, proc_cwd: Path | None = None
) -> tuple[Path, str]:
    """The cwd for measures and for `git ls-files` exposure.

    DIR when given. Otherwise the git toplevel of the process cwd when the spec
    is outside that tree or ignored by it, else the spec's own git toplevel.
    """
    if root:
        return Path(root).expanduser().resolve(), "--root"
    pc = (proc_cwd or Path.cwd()).resolve()
    ptop = _toplevel(pc)
    spec = spec_path.resolve()
    if ptop is not None:
        try:
            rel = spec.relative_to(ptop)
        except ValueError:
            return ptop, "process-cwd toplevel (spec outside it)"
        if _git(["check-ignore", "-q", "--", rel.as_posix()], ptop).returncode == 0:
            return ptop, "process-cwd toplevel (spec ignored by it)"
    stop = _toplevel(spec.parent)
    if stop is not None:
        return stop, "spec toplevel"
    return (ptop or pc), "process cwd (no git toplevel)"


def tracked_tool_scripts(root: Path) -> set[str]:
    r = _git(["ls-files", "-z", "--", "09-tools"], root)
    if r.returncode != 0:
        return set()
    return {p for p in r.stdout.split("\0") if p}


# ---------------------------------------------------------------------------
# Automated context (profile_resolve; fail-closed)
# ---------------------------------------------------------------------------


def _import_profile_resolve():
    """Vault consumer import (3d): the vault 09-tools copy, lazily."""
    tools = str(TOOLS)
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import profile_resolve

    here = Path(getattr(profile_resolve, "__file__", "") or "").resolve()
    if here.parent != TOOLS:
        raise ImportError(f"profile_resolve resolved outside 09-tools: {here}")
    return profile_resolve


def automated_context(
    *, env=None, ancestry=None, isatty=None, loader=None
) -> tuple[bool, str]:
    """(automated, source). ImportError or any resolver error → automated (fail-closed)."""
    try:
        mod = loader() if loader else _import_profile_resolve()
        kw = {}
        if env is not None:
            kw["env"] = env
        if ancestry is not None:
            kw["ancestry"] = ancestry
        if isatty is not None:
            kw["isatty"] = isatty
        return bool(mod.automated_context(**kw)), "profile_resolve"
    except Exception as exc:  # fail-closed by contract (3f)
        return True, f"fallback-automated ({type(exc).__name__})"


def exposure_refusal(measure: str, argv: list[str], tracked: set[str]) -> str | None:
    """None when the measure may run in an automated context, else the reason."""
    bad = sorted({c for c in measure if c in SHELL_META})
    if bad:
        return f"shell metacharacter {''.join(bad)!r}"
    if not argv or argv[0] not in ("python3", sys.executable):
        return "argv[0] is not python3"
    if len(argv) < 2:
        return "no script argument"
    norm = posixpath.normpath(argv[1])
    if not TRACKED_SCRIPT_RE.match(norm):
        return "argv[1] is not a 09-tools/*.py script"
    if norm not in tracked:
        return "argv[1] is not git-tracked in the verify root"
    return None


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


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
    r = _git(["--version"], Path.cwd())
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
    r = subprocess.run(cmd, timeout=60)
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
    for level, msg in lint_spec(spec):
        print(f"lint {level}: {msg}")
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
    for level, msg in lint_spec(spec):
        print(f"LINT {level} — {msg}", file=sys.stderr)
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
        timeout=120,
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


def classify_check(check: dict, *, automated: bool, tracked: set[str]) -> tuple[str, str, list[str]]:
    """(status, reason, argv) before execution.

    status: SKIP | HUMAN | HUMAN-ATTESTED | NOT_EXPOSED | BAD | RUN
    """
    measure = str(check.get("measure") or "").strip()
    if not measure:
        return "SKIP", "no measure", []
    if measure.lower().startswith("human:"):
        return ("HUMAN-ATTESTED" if check.get("done") else "HUMAN"), "human step", []
    try:
        argv = shlex.split(measure)
    except ValueError as exc:
        return "BAD", f"unparseable measure ({exc})", []
    if not argv:
        return "SKIP", "empty measure", []
    if automated:
        why = exposure_refusal(measure, argv, tracked)
        if why:
            return "NOT_EXPOSED", why, argv
    return "RUN", "", argv


def cmd_verify(
    spec_path: Path,
    run: bool,
    root: str | None = None,
    *,
    automated: bool | None = None,
    proc_cwd: Path | None = None,
) -> int:
    spec = load_spec(spec_path)
    if not spec["checks"]:
        print("no checklist items", file=sys.stderr)
        return 1
    vroot, why_root = resolve_verify_root(spec_path, root, proc_cwd=proc_cwd)
    if not vroot.is_dir():
        print(f"verify root is not a directory: {vroot}", file=sys.stderr)
        return 2
    if automated is None:
        automated, ctx_src = automated_context()
    else:
        ctx_src = "injected"
    tracked = tracked_tool_scripts(vroot)

    def say(line: str) -> None:
        # One stream, flushed before any measure runs: piped output keeps each verdict under its RUN line.
        print(line, flush=True)

    counts = {"PASS": 0, "FAIL": 0, "SKIP": 0, "NOT_EXPOSED": 0, "HUMAN": 0, "HUMAN-ATTESTED": 0}
    say(f"verify cwd: {vroot} ({why_root})")
    say(f"context: {'automated' if automated else 'interactive'} ({ctx_src})")
    for c in spec["checks"]:
        status, reason, argv = classify_check(c, automated=automated, tracked=tracked)
        label = c["label"]
        if status == "SKIP":
            say(f"SKIP ({reason}): {label}")
            counts["SKIP"] += 1
            continue
        if status in ("HUMAN", "HUMAN-ATTESTED"):
            say(f"{status}: {label}")
            counts[status] += 1
            continue
        if status == "BAD":
            say(f"FAIL ({reason}): {label}")
            counts["FAIL"] += 1
            continue
        if status == "NOT_EXPOSED":
            say(f"NOT_EXPOSED ({reason}): {label}")
            counts["NOT_EXPOSED"] += 1
            continue
        say(f"{'RUN' if run else 'CMD'} {c['measure']}")
        if not run:
            continue
        try:
            rc = subprocess.run(argv, cwd=str(vroot), shell=False, timeout=MEASURE_TIMEOUT,
                                stdout=_MEASURE_STDIO, stderr=_MEASURE_STDIO).returncode
        except FileNotFoundError:
            rc = 127
        except subprocess.TimeoutExpired:
            rc = 124
        except OSError:
            rc = 126
        if rc != 0:
            say(f"FAIL exit {rc}: {label}")
            counts["FAIL"] += 1
        else:
            say(f"PASS {label}")
            counts["PASS"] += 1
    human_total = counts["HUMAN"] + counts["HUMAN-ATTESTED"]
    say(
        f"summary: pass={counts['PASS']} fail={counts['FAIL']} skip={counts['SKIP']} "
        f"not_exposed={counts['NOT_EXPOSED']} human={human_total} "
        f"(attested {counts['HUMAN-ATTESTED']})"
    )
    if not run:
        say("dry — pass --run to execute measures")
        return 0
    if counts["FAIL"] or counts["SKIP"]:
        return 1
    if counts["NOT_EXPOSED"]:
        return 2
    return 0


# ---------------------------------------------------------------------------
# scope-audit
# ---------------------------------------------------------------------------


class ScopeError(ValueError):
    pass


def _split_depth0(cell: str) -> list[str]:
    out: list[str] = []
    buf: list[str] = []
    depth = 0
    for ch in cell:
        if ch in "[{":
            depth += 1
        elif ch in "]}":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            out.append("".join(buf).strip())
            buf = []
            continue
        buf.append(ch)
    out.append("".join(buf).strip())
    return [t for t in out if t]


def _expand_braces(pat: str) -> list[str]:
    m = re.search(r"\{([^{}]*)\}", pat)
    if not m:
        return [pat]
    out: list[str] = []
    for alt in m.group(1).split(","):
        out.extend(_expand_braces(pat[: m.start()] + alt.strip() + pat[m.end() :]))
    return out


def _glob_re(pat: str) -> re.Pattern:
    i = 0
    out = []
    while i < len(pat):
        if pat.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pat.startswith("**", i):
            out.append(".*")
            i += 2
        elif pat[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pat[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pat[i]))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def _is_glob(pat: str) -> bool:
    return any(ch in pat for ch in "*?")


def parse_write_token(tok: str) -> dict:
    tok = tok.strip().strip("`")
    m = re.fullmatch(r"@(\S+)", tok)
    if m:
        return {"kind": "ref", "id": m.group(1)}
    m = re.fullmatch(r"(.+?)\[(.*)\]", tok)
    if m:
        sels = [s.strip() for s in _split_depth0(m.group(2)) if s.strip()]
        return {"kind": "path", "path": m.group(1).strip(), "selectors": sels}
    return {"kind": "path", "path": tok, "selectors": None}


def task_writes(spec: dict, task_id: str, _seen: set[str] | None = None) -> list[dict]:
    """Expanded write entries {path, selectors, re} for a task (resolves @Tn, braces)."""
    by_id = {(t.get("id") or "").strip().upper(): t for t in spec["tasks"]}
    key = task_id.strip().upper()
    if key not in by_id:
        raise ScopeError(f"unknown task {task_id}")
    seen = set(_seen or ())
    if key in seen:
        return []
    seen.add(key)
    cell = (by_id[key].get("writes") or "").strip()
    if cell.lower() in ("", "none", "-", "—", "n/a"):
        return []
    out: list[dict] = []
    for tok in _split_depth0(cell):
        ent = parse_write_token(tok)
        if ent["kind"] == "ref":
            out.extend(task_writes(spec, ent["id"], seen))
            continue
        for p in _expand_braces(ent["path"]):
            out.append({"path": p, "selectors": ent["selectors"], "re": _glob_re(p)})
    return out


def held_entries(spec: dict) -> list[dict]:
    """HELD globs from the spec's `**HELD:**` bullet; `.claude/state/held/**` always."""
    ents = [{"path": ".claude/state/held/**", "body_only": False}]
    lines = spec["body"].splitlines()
    for i, line in enumerate(lines):
        if not re.match(r"^\s*[-*]\s+\*\*HELD:?\*\*", line):
            continue
        indent = len(line) - len(line.lstrip())
        block = [line]
        for nxt in lines[i + 1 :]:
            if not nxt.strip():
                break
            if len(nxt) - len(nxt.lstrip()) <= indent:
                break
            block.append(nxt)
        for bl in block:
            for tok in re.findall(r"`([^`]+)`", bl):
                if "/" not in tok and "." not in tok:
                    continue
                pre = bl[: bl.find("`" + tok + "`")].lower()
                ents.append({"path": tok.strip(), "body_only": "body of" in pre})
        break
    seen: set[tuple[str, bool]] = set()
    uniq = []
    for e in ents:
        k = (e["path"], e["body_only"])
        if k not in seen:
            seen.add(k)
            e["re"] = _glob_re(e["path"])
            uniq.append(e)
    return uniq


def _json_changes(old, new, path: tuple = ()) -> list[tuple]:
    if type(old) is not type(new):
        return [path]
    if isinstance(old, dict):
        out: list[tuple] = []
        for k in list(old.keys()) + [k for k in new.keys() if k not in old]:
            if k not in old or k not in new:
                out.append(path + (k,))
            else:
                out.extend(_json_changes(old[k], new[k], path + (k,)))
        return out
    if isinstance(old, list):
        def ids(lst):
            if not all(isinstance(x, dict) and "id" in x for x in lst):
                return None
            keys = [str(x["id"]) for x in lst]
            return keys if len(set(keys)) == len(keys) else None

        oi, ni = ids(old), ids(new)
        if oi is not None and ni is not None:
            om = {str(x["id"]): x for x in old}
            nm = {str(x["id"]): x for x in new}
            out = []
            for k in oi + [k for k in ni if k not in om]:
                if k not in om or k not in nm:
                    out.append(path + (k,))
                else:
                    out.extend(_json_changes(om[k], nm[k], path + (k,)))
            return out
        return [] if old == new else [path]
    return [] if old == new else [path]


def _selector_covers(selector: str, change: tuple) -> bool:
    parts = [p for p in selector.split(".") if p]
    if not parts or len(change) < len(parts):
        return False
    return all(s == "*" or s == str(c) for s, c in zip(parts, change))


def _blob(root: Path, rev: str, path: str) -> str | None:
    r = _git(["cat-file", "-p", f"{rev}:{path}"], root)
    return r.stdout if r.returncode == 0 else None


def _body_of(text: str | None) -> str | None:
    if text is None:
        return None
    return _split_frontmatter_ex(text)[1] if text.startswith("---") else text


def _commit_log(root: Path, rng: list[str]) -> list[dict]:
    r = _git(["log", "--format=%H%x1f%P%x1f%s%x1f%b%x1e", *rng], root)
    if r.returncode != 0:
        raise ScopeError(f"git log failed: {r.stderr.strip()[:200]}")
    out = []
    for rec in r.stdout.split("\x1e"):
        rec = rec.strip("\n")
        if not rec.strip():
            continue
        parts = rec.split("\x1f")
        while len(parts) < 4:
            parts.append("")
        out.append({"sha": parts[0].strip(), "parents": parts[1].split(), "subject": parts[2], "body": parts[3]})
    return out


def unreverted_autocommits(root: Path, base: str, tip: str) -> list[str]:
    commits = _commit_log(root, [f"{base}..{tip}"])
    autos = [c["sha"] for c in commits if c["subject"].strip().startswith("session: auto-commit")]
    reverted = set()
    for c in commits:
        for m in re.finditer(r"This reverts commit ([0-9a-f]{7,40})", c["body"] + "\n" + c["subject"]):
            reverted.add(m.group(1))
    return [a for a in autos if not any(a.startswith(r) for r in reverted)]


def audit_diff(
    root: Path, old_rev: str, new_rev: str, allowed: list[dict], held: list[dict]
) -> tuple[list[str], list[str], int]:
    """(violations, notes, n_paths) for the tree diff old_rev → new_rev."""
    r = _git(["diff", "--name-only", "--no-renames", old_rev, new_rev], root)
    if r.returncode != 0:
        raise ScopeError(f"git diff failed: {r.stderr.strip()[:200]}")
    paths = [p for p in r.stdout.splitlines() if p.strip()]
    violations: list[str] = []
    notes: list[str] = []
    for p in paths:
        matched = [e for e in allowed if e["re"].match(p)]
        exact = any(e["path"] == p and not _is_glob(e["path"]) for e in allowed)
        for h in held:
            if not h["re"].match(p) or exact:
                continue
            if h["body_only"] and _body_of(_blob(root, old_rev, p)) == _body_of(_blob(root, new_rev, p)):
                continue
            violations.append(f"held: {p}" + (" (body changed)" if h["body_only"] else ""))
            break
        if not matched:
            violations.append(f"outside-writes: {p}")
            continue
        if any(e["selectors"] is None for e in matched):
            continue
        sels = sorted({s for e in matched for s in (e["selectors"] or [])})
        if not p.endswith(".json"):
            notes.append(f"section-selector: {p}[{', '.join(sels)}] (file-level audit only)")
            continue
        old_t, new_t = _blob(root, old_rev, p), _blob(root, new_rev, p)
        if new_t is None:
            violations.append(f"json-selector: {p} deleted (selectors {', '.join(sels)})")
            continue
        try:
            old_j = json.loads(old_t) if old_t is not None else {}
            new_j = json.loads(new_t)
        except ValueError:
            violations.append(f"json-selector: {p} is not valid JSON")
            continue
        outside = [c for c in _json_changes(old_j, new_j) if not any(_selector_covers(s, c) for s in sels)]
        if outside:
            shown = ", ".join(".".join(str(x) for x in c) or "<root>" for c in outside[:5])
            violations.append(f"json-selector: {p} changed outside [{', '.join(sels)}]: {shown}")
    return violations, notes, len(paths)


def _wave_prefix(spec: dict) -> str:
    w = str(spec["meta"].get("wave") or "").strip()
    return re.escape(w) if re.fullmatch(r"\d+", w) else r"\d+"


def _union_allowed(spec: dict, ids: list[str]) -> list[dict]:
    out: list[dict] = []
    for tid in ids:
        out.extend(task_writes(spec, tid))
    return out


def _integrator_base(spec: dict) -> list[str]:
    ids = {(t.get("id") or "").strip().upper() for t in spec["tasks"]}
    return ["T9a"] if "T9A" in ids else []


def _main_checkout_path(rel: Path) -> Path | None:
    """`rel` under the main checkout of the repo that owns cwd (a held spec is gitignored, so a linked
    worktree never has its own copy), or None."""
    r = _git(["rev-parse", "--path-format=absolute", "--git-common-dir"], Path.cwd())
    if r.returncode != 0 or not r.stdout.strip():
        return None
    cand = Path(r.stdout.strip()).parent / rel
    return cand.resolve() if cand.is_file() else None


def cmd_scope_audit(
    spec_path: Path,
    *,
    task: str | None,
    rev: str | None,
    wave_merges: bool,
    ref: str = "main",
    root: str | None = None,
    as_json: bool = False,
) -> int:
    spec = load_spec(spec_path)
    if root:
        aroot = Path(root).expanduser().resolve()
    else:
        aroot = _toplevel(Path.cwd()) or Path.cwd()
    held = held_entries(spec)
    base_ids = _integrator_base(spec)
    records: list[dict] = []
    try:
        if task:
            if not rev or ".." not in rev:
                raise ScopeError("--task needs --rev A..B")
            a, b = rev.split("..", 1)
            a, b = a or "HEAD", b or "HEAD"
            own_ents = task_writes(spec, task)
            allowed = own_ents + _union_allowed(spec, base_ids)
            commits = _commit_log(aroot, [f"{a}..{b}"])
            if not commits:
                return _emit_audit(records, as_json, mode="task", nothing=True)
            mb = _git(["merge-base", a, b], aroot)
            if mb.returncode != 0:
                raise ScopeError(f"no merge-base for {rev}")
            base = mb.stdout.strip()
            vio, notes, n = audit_diff(aroot, base, b, allowed, held)
            d = _git(["diff", "--name-only", "--no-renames", base, b], aroot)
            for p in d.stdout.splitlines():
                if p and not any(e["re"].match(p) for e in own_ents) and any(
                    e["re"].match(p) for e in allowed
                ):
                    notes.append(f"integrator path on task branch: {p}")
            for s in unreverted_autocommits(aroot, a, b):
                vio.append(f"auto-commit: {s[:12]} unreverted")
            records.append({"sha": b, "subject": f"{task} {rev}", "task": task, "paths": n,
                            "violations": vio, "notes": notes})
            return _emit_audit(records, as_json, mode="task")
        if not wave_merges:
            raise ScopeError("pass --task ID --rev A..B or --wave-merges")
        wp = _wave_prefix(spec)
        merge_re = re.compile(rf"^wave{wp}\(([^)]+)\): merge intent/(\S+)\s*$")
        fix_re = re.compile(rf"^wave{wp}\(([^)]+)\): F-(\d+) \(([^)]+)\)")
        if _git(["rev-parse", "--verify", "--quiet", ref], aroot).returncode != 0:
            return _emit_audit(records, as_json, mode="wave-merges", nothing=True)
        for c in _commit_log(aroot, ["--first-parent", ref]):
            m = merge_re.match(c["subject"].strip())
            if not m or len(c["parents"]) < 2:
                continue
            integ, tid = m.group(1), m.group(2)
            ids = [tid] + base_ids
            if integ.strip().upper() in {(t.get("id") or "").strip().upper() for t in spec["tasks"]}:
                ids.append(integ.strip())
            allowed = _union_allowed(spec, ids)
            p1, p2 = c["parents"][0], c["parents"][1]
            vio, notes, n = audit_diff(aroot, p1, c["sha"], allowed, held)
            for s in unreverted_autocommits(aroot, p1, p2):
                vio.append(f"auto-commit: {s[:12]} unreverted")
            records.append({"sha": c["sha"], "subject": c["subject"], "task": tid, "paths": n,
                            "violations": vio, "notes": notes})
        direct_re = re.compile(rf"^wave{wp}\(([^)]+)\): ")
        for c in _commit_log(aroot, ["--first-parent", ref]):
            subj = c["subject"].strip()
            if len(c["parents"]) >= 2 or merge_re.match(subj) or fix_re.match(subj) or not direct_re.match(subj):
                continue
            records.append({"sha": c["sha"], "subject": c["subject"], "task": direct_re.match(subj).group(1),
                            "paths": 0, "violations": [],
                            "notes": ["unaudited direct commit (not a task merge or a fix-round commit)"]})
        for c in _commit_log(aroot, [ref]):
            m = fix_re.match(c["subject"].strip())
            if not m or not c["parents"]:
                continue
            owner = m.group(3).strip()
            allowed = _union_allowed(spec, [owner] + base_ids)
            vio, notes, n = audit_diff(aroot, c["parents"][0], c["sha"], allowed, held)
            records.append({"sha": c["sha"], "subject": c["subject"], "task": owner, "paths": n,
                            "violations": vio, "notes": notes})
        return _emit_audit(records, as_json, mode="wave-merges", nothing=not records)
    except ScopeError as exc:
        if as_json:
            print(json.dumps({"schema_version": 1, "cmd": "scope-audit", "error": str(exc)}))
        else:
            print(f"scope-audit: {exc}", file=sys.stderr)
        return 2


def _emit_audit(records: list[dict], as_json: bool, *, mode: str, nothing: bool = False) -> int:
    nv = sum(len(r["violations"]) for r in records)
    nn = sum(len(r["notes"]) for r in records)
    rc = 3 if nothing else (1 if nv else 0)
    if as_json:
        print(json.dumps({"schema_version": 1, "cmd": "scope-audit", "mode": mode,
                          "commits": records, "violations": nv, "notes": nn, "exit": rc},
                         indent=2, ensure_ascii=False))
        return rc
    if nothing:
        print("scope-audit: nothing to audit (no matching commits)")
        return rc
    for r in records:
        print(f"AUDIT {r['sha'][:12]} task={r['task']} paths={r['paths']} :: {r['subject']}")
        for v in r["violations"]:
            print(f"  VIOLATION {v}")
        for n in r["notes"]:
            print(f"  NOTE {n}")
    print(f"scope-audit: {len(records)} commit(s), {nv} violation(s), {nn} note(s)")
    return rc


def cmd_open_app() -> int:
    app = find_app()
    if app is None:
        print("Intent.app not installed. Run: python3 09-tools/intent-run.py install-app")
        return 1
    subprocess.run(["open", str(app)], check=False, timeout=30)
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
            subprocess.run(["open", str(target)], check=False, timeout=30)
            return 0
    if name.endswith(".dmg"):
        print(f"downloaded {archive} — open the dmg and drag Intent.app to Applications")
        subprocess.run(["open", str(archive)], check=False, timeout=30)
        return 0
    print(f"downloaded {archive}")
    return 0


# ---------------------------------------------------------------------------
# No-git-write invariant
# ---------------------------------------------------------------------------


def _call_name(node: ast.Call) -> str:
    f = node.func
    if isinstance(f, ast.Attribute):
        return f.attr
    if isinstance(f, ast.Name):
        return f.id
    return ""


def git_write_violations(source: str) -> list[str]:
    """Calls that pass commit/push/merge/reset/stash/rebase to git (list or string form)."""
    out: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node)
        args = list(node.args) + [k.value for k in node.keywords]
        for arg in args:
            if isinstance(arg, (ast.List, ast.Tuple)):
                consts = [e.value for e in arg.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
                gitish = "git" in consts or "git" in name.lower()
                verbs = GIT_WRITE_VERBS.intersection(consts)
                if gitish and verbs:
                    out.append(f"line {node.lineno}: {name}(... {sorted(verbs)} ...)")
            elif isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                toks = arg.value.split()
                if len(toks) >= 2 and toks[0] == "git" and GIT_WRITE_VERBS.intersection(toks[1:]):
                    out.append(f"line {node.lineno}: {name}({arg.value[:40]!r})")
    return out


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------


def _legacy_parse(text: str) -> dict:
    """The pre-H3 parser, kept only as a parity oracle for held specs (self-test)."""
    meta: dict[str, str] = {}
    body = text
    if text.startswith("---"):
        rest = text[3:]
        end = rest.find("\n---")
        if end >= 0:
            body = rest[end + 4 :].lstrip("\n")
            for line in rest[:end].splitlines():
                if not line.strip() or line.strip().startswith("#") or ":" not in line:
                    continue
                key, val = line.split(":", 1)
                meta[key.strip().lower()] = val.split("#", 1)[0].strip().strip("'\"")
    rows: list[dict[str, str]] = []
    header: list[str] | None = None
    for line in _section(body, "Task graph").splitlines():
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
        rows.append({header[i]: cells[i] if i < len(cells) else "" for i in range(len(header))})
    old_re = re.compile(r"(?:measure|cmd)\s*:\s*(.+)$", re.IGNORECASE)
    checks = []
    for line in _section(body, "Fidelity / acceptance checklist").splitlines():
        bm = BOX_RE.match(line.strip())
        if not bm:
            continue
        rest = bm.group(2).strip()
        mm = old_re.search(rest)
        checks.append({
            "label": rest[: mm.start()].strip(" -–—") if mm else rest,
            "measure": mm.group(1).strip() if mm else "",
            "done": bm.group(1).lower() == "x",
        })
    return {"meta": meta, "tasks": rows, "checks": checks}


def _held_spec_candidates() -> list[Path]:
    dirs = [ROOT / ".claude" / "state" / "held"]
    r = _git(["rev-parse", "--path-format=absolute", "--git-common-dir"], ROOT)
    if r.returncode == 0 and r.stdout.strip():
        main_root = Path(r.stdout.strip()).parent
        dirs.append(main_root / ".claude" / "state" / "held")
    out: list[Path] = []
    for d in dirs:
        if d.is_dir():
            for p in sorted(d.glob("INTENT-*.md")):
                if p.resolve() not in [q.resolve() for q in out]:
                    out.append(p)
    return out


class _FakeResolver:
    """Contract fake for profile_resolve.automated_context (3c): used until T9a merges T2."""

    MARKERS = {
        "claude": {"WS_SURFACE_FAMILY": "claude"},
        "cursor": {"CURSOR_AGENT": "1"},
        "codex": {"CODEX_SANDBOX": "seatbelt"},
        "gemini": {"GEMINI_CLI": "1"},
        "copilot": {"VSCODE_COPILOT_CHAT": "1"},
        "none": {},
    }
    AGENT_POSSIBLE = ("CLAUDECODE", "CLAUDE_PROJECT_DIR", "CLAUDE_PLUGIN_ROOT",
                      "CLAUDE_WORKSPACE_VAULT", "CLAUDE_ENV_FILE")

    @classmethod
    def automated_context(cls, *, env=None, ancestry=None, isatty=None, root=None):
        env = env or {}
        tty = isatty or {"stdin": False, "stdout": False}
        if env.get("CI") or env.get("GITHUB_ACTIONS"):
            return True
        for fam_env in cls.MARKERS.values():
            if fam_env and all(env.get(k) == v for k, v in fam_env.items()):
                return True
        if any(k in env for k in cls.AGENT_POSSIBLE) or any(k.startswith("CLAUDE_CODE_") for k in env):
            return True
        if ancestry:
            return True
        return not (tty.get("stdin") and tty.get("stdout"))


def _fixture_env(home: Path) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update({
        "HOME": str(home),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
    })
    return env


def _run_fixture_git(args: list[str], cwd: Path, env: dict, stdin: bytes | None = None) -> str:
    tmp = Path(tempfile.gettempdir()).resolve()
    if tmp not in cwd.resolve().parents and cwd.resolve() != tmp:
        raise RuntimeError(f"fixture git refused outside the temp dir: {cwd}")
    r = subprocess.run(["git", *args], cwd=str(cwd), env=env, input=stdin,
                       capture_output=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError(f"fixture git {args[0]} failed: {r.stderr.decode(errors='replace')[:300]}")
    return r.stdout.decode(errors="replace")


class _History:
    """Synthetic history built with `git fast-import` inside a temp dir (no porcelain writes)."""

    def __init__(self, repo: Path, env: dict):
        self.repo, self.env = repo, env
        self.mark = 0
        self.t = 1_700_000_000
        self.chunks: list[bytes] = []
        self.marks_file = repo.parent / (repo.name + ".marks")

    @staticmethod
    def _data(text: str) -> bytes:
        raw = text.encode("utf-8")
        return b"data %d\n" % len(raw) + raw + b"\n"

    def commit(self, branch: str, msg: str, files: dict | None = None, *, frm: str | None = None,
               merge: str | None = None, deletes: tuple = ()) -> str:
        self.mark += 1
        self.t += 60
        who = f"Fixture <fixture@example.invalid> {self.t} +0000"
        buf = [f"commit refs/heads/{branch}\n".encode(), f"mark :{self.mark}\n".encode(),
               f"author {who}\n".encode(), f"committer {who}\n".encode(), self._data(msg)]
        if frm:
            buf.append(f"from {frm}\n".encode())
        if merge:
            buf.append(f"merge {merge}\n".encode())
        for p, content in (files or {}).items():
            buf.append(f"M 100644 inline {p}\n".encode())
            buf.append(self._data(content))
        for p in deletes:
            buf.append(f"D {p}\n".encode())
        self.chunks.append(b"".join(buf) + b"\n")
        return f":{self.mark}"

    def flush(self) -> None:
        args = ["fast-import", "--quiet", f"--export-marks={self.marks_file}"]
        if self.marks_file.exists():
            args.append(f"--import-marks={self.marks_file}")
        _run_fixture_git(args, self.repo, self.env, b"".join(self.chunks) + b"done\n")
        self.chunks = []

    def sha(self, mark: str) -> str:
        for line in self.marks_file.read_text().splitlines():
            m, s = line.split()
            if m == mark:
                return s
        raise KeyError(mark)


def _new_repo(td: Path, name: str) -> tuple[Path, dict]:
    home = td / "home"
    home.mkdir(exist_ok=True)
    env = _fixture_env(home)
    repo = td / name
    repo.mkdir()
    _run_fixture_git(["init", "-q", "-b", "main"], repo, env)
    return repo, env


def _quiet(fn, *a, **kw):
    buf_o, buf_e = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(buf_o), contextlib.redirect_stderr(buf_e):
        rc = fn(*a, **kw)
    return rc, buf_o.getvalue() + buf_e.getvalue()


def _fixture_spec_text() -> str:
    p = FIXTURES / "synthetic-spec.md"
    return p.read_text(encoding="utf-8")


def _st_parser() -> None:
    cases = json.loads((FIXTURES / "parser-cases.json").read_text(encoding="utf-8"))
    for case in cases["frontmatter"]:
        text = "---\n" + case["line"] + "\n---\n# x\n"
        meta, _, comments = _split_frontmatter_ex(text)
        key = case["line"].split(":", 1)[0].strip().lower()
        assert meta.get(key) == case["value"], (case, meta.get(key))
        if "comment" in case:
            assert comments.get(key) == case["comment"], (case, comments)
        if "lint_error" in case:
            det = approval_detail(meta, comments)
            assert bool(det["errors"]) == case["lint_error"], (case, det)
        if "kind" in case:
            det = approval_detail(meta, comments)
            assert det["kind"] == case["kind"], (case, det)
            assert det["ok"] == case.get("ok", True), (case, det)
    for case in cases["tables"]:
        rows = _parse_table(case["table"])
        assert rows and rows[0].get(case["column"]) == case["cell"], (case, rows)
    for case in cases["measures"]:
        spec = parse_spec("---\nprofile: p\n---\n## Fidelity / acceptance checklist\n\n" + case["line"] + "\n")
        got = spec["checks"][0]
        assert got["measure"] == case["measure"], (case, got)
        if "label" in case:
            assert got["label"] == case["label"], (case, got)
    # The template still parses as a pending, grammar-valid spec.
    if TEMPLATE.is_file():
        t = load_spec(TEMPLATE)
        det = approval_detail(t["meta"], t["meta_comments"])
        assert det["kind"] == "pending" and not det["errors"], det
        assert not approval_ok(t["meta"])


def _st_fixture_spec() -> None:
    spec = parse_spec(_fixture_spec_text())
    ids = [t["id"] for t in spec["tasks"]]
    assert ids == ["T0", "T1", "T2", "T9a", "T9b", "T3", "V1"], ids
    det = approval_detail(spec["meta"], spec["meta_comments"])
    assert det["ok"] and det["grammar_ok"] and det["kind"] == "approved", det
    assert det["note"] and "(" in det["note"], det
    t1 = index_tasks(spec["tasks"])["T1"]
    assert t1["skill_specialist"] == "alpha (foo|bar)", t1
    w = task_writes(spec, "T1")
    sel = [e for e in w if e["path"] == "data/table.json"]
    assert sel and sel[0]["selectors"] == ["rows.*.cov.A1", "outputs"], w
    w3 = {e["path"] for e in task_writes(spec, "T3")}
    assert "tools/alpha.py" in w3 and "tools/beta.py" in w3, w3
    w9b = {e["path"] for e in task_writes(spec, "T9b")}
    assert w9b == {e["path"] for e in task_writes(spec, "T9a")}, w9b
    assert {"docs/one.md", "docs/two.md"} <= {e["path"] for e in task_writes(spec, "T2")}
    assert task_writes(spec, "V1") == []
    held = {(h["path"], h["body_only"]) for h in held_entries(spec)}
    assert ("mem/rule.md", True) in held and ("secrets/policy.json", False) in held, held
    human = [c for c in spec["checks"] if str(c["measure"]).startswith("human:")]
    assert human, spec["checks"]
    sig = [c for c in spec["checks"] if c["label"].startswith("tool self-test")]
    assert sig and sig[0]["measure"] == "python3 09-tools/tool.py --self-test", sig


class _Skip(Exception):
    """A self-test case that could not run here: reported as SKIP, never counted as ok."""


def _st_held_parity() -> str:
    found = _held_spec_candidates()
    if not found:
        raise _Skip("no held spec on this checkout")
    for p in found:
        text = p.read_text(encoding="utf-8")
        old, new = _legacy_parse(text), parse_spec(text)
        assert [t.get("id") for t in old["tasks"]] == [t.get("id") for t in new["tasks"]], p.name
        assert old["tasks"] == new["tasks"], f"{p.name}: task rows differ"
        oc = [(c["label"], c["measure"], c["done"]) for c in old["checks"]]
        nc = [(c["label"], c["measure"], c["done"]) for c in new["checks"]]
        assert oc == nc, f"{p.name}: checklist differs"
        if approval_ok(old["meta"]):
            assert approval_ok(new["meta"]), f"{p.name}: approval_ok regressed"
    return f"{len(found)} held spec(s) parse identically"


def _st_invariant() -> None:
    own = git_write_violations(Path(__file__).read_text(encoding="utf-8"))
    assert not own, own
    planted = "import subprocess\nsubprocess.run(['git','commit'])\n"
    assert git_write_violations(planted), "planted list form not detected"
    assert git_write_violations("import subprocess\nsubprocess.run('git push origin', shell=True)\n")
    assert git_write_violations("_git(['reset', '--hard'], cwd)\n")
    assert not git_write_violations("subprocess.run(['git','log'])\n")
    if os.environ.get("INTENT_RUN_SELFTEST_ONLY") == "invariant":
        return
    with tempfile.TemporaryDirectory() as td:
        copy = Path(td) / "09-tools" / "intent-run.py"
        copy.parent.mkdir()
        copy.write_text(Path(__file__).read_text(encoding="utf-8")
                        + "\n\ndef _planted():\n    subprocess.run(['git','commit'])\n", encoding="utf-8")
        env = dict(os.environ, INTENT_RUN_SELFTEST_ONLY="invariant")
        r = subprocess.run([sys.executable, str(copy), "--self-test"], capture_output=True,
                           text=True, env=env, timeout=60)
        assert r.returncode == 1, (r.returncode, r.stdout[-400:])
        assert "no-git-write" in r.stdout and "FAIL" in r.stdout, r.stdout[-400:]


def _verify_spec(td: Path, checklist: str) -> Path:
    p = td / "spec.md"
    p.write_text("---\nprofile: personal-solo\napproval: approved 2026-01-01 by Fixture\n---\n"
                 "## Fidelity / acceptance checklist\n\n" + checklist + "\n", encoding="utf-8")
    return p


def _st_verify() -> None:
    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds).resolve()
        repo, env = _new_repo(td, "vroot")
        (repo / "09-tools").mkdir()
        (repo / "09-tools" / "ok.py").write_text(
            "from pathlib import Path\nPath('ran-ok').write_text('1')\n", encoding="utf-8")
        (repo / "09-tools" / "untracked.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
        _run_fixture_git(["add", "09-tools/ok.py"], repo, env)
        pwned = td / "pwned"
        human_mark = td / "human-ran"
        checklist = "\n".join([
            "- [ ] tracked script -- measure: python3 09-tools/ok.py",
            f"- [ ] injected -- measure: python3 09-tools/ok.py; touch {pwned}",
            "- [ ] untracked -- measure: python3 09-tools/untracked.py",
            f"- [ ] human step -- measure: human: python3 -c \"open('{human_mark}','w')\"",
            f"- [x] human attested -- measure: human: touch {human_mark}",
        ])
        spec = _verify_spec(td, checklist)
        # Automated (CI=1 through the injected resolver): injected `;` never runs, exit 2.
        auto, _ = automated_context(env={"CI": "1"}, isatty={"stdin": True, "stdout": True},
                                    loader=lambda: _FakeResolver)
        assert auto is True
        rc, out = _quiet(cmd_verify, spec, True, str(repo), automated=auto)
        assert rc == 2, (rc, out)
        assert not pwned.exists(), "injected command ran"
        assert not human_mark.exists(), "human measure ran"
        assert (repo / "ran-ok").exists(), "tracked script did not run in --root"
        assert "HUMAN: human step" in out and "HUMAN-ATTESTED: human attested" in out, out
        assert out.count("NOT_EXPOSED") >= 2, out
        # An item with no measure is a SKIP, and a SKIP never lets verify --run pass.
        spec_nm = _verify_spec(td, "- [ ] tracked script -- measure: python3 09-tools/ok.py\n- [ ] no measure here")
        rc_nm, out_nm = _quiet(cmd_verify, spec_nm, True, str(repo), automated=False)
        assert rc_nm == 1 and "SKIP" in out_nm, (rc_nm, out_nm)
        # Interactive: shell=False still never runs the injected command; human still never runs.
        (repo / "ran-ok").unlink()
        rc, out = _quiet(cmd_verify, spec, True, str(repo), automated=False)
        assert rc == 1, (rc, out)
        assert not pwned.exists() and not human_mark.exists(), out
        # Marker matrix: identical outcomes under every family marker (no TTY, injected).
        outcomes = set()
        for fam, fam_env in _FakeResolver.MARKERS.items():
            a, _ = automated_context(env=dict(fam_env), isatty={"stdin": False, "stdout": False},
                                     loader=lambda: _FakeResolver)
            rc, out = _quiet(cmd_verify, spec, True, str(repo), automated=a)
            statuses = tuple(line.split(" ", 1)[0] for line in out.splitlines()
                             if line.split(" ", 1)[0] in ("PASS", "FAIL", "NOT_EXPOSED", "HUMAN:",
                                                           "HUMAN-ATTESTED:", "SKIP"))
            outcomes.add((a, rc, statuses))
        assert len(outcomes) == 1, outcomes
        assert not pwned.exists() and not human_mark.exists()
        # CLAUDECODE=1 with a TTY is automated (agent possible).
        a, _ = automated_context(env={"CLAUDECODE": "1"}, ancestry=[],
                                 isatty={"stdin": True, "stdout": True}, loader=lambda: _FakeResolver)
        assert a is True
        # Missing resolver → automated (fail-closed).
        def _boom():
            raise ImportError("absent")
        a, src = automated_context(loader=_boom)
        assert a is True and src.startswith("fallback"), src
        # Real resolver, when merged: same CLAUDECODE + TTY verdict.
        try:
            real = _import_profile_resolve()
        except Exception:
            real = None
        if real is not None and hasattr(real, "automated_context"):
            a, _ = automated_context(env={"CLAUDECODE": "1"}, ancestry=[],
                                     isatty={"stdin": True, "stdout": True}, loader=lambda: real)
            assert a is True, "real profile_resolve: CLAUDECODE+TTY must be automated"
        # cwd resolution: a spec ignored by the process-cwd tree resolves to that toplevel.
        (repo / ".gitignore").write_text("held/\n", encoding="utf-8")
        (repo / "held").mkdir()
        ign = repo / "held" / "INTENT-x.md"
        ign.write_text(spec.read_text(encoding="utf-8"), encoding="utf-8")
        (repo / "sub").mkdir()
        got, why = resolve_verify_root(ign, None, proc_cwd=repo / "sub")
        assert got == repo.resolve() and "ignored" in why, (got, why)
        # A spec outside the process-cwd tree → the process-cwd toplevel.
        got, why = resolve_verify_root(spec, None, proc_cwd=repo / "sub")
        assert got == repo.resolve() and "outside" in why, (got, why)
        # --root wins.
        got, why = resolve_verify_root(ign, str(td), proc_cwd=repo / "sub")
        assert got == td and why == "--root", (got, why)
        # A spec tracked inside the process-cwd tree → its own toplevel.
        (repo / "docs").mkdir()
        tracked_spec = repo / "docs" / "INTENT.md"
        tracked_spec.write_text("x\n", encoding="utf-8")
        got, why = resolve_verify_root(tracked_spec, None, proc_cwd=repo / "sub")
        assert got == repo.resolve() and why == "spec toplevel", (got, why)
        # Exposure uses `git ls-files` in the verify root.
        assert exposure_refusal("python3 09-tools/ok.py", ["python3", "09-tools/ok.py"],
                                tracked_tool_scripts(repo)) is None
        assert exposure_refusal("python3 09-tools/untracked.py", ["python3", "09-tools/untracked.py"],
                                tracked_tool_scripts(repo))
        assert exposure_refusal("bash 09-tools/ok.py", ["bash", "09-tools/ok.py"], {"09-tools/ok.py"})
        assert exposure_refusal("python3 ../09-tools/ok.py", ["python3", "../09-tools/ok.py"],
                                {"09-tools/ok.py"})
        # Piped (T10 rerun T-03): each RUN line is followed by its own verdict, before the next RUN,
        # with the measures' own output inherited on the same pipe.
        for name, code in (("p1", 0), ("f2", 2), ("p3", 0)):
            (repo / "09-tools" / f"{name}.py").write_text(
                f"print('measure output {name}')\nraise SystemExit({code})\n", encoding="utf-8")
            _run_fixture_git(["add", f"09-tools/{name}.py"], repo, env)
        piped = _verify_spec(td, "\n".join(f"- [ ] {n} -- measure: python3 09-tools/{n}.py" for n in ("p1", "f2", "p3")))
        r = subprocess.run([sys.executable, str(Path(__file__).resolve()), "verify", "--spec", str(piped), "--run",
                            "--root", str(repo)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                           timeout=120)
        lines = r.stdout.splitlines()
        runs = [i for i, ln in enumerate(lines) if ln.startswith("RUN ")]
        assert lines and lines[0].startswith("verify cwd:") and len(runs) == 3, r.stdout
        for i, want in zip(runs, ("PASS p1", "FAIL exit 2: f2", "PASS p3")):
            nxt = next(ln for ln in lines[i + 1:] if ln.startswith(("PASS", "FAIL", "RUN ")))
            assert nxt == want, (want, r.stdout)


def _audit_spec_path(td: Path) -> Path:
    p = td / "INTENT-fixture.md"
    p.write_text(_fixture_spec_text(), encoding="utf-8")
    return p


def _st_scope_audit() -> None:
    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds).resolve()
        spec = _audit_spec_path(td)
        base_files = {
            "README.md": "base\n",
            "data/table.json": json.dumps({"rows": [{"id": "a", "cov": {"A1": "x", "B2": "y"}}],
                                           "outputs": [], "other": 1}, indent=2) + "\n",
            "mem/rule.md": "---\nupdated: 2026-01-01\n---\nbody\n",
            "notes/beta.md": "# beta\n",
        }

        counter = [0]

        def scenario(name, branch_files, *, merge_subject=None, extra=None, deletes=()):
            counter[0] += 1
            repo, env = _new_repo(td, f"{name}-{counter[0]}")
            h = _History(repo, env)
            b0 = h.commit("main", "base", base_files)
            s = h.commit(f"intent/{name}", f"wave0({name}): start", frm=b0)
            tip = h.commit(f"intent/{name}", f"wave0({name}): work", branch_files, frm=s, deletes=deletes)
            if extra:
                tip = extra(h, name, tip)
            h.flush()
            if merge_subject is not None:
                merged = dict(branch_files)
                merged["tools/test-validators.py"] = "# integrator\n"
                h.commit("main", merge_subject, merged, frm=b0, merge=tip, deletes=deletes)
                h.flush()
            return repo, h

        def audit(repo, **kw):
            return _quiet(cmd_scope_audit, spec, task=kw.get("task"), rev=kw.get("rev"),
                          wave_merges=kw.get("wave_merges", False), ref="main", root=str(repo),
                          as_json=False)

        # 1. No wave merges yet → exit 3.
        repo, _ = scenario("T1", {"tools/alpha.py": "a\n"})
        rc, out = audit(repo, wave_merges=True)
        assert rc == 3, (rc, out)
        # 2. Task writes ∪ @T9a passes (the merge also carries an integrator path).
        repo, _ = scenario("T2", {"tools/beta.py": "b\n", "docs/one.md": "1\n", "gen/registry.json": "{}\n"},
                           merge_subject="wave0(T9a): merge intent/T2")
        rc, out = audit(repo, wave_merges=True)
        assert rc == 0, (rc, out)
        # The pre-merge form T9 runs: --task ID --rev main..intent/<id>.
        repo, _ = scenario("T2", {"tools/beta.py": "b\n", "tools/test-validators.py": "# w9\n"})
        rc, out = audit(repo, task="T2", rev="main..intent/T2")
        assert rc == 0 and "NOTE integrator path on task branch: tools/test-validators.py" in out, (rc, out)
        repo, _ = scenario("T2", {"tools/beta.py": "b\n", "secrets/policy.json": "{}\n"})
        rc, out = audit(repo, task="T2", rev="main..intent/T2")
        assert rc == 1 and "held: secrets/policy.json" in out, (rc, out)
        # 3. A path outside writes ∪ @T9a fails.
        repo, _ = scenario("T1", {"tools/alpha.py": "a\n", "tools/beta.py": "x\n"},
                           merge_subject="wave0(T9a): merge intent/T1")
        rc, out = audit(repo, wave_merges=True)
        assert rc == 1 and "outside-writes: tools/beta.py" in out, (rc, out)
        # 4. HELD fails (held glob, and a body change of a body-held file).
        repo, _ = scenario("T1", {"tools/alpha.py": "a\n", "held/INTENT-x.md": "x\n"},
                           merge_subject="wave0(T9a): merge intent/T1")
        rc, out = audit(repo, wave_merges=True)
        assert rc == 1 and "held: held/INTENT-x.md" in out, (rc, out)
        repo, _ = scenario("T9a", {"mem/rule.md": "---\nupdated: 2026-01-01\n---\nnew body\n"},
                           merge_subject="wave0(T9a): merge intent/T9a")
        rc, out = audit(repo, wave_merges=True)
        assert rc == 1 and "held: mem/rule.md (body changed)" in out, (rc, out)
        repo, _ = scenario("T9a", {"mem/rule.md": "---\nupdated: 2026-02-02\n---\nbody\n"},
                           merge_subject="wave0(T9a): merge intent/T9a")
        rc, out = audit(repo, wave_merges=True)
        assert rc == 0, (rc, out)
        # 5. JSON selectors: inside passes; outside fails.
        inside = json.dumps({"rows": [{"id": "a", "cov": {"A1": "CHANGED", "B2": "y"}}],
                             "outputs": ["o"], "other": 1}, indent=2) + "\n"
        repo, _ = scenario("T1", {"data/table.json": inside}, merge_subject="wave0(T9a): merge intent/T1")
        rc, out = audit(repo, wave_merges=True)
        assert rc == 0, (rc, out)
        outside = json.dumps({"rows": [{"id": "a", "cov": {"A1": "x", "B2": "CHANGED"}}],
                              "outputs": [], "other": 2}, indent=2) + "\n"
        repo, _ = scenario("T1", {"data/table.json": outside}, merge_subject="wave0(T9a): merge intent/T1")
        rc, out = audit(repo, wave_merges=True)
        assert rc == 1 and "json-selector: data/table.json" in out and "rows.a.cov.B2" in out, (rc, out)
        # 6. Non-JSON section selector → NOTE only.
        repo, _ = scenario("T2", {"notes/beta.md": "# beta 2\n"}, merge_subject="wave0(T9a): merge intent/T2")
        rc, out = audit(repo, wave_merges=True)
        assert rc == 0 and "NOTE section-selector: notes/beta.md" in out, (rc, out)

        # 7. Unreverted session auto-commit on the second parent fails; reverted passes.
        def add_auto(h, name, tip):
            return h.commit(f"intent/{name}", "session: auto-commit", {"tools/alpha.py": "auto\n"}, frm=tip)

        repo, _ = scenario("T1", {"tools/alpha.py": "a\n"}, extra=add_auto,
                           merge_subject="wave0(T9a): merge intent/T1")
        rc, out = audit(repo, wave_merges=True)
        assert rc == 1 and "auto-commit:" in out, (rc, out)
        repo, _ = scenario("T1", {"tools/alpha.py": "a\n"}, extra=add_auto)
        rc, out = audit(repo, task="T1", rev="main..intent/T1")
        assert rc == 1 and "auto-commit:" in out, (rc, out)

        repo, env = _new_repo(td, "revert")
        h = _History(repo, env)
        b0 = h.commit("main", "base", base_files)
        s = h.commit("intent/T1", "wave0(T1): start", frm=b0)
        auto = h.commit("intent/T1", "session: auto-commit", {"tools/alpha.py": "auto\n"}, frm=s)
        h.flush()
        auto_sha = h.sha(auto)
        rv = h.commit("intent/T1", 'Revert "session: auto-commit"\n\nThis reverts commit ' + auto_sha + ".\n",
                      {"tools/alpha.py": "a\n"}, frm=auto)
        h.commit("main", "wave0(T9a): merge intent/T1",
                 {"tools/test-validators.py": "# i\n", "tools/alpha.py": "a\n"}, frm=b0, merge=rv)
        h.flush()
        rc, out = audit(repo, wave_merges=True)
        assert rc == 0, (rc, out)

        # 8. A fix-round commit is audited against its owner's writes.
        repo, env = _new_repo(td, "fix")
        h = _History(repo, env)
        b0 = h.commit("main", "base", base_files)
        f1 = h.commit("main", "wave0(T3): F-01 (T1) fix alpha", {"tools/alpha.py": "fixed\n"}, frm=b0)
        h.commit("main", "wave0(T3): F-02 (T1) stray edit", {"tools/beta.py": "stray\n"}, frm=f1)
        h.flush()
        rc, out = audit(repo, wave_merges=True)
        assert rc == 1 and out.count("AUDIT") == 2 and "outside-writes: tools/beta.py" in out, (rc, out)
        # 9. Unknown task → usage (2).
        rc, out = audit(repo, task="TX", rev="main..main")
        assert rc == 2, (rc, out)
        # 10. A direct first-parent wave commit (no merge, no fix subject) is listed, never silent.
        repo, env = _new_repo(td, "direct")
        h = _History(repo, env)
        b0 = h.commit("main", "base", base_files)
        h.commit("main", "wave0(T0): table rows", {"tools/alpha.py": "direct\n"}, frm=b0)
        h.flush()
        rc, out = audit(repo, wave_merges=True)
        assert "NOTE unaudited direct commit" in out and "wave0(T0): table rows" in out, (rc, out)


SELF_TESTS = (
    ("no-git-write invariant", _st_invariant),
    ("parser cases", _st_parser),
    ("synthetic spec", _st_fixture_spec),
    ("held-spec parity", _st_held_parity),
    ("verify hardening", _st_verify),
    ("scope-audit", _st_scope_audit),
)


_SKIPPED: list = []


def self_test() -> int:
    only = os.environ.get("INTENT_RUN_SELFTEST_ONLY")
    del _SKIPPED[:]
    failed = 0
    saved = dict(os.environ)
    home = tempfile.mkdtemp(prefix="intent-run-home-")
    os.environ.update({"HOME": home, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull})
    try:
        failed = _run_self_tests(only)
    finally:
        os.environ.clear()
        os.environ.update(saved)
        shutil.rmtree(home, ignore_errors=True)
    ran = 1 if only == "invariant" else len(SELF_TESTS)
    print(f"self-test: {ran - failed - len(_SKIPPED)} ok, {len(_SKIPPED)} skipped, {failed} failed")
    return 1 if failed else 0


def _run_self_tests(only: str | None) -> int:
    global _MEASURE_STDIO
    _MEASURE_STDIO = subprocess.DEVNULL
    failed = 0
    for name, fn in SELF_TESTS:
        if only == "invariant" and fn is not _st_invariant:
            continue
        try:
            note = fn()
            print(f"ok   {name}" + (f" — {note}" if note else ""))
        except _Skip as sk:
            _SKIPPED.append(name)
            print(f"SKIP {name} — {sk}")
        except Exception as exc:  # report every failing case, then exit 1
            failed += 1
            msg = str(exc).replace("\n", " ")[:600]
            print(f"FAIL {name}: {type(exc).__name__}: {msg}")
    return failed


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv == ["--self-test"]:
        return self_test()
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
    p_ver.add_argument("--root", help="checkout used as measure cwd and for git ls-files exposure")
    p_sa = sub.add_parser("scope-audit")
    p_sa.add_argument("--spec", required=True)
    p_sa.add_argument("--task")
    p_sa.add_argument("--rev", help="A..B range for --task")
    p_sa.add_argument("--wave-merges", action="store_true")
    p_sa.add_argument("--ref", default="main", help="branch whose first-parent merges are audited")
    p_sa.add_argument("--root", help="checkout to audit (default: git toplevel of the cwd)")
    p_sa.add_argument("--json", action="store_true")
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
    if args.cmd == "scope-audit":
        if bool(args.task) == bool(args.wave_merges):
            print("scope-audit: pass exactly one of --task ID --rev A..B or --wave-merges", file=sys.stderr)
            return 2
        spec_p = Path(args.spec).expanduser().resolve()
        if not spec_p.is_file() and not Path(args.spec).expanduser().is_absolute():
            alt = _main_checkout_path(Path(args.spec))
            if alt is not None:
                spec_p = alt
        if not spec_p.is_file():
            print(f"spec not found: {spec_p}", file=sys.stderr)
            return 2
        return cmd_scope_audit(spec_p, task=args.task, rev=args.rev, wave_merges=args.wave_merges,
                               ref=args.ref, root=args.root, as_json=args.json)
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
        return cmd_verify(spec, args.run, args.root)
    return 2


if __name__ == "__main__":
    sys.exit(main())
