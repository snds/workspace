"""`wsx adapter` — bring wsx tooling to a HAND-BUILT vault WITHOUT scaffolding or clobbering.

`examine`'s verdict for a rich foreign vault is: don't `upgrade` — the right path is a thin
adapter that maps its existing folders to the wsx concepts. This is that adapter. It writes a
small MAP (`.wsx/adapter.json`) of the vault's own folders/files → wsx concepts and marks it
`mode: reference`. wsx tools then operate on the person's OWN structure — their home file,
their registry, their conventions — and never add scaffold or edit their content.

It is the safe on-ramp: a vault like Sean's gets wsx capabilities (health, examine, the
profile/preferences interview, wire) while `upgrade`/`init` stay refused. Non-destructive:
it writes only `.wsx/` (the adapter map + a copy of the CLI so the vault is self-driving).
"""
from __future__ import annotations

import json
from pathlib import Path

from . import core, examine, layout, scaffold

ADAPTER_PATH = ".wsx/adapter.json"


def path_of(root: Path) -> Path:
    return root / ADAPTER_PATH


def load(root: Path) -> dict | None:
    f = path_of(root)
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def is_adapted(root: Path) -> bool:
    d = load(root)
    return bool(d and d.get("mode") == "reference")


def _home_file(root: Path) -> str:
    for name in ("HOME.md", "_HOME.md", "index.md", "README.md"):
        if (root / name).exists():
            return name
    return ""


def _registry_file(root: Path) -> str:
    lay = layout.of(root)
    for name in ("skills.registry.json", "skills.registry.wsx.json"):
        if (lay.dir("skills") / name).exists():
            return f"{lay.name('skills')}/{name}"
    return ""


def detect_map(root: Path) -> dict:
    """Map the vault's OWN folders/files to wsx concepts (read-only detection)."""
    concept_dirs = {}
    for concept in examine._CONCEPTS:
        d = examine._find_concept_dir(root, concept)
        if d:
            concept_dirs[concept] = d.name
    return {
        "concepts": concept_dirs,
        "home": _home_file(root),
        "registry": _registry_file(root),
        "ai_files": [f for f in ("AGENTS.md", "CLAUDE.md") if (root / f).exists()],
        "has_profile": core.profile_path(root).exists(),
    }


def create(root: Path, copy_cli: bool = True) -> int:
    if not examine._looks_like_workspace(root):
        raise SystemExit(f"error: {root} doesn't look like a workspace — nothing to adapt. "
                         "(`wsx examine <path>` to inspect, or `wsx init` for a new vault.)")
    m = detect_map(root)
    record = {
        "adapter_version": "1.0",
        "mode": "reference",           # wsx tools READ this vault; never scaffold/clobber it
        "created": core.now_stamp(),
        "root": str(root),
        "map": m,
        "note": ("This vault is hand-built and RICHER than the wsx scaffold. wsx operates in "
                 "reference mode: it uses the folders/files mapped above and never adds scaffold "
                 "or edits your content. `wsx upgrade`/`init` stay refused here by design."),
    }
    out = path_of(root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    copied = scaffold.copy_cli(root) if copy_cli else []

    print(f"wsx adapter — mapped your vault to the wsx concepts (reference mode)\n")
    print(f"  wrote {ADAPTER_PATH}  ·  {'copied the CLI into .wsx/ (self-driving)' if copied else ''}\n")
    print("  Concept map:")
    for concept in examine._CONCEPTS:
        got = m["concepts"].get(concept)
        print(f"    {concept:12} → {got + '/' if got else '(none — wsx will just skip it)'}")
    print(f"    {'home':12} → {m['home'] or '(none)'}")
    print(f"    {'registry':12} → {m['registry'] or '(none)'}")
    print(f"    {'ai wiring':12} → {', '.join(m['ai_files']) or '(none)'}")
    if not m["has_profile"]:
        print("\n  No profile yet. Build one from your existing context (voice/tone included):")
        print("    wsx profile init          # seed a profile + preferences, then refine")
    print("\n  Now safe to run on this vault: wsx examine · wsx health · wsx wire · wsx profile.")
    print("  wsx will NOT scaffold or edit your content while the adapter is in reference mode.")
    return 0


def run(root: Path) -> int:
    existing = load(root)
    if existing:
        print(f"wsx adapter — this vault is already adapted ({existing.get('mode')} mode).\n")
        m = existing.get("map", {})
        for concept in examine._CONCEPTS:
            got = m.get("concepts", {}).get(concept)
            print(f"    {concept:12} → {got + '/' if got else '(none)'}")
        print(f"\n  Re-map with:  wsx adapter --refresh")
        return 0
    return create(root)
