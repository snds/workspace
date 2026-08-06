#!/usr/bin/env python3
"""
vault-retrieve.py — Layer-1 lexical retrieval over the personal vault.

Stdlib-only FTS5 index over frameworks, shared references, skills, preferences,
memory, and knowledge. Returns ranked paths + short snippets (preferring each
note's `## For future agent` TL;DR). Optional one-hop graph expand via
knowledge `relations:` and skill `## Related` wikilinks.

Does NOT replace trigger routing (Layer 0). Use this when vocabulary misses
or you need ranked candidates across the vault. Token-frugal by design:
paths + TL;DRs, not full file bodies.

Index is machine-local (`.claude/state/vault-retrieve/`), rebuildable from git.
Never indexes `07-projects/` or employer surfaces.

Usage:
  python3 09-tools/vault-retrieve.py "contracts first delivery"
  python3 09-tools/vault-retrieve.py "session fragment compaction" --limit 6
  python3 09-tools/vault-retrieve.py --rebuild
  python3 09-tools/vault-retrieve.py --check
  python3 09-tools/vault-retrieve.py "token frugal" --json
  python3 09-tools/vault-retrieve.py "open rail" --no-expand --paths-only
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_VERSION = "2"

# Personal vault layers only. Projects and artifacts stay out of the index.
CORPUS = [
    ("frameworks", "01-frameworks"),
    ("references", "02-shared-references"),
    ("skills", "03-skills"),
    ("preferences", "04-preferences"),
    ("context", "06-context"),
    ("knowledge", "08-knowledge"),
]

SKIP_PARTS = {
    "_archive", ".obsidian", "node_modules", "dist", ".git",
    "_qa-out", "__pycache__",
}
SKIP_NAMES = {
    "session-log.md",
    "session-log-archive.md",
    "skills.registry.json",
    "_template.md",
    "ARCHIVE-LOG.md",
}
# Context files worth indexing (everything else under 06-context/ is skipped
# except memory/ and these roots). Keeps the hot operational prose without
# the growing logs.
CONTEXT_ROOT_ALLOW = {
    "CRITICAL_FACTS.md",
    "project-context.md",
    "relational-context.md",
    "role-and-context.md",
    "open-threads.md",
    "artifact-registry.md",
}

WIKILINK = re.compile(r"\[\[([^\]|#]+?)(?:[#|][^\]]*)?\]\]")
HEADING = re.compile(r"^(#{1,3})\s+(.+?)\s*$")
TLDR = re.compile(
    r"\*\*TL;DR:\*\*\s*(.+?)(?=\n\s*-\s*\*\*|\n## |\Z)",
    re.DOTALL | re.IGNORECASE,
)
# Soft layer priors for ranking (lower bm25 is better; we subtract a bonus).
LAYER_BONUS = {
    "knowledge": 0.35,
    "memory": 0.30,
    "frameworks": 0.20,
    "skills": 0.15,
    "references": 0.10,
    "preferences": 0.05,
    "context": 0.05,
}


# ---- helpers ---------------------------------------------------------------

def find_workspace(start: Path) -> Path | None:
    p = start.resolve()
    for cand in [p, *p.parents]:
        if (cand / "AGENTS.md").exists():
            return cand
    return None


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def split_frontmatter(text: str) -> tuple[str, str]:
    """Split YAML frontmatter. Only the opening/closing `---` pair counts —

    a later `---` horizontal rule in the body must not re-open the split.
    """
    if not text.startswith("---"):
        return "", text
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return "", text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "".join(lines[1:i]), "".join(lines[i + 1 :])
    return "", text


def fm_scalar(fm: str, key: str) -> str:
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", fm, re.MULTILINE)
    if not m:
        return ""
    v = m.group(1).strip()
    if v in (">", ">-", "|", "|-"):
        # Folded/literal block: indented lines until next key or EOF
        start = m.end()
        lines = []
        for line in fm[start:].splitlines():
            if not line.strip():
                lines.append("")
                continue
            if re.match(r"^[A-Za-z0-9_]+:", line):
                break
            if line.startswith("  ") or line.startswith("\t"):
                lines.append(line.strip())
            else:
                break
        return " ".join(x for x in lines if x)
    if len(v) >= 2 and v[0] in "\"'" and v[-1] == v[0]:
        v = v[1:-1]
    return v


def fm_triggers(fm: str) -> str:
    """Flatten triggers / aliases / tags into searchable boost text."""
    bits: list[str] = []
    for key in ("triggers", "aliases", "tags"):
        m = re.search(rf"^{key}:\s*(.+)$", fm, re.MULTILINE)
        if not m:
            # block list
            block = re.search(
                rf"^{key}:\s*\n((?:[ \t]+- .+\n?)+)",
                fm,
                re.MULTILINE,
            )
            if block:
                items = re.findall(r"-\s+(.+)", block.group(1))
                bits.extend(i.strip().strip("\"'") for i in items)
            continue
        v = m.group(1).strip()
        if v.startswith("[") and v.endswith("]"):
            inner = v[1:-1]
            bits.extend(x.strip().strip("\"'") for x in inner.split(",") if x.strip())
        elif v and v not in (">", "|"):
            bits.append(v.strip("\"'"))
    return " ".join(bits)


def relations_edges(fm: str, src_path: str) -> list[tuple[str, str, str]]:
    """Parse relations: frontmatter into (src, rel, dst_slug) edges."""
    m = re.search(r"^relations:\s*(.*?)(?=^\S|\Z)", fm, re.MULTILINE | re.DOTALL)
    if not m:
        return []
    block = m.group(1)
    edges = []
    for rel, targets in re.findall(
        r"^\s*(builds-on|relates-to|contradicts|refutes|exemplifies):\s*\[([^\]]*)\]",
        block,
        re.MULTILINE,
    ):
        for name in WIKILINK.findall(targets):
            slug = name.split("/")[-1].strip()
            if slug:
                edges.append((src_path, rel, slug.lower()))
    # also bare wikilinks under relations if flow form used differently
    if not edges:
        for name in WIKILINK.findall(block):
            slug = name.split("/")[-1].strip()
            if slug:
                edges.append((src_path, "relates-to", slug.lower()))
    return edges


def related_skill_edges(body: str, src_path: str) -> list[tuple[str, str, str]]:
    """Parse ## Related wikilinks from a skill body."""
    m = re.search(r"^## Related\s*$", body, re.MULTILINE)
    if not m:
        return []
    section = body[m.end():]
    nxt = re.search(r"^## ", section, re.MULTILINE)
    if nxt:
        section = section[: nxt.start()]
    edges = []
    for name in WIKILINK.findall(section):
        slug = name.split("/")[-1].strip()
        if slug:
            edges.append((src_path, "related", slug.lower()))
    return edges


