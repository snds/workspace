"""Hook-level fixtures for the H17 overlay, identity include and Claude git floor (T8).

Everything runs in temp dirs with a temp HOME: a synthetic pinned lib (copies of this checkout's
ws_hook.py and profile_resolve.py plus the synthetic tables beside this file), the dist ws-hook
wrapper, local bare remotes standing in for the network, and synthetic owners only
(pat-sample personal, acme-corp employer). Nothing touches the real HOME, ~/.gitconfig or a real
checkout under projects_root. Nothing is pushed anywhere but a temp bare repo.

Each case is (name, passed, detail); passed is None for a SKIP (git too old), which callers
report as a skip and never as a pass. Used by `profile_resolve.py --self-test` and by the
TestIdentity, TestOverlay, TestClaudeFloor and TestFloorDecisions classes in test-validators.py.
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
from pathlib import Path

FX = Path(__file__).resolve().parent
ROOT = FX.parents[2]
TOOLS = ROOT / "09-tools"
DIST = ROOT / "00-bootstrap" / "dist"
SCRIPT_REL = "09-tools/fixture-housekeeper.py"
FLOOR = "ws-claude-wall"
HUMAN = {"human": True, "determined": True, "reasons": []}
AGENT = {"human": False, "determined": True, "reasons": ["marker:CURSOR_AGENT"]}
TTY = {"stdin": True, "stdout": True}
HOUSEKEEPER = '''"""Synthetic vetted housekeeper (fixture): one intent line, then one remote branch deletion."""
import json, os, subprocess, sys
repo, branch = sys.argv[1], sys.argv[2]
line = {"type": "intent", "ts": "2026-09-23T00:00:00Z", "pid": os.getpid(), "ppid": os.getppid(),
        "script": "fixture-housekeeper", "script_blob": "fixture", "repo_slug": "acme-corp/widget",
        "action_class": "housekeeping", "action": "remote-branch-delete", "refs": ["refs/heads/" + branch]}
with open(os.path.join(os.environ["HOME"], ".config/snds-workspace/control/receipts.jsonl"), "a") as fh:
    fh.write(json.dumps(line) + "\\n")
r = subprocess.run(["git", "push", "origin", "--delete", branch], cwd=repo, capture_output=True, text=True)
sys.stderr.write(r.stderr)
sys.exit(r.returncode)
'''


def load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    if spec is None or spec.loader is None:
        raise ImportError(rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, mod)
    spec.loader.exec_module(mod)
    return mod


def git_version() -> tuple:
    try:
        out = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.SubprocessError):
        return (0,)
    m = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", out)
    return tuple(int(x) for x in m.groups() if x is not None) if m else (0,)


def tables():
    cr = json.loads((FX / "context-remotes.json").read_text(encoding="utf-8"))
    dev = json.loads((FX / "devices.json").read_text(encoding="utf-8"))
    return cr, dev


class Lab:
    """A temp world: HOME with a pinned lib, a fake workspace, bare remotes and an employer clone."""

    def __init__(self, pr, rs, tmp: Path, *, pin: bool = True, wrapper: bool = True):
        self.pr, self.rs, self.tmp = pr, rs, tmp
        self.home = tmp / "home"
        self.home.mkdir(parents=True, exist_ok=True)
        self.base = self.home / ".config" / "snds-workspace"
        self.ws = tmp / "ws"
        self.cr, self.dev = tables()
        for d in ("control", "telemetry", "git"):
            (self.base / d).mkdir(parents=True, exist_ok=True)
        (self.base / "git" / "claude-identity.inc").write_text(rs.render_claude_identity_inc(self.dev), encoding="utf-8")
        inst = load("00-bootstrap/doctor/installers.py", "installers")
        noident = getattr(inst, "EMPLOYER_NOIDENT_INC", None)
        if noident is not None:
            (self.base / "git" / inst.EMPLOYER_NOIDENT_NAME).write_text(noident, encoding="utf-8")
        self.ws.mkdir(parents=True, exist_ok=True)
        (self.ws / "AGENTS.md").write_text("# fixture workspace\n", encoding="utf-8")
        self.script = self.ws / SCRIPT_REL
        self.script.parent.mkdir(parents=True, exist_ok=True)
        self.script.write_text(HOUSEKEEPER, encoding="utf-8")
        (self.base / "root").write_text(f"{self.ws}\n", encoding="utf-8")
        self.lib = self.base / "lib" / ("a" * 40)
        if pin:
            self._pin()
        if wrapper:
            self.install_wrapper()
        self.base_env = pr._git_env(self.home)

    def _pin(self) -> None:
        tp = self.pr.TABLE_PATHS
        src = {"devices": FX / "devices.json", "context-remotes": FX / "context-remotes.json",
               "surfaces": TOOLS / "fixtures" / "profile_resolve" / "surfaces.json",
               "action-policy": TOOLS / "fixtures" / "action_policy" / "action-policy.json",
               "vetted-scripts": TOOLS / "fixtures" / "action_policy" / "vetted-scripts.json"}
        for name, path in src.items():
            dst = self.lib / tp[name]
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        for mod in ("ws_hook.py", "profile_resolve.py"):
            dst = self.lib / "09-tools" / mod
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(TOOLS / mod, dst)
        lock = {"schema_version": 1, "pinned_sha": "a" * 40,
                "scripts": [{"id": "fixture-housekeeper", "path": SCRIPT_REL, "blob": self.pr.git_blob_sha(self.script)}]}
        (self.lib / "vetted.lock.json").write_text(json.dumps(lock), encoding="utf-8")
        cur = self.base / "lib" / "current"
        if cur.is_symlink() or cur.exists():
            cur.unlink()
        cur.symlink_to(self.lib)

    def install_wrapper(self, body: bytes = b"") -> Path:
        w = self.base / "bin" / "ws-hook"
        w.parent.mkdir(parents=True, exist_ok=True)
        w.write_bytes(body or (DIST / "ws-hook").read_bytes())
        w.chmod(0o755)
        return w

    def overlay(self, *, lifted: bool = False) -> dict:
        """The v5 env exactly as the installer writes it (merge_settings.expand_env_home on this HOME)."""
        ms = load("00-bootstrap/doctor/merge_settings.py", "merge_settings")
        frag = ms.expand_env_home({"env": dict(self.rs.overlay_env(self.cr, self.dev, "v5"))}, self.home)
        env = dict(self.base_env)
        env.update(frag["env"])
        return self.pr.lift_env(env, root=self.lib) if lifted else env

    def g(self, env: dict, *args: str, cwd=None) -> subprocess.CompletedProcess:
        return subprocess.run(["git", *args], cwd=str(cwd) if cwd else None, env=env, capture_output=True, text=True,
                              timeout=120)

    def employer(self, branches=("feat/done",)) -> tuple:
        clone, bare, genv = self.pr._employer_pair(self.tmp, self.home)
        for b in branches:
            if b == "feat/done":
                continue
            self.g(genv, "branch", b, "main", cwd=clone)
            self.g(genv, "push", "-q", "origin", b, cwd=clone)
        self.g(genv, "config", "user.name", "Acme Worker", cwd=clone)
        self.g(genv, "config", "user.email", self.acme_mail(), cwd=clone)
        return clone, bare, genv

    def acme_mail(self) -> str:
        return next(i["email"] for i in self.dev["identities"] if i["id"] == "acme-id")

    def with_ident(self, env: dict) -> dict:
        """An explicit employer identity (env beats config): under the v5 overlay an employer remote gets a
        blank identity (useConfigOnly), so commit cases that must reach the floor carry one explicitly."""
        return dict(env, GIT_AUTHOR_NAME="Acme Worker", GIT_AUTHOR_EMAIL=self.acme_mail(),
                    GIT_COMMITTER_NAME="Acme Worker", GIT_COMMITTER_EMAIL=self.acme_mail())

    def pat_mail(self) -> str:
        return next(i["email"] for i in self.dev["identities"] if i["id"] == "pat")

    def has_ref(self, bare: Path, branch: str) -> bool:
        r = self.g(self.base_env, "--git-dir", str(bare), "show-ref", "--verify", "--quiet", f"refs/heads/{branch}")
        return r.returncode == 0


def _mk(pr, rs, **kw):
    td = tempfile.mkdtemp(prefix="ws-t8-floor-")
    return Lab(pr, rs, Path(os.path.realpath(td)), **kw), td


def _cleanup(td: str) -> None:
    for d, _dirs, _files in os.walk(td):
        try:
            os.chmod(d, 0o755)
        except OSError:
            pass
    shutil.rmtree(td, ignore_errors=True)


def _need(minimum: tuple, names: list) -> list:
    v = git_version()
    if v >= minimum:
        return []
    return [(n, None, f"git {'.'.join(map(str, v))} < {'.'.join(map(str, minimum))}") for n in names]


# --------------------------------------------------------------------------- TestIdentity (hasconfig)

IDENTITY_CASES = ["identity: pat-sample remote gets the include identity (scp, alias, https, ssh forms)",
                  "identity: acme-corp remote never gets the include identity",
                  "identity: identity() reports I1 for a personal identity in an employer repo",
                  "identity: no remote gets no overlay identity",
                  "identity: an employer repo that also has a personal remote gets no personal identity",
                  "identity: cherry-pick and revert on such a repo cannot create a personal-identity commit"]


def identity_cases(pr, rs) -> list:
    skip = _need((2, 36), IDENTITY_CASES)
    if skip:
        return skip
    out = []
    lab, td = _mk(pr, rs, pin=False, wrapper=False)
    try:
        env = lab.overlay()
        env.pop("GIT_CONFIG_GLOBAL", None)
        forms_ok = []
        for i, url in enumerate(("git@github.com:pat-sample/a.git", "git@github-work:pat-sample/a.git",
                                 "https://github.com/pat-sample/a", "ssh://git@github.com/pat-sample/a.git")):
            r = lab.tmp / f"mine-{i}"
            lab.g(lab.base_env, "init", "-q", str(r))
            lab.g(lab.base_env, "remote", "add", "origin", url, cwd=r)
            got = lab.g(env, "config", "--get", "user.email", cwd=r).stdout.strip()
            forms_ok.append(got == lab.pat_mail())
        out.append((IDENTITY_CASES[0], all(forms_ok), str(forms_ok)))
        emp = lab.tmp / "emp"
        lab.g(lab.base_env, "init", "-q", str(emp))
        lab.g(lab.base_env, "remote", "add", "origin", "git@github.com:acme-corp/w.git", cwd=emp)
        got = lab.g(env, "config", "--get", "user.email", cwd=emp).stdout.strip()
        out.append((IDENTITY_CASES[1], got != lab.pat_mail(), got or "(unset)"))
        lab.g(lab.base_env, "config", "user.email", lab.pat_mail(), cwd=emp)
        root = lab.tmp / "tables"
        for name in ("devices", "context-remotes"):
            p = root / pr.TABLE_PATHS[name]
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text((FX / f"{name}.json").read_text(encoding="utf-8"), encoding="utf-8")
        human = {"family": "cursor", "family_for_walls": "cursor", "agent_possible": False, "acting_host": "cursor"}
        res = pr.identity(repo=str(emp), family="cursor", device="dev-a", root=root, env=lab.base_env, home=lab.home,
                          detection=human)
        out.append((IDENTITY_CASES[2], res["invariants_hit"] == ["I1"], json.dumps(res)[:300]))
        none = lab.tmp / "loose"
        lab.g(lab.base_env, "init", "-q", str(none))
        got = lab.g(env, "config", "--get", "user.email", cwd=none).stdout.strip()
        out.append((IDENTITY_CASES[3], got != lab.pat_mail(), got or "(unset)"))
        dual = lab.tmp / "dual"
        lab.g(lab.base_env, "init", "-q", "-b", "main", str(dual))
        lab.g(lab.base_env, "remote", "add", "origin", "git@github.com:acme-corp/w.git", cwd=dual)
        lab.g(lab.base_env, "remote", "add", "fork", "https://github.com/pat-sample/w.git", cwd=dual)
        got = lab.g(env, "config", "--get", "user.email", cwd=dual).stdout.strip()
        out.append((IDENTITY_CASES[4], got != lab.pat_mail(), got or "(unset)"))
        benv = dict(env, GIT_AUTHOR_NAME="Acme Worker", GIT_AUTHOR_EMAIL=lab.acme_mail(),
                    GIT_COMMITTER_NAME="Acme Worker", GIT_COMMITTER_EMAIL=lab.acme_mail())
        for i in range(2):
            (dual / f"f{i}.txt").write_text(f"{i}\n", encoding="utf-8")
            lab.g(benv, "-c", "core.hooksPath=/dev/null", "add", f"f{i}.txt", cwd=dual)
            lab.g(dict(benv, GIT_CONFIG_COUNT="0"), "commit", "-q", "-m", f"c{i}", cwd=dual)
        lab.g(lab.base_env, "switch", "-q", "-c", "side", "HEAD~1", cwd=dual)
        cp = lab.g(env, "cherry-pick", "main", cwd=dual)
        rv = lab.g(env, "revert", "--no-edit", "HEAD", cwd=dual)
        who = {lab.g(lab.base_env, "log", "-1", "--format=%ae|%ce", ref, cwd=dual).stdout.strip()
               for ref in ("HEAD", "side")}
        made_personal = any(lab.pat_mail() in w for w in who)
        out.append((IDENTITY_CASES[5], cp.returncode != 0 and rv.returncode != 0 and not made_personal,
                    f"cherry-pick={cp.returncode} revert={rv.returncode} idents={who} {cp.stderr[-160:]}"))
    finally:
        _cleanup(td)
    return out


# --------------------------------------------------------------------------- TestClaudeFloor (config hooks)

FLOOR_CASES = ["floor: ws-claude-wall listed by git hook list for every floor event under the overlay env",
               "floor: survives a repo-local command override and a repo-local enabled=false",
               "floor: with bin/ws-hook absent a commit proceeds (guarded command)",
               "floor: with the wrapper present and the lib missing the hook exits 0",
               "floor: git passes exactly 2 hook args at pre-push, 1 at commit-msg, 0 at pre-commit"]


def claude_floor_cases(pr, rs) -> list:
    skip = _need((2, 54), FLOOR_CASES)
    if skip:
        return skip
    out = []
    lab, td = _mk(pr, rs)
    try:
        env = lab.with_ident(lab.overlay(lifted=True))
        clone, _bare, _genv = lab.employer()
        listed = {}
        for ev in ("pre-commit", "commit-msg", "pre-merge-commit", "pre-push"):
            listed[ev] = FLOOR in lab.g(env, "hook", "list", ev, cwd=clone).stdout.split()
        out.append((FLOOR_CASES[0], all(listed.values()), str(listed)))
        lab.g(lab.base_env, "config", f"hook.{FLOOR}.command", "exit 0", cwd=clone)
        lab.g(lab.base_env, "config", f"hook.{FLOOR}.enabled", "false", cwd=clone)
        r = lab.g(env, "commit", "--allow-empty", "-m", "should block", cwd=clone)
        out.append((FLOOR_CASES[1], r.returncode != 0 and "[I2]" in r.stderr, f"rc={r.returncode} {r.stderr[-300:]}"))
        lab.g(lab.base_env, "config", "--unset-all", f"hook.{FLOOR}.command", cwd=clone)
        lab.g(lab.base_env, "config", "--unset-all", f"hook.{FLOOR}.enabled", cwd=clone)
        w = lab.base / "bin" / "ws-hook"
        w.unlink()
        r = lab.g(env, "commit", "--allow-empty", "-m", "no pin, proceeds", cwd=clone)
        out.append((FLOOR_CASES[2], r.returncode == 0, f"rc={r.returncode} {r.stderr[-300:]}"))
        lab.install_wrapper()
        (lab.base / "lib" / "current").unlink()
        r = lab.g(env, "commit", "--allow-empty", "-m", "no lib, proceeds", cwd=clone)
        out.append((FLOOR_CASES[3], r.returncode == 0, f"rc={r.returncode} {r.stderr[-300:]}"))
        rec = lab.tmp / "argv.log"
        lab.install_wrapper(("#!/bin/sh\nprintf '%s|' \"$#\" \"$@\" >> '" + str(rec) + "'\necho >> '" + str(rec)
                             + "'\nexit 0\n").encode())
        rec.write_text("", encoding="utf-8")
        lab.g(env, "commit", "--allow-empty", "-m", "argv", cwd=clone)
        lab.g(env, "push", "-q", "origin", "HEAD:refs/heads/feat/argv", cwd=clone)
        lines = [x for x in rec.read_text(encoding="utf-8").splitlines() if x]
        want_push = [ln for ln in lines if ln.startswith("6|--host|git|--floor|claude|origin|")]
        want_msg = [ln for ln in lines if re.match(r"^5\|--host\|git\|--floor\|claude\|[^|]*COMMIT_EDITMSG\|$", ln)]
        want_pre = [ln for ln in lines if ln == "4|--host|git|--floor|claude|"]
        out.append((FLOOR_CASES[4], len(want_push) == 1 and len(want_msg) == 1 and len(want_pre) == 1, str(lines)))
    finally:
        _cleanup(td)
    return out


# --------------------------------------------------------------------------- TestFloorDecisions

DECISION_CASES = ["decisions: a model-composed employer push --delete is blocked with [I2] and the ref survives",
                  "decisions: a rebase-created personal-identity commit is blocked at pre-push with [I1]",
                  "decisions: an uncached personal-looking repo under projects_root is blocked [not-positively-personal]",
                  "decisions: the vetted shape (registered script, pinned blob, intent line) deletes the branch",
                  "bypass: -c hook.ws-claude-wall.enabled=false skips the floor (declared residual)",
                  "bypass: push --no-verify skips the floor (declared residual)",
                  "bypass: commit --no-verify skips the floor (declared residual)",
                  "bypass: GIT_CONFIG_COUNT=0 removes the floor with the overlay (declared residual)",
                  "bypass: classify marks each bypass hook_bypass and the P05 fixture row denies it",
                  "bypass: with the transport block active the same employer push fails at transport, not the floor",
                  "decisions: a bare-mirror push --delete to the employer URL is blocked [I2] and the ref survives",
                  "decisions: a GIT_DIR push to the employer default branch from outside the work tree is blocked [I2]",
                  "decisions: an employer remote seen only through [include], a legacy section or an inline comment "
                  "blocks the commit [I2]",
                  "decisions: a modified copy of the vetted script at the same relative path is not vetted",
                  "decisions: the genuine vetted script run without -I (PYTHONPATH injection possible) is not vetted",
                  "decisions: HOME=<elsewhere> git commit on an employer repo still reaches the floor [I2]",
                  "decisions: PYTHONPATH with a sitecustomize that exits 0 does not silence the floor [I2]",
                  "transport: every declared employer URL form (ssh alias, ports, :/owner, www) is rewritten to the "
                  "blocked scheme; mixed case and ssh.github.com classify employer at the floor",
                  "identity: under the overlay a composed commit on an employer repo has no identity to commit with",
                  "decisions: a Claude commit in a personal linked worktree under projects_root is allowed "
                  "(git exports GIT_DIR to its hooks)",
                  "decisions: a Claude commit in an employer linked worktree is blocked [I2]",
                  "decisions: with the device's employer identity in ~/.gitconfig, a Claude commit in a no-remote "
                  "repo, a third-party repo and a personal repo whose remote form the include misses is blocked [IR1]",
                  "decisions: with the same ~/.gitconfig, a personal repo the include matches commits as the "
                  "personal identity",
                  "bypass: composed local branch deletion and rename on an employer repo reach no floor event "
                  "(declared residual H17-R11)",
                  "bypass: an undeclared-owner repo outside projects_root commits past the floor with a notice "
                  "(declared residual H17-R12)",
                  "decisions: with the device's employer identity in ~/.gitconfig, a Claude revert in a personal repo "
                  "whose remote form the include misses records it, and the Claude push of it is blocked [IR1]",
                  "decisions: with the same ~/.gitconfig, a Claude push of personal-identity commits to a personal "
                  "remote is allowed",
                  "decisions: a Claude pre-push to a personal remote whose range git cannot read allows with the IR1 "
                  "notice",
                  "decisions: a Claude commit in a linked worktree outside projects_root of a cached personal checkout "
                  "under it is allowed",
                  "decisions: a Claude commit in a linked worktree outside projects_root of an unknown-owner checkout "
                  "under it is blocked [not-positively-personal]",
                  "decisions: a Claude commit in a linked worktree outside projects_root of a checkout under it that "
                  "matches an employer path glob is blocked [I2]",
                  "decisions: a linked worktree's admin dir used as GIT_DIR from another cwd locates that worktree",
                  "decisions: a Claude push of an annotated tag whose tagger is the employer identity is blocked "
                  "[IR1]; the same tag with the personal tagger pushes",
                  "decisions: scan records bare repos under projects_root, so a Claude commit in a personal bare "
                  "repo's linked worktree is allowed and one in an employer bare repo's worktree stays blocked [I2]",
                  "decisions: a Claude push to a personal fork of a branch carrying an upstream commit with an "
                  "employer author stays blocked [IR1], and the reason names the upstream remote it is already on",
                  "decisions: a --relative-paths linked worktree's admin dir used as GIT_DIR from another cwd locates "
                  "that worktree, and its relative gitdir file is listed among the workspace's worktrees",
                  "decisions: a Claude cherry-pick of a personal-authored commit records the employer identity as "
                  "committer only, and the push of it is blocked [IR1] on the committer",
                  "decisions: a Claude commit in a cached personal linked worktree under projects_root whose main "
                  "checkout is uncached is blocked [not-positively-personal] (both must be positively personal)",
                  "decisions: an annotated tag chain longer than the floor reads is blocked [IR1] (never fail-open on a crafted chain)",
                  "decisions: an unreadable tag never switches off the commit identity check (_push_idents keeps the commit part)"]
VETTED_CASES = (DECISION_CASES[3], DECISION_CASES[13], DECISION_CASES[14])


def ps_permitted() -> bool:
    """The vetted shape is proven from the process table; a sandbox that denies `ps` cannot prove it."""
    try:
        r = subprocess.run(["ps", "-A", "-o", "pid="], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0 and bool(r.stdout.strip())


def floor_decision_cases(pr, rs) -> list:
    skip = _need((2, 54), DECISION_CASES)
    if skip:
        return skip
    out = []
    lab, td = _mk(pr, rs)
    try:
        lifted = lab.overlay(lifted=True)
        full = lab.overlay()
        clone, bare, genv = lab.employer(("feat/done", "feat/b1", "feat/b2", "feat/b4", "feat/m1", "feat/col",
                                          "feat/col2"))
        ps_ok = ps_permitted()
        r = lab.g(lifted, "push", "origin", "--delete", "feat/done", cwd=clone)
        out.append((DECISION_CASES[0], r.returncode != 0 and "[I2]" in r.stderr and lab.has_ref(bare, "feat/done"),
                    f"rc={r.returncode} {r.stderr[-300:]}"))
        lab.g(genv, "switch", "-q", "-c", "feat/r", "main", cwd=clone)
        lab.g(genv, "commit", "-q", "--allow-empty", "-m", "employer work", cwd=clone)
        lab.g(genv, "commit", "-q", "--allow-empty", "-m", "base moves", cwd=clone)
        rb = lab.g(dict(lifted), "-c", f"user.email={lab.pat_mail()}", "-c", "user.name=Pat Sample",
                   "rebase", "-q", "--force-rebase", "main", cwd=clone)
        who = lab.g(genv, "log", "-1", "--format=%ce", cwd=clone).stdout.strip()
        r = lab.g(lifted, "push", "origin", "feat/r", cwd=clone)
        out.append((DECISION_CASES[1], rb.returncode == 0 and who == lab.pat_mail() and r.returncode != 0
                    and "[I1]" in r.stderr, f"rebase={rb.returncode} committer={who} push={r.returncode} {r.stderr[-300:]}"))
        lab.g(genv, "switch", "-q", "main", cwd=clone)
        mine = lab.home / "Projects" / "looks-mine"
        lab.g(genv, "init", "-q", str(mine))
        lab.g(genv, "remote", "add", "origin", "git@github.com:pat-sample/looks-mine.git", cwd=mine)
        r = lab.g(lifted, "commit", "--allow-empty", "-m", "x", cwd=mine)
        out.append((DECISION_CASES[2], r.returncode != 0 and "[not-positively-personal]" in r.stderr
                    and "scan" in r.stderr, f"rc={r.returncode} {r.stderr[-300:]}"))
        py = shutil.which("python3") or sys.executable
        if ps_ok:
            v = subprocess.run([py, "-I", str(lab.script), str(clone), "feat/done"], env=lifted, capture_output=True,
                               text=True, timeout=120)
            out.append((DECISION_CASES[3], v.returncode == 0 and not lab.has_ref(bare, "feat/done"),
                        f"rc={v.returncode} {v.stderr[-400:]}"))
        else:
            out.append((DECISION_CASES[3], None, "ps not permitted (sandbox): the vetted shape cannot be proven here"))
        r = lab.g(lifted, "-c", f"hook.{FLOOR}.enabled=false", "push", "origin", "--delete", "feat/b1", cwd=clone)
        out.append((DECISION_CASES[4], r.returncode == 0 and not lab.has_ref(bare, "feat/b1") and FLOOR not in r.stderr,
                    f"rc={r.returncode} {r.stderr[-200:]}"))
        r = lab.g(lifted, "push", "--no-verify", "origin", "--delete", "feat/b2", cwd=clone)
        out.append((DECISION_CASES[5], r.returncode == 0 and not lab.has_ref(bare, "feat/b2"),
                    f"rc={r.returncode} {r.stderr[-200:]}"))
        r = lab.g(lab.with_ident(lifted), "commit", "--no-verify", "--allow-empty", "-m", "bypass", cwd=clone)
        out.append((DECISION_CASES[6], r.returncode == 0, f"rc={r.returncode} {r.stderr[-200:]}"))
        stripped = dict(lifted, GIT_CONFIG_COUNT="0")
        r = lab.g(stripped, "commit", "--allow-empty", "-m", "env removed", cwd=clone)
        out.append((DECISION_CASES[7], r.returncode == 0 and FLOOR not in r.stderr, f"rc={r.returncode}"))
        cmds = [f"git -c hook.{FLOOR}.enabled=false push origin --delete feat/x", "git push --no-verify origin main",
                "git commit --no-verify -m x", "GIT_CONFIG_COUNT=0 git push origin main"]
        root = lab.tmp / "policy-root"
        for name in ("devices", "context-remotes"):
            p = root / pr.TABLE_PATHS[name]
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text((FX / f"{name}.json").read_text(encoding="utf-8"), encoding="utf-8")
        for name, src in (("surfaces", TOOLS / "fixtures" / "profile_resolve" / "surfaces.json"),
                          ("action-policy", TOOLS / "fixtures" / "action_policy" / "action-policy.json"),
                          ("vetted-scripts", TOOLS / "fixtures" / "action_policy" / "vetted-scripts.json")):
            p = root / pr.TABLE_PATHS[name]
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        det = {"family": "claude", "family_for_walls": "claude", "agent_possible": True, "acting_host": "claude-code"}
        verdicts = []
        for c in cmds:
            inv = pr.classify_command(c, cwd=str(clone), root=root, detection=det, home=lab.home)
            pol = pr.policy(repo=str(clone), command=c, root=root, home=lab.home, detection=det, device="dev-a",
                            record=False)
            verdicts.append((inv[0]["hook_bypass"], pol["outcome"], pol["rule_id"]))
        out.append((DECISION_CASES[8], all(b and o == "deny" and str(rid).startswith("P05") for b, o, rid in verdicts),
                    str(verdicts)))
        r1 = lab.g(full, "push", "origin", "--delete", "feat/b4", cwd=clone)
        r2 = lab.g(full, "-c", f"hook.{FLOOR}.enabled=false", "push", "origin", "--delete", "feat/b4", cwd=clone)
        scheme = str(lab.cr["blocked_scheme"]).split("://", 1)[0]
        out.append((DECISION_CASES[9], r1.returncode != 0 and r2.returncode != 0 and lab.has_ref(bare, "feat/b4")
                    and FLOOR not in r1.stderr and scheme in r1.stderr + r2.stderr,
                    f"{r1.returncode}/{r2.returncode} {r1.stderr[-200:]}"))
        emp_url = "git@github.com:acme-corp/widget.git"
        nowhere = lab.tmp / "nowhere"
        nowhere.mkdir(exist_ok=True)
        mirror = lab.tmp / "mirror.git"
        lab.g(genv, "clone", "-q", "--bare", str(bare), str(mirror))
        r = lab.g(lifted, "--git-dir", str(mirror), "push", emp_url, "--delete", "feat/m1", cwd=nowhere)
        out.append((DECISION_CASES[10], r.returncode != 0 and "[I2]" in r.stderr and lab.has_ref(bare, "feat/m1"),
                    f"rc={r.returncode} {r.stderr[-300:]}"))
        before = lab.g(genv, "--git-dir", str(bare), "rev-parse", "refs/heads/main").stdout.strip()
        lab.g(genv, "commit", "-q", "--allow-empty", "-m", "employer default push", cwd=clone)
        r = lab.g(dict(lifted, GIT_DIR=str(clone / ".git")), "push", emp_url, "HEAD:refs/heads/main", cwd=nowhere)
        after = lab.g(genv, "--git-dir", str(bare), "rev-parse", "refs/heads/main").stdout.strip()
        out.append((DECISION_CASES[11], r.returncode != 0 and "[I2]" in r.stderr and before == after,
                    f"rc={r.returncode} {r.stderr[-300:]}"))
        shapes = {"include": None, "legacy": "[remote.origin]\n\turl = git@github.com:acme-corp/w.git\n",
                  "comment": '[remote "origin"]\n\turl = git@github.com:acme-corp/w.git ; a note\n'}
        got = {}
        for name, text in shapes.items():
            rp = lab.tmp / f"shape-{name}"
            lab.g(genv, "init", "-q", str(rp))
            cfg = rp / ".git" / "config"
            if name == "include":
                inc = lab.tmp / "shape-include.inc"
                inc.write_text('[remote "origin"]\n\turl = git@github.com:acme-corp/w.git\n', encoding="utf-8")
                text = f"[include]\n\tpath = {inc}\n"
            with open(cfg, "a", encoding="utf-8") as fh:
                fh.write(text)
            seen = lab.g(genv, "config", "--get", "remote.origin.url", cwd=rp).stdout.strip()
            r = lab.g(lab.with_ident(lifted), "commit", "--allow-empty", "-m", "x", cwd=rp)
            got[name] = (seen == "git@github.com:acme-corp/w.git", r.returncode, "[I2]" in r.stderr)
        out.append((DECISION_CASES[12], all(s and rc != 0 and hit for s, rc, hit in got.values()), str(got)))
        if ps_ok:
            evil = lab.tmp / "evil"
            copy = evil / SCRIPT_REL
            copy.parent.mkdir(parents=True, exist_ok=True)
            copy.write_text(HOUSEKEEPER + "# modified copy\n", encoding="utf-8")
            v = subprocess.run([py, "-I", SCRIPT_REL, str(clone), "feat/col"], cwd=str(evil), env=lifted,
                               capture_output=True, text=True, timeout=120)
            out.append((DECISION_CASES[13], v.returncode != 0 and lab.has_ref(bare, "feat/col")
                        and "wall: vetted housekeeping" not in v.stderr, f"rc={v.returncode} {v.stderr[-300:]}"))
            inj = lab.tmp / "inject"
            inj.mkdir(exist_ok=True)
            v = subprocess.run([py, str(lab.script), str(clone), "feat/col2"], env=dict(lifted, PYTHONPATH=str(inj)),
                               capture_output=True, text=True, timeout=120)
            out.append((DECISION_CASES[14], v.returncode != 0 and lab.has_ref(bare, "feat/col2")
                        and "wall: vetted housekeeping" not in v.stderr, f"rc={v.returncode} {v.stderr[-300:]}"))
        else:
            for n in VETTED_CASES[1:]:
                out.append((n, None, "ps not permitted (sandbox): the vetted shape cannot be proven here"))
        fake_home = lab.tmp / "fake-home"
        fake_home.mkdir(exist_ok=True)
        r = lab.g(lab.with_ident(dict(lifted, HOME=str(fake_home))), "commit", "--allow-empty", "-m", "home override",
                  cwd=clone)
        out.append((DECISION_CASES[15], r.returncode != 0 and "[I2]" in r.stderr, f"rc={r.returncode} {r.stderr[-300:]}"))
        site = lab.tmp / "site-inject"
        site.mkdir(exist_ok=True)
        (site / "sitecustomize.py").write_text("import os\nos._exit(0)\n", encoding="utf-8")
        r = lab.g(lab.with_ident(dict(lifted, PYTHONPATH=str(site))), "commit", "--allow-empty", "-m", "site inject",
                  cwd=clone)
        out.append((DECISION_CASES[16], r.returncode != 0 and "[I2]" in r.stderr, f"rc={r.returncode} {r.stderr[-300:]}"))
        forms = ["ssh://git@github-work/acme-corp/w.git", "ssh://github-work/acme-corp/w.git",
                 "ssh://git@github.com:22/acme-corp/w.git", "https://github.com:443/acme-corp/w",
                 "git@github.com:/acme-corp/w.git", "ssh://git@ssh.github.com:443/acme-corp/w.git",
                 "https://www.github.com/acme-corp/w", "git@github.com:ACME-CORP/w.git", "ssh://github.com/acme-corp/w"]
        bl = str(lab.cr["blocked_scheme"])
        miss = [u for u in forms if not lab.g(full, "ls-remote", "--get-url", u).stdout.strip().startswith(bl)]
        floor_cls = {u: pr._push_url_class(u, lab.lib) for u in ("https://github.com/AcMe-CoRp/w",
                                                                 "ssh://git@ssh.github.com:443/acme-corp/w.git",
                                                                 "https://www.github.com/acme-corp/w")}
        out.append((DECISION_CASES[17], not miss and all(c == "employer" for c in floor_cls.values()),
                    f"not rewritten: {miss} floor: {floor_cls}"))
        r = lab.g(lifted, "commit", "--allow-empty", "-m", "no identity", cwd=clone)
        out.append((DECISION_CASES[18], r.returncode != 0 and lab.g(lifted, "config", "--get", "user.email",
                                                                    cwd=clone).stdout.strip() == "",
                    f"rc={r.returncode} {r.stderr[-200:]}"))
        # Linked worktrees: git exports GIT_DIR=<main>/.git/worktrees/<name> to every hook it runs there.
        root_file = lab.base / "root"
        saved_root = root_file.read_text(encoding="utf-8")
        try:
            ws2 = lab.home / "Projects" / "workspace"
            ws2.mkdir(parents=True, exist_ok=True)
            (ws2 / "AGENTS.md").write_text("# fixture workspace (worktree case)\n", encoding="utf-8")
            lab.g(genv, "init", "-q", "-b", "main", str(ws2))
            lab.g(genv, "remote", "add", "origin", "https://github.com/pat-sample/ws.git", cwd=ws2)
            root_file.write_text(f"{ws2}\n", encoding="utf-8")
            base_c = lab.g(lifted, "commit", "--allow-empty", "-m", "main checkout", cwd=ws2)
            wt = lab.home / "Projects" / "workspace.intent-t1"
            lab.g(genv, "worktree", "add", "-q", "-b", "intent/t1", str(wt), cwd=ws2)
            r = lab.g(lifted, "commit", "--allow-empty", "-m", "worktree commit", cwd=wt)
            out.append((DECISION_CASES[19], base_c.returncode == 0 and r.returncode == 0 and FLOOR not in r.stderr,
                        f"main={base_c.returncode} worktree={r.returncode} {r.stderr[-300:]}"))
        finally:
            root_file.write_text(saved_root, encoding="utf-8")
        ewt = lab.tmp / "emp-wt"
        lab.g(genv, "worktree", "add", "-q", "-b", "feat/wt", str(ewt), "main", cwd=clone)
        r = lab.g(lab.with_ident(lifted), "commit", "--allow-empty", "-m", "employer worktree", cwd=ewt)
        out.append((DECISION_CASES[20], ewt.is_dir() and r.returncode != 0 and "[I2]" in r.stderr,
                    f"rc={r.returncode} {r.stderr[-300:]}"))
        # IR1: the device default identity (IR2 on an employer-default device) never reaches a Claude commit.
        gc = lab.home / ".gitconfig"
        gc.write_text(f"[user]\n\tname = Acme Worker\n\temail = {lab.acme_mail()}\n", encoding="utf-8")
        try:
            got = {}
            for name, url in (("no-remote", None), ("third-party", "https://github.com/oss-upstream/lib.git"),
                              ("personal-www", "https://www.github.com/pat-sample/x"),
                              ("personal-scp", "git@github.com:pat-sample/x.git")):
                rp = lab.tmp / f"ir1-{name}"
                lab.g(genv, "init", "-q", "-b", "main", str(rp))
                if url:
                    lab.g(genv, "remote", "add", "origin", url, cwd=rp)
                r = lab.g(lifted, "commit", "--allow-empty", "-m", "claude commit", cwd=rp)
                who = lab.g(genv, "log", "-1", "--format=%ae|%ce", cwd=rp).stdout.strip() if r.returncode == 0 else ""
                got[name] = (r.returncode, "[IR1]" in r.stderr, who)
            blocked = all(got[n][0] != 0 and got[n][1] for n in ("no-remote", "third-party", "personal-www"))
            out.append((DECISION_CASES[21], blocked, str(got)))
            mine = got["personal-scp"]
            out.append((DECISION_CASES[22], mine[0] == 0 and mine[2] == f"{lab.pat_mail()}|{lab.pat_mail()}", str(got)))
        finally:
            gc.unlink()
        lab.g(genv, "branch", "feat/r11", "main", cwd=clone)
        mv = lab.g(full, "branch", "-m", "feat/r11", "feat/r11b", cwd=clone)
        rm = lab.g(full, "branch", "-D", "feat/r11b", cwd=clone)
        out.append((DECISION_CASES[23], mv.returncode == 0 and rm.returncode == 0 and FLOOR not in mv.stderr + rm.stderr,
                    f"-m {mv.returncode} -D {rm.returncode} {rm.stderr[-200:]}"))
        und = lab.tmp / "undeclared"
        lab.g(genv, "init", "-q", "-b", "main", str(und))
        lab.g(genv, "remote", "add", "origin", "https://github.com/someone-else/tool.git", cwd=und)
        penv = dict(lifted, GIT_AUTHOR_NAME="Pat Sample", GIT_AUTHOR_EMAIL=lab.pat_mail(),
                    GIT_COMMITTER_NAME="Pat Sample", GIT_COMMITTER_EMAIL=lab.pat_mail())
        r = lab.g(penv, "commit", "--allow-empty", "-m", "outside code", cwd=und)
        out.append((DECISION_CASES[24], r.returncode == 0 and "outside projects_root; the floor allows it" in r.stderr,
                    f"rc={r.returncode} {r.stderr[-200:]}"))
        out += _ir1_push_cases(lab, pr, lifted)
        out += _outside_worktree_cases(lab, pr, penv)
        out += _bare_worktree_cases(lab, pr, penv)
        out += _uncached_main_cases(lab, pr, penv)
    finally:
        _cleanup(td)
    return out


def _ir1_push_cases(lab: Lab, pr, lifted: dict) -> list:
    """IR1 at pre-push (W-06): revert, cherry-pick, rebase and am make commits that no commit hook sees, so the
    push to a non-employer remote reads the pushed range. The local bare remotes stand in for the network."""
    out = []
    bare_root = lab.tmp / "remotes"
    gc = lab.home / ".gitconfig"
    # The overlay rewrites personal scp and ssh forms to https, so the stand-in maps the https forms.
    gc.write_text(f'[url "file://{bare_root}/"]\n\tinsteadOf = https://www.github.com/\n'
                  '\tinsteadOf = https://github.com/\n'
                  f"[user]\n\tname = Acme Worker\n\temail = {lab.acme_mail()}\n", encoding="utf-8")
    pat = dict(lab.base_env, GIT_AUTHOR_NAME="Pat Sample", GIT_AUTHOR_EMAIL=lab.pat_mail(),
               GIT_COMMITTER_NAME="Pat Sample", GIT_COMMITTER_EMAIL=lab.pat_mail())
    try:
        repos = {}
        for name, url in (("www", "https://www.github.com/pat-sample/ir1-www.git"),
                          ("https", "https://github.com/pat-sample/ir1-https.git")):
            bare = bare_root / "pat-sample" / f"ir1-{name}.git"
            lab.g(lab.base_env, "init", "-q", "--bare", "-b", "main", str(bare))
            rp = lab.tmp / f"ir1-push-{name}"
            lab.g(pat, "init", "-q", "-b", "main", str(rp))
            lab.g(pat, "remote", "add", "origin", url, cwd=rp)
            for i in range(2):
                (rp / "f.txt").write_text("a\n" * (i + 1), encoding="utf-8")
                lab.g(pat, "add", "f.txt", cwd=rp)
                lab.g(pat, "commit", "-q", "-m", f"seed {i}", cwd=rp)
            lab.g(pat, "push", "-q", "origin", "main", cwd=rp)
            repos[name] = (rp, bare, url)

        def tip(bare: Path) -> str:
            return lab.g(lab.base_env, "--git-dir", str(bare), "rev-parse", "refs/heads/main").stdout.strip()

        rp, bare, _url = repos["www"]
        before = tip(bare)
        rv = lab.g(lifted, "revert", "--no-edit", "HEAD", cwd=rp)
        who = lab.g(lab.base_env, "log", "-1", "--format=%ae|%ce", cwd=rp).stdout.strip()
        r = lab.g(lifted, "push", "origin", "main", cwd=rp)
        out.append((DECISION_CASES[25], rv.returncode == 0 and lab.acme_mail() in who and r.returncode != 0
                    and "[IR1]" in r.stderr and tip(bare) == before,
                    f"revert={rv.returncode} idents={who} push={r.returncode} {r.stderr[-300:]}"))
        rp, bare, url = repos["https"]
        c = lab.g(lifted, "commit", "--allow-empty", "-m", "claude commit", cwd=rp)
        head = lab.g(lab.base_env, "rev-parse", "HEAD", cwd=rp).stdout.strip()
        who = lab.g(lab.base_env, "log", "-1", "--format=%ae|%ce", cwd=rp).stdout.strip()
        r = lab.g(lifted, "push", "origin", "main", cwd=rp)
        out.append((DECISION_CASES[26], c.returncode == 0 and who == f"{lab.pat_mail()}|{lab.pat_mail()}"
                    and r.returncode == 0 and tip(bare) == head, f"commit={c.returncode} idents={who} "
                    f"push={r.returncode} {r.stderr[-300:]}"))
        line = f"refs/heads/main {'f' * 40} refs/heads/main {'0' * 40}"
        v = pr.floor_decide("pre-push", ["origin", url], [line], env=lifted, root=lab.lib, home=lab.home, cwd=str(rp))
        out.append((DECISION_CASES[27], v["decision"] == "allow" and "IR1 range check unavailable" in str(v["notice"]),
                    str(v)))
        # W3-01: an annotated tag carries its own tagger identity, and `git tag` runs no hook. The tag points at a
        # commit origin already has, so the commit range is empty and only the tagger check can refuse it.
        rp, bare, _url = repos["www"]
        base = tip(bare)
        tg = lab.g(lifted, "tag", "-a", "v-emp", "-m", "employer tagger", base, cwd=rp)
        tagger = lab.g(lab.base_env, "for-each-ref", "--format=%(taggeremail)", "refs/tags/v-emp", cwd=rp).stdout
        r = lab.g(lifted, "push", "origin", "refs/tags/v-emp", cwd=rp)
        landed = lab.g(lab.base_env, "--git-dir", str(bare), "show-ref", "--verify", "--quiet", "refs/tags/v-emp")
        lab.g(pat, "tag", "-a", "v-pat", "-m", "personal tagger", base, cwd=rp)
        pp = lab.g(lifted, "push", "origin", "refs/tags/v-pat", cwd=rp)
        out.append((DECISION_CASES[32], tg.returncode == 0 and lab.acme_mail() in tagger and r.returncode != 0
                    and "[IR1]" in r.stderr and "tagger" in r.stderr and landed.returncode != 0
                    and pp.returncode == 0, f"tag={tg.returncode} tagger={tagger.strip()} push={r.returncode} "
                    f"landed={landed.returncode == 0} personal={pp.returncode} {r.stderr[-300:]} {pp.stderr[-200:]}"))
        # Review fix: a tag chain past the reader's limit blocks, and a tag read failure leaves the commit check on.
        prev = "v-pat"
        for k in range(pr._TAG_CHAIN_MAX + 1):
            lab.g(pat, "tag", "-a", f"deep-{k}", "-m", "chain", prev, cwd=rp)
            prev = f"deep-{k}"
        dr = lab.g(lifted, "push", "origin", f"refs/tags/{prev}", cwd=rp)
        dlanded = lab.g(lab.base_env, "--git-dir", str(bare), "show-ref", "--verify", "--quiet", f"refs/tags/{prev}")
        out.append((DECISION_CASES[38], dr.returncode != 0 and "[IR1]" in dr.stderr and "longer than" in dr.stderr
                    and dlanded.returncode != 0, f"push={dr.returncode} landed={dlanded.returncode == 0} {dr.stderr[-300:]}"))
        saved_rng, saved_tag = pr._range_idents, pr._tag_taggers
        try:
            pr._range_idents = lambda *a, **k: [("c" * 40, "a@x.invalid", "b@x.invalid")]
            pr._tag_taggers = lambda *a, **k: None
            got, tags_ok = pr._push_idents(rp, {"local_sha": "c" * 40}, "origin", {}, "git")
        finally:
            pr._range_idents, pr._tag_taggers = saved_rng, saved_tag
        out.append((DECISION_CASES[39], got is not None and not tags_ok
                    and [(k, r) for k, _s, r, _e in got] == [("commit", "author"), ("commit", "committer")], f"{got} {tags_ok}"))
        # TR3-02: cherry-pick keeps the author and records the committer from config, so the author is personal and
        # only the committer is the employer identity; the push must be refused on the committer alone.
        lab.g(pat, "switch", "-q", "-c", "pick-src", base, cwd=rp)
        (rp / "picked.txt").write_text("picked\n", encoding="utf-8")
        lab.g(pat, "add", "picked.txt", cwd=rp)
        lab.g(pat, "commit", "-q", "-m", "personal work to pick", cwd=rp)
        lab.g(pat, "switch", "-q", "-c", "picked", base, cwd=rp)
        cp = lab.g(lifted, "cherry-pick", "pick-src", cwd=rp)
        who = lab.g(lab.base_env, "log", "-1", "--format=%ae|%ce", cwd=rp).stdout.strip()
        r = lab.g(lifted, "push", "origin", "picked", cwd=rp)
        landed = lab.g(lab.base_env, "--git-dir", str(bare), "show-ref", "--verify", "--quiet", "refs/heads/picked")
        out.append((DECISION_CASES[36], cp.returncode == 0 and who == f"{lab.pat_mail()}|{lab.acme_mail()}"
                    and r.returncode != 0 and "[IR1]" in r.stderr and "as committer" in r.stderr
                    and landed.returncode != 0,
                    f"cherry-pick={cp.returncode} idents={who} push={r.returncode} {r.stderr[-300:]}"))
        # W3-03: fork workflow. The upstream (third-party) history holds a commit an employer identity authored; a
        # branch on top of it pushed to the personal fork would publish it there. Remote-tracking refs are local and
        # forgeable, so the floor keeps blocking, and the reason says where the commit already is.
        acme = dict(lab.base_env, GIT_AUTHOR_NAME="Acme Worker", GIT_AUTHOR_EMAIL=lab.acme_mail(),
                    GIT_COMMITTER_NAME="Acme Worker", GIT_COMMITTER_EMAIL=lab.acme_mail())
        up_bare = bare_root / "oss-upstream" / "lib.git"
        fork_bare = bare_root / "pat-sample" / "lib.git"
        for b in (up_bare, fork_bare):
            lab.g(lab.base_env, "init", "-q", "--bare", "-b", "main", str(b))
        seed = lab.tmp / "upstream-seed"
        lab.g(acme, "init", "-q", "-b", "main", str(seed))
        lab.g(acme, "commit", "-q", "--allow-empty", "-m", "upstream work by an employer author", cwd=seed)
        lab.g(acme, "push", "-q", f"file://{up_bare}", "main", cwd=seed)
        fork = lab.tmp / "fork-clone"
        lab.g(pat, "init", "-q", "-b", "main", str(fork))
        lab.g(pat, "remote", "add", "origin", "https://github.com/pat-sample/lib.git", cwd=fork)
        lab.g(pat, "remote", "add", "upstream", "https://github.com/oss-upstream/lib.git", cwd=fork)
        lab.g(pat, "fetch", "-q", "upstream", cwd=fork)
        lab.g(pat, "switch", "-q", "-c", "feat/fork", "upstream/main", cwd=fork)
        lab.g(pat, "commit", "-q", "--allow-empty", "-m", "my change on the fork", cwd=fork)
        r = lab.g(lifted, "push", "origin", "feat/fork", cwd=fork)
        landed = lab.g(lab.base_env, "--git-dir", str(fork_bare), "show-ref", "--verify", "--quiet",
                       "refs/heads/feat/fork")
        out.append((DECISION_CASES[34], r.returncode != 0 and "[IR1]" in r.stderr and landed.returncode != 0
                    and "already on remote 'upstream'" in r.stderr and "rewrite it" not in r.stderr,
                    f"push={r.returncode} landed={landed.returncode == 0} {r.stderr[-400:]}"))
    finally:
        gc.unlink()
    return out


def _outside_worktree_cases(lab: Lab, pr, penv: dict) -> list:
    """W-07: a linked worktree outside projects_root counts as its main checkout under it (cache-only rule and
    employer path globs included). The fixture table's globs include '*acme*'."""
    out = []
    pat = dict(lab.base_env, GIT_AUTHOR_NAME="Pat Sample", GIT_AUTHOR_EMAIL=lab.pat_mail(),
               GIT_COMMITTER_NAME="Pat Sample", GIT_COMMITTER_EMAIL=lab.pat_mail())
    cache = pr.ws_paths(home=lab.home)["telemetry"] / "checkouts.json"
    rows = []
    got = {}
    try:
        for name, url, cached in (("wt-mine", "git@github.com:pat-sample/wt-mine.git", "personal"),
                                  ("wt-tool", "https://github.com/someone-else/tool.git", None),
                                  ("acme-ds", "https://github.com/someone-else/ds.git", "employer")):
            main = lab.home / "Projects" / name
            lab.g(pat, "init", "-q", "-b", "main", str(main))
            lab.g(pat, "remote", "add", "origin", url, cwd=main)
            lab.g(pat, "commit", "-q", "--allow-empty", "-m", "seed", cwd=main)
            wt = lab.tmp / f"{name}-outside-wt"
            lab.g(pat, "worktree", "add", "-q", "-b", "wt-outside", str(wt), cwd=main)
            norm = pr.normalize_remote(url, root=lab.lib)
            if cached:
                rows.append({"path": str(main), "kind": "repo", "owner_class": cached, "default_branch": None,
                             "remotes": [{"name": "origin", "form": norm["form"], "host": norm["host"],
                                          "slug": norm["slug"]}]})
            got[name] = (main, wt)
        cache.write_text(json.dumps({"schema_version": 1, "device": "dev-a", "generated_at": "2026-09-23T00:00:00Z",
                                     "generated_by": "human", "projects_root": str(lab.home / "Projects"),
                                     "checkouts": rows}), encoding="utf-8")
        res = {}
        for name, (_main, wt) in got.items():
            r = lab.g(penv, "commit", "--allow-empty", "-m", "claude worktree commit", cwd=wt)
            res[name] = (r.returncode, r.stderr.strip().splitlines()[-1:] if r.stderr.strip() else [])
        mine, tool, ds = res["wt-mine"], res["wt-tool"], res["acme-ds"]
        out.append((DECISION_CASES[28], mine[0] == 0 and "blocked" not in str(mine[1]), str(mine)))
        out.append((DECISION_CASES[29], tool[0] != 0 and "[not-positively-personal]" in str(tool[1]), str(tool)))
        out.append((DECISION_CASES[30], ds[0] != 0 and "[I2]" in str(ds[1]), str(ds)))
        main, wt = got["wt-tool"]
        admin = main / ".git" / "worktrees" / wt.name
        elsewhere = lab.tmp / "elsewhere-cwd"
        elsewhere.mkdir(exist_ok=True)
        gd, top = pr._floor_locate(elsewhere, dict(lab.base_env, GIT_DIR=str(admin)), "git")
        out.append((DECISION_CASES[31], gd is not None and top is not None
                    and os.path.realpath(top) == os.path.realpath(wt), f"gitdir={gd} top={top}"))
        # W3-04: with --relative-paths both gitdir files hold relative paths (the admin dir's is relative to
        # the admin dir, the worktree's .git file to the worktree).
        rwt = lab.tmp / "wt-tool-relative"
        add = lab.g(pat, "worktree", "add", "-q", "--relative-paths", "-b", "wt-rel", str(rwt), cwd=main)
        radmin = main / ".git" / "worktrees" / rwt.name
        named = (radmin / "gitdir").read_text(encoding="utf-8").strip() if (radmin / "gitdir").is_file() else ""
        gd, top = pr._floor_locate(elsewhere, dict(lab.base_env, GIT_DIR=str(radmin)), "git")
        listed = [os.path.realpath(p) for p in pr._linked_worktrees(main)]
        out.append((DECISION_CASES[35], add.returncode == 0 and not os.path.isabs(named) and top is not None
                    and os.path.realpath(top) == os.path.realpath(rwt) and os.path.realpath(rwt) in listed,
                    f"add={add.returncode} named={named} gitdir={gd} top={top} listed={listed}"))
    finally:
        if cache.exists():
            cache.unlink()
    return out


