#!/usr/bin/env python3
"""wall_guard.py — the workspace-owned, LLM-agnostic wall guard (H15).

One decide() over the action-policy table, reached from every hooked host through a generated shim.
Hosts differ only in how a payload arrives and how a decision is rendered; the rules are the same:

  R1  a Claude-family process in the chain: the action-policy rules P10-P22 (employer targets route
      to Cursor or Codex, merge is human-only, model-composed meta and housekeeping name the vetted
      script, a target that is not positively personal is refused). The Claude-only static file rules
      for employer vault folders are mirrored here for the file and MCP tools.
  R2  non-Claude agents on employer repos (P30-P32, P40): branch -> PR -> human review.
  R3  I1: a personal effective identity never commits on an employer repo (any family).
  R4  an unknown or conflicted repo for a non-Claude agent: ask where the host can, deny elsewhere.
  R6  tamper (every family, every profile): hook skips and config bypasses (P05), git config and
      identity env, WS_*, GH_CONFIG_DIR and HOME, git config writes of hook/hooksPath/include keys,
      and writes to the git, Cursor, Codex and workspace control files; Claude settings files ask.
  R6c candidate tamper shapes (repo aliases, URL rewrites and identity keys written to git config, and
      agent edits of .git/config, .git/hooks, the pinned lib and the hook scripts): report-only
      labels until Sean decides to enforce them.
  R7  a Claude chain launching another agent CLI or app: denied for employer targets, else a notice.

Which rules enforce and which only log a would-deny is data: surfaces.json `wall_guard.rules`
(R1, R3 and R6 enforce from install; R2, R4, R6c and R7 are report-only during the rollout window).
A route renders as deny plus a handoff line. No environment variable ever turns a deny into an allow.

A detection discount (walls lower than the env and ancestry evidence alone give) needs verified
evidence: a host hook payload whose marker surfaces.json declares verified (D-W1-3). An env var
alone never lowers the walls; an inherited Claude overlay keeps them at claude.

Fail-open (declared, H17-R8 class): a missing table, an import failure, an exception or a timeout
gives no decision (exit 0). Inside decide(), text it cannot follow fails closed: an unparseable
command is the unknown-verb class and an unfollowable cd is the most restrictive target.

Usage:
  wall_guard.py hook --host HOST|auto              stdin: the host's pre-tool payload JSON
  wall_guard.py decide --host HOST --command TEXT [--cwd DIR] [--json]
  wall_guard.py decide --host HOST --path PATH [--write] [--json]
  wall_guard.py report [--days N] [--json]          would-deny counts from the decision log
  wall_guard.py probe-setup                         human: create the probe scratch repos
  wall_guard.py probe-record --host HOST [--device ID]   human: write the live probe record
  wall_guard.py --self-test

Exit: hook 0 (a decision is in the output), 2 on a Codex or Windsurf deny (their block contract);
decide 0 allow, 1 deny/ask/route, 2 usage; report/probe 0 ok, 1 fail, 2 usage.
Stdlib only; python3 3.9+. Nothing here is auto-loaded.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shlex
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
FIXTURES = TOOLS / "fixtures" / "wall_guard"
SCHEMA_VERSION = 1

HOOK_BUDGET_S = 4.5
NO_TTY = {"stdin": False, "stdout": False}
RULE_IDS = ("R1", "R2", "R3", "R4", "R6", "R6c", "R7")
DEFAULT_MODES = {"R1": "enforce", "R2": "report", "R3": "enforce", "R4": "report", "R6": "enforce",
                 "R6c": "report", "R7": "report"}
RANK = {"none": 0, "allow": 0, "ask": 1, "route": 2, "deny": 3}
LOG_NAME = "wall-guard.jsonl"
PROBE_MARK_RE = re.compile(r"wallguard-probe-([A-Za-z0-9]{1,24})")
REDACT_RE = re.compile(r"^[A-Za-z0-9_.:+ ()-]{0,80}$")

# --- R6: tamper vocabulary (every family, every profile) -----------------------------------------
TAMPER_ENV_EXACT = ("GIT_CONFIG_COUNT", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM",
                    "GIT_CONFIG_SYSTEM", "GH_CONFIG_DIR", "HOME")
TAMPER_ENV_PREFIXES = ("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_", "GIT_AUTHOR_", "GIT_COMMITTER_", "WS_")
TAMPER_CFG_PREFIXES = ("hook.", "url.", "include.", "includeif.", "user.")
TAMPER_CFG_EXACT = ("core.hookspath",)
CONFIG_WRITE_DENY_PREFIXES = ("hook.", "include.", "includeif.")
CONFIG_WRITE_DENY_EXACT = ("core.hookspath",)
CONFIG_WRITE_REPORT_PREFIXES = ("url.", "alias.", "user.")
# home-relative files an agent never writes (R6) or writes only with Sean's approval (ask)
PROTECTED_DENY = (".gitconfig", ".config/snds-workspace/control", ".cursor/hooks.json", ".codex/hooks.json",
                  ".codex/config.toml")
PROTECTED_ASK_RE = re.compile(r"^\.claude/settings[^/]*\.json$")
PROTECTED_REPORT = (".config/git", ".config/snds-workspace/lib", ".config/snds-workspace/bin", ".claude/hooks",
                    ".cursor/hooks", ".codex/rules")
GIT_CONFIG_READ_FLAGS = frozenset({"--get", "--get-all", "--get-regexp", "--get-urlmatch", "-l", "--list",
                                   "--show-origin", "--show-scope", "--name-only", "--get-color",
                                   "--get-colorbool", "-e", "--edit"})
GIT_CONFIG_WRITE_FLAGS = frozenset({"--add", "--replace-all", "--unset", "--unset-all", "--rename-section",
                                    "--remove-section"})
GIT_CONFIG_VALUE_OPTS = frozenset({"-f", "--file", "--blob", "--type", "--default", "--comment", "--value"})
COMMIT_VERBS = frozenset({"commit", "merge", "cherry-pick", "revert", "rebase", "am", "pull"})
NETWORK_VERBS = {"push": "publish", "send-pack": "publish", "fetch": "content-read", "pull": "content-read",
                 "clone": "content-read", "ls-remote": "content-read", "archive": "content-read"}
LAUNCH_CLIS = frozenset({"codex", "cursor", "agent", "cursor-agent", "code", "code-insiders"})
LAUNCH_APPS = ("Cursor", "Codex", "ChatGPT", "Visual Studio Code", "Code")
WRITE_TOOLS = {"tee": "all", "touch": "all", "truncate": "all", "rm": "all", "unlink": "all", "rmdir": "all",
               "shred": "all", "cp": "last", "mv": "last", "install": "last", "ln": "last", "rsync": "last"}
# wrappers that only change how a program runs; the program after them is what the guard judges
WRAPPERS = {"command": frozenset(), "builtin": frozenset(), "nohup": frozenset(), "time": frozenset(),
            "exec": frozenset({"-a"}), "nice": frozenset({"-n"}), "xargs": frozenset({"-n", "-I", "-P", "-L", "-d",
                                                                                      "-E", "-s", "-a"}),
            "stdbuf": frozenset({"-o", "-e", "-i"}), "caffeinate": frozenset({"-t", "-w"}),
            "sudo": frozenset({"-u", "-g", "-h", "-p", "-C", "-D", "-U", "-r", "-t"}), "doas": frozenset({"-u", "-C"}),
            "timeout": frozenset({"-s", "-k", "--signal", "--kill-after"}), "unbuffer": frozenset()}
KEYWORDS = frozenset({"if", "then", "else", "elif", "do", "while", "until", "!", "done", "fi", "esac"})
SHELLS = frozenset({"sh", "bash", "zsh", "dash", "ksh"})
PY_RE = re.compile(r"^python(?:3(?:\.\d+)?)?$")
PY_VALUE_OPTS = frozenset({"-W", "-X", "--check-hash-based-pycs"})

# Codex rules, Claude Bash rules, and the Warp / Zed / OpenCode lists are all rendered from these
# argv prefixes. Every prefix is one the core denies (R6), so no belt is stricter than the core.
# Shapes a prefix cannot express without also matching a read the core allows (a bare
# `git config <key>` read, any `git -c <key>=<value>` spelled differently) stay with the core.
BELT_INVARIANTS: List[dict] = [
    {"id": "hook-skip", "argv": [["git"], ["commit", "push", "merge"], ["--no-verify", "--no-verif", "--no-veri"]],
     "why": "git's hook-skip option skips the workspace git floor (R6)"},
    {"id": "commit-n", "argv": [["git"], ["commit"], ["-n"]],
     "why": "git commit -n skips the commit hooks (R6)"},
    {"id": "floor-off", "argv": [["git"], ["-c"], ["hook.ws-claude-wall.enabled=false"]],
     "why": "switches the workspace git floor off for one command (R6)"},
    {"id": "config-count", "argv": [["GIT_CONFIG_COUNT=0"]],
     "why": "drops the overlay's env-scope git config for one command (R6)"},
    {"id": "env-scrub", "argv": [["env"], ["-i"]],
     "why": "scrubs the environment the walls live in (R6)"},
]
STRICTER_BELTS_DECLARED: List[str] = []   # belts allowed to be stricter than the core (expected empty)


# --------------------------------------------------------------------------- imports + tables

_PR = None          # test seam
_PR_CACHE: dict = {}


def _pr():
    """The sibling profile_resolve module (the pinned lib's copy in production), or None."""
    if _PR is not None:
        return _PR
    if "mod" in _PR_CACHE:
        return _PR_CACHE["mod"]
    try:
        if str(TOOLS) not in sys.path:
            sys.path.insert(0, str(TOOLS))
        import profile_resolve  # noqa: PLC0415
        mod = profile_resolve
    except BaseException:  # noqa: BLE001 - a broken pinned module must never block a host
        sys.modules.pop("profile_resolve", None)
        mod = None
    _PR_CACHE["mod"] = mod
    return mod


def _surfaces(root: Optional[Path]) -> Optional[dict]:
    pr = _pr()
    if pr is None:
        return None
    try:
        t = pr.load_table("surfaces", root=root)
    except Exception:  # noqa: BLE001
        return None
    return t if isinstance(t, dict) else None


def guard_config(t: Optional[dict]) -> dict:
    cfg = dict((t or {}).get("wall_guard") or {})
    modes = dict(DEFAULT_MODES)
    for k, v in (cfg.get("rules") or {}).items():
        if k in modes and v in ("enforce", "report"):
            modes[k] = v
    cfg["rules"] = modes
    cfg.setdefault("host_overrides", {})
    return cfg


def rule_mode(cfg: dict, rule: str, host: str) -> str:
    over = ((cfg.get("host_overrides") or {}).get(host) or {}).get(rule)
    if over in ("enforce", "report"):
        # a host override may only flip a report-only rule to enforce, never relax an enforced one
        if cfg["rules"].get(rule) == "enforce":
            return "enforce"
        return over
    return cfg["rules"].get(rule, "enforce")


def _row(t: Optional[dict], sid: Optional[str]) -> Optional[dict]:
    for s in (t or {}).get("surfaces") or []:
        if isinstance(s, dict) and s.get("id") == sid:
            return s
    return None


def payload_hint(payload: dict, t: Optional[dict]) -> Tuple[Optional[str], bool]:
    """(surface id whose declared payload keys are present, whether that marker is verified).

    Only a unique hit counts, as in ws_hook.payload_host_hint."""
    if not isinstance(payload, dict) or not payload or not t:
        return None, False
    hits: List[Tuple[str, bool]] = []
    for s in t.get("surfaces") or []:
        for m in (s.get("markers") or {}).get("payload_keys_any") or []:
            key = m.get("key")
            if key not in payload:
                continue
            needle = m.get("contains")
            if needle is not None and needle not in str(payload.get(key) or ""):
                continue
            if s["id"] not in [h[0] for h in hits]:
                hits.append((s["id"], bool(m.get("verified"))))
            break
    return hits[0] if len(hits) == 1 else (None, False)


def own_guard_hosts(t: Optional[dict]) -> set:
    """Hosts with their own wall-guard registration (the `--host X` of a wall-guard command)."""
    out = set()
    cmds = (t or {}).get("commands") or {}
    for name, c in cmds.items():
        if isinstance(c, dict) and c.get("behaviour") == "wall-guard":
            m = re.search(r"--host\s+([a-z0-9-]+)", str(c.get("template") or ""))
            if m and m.group(1) != "auto":
                out.add(m.group(1))
    return out


# --------------------------------------------------------------------------- detection (walls)

def detect(declared: str, payload: dict, *, env: dict, ancestry: Optional[list], root: Optional[Path],
           t: dict) -> dict:
    """The resolver's detection, plus a discount that only verified host evidence can grant (D-W1-3)."""
    pr = _pr()
    hint, verified = payload_hint(payload, t)
    det = dict(pr.detect_surface(hint, env=env, ancestry=ancestry, isatty=NO_TTY, root=root))
    fams = t.get("families") or {}
    det["payload_host"], det["payload_verified"] = hint, verified
    det["declared_host"] = declared
    det["notices"] = []
    rank = lambda f: (fams.get(f) or {}).get("wall_rank", 100)  # noqa: E731 - unknown family ranks highest
    if hint and verified:
        hfam = (_row(t, hint) or {}).get("family")
        chain = [{"comm": c} for c in det.get("chain") or []]
        cands = [hfam] + [a["family"] for a in pr._ancestry_matches(pr._norm_chain(chain), t)]
        cands += [m["family"] for m in pr._env_markers(env, t)]
        wsf = env.get("WS_SURFACE_FAMILY")
        if wsf in fams:
            cands.append(wsf)
        if env.get("WS_CLAUDE_OVERLAY"):
            cands.append("claude")          # an inherited Claude overlay is Claude evidence, never discounted
        cands = [c for c in cands if c in fams]
        walls = max(cands, key=rank) if cands else det.get("family_for_walls")
        if walls and rank(walls) < rank(det.get("family_for_walls") or "unknown"):
            det["discount"] = {"from": det.get("family_for_walls"), "to": walls,
                               "evidence": f"verified host payload ({hint})"}
            det["family_for_walls"] = walls
            det["agent_possible"] = False   # the agent-possible names are explained by the verified host
            det["conflict"] = walls != det.get("family")
    if det.get("conflict"):
        det["notices"].append(f"conflict: acting {det.get('family')} but walls {det.get('family_for_walls')} "
                              "(an inherited overlay or ancestry outranks the host)")
    return det


# --------------------------------------------------------------------------- payload -> actions

def _tool_families(t: Optional[dict]) -> List[dict]:
    return [f for f in (t or {}).get("tool_families") or [] if isinstance(f, dict)]


def _split_tool(name: str) -> Tuple[Optional[str], str]:
    m = re.match(r"^mcp__(.+?)__(.+)$", name or "")
    return (m.group(1), m.group(2)) if m else (None, name or "")


def _jsonish(v: Any) -> Any:
    if isinstance(v, str) and v.strip()[:1] in ("{", "["):
        try:
            return json.loads(v)
        except ValueError:
            return v
    return v


def _first(d: dict, keys: List[str]) -> Any:
    for k in keys:
        if isinstance(d, dict) and d.get(k) not in (None, ""):
            return d[k]
    return None


def _patch_paths(text: str) -> List[str]:
    out = []
    for line in str(text or "").splitlines():
        m = re.match(r"^\*\*\* (?:Add File|Update File|Delete File|Move to): (.+)$", line.strip())
        if m:
            out.append(m.group(1).strip())
    return out


def extract(payload: dict, t: Optional[dict]) -> Tuple[str, str, List[dict], Optional[str]]:
    """(raw event, tool name, actions, cwd) from any host's pre-tool payload.

    An action is {kind: shell, command} | {kind: file, op, path} | {kind: mcp, server, tool, owner_class,
    family} | {kind: url, url}. Unknown tools give no actions (no decision)."""
    p = payload if isinstance(payload, dict) else {}
    event = str(p.get("hook_event_name") or p.get("hookEventName") or p.get("agent_action_name")
                or p.get("hookName") or "")
    info = p.get("tool_info") if isinstance(p.get("tool_info"), dict) else {}
    nested = p.get("preToolUse") if isinstance(p.get("preToolUse"), dict) else {}
    tool = str(p.get("tool_name") or p.get("toolName") or nested.get("toolName") or "")
    tin = _jsonish(p.get("tool_input") if "tool_input" in p else p.get("toolInput", p.get("toolArgs")))
    if not isinstance(tin, dict):
        tin = _jsonish(nested.get("parameters")) if nested else {}
    tin = tin if isinstance(tin, dict) else {}
    cwd = p.get("cwd") or info.get("cwd") or _first(tin, ["cwd", "workdir", "directory"])
    if not cwd and isinstance(p.get("workspace_roots"), list) and p["workspace_roots"]:
        cwd = p["workspace_roots"][0]
    fams = _tool_families(t)
    actions: List[dict] = []
    # host events that carry the command or file directly (Cursor beforeShellExecution, Windsurf)
    if event == "beforeShellExecution" or (not tool and p.get("command") and event != "beforeMCPExecution"):
        return event, tool or "Shell", [{"kind": "shell", "command": str(p.get("command") or "")}], cwd
    if event == "pre_run_command" or info.get("command_line"):
        return event, tool or "pre_run_command", [{"kind": "shell", "command": str(info.get("command_line") or "")}], cwd
    if event in ("pre_write_code", "pre_read_code") and info.get("file_path"):
        op = "write" if event == "pre_write_code" else "read"
        return event, tool or event, [{"kind": "file", "op": op, "path": str(info["file_path"])}], cwd
    server, bare = _split_tool(tool)
    if event == "beforeMCPExecution" and not server:
        server = str(p.get("server") or p.get("server_name") or "") or None
    by_id = {f.get("id"): f for f in fams}
    shell = by_id.get("shell") or {}
    if bare in (shell.get("names") or []) or any(tool.endswith(s) for s in shell.get("mcp_suffixes") or []):
        cmd = _first(tin, list(shell.get("command_keys") or ["command"]))
        if isinstance(cmd, list):
            cmd = shlex.join(str(x) for x in cmd)
        if cmd:
            actions.append({"kind": "shell", "command": str(cmd)})
        wd = _first(tin, list(shell.get("cwd_keys") or ["cwd", "workdir"]))
        return event, tool, actions, str(wd) if wd else cwd
    for fam in fams:
        if fam.get("kind") in ("mcp", "url") and server and fam.get("server") == server:
            if fam["kind"] == "url":
                url = _first(tin, list(fam.get("url_keys") or ["url"]))
                if url:
                    actions.append({"kind": "url", "url": str(url), "family": fam.get("id"),
                                    "rollout": fam.get("rollout")})
                return event, tool, actions, cwd
            actions.append({"kind": "mcp", "server": server, "tool": bare, "family": fam.get("id"),
                            "owner_class": fam.get("owner_class"), "rollout": fam.get("rollout"),
                            "op": "write" if re.match(r"^(save|create|update|delete|merge|submit|set|add|remove|"
                                                      r"resolve|mark|retire|restore|share|unshare|transition|edit)",
                                                      bare) else "read"})
            return event, tool, actions, cwd
    for fam in fams:
        if fam.get("kind") != "file" or bare not in (fam.get("names") or []):
            continue
        keys = list(fam.get("path_keys") or ["file_path", "path"])
        paths: List[str] = []
        for k in keys:
            v = tin.get(k)
            if isinstance(v, str) and v:
                paths.append(v)
            elif isinstance(v, list):
                paths += [str(x) for x in v if isinstance(x, str) and x]
        if bare == "apply_patch":
            paths += _patch_paths(_first(tin, ["patch", "input", "command"]) or "")
        for path in dict.fromkeys(paths):
            actions.append({"kind": "file", "op": fam.get("op", "write"), "path": path})
        if bare == "apply_patch" and not paths:
            actions.append({"kind": "file", "op": "write", "path": None})
        return event, tool, actions, cwd
    return event, tool, actions, cwd


# --------------------------------------------------------------------------- shell analysis

def _expand(p: str, home: Path, cwd: Optional[str]) -> Optional[str]:
    if not p:
        return None
    s = p
    for pre in ("$HOME/", "${HOME}/"):
        if s.startswith(pre):
            s = str(home) + "/" + s[len(pre):]
    if s in ("$HOME", "${HOME}", "~"):
        s = str(home)
    if s.startswith("~/"):
        s = str(home) + s[1:]
    if "$" in s or "`" in s:
        return None
    if not os.path.isabs(s):
        if not cwd or cwd.startswith("\x00"):
            return None
        s = os.path.join(cwd, s)
    return os.path.normpath(s)


def _home_rel(path: str, home: Path) -> Optional[str]:
    cands = {os.path.normpath(str(home))}
    try:
        cands.add(os.path.realpath(str(home)))
    except OSError:
        pass
    pv = {path}
    try:
        pv.add(os.path.realpath(path))
    except OSError:
        pass
    for h in cands:
        for q in pv:
            if q.casefold() == h.casefold():
                return ""
            if q.casefold().startswith(h.casefold() + "/"):
                return q[len(h) + 1:]
    return None


def protected_class(path: Optional[str], home: Path) -> Optional[Tuple[str, str]]:
    """('deny'|'ask'|'report', reason) for a write to a protected file, else None."""
    if not path:
        return None
    rel = _home_rel(path, home)
    low = path.replace("\\", "/")
    if rel is not None:
        rl = rel.casefold()
        for d in PROTECTED_DENY:
            dl = d.casefold()
            if rl == dl or rl.startswith(dl + "/"):
                return "deny", f"~/{d} is a wall file; agents never write it"
        if PROTECTED_ASK_RE.match(rel):
            return "ask", f"~/{rel} holds Claude's hooks and permissions; Sean approves every write"
        for d in PROTECTED_REPORT:
            dl = d.casefold()
            if rl == dl or rl.startswith(dl + "/"):
                return "report", f"~/{d} carries the walls' code or config (candidate R6)"
    if re.search(r"(^|/)\.git/(config|hooks(/|$))", low):
        return "report", "a repository's .git/config or .git/hooks (candidate R6)"
    return None


def _strip_heredocs(text: str) -> str:
    """Drop here-document bodies, which are data, unless a shell reads them as a script."""
    lines = text.split("\n")
    out: List[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        m = re.search(r"<<(-?)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2", line)
        if m and not re.search(r"<<<", line[:m.start() + 3]):
            first = (line.strip().split() or [""])[0].rsplit("/", 1)[-1]
            if first in SHELLS or first == "eval":
                i += 1
                continue
            delim, dash = m.group(3), m.group(1) == "-"
            i += 1
            while i < len(lines):
                body = lines[i].lstrip("\t") if dash else lines[i]
                if body.strip() == delim:
                    break
                i += 1
        i += 1
    return "\n".join(out)


def _substitutions(tok: str) -> List[str]:
    """Inner scripts of $( ... ) and `...` inside one token."""
    out = []
    i = 0
    while i < len(tok):
        if tok.startswith("$(", i) and not tok.startswith("$((", i):
            depth, j = 1, i + 2
            while j < len(tok) and depth:
                if tok[j] == "(":
                    depth += 1
                elif tok[j] == ")":
                    depth -= 1
                j += 1
            out.append(tok[i + 2:j - 1] if depth == 0 else tok[i + 2:])
            i = j
            continue
        if tok[i] == "`":
            j = tok.find("`", i + 1)
            out.append(tok[i + 1:j] if j > 0 else tok[i + 1:])
            i = (j + 1) if j > 0 else len(tok)
            continue
        i += 1
    return [s for s in out if s.strip()]


def _is_tamper_env(name: str) -> bool:
    n = name.rstrip("+")
    return n in TAMPER_ENV_EXACT or n.startswith(TAMPER_ENV_PREFIXES)


def _cfg_key_tamper(item: str) -> bool:
    key = item.split("=", 1)[0].strip().casefold()
    return key.startswith(TAMPER_CFG_PREFIXES) or key in TAMPER_CFG_EXACT


class ShellScan:
    """What one command text does, as the guard needs it: normalized simple commands for the
    resolver's parser, plus the findings the parser does not label."""

    def __init__(self, home: Path, cwd: Optional[str]):
        self.home = home
        self.cwd0 = cwd
        self.simples: List[List[str]] = []
        self.tamper: List[str] = []           # R6 reasons
        self.candidates: List[str] = []       # R6c reasons
        self.writes: List[Tuple[str, Optional[str]]] = []   # (raw target, expanded path)
        self.vetted: List[dict] = []          # python invocations to check against the registry
        self.launches: List[dict] = []        # R7
        self.authors: List[str] = []          # --author values (R3)
        self.unparsed = False

    # -- entry
    def scan(self, text: str, depth: int = 0, env_prefix: Optional[List[str]] = None) -> None:
        pr = _pr()
        text = _strip_heredocs(text or "")
        tokens = pr._tokenize(text)
        if tokens is None:
            self.unparsed = True
            self.simples.append(["?unparsed"])
            return
        cwd = self.cwd0
        stack: List[bool] = []
        cur: List[str] = []
        groups: List[Tuple[List[str], Optional[str]]] = []
        for tk in tokens:
            if tk in pr._CTRL_TOKENS:
                if cur:
                    groups.append((cur, None))
                    cur = []
                if tk in ("(", ")", "{", "}"):
                    groups.append(([], tk))
                continue
            cur.append(tk)
        if cur:
            groups.append((cur, None))
        moved: List[bool] = [False]
        for simple, marker in groups:
            if marker in ("(", "{"):
                stack.append(moved[-1])
                moved.append(False)
                continue
            if marker in (")", "}"):
                inner = moved.pop() if len(moved) > 1 else False
                if marker == ")" and inner:
                    self.simples.append(["popd"])      # the subshell's cd cannot be followed: most restrictive
                if marker == "}" and inner:
                    moved[-1] = True
                if stack:
                    stack.pop()
                continue
            cwd, did_cd = self._simple(simple, depth, list(env_prefix or []), cwd)
            if did_cd:
                moved[-1] = True

    # -- one simple command
    def _simple(self, toks0: List[str], depth: int, prefix: List[str], cwd: Optional[str]) -> Tuple[Optional[str], bool]:
        pr = _pr()
        toks: List[str] = []
        k = 0
        while k < len(toks0):
            t = toks0[k]
            if t in pr._REDIRECT_OPS:
                target = toks0[k + 1] if k + 1 < len(toks0) else ""
                if toks and toks[-1].isdigit():
                    toks.pop()
                if t in (">", ">>", ">|", "&>", "&>>") and target and not target.startswith("&") \
                        and target != "/dev/null":
                    self._write(target, cwd)
                k += 2
                continue
            toks.append(t)
            k += 1
        for tok in toks:
            for inner in _substitutions(tok):
                if depth < 6:
                    before = len(self.simples)
                    self.scan(inner, depth + 1, prefix)
                    if any(s and s[0] in ("cd", "pushd", "popd") for s in self.simples[before:]):
                        self.simples.append(["popd"])
        assigns = list(prefix)
        i = 0
        while i < len(toks) and pr._ASSIGN_RE.match(toks[i]):
            self._env_name(pr._split_assign(toks[i])[0], "set")
            assigns.append(toks[i])
            i += 1
        envtoks: List[str] = []
        while i < len(toks):
            base = toks[i].rstrip("/").rsplit("/", 1)[-1]
            if base in KEYWORDS:
                i += 1
                continue
            if base == "env":
                envtoks.append("env")
                i += 1
                while i < len(toks):
                    t = toks[i]
                    if t in ("-i", "--ignore-environment", "-"):
                        self.tamper.append("env -i scrubs the environment the walls live in")
                        envtoks.append(t)
                        i += 1
                    elif t in ("-u", "--unset") and i + 1 < len(toks):
                        self._env_name(toks[i + 1], "unset")
                        envtoks += [t, toks[i + 1]]
                        i += 2
                    elif t.startswith("--unset=") or (t.startswith("-u") and len(t) > 2):
                        self._env_name(t.split("=", 1)[1] if "=" in t else t[2:], "unset")
                        envtoks.append(t)
                        i += 1
                    elif t in ("-C", "--chdir", "-S", "--split-string") and i + 1 < len(toks):
                        if t in ("-S", "--split-string") and depth < 6:
                            self.scan(toks[i + 1] + " " + shlex.join(toks[i + 2:]), depth + 1, assigns)
                            return cwd, False
                        envtoks += [t, toks[i + 1]]
                        i += 2
                    elif t == "--":
                        i += 1
                        break
                    elif pr._ASSIGN_RE.match(t):
                        self._env_name(pr._split_assign(t)[0], "set")
                        envtoks.append(t)
                        i += 1
                    elif t.startswith("-"):
                        envtoks.append(t)
                        i += 1
                    else:
                        break
                continue
            if base in WRAPPERS:
                opts = WRAPPERS[base]
                i += 1
                while i < len(toks) and toks[i].startswith("-") and toks[i] != "--":
                    i += 2 if (toks[i] in opts and i + 1 < len(toks)) else 1
                if i < len(toks) and toks[i] == "--":
                    i += 1
                if base == "timeout" and i < len(toks):
                    i += 1                              # the duration
                continue
            break
        if i >= len(toks):
            if assigns or envtoks:
                self.simples.append(assigns + envtoks + [":"])
            return cwd, False
        tool = toks[i].rstrip("/").rsplit("/", 1)[-1]
        args = toks[i + 1:]
        head = assigns + envtoks
        if tool == "eval" and depth < 6:
            before = len(self.simples)
            self.scan(" ".join(args), depth + 1, head)
            return cwd, any(s and s[0] in ("cd", "pushd", "popd") for s in self.simples[before:])
        if tool in SHELLS:
            j, has_c = 0, False
            while j < len(args) and args[j].startswith("-") and len(args[j]) > 1:
                has_c = has_c or (not args[j].startswith("--") and "c" in args[j][1:])
                j += 1
            if has_c and j < len(args) and depth < 6:
                before = len(self.simples)
                self.scan(args[j], depth + 1, head)
                if any(s and s[0] in ("cd", "pushd", "popd") for s in self.simples[before:]):
                    self.simples.append(["popd"])
                return cwd, False
        if tool in ("export", "unset", "declare", "typeset", "readonly", "local"):
            for a in args:
                if a.startswith("-"):
                    continue
                name = pr._split_assign(a)[0] if pr._ASSIGN_RE.match(a) else a
                self._env_name(name, "unset" if tool == "unset" else "set")
        if tool in ("cd", "pushd", "popd"):
            self.simples.append(head + toks[i:])
            dest = [a for a in args if not a.startswith("-") or a == "-"]
            if tool == "cd" and dest and dest[0] != "-":
                return _expand(dest[0], self.home, cwd), True
            return "\x00unknown", True
        self._program(tool, args, head, cwd)
        self.simples.append(head + [toks[i]] + args)
        return cwd, False

    def _env_name(self, name: str, how: str) -> None:
        if _is_tamper_env(name):
            self.tamper.append(f"{how} {name.rstrip('+')} (the walls' git config, identity, WS_*, gh belt or HOME)")

    def _write(self, raw: str, cwd: Optional[str]) -> None:
        self.writes.append((raw, _expand(raw, self.home, cwd)))

    def _program(self, tool: str, args: List[str], head: List[str], cwd: Optional[str]) -> None:
        if tool == "git":
            self._git(args, cwd)
        elif PY_RE.match(tool):
            self._python(args, head, cwd)
        elif tool in LAUNCH_CLIS or (tool == "open" and "-a" in args):
            app = None
            if tool == "open":
                j = args.index("-a")
                app = args[j + 1] if j + 1 < len(args) else ""
                if not any(app.casefold().startswith(a.casefold()) for a in LAUNCH_APPS):
                    return
            paths = [a for a in args if not a.startswith("-") and a != app and not re.match(r"^[a-z]+$", a)]
            self.launches.append({"tool": tool, "app": app, "cwd": cwd,
                                  "paths": [_expand(p, self.home, cwd) for p in paths]})
        elif tool in WRITE_TOOLS:
            pos = [a for a in args if not a.startswith("-")]
            targets = pos if WRITE_TOOLS[tool] == "all" else pos[-1:]
            for tgt in targets:
                self._write(tgt, cwd)
                if WRITE_TOOLS[tool] == "last" and len(pos) > 1 and tgt.endswith("/"):
                    self._write(tgt + os.path.basename(pos[0]), cwd)
        elif tool in ("sed", "perl") and any(a.startswith("-i") or (a.startswith("-") and "i" in a[1:]
                                                                    and tool == "perl") for a in args):
            pos = [a for a in args if not a.startswith("-")]
            for tgt in pos[1:]:
                self._write(tgt, cwd)
        elif tool == "dd":
            for a in args:
                if a.startswith("of="):
                    self._write(a[3:], cwd)

    def _python(self, args: List[str], head: List[str], cwd: Optional[str]) -> None:
        j, isolated = 0, False
        while j < len(args) and args[j].startswith("-") and args[j] != "-":
            if args[j] in ("-m", "-c"):
                return
            if "I" in args[j][1:] and not args[j].startswith("--"):
                isolated = True
            j += 2 if args[j] in PY_VALUE_OPTS else 1
        if j >= len(args):
            return
        rest = args[j + 1:]
        repo = None
        for k, a in enumerate(rest):
            if a == "--repo" and k + 1 < len(rest):
                repo = rest[k + 1]
            elif a.startswith("--repo="):
                repo = a.split("=", 1)[1]
        # _program runs before the simple command is appended, so its index is the current length
        self.vetted.append({"script": _expand(args[j], self.home, cwd), "isolated": isolated, "cwd": cwd,
                            "repo": _expand(repo, self.home, cwd) if repo else None, "head": list(head),
                            "index": len(self.simples)})

    def _git(self, args: List[str], cwd: Optional[str]) -> None:
        j = 0
        while j < len(args):
            a = args[j]
            if a in ("-c", "--config-env") and j + 1 < len(args):
                if _cfg_key_tamper(args[j + 1]):
                    self.tamper.append(f"git {a} {args[j + 1].split('=', 1)[0]}: a per-command hook, URL, include "
                                       "or identity key")
                j += 2
                continue
            if a.startswith("--config-env="):
                if _cfg_key_tamper(a.split("=", 1)[1]):
                    self.tamper.append("git --config-env with a hook, URL, include or identity key")
                j += 1
                continue
            if a.startswith("--exec-path="):
                self.candidates.append("git --exec-path (a helper search path; candidate R6)")
            if a in pr_git_opts_with_value():
                j += 2
                continue
            if a.startswith("-"):
                j += 1
                continue
            break
        sub = args[j] if j < len(args) else None
        rest = args[j + 1:]
        if sub == "config":
            self._git_config(rest, cwd)
        if sub in COMMIT_VERBS:
            for k, a in enumerate(rest):
                if a == "--author" and k + 1 < len(rest):
                    self.authors.append(rest[k + 1])
                elif a.startswith("--author="):
                    self.authors.append(a.split("=", 1)[1])
        if sub == "send-pack":
            self.candidates.append("git send-pack (a lower-level push; candidate R6)")

    def _git_config(self, rest: List[str], cwd: Optional[str]) -> None:
        scope_file = None
        glob = False
        write_flag = False
        read_flag = False
        pos: List[str] = []
        j = 0
        if rest[:1] in (["set"], ["unset"], ["rename-section"], ["remove-section"], ["edit"]):
            write_flag = rest[0] != "edit"
            read_flag = rest[0] == "edit"
            j = 1
        elif rest[:1] in (["get"], ["list"]):
            read_flag = True
            j = 1
        while j < len(rest):
            a = rest[j]
            if a in ("--global", "--system"):
                glob = True
            elif a in ("-f", "--file") and j + 1 < len(rest):
                scope_file = rest[j + 1]
                j += 2
                continue
            elif a.startswith("--file="):
                scope_file = a.split("=", 1)[1]
            elif a in GIT_CONFIG_WRITE_FLAGS:
                write_flag = True
            elif a in GIT_CONFIG_READ_FLAGS or a.startswith(("--get", "--list")):
                read_flag = True
            elif a in GIT_CONFIG_VALUE_OPTS and j + 1 < len(rest):
                j += 2
                continue
            elif a.startswith("-"):
                pass
            else:
                pos.append(a)
            j += 1
        writes = write_flag or (not read_flag and len(pos) >= 2)
        if not writes:
            return
        key = (pos[0] if pos else "").casefold()
        if key.startswith(CONFIG_WRITE_DENY_PREFIXES) or key in CONFIG_WRITE_DENY_EXACT:
            self.tamper.append(f"git config writes {key or 'a hook key'} (hooks, hooksPath or includes)")
        elif key.startswith(CONFIG_WRITE_REPORT_PREFIXES):
            self.candidates.append(f"git config writes a {key.split('.', 1)[0]}.* key (candidate R6)")
        if glob:
            self.tamper.append("git config --global/--system writes the user or system git config")
        if scope_file:
            self._write(scope_file, cwd)

    # -- output
    def normalized(self) -> str:
        return " ; ".join(shlex.join(s) for s in self.simples if s)


def pr_git_opts_with_value() -> frozenset:
    pr = _pr()
    return pr._GIT_OPTS_WITH_VALUE if pr is not None else frozenset({"-C", "-c", "--git-dir", "--work-tree"})


# --------------------------------------------------------------------------- employer vault folders

def employer_vault_folders(root: Path) -> List[Path]:
    """07-projects/* whose SESSION-STATE `Context profile` starts `centric-` or whose name matches an
    employer path glob (context-remotes). Used by the Claude permission rules and the file rule."""
    out: List[Path] = []
    proj = Path(root) / "07-projects"
    pr = _pr()
    globs: List[str] = []
    try:
        globs = list(pr.load_table("context-remotes", root=root).get("employer_path_globs") or []) if pr else []
    except Exception:  # noqa: BLE001
        globs = []
    import fnmatch

    try:
        dirs = sorted(d for d in proj.iterdir() if d.is_dir())
    except OSError:
        return out
    for d in dirs:
        prof = ""
        try:
            text = (d / "SESSION-STATE.md").read_text(encoding="utf-8", errors="replace")
            m = re.search(r"^\s*-\s+\*\*Context profile\*\*:\s*(.+)$", text, re.MULTILINE)
            if m:
                prof = m.group(1).strip().split()[0].strip("`").strip()
        except OSError:
            pass
        name = d.name.casefold()
        if prof.startswith("centric-") or any(fnmatch.fnmatchcase(name, g.casefold()) for g in globs if "/" not in g):
            out.append(d)
    return out


def vault_root(root: Optional[Path], home: Optional[Path]) -> Path:
    """The vault checkout: the test root, else the root file the pin installer wrote, else this tree."""
    if root is not None:
        return Path(root)
    pr = _pr()
    try:
        return Path(pr._workspace_checkout(home, None))
    except Exception:  # noqa: BLE001
        return ROOT


def _vault_folder_hit(path: Optional[str], root: Optional[Path], home: Optional[Path] = None) -> Optional[Path]:
    if not path:
        return None
    for d in employer_vault_folders(vault_root(root, home)):
        dd = os.path.normpath(str(d))
        for q in {path, os.path.realpath(path)}:
            if q.casefold() == dd.casefold() or q.casefold().startswith(dd.casefold() + "/"):
                return d
    return None


# --------------------------------------------------------------------------- decide

class Ctx:
    def __init__(self, *, host: str, det: dict, device: str, root: Optional[Path], home: Path, cache: Any,
                 env: dict, cwd: Optional[str], record: bool, cfg: dict, ask_capable: bool):
        self.host, self.det, self.device = host, det, device
        self.root, self.home, self.cache, self.env, self.cwd = root, home, cache, env, cwd
        self.record, self.cfg, self.ask_capable = record, cfg, ask_capable


def _finding(rule: str, outcome: str, reason: str, *, policy_rule: Optional[str] = None,
             route_to: Optional[list] = None, mode: Optional[str] = None) -> dict:
    return {"rule": rule, "outcome": outcome, "reason": reason, "policy_rule": policy_rule,
            "route_to": list(route_to or []), "mode": mode}


def _map_policy(d: dict, walls: str) -> Optional[dict]:
    """Rule id for a policy() result, or None for an allow."""
    out, rid = d.get("outcome"), d.get("rule_id")
    if out == "allow":
        return None
    facts = d.get("facts") or {}
    if rid == "P05-agent-hook-bypass":
        rule = "R6"
    elif walls == "claude":
        rule = "R1"
    elif (facts.get("owner_class") in ("unknown", "third-party") or facts.get("repo_conflict")) \
            and not (rid or "").startswith(("P30", "P31", "P40")):
        rule = "R4"
    else:
        rule = "R2"
    outcome = "route" if out == "route" else ("ask" if rule == "R4" else "deny")
    return _finding(rule, outcome, d.get("reason") or "", policy_rule=rid, route_to=d.get("route_to"))


def _policy(ctx: Ctx, *, repo: str, command: Optional[str] = None, action_class: Optional[str] = None,
            via: str = "composed") -> dict:
    pr = _pr()
    return pr.policy(repo=repo, command=command, action_class=action_class, via=via, root=ctx.root, home=ctx.home,
                     detection=ctx.det, device=ctx.device, record=ctx.record, cache=ctx.cache, env=ctx.env)


def _target_dir(path: Optional[str]) -> Optional[str]:
    """The nearest existing directory at or above a (possibly new) path."""
    if not path:
        return None
    p = Path(path)
    for q in [p] + list(p.parents):
        try:
            if q.is_dir():
                return str(q)
        except OSError:
            continue
    return None


def _vetted_row(script: Optional[str], ctx: Ctx) -> Optional[dict]:
    """The registry row whose path the invocation runs, when the script is the pinned blob."""
    pr = _pr()
    if not script:
        return None
    try:
        reg = pr.load_table("vetted-scripts", root=ctx.root)
    except Exception:  # noqa: BLE001
        return None
    for row in reg.get("scripts") or []:
        rel = str(row.get("path") or "")
        if not rel or not script.replace("\\", "/").endswith("/" + rel):
            continue
        base = script[: -len(rel) - 1]
        if pr._workspace_kind(base, ctx.root, ctx.home) is None and \
                os.path.normpath(base) != os.path.normpath(str(ctx.root or "")):
            continue
        st = pr.vetted_status(str(row.get("id")), script_path=script, home=ctx.home, root=ctx.root)
        if st.get("status") == "vetted":
            return row
    return None


def _identity_findings(ctx: Ctx, scan: ShellScan, invs: List[dict]) -> List[dict]:
    """R3 (I1): a personal effective identity on an employer repo. Never for a Claude chain: R1 already
    refuses Claude on employer repos, and a Claude process never opens an employer checkout to decide."""
    pr = _pr()
    if ctx.det.get("family_for_walls") == "claude":
        return []
    out: List[dict] = []
    try:
        dev_t = pr.load_table("devices", root=ctx.root)
    except Exception:  # noqa: BLE001
        return out
    for inv in invs:
        if inv.get("tool") != "git" or not inv.get("argv") or inv["argv"][0] not in COMMIT_VERBS:
            continue
        target = _target_dir(pr._abs_hint(ctx.cwd or os.getcwd(), inv.get("cwd_hint")))
        if not target:
            continue
        res = pr.repo_resolve(target, root=ctx.root, home=ctx.home, detection=ctx.det, cache=ctx.cache)
        if res.get("owner_class") != "employer":
            continue
        emails = [re.search(r"<([^>]*)>", a).group(1) if re.search(r"<([^>]*)>", a) else a for a in scan.authors]
        top = pr._find_top(Path(target))
        if not emails and top is not None:
            _name, email = pr._effective_git_identity(top, ctx.env, "git")
            emails = [email] if email else []
        for e in emails:
            if pr.email_class(e, dev_t) == "personal":
                out.append(_finding("R3", "deny", "I1: a personal identity never commits on an employer repo"))
                break
    return out


def decide(action: dict, ctx: Ctx) -> dict:
    """decide(action, target, chain, device, host caps) -> allow | deny | ask | route (the H15 core).

    Returns {decision, rule, policy_rule, reason, route_to, enforced, findings[], notices[]}: the most
    restrictive enforced finding decides; report-only findings are logged as would-deny and allow."""
    pr = _pr()
    fams = (_surfaces(ctx.root) or {}).get("families") or {}
    walls = str(ctx.det.get("family_for_walls") or "unknown")
    acting = str(ctx.det.get("family") or "unknown")
    agent = pr._chain_has_agent(walls, acting, ctx.det, fams)
    findings: List[dict] = []
    notices = list(ctx.det.get("notices") or [])
    kind = action.get("kind")
    if not agent:
        return _combine(findings, ctx, notices)       # P00: humans are not policy-gated
    if kind == "shell":
        scan = ShellScan(ctx.home, ctx.cwd)
        scan.scan(str(action.get("command") or ""))
        for r in dict.fromkeys(scan.tamper):
            findings.append(_finding("R6", "deny", f"tamper: {r}"))
        for r in dict.fromkeys(scan.candidates):
            findings.append(_finding("R6c", "deny", r))
        for raw, path in scan.writes:
            pc = protected_class(path, ctx.home)
            if pc:
                findings.append(_finding("R6" if pc[0] != "report" else "R6c",
                                         "ask" if pc[0] == "ask" else "deny", pc[1]))
        # vetted invocations are judged on their own (via=vetted); the rest of the text goes to policy
        simples = [list(s) for s in scan.simples]
        for v in scan.vetted:
            row = _vetted_row(v["script"], ctx) if v["isolated"] else None
            if row is None:
                continue
            target = v["repo"] or (v["cwd"] if v["cwd"] and not v["cwd"].startswith("\x00") else None) \
                or ctx.cwd or os.getcwd()
            d = _policy(ctx, repo=target, action_class="housekeeping", via="vetted")
            f = _map_policy(d, walls)
            if f:
                findings.append(f)
            elif d.get("receipt"):
                notices.append(f"vetted {row.get('id')}: allowed; the script writes its own receipt")
            if 0 <= v["index"] < len(simples):
                simples[v["index"]] = [":"]          # judged above with via=vetted
        norm = " ; ".join(shlex.join(s) for s in simples if s) or ":"
        repo = ctx.cwd or os.getcwd()
        invs = pr.parse_command(norm)
        if invs:                                     # only no-op builtins: nothing for the policy to judge
            d = _policy(ctx, repo=repo, command=norm)
            f = _map_policy(d, walls)
            if f:
                if f["policy_rule"] == "P11-claude-employer-composed":
                    names = _vetted_names(ctx)
                    f["reason"] = f"{f['reason']} ({names})" if names else f["reason"]
                findings.append(f)
        findings += _url_findings(ctx, invs, walls)
        findings += _identity_findings(ctx, scan, invs)
        findings += _launch_findings(ctx, scan, walls)
    elif kind == "file":
        path = _expand(str(action.get("path") or ""), ctx.home, ctx.cwd) if action.get("path") else None
        write = action.get("op") == "write"
        if write:
            pc = protected_class(path, ctx.home)
            if pc:
                findings.append(_finding("R6" if pc[0] != "report" else "R6c", "ask" if pc[0] == "ask" else "deny",
                                         pc[1]))
        if walls == "claude" and _vault_folder_hit(path, ctx.root, ctx.home):
            findings.append(_finding("R1", "route", "an employer vault folder: Claude never reads or writes it",
                                     route_to=["cursor", "codex"]))
        target = _target_dir(path) if path else (ctx.cwd or os.getcwd())
        if target:
            d = _policy(ctx, repo=target, action_class="author" if write else "content-read")
            f = _map_policy(d, walls)
            if f:
                findings.append(f)
    elif kind == "mcp":
        if action.get("owner_class") == "employer" and walls == "claude":
            f = _finding("R1", "route", f"{action.get('server')} is an employer channel: employer content-read "
                                        "and authoring route to Cursor or Codex", route_to=["cursor", "codex"])
            if action.get("rollout") == "report":
                f["mode"] = "report"
            findings.append(f)
    elif kind == "url":
        findings += _url_owner_findings(ctx, str(action.get("url") or ""), walls, action.get("rollout"))
    return _combine(findings, ctx, notices)


def _vetted_names(ctx: Ctx) -> str:
    pr = _pr()
    try:
        reg = pr.load_table("vetted-scripts", root=ctx.root)
    except Exception:  # noqa: BLE001
        return ""
    names = [f"python3 -I {r.get('path')}" for r in reg.get("scripts") or [] if isinstance(r, dict)]
    return "vetted: " + ", ".join(names) if names else ""


def _is_url(a: str) -> bool:
    """A remote URL argument (scheme URL or scp form host:owner/repo), not a refspec or a path."""
    if "://" in a:
        return True
    if a.startswith(("./", "/", "~", "-", "+")) or ":" not in a:
        return False
    host, _, path = a.partition(":")
    return "/" in path and ("." in host.rsplit("@", 1)[-1] or "@" in host)


def _url_findings(ctx: Ctx, invs: List[dict], walls: str) -> List[dict]:
    """Explicit remote URLs and gh repo slugs are targets too (H17-R6: resolved with the floor's resolver)."""
    out: List[dict] = []
    for inv in invs:
        argv = inv.get("argv") or []
        tool = inv.get("tool")
        targets: List[Tuple[str, str]] = []
        if tool == "git" and argv:
            sub = argv[0]
            if sub in NETWORK_VERBS:
                targets += [(a, NETWORK_VERBS[sub]) for a in argv[1:] if not a.startswith("-") and _is_url(a)]
            if sub == "remote" and len(argv) >= 4 and argv[1] in ("add", "set-url"):
                targets += [(a, "author") for a in argv[2:] if _is_url(a)]
            if sub == "archive":
                targets += [(a.split("=", 1)[1], "content-read") for a in argv if a.startswith("--remote=")]
        elif tool == "gh" and argv:
            if argv[0] == "repo" and len(argv) >= 3 and re.match(r"^[\w.-]+/[\w.-]+$", argv[2]):
                targets.append((argv[2], "author" if argv[1] in ("create", "edit", "delete", "fork") else
                                "content-read"))
            if argv[0] == "api":
                m = next((re.match(r"^/?repos/([\w.-]+/[\w.-]+)", a) for a in argv[1:] if re.match(r"^/?repos/", a)),
                         None)
                if m:
                    targets.append((m.group(1), "publish" if _gh_api_writes(argv) else "content-read"))
        for url, cls in targets:
            d = _policy(ctx, repo=url, action_class=cls)
            f = _map_policy(d, walls)
            if f:
                out.append(f)
    return out


def _gh_api_writes(argv: List[str]) -> bool:
    """gh api sends a body (-f/-F/--input) or a non-GET method: a write."""
    for i, a in enumerate(argv):
        if a in ("-f", "-F", "--field", "--raw-field", "--input") or a.startswith(("--field=", "--raw-field=",
                                                                                   "--input=")):
            return True
        method = None
        if a in ("-X", "--method") and i + 1 < len(argv):
            method = argv[i + 1]
        elif a.startswith("--method="):
            method = a.split("=", 1)[1]
        elif a.startswith("-X") and len(a) > 2:
            method = a[2:]
        if method is not None and method.upper() != "GET":
            return True
    return False


def _launch_findings(ctx: Ctx, scan: ShellScan, walls: str) -> List[dict]:
    pr = _pr()
    out: List[dict] = []
    if walls != "claude":
        return out
    for ln in scan.launches:
        what = ln.get("app") or ln.get("tool")
        employer = False
        for tgt in [ln.get("cwd") or ctx.cwd] + list(ln.get("paths") or []):
            if not tgt or str(tgt).startswith("\x00"):
                continue
            res = pr.repo_resolve(_target_dir(tgt) or tgt, root=ctx.root, home=ctx.home, detection=ctx.det,
                                  cache=ctx.cache)
            employer = employer or res.get("owner_class") == "employer"
        if employer:
            out.append(_finding("R7", "deny", f"a Claude chain launching {what} on an employer target: open it "
                                              "yourself so it is not classified Claude"))
        else:
            out.append(_finding("R7", "allow", f"{what} launched from a Claude chain inherits the overlay and is "
                                               f"classified Claude; for a GUI launch use `open -a <App>`"))
    return out


def _url_owner_findings(ctx: Ctx, url: str, walls: str, rollout: Optional[str]) -> List[dict]:
    """URL-owner policy for browser control driven from Claude Code: employer hosts are employer
    content-read (route)."""
    pr = _pr()
    if walls != "claude" or not url:
        return []
    from urllib.parse import urlparse

    try:
        u = urlparse(url if "://" in url else "https://" + url)
    except ValueError:
        return []
    host = (u.hostname or "").casefold()
    host = {"www.github.com": "github.com", "www.bitbucket.org": "bitbucket.org"}.get(host, host)
    owner = next((seg for seg in (u.path or "").split("/") if seg), "")
    if not host or not owner:
        return []
    try:
        cls = pr.owner_class(host, owner.casefold(), root=ctx.root)
    except Exception:  # noqa: BLE001
        return []
    if cls != "employer":
        return []
    f = _finding("R1", "route", "an employer host in the browser is employer content-read: route to Cursor or Codex",
                 route_to=["cursor", "codex"])
    if rollout == "report":
        f["mode"] = "report"
    return [f]


def _combine(findings: List[dict], ctx: Ctx, notices: List[str]) -> dict:
    enforced: List[dict] = []
    report: List[dict] = []
    for f in findings:
        mode = f.get("mode") or rule_mode(ctx.cfg, f["rule"], ctx.host)
        f["mode"] = mode
        if f["outcome"] == "allow":
            notices.append(f"{f['rule']}: {f['reason']}")
            continue
        (enforced if mode == "enforce" else report).append(f)
    best = None
    for f in enforced:
        if best is None or RANK[f["outcome"]] > RANK[best["outcome"]]:
            best = f
    out = {"decision": "none", "rule": None, "policy_rule": None, "reason": "", "route_to": [], "enforced": False,
           "findings": findings, "report_only": report, "notices": notices,
           "walls_family": ctx.det.get("family_for_walls"), "acting": ctx.det.get("acting_host")}
    if best is not None:
        dec = best["outcome"]
        if dec == "ask" and not ctx.ask_capable:
            dec = "deny"
        out.update(decision=dec, rule=best["rule"], policy_rule=best["policy_rule"], reason=best["reason"],
                   route_to=best["route_to"], enforced=True)
    return out


# --------------------------------------------------------------------------- dialects

ASK_CAPABLE = {"claude": True, "cursor": True, "codex": False, "gemini": False, "copilot-cli": True,
               "windsurf": False, "cline": False, "plain": False}


def dialect_for(host: str, t: Optional[dict]) -> str:
    row = _row(t, host) or {}
    d = row.get("dialect") or "none"
    if host in ("gemini-cli",):
        return "gemini"
    if host in ("copilot-cli",):
        return "copilot-cli"
    if host in ("windsurf",):
        return "windsurf"
    return d if d in ("claude", "cursor", "codex") else "claude"


def reason_text(dec: dict) -> str:
    tag = dec.get("rule") or "R?"
    pol = f" {dec['policy_rule']}" if dec.get("policy_rule") else ""
    text = f"workspace wall guard [{tag}{pol}]: {dec.get('reason') or 'refused'}"
    if dec.get("decision") == "route" or dec.get("route_to"):
        text += f" — hand this to {' or '.join(dec.get('route_to') or ['cursor', 'codex'])} (a handoff line was logged)"
    return text


def render(dialect: str, dec: dict, event_raw: str = "") -> Tuple[int, str, str]:
    """(exit code, stdout, stderr) in the host's dialect. No decision: the host's no-op."""
    d = dec.get("decision")
    if d in ("route",):
        d = "deny"
    if d not in ("deny", "ask"):
        return 0, ("{}" if dialect == "cursor" else ""), ""
    why = reason_text(dec)
    if dialect == "claude":
        return 0, json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": d,
                                                     "permissionDecisionReason": why}}, ensure_ascii=False), ""
    if dialect == "cursor":
        return 0, json.dumps({"permission": d, "user_message": why, "agent_message": why}, ensure_ascii=False), ""
    if dialect == "gemini":
        return 0, json.dumps({"decision": "deny", "reason": why}, ensure_ascii=False), ""
    if dialect == "copilot-cli":
        return 0, json.dumps({"permissionDecision": d, "permissionDecisionReason": why}, ensure_ascii=False), ""
    # codex, windsurf and any plain host: the blocking exit code with the reason on stderr (deny only)
    return 2, "", why


