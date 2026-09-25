#!/usr/bin/env python3
"""closure.py — surface- and device-aware session closure per touched repo (H23), with H25's
limits on fragments from employer-touched sessions.

Every surface closes a session the same way: read the session's touch ledger
(~/.config/snds-workspace/telemetry/sessions/<sid>.touched, written by `ws-hook --event post-tool`),
classify each touched repo through profile_resolve, and print what closes it:

  workspace                 fold, rebuild, verify, commit, push under the resolved identity
  personal (positively)     commit and push per its profile, under the device's resolved identity
  not personal, Claude      a handoff note and vetted housekeeping only; never git
  not personal, other host  a feature branch and a PR; never the default branch

With no ledger, the fallback is `git status --porcelain` over the checkout cache (profile_resolve's
checkouts.json) and the workspace; for a Claude session only the workspace and positively personal
repos are read.

The sweeper runs at session start on any verified surface (`ws-hook sweep`). For every DEAD session
(a ledger with no activity for IDLE_S: ledger, ws-hook claims, baseline) it commits only the
MECHANICAL workspace leftovers (its 06-context/sessions fragment and the fold/rebuild outputs) that no
live session claims, in the workspace only, under the resolved identity; it never pushes (pushing is
closure's job, run by an agent or a human who can see a rejection). Substantive leftovers become one
card notice each (session-status reads telemetry/closure-notices.json).

H25: a fragment written by a session whose ledger touched a repo that is not positively personal keeps
no line naming that repo's substance; it gets one `Employer repos (H25 limits):` section holding
{slug, status, PR URL if allowed} per repo. In a public workspace the slug is an opaque stable id and
PR URLs are dropped. compact-sessions.py applies this at fold time; the sweeper before it commits.

  closure.py plan --session SID|latest [--json] [--family F]
  closure.py fragment --session SID PATH        apply the H25 limits to one fragment in place
  closure.py sweep [--json] [--dry-run]         the session-start sweeper, by hand
  closure.py --self-test

Stdlib only; Python 3.9+. Imports the sibling profile_resolve and ws_hook.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
IDLE_S = 4 * 3600
LEDGER_MAX_AGE_S = 14 * 86400
GIT_TIMEOUT_S = 10.0
NOTICES_NAME = "closure-notices.json"
FRAGMENT_RE = re.compile(r"^06-context/sessions/(?!README\.md$)[^/]+\.md$")
GENERATED = ("06-context/session-log.md", "06-context/session-log-archive.md",
             "03-skills/skills.registry.json", "02-shared-references/trigger-routes.md",
             "02-shared-references/trigger-routes-digest.md")
H25_HEADER = "Employer repos (H25 limits):"
WORKSPACE_STEPS = ("fold", "rebuild", "verify", "commit", "push")
# Families whose sessions get the handoff (never git) on a repo that is not positively personal, and
# whose closure reads only the workspace and positively personal repos (session-status's restrictive set).
RESTRICTIVE = ("claude", "unknown-agent")


# --------------------------------------------------------------------------- siblings

def _sibling(name: str):
    if str(TOOLS) not in sys.path:
        sys.path.insert(0, str(TOOLS))
    return __import__(name)


def _pr():
    return _sibling("profile_resolve")


def _wh():
    return _sibling("ws_hook")


def _run(argv: List[str], cwd: Path, *, timeout: float = GIT_TIMEOUT_S, env=None):
    """The one subprocess seam (tests spy on it). None when it cannot run."""
    try:
        return subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True, timeout=timeout, env=env)
    except (OSError, subprocess.SubprocessError, ValueError):
        return None


def _git(cwd: Path, *args: str, timeout: float = GIT_TIMEOUT_S):
    return _run(["git", *args], cwd, timeout=timeout)


def _real(p) -> str:
    return os.path.realpath(str(p))


# --------------------------------------------------------------------------- ledger + families

def telemetry(home=None) -> Path:
    return _pr().ws_paths(home=home)["telemetry"]


def ledger(sid: str, *, home=None) -> List[dict]:
    return _wh().read_ledger(sid, home=home)


def _families(root=None) -> dict:
    try:
        return _pr().load_table("surfaces", root=root).get("families") or {}
    except Exception:  # noqa: BLE001
        return {}


def host_family(host: str, *, root=None) -> str:
    try:
        t = _pr().load_table("surfaces", root=root)
    except Exception:  # noqa: BLE001
        return "unknown-agent"
    for s in t.get("surfaces") or []:
        if s.get("id") == host:
            return str(s.get("family") or "unknown-agent")
    return "unknown-agent"


def tightest(fams: List[str], *, root=None) -> str:
    """The most restrictive family (wall_rank); unknown-agent when nothing is known."""
    table = _families(root)
    known = [f if f in table or not table else "unknown-agent" for f in fams if f]
    if not known:
        return "unknown-agent"
    # An undeclared family ranks as unknown-agent (tighten-only).
    fallback = (table.get("unknown-agent") or {}).get("wall_rank", 90)
    return max(known, key=lambda f: (table.get(f) or {}).get("wall_rank", fallback))


def detection(family: str) -> dict:
    """A detection object for a session's walls (never looser than the family)."""
    return {"family": family, "family_for_walls": family, "acting_host": family, "agent_possible": family != "human",
            "via": "closure", "verified": True, "determined": True, "conflict": False, "chain": []}


