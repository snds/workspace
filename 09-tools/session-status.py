#!/usr/bin/env python3
"""Session-start ritual card — the same summary Claude Code renders.

Any surface runs this and emits the stdout as the first reply of a new session.
Stdlib-only. Read-only.

Usage:
  python3 09-tools/session-status.py
  python3 09-tools/session-status.py --surface Cursor --via cursor-hook/startup
  python3 09-tools/session-status.py --json
  python3 09-tools/session-status.py --check
  python3 09-tools/session-status.py --family claude|cursor|codex|auto
  python3 09-tools/session-status.py --self-test

Family-aware (H25): when the walls family is `claude`, projects whose SESSION-STATE
`Context profile` starts with `centric-` collapse to one count line, and the pending
line adds the employer-keyword count. Every other family gets today's card, byte for
byte. The machine label comes from `profile_resolve.device_label()`; if that import
fails the label is the raw short hostname. Fail-open throughout.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import io
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Optional

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent

AUDIT_STALE_DAYS = 14
HARNESS_MAP_STALE_DAYS = 30
AUDIT_LOG = ROOT / "06-context" / "audit-log.md"
SESSION_LOG = ROOT / "06-context" / "session-log.md"
PROJECT_CONTEXT = ROOT / "06-context" / "project-context.md"
HARNESS_STAMP = (
    ROOT / "07-projects" / "19-workspace-brain" / "reports" / "harness-map.stamp"
)
ROUTING_STAMP = (
    ROOT / "07-projects" / "19-workspace-brain" / "reports" / "skill-routing-harness.stamp"
)
SIDE_CHAT = ROOT / "06-context" / "side-chat-inbox.md"
DOCTOR_STATE = Path.home() / ".claude" / "ws-state"

EMPLOYER_PROFILE_PREFIX = "centric-"
EMPLOYER_HANDLERS = "Cursor/Codex"
ORACLE_SHA = "2ff02e7"
_UNSET: Any = object()


def _resolver() -> Any:
    """Lazy import of the vault resolver (3d import rules). None when absent. Fail-open."""
    try:
        if str(TOOLS) not in sys.path:
            sys.path.insert(0, str(TOOLS))
        import profile_resolve  # noqa: PLC0415 — lazy by contract

        return profile_resolve
    except Exception:  # fail-open: any import-time failure means "no resolver"
        return None


def _short_hostname() -> str:
    host = socket.gethostname() or "unknown-host"
    return host.split(".", 1)[0] or host


def machine_label(*, resolver: Any = _UNSET) -> str:
    pr = _resolver() if resolver is _UNSET else resolver
    if pr is not None:
        try:
            label = pr.device_label()
            if isinstance(label, str) and label.strip():
                return label
        except Exception:
            pass
    return _short_hostname()


def resolve_family(family: str = "auto", *, resolver: Any = _UNSET) -> str:
    """The walls family: explicit flag, else profile_resolve.detect_surface(). Unknown on failure."""
    if family and family != "auto":
        return family
    pr = _resolver() if resolver is _UNSET else resolver
    if pr is None:
        return "unknown"
    try:
        det = pr.detect_surface()
        fam = det.get("family_for_walls") if isinstance(det, dict) else None
        return fam if isinstance(fam, str) and fam else "unknown"
    except Exception:
        return "unknown"


def employer_keywords(*, resolver: Any = _UNSET) -> Optional[list[str]]:
    """`employer_substance.count_keywords` from context-remotes, or None when unreadable."""
    pr = _resolver() if resolver is _UNSET else resolver
    if pr is None:
        return None
    try:
        table = pr.load_table("context-remotes")
        words = table["employer_substance"]["count_keywords"]
    except Exception:
        return None
    if not isinstance(words, list):
        return None
    return [w for w in words if isinstance(w, str) and w.strip()]


def count_pending_employer(keywords: list[str], path: Optional[Path] = None) -> int:
    """Open `- [ ]` lines naming any keyword (case-insensitive, word boundaries)."""
    target = path or PROJECT_CONTEXT
    if not keywords or not target.is_file():
        return 0
    rx = re.compile(
        r"(?<![A-Za-z0-9_])(?:" + "|".join(re.escape(k) for k in keywords) + r")(?![A-Za-z0-9_])",
        re.IGNORECASE,
    )
    n = 0
    for line in target.read_text(encoding="utf-8", errors="replace").splitlines():
        if re.match(r"^\s*-\s\[\s\]\s", line) and rx.search(line):
            n += 1
    return n


def project_profile(state: Path) -> str:
    """The SESSION-STATE `Context profile` value (first token, backticks stripped)."""
    try:
        text = state.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    m = re.search(r"^\s*-\s+\*\*Context profile\*\*:\s*(.+)$", text, re.MULTILINE)
    if not m:
        return ""
    value = m.group(1).strip().lstrip("`").strip()
    return re.split(r"[`\s/]", value, maxsplit=1)[0] if value else ""


def _git(*args: str) -> str:
    try:
        r = subprocess.run(
            ["git", "-C", str(ROOT), *args],
            capture_output=True,
            text=True,
            timeout=4,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return (r.stdout or "").strip() if r.returncode == 0 else ""


def git_state() -> dict:
    branch = _git("branch", "--show-current") or "?"
    sha = _git("rev-parse", "--short", "HEAD") or "?"
    porcelain = _git("status", "--porcelain")
    dirty = len([ln for ln in porcelain.splitlines() if ln.strip()]) if porcelain else 0
    ahead = _git("rev-list", "--count", "@{u}..HEAD")
    try:
        unpushed = int(ahead) if ahead else 0
    except ValueError:
        unpushed = 0
    return {
        "branch": branch,
        "sha": sha,
        "dirty": dirty,
        "unpushed": unpushed,
        "line": (
            f"`{branch}` @ `{sha}`, "
            + ("clean" if dirty == 0 else f"{dirty} modified")
            + (f" · {unpushed} unpushed" if unpushed else "")
        ),
    }


def count_pending(path: Path | None = None) -> int:
    target = path or PROJECT_CONTEXT
    if not target.is_file():
        return 0
    text = target.read_text(encoding="utf-8", errors="replace")
    return len(re.findall(r"^\s*-\s\[\s\]\s", text, re.MULTILINE))


def last_session(path: Path | None = None) -> str:
    target = path or SESSION_LOG
    if not target.is_file():
        return ""
    in_entries = False
    in_block = False
    block_date = ""
    try:
        with target.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.startswith("## Session Entries"):
                    in_entries = True
                    continue
                if not in_entries:
                    continue
                m = re.match(r"^### (\d{4}-\d{2}-\d{2})\s+[—-]\s+(.+?)\s*$", line)
                if m:
                    return f"{m.group(1)} — {m.group(2)}"
                if line.strip() == "--- SESSION BLOCK ---":
                    in_block = True
                    block_date = ""
                    continue
                if in_block:
                    dm = re.match(r"^Date:\s*(\d{4}-\d{2}-\d{2})\s*$", line)
                    if dm:
                        block_date = dm.group(1)
                        continue
                    pm = re.match(r"^Project\(s\):\s*(.+?)\s*$", line)
                    if pm and block_date:
                        title = pm.group(1)
                        if len(title) > 100:
                            title = title[:99].rstrip() + "…"
                        return f"{block_date} — {title}"
                    if line.strip() == "--- END BLOCK ---":
                        in_block = False
    except OSError:
        return ""
    return ""


def active_projects(projects_dir: Path | None = None) -> list[tuple[str, str, str]]:
    """(folder, last-updated, title) for each 07-projects/*/SESSION-STATE.md."""
    base = projects_dir or (ROOT / "07-projects")
    if not base.is_dir():
        return []
    out: list[tuple[str, str, str]] = []
    for child in sorted(base.iterdir()):
        if not child.is_dir() or child.name.startswith("_"):
            continue
        state = child / "SESSION-STATE.md"
        if not state.is_file():
            continue
        try:
            text = state.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        updated = ""
        m = re.search(r"_Last updated:\s*(\d{4}-\d{2}-\d{2})", text)
        if m:
            updated = m.group(1)
        title = ""
        after = text.split("## Session history", 1)
        if len(after) == 2:
            m2 = re.search(
                r"^###\s+\d{4}-\d{2}-\d{2}\s+[—–-]\s+(.+?)\s*$",
                after[1],
                re.MULTILINE,
            )
            if m2:
                title = m2.group(1).strip()
        if not title:
            hm = re.search(
                r"^\s*-\s+\*\*Current focus\*\*:\s*(.+)$",
                text,
                re.MULTILINE,
            )
            if hm:
                title = hm.group(1).strip()
                if len(title) > 100:
                    title = title[:99].rstrip() + "…"
        out.append((child.name, updated, title or "(no state info)"))
    return out


def doctor_misses() -> int:
    log = DOCTOR_STATE / "audit.log"
    mark_path = DOCTOR_STATE / "ack-mark"
    if not log.is_file():
        return 0
    mark = ""
    if mark_path.is_file():
        try:
            mark = mark_path.read_text(encoding="utf-8").strip()
        except OSError:
            mark = ""
    n = 0
    try:
        for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
            if " MISS " not in line:
                continue
            ts = line.split(" ", 1)[0] if line else ""
            if not mark or ts > mark:
                n += 1
    except OSError:
        return 0
    return n


def _stamp_age_days(path: Path, key: str = "date") -> int | None:
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = re.search(
        rf"^{key}:\s*(\d{{4}})-(\d{{2}})-(\d{{2}})\b",
        text,
        re.MULTILINE,
    )
    if not m:
        m = re.search(r"^##\s+(\d{4})-(\d{2})-(\d{2})\b", text, re.MULTILINE)
    if not m:
        return None
    try:
        last = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except ValueError:
        return None
    # One clock: stamps are authored as local calendar dates, so measure against the
    # local date. Mixing a UTC "now" in made every Pacific evening read one day older.
    return (date.today() - last).days


def notices() -> list[str]:
    try:
        return _notices()
    except Exception:
        return []


def _notices() -> list[str]:
    out: list[str] = []
    misses = doctor_misses()
    if misses:
        out.append(
            f"{misses} un-acknowledged bootstrap MISS(es) — run workspace-doctor"
        )
    audit_days = _stamp_age_days(AUDIT_LOG)
    if audit_days is not None and audit_days >= AUDIT_STALE_DAYS:
        if audit_days >= AUDIT_STALE_DAYS * 2:
            out.append(
                f"P0 — workspace audit is {audit_days} days overdue "
                f"(threshold {AUDIT_STALE_DAYS}). Propose `/optimize` this session."
            )
        else:
            out.append(
                f"Workspace audit is stale — last audit {audit_days} days ago. Run `/optimize`."
            )
    harness_days = _stamp_age_days(HARNESS_STAMP)
    if harness_days is not None and harness_days >= HARNESS_MAP_STALE_DAYS:
        out.append(
            f"Harness map is stale ({harness_days} days). Run `/harness-map` when convenient."
        )
    if not ROUTING_STAMP.is_file():
        out.append(
            "Skill-routing harness stamp missing — run "
            "`python3 09-tools/evaluate-skill-routing.py` (not a blocker)."
        )
    git = git_state()
    if git["unpushed"]:
        out.append(f"{git['unpushed']} unpushed commit(s) — other machines are stale until push.")
    if SIDE_CHAT.is_file():
        try:
            head = SIDE_CHAT.read_text(encoding="utf-8", errors="replace")[:400]
        except OSError:
            head = ""
        if re.search(r"^status:\s*pending\b", head, re.MULTILINE | re.IGNORECASE):
            out.append("Side-chat inbox pending — read `06-context/side-chat-inbox.md` first.")
    return out


def collect(
    surface: str = "", via: str = "session-status", family: str = "auto", *, resolver: Any = _UNSET
) -> dict:
    pr = _resolver() if resolver is _UNSET else resolver
    now = datetime.now().astimezone()
    git = git_state()
    projects = active_projects()
    fam = resolve_family(family, resolver=pr)
    hidden = 0
    pending_employer: Optional[int] = None
    if fam == "claude":
        base = ROOT / "07-projects"
        kept = [
            p for p in projects
            if not project_profile(base / p[0] / "SESSION-STATE.md").startswith(EMPLOYER_PROFILE_PREFIX)
        ]
        hidden = len(projects) - len(kept)
        projects = kept
        words = employer_keywords(resolver=pr)
        if words is not None:
            pending_employer = count_pending_employer(words)
    data = {
        "branch": git["branch"],
        "sha": git["sha"],
        "date": now.strftime("%Y-%m-%d"),
        "datetime": now.strftime("%Y-%m-%d %H:%M %Z") or now.strftime("%Y-%m-%d %H:%M"),
        "via": via,
        "machine": machine_label(resolver=pr),
        "surface": surface or os.environ.get("WORKSPACE_SURFACE", "agent"),
        "last_session": last_session() or "(none in log)",
        "pending": count_pending(),
        "projects": [
            {"name": n, "updated": u, "title": t} for n, u, t in projects
        ],
        "git_line": git["line"],
        "notices": notices(),
    }
    data["family"] = fam
    data["employer_projects_hidden"] = hidden
    data["pending_employer"] = pending_employer
    return data


def format_card(data: dict) -> str:
    lines: list[str] = []
    for note in data["notices"]:
        lines.append(f"- ⚠ {note}")
    if data["notices"]:
        lines.append("")
    lines.append(
        f"[workspace: LOADED · {data['branch']}@{data['sha']} · {data['date']} · via:{data['via']}]"
    )
    lines.append(f"**✓ Workspace loaded** — {data['machine']} · {data['datetime']}")
    lines.append("")
    lines.append(f"- **Surface:** {data['surface']}")
    lines.append(f"- **Last session:** {data['last_session']}")
    employer = data.get("pending_employer")
    split = (
        f" ({employer} employer — handled by {EMPLOYER_HANDLERS})" if employer is not None else ""
    )
    lines.append(
        f"- **Pending:** {data['pending']} items{split} → "
        "06-context/project-context.md"
    )
    hidden = data.get("employer_projects_hidden") or 0
    n = len(data["projects"]) + hidden
    lines.append(f"- **Active projects ({n}):**")
    if not data["projects"] and not hidden:
        lines.append("  - (none with SESSION-STATE.md)")
    else:
        for p in data["projects"]:
            when = f" ({p['updated']})" if p["updated"] else ""
            lines.append(f"  - **{p['name']}**{when} — {p['title']}")
        if hidden:
            lines.append(f"  - {hidden} employer projects — handled by {EMPLOYER_HANDLERS}")
    lines.append(f"- **Git:** {data['git_line']}")
    lines.append("")
    lines.append("What's on the agenda today?")
    return "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Session-start ritual card")
    parser.add_argument("--surface", default="")
    parser.add_argument("--via", default="session-status")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--family", default="auto",
        help="walls family: auto (profile_resolve.detect_surface), claude, cursor, codex, …",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    data = collect(surface=args.surface, via=args.via, family=args.family)
    if args.check:
        if not data["sha"] or data["sha"] == "?":
            print("session-status FAIL: no git sha", file=sys.stderr)
            return 1
        if data["pending"] < 0:
            print("session-status FAIL: pending count", file=sys.stderr)
            return 1
        print(
            f"OK session-status — {len(data['projects'])} projects, "
            f"{data['pending']} pending, {len(data['notices'])} notice(s)"
        )
        return 0
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print(format_card(data))
    return 0


# ---------------------------------------------------------------------------
# --self-test: the 2ff02e7 oracle plus family cases. profile_resolve is faked
# (3d parallel-wave rule); HOME-derived state points at a temp dir.
# ---------------------------------------------------------------------------

_PATH_CONSTS = (
    "ROOT", "AUDIT_LOG", "SESSION_LOG", "PROJECT_CONTEXT", "HARNESS_STAMP", "ROUTING_STAMP", "SIDE_CHAT",
)


class _FixedDateTime(datetime):
    @classmethod
    def now(cls, tz=None):  # type: ignore[override]
        return datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone.utc)


class _FakeResolver:
    def __init__(self, *, family: str = "claude", keywords=("acme",), label: str = "Dev A",
                 broken: bool = False) -> None:
        self.family, self.keywords, self.label, self.broken = family, list(keywords), label, broken

    def detect_surface(self, payload_hint=None, **_kw):
        if self.broken:
            raise RuntimeError("fixture: detection failed")
        return {"family_for_walls": self.family, "family": self.family, "via": "env", "verified": True}

    def device_label(self, hostname=None, **_kw):
        if self.broken:
            raise RuntimeError("fixture: no label")
        return self.label

    def load_table(self, name, **_kw):
        if self.broken or name != "context-remotes":
            raise ValueError("fixture: no table")
        return {"employer_substance": {"count_keywords": self.keywords}}


def _load_oracle(tmp: Path) -> Any:
    """The 2ff02e7 module from git history, or None when history is unavailable."""
    try:
        r = subprocess.run(
            ["git", "-C", str(ROOT), "show", f"{ORACLE_SHA}:09-tools/session-status.py"],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if r.returncode != 0 or not r.stdout:
        return None
    path = tmp / "session_status_oracle.py"
    path.write_text(r.stdout, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("session_status_oracle", path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@contextlib.contextmanager
def _pinned(mods: list, consts: dict, doctor: Path, label: str):
    """Point every module at the same tree, a temp doctor dir, a fixed clock and label."""
    saved = []
    for mod in mods:
        keep = {k: getattr(mod, k) for k in (*_PATH_CONSTS, "DOCTOR_STATE", "datetime", "machine_label")}
        saved.append((mod, keep))
        for k, v in consts.items():
            setattr(mod, k, v)
        mod.DOCTOR_STATE = doctor
        mod.datetime = _FixedDateTime
        mod.machine_label = lambda *a, **k: label
    try:
        yield
    finally:
        for mod, keep in saved:
            for k, v in keep.items():
                setattr(mod, k, v)


def _consts_for(root: Path) -> dict:
    return {
        "ROOT": root,
        "AUDIT_LOG": root / "06-context" / "audit-log.md",
        "SESSION_LOG": root / "06-context" / "session-log.md",
        "PROJECT_CONTEXT": root / "06-context" / "project-context.md",
        "HARNESS_STAMP": root / "07-projects" / "19-workspace-brain" / "reports" / "harness-map.stamp",
        "ROUTING_STAMP": root / "07-projects" / "19-workspace-brain" / "reports"
        / "skill-routing-harness.stamp",
        "SIDE_CHAT": root / "06-context" / "side-chat-inbox.md",
    }


def _synthetic_tree(root: Path) -> None:
    """Synthetic owners only: two employer-profile projects, two personal, keyworded pending."""
    projects = {
        "01-alpha": ("personal-solo", "Alpha focus line"),
        "02-acme-work": ("centric-engineering", "ZZ-EMPLOYER-FOCUS acme widget rollout"),
        "03-beta": ("", "Beta focus line"),
        "04-acme-design": ("centric-design", "ZZ-EMPLOYER-FOCUS acme audit"),
    }
    for name, (profile, focus) in projects.items():
        d = root / "07-projects" / name
        d.mkdir(parents=True)
        prof = f"- **Context profile**: `{profile}` — fixture\n" if profile else ""
        d.joinpath("SESSION-STATE.md").write_text(
            f"# {name}\n\n_Last updated: 2026-01-01_\n\n{prof}- **Current focus**: {focus}\n",
            encoding="utf-8",
        )
    ctx = root / "06-context"
    ctx.mkdir(parents=True)
    ctx.joinpath("project-context.md").write_text(
        "- [ ] personal task\n"
        "- [ ] ACME review of the widget\n"
        "- [ ] acme-corp follow-up\n"
        "- [ ] acmex is not a keyword hit\n"
        "- [x] acme done item\n",
        encoding="utf-8",
    )
    ctx.joinpath("session-log.md").write_text(
        "## Session Entries\n\n### 2026-01-01 — fixture session\n", encoding="utf-8"
    )


def self_test() -> int:
    failures: list[str] = []
    passed = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal passed
        if cond:
            passed += 1
        else:
            failures.append(f"{name}{(' — ' + detail) if detail else ''}")

    me = sys.modules[__name__]
    label = "Fixture Label"
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        doctor = tmp / "home" / ".claude" / "ws-state"
        doctor.mkdir(parents=True)
        oracle = _load_oracle(tmp)
        tree = tmp / "tree"
        _synthetic_tree(tree)

        # 1. Oracle: every non-claude family is byte-identical to 2ff02e7 on the same tree.
        oracle_skipped = oracle is None
        if oracle is None:
            print(f"  SKIP oracle — {ORACLE_SHA} not in local history (shallow clone?)")
        else:
            for label_root, root in (("real tree", ROOT), ("synthetic tree", tree)):
                with _pinned([oracle, me], _consts_for(root), doctor, label):
                    want = oracle.format_card(oracle.collect(surface="S", via="V"))
                    for fam, res in (
                        ("cursor", _FakeResolver(family="cursor")),
                        ("codex", None),
                        ("auto", _FakeResolver(family="cursor")),
                        ("auto", _FakeResolver(broken=True)),
                        ("auto", None),
                    ):
                        got = format_card(collect(surface="S", via="V", family=fam, resolver=res))
                        check(f"oracle {label_root} family={fam} res={type(res).__name__}",
                              got == want, "card differs from the 2ff02e7 module")
                    claude = format_card(collect(surface="S", via="V", family="claude",
                                                 resolver=_FakeResolver()))
                    ritual = [ln for ln in want.splitlines() if ln.startswith("[workspace: ")]
                    check(f"ritual line unchanged ({label_root})",
                          bool(ritual) and ritual[0] in claude.splitlines())

        # 2. --family claude hides centric-* projects and prints the counts.
        with _pinned([me], _consts_for(tree), doctor, label):
            fake = _FakeResolver()
            data = collect(surface="S", via="V", family="claude", resolver=fake)
            card = format_card(data)
            names = [p["name"] for p in data["projects"]]
            check("claude hides centric-* projects", names == ["01-alpha", "03-beta"], str(names))
            check("claude card has no employer focus lines", "ZZ-EMPLOYER-FOCUS" not in card)
            check("claude card count line",
                  "  - 2 employer projects — handled by Cursor/Codex" in card.splitlines(), card)
            check("claude pending line",
                  "- **Pending:** 4 items (2 employer — handled by Cursor/Codex) → "
                  "06-context/project-context.md" in card.splitlines(), card)
            check("claude header counts all projects", "- **Active projects (4):**" in card.splitlines())
            check("json fields", data["family"] == "claude" and data["employer_projects_hidden"] == 2
                  and data["pending_employer"] == 2, json.dumps({k: data[k] for k in (
                      "family", "employer_projects_hidden", "pending_employer")}))
            auto = collect(surface="S", via="V", family="auto", resolver=fake)
            check("auto uses detect_surface family_for_walls", auto["family"] == "claude"
                  and auto["employer_projects_hidden"] == 2)
            nokw = format_card(collect(surface="S", via="V", family="claude",
                                       resolver=_FakeResolver(broken=True)))
            check("claude without tables still hides, no split", "ZZ-EMPLOYER-FOCUS" not in nokw
                  and "- **Pending:** 4 items → 06-context/project-context.md" in nokw.splitlines())
            cur = collect(surface="S", via="V", family="cursor", resolver=fake)
            check("cursor json fields", cur["family"] == "cursor" and cur["employer_projects_hidden"] == 0
                  and cur["pending_employer"] is None)
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                real_resolver = globals()["_resolver"]
                globals()["_resolver"] = lambda: fake
                try:
                    rc = main(["--json", "--family", "claude", "--surface", "S"])
                finally:
                    globals()["_resolver"] = real_resolver
            try:
                j = json.loads(out.getvalue())
                check("cli --json --family claude", rc == 0 and j["family"] == "claude"
                      and j["employer_projects_hidden"] == 2 and j["pending_employer"] == 2)
            except (ValueError, KeyError) as exc:
                check("cli json parses", False, repr(exc))

    # 3. The label: device_label when the resolver loads; raw short hostname when the import fails.
    check("label from device_label", machine_label(resolver=_FakeResolver(label="Dev B")) == "Dev B")
    check("label falls back when device_label raises",
          machine_label(resolver=_FakeResolver(broken=True)) == _short_hostname())
    saved_mod = sys.modules.get("profile_resolve", _UNSET)
    sys.modules["profile_resolve"] = None  # type: ignore[assignment]  # forces ImportError
    try:
        check("import failure → resolver None", _resolver() is None)
        check("import failure → raw short hostname", machine_label() == socket.gethostname().split(".", 1)[0])
        check("import failure → family unknown", resolve_family("auto") == "unknown")
    finally:
        if saved_mod is _UNSET:
            sys.modules.pop("profile_resolve", None)
        else:
            sys.modules["profile_resolve"] = saved_mod

    # 4. No hostname→label literal remains in this module.
    src = Path(__file__).read_text(encoding="utf-8")
    check("no hostname map literal", ("HOSTNAME" + "_MAP") not in src)

    # 5. Keyword counting: word boundaries, open boxes only.
    with tempfile.TemporaryDirectory() as td:
        pc = Path(td) / "pc.md"
        pc.write_text("- [ ] Acme x\n- [ ] acmex y\n- [x] acme z\n- [ ] (acme-corp)\n", encoding="utf-8")
        check("count_pending_employer", count_pending_employer(["acme"], pc) == 2)

    for f in failures:
        print(f"  ✗ {f}", file=sys.stderr)
    if failures:
        print(f"session-status self-test FAILED — {len(failures)} of {passed + len(failures)}",
              file=sys.stderr)
        return 1
    if oracle_skipped:
        # The oracle is the byte-identity guarantee for non-Claude cards: a run without it is not green.
        print(f"SKIPPED session-status self-test — {passed} checks, the {ORACLE_SHA} oracle did not run (exit 3)")
        return 3
    print(f"OK session-status self-test — {passed} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
