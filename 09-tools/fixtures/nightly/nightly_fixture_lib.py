"""Shared helpers for the nightly.py and dispatcher.py self-tests (H1, wave 0).

Everything here is hermetic: temp repos, a temp HOME, stubbed launchctl/gh/osascript/
claude first on PATH, and every host marker or GIT_* variable stripped from the child
environment. Synthetic data only; nothing reads the real vault except the generator
scripts copied into a temp vault.

Fake resolver modules (ws_hook, profile_resolve) are written as source text into a temp
repo's 09-tools/ and export their functions through a registration table, so no second
top-level definition of a contract helper exists in a tracked file (3d single sources).
"""

from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAYLOADS = HERE / "payloads"

_MARKER_PREFIXES = ("GIT_", "CLAUDE", "CURSOR", "CODEX", "WS_", "GH_", "VSCODE", "TERM_PROGRAM",
                    "GEMINI", "COPILOT", "AI_AGENT", "WINDSURF", "GROK", "AIDER", "GOOSE",
                    "OPENCODE")
STUBS = ("launchctl", "gh", "osascript", "claude")
FIXTURE_IDENTITY = {"GIT_AUTHOR_NAME": "Fixture Author", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
                    "GIT_COMMITTER_NAME": "Fixture Author",
                    "GIT_COMMITTER_EMAIL": "fixture@example.invalid"}


class Checks:
    """Tiny assertion collector: every check prints one line; run() returns 0 or 1."""

    def __init__(self, title: str) -> None:
        self.title = title
        self.failed: list[str] = []
        self.passed = 0

    def check(self, cond: bool, label: str, detail: str = "") -> bool:
        if cond:
            self.passed += 1
            print(f"  ok   {label}")
        else:
            self.failed.append(label)
            print(f"  FAIL {label}" + (f" — {detail}" if detail else ""))
        return bool(cond)

    def result(self) -> int:
        total = self.passed + len(self.failed)
        verdict = "PASS" if not self.failed else "FAIL"
        print(f"{self.title}: {verdict} — {self.passed}/{total} checks")
        return 0 if not self.failed else 1


def make_stubs(base: Path) -> Path:
    """Stub binaries that record a call and exit 0. `claude --version` prints a fixed string."""
    stub_dir = base / "stub-bin"
    stub_dir.mkdir(parents=True, exist_ok=True)
    for name in STUBS:
        p = stub_dir / name
        extra = 'echo "0.0.0 (fixture)"\n' if name == "claude" else ""
        p.write_text(f'#!/bin/sh\necho "$0 $*" >> "{stub_dir}/calls-{name}"\n{extra}exit 0\n',
                     encoding="utf-8")
        p.chmod(0o755)
    return stub_dir


def stub_calls(stub_dir: Path, name: str) -> int:
    f = stub_dir / f"calls-{name}"
    return len(f.read_text(encoding="utf-8").splitlines()) if f.is_file() else 0


def hermetic_env(home: Path, stub_dir: Path, extra: dict | None = None) -> dict:
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(_MARKER_PREFIXES) and k not in ("CI", "GITHUB_ACTIONS")}
    env["HOME"] = str(home)
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["PATH"] = str(stub_dir) + os.pathsep + env.get("PATH", "")
    env.update(FIXTURE_IDENTITY)
    if extra:
        env.update(extra)
    return env


def git(repo: Path, *args: str, env: dict, check: bool = True, input_text: str | None = None,
        timeout: float = 30) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *args], cwd=str(repo), env=env, capture_output=True, text=True,
                       input=input_text, timeout=timeout)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r


def py(script: Path, *args: str, cwd: Path, env: dict, stdin: str = "",
       timeout: float = 120) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script), *args], cwd=str(cwd), env=env,
                          input=stdin, capture_output=True, text=True, timeout=timeout)


def payload(name: str) -> dict:
    return json.loads((PAYLOADS / f"{name}.json").read_text(encoding="utf-8"))


# ---------- synthetic vault (real generators, synthetic skills) ----------

GITIGNORE = (".workspace/\n.claude/state/\n.claude/worktrees/\n"
             "06-context/sessions/*.touched\n06-context/sessions/*.dirty\n")

