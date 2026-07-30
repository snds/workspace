#!/usr/bin/env python3
"""
linear-lanes.py — Open Agent Engine lane preflight (deterministic half).

Checks that THIS machine has the lanes it is supposed to have, on the surface you
are actually using, and that no lane exists here that shouldn't. Filesystem and
config inspection only: no network, no credentials read, no tokens printed.

    python3 00-bootstrap/doctor/linear-lanes.py              # human report
    python3 00-bootstrap/doctor/linear-lanes.py --check      # exit 1 on drift
    python3 00-bootstrap/doctor/linear-lanes.py --json       # machine-readable
    python3 00-bootstrap/doctor/linear-lanes.py --notice     # one line, empty if healthy
    python3 00-bootstrap/doctor/linear-lanes.py --surface cursor

WHAT THIS CANNOT DO — and why stage 2 exists.
A file-based check proves a connection is *registered* and *authenticated*. It cannot
prove WHICH Linear workspace is behind that connection: a `linear-c8` server that
OAuth'd into the personal workspace looks perfectly healthy here. That check requires
a live call and belongs to the agent — see 03-skills/open-agent-engine/SKILL.md
→ "Preflight". Never report a lane as verified on the strength of this script alone.

Canonical expectations live in the fenced json block of 06-context/open-engine/README.md.
"""

from __future__ import annotations

import argparse
import json
import re
import socket
import sys
from pathlib import Path

LANE_INDEX_REL = "06-context/open-engine/README.md"

# surface id -> (config path, dotted path to the server map)
SURFACES = {
    "claude-code": (Path.home() / ".claude.json", ("mcpServers",)),
    "cursor": (Path.home() / ".cursor" / "mcp.json", ("mcpServers",)),
}


def workspace_root() -> Path:
    """Nearest ancestor containing AGENTS.md — the contract's own rule."""
    for d in [Path(__file__).resolve(), *Path(__file__).resolve().parents]:
        if (d / "AGENTS.md").is_file():
            return d
    raise SystemExit("FATAL: workspace root (nearest ancestor with AGENTS.md) not found")


def load_manifest(root: Path) -> dict:
    p = root / LANE_INDEX_REL
    if not p.is_file():
        raise SystemExit(f"FATAL: lane index missing at {LANE_INDEX_REL}")
    m = re.search(r"```json\s*\n(.*?)\n```", p.read_text(encoding="utf-8"), re.DOTALL)
    if not m:
        raise SystemExit(f"FATAL: no canonical json block in {LANE_INDEX_REL}")
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError as e:
        raise SystemExit(f"FATAL: lane manifest is not valid JSON — {e}")


def resolve_machine(machines: dict, override: str | None = None) -> tuple[str | None, list[str]]:
    host = override or socket.gethostname()
    for cand in (host, host.removesuffix(".local")):
        if cand in machines:
            return cand, machines[cand]
    lowered = {k.lower(): k for k in machines}
    for cand in (host.lower(), host.lower().removesuffix(".local")):
        if cand in lowered:
            key = lowered[cand]
            return key, machines[key]
    return None, []


def registered_servers(surface: str) -> set[str]:
    """Server names registered for a surface. Never reads values — names only."""
    path, keypath = SURFACES[surface]
    if not path.is_file():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return set()
    node = data
    for k in keypath:
        node = node.get(k, {}) if isinstance(node, dict) else {}
    return set(node) if isinstance(node, dict) else set()


def auth_state(auth_dir: str) -> str:
    """'authed' | 'incomplete' | 'none'. Filenames only — token contents are never read.

    mcp-remote nests its store under <dir>/mcp-remote-<version>/, so this recurses. A lone
    *_code_verifier.txt with no *_tokens.json means an OAuth flow was started and abandoned —
    that state looks finished to a human and must not be reported as authenticated.
    """
    d = Path(auth_dir).expanduser()
    if not d.is_dir():
        return "none"
    if any(d.rglob("*_tokens.json")):
        return "authed"
    if any(d.rglob("*_code_verifier.txt")):
        return "incomplete"
    return "none"


def authed(auth_dir: str) -> bool:
    return auth_state(auth_dir) == "authed"


