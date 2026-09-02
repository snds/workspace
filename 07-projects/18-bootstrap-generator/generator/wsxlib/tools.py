"""`09-tools/` — the workspace's own maintenance/validation scripts.

Written verbatim (never through the template renderer) so their regexes and f-strings are
safe. They are thin wrappers over the copied-in `.wsx/wsxlib`, or self-contained stdlib
scripts. All are data-driven off the person's OWN content — no hardcoded routing, no
hardcoded terminology, no identity. Written on `init`, `upgrade`, and `emit all`, so a
workspace always has them; each is created only if missing (never clobbers an edit).
"""
from __future__ import annotations

from pathlib import Path

from . import layout

_BUILD_REGISTRY = r'''#!/usr/bin/env python3
"""Rebuild <skills>/skills.registry.json from every skill's front matter.

Run from anywhere: `python3 09-tools/build-registry.py`. The registry is the machine
index the trigger-router hook reads; a skill routes on the triggers IT declares — there is
no hardcoded routing table. Uses the workspace's own copied-in library (.wsx/)."""
import sys
from pathlib import Path

WS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WS / ".wsx"))
try:
    from wsxlib import registry
except Exception:
    sys.stderr.write("This tool needs the copied-in CLI (.wsx/). Run `python3 wsx.py upgrade` first.\n")
    sys.exit(1)

out = registry.build(WS)
print("wrote", out.relative_to(WS))
'''

_BUILD_RELATED = r'''#!/usr/bin/env python3
"""Weave a generated `## Related` block into each skill from the hub graph.

Run: `python3 09-tools/build-related.py`. Marker-delimited and idempotent — it only ever
rewrites its own block, never your hand-authored body. Uses the copied-in library (.wsx/)."""
import sys
from pathlib import Path

WS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WS / ".wsx"))
try:
    from wsxlib import related
except Exception:
    sys.stderr.write("This tool needs the copied-in CLI (.wsx/). Run `python3 wsx.py upgrade` first.\n")
    sys.exit(1)

sys.exit(related.run(WS))
'''

_VALIDATE = r'''#!/usr/bin/env python3
"""Run the whole validation suite over this workspace, in one command:

  verify  — profile round-trips + every adapter is emit-ready (integrity)
  lint    — skills: no unfilled skeletons, no trigger overlaps
  health  — graph: orphan notes, #stale/aging claims, dangling typed edges (links)

Maps the named validators to the workspace's own commands. Exit non-zero if any fails."""
import subprocess
import sys
from pathlib import Path

WS = Path(__file__).resolve().parents[1]
wsx = WS / "wsx.py"
rc = 0
for cmd in ("verify", "lint", "health"):
    print("\n===== wsx " + cmd + " =====")
    r = subprocess.run([sys.executable, str(wsx), cmd])
    rc = rc or r.returncode
sys.exit(rc)
'''

_CHECK_TERMINOLOGY = r'''#!/usr/bin/env python3
"""Enforce YOUR terminology rules across the vault (optional, opt-in).

Define rules in `02-shared-references/terminology.md`, one per line, like:
    - avoid "foo" -> prefer "bar"    (reason)
This greps the markdown notes for each avoided term and reports every hit. No terms are
baked in — it is a no-op until you write some. Zero dependency; skips generated/dot output."""
import re
import sys
from pathlib import Path

WS = Path(__file__).resolve().parents[1]


def _dir(logical):
    _NUM = {"context": "06-context", "skills": "03-skills", "frameworks": "01-frameworks",
            "knowledge": "08-knowledge", "projects": "07-projects",
            "shared": "02-shared-references"}
    num = _NUM.get(logical, logical)
    if (WS / num).is_dir():
        return num
    if (WS / logical).is_dir():
        return logical
    return num


def _rules():
    f = WS / _dir("shared") / "terminology.md"
    rules = []
    try:
        text = f.read_text(encoding="utf-8")
    except OSError:
        return rules
    for line in text.splitlines():
        m = re.search(r'avoid\s+"([^"]+)"(?:.*?(?:->|prefer)\s*"([^"]+)")?', line, re.IGNORECASE)
        if m:
            rules.append((m.group(1), m.group(2) or ""))
    return rules


def main():
    rules = _rules()
    if not rules:
        print("check-terminology: no rules in " + _dir("shared")
              + "/terminology.md — nothing to check.")
        return 0
    scan = ("context", "skills", "frameworks", "knowledge", "projects", "shared")
    hits = 0
    for key in scan:
        base = WS / _dir(key)
        if not base.is_dir():
            continue
        for p in sorted(base.rglob("*.md")):
            if any(part.startswith(".") for part in p.relative_to(WS).parts):
                continue
            try:
                lines = p.read_text(encoding="utf-8").splitlines()
            except OSError:
                continue
            for i, line in enumerate(lines, 1):
                for term, prefer in rules:
                    if re.search(r"\b" + re.escape(term) + r"\b", line, re.IGNORECASE):
                        sug = ' -> prefer "' + prefer + '"' if prefer else ""
                        print("  " + str(p.relative_to(WS)) + ":" + str(i)
                              + ': "' + term + '"' + sug)
                        hits += 1
    print("\ncheck-terminology: " + str(hits) + " violation(s) across "
          + str(len(rules)) + " rule(s).")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
'''

_SCRIPTS = {
    "build-registry.py": _BUILD_REGISTRY,
    "build-related.py": _BUILD_RELATED,
    "validate.py": _VALIDATE,
    "check-terminology.py": _CHECK_TERMINOLOGY,
}


def write_tools(root: Path) -> list:
    """Write the 09-tools scripts (create-if-missing; never clobber a hand-edit)."""
    tdir = layout.of(root).dir("tools")
    tdir.mkdir(parents=True, exist_ok=True)
    written = []
    for fname, body in _SCRIPTS.items():
        f = tdir / fname
        if f.exists():
            continue
        f.write_text(body, encoding="utf-8")
        f.chmod(0o755)
        written.append(f)
    return written
