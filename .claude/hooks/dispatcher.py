#!/usr/bin/env python3
"""
Claude Code hook dispatcher. One entry point for all hook events.
Cross-platform: macOS, Windows, Linux. Python 3.8+.

Hook events receive JSON on stdin with session context. We dispatch by argv[1]
to the handler for that event. Output to stdout is displayed in the Claude Code
transcript (for transcript-visible output) or injected as additional context
(when JSON with hookSpecificOutput.additionalContext is returned).

Reference: https://docs.claude.com/en/docs/claude-code/hooks
"""

from __future__ import annotations

import importlib
import importlib.util
import json
import os
import re
import socket
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

_PROCESS_T0 = time.monotonic()  # the SessionEnd budget counts from process start
# `--self-test` runs hermetic fixtures in temp repos (09-tools/fixtures/nightly/), so it
# is the one entry allowed without CLAUDE_PROJECT_DIR.
_SELF_TEST = __name__ == "__main__" and sys.argv[1:2] == ["--self-test"]
_project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
if not _project_dir and not _SELF_TEST:
    # Not invoked by Claude Code from a project checkout (stray copy, mis-registered
    # hook). Abort silently rather than treating an arbitrary cwd as the workspace.
    sys.exit(0)
WORKSPACE_ROOT = Path(_project_dir) if _project_dir else Path(__file__).resolve().parents[2]
CONTEXT_DIR = WORKSPACE_ROOT / "06-context"
SESSION_LOG = CONTEXT_DIR / "session-log.md"
PROJECT_CONTEXT = CONTEXT_DIR / "project-context.md"
AUDIT_LOG = CONTEXT_DIR / "audit-log.md"
HARNESS_MAP_STAMP = (
    WORKSPACE_ROOT / "07-projects" / "19-workspace-brain" / "reports" / "harness-map.stamp"
)
SKILL_ROUTING_EVAL = WORKSPACE_ROOT / "09-tools" / "evaluate-skill-routing.py"
STATE_DIR = WORKSPACE_ROOT / ".claude" / "state"
CLAUDE_VERSION_PIN = STATE_DIR / "claude-version"
DESYNC_NOTICE = STATE_DIR / "desync-notice.md"
KNOWLEDGE_DIR = WORKSPACE_ROOT / "08-knowledge"
KNOWLEDGE_INDEX = KNOWLEDGE_DIR / "_INDEX.md"
SKILLS_REGISTRY = WORKSPACE_ROOT / "03-skills" / "skills.registry.json"

CLAUDE_CODE_CHANGELOG_URL = "https://github.com/anthropics/claude-code/releases"
AUDIT_STALE_DAYS = 14
HARNESS_MAP_STALE_DAYS = 30  # Notice only after a first map exists (stamp present)

# Files where session edits reliably land. When the auto-commit's broad `git add -A`
# would risk committing phantom or stale deletions, the session-end hook falls back
# to content-hash staging on JUST these paths. Anything outside this list waits for
# the next `/session-end` skill invocation (which runs interactively and can scope
# changes mindfully) or for Drive sync / cross-worktree state to settle.
SAFE_STAGE_PATHS = [
    "06-context/session-log.md",
    "06-context/project-context.md",
    "06-context/audit-log.md",
    "06-context/artifact-registry.md",
]

# Heuristic threshold for stale-worktree detection. When `git status` reports more
# than this many worktree deletions, assume the working tree is out of sync with
# HEAD (e.g., a stale Claude Code worktree that wasn't refreshed) and fall back to
# safe-paths staging — committing those deletions could destroy real files on main.
STALE_DELETION_THRESHOLD = 5

# Machine labels come from 02-shared-references/devices.json through
# profile_resolve.device_label() (D14: one declared device table). Fallback: the raw
# short hostname.

# Hosts whose hook payloads this dispatcher serves. Any other VERIFIED host (Cursor,
# VS Code, ...) that loads .claude/settings.json gets no output from this file.
CLAUDE_HOSTS = frozenset({"claude-code", "claude-code-cloud"})

# Default timeout for read-only git calls on hook paths. Index-writing and network
# calls pass their own, bounded by the SessionEnd deadline.
GIT_TIMEOUT_S = 4.0
GIT_WRITE_TIMEOUT_S = 15.0

def read_stdin_json() -> dict:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return {}


def emit_context(text: str, event_name: str) -> None:
    """Inject additional context into the session (SessionStart / UserPromptSubmit only).

    `event_name` MUST be the exact hook event name ("SessionStart" / "UserPromptSubmit").
    A null/missing hookEventName fails harness-side validation and the whole payload —
    including additionalContext — is silently dropped (observed 2026-07-08; this was
    the delivery defect that dark-launched the entire context layer).
    """
    payload = {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": text,
        }
    }
    print(json.dumps(payload))


def _vault_module(name: str):
    """Import a vault `09-tools` module lazily (import contract 3d). None on any failure,
    so every caller keeps its fail-open fallback."""
    tools = str(WORKSPACE_ROOT / "09-tools")
    try:
        if tools not in sys.path:
            sys.path.insert(0, tools)
        return importlib.import_module(name)
    except Exception:  # noqa: BLE001 — ImportError, OSError, ValueError or a broken module
        return None


def _short_hostname() -> str:
    try:
        return socket.gethostname().split(".")[0] or "unknown-host"
    except OSError:
        return "unknown-host"


def resolve_machine_label() -> str:
    """Label from devices.json via profile_resolve.device_label(); raw short hostname
    when the resolver is absent or fails."""
    pr = _vault_module("profile_resolve")
    if pr is not None:
        try:
            label = pr.device_label()
            if isinstance(label, str) and label.strip():
                return label.strip()
        except Exception:  # noqa: BLE001 — device_label never raises by contract; stay safe
            pass
    return _short_hostname()


def _should_defer(payload: dict) -> bool:
    """True only when a VERIFIED non-Claude host is running this hook (for example Cursor
    or VS Code loading .claude/settings.json). The payload hint decides first, with no
    ancestry walk when it names Claude Code. Any error, or unverified evidence, keeps
    today's behaviour."""
    try:
        ws_hook = _vault_module("ws_hook")
        if ws_hook is None:
            return False
        hint = ws_hook.payload_host_hint(payload)
        if hint in CLAUDE_HOSTS:
            return False
        pr = _vault_module("profile_resolve")
        if pr is None:
            return False
        det = pr.detect_surface(hint)
        if not isinstance(det, dict):
            return False
        host = det.get("acting_host")
        return bool(det.get("determined") and det.get("verified") and host
                    and host not in CLAUDE_HOSTS)
    except Exception:  # noqa: BLE001 — fail open: proceed as Claude Code
        return False


def read_head(path: Path, lines: int = 30) -> str:
    if not path.exists():
        return f"_({path.name} not found)_"
    with path.open("r", encoding="utf-8", errors="replace") as f:
        head = [next(f, "") for _ in range(lines)]
    return "".join(head).rstrip()


