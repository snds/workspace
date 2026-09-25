#!/usr/bin/env python3
"""Reusable test harness for the workspace: quality, connection solidity, token cost.

Three lanes, one report card. Stdlib-only, read-only, and deterministic — no clock
dependence, no network, no LLM judgment anywhere in the pass/fail path.

  quality      Runs the documented enforcement chain as subprocesses and aggregates
               exit codes. Does NOT reimplement any validator; if a tool is the source
               of truth for a rule, this lane runs that tool.
  connections  The graph checks nothing else performs: does every Layer-0 route resolve
               to a real file, can an agent actually REACH every skill and knowledge
               entry, do hub edges terminate, do the named detectors exist.
  tokens       What a traversal costs. Five tiers from the contract floor every agent
               pays to the banned-ingest number the routing layer exists to avoid.
               Budget ceilings below are a regression gate, not a suggestion.

Usage:
  python3 09-tools/workspace-harness.py                  # all lanes, report card
  python3 09-tools/workspace-harness.py --quality
  python3 09-tools/workspace-harness.py --connections
  python3 09-tools/workspace-harness.py --tokens
  python3 09-tools/workspace-harness.py --json
  python3 09-tools/workspace-harness.py --stamp          # write the report stamp
  python3 09-tools/workspace-harness.py --self-test      # police the harness itself

Exit: 0 all green · 1 a lane failed · 2 the harness could not run.

Why this exists: the validators answer "is each file well-formed?" They cannot answer
"can a cold agent on another surface FIND this, and what does finding it cost?" Those
two questions are where Cursor kept missing skills, so they get a detector.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
REGISTRY = ROOT / "03-skills" / "skills.registry.json"
TRIGGER_ROUTES = ROOT / "02-shared-references" / "trigger-routes.json"
KNOWLEDGE_HINTS = ROOT / "02-shared-references" / "knowledge-hints.json"
KNOWLEDGE_DIR = ROOT / "08-knowledge"
STAMP = ROOT / "07-projects" / "19-workspace-brain" / "reports" / "workspace-harness.stamp"

# Token budget ceilings. Raising one is a deliberate, reviewable diff — never a
# side effect of "the report went red". Measured 2026-09-15; headroom ~15%.
# session_floor dropped 21,697 -> 14,778 when artifact-registry.md moved from "read" to
# "query" (C2). The ceiling was lowered with it on purpose: reverting the read order now
# fails CI instead of quietly costing 6.9k a session again.
# Cross-chain trigger collisions: correct sometimes, so a ceiling rather than zero.
# Raising it is a reviewable diff, which is the point.
CROSS_CHAIN_COLLISION_CEILING = 25

# Byte ceilings for the files every session loads, pinned at their 2ff02e7 sizes (wave 0,
# plan v1.1). Edits there are net-negative or neutral; raising one is a reviewable diff.
CODEX_DOC_MAX_BYTES = 32_768   # Codex project_doc_max_bytes default
CODEX_MIN_HEADROOM_BYTES = 3_072  # wave 1 exit gate (H6)

ALWAYS_LOADED_BYTES_CEILING = {
    "AGENTS.md": 26_044,  # re-pinned after the H6 cuts (wave 1, 2026-09-24)
    "CLAUDE.md": 5_769,
    "CURSOR.md": 6_153,
    ".cursor/rules/brain.mdc": 3_592,
    ".cursor/rules/01-agent-controller.mdc": 1_218,
    ".cursor/rules/02-workspace-filesystem.mdc": 1_602,
    "00-bootstrap/dist/user-CLAUDE.md": 1_515,
    "00-bootstrap/dist/BEACON.md": 1_515,
    "00-bootstrap/dist/RULES.txt": 293,
    # H6 per-family renders (wave 1, 2026-09-24). New files, so these are new pins, not raises:
    # the Codex beacon is held to the old shared beacon's 1,515 B (it counts toward the Codex
    # window); the ~/Projects pointer to the spec's 1 KiB; the Cursor paste to its first render.
    "00-bootstrap/dist/codex-AGENTS.md": 1_515,
    "00-bootstrap/dist/projects-AGENTS.md": 1_024,
    "00-bootstrap/dist/cursor-user-rules.txt": 670,
}
# The files that can sit at ~/.codex/AGENTS.md: the Codex beacon, or the shared paste beacon
# that was installed there before H6. The worst case counts the larger.
CODEX_BEACONS = ("00-bootstrap/dist/codex-AGENTS.md", "00-bootstrap/dist/BEACON.md")

BUDGETS = {
    "contract_floor": 11_800,
    "session_floor": 17_000,
    "loadset_p95": 14_500,
    "worst_case_legal": 64_000,
    # H6 per-surface floors (wave 1, 2026-09-24, bytes/4 estimate). Each is the value measured
    # after the H6 cuts plus about 5% headroom, rounded up to the next 100:
    #   cursor_floor 9,076 (AGENTS.md + alwaysApply .mdc + CLAUDE.md, which Cursor injects) -> 9,600
    #   claude_floor 8,304 (CLAUDE.md + @AGENTS.md + ~/.claude/CLAUDE.md beacon)            -> 8,800
    #   web_pack     4,393 (web-session.md + dist/BEACON.md + the route digest)              -> 4,700
    # web_pack grows with trigger-routes.json; raising any of these is a deliberate diff.
    "cursor_floor": 9_600,
    "claude_floor": 8_800,
    "web_pack": 4_700,
}

# The enforcement chain, in the order AGENTS.md fixes. build-related rewrites Related
# blocks and build-registry hashes them, so registry-after-related is load-bearing;
# --check keeps this harness read-only.
QUALITY_STEP_TIMEOUT_S = 300.0   # one hanging self-test must not hang the chain; a timeout is a FAIL
# Per-step overrides, each a deliberate diff. test-validators runs every fixture suite that builds real
# git repos (floor, identity, installers); it measured 309 s outside the sandbox on 2026-09-24 after the
# wave-1 floor cases, so it gets 600 s. Every other step keeps the 300 s hang guard.
QUALITY_STEP_TIMEOUT_OVERRIDE_S = {"test-validators.py": 600.0}
QUALITY_CHAIN = [
    ("build-related.py", ["--check"]),
    ("build-registry.py", ["--check"]),
    ("build-trigger-routes.py", ["--check"]),
    ("evaluate-skill-routing.py", ["--check"]),
    ("evaluate-surface-trajectories.py", ["--self-test"]),
    ("evaluate-surface-trajectories.py", ["--check"]),
    ("validate-integrity.py", []),
    ("validate-links.py", []),
    ("validate-workspace.py", []),
    ("validate-capabilities.py", ["--check"]),
    ("validate-evidence-grades.py", []),
    ("validate-evidence-grades.py", ["--self-test"]),
    ("artifact-find.py", ["--check"]),
    ("artifact-find.py", ["--self-test"]),
    ("figma-bind-probe.py", ["--self-test"]),
    ("validate-layer0-schema.py", ["--check"]),
    ("skill-loadset.py", ["--self-test"]),
    ("close-out-dispatch.py", ["--check"]),
    ("session-status.py", ["--check"]),
    ("check-secrets.py", []),
    ("vault-health.py", []),
    ("profile_resolve.py", ["--self-test"]),
    ("git_lanes.py", ["--self-test"]),
    ("profile_resolve.py", ["validate-tables", "--require-all"]),
    ("prune-our-branches.py", ["--self-test"]),
    ("../00-bootstrap/doctor/pin_lib.py", ["--self-test"]),
    ("../00-bootstrap/doctor/installers.py", ["--self-test"]),
    ("ws_hook.py", ["--self-test"]),
    ("ws_hook.py", ["--self-test-shell"]),
    ("../00-bootstrap/doctor/render_shims.py", ["--check"]),
    ("../00-bootstrap/doctor/render_shims.py", ["--self-test"]),
    ("intent-run.py", ["--self-test"]),
    ("check-secrets.py", ["--self-test"]),
    ("check-secrets.py", ["--class", "employer-substance", "--report"]),
    ("nightly.py", ["--self-test"]),
    ("../.claude/hooks/dispatcher.py", ["--self-test"]),
    ("test-validators.py", []),
]

# Fingerprints a sandboxed agent shell leaves in gate output (Claude Code's Bash sandbox on
# macOS, observed 2026-09-23: 3 red gates, all environmental). A match names the likely
# cause beside the result; it never changes the result.
AMBIENT_FINGERPRINTS = [
    ("xcrun_db", "git's macOS launcher (xcrun) cannot write its cache here, so every git call is "
                 "slow and prints a warning: expect timeouts and 'not silent' failures. To verify, "
                 "prepend a folder holding only a symlink to $(xcode-select -p)/usr/bin/git to PATH "
                 "(not Xcode's whole bin folder, which also swaps in its older python3)"),
    ("ps not permitted (sandbox)", "`ps` is denied here, so process-ancestry cases SKIP; "
                                   "prove them outside the sandbox"),
]


def ambient_notes(text: str) -> list[str]:
    """The environment notes whose fingerprint appears in a gate's output."""
    return [note for mark, note in AMBIENT_FINGERPRINTS if mark in text]


