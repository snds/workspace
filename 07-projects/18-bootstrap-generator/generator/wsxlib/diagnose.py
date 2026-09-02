"""`wsx diagnose` — the safety net for pointing the generator at an EXISTING workspace.

When someone runs the generator/CLI against a workspace they already have, this REPORTS
what's wrong, stale, or out-of-date and names the SAFE correction for each — instead of
failing cryptically or clobbering their content. It is **read-only by default**; `--fix`
applies only NON-DESTRUCTIVE corrections (upgrade → emit → reindex), which add missing
pieces and regenerate derived files but never overwrite hand-authored content.

Every check is wrapped so a malformed file becomes a reported FINDING, not a stack trace —
that is the "error reporting" contract: a run against a broken existing workspace tells the
person exactly what to fix, and (with --fix) fixes what it safely can.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import core, examine, health, layout, scaffold

# level ranks for sorting + the exit code (error → non-zero).
_RANK = {"error": 0, "warn": 1, "ok": 2}
_MARK = {"error": "✗", "warn": "⚠", "ok": "✓"}


def _finding(level, area, msg, fix=""):
    return {"level": level, "area": area, "msg": msg, "fix": fix}


def _safe(fn, area, ok_msg):
    """Run a check; turn any exception into an ERROR finding instead of crashing."""
    try:
        return fn()
    except Exception as e:  # noqa: BLE001 — the whole point is to report, not raise
        return [_finding("error", area, f"check failed: {e}",
                         "this usually means a malformed file — see the message above")]


# --------------------------------------------------------------- individual checks ---
def _check_is_workspace(root: Path) -> list:
    man = core.load_manifest(root)
    if not (root / "manifest.json").exists():
        return [_finding("error", "workspace",
                         "no manifest.json — this isn't a wsx workspace.",
                         "run `wsx examine <path>` (foreign readout) or `wsx init` for a new one")]
    if man.get("generator") != "wsx":
        return [_finding("warn", "workspace",
                         "manifest.json has no wsx generator marker — hand-built or partial.",
                         "`wsx upgrade` brings it up to the scaffold non-destructively")]
    return [_finding("ok", "workspace", "recognized wsx workspace.")]


def _check_layout(root: Path) -> list:
    lay = layout.of(root)
    if lay.numbered:
        return [_finding("ok", "layout", "numbered taxonomy (current).")]
    return [_finding("warn", "layout",
                     "legacy FLAT layout — works, but below the current richer default.",
                     "`wsx restructure` (dry-run first) migrates it up; the broken-ref gate keeps it safe")]


def _check_scaffold(root: Path) -> list:
    missing = examine._missing_scaffold(root)
    if not missing:
        return [_finding("ok", "scaffold", "all canonical files present.")]
    head = ", ".join(missing[:5]) + (" …" if len(missing) > 5 else "")
    return [_finding("warn", "scaffold", f"{len(missing)} missing scaffold file(s): {head}",
                     "`wsx upgrade` adds them (never clobbers your files)")]


def _check_graph(root: Path) -> list:
    conn = examine._connections(root)  # quiet reuse of health's graph helpers
    out = []
    if conn["dangling"]:
        out.append(_finding("error", "graph",
                            f"{len(conn['dangling'])} dangling typed edge(s) — `relations:` points at a missing note.",
                            "`wsx health` lists them; fix the target name or `wsx archive` the source"))
    if conn["orphans"]:
        out.append(_finding("warn", "graph",
                            f"{len(conn['orphans'])} orphan note(s) — nothing links to them.",
                            "link each from its natural parent, or `wsx archive` it"))
    if not out:
        out.append(_finding("ok", "graph", "connected — no dangling edges or orphans."))
    return out


def _check_references(root: Path) -> list:
    """Traverse EVERY path-encoding reference (md-links, image embeds, Dataview `FROM`) and
    confirm each resolves on disk. This is the piece `health` doesn't cover — it counts
    inbound links but never flags a broken OUTBOUND target. Uses the same resolver the
    restructure migration's safety gate uses, so 'do the connections still map?' is a real
    check, not an assumption."""
    from . import restructure
    broken = restructure._broken_refs(root)  # {(source_name, kind, target_tail)}
    if broken:
        head = "; ".join(f"{s} → …/{tail}" for s, _k, tail in sorted(broken)[:4])
        return [_finding("error", "references",
                         f"{len(broken)} link(s)/query(ies) don't resolve on disk: {head}"
                         + (" …" if len(broken) > 4 else ""),
                         "fix the path in the source note, or `wsx archive` it (typed-edge "
                         "details: `wsx health`)")]
    return [_finding("ok", "references", "every md-link + Dataview query resolves on disk.")]


def _check_integrity(root: Path) -> list:
    from . import yamlio
    out = []
    prof = core.load_profile(root)
    if prof:
        try:
            if yamlio.loads(yamlio.dumps(prof)) != prof:
                out.append(_finding("warn", "integrity",
                                    "profile.yaml doesn't round-trip through the YAML subset.",
                                    "re-save a field: `wsx profile set identity.name=\"…\"`"))
        except Exception:
            out.append(_finding("error", "integrity", "profile.yaml is unparseable.",
                                "open context/profile.yaml and fix the YAML"))
    else:
        out.append(_finding("error", "integrity", "profile.yaml missing or empty.",
                            "`wsx upgrade`, then `wsx profile set …`"))
    try:
        json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    except Exception:
        out.append(_finding("error", "integrity", "manifest.json is not valid JSON.",
                            "restore it from git, or `wsx init --force` a fresh one elsewhere and copy content"))
    if not out:
        out.append(_finding("ok", "integrity", "profile + manifest parse and round-trip."))
    return out


def _check_manifest_drift(root: Path) -> list:
    man = core.load_manifest(root)
    recorded = set(man.get("skills", {}) or {})
    on_disk = {name for name, _sk in core.iter_skills(root)}
    missing = on_disk - recorded
    stale = recorded - on_disk
    if missing or stale:
        bits = []
        if missing:
            bits.append(f"{len(missing)} skill(s) on disk not in the manifest")
        if stale:
            bits.append(f"{len(stale)} manifest record(s) with no folder")
        return [_finding("warn", "skills", "; ".join(bits) + ".",
                         "`wsx skill reindex` rebuilds the manifest from disk")]
    return [_finding("ok", "skills", f"manifest matches {len(on_disk)} skill(s) on disk.")]


def _check_emitted(root: Path) -> list:
    man = core.load_manifest(root)
    emitted = man.get("emitted", {}) or {}
    if not emitted and any(True for _ in core.iter_skills(root)):
        return [_finding("warn", "adapters", "skills exist but adapters were never emitted.",
                         "`wsx emit all` compiles CLAUDE.md/AGENTS.md/hooks/MCP from the workspace")]
    if not (root / "CLAUDE.md").exists() and not (root / "AGENTS.md").exists():
        return [_finding("warn", "adapters", "no emitted adapter files (CLAUDE.md/AGENTS.md).",
                         "`wsx emit all`")]
    return [_finding("ok", "adapters", "adapter files present.")]


def _check_wiring(root: Path) -> list:
    """Unanticipated content dirs whose notes aren't wired in yet (no _INDEX → orphaned)."""
    from . import wire
    unwired = [d.name for d in wire.discover_extras(root) if not (d / "_INDEX.md").exists()]
    if unwired:
        return [_finding("warn", "wiring",
                         f"{len(unwired)} unanticipated content dir(s) not wired in: {', '.join(unwired[:5])}.",
                         "`wsx wire` connects them (HOME + an index + git-trackable)")]
    return [_finding("ok", "wiring", "all content dirs are wired into the graph.")]


