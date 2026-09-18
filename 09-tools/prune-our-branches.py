#!/usr/bin/env python3
"""Prune merged branches we created. Safe for /session-end hygiene.

Deletes a local (and still-present remote) branch only when ALL of:
  - `gh pr` shows a MERGED pull request for that head, authored by `@me`
  - no OPEN pull request uses that head
  - the branch is not `main` / `master`
  - local is not ahead of `origin/<branch>` (no unpushed unique commits)
  - a linked worktree is clean, or the primary checkout can fast-forward to main

Squash-merged branches are not ancestors of main — do not use merge-base as
the keep/delete signal. Unmerged work, someone else's PRs, and dirty leftover
worktrees are left alone.

Usage:
  python3 09-tools/prune-our-branches.py              # dry-run default repos
  python3 09-tools/prune-our-branches.py --apply
  python3 09-tools/prune-our-branches.py --apply --repo /path/to/checkout
  python3 09-tools/prune-our-branches.py --self-test
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROTECTED = frozenset({"main", "master", "HEAD"})
DEFAULT_RELATIVE_REPOS = (
    "cpes-software/cds",
    "cpes-software/saas-plm-prototype",
)


def projects_root() -> Path:
    for name in ("Projects", "projects"):
        path = Path.home() / name
        if path.is_dir():
            return path
    return Path.home() / "Projects"


def default_repos() -> list[Path]:
    found = [ROOT]
    root = projects_root()
    for rel in DEFAULT_RELATIVE_REPOS:
        path = root / rel
        if (path / ".git").exists():
            found.append(path)
    return found


def git(repo: Path, *args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=check,
    )


def gh_json(repo: Path, args: list[str]) -> list[dict]:
    proc = subprocess.run(
        ["gh", "pr", "list", *args, "--json", "number,headRefName,state"],
        capture_output=True,
        text=True,
        cwd=str(repo),
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "gh pr list failed")
    data = json.loads(proc.stdout or "[]")
    if not isinstance(data, list):
        raise RuntimeError("gh pr list returned a non-list")
    return data


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


def local_branches(repo: Path) -> list[str]:
    proc = git(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads")
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def current_branch(repo: Path) -> str:
    return git(repo, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()


def ahead_of_remote(repo: Path, name: str) -> bool:
    remote = f"origin/{name}"
    exists = git(repo, "show-ref", "--verify", "--quiet", f"refs/remotes/{remote}")
    if exists.returncode != 0:
        return False
    counts = git(repo, "rev-list", "--left-right", "--count", f"{remote}...{name}").stdout.strip()
    try:
        _behind, ahead = (int(part) for part in counts.split())
    except ValueError:
        return True
    return ahead > 0


def worktree_map(repo: Path) -> dict[str, Path]:
    """branch name → worktree path (skips detached)."""
    mapping: dict[str, Path] = {}
    proc = git(repo, "worktree", "list", "--porcelain")
    path: Path | None = None
    for line in proc.stdout.splitlines():
        if line.startswith("worktree "):
            path = Path(line[len("worktree ") :])
        elif line.startswith("branch refs/heads/") and path is not None:
            mapping[line.split("refs/heads/", 1)[1]] = path
            path = None
        elif line == "":
            path = None
    return mapping


def worktree_dirty(path: Path) -> bool:
    # Tracked changes only — node_modules and gitignored vendor do not block.
    proc = git(path, "status", "--porcelain", "--untracked-files=no")
    return bool(proc.stdout.strip())


def remote_branch_exists(repo: Path, name: str) -> bool:
    return git(repo, "show-ref", "--verify", "--quiet", f"refs/remotes/origin/{name}").returncode == 0


def switch_to_main(repo: Path) -> str | None:
    fetch = git(repo, "fetch", "origin", "main")
    if fetch.returncode != 0:
        return fetch.stderr.strip() or "fetch origin main failed"
    switched = git(repo, "switch", "-C", "main", "origin/main")
    if switched.returncode != 0:
        return switched.stderr.strip() or "switch to origin/main failed"
    return None


def prune_repo(repo: Path, *, apply: bool) -> list[str]:
    lines: list[str] = [f"## {repo}"]
    fetch = git(repo, "fetch", "--prune", "origin")
    if fetch.returncode != 0:
        lines.append(f"  skip: fetch failed ({fetch.stderr.strip() or 'unknown'})")
        return lines

    try:
        merged = {row["headRefName"] for row in gh_json(repo, ["--state", "merged", "--author", "@me", "--limit", "200"])}
        opened = {row["headRefName"] for row in gh_json(repo, ["--state", "open", "--limit", "100"])}
    except RuntimeError as exc:
        lines.append(f"  skip: {exc}")
        return lines

    trees = worktree_map(repo)
    current = current_branch(repo)

    for name in local_branches(repo):
        decision = decide(
            name,
            merged_ours=merged,
            open_heads=opened,
            ahead_of_remote=ahead_of_remote(repo, name),
        )
        if decision.action == "keep":
            lines.append(f"  keep  {name} — {decision.reason}")
            continue

        wt = trees.get(name)
        if wt is not None and worktree_dirty(wt):
            lines.append(f"  keep  {name} — dirty worktree {wt}")
            continue

        if not apply:
            extra = " + remote" if remote_branch_exists(repo, name) else ""
            lines.append(f"  prune {name}{extra} (dry-run)")
            continue

        if wt is not None:
            if wt.resolve() == repo.resolve():
                err = switch_to_main(repo)
                if err:
                    lines.append(f"  keep  {name} — cannot leave checkout: {err}")
                    continue
            else:
                removed = git(repo, "worktree", "remove", str(wt))
                if removed.returncode != 0:
                    lines.append(f"  keep  {name} — worktree remove failed: {removed.stderr.strip()}")
                    continue

        deleted = git(repo, "branch", "-D", name)
        if deleted.returncode != 0:
            lines.append(f"  keep  {name} — local delete failed: {deleted.stderr.strip()}")
            continue
        note = f"  pruned {name}"
        if remote_branch_exists(repo, name):
            pushed = git(repo, "push", "origin", "--delete", name)
            if pushed.returncode == 0:
                note += " + remote"
            else:
                note += f" (remote left: {pushed.stderr.strip()})"
        if current == name:
            note += " (was HEAD; now main)"
        lines.append(note)

    remaining_local = set(local_branches(repo))
    for name in sorted(merged - remaining_local):
        if name in PROTECTED or name in opened:
            continue
        if not remote_branch_exists(repo, name):
            continue
        if not apply:
            lines.append(f"  prune origin/{name} (dry-run, remote-only)")
            continue
        pushed = git(repo, "push", "origin", "--delete", name)
        if pushed.returncode == 0:
            lines.append(f"  pruned origin/{name} (remote-only)")
        else:
            lines.append(f"  keep  origin/{name} — {pushed.stderr.strip()}")
    return lines


def self_test() -> int:
    merged = {"feat/done"}
    opened = {"feat/open"}
    cases = [
        decide("main", merged_ours=merged, open_heads=opened, ahead_of_remote=False),
        decide("feat/done", merged_ours=merged, open_heads=opened, ahead_of_remote=False),
        decide("feat/done", merged_ours=merged, open_heads=opened, ahead_of_remote=True),
        decide("feat/open", merged_ours=merged, open_heads=opened, ahead_of_remote=False),
        decide("feat/theirs", merged_ours=merged, open_heads=opened, ahead_of_remote=False),
    ]
    expect = [
        ("main", "keep", "protected"),
        ("feat/done", "prune", "merged PR by us"),
        ("feat/done", "keep", "unpushed unique commits"),
        ("feat/open", "keep", "open PR"),
        ("feat/theirs", "keep", "not a merged PR by us"),
    ]
    ok = True
    for got, wanted in zip(cases, expect, strict=True):
        actual = (got.name, got.action, got.reason)
        if actual != wanted:
            print(f"FAIL {actual} != {wanted}", file=sys.stderr)
            ok = False
    if ok:
        print("prune-our-branches self-test ok")
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="delete prune-ok branches (default is dry-run)")
    parser.add_argument("--repo", action="append", type=Path, help="checkout to scan (repeatable)")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()

    repos = [path.resolve() for path in (args.repo or default_repos())]
    mode = "apply" if args.apply else "dry-run"
    print(f"prune-our-branches ({mode})")
    for repo in repos:
        if not (repo / ".git").exists():
            print(f"## {repo}\n  skip: not a git checkout")
            continue
        print("\n".join(prune_repo(repo, apply=args.apply)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
