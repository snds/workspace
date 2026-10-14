#!/usr/bin/env python3
"""One GitHub login route for every surface: the account follows the repo's owner. Pinned.

Why it exists (Sean, 2026-10-13: "I need to be able to push both Centric and Personal work from my
work laptop ... regardless of agentic surface"). Before this, Claude had its own gh config that named
only the personal account, Terminal and Cursor used whichever gh account was active, and a Centric gh
call from Claude worked only through a vetted script. Every surface now asks this one router:

  snds/*           -> the personal identity's account   (devices.json identities, class personal)
  cpes-software/*  -> the employer identity's account   (class employer)
  any other owner  -> nothing (git gets no credential; gh runs unchanged)

The owner -> class table is context-remotes.json `owners`; the class -> account table is devices.json
`identities`. Both are read from the copy beside this file, so a pinned router reads pinned tables.
A repo can therefore only ever receive its own owner's token: the credential wall holds by construction.

Entry points (byte-stable wrappers in 00-bootstrap/dist, copied into bin/ by the pin):
  bin/git-credential-ws  ->  gh_route.py credential get|store|erase   (git's credential helper protocol)
  bin/gh                 ->  gh_route.py gh ARGS...                    (the gh shim on PATH)

Usage:
  python3 09-tools/gh_route.py which [--repo PATH|OWNER/REPO|URL]     print the account a repo routes to
  python3 09-tools/gh_route.py --self-test
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parent.parent
CONTEXT_REMOTES = "02-shared-references/delivery-playbooks/context-remotes.json"
DEVICES = "02-shared-references/devices.json"
ROUTE_HOSTS = ("github.com",)             # hosts gh can hold a token for; others are not routed
TOKEN_TIMEOUT_S = 20
GIT_TIMEOUT_S = 10
# gh subcommands that never touch a repo or that manage the logins themselves: run unchanged
PASS_THROUGH = frozenset({"auth", "config", "alias", "extension", "extensions", "completion", "help", "version",
                          "--version", "-h", "--help", "status"})
# env names that already pick a gh credential; a caller who set one keeps it (agents cannot: guard R6/P05)
TOKEN_ENV = ("GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN")
SCP_RE = re.compile(r"^(?:[A-Za-z0-9._-]+@)?([A-Za-z0-9.-]+):/?([^/]+)/[^/]+?/?$")
API_REPO_RE = re.compile(r"^/?repos/([^/{}]+)/")


class RouteError(Exception):
    """The router refuses (owner mismatch, unreadable tables). The message is for the person."""


# --------------------------------------------------------------------------- tables


def _load(root: Path, rel: str) -> dict:
    try:
        return json.loads((root / rel).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise RouteError(f"cannot read {rel}: {type(e).__name__}") from e


def ssh_aliases(root: Path = ROOT) -> Dict[str, str]:
    """{alias: real host} from devices.json, e.g. github-work -> github.com."""
    out = {}
    for row in _load(root, DEVICES).get("ssh_aliases") or []:
        if isinstance(row, dict) and row.get("alias") and row.get("host"):
            out[str(row["alias"]).lower()] = str(row["host"]).lower()
    return out


def account_for(host: str, owner: str, root: Path = ROOT) -> Optional[str]:
    """The gh account for host/owner, or None when the owner is not declared or not routable."""
    host, owner = (host or "").lower(), (owner or "").casefold()
    if host not in ROUTE_HOSTS or not owner:
        return None
    cls = None
    for row in _load(root, CONTEXT_REMOTES).get("owners") or []:
        if isinstance(row, dict) and str(row.get("host", "")).lower() == host \
                and str(row.get("owner", "")).casefold() == owner:
            cls = row.get("class")
            break
    if cls not in ("personal", "employer"):
        return None
    for ident in _load(root, DEVICES).get("identities") or []:
        if isinstance(ident, dict) and ident.get("class") == cls:
            accts = [a for a in ident.get("accounts") or [] if isinstance(a, str) and a]
            if accts:
                return accts[0]
    return None


def routed_owners(root: Path = ROOT) -> List[Tuple[str, str]]:
    """[(host, owner)] the route serves: declared personal and employer owners on a routable host."""
    out = []
    for row in _load(root, CONTEXT_REMOTES).get("owners") or []:
        if isinstance(row, dict) and str(row.get("host", "")).lower() in ROUTE_HOSTS \
                and row.get("class") in ("personal", "employer") and row.get("owner"):
            out.append((str(row["host"]).lower(), str(row["owner"])))
    return out


CREDENTIAL_HELPER = '!"$HOME/.config/snds-workspace/bin/git-credential-ws"'


def gitconfig_route(root: Path = ROOT) -> List[Tuple[str, str, str]]:
    """[(section, key, value)] for the global include (git_lanes render): the route helper on every
    routable host, and the SSH forms of every routed owner fetched over HTTPS so they meet the route too
    (the github-work SSH alias times out on the Work MBP, ^pc-09)."""
    aliases = ssh_aliases(root)
    out: List[Tuple[str, str, str]] = []
    for host in ROUTE_HOSTS:
        sec = f'credential "https://{host}"'
        out += [(sec, "useHttpPath", "true"), (sec, "helper", ""), (sec, "helper", CREDENTIAL_HELPER)]
    for host, owner in routed_owners(root):
        sec = f'url "https://{host}/{owner}/"'
        names = [host] + sorted(a for a, h in aliases.items() if h == host)
        for n in names:
            out.append((sec, "insteadOf", f"git@{n}:{owner}/"))
        out.append((sec, "insteadOf", f"ssh://git@{host}/{owner}/"))
    return out


def _cfg_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def gitconfig_text(root: Path = ROOT) -> str:
    """The route's git config sections, as git_lanes appends them to the global lanes include."""
    route = gitconfig_route(root)
    if not route:
        return ""
    lines = ["# GitHub route (2026-10-13): every GitHub HTTPS remote gets its owner's gh account from the",
             "# pinned gh_route.py (bin/git-credential-ws); SSH forms of routed owners fetch over HTTPS too."]
    cur = None
    for sec, key, val in route:
        if sec != cur:
            lines.append(f"[{sec}]")
            cur = sec
        lines.append(f"\t{key} = {_cfg_quote(val)}" if val else f"\t{key} =")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- owners from text