def git(*args: str, check: bool = False,
        timeout: float = GIT_TIMEOUT_S, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run git in the workspace. A timeout returns exit 124 instead of raising."""
    try:
        return subprocess.run(
            ["git", "-C", str(WORKSPACE_ROOT), *args],
            capture_output=True,
            text=True,
            check=check,
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(["git", *args], 124, stdout="",
                                           stderr=f"git timed out after {timeout:g}s")


def _is_inside_linked_worktree() -> bool:
    """True if this hook is running inside a linked worktree (vs the main working tree).

    git distinguishes via --git-dir (this worktree's .git/worktrees/<name>/) vs
    --git-common-dir (the shared .git/). They're equal in the main working tree
    and differ in any linked worktree.
    """
    git_dir = git("rev-parse", "--git-dir").stdout.strip()
    common_dir = git("rev-parse", "--git-common-dir").stdout.strip()
    if not git_dir or not common_dir:
        return False
    try:
        return Path(git_dir).resolve() != Path(common_dir).resolve()
    except Exception:
        return False


def _list_worktrees() -> list[dict]:
    """Parse `git worktree list --porcelain` into a list of dicts.

    Each entry: {"path": str, "head": str, "branch": str, "bare": bool, "detached": bool}.
    Branch is the full ref name ("refs/heads/foo") or "" for detached / bare.
    """
    r = git("worktree", "list", "--porcelain")
    if r.returncode != 0:
        return []
    entries: list[dict] = []
    current: dict = {}
    for line in r.stdout.splitlines():
        if not line:
            if current:
                entries.append(current)
                current = {}
            continue
        if line.startswith("worktree "):
            current["path"] = line[len("worktree "):]
        elif line.startswith("HEAD "):
            current["head"] = line[len("HEAD "):]
        elif line.startswith("branch "):
            current["branch"] = line[len("branch "):]
        elif line == "bare":
            current["bare"] = True
        elif line == "detached":
            current["detached"] = True
    if current:
        entries.append(current)
    return entries


def _branch_fully_merged_into_main(branch_ref: str) -> bool:
    """True if every commit on `branch_ref` is also on main (i.e., main..branch is empty)."""
    if not branch_ref:
        return False
    r = git("log", "--oneline", f"main..{branch_ref}")
    return r.returncode == 0 and not r.stdout.strip()


def _cleanup_stale_worktrees() -> tuple[list[str], list[str]]:
    """Auto-remove fully-merged Drive-resident worktrees.

    Criteria for removal:
    - Nested: path lies under WORKSPACE_ROOT + os.sep. Worktrees elsewhere (e.g.
      ~/.claude-worktrees/, or sibling `<root>.intent-*` wave worktrees) are skipped —
      those may be parked work the user wants to keep.
    - Branch fully merged into main: `main..branch` is empty. Means main has every
      commit, so removing the worktree's working-tree copy loses nothing.
    - Not the current worktree: git refuses self-removal anyway, but skip explicitly.
    - Not the main working tree: never auto-remove the canonical checkout.

    Returns (cleaned, skipped) where:
    - cleaned: list of branch short-names removed
    - skipped: list of "<path>: <reason>" strings for worktrees that didn't qualify
    """
    if not in_git_repo():
        return [], []

    cleaned: list[str] = []
    skipped: list[str] = []

    try:
        ws_root_resolved = WORKSPACE_ROOT.resolve()
    except Exception:
        return [], []
    drive_prefix = str(ws_root_resolved)

    # The path of the currently-running worktree, if any. Used to avoid self-removal.
    cur_path = ""
    try:
        toplevel = git("rev-parse", "--show-toplevel").stdout.strip()
        if toplevel:
            cur_path = str(Path(toplevel).resolve())
    except Exception:
        pass

    for entry in _list_worktrees():
        path = entry.get("path", "")
        branch = entry.get("branch", "")
        if not path:
            continue
        if entry.get("bare"):
            continue
        try:
            resolved = str(Path(path).resolve())
        except Exception:
            continue

        # Skip the main working tree (workspace root itself)
        if resolved == drive_prefix:
            continue
        # Only worktrees nested UNDER the workspace root. The separator matters:
        # a sibling `<root>.intent-*` worktree shares the string prefix and must never
        # be a candidate (wave worktrees are removed by their owner, not by this hook).
        if not resolved.startswith(drive_prefix + os.sep):
            continue
        # Never self-remove
        if cur_path and resolved == cur_path:
            skipped.append(f"{path}: current worktree (next session-start will handle it)")
            continue
        # Need a branch ref to verify merged state
        if not branch:
            skipped.append(f"{path}: detached HEAD; manual cleanup required")
            continue
        if not _branch_fully_merged_into_main(branch):
            skipped.append(f"{path}: {branch} has commits not in main; manual review needed")
            continue

        rm = git("worktree", "remove", "--force", path, timeout=GIT_WRITE_TIMEOUT_S)
        if rm.returncode != 0:
            skipped.append(f"{path}: `git worktree remove` failed — {rm.stderr.strip()}")
            continue

        short = branch.replace("refs/heads/", "")
        # Use -D since we already verified the branch is merged. Quiet on failure
        # (branch may already be gone if --force pruned it).
        git("branch", "-D", short, timeout=GIT_WRITE_TIMEOUT_S)
        cleaned.append(short)

    return cleaned, skipped


def in_git_repo() -> bool:
    r = git("rev-parse", "--is-inside-work-tree")
    return r.returncode == 0 and r.stdout.strip() == "true"


def _describe_git_state() -> str:
    """Short description of git HEAD + cleanliness, e.g. 'main @ f7b8c4e, clean' or '..., 3 modified'."""
    try:
        if not in_git_repo():
            return ""
        branch = git("symbolic-ref", "--short", "HEAD").stdout.strip() or "(detached)"
        sha = git("rev-parse", "--short", "HEAD").stdout.strip() or "(no commits)"
        status = git("status", "--porcelain").stdout.strip()
        clean = "clean" if not status else f"{len(status.splitlines())} modified"
        return f"{branch} @ {sha}, {clean}"
    except Exception:
        return ""


def _parse_last_session_entry(path: Path) -> str:
    """Return 'YYYY-MM-DD — title' from the first entry under '## Session Entries' in session-log.md.

    Understands BOTH entry shapes (FX-5, 2026-07-09 — the heading-only parser showed a
    month-stale "last session" on every boot once newer entries were bare blocks):
    - '### YYYY-MM-DD — title' headings (preferred; /session-end writes one per block)
    - bare '--- SESSION BLOCK ---' blocks (title recovered from Date: + Project(s): lines)
    Whichever shape appears first below '## Session Entries' (newest-first log) wins.
    """
    if not path.exists():
        return ""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            in_entries = False
            in_block = False
            block_date = ""
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
                        # Malformed block (no Date:/Project(s):) — keep scanning.
                        in_block = False
    except Exception:
        pass
    return ""


def _count_pending_items(path: Path) -> int:
    """Count open task checkboxes (- [ ]) in project-context.md. Excludes completed (- [x])."""
    if not path.exists():
        return 0
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        return len(re.findall(r"^\s*-\s\[\s\]\s", text, re.MULTILINE))
    except Exception:
        return 0


def _check_claude_version_change() -> str:
    """Compare current `claude --version` against pinned value (per-machine, .claude/state/).

    Returns a notice string if the version changed since the pin was last written.
    Returns "" on first run (no pin yet — writes the pin silently) or if version is unchanged.
    Updates the pin to the current version after detecting a change so we don't re-notify.
    """
    try:
        r = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        current = (r.stdout or r.stderr or "").strip()
        if not current:
            return ""
    except Exception:
        return ""

    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        return ""

    if not CLAUDE_VERSION_PIN.exists():
        try:
            CLAUDE_VERSION_PIN.write_text(current + "\n", encoding="utf-8")
        except Exception:
            pass
        return ""

    try:
        previous = CLAUDE_VERSION_PIN.read_text(encoding="utf-8").strip()
    except Exception:
        return ""

    if previous == current:
        return ""

    try:
        CLAUDE_VERSION_PIN.write_text(current + "\n", encoding="utf-8")
    except Exception:
        pass

    return (
        f"Claude Code updated from `{previous}` to `{current}` on this machine since last session. "
        f"Review changelog: {CLAUDE_CODE_CHANGELOG_URL}. "
        f"If anything in the new release could affect this brain (hooks, slash commands, file conventions, "
        f"sandboxing, settings.json schema, worktree behavior), document it in pending items "
        f"in `06-context/project-context.md` so it's surfaced next session."
    )


def _check_audit_staleness() -> str:
    """Return a notice if the workspace audit hasn't been run within AUDIT_STALE_DAYS.

    Reads the most recent date from 06-context/audit-log.md. Returns "" if log is missing
    (treat as fresh — no nag until first audit) or if last audit is within threshold.
    """
    if not AUDIT_LOG.exists():
        return ""
    try:
        text = AUDIT_LOG.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^##\s+(\d{4})-(\d{2})-(\d{2})\b", text, re.MULTILINE)
        if not m:
            return ""
        last_audit = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=timezone.utc)
        now_utc = datetime.now(timezone.utc)
        days = (now_utc - last_audit).days
        if days < AUDIT_STALE_DAYS:
            return ""
        if days >= AUDIT_STALE_DAYS * 2:
            # Escalation tier: the plain nag was ignored for 72 days once (2026-07-08)
            # and the un-audited drift contributed to a real failure. Past 2x the
            # threshold, the notice demands scheduling, not just awareness.
            return (
                f"P0 — workspace audit is {days} days overdue (threshold: {AUDIT_STALE_DAYS} days). "
                f"Un-audited drift has caused real failures before (see audit-log 2026-07-08). "
                f"Propose running `/optimize` THIS session before starting new work, and say so "
                f"explicitly in your first reply — do not let this notice pass silently."
            )
        return (
            f"Workspace audit is stale — last audit was {days} days ago "
            f"(threshold: {AUDIT_STALE_DAYS} days). Run `/optimize` to review the brain "
            f"for stale items, contradictions, drift, and consolidation opportunities."
        )
    except Exception:
        return ""


def _check_harness_map_staleness() -> str:
    """Return a notice if the last harness-map is older than HARNESS_MAP_STALE_DAYS.

    Silent when the stamp is missing — no nag before the first map (see harness-map skill).
    Stamp path: 07-projects/19-workspace-brain/reports/harness-map.stamp
    """
    if not HARNESS_MAP_STAMP.exists():
        return ""
    try:
        text = HARNESS_MAP_STAMP.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^date:\s*(\d{4})-(\d{2})-(\d{2})\b", text, re.MULTILINE)
        if not m:
            return ""
        last = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=timezone.utc)
        days = (datetime.now(timezone.utc) - last).days
        if days < HARNESS_MAP_STALE_DAYS:
            return ""
        return (
            f"Harness map is stale — last map was {days} days ago "
            f"(threshold: {HARNESS_MAP_STALE_DAYS} days). Run `/harness-map` when convenient "
            f"(read-only; not a blocker for ordinary work)."
        )
    except Exception:
        return ""


def _check_skill_routing_harness() -> str:
    """If the routing graph drifted, run the adversarial corpus. Fail-open.

    Silent when the stamp is current and last result is pass. Not a daemon:
    session start + write-quality gate + /health + /optimize + live --utterance.
    """
    if not SKILL_ROUTING_EVAL.exists():
        return ""
    try:
        stale = subprocess.run(
            [sys.executable, str(SKILL_ROUTING_EVAL), "--stale"],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            timeout=8,
        )
        if stale.returncode == 0:
            return ""
        check = subprocess.run(
            [sys.executable, str(SKILL_ROUTING_EVAL), "--check"],
            cwd=WORKSPACE_ROOT,
            capture_output=True,
            text=True,
            timeout=20,
        )
        if check.returncode == 0:
            subprocess.run(
                [sys.executable, str(SKILL_ROUTING_EVAL)],
                cwd=WORKSPACE_ROOT,
                capture_output=True,
                text=True,
                timeout=20,
            )
            return ""
        summary = (check.stdout or check.stderr or "routing corpus failed").strip().splitlines()
        head = summary[0] if summary else "routing corpus failed"
        return (
            f"Skill-routing harness failed — {head}. "
            "Run `python3 09-tools/evaluate-skill-routing.py` (not a blocker)."
        )
    except Exception:
        return ""


def _classify_worktree_state() -> dict:
    """Inspect `git status --porcelain` for conditions that make `git add -A` unsafe.

    Returns a dict with:
    - phantoms: list of (kind, path) where status disagrees with `os.path.exists`.
      Kinds: "phantom-untracked" (?? but file missing) or "phantom-deleted" (D but
      file present). Indicates Drive stat-cache lies on Windows.
    - deletions: count of worktree D entries (real or phantom). When this exceeds
      STALE_DELETION_THRESHOLD it usually means this checkout is a stale worktree
      whose local filesystem hasn't been refreshed to reflect HEAD — committing
      those deletions would destroy real files on main.
    - safe: False if phantoms or excessive deletions detected.
    - reason: short string explaining why safe is False, or "" when safe.
    """
    out = {"phantoms": [], "deletions": 0, "safe": True, "reason": ""}
    if not in_git_repo():
        return out
    r = git("status", "--porcelain")
    if r.returncode != 0:
        return out

    for line in r.stdout.splitlines():
        if len(line) < 4:
            continue
        xy = line[:2]
        path = line[3:]
        # Strip rename arrow (porcelain v1: "R  old -> new")
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        # Strip optional quoting around filenames with special chars
        if path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
        full = WORKSPACE_ROOT / path
        if xy == "??" and not full.exists():
            out["phantoms"].append(("phantom-untracked", path))
        elif "D" in xy and full.exists():
            out["phantoms"].append(("phantom-deleted", path))
        if "D" in xy:
            out["deletions"] += 1

    if out["phantoms"]:
        out["safe"] = False
        out["reason"] = f"{len(out['phantoms'])} phantom git-status entries (Drive stat-cache desync)"
    elif out["deletions"] > STALE_DELETION_THRESHOLD:
        out["safe"] = False
        out["reason"] = (
            f"{out['deletions']} deletions in status (> threshold {STALE_DELETION_THRESHOLD}) — "
            f"probable stale worktree relative to HEAD"
        )
    return out


def _content_hash_stage(rel_paths: list[str]) -> int:
    """Stage files via hash-object + update-index --cacheinfo, bypassing stat-cache.

    For each path, compute the on-disk content hash and compare to the index hash.
    If they differ, write the blob to the object store and force the index to point
    at it. This is the only reliable way to commit edits when Drive's stat-cache
    has lied to git.

    Returns the count of files actually staged (i.e., where content hash diverged).
    """
    staged = 0
    for rel in rel_paths:
        full = WORKSPACE_ROOT / rel
        if not full.exists():
            continue
        h = git("hash-object", "-w", "--", rel)
        if h.returncode != 0:
            continue
        disk_hash = h.stdout.strip()
        if not disk_hash:
            continue
        ls = git("ls-files", "-s", "--", rel)
        index_hash = ""
        if ls.stdout.strip():
            parts = ls.stdout.split()
            if len(parts) >= 2:
                index_hash = parts[1]
        if disk_hash != index_hash:
            up = git("update-index", "--add", "--cacheinfo", f"100644,{disk_hash},{rel}",
                     timeout=GIT_WRITE_TIMEOUT_S)
            if up.returncode == 0:
                staged += 1
    return staged


def _write_desync_notice(state: dict, staged_count: int) -> None:
    """Write a notice the next SessionStart will surface as a warning."""
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        when = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        phantoms = state.get("phantoms", [])
        deletions = state.get("deletions", 0)
        reason = state.get("reason", "(unspecified)")
        body = [
            f"# Auto-commit safety fallback — {when}",
            "",
            "Last session-end aborted `git add -A` and used content-hash staging "
            "on the safe-paths allowlist instead.",
            "",
            f"**Trigger:** {reason}",
            "",
            f"**Files committed via fallback:** {staged_count}",
            "",
            "## Why this matters",
            "",
            "`git add -A` would have staged the entries below as deletions. If those entries "
            "are phantoms (Drive stat-cache lying) OR if this working tree is stale relative to "
            "HEAD (a worktree that didn't pick up recent commits), committing those deletions "
            "could destroy real files on `main`.",
            "",
            "## Recovery",
            "",
            "1. Run `git status` from the canonical workspace root once Drive sync settles, or",
            "2. If this was a Claude Code worktree, `git pull --rebase` the worktree so its "
            "filesystem reflects HEAD before next session, or",
            "3. Inspect the phantom list below and reconcile manually.",
            "",
            f"## Status entries flagged ({len(phantoms)} phantom · {deletions} deletion total)",
            "",
        ]
        for kind, path in phantoms[:25]:
            body.append(f"- **{kind}** — `{path}`")
        if len(phantoms) > 25:
            body.append(f"- _... and {len(phantoms) - 25} more_")
        DESYNC_NOTICE.write_text("\n".join(body) + "\n", encoding="utf-8")
    except Exception:
        pass


def _check_linear_lanes() -> str:
    """Open Agent Engine lane preflight for THIS surface — '' when healthy (the common case).

    Deterministic and cheap: filesystem + MCP-config inspection, no network, no credentials.
    Delegates to 00-bootstrap/doctor/linear-lanes.py so Cursor and any other surface run the
    same check. Fails silent — a broken detector must never block a session start.
    """
    script = WORKSPACE_ROOT / "00-bootstrap" / "doctor" / "linear-lanes.py"
    if not script.is_file():
        return ""
    try:
        out = subprocess.run(
            [sys.executable, str(script), "--notice", "--surface", "claude-code"],
            capture_output=True, text=True, timeout=5,
        )
    except Exception:
        return ""
    return out.stdout.strip()


def _read_desync_notice() -> str:
    """Return a one-line summary of the last desync notice for SessionStart, or ''."""
    if not DESYNC_NOTICE.exists():
        return ""
    try:
        text = DESYNC_NOTICE.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"^# Auto-commit safety fallback — (.+)$", text, re.MULTILINE)
        when = m.group(1).strip() if m else "(unknown time)"
        return (
            f"Auto-commit safety fallback fired at last session-end ({when}). "
            f"`git add -A` was aborted; only safe-paths were committed via content-hash. "
            f"See `.claude/state/desync-notice.md` for the trigger and phantom list."
        )
    except Exception:
        return ""


def _compact_session_fragments() -> None:
    """Fold 06-context/sessions/*.md fragments into session-log.md (idempotent).
    Non-fatal: session maintenance must never break a session start."""
    tool = WORKSPACE_ROOT / "09-tools" / "compact-sessions.py"
    if not tool.exists():
        return
    try:
        subprocess.run([sys.executable, str(tool), "--quiet"],
                       cwd=str(WORKSPACE_ROOT), capture_output=True, text=True, timeout=20)
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"[session-start] session compaction skipped: {exc}\n")


def _ensure_drive_safe_git_config() -> None:
    """Set conservative stat-cache config to reduce Drive flakiness, and pin
    rebase.autoStash off so the cross-machine auto-sync can never stash-and-strand
    a live editing session's uncommitted work (a dirty-tree `pull --rebase` refuses
    instead). Not load-bearing — the content-hash fallback is the real safety net —
    but it keeps the safe default from drifting if a global config ever flips it.
    """
    if not in_git_repo():
        return
    for key, value in [("core.checkStat", "minimal"), ("core.trustctime", "false"),
                       ("rebase.autoStash", "false")]:
        try:
            existing = git("config", "--local", "--get", key).stdout.strip()
            if existing != value:
                git("config", "--local", key, value)
        except Exception:
            continue


def _ensure_executable_bits() -> None:
    """Restore +x on tracked-as-executable scripts that Drive may have stripped.

    Google Drive for Desktop on macOS sometimes drops the +x bit during sync transit,
    turning a tracked `100755` script into an on-disk `100644`. Functionally harmless
    when the file is invoked via an explicit interpreter (e.g., `python3 dispatcher.py`),
    but produces phantom mode-change diffs in `git status`. Restoring the bit at every
    session-start keeps the tree clean without manual `chmod +x`.
    """
    if not in_git_repo() or sys.platform.startswith("win"):
        return
    try:
        result = git("ls-tree", "-r", "HEAD")
        if not result.stdout:
            return
        healed: list[str] = []
        for line in result.stdout.splitlines():
            # Format: <mode> <type> <hash>\t<path>
            parts = line.split(None, 3)
            if len(parts) < 4 or parts[0] != "100755":
                continue
            rel_path = parts[3]
            full = WORKSPACE_ROOT / rel_path
            if not full.is_file():
                continue
            try:
                current = full.stat().st_mode
            except OSError:
                continue
            if current & 0o100:  # owner-execute already set; nothing to do
                continue
            try:
                full.chmod(current | 0o111)
                healed.append(rel_path)
            except OSError:
                continue
        if healed:
            sys.stderr.write(
                "[session-start] restored +x on Drive-stripped scripts: "
                + ", ".join(healed) + "\n"
            )
    except Exception:
        return


def _scan_active_projects(projects_dir: Path) -> list[tuple[str, str]]:
    """For each 07-projects/*/SESSION-STATE.md, return (project_name, 'last-updated - first-entry-title')."""
    if not projects_dir.exists():
        return []
    out = []
    for child in sorted(projects_dir.iterdir()):
        if not child.is_dir() or child.name.startswith("_"):
            continue
        state_file = child / "SESSION-STATE.md"
        if not state_file.exists():
            continue
        try:
            text = state_file.read_text(encoding="utf-8", errors="replace")
            updated = ""
            m = re.search(r"_Last updated:\s*(\d{4}-\d{2}-\d{2})", text)
            if m:
                updated = m.group(1)
            # First session-history entry's title (skip the leading date — redundant with _Last updated)
            entry_title = ""
            after_history = text.split("## Session history", 1)
            if len(after_history) == 2:
                m2 = re.search(
                    r"^###\s+\d{4}-\d{2}-\d{2}\s+[—–-]\s+(.+?)\s*$",
                    after_history[1],
                    re.MULTILINE,
                )
                if m2:
                    entry_title = m2.group(1).strip()
            if updated and entry_title:
                summary = f"{updated} - {entry_title}"
            else:
                summary = updated or entry_title or "(no state info)"
            out.append((child.name, summary))
        except Exception:
            continue
    return out


def _format_worktree_cleanup_notice(cleaned: list[str], skipped: list[str]) -> str:
    """Compose a one-paragraph SessionStart notice about worktree cleanup, or ''."""
    if not cleaned and not skipped:
        return ""
    parts = []
    if cleaned:
        parts.append(
            f"Auto-removed {len(cleaned)} stale worktree(s): " + ", ".join(f"`{c}`" for c in cleaned)
        )
    if skipped:
        parts.append(
            f"{len(skipped)} worktree(s) need manual review:\n" +
            "\n".join(f"  - {s}" for s in skipped[:5]) +
            (f"\n  - _... and {len(skipped) - 5} more_" if len(skipped) > 5 else "")
        )
    return ". ".join(parts) + "."


def _portable_session_card(surface: str, via: str) -> str:
    """Same ritual card Cursor and other LLMs emit. Fail-open."""
    script = WORKSPACE_ROOT / "09-tools" / "session-status.py"
    if not script.is_file():
        return ""
    try:
        r = subprocess.run(
            [sys.executable, str(script), "--surface", surface, "--via", via],
            cwd=str(WORKSPACE_ROOT),
            capture_output=True,
            text=True,
            timeout=8,
        )
        return (r.stdout or "").strip()
    except Exception:
        return ""


def build_session_start_context(
    machine: str,
    now: datetime,
    cleaned_worktrees: list[str] | None = None,
    skipped_worktrees: list[str] | None = None,
    via: str = "project-hook/startup",
) -> str:
    """Assemble the structured + raw context block injected at SessionStart.

    The ritual card is `09-tools/session-status.py` (shared with Cursor). Claude-only
    notices (version pin, desync, Linear lanes, worktree cleanup) append above it.
    """
    version_notice = _check_claude_version_change()
    desync_notice = _read_desync_notice()
    lanes_notice = _check_linear_lanes()
    extra: list[str] = []
    if version_notice:
        extra.append(f"⚠ {version_notice}")
    if desync_notice:
        extra.append(f"⚠ {desync_notice}")
    if lanes_notice:
        extra.append(f"⚠ {lanes_notice}")
    worktree_notice = _format_worktree_cleanup_notice(
        cleaned_worktrees or [], skipped_worktrees or []
    )
    if worktree_notice:
        extra.append(f"ℹ {worktree_notice}")

    card = _portable_session_card("Claude Code", via)
    if extra:
        prefix = "\n".join(f"- {n}" for n in extra) + "\n\n"
        card = prefix + card if card else prefix.rstrip()
    if not card:
        # Fallback if the portable script is missing on this machine.
        last_sess = _parse_last_session_entry(SESSION_LOG)
        pending = _count_pending_items(PROJECT_CONTEXT)
        projects = _scan_active_projects(WORKSPACE_ROOT / "07-projects")
        git_state = _describe_git_state()
        project_lines = "\n".join(f"  - {name}: {summary}" for name, summary in projects) or "  (none found)"
        card = (
            f"[workspace: LOADED · via:{via}]\n"
            f"- last_session: {last_sess or '(none in log)'}\n"
            f"- pending_count: {pending}\n"
            f"- git_state: {git_state or '(no git)'}\n"
            f"- active_projects ({len(projects)}):\n{project_lines}"
        )

    session_log_head = read_head(SESSION_LOG, 20)
    project_ctx_head = read_head(PROJECT_CONTEXT, 20)

    knowledge_block = """
## Knowledge vault
Do **not** ingest `08-knowledge/_INDEX.md`. Match via Layer 0 (`knowledge-hints.json` +
entry `Triggers:`). Read only the matched file. Path: `08-knowledge/_INDEX.md`.
""" if KNOWLEDGE_INDEX.exists() else ""

    return f"""# Workspace session context (auto-loaded)

Render the ritual card below as your first reply, then answer.

{card}

## Recent session log (head)
```
{session_log_head}
```

## Project context (head — pending items first)
```
{project_ctx_head}
```
{knowledge_block}
_Full context: `06-context/project-context.md`, `06-context/session-log.md`,_
_`06-context/role-and-context.md`, `04-preferences/user-preferences.md`._
_Frameworks: `01-frameworks/00-README.md`._
_Lexical fallback (when triggers miss): `python3 09-tools/vault-retrieve.py \"…\"` —_
_FTS over vault; paths + TL;DRs. Layer 0 triggers still win on exact routes._
_The mandatory session-start ritual is the card above (09-tools/session-status.py)._
"""


def _find_canonical_workspace_root(start: Path | None = None) -> Path | None:
    """Walk up from `start` (default CWD) looking for the canonical workspace
    root — the topmost directory with `.claude/`, `01-frameworks/`, and
    `06-context/` that is NOT itself inside a `.claude/worktrees/` path.

    Used to heal the canonical workspace's `.git` pointer even when the
    current session is running from a worktree (e.g. `.claude/worktrees/<name>/`),
    where `WORKSPACE_ROOT` would otherwise resolve to the worktree, not
    the canonical workspace.
    """
    cur = (start or Path.cwd()).resolve()
    for candidate in [cur, *cur.parents]:
        s = str(candidate)
        if "/.claude/worktrees/" in s or "\\.claude\\worktrees\\" in s:
            continue
        if (
            (candidate / ".claude").is_dir()
            and (candidate / "01-frameworks").is_dir()
            and (candidate / "06-context").is_dir()
        ):
            return candidate
    return None


def _heal_gitdir_pointer(git_path: Path, expected: str, store: Path) -> bool:
    """Rewrite a single .git gitfile to `expected` if it doesn't already match
    and isn't a worktree pointer. Returns True if it actually rewrote.
    """
    if not git_path.exists() or git_path.is_dir():
        return False
    try:
        actual = git_path.read_text(encoding="utf-8")
    except Exception:
        return False
    if actual == expected:
        return False
    # Don't stomp per-worktree pointers; they have a /worktrees/ segment.
    if "/worktrees/" in actual:
        return False
    if not store.exists():
        sys.stderr.write(
            f"[session-start] .git pointer at {git_path} doesn't match this machine "
            f"and local store is missing at {store}. See 00-bootstrap/OBSIDIAN-SETUP.md "
            f"→ 'Git store lives off Drive' for one-time setup.\n"
        )
        return False
    try:
        git_path.write_text(expected, encoding="utf-8")
        sys.stderr.write(f"[session-start] rewrote .git pointer at {git_path} → {store}\n")
        return True
    except Exception as exc:
        sys.stderr.write(f"[session-start] failed to rewrite .git pointer at {git_path}: {exc}\n")
        return False


def ensure_local_gitdir() -> None:
    """Auto-rewrite workspace .git pointer files to match this machine's local
    git store. Heals BOTH the canonical workspace pointer AND the current
    WORKSPACE_ROOT pointer when they differ.

    The workspace uses --separate-git-dir so .git/ lives off Drive. The .git
    pointer file itself IS Drive-synced, so each machine's pointer overwrites
    the previous machine's. This self-heals on SessionStart so the user never
    has to fix it manually — even when the session is running inside a worktree
    (where WORKSPACE_ROOT resolves to the worktree, not the canonical workspace,
    and the canonical pointer would otherwise stay broken until a session ran
    at the workspace root).

    No-op if: pointer matches, pointer is a directory (full repo), pointer is
    a worktree pointer (would orphan it), or local store doesn't exist (warn).

    Override the default store path with the CLAUDE_WORKSPACE_GIT_STORE env var.
    """
    default_store = Path.home() / ".git-stores" / "workspace"
    store = Path(os.environ.get("CLAUDE_WORKSPACE_GIT_STORE", str(default_store)))
    expected = f"gitdir: {store.as_posix()}\n"

    # Always check WORKSPACE_ROOT/.git (covers the canonical-workspace session).
    _heal_gitdir_pointer(WORKSPACE_ROOT / ".git", expected, store)

    # Also check the canonical workspace's .git when running from a worktree.
    # Without this, a worktree session would leave the canonical pointer broken
    # on this machine for the next non-worktree git operation.
    canonical = _find_canonical_workspace_root(WORKSPACE_ROOT)
    if canonical and canonical != WORKSPACE_ROOT:
        _heal_gitdir_pointer(canonical / ".git", expected, store)


# ---------- Handlers ----------


def build_reorientation_context(machine: str, now: datetime, source: str) -> str:
    """Compact re-orientation block for compact/resume session starts.

    Compaction is exactly the moment the boot-time foundations injection gets
    summarized away — re-inject the load discipline and the knowledge index so
    mid-session work doesn't decay into freestyling (the 2026-07-08 failure mode)."""
    source_label = {"compact": "compacted", "resume": "resumed"}.get(source, source)
    return f"""# Workspace re-orientation (context was {source_label})

**Machine:** {machine} · **Date:** {now.strftime('%Y-%m-%d %H:%M %Z')}

Standing discipline (unchanged by compaction):
- Load skills per the AGENTS.md precedence algorithm — triggers → load chain, foundation-first.
- Foundational color/UX/a11y baseline (system-agnostic): `03-skills/design-foundations/SKILL.md`,
  `03-skills/found-color/SKILL.md`, `03-skills/a11y-visual/SKILL.md`.
- When authoring inside a specific design system, resolve within THAT system's own
  tokens/variables (read its DESIGN.md / connected libraries). Missing tokens/features go to
  the backlog (`06-context/project-context.md` → Pending Items); never import another
  system's conventions into a system that doesn't use them.
- QA pre-output gate: `01-frameworks/06-qa-operating-model.md` — runs before any deliverable,
  including canvas writes.

## Knowledge vault
Do **not** ingest `_INDEX.md`. Match via Layer 0 (`knowledge-hints.json` + entry Triggers).
Read only the matched file. Lexical fallback: `python3 09-tools/vault-retrieve.py "…"`.
"""


def handle_session_start(payload: dict) -> None:
    now = datetime.now().astimezone()
    machine = resolve_machine_label()
    source = (payload.get("source") or "startup").lower()

    # Post-compaction / resume: the original boot injection is gone or stale in the
    # summarized context. Re-inject a compact re-orientation block and skip the
    # filesystem side effects (healing/cleanup already ran at true startup).
    if source in ("compact", "resume"):
        emit_context(build_reorientation_context(machine, now, source), "SessionStart")
        _write_session_baseline(payload, source)
        return

    ensure_local_gitdir()
    _ensure_executable_bits()
    # Fold any per-session fragments into session-log.md before the boot-read below,
    # so this session opens with the latest reconciled history. Idempotent + safe.
    _compact_session_fragments()
    # Refresh the lexical FTS index so UserPromptSubmit --cached queries stay current.
    _refresh_vault_retrieve_index()
    # Auto-clean stale Drive-resident worktrees whose branches are fully merged.
    # Runs only when this session is in the canonical workspace root (not inside a
    # worktree itself) — that's the natural moment to clean the prior session's
    # leftover worktree without race conditions.
    cleaned: list[str] = []
    skipped: list[str] = []
    if not _is_inside_linked_worktree():
        try:
            cleaned, skipped = _cleanup_stale_worktrees()
        except Exception as exc:
            sys.stderr.write(f"[session-start] worktree cleanup error: {exc}\n")
    emit_context(
        build_session_start_context(
            machine, now, cleaned, skipped, via=f"project-hook/{source}"
        ),
        "SessionStart",
    )
    _write_session_baseline(payload, source)


def _write_session_baseline(payload: dict, source: str) -> None:
    """Record this session's starting porcelain (ws_hook.write_baseline, workspace only),
    so `nightly --scope session:<sid>` can tell this session's edits from older dirt.
    A resumed or compacted session keeps the baseline it started with. Fail-open."""
    try:
        sid = str(payload.get("session_id") or "")
        existing = WORKSPACE_ROOT / ".workspace" / "state" / "sessions" / f"{sid}.json"
        if source in ("compact", "resume") and sid and existing.is_file():
            return
        ws_hook = _vault_module("ws_hook")
        if ws_hook is not None:
            ws_hook.write_baseline(payload, WORKSPACE_ROOT)
    except Exception:  # noqa: BLE001 — a baseline is an accelerator, never a blocker
        pass


LEXICAL_TOOL = WORKSPACE_ROOT / "09-tools" / "vault-retrieve.py"


def _refresh_vault_retrieve_index() -> None:
    """Keep the lexical index fresh at SessionStart. Non-fatal."""
    if not LEXICAL_TOOL.exists():
        return
    try:
        subprocess.run(
            [sys.executable, str(LEXICAL_TOOL), "--rebuild", "--quiet"],
            cwd=str(WORKSPACE_ROOT),
            capture_output=True,
            text=True,
            timeout=60,
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"[session-start] vault-retrieve rebuild skipped: {exc}\n")


def handle_user_prompt(payload: dict) -> None:
    """Delegate Layer 0 + Layer 1 to the ONE shared matcher (09-tools/prompt_route.py).

    This used to be a second full implementation of the tier machinery, and it drifted:
    on 2026-09-15 six of the 48 routing fixtures delivered a different file set here than
    on Cursor — Cursor had no lexical fallback, and this copy deduped a knowledge hint
    away when the same trigger had already produced a curated hit. Same vault, same
    utterance, different context. One matcher is the only shape that cannot drift;
    `evaluate-surface-trajectories.py` is what keeps it honest.
    """
    raw_prompt = payload.get("prompt") or ""
    if not raw_prompt:
        return
    tools = WORKSPACE_ROOT / "09-tools"
    if str(tools) not in sys.path:
        sys.path.insert(0, str(tools))
    try:
        import prompt_route  # noqa: PLC0415
    except Exception as exc:  # noqa: BLE001 — never block the session
        sys.stderr.write(f"[user-prompt] prompt_route unavailable: {exc}\n")
        return
    injection = prompt_route.route_payload(payload, "claude-code", WORKSPACE_ROOT)
    if injection:
        emit_context(injection, "UserPromptSubmit")


# Tool names that put pixels on a canvas Sean will inspect. First call per session
# is denied once with the design-judgment gate below; the retry passes. This is the
# only layer immune to session length and compaction — every advisory layer above it
# (boot injection, prompt triggers, skill descriptions) is skippable under execution
# momentum, and on 2026-07-08 all of them were skipped at once.
FIGMA_WRITE_TOOL_PATTERN = re.compile(r"use_figma", re.IGNORECASE)
FIGMA_GATE_STATE_DIR = STATE_DIR / "figma-gate"
FIGMA_GATE_TTL_DAYS = 7

FIGMA_GATE_TEXT = """FIGMA DESIGN-JUDGMENT GATE (fires ONCE per session — after reading this, simply re-issue the exact same tool call and it will proceed).

This gate prompts skill-loading and judgment. It is NOT a ruleset — design decisions are
made in context, by you, through the right lenses.

1. LOAD THE LENS (if not already loaded): 03-skills/design-foundations/SKILL.md +
   03-skills/found-color/SKILL.md + 03-skills/a11y-visual/SKILL.md +
   03-skills/uid-color-for-ui/SKILL.md — the system-agnostic color/UX/a11y baseline.
2. TARGET SYSTEM FIRST. Identify the design system this file/library belongs to. Read its
   DESIGN.md (if the project has one), its connected Figma libraries, and its variable
   collections. Select tokens by their object context (fill vs border vs text scope).
   Don't import another system's conventions (Radix steps, Tailwind shades, shadcn slots)
   into a system that doesn't use them.
3. DESIGN WITH JUDGMENT; VERIFY A11Y. Palette, emphasis, and composition choices — including
   full-color, full-bleed surfaces carrying text or icons — are legitimate whenever the
   implementation makes sense from a UI/UX/a11y perspective. What is non-negotiable is
   verification, not any fixed palette rule: every foreground/background pairing is
   legibility-checked (APCA preferred, WCAG AA fallback), and status meaning never rides
   on color alone (CVD redundancy).
4. TOKEN GAPS GO TO THE BACKLOG; WORK CONTINUES. If the target system lacks something you
   need, derive minimally within its constraints — e.g. the right semantic token, detached
   to control opacity when that is the system's only lever (an emblematic example, not a
   rule) — and note the gap in 06-context/project-context.md -> Pending Items. A11y
   compliance itself is never deferred: what ships now must pass now.
5. VERIFY AFTER WRITE at meaningful zoom (screenshot), per the pre-output gate in
   01-frameworks/06-qa-operating-model.md."""


def _prune_gate_markers() -> None:
    """Drop gate markers older than the TTL so .claude/state/ doesn't accumulate."""
    try:
        cutoff = datetime.now(timezone.utc).timestamp() - FIGMA_GATE_TTL_DAYS * 86400
        for f in FIGMA_GATE_STATE_DIR.iterdir():
            if f.is_file() and f.stat().st_mtime < cutoff:
                f.unlink()
    except Exception:
        pass


def handle_pre_tool(payload: dict) -> None:
    tool = payload.get("tool_name") or ""
    if not FIGMA_WRITE_TOOL_PATTERN.search(tool):
        return  # no output = proceed normally
    session = payload.get("session_id") or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    marker = FIGMA_GATE_STATE_DIR / re.sub(r"[^A-Za-z0-9_.-]", "_", str(session))
    if marker.exists():
        return  # gate already shown this session — allow silently
    try:
        FIGMA_GATE_STATE_DIR.mkdir(parents=True, exist_ok=True)
        marker.write_text(datetime.now(timezone.utc).isoformat() + "\n", encoding="utf-8")
        _prune_gate_markers()
    except Exception:
        return  # if state can't be written, never wedge the session in a deny loop
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": FIGMA_GATE_TEXT,
        }
    }))


_EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit", "Update"}
SESSIONS_DIR = WORKSPACE_ROOT / "06-context" / "sessions"


def _session_touch_file(session_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9._-]", "-", session_id)[:80]
    return SESSIONS_DIR / f"{safe}.touched"


def _rel_to_workspace(p: str) -> str | None:
    """Return the workspace-relative path if p is inside the workspace, else None."""
    try:
        rp = Path(p).resolve()
        return str(rp.relative_to(WORKSPACE_ROOT))
    except (ValueError, OSError):
        return None


def handle_post_tool(payload: dict) -> None:
    """Record files THIS session edited, so session-end can scope its commit to them
    (never sweeping a concurrent session's in-flight edits). Append-only per session
    → conflict-free. Transient (*.touched is gitignored)."""
    if (payload.get("tool_name") or "") not in _EDIT_TOOLS:
        return
    session_id = payload.get("session_id")
    if not session_id:
        return  # no id → session-end falls back to `git add -A`
    ti = payload.get("tool_input") or {}
    fp = ti.get("file_path") or ti.get("notebook_path") or ti.get("path")
    if not fp:
        return
    rel = _rel_to_workspace(fp)
    if not rel:
        return  # edit outside the workspace — not ours to commit
    try:
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        tf = _session_touch_file(session_id)
        existing = set(tf.read_text(encoding="utf-8").splitlines()) if tf.exists() else set()
        if rel not in existing:
            with tf.open("a", encoding="utf-8") as f:
                f.write(rel + "\n")
    except OSError:
        pass  # tracking is best-effort; never disrupt a tool call


