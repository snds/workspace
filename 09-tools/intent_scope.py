#!/usr/bin/env python3
"""intent_scope.py — write scope as task data (H9): the fast, fail-open kernel.

A task graph row's `writes` and `forbids` cells are the task's declared write scope. This module
holds the grammar both of them share (moved here from intent-run.py so the pinned hook lib and the
CLI read one copy), the disjoint-wave lint, the active-task pointer, and the per-path check the
pre-write accelerators run.

  writes    comma-separated at bracket depth 0: paths and globs (`*`, `**`, `?`, `{a,b}`),
            `path.json[key.path, ...]` selectors, `@Tn` for another task's writes, or `none`.
            A literal path also covers everything under it (a directory). A token with whitespace
            is prose: the cell is then not machine-checkable and nothing is reported as outside it.
  forbids   the same grammar; prose tokens contribute only their `backticked` paths.
  enforce   an optional task-graph column; `true` makes `intent-run scope --check-path` exit 1 on a
            finding. The hook step is report-only whatever it says (blocking opt-ins are per machine).

Active-task pointer (one JSON file: spec, task, repo, set_at):
  the workspace (or a linked worktree of it)  <top>/.workspace/state/active-task  (gitignored)
  any other repo                             ~/.config/snds-workspace/state/telemetry/<slug>/active-task
The second is never inside the repo, so `git add -A` in an employer checkout cannot sweep it.
Findings from the hook go to `scope.jsonl` beside the pointer (non-workspace rows carry a path hash,
never the path).

Stdlib only; Python 3.9+. Never calls git: the pointer and the slug come from plain file reads.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

POINTER_WS_REL = ".workspace/state/active-task"
TELEMETRY_PARTS = (".config", "snds-workspace", "state", "telemetry")
POINTER_NAME = "active-task"
LOG_NAME = "scope.jsonl"
CHECK_BUDGET_S = 0.05
BLANK_CELLS = ("", "none", "-", "—", "n/a")
TRUE_CELLS = ("true", "yes", "y", "1", "on", "enforce")
BACKTICK_RE = re.compile(r"`([^`\s]+)`")
# The sensitive denylist (plan H9): a change here needs a writes entry that owns it explicitly.
# LOCKFILES must equal check-secrets.py SKIP_NAMES (TestIntentScope pins the two together).
LOCKFILES = ("package-lock.json", "yarn.lock", "pnpm-lock.yaml", "Cargo.lock", "poetry.lock")
MANIFESTS = ("package.json", "pyproject.toml", "requirements*.txt", "Pipfile", "Gemfile", "Cargo.toml", "go.mod")
SENSITIVE_GLOBS = tuple(f"**/{n}" for n in LOCKFILES + MANIFESTS) + (".github/workflows/**", "**/.env*", "**/*.pem")


# --------------------------------------------------------------------------- table grammar

def _split_row(line: str) -> List[str]:
    """Split a markdown table row on unescaped pipes; `\\|` becomes a literal pipe."""
    inner = line.strip()
    if inner.startswith("|"):
        inner = inner[1:]
    if inner.endswith("|") and not inner.endswith("\\|"):
        inner = inner[:-1]
    cells: List[str] = []
    buf: List[str] = []
    i = 0
    while i < len(inner):
        ch = inner[i]
        if ch == "\\" and i + 1 < len(inner) and inner[i + 1] == "|":
            buf.append("|")
            i += 2
            continue
        if ch == "|":
            cells.append("".join(buf).strip())
            buf = []
            i += 1
            continue
        buf.append(ch)
        i += 1
    cells.append("".join(buf).strip())
    return cells


def _parse_table(section: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    header: Optional[List[str]] = None
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            if header and rows:
                break
            continue
        cells = _split_row(line)
        if all(set(c) <= set("-: ") and c for c in cells):
            continue
        if header is None:
            header = [re.sub(r"[^a-z0-9]+", "_", c.lower()).strip("_") for c in cells]
            continue
        rows.append({header[i]: cells[i] if i < len(cells) else "" for i in range(len(header))})
    return rows


def _section(body: str, heading: str) -> str:
    pat = re.compile(rf"^##\s+{re.escape(heading)}\s*$", re.IGNORECASE | re.M)
    m = pat.search(body)
    if not m:
        return ""
    start = m.end()
    nxt = re.search(r"^##\s+\S", body[start:], re.M)
    return body[start: start + nxt.start()] if nxt else body[start:]


def _split_spec(text: str) -> Tuple[Dict[str, str], str]:
    """(frontmatter key → value with ` #` comments dropped, body). Enough for scope keys only."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    meta: Dict[str, str] = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*)\s*:\s*(.*)$", line)
        if m:
            val = re.split(r"\s+#", m.group(2), maxsplit=1)[0].strip()
            meta[m.group(1)] = val[1:-1] if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'" else val
    return meta, text[end + 4:]


