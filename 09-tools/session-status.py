#!/usr/bin/env python3
"""Session-start ritual card — the same summary Claude Code renders.

Any surface runs this and emits the stdout as the first reply of a new session.
Stdlib-only. Read-only.

Usage:
  python3 09-tools/session-status.py
  python3 09-tools/session-status.py --surface Cursor --via cursor-hook/startup
  python3 09-tools/session-status.py --json
  python3 09-tools/session-status.py --check
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent

HOSTNAME_MAP = {
    "Voyager-2.local": "Personal MacBook Pro",
    "seansands.local": "Work MacBook Pro",
    "CS-KQ23N94M0W": "Work MacBook Pro (loaner)",
    "CS-K746DRWXY1": "Work MacBook Pro",
    "Enterprise": "Windows Desktop",
}

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


def machine_label() -> str:
    host = socket.gethostname()
    return HOSTNAME_MAP.get(host, host)


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
        last = datetime(
            int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=timezone.utc
        )
    except ValueError:
        return None
    return (datetime.now(timezone.utc) - last).days


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


def collect(surface: str = "", via: str = "session-status") -> dict:
    now = datetime.now().astimezone()
    git = git_state()
    projects = active_projects()
    return {
        "branch": git["branch"],
        "sha": git["sha"],
        "date": now.strftime("%Y-%m-%d"),
        "datetime": now.strftime("%Y-%m-%d %H:%M %Z") or now.strftime("%Y-%m-%d %H:%M"),
        "via": via,
        "machine": machine_label(),
        "surface": surface or os.environ.get("WORKSPACE_SURFACE", "agent"),
        "last_session": last_session() or "(none in log)",
        "pending": count_pending(),
        "projects": [
            {"name": n, "updated": u, "title": t} for n, u, t in projects
        ],
        "git_line": git["line"],
        "notices": notices(),
    }


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
    lines.append(
        f"- **Pending:** {data['pending']} items → "
        "06-context/project-context.md"
    )
    n = len(data["projects"])
    lines.append(f"- **Active projects ({n}):**")
    if not data["projects"]:
        lines.append("  - (none with SESSION-STATE.md)")
    else:
        for p in data["projects"]:
            when = f" ({p['updated']})" if p["updated"] else ""
            lines.append(f"  - **{p['name']}**{when} — {p['title']}")
    lines.append(f"- **Git:** {data['git_line']}")
    lines.append("")
    lines.append("What's on the agenda today?")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Session-start ritual card")
    parser.add_argument("--surface", default="")
    parser.add_argument("--via", default="session-status")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = collect(surface=args.surface, via=args.via)
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


if __name__ == "__main__":
    raise SystemExit(main())