def session_family(records: List[dict], family: str = "auto", *, root=None) -> str:
    fams = [host_family(r.get("host") or "", root=root) for r in records]
    if family != "auto":
        fams.append(family)
    return tightest(sorted(set(fams)), root=root) if fams else "unknown-agent"


def group_repos(records: List[dict]) -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for r in records:
        key = _real(r["repo"])
        g = out.setdefault(key, {"repo": key, "paths": [], "shell": False, "hosts": []})
        if r.get("path"):
            if r["path"] not in g["paths"]:
                g["paths"].append(r["path"])
        else:
            g["shell"] = True
        if r.get("host") and r["host"] not in g["hosts"]:
            g["hosts"].append(r["host"])
    return out


# --------------------------------------------------------------------------- classification

def workspace_root(*, home=None, root=None) -> Optional[Path]:
    pr = _pr()
    cands = []
    if root is not None:
        cands.append(Path(root))
    try:
        line = pr.ws_paths(home=home)["root_file"].read_text(encoding="utf-8").splitlines()[0].strip()
        if line:
            cands.append(Path(line).expanduser())
    except (OSError, IndexError):
        pass
    cands.append(ROOT)
    for c in cands:
        if (c / "AGENTS.md").is_file() and (c / ".git").exists():
            return Path(_real(c))
    return None


def classify(repo: str, family: str, *, home=None, root=None, cache=None) -> dict:
    """{class: workspace|personal|employer|unknown, ...repo_resolve facts}. Walls are the session's
    family, so a Claude session's repos under projects_root come from the cache only."""
    pr = _pr()
    if pr.is_workspace_checkout(repo, root=root, home=home):
        res = {"owner_class": "personal", "positively_personal": True, "profile": "personal-solo",
               "remotes": [], "in_projects_root": False, "reasons": ["workspace checkout"]}
        cls = "workspace"
    else:
        res = pr.repo_resolve(repo, root=root, home=home, detection=detection(family), cache=cache)
        if res.get("positively_personal"):
            cls = "personal"
        elif res.get("owner_class") == "employer":
            cls = "employer"
        else:
            cls = "unknown"
    slug = next((r.get("slug") for r in res.get("remotes") or [] if r.get("slug")), None)
    return {"class": cls, "slug": slug, "profile": res.get("profile"), "owner_class": res.get("owner_class"),
            "in_projects_root": bool(res.get("in_projects_root")), "reasons": list(res.get("reasons") or [])}


def _identity(repo: str, family: str, *, home=None, root=None, cache=None, hostname=None) -> dict:
    try:
        return _pr().identity(repo=repo, family=family, root=root, home=home, detection=detection(family),
                              cache=cache, hostname=hostname)
    except Exception as exc:  # noqa: BLE001
        return {"expected": None, "invariants_hit": [], "flag": None, "notice": f"identity unavailable ({exc})",
                "device": "unknown"}


def restricted(family: str) -> bool:
    return family in RESTRICTIVE


def _may_read(cls: str, family: str) -> bool:
    """A Claude session reads (git status, HEAD files) only the workspace and positively personal repos."""
    return cls in ("workspace", "personal") or not restricted(family)