# --------------------------------------------------------------------------- telemetry

def _log(home: Path, host: str, dec: dict, action: dict, probe_id: Optional[str]) -> None:
    pr = _pr()
    try:
        tel = pr.ws_paths(home=home)["telemetry"]
    except Exception:  # noqa: BLE001
        return
    if not tel.is_dir():
        return
    rows = []
    base = {"schema_version": SCHEMA_VERSION, "ts": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "host": host, "walls": dec.get("walls_family"), "kind": action.get("kind")}
    if probe_id:
        base["probe"] = probe_id
    if dec.get("decision") != "none" or probe_id:
        rows.append(dict(base, decision=dec.get("decision"), rule=dec.get("rule"), policy_rule=dec.get("policy_rule"),
                         enforced=bool(dec.get("enforced"))))
    for f in dec.get("report_only") or []:
        rows.append(dict(base, decision=f"would-{'deny' if f['outcome'] == 'route' else f['outcome']}",
                         rule=f["rule"], policy_rule=f.get("policy_rule"), enforced=False))
    try:
        with open(tel / LOG_NAME, "a", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, separators=(",", ":")) + "\n")
    except OSError:
        pass


# --------------------------------------------------------------------------- hook entry

def run_hook(host_arg: str, payload: dict, *, env: Optional[dict] = None, ancestry: Optional[list] = None,
             home: Optional[Path] = None, root: Optional[Path] = None, device: Optional[str] = None,
             hostname: Optional[str] = None, cache: Any = None, budget: Optional[float] = None,
             record: bool = True) -> Tuple[int, str, str, Optional[dict]]:
    """(exit code, stdout, stderr, decision) for one pre-tool payload. Fails open on every error."""
    box: Dict[str, Any] = {}

    def work() -> None:
        try:
            box["v"] = _hook(host_arg, payload, env=dict(os.environ if env is None else env), ancestry=ancestry,
                             home=Path(home) if home else Path.home(), root=root, device=device, hostname=hostname,
                             cache=cache, record=record)
        except Exception as exc:  # noqa: BLE001 - fail open (H17-R8 class)
            box["e"] = exc

    t0 = time.monotonic()
    th = threading.Thread(target=work, daemon=True)
    th.start()
    th.join(HOOK_BUDGET_S if budget is None else budget)
    if th.is_alive() or "e" in box or "v" not in box:
        why = "timed out" if th.is_alive() else f"error ({type(box.get('e')).__name__})"
        dialect = "cursor" if host_arg == "cursor" else "none"
        return 0, ("{}" if dialect == "cursor" else ""), f"wall guard: {why} after {time.monotonic() - t0:.1f}s; " \
                                                         "no decision", None
    return box["v"]


