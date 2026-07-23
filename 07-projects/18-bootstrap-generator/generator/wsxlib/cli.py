"""wsx — the command surface. Deterministic 'hands' driven by the brain.

  wsx init <dir>                 scaffold neutral workspace + Obsidian vault + git init
  wsx profile get [key]          read profile.yaml (whole, or a dotted key)
  wsx profile set k=v [k=v ...]  validate + write profile.yaml fields
  wsx resolve                    fetch + pin pulled skills (stub)
  wsx emit <target>              compile canonical -> adapter
                                 (claude-code | agents-md | cursor | mcp | pack | all)
  wsx lint                       validate skills + manifest, report trigger overlaps
  wsx verify                     dry-run load per target
  wsx session start|end|reconcile
  wsx sync                       git pull --rebase + push
"""
from __future__ import annotations

import argparse
import sys

from . import adapters, core, lifecycle, scaffold, skills


# profile fields that are lists — `set` splits these on commas (and accepts [a, b] form).
# Everything else stays a scalar, so a string value may safely contain commas
# (e.g. contexts.work.role="Senior designer, fintech").
LIST_FIELDS = {
    "surfaces.agents",
    "surfaces.machines",
    "contexts.professional.crafts",
    "contexts.personal.interests",
    "preferences.banned",
    "imports",
}


def _coerce(v: str):
    low = v.lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("~", "null", ""):
        return None
    if v.startswith("[") and v.endswith("]"):
        return _coerce_list(v)
    if v.lstrip("-").isdigit():
        return int(v)
    return v


def _coerce_list(v: str):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        v = v[1:-1]
    return [p.strip() for p in v.split(",") if p.strip()]


def _coerce_for(key: str, raw: str):
    return _coerce_list(raw) if key in LIST_FIELDS else _coerce(raw)


def _set_dotted(d: dict, dotted: str, value):
    parts = dotted.split(".")
    cur = d
    for p in parts[:-1]:
        cur = cur.setdefault(p, {})
        if not isinstance(cur, dict):
            raise SystemExit(f"error: cannot set '{dotted}' — '{p}' is not a mapping")
    cur[parts[-1]] = value


def _get_dotted(d: dict, dotted: str):
    cur = d
    for p in dotted.split("."):
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return cur


def cmd_init(a):
    scaffold.init(a.dir, name=a.name, handle=a.handle, do_git=not a.no_git, force=a.force)
    return 0


def cmd_profile(a):
    root = core.require_workspace()
    prof = core.load_profile(root)
    from . import yamlio
    if a.action == "get":
        key = a.rest[0] if a.rest else None
        if key:
            val = _get_dotted(prof, key)
            if isinstance(val, (dict, list)):
                import json
                print(json.dumps(val, indent=2))
            else:
                print("" if val is None else val)
        else:
            print(yamlio.dumps(prof))
        return 0
    if a.action == "set":
        if not a.rest:
            raise SystemExit("error: profile set needs at least one key=value")
        for pair in a.rest:
            if "=" not in pair:
                raise SystemExit(f"error: '{pair}' is not key=value")
            key, _, raw = pair.partition("=")
            key = key.strip()
            _set_dotted(prof, key, _coerce_for(key, raw.strip()))
        core.save_profile(root, prof)
        print(f"✓ updated {len(a.rest)} field(s) in context/profile.yaml")
        return 0
    raise SystemExit("error: profile expects get|set")


def cmd_emit(a):
    root = core.require_workspace()
    prof = core.load_profile(root)
    man = core.load_manifest(root)
    written = adapters.emit(root, a.target, prof, man)
    print(f"✓ emit {a.target}: {len(written)} file(s)")
    for w in written:
        try:
            print(f"  {w.relative_to(root)}")
        except ValueError:
            print(f"  {w}")
    return 0


def cmd_resolve(a):
    return lifecycle.resolve(core.require_workspace())


def cmd_lint(a):
    return 1 if lifecycle.lint(core.require_workspace()) else 0


def cmd_verify(a):
    return 1 if lifecycle.verify(core.require_workspace()) else 0


def cmd_session(a):
    return lifecycle.session(core.require_workspace(), a.action)


def cmd_sync(a):
    return lifecycle.sync(core.require_workspace())


def cmd_doctor(a):
    return lifecycle.doctor()