SKILLS = {
    "alpha": ("cross-cutting", "alpha-topic"),
    "beta": ("cross-cutting", "beta-topic"),
    "gamma": ("hub", "gamma-topic"),
}
GENERATORS = ("build-registry.py", "build-related.py", "build-trigger-routes.py")
EDGE_LINE = "governed_by: [alpha]\n"


def skill_text(name: str, tier: str, trigger: str) -> str:
    return (f"---\nname: {name}\ndescription: Fixture skill {name}.\ntier: {tier}\n"
            f"triggers: [{trigger}]\n---\n\n# {name}\n\nFixture body for {name}.\n")


def add_edge(vault: Path) -> Path:
    """The X1 edit: beta gains a governed_by edge to alpha (a graph edge that makes
    build-related rewrite BOTH Related blocks and changes the registry twice)."""
    p = vault / "03-skills" / "beta" / "SKILL.md"
    text = p.read_text(encoding="utf-8")
    p.write_text(text.replace("tier: cross-cutting\n", "tier: cross-cutting\n" + EDGE_LINE, 1),
                 encoding="utf-8")
    return p


def build_vault(dest: Path, tools_src: Path, env: dict) -> Path:
    """A committed temp vault with the real nightly.py + generators and three skills."""
    (dest / "09-tools").mkdir(parents=True)
    for name in ("nightly.py", *GENERATORS):
        shutil.copy2(tools_src / name, dest / "09-tools" / name)
    (dest / "AGENTS.md").write_text("# fixture vault\n", encoding="utf-8")
    (dest / ".gitignore").write_text(GITIGNORE, encoding="utf-8")
    (dest / "notes.md").write_text("fixture notes\n", encoding="utf-8")
    for name, (tier, trig) in SKILLS.items():
        d = dest / "03-skills" / name
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(skill_text(name, tier, trig), encoding="utf-8")
    refs = dest / "02-shared-references"
    refs.mkdir(parents=True)
    (refs / "trigger-routes.json").write_text(json.dumps(
        {"templates": {}, "routes": {"alpha topic": "03-skills/alpha/SKILL.md"}}, indent=2) + "\n",
        encoding="utf-8")
    (dest / "06-context" / "sessions").mkdir(parents=True)
    (dest / "06-context" / "sessions" / ".keep").write_text("", encoding="utf-8")
    for gen in ("build-registry.py", "build-related.py", "build-registry.py", "build-trigger-routes.py"):
        r = py(dest / "09-tools" / gen, cwd=dest, env=env)
        if r.returncode != 0:
            raise RuntimeError(f"fixture vault: {gen} failed: {r.stderr.strip()}")
    git(dest, "init", "-q", "-b", "main", env=env)
    git(dest, "add", "-A", env=env)
    git(dest, "commit", "-q", "-m", "fixture: base vault", env=env)
    return dest


def clone(base: Path, dest: Path, env: dict) -> Path:
    git(base.parent, "clone", "-q", str(base), str(dest), env=env)
    return dest


def archive_tree(repo: Path, dest: Path, env: dict) -> Path:
    """`git archive HEAD` extracted to dest (the committed tree, nothing else)."""
    r = subprocess.run(["git", "archive", "--format=tar", "HEAD"], cwd=str(repo), env=env,
                       capture_output=True, timeout=30)
    if r.returncode != 0:
        raise RuntimeError("git archive failed")
    dest.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(r.stdout)) as tf:
        try:
            tf.extractall(dest, filter="data")
        except TypeError:  # Python < 3.12 without the filter backport
            tf.extractall(dest)  # noqa: S202 — our own fixture archive
    return dest


def hook_dir(base: Path, repo_python: str = sys.executable) -> Path:
    """A core.hooksPath directory whose pre-commit runs the nightly lane."""
    d = base / "hooks"
    d.mkdir(parents=True, exist_ok=True)
    hook = d / "pre-commit"
    hook.write_text(f'#!/bin/sh\nexec "{repo_python}" 09-tools/nightly.py --lane pre-commit\n',
                    encoding="utf-8")
    hook.chmod(0o755)
    return d


# ---------- fake resolver modules (contract-shaped; 3d signatures) ----------