def _dirty_paths() -> set[str]:
    """Every path git currently reports as changed or untracked."""
    r = git("status", "--porcelain", check=False)
    out: set[str] = set()
    for line in (r.stdout or "").splitlines():
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:               # rename: credit the destination
            path = path.split(" -> ", 1)[1]
        out.add(path.strip().strip('"'))
    return out


def _session_snapshot_file(session_id: str):
    return SESSIONS_DIR / f"{session_id}.dirty"


def _record_bash_writes(session_id: str) -> None:
    """Attribute paths that went dirty during this turn to this session.

    PostToolUse only sees Edit/Write tool inputs, so anything written through Bash —
    a heredoc, `sed`, `python3 -` — was invisible to the touch-list. Measured
    2026-09-15: 8 recorded paths against 67 the session actually changed, which meant
    session-end fell through to a blanket `git add -A` and swept a concurrent session's
    work into the wrong commit.

    Snapshot-and-diff once per turn (here) rather than once per Bash call: same
    attribution, a fraction of the cost on a hot path.

    Residual race, stated rather than hidden: a file another session dirties *between
    my turns* is credited to me. That is strictly narrower than `git add -A`, and
    `_other_session_claims()` subtracts it back out whenever that session has declared
    the path itself.
    """
    if not session_id:
        return
    snap = _session_snapshot_file(session_id)
    try:
        previous = set(snap.read_text(encoding="utf-8").splitlines()) if snap.exists() else set()
        current = _dirty_paths()
        new_paths = current - previous
        if new_paths:
            tf = _session_touch_file(session_id)
            known = set(tf.read_text(encoding="utf-8").splitlines()) if tf.exists() else set()
            add = sorted(p for p in new_paths if p and p not in known)
            if add:
                SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
                with tf.open("a", encoding="utf-8") as f:
                    f.write("\n".join(add) + "\n")
        snap.write_text("\n".join(sorted(current)) + "\n", encoding="utf-8")
    except OSError:
        pass  # best-effort; never disrupt the turn


