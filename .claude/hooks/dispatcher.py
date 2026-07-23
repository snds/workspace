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

import json
import os
import re
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
if not _project_dir:
    # Not invoked by Claude Code from a project checkout (stray copy, mis-registered
    # hook). Abort silently rather than treating an arbitrary cwd as the workspace.
    sys.exit(0)
WORKSPACE_ROOT = Path(_project_dir)
CONTEXT_DIR = WORKSPACE_ROOT / "06-context"
SESSION_LOG = CONTEXT_DIR / "session-log.md"
PROJECT_CONTEXT = CONTEXT_DIR / "project-context.md"
AUDIT_LOG = CONTEXT_DIR / "audit-log.md"
STATE_DIR = WORKSPACE_ROOT / ".claude" / "state"
CLAUDE_VERSION_PIN = STATE_DIR / "claude-version"
DESYNC_NOTICE = STATE_DIR / "desync-notice.md"
KNOWLEDGE_DIR = WORKSPACE_ROOT / "08-knowledge"
KNOWLEDGE_INDEX = KNOWLEDGE_DIR / "_INDEX.md"
SKILLS_REGISTRY = WORKSPACE_ROOT / "03-skills" / "skills.registry.json"

CLAUDE_CODE_CHANGELOG_URL = "https://github.com/anthropics/claude-code/releases"
AUDIT_STALE_DAYS = 14

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

HOSTNAME_MAP = {
    "Voyager-2.local": "Personal MacBook Pro",
    "seansands.local": "Work MacBook Pro",
    "CS-KQ23N94M0W": "Work MacBook Pro (loaner)",
    "CS-K746DRWXY1": "Work MacBook Pro (main, going forward)",
    "Enterprise": "Windows Desktop",
}

# Foundational design route — fires on UI status/validation/color/a11y vocabulary.
# The baseline is design-system-AGNOSTIC (design-foundations + found-color + a11y-visual);
# system-specific token rules (Radix, Tailwind, centric-ui) apply ONLY when the target
# system actually uses that system. Missing tokens/features in the target system are
# noted to the backlog (project-context.md Pending Items), never solved by importing
# another system's conventions.
FOUNDATION_ROUTE = (
    "FOUNDATIONS FIRST: 03-skills/design-foundations/SKILL.md + 03-skills/found-color/SKILL.md "
    "+ 03-skills/a11y-visual/SKILL.md + 03-skills/uid-color-for-ui/SKILL.md "
    "(system-agnostic color/UX/a11y baseline). "
    "Then resolve within the TARGET design system's OWN tokens/variables (read its DESIGN.md / "
    "connected Figma libraries); if the target system lacks a needed token, derive minimally "
    "within its constraints and add the gap to the backlog — do not import another system's "
    "conventions (e.g. Radix steps) into a system that doesn't use them. Token gaps are "
    "backloggable; a11y compliance is not deferrable — the delivered artifact must pass now."
)

