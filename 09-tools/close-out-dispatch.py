#!/usr/bin/env python3
"""Named close-out detectors for command hubs, and diff-computed gate selection (H10).

Exit codes:
  0  runnable CLI detectors passed (SKIP lines may remain — those classes are not verified)
  1  a runnable detector failed (for --from-diff: a CHARGED failure)
  2  nothing runnable (honest skip only), no hub matched, or (--from-diff) a step SKIPPED
  --check: 0 if every rigor_role=command-hub skill has a table row and the H10 diff classes are
           sound (steps exist in QUALITY_CHAIN, every chain step is classed, every class glob is in a
           workflow path filter, every tracked, hook, instruction and plugin path lies in a class)

Usage:
  python3 09-tools/close-out-dispatch.py --hub figma
  python3 09-tools/close-out-dispatch.py --from-prompt "build this in figma" --run
  python3 09-tools/close-out-dispatch.py --from-diff [--staged | --range A..B | --paths P...] [--run]
        [--fast] [--budget S] [--baseline REF] [--touched FILE] [--via V] [--json]
  python3 09-tools/close-out-dispatch.py --compliance [--range A..B] [--receipts FILE]
  python3 09-tools/close-out-dispatch.py --unlaned [--range A..B] [--since DATE]
  python3 09-tools/close-out-dispatch.py --identity-audit [--range A..B]
  python3 09-tools/close-out-dispatch.py --check
  python3 09-tools/close-out-dispatch.py --self-test

Every local --run appends one receipt (counts and ids only) to .workspace/state/receipts.jsonl in
the workspace checkout; CI and employer repos never get one. Commits carry the Workspace-Lane
trailer (git_lanes.py prepare-commit-msg); --compliance joins the two per surface.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
REGISTRY = ROOT / "03-skills" / "skills.registry.json"
PY = sys.executable or "python3"


def _load_hyphen(name: str):
    path = TOOLS / f"{name}.py"
    mod_name = name.replace("-", "_")
    spec = importlib.util.spec_from_file_location(mod_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


skill_loadset = _load_hyphen("skill-loadset")


@dataclass(frozen=True)
class Step:
    kind: str  # cli | skip
    name: str
    argv: tuple[str, ...] = ()
    note: str = ""


def _cli(script: str, *args: str, name: str | None = None) -> Step:
    path = TOOLS / script
    argv = (PY, str(path), *args)
    label = name or (f"{script} {' '.join(args)}".strip())
    return Step("cli", label, argv)


def _skip(name: str, note: str) -> Step:
    return Step("skip", name, note=note)


# One home for command-hub L3. --check fails if a rigor_role=command-hub skill
# is missing from this table, or if a table key is not a real skill. Skip steps
# are named detectors that cannot run in this process (MCP, device farm).
# Do not treat SKIP as verified.
HUB_DETECTORS: dict[str, tuple[Step, ...]] = {
    "qa": (
        _cli("validate-integrity.py"),
        _cli("evaluate-skill-routing.py", "--check"),
    ),
    # Editing the vault itself. validate-integrity alone cannot see a skill that became
    # unreachable or a traversal that got more expensive, so the harness is the detector.
    "self-improve": (
        _cli("workspace-harness.py", "--self-test"),
        _cli("workspace-harness.py", "--connections", "--tokens"),
        _cli("evaluate-surface-trajectories.py", "--check"),
        _cli("vault-health.py"),
    ),
    # Periodic full brain audit. These are the Step 1.6 probes that have a CLI; the judgment
    # findings (contradictions, staleness, consolidation) are critique and stay unverified here.
    "optimize": (
        _cli("validate-links.py"),
        _cli("build-registry.py", "--check"),
        _cli("validate-workspace.py"),
        _cli("vault-health.py"),
    ),
    # End-of-session protocol. The card must still render for the next session and the artifact
    # registry must stay queryable (Step 4). The push result itself is the evidence it landed.
    "session-end": (
        _cli("session-status.py", "--check"),
        _cli("artifact-find.py", "--check"),
    ),
    "ds": (
        _cli("validate-integrity.py"),
        _skip(
            "qa-visual",
            "Invoke /qa + Proofboard for a design-system artifact; vault integrity is not that detector.",
        ),
    ),
    "figma": (
        # Capture needs MCP (agent-only); JUDGING the capture is a CLI. Split honestly:
        # the skip is the capture step, the probe is the assess step A8 minted.
        _skip(
            "figma-mcp-capture",
            "Agent step: get_variable_defs + get_metadata on the node you just wrote, into "
            "your scratchpad (transient artifact, not a fixture). "
            "`figma-bind-probe.py --emit-template` prints the calls.",
        ),
        _cli("figma-bind-probe.py", "--self-test"),
        _skip("vqa-prove", "vqa prove BUILD CUESPEC when a reference exists."),
    ),
    "eng": (
        _cli("validate-integrity.py"),
        _skip(
            "product-ci",
            "Run the product repo's test/lint CI (`npm run lint:ds` when shadcn-bound). Vault integrity is not Pages/GHA.",
        ),
    ),
    "motion": (
        _skip("vqa-motion", "vqa motion --frames DIR when a sequence exists."),
        _cli("validate-integrity.py"),
    ),
    "type": (
        _skip("type-contrast", "a11y-visual / fonttools contrast on the delivered glyphs."),
        _cli("validate-integrity.py"),
    ),
    "redesign": (
        _cli("validate-integrity.py"),
        _skip(
            "qa-visual",
            "Native-zoom vs reference after redesign; vault integrity is not the visual detector.",
        ),
    ),
    "ai-design-systems": (
        _cli("validate-integrity.py"),
        _skip(
            "steel-curtain",
            "CI/axe/evals in the target product repo (`npm run lint:ds` when shadcn-bound); not LLM-as-judge.",
        ),
    ),
    "design-system-ops": (
        _cli("validate-integrity.py"),
        _cli("ds-source-watch.py", "--check"),
        _cli("token-audit.py", "--self-test"),
    ),
    # Three-tier token architecture (Subatomic canon). The self-test proves the detector; auditing a real
    # token source is the product repo's run (`token-audit.py --config … tokens/**/*.json`), not the vault's.
    "token-architecture": (
        _cli("token-audit.py", "--self-test"),
        _skip(
            "token-audit-target",
            "Run `09-tools/token-audit.py` against the target token source (+ --themes/--parity/--css/--outputs) "
            "in the product repo; Figma scopes via figma-mcp get_variable_defs.",
        ),
    ),
    "intent-coordination": (
        _cli("intent-run.py", "--self-test"),
        _skip("intent-run-doctor", "doctor is environment info, not a detector"),
    ),
    "lead-security-architect": (
        _skip(
            "sec-threat-modeling",
            "Threat model artifact before controls; no vault SAST of employer code.",
        ),
    ),
    "lead-mobile-engineer": (
        _skip(
            "device-lab",
            "No device farm in this vault. Product-repo tests stay in that repo.",
        ),
    ),
    "adobe-app-builder": (
        _skip("aio-cli", "requires aio-cli; degrade if missing (capability-registry)."),
    ),
    "vgpu-webgpu": (
        _skip("vgpu-doctor", "npx vgpu doctor when the job is a web GPU runtime."),
    ),
    "web-3d-extensions": (
        _skip("gltf-mesh", "vqa mesh ASSET when a glTF/GLB was produced."),
    ),
}


# --------------------------------------------------------------------------- H10: diff classes
#
# Gate selection computed from the diff. Every class maps path globs to QUALITY_CHAIN step names
# (workspace-harness.py is the one step source, so no flag is ever invented here). `owns` steps are
# the class's own consistency checks: a failure is CHARGED to the change. `tree` steps are
# whole-tree validators: a failure is CHARGED only when it names a changed path or the stem of a
# deleted/renamed one, or (with --baseline REF) when it adds error lines the baseline lacks;
# everything else is AMBIENT (printed, never red). `universal` classes do not count when --check
# asks whether every tracked path lies in a class. A changed tool also selects its own chain steps
# (TOOL_OWN). Step names are "<script> <args>" exactly as QUALITY_CHAIN spells them.
TOOL_OWN = "<tool-own>"
DIFF_CLASSES: dict[str, dict] = {
    "skills": {
        "globs": ["03-skills/**"],
        "owns": ["build-registry.py --check", "build-related.py --check", "build-trigger-routes.py --check",
                 "build-local-skill-plugin.py --check", "close-out-dispatch.py --check"],
        "tree": ["evaluate-skill-routing.py --check", "validate-links.py", "validate-capabilities.py --check",
                 "skill-loadset.py --self-test", "validate-integrity.py"],
    },
    "layer0": {
        "globs": ["02-shared-references/trigger-routes.json", "02-shared-references/knowledge-hints.json",
                  "02-shared-references/schemas/**", "02-shared-references/skill-routing-cases.jsonl",
                  "02-shared-references/surface-trajectory-cases.jsonl", "02-shared-references/trigger-routes*.md"],
        "owns": ["validate-layer0-schema.py --check", "build-trigger-routes.py --check"],
        "tree": ["evaluate-skill-routing.py --check", "evaluate-surface-trajectories.py --self-test",
                 "evaluate-surface-trajectories.py --check"],
    },
    "tools": {
        "globs": ["09-tools/**", "ruff.toml"],
        "owns": [TOOL_OWN, "test-validators.py"],
        "tree": [],
    },
    "hooks": {
        "globs": [".claude/hooks/**", "00-bootstrap/**"],
        "owns": ["../00-bootstrap/doctor/render_shims.py --check", "../.claude/hooks/dispatcher.py --self-test"],
        "tree": ["ws_hook.py --self-test", "ws_hook.py --self-test-shell", "../00-bootstrap/doctor/installers.py --self-test",
                 "../00-bootstrap/doctor/pin_lib.py --self-test", "git_lanes.py --self-test", "nightly.py --self-test"],
    },
    # Hook registrations, host settings, probes and the plugin layer (the snds plugin's hooks, the
    # generated skill wrappers Claude Code, Codex and Cursor discover, the Copilot skill pack).
    "surface-config": {
        "globs": ["02-shared-references/surfaces.json", "02-shared-references/probes/**",
                  "02-shared-references/beacons.json", "02-shared-references/skill-wrapper-allowlist.json",
                  ".claude/settings.json", ".claude/skills/**", ".agents/skills/**", ".cursor/hooks.json",
                  ".cursor/hooks/**", ".cursor/settings.json", ".cursor/agents/**", ".cursorignore", ".gemini/**",
                  ".windsurf/**", ".aider.conf.yml", "copilot/**", "00-bootstrap/dist/**"],
        "owns": ["../00-bootstrap/doctor/render_shims.py --check", "build-local-skill-plugin.py --check"],
        "tree": ["../00-bootstrap/doctor/render_shims.py --self-test", "build-local-skill-plugin.py --self-test",
                 "evaluate-surface-trajectories.py --check", "ws_hook.py --self-test"],
    },
    "identity-tables": {
        "globs": ["02-shared-references/devices.json", "02-shared-references/delivery-playbooks/*.json",
                  "02-shared-references/vetted-scripts.json"],
        "owns": ["profile_resolve.py validate-tables --require-all"],
        "tree": ["profile_resolve.py --self-test", "wall_guard.py --self-test", "git_lanes.py --self-test",
                 "prune-our-branches.py --self-test"],
    },
    "specs": {
        "globs": ["02-shared-references/intent-spec.md", "07-projects/*/PROJECT.md", "**/INTENT-*.md"],
        "owns": [],
        "tree": ["intent-run.py --self-test", "validate-evidence-grades.py"],
    },
    "entry-points": {
        "globs": ["AGENTS.md", "CLAUDE.md", "CURSOR.md", "PERPLEXITY.md", "GEMINI.md", "WARP.md", "CONVENTIONS.md",
                  "README.md", "llms.txt", ".cursor/rules/**", ".windsurf/rules/**", ".github/copilot-instructions.md",
                  ".github/CONVENTIONS.md"],
        "owns": [],
        "tree": ["evaluate-surface-trajectories.py --self-test", "evaluate-surface-trajectories.py --check",
                 "validate-integrity.py", "session-status.py --check"],
    },
    "context": {
        "globs": ["06-context/**"],
        "owns": ["artifact-find.py --check"],
        "tree": ["validate-workspace.py", "artifact-find.py --self-test", "session-status.py --check", "vault-health.py"],
    },
    "references": {
        "globs": ["02-shared-references/**"],
        "owns": [],
        "tree": ["validate-integrity.py", "validate-evidence-grades.py"],
    },
    "markdown": {
        "globs": ["**/*.md", "_archive/**", "01-frameworks/**", "04-preferences/**", "05-artifacts/**",
                  "08-knowledge/**", ".obsidian/**", ".github/*.md"],
        "owns": [],
        "tree": ["validate-integrity.py", "validate-workspace.py", "vault-health.py"],
    },
    # A newly tracked project folder is classed on arrival, so opting it in never turns --check red.
    "projects": {
        "globs": ["07-projects/**"],
        "owns": [],
        "tree": ["validate-integrity.py", "validate-workspace.py"],
    },
    "ci": {
        "globs": [".github/**", ".gitignore", ".gitattributes"],
        "owns": ["close-out-dispatch.py --check", "close-out-dispatch.py --self-test"],
        "tree": [],
    },
    "all": {
        "globs": ["**"],
        "universal": True,
        "owns": [],
        "tree": ["check-secrets.py", "check-secrets.py --class employer-substance --report"],
    },
}
# Flagged in the output and in the receipt; never silently green.
SENSITIVE_GLOBS = (
    ".github/workflows/**", ".gitignore", ".gitattributes", ".claude/settings.json",
    "00-bootstrap/dist/settings-user-fragment.json", "02-shared-references/surfaces.json",
    "02-shared-references/devices.json", "02-shared-references/delivery-playbooks/context-remotes.json",
    "02-shared-references/delivery-playbooks/action-policy.json", "02-shared-references/vetted-scripts.json",
)
# Steps measured over 5 s (2026-09-25, a sandboxed read-only chain run on the Work MBP); --fast drops them.
SLOW_STEPS = frozenset({
    "test-validators.py", "git_lanes.py --self-test", "profile_resolve.py --self-test", "intent-run.py --self-test",
    "../00-bootstrap/doctor/installers.py --self-test", "ws_hook.py --self-test", "ws_hook.py --self-test-shell",
    "nightly.py --self-test", "closure.py --self-test", "wall_guard.py --self-test", "prune-our-branches.py --self-test",
    "../00-bootstrap/doctor/render_shims.py --self-test", "build-local-skill-plugin.py --self-test",
    "../.claude/hooks/dispatcher.py --self-test", "evaluate-surface-trajectories.py --check",
    "../00-bootstrap/doctor/pin_lib.py --self-test",
})
STEP_TIMEOUT_S = 300.0
DEFAULT_BUDGET_S = 900.0
# The lane trailer (git_lanes.py prepare-commit-msg) and where local gate receipts go (gitignored state).
TRAILER_KEY = "Workspace-Lane"
RECEIPTS_REL = ".workspace/state/receipts.jsonl"
COMPLIANCE_SURFACES = ("claude-code", "cursor", "codex")
# Surfaces whose transcripts no workspace reader scans: their compliance column is an honest SKIP.
TRANSCRIPT_SKIP = {"codex": "no Codex transcript reader; receipts and trailers only"}
UNLANED_SINCE = "2026-09-26"
GATE_WORKFLOW = ".github/workflows/gate-selection.yml"
INSTRUCTION_FILES = ("AGENTS.md", "CLAUDE.md", "CURSOR.md", "PERPLEXITY.md", "GEMINI.md", "WARP.md",
                     "CONVENTIONS.md", "llms.txt")


def _glob_re(pattern: str):
    """GitHub path-filter semantics: `**` crosses '/', `*` and `?` do not."""
    out, i = [], 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def glob_match(pattern: str, path: str) -> bool:
    return bool(_glob_re(pattern).match(path))


def filter_covers(flt: str, glob: str) -> bool:
    """A workflow path filter covers a class glob when they are equal or the filter matches the glob
    read as a literal path (`03-skills/**` covers `03-skills/**/SKILL.md`)."""
    return flt == glob or glob_match(flt, glob)


def chain_steps(chain=None) -> dict[str, tuple[str, list[str]]]:
    """{step name: (script, args)} from workspace-harness QUALITY_CHAIN (or an injected chain)."""
    if chain is None:
        chain = _load_hyphen("workspace-harness").QUALITY_CHAIN
    return {f"{s} {' '.join(a)}".strip(): (s, list(a)) for s, a in chain}


def _script_rel(script: str) -> str:
    return os.path.normpath(os.path.join("09-tools", script)).replace(os.sep, "/")


def classes_for(paths, classes=None) -> list[str]:
    classes = DIFF_CLASSES if classes is None else classes
    return [name for name, c in classes.items() if any(glob_match(g, p) for p in paths for g in c["globs"])]


def tool_own_steps(paths, steps: dict) -> list[str]:
    """A changed tool (or its fixtures folder) selects its own chain entries."""
    out = []
    for name, (script, _a) in steps.items():
        rel = _script_rel(script)
        stem = Path(rel).stem
        for p in paths:
            if p == rel or p.startswith(f"09-tools/fixtures/{stem}/"):
                out.append(name)
                break
    return out


def select_steps(paths, *, classes=None, steps=None, fast=False) -> dict:
    """{classes, steps: [(name, owned_by_class_or_None)], sensitive, dropped_slow} in chain order."""
    classes = DIFF_CLASSES if classes is None else classes
    steps = chain_steps() if steps is None else steps
    matched = classes_for(paths, classes)
    owned: dict[str, str] = {}
    tree: set[str] = set()
    for cname in matched:
        for s in classes[cname].get("owns", []):
            if s == TOOL_OWN:
                for t in tool_own_steps(paths, steps):
                    owned.setdefault(t, cname)
            else:
                owned.setdefault(s, cname)
        tree.update(classes[cname].get("tree", []))
    wanted = set(owned) | tree
    order = [n for n in steps if n in wanted]
    dropped = [n for n in order if fast and n in SLOW_STEPS]
    order = [n for n in order if n not in dropped]
    sensitive = sorted(p for p in paths if any(glob_match(g, p) for g in SENSITIVE_GLOBS))
    return {"classes": matched, "steps": [(n, owned.get(n)) for n in order], "sensitive": sensitive,
            "dropped_slow": dropped}


# ------------------------------------------------------------------ workflows (stdlib reader)

def read_workflow(text: str) -> dict:
    """The bits --check needs from one workflow file: push/pull_request path filters (None when the
    event has no filter), schedule, workflow_dispatch. A line reader, not a YAML parser: it knows the
    block and flow forms these workflows use."""
    out = {"push": None, "pull_request": None, "push_on": False, "pr_on": False, "schedule": False,
           "dispatch": False, "text": text}
    lines = text.splitlines()
    in_on, on_indent, event, ev_indent, in_paths, p_indent = False, 0, None, 0, False, 0
    for raw in lines:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        ind = len(raw) - len(raw.lstrip())
        s = raw.strip()
        if re.match(r"^['\"]?on['\"]?\s*:", s) and ind == 0:
            in_on, on_indent, event = True, ind, None
            rest = s.split(":", 1)[1].strip()
            if rest:
                for ev in re.findall(r"[\w_]+", rest):
                    out.update({"push_on": out["push_on"] or ev == "push", "pr_on": out["pr_on"] or ev == "pull_request",
                                "dispatch": out["dispatch"] or ev == "workflow_dispatch"})
                in_on = False
            continue
        if in_on and ind <= on_indent:
            in_on = False
        if not in_on:
            continue
        if in_paths and ind > p_indent and s.startswith("- "):
            out[event].append(s[2:].strip().strip("'\""))
            continue
        in_paths = False
        m = re.match(r"^([\w_-]+)\s*:\s*(.*)$", s)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if event is None or ind <= ev_indent:
            event, ev_indent = key, ind
            if key == "push":
                out["push_on"] = True
            elif key == "pull_request":
                out["pr_on"] = True
            elif key == "schedule":
                out["schedule"] = True
            elif key == "workflow_dispatch":
                out["dispatch"] = True
            continue
        if key == "paths" and event in ("push", "pull_request"):
            if val.startswith("["):
                out[event] = [x.strip().strip("'\"") for x in val.strip("[]").split(",") if x.strip()]
            else:
                out[event] = []
                in_paths, p_indent = True, ind
    return out


def read_workflows(root: Path) -> dict[str, dict]:
    wf_dir = root / ".github" / "workflows"
    out = {}
    for p in sorted(wf_dir.glob("*.y*ml")) if wf_dir.is_dir() else []:
        try:
            out[f".github/workflows/{p.name}"] = read_workflow(p.read_text(encoding="utf-8"))
        except OSError:
            continue
    return out


# ------------------------------------------------------------------ the diff check

def _tracked(root: Path) -> list[str]:
    try:
        r = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return []
    return [ln for ln in r.stdout.splitlines() if ln.strip()] if r.returncode == 0 else []


def surface_paths(root: Path) -> dict[str, list[str]]:
    """Hook, instruction and plugin paths the surface table and the tree declare (repo-relative)."""
    hooks, plugin = set(), set()
    try:
        t = json.loads((root / "02-shared-references" / "surfaces.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        t = {}
    for lay in t.get("layers") or []:
        out = lay.get("output")
        if isinstance(out, str) and not out.startswith("~"):
            (plugin if "plugin" in str(lay.get("id")) else hooks).add(out)
    for o in t.get("outputs") or []:
        p = o.get("path")
        if isinstance(p, str) and not p.startswith("~"):
            (plugin if "plugin" in str(o.get("id")) else hooks).add(p)
    for p in (t.get("wrappers") or {}):
        hooks.add(p)
    tracked = _tracked(root)
    hooks.update(p for p in tracked if p.startswith(".claude/hooks/") or p.startswith(".cursor/hooks"))
    plugin.update(p for p in tracked if p.startswith((".claude/skills/", ".agents/skills/", "copilot/")))
    instr = {p for p in INSTRUCTION_FILES if (root / p).is_file()}
    instr.update(p for p in tracked if p.startswith((".cursor/rules/", ".windsurf/rules/")))
    return {"hook": sorted(hooks), "instruction": sorted(instr), "plugin": sorted(plugin)}


def check_diff_classes(*, root: Path = ROOT, classes=None, steps=None, workflows=None, tracked=None,
                       surface=None) -> list[str]:
    """--check for H10. Every error is one line."""
    classes = DIFF_CLASSES if classes is None else classes
    steps = chain_steps() if steps is None else steps
    workflows = read_workflows(root) if workflows is None else workflows
    tracked = _tracked(root) if tracked is None else tracked
    surface = surface_paths(root) if surface is None else surface
    errors: list[str] = []
    used: set[str] = set()
    for cname, c in classes.items():
        for s in list(c.get("owns", [])) + list(c.get("tree", [])):
            if s == TOOL_OWN:
                used.update(n for n, (sc, _a) in steps.items() if _script_rel(sc).startswith("09-tools/")
                            or sc.startswith("../"))
                continue
            if s not in steps:
                errors.append(f"class {cname}: step {s!r} is not in QUALITY_CHAIN (workspace-harness.py)")
            used.add(s)
    for n in steps:
        if n not in used:
            errors.append(f"QUALITY_CHAIN step {n!r} belongs to no diff class")
    filtered = {name: w for name, w in workflows.items() if w.get("push")}
    for cname, c in classes.items():
        if c.get("universal"):
            continue
        for g in c["globs"]:
            if not any(filter_covers(f, g) for w in filtered.values() for f in w["push"]):
                errors.append(f"filter gap: class {cname} glob {g!r} is in no workflow's push path filter")
    gate = workflows.get(GATE_WORKFLOW)
    if gate is None:
        errors.append(f"{GATE_WORKFLOW} is missing (diff-selected gates, schedule, dispatch)")
    else:
        if not (gate.get("schedule") and gate.get("dispatch")):
            errors.append(f"{GATE_WORKFLOW}: needs both a schedule and a workflow_dispatch trigger")
        if "close-out-dispatch.py --from-diff" not in gate.get("text", ""):
            errors.append(f"{GATE_WORKFLOW}: does not run close-out-dispatch.py --from-diff")
    named = [c for n, c in classes.items() if not c.get("universal")]
    for p in tracked:
        if not any(glob_match(g, p) for c in named for g in c["globs"]):
            errors.append(f"tracked path {p} lies in no diff class")
    by_kind = {"hook": ("hooks", "surface-config"), "instruction": ("entry-points",), "plugin": ("surface-config",)}
    for kind, owners in by_kind.items():
        for p in surface.get(kind, []):
            if not any(glob_match(g, p) for o in owners for g in (classes.get(o) or {}).get("globs", [])):
                errors.append(f"{kind} path {p} lies in none of the {'/'.join(owners)} classes")
    return errors


# ------------------------------------------------------------------ changed paths

def _git_lines(root: Path, *args: str) -> list[str]:
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return []
    return r.stdout.splitlines() if r.returncode == 0 else []


def changed_paths(root: Path, *, staged: bool = False, rng: str | None = None) -> dict:
    """{changed: [...], deleted: [...]} from `git diff --name-status` (renames count as delete+add)."""
    if rng:
        lines = _git_lines(root, "diff", "--name-status", "-M", rng)
    elif staged:
        lines = _git_lines(root, "diff", "--cached", "--name-status", "-M")
    else:
        lines = _git_lines(root, "diff", "--name-status", "-M", "HEAD")
        lines += [f"A\t{p}" for p in _git_lines(root, "ls-files", "--others", "--exclude-standard")]
    changed, deleted = [], []
    for ln in lines:
        parts = ln.split("\t")
        if len(parts) < 2:
            continue
        st = parts[0][:1]
        if st == "D":
            deleted.append(parts[1])
        elif st == "R" and len(parts) >= 3:
            deleted.append(parts[1])
            changed.append(parts[2])
        else:
            changed.append(parts[-1])
    return {"changed": sorted(set(changed)), "deleted": sorted(set(deleted))}


# ------------------------------------------------------------------ run + attribution

def _norm_lines(text: str) -> set[str]:
    return {re.sub(r"\d+(\.\d+)?\s*(ms|s)\b", "<t>", ln.strip()) for ln in text.splitlines() if ln.strip()}


def _names(text: str, paths, deleted) -> bool:
    for p in paths:
        if p and p in text:
            return True
    for d in deleted:
        stem = Path(d).stem
        if d in text or (len(stem) >= 3 and (f"[[{stem}" in text or f"{stem}.md" in text or f"'{stem}'" in text)):
            return True
    return False


def _run_step(root: Path, script: str, args: list[str], timeout: float) -> dict:
    target = (root / "09-tools" / script).resolve()
    if not target.is_file():
        return {"rc": None, "out": f"missing {script}", "secs": 0.0, "timeout": False}
    start = time.monotonic()
    try:
        p = subprocess.run([PY, str(target), *args], cwd=str(root), capture_output=True, text=True,
                           timeout=max(0.1, timeout))
    except subprocess.TimeoutExpired:
        return {"rc": None, "out": "", "secs": round(time.monotonic() - start, 2), "timeout": True}
    return {"rc": p.returncode, "out": (p.stdout or "") + (p.stderr or ""),
            "secs": round(time.monotonic() - start, 2), "timeout": False}


def _baseline_tree(root: Path, ref: str, dest: Path) -> bool:
    """Export REF (tracked files only) into dest without touching the repo."""
    try:
        a = subprocess.run(["git", "-C", str(root), "archive", "--format=tar", ref], capture_output=True, timeout=120)
        if a.returncode != 0:
            return False
        import io as _io
        import tarfile
        with tarfile.open(fileobj=_io.BytesIO(a.stdout)) as tf:
            tf.extractall(dest, filter="data") if hasattr(tarfile, "data_filter") else tf.extractall(dest)
        return True
    except Exception:  # noqa: BLE001 - a baseline is best effort
        return False


def run_gate(paths: dict, *, root: Path = ROOT, classes=None, steps=None, fast: bool = False,
             budget: float = DEFAULT_BUDGET_S, step_timeout: float = STEP_TIMEOUT_S, touched=None,
             baseline: str | None = None, out=None) -> dict:
    """Run the diff-selected steps. CHARGED fails the gate (exit 1); SKIPPED (timeout, budget) is exit 2
    unless something is charged; AMBIENT failures print and stay exit 0."""
    out = out or sys.stdout
    steps = chain_steps() if steps is None else steps
    changed, deleted = list(paths.get("changed") or []), list(paths.get("deleted") or [])
    attrib = list(touched) if touched is not None else changed
    sel = select_steps(changed + deleted, classes=classes, steps=steps, fast=fast)
    base_dir = None
    results = []
    deadline = time.monotonic() + budget
    try:
        for name, owner in sel["steps"]:
            script, args = steps[name]
            left = deadline - time.monotonic()
            if left <= 0:
                results.append({"step": name, "status": "SKIPPED", "why": "budget spent"})
                continue
            r = _run_step(root, script, args, min(step_timeout, left))
            if r["timeout"]:
                results.append({"step": name, "status": "SKIPPED", "why": f"timed out after {r['secs']}s"})
                continue
            if r["rc"] == 0:
                results.append({"step": name, "status": "ok", "secs": r["secs"]})
                continue
            if r["rc"] == 3:
                results.append({"step": name, "status": "SKIPPED", "why": "the step reported SKIPPED (exit 3)"})
                continue
            if owner is not None:
                why = f"owned by class {owner}"
                charged = True
            elif baseline:
                if base_dir is None:
                    base_dir = Path(tempfile.mkdtemp(prefix="ws-gate-base-"))
                    if not _baseline_tree(root, baseline, base_dir):
                        base_dir = False
                if base_dir:
                    b = _run_step(base_dir, script, args, min(step_timeout, max(0.1, deadline - time.monotonic())))
                    new = _norm_lines(r["out"]) - (_norm_lines(b["out"]) if b["rc"] not in (0, None) else set())
                    charged = b["rc"] == 0 or bool(new)
                    why = f"new against {baseline}" if charged else f"also fails at {baseline}"
                else:
                    charged = _names(r["out"], attrib, deleted)
                    why = "names a changed path" if charged else "names no changed path (baseline unavailable)"
            else:
                charged = _names(r["out"], attrib, deleted)
                why = "names a changed or deleted path" if charged else "names no changed path"
            tail = [ln for ln in r["out"].strip().splitlines()][-8:]
            results.append({"step": name, "status": "CHARGED" if charged else "AMBIENT", "why": why,
                            "rc": r["rc"], "tail": tail})
    finally:
        if base_dir:
            shutil.rmtree(base_dir, ignore_errors=True)
    charged_n = sum(1 for x in results if x["status"] == "CHARGED")
    skipped_n = sum(1 for x in results if x["status"] == "SKIPPED")
    ambient_n = sum(1 for x in results if x["status"] == "AMBIENT")
    rc = 1 if charged_n else (2 if skipped_n or not results else 0)
    verdict = {"result": {0: "pass", 1: "fail", 2: "skipped"}[rc], "steps": len(results), "charged": charged_n,
               "ambient": ambient_n, "skipped": skipped_n, "sensitive": len(sel["sensitive"])}
    return {"rc": rc, "selection": sel, "results": results, "verdict": verdict}


def format_gate(res: dict) -> str:
    sel = res["selection"]
    lines = ["# close-out-dispatch --from-diff",
             "classes: " + (", ".join(sel["classes"]) or "(none)")]
    for p in sel["sensitive"]:
        lines.append(f"SENSITIVE {p}")
    for d in sel["dropped_slow"]:
        lines.append(f"FAST-DROPPED {d} (over 5 s; not verified this run)")
    for r in res.get("results") or []:
        extra = f" — {r['why']}" if r.get("why") else ""
        lines.append(f"{r['status']:8} {r['step']}{extra}")
        if r["status"] == "CHARGED":
            lines += [f"    {t}" for t in r.get("tail", [])]
            lines.append(f"    repro: python3 09-tools/{r['step']}")
    v = res["verdict"]
    lines.append(f"gate: {v['result']} (steps {v['steps']}, charged {v['charged']}, ambient {v['ambient']}, "
                 f"skipped {v['skipped']}, sensitive {v['sensitive']})")
    if v["skipped"]:
        lines.append("SKIPPED steps are not verified (exit 2 unless something is charged).")
    return "\n".join(lines)


# ------------------------------------------------------------------ receipts

def _profile_resolve():
    try:
        return _load_hyphen("profile_resolve")
    except Exception:  # noqa: BLE001 - a receipt is best effort
        return None


def gate_context(root: Path = ROOT, *, pr=None) -> dict:
    """{surface, family, device, repo_slug, owner_class}; every field falls back to 'unknown'."""
    pr = _profile_resolve() if pr is None else pr
    ctx = {"surface": "unknown", "family": "unknown", "device": "unknown", "repo_slug": None, "owner_class": "unknown"}
    if pr is None:
        return ctx
    try:
        det = pr.detect_surface()
        ctx["surface"] = str(det.get("acting_host") or ("human" if det.get("family") == "human" else "unknown"))
        ctx["family"] = str(det.get("family_for_walls") or "unknown")
    except Exception:  # noqa: BLE001
        pass
    try:
        ctx["device"] = str(pr.current_device().get("id") or "unknown")
    except Exception:  # noqa: BLE001
        pass
    try:
        res = pr.repo_resolve(str(root))
        ctx["repo_slug"] = pr._slug_of(res)
        ctx["owner_class"] = str(res.get("owner_class") or "unknown")
    except Exception:  # noqa: BLE001
        pass
    return ctx


def make_receipt(ctx: dict, *, via: str, head: str, classes, verdict: dict, ts: str | None = None) -> dict:
    """Counts and ids only: no paths, no output, no credential values."""
    return {"ts": ts or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "surface": ctx.get("surface"),
            "family": ctx.get("family"), "via": via, "device": ctx.get("device"), "repo_slug": ctx.get("repo_slug"),
            "action_class": "gate", "credential": "none", "head": head, "classes": list(classes),
            "verdict": dict(verdict)}


def write_receipt(root: Path, receipt: dict, *, owner_class: str = "unknown") -> Path | None:
    """Append to <workspace>/.workspace/state/receipts.jsonl. Never in CI, never outside a workspace
    checkout (AGENTS.md at the root), never for an employer-classed repo. Fails quiet."""
    if os.environ.get("GITHUB_ACTIONS") or owner_class == "employer" or not (root / "AGENTS.md").is_file():
        return None
    path = root / RECEIPTS_REL
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(receipt, sort_keys=True) + "\n")
    except OSError:
        return None
    return path


def read_receipts(path: Path) -> list[dict]:
    out = []
    try:
        for ln in path.read_text(encoding="utf-8").splitlines():
            try:
                obj = json.loads(ln)
            except ValueError:
                continue
            if isinstance(obj, dict):
                out.append(obj)
    except OSError:
        pass
    return out


def _head(root: Path) -> str:
    lines = _git_lines(root, "rev-parse", "HEAD")
    return lines[0].strip() if lines else "unknown"


# ------------------------------------------------------------------ trailers, compliance, identity

def read_commits(root: Path, rng: str | None = None, *, since: str | None = None, limit: int = 500) -> list[dict]:
    """[{sha, parents, lane, author, committer}] newest first. `lane` is the Workspace-Lane trailer."""
    fmt = f"%H%x00%P%x00%ae%x00%ce%x00%(trailers:key={TRAILER_KEY},valueonly,separator=%x2C)%x1e"
    args = ["log", f"--format={fmt}", f"-n{limit}"]
    if since:
        args.append(f"--since={since}")
    args.append(rng or "HEAD")
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return []
    if r.returncode != 0:
        return []
    out = []
    for rec in r.stdout.split("\x1e"):
        rec = rec.strip("\n")
        if not rec.strip():
            continue
        parts = rec.split("\x00")
        if len(parts) < 5:
            continue
        lane = parts[4].strip().split(",")[0].strip() or None
        out.append({"sha": parts[0], "parents": parts[1].split(), "author": parts[2], "committer": parts[3],
                    "lane": lane})
    return out


def parse_lane(value: str | None) -> dict | None:
    if not value:
        return None
    bits = value.strip().split("/")
    if len(bits) != 3 or not all(bits):
        return None
    return {"surface": bits[0], "family": bits[1], "device": bits[2]}


def unlaned(commits: list[dict]) -> int:
    """Non-merge commits with no parseable lane trailer."""
    return sum(1 for c in commits if len(c.get("parents") or []) <= 1 and parse_lane(c.get("lane")) is None)


def compliance(receipts: list[dict], commits: list[dict], surfaces=COMPLIANCE_SURFACES) -> dict:
    """Per surface: laned commits, how many a same-surface gate receipt covers (receipt head is the
    commit or its first parent), receipts seen, and the transcript column (SKIP where no reader)."""
    by_surface: dict[str, dict] = {}
    heads: dict[str, set] = {}
    for rc in receipts:
        if rc.get("action_class") != "gate":
            continue
        s = str(rc.get("surface") or "unknown")
        heads.setdefault(s, set()).add(str(rc.get("head")))
        by_surface.setdefault(s, {"commits": 0, "gated": 0, "receipts": 0})["receipts"] += 1
    for c in commits:
        lane = parse_lane(c.get("lane"))
        if lane is None:
            continue
        s = lane["surface"]
        row = by_surface.setdefault(s, {"commits": 0, "gated": 0, "receipts": 0})
        row["commits"] += 1
        parents = c.get("parents") or []
        if c["sha"] in heads.get(s, ()) or (parents and parents[0] in heads.get(s, ())):
            row["gated"] += 1
    order = list(surfaces) + sorted(s for s in by_surface if s not in surfaces)
    rows = []
    for s in order:
        row = dict(by_surface.get(s) or {"commits": 0, "gated": 0, "receipts": 0})
        row["surface"] = s
        row["transcripts"] = f"SKIP ({TRANSCRIPT_SKIP[s]})" if s in TRANSCRIPT_SKIP else "-"
        rows.append(row)
    return {"commits": len(commits), "unlaned": unlaned(commits), "rows": rows}


def format_compliance(res: dict, rng: str) -> str:
    lines = [f"compliance range={rng} commits={res['commits']} unlaned={res['unlaned']}"]
    for r in res["rows"]:
        ratio = f"{r['gated']}/{r['commits']}" if r["commits"] else "n/a (no laned commits)"
        lines.append(f"  {r['surface']:<12} commits={r['commits']} gated={r['gated']} receipts={r['receipts']} "
                     f"compliance={ratio} transcripts={r['transcripts']}")
    return "\n".join(lines)


def identity_audit(commits: list[dict], devices: dict) -> dict:
    """Counts only: commits whose author or committer is not a declared identity or known agent bot, and
    Claude-laned commits not made with a personal identity (IR1)."""
    ids = {str(i.get("email", "")).casefold(): str(i.get("class")) for i in devices.get("identities") or []}
    bots = ("cursoragent@cursor.com", "noreply@github.com", "github-actions[bot]@users.noreply.github.com")
    undeclared = claude_non_personal = 0
    for c in commits:
        emails = {str(c.get("author", "")).casefold(), str(c.get("committer", "")).casefold()}
        if any(e not in ids and not e.endswith(bots) and "[bot]" not in e for e in emails):
            undeclared += 1
        lane = parse_lane(c.get("lane"))
        if lane and lane["family"] == "claude" and ids.get(str(c.get("author", "")).casefold()) != "personal":
            claude_non_personal += 1
    return {"commits": len(commits), "undeclared_identity": undeclared, "claude_non_personal": claude_non_personal}


def command_hubs(data: dict) -> list[str]:
    return sorted(
        name
        for name, rec in (data.get("skills") or {}).items()
        if rec.get("rigor_role") == "command-hub"
    )


def hubs_for_prompt(prompt: str, data: dict) -> list[str]:
    result = skill_loadset.load_set(prompt, data)
    names: list[str] = []
    skills = data.get("skills") or {}
    for name in result["load"] + result["matched"]:
        rec = skills.get(name) or {}
        if rec.get("rigor_role") == "command-hub" or name in HUB_DETECTORS:
            if name not in names:
                names.append(name)
        for gov in rec.get("governed_by") or []:
            if gov in HUB_DETECTORS and gov not in names:
                names.append(gov)
    if not names:
        lowered = (prompt or "").lower()
        if any(w in lowered for w in ("workspace", "vault", "agents.md", "skill-loadset")):
            names.append("self-improve")
    return names


def format_plan(hubs: list[str]) -> str:
    lines = ["# close-out-dispatch", ""]
    if not hubs:
        lines.append("hubs: (none)")
        lines.append("SKIP: no command hub matched — do not claim verified.")
        return "\n".join(lines)
    lines.append("hubs: " + ", ".join(hubs))
    for hub in hubs:
        lines.append(f"## {hub}")
        for step in HUB_DETECTORS.get(hub, ()):
            if step.kind == "cli":
                cmd = " ".join(step.argv) if step.argv else step.name
                lines.append(f"- CLI `{step.name}`: {cmd}")
            else:
                lines.append(f"- SKIP `{step.name}`: {step.note}")
    lines.append("")
    lines.append(
        "Run with --run. Exit 0 means runnable CLIs passed; SKIP classes are not verified. "
        "Exit 2 means nothing runnable (honest skip only)."
    )
    return "\n".join(lines)


def run_hubs(hubs: list[str], *, via: str = "manual") -> int:
    rc = _run_hubs(hubs)
    try:
        ctx = gate_context(ROOT)
        verdict = {"result": {0: "pass", 1: "fail", 2: "skipped"}.get(rc, "fail"), "hubs": len(hubs)}
        write_receipt(ROOT, make_receipt(ctx, via=via, head=_head(ROOT), classes=[f"hub:{h}" for h in hubs],
                                         verdict=verdict), owner_class=ctx["owner_class"])
    except Exception:  # noqa: BLE001 - a receipt never changes the gate's result
        pass
    return rc


def _run_hubs(hubs: list[str]) -> int:
    if not hubs:
        print("SKIP: no command hub matched — do not claim verified.", file=sys.stderr)
        return 2
    ran = 0
    failed = 0
    skips = 0
    print(format_plan(hubs))
    print("--- run ---")
    for hub in hubs:
        for step in HUB_DETECTORS.get(hub, ()):
            if step.kind == "skip":
                skips += 1
                print(f"SKIP {hub}/{step.name}: {step.note}")
                continue
            argv = list(step.argv)
            print(f"RUN {' '.join(argv)}")
            proc = subprocess.run(argv, cwd=str(ROOT))
            ran += 1
            if proc.returncode != 0:
                failed += 1
                print(f"FAIL {step.name} exit {proc.returncode}", file=sys.stderr)
    if failed:
        return 1
    if ran == 0:
        print("SKIP-only: no CLI detector ran. Do not claim verified.", file=sys.stderr)
        return 2
    if skips:
        print(f"CLI passed ({ran}); {skips} SKIP class(es) remain unverified.")
    return 0


def check_table() -> int:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    skills = data.get("skills") or {}
    hubs = command_hubs(data)
    errors: list[str] = []
    missing = [h for h in hubs if h not in HUB_DETECTORS]
    if missing:
        errors.append("command hubs missing from HUB_DETECTORS: " + ", ".join(missing))
    for name, steps in HUB_DETECTORS.items():
        if name not in skills:
            errors.append(f"{name}: not a registry skill")
        elif skills[name].get("rigor_role") != "command-hub":
            errors.append(f"{name}: table key is not rigor_role=command-hub")
        if not steps:
            errors.append(f"{name}: empty detector list")
        names = [s.name for s in steps]
        if len(names) != len(set(names)):
            errors.append(f"{name}: duplicate detector name")
    errors += check_diff_classes()
    for e in errors:
        print(f"  ✗ {e}", file=sys.stderr)
    if errors:
        return 1
    print(f"OK close-out-dispatch — {len(hubs)} command hubs have named detectors; "
          f"{len(DIFF_CLASSES)} diff classes cover the chain, the workflow filters and every tracked path")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Named close-out detectors and diff-computed gates")
    parser.add_argument("--hub", action="append", default=[])
    parser.add_argument("--from-prompt", default="")
    parser.add_argument("--skills", default="", help="comma-separated skill names")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--from-diff", action="store_true", help="select QUALITY_CHAIN steps from the diff")
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--range", dest="rng", default=None)
    parser.add_argument("--paths", nargs="*", default=None)
    parser.add_argument("--fast", action="store_true")
    parser.add_argument("--budget", type=float, default=DEFAULT_BUDGET_S)
    parser.add_argument("--baseline", default=None, help="REF whose own failures are AMBIENT")
    parser.add_argument("--touched", default=None, help="file listing this session's paths (attribution)")
    parser.add_argument("--via", default="manual", help="who invoked the gate (receipt field)")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--compliance", action="store_true")
    parser.add_argument("--receipts", default=None)
    parser.add_argument("--unlaned", action="store_true")
    parser.add_argument("--since", default=None)
    parser.add_argument("--identity-audit", action="store_true")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.check:
        return check_table()
    if args.compliance or args.unlaned or args.identity_audit:
        return _report(args)
    if args.from_diff:
        return _from_diff(args)
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    hubs: list[str] = []
    for h in args.hub:
        if h not in hubs:
            hubs.append(h)
    if args.skills:
        skills = data.get("skills") or {}
        for name in args.skills.split(","):
            name = name.strip()
            if not name:
                continue
            rec = skills.get(name) or {}
            if name in HUB_DETECTORS and name not in hubs:
                hubs.append(name)
            for gov in rec.get("governed_by") or []:
                if gov in HUB_DETECTORS and gov not in hubs:
                    hubs.append(gov)
            if rec.get("rigor_role") == "command-hub" and name not in hubs:
                hubs.append(name)
    if args.from_prompt.strip():
        for name in hubs_for_prompt(args.from_prompt, data):
            if name not in hubs:
                hubs.append(name)
    if args.run:
        return run_hubs(hubs, via=args.via)
    print(format_plan(hubs))
    return 0 if hubs else 2


def _from_diff(args) -> int:
    if args.paths is not None:
        paths = {"changed": sorted(set(args.paths)), "deleted": []}
    else:
        paths = changed_paths(ROOT, staged=args.staged, rng=args.rng)
    touched = None
    if args.touched:
        try:
            touched = [ln.strip() for ln in Path(args.touched).read_text(encoding="utf-8").splitlines() if ln.strip()]
        except OSError:
            touched = None
    if not args.run:
        sel = select_steps(paths["changed"] + paths["deleted"], fast=args.fast)
        if args.json:
            print(json.dumps({**sel, "paths": len(paths["changed"]) + len(paths["deleted"])}, indent=2))
        else:
            print("classes: " + (", ".join(sel["classes"]) or "(none)"))
            for p in sel["sensitive"]:
                print(f"SENSITIVE {p}")
            for name, owner in sel["steps"]:
                print(f"- {name}" + (f"  (owned by {owner})" if owner else ""))
            for d in sel["dropped_slow"]:
                print(f"FAST-DROPPED {d}")
        return 0 if sel["steps"] else 2
    res = run_gate(paths, fast=args.fast, budget=args.budget, touched=touched, baseline=args.baseline)
    print(json.dumps(res, indent=2) if args.json else format_gate(res))
    try:
        ctx = gate_context(ROOT)
        write_receipt(ROOT, make_receipt(ctx, via=args.via, head=_head(ROOT), classes=res["selection"]["classes"],
                                         verdict=res["verdict"]), owner_class=ctx["owner_class"])
    except Exception:  # noqa: BLE001 - a receipt never changes the gate's result
        pass
    return res["rc"]


def _report(args) -> int:
    rng = args.rng
    label = rng or "HEAD (last 500)"
    if args.since == "epoch":
        args.since = UNLANED_SINCE
    commits = read_commits(ROOT, rng, since=args.since)
    if args.unlaned:
        n = unlaned(commits)
        since = f" since {args.since}" if args.since else ""
        print(f"unlaned={n} commits={len(commits)} range={label}{since}")
        if os.environ.get("GITHUB_ACTIONS") and n:
            print(f"::warning::{n} workspace commit(s) in {label} carry no {TRAILER_KEY} trailer (unlaned)")
        return 0
    if args.identity_audit:
        try:
            devices = json.loads((ROOT / "02-shared-references" / "devices.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            print("identity audit: devices.json unreadable", file=sys.stderr)
            return 2
        res = identity_audit(commits, devices)
        print(f"identity commits={res['commits']} undeclared_identity={res['undeclared_identity']} "
              f"claude_non_personal={res['claude_non_personal']} range={label}")
        if os.environ.get("GITHUB_ACTIONS") and (res["undeclared_identity"] or res["claude_non_personal"]):
            print("::warning::identity audit: commits with an undeclared identity or a Claude lane without the "
                  "personal identity (counts above)")
        return 0
    path = Path(args.receipts) if args.receipts else ROOT / RECEIPTS_REL
    res = compliance(read_receipts(path), commits)
    print(json.dumps(res, indent=2) if args.json else format_compliance(res, label))
    return 0


# --------------------------------------------------------------------------- self-test

def self_test() -> int:
    """Pure cases (no git, no subprocess): selection, filter and plugin gaps, compliance, unlaned,
    receipts. The temp-repo cases live in TestCloseOutDispatch (test-validators.py)."""
    fails: list[str] = []
    n = [0]

    def ok(cond, label):
        n[0] += 1
        if not cond:
            fails.append(label)
            print(f"FAIL {label}", file=sys.stderr)

    steps = {"a.py --check": ("a.py", ["--check"]), "b.py": ("b.py", []), "c.py --self-test": ("c.py", ["--self-test"])}
    classes = {
        "skills": {"globs": ["03-skills/**"], "owns": ["a.py --check"], "tree": ["b.py"]},
        "tools": {"globs": ["09-tools/**"], "owns": [TOOL_OWN], "tree": []},
        "docs": {"globs": ["**/*.md"], "owns": [], "tree": ["b.py"]},
        "surface-config": {"globs": [".claude/skills/**", "00-bootstrap/dist/**"], "owns": [], "tree": []},
        "hooks": {"globs": [".claude/hooks/**"], "owns": [], "tree": []},
        "entry-points": {"globs": ["AGENTS.md"], "owns": [], "tree": []},
        "all": {"globs": ["**"], "universal": True, "owns": [], "tree": []},
    }
    sel = select_steps(["README.md"], classes=classes, steps=steps)
    ok(sel["classes"] == ["docs", "all"] and [s for s, _o in sel["steps"]] == ["b.py"], f"docs-only diff: {sel}")
    sel = select_steps(["03-skills/x/SKILL.md"], classes=classes, steps=steps)
    ok(("a.py --check", "skills") in sel["steps"], f"skills diff owns its generator: {sel}")
    sel = select_steps(["09-tools/c.py"], classes=classes, steps=steps)
    ok(("c.py --self-test", "tools") in sel["steps"], f"a changed tool selects its own chain step: {sel}")
    ok(select_steps([".github/workflows/x.yml"], classes=classes, steps=steps)["sensitive"]
       == [".github/workflows/x.yml"], "a workflow edit is SENSITIVE")
    ok(glob_match("**/*.md", "a/b/c.md") and glob_match("**/*.md", "c.md")
       and not glob_match("03-skills/*", "03-skills/a/b"), "glob semantics")
    ok(filter_covers("03-skills/**", "03-skills/**/SKILL.md") and not filter_covers("**/*.md", "07-projects/**"),
       "filter coverage semantics")
    wf = read_workflow("name: x\non:\n  push:\n    branches: [main]\n    paths:\n      - \"03-skills/**\"\n"
                       "      - \"09-tools/**\"\n  schedule:\n    - cron: \"0 6 * * *\"\n  workflow_dispatch:\n"
                       "jobs:\n  g:\n    steps:\n      - run: python3 09-tools/close-out-dispatch.py --from-diff\n")
    ok(wf["push"] == ["03-skills/**", "09-tools/**"] and wf["schedule"] and wf["dispatch"], f"workflow reader: {wf}")
    flow = read_workflow('on:\n  push:\n    paths: ["a/**", "b.md"]\n')
    ok(flow["push"] == ["a/**", "b.md"], f"flow-form paths: {flow['push']}")
    base = dict(classes=classes, steps=steps, workflows={GATE_WORKFLOW: wf, "w2.yml": read_workflow(
        'on:\n  push:\n    paths: ["**/*.md", ".claude/**", "00-bootstrap/**", "AGENTS.md"]\n')},
        tracked=["03-skills/x/SKILL.md", "09-tools/c.py", "AGENTS.md"],
        surface={"hook": [".claude/hooks/d.py"], "instruction": ["AGENTS.md"], "plugin": [".claude/skills/w/SKILL.md"]})
    ok(check_diff_classes(**base) == [], f"a sound fixture passes --check: {check_diff_classes(**base)}")
    gap = dict(base, workflows={GATE_WORKFLOW: wf})
    ok(any("filter gap" in e and ".claude/hooks/**" in e for e in check_diff_classes(**gap)),
       "removing .claude/hooks/** from the filters FAILs --check")
    bad = dict(base, classes=dict(classes, skills=dict(classes["skills"], owns=["a.py --self-test"])))
    ok(any("not in QUALITY_CHAIN" in e for e in check_diff_classes(**bad)), "an invented step FAILs --check")
    plug = dict(base, classes=dict(classes, **{"surface-config": {"globs": ["00-bootstrap/dist/**"], "owns": [],
                                                                   "tree": []}}))
    ok(any("plugin path .claude/skills/w/SKILL.md" in e for e in check_diff_classes(**plug)),
       "a plugin path outside surface-config FAILs --check")
    ok(any("lies in no diff class" in e for e in check_diff_classes(**dict(base, tracked=["zz/unclassed.bin"]))),
       "an unclassed tracked path FAILs --check")
    ok(check_diff_classes(**dict(base, tracked=base["tracked"] + ["07-projects/99-new/README.md"])) == [],
       "a newly tracked project folder is classed (markdown)")
    commits = [
        {"sha": "c1", "parents": ["p1"], "lane": "claude-code/claude/dev-a", "author": "x", "committer": "x"},
        {"sha": "c2", "parents": ["p2"], "lane": "cursor/cursor/dev-a", "author": "x", "committer": "x"},
        {"sha": "c3", "parents": ["p3"], "lane": "codex/codex/dev-b", "author": "x", "committer": "x"},
        {"sha": "c4", "parents": ["p4"], "lane": None, "author": "x", "committer": "x"},
        {"sha": "m1", "parents": ["c1", "c2"], "lane": None, "author": "x", "committer": "x"},
    ]
    receipts = [{"action_class": "gate", "surface": "claude-code", "head": "p1"},
                {"action_class": "gate", "surface": "cursor", "head": "zz"}]
    res = compliance(receipts, commits)
    rows = {r["surface"]: r for r in res["rows"]}
    ok(rows["claude-code"]["gated"] == 1 and rows["cursor"]["gated"] == 0 and rows["codex"]["commits"] == 1
       and rows["codex"]["transcripts"].startswith("SKIP"), f"compliance join: {rows}")
    ok(res["unlaned"] == 1 and unlaned(commits) == 1, "unlaned counts non-merge commits with no trailer")
    ok(parse_lane("a/b") is None and parse_lane("a/b/c") == {"surface": "a", "family": "b", "device": "c"},
       "parse_lane")
    rec = make_receipt({"surface": "cursor", "family": "cursor", "device": "dev-a", "repo_slug": "pat-sample/ws"},
                       via="t", head="h", classes=["docs"], verdict={"result": "pass"}, ts="T")
    ok(sorted(rec) == sorted(["ts", "surface", "family", "via", "device", "repo_slug", "action_class", "credential",
                              "head", "classes", "verdict"]) and rec["credential"] == "none", f"receipt keys: {rec}")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        saved = os.environ.pop("GITHUB_ACTIONS", None)
        try:
            ok(write_receipt(root, rec) is None, "no receipt outside a workspace checkout")
            (root / "AGENTS.md").write_text("x\n", encoding="utf-8")
            ok(write_receipt(root, rec, owner_class="employer") is None, "no receipt for an employer-classed repo")
            p = write_receipt(root, rec)
            ok(p is not None and read_receipts(p) == [rec], "a receipt round-trips")
        finally:
            if saved is not None:
                os.environ["GITHUB_ACTIONS"] = saved
    ok(identity_audit(commits, {"identities": [{"email": "x", "class": "personal"}]})["undeclared_identity"] == 0,
       "identity audit: declared identities are clean")
    print(f"close-out-dispatch self-test: {n[0] - len(fails)}/{n[0]} passed")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
