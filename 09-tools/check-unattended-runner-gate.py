#!/usr/bin/env python3
"""Hard gate for Open Engine unattended / scheduled runners (harness-map rec #6).

Unattended runs that hold Bash/Edit/Write while reading untrusted issue bodies are a
prompt-injection path. Prose in the skill is not enforcement — this script is.

Usage:
  # Default: silent OK when not claiming unattended mode
  python3 09-tools/check-unattended-runner-gate.py

  # Claimed unattended run (cron / headless): must pass or exit 1
  UNATTENDED_RUNNER=1 \\
  OPEN_ENGINE_TOOLS='mcp__linear-personal' \\
  OPEN_ENGINE_DISALLOWED_TOOLS='Bash,Edit,Write,Agent,CronCreate' \\
  OPEN_ENGINE_STRICT_MCP=1 \\
    python3 09-tools/check-unattended-runner-gate.py --require

Exit codes: 0 = safe to proceed (or not unattended); 1 = blocked; 2 = usage error.

Required when UNATTENDED_RUNNER=1 (or --require):
  - OPEN_ENGINE_TOOLS           non-empty allowlist passed to the runner's --tools
  - OPEN_ENGINE_DISALLOWED_TOOLS must include Bash, Edit, Write, Agent, CronCreate
  - OPEN_ENGINE_STRICT_MCP=1    lane-scoped MCP only (--strict-mcp-config)
"""
from __future__ import annotations

import argparse
import os
import sys

REQUIRED_DENY = ("Bash", "Edit", "Write", "Agent", "CronCreate")


def _split_tools(raw: str) -> set[str]:
    return {p.strip() for p in raw.replace(";", ",").split(",") if p.strip()}


def check(require: bool) -> int:
    unattended = os.environ.get("UNATTENDED_RUNNER", "").strip() in ("1", "true", "yes")
    if not unattended and not require:
        print("ok — not an unattended runner (gate idle)")
        return 0

    errors: list[str] = []
    tools = os.environ.get("OPEN_ENGINE_TOOLS", "").strip()
    denied_raw = os.environ.get("OPEN_ENGINE_DISALLOWED_TOOLS", "").strip()
    strict = os.environ.get("OPEN_ENGINE_STRICT_MCP", "").strip() in ("1", "true", "yes")

    if not tools:
        errors.append("OPEN_ENGINE_TOOLS is empty — set the runner --tools allowlist")
    if not denied_raw:
        errors.append(
            "OPEN_ENGINE_DISALLOWED_TOOLS is empty — deny Bash,Edit,Write,Agent,CronCreate"
        )
    else:
        denied = _split_tools(denied_raw)
        missing = [t for t in REQUIRED_DENY if t not in denied]
        if missing:
            errors.append(
                "OPEN_ENGINE_DISALLOWED_TOOLS missing required denies: "
                + ", ".join(missing)
            )
    if not strict:
        errors.append(
            "OPEN_ENGINE_STRICT_MCP must be 1 (lane-scoped --strict-mcp-config)"
        )

    if errors:
        print("BLOCKED — unattended runner hard gate failed:", file=sys.stderr)
        for e in errors:
            print(f"  • {e}", file=sys.stderr)
        print(
            "See 03-skills/open-agent-engine/SKILL.md → Unattended runner hard gate.",
            file=sys.stderr,
        )
        return 1

    print("ok — unattended runner hard gate passed")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--require",
        action="store_true",
        help="Fail unless env proves a scoped unattended launch (even if UNATTENDED_RUNNER unset)",
    )
    args = p.parse_args()
    return check(require=args.require)


if __name__ == "__main__":
    sys.exit(main())
