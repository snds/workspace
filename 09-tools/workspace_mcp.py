#!/usr/bin/env python3
"""workspace_mcp.py — the workspace MCP server for MCP-only hosts (H21).

A stdio JSON-RPC 2.0 MCP server (newline-delimited, no HTTP transport) that replaces the generic
filesystem MCP (workspace-fs) for Claude Desktop Chat and Cowork, Claude Code desktop sessions,
Codex and any other MCP client or local model. Ported from the bootstrap generator's emitted server
(07-projects/18-bootstrap-generator/generator/wsxlib/mcp_template.py); stdlib only.

Read tools run the same CLIs every other surface runs, so an MCP client gets the same answers:

  session_status   09-tools/session-status.py (the card), family from clientInfo
  route            09-tools/prompt_route.py --utterance (output is the CLI's output, byte for byte)
  loadset          09-tools/skill-loadset.py
  resolve          profile_resolve.repo_resolve, status fields only (no paths, remotes or reasons)
  policy           profile_resolve.policy, the answer only (outcome, rule, reason, route_to); never recorded
  guard_check      wall_guard.decide for a path or command, plus this server's own vault verdict
  context_load     the canonical read order (CRITICAL_FACTS, role, project-context, the session-log head,
                   preferences) or named vault files
  skills_load      03-skills/<name>/SKILL.md by name, or the load chain skill-loadset.py computes
  read_file, list_directory, search_files   vault-only reads (the workspace-fs replacement)

Write tools are guarded and attributed:

  write_file, edit_file   vault only. The vault root is the nearest ancestor holding AGENTS.md.
      Refused: a path outside the vault (.., absolute, ~), any symlink on the way (no escape through a
      link), an employer vault folder (wall_guard.employer_vault_folders, the classification the wall
      guard and the Claude permission rules use), a generated file (closure.GENERATED, the skill wrapper
      roots and marker of build-local-skill-plugin.py, every render_shims output in surfaces.json), a
      wall or control file (wall_guard.protected_class against the home and the vault), the pinned guard
      code (pin_lib.PINNED_PATHS) and this server, git internals, and content that raises the secret or
      employer-substance hit count of the file (check-secrets.py rules; the baseline can only shrink).
      Every write is stamped with the MCP clientInfo (name and version from initialize; Claude* maps to
      family claude) and recorded in the H23 touch ledger
      (~/.config/snds-workspace/telemetry/sessions/<sid>.touched; nothing until telemetry/ exists).
  session_end   writes a 06-context/sessions/<id>.md fragment (compaction folds it; never the log).

Reads refuse the same employer vault folders and hide them from listings and searches, for every
client: clientInfo is self-reported, so no refusal loosens on it (tighten-only).

Declared gaps: the server guards only writes made through its own tools. Cowork's shell, computer use,
the browser and Desktop Extensions write around it; a host that keeps workspace-fs registered next
to it still has an unguarded writer (the installer replaces that entry).

Usage:
  workspace_mcp.py [--root DIR] [--home DIR]   serve on stdio (the MCP registration runs this)
  workspace_mcp.py --self-test

Stdlib only; python3 3.9+. Nothing here is auto-loaded.
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import fnmatch
import importlib.util
import json
import os
import re
import secrets
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

TOOLS = Path(__file__).resolve().parent
SERVER_NAME = "workspace-mcp"
SERVER_VERSION = "1.0"
SERVER_REL = "09-tools/workspace_mcp.py"
PROTOCOLS = ("2025-06-18", "2025-03-26", "2024-11-05")
CLI_TIMEOUT_S = 60
MAX_READ_BYTES = 1_000_000
MAX_WRITE_BYTES = 2_000_000
MAX_SEARCH_RESULTS = 200
LOG_HEAD_LINES = 80
SKILL_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
PRUNE_DIRS = frozenset({".git", "node_modules", "__pycache__"})
BLOCK_LINE_RE = re.compile(r"^(--- (SESSION BLOCK|END BLOCK) ---|SessionID:|### )")
CORE_CONTEXT = ("06-context/CRITICAL_FACTS.md", "06-context/role-and-context.md",
                "06-context/project-context.md", "06-context/session-log.md",
                "04-preferences/user-preferences.md")
SURFACES_REL = "02-shared-references/surfaces.json"
PLUGIN_BUILDER_REL = "09-tools/build-local-skill-plugin.py"
PIN_LIB_REL = "00-bootstrap/doctor/pin_lib.py"
CLOSURE_REL = "09-tools/closure.py"


class Refused(Exception):
    """A guarded tool call the server will not perform (the text says why)."""


# --------------------------------------------------------------------------- roots + siblings

def find_root(start: Path) -> Optional[Path]:
    """The vault root: the nearest ancestor (or self) holding AGENTS.md."""
    cur = Path(start).resolve()
    for p in [cur, *cur.parents]:
        if (p / "AGENTS.md").is_file():
            return p
    return None


def _sibling(name: str):
    if str(TOOLS) not in sys.path:
        sys.path.insert(0, str(TOOLS))
    return __import__(name)


def _load_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _const(path: Path, name: str) -> Any:
    """A module-level literal read with ast (the generator is never executed to learn its outputs)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in tree.body:
        targets = node.targets if isinstance(node, ast.Assign) else (
            [node.target] if isinstance(node, ast.AnnAssign) else [])
        if any(getattr(t, "id", None) == name for t in targets) and node.value is not None:
            return ast.literal_eval(node.value)
    raise KeyError(f"{name} not found in {path.name}")


def client_family(name: Optional[str]) -> Tuple[str, str]:
    """(family, surface id) for an MCP clientInfo name. Claude* is family claude."""
    n = (name or "").casefold()
    if n.startswith("claude"):
        return "claude", ("claude-code" if "code" in n else "claude-chat-desktop")
    if n.startswith("local-agent-mode"):  # the Claude desktop app's Code tab (observed live 2026-09-26)
        return "claude", "claude-code"
    if "cursor" in n:
        return "cursor", "cursor"
    if "codex" in n:
        return "codex", "codex"
    return "unknown-agent", "mcp-clients"


