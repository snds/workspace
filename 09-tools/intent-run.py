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

H4/H5: PROJECT.md project intent (init --frame, a --neutral render pre-scanned by
check-secrets' workspace-leak class, inheritance by remote slug within one owner
class), lifecycle-scaled lint with git provenance on approvals, human-only approve,
next, and verify --record stamped with surface, family, via and device.

H8: the remediation loop. init --recon writes a read-only recon card (content-read
policy first: a Claude chain on a non-personal repo is routed; employer recon goes to
stdout), a findings register with closures and a preserve list, vendor-neutral
self-contained packets, and a mission-fit verdict keyed to a branch or range.

H9: write scope as task data. `writes` / `forbids` / `enforce` task-graph cells, a disjoint-wave lint
(gate refuses two parallel implementors with overlapping writes, or a verifier that writes), `scope
--branch|--range` (read-only diff vs the declared scope), and `scope --check-path` for the report-only
pre-write accelerators. The kernel and the active-task pointer live in the sibling intent_scope.py.

Usage:
  python3 09-tools/intent-run.py doctor
  python3 09-tools/intent-run.py daemon [status|workspace.list]
  python3 09-tools/intent-run.py init [--path PATH]
  python3 09-tools/intent-run.py init --frame --repo DIR [--neutral] [--stdout] [--inherits SLUG]
                                 [--inherits-context SLUG#AGENTS.md[,vault:ID]] [--lifecycle L]
  python3 09-tools/intent-run.py init --recon [--repo DIR] [--spec PATH] [--stdout]
  python3 09-tools/intent-run.py lint (--repo DIR | --spec PATH [--since REF] [--run-closures] | --all)
  python3 09-tools/intent-run.py next [--repo DIR | --spec PATH]
  python3 09-tools/intent-run.py findings [--spec PATH] [--status OPEN|RESOLVED|DEFERRED] [--json]
  python3 09-tools/intent-run.py packet --format prompt|json (T<n> | F-NNN) [--spec PATH]
  python3 09-tools/intent-run.py verdict [--spec PATH] [--branch B [--base REF] | --range A..B] [--run] [--json]
  python3 09-tools/intent-run.py approve (--repo DIR | --spec PATH) --by NAME [--note TEXT]
  python3 09-tools/intent-run.py status [--spec PATH]
  python3 09-tools/intent-run.py gate [--spec PATH]
  python3 09-tools/intent-run.py ready [--spec PATH]
  python3 09-tools/intent-run.py worktree add TASK_ID [--spec PATH] [--repo DIR]
  python3 09-tools/intent-run.py verify [--spec PATH] [--run] [--root DIR] [--record]
  python3 09-tools/intent-run.py scope-audit --spec PATH (--task ID --rev A..B | --wave-merges)
                                 [--ref REF] [--root DIR] [--json]
  python3 09-tools/intent-run.py scope (--branch B [--base REF] | --range A..B) [--spec PATH] [--task ID]
                                 [--repo DIR] [--json]
  python3 09-tools/intent-run.py scope --check-path PATH [--cwd DIR] [--json]
  python3 09-tools/intent-run.py scope (--set TASK [--spec PATH] | --clear | --show) [--repo DIR]
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
from pathlib import Path

_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)
import intent_scope  # noqa: E402 - the H9 kernel, a sibling shared with the pinned hook lib
from intent_scope import (  # noqa: E402
    _expand_braces,
    _glob_re,
    _is_glob,
    _parse_table,
    _section,
    _split_depth0,
    parse_write_token,
)

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
    out += intent_scope.lint_scope(spec.get("tasks") or [])  # H9: disjoint waves, read-only verifiers
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
    wts = load_state(spec_path).get("worktrees") or {}
    print("tasks:")
    for t in spec["tasks"]:
        st = task_status(t, meta, by_id)
        sc = task_scope_state(spec_path, t.get("id") or "", wts)
        if st == "verified" and sc == "fail":
            st = "scope-fail"  # a task never shows verified while its branch is out of scope (H9)
        print(
            f"  {t.get('id','?'):4} {st:9} {(t.get('role') or ''):12} "
            f"deps={t.get('depends_on') or '—'} isol={t.get('isolation') or ''} scope={sc}"
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


def task_scope_state(spec_path: Path, task_id: str, worktrees: dict) -> str:
    """pass | fail | unchecked for a task's recorded branch against its declared scope (read-only)."""
    info = worktrees.get(task_id) if task_id else None
    top = _toplevel(spec_path)
    if not info or not info.get("branch") or top is None:
        return "unchecked"
    try:
        base_ref = "main" if _rev(top, "main") else "HEAD"
        mb = _git(["merge-base", base_ref, info["branch"]], top)
        d = _git(["diff", "--name-only", "--no-renames", mb.stdout.strip(), info["branch"]], top)
        if mb.returncode != 0 or d.returncode != 0:
            return "unchecked"
        sc = intent_scope.spec_scope(spec_path.read_text(encoding="utf-8"), task_id)
        paths = [p for p in d.stdout.splitlines() if p.strip()]
        return "fail" if any(intent_scope.evaluate(sc, p) for p in paths) else "pass"
    except (KeyError, OSError):
        return "unchecked"


def contract_missing(spec_path: Path, meta: dict) -> tuple[list[str], list[str]]:
    """(declared contract paths, those not committed at HEAD or with uncommitted changes)."""
    declared = [t.strip().strip("`") for t in _split_depth0(meta.get("contract") or "")
                if t.strip() and t.strip().lower() not in BLANK_CELLS]
    top = _toplevel(spec_path)
    missing = []
    for p in declared:
        if top is None or _git(["cat-file", "-e", f"HEAD:{p}"], top).returncode != 0 \
                or _git(["diff", "--quiet", "HEAD", "--", p], top).returncode != 0:
            missing.append(p)
    return declared, missing


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
    scope_errors = [m for lv, m in intent_scope.lint_scope(spec["tasks"]) if lv == "ERROR"]
    if scope_errors:
        print("BLOCKED — write scopes are not disjoint (H9); fix the task graph first", file=sys.stderr)
        return 1
    for level, msg in lint_provenance(spec_path, spec["meta"], 2):
        if level == "ERROR":
            print(msg, file=sys.stderr)
            return 1
        print(f"LINT {level} — {msg}", file=sys.stderr)
    for ref, hit in blocked_by_paths(spec, spec_path):
        if hit is None:
            print(f"BLOCKED — blocked_by {ref!r} does not resolve", file=sys.stderr)
            return 1
        up = parse_spec(hit.read_text(encoding="utf-8"))
        v = compute_verdict(up, closures=closure_results(up, run=False, runnable=False))
        if v["verdict"] in ("Unfit", "Blocked"):
            print(f"BLOCKED — upstream {ref} is {v['verdict']}: {'; '.join(v['reasons'][:3])}", file=sys.stderr)
            return 1
    print("ok — spec approved; implementor waves may start")
    return 0


def cmd_ready(spec_path: Path) -> int:
    spec = load_spec(spec_path)
    if cmd_gate(spec_path) != 0:
        return 1
    ready = []
    for t in ready_implementors(spec):
        tripped, n, since = loop_breaker(spec_path, spec, t.get("id") or "")
        if tripped:
            print(f"HELD (loop-breaker): {t.get('id')} has {n} FAIL verify records since "
                  f"{since or 'the start'}; add a Previous attempts entry to its packet first")
            continue
        ready.append(t)
    if len(ready) > 1:
        declared, missing = contract_missing(spec_path, spec["meta"])
        if not declared or missing:
            why = f"uncommitted: {', '.join(missing)}" if declared else "the spec declares no `contract:` paths"
            for t in ready[1:]:
                print(f"HELD (contract): {t.get('id')} — parallel fan-out needs every contract path committed "
                      f"at HEAD ({why})")
            ready = ready[:1]
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
    tripped, n, since = loop_breaker(spec_path, spec, task_id)
    if tripped:
        print(f"REFUSED (loop-breaker) — {task_id} has {n} FAIL verify records since {since or 'the start'}; "
              "record what changed under the packet's Previous attempts first", file=sys.stderr)
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
    try:
        ptr = intent_scope.write_pointer(dest, spec_path, task_id)
        print(f"active task: {task_id} (pointer {ptr})")
    except Exception as exc:  # noqa: BLE001 - the pointer only feeds report-only accelerators
        print(f"active task not set ({type(exc).__name__}); run `scope --set {task_id}` in the worktree")
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
    record: bool = False,
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
    results: list[tuple[int, str, str]] = []
    for idx, c in enumerate(spec["checks"], 1):
        status, reason, argv = classify_check(c, automated=automated, tracked=tracked)
        label = c["label"]
        if status == "SKIP":
            say(f"SKIP ({reason}): {label}")
            counts["SKIP"] += 1
            results.append((idx, label, "SKIP"))
            continue
        if status in ("HUMAN", "HUMAN-ATTESTED"):
            say(f"{status}: {label}")
            counts[status] += 1
            results.append((idx, label, status))
            continue
        if status == "BAD":
            say(f"FAIL ({reason}): {label}")
            counts["FAIL"] += 1
            results.append((idx, label, "FAIL"))
            continue
        if status == "NOT_EXPOSED":
            say(f"NOT_EXPOSED ({reason}): {label}")
            counts["NOT_EXPOSED"] += 1
            results.append((idx, label, "NOT_EXPOSED"))
            continue
        say(f"{'RUN' if run else 'CMD'} {c['measure']}")
        if not run:
            results.append((idx, label, "CMD"))
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
            results.append((idx, label, "FAIL"))
        else:
            say(f"PASS {label}")
            counts["PASS"] += 1
            results.append((idx, label, "PASS"))
    human_total = counts["HUMAN"] + counts["HUMAN-ATTESTED"]
    say(
        f"summary: pass={counts['PASS']} fail={counts['FAIL']} skip={counts['SKIP']} "
        f"not_exposed={counts['NOT_EXPOSED']} human={human_total} "
        f"(attested {counts['HUMAN-ATTESTED']})"
    )
    if record:
        verify_record(spec_path, results, dict(counts), run)
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


# ---------------------------------------------------------------------------
# H9 — scope: the diff (or one path) against the task's declared writes / forbids
# ---------------------------------------------------------------------------


def _scope_home() -> Path | None:
    return Path(_PR_KW["home"]) if _PR_KW.get("home") else None


def cmd_scope_check_path(path: str, *, cwd: str | None = None, as_json: bool = False) -> int:
    """The pre-write accelerator's CLI form. Fails open (exit 0) on every error; exit 1 only for a
    finding on a task whose `enforce` cell is true."""
    res = intent_scope.check_path(path, cwd=cwd, home=_scope_home())
    if as_json:
        print(json.dumps(res, ensure_ascii=False))
    elif res["status"] == "outside":
        print(intent_scope.message(res))
    return 1 if res["block"] else 0


def _scope_top(repo: str | None) -> Path | None:
    return intent_scope.find_top(Path(repo).expanduser() if repo else Path.cwd())


def cmd_scope_pointer(action: str, *, task: str | None = None, spec: str | None = None,
                      repo: str | None = None, as_json: bool = False) -> int:
    top = _scope_top(repo)
    if top is None:
        print("scope: not inside a git checkout (pass --repo DIR)", file=sys.stderr)
        return 2
    home = _scope_home()
    where = intent_scope.pointer_path(top, home=home)
    if action == "clear":
        gone = intent_scope.clear_pointer(top, home=home)
        print(f"active task cleared ({where})" if gone else f"no active task ({where})")
        return 0
    if action == "show":
        ptr = intent_scope.read_pointer(top, home=home)
        if as_json:
            print(json.dumps({"pointer": str(where), "active": ptr}))
        else:
            print(f"active task: {ptr['task']} · spec {ptr['spec']} · set {ptr.get('set_at')}" if ptr
                  else "no active task")
            print(f"pointer: {where}")
        return 0
    why = _content_gate(top, _detection())
    if why:
        print(f"REFUSED — {why}", file=sys.stderr)
        return 4
    sp = find_spec(spec)
    try:
        sc = intent_scope.spec_scope(sp.read_text(encoding="utf-8"), task or "")
        dest = intent_scope.write_pointer(top, sp, sc["task"], home=home)
    except KeyError as exc:
        print(f"scope: {exc.args[0]}", file=sys.stderr)
        return 2
    except PermissionError as exc:
        print(f"scope: {exc}", file=sys.stderr)
        return 4
    print(f"active task: {sc['task']} ({'enforce' if sc['enforce'] else 'report-only'})")
    print(f"pointer: {dest}")
    for p in sc["prose_writes"]:
        print(f"  NOTE writes token is prose, not a path: {p}")
    return 0


def cmd_scope_diff(*, spec: str | None, task: str | None, branch: str | None, base: str | None,
                   rng: str | None, repo: str | None, as_json: bool = False) -> int:
    """Read-only: every path the branch (since its merge-base) or range changed, against the task's
    writes and forbids. Exit 0 clean, 1 findings, 2 usage or git error, 3 nothing changed,
    4 refused (content-read policy)."""
    def fail(msg: str, rc: int = 2) -> int:
        if as_json:
            print(json.dumps({"schema_version": 1, "cmd": "scope", "error": msg, "exit": rc}))
        else:
            print(f"scope: {msg}", file=sys.stderr)
        return rc

    top = _toplevel(Path(repo).expanduser().resolve() if repo else Path.cwd())
    if top is None:
        return fail("not inside a git checkout (pass --repo DIR)")
    why = _content_gate(top, _detection())
    if why:
        return fail(f"REFUSED — {why}", 4)
    ptr = intent_scope.read_pointer(top, home=_scope_home())
    if not task and branch:
        m = re.fullmatch(r"(?:refs/heads/)?intent/(\S+)", branch)
        task = m.group(1) if m else None
    task = task or (ptr or {}).get("task")
    if not task:
        return fail("no task: pass --task ID, use an intent/<ID> branch, or set the active task")
    sp = Path(spec).expanduser().resolve() if spec else (Path(ptr["spec"]) if ptr else find_spec(None))
    if branch:
        base_ref = base or ("main" if _rev(top, "main") else "HEAD")
        mb = _git(["merge-base", base_ref, branch], top)
        if mb.returncode != 0:
            return fail(f"no merge-base between {base_ref} and {branch}")
        start, tip_ref, key = mb.stdout.strip(), branch, f"branch {branch} (since merge-base with {base_ref})"
    else:
        if not rng or ".." not in rng:
            return fail("--range is A..B")
        a, tip_ref = rng.split("..", 1)
        a, tip_ref = a or "HEAD", tip_ref or "HEAD"
        mb = _git(["merge-base", a, tip_ref], top)
        start, key = (mb.stdout.strip() if mb.returncode == 0 else a), f"range {rng}"
    tip = _rev(top, tip_ref)
    if tip is None or _rev(top, start) is None:
        return fail(f"{tip_ref if tip is None else start} does not resolve here (fetch it first)")
    d = _git(["diff", "--name-only", "--no-renames", start, tip], top, timeout=60)
    if d.returncode != 0:
        return fail(f"git diff failed: {d.stderr.strip()[:200]}")
    paths = [p for p in d.stdout.splitlines() if p.strip()]
    try:
        rel = sp.resolve().relative_to(top).as_posix()
    except ValueError:
        rel = None
    text = (_git_text_at(top, tip, rel) if rel else None)
    source = f"{rel} @ {tip[:9]}" if text is not None else str(sp)
    if text is None:
        if not sp.is_file():
            return fail(f"spec not found: {sp}")
        text = sp.read_text(encoding="utf-8")
    try:
        sc = intent_scope.spec_scope(text, task)
    except KeyError as exc:
        return fail(str(exc.args[0]))
    findings = [f for p in paths for f in intent_scope.evaluate(sc, p)]
    notes = []
    if not sc["checkable"]:
        notes.append("writes cell is prose or absent: only forbids are checked"
                     + (f" ({'; '.join(sc['prose_writes'])})" if sc["prose_writes"] else ""))
    sels = sorted({e["path"] for e in sc["writes"] if e["selectors"]})
    if sels:
        notes.append(f"selector writes are checked at file level here ({', '.join(sels)}); "
                     "scope-audit checks JSON selectors")
    rc = 3 if not paths else (1 if findings else 0)
    if as_json:
        print(json.dumps({"schema_version": 1, "cmd": "scope", "task": sc["task"], "key": key, "tip": tip,
                          "spec": source, "paths": len(paths), "findings": findings, "notes": notes,
                          "enforce": sc["enforce"], "exit": rc}, indent=2, ensure_ascii=False))
        return rc
    print(f"scope: task {sc['task']} · {key} @ {tip[:9]} · {len(paths)} path(s) · spec {source}")
    labels = {"forbidden": ("FORBIDDEN", "forbids {}"), "preserve": ("PRESERVE", "preserve list {}"),
              "sensitive": ("SENSITIVE", "denylist {}, not owned by an explicit writes entry"),
              "outside-writes": ("OUTSIDE", "not in writes")}
    for f in findings:
        tag, what = labels.get(f["kind"], (f["kind"].upper(), "{}"))
        print(f"  {tag} {f['path']} ({what.format(f.get('rule'))})")
    for n in notes:
        print(f"  NOTE {n}")
    print("scope: nothing changed" if rc == 3 else f"scope: {len(findings)} finding(s)")
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
    import urllib.request  # noqa: PLC0415 - lazy: keeps `scope --check-path` start-up small
    import zipfile  # noqa: PLC0415
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
# H4 — project intent (PROJECT.md) · H5 — lint / approve / next / verify --record
# ---------------------------------------------------------------------------

PROJECT_FILE = "PROJECT.md"
PROJECT_TEMPLATE = ROOT / "00-bootstrap" / "templates" / "project-intent.md"
POINTER_LINE = "Project intent: PROJECT.md (problem, audience, knowns/unknowns, scope)."
POINTER_RE = re.compile(r"(?im)^\W*Project intent:\W*PROJECT\.md\b")
README_POINTER_RE = re.compile(r"(?im)^\W*Project intent:\**\s*`?(?P<target>[^`\s]+)`?(?P<rest>.*)$")
LIFECYCLES = ("discover", "define", "build", "operate")
PROJECT_KEYS = ("profile", "lifecycle", "inherits", "inherits_context", "approval")
PROJECT_INTENT_SECTIONS = ("Problem & audience", "Knowns & unknowns", "Out of scope & later")
CLAIM_LABELS = ("known", "inferred", "assumed", "unknown", "conflicted")
KNOWNS_COLUMNS = ("claim", "label", "tier", "evidence", "decision_rule")
TIER_RE = re.compile(r"^T[1-5]$", re.IGNORECASE)
HUMAN_MARK_RE = re.compile(r"\[HUMAN:[^\]]*\]")
NA_RE = re.compile(r"^n/a\b", re.IGNORECASE)
NA_REASON_RE = re.compile(r"^n/a\s*\((.+)\)\s*\.?$", re.IGNORECASE)
INHERITS_RE = re.compile(
    r"^(?P<slug>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)(?:#(?P<path>[^@\s,]+))?(?:@(?P<ref>[^\s,]+))?$"
)
INTENT_MAX_LINES = 40
INHERIT_MAX_DEPTH = 3
WS_ONLY_MARK = "<!-- ws-only -->"
CHILD_SENTENCE = "Intent and context are defined by the parent repository named in `inherits`."
CONDUCT_FALLBACK = ("personal-solo",)  # the table is authoritative; unknown profiles rank strictest
# Agent evidence in the commit that introduced an approval (H5 provenance).
AGENT_EVIDENCE = (
    ("claude", re.compile(r"(?im)^co-authored-by:[^\n]*\b(claude|anthropic)\b|noreply@anthropic\.com"
                          r"|generated with \[?claude")),
    ("cursor", re.compile(r"(?im)^co-authored-by:[^\n]*\bcursor\b|cursoragent@cursor\.com")),
    ("workspace-agent", re.compile(r"(?im)^workspace-agent:[ \t]*(?!none\b|human\b)\S+")),
    ("other-agent", re.compile(r"(?im)^co-authored-by:[^\n]*\b(codex|openai|copilot|gemini|devin|jules)\b")),
)
AUTO_COMMIT_SUBJECT = "session: auto-commit"

# Resolver context: tests point these at a fixture root, temp HOME and hostname.
_PR_KW: dict = {"root": None, "home": None, "hostname": None}
_DETECTION_OVERRIDE: dict | None = None
_HUMAN_OVERRIDE: bool | None = None
_READS: list | None = None  # self-test spy: parent reads (path, source)


def _pr():
    return _import_profile_resolve()


def _detection() -> dict:
    if _DETECTION_OVERRIDE is not None:
        return dict(_DETECTION_OVERRIDE)
    try:
        return _pr().detect_surface(root=_PR_KW.get("root"))
    except Exception:  # fail closed: an undetermined chain is walled like an agent
        return {"acting_host": "unknown", "family": "unknown-agent", "family_for_walls": "unknown-agent",
                "via": "none", "agent_possible": True}


def _restricted(det: dict) -> bool:
    """A Claude chain (or an undetermined agent) never reads or writes non-personal repos."""
    return det.get("family_for_walls") in ("claude", "unknown-agent")


def _resolve_repo(target) -> dict:
    return _pr().repo_resolve(str(target), root=_PR_KW.get("root"), home=_PR_KW.get("home"),
                              detection=_detection())


def _policy(repo, action_class: str, det: dict) -> dict:
    return _pr().policy(repo=str(repo), action_class=action_class, root=_PR_KW.get("root"),
                        home=_PR_KW.get("home"), hostname=_PR_KW.get("hostname"), detection=det)


def _where(slug: str, det: dict) -> dict:
    # A non-Claude miss rescans live; profile_resolve itself refuses the scan under an agent chain.
    return _pr().where(slug, root=_PR_KW.get("root"), home=_PR_KW.get("home"), rescan=not _restricted(det),
                       detection=det, hostname=_PR_KW.get("hostname"))


def _conduct() -> list[str]:
    try:
        t = _pr().load_table("context-remotes", root=_PR_KW.get("root"))
        order = list(t.get("conduct_order") or [])
        return order or list(CONDUCT_FALLBACK)
    except Exception:
        return list(CONDUCT_FALLBACK)


def _conduct_rank(profile: str | None, conduct: list[str]) -> int:
    """Total order over profiles; anything unknown ranks most restrictive."""
    return conduct.index(profile) if profile in conduct else len(conduct)


def _origin_slug(res: dict) -> str | None:
    rems = res.get("remotes") or []
    for r in rems:
        if r.get("name") == "origin" and r.get("slug"):
            return r["slug"]
    for r in rems:
        if r.get("slug"):
            return r["slug"]
    return None


def _subsection(text: str, heading: str) -> str:
    pat = re.compile(rf"^###\s+{re.escape(heading)}\s*$", re.IGNORECASE | re.M)
    m = pat.search(text)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"^#{2,3}\s+\S", text[start:], re.M)
    return text[start : start + nxt.start()] if nxt else text[start:]


