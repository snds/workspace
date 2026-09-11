#!/usr/bin/env python3
"""Refuse malformed Layer 0 JSON. Malformed files currently fail-open to {}.

Stdlib-only. Schemas live under 02-shared-references/schemas/.

Usage:
  python3 09-tools/validate-layer0-schema.py
  python3 09-tools/validate-layer0-schema.py --check
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
SCHEMAS = ROOT / "02-shared-references" / "schemas"
TRIGGER_ROUTES = ROOT / "02-shared-references" / "trigger-routes.json"
KNOWLEDGE_HINTS = ROOT / "02-shared-references" / "knowledge-hints.json"
ROUTING_CASES = ROOT / "02-shared-references" / "skill-routing-cases.jsonl"


def _expect_object(value, path: str, errors: list[str]) -> dict | None:
    if not isinstance(value, dict):
        errors.append(f"{path}: expected object")
        return None
    return value


def _expect_string(value, path: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}: expected non-empty string")


def _string_map(value, path: str, errors: list[str], required: bool = True) -> None:
    obj = _expect_object(value, path, errors)
    if obj is None:
        return
    if required and not obj:
        errors.append(f"{path}: expected at least one key")
        return
    for key, val in obj.items():
        if not isinstance(key, str) or not key.strip():
            errors.append(f"{path}: empty key")
            continue
        _expect_string(val, f"{path}.{key}", errors)


def check_trigger_routes(data, label: str, errors: list[str]) -> None:
    obj = _expect_object(data, label, errors)
    if obj is None:
        return
    for key in ("spec_version", "templates", "routes"):
        if key not in obj:
            errors.append(f"{label}: missing {key}")
    if "spec_version" in obj:
        _expect_string(obj.get("spec_version"), f"{label}.spec_version", errors)
    if "templates" in obj:
        _string_map(obj.get("templates"), f"{label}.templates", errors, required=True)
    if "routes" in obj:
        _string_map(obj.get("routes"), f"{label}.routes", errors, required=True)


def check_knowledge_hints(data, label: str, errors: list[str]) -> None:
    obj = _expect_object(data, label, errors)
    if obj is None:
        return
    for key in ("spec_version", "hints"):
        if key not in obj:
            errors.append(f"{label}: missing {key}")
    if "spec_version" in obj:
        _expect_string(obj.get("spec_version"), f"{label}.spec_version", errors)
    if "hints" in obj:
        _string_map(obj.get("hints"), f"{label}.hints", errors, required=True)


def check_routing_case(row, label: str, errors: list[str]) -> None:
    obj = _expect_object(row, label, errors)
    if obj is None:
        return
    for key in ("id", "utterance"):
        if key not in obj:
            errors.append(f"{label}: missing {key}")
        else:
            _expect_string(obj.get(key), f"{label}.{key}", errors)
    for key in ("expect_skills", "expect_routes", "expect_knowledge", "forbid_skills", "forbid_routes"):
        if key in obj and not isinstance(obj[key], list):
            errors.append(f"{label}.{key}: expected array")


def load_json(path: Path, errors: list[str]):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"{path.as_posix()}: {e}")
        return None


def check_files(
    trigger_routes: Path | None = None,
    knowledge_hints: Path | None = None,
    routing_cases: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    tr = load_json(trigger_routes or TRIGGER_ROUTES, errors)
    if tr is not None:
        check_trigger_routes(tr, (trigger_routes or TRIGGER_ROUTES).as_posix(), errors)
    kh = load_json(knowledge_hints or KNOWLEDGE_HINTS, errors)
    if kh is not None:
        check_knowledge_hints(kh, (knowledge_hints or KNOWLEDGE_HINTS).as_posix(), errors)
    cases_path = routing_cases or ROUTING_CASES
    try:
        text = cases_path.read_text(encoding="utf-8")
    except OSError as e:
        errors.append(f"{cases_path.as_posix()}: {e}")
        return errors
    n = 0
    for i, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as e:
            errors.append(f"{cases_path.as_posix()}:{i}: {e}")
            continue
        n += 1
        check_routing_case(row, f"{cases_path.as_posix()}:{i}", errors)
    if n == 0:
        errors.append(f"{cases_path.as_posix()}: empty corpus")
    return errors


def check_schema_files_exist() -> list[str]:
    errors: list[str] = []
    for name in (
        "trigger-routes.schema.json",
        "knowledge-hints.schema.json",
        "skill-routing-cases.schema.json",
    ):
        path = SCHEMAS / name
        if not path.is_file():
            errors.append(f"missing schema {path.as_posix()}")
            continue
        try:
            spec = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"{path.as_posix()}: {e}")
            continue
        if not isinstance(spec, dict) or spec.get("type") != "object":
            errors.append(f"{path.as_posix()}: schema must be a JSON object type")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Layer 0 JSON shape check")
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    errors = check_schema_files_exist()
    errors.extend(check_files())
    for e in errors:
        print(f"  ✗ {e}", file=sys.stderr)
    if errors:
        print(f"layer0 schema FAILED — {len(errors)} errors", file=sys.stderr)
        return 1
    print("OK validate-layer0-schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
