#!/usr/bin/env python3
"""Shared Layer-0 prompt routing for Claude dispatcher and Cursor beforeSubmitPrompt.

Reads curated trigger-routes, knowledge-hints, the skill registry, and
08-knowledge/_INDEX.md from the portable workspace (brain) checkout — never from
the current project cwd. That is the employer-repo pathing fix: cds/centric-ui
sessions still get workspace doctrine.

Fail-open: missing files or parse errors yield no hits. Work verbs with zero
hits inject a visible miss (not silence). Produce language also injects
close-out then self-improve so those skills are not hope after a hub body.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import NamedTuple

TIER_CAPS = {
    "curated trigger": 8,
    "knowledge hint": 4,
    "registry trigger": 6,
    "index trigger": 4,
    "lexical fallback": 2,
}

# Layer 1 runs only when Layer 0 under-fires, so triggers stay primary and a thin
# prompt still reaches the vault. This lived only in the Claude hook until
# 2026-09-15, which is why Cursor silently returned less on the same utterance.
LEXICAL_FALLBACK_MIN = 2
LEXICAL_FALLBACK_LIMIT = 2

_HINT_TARGET_RE = re.compile(r"\d{2}-[\w./-]+\.md")


@dataclass
class RouteResult:
    lines: list[str] = field(default_factory=list)
    seen: set[str] = field(default_factory=set)
    unique_count: int = 0
    any_layer0: bool = False


def resolve_brain_root(project: Path | None = None) -> Path | None:
    """Locate the portable workspace checkout (AGENTS.md + trigger-routes.json)."""
    candidates: list[Path] = []
    if project is not None:
        candidates.append(project)
    try:
        pointer = Path.home() / ".claude" / "workspace-brain-path"
        text = pointer.read_text(encoding="utf-8").strip().splitlines()
        if text:
            candidates.append(Path(text[0].strip()))
    except OSError:
        pass
    home = Path.home()
    candidates += [
        home / "Projects" / "Workspace",
        home / "Projects" / "workspace",
        home / "projects" / "workspace",
    ]
    seen: set[str] = set()
    for c in candidates:
        if not c:
            continue
        try:
            key = str(c.resolve())
        except OSError:
            key = str(c)
        if key in seen:
            continue
        seen.add(key)
        if (c / "AGENTS.md").is_file() and (
            c / "02-shared-references" / "trigger-routes.json"
        ).is_file():
            return c
    return None


def term_matches(term: str, prompt: str) -> bool:
    """Word-boundary match; prompt must already be lowercased.

    Skip 1-character terms (`a`, `i`) — they fire inside ordinary English and steal
    registry slots from the skills that actually matched.
    """
    t = term.lower().strip()
    if len(t) < 2:
        return False
    return re.search(r"(?<!\w)" + re.escape(t) + r"(?!\w)", prompt) is not None


def hint_target_key(hint: str) -> str:
    m = _HINT_TARGET_RE.search(hint)
    return m.group(0) if m else hint


def _expand_hint(hint: str, templates: dict[str, str]) -> str:
    if isinstance(hint, str) and hint.startswith("$") and hint[1:] in templates:
        return templates[hint[1:]]
    return hint


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _curated_hits(prompt: str, brain: Path) -> list[tuple[str, str]]:
    data = _load_json(brain / "02-shared-references" / "trigger-routes.json")
    templates = data.get("templates") or {}
    routes = data.get("routes") or {}
    hits: list[tuple[str, str]] = []
    for trigger, hint in routes.items():
        if term_matches(str(trigger), prompt):
            hits.append((str(trigger), _expand_hint(str(hint), templates)))
    return hits


def _knowledge_hint_hits(prompt: str, brain: Path) -> list[tuple[str, str]]:
    data = _load_json(brain / "02-shared-references" / "knowledge-hints.json")
    hints = data.get("hints") or {}
    out: list[tuple[str, str]] = []
    for kw, path in hints.items():
        if term_matches(str(kw), prompt):
            out.append((str(kw), f"knowledge: read `{path}` before proceeding"))
    return out


def _trigger_terms(raw) -> list[str]:
    """Registry `triggers` must be a list. A string means the YAML parser collapsed
    a wrapped flow list — iterating it would match every letter (`a` in 'as a')."""
    if isinstance(raw, list):
        return [str(t) for t in raw if str(t).strip()]
    return []


def _registry_trigger_hits(prompt: str, brain: Path) -> list[tuple[str, str]]:
    data = _load_json(brain / "03-skills" / "skills.registry.json")
    skills = data.get("skills", {})
    chains = data.get("load_chains", {})
    hits: list[tuple[str, str]] = []
    for name, rec in skills.items():
        for term in _trigger_terms(rec.get("triggers")):
            if term_matches(str(term), prompt):
                chain = chains.get(name) or [name]
                path_hint = " → ".join(f"03-skills/{n}/SKILL.md" for n in chain)
                hits.append(
                    (
                        str(term),
                        f"skill `{name}` (load chain, foundation-first): {path_hint}",
                    )
                )
                break
    return hits


def _knowledge_index_hits(prompt: str, brain: Path) -> list[tuple[str, str]]:
    index = brain / "08-knowledge" / "_INDEX.md"
    knowledge_dir = brain / "08-knowledge"
    if not index.is_file():
        return []
    hits: list[tuple[str, str]] = []
    try:
        for line in index.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"^-\s+\[\[([^\]]+)\]\]", line.strip())
            if not m:
                continue
            name = m.group(1)
            tm = re.search(r"[Tt]riggers:\s*(.+)$", line)
            if not tm:
                continue
            for term in re.findall(r"`([^`]+)`", tm.group(1)):
                if term_matches(term, prompt):
                    found = sorted(knowledge_dir.glob(f"*/{name}.md"))
                    target = (
                        str(found[0].relative_to(brain))
                        if found
                        else f"08-knowledge (entry [[{name}]] — see _INDEX.md)"
                    )
                    hits.append((term, f"knowledge: read `{target}` before proceeding"))
                    break
    except OSError:
        return []
    return hits


class LexicalFallback(NamedTuple):
    hits: list[tuple[str, str]]
    status: str  # ok | empty | skipped-short | skipped-empty-prompt | tool-missing | failed
    detail: str


def lexical_fallback(prompt: str, brain: Path, limit: int = LEXICAL_FALLBACK_LIMIT) -> LexicalFallback:
    """Query vault-retrieve --cached. Fail-observable: empty/error is a named status, not silence."""
    tool = brain / "09-tools" / "vault-retrieve.py"
    if not prompt.strip():
        return LexicalFallback([], "skipped-empty-prompt", "")
    if len(re.findall(r"[A-Za-z0-9]{4,}", prompt)) < 2:
        return LexicalFallback([], "skipped-short", "")
    if not tool.exists():
        return LexicalFallback([], "tool-missing", str(tool))
    try:
        proc = subprocess.run(
            [sys.executable, str(tool), prompt.strip(), "--cached", "--json",
             "--quiet", "--no-expand", "--limit", str(limit)],
            cwd=str(brain), capture_output=True, text=True, timeout=8,
        )
    except Exception as exc:  # noqa: BLE001
        return LexicalFallback([], "failed", str(exc))
    if proc.returncode not in (0, 1):
        return LexicalFallback([], "failed", f"exit {proc.returncode}")
    if not proc.stdout.strip():
        return LexicalFallback([], "failed", "empty-stdout")
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return LexicalFallback([], "failed", "bad-json")
    out: list[tuple[str, str]] = []
    for hit in data.get("hits") or []:
        path = hit.get("path") or ""
        if not path.endswith(".md"):
            continue
        snip = re.sub(r"\s+", " ", (hit.get("snippet") or hit.get("title") or "").strip())
        if len(snip) > 140:
            snip = snip[:137] + "\u2026"
        hint = f"lexical: read `{path}` before proceeding"
        if snip:
            hint += f" \u2014 {snip}"
        out.append((path, hint))
    return LexicalFallback(out, "ok" if out else "empty", "")


def apply_lexical_fallback(result: RouteResult, prompt: str, brain: Path) -> None:
    """Layer 1 gap-fill, in place. An under-fire must never look like 'nothing matched'."""
    if len(result.seen) >= LEXICAL_FALLBACK_MIN:
        return
    layer0_n = len(result.seen)
    lex = lexical_fallback(prompt, brain)
    if lex.status in ("skipped-short", "skipped-empty-prompt"):
        return
    cap = TIER_CAPS["lexical fallback"]
    emitted = 0
    for path, hint in lex.hits:
        key = hint_target_key(hint) or path
        if key in result.seen:
            continue
        if emitted >= cap:
            break
        result.seen.add(key)
        result.lines.append(f"- **`lexical`** \u2192 {hint}")
        emitted += 1
    if emitted:
        result.lines.append(
            f"- _(lexical fallback \u2014 Layer 0 had {layer0_n} unique target(s); "
            f"cap {cap}. CLI: `python3 09-tools/vault-retrieve.py \"\u2026\"`)_"
        )
    elif lex.status == "empty":
        result.lines.append(
            f"- _(routing skip \u2014 Layer 0 under-fired ({layer0_n} unique). "
            f"Lexical fallback ran: 0 hits. Do not treat this as no vault entry. "
            f"CLI: `python3 09-tools/vault-retrieve.py \"\u2026\"`)_"
        )
    elif lex.status == "tool-missing":
        result.lines.append(
            f"- _(routing skip \u2014 Layer 0 under-fired ({layer0_n} unique). "
            f"Lexical fallback skipped: vault-retrieve.py missing. "
            f"Do not treat this skip as no match.)_"
        )
    elif lex.status == "failed":
        result.lines.append(
            f"- _(routing skip \u2014 Layer 0 under-fired ({layer0_n} unique). "
            f"Lexical fallback FAILED ({lex.detail or 'error'}). "
            f"Do not treat this skip as no match.)_"
        )


def collect(prompt: str, brain: Path) -> RouteResult:
    """Match Layer 0 (curated \u2192 knowledge hints \u2192 registry \u2192 index)."""
    result = RouteResult()
    raw = (prompt or "").strip()
    if len(re.findall(r"[A-Za-z0-9]{4,}", raw)) < 2:
        return result
    lowered = raw.lower()
    tiers = [
        ("curated trigger", _curated_hits(lowered, brain)),
        ("knowledge hint", _knowledge_hint_hits(lowered, brain)),
        ("registry trigger", _registry_trigger_hits(lowered, brain)),
        ("index trigger", _knowledge_index_hits(lowered, brain)),
    ]
    result.any_layer0 = any(hits for _, hits in tiers)
    for tier_name, hits in tiers:
        cap = TIER_CAPS[tier_name]
        emitted = 0
        dropped = 0
        for trigger, hint in hits:
            key = hint_target_key(hint)
            if key in result.seen:
                continue
            if emitted >= cap:
                dropped += 1
                continue
            result.seen.add(key)
            result.lines.append(f"- **`{trigger}`** → {hint}")
            emitted += 1
        if dropped:
            result.lines.append(
                f"- _(+{dropped} more {tier_name} match(es) dropped — per-tier cap {cap})_"
            )
    result.unique_count = len(result.seen)
    return result


# Produce / ship language already in Layer 0. Matching these must also inject
# close-out + self-improve so those skills are not "hope after the hub body."
PRODUCE_FOLLOWTHROUGH_TERMS = frozenset(
    {
        "implement this",
        "in figma",
        "build in figma",
        "component set",
        "library file",
        "stickersheet",
        "generate a library",
        "figma",
        "open a pr",
        "pull request",
        "fix ci",
        "qa this",
        "audit this screen",
        "close-out",
        "capability mint",
    }
)

# Work verbs with zero Layer-0 hits: make the miss visible (Cursor has no
# lexical fallback; silence previously looked like "nothing in the vault").
WORK_VERBS = frozenset(
    {
        "make",
        "build",
        "fix",
        "add",
        "create",
        "generate",
        "implement",
        "update",
        "refactor",
        "design",
        "draw",
        "ship",
    }
)

# Ordinary English that contains a work verb but is not produce.
MAKE_SKIP_PHRASES = ("make sure", "make sense", "make up for")

FOLLOWTHROUGH_CLOSE_OUT = (
    "- **after produce** → 03-skills/close-out/SKILL.md then "
    "03-skills/self-improve/SKILL.md — run "
    "`python3 09-tools/close-out-dispatch.py --from-prompt \"…\" --run`; "
    "exit 0 is not verified for SKIP classes. Do not skip because the user "
    "did not name those skills."
)
FOLLOWTHROUGH_LAYER0_MISS = (
    "- **Layer 0 missed** → if this is new work, match "
    "02-shared-references/trigger-routes.json and skill `triggers` "
    "before producing. Continuations already in-flight: stay on the baton. "
    "Do not announce this miss as the answer. Do not freestyle doctrine. "
    "CLI: `python3 09-tools/skill-loadset.py \"…\"` then "
    "`python3 09-tools/vault-retrieve.py \"…\"`."
)


def has_work_verb(prompt: str) -> bool:
    """True when the prompt looks like produce, not 'make sure' English."""
    lowered = (prompt or "").lower()
    for verb in WORK_VERBS:
        if verb == "make":
            continue
        if term_matches(verb, lowered):
            return True
    if not term_matches("make", lowered):
        return False
    stripped = lowered
    for phrase in MAKE_SKIP_PHRASES:
        stripped = stripped.replace(phrase, " ")
    return term_matches("make", stripped)


def followthrough_lines(prompt: str, any_layer0: bool) -> list[str]:
    """Extra injection lines after Layer 0 match (or a visible miss on work verbs)."""
    lowered = (prompt or "").lower()
    produce = any(term_matches(t, lowered) for t in PRODUCE_FOLLOWTHROUGH_TERMS)
    work = has_work_verb(prompt)
    if produce or (any_layer0 and work):
        return [FOLLOWTHROUGH_CLOSE_OUT]
    if work and not any_layer0:
        return [FOLLOWTHROUGH_LAYER0_MISS]
    return []


def format_injection(result: RouteResult, extra_lines: list[str] | None = None) -> str:
    extra = extra_lines or []
    lines = list(result.lines)
    lines.extend(extra)
    if not lines:
        return ""
    # A payload made only of parenthetical status notes is noise: nothing matched, and
    # nothing in the prompt asked for work. Chatter must not be taxed on every message
    # (token frugality is a #1 rule). A work verb still gets its visible miss, because
    # followthrough contributes a real line and this guard then does not fire.
    if all(ln.lstrip().startswith("- _(") for ln in lines):
        return ""
    if result.any_layer0:
        header = "# Project trigger detected"
    elif any("Layer 0 missed" in ln for ln in extra):
        header = "# Layer 0 missed"
    elif any("**`lexical`**" in ln for ln in lines):
        header = "# Vault lexical fallback"
    else:
        header = "# Routing coverage note"
    return "\n".join(
        [
            header,
            "",
            *lines,
            "",
            "_Load the matched skills per the AGENTS.md precedence algorithm "
            "(foundation-first) and read matched knowledge entries BEFORE acting. "
            "When authoring inside a specific design system, resolve within that "
            "system's own tokens; backlog its gaps. Layer 0 triggers outrank lexical "
            "hints on conflict. Vendor Figma plugin skills are mechanics only._",
        ]
    )


def route_prompt(prompt: str, brain: Path | None = None) -> str:
    root = brain or resolve_brain_root()
    if root is None:
        return ""
    result = collect(prompt, root)
    apply_lexical_fallback(result, prompt, root)
    extra = followthrough_lines(prompt, result.any_layer0)
    return format_injection(result, extra)