# NOTE: insertion order IS emission priority — under the per-tier cap (FX-2), rows
# earlier in this dict win. Mandate rows (framework #06 pre-output gate) come first:
# CLAUDE.md requires them loaded "before doing anything else" for audit-class work.
TRIGGER_WORDS = {
    # Audit-class carrier (2026-07-09, FX-4): CLAUDE.md mandates framework #06 for any
    # audit/review/critique/refinement work, but no trigger carried it — the mandate
    # was un-fired on the one session that WAS an audit. Pre-output gate loads FIRST.
    "audit": "01-frameworks/06-qa-operating-model.md — pre-output gate: load BEFORE the work",
    "review": "01-frameworks/06-qa-operating-model.md — pre-output gate: load BEFORE the work",
    "critique": "01-frameworks/06-qa-operating-model.md — pre-output gate: load BEFORE the work",
    "qa pass": "01-frameworks/06-qa-operating-model.md — pre-output gate: load BEFORE the work",
    "refine": "01-frameworks/06-qa-operating-model.md — pre-output gate: load BEFORE the work",
    "legion": "03-skills/legion-project/SKILL.md + appropriate hub (lead-game-designer / lead-art-director / lead-game-developer)",
    "bobiverse": "03-skills/legion-project/SKILL.md",
    "centric": "Centric PLM project context — see 06-context/project-context.md; ds-advisor hub",
    "data table": "Data table cell anatomy work — cross-reference 06-context/artifact-registry.md; knowledge: 08-knowledge/design/enterprise-saas-design-patterns.md",
    "icon font": "03-skills/variable-icon-font-architect/SKILL.md + math spokes",
    "centricsymbols": "03-skills/variable-icon-font-architect/SKILL.md",
    "omni": "03-skills/omni-project/SKILL.md",
    "workspace brain": "07-projects/19-workspace-brain/ — standing home for workspace-subject sessions; read its SESSION-STATE.md Live handoff",
    "workspace fix": "07-projects/19-workspace-brain/ — standing home for workspace-subject sessions; read its SESSION-STATE.md Live handoff",
    "workspace validation": "07-projects/19-workspace-brain/ — standing home for workspace-subject sessions; read its SESSION-STATE.md Live handoff",
    "figma plugin": "03-skills/figma-plugin-dev/SKILL.md",
    "figma": "03-skills/figma-canvas-designer/SKILL.md + 03-skills/design-engineer/SKILL.md — real-library-components rule",
    "design system": "03-skills/ds-advisor/SKILL.md + design-engineer",
    "component": "03-skills/design-engineer/SKILL.md",
    "variant": "03-skills/design-engineer/SKILL.md",
    "mockup": "03-skills/figma-canvas-designer/SKILL.md",
    "wireframe": "03-skills/figma-canvas-designer/SKILL.md",
    # Foundational color / UX-of-color / a11y vocabulary (2026-07-08, added after the
    # cell-validation failure: none of these words routed anywhere before).
    # `validation` narrowed to two-word phrases 2026-07-09 (FX-3): the bare word
    # collided with Proofboard/validation-harness talk and misrouted it to color/a11y.
    "field validation": FOUNDATION_ROUTE,
    "validation state": FOUNDATION_ROUTE,
    "invalid": FOUNDATION_ROUTE,
    "warning": FOUNDATION_ROUTE,
    "error state": FOUNDATION_ROUTE,
    "status color": FOUNDATION_ROUTE,
    "status colors": FOUNDATION_ROUTE,
    "semantic token": FOUNDATION_ROUTE,
    "semantic tokens": FOUNDATION_ROUTE,
    "a11y": FOUNDATION_ROUTE,
    "accessibility": FOUNDATION_ROUTE,
    "contrast": FOUNDATION_ROUTE,
    "legibility": FOUNDATION_ROUTE,
    "legible": FOUNDATION_ROUTE,
    "wcag": FOUNDATION_ROUTE,
    "apca": FOUNDATION_ROUTE,
    "color blind": FOUNDATION_ROUTE,
    "color-blind": FOUNDATION_ROUTE,
    "cvd": FOUNDATION_ROUTE,
    # Delivery playbooks — context is king / audience / medium / evidence (2026-07-09).
    # Resolve the context profile (00-context-profiles.md) before acting on any of these.
    "diagram": "02-shared-references/delivery-playbooks/02-diagrams-and-flows.md — medium is the requirement; resolve context profile (00-context-profiles.md) first",
    "flowchart": "02-shared-references/delivery-playbooks/02-diagrams-and-flows.md — medium is the requirement; resolve context profile (00-context-profiles.md) first",
    "user journey": "02-shared-references/delivery-playbooks/02-diagrams-and-flows.md — medium is the requirement; resolve context profile (00-context-profiles.md) first",
    "how does it work": "02-shared-references/delivery-playbooks/02-diagrams-and-flows.md — medium is the requirement; resolve context profile (00-context-profiles.md) first",
    "show me the steps": "02-shared-references/delivery-playbooks/02-diagrams-and-flows.md — medium is the requirement; resolve context profile (00-context-profiles.md) first",
    "walkthrough": "02-shared-references/delivery-playbooks/README.md — pre-delivery gate: context, audience, translation, medium",
    "proofboard": "02-shared-references/delivery-playbooks/05-validation-harness.md",
    "validation harness": "02-shared-references/delivery-playbooks/05-validation-harness.md",
    "context profile": "02-shared-references/delivery-playbooks/00-context-profiles.md",
    "explain this to": "02-shared-references/delivery-playbooks/01-audience-contract.md — forward test + three-altitude model",
    "explain like": "02-shared-references/delivery-playbooks/01-audience-contract.md — forward test + three-altitude model",
    "eli5": "02-shared-references/delivery-playbooks/01-audience-contract.md — forward test + three-altitude model",
    "present to": "02-shared-references/delivery-playbooks/01-audience-contract.md — forward test + three-altitude model",
    "chart": "02-shared-references/delivery-playbooks/03-data-and-charts.md — audience layer on top of the dataviz skill",
    "write a spec": "02-shared-references/delivery-playbooks/04-documents-and-specs.md — structure serves the second reader",
    "write a report": "02-shared-references/delivery-playbooks/04-documents-and-specs.md — structure serves the second reader",
    "validation report": "02-shared-references/delivery-playbooks/04-documents-and-specs.md — structure serves the second reader",
    "full report": "02-shared-references/delivery-playbooks/04-documents-and-specs.md — structure serves the second reader",
}