def task_rows(text: str) -> List[Dict[str, str]]:
    """The task graph rows of a spec's text (frontmatter skipped)."""
    return _parse_table(_section(_split_spec(text)[1], "Task graph"))


def _glob_list(cell: str) -> List[dict]:
    return [_entry(p, None) for tok in _split_depth0(cell or "") if not _is_blank(tok)
            for p in _expand_braces(tok.strip().strip("`")) if not re.search(r"\s", p)]


def spec_scope(text: str, task_id: str) -> dict:
    """task_scope plus the spec-level sets: H8 `## Preserve` globs, frontmatter `generated:` globs
    (allowed anywhere) and `contract:` paths."""
    meta, body = _split_spec(text)
    sc = task_scope(_parse_table(_section(body, "Task graph")), task_id)
    sc["preserve"] = [e for r in _parse_table(_section(body, "Preserve")) for e in _glob_list(r.get("glob") or "")]
    sc["generated"] = _glob_list(meta.get("generated") or "")
    sc["contract"] = [e["path"] for e in _glob_list(meta.get("contract") or "")]
    return sc


# --------------------------------------------------------------------------- write grammar

def _split_depth0(cell: str) -> List[str]:
    out: List[str] = []
    buf: List[str] = []
    depth = 0
    for ch in cell:
        if ch in "[{":
            depth += 1
        elif ch in "]}":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            out.append("".join(buf).strip())
            buf = []
            continue
        buf.append(ch)
    out.append("".join(buf).strip())
    return [t for t in out if t]


def _expand_braces(pat: str) -> List[str]:
    m = re.search(r"\{([^{}]*)\}", pat)
    if not m:
        return [pat]
    out: List[str] = []
    for alt in m.group(1).split(","):
        out.extend(_expand_braces(pat[: m.start()] + alt.strip() + pat[m.end():]))
    return out


def _glob_re(pat: str) -> "re.Pattern":
    i = 0
    out = []
    while i < len(pat):
        if pat.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pat.startswith("**", i):
            out.append(".*")
            i += 2
        elif pat[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pat[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pat[i]))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def _is_glob(pat: str) -> bool:
    return any(ch in pat for ch in "*?")


def parse_write_token(tok: str) -> dict:
    tok = tok.strip().strip("`")
    m = re.fullmatch(r"@(\S+)", tok)
    if m:
        return {"kind": "ref", "id": m.group(1)}
    m = re.fullmatch(r"(.+?)\[(.*)\]", tok)
    if m:
        sels = [s.strip() for s in _split_depth0(m.group(2)) if s.strip()]
        return {"kind": "path", "path": m.group(1).strip(), "selectors": sels}
    return {"kind": "path", "path": tok, "selectors": None}


def _entry(path: str, selectors) -> dict:
    path = path.strip()
    if path.startswith("./"):
        path = path[2:]
    return {"path": path, "selectors": selectors, "re": _glob_re(path), "glob": _is_glob(path)}


def entry_matches(ent: dict, rel: str) -> bool:
    """A glob matches by pattern; a literal path matches itself and everything under it."""
    if ent["re"].match(rel):
        return True
    if ent["glob"]:
        return False
    base = ent["path"].rstrip("/")
    return bool(base) and rel.startswith(base + "/")


def _is_blank(cell: Optional[str]) -> bool:
    return (cell or "").strip().lower() in BLANK_CELLS


