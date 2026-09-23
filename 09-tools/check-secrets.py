#!/usr/bin/env python3
"""Scan tracked files for well-known secret shapes. Stdlib-only.

Does not depend on gitleaks. Exit 1 on any hit. Skip _archive, lockfiles,
node_modules, *.example, and binary files.

Second class, `employer-substance` (H25, report-only in wave 0): flags employer
PR/issue/blob/tree URLs, file-level paths inside employer repos, repo-level
employer slugs, and quoted text near those hits. The rules come from the declared
table `context-remotes.json` (`owners`, `employer_path_globs`, `employer_substance`),
read through `profile_resolve.load_table`. Output is `path:line rule` only; matched
text is never printed. Counts ratchet against
`02-shared-references/employer-substance-baseline.json` (may only shrink).

Usage:
  python3 09-tools/check-secrets.py
  python3 09-tools/check-secrets.py --check
  python3 09-tools/check-secrets.py --class employer-substance [--report|--baseline-check|--write-baseline]
      [--staged] [--json] [--root DIR]
  python3 09-tools/check-secrets.py --self-test

Exit codes (employer-substance): 0 ok · 1 baseline exceeded / growth refused ·
2 usage or tables unreadable · 3 baseline absent.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Any, Callable, Optional

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




def secrets_main() -> int:
    errors = scan_root()
    for e in errors:
        print(f"  ✗ {e}", file=sys.stderr)
    if errors:
        print(f"secret scan FAILED — {len(errors)} hit(s); do not echo values", file=sys.stderr)
        return 1
    print("OK check-secrets — no known secret shapes in tracked files")
    return 0


# ---------------------------------------------------------------------------
# employer-substance class (H25). Report-only in wave 0.
# ---------------------------------------------------------------------------

EMP_CLASS = "employer-substance"
EMP_RULES: tuple[str, ...] = ("emp-url", "emp-path", "emp-slug", "emp-quote")
BASELINE_REL = "02-shared-references/employer-substance-baseline.json"
REMOTES_REL = "02-shared-references/delivery-playbooks/context-remotes.json"
EMP_EXCLUDE = frozenset({BASELINE_REL, REMOTES_REL})
QUOTE_WINDOW = 3
# Web routes that make an employer URL PR-, issue-, blob- or tree-level.
URL_KINDS = (
    "pull", "pulls", "issues", "blob", "tree", "pull-requests",
    "src", "commit", "commits", "compare", "browse",
)
_NAME = r"[A-Za-z0-9_.-]*[A-Za-z0-9][A-Za-z0-9_.-]*"
_FILE = r"[A-Za-z0-9_.@+-]*[A-Za-z0-9][A-Za-z0-9_.@+-]*"
_URL_TAIL = r"[^\s)\]>\"'`]*"
_TOKEN_RX = re.compile(r"[A-Za-z0-9_.~$@*/-]+")
# Base64 / SRI integrity blobs (lockfiles) are not paths.
_BLOB_RX = re.compile(r"^sha\d+-", re.IGNORECASE)
_GLOB_CHARS = re.compile(r"[*?\[\]]")
_ALNUM = re.compile(r"[A-Za-z0-9]")
_FENCE_RX = re.compile(r"^\s*(```|~~~)")
_QUOTE_RX = re.compile(r"^\s*>")


class EmpTableError(ValueError):
    """The declared tables could not be read or have the wrong shape."""


def _resolver() -> Any:
    """Lazy import of the vault resolver (3d import rules). None when absent."""
    try:
        if str(TOOLS) not in sys.path:
            sys.path.insert(0, str(TOOLS))
        import profile_resolve  # noqa: PLC0415 — lazy by contract

        return profile_resolve
    except (ImportError, OSError, ValueError):
        return None


class EmpRules:
    """Compiled employer-substance rules from one `context-remotes` table."""

    def __init__(self, table: dict) -> None:
        if not isinstance(table, dict):
            raise EmpTableError("context-remotes: not an object")
        owners = table.get("owners")
        sub = table.get("employer_substance")
        globs = table.get("employer_path_globs", [])
        if not isinstance(owners, list) or not isinstance(sub, dict):
            raise EmpTableError("context-remotes: owners/employer_substance missing")
        if not isinstance(globs, list) or not all(isinstance(g, str) for g in globs):
            raise EmpTableError("context-remotes: employer_path_globs must be a string list")
        names: list[str] = []
        for row in owners:
            if not isinstance(row, dict):
                raise EmpTableError("context-remotes: owners[] must be objects")
            if row.get("class") == "employer" and isinstance(row.get("owner"), str):
                if row["owner"].lower() not in (n.lower() for n in names):
                    names.append(row["owner"])
        lists: dict[str, list[str]] = {}
        for key in ("allow_tokens", "url_prefixes", "domains", "count_keywords"):
            val = sub.get(key, [])
            if not isinstance(val, list) or not all(isinstance(v, str) for v in val):
                raise EmpTableError(f"context-remotes: employer_substance.{key} must be a string list")
            lists[key] = [v for v in val if v]
        self.owners = names
        self.allow = {t.lower() for t in lists["allow_tokens"]}
        self.globs = [g.strip("/") for g in globs if g.strip("/")]
        kinds = "|".join(URL_KINDS)
        self.url_rx: list[re.Pattern[str]] = []
        for prefix in lists["url_prefixes"]:
            body = re.escape(prefix.rstrip("/"))
            self.url_rx.append(re.compile(
                rf"(?<![A-Za-z0-9_.-])(?:https?://)?(?:www\.)?{body}/{_NAME}/(?:{kinds})"
                rf"(?![A-Za-z0-9_-]){_URL_TAIL}",
                re.IGNORECASE,
            ))
        for dom in lists["domains"]:
            self.url_rx.append(re.compile(
                rf"(?<![A-Za-z0-9.-])(?:https?://)?(?:[A-Za-z0-9-]+\.)*{re.escape(dom)}"
                rf"(?![A-Za-z0-9-])(?!\.[A-Za-z0-9]){_URL_TAIL}",
                re.IGNORECASE,
            ))
        if names:
            alt = "|".join(re.escape(n) for n in names)
            self.path_rx: Optional[re.Pattern[str]] = re.compile(
                rf"(?<![A-Za-z0-9_.-])(?:{alt})/{_NAME}/{_FILE}", re.IGNORECASE
            )
            self.slug_rx: Optional[re.Pattern[str]] = re.compile(
                rf"(?<![A-Za-z0-9_.-])({alt})/({_NAME})", re.IGNORECASE
            )
        else:
            self.path_rx = None
            self.slug_rx = None

    # -- per-line matchers ---------------------------------------------------
    def _glob_path_spans(self, line: str) -> list[tuple[int, int]]:
        """projects_root-relative employer globs plus a file component."""
        spans: list[tuple[int, int]] = []
        if not self.globs:
            return spans
        for m in _TOKEN_RX.finditer(line):
            tok = m.group(0)
            if "/" not in tok or _BLOB_RX.match(tok):
                continue
            if m.start() and line[m.start() - 1] in "+=":
                continue
            rel = _projects_rel(tok.rstrip(".,;:"))
            if rel is None:
                continue
            for glob in self.globs:
                gsegs = glob.split("/")
                k = len(gsegs)
                if len(rel) <= k:
                    continue
                head = rel[:k]
                if any(not seg or _GLOB_CHARS.search(seg) for seg in head):
                    continue
                if not all(fnmatchcase(seg, pat) for seg, pat in zip(head, gsegs)):
                    continue
                if not _ALNUM.search(rel[k]) or _GLOB_CHARS.search(rel[k]):
                    continue
                spans.append(m.span())
                break
        return spans

    def line_hits(self, line: str) -> tuple[bool, bool, bool]:
        """(url, path, slug) for one line. URL spans mask path; path masks slug."""
        work = line
        url = False
        for rx in self.url_rx:
            for m in rx.finditer(work):
                url = True
                work = _mask(work, m.span())
        path = False
        if self.path_rx is not None:
            for m in self.path_rx.finditer(work):
                path = True
                work = _mask(work, m.span())
        for span in self._glob_path_spans(work):
            path = True
            work = _mask(work, span)
        slug = False
        if self.slug_rx is not None:
            for m in self.slug_rx.finditer(work):
                repo = m.group(2)
                if repo.lower().endswith(".git"):
                    repo = repo[:-4]
                repo = repo.rstrip(".")
                full = f"{m.group(1)}/{repo}".lower()
                if not _ALNUM.search(repo) or repo.lower() in self.allow or full in self.allow:
                    continue
                slug = True
        return url, path, slug

    def scan_text(self, text: str) -> list[tuple[int, str]]:
        """Sorted (line, rule) hits. Never returns matched text."""
        lines = text.splitlines()
        hits: set[tuple[int, str]] = set()
        anchor: list[int] = []
        quoted: list[int] = []
        in_fence = False
        for i, line in enumerate(lines, 1):
            if _FENCE_RX.match(line):
                in_fence = not in_fence
            elif in_fence or _QUOTE_RX.match(line):
                quoted.append(i)
            url, path, slug = self.line_hits(line)
            if url:
                hits.add((i, "emp-url"))
            if path:
                hits.add((i, "emp-path"))
            if slug:
                hits.add((i, "emp-slug"))
            if url or path:
                anchor.append(i)
        for q in quoted:
            if any(abs(q - a) <= QUOTE_WINDOW for a in anchor):
                hits.add((q, "emp-quote"))
        order = {r: n for n, r in enumerate(EMP_RULES)}
        return sorted(hits, key=lambda h: (h[0], order[h[1]]))


def _mask(line: str, span: tuple[int, int]) -> str:
    a, b = span
    return line[:a] + " " * (b - a) + line[b:]


def _projects_rel(tok: str) -> Optional[list[str]]:
    """Segments relative to projects_root, or None when the token is not relative to it."""
    segs = tok.split("/")
    if "Projects" in segs:
        rel = segs[segs.index("Projects") + 1:]
    elif tok.startswith(("/", "~", "$", ".")):
        return None
    else:
        rel = segs
    while rel and rel[-1] == "":
        rel.pop()
    return rel


def load_emp_rules(resolver: Any, root: Path) -> EmpRules:
    if resolver is None:
        raise EmpTableError("profile_resolve unavailable")
    try:
        table = resolver.load_table("context-remotes", root=root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise EmpTableError(f"context-remotes unreadable ({type(exc).__name__})") from None
    return EmpRules(table)


def _git_out(root: Path, *args: str) -> Optional[bytes]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True, timeout=30, check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return proc.stdout if proc.returncode == 0 else None


def _decode_text(data: Optional[bytes]) -> Optional[str]:
    if data is None or len(data) > MAX_BYTES or b"\0" in data[:8192]:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def emp_sources(root: Path, *, staged: bool = False) -> list[tuple[str, Callable[[], Optional[bytes]]]]:
    """(rel, reader) for every scanned file: tracked (or staged) text, minus the exclusions."""
    out: list[tuple[str, Callable[[], Optional[bytes]]]] = []

    def disk(path: Path) -> Callable[[], Optional[bytes]]:
        def read() -> Optional[bytes]:
            try:
                return path.read_bytes() if path.is_file() else None
            except OSError:
                return None
        return read

    if staged:
        raw = _git_out(root, "diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR")
        for item in (raw or b"").split(b"\0"):
            rel = item.decode("utf-8", errors="replace")
            if rel and rel not in EMP_EXCLUDE:
                out.append((rel, (lambda r=rel: _git_out(root, "show", f":{r}"))))
        return out
    raw = _git_out(root, "ls-files", "-z")
    if raw is not None:
        for item in raw.split(b"\0"):
            rel = item.decode("utf-8", errors="replace")
            if rel and rel not in EMP_EXCLUDE:
                out.append((rel, disk(root / rel)))
        return out
    for path in sorted(root.rglob("*")):
        if ".git" in path.parts or not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel not in EMP_EXCLUDE:
            out.append((rel, disk(path)))
    return out


def emp_scan(rules: EmpRules, root: Path, *, staged: bool = False) -> dict[str, list[tuple[int, str]]]:
    found: dict[str, list[tuple[int, str]]] = {}
    for rel, read in emp_sources(root, staged=staged):
        text = _decode_text(read())
        if text is None:
            continue
        hits = rules.scan_text(text)
        if hits:
            found[rel] = hits
    return found


def emp_counts(found: dict[str, list[tuple[int, str]]]) -> tuple[dict, dict]:
    totals = {r: 0 for r in EMP_RULES}
    paths: dict[str, dict[str, int]] = {}
    for rel in sorted(found):
        per: dict[str, int] = {}
        for _line, rule in found[rel]:
            per[rule] = per.get(rule, 0) + 1
            totals[rule] += 1
        paths[rel] = {r: per[r] for r in EMP_RULES if per.get(r)}
    return totals, paths


def cache_slugs(resolver: Any, home: Optional[Path]) -> tuple[list[str], str]:
    """Employer slugs from the machine-local checkouts cache. Never compared with the baseline."""
    if resolver is None or not hasattr(resolver, "ws_paths"):
        return [], "skipped (resolver unavailable)"
    try:
        tele = Path(resolver.ws_paths(home=home)["telemetry"])
        data = json.loads((tele / "checkouts.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [], "skipped (no cache)"
    except (OSError, ValueError, KeyError, TypeError):
        return [], "skipped (cache unreadable)"
    slugs: list[str] = []
    for row in data.get("checkouts", []) if isinstance(data, dict) else []:
        if not isinstance(row, dict) or row.get("owner_class") != "employer":
            continue
        for rem in row.get("remotes", []) or []:
            slug = rem.get("slug") if isinstance(rem, dict) else None
            if isinstance(slug, str) and "/" in slug and slug.lower() not in (s.lower() for s in slugs):
                slugs.append(slug)
    return slugs, "ok"


def cache_hits(slugs: list[str], root: Path, *, staged: bool = False) -> list[tuple[str, int]]:
    if not slugs:
        return []
    rx = re.compile(
        r"(?<![A-Za-z0-9_.-])(?:" + "|".join(re.escape(s) for s in slugs) + r")(?![A-Za-z0-9_-])",
        re.IGNORECASE,
    )
    out: list[tuple[str, int]] = []
    for rel, read in emp_sources(root, staged=staged):
        text = _decode_text(read())
        if text is None:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if rx.search(line):
                out.append((rel, i))
    return out


def _load_baseline(root: Path) -> Optional[dict]:
    """None when absent; raises EmpTableError when malformed."""
    path = root / BASELINE_REL
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        raise EmpTableError("baseline unreadable") from None
    if (
        not isinstance(data, dict)
        or data.get("schema_version") != 1
        or not isinstance(data.get("paths"), dict)
        or not isinstance(data.get("totals"), dict)
    ):
        raise EmpTableError("baseline has the wrong shape")
    return data


def baseline_growth(paths: dict, baseline: dict, *, only: Optional[set] = None) -> list[tuple[str, str, int, int]]:
    """(path, rule, now, allowed) for every count above the baseline or new."""
    base = baseline.get("paths", {})
    grew: list[tuple[str, str, int, int]] = []
    for rel in sorted(paths):
        if only is not None and rel not in only:
            continue
        allowed = base.get(rel, {}) if isinstance(base.get(rel), dict) else {}
        for rule, n in paths[rel].items():
            cap = allowed.get(rule, 0) if isinstance(allowed.get(rule, 0), int) else 0
            if n > cap:
                grew.append((rel, rule, n, cap))
    return grew


def _head_sha(root: Path) -> str:
    out = _git_out(root, "rev-parse", "HEAD")
    return out.decode().strip() if out else "unknown"


def _dump(obj: dict) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def run_employer(
    args: argparse.Namespace, *, resolver: Any = None, home: Optional[Path] = None
) -> int:
    root = Path(args.root).resolve() if args.root else ROOT
    mode = "write-baseline" if args.write_baseline else "baseline-check" if args.baseline_check else "report"
    env: dict[str, Any] = {"schema_version": 1, "cmd": EMP_CLASS, "mode": mode, "staged": bool(args.staged)}

    def finish(rc: int) -> int:
        env["exit"] = rc
        if args.json:
            print(json.dumps(env, indent=2, ensure_ascii=False))
        return rc

    if args.staged and args.write_baseline:
        print("employer-substance: --write-baseline needs the full tree, not --staged", file=sys.stderr)
        return finish(2)
    try:
        rules = load_emp_rules(resolver, root)
    except EmpTableError as exc:
        print(f"employer-substance: tables unreadable — {exc}", file=sys.stderr)
        env["error"] = str(exc)
        return finish(2)
    found = emp_scan(rules, root, staged=args.staged)
    totals, paths = emp_counts(found)
    slugs, cache_status = cache_slugs(resolver, home)
    chits = cache_hits(slugs, root, staged=args.staged)
    env["totals"] = totals
    env["findings"] = [
        {"path": rel, "line": line, "rule": rule} for rel in sorted(found) for line, rule in found[rel]
    ]
    env["cache_derived"] = {
        "status": cache_status,
        "hits": [{"path": rel, "line": line} for rel, line in chits],
        "compared_with_baseline": False,
    }
    human = not args.json
    if human:
        for item in env["findings"]:
            print(f"{item['path']}:{item['line']} {item['rule']}")
        for rel, line in chits:
            print(f"cache-derived: {rel}:{line} emp-slug")
        if not chits:
            print(f"cache-derived: {len(chits)} hit(s) — {cache_status}")
        summary = " · ".join(f"{r} {totals[r]}" for r in EMP_RULES)
        print(f"employer-substance ({mode}, report-only): {summary} in {len(paths)} file(s)")

    if mode == "report":
        return finish(0)

    try:
        baseline = _load_baseline(root)
    except EmpTableError as exc:
        print(f"employer-substance: {exc}", file=sys.stderr)
        env["error"] = str(exc)
        return finish(2)

    if mode == "baseline-check":
        if baseline is None:
            print(f"employer-substance: baseline absent ({BASELINE_REL})", file=sys.stderr)
            env["error"] = "baseline absent"
            return finish(3)
        only = set(found) if args.staged else None
        grew = baseline_growth(paths, baseline, only=only)
        env["growth"] = [{"path": p, "rule": r, "count": n, "baseline": c} for p, r, n, c in grew]
        for p, r, n, c in grew:
            print(f"  ✗ {p} {r} {n} > baseline {c}", file=sys.stderr)
        if grew:
            print(f"employer-substance baseline EXCEEDED — {len(grew)} (path, rule) count(s)", file=sys.stderr)
            return finish(1)
        if human:
            print("OK employer-substance — no (path, rule) count above the baseline")
        return finish(0)

    # write-baseline
    if baseline is not None:
        grew = baseline_growth(paths, baseline)
        env["growth"] = [{"path": p, "rule": r, "count": n, "baseline": c} for p, r, n, c in grew]
        if grew:
            for p, r, n, c in grew:
                print(f"  ✗ {p} {r} {n} > baseline {c}", file=sys.stderr)
            print("employer-substance: refusing to rewrite a baseline that would grow", file=sys.stderr)
            return finish(1)
    record = {
        "schema_version": 1,
        "generated_at": date.today().isoformat(),
        "generated_from": _head_sha(root),
        "rules": list(EMP_RULES),
        "totals": totals,
        "paths": paths,
    }
    target = root / BASELINE_REL
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_dump(record), encoding="utf-8")
    except OSError as exc:
        print(f"employer-substance: cannot write baseline ({type(exc).__name__})", file=sys.stderr)
        return finish(2)
    env["written"] = BASELINE_REL
    if human:
        print(f"wrote {BASELINE_REL}")
    return finish(0)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Secret shape scan on tracked files")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--class", dest="klass", choices=["secrets", EMP_CLASS], default="secrets")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--report", action="store_true")
    mode.add_argument("--baseline-check", action="store_true")
    mode.add_argument("--write-baseline", action="store_true")
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", default="")
    parser.add_argument("--self-test", action="store_true")
    return parser


def main(argv: Optional[list[str]] = None, *, resolver: Any = "auto", home: Optional[Path] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    emp_only = args.report or args.baseline_check or args.write_baseline or args.staged or args.json or args.root
    if args.klass == EMP_CLASS:
        return run_employer(args, resolver=_resolver() if resolver == "auto" else resolver, home=home)
    if emp_only:
        parser.error("--report/--baseline-check/--write-baseline/--staged/--json/--root need --class employer-substance")
    return secrets_main()


# ---------------------------------------------------------------------------
# --self-test (fakes profile_resolve; synthetic owners in temp dirs only)
# ---------------------------------------------------------------------------

FIXTURES = TOOLS / "fixtures" / "employer_substance"


class _FakeResolver:
    """Stands in for profile_resolve until T2 lands (3d parallel-wave rule)."""

    class TableError(ValueError):
        pass

    def __init__(self, home: Path, *, broken: bool = False) -> None:
        self.home = home
        self.broken = broken

    def load_table(self, name: str, *, root: Optional[Path] = None) -> dict:
        if self.broken:
            raise self.TableError("fixture: broken table")
        path = Path(root or ROOT) / REMOTES_REL
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise self.TableError(str(exc)) from None

    def ws_paths(self, *, home: Optional[Path] = None) -> dict:
        base = Path(home or self.home) / ".config" / "snds-workspace"
        return {"base": base, "telemetry": base / "telemetry", "control": base / "control"}


def _run_captured(argv: list[str], resolver: Any, home: Path) -> tuple[int, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            rc = main(argv, resolver=resolver, home=home)
        except SystemExit as exc:  # argparse usage errors
            rc = int(exc.code or 0)
    return rc, out.getvalue() + err.getvalue()


def self_test() -> int:
    failures: list[str] = []
    passed = 0

    def check(name: str, cond: bool, detail: str = "") -> None:
        nonlocal passed
        if cond:
            passed += 1
        else:
            failures.append(f"{name}{(' — ' + detail) if detail else ''}")

    planted_markers = json.loads((FIXTURES / "planted-markers.json").read_text(encoding="utf-8"))["markers"]

    def leaks(text: str) -> list[str]:
        return [m for m in planted_markers if m.lower() in text.lower()]

    # Secrets class unchanged.
    check("secrets: planted key still flagged",
          any(n == "aws-access-key" for n, _ in findings_in_text("k=" + "AKIA" + "FAKESECRETTEST99\n")))
    check("secrets: clean prose passes", findings_in_text("No keys here.\n") == [])

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        home = tmp / "home"
        (home / ".config" / "snds-workspace" / "telemetry").mkdir(parents=True)
        root = tmp / "vault"
        (root / "notes").mkdir(parents=True)
        (root / Path(REMOTES_REL).parent).mkdir(parents=True)
        shutil.copy(FIXTURES / "context-remotes.json", root / REMOTES_REL)
        shutil.copy(FIXTURES / "planted.md", root / "notes" / "planted.md")
        shutil.copy(FIXTURES / "clean.md", root / "notes" / "clean.md")
        fake = _FakeResolver(home)
        rules = load_emp_rules(fake, root)

        # Planted URL, path and slug are flagged, at the lines the fixture declares.
        expect = json.loads((FIXTURES / "expected.json").read_text(encoding="utf-8"))
        got = rules.scan_text((root / "notes" / "planted.md").read_text(encoding="utf-8"))
        got_pairs = sorted([line, rule] for line, rule in got)
        check("planted hits match expected.json", got_pairs == sorted(expect["planted.md"]),
              f"got {got_pairs}")
        for rule in ("emp-url", "emp-path", "emp-slug", "emp-quote"):
            check(f"planted: {rule} flagged", any(r == rule for _, r in got))

        # Allowlisted owner-level tokens and non-employer owners pass.
        clean = rules.scan_text((root / "notes" / "clean.md").read_text(encoding="utf-8"))
        check("allowlisted owner-level tokens pass", clean == [], f"got {clean}")

        # Excluded files are never scanned.
        (root / BASELINE_REL).parent.mkdir(parents=True, exist_ok=True)
        found = emp_scan(rules, root)
        check("context-remotes.json excluded", REMOTES_REL not in found)

        # Report mode: exit 0, output is path:line rule only, never the planted text.
        rc, text = _run_captured(["--class", EMP_CLASS, "--report", "--root", str(root)], fake, home)
        check("report exits 0", rc == 0, f"rc={rc}")
        check("report prints path:line rule", "notes/planted.md:" in text and " emp-url" in text)
        check("report never prints planted text", not leaks(text), f"leaked {leaks(text)}")
        rc, text = _run_captured(["--class", EMP_CLASS, "--report", "--json", "--root", str(root)], fake, home)
        check("json report exits 0", rc == 0)
        check("json never prints planted text", not leaks(text), f"leaked {leaks(text)}")
        try:
            env = json.loads(text)
            check("json envelope", env.get("schema_version") == 1 and env.get("cmd") == EMP_CLASS)
        except ValueError:
            check("json envelope parses", False, text[:80])

        # Tables unreadable → exit 2 (resolver absent, or load_table raising).
        rc, _ = _run_captured(["--class", EMP_CLASS, "--report", "--root", str(root)], None, home)
        check("no resolver → exit 2", rc == 2, f"rc={rc}")
        rc, _ = _run_captured(["--class", EMP_CLASS, "--report", "--root", str(root)],
                              _FakeResolver(home, broken=True), home)
        check("broken table → exit 2", rc == 2, f"rc={rc}")

        # Baseline: absent → 3; write → 0; check → 0.
        rc, _ = _run_captured(["--class", EMP_CLASS, "--baseline-check", "--root", str(root)], fake, home)
        check("baseline absent → exit 3", rc == 3, f"rc={rc}")
        rc, text = _run_captured(["--class", EMP_CLASS, "--write-baseline", "--root", str(root)], fake, home)
        check("write-baseline creates", rc == 0 and (root / BASELINE_REL).is_file(), f"rc={rc}")
        check("write-baseline output never prints planted text", not leaks(text))
        base_bytes = (root / BASELINE_REL).read_bytes()
        check("baseline file never holds planted text", not leaks(base_bytes.decode("utf-8")))
        rc, _ = _run_captured(["--class", EMP_CLASS, "--baseline-check", "--root", str(root)], fake, home)
        check("baseline-check holds", rc == 0, f"rc={rc}")

        # Baseline growth → --baseline-check exits 1; --write-baseline refuses and leaves the file.
        grow = (FIXTURES / "growth.md").read_text(encoding="utf-8")
        (root / "notes" / "planted.md").write_text(
            (root / "notes" / "planted.md").read_text(encoding="utf-8") + grow, encoding="utf-8")
        (root / "notes" / "new.md").write_text(grow, encoding="utf-8")
        rc, text = _run_captured(["--class", EMP_CLASS, "--baseline-check", "--root", str(root)], fake, home)
        check("growth → baseline-check exit 1", rc == 1, f"rc={rc}")
        check("growth output never prints planted text", not leaks(text))
        rc, _ = _run_captured(["--class", EMP_CLASS, "--write-baseline", "--root", str(root)], fake, home)
        check("write-baseline refuses growth", rc == 1, f"rc={rc}")
        check("refused write leaves baseline bytes", (root / BASELINE_REL).read_bytes() == base_bytes)

        # Shrink → rewrite allowed, and the ratchet tightens.
        (root / "notes" / "new.md").unlink()
        shutil.copy(FIXTURES / "clean.md", root / "notes" / "planted.md")
        rc, _ = _run_captured(["--class", EMP_CLASS, "--write-baseline", "--root", str(root)], fake, home)
        check("write-baseline accepts shrink", rc == 0, f"rc={rc}")
        shrunk = json.loads((root / BASELINE_REL).read_text(encoding="utf-8"))
        check("shrunk baseline totals zero", all(v == 0 for v in shrunk["totals"].values()), str(shrunk["totals"]))
        check("baseline keys in schema order",
              list(shrunk) == ["schema_version", "generated_at", "generated_from", "rules", "totals", "paths"])
        shutil.copy(FIXTURES / "planted.md", root / "notes" / "planted.md")
        rc, _ = _run_captured(["--class", EMP_CLASS, "--baseline-check", "--root", str(root)], fake, home)
        check("re-planting after shrink → exit 1", rc == 1, f"rc={rc}")

        # Cache-derived slugs: printed separately, never change the exit code or the counts.
        shutil.copy(FIXTURES / "clean.md", root / "notes" / "planted.md")
        (root / "notes" / "cached.md").write_text(
            (FIXTURES / "cache-planted.md").read_text(encoding="utf-8"), encoding="utf-8")
        argv = ["--class", EMP_CLASS, "--baseline-check", "--root", str(root)]
        rc_before, text_before = _run_captured(argv + ["--json"], fake, home)
        shutil.copy(FIXTURES / "checkouts.json",
                    home / ".config" / "snds-workspace" / "telemetry" / "checkouts.json")
        rc_after, text_after = _run_captured(argv, fake, home)
        check("cache-derived line printed", "cache-derived: notes/cached.md:" in text_after, text_after[-200:])
        check("cache-derived never changes exit", rc_before == rc_after == 0, f"{rc_before} {rc_after}")
        check("cache-derived output never prints slugs", not leaks(text_after), f"leaked {leaks(text_after)}")
        rc_json, text_json = _run_captured(argv + ["--json"], fake, home)
        try:
            env_before, env_after = json.loads(text_before), json.loads(text_json)
            check("cache-derived never changes totals", env_before["totals"] == env_after["totals"])
            check("cache-derived flagged not compared",
                  env_after["cache_derived"]["compared_with_baseline"] is False
                  and len(env_after["cache_derived"]["hits"]) >= 1)
        except (ValueError, KeyError) as exc:
            check("cache-derived json", False, repr(exc))

        # --staged reads the index, not the working tree.
        git_env = dict(os.environ, HOME=str(home), GIT_CONFIG_NOSYSTEM="1",
                       GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
                       GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")
        repo = tmp / "repo"
        (repo / Path(REMOTES_REL).parent).mkdir(parents=True)
        shutil.copy(FIXTURES / "context-remotes.json", repo / REMOTES_REL)
        try:
            subprocess.run(["git", "init", "-q", str(repo)], env=git_env, check=True, timeout=20,
                           capture_output=True)
            (repo / "a.md").write_text((FIXTURES / "clean.md").read_text(encoding="utf-8"), encoding="utf-8")
            subprocess.run(["git", "-C", str(repo), "add", "a.md"], env=git_env, check=True, timeout=20)
            (repo / "a.md").write_text((FIXTURES / "planted.md").read_text(encoding="utf-8"),
                                       encoding="utf-8")
            rc, text = _run_captured(["--class", EMP_CLASS, "--report", "--staged", "--root", str(repo)],
                                     fake, home)
            check("staged scan reads the clean index", rc == 0 and "a.md:" not in text, text[-200:])
            subprocess.run(["git", "-C", str(repo), "add", "a.md"], env=git_env, check=True, timeout=20)
            rc, text = _run_captured(["--class", EMP_CLASS, "--report", "--staged", "--root", str(repo)],
                                     fake, home)
            check("staged scan flags staged substance", rc == 0 and "a.md:" in text, text[-200:])
            rc, _ = _run_captured(["--class", EMP_CLASS, "--write-baseline", "--staged", "--root", str(repo)],
                                  fake, home)
            check("--staged --write-baseline is a usage error", rc == 2, f"rc={rc}")
        except (OSError, subprocess.SubprocessError) as exc:
            check("staged fixture git", False, repr(exc))

    # Usage: employer-only flags without the class → exit 2.
    rc, _ = _run_captured(["--report"], None, Path(tempfile.gettempdir()))
    check("--report without --class → usage exit 2", rc == 2, f"rc={rc}")

    for f in failures:
        print(f"  ✗ {f}", file=sys.stderr)
    if failures:
        print(f"check-secrets self-test FAILED — {len(failures)} of {passed + len(failures)}", file=sys.stderr)
        return 1
    print(f"OK check-secrets self-test — {passed} checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
