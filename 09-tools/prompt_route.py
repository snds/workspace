#!/usr/bin/env python3
"""The one Layer-0 prompt matcher (H7). Every surface routes through it.

Reads curated trigger-routes, knowledge-hints, the skill registry, and
08-knowledge/_INDEX.md from the portable workspace (brain) checkout — never from
the current project cwd, so a session in any other repo still gets workspace
routing (pointers only; nothing is ever written into the cwd).

Callers: the Claude dispatcher (import), ws_hook.py user-prompt (subprocess),
cursor-prompt-route.py (compat shim), and every hookless shell through the neutral
`ws route --stdin` (the Cursor and Codex steers).

  prompt_route.py --stdin [--payload] [--host H] [--brain DIR] [--format text|json]
  prompt_route.py --utterance TEXT [--host H] [--brain DIR] [--format text|json]
  prompt_route.py --self-test

--stdin reads the raw utterance (a quoted heredoc, never a shell argument); with
--payload, stdin is the host's hook payload JSON and a host adapter extracts the
prompt. A non-user turn (a declared envelope such as a background task notification,
X2) routes nothing. A single-word trigger that only occurs inside a matched multiword
trigger is suppressed (longest match wins).

Fail-open: missing files or parse errors yield no hits, and the CLI exits 0. Work
verbs with zero hits inject a visible miss (not silence). Produce language also
injects close-out then self-improve so those skills are not hope after a hub body.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
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

SURFACES_REL = "02-shared-references/surfaces.json"
POINTER_REL = (".config", "snds-workspace", "root")
ALIAS_REL = (".claude", "workspace-brain-path")
# Transitional: applies only while no surfaces.json row declares `non_user_envelopes`
# (the table owner adds the key; then this dict is dead and the table alone decides).
_FALLBACK_NON_USER_ENVELOPES = {"claude-code": ("<task-notification>", "Another Claude session sent a message:",
                                                "<agent-message")}
# Mirrors the claude-code `payload_keys_any` marker in surfaces.json (drift-checked by
# --self-test). Only a payload carrying it lets CLAUDE_PROJECT_DIR name the brain.
CLAUDE_PAYLOAD_MARKER = ("transcript_path", "/.claude/projects/")
# Host payload adapters: where each host puts the user's text. Unknown hosts try all.
PAYLOAD_PROMPT_KEYS = {
    "claude-code": ("prompt",),
    "codex": ("prompt",),
    "copilot-vscode": ("prompt",),
    "cursor": ("prompt", "content", "text", "message"),
}
_ANY_PROMPT_KEYS = ("prompt", "userPrompt", "content", "text", "message")


@dataclass
class RouteResult:
    lines: list[str] = field(default_factory=list)
    seen: set[str] = field(default_factory=set)
    unique_count: int = 0
    any_layer0: bool = False


def _is_brain(c: Path) -> bool:
    return (c / "AGENTS.md").is_file() and (c / "02-shared-references" / "trigger-routes.json").is_file()


def _first_line(path: Path) -> Path | None:
    try:
        text = path.read_text(encoding="utf-8").strip().splitlines()
    except OSError:
        return None
    return Path(text[0].strip()) if text and text[0].strip() else None


def resolve_brain_root(project: Path | None = None, *, host: str | None = None,
                       verified: bool = False) -> Path | None:
    """Locate the portable workspace checkout (AGENTS.md + trigger-routes.json).

    Order: an explicit `project`; the neutral pointer ~/.config/snds-workspace/root;
    CLAUDE_PROJECT_DIR, only for a verified Claude host; the ~/.claude alias; then the
    candidate list. A cwd that is not a brain (any other repo, even one with its own
    AGENTS.md) is skipped, so routing works from any cwd and reads only the brain.
    """
    home = Path.home()
    candidates: list[Path | None] = [project, _first_line(home.joinpath(*POINTER_REL))]
    env_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if env_dir and host == "claude-code" and verified:
        candidates.append(Path(env_dir))
    candidates.append(_first_line(home.joinpath(*ALIAS_REL)))
    candidates += [
        home / "Projects" / "Workspace",
        home / "Projects" / "workspace",
        home / "projects" / "workspace",
        Path.cwd(),
        *Path.cwd().parents,
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
        if _is_brain(c):
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


CURATED_TIER = "curated trigger"


def _spans(term: str, prompt: str) -> list[tuple[int, int]]:
    t = term.lower().strip()
    return [m.span() for m in re.finditer(r"(?<!\w)" + re.escape(t) + r"(?!\w)", prompt)]


def suppress_contained(tiers: list, prompt: str) -> list:
    """Longest match wins (X2): a single-word trigger whose every occurrence lies inside a
    matched multiword trigger is dropped. 'zero vector' (a knowledge-index entry) must not
    also fire the bare `vector` registry trigger; a separate 'vector' elsewhere in the
    prompt still does. Curated routes are hand-placed gates and are never suppressed: the
    registry's 'figma component' leaves the curated `figma` gate in place, and the curated
    'theme audit' leaves the curated `audit` QA pre-output gate in place."""
    outer = [sp for _, hits in tiers for t, _ in hits
             if len(str(t).split()) > 1 for sp in _spans(str(t), prompt)]

    def contained(term: str) -> bool:
        t = str(term).lower().strip()
        if len(t.split()) != 1 or not outer:
            return False
        spans = _spans(t, prompt)
        return bool(spans) and all(any(a <= s0 and e0 <= b for a, b in outer) for s0, e0 in spans)

    return [(name, hits if name == CURATED_TIER else [(t, h) for t, h in hits if not contained(t)])
            for name, hits in tiers]


def collect(prompt: str, brain: Path) -> RouteResult:
    """Match Layer 0 (curated \u2192 knowledge hints \u2192 registry \u2192 index)."""
    result = RouteResult()
    raw = (prompt or "").strip()
    if len(re.findall(r"[A-Za-z0-9]{4,}", raw)) < 2:
        return result
    lowered = raw.lower()
    tiers = suppress_contained([
        ("curated trigger", _curated_hits(lowered, brain)),
        ("knowledge hint", _knowledge_hint_hits(lowered, brain)),
        ("registry trigger", _registry_trigger_hits(lowered, brain)),
        ("index trigger", _knowledge_index_hits(lowered, brain)),
    ], lowered)
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


# ------------------------------------------------------------------ turns + host payloads

def non_user_envelopes(host: str | None = None, brain: Path | None = None) -> tuple:
    """Declared non-user turn envelopes (surfaces.json `non_user_envelopes`).

    A known host gets its own list (empty until probed). An unknown or absent host gets
    the union of every declared list: a hookless steer cannot say who is asking, and a
    system envelope is never a work request on any surface."""
    table = _load_json(brain / SURFACES_REL) if brain is not None else {}
    rows = [r for r in table.get("surfaces") or [] if isinstance(r, dict)]
    declared = {r.get("id"): tuple(str(e) for e in r["non_user_envelopes"] if str(e))
                for r in rows if isinstance(r.get("non_user_envelopes"), list)}
    if not declared:
        declared = dict(_FALLBACK_NON_USER_ENVELOPES)
    if host and host != "unknown" and (host in declared or any(r.get("id") == host for r in rows)):
        return declared.get(host, ())
    return tuple(dict.fromkeys(e for envs in declared.values() for e in envs))


def is_user_turn(prompt: str, payload: dict | None = None, host: str | None = None,
                 brain: Path | None = None) -> bool:
    """False for a turn the host injected itself (X2: Claude Code fires UserPromptSubmit on
    background task-notification turns, and X2b: on subagent hand-back agent-message turns).
    Keyed on the declared envelope at the start."""
    text = (prompt or "").lstrip()
    return not any(text.startswith(env) for env in non_user_envelopes(host, brain))


def extract_prompt(payload: dict | None, host: str | None = None) -> str:
    """Host payload adapter: the user's text from a hook payload, or ''."""
    if not isinstance(payload, dict):
        return ""
    for key in PAYLOAD_PROMPT_KEYS.get(host or "", _ANY_PROMPT_KEYS):
        val = payload.get(key)
        if isinstance(val, dict):
            val = val.get("text") or val.get("content") or val.get("prompt") or ""
        if val:
            return str(val)
    return ""