def _cell_scope(cell: str, by_id: Dict[str, dict], column: str, seen: set) -> Tuple[List[dict], List[str]]:
    """(entries, prose tokens) for one writes/forbids cell; `@Tn` pulls in that task's same column."""
    if _is_blank(cell):
        return [], []
    ents: List[dict] = []
    prose: List[str] = []
    for tok in _split_depth0(cell):
        raw = tok.strip()
        bare = raw.strip("`")
        if not bare:
            continue
        if re.search(r"\s", bare):
            prose.append(raw)
            if column == "forbids":
                for p in BACKTICK_RE.findall(raw):
                    ents.extend(_entry(x, None) for x in _expand_braces(p))
            continue
        ent = parse_write_token(bare)
        if ent["kind"] == "ref":
            key = ent["id"].strip().upper()
            if key in seen or key not in by_id:
                if key not in by_id:
                    prose.append(raw)
                continue
            sub_e, sub_p = _cell_scope(by_id[key].get(column) or "", by_id, column, seen | {key})
            ents.extend(sub_e)
            prose.extend(sub_p)
            continue
        for p in _expand_braces(ent["path"]):
            ents.append(_entry(p, ent["selectors"]))
    return ents, prose


def index_rows(rows: List[Dict[str, str]]) -> Dict[str, dict]:
    return {(r.get("id") or "").strip().upper(): r for r in rows if (r.get("id") or "").strip()}


def task_scope(rows: List[Dict[str, str]], task_id: str) -> dict:
    """{task, writes, forbids, prose_writes, prose_forbids, checkable, enforce} for one task."""
    by_id = index_rows(rows)
    key = (task_id or "").strip().upper()
    if key not in by_id:
        raise KeyError(f"unknown task {task_id}")
    row = by_id[key]
    writes, pw = _cell_scope(row.get("writes") or "", by_id, "writes", {key})
    forbids, pf = _cell_scope(row.get("forbids") or "", by_id, "forbids", {key})
    has_writes_col = "writes" in row
    return {"task": (row.get("id") or "").strip(), "writes": writes, "forbids": forbids,
            "prose_writes": pw, "prose_forbids": pf,
            "checkable": has_writes_col and not pw,
            "enforce": (row.get("enforce") or "").strip().lower() in TRUE_CELLS}


_SENSITIVE = [_entry(g, None) for g in SENSITIVE_GLOBS]


def _static_prefix(pat: str) -> str:
    m = re.search(r"[*?]", pat)
    return pat if m is None else pat[: m.start()]


def owns(ent: dict, rel: str, sensitive: dict) -> bool:
    """An explicit owner of a sensitive path: a literal entry, an entry whose last segment names
    something (`**/package.json`, `certs/*.pem`), or one under the denylist glob's own prefix
    (`.github/workflows/**`). `src/**` or `**` never owns a lockfile it happens to cover."""
    if not entry_matches(ent, rel):
        return False
    if not ent["glob"]:
        return True
    if ent["path"].rstrip("/").rsplit("/", 1)[-1] not in ("*", "**"):
        return True
    pre = _static_prefix(sensitive["path"])
    return bool(pre) and _static_prefix(ent["path"]).startswith(pre)


def evaluate(scope: dict, rel: str) -> List[dict]:
    """Findings for one repo-relative path, in order: forbidden (a forbids entry), preserve (an H8
    Preserve glob), sensitive (the denylist, unless a writes entry owns it explicitly) and
    outside-writes (no writes entry covers it; only when the writes cell is machine-checkable).
    A `generated:` glob allows the path apart from forbids."""
    out: List[dict] = []
    for ent in scope["forbids"]:
        if entry_matches(ent, rel):
            out.append({"kind": "forbidden", "path": rel, "rule": ent["path"]})
            break
    if any(entry_matches(e, rel) for e in scope.get("generated") or []):
        return out
    for ent in scope.get("preserve") or []:
        if entry_matches(ent, rel):
            out.append({"kind": "preserve", "path": rel, "rule": ent["path"]})
            break
    for sens in _SENSITIVE:
        if entry_matches(sens, rel):
            if not any(owns(e, rel, sens) for e in scope["writes"]):
                out.append({"kind": "sensitive", "path": rel, "rule": sens["path"]})
            break
    if scope["checkable"] and not any(entry_matches(e, rel) for e in scope["writes"]):
        out.append({"kind": "outside-writes", "path": rel, "rule": None})
    return out


# --------------------------------------------------------------------------- disjoint-wave lint