def _uncached_main_cases(lab: Lab, pr, penv: dict) -> list:
    """TR3-03: a linked worktree is positively personal only when it AND its main checkout are. Here the
    worktree itself is cached personal and the main checkout (same personal remote) is a cache miss, so
    only the AND refuses it; an OR would allow."""
    out = []
    pat = dict(lab.base_env, GIT_AUTHOR_NAME="Pat Sample", GIT_AUTHOR_EMAIL=lab.pat_mail(),
               GIT_COMMITTER_NAME="Pat Sample", GIT_COMMITTER_EMAIL=lab.pat_mail())
    cache = pr.ws_paths(home=lab.home)["telemetry"] / "checkouts.json"
    try:
        url = "git@github.com:pat-sample/uncached-main.git"
        main = lab.home / "Projects" / "uncached-main"
        lab.g(pat, "init", "-q", "-b", "main", str(main))
        lab.g(pat, "remote", "add", "origin", url, cwd=main)
        lab.g(pat, "commit", "-q", "--allow-empty", "-m", "seed", cwd=main)
        wt = lab.home / "Projects" / "uncached-main-wt"
        lab.g(pat, "worktree", "add", "-q", "-b", "wt", str(wt), cwd=main)
        norm = pr.normalize_remote(url, root=lab.lib)
        row = {"path": str(wt), "kind": "linked-worktree", "owner_class": "personal", "default_branch": None,
               "remotes": [{"name": "origin", "form": norm["form"], "host": norm["host"], "slug": norm["slug"]}]}
        cache.write_text(json.dumps({"schema_version": 1, "device": "dev-a", "generated_at": "2026-09-24T00:00:00Z",
                                     "generated_by": "human", "projects_root": str(lab.home / "Projects"),
                                     "checkouts": [row]}), encoding="utf-8")
        r = lab.g(penv, "commit", "--allow-empty", "-m", "claude commit, main checkout uncached", cwd=wt)
        out.append((DECISION_CASES[37], r.returncode != 0 and "[not-positively-personal]" in r.stderr,
                    f"rc={r.returncode} {r.stderr[-300:]}"))
    finally:
        if cache.exists():
            cache.unlink()
    return out


