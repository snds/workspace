"""`wsx scan` — detect the user's own agentic stack so the interview can pre-fill it.

Three detectors, all best-effort and zero-dependency (stdlib only):
  * agents        — installed AI coding tools (PATH binaries + known config dirs)
  * mcp           — configured MCP integrations (server NAMES only — never values)
  * local_llms    — local model servers, by probing localhost with a short timeout

Reinforces the BYO-tokens model: the generator has no API key and makes no model
calls — it detects *your* tools and *your* accounts, and a local model (Ollama /
LM Studio) means fully-private, zero-token-cost operation.

SECURITY: MCP config files can contain API keys in server `env` blocks. This module
reads only the *names* of configured servers (the keys of `mcpServers`) and never
reads, prints, or stores any value/env — so no secret can leak through a scan.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

HOME = Path.home()

# macOS app bundles live here; Windows/Linux fall back to bins + config paths.
APP_DIRS = [Path("/Applications"), HOME / "Applications"]
# VS Code / Cursor extension roots — where editor-embedded agents (Cline, Roo, Cody) install.
EXT_DIRS = [HOME / ".vscode/extensions", HOME / ".vscode-insiders/extensions",
            HOME / ".cursor/extensions", HOME / ".windsurf/extensions"]

# Known agentic tools. A PATH binary, a config dir, a macOS .app, or an installed
# editor extension signals "installed". `surface` maps to the wsx emit target that
# fits the tool; `kind` is coding (drives files) vs chat (paste a context pack).
#   coding agents  → read AGENTS.md / native config / MCP  → surface = that target
#   chat/desktop   → no file-reading → surface = pack (paste `wsx emit pack`)
AGENTS = [
    # --- coding agents (read files / MCP) ---------------------------------------
    {"id": "claude-code", "name": "Claude Code", "kind": "coding", "bins": ["claude"],
     "paths": ["~/.claude", "~/.claude.json"], "surface": "claude-code"},
    {"id": "cursor", "name": "Cursor", "kind": "coding", "bins": ["cursor"],
     "paths": ["~/.cursor"], "apps": ["Cursor.app"], "surface": "cursor"},
    {"id": "codex", "name": "OpenAI Codex CLI", "kind": "coding", "bins": ["codex"],
     "paths": ["~/.codex"], "surface": "agents-md"},
    {"id": "gemini", "name": "Gemini CLI", "kind": "coding", "bins": ["gemini"],
     "paths": ["~/.gemini"], "surface": "agents-md"},
    {"id": "copilot", "name": "GitHub Copilot CLI", "kind": "coding", "bins": ["copilot"],
     "paths": ["~/.config/github-copilot"], "surface": "agents-md"},
    {"id": "windsurf", "name": "Windsurf", "kind": "coding", "bins": ["windsurf"],
     "paths": ["~/.codeium"], "apps": ["Windsurf.app"], "surface": "agents-md"},
    {"id": "zed", "name": "Zed", "kind": "coding", "bins": ["zed"],
     "paths": ["~/.config/zed"], "apps": ["Zed.app"], "surface": "agents-md"},
    {"id": "aider", "name": "Aider", "kind": "coding", "bins": ["aider"],
     "paths": ["~/.aider"], "surface": "agents-md"},
    {"id": "amazon-q", "name": "Amazon Q Developer", "kind": "coding", "bins": ["q"],
     "paths": ["~/.aws/amazonq"], "surface": "agents-md"},
    {"id": "continue", "name": "Continue", "kind": "coding", "bins": [],
     "paths": ["~/.continue"], "exts": ["continue.continue"], "surface": "mcp"},
    {"id": "cline", "name": "Cline", "kind": "coding", "bins": [],
     "exts": ["saoudrizwan.claude-dev"], "surface": "mcp"},
    {"id": "roo", "name": "Roo Code", "kind": "coding", "bins": [],
     "exts": ["rooveterinaryinc.roo-cline"], "surface": "mcp"},
    {"id": "cody", "name": "Sourcegraph Cody", "kind": "coding", "bins": ["cody"],
     "exts": ["sourcegraph.cody-ai"], "surface": "mcp"},
    # --- chat / desktop apps (no file-reading → paste a context pack) ------------
    {"id": "chatgpt", "name": "ChatGPT (desktop)", "kind": "chat", "bins": ["chatgpt"],
     "paths": ["~/Library/Application Support/com.openai.chat"],
     "apps": ["ChatGPT.app"], "surface": "pack"},
    {"id": "claude-desktop", "name": "Claude (desktop)", "kind": "chat", "bins": [],
     "paths": ["~/Library/Application Support/Claude"],
     "apps": ["Claude.app"], "surface": "pack"},
    {"id": "perplexity", "name": "Perplexity (desktop)", "kind": "chat", "bins": [],
     "apps": ["Perplexity.app"], "surface": "pack"},
    {"id": "copilot-app", "name": "Microsoft Copilot (desktop)", "kind": "chat", "bins": [],
     "apps": ["Copilot.app", "Microsoft Copilot.app"], "surface": "pack"},
    {"id": "msty", "name": "Msty", "kind": "chat", "bins": [],
     "apps": ["Msty.app"], "surface": "pack"},
    {"id": "cherry-studio", "name": "Cherry Studio", "kind": "chat", "bins": [],
     "apps": ["Cherry Studio.app"], "surface": "pack"},
]

# Local model servers, by their well-known localhost OpenAI-ish endpoints. Kept to
# DISTINCTIVE ports (avoid 8000/8080 which collide with unrelated dev servers, to
# not false-positive a running app as a local LLM).
LOCAL_LLMS = [
    {"id": "ollama", "name": "Ollama", "url": "http://localhost:11434/api/tags",
     "list_key": "models", "name_field": "name"},
    {"id": "lmstudio", "name": "LM Studio", "url": "http://localhost:1234/v1/models",
     "list_key": "data", "name_field": "id"},
    {"id": "jan", "name": "Jan", "url": "http://localhost:1337/v1/models",
     "list_key": "data", "name_field": "id"},
    {"id": "gpt4all", "name": "GPT4All", "url": "http://localhost:4891/v1/models",
     "list_key": "data", "name_field": "id"},
    {"id": "textgen", "name": "Text-Generation-WebUI", "url": "http://localhost:5000/v1/models",
     "list_key": "data", "name_field": "id"},
]


def _which(bins) -> str | None:
    for b in bins:
        if shutil.which(b):
            return b
    return None


def _exists(paths) -> bool:
    return any(Path(p).expanduser().exists() for p in paths)


def _app_exists(apps) -> bool:
    """macOS-only: is any of these .app bundles installed?"""
    if not apps or sys.platform != "darwin":
        return False
    return any((d / a).exists() for a in apps for d in APP_DIRS)


def _ext_exists(exts) -> bool:
    """Is any editor extension id installed (dir name starts with the publisher.id)?"""
    if not exts:
        return False
    for d in EXT_DIRS:
        if not d.is_dir():
            continue
        try:
            names = [p.name.lower() for p in d.iterdir()]
        except OSError:
            continue
        for e in exts:
            if any(n.startswith(e.lower()) for n in names):
                return True
    return False


def _detect_agents() -> list:
    found = []
    for a in AGENTS:
        hit_bin = _which(a["bins"]) if a.get("bins") else None
        hit_path = _exists(a["paths"]) if a.get("paths") else False
        hit_app = _app_exists(a.get("apps"))
        hit_ext = _ext_exists(a.get("exts"))
        if hit_bin or hit_path or hit_app or hit_ext:
            via = ("PATH" if hit_bin else "app" if hit_app
                   else "extension" if hit_ext else "config")
            found.append({"id": a["id"], "name": a["name"], "kind": a.get("kind", "coding"),
                          "surface": a["surface"], "via": via})
    return found


def _mcp_config_paths() -> list:
    paths = []
    if sys.platform == "darwin":
        paths.append(HOME / "Library/Application Support/Claude/claude_desktop_config.json")
    elif os.name == "nt":
        appdata = os.environ.get("APPDATA", "")
        if appdata:
            paths.append(Path(appdata) / "Claude/claude_desktop_config.json")
    else:
        paths.append(HOME / ".config/Claude/claude_desktop_config.json")
    paths += [HOME / ".cursor/mcp.json", HOME / ".claude.json"]
    return paths


def _detect_mcp() -> dict:
    """Return {config_path: [server names]} — NAMES ONLY, never values/env (secrets)."""
    out = {}
    for cfg in _mcp_config_paths():
        if not cfg.exists():
            continue
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        servers = data.get("mcpServers")
        if isinstance(servers, dict) and servers:
            out[_tilde(cfg)] = sorted(servers.keys())   # keys only — no env/args read
    return out


def _probe(url: str, timeout: float = 0.5):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:  # noqa: S310
            return json.loads(r.read())
    except (urllib.error.URLError, OSError, ValueError):
        return None


def _detect_local_llms() -> list:
    found = []
    for l in LOCAL_LLMS:
        data = _probe(l["url"])
        if not isinstance(data, dict):
            continue
        items = data.get(l["list_key"], []) or []
        models = [it.get(l["name_field"]) for it in items
                  if isinstance(it, dict) and it.get(l["name_field"])][:8]
        found.append({"id": l["id"], "name": l["name"], "models": models})
    return found


def _tilde(p: Path) -> str:
    s = str(p)
    return s.replace(str(HOME), "~", 1) if s.startswith(str(HOME)) else s


# When nothing is detected, recommend a surface BEFORE the interview — the generator
# leans on the chosen assistant for the interview, synthesis, and composite authoring,
# so a capable one directly yields a better workspace. Prioritized best-outcome-first.
RECOMMENDED_SURFACES = [
    ("Claude Code", "recommended — the fully-tested path here; richest setup and best "
     "authoring quality", "the Claude desktop app, or https://claude.com/claude-code"),
    ("Cursor", "a popular AI code editor; reads AGENTS.md + MCP out of the box",
     "https://cursor.com"),
    ("A frontier chat + AGENTS.md/pack", "Claude, ChatGPT, or Gemini in the browser — "
     "drive it with the emitted AGENTS.md or context pack", "your existing account"),
    ("A local model (Ollama)", "fully private, zero token cost — but a frontier model "
     "produces noticeably richer skills; best as a complement", "https://ollama.com"),
]


def _needs_setup(agents: list, local: list) -> bool:
    return not agents and not local


def _suggest(agents: list, local: list) -> dict:
    """Advisory pre-fill for surfaces/models — the brain confirms with the user.

    Prefer a coding agent (drives files directly) as the primary surface; a chat-only
    app (ChatGPT/Perplexity/…) still counts, but its best delivery is a pasted pack.
    """
    order = ["claude-code", "cursor", "codex", "gemini", "copilot", "windsurf", "zed",
             "aider", "amazon-q", "continue", "cline", "roo", "cody"]
    coding = [a for a in agents if a.get("kind", "coding") == "coding"]
    chat = [a for a in agents if a.get("kind") == "chat"]
    ranked = sorted(coding, key=lambda a: order.index(a["id"]) if a["id"] in order else 99)
    surfaces = []
    for a in ranked + chat:
        if a["surface"] not in surfaces:
            surfaces.append(a["surface"])
    if ranked:
        primary = ranked[0]["surface"]
    elif chat:
        primary = "pack"
    elif local:
        primary = "mcp"
    else:
        primary = ""
    tier = "frontier" if (ranked or chat) else ("small-local" if local else "")
    if (ranked or chat) and local:
        tier = "mixed"
    return {
        "surfaces.primary": primary,
        "surfaces.agents": surfaces or (["mcp"] if local else []),
        "models.tier": tier,
        "models.offline": bool(local and not ranked and not chat),
    }


# ---------------------------------------------------------- workspace discovery ---
# Common places a wsx workspace tends to live. Searched shallowly (bounded depth) so
# "help me update my workspace" can OFFER the existing one instead of asking cold.
def _search_roots() -> list:
    roots = [HOME / d for d in ("Documents", "Projects", "projects", "obsidian",
                                "Obsidian", "vaults", "Vaults", "Desktop", "Notes")]
    roots.append(HOME)
    # Obsidian's iCloud vault location (macOS)
    roots.append(HOME / "Library/Mobile Documents/iCloud~md~obsidian/Documents")
    return [r for r in roots if r.is_dir()]


_SKIP_WALK = {".git", "node_modules", "Library", ".Trash", ".cache", "venv", ".venv",
              "__pycache__", "dist", "build", "target", ".obsidian"}


def _is_workspace(d: Path) -> dict | None:
    """A wsx workspace = a dir with manifest.json + context/. Returns a summary or None."""
    man = d / "manifest.json"
    if not (man.exists() and (d / "context").is_dir()):
        return None
    info = {"path": _tilde(d), "name": d.name, "skills": 0, "generator": "",
            "has_git": (d / ".git").exists()}
    try:
        data = json.loads(man.read_text(encoding="utf-8"))
        info["generator"] = data.get("generator", "")
        info["name"] = data.get("workspace", {}).get("name", d.name)
        info["skills"] = len(data.get("skills", {}) or {})
    except (OSError, json.JSONDecodeError):
        pass
    return info


def find_workspaces(max_depth: int = 3) -> list:
    """Shallow-walk the common roots for wsx workspaces. Deduped, best-effort."""
    found, seen = [], set()
    for base in _search_roots():
        base = base.resolve()
        # bounded BFS so we never crawl the whole disk
        stack = [(base, 0)]
        while stack:
            d, depth = stack.pop()
            hit = _is_workspace(d)
            if hit and str(d) not in seen:
                seen.add(str(d))
                found.append(hit)
                continue  # don't descend into a workspace
            if depth >= max_depth:
                continue
            try:
                for child in d.iterdir():
                    if child.is_dir() and child.name not in _SKIP_WALK \
                            and not child.name.startswith("."):
                        stack.append((child, depth + 1))
            except (OSError, PermissionError):
                continue
    found.sort(key=lambda w: (-w["skills"], w["path"]))
    return found


def scan(root: Path | None, as_json: bool = False, write: bool = False,
         find_ws: bool = False) -> int:
    agents = _detect_agents()
    mcp = _detect_mcp()
    local = _detect_local_llms()
    report = {"agents": agents, "mcp": mcp, "local_llms": local,
              "needs_setup": _needs_setup(agents, local),
              "suggested": _suggest(agents, local)}
    if find_ws:
        report["workspaces"] = find_workspaces()

    if as_json:
        print(json.dumps(report, indent=2))
    else:
        _print_human(agents, mcp, local, report["suggested"])
        if find_ws:
            _print_workspaces(report["workspaces"])
        if report["needs_setup"]:
            _print_recommendation()

    if write and root is not None:
        out = root / "context" / "scan.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(f"\n✓ wrote {_rel(out, root)} — the interview reads this to pre-fill your setup.")
    return 0


def _print_human(agents: list, mcp: dict, local: list, sugg: dict) -> None:
    print("wsx scan — detecting YOUR agentic stack (nothing here uses the generator's")
    print("API or any key; it drives the tools and accounts you already have).\n")

    coding = [a for a in agents if a.get("kind", "coding") == "coding"]
    chat = [a for a in agents if a.get("kind") == "chat"]

    print("AI coding tools (drive the workspace files directly):")
    if coding:
        for a in coding:
            print(f"  ✓ {a['name']}  (found via {a['via']} → emits `{a['surface']}`)")
    else:
        print("  — none detected on PATH or in the usual config locations.")

    print("\nChat / desktop assistants (no file access → paste a context pack):")
    if chat:
        for a in chat:
            print(f"  ✓ {a['name']}  (found via {a['via']} → `wsx emit pack`)")
    else:
        print("  — none detected (ChatGPT, Claude, Perplexity, …).")

    print("\nMCP integrations (server names only — no keys/values are read):")
    if mcp:
        for cfg, names in mcp.items():
            print(f"  ✓ {cfg}: {', '.join(names)}")
    else:
        print("  — no MCP server configs found.")

    print("\nLocal LLMs (probed on localhost):")
    if local:
        for l in local:
            models = ", ".join(m for m in l["models"] if m) or "(running, no models listed)"
            print(f"  ✓ {l['name']}: {models}")
        print("  → a local model runs fully offline at zero token cost — your data never leaves.")
    else:
        print("  — none responding (Ollama :11434, LM Studio :1234, Jan :1337, "
              "GPT4All :4891, TextGen :5000).")

    print("\nSuggested (the interview will confirm with you, and you can override):")
    print(f"  primary surface : {sugg['surfaces.primary'] or '(ask the user)'}")
    print(f"  emit targets    : {', '.join(sugg['surfaces.agents']) or '(ask the user)'}")
    print(f"  model tier      : {sugg['models.tier'] or '(ask the user)'}"
          f"{'  · offline-capable' if sugg['models.offline'] else ''}")
    print("\nThese are YOUR tools/accounts. Bring your own tokens; the generator supplies none.")


def _print_workspaces(workspaces: list) -> None:
    print("\nExisting workspaces found (to update one, `cd` into it → `wsx upgrade`):")
    if not workspaces:
        print("  — none found in the usual places. If you have one elsewhere, `cd` into")
        print("    it and run `wsx upgrade`; or `wsx init <dir>` to make a new one.")
        return
    for w in workspaces:
        tag = "" if w["generator"] == "wsx" else "  (not wsx-generated?)"
        git = "git" if w["has_git"] else "no-git"
        print(f"  ✓ {w['name']}  → {w['path']}  ({w['skills']} skill(s), {git}){tag}")


def _print_recommendation() -> None:
    print("\n" + "─" * 68)
    print("⚠  No AI assistant or local model detected on this machine.")
    print("   The generator uses your assistant to do the heavy lifting — the")
    print("   interview, the synthesis, and authoring your skills. For the best")
    print("   possible workspace, set one up FIRST, then re-run `wsx scan`:")
    print()
    for i, (name, why, where) in enumerate(RECOMMENDED_SURFACES, 1):
        print(f"   {i}. {name} — {why}")
        print(f"      → {where}")
    print()
    print("   A capable frontier model (Claude, etc.) gives the richest result; a")
    print("   local model works and is fully private. Either way it's YOUR account.")
    print("   (No assistant at all? You can still scaffold a starter workspace with")
    print("   `wsx init` and grow it once you've set one up.)")
    print("─" * 68)


def _rel(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except ValueError:
        return str(p)