# A path-shaped token inside Layer-0 prose: "02-shared-references/x.md", "09-tools/y.py".
PATH_RE = re.compile(r"((?:0\d-|_)[\w][\w./-]*\.(?:md|py|json|jsonl|txt))")
FRONTMATTER_LIST = re.compile(r"^(trigger_words|triggers):\s*(.*?)(?=^\S|\Z)", re.M | re.S)


# --------------------------------------------------------------------------- tokens

def est_tokens(text: str) -> int:
    """Token estimate. Exact where tiktoken happens to be installed, bytes/4 otherwise.

    bytes/4 is the vault's own stated convention (compact-sessions.py: 48 KB ~ 12k).
    It is an ESTIMATE and every report says so — the harness gates on relative
    regression, which the heuristic tracks faithfully, not on an absolute truth.
    """
    try:
        import tiktoken  # type: ignore

        return len(tiktoken.get_encoding("cl100k_base").encode(text))
    except Exception:
        return round(len(text.encode("utf-8")) / 4)


def file_tokens(path: Path, head_lines: int | None = None) -> int:
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8", errors="replace")
    if head_lines is not None:
        text = "".join(text.splitlines(keepends=True)[:head_lines])
    return est_tokens(text)


# ------------------------------------------------------------------------ lane: quality

def run_quality(verbose: bool = False) -> dict:
    results, failed = [], 0
    seen: dict[str, list[str]] = {}   # ambient note -> gates whose output carried its fingerprint

    def note_env(script: str, *streams) -> None:
        text = "".join(s.decode(errors="replace") if isinstance(s, bytes) else (s or "") for s in streams)
        for n in ambient_notes(text):
            seen.setdefault(n, []).append(script)

    for script, args in QUALITY_CHAIN:
        target = TOOLS / script
        if not target.exists():
            results.append({"tool": script, "status": "MISSING", "seconds": 0.0})
            failed += 1
            continue
        start = time.monotonic()
        limit = QUALITY_STEP_TIMEOUT_OVERRIDE_S.get(script, QUALITY_STEP_TIMEOUT_S)
        try:
            proc = subprocess.run(
                [sys.executable, str(target), *args],
                capture_output=True, text=True, cwd=str(ROOT), timeout=limit,
            )
        except subprocess.TimeoutExpired as exc:
            note_env(script, exc.stdout, exc.stderr)   # partial output; bytes even under text=True
            failed += 1
            results.append({"tool": script, "status": "FAIL", "exit": None, "seconds": limit,
                            "last": f"SKIPPED: timed out after {limit:g}s (never green)",
                            "output": ""})
            continue
        elapsed = round(time.monotonic() - start, 2)
        note_env(script, proc.stdout, proc.stderr)
        ok = proc.returncode == 0
        failed += 0 if ok else 1
        tail = (proc.stdout + proc.stderr).strip().splitlines()
        results.append({
            "tool": script,
            "status": "ok" if ok else ("SKIPPED" if proc.returncode == 3 else "FAIL"),
            "exit": proc.returncode,
            "seconds": elapsed,
            "last": tail[-1] if tail else "",
            "output": "\n".join(tail[-12:]) if (verbose and not ok) else "",
        })
    return {"lane": "quality", "failed": failed, "checks": results,
            "environment": [{"note": n, "gates": g} for n, g in seen.items()]}


# -------------------------------------------------------------------- lane: connections

def _layer0_targets() -> list[tuple[str, str, str]]:
    out = []
    for path, key in ((TRIGGER_ROUTES, "routes"), (KNOWLEDGE_HINTS, "hints")):
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8")).get(key, {})
        for trigger, value in data.items():
            blob = value if isinstance(value, str) else " ".join(value)
            for hit in PATH_RE.findall(blob):
                out.append((path.name, trigger, hit))
    return out


def _git_ignored(rel: str) -> bool:
    """True when `rel` is gitignored — present on a dirty laptop, absent in CI."""
    proc = subprocess.run(
        ["git", "-C", str(ROOT), "check-ignore", "-q", "--", rel],
        capture_output=True,
    )
    return proc.returncode == 0


def _clone_visible(rel: str) -> bool:
    dest = ROOT / rel
    return dest.exists() and not _git_ignored(rel)


def check_layer0_targets() -> dict:
    """C1 — a route that names a file that isn't there sends the agent nowhere.

    The Layer-0 schema validates SHAPE only; nothing checked that the paths resolve
    until four routes were found pointing at a bare `00-context-profiles.md` that
    does not exist at the root (2026-09-15). Gitignored files (the side-chat inbox)
    exist locally and vanish on a clean clone — treat them as missing (2026-09-15).
    """
    targets = _layer0_targets()
    missing = []
    for source, trigger, rel in targets:
        if _clone_visible(rel):
            continue
        why = "gitignored — absent on a clean clone" if _git_ignored(rel) else "no such file"
        missing.append((source, trigger, rel, why))
    return {
        "check": "layer0-targets",
        "scanned": len(targets),
        "failures": [f"{f}: '{trig}' → {p} ({why})" for f, trig, p, why in missing],
    }


def check_skill_reachability(reg: dict, root: Path = ROOT) -> dict:
    """C2 — a skill nothing can route to is authored, indexed, and unusable.

    Three grades, because the vault's real topology has three:
      routable    own triggers, or an ancestor in another skill's chain, or named by a route
      hub-prose   no machine route, but its hub's SKILL.md names it — an agent that
                  opened the hub can still find it. Reported, not failed: this is the
                  known silent-spoke population, and failing 141 of them every run
                  would train everyone to ignore the harness.
      unreachable neither. Nothing gets here except by accident. That is the defect.
    """
    skills = reg["skills"]
    chains = reg.get("load_chains", {})
    routable = {n for n, m in skills.items() if m.get("triggers")}
    for owner, chain in chains.items():
        routable.update(step for step in chain if step != owner)
    routes = TRIGGER_ROUTES
    if routes.exists():
        blob = " ".join(
            v if isinstance(v, str) else " ".join(v)
            for v in json.loads(routes.read_text(encoding="utf-8")).get("routes", {}).values()
        )
        routable.update(n for n in skills if f"03-skills/{n}/" in blob)

    hub_prose, unreachable = [], []
    for name in sorted(set(skills) - routable):
        hub = skills[name].get("hub")
        hub_path = root / (skills.get(hub, {}).get("path") or "")
        named_by_hub = (
            hub in skills
            and hub_path.exists()
            and name in hub_path.read_text(encoding="utf-8", errors="replace")
        )
        (hub_prose if named_by_hub else unreachable).append(name)
    return {
        "check": "skill-reachability",
        "scanned": len(skills),
        "note": f"{len(routable)} routable · {len(hub_prose)} hub-prose only · {len(unreachable)} unreachable",
        "failures": [f"unreachable skill (no trigger, no chain, no route, not named by its hub): {n}"
                     for n in unreachable],
    }