def owner_of(spec: str, aliases: Optional[Dict[str, str]] = None) -> Optional[Tuple[str, str]]:
    """(host, owner) from OWNER/REPO, HOST/OWNER/REPO, an https/ssh URL or an scp-form remote."""
    s = (spec or "").strip()
    if not s:
        return None
    aliases = aliases or {}
    m = re.match(r"^(?:https?|ssh|git)://(?:[^@/]+@)?([^/:]+)(?::\d+)?/+([^/]+)/", s)
    if m:
        host = m.group(1).lower()
        return aliases.get(host, host), m.group(2)
    m = SCP_RE.match(s)
    if m and "/" not in m.group(1):
        host = m.group(1).lower()
        return aliases.get(host, host), m.group(2)
    parts = [p for p in s.split("/") if p]
    if len(parts) == 2 and ":" not in s:
        return "github.com", parts[0]
    if len(parts) == 3 and "." in parts[0] and ":" not in s:
        return parts[0].lower(), parts[1]
    return None


def _origin_url(cwd: str) -> Optional[str]:
    try:
        r = subprocess.run(["git", "-C", cwd, "remote", "get-url", "origin"], capture_output=True, text=True,
                           timeout=GIT_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def gh_target(args: Sequence[str], env: Dict[str, str], cwd: str,
              aliases: Optional[Dict[str, str]] = None) -> Optional[Tuple[str, str]]:
    """(host, owner) a gh call acts on. Every explicit hint must agree; the checkout is the fallback."""
    hints: List[Tuple[str, str]] = []
    i, a, rest = 0, list(args), []
    while i < len(a):
        x = a[i]
        if x in ("-R", "--repo") and i + 1 < len(a):
            t = owner_of(a[i + 1], aliases)
            if t:
                hints.append(t)
            i += 2
            continue
        if x.startswith("--repo="):
            t = owner_of(x.split("=", 1)[1], aliases)
            if t:
                hints.append(t)
            i += 1
            continue
        rest.append(x)
        i += 1
    if env.get("GH_REPO"):
        t = owner_of(env["GH_REPO"], aliases)
        if t:
            hints.append(t)
    if rest[:1] == ["api"]:
        for x in rest[1:]:
            m = API_REPO_RE.match(x)
            if m and "{" not in m.group(1):
                hints.append(("github.com", m.group(1)))
                break
    if hints:
        keys = {(h, o.casefold()) for h, o in hints}
        if len(keys) > 1:
            raise RouteError("this gh call names more than one repo owner ("
                             + ", ".join(sorted(f"{h}/{o}" for h, o in keys))
                             + "); run it once per owner so each gets its own account")
        return hints[0]
    url = _origin_url(cwd)
    return owner_of(url, aliases) if url else None


# --------------------------------------------------------------------------- the real gh and tokens


def real_gh(env: Dict[str, str]) -> Optional[str]:
    """The gh binary on PATH that is not this router's wrapper."""
    mine = {str(Path(__file__).resolve().parent.parent)}
    for d in (env.get("PATH") or os.defpath).split(os.pathsep):
        cand = Path(d or ".") / "gh"
        try:
            if not cand.is_file() or not os.access(cand, os.X_OK):
                continue
            head = cand.read_bytes()[:400]
        except OSError:
            continue
        if b"gh_route.py" in head:          # our wrapper (bin/gh or a ~/.local/bin link to it)
            continue
        if any(str(cand.resolve()).startswith(m) for m in mine):
            continue
        return str(cand)
    for fallback in ("/opt/homebrew/bin/gh", "/usr/local/bin/gh", "/usr/bin/gh"):
        if os.access(fallback, os.X_OK):
            return fallback
    return None


def _clean_env(env: Dict[str, str]) -> Dict[str, str]:
    """The device's own gh logins: no per-surface config dir, no caller token."""
    out = {k: v for k, v in env.items() if k not in TOKEN_ENV and k != "GH_CONFIG_DIR"}
    return out


def token_for(host: str, account: str, env: Dict[str, str], gh: Optional[str] = None) -> Optional[str]:
    gh = gh or real_gh(env)
    if not gh:
        return None
    try:
        r = subprocess.run([gh, "auth", "token", "--hostname", host, "--user", account], capture_output=True,
                           text=True, timeout=TOKEN_TIMEOUT_S, env=_clean_env(env))
    except (OSError, subprocess.SubprocessError):
        return None
    tok = r.stdout.strip()
    return tok if r.returncode == 0 and tok and "\n" not in tok else None


# --------------------------------------------------------------------------- git credential helper


def credential(op: str, stdin_text: str, env: Dict[str, str], root: Path = ROOT,
               gh: Optional[str] = None) -> Tuple[str, str]:
    """(stdout, stderr) for one git credential call. Only `get` answers; store and erase are no-ops."""
    if op != "get":
        return "", ""
    req: Dict[str, str] = {}
    for ln in stdin_text.splitlines():
        if "=" in ln:
            k, v = ln.split("=", 1)
            req[k] = v
    if req.get("protocol") != "https":
        return "", ""
    host = (req.get("host") or "").lower()
    path = req.get("path") or ""
    if not path:
        return "", ("ws github route: git sent no repo path, so the account cannot be chosen "
                    "(credential.https://github.com.useHttpPath must be true)\n")
    owner = path.strip("/").split("/", 1)[0]
    acct = account_for(host, owner, root)
    if not acct:
        return "", ""                      # an undeclared owner gets no credential from the route
    want = req.get("username")
    if want and want.casefold() != acct.casefold():
        return "", (f"ws github route: the remote names user {want} but {owner} repos use {acct}; "
                    "drop the user from the remote URL\n")
    tok = token_for(host, acct, env, gh)
    if not tok:
        return "", (f"ws github route: no gh token for {acct}. Run: gh auth login --hostname {host} "
                    f"(as {acct})\n")
    return f"username={acct}\npassword={tok}\n", ""


# --------------------------------------------------------------------------- gh shim


def gh_plan(args: Sequence[str], env: Dict[str, str], cwd: str, root: Path = ROOT,
            gh: Optional[str] = None) -> Tuple[str, List[str], Dict[str, str]]:
    """(binary, argv, env) to exec for one gh call."""
    gh = gh or real_gh(env)
    if not gh:
        raise RouteError("gh is not installed (no gh on PATH besides the workspace wrapper)")
    argv = [gh, *args]
    first = next((a for a in args if not a.startswith("-")), args[0] if args else "")
    if not args or first in PASS_THROUGH or any(env.get(k) for k in TOKEN_ENV):
        return gh, argv, dict(env)
    tgt = gh_target(args, env, cwd, ssh_aliases(root))
    if not tgt:
        return gh, argv, dict(env)
    acct = account_for(tgt[0], tgt[1], root)
    if not acct:
        return gh, argv, dict(env)
    tok = token_for(tgt[0], acct, env, gh)
    if not tok:
        raise RouteError(f"no gh token for {acct} ({tgt[1]} repos use it). Run: gh auth login "
                         f"--hostname {tgt[0]} (as {acct})")
    out = {k: v for k, v in env.items() if k not in TOKEN_ENV}
    out["GH_TOKEN"] = tok
    return gh, argv, out


# --------------------------------------------------------------------------- CLI


def main(argv: Sequence[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--self-test":
        return self_test()
    env = dict(os.environ)
    if argv[0] == "credential":
        out, err = credential(argv[1] if len(argv) > 1 else "", sys.stdin.read(), env)
        sys.stdout.write(out)
        sys.stderr.write(err)
        return 0
    if argv[0] == "gh":
        try:
            binary, args, new_env = gh_plan(argv[1:], env, os.getcwd())
        except RouteError as e:
            print(f"ws github route: {e}", file=sys.stderr)
            return 2
        os.execve(binary, args, new_env)
    if argv[0] == "which":
        spec = argv[2] if len(argv) > 2 and argv[1] == "--repo" else os.getcwd()
        aliases = ssh_aliases()
        tgt = owner_of(spec, aliases) if not os.path.isdir(spec) else \
            (owner_of(_origin_url(spec) or "", aliases))
        acct = account_for(*tgt) if tgt else None
        print(f"{tgt[0]}/{tgt[1]} -> {acct or 'no route'}" if tgt else "no GitHub owner found -> no route")
        return 0 if acct else 1
    print(__doc__, file=sys.stderr)
    return 2


# --------------------------------------------------------------------------- self-test


def _fixture_root(tmp: Path) -> Path:
    root = tmp / "ws"
    (root / CONTEXT_REMOTES).parent.mkdir(parents=True)
    (root / CONTEXT_REMOTES).write_text(json.dumps({"owners": [
        {"host": "github.com", "owner": "pat-sample", "class": "personal"},
        {"host": "github.com", "owner": "acme-corp", "class": "employer"},
        {"host": "bitbucket.org", "owner": "acme-bb", "class": "employer"}]}), encoding="utf-8")
    (root / DEVICES).write_text(json.dumps({
        "ssh_aliases": [{"alias": "github-acme", "host": "github.com"}],
        "identities": [{"id": "acme", "class": "employer", "accounts": ["pat-acme"]},
                       {"id": "pat", "class": "personal", "accounts": ["pat-sample"]}]}), encoding="utf-8")
    return root


def _fake_gh(tmp: Path) -> str:
    """A stand-in gh: `auth token --user U` prints tok-U; anything else prints the token it was given."""
    p = tmp / "bin" / "gh"
    p.parent.mkdir(parents=True)
    p.write_text("#!/bin/sh\n"
                 'if [ "$1" = auth ] && [ "$2" = token ]; then\n'
                 '  [ -n "$GH_CONFIG_DIR" ] && { echo "config dir leaked" >&2; exit 9; }\n'
                 '  while [ $# -gt 0 ]; do [ "$1" = --user ] && { echo "tok-$2"; exit 0; }; shift; done; exit 1\n'
                 "fi\n"
                 'echo "token=${GH_TOKEN:-none}"\n', encoding="utf-8")
    p.chmod(0o755)
    return str(p)


def self_test() -> int:
    fails: List[str] = []

    def ok(cond: bool, label: str) -> None:
        if not cond:
            fails.append(label)

    with tempfile.TemporaryDirectory(prefix="gh-route-") as td:
        tmp = Path(td)
        root = _fixture_root(tmp)
        gh = _fake_gh(tmp)
        env = {"PATH": str(tmp / "bin") + os.pathsep + os.defpath, "GH_CONFIG_DIR": "/x/gh-claude"}
        al = ssh_aliases(root)

        ok(account_for("github.com", "pat-sample", root) == "pat-sample", "personal owner -> personal account")
        ok(account_for("github.com", "ACME-CORP", root) == "pat-acme", "employer owner, any case -> employer account")
        ok(account_for("github.com", "someone-else", root) is None, "undeclared owner -> no route")
        ok(account_for("bitbucket.org", "acme-bb", root) is None, "a host gh cannot serve -> no route")

        ok(owner_of("acme-corp/widget") == ("github.com", "acme-corp"), "OWNER/REPO")
        ok(owner_of("github.com/acme-corp/widget") == ("github.com", "acme-corp"), "HOST/OWNER/REPO")
        ok(owner_of("https://github.com/pat-sample/ws.git") == ("github.com", "pat-sample"), "https URL")
        ok(owner_of("https://pat-sample@github.com/pat-sample/ws.git") == ("github.com", "pat-sample"), "https userinfo")
        ok(owner_of("git@github-acme:acme-corp/widget.git", al) == ("github.com", "acme-corp"), "scp alias -> real host")
        ok(owner_of("ssh://git@github.com/acme-corp/widget") == ("github.com", "acme-corp"), "ssh URL")
        ok(owner_of("not a repo") is None, "free text -> None")

        def cred(stdin: str) -> Tuple[str, str]:
            return credential("get", stdin, env, root, gh)

        out, err = cred("protocol=https\nhost=github.com\npath=acme-corp/widget.git\n")
        ok(out == "username=pat-acme\npassword=tok-pat-acme\n" and not err, f"git: employer repo -> employer token {out!r} {err!r}")
        out, _ = cred("protocol=https\nhost=github.com\npath=pat-sample/ws.git\n")
        ok(out == "username=pat-sample\npassword=tok-pat-sample\n", "git: personal repo -> personal token")
        out, _ = cred("protocol=https\nhost=github.com\npath=someone-else/x.git\n")
        ok(out == "", "git: undeclared owner -> no credential")
        out, err = cred("protocol=https\nhost=github.com\n")
        ok(out == "" and "useHttpPath" in err, "git: no path -> refuse with the fix")
        out, err = cred("protocol=https\nhost=github.com\npath=acme-corp/w.git\nusername=pat-sample\n")
        ok(out == "" and "drop the user" in err, "git: a URL user that disagrees with the route -> refuse")
        ok(credential("store", "protocol=https\nhost=github.com\npath=acme-corp/w\npassword=x\n", env, root, gh)
           == ("", ""), "git: store is a no-op")

        def plan(args: List[str], cwd: str = td, e: Optional[Dict[str, str]] = None):
            return gh_plan(args, e if e is not None else env, cwd, root, gh)

        _b, _a, e2 = plan(["-R", "acme-corp/widget", "pr", "comment", "3", "--body", "x"])
        ok(e2.get("GH_TOKEN") == "tok-pat-acme", "gh -R employer -> employer token")
        _b, _a, e2 = plan(["issue", "create", "--repo=pat-sample/ws", "-t", "x"])
        ok(e2.get("GH_TOKEN") == "tok-pat-sample", "gh --repo= personal -> personal token")
        _b, _a, e2 = plan(["api", "repos/acme-corp/widget/pulls"])
        ok(e2.get("GH_TOKEN") == "tok-pat-acme", "gh api repos/OWNER -> that owner's token")
        try:
            plan(["-R", "pat-sample/ws", "api", "repos/acme-corp/widget/issues", "-f", "title=x"])
            ok(False, "gh with two owners must refuse")
        except RouteError as e:
            ok("more than one repo owner" in str(e), "gh with two owners refuses")
        _b, _a, e2 = plan(["auth", "status"])
        ok("GH_TOKEN" not in e2 and e2.get("GH_CONFIG_DIR") == "/x/gh-claude", "gh auth runs unchanged")
        _b, _a, e2 = plan(["-R", "someone-else/x", "pr", "list"])
        ok("GH_TOKEN" not in e2, "gh on an undeclared owner runs unchanged")
        _b, _a, e2 = plan(["pr", "list"], e=dict(env, GH_TOKEN="caller"))
        ok(e2.get("GH_TOKEN") == "caller", "a caller's own token is kept")

        repo = tmp / "checkout"
        subprocess.run(["git", "init", "-q", str(repo)], check=True, timeout=GIT_TIMEOUT_S)
        subprocess.run(["git", "-C", str(repo), "remote", "add", "origin", "git@github-acme:acme-corp/widget.git"],
                       check=True, timeout=GIT_TIMEOUT_S)
        _b, _a, e2 = plan(["pr", "list"], cwd=str(repo))
        ok(e2.get("GH_TOKEN") == "tok-pat-acme", "gh in an employer checkout (alias remote) -> employer token")
        _b, _a, e2 = plan(["pr", "list"], cwd=td)
        ok("GH_TOKEN" not in e2, "gh outside any checkout runs unchanged")

        # end to end through git itself: a temp home whose global config is a gh helper (as `gh auth
        # setup-git` writes it) followed by the route sections, with a stand-in bin/git-credential-ws
        home = tmp / "home"
        helper = home / ".config" / "snds-workspace" / "bin" / "git-credential-ws"
        helper.parent.mkdir(parents=True)
        helper.write_text("#!/bin/sh\ncat >/dev/null\necho username=via-route\necho password=from-route\n",
                          encoding="utf-8")
        helper.chmod(0o755)
        gc = home / "gitconfig"
        gc.write_text('[credential "https://github.com"]\n\thelper =\n\thelper = !gh auth git-credential\n'
                      + gitconfig_text(root), encoding="utf-8")
        genv = {"PATH": os.environ.get("PATH", os.defpath), "HOME": str(home), "GIT_CONFIG_GLOBAL": str(gc),
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0", "LANG": "C", "LC_ALL": "C"}

        def git(*a: str, stdin: Optional[str] = None) -> str:
            return subprocess.run(["git", *a], input=stdin, capture_output=True, text=True, env=genv,
                                  timeout=GIT_TIMEOUT_S).stdout

        ok(git("ls-remote", "--get-url", "git@github-acme:acme-corp/widget.git").strip()
           == "https://github.com/acme-corp/widget.git", "git: an employer alias remote fetches over HTTPS")
        ok(git("ls-remote", "--get-url", "git@github.com:pat-sample/ws.git").strip()
           == "https://github.com/pat-sample/ws.git", "git: a personal scp remote fetches over HTTPS")
        ok(git("ls-remote", "--get-url", "git@github.com:someone-else/x.git").strip()
           == "git@github.com:someone-else/x.git", "git: an undeclared owner keeps its own transport")
        got = git("credential", "fill", stdin="url=https://github.com/acme-corp/widget.git\n\n")
        ok("password=from-route" in got and "path=acme-corp/widget.git" in got,
           f"git: the route helper replaces gh's and receives the repo path: {got!r}")

        r = subprocess.run([sys.executable, str(Path(__file__).resolve()), "credential", "get"],
                           input="protocol=https\nhost=github.com\npath=nobody-declared/x\n", capture_output=True,
                           text=True, timeout=60)
        ok(r.returncode == 0 and r.stdout == "", "CLI credential get on an unknown owner prints nothing")

    if fails:
        for f in fails:
            print(f"FAIL gh_route: {f}")
        return 1
    print("OK gh_route self-test")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