def _nfa(pat: str):
    """An NFA for one glob (same language as _glob_re): (states, accept). A state is
    {"eps": [..], "edges": [(cls, to)]}; cls is ("c", ch) | ("ns",) (any but /) | ("any",)."""
    states = [{"eps": [], "edges": []}]

    def new() -> int:
        states.append({"eps": [], "edges": []})
        return len(states) - 1

    cur, i = 0, 0
    while i < len(pat):
        if pat.startswith("**/", i):
            nxt, loop = new(), new()
            states[cur]["eps"] += [nxt, loop]
            states[loop]["edges"] += [(("any",), loop), (("c", "/"), nxt)]
            cur, i = nxt, i + 3
        elif pat.startswith("**", i):
            nxt = new()
            states[cur]["eps"].append(nxt)
            states[nxt]["edges"].append((("any",), nxt))
            cur, i = nxt, i + 2
        elif pat[i] == "*":
            nxt = new()
            states[cur]["eps"].append(nxt)
            states[nxt]["edges"].append((("ns",), nxt))
            cur, i = nxt, i + 1
        else:
            nxt = new()
            states[cur]["edges"].append(((("ns",) if pat[i] == "?" else ("c", pat[i])), nxt))
            cur, i = nxt, i + 1
    return states, cur


def _closure(states, s: int) -> set:
    seen, stack = {s}, [s]
    while stack:
        for t in states[stack.pop()]["eps"]:
            if t not in seen:
                seen.add(t)
                stack.append(t)
    return seen


def _compatible(a: tuple, b: tuple) -> bool:
    if a[0] == "c" and b[0] == "c":
        return a[1] == b[1]
    if a[0] == "c":
        a, b = b, a
    if b[0] == "c":
        return a[0] == "any" or b[1] != "/"
    return True


def globs_intersect(p: str, q: str) -> bool:
    """True when some path matches both globs (product of the two NFAs, breadth-first)."""
    sa, fa = _nfa(p)
    sb, fb = _nfa(q)
    start = {(x, y) for x in _closure(sa, 0) for y in _closure(sb, 0)}
    seen, todo = set(start), list(start)
    while todo:
        x, y = todo.pop()
        if x == fa and y == fb:
            return True
        for ca, ta in sa[x]["edges"]:
            for cb, tb in sb[y]["edges"]:
                if not _compatible(ca, cb):
                    continue
                for pair in ((u, v) for u in _closure(sa, ta) for v in _closure(sb, tb)):
                    if pair not in seen:
                        seen.add(pair)
                        todo.append(pair)
    return False


def _variants(ent: dict) -> List[str]:
    if ent["glob"]:
        return [ent["path"]]
    base = ent["path"].rstrip("/")
    if not base:
        return []
    # A literal whose last segment has an extension is a file: it covers nothing beneath it here.
    dir_like = ent["path"].endswith("/") or "." not in base.rsplit("/", 1)[-1]
    return [base, base + "/**"] if dir_like else [base]


def _selectors_overlap(a, b) -> bool:
    if a is None or b is None:
        return True
    for x in a:
        for y in b:
            xs, ys = [p for p in x.split(".") if p], [p for p in y.split(".") if p]
            if all(s == t or "*" in (s, t) for s, t in zip(xs, ys)):
                return True
    return False


def entries_overlap(a: dict, b: dict) -> bool:
    if not any(globs_intersect(p, q) for p in _variants(a) for q in _variants(b)):
        return False
    return _selectors_overlap(a["selectors"], b["selectors"])


def _deps(row: dict) -> List[str]:
    raw = (row.get("depends_on") or "").strip()
    if _is_blank(raw):
        return []
    return [p.strip().upper() for p in re.split(r"[,;/]", raw) if p.strip() and not _is_blank(p)]


def _ancestors(by_id: Dict[str, dict]) -> Dict[str, set]:
    memo: Dict[str, set] = {}

    def walk(k: str, stack: frozenset) -> set:
        if k in memo:
            return memo[k]
        out: set = set()
        for d in _deps(by_id.get(k) or {}):
            if d in stack or d not in by_id:
                continue
            out.add(d)
            out |= walk(d, stack | {d})
        memo[k] = out
        return out

    for k in by_id:
        walk(k, frozenset({k}))
    return memo


