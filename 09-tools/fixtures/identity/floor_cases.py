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
        env = dict(self.base_env)
        for k, v in self.rs.overlay_env(self.cr, self.dev, "v5").items():
            env[k] = str(self.home / v[2:]) if v.startswith("~/") else v
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
                  "identity: no remote gets no overlay identity"]


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
        res = pr.identity(repo=str(emp), family="cursor", device="dev-a", root=root, env=env, home=lab.home,
                          detection=human)
        out.append((IDENTITY_CASES[2], res["invariants_hit"] == ["I1"], json.dumps(res)[:300]))
        none = lab.tmp / "loose"
        lab.g(lab.base_env, "init", "-q", str(none))
        got = lab.g(env, "config", "--get", "user.email", cwd=none).stdout.strip()
        out.append((IDENTITY_CASES[3], got != lab.pat_mail(), got or "(unset)"))
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
        env = lab.overlay(lifted=True)
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
                  "bypass: with the transport block active the same employer push fails at transport, not the floor"]


def floor_decision_cases(pr, rs) -> list:
    skip = _need((2, 54), DECISION_CASES)
    if skip:
        return skip
    out = []
    lab, td = _mk(pr, rs)
    try:
        lifted = lab.overlay(lifted=True)
        full = lab.overlay()
        clone, bare, genv = lab.employer(("feat/done", "feat/b1", "feat/b2", "feat/b4"))
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
        v = subprocess.run([py, str(lab.script), str(clone), "feat/done"], env=lifted, capture_output=True, text=True,
                           timeout=120)
        out.append((DECISION_CASES[3], v.returncode == 0 and not lab.has_ref(bare, "feat/done"),
                    f"rc={v.returncode} {v.stderr[-400:]}"))
        r = lab.g(lifted, "-c", f"hook.{FLOOR}.enabled=false", "push", "origin", "--delete", "feat/b1", cwd=clone)
        out.append((DECISION_CASES[4], r.returncode == 0 and not lab.has_ref(bare, "feat/b1") and FLOOR not in r.stderr,
                    f"rc={r.returncode} {r.stderr[-200:]}"))
        r = lab.g(lifted, "push", "--no-verify", "origin", "--delete", "feat/b2", cwd=clone)
        out.append((DECISION_CASES[5], r.returncode == 0 and not lab.has_ref(bare, "feat/b2"),
                    f"rc={r.returncode} {r.stderr[-200:]}"))
        r = lab.g(lifted, "commit", "--no-verify", "--allow-empty", "-m", "bypass", cwd=clone)
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
    finally:
        _cleanup(td)
    return out


# --------------------------------------------------------------------------- TestOverlay (installer path)

INSTALL_CASES = ["install: --install-claude-overlay lands the v5 env on a temp HOME through installers.run",
                 "install: the installed env is a full-key replace (stale managed keys gone, user keys kept)",
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
        for rel in ("00-bootstrap/dist/settings-user-fragment.json",):
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
        (base / "lib" / "x").mkdir(parents=True)
        (base / "lib" / "current").symlink_to(base / "lib" / "x")
        (base / "control").mkdir()
        dev = pr.current_device().get("id") or "unknown"
        probes = repo / "02-shared-references" / "probes"
        probes.mkdir(parents=True)
        (probes / f"cursor@{dev}.json").write_text(json.dumps(
            {"schema_version": 1, "surface": "cursor", "device": dev,
             "env_probe": {"env_presence": {"WS_CLAUDE_OVERLAY": False}}}), encoding="utf-8")
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
        frag = ms.expand_env_home(json.loads((ROOT / "00-bootstrap/dist/settings-user-fragment.json")
                                             .read_text(encoding="utf-8")), home)
        managed = {k: v for k, v in got.get("env", {}).items() if ms.is_managed_env(k)}
        env = got.get("env", {})
        keys = [env.get(f"GIT_CONFIG_KEY_{i}") for i in range(int(env.get("GIT_CONFIG_COUNT", "0")))]
        good = (rc == 0 and managed == frag["env"] and env.get("WS_CLAUDE_OVERLAY") == "v5"
                and env.get("WS_SURFACE_FAMILY") == "claude" and f"hook.{FLOOR}.command" in keys
                and env.get("GH_CONFIG_DIR", "").startswith(str(home))
                and (base / "git" / "claude-identity.inc").is_file())
        out.append((INSTALL_CASES[0], good, f"rc={rc} {e[-200:]}"))
        out.append((INSTALL_CASES[1], env.get("EDITOR") == "vi" and "GIT_AUTHOR_EMAIL" not in env
                    and "x.y" not in keys, str(sorted(k for k in env if not k.startswith("GIT_CONFIG_")))))
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
