#!/usr/bin/env python3
"""Compute AGENTS.md load_set without ingesting the skill registry.

Usage:
  python3 09-tools/skill-loadset.py "dark-mode palette for this dashboard"
  python3 09-tools/skill-loadset.py --json "…"
  python3 09-tools/skill-loadset.py --self-test
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import prompt_route  # noqa: E402

ROOT = TOOLS.parent
REGISTRY = ROOT / "03-skills" / "skills.registry.json"


def _load_registry(path: Path | None = None) -> dict:
    target = path or REGISTRY
    return json.loads(target.read_text(encoding="utf-8"))


def matched_skill_names(prompt: str, data: dict) -> list[str]:
    lowered = (prompt or "").lower()
    names: list[str] = []
    for name, rec in (data.get("skills") or {}).items():
        for term in prompt_route._trigger_terms(rec.get("triggers")):
            if prompt_route.term_matches(str(term), lowered):
                names.append(name)
                break
    return names


def load_set(prompt: str, data: dict | None = None) -> dict:
    """AGENTS.md load_set(message, registry) as data."""
    data = data or _load_registry()
    skills = data.get("skills") or {}
    chains = data.get("load_chains") or {}
    matched = matched_skill_names(prompt, data)
    ordered: list[str] = []
    seen: set[str] = set()
    for name in matched:
        for step in chains.get(name) or [name]:
            if step in seen:
                continue
            seen.add(step)
            ordered.append(step)
    suggestions: list[str] = []
    sug_seen: set[str] = set()
    lenses: list[str] = []
    lens_seen: set[str] = set()
    for name in ordered:
        rec = skills.get(name) or {}
        for rel in rec.get("related") or []:
            if rel in seen or rel in sug_seen:
                continue
            sug_seen.add(rel)
            suggestions.append(rel)
        for lens in rec.get("governed_by") or []:
            if lens in lens_seen:
                continue
            lens_seen.add(lens)
            lenses.append(lens)
    paths = [
        f"03-skills/{name}/SKILL.md"
        for name in ordered
        if (ROOT / "03-skills" / name / "SKILL.md").is_file()
        or name in skills
    ]
    return {
        "matched": matched,
        "load": ordered,
        "paths": paths,
        "suggest": suggestions,
        "lenses": lenses,
        "close_out": (
            "python3 09-tools/close-out-dispatch.py --from-prompt "
            + json.dumps(prompt)
            + " --run"
        ),
    }


def format_text(result: dict) -> str:
    lines = [
        "# skill-loadset",
        "",
        "matched: " + (", ".join(result["matched"]) or "(none)"),
        "load:",
    ]
    if result["paths"]:
        lines.extend(f"  {p}" for p in result["paths"])
    else:
        lines.append("  (none — try python3 09-tools/vault-retrieve.py \"…\")")
    lines.append("suggest: " + (", ".join(result["suggest"]) or "(none)"))
    lines.append("lenses (after produce): " + (", ".join(result["lenses"]) or "(none)"))
    lines.append("close_out: " + result["close_out"])
    lines.append("")
    lines.append(
        "Read the load paths foundation-first. Do not ingest skills.registry.json. "
        "After producing, run close_out — exit 0 is not verified for SKIP classes."
    )
    return "\n".join(lines)


def self_test() -> int:
    data = _load_registry()
    result = load_set("dark-mode palette for this dashboard", data)
    if "uid-color-for-ui" not in result["matched"] and "uid-color-for-ui" not in result["load"]:
        print("self-test FAIL: expected uid-color-for-ui in load set", file=sys.stderr)
        print(json.dumps(result, indent=2), file=sys.stderr)
        return 1
    if "design-foundations" not in result["load"]:
        print("self-test FAIL: expected design-foundations first in chain", file=sys.stderr)
        return 1
    print("OK skill-loadset self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="AGENTS.md load_set as a CLI")
    parser.add_argument("prompt", nargs="?", default="")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if not (args.prompt or "").strip():
        parser.print_help()
        return 2
    result = load_set(args.prompt)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))
    return 0 if result["load"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