def extract_preamble(body: str) -> str:
    m = re.search(
        r"^## For future agent\s*\n(.*?)(?=^## |\Z)",
        body,
        re.MULTILINE | re.DOTALL,
    )
    return m.group(1).strip() if m else ""


def extract_tldr(preamble: str) -> str:
    m = TLDR.search(preamble)
    if not m:
        return ""
    return re.sub(r"\s+", " ", m.group(1)).strip()


def chunk_body(body: str) -> list[tuple[str, str, str]]:
    """Split body into (kind, heading, text) chunks.

    kind: preamble | section | body
    """
    preamble = extract_preamble(body)
    chunks: list[tuple[str, str, str]] = []
    if preamble:
        chunks.append(("preamble", "For future agent", preamble))

    # section-split on ## / ### (skip the preamble heading itself)
    parts = re.split(r"(?=^#{1,3} )", body, flags=re.MULTILINE)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        hm = HEADING.match(part.splitlines()[0]) if part else None
        if hm:
            heading = hm.group(2).strip()
            if heading.lower() == "for future agent":
                continue
            text = "\n".join(part.splitlines()[1:]).strip()
            if text:
                chunks.append(("section", heading, text))
        else:
            # leading prose before first heading
            if part and not chunks:
                chunks.append(("body", "", part))

    if not chunks and body.strip():
        chunks.append(("body", "", body.strip()[:8000]))
    return chunks