def inspect(root: Path, manifest: dict, surfaces: list[str], as_machine: str | None = None) -> dict:
    lanes = manifest.get("lanes", {})
    machine, expected = resolve_machine(manifest.get("machines", {}), as_machine)
    reg = {s: registered_servers(s) for s in surfaces}

    findings, results = [], {}
    for lane in expected:
        spec = lanes.get(lane)
        if not spec:
            findings.append(f"lane `{lane}` expected on this machine but absent from the manifest")
            continue
        cfg = root / spec["config"]
        server = spec["mcp_server"]
        where = [s for s in surfaces if server in reg[s]]
        state = {
            "config_present": cfg.is_file(),
            # Match the backticked FIELD form only. A bare "PENDING" also appears in prose
            # (status banners, the runner's own refuse-while-PENDING rule), and matching that
            # reported a fully-provisioned lane as not-provisioned — observed on c8, 2026-07-29.
            "provisioned": cfg.is_file() and "`PENDING`" not in cfg.read_text(encoding="utf-8"),
            "registered_on": where,
            "auth": auth_state(spec["auth_dir"]),
        }
        if not state["config_present"]:
            state["status"] = "config-missing"
        elif not where:
            state["status"] = "not-registered"
        elif state["auth"] == "incomplete":
            state["status"] = "auth-incomplete"
        elif state["auth"] != "authed":
            state["status"] = "not-authed"
        elif not state["provisioned"]:
            state["status"] = "not-provisioned"
        else:
            state["status"] = "ok"
        results[lane] = state

    # A lane present here that this machine should not have is the dangerous direction.
    for lane, spec in lanes.items():
        if lane in expected:
            continue
        where = [s for s in surfaces if spec["mcp_server"] in reg[s]]
        if where or authed(spec["auth_dir"]):
            results[lane] = {"status": "unexpected", "registered_on": where,
                             "authed": authed(spec["auth_dir"])}
            findings.append(
                f"lane `{lane}` is present on this machine but not expected here "
                f"({'registered on ' + ', '.join(where) if where else 'auth context exists'})"
            )

    return {"machine": machine, "hostname": socket.gethostname(), "expected": expected,
            "surfaces": surfaces, "lanes": results, "findings": findings}


REMEDY = {
    "config-missing": "lane config not on this machine — recreate it (machine-local lanes are per-machine by design)",
    "not-registered": "MCP not registered — add the server for this surface",
    "not-authed": "registered but no auth context — complete the OAuth flow",
    "auth-incomplete": "OAuth was STARTED BUT NOT FINISHED (verifier present, no token) — redo the flow",
    "not-provisioned": "connected, but the config still has PENDING fields — finish provisioning the board",
    "unexpected": "PRESENT BUT NOT EXPECTED HERE — remove it or declare it in the manifest",
}
DRIFTY = set(REMEDY) - {"ok"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="exit 1 on drift")
    ap.add_argument("--json", action="store_true", dest="as_json")
    ap.add_argument("--notice", action="store_true", help="one line for the session-start hook; silent if healthy")
    ap.add_argument("--surface", choices=sorted(SURFACES), action="append",
                    help="limit to a surface (repeatable; default: all known)")
    ap.add_argument("--as-machine", metavar="HOSTNAME",
                    help="evaluate another machine's expectations against THIS machine's state "
                         "(planning another device, or proving the detector fires)")
    args = ap.parse_args()

    root = workspace_root()
    report = inspect(root, load_manifest(root), args.surface or sorted(SURFACES), args.as_machine)
    drift = [l for l, s in report["lanes"].items() if s["status"] in DRIFTY]
    unknown_machine = report["machine"] is None

    if args.as_json:
        print(json.dumps(report, indent=2))
    elif args.notice:
        if unknown_machine:
            print(f"Open Engine: machine `{report['hostname']}` is not declared in "
                  f"{LANE_INDEX_REL} — add it so lane expectations are a declared fact, not a guess.")
        elif drift:
            bits = ", ".join(f"{l} ({report['lanes'][l]['status']})" for l in drift)
            print(f"Open Engine lanes need attention on {report['machine']}: {bits}. "
                  f"Run `python3 00-bootstrap/doctor/linear-lanes.py` or ask me to fix it.")
    else:
        print(f"Open Agent Engine — lane preflight")
        print(f"  machine   : {report['machine'] or '(UNDECLARED) ' + report['hostname']}")
        print(f"  surfaces  : {', '.join(report['surfaces'])}")
        print(f"  expected  : {', '.join(report['expected']) or '(none)'}\n")
        if unknown_machine:
            print(f"  ✗ hostname `{report['hostname']}` not in the manifest — add it to {LANE_INDEX_REL}\n")
        for lane, s in sorted(report["lanes"].items()):
            mark = "✓" if s["status"] == "ok" else "✗"
            print(f"  {mark} {lane:<10} {s['status']}")
            if s["status"] != "ok":
                print(f"       → {REMEDY[s['status']]}")
            if s.get("registered_on"):
                print(f"       registered on: {', '.join(s['registered_on'])}")
        print("\n  Stage 2 (agent, not this script): confirm each connection actually points at the")
        print("  INTENDED workspace. Registration and auth cannot prove workspace identity.")

    if args.check:
        return 1 if (drift or unknown_machine) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
