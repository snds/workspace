#!/usr/bin/env python3
"""git_lanes.py — global config-based git lanes for every local committer (H18, wave 1).

The lanes are git >= 2.54 config-based hooks (`hook.<name>.command` / `.event` / `.enabled`) in one
rendered include that only Sean installs, through `workspace-doctor.sh --install-git-hooks` (the
installers.py `git-hooks` name: TTY + human verdict, diff + y/N, backup, byte-for-byte uninstall).
Every lane enters through the one pinned entry point, `~/.config/snds-workspace/bin/ws-hook lane EVENT`
(W2-0 item 2), which runs the PINNED copy of this file (`~/.config/snds-workspace/lib/current/09-tools/`),
so Cursor, Codex, Copilot, other local agents and humans all pass the same boundary and the include
stays byte-stable while the lanes evolve. No ws-hook (no pin) means the lane allows. The Claude floor
(`ws-claude-wall`, from the Claude overlay) is a second channel and keeps its own semantics: for a
Claude chain the lane calls the same `profile_resolve.floor_decide`, so a lane is never weaker.

  git_lanes.py hook EVENT [HOOK_ARGS...]     stdin: pre-push ref lines (what `ws-hook lane EVENT` runs)
  git_lanes.py hook prepare-commit-msg FILE [SOURCE [SHA]]   the H10 trailer lane (below)
  git_lanes.py hook post-commit              the H11 post-commit verify (detached; never blocks)
  git_lanes.py gate-verify --top DIR --tree T --head H --range R [--via V] [--budget S]
  git_lanes.py gate-notice [--top DIR]       the one-line last-gate notice (card, stop hooks), or nothing
  git_lanes.py render [--check]              write/check 00-bootstrap/dist/git/lanes/ws-lanes.inc
  git_lanes.py audit [--repo DIR]... [--cache] [--home DIR] [--json]
  git_lanes.py --self-test

Lanes are deciders: they read the repo and the pinned tables and write nothing into a repo's tracked
state. The H10 trailer lane (prepare-commit-msg) writes only the message file git hands it: in the
workspace, and in a positively personal repo that opts in (`git config ws.laneTrailer true`), it adds
`Workspace-Lane: <surface>/<family>/<device>`. Never in an employer repo, never in an unknown one; any
error writes nothing and allows.

H11, the gate at commit and push (workspace lane only; every write goes to the workspace's gitignored
`.workspace/state/`): post-commit detaches `nightly.py --phases verify --from-diff --range HEAD~1..HEAD
--fast` and records the result for HEAD's tree in `last-gate.json` (a ring of the last 50 runs).
pre-push reuses that record on a tree-hash match, otherwise runs `nightly.py --phases verify --from-diff
--range <upstream>..<pushed> --fast --budget 20` itself. It is REPORT-ONLY: it blocks only when Sean's
installer set `ws.pushgate = block` in the managed ~/.gitconfig block on that machine (a repo-local
value never counts), and then only on a red (CHARGED) verify. WS_PUSH_GATE=off switches the gate lanes
off. WS_GATE_BYPASS='<reason>' lets a held push through only when no agent is in the process ancestry
(profile_resolve.agent_check with the hook's non-TTY stdin set aside); an honoured or refused bypass
is recorded in the ring and in receipts.jsonl. Every gate line ends in `[gate:<verdict>@<tree12>]`,
a suffix that depends only on the tree and its verdict, so it is identical whichever chain pushed.
The lane is chosen by the repo profile (profile_resolve):
  employer   I1 over the commit identity (pre-commit, commit-msg, pre-merge-commit) and over every
             commit and annotated tag in a pushed range (author AND committer on the employer
             allowlist; any personal marker blocks). R2 (agent default-branch and force pushes) is
             report-only here, under H15's rollout. Nothing is ever written into an employer repo.
  workspace  identity as for personal, plus the H25 employer-substance scan over the staged files
             (blocks above its baseline) and the H1 heal lane (`nightly.py --lane pre-commit`).
  personal   the device-mismatch flag (a notice, never a block).
  unknown    agents WARN, humans are allowed.
A Claude chain (the most restrictive family anywhere in the chain; env markers only ever tighten)
first gets the Claude floor's own decision. An infrastructure error, a missing table or a timeout
allows with a notice (the wrapper exits 0): the Claude floor, the transport block and the servers
remain. Per-invocation bypasses (hook-skipping flags, per-command config, a redirected git config or
HOME) are declared residuals answered by H15's R6 rules and CI; config entries that replace, clear
or disable a lane at any scope are what `audit` (doctor --check) reports.

Exit codes: hook 0 allow · 1 block. render --check 1 on drift. audit 0 clean · 1 findings · 3 not
installed · 2 could not run. Stdlib only; Python 3.9+.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.dont_write_bytecode = True          # the pinned lib is read-only; never litter it

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
LANE_EVENTS = ("pre-commit", "commit-msg", "pre-merge-commit", "pre-push")
TRAILER_EVENT = "prepare-commit-msg"      # H10: the one lane that writes (the message file only)
TRAILER_KEY = "Workspace-Lane"
TRAILER_OPTIN = "ws.laneTrailer"          # a personal repo's own opt-in (repo-local git config)
TRAILER_BUDGET_S = 5.0
GATE_EVENT = "post-commit"                # H11: the detached verify (never blocks)
LANE_PREFIX = "ws-lane-"
LANES: Tuple[Tuple[str, str], ...] = tuple((LANE_PREFIX + ev, ev)
                                           for ev in LANE_EVENTS + (TRAILER_EVENT, GATE_EVENT))
WS_HOOK_REL = ".config/snds-workspace/bin/ws-hook"     # the one pinned entry point (under HOME)
DIST_INCLUDE_REL = "00-bootstrap/dist/git/lanes/ws-lanes.inc"
INSTALL_INCLUDE_REL = ".config/snds-workspace/git/lanes/ws-lanes.inc"   # under HOME
PINNED_SELF_REL = ".config/snds-workspace/lib/current/09-tools/git_lanes.py"
GITCONFIG_BEGIN = "# BEGIN snds-workspace git lanes (installers.py git-hooks; do not edit)"
GITCONFIG_END = "# END snds-workspace git lanes"
LANE_BUDGET_S = 10.0
HEAL_TIMEOUT_S = 120.0
EMP_TIMEOUT_S = 30.0
GIT_TIMEOUT_S = 10
TAG = "ws-lanes"
AGENT_FAMILIES_R2 = ("cursor", "codex", "copilot", "gemini", "unknown-agent")
# H11 gate
GATE_STATE_DIR = ".workspace/state"                     # gitignored, workspace only
GATE_FILE = "last-gate.json"
RECEIPTS_FILE = "receipts.jsonl"                        # close-out-dispatch.py RECEIPTS_REL
GATE_RING = 50
GATE_BUDGET_S = 20.0                                    # nightly --budget for the pre-push verify
GATE_POST_BUDGET_S = 20.0                               # the detached post-commit verify
GATE_LOCK_STALE_S = 180.0
POST_BUDGET_S = 6.0                                     # the post-commit hook process itself
PUSHGATE_KEY = "ws.pushgate"
KILL_ENV = "WS_PUSH_GATE"
BYPASS_ENV = "WS_GATE_BYPASS"
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
GATE_VERDICTS = ("green", "red")                        # a record reusable on a tree match
GATE_FIX = "python3 09-tools/nightly.py --phases verify --from-diff --range @{u}..HEAD --fast"

_PR = None      # test seam: a stand-in profile_resolve module


# --------------------------------------------------------------------------- rendering


def lane_command(event: str) -> str:
    """The shell command git runs for one lane: the one pinned entry point, `bin/ws-hook lane EVENT`,
    which runs the pinned ws_hook.py, which runs the pinned sibling of this file. It carries no "$@":
    git appends the hook args. No ws-hook (no pin) allows. The PYTHON* startup variables are dropped so
    a caller's PYTHONPATH cannot route the pinned lib elsewhere."""
    return (f'W="$HOME/{WS_HOOK_REL}"; [ -x "$W" ] || exit 0; '
            'exec env -u PYTHONPATH -u PYTHONHOME -u PYTHONSTARTUP -u PYTHONINSPECT -u PYTHONUSERBASE '
            f'"$W" lane {event}')