def iter_corpus_files(root: Path) -> list[tuple[str, Path]]:
    """Return (layer, path) for every indexable markdown file."""
    out: list[tuple[str, Path]] = []
    for layer, rel in CORPUS:
        base = root / rel
        if not base.exists():
            continue
        if base.is_file() and base.suffix == ".md":
            out.append((layer, base))
            continue
        for f in base.rglob("*.md"):
            parts = f.relative_to(root).parts
            if any(p in SKIP_PARTS for p in parts):
                continue
            if f.name in SKIP_NAMES:
                continue
            if layer == "context":
                # memory/ is fully in; root allowlist for sibling files;
                # skip sessions/, open-engine/ boards, audit-log growth.
                rel_parts = f.relative_to(base).parts
                if rel_parts[0] == "memory":
                    pass
                elif len(rel_parts) == 1 and f.name in CONTEXT_ROOT_ALLOW:
                    pass
                else:
                    continue
                # retag memory files
                if rel_parts[0] == "memory":
                    out.append(("memory", f))
                    continue
            out.append((layer, f))
    return out


def file_fingerprint(root: Path, paths: list[Path]) -> str:
    h = hashlib.sha256()
    h.update(INDEX_VERSION.encode())
    for p in sorted(paths, key=lambda x: str(x)):
        try:
            st = p.stat()
        except OSError:
            continue
        try:
            rel = str(p.relative_to(root))
        except ValueError:
            rel = str(p)
        h.update(f"{rel}\0{st.st_mtime_ns}\0{st.st_size}\n".encode())
    return h.hexdigest()


def index_paths(root: Path) -> tuple[Path, Path]:
    """Machine-local index location under the workspace checkout."""
    d = root / ".claude" / "state" / "vault-retrieve"
    return d, d / "fts.sqlite"


# ---- index -----------------------------------------------------------------

def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(db_path))
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA journal_mode=WAL")
    return con


