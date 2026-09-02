"""wsx — the command surface. Deterministic 'hands' driven by the brain.

  wsx init <dir>                 scaffold neutral workspace + Obsidian vault + git init
  wsx profile get [key]          read profile.yaml (whole, or a dotted key)
  wsx profile set k=v [k=v ...]  validate + write profile.yaml fields
  wsx resolve                    fetch + pin pulled skills (stub)
  wsx emit <target>              compile canonical -> adapter
                                 (claude-code | agents-md | cursor | mcp | pack | all)
  wsx lint                       validate skills + manifest, report trigger overlaps
  wsx health                     vault graph hygiene: orphans, stale claims, dangling edges
  wsx verify                     dry-run load per target
  wsx project new|list|adopt     per-project docs (adopt = reference an EXISTING repo/folder in place)
  wsx bridge list|extract|point  connect other AI tools: read their memory (→ quarantine) · point them here
  wsx ingest [discover|<path>]   consent-gated ingestion of outside notes/projects (secret-scanned; --apply to promote)
  wsx archive <path> [--reason]  retire a note with provenance (never delete)
  wsx examine [--json]           read-only: what an existing workspace still needs (augment additively)
  wsx adapter [<path>]           map a HAND-BUILT vault to wsx concepts (reference mode — no scaffolding/clobbering)
  wsx diagnose [--fix]           report problems in an EXISTING workspace; --fix applies the safe corrections
  wsx help                       the command cheat sheet (also written to COMMANDS.md)
  wsx wire                       self-wire: connect any unexpected dir/orphan/un-indexed skill (generator-independent)
  wsx upgrade [--dry-run]        corrective pass: add missing scaffold + reconnect graph
  wsx restructure [--apply]      migrate a legacy FLAT workspace up to the numbered taxonomy (dry-run default; --rollback to undo)
  wsx scan [--find-workspaces]   detect your stack (+ locate existing workspaces to update)
  wsx remote <url> --scope …     map a remote → scope → identity (work/personal, non-overlapping)
  wsx identity --scope …         apply the mapped repo-local identity for a scope
  wsx ssh-setup                  scaffold SSH host-aliases for work/personal keys (append-only)
  wsx push                       finalize a fresh workspace: first commit + push (personal-solo only)
  wsx collab <account>           grant a work account access to your PRIVATE workspace repo
  wsx session start|end|reconcile
  wsx sync                       git pull --rebase + push
"""
from __future__ import annotations

import argparse
import sys

from . import (adapter, adapters, archive, bridges, commands, core, diagnose, examine,
               gitscope, health, ingest, lifecycle, projects, resolver, restructure, scaffold,
               scan, search, skills, upgrade, wire)


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
        # Rebuild EVERYTHING derived from the profile. The mirror was only half of it:
        # the emitted adapters (AGENTS.md / CLAUDE.md / cursor rules / pack) also embed
        # profile values (role, tone, audience, separation), and the AI treats those as
        # authoritative — so a stale adapter silently instructs it with the old identity.
        from . import moc
        moc.write_mocs(root)
        print(f"✓ updated {len(a.rest)} field(s) in context/profile.yaml")
        print("  regenerated context/profile.md + HOME.md from the new values.")
        man = core.load_manifest(root)
        targets = [t for t in man.get("emitted", {}) if t in adapters.ADAPTERS]
        if targets:
            for t in targets:
                adapters.ADAPTERS[t](root, prof, man)
            print(f"  re-emitted {len(targets)} adapter target(s) so they can't go stale: "
                  f"{', '.join(sorted(targets))}")
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
    return resolver.resolve(core.require_workspace(),
                            plan_path=a.plan, update=a.update,
                            allow_unvetted=a.allow_unvetted, cache_refs=a.cache_refs)


def cmd_search(a):
    return search.search(core.require_workspace(), a.query, kind=a.kind, source=a.source)


def cmd_scan(a):
    # scan is environment-level — it works with or without a workspace.
    return scan.scan(core.find_workspace_root(), as_json=a.json, write=a.write,
                     find_ws=a.find_workspaces)


def cmd_lint(a):
    return 1 if lifecycle.lint(core.require_workspace()) else 0


def cmd_health(a):
    return 1 if health.health(core.require_workspace()) else 0


def cmd_verify(a):
    return 1 if lifecycle.verify(core.require_workspace()) else 0


def cmd_session(a):
    return lifecycle.session(
        core.require_workspace(), a.action,
        summary=getattr(a, "summary", "") or "", next_=getattr(a, "next", "") or "",
        machine=getattr(a, "machine", "") or "", surface=getattr(a, "surface", "") or "",
        agent=getattr(a, "agent", "") or "", project=getattr(a, "project", "") or "")


def cmd_sync(a):
    return lifecycle.sync(core.require_workspace())