def handle_stop(payload: dict) -> None:
    # Light-touch. No-op unless session-log.md was modified in the last turn —
    # then stage it so the session-end commit captures it cleanly.
    if not in_git_repo():
        return
    _record_bash_writes(payload.get("session_id") or "")
    r = git("diff", "--name-only", "--", "06-context/session-log.md")
    if r.stdout.strip():
        git("add", "06-context/session-log.md", timeout=GIT_WRITE_TIMEOUT_S)


# Paths every session-end must stage regardless of tool tracking (the reconciled
# log, fragment add/removal, and a possibly-regenerated registry).
_SCOPE_ALWAYS = ["06-context/session-log.md", "06-context/sessions",
                 "03-skills/skills.registry.json"]


def _other_session_claims(session_id: str) -> set[str]:
    """Paths declared by every OTHER session's touch file — never ours to commit."""
    claims: set[str] = set()
    try:
        for tf in SESSIONS_DIR.glob("*.touched"):
            if tf.stem == session_id:
                continue
            claims.update(ln.strip() for ln in tf.read_text(encoding="utf-8").splitlines()
                          if ln.strip())
    except OSError:
        pass
    return claims


def _stage_session_scope(payload: dict, extra: list[str] | None = None,
                         exclude: set[str] | None = None) -> str:
    """Stage this session's changes. Returns 'scoped' when a PostToolUse touch-list
    exists (commit limited to this session's files), else 'all' (blanket `git add -A`
    fallback, backward compatible). Scoping is what keeps concurrent sessions from
    committing each other's in-flight work.

    `extra` = paths the session-end rebuild WROTE (minus foreign ones), so rewritten
    Related blocks and the registry ride with the edit that caused them. `exclude` =
    paths that must never be staged here: foreign edits, and generator output from a
    rebuild that was SKIPPED or FAILED."""
    extra = list(extra or [])
    exclude = set(exclude or ())
    session_id = payload.get("session_id")
    touched: list[str] = []
    if session_id:
        tf = _session_touch_file(session_id)
        if tf.exists():
            touched = [ln.strip() for ln in tf.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not touched:
        git("add", "-A", timeout=GIT_WRITE_TIMEOUT_S)
        if exclude:
            git("reset", "-q", "--", *sorted(exclude), timeout=GIT_WRITE_TIMEOUT_S)
        return "all"
    # Subtract what OTHER live sessions have claimed. Each session declares its own
    # paths in its own touch file, so a path another session is mid-edit on is theirs
    # even if it went dirty on our watch — this is what the snapshot race above cannot
    # resolve on its own, and it is the concrete failure observed 2026-09-15.
    theirs = _other_session_claims(session_id)
    mine = [p for p in touched if p not in theirs]
    # Stage add/mod/del for exactly this session's paths + the always-staged set + what
    # the rebuild wrote. Per-path + check=False so one stale pathspec never aborts the
    # whole stage.
    seen: set[str] = set()
    for path in mine + _SCOPE_ALWAYS + extra:
        if path in seen or path in exclude:
            continue
        seen.add(path)
        git("add", "-A", "--", path, check=False, timeout=GIT_WRITE_TIMEOUT_S)
    if exclude:
        # A directory pathspec above (06-context/sessions) may have swept one in.
        git("reset", "-q", "--", *sorted(exclude), timeout=GIT_WRITE_TIMEOUT_S)
    try:
        tf = _session_touch_file(session_id)
        tf.unlink()  # consume the touch-list; it's transient + gitignored
    except OSError:
        pass
    return "scoped"


def _remaining(deadline: float | None, cap: float) -> float:
    if deadline is None:
        return cap
    return max(0.0, min(cap, deadline - time.monotonic()))


def _push_with_retry(attempts: int = 3, deadline: float | None = None) -> bool:
    """Push, integrating any commits another machine pushed first — safely.

    On a non-fast-forward rejection: `git pull --rebase` (autostash is pinned OFF, so
    it REFUSES over a dirty tree rather than stashing — see _ensure_drive_safe_git_config).
    Union-merge (session-log.md/audit-log.md) auto-resolves during the rebase; a real
    conflict in a structured file (project-context.md) aborts the rebase and is left
    for a deliberate /reconcile — never auto-guessed. In every failure path the local
    commit is SAFE (committed, just not yet pushed); a later clean session-end or
    /reconcile carries it up. Idempotent + non-lossy. Every network call is bounded by
    the SessionEnd `deadline`.
    """
    for _ in range(attempts):
        budget = _remaining(deadline, GIT_WRITE_TIMEOUT_S)
        if budget < 1.0:
            sys.stderr.write("[session-end] push deferred: SessionEnd budget spent; "
                             "your commit is safe locally.\n")
            return False
        # H11: a report-only pre-push gate reuses this tree's verdict or detaches the verify
        # instead of waiting up to 20 s for it (git_lanes WS_GATE_NOWAIT; ignored under block).
        push = git("push", timeout=budget, env=dict(os.environ, WS_GATE_NOWAIT="1"))
        if push.returncode == 0:
            return True
        err = ((push.stderr or "") + (push.stdout or "")).lower()
        if not any(s in err for s in ("non-fast-forward", "fetch first", "rejected", "behind")):
            sys.stderr.write(f"[session-end] push failed (not a race): {push.stderr.strip()}\n")
            return False
        # Remote moved. Integrate it by rebasing our commit on top.
        budget = _remaining(deadline, GIT_WRITE_TIMEOUT_S)
        pull = git("pull", "--rebase", timeout=max(budget, 1.0))
        if pull.returncode != 0:
            git("rebase", "--abort", check=False, timeout=GIT_WRITE_TIMEOUT_S)  # no-op if not mid-rebase
            sys.stderr.write(
                "[session-end] push deferred: remote moved and the local tree/rebase "
                "isn't clean (a concurrent session's edits, or a structured-file "
                "conflict). Your commit is safe locally; it will sync on a later clean "
                "session-end or `/reconcile`.\n")
            return False
        # Rebased cleanly (union/fragment files merged automatically) — retry push.
    sys.stderr.write("[session-end] push still racing after retries; commit is safe locally.\n")
    return False


# SessionEnd budget invariant (H1): heal, commit and push together stay <= 55 s, under
# Claude's 60 s SessionEnd maximum. The rebuild gets max(5, 55 - elapsed - 20) seconds;
# the 20 s reserve covers staging, commit, last-gate.json and push.
SESSION_END_BUDGET_S = 55.0
SESSION_END_RESERVE_S = 20.0
LAST_GATE = WORKSPACE_ROOT / ".workspace" / "state" / "last-gate.json"
GENERATED_OUTPUTS = ("03-skills/skills.registry.json", "02-shared-references/trigger-routes.md")


def _current_branch() -> str:
    return git("symbolic-ref", "--short", "-q", "HEAD").stdout.strip()


def _session_rebuild(session_id: str | None, budget: float) -> dict | None:
    """Delegate the regeneration fixpoint to nightly.py. Returns its JSON report, a
    synthetic SKIPPED report on a hard timeout, or None when nightly is unavailable or
    unparseable (the caller then falls back to the inline registry rebuild)."""
    tool = WORKSPACE_ROOT / "09-tools" / "nightly.py"
    if not tool.is_file():
        return None
    scope = f"session:{session_id}" if session_id else "all"
    cmd = [sys.executable, str(tool), "--phases", "rebuild", "--scope", scope, "--json",
           "--budget", f"{budget:.1f}"]
    try:
        r = subprocess.run(cmd, cwd=str(WORKSPACE_ROOT), capture_output=True, text=True,
                           timeout=budget + 5.0)
    except subprocess.TimeoutExpired:
        return {"status": "skipped", "written": [], "foreign": [], "hard_timeout": True}
    except OSError:
        return None
    try:
        report = json.loads(r.stdout)
    except ValueError:
        return None
    if not isinstance(report, dict) or report.get("status") not in ("ok", "fail", "skipped", "refused"):
        return None
    return report


def _inline_registry_rebuild() -> None:
    """Pre-H1 fallback: regenerate the registry when a SKILL.md changed and nightly.py
    is unavailable, so the auto-commit never ships a stale graph."""
    if "SKILL.md" not in git("status", "--porcelain", "--", "03-skills").stdout:
        return
    builder = WORKSPACE_ROOT / "09-tools" / "build-registry.py"
    if not builder.exists():
        return
    try:
        reg = subprocess.run([sys.executable, str(builder)], capture_output=True, text=True,
                             cwd=str(WORKSPACE_ROOT), timeout=20)
    except (OSError, subprocess.TimeoutExpired) as exc:
        sys.stderr.write(f"[session-end] registry regeneration skipped: {exc}\n")
        return
    if reg.returncode != 0:
        sys.stderr.write(f"[session-end] registry regeneration failed: {reg.stderr}\n")
    else:
        sys.stderr.write("[session-end] regenerated skills.registry.json (SKILL.md changed)\n")


def _write_last_gate(nightly_status: str) -> None:
    """Record this rebuild's status for the exact post-commit HEAD tree (workspace only,
    gitignored) as the `nightly` field. The H11 verify record (`gate`, `ring`, written by
    git_lanes) is kept, never clobbered; a `gate` for another tree is dropped from the
    top level only (the ring still holds it). A rebuild is not a verify: pre-push reuses
    only a `gate`/`ring` verdict for the tree."""
    try:
        head = git("rev-parse", "HEAD").stdout.strip()
        tree = git("rev-parse", "HEAD^{tree}").stdout.strip()
        if not head or not tree:
            return
        LAST_GATE.parent.mkdir(parents=True, exist_ok=True)
        try:
            data = json.loads(LAST_GATE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
        if not isinstance(data, dict):
            data = {}
        if data.get("tree") != tree:
            data.pop("gate", None)
            data.pop("held", None)
        data.update({"schema_version": data.get("schema_version") or 1, "head": head, "tree": tree,
                     "nightly": {"status": nightly_status, "phases": ["rebuild"]},
                     "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")})
        tmp = LAST_GATE.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, LAST_GATE)
    except OSError:
        pass