def _depth(k: str, by_id: Dict[str, dict], memo: Dict[str, int], stack: frozenset = frozenset()) -> int:
    if k in memo:
        return memo[k]
    ds = [d for d in _deps(by_id.get(k) or {}) if d in by_id and d not in stack]
    memo[k] = 0 if not ds else 1 + max(_depth(d, by_id, memo, stack | {k}) for d in ds)
    return memo[k]


def task_wave(k: str, by_id: Dict[str, dict], memo: Dict[str, int]) -> str:
    """An explicit `wave` cell, else the dependency depth."""
    explicit = (by_id[k].get("wave") or "").strip()
    return explicit if not _is_blank(explicit) else f"depth-{_depth(k, by_id, memo)}"


def lint_scope(rows: List[Dict[str, str]]) -> List[Tuple[str, str]]:
    """(level, message): a verifier that declares writes, and two implementors in the same wave
    (neither depending on the other, neither verified) whose writes overlap. Prose tokens are not
    compared."""
    out: List[Tuple[str, str]] = []
    if not rows or "writes" not in rows[0]:
        return out
    by_id = index_rows(rows)
    for k, r in by_id.items():
        if (r.get("role") or "").strip().lower() == "verifier" and not _is_blank(r.get("writes")):
            out.append(("ERROR", f"verifier {r.get('id')} declares writes ({r.get('writes')}); "
                                 "a verifier is read-only (writes: none)"))
    anc = _ancestors(by_id)
    memo: Dict[str, int] = {}
    impl = [k for k, r in by_id.items() if (r.get("role") or "").strip().lower() == "implementor"
            and (r.get("status") or "").strip().lower() != "verified"]
    scopes = {}
    for k in impl:
        try:
            scopes[k] = task_scope(list(by_id.values()), k)["writes"]
        except KeyError:
            scopes[k] = []
    waves: Dict[str, List[str]] = {}
    for k in impl:
        waves.setdefault(task_wave(k, by_id, memo), []).append(k)
    for wave, ids in waves.items():
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                if a in anc.get(b, set()) or b in anc.get(a, set()):
                    continue
                hits = []
                for ea in scopes[a]:
                    for eb in scopes[b]:
                        if entries_overlap(ea, eb):
                            hits.append(ea["path"] if ea["path"] == eb["path"] else f"{ea['path']} ~ {eb['path']}")
                if hits:
                    shown = ", ".join(dict.fromkeys(hits))
                    out.append(("ERROR", f"wave {wave}: {by_id[a].get('id')} and {by_id[b].get('id')} may run in "
                                         f"parallel and both write {shown} (serialize with depends_on, or give "
                                         "one task the shared path)"))
    return out


# --------------------------------------------------------------------------- active-task pointer

def find_top(path: Path) -> Optional[Path]:
    """The nearest ancestor (of the path or its first existing parent) holding `.git`."""
    cur = Path(os.path.realpath(str(path)))
    for _ in range(128):
        try:
            if (cur / ".git").exists():
                return cur
        except OSError:
            return None
        if cur.parent == cur:
            return None
        cur = cur.parent
    return None


def is_workspace(top: Path) -> bool:
    """The workspace checkout or one of its linked worktrees (plain file tests, no git)."""
    return ((top / "AGENTS.md").is_file() and (top / "02-shared-references" / "surfaces.json").is_file()
            and (top / "09-tools" / "intent-run.py").is_file())


def _git_config(top: Path) -> Optional[Path]:
    g = top / ".git"
    if g.is_dir():
        return g / "config"
    if not g.is_file():
        return None
    first = g.read_text(encoding="utf-8", errors="replace").splitlines()[0].strip()
    if not first.startswith("gitdir:"):
        return None
    gd = Path(first[len("gitdir:"):].strip())
    gd = gd if gd.is_absolute() else top / gd
    cd = gd / "commondir"
    if cd.is_file():
        c = Path(cd.read_text(encoding="utf-8", errors="replace").strip())
        gd = c if c.is_absolute() else gd / c
    return gd / "config"


