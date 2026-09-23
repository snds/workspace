#!/usr/bin/env python3
"""Prune merged branches we created. Safe for /session-end hygiene.

Deletes a local (and still-present remote) branch only when ALL of:
  - `gh pr` shows a MERGED pull request for that head, authored by `@me`
  - no OPEN pull request uses that head
  - the branch is not the default branch, `main` or `master`
  - local is not ahead of `origin/<branch>` (no unpushed unique commits)
  - a linked worktree is clean, or the primary checkout can switch to the default branch and
    fast-forward it (a diverged default branch is reported and never reset)

Squash-merged branches are not ancestors of main — do not use merge-base as
the keep/delete signal. Unmerged work, someone else's PRs, and dirty leftover
worktrees are left alone.

Vetted script (DECISIONS-2 item 9, registered in 02-shared-references/vetted-scripts.json).
Every remote action and deletion runs through `vetted_context().run()`: an intent line, the
lifted env (the Claude transport block dropped, nothing else), and one receipt per action in
~/.config/snds-workspace/control/receipts.jsonl. `vetted_context` is imported from the PINNED
lib; without it the vault module runs with status `unpinned`. Under a Claude chain, a repo that
is not positively personal is skipped (zero git or gh calls in it) unless the pinned blob of
this file matches (`vetted`).

Targets: this workspace plus DEFAULT_SLUGS resolved per device through `profile_resolve where`
(not on this device = a skip with a notice), or the `--repo` paths given.

Usage:
  python3 09-tools/prune-our-branches.py              # dry-run default targets
  python3 09-tools/prune-our-branches.py --apply
  python3 09-tools/prune-our-branches.py --apply --repo /path/to/checkout
  python3 09-tools/prune-our-branches.py --self-test
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
SCRIPT_ID = "prune-our-branches"
PROTECTED = frozenset({"main", "master", "HEAD"})
# D10: the two slugs this script has always named (no new slug); resolved per device via `where`.
DEFAULT_SLUGS = (
    "cpes-software/cds",
    "cpes-software/saas-plm-prototype",
)
LOCAL_TIMEOUT_S = 30.0
NETWORK_TIMEOUT_S = 120.0


# --------------------------------------------------------------------------- resolver loading


def _vault_resolver() -> Any:
    try:
        tools = str(ROOT / "09-tools")
        if tools not in sys.path:
            sys.path.insert(0, tools)
        import profile_resolve  # noqa: PLC0415 - lazy by contract

        return profile_resolve
    except (ImportError, OSError, ValueError):
        return None


_PINNED_API = ("vetted_context", "vetted_status", "where", "repo_resolve", "detect_surface")


def _pinned_resolver(home: Optional[Path] = None) -> Any:
    """profile_resolve from $HOME/.config/snds-workspace/lib/current, or None (then: unpinned)."""
    lib = (Path(home) if home is not None else Path.home()) / ".config" / "snds-workspace" / "lib" / "current"
    path = lib / "09-tools" / "profile_resolve.py"
    if not path.is_file():
        return None
    try:
        spec = importlib.util.spec_from_file_location("ws_pinned_profile_resolve", path)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        sys.modules["ws_pinned_profile_resolve"] = mod
        spec.loader.exec_module(mod)
    except Exception:  # noqa: BLE001 - a broken pin is an unpinned pin
        return None
    return mod if all(hasattr(mod, n) for n in _PINNED_API) else None


# --------------------------------------------------------------------------- decisions


@dataclass(frozen=True)
class BranchDecision:
    name: str
    action: str  # prune | keep
    reason: str


def decide(
    name: str,
    *,
    merged_ours: set[str],
    open_heads: set[str],
    ahead_of_remote: bool,
    protected: frozenset[str] = PROTECTED,
) -> BranchDecision:
    if name in protected:
        return BranchDecision(name, "keep", "protected")
    if name in open_heads:
        return BranchDecision(name, "keep", "open PR")
    if name not in merged_ours:
        return BranchDecision(name, "keep", "not a merged PR by us")
    if ahead_of_remote:
        return BranchDecision(name, "keep", "unpushed unique commits")
    return BranchDecision(name, "prune", "merged PR by us")


# --------------------------------------------------------------------------- repo queries (via ctx)


class _PlainCtx:
    """Fallback when no resolver imports: the workspace checkout only, no policy, no receipts."""

    def __init__(self, repo: Path, env: Optional[dict], runner: Optional[Callable[..., Any]]) -> None:
        self.path = str(repo)
        self._env = env
        self._runner = runner

    def _exec(self, argv: List[str], timeout: float) -> subprocess.CompletedProcess:
        env = dict(os.environ if self._env is None else self._env)
        if self._runner is not None:
            return self._runner(list(argv), cwd=self.path, env=env, timeout=timeout)
        try:
            return subprocess.run(list(argv), cwd=self.path, env=env, capture_output=True, text=True, timeout=timeout)
        except (OSError, subprocess.SubprocessError) as exc:
            return subprocess.CompletedProcess(list(argv), 125, "", exc.__class__.__name__)

    def query(self, argv: List[str], timeout: float = LOCAL_TIMEOUT_S) -> subprocess.CompletedProcess:
        return self._exec(argv, timeout)

    def run(self, argv: List[str], action: str, refs: Any = (), needs_employer_gh: bool = False,
            timeout: float = NETWORK_TIMEOUT_S) -> subprocess.CompletedProcess:
        return self._exec(argv, timeout)


def _err(proc: subprocess.CompletedProcess, fallback: str) -> str:
    return (proc.stderr or "").strip().splitlines()[-1:][0] if (proc.stderr or "").strip() else fallback


def gh_json(ctx: Any, args: list[str], employer_gh: bool) -> list[dict]:
    proc = ctx.run(["gh", "pr", "list", *args, "--json", "number,headRefName,state"], action="pr-list",
                   needs_employer_gh=employer_gh)
    if proc.returncode != 0:
        raise RuntimeError(_err(proc, "gh pr list failed"))
    data = json.loads(proc.stdout or "[]")
    if not isinstance(data, list):
        raise RuntimeError("gh pr list returned a non-list")
    return data


def local_branches(ctx: Any) -> list[str]:
    proc = ctx.query(["git", "for-each-ref", "--format=%(refname:short)", "refs/heads"])
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def current_branch(ctx: Any) -> str:
    return ctx.query(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()


def default_branch(ctx: Any) -> str:
    q = ctx.query(["git", "symbolic-ref", "--short", "refs/remotes/origin/HEAD"])
    if q.returncode == 0 and q.stdout.strip().startswith("origin/"):
        return q.stdout.strip()[len("origin/"):]
    for name in ("main", "master"):
        if ctx.query(["git", "show-ref", "--verify", "--quiet", f"refs/remotes/origin/{name}"]).returncode == 0:
            return name
    return "main"


def ahead_of_remote(ctx: Any, name: str) -> bool:
    remote = f"origin/{name}"
    exists = ctx.query(["git", "show-ref", "--verify", "--quiet", f"refs/remotes/{remote}"])
    if exists.returncode != 0:
        return False
    counts = ctx.query(["git", "rev-list", "--left-right", "--count", f"{remote}...{name}"]).stdout.strip()
    try:
        _behind, ahead = (int(part) for part in counts.split())
    except ValueError:
        return True
    return ahead > 0


def worktree_map(ctx: Any) -> dict[str, Path]:
    """branch name → worktree path (skips detached)."""
    mapping: dict[str, Path] = {}
    proc = ctx.query(["git", "worktree", "list", "--porcelain"])
    path: Path | None = None
    for line in proc.stdout.splitlines():
        if line.startswith("worktree "):
            path = Path(line[len("worktree "):])
        elif line.startswith("branch refs/heads/") and path is not None:
            mapping[line.split("refs/heads/", 1)[1]] = path
            path = None
        elif line == "":
            path = None
    return mapping


def worktree_dirty(ctx: Any, path: Path) -> bool:
    # Tracked changes only — node_modules and gitignored vendor do not block.
    proc = ctx.query(["git", "-C", str(path), "status", "--porcelain", "--untracked-files=no"])
    return proc.returncode != 0 or bool(proc.stdout.strip())


def remote_branch_exists(ctx: Any, name: str) -> bool:
    return ctx.query(["git", "show-ref", "--verify", "--quiet", f"refs/remotes/origin/{name}"]).returncode == 0


def switch_to_default(ctx: Any, default: str, employer_gh: bool) -> str | None:
    """`git switch <default>` then `git merge --ff-only origin/<default>`. Never resets."""
    ref = [f"refs/heads/{default}"]
    fetch = ctx.run(["git", "fetch", "origin", default], action="fetch", refs=ref, needs_employer_gh=employer_gh)
    if fetch.returncode != 0:
        return _err(fetch, f"fetch origin {default} failed")
    switched = ctx.run(["git", "switch", default], action="switch-default", refs=ref, timeout=LOCAL_TIMEOUT_S)
    if switched.returncode != 0:
        return _err(switched, f"switch to {default} failed")
    ff = ctx.run(["git", "merge", "--ff-only", f"origin/{default}"], action="ff-default", refs=ref,
                 timeout=LOCAL_TIMEOUT_S)
    if ff.returncode != 0:
        return f"{default} cannot fast-forward to origin/{default} (diverged; left as is, never reset)"
    return None


def prune_repo(ctx: Any, *, apply: bool, employer_gh: bool = False, label: str = "") -> list[str]:
    lines: list[str] = [f"## {label or ctx.path}"]
    fetch = ctx.run(["git", "fetch", "--prune", "origin"], action="fetch", needs_employer_gh=employer_gh)
    if fetch.returncode != 0:
        lines.append(f"  skip: fetch failed ({_err(fetch, 'unknown')})")
        return lines

    try:
        merged = {row["headRefName"] for row in
                  gh_json(ctx, ["--state", "merged", "--author", "@me", "--limit", "200"], employer_gh)}
        opened = {row["headRefName"] for row in gh_json(ctx, ["--state", "open", "--limit", "100"], employer_gh)}
    except (RuntimeError, ValueError, KeyError, TypeError) as exc:
        lines.append(f"  skip: {exc}")
        return lines

    default = default_branch(ctx)
    protected = frozenset(PROTECTED | {default})
    trees = worktree_map(ctx)
    current = current_branch(ctx)
    here = Path(ctx.path).resolve()

    for name in local_branches(ctx):
        decision = decide(name, merged_ours=merged, open_heads=opened, ahead_of_remote=ahead_of_remote(ctx, name),
                          protected=protected)
        if decision.action == "keep":
            lines.append(f"  keep  {name} — {decision.reason}")
            continue

        wt = trees.get(name)
        if wt is not None and worktree_dirty(ctx, wt):
            lines.append(f"  keep  {name} — dirty worktree {wt}")
            continue

        if not apply:
            extra = " + remote" if remote_branch_exists(ctx, name) else ""
            lines.append(f"  prune {name}{extra} (dry-run)")
            continue

        ref = [f"refs/heads/{name}"]
        if wt is not None:
            if wt.resolve() == here:
                err = switch_to_default(ctx, default, employer_gh)
                if err:
                    lines.append(f"  keep  {name} — cannot leave checkout: {err}")
                    continue
            else:
                removed = ctx.run(["git", "worktree", "remove", str(wt)], action="worktree-remove", refs=ref,
                                  timeout=LOCAL_TIMEOUT_S)
                if removed.returncode != 0:
                    lines.append(f"  keep  {name} — worktree remove failed: {_err(removed, 'unknown')}")
                    continue

        deleted = ctx.run(["git", "branch", "-D", name], action="branch-delete", refs=ref, timeout=LOCAL_TIMEOUT_S)
        if deleted.returncode != 0:
            lines.append(f"  keep  {name} — local delete failed: {_err(deleted, 'unknown')}")
            continue
        note = f"  pruned {name}"
        if remote_branch_exists(ctx, name):
            pushed = ctx.run(["git", "push", "origin", "--delete", name], action="remote-branch-delete", refs=ref,
                             needs_employer_gh=employer_gh)
            if pushed.returncode == 0:
                note += " + remote"
            else:
                note += f" (remote left: {_err(pushed, 'unknown')})"
        if current == name:
            note += f" (was HEAD; now {default})"
        lines.append(note)

    remaining_local = set(local_branches(ctx))
    for name in sorted(merged - remaining_local):
        if name in protected or name in opened:
            continue
        if not remote_branch_exists(ctx, name):
            continue
        if not apply:
            lines.append(f"  prune origin/{name} (dry-run, remote-only)")
            continue
        pushed = ctx.run(["git", "push", "origin", "--delete", name], action="remote-branch-delete",
                         refs=[f"refs/heads/{name}"], needs_employer_gh=employer_gh)
        if pushed.returncode == 0:
            lines.append(f"  pruned origin/{name} (remote-only)")
        else:
            lines.append(f"  keep  origin/{name} — {_err(pushed, 'unknown')}")
    return lines


# --------------------------------------------------------------------------- run


@dataclass
class Deps:
    """Test seams. Production uses the defaults (real HOME, live detection, pinned lib)."""

    home: Optional[Path] = None
    detection: Optional[dict] = None
    hostname: Optional[str] = None
    env: Optional[dict] = None
    runner: Optional[Callable[..., Any]] = None
    resolver: Any = "auto"
    pinned: Any = "auto"
    workspace: Path = ROOT
    slugs: Tuple[str, ...] = DEFAULT_SLUGS
    out: Callable[[str], None] = print
    script: Path = field(default_factory=lambda: Path(__file__).resolve())


def _claude_chain(det: dict) -> bool:
    return det.get("family_for_walls") == "claude" or bool(det.get("agent_possible"))


def run(repos: Optional[List[Path]], *, apply: bool, deps: Optional[Deps] = None) -> int:
    d = deps or Deps()
    pinned = _pinned_resolver(d.home) if d.pinned == "auto" else d.pinned
    mod = d.resolver if d.resolver != "auto" else (pinned or _vault_resolver())
    out = d.out
    out(f"prune-our-branches ({'apply' if apply else 'dry-run'})")
    det = d.detection
    if det is None and mod is not None:
        try:
            det = mod.detect_surface()
        except Exception:  # noqa: BLE001 - undetermined detection is treated as a Claude chain
            det = {"family_for_walls": "claude", "agent_possible": True}
    det = det or {"family_for_walls": "claude", "agent_possible": True}

    targets: List[Tuple[Path, str]] = []
    if repos:
        targets = [(Path(p).resolve(), str(Path(p).resolve())) for p in repos]
    else:
        targets.append((Path(d.workspace).resolve(), str(Path(d.workspace).resolve())))
        if mod is None:
            out("notice: profile_resolve unavailable — default slugs skipped")
        for slug in d.slugs if mod is not None else ():
            try:
                w = mod.where(slug, home=d.home, detection=det, hostname=d.hostname)
            except Exception as exc:  # noqa: BLE001
                out(f"## {slug}\n  skip: where failed ({exc.__class__.__name__})")
                continue
            if w.get("status") != "found":
                out(f"## {slug}\n  skip: not on this device ({w.get('status')})")
                continue
            for p in w.get("paths") or []:
                targets.append((Path(p), slug))

    for repo, label in targets:
        if not (repo / ".git").exists():
            out(f"## {label}\n  skip: not a git checkout")
            continue
        if mod is None:
            if repo != Path(d.workspace).resolve():
                out(f"## {label}\n  skip: profile_resolve unavailable (only the workspace runs without it)")
                continue
            out("\n".join(prune_repo(_PlainCtx(repo, d.env, d.runner), apply=apply, label=label)))
            continue
        try:
            res = mod.repo_resolve(str(repo), home=d.home, detection=det)
        except Exception as exc:  # noqa: BLE001
            out(f"## {label}\n  skip: resolve failed ({exc.__class__.__name__})")
            continue
        if _claude_chain(det) and not res.get("positively_personal"):
            # Checked before ANY git or gh subprocess in this repo.
            if pinned is None:
                st = {"status": "unpinned", "notice": "pinned lib absent or predates vetted_context"}
            else:
                st = pinned.vetted_status(SCRIPT_ID, script_path=d.script, home=d.home)
            if st.get("status") != "vetted":
                out(f"## {label}\n  skip: vetted-status {st.get('status')} — {st.get('notice') or 'not vetted'}")
                continue
        employer_gh = res.get("owner_class") == "employer"
        with mod.vetted_context(SCRIPT_ID, str(repo), d.script, home=d.home, detection=det, hostname=d.hostname,
                                env=d.env, runner=d.runner, assume_unpinned=pinned is None,
                                out=lambda s: out(f"  {s}")) as ctx:
            out("\n".join(prune_repo(ctx, apply=apply, employer_gh=employer_gh, label=label)))
    return 0


# --------------------------------------------------------------------------- self-test


def _decide_cases() -> list[str]:
    merged = {"feat/done"}
    opened = {"feat/open"}
    cases = [
        decide("main", merged_ours=merged, open_heads=opened, ahead_of_remote=False),
        decide("feat/done", merged_ours=merged, open_heads=opened, ahead_of_remote=False),
        decide("feat/done", merged_ours=merged, open_heads=opened, ahead_of_remote=True),
        decide("feat/open", merged_ours=merged, open_heads=opened, ahead_of_remote=False),
        decide("feat/theirs", merged_ours=merged, open_heads=opened, ahead_of_remote=False),
        decide("develop", merged_ours={"develop"}, open_heads=set(), ahead_of_remote=False,
               protected=frozenset(PROTECTED | {"develop"})),
    ]
    expect = [
        ("main", "keep", "protected"),
        ("feat/done", "prune", "merged PR by us"),
        ("feat/done", "keep", "unpushed unique commits"),
        ("feat/open", "keep", "open PR"),
        ("feat/theirs", "keep", "not a merged PR by us"),
        ("develop", "keep", "protected"),
    ]
    fails = []
    for got, wanted in zip(cases, expect):
        if (got.name, got.action, got.reason) != wanted:
            fails.append(f"decide {(got.name, got.action, got.reason)} != {wanted}")
    return fails


def _load_file(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def self_test() -> int:
    fails = _decide_cases()
    passes = [0]

    def ok(cond: Any, label: str) -> None:
        if cond:
            passes[0] += 1
        else:
            fails.append(label)

    me = Path(__file__).resolve()
    again = _isolated_argv(["--apply"], False, "/usr/bin/python3", Path("09-tools/../09-tools/prune-our-branches.py"))
    ok(again is not None and again[:2] == ["/usr/bin/python3", "-I"] and os.path.isabs(again[2])
       and again[3:] == ["--apply"], f"a non-isolated run re-execs under -I by absolute path: {again}")
    ok(_isolated_argv(["--apply"], True, "/usr/bin/python3", me) is None, "an isolated run does not re-exec")

    vault = _vault_resolver()
    fx = ROOT / "09-tools" / "fixtures"
    if vault is None or not (fx / "action_policy").is_dir() or not (fx / "profile_resolve").is_dir():
        print("prune-our-branches self-test FAIL: profile_resolve or its fixtures are missing", file=sys.stderr)
        return 1
    if not hasattr(vault, "vetted_context"):
        print("prune-our-branches self-test FAIL: profile_resolve has no vetted_context", file=sys.stderr)
        return 1
    this = Path(__file__).resolve()
    with tempfile.TemporaryDirectory(prefix="ws-prune-") as td:
        tmp = Path(os.path.realpath(td))
        # A synthetic vault: fixture tables, the committed registry, and a copy of the resolver.
        vroot = tmp / "vault"
        for name in ("devices", "context-remotes", "surfaces"):
            vault._write(vroot / vault.TABLE_PATHS[name], (fx / "profile_resolve" / f"{name}.json").read_text("utf-8"))
        vault._write(vroot / vault.TABLE_PATHS["action-policy"], (fx / "action_policy" / "action-policy.json").read_text("utf-8"))
        vault._write(vroot / vault.TABLE_PATHS["vetted-scripts"],
                     (ROOT / vault.TABLE_PATHS["vetted-scripts"]).read_text("utf-8"))
        vault._write(vroot / "09-tools" / "profile_resolve.py", (ROOT / "09-tools" / "profile_resolve.py").read_text("utf-8"))
        vault._write(vroot / "AGENTS.md", "# fixture\n")
        fixture_mod = _load_file("ws_fixture_vault_profile_resolve", vroot / "09-tools" / "profile_resolve.py")
        home = tmp / "home"
        home.mkdir()
        blocked = str(fixture_mod.load_table("context-remotes")["blocked_scheme"])

        # gh is never executed: the runner seam answers `gh pr list`; a PATH stub records any call.
        stub_dir = tmp / "bin"
        stub_dir.mkdir()
        marker = tmp / "gh-called"
        gh = stub_dir / "gh"
        gh.write_text(f"#!/bin/sh\ntouch '{marker}'\nexit 1\n", encoding="utf-8")
        gh.chmod(0o755)
        genv = dict(vault._git_env(home), PATH=f"{stub_dir}{os.pathsep}{os.environ.get('PATH', '/usr/bin:/bin')}")
        calls: list[Tuple[List[str], str, dict]] = []

        def runner(argv: List[str], *, cwd: str, env: dict, timeout: float) -> subprocess.CompletedProcess:
            calls.append((list(argv), cwd, dict(env)))
            if argv and argv[0] == "gh":
                heads = ["feat/done"] if "merged" in argv else []
                return subprocess.CompletedProcess(argv, 0, json.dumps([{"number": 1, "headRefName": h, "state": "x"}
                                                                         for h in heads]), "")
            return subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)

        def has_ref(bare: Path, name: str) -> bool:
            return vault._g(genv, "--git-dir", str(bare), "show-ref", "--verify", "--quiet",
                            f"refs/heads/{name}").returncode == 0

        def local_has(clone: Path, name: str) -> bool:
            return vault._g(genv, "show-ref", "--verify", "--quiet", f"refs/heads/{name}", cwd=clone).returncode == 0

        human = fixture_mod.detect_surface(env={}, ancestry=[{"comm": "zsh"}], isatty=vault.HUMAN_TTY)
        claude = fixture_mod.detect_surface(env={}, ancestry=[{"comm": "claude"}], isatty=vault.HUMAN_TTY)

        # the pinned lib (what --install-pin leaves), holding this file's blob
        lib = vault._pin_fixture(home, vroot, "09-tools/prune-our-branches.py", vault.git_blob_sha(this))
        vault._write(lib / "09-tools" / "profile_resolve.py", (vroot / "09-tools" / "profile_resolve.py").read_text("utf-8"))
        pinned = _pinned_resolver(home)
        ok(pinned is not None and pinned.vetted_status(SCRIPT_ID, script_path=this, home=home)["status"] == "vetted",
           "pinned lib imports and this file is vetted")
        receipts = vault.ws_paths(home=home)["control"] / "receipts.jsonl"

        def new_receipts(before: int) -> list[dict]:
            if not receipts.exists():
                return []
            return [json.loads(x) for x in receipts.read_text("utf-8").splitlines()[before:]]

        def n_lines() -> int:
            return len(receipts.read_text("utf-8").splitlines()) if receipts.exists() else 0

        printed: list[str] = []

        def deps(**kw: Any) -> Deps:
            base = dict(home=home, detection=human, hostname="host-a", env=genv, runner=runner, resolver=pinned,
                        pinned=pinned, out=printed.append, script=this)
            base.update(kw)
            return Deps(**base)

        # 1. human, personal repo: local + remote deleted, one receipt per deletion
        mine, mine_bare, _e = vault._employer_pair(tmp, home, slug="pat-sample/mine")
        before = n_lines()
        run([mine], apply=True, deps=deps())
        rec = [r for r in new_receipts(before) if r["type"] == "receipt"]
        ok(not local_has(mine, "feat/done") and not has_ref(mine_bare, "feat/done"), "human apply prunes local + remote")
        dels = [r for r in rec if r["action"] in ("branch-delete", "remote-branch-delete")]
        ok([r["action"] for r in dels] == ["branch-delete", "remote-branch-delete"]
           and all(r["result"] == "ok" and r["refs"] == ["refs/heads/feat/done"] for r in dels),
           f"one receipt per deletion: {[(r['action'], r['result']) for r in rec]}")
        ok(any(c[0][:1] == ["gh"] for c in calls), "gh calls go through the runner seam")

        # 2. a diverged default branch is never reset
        div, div_bare, _e = vault._employer_pair(tmp, home, slug="pat-sample/diverged")
        vault._g(genv, "switch", "-q", "feat/done", cwd=div)
        vault._g(genv, "branch", "-q", "-f", "main", "main", cwd=div)
        other = tmp / "other-clone"
        vault._g(genv, "clone", "-q", str(div_bare), str(other))
        vault._write(other / "up.txt", "upstream\n")
        vault._g(genv, "add", "up.txt", cwd=other)
        vault._g(genv, "commit", "-q", "-m", "upstream", cwd=other)
        vault._g(genv, "push", "-q", "origin", "main", cwd=other)
        vault._g(genv, "switch", "-q", "main", cwd=div)
        vault._write(div / "local.txt", "local only\n")
        vault._g(genv, "add", "local.txt", cwd=div)
        vault._g(genv, "commit", "-q", "-m", "local only", cwd=div)
        local_main = vault._g(genv, "rev-parse", "main", cwd=div).stdout.strip()
        vault._g(genv, "switch", "-q", "feat/done", cwd=div)
        printed.clear()
        run([div], apply=True, deps=deps())
        ok(vault._g(genv, "rev-parse", "main", cwd=div).stdout.strip() == local_main, "a diverged main is never reset")
        ok(local_has(div, "feat/done") and any("never reset" in p for p in printed),
           f"the branch is kept and the divergence reported: {printed[-3:]}")

        # 3. Claude chain, employer repo, unpinned lib: skipped with zero git/gh calls in it
        emp, emp_bare, _e = vault._employer_pair(tmp, home, slug="acme-corp/widget")
        pers, _pb, _e = vault._employer_pair(tmp, home, slug="pat-sample/other")
        overlay = vault._overlay_env(genv, blocked, ["git@github.com:acme-corp/", "git@bitbucket.org:acme-bb/"])
        spied: list[Tuple[List[str], str]] = []
        real_run = subprocess.run

        def spy(argv: Any, *a: Any, **kw: Any) -> Any:
            spied.append((list(argv) if isinstance(argv, (list, tuple)) else [str(argv)], str(kw.get("cwd") or "")))
            return real_run(argv, *a, **kw)

        printed.clear()
        subprocess.run = spy  # type: ignore[assignment]
        try:
            run([emp, pers], apply=True, deps=deps(detection=claude, env=overlay, resolver=fixture_mod, pinned=None,
                                                  home=tmp / "home-unpinned"))
        finally:
            subprocess.run = real_run  # type: ignore[assignment]
        in_emp = [c for c in spied if c[1].startswith(str(emp)) or any(str(emp) in x for x in c[0])]
        in_pers = [c for c in spied if c[1].startswith(str(pers))]
        ok(not in_emp, f"unpinned: zero git or gh calls in the employer repo ({len(in_emp)})")
        ok(any("vetted-status unpinned" in p for p in printed) and in_pers, "unpinned: a notice, and the run continues")
        ok(local_has(emp, "feat/done") and has_ref(emp_bare, "feat/done"), "unpinned: the employer repo is untouched")

        # 4. hash mismatch: skipped with zero calls
        spied.clear()
        printed.clear()
        bad_lock = json.loads((lib / "vetted.lock.json").read_text("utf-8"))
        bad_lock["scripts"][0]["blob"] = "0" * 40
        (lib / "vetted.lock.json").write_text(json.dumps(bad_lock), encoding="utf-8")
        subprocess.run = spy  # type: ignore[assignment]
        try:
            run([emp], apply=True, deps=deps(detection=claude, env=overlay))
        finally:
            subprocess.run = real_run  # type: ignore[assignment]
        in_emp = [c for c in spied if c[1].startswith(str(emp)) or any(str(emp) in x for x in c[0])]
        ok(not in_emp and any("hash-mismatch" in p for p in printed), "hash mismatch: skipped, zero calls")
        vault._pin_fixture(home, vroot, "09-tools/prune-our-branches.py", vault.git_blob_sha(this))
        vault._write(lib / "09-tools" / "profile_resolve.py", (vroot / "09-tools" / "profile_resolve.py").read_text("utf-8"))

        # 5. Claude chain, employer repo, vetted: composed push --delete fails, the vetted path succeeds
        composed = vault._g(overlay, "push", "origin", "--delete", "feat/done", cwd=emp)
        ok(composed.returncode != 0 and has_ref(emp_bare, "feat/done"), "composed employer push --delete fails (transport)")
        calls.clear()
        before = n_lines()
        printed.clear()
        run([emp], apply=True, deps=deps(detection=claude, env=overlay))
        ok(not local_has(emp, "feat/done") and not has_ref(emp_bare, "feat/done"),
           f"vetted apply prunes the employer branch via the lifted env: {printed[-4:]}")
        rec = new_receipts(before)
        rd = [r for r in rec if r["type"] == "receipt" and r["action"] == "remote-branch-delete"]
        ok(len(rd) == 1 and rd[0]["result"] == "ok" and rd[0]["credential"] == "ssh:github.com"
           and rd[0]["repo_slug"] == "acme-corp/widget" and rd[0]["family"] == "claude",
           f"the remote deletion has a receipt naming repo and credential: {rd}")
        ok(any(r["type"] == "intent" and r["action"] == "remote-branch-delete" for r in rec), "intent line precedes it")
        gh_envs = [c[2] for c in calls if c[0][:1] == ["gh"]]
        git_envs = [c[2] for c in calls if c[0][:1] == ["git"]]
        ok(gh_envs and all("GH_CONFIG_DIR" not in e for e in gh_envs), "employer gh calls restore the default gh")
        ok(git_envs and all(blocked not in json.dumps(e) for e in git_envs), "every git call ran with the lifted env")
        ok(not marker.exists(), "the gh stub on PATH was never called")

        # 6. DEFAULT_SLUGS resolve through `where`; a slug not on this device is a skip with a notice
        tel = vault.ws_paths(home=home)["telemetry"]
        tel.mkdir(parents=True, exist_ok=True)
        (tel / "checkouts.json").write_text(json.dumps({
            "schema_version": 1, "device": "dev-a", "generated_at": vault._now_z(), "generated_by": "human",
            "projects_root": str(home / "Projects"),
            "checkouts": [{"path": str(pers), "kind": "repo", "owner_class": "personal", "default_branch": None,
                           "remotes": [{"name": "origin", "form": "scp", "host": "github.com",
                                        "slug": "pat-sample/other"}]}]}), encoding="utf-8")
        printed.clear()
        calls.clear()
        run(None, apply=False, deps=deps(workspace=mine, slugs=("pat-sample/other", "acme-corp/absent")))
        ok(any(p.startswith(f"## {mine}") for p in printed) and any(p.startswith("## pat-sample/other") for p in printed)
           and any("acme-corp/absent" in p and "not on this device" in p for p in printed),
           f"slugs via where: {[p.splitlines()[0] for p in printed]}")
        ok(not any(c[0][:1] == ["git"] and c[0][1:3] in (["branch", "-D"], ["push", "origin"]) for c in calls),
           "dry-run deletes nothing")
        ok(not marker.exists(), "gh stub never called")

    if fails:
        for f in fails:
            print(f"FAIL {f}", file=sys.stderr)
        print(f"prune-our-branches self-test: {passes[0]} passed, {len(fails)} failed", file=sys.stderr)
        return 1
    print(f"prune-our-branches self-test ok ({passes[0] + 6} checks)")
    return 0


def _isolated_argv(argv: List[str], isolated: bool, exe: str, script: Path) -> Optional[List[str]]:
    """The argv to re-exec under `python3 -I <absolute path>`, or None when already isolated.

    The Claude floor accepts a vetted ancestor only when it runs isolated and names its script by an
    absolute path, so PYTHONPATH, user site hooks or a same-named copy elsewhere cannot stand in."""
    if isolated or "--self-test" in argv:
        return None
    return [exe, "-I", str(Path(script).resolve()), *argv]


def main() -> int:
    again = _isolated_argv(sys.argv[1:], bool(sys.flags.isolated), sys.executable, Path(__file__))
    if again is not None:
        os.execv(sys.executable, again)
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="delete prune-ok branches (default is dry-run)")
    parser.add_argument("--repo", action="append", type=Path, help="checkout to scan (repeatable)")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    return run(args.repo, apply=args.apply)


if __name__ == "__main__":
    raise SystemExit(main())