def payload_is_claude(payload: dict | None) -> bool:
    key, needle = CLAUDE_PAYLOAD_MARKER
    return isinstance(payload, dict) and needle in str(payload.get(key) or "")


def route_prompt(prompt: str, brain: Path | None = None, *, host: str | None = None,
                 payload: dict | None = None) -> str:
    root = brain or resolve_brain_root(host=host)
    if root is None:
        return ""
    if not is_user_turn(prompt, payload, host, root):
        return ""
    result = collect(prompt, root)
    apply_lexical_fallback(result, prompt, root)
    extra = followthrough_lines(prompt, result.any_layer0)
    return format_injection(result, extra)


def route_payload(payload: dict | None, host: str | None = None, brain: Path | None = None) -> str:
    """What every hook shim calls: the raw host payload in, the injection text out."""
    verified = host == "claude-code" and payload_is_claude(payload)
    root = brain or resolve_brain_root(host=host, verified=verified)
    return route_prompt(extract_prompt(payload, host), root, host=host, payload=payload)


# ---------------------------------------------------------------------------- CLI

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "prompt_route"


def _fixture_brain(tmp: Path) -> Path:
    brain = tmp / "brain"
    shutil.copytree(FIXTURES / "brain", brain)
    (brain / "AGENTS.md").write_text("# fixture brain\n", encoding="utf-8")
    return brain