def _bare_worktree_cases(lab: Lab, pr, penv: dict) -> list:
    """W3-02: a linked worktree's main checkout is its common dir when that is a bare repo; the floor
    resolves it from the cache, so `scan` (run as a human) must record bare repos."""
    out = []
    pat = dict(lab.base_env, GIT_AUTHOR_NAME="Pat Sample", GIT_AUTHOR_EMAIL=lab.pat_mail(),
               GIT_COMMITTER_NAME="Pat Sample", GIT_COMMITTER_EMAIL=lab.pat_mail())
    cache = pr.ws_paths(home=lab.home)["telemetry"] / "checkouts.json"
    human = {"family": "human", "family_for_walls": "human", "agent_possible": False}
    try:
        seed = lab.tmp / "bare-seed"
        lab.g(pat, "init", "-q", "-b", "main", str(seed))
        lab.g(pat, "commit", "-q", "--allow-empty", "-m", "seed", cwd=seed)
        bare = lab.home / "Projects" / "bare-mine.git"
        lab.g(pat, "clone", "-q", "--bare", str(seed), str(bare))
        lab.g(pat, "--git-dir", str(bare), "remote", "set-url", "origin", "git@github.com:pat-sample/bare-mine.git")
        wt = lab.tmp / "bare-mine-wt"
        lab.g(pat, "--git-dir", str(bare), "worktree", "add", "-q", "-b", "wt", str(wt), "main")
        ebare = lab.home / "Projects" / "bare-theirs.git"
        lab.g(pat, "clone", "-q", "--bare", str(seed), str(ebare))
        lab.g(pat, "--git-dir", str(ebare), "remote", "set-url", "origin", "git@github.com:acme-corp/bare-theirs.git")
        ewt = lab.tmp / "bare-theirs-wt"
        lab.g(pat, "--git-dir", str(ebare), "worktree", "add", "-q", "-b", "wt", str(ewt), "main")
        sc = pr.scan(root=lab.lib, home=lab.home, detection=human)
        rows = {os.path.basename(c["path"]): c["owner_class"] for c in ((sc.get("_doc") or {}).get("checkouts") or [])
                if c.get("kind") == "bare"}
        r = lab.g(penv, "commit", "--allow-empty", "-m", "claude commit in a bare repo's worktree", cwd=wt)
        e = lab.g(lab.with_ident(penv), "commit", "--allow-empty", "-m", "employer bare worktree", cwd=ewt)
        out.append((DECISION_CASES[33], sc.get("written") and rows == {"bare-mine.git": "personal",
                                                                     "bare-theirs.git": "employer"}
                    and r.returncode == 0 and "blocked" not in r.stderr and e.returncode != 0 and "[I2]" in e.stderr,
                    f"written={sc.get('written')} rows={rows} rc={r.returncode} {r.stderr[-300:]} "
                    f"employer rc={e.returncode} {e.stderr[-200:]}"))
    finally:
        if cache.exists():
            cache.unlink()
    return out


