#!/usr/bin/env python3
"""Land vendor-surface artifacts in the vault (clipboard, file, or drop-folder).

Write-through is the contract ([[decision-vendor-surface-artifacts]]). This CLI
is the harvest path when the bytes already exist outside the git tree: a copied
Claude/ChatGPT/Gemini canvas, an HTML preview download, or a drop in
`05-artifacts/inbox/`.

Stdlib-only. Never scrapes vendor UIs. Never copies employer (`cpes-software`,
`c8`) paths into this vault. HTML stays HTML. Secret-scan before write.
Does not overwrite — bumps the artifact-standards minor version.

Usage:
  python3 09-tools/artifact-ingest.py --inbox
  python3 09-tools/artifact-ingest.py --from-clipboard [--context X] [--descriptor Y]
  python3 09-tools/artifact-ingest.py --from-file PATH
  python3 09-tools/artifact-ingest.py --check          # pending inbox files; exit 1 if any
  python3 09-tools/artifact-ingest.py --self-test
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
INBOX = ROOT / "05-artifacts" / "inbox"
DONE = INBOX / ".done"
DEFAULT_OUT = ROOT / "05-artifacts" / "active"

EMPLOYER_MARKERS = ("cpes-software", "/c8/", "\\c8\\", "centric-ui")
SKIP_INBOX_NAMES = frozenset({"readme.md", ".ds_store"})


def load_secrets():
    path = TOOLS / "check-secrets.py"
    spec = importlib.util.spec_from_file_location("check_secrets", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def refuse_path(path: Path) -> str | None:
    text = path.resolve().as_posix().lower()
    for marker in EMPLOYER_MARKERS:
        if marker.strip("\\").lower() in text:
            return f"employer path ({marker.strip()})"
    return None


def sniff(text: str, source_name: str = "") -> str:
    suffix = Path(source_name).suffix.lower()
    if suffix in {".html", ".htm"}:
        return "html"
    if suffix in {".tsx", ".canvas.tsx"} or source_name.endswith(".canvas.tsx"):
        return "canvas.tsx"
    if suffix in {".md", ".markdown"}:
        return "md"
    s = text.lstrip().lower()
    if s.startswith("<!doctype html") or s.startswith("<html"):
        return "html"
    if "from \"cursor/canvas\"" in text or "from 'cursor/canvas'" in text:
        return "canvas.tsx"
    return "md"


def slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s[:48] or "ingest"


def versioned(dest_dir: Path, context: str, descriptor: str, ext: str, day: str) -> Path:
    major, minor = 1, 0
    while True:
        name = f"{context}_{descriptor}_v{major}.{minor}_{day}.{ext}"
        cand = dest_dir / name
        if not cand.exists():
            return cand
        minor += 1
        if minor > 99:
            major += 1
            minor = 0


def add_provenance(text: str, kind: str, source: str, day: str) -> str:
    note = f"captured: {day} · source: {source} · via: artifact-ingest"
    if kind == "html":
        if "via: artifact-ingest" in text:
            return text
        return f"<!-- {note} -->\n" + text
    if kind == "canvas.tsx":
        if "via: artifact-ingest" in text:
            return text
        return f"// {note}\n" + text
    if text.lstrip().startswith("---"):
        return text
    return f"---\ncaptured: {day}\nsource: {source}\nvia: artifact-ingest\n---\n\n" + text


def read_clipboard() -> str:
    cmds = (
        ["pbpaste"],
        ["wl-paste"],
        ["xclip", "-selection", "clipboard", "-o"],
    )
    last = "no clipboard tool"
    for cmd in cmds:
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        except OSError as e:
            last = str(e)
            continue
        if proc.returncode == 0:
            return proc.stdout
        last = proc.stderr.strip() or f"{cmd[0]} exit {proc.returncode}"
    raise SystemExit(f"error: clipboard read failed ({last})")


def write_bytes(dest: Path, text: str) -> None:
    secrets = load_secrets()
    hits = secrets.findings_in_text(text)
    if hits:
        kinds = ", ".join(sorted({n for n, _ln in hits}))
        raise SystemExit(f"error: secret scan hit ({kinds}) — not written")
    blocked = refuse_path(dest)
    if blocked:
        raise SystemExit(f"error: refuse dest — {blocked}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text, encoding="utf-8")


def resolve_out(args: argparse.Namespace, kind: str) -> Path:
    if args.out:
        dest = Path(args.out).expanduser()
        if not dest.is_absolute():
            dest = ROOT / dest
        return dest
    if args.project:
        proj = ROOT / "07-projects" / args.project
        if kind == "canvas.tsx":
            return proj / "canvases"
        return proj
    return DEFAULT_OUT


def stem_parts(args: argparse.Namespace, kind: str, source_name: str) -> tuple[str, str, str, str]:
    day = dt.date.today().isoformat()
    context = args.context or "ingest"
    if args.descriptor:
        descriptor = slug(args.descriptor)
    elif source_name:
        descriptor = slug(Path(source_name).stem.replace(".canvas", ""))
    else:
        descriptor = "clipboard" if args.from_clipboard else "drop"
    ext = "canvas.tsx" if kind == "canvas.tsx" else kind
    return context, descriptor, ext, day


def dest_file(args: argparse.Namespace, kind: str, source_name: str) -> Path:
    out = resolve_out(args, kind)
    blocked = refuse_path(out)
    if blocked:
        raise SystemExit(f"error: refuse dest — {blocked}")
    if out.suffix:  # explicit file path
        if out.exists():
            raise SystemExit(f"error: exists, will not overwrite: {out}")
        return out
    context, descriptor, ext, day = stem_parts(args, kind, source_name)
    return versioned(out, context, descriptor, ext, day)


def ingest_text(text: str, source: str, args: argparse.Namespace, source_name: str = "") -> Path:
    if not text.strip():
        raise SystemExit("error: empty content")
    kind = args.as_format or sniff(text, source_name)
    dest = dest_file(args, kind, source_name)
    body = add_provenance(text, kind, source, dt.date.today().isoformat())
    write_bytes(dest, body)
    try:
        rel = dest.relative_to(ROOT).as_posix()
    except ValueError:
        rel = str(dest)
    print(f"ingested: {source} → {rel}")
    return dest


def inbox_files() -> list[Path]:
    if not INBOX.is_dir():
        return []
    out = []
    for p in sorted(INBOX.iterdir()):
        if p.name.startswith(".") or p.name.lower() in SKIP_INBOX_NAMES:
            continue
        if p.is_file():
            out.append(p)
    return out


def cmd_inbox(args: argparse.Namespace) -> int:
    pending = inbox_files()
    if not pending:
        print("artifact-ingest: inbox empty")
        return 0
    n = 0
    for src in pending:
        blocked = refuse_path(src)
        if blocked:
            print(f"skip ({blocked}): {src.name}")
            continue
        text = src.read_text(encoding="utf-8", errors="replace")
        dest = ingest_text(text, f"inbox:{src.name}", args, source_name=src.name)
        DONE.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(DONE / src.name))
        n += 1
        _ = dest
    print(f"artifact-ingest: promoted {n}, pending was {len(pending)}")
    return 0


def cmd_check() -> int:
    pending = inbox_files()
    if not pending:
        print("artifact-ingest: inbox empty")
        return 0
    for p in pending:
        print(f"pending: {p.name}")
    print(f"artifact-ingest: {len(pending)} inbox file(s) waiting — run --inbox")
    return 1


def self_test() -> int:
    errors = 0

    def check(cond: bool, msg: str) -> None:
        nonlocal errors
        if not cond:
            print(f"FAIL {msg}")
            errors += 1

    check(sniff("<!DOCTYPE html><html></html>", "") == "html", "sniff html")
    check(sniff("# Hello\n", "note.md") == "md", "sniff md")
    check(sniff('import { H1 } from "cursor/canvas"\n', "x.canvas.tsx") == "canvas.tsx", "sniff canvas")
    check(refuse_path(Path("/tmp/cpes-software/cds/foo.html")) is not None, "refuse employer")
    check(refuse_path(ROOT / "05-artifacts" / "active" / "ok.md") is None, "allow vault dest")
    check(slug("ChatGPT Canvas!") == "chatgpt-canvas", "slug")
    with __import__("tempfile").TemporaryDirectory() as td:
        d = Path(td)
        a = versioned(d, "ingest", "clip", "md", "2026-09-11")
        a.write_text("x", encoding="utf-8")
        b = versioned(d, "ingest", "clip", "md", "2026-09-11")
        check(a.name.endswith("_v1.0_2026-09-11.md"), "first version")
        check(b.name.endswith("_v1.1_2026-09-11.md"), "bump version")
    body = add_provenance("# Hi\n", "md", "clipboard", "2026-09-11")
    check(body.startswith("---\ncaptured: 2026-09-11"), "md provenance")
    if errors:
        print(f"artifact-ingest --self-test: {errors} error(s)")
        return 1
    print("artifact-ingest --self-test: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--inbox", action="store_true", help="promote 05-artifacts/inbox/ files")
    src.add_argument("--from-clipboard", action="store_true", help="read the OS clipboard")
    src.add_argument("--from-file", metavar="PATH", help="read one file")
    ap.add_argument("--check", action="store_true", help="exit 1 if inbox has pending files")
    ap.add_argument("--self-test", action="store_true", help="fixtures; no disk writes to the vault")
    ap.add_argument("--out", help="explicit dest file or directory (under the vault)")
    ap.add_argument("--project", help="07-projects/<id> folder name (e.g. 19-workspace-brain)")
    ap.add_argument("--context", help="artifact-standards context segment")
    ap.add_argument("--descriptor", help="artifact-standards descriptor segment")
    ap.add_argument("--as", dest="as_format", choices=("html", "md", "canvas.tsx"), help="override sniff")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if args.check:
        return cmd_check()
    if args.inbox:
        return cmd_inbox(args)
    if args.from_clipboard:
        return 0 if ingest_text(read_clipboard(), "clipboard", args) else 1
    if args.from_file:
        src_path = Path(args.from_file).expanduser()
        blocked = refuse_path(src_path)
        if blocked:
            raise SystemExit(f"error: refuse source — {blocked}")
        text = src_path.read_text(encoding="utf-8", errors="replace")
        ingest_text(text, src_path.name, args, source_name=src_path.name)
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
