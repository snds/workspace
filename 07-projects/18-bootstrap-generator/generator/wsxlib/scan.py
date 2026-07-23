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

# Known agentic tools: a PATH binary and/or a config dir signals "installed".
# `surface` maps to the wsx emit target that fits the tool.
AGENTS = [
    {"id": "claude-code", "name": "Claude Code", "bins": ["claude"],
     "paths": ["~/.claude", "~/.claude.json"], "surface": "claude-code"},
    {"id": "cursor", "name": "Cursor", "bins": ["cursor"],
     "paths": ["~/.cursor", "/Applications/Cursor.app"], "surface": "cursor"},
    {"id": "codex", "name": "OpenAI Codex CLI", "bins": ["codex"],
     "paths": ["~/.codex"], "surface": "agents-md"},
    {"id": "gemini", "name": "Gemini CLI", "bins": ["gemini"],
     "paths": ["~/.gemini"], "surface": "agents-md"},
    {"id": "copilot", "name": "GitHub Copilot", "bins": ["copilot"],
     "paths": ["~/.config/github-copilot"], "surface": "agents-md"},
    {"id": "windsurf", "name": "Windsurf", "bins": ["windsurf"],
     "paths": ["/Applications/Windsurf.app", "~/.codeium"], "surface": "agents-md"},
    {"id": "aider", "name": "Aider", "bins": ["aider"], "paths": [], "surface": "agents-md"},
    {"id": "continue", "name": "Continue", "bins": [], "paths": ["~/.continue"], "surface": "mcp"},
]

# Local model servers, by their well-known localhost OpenAI-ish endpoints.
LOCAL_LLMS = [
    {"id": "ollama", "name": "Ollama", "url": "http://localhost:11434/api/tags",
     "list_key": "models", "name_field": "name"},
    {"id": "lmstudio", "name": "LM Studio", "url": "http://localhost:1234/v1/models",
     "list_key": "data", "name_field": "id"},
    {"id": "jan", "name": "Jan", "url": "http://localhost:1337/v1/models",
     "list_key": "data", "name_field": "id"},
]


def _which(bins) -> str | None:
    for b in bins:
        if shutil.which(b):
            return b
    return None


def _exists(paths) -> bool:
    return any(Path(p).expanduser().exists() for p in paths)


def _detect_agents() -> list:
    found = []
    for a in AGENTS:
        hit_bin = _which(a["bins"]) if a["bins"] else None
        hit_path = _exists(a["paths"]) if a["paths"] else False
        if hit_bin or hit_path:
            found.append({"id": a["id"], "name": a["name"], "surface": a["surface"],
                          "via": "PATH" if hit_bin else "config"})
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
    """Advisory pre-fill for surfaces/models — the brain confirms with the user."""
    order = ["claude-code", "cursor", "codex", "gemini", "copilot", "windsurf", "aider", "continue"]
    ranked = sorted(agents, key=lambda a: order.index(a["id"]) if a["id"] in order else 99)
    surfaces = []
    for a in ranked:
        if a["surface"] not in surfaces:
            surfaces.append(a["surface"])
    tier = "frontier" if ranked else ("small-local" if local else "")
    if ranked and local:
        tier = "mixed"
    return {
        "surfaces.primary": ranked[0]["surface"] if ranked else ("mcp" if local else ""),
        "surfaces.agents": surfaces or (["mcp"] if local else []),
        "models.tier": tier,
        "models.offline": bool(local and not ranked),
    }


def scan(root: Path | None, as_json: bool = False, write: bool = False) -> int:
    agents = _detect_agents()
    mcp = _detect_mcp()
    local = _detect_local_llms()
    report = {"agents": agents, "mcp": mcp, "local_llms": local,
              "needs_setup": _needs_setup(agents, local),
              "suggested": _suggest(agents, local)}

    if as_json:
        print(json.dumps(report, indent=2))
    else:
        _print_human(agents, mcp, local, report["suggested"])
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

    print("AI coding tools:")
    if agents:
        for a in agents:
            print(f"  ✓ {a['name']}  (found via {a['via']} → emits `{a['surface']}`)")
    else:
        print("  — none detected on PATH or in the usual config locations.")

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
        print("  — none responding (Ollama :11434, LM Studio :1234, Jan :1337).")

    print("\nSuggested (the interview will confirm with you, and you can override):")
    print(f"  primary surface : {sugg['surfaces.primary'] or '(ask the user)'}")
    print(f"  emit targets    : {', '.join(sugg['surfaces.agents']) or '(ask the user)'}")
    print(f"  model tier      : {sugg['models.tier'] or '(ask the user)'}"
          f"{'  · offline-capable' if sugg['models.offline'] else ''}")
    print("\nThese are YOUR tools/accounts. Bring your own tokens; the generator supplies none.")


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