def parse_intent(text: str) -> dict:
    """PROJECT.md or a README `## Project intent` block: frontmatter + the block."""
    meta, body, comments = _split_frontmatter_ex(text)
    has_block = bool(re.search(r"^##\s+Project intent\s*$", body, re.IGNORECASE | re.M))
    block = _section(body, "Project intent") if has_block else ""
    lines = block.strip("\n").splitlines()
    subs = {name: _subsection(block, name) for name in PROJECT_INTENT_SECTIONS}
    present = {name: bool(re.search(rf"^###\s+{re.escape(name)}\s*$", block, re.IGNORECASE | re.M))
               for name in PROJECT_INTENT_SECTIONS}
    knowns = _parse_table(subs["Knowns & unknowns"])
    return {"meta": meta, "meta_comments": comments, "body": body, "has_block": has_block, "block": block,
            "block_lines": len(lines), "sections": subs, "present": present, "knowns": knowns}


def lint_intent(doc: dict, *, kind: str = "project") -> list[tuple[str, str]]:
    """Text-only lint of one intent home, scaled by lifecycle (discover warns; define and later error)."""
    out: list[tuple[str, str]] = []
    meta = doc["meta"]
    life = (meta.get("lifecycle") or "").strip().lower()
    if life not in LIFECYCLES:
        out.append(("ERROR", f"lifecycle {life or '(missing)'!r} is not one of {'|'.join(LIFECYCLES)}"))
        stage = len(LIFECYCLES)
    else:
        stage = LIFECYCLES.index(life)
    strict = "ERROR" if stage >= 1 else "WARN"
    if kind == "project":
        for key in meta:
            if key not in PROJECT_KEYS:
                out.append(("WARN", f"frontmatter key {key!r} is not in the PROJECT.md grammar"))
    inherits = (meta.get("inherits") or "").strip()
    if inherits and not INHERITS_RE.match(inherits):
        out.append(("ERROR", f"inherits {inherits!r} is not <owner>/<repo>[#path][@ref]"))
    if not doc["has_block"]:
        if not inherits:
            out.append(("ERROR", "no `## Project intent` block (and no `inherits:`)"))
        return out + _lint_approval(meta, doc.get("meta_comments"), stage)
    if doc["block_lines"] > INTENT_MAX_LINES:
        out.append(("ERROR", f"`## Project intent` is {doc['block_lines']} lines (max {INTENT_MAX_LINES})"))
    if inherits and not any(doc["present"].values()):
        return out + _lint_approval(meta, doc.get("meta_comments"), stage)
    for name in PROJECT_INTENT_SECTIONS:
        if not doc["present"][name]:
            out.append((strict, f"missing `### {name}`"))
            continue
        content = [ln.strip() for ln in doc["sections"][name].splitlines() if ln.strip()]
        if not content:
            out.append((strict, f"`### {name}` is empty (write it, or `n/a (reason)`)"))
        elif len(content) == 1 and NA_RE.match(content[0]) and not NA_REASON_RE.match(content[0]):
            out.append(("ERROR", f"`### {name}`: `n/a` needs a reason: `n/a (reason)`"))
    marks = len(HUMAN_MARK_RE.findall(doc["block"]))
    if marks:
        out.append((strict, f"{marks} unresolved [HUMAN: …] marker(s)"))
    if doc["present"]["Knowns & unknowns"]:
        sec = doc["sections"]["Knowns & unknowns"]
        if NA_REASON_RE.match(sec.strip()):
            pass
        elif not doc["knowns"]:
            out.append((strict, "Knowns & unknowns has no claim | label | tier | evidence | decision rule table"))
        else:
            cols = set(doc["knowns"][0])
            missing = [c for c in KNOWNS_COLUMNS if c not in cols]
            if missing:
                out.append(("ERROR", f"knowns table lacks column(s): {', '.join(missing)}"))
            for i, row in enumerate(doc["knowns"], 1):
                label = (row.get("label") or "").strip().lower()
                tier = (row.get("tier") or "").strip()
                if label not in CLAIM_LABELS and not HUMAN_MARK_RE.search(label):
                    out.append(("ERROR", f"knowns row {i}: label {label!r} is not one of {'|'.join(CLAIM_LABELS)}"))
                if not TIER_RE.match(tier) and not NA_RE.match(tier) and not HUMAN_MARK_RE.search(tier):
                    out.append(("ERROR", f"knowns row {i}: tier {tier!r} is not T1..T5"))
                rule = (row.get("decision_rule") or "").strip()
                if label != "known" and (not rule or rule in ("-", "—")):
                    out.append((strict, f"knowns row {i}: a {label or 'claim'} needs a decision rule written "
                                        "before the evidence"))
    return out + _lint_approval(meta, doc.get("meta_comments"), stage)


def _lint_approval(meta: dict, comments: dict | None, stage: int) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    if not (meta.get("approval") or "").strip():
        if stage >= 2 and stage < len(LIFECYCLES):
            out.append(("ERROR", f"lifecycle {LIFECYCLES[stage]} needs an approval (intent-run approve)"))
        return out
    det = approval_detail(meta, comments)
    out += [("ERROR", e) for e in det["errors"]] + [("WARN", w) for w in det["warnings"]]
    if stage >= 2 and stage < len(LIFECYCLES) and not det["ok"]:
        out.append(("ERROR", f"lifecycle {LIFECYCLES[stage]} needs an approval, not {det['value']!r}"))
    return out


def has_trailer_lane(top: Path) -> bool:
    """True when a commit-msg lane (the H18 `ws-lane-*` hook) is configured for this repo."""
    r = _git(["config", "--get-regexp", r"^hook\..*\.event$"], top)
    if r.returncode != 0:
        return False
    for line in r.stdout.splitlines():
        key, _, val = line.partition(" ")
        if val.strip() == "commit-msg" and key.lower().startswith("hook.ws-lane"):
            return True
    return False


def approval_provenance(path: Path, value: str) -> dict:
    """Find the commit that introduced the approval (git log -S) and read its agent evidence.

    status: agent | ok | unknown (no trailer lane) | uncommitted | no-git
    """
    top = _toplevel(path)
    if top is None:
        return {"status": "no-git", "sha": None, "evidence": None}
    try:
        rel = path.resolve().relative_to(top).as_posix()
    except ValueError:
        return {"status": "no-git", "sha": None, "evidence": None}
    hit = None
    for needle in (f"approval: {value}", "approval:"):
        r = _git(["log", f"-S{needle}", "--format=%H%x1f%s%x1f%B%x1e", "--", rel], top)
        recs = [x for x in r.stdout.split("\x1e") if x.strip()] if r.returncode == 0 else []
        if recs:
            hit = recs[0].strip("\n").split("\x1f")
            break
    if hit is None:
        return {"status": "uncommitted", "sha": None, "evidence": None}
    sha, subject, body = (hit + ["", "", ""])[:3]
    for name, rx in AGENT_EVIDENCE:
        if rx.search(body):
            return {"status": "agent", "sha": sha, "evidence": f"{name} trailer"}
    if subject.strip().startswith(AUTO_COMMIT_SUBJECT):
        return {"status": "agent", "sha": sha, "evidence": "recorded agent chain (session auto-commit)"}
    if not has_trailer_lane(top):
        return {"status": "unknown", "sha": sha, "evidence": None}
    return {"status": "ok", "sha": sha, "evidence": None}


def lint_provenance(path: Path, meta: dict, stage: int) -> list[tuple[str, str]]:
    det = approval_detail(meta)
    if det["kind"] not in ("approved", "waived"):
        return []
    prov = approval_provenance(path, det["value"])
    st = prov["status"]
    sha = (prov["sha"] or "")[:9]
    if st == "agent":
        lvl = "ERROR" if stage >= 1 else "WARN"
        return [(lvl, f"BLOCKED — approval introduced by {sha} carries agent evidence ({prov['evidence']}); "
                      "an approval must be a human commit")]
    if st == "unknown":
        return [("WARN", f"provenance unknown — {sha} has no agent trailer, but this repo runs no trailer lane")]
    if st == "uncommitted":
        return [("WARN", "approval is not committed yet; provenance unknown until a human commit carries it")]
    return []


def resolve_inheritance(child: dict, meta: dict, det: dict, *, depth: int = 1,
                        seen: frozenset = frozenset()) -> list[tuple[str, str]]:
    """Inheritance by remote slug. The order is the wall: classes from the table, conduct, then a read.

    child: {slug, owner_class, profile}. Parent text is held in memory only, never written.
    """
    out: list[tuple[str, str]] = []
    val = (meta.get("inherits") or "").strip()
    ctx = (meta.get("inherits_context") or "").strip()
    if ctx:
        for part in [p.strip() for p in ctx.split(",") if p.strip()]:
            if part.startswith("vault:"):
                pid = part[len("vault:"):].strip()
                if child.get("owner_class") != "personal":
                    out.append(("ERROR", "inherits_context: a vault: pointer is personal-only"))
                elif not pid or not (ROOT / "07-projects" / pid).is_dir():
                    out.append(("ERROR", f"inherits_context vault:{pid} is not a vault project on disk (drift)"))
            elif not INHERITS_RE.match(part):
                out.append(("ERROR", f"inherits_context part {part!r} is not <owner>/<repo>#AGENTS.md"))
            elif not val or INHERITS_RE.match(part).group("slug").casefold() != \
                    (INHERITS_RE.match(val).group("slug").casefold() if INHERITS_RE.match(val) else ""):
                out.append(("WARN", f"inherits_context {part!r} names a different slug than inherits"))
    if not val:
        return out
    m = INHERITS_RE.match(val)
    if not m:
        return out + [("ERROR", f"inherits {val!r} is not <owner>/<repo>[#path][@ref]")]
    slug = m.group("slug").casefold()
    here = frozenset(seen | ({child["slug"]} if child.get("slug") else set()))
    if slug in here:
        return out + [("ERROR", f"inheritance cycle at {slug}")]
    if depth > INHERIT_MAX_DEPTH:
        return out + [("ERROR", f"inheritance deeper than {INHERIT_MAX_DEPTH} at {slug}")]
    try:
        pres = _resolve_repo(slug)  # table only for a slug: no parent read yet
    except Exception as exc:
        return out + [("ERROR", f"resolver unavailable for {slug} ({type(exc).__name__}); fail-closed")]
    c_cls, p_cls = child.get("owner_class"), pres.get("owner_class")
    if c_cls != p_cls or c_cls not in ("personal", "employer"):
        return out + [("ERROR", f"cross-owner inheritance: child is {c_cls}, parent {slug} is {p_cls} "
                                "(only personal→personal or employer→employer; nothing was read)")]
    conduct = _conduct()
    if _conduct_rank(child.get("profile"), conduct) < _conduct_rank(pres.get("profile"), conduct):
        return out + [("ERROR", f"child conduct {child.get('profile')} is looser than parent {slug} "
                                f"({pres.get('profile')})")]
    if c_cls != "personal" and _restricted(det):
        return out + [("WARN", f"parent {slug} is not read from this chain (route: cursor|codex)")]
    w = _where(slug, det)
    if not w.get("paths"):
        return out + [("WARN", f"parent {slug} not on this device ({w.get('status')})")]
    checkout = Path(w["paths"][0])
    relp = m.group("path") or PROJECT_FILE
    rev = m.group("ref") or "origin/HEAD"
    r = _git(["show", f"{rev}:{relp}"], checkout)
    if r.returncode == 0:
        text, src = r.stdout, rev
    elif (checkout / relp).is_file():
        text, src = (checkout / relp).read_text(encoding="utf-8"), "working-tree"
        out.append(("WARN", f"parent {slug}: {rev}:{relp} missing; read the working tree"))
    else:
        return out + [("WARN", f"parent {slug} has no {relp} at {rev} or in its working tree")]
    if _READS is not None:
        _READS.append((str(checkout), src))
    parent = parse_intent(text)
    for lvl, msg in lint_intent(parent):
        if lvl == "ERROR":
            out.append(("WARN", f"parent {slug}: {msg}"))
    out += resolve_inheritance({"slug": slug, "owner_class": p_cls, "profile": pres.get("profile")},
                               parent["meta"], det, depth=depth + 1, seen=here)
    return out


def _profile_drift(meta: dict, res: dict, ss_profile: str | None) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    declared = (meta.get("profile") or "").strip()
    if not declared:
        return out
    conduct = _conduct()
    if declared not in conduct:
        return [("ERROR", f"profile {declared!r} is not a context profile ({'|'.join(conduct)})")]
    if res.get("owner_class") != "personal":
        out.append(("ERROR", "profile: is for personal repos only (the context table is authoritative)"))
    for c in res.get("conflicts") or []:
        if "PROJECT.md profile" in c:
            out.append(("ERROR", f"{c} (drift: profile may only tighten)"))
    if ss_profile and _conduct_rank(declared, conduct) < _conduct_rank(ss_profile, conduct):
        out.append(("ERROR", f"profile {declared} is looser than the SESSION-STATE declaration {ss_profile}"))
    return out


def _session_state_profile(project_dir: Path) -> str | None:
    try:
        text = (project_dir / "SESSION-STATE.md").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    conduct = _conduct()
    for line in text.splitlines():
        if "context profile" in line.casefold():
            for tok in re.findall(r"`([^`]+)`", line):
                if tok in conduct:
                    return tok
    return None


def lint_home(path: Path, *, kind: str, res: dict, det: dict, repo_top: Path | None,
              ss_profile: str | None = None) -> list[tuple[str, str]]:
    """Full lint of one intent home: text, pointers, drift, provenance, employer approvals, inheritance."""
    doc = parse_intent(path.read_text(encoding="utf-8"))
    out = lint_intent(doc, kind=kind)
    meta = doc["meta"]
    life = (meta.get("lifecycle") or "").strip().lower()
    stage = LIFECYCLES.index(life) if life in LIFECYCLES else len(LIFECYCLES)
    if repo_top is not None:
        agents = repo_top / "AGENTS.md"
        if not agents.is_file():
            out.append(("WARN", "no AGENTS.md: add the pointer line so every agent finds PROJECT.md"))
        elif not POINTER_RE.search(agents.read_text(encoding="utf-8", errors="replace")):
            out.append(("ERROR", f"AGENTS.md lacks the pointer line: {POINTER_LINE}"))
        override = repo_top / "AGENTS.override.md"
        if override.is_file() and not POINTER_RE.search(override.read_text(encoding="utf-8", errors="replace")):
            out.append(("ERROR", "AGENTS.override.md lacks the pointer line (Codex reads it instead of AGENTS.md)"))
    out += _profile_drift(meta, res, ss_profile)
    det_a = approval_detail(meta, doc.get("meta_comments"))
    if res.get("owner_class") == "employer" and det_a["kind"] not in ("approved-pr", "pending"):
        out.append(("ERROR", "employer intent accepts only `approved via PR <n>`"))
    elif det_a["kind"] in ("approved", "waived"):
        out += lint_provenance(path, meta, stage)
    child = {"slug": _origin_slug(res), "owner_class": res.get("owner_class"), "profile": res.get("profile")}
    out += resolve_inheritance(child, meta, det)
    return out


def _vault_project_dirs() -> list[tuple[Path, str | None]]:
    """Readable, personal vault projects. Read-denied (employer) folders are skipped silently."""
    base = ROOT / "07-projects"
    out: list[tuple[Path, str | None]] = []
    try:
        kids = sorted(base.iterdir())
    except OSError:
        return out
    conduct = _conduct()
    for d in kids:
        if d.name.startswith((".", "_")) or not d.is_dir() or not re.match(r"\d{2}-", d.name):
            continue            # vault projects are NN-name folders; plans/, todos/ are not projects
        try:
            os.listdir(d)
        except OSError:
            continue
        ss = _session_state_profile(d)
        if ss and ss != conduct[0]:
            continue  # declared non-personal: never linted from here
        out.append((d, ss))
    return out


def lint_vault_project(d: Path, ss_profile: str | None, det: dict, res_ws: dict) -> list[tuple[str, str]]:
    pm, readme = d / PROJECT_FILE, d / "README.md"
    rtext = ""
    if readme.is_file():
        try:
            rtext = readme.read_text(encoding="utf-8")
        except OSError:
            rtext = ""
    block = bool(re.search(r"^##\s+Project intent\s*$", rtext, re.IGNORECASE | re.M))
    if pm.is_file() and block:
        return [("ERROR", "one home: both PROJECT.md and a README `## Project intent` block exist")]
    if pm.is_file():
        return lint_home(pm, kind="project", res=res_ws, det=det, repo_top=None, ss_profile=ss_profile)
    if block:
        return lint_home(readme, kind="readme", res=res_ws, det=det, repo_top=None, ss_profile=ss_profile)
    pm_ptr = README_POINTER_RE.search(rtext)
    if pm_ptr:
        target = pm_ptr.group("target").rstrip(".,;")
        if NA_RE.match(target):
            if not NA_REASON_RE.match((target + pm_ptr.group("rest")).strip()):
                return [("ERROR", "`Project intent: n/a` needs a reason")]
            return [("INFO", "intent: n/a (reason given)")]
        slug = target.split(":", 1)[0]
        if not INHERITS_RE.match(slug):
            return [("ERROR", f"README pointer {target!r} is not <owner>/<repo>:PROJECT.md")]
        w = _where(slug.casefold(), det)
        if not w.get("paths"):
            return [("WARN", f"intent lives in {slug}; that checkout is not on this device ({w.get('status')})")]
        return lint_repo(Path(w["paths"][0]), det, missing_ok=True)
    return [("WARN", "no intent home (PROJECT.md, a README `## Project intent` block, or a README pointer)")]


def lint_repo(top: Path, det: dict, *, missing_ok: bool = False) -> list[tuple[str, str]]:
    try:
        if _restricted(det):
            pol = _policy(top, "content-read", det)
            if pol.get("outcome") != "allow":
                return [("REFUSED", pol.get("reason") or "not allowed from this chain")]
        res = _resolve_repo(top)
    except Exception as exc:
        return [("ERROR", f"resolver unavailable ({type(exc).__name__}); fail-closed")]
    pm = top / PROJECT_FILE
    if not pm.is_file():
        return [("WARN" if missing_ok else "ERROR",
                 f"no {PROJECT_FILE}; frame one: python3 09-tools/intent-run.py init --frame --repo {top}")]
    return lint_home(pm, kind="project", res=res, det=det, repo_top=top)


def _print_findings(where_label: str, findings: list[tuple[str, str]]) -> tuple[int, int]:
    errs = sum(1 for lvl, _ in findings if lvl in ("ERROR", "REFUSED"))
    warns = sum(1 for lvl, _ in findings if lvl == "WARN")
    if not findings:
        print(f"{where_label}: ok")
    for lvl, msg in findings:
        print(f"{where_label}: {lvl} {msg}")
    return errs, warns


