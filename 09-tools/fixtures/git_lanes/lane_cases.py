"""Temp-HOME fixtures for the H18 global git lanes (git_lanes.py).

Everything runs in a temp dir with a temp HOME: a synthetic pinned lib (copies of this checkout's
git_lanes.py and profile_resolve.py plus the synthetic identity tables), the lanes installed by the
REAL installer (installers.py `git-hooks`, human verdict injected, temp HOME only), local bare remotes
standing in for the network (url.insteadOf in the temp ~/.gitconfig), and synthetic owners only
(pat-sample personal, acme-corp employer). Nothing touches the real HOME, the real ~/.gitconfig or
any real checkout, and nothing is pushed anywhere but a temp bare repo.

The fixture lib's profile_resolve copy reads no process table (its `_ps_default` is replaced at the
end of the copy), so the runner's own ancestry (a Claude session, a terminal) never decides a case:
each case's family comes from its env markers, exactly as a sandboxed host that denies `ps` would.
Ancestry-based detection is covered in-process through lane_decide(ancestry=...).

Each case is (name, passed, detail); passed is None for a SKIP (git < 2.54), which callers report as
a skip and never as a pass. Used by `git_lanes.py --self-test` and TestGitLanes in test-validators.py.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

FX = Path(__file__).resolve().parent
ROOT = FX.parents[2]
TOOLS = ROOT / "09-tools"
ID_FX = TOOLS / "fixtures" / "identity"
HUMAN = {"human": True, "determined": True, "reasons": []}
TTY = {"stdin": True, "stdout": True}
PS_STUB = ('\n\n# --- lane fixture: no process table (the runner\'s ancestry never decides a case) ---\n'
           'def _ps_default(columns):\n    raise OSError("lane fixture: ps disabled")\n')
NIGHTLY_STUB = ('import os, sys\n'
                'flag = os.path.join(os.environ["HOME"], "heal-stale")\n'
                'if os.path.exists(flag):\n'
                '    print("nightly lane: generated files are stale (fixture)", file=sys.stderr)\n'
                '    sys.exit(1)\n'
                'sys.exit(0)\n')


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(str(path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def git_version() -> tuple:
    try:
        out = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return (0,)
    m = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", out)
    return tuple(int(x) for x in m.groups() if x is not None) if m else (0,)


def snapshot(top: Path) -> dict:
    """Every path under a repo (work tree AND .git/) with its bytes, link target or dir marker."""
    snap = {}
    for dirpath, dirnames, filenames in os.walk(top):
        for d in dirnames:
            p = Path(dirpath) / d
            snap[str(p.relative_to(top))] = ("link", os.readlink(p)) if p.is_symlink() else ("dir",)
        for f in filenames:
            p = Path(dirpath) / f
            snap[str(p.relative_to(top))] = ("link", os.readlink(p)) if p.is_symlink() else ("file", p.read_bytes())
    return snap


def diff_snap(a: dict, b: dict) -> list:
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


class Lab:
    """A temp world: HOME with a pinned lib, lanes installed by the real installer, bare remotes."""

    def __init__(self, tmp: Path):
        self.tmp = tmp
        self.home = tmp / "home"
        self.home.mkdir(parents=True)
        self.base = self.home / ".config" / "snds-workspace"
        self.bare_root = tmp / "remotes"
        self.bare_root.mkdir()
        self.pr = load(TOOLS / "profile_resolve.py", "lane_fx_profile_resolve")
        self.dev = json.loads((ID_FX / "devices.json").read_text(encoding="utf-8"))
        self.lib = self.base / "lib" / ("b" * 40)
        self.env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(self.home),
                    "XDG_CONFIG_HOME": str(self.home / ".config"), "GIT_CONFIG_NOSYSTEM": "1", "LANG": "C",
                    "LC_ALL": "C", "GIT_TERMINAL_PROMPT": "0", "TMPDIR": os.environ.get("TMPDIR", "/tmp")}
        (self.home / ".gitconfig").write_text(
            f'[url "file://{self.bare_root}/"]\n\tinsteadOf = git@github.com:\n'
            "[init]\n\tdefaultBranch = main\n", encoding="utf-8")
        self._pin()
        self.ws = self._workspace()

    # -- setup ---------------------------------------------------------------------------------
    def _pin(self) -> None:
        tp = self.pr.TABLE_PATHS
        src = {"devices": ID_FX / "devices.json", "context-remotes": ID_FX / "context-remotes.json",
               "surfaces": TOOLS / "fixtures" / "profile_resolve" / "surfaces.json",
               "action-policy": TOOLS / "fixtures" / "action_policy" / "action-policy.json",
               "vetted-scripts": TOOLS / "fixtures" / "action_policy" / "vetted-scripts.json"}
        for name, path in src.items():
            dst = self.lib / tp[name]
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dst)
        (self.lib / "09-tools").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(TOOLS / "git_lanes.py", self.lib / "09-tools" / "git_lanes.py")
        # W2-0 item 2: every lane enters through the pinned bin/ws-hook → ws_hook.py lane EVENT.
        shutil.copyfile(TOOLS / "ws_hook.py", self.lib / "09-tools" / "ws_hook.py")
        wh = self.base / "bin" / "ws-hook"
        wh.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "00-bootstrap" / "dist" / "ws-hook", wh)
        wh.chmod(0o755)
        (self.base / "telemetry").mkdir(parents=True, exist_ok=True)
        (self.lib / "09-tools" / "profile_resolve.py").write_text(
            (TOOLS / "profile_resolve.py").read_text(encoding="utf-8") + PS_STUB, encoding="utf-8")
        (self.lib / "vetted.lock.json").write_text(json.dumps({"schema_version": 1, "scripts": []}), encoding="utf-8")
        (self.base / "lib" / "current").symlink_to(self.lib.name)

    def _workspace(self) -> Path:
        """A workspace-shaped checkout (the fixture context-remotes declares pat-sample/ws role workspace)
        with a stand-in H1 lane that fails while $HOME/heal-stale exists."""
        ws = self.tmp / "ws"
        self.bare("pat-sample/ws")
        self.g(self.env, "init", "-q", "-b", "main", str(ws))
        self.g(self.env, "remote", "add", "origin", "git@github.com:pat-sample/ws.git", cwd=ws)
        (ws / "AGENTS.md").write_text("# fixture workspace\n", encoding="utf-8")
        (ws / "09-tools").mkdir()
        (ws / "09-tools" / "nightly.py").write_text(NIGHTLY_STUB, encoding="utf-8")
        (self.base / "root").write_text(f"{ws}\n", encoding="utf-8")
        return ws

    def install(self, name: str = "git-hooks") -> tuple:
        """The lanes through the real installer (git-hooks, or git-hooks=block), into this temp HOME only."""
        inst = load(ROOT / "00-bootstrap" / "doctor" / "installers.py", "lane_fx_installers")
        dev = inst.pin_lib._PR_LOADER().current_device().get("id") or "unknown"
        repo = self.tmp / "vault"
        (repo / "02-shared-references" / "probes").mkdir(parents=True, exist_ok=True)
        (repo / "02-shared-references" / "probes" / f"git@{dev}.json").write_text(json.dumps(
            {"schema_version": 1, "surface": "git", "device": dev, "git_version": ".".join(map(str, git_version())),
             "hasconfig": True, "config_hooks": True, "recorded_at": "2026-09-24"}), encoding="utf-8")
        dist = repo / "00-bootstrap" / "dist" / "git" / "lanes" / "ws-lanes.inc"
        dist.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / "00-bootstrap" / "dist" / "git" / "lanes" / "ws-lanes.inc", dist)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = inst.run(name, "install", home=self.home, repo=repo, agent_check=lambda: dict(HUMAN),
                          isatty=dict(TTY), confirm=lambda _p: "y")
        return rc, out.getvalue() + err.getvalue()

    def bare(self, slug: str) -> Path:
        b = self.bare_root / f"{slug}.git"
        if not b.exists():
            b.parent.mkdir(parents=True, exist_ok=True)
            self.g(self.env, "init", "-q", "--bare", "-b", "main", str(b))
        return b

    def g(self, env: dict, *args: str, cwd=None) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *args], cwd=str(cwd) if cwd else None, env=env, capture_output=True,
                              text=True, timeout=120)

    def mail(self, iid: str) -> str:
        return next(i["email"] for i in self.dev["identities"] if i["id"] == iid)

    def ident(self, env: dict, iid: str) -> dict:
        name = next(i["name"] for i in self.dev["identities"] if i["id"] == iid)
        return dict(env, GIT_AUTHOR_NAME=name, GIT_AUTHOR_EMAIL=self.mail(iid), GIT_COMMITTER_NAME=name,
                    GIT_COMMITTER_EMAIL=self.mail(iid))

    def clone(self, slug: str, name: str, *, email_id: str) -> Path:
        """A repo with an origin at git@github.com:<slug>.git (a local bare), one base commit pushed
        with the lanes bypassed (setup only), and a repo-local identity."""
        self.bare(slug)
        c = self.tmp / "work" / name
        c.parent.mkdir(parents=True, exist_ok=True)
        self.g(self.env, "init", "-q", "-b", "main", str(c))
        self.g(self.env, "remote", "add", "origin", f"git@github.com:{slug}.git", cwd=c)
        setup = dict(self.ident(self.env, "acme-id" if slug.startswith("acme") else "pat"), GIT_CONFIG_GLOBAL="/dev/null")
        setup_url = ["-c", f"url.file://{self.bare_root}/.insteadOf=git@github.com:"]
        (c / "README.md").write_text("fixture\n", encoding="utf-8")
        self.g(setup, "add", "README.md", cwd=c)
        self.g(setup, "commit", "-q", "-m", "base", cwd=c)
        self.g(setup, *setup_url, "push", "-q", "origin", "main", cwd=c)
        self.g(setup, *setup_url, "fetch", "-q", "origin", cwd=c)
        self.g(self.env, "remote", "set-head", "origin", "main", cwd=c)
        self.g(self.env, "config", "user.name", "Fixture", cwd=c)
        self.g(self.env, "config", "user.email", self.mail(email_id), cwd=c)
        return c

    def stage(self, repo: Path, name: str) -> None:
        """Stage a file and settle the index, so a later snapshot sees only what the lane did. `git
        commit` writes the staged tree's objects and the index cache-tree BEFORE any hook runs (git's
        own step, identical with no hooks at all); write-tree does that step up front, and waiting past
        the racy-git window keeps a later refresh from rewriting the index."""
        (repo / name).write_text(f"{name}\n", encoding="utf-8")
        self.g(self.env, "add", name, cwd=repo)
        self.g(self.env, "write-tree", cwd=repo)
        time.sleep(1.1)
        self.g(self.env, "status", "--porcelain", cwd=repo)

    def ref(self, slug: str, branch: str) -> str:
        r = self.g(self.env, "--git-dir", str(self.bare(slug)), "rev-parse", "-q", "--verify", f"refs/heads/{branch}")
        return r.stdout.strip()


CASES = [
    "install: the real installer writes the include and the ~/.gitconfig block; git hook list shows every lane",
    "employer I1: a commit with a personal identity is blocked [I1], names the expected identity, and the repo "
    "stays byte-identical including .git/",
    "employer I1: a commit with an identity off the employer allowlist is blocked [I1]",
    "employer Claude chain: a WS_SURFACE_FAMILY=claude commit with the employer identity is blocked [I2] and the "
    "repo stays byte-identical including .git/",
    "employer Claude chain: an agent-possible env (CLAUDECODE) alone tightens to the Claude floor [I2]",
    "employer: a Cursor commit with the employer identity on a feature branch passes",
    "employer pre-push: a rebase-created personal-identity commit is blocked [I1] and the remote ref is unchanged",
    "employer pre-push: employer-identity commits push",
    "employer R2: an agent push to the default branch passes with the report-only R2 notice",
    "personal: a personal-identity commit and push pass for a human, Cursor and a Claude chain",
    "unknown owner: an agent gets a WARN and passes; a human passes silently",
    "workspace: the H1 heal lane blocks a stale commit [H1] and passes a clean one",
    "husky: a core.hooksPath hook still runs beside the lanes, and the lane still blocks [I1]",
    "audit: an installed, untouched setup is clean (global and per repo)",
    "audit: a repo-local last-one-wins command, an empty event= entry and enabled=false are each findings",
    "audit: a later global entry outside the lane include is a finding",
    "residual: a repo-local empty event= really disables the lane (why the audit exists)",
    "residual: --no-verify and -c hook.ws-lane-pre-commit.enabled=false skip the lane (declared; H15 R6 and CI)",
    "fail-open: with the pin absent the lane allows (declared; the installer refuses without a pinned lane)",
    "in-process: a claude process in the ancestry gets the Claude floor [I2] on an employer repo",
    "in-process: the device-mismatch flag is a notice, never a block",
    "in-process (Sean 2026-09-24): a Cursor shell that also carries CLAUDE_CODE_SSE_PORT (an IDE terminal "
    "with the Claude extension, as the work-mbp cursor probe records) keeps Cursor's walls, and its "
    "employer-identity commit on an employer repo is allowed",
    "trailer (H10): an employer-repo commit carries no Workspace-Lane trailer and the lane leaves the employer repo "
    "byte-identical apart from git's own commit",
    "trailer (H10): a workspace commit carries Workspace-Lane <surface>/<family>/<device>; a personal repo gets one "
    "only after it opts in (ws.laneTrailer), an unknown-owner repo never",
    "ws-hook entry (W2-0 item 2): every rendered lane runs `bin/ws-hook lane EVENT`; with bin/ws-hook absent, or "
    "a broken git_lanes.py in the pin, the lane still allows (fail-open)",
]
TRAILER = "Workspace-Lane"
# Measurements, never pass/fail: the 300 ms target depends on the host (python start, bytecode, ps, git spawns).
REPORT: list = []


def lane_cases() -> list:
    if git_version() < (2, 54):
        v = ".".join(map(str, git_version()))
        return [(n, None, f"git {v} < 2.54 (config-based hooks)") for n in CASES]
    out = []
    td = tempfile.mkdtemp(prefix="ws-lanes-")
    try:
        lab = Lab(Path(os.path.realpath(td)))
        rc, log = lab.install()
        emp = lab.clone("acme-corp/widget", "emp", email_id="acme-id")
        gc = (lab.home / ".gitconfig").read_text(encoding="utf-8")
        listed = {ev: f"ws-lane-{ev}" in lab.g(lab.env, "hook", "list", ev, cwd=emp).stdout
                  for ev in ("pre-commit", "commit-msg", "pre-merge-commit", "pre-push", "prepare-commit-msg")}
        out.append((CASES[0], rc == 0 and "insteadOf" in gc and "path = ~/.config/snds-workspace/git/lanes/ws-lanes.inc"
                    in gc and all(listed.values()), f"rc={rc} listed={listed} {log[-300:]}"))

        # I1 at commit time, byte-identical
        lab.g(lab.env, "config", "user.email", lab.mail("pat"), cwd=emp)
        lab.stage(emp, "a.txt")
        before = snapshot(emp)
        r = lab.g(lab.env, "commit", "-m", "personal on employer", cwd=emp)
        changed = diff_snap(before, snapshot(emp))
        out.append((CASES[1], r.returncode != 0 and "[I1]" in r.stderr and "Acme Worker <4242+acme-worker" in r.stderr
                    and "-c user." not in r.stderr and not changed,
                    f"rc={r.returncode} changed={changed[:5]} {r.stderr[-400:]}"))
        lab.g(lab.env, "config", "user.email", "someone@elsewhere.example", cwd=emp)
        r = lab.g(lab.env, "commit", "-m", "outsider", cwd=emp)
        out.append((CASES[2], r.returncode != 0 and "[I1]" in r.stderr and "not on the employer allowlist" in r.stderr,
                    f"rc={r.returncode} {r.stderr[-300:]}"))
        lab.g(lab.env, "config", "user.email", lab.mail("acme-id"), cwd=emp)

        # Claude chain in the employer repo
        before = snapshot(emp)
        r = lab.g(dict(lab.env, WS_SURFACE_FAMILY="claude"), "commit", "-m", "claude on employer", cwd=emp)
        changed = diff_snap(before, snapshot(emp))
        out.append((CASES[3], r.returncode != 0 and "[I2]" in r.stderr and not changed,
                    f"rc={r.returncode} changed={changed[:5]} {r.stderr[-300:]}"))
        r = lab.g(dict(lab.env, CLAUDECODE="1"), "commit", "-m", "claude env on employer", cwd=emp)
        out.append((CASES[4], r.returncode != 0 and "[I2]" in r.stderr, f"rc={r.returncode} {r.stderr[-300:]}"))

        # Cursor feature-branch commit passes
        lab.g(lab.env, "switch", "-q", "-c", "feat/x", cwd=emp)
        cur = dict(lab.env, CURSOR_AGENT="1")
        lab.stage(emp, "cursor.txt")
        before = snapshot(emp)
        r = lab.g(cur, "commit", "-q", "-m", "cursor work", cwd=emp)
        out.append((CASES[5], r.returncode == 0, f"rc={r.returncode} {r.stderr[-300:]}"))
        body = lab.g(lab.env, "log", "-1", "--format=%B", cwd=emp).stdout
        # git's own commit touches HEAD, the branch ref, the logs, the index, objects and COMMIT_EDITMSG;
        # the lane may add nothing else (no config, no hook, no state file anywhere in the repo).
        own = (".git/logs/", ".git/refs/heads/", ".git/objects/", ".git/index", ".git/COMMIT_EDITMSG", ".git/ORIG_HEAD",
               ".git/HEAD")
        extra = [c for c in diff_snap(before, snapshot(emp)) if not any(str(c).startswith(o) for o in own)]
        trailer_emp = (r.returncode == 0 and TRAILER not in body and not extra, f"body={body!r} extra={extra[:5]}")

        # rebase-created personal commit, pre-push
        before_ref = lab.ref("acme-corp/widget", "feat/x")
        rb = lab.g(lab.env, "-c", f"user.email={lab.mail('pat')}", "-c", "user.name=Pat Sample", "rebase", "-q",
                   "--force-rebase", "main", cwd=emp)
        who = lab.g(lab.env, "log", "-1", "--format=%ce", cwd=emp).stdout.strip()
        r = lab.g(cur, "push", "origin", "feat/x", cwd=emp)
        out.append((CASES[6], rb.returncode == 0 and who == lab.mail("pat") and r.returncode != 0 and "[I1]" in r.stderr
                    and lab.ref("acme-corp/widget", "feat/x") == before_ref,
                    f"rebase={rb.returncode} committer={who} push={r.returncode} {r.stderr[-300:]}"))
        lab.g(lab.ident(lab.env, "acme-id"), "rebase", "-q", "--force-rebase", "main", cwd=emp)
        r = lab.g(cur, "push", "-q", "origin", "feat/x", cwd=emp)
        out.append((CASES[7], r.returncode == 0 and lab.ref("acme-corp/widget", "feat/x") != "",
                    f"rc={r.returncode} {r.stderr[-300:]}"))
        lab.g(lab.env, "switch", "-q", "main", cwd=emp)
        lab.g(lab.ident(lab.env, "acme-id"), "merge", "-q", "--ff-only", "feat/x", cwd=emp)
        r = lab.g(cur, "push", "origin", "main", cwd=emp)
        out.append((CASES[8], r.returncode == 0 and "R2 report-only" in r.stderr and "default branch" in r.stderr,
                    f"rc={r.returncode} {r.stderr[-300:]}"))

        # personal repo: human, Cursor, Claude chain
        mine = lab.clone("pat-sample/tool", "mine", email_id="pat")
        res = []
        for label, env in (("human", lab.env), ("cursor", cur), ("claude", dict(lab.env, WS_SURFACE_FAMILY="claude"))):
            lab.stage(mine, f"{label}.txt")
            c = lab.g(env, "commit", "-q", "-m", label, cwd=mine)
            p = lab.g(env, "push", "-q", "origin", "main", cwd=mine)
            res.append((label, c.returncode, p.returncode, (c.stderr + p.stderr)[-160:]))
        out.append((CASES[9], all(c == 0 and p == 0 for _l, c, p, _e in res), str(res)))
        mine_plain = lab.g(lab.env, "log", "-3", "--format=%B", cwd=mine).stdout
        lab.g(lab.env, "config", "ws.laneTrailer", "true", cwd=mine)
        lab.g(cur, "commit", "--allow-empty", "-q", "-m", "opted in", cwd=mine)
        mine_opt = lab.g(lab.env, "log", "-1", "--format=%(trailers:key=" + TRAILER + ",valueonly)", cwd=mine).stdout.strip()

        # unknown owner
        unk = lab.clone("someone-else/lib", "unk", email_id="pat")
        r_agent = lab.g(cur, "commit", "--allow-empty", "-m", "agent", cwd=unk)
        r_human = lab.g(lab.env, "commit", "--allow-empty", "-m", "human", cwd=unk)
        unk_body = lab.g(lab.env, "log", "-2", "--format=%B", cwd=unk).stdout
        out.append((CASES[10], r_agent.returncode == 0 and "WARN" in r_agent.stderr and r_human.returncode == 0
                    and "WARN" not in r_human.stderr, f"agent={r_agent.returncode} {r_agent.stderr[-200:]} "
                                                      f"human={r_human.returncode} {r_human.stderr[-200:]}"))

        # workspace H1
        lab.g(lab.env, "config", "user.email", lab.mail("pat"), cwd=lab.ws)
        lab.g(lab.env, "config", "user.name", "Pat Sample", cwd=lab.ws)
        (lab.home / "heal-stale").write_text("1", encoding="utf-8")
        lab.stage(lab.ws, "AGENTS.md")
        r1 = lab.g(lab.env, "commit", "-q", "-m", "stale", cwd=lab.ws)
        (lab.home / "heal-stale").unlink()
        r2 = lab.g(lab.env, "commit", "-q", "-m", "clean", cwd=lab.ws)
        out.append((CASES[11], r1.returncode != 0 and "[H1]" in r1.stderr and r2.returncode == 0,
                    f"stale={r1.returncode} {r1.stderr[-200:]} clean={r2.returncode} {r2.stderr[-200:]}"))
        ws_lane = lab.g(lab.env, "log", "-1", "--format=%(trailers:key=" + TRAILER + ",valueonly)", cwd=lab.ws).stdout.strip()
        r3 = lab.g(cur, "commit", "--allow-empty", "-q", "-m", "cursor in the workspace", cwd=lab.ws)
        ws_cursor = lab.g(lab.env, "log", "-1", "--format=%(trailers:key=" + TRAILER + ",valueonly)", cwd=lab.ws).stdout.strip()
        out.append((CASES[22], trailer_emp[0], trailer_emp[1]))
        out.append((CASES[23], len(ws_lane.split("/")) == 3 and r3.returncode == 0 and ws_cursor.startswith("cursor/cursor/")
                    and TRAILER not in mine_plain and mine_opt.startswith("cursor/cursor/") and TRAILER not in unk_body,
                    f"ws={ws_lane!r} ws_cursor={ws_cursor!r} personal_plain={TRAILER in mine_plain} "
                    f"personal_opted={mine_opt!r} unknown={TRAILER in unk_body}"))

        # husky beside the lanes
        marker = lab.tmp / "husky-ran"
        for repo, email in ((mine, "pat"), (emp, "pat")):
            (repo / ".husky").mkdir(exist_ok=True)
            hk = repo / ".husky" / "pre-commit"
            hk.write_text(f"#!/bin/sh\necho {repo.name} >> '{marker}'\nexit 0\n", encoding="utf-8")
            hk.chmod(0o755)
            lab.g(lab.env, "config", "core.hooksPath", ".husky", cwd=repo)
            lab.g(lab.env, "config", "user.email", lab.mail(email), cwd=repo)
        rm = lab.g(lab.env, "commit", "--allow-empty", "-m", "husky personal", cwd=mine)
        re_ = lab.g(lab.env, "commit", "--allow-empty", "-m", "husky employer", cwd=emp)
        ran = marker.read_text(encoding="utf-8").split() if marker.exists() else []
        out.append((CASES[12], rm.returncode == 0 and "mine" in ran and re_.returncode != 0 and "[I1]" in re_.stderr,
                    f"personal={rm.returncode} employer={re_.returncode} husky ran in {ran} {re_.stderr[-200:]}"))
        for repo in (mine, emp):
            lab.g(lab.env, "config", "--unset", "core.hooksPath", cwd=repo)
        lab.g(lab.env, "config", "user.email", lab.mail("acme-id"), cwd=emp)

        # audit
        gl = load(TOOLS / "git_lanes.py", "lane_fx_git_lanes")
        a = gl.audit(repos=[str(emp), str(mine)], home=lab.home, env=lab.env, ancestry=[])
        out.append((CASES[13], a["status"] == "clean" and a["repos_checked"] == 2, json.dumps(a)[:400]))
        lab.g(lab.env, "config", "hook.ws-lane-pre-commit.command", "true", cwd=emp)
        lab.g(lab.env, "config", "hook.ws-lane-pre-push.event", "", cwd=emp)
        lab.g(lab.env, "config", "hook.ws-lane-commit-msg.enabled", "false", cwd=emp)
        a = gl.audit(repos=[str(emp)], home=lab.home, env=lab.env, ancestry=[])
        f = " | ".join(a["findings"])
        out.append((CASES[14], a["status"] == "findings" and "command replaced" in f and "event cleared" in f
                    and "disabled" in f and str(emp) in f, f[:500]))
        with open(lab.home / ".gitconfig", "a", encoding="utf-8") as fh:
            fh.write('[hook "ws-lane-pre-push"]\n\tenabled = false\n')
        a = gl.audit(home=lab.home, env=lab.env, ancestry=[])
        f = " | ".join(a["findings"])
        out.append((CASES[15], a["status"] == "findings" and "global" in f and "outside the lane include" in f, f[:500]))
        gc_path = lab.home / ".gitconfig"
        gc_path.write_text(gc_path.read_text(encoding="utf-8").replace('[hook "ws-lane-pre-push"]\n\tenabled = false\n', ""),
                           encoding="utf-8")

        # residuals
        lab.g(lab.env, "config", "--unset-all", "hook.ws-lane-pre-commit.command", cwd=emp)
        lab.g(lab.env, "config", "--unset-all", "hook.ws-lane-commit-msg.enabled", cwd=emp)
        lab.g(lab.env, "config", "--unset-all", "hook.ws-lane-pre-push.event", cwd=emp)
        for hk in ("pre-commit", "commit-msg"):
            lab.g(lab.env, "config", f"hook.ws-lane-{hk}.event", "", cwd=emp)
        lab.g(lab.env, "config", "user.email", lab.mail("pat"), cwd=emp)
        r = lab.g(lab.env, "commit", "--allow-empty", "-q", "-m", "lane disabled locally", cwd=emp)
        out.append((CASES[16], r.returncode == 0, f"rc={r.returncode} {r.stderr[-200:]}"))
        for hk in ("pre-commit", "commit-msg"):
            lab.g(lab.env, "config", "--unset-all", f"hook.ws-lane-{hk}.event", cwd=emp)
        r1 = lab.g(lab.env, "commit", "--allow-empty", "-q", "--no-verify", "-m", "no-verify", cwd=emp)
        r2 = lab.g(lab.env, "-c", "hook.ws-lane-pre-commit.enabled=false", "-c", "hook.ws-lane-commit-msg.enabled=false",
                   "commit", "--allow-empty", "-q", "-m", "c-disabled", cwd=emp)
        r3 = lab.g(lab.env, "commit", "--allow-empty", "-q", "-m", "still blocked", cwd=emp)
        out.append((CASES[17], r1.returncode == 0 and r2.returncode == 0 and r3.returncode != 0 and "[I1]" in r3.stderr,
                    f"no-verify={r1.returncode} -c={r2.returncode} plain={r3.returncode}"))
        cur_link = lab.base / "lib" / "current"
        cur_link.unlink()
        r = lab.g(lab.env, "commit", "--allow-empty", "-q", "-m", "no pin", cwd=emp)
        cur_link.symlink_to(lab.lib.name)
        out.append((CASES[18], r.returncode == 0, f"rc={r.returncode} {r.stderr[-200:]}"))
        inc_text = (lab.home / ".config" / "snds-workspace" / "git" / "lanes" / "ws-lanes.inc").read_text(encoding="utf-8")
        via_entry = all(f"lane {ev}" in inc_text for ev in ("pre-commit", "commit-msg", "pre-merge-commit", "pre-push",
                                                             "prepare-commit-msg", "post-commit")) and "bin/ws-hook" in inc_text
        wh = lab.base / "bin" / "ws-hook"
        wh_bytes = wh.read_bytes()
        wh.unlink()
        r_nohook = lab.g(lab.env, "commit", "--allow-empty", "-q", "-m", "no ws-hook", cwd=emp)
        wh.write_bytes(wh_bytes)
        wh.chmod(0o755)
        lane_src = lab.lib / "09-tools" / "git_lanes.py"
        good_src = lane_src.read_bytes()
        lane_src.write_text("raise SystemExit(1)\n", encoding="utf-8")
        r_broken = lab.g(lab.env, "commit", "--allow-empty", "-q", "-m", "broken lane module", cwd=emp)
        lane_src.write_bytes(good_src)
        r_back = lab.g(lab.env, "commit", "--allow-empty", "-q", "-m", "lane back", cwd=emp)
        out.append((CASES[24], via_entry and r_nohook.returncode == 0 and r_broken.returncode == 0
                    and "allowing" in r_broken.stderr and r_back.returncode != 0 and "[I1]" in r_back.stderr,
                    f"via={via_entry} no-hook={r_nohook.returncode} broken={r_broken.returncode} "
                    f"{r_broken.stderr[-160:]} back={r_back.returncode}"))
        lab.g(lab.env, "config", "user.email", lab.mail("acme-id"), cwd=emp)

        # in-process (real ancestry input, no ps)
        gl._PR = None
        d = gl.lane_decide("pre-commit", [], [], env=lab.ident(lab.env, "acme-id"), ancestry=[{"comm": "claude"}],
                           root=lab.lib, home=lab.home, cwd=emp)
        out.append((CASES[19], d["decision"] == "block" and d["rule"] == "I2" and d["lane"] == "claude-floor",
                    json.dumps(d)[:300]))
        lab.g(lab.env, "config", "user.email", lab.mail("acme-id"), cwd=mine)
        d = gl.lane_decide("pre-commit", [], [], env=lab.env, ancestry=[], root=lab.lib, home=lab.home, cwd=mine,
                           hostname="host-b", heal=False)
        out.append((CASES[20], d["decision"] == "allow" and any(n.startswith("flag: device mismatch") for n in d["notices"]),
                    json.dumps(d)[:300]))
        lab.g(lab.env, "config", "user.email", lab.mail("pat"), cwd=mine)
        ide = lab.ident(dict(lab.env, CURSOR_AGENT="1", CLAUDE_CODE_SSE_PORT="41234"), "acme-id")
        d = gl.lane_decide("pre-commit", [], [], env=ide, ancestry=[{"comm": "Cursor Helper (Plugin)"}],
                           root=lab.lib, home=lab.home, cwd=emp)
        out.append((CASES[21], d["decision"] == "allow" and d["family"] == "cursor",
                    json.dumps(d)[:300]))

        # budget (reported, never asserted): the whole pre-commit hook process outside the workspace with the
        # fixture's ps stub, plus what a real process-table walk adds on this host.
        del REPORT[:]
        spawn = []
        for _ in range(3):
            t0 = time.monotonic()
            subprocess.run([sys.executable, "-I", "-S", str(lab.lib / "09-tools" / "git_lanes.py"), "hook",
                            "pre-commit"], cwd=str(mine), env=lab.env, capture_output=True, timeout=60)
            spawn.append(round((time.monotonic() - t0) * 1000))
        walk = []
        for _ in range(3):
            t0 = time.monotonic()
            _anc, err = lab.pr._walk_ancestry_ex(None, None, 12)
            walk.append(None if err else round((time.monotonic() - t0) * 1000))
        REPORT.append(f"budget (target 300 ms outside the workspace): pre-commit hook process median "
                      f"{sorted(spawn)[1]} ms of {spawn} with no process-table walk; a real walk adds "
                      f"{walk} ms here (None: ps denied), overlapped with the repo readers")
    finally:
        for d, _dirs, _files in os.walk(td):
            try:
                os.chmod(d, 0o755)
            except OSError:
                pass
        shutil.rmtree(td, ignore_errors=True)
    return out


def run_all() -> list:
    """The H18 lane cases, then the H11 gate cases (gate_cases.py, the same Lab)."""
    gate = load(FX / "gate_cases.py", "lane_fx_gate_cases")
    return lane_cases() + [(f"gate: {n}", p, d) for n, p, d in gate.gate_cases()]


if __name__ == "__main__":
    fails = 0
    for name, passed, detail in run_all():
        mark = "SKIP" if passed is None else ("ok" if passed else "FAIL")
        fails += passed is False
        print(f"{mark:4} {name}\n     {detail}")
    for line in REPORT:
        print(f"info {line}")
    sys.exit(1 if fails else 0)