def _is_subsequence(small: list, big: list) -> bool:
    """Every element of `small` appears in `big`, in that order (gaps allowed)."""
    it = iter(big)
    return all(step in it for step in small)


def check_hub_edges(reg: dict) -> dict:
    """C3 — the load chain must strictly ascend, so principles land before specialty work.

    The invariant is the CHAIN, not the tier enum: this vault has legitimate sub-spokes
    (threejs-vfx-atmosphere parents two vfx spokes), so "parent must be tier hub" would
    flag correct structure. What must hold is that the parent's chain is a prefix of the
    child's — that is what guarantees foundation-first for real.
    """
    skills = reg["skills"]
    chains = reg.get("load_chains", {})
    fails = []
    for name, meta in skills.items():
        hub = meta.get("hub")
        if hub and hub not in skills:
            fails.append(f"{name}: hub '{hub}' is not a skill")
        for dep in meta.get("prerequisites", []) or []:
            if dep not in skills:
                fails.append(f"{name}: prerequisite '{dep}' is not a skill")
        if hub in skills and name in chains and hub in chains:
            parent, child = chains[hub], chains[name]
            # Subsequence, not prefix: a child may inject its own prerequisite ahead of
            # the hub (3d-lighting-rendering pulls imaging-foundations in before
            # lead-3d-designer). What must survive is the parent's ORDER inside the
            # child's chain, and the hub landing before the child.
            if not _is_subsequence(parent, child):
                fails.append(
                    f"{name}: hub chain is not preserved in order "
                    f"({' → '.join(child)} must contain {' → '.join(parent)} in order)"
                )
            elif child.index(hub) > child.index(name):
                fails.append(f"{name}: hub '{hub}' loads after its own spoke")
    for owner, chain in chains.items():
        if not chain or chain[-1] != owner:
            fails.append(f"load_chain for '{owner}' does not terminate at itself")
        if len(set(chain)) != len(chain):
            fails.append(f"load_chain for '{owner}' repeats a step (cycle): {' → '.join(chain)}")
        for step in chain:
            if step not in skills:
                fails.append(f"load_chain for '{owner}' names missing skill '{step}'")
    return {"check": "hub-edges", "scanned": len(skills), "failures": fails}


def check_skill_files(reg: dict) -> dict:
    """C4 — the registry is a map; a map to a file that moved is worse than no map."""
    fails = []
    for name, meta in reg["skills"].items():
        rel = meta.get("path")
        if not rel:
            fails.append(f"{name}: registry entry has no path")
        elif not (ROOT / rel).exists():
            fails.append(f"{name}: path '{rel}' does not exist")
    return {"check": "skill-files", "scanned": len(reg["skills"]), "failures": fails}


def _index_triggered_names(index: Path) -> set[str]:
    """The `[[name]]`s _INDEX.md gives a backticked `Triggers:` list — mirrors
    prompt_route._knowledge_index_hits exactly. The agent never ingests the index;
    the ROUTER parses it, which is why an index Triggers list is a real match path.
    """
    names = set()
    if not index.is_file():
        return names
    for line in index.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^-\s+\[\[([^\]]+)\]\]", line.strip())
        if not m:
            continue
        tm = re.search(r"[Tt]riggers:\s*(.+)$", line)
        if tm and re.findall(r"`([^`]+)`", tm.group(1)):
            names.add(m.group(1))
    return names


def check_knowledge_routability(root: Path = ROOT) -> dict:
    """C5 — an entry no trigger reaches is findable only by reading the whole index,
    and the contract forbids that. Matches the three paths the router actually uses:
    knowledge-hints.json, an _INDEX.md `Triggers:` list, or frontmatter trigger_words.
    """
    knowledge_dir = root / "08-knowledge"
    hints_path = root / "02-shared-references" / "knowledge-hints.json"
    hints_blob = ""
    if hints_path.exists():
        hints = json.loads(hints_path.read_text(encoding="utf-8")).get("hints", {})
        hints_blob = " ".join(v if isinstance(v, str) else " ".join(v) for v in hints.values())
    indexed = _index_triggered_names(knowledge_dir / "_INDEX.md")

    entries, fails = 0, []
    for path in sorted(knowledge_dir.rglob("*.md")):
        rel = path.relative_to(root).as_posix()
        if path.name.startswith("_") or "/_archive/" in rel or "/research/" in rel:
            continue
        entries += 1
        if rel in hints_blob or path.stem in indexed:
            continue
        if FRONTMATTER_LIST.search(path.read_text(encoding="utf-8", errors="replace")[:2000]):
            continue
        fails.append(f"no Layer-0 route reaches this entry (no hint, no index Triggers, "
                     f"no trigger_words): {rel}")
    return {"check": "knowledge-routability", "scanned": entries, "failures": fails}


def check_index_link_resolution(root: Path = ROOT) -> dict:
    """C6 — the router resolves an index hit with glob("*/<name>.md"). When that misses
    it injects the prose string "see _INDEX.md" instead of a path, so the route fires
    and the agent still cannot open the file. One level deep only: an entry nested
    deeper silently degrades the same way.
    """
    knowledge_dir = root / "08-knowledge"
    index = knowledge_dir / "_INDEX.md"
    fails = []
    if not index.is_file():
        return {"check": "index-link-resolution", "scanned": 0,
                "failures": ["08-knowledge/_INDEX.md is missing"]}
    names = [m.group(1) for line in index.read_text(encoding="utf-8", errors="replace").splitlines()
             if (m := re.match(r"^-\s+\[\[([^\]]+)\]\]", line.strip()))]
    for name in names:
        hits = sorted(knowledge_dir.glob(f"*/{name}.md"))
        if not hits:
            deep = sorted(knowledge_dir.rglob(f"{name}.md"))
            fails.append(
                f"_INDEX entry [[{name}]] resolves to no file the router can reach"
                + (f" (exists at {deep[0].relative_to(root)} — too deep for glob('*/…'))" if deep else "")
            )
        elif len(hits) > 1:
            fails.append(f"_INDEX entry [[{name}]] is ambiguous: {len(hits)} files share that name")
    return {"check": "index-link-resolution", "scanned": len(names), "failures": fails}


def check_trigger_collisions(reg: dict) -> dict:
    """C8 — two skills claiming one trigger from DIFFERENT chains is routing ambiguity.

    Most collisions are benign: a foundation and its hub both claim `api contract`, and the
    load chain pulls both anyway. The ones that cost you are cross-chain — `mechanics`
    claimed by game-foundations AND science-foundations drags two unrelated chains into
    context for one word.

    Reported against a ceiling rather than failed at zero: some cross-chain collisions are
    correct (`color blindness` genuinely wants a11y-visual and found-color). What must not
    happen is silent growth, so the ceiling makes a new one a reviewable diff.
    """
    skills, chains = reg["skills"], reg.get("load_chains", {})
    owners: dict[str, list[str]] = {}
    for name, meta in skills.items():
        for term in meta.get("triggers") or []:
            owners.setdefault(str(term).lower().strip(), []).append(name)

    benign, cross = 0, []
    for term, claimants in owners.items():
        if len(claimants) < 2:
            continue
        related = any(
            a in (chains.get(b) or []) or b in (chains.get(a) or [])
            for a in claimants for b in claimants if a != b
        )
        if related:
            benign += 1
        else:
            cross.append((term, sorted(claimants)))

    fails = []
    if len(cross) > CROSS_CHAIN_COLLISION_CEILING:
        worst = sorted(cross)[: len(cross) - CROSS_CHAIN_COLLISION_CEILING]
        fails = [f"cross-chain trigger collision over ceiling "
                 f"({len(cross)} > {CROSS_CHAIN_COLLISION_CEILING}): '{t}' -> {c}"
                 for t, c in worst]
    return {
        "check": "trigger-collisions",
        "scanned": len(owners),
        "note": f"{benign} benign (same chain) · {len(cross)} cross-chain "
                f"(ceiling {CROSS_CHAIN_COLLISION_CEILING})",
        "failures": fails,
    }