def _lint_remediation_run(sp: Path, doc: dict, run_closures: bool) -> list[tuple[str, str]]:
    if not run_closures:
        return []
    top = _toplevel(sp) or sp.parent
    automated, _ = automated_context()
    res = closure_results(doc, run=True, runnable=True, vroot=top, automated=automated)
    out = [("ERROR", f"{f}: REGRESSED — its RESOLVED closure now fails") for f, s in res.items() if s == "FAIL"]
    out += [("WARN", f"{f}: closure NOT_EXPOSED here (automated allowlist)") for f, s in res.items()
            if s == "NOT_EXPOSED"]
    return out


def _vault_remediation_specs(d: Path) -> list[Path]:
    out = []
    docs = d / "docs"
    for p in sorted(docs.glob("INTENT*.md")) if docs.is_dir() else []:
        try:
            if is_remediation(load_spec(p)):
                out.append(p)
        except OSError:
            continue
    return out


def cmd_lint(*, repo: str | None, spec: str | None, all_: bool, since: str | None = None,
             run_closures: bool = False) -> int:
    det = _detection()
    errs = warns = 0
    if spec:
        sp = Path(spec).expanduser().resolve()
        why = _content_gate(sp.parent, det)
        if why:
            print(f"{sp}: REFUSED {why}")
            return 1
        doc = load_spec(sp)
        findings = lint_spec(doc)
        if is_remediation(doc):
            findings += lint_remediation(doc, sp, since=since) + _lint_remediation_run(sp, doc, run_closures)
        try:
            res = _resolve_repo(sp.parent)
        except Exception:
            res = {}
        a = approval_detail(doc["meta"], doc.get("meta_comments"))
        if res.get("owner_class") == "employer" and a["kind"] not in ("approved-pr", "pending"):
            findings.append(("ERROR", "employer specs accept only `approved via PR <n>`"))
        elif a["kind"] in ("approved", "waived"):
            findings += lint_provenance(sp, doc["meta"], 2)
        e, w = _print_findings(str(sp), findings)
        return 1 if e else 0
    if repo and not all_:
        top = _toplevel(Path(repo).expanduser().resolve()) or Path(repo).expanduser().resolve()
        e, w = _print_findings(str(top), lint_repo(top, det))
        return 1 if e else 0
    if not all_:
        top = _toplevel(Path.cwd())
        if top is None:
            print("lint: pass --repo DIR, --spec PATH or --all", file=sys.stderr)
            return 2
        e, w = _print_findings(str(top), lint_repo(top, det))
        return 1 if e else 0
    try:
        res_ws = _resolve_repo(ROOT)
    except Exception:
        res_ws = {"owner_class": "unknown", "profile": _conduct()[-1], "remotes": []}
    homes = 0
    for d, ss in _vault_project_dirs():
        homes += 1
        e, w = _print_findings(d.relative_to(ROOT).as_posix(), lint_vault_project(d, ss, det, res_ws))
        errs, warns = errs + e, warns + w
        for sp in _vault_remediation_specs(d):
            doc = load_spec(sp)
            f = lint_spec(doc) + lint_remediation(doc, sp) + _lint_remediation_run(sp, doc, run_closures)
            e, w = _print_findings(sp.relative_to(ROOT).as_posix(), f)
            errs, warns = errs + e, warns + w
    skipped = 0
    cache = None
    try:
        pr = _pr()
        dev = pr.current_device(hostname=_PR_KW.get("hostname"), root=_PR_KW.get("root"))["id"]
        cache = pr._load_cache(None, _PR_KW.get("home"))
        if cache is not None and cache.get("device") not in (None, dev):
            print("lint --all: checkout cache belongs to another device; checkouts skipped")
            cache = None
    except Exception as exc:
        print(f"lint --all: checkout cache unavailable ({type(exc).__name__})")
    for co in (cache or {}).get("checkouts") or []:
        p = Path(str(co.get("path") or ""))
        if not p.is_dir():
            continue
        try:
            if _pr().is_workspace_checkout(p, root=_PR_KW.get("root"), home=_PR_KW.get("home")):
                continue  # the vault projects above cover the workspace
        except Exception:
            pass
        if co.get("owner_class") != "personal" and _restricted(det):
            skipped += 1
            continue
        homes += 1
        e, w = _print_findings(str(p), lint_repo(p, det, missing_ok=True))
        errs, warns = errs + e, warns + w
    print(f"lint --all: {homes} home(s), {errs} error(s), {warns} warning(s); "
          f"{skipped} non-personal checkout(s) skipped from this chain")
    return 1 if errs else 0


def _intent_target(repo: str | None, spec: str | None) -> Path:
    if spec:
        return Path(spec).expanduser().resolve()
    base = Path(repo).expanduser().resolve() if repo else Path.cwd()
    if (base / PROJECT_FILE).is_file():
        return base / PROJECT_FILE
    readme = base / "README.md"
    if readme.is_file() and re.search(r"^##\s+Project intent\s*$", readme.read_text(encoding="utf-8"),
                                      re.IGNORECASE | re.M):
        return readme
    top = _toplevel(base)
    if top is not None and (top / PROJECT_FILE).is_file():
        return top / PROJECT_FILE
    return base / PROJECT_FILE


def cmd_next(repo: str | None) -> int:
    target = _intent_target(repo, None)
    if not target.is_file():
        print(f"next: frame the intent — python3 09-tools/intent-run.py init --frame --repo {target.parent}")
        return 0
    doc = parse_intent(target.read_text(encoding="utf-8"))
    findings = lint_intent(doc, kind="project" if target.name == PROJECT_FILE else "readme")
    errors = [m for lvl, m in findings if lvl == "ERROR"]
    life = (doc["meta"].get("lifecycle") or "").strip().lower()
    if errors:
        print(f"next: fix — {errors[0]}")
        return 1
    steps = {
        "discover": "resolve the [HUMAN: …] markers and write a decision rule for every non-known claim, "
                    "then set lifecycle: define",
        "define": "a human approves: python3 09-tools/intent-run.py approve --repo <dir> --by <name> "
                  "(employer repos: `approved via PR <n>`), then set lifecycle: build",
        "build": "verify against the living spec: python3 09-tools/intent-run.py verify --run --record",
        "operate": "keep the knowns table current; re-run intent-run lint when a claim changes",
    }
    print(f"next ({life}): {steps.get(life, 'set a lifecycle: ' + '|'.join(LIFECYCLES))}")
    return 0


def _set_frontmatter_key(text: str, key: str, value: str) -> str:
    line = f"{key}: {value}"
    if not text.startswith("---"):
        return f"---\n{line}\n---\n\n" + text
    end = text.find("\n---", 3)
    head, tail = text[: end], text[end:]
    rx = re.compile(rf"(?m)^{re.escape(key)}\s*:.*$")
    if rx.search(head):
        head = rx.sub(line.replace("\\", "\\\\"), head, count=1)
    else:
        head = head.rstrip("\n") + "\n" + line
    return head + tail


def cmd_approve(*, repo: str | None, spec: str | None, by: str, note: str | None) -> int:
    """Human-only, personal-solo only. Writes the approval line; the human commits it."""
    human = _HUMAN_OVERRIDE
    if human is None:
        try:
            human = bool(_pr().agent_check().get("human"))
        except Exception:
            human = False
    if not human:
        print("REFUSED — approve needs a human at a terminal (an agent cannot approve its own plan)",
              file=sys.stderr)
        return 4
    if not re.fullmatch(r"[^\s#]+", by or "") or (note and "#" in note):
        print("approve: --by is one word without '#', and --note has no '#'", file=sys.stderr)
        return 2
    target = _intent_target(repo, spec)
    if not target.is_file():
        print(f"approve: no intent home or spec at {target}", file=sys.stderr)
        return 2
    try:
        res = _resolve_repo(target.parent)
    except Exception as exc:
        print(f"REFUSED — resolver unavailable ({type(exc).__name__})", file=sys.stderr)
        return 4
    if not res.get("positively_personal"):
        print("REFUSED — approve writes only in personal-solo repos; employer approvals are "
              "`approved via PR <n>` recorded by the PR", file=sys.stderr)
        return 4
    import datetime as _dt
    value = f"approved {_dt.date.today().isoformat()} by {by}" + (f" {note.strip()}" if note else "")
    target.write_text(_set_frontmatter_key(target.read_text(encoding="utf-8"), "approval", value),
                      encoding="utf-8")
    print(f"wrote approval to {target}: {value}")
    print("Commit it yourself, as a human commit with no agent trailer; lint checks the provenance.")
    return 0


def render_project_intent(*, neutral: bool, lifecycle: str = "discover", inherits: str | None = None,
                          inherits_context: str | None = None) -> str:
    """The template, rendered. --neutral drops ws-only lines (and so every `profile:`)."""
    raw = PROJECT_TEMPLATE.read_text(encoding="utf-8")
    lines = []
    for ln in raw.splitlines():
        if WS_ONLY_MARK in ln:
            if neutral:
                continue
            ln = ln.replace(" " + WS_ONLY_MARK, "").replace(WS_ONLY_MARK, "")
        if ln.startswith("lifecycle:"):
            ln = f"lifecycle: {lifecycle}"
        lines.append(ln)
    text = "\n".join(lines).rstrip("\n") + "\n"
    if inherits:
        ctx = inherits_context
        if neutral and ctx:
            ctx = ", ".join(p.strip() for p in ctx.split(",") if not p.strip().startswith("vault:")) or None
        extra = f"inherits: {inherits}\n" + (f"inherits_context: {ctx}\n" if ctx else "")
        meta_end = text.find("\n---", 3)
        head = text[: meta_end + 4]
        head = head[: -4].rstrip("\n") + "\n" + extra + "---"
        text = head + "\n\n## Project intent\n\n" + CHILD_SENTENCE + "\n"
    return text


def _load_check_secrets():
    import importlib.util
    spec = importlib.util.spec_from_file_location("check_secrets_ws", TOOLS / "check-secrets.py")
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def workspace_leak_hits(text: str) -> list[tuple[int, str]]:
    return _load_check_secrets().workspace_leak_scan(text)


def _ensure_pointer(path: Path, *, create: bool) -> str:
    if path.is_file():
        text = path.read_text(encoding="utf-8")
        if POINTER_RE.search(text):
            return "present"
        path.write_text(text.rstrip("\n") + "\n\n" + POINTER_LINE + "\n", encoding="utf-8")
        return "added"
    if not create:
        return "absent"
    path.write_text("# AGENTS.md\n\n" + POINTER_LINE + "\n", encoding="utf-8")
    return "created"


def cmd_init_frame(repo: str | None, *, neutral: bool = False, stdout: bool = False,
                   inherits: str | None = None, inherits_context: str | None = None,
                   lifecycle: str = "discover") -> int:
    if lifecycle not in LIFECYCLES:
        print(f"init --frame: --lifecycle is one of {'|'.join(LIFECYCLES)}", file=sys.stderr)
        return 2
    if inherits and not INHERITS_RE.match(inherits):
        print("init --frame: --inherits is <owner>/<repo>[#path][@ref]", file=sys.stderr)
        return 2
    det = _detection()
    top = Path(repo).expanduser().resolve() if repo else Path.cwd().resolve()
    try:
        if _restricted(det):
            # The Claude refusal runs through the action policy before anything in the repo is read.
            pol = _policy(top, "author", det)
            if pol.get("outcome") != "allow" or not (pol.get("facts") or {}).get("positively_personal"):
                route = " or ".join(pol.get("route_to") or []) or "cursor or codex"
                print(f"REFUSED — {pol.get('reason') or 'not positively personal'}", file=sys.stderr)
                print(f"route: {route} runs `intent-run init --frame --repo <path> --neutral --stdout` "
                      "and lands it by branch → PR → human review", file=sys.stderr)
                return 4
        res = _resolve_repo(top)
    except Exception as exc:
        print(f"REFUSED — resolver unavailable ({type(exc).__name__}); fail-closed", file=sys.stderr)
        return 4
    personal = bool(res.get("positively_personal"))
    use_neutral = neutral or not personal
    text = render_project_intent(neutral=use_neutral, lifecycle=lifecycle, inherits=inherits,
                                 inherits_context=inherits_context)
    if use_neutral:
        hits = workspace_leak_hits(text)
        if hits:
            for line, rule in hits:
                print(f"PROJECT.md:{line} {rule}", file=sys.stderr)
            print("init --frame: the neutral render failed the workspace-leak scan", file=sys.stderr)
            return 1
    if stdout or not personal:
        print(text, end="")
        if not personal:
            print("not positively personal: printed for a branch → PR; nothing was written", file=sys.stderr)
        return 0
    pm = top / PROJECT_FILE
    if pm.exists():
        print(f"exists: {pm}")
    else:
        pm.write_text(text, encoding="utf-8")
        print(f"wrote {pm}")
    print(f"AGENTS.md pointer: {_ensure_pointer(top / 'AGENTS.md', create=True)}")
    ov = _ensure_pointer(top / "AGENTS.override.md", create=False)
    if ov != "absent":
        print(f"AGENTS.override.md pointer: {ov}")
    print("Fill the [HUMAN: …] markers, then: python3 09-tools/intent-run.py lint --repo " + str(top))
    return 0