def cmd_compact(a):
    return lifecycle.compact(core.require_workspace())


def cmd_remote(a):
    root = core.require_workspace()
    # `wsx remote <url> --scope …` records the remote→scope→identity map (keeps
    # work/personal non-overlapping) AND wires origin for the personal vault repo.
    if getattr(a, "scope", None):
        if not a.url:
            raise SystemExit("error: --scope needs a URL (wsx remote <url> --scope personal …)")
        rc = gitscope.map_remote(root, a.url, a.scope, a.name or "", a.email or "",
                                 host_alias=a.host_alias or "")
        if rc == 0 and a.scope == "personal":
            lifecycle.remote(root, a.url)  # set origin for the vault's own repo
        return rc
    return lifecycle.remote(root, a.url or "")


def cmd_identity(a):
    root = core.require_workspace()
    if getattr(a, "scope", None):
        prof = core.load_profile(root)
        ok, who = gitscope.apply_repo_identity(root, prof, a.scope)
        print(f"✓ repo-local identity for '{a.scope}' scope → {who}" if ok else f"✗ {who}")
        return 0 if ok else 1
    return lifecycle.identity(root, a.name or "", a.email or "", set_global=a.global_)


def cmd_push(a):
    return gitscope.first_push(core.require_workspace())


def cmd_ssh_setup(a):
    return gitscope.ssh_setup()


def cmd_collab(a):
    return gitscope.add_collaborator(core.require_workspace(), a.account,
                                     repo_url=a.repo or "", permission=a.permission)


def cmd_help(a):
    print(commands.help_text())
    return 0


def cmd_diagnose(a):
    return diagnose.diagnose(core.require_workspace(), fix=a.fix)


def cmd_wire(a):
    return wire.wire(core.require_workspace())


def cmd_doctor(a):
    return lifecycle.doctor()


def cmd_skill(a):
    root = core.require_workspace()
    if a.skill_cmd == "add":
        return skills.add(root, a.name, a.desc, a.triggers, a.hub, a.source, a.title, a.kind,
                          a.level, a.seniority)
    if a.skill_cmd == "list":
        return skills.list_skills(root)
    if a.skill_cmd == "reindex":
        return skills.reindex(root)
    raise SystemExit("error: skill expects add|list|reindex")


def cmd_project(a):
    root = core.require_workspace()
    if a.project_cmd == "new":
        return projects.new(root, a.name, a.title)
    if a.project_cmd == "list":
        return projects.list_projects(root)
    if a.project_cmd == "adopt":
        return projects.adopt(root, a.path, move=a.move, import_docs=a.import_docs,
                              title=a.title or "")
    raise SystemExit("error: project expects new|list|adopt")


def cmd_bridge(a):
    return bridges.run(core.require_workspace(), a.bridge_cmd, tool=getattr(a, "tool", "") or "")


def cmd_ingest(a):
    return ingest.run(core.require_workspace(), path=getattr(a, "path", "") or "",
                      apply=getattr(a, "apply", False))


def cmd_archive(a):
    return archive.archive(core.require_workspace(), a.path, a.reason)


def cmd_adapter(a):
    from pathlib import Path as _P
    root = _P(a.path or ".").resolve()
    return adapter.create(root) if getattr(a, "refresh", False) else adapter.run(root)


def cmd_examine(a):
    # examine works on a non-wsx path too (foreign-workspace mode), so it does NOT
    # require_workspace — it resolves and dispatches itself.
    return examine.run(a.path or ".", as_json=a.json)


def cmd_upgrade(a):
    return upgrade.upgrade(core.require_workspace(), dry_run=a.dry_run,
                           force=getattr(a, "force", False))


