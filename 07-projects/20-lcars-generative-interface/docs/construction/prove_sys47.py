#!/usr/bin/env python3
"""SUPERSEDED tombstone.

This file was the per-project S-SYS47-01 prove script. It declared `pass: True`
on cues the engine later measured as fail (silhouette chip at 0.0 foreground).
The original body is in git history before 2026-09-03.

Workspace path (any project):
  python3 03-skills/visual-prove-engine/vqa.py capture URL -o BUILD.png --assistance off
  python3 03-skills/visual-prove-engine/vqa.py prove BUILD.png CUESPEC.json

See 08-knowledge/design/agent-output-rails.md and 03-skills/visual-prove-engine/SKILL.md.
"""
from __future__ import annotations

import sys

sys.exit(
    "prove_sys47.py is retired. Use vqa capture + vqa prove "
    "(03-skills/visual-prove-engine/vqa.py)."
)