def _sha256(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()


def verify_record(spec_path: Path, results: list[tuple[int, str, str]], counts: dict, run: bool) -> Path | None:
    """Append a verify record. Personal/workspace: <spec>.verify.jsonl beside the spec.
    Anything else: counts, ids and hashes only, under ~/.config/snds-workspace/state/telemetry/<slug>/."""
    import datetime as _dt
    det = _detection()
    try:
        pr = _pr()
        device = pr.current_device(hostname=_PR_KW.get("hostname"), root=_PR_KW.get("root"))["id"]
    except Exception:
        pr, device = None, "unknown"
    try:
        res = _resolve_repo(spec_path.parent)
    except Exception:
        res = {}
    personal = bool(res.get("positively_personal"))
    if not personal and pr is not None:
        try:
            personal = bool(pr.is_workspace_checkout(spec_path.parent, root=_PR_KW.get("root"),
                                                     home=_PR_KW.get("home")))
        except Exception:
            personal = False
    base = {"schema_version": 1, "ts": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "surface": det.get("acting_host"), "family": det.get("family"), "via": det.get("via"),
            "device": device, "run": run, "counts": counts}
    if personal:
        rec = dict(base, spec=spec_path.name,
                   checks=[{"id": i, "label": lab, "status": st} for i, lab, st in results])
        dest = spec_path.with_name(spec_path.stem + ".verify.jsonl")
    else:
        slug = _origin_slug(res) or "_unknown"
        rec = dict(base, slug=slug, spec_sha256=_sha256(spec_path.read_bytes()),
                   checks=[{"id": i, "label_sha256": _sha256(lab.encode("utf-8"))[:16], "status": st}
                           for i, lab, st in results])
        home = Path(_PR_KW.get("home") or Path.home())
        dest = home / ".config" / "snds-workspace" / "state" / "telemetry"
        for part in slug.split("/"):
            dest = dest / re.sub(r"[^A-Za-z0-9_.-]", "_", part)
        dest = dest / "verify.jsonl"
        top = _toplevel(spec_path)
        for guard in [p for p in (top, spec_path.parent) if p is not None]:
            if dest.resolve().is_relative_to(guard.resolve()):
                print("verify --record: refused a record path inside the repo", file=sys.stderr)
                return None
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n")
    except OSError as exc:
        print(f"verify --record: not written ({type(exc).__name__})", file=sys.stderr)
        return None
    print(f"verify record: {dest}")
    return dest


# ---------------------------------------------------------------------------
# H8 — remediation: recon card, findings register, preserve list, packets, verdict
# ---------------------------------------------------------------------------

SEVERITIES = ("Critical", "High", "Medium", "Low")
A11Y_SEVERITY = {"blocker": "Critical", "major": "High", "minor": "Medium", "nit": "Low"}
FINDING_STATUSES = ("OPEN", "RESOLVED", "DEFERRED")
FINDING_COLUMNS = ("id", "sev", "status", "origin", "observed", "expected", "evidence", "closure",
                   "closed_by", "revisit")
RISK_BANDS = ("low", "medium", "high")
FINDING_ID_RE = re.compile(r"^F-\d{3,}$")
CLOSURE_ID_RE = re.compile(r"^C-\d{3,}$")
CLOSURE_LINE_RE = re.compile(r"^[-*]\s+(C-\d{3,})\s*:\s*(measure|judgment)\s*:\s*(.*?)\s*$", re.IGNORECASE)
ORIGIN_RE = re.compile(r"^(?:recon|external|[a-z0-9][a-z0-9._-]*#[A-Za-z0-9._-]+)$")
WHEN_RE = re.compile(r"^(?:(?P<date>\d{4}-\d{2}-\d{2})|on:\s*\S.*)$", re.IGNORECASE)
DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
PACKET_HEAD_RE = re.compile(r"^###\s+(?P<id>[A-Za-z][\w.-]*)(?:\s+[—–:-]+\s*|\s*$)(?P<title>.*)$")
PACKET_FIELD_RE = re.compile(r"^[-*]\s+\**(?P<key>[A-Za-z][A-Za-z -]*?)\**\s*:\s*\**\s*(?P<val>.*?)\s*$")
PACKET_ORDER = ("outcome", "context", "findings", "sources", "acceptance", "output", "boundaries",
                "last verified state", "non-goals", "verification", "rollback", "bail point", "previous attempts")
PACKET_REQUIRED = ("outcome", "findings", "acceptance", "last verified state", "non-goals", "verification",
                   "rollback", "bail point", "previous attempts")
LOOP_BREAKER_FAILS = 3
RERECON_COMMITS = 50
RECON_START = "<!-- intent:recon:start -->"
RECON_END = "<!-- intent:recon:end -->"
BLANK_CELLS = ("", "-", "—", "n/a", "none")
# A packet is a brief for a cold agent in another tool: these shapes mean it leans on context it lacks.
PACKET_LEAN_RE = (
    ("a wikilink", re.compile(r"\[\[")),
    ("a home-relative path", re.compile(r"(?<![\w.])~/")),
    ("an absolute user path", re.compile(r"/(?:Users|home)/\w")),
    ("local-only agent state", re.compile(r"\.claude/state\b|\bheld/")),
    ("a pointer to the spec instead of its content", re.compile(r"\bsee (?:the )?(?:spec|above|intent)\b", re.I)),
)


def _blank(v: str | None) -> bool:
    return (v or "").strip().lower() in BLANK_CELLS


def norm_sev(raw: str | None) -> str | None:
    """Critical/High/Medium/Low (the ds-advisor DDR scale); a11y blocker/major/minor/nit map 1:1."""
    low = (raw or "").strip().strip("*").lower()
    if low in A11Y_SEVERITY:
        return A11Y_SEVERITY[low]
    for s in SEVERITIES:
        if low == s.lower():
            return s
    return None


def is_remediation(spec: dict) -> bool:
    kind = (spec["meta"].get("kind") or "").strip().lower()
    return kind == "remediation" or bool(re.search(r"^##\s+Findings\s*$", spec["body"], re.IGNORECASE | re.M))


def parse_packets(section: str) -> dict[str, dict]:
    """`### T<n> — title` blocks of `- key: value` fields; indented bullets extend the last field."""
    packets: dict[str, dict] = {}
    cur: dict | None = None
    last: str | None = None
    for raw in section.splitlines():
        m = PACKET_HEAD_RE.match(raw.strip()) if raw.startswith("###") else None
        if m:
            cur = {"id": m.group("id"), "title": m.group("title").strip(), "fields": {}}
            packets[m.group("id").upper()] = cur
            last = None
            continue
        if cur is None or not raw.strip():
            continue
        indented = raw[:1].isspace()
        fm = PACKET_FIELD_RE.match(raw.strip())
        if fm and not indented:
            last = re.sub(r"\s+", " ", fm.group("key").strip().lower())
            cur["fields"][last] = [fm.group("val")] if fm.group("val") else []
        elif last is not None:
            item = re.sub(r"^[-*]\s+", "", raw.strip())
            cur["fields"][last].append(item)
    return packets


def _field(p: dict | None, key: str) -> list[str]:
    return [v for v in ((p or {}).get("fields") or {}).get(key, []) if v.strip()]


def parse_recon_block(body: str) -> dict:
    i, j = body.find(RECON_START), body.find(RECON_END)
    if i < 0 or j < i:
        return {"present": False, "source_sha": None}
    block = body[i:j]
    m = re.search(r"source_sha:\s*`?([0-9a-f]{7,40})`?", block)
    return {"present": True, "source_sha": m.group(1) if m else None}


def parse_remediation(spec: dict) -> dict:
    body = spec["body"]
    fsec = _section(body, "Findings")
    rows = _parse_table(fsec)
    closures: dict[str, dict] = {}
    dupes: list[str] = []
    for line in _subsection(fsec, "Closures").splitlines():
        m = CLOSURE_LINE_RE.match(line.strip())
        if m:
            cid = m.group(1).upper()
            if cid in closures:
                dupes.append(cid)
            closures[cid] = {"kind": m.group(2).lower(), "value": m.group(3).strip()}
    return {"rows": rows, "closures": closures, "closure_dupes": dupes,
            "preserve": _parse_table(_section(body, "Preserve")),
            "packets": parse_packets(_section(body, "Packets")),
            "recon": parse_recon_block(body)}


def _finding_ids(cell: str) -> list[str]:
    return [t.strip().upper() for t in re.split(r"[,;\s]+", cell or "") if t.strip()]


def _today():
    import datetime as _dt
    return _dt.date.today()


def _when_problem(value: str, what: str) -> tuple[str, str] | None:
    v = (value or "").strip()
    m = WHEN_RE.match(v)
    if not m:
        return ("ERROR", f"{what} {v!r} is not a date (YYYY-MM-DD) or `on: <trigger>`")
    if m.group("date") and m.group("date") < _today().isoformat():
        return ("WARN", f"{what} {m.group('date')} has passed")
    return None


def _git_text_at(top: Path, ref: str, rel: str) -> str | None:
    r = _git(["show", f"{ref}:{rel}"], top)
    return r.stdout if r.returncode == 0 else None


def _rel_to_top(path: Path) -> tuple[Path | None, str | None]:
    top = _toplevel(path)
    if top is None:
        return None, None
    try:
        return top, path.resolve().relative_to(top).as_posix()
    except ValueError:
        return top, None


def blocked_by_paths(spec: dict, spec_path: Path | None) -> list[tuple[str, Path | None]]:
    out: list[tuple[str, Path | None]] = []
    raw = (spec["meta"].get("blocked_by") or "").strip()
    if not raw or raw.lower() in BLANK_CELLS:
        return out
    for ref in [r.strip() for r in raw.split(",") if r.strip()]:
        hit = None
        if spec_path is not None:
            top = _toplevel(spec_path)
            for base in [spec_path.parent] + ([top] if top else []):
                cand = (base / ref).resolve()
                if cand.is_file():
                    hit = cand
                    break
        out.append((ref, hit))
    return out


def lint_remediation(spec: dict, spec_path: Path | None = None, *, since: str | None = None) -> list[tuple[str, str]]:
    """The findings register, closures, packets, preserve list and recon freshness."""
    rem = parse_remediation(spec)
    out: list[tuple[str, str]] = []
    rows = rem["rows"]
    if not rows:
        out.append(("ERROR", "remediation spec has no `## Findings` table"))
    else:
        missing = [c for c in FINDING_COLUMNS if c not in rows[0]]
        if missing:
            out.append(("ERROR", f"findings table lacks column(s): {', '.join(missing)}"))
    seen: set[str] = set()
    open_rows = []
    for r in rows:
        fid = (r.get("id") or "").strip()
        tag = fid or "(no id)"
        if not FINDING_ID_RE.match(fid):
            out.append(("ERROR", f"{tag}: id is not F-NNN"))
        elif fid in seen:
            out.append(("ERROR", f"{fid}: duplicate finding id (ids are never reused)"))
        seen.add(fid)
        if norm_sev(r.get("sev")) is None:
            out.append(("ERROR", f"{tag}: sev {r.get('sev')!r} is not Critical|High|Medium|Low "
                                 "(or an a11y blocker|major|minor|nit)"))
        st = (r.get("status") or "").strip().upper()
        if st not in FINDING_STATUSES:
            out.append(("ERROR", f"{tag}: status {r.get('status')!r} is not OPEN|RESOLVED|DEFERRED"))
        if st == "OPEN":
            open_rows.append(fid)
        if not ORIGIN_RE.match((r.get("origin") or "").strip()):
            out.append(("ERROR", f"{tag}: origin {r.get('origin')!r} is not <report-slug>#<ID>, recon or external"))
        cl = (r.get("closure") or "").strip()
        if not _blank(cl):
            if not CLOSURE_ID_RE.match(cl):
                out.append(("ERROR", f"{tag}: closure {cl!r} is not a C-ID into `### Closures` "
                                     "(never a command inside a cell)"))
            elif cl.upper() not in rem["closures"]:
                out.append(("ERROR", f"{tag}: closure {cl} is not defined under `### Closures`"))
        elif st == "RESOLVED":
            out.append(("ERROR", f"{tag}: RESOLVED needs a closure (a C-ID)"))
        if st == "RESOLVED" and _blank(r.get("closed_by")):
            out.append(("ERROR", f"{tag}: RESOLVED needs closed_by (a sha, a verify record or a decision note)"))
        if st == "DEFERRED":
            if _blank(r.get("closed_by")):
                out.append(("ERROR", f"{tag}: DEFERRED needs a reason in closed_by"))
            if _blank(r.get("revisit")):
                out.append(("ERROR", f"{tag}: DEFERRED needs a revisit (a date or `on: <trigger>`)"))
            else:
                p = _when_problem(r.get("revisit") or "", f"{tag}: revisit")
                if p:
                    out.append(p)
        risk = (r.get("risk") or "").strip().lower()
        if risk and risk not in BLANK_CELLS and risk not in RISK_BANDS:
            out.append(("ERROR", f"{tag}: risk {risk!r} is not low|medium|high"))
    for cid in rem["closure_dupes"]:
        out.append(("ERROR", f"closure {cid} is defined twice"))
    for cid, c in rem["closures"].items():
        if not c["value"]:
            out.append(("ERROR", f"closure {cid}: an empty {c['kind']}"))
    if (spec["meta"].get("status") or "").strip().lower() == "closed" and open_rows:
        out.append(("ERROR", f"status: closed is refused while {len(open_rows)} row(s) are OPEN "
                             f"({', '.join(open_rows[:5])})"))
    packets = rem["packets"]
    task_ids = set()
    for t in spec["tasks"]:
        tid = (t.get("id") or "").strip()
        task_ids.add(tid.upper())
        if (t.get("role") or "").strip().lower() == "implementor" and tid.upper() not in packets:
            out.append(("ERROR", f"implementor {tid} has no packet (`### {tid}` under `## Packets`)"))
    for pid, p in packets.items():
        for key in PACKET_REQUIRED:
            if not _field(p, key):
                out.append(("ERROR", f"packet {p['id']}: missing `{key}`"))
        for fid in _finding_ids(" ".join(_field(p, "findings"))):
            if fid not in seen:
                out.append(("ERROR", f"packet {p['id']}: finding {fid} is not in the register"))
        if pid not in task_ids:
            out.append(("WARN", f"packet {p['id']} has no Task graph row"))
    for i, row in enumerate(rem["preserve"], 1):
        glob = (row.get("glob") or "").strip()
        if not glob:
            out.append(("ERROR", f"preserve row {i}: no glob"))
        if _blank(row.get("until")):
            out.append(("ERROR", f"preserve {glob or i}: no `until` (a date or `on: <trigger>`)"))
        else:
            p = _when_problem(row.get("until") or "", f"preserve {glob or i}: until")
            if p:
                out.append(("WARN", p[1] + " (expired)") if p[0] == "WARN" else p)
    for ref, hit in blocked_by_paths(spec, spec_path):
        if hit is None:
            out.append(("ERROR", f"blocked_by {ref!r} does not resolve to a spec file"))
    sha = rem["recon"]["source_sha"]
    if spec_path is not None and sha:
        top = _toplevel(spec_path)
        if top is not None:
            paths = [p.strip() for p in (spec["meta"].get("recon_paths") or "").split(",") if p.strip()]
            r = _git(["rev-list", "--count", f"{sha}..HEAD", "--", *paths], top)
            if r.returncode != 0:
                out.append(("WARN", f"recon source_sha {sha[:9]} is not in this history: re-recon"))
            elif int(r.stdout.strip() or 0) > RERECON_COMMITS:
                out.append(("WARN", f"re-recon: source_sha {sha[:9]} is {r.stdout.strip()} commits behind "
                                    f"(> {RERECON_COMMITS}) on the declared paths"))
    elif rem["recon"]["present"] and not sha:
        out.append(("WARN", "recon block has no source_sha: re-recon"))
    if since and spec_path is not None:
        top, rel = _rel_to_top(spec_path)
        old = _git_text_at(top, since, rel) if top and rel else None
        if old is None:
            out.append(("WARN", f"--since {since}: the spec is absent at that ref"))
        else:
            before = {(r.get("id") or "").strip() for r in parse_remediation(parse_spec(old))["rows"]}
            gone = sorted(x for x in before - seen if x)
            if gone:
                out.append(("ERROR", f"silent drop: {', '.join(gone)} vanished since {since} "
                                     "(defer or resolve a finding; never delete it)"))
    return out


# --- the loop-breaker -------------------------------------------------------


def loop_breaker(spec_path: Path, spec: dict, task_id: str) -> tuple[bool, int, str | None]:
    """(tripped, fails, since). FAIL verify records naming the task since its newest Previous attempt."""
    if not is_remediation(spec):
        return False, 0, None
    p = parse_remediation(spec)["packets"].get(task_id.upper())
    dates = DATE_RE.findall(" ".join(_field(p, "previous attempts")))
    since = max(dates) if dates else None
    rec = spec_path.with_name(spec_path.stem + ".verify.jsonl")
    fails = 0
    tok = re.compile(rf"(?<![\w-]){re.escape(task_id)}(?![\w-])", re.IGNORECASE)
    try:
        lines = rec.read_text(encoding="utf-8").splitlines()
    except OSError:
        lines = []
    for line in lines:
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if since and str(r.get("ts") or "")[:10] <= since:
            continue
        if any(c.get("status") == "FAIL" and tok.search(str(c.get("label") or "")) for c in r.get("checks") or []):
            fails += 1
    return fails >= LOOP_BREAKER_FAILS, fails, since


# --- the content-read gate ---------------------------------------------------


def _content_gate(target: Path, det: dict) -> str | None:
    """None when this chain may read the target's content; else the refusal with its route."""
    if not _restricted(det):
        return None
    try:
        pol = _policy(target, "content-read", det)
    except Exception as exc:
        return f"resolver unavailable ({type(exc).__name__}); fail-closed"
    if pol.get("outcome") != "allow":
        route = " or ".join(pol.get("route_to") or []) or "cursor or codex"
        return f"{pol.get('reason') or 'not allowed from this chain'} — route: {route}"
    return None


def _personal(top: Path, res: dict) -> bool:
    if res.get("positively_personal"):
        return True
    try:
        return bool(_pr().is_workspace_checkout(top, root=_PR_KW.get("root"), home=_PR_KW.get("home")))
    except Exception:
        return False


# --- recon -------------------------------------------------------------------

RECON_SKIP_DIRS = frozenset((".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next",
                             ".cache", "target", ".obsidian", ".smart-env", "vendor", "coverage", ".tox"))
SECRET_NAME_RE = re.compile(
    r"(?:^|/)(?:\.env(?:\.[^/]*)?|[^/]*\.(?:pem|key|p12|pfx|keystore|jks)|id_(?:rsa|dsa|ecdsa|ed25519)|"
    r"\.npmrc|\.pypirc|\.netrc|credentials(?:\.[^/]*)?|secrets?(?:\.[^/]*)?)$", re.IGNORECASE)
LANG_BY_EXT = {
    ".py": "Python", ".js": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".go": "Go", ".rs": "Rust", ".rb": "Ruby", ".java": "Java",
    ".kt": "Kotlin", ".swift": "Swift", ".c": "C", ".h": "C", ".cc": "C++", ".cpp": "C++", ".hpp": "C++",
    ".cs": "C#", ".php": "PHP", ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell", ".vue": "Vue",
    ".svelte": "Svelte", ".css": "CSS", ".scss": "CSS", ".html": "HTML", ".lua": "Lua", ".dart": "Dart",
}
MANIFESTS = ("package.json", "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "Pipfile",
             "Cargo.toml", "go.mod", "Gemfile", "pom.xml", "build.gradle", "build.gradle.kts", "composer.json",
             "Package.swift", "deno.json", "Makefile", "justfile")
LOCKFILES = {"package-lock.json": "package.json", "yarn.lock": "package.json", "pnpm-lock.yaml": "package.json",
             "poetry.lock": "pyproject.toml", "uv.lock": "pyproject.toml", "Pipfile.lock": "Pipfile",
             "Cargo.lock": "Cargo.toml", "go.sum": "go.mod", "Gemfile.lock": "Gemfile",
             "composer.lock": "composer.json"}
MONOREPO_MARKERS = ("pnpm-workspace.yaml", "lerna.json", "nx.json", "turbo.json", "go.work", "rush.json")
LINT_CONFIGS = re.compile(r"^(?:\.eslintrc(?:\.\w+)?|eslint\.config\.\w+|\.prettierrc(?:\.\w+)?|ruff\.toml|\.ruff\.toml|"
                          r"\.flake8|\.pre-commit-config\.yaml|\.golangci\.ya?ml|rustfmt\.toml|biome\.json|"
                          r"\.stylelintrc(?:\.\w+)?|\.markdownlint(?:\.\w+)?)$")
CONVENTION_FILES = ("AGENTS.md", "AGENTS.override.md", "CLAUDE.md", "CONTRIBUTING.md", PROJECT_FILE, "README.md",
                    "CODEOWNERS", ".github/CODEOWNERS", ".editorconfig")
CI_RE = re.compile(r"^(?:\.github/workflows/[^/]+\.ya?ml|\.gitlab-ci\.yml|\.circleci/config\.yml|Jenkinsfile|"
                   r"azure-pipelines\.yml|\.buildkite/[^/]+)$")
TEST_NAME_RE = re.compile(r"(?:^|/)(?:tests?|__tests__|spec)/|(?:^|/)test_[^/]+\.py$|_test\.(?:py|go)$|"
                          r"\.(?:test|spec)\.[jt]sx?$")
LONG_FILE_FLOOR = 200
SOURCE_EXTS = frozenset(set(LANG_BY_EXT) | {".md"})
RECON_FILE_CAP = 2_000_000


def _recon_files(top: Path) -> list[str]:
    """The committed tree at HEAD (read-only: no index refresh), else the index, else a walk."""
    r = _git(["ls-tree", "-r", "-z", "--name-only", "HEAD"], top, timeout=60)
    if r.returncode != 0 or not r.stdout:
        r = _git(["ls-files", "-z"], top, timeout=60)
    if r.returncode == 0 and r.stdout:
        files = [p for p in r.stdout.split("\0") if p]
    else:
        files = []
        for dp, dns, fns in os.walk(top):
            dns[:] = [d for d in dns if d not in RECON_SKIP_DIRS]
            files += [Path(dp, f).relative_to(top).as_posix() for f in fns]
    return sorted(f for f in files if not RECON_SKIP_DIRS.intersection(f.split("/")[:-1]))


def _line_count(p: Path) -> int | None:
    """Lines in a text file, or None (binary, a symlink, unreadable). Never called on a secret name."""
    try:
        if p.is_symlink() or not p.is_file():
            return None
        with open(p, "rb") as fh:
            data = fh.read(RECON_FILE_CAP + 1)
    except OSError:
        return None
    if b"\0" in data[:8192]:
        return None
    return data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0)


