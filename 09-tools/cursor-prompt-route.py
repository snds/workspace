#!/usr/bin/env python3
"""Cursor beforeSubmitPrompt CLI.

Reads the event JSON from stdin, matches against the portable workspace routing
maps, prints {"additional_context": "..."} or {}. Fail-open.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow `python3 09-tools/cursor-prompt-route.py` and hook-installed copies.
_TOOLS = Path(__file__).resolve().parent
if str(_TOOLS) not in sys.path:
    sys.path.insert(0, str(_TOOLS))

import prompt_route  # noqa: E402


def _prompt_from_payload(payload: dict) -> str:
    prompt = (
        payload.get("prompt")
        or payload.get("content")
        or payload.get("text")
        or payload.get("message")
        or ""
    )
    if isinstance(prompt, dict):
        prompt = prompt.get("text") or prompt.get("content") or prompt.get("prompt") or ""
    return str(prompt)


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        print("{}")
        return 0
    if not isinstance(payload, dict):
        print("{}")
        return 0
    brain = prompt_route.resolve_brain_root()
    if brain is None:
        print("{}")
        return 0
    text = prompt_route.route_prompt(_prompt_from_payload(payload), brain)
    if not text:
        print("{}")
        return 0
    print(json.dumps({"additional_context": text}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