def _hook(host_arg: str, payload: dict, *, env: dict, ancestry: Optional[list], home: Path, root: Optional[Path],
          device: Optional[str], hostname: Optional[str], cache: Any, record: bool
          ) -> Tuple[int, str, str, Optional[dict]]:
    pr = _pr()
    t = _surfaces(root)
    if pr is None or t is None:
        return 0, ("{}" if host_arg == "cursor" else ""), "", None
    hint, verified = payload_hint(payload, t)
    declared = host_arg if host_arg != "auto" else (hint or "unknown")
    dialect = dialect_for(declared, t)
    noop = "{}" if dialect == "cursor" else ""
    if hint and verified and hint != declared and hint in own_guard_hosts(t):
        return 0, noop, "", {"decision": "none", "deferred_to": hint}
    event, tool, actions, cwd = extract(payload, t)
    if not actions:
        return 0, noop, "", None
    det = detect(declared, payload, env=env, ancestry=ancestry, root=root, t=t)
    dev = device or pr.current_device(hostname=hostname, root=root)["id"]
    cfg = guard_config(t)
    ctx = Ctx(host=declared, det=det, device=dev, root=root, home=home, cache=cache, env=env,
              cwd=str(cwd) if cwd else None, record=record, cfg=cfg, ask_capable=ASK_CAPABLE.get(dialect, False))
    best: Optional[dict] = None
    for action in actions:
        dec = decide(action, ctx)
        probe = None
        text = json.dumps(action)
        m = PROBE_MARK_RE.search(text)
        if m:
            probe = m.group(1)
        if record:
            _log(home, declared, dec, action, probe)
        if best is None or RANK[dec["decision"]] > RANK[best["decision"]]:
            best = dec
    assert best is not None
    rc, out, err = render(dialect, best, event)
    if best["decision"] == "none":
        out = noop
    return rc, out, err, best