def _p99(values: list[int]) -> float:
    s = sorted(values)
    if not s:
        return 0.0
    pos = 0.99 * (len(s) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def _last_change(top: Path, rel: str) -> int:
    r = _git(["log", "-1", "--format=%ct", "--", rel], top)
    if r.returncode == 0 and r.stdout.strip().isdigit():
        return int(r.stdout.strip())
    try:
        return int((top / rel).stat().st_mtime)
    except OSError:
        return 0


def _read_small(p: Path, cap: int = 400_000) -> str:
    try:
        with open(p, "rb") as fh:
            return fh.read(cap).decode("utf-8", errors="replace")
    except OSError:
        return ""


def build_recon(top: Path, res: dict) -> tuple[dict, list[str]]:
    """The recon facts, and the secret-shaped names (stdout only; never opened, never stored)."""
    files = _recon_files(top)
    secrets = [f for f in files if SECRET_NAME_RE.search(f)]
    secret_set = set(secrets)
    safe = [f for f in files if f not in secret_set]
    langs: dict[str, int] = {}
    for f in safe:
        lang = LANG_BY_EXT.get(Path(f).suffix.lower())
        if lang:
            langs[lang] = langs.get(lang, 0) + 1
    counts: dict[str, int] = {}
    binary = 0
    for f in safe:
        n = _line_count(top / f)
        if n is None:
            binary += 1
        else:
            counts[f] = n
    # Long-file hazard over source and prose only: lockfiles and data dumps are long by nature.
    src = {f: n for f, n in counts.items() if Path(f).suffix.lower() in SOURCE_EXTS}
    p99 = _p99(list(src.values()))
    long_files = sorted(((n, f) for f, n in src.items() if n > p99 and n >= LONG_FILE_FLOOR), reverse=True)
    manifests = [f for f in safe if f.rsplit("/", 1)[-1] in MANIFESTS]
    root_pkg = top / "package.json" if "package.json" in safe else None
    pkg: dict = {}
    if root_pkg is not None:
        try:
            pkg = json.loads(_read_small(root_pkg) or "{}")
        except ValueError:
            pkg = {}
    scripts = pkg.get("scripts") if isinstance(pkg.get("scripts"), dict) else {}
    runner = "pnpm" if "pnpm-lock.yaml" in safe else "yarn" if "yarn.lock" in safe else "npm"
    pyproject = _read_small(top / "pyproject.toml") if "pyproject.toml" in safe else ""
    makefile = _read_small(top / "Makefile") if "Makefile" in safe else ""
    make_targets = [t for t in re.findall(r"(?m)^([A-Za-z][\w.-]*)\s*:(?!=)", makefile)][:8]
    build, test = [], []
    if "build" in scripts:
        build.append(f"{runner} run build")
    if "[build-system]" in pyproject:
        build.append("python -m build")
    if make_targets:
        build.append("make " + "|".join(make_targets))
    if "test" in scripts:
        test.append(f"{runner} test")
    if "[tool.pytest" in pyproject:
        test.append("pytest")
    if "test" in make_targets:
        test.append("make test")
    test_files = [f for f in safe if TEST_NAME_RE.search(f)]
    ci = [f for f in safe if CI_RE.match(f)]
    lint = sorted({f for f in safe if "/" not in f and LINT_CONFIGS.match(f)}
                  | ({"pyproject.toml [tool.ruff]"} if "[tool.ruff" in pyproject else set()))
    conventions = [c for c in CONVENTION_FILES if c in safe]
    stale = []
    for f in safe:
        base = f.rsplit("/", 1)[-1]
        if base in LOCKFILES:
            man = (f.rsplit("/", 1)[0] + "/" if "/" in f else "") + LOCKFILES[base]
            if man in safe and _last_change(top, f) < _last_change(top, man):
                stale.append(f"{f} older than {man}")
    mono = sorted({f for f in safe if f.rsplit("/", 1)[-1] in MONOREPO_MARKERS})
    if isinstance(pkg.get("workspaces"), (list, dict)):
        mono.append("package.json workspaces")
    if re.search(r"(?m)^\[workspace\]", _read_small(top / "Cargo.toml") if "Cargo.toml" in safe else ""):
        mono.append("Cargo.toml [workspace]")
    head = _git(["rev-parse", "HEAD"], top)
    when = _git(["log", "-1", "--format=%cs"], top)
    facts = {
        "source_sha": head.stdout.strip() if head.returncode == 0 else None,
        "date": when.stdout.strip() if when.returncode == 0 else None,
        "repo": _origin_slug(res) or top.name, "owner_class": res.get("owner_class"), "profile": res.get("profile"),
        "files": len(files), "text_files": len(counts), "binary_files": binary,
        "languages": sorted(langs.items(), key=lambda kv: (-kv[1], kv[0])),
        "manifests": manifests, "build": build, "test": test, "test_files": len(test_files), "ci": ci,
        "lint": lint, "conventions": conventions, "secret_count": len(secrets),
        "p99": round(p99), "long_files": [(f, n) for n, f in long_files], "stale_locks": stale, "monorepo": mono,
    }
    return facts, secrets


def _list_cell(items: list[str], cap: int = 8) -> str:
    if not items:
        return "none found"
    more = f" (+{len(items) - cap} more)" if len(items) > cap else ""
    return ", ".join(f"`{i}`" for i in items[:cap]) + more


def render_recon(f: dict) -> str:
    langs = ", ".join(f"{k} {v}" for k, v in f["languages"]) or "none detected"
    rows = [
        ("languages (file counts by extension)", langs, "inferred"),
        ("manifests", _list_cell(f["manifests"]), "known"),
        ("build", _list_cell(f["build"]), "known" if f["build"] else "assumed"),
        ("test commands", _list_cell(f["test"]), "known" if f["test"] else "assumed"),
        ("test files (by name)", str(f["test_files"]), "assumed"),
        ("CI", _list_cell(f["ci"]), "known"),
        ("lint / format config", _list_cell(f["lint"]), "known"),
        ("conventions", _list_cell(f["conventions"]), "known"),
        ("secret-shaped filenames", f"{f['secret_count']} (names printed to stdout only; never opened)", "assumed"),
    ]
    hazards = []
    if f["long_files"]:
        top5 = ", ".join(f"`{p}` ({n})" for p, n in f["long_files"][:5])
        more = f" (+{len(f['long_files']) - 5} more)" if len(f["long_files"]) > 5 else ""
        hazards.append(("long files", f"{len(f['long_files'])} source or prose files above this repo's p99 ({f['p99']} lines, floor "
                                      f"{LONG_FILE_FLOOR}): {top5}{more}", "inferred"))
    if f["stale_locks"]:
        hazards.append(("lockfile older than its manifest", "; ".join(f["stale_locks"][:5]), "inferred"))
    if len(f["languages"]) >= 3:
        hazards.append(("three or more languages", ", ".join(k for k, _ in f["languages"]), "inferred"))
    if f["monorepo"]:
        hazards.append(("monorepo markers", _list_cell(f["monorepo"]), "known"))
    out = [RECON_START, "", "Regenerated by `intent-run init --recon`; edits inside these markers are overwritten.",
           "", f"- source_sha: `{f['source_sha']}` (committed {f['date']})",
           f"- repo: `{f['repo']}` · owner class: {f['owner_class']} · profile: {f['profile']}",
           f"- files: {f['files']} tracked ({f['text_files']} text, {f['binary_files']} binary or unreadable)",
           "", "| signal | value | label |", "|---|---|---|"]
    out += [f"| {a} | {b.replace('|', chr(92) + '|')} | {c} |" for a, b, c in rows]
    out += ["", "| hazard | detail | label |", "|---|---|---|"]
    out += ([f"| {a} | {b.replace('|', chr(92) + '|')} | {c} |" for a, b, c in hazards]
            or ["| none | no hazard crossed this repo's own thresholds | inferred |"])
    out += ["", "Labels: known = read from a manifest or config; inferred = counted; assumed = naming only.",
            "", RECON_END]
    return "\n".join(out) + "\n"


def _place_recon(text: str, block: str) -> str:
    i, j = text.find(RECON_START), text.find(RECON_END)
    if i >= 0 and j > i:
        return text[:i] + block.rstrip("\n") + text[j + len(RECON_END):]
    m = re.search(r"^##\s+Recon\s*$", text, re.IGNORECASE | re.M)
    if m:
        rest = text[m.end():].lstrip("\n")
        return text[: m.end()] + "\n\n" + block + ("\n" + rest if rest.strip() else "")
    return text.rstrip("\n") + "\n\n## Recon\n\n" + block


def cmd_init_recon(repo: str | None, *, spec: str | None = None, stdout: bool = False) -> int:
    """A read-only recon card. Content-read policy first: a Claude chain on a non-personal repo is routed."""
    det = _detection()
    top0 = Path(repo).expanduser().resolve() if repo else Path.cwd().resolve()
    why = _content_gate(top0, det)
    if why:
        print(f"REFUSED — {why}", file=sys.stderr)
        print("route: that surface runs `intent-run init --recon --repo <path>`; the card goes to stdout and "
              "nothing is committed by default", file=sys.stderr)
        return 4
    top = _toplevel(top0)
    if top is None:
        print(f"init --recon: {top0} is not a git repo", file=sys.stderr)
        return 2
    try:
        res = _resolve_repo(top)
    except Exception as exc:
        print(f"REFUSED — resolver unavailable ({type(exc).__name__}); fail-closed", file=sys.stderr)
        return 4
    personal = _personal(top, res)
    facts, secrets = build_recon(top, res)
    block = render_recon(facts)
    note = ("secret-shaped filenames (stdout only, never opened): " + ", ".join(secrets)) if secrets else ""
    if stdout or not personal:
        print(block, end="")
        if note:
            print(note)
        if not personal:
            print("not positively personal: printed only; nothing was written or committed", file=sys.stderr)
        return 0
    dest = Path(spec).expanduser().resolve() if spec else top / "docs" / "RECON.md"
    try:
        dest.relative_to(top)
    except ValueError:
        print(f"init --recon: {dest} is outside {top}", file=sys.stderr)
        return 2
    if dest.exists():
        dest.write_text(_place_recon(dest.read_text(encoding="utf-8"), block), encoding="utf-8")
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text("# Recon\n\n" + block, encoding="utf-8")
    print(f"wrote recon card to {dest} (source_sha {str(facts['source_sha'])[:9]})")
    if note:
        print(note)
    return 0


# --- verdict -----------------------------------------------------------------


def closure_results(spec: dict, *, run: bool, runnable: bool, vroot: Path | None = None,
                    automated: bool = True) -> dict[str, str]:
    """RESOLVED rows' closures → PASS | FAIL | NOT_EXPOSED | UNRUN | ATTESTED | NONE."""
    rem = parse_remediation(spec)
    tracked = tracked_tool_scripts(vroot) if (run and runnable and vroot) else set()
    out: dict[str, str] = {}
    cache: dict[str, str] = {}
    for r in rem["rows"]:
        fid = (r.get("id") or "").strip()
        if (r.get("status") or "").strip().upper() != "RESOLVED":
            continue
        c = rem["closures"].get((r.get("closure") or "").strip().upper())
        if c is None:
            out[fid] = "NONE"
            continue
        if c["kind"] == "judgment":
            out[fid] = "ATTESTED"
            continue
        if not run:
            out[fid] = "UNRUN"
            continue
        if not runnable:
            out[fid] = "NOT_EXPOSED"
            continue
        if c["value"] in cache:
            out[fid] = cache[c["value"]]
            continue
        status, _, argv = classify_check({"measure": c["value"]}, automated=automated, tracked=tracked)
        if status == "RUN":
            try:
                rc = subprocess.run(argv, cwd=str(vroot), shell=False, timeout=MEASURE_TIMEOUT,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
            except (OSError, subprocess.TimeoutExpired):
                rc = 126
            status = "PASS" if rc == 0 else "FAIL"
        elif status == "BAD":
            status = "FAIL"
        elif status not in ("NOT_EXPOSED",):
            status = "NOT_EXPOSED"
        cache[c["value"]] = status
        out[fid] = status
    return out


def compute_verdict(spec: dict, *, closures: dict[str, str], prior: dict | None = None) -> dict:
    """mission-fit verdict: Fit (0), Fit with gaps (0), Unfit (1), Blocked (2). Blocked beats a plausible Fit."""
    rows = {(r.get("id") or "").strip(): r for r in parse_remediation(spec)["rows"]}
    sev = {fid: norm_sev(r.get("sev")) for fid, r in rows.items()}
    st = {fid: (r.get("status") or "").strip().upper() for fid, r in rows.items()}
    hi = ("Critical", "High")
    reasons: list[str] = []
    open_hi = [f for f in rows if st[f] == "OPEN" and sev[f] in hi]
    regressed = [f for f, s in closures.items() if s == "FAIL"]
    dropped: list[str] = []
    reopened: list[str] = []
    resolved_in_range: list[str] = []
    if prior is not None:
        prows = {(r.get("id") or "").strip(): r for r in parse_remediation(prior)["rows"]}
        pst = {f: (r.get("status") or "").strip().upper() for f, r in prows.items()}
        dropped = sorted(f for f in prows if f and f not in rows)
        reopened = sorted(f for f in rows if pst.get(f) == "RESOLVED" and st[f] == "OPEN")
        resolved_in_range = sorted(f for f in rows if st[f] == "RESOLVED" and pst.get(f) != "RESOLVED")
    blocked = [f for f, s in closures.items() if s in ("UNRUN", "NOT_EXPOSED") and sev.get(f) in hi]
    gaps = [f for f in rows if (st[f] == "OPEN" and sev[f] not in hi) or st[f] == "DEFERRED"]
    for f in open_hi:
        reasons.append(f"{f} {sev[f]} OPEN")
    for f in regressed:
        reasons.append(f"{f} REGRESSED (its closure now fails)")
    for f in reopened:
        reasons.append(f"{f} REGRESSED (RESOLVED before the range, OPEN at its tip)")
    for f in dropped:
        reasons.append(f"{f} dropped from the register (silent drop)")
    for f in blocked:
        why = "not run: pass --run on a checkout of the keyed ref" if closures[f] == "UNRUN" else "not exposed here"
        reasons.append(f"{f} {sev[f]} RESOLVED but its closure is {closures[f]} ({why})")
    for f in gaps:
        extra = f" (revisit {rows[f].get('revisit')})" if st[f] == "DEFERRED" else ""
        reasons.append(f"{f} {sev[f] or '?'} {st[f]}{extra}")
    if open_hi or regressed or reopened or dropped:
        word, code = "Unfit", 1
    elif blocked:
        word, code = "Blocked", 2
    elif gaps:
        word, code = "Fit with gaps", 0
    else:
        word, code = "Fit", 0
    counts = {s: sum(1 for f in rows if st[f] == s) for s in FINDING_STATUSES}
    return {"verdict": word, "exit": code, "counts": counts, "open_critical_high": open_hi,
            "regressed": sorted(set(regressed) | set(reopened)), "dropped": dropped, "blocked": blocked,
            "gaps": gaps, "resolved_in_range": resolved_in_range, "closures": closures, "reasons": reasons}


def _rev(top: Path, ref: str) -> str | None:
    r = _git(["rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"], top)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def _cited_ids(top: Path, rng: str) -> list[str]:
    r = _git(["log", "--format=%s%n%b", rng], top, timeout=30)
    if r.returncode != 0:
        return []
    return sorted(set(re.findall(r"\b(?:F-\d{3,}|T\d+[\w.-]*)\b", r.stdout)))


def cmd_verdict(spec_path: Path, *, branch: str | None = None, rng: str | None = None, run: bool = False,
                as_json: bool = False, base: str | None = None, automated: bool | None = None) -> int:
    det = _detection()
    why = _content_gate(spec_path.parent, det)
    if why:
        print(f"REFUSED — {why}", file=sys.stderr)
        return 4
    top, rel = _rel_to_top(spec_path)
    key = "working tree"
    prior_text = None
    tip = None
    commits = []
    if branch or rng:
        if top is None or rel is None:
            print("verdict: --branch/--range need the spec inside a git repo", file=sys.stderr)
            return 2
        if branch:
            tip_ref = branch
            base_ref = base or ("main" if _rev(top, "main") else "HEAD")
            mb = _git(["merge-base", base_ref, branch], top)
            start = mb.stdout.strip() if mb.returncode == 0 else None
            key = f"branch {branch} (since merge-base with {base_ref})"
        else:
            if ".." not in rng:
                print("verdict: --range is A..B", file=sys.stderr)
                return 2
            start, tip_ref = rng.split("..", 1)
            key = f"range {rng}"
        tip = _rev(top, tip_ref)
        if tip is None:
            print(f"verdict: Blocked — {tip_ref} does not resolve here (fetch it first)")
            return 2
        text = _git_text_at(top, tip, rel)
        if text is None:
            print(f"verdict: Blocked — the spec {rel} is absent at {tip_ref}")
            return 2
        if start:
            prior_text = _git_text_at(top, start, rel)
            commits = _cited_ids(top, f"{start}..{tip}")
    else:
        text = spec_path.read_text(encoding="utf-8")
    spec = parse_spec(text)
    if not is_remediation(spec):
        print("verdict: not a remediation spec (no `## Findings` register)", file=sys.stderr)
        return 2
    runnable = tip is None or (top is not None and _rev(top, "HEAD") == tip)
    vroot = top or spec_path.parent
    if automated is None and run:
        automated, _ = automated_context()
    res = compute_verdict(spec, closures=closure_results(spec, run=run, runnable=runnable, vroot=vroot,
                                                          automated=bool(automated)),
                          prior=parse_spec(prior_text) if prior_text is not None else None)
    res.update(spec=rel or str(spec_path), key=key, tip=tip, cites=commits)
    if as_json:
        print(json.dumps(res, indent=2))
        return res["exit"]
    c = res["counts"]
    print(f"verdict: {res['verdict']} (exit {res['exit']})")
    print(f"spec: {res['spec']} · key: {key}" + (f" @ {tip[:9]}" if tip else ""))
    print(f"findings: open={c['OPEN']} resolved={c['RESOLVED']} deferred={c['DEFERRED']} · "
          f"critical/high open={len(res['open_critical_high'])}")
    if prior_text is not None or branch or rng:
        print(f"range: resolved={', '.join(res['resolved_in_range']) or 'none'} · "
              f"regressed={', '.join(res['regressed']) or 'none'} · dropped={', '.join(res['dropped']) or 'none'} · "
              f"commits cite={', '.join(commits) or 'none'}")
    for line in res["reasons"]:
        print(f"  - {line}")
    return res["exit"]


# --- findings, next, packet --------------------------------------------------


def _ordered_open(spec: dict) -> list[dict]:
    rows = [r for r in parse_remediation(spec)["rows"] if (r.get("status") or "").strip().upper() == "OPEN"]

    def key(r):
        risk = (r.get("risk") or "").strip().lower()
        band = RISK_BANDS.index(risk) if risk in RISK_BANDS else 1
        s = norm_sev(r.get("sev"))
        return band, SEVERITIES.index(s) if s else len(SEVERITIES), (r.get("id") or "")
    return sorted(rows, key=key)


def _packet_for(rem: dict, fid: str) -> dict | None:
    for p in rem["packets"].values():
        if fid.upper() in _finding_ids(" ".join(_field(p, "findings"))):
            return p
    return None


def cmd_findings(spec_path: Path, *, status: str | None = None, as_json: bool = False) -> int:
    why = _content_gate(spec_path.parent, _detection())
    if why:
        print(f"REFUSED — {why}", file=sys.stderr)
        return 4
    spec = load_spec(spec_path)
    rem = parse_remediation(spec)
    rows = [r for r in rem["rows"] if not status or (r.get("status") or "").strip().upper() == status.upper()]
    lint = lint_remediation(spec, spec_path)
    if as_json:
        print(json.dumps({"findings": rows, "closures": rem["closures"], "preserve": rem["preserve"],
                          "packets": sorted(p["id"] for p in rem["packets"].values()),
                          "lint": [{"level": lv, "message": m} for lv, m in lint]}, indent=2))
    else:
        for r in rows:
            p = _packet_for(rem, r.get("id") or "")
            print(f"{(r.get('id') or '?'):6} {(norm_sev(r.get('sev')) or '?'):8} {(r.get('status') or '?').upper():9}"
                  f" {(r.get('origin') or ''):38} {'→ ' + p['id'] if p else ''}")
        counts = {s: sum(1 for r in rem["rows"] if (r.get("status") or "").strip().upper() == s)
                  for s in FINDING_STATUSES}
        print(f"register: {len(rem['rows'])} finding(s) · " + " ".join(f"{k.lower()}={v}" for k, v in counts.items())
              + f" · packets={len(rem['packets'])} · preserve={len(rem['preserve'])}")
        for lv, m in lint:
            print(f"lint {lv}: {m}")
    return 1 if any(lv == "ERROR" for lv, _ in lint) else 0


def cmd_next_remediation(spec_path: Path) -> int:
    spec = load_spec(spec_path)
    rem = parse_remediation(spec)
    by_id = index_tasks(spec["tasks"])
    ordered = _ordered_open(spec)
    if not ordered:
        print("next: no OPEN findings — run `intent-run verdict --spec <spec> --run` for the mission-fit verdict")
        return 0
    lines = []
    for r in ordered:
        fid = (r.get("id") or "").strip()
        p = _packet_for(rem, fid)
        if p is None:
            state = "no packet (write `### T<n>` under `## Packets`)"
        else:
            t = by_id.get(p["id"]) or by_id.get(p["id"].upper())
            tripped, n, _ = loop_breaker(spec_path, spec, p["id"])
            if tripped:
                state = f"{p['id']} loop-breaker ({n} FAIL records): add a Previous attempts entry first"
            else:
                state = f"{p['id']} {task_status(t, spec['meta'], by_id) if t else 'no task row'}"
        lines.append((fid, r, state))
    fid, r, state = lines[0]
    print(f"next: {fid} ({norm_sev(r.get('sev'))}, risk {(r.get('risk') or 'medium').strip().lower()}) → {state}")
    if not state.startswith("no packet"):
        print(f"      brief: python3 09-tools/intent-run.py packet --format prompt {state.split()[0]} --spec {spec_path}")
    for fid, r, state in lines[1:10]:
        print(f"  then {fid} ({norm_sev(r.get('sev'))}) → {state}")
    return 0


def packet_problems(text: str) -> list[str]:
    return [f"leans on {name}: {m.group(0)!r}" for name, rx in PACKET_LEAN_RE for m in [rx.search(text)] if m]


def _synth_packet(row: dict, rem: dict) -> dict:
    fid = (row.get("id") or "").strip()
    cl = rem["closures"].get((row.get("closure") or "").strip().upper())
    ver = [cl["value"]] if cl and cl["kind"] == "measure" else []
    return {"id": fid, "title": (row.get("observed") or fid)[:80], "synthetic": True, "fields": {
        "outcome": [row.get("expected") or ""], "findings": [fid], "acceptance": [row.get("expected") or ""],
        "last verified state": [], "non-goals": ["anything outside this finding"], "verification": ver,
        "rollback": ["discard the branch"], "previous attempts": ["none recorded"],
        "bail point": ["the fix needs a path outside the scope below, or a verify command cannot run here"]}}


def build_packet(spec_path: Path, spec: dict, ident: str) -> dict:
    rem = parse_remediation(spec)
    rows = {(r.get("id") or "").strip().upper(): r for r in rem["rows"]}
    ident_u = ident.strip().upper()
    if ident_u in rem["packets"]:
        p = rem["packets"][ident_u]
    elif ident_u in rows:
        p = _packet_for(rem, ident_u) or _synth_packet(rows[ident_u], rem)
    else:
        raise KeyError(ident)
    fids = _finding_ids(" ".join(_field(p, "findings")))
    task = index_tasks(spec["tasks"]).get(p["id"]) or index_tasks(spec["tasks"]).get(p["id"].upper()) or {}
    top = _toplevel(spec_path)
    try:
        res = _resolve_repo(top) if top else {}
    except Exception:
        res = {}
    repo = _origin_slug(res) or (top.name if top else spec_path.parent.name)
    sha = " ".join(_field(p, "last verified state")).strip("` ")
    if not sha and top is not None:
        h = _git(["rev-parse", "HEAD"], top)
        sha = h.stdout.strip() if h.returncode == 0 else ""
    verify: list[str] = []
    for v in _field(p, "verification"):
        v = v.strip().strip("`")
        if v and v not in verify:
            verify.append(v)
    findings = []
    for fid in fids:
        r = rows.get(fid) or {}
        cl = rem["closures"].get((r.get("closure") or "").strip().upper())
        if cl and cl["kind"] == "measure" and cl["value"] not in verify:
            verify.append(cl["value"])
        findings.append({"id": fid, "sev": norm_sev(r.get("sev")), "observed": r.get("observed") or "",
                         "expected": r.get("expected") or "", "evidence": r.get("evidence") or ""})
    writes = [t for t in _split_depth0(task.get("writes") or "") if not _blank(t)]
    forbids = [t for t in _split_depth0(task.get("forbids") or "") if not _blank(t)]
    preserve = [{"glob": (x.get("glob") or "").strip("` "), "why": x.get("why") or "", "until": x.get("until") or ""}
                for x in rem["preserve"] if (x.get("glob") or "").strip()]
    return {"id": p["id"], "title": p.get("title") or "", "repo": repo, "base": sha, "fields": p["fields"],
            "synthetic": bool(p.get("synthetic")), "findings": findings, "writes": writes, "forbids": forbids,
            "preserve": preserve, "verify": verify, "owner_class": res.get("owner_class")}


def render_packet_prompt(pk: dict) -> str:
    f = pk["fields"]

    def txt(key: str, default: str = "n/a") -> str:
        vals = [v for v in f.get(key, []) if v.strip()]
        return "\n".join(vals) if vals else default

    def bullets(items: list[str], default: str) -> list[str]:
        return [f"- {i}" for i in items] if items else [f"- {default}"]

    title = f"Task brief {pk['id']}" + (f": {pk['title']}" if pk["title"] else "")
    out = [f"# {title}", "",
           f"You are a coding agent working in the git repository `{pk['repo']}`. This brief is self-contained: "
           "everything you need is below, and nothing outside this repository is required. Work on a new "
           f"branch from commit `{pk['base'] or 'the default branch tip'}`; never push to the default branch.", "",
           "## Goal", "", txt("outcome"), ""]
    if f.get("context"):
        out += ["## Context", "", txt("context"), ""]
    out += ["## Findings to resolve", ""]
    for x in pk["findings"]:
        out.append(f"- {x['id']} ({x['sev'] or 'unrated'}): observed: {x['observed']} · expected: {x['expected']}"
                   + (f" · evidence: {x['evidence']}" if not _blank(x["evidence"]) else ""))
    if not pk["findings"]:
        out.append("- none linked")
    out += ["", "## Scope", ""]
    out += [f"- May write: {', '.join(f'`{w}`' for w in pk['writes']) if pk['writes'] else 'only what the goal needs'}",
            f"- Must not touch: {', '.join(f'`{w}`' for w in pk['forbids']) if pk['forbids'] else 'anything the goal does not need'}"]
    for x in pk["preserve"]:
        until = re.sub(r"^on:\s*", "", x["until"].strip(), flags=re.IGNORECASE)
        out.append(f"- Preserve `{x['glob']}`: {x['why']} (until {until})")
    if f.get("boundaries"):
        out.append(f"- {txt('boundaries')}")
    out += ["", "## Non-goals", ""] + bullets([v for v in f.get("non-goals", []) if v.strip()], "none stated")
    out += ["", "## Acceptance", ""]
    out += bullets([v for v in f.get("acceptance", []) if v.strip()] + [f"{x['id']}: {x['expected']}"
                                                                        for x in pk["findings"] if x["expected"]],
                   "the verify commands pass")
    out += ["", "## Verify", "", "Run each command from the repository root; every one must exit 0.", ""]
    out += bullets([f"`{v}`" for v in pk["verify"]], "no command: say so in the report, and do not claim done")
    if f.get("output"):
        out += ["", "## Output", "", txt("output")]
    out += ["", "## Rollback", "", txt("rollback", "discard the branch"),
            "", "## Bail point", "",
            "Stop and report `blocked` (never a plausible substitute) when: " + txt("bail point", "a step is impossible"),
            "", "## Previous attempts", "", txt("previous attempts", "none recorded"),
            "", "## Report back", "",
            "Reply with the branch name, the commits, each Verify command with its exit code, and the finding ids "
            "you believe resolved. If you could not finish, say `blocked` and why."]
    return "\n".join(out).rstrip("\n") + "\n"


def cmd_packet(spec_path: Path, ident: str, *, fmt: str = "prompt") -> int:
    det = _detection()
    why = _content_gate(spec_path.parent, det)
    if why:
        print(f"REFUSED — {why}", file=sys.stderr)
        return 4
    spec = load_spec(spec_path)
    try:
        pk = build_packet(spec_path, spec, ident)
    except KeyError:
        print(f"packet: {ident} is neither a packet (### T<n>) nor a finding (F-NNN) in {spec_path.name}",
              file=sys.stderr)
        return 2
    if fmt == "json":
        print(json.dumps(pk, indent=2))
        return 0
    text = render_packet_prompt(pk)
    problems = packet_problems(text)
    if pk.get("owner_class") != "personal":
        problems += [f"workspace-leak: line {ln} {rule}" for ln, rule in workspace_leak_hits(text)]
    if problems:
        for p in problems:
            print(f"packet {pk['id']}: not self-contained — {p}", file=sys.stderr)
        return 1
    if pk["synthetic"]:
        print(f"packet: {ident} has no packet; this brief is synthesized from the finding alone", file=sys.stderr)
    print(text, end="")
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
    kernel = Path(intent_scope.__file__)
    assert "subprocess" not in kernel.read_text(encoding="utf-8"), "intent_scope.py must never shell out"
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
        shutil.copy2(kernel, copy.parent / kernel.name)
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


CLAUDE_DET = {"acting_host": "claude-code", "family": "claude", "family_for_walls": "claude", "via": "ancestry",
              "verified": True, "agent_possible": True}
CURSOR_DET = {"acting_host": "cursor", "family": "cursor", "family_for_walls": "cursor", "via": "env",
              "verified": True, "agent_possible": False}
LANE_CFG = '[hook "ws-lane-commit-msg"]\n\tcommand = true\n\tevent = commit-msg\n'


@contextlib.contextmanager
def _pr_context(root: Path, home: Path, det: dict, human: bool | None = None):
    global _DETECTION_OVERRIDE, _HUMAN_OVERRIDE, _READS
    saved = (dict(_PR_KW), _DETECTION_OVERRIDE, _HUMAN_OVERRIDE, _READS)
    _PR_KW.update(root=root, home=home, hostname="host-a")
    _DETECTION_OVERRIDE, _HUMAN_OVERRIDE, _READS = det, human, []
    try:
        yield
    finally:
        _PR_KW.clear()
        _PR_KW.update(saved[0])
        _DETECTION_OVERRIDE, _HUMAN_OVERRIDE, _READS = saved[1], saved[2], saved[3]


def _pr_fixture_root(td: Path) -> tuple[Path, Path, list[str]]:
    """Synthetic tables (pat-sample personal, acme-corp employer), a temp HOME with telemetry/."""
    pr = _pr()
    root = td / "fxroot"
    for name, src in (("devices", "profile_resolve"), ("context-remotes", "profile_resolve"),
                      ("surfaces", "profile_resolve"), ("action-policy", "action_policy"),
                      ("vetted-scripts", "action_policy")):
        dest = root / pr.TABLE_PATHS[name]
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text((TOOLS / "fixtures" / src / f"{name}.json").read_text(encoding="utf-8"), encoding="utf-8")
    cr_path = root / pr.TABLE_PATHS["context-remotes"]
    cr = json.loads(cr_path.read_text(encoding="utf-8"))
    conduct = list(cr["conduct_order"])
    cr["repos"].append({"slug": "pat-sample/strict", "host": "github.com", "role": "personal",
                        "profile": conduct[1], "visibility": "private", "beacon": False, "vault_project": None})
    cr_path.write_text(json.dumps(cr, indent=2) + "\n", encoding="utf-8")
    (root / "AGENTS.md").write_text("# fixture workspace\n", encoding="utf-8")
    home = td / "home"
    (home / ".config" / "snds-workspace" / "telemetry").mkdir(parents=True, exist_ok=True)
    return root, home, conduct


def _fx_cache(home: Path, repos: dict) -> None:
    """repos: slug -> checkout path. Rewritten before each case (a live rescan may replace it)."""
    doc = {"schema_version": 1, "device": "dev-a", "generated_at": "2026-01-01T00:00:00Z", "generated_by": "human",
           "projects_root": str(home / "Projects"),
           "checkouts": [{"path": str(p), "kind": "repo", "owner_class": "personal", "default_branch": None,
                          "remotes": [{"name": "origin", "form": "https", "host": "github.com", "slug": s}]}
                         for s, p in repos.items()]}
    for co in doc["checkouts"]:
        if co["remotes"][0]["slug"].startswith("acme-corp/"):
            co["owner_class"] = "employer"
    (home / ".config" / "snds-workspace" / "telemetry" / "checkouts.json").write_text(json.dumps(doc), encoding="utf-8")


def _fx_intent(lifecycle: str = "define", extra_meta: str = "", sentinel: str = "") -> str:
    return (f"---\nlifecycle: {lifecycle}\n{extra_meta}---\n\n## Project intent\n\n### Problem & audience\n\n"
            f"A synthetic problem for a synthetic audience. {sentinel}\n\n### Knowns & unknowns\n\n"
            "| claim | label | tier | evidence | decision rule |\n|---|---|---|---|---|\n"
            "| People want the widget | assumed | T4 | two interviews | if fewer than 3 of 5 confirm, drop it |\n\n"
            "### Out of scope & later\n\nn/a (fixture)\n")


def _fx_repo(td: Path, name: str, slug: str, files: dict | None = None, *, msg: str = "init",
             lane: bool = False, agents: bool = True) -> Path:
    repo, env = _new_repo(td, name)
    _run_fixture_git(["remote", "add", "origin", f"https://github.com/{slug}.git"], repo, env)
    if lane:
        with open(repo / ".git" / "config", "a", encoding="utf-8") as fh:
            fh.write(LANE_CFG)
    files = dict(files or {})
    if agents:
        files.setdefault("AGENTS.md", "# agents\n\n" + POINTER_LINE + "\n")
    h = _History(repo, env)
    mark = h.commit("main", msg, files)
    h.flush()
    sha = h.sha(mark)
    _run_fixture_git(["update-ref", "refs/remotes/origin/main", sha], repo, env)
    _run_fixture_git(["symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main"], repo, env)
    for rel, content in files.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(content, encoding="utf-8")
    return repo


def _levels(findings: list[tuple[str, str]], level: str) -> list[str]:
    return [m for lvl, m in findings if lvl == level]


def _snapshot(top: Path) -> dict:
    return {p.relative_to(top).as_posix(): p.read_bytes() for p in sorted(top.rglob("*")) if p.is_file()}


def _st_project_frame() -> None:
    import builtins
    from unittest import mock
    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds).resolve()
        root, home, _ = _pr_fixture_root(td)
        projects = home / "Projects"  # under projects_root a Claude chain resolves from the cache only
        projects.mkdir()
        emp = _fx_repo(projects, "emp", "acme-corp/widget", {"README.md": "x\n"})
        mine = _fx_repo(td, "mine", "pat-sample/child", {"README.md": "x\n"}, agents=False)
        _fx_cache(home, {"acme-corp/widget": emp})
        # Claude chain + not-personal repo: refused through the policy, nothing in the repo read or written.
        before = _snapshot(emp)
        seen: list[str] = []
        real_open = builtins.open

        def spy(file, *a, **kw):
            seen.append(str(file))
            return real_open(file, *a, **kw)

        with _pr_context(root, home, CLAUDE_DET), mock.patch("builtins.open", spy), mock.patch("io.open", spy):
            rc, out = _quiet(cmd_init_frame, str(emp))
        assert rc == 4 and "REFUSED" in out and "route" in out, (rc, out)
        read_in_repo = [p for p in seen if p.startswith(str(emp) + "/") and not p.startswith(str(emp / ".git"))]
        assert not read_in_repo, read_in_repo
        assert _snapshot(emp) == before, "refused init changed the employer repo"
        # Non-Claude surface + not-personal repo: the neutral render on stdout, never written.
        with _pr_context(root, home, CURSOR_DET):
            rc, out = _quiet(cmd_init_frame, str(emp))
        assert rc == 0 and "## Project intent" in out and "profile:" not in out, out
        assert "nothing was written" in out and _snapshot(emp) == before
        assert workspace_leak_hits(render_project_intent(neutral=True)) == []
        assert workspace_leak_hits(render_project_intent(neutral=False)), "workspace render should be flagged"
        # Claude chain + personal repo: PROJECT.md and the AGENTS.md pointer are written.
        with _pr_context(root, home, CLAUDE_DET):
            rc, out = _quiet(cmd_init_frame, str(mine))
            assert rc == 0 and (mine / PROJECT_FILE).is_file(), out
            assert POINTER_RE.search((mine / "AGENTS.md").read_text(encoding="utf-8"))
            f = lint_repo(mine, CLAUDE_DET)
            assert not _levels(f, "ERROR"), f  # a fresh frame is fine at discover...
            pm = mine / PROJECT_FILE
            pm.write_text(pm.read_text(encoding="utf-8").replace("lifecycle: discover", "lifecycle: define"),
                          encoding="utf-8")
            f = lint_repo(mine, CLAUDE_DET)
            assert any("[HUMAN" in m for m in _levels(f, "ERROR")), f  # ...and fails from define onward
            pm.write_text(_fx_intent(), encoding="utf-8")
            assert not _levels(lint_repo(mine, CLAUDE_DET), "ERROR")
            (mine / "AGENTS.override.md").write_text("# override\n", encoding="utf-8")
            f = lint_repo(mine, CLAUDE_DET)
            assert any("AGENTS.override.md" in m for m in _levels(f, "ERROR")), f
            rc, _ = _quiet(cmd_init_frame, str(mine))
            assert rc == 0 and not _levels(lint_repo(mine, CLAUDE_DET), "ERROR")
            rc, out = _quiet(cmd_lint, repo=str(mine), spec=None, all_=False)
            assert rc == 0, out
            pm.write_text(_fx_intent(extra_meta="profile: nonsense\n"), encoding="utf-8")
            assert _levels(lint_repo(mine, CLAUDE_DET), "ERROR")


def _st_project_inheritance() -> None:
    global _READS
    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds).resolve()
        root, home, conduct = _pr_fixture_root(td)
        sentinel = "PARENT-SENTINEL-7f3a"
        parent = _fx_repo(td, "parent", "pat-sample/parent", {PROJECT_FILE: _fx_intent(sentinel=sentinel)})
        (parent / PROJECT_FILE).write_text(_fx_intent(sentinel="WORKTREE-ONLY"), encoding="utf-8")

        def child_of(name: str, slug: str, parent_slug: str) -> Path:
            meta = f"inherits: {parent_slug}\n"
            return _fx_repo(td, name, slug,
                            {PROJECT_FILE: f"---\nlifecycle: define\n{meta}---\n\n## Project intent\n\n"
                                           f"{CHILD_SENTENCE}\n"})

        c_ok = child_of("c-ok", "pat-sample/child", "pat-sample/parent")
        c_cross = child_of("c-cross", "pat-sample/cross", "acme-corp/widget")
        c_strict = child_of("c-strict", "pat-sample/loose", "pat-sample/strict")
        c_absent = child_of("c-absent", "pat-sample/lonely", "pat-sample/missing")
        cyc_a = child_of("cyc-a", "pat-sample/cyc-a", "pat-sample/cyc-b")
        cyc_b = child_of("cyc-b", "pat-sample/cyc-b", "pat-sample/cyc-a")
        d = [child_of(f"d{i}", f"pat-sample/d{i}", f"pat-sample/d{i + 1}") for i in range(5)]
        cache = {"pat-sample/parent": parent, "pat-sample/cyc-a": cyc_a, "pat-sample/cyc-b": cyc_b}
        cache.update({f"pat-sample/d{i}": d[i] for i in range(5)})
        with _pr_context(root, home, CLAUDE_DET):
            _fx_cache(home, cache)
            f = lint_repo(c_ok, CLAUDE_DET)
            assert not _levels(f, "ERROR"), f
            assert _READS == [(str(parent), "origin/HEAD")], _READS  # origin/HEAD preferred over the tree
            _READS = []
            f = lint_repo(c_cross, CLAUDE_DET)
            assert any("cross-owner" in m for m in _levels(f, "ERROR")) and _READS == [], (f, _READS)
            f = lint_repo(c_strict, CLAUDE_DET)
            assert any("looser" in m for m in _levels(f, "ERROR")) and _READS == [], (f, _READS)
            f = lint_repo(c_absent, CLAUDE_DET)
            assert not _levels(f, "ERROR") and any("not on this device" in m for m in _levels(f, "WARN")), f
            rc, _ = _quiet(cmd_lint, repo=str(c_absent), spec=None, all_=False)
            assert rc == 0
            f = lint_repo(cyc_a, CLAUDE_DET)
            assert any("cycle" in m for m in _levels(f, "ERROR")), f
            f = lint_repo(d[0], CLAUDE_DET)
            assert any("deeper than" in m for m in _levels(f, "ERROR")), f
            # A missing origin/HEAD falls back to the working tree with a WARN.
            _run_fixture_git(["symbolic-ref", "--delete", "refs/remotes/origin/HEAD"], parent, _fixture_env(home))
            _READS = []
            f = lint_repo(c_ok, CLAUDE_DET)
            assert _READS == [(str(parent), "working-tree")] and any("working tree" in m for m in _levels(f, "WARN"))
        # Parent intent text is never written anywhere outside the parent checkout.
        for p in td.rglob("*"):
            if p.is_file() and not str(p).startswith(str(parent)):
                assert sentinel.encode() not in p.read_bytes(), f"parent text cached at {p}"