# Knowledge hints: topic keywords → relevant 08-knowledge/ entry paths.
# When a prompt matches, the entry path is surfaced alongside any skill hint
# so Claude knows to read it before diving into domain work.
KNOWLEDGE_HINTS = {
    "legion": "08-knowledge/game-dev/legion-architecture.md",
    "bobiverse": "08-knowledge/game-dev/legion-architecture.md",
    "centric": "08-knowledge/design/centric-plm-design-system.md · 08-knowledge/engineering/centric-plm-codebase.md",
    "data table": "08-knowledge/design/centric-plm-design-system.md",
    "icon font": "08-knowledge/design/centricsymbols-icon-font.md",
    "centricsymbols": "08-knowledge/design/centricsymbols-icon-font.md",
    "meridian": "08-knowledge/design/meridian-ds-prototype.md",
    "dispatcher": "08-knowledge/cross-domain/workspace-infrastructure.md",
    "worktree": "08-knowledge/cross-domain/workspace-infrastructure.md",
    "drive sync": "08-knowledge/cross-domain/workspace-infrastructure.md",
    "desync": "08-knowledge/cross-domain/workspace-infrastructure.md",
    "session-end": "08-knowledge/cross-domain/workflow-patterns.md",
    "session end": "08-knowledge/cross-domain/workflow-patterns.md",
    "optimize": "08-knowledge/cross-domain/workflow-patterns.md",
    "audit_skip": "08-knowledge/cross-domain/workflow-patterns.md",
    "figma": "08-knowledge/design/figma-ds-surface-authoring.md",
    "component": "08-knowledge/design/figma-ds-surface-authoring.md",
    "variant": "08-knowledge/design/figma-ds-surface-authoring.md",
    "design system": "08-knowledge/design/figma-ds-surface-authoring.md",
    "mockup": "08-knowledge/design/figma-ds-surface-authoring.md",
    "wireframe": "08-knowledge/design/figma-ds-surface-authoring.md",
}


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


def resolve_machine_label() -> str:
    host = socket.gethostname()
    return HOSTNAME_MAP.get(host, f"{host} (unknown machine — add to CLAUDE.md)")


def read_head(path: Path, lines: int = 30) -> str:
    if not path.exists():
        return f"_({path.name} not found)_"
    with path.open("r", encoding="utf-8", errors="replace") as f:
        head = [next(f, "") for _ in range(lines)]
    return "".join(head).rstrip()


