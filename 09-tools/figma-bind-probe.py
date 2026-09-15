#!/usr/bin/env python3
"""A8 — the assess half of the Figma prove-gate, as a detector instead of a good intention.

`03-skills/figma/SKILL.md` step 7 says: capture (MCP inspect + native-zoom screenshot) →
assess (refuse `Color/*`; instances not rects; variant matrix) → correct and re-prove, and
"missing detector → mint it". This is that mint. It judges a capture; it does not take one.

**The split is deliberate.** Capturing needs MCP, which only the agent has. Judging needs
rules, which a script does better than a model grading its own work — same-model critique is
not a detector ([[agentic-error-correction-foundations]]). So:

    agent  →  get_variable_defs / get_metadata  →  capture.json  →  THIS  →  verdict

Run `--emit-template` to get the exact MCP calls and the capture skeleton, so the agent side
is mechanical rather than remembered.

Rules, all from [[figma-ds-surface-authoring]] and the `figma` hub hard gate:

  R1 primitive-binding (FAIL)  A node binding `Color/*` directly. Semantic tokens may RESOLVE
                               through a primitive — that is the correct pattern — but the
                               node must bind the semantic alias, not the primitive.
  R2 raw-value (FAIL)          Zeros and blanks are not exempt: pad/gap 0 -> `space-0`,
                               radius 0 -> `radius-none`, stroke 0 -> `border-width-0`,
                               transparent -> the `transparent` token, never an empty paint.
  R3 rect-not-instance (FAIL)  Chrome drawn as RECTANGLE/ELLIPSE where a component instance
                               belongs.
  R4 density-unaware (WARN)    Controls and their overlays should prefer
                               `control-height/*`, `control-radius/*`, `padding-*`, `gap/*`,
                               `type-size/*` over a Density-unaware Radii/Spacing alias
                               (standing rule, Sean 2026-08-06). A warning, not a failure:
                               general surface radius may legitimately use the Radii ladder.

Sanctioned exceptions exist (SECTION chrome, deliberate negative overlaps) but doctrine says
they are *noted, not silently left* — so `allow` entries require a written reason, and an
allowance without one is itself a failure.

**An empty capture is not a pass.** Nothing to verify exits 2, never 0. That is the whole
difference between a detector and a green tick.

Usage:
  python3 09-tools/figma-bind-probe.py --emit-template
  python3 09-tools/figma-bind-probe.py --capture /tmp/cap.json
  python3 09-tools/figma-bind-probe.py --capture /tmp/cap.json --json
  python3 09-tools/figma-bind-probe.py --self-test

Exit: 0 clean · 1 a rule failed · 2 nothing verifiable (honest skip, never a pass).

Employer note: the Figma account on this machine is Centric. Run the probe against those
files freely — it is read-only — but captures are employer content and must NOT be committed
to this personal workspace. Fixtures here are synthetic for that reason.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from xml.etree import ElementTree

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent

# Primitive namespaces a node must never bind directly. Doctrine names `Color/*`.
PRIMITIVE_NS = ("color/",)
# Density-aware families the standing rule prefers on controls and their overlays.
DENSITY_FAMILIES = ("control-height/", "control-radius/", "control-font-size/",
                    "padding-x/", "padding-y/", "gap/", "type-size/", "popover/")
# Density-unaware ladders — fine on general surfaces, suspect on a control.
GENERIC_LADDERS = ("radius/", "spacing/", "space/", "size/")
CONTROL_HINT = re.compile(
    r"button|input|field|select|combobox|toggle|switch|checkbox|radio|chip|tag|menu|"
    r"popover|tooltip|dropdown|tab|stepper|slider",
    re.I,
)
# Layer types that are chrome when they carry paint, and should be instances.
RAW_SHAPE_TYPES = {"RECTANGLE", "ELLIPSE", "VECTOR", "LINE", "POLYGON", "STAR"}

CAPTURE_TEMPLATE = {
    "system": "<target design system, e.g. CDS>",
    "file_key": "<from the /design/:fileKey/ URL>",
    "node_id": "<e.g. 1:234>",
    "variables": {
        "<name from get_variable_defs>": "<resolved value>",
    },
    "metadata_xml": "<verbatim get_metadata output, or omit>",
    "nodes": [
        {
            "id": "1:235",
            "name": "Button / Primary",
            "type": "INSTANCE",
            "bindings": {"fill": "surface/action/primary", "cornerRadius": "control-radius/sm"},
            "raw": {},
        }
    ],
    "allow": [
        {"pattern": "Section Chrome/*", "reason": "Figma SECTION chrome — sanctioned raw (rule 13)"}
    ],
}

EMIT_HELP = """# Figma bind probe — capture, then judge

