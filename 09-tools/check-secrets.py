#!/usr/bin/env python3
"""Scan tracked files for well-known secret shapes. Stdlib-only.

Does not depend on gitleaks. Exit 1 on any hit. Skip _archive, lockfiles,
node_modules, *.example, and binary files.

Usage:
  python3 09-tools/check-secrets.py
  python3 09-tools/check-secrets.py --check
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent

# Tight shapes only. Do not copy bootstrap-generator's generic `sk-` or
# secret-assignment patterns — they false-fire on capability-registry URLs
# and radix JSON.
PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("aws-access-key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("github-pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}\b")),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("anthropic-key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("openai-proj-key", re.compile(r"\bsk-proj-[A-Za-z0-9_-]{20,}\b")),
)

SKIP_DIR_PARTS = frozenset({"_archive", "node_modules", ".git", "dist", "__pycache__"})
SKIP_SUFFIXES = frozenset({".example", ".lock", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".woff", ".woff2", ".ttf"})
SKIP_NAMES = frozenset({"package-lock.json", "yarn.lock", "pnpm-lock.yaml", "Cargo.lock", "poetry.lock"})
MAX_BYTES = 1_000_000


def skip_rel(rel: str) -> bool:
    path = Path(rel)
    if any(part in SKIP_DIR_PARTS for part in path.parts):
        return True
    if path.name in SKIP_NAMES:
        return True
    if path.suffix.lower() in SKIP_SUFFIXES or path.name.endswith(".example"):
        return True
    return False


def findings_in_text(text: str) -> list[tuple[str, int]]:
    """Return (pattern-name, line-number) hits. Never echo the secret."""
    hits: list[tuple[str, int]] = []
    for i, line in enumerate(text.splitlines(), 1):
        for name, rx in PATTERNS:
            if rx.search(line):
                hits.append((name, i))
    return hits


def tracked_files(root: Path | None = None) -> list[Path]:
    root = root or ROOT
    try:
        proc = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=str(root),
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []
    out: list[Path] = []
    for raw in proc.stdout.split(b"\0"):
        if not raw:
            continue
        rel = raw.decode("utf-8", errors="replace")
        if skip_rel(rel):
            continue
        path = root / rel
        if not path.is_file():
            continue
        out.append(path)
    return out


def scan_file(path: Path, root: Path | None = None) -> list[str]:
    root = root or ROOT
    try:
        data = path.read_bytes()
    except OSError as e:
        return [f"{path}: unreadable ({e})"]
    if len(data) > MAX_BYTES or b"\0" in data[:8192]:
        return []
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return []
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        rel = str(path)
    return [f"{rel}:{line} {name}" for name, line in findings_in_text(text)]


def scan_root(root: Path | None = None) -> list[str]:
    root = root or ROOT
    errors: list[str] = []
    files = tracked_files(root)
    if not files:
        # Not a git checkout — still scan portable layers so tests can plant trees.
        for folder in (
            "09-tools",
            "02-shared-references",
            "03-skills",
            "08-knowledge",
            "06-context",
            "01-frameworks",
            ".github",
        ):
            base = root / folder
            if not base.is_dir():
                continue
            for path in base.rglob("*"):
                if not path.is_file():
                    continue
                rel = path.relative_to(root).as_posix()
                if skip_rel(rel):
                    continue
                errors.extend(scan_file(path, root))
        return errors
    for path in files:
        errors.extend(scan_file(path, root))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Secret shape scan on tracked files")
    parser.add_argument("--check", action="store_true")
    parser.parse_args()
    errors = scan_root()
    for e in errors:
        print(f"  ✗ {e}", file=sys.stderr)
    if errors:
        print(f"secret scan FAILED — {len(errors)} hit(s); do not echo values", file=sys.stderr)
        return 1
    print("OK check-secrets — no known secret shapes in tracked files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