CLOSURE_PLAN_MIN_S = 3.0


def _defer_to_closure(payload: dict, deadline: float) -> None:
    """H23: anything beyond this workspace's own fold/commit/push is closure.py's job. When
    this session's touch ledger names other repos, print the plan for them and act on none.
    Only runs when a ledger exists (no fallback scan in the SessionEnd budget). Fail-open."""
    sid = payload.get("session_id")
    budget = _remaining(deadline, 10.0)
    if not sid or budget < CLOSURE_PLAN_MIN_S:
        return
    ws_hook = _vault_module("ws_hook")
    tool = WORKSPACE_ROOT / "09-tools" / "closure.py"
    try:
        if ws_hook is None or not tool.is_file() or not ws_hook.ledger_path(str(sid)).is_file():
            return
        r = subprocess.run([sys.executable, str(tool), "plan", "--session", str(sid),
                            "--family", "claude", "--json"], cwd=str(WORKSPACE_ROOT),
                           capture_output=True, text=True, timeout=budget)
        plan = json.loads(r.stdout) if r.returncode == 0 else {}
    except Exception:  # noqa: BLE001 — closure is advisory here; never block SessionEnd
        return
    others = [e for e in plan.get("repos") or [] if isinstance(e, dict) and e.get("class") != "workspace"]
    for e in others:
        sys.stderr.write(f"[session-end] {e.get('slug') or e.get('repo')} [{e.get('class')}]: "
                         f"not closed here -> {e.get('action')} (see `ws closure plan --session {sid}`)\n")