def check_named_detectors(root: Path = ROOT) -> dict:
    """C7 — a gate whose binary is gone fails open, and so does one git never took.

    This vault's .gitignore is deny-by-default with an allowlist, so a new tool is
    untracked until someone remembers the allowlist line. It then passes locally and
    does not exist on the checkout CI runs — a detector that is green for the wrong
    reason. `workspace-harness.py` itself was one `git add -A` away from shipping that
    way (2026-09-15), so existence and TRACKEDNESS are both checked.
    """
    tools = root / "09-tools"
    named: set[str] = set()
    sources = [root / "AGENTS.md", root / "CLAUDE.md",
               root / "01-frameworks" / "08-workspace-contribution-framework.md"]  # H6: the chain moved there
    sources += sorted((root / ".github" / "workflows").glob("*.yml"))
    for doc in sources:
        if doc.exists():
            named.update(re.findall(r"09-tools/([\w-]+\.py)", doc.read_text(encoding="utf-8")))

    fails = [f"contract or CI names 09-tools/{s}, which does not exist"
             for s in sorted(named) if not (tools / s).exists()]

    present = sorted(s for s in named if (tools / s).exists())
    if present:
        try:
            tracked = set(subprocess.run(
                ["git", "ls-files", "--", *[f"09-tools/{s}" for s in present]],
                capture_output=True, text=True, cwd=str(root), check=True,
            ).stdout.split())
            fails += [f"09-tools/{s} is a named gate but is untracked — CI will not have it"
                      for s in present if f"09-tools/{s}" not in tracked]
        except (OSError, subprocess.CalledProcessError):
            pass  # not a git checkout; existence check above still stands

    return {"check": "named-detectors", "scanned": len(named), "failures": fails}


# 3d single-source rule (wave 0): each resolver helper has exactly one home. A second
# module-level definition is a fork; the harness finds it by AST, so fake modules held as
# source text and methods on test doubles do not count.
SINGLE_SOURCE_HOME = "09-tools/profile_resolve.py"
SINGLE_SOURCE_HELPERS = ("detect_surface", "normalize_remote", "load_table", "agent_check")
# render_shims reads surfaces.json itself (3b allows it); its loader is not the H2 helper.
SINGLE_SOURCE_EXEMPT = {("00-bootstrap/doctor/render_shims.py", "load_table")}
_LEGACY_MAP_RE = re.compile(r"\b" + "HOSTNAME" + r"_MAP\s*=")
_SHELL_CLASSIFY_RE = re.compile(r"^\s*classify\s*\(\)\s*\{(.*?)^\}", re.M | re.S)
_TEXT_SUFFIXES = {".py", ".sh", ".md", ".mdc", ".json", ".toml", ".yml", ".yaml", ".txt"}


def _tracked_files(root: Path) -> list:
    try:
        out = subprocess.run(["git", "ls-files", "-z"], capture_output=True, text=True,
                             cwd=str(root), check=True, timeout=30).stdout
        return [f for f in out.split("\0") if f]
    except (OSError, subprocess.SubprocessError):
        return [p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()]


def check_single_sources(root: Path = ROOT, files: list | None = None) -> dict:
    """C8 — one home per helper: no legacy hostname map, no forked resolver helper, and
    every shell classify() delegates to profile_resolve.py."""
    import ast

    files = _tracked_files(root) if files is None else files
    fails, scanned = [], 0
    for rel in files:
        path = root / rel
        if path.suffix not in _TEXT_SUFFIXES or "_archive/" in rel or not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        scanned += 1
        if _LEGACY_MAP_RE.search(text):
            fails.append(f"{rel}: legacy hostname map literal (labels live in devices.json)")
        if path.suffix == ".py" and rel != SINGLE_SOURCE_HOME:
            try:
                tree = ast.parse(text)
            except SyntaxError:
                continue
            for node in tree.body:
                if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                        and node.name in SINGLE_SOURCE_HELPERS
                        and (rel, node.name) not in SINGLE_SOURCE_EXEMPT):
                    fails.append(f"{rel}:{node.lineno}: second definition of {node.name}() "
                                 f"(its home is {SINGLE_SOURCE_HOME})")
        if path.suffix == ".sh":
            for body in _SHELL_CLASSIFY_RE.findall(text):
                if "profile_resolve.py" not in body:
                    fails.append(f"{rel}: shell classify() does not delegate to profile_resolve.py")
    return {"check": "single-sources", "scanned": scanned, "failures": fails}


# H6 entry points. Each rendered beacon must carry its family's wall; each tuple is satisfied
# by one line that contains every token.
BEACON_RULES = {
    "00-bootstrap/dist/BEACON.md": [("Claude", "personal-only")],
    "00-bootstrap/dist/user-CLAUDE.md": [("Claude", "personal-only")],
    "00-bootstrap/dist/codex-AGENTS.md": [("Codex", "feature branch", "PR"), ("ws status",)],
    "00-bootstrap/dist/cursor-user-rules.txt": [("Cursor", "feature branch", "PR")],
    "00-bootstrap/dist/projects-AGENTS.md": [("Claude", "personal-only"), ("Codex", "feature branch", "PR"),
                                             ("Cursor", "feature branch", "PR"), ("ws status",)],
}
# Facts restated somewhere they have gone stale (observed drift only). Each: id, pattern,
# where to look (path globs; "*" = tracked text), and the correction the failure names.
RESTATED_FACTS = [
    ("workspace-private", r"snds/workspace[`)\]]*\s*\(\**private",
     ["*"], "snds/workspace is PUBLIC (verified 2026-09-22)"),
    ("beacon-c8-only", r"Employer repos \(c8/\*\)",
     ["00-bootstrap/dist/*.md", "00-bootstrap/dist/*.txt"],
     "c8/* is not the whole employer set; beacons name the profile (`ws resolve repo`)"),
]
RESTATED_EXCLUDE = ("_archive/", "06-context/session-log", ".claude/state/", "07-projects/19-workspace-brain/")
LLMS_START_RE = re.compile(r"^## Start here.*?$(.*?)(?=^## |\Z)", re.M | re.S)
MD_LINK_RE = re.compile(r"\]\(([^)\s]+)\)")