1. Inspect the node you just wrote (read-only, no `use_figma` needed):

     get_variable_defs(fileKey=<key>, nodeId=<id>)   -> the name->value map for `variables`
     get_metadata(fileKey=<key>, nodeId=<id>)        -> XML for `metadata_xml`
     get_design_context(...)                         -> per-node bindings for `nodes` (optional
                                                        but this is what makes R2 checkable)

2. Write the capture to your SCRATCHPAD — never into this repo; Figma here is the employer
   account and captures are employer content.

3. python3 09-tools/figma-bind-probe.py --capture <scratchpad>/cap.json

Exit 2 means the capture had nothing to verify. That is not a pass — go back to step 1.

Skeleton:
"""


# ------------------------------------------------------------------------- rules

def _is_primitive(name: str) -> bool:
    return name.lower().startswith(PRIMITIVE_NS)


def _allowed(name: str, allows: list[dict]) -> bool:
    for entry in allows:
        pattern = (entry.get("pattern") or "").rstrip("*")
        if pattern and name.lower().startswith(pattern.lower()):
            return True
    return False


def check_allowlist(capture: dict) -> list[str]:
    """Doctrine: sanctioned exceptions are NOTED, not silently left."""
    fails = []
    for i, entry in enumerate(capture.get("allow") or []):
        if not (entry.get("pattern") or "").strip():
            fails.append(f"R0 allow[{i}]: no pattern")
        if not (entry.get("reason") or "").strip():
            fails.append(
                f"R0 allow[{i}] ('{entry.get('pattern', '?')}'): no reason. A sanctioned "
                f"exception is noted, not silently left."
            )
    return fails


def check_primitives(capture: dict) -> list[str]:
    """R1 — the hard gate. A bound `Color/*` is the violation the whole gate exists for."""
    allows = capture.get("allow") or []
    fails = []
    for name in sorted(capture.get("variables") or {}):
        if _is_primitive(name) and not _allowed(name, allows):
            fails.append(
                f"R1 primitive binding: `{name}` — bind the target system's semantic + "
                f"theme/mode alias instead. Missing? Create the alias, then bind."
            )
    for node in capture.get("nodes") or []:
        for prop, token in (node.get("bindings") or {}).items():
            if _is_primitive(str(token)) and not _allowed(str(token), allows):
                fails.append(
                    f"R1 primitive binding: {node.get('name', node.get('id', '?'))}.{prop} "
                    f"-> `{token}`"
                )
    return fails


def check_raw_values(capture: dict) -> list[str]:
    """R2 — zeros and blanks are not exempt; an unbound value is an unbound value."""
    fails = []
    for node in capture.get("nodes") or []:
        who = node.get("name", node.get("id", "?"))
        for prop, value in (node.get("raw") or {}).items():
            fails.append(
                f"R2 raw value: {who}.{prop} = {value!r} is not bound. Zeros are not exempt "
                f"(pad/gap 0 -> `space-0`, radius 0 -> `radius-none`, stroke 0 -> "
                f"`border-width-0`, transparent -> the `transparent` token)."
            )
    return fails


def check_instances(capture: dict) -> list[str]:
    """R3 — instances, not rects. Painted raw shapes are chrome that should be a component."""
    allows = capture.get("allow") or []
    fails = []
    for node in capture.get("nodes") or []:
        kind = str(node.get("type", "")).upper()
        who = node.get("name", node.get("id", "?"))
        if kind in RAW_SHAPE_TYPES and not _allowed(who, allows):
            painted = bool(node.get("bindings") or node.get("raw"))
            if painted:
                fails.append(
                    f"R3 rect not instance: {who} is a {kind} carrying paint/geometry — "
                    f"build from the real component, not a shape."
                )
    return fails


def check_density(capture: dict) -> list[str]:
    """R4 — warning. Controls should prefer the Density families; surfaces may not need to."""
    warns = []
    for node in capture.get("nodes") or []:
        who = str(node.get("name", node.get("id", "")))
        if not CONTROL_HINT.search(who):
            continue
        for prop, token in (node.get("bindings") or {}).items():
            low = str(token).lower()
            if low.startswith(GENERIC_LADDERS) and not low.startswith(DENSITY_FAMILIES):
                warns.append(
                    f"R4 density-unaware: {who}.{prop} -> `{token}` on a control. Prefer a "
                    f"Density family ({', '.join(DENSITY_FAMILIES[:5])}…) so Compact/Normal/"
                    f"Spacious works without pinning Radii."
                )
    return warns


def nodes_from_metadata(xml_text: str) -> list[dict]:
    """get_metadata returns XML of layer types/names. Enough for R3 when nodes[] is absent."""
    try:
        root = ElementTree.fromstring(xml_text)
    except ElementTree.ParseError:
        return []
    out = []
    for el in root.iter():
        attrs = el.attrib
        kind = (attrs.get("type") or el.tag or "").upper()
        if not kind:
            continue
        out.append({
            "id": attrs.get("id", ""),
            "name": attrs.get("name", ""),
            "type": kind,
            # Metadata carries no binding detail, so R2 cannot run from it. Mark geometry
            # present so R3 can still judge a painted shape.
            "bindings": {},
            "raw": {} if not attrs.get("fill") else {"fill": attrs.get("fill")},
        })
    return out


def evaluate(capture: dict) -> dict:
    """Returns {failures, warnings, verified} — `verified` lists which rules actually ran."""
    cap = dict(capture)
    if not cap.get("nodes") and cap.get("metadata_xml"):
        cap["nodes"] = nodes_from_metadata(cap["metadata_xml"])

    has_vars = bool(cap.get("variables"))
    has_nodes = bool(cap.get("nodes"))
    verified = []
    failures = check_allowlist(cap)

    if has_vars or has_nodes:
        verified.append("R1 primitive-binding")
        failures += check_primitives(cap)
    if has_nodes and any("raw" in n or "bindings" in n for n in cap["nodes"]):
        verified.append("R2 raw-value")
        failures += check_raw_values(cap)
    if has_nodes:
        verified.append("R3 rect-not-instance")
        failures += check_instances(cap)

    warnings = check_density(cap) if has_nodes else []
    return {"failures": failures, "warnings": warnings, "verified": verified,
            "counted": {"variables": len(cap.get("variables") or {}),
                        "nodes": len(cap.get("nodes") or [])}}


# --------------------------------------------------------------------- self-test

def self_test() -> int:
    """Every rule must be able to fail on a planted defect, and pass on a clean capture."""
    failures = []

    def expect(name, cond):
        if not cond:
            failures.append(name)

    clean = {
        "system": "CDS",
        "variables": {"surface/action/primary": "#1d4ed8", "control-radius/sm": "4"},
        "nodes": [{"id": "1:2", "name": "Button / Primary", "type": "INSTANCE",
                   "bindings": {"fill": "surface/action/primary",
                                "cornerRadius": "control-radius/sm"},
                   "raw": {}}],
    }
    res = evaluate(clean)
    expect("clean capture passes", not res["failures"])
    expect("clean capture has no warnings", not res["warnings"])
    expect("clean capture reports which rules ran", len(res["verified"]) == 3)

    prim_var = json.loads(json.dumps(clean))
    prim_var["variables"]["Color/Gray/100"] = "#f5f5f5"
    expect("R1 catches a primitive in the variable map",
           any("R1" in f and "Color/Gray/100" in f for f in evaluate(prim_var)["failures"]))

    prim_bind = json.loads(json.dumps(clean))
    prim_bind["nodes"][0]["bindings"]["stroke"] = "Color/Base/White"
    expect("R1 catches a primitive bound on a node",
           any("R1" in f and "Color/Base/White" in f for f in evaluate(prim_bind)["failures"]))

    raw = json.loads(json.dumps(clean))
    raw["nodes"][0]["raw"] = {"itemSpacing": 0}
    expect("R2 catches a raw zero (zeros are not exempt)",
           any("R2" in f for f in evaluate(raw)["failures"]))

    rect = json.loads(json.dumps(clean))
    rect["nodes"][0]["type"] = "RECTANGLE"
    expect("R3 catches a painted rectangle",
           any("R3" in f for f in evaluate(rect)["failures"]))
    bare = json.loads(json.dumps(rect))
    bare["nodes"][0]["bindings"] = {}
    bare["nodes"][0]["raw"] = {}
    expect("R3 ignores an unpainted shape", not evaluate(bare)["failures"])

    dens = json.loads(json.dumps(clean))
    dens["nodes"][0]["bindings"]["cornerRadius"] = "radius/md"
    dres = evaluate(dens)
    expect("R4 warns on a density-unaware control", dres["warnings"])
    expect("R4 is a warning, not a failure", not dres["failures"])
    surface = json.loads(json.dumps(dens))
    surface["nodes"][0]["name"] = "Card / Elevated"
    expect("R4 leaves a general surface alone", not evaluate(surface)["warnings"])

    allowed = json.loads(json.dumps(prim_var))
    allowed["allow"] = [{"pattern": "Color/Gray/*", "reason": "SECTION chrome, rule 13"}]
    expect("a reasoned allowance suppresses R1", not evaluate(allowed)["failures"])
    unreasoned = json.loads(json.dumps(allowed))
    unreasoned["allow"] = [{"pattern": "Color/Gray/*"}]
    expect("an allowance without a reason is itself a failure",
           any("R0" in f for f in evaluate(unreasoned)["failures"]))

    empty = evaluate({"system": "CDS"})
    expect("an empty capture verifies nothing", not empty["verified"])

    meta = evaluate({"metadata_xml":
                     '<node id="1:2" name="Chrome" type="RECTANGLE" fill="#fff"/>'})
    expect("metadata XML alone still supports R3",
           any("R3" in f for f in meta["failures"]))
    expect("malformed XML degrades to nothing verified",
           not evaluate({"metadata_xml": "<not xml"})["verified"])

    for name in failures:
        print(f"  ✗ {name}")
    if failures:
        print(f"FAIL figma-bind-probe self-test — {len(failures)} assertion(s)")
        return 1
    print("OK figma-bind-probe self-test")
    return 0


# -------------------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--capture", help="path to the capture JSON assembled from MCP output")
    ap.add_argument("--emit-template", action="store_true",
                    help="print the MCP calls and the capture skeleton")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if args.emit_template:
        print(EMIT_HELP)
        print(json.dumps(CAPTURE_TEMPLATE, indent=2))
        return 0
    if not args.capture:
        ap.print_usage()
        print("\nNo capture. Run --emit-template for the MCP calls that produce one.")
        return 2

    path = Path(args.capture)
    if not path.exists():
        print(f"figma-bind-probe: no such capture: {path}", file=sys.stderr)
        return 2
    try:
        capture = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"figma-bind-probe: capture is not valid JSON ({exc})", file=sys.stderr)
        return 2

    result = evaluate(capture)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for f in result["failures"]:
            print(f"  ✗ {f}")
        for w in result["warnings"]:
            print(f"  ⚠ {w}")
        counted = result["counted"]
        ran = ", ".join(result["verified"]) or "nothing"
        print(f"\nverified: {ran}  ({counted['variables']} variable(s), "
              f"{counted['nodes']} node(s))")

    if not result["verified"]:
        print("SKIP figma-bind-probe — the capture had nothing to verify. This is NOT a pass; "
              "re-capture with get_variable_defs / get_metadata.", file=sys.stderr)
        return 2
    if result["failures"]:
        print(f"FAIL figma-bind-probe — {len(result['failures'])} violation(s) of the "
              f"construction gate.")
        return 1
    print(f"OK figma-bind-probe — {len(result['warnings'])} warning(s), no violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