def _url_slug(url: str) -> Optional[str]:
    pr = sys.modules.get("profile_resolve")
    if pr is not None and hasattr(pr, "normalize_remote"):
        try:
            norm = pr.normalize_remote(url)
            return norm["slug"] if norm else None
        except Exception:  # noqa: BLE001 - fall back to the plain parse
            pass
    u = url.strip().strip("\"'")
    m = re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://[^/]+/(.*)$", u) or re.match(r"^(?:[^@/\s:]+@)?[\w.-]+:(.*)$", u)
    if not m:
        return None
    path = m.group(1).split("?", 1)[0].split("#", 1)[0].strip("/")
    if path.endswith(".git"):
        path = path[:-4]
    parts = [p for p in path.split("/") if p and p not in (".", "..")]
    if len(parts) < 2:
        return None
    return f"{parts[0].casefold()}/{'/'.join(parts[1:]).casefold()}"


def origin_slug(top: Path) -> Optional[str]:
    """owner/repo from the checkout's git config (origin first), read as a file."""
    try:
        cfg = _git_config(top)
        text = cfg.read_text(encoding="utf-8", errors="replace") if cfg else ""
    except (OSError, IndexError):
        return None
    urls: List[Tuple[str, str]] = []
    section = None
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("["):
            m = re.match(r'^\[\s*remote\s+"([^"]+)"\s*\]', s, re.I)
            section = m.group(1) if m else None
            continue
        if section and "=" in s:
            k, _, v = s.partition("=")
            if k.strip().lower() == "url":
                urls.append((section, v.strip()))
    urls.sort(key=lambda p: p[0] != "origin")
    for _, url in urls:
        slug = _url_slug(url)
        if slug:
            return slug
    return None


def telemetry_dir(slug: str, home: Optional[Path] = None) -> Path:
    d = Path(home or Path.home()).joinpath(*TELEMETRY_PARTS)
    for part in (slug or "_unknown").split("/"):
        d = d / (re.sub(r"[^A-Za-z0-9_.-]", "_", part) or "_")
    return d


def pointer_path(top: Path, *, home: Optional[Path] = None) -> Path:
    if is_workspace(top):
        return top / POINTER_WS_REL
    return telemetry_dir(origin_slug(top) or "_unknown", home) / POINTER_NAME


def _inside(p: Path, top: Path) -> bool:
    try:
        Path(os.path.realpath(str(p))).relative_to(Path(os.path.realpath(str(top))))
        return True
    except ValueError:
        return False


def read_pointer(top: Path, *, home: Optional[Path] = None) -> Optional[dict]:
    """The pointer for this checkout, or None (absent, unreadable, or set for another checkout)."""
    try:
        data = json.loads(pointer_path(top, home=home).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or not data.get("spec") or not data.get("task"):
        return None
    if os.path.realpath(str(data.get("repo") or "")) != os.path.realpath(str(top)):
        return None
    return data


def write_pointer(top: Path, spec: Path, task: str, *, home: Optional[Path] = None,
                  now: Optional[str] = None) -> Path:
    """Write the pointer atomically. Outside the workspace it must land outside the repo."""
    dest = pointer_path(top, home=home)
    if not is_workspace(top) and _inside(dest, top):
        raise PermissionError("refused: the active-task pointer would land inside a non-workspace repo")
    stamp = now or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    data = {"schema_version": 1, "spec": os.path.realpath(str(spec)), "task": task,
            "repo": os.path.realpath(str(top)), "set_at": stamp}
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name(dest.name + f".tmp{os.getpid()}")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, dest)
    return dest


def clear_pointer(top: Path, *, home: Optional[Path] = None) -> bool:
    p = pointer_path(top, home=home)
    try:
        p.unlink()
        return True
    except OSError:
        return False


# --------------------------------------------------------------------------- the per-path check

_SPEC_CACHE: Dict[Tuple[str, str], Tuple[float, dict]] = {}


def _scope_for(spec: str, task: str) -> dict:
    st = os.stat(spec)
    hit = _SPEC_CACHE.get((spec, task))
    if hit and hit[0] == st.st_mtime:
        return hit[1]
    sc = spec_scope(Path(spec).read_text(encoding="utf-8"), task)
    _SPEC_CACHE[(spec, task)] = (st.st_mtime, sc)
    return sc


