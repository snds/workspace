"""Archived matcher copy from .claude/hooks/dispatcher.py (W2-0, 2026-09-25).

Dead since 2026-09-15: handle_user_prompt delegates to 09-tools/prompt_route.py (the one
Layer-0 matcher, H7), and after W2-0 it calls prompt_route.route_payload. Nothing imports
this file; it is kept only for provenance (AGENTS.md mutation policy). The live matcher is
09-tools/prompt_route.py. Names such as WORKSPACE_ROOT refer to the dispatcher's module scope.
"""
# ruff: noqa
# fmt: off

# ---- from dispatcher.py module top (curated trigger map, knowledge hints)
# Curated trigger → load-hint map. Source of truth:
# 02-shared-references/trigger-routes.json (also rendered to trigger-routes.md for
# non-Claude agents). Insertion order IS emission priority — under the per-tier cap
# (FX-2), earlier rows win. Mandate rows (framework #06) come first.
TRIGGER_ROUTES_JSON = WORKSPACE_ROOT / "02-shared-references" / "trigger-routes.json"


def _load_trigger_words() -> dict:
    """Load curated routes from JSON; expand $TEMPLATE refs. Empty dict if missing."""
    try:
        data = json.loads(TRIGGER_ROUTES_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    templates = data.get("templates") or {}
    routes = data.get("routes") or {}
    out = {}
    for trigger, hint in routes.items():
        if isinstance(hint, str) and hint.startswith("$") and hint[1:] in templates:
            out[trigger] = templates[hint[1:]]
        else:
            out[trigger] = hint
    return out


TRIGGER_WORDS = _load_trigger_words()

# Knowledge hints: topic keywords → relevant 08-knowledge/ entry paths.
# When a prompt matches, the entry path is surfaced alongside any skill hint
# so Claude knows to read it before diving into domain work.
KNOWLEDGE_HINTS = {
    "legion": "08-knowledge/game-dev/legion-architecture.md",
    "bobiverse": "08-knowledge/game-dev/legion-architecture.md",
    "centric": "08-knowledge/design/centric-plm-design-system.md · 08-knowledge/engineering/centric-plm-codebase.md",
    "data table": "08-knowledge/design/centric-plm-design-system.md",
    "icon font": "08-knowledge/design/centricsymbols-icon-font.md",
    "centricsymbols": "08-knowledge/design/centricsymbols-icon-font.md",
    "meridian": "08-knowledge/design/meridian-ds-prototype.md",
    "dispatcher": "08-knowledge/cross-domain/workspace-infrastructure.md",
    "worktree": "08-knowledge/cross-domain/workspace-infrastructure.md",
    "drive sync": "08-knowledge/cross-domain/workspace-infrastructure.md",
    "desync": "08-knowledge/cross-domain/workspace-infrastructure.md",
    "session-end": "08-knowledge/cross-domain/workflow-patterns.md",
    "session end": "08-knowledge/cross-domain/workflow-patterns.md",
    "optimize": "08-knowledge/cross-domain/workflow-patterns.md",
    "audit_skip": "08-knowledge/cross-domain/workflow-patterns.md",
    "figma": "08-knowledge/design/figma-ds-surface-authoring.md",
    "component": "08-knowledge/design/figma-ds-surface-authoring.md",
    "variant": "08-knowledge/design/figma-ds-surface-authoring.md",
    "design system": "08-knowledge/design/figma-ds-surface-authoring.md",
    "mockup": "08-knowledge/design/figma-ds-surface-authoring.md",
    "wireframe": "08-knowledge/design/figma-ds-surface-authoring.md",
}



# ---- from dispatcher.py Layer-0/Layer-1 section
def _term_matches(term: str, prompt: str) -> bool:
    """Word-boundary match of a (possibly multiword) trigger term against the
    lowercased prompt. Boundary-anchored so short triggers like `ui` don't fire
    inside words like `build` or `guide`."""
    return re.search(r"(?<!\w)" + re.escape(term.lower()) + r"(?!\w)", prompt) is not None


def _registry_trigger_hits(prompt: str) -> list[tuple[str, str]]:
    """Match skill `triggers` declared in skills.registry.json — the machine graph
    generated from SKILL.md frontmatter. This is the same graph AGENTS.md's loading
    precedence algorithm routes by; reading it here makes the deterministic hook
    layer honor it instead of a hand-synced mirror table. Hints include the
    foundation-first load chain so ancestors load before the skill itself."""
    try:
        data = json.loads(SKILLS_REGISTRY.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return []
    skills = data.get("skills", {})
    chains = data.get("load_chains", {})
    hits: list[tuple[str, str]] = []
    for name, rec in skills.items():
        raw = rec.get("triggers", []) or []
        if isinstance(raw, str):
            # A stored string is one term, never a character iterable.
            # (Wrapped YAML flow lists used to land here and made `a` a trigger.)
            raw = [raw]
        for term in raw:
            term = str(term).strip()
            if len(term) < 2:
                continue
            if _term_matches(term, prompt):
                chain = chains.get(name) or [name]
                path_hint = " → ".join(f"03-skills/{n}/SKILL.md" for n in chain)
                hits.append((str(term), f"skill `{name}` (load chain, foundation-first): {path_hint}"))
                break  # one hit per skill
    return hits


def _knowledge_index_hits(prompt: str) -> list[tuple[str, str]]:
    """Match trigger terms declared inline on 08-knowledge/_INDEX.md entry lines
    (the `Triggers: \\`a\\`, \\`b\\`` convention). The index is the single source of
    truth — entries gain routing the moment their index line declares triggers,
    with no dispatcher edit required."""
    if not KNOWLEDGE_INDEX.exists():
        return []
    hits: list[tuple[str, str]] = []
    try:
        for line in KNOWLEDGE_INDEX.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"^-\s+\[\[([^\]]+)\]\]", line.strip())
            if not m:
                continue
            name = m.group(1)
            tm = re.search(r"[Tt]riggers:\s*(.+)$", line)
            if not tm:
                continue
            for term in re.findall(r"`([^`]+)`", tm.group(1)):
                if _term_matches(term, prompt):
                    found = sorted(KNOWLEDGE_DIR.glob(f"*/{name}.md"))
                    target = (
                        str(found[0].relative_to(WORKSPACE_ROOT)) if found
                        else f"08-knowledge (entry [[{name}]] — see _INDEX.md)"
                    )
                    hits.append((term, f"knowledge: read `{target}` before proceeding"))
                    break  # one hit per entry
    except Exception:
        return []
    return hits


# Per-tier caps (FX-2, 2026-07-09). The old single global cap (15 lines, emit order
# skill → registry → knowledge → index) let a flood of registry matches truncate the
# curated knowledge hints away — the highest-value tier lost to the noisiest one.
# Curated tiers now emit FIRST and every tier keeps its own budget; a hot tier can
# no longer starve the others.
TIER_CAPS = {
    "curated trigger": 8,
    "knowledge hint": 4,
    "registry trigger": 6,
    "index trigger": 4,
    "lexical fallback": 2,
}

# Run FTS only when Layer-0 unique targets fall below this. Keeps triggers primary
# and avoids paying lexical cost (and noise) on well-routed prompts.
LEXICAL_FALLBACK_MIN = 2
LEXICAL_FALLBACK_LIMIT = 2
# LEXICAL_TOOL stays live in the dispatcher (the session-start index refresh).


# Extracts the first workspace-relative .md path in a hint — the dedupe key. Hints
# from different tiers pointing at the same file (e.g. a curated row and a registry
# row both routing to design-engineer/SKILL.md) collapse to the first occurrence.
_HINT_TARGET_RE = re.compile(r"\d{2}-[\w./-]+\.md")


def _hint_target_key(hint: str) -> str:
    m = _HINT_TARGET_RE.search(hint)
    return m.group(0) if m else hint


class LexicalFallback(NamedTuple):
    hits: list[tuple[str, str]]
    status: str  # ok | empty | skipped-short | skipped-empty-prompt | tool-missing | failed
    detail: str


def _lexical_fallback(prompt: str, limit: int = LEXICAL_FALLBACK_LIMIT) -> LexicalFallback:
    """Query vault-retrieve --cached. Fail-observable: empty/error is a named status, not silence."""
    if not prompt.strip():
        return LexicalFallback([], "skipped-empty-prompt", "")
    if len(re.findall(r"[A-Za-z0-9]{4,}", prompt)) < 2:
        return LexicalFallback([], "skipped-short", "")
    if not LEXICAL_TOOL.exists():
        return LexicalFallback([], "tool-missing", str(LEXICAL_TOOL))
    try:
        proc = subprocess.run(
            [
                sys.executable,
                str(LEXICAL_TOOL),
                prompt.strip(),
                "--cached",
                "--json",
                "--quiet",
                "--no-expand",
                "--limit",
                str(limit),
            ],
            cwd=str(WORKSPACE_ROOT),
            capture_output=True,
            text=True,
            timeout=8,
        )
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(f"[user-prompt] vault-retrieve skipped: {exc}\n")
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
        snip = (hit.get("snippet") or hit.get("title") or "").strip()
        snip = re.sub(r"\s+", " ", snip)
        if len(snip) > 140:
            snip = snip[:137] + "…"
        hint = f"lexical: read `{path}` before proceeding"
        if snip:
            hint += f" — {snip}"
        out.append((path, hint))
    if not out:
        return LexicalFallback([], "empty", "")
    return LexicalFallback(out, "ok", "")


def _lexical_fallback_hits(prompt: str, limit: int = LEXICAL_FALLBACK_LIMIT) -> list[tuple[str, str]]:
    """Compat wrapper: hits only. Prefer `_lexical_fallback` when status matters."""
    return _lexical_fallback(prompt, limit=limit).hits


def _followthrough_lines(raw_prompt: str, layer0_any: bool) -> list[str]:
    """Same produce-followthrough as Cursor (`09-tools/prompt_route.py`). Fail-open."""
    tools_dirs = [WORKSPACE_ROOT / "09-tools"]
    try:
        pointer = Path.home() / ".claude" / "workspace-brain-path"
        text = pointer.read_text(encoding="utf-8").strip().splitlines()
        if text:
            tools_dirs.append(Path(text[0].strip()) / "09-tools")
    except OSError:
        pass
    for tools in tools_dirs:
        if not (tools / "prompt_route.py").is_file():
            continue
        if str(tools) not in sys.path:
            sys.path.insert(0, str(tools))
        try:
            import prompt_route as _pr

            return _pr.followthrough_lines(raw_prompt, layer0_any)
        except Exception:
            continue
    return []
