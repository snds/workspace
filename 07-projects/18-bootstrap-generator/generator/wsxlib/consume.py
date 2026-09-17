"""`wsx consume <path>` — speak a never-wsx vault's dialect (Wave 7).

Not init. Not upgrade. Not a second numbered taxonomy. The detector is a digest
on disk; an LLM "I understood your ontology" without that file is not a consume.

Writes only under the target vault's `.wsx/`:
  adapter.json       folder → concept map, mode: reference (exceeds/partial)
  dialect.json       skill path, graph vocab, dest guesses, layout kind
  consume-digest.md  bounded readout the LLM is allowed to load
  consume-prompt.md  one-shot brief generated FROM the digest
  outcome.json       Wave 6 shape snapshot (names, not bodies)

Never reads personal.md. Never copies notes into the generator. Secret-scans
the digest. Thin notes dumps are offered migrate-up, not consume-as-peer.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import __version__, adapter, core, dest, examine, secretscan

SAMPLE_SKILLS = 8
DEST_HINTS = ("artifacts", "canvases", "docs", "briefs", "inbox")
_SKIP_NAMES = frozenset({"personal.md", ".ds_store", "readme.md"})
_REL_KEYS = re.compile(r"^[\s-]*([A-Za-z][\w-]*)\s*:", re.MULTILINE)


def _is_generator(root: Path) -> bool:
    return (root / "generator" / "wsxlib").is_dir() and (root / "SPEC.md").exists()


def _heading(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8").splitlines()[:40]:
            s = line.strip()
            if s.startswith("#"):
                return s.lstrip("#").strip()[:80]
    except (OSError, UnicodeDecodeError):
        return ""
    return ""


def _skill_pattern(skills_dir: Path) -> str:
    if not skills_dir.is_dir():
        return "SKILL.md"
    skill_md = 0
    loose = 0
    try:
        for p in skills_dir.rglob("*.md"):
            if p.name.lower() in _SKIP_NAMES or p.name.startswith("_"):
                continue
            if p.name.lower() == "skill.md":
                skill_md += 1
            elif p.parent == skills_dir:
                loose += 1
    except OSError:
        return "SKILL.md"
    if skill_md >= loose:
        return "SKILL.md"
    return "*.md"


def _sample_skills(skills_dir: Path, pattern: str) -> list:
    rows = []
    if not skills_dir.is_dir():
        return rows
    paths = []
    try:
        if pattern == "SKILL.md":
            paths = sorted(p for p in skills_dir.rglob("SKILL.md") if p.is_file())
        else:
            paths = sorted(p for p in skills_dir.glob("*.md")
                           if p.is_file() and not p.name.startswith("_")
                           and p.name.lower() not in _SKIP_NAMES)
    except OSError:
        return rows
    for p in paths[:SAMPLE_SKILLS]:
        if p.name.lower() == "personal.md":
            continue
        fm, _body = core.parse_frontmatter(p)
        name = p.parent.name if p.name.lower() == "skill.md" else p.stem
        rel = p.name
        try:
            rel = str(p.relative_to(skills_dir.parent if skills_dir.parent.is_dir() else skills_dir))
        except ValueError:
            rel = p.name
        rows.append({
            "name": str(fm.get("name") or name),
            "triggers": core.skill_triggers(fm),
            "kind": str(fm.get("kind") or ""),
            "path": rel,
        })
    return rows


def _graph_vocab(root: Path, samples: list, skills_dir: Path) -> list:
    keys = set()
    related = False
    files = []
    if skills_dir.is_dir():
        try:
            files = list(skills_dir.rglob("*.md"))[:20]
        except OSError:
            files = []
    for p in files:
        if p.name.lower() == "personal.md":
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if re.search(r"^## Related\b", text, re.MULTILINE):
            related = True
        if "relations:" in text[:800]:
            block = text.split("relations:", 1)[-1][:600]
            for m in _REL_KEYS.finditer(block):
                k = m.group(1)
                if k.lower() not in {"name", "title", "tags", "created", "updated", "status"}:
                    keys.add(k)
    vocab = sorted(keys) or (["builds-on", "relates-to"] if samples else [])
    if related:
        vocab.append("## Related")
    return vocab


def _dest_guesses(root: Path, scope: str) -> list:
    found = []
    try:
        kids = list(root.iterdir())
    except OSError:
        kids = []
    for d in kids:
        if not d.is_dir() or d.name.startswith("."):
            continue
        low = d.name.lower()
        if low in DEST_HINTS or any(h in low for h in DEST_HINTS):
            found.append({"name": low[:24], "path": d.name,
                          "scope": scope, "wall": "vault"})
    if not found:
        found.append({"name": "vault", "path": ".", "scope": scope, "wall": "vault"})
    return found[:6]


def _layout_kind(root: Path, concepts: dict) -> str:
    names = [n for n in concepts.values() if n]
    if not names:
        return "other"
    if all(re.match(r"^\d{2}-", n) for n in names):
        return "numbered"
    flat = {"context", "skills", "frameworks", "projects", "knowledge", "preferences", "adapters"}
    if all(n in flat for n in names):
        return "flat"
    return "other"


def _home(root: Path) -> str:
    return adapter._home_file(root)


def _write_scanned(path: Path, text: str) -> None:
    if secretscan.blocked(secretscan.scan_text(text)):
        raise SystemExit("error: secret scan hit — consume digest/prompt not written")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _digest_md(root: Path, snap: dict, dialect: dict, samples: list) -> str:
    present = snap.get("present") or {}
    lines = [
        f"# Consume digest — {root.name}",
        "",
        "_Generated by `wsx consume`. Bounded readout. Do not crawl the tree._",
        f"_wsx {__version__} · verdict: **{dialect.get('verdict')}**_",
        "",
        f"- Path: `{root}`",
        f"- Layout: {dialect.get('layout')} · skill files: `{dialect.get('skill_file')}`",
        f"- Home: {dialect.get('home') or '(none)'}",
        f"- Coverage: {snap.get('coverage')} · {snap.get('total_md')} markdown files",
        f"- Git: {'yes' if snap.get('git') else 'no'} · Obsidian: {'yes' if snap.get('obsidian') else 'no'}",
        "",
        "## Concepts (this vault's names)",
        "",
    ]
    for concept in examine._CONCEPTS:
        if concept in present:
            p = present[concept]
            lines.append(f"- **{concept}** → `{p['dir']}/` ({p['md_files']} md)")
        else:
            lines.append(f"- **{concept}** → (not detected)")
    lines += ["", "## Top-level dirs", ""]
    try:
        tops = sorted(d.name for d in root.iterdir()
                      if d.is_dir() and not d.name.startswith("."))[:24]
    except OSError:
        tops = []
    lines.append(", ".join(f"`{t}`" for t in tops) or "(none)")
    home = dialect.get("home")
    if home:
        title = _heading(root / home)
        lines += ["", "## Home title", "", title or home]
    lines += ["", "## Skill sample (names + triggers, not bodies)", ""]
    if samples:
        for s in samples:
            trg = ", ".join(s.get("triggers") or []) or "(none)"
            kind = f" [{s['kind']}]" if s.get("kind") else ""
            lines.append(f"- `{s['name']}`{kind} — {trg}")
        if dialect.get("skill_count_more"):
            lines.append(f"- …and {dialect['skill_count_more']} more (not listed)")
    else:
        lines.append("_(no skill files sampled)_")
    lines += ["", "## Graph vocab", "",
              ", ".join(f"`{v}`" for v in (dialect.get("graph_vocab") or [])) or "(none detected)",
              "", "## Dest guesses", ""]
    for g in dialect.get("dest_guesses") or []:
        lines.append(f"- `{g.get('name')}` → `{g.get('path')}` (scope={g.get('scope')}, wall={g.get('wall')})")
    if not dialect.get("dest_guesses"):
        lines.append("_(none)_")
    lines += [
        "",
        "## What wsx will NOT do",
        "",
        "- `init` / `upgrade` / `restructure` on this tree",
        "- impose a numbered `00–09` taxonomy",
        "- rewrite AGENTS.md / CLAUDE.md / HOME",
        "- ingest `personal.md` or copy notes into the generator",
        "",
    ]
    return "\n".join(lines) + "\n"


def _prompt_md(root: Path, dialect: dict, digest_rel: str) -> str:
    verdict = dialect.get("verdict")
    skip = ", ".join(dialect.get("skip_movements") or []) or "(none — ask dests, altitude, what to add)"
    if verdict == "thin":
        intent = (
            "This looks thinner than a wsx workspace. Offer **migrate-up**: "
            "`wsx init` a new workspace and bring this content in via ingest/adopt. "
            "Do not treat this folder as a peer to consume-and-extend."
        )
    elif verdict == "exceeds":
        intent = (
            "This vault meets or exceeds the wsx model. Dialect mode only. "
            "Never migrate-down. Ask one intent question: add / improve / change / just map it."
        )
    else:
        intent = (
            "Partial coverage. Dialect + optional additive folders **they** accept. "
            "Ask one intent question: add / improve / change / just map it."
        )
    concepts = dialect.get("concepts") or {}
    cmap = ", ".join(f"{k}=`{v}`" for k, v in concepts.items()) or "(none)"
    return "\n".join([
        f"# Consume brief — {root.name}",
        "",
        "_Generated FROM `.wsx/consume-digest.md`. Replayable. Do not freestyle a tree crawl._",
        "",
        "## This vault's dialect (quoted, not invented)",
        "",
        f"- Layout: `{dialect.get('layout')}` · skill files: `{dialect.get('skill_file')}`",
        f"- Address skills by: `{dialect.get('skill_address')}`",
        f"- Home: `{dialect.get('home') or '(none)'}`",
        f"- Concepts: {cmap}",
        f"- Graph vocab: {', '.join(dialect.get('graph_vocab') or []) or '(none)'}",
        f"- Dest default: `{dialect.get('dest_default') or '(none)'}`",
        f"- Verdict: **{verdict}**",
        "",
        f"Read `{digest_rel}` before asking anything. If you need a hub, load that hub's",
        "cluster — not the whole tree.",
        "",
        "## Rules",
        "",
        "- Do **not** impose the wsx numbered layout.",
        "- Do **not** rewrite their AGENTS.md / CLAUDE.md / HOME.",
        "- Additive writes go through `wsx` (`skill add`, `dest add`, harvest) in",
        "  **reference mode** — their files stay theirs.",
        f"- Skip-list (already in evidence): {skip}",
        "",
        "## Your first (and only opening) question",
        "",
        intent,
        "",
        "Then only the pertinent movements: dests, expertise altitude, what to add.",
        "A consume is the `notes` persona seed — they already have a vault.",
        "",
    ]) + "\n"


def consume(path: str, scope: str = "personal") -> int:
    root = Path(path).expanduser().resolve()
    if not root.is_dir():
        raise SystemExit(f"error: {root} is not a directory")
    if _is_generator(root):
        raise SystemExit("error: that folder is the generator, not a vault. Point consume at THEIR notes.")
    if not examine._looks_like_workspace(root):
        raise SystemExit(
            f"error: {root} doesn't look like a workspace (Obsidian, AGENTS.md tree, or concept dirs).\n"
            "       `wsx examine` for a readout, or `wsx init` for a new vault.")
    if scope not in dest.SCOPES:
        raise SystemExit(f"error: --scope must be one of {', '.join(dest.SCOPES)}")

    snap = examine.foreign_snapshot(root)
    concepts = {k: v["dir"] for k, v in (snap.get("present") or {}).items()}
    skills_dir = root / concepts["skills"] if "skills" in concepts else Path()
    pattern = _skill_pattern(skills_dir) if skills_dir else "SKILL.md"
    samples = _sample_skills(skills_dir, pattern) if skills_dir else []
    more = 0
    if skills_dir.is_dir():
        try:
            n = sum(1 for _ in (skills_dir.rglob("SKILL.md") if pattern == "SKILL.md"
                                else skills_dir.glob("*.md")))
            more = max(0, n - len(samples))
        except OSError:
            more = 0
    guesses = _dest_guesses(root, scope)
    home = _home(root)
    verdict = snap["verdict"]
    skip = []
    if snap.get("ai_wired"):
        skip.append("M0-surfaces")
    dialect = {
        "wsx_version": __version__,
        "verdict": verdict,
        "layout": _layout_kind(root, concepts),
        "skill_file": pattern,
        "skill_address": "parent-dir" if pattern == "SKILL.md" else "stem",
        "home": home,
        "concepts": concepts,
        "graph_vocab": _graph_vocab(root, samples, skills_dir) if skills_dir else [],
        "dest_guesses": guesses,
        "dest_default": guesses[0]["name"] if guesses else "",
        "skip_movements": skip,
        "persona_seed": "notes",
        "scope": scope,
        "skill_count_more": more,
    }

    wsx = root / ".wsx"
    wsx.mkdir(parents=True, exist_ok=True)
    digest = _digest_md(root, snap, dialect, samples)
    prompt = _prompt_md(root, dialect, ".wsx/consume-digest.md")
    _write_scanned(wsx / "consume-digest.md", digest)
    _write_scanned(wsx / "consume-prompt.md", prompt)
    (wsx / "dialect.json").write_text(json.dumps(dialect, indent=2) + "\n", encoding="utf-8")

    if verdict == "thin":
        print(f"wsx consume — {root}")
        print(f"  verdict: thin notes dump → migrate-up, not consume-as-peer")
        print("  wrote .wsx/consume-digest.md + consume-prompt.md + dialect.json")
        print("  did NOT enable reference mode (would pretend this is a peer vault).")
        print("  next: read `.wsx/consume-prompt.md`; offer `wsx init` + ingest/adopt.")
        return 0

    # exceeds / partial: reference mode + CLI + outcome/index
    adapter.create(root, copy_cli=True, quiet=True)
    from . import interview as _iv
    _iv.try_refresh(root)

    print(f"wsx consume — {root}")
    print(f"  verdict: {verdict}  ·  layout: {dialect['layout']}  ·  skills: {pattern}")
    print("  wrote .wsx/{adapter.json, dialect.json, consume-digest.md, consume-prompt.md, outcome.json}")
    print("  reference mode: init/upgrade/restructure stay refused.")
    print("  next: load `.wsx/consume-prompt.md` (generated from the digest). Do not crawl the tree.")
    return 0
