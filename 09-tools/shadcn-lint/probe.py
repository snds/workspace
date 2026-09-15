#!/usr/bin/env python3
"""Token-tier overlay for @shadcn/lint — vault-side matcher, not a vault CI gate.

Detects authoring classes that skip the semantic tier: Radix steps, Tailwind
shade aliases, raw black/white, and CDS compat utilities (`bg-cds-blue-500`).
Those last names are declared in cds `semantic.css` `@theme inline`, so stock
`shadcn/no-raw-colors` false-greens them.

This probe is independent of workspace-harness / validate-integrity.
It *does* refuse a shareable policy that can be adopted without the overlay —
that skip path was the first breaker.

Usage:
  python3 09-tools/shadcn-lint/probe.py --self-test
  python3 09-tools/shadcn-lint/probe.py --classes "bg-primary bg-cds-blue-500"
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC_PATH = HERE / "tier-leakage.json"
POLICY_PATH = HERE / "design-system.lint.json"
CONFIG_PATH = HERE / "eslint.ds.config.mjs"

REQUIRED_SHADCN_RULES = (
    "shadcn/no-restyle",
    "shadcn/no-raw-colors",
    "shadcn/no-arbitrary-values",
    "shadcn/no-inline-styles",
    "shadcn/require-static-classes",
)
MUST_STAY_ON = ("shadcn/no-raw-colors", "ds-lint/no-tier-leakage")
CONFIG_MARKERS = (
    'ds-lint/no-tier-leakage": "error',
    'plugin as shadcn',
    'from "./index.js"',
)
OFF_VALUES = {"off", "0", 0, False}
ERROR_VALUES = {"error", "2", 2}


def load_spec(path: Path = SPEC_PATH) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("prefixes", "hues", "steps", "literal_palette"):
        if not data.get(key):
            raise ValueError(f"{path.name} missing {key}")
    return data


def _alt(values: list[str]) -> str:
    return "|".join(sorted(values, key=len, reverse=True))


def leak_pattern(spec: dict) -> str:
    prefixes = _alt(spec["prefixes"])
    hues = _alt(spec["hues"])
    steps = _alt(spec["steps"])
    literals = _alt(spec["literal_palette"])
    compat = _alt(list(spec.get("compat_prefixes") or ["cds"]))
    families = list(spec["hues"]) + list(spec.get("compat_extra_families") or ["black"])
    compat_hues = _alt(families)
    return (
        rf"^(?:{prefixes})-(?:"
        rf"(?:{hues})A?-(?:{steps})"
        rf"|(?:{literals})"
        rf"|(?:{compat})-(?:{compat_hues})A?-(?:{steps})"
        rf")$"
    )


def compile_leak_re(spec: dict) -> re.Pattern[str]:
    return re.compile(leak_pattern(spec))


def utility_stem(token: str) -> str:
    token = token.strip()
    if not token:
        return ""
    if token.startswith("!"):
        token = token[1:]
    if ":" in token:
        token = token.rsplit(":", 1)[-1]
    if token.startswith("!"):
        token = token[1:]
    if "/" in token:
        token = token.split("/", 1)[0]
    return token


def iter_leaks(class_string: str, spec: dict | None = None) -> list[str]:
    spec = spec if spec is not None else load_spec()
    leak_re = compile_leak_re(spec)
    found: list[str] = []
    for raw in class_string.split():
        stem = utility_stem(raw)
        if stem and leak_re.match(stem):
            found.append(raw)
    return found


def _severity(value):
    """ESLint accepts 'error' or ['error', options]. Never hash a list."""
    if isinstance(value, (list, tuple)) and value:
        value = value[0]
    if isinstance(value, str):
        return value.lower()
    return value


def _rule_is_off(value) -> bool:
    return _severity(value) in OFF_VALUES


def _rule_is_error(value) -> bool:
    return _severity(value) in ERROR_VALUES


def validate_policy(path: Path = POLICY_PATH) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path.name}: invalid JSON ({exc})"]
    rules = data.get("rules")
    if not isinstance(rules, dict):
        return [f"{path.name}: missing rules object"]
    for name in REQUIRED_SHADCN_RULES:
        if name not in rules:
            errors.append(f"{path.name}: missing {name}")
    raw = rules.get("shadcn/no-raw-colors")
    if raw is not None and not _rule_is_error(raw):
        errors.append(
            f"{path.name}: shadcn/no-raw-colors must be error "
            "(warn/off is the declared-@theme false-green)"
        )
    overrides = data.get("overrides")
    if not isinstance(overrides, list) or not overrides:
        errors.append(f"{path.name}: missing component-directory overrides")
        return errors
    for i, ov in enumerate(overrides):
        if not isinstance(ov, dict):
            errors.append(f"{path.name}: override {i} is not an object")
            continue
        ov_rules = ov.get("rules") or {}
        if not isinstance(ov_rules, dict):
            continue
        for name in MUST_STAY_ON:
            if name in ov_rules and not _rule_is_error(ov_rules[name]):
                errors.append(
                    f"{path.name}: override weakens {name} — reopens the "
                    "declared-@theme false-green (bg-cds-blue-500)"
                )
    return errors


def validate_hosts(here: Path = HERE) -> list[str]:
    errors: list[str] = []
    walker = (here / "no-tier-leakage.js").read_text(encoding="utf-8")
    for marker in ('BUILDERS', '"cva"', "walk("):
        if marker not in walker:
            errors.append(f"no-tier-leakage.js: missing {marker} — CDS ternary/cva walker required")
    host_dir = here / "hosts"
    expected = {
        "cds.config.mjs": "@centric/ui",
        "centric-ui.config.mjs": "@centric/ui",
        "proto.config.mjs": "@centric/ui",
    }
    for name, ui in expected.items():
        path = host_dir / name
        if not path.is_file():
            errors.append(f"hosts/{name}: missing")
            continue
        text = path.read_text(encoding="utf-8")
        if "withHost" not in text:
            errors.append(f"hosts/{name}: must call withHost")
        if ui not in text:
            errors.append(f"hosts/{name}: settings.shadcn.ui must be {ui}")
    if not (here / "with-host.js").is_file():
        errors.append("with-host.js: missing")
    if not (here / "ratchet.mjs").is_file():
        errors.append("ratchet.mjs: missing")
    return errors


def validate_config(path: Path = CONFIG_PATH) -> list[str]:
    if not path.is_file():
        return [
            f"{path.name}: missing — lint:ds must load ds-lint/no-tier-leakage "
            "in the same config as @shadcn/lint"
        ]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for marker in CONFIG_MARKERS:
        if marker not in text:
            errors.append(f"{path.name}: missing required marker {marker!r}")
    if re.search(r'["\']ds-lint/no-tier-leakage["\']\s*:\s*["\']off["\']', text):
        errors.append(f"{path.name}: no-tier-leakage is turned off")
    return errors


def self_test() -> list[str]:
    errors = validate_policy()
    errors.extend(validate_config())
    errors.extend(validate_hosts())
    spec = load_spec()
    for cls in spec.get("allowed_examples") or []:
        leaks = iter_leaks(cls, spec)
        if leaks:
            errors.append(f"false positive: {cls!r} leaked {leaks}")
    for cls in spec.get("denied_examples") or []:
        leaks = iter_leaks(cls, spec)
        if not leaks:
            errors.append(f"false negative: {cls!r} was allowed")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--classes", default="")
    args = parser.parse_args(argv)
    if args.self_test:
        errors = self_test()
        if errors:
            print("ds-lint overlay self-test FAIL")
            for err in errors:
                print(f"  {err}")
            return 1
        print("ds-lint overlay self-test OK")
        return 0
    if not args.classes:
        parser.error("pass --self-test or --classes")
    leaks = iter_leaks(args.classes)
    if not leaks:
        print("no tier leaks")
        return 0
    print("tier leaks:")
    for item in leaks:
        print(f"  {item}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