def _cfg_quote(value: str) -> str:
    """A git config value in double quotes (';' and '#' would start a comment unquoted)."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_include() -> str:
    lines = [
        "# snds-workspace git lanes (H18). Generated by 09-tools/git_lanes.py render; do not edit.",
        "# Installed only by a human: workspace-doctor.sh --install-git-hooks (included from ~/.gitconfig).",
        "# Global config-based hooks (git >= 2.54). Each lane execs the pinned bin/ws-hook, which runs the",
        "# pinned git_lanes.py; with no pin the lane allows. Audit: python3 09-tools/git_lanes.py audit.",
    ]
    for name, event in LANES:
        lines += [f'[hook "{name}"]', f"\tcommand = {_cfg_quote(lane_command(event))}",
                  f"\tevent = {event}", "\tenabled = true"]
    return "\n".join(lines) + "\n"


def gitconfig_block(home: Path) -> str:
    """The managed ~/.gitconfig block the installer adds: one include line, nothing else."""
    return (f"{GITCONFIG_BEGIN}\n[include]\n\tpath = ~/{INSTALL_INCLUDE_REL}\n{GITCONFIG_END}\n")


def expected_lanes() -> Dict[str, dict]:
    return {name: {"command": lane_command(ev), "events": [ev], "enabled": True} for name, ev in LANES}


# --------------------------------------------------------------------------- profile_resolve


def _pr():
    global _PR
    if _PR is None:
        path = TOOLS / "profile_resolve.py"
        spec = importlib.util.spec_from_file_location("ws_lanes_profile_resolve", path)
        if spec is None or spec.loader is None:
            raise ImportError(str(path))
        mod = importlib.util.module_from_spec(spec)
        sys.modules["ws_lanes_profile_resolve"] = mod
        spec.loader.exec_module(mod)
        # One hook process asks for the LocalHostName several times (device, projects_root per resolve);
        # the answer cannot change within it, so the lane asks scutil once (same results, less latency).
        probe = getattr(mod, "_default_scutil", None)
        if callable(probe):
            box: dict = {}

            def _once():
                if "v" not in box:
                    box["v"] = probe()
                return box["v"]
            mod._default_scutil = _once
        _PR = mod
    return _PR


# --------------------------------------------------------------------------- decisions


def _allow(**kw) -> dict:
    d = {"decision": "allow", "rule": None, "reason": "", "notices": [], "lane": None, "family": None,
         "repo_class": None}
    d.update(kw)
    return d


def _block(base: dict, rule: str, reason: str, lane: str) -> dict:
    out = dict(base)
    out.update(decision="block", rule=rule, reason=reason, lane=lane)
    return out


def _employer_identity(dev_t: dict, pr) -> Optional[str]:
    ids = pr._identities(dev_t)
    for iid in (dev_t.get("employer_allowlist") or {}).get("identity_ids") or []:
        row = ids.get(iid)
        if row and row.get("email"):
            return f"{row.get('name') or ''} <{row['email']}>".strip()
    return None


def _commit_fix(dev_t: dict, pr) -> str:
    exp = _employer_identity(dev_t, pr)
    if not exp:
        return "set this repo's user.name and user.email to an identity on the employer allowlist, then retry"
    name, _, mail = exp.partition(" <")
    return (f"expected {exp}; run `git config user.name \"{name}\"` and `git config user.email "
            f"\"{mail.rstrip('>')}\"` in this repo, then retry")


def _push_fix(dev_t: dict, pr) -> str:
    exp = _employer_identity(dev_t, pr)
    who = f"the employer identity {exp}" if exp else "an identity on the employer allowlist"
    return (f"rewrite those commits with {who} (set user.name and user.email in this repo, then "
            "`git rebase --exec 'git commit --amend --no-edit --reset-author' <upstream>`), then push again")


def _locate(pr, here: Path, e: dict, git: str) -> tuple:
    """(git dir, work tree, remote urls as git resolves the repo config): the floor's own readers."""
    gitdir, top = pr._floor_locate(here, e, git)
    cfg = pr._floor_config_remotes(here, gitdir, e, git) if (gitdir is not None or top is not None) else None
    return gitdir, top, cfg


def _classify(pr, here: Path, e: dict, det: dict, hook_args: List[str], event: str, root, home, git: str,
              loc: Optional[tuple] = None) -> dict:
    """Repo facts, most restrictive of every source (the floor's own reading, plus path globs)."""
    url_cls = "none"
    if event == "pre-push" and len(hook_args) >= 2:
        cls2 = [pr._push_url_class(str(a), root) for a in hook_args[:2]]
        url_cls = max(cls2, key=lambda c: pr.CLASS_RANK.get(c, -1))
    gitdir, top, cfg_urls = loc if loc is not None else _locate(pr, here, e, git)
    facts = {"gitdir": gitdir, "top": top, "url_cls": url_cls, "res": {}, "employer": url_cls == "employer",
             "role": "unknown", "owner_class": "unknown", "positively_personal": False, "profile": None,
             "cfg_urls": None}
    if gitdir is None and top is None:
        return facts
    res: dict = {}
    if top is not None:
        res = pr.repo_resolve(str(top), root=root, home=home, detection=det)
        main = pr._main_checkout(top)
        if main is not None:
            mres = pr.repo_resolve(str(main), root=root, home=home, detection=det)
            res = dict(res, owner_class=max((res.get("owner_class"), mres.get("owner_class")),
                                            key=lambda c: pr.CLASS_RANK.get(str(c), pr.CLASS_RANK["unknown"])),
                       positively_personal=bool(res.get("positively_personal") and mres.get("positively_personal")),
                       role=res.get("role") if res.get("role") == "workspace" else mres.get("role"))
    cfg_cls = [pr._push_url_class(u, root) for u in cfg_urls or []]
    glob = None
    if top is not None:
        table = pr._try_table("context-remotes", root) or {}
        glob = pr._glob_hit(pr._real(top), pr.projects_root(root=root, home=home),
                            list(table.get("employer_path_globs") or []))
    employer = (res.get("owner_class") == "employer" or url_cls == "employer" or "employer" in cfg_cls
                or bool(glob))
    facts.update(res=res, employer=employer, role=str(res.get("role") or "unknown"),
                 owner_class="employer" if employer else str(res.get("owner_class") or "unknown"),
                 positively_personal=bool(res.get("positively_personal")) and not employer,
                 profile=res.get("profile"), cfg_urls=cfg_urls)
    return facts


def _r2_notices(pr, facts: dict, event: str, stdin_lines: List[str], walls: str, e: dict, git: str) -> List[str]:
    """R2 for non-Claude agents on employer repos, REPORT-ONLY in wave 1 (H15 rollout): notices only."""
    if walls not in AGENT_FAMILIES_R2:
        return []
    top = facts.get("top")
    cur, dflt = pr._repo_heads(top) if top is not None else (None, None)
    prof = facts.get("profile") or "centric-engineering"
    out = []
    if event in ("pre-commit", "pre-merge-commit") and cur and pr._ref_kind(cur, dflt) == "default":
        out.append(f"R2 report-only: would deny an agent commit on the default branch {cur!r} (profile {prof})")
    if event == "pre-push":
        genv = pr._clean_git_env(e)
        for ln in pr._push_lines(stdin_lines):
            if ln.get("bad") or not ln["remote_ref"].startswith("refs/heads/"):
                continue
            ref = ln["remote_ref"]
            if pr._ref_kind(ref, dflt) == "default":
                what = "a deletion of" if pr._ZERO_SHA_RE.match(ln["local_sha"]) else "a push to"
                out.append(f"R2 report-only: would deny {what} the default branch {pr._short_ref(ref)!r} "
                           f"(profile {prof})")
            elif not pr._ZERO_SHA_RE.match(ln["remote_sha"]) and not pr._ZERO_SHA_RE.match(ln["local_sha"]):
                r = pr._git_run(["merge-base", "--is-ancestor", ln["remote_sha"], ln["local_sha"]],
                                top if top is not None else Path("."), genv, git)
                if r is not None and r.returncode == 1:
                    out.append(f"R2 report-only: would deny a force-push to {pr._short_ref(ref)!r} (profile {prof})")
    return out


def _employer_lane(pr, base: dict, facts: dict, event: str, hook_args: List[str], stdin_lines: List[str],
                   here: Path, e: dict, root, git: str) -> dict:
    dev_t = pr._try_table("devices", root)
    if dev_t is None:
        base["notices"].append("devices table unavailable: employer identity check skipped (fail-open)")
        return base
    if event != "pre-push":
        idents = pr._commit_idents(here, e, git)
        if not idents:
            base["notices"].append("commit identity unreadable; git itself refuses a commit with no identity")
        for role, em in idents:
            cls = pr.email_class(em, dev_t)
            if cls != "employer":
                what = "a personal identity" if cls == "personal" else "an identity not on the employer allowlist"
                return _block(base, "I1", f"{event}: the {role} identity {em!r} is {what}; an employer repo takes "
                                          f"only employer identities; {_commit_fix(dev_t, pr)}", "employer")
        return base
    remote = str(hook_args[0]) if hook_args else "origin"
    genv = pr._clean_git_env(e)
    top, gitdir = facts.get("top"), facts.get("gitdir")
    for ln in pr._push_lines(stdin_lines):
        if ln.get("bad"):
            continue
        try:
            idents, tags_ok = pr._push_idents(top if top is not None else here, ln, remote, genv, git, gitdir)
        except pr._TagChainTooDeep as exc:
            return _block(base, "I1", f"annotated tag chain from {str(exc)[:12]} is too long to check its "
                                      "taggers (I1)", "employer")
        if not tags_ok:
            base["notices"].append("I1 tag check unavailable (git error)")
        if idents is None:
            base["notices"].append("I1 range check unavailable (git error); CI re-checks the pushed range")
            continue
        for kind, sha, role, em in idents:
            cls = pr.email_class(em, dev_t)
            if cls != "employer":
                what = "a personal identity" if cls == "personal" else "an identity not on the employer allowlist"
                return _block(base, "I1", f"{kind} {sha[:12]} in the push has {what} as {role}; an employer repo "
                                          f"takes only employer identities, whatever created the commit; "
                                          f"{_push_fix(dev_t, pr)}", "employer")
    return base