def check_entry_points(root: Path = ROOT, files: list | None = None) -> dict:
    """H6: entry points agents read first stay honest. llms.txt Start-here never links a
    never-ingest file; every beacon carries its family's wall; Windsurf rules use `trigger:`;
    a tracked hook copy matches its dist source; no stale fact is restated."""
    fails, scanned = [], 0
    llms = root / "llms.txt"
    if llms.is_file():
        scanned += 1
        m = LLMS_START_RE.search(llms.read_text(encoding="utf-8"))
        banned = set(BANNED_INGEST) | {q for q, _cli in QUERIED_NOT_INGESTED}
        for target in MD_LINK_RE.findall(m.group(1) if m else ""):
            if target.lstrip("./") in banned:
                fails.append(f"llms.txt Start-here links {target}, which the contract says never to ingest")
    for rel, needs in BEACON_RULES.items():
        path = root / rel
        if not path.is_file():
            fails.append(f"{rel}: beacon missing (render_shims.py --write)")
            continue
        scanned += 1
        lines = path.read_text(encoding="utf-8").splitlines()
        for need in needs:
            if not any(all(tok in ln for tok in need) for ln in lines):
                fails.append(f"{rel}: no line carries the {' + '.join(need)} rule")
    for rule in sorted((root / ".windsurf" / "rules").glob("*.md")):
        scanned += 1
        head = rule.read_text(encoding="utf-8").split("\n---", 1)[0]
        rel = rule.relative_to(root).as_posix()
        if re.search(r"^alwaysApply:", head, re.M):
            fails.append(f"{rel}: uses alwaysApply; Windsurf reads `trigger: always_on`")
        elif not re.search(r"^trigger:", head, re.M):
            fails.append(f"{rel}: no `trigger:` frontmatter, so Windsurf may never load it")
    for hook in sorted((root / ".cursor" / "hooks").glob("*")):
        twin = root / "00-bootstrap" / "dist" / hook.name
        if not (hook.is_file() and twin.is_file()):
            continue
        scanned += 1
        body = [ln for ln in hook.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")]
        if hook.read_bytes() != twin.read_bytes() and not (len(body) == 1 and body[0].lstrip().startswith("exec ")):
            fails.append(f".cursor/hooks/{hook.name} diverges from 00-bootstrap/dist/{hook.name} "
                         "(keep one copy, or make the local one a one-line exec)")
    tracked = _tracked_files(root) if files is None else files
    text_files = [f for f in tracked if Path(f).suffix in {".md", ".mdc", ".txt"}
                  and not f.startswith(RESTATED_EXCLUDE)]
    for fid, pattern, scope, fix in RESTATED_FACTS:
        rx = re.compile(pattern)
        pool = text_files if scope == ["*"] else [f for f in text_files if any(Path(f).match(g) for g in scope)]
        for rel in pool:
            try:
                text = (root / rel).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for n, ln in enumerate(text.splitlines(), 1):
                if rx.search(ln):
                    fails.append(f"{rel}:{n}: stale restatement [{fid}] — {fix}")
    return {"check": "entry-points", "scanned": scanned, "failures": fails}


def run_connections() -> dict:
    if not REGISTRY.exists():
        return {"lane": "connections", "failed": 1,
                "checks": [{"check": "registry", "scanned": 0,
                            "failures": ["skills.registry.json missing — run build-registry.py"]}]}
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    checks = [
        check_layer0_targets(),
        check_skill_reachability(reg),
        check_hub_edges(reg),
        check_skill_files(reg),
        check_knowledge_routability(),
        check_index_link_resolution(),
        check_trigger_collisions(reg),
        check_named_detectors(),
        check_single_sources(),
        check_entry_points(),
    ]
    return {"lane": "connections",
            "failed": sum(1 for c in checks if c["failures"]),
            "checks": checks}


# ------------------------------------------------------------------------- lane: tokens

# What a compliant agent reads before it has done anything. Heads where the contract
# says head — reading a growing log whole is the failure this models, not the norm.
CONTRACT_FLOOR = [("llms.txt", None), ("AGENTS.md", None)]
ADAPTERS = ["CLAUDE.md", "CURSOR.md", "GEMINI.md", "PERPLEXITY.md", "WARP.md", "CONVENTIONS.md"]
SESSION_CONTEXT = [
    ("06-context/CRITICAL_FACTS.md", None),
    ("06-context/role-and-context.md", None),
    ("06-context/project-context.md", 30),
    ("06-context/session-log.md", 30),
    ("04-preferences/user-preferences.md", None),
]
# Indexes the contract says to QUERY, never ingest. Not in the floor, because no compliant
# agent pays them — but priced here so the saving stays visible and a silent reversion of
# the read order shows up as a number rather than as nothing. Each has a retrieval CLI:
#   artifact-registry.md -> artifact-find.py · skills.registry.json -> skill-loadset.py
#   _INDEX.md            -> knowledge-hints + prompt_route parsing it server-side
QUERIED_NOT_INGESTED = [
    ("06-context/artifact-registry.md", "09-tools/artifact-find.py"),
]
# Reached on a real request, on top of the floor.
REQUEST_EXTRAS = [
    ("02-shared-references/workspace-ontology.md", None),
    ("02-shared-references/delivery-playbooks/00-context-profiles.md", None),
    ("03-skills/close-out/SKILL.md", None),
]
# Files the contract explicitly says never to ingest. The gap between this and
# worst_case_legal is what the routing layer buys.
BANNED_INGEST = [
    "03-skills/skills.registry.json",
    "08-knowledge/_INDEX.md",
    "02-shared-references/trigger-routes.md",
]


def check_always_loaded_bytes(root: Path = ROOT, ceilings: dict | None = None) -> dict:
    """Always-loaded files may not grow past their pinned byte ceiling."""
    ceilings = ALWAYS_LOADED_BYTES_CEILING if ceilings is None else ceilings
    sizes = {rel: (root / rel).stat().st_size for rel in ceilings if (root / rel).is_file()}
    over = [f"{rel}: {sizes[rel]:,} bytes over ceiling {cap:,}"
            for rel, cap in ceilings.items() if sizes.get(rel, 0) > cap]
    warnings = []
    if ceilings is ALWAYS_LOADED_BYTES_CEILING:
        fails, warnings = codex_window(sizes)
        over += fails
    return {"sizes": sizes, "over": over, "warnings": warnings}


def codex_window(sizes: dict, baseline: int | None = None) -> tuple:
    """H6 codex_floor: Codex reads AGENTS.md plus the ~/.codex/AGENTS.md beacon into one 32 KiB
    project-doc window. Over the window is a FAIL. Under 3 KiB of worst-case headroom is a FAIL
    when AGENTS.md grew past its committed baseline (the pinned ceiling) and a WARN when it did
    not, which is accepted only while a named cut is pending. Returns (failures, warnings)."""
    baseline = ALWAYS_LOADED_BYTES_CEILING["AGENTS.md"] if baseline is None else baseline
    agents = sizes.get("AGENTS.md", 0)
    beacon = max((sizes.get(b, 0) for b in CODEX_BEACONS), default=0)
    codex = agents + beacon
    head = CODEX_DOC_MAX_BYTES - codex
    what = f"(AGENTS.md {agents:,} + beacon {beacon:,} = {codex:,} of {CODEX_DOC_MAX_BYTES:,})"
    if head < 0:
        return [f"Codex window over the cap by {-head:,} bytes {what}"], []
    if head < CODEX_MIN_HEADROOM_BYTES:
        line = f"Codex worst-case headroom {head:,} bytes < {CODEX_MIN_HEADROOM_BYTES:,} {what}"
        if agents > baseline:
            return [line + f"; AGENTS.md grew past its {baseline:,} B baseline"], []
        return [], [line + " — accepted only while a named cut is pending"]
    return [], []


def check_codex_headroom(sizes: dict) -> list:
    """Failures only (the baseline-relative WARN is reported by check_always_loaded_bytes)."""
    return codex_window(sizes)[0]


def run_tokens() -> dict:
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    skills, chains = reg["skills"], reg.get("load_chains", {})

    floor_parts = {p: file_tokens(ROOT / p, n) for p, n in CONTRACT_FLOOR}
    adapter_costs = {a: file_tokens(ROOT / a) for a in ADAPTERS if (ROOT / a).exists()}
    worst_adapter = max(adapter_costs, key=adapter_costs.get) if adapter_costs else ""
    contract_floor = sum(floor_parts.values()) + adapter_costs.get(worst_adapter, 0)

    floors = surface_floors()

    session_parts = {p: file_tokens(ROOT / p, n) for p, n in SESSION_CONTEXT}
    session_floor = contract_floor + sum(session_parts.values())
    avoided = {p: file_tokens(ROOT / p) for p, _cli in QUERIED_NOT_INGESTED}

    chain_costs = {}
    for name in skills:
        chain = chains.get(name, [name])
        chain_costs[name] = sum(
            file_tokens(ROOT / skills[s]["path"]) for s in chain if s in skills
        )
    ordered = sorted(chain_costs.values())
    n = len(ordered) or 1

    def pct(q: float) -> int:
        return ordered[min(n - 1, int(q * n))] if ordered else 0

    worst_skill = max(chain_costs, key=chain_costs.get) if chain_costs else ""
    worst_chain = chains.get(worst_skill, [worst_skill])

    knowledge = {
        p.relative_to(ROOT).as_posix(): file_tokens(p)
        for p in KNOWLEDGE_DIR.rglob("*.md")
        if not p.name.startswith("_")
    }
    worst_knowledge = max(knowledge, key=knowledge.get) if knowledge else ""
    extras = {p: file_tokens(ROOT / p, n) for p, n in REQUEST_EXTRAS}

    worst_case_legal = (
        session_floor
        + chain_costs.get(worst_skill, 0)
        + knowledge.get(worst_knowledge, 0)
        + sum(extras.values())
    )
    banned = {p: file_tokens(ROOT / p) for p in BANNED_INGEST}

    measured = {
        "contract_floor": contract_floor,
        "session_floor": session_floor,
        "loadset_p50": pct(0.50),
        "loadset_p95": pct(0.95),
        "loadset_max": ordered[-1] if ordered else 0,
        "worst_case_legal": worst_case_legal,
        "banned_ingest_total": sum(banned.values()),
        "avoided_by_retrieval": sum(avoided.values()),
        **{k: sum(v.values()) for k, v in floors.items()},
    }
    over = [
        f"{k}: {measured[k]:,} tokens over budget {BUDGETS[k]:,}"
        for k in BUDGETS
        if measured.get(k, 0) > BUDGETS[k]
    ]
    ceilings = check_always_loaded_bytes()
    over += ceilings["over"]
    warnings = ceilings.get("warnings", [])
    return {
        "lane": "tokens",
        "failed": 1 if over else 0,
        "always_loaded_bytes": ceilings["sizes"],
        "estimator": "tiktoken" if _has_tiktoken() else "bytes/4 (estimate)",
        "measured": measured,
        "budgets": BUDGETS,
        "over_budget": over,
        "warnings": warnings,
        "detail": {
            "surface_floors": floors,
            "worst_adapter": worst_adapter,
            "adapters": adapter_costs,
            "floor_parts": floor_parts,
            "session_parts": session_parts,
            "worst_loadset_skill": worst_skill,
            "worst_loadset_chain": worst_chain,
            "worst_knowledge_entry": worst_knowledge,
            "request_extras": extras,
            "banned_ingest": banned,
            "avoided_by_retrieval": avoided,
            "retrieval_clis": {p: cli for p, cli in QUERIED_NOT_INGESTED},
        },
    }


def _always_apply_rules(root: Path = ROOT) -> list:
    rules = []
    for p in sorted((root / ".cursor" / "rules").glob("*.mdc")):
        head = p.read_text(encoding="utf-8").split("\n---", 1)[0]
        if re.search(r"^alwaysApply:\s*true\b", head, re.M):
            rules.append(p.relative_to(root).as_posix())
    return rules


def surface_floors(root: Path = ROOT) -> dict:
    """H6: what each surface family auto-loads before doing anything, per file.
    cursor_floor: AGENTS.md + every alwaysApply rule + CLAUDE.md (Cursor's third-party import is
    on by default). claude_floor: CLAUDE.md + its @AGENTS.md import + the ~/.claude/CLAUDE.md
    beacon. web_pack: what a RULES-ONLY chat gets (the paste pack plus the route digest)."""
    def cost(rels):
        return {r: file_tokens(root / r) for r in rels if (root / r).is_file()}
    return {
        "cursor_floor": cost(["AGENTS.md", *_always_apply_rules(root), "CLAUDE.md"]),
        "claude_floor": cost(["CLAUDE.md", "AGENTS.md", "00-bootstrap/dist/user-CLAUDE.md"]),
        "web_pack": cost(["00-bootstrap/adapters/web-session.md", "00-bootstrap/dist/BEACON.md",
                          "02-shared-references/trigger-routes-digest.md"]),
    }


def _has_tiktoken() -> bool:
    try:
        import tiktoken  # noqa: F401

        return True
    except Exception:
        return False


# -------------------------------------------------------------------------- reporting

def print_report(report: dict) -> None:
    print("workspace-harness — quality · connections · tokens\n")

    q = report.get("quality")
    if q:
        print(f"## quality — {len(q['checks'])} gates, {q['failed']} failing")
        for c in q["checks"]:
            mark = "✓" if c["status"] == "ok" else "✗"
            print(f"  {mark} {c['tool']:<28} {c['status']:<8} {c['seconds']:>5.2f}s  {c['last'][:70]}")
            if c.get("output"):
                for line in c["output"].splitlines():
                    print(f"        {line}")
        for env in q.get("environment", []):
            print(f"  ! environment: {env['note']} (seen in: {', '.join(env['gates'])})")
        print()

    c = report.get("connections")
    if c:
        total = sum(len(x["failures"]) for x in c["checks"])
        print(f"## connections — {len(c['checks'])} checks, {total} defect(s)")
        for chk in c["checks"]:
            mark = "✓" if not chk["failures"] else "✗"
            detail = f" — {chk['note']}" if chk.get("note") else ""
            print(f"  {mark} {chk['check']:<24} {chk['scanned']:>4} scanned, "
                  f"{len(chk['failures'])} defect(s){detail}")
            for f in chk["failures"][:12]:
                print(f"        · {f}")
            if len(chk["failures"]) > 12:
                print(f"        … {len(chk['failures']) - 12} more")
        print()

    t = report.get("tokens")
    if t:
        m, b = t["measured"], t["budgets"]
        print(f"## tokens — worst-case traversal ({t['estimator']})")
        rows = [
            ("contract floor (llms+AGENTS+worst adapter)", "contract_floor"),
            ("session floor (+ context read order)", "session_floor"),
            ("load set p50 / p95 / max", None),
            ("worst-case legal request", "worst_case_legal"),
            ("cursor floor (AGENTS+alwaysApply+CLAUDE)", "cursor_floor"),
            ("claude floor (CLAUDE+AGENTS+beacon)", "claude_floor"),
            ("web pack (paste pack + route digest)", "web_pack"),
        ]
        for label, key in rows:
            if key is None:
                print(f"  · {label:<44} {m['loadset_p50']:>7,} / {m['loadset_p95']:>6,} / {m['loadset_max']:,}")
                continue
            ceiling = b.get(key)
            mark = "✗" if ceiling and m[key] > ceiling else "·"
            budget = f"  (budget {ceiling:,})" if ceiling else ""
            print(f"  {mark} {label:<44} {m[key]:>7,}{budget}")
        d = t["detail"]
        print(f"  · worst load chain: {' → '.join(d['worst_loadset_chain'])}")
        if m.get("avoided_by_retrieval"):
            print(f"  · avoided by retrieval (query, never ingest): {m['avoided_by_retrieval']:>7,}"
                  f"  — {', '.join(d['retrieval_clis'].values())}")
        print(f"  · banned ingest if routing is skipped:       {m['banned_ingest_total']:>7,}"
              f"  ({m['banned_ingest_total'] / max(m['worst_case_legal'], 1):.1f}× the legal worst case)")
        sizes = t.get("always_loaded_bytes", {})
        print(f"  · always-loaded bytes: {sum(sizes.values()):,} across {len(sizes)} file(s)"
              f" (ceiling {sum(ALWAYS_LOADED_BYTES_CEILING.values()):,})")
        for line in t["over_budget"]:
            print(f"  ✗ OVER BUDGET — {line}")
        for line in t.get("warnings", []):
            print(f"  ! WARN — {line}")
        print()

    lanes = [report[k] for k in ("quality", "connections", "tokens") if k in report]
    failed = sum(l["failed"] for l in lanes)
    print(f"harness: {'PASS' if failed == 0 else 'FAIL'} — {failed} failing check(s) across {len(lanes)} lane(s)")
    if failed and (q or {}).get("environment"):
        print("  the environment notes under quality may explain some of these; they do not change the result")


def write_stamp(report: dict) -> None:
    t = report.get("tokens", {}).get("measured", {})
    q, c = report.get("quality", {}), report.get("connections", {})
    failed = sum(report[k]["failed"] for k in ("quality", "connections", "tokens") if k in report)
    STAMP.parent.mkdir(parents=True, exist_ok=True)
    STAMP.write_text(
        "\n".join([
            f"result: {'pass' if failed == 0 else 'fail'}",
            f"quality_failing: {q.get('failed', 'n/a')}",
            f"connection_defects: {sum(len(x['failures']) for x in c.get('checks', []))}",
            f"session_floor: {t.get('session_floor', 0)}",
            f"loadset_p95: {t.get('loadset_p95', 0)}",
            f"worst_case_legal: {t.get('worst_case_legal', 0)}",
            f"estimator: {report.get('tokens', {}).get('estimator', 'n/a')}",
        ]) + "\n",
        encoding="utf-8",
    )
    print(f"✓ wrote {STAMP.relative_to(ROOT)}")


# -------------------------------------------------------------------------- self-test

def _plant_entry_points(root: Path) -> list:
    """A minimal clean tree for check_entry_points; returns its 'tracked' file list."""
    walls = {"claude": "- Claude surfaces are personal-only.",
             "codex": "- Codex: employer work only via a feature branch + PR.",
             "cursor": "- Cursor: employer work only via a feature branch + PR.",
             "ws": "- `ws status` prints the card."}
    body = {
        "llms.txt": "# x\n\n## Start here\n- [AGENTS.md](AGENTS.md)\n- run skill-loadset; never ingest "
                    "`03-skills/skills.registry.json`\n\n## Other\n- [r](03-skills/skills.registry.json)\n",
        "00-bootstrap/dist/BEACON.md": walls["claude"],
        "00-bootstrap/dist/user-CLAUDE.md": walls["claude"],
        "00-bootstrap/dist/codex-AGENTS.md": walls["codex"] + "\n" + walls["ws"],
        "00-bootstrap/dist/cursor-user-rules.txt": walls["cursor"],
        "00-bootstrap/dist/projects-AGENTS.md": "\n".join(walls.values()),
        ".windsurf/rules/workspace.md": "---\ntrigger: always_on\n---\nread AGENTS.md\n",
        "notes/fact.md": "Remote: snds/workspace (**public**)\n",
    }
    for rel, text in body.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text + ("" if text.endswith("\n") else "\n"), encoding="utf-8")
    return sorted(body)


