"""Minimal, zero-dependency YAML I/O for the constrained profile.yaml subset.

Why not PyYAML: the generator must run identically on any machine without
installing anything (the user README promises "no Node, no extra installs").
So we implement exactly the slice of YAML the profile schema needs and nothing
more — one code path, fully under our control, easy to verify.

Supported:
  - nested mappings via 2-space indentation        key:\\n  child: v
  - scalar values: str / int / float / bool / null  (null = ~ or empty-after-mapping)
  - inline flow lists of scalars                     key: [a, b, c]   (and [])
  - full-line comments (# ...) and blank lines are ignored

NOT supported (keep profile.yaml within the subset): block lists (- item),
lists of mappings, anchors/aliases, multi-line/folded strings. `wsx verify`
round-trips the profile to catch any drift out of the subset.
"""
from __future__ import annotations

import re

_INT = re.compile(r"-?\d+$")
_FLOAT = re.compile(r"-?\d+\.\d+$")


def _parse_scalar(s: str):
    s = s.strip()
    if s == "" or s == "~" or s.lower() == "null":
        return None
    if len(s) >= 2 and s[0] == s[-1] and s[0] in ("'", '"'):
        return s[1:-1]
    low = s.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if _INT.match(s):
        return int(s)
    if _FLOAT.match(s):
        return float(s)
    return s


def _parse_flow_list(s: str):
    inner = s.strip()
    inner = inner[1:-1].strip()  # drop [ ]
    if not inner:
        return []
    return [_parse_scalar(p) for p in inner.split(",")]


def loads(text: str) -> dict:
    """Parse the supported YAML subset into nested dicts/lists/scalars."""
    root: dict = {}
    stack = [(-1, root)]  # (indent, container)
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        line = raw.strip()
        if ":" not in line:
            continue  # malformed / unsupported — skip rather than crash
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if val == "":
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
        elif val.startswith("["):
            parent[key] = _parse_flow_list(val)
        else:
            parent[key] = _parse_scalar(val)
    return root


def _dump_scalar(v) -> str:
    if v is None:
        return "~"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, (int, float)):
        return str(v)
    s = str(v)
    if s == "" or s.strip() != s or any(c in s for c in (":", "#", "[", "]", ",", '"', "'")):
        return '"' + s.replace('"', "'") + '"'
    return s


def dumps(obj: dict, _indent: int = 0) -> str:
    """Serialize nested dicts/lists/scalars back into the supported subset."""
    lines = []
    pad = " " * _indent
    for k, v in obj.items():
        if isinstance(v, dict):
            lines.append(f"{pad}{k}:")
            if v:
                lines.append(dumps(v, _indent + 2))
        elif isinstance(v, list):
            inner = ", ".join(_dump_scalar(x) for x in v)
            lines.append(f"{pad}{k}: [{inner}]")
        else:
            lines.append(f"{pad}{k}: {_dump_scalar(v)}")
    return "\n".join(lines)