def cmd_skill(a):
    root = core.require_workspace()
    if a.skill_cmd == "add":
        return skills.add(root, a.name, a.desc, a.triggers, a.hub, a.source, a.title, a.kind)
    if a.skill_cmd == "list":
        return skills.list_skills(root)
    if a.skill_cmd == "reindex":
        return skills.reindex(root)
    raise SystemExit("error: skill expects add|list|reindex")


def _welcome() -> int:
    import os
    root = core.find_workspace_root()
    print("wsx — the Bootstrap Generator CLI (the 'hands').\n")
    if root:
        print(f"✓ You're in a workspace: {root}")
        print("  Common next steps:  wsx verify   ·   wsx emit claude-code\n")
    else:
        print(f"You're in: {os.getcwd()}")
        print("ℹ️  This folder is NOT a workspace yet — it's likely the generator itself.")
        print("    (The generator BUILDS a separate workspace folder for you.)\n")
    print("Most people never run wsx by hand — your AI assistant drives it. To start, pick one:")
    print("  • Easiest — open this folder in your AI (Claude Code, Cursor, …) and say:")
    print('        "set up my workspace"')
    print("  • By hand — create your workspace folder:")
    print('        wsx init ~/Documents/my-workspace --name "Your Name"')
    print("\nRun  wsx doctor  to check your setup, or  wsx -h  for all commands.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="wsx", description="Bootstrap Generator — workspace CLI (the hands).")
    p.add_argument("--version", action="version", version=f"wsx {_version()}")
    sub = p.add_subparsers(dest="cmd")  # no subcommand → friendly welcome (see main)

    pi = sub.add_parser("init", help="scaffold a neutral workspace")
    pi.add_argument("dir", help="destination directory")
    pi.add_argument("--name", default="you", help="your name")
    pi.add_argument("--handle", default="you", help="short handle")
    pi.add_argument("--no-git", action="store_true", help="skip git init")
    pi.add_argument("--force", action="store_true", help="scaffold into a non-empty dir")
    pi.set_defaults(fn=cmd_init)

    pp = sub.add_parser("profile", help="read/write profile.yaml")
    pp.add_argument("action", choices=["get", "set"])
    pp.add_argument("rest", nargs="*", help="dotted key (get) or key=value pairs (set)")
    pp.set_defaults(fn=cmd_profile)

    pe = sub.add_parser("emit", help="compile canonical workspace to a surface adapter")
    pe.add_argument("target", help="claude-code | agents-md | cursor | mcp | pack | all")
    pe.set_defaults(fn=cmd_emit)

    for name, fn, helptext in [
        ("doctor", cmd_doctor, "check your environment + what to do next"),
        ("resolve", cmd_resolve, "fetch + pin pulled skills (stub)"),
        ("lint", cmd_lint, "validate skills + manifest"),
        ("verify", cmd_verify, "dry-run load per target"),
        ("sync", cmd_sync, "git pull --rebase + push"),
    ]:
        sp = sub.add_parser(name, help=helptext)
        sp.set_defaults(fn=fn)

    ps = sub.add_parser("session", help="lifecycle file ops")
    ps.add_argument("action", choices=["start", "end", "reconcile"])
    ps.set_defaults(fn=cmd_session)

    psk = sub.add_parser("skill", help="create / list / reindex skills")
    sksub = psk.add_subparsers(dest="skill_cmd", required=True)
    ska = sksub.add_parser("add", help="create a generated skill + register it")
    ska.add_argument("name", help="skill folder name, e.g. lead-ux-researcher")
    ska.add_argument("--desc", required=True, help="one-line description (when it loads)")
    ska.add_argument("--triggers", default="", help="comma-separated trigger words")
    ska.add_argument("--hub", default="", help="hub this belongs to (defaults to its own name)")
    ska.add_argument("--kind", default="spoke", choices=["hub", "spoke"],
                     help="hub (an orchestrator with spokes) or spoke (a focused skill); shapes the skeleton")
    ska.add_argument("--source", default="generated", choices=["generated", "pulled", "pulled+patched"])
    ska.add_argument("--title", default="", help="display title for the body heading")
    sksub.add_parser("list", help="list registered skills, grouped by hub")
    sksub.add_parser("reindex", help="rebuild manifest skill index from disk")
    psk.set_defaults(fn=cmd_skill)

    return p


def _version() -> str:
    from . import __version__
    return __version__


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    args = build_parser().parse_args(argv)
    if not getattr(args, "cmd", None):
        return _welcome()
    return args.fn(args)