def _heal_lane(base: dict, top: Path, e: dict) -> dict:
    """H1: the workspace's own stateless pre-commit lane (nightly.py --lane pre-commit), run from
    the checkout being committed. Missing or broken: allow with a notice (CI re-checks)."""
    script = top / "09-tools" / "nightly.py"
    if not script.is_file():
        return base
    try:
        r = subprocess.run([sys.executable, str(script), "--lane", "pre-commit"], cwd=str(top), env=e,
                           capture_output=True, text=True, timeout=HEAL_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError) as exc:
        base["notices"].append(f"H1 heal lane could not run ({exc.__class__.__name__}); CI re-checks")
        return base
    if r.returncode == 1:
        return _block(base, "H1", (r.stderr or "").strip() or "generated files are stale", "workspace")
    if r.stderr.strip():
        base["notices"].append(r.stderr.strip().splitlines()[-1])
    return base


def _emp_lane(base: dict, top: Path, e: dict) -> dict:
    """H25 (W1-10): the employer-substance scan over the staged files, blocking against the baseline
    (`check-secrets.py --class employer-substance --baseline-check --staged`, from the checkout being
    committed). Exit 1 blocks; a missing script, a timeout or any other exit allows with a notice
    (CI runs the full-tree check on every push)."""
    script = top / "09-tools" / "check-secrets.py"
    if not script.is_file():
        return base
    try:
        r = subprocess.run([sys.executable, str(script), "--class", "employer-substance", "--baseline-check",
                            "--staged"], cwd=str(top), env=e, capture_output=True, text=True,
                           timeout=EMP_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError) as exc:
        base["notices"].append(f"H25 employer-substance scan could not run ({exc.__class__.__name__}); CI re-checks")
        return base
    if r.returncode == 1:
        # The scan prints `path rule count > baseline` lines only; matched text is never printed.
        lines = [ln.strip() for ln in (r.stderr or "").splitlines() if ln.strip()]
        return _block(base, "H25", "; ".join(lines[-6:]) or "employer-substance baseline exceeded", "workspace")
    if r.returncode != 0:
        base["notices"].append(f"H25 employer-substance scan exited {r.returncode}; CI re-checks")
    return base


# --------------------------------------------------------------------------- H11 gate


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _git_out(top: Path, args: List[str], env: Optional[dict] = None, git: str = "git") -> Optional[str]:
    try:
        r = subprocess.run([git, "-C", str(top), *args], capture_output=True, text=True, timeout=GIT_TIMEOUT_S,
                           env=_clean_env(env))
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def tree_of(top: Path, rev: str, env: Optional[dict] = None, git: str = "git") -> Optional[str]:
    return _git_out(top, ["rev-parse", "-q", "--verify", f"{rev}^{{tree}}"], env, git) or None


def _detector(name: Any) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", str(name)).strip("-") or "unknown"


def gate_suffix(tree: Optional[str], status: str, detectors: Any = ()) -> str:
    """`[gate:<verdict>@<tree12>]`: the tree and its verdict only, never the chain that pushed."""
    verdict = str(status)
    dets = sorted({_detector(d) for d in detectors or []})
    if status == "red" and dets:
        verdict = "red:" + ",".join(dets)
    return f"[gate:{verdict}@{(tree or 'unknown')[:12]}]"


def _state_dir(top: Path) -> Path:
    return Path(top) / GATE_STATE_DIR


