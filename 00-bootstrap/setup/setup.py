#!/usr/bin/env python3
"""
Claude Workspace — cross-platform installer.

Runs on macOS, Windows, Linux. Python 3.8+. Standard library only (no pip deps)
so it can run before the rest of the environment exists.

What it does, in order:
  1. Detect OS, hostname, existing tooling.
  2. Install package manager if missing (Homebrew on macOS; winget assumed on Win 11).
  3. Install Claude Code, Obsidian, Git, gh (GitHub CLI).
  4. Resolve the workspace root = the checkout this script lives in (the dir containing AGENTS.md).
     No Google Drive, no cloud-mount detection — the workspace is a plain git checkout.
  5. Install Obsidian community plugins from .obsidian/plugins-manifest.json.
  6. Register this machine's hostname if unknown.
  7. Verify: run `claude --version`, check Obsidian opens, verify git remote.

Run this from inside a `git clone` of the workspace. Idempotent. Safe to re-run.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

# ---------- Config ----------

REPO_NAME = "workspace"
DEFAULT_REPO_URL = os.environ.get("CLAUDE_WORKSPACE_REPO", "")  # e.g. git@github.com:snds/workspace.git

HOSTNAME_MAP = {
    "Voyager-2.local": "Personal MacBook Pro",
    "seansands.local": "Work MacBook Pro",
    "CS-KQ23N94M0W": "Work MacBook Pro (loaner)",
    "CS-K746DRWXY1": "Work MacBook Pro (main, going forward)",
    "Enterprise": "Windows Desktop",
}

# Marker file that identifies the workspace root (the universal contract).
ROOT_MARKER = "AGENTS.md"


# ---------- Utilities ----------


def ok(msg: str) -> None:
    print(f"  \u2713 {msg}")


def info(msg: str) -> None:
    print(f"  \u2022 {msg}")


def warn(msg: str) -> None:
    print(f"  \u26a0 {msg}", file=sys.stderr)


def err(msg: str) -> None:
    print(f"  \u2717 {msg}", file=sys.stderr)


def step(msg: str) -> None:
    print(f"\n\033[1m{msg}\033[0m")


def run(cmd, check: bool = True, capture: bool = True, shell: bool = False):
    """Run a command. cmd is a list (preferred) or a string (if shell=True)."""
    try:
        return subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
            check=check,
            shell=shell,
        )
    except subprocess.CalledProcessError as e:
        if capture:
            err(f"command failed: {cmd}")
            err(f"stdout: {e.stdout}")
            err(f"stderr: {e.stderr}")
        raise


def have(binary: str) -> bool:
    """Is a binary on PATH?"""
    return shutil.which(binary) is not None


def confirm(prompt: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    try:
        reply = input(f"  {prompt} {suffix} ").strip().lower()
    except EOFError:
        return default
    if not reply:
        return default
    return reply in ("y", "yes")


# ---------- Detection ----------


def detect_os() -> str:
    s = platform.system().lower()
    if s == "darwin":
        return "macos"
    if s == "windows":
        return "windows"
    if s == "linux":
        return "linux"
    return s


def detect_machine_label() -> str:
    host = socket.gethostname()
    return HOSTNAME_MAP.get(host, f"unknown ({host})")


def find_workspace_root() -> Path | None:
    """Resolve the workspace root = nearest ancestor of this script containing AGENTS.md.

    The workspace is a plain git checkout; this script lives at 00-bootstrap/setup/setup.py,
    so the root is normally three levels up. No Google Drive / cloud-mount detection.
    """
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ROOT_MARKER).is_file():
            return parent
    return None


# Back-compat shims: callers may still reference the old names. Both now resolve the checkout.
def find_drive_root(os_name: str | None = None) -> Path | None:  # noqa: ARG001
    return find_workspace_root()


def wait_for_drive(os_name: str | None = None, timeout: int = 0) -> Path:  # noqa: ARG001
    root = find_workspace_root()
    if root is None:
        raise SystemExit(
            "Could not resolve the workspace root. Run setup.py from inside a git clone of the "
            "workspace (the directory tree containing AGENTS.md)."
        )
    ok(f"Workspace root: {root}")
    return root


# ---------- Package managers + tool installs ----------


def ensure_homebrew() -> None:
    if have("brew"):
        ok("Homebrew present")
        return
    step("Installing Homebrew")
    run(
        '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
        shell=True,
        capture=False,
    )


def brew_install_cask(name: str) -> None:
    if have(name):
        ok(f"{name} already on PATH")
        return
    info(f"Installing {name} (brew cask)...")
    run(["brew", "install", "--cask", name], capture=False)


def winget_install(pkg_id: str, tool_name: str | None = None) -> None:
    name = tool_name or pkg_id
    if tool_name and have(tool_name):
        ok(f"{name} already on PATH")
        return
    info(f"Installing {name} via winget ({pkg_id})...")
    run(
        ["winget", "install", "--id", pkg_id, "-e", "--silent", "--accept-package-agreements", "--accept-source-agreements"],
        check=False,
        capture=False,
    )


def ensure_python3_shim_windows() -> None:
    """Create a python3.bat shim on Windows so hooks can call python3 cross-platform."""
    # Find where python.exe lives and put python3.bat next to it.
    python_path = shutil.which("python")
    if not python_path:
        warn("python not on PATH; skipping python3 shim.")
        return
    shim = Path(python_path).parent / "python3.bat"
    if shim.exists():
        ok("python3 shim already present")
        return
    shim.write_text(f'@echo off\n"{python_path}" %*\n')
    ok(f"Created python3 shim at {shim}")


def install_claude_code(os_name: str) -> None:
    step("Installing Claude Code")
    if have("claude"):
        ok("claude already on PATH")
        return
    if os_name == "macos":
        brew_install_cask("claude-code")
    elif os_name == "windows":
        winget_install("Anthropic.ClaudeCode", "claude")
    else:
        info("Installing Claude Code via curl...")
        run("curl -fsSL https://claude.ai/install.sh | bash", shell=True, capture=False)


def install_obsidian(os_name: str) -> None:
    step("Installing Obsidian")
    if os_name == "macos":
        brew_install_cask("obsidian")
    elif os_name == "windows":
        winget_install("Obsidian.Obsidian", "Obsidian")
    elif os_name == "linux":
        info("Linux: install Obsidian manually from https://obsidian.md/download (AppImage/Flatpak).")


def install_git_and_gh(os_name: str) -> None:
    step("Installing Git + GitHub CLI")
    if os_name == "macos":
        if not have("git"):
            run(["brew", "install", "git"], capture=False)
        if not have("gh"):
            run(["brew", "install", "gh"], capture=False)
    elif os_name == "windows":
        if not have("git"):
            winget_install("Git.Git", "git")
        if not have("gh"):
            winget_install("GitHub.cli", "gh")
    ok("git + gh ready")


# ---------- Git repo setup ----------


def git_clone_or_pull(workspace: Path, repo_url: str) -> None:
    step("Syncing workspace Git repo")
    git_dir = workspace / ".git"
    if git_dir.exists():
        info("Git repo already initialized here.")
        # Never rebase over a live editing session. If the tree is dirty, skip the
        # pull rather than error/strand work — the user commits, then re-syncs.
        dirty = run(["git", "-C", str(workspace), "status", "--porcelain"],
                    check=False, capture=True)
        if getattr(dirty, "stdout", "").strip():
            warn("Uncommitted changes present — skipping auto-pull to protect your work.")
            warn("Commit (or stash) first, then re-run to sync from remote.")
            return
        run(["git", "-C", str(workspace), "pull", "--rebase"], check=False, capture=False)
        ok("Pulled latest from remote")
        return
    if not repo_url:
        warn("No repo URL configured. Skipping clone.")
        warn("Set CLAUDE_WORKSPACE_REPO env var, or run: git init + git remote add origin <url>")
        return

    # We can't clone into a non-empty directory; init + remote + pull instead.
    info(f"Initializing Git in {workspace}")
    run(["git", "-C", str(workspace), "init"], capture=False)
    run(["git", "-C", str(workspace), "remote", "add", "origin", repo_url], check=False, capture=False)
    run(["git", "-C", str(workspace), "fetch", "origin"], check=False, capture=False)
    r = run(["git", "-C", str(workspace), "branch", "-a"], check=False)
    default_branch = "main"
    if r and "remotes/origin/" in (r.stdout or ""):
        for line in r.stdout.splitlines():
            line = line.strip()
            if line.startswith("remotes/origin/") and "HEAD" not in line:
                default_branch = line.replace("remotes/origin/", "")
                break
    run(["git", "-C", str(workspace), "checkout", "-b", default_branch, f"origin/{default_branch}"], check=False, capture=False)
    ok(f"Checked out {default_branch}")


# ---------- Obsidian plugin install ----------


def install_obsidian_plugins(workspace: Path) -> None:
    step("Installing Obsidian community plugins")
    manifest_path = workspace / ".obsidian" / "plugins-manifest.json"
    if not manifest_path.exists():
        warn(f"No plugins manifest at {manifest_path}; skipping.")
        return
    manifest = json.loads(manifest_path.read_text())
    for plugin in manifest.get("plugins", []):
        pid = plugin["id"]
        repo = plugin["repo"]
        plugin_dir = workspace / ".obsidian" / "plugins" / pid
        if (plugin_dir / "main.js").exists():
            ok(f"{pid} already installed")
            continue
        try:
            install_single_plugin(pid, repo, plugin_dir)
        except Exception as e:
            err(f"Failed to install {pid}: {e}")


def install_single_plugin(pid: str, repo: str, plugin_dir: Path) -> None:
    """Fetch the latest release zip from GitHub and extract main.js, manifest.json, styles.css."""
    info(f"Fetching {pid} from {repo}...")
    api = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(api, headers={"User-Agent": "claude-workspace-setup"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        release = json.loads(resp.read())

    # Prefer a release zip named like {pid}-x.y.z.zip, else fall back to individual assets.
    zip_asset = None
    file_assets = {}
    for a in release.get("assets", []):
        n = a["name"]
        if n.endswith(".zip"):
            zip_asset = a
        elif n in ("main.js", "manifest.json", "styles.css"):
            file_assets[n] = a

    plugin_dir.mkdir(parents=True, exist_ok=True)

    if file_assets:
        # Individual files — typical for Obsidian community plugins.
        for fname, asset in file_assets.items():
            download_file(asset["browser_download_url"], plugin_dir / fname)
    elif zip_asset:
        tmp_zip = plugin_dir / "_tmp.zip"
        download_file(zip_asset["browser_download_url"], tmp_zip)
        with zipfile.ZipFile(tmp_zip, "r") as z:
            for member in z.namelist():
                if Path(member).name in ("main.js", "manifest.json", "styles.css"):
                    z.extract(member, plugin_dir)
                    # Flatten if nested
                    extracted = plugin_dir / member
                    flat = plugin_dir / Path(member).name
                    if extracted != flat and extracted.is_file():
                        extracted.replace(flat)
        tmp_zip.unlink(missing_ok=True)
    else:
        raise RuntimeError("No downloadable assets in latest release")

    ok(f"Installed {pid}")


def download_file(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "claude-workspace-setup"})
    with urllib.request.urlopen(req, timeout=60) as resp, dest.open("wb") as f:
        shutil.copyfileobj(resp, f)


# ---------- Hostname registration ----------


def register_hostname(workspace: Path) -> None:
    host = socket.gethostname()
    if host in HOSTNAME_MAP:
        ok(f"Hostname '{host}' known → {HOSTNAME_MAP[host]}")
        return
    step(f"Unknown hostname: {host}")
    label = input(f"  Label for this machine (e.g. 'Personal MacBook Pro'): ").strip()
    if not label:
        warn("No label provided; skipping registration.")
        return
    # Update CLAUDE.md's hostname table + the dispatcher.
    warn("Add this mapping manually to CLAUDE.md and .claude/hooks/dispatcher.py:")
    print(f"    '{host}': '{label}',")


# ---------- Verification ----------


def verify(workspace: Path) -> None:
    step("Verifying install")
    checks = [
        ("claude", "Claude Code CLI"),
        ("git", "Git"),
        ("gh", "GitHub CLI"),
        ("python3" if detect_os() != "windows" else "python", "Python"),
    ]
    all_good = True
    for binary, label in checks:
        if have(binary):
            ok(f"{label}")
        else:
            err(f"{label} not on PATH")
            all_good = False

    # Key files
    key_files = [
        "CLAUDE.md",
        ".claude/settings.json",
        ".claude/hooks/dispatcher.py",
        "06-context/project-context.md",
        ".obsidian/app.json",
    ]
    for relpath in key_files:
        p = workspace / relpath
        if p.exists():
            ok(f"{relpath}")
        else:
            err(f"MISSING: {relpath}")
            all_good = False

    # Git remote
    r = run(["git", "-C", str(workspace), "remote", "-v"], check=False)
    if r and r.stdout.strip():
        ok("Git remote configured")
    else:
        warn("No Git remote — set it manually: git remote add origin <url>")

    if all_good:
        print("\n\033[32m\u2713 Setup complete.\033[0m Next steps:")
        print(f"  1. Open Obsidian → Open folder as vault → select: {workspace}")
        print(f"  2. Enable community plugins when Obsidian prompts (it will auto-discover installed ones).")
        print(f"  3. From a terminal, cd to the workspace and run: claude")
        print(f"  4. Say 'hello' — you should see workspace context auto-load.")
    else:
        print("\n\033[33m\u26a0 Setup finished with issues above.\033[0m Re-run after fixing.")


# ---------- Orchestration ----------


def main() -> int:
    os_name = detect_os()
    host = socket.gethostname()
    machine = detect_machine_label()

    print(f"\n\033[1mClaude Workspace Installer\033[0m")
    print(f"  OS:        {os_name}")
    print(f"  Hostname:  {host}  →  {machine}")

    if os_name not in ("macos", "windows", "linux"):
        err(f"Unsupported OS: {os_name}")
        return 2

    # 1. Package manager
    if os_name == "macos":
        ensure_homebrew()
    elif os_name == "windows" and not have("winget"):
        err("winget not found. Install 'App Installer' from the Microsoft Store, then re-run.")
        return 2

    # 2. Core tools
    install_git_and_gh(os_name)
    install_claude_code(os_name)
    install_obsidian(os_name)
    if os_name == "windows":
        ensure_python3_shim_windows()

    # 3. Resolve the workspace root = the checkout this script lives in (dir containing AGENTS.md).
    workspace = wait_for_drive()

    # 4. Git sync — pull latest if this is a clone with a remote (idempotent; optional).
    repo_url = DEFAULT_REPO_URL
    if not repo_url:
        repo_url = input(f"\n  Git remote URL for {REPO_NAME} (blank to skip, already cloned): ").strip()
    if repo_url:
        git_clone_or_pull(workspace, repo_url)

    # 5. Obsidian plugins
    install_obsidian_plugins(workspace)

    # 6. Register hostname if new
    register_hostname(workspace)

    # 7. Verify
    verify(workspace)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\033[33mAborted.\033[0m")
        sys.exit(130)