def handle_session_end(payload: dict) -> None:
    deadline = _PROCESS_T0 + SESSION_END_BUDGET_S
    try:
        _workspace_session_end(payload, deadline)
    finally:
        _defer_to_closure(payload, deadline)


def _workspace_session_end(payload: dict, deadline: float) -> None:
    if not in_git_repo():
        sys.stderr.write("[session-end] not a git repo; skipping commit/push\n")
        return

    # Wave implementor branches are committed explicitly by their owner. An auto-commit
    # here would stage _SCOPE_ALWAYS or `git add -A` onto the task branch.
    branch = _current_branch()
    if branch.startswith("intent/"):
        sys.stderr.write(f"[session-end] on {branch}: auto-commit and push skipped "
                         "(intent/* branches are committed explicitly by their task)\n")
        return

    _ensure_drive_safe_git_config()
    # Fold this session's fragment into session-log.md so the commit below captures
    # the reconciled log (and the fragment's removal) atomically. Idempotent.
    _compact_session_fragments()

    machine = resolve_machine_label()
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    gate_status = "skipped"

    # Auto-commit safety guard. `git add -A` is unsafe in two cases:
    #   1. Drive stat-cache lies about file existence (phantom entries) → would
    #      commit fictitious deletions and miss real edits.
    #   2. This working tree is stale relative to HEAD (e.g., a Claude Code worktree
    #      that wasn't refreshed) → would commit a deletion of every file the worktree
    #      hasn't yet checked out.
    # Both conditions are caught by inspecting status. On detection, fall back to
    # content-hash staging on a small allowlist of paths where session edits land.
    state = _classify_worktree_state()

    if not state["safe"]:
        sys.stderr.write(
            f"[session-end] AUTO-COMMIT FALLBACK: {state['reason']}. "
            f"Skipping `git add -A`; staging safe paths via content-hash.\n"
        )
        staged = _content_hash_stage(SAFE_STAGE_PATHS)
        _write_desync_notice(state, staged)
        if staged == 0:
            sys.stderr.write("[session-end] no safe-path content drift; nothing to commit\n")
            return
        msg = (
            f"session: auto-commit from {machine} @ {stamp} "
            f"(safe-paths fallback — see .claude/state/desync-notice.md)"
        )
    else:
        # No desync. Clear any stale notice from a previous session.
        if DESYNC_NOTICE.exists():
            try:
                DESYNC_NOTICE.unlink()
            except Exception:
                pass
        status = git("status", "--porcelain").stdout.strip()
        if not status:
            sys.stderr.write("[session-end] no changes to commit\n")
            return
        # Heal BEFORE staging so the auto-commit never ships a stale graph: the
        # regeneration fixpoint runs through nightly.py, scoped to this session, within
        # the SessionEnd budget. Stage the session scope plus what the rebuild wrote,
        # minus foreign edits; never stage generator output from a SKIPPED/FAIL rebuild.
        elapsed = time.monotonic() - _PROCESS_T0
        budget = max(5.0, SESSION_END_BUDGET_S - elapsed - SESSION_END_RESERVE_S)
        session_id = payload.get("session_id")
        report = _session_rebuild(session_id, budget)
        extra: list[str] = []
        exclude: set[str] = set()
        if report is None:
            _inline_registry_rebuild()  # fail-open fallback (pre-H1 behaviour)
        else:
            rstatus = report.get("status")
            written = [p for p in report.get("written") or [] if isinstance(p, str)]
            foreign = {p for p in report.get("foreign") or [] if isinstance(p, str)}
            exclude |= foreign
            if rstatus in ("ok", "refused"):
                extra = [p for p in written if p not in foreign]
                gate_status = "ok" if rstatus == "ok" else "fail"
                if rstatus == "refused":
                    exclude |= set(GENERATED_OUTPUTS)
                    extra = [p for p in extra if p not in GENERATED_OUTPUTS]
            else:
                exclude |= set(written) | set(GENERATED_OUTPUTS)
                gate_status = "fail" if rstatus == "fail" else "skipped"
            if foreign:
                sys.stderr.write("[session-end] left unstaged (another session's edits on "
                                 f"regenerated files): {', '.join(sorted(foreign))}\n")
            if rstatus not in ("ok", "refused"):
                sys.stderr.write(f"[session-end] rebuild {rstatus}: generated files not "
                                 "staged; CI and the next session re-check\n")
        # Stage this session's work. If we tracked which files THIS session edited
        # (PostToolUse), scope the commit to exactly those (+ the reconciled log and
        # fragment churn) so a CONCURRENT session's in-flight edits are never swept
        # into our commit. Otherwise fall back to `git add -A` (backward compatible).
        scope = _stage_session_scope(payload, extra=extra, exclude=exclude)
        msg = f"session: auto-commit from {machine} @ {stamp}"
        if scope == "scoped":
            msg += " (scoped)"

    commit = git("commit", "-m", msg, timeout=max(1.0, _remaining(deadline, GIT_WRITE_TIMEOUT_S)))
    if commit.returncode != 0:
        sys.stderr.write(f"[session-end] commit failed: {commit.stderr}\n")
        return

    # Record the gate for the exact committed tree BEFORE pushing.
    _write_last_gate(gate_status)

    # Push if a remote is configured — safely, idempotently, non-lossily.
    remote = git("remote").stdout.strip()
    if remote:
        _push_with_retry(deadline=deadline)

    # Opportunistic cleanup of OTHER stale worktrees. Skips the current one
    # (git refuses self-removal); next session-start in the canonical workspace
    # root will catch this one. Only when the budget still has room.
    if _remaining(deadline, 60.0) < 5.0:
        return
    try:
        cleaned, _ = _cleanup_stale_worktrees()
        if cleaned:
            sys.stderr.write(f"[session-end] auto-removed worktrees: {', '.join(cleaned)}\n")
    except Exception as exc:
        sys.stderr.write(f"[session-end] worktree cleanup error: {exc}\n")