def _entry_point_fixtures() -> list:
    def write(rel, text):
        def plant(root, files):
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text, encoding="utf-8")
            if rel not in files:
                files.append(rel)
        return plant
    return [
        ("an llms.txt Start-here that links the registry fails (H6)", "llms.txt Start-here links",
         write("llms.txt", "## Start here\n- [reg](03-skills/skills.registry.json)\n")),
        ("a beacon missing the Claude personal-only rule fails (H6)", "Claude + personal-only",
         write("00-bootstrap/dist/user-CLAUDE.md", "- Figma work uses real library components.\n")),
        ("a Codex beacon without the feature-branch rule fails (H6)", "Codex + feature branch + PR",
         write("00-bootstrap/dist/codex-AGENTS.md", "- `ws status` prints the card.\n")),
        ("a Windsurf rule using alwaysApply is flagged (H6)", "uses alwaysApply",
         write(".windsurf/rules/workspace.md", "---\nalwaysApply: true\n---\nx\n")),
        ("a stale 'private' restatement is flagged (H6)", "[workspace-private]",
         write("notes/old.md", "Git remote: `https://github.com/snds/workspace` (**private**)\n")),
        ("the 'c8/* only' beacon wording is flagged (H6)", "[beacon-c8-only]",
         write("00-bootstrap/dist/RULES.txt", "- Employer repos (c8/*) never receive it.\n")),
        ("a divergent tracked hook copy fails (H6)", "diverges from 00-bootstrap/dist",
         lambda root, files: [write(".cursor/hooks/x.sh", "#!/bin/sh\necho a\necho b\n")(root, files),
                              write("00-bootstrap/dist/x.sh", "#!/bin/sh\necho c\n")(root, files)]),
    ]