def git(*args: str, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(WORKSPACE_ROOT), *args],
        capture_output=True,
        text=True,
        check=check,
    )


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
    - Drive-resident: path begins with the canonical WORKSPACE_ROOT (Drive-synced).
      Off-Drive worktrees (Tier 2 setup at e.g. ~/.claude-worktrees/) are skipped —
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
        # Only Drive-resident worktrees
        if not resolved.startswith(drive_prefix):
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

        rm = git("worktree", "remove", "--force", path)
        if rm.returncode != 0:
            skipped.append(f"{path}: `git worktree remove` failed — {rm.stderr.strip()}")
            continue

        short = branch.replace("refs/heads/", "")
        # Use -D since we already verified the branch is merged. Quiet on failure
        # (branch may already be gone if --force pruned it).
        git("branch", "-D", short)
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
            up = git("update-index", "--add", "--cacheinfo", f"100644,{disk_hash},{rel}")
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
            f"Last session-end aborted `git add -A` and used content-hash staging "
            f"on the safe-paths allowlist instead.",
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


def build_session_start_context(
    machine: str,
    now: datetime,
    cleaned_worktrees: list[str] | None = None,
    skipped_worktrees: list[str] | None = None,
) -> str:
    """Assemble the structured + raw context block injected at SessionStart.

    Includes pre-parsed fields (last session, pending count, project states, git state)
    so Claude can render CLAUDE.md's mandatory session-start ritual without re-parsing
    raw markdown. Also includes the head of session-log and project-context for richer
    follow-up context.
    """
    last_sess = _parse_last_session_entry(SESSION_LOG)
    pending = _count_pending_items(PROJECT_CONTEXT)
    projects = _scan_active_projects(WORKSPACE_ROOT / "07-projects")
    git_state = _describe_git_state()
    version_notice = _check_claude_version_change()
    audit_notice = _check_audit_staleness()
    desync_notice = _read_desync_notice()

    project_lines = "\n".join(f"  - {name}: {summary}" for name, summary in projects) or "  (none found)"

    notices = []
    if version_notice:
        notices.append(f"⚠ {version_notice}")
    if audit_notice:
        notices.append(f"⚠ {audit_notice}")
    if desync_notice:
        notices.append(f"⚠ {desync_notice}")
    worktree_notice = _format_worktree_cleanup_notice(
        cleaned_worktrees or [], skipped_worktrees or []
    )
    if worktree_notice:
        notices.append(f"ℹ {worktree_notice}")
    notices_block = ("\n## Notices (surface these in the session-start ritual)\n\n" +
                     "\n\n".join(notices) + "\n") if notices else ""

    structured = f"""## Session-start data (pre-parsed for the mandatory ritual in CLAUDE.md)

- machine: {machine}
- date: {now.strftime('%Y-%m-%d %H:%M %Z')}
- last_session: {last_sess or '(none in log)'}
- pending_count: {pending}
- git_state: {git_state or '(no git)'}
- active_projects ({len(projects)}):
{project_lines}
{notices_block}"""

    project_ctx_head = read_head(PROJECT_CONTEXT, 60)
    session_log_head = read_head(SESSION_LOG, 40)

    knowledge_index = read_head(KNOWLEDGE_INDEX, 60)
    knowledge_block = f"""
## Knowledge vault index (08-knowledge/_INDEX.md)
When working in any domain below, read the relevant entry before starting.
If the session produces a durable insight, add or update the entry at session end.
```
{knowledge_index}
```
""" if KNOWLEDGE_INDEX.exists() else ""

    return f"""# Workspace session context (auto-loaded)

**Date:** {now.strftime('%Y-%m-%d %H:%M %Z')}
**Machine:** {machine}
**Workspace:** `{WORKSPACE_ROOT}`

{structured}

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
_The mandatory session-start ritual format is in CLAUDE.md — render it before responding._
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
    knowledge_index = read_head(KNOWLEDGE_INDEX, 60)
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

## Knowledge vault index (08-knowledge/_INDEX.md)
Read the relevant entry before continuing domain work.
```
{knowledge_index}
```
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
        return

    ensure_local_gitdir()
    _ensure_executable_bits()
    # Fold any per-session fragments into session-log.md before the boot-read below,
    # so this session opens with the latest reconciled history. Idempotent + safe.
    _compact_session_fragments()
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
    emit_context(build_session_start_context(machine, now, cleaned, skipped), "SessionStart")


def _term_matches(term: str, prompt: str) -> bool:
    """Word-boundary match of a (possibly multiword) trigger term against the
    lowercased prompt. Boundary-anchored so short triggers like `ui` don't fire
    inside words like `build` or `guide`."""
    return re.search(r"(?<!\w)" + re.escape(term.lower()) + r"(?!\w)", prompt) is not None


def _registry_trigger_hits(prompt: str) -> list[tuple[str, str]]:
    """Match skill `triggers` declared in skills.registry.json — the machine graph
    generated from SKILL.md frontmatter. This is the same graph AGENTS.md's loading
    precedence algorithm routes by; reading it here makes the deterministic hook
    layer honor it instead of a hand-synced mirror table. Hints include the
    foundation-first load chain so ancestors load before the skill itself."""
    try:
        data = json.loads(SKILLS_REGISTRY.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return []
    skills = data.get("skills", {})
    chains = data.get("load_chains", {})
    hits: list[tuple[str, str]] = []
    for name, rec in skills.items():
        for term in rec.get("triggers", []) or []:
            if _term_matches(str(term), prompt):
                chain = chains.get(name) or [name]
                path_hint = " → ".join(f"03-skills/{n}/SKILL.md" for n in chain)
                hits.append((str(term), f"skill `{name}` (load chain, foundation-first): {path_hint}"))
                break  # one hit per skill
    return hits


def _knowledge_index_hits(prompt: str) -> list[tuple[str, str]]:
    """Match trigger terms declared inline on 08-knowledge/_INDEX.md entry lines
    (the `Triggers: \\`a\\`, \\`b\\`` convention). The index is the single source of
    truth — entries gain routing the moment their index line declares triggers,
    with no dispatcher edit required."""
    if not KNOWLEDGE_INDEX.exists():
        return []
    hits: list[tuple[str, str]] = []
    try:
        for line in KNOWLEDGE_INDEX.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"^-\s+\[\[([^\]]+)\]\]", line.strip())
            if not m:
                continue
            name = m.group(1)
            tm = re.search(r"[Tt]riggers:\s*(.+)$", line)
            if not tm:
                continue
            for term in re.findall(r"`([^`]+)`", tm.group(1)):
                if _term_matches(term, prompt):
                    found = sorted(KNOWLEDGE_DIR.glob(f"*/{name}.md"))
                    target = (
                        str(found[0].relative_to(WORKSPACE_ROOT)) if found
                        else f"08-knowledge (entry [[{name}]] — see _INDEX.md)"
                    )
                    hits.append((term, f"knowledge: read `{target}` before proceeding"))
                    break  # one hit per entry
    except Exception:
        return []
    return hits


# Per-tier caps (FX-2, 2026-07-09). The old single global cap (15 lines, emit order
# skill → registry → knowledge → index) let a flood of registry matches truncate the
# curated knowledge hints away — the highest-value tier lost to the noisiest one.
# Curated tiers now emit FIRST and every tier keeps its own budget; a hot tier can
# no longer starve the others.
TIER_CAPS = {
    "curated trigger": 8,
    "knowledge hint": 4,
    "registry trigger": 6,
    "index trigger": 4,
}

# Extracts the first workspace-relative .md path in a hint — the dedupe key. Hints
# from different tiers pointing at the same file (e.g. a curated row and a registry
# row both routing to design-engineer/SKILL.md) collapse to the first occurrence.
_HINT_TARGET_RE = re.compile(r"\d{2}-[\w./-]+\.md")


def _hint_target_key(hint: str) -> str:
    m = _HINT_TARGET_RE.search(hint)
    return m.group(0) if m else hint


def handle_user_prompt(payload: dict) -> None:
    prompt = (payload.get("prompt") or "").lower()
    if not prompt:
        return
    skill_hits = [(t, s) for t, s in TRIGGER_WORDS.items() if _term_matches(t, prompt)]
    knowledge_hits = [
        (kw, f"knowledge: read `{path}` before proceeding")
        for kw, path in KNOWLEDGE_HINTS.items() if _term_matches(kw, prompt)
    ]
    registry_hits = _registry_trigger_hits(prompt)
    index_hits = _knowledge_index_hits(prompt)
    tiers = [
        ("curated trigger", skill_hits),
        ("knowledge hint", knowledge_hits),
        ("registry trigger", registry_hits),
        ("index trigger", index_hits),
    ]
    if not any(hits for _, hits in tiers):
        return
    lines = ["# Project trigger detected", ""]
    seen: set[str] = set()
    for tier_name, hits in tiers:
        cap = TIER_CAPS[tier_name]
        emitted = 0
        dropped = 0
        for trigger, hint in hits:
            key = _hint_target_key(hint)
            if key in seen:
                continue
            if emitted >= cap:
                dropped += 1
                continue
            seen.add(key)
            lines.append(f"- **`{trigger}`** → {hint}")
            emitted += 1
        if dropped:
            lines.append(f"- _(+{dropped} more {tier_name} match(es) dropped — per-tier cap {cap})_")
    lines += [
        "",
        "_Load the matched skills per the AGENTS.md precedence algorithm (foundation-first) "
        "and read matched knowledge entries BEFORE acting. When authoring inside a specific "
        "design system, resolve within that system's own tokens; backlog its gaps._",
    ]
    emit_context("\n".join(lines), "UserPromptSubmit")


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


def handle_stop(payload: dict) -> None:
    # Light-touch. No-op unless session-log.md was modified in the last turn —
    # then stage it so the session-end commit captures it cleanly.
    if not in_git_repo():
        return
    r = git("diff", "--name-only", "--", "06-context/session-log.md")
    if r.stdout.strip():
        git("add", "06-context/session-log.md")


def handle_session_end(payload: dict) -> None:
    if not in_git_repo():
        sys.stderr.write("[session-end] not a git repo; skipping commit/push\n")
        return

    _ensure_drive_safe_git_config()
    # Fold this session's fragment into session-log.md so the commit below captures
    # the reconciled log (and the fragment's removal) atomically. Idempotent.
    _compact_session_fragments()

    machine = resolve_machine_label()
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

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
        # Self-heal: if any SKILL.md changed this session, regenerate the skills
        # registry BEFORE staging so the auto-commit never ships a stale graph.
        # (Previously only GitHub CI's `build-registry.py --check` caught this,
        # after the stale registry was already pushed.)
        if "SKILL.md" in git("status", "--porcelain", "--", "03-skills").stdout:
            builder = WORKSPACE_ROOT / "09-tools" / "build-registry.py"
            if builder.exists():
                reg = subprocess.run(
                    [sys.executable, str(builder)],
                    capture_output=True, text=True, cwd=str(WORKSPACE_ROOT),
                )
                if reg.returncode != 0:
                    sys.stderr.write(f"[session-end] registry regeneration failed: {reg.stderr}\n")
                else:
                    sys.stderr.write("[session-end] regenerated skills.registry.json (SKILL.md changed)\n")
        # .gitignore is the source of truth for what's tracked. Add everything
        # not ignored — covers all system-layer paths plus the 00-obsidian project.
        git("add", "-A")
        msg = f"session: auto-commit from {machine} @ {stamp}"

    commit = git("commit", "-m", msg)
    if commit.returncode != 0:
        sys.stderr.write(f"[session-end] commit failed: {commit.stderr}\n")
        return

    # Push if a remote is configured. Silent success, verbose failure.
    remote = git("remote").stdout.strip()
    if remote:
        push = git("push")
        if push.returncode != 0:
            sys.stderr.write(f"[session-end] push failed: {push.stderr}\n")

    # Opportunistic cleanup of OTHER stale worktrees. Skips the current one
    # (git refuses self-removal); next session-start in the canonical workspace
    # root will catch this one.
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
    "stop": handle_stop,
    "session-end": handle_session_end,
}


def main() -> int:
    if len(sys.argv) < 2:
        sys.stderr.write("usage: dispatcher.py <event>\n")
        return 2
    event = sys.argv[1]
    handler = HANDLERS.get(event)
    if not handler:
        sys.stderr.write(f"unknown event: {event}\n")
        return 2
    try:
        payload = read_stdin_json()
        handler(payload)
        return 0
    except Exception as exc:
        sys.stderr.write(f"[{event}] handler error: {exc}\n")
        return 0  # never block the session


if __name__ == "__main__":
    sys.exit(main())