def _check_cli_copy(root: Path) -> list:
    ver = root / ".wsx" / "VERSION"
    if not (root / ".wsx" / "wsxlib").is_dir() or not (root / "wsx.py").exists():
        return [_finding("warn", "self-sufficiency", "the copied-in CLI (.wsx/ + wsx.py) is missing.",
                         "`wsx upgrade` copies it in so the workspace can drive itself")]
    from . import __version__ as cur
    have = ver.read_text(encoding="utf-8").strip() if ver.exists() else "?"
    if have != cur:
        return [_finding("warn", "self-sufficiency",
                         f"copied-in CLI is v{have}, current is v{cur} (stale).",
                         "`wsx upgrade` refreshes it")]
    return [_finding("ok", "self-sufficiency", f"self-contained CLI present (v{have}).")]


def _check_git(root: Path) -> list:
    if not (root / ".git").exists():
        return [_finding("warn", "git", "not a git repo — no version history or backup.",
                         "`git init` here, then `wsx sync`")]
    out = []
    r = core.git(root, "rev-list", "--count", "HEAD", check=False, capture=True)
    if not ((r.stdout or "").strip().isdigit() and int(r.stdout.strip()) > 0):
        name = core.git(root, "config", "--get", "user.name", check=False, capture=True)
        if not (name.stdout or "").strip():
            out.append(_finding("error", "git", "no commits AND no git identity — nothing is being saved.",
                                "`wsx identity --name \"…\" --email \"…\"` (sets it for THIS repo + first commit)"))
        else:
            out.append(_finding("warn", "git", "repo has no commits yet.", "`wsx sync` to make the first"))
    if not core.has_remote(root):
        out.append(_finding("warn", "git", "no remote — local only, no off-machine backup.",
                            "`wsx remote` shows free hosting; then `wsx remote <url>` + `wsx sync`"))
    if not out:
        out.append(_finding("ok", "git", "repo with history + remote."))
    return out


