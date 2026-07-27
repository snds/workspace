"""Work/personal GitHub separation — kept NON-OVERLAPPING by construction.

This mirrors the working setup this project was built inside: two GitHub identities,
told apart by **SSH host-alias** (`github.com` → personal, `github-work` → work), with
**repo-local git identity, never global**. The one rule that matters most, learned the
hard way: **never pass `-c user.name` / `-c user.email` on the command line** — that is
exactly how a personal email once leaked into an employer repo, overriding correct
repo-local config. So every identity write here is `git config --local`, and nothing in
this module ever uses `-c`.

The model:
  * profile.transport.remotes[] = [{url, scope, host_alias, name, email}]  — the map.
  * scope ∈ {personal, work}. An identity (name+email) may belong to exactly ONE scope
    across the whole map — a collision is refused, which is what makes the two worlds
    non-overlapping.
  * The vault's own repo is personal; work identities are for adopted work project repos.
  * Auto-push is a `personal-solo` behavior ONLY. Work scope prints branch→PR guidance
    and does nothing destructive.
  * `gh` is OPTIONAL — the SSH path works without it; `gh` only enables the collaborator
    convenience.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from . import core

SSH_CONFIG = Path.home() / ".ssh" / "config"


# ------------------------------------------------------------------- the map ---
# The remote → scope → identity map lives in context/remotes.json — JSON, because
# profile.yaml's deliberately-minimal serializer can't round-trip a list of maps
# (it stringifies them). Kept git-tracked so it syncs across the person's machines.
def _map_path(root: Path) -> Path:
    return root / "context" / "remotes.json"


def _load_map(root: Path) -> list:
    f = _map_path(root)
    if not f.exists():
        return []
    try:
        return json.loads(f.read_text(encoding="utf-8")).get("remotes", [])
    except (OSError, json.JSONDecodeError):
        return []


def _save_map(root: Path, remotes: list) -> None:
    f = _map_path(root)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps({"remotes": remotes}, indent=2) + "\n", encoding="utf-8")


def _norm_url(url: str) -> str:
    return url.strip().rstrip("/").removesuffix(".git")


def find_mapping(remotes: list, url: str) -> dict | None:
    n = _norm_url(url)
    for r in remotes:
        if _norm_url(str(r.get("url", ""))) == n:
            return r
    return None


def _identity_scope_conflict(remotes: list, scope: str, name: str, email: str) -> str | None:
    """An identity may live in exactly ONE scope. Return the offending other scope, or None.
    This is the check that keeps work and personal auth from silently merging."""
    for r in remotes:
        same_identity = (str(r.get("name", "")).strip().lower() == name.strip().lower()
                         and str(r.get("email", "")).strip().lower() == email.strip().lower())
        if same_identity and r.get("scope") and r.get("scope") != scope:
            return r["scope"]
    return None


def map_remote(root: Path, url: str, scope: str, name: str, email: str,
               host_alias: str = "") -> int:
    if scope not in ("personal", "work"):
        raise SystemExit("error: --scope must be 'personal' or 'work'")
    if not name or not email:
        raise SystemExit('error: mapping a remote needs --name and --email '
                         '(the identity that scope commits as)')
    remotes = _load_map(root)

    # Non-overlap guard 1: this identity must not already belong to the other scope.
    other = _identity_scope_conflict(remotes, scope, name, email)
    if other:
        raise SystemExit(
            f"error: {name} <{email}> is already mapped to the '{other}' scope. An identity "
            f"may belong to only ONE scope — that is what keeps work and personal separate. "
            f"Use a different email for '{scope}' (a GitHub noreply address works well).")

    # Non-overlap guard 2: this URL must not already be mapped to a different scope.
    existing = find_mapping(remotes, url)
    if existing and existing.get("scope") and existing["scope"] != scope:
        raise SystemExit(
            f"error: {url} is already mapped to the '{existing['scope']}' scope; refusing to "
            f"re-map it to '{scope}'. Remove the old mapping first if this is intentional.")

    alias = host_alias or ("github.com" if scope == "personal" else "github-work")
    entry = {"url": _norm_url(url), "scope": scope, "host_alias": alias,
             "name": name, "email": email}
    if existing:
        existing.update(entry)
        verb = "updated"
    else:
        remotes.append(entry)
        verb = "added"
    _save_map(root, remotes)
    print(f"✓ {verb} remote mapping: {url}")
    print(f"    scope={scope}  identity={name} <{email}>  ssh-alias={alias}")
    print("  This mapping is what gates the right identity per repo — never a global config,")
    print("  never a `-c user.*` override (that is how identities leak across the wall).")
    return 0


# --------------------------------------------------------------- ssh aliases ---
def _alias_block(alias: str, key: Path) -> str:
    return (f"\n# --- wsx: {alias} (managed; edit the key path if needed) ---\n"
            f"Host {alias}\n"
            f"    HostName github.com\n"
            f"    User git\n"
            f"    IdentityFile {key}\n"
            f"    IdentitiesOnly yes\n")


def ssh_setup(personal_alias: str = "github.com", work_alias: str = "github-work") -> int:
    """Append (never overwrite) SSH host-alias blocks so the two identities are told
    apart by hostname. Idempotent: skips an alias that already has a `Host` block."""
    if not shutil.which("ssh"):
        print("✗ ssh not found — install OpenSSH, then re-run `wsx ssh-setup`.")
        return 1
    SSH_CONFIG.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    current = SSH_CONFIG.read_text(encoding="utf-8") if SSH_CONFIG.exists() else ""

    home = Path.home()
    plan = [(personal_alias, home / ".ssh" / "id_ed25519"),
            (work_alias, home / ".ssh" / "id_ed25519_work")]
    added = []
    to_write = current
    for alias, key in plan:
        # crude but safe: only add if there is no existing `Host <alias>` line
        if any(line.strip() == f"Host {alias}" for line in current.splitlines()):
            print(f"  · {alias}: already configured — left untouched")
            continue
        to_write += _alias_block(alias, key)
        added.append((alias, key))

    if added:
        SSH_CONFIG.write_text(to_write, encoding="utf-8")
        try:
            SSH_CONFIG.chmod(0o600)
        except OSError:
            pass
        print(f"✓ added {len(added)} SSH host-alias block(s) to ~/.ssh/config (existing entries untouched):")
        for alias, key in added:
            print(f"    Host {alias}  →  {key}")
    else:
        print("✓ SSH host-aliases already present — nothing to add.")

    print("\n  Next, one key per identity (skip any you already have):")
    for alias, key in plan:
        if not key.exists():
            print(f"    ssh-keygen -t ed25519 -f {key} -C \"<the email for {alias}>\"")
            print(f"    then add {key}.pub to that GitHub account → Settings → SSH keys")
    print("\n  A personal remote uses  git@github.com:owner/repo.git ;")
    print("  a work remote uses       git@github-work:owner/repo.git  (same key never spans both).")
    return 0


# ------------------------------------------------------------ scope + push ---
def _repo_origin(root: Path) -> str:
    if not (root / ".git").exists():
        return ""
    r = core.git(root, "remote", "get-url", "origin", check=False, capture=True)
    return (r.stdout or "").strip()


def resolve_scope(root: Path, prof: dict | None = None) -> str:
    """Best-effort scope of the CURRENT repo. Fail-safe = the profile's context (default
    personal-solo→personal). Never guesses 'personal' for an unknown work-looking remote."""
    prof = prof or core.load_profile(root)
    origin = _repo_origin(root)
    if origin:
        m = find_mapping(_load_map(root), origin)
        if m and m.get("scope"):
            return m["scope"]
        # a `github-work` alias in the URL is an unambiguous work signal
        if "github-work" in origin:
            return "work"
    return "personal" if prof.get("context", "personal-solo") == "personal-solo" else "work"


def apply_repo_identity(root: Path, prof: dict, scope: str) -> tuple[bool, str]:
    """Set repo-local identity from the map for `scope`. Returns (ok, message).
    Repo-local only — never global, never `-c`."""
    ident = next((r for r in _load_map(root)
                  if r.get("scope") == scope and r.get("name") and r.get("email")), None)
    if not ident:
        return False, (f"no {scope} identity mapped yet — run "
                       f'`wsx remote add <url> --scope {scope} --name "…" --email "…"`')
    core.git(root, "config", "--local", "user.name", ident["name"], check=False)
    core.git(root, "config", "--local", "user.email", ident["email"], check=False)
    return True, f"{ident['name']} <{ident['email']}>"


def first_push(root: Path, prof: dict | None = None) -> int:
    """Finalize a fresh workspace: land the first commit + push so `gh` auth is exercised.
    GATED: auto-push only for personal-solo. Work/employer scope refuses and guides."""
    prof = prof or core.load_profile(root)
    if not (root / ".git").exists():
        print("✗ not a git repository yet. Run `wsx init` (without --no-git), or `git init`.")
        return 1

    scope = resolve_scope(root, prof)
    if scope != "personal":
        print("⚠ this repo resolves to WORK scope — refusing to auto-push.")
        print("  Employer repos go branch → PR → human review, never a direct push from a tool.")
        print("  Push it yourself once it's review-ready.")
        return 1

    ok, who = apply_repo_identity(root, prof, "personal")
    if not ok:
        # fall back to whatever repo-local identity already exists; only block on total absence
        n = core.git(root, "config", "--local", "--get", "user.name", check=False, capture=True)
        e = core.git(root, "config", "--local", "--get", "user.email", check=False, capture=True)
        if not (n.stdout or "").strip() or not (e.stdout or "").strip():
            print(f"✗ can't push — {who}")
            print('  set it: wsx identity --name "Your Name" --email "you@example.com"')
            return 1

    if not core.has_remote(root):
        print("✗ no remote configured. Point the workspace at your (private) GitHub repo first:")
        print("    wsx remote add <url> --scope personal --name \"…\" --email \"…\"")
        return 1

    core.git(root, "add", "-A", check=False)
    # commit only if there is something to commit
    st = core.git(root, "status", "--porcelain", check=False, capture=True)
    if (st.stdout or "").strip():
        core.git(root, "commit", "-q", "-m", "wsx: finalize workspace", check=False)

    print("pushing the first commit (this finalizes your GitHub auth)…")
    branch = core.git(root, "rev-parse", "--abbrev-ref", "HEAD", check=False, capture=True).stdout.strip() or "main"
    push = core.git(root, "push", "-u", "origin", branch, check=False, capture=True)
    if push.returncode == 0:
        print(f"✓ pushed {branch} → origin. Your workspace is now backed up and versioned.")
        return 0
    err = (push.stderr or "") + (push.stdout or "")
    print("✗ push did not complete. Nothing was lost — your commit is safe locally.")
    if "Permission denied" in err or "publickey" in err.lower():
        print("  Looks like an auth problem. If you use SSH, run `wsx ssh-setup` and make sure")
        print("  the key for this account is added to GitHub. Then `wsx push` again.")
    elif "not found" in err.lower() or "does not exist" in err.lower():
        print("  The remote repo may not exist yet — create an EMPTY private repo on GitHub")
        print("  (no README), then `wsx push` again.")
    else:
        print("  " + (push.stderr or "").strip().splitlines()[-1] if push.stderr.strip() else "  see git output above")
    return 1


# --------------------------------------------------------------- collaborator ---
def add_collaborator(root: Path, account: str, repo_url: str = "", permission: str = "push") -> int:
    """Offer to add a SECOND account (e.g. a work account) as a collaborator on the
    private personal workspace repo, so that account's machine can keep the workspace
    updated. User-authorized; `gh` required for the automated path, manual steps otherwise.
    This never syncs work repos INTO personal — it only grants access to the vault repo."""
    prof = core.load_profile(root)
    url = repo_url or prof.get("transport", {}).get("remote", "") or _repo_origin(root)
    if not url:
        print("✗ no workspace repo URL known — set it with `wsx remote add … --scope personal` first.")
        return 1
    # derive owner/repo from an https or ssh URL
    slug = _norm_url(url).split("github.com")[-1].split("github-work")[-1].lstrip(":/")
    print(f"About to grant '{account}' {permission} access to your workspace repo: {slug}")
    print("  (so a machine signed in as that account can pull/push THIS repo — nothing else).")
    if not shutil.which("gh"):
        print("\n  `gh` (GitHub CLI) isn't installed, so do it in the browser:")
        print(f"    https://github.com/{slug}/settings/access → Add people → {account} → {permission}")
        return 0
    print(f"\n  Run this yourself to authorize it (uses YOUR gh login for {slug}):")
    print(f"    gh api -X PUT repos/{slug}/collaborators/{account} -f permission={permission}")
    print("  (Printed, not executed — granting access is your call, not the tool's.)")
    return 0
