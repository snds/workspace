#!/usr/bin/env python3
"""Per-surface routing trajectories — does each surface actually DELIVER the context?

`evaluate-skill-routing.py` proves a matcher routes correctly, but it carries its own
copy of the matcher, so it can be green while every real surface is wrong. This runs
each surface's **actual entry point** — the command the tool itself invokes — and asserts
what lands in the model's context.

The failure it exists to prevent, measured 2026-09-15: six of the 48 routing fixtures
delivered a different file set on Claude Code than on Cursor. Same vault, same utterance.
Both surfaces were wrong, in opposite directions, and nothing could see it because nothing
ran both.

Surfaces (H7):
  claude-code   .claude/hooks/dispatcher.py user-prompt   (stdin JSON, CLAUDE_PROJECT_DIR)
  cursor        the steer: `ws route --stdin <<'EOF' … EOF` (brain.mdc + User Rules)
  codex         the steer from the Codex beacon (UserPromptSubmit once trusted)
  cursor-hook   09-tools/cursor-prompt-route.py           (compatibility shim)
  shell-agent   09-tools/skill-loadset.py --json          (a different code path: the load set)
  claude-chat   literal reader: the web pack (web-session.md, BEACON.md, the route digest)
  aider         literal reader: the files .aider.conf.yml loads, following what they name

Every non-Claude surface runs with a scrubbed env (PATH, a temp HOME whose neutral pointer
names this checkout, the host's own family marker from surfaces.json) — never
CLAUDE_PROJECT_DIR. The steer runs the real `00-bootstrap/dist/ws` wrapper through /bin/sh,
so quoting is tested as the agent runs it. The parity set is derived from surfaces.json:
the `minimum_surfaces` rows that are hookable.

Case fields: `expect_paths`, `forbid_paths`, `expect_header`, `expect_empty`, `parity`, and
`cwd` ("workspace" default, or "employer-shaped": a temp git repo with an unknown-owner
remote and its own AGENTS.md). In an employer-shaped cwd the routes must resolve from the
brain, the repo must stay byte-identical (.git included), and nothing from the repo may
appear in the payload (routing context only, never employer substance).

Structural checks: one matcher behind every entry point (AST) and every registered
user-prompt command (surfaces.json commands), the steer text where it is declared, digest
drift, and the hookless adapters. The adapter list, the hook files and the user-prompt event
names all come from surfaces.json (surfaces[].adapters, outputs, formats), never from here.

Usage:
  python3 09-tools/evaluate-surface-trajectories.py           # run corpus
  python3 09-tools/evaluate-surface-trajectories.py --check   # CI gate
  python3 09-tools/evaluate-surface-trajectories.py --utterance "…"   # ad-hoc, all surfaces
  python3 09-tools/evaluate-surface-trajectories.py --json
  python3 09-tools/evaluate-surface-trajectories.py --self-test

Exit: 0 pass · 1 a trajectory failed · 2 could not run.
"""

from __future__ import annotations

import argparse
import ast
import atexit
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
CORPUS = ROOT / "02-shared-references" / "surface-trajectory-cases.jsonl"
DISPATCHER = ROOT / ".claude" / "hooks" / "dispatcher.py"
SURFACES_JSON = ROOT / "02-shared-references" / "surfaces.json"
WS_WRAPPER = ROOT / "00-bootstrap" / "dist" / "ws"
DIGEST_REL = "02-shared-references/trigger-routes-digest.md"
ROUTES_REL = "02-shared-references/trigger-routes.json"

# Workspace-relative path inside a delivered payload.
PATH_RE = re.compile(r"\b(?:0\d-[\w./-]+\.(?:md|py)|llms\.txt)")

# The steer every hookless surface runs. The utterance travels in a quoted heredoc on
# stdin, never interpolated into a shell argument.
STEER_TOKEN = "ws route --stdin"
STEER = STEER_TOKEN + " <<'EOF'\n{utterance}\nEOF\n"
# Where the steer is declared. brain.mdc is tracked in the workspace; the two paste and
# beacon texts are rendered from beacons.json (render_shims.py) and reach a machine only
# through a human install, so until they carry the steer they are reported as PENDING.
STEER_REQUIRED = [".cursor/rules/brain.mdc"]
STEER_RENDERED = {"cursor": "00-bootstrap/dist/cursor-user-rules.txt",
                  "codex": "00-bootstrap/dist/codex-AGENTS.md"}

# Every hookless adapter must name the workspace entry points itself — that file is the
# only thing reaching the model when no hook exists. The list (HOOKLESS_ADAPTERS, below the
# table readers) comes from surfaces.json `surfaces[].adapters`.
HOOKLESS_MUST_NAME = ["AGENTS.md"]