def _dirty(repo: Path) -> Optional[List[str]]:
    r = _git(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    if r is None or r.returncode != 0:
        return None
    return [e["path"] for e in _wh().parse_porcelain_z(r.stdout)]


# --------------------------------------------------------------------------- the plan

def _workspace_entry(e: dict, sid: str, ident: dict, h25: bool) -> dict:
    repo = e["repo"]
    branch = _branch(Path(repo))
    steps = list(WORKSPACE_STEPS)
    cmds = ["python3 09-tools/compact-sessions.py"]
    if h25:
        steps.insert(0, "limit-fragment")
        cmds.insert(0, f"python3 09-tools/closure.py fragment --session {sid} 06-context/sessions/<fragment>.md")
    cmds += [f"python3 09-tools/nightly.py --phases rebuild --scope session:{sid}",
             "python3 09-tools/workspace-harness.py",
             f"git -C {repo} add -A -- <session paths>",
             f"git -C {repo} commit -m \"session: <date> [<machine> / <surface>] — <summary>\""]
    notes = []
    if branch and branch.startswith("intent/"):
        steps.remove("push")
        notes.append(f"{branch}: committed by its task; no push from closure")
    else:
        cmds.append(f"git -C {repo} push")
    return {"action": "workspace", "steps": steps, "commands": cmds, "notes": notes, "branch": branch,
            "identity": ident.get("expected"), "identity_flag": ident.get("flag")}


def _branch(repo: Path) -> Optional[str]:
    try:
        return _pr()._repo_heads(repo)[0]
    except Exception:  # noqa: BLE001
        return None


def _handoff_entry(e: dict, *, home=None) -> dict:
    try:
        vet = _pr().vetted_status("prune-our-branches", home=home).get("status")
    except Exception:  # noqa: BLE001
        vet = "unknown"
    cmds = ["python3 09-tools/prune-our-branches.py --apply"] if vet == "vetted" else []
    notes = ["write a handoff note (slug and status only) for Cursor or Codex; this session runs no git here"]
    if vet != "vetted":
        notes.append(f"vetted housekeeping unavailable (prune-our-branches: {vet})")
    return {"action": "handoff", "steps": ["handoff-note"] + (["vetted-housekeeping"] if cmds else []),
            "commands": cmds, "notes": notes, "branch": None, "identity": None, "identity_flag": None}


def _branch_pr_entry(e: dict, ident: dict) -> dict:
    repo = e["repo"]
    try:
        cur, dflt = _pr()._repo_heads(Path(repo))
    except Exception:  # noqa: BLE001
        cur, dflt = None, None
    defaults = {d for d in (dflt, "main", "master") if d}
    on_default = cur is None or cur in defaults
    steps = (["feature-branch"] if on_default else []) + ["commit", "push-branch", "pr"]
    cmds = ([f"git -C {repo} switch -c <topic-branch>"] if on_default else []) + [
        f"git -C {repo} add -- <session paths>",
        f"git -C {repo} commit -m \"<summary>\"",
        f"git -C {repo} push -u origin HEAD",
        "gh pr create --fill"]
    notes = [f"never commit or push the default branch ({dflt or 'unknown'})", "a human engineer reviews and merges"]
    if ident.get("invariants_hit"):
        notes.append("identity invariant hit: " + ", ".join(ident["invariants_hit"]) + "; fix the identity first")
    return {"action": "branch-pr", "steps": steps, "commands": cmds, "notes": notes, "branch": cur,
            "identity": ident.get("expected"), "identity_flag": ident.get("flag")}


def _personal_entry(e: dict, ident: dict) -> dict:
    repo = e["repo"]
    held = bool(ident.get("invariants_hit")) or not ident.get("expected")
    notes = []
    if ident.get("flag"):
        notes.append(f"identity: {ident['flag']}")
    if held:
        notes.append("commit held: no resolved identity for this device and family" if not ident.get("expected")
                     else "commit held: " + ", ".join(ident["invariants_hit"]))
    return {"action": "commit-push" if not held else "hold",
            "steps": [] if held else ["commit", "push"],
            "commands": [] if held else [f"git -C {repo} add -A -- <session paths>",
                                         f"git -C {repo} commit -m \"<summary>\"", f"git -C {repo} push"],
            "notes": notes, "branch": _branch(Path(repo)), "identity": ident.get("expected"),
            "identity_flag": ident.get("flag")}


def fallback_repos(family: str, *, home=None, root=None, cache=None) -> Dict[str, dict]:
    """No ledger: dirty repos among the workspace and the checkout cache (Claude: workspace and
    positively personal repos only)."""
    pr = _pr()
    cands: List[str] = []
    ws = workspace_root(home=home, root=root)
    if ws is not None:
        cands.append(str(ws))
    c = cache if cache is not None else pr._load_cache(None, home)
    for co in (c or {}).get("checkouts") or []:
        if isinstance(co, dict) and co.get("path") and co.get("kind") != "bare":
            cands.append(_real(co["path"]))
    out: Dict[str, dict] = {}
    for repo in dict.fromkeys(cands):
        cl = classify(repo, family, home=home, root=root, cache=c)
        if not _may_read(cl["class"], family) or not Path(repo).is_dir():
            continue
        dirty = _dirty(Path(repo))
        if dirty:
            out[repo] = {"repo": repo, "paths": dirty, "shell": False, "hosts": []}
    return out


def plan(sid: str, *, family: str = "auto", home=None, root=None, cache=None, hostname=None) -> dict:
    pr = _pr()
    recs = ledger(sid, home=home)
    fam = session_family(recs, family, root=root) if (recs or family != "auto") else _current_family(root)
    c = cache if cache is not None else pr._load_cache(None, home)
    groups = group_repos(recs)
    source = "ledger"
    if not groups:
        groups = fallback_repos(fam, home=home, root=root, cache=c)
        source = "fallback-git-status"
    entries = []
    for key, g in groups.items():
        cl = classify(key, fam, home=home, root=root, cache=c)
        entries.append(dict(g, **cl))
    h25 = any(e["class"] in ("employer", "unknown") for e in entries)
    out = []
    for e in entries:
        ident = {} if (e["class"] not in ("workspace", "personal") and restricted(fam)) else \
            _identity(e["repo"], fam, home=home, root=root, cache=c, hostname=hostname)
        if e["class"] == "workspace":
            act = _workspace_entry(e, sid, ident, h25)
        elif e["class"] == "personal":
            act = _personal_entry(e, ident)
        elif restricted(fam):
            act = _handoff_entry(e, home=home)
        else:
            act = _branch_pr_entry(e, ident)
        dirty = None
        if _may_read(e["class"], fam) and Path(e["repo"]).is_dir():
            d = _dirty(Path(e["repo"]))
            dirty = None if d is None else len(d)
        row = {"repo": e["repo"], "slug": e.get("slug"), "class": e["class"], "profile": e.get("profile"),
               "recorded_paths": len(e["paths"]), "shell": e["shell"], "hosts": e["hosts"], "dirty": dirty}
        row.update(act)
        out.append(row)
    return {"session": sid, "family": fam, "source": source, "device": _device(hostname, root),
            "h25_fragment_limits": h25, "repos": out}


def _current_family(root=None) -> str:
    try:
        det = _pr().detect_surface(root=root)
        return str(det.get("family_for_walls") or "unknown-agent")
    except Exception:  # noqa: BLE001
        return "unknown-agent"


def _device(hostname=None, root=None) -> str:
    try:
        return str(_pr().current_device(hostname=hostname, root=root).get("id") or "unknown")
    except Exception:  # noqa: BLE001
        return "unknown"


def format_plan(p: dict) -> str:
    lines = [f"closure plan · session {p['session']} · family {p['family']} · device {p['device']} · "
             f"source {p['source']}"]
    if not p["repos"]:
        lines.append("  nothing touched: no closure needed")
    for r in p["repos"]:
        label = r["slug"] or r["repo"]
        lines.append(f"- {label} [{r['class']}] -> {r['action']}: {' > '.join(r['steps']) or 'none'}"
                     + (f" · identity {r['identity']}" if r.get("identity") else ""))
        for c in r["commands"]:
            lines.append(f"    $ {c}")
        for n in r["notes"] + ([f"identity flag: {r['identity_flag']}"] if r.get("identity_flag") else []):
            lines.append(f"    note: {n}")
    if p["h25_fragment_limits"]:
        lines.append("H25: this session touched a repo that is not positively personal; its fragment holds only "
                     "{slug, status, PR URL if allowed} for it (closure.py fragment applies the limits)")
    return "\n".join(lines)


# --------------------------------------------------------------------------- H25 fragment limits

def _context_table(root=None) -> dict:
    try:
        return _pr().load_table("context-remotes", root=root)
    except Exception:  # noqa: BLE001
        return {}


def workspace_public(root=None) -> bool:
    """True unless the table declares the workspace repo private (unknown = public, tighten-only)."""
    for r in _context_table(root).get("repos") or []:
        if isinstance(r, dict) and r.get("role") == "workspace":
            return r.get("visibility") != "private"
    return True


def employer_tokens(limited: List[dict], *, root=None) -> List[str]:
    t = _context_table(root)
    toks = [str(o.get("owner")) for o in t.get("owners") or []
            if isinstance(o, dict) and o.get("class") == "employer" and o.get("owner")]
    sub = t.get("employer_substance") or {}
    for k in ("url_prefixes", "domains", "count_keywords"):
        toks += [str(x) for x in sub.get(k) or [] if x]
    for e in limited:
        if e.get("slug"):
            toks.append(e["slug"])
            name = e["slug"].split("/", 1)[-1]
            if len(name) >= 3:
                toks.append(name)
        if e.get("repo"):
            toks.append(e["repo"])
            if len(Path(e["repo"]).name) >= 3:
                toks.append(Path(e["repo"]).name)
    return sorted({x.casefold() for x in toks if x}, key=len, reverse=True)


def opaque_id(e: dict) -> str:
    return "emp-" + hashlib.sha1(str(e.get("slug") or e.get("repo") or "").encode("utf-8")).hexdigest()[:8]


def limit_fragment(text: str, limited: List[dict], *, family: str, public: bool, tokens: List[str]) -> str:
    """Drop every line that names a limited repo's substance; add one H25 section of
    {slug, status, PR URL if allowed}. Idempotent."""
    if not limited:
        return text
    keep, in_sec = [], False
    for ln in text.splitlines():
        if ln.strip() == H25_HEADER:
            in_sec = True
            continue
        if in_sec:
            if ln.startswith("  - "):
                continue
            in_sec = False
        low = ln.casefold()
        if any(t in low for t in tokens):
            continue
        keep.append(ln)
    sec = [H25_HEADER]
    for e in limited:
        ident = opaque_id(e) if public else (e.get("slug") or opaque_id(e))
        status = e.get("status") or ("handoff" if restricted(family) else "branch-pr")
        url = e.get("pr_url") if (e.get("pr_url") and not public and not restricted(family)) else None
        sec.append(f"  - {ident} — {status}" + (f" — {url}" if url else ""))
    end = next((i for i, ln in enumerate(keep) if ln.strip() == "--- END BLOCK ---"), None)
    out = keep[:end] + sec + keep[end:] if end is not None else keep + sec
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def limited_repos(records: List[dict], family: str, *, home=None, root=None, cache=None) -> List[dict]:
    """The session's repos that are not positively personal (employer or unknown), classified under
    the Claude walls (cache only under projects_root) so no employer repo is read here."""
    out = []
    for key, g in group_repos(records).items():
        cl = classify(key, "claude", home=home, root=root, cache=cache)
        if cl["class"] in ("employer", "unknown"):
            out.append({"repo": key, "slug": cl["slug"], "class": cl["class"],
                        "status": "handoff" if restricted(family) else "branch-pr"})
    return out


def limit_fragment_file(path: Path, sid: str, *, home=None, root=None, cache=None) -> bool:
    """Apply the H25 limits to one fragment in place. True when it changed."""
    recs = ledger(sid, home=home)
    fam = session_family(recs, root=root)
    lim = limited_repos(recs, fam, home=home, root=root, cache=cache)
    if not lim:
        return False
    text = path.read_text(encoding="utf-8")
    new = limit_fragment(text, lim, family=fam, public=workspace_public(root),
                         tokens=employer_tokens(lim, root=root))
    if new == text:
        return False
    path.write_text(new, encoding="utf-8")
    return True


def fragment_sessions(ws: Path, rel: str, text: str, *, home=None) -> List[str]:
    """Ledger sids that wrote this fragment (recorded path), share its stem, or that it names."""
    tele = telemetry(home) / "sessions"
    stem = Path(rel).stem
    named = set(re.findall(r"^(?:SessionID|HostSession):\s*(\S+)", text, re.MULTILINE))
    out = []
    for lf in sorted(tele.glob("*.touched")) if tele.is_dir() else []:
        sid = lf.stem
        if sid == stem or sid in named:
            out.append(sid)
            continue
        for r in ledger(sid, home=home):
            if r.get("path") == rel and _real(r.get("repo", "")) == _real(ws):
                out.append(sid)
                break
    return out


def limit_for_fold(ws: Path, frag: Path, text: str, *, home=None, root=None) -> str:
    """compact-sessions.py hook: the fragment text with H25 limits for every session that wrote it."""
    rel = frag.resolve().relative_to(Path(_real(ws))).as_posix()
    for sid in fragment_sessions(ws, rel, text, home=home):
        recs = ledger(sid, home=home)
        fam = session_family(recs, root=root)
        lim = limited_repos(recs, fam, home=home, root=root)
        if lim:
            text = limit_fragment(text, lim, family=fam, public=workspace_public(root),
                                  tokens=employer_tokens(lim, root=root))
    return text


# --------------------------------------------------------------------------- the sweeper

def _mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except OSError:
        return 0.0


def last_activity(sid: str, *, home=None, ws: Optional[Path] = None) -> float:
    tele = telemetry(home)
    wh = _wh()
    safe = wh._safe(sid)
    times = [_mtime(tele / "sessions" / f"{safe}.touched")]
    claims = tele / "claims"
    if claims.is_dir():
        times += [_mtime(d) for d in claims.glob(f"{safe}.*")]
    if ws is not None:
        times.append(_mtime(ws / ".workspace" / "state" / "sessions" / f"{safe}.json"))
        times.append(_mtime(ws / "06-context" / "sessions" / f"{safe}.touched"))
    return max(times)


def _dispatcher_paths(ws: Path, sid: str) -> List[str]:
    """The Claude dispatcher's own workspace touch file for this sid (06-context/sessions/<sid>.touched)."""
    f = ws / "06-context" / "sessions" / f"{re.sub(r'[^A-Za-z0-9._-]', '-', sid)[:80]}.touched"
    try:
        return [ln.strip() for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip()]
    except OSError:
        return []


def _ws_view(sid: str, ws: Path, *, home=None) -> dict:
    recs = [r for r in ledger(sid, home=home) if _real(r.get("repo", "")) == str(ws)]
    paths = {r["path"] for r in recs if r.get("path")} | set(_dispatcher_paths(ws, sid))
    return {"paths": paths, "touched": bool(recs) or bool(paths), "shell": any(not r.get("path") for r in recs)}


def _named_fragments(ws: Path, sid: str, dirty: List[str]) -> set:
    out = set()
    for p in dirty:
        if not FRAGMENT_RE.match(p):
            continue
        if Path(p).stem == sid:
            out.add(p)
            continue
        try:
            text = (ws / p).read_text(encoding="utf-8")[:4000]
        except OSError:
            continue
        if re.search(rf"^(?:SessionID|HostSession):\s*{re.escape(sid)}\s*$", text, re.MULTILINE):
            out.add(p)
    return out


def partition(sid: str, ws: Path, dirty: List[str], live: Dict[str, dict], *, home=None) -> dict:
    """{mechanical, substantive} dirty workspace paths of one dead session, minus live claims."""
    me = _ws_view(sid, ws, home=home)
    claimed = set().union(*(v["paths"] for v in live.values())) if live else set()
    live_ws = any(v["touched"] for v in live.values())
    dset = set(dirty)
    frags = ({p for p in me["paths"] if FRAGMENT_RE.match(p)} | _named_fragments(ws, sid, dirty)) & dset
    mech = set(frags)
    if me["touched"] and not live_ws:
        mech |= {g for g in GENERATED if g in dset}
    mech -= claimed
    subst = {p for p in me["paths"] if p in dset and p not in mech and p not in claimed}
    return {"mechanical": sorted(mech), "substantive": sorted(subst)}


def _commit_identity(ws: Path, family: str, *, home=None, root=None, hostname=None) -> Optional[dict]:
    pr = _pr()
    ident = _identity(str(ws), family, home=home, root=root, hostname=hostname)
    if ident.get("invariants_hit") or not ident.get("expected"):
        return None
    try:
        rows = {r.get("id"): r for r in pr.load_table("devices", root=root).get("identities") or []}
    except Exception:  # noqa: BLE001
        return None
    row = rows.get(ident["expected"]) or {}
    if not row.get("email") or not row.get("name"):
        return None
    return {"id": ident["expected"], "name": row["name"], "email": row["email"]}


def _surface_of(sid: str, *, home=None) -> str:
    hosts = [r.get("host") for r in ledger(sid, home=home) if r.get("host")]
    return hosts[0] if hosts else "unknown"


def sweep(*, home=None, root=None, current_sid: str = "", host: str = "unknown", budget: float = 4.0,
          now: Optional[float] = None, idle_s: float = IDLE_S, dry_run: bool = False, hostname=None) -> dict:
    """Commit dead sessions' mechanical workspace leftovers; record notices for substantive ones."""
    t0 = time.monotonic()
    out: Dict[str, Any] = {"committed": [], "notices": [], "skipped": [], "workspace": None}
    tele = telemetry(home)
    sess = tele / "sessions"
    ws = workspace_root(home=home, root=root)
    if ws is None or not sess.is_dir():
        return out
    out["workspace"] = str(ws)
    now = time.time() if now is None else now
    sids = [p.stem for p in sorted(sess.glob("*.touched"))]
    live, dead = {}, []
    for sid in sids:
        if sid == _wh()._safe(current_sid) or last_activity(sid, home=home, ws=ws) > now - idle_s:
            live[sid] = _ws_view(sid, ws, home=home)
        else:
            dead.append(sid)
    for f in (ws / "06-context" / "sessions").glob("*.touched"):
        if f.stem not in sids and f.stem not in dead and _mtime(f) > now - idle_s:
            live[f.stem] = {"paths": set(_dispatcher_paths(ws, f.stem)), "touched": True, "shell": False}
    dirty = _dirty(ws)
    if dirty is None:
        return out
    hfam = host_family(host, root=root)
    for sid in dead:
        if time.monotonic() - t0 > budget * 0.8:
            out["skipped"].append(sid)
            continue
        part = partition(sid, ws, dirty, live, home=home)
        surface = _surface_of(sid, home=home)
        done = not part["mechanical"]
        if part["mechanical"] and dry_run:
            out["committed"].append({"sid": sid, "paths": part["mechanical"], "sha": None, "dry_run": True})
        elif part["mechanical"]:
            for p in part["mechanical"]:
                if FRAGMENT_RE.match(p) and (ws / p).is_file():
                    limit_fragment_file(ws / p, sid, home=home, root=root)
            who = _commit_identity(ws, hfam, home=home, root=root, hostname=hostname)
            sha = _commit(ws, part["mechanical"], sid, surface, who) if who else None
            if sha:
                out["committed"].append({"sid": sid, "paths": part["mechanical"], "sha": sha})
                dirty = [p for p in dirty if p not in part["mechanical"]]
                done = True
            else:
                part["substantive"] = sorted(set(part["substantive"]) | set(part["mechanical"]))
        if part["substantive"]:
            out["notices"].append({"sid": sid, "surface": surface, "files": len(part["substantive"]),
                                   "text": notice_text(surface, sid, len(part["substantive"]))})
        elif done and not dry_run:
            _close_ledger(sess, sid)
    if not dry_run:
        _write_notices(tele, out["notices"])
        _prune_closed(sess, now)
    return out


def notice_text(surface: str, sid: str, n: int) -> str:
    return (f"uncommitted work from {surface} session {sid}: {n} file{'s' if n != 1 else ''} — "
            f"run: ws closure plan --session {sid}")


def _commit(ws: Path, paths: List[str], sid: str, surface: str, who: dict) -> Optional[str]:
    r = _git(ws, "add", "-A", "--", *paths)
    if r is None or r.returncode != 0:
        return None
    msg = f"session: sweep {surface} session {sid[:12]} — mechanical leftovers (H23 closure)"
    r = _run(["git", "-c", f"user.name={who['name']}", "-c", f"user.email={who['email']}", "commit", "-q",
              "--only", "-m", msg, "--", *paths], ws)
    if r is None or r.returncode != 0:
        _git(ws, "reset", "-q", "--", *paths)
        return None
    head = _git(ws, "rev-parse", "HEAD")
    return head.stdout.strip() if head is not None and head.returncode == 0 else None


def _close_ledger(sess: Path, sid: str) -> None:
    try:
        os.replace(sess / f"{sid}.touched", sess / f"{sid}.closed")
    except OSError:
        pass


def _prune_closed(sess: Path, now: float) -> None:
    for f in sess.glob("*.closed"):
        if _mtime(f) < now - LEDGER_MAX_AGE_S:
            try:
                f.unlink()
            except OSError:
                pass


def _write_notices(tele: Path, notices: List[dict]) -> None:
    target = tele / NOTICES_NAME
    try:
        tmp = target.with_name(f".{target.name}.{os.getpid()}.tmp")
        tmp.write_text(json.dumps({"schema_version": 1, "notices": notices}, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, target)
    except OSError:
        pass


def read_notices(home=None) -> List[str]:
    """Card notice lines (session-status). Fail-open: [] on any problem."""
    try:
        base = (Path(home) if home is not None else Path.home()) / ".config" / "snds-workspace" / "telemetry"
        obj = json.loads((base / NOTICES_NAME).read_text(encoding="utf-8"))
        return [str(n["text"]) for n in obj.get("notices") or [] if isinstance(n, dict) and n.get("text")]
    except (OSError, ValueError, AttributeError, KeyError, TypeError):
        return []


# --------------------------------------------------------------------------- CLI

def resolve_session(sid: str, *, home=None) -> str:
    """`latest` is the most recently written ledger (for an agent that does not know its host
    session id); anything else is taken as given."""
    if sid != "latest":
        return sid
    sess = telemetry(home) / "sessions"
    files = sorted(sess.glob("*.touched"), key=_mtime) if sess.is_dir() else []
    return files[-1].stem if files else "latest"


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["--self-test"]:
        return self_test()
    ap = argparse.ArgumentParser(prog="closure.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan")
    p.add_argument("--session", required=True)
    p.add_argument("--family", default="auto")
    p.add_argument("--json", action="store_true")
    f = sub.add_parser("fragment")
    f.add_argument("--session", required=True)
    f.add_argument("path")
    s = sub.add_parser("sweep")
    s.add_argument("--json", action="store_true")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--budget", type=float, default=30.0)
    a = ap.parse_args(argv)
    if a.cmd in ("plan", "fragment"):
        a.session = resolve_session(a.session)
    if a.cmd == "plan":
        res = plan(a.session, family=a.family)
        print(json.dumps(res, indent=2) if a.json else format_plan(res))
        return 0
    if a.cmd == "fragment":
        changed = limit_fragment_file(Path(a.path), a.session)
        print(f"closure fragment: {'limited' if changed else 'unchanged'} {a.path}")
        return 0
    res = sweep(budget=a.budget, dry_run=a.dry_run, host="human")
    print(json.dumps(res, indent=2) if a.json else
          f"closure sweep: {len(res['committed'])} committed, {len(res['notices'])} notice(s)")
    return 0


# --------------------------------------------------------------------------- self-test

def self_test() -> int:
    """Runs TestClosure's cases (closure_cases) in a synthetic world; temp HOME only."""
    results = closure_cases()
    failed = [r for r in results if not r[1]]
    for name, good, detail in results:
        print(f"{'ok  ' if good else 'FAIL'} {name}" + ("" if good else f" — {detail}"))
    print(f"closure self-test: {len(results) - len(failed)}/{len(results)} passed")
    return 1 if failed else 0


def closure_cases() -> list:
    """[(name, ok, detail)] from fixtures/closure/cases.py (synthetic owners, temp HOME)."""
    import importlib.util  # noqa: PLC0415
    spec = importlib.util.spec_from_file_location("closure_fixture_cases",
                                                  TOOLS / "fixtures" / "closure" / "cases.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.run_cases(_sibling("closure"))


if __name__ == "__main__":
    sys.exit(main())