# ---------- Entry point ----------


HANDLERS = {
    "session-start": handle_session_start,
    "user-prompt": handle_user_prompt,
    "pre-tool": handle_pre_tool,
    "post-tool": handle_post_tool,
    "stop": handle_stop,
    "session-end": handle_session_end,
}


def _self_test() -> int:
    """Hermetic fixtures (temp repos, fake resolver modules, temp HOME). The fixture code
    lives in 09-tools/fixtures/nightly/ so this hot-path file stays small."""
    fx = Path(__file__).resolve().parents[2] / "09-tools" / "fixtures" / "nightly" / "selftest_dispatcher.py"
    if not fx.is_file():
        sys.stderr.write(f"dispatcher self-test: missing {fx}\n")
        return 1
    spec = importlib.util.spec_from_file_location("selftest_dispatcher", fx)
    if spec is None or spec.loader is None:
        return 1
    mod = importlib.util.module_from_spec(spec)
    sys.modules["selftest_dispatcher"] = mod
    spec.loader.exec_module(mod)
    return int(mod.run(Path(__file__).resolve()))


def main() -> int:
    # Never exit 2 on a usage error or an unknown event: exit 2 is a BLOCK for
    # UserPromptSubmit and PreToolUse (and in VS Code).
    if len(sys.argv) < 2:
        sys.stderr.write("dispatcher: no event given; nothing to do\n")
        return 0
    event = sys.argv[1]
    if event == "--self-test":
        return _self_test()
    handler = HANDLERS.get(event)
    if not handler:
        sys.stderr.write(f"dispatcher: unknown event {event!r}; ignored\n")
        return 0
    try:
        payload = read_stdin_json()
        if not isinstance(payload, dict):
            payload = {}
        # Another verified host (Cursor, VS Code) loading .claude/settings.json: no output.
        if _should_defer(payload):
            return 0
        handler(payload)
        return 0
    except Exception as exc:
        sys.stderr.write(f"[{event}] handler error: {exc}\n")
        return 0  # never block the session


if __name__ == "__main__":
    sys.exit(main())