# --------------------------------------------------------------------------- report + probes

def read_log(home: Optional[Path] = None) -> List[dict]:
    pr = _pr()
    try:
        path = pr.ws_paths(home=home)["telemetry"] / LOG_NAME
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, AttributeError):
        return []
    out = []
    for ln in lines:
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        if isinstance(r, dict):
            out.append(r)
    return out


def report(*, home: Optional[Path] = None, days: int = 14) -> dict:
    rows = read_log(home)
    start = min((r.get("ts") for r in rows if str(r.get("decision", "")).startswith("would-")), default=None)
    counts: Dict[str, int] = {}
    for r in rows:
        key = f"{r.get('host')} {r.get('rule')} {r.get('decision')}"
        counts[key] = counts.get(key, 0) + 1
    ends = None
    if start:
        try:
            ends = (dt.datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ") + dt.timedelta(days=days)).strftime("%Y-%m-%d")
        except ValueError:
            ends = None
    return {"window_start": start, "window_days": days, "window_ends": ends, "counts": counts, "rows": len(rows)}


PROBE_ROOT = "/tmp/wallguard-probe"
PROBE_CASES = [
    {"id": "R6noverify", "command": f"git -C {PROBE_ROOT}/scratch commit --allow-empty --no-verify -m wallguard-probe-R6noverify",
     "expect": {"*": "deny"}},
    {"id": "R6count", "command": f"GIT_CONFIG_COUNT=0 git -C {PROBE_ROOT}/scratch status # wallguard-probe-R6count",
     "expect": {"*": "deny"}},
    {"id": "allow", "command": f"git -C {PROBE_ROOT}/scratch status # wallguard-probe-allow",
     "expect": {"*": "none"}},
    {"id": "R1meta", "command": f"git -C {PROBE_ROOT}/emp status # wallguard-probe-R1meta",
     "expect": {"claude-code": "deny", "cursor": "none", "codex": "none"}},
    {"id": "R3ident", "command": f"git -C {PROBE_ROOT}/emp-personal commit --allow-empty -m wallguard-probe-R3ident",
     "expect": {"claude-code": "deny", "cursor": "deny", "codex": "deny"}},
]


def probe_setup(*, root_dir: str = PROBE_ROOT) -> int:
    """Human step: scratch repos for the live probes (a synthetic employer-owner remote that is never pushed)."""
    import subprocess

    pr = _pr()
    cr = pr.load_table("context-remotes")
    owner = next((o["owner"] for o in cr.get("owners") or [] if o.get("class") == "employer"
                  and o.get("host") == "github.com"), None)
    dev_t = pr.load_table("devices")
    personal = next((i.get("email") for i in dev_t.get("identities") or [] if i.get("class") == "personal"), None)
    if not owner or not personal:
        print("probe-setup: no employer owner or personal identity declared", file=sys.stderr)
        return 1
    base = Path(root_dir)
    for name, remote, email in (("scratch", None, None), ("emp", f"git@github.com:{owner}/wallguard-probe.git", None),
                                ("emp-personal", f"git@github.com:{owner}/wallguard-probe.git", personal)):
        d = base / name
        d.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "init", "-q", "-b", "main", str(d)], check=False)
        if remote:
            subprocess.run(["git", "-C", str(d), "remote", "remove", "origin"], capture_output=True, check=False)
            subprocess.run(["git", "-C", str(d), "remote", "add", "origin", remote], check=False)
        if email:
            subprocess.run(["git", "-C", str(d), "config", "user.email", email], check=False)
    print(f"probe repos ready under {base} (the employer-shaped remote is never pushed)")
    return 0