def cmd_restructure(a):
    return restructure.restructure(core.require_workspace(),
                                   apply=a.apply, rollback=a.rollback)


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
    print('        wsx init ~/Documents/Projects/Workspace --name "Your Name"')
    print("\nRun  wsx doctor  to check your setup  ·  wsx help  for the command cheat sheet")
    print("(in a workspace, the full reference is COMMANDS.md).")
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

    pdg = sub.add_parser("diagnose",
                         help="report problems in an EXISTING workspace (+ --fix the safe ones)")
    pdg.add_argument("--fix", action="store_true",
                     help="apply the safe, non-destructive corrections (upgrade + emit + reindex)")
    pdg.set_defaults(fn=cmd_diagnose)

    for name, fn, helptext in [
        ("help", cmd_help, "the command cheat sheet (also written to COMMANDS.md)"),
        ("doctor", cmd_doctor, "check your environment + what to do next"),
        ("wire", cmd_wire, "connect anything loose (unexpected dirs, orphan notes, un-indexed skills)"),
        ("lint", cmd_lint, "validate skills + manifest"),
        ("health", cmd_health, "vault graph hygiene: orphans, stale claims, dangling edges"),
        ("verify", cmd_verify, "dry-run load per target"),
        ("sync", cmd_sync, "safe multi-device git sync (rebase + retry)"),
        ("compact", cmd_compact, "fold session fragments into the session log (idempotent)"),
    ]:
        sp = sub.add_parser(name, help=helptext)
        sp.set_defaults(fn=fn)

    pr = sub.add_parser("resolve", help="execute an approved skill plan (fetch + pin + register)")
    pr.add_argument("--plan", default=None, help="path to the plan JSON (default: context/skill-plan.json)")
    pr.add_argument("--update", action="store_true", help="bump the pin when an upstream skill changed")
    pr.add_argument("--allow-unvetted", action="store_true",
                    help="permit pulls from unvetted registries (skills.sh/community) not marked audited")
    pr.add_argument("--cache-refs", action="store_true",
                    help="for composite skills, fetch + pin + cache each reference URL for offline provenance")
    pr.set_defaults(fn=cmd_resolve)

    psc = sub.add_parser("scan", help="detect your installed agents, MCP servers, and local LLMs")
    psc.add_argument("--json", action="store_true", help="machine-readable output")
    psc.add_argument("--write", action="store_true", help="save to context/scan.json (inside a workspace)")
    psc.add_argument("--find-workspaces", action="store_true",
                     help="also search common locations for existing workspaces to update/upgrade")
    psc.set_defaults(fn=cmd_scan)

    prm = sub.add_parser("remote", help="set/show the vault remote, or map a remote → scope → identity")
    prm.add_argument("url", nargs="?", default="", help="git remote URL (omit to see recommendations)")
    # Passing --scope turns this into a MAPPING (remote→scope→identity), which keeps
    # work/personal auth non-overlapping. Without it, behaves as before (show/set origin).
    prm.add_argument("--scope", choices=["personal", "work"], default=None,
                     help="map this URL to a scope + identity (keeps work/personal separate)")
    prm.add_argument("--name", default="", help="repo-local author name (with --scope)")
    prm.add_argument("--email", default="", help="repo-local author email — a GitHub noreply address avoids publishing a personal one (with --scope)")
    prm.add_argument("--host-alias", dest="host_alias", default="",
                     help="SSH host alias (defaults: personal=github.com, work=github-work)")
    prm.set_defaults(fn=cmd_remote)

    pid = sub.add_parser("identity", help="set/show the git author identity for commits")
    pid.add_argument("--name", default="", help='author name, e.g. "Ada Lovelace"')
    pid.add_argument("--email", default="", help='author email, e.g. "ada@example.com"')
    pid.add_argument("--scope", choices=["personal", "work"],
                     help="apply the mapped identity for this scope to THIS repo (repo-local)")
    pid.add_argument("--global", dest="global_", action="store_true",
                     help="set as the default for ALL repos (default: this workspace only)")
    pid.set_defaults(fn=cmd_identity)

    ppush = sub.add_parser("push", help="finalize a fresh workspace: first commit + push (personal-solo only)")
    ppush.set_defaults(fn=cmd_push)

    pssh = sub.add_parser("ssh-setup", help="scaffold SSH host-aliases for work/personal GitHub keys (append-only)")
    pssh.set_defaults(fn=cmd_ssh_setup)

    pcol = sub.add_parser("collab", help="grant a work account access to your PRIVATE workspace repo (you-authorized)")
    pcol.add_argument("account", help="the GitHub username to grant access to")
    pcol.add_argument("--repo", default="", help="repo URL (defaults to the workspace's own remote)")
    pcol.add_argument("--permission", default="push", choices=["pull", "push", "admin"],
                      help="access level (default: push)")
    pcol.set_defaults(fn=cmd_collab)

    pse = sub.add_parser("search", help="find sources (skill registries + reference anchors)")
    pse.add_argument("query", nargs="?", default="", help="capability to search for")
    pse.add_argument("--kind", default="all", choices=["all", "skill", "reference"],
                     help="limit to skill registries or reference anchors")
    pse.add_argument("--source", default=None, help="limit to one source id from the catalog")
    pse.set_defaults(fn=cmd_search)

    ps = sub.add_parser("session", help="lifecycle file ops (start · end · reconcile)")
    ps.add_argument("action", choices=["start", "end", "reconcile"])
    # `end` writes an attributed session fragment; the session-end skill passes these.
    ps.add_argument("--summary", default="", help="one-line session summary (end)")
    ps.add_argument("--next", default="", help="the next action to resume from (end)")
    ps.add_argument("--machine", default="", help="machine label (end; default: hostname)")
    ps.add_argument("--surface", default="", help="AI surface, e.g. claude-code/cursor (end)")
    ps.add_argument("--agent", default="", help="agent/model identity (end)")
    ps.add_argument("--project", default="", help="project(s) this session touched (end)")
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
    ska.add_argument("--level", default="intermediate",
                     choices=["hobbyist", "intermediate", "advanced", "expert"],
                     help="the person's expertise IN THIS DOMAIN — sets the skill's altitude "
                          "(hobbyist teaches fundamentals; expert assumes fluency + captures judgment)")
    ska.add_argument("--seniority", default="",
                     help="e.g. 'staff', 'principal' — adds a leadership/setting-the-bar frame for experts")
    ska.add_argument("--source", default="generated", choices=["generated", "pulled", "pulled+patched"])
    ska.add_argument("--title", default="", help="display title for the body heading")
    sksub.add_parser("list", help="list registered skills, grouped by hub")
    sksub.add_parser("reindex", help="rebuild manifest skill index from disk")
    psk.set_defaults(fn=cmd_skill)

    ppr = sub.add_parser("project", help="per-project documentation folders (docs, not code)")
    prsub = ppr.add_subparsers(dest="project_cmd", required=True)
    pra = prsub.add_parser("new", help="scaffold projects/<name>/ (PROJECT.md + notes/)")
    pra.add_argument("name", help='project name, e.g. "My Side Project"')
    pra.add_argument("--title", default="", help="display title (defaults to name)")
    prsub.add_parser("list", help="list project documentation folders")
    pad = prsub.add_parser("adopt",
                           help="adopt an EXISTING project (repo or folder) — reference-in-place")
    pad.add_argument("path", help="path to the existing project directory")
    pad.add_argument("--title", default="", help="display title (defaults to the folder name)")
    pad.add_argument("--move", action="store_true",
                     help="physically move the project to sit beside the vault (code stays out of the vault)")
    pad.add_argument("--import-docs", dest="import_docs", action="store_true",
                     help="copy a PLAIN folder's loose docs into notes/ (ignored for git repos; skips secrets)")
    ppr.set_defaults(fn=cmd_project)

    pbr = sub.add_parser("bridge",
                         help="connect other AI tools: list · extract their memory · point them here")
    brsub = pbr.add_subparsers(dest="bridge_cmd", required=True)
    brsub.add_parser("list", help="show your AI tools + memory/pointer status")
    bre = brsub.add_parser("extract", help="copy a tool's memory into read-only quarantine")
    bre.add_argument("tool", nargs="?", default="", help="one tool id (default: all installed)")
    brp = brsub.add_parser("point", help="write a workspace pointer into a tool's own config")
    brp.add_argument("tool", nargs="?", default="", help="one tool id (default: all installed)")
    pbr.set_defaults(fn=cmd_bridge)

    pin = sub.add_parser("ingest",
                         help="consent-gated ingestion: pull outside notes/projects in, secret-scanned")
    pin.add_argument("path", nargs="?", default="",
                     help="a folder to stage (omit or 'discover' to list where content could come from)")
    pin.add_argument("--apply", action="store_true",
                     help="promote the SAFE, classified docs (secret-bearing files are never promoted)")
    pin.set_defaults(fn=cmd_ingest)

    par = sub.add_parser("archive", help="retire a note with provenance (never delete)")
    par.add_argument("path", help="path to the note, relative to the workspace")
    par.add_argument("--reason", default="", help="why it is being retired")
    par.set_defaults(fn=cmd_archive)

    pad2 = sub.add_parser("adapter",
                          help="map a HAND-BUILT vault to wsx concepts (reference mode; no scaffolding)")
    pad2.add_argument("path", nargs="?", default="", help="path to the vault (default: current dir)")
    pad2.add_argument("--refresh", action="store_true", help="re-detect + rewrite the concept map")
    pad2.set_defaults(fn=cmd_adapter)

    pex = sub.add_parser("examine", help="read-only: what an existing workspace needs (interview coverage + gaps)")
    pex.add_argument("path", nargs="?", default=".", help="workspace path (default: current dir; works on foreign layouts too)")
    pex.add_argument("--json", action="store_true", help="machine-readable output for the brain")
    pex.set_defaults(fn=cmd_examine)

    pu = sub.add_parser("upgrade", help="corrective pass: add missing scaffold + reconnect the graph")
    pu.add_argument("--dry-run", action="store_true", help="preview the plan without writing")
    pu.add_argument("--force", action="store_true",
                    help="override the foreign-vault guard (add scaffold to a hand-built vault — not advised)")
    pu.set_defaults(fn=cmd_upgrade)

    prs = sub.add_parser("restructure",
                         help="migrate a legacy FLAT workspace up to the numbered taxonomy")
    prs.add_argument("--apply", action="store_true",
                     help="actually perform the migration (default is a dry-run preview)")
    prs.add_argument("--rollback", action="store_true",
                     help="undo the most recent restructure, restoring the flat layout from backup")
    prs.set_defaults(fn=cmd_restructure)

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