# Literal readers (D7): no python, no hook. They follow only what their entry files say.
LITERAL_READERS = {
    "claude-chat": ["00-bootstrap/adapters/web-session.md", "00-bootstrap/dist/BEACON.md", DIGEST_REL],
    "aider": ".aider.conf.yml",
}

EMPLOYER_SENTINEL = "EMPLOYER-SUBSTANCE-SENTINEL"
EMPLOYER_REMOTE = "git@github.com:acme-corp/employer-shaped.git"   # unknown owner: most restrictive walls

# The matcher's internals. No entry point may define or call them; they live in prompt_route.
MATCHER_INTERNALS = {"_curated_hits", "_knowledge_hint_hits", "_registry_trigger_hits",
                     "_knowledge_index_hits", "collect", "suppress_contained", "TIER_CAPS"}
# USER_PROMPT_EVENTS and HOOK_FILES are derived from surfaces.json below (formats, outputs).
ROUTING_ENTRY_TOKENS = ("/.claude/hooks/dispatcher.py", "/bin/ws-hook")


# ------------------------------------------------------------------------- table

def _table() -> dict:
    try:
        t = json.loads(SURFACES_JSON.read_text(encoding="utf-8"))
        return t if isinstance(t, dict) else {}
    except (OSError, ValueError):
        return {}


def parity_surfaces(table: dict | None = None) -> tuple:
    """The surfaces that run the one matcher and therefore MUST agree: the hookable rows of
    surfaces.json `minimum_surfaces`. A newly probed host needs a table row, not code."""
    t = _table() if table is None else table
    rows = {r.get("id"): r for r in t.get("surfaces") or [] if isinstance(r, dict)}
    return tuple(s for s in t.get("minimum_surfaces") or [] if (rows.get(s) or {}).get("hookable"))


def host_markers(host: str, table: dict | None = None) -> dict:
    """The host's own env markers from surfaces.json, so the scrubbed env looks like the host."""
    t = _table() if table is None else table
    for r in t.get("surfaces") or []:
        if r.get("id") == host:
            return {m["name"]: (m.get("value") or m.get("value_prefix") or "trajectory-fixture")
                    for m in (r.get("markers") or {}).get("env") or [] if m.get("name")}
    return {}


def hookless_adapters(table: dict | None = None) -> list:
    """The md adapters (surfaces[].adapters, role md) of rows whose dialect is `none`: no hook
    output reaches the model there, so the adapter file is the only way in. A new surface row
    with an adapter is picked up here without a code edit."""
    t = _table() if table is None else table
    out = []
    for r in t.get("surfaces") or []:
        if not isinstance(r, dict) or r.get("dialect", "none") != "none":
            continue
        for a in r.get("adapters") or []:
            rel = a.get("path") if isinstance(a, dict) else None
            if rel and a.get("role", "md") == "md" and rel not in out:
                out.append(rel)
    return out


def hook_files(table: dict | None = None) -> list:
    """Every non-probe output that renders a hook layer (a JSON file with a `hooks` key)."""
    t = _table() if table is None else table
    layers = {lay.get("id") for lay in t.get("layers") or [] if isinstance(lay, dict)}
    return [o["path"] for o in t.get("outputs") or []
            if isinstance(o, dict) and o.get("path") and o.get("layer") in layers
            and o.get("render", "hooks") == "hooks" and not o.get("probe")]


def user_prompt_events(table: dict | None = None) -> set:
    """Each hook format's native name for the neutral user-prompt event."""
    t = _table() if table is None else table
    return {f["user-prompt"] for f in (t.get("formats") or {}).values()
            if isinstance(f, dict) and f.get("user-prompt")}


PARITY_SURFACES = parity_surfaces()
HOOKLESS_ADAPTERS = hookless_adapters()
HOOK_FILES = hook_files()
USER_PROMPT_EVENTS = user_prompt_events()


# ---------------------------------------------------------------------- sandbox