def _payload_fixture(name: str) -> dict:
    return json.loads((FIXTURES / "payloads" / f"{name}.json").read_text(encoding="utf-8"))


@contextlib.contextmanager
def _env(**kv):
    saved = {k: os.environ.get(k) for k in kv}
    for k, v in kv.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = str(v)
    try:
        yield
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def self_test_cases() -> list:
    """Hermetic cases over a fixture brain in a temp dir, plus drift checks of the constants
    that mirror surfaces.json."""
    results = []

    def ok(name, cond, detail=""):
        results.append((name, bool(cond), "" if cond else str(detail)))

    live = Path(__file__).resolve().parents[1] / SURFACES_REL
    try:
        rows = {r["id"]: r for r in json.loads(live.read_text(encoding="utf-8"))["surfaces"]}
        marks = [(m.get("key"), m.get("contains")) for m in rows["claude-code"]["markers"]["payload_keys_any"]]
        ok("CLAUDE_PAYLOAD_MARKER mirrors the surfaces.json claude-code marker", CLAUDE_PAYLOAD_MARKER in marks, marks)
        ok("every payload adapter names a surfaces.json host", set(PAYLOAD_PROMPT_KEYS) <= set(rows),
           set(PAYLOAD_PROMPT_KEYS) - set(rows))
    except (OSError, ValueError, KeyError) as exc:
        ok("surfaces.json readable for the drift checks", False, exc)

    with tempfile.TemporaryDirectory(prefix="prompt-route-st-") as td:
        tmp = Path(td)
        brain = _fixture_brain(tmp)
        x2 = _payload_fixture("claude-code.task-notification")
        user = _payload_fixture("claude-code.user")

        # X2: a task-notification turn is not a user turn and routes nothing.
        ok("X2: task-notification is not a user turn (claude-code)",
           not is_user_turn(x2["prompt"], x2, "claude-code", brain))
        got = route_payload(x2, "claude-code", brain)
        ok("X2: route_payload gives nothing for a task-notification turn", got == "", got)
        ok("X2: an unknown host gets the union of declared envelopes",
           route_prompt(x2["prompt"], brain) == "" and
           route_prompt("<fixture-envelope> the zero vector plan", brain) == "")
        ok("X2: a host declared with no envelopes routes the text (cursor)",
           "zero-vector.md" in route_prompt(x2["prompt"], brain, host="cursor"))
        x2b = _payload_fixture("claude-code.agent-message")
        ok("X2b: a subagent hand-back (agent-message) is not a user turn (claude-code)",
           not is_user_turn(x2b["prompt"], x2b, "claude-code", brain)
           and route_payload(x2b, "claude-code", brain) == "")
        ok("X2: the envelope only counts at the start of the turn",
           is_user_turn("please explain <task-notification> tags", None, "claude-code", brain))
        ok("X2: a host row without the key gets no envelopes (gemini-cli)",
           non_user_envelopes("gemini-cli", brain) == ())
        nokey = tmp / "nokey"
        (nokey / "02-shared-references").mkdir(parents=True)
        (nokey / SURFACES_REL).write_text('{"surfaces": [{"id": "claude-code"}]}', encoding="utf-8")
        ok("X2: the transitional fallback applies only when no row declares envelopes",
           non_user_envelopes("claude-code", nokey) == ("<task-notification>", "Another Claude session sent a message:", "<agent-message")
           and non_user_envelopes("claude-code", brain) == ("<task-notification>", "Another Claude session sent a message:", "<agent-message")
           and non_user_envelopes("codex", brain) == ("<fixture-envelope>",))

        # Host payload adapters.
        for name in ("claude-code.user", "cursor.user", "codex.user"):
            host = name.split(".")[0]
            text = route_payload(_payload_fixture(name), host, brain)
            ok(f"adapter {host}: the payload prompt routes",
               "zero-vector.md" in text and "fixture-harness" in text, text)
        ok("adapter: an empty payload routes nothing", route_payload({}, "cursor", brain) == "")

        # Longest match: 'zero vector' suppresses the bare 'vector' trigger.
        text = route_prompt("review the zero vector plan and the harness", brain)
        ok("longest match: the multiword trigger fires", "zero-vector.md" in text, text)
        ok("longest match: the contained single-word trigger is suppressed",
           "fixture-linear-algebra" not in text, text)
        text = route_prompt("the zero vector is a vector with every component zero", brain)
        ok("longest match: a separate occurrence of the single word still fires",
           "fixture-linear-algebra" in text and "zero-vector.md" in text, text)
        text = route_prompt("vector math for the harness", brain)
        ok("longest match: no multiword match leaves single words alone", "fixture-linear-algebra" in text, text)
        text = route_prompt("run the harness audit on this plan", brain)
        ok("longest match: a curated route is never silenced",
           "harness-audit.md" in text and "fixture-harness" in text, text)
        ok("longest match: it silences a contained non-curated single word (registry `audit`)",
           "fixture-audit" not in text, text)
        text = route_prompt("audit the vector plan", brain)
        ok("longest match: the registry single word fires on its own", "fixture-audit" in text, text)

        # Brain resolution order, from an employer-shaped cwd.
        home = tmp / "home"
        (home / ".config" / "snds-workspace").mkdir(parents=True)
        (home / ".claude").mkdir()
        pointer = home / ".config" / "snds-workspace" / "root"
        alias = home / ".claude" / "workspace-brain-path"
        other = tmp / "other-brain"
        shutil.copytree(brain, other)
        employer = tmp / "employer-shaped"
        (employer / "02-shared-references").mkdir(parents=True)
        (employer / "AGENTS.md").write_text("# another repo's contract\n", encoding="utf-8")
        cwd0 = os.getcwd()
        try:
            os.chdir(employer)
            with _env(HOME=home, CLAUDE_PROJECT_DIR=other):
                alias.write_text(f"{other}\n", encoding="utf-8")
                ok("resolve: the ~/.claude alias is used when there is no pointer", resolve_brain_root() == other)
                pointer.write_text(f"{brain}\n", encoding="utf-8")
                ok("resolve: the neutral pointer wins over the alias", resolve_brain_root() == brain)
                ok("resolve: the pointer wins over CLAUDE_PROJECT_DIR even for verified Claude",
                   resolve_brain_root(host="claude-code", verified=True) == brain)
                pointer.unlink()
                alias.write_text(f"{brain}\n", encoding="utf-8")
                ok("resolve: CLAUDE_PROJECT_DIR is used for a verified Claude host",
                   resolve_brain_root(host="claude-code", verified=True) == other)
                ok("resolve: CLAUDE_PROJECT_DIR is ignored for an unverified host",
                   resolve_brain_root(host="claude-code") == brain and resolve_brain_root(host="cursor") == brain)
                ok("resolve: only a payload carrying the Claude marker verifies Claude",
                   payload_is_claude(user) and not payload_is_claude(_payload_fixture("codex.user")))
                ok("resolve: an employer-shaped cwd with its own AGENTS.md is never the brain",
                   resolve_brain_root() != employer)
                before = sorted(str(p.relative_to(employer)) for p in employer.rglob("*"))
                out = route_prompt("review the zero vector plan", resolve_brain_root())
                after = sorted(str(p.relative_to(employer)) for p in employer.rglob("*"))
                ok("employer cwd: routes resolve from the brain", "zero-vector.md" in out, out)
                ok("employer cwd: nothing is written into the cwd", before == after, (before, after))
        finally:
            os.chdir(cwd0)

        # CLI: stdin utterance, payload mode, json format, fail-open, metacharacters.
        script = str(Path(__file__).resolve())

        def cli(args, stdin):
            return subprocess.run([sys.executable, script, *args], input=stdin, capture_output=True,
                                  text=True, timeout=60, env=dict(os.environ, HOME=str(home)))

        r = cli(["--stdin", "--brain", str(brain)], "review the zero vector plan\n")
        ok("cli --stdin routes the utterance", r.returncode == 0 and "zero-vector.md" in r.stdout, r)
        r = cli(["--stdin", "--payload", "--host", "claude-code", "--brain", str(brain)], json.dumps(x2))
        ok("cli --payload X2 prints nothing", r.returncode == 0 and r.stdout == "", r)
        r = cli(["--stdin", "--format", "json", "--brain", str(brain)], x2["prompt"])
        try:
            obj = json.loads(r.stdout)
        except ValueError:
            obj = {}
        ok("cli --format json reports a non-user turn", obj.get("user_turn") is False and obj.get("text") == "", r)
        marker = tmp / "pwned"
        evil = f"review the zero vector plan $(touch {marker}) `touch {marker}`; touch {marker} 'x\" \\"
        r = cli(["--stdin", "--brain", str(brain)], evil)
        ok("cli: shell metacharacters on stdin are data, never run",
           r.returncode == 0 and not marker.exists() and "zero-vector.md" in r.stdout, r)
        r = cli(["--stdin", "--payload", "--brain", str(brain)], "{not json")
        ok("cli: a malformed payload fails open (exit 0, no output)", r.returncode == 0 and r.stdout == "", r)
        r = cli(["--utterance", "review the zero vector plan", "--brain", str(tmp / "missing")], "")
        ok("cli: a missing brain fails open (exit 0, no output)", r.returncode == 0 and r.stdout == "", r)
        r = cli([], "")
        ok("cli: no mode is a usage error (exit 2)", r.returncode == 2, r)
    return results