# --------------------------------------------------------------------------- TestOverlay (installer path)

INSTALL_CASES = ["install: --install-claude-overlay lands the v5 env file and its env-file SessionStart entry on a "
                 "temp HOME through installers.run, and the hook renders it to the bound v5 env",
                 "install: the settings env is never touched (D-W1-4: the old channel stays until the retire step)",
                 "install: refused under an agent marker, a Claude ancestor and without a TTY (exit 4, nothing written)",
                 "install: the diff is printed and the answer N writes nothing",
                 "install: launchctl, gh and osascript are never called"]


def overlay_install_cases(pr, rs) -> list:
    out = []
    try:
        inst = load("00-bootstrap/doctor/installers.py", "installers")
        ms = inst.merge_settings
    except (ImportError, OSError, AttributeError) as exc:
        return [(n, False, f"installers.py unavailable ({exc.__class__.__name__})") for n in INSTALL_CASES]
    td = tempfile.mkdtemp(prefix="ws-t8-install-")
    saved_path = os.environ.get("PATH", "")
    try:
        tmp = Path(os.path.realpath(td))
        home, repo, stubs = tmp / "home", tmp / "repo", tmp / "stubs"
        for d in (home, repo, stubs):
            d.mkdir(parents=True)
        log = tmp / "stub-calls.log"
        for name in ("launchctl", "gh", "osascript"):
            s = stubs / name
            s.write_text(f"#!/bin/sh\necho {name} >> '{log}'\nexit 0\n", encoding="utf-8")
            s.chmod(0o755)
        os.environ["PATH"] = f"{stubs}{os.pathsep}{saved_path}"
        for rel in ("00-bootstrap/dist/settings-user-fragment.json", "00-bootstrap/dist/claude-overlay.env"):
            (repo / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, repo / rel)
        for sub in ("git", "gh-claude"):
            for f in sorted((DIST / sub).iterdir()):
                if f.is_file():
                    (repo / "00-bootstrap" / "dist" / sub).mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(f, repo / "00-bootstrap" / "dist" / sub / f.name)
        base = home / ".config" / "snds-workspace"
        (base / "bin").mkdir(parents=True)
        shutil.copyfile(DIST / "ws-hook", base / "bin" / "ws-hook")
        (base / "bin" / "ws-hook").chmod(0o755)
        (base / "lib" / "x" / "09-tools").mkdir(parents=True)
        # the installer refuses a pin without ws_hook's env-file step (D-W1-4); pin the real one
        shutil.copyfile(ROOT / "09-tools" / "ws_hook.py", base / "lib" / "x" / "09-tools" / "ws_hook.py")
        (base / "lib" / "current").symlink_to(base / "lib" / "x")
        (base / "control").mkdir()
        dev = pr.current_device().get("id") or "unknown"
        probes = repo / "02-shared-references" / "probes"
        probes.mkdir(parents=True)
        (probes / f"cursor@{dev}.json").write_text(json.dumps(
            {"schema_version": 1, "surface": "cursor", "device": dev,
             "env_probe": {"env_presence": {"WS_CLAUDE_OVERLAY": False}}}), encoding="utf-8")
        (probes / f"git@{dev}.json").write_text(json.dumps(
            {"schema_version": 1, "surface": "git", "device": dev, "git_version": "2.54.0", "hasconfig": True,
             "config_hooks": True, "recorded_at": "2026-09-24"}), encoding="utf-8")
        sj = home / ".claude" / "settings.json"
        sj.parent.mkdir(parents=True)
        stale = {"env": {"EDITOR": "vi", "WS_CLAUDE_OVERLAY": "v4", "GIT_AUTHOR_EMAIL": "stale@example.invalid",
                         "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "x.y", "GIT_CONFIG_VALUE_0": "z"},
                 "hooks": {}}
        sj.write_text(json.dumps(stale, indent=2) + "\n", encoding="utf-8")
        before = sj.read_bytes()
        render_list = {"outputs": rs.list_outputs(rs.load_table(ROOT))}

        def run(verdict=HUMAN, tty=TTY, answer="y"):
            o, e = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
                rc = inst.run("claude-overlay", "install", home=home, repo=repo, agent_check=lambda: dict(verdict),
                              isatty=tty, confirm=lambda _p: answer, render_list=render_list,
                              which=lambda _n: None, app_exists=lambda _p: False)
            return rc, o.getvalue(), e.getvalue()

        rc_a, _o, err_a = run(verdict=AGENT)
        anc = pr.agent_check(env={}, ancestry=[{"comm": "zsh"}, {"comm": "Claude"}], isatty=TTY)
        rc_c, _o, err_c = run(verdict=anc)
        rc_t, _o, err_t = run(tty={"stdin": True, "stdout": False})
        out.append((INSTALL_CASES[2], rc_a == 4 and rc_c == 4 and rc_t == 4 and sj.read_bytes() == before
                    and "agent:claude" in err_c and "refused" in err_a + err_t,
                    f"{rc_a}/{rc_c}/{rc_t} {err_a[-160:]} {err_t[-160:]}"))
        rc_n, o_n, _e = run(answer="n")
        out.append((INSTALL_CASES[3], rc_n == 1 and "WS_CLAUDE_OVERLAY" in o_n and sj.read_bytes() == before,
                    f"rc={rc_n}"))
        rc, o, e = run()
        got = json.loads(sj.read_text(encoding="utf-8"))
        installed = base / "claude-overlay.env"
        wh = load("09-tools/ws_hook.py", "ws_hook_install_cases")
        env = {k: wh._expand_home(v, home) for k, v in wh.parse_overlay_env(installed.read_text(encoding="utf-8"))} \
            if installed.is_file() else {}
        want = ms.expand_env_home({"env": dict(rs.overlay_env(*rs.identity_tables(ROOT), "v5"))}, home)["env"]
        keys = [env.get(f"GIT_CONFIG_KEY_{i}") for i in range(int(env.get("GIT_CONFIG_COUNT", "0")))]
        cmd_i = next((i for i, k in enumerate(keys) if k == f"hook.{FLOOR}.command"), None)
        bound = cmd_i is not None and env.get(f"GIT_CONFIG_VALUE_{cmd_i}", "").startswith(f"H={home};") \
            and "$HOME" not in env.get(f"GIT_CONFIG_VALUE_{cmd_i}", "")
        cmds = [h.get("command", "") for g in (got.get("hooks") or {}).get("SessionStart") or [] for h in g.get("hooks") or []]
        good = (rc == 0 and bound and installed.read_bytes() == (DIST / "claude-overlay.env").read_bytes()
                and {k: v for k, v in env.items() if k != "WS_OVERLAY_CHANNEL"} == want
                and env.get("WS_OVERLAY_CHANNEL") == "env-file" and env.get("WS_SURFACE_FAMILY") == "claude"
                and env.get("GH_CONFIG_DIR", "").startswith(str(home))
                and sum("ws-hook env-file --host claude-code" in c for c in cmds) == 1
                and (base / "git" / "claude-identity.inc").is_file())
        out.append((INSTALL_CASES[0], good, f"rc={rc} {e[-200:]}"))
        out.append((INSTALL_CASES[1], got.get("env") == stale["env"], str(sorted(got.get("env") or {}))))
        out.append((INSTALL_CASES[4], not log.exists(), log.read_text() if log.exists() else ""))
    except Exception as exc:  # noqa: BLE001 - a broken fixture must fail, not crash the suite
        out.append(("install: fixture ran", False, f"{exc.__class__.__name__}: {exc}"))
    finally:
        os.environ["PATH"] = saved_path
        shutil.rmtree(td, ignore_errors=True)
    return out


def run_all(pr=None) -> list:
    pr = pr or load("09-tools/profile_resolve.py", "profile_resolve")
    rs = load("00-bootstrap/doctor/render_shims.py", "render_shims")
    return identity_cases(pr, rs) + claude_floor_cases(pr, rs) + floor_decision_cases(pr, rs) + \
        overlay_install_cases(pr, rs)


if __name__ == "__main__":
    fails = 0
    for name, passed, detail in run_all():
        tag = "SKIP" if passed is None else ("ok  " if passed else "FAIL")
        fails += passed is False
        print(f"{tag} {name}" + ("" if passed else f" — {detail}"))
    sys.exit(1 if fails else 0)