def check_path(path, *, cwd=None, home=None, budget: float = CHECK_BUDGET_S) -> dict:
    """The accelerator's check for one path about to be written. Never raises (fail open).

    status: no-repo | no-task | in-scope | outside | timeout | error. `block` is true only for an
    `outside` result on a task whose enforce cell is true; callers that are report-only ignore it."""
    t0 = time.monotonic()
    res: dict = {"status": "no-task", "path": str(path), "task": None, "rel": None, "findings": [],
                 "enforce": False, "block": False, "notes": []}
    try:
        p = Path(os.path.expanduser(str(path)))
        if not p.is_absolute():
            p = Path(cwd or os.getcwd()) / p
        p = Path(os.path.realpath(os.path.normpath(str(p))))
        top = find_top(p.parent)
        if top is None:
            res["status"] = "no-repo"
            return res
        ptr = read_pointer(top, home=home)
        if ptr is None:
            return res
        rel = p.relative_to(Path(os.path.realpath(str(top)))).as_posix()
        scope = _scope_for(str(ptr["spec"]), str(ptr["task"]))
        res.update(task=scope["task"], rel=rel, enforce=scope["enforce"])
        if not scope["checkable"]:
            res["notes"].append("writes cell is prose or absent: only forbids are checked")
        if time.monotonic() - t0 > budget:
            res["status"] = "timeout"
            return res
        res["findings"] = evaluate(scope, rel)
        res["status"] = "outside" if res["findings"] else "in-scope"
        res["block"] = bool(res["findings"]) and scope["enforce"]
    except Exception as exc:  # noqa: BLE001 - fail open
        res.update(status="error", findings=[], block=False)
        res["notes"].append(type(exc).__name__)
    finally:
        res["elapsed_ms"] = round((time.monotonic() - t0) * 1000, 2)
    return res


def message(res: dict) -> str:
    kinds = ", ".join(f["kind"] + (f" ({f['rule']})" if f.get("rule") else "") for f in res["findings"])
    mode = "enforce" if res.get("enforce") else "report-only"
    return f"ws-scope [{mode}]: {res.get('rel')} is {kinds} for task {res.get('task')}"


def log_finding(res: dict, *, host: str, home=None, now: Optional[str] = None) -> Optional[Path]:
    """Append one row to scope.jsonl beside the pointer. Non-workspace rows carry a path hash."""
    try:
        top = find_top(Path(res["path"]).parent)
        if top is None:
            return None
        dest = pointer_path(top, home=home).with_name(LOG_NAME)
        ws = is_workspace(top)
        if not ws and _inside(dest, top):
            return None
        rel = res.get("rel") or ""
        row = {"schema_version": 1, "ts": now or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "host": host, "task": res.get("task"), "kinds": [f["kind"] for f in res["findings"]],
               "enforce": bool(res.get("enforce"))}
        if ws:
            row["path"] = rel
        else:
            row["path_sha256"] = hashlib.sha256(rel.encode("utf-8")).hexdigest()[:16]
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, separators=(",", ":")) + "\n")
        return dest
    except Exception:  # noqa: BLE001 - fail open
        return None


def write_paths(payload: dict, table: Optional[dict]) -> Tuple[List[str], Optional[str]]:
    """The file paths a host's pre-tool payload is about to write, via the guard's own reader."""
    wg = sys.modules.get("wall_guard")
    if wg is None:
        here = str(Path(__file__).resolve().parent)
        if here not in sys.path:
            sys.path.insert(0, here)
        import wall_guard as wg  # noqa: PLC0415
    _event, _tool, actions, cwd = wg.extract(payload, table)
    paths = [a["path"] for a in actions
             if a.get("kind") == "file" and a.get("op") == "write" and a.get("path")]
    return list(dict.fromkeys(paths)), (str(cwd) if cwd else None)


def report_payload(host: str, payload: dict, *, table: Optional[dict] = None, home=None, err=None,
                   log: bool = True) -> List[dict]:
    """The report-only pre-write step: check every path the payload writes, log and print each
    finding to stderr. Returns the results; never raises, never writes stdout."""
    out: List[dict] = []
    try:
        paths, cwd = write_paths(payload, table)
        for p in paths:
            res = check_path(p, cwd=cwd, home=home)
            out.append(res)
            if res["status"] == "outside":
                if log:
                    log_finding(res, host=host, home=home)
                if err is not None:
                    err.write(message(res) + "\n")
    except Exception:  # noqa: BLE001 - fail open
        pass
    return out