def init_schema(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        DROP TABLE IF EXISTS chunks_fts;
        DROP TABLE IF EXISTS edges;
        DROP TABLE IF EXISTS docs;
        DROP TABLE IF EXISTS meta;

        CREATE TABLE meta (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL
        );

        CREATE TABLE docs (
          id INTEGER PRIMARY KEY,
          path TEXT NOT NULL UNIQUE,
          layer TEXT NOT NULL,
          title TEXT,
          slug TEXT NOT NULL
        );

        CREATE TABLE edges (
          src_path TEXT NOT NULL,
          rel TEXT NOT NULL,
          dst_slug TEXT NOT NULL
        );
        CREATE INDEX edges_dst ON edges(dst_slug);
        CREATE INDEX edges_src ON edges(src_path);

        CREATE VIRTUAL TABLE chunks_fts USING fts5(
          path UNINDEXED,
          layer UNINDEXED,
          kind UNINDEXED,
          title,
          heading,
          body,
          boost,
          tokenize = 'porter unicode61'
        );
        """
    )


def rebuild(root: Path, quiet: bool = False) -> int:
    _, db_path = index_paths(root)
    files = iter_corpus_files(root)
    paths = [p for _, p in files]
    fp = file_fingerprint(root, paths)

    con = connect(db_path)
    try:
        init_schema(con)
        n_chunks = 0
        n_edges = 0
        for layer, path in files:
            text = read_text(path)
            if not text.strip():
                continue
            rel = str(path.relative_to(root))
            fm, body = split_frontmatter(text)
            title = fm_scalar(fm, "title") or fm_scalar(fm, "name") or path.stem
            # H1 override if present
            h1 = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
            if h1 and not fm_scalar(fm, "title"):
                title = h1.group(1).strip()
            slug = path.stem.lower()
            boost = fm_triggers(fm)
            desc = fm_scalar(fm, "description")
            if desc:
                boost = (boost + " " + desc).strip()

            con.execute(
                "INSERT INTO docs(path, layer, title, slug) VALUES (?,?,?,?)",
                (rel, layer, title, slug),
            )

            for src, rel_name, dst in relations_edges(fm, rel):
                con.execute(
                    "INSERT INTO edges(src_path, rel, dst_slug) VALUES (?,?,?)",
                    (src, rel_name, dst),
                )
                n_edges += 1
            if layer == "skills" and path.name == "SKILL.md":
                for src, rel_name, dst in related_skill_edges(body, rel):
                    con.execute(
                        "INSERT INTO edges(src_path, rel, dst_slug) VALUES (?,?,?)",
                        (src, rel_name, dst),
                    )
                    n_edges += 1

            for kind, heading, chunk_text in chunk_body(body):
                # Cap chunk body to keep the index lean
                body_text = chunk_text[:12000]
                chunk_boost = boost
                if kind == "preamble":
                    chunk_boost = (boost + " " + extract_tldr(chunk_text)).strip()
                con.execute(
                    "INSERT INTO chunks_fts(path, layer, kind, title, heading, body, boost) "
                    "VALUES (?,?,?,?,?,?,?)",
                    (rel, layer, kind, title, heading, body_text, chunk_boost),
                )
                n_chunks += 1

        con.execute(
            "INSERT INTO meta(key, value) VALUES ('fingerprint', ?)", (fp,)
        )
        con.execute(
            "INSERT INTO meta(key, value) VALUES ('version', ?)", (INDEX_VERSION,)
        )
        con.execute(
            "INSERT INTO meta(key, value) VALUES ('doc_count', ?)",
            (str(len(files)),),
        )
        con.execute(
            "INSERT INTO meta(key, value) VALUES ('chunk_count', ?)",
            (str(n_chunks),),
        )
        con.commit()
    finally:
        con.close()

    if not quiet:
        print(
            f"vault-retrieve: rebuilt index — {len(files)} docs, "
            f"{n_chunks} chunks, {n_edges} edges → {db_path.relative_to(root)}"
        )
    return 0


def current_fingerprint(root: Path) -> str:
    files = iter_corpus_files(root)
    return file_fingerprint(root, [p for _, p in files])


def index_meta(con: sqlite3.Connection) -> dict[str, str]:
    try:
        rows = con.execute("SELECT key, value FROM meta").fetchall()
    except sqlite3.Error:
        return {}
    return {r["key"]: r["value"] for r in rows}


def ensure_fresh(root: Path, quiet: bool = False) -> Path:
    """Rebuild if missing/stale. Returns the db path."""
    _, db_path = index_paths(root)
    need = True
    if db_path.exists():
        con = connect(db_path)
        try:
            meta = index_meta(con)
            if (
                meta.get("version") == INDEX_VERSION
                and meta.get("fingerprint") == current_fingerprint(root)
            ):
                need = False
        finally:
            con.close()
    if need:
        rebuild(root, quiet=quiet)
    return db_path


def cached_db(root: Path) -> Path | None:
    """Return the index path if a usable DB exists; never rebuild.

    Hot-path callers (dispatcher UserPromptSubmit) use this so a prompt never
    pays for a corpus walk. SessionStart / explicit --rebuild keep it fresh.
    """
    _, db_path = index_paths(root)
    if not db_path.exists():
        return None
    con = connect(db_path)
    try:
        meta = index_meta(con)
    finally:
        con.close()
    if meta.get("version") != INDEX_VERSION:
        return None
    return db_path


# ---- query -----------------------------------------------------------------

def _query_terms(raw: str) -> list[str]:
    phrases = re.findall(r'"([^"]+)"', raw)
    rest = re.sub(r'"[^"]+"', " ", raw)
    parts: list[str] = []
    for p in phrases:
        p = p.strip()
        if p:
            parts.append('"' + p.replace('"', "") + '"')
    for t in re.findall(r"[A-Za-z0-9_./+-]{2,}", rest):
        safe = re.sub(r"[^\w./+-]", "", t)
        if safe:
            parts.append(safe)
    return parts


def fts_query(raw: str, joiner: str = " AND ") -> str:
    """Build an FTS5 query from free text (AND by default; OR for fallback)."""
    parts = _query_terms(raw.strip())
    return joiner.join(parts) if parts else ""


def snippet_for(kind: str, heading: str, body: str, query: str) -> str:
    if kind == "preamble":
        tldr = extract_tldr(body)
        if tldr:
            return tldr[:280]
    # first sentence-ish containing a query term, else head
    terms = [t.lower() for t in re.findall(r"[A-Za-z0-9]{3,}", query)]
    flat = re.sub(r"\s+", " ", body).strip()
    if terms:
        low = flat.lower()
        for t in terms:
            i = low.find(t)
            if i >= 0:
                start = max(0, i - 60)
                end = min(len(flat), i + 200)
                snip = flat[start:end].strip()
                if start > 0:
                    snip = "…" + snip
                if end < len(flat):
                    snip = snip + "…"
                return snip[:280]
    prefix = f"{heading}: " if heading else ""
    return (prefix + flat)[:280]


def retrieve(
    root: Path,
    query: str,
    limit: int = 8,
    expand: bool = True,
    quiet: bool = False,
    cached: bool = False,
) -> list[dict]:
    if cached:
        db_path = cached_db(root)
        if db_path is None:
            return []
    else:
        db_path = ensure_fresh(root, quiet=quiet)
    fts_and = fts_query(query, " AND ")
    if not fts_and:
        return []

    con = connect(db_path)
    try:
        # Weighted columns: boost (triggers/desc) > title > heading > body
        sql = """
            SELECT path, layer, kind, title, heading, body,
                   bm25(chunks_fts, 0, 0, 0, 4.0, 2.0, 1.0, 3.0) AS rank
            FROM chunks_fts
            WHERE chunks_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """
        fetch_n = max(limit * 6, 24)

        def _run(match: str) -> list:
            try:
                return con.execute(sql, (match, fetch_n)).fetchall()
            except sqlite3.OperationalError:
                return []

        def _absorb(rows: list, via: str, score_pad: float, into: dict[str, dict]) -> None:
            for r in rows:
                path = r["path"]
                bonus = LAYER_BONUS.get(r["layer"], 0.0)
                if r["kind"] == "preamble":
                    bonus += 0.15
                if path.endswith("/SKILL.md"):
                    bonus += 0.1
                score = float(r["rank"]) - bonus + score_pad
                prev = into.get(path)
                if prev is None or score < prev["score"]:
                    into[path] = {
                        "path": path,
                        "layer": r["layer"],
                        "kind": r["kind"],
                        "title": r["title"] or Path(path).stem,
                        "heading": r["heading"] or "",
                        "score": score,
                        "snippet": snippet_for(
                            r["kind"], r["heading"], r["body"], query
                        ),
                        "via": via,
                    }

        # Keep AND hits; fill remaining slots from OR (don't discard strict matches).
        best: dict[str, dict] = {}
        _absorb(_run(fts_and), "fts", 0.0, best)
        if len(best) < limit:
            fts_or = fts_query(query, " OR ")
            if fts_or and fts_or != fts_and:
                _absorb(_run(fts_or), "fts-or", 0.4, best)

        ranked = sorted(best.values(), key=lambda x: x["score"])[:limit]

        if expand and ranked:
            # one-hop graph expand from top hits
            seeds = [h["path"] for h in ranked[: min(4, len(ranked))]]
            placeholders = ",".join("?" * len(seeds))
            edge_rows = con.execute(
                f"SELECT src_path, rel, dst_slug FROM edges "
                f"WHERE src_path IN ({placeholders})",
                seeds,
            ).fetchall()
            have = {h["path"] for h in ranked}
            # slug → paths
            slug_paths: dict[str, list[str]] = {}
            for row in con.execute("SELECT path, slug FROM docs"):
                slug_paths.setdefault(row["slug"], []).append(row["path"])

            extras: list[dict] = []
            for er in edge_rows:
                for dst_path in slug_paths.get(er["dst_slug"], []):
                    if dst_path in have:
                        continue
                    doc = con.execute(
                        "SELECT path, layer, title FROM docs WHERE path = ?",
                        (dst_path,),
                    ).fetchone()
                    if not doc:
                        continue
                    # pull preamble/body snippet from fts if present
                    chunk = con.execute(
                        "SELECT kind, heading, body FROM chunks_fts "
                        "WHERE path = ? ORDER BY "
                        "CASE kind WHEN 'preamble' THEN 0 ELSE 1 END LIMIT 1",
                        (dst_path,),
                    ).fetchone()
                    snip = ""
                    heading = ""
                    kind = "graph"
                    if chunk:
                        kind = chunk["kind"]
                        heading = chunk["heading"] or ""
                        snip = snippet_for(kind, heading, chunk["body"], query)
                    extras.append(
                        {
                            "path": dst_path,
                            "layer": doc["layer"],
                            "kind": kind,
                            "title": doc["title"] or Path(dst_path).stem,
                            "heading": heading,
                            "score": ranked[-1]["score"] + 0.5 + len(extras) * 0.01,
                            "snippet": snip or f"graph:{er['rel']} from {er['src_path']}",
                            "via": f"graph:{er['rel']}",
                        }
                    )
                    have.add(dst_path)
                    if len(extras) >= max(2, limit // 3):
                        break
                if len(extras) >= max(2, limit // 3):
                    break
            ranked = (ranked + extras)[: limit + max(2, limit // 3)]

        return ranked
    finally:
        con.close()


# ---- CLI -------------------------------------------------------------------

def cmd_check(root: Path) -> int:
    _, db_path = index_paths(root)
    files = iter_corpus_files(root)
    fp = file_fingerprint(root, [p for _, p in files])
    if not db_path.exists():
        print(f"vault-retrieve: no index at {db_path.relative_to(root)}")
        print(f"  corpus: {len(files)} docs (run --rebuild)")
        return 1
    con = connect(db_path)
    try:
        meta = index_meta(con)
    finally:
        con.close()
    fresh = meta.get("fingerprint") == fp and meta.get("version") == INDEX_VERSION
    status = "fresh" if fresh else "STALE"
    print(f"vault-retrieve: index {status}")
    print(f"  path:    {db_path.relative_to(root)}")
    print(f"  version: {meta.get('version', '?')} (want {INDEX_VERSION})")
    print(f"  docs:    {meta.get('doc_count', '?')} indexed / {len(files)} corpus")
    print(f"  chunks:  {meta.get('chunk_count', '?')}")
    return 0 if fresh else 1


def format_text(hits: list[dict]) -> str:
    if not hits:
        return "vault-retrieve: no matches."
    lines = [f"vault-retrieve: {len(hits)} hit(s)", ""]
    for i, h in enumerate(hits, 1):
        via = h.get("via", "fts")
        heading = f" › {h['heading']}" if h.get("heading") else ""
        lines.append(
            f"{i}. `{h['path']}`  [{h['layer']}/{via}]"
            f"{heading}"
        )
        lines.append(f"   {h['title']}")
        if h.get("snippet"):
            lines.append(f"   {h['snippet']}")
        lines.append("")
    lines.append(
        "_Read matched paths before acting. Prefer `## For future agent` then "
        "the smallest sufficient section. Layer 0 triggers still win on exact routes._"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Lexical vault retrieval (FTS5) with optional graph expand."
    )
    ap.add_argument("query", nargs="?", help="Free-text query")
    ap.add_argument("--rebuild", action="store_true", help="Force rebuild the index")
    ap.add_argument("--check", action="store_true", help="Report index freshness")
    ap.add_argument("--limit", type=int, default=8, help="Max FTS hits (default 8)")
    ap.add_argument("--no-expand", action="store_true", help="Skip graph expand")
    ap.add_argument(
        "--cached",
        action="store_true",
        help="Query only; never rebuild (empty if index missing/incompatible)",
    )
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--paths-only", action="store_true", help="Print paths only")
    ap.add_argument("--quiet", action="store_true", help="Suppress rebuild chatter")
    args = ap.parse_args(argv)

    root = find_workspace(Path.cwd()) or ROOT
    if not (root / "AGENTS.md").exists():
        print("vault-retrieve: AGENTS.md not found — not a workspace root", file=sys.stderr)
        return 2

    if args.rebuild:
        return rebuild(root, quiet=args.quiet)
    if args.check:
        return cmd_check(root)
    if not args.query:
        ap.print_help()
        return 2

    hits = retrieve(
        root,
        args.query,
        limit=max(1, args.limit),
        expand=not args.no_expand,
        quiet=args.quiet,
        cached=args.cached,
    )
    if args.paths_only:
        for h in hits:
            print(h["path"])
        return 0 if hits else 1
    if args.json:
        print(json.dumps({"query": args.query, "hits": hits}, indent=2))
        return 0 if hits else 1
    print(format_text(hits))
    return 0 if hits else 1


if __name__ == "__main__":
    sys.exit(main())
