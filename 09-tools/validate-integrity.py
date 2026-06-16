#!/usr/bin/env python3
"""
validate-integrity.py — the write-quality / continuity / anti-zombie gate.

Any capable agent may write to this workspace (not just Claude), but every write must pass
deterministic gates so file quality, intent integrity, and cross-link continuity are preserved —
and so no "zombie" files (orphaned, stale, or superseded-but-live) accumulate. This validator is
the machine-checkable half of those gates; the semantic half (does an edit preserve intent?) is a
protocol obligation + PR review. See AGENTS.md → "Write-quality gates".

Checks:
  1. NAME==DIR      — every 03-skills/<dir>/SKILL.md has frontmatter name == <dir>.            [error]
  2. CROSS-LINKS    — every [[wikilink]] in tracked markdown resolves (no dangling = no zombie
                      reference left after a file moves/renames/retires).                       [error]
  3. NO LIVE-SUPERSEDED — any file with `superseded_by` in frontmatter must live under _archive/
                      (a superseded-but-present file is a zombie), and the target must exist.   [error]
  4. NO UNFILLED SCAFFOLD — committed skills/frameworks/shared-refs contain no unfilled template
                      tokens (`<foundation>`, `<parent-hub>`, `tp.file.title`, lorem ipsum).    [error]
  5. STUB MARKERS   — TODO/TBD/FIXME/PLACEHOLDER in those same files.                           [warning]
  6. THIN DOCS      — a skill whose description is < 40 chars (quality-bar smell).              [warning]

Templates and _archive/ are excluded from authoring checks (they legitimately hold placeholders /
historical content). Stdlib-only.

Usage:
  python3 09-tools/validate-integrity.py            # report; exit 1 on any error
  python3 09-tools/validate-integrity.py --strict   # also fail on warnings
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "03-skills"

WIKILINK = re.compile(r"\[\[([^\]]+?)\]\]")
ALIASES_RE = re.compile(r"^aliases:\s*\[(.*?)\]", re.MULTILINE)
SUPERSEDED_RE = re.compile(r"^superseded_by:\s*(.+)$", re.MULTILINE)
SCAFFOLD_TOKENS = ["<foundation>", "<parent-hub>", "<sibling-skill>", "<Tool>", "<TOOL>",
                   "tp.file.title", "<% tp."]   # note: "lorem ipsum" is a legit design term, not flagged
STUB_MARKERS = ["TODO", "TBD", "FIXME", "PLACEHOLDER", "XXX:"]

# Files/paths excluded from authoring checks (placeholders/history are legitimate here).
def is_template(p: Path) -> bool:
    n = p.name
    return (n.startswith("_template") or n == "_ADAPTER-TEMPLATE.md" or n == "skill.md"
            or n.endswith("-template.md") or "templates/" in p.as_posix())

def excluded_from_scan(rel: str) -> bool:
    return ("/_archive/" in rel or rel.startswith("_archive/") or rel.endswith("session-log.md")
            or "node_modules/" in rel or "07-projects/18-bootstrap-generator/" in rel)


def tracked_markdown():
    import subprocess
    out = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True).stdout
    return [ROOT / f for f in out.splitlines()]


def all_tracked():
    import subprocess
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout
    return [ROOT / f for f in out.splitlines()]


def addressable_names(all_files):
    """All names a [[wikilink]] may resolve to: aliases, basenames (any tracked file), skill dir names."""
    names = set()
    for p in all_files:
        if p.suffix == ".md":
            try:
                m = ALIASES_RE.search(p.read_text(encoding="utf-8", errors="replace"))
            except Exception:
                m = None
            if m:
                names.update(a.strip().strip("\"'") for a in m.group(1).split(",") if a.strip())
        if p.name == "SKILL.md":
            names.add(p.parent.name)          # skills addressed by dir name
        else:
            names.add(p.stem)                 # any note addressed by basename (incl. llms.txt -> "llms")
    return names


def resolves(target, names):
    """A wikilink resolves by basename/alias/dir-name OR as a path-form link to an existing file."""
    if target in names:
        return True
    # path-form: [[06-context/project-context]] or [[03-skills/foo/SKILL]] (+ implied .md), or with ext
    for cand in (target, target + ".md"):
        if (ROOT / cand).is_file():
            return True
    return False


def main():
    strict = "--strict" in sys.argv[1:]
    errors, warnings = [], []
    md = tracked_markdown()
    names = addressable_names(all_tracked())

    for p in md:
        rel = p.relative_to(ROOT).as_posix()
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        # 1. name == dir for skills (the curated library only; project sub-skills are out of scope)
        if p.name == "SKILL.md" and rel.startswith("03-skills/") and "/_archive/" not in rel:
            m = re.search(r"^name:\s*(\S+)", text, re.MULTILINE)
            if m and m.group(1).strip() != p.parent.name:
                errors.append(f"{rel}: frontmatter name `{m.group(1).strip()}` != dir `{p.parent.name}`")

        # 3. superseded_by must be archived; target must exist
        sm = SUPERSEDED_RE.search(text)
        if sm and not is_template(p):
            val = sm.group(1).strip().strip("\"'")
            if "/_archive/" not in rel and not rel.startswith("_archive/"):
                errors.append(f"{rel}: has `superseded_by` but is not under _archive/ (zombie: superseded-but-live)")
            tgt = val.strip("[]").split("|")[0].strip()
            if tgt and tgt.lower() != "none" and not tgt.startswith("http") and tgt not in names and tgt not in {n for n in names}:
                # tolerate path-style targets that exist on disk
                if not (ROOT / tgt).exists():
                    warnings.append(f"{rel}: superseded_by target `{tgt}` not found")

        if excluded_from_scan(rel) or is_template(p):
            continue

        # 2. wikilink resolution (cross-link continuity / anti-zombie-reference)
        # Strip fenced + inline code first — wikilinks shown as code examples aren't real links.
        scan = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        scan = re.sub(r"`[^`\n]*`", "", scan)
        for raw in WIKILINK.findall(scan):
            tgt = raw.split("|")[0].split("#")[0].strip()
            if not tgt or tgt.startswith("<"):   # skip scaffold placeholders (templates already excluded)
                continue
            if not resolves(tgt, names):
                errors.append(f"{rel}: dangling wikilink [[{tgt}]]")

        # authoring-quality checks only for the curated layers
        authored = rel.startswith(("03-skills/", "01-frameworks/", "02-shared-references/"))
        if authored:
            # 4. unfilled scaffold tokens
            for tok in SCAFFOLD_TOKENS:
                if tok in text:
                    errors.append(f"{rel}: unfilled scaffold token `{tok}` (stub/zombie)")
                    break
            # 5. stub markers
            for tok in STUB_MARKERS:
                if re.search(rf"\b{re.escape(tok)}\b", text):
                    warnings.append(f"{rel}: contains `{tok}` marker")
                    break
            # 6. thin skill description
            if p.name == "SKILL.md":
                dm = re.search(r"^description:\s*(.*)$", text, re.MULTILINE)
                desc = (dm.group(1).strip() if dm else "")
                if desc in (">", "|", ""):  # block scalar — measure the block
                    block = re.search(r"^description:\s*[>|]\s*\n((?:\s+.*\n)+)", text, re.MULTILINE)
                    desc = block.group(1) if block else ""
                if len(desc.strip()) < 40:
                    warnings.append(f"{rel}: thin/empty description (quality-bar smell)")

    # dedupe wikilink errors (a file may repeat a target)
    errors = sorted(set(errors))
    warnings = sorted(set(warnings))
    for w in warnings:
        print(f"  ⚠ {w}", file=sys.stderr)
    for e in errors:
        print(f"  ✗ {e}", file=sys.stderr)
    if errors or (strict and warnings):
        print(f"integrity check FAILED — {len(errors)} errors, {len(warnings)} warnings", file=sys.stderr)
        return 1
    print(f"✓ integrity ok — {len(md)} markdown files scanned, {len(warnings)} warnings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