FAKE_WS_HOOK = '''"""FAKE ws_hook for T5 self-tests (contract 3d shape only)."""
import json
from pathlib import Path


def _hint(payload):
    if not isinstance(payload, dict):
        return None
    if "cursor_version" in payload:
        return "cursor"
    if "hookEventName" in payload and "sessionId" in payload:
        return "copilot-vscode"
    if "hook_event_name" in payload and "session_id" in payload:
        return "claude-code"
    return None


def _baseline(payload, root):
    d = Path(root) / ".workspace" / "state" / "sessions"
    d.mkdir(parents=True, exist_ok=True)
    sid = str(payload.get("session_id") or "none")
    out = d / (sid + ".json")
    out.write_text(json.dumps({"schema_version": 1, "sid": sid, "porcelain": []}) + "\\n")
    return out


_EXPORTS = {"payload_host_hint": _hint, "write_baseline": _baseline}
globals().update(_EXPORTS)
'''

FAKE_PROFILE_RESOLVE = '''"""FAKE profile_resolve for T5 self-tests (contract 3d shape only)."""
import json
import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_FIXTURE_HOST = "host-a.local"
_ENV_MARKERS = {"CURSOR_AGENT": ("cursor", True), "CODEX_THREAD_ID": ("codex", False)}


def _mark_called():
    d = _ROOT / ".workspace"
    d.mkdir(parents=True, exist_ok=True)
    (d / "detect-called").write_text("1\\n")


def _detect(payload_hint=None, *, env=None, ancestry=None, isatty=None, root=None):
    _mark_called()
    if payload_hint:
        return {"acting_host": payload_hint, "family": payload_hint, "family_for_walls": payload_hint,
                "via": "payload", "verified": True, "determined": True}
    env = os.environ if env is None else env
    for name, (host, verified) in _ENV_MARKERS.items():
        if env.get(name):
            return {"acting_host": host, "family": host, "family_for_walls": host, "via": "env",
                    "verified": verified, "determined": True}
    return {"acting_host": "unknown", "family": "unknown-agent", "via": "none",
            "verified": False, "determined": False}


def _devices():
    return json.loads((_ROOT / "02-shared-references" / "devices.json").read_text())


def _label(hostname=None, *, root=None):
    short = (hostname or _FIXTURE_HOST).split(".")[0]
    for d in _devices().get("devices", []):
        if short.casefold() in [h.casefold() for h in d.get("hostnames", [])]:
            return d.get("hostname_labels", {}).get(short) or d.get("label") or short
    return short


def _current(*, hostname=None, root=None, scutil=None):
    short = (hostname or _FIXTURE_HOST).split(".")[0]
    for d in _devices().get("devices", []):
        if short.casefold() in [h.casefold() for h in d.get("hostnames", [])]:
            return {"id": d["id"], "label": d["label"], "hostname_known": True, "notice": ""}
    return {"id": "unknown", "label": short, "hostname_known": False, "notice": "unknown host"}


_EXPORTS = {"detect_surface": _detect, "device_label": _label, "current_device": _current}
globals().update(_EXPORTS)
'''

FIXTURE_DEVICES = {
    "schema_version": 1,
    "doc": "Synthetic device table for T5 self-tests.",
    "devices": [
        {"id": "dev-a", "label": "Fixture Device A", "hostnames": ["host-a"], "hostname_labels": {},
         "os": "macos", "projects_root": "Projects", "brain": "Projects/workspace"},
        {"id": "dev-b", "label": "Fixture Device B", "hostnames": ["host-b"], "hostname_labels": {},
         "os": "macos", "projects_root": "Projects", "brain": "Projects/Workspace"},
    ],
    "ssh_aliases": [],
}


def install_fakes(repo: Path, *, ws_hook: bool = True, profile_resolve: bool = True) -> None:
    tools = repo / "09-tools"
    tools.mkdir(parents=True, exist_ok=True)
    if ws_hook:
        (tools / "ws_hook.py").write_text(FAKE_WS_HOOK, encoding="utf-8")
    if profile_resolve:
        (tools / "profile_resolve.py").write_text(FAKE_PROFILE_RESOLVE, encoding="utf-8")
        refs = repo / "02-shared-references"
        refs.mkdir(parents=True, exist_ok=True)
        (refs / "devices.json").write_text(json.dumps(FIXTURE_DEVICES, indent=2) + "\n",
                                           encoding="utf-8")
