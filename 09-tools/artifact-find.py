#!/usr/bin/env python3
"""C2 — query the artifact registry instead of ingesting it.

`06-context/artifact-registry.md` is a structural index of known files. The contract used
to tell every agent to READ it at session start, which costs ~6.9k tokens — the largest
recurring item in the session floor after AGENTS.md itself, and more than the whole Cursor
adapter, role, preferences, project-context head and session-log head combined.

An index is for looking things up. This is the same fix already applied twice:
`skills.registry.json` → `skill-loadset.py`, and `08-knowledge/_INDEX.md` → knowledge-hints
plus the router parsing the index server-side. The agent never reads the index; a CLI does.

  artifact-find.py "lcars"        what the registry knows about a subject   (~200 tok)
  artifact-find.py --list         every group and entry name, nothing else  (~700 tok)
  artifact-find.py --path 07-projects/19    everything under a path
  artifact-find.py --check        CI: the file is still parseable and complete

`--check` matters as much as the query. A retrieval layer is only as good as the structure
it reads, so the same tool that queries the file polices its shape: drift the format and
queries start silently missing rather than loudly failing.

Usage:
  python3 09-tools/artifact-find.py "session state"
  python3 09-tools/artifact-find.py --list
  python3 09-tools/artifact-find.py --path 05-artifacts --json
  python3 09-tools/artifact-find.py --check
  python3 09-tools/artifact-find.py --self-test

Exit: 0 ok (or query ran) · 1 --check failed · 2 registry missing.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
REGISTRY = ROOT / "06-context" / "artifact-registry.md"

GROUP_RE = re.compile(r"^## (.+)$", re.M)
ENTRY_RE = re.compile(r"^### (.+)$", re.M)
FIELD_RE = re.compile(r"^- \*\*([\w /]+)\*\*:\s*(.*?)(?=^- \*\*|\Z)", re.M | re.S)
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
# A group heading is "Label — path/one/ + path/two/ (note)". Keep the paths.
PATH_IN_HEADING = re.compile(r"(\d{2}-[\w./~-]+|~/\.[\w./-]+)")


def parse(text: str) -> list[dict]:
    """Registry markdown -> records. Tolerant of extra fields; strict about the shape."""
    records: list[dict] = []
    group, group_paths = "", []
    # Walk headings in order so each entry inherits the group above it.
    for match in re.finditer(r"^(##|###) (.+)$", text, re.M):
        level, title = match.group(1), match.group(2).strip()
        if level == "##":
            group = title
            group_paths = PATH_IN_HEADING.findall(title)
            continue
        end = text.find("\n## ", match.end())
        nxt = text.find("\n### ", match.end())
        stop = min(x for x in (end, nxt, len(text)) if x != -1)
        body = text[match.end():stop]
        fields = {k.strip(): " ".join(v.split()) for k, v in FIELD_RE.findall(body)}
        records.append({
            "name": title,
            "group": group,
            "paths": group_paths + PATH_IN_HEADING.findall(title),
            "purpose": fields.get("Purpose", ""),
            "last_modified": fields.get("Last modified", ""),
            "date": (DATE_RE.search(fields.get("Last modified", "")) or [None])
                    and (DATE_RE.search(fields.get("Last modified", "")).group(1)
                         if DATE_RE.search(fields.get("Last modified", "")) else ""),
            "fields": fields,
        })
    return records


def load(path: Path | None = None) -> list[dict]:
    target = path or REGISTRY
    if not target.exists():
        return []
    return parse(target.read_text(encoding="utf-8", errors="replace"))


def search(records: list[dict], terms: list[str]) -> list[dict]:
    """Score by where the term lands: a name hit beats a group hit beats prose."""
    lowered = [t.lower() for t in terms if t.strip()]
    if not lowered:
        return []
    scored = []
    for rec in records:
        hay = {
            "name": rec["name"].lower(),
            "group": rec["group"].lower(),
            "paths": " ".join(rec["paths"]).lower(),
            "purpose": rec["purpose"].lower(),
        }
        score = 0
        for term in lowered:
            score += 6 * hay["name"].count(term)
            score += 4 * hay["paths"].count(term)
            score += 3 * hay["group"].count(term)
            score += 1 * hay["purpose"].count(term)
        if score:
            scored.append((score, rec))
    scored.sort(key=lambda pair: (-pair[0], pair[1]["name"]))
    return [rec for _score, rec in scored]


def by_path(records: list[dict], needle: str) -> list[dict]:
    low = needle.lower()
    return [r for r in records
            if any(low in p.lower() for p in r["paths"]) or low in r["name"].lower()]


def check(records: list[dict]) -> list[str]:
    """Keep the file queryable. Drift here makes queries miss silently, not loudly."""
    errors = []
    if not records:
        return ["artifact registry has no parseable entries — the retrieval layer is blind"]
    seen: dict[str, int] = {}
    for rec in records:
        where = f"### {rec['name']}"
        if not rec["purpose"]:
            errors.append(f"{where}: no **Purpose** — nothing for a query to match on")
        if not rec["last_modified"]:
            errors.append(f"{where}: no **Last modified** — staleness is unknowable")
        elif not rec["date"]:
            errors.append(f"{where}: **Last modified** has no YYYY-MM-DD date")
        if not rec["group"]:
            errors.append(f"{where}: sits above the first `## ` group heading")
        seen[rec["name"]] = seen.get(rec["name"], 0) + 1
    errors += [f"### {name}: appears {n} times — a query cannot disambiguate them"
               for name, n in seen.items() if n > 1]
    return errors


# ------------------------------------------------------------------------- output

def fmt(rec: dict, width: int = 150) -> str:
    purpose = rec["purpose"]
    if len(purpose) > width:
        purpose = purpose[: width - 1] + "…"
    head = f"### {rec['name']}"
    meta = f"    group: {rec['group']}"
    if rec["date"]:
        meta += f"  ·  last modified {rec['date']}"
    return f"{head}\n{meta}\n    {purpose}"


def self_test() -> int:
    """Prove parsing, scoring and the shape check all behave — and can fail."""
    failures = []

    def expect(name, cond):
        if not cond:
            failures.append(name)

    sample = (
        "# Artifact Registry\n\n"
        "## Legion — 07-projects/13-legion/ (git-tracked)\n\n"
        "### 13-legion/ (README + SESSION-STATE)\n"
        "- **Purpose**: the game project home.\n"
        "- **Last modified**: 2026-06-14 — codebase extracted.\n\n"
        "### legion-notes.md — 05-artifacts/active/\n"
        "- **Purpose**: scratch notes about shaders.\n"
        "- **Size**: ~10 KB\n"
        "- **Last modified**: 2026-05-01 — created.\n\n"
        "## Brain — 07-projects/19-workspace-brain/\n\n"
        "### 19-workspace-brain/ (reports)\n"
        "- **Purpose**: workspace-subject sessions.\n"
        "- **Last modified**: 2026-09-02 — session-end.\n"
    )
    recs = parse(sample)
    expect("parses every entry", len(recs) == 3)
    expect("entry inherits its group", recs[0]["group"].startswith("Legion"))
    expect("later group is picked up", recs[2]["group"].startswith("Brain"))
    expect("extracts the date", recs[0]["date"] == "2026-06-14")
    expect("captures a non-required field", recs[1]["fields"].get("Size") == "~10 KB")
    expect("group path is attached", any("07-projects/13-legion" in p for p in recs[0]["paths"]))

    hits = search(recs, ["legion"])
    expect("search finds both legion entries", len(hits) == 2)
    expect("name/path hit outranks a prose-only hit", hits[0]["name"].startswith("13-legion"))
    expect("search on prose works", search(recs, ["shaders"])[0]["name"].startswith("legion-notes"))
    expect("no match returns nothing", search(recs, ["zzzznope"]) == [])
    expect("empty query returns nothing", search(recs, []) == [])

    expect("path filter narrows", len(by_path(recs, "19-workspace-brain")) == 1)

    expect("clean sample passes check", not check(recs))
    broken = parse(sample.replace("- **Purpose**: the game project home.\n", ""))
    expect("missing Purpose fails check", any("Purpose" in e for e in check(broken)))
    undated = parse(sample.replace("2026-06-14 — codebase extracted.", "recently"))
    expect("undated Last modified fails check", any("YYYY-MM-DD" in e for e in check(undated)))
    expect("empty registry fails check", check([]))
    dupe = parse(sample + "\n### 13-legion/ (README + SESSION-STATE)\n"
                          "- **Purpose**: duplicate.\n- **Last modified**: 2026-01-01 — x.\n")
    expect("duplicate entry name fails check", any("appears 2 times" in e for e in check(dupe)))

    for name in failures:
        print(f"  ✗ {name}")
    if failures:
        print(f"FAIL artifact-find self-test — {len(failures)} assertion(s)")
        return 1
    print("OK artifact-find self-test")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("terms", nargs="*", help="what to look for")
    ap.add_argument("--list", action="store_true", help="every group and entry name, nothing else")
    ap.add_argument("--path", help="entries under a path fragment")
    ap.add_argument("--limit", type=int, default=6, help="max hits (default 6)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true", help="CI: registry parseable and complete")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if not REGISTRY.exists():
        print(f"artifact-find: {REGISTRY.relative_to(ROOT)} not found", file=sys.stderr)
        return 2
    records = load()

    if args.check:
        errors = check(records)
        for e in errors:
            print(f"  ✗ {e}")
        if errors:
            print(f"artifact registry FAILED — {len(errors)} structural defect(s); "
                  f"queries would miss silently")
            return 1
        print(f"✓ artifact registry ok — {len(records)} entries parseable, "
              f"every one has a purpose and a date")
        return 0

    if args.list:
        if args.json:
            print(json.dumps([{"group": r["group"], "name": r["name"]} for r in records], indent=2))
            return 0
        group = None
        for rec in records:
            if rec["group"] != group:
                group = rec["group"]
                print(f"\n## {group}")
            print(f"  - {rec['name']}")
        print(f"\n{len(records)} entries. Query one: "
              f"python3 09-tools/artifact-find.py \"<terms>\"")
        return 0

    hits = by_path(records, args.path) if args.path else search(records, args.terms)
    if not args.path and not args.terms:
        ap.print_usage()
        print("\nGive terms, --path, --list or --check. Do not read the registry whole: "
              "it is ~6.9k tokens and this tool is why you no longer have to.")
        return 0

    shown = hits[: args.limit]
    if args.json:
        print(json.dumps(shown, indent=2))
        return 0
    if not shown:
        print(f"no registry entry matches {args.path or ' '.join(args.terms)!r}. "
              f"The registry indexes known artifacts, not everything — "
              f"try `python3 09-tools/vault-retrieve.py` for content.")
        return 0
    for rec in shown:
        print(fmt(rec))
        print()
    if len(hits) > len(shown):
        print(f"({len(hits) - len(shown)} more — raise --limit)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