def _st_provenance() -> None:
    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds).resolve()
        root, home, _ = _pr_fixture_root(td)
        approved = _fx_intent(extra_meta="approval: approved 2026-01-02 by Pat\n")
        cases = [
            ("cursor", "Co-authored-by: Cursor <cursoragent@cursor.com>", True, "ERROR", "BLOCKED"),
            ("codex", "Workspace-Agent: codex", True, "ERROR", "BLOCKED"),
            ("claude", "Co-Authored-By: Claude <noreply@anthropic.com>", True, "ERROR", "BLOCKED"),
            ("nolane", "", False, "WARN", "provenance unknown"),
            ("human", "", True, None, None),
        ]
        with _pr_context(root, home, CLAUDE_DET):
            for name, trailer, lane, level, needle in cases:
                msg = "intent: approve" + (f"\n\n{trailer}\n" if trailer else "\n")
                repo = _fx_repo(td, f"prov-{name}", f"pat-sample/prov-{name}", {PROJECT_FILE: approved},
                                msg=msg, lane=lane)
                f = lint_repo(repo, CLAUDE_DET)
                prov = [(lvl, m) for lvl, m in f if "provenance" in m or "BLOCKED" in m]
                if level is None:
                    assert not prov and not _levels(f, "ERROR"), (name, f)
                else:
                    assert any(lvl == level and needle in m for lvl, m in prov), (name, f)
            # The gate refuses a spec whose approval came from an agent-marked commit.
            spec_text = "---\nprofile: personal-solo\napproval: approved 2026-01-02 by Pat\n---\n# s\n"
            repo = _fx_repo(td, "gate", "pat-sample/gate", {"docs/INTENT.md": spec_text},
                            msg="spec\n\nCo-authored-by: Cursor <cursoragent@cursor.com>\n", lane=True)
            rc, out = _quiet(cmd_gate, repo / "docs" / "INTENT.md")
            assert rc == 1 and "BLOCKED" in out, out
        # Employer intent accepts only `approved via PR <n>` (read by a non-Claude surface).
        with _pr_context(root, home, CURSOR_DET):
            ok = _fx_repo(td, "emp-pr", "acme-corp/pr-ok",
                          {PROJECT_FILE: _fx_intent(extra_meta="approval: approved via PR 12\n")})
            assert not _levels(lint_repo(ok, CURSOR_DET), "ERROR")
            bad = _fx_repo(td, "emp-date", "acme-corp/pr-bad", {PROJECT_FILE: approved})
            assert any("approved via PR" in m for m in _levels(lint_repo(bad, CURSOR_DET), "ERROR"))
        # A Claude chain never lints an employer repo: the policy routes it.
        with _pr_context(root, home, CLAUDE_DET):
            f = lint_repo(ok, CLAUDE_DET)
            assert f and f[0][0] == "REFUSED", f


def _st_approve_and_record() -> None:
    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds).resolve()
        root, home, _ = _pr_fixture_root(td)
        mine = _fx_repo(td, "mine", "pat-sample/appr", {PROJECT_FILE: _fx_intent()})
        emp = _fx_repo(td, "emp", "acme-corp/rec", {"docs/INTENT.md": "x\n"})
        with _pr_context(root, home, CLAUDE_DET, human=False):
            rc, out = _quiet(cmd_approve, repo=str(mine), spec=None, by="Pat", note=None)
            assert rc == 4 and "human" in out, out
        with _pr_context(root, home, CURSOR_DET, human=True):
            rc, out = _quiet(cmd_approve, repo=str(mine), spec=None, by="Pat", note=None)
            assert rc == 0 and "approval: approved " in (mine / PROJECT_FILE).read_text(encoding="utf-8"), out
            (emp / PROJECT_FILE).write_text(_fx_intent(), encoding="utf-8")
            rc, out = _quiet(cmd_approve, repo=str(emp), spec=None, by="Pat", note=None)
            assert rc == 4 and "approved via PR" in out, out
            (emp / PROJECT_FILE).unlink()
            rc, out = _quiet(cmd_next, str(mine))
            assert rc == 0 and "next (define)" in out, out
        # verify --record: an employer record lands outside the repo; the repo stays byte-identical.
        spec_text = ("---\nprofile: p\napproval: approved via PR 3\n---\n## Fidelity / acceptance checklist\n\n"
                     "- [ ] secret-label-alpha -- measure: python3 09-tools/none.py\n"
                     "- [ ] reviewed -- measure: human: look\n")
        (emp / "docs" / "INTENT.md").write_text(spec_text, encoding="utf-8")
        before = _snapshot(emp)
        with _pr_context(root, home, CURSOR_DET):
            rc, out = _quiet(cmd_verify, emp / "docs" / "INTENT.md", False, str(emp), automated=True, record=True)
        dest = home / ".config" / "snds-workspace" / "state" / "telemetry" / "acme-corp" / "rec" / "verify.jsonl"
        assert dest.is_file(), out
        assert _snapshot(emp) == before, "verify --record changed the employer repo (incl. .git/)"
        rec = json.loads(dest.read_text(encoding="utf-8").splitlines()[-1])
        assert {"surface", "family", "via", "device"} <= set(rec) and rec["family"] == "cursor", rec
        assert "secret-label-alpha" not in dest.read_text(encoding="utf-8") and "label" not in rec["checks"][0]
        # A personal record sits beside the spec, with labels.
        (mine / "docs").mkdir(exist_ok=True)
        (mine / "docs" / "INTENT.md").write_text(spec_text, encoding="utf-8")
        with _pr_context(root, home, CLAUDE_DET):
            rc, out = _quiet(cmd_verify, mine / "docs" / "INTENT.md", False, str(mine), automated=True, record=True)
        local = mine / "docs" / "INTENT.verify.jsonl"
        assert local.is_file() and "secret-label-alpha" in local.read_text(encoding="utf-8"), out
        assert json.loads(local.read_text(encoding="utf-8"))["device"] == "dev-a"


