#!/usr/bin/env python3
"""Named close-out detectors for command hubs. Print the plan; --run executes CLIs.

Exit codes:
  0  runnable CLI detectors passed (SKIP lines may remain — those classes are not verified)
  1  a runnable detector failed
  2  nothing runnable (honest skip only) OR no hub matched
  --check: 0 if every rigor_role=command-hub skill has a table row; else 1

Usage:
  python3 09-tools/close-out-dispatch.py --hub figma
  python3 09-tools/close-out-dispatch.py --from-prompt "build this in figma" --run
  python3 09-tools/close-out-dispatch.py --check
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from dataclasses import dataclass
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


def run_hubs(hubs: list[str]) -> int:
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
    for e in errors:
        print(f"  ✗ {e}", file=sys.stderr)
    if errors:
        return 1
    print(f"OK close-out-dispatch — {len(hubs)} command hubs have named detectors")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Named close-out detectors")
    parser.add_argument("--hub", action="append", default=[])
    parser.add_argument("--from-prompt", default="")
    parser.add_argument("--skills", default="", help="comma-separated skill names")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        return check_table()
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
        return run_hubs(hubs)
    print(format_plan(hubs))
    return 0 if hubs else 2


if __name__ == "__main__":
    raise SystemExit(main())