def main(argv: list | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["--self-test"]:
        results = self_test_cases()
        failed = [r for r in results if not r[1]]
        for name, good, detail in results:
            print(f"{'ok  ' if good else 'FAIL'} {name}" + ("" if good else f" — {detail}"))
        print(f"prompt_route self-test: {len(results) - len(failed)}/{len(results)} passed")
        return 1 if failed else 0
    ap = argparse.ArgumentParser(prog="prompt_route.py", description="Layer-0 routing for any surface.")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--stdin", action="store_true",
                      help="read the utterance (or, with --payload, the hook payload JSON) from stdin")
    mode.add_argument("--utterance")
    ap.add_argument("--payload", action="store_true", help="stdin is the host hook payload JSON")
    ap.add_argument("--host", help="surfaces.json id of the asking host (optional)")
    ap.add_argument("--brain", help="workspace checkout (default: resolved)")
    ap.add_argument("--format", choices=("text", "json"), default="text")
    try:
        a = ap.parse_args(argv)
    except SystemExit as exc:
        return 0 if exc.code == 0 else 2
    brain: Path | None = None
    user_turn, text = False, ""
    try:
        payload: dict | None = None
        if a.stdin:
            raw = sys.stdin.read()
            if a.payload:
                try:
                    payload = json.loads(raw) if raw.strip() else {}
                except ValueError:
                    payload = {}
                payload = payload if isinstance(payload, dict) else {}
                prompt = extract_prompt(payload, a.host)
            else:
                prompt = raw.strip()
        else:
            prompt = a.utterance or ""
        verified = a.host == "claude-code" and payload_is_claude(payload)
        brain = Path(a.brain) if a.brain else resolve_brain_root(host=a.host, verified=verified)
        if brain is not None and not _is_brain(brain):
            brain = None
        user_turn = brain is not None and is_user_turn(prompt, payload, a.host, brain)
        text = route_prompt(prompt, brain, host=a.host, payload=payload) if user_turn else ""
    except Exception:  # noqa: BLE001 - routing never blocks a host
        brain, user_turn, text = None, False, ""
    if a.format == "json":
        print(json.dumps({"brain": str(brain) if brain else None, "user_turn": user_turn,
                          "routed": bool(text), "text": text}, ensure_ascii=False))
    elif text:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())