def _rem_text() -> str:
    return (FIXTURES / "remediation-spec.md").read_text(encoding="utf-8")


def _rem_errors(text: str, **kw) -> list[str]:
    return _levels(lint_remediation(parse_spec(text), **kw), "ERROR")


def _st_remediation_lint() -> None:
    base = _rem_text()
    assert not _rem_errors(base), _rem_errors(base)
    planted = {
        "duplicate id": base.replace("| F-003 | minor", "| F-002 | minor"),
        "RESOLVED without closed_by": base.replace("| C-002 | abc1234 |", "| C-002 | - |"),
        "RESOLVED without closure": base.replace("| C-002 | abc1234 |", "| - | abc1234 |"),
        "DEFERRED without revisit": base.replace("| on: the v2 branch opens |", "| - |"),
        "DEFERRED without reason": base.replace("| not worth it before v2 |", "| - |"),
        "closed with an OPEN row": base.replace("status: open", "status: closed"),
        "implementor without packet": base.replace("### T1 — Make", "### T9 — Make"),
        "preserve without until": base.replace("| on: a squash release |", "| |"),
        "command in a closure cell": base.replace("| C-001 | - | - | low |", "| python3 x.py | - | - | low |"),
        "unknown closure": base.replace("| C-001 | - | - | low |", "| C-009 | - | - | low |"),
        "bad severity": base.replace("| F-001 | High |", "| F-001 | Urgent |"),
        "bad origin": base.replace("| widget-audit#A1 |", "| widget audit A1 |"),
        "packet missing a field": base.replace("- bail point: the fix needs a change under migrations/\n", ""),
        "packet names an unknown finding": base.replace("- findings: F-001", "- findings: F-001, F-042"),
        "blocked_by that does not resolve": base.replace("status: open", "status: open\nblocked_by: nowhere.md"),
    }
    for name, text in planted.items():
        assert text != base, f"{name}: the plant did not apply"
        assert _rem_errors(text, spec_path=FIXTURES / "remediation-spec.md"), f"{name}: no ERROR"
    # a11y severities map 1:1; namespaced origins with the same ID coexist.
    assert [norm_sev(x) for x in ("blocker", "major", "minor", "nit")] == list(SEVERITIES)
    twin = base.replace("| F-002 | Medium | RESOLVED | widget-audit#A2 |",
                        "| F-002 | Medium | RESOLVED | process-rigor-gaps#R2 |").replace(
        "| F-001 | High | OPEN | widget-audit#A1 |", "| F-001 | High | OPEN | workspace-automation-review#R2 |")
    assert not _rem_errors(twin), _rem_errors(twin)
    # An expired preserve entry and a passed revisit WARN, not ERROR.
    old = base.replace("| on: a squash release |", "| 2001-01-01 |")
    f = lint_remediation(parse_spec(old))
    assert not _levels(f, "ERROR") and any("expired" in m for m in _levels(f, "WARN")), f
    # --since: a finding id that vanished is a silent drop (temp git repo).
    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds).resolve()
        repo, env = _new_repo(td, "since")
        h = _History(repo, env)
        h.commit("main", "spec", {"docs/INTENT-remediation.md": base})
        h.flush()
        sp = repo / "docs" / "INTENT-remediation.md"
        sp.parent.mkdir(parents=True)
        dropped = "\n".join(ln for ln in base.splitlines() if not ln.startswith("| F-003 ")) + "\n"
        sp.write_text(dropped, encoding="utf-8")
        f = lint_remediation(parse_spec(dropped), sp, since="main")
        assert any("silent drop" in m and "F-003" in m for m in _levels(f, "ERROR")), f
        sp.write_text(base, encoding="utf-8")
        assert not _rem_errors(base, spec_path=sp, since="main")


def _st_remediation_gate_loop() -> None:
    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds).resolve()
        root, home, _ = _pr_fixture_root(td)
        base = _rem_text()
        up_unfit = base  # F-001 is an OPEN High: Unfit
        up_fit = base.replace("| F-001 | High | OPEN |", "| F-001 | High | DEFERRED |").replace(
            "| C-001 | - | - | low |", "| C-001 | waiting on CI | on: CI exists | low |")
        down = base.replace("status: open", "status: open\nblocked_by: upstream.md")
        repo = _fx_repo(td, "gate", "pat-sample/gate", {"docs/INTENT.md": down, "docs/upstream.md": up_unfit})
        spec = repo / "docs" / "INTENT.md"
        with _pr_context(root, home, CURSOR_DET):
            rc, out = _quiet(cmd_gate, spec)
            assert rc == 1 and "upstream upstream.md is Unfit" in out, out
            (repo / "docs" / "upstream.md").write_text(up_fit, encoding="utf-8")
            rc, out = _quiet(cmd_gate, spec)
            assert rc == 0, out
            # Loop-breaker: 3 FAIL records naming T1 since its newest Previous attempts entry.
            rec = spec.with_name("INTENT.verify.jsonl")
            fail = {"ts": "2026-01-05T00:00:00Z", "checks": [{"id": 1, "label": "T1 lint gate", "status": "FAIL"}]}
            rec.write_text("\n".join(json.dumps(fail) for _ in range(3)) + "\n", encoding="utf-8")
            rc, out = _quiet(cmd_worktree_add, spec, "T1", str(repo))
            assert rc == 1 and "loop-breaker" in out, out
            rc, out = _quiet(cmd_ready, spec)
            assert "HELD (loop-breaker)" in out and "no implementor tasks ready" in out, out
            spec.write_text(spec.read_text(encoding="utf-8").replace(
                "- previous attempts: none", "- previous attempts: 2026-01-06 — the log pipe swallowed the exit code"),
                encoding="utf-8")
            assert loop_breaker(spec, load_spec(spec), "T1")[0] is False
            assert not (td / "gate.intent-T1").exists()


def _st_remediation_recon() -> None:
    import builtins
    from unittest import mock
    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds).resolve()
        root, home, _ = _pr_fixture_root(td)
        projects = home / "Projects"
        projects.mkdir()
        files = {
            "package.json": json.dumps({"name": "w", "scripts": {"test": "node t.js", "build": "node b.js"}}),
            "package-lock.json": "{}\n", "README.md": "# w\n", ".env": "TOKEN=synthetic\n",
            "src/big.py": "x = 1\n" * 1200, "src/a.py": "a = 1\n" * 10, "src/b.ts": "let b = 1\n",
            "src/c.sh": "echo c\n", "tests/test_a.py": "def test_a():\n    pass\n",
            ".github/workflows/ci.yml": "on: push\n",
        }
        mine = _fx_repo(td, "mine", "pat-sample/recon", files)
        emp = _fx_repo(projects, "emp", "acme-corp/recon", files)
        _fx_cache(home, {"acme-corp/recon": emp})
        seen: list[str] = []
        real_open = builtins.open

        def spy(file, *a, **kw):
            seen.append(str(file))
            return real_open(file, *a, **kw)

        # Claude chain + employer repo: routed through the content-read policy; the tree stays byte-identical.
        before = _snapshot(emp)
        with _pr_context(root, home, CLAUDE_DET), mock.patch("builtins.open", spy), mock.patch("io.open", spy):
            rc, out = _quiet(cmd_init_recon, str(emp))
        assert rc == 4 and "REFUSED" in out and "route" in out, (rc, out)
        read_in_repo = [p for p in seen if p.startswith(str(emp) + "/") and not p.startswith(str(emp / ".git"))]
        assert not read_in_repo, read_in_repo
        assert _snapshot(emp) == before, "a routed recon changed the employer repo (incl. .git/)"
        # Non-Claude surface + employer repo: the card goes to stdout; nothing is written.
        with _pr_context(root, home, CURSOR_DET):
            rc, out = _quiet(cmd_init_recon, str(emp))
        assert rc == 0 and RECON_START in out and "nothing was written" in out, out
        assert _snapshot(emp) == before, "an employer recon wrote into the repo"
        # Claude chain + personal repo: stored in docs/; .env never opened; the card holds a count, not names.
        seen.clear()
        with _pr_context(root, home, CLAUDE_DET), mock.patch("builtins.open", spy), mock.patch("io.open", spy):
            rc, out = _quiet(cmd_init_recon, str(mine))
        assert rc == 0 and "wrote recon card" in out, out
        assert not [p for p in seen if p.endswith("/.env")], "recon opened a secret-shaped file"
        card = (mine / "docs" / "RECON.md").read_text(encoding="utf-8")
        head = _git(["rev-parse", "HEAD"], mine).stdout.strip()
        assert f"source_sha: `{head}`" in card, card
        assert "| secret-shaped filenames | 1 (" in card and ".env" not in card, card
        assert ".env" in out, "secret-shaped names belong on stdout"
        for needle in ("src/big.py", "package.json", "npm test", "npm run build", ".github/workflows/ci.yml",
                       "three or more languages", "| known |", "| inferred |", "| assumed |"):
            assert needle in card, (needle, card)
        # A re-run regenerates the block in place; --spec targets a remediation spec's Recon section.
        spec = mine / "docs" / "INTENT-remediation.md"
        spec.write_text(_rem_text(), encoding="utf-8")
        with _pr_context(root, home, CLAUDE_DET):
            assert _quiet(cmd_init_recon, str(mine))[0] == 0
            assert (mine / "docs" / "RECON.md").read_text(encoding="utf-8").count(RECON_START) == 1
            rc, _ = _quiet(cmd_init_recon, str(mine), spec=str(spec))
            text = spec.read_text(encoding="utf-8")
            assert rc == 0 and text.count(RECON_START) == 1 and text.index(RECON_START) < text.index("## Findings")
            assert parse_remediation(parse_spec(text))["recon"]["source_sha"] == head
            assert not _levels(lint_remediation(parse_spec(text), spec), "ERROR")


def _st_remediation_packet() -> None:
    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds).resolve()
        root, home, _ = _pr_fixture_root(td)
        repo = _fx_repo(td, "widget", "pat-sample/widget", {"docs/INTENT-remediation.md": _rem_text()})
        spec = repo / "docs" / "INTENT-remediation.md"
        with _pr_context(root, home, CURSOR_DET):
            rc, out = _quiet(cmd_packet, spec, "T1")
            golden = (FIXTURES / "remediation-packet.golden.md").read_text(encoding="utf-8")
            assert rc == 0 and out == golden, out
            assert packet_problems(out) == []
            # A finding id resolves to its packet; a finding without one gets a synthesized brief.
            assert _quiet(cmd_packet, spec, "F-001")[1] == golden
            rc, out = _quiet(cmd_packet, spec, "F-003")
            assert rc == 0 and "synthesized" in out and "F-003" in out and packet_problems(out) == [], out
            assert _quiet(cmd_packet, spec, "T7")[0] == 2
        # A brief that leans on context the cold agent lacks is refused.
        leaning = _rem_text().replace("- context: The build", "- context: see the spec and [[notes]]; The build")
        spec.write_text(leaning, encoding="utf-8")
        with _pr_context(root, home, CURSOR_DET):
            rc, out = _quiet(cmd_packet, spec, "T1")
        assert rc == 1 and "not self-contained" in out, out
        # A Claude chain never reads an employer spec: routed before any read.
        emp = _fx_repo(td, "emp", "acme-corp/widget", {"docs/INTENT-remediation.md": _rem_text()})
        with _pr_context(root, home, CLAUDE_DET):
            rc, out = _quiet(cmd_packet, emp / "docs" / "INTENT-remediation.md", "T1")
        assert rc == 4 and "REFUSED" in out, out


def _st_remediation_verdict() -> None:
    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds).resolve()
        root, home, _ = _pr_fixture_root(td)
        base = _rem_text()
        rel = "docs/INTENT-remediation.md"
        fixed = base.replace("| F-001 | High | OPEN |", "| F-001 | High | RESOLVED |").replace(
            "| C-001 | - | - | low |", "| C-002 | feedc0de | - | low |")
        dropped = "\n".join(ln for ln in base.splitlines() if not ln.startswith("| F-003 ")) + "\n"
        reopened = base.replace("| F-002 | Medium | RESOLVED |", "| F-002 | Medium | OPEN |")
        gated = fixed.replace("| C-002 | feedc0de |", "| C-001 | feedc0de |")
        repo, env = _new_repo(td, "verdict")
        _run_fixture_git(["remote", "add", "origin", "https://github.com/pat-sample/verdict.git"], repo, env)
        h = _History(repo, env)
        m0 = h.commit("main", "remediation spec", {rel: base})
        h.commit("fix-lint", "T1: fail the build on lint errors (F-001)", {rel: fixed}, frm=m0)
        h.commit("drop", "tidy the register", {rel: dropped}, frm=m0)
        h.commit("reopen", "reopen", {rel: reopened}, frm=m0)
        h.commit("gated", "resolve F-001 with a measured closure", {rel: gated}, frm=m0)
        h.flush()
        spec = repo / rel
        spec.parent.mkdir(parents=True)
        spec.write_text(base, encoding="utf-8")
        with _pr_context(root, home, CURSOR_DET):
            rc, out = _quiet(cmd_verdict, spec)
            assert rc == 1 and "verdict: Unfit" in out and "F-001 High OPEN" in out, out
            rc, out = _quiet(cmd_verdict, spec, branch="fix-lint")
            assert rc == 0 and "verdict: Fit with gaps" in out, out
            assert "key: branch fix-lint" in out and "resolved=F-001" in out and "F-001, T1" in out, out
            rc, out = _quiet(cmd_verdict, spec, branch="drop")
            assert rc == 1 and "dropped=F-003" in out and "silent drop" in out, out
            rc, out = _quiet(cmd_verdict, spec, rng="main..reopen")
            assert rc == 1 and "regressed=F-002" in out, out
            # A High row resolved by a measure that was not run is Blocked, never a plausible Fit.
            rc, out = _quiet(cmd_verdict, spec, branch="gated")
            assert rc == 2 and "verdict: Blocked" in out and "UNRUN" in out, out
            rc, out = _quiet(cmd_verdict, spec, branch="gated", run=True)
            assert rc == 2 and "NOT_EXPOSED" in out, out  # the keyed ref is not the checkout
            rc, out = _quiet(cmd_verdict, spec, branch="nope")
            assert rc == 2 and "Blocked" in out, out
            rc, out = _quiet(cmd_verdict, spec, branch="fix-lint", as_json=True)
            doc = json.loads(out)
            assert doc["verdict"] == "Fit with gaps" and doc["tip"] and doc["resolved_in_range"] == ["F-001"], doc
        # A RESOLVED row whose allowlisted closure now fails is REGRESSED (Unfit).
        (repo / "09-tools").mkdir()
        (repo / "09-tools" / "lint_gate.py").write_text("raise SystemExit(1)\n", encoding="utf-8")
        _run_fixture_git(["add", "09-tools/lint_gate.py"], repo, env)
        spec.write_text(gated, encoding="utf-8")
        sp = parse_spec(gated)
        res = closure_results(sp, run=True, runnable=True, vroot=repo, automated=True)
        assert res.get("F-001") == "FAIL", res
        v = compute_verdict(sp, closures=res)
        assert v["verdict"] == "Unfit" and "F-001" in v["regressed"], v
        (repo / "09-tools" / "lint_gate.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
        v = compute_verdict(sp, closures=closure_results(sp, run=True, runnable=True, vroot=repo, automated=True))
        assert v["verdict"] == "Fit with gaps", v


# --- H9: scope -----------------------------------------------------------------------------

SCOPE_GOLDENS = ("claude-code.write", "cursor.pre-tool-write", "codex.apply-patch", "copilot-vscode.pre-write",
                 "windsurf.pre-write")


def _scope_spec(rows: str, extra_cols: str = "", extra_sep: str = "") -> str:
    return ("---\ntitle: scope fixture\nprofile: personal-solo\napproval: pending\n---\n\n# scope fixture\n\n"
            "## Task graph\n\n"
            f"| id | role | isolation | depends_on | status | writes | forbids{extra_cols} |\n"
            f"|---|---|---|---|---|---|---{extra_sep}|\n" + rows + "\n## Changelog\n\n- 2026-01-01 — created\n")


def scope_golden(name: str, *, path: str, cwd: str) -> dict:
    text = (TOOLS / "fixtures" / "wall_guard" / "goldens" / f"{name}.json").read_text(encoding="utf-8")
    for key, val in (("PATH", path), ("CWD", cwd)):
        text = text.replace("{" + key + "}", json.dumps(val)[1:-1])
    return json.loads(text)


def _ws_shape(top: Path) -> None:
    """The plain-file shape intent_scope.is_workspace reads (a synthetic workspace checkout)."""
    for rel in ("AGENTS.md", "02-shared-references/surfaces.json", "09-tools/intent-run.py"):
        (top / rel).parent.mkdir(parents=True, exist_ok=True)
        (top / rel).write_text("{}\n" if rel.endswith(".json") else "# fixture\n", encoding="utf-8")


def _st_scope_lint() -> None:
    gi = intent_scope.globs_intersect
    for p, q, want in (("03-skills/*/SKILL.md", "03-skills/x/SKILL.md", True), ("a/*.md", "a/*.py", False),
                       ("a/**/b.md", "a/b.md", True), ("a/*", "a/x/y", False), ("x/**/y", "x/**/z", False)):
        assert gi(p, q) is want, (p, q)
    rows = ("| T0 | coordinator | n/a | - | | docs/INTENT.md | |\n"
            "| T1 | implementor | worktree | T0 | | src/a/**, data.json[rows.a] | |\n"
            "| T2 | implementor | worktree | T0 | | src/a/x.py | |\n"
            "| T3 | implementor | worktree | T0 | | src/b/**, data.json[rows.b] | |\n"
            "| T4 | implementor | worktree | T1 | | src/a/y.py | |\n"
            "| T5 | implementor | worktree | T0 | verified | src/b/z.py | |\n"
            "| V1 | verifier | read-only | T1, T2, T3 | | notes.md | |\n")
    errs = _levels(lint_spec(parse_spec(_scope_spec(rows))), "ERROR")
    assert any("T1 and T2" in e and "src/a/**" in e for e in errs), errs      # parallel, overlapping
    assert not any("T1 and T3" in e for e in errs), errs                       # disjoint selectors
    assert not any("T4" in e for e in errs), errs                              # T4 depends on T1
    assert not any("T5" in e for e in errs), errs                              # verified: no longer runs
    assert any("verifier V1 declares writes" in e for e in errs), errs
    assert len(errs) == 2, errs
    # An explicit wave column overrides the dependency depth; prose tokens are never compared.
    rows = ("| T1 | implementor | worktree | - | | lib/**, per item | | 1 |\n"
            "| T2 | implementor | worktree | T9 | | lib/core.py | | 2 |\n"
            "| T3 | implementor | worktree | - | | per item | | 1 |\n")
    errs = _levels(lint_spec(parse_spec(_scope_spec(rows, " | wave", "|---"))), "ERROR")
    assert errs == [], errs
    with tempfile.TemporaryDirectory() as tds:
        sp = Path(tds) / "INTENT.md"
        sp.write_text(_scope_spec("| T1 | implementor | worktree | - | | a/** | |\n"
                                  "| T2 | implementor | worktree | - | | a/b.md | |\n")
                      .replace("approval: pending", "approval: approved 2026-01-01 by Sean"), encoding="utf-8")
        rc, out = _quiet(cmd_gate, sp)
        assert rc == 1 and "not disjoint" in out, out


def _scope_repo(td: Path) -> tuple[Path, dict, Path, str, str]:
    repo, env = _new_repo(td, "scoped")
    _run_fixture_git(["remote", "add", "origin", "https://github.com/pat-sample/scoped.git"], repo, env)
    rel = "docs/INTENT.md"
    spec_text = _scope_spec("| T1 | implementor | worktree | - | | src/**, docs/notes.md | src/secret/** |\n"
                            "| T2 | implementor | worktree | T1 | | per item | `vendor/` (never) |\n")
    h = _History(repo, env)
    m0 = h.commit("main", "base", {rel: spec_text, "src/a.py": "a\n", "README.md": "r\n"})
    h.commit("intent/T1", "T1 work", {"src/a.py": "a2\n", "src/b.py": "b\n"}, frm=m0)
    m2 = h.commit("stray", "T1 strays", {"src/a.py": "a3\n", "README.md": "r2\n", "src/secret/k.txt": "k\n"},
                  frm=m0)
    h.commit("prose", "T2", {"src/c.py": "c\n", "vendor/lib.js": "v\n"}, frm=m0)
    h.flush()
    spec = repo / rel
    spec.parent.mkdir(parents=True)
    spec.write_text(spec_text, encoding="utf-8")
    return repo, env, spec, h.sha(m0), h.sha(m2)


def _st_scope_branch_range() -> None:
    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds).resolve()
        root, home, _ = _pr_fixture_root(td)
        repo, env, spec, base, stray = _scope_repo(td)
        with _pr_context(root, home, CURSOR_DET):
            # The task comes from the intent/<ID> branch name; everything stays inside writes.
            rc, out = _quiet(cmd_scope_diff, spec=str(spec), task=None, branch="intent/T1", base="main",
                             rng=None, repo=str(repo))
            assert rc == 0 and "task T1" in out and "0 finding(s)" in out and "2 path(s)" in out, out
            rc, out = _quiet(cmd_scope_diff, spec=str(spec), task="T1", branch="stray", base="main", rng=None,
                             repo=str(repo))
            assert rc == 1 and "OUTSIDE README.md" in out and "FORBIDDEN src/secret/k.txt" in out, out
            assert "OUTSIDE src/a.py" not in out, out
            rc, out = _quiet(cmd_scope_diff, spec=str(spec), task="T1", branch=None, base=None,
                             rng=f"{base}..{stray}", repo=str(repo), as_json=True)
            doc = json.loads(out)
            kinds = sorted((f["kind"], f["path"]) for f in doc["findings"])
            assert rc == 1 and kinds == [("forbidden", "src/secret/k.txt"), ("outside-writes", "README.md")], doc
            assert doc["spec"].startswith("docs/INTENT.md @ "), doc   # read at the tip, not the work tree
            # Prose writes: only forbids are checked, and the note says so.
            rc, out = _quiet(cmd_scope_diff, spec=str(spec), task="T2", branch="prose", base="main", rng=None,
                             repo=str(repo))
            assert rc == 1 and "FORBIDDEN vendor/lib.js" in out and "OUTSIDE" not in out and "prose" in out, out
            rc, out = _quiet(cmd_scope_diff, spec=str(spec), task="T1", branch=None, base=None,
                             rng="main..main", repo=str(repo))
            assert rc == 3 and "nothing changed" in out, out
            rc, out = _quiet(cmd_scope_diff, spec=str(spec), task="T1", branch="nope", base="main", rng=None,
                             repo=str(repo))
            assert rc == 2, out
            rc, out = _quiet(cmd_scope_diff, spec=str(spec), task="T9", branch="stray", base="main", rng=None,
                             repo=str(repo))
            assert rc == 2 and "unknown task" in out, out


