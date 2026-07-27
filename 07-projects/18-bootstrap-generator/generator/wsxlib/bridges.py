"""`wsx bridge` — connect the workspace to the OTHER AI tools a person uses.

Two directions, both non-destructive:

  * **extract** — READ a tool's own memory/instructions and copy them, read-only, into
    `.wsx/quarantine/<tool>/` (gitignored). Nothing is promoted into the vault: quarantine
    is a staging area that the consent-gated ingestion pass (P6) scans + classifies before
    anything is ever tracked. So a bridge can surface "here's what Cursor/Copilot/ChatGPT
    already remember about you" without risking the public repo.
  * **point** — WRITE an idempotent, marker-delimited pointer into the tool's OWN global
    config, so that tool — used anywhere, on any model — re-anchors to this workspace
    ("your second brain is at <path>; read it first"). Reinforces the identity anchor
    beyond the vault dir. Append-only within markers; never clobbers the person's config.

Tool detection reuses `scan` (PATH bins / config dirs / macOS apps). Memory locations and
pointer files are best-known per tool and labelled by confidence — a bridge never asserts
a path it didn't find on disk.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from . import core, layout, scan

HOME = Path.home()

# Per-tool bridge data, keyed by the scan AGENTS id. `memory` = candidate files/dirs that
# hold the tool's own instructions/memory (extracted to quarantine if present). `pointer`
# = a global instruction file the tool reads every session, where we append the workspace
# pointer (None → we can't write safely, so we print guidance instead). `confidence` is
# how sure we are of these paths.
BRIDGES = {
    "claude-code": {"memory": ["~/.claude/CLAUDE.md"],
                    "pointer": "~/.claude/CLAUDE.md", "confidence": "high"},
    "codex": {"memory": ["~/.codex/AGENTS.md", "~/.codex/instructions.md"],
              "pointer": "~/.codex/AGENTS.md", "confidence": "medium"},
    "gemini": {"memory": ["~/.gemini/GEMINI.md"],
               "pointer": "~/.gemini/GEMINI.md", "confidence": "medium"},
    "cursor": {"memory": ["~/.cursor/rules", "~/.cursor/User"], "pointer": None,
               "guidance": "Cursor reads a project's `.cursor/rules` automatically — open "
                           "the workspace folder in Cursor (its rule is already emitted).",
               "confidence": "low"},
    "copilot": {"memory": ["~/.config/github-copilot"], "pointer": None,
                "guidance": "Point Copilot at the workspace's emitted AGENTS.md (open the "
                            "folder as a workspace).", "confidence": "low"},
    "windsurf": {"memory": ["~/.codeium/memories", "~/.codeium"], "pointer": None,
                 "guidance": "Windsurf reads AGENTS.md / its rules from an opened folder.",
                 "confidence": "low"},
    "continue": {"memory": ["~/.continue"], "pointer": None,
                 "guidance": "Add the workspace's MCP server (adapters/mcp/) to Continue.",
                 "confidence": "low"},
    "cline": {"memory": [], "pointer": None,
              "guidance": "Add the workspace's MCP server (adapters/mcp/) in Cline settings.",
              "confidence": "low"},
    "roo": {"memory": [], "pointer": None,
            "guidance": "Add the workspace's MCP server (adapters/mcp/) in Roo settings.",
            "confidence": "low"},
    "aider": {"memory": ["~/.aider.conf.yml"], "pointer": None,
              "guidance": "Run Aider from the workspace folder; it reads CONVENTIONS/AGENTS.",
              "confidence": "low"},
    "chatgpt": {"memory": ["~/Library/Application Support/com.openai.chat"], "pointer": None,
                "guidance": "Desktop chat app (no file config) — paste `wsx emit pack`, or "
                            "add the vault as a Project's files.", "confidence": "low"},
    "claude-desktop": {"memory": ["~/Library/Application Support/Claude"], "pointer": None,
                       "guidance": "Add the workspace MCP server to Claude Desktop's config, "
                                   "or paste `wsx emit pack`.", "confidence": "low"},
    "perplexity": {"memory": [], "pointer": None,
                   "guidance": "No local config — paste `wsx emit pack` when you need it.",
                   "confidence": "low"},
}

_POINTER_START = "<!-- wsx:workspace-pointer:start -->"
_POINTER_END = "<!-- wsx:workspace-pointer:end -->"
# Files we never copy out of a tool's config (secret-bearing).
_SECRET_HINTS = (".env", ".pem", ".key", "token", "secret", "credential", "id_rsa",
                 "cookies", ".sqlite", ".db")
_EXTRACT_EXT = {".md", ".markdown", ".txt", ".json", ".yml", ".yaml", ".toml", ".mdc"}


def _name(tid: str) -> str:
    for a in scan.AGENTS:
        if a["id"] == tid:
            return a["name"]
    return tid


def _installed_ids() -> set:
    return {a["id"] for a in scan._detect_agents()}


def quarantine_dir(root: Path) -> Path:
    return root / ".wsx" / "quarantine"


def _looks_secret(name: str) -> bool:
    low = name.lower()
    return any(h in low for h in _SECRET_HINTS)


def _pointer_block(root: Path) -> str:
    prof = core.load_profile(root)
    name = str(prof.get("identity", {}).get("name", "you"))
    lay = layout.of(root)
    c = lay.name("context")
    front = "CLAUDE.md" if (root / "CLAUDE.md").exists() else "AGENTS.md"
    # Prescriptive but token-FRUGAL: the whole point of a global pointer is that it loads
    # every session/window (even outside the vault), so it must orient WITHOUT itself being
    # expensive. It names the hot-cache + the frugal read order + the privacy wall — the
    # exact "auto-orient at session start" behavior, not just a location.
    return "\n".join([
        _POINTER_START,
        f"## {name}'s workspace / second brain — orient here at session start",
        f"{name}'s personal **workspace** (second brain / micro-brain / knowledge base) lives at:",
        f"  `{root}`",
        "**At the start of every session/window, orient from it** (do this on your own — don't",
        f"wait to be asked): read `{root}/{c}/CRITICAL_FACTS.md` FIRST (the tiny always-on hot",
        f"cache), then skim the TOP of `{c}/project-context.md` + `{c}/session-log.md` for the",
        f"active work, and follow the vault's `{front}`. Keep it light — heads of logs, not whole",
        "files (the vault is token-frugal by rule).",
        f"**Voice:** honor `{lay.name('preferences')}/user-preferences.md` — its Voice + \"Never do",
        f"these\" list is how {name} wants to be spoken to, in every reply (not a generic default).",
        f"**Privacy wall:** never read `{c}/personal.md` unless {name} explicitly asks.",
        f"When {name} says \"workspace\", \"second brain\", \"micro-brain\", \"my notes\", or asks to",
        "gather/recall across their work, that means **this vault** — resolve it here, NOT a",
        "commercial connector (Notion/Confluence/Drive/Slack/…) unless explicitly named.",
        _POINTER_END,
    ]) + "\n"


# -------------------------------------------------------------------- extract ---
def _extract_one(root: Path, tid: str) -> dict:
    b = BRIDGES.get(tid, {})
    qdir = quarantine_dir(root) / tid
    sources, copied = [], 0
    for rel in b.get("memory", []):
        src = Path(rel.replace("~", str(HOME))).expanduser()
        if not src.exists():
            continue
        files = [src] if src.is_file() else [p for p in src.rglob("*") if p.is_file()]
        for f in files:
            if _looks_secret(f.name) or f.suffix.lower() not in _EXTRACT_EXT:
                continue
            try:
                data = f.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            rel_name = f.name if src.is_file() else "__".join(f.relative_to(src).parts)
            dst = qdir / rel_name
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(data, encoding="utf-8")
            try:
                dst.chmod(0o444)  # read-only: quarantine is staging, not editable
            except OSError:
                pass
            sources.append(str(f))
            copied += 1
    if copied:
        qdir.mkdir(parents=True, exist_ok=True)
        man = qdir / "_manifest.json"
        # manifest is metadata → keep writable
        man.write_text(json.dumps(
            {"tool": tid, "name": _name(tid), "extracted_at": core.now_stamp(),
             "sources": sources, "note": "READ-ONLY staging. Not tracked, not in the vault. "
             "The consent-gated ingestion pass scans + classifies before anything is kept."},
            indent=2) + "\n", encoding="utf-8")
    return {"tool": tid, "copied": copied, "sources": sources}


def extract(root: Path, tool: str = "") -> int:
    installed = _installed_ids()
    targets = [tool] if tool else [t for t in BRIDGES if t in installed]
    if tool and tool not in BRIDGES:
        raise SystemExit(f"error: unknown tool '{tool}'. Known: {', '.join(sorted(BRIDGES))}")
    print("wsx bridge extract — copying each tool's own memory into read-only quarantine\n")
    print(f"  (staging at {quarantine_dir(root).relative_to(root)}/ — gitignored, NOT in the")
    print("   vault. Consent-gated ingestion scans + classifies it before anything is kept.)\n")
    total = 0
    for tid in targets:
        r = _extract_one(root, tid)
        total += r["copied"]
        if r["copied"]:
            print(f"  ✓ {_name(tid):22} {r['copied']} file(s) → .wsx/quarantine/{tid}/")
        elif tool:
            print(f"  · {_name(tid):22} no readable memory found at the known locations.")
    if not total:
        print("  (nothing extracted — no known tool-memory files were present.)")
    else:
        print(f"\n  {total} file(s) staged. Review them under .wsx/quarantine/; nothing is "
              "tracked or promoted automatically.")
    return 0


# ---------------------------------------------------------------------- point ---
def _point_one(root: Path, tid: str) -> str:
    b = BRIDGES.get(tid, {})
    ptr = b.get("pointer")
    if not ptr:
        return "guidance"
    pf = Path(ptr.replace("~", str(HOME))).expanduser()
    # Only write if the tool's config dir exists (i.e., it's actually installed here) —
    # never create a config tree for a tool the person doesn't use.
    if not pf.parent.exists():
        return "absent"
    block = _pointer_block(root)
    import re
    text = pf.read_text(encoding="utf-8") if pf.exists() else ""
    pat = re.compile(re.escape(_POINTER_START) + r".*?" + re.escape(_POINTER_END), re.DOTALL)
    if pat.search(text):
        text = pat.sub(lambda _m: block.rstrip("\n"), text)
    else:
        text = (text.rstrip() + "\n\n" + block) if text.strip() else block
    pf.write_text(text, encoding="utf-8")
    return "written"


def point(root: Path, tool: str = "") -> int:
    installed = _installed_ids()
    targets = [tool] if tool else [t for t in BRIDGES if t in installed]
    if tool and tool not in BRIDGES:
        raise SystemExit(f"error: unknown tool '{tool}'. Known: {', '.join(sorted(BRIDGES))}")
    print("wsx bridge point — re-anchor your other AI tools to this workspace\n")
    wrote = 0
    for tid in targets:
        b = BRIDGES[tid]
        res = _point_one(root, tid)
        if res == "written":
            wrote += 1
            print(f"  ✓ {_name(tid):22} wrote workspace pointer → {b['pointer']} (idempotent)")
        elif res == "absent":
            print(f"  · {_name(tid):22} config dir not found — skipped (install it first).")
        else:
            g = b.get("guidance", "open the workspace folder in this tool.")
            print(f"  · {_name(tid):22} no safe global config to write — {g}")
    if wrote:
        print(f"\n  {wrote} tool(s) now re-anchor to {root} on every session.")
    return 0


# ----------------------------------------------------------------------- list ---
def list_bridges(root: Path) -> int:
    installed = _installed_ids()
    qdir = quarantine_dir(root)
    print("wsx bridge — your AI tools and how they connect to this workspace\n")
    print(f"  {'TOOL':24} {'INSTALLED':10} {'MEMORY':8} {'POINTER':8}")
    for tid, b in BRIDGES.items():
        here = "yes" if tid in installed else "—"
        has_mem = any(Path(m.replace('~', str(HOME))).expanduser().exists()
                      for m in b.get("memory", []))
        mem = "found" if has_mem else "—"
        ptr = "auto" if b.get("pointer") else "manual"
        print(f"  {_name(tid):24} {here:10} {mem:8} {ptr:8}")
    print("\n  extract → copy a tool's memory into read-only quarantine (.wsx/quarantine/).")
    print("  point   → write a workspace pointer into a tool's own config so it re-anchors here.")
    if qdir.is_dir():
        staged = [p.name for p in qdir.iterdir() if p.is_dir()]
        if staged:
            print(f"\n  quarantined so far: {', '.join(staged)} (review under .wsx/quarantine/).")
    return 0


def run(root: Path, sub: str, tool: str = "") -> int:
    if sub == "list":
        return list_bridges(root)
    if sub == "extract":
        return extract(root, tool)
    if sub == "point":
        return point(root, tool)
    raise SystemExit("error: bridge expects list|extract|point")