def probe_record(host: str, *, device: Optional[str] = None, home: Optional[Path] = None,
                 root: Optional[Path] = None, write: bool = True) -> Tuple[int, dict]:
    """Human step: compare the decision log's probe rows with the expected goldens and write
    02-shared-references/probes/wallguard-<host>@<device>.json (redacted, like every probe record)."""
    pr = _pr()
    dev = device or pr.current_device(root=root)["id"]
    rows = [r for r in read_log(home) if r.get("host") == host and r.get("probe")]
    seen: Dict[str, dict] = {}
    for r in rows:
        if not str(r.get("decision", "")).startswith("would-"):   # report-only rows ride along; the verdict row decides
            seen[r["probe"]] = r
    cases = {}
    ok = True
    for c in PROBE_CASES:
        want = c["expect"].get(host, c["expect"].get("*"))
        got = seen.get(c["id"])
        observed = got.get("decision") if got else "not-seen"
        if observed == "route":
            observed = "deny"               # a route renders as deny on every host
        match = observed == want
        ok = ok and match
        cases[c["id"]] = {"expected": want, "observed": observed, "rule": (got or {}).get("rule") or "none",
                          "match": match}
    rec = {"schema_version": 1, "surface": f"wallguard-{host}", "device": dev,
           "recorded_at": dt.date.today().isoformat(), "declared_host": host, "component": "H15",
           "cases": cases, "all_match": ok}
    for v in _walk_strings(rec):
        if not REDACT_RE.match(v):
            return 1, {"error": f"redaction: {v!r}"}
    if write:
        out = (root or ROOT) / "02-shared-references" / "probes" / f"wallguard-{host}@{dev}.json"
        out.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
    return (0 if ok else 1), rec


