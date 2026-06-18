#!/usr/bin/env python3
"""
build-registry.py — generate the skill routing/dependency registry from frontmatter.

Single source of truth = the YAML frontmatter on every `03-skills/<name>/SKILL.md`.
This script reads that frontmatter, builds the skill graph (hub/spoke membership +
hard `prerequisites`), validates it (no cycles, no dangling references), precomputes
the ordered load chain for every skill, and writes `03-skills/skills.registry.json`.

It is intentionally:
  - stdlib-only (no PyYAML) — runs on any machine with Python 3, no install step;
  - deterministic — no wall-clock timestamp in the output, so `--check` can detect
    drift in CI by regenerating and diffing;
  - portable — knows nothing about Google Drive, a file-sync bridge, or any one LLM.

Usage:
  python3 09-tools/build-registry.py            # regenerate the registry, print a summary
  python3 09-tools/build-registry.py --check    # CI: fail (exit 1) if the committed
                                                #     registry differs from a fresh build,
                                                #     or if the graph is invalid
  python3 09-tools/build-registry.py --quiet    # only print on error

See 02-shared-references/skill-frontmatter.md for the field spec and
AGENTS.md "Skill loading precedence" for how an agent consumes the registry.
"""

import json
import hashlib
import sys
from pathlib import Path

# ---- locations -------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent
SKILLS_DIR = WORKSPACE_ROOT / "03-skills"
REGISTRY_PATH = SKILLS_DIR / "skills.registry.json"

REGISTRY_VERSION = "1.0"        # shape of skills.registry.json
SPEC_VERSION = "2.0"            # frontmatter contract version

# Load order: smaller rank loads first. Used for deterministic tie-breaking.
TIER_RANK = {"foundation": 0, "hub": 1, "spoke": 2, "cross-cutting": 3, None: 4}

# Frontmatter keys we lift into the registry. `description` is deliberately NOT
# stored here (it's token-heavy and already lives in the SKILL.md, which is the
# zero-cost routing surface in the system prompt).
LIST_KEYS = {"aliases", "triggers", "prerequisites", "related",
             "governed_by", "governs", "surfaces", "requires"}
SCALAR_KEYS = {"name", "hub", "tier", "domain", "spec_version", "pinned_version"}


# ---- minimal frontmatter parser -------------------------------------------
# Handles the constrained grammar the skill template emits: scalar `key: value`,
# inline flow lists `key: [a, b]`, block lists (`key:` then `- item` lines), and
# block scalars (`key: >` / `key: |`, whose body we skip). This is NOT a general
# YAML parser — it only needs to read our own frontmatter reliably.

def _strip_scalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] in "\"'" and v[-1] == v[0]:
        v = v[1:-1]
    return v


def _parse_flow_list(v):
    inner = v.strip()[1:-1].strip()      # drop [ ]
    if not inner:
        return []
    return [_strip_scalar(item) for item in inner.split(",") if item.strip()]


