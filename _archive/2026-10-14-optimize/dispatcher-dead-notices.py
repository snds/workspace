"""Archived dead session-start notice code from .claude/hooks/dispatcher.py (/optimize 2026-10-14).

Origin: .claude/hooks/dispatcher.py at 6dc1746 — module constants at lines 41, 42-44, 45, 51,
54, 55 and the functions `_check_audit_staleness`, `_check_harness_map_staleness` and
`_check_skill_routing_harness` at lines 541-645 (the audit cited them as ~:469-573 before the
file grew).

Reason: no callers since 46d207a (2026-09-11), when the session-start notices moved to
09-tools/session-status.py (the card every surface prints). An AST reference count on
2026-10-14 found zero loads of the three functions and of SKILLS_REGISTRY, and no use of
AUDIT_LOG, HARNESS_MAP_STAMP, SKILL_ROUTING_EVAL, AUDIT_STALE_DAYS or HARNESS_MAP_STALE_DAYS
outside those functions. The live replacements are session-status.py `_notices()` (audit,
harness-map) and `routing_stamp_stale()` (the `evaluate-skill-routing.py --stale` comparison,
restored 2026-10-14). Nothing imports this file; it is kept for provenance (AGENTS.md mutation
policy). Names such as WORKSPACE_ROOT, CONTEXT_DIR, re, subprocess, sys and datetime refer to
the dispatcher's module scope.
"""
# ruff: noqa
# fmt: off

# ---- from dispatcher.py module top (lines 41-45, 51, 54-55)
AUDIT_LOG = CONTEXT_DIR / "audit-log.md"
HARNESS_MAP_STAMP = (
    WORKSPACE_ROOT / "07-projects" / "19-workspace-brain" / "reports" / "harness-map.stamp"
)
SKILL_ROUTING_EVAL = WORKSPACE_ROOT / "09-tools" / "evaluate-skill-routing.py"
SKILLS_REGISTRY = WORKSPACE_ROOT / "03-skills" / "skills.registry.json"
AUDIT_STALE_DAYS = 14
HARNESS_MAP_STALE_DAYS = 30  # Notice only after a first map exists (stamp present)


# ---- from dispatcher.py lines 541-645
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