def _walk_strings(obj: Any) -> List[str]:
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, dict):
        return [s for k, v in obj.items() for s in (_walk_strings(k) + _walk_strings(v))]
    if isinstance(obj, list):
        return [s for v in obj for s in _walk_strings(v)]
    return []


# --------------------------------------------------------------------------- belts

def belt_prefixes() -> List[Tuple[str, List[str], str]]:
    """Every concrete argv prefix the belts carry: (invariant id, argv, why)."""
    import itertools

    out = []
    for inv in BELT_INVARIANTS:
        for combo in itertools.product(*inv["argv"]):
            out.append((inv["id"], list(combo), inv["why"]))
    return out


def belt_match(argv: List[str]) -> Optional[str]:
    """The invariant id whose argv prefix `argv` starts with (Codex prefix_rule semantics), else None."""
    for iid, pre, _why in belt_prefixes():
        if argv[:len(pre)] == pre:
            return iid
    return None


def render_codex_rules() -> str:
    lines = ["# snds-workspace wall belt (H15). Rendered by 00-bootstrap/doctor/render_shims.py from",
             "# 09-tools/wall_guard.py BELT_INVARIANTS; do not edit by hand. Forbidden invariants only: each",
             "# prefix is one the wall guard also denies, so this file is never stricter than the guard.", ""]
    for inv in BELT_INVARIANTS:
        pattern = ", ".join(json.dumps(alts[0]) if len(alts) == 1 else "[" + ", ".join(json.dumps(a) for a in alts)
                            + "]" for alts in inv["argv"])
        lines += ["prefix_rule(", f"    pattern = [{pattern}],", '    decision = "forbidden",',
                  f"    justification = {json.dumps(inv['why'])},", ")", ""]
    return "\n".join(lines)