_CHECKS = [
    ("workspace", _check_is_workspace), ("layout", _check_layout),
    ("scaffold", _check_scaffold), ("integrity", _check_integrity),
    ("skills", _check_manifest_drift), ("adapters", _check_emitted),
    ("graph", _check_graph), ("references", _check_references),
    ("wiring", _check_wiring), ("self-sufficiency", _check_cli_copy), ("git", _check_git),
]


def collect(root: Path) -> list:
    findings = []
    for area, fn in _CHECKS:
        findings += _safe(lambda fn=fn, root=root: fn(root), area, "")
    return findings


# ------------------------------------------------------------------------ run ---
def _apply_fix(root: Path) -> None:
    """Non-destructive corrections only: add missing scaffold + regenerate derived +
    refresh the copied CLI (upgrade), reindex the manifest, then re-emit adapters."""
    from . import adapters, skills, upgrade, wire
    print("\n— applying SAFE corrections (non-destructive: nothing hand-authored is overwritten) —\n")
    upgrade.upgrade(root)
    skills.reindex(root)
    prof = core.load_profile(root)
    adapters.emit(root, "all", prof, core.load_manifest(root))
    wire.wire(root)  # discovery-driven: index + link + git-track any unanticipated dir
    print("\n— re-checking —")


def diagnose(root: Path, fix: bool = False) -> int:
    findings = collect(root)
    if fix and any(f["level"] != "ok" for f in findings):
        from . import restructure
        # Baseline the references BEFORE correcting; re-check AFTER. The corrections are
        # additive/regenerative (they don't move dirs), so they must NOT break a reference
        # that resolved before — if one does, that's a real regression and we say so loudly.
        before = restructure._broken_refs(root)
        _apply_fix(root)
        introduced = sorted(restructure._broken_refs(root) - before)
        findings = collect(root)
        if introduced:
            head = "; ".join(f"{s} → …/{tail}" for s, _k, tail in introduced[:4])
            findings.insert(0, _finding(
                "error", "references",
                f"the correction INTRODUCED {len(introduced)} broken reference(s): {head} — unexpected.",
                "the corrections are non-destructive; `git diff`/revert and report this — it's a bug"))

    errors = [f for f in findings if f["level"] == "error"]
    warns = [f for f in findings if f["level"] == "warn"]

    print(f"wsx diagnose — {root}\n")
    for f in sorted(findings, key=lambda f: (_RANK[f["level"]], f["area"])):
        line = f"  {_MARK[f['level']]} {f['area']:16} {f['msg']}"
        print(line)
        if f["level"] != "ok" and f["fix"]:
            print(f"       ↳ fix: {f['fix']}")

    print()
    if errors:
        print(f"✗ {len(errors)} error(s), {len(warns)} warning(s). "
              + ("Some need a hand (see ↳). " if not fix else "")
              + ("Re-run with `wsx diagnose --fix` to auto-apply the safe ones."
                 if not fix else "Remaining items need manual attention."))
    elif warns:
        print(f"⚠ 0 errors, {len(warns)} warning(s) — all safely auto-correctable. "
              + ("Run `wsx diagnose --fix`." if not fix else "Re-run if any persist."))
    else:
        print("✓ healthy — no issues. This workspace is current and self-sufficient.")
    return 1 if errors else 0