class Sandbox:
    """A temp HOME whose neutral pointer names this checkout, the real `ws` wrapper on PATH,
    and an employer-shaped repo. Created once per run; removed at exit."""

    def __init__(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="surface-traj-"))
        self.home = self.tmp / "home"
        base = self.home / ".config" / "snds-workspace"
        self.bin = base / "bin"
        self.bin.mkdir(parents=True)
        (base / "root").write_text(f"{ROOT}\n", encoding="utf-8")
        if WS_WRAPPER.is_file():
            shutil.copy2(WS_WRAPPER, self.bin / "ws")
            (self.bin / "ws").chmod(0o755)
        (self.bin / "python3").symlink_to(sys.executable)
        self.employer = self._employer_repo()
        atexit.register(shutil.rmtree, self.tmp, True)

    def env(self, host: str | None = None) -> dict:
        env = {"PATH": f"{self.bin}:/usr/bin:/bin", "HOME": str(self.home), "LANG": "C.UTF-8"}
        env.update(host_markers(host) if host else {})
        return env

    def _employer_repo(self) -> Path:
        repo = self.tmp / "employer-shaped"
        (repo / "src").mkdir(parents=True)
        (repo / "AGENTS.md").write_text(f"# Employer-shaped fixture contract\n{EMPLOYER_SENTINEL}\n",
                                        encoding="utf-8")
        (repo / "src" / "app.txt").write_text(f"{EMPLOYER_SENTINEL}\n", encoding="utf-8")
        genv = dict(self.env(), GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        try:
            subprocess.run(["git", "init", "-q"], cwd=repo, env=genv, check=True, capture_output=True, timeout=30)
            subprocess.run(["git", "remote", "add", "origin", EMPLOYER_REMOTE], cwd=repo, env=genv, check=True,
                           capture_output=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            pass    # still a foreign repo with its own AGENTS.md; the byte check stands
        return repo

    @staticmethod
    def snapshot(path: Path) -> dict:
        out = {}
        for p in sorted(path.rglob("*")):
            rel = str(p.relative_to(path))
            out[rel] = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "dir"
        return out


_SANDBOX: Sandbox | None = None


def sandbox() -> Sandbox:
    global _SANDBOX
    if _SANDBOX is None:
        _SANDBOX = Sandbox()
    return _SANDBOX


def _cwd(case_cwd: str | None) -> Path:
    return sandbox().employer if case_cwd == "employer-shaped" else ROOT


# ------------------------------------------------------------------ surface delivery

def _run(cmd: list[str], stdin: str = "", *, cwd: Path = ROOT, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, input=stdin, capture_output=True, text=True, cwd=str(cwd),
                          env=env if env is not None else sandbox().env(), timeout=60)


def deliver_claude_code(utterance: str, cwd: Path = ROOT) -> str:
    """Claude runs only in the workspace here (the walls keep it out of employer repos)."""
    if not DISPATCHER.exists():
        return ""
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(ROOT))
    proc = _run([sys.executable, str(DISPATCHER), "user-prompt"], json.dumps({"prompt": utterance}),
                cwd=ROOT, env=env)
    if not proc.stdout.strip():
        return ""
    try:
        return json.loads(proc.stdout).get("hookSpecificOutput", {}).get("additionalContext", "")
    except json.JSONDecodeError:
        return ""


def _steer(host: str, utterance: str, cwd: Path) -> str:
    proc = _run(["/bin/sh", "-c", STEER.format(utterance=utterance)], cwd=cwd, env=sandbox().env(host))
    return proc.stdout if proc.returncode == 0 else ""


def deliver_cursor(utterance: str, cwd: Path = ROOT) -> str:
    return _steer("cursor", utterance, cwd)


def deliver_codex(utterance: str, cwd: Path = ROOT) -> str:
    return _steer("codex", utterance, cwd)


def deliver_cursor_hook(utterance: str, cwd: Path = ROOT) -> str:
    proc = _run([sys.executable, str(TOOLS / "cursor-prompt-route.py")], json.dumps({"prompt": utterance}),
                cwd=cwd, env=sandbox().env("cursor"))
    try:
        return (json.loads(proc.stdout or "{}") or {}).get("additional_context", "")
    except json.JSONDecodeError:
        return ""


def deliver_shell_agent(utterance: str, cwd: Path = ROOT) -> str:
    """The contract tells any shell-capable agent to run this. Its paths ARE the delivery."""
    proc = _run([sys.executable, str(TOOLS / "skill-loadset.py"), "--json", utterance], cwd=cwd)
    try:
        data = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return ""
    return "\n".join([*data.get("paths", []), data.get("close_out", "")])


def _reader_entry(surface: str) -> list[str]:
    spec = LITERAL_READERS.get(surface)
    if isinstance(spec, list):
        return spec
    try:
        text = (ROOT / spec).read_text(encoding="utf-8")
    except (OSError, TypeError):
        return []
    block = re.search(r"^read:\s*\n((?:\s+-\s*.+\n?)+)", text, re.M)
    return [ln.split("-", 1)[1].strip() for ln in (block.group(1).splitlines() if block else []) if "-" in ln]


def _word(term: str, lowered: str) -> bool:
    t = term.strip().lower()
    return len(t) > 1 and re.search(r"(?<!\w)" + re.escape(t) + r"(?!\w)", lowered) is not None


def literal_read(entry: list[str], utterance: str) -> str:
    """What a reader that cannot run python gets: it follows only the route sources its
    entry files name (the digest, or trigger-routes.json) and matches triggers literally."""
    texts = {}
    for rel in entry:
        try:
            texts[rel] = (ROOT / rel).read_text(encoding="utf-8")
        except OSError:
            continue
    blob = "\n".join(texts.values())
    lowered = utterance.lower()
    out = []
    if DIGEST_REL in texts or "trigger-routes-digest.md" in blob:
        for line in (ROOT / DIGEST_REL).read_text(encoding="utf-8").splitlines():
            m = re.match(r"^- (.+?) → (.+)$", line)
            if m and any(_word(t, lowered) for t in m.group(1).split(",")):
                out.append(m.group(2))
    if "trigger-routes.json" in blob:
        data = json.loads((ROOT / ROUTES_REL).read_text(encoding="utf-8"))
        templates = data.get("templates") or {}
        for trig, hint in (data.get("routes") or {}).items():
            if _word(str(trig), lowered):
                hint = str(hint)
                out.append(templates.get(hint[1:], hint) if hint.startswith("$") else hint)
    return "\n".join(out)


def deliver_claude_chat(utterance: str, cwd: Path = ROOT) -> str:
    return literal_read(_reader_entry("claude-chat"), utterance)


def deliver_aider(utterance: str, cwd: Path = ROOT) -> str:
    return literal_read(_reader_entry("aider"), utterance)


SURFACES = {
    "claude-code": deliver_claude_code,
    "cursor": deliver_cursor,
    "codex": deliver_codex,
    "cursor-hook": deliver_cursor_hook,
    "shell-agent": deliver_shell_agent,
    "claude-chat": deliver_claude_chat,
    "aider": deliver_aider,
}
# Surfaces that may run with an employer-shaped cwd (Claude never works there).
EMPLOYER_CWD_SURFACES = {"cursor", "codex", "cursor-hook"}


# ------------------------------------------------------------------------ assertions

def _paths(payload: str) -> set[str]:
    return set(PATH_RE.findall(payload))


def evaluate_case(case: dict) -> list[str]:
    wanted = case.get("surfaces") or list(PARITY_SURFACES)
    if wanted == "*":
        wanted = list(SURFACES)
    where = case.get("cwd") or "workspace"
    fails: list[str] = []
    if where not in ("workspace", "employer-shaped"):
        return [f"{case['id']}: unknown cwd '{where}'"]
    cwd = _cwd(where)
    delivered: dict[str, str] = {}

    for surface in wanted:
        fn = SURFACES.get(surface)
        if fn is None:
            fails.append(f"{case['id']}: unknown surface '{surface}'")
            continue
        if where == "employer-shaped" and surface not in EMPLOYER_CWD_SURFACES:
            fails.append(f"{case['id']}: {surface} does not run in an employer-shaped cwd")
            continue
        before = Sandbox.snapshot(cwd) if where == "employer-shaped" else None
        payload = fn(case["utterance"], cwd)
        delivered[surface] = payload
        if before is not None:
            after = Sandbox.snapshot(cwd)
            if after != before:
                changed = sorted(set(before.items()) ^ set(after.items()))
                fails.append(f"{case['id']} [{surface}]: wrote into the employer-shaped cwd {changed[:3]}")
            if EMPLOYER_SENTINEL in payload or str(cwd) in payload:
                fails.append(f"{case['id']} [{surface}]: employer-repo content reached the payload")

        if case.get("expect_empty") and payload.strip():
            fails.append(f"{case['id']} [{surface}]: expected no injection, got {len(payload)} chars")
        for want in case.get("expect_paths", []):
            if want not in payload:
                fails.append(f"{case['id']} [{surface}]: missing {want}")
        for nope in case.get("forbid_paths", []):
            if nope in payload:
                fails.append(f"{case['id']} [{surface}]: delivered forbidden {nope}")
        header = case.get("expect_header")
        if header and not payload.startswith(header):
            got = payload.splitlines()[0] if payload.strip() else "(nothing)"
            fails.append(f"{case['id']} [{surface}]: header '{got}' != '{header}'")

    if case.get("parity"):
        pair = [s for s in PARITY_SURFACES if s in delivered]
        if len(pair) >= 2:
            sets = {s: _paths(delivered[s]) for s in pair}
            base = sets[pair[0]]
            for other in pair[1:]:
                diff = base ^ sets[other]
                if diff:
                    fails.append(
                        f"{case['id']}: SURFACE DIVERGENCE {pair[0]} vs {other} — "
                        f"{sorted(diff)} (one matcher means one delivery)"
                    )
    return fails


# ----------------------------------------------------------------------- structure

def _defs_and_calls(tree: ast.AST) -> tuple[set, set]:
    defs, calls = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defs.add(node.name)
        elif isinstance(node, ast.Assign):
            defs.update(t.id for t in node.targets if isinstance(t, ast.Name))
        elif isinstance(node, ast.Call):
            f = node.func
            calls.add(f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", ""))
    return defs, calls


def _function(tree: ast.AST, name: str):
    return next((n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name), None)


def check_one_matcher(root: Path = ROOT, table: dict | None = None) -> list[str]:
    """Structural guard: every entry point delegates to prompt_route; none forks it.

    Parity fixtures catch drift only for utterances in the corpus. This catches the shape
    that produced the drift — a second implementation — for every utterance: the Claude
    hook handler, the Cursor compat shim, the hook core, the `ws route` wrapper, and every
    registered user-prompt command (including plugin hooks), resolved through surfaces.json.
    """
    fails: list[str] = []

    def parse(rel):
        try:
            return ast.parse((root / rel).read_text(encoding="utf-8"))
        except (OSError, SyntaxError) as exc:
            fails.append(f"{rel}: cannot parse ({exc.__class__.__name__})")
            return None

    disp_rel = ".claude/hooks/dispatcher.py"
    if (root / disp_rel).exists():
        tree = parse(disp_rel)
        fn = _function(tree, "handle_user_prompt") if tree else None
        if tree and fn is None:
            fails.append("dispatcher.py has no handle_user_prompt")
        elif fn is not None:
            text = ast.get_source_segment((root / disp_rel).read_text(encoding="utf-8"), fn) or ""
            _, calls = _defs_and_calls(fn)
            if "prompt_route" not in text or not calls & {"route_prompt", "route_payload"}:
                fails.append("dispatcher.handle_user_prompt does not delegate to prompt_route — "
                             "a second matcher is how the surfaces drifted apart (2026-09-15)")
            for forked in sorted(calls & MATCHER_INTERNALS):
                fails.append(f"dispatcher.handle_user_prompt calls `{forked}` — the matcher lives in "
                             "09-tools/prompt_route.py")

    for rel in ("09-tools/cursor-prompt-route.py", "09-tools/ws_hook.py"):
        tree = parse(rel)
        if tree is None:
            continue
        defs, calls = _defs_and_calls(tree)
        for forked in sorted(defs & MATCHER_INTERNALS):
            fails.append(f"{rel} defines `{forked}` — the matcher lives in 09-tools/prompt_route.py")
        if "prompt_route" not in (root / rel).read_text(encoding="utf-8"):
            fails.append(f"{rel} does not delegate to prompt_route")

    try:
        ws = (root / "00-bootstrap" / "dist" / "ws").read_text(encoding="utf-8")
    except OSError:
        ws = ""
    if not re.search(r'^\s*route\)\s*shift;\s*exec python3 "\$R/09-tools/prompt_route\.py" "\$@";;', ws, re.M):
        fails.append("00-bootstrap/dist/ws: `ws route` does not exec 09-tools/prompt_route.py")

    t = _table() if table is None else table
    behaviours = []
    for cid, c in (t.get("commands") or {}).items():
        b = c.get("behaviour") or (c.get("behaviour_by_event") or {}).get("user-prompt")
        behaviours.append((cid, str(c.get("template") or "").replace("{event}", "user-prompt"), b))
    for rel in HOOK_FILES:
        try:
            hooks = (json.loads((root / rel).read_text(encoding="utf-8")) or {}).get("hooks") or {}
        except (OSError, ValueError):
            continue
        for event, entries in hooks.items():
            if event not in USER_PROMPT_EVENTS:
                continue
            for e in entries or []:
                for h in (e.get("hooks") if isinstance(e, dict) and "hooks" in e else [e]) or []:
                    cmd = str((h or {}).get("command") or "")
                    hit = next((x for x in behaviours if x[1] and x[1] in cmd), None)
                    if hit is None:
                        fails.append(f"{rel}: {event} runs an undeclared command ({cmd[:60]}) — "
                                     "declare it in surfaces.json commands")
                    elif hit[2] == "layer0-route" and not any(tok in cmd for tok in ROUTING_ENTRY_TOKENS):
                        fails.append(f"{rel}: {event} command `{hit[0]}` routes outside the checked entry points")
    return fails


def dispatcher_dead_fork(root: Path = ROOT) -> list[str]:
    """D3 notice: matcher internals still defined in the dispatcher but no longer called by
    handle_user_prompt. Archiving them is the dispatcher owner's step; reported, not failed."""
    try:
        tree = ast.parse((root / ".claude" / "hooks" / "dispatcher.py").read_text(encoding="utf-8"))
    except (OSError, SyntaxError):
        return []
    defs, _ = _defs_and_calls(tree)
    return sorted(defs & (MATCHER_INTERNALS | {"TRIGGER_WORDS", "_lexical_fallback", "_followthrough_lines"}))


def check_steers(root: Path = ROOT) -> tuple[list[str], list[str]]:
    """The steer text where it is declared. Returns (fails, pending)."""
    fails, pending = [], []
    for rel in STEER_REQUIRED:
        try:
            if STEER_TOKEN not in (root / rel).read_text(encoding="utf-8"):
                fails.append(f"{rel}: no `{STEER_TOKEN}` steer line")
        except OSError:
            fails.append(f"{rel}: missing")
    for host, rel in STEER_RENDERED.items():
        try:
            if STEER_TOKEN not in (root / rel).read_text(encoding="utf-8"):
                pending.append(f"{rel}: the {host} steer awaits the beacons.json `ws` line (render_shims.py --write)")
        except OSError:
            pending.append(f"{rel}: not rendered")
    return fails, pending


def check_digest(root: Path = ROOT) -> list[str]:
    tool = root / "09-tools" / "build-trigger-routes.py"
    if not tool.is_file():
        return ["09-tools/build-trigger-routes.py missing (the route digest cannot be drift-checked)"]
    proc = subprocess.run([sys.executable, str(tool), "--check"], capture_output=True, text=True,
                          cwd=str(root), timeout=60)
    return [] if proc.returncode == 0 else [f"route digest drift: {(proc.stdout + proc.stderr).strip()[:200]}"]


def check_hookless_adapters() -> list[str]:
    """A surface with no hook gets only what its adapter file says. Assert it says it."""
    fails = [] if HOOKLESS_ADAPTERS else ["surfaces.json yields no hookless adapters (surfaces[].adapters)"]
    for rel in HOOKLESS_ADAPTERS:
        path = ROOT / rel
        if not path.exists():
            fails.append(f"hookless adapter missing: {rel}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in HOOKLESS_MUST_NAME:
            if token not in text:
                fails.append(f"{rel}: never names {token} — a hookless agent has no other way in")
    for surface in LITERAL_READERS:
        entry = _reader_entry(surface)
        blob = "".join((ROOT / r).read_text(encoding="utf-8") for r in entry if (ROOT / r).is_file())
        if not entry or ("trigger-routes-digest.md" not in blob and "trigger-routes.json" not in blob
                         and DIGEST_REL not in entry):
            fails.append(f"literal reader {surface}: its entry files name no route source")
    return fails


def structural() -> tuple[list[str], list[str]]:
    fails = []
    if len(PARITY_SURFACES) < 2:
        fails.append(f"surfaces.json yields {len(PARITY_SURFACES)} parity surface(s); need at least 2")
    for s in PARITY_SURFACES:
        if s not in SURFACES:
            fails.append(f"parity surface {s} (surfaces.json) has no delivery here")
    steer_fails, pending = check_steers()
    fails += check_one_matcher() + steer_fails + check_digest() + check_hookless_adapters()
    dead = dispatcher_dead_fork()
    if dead:
        pending.append(f"D3: dispatcher.py still defines unused matcher internals {dead} (archive them)")
    return fails, pending


# ----------------------------------------------------------------------- self-test

def self_test() -> int:
    """Prove the assertions can fail. A trajectory suite that only passes proves nothing."""
    failures = []

    def expect(name, cond):
        if not cond:
            failures.append(name)

    expect("paths() extracts a skill path",
           _paths("load 03-skills/qa/SKILL.md now") == {"03-skills/qa/SKILL.md"})
    expect("paths() ignores prose", _paths("nothing pathlike here") == set())

    fake = {"minimum_surfaces": ["a", "b", "c"],
            "surfaces": [{"id": "a", "hookable": True}, {"id": "b", "hookable": False},
                         {"id": "c", "hookable": True, "markers": {"env": [{"name": "C_AGENT", "value": "1"}]}}]}
    expect("parity surfaces come from the table (hookable minimum rows)", parity_surfaces(fake) == ("a", "c"))
    expect("host markers come from the table", host_markers("c", fake) == {"C_AGENT": "1"})
    expect("the live table yields claude-code, cursor and codex",
           set(PARITY_SURFACES) >= {"claude-code", "cursor", "codex"})
    fake_adapters = {"surfaces": [
        {"id": "hooked", "dialect": "claude", "adapters": [{"path": "HOOKED.md", "role": "md"}]},
        {"id": "new-agent", "dialect": "none", "adapters": [{"path": "NEWAGENT.md", "role": "md"},
                                                            {"path": ".newagent.toml", "role": "config"}]}],
        "layers": [{"id": "new-user"}], "formats": {"new-hooks": {"user-prompt": "OnPrompt"}},
        "outputs": [{"path": "dist/new-hooks.json", "layer": "new-user"},
                    {"path": "dist/probe/new.json", "layer": "new-user", "probe": True},
                    {"path": "dist/NEW.md", "layer": None, "render": "beacon"}]}
    expect("hookless adapters come from the table (md adapters on dialect-none rows)",
           hookless_adapters(fake_adapters) == ["NEWAGENT.md"])
    expect("hook files come from the table (non-probe hook outputs)",
           hook_files(fake_adapters) == ["dist/new-hooks.json"])
    expect("user-prompt event names come from the table", user_prompt_events(fake_adapters) == {"OnPrompt"})
    expect("the live table yields the hookless adapters and the codex hook file",
           "PERPLEXITY.md" in HOOKLESS_ADAPTERS and "00-bootstrap/dist/codex-hooks.json" in HOOK_FILES
           and {"UserPromptSubmit", "beforeSubmitPrompt"} <= USER_PROMPT_EVENTS)

    real = {"id": "t", "utterance": "figma component variants",
            "surfaces": ["cursor"], "expect_paths": ["03-skills/figma/SKILL.md"]}
    expect("a satisfied expectation passes (the cursor steer)", not evaluate_case(real))

    missing = dict(real, expect_paths=["03-skills/definitely-not-a-skill/SKILL.md"])
    expect("a missing path fails", evaluate_case(missing))

    forbidden = dict(real, expect_paths=[], forbid_paths=["03-skills/figma/SKILL.md"])
    expect("a forbidden path fails", evaluate_case(forbidden))

    wrong_header = dict(real, expect_paths=[], expect_header="# Definitely Not The Header")
    expect("a wrong header fails", evaluate_case(wrong_header))

    expect("expect_empty fails on a firing utterance",
           evaluate_case(dict(real, expect_paths=[], expect_empty=True)))

    expect("unknown surface is an error",
           evaluate_case({"id": "t", "utterance": "x", "surfaces": ["nope"]}))
    expect("claude-code in an employer-shaped cwd is an error",
           evaluate_case({"id": "t", "utterance": "x", "surfaces": ["claude-code"], "cwd": "employer-shaped"}))

    # Parity is the centerpiece, so prove it fails on a planted divergence rather than
    # trusting that today's surfaces happen to agree.
    saved = dict(SURFACES)
    try:
        for s in PARITY_SURFACES:
            SURFACES[s] = lambda _u, _c=ROOT: "load 03-skills/qa/SKILL.md"
        expect("parity passes when every parity surface delivers the same set",
               not evaluate_case({"id": "p", "utterance": "x", "parity": True}))
        SURFACES["codex"] = lambda _u, _c=ROOT: "load 03-skills/qa/SKILL.md and 08-knowledge/design/extra.md"
        planted = evaluate_case({"id": "p", "utterance": "x", "parity": True})
        expect("parity fails on a planted divergence in the third surface", planted)
        expect("the divergence message names the offending path",
               any("extra.md" in f for f in planted))

        def writer(_u, cwd=ROOT):
            (cwd / "planted.txt").write_text("x", encoding="utf-8")
            return ""
        SURFACES["cursor"] = writer
        wrote = evaluate_case({"id": "w", "utterance": "x", "surfaces": ["cursor"], "cwd": "employer-shaped"})
        (sandbox().employer / "planted.txt").unlink(missing_ok=True)
        expect("a delivery that writes into the employer cwd fails", any("wrote into" in f for f in wrote))
        SURFACES["cursor"] = lambda _u, _c=ROOT: f"see {EMPLOYER_SENTINEL}"
        leak = evaluate_case({"id": "l", "utterance": "x", "surfaces": ["cursor"], "cwd": "employer-shaped"})
        expect("employer-repo content in the payload fails", any("employer-repo content" in f for f in leak))
    finally:
        SURFACES.clear()
        SURFACES.update(saved)

    expect("a literal reader with no named route source delivers nothing",
           literal_read(["PERPLEXITY.md"], "run the harness map") == "" or
           "trigger-routes" in (ROOT / "PERPLEXITY.md").read_text(encoding="utf-8"))
    expect("the digest reader matches a trigger literally",
           "03-skills/harness-map/SKILL.md" in literal_read([DIGEST_REL], "map the harness before cleaning"))

    with tempfile.TemporaryDirectory(prefix="traj-st-") as td:
        tmp = Path(td)
        (tmp / "09-tools").mkdir()
        (tmp / "09-tools" / "cursor-prompt-route.py").write_text(
            "import prompt_route\ndef _registry_trigger_hits(p):\n    return []\n", encoding="utf-8")
        (tmp / "09-tools" / "ws_hook.py").write_text("x = 'prompt_route.py'\n", encoding="utf-8")
        (tmp / "00-bootstrap" / "dist").mkdir(parents=True)
        (tmp / "00-bootstrap" / "dist" / "ws").write_text("#!/bin/sh\n", encoding="utf-8")
        (tmp / ".claude").mkdir()
        (tmp / ".claude" / "settings.json").write_text(json.dumps(
            {"hooks": {"UserPromptSubmit": [{"hooks": [{"command": "python3 my-own-matcher.py"}]}]}}), encoding="utf-8")
        forked = check_one_matcher(tmp, {"commands": {}})
        expect("one-matcher guard fails on a shim that defines a matcher internal",
               any("defines `_registry_trigger_hits`" in f for f in forked))
        expect("one-matcher guard fails when `ws route` does not exec prompt_route",
               any("ws route" in f for f in forked))
        expect("one-matcher guard fails on an undeclared user-prompt command",
               any("undeclared command" in f for f in forked))
        (tmp / ".cursor" / "rules").mkdir(parents=True)
        (tmp / ".cursor" / "rules" / "brain.mdc").write_text("no steer here\n", encoding="utf-8")
        steer_fails, _ = check_steers(tmp)
        expect("a brain.mdc without the steer fails", bool(steer_fails))

    expect("one-matcher guard passes on the live entry points", not check_one_matcher())
    expect("hookless adapter check passes on the live adapters", not check_hookless_adapters())
    expect("the route digest is in sync", not check_digest())

    for name in failures:
        print(f"  ✗ {name}")
    if failures:
        print(f"FAIL surface-trajectories self-test — {len(failures)} assertion(s)")
        return 1
    print("OK surface-trajectories self-test")
    return 0


# ---------------------------------------------------------------------------- main

def load_corpus() -> list[dict]:
    if not CORPUS.exists():
        return []
    return [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("//")]


def show_utterance(utterance: str) -> None:
    for surface, fn in SURFACES.items():
        payload = fn(utterance, ROOT)
        print(f"\n### {surface} — {len(_paths(payload))} path(s)")
        print(payload.strip() or "(no injection)")
    sets = {s: _paths(SURFACES[s](utterance, ROOT)) for s in PARITY_SURFACES}
    base = sets[PARITY_SURFACES[0]]
    diff = set().union(*(base ^ v for v in sets.values()))
    print(f"\nparity({' vs '.join(PARITY_SURFACES)}): " + ("OK" if not diff else f"DIVERGENT {sorted(diff)}"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="CI gate: exit 1 on any failure")
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    ap.add_argument("--utterance", help="show what every surface delivers for one utterance")
    ap.add_argument("--self-test", action="store_true", help="prove the assertions can fail")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if args.utterance:
        show_utterance(args.utterance)
        return 0

    cases = load_corpus()
    if not cases:
        print(f"surface-trajectories: no corpus at {CORPUS.relative_to(ROOT)}", file=sys.stderr)
        return 2

    failures: list[str] = []
    for case in cases:
        failures.extend(evaluate_case(case))
    struct_fails, pending = structural()
    failures.extend(struct_fails)

    if args.json:
        print(json.dumps({"cases": len(cases), "parity_surfaces": list(PARITY_SURFACES),
                          "failures": failures, "pending": pending}, indent=2))
    else:
        for f in failures:
            print(f"  ✗ {f}")
        for p in pending:
            print(f"  … PENDING {p}")
        surfaces = ", ".join(SURFACES)
        if failures:
            print(f"FAIL {len(failures)} trajectory failure(s) over {len(cases)} case(s) "
                  f"[{surfaces}] + structure")
        else:
            print(f"OK {len(cases)} trajectory case(s) across {surfaces} + structure; "
                  f"parity over {', '.join(PARITY_SURFACES)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