def claude_bash_rules() -> List[str]:
    return [f"Bash({' '.join(pre)}:*)" for _iid, pre, _why in belt_prefixes()]


def belt_lists() -> dict:
    """The same invariants as regexes (Warp denylist, Zed always_deny) and globs (OpenCode)."""
    regexes, globs = [], []
    for _iid, pre, _why in belt_prefixes():
        regexes.append("^" + r"\s+".join(re.escape(x) for x in pre) + r"(\s|$)")
        globs += [" ".join(pre), " ".join(pre) + " *"]
    return {"regex": regexes, "glob": globs}


# --------------------------------------------------------------------------- CLI

def _read_payload() -> dict:
    try:
        if sys.stdin.isatty():
            return {}
        data = sys.stdin.read()
        p = json.loads(data) if data.strip() else {}
    except (OSError, ValueError):
        return {}
    return p if isinstance(p, dict) else {}


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["--self-test"]:
        return self_test()
    if argv[:1] == ["hook"]:
        try:
            ap = argparse.ArgumentParser(prog="wall_guard.py hook")
            ap.add_argument("--host", default="auto")
            ap.add_argument("--event", default="pre-tool")
            a = ap.parse_args(argv[1:])
        except SystemExit:
            return 0
        try:
            rc, out, err, _d = run_hook(a.host, _read_payload())
        except Exception:  # noqa: BLE001
            return 0
        if out:
            print(out)
        if err:
            print(err, file=sys.stderr)
        return rc
    ap = argparse.ArgumentParser(prog="wall_guard.py")
    sub = ap.add_subparsers(dest="cmd")
    d = sub.add_parser("decide")
    d.add_argument("--host", default="auto")
    d.add_argument("--command")
    d.add_argument("--path")
    d.add_argument("--write", action="store_true")
    d.add_argument("--cwd")
    d.add_argument("--json", action="store_true")
    r = sub.add_parser("report")
    r.add_argument("--days", type=int, default=14)
    r.add_argument("--json", action="store_true")
    sub.add_parser("probe-setup")
    p = sub.add_parser("probe-record")
    p.add_argument("--host", required=True)
    p.add_argument("--device")
    try:
        a = ap.parse_args(argv)
    except SystemExit:
        return 2
    if a.cmd == "decide":
        if bool(a.command) == bool(a.path):
            print("decide: give exactly one of --command or --path", file=sys.stderr)
            return 2
        payload: Dict[str, Any] = {"hook_event_name": "PreToolUse", "cwd": a.cwd or os.getcwd()}
        if a.command:
            payload.update(tool_name="Bash", tool_input={"command": a.command})
        else:
            payload.update(tool_name="Write" if a.write else "read_file",
                           tool_input={"file_path": a.path, "path": a.path})
        rc, out, err, dec = run_hook(a.host, payload, record=False)
        dec = dec or {"decision": "none"}
        if a.json:
            print(json.dumps({k: v for k, v in dec.items() if k != "findings"}, indent=2, default=str))
        else:
            print(f"{dec.get('decision')} {dec.get('rule') or ''} {dec.get('reason') or ''}".rstrip())
            for f in dec.get("report_only") or []:
                print(f"  report-only {f['rule']}: would-{f['outcome']} — {f['reason']}")
        return 0 if dec.get("decision") in ("none", "allow") else 1
    if a.cmd == "report":
        rep = report(days=a.days)
        if a.json:
            print(json.dumps(rep, indent=2))
        else:
            print(f"window: {rep['window_start'] or 'not started'} (+{rep['window_days']}d → {rep['window_ends']})")
            for k, v in sorted(rep["counts"].items()):
                print(f"  {v:5d}  {k}")
        return 0
    if a.cmd == "probe-setup":
        return probe_setup()
    if a.cmd == "probe-record":
        rc, rec = probe_record(a.host, device=a.device)
        print(json.dumps(rec, indent=2))
        return rc
    ap.print_help()
    return 2


# --------------------------------------------------------------------------- self-test

def self_test() -> int:
    """Runs the golden corpus (09-tools/fixtures/wall_guard) through the guard in a temp world."""
    cases_mod = _load_cases()
    if cases_mod is None:
        print("FAIL wall_guard self-test — fixtures/wall_guard/cases.py missing")
        return 1
    results = cases_mod.core_cases(sys.modules[__name__])
    fails = [r for r in results if not r[1]]
    for name, ok, detail in results:
        if not ok:
            print(f"FAIL {name}: {detail}")
    print(f"{'OK' if not fails else 'FAIL'} wall_guard self-test — {len(results) - len(fails)}/{len(results)} cases")
    return 0 if not fails else 1


def _load_cases():
    import importlib.util

    path = FIXTURES / "cases.py"
    if not path.is_file():
        return None
    spec = importlib.util.spec_from_file_location("wall_guard_cases", path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["wall_guard_cases"] = mod
    spec.loader.exec_module(mod)
    return mod


if __name__ == "__main__":
    sys.exit(main())