def self_test() -> int:
    """Prove each connection check can FAIL. A detector that only ever passes is decor.

    Everything here is synthetic and clock-free — a fixture stamped with the authoring
    date is a test that goes red on its own, which is how test-validators.py broke
    (observed 2026-09-15).
    """
    failures = []

    def expect(name, condition):
        if not condition:
            failures.append(name)

    reg = {
        "skills": {
            "found": {"path": "03-skills/found/SKILL.md", "tier": "foundation", "triggers": ["x"]},
            "silent": {"path": "03-skills/silent/SKILL.md", "tier": "spoke", "triggers": [],
                       "hub": "nope"},
        },
        "load_chains": {"found": ["found"], "silent": ["found", "silent"]},
    }
    # A spoke that appears only in its OWN chain is reachable by nothing.
    expect("reachability rejects unroutable spoke", check_skill_reachability(reg)["failures"])
    # Make it an ancestor of something else and it becomes routable.
    chained = json.loads(json.dumps(reg))
    chained["skills"]["leaf"] = {"path": "03-skills/leaf/SKILL.md", "tier": "spoke",
                                 "triggers": ["y"], "hub": "silent"}
    chained["load_chains"]["leaf"] = ["found", "silent", "leaf"]
    expect("reachability accepts chain-reachable spoke",
           not check_skill_reachability(chained)["failures"])

    expect("hub-edges rejects missing hub", check_hub_edges(reg)["failures"])
    good = json.loads(json.dumps(reg))
    good["skills"]["silent"]["hub"] = "found"
    expect("hub-edges accepts real hub", not check_hub_edges(good)["failures"])

    inverted = json.loads(json.dumps(good))
    inverted["load_chains"]["silent"] = ["silent", "found"]
    expect("hub-edges rejects a chain that does not terminate at itself",
           check_hub_edges(inverted)["failures"])

    expect("subsequence allows an injected prerequisite",
           _is_subsequence(["a", "c"], ["a", "b", "c"]))
    expect("subsequence rejects reordering", not _is_subsequence(["c", "a"], ["a", "b", "c"]))

    expect("skill-files rejects missing path", check_skill_files(reg)["failures"])

    collide = {"skills": {"a": {"triggers": ["shared"], "path": "p"},
                          "b": {"triggers": ["shared"], "path": "p"}},
               "load_chains": {"a": ["a"], "b": ["b"]}}
    expect("collision check counts a cross-chain claim",
           "1 cross-chain" in check_trigger_collisions(collide)["note"])
    same = {"skills": collide["skills"], "load_chains": {"a": ["a"], "b": ["a", "b"]}}
    expect("collision check treats a same-chain claim as benign",
           "1 benign" in check_trigger_collisions(same)["note"])

    with tempfile.TemporaryDirectory() as td:
        fake = Path(td)
        (fake / "09-tools").mkdir()
        (fake / "AGENTS.md").write_text("run `09-tools/ghost-gate.py` before shipping\n",
                                        encoding="utf-8")
        expect("named-detectors catches a gate the contract names but nothing provides",
               check_named_detectors(fake)["failures"])

    with tempfile.TemporaryDirectory() as td:
        fake = Path(td)
        kn = fake / "08-knowledge" / "design"
        kn.mkdir(parents=True)
        (kn / "routed.md").write_text("---\ntrigger_words:\n  - thing\n---\nbody\n", encoding="utf-8")
        (kn / "stranded.md").write_text("---\ntags: [x]\n---\nbody\n", encoding="utf-8")
        (fake / "08-knowledge" / "_INDEX.md").write_text(
            "- [[routed]] — blurb. Triggers: `thing`\n- [[ghost]] — never written\n", encoding="utf-8")
        routability = check_knowledge_routability(fake)
        expect("knowledge-routability flags the entry with no route",
               any("stranded.md" in f for f in routability["failures"]))
        expect("knowledge-routability accepts trigger_words",
               not any("routed.md" in f for f in routability["failures"]))
        resolution = check_index_link_resolution(fake)
        expect("index-link-resolution catches an index entry with no file",
               any("ghost" in f for f in resolution["failures"]))
        expect("index-link-resolution accepts a real entry",
               not any("[[routed]]" in f for f in resolution["failures"]))

    expect("token estimate is monotonic", est_tokens("a" * 4000) > est_tokens("a" * 400))
    expect("token estimate of empty is zero", est_tokens("") == 0)
    expect("head read is cheaper than whole file",
           file_tokens(ROOT / "AGENTS.md", 5) < file_tokens(ROOT / "AGENTS.md"))

    # The point of moving an index behind a CLI is that reverting must COST something
    # visible. A ceiling a revert would not breach is decoration, so assert the gap.
    tokens = run_tokens()
    reverted = tokens["measured"]["session_floor"] + tokens["measured"]["avoided_by_retrieval"]
    expect("session_floor budget would catch a reverted read order",
           reverted > BUDGETS["session_floor"] >= tokens["measured"]["session_floor"])

    with tempfile.TemporaryDirectory() as td:
        fake = Path(td)
        (fake / "AGENTS.md").write_text("x" * 11, encoding="utf-8")
        (fake / "CLAUDE.md").write_text("x" * 5, encoding="utf-8")
        grown = check_always_loaded_bytes(fake, {"AGENTS.md": 10, "CLAUDE.md": 5})
        expect("always-loaded ceiling catches a grown file",
               any("AGENTS.md" in o for o in grown["over"]))
        expect("always-loaded ceiling accepts a file at its ceiling",
               not any("CLAUDE.md" in o for o in grown["over"]))
    expect("always-loaded ceilings hold on the live tree", not check_always_loaded_bytes()["over"])
    expect("Codex headroom under 3 KiB fails (H6)",
           bool(check_codex_headroom({"AGENTS.md": 30_221, "00-bootstrap/dist/BEACON.md": 1_515})))
    expect("Codex headroom at 3 KiB or more passes (H6)",
           not check_codex_headroom({"AGENTS.md": 28_181, "00-bootstrap/dist/BEACON.md": 1_515}))
    grown = codex_window({"AGENTS.md": 28_300, "00-bootstrap/dist/codex-AGENTS.md": 1_515}, baseline=28_000)
    expect("a net-positive AGENTS.md diff below 3 KiB headroom fails (H6)", grown[0] and not grown[1])
    held = codex_window({"AGENTS.md": 28_500, "00-bootstrap/dist/codex-AGENTS.md": 1_515}, baseline=28_600)
    expect("under 3 KiB without AGENTS.md growth is a WARN, not a FAIL (H6)", not held[0] and held[1])
    over = codex_window({"AGENTS.md": 31_900, "00-bootstrap/dist/BEACON.md": 1_000}, baseline=40_000)
    expect("codex_floor over the 32 KiB window fails whatever the baseline (H6)", bool(over[0]))
    big_beacon = codex_window({"AGENTS.md": 26_000, "00-bootstrap/dist/BEACON.md": 1_000,
                               "00-bootstrap/dist/codex-AGENTS.md": 4_000}, baseline=26_000)
    expect("the larger of the two Codex beacons is the one counted (H6)", bool(big_beacon[1]))
    floors = surface_floors()
    expect("surface floors price every H6 family", sorted(floors) == ["claude_floor", "cursor_floor", "web_pack"]
           and all(floors.values()))
    live = run_tokens()
    expect("the H6 floors hold on the live tree", not any(k in o for o in live["over_budget"]
                                                           for k in ("cursor_floor", "claude_floor", "web_pack")))
    expect("entry points are clean on the live tree", not check_entry_points()["failures"])
    for name, needle, plant in _entry_point_fixtures():
        with tempfile.TemporaryDirectory() as td:
            fake = Path(td)
            files = _plant_entry_points(fake)
            plant(fake, files)
            got = check_entry_points(fake, files)["failures"]
            expect(name, any(needle in f for f in got))
    with tempfile.TemporaryDirectory() as td:
        fake = Path(td)
        files = _plant_entry_points(fake)
        clean = check_entry_points(fake, files)["failures"]
        expect("the planted clean entry-point tree passes", not clean)

    with tempfile.TemporaryDirectory() as td:
        fake = Path(td)
        (fake / "09-tools").mkdir()
        (fake / "09-tools" / "profile_resolve.py").write_text("def agent_check():\n    pass\n",
                                                           encoding="utf-8")
        (fake / "09-tools" / "fork.py").write_text(
            "def agent_check():\n    pass\n" + "HOSTNAME" + "_MAP = {}\n", encoding="utf-8")
        (fake / "09-tools" / "double.py").write_text(
            "SRC = 'def load_table(name):\\n    pass'\nclass Fake:\n    def detect_surface(self):\n"
            "        pass\n", encoding="utf-8")
        (fake / "enroll.sh").write_text("classify() {\n  echo unknown\n}\n", encoding="utf-8")
        (fake / "ok.sh").write_text("classify() {\n  python3 x/profile_resolve.py repo\n}\n",
                                    encoding="utf-8")
        files = ["09-tools/profile_resolve.py", "09-tools/fork.py", "09-tools/double.py",
                 "enroll.sh", "ok.sh"]
        single = check_single_sources(fake, files)["failures"]
        expect("single-sources catches a forked helper",
               any("fork.py" in f and "agent_check" in f for f in single))
        expect("single-sources catches a legacy hostname map",
               any("fork.py" in f and "hostname map" in f for f in single))
        expect("single-sources catches a non-delegating shell classify()",
               any("enroll.sh" in f for f in single))
        expect("single-sources ignores the home, source text, methods and delegating shells",
               not any(x in f for f in single
                       for x in ("profile_resolve.py:", "double.py", "ok.sh")))

    expect("PATH_RE finds a parenthesised path",
           PATH_RE.findall("resolve (02-shared-references/x.md) first") == ["02-shared-references/x.md"])
    expect("PATH_RE ignores prose", not PATH_RE.findall("no paths. here at all"))
    expect(
        "gitignored inbox is not clone-visible",
        not _clone_visible("06-context/side-chat-inbox.md"),
    )
    expect(
        "handback Layer-0 hints do not name the gitignored inbox path",
        not any("side-chat-inbox.md" in t[2] for t in _layer0_targets()),
    )

    expect("ambient note names the unwritable git launcher cache",
           len(ambient_notes("git: error: couldn't create cache file '/var/folders/x/T/xcrun_db-ab' "
                             "(errno=Operation not permitted)")) == 1)
    expect("ambient note names a sandbox ps denial",
           len(ambient_notes("self-test SKIP: x (ps not permitted (sandbox): y) — not a pass")) == 1)
    expect("clean gate output carries no ambient note", ambient_notes("OK all 74 checks") == [])

    for name in failures:
        print(f"  ✗ {name}")
    if failures:
        print(f"FAIL workspace-harness self-test — {len(failures)} assertion(s)")
        return 1
    print("OK workspace-harness self-test")
    return 0


# ------------------------------------------------------------------------------ main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quality", action="store_true", help="run the enforcement chain only")
    ap.add_argument("--connections", action="store_true", help="run the graph checks only")
    ap.add_argument("--tokens", action="store_true", help="run the traversal budget only")
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    ap.add_argument("--stamp", action="store_true", help="write the report stamp")
    ap.add_argument("--verbose", action="store_true", help="show output of failing gates")
    ap.add_argument("--self-test", action="store_true", help="police the harness itself")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if not REGISTRY.exists():
        print("workspace-harness: skills.registry.json missing — run build-registry.py first",
              file=sys.stderr)
        return 2

    pick_all = not (args.quality or args.connections or args.tokens)
    report: dict = {}
    if args.quality or pick_all:
        report["quality"] = run_quality(verbose=args.verbose)
    if args.connections or pick_all:
        report["connections"] = run_connections()
    if args.tokens or pick_all:
        report["tokens"] = run_tokens()

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)
    if args.stamp:
        write_stamp(report)

    return 1 if sum(report[k]["failed"] for k in report) else 0


if __name__ == "__main__":
    sys.exit(main())