def _utc(now: Optional[dt.datetime] = None) -> dt.datetime:
    return now or dt.datetime.now(dt.timezone.utc)


# --------------------------------------------------------------------------- the server

class Server:
    def __init__(self, root: Optional[Path] = None, home: Optional[Path] = None,
                 now: Optional[Any] = None):
        r = Path(root) if root is not None else find_root(TOOLS)
        if r is None or not (Path(r) / "AGENTS.md").is_file():
            raise SystemExit("workspace_mcp: no AGENTS.md at or above the server (not a vault)")
        self.root = Path(os.path.realpath(str(r)))
        self.home = Path(home) if home is not None else Path.home()
        self._now = now
        self.client: Dict[str, Optional[str]] = {"name": None, "version": None}
        self.family, self.host = client_family(None)
        self.sid: Optional[str] = None
        self._cache: Dict[str, Any] = {}

    # ------------------------------------------------------------------ identity

    def now(self) -> dt.datetime:
        return _utc(self._now() if callable(self._now) else self._now)

    def set_client(self, info: Any) -> None:
        info = info if isinstance(info, dict) else {}
        name = str(info.get("name") or "")[:80] or None
        ver = str(info.get("version") or "")[:40] or None
        self.client = {"name": name, "version": ver}
        self.family, self.host = client_family(name)
        stamp = self.now().strftime("%Y%m%dT%H%M%SZ")
        self.sid = f"mcp-{self.host}-{stamp}-{os.getpid()}"

    def session_id(self) -> str:
        if self.sid is None:
            self.set_client(None)
        return str(self.sid)

    # ------------------------------------------------------------------ tables (cached, fail closed)

    def _table_root(self) -> Path:
        return self.root

    def _surfaces(self) -> dict:
        if "surfaces" not in self._cache:
            p = self.root / SURFACES_REL
            if not p.is_file():
                p = TOOLS.parent / SURFACES_REL
            self._cache["surfaces"] = json.loads(p.read_text(encoding="utf-8"))
        return self._cache["surfaces"]

    def _tool_file(self, rel: str) -> Path:
        p = self.root / rel
        return p if p.is_file() else TOOLS.parent / rel

    def generated_paths(self) -> Tuple[set, Tuple[str, ...], str]:
        """(exact generated paths, generated roots, generated-file marker), from the generators' own
        declarations: closure.GENERATED, build-local-skill-plugin TRACKED_ROOTS and MARKER_PREFIX, and
        the render_shims outputs in surfaces.json (a spliced block, surfaces-md-block, is not a
        whole generated file)."""
        if "generated" not in self._cache:
            exact = set(_const(self._tool_file(CLOSURE_REL), "GENERATED"))
            roots = tuple(_const(self._tool_file(PLUGIN_BUILDER_REL), "TRACKED_ROOTS"))
            marker = str(_const(self._tool_file(PLUGIN_BUILDER_REL), "MARKER_PREFIX"))
            for o in self._surfaces().get("outputs") or []:
                if isinstance(o, dict) and o.get("path") and o.get("render") != "surfaces-md-block":
                    exact.add(str(o["path"]))
            self._cache["generated"] = (exact, roots, marker)
        return self._cache["generated"]

    def guard_code(self) -> set:
        if "guard_code" not in self._cache:
            paths = set(_const(self._tool_file(PIN_LIB_REL), "PINNED_PATHS"))
            paths.update({SERVER_REL, PIN_LIB_REL.rsplit("/", 1)[0] + "/installers.py"})
            self._cache["guard_code"] = paths
        return self._cache["guard_code"]

    def employer_folders(self) -> List[str]:
        wg = _sibling("wall_guard")
        return [os.path.realpath(str(d)) for d in wg.employer_vault_folders(self._table_root())]

    def _secrets_mod(self):
        if "secrets_mod" not in self._cache:
            self._cache["secrets_mod"] = _load_path("check_secrets_for_mcp", TOOLS / "check-secrets.py")
        return self._cache["secrets_mod"]

    def _emp_rules(self):
        if "emp_rules" not in self._cache:
            cs = self._secrets_mod()
            self._cache["emp_rules"] = cs.load_emp_rules(_sibling("profile_resolve"), self._table_root())
        return self._cache["emp_rules"]

    # ------------------------------------------------------------------ path guard

    def _rel(self, path: Any) -> Tuple[str, Path]:
        """(vault-relative posix path, absolute path) or Refused. No symlink anywhere on the way."""
        if not isinstance(path, str) or not path.strip():
            raise Refused("a path is required")
        raw = path.strip()
        if "\x00" in raw:
            raise Refused("a NUL byte in the path")
        if raw.startswith("~"):
            raw = os.path.expanduser(raw) if raw.startswith("~/") or raw == "~" else raw
        p = Path(raw)
        absp = Path(os.path.normpath(str(p if p.is_absolute() else self.root / p)))
        root_s = str(self.root)
        if not (str(absp) == root_s or str(absp).startswith(root_s + os.sep)):
            # an absolute path through a linked prefix (e.g. /var -> /private/var) names the vault by its
            # real path; the link checks below then run on that real, link-free spelling
            real = os.path.realpath(str(absp))
            if real == root_s or real.startswith(root_s + os.sep):
                absp = Path(real)
        if not (str(absp) == root_s or str(absp).startswith(root_s + os.sep)):
            raise Refused(f"{path}: outside the vault (the vault root is the nearest ancestor holding AGENTS.md)")
        rel = os.path.relpath(str(absp), root_s).replace(os.sep, "/")
        rel = "" if rel == "." else rel
        cur = self.root
        for part in [x for x in rel.split("/") if x]:
            cur = cur / part
            if os.path.islink(str(cur)):
                raise Refused(f"{rel}: a symlink on the path ({os.path.relpath(str(cur), root_s)}); "
                              "the server never follows a link")
        real = os.path.realpath(str(absp))
        if not (real == root_s or real.startswith(root_s + os.sep)):
            raise Refused(f"{rel}: resolves outside the vault")
        return rel, absp

    def _employer_hit(self, absp: Path) -> Optional[str]:
        try:
            folders = self.employer_folders()
        except Exception as e:  # noqa: BLE001 - fail closed: no classification, no project folder access
            if "07-projects" in Path(absp).parts:
                return f"the employer-folder classification is unavailable ({type(e).__name__})"
            return None
        q = os.path.realpath(str(absp)).casefold()
        for d in folders:
            dl = d.casefold()
            if q == dl or q.startswith(dl + os.sep):
                return "an employer vault folder: agents never read or write it through this server"
        return None

    def guard_read(self, path: Any) -> Tuple[str, Path]:
        rel, absp = self._rel(path)
        if ".git" in rel.split("/"):
            raise Refused(f"{rel}: git internals are not served")
        why = self._employer_hit(absp)
        if why:
            raise Refused(f"{rel}: {why}")
        return rel, absp

    def write_refusal(self, rel: str, absp: Path) -> Optional[str]:
        """Why a write to this vault path is refused, or None."""
        if not rel:
            return "the vault root itself is not a file"
        parts = rel.split("/")
        if ".git" in parts:
            return "git internals (.git) are never written"
        why = self._employer_hit(absp)
        if why:
            return why
        try:
            exact, roots, marker = self.generated_paths()
            guard = self.guard_code()
        except Exception as e:  # noqa: BLE001 - fail closed
            return f"the generated-file and guard tables are unavailable ({type(e).__name__}); nothing is written"
        if rel in exact:
            return "a generated file: edit its source and run the rebuild (python3 09-tools/nightly.py --phases rebuild)"
        for r in roots:
            if rel == r or rel.startswith(r.rstrip("/") + "/"):
                return f"a generated skill wrapper under {r} (build-local-skill-plugin.py); edit 03-skills/<name>/SKILL.md"
        try:
            if absp.is_file() and marker in absp.read_text(encoding="utf-8", errors="replace")[:4096]:
                return "a generated file (it carries the generator marker)"
        except OSError:
            pass
        if rel in guard:
            return "guard code (a pinned path or this server); agents never rewrite the walls through the walls"
        wg = _sibling("wall_guard")
        for base in (self.home, self.root):
            pc = wg.protected_class(str(absp), Path(base))
            if pc:
                return f"a wall or control file ({pc[1]})"
        if absp.is_dir():
            return "a directory, not a file"
        return None

    def guard_write(self, path: Any) -> Tuple[str, Path]:
        rel, absp = self._rel(path)
        why = self.write_refusal(rel, absp)
        if why:
            raise Refused(f"{rel or path}: {why}")
        return rel, absp

    def content_refusal(self, new: str, old: str) -> Optional[str]:
        """The content may not raise the secret or employer-substance hit count of the file."""
        try:
            cs = self._secrets_mod()
            s_new, s_old = len(cs.findings_in_text(new)), len(cs.findings_in_text(old))
            rules = self._emp_rules()
            e_new, e_old = len(rules.scan_text(new)), len(rules.scan_text(old))
        except Exception as e:  # noqa: BLE001 - fail closed
            return f"the secret and employer-substance rules are unavailable ({type(e).__name__}); nothing is written"
        if s_new > s_old:
            return f"the content carries a secret shape ({s_new - s_old} new hit(s)); nothing is written"
        if e_new > e_old:
            return (f"the content carries employer substance ({e_new - e_old} new hit(s)); this vault is public "
                    "and its baseline only shrinks")
        return None

    # ------------------------------------------------------------------ ledger

    def record(self, rel: str, tool: str) -> bool:
        """One H23 ledger line for this write, stamped with the clientInfo. Nothing until telemetry/ exists."""
        try:
            wh = _sibling("ws_hook")
            target = wh.ledger_path(self.session_id(), home=self.home)
            if not target.parent.parent.is_dir():
                return False
            target.parent.mkdir(exist_ok=True)
            top = wh._repo_top(self.root) or self.root
            rec = {"repo": str(top), "path": (Path(self.root, rel).relative_to(top)).as_posix(), "tool": tool,
                   "ts": self.now().strftime("%Y-%m-%dT%H:%M:%SZ"), "host": self.host, "family": self.family,
                   "client": dict(self.client), "via": SERVER_NAME}
            fd = os.open(str(target), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
            try:
                os.write(fd, (json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))
            finally:
                os.close(fd)
            return True
        except Exception:  # noqa: BLE001 - the ledger never blocks a guarded write
            return False

    def _write(self, rel: str, absp: Path, text: str, tool: str) -> str:
        data = text.encode("utf-8")
        if len(data) > MAX_WRITE_BYTES:
            raise Refused(f"{rel}: {len(data)} bytes is over the {MAX_WRITE_BYTES}-byte limit")
        old = ""
        if absp.is_file():
            old = absp.read_text(encoding="utf-8", errors="replace")
        why = self.content_refusal(text, old)
        if why:
            raise Refused(f"{rel}: {why}")
        # create missing parents one by one inside the vault (each checked: none may be a link)
        cur = self.root
        for part in rel.split("/")[:-1]:
            cur = cur / part
            if os.path.islink(str(cur)):
                raise Refused(f"{rel}: a symlink on the path")
            if not cur.exists():
                cur.mkdir()
        mode = (absp.stat().st_mode & 0o777) if absp.is_file() else 0o644
        tmp = absp.with_name(f".{absp.name}.mcp-tmp.{os.getpid()}")
        with open(tmp, "wb") as f:
            f.write(data)
        os.chmod(tmp, mode)
        os.replace(tmp, absp)
        logged = self.record(rel, tool)
        return f"wrote {rel} ({len(data)} bytes){'' if logged else '; touch ledger not installed'}"

    # ------------------------------------------------------------------ CLIs

    def _cli(self, rel: str, args: List[str]) -> str:
        path = self._tool_file(rel)
        try:
            p = subprocess.run([sys.executable, str(path), *args], cwd=str(self.root), capture_output=True,
                               text=True, timeout=CLI_TIMEOUT_S, stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            raise Refused(f"{rel} timed out after {CLI_TIMEOUT_S}s") from None
        out = p.stdout
        if p.returncode not in (0, 1, 3) and not out.strip():
            raise Refused(f"{rel} exited {p.returncode}: {p.stderr.strip()[-400:]}")
        return out

    def route_args(self, utterance: str, fmt: str = "text") -> List[str]:
        return ["--utterance", utterance, "--host", self.host, "--brain", str(self.root), "--format", fmt]

    # ------------------------------------------------------------------ tools

    def t_session_status(self, a: dict) -> str:
        label = f"{self.client.get('name') or 'MCP client'} via {SERVER_NAME}"
        return self._cli("09-tools/session-status.py", ["--surface", label, "--via", SERVER_NAME,
                                                        "--family", self.family])

    def t_route(self, a: dict) -> str:
        u = str(a.get("utterance") or "")
        if not u.strip():
            raise Refused("route needs an utterance")
        fmt = "json" if a.get("format") == "json" else "text"
        return self._cli("09-tools/prompt_route.py", self.route_args(u, fmt))

    def t_loadset(self, a: dict) -> str:
        u = str(a.get("utterance") or "")
        if not u.strip():
            raise Refused("loadset needs an utterance")
        return self._cli("09-tools/skill-loadset.py", (["--json"] if a.get("json") else []) + [u])

    def _detection(self) -> dict:
        return {"family": self.family, "family_for_walls": self.family, "acting_host": self.host,
                "agent_possible": True, "via": SERVER_NAME, "verified": False, "determined": True,
                "conflict": False, "chain": [], "notices": []}

    def _pr_root(self) -> Optional[Path]:
        pr = _sibling("profile_resolve")
        return None if os.path.realpath(str(pr.ROOT)) == str(self.root) else self.root

    def t_resolve(self, a: dict) -> str:
        target = str(a.get("target") or "").strip()
        if not target:
            raise Refused("resolve needs a target (a path or an owner/repo slug)")
        pr = _sibling("profile_resolve")
        res = pr.repo_resolve(target, root=self._pr_root(), home=self.home, detection=self._detection())
        keep = {"owner_class": res.get("owner_class"), "role": res.get("role"), "profile": res.get("profile"),
                "positively_personal": bool(res.get("positively_personal")), "conflict": bool(res.get("conflict")),
                "classification": pr.classify_word(res)}
        return json.dumps({"target": target, **keep}, indent=2)

    def t_policy(self, a: dict) -> str:
        repo = str(a.get("repo") or "").strip()
        ac, cmd = a.get("action_class"), a.get("command")
        if not repo or bool(ac) == bool(cmd):
            raise Refused("policy needs a repo and exactly one of action_class or command")
        pr = _sibling("profile_resolve")
        d = pr.policy(repo=repo, action_class=ac or None, command=cmd or None, root=self._pr_root(),
                      home=self.home, detection=self._detection(), record=False)
        return json.dumps({k: d.get(k) for k in ("outcome", "rule_id", "reason", "route_to", "action_class")},
                          indent=2)

    def t_guard_check(self, a: dict) -> str:
        path, cmd = a.get("path"), a.get("command")
        if bool(path) == bool(cmd):
            raise Refused("guard_check needs exactly one of path or command")
        write = bool(a.get("write"))
        out: Dict[str, Any] = {"family": self.family, "host": self.host}
        if path:
            try:
                rel, absp = self._rel(path)
                why = self.write_refusal(rel, absp) if write else None
                if not write:
                    try:
                        self.guard_read(path)
                    except Refused as e:
                        why = str(e)
                out["server"] = {"decision": "refuse" if why else "allow", "reason": why or ""}
                target = str(absp)
            except Refused as e:
                out["server"] = {"decision": "refuse", "reason": str(e)}
                target = os.path.normpath(os.path.expanduser(str(path)))
            action = {"kind": "file", "path": target, "op": "write" if write else "read"}
        else:
            action = {"kind": "shell", "command": str(cmd)}
        try:
            wg, pr = _sibling("wall_guard"), _sibling("profile_resolve")
            t = wg._surfaces(self._pr_root()) or {}
            dev = pr.current_device(root=self._pr_root())["id"]
            ctx = wg.Ctx(host=self.host, det=self._detection(), device=dev, root=self._pr_root(), home=self.home,
                         cache=None, env=dict(os.environ), cwd=str(self.root), record=False,
                         cfg=wg.guard_config(t), ask_capable=False)
            dec = wg.decide(action, ctx)
            out["wall_guard"] = {k: dec.get(k) for k in ("decision", "rule", "policy_rule", "reason", "route_to")}
            out["wall_guard"]["report_only"] = [f"{f['rule']}: would-{f['outcome']}" for f in dec.get("report_only") or []]
        except Exception as e:  # noqa: BLE001
            out["wall_guard"] = {"decision": "unavailable", "reason": type(e).__name__}
        return json.dumps(out, indent=2, default=str)

    def _read_text(self, absp: Path, rel: str, head: Optional[int] = None) -> str:
        if not absp.is_file():
            raise Refused(f"{rel}: not a file")
        data = absp.read_bytes()
        note = ""
        if len(data) > MAX_READ_BYTES:
            data, note = data[:MAX_READ_BYTES], f"\n[truncated at {MAX_READ_BYTES} bytes]"
        text = data.decode("utf-8", errors="replace")
        if head:
            lines = text.splitlines(True)
            if len(lines) > head:
                text, note = "".join(lines[:head]), f"\n[first {head} of {len(lines)} lines]"
        return text + note

    def t_context_load(self, a: dict) -> str:
        sections = a.get("sections") or list(CORE_CONTEXT)
        if not isinstance(sections, list):
            raise Refused("sections must be a list of vault paths")
        out = []
        for s in sections:
            try:
                rel, absp = self.guard_read(str(s))
                if not absp.is_file():
                    continue
                head = int(a.get("log_lines") or LOG_HEAD_LINES) if rel.endswith("session-log.md") else None
                out.append(f"===== {rel} =====\n" + self._read_text(absp, rel, head).strip())
            except Refused as e:
                out.append(f"===== {s} =====\n(refused: {e})")
        return "\n\n".join(out) if out else "(no context files found)"

    def t_skills_load(self, a: dict) -> str:
        names = a.get("names") or ([a["name"]] if a.get("name") else [])
        if a.get("utterance"):
            data = json.loads(self._cli("09-tools/skill-loadset.py", ["--json", str(a["utterance"])]) or "{}")
            names = list(dict.fromkeys(list(names) + list(data.get("load") or [])))
        if not names:
            raise Refused("skills_load needs name, names or utterance")
        out = []
        for n in names[:12]:
            if not SKILL_NAME_RE.match(str(n)):
                out.append(f"===== {n} =====\n(refused: not a skill name)")
                continue
            try:
                rel, absp = self.guard_read(f"03-skills/{n}/SKILL.md")
                out.append(f"===== {rel} =====\n" + self._read_text(absp, rel).strip())
            except Refused as e:
                out.append(f"===== {n} =====\n(refused: {e})")
        return "\n\n".join(out)

    def t_read_file(self, a: dict) -> str:
        rel, absp = self.guard_read(a.get("path"))
        head = a.get("head")
        return self._read_text(absp, rel, int(head) if head else None)

    def _hidden(self, p: Path) -> bool:
        return p.name in PRUNE_DIRS or self._employer_hit(p) is not None

    def t_list_directory(self, a: dict) -> str:
        rel, absp = self.guard_read(a.get("path") or ".")
        if not absp.is_dir():
            raise Refused(f"{rel or '.'}: not a directory")
        lines = []
        for c in sorted(absp.iterdir(), key=lambda x: x.name.casefold()):
            if self._hidden(c):
                continue
            kind = "LINK" if c.is_symlink() else ("DIR" if c.is_dir() else "FILE")
            lines.append(f"[{kind}] {c.name}")
        return "\n".join(lines) or "(empty)"

    def t_search_files(self, a: dict) -> str:
        pattern = str(a.get("pattern") or "*")
        contains = a.get("contains")
        limit = min(int(a.get("max_results") or MAX_SEARCH_RESULTS), MAX_SEARCH_RESULTS)
        rel0, base = self.guard_read(a.get("path") or ".")
        if not base.is_dir():
            raise Refused(f"{rel0 or '.'}: not a directory")
        hits: List[str] = []
        for d, dirs, files in os.walk(str(base), followlinks=False):
            dp = Path(d)
            dirs[:] = sorted(x for x in dirs if not os.path.islink(os.path.join(d, x)) and not self._hidden(dp / x))
            for f in sorted(files):
                fp = dp / f
                if fp.is_symlink():
                    continue
                rel = fp.relative_to(self.root).as_posix()
                if not (fnmatch.fnmatch(f, pattern) or fnmatch.fnmatch(rel, pattern)):
                    continue
                if contains:
                    try:
                        if fp.stat().st_size > MAX_READ_BYTES or str(contains) not in fp.read_text(
                                encoding="utf-8", errors="ignore"):
                            continue
                    except OSError:
                        continue
                hits.append(rel)
                if len(hits) >= limit:
                    return "\n".join(hits) + f"\n[stopped at {limit} results]"
        return "\n".join(hits) or "(no matches)"

    def t_write_file(self, a: dict) -> str:
        content = a.get("content")
        if not isinstance(content, str):
            raise Refused("write_file needs string content")
        rel, absp = self.guard_write(a.get("path"))
        return self._write(rel, absp, content, "Write")

    def t_edit_file(self, a: dict) -> str:
        old_t, new_t = a.get("old_text"), a.get("new_text")
        if not isinstance(old_t, str) or not old_t or not isinstance(new_t, str):
            raise Refused("edit_file needs old_text (non-empty) and new_text")
        rel, absp = self.guard_write(a.get("path"))
        if not absp.is_file():
            raise Refused(f"{rel}: not a file (use write_file to create one)")
        cur = absp.read_text(encoding="utf-8")
        n = cur.count(old_t)
        if n == 0:
            raise Refused(f"{rel}: old_text not found")
        if n > 1 and not a.get("replace_all"):
            raise Refused(f"{rel}: old_text occurs {n} times; pass replace_all or a longer old_text")
        new = cur.replace(old_t, new_t) if a.get("replace_all") else cur.replace(old_t, new_t, 1)
        return self._write(rel, absp, new, "Edit")

    def t_session_end(self, a: dict) -> str:
        summary = str(a.get("summary") or "").strip()
        if not summary:
            raise Refused("session_end needs a summary")
        pr = _sibling("profile_resolve")
        now = self.now()
        date = now.strftime("%Y-%m-%d")
        try:
            dev = str(pr.current_device(root=self._pr_root())["id"] or "unknown")
            machine = pr.device_label(root=self._pr_root())
        except Exception:  # noqa: BLE001
            dev, machine = "unknown", "unknown"
        sid = f"{date}-{re.sub(r'[^a-z0-9-]', '-', dev.casefold())}-mcp-{secrets.token_hex(3)}"
        rel = f"06-context/sessions/{sid}.md"
        _rel, absp = self.guard_write(rel)
        if absp.exists():
            raise Refused(f"{rel}: already exists")

        def clean(s: str) -> str:
            return "\n".join(("  " + ln) if BLOCK_LINE_RE.match(ln) else ln for ln in s.splitlines())

        title = re.sub(r"\s+", " ", str(a.get("title") or "session via MCP")).strip()[:100]
        client = " ".join(x for x in (self.client.get("name"), self.client.get("version")) if x) or "MCP client"
        lines = [f"### {date} — {title}", "", f"SessionID: {sid}", "--- SESSION BLOCK ---", f"Date: {date}",
                 f"Machine: {machine}", f"Surface: {client} via {SERVER_NAME} ({self.host})",
                 f"Agent: {clean(str(a.get('agent') or client))} · {self.host} · {machine}"]
        if a.get("projects"):
            lines.append(f"Project(s): {clean(str(a['projects']))}")
        lines.append(f"Summary: {clean(summary)}")
        if a.get("next"):
            lines.append(f"Next: {clean(str(a['next']))}")
        lines.append("--- END BLOCK ---")
        msg = self._write(rel, absp, "\n".join(lines) + "\n", "Write")
        return f"{msg}; session recorded as fragment {rel} (compaction folds it into session-log.md)"


# --------------------------------------------------------------------------- tool table

def _obj(props: dict, required: Optional[list] = None) -> dict:
    o: Dict[str, Any] = {"type": "object", "properties": props}
    if required:
        o["required"] = required
    return o


_S = {"type": "string"}
_B = {"type": "boolean"}
_I = {"type": "integer"}
TOOLS_SPEC: List[Tuple[str, str, dict, str]] = [
    ("session_status", "The session-start card (09-tools/session-status.py) for this client's family.", _obj({}),
     "t_session_status"),
    ("route", "Layer-0 routing hints for an utterance (09-tools/prompt_route.py; same output as the CLI).",
     _obj({"utterance": _S, "format": {"type": "string", "enum": ["text", "json"]}}, ["utterance"]), "t_route"),
    ("loadset", "Ordered SKILL.md load set for an utterance (09-tools/skill-loadset.py).",
     _obj({"utterance": _S, "json": _B}, ["utterance"]), "t_loadset"),
    ("resolve", "Owner class and context profile of a repo path or owner/repo slug (status only).",
     _obj({"target": _S}, ["target"]), "t_resolve"),
    ("policy", "The action-policy answer (outcome, rule, reason, route_to) for an action class or a command on "
               "a repo. Never recorded, never executed.",
     _obj({"repo": _S, "action_class": _S, "command": _S}, ["repo"]), "t_policy"),
    ("guard_check", "What the wall guard and this server would decide for a path (read or write) or a command.",
     _obj({"path": _S, "command": _S, "write": _B}), "t_guard_check"),
    ("context_load", "The canonical workspace context in read order (or named vault files); session-log head only.",
     _obj({"sections": {"type": "array", "items": _S}, "log_lines": _I}), "t_context_load"),
    ("skills_load", "Load 03-skills/<name>/SKILL.md by name(s), or the chain skill-loadset computes for an utterance.",
     _obj({"name": _S, "names": {"type": "array", "items": _S}, "utterance": _S}), "t_skills_load"),
    ("read_file", "Read a vault file (vault only; employer folders refused).", _obj({"path": _S, "head": _I}, ["path"]),
     "t_read_file"),
    ("list_directory", "List a vault directory (employer folders and .git hidden).", _obj({"path": _S}),
     "t_list_directory"),
    ("search_files", "Find vault files by glob (name or vault-relative path), optionally containing text.",
     _obj({"pattern": _S, "path": _S, "contains": _S, "max_results": _I}, ["pattern"]), "t_search_files"),
    ("write_file", "Create or overwrite a vault file. Refuses employer folders, generated files, wall and guard "
                   "files, path escapes and symlinks, and content adding secret or employer-substance hits. "
                   "Stamped with clientInfo and recorded in the session touch ledger.",
     _obj({"path": _S, "content": _S}, ["path", "content"]), "t_write_file"),
    ("edit_file", "Replace exact text in a vault file (same guard as write_file).",
     _obj({"path": _S, "old_text": _S, "new_text": _S, "replace_all": _B}, ["path", "old_text", "new_text"]),
     "t_edit_file"),
    ("session_end", "Record this session as a 06-context/sessions/<id>.md fragment (never the shared log).",
     _obj({"summary": _S, "title": _S, "projects": _S, "next": _S, "agent": _S}, ["summary"]), "t_session_end"),
]
TOOL_NAMES = tuple(t[0] for t in TOOLS_SPEC)
INSTRUCTIONS = ("Workspace MCP (H21). Start with session_status, route the request with route or loadset, and "
                "write only through write_file, edit_file and session_end: they refuse employer folders, generated "
                "files and path escapes, and every write is attributed to this client.")


def _ok(mid: Any, result: dict) -> dict:
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def _err(mid: Any, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}


def handle(server: Server, msg: Any) -> Optional[dict]:
    if not isinstance(msg, dict):
        return _err(None, -32600, "invalid request")
    mid, method = msg.get("id"), msg.get("method")
    params = msg.get("params") if isinstance(msg.get("params"), dict) else {}
    if method == "initialize":
        server.set_client(params.get("clientInfo"))
        want = params.get("protocolVersion")
        return _ok(mid, {"protocolVersion": want if want in PROTOCOLS else PROTOCOLS[0],
                         "capabilities": {"tools": {"listChanged": False}},
                         "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                         "instructions": INSTRUCTIONS})
    if isinstance(method, str) and method.startswith("notifications/"):
        return None
    if method == "ping":
        return _ok(mid, {})
    if method == "tools/list":
        return _ok(mid, {"tools": [{"name": n, "description": d, "inputSchema": s} for n, d, s, _f in TOOLS_SPEC]})
    if method == "tools/call":
        name = params.get("name")
        spec = next((t for t in TOOLS_SPEC if t[0] == name), None)
        if spec is None:
            return _err(mid, -32602, f"unknown tool: {name}")
        args = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
        try:
            text, is_err = getattr(server, spec[3])(args), False
        except Refused as e:
            text, is_err = f"refused: {e}", True
        except Exception as e:  # noqa: BLE001 - a tool error is a result, not a protocol error
            text, is_err = f"error: {type(e).__name__}: {e}", True
        return _ok(mid, {"content": [{"type": "text", "text": text}], "isError": is_err})
    if mid is not None:
        return _err(mid, -32601, f"unknown method: {method}")
    return None


def serve(server: Server, stdin=None, stdout=None) -> int:
    rd, wr = stdin or sys.stdin, stdout or sys.stdout
    for line in rd:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            resp: Optional[dict] = _err(None, -32700, "parse error")
        else:
            resp = handle(server, msg)
        if resp is not None:
            wr.write(json.dumps(resp) + "\n")
            wr.flush()
    return 0


# --------------------------------------------------------------------------- self-test

def _fixture_vault(td: Path) -> Tuple[Path, Path]:
    """A temp vault (the real tables, a planted employer folder matched by a fixture glob) and home."""
    src = TOOLS.parent
    vault, home = td / "vault", td / "home"
    (home / ".config" / "snds-workspace" / "telemetry").mkdir(parents=True)
    for rel in ("AGENTS.md", SURFACES_REL, "02-shared-references/devices.json",
                "02-shared-references/delivery-playbooks/context-remotes.json",
                "02-shared-references/delivery-playbooks/action-policy.json",
                "02-shared-references/vetted-scripts.json"):
        dst = vault / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if (src / rel).is_file():
            dst.write_bytes((src / rel).read_bytes())
    cr = vault / "02-shared-references/delivery-playbooks/context-remotes.json"
    t = json.loads(cr.read_text(encoding="utf-8"))
    t["employer_path_globs"] = list(t.get("employer_path_globs") or []) + ["zz-emp-*"]
    cr.write_text(json.dumps(t, indent=2) + "\n", encoding="utf-8")
    for rel, body in (("07-projects/zz-emp-fixture/notes.md", "fixture\n"),
                      ("07-projects/01-personal/notes.md", "hello\n"),
                      ("03-skills/skills.registry.json", "{}\n"),
                      ("03-skills/demo/SKILL.md", "---\nname: demo\n---\nDemo skill.\n"),
                      ("06-context/sessions/README.md", "fragments\n")):
        (vault / rel).parent.mkdir(parents=True, exist_ok=True)
        (vault / rel).write_text(body, encoding="utf-8")
    (vault / ".git").mkdir()
    (td / "outside").mkdir()
    os.symlink(str(td / "outside"), str(vault / "07-projects" / "link-out"))
    return vault, home


def self_test_cases() -> List[Tuple[str, bool, str]]:
    import tempfile

    results: List[Tuple[str, bool, str]] = []

    def ok(name: str, cond: bool, detail: Any = "") -> None:
        results.append((name, bool(cond), str(detail)[:600]))

    def call(srv: Server, name: str, args: dict) -> Tuple[str, bool]:
        r = handle(srv, {"jsonrpc": "2.0", "id": 9, "method": "tools/call", "params": {"name": name, "arguments": args}})
        res = (r or {}).get("result") or {}
        return res.get("content", [{}])[0].get("text", ""), bool(res.get("isError"))

    with tempfile.TemporaryDirectory(prefix="workspace-mcp-") as tds:
        td = Path(os.path.realpath(tds))
        vault, home = _fixture_vault(td)
        fixed = dt.datetime(2026, 9, 26, 12, 0, 0, tzinfo=dt.timezone.utc)

        # 1. the JSON-RPC handshake over real stdio (initialize, notification, tools/list, tools/call)
        msgs = [{"jsonrpc": "2.0", "id": 1, "method": "initialize",
                 "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                            "clientInfo": {"name": "claude-ai", "version": "0.9.1"}}},
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                 "params": {"name": "read_file", "arguments": {"path": "07-projects/01-personal/notes.md"}}},
                {"jsonrpc": "2.0", "id": 4, "method": "nope"}]
        p = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--root", str(vault), "--home", str(home)],
                           input="".join(json.dumps(m) + "\n" for m in msgs) + "not json\n",
                           capture_output=True, text=True, timeout=60)
        try:
            resp = [json.loads(ln) for ln in p.stdout.splitlines() if ln.strip()]
        except ValueError:
            resp = []
        by_id = {r.get("id"): r for r in resp}
        init = (by_id.get(1) or {}).get("result") or {}
        ok("handshake: initialize negotiates the protocol and names the server",
           init.get("protocolVersion") == "2025-06-18" and init.get("serverInfo", {}).get("name") == SERVER_NAME
           and "tools" in init.get("capabilities", {}), p.stdout[:300] + p.stderr[-300:])
        names = [t["name"] for t in ((by_id.get(2) or {}).get("result") or {}).get("tools", [])]
        ok("handshake: tools/list carries every tool", tuple(names) == TOOL_NAMES, names)
        call3 = ((by_id.get(3) or {}).get("result") or {})
        ok("handshake: tools/call reads a vault file", call3.get("content", [{}])[0].get("text") == "hello\n"
           and not call3.get("isError"), call3)
        ok("handshake: a notification gets no reply; unknown method and bad JSON are errors",
           len(resp) == 5 and (by_id.get(4) or {}).get("error", {}).get("code") == -32601
           and (by_id.get(None) or {}).get("error", {}).get("code") == -32700, [r.get("id") for r in resp])

        # in-process server for the guard cases
        srv = Server(root=vault, home=home, now=fixed)
        handle(srv, {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                     "params": {"clientInfo": {"name": "claude-ai", "version": "0.9.1"}}})
        ok("clientInfo Claude* maps to family claude", (srv.family, srv.host) == ("claude", "claude-chat-desktop"),
           (srv.family, srv.host))
        ok("clientInfo mapping for other clients", client_family("claude-code") == ("claude", "claude-code")
           and client_family("codex-mcp-client") == ("codex", "codex")
           and client_family("local-agent-mode-workspace-mcp") == ("claude", "claude-code")
           and client_family("some-local-model") == ("unknown-agent", "mcp-clients"), "")

        text, err = call(srv, "write_file", {"path": "07-projects/zz-emp-fixture/new.md", "content": "x\n"})
        ok("employer-path write refused", err and "employer vault folder" in text
           and not (vault / "07-projects/zz-emp-fixture/new.md").exists(), text)
        text, err = call(srv, "read_file", {"path": "07-projects/zz-emp-fixture/notes.md"})
        ok("employer-path read refused", err and "employer vault folder" in text, text)
        text, err = call(srv, "list_directory", {"path": "07-projects"})
        ok("employer folder hidden from listings", not err and "zz-emp-fixture" not in text and "01-personal" in text,
           text)
        text, err = call(srv, "search_files", {"pattern": "*.md"})
        ok("employer folder hidden from search", not err and "zz-emp" not in text and "01-personal/notes.md" in text,
           text)

        for rel in ("03-skills/skills.registry.json", "02-shared-references/trigger-routes.md",
                    "06-context/session-log.md", ".claude/skills/demo/SKILL.md", "00-bootstrap/dist/codex-hooks.json",
                    ".claude/settings.json"):
            text, err = call(srv, "write_file", {"path": rel, "content": "x\n"})
            ok(f"generated-file write refused: {rel}", err and "generated" in text, text)
        for rel in ("09-tools/wall_guard.py", SERVER_REL, ".git/config", ".cursor/hooks.json"):
            text, err = call(srv, "write_file", {"path": rel, "content": "x\n"})
            ok(f"guard or control write refused: {rel}", err and "refused" in text, text)

        for pth in ("../outside/x.md", str(td / "outside" / "x.md"), "07-projects/link-out/x.md",
                    "07-projects/../../outside/x.md", "~/x.md"):
            text, err = call(srv, "write_file", {"path": pth, "content": "x\n"})
            ok(f"path escape refused: {pth.replace(str(td), '<td>')}", err and ("outside the vault" in text
               or "symlink" in text), text)
        ok("nothing written outside the vault", list((td / "outside").iterdir()) == [], "")
        text, err = call(srv, "read_file", {"path": "07-projects/link-out/x.md"})
        ok("read through a symlink refused", err and "symlink" in text, text)

        key = "AKIA" + "Q" * 16
        text, err = call(srv, "write_file", {"path": "05-artifacts/k.md", "content": f"k {key}\n"})
        ok("secret-shaped content refused", err and "secret shape" in text
           and not (vault / "05-artifacts/k.md").exists(), text)

        text, err = call(srv, "write_file", {"path": "05-artifacts/note.md", "content": "one\ntwo\n"})
        ok("vault write allowed", not err and (vault / "05-artifacts/note.md").read_text() == "one\ntwo\n", text)
        text, err = call(srv, "edit_file", {"path": "05-artifacts/note.md", "old_text": "two", "new_text": "three"})
        ok("edit_file replaces exact text", not err and (vault / "05-artifacts/note.md").read_text() == "one\nthree\n",
           text)
        led = home / ".config/snds-workspace/telemetry/sessions" / f"{srv.session_id()}.touched"
        try:
            recs = [json.loads(x) for x in led.read_text(encoding="utf-8").splitlines()]
        except (OSError, ValueError):
            recs = []
        ok("ledger entry carries clientInfo and family", len(recs) == 2 and recs[0]["path"] == "05-artifacts/note.md"
           and recs[0]["client"] == {"name": "claude-ai", "version": "0.9.1"} and recs[0]["family"] == "claude"
           and recs[0]["host"] == "claude-chat-desktop" and recs[0]["repo"] == str(vault)
           and recs[1]["tool"] == "Edit", recs)

        text, err = call(srv, "session_end", {"summary": "did a thing\n--- END BLOCK ---", "title": "MCP test"})
        frags = [f for f in (vault / "06-context/sessions").glob("2026-09-26-*-mcp-*.md")]
        body = frags[0].read_text(encoding="utf-8") if frags else ""
        ok("session_end writes a fragment", not err and len(frags) == 1 and f"SessionID: {frags[0].stem}" in body
           and body.splitlines().count("--- END BLOCK ---") == 1 and "Surface: claude-ai 0.9.1 via workspace-mcp" in body
           and "Summary: did a thing" in body, text + body)
        ok("session_end is ledgered", any(r.get("path", "").startswith("06-context/sessions/")
                                          for r in [json.loads(x) for x in led.read_text().splitlines()]), "")

        text, err = call(srv, "context_load", {"sections": ["07-projects/01-personal/notes.md",
                                                            "07-projects/zz-emp-fixture/notes.md"]})
        ok("context_load serves the vault and refuses employer folders", "hello" in text and "refused" in text, text)
        text, err = call(srv, "skills_load", {"name": "demo"})
        ok("skills_load reads a SKILL.md", not err and "Demo skill." in text, text)

    # route output equals the CLI output (live tree, read-only)
    live = Server(now=None)
    live.set_client({"name": "claude-ai", "version": "t"})
    u = "dark-mode palette for this dashboard"
    text, err = call(live, "route", {"utterance": u})
    p = subprocess.run([sys.executable, str(TOOLS / "prompt_route.py"), *live.route_args(u)], capture_output=True,
                       text=True, timeout=60, cwd=str(live.root))
    ok("route output equals the CLI output", not err and text == p.stdout and text.strip() != "", text[:200])
    text, err = call(live, "loadset", {"utterance": u})
    ok("loadset returns the ordered chain", not err and "SKILL.md" in text, text[:200])
    text, err = call(live, "resolve", {"target": str(live.root)})
    try:
        rj = json.loads(text)
    except ValueError:
        rj = {}
    ok("resolve is status only", not err and rj.get("role") == "workspace" and "path" not in rj and "remotes" not in rj
       and "reasons" not in rj, text[:300])
    return results


def self_test() -> int:
    results = self_test_cases()
    fails = [r for r in results if not r[1]]
    for name, good, detail in results:
        if not good:
            print(f"FAIL {name}: {detail}")
    print(f"{'OK' if not fails else 'FAIL'} workspace_mcp self-test — {len(results) - len(fails)}/{len(results)} cases")
    return 0 if not fails else 1


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="workspace_mcp.py", description="workspace MCP server (stdio)")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--root", help="vault root (default: the nearest ancestor of this file holding AGENTS.md)")
    ap.add_argument("--home", help="home directory for the touch ledger (tests)")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    return serve(Server(root=Path(a.root) if a.root else None, home=Path(a.home) if a.home else None))


if __name__ == "__main__":
    sys.exit(main())