def read_gate(top: Path) -> dict:
    try:
        obj = json.loads((_state_dir(top) / GATE_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return obj if isinstance(obj, dict) else {}


def gate_for_tree(rec: dict, tree: Optional[str]) -> Optional[dict]:
    """The newest green/red verify of `tree` in the record (current entry, then the ring)."""
    if not tree:
        return None
    cur = rec.get("gate")
    if rec.get("tree") == tree and isinstance(cur, dict) and cur.get("status") in GATE_VERDICTS:
        return cur
    for r in reversed([x for x in rec.get("ring") or [] if isinstance(x, dict)]):
        if r.get("tree") == tree and r.get("status") in GATE_VERDICTS and not r.get("event"):
            return r
    return None


def write_gate(top: Path, tree: str, head: Optional[str], entry: dict) -> None:
    """Atomic write of last-gate.json: this entry becomes current and joins the ring (last 50).
    A SessionEnd `nightly` field for the same tree is kept. Fails quiet."""
    try:
        d = _state_dir(top)
        d.mkdir(parents=True, exist_ok=True)
        rec = read_gate(top)
        row = dict(entry, tree=tree, head=head)
        ring = [x for x in rec.get("ring") or [] if isinstance(x, dict)][-(GATE_RING - 1):] + [row]
        new = {"schema_version": 2, "head": head, "tree": tree, "ts": row.get("ts") or _now(), "gate": row,
               "held": bool(row.get("held")), "ring": ring}
        if rec.get("tree") == tree and isinstance(rec.get("nightly"), dict):
            new["nightly"] = rec["nightly"]
        tmp = d / f".{GATE_FILE}.{os.getpid()}.tmp"
        tmp.write_text(json.dumps(new, indent=2) + "\n", encoding="utf-8")
        os.replace(tmp, d / GATE_FILE)
    except OSError:
        pass


def note_gate_event(top: Path, tree: str, head: Optional[str], base: dict, **event: Any) -> None:
    """Record a hold or a bypass against the verdict it acted on (the ring keeps both)."""
    entry = {k: base.get(k) for k in ("status", "detectors", "range")}
    entry.update(event, via="pre-push", ts=_now())
    write_gate(top, tree, head, entry)


def _lock(top: Path, tree: str) -> Optional[Path]:
    """O_EXCL lock for one in-flight verify of a tree; a lock older than GATE_LOCK_STALE_S is broken."""
    p = _state_dir(top) / f"gate-{tree[:16]}.lock"
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.exists() and time.time() - p.stat().st_mtime > GATE_LOCK_STALE_S:
            p.unlink()
        fd = os.open(str(p), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.write(fd, f"{os.getpid()}\n".encode())
        os.close(fd)
        return p
    except FileExistsError:
        return None
    except OSError:
        return None


def run_verify(top: Path, rng: str, *, env: Optional[dict] = None, budget: float = GATE_BUDGET_S,
               via: str = "pre-push") -> dict:
    """`nightly.py --phases verify --from-diff --range R --fast --budget B --json` from the checkout.
    {status: green|red|skipped|error, detectors, why}."""
    script = Path(top) / "09-tools" / "nightly.py"
    if not script.is_file():
        return {"status": "error", "detectors": [], "why": "no 09-tools/nightly.py in this checkout"}
    e = _clean_env(env)
    try:
        r = subprocess.run([sys.executable, str(script), "--phases", "verify", "--from-diff", "--range", rng, "--fast",
                            "--budget", f"{budget:g}", "--json", "--via", via], cwd=str(top), env=e,
                           capture_output=True, text=True, timeout=budget + 15)
    except subprocess.TimeoutExpired:
        return {"status": "skipped", "detectors": [], "why": f"verify outlasted {budget:g}s"}
    except (OSError, subprocess.SubprocessError) as exc:
        return {"status": "error", "detectors": [], "why": f"verify could not run ({exc.__class__.__name__})"}
    try:
        rep = json.loads(r.stdout)
    except ValueError:
        return {"status": "error", "detectors": [], "why": f"verify exited {r.returncode} without a report"}
    st = rep.get("status") if isinstance(rep, dict) else None
    charged = [c for ph in rep.get("phases") or [] if isinstance(ph, dict) for c in ph.get("charged") or []]
    if st == "ok":
        return {"status": "green", "detectors": [], "why": ""}
    if st == "fail":
        return {"status": "red", "detectors": charged or ["close-out-dispatch.py"], "why": ""}
    if st == "skipped":
        return {"status": "skipped", "detectors": [], "why": "a diff-selected step SKIPPED (budget or timeout)"}
    return {"status": "error", "detectors": [], "why": f"verify status {st!r}"}


def verify_tree(top: Path, tree: str, head: Optional[str], rng: str, *, env: Optional[dict] = None,
                budget: float = GATE_BUDGET_S, via: str = "pre-push", wait: bool = True, runner=None) -> dict:
    """Reuse a green/red record for this tree; else run the verify once (lock) and record it. A run
    already in flight for the tree is awaited (wait=True) up to the budget, never duplicated."""
    hit = gate_for_tree(read_gate(top), tree)
    if hit:
        return dict(hit, reused=True)
    lock = _lock(top, tree)
    if lock is None:
        deadline = time.monotonic() + (budget if wait else 0)
        while time.monotonic() < deadline:
            time.sleep(0.25)
            hit = gate_for_tree(read_gate(top), tree)
            if hit:
                return dict(hit, reused=True)
        return {"status": "skipped", "detectors": [], "why": "another verify of this tree is still running"}
    t0 = time.monotonic()
    try:
        res = (runner or run_verify)(top, rng, env=env, budget=budget, via=via)
        entry = {"status": res.get("status") or "error", "detectors": sorted(set(res.get("detectors") or [])),
                 "why": res.get("why") or "", "via": via, "range": rng,
                 "secs": round(time.monotonic() - t0, 2), "ts": _now()}
        write_gate(top, tree, head, entry)
        return entry
    finally:
        try:
            lock.unlink()
        except OSError:
            pass


def pushgate_mode(top: Path, env: Optional[dict] = None, git: str = "git") -> Tuple[str, List[str]]:
    """('block'|'report', notices). Only the installer's value counts: the last `ws.pushgate` entry at
    global scope from ~/.gitconfig itself. A value at any other scope never enables or disables the
    hold, and is named in a notice (and in `audit`)."""
    e = _clean_env(env)
    home = Path(e.get("HOME") or Path.home())
    try:
        r = subprocess.run([git, "-C", str(top), "config", "--show-scope", "--show-origin", "-z", "--get-regexp",
                            r"^ws\.pushgate$"], capture_output=True, timeout=GIT_TIMEOUT_S, env=e)
    except (OSError, subprocess.SubprocessError):
        return "report", ["ws.pushgate unreadable; report-only"]
    ents = parse_listing(r.stdout) if r.returncode == 0 else []
    notes, mode = [], "report"
    gc = _cf(home / ".gitconfig")
    for ent in ents:
        p = _origin_path(ent["origin"], Path(top))
        if ent["scope"] == "global" and p is not None and _cf(p) == gc:
            mode = "block" if str(ent["value"] or "").strip().lower() == "block" else "report"
        else:
            notes.append(f"{PUSHGATE_KEY} at {ent['scope']} scope ({ent['origin']}) is ignored; only the "
                         "installer's ~/.gitconfig block sets the hold")
    return mode, notes


def bypass_allowed(env: dict, ancestry: Optional[list], root: Optional[Path] = None) -> Tuple[bool, str]:
    """WS_GATE_BYPASS counts only with no agent in the process ancestry: profile_resolve.agent_check with
    the hook's own stdio set aside (git hands a pre-push hook the ref list, not a TTY). Undetermined
    (no process table) refuses."""
    try:
        v = _pr().agent_check(env=env, ancestry=ancestry, isatty={"stdin": True, "stdout": True}, root=root)
    except Exception as exc:  # noqa: BLE001
        return False, f"undetermined ({exc.__class__.__name__})"
    ok = bool(v.get("human") and v.get("determined"))
    return ok, ", ".join(str(x) for x in v.get("reasons") or []) or ("human" if ok else "undetermined")


def _safe_text(s: Any, n: int = 120) -> str:
    return re.sub(r"[^ -~]+", " ", str(s or "")).strip()[:n]


def write_gate_receipt(top: Path, *, det: dict, head: Optional[str], result: str, reason: str,
                       root: Optional[Path] = None) -> None:
    """One receipts.jsonl row for a bypass (honoured or refused). Workspace only, never in CI; ids and
    a short sanitised reason only. Fails quiet."""
    if os.environ.get("GITHUB_ACTIONS") or not (Path(top) / "AGENTS.md").is_file():
        return
    try:
        device = _pr().current_device(root=root).get("id") or "unknown"
    except Exception:  # noqa: BLE001
        device = "unknown"
    row = {"ts": _now(), "surface": str(det.get("acting_host") or "unknown"),
           "family": str(det.get("family_for_walls") or "unknown"), "via": "pre-push", "device": device,
           "repo_slug": None, "action_class": "gate-bypass", "credential": "none", "head": head or "unknown",
           "classes": [], "verdict": {"result": result, "reason": _safe_text(reason)}}
    try:
        d = _state_dir(top)
        d.mkdir(parents=True, exist_ok=True)
        with open(d / RECEIPTS_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, sort_keys=True) + "\n")
    except OSError:
        pass


def _gate_off(env: dict) -> bool:
    return str(env.get(KILL_ENV, "")).strip().lower() == "off"


def _push_range(top: Path, local: str, remote_sha: str, env: dict, git: str) -> str:
    zero = re.fullmatch(r"0+", remote_sha or "") is not None
    if not zero and _git_out(top, ["cat-file", "-e", f"{remote_sha}^{{commit}}"], env, git) is not None:
        return f"{remote_sha}..{local}"
    up = _git_out(top, ["rev-parse", "-q", "--verify", "@{u}"], env, git)
    if up:
        base = _git_out(top, ["merge-base", up, local], env, git)
        if base:
            return f"{base}..{local}"
    parent = _git_out(top, ["rev-parse", "-q", "--verify", f"{local}~1"], env, git)
    return f"{parent or EMPTY_TREE}..{local}"


def gate_push(base: dict, top: Path, stdin_lines: List[str], e: dict, det: dict, *, ancestry: Optional[list] = None,
              root: Optional[Path] = None, git: str = "git", runner=None, budget: float = GATE_BUDGET_S) -> dict:
    """The pre-push gate (workspace lane). Report-only unless the installer's ws.pushgate is `block`;
    then a red verify holds the push, unless a human-only WS_GATE_BYPASS lets it through."""
    refs = []
    for ln in stdin_lines:
        parts = str(ln).split()
        if len(parts) == 4 and not re.fullmatch(r"0+", parts[1]):
            refs.append((parts[1], parts[3]))
    if not refs:
        return base
    if _gate_off(e):
        for local, _r in refs[:1]:
            base["notices"].append(f"pre-push gate off ({KILL_ENV}=off); this push is not verified "
                                   f"{gate_suffix(tree_of(top, local, e, git), 'off')}")
        return base
    mode, notes = pushgate_mode(top, e, git)
    base["notices"] += notes
    label = "blocking" if mode == "block" else "report-only"
    seen = set()
    deadline = time.monotonic() + budget
    for local, remote_sha in refs:
        tree = tree_of(top, local, e, git)
        if not tree or tree in seen:
            continue
        seen.add(tree)
        rng = _push_range(top, local, remote_sha, e, git)
        left = max(1.0, deadline - time.monotonic())
        g = verify_tree(top, tree, local, rng, env=e, budget=left, via="pre-push", runner=runner)
        st, dets = g.get("status") or "error", list(g.get("detectors") or [])
        sfx = gate_suffix(tree, st, dets)
        how = " (reused)" if g.get("reused") else ""
        if st == "green":
            base["notices"].append(f"pre-push gate ({label}): green{how} {sfx}")
            continue
        if st != "red":
            base["notices"].append(f"pre-push gate ({label}): {st}, not verified — {g.get('why') or 'no verdict'}; "
                                   f"allowing {sfx}")
            continue
        red = f"red{how} — charged {', '.join(dets) or 'unknown'}"
        if mode != "block":
            base["notices"].append(f"pre-push gate (report-only): {red}; the push goes ahead. Fix: {GATE_FIX} {sfx}")
            continue
        reason = str(e.get(BYPASS_ENV, "") or "").strip()
        if reason:
            ok, why = bypass_allowed(e, ancestry, root)
            write_gate_receipt(top, det=det, head=local, result="bypass" if ok else "bypass-refused", reason=reason,
                               root=root)
            note_gate_event(top, tree, local, g, event="bypass" if ok else "bypass-refused",
                            bypass=_safe_text(reason), held=not ok)
            if ok:
                base["notices"].append(f"pre-push gate (blocking): {red}; allowed by {BYPASS_ENV} (recorded) {sfx}")
                continue
            return _block(base, "GATE", f"pre-push gate: {red}; {BYPASS_ENV} refused — an agent or an undetermined "
                                        f"process is in the ancestry ({why}); the refusal is recorded. Fix: "
                                        f"{GATE_FIX} {sfx}", "workspace")
        note_gate_event(top, tree, local, g, event="held", held=True)
        return _block(base, "GATE", f"pre-push gate: {red}; push held ({PUSHGATE_KEY}=block on this machine). Fix: "
                                    f"{GATE_FIX}, then push again (a human in a plain terminal may set "
                                    f"{BYPASS_ENV}='<reason>') {sfx}", "workspace")
    return base


def _sequencing(gitdir: Optional[Path], env: dict) -> bool:
    """A rebase, cherry-pick, am or revert is replaying commits: post-commit stays quiet."""
    if re.search(r"\b(rebase|cherry-pick|am|revert)\b", str(env.get("GIT_REFLOG_ACTION", ""))):
        return True
    if gitdir is None:
        return False
    return any((Path(gitdir) / n).exists() for n in ("rebase-merge", "rebase-apply", "CHERRY_PICK_HEAD",
                                                     "REVERT_HEAD", "sequencer"))


def post_commit_decide(*, env: Optional[dict] = None, ancestry: Optional[list] = None, root: Optional[Path] = None,
                       home: Optional[Path] = None, cwd: Optional[Any] = None, git: str = "git") -> dict:
    """{action: none|reuse|spawn, line, top, tree, head, range}. Workspace lane only."""
    pr = _pr()
    e = dict(os.environ if env is None else env)
    none = {"action": "none", "line": None}
    if _gate_off(e):
        return none
    here = pr._real(cwd if cwd is not None else os.getcwd())
    det = pr.detect_surface(env=e, ancestry=ancestry, root=root)
    facts = _classify(pr, here, e, det, [], GATE_EVENT, root, home, git)
    top = facts.get("top")
    if top is None or facts["employer"] or facts["role"] != "workspace" or _sequencing(facts.get("gitdir"), e):
        return none
    head = _git_out(top, ["rev-parse", "HEAD"], e, git)
    tree = tree_of(top, "HEAD", e, git)
    if not head or not tree:
        return none
    hit = gate_for_tree(read_gate(top), tree)
    if hit:
        return {"action": "reuse", "top": top, "tree": tree, "head": head,
                "line": f"post-commit gate: {hit.get('status')} (this tree was already verified) "
                        f"{gate_suffix(tree, hit.get('status') or 'error', hit.get('detectors'))}"}
    parent = _git_out(top, ["rev-parse", "-q", "--verify", "HEAD~1"], e, git)
    return {"action": "spawn", "top": top, "tree": tree, "head": head, "range": f"{parent or EMPTY_TREE}..{head}",
            "env": e, "line": f"post-commit gate: verify started in the background {gate_suffix(tree, 'pending')}"}


def spawn_verify(d: dict) -> bool:
    """Detach `git_lanes.py gate-verify` (its own session; stdio closed) and return at once."""
    try:
        subprocess.Popen([sys.executable, "-I", "-S", str(Path(__file__).resolve()), "gate-verify", "--top",
                          str(d["top"]), "--tree", d["tree"], "--head", d["head"], "--range", d["range"],
                          "--via", "post-commit", "--budget", f"{GATE_POST_BUDGET_S:g}"],
                         cwd=str(d["top"]), env=_clean_env(d.get("env")), stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def run_post_commit(*, err=None, decide=None, spawn=None, budget: float = POST_BUDGET_S) -> int:
    """The post-commit path: always exit 0, at most one line."""
    err = err or sys.stderr
    box: dict = {}

    def work():
        try:
            box["v"] = (decide or post_commit_decide)()
        except BaseException as exc:  # noqa: BLE001
            box["e"] = exc

    th = threading.Thread(target=work, daemon=True)
    th.start()
    th.join(budget)
    v = box.get("v") if isinstance(box.get("v"), dict) else None
    if th.is_alive() or "e" in box or not v or v.get("action") == "none":
        return 0
    if v.get("action") == "spawn" and not (spawn or spawn_verify)(v):
        print(f"{TAG}: post-commit gate could not start the verify; the pre-push gate runs it", file=err)
        return 0
    if v.get("line"):
        print(f"{TAG}: {v['line']}", file=err)
    return 0


def gate_notice(top: Path, *, env: Optional[dict] = None, git: str = "git") -> Optional[str]:
    """One line for the card and the stop hooks, or None: HEAD's tree is red or did not verify, or
    HEAD is unpushed and no gate covered its tree (only once a gate has run in this checkout)."""
    rec = read_gate(top)
    if not rec.get("gate") and not rec.get("ring"):
        return None
    tree = tree_of(top, "HEAD", env, git)
    if not tree:
        return None
    cur = rec.get("gate") if rec.get("tree") == tree and isinstance(rec.get("gate"), dict) else None
    hit = gate_for_tree(rec, tree)
    if hit and hit.get("status") == "red":
        return (f"Last gate red for HEAD: {', '.join(hit.get('detectors') or []) or 'unknown'} "
                f"{gate_suffix(tree, 'red', hit.get('detectors'))} — fix, then `{GATE_FIX}`")
    if hit:
        return None
    ahead = _git_out(top, ["rev-list", "--count", "@{u}..HEAD"], env, git)
    if not ahead or not ahead.isdigit() or int(ahead) == 0:
        return None
    st = (cur or {}).get("status") or "unverified"
    return f"HEAD is not gate-verified ({st}) {gate_suffix(tree, st)} — run `{GATE_FIX}`"


def lane_decide(event: str, hook_args: Optional[list] = None, stdin_lines: Optional[list] = None, *,
                env: Optional[dict] = None, ancestry: Optional[list] = None, root: Optional[Path] = None,
                home: Optional[Path] = None, cwd: Optional[Any] = None, hostname: Optional[str] = None,
                git: str = "git", heal: bool = True, gate: bool = True, gate_runner=None) -> dict:
    """{decision: allow|block, rule, reason, notices[], lane, family, repo_class}. Only the workspace
    pre-push gate writes (its own gitignored state)."""
    pr = _pr()
    args = [str(a) for a in hook_args or []]
    lines = [str(x) for x in stdin_lines or []]
    if event not in LANE_EVENTS:
        return _allow(notices=[f"unknown lane event {event!r}; allowing"])
    e = dict(os.environ if env is None else env)
    here = pr._real(cwd if cwd is not None else os.getcwd())
    # Detection (a process-table walk) and the repo readers (git spawns) are independent: run them
    # side by side to stay near the hook budget. A reader error surfaces here as it would inline.
    loc_box: dict = {}

    def _loc():
        try:
            loc_box["v"] = _locate(pr, here, e, git)
        except BaseException as exc:  # noqa: BLE001
            loc_box["e"] = exc

    th = threading.Thread(target=_loc, daemon=True)
    th.start()
    det = pr.detect_surface(env=e, ancestry=ancestry, root=root)
    th.join()
    if "e" in loc_box:
        raise loc_box["e"]
    walls = str(det.get("family_for_walls") or "unknown")
    base = _allow(family=walls)
    # 1. A Claude chain gets the Claude floor's own decision first: the lane is never weaker than it.
    if walls == "claude":
        v = pr.floor_decide(event, args, lines, env=e, ancestry=ancestry, root=root, home=home, cwd=here, git=git)
        if v.get("decision") == "block":
            return _block(base, str(v.get("rule") or "I2"), str(v.get("reason") or ""), "claude-floor")
        if v.get("notice"):
            base["notices"].append(f"claude floor: {v['notice']}")
    # 2. The repo profile picks the lane.
    facts = _classify(pr, here, e, det, args, event, root, home, git, loc_box.get("v"))
    if facts["gitdir"] is None and facts["top"] is None:
        base["notices"].append("not inside a repository; allowing")
        return base
    base["repo_class"] = facts["owner_class"]
    if facts["employer"]:
        base["lane"] = "employer"
        out = _employer_lane(pr, base, facts, event, args, lines, here, e, root, git)
        if out["decision"] == "block":
            return out
        out["notices"] += _r2_notices(pr, facts, event, lines, walls, e, git)
        return out
    top = facts["top"]
    if facts["role"] == "workspace":
        base["lane"] = "workspace"
    elif facts["positively_personal"]:
        base["lane"] = "personal"
    else:
        base["lane"] = "unknown"
        fams = (pr._surfaces_or_fallback(root).get("families") or {})
        if walls != "claude" and (fams.get(walls) or {}).get("agent") and event in ("pre-commit", "pre-push"):
            base["notices"].append(f"WARN: this repo's owner is not declared personal ({facts['owner_class']}); "
                                   "an agent works here only with Sean's say-so (run profile_resolve.py scan in "
                                   "a plain terminal, or declare the owner in context-remotes.json)")
    if event == "pre-push" and top is not None and base["lane"] == "workspace" and gate:
        return gate_push(base, top, lines, e, det, ancestry=ancestry, root=root, git=git, runner=gate_runner)
    if event == "pre-commit" and top is not None:
        try:
            idn = pr.identity(repo=str(top), root=root, env=e, ancestry=ancestry, home=home, hostname=hostname,
                              detection=det, git=git)
            if idn.get("flag"):
                base["notices"].append(f"flag: {idn['flag']}")
        except Exception as exc:  # noqa: BLE001 - a flag is advisory; never block on its failure
            base["notices"].append(f"identity flag unavailable ({exc.__class__.__name__})")
        if base["lane"] == "workspace" and heal:
            base = _emp_lane(base, top, e)
            if base.get("decision") == "block":
                return base
            return _heal_lane(base, top, e)
    return base


def _lane_token(v: Any) -> str:
    t = re.sub(r"[^A-Za-z0-9._-]+", "-", str(v or "").strip()).strip("-")
    return t or "unknown"


def trailer_decide(hook_args: Optional[list] = None, *, env: Optional[dict] = None, ancestry: Optional[list] = None,
                   root: Optional[Path] = None, home: Optional[Path] = None, cwd: Optional[Any] = None,
                   git: str = "git") -> dict:
    """{write, value, reason, lane}. Workspace: always; positively personal + opted in: yes; else no."""
    pr = _pr()
    e = dict(os.environ if env is None else env)
    here = pr._real(cwd if cwd is not None else os.getcwd())
    det = pr.detect_surface(env=e, ancestry=ancestry, root=root)
    facts = _classify(pr, here, e, det, [], TRAILER_EVENT, root, home, git)
    top = facts.get("top")
    no = {"write": False, "value": None, "lane": None}
    if top is None:
        return dict(no, reason="not inside a work tree")
    if facts["employer"]:
        return dict(no, lane="employer", reason="employer repo: never a trailer")
    if facts["role"] == "workspace":
        lane = "workspace"
    elif facts["positively_personal"]:
        try:
            r = subprocess.run([git, "-C", str(top), "config", "--bool", "--get", TRAILER_OPTIN], capture_output=True,
                               text=True, timeout=GIT_TIMEOUT_S, env=_clean_env(e))
            opted = r.stdout.strip() == "true"
        except (OSError, subprocess.SubprocessError):
            opted = False
        if not opted:
            return dict(no, lane="personal", reason=f"personal repo without {TRAILER_OPTIN}=true")
        lane = "personal"
    else:
        return dict(no, lane="unknown", reason="owner not declared personal")
    try:
        device = pr.current_device(root=root).get("id") or "unknown"
    except Exception:  # noqa: BLE001
        device = "unknown"
    value = "/".join(_lane_token(x) for x in (det.get("acting_host"), det.get("family_for_walls"), device))
    return {"write": True, "value": value, "lane": lane, "reason": "", "top": str(top)}


def run_trailer(hook_args: List[str], *, err=None, decide=None, budget: float = TRAILER_BUDGET_S,
                git: str = "git") -> int:
    """The prepare-commit-msg path: always exit 0. Writes the trailer only when trailer_decide says so."""
    err = err or sys.stderr
    if not hook_args:
        return 0
    msg = Path(hook_args[0])
    box: dict = {}

    def work():
        try:
            box["v"] = (decide or trailer_decide)(hook_args[1:])
        except BaseException as exc:  # noqa: BLE001
            box["e"] = exc

    th = threading.Thread(target=work, daemon=True)
    th.start()
    th.join(budget)
    v = box.get("v") if isinstance(box.get("v"), dict) else None
    if th.is_alive() or "e" in box or not v or not v.get("write"):
        return 0
    try:
        subprocess.run([git, "interpret-trailers", "--in-place", "--if-exists", "replace", "--trailer",
                        f"{TRAILER_KEY}: {v['value']}", str(msg)], capture_output=True, text=True,
                       timeout=GIT_TIMEOUT_S, env=_clean_env())
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"{TAG}: trailer not written ({exc.__class__.__name__})", file=err)
    return 0


def run_hook(event: str, hook_args: List[str], stdin_lines: List[str], *, budget: float = LANE_BUDGET_S,
             err=None, decide=None) -> int:
    """The hook path: 1 on a block, 0 otherwise (an exception or a timeout allows with a notice)."""
    err = err or sys.stderr
    fn = decide or lane_decide
    box: dict = {}

    def work():
        try:
            box["v"] = fn(event, hook_args, stdin_lines)
        except BaseException as exc:  # noqa: BLE001
            box["e"] = exc

    th = threading.Thread(target=work, daemon=True)
    th.start()
    th.join(budget)
    if th.is_alive():
        print(f"{TAG}: lane timed out after {budget:g}s; allowing", file=err)
        return 0
    if "e" in box:
        print(f"{TAG}: lane error ({type(box['e']).__name__}); allowing", file=err)
        return 0
    v = box.get("v") if isinstance(box.get("v"), dict) else {}
    for n in v.get("notices") or []:
        print(f"{TAG}: {n}", file=err)
    if v.get("decision") == "block":
        print(f"{TAG}: blocked [{v.get('rule') or 'unknown'}] {v.get('reason') or ''}".rstrip(), file=err)
        return 1
    return 0


# --------------------------------------------------------------------------- audit (doctor --check)


def _clean_env(env: Optional[dict] = None) -> dict:
    e = dict(os.environ if env is None else env)
    for k in list(e):
        if k.startswith("GIT_CONFIG_") or k in ("GIT_CONFIG_PARAMETERS", "GIT_CONFIG", "GIT_DIR", "GIT_WORK_TREE",
                                                  "GIT_INDEX_FILE", "GIT_COMMON_DIR", "GIT_CEILING_DIRECTORIES"):
            e.pop(k, None)
    e["GIT_TERMINAL_PROMPT"] = "0"
    return e


def parse_listing(raw: bytes) -> List[dict]:
    """`git config --show-scope --show-origin -z --get-regexp` output → [{scope, origin, key, value}]."""
    parts = raw.decode("utf-8", "replace").split("\0")
    out = []
    i = 0
    while i + 2 < len(parts):
        scope, origin, kv = parts[i], parts[i + 1], parts[i + 2]
        i += 3
        key, nl, value = kv.partition("\n")
        out.append({"scope": scope, "origin": origin, "key": key, "value": value if nl else None})
    return out


def _bool(v: Optional[str]) -> bool:
    return v is None or str(v).strip().lower() in ("true", "yes", "on", "1")


def effective(entries: List[dict]) -> Dict[str, dict]:
    """Per lane name, what git will use: last command, last enabled, the event list with empty resets;
    `last` records where each of those was last set."""
    out: Dict[str, dict] = {}
    for ent in entries:
        m = re.fullmatch(r"hook\.(.+)\.(command|event|enabled)", ent["key"], flags=re.I)
        if not m:
            continue
        name, field = m.group(1), m.group(2).lower()
        cur = out.setdefault(name, {"command": None, "events": [], "enabled": True, "last": {}, "entries": []})
        cur["entries"].append(ent)
        if field == "command":
            cur["command"] = ent["value"]
        elif field == "enabled":
            cur["enabled"] = _bool(ent["value"])
        elif not (ent["value"] or "").strip():
            cur["events"] = []
        else:
            cur["events"].append(ent["value"].strip())
        cur["last"][field] = f"{ent['scope']} {ent['origin']}"
    return out


def _origin_path(origin: str, cwd: Optional[Path]) -> Optional[Path]:
    if not origin.startswith("file:"):
        return None
    p = Path(origin[len("file:"):])
    if not p.is_absolute() and cwd is not None:
        p = cwd / p
    return p


def _inside_repo(path: Path) -> Optional[Path]:
    cur = path.parent
    for _ in range(64):
        try:
            if (cur / ".git").exists():
                return cur
        except OSError:
            return None
        if cur.parent == cur:
            return None
        cur = cur.parent
    return None


def _cf(p: Any) -> str:
    return os.path.realpath(str(p)).casefold()


def findings_for(entries: List[dict], *, home: Path, where: str, cwd: Optional[Path] = None) -> List[str]:
    """Every way the effective lane config differs from the rendered lanes, with where it was set."""
    want = expected_lanes()
    inc = home / INSTALL_INCLUDE_REL
    eff = effective([x for x in entries if x["key"].lower().startswith("hook." + LANE_PREFIX)])
    out: List[str] = []
    for name, exp in want.items():
        got = eff.get(name)
        if got is None or got["command"] is None:
            out.append(f"{where}: lane {name} missing (no command in any scope)")
            continue
        if got["command"] != exp["command"]:
            out.append(f"{where}: lane {name} command replaced (last set at {got['last'].get('command')})")
        if exp["events"][0] not in got["events"]:
            out.append(f"{where}: lane {name} event cleared or missing (last event entry at "
                       f"{got['last'].get('event', 'nowhere')})")
        extra = [ev for ev in got["events"] if ev not in exp["events"]]
        if extra:
            out.append(f"{where}: lane {name} runs on extra events {extra} (last at {got['last'].get('event')})")
        if not got["enabled"]:
            out.append(f"{where}: lane {name} disabled (enabled=false at {got['last'].get('enabled')})")
        for ent in got["entries"]:
            p = _origin_path(ent["origin"], cwd)
            if p is None or _cf(p) != _cf(inc):
                out.append(f"{where}: {ent['key']} set outside the lane include ({ent['scope']} {ent['origin']})")
            elif _inside_repo(p) is not None:
                out.append(f"{where}: the lane include {p} lies inside a git repository")
    for name in sorted(set(eff) - set(want)):
        out.append(f"{where}: unexpected hook {name} uses the reserved {LANE_PREFIX} prefix "
                   f"({eff[name]['last'].get('command') or eff[name]['last']})")
    gc = _cf(home / ".gitconfig")
    for ent in entries:
        if ent["key"].lower() != PUSHGATE_KEY:
            continue
        p = _origin_path(ent["origin"], cwd)
        if ent["scope"] != "global" or p is None or _cf(p) != gc:
            out.append(f"{where}: {PUSHGATE_KEY} set outside the installer's ~/.gitconfig block ({ent['scope']} "
                       f"{ent['origin']}); the gate ignores it — remove it (workspace-doctor.sh "
                       "--install-git-hooks=block sets the hold)")
    return list(dict.fromkeys(out))


def _listing(cwd: Path, env: dict, git: str) -> Optional[List[dict]]:
    try:
        r = subprocess.run([git, "config", "--show-scope", "--show-origin", "-z", "--get-regexp",
                            r"^hook\.|^ws\.pushgate$"], cwd=str(cwd), env=env, capture_output=True,
                           timeout=GIT_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode not in (0, 1):
        return None
    return parse_listing(r.stdout)


def _hook_list(cwd: Path, env: dict, git: str, event: str) -> Optional[str]:
    try:
        r = subprocess.run([git, "hook", "list", "--show-scope", event], cwd=str(cwd), env=env,
                           capture_output=True, text=True, timeout=GIT_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode in (0, 1) else None


def _cache_repos(home: Path) -> List[dict]:
    try:
        obj = json.loads((home / ".config" / "snds-workspace" / "telemetry" / "checkouts.json").read_text("utf-8"))
    except (OSError, ValueError):
        return []
    return [c for c in obj.get("checkouts") or [] if isinstance(c, dict) and isinstance(c.get("path"), str)]


def audit(*, repos: Optional[List[str]] = None, use_cache: bool = False, home: Optional[Path] = None,
          env: Optional[dict] = None, git: str = "git", ancestry: Optional[list] = None,
          dist: Optional[Path] = None) -> dict:
    """The doctor --check audit: {status: clean|findings|absent|error, installed, findings[], notices[],
    repos_checked, repos_skipped}. Reads config only; never writes."""
    home = Path(home) if home is not None else Path.home()
    e = _clean_env(env)
    e["HOME"] = str(home)
    notices: List[str] = []
    findings: List[str] = []
    src = dict(os.environ if env is None else env)
    for k in ("GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM"):
        if src.get(k):
            notices.append(f"{k} is set in this environment: a git run with it would not read the global lanes")
    inc = home / INSTALL_INCLUDE_REL
    dist = dist or (ROOT / DIST_INCLUDE_REL)
    installed = inc.is_file()
    if installed:
        try:
            if dist.is_file() and inc.read_bytes() != dist.read_bytes():
                findings.append(f"{inc} differs from {DIST_INCLUDE_REL} — review, then run workspace-doctor.sh "
                                "--install-git-hooks")
        except OSError:
            findings.append(f"{inc} unreadable")
        if _inside_repo(inc) is not None:
            findings.append(f"{inc} lies inside a git repository (the lanes must not live in a repo)")
        if not os.access(home / WS_HOOK_REL, os.X_OK):
            findings.append(f"~/{WS_HOOK_REL} missing or not executable: every lane allows (run workspace-doctor.sh "
                            "--install-pin)")
    with tempfile.TemporaryDirectory(prefix="ws-lanes-audit-") as td:
        neutral = Path(td)
        ents = _listing(neutral, e, git)
        if ents is None:
            return {"status": "error", "installed": installed, "findings": findings,
                    "notices": notices + ["git config unreadable"], "repos_checked": 0, "repos_skipped": 0}
        lane_ents = [x for x in ents if x["key"].lower().startswith("hook." + LANE_PREFIX)]
        if not installed and not lane_ents:
            return {"status": "absent", "installed": False, "findings": findings, "notices": notices,
                    "repos_checked": 0, "repos_skipped": 0}
        findings += findings_for(ents, home=home, where="global")
        for name, ev in LANES:
            out = _hook_list(neutral, e, git, ev)
            if out is None:
                notices.append(f"git hook list {ev} unavailable (git < 2.54?)")
            elif not any(ln.split("\t")[-1] == name and "disabled" not in ln.split("\t") for ln in out.splitlines()):
                findings.append(f"global: git hook list {ev} does not show {name} enabled")
    targets: List[Tuple[str, Optional[str]]] = [(r, None) for r in repos or []]
    if use_cache:
        targets += [(c["path"], c.get("owner_class")) for c in _cache_repos(home)]
    checked = skipped = 0
    claude = False
    try:
        det = _pr().detect_surface(env=src, ancestry=ancestry)
        claude = det.get("family_for_walls") == "claude" or bool(det.get("agent_possible"))
    except Exception:  # noqa: BLE001 - undetermined: treat as Claude (never open a non-personal repo)
        claude = True
    seen = set()
    for path, oc in targets:
        p = Path(path)
        if _cf(p) in seen or not p.exists():
            continue
        seen.add(_cf(p))
        if claude:
            try:
                personal = oc == "personal" if oc is not None else bool(
                    _pr().repo_resolve(str(p), home=home, detection=det).get("positively_personal"))
            except Exception:  # noqa: BLE001
                personal = False
            if not personal:
                skipped += 1
                continue
        ents = _listing(p, e, git)
        if ents is None:
            notices.append(f"{p}: git config unreadable")
            continue
        checked += 1
        findings += findings_for(ents, home=home, where=str(p), cwd=p)
    if skipped:
        notices.append(f"{skipped} non-personal repo(s) not audited from an agent chain (run the doctor in a "
                       "plain terminal)")
    findings = list(dict.fromkeys(findings))
    return {"status": "findings" if findings else "clean", "installed": installed, "findings": findings,
            "notices": notices, "repos_checked": checked, "repos_skipped": skipped}


# --------------------------------------------------------------------------- CLI


def _read_lines() -> List[str]:
    try:
        if sys.stdin is None or sys.stdin.isatty():
            return []
        return [ln.rstrip("\n") for ln in sys.stdin.read().splitlines() if ln.strip()]
    except (OSError, ValueError):
        return []


def cmd_render(check: bool) -> int:
    path = ROOT / DIST_INCLUDE_REL
    want = render_include()
    have = path.read_text(encoding="utf-8") if path.is_file() else None
    if check:
        if have != want:
            print(f"git_lanes: {DIST_INCLUDE_REL} is stale; run python3 09-tools/git_lanes.py render", file=sys.stderr)
            return 1
        return 0
    if have != want:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(want, encoding="utf-8")
        print(f"wrote {DIST_INCLUDE_REL}")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["--self-test"]:
        return self_test()
    if argv[:1] == ["hook"]:
        # Hook path: never a usage error that blocks. git appends the hook's own args after the event.
        if len(argv) < 2:
            return 0
        event, hook_args = argv[1], argv[2:]
        if event in (TRAILER_EVENT, GATE_EVENT):
            try:
                return run_trailer(hook_args) if event == TRAILER_EVENT else run_post_commit()
            except BaseException as exc:  # noqa: BLE001
                if isinstance(exc, KeyboardInterrupt):
                    raise
                return 0
        # pre-commit may run the workspace's H25 scan and H1 lane, pre-push the H11 gate (their own
        # timeouts); every other event gets the lane budget.
        budget = LANE_BUDGET_S + (EMP_TIMEOUT_S + HEAL_TIMEOUT_S if event == "pre-commit" else 0) + (
            GATE_BUDGET_S + 20 if event == "pre-push" else 0)
        try:
            return run_hook(event, hook_args, _read_lines() if event == "pre-push" else [], budget=budget)
        except BaseException as exc:  # noqa: BLE001
            if isinstance(exc, KeyboardInterrupt):
                raise
            print(f"{TAG}: {exc.__class__.__name__} in the lane; allowing", file=sys.stderr)
            return 0
    if argv[:1] == ["gate-verify"]:
        # The detached post-commit verify: never raises, always 0.
        try:
            gp = argparse.ArgumentParser(prog="git_lanes.py gate-verify")
            for k in ("--top", "--tree", "--head", "--range"):
                gp.add_argument(k, required=True)
            gp.add_argument("--via", default="post-commit")
            gp.add_argument("--budget", type=float, default=GATE_POST_BUDGET_S)
            ns = gp.parse_args(argv[1:])
            verify_tree(Path(ns.top), ns.tree, ns.head, ns.range, budget=ns.budget, via=ns.via, wait=False)
        except BaseException as exc:  # noqa: BLE001
            if isinstance(exc, KeyboardInterrupt):
                raise
        return 0
    if argv[:1] == ["gate-notice"]:
        top = Path(argv[argv.index("--top") + 1]) if "--top" in argv[:-1] else ROOT
        try:
            line = gate_notice(top)
        except Exception:  # noqa: BLE001 - a notice is best effort
            line = None
        if line:
            print(line)
        return 0
    ap = argparse.ArgumentParser(prog="git_lanes.py")
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("render")
    r.add_argument("--check", action="store_true")
    a = sub.add_parser("audit")
    a.add_argument("--repo", action="append", default=[])
    a.add_argument("--cache", action="store_true")
    a.add_argument("--home")
    a.add_argument("--json", action="store_true")
    ns = ap.parse_args(argv)
    if ns.cmd == "render":
        return cmd_render(ns.check)
    if ns.cmd == "audit":
        res = audit(repos=ns.repo, use_cache=ns.cache, home=Path(ns.home) if ns.home else None)
        if ns.json:
            print(json.dumps(res, indent=2))
        else:
            for f in res["findings"]:
                print(f"FINDING: {f}")
            for n in res["notices"]:
                print(f"NOTE: {n}")
            print(f"git lanes: {res['status']} (repos checked {res['repos_checked']}, skipped {res['repos_skipped']})")
        return {"clean": 0, "findings": 1, "absent": 3}.get(res["status"], 2)
    ap.print_help(sys.stderr)
    return 2


# --------------------------------------------------------------------------- self-test


def self_test() -> int:
    """Unit cases here; the temp-HOME git fixtures live in fixtures/git_lanes/lane_cases.py
    (0 pass · 1 fail · 3 a case SKIPPED, never green)."""
    fails: List[str] = []
    skips: List[str] = []
    n = [0]

    def ok(cond: Any, label: str) -> None:
        n[0] += 1
        if not cond:
            fails.append(label)
            print(f"FAIL {label}", file=sys.stderr)

    inc = render_include()
    ok(inc.count("[hook \"ws-lane-") == len(LANES), "render: one hook section per lane event")
    ok("\"$@\"" not in inc, "render: no \"$@\" (git appends the hook args itself)")
    ok(cmd_render(True) == 0, f"render --check: {DIST_INCLUDE_REL} is current")
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "x.inc"
        f.write_text(inc, encoding="utf-8")
        e = _clean_env({"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": td, "GIT_CONFIG_NOSYSTEM": "1"})
        try:
            r = subprocess.run(["git", "config", "--file", str(f), "--show-scope", "--show-origin", "-z",
                                "--get-regexp", r"^hook\."], env=e, capture_output=True, timeout=GIT_TIMEOUT_S)
            ents = parse_listing(r.stdout)
            eff = effective(ents)
            ok(all(eff.get(nm, {}).get("command") == lane_command(ev) for nm, ev in LANES),
               "render: git reads back every command byte-for-byte (';' and '\"' quoted)")
            ok(all(eff[nm]["events"] == [ev] and eff[nm]["enabled"] for nm, ev in LANES),
               "render: git reads back one event per lane, enabled")
        except (OSError, subprocess.SubprocessError) as exc:
            ok(False, f"git config readback ran ({exc})")
    home = Path("/h")
    good = [{"scope": "global", "origin": f"file:{home / INSTALL_INCLUDE_REL}", "key": f"hook.{nm}.{k}", "value": v}
            for nm, ev in LANES for k, v in (("command", lane_command(ev)), ("event", ev), ("enabled", "true"))]
    ok(findings_for(good, home=home, where="t") == [], "audit: the rendered include alone has no findings")
    loc = {"scope": "local", "origin": "file:.git/config"}
    for label, extra, needle in (
            ("repo-local last-one-wins command", {"key": "hook.ws-lane-pre-commit.command", "value": "true"},
             "command replaced"),
            ("repo-local empty event= entry", {"key": "hook.ws-lane-pre-push.event", "value": ""},
             "event cleared"),
            ("repo-local enabled=false", {"key": "hook.ws-lane-commit-msg.enabled", "value": "false"}, "disabled"),
            ("an extra event on a lane", {"key": "hook.ws-lane-pre-commit.event", "value": "pre-push"},
             "extra events"),
            ("a foreign hook under the reserved prefix", {"key": "hook.ws-lane-x.command", "value": "true"},
             "reserved"),
    ):
        got = findings_for(good + [dict(loc, **extra)], home=home, where="t")
        ok(any(needle in g for g in got), f"audit: {label} is a finding ({got})")
    ok(any("missing" in g for g in findings_for(good[3:], home=home, where="t")), "audit: a missing lane is a finding")
    ok(_bool(None) and _bool("yes") and not _bool("false"), "audit: git boolean parsing")
    ok(parse_listing(b"global\0file:/x\0hook.a.event\n\0local\0file:.git/config\0hook.a.enabled\0") ==
       [{"scope": "global", "origin": "file:/x", "key": "hook.a.event", "value": ""},
        {"scope": "local", "origin": "file:.git/config", "key": "hook.a.enabled", "value": None}],
       "audit: -z listing parse (empty value vs no value)")
    # run_hook mapping: block → 1 with the rule; exception / timeout → 0 with a notice.
    import io
    for label, fn, want, needle in (
            ("block exits 1 with the rule", lambda *_a: {"decision": "block", "rule": "I1", "reason": "x",
                                                        "notices": []}, 1, "[I1]"),
            ("allow exits 0", lambda *_a: {"decision": "allow", "notices": ["n"]}, 0, "n"),
            ("an exception allows with a notice", lambda *_a: 1 / 0, 0, "lane error"),
    ):
        err = io.StringIO()
        rc = run_hook("pre-commit", [], [], err=err, decide=fn)
        ok(rc == want and needle in err.getvalue(), f"run_hook: {label} (rc={rc} {err.getvalue()!r})")
    err = io.StringIO()
    rc = run_hook("pre-commit", [], [], err=err, decide=lambda *_a: __import__("time").sleep(2), budget=0.2)
    ok(rc == 0 and "timed out" in err.getvalue(), "run_hook: a timeout allows with a notice")
    # H10 trailer lane: always exit 0; writes only on write=True; an error or a timeout writes nothing.
    with tempfile.TemporaryDirectory() as td:
        m = Path(td) / "MSG"
        for label, fn, want in (
                ("write adds the trailer", lambda _a: {"write": True, "value": "cursor/cursor/dev-a"},
                 f"{TRAILER_KEY}: cursor/cursor/dev-a"),
                ("write=False leaves the message", lambda _a: {"write": False}, None),
                ("an exception writes nothing", lambda _a: 1 / 0, None),
                ("a timeout writes nothing", lambda _a: __import__("time").sleep(2), None)):
            m.write_text("subject\n", encoding="utf-8")
            rc = run_trailer([str(m), "message"], err=io.StringIO(), decide=fn, budget=0.3)
            body = m.read_text(encoding="utf-8")
            ok(rc == 0 and ((want in body) if want else body == "subject\n"), f"run_trailer: {label} ({body!r})")
        m.write_text(f"subject\n\n{TRAILER_KEY}: old/old/old\n", encoding="utf-8")
        run_trailer([str(m)], err=io.StringIO(), decide=lambda _a: {"write": True, "value": "codex/codex/dev-b"})
        body = m.read_text(encoding="utf-8")
        ok(body.count(TRAILER_KEY) == 1 and "codex/codex/dev-b" in body, f"run_trailer: replaces, never stacks ({body!r})")
    ok(_lane_token("a b/c") == "a-b-c" and _lane_token(None) == "unknown", "trailer value tokens are sanitised")
    # H11 gate: the suffix is the tree and its verdict only; detector order never changes it.
    t = "0123456789abcdef" * 2
    ok(gate_suffix(t, "red", ["b.py", "a b.py", "b.py"]) == "[gate:red:a-b.py,b.py@0123456789ab]",
       "gate suffix: red with sorted, sanitised, deduped detectors")
    ok(gate_suffix(t, "green", ["x"]) == "[gate:green@0123456789ab]" and gate_suffix(None, "off") ==
       "[gate:off@unknown]", "gate suffix: green ignores detectors; no tree is 'unknown'")
    ok("lane post-commit" in inc and all(f"lane {ev}" in inc for _n, ev in LANES) and inc.count("bin/ws-hook") ==
       len(LANES), "render: every lane enters through bin/ws-hook lane EVENT")
    rec = {"tree": "T1", "gate": {"status": "skipped"}, "ring": [{"tree": "T1", "status": "red", "detectors": ["d"]},
                                                                {"tree": "T2", "status": "green"}]}
    ok((gate_for_tree(rec, "T1") or {}).get("status") == "red" and (gate_for_tree(rec, "T2") or {}).get("status") ==
       "green" and gate_for_tree(rec, "T3") is None and gate_for_tree(rec, None) is None,
       "gate record: a skipped current entry falls back to the ring's verdict for the same tree")
    helper = TOOLS / "fixtures" / "git_lanes" / "lane_cases.py"
    if not helper.is_file():
        print("self-test SKIP: git-lane fixtures absent (a pinned copy) — not a pass", file=sys.stderr)
        skips.append("fixtures absent")
    else:
        spec = importlib.util.spec_from_file_location("ws_lane_cases", helper)
        mod = importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)
        for name, passed, detail in mod.run_all():
            if passed is None:
                print(f"self-test SKIP: {name} ({detail}) — not a pass", file=sys.stderr)
                skips.append(name)
                continue
            ok(passed, f"{name}: {detail}")
        for line in getattr(mod, "REPORT", []):
            print(f"git_lanes self-test info: {line}")
    print(f"git_lanes self-test: {n[0] - len(fails)}/{n[0]} passed, {len(skips)} skipped")
    if fails:
        return 1
    return 3 if skips else 0


if __name__ == "__main__":
    sys.exit(main())