def parse_frontmatter(text):
    """Return a dict of the recognized frontmatter keys for one SKILL.md."""
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    # frontmatter is between the first '---' and the next '---'
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}
    body = lines[1:end]

    data = {}
    i = 0
    while i < len(body):
        line = body[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        # only parse top-level keys (no leading indent)
        if line[0] in " \t":
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, _, rest = line.partition(":")
        key = key.strip()
        rest = rest.strip()

        if rest.startswith("[") and rest.endswith("]"):
            data[key] = _parse_flow_list(rest)
            i += 1
            continue
        if rest in (">", "|", ">-", "|-", "") :
            # block scalar or block list: consume indented continuation lines
            items = []
            j = i + 1
            is_list = False
            while j < len(body) and (not body[j].strip() or body[j][0] in " \t"):
                stripped = body[j].strip()
                if stripped.startswith("- "):
                    is_list = True
                    items.append(_strip_scalar(stripped[2:]))
                j += 1
            if is_list:
                data[key] = items
            # block scalars (e.g. description) are intentionally not stored
            i = j
            continue
        # plain scalar
        data[key] = _strip_scalar(rest)
        i += 1
    return data


def compute_hash(path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


# ---- graph build -----------------------------------------------------------

def read_skills():
    """Map skill-name -> record dict, read from every 03-skills/*/SKILL.md."""
    skills = {}
    for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
        dir_name = skill_md.parent.name
        fm = parse_frontmatter(skill_md.read_text(encoding="utf-8", errors="replace"))
        name = fm.get("name") or dir_name
        rec = {
            "path": f"03-skills/{dir_name}/SKILL.md",
            "tier": fm.get("tier"),
            "domain": fm.get("domain"),
            "hub": fm.get("hub"),
            "prerequisites": fm.get("prerequisites", []),
            "related": fm.get("related", []),
            "governed_by": fm.get("governed_by", []),
            "governs": fm.get("governs", []),
            "triggers": fm.get("triggers", []),
            "surfaces": fm.get("surfaces", ["*"]),
            "requires": fm.get("requires", []),
            "hash": compute_hash(skill_md),
            "dir": dir_name,
        }
        skills[name] = rec
    return skills


def edges_of(name, skills):
    """Hard load-before edges: explicit prerequisites + the implicit spoke->hub edge."""
    rec = skills[name]
    e = list(rec.get("prerequisites") or [])
    hub = rec.get("hub")
    if hub and hub != name and hub not in e:
        e.append(hub)
    return e


def validate(skills):
    """Return (errors, warnings). Errors block; warnings inform."""
    errors, warnings = [], []
    names = set(skills)

    # dangling references
    for name, rec in skills.items():
        for tgt in edges_of(name, skills):
            if tgt not in names:
                errors.append(f"{name}: prerequisite/hub '{tgt}' does not exist")
        for tgt in rec.get("related", []):
            if tgt not in names:
                warnings.append(f"{name}: related '{tgt}' does not exist")
        if rec.get("tier") is None:
            warnings.append(f"{name}: missing `tier` (defaults to unspecified)")

    # cycle detection over the hard-edge graph (DFS coloring)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in names}
    stack_path = []

    def dfs(n):
        color[n] = GRAY
        stack_path.append(n)
        for m in edges_of(n, skills):
            if m not in names:
                continue
            if color[m] == GRAY:
                cyc = stack_path[stack_path.index(m):] + [m]
                errors.append("dependency cycle: " + " -> ".join(cyc))
            elif color[m] == WHITE:
                dfs(m)
        stack_path.pop()
        color[n] = BLACK

    for n in sorted(names):
        if color[n] == WHITE:
            dfs(n)
    return errors, warnings


def load_chain(name, skills):
    """Deterministic, dependency-first ordered list: every ancestor + self.

    Within the ancestor closure, emit a node once all its in-closure prerequisites
    are already emitted, breaking ties by (tier_rank, name) so foundations precede
    hubs precede spokes.
    """
    # closure of ancestors (+ self) via hard edges
    closure, stack = set(), [name]
    while stack:
        n = stack.pop()
        if n in closure or n not in skills:
            continue
        closure.add(n)
        stack.extend(edges_of(n, skills))

    ordered, emitted = [], set()
    while len(ordered) < len(closure):
        ready = [n for n in closure
                 if n not in emitted
                 and all(d in emitted for d in edges_of(n, skills) if d in closure)]
        if not ready:                      # cycle (already reported) — bail safely
            ready = [n for n in closure if n not in emitted]
        ready.sort(key=lambda n: (TIER_RANK.get(skills[n].get("tier"), 4), n))
        pick = ready[0]
        ordered.append(pick)
        emitted.add(pick)
    return ordered


def build():
    skills = read_skills()
    errors, warnings = validate(skills)

    registry = {
        "$schema": "./skills.registry.schema.json",
        "registry_version": REGISTRY_VERSION,
        "spec_version": SPEC_VERSION,
        "generated_from": "frontmatter",
        "tier_rank": {k: v for k, v in TIER_RANK.items() if k is not None},
        "counts": {},
        "skills": {},
        "load_chains": {},
    }

    tier_counts = {}
    for name in sorted(skills):
        rec = skills[name]
        registry["skills"][name] = {
            "path": rec["path"],
            "tier": rec["tier"],
            "domain": rec["domain"],
            "hub": rec["hub"],
            "prerequisites": rec["prerequisites"],
            "related": rec["related"],
            "governed_by": rec["governed_by"],
            "governs": rec["governs"],
            "triggers": rec["triggers"],
            "surfaces": rec["surfaces"],
            "requires": rec["requires"],
            "hash": rec["hash"],
        }
        if not errors:
            registry["load_chains"][name] = load_chain(name, skills)
        tier_counts[rec["tier"] or "unspecified"] = tier_counts.get(rec["tier"] or "unspecified", 0) + 1

    registry["counts"] = {"total": len(skills), "by_tier": dict(sorted(tier_counts.items()))}
    return registry, errors, warnings


def serialize(registry):
    return json.dumps(registry, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def main():
    args = set(sys.argv[1:])
    quiet = "--quiet" in args
    check = "--check" in args

    registry, errors, warnings = build()
    rendered = serialize(registry)

    if errors:
        print("REGISTRY BUILD FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        return 1

    if check:
        existing = REGISTRY_PATH.read_text(encoding="utf-8") if REGISTRY_PATH.exists() else ""
        if existing != rendered:
            print("✗ skills.registry.json is out of date — run: "
                  "python3 09-tools/build-registry.py", file=sys.stderr)
            return 1
        if not quiet:
            print(f"✓ registry up to date — {registry['counts']['total']} skills")
        return 0

    REGISTRY_PATH.write_text(rendered, encoding="utf-8")
    if not quiet:
        c = registry["counts"]
        print(f"✓ wrote {REGISTRY_PATH.relative_to(WORKSPACE_ROOT)} — "
              f"{c['total']} skills {c['by_tier']}")
        if warnings:
            print(f"  ({len(warnings)} warnings — e.g. skills not yet migrated to frontmatter v2)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
