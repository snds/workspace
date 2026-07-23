"""`wsx search` — the discovery layer feeding the Resolver's two-track sourcing.

Two kinds of source (see brain/resolver.md → two-track sourcing):
  * skill-registry — a directory of ready-made skills to PULL / ADAPT. If it exposes a
    machine-readable JSON index, `wsx search` fetches + filters it and prints candidates
    (with a ready-to-paste plan fragment). If not, it points the brain at the homepage.
  * reference — an anchor for *industry-leading reference* (standards, canonical
    guidance). Finding these is the brain's own research (web search/fetch,
    deep-research); this command lists the anchors and says so honestly.

Sources are pluggable: `context/sources.json` overrides the built-in default catalog.
The brain never fetches blindly — it reads provenance + trust here, then decides.
"""
from __future__ import annotations

import json
import urllib.error
from pathlib import Path

from . import core
from .resolver import _fetch, _is_unvetted

# Built-in default catalog. Registries without a stable machine index carry
# index_url=None (browse the homepage); a workspace can override via context/sources.json.
DEFAULT_SOURCES = [
    {"id": "anthropics/skills", "kind": "skill-registry",
     "homepage": "https://github.com/anthropics/skills", "index_url": None,
     "trust": "trusted anchor", "license": "varies (per skill)"},
    {"id": "agentskills.io", "kind": "skill-registry",
     "homepage": "https://agentskills.io", "index_url": None,
     "trust": "trusted anchor", "license": "open Agent Skills standard"},
    {"id": "skills.sh", "kind": "skill-registry",
     "homepage": "https://skills.sh", "index_url": None,
     "trust": "UNVETTED — audit before install", "license": "varies"},
    {"id": "web-references", "kind": "reference",
     "homepage": None, "index_url": None,
     "trust": "varies — you evaluate authority",
     "note": "Industry-leading references are found by your own research (web "
             "search/fetch, or the deep-research skill). Prefer normative standards + "
             "canonical guidance; cite everything on the composite skill."},
]


def _catalog(root: Path) -> list:
    f = root / "context" / "sources.json"
    if f.exists():
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            return data.get("sources", data) if isinstance(data, (dict, list)) else DEFAULT_SOURCES
        except json.JSONDecodeError as ex:
            print(f"  ⚠ context/sources.json is not valid JSON ({ex}); using the built-in catalog.")
    return DEFAULT_SOURCES


def _score(entry: dict, terms: list) -> int:
    hay = " ".join([
        str(entry.get("name", "")),
        str(entry.get("description", "")),
        " ".join(entry.get("tags", []) if isinstance(entry.get("tags"), list) else []),
    ]).lower()
    return sum(1 for t in terms if t in hay)


def _search_registry(src: dict, terms: list) -> list:
    """Fetch + filter a skill-registry's JSON index. Returns scored candidates."""
    idx_url = src.get("index_url")
    if not idx_url:
        return []
    try:
        raw = _fetch(idx_url, base=Path.cwd())
        entries = json.loads(raw)
    except (urllib.error.URLError, OSError, ValueError, json.JSONDecodeError) as ex:
        print(f"  ⚠ {src['id']}: could not read index ({idx_url}) — {ex}")
        return []
    if isinstance(entries, dict):
        entries = entries.get("skills", entries.get("entries", []))
    hits = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        s = _score(e, terms) if terms else 1
        if s > 0:
            hits.append((s, e))
    hits.sort(key=lambda x: (-x[0], str(x[1].get("name", ""))))
    return [e for _, e in hits]


def _plan_fragment(src: dict, e: dict) -> str:
    entry = {
        "name": e.get("name", "TODO"),
        "source": "pulled",
        "registry": src["id"],
        "url": e.get("url", "TODO: skill SKILL.md url"),
        "hub": "TODO: assign",
        "triggers": ["TODO"],
    }
    if _is_unvetted(src["id"]):
        entry["audited"] = False  # brain must audit + flip to true
    return json.dumps(entry, indent=2)


def search(root: Path, query: str, kind: str = "all", source: str | None = None) -> int:
    terms = [t for t in (query or "").lower().split() if t]
    sources = _catalog(root)
    if source:
        sources = [s for s in sources if s.get("id") == source]
        if not sources:
            print(f"no source with id {source!r} in the catalog (see context/sources.json).")
            return 1
    if kind != "all":
        want = "skill-registry" if kind == "skill" else "reference"
        sources = [s for s in sources if s.get("kind") == want]

    print(f'wsx search "{query}"  ·  {len(sources)} source(s)'
          + (f"  ·  kind={kind}" if kind != "all" else "") + "\n")

    total_hits = 0
    for src in sources:
        header = f"── {src['id']}  [{src.get('kind')}]  trust: {src.get('trust', '?')}"
        if _is_unvetted(src["id"]):
            header += "  ⚠"
        print(header)

        if src.get("kind") == "reference":
            if src.get("note"):
                print(f"   {src['note']}")
            if src.get("homepage"):
                print(f"   anchor: {src['homepage']}")
            print()
            continue

        # skill-registry
        hits = _search_registry(src, terms)
        if not src.get("index_url"):
            print(f"   no machine index — browse: {src.get('homepage', '(no homepage)')}")
            print(f"   (audit before pulling)" if _is_unvetted(src["id"]) else "")
            print()
            continue
        if not hits:
            print("   (no matches in this registry's index)\n")
            continue
        total_hits += len(hits)
        for e in hits[:8]:
            desc = str(e.get("description", "")).strip()
            print(f"   • {e.get('name', '?')} — {desc[:70]}")
        if len(hits) > 8:
            print(f"   … and {len(hits) - 8} more")
        # one ready-to-paste plan fragment for the top hit
        print("   plan fragment (top hit — the brain fills hub/triggers, picks pull vs adapt):")
        for line in _plan_fragment(src, hits[0]).splitlines():
            print("     " + line)
        print()

    print("Two-track reminder: pair any skill candidate above with the *reference* track —")
    print("find the industry-leading standard/guidance yourself and add it as references[] on a")
    print("composite skill (brain/resolver.md). The best skill fuses both. Nothing installs until")
    print("you write the approved plan and run `wsx resolve`.")
    return 0