def _st_scope_check_path() -> None:
    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds).resolve()
        home = td / "home"
        repo, env = _new_repo(td, "ws")
        _ws_shape(repo)
        spec = repo / "docs" / "INTENT.md"
        spec.parent.mkdir(parents=True)
        spec.write_text(_scope_spec("| T1 | implementor | worktree | - | | src/**, docs/ | src/gen/** | |\n"
                                    "| T2 | implementor | worktree | - | | lib/** | | true |\n",
                                    " | enforce", "|---"), encoding="utf-8")
        target = repo / "src" / "a.py"
        res = intent_scope.check_path(target, home=home)
        assert res["status"] == "no-task" and not res["findings"], res
        ptr = intent_scope.write_pointer(repo, spec, "T1", home=home)
        assert ptr == repo / ".workspace" / "state" / "active-task", ptr
        assert intent_scope.check_path(target, home=home)["status"] == "in-scope"
        assert intent_scope.check_path(repo / "docs" / "x.md", home=home)["status"] == "in-scope"
        res = intent_scope.check_path("README.md", cwd=str(repo), home=home)
        assert res["status"] == "outside" and res["findings"][0]["kind"] == "outside-writes" and not res["block"], res
        res = intent_scope.check_path(repo / "src" / "gen" / "x.py", home=home)
        assert [f["kind"] for f in res["findings"]] == ["forbidden"], res
        assert intent_scope.check_path(td / "elsewhere.txt", home=home)["status"] == "no-repo"
        with _pr_context(td, home, CURSOR_DET):
            rc, out = _quiet(cmd_scope_check_path, str(repo / "README.md"))
            assert rc == 0 and "report-only" in out and "outside-writes" in out, out   # report-only exit 0
            intent_scope.write_pointer(repo, spec, "T2", home=home)
            rc, out = _quiet(cmd_scope_check_path, str(repo / "README.md"))
            assert rc == 1 and "[enforce]" in out, out                                # enforce: true
            rc, out = _quiet(cmd_scope_check_path, str(repo / "lib" / "x.py"))
            assert rc == 0 and out == "", out
            rc, out = _quiet(cmd_scope_pointer, "show", repo=str(repo))
            assert "active task: T2" in out, out
            rc, out = _quiet(cmd_scope_pointer, "clear", repo=str(repo))
            assert rc == 0 and "cleared" in out and not ptr.exists(), out
        # Fails open: a spec that vanished, a task that no longer exists, a zero budget.
        intent_scope.write_pointer(repo, spec, "T1", home=home)
        assert intent_scope.check_path(repo / "README.md", home=home, budget=0.0)["status"] == "timeout"
        intent_scope.write_pointer(repo, spec, "T9", home=home)
        res = intent_scope.check_path(repo / "README.md", home=home)
        assert res["status"] == "error" and not res["block"], res
        intent_scope.write_pointer(repo, spec, "T1", home=home)
        spec.rename(spec.with_suffix(".gone"))
        res = intent_scope.check_path(repo / "README.md", home=home)
        assert res["status"] == "error" and not res["findings"], res
        spec.with_suffix(".gone").rename(spec)
        # Budget: each warm check stays under 50 ms.
        times = [intent_scope.check_path(repo / "src" / f"f{i}.py", home=home)["elapsed_ms"] for i in range(25)]
        assert max(times[1:]) < intent_scope.CHECK_BUDGET_S * 1000, times
        # The pointer is gitignored state in the workspace: git never lists it.
        (repo / ".gitignore").write_text(".workspace/\n", encoding="utf-8")
        st = _run_fixture_git(["status", "--porcelain", "--untracked-files=all"], repo, env)
        assert ".workspace" not in st, st


def _st_scope_employer_pointer() -> None:
    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds).resolve()
        root, home, _ = _pr_fixture_root(td)
        spec_text = _scope_spec("| T1 | implementor | worktree | - | | src/** | |\n")
        repo = _fx_repo(td, "widget", "acme-corp/widget", {"src/a.py": "a\n", "docs/INTENT.md": spec_text},
                        agents=False)
        before = _snapshot(repo)
        ptr = intent_scope.write_pointer(repo, repo / "docs" / "INTENT.md", "T1", home=home)
        want = home / ".config" / "snds-workspace" / "state" / "telemetry" / "acme-corp" / "widget" / "active-task"
        assert ptr == want and not ptr.resolve().is_relative_to(repo), ptr
        res = intent_scope.check_path(repo / "README.md", home=home)
        assert res["status"] == "outside", res
        log = intent_scope.log_finding(res, host="cursor", home=home)
        assert log == want.with_name("scope.jsonl"), log
        row = json.loads(log.read_text(encoding="utf-8").splitlines()[-1])
        assert "path" not in row and len(row["path_sha256"]) == 16, row             # a hash, never the path
        out = io.StringIO()
        payload = scope_golden("cursor.pre-tool-write", path=str(repo / "README.md"), cwd=str(repo))
        results = intent_scope.report_payload("cursor", payload, table=_pr().load_table("surfaces"), home=home,
                                              err=out)
        assert [r["status"] for r in results] == ["outside"] and "ws-scope" in out.getvalue(), results
        assert _snapshot(repo) == before, "the employer tree changed"
        # A Claude chain is refused before reading anything for set / branch / range.
        with _pr_context(root, home, CLAUDE_DET):
            rc, msg = _quiet(cmd_scope_pointer, "set", task="T1", spec=str(repo / "docs" / "INTENT.md"),
                             repo=str(repo))
            assert rc == 4 and "REFUSED" in msg, msg
            rc, msg = _quiet(cmd_scope_diff, spec=None, task="T1", branch=None, base=None, rng="HEAD..HEAD",
                             repo=str(repo))
            assert rc == 4 and "REFUSED" in msg, msg
        # Refused outright: a pointer path that would land inside a non-workspace repo.
        try:
            intent_scope.write_pointer(repo, repo / "docs" / "INTENT.md", "T1", home=repo)
            raise AssertionError("pointer written inside the employer repo")
        except PermissionError:
            pass
        assert _snapshot(repo) == before, "the employer tree changed"


def _st_scope_denylist_contract() -> None:
    """v1.0 mechanics: sensitive denylist unless explicitly owned, Preserve paths, generated globs,
    `\\|` in a glob cell, contract-gated fan-out in ready, and scope on status."""
    head = ("---\ntitle: t\nprofile: personal-solo\napproval: approved 2026-01-01 by Sean\n"
            "generated: gen/**, docs/registry.json\ncontract: api/contract.md\n---\n\n# t\n\n")
    text = head + ("## Preserve\n\n| glob | why | until |\n|---|---|---|\n| migrations/** | history | on: squash |\n\n"
                   "## Task graph\n\n| id | role | isolation | depends_on | status | writes | forbids |\n"
                   "|---|---|---|---|---|---|---|\n"
                   "| T1 | implementor | worktree | - | | src/**, **/package.json, .github/workflows/** | |\n"
                   "| T2 | implementor | worktree | - | | lib/a\\|b.py | |\n")
    sc = intent_scope.spec_scope(text, "T1")
    kinds = {p: [f["kind"] for f in intent_scope.evaluate(sc, p)] for p in (
        "src/package-lock.json", "src/package.json", ".github/workflows/ci.yml", "migrations/001.sql",
        "gen/out.txt", "docs/registry.json", "src/.env.local", "src/ok.py")}
    assert kinds == {"src/package-lock.json": ["sensitive"], "src/package.json": [], ".github/workflows/ci.yml": [],
                     "migrations/001.sql": ["preserve", "outside-writes"], "gen/out.txt": [],
                     "docs/registry.json": [], "src/.env.local": ["sensitive"], "src/ok.py": []}, kinds
    assert [e["path"] for e in intent_scope.spec_scope(text, "T2")["writes"]] == ["lib/a|b.py"]
    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds).resolve()
        root, home, _ = _pr_fixture_root(td)
        repo, env = _new_repo(td, "fan")
        _run_fixture_git(["remote", "add", "origin", "https://github.com/pat-sample/fan.git"], repo, env)
        h = _History(repo, env)
        m0 = h.commit("main", "spec", {"docs/INTENT.md": text})
        h.commit("intent/T1", "T1", {"src/package-lock.json": "{}\n"}, frm=m0)
        h.flush()
        spec = repo / "docs" / "INTENT.md"
        spec.parent.mkdir(parents=True)
        spec.write_text(text, encoding="utf-8")
        with _pr_context(root, home, CURSOR_DET):
            rc, out = _quiet(cmd_ready, spec)
            assert "HELD (contract): T2" in out and "uncommitted: api/contract.md" in out and "  T1 " in out, out
            h.commit("main", "contract", {"api/contract.md": "# contract\n"}, frm=h.sha(m0))
            h.flush()
            (repo / "api").mkdir()
            (repo / "api" / "contract.md").write_text("# contract\n", encoding="utf-8")
            _run_fixture_git(["add", "api/contract.md", "docs/INTENT.md"], repo, env)   # match HEAD
            rc, out = _quiet(cmd_ready, spec)
            assert "HELD" not in out and "  T1 " in out and "  T2 " in out, out
            save_state(spec, {"worktrees": {"T1": {"path": str(repo), "branch": "intent/T1", "repo": str(repo)}}})
            rc, out = _quiet(cmd_status, spec)
            assert re.search(r"T1 .* scope=fail", out) and re.search(r"T2 .* scope=unchecked", out), out
            rc, out = _quiet(cmd_scope_diff, spec=str(spec), task=None, branch="intent/T1", base="main", rng=None,
                             repo=str(repo))
            assert rc == 1 and "SENSITIVE src/package-lock.json" in out, out


def _st_scope_accelerator_parity() -> str:
    """The five hosts' golden pre-write payloads reach the same check with the same result."""
    with tempfile.TemporaryDirectory() as tds:
        td = Path(tds).resolve()
        home = td / "home"
        repo, _env = _new_repo(td, "ws")
        _ws_shape(repo)
        spec = repo / "docs" / "INTENT.md"
        spec.parent.mkdir(parents=True)
        spec.write_text(_scope_spec("| T1 | implementor | worktree | - | | src/** | src/gen/** |\n"), encoding="utf-8")
        intent_scope.write_pointer(repo, spec, "T1", home=home)
        table = _pr().load_table("surfaces")
        seen = {}
        for rel in ("src/ok.py", "README.md", "src/gen/x.py"):
            for g in SCOPE_GOLDENS:
                payload = scope_golden(g, path=str(repo / rel), cwd=str(repo))
                paths, _cwd = intent_scope.write_paths(payload, table)
                assert paths == [str(repo / rel)], (g, paths)
                res = intent_scope.report_payload(g.split(".")[0], payload, table=table, home=home, log=False)
                seen.setdefault(rel, set()).add(json.dumps([(r["status"], [f["kind"] for f in r["findings"]])
                                                            for r in res]))
        assert all(len(v) == 1 for v in seen.values()), seen
        return f"{len(SCOPE_GOLDENS)} goldens agree on {len(seen)} paths"


SELF_TESTS = (
    ("no-git-write invariant", _st_invariant),
    ("parser cases", _st_parser),
    ("synthetic spec", _st_fixture_spec),
    ("held-spec parity", _st_held_parity),
    ("verify hardening", _st_verify),
    ("scope-audit", _st_scope_audit),
    ("project intent: frame, neutral render, pointers, Claude refusal", _st_project_frame),
    ("project intent: inheritance", _st_project_inheritance),
    ("approval provenance", _st_provenance),
    ("approve, next, verify --record", _st_approve_and_record),
    ("remediation: findings register lint (v1.0 planted cases)", _st_remediation_lint),
    ("remediation: blocked_by gate and the loop-breaker", _st_remediation_gate_loop),
    ("remediation: recon card, policy-routed and byte-identical", _st_remediation_recon),
    ("remediation: golden self-contained packet", _st_remediation_packet),
    ("remediation: branch- and range-keyed verdict", _st_remediation_verdict),
    ("scope: globs, disjoint-wave lint, read-only verifier, gate", _st_scope_lint),
    ("scope: branch- and range-keyed diff vs writes/forbids", _st_scope_branch_range),
    ("scope: --check-path, pointer, enforce, fail-open, budget", _st_scope_check_path),
    ("scope: employer pointer outside the repo, tree byte-identical", _st_scope_employer_pointer),
    ("scope: denylist, preserve, generated, contract-gated ready, status", _st_scope_denylist_contract),
    ("scope: accelerator parity across five host goldens", _st_scope_accelerator_parity),
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
    p_init.add_argument("--frame", action="store_true", help="frame PROJECT.md (project intent) in --repo")
    p_init.add_argument("--repo")
    p_init.add_argument("--neutral", action="store_true", help="the employer-safe render (no profile:)")
    p_init.add_argument("--stdout", action="store_true")
    p_init.add_argument("--inherits")
    p_init.add_argument("--inherits-context")
    p_init.add_argument("--lifecycle", default="discover")
    p_init.add_argument("--recon", action="store_true", help="a read-only recon card for --repo (H8)")
    p_init.add_argument("--spec", help="with --recon: the remediation spec whose recon block is regenerated")
    p_lint = sub.add_parser("lint")
    p_lint.add_argument("--repo")
    p_lint.add_argument("--spec")
    p_lint.add_argument("--all", action="store_true")
    p_lint.add_argument("--since", help="with --spec: fail if a finding id vanished since REF")
    p_lint.add_argument("--run-closures", action="store_true", help="re-run RESOLVED closures; a failure is REGRESSED")
    p_next = sub.add_parser("next")
    p_next.add_argument("--repo")
    p_next.add_argument("--spec", help="a remediation spec: the next finding by risk band, then severity")
    p_find = sub.add_parser("findings")
    p_find.add_argument("--spec")
    p_find.add_argument("--status", choices=FINDING_STATUSES)
    p_find.add_argument("--json", action="store_true")
    p_pk = sub.add_parser("packet")
    p_pk.add_argument("ident", help="a packet id (T<n>) or a finding id (F-NNN)")
    p_pk.add_argument("--spec")
    p_pk.add_argument("--format", choices=("prompt", "json"), default="prompt")
    p_vd = sub.add_parser("verdict")
    p_vd.add_argument("--spec")
    p_vd.add_argument("--branch")
    p_vd.add_argument("--base", help="with --branch: the ref the branch is compared against (default main)")
    p_vd.add_argument("--range", dest="rng")
    p_vd.add_argument("--run", action="store_true", help="run RESOLVED rows' closures (keyed ref must be HEAD)")
    p_vd.add_argument("--json", action="store_true")
    p_appr = sub.add_parser("approve")
    p_appr.add_argument("--repo")
    p_appr.add_argument("--spec")
    p_appr.add_argument("--by", required=True)
    p_appr.add_argument("--note")
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
    p_ver.add_argument("--record", action="store_true", help="append a verify record (surface, family, device)")
    p_sa = sub.add_parser("scope-audit")
    p_sa.add_argument("--spec", required=True)
    p_sa.add_argument("--task")
    p_sa.add_argument("--rev", help="A..B range for --task")
    p_sa.add_argument("--wave-merges", action="store_true")
    p_sa.add_argument("--ref", default="main", help="branch whose first-parent merges are audited")
    p_sa.add_argument("--root", help="checkout to audit (default: git toplevel of the cwd)")
    p_sa.add_argument("--json", action="store_true")
    p_sc = sub.add_parser("scope", help="H9: a diff or one path against the task's writes/forbids")
    p_sc_mode = p_sc.add_mutually_exclusive_group(required=True)
    p_sc_mode.add_argument("--check-path", metavar="PATH", help="pre-write accelerator: one path (fails open)")
    p_sc_mode.add_argument("--branch")
    p_sc_mode.add_argument("--range", dest="rng", metavar="A..B")
    p_sc_mode.add_argument("--set", dest="set_task", metavar="TASK", help="set the active task for --repo")
    p_sc_mode.add_argument("--clear", action="store_true", help="clear the active task for --repo")
    p_sc_mode.add_argument("--show", action="store_true", help="print the active task for --repo")
    p_sc.add_argument("--spec")
    p_sc.add_argument("--task")
    p_sc.add_argument("--base", help="with --branch: the ref compared against (default main)")
    p_sc.add_argument("--repo", help="checkout (default: the cwd's)")
    p_sc.add_argument("--cwd", help="with --check-path: resolve a relative PATH from here")
    p_sc.add_argument("--json", action="store_true")
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
        if args.recon:
            return cmd_init_recon(args.repo, spec=args.spec, stdout=args.stdout)
        if args.frame:
            return cmd_init_frame(args.repo, neutral=args.neutral, stdout=args.stdout, inherits=args.inherits,
                                  inherits_context=args.inherits_context, lifecycle=args.lifecycle)
        return cmd_init(args.path)
    if args.cmd == "lint":
        return cmd_lint(repo=args.repo, spec=args.spec, all_=args.all, since=args.since,
                        run_closures=args.run_closures)
    if args.cmd == "next":
        if args.spec:
            return cmd_next_remediation(Path(args.spec).expanduser().resolve())
        return cmd_next(args.repo)
    if args.cmd == "approve":
        return cmd_approve(repo=args.repo, spec=args.spec, by=args.by, note=args.note)
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
    if args.cmd == "scope":
        if args.check_path:
            return cmd_scope_check_path(args.check_path, cwd=args.cwd, as_json=args.json)
        if args.set_task or args.clear or args.show:
            action = "set" if args.set_task else ("clear" if args.clear else "show")
            return cmd_scope_pointer(action, task=args.set_task, spec=args.spec, repo=args.repo, as_json=args.json)
        return cmd_scope_diff(spec=args.spec, task=args.task, branch=args.branch, base=args.base, rng=args.rng,
                              repo=args.repo, as_json=args.json)
    spec = find_spec(getattr(args, "spec", None))
    if args.cmd == "findings":
        return cmd_findings(spec, status=args.status, as_json=args.json)
    if args.cmd == "packet":
        return cmd_packet(spec, args.ident, fmt=args.format)
    if args.cmd == "verdict":
        if args.branch and args.rng:
            print("verdict: pass --branch or --range, not both", file=sys.stderr)
            return 2
        return cmd_verdict(spec, branch=args.branch, rng=args.rng, run=args.run, as_json=args.json, base=args.base)
    if args.cmd == "status":
        return cmd_status(spec)
    if args.cmd == "gate":
        return cmd_gate(spec)
    if args.cmd == "ready":
        return cmd_ready(spec)
    if args.cmd == "worktree":
        return cmd_worktree_add(spec, args.task_id, args.repo)
    if args.cmd == "verify":
        return cmd_verify(spec, args.run, args.root, record=args.record)
    return 2


if __name__ == "__main__":
    sys.exit(main())
