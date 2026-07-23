#!/usr/bin/env python3
"""
vault-health.py — epistemic-graph hygiene for the knowledge/memory/context layer.

Complements the existing validators (which cover the SKILL graph):
  - validate-links.py     → skills' `## Related` typed graph (foundation/hub/peer/…)
  - validate-integrity.py → structural integrity
This script covers the FRESHNESS + EPISTEMIC-EDGE layer that /health owns:

  1. STALE       — notes tagged `#stale`, or `as of YYYY-MM` dates older than 12 months. [warn]
  2. DANGLING    — `relations:` typed edges (builds-on/refutes/…) pointing at a missing note. [error]
  3. ORPHAN      — knowledge/memory entries with no inbound wikilink (unreachable). [warn]

Scope: 06-context/memory, 08-knowledge, 02-shared-references (the epistemic notes).
Skills are intentionally excluded (validate-links.py owns them). Stdlib-only.

Usage:
  python3 09-tools/vault-health.py            # report; exit 1 on any DANGLING (error)
  python3 09-tools/vault-health.py --strict   # also exit 1 on STALE/ORPHAN warnings
"""
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Where the epistemic notes live. Inbound links are counted across the WHOLE vault,
# but only these dirs are checked FOR being orphans / stale / dangling.
SCOPE = ["06-context/memory", "08-knowledge", "02-shared-references"]
LINK_SOURCES = ["01-frameworks", "02-shared-references", "03-skills", "04-preferences",
                "06-context", "08-knowledge", "AGENTS.md", "CLAUDE.md", "README.md"]
SKIP_PARTS = {"_archive", ".obsidian", "node_modules", "dist", ".git"}

WIKILINK = re.compile(r"\[\[([^\]|#]+?)(?:[#|][^\]]*)?\]\]")
MDLINK = re.compile(r"\[[^\]]*\]\(([^)]+\.md)[^)]*\)")
STALE = re.compile(r"(^|\s)#stale(\s|$)")
ASOF = re.compile(r"as of (\d{4})-(\d{2})", re.IGNORECASE)
STALE_MONTHS = 12
EXEMPT = {"MEMORY.md", "_template.md", "_INDEX.md", "_README.md", "CRITICAL_FACTS.md"}


def md_files(rel_roots):
    for r in rel_roots:
        p = ROOT / r
        if p.is_file() and p.suffix == ".md":
            yield p
        elif p.is_dir():
            for f in p.rglob("*.md"):
                if not any(part in SKIP_PARTS for part in f.relative_to(ROOT).parts):
                    yield f


def relations_targets(text):
    if not text.startswith("---"):
        return []
    end = text.find("\n---", 3)
    if end == -1:
        return []
    m = re.search(r"^relations:\s*(.*?)(?=^\S|\Z)", text[3:end], re.MULTILINE | re.DOTALL)
    return [t.split("/")[-1].lower() for t in WIKILINK.findall(m.group(1))] if m else []


def main():
    strict = "--strict" in sys.argv
    all_notes = list(md_files(LINK_SOURCES))
    by_name = {}
    for p in all_notes:
        by_name.setdefault(p.stem.lower(), []).append(p)

    # inbound wikilink counts across the whole vault
    inbound = {p.resolve(): 0 for p in all_notes}
    for p in all_notes:
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        seen = set()
        # wikilinks resolve by basename (Obsidian shortest-path)
        for name in (t.split("/")[-1].lower() for t in WIKILINK.findall(text)):
            for tgt in by_name.get(name, []):
                if tgt.resolve() != p.resolve():
                    seen.add(tgt.resolve())
        # markdown links resolve by relative path (this vault mixes both styles)
        for href in MDLINK.findall(text):
            if "://" in href:
                continue
            cand = (p.parent / href.split("#")[0]).resolve()
            if cand != p.resolve() and cand.exists():
                seen.add(cand)
        for t in seen:
            if t in inbound:
                inbound[t] += 1

    stale, aging, dangling, orphans = [], [], [], []
    now = datetime.now(timezone.utc)
    scope_files = list(md_files(SCOPE))
    for p in scope_files:
        rel = p.relative_to(ROOT)
        if p.name in EXEMPT or p.stem.startswith("_"):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        if STALE.search(text):
            stale.append(rel)
        m = ASOF.search(text)
        if m:
            y, mo = int(m.group(1)), int(m.group(2))
            months = (now.year - y) * 12 + (now.month - mo)
            if months >= STALE_MONTHS:
                aging.append((rel, f"{y:04d}-{mo:02d}", months))
        for name in relations_targets(text):
            if name not in by_name:
                dangling.append((rel, name))
        if inbound.get(p.resolve(), 0) == 0:
            orphans.append(rel)

    print("vault-health — epistemic graph hygiene (knowledge / memory / shared-refs)\n")
    errors = 0

    if dangling:
        errors += len(dangling)
        print(f"  ✗ {len(dangling)} dangling typed edge(s) — `relations:` points at a missing note:")
        for rel, name in dangling:
            print(f"      · {rel} → [[{name}]]")
    else:
        print("  ✓ no dangling typed edges.")

    if stale:
        print(f"  ⚠ {len(stale)} note(s) tagged #stale — re-check, refute, or archive:")
        for rel in stale:
            print(f"      · {rel}")
    if aging:
        print(f"  ⚠ {len(aging)} aging claim(s) — `as of` older than {STALE_MONTHS}mo:")
        for rel, when, months in aging:
            print(f"      · {rel}  (as of {when}, ~{months}mo)")
    if orphans:
        print(f"  ⚠ {len(orphans)} orphan note(s) — no inbound wikilink (link them or archive):")
        for rel in orphans:
            print(f"      · {rel}")
    if not (stale or aging or orphans):
        print("  ✓ no #stale tags, no aging claims, no orphans in scope.")

    warns = len(stale) + len(aging) + len(orphans)
    print(f"\n{'✓ health clean' if errors == 0 and warns == 0 else 'health report'}: "
          f"{errors} error(s), {warns} warning(s) across {len(scope_files)} scoped note(s).")
    return 1 if errors or (strict and warns) else 0


if __name__ == "__main__":
    sys.exit(main())
