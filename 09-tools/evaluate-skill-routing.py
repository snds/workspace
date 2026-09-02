#!/usr/bin/env python3
"""Adversarial skill-routing harness.

Proves Layer 0 still fires the right skill (and does not fire the wrong one)
against a curated utterance corpus. Matching must stay aligned with
`.claude/hooks/dispatcher.py` (`_term_matches`, curated routes, registry
triggers, knowledge-index triggers).

Usage:
  python3 09-tools/evaluate-skill-routing.py              # run corpus, write stamp on pass
  python3 09-tools/evaluate-skill-routing.py --check      # CI / write-gate: fail on miss
  python3 09-tools/evaluate-skill-routing.py --lint       # short/stopword trigger lint only
  python3 09-tools/evaluate-skill-routing.py --utterance "…"
  python3 09-tools/evaluate-skill-routing.py --stale      # exit 1 if graph hash != stamp

When to run (session, not a daemon):
  - session start, if the stamp is missing or the graph hash changed
  - after any skill / trigger-routes / routing-corpus edit (write-quality gate)
  - when a live prompt under-fires or over-fires (`--utterance`)
  - /health and /optimize (surface 5)
  - after skill authoring (#13 / skill-placement)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CURATED = ROOT / "02-shared-references" / "trigger-routes.json"
REGISTRY = ROOT / "03-skills" / "skills.registry.json"
INDEX = ROOT / "08-knowledge" / "_INDEX.md"
CORPUS = ROOT / "02-shared-references" / "skill-routing-cases.jsonl"
STAMP = (
    ROOT
    / "07-projects"
    / "19-workspace-brain"
    / "reports"
    / "skill-routing-harness.stamp"
)

# Word-boundary match — copy of dispatcher._term_matches. Do not drift.
def term_matches(term: str, prompt: str) -> bool:
    return re.search(r"(?<!\w)" + re.escape(term.lower()) + r"(?!\w)", prompt) is not None


STOPWORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "i",
        "to",
        "of",
        "in",
        "on",
        "for",
        "and",
        "or",
        "is",
        "it",
        "be",
        "we",
        "you",
        "me",
        "as",
        "at",
        "by",
        "from",
        "this",
        "that",
        "with",
        "do",
        "if",
    }
)

WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'/-]*")


def load_curated() -> dict[str, str]:
    data = json.loads(CURATED.read_text(encoding="utf-8"))
    templates = data.get("templates") or {}
    out: dict[str, str] = {}
    for trigger, hint in (data.get("routes") or {}).items():
        if isinstance(hint, str) and hint.startswith("$") and hint[1:] in templates:
            out[trigger] = templates[hint[1:]]
        else:
            out[trigger] = hint
    return out


def _as_terms(raw) -> list[str]:
    """Normalize registry triggers. A stored string is one term, not characters."""
    if raw is None:
        return []
    if isinstance(raw, str):
        s = raw.strip()
        if s.startswith("["):
            inner = s[1:]
            if "]" in inner:
                inner = inner[: inner.rfind("]")]
            return [t.strip().strip("'\"") for t in inner.split(",") if t.strip()]
        return [s] if s else []
    return [str(t).strip() for t in raw if str(t).strip()]


def load_registry() -> dict[str, list[str]]:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    skills = data.get("skills") or {}
    return {name: _as_terms(rec.get("triggers")) for name, rec in skills.items()}


def load_index_triggers() -> dict[str, list[str]]:
    if not INDEX.exists():
        return {}
    out: dict[str, list[str]] = {}
    for line in INDEX.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^-\s+\[\[([^\]]+)\]\]", line.strip())
        if not m:
            continue
        tm = re.search(r"[Tt]riggers:\s*(.+)$", line)
        if not tm:
            continue
        out[m.group(1)] = re.findall(r"`([^`]+)`", tm.group(1))
    return out


def load_descriptions() -> dict[str, str]:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    return {
        name: str(rec.get("description") or "")
        for name, rec in (data.get("skills") or {}).items()
    }


def layer0(prompt: str) -> dict[str, set[str]]:
    p = prompt.lower()
    curated = {t for t in load_curated() if term_matches(t, p)}
    registry: set[str] = set()
    for name, triggers in load_registry().items():
        if any(term_matches(t, p) for t in triggers):
            registry.add(name)
    knowledge: set[str] = set()
    for name, triggers in load_index_triggers().items():
        if any(term_matches(t, p) for t in triggers):
            knowledge.add(name)
    return {"routes": curated, "skills": registry, "knowledge": knowledge}


def description_overfire(prompt: str) -> dict[str, list[str]]:
    """Naive description-token match. Diagnoses Cursor-style fallback over-fire.

    Only counts a skill when a stopword from its description matches the prompt
    and no content word from the description does. That is the article/pronoun
    false-positive (``a`` / ``I``), not ordinary overlap.
    """
    p = prompt.lower()
    hits: dict[str, list[str]] = {}
    for name, desc in load_descriptions().items():
        words = {w.lower() for w in WORD_RE.findall(desc)}
        stop = [w for w in words if w in STOPWORDS and term_matches(w, p)]
        content = [
            w for w in words if w not in STOPWORDS and term_matches(w, p)
        ]
        if stop and not content:
            hits[name] = sorted(set(stop))
    return hits


def graph_hash() -> str:
    h = hashlib.sha256()
    for path in (CURATED, REGISTRY, CORPUS, INDEX):
        h.update(path.read_bytes() if path.exists() else b"")
        h.update(b"\0")
    return h.hexdigest()[:16]


def write_stamp(result: str, cases: int, failed: int) -> None:
    STAMP.parent.mkdir(parents=True, exist_ok=True)
    STAMP.write_text(
        (
            f"date: {date.today().isoformat()}\n"
            f"hash: {graph_hash()}\n"
            f"result: {result}\n"
            f"cases: {cases}\n"
            f"failed: {failed}\n"
        ),
        encoding="utf-8",
    )


def read_stamp() -> dict[str, str]:
    if not STAMP.exists():
        return {}
    out: dict[str, str] = {}
    for line in STAMP.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def load_corpus() -> list[dict]:
    cases: list[dict] = []
    for i, line in enumerate(CORPUS.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        row = json.loads(line)
        if "id" not in row or "utterance" not in row:
            raise ValueError(f"{CORPUS}:{i} needs id and utterance")
        cases.append(row)
    if not cases:
        raise ValueError(f"{CORPUS} is empty")
    return cases


def lint_triggers() -> list[str]:
    errors: list[str] = []
    for name, triggers in load_registry().items():
        for t in triggers:
            low = t.strip().lower()
            if low in STOPWORDS:
                errors.append(f"stopword trigger `{t}` on {name}")
            elif len(low) < 2:
                errors.append(f"too-short trigger `{t}` on {name}")
    for name, triggers in load_index_triggers().items():
        for t in triggers:
            low = t.strip().lower()
            if low in STOPWORDS:
                errors.append(f"stopword index trigger `{t}` on [[{name}]]")
    return errors


def eval_case(row: dict) -> list[str]:
    hits = layer0(row["utterance"])
    desc = description_overfire(row["utterance"])
    errs: list[str] = []
    cid = row["id"]

    def missing(kind: str, expected: list[str], actual: set[str]) -> None:
        for item in expected:
            if item not in actual:
                errs.append(f"{cid}: expected {kind} `{item}` (got {sorted(actual) or 'none'})")

    def forbidden(kind: str, banned: list[str], actual: set[str]) -> None:
        for item in banned:
            if item in actual:
                errs.append(f"{cid}: forbid {kind} `{item}` fired")

    missing("skill", row.get("expect_skills") or [], hits["skills"])
    missing("route", row.get("expect_routes") or [], hits["routes"])
    missing("knowledge", row.get("expect_knowledge") or [], hits["knowledge"])
    forbidden("skill", row.get("forbid_skills") or [], hits["skills"])
    forbidden("route", row.get("forbid_routes") or [], hits["routes"])
    forbidden("knowledge", row.get("forbid_knowledge") or [], hits["knowledge"])

    # Description-tokenization risk is a warning, not a Layer-0 failure.
    # Layer 0 (dispatcher) does not match description words.
    if row.get("forbid_description_skills"):
        for name in row["forbid_description_skills"]:
            if name in desc:
                print(
                    f"WARN {cid}: description fallback would load `{name}` via {desc[name]}"
                )

    min_l0 = row.get("min_layer0")
    if min_l0 is not None:
        n = len(hits["skills"] | hits["routes"] | hits["knowledge"])
        if n < int(min_l0):
            errs.append(f"{cid}: Layer 0 under-fired ({n} < {min_l0})")

    return errs


def run_corpus() -> tuple[int, list[str]]:
    cases = load_corpus()
    errors: list[str] = []
    errors.extend(lint_triggers())
    for row in cases:
        errors.extend(eval_case(row))
    return len(cases), errors


def print_utterance(text: str) -> None:
    hits = layer0(text)
    desc = description_overfire(text)
    print(f"utterance: {text}")
    print(f"routes: {sorted(hits['routes']) or '—'}")
    print(f"skills: {sorted(hits['skills']) or '—'}")
    print(f"knowledge: {sorted(hits['knowledge']) or '—'}")
    if desc:
        risky = {k: v for k, v in desc.items() if k not in hits["skills"]}
        if risky:
            print("description-overfire (not Layer 0):")
            for name, words in sorted(risky.items()):
                print(f"  {name}: {words}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Adversarial skill-routing harness")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="run corpus; no stamp write")
    mode.add_argument("--lint", action="store_true", help="lint triggers only")
    mode.add_argument("--stale", action="store_true", help="fail if stamp hash drifted")
    mode.add_argument("--utterance", metavar="TEXT", help="probe one prompt")
    args = parser.parse_args()

    if args.utterance is not None:
        print_utterance(args.utterance)
        return 0

    if args.lint:
        errors = lint_triggers()
        if errors:
            print("\n".join(errors))
            return 1
        print("trigger lint OK")
        return 0

    if args.stale:
        stamp = read_stamp()
        current = graph_hash()
        if not stamp:
            print("skill-routing harness stamp missing — run evaluate-skill-routing.py")
            return 1
        if stamp.get("hash") != current:
            print(
                f"skill-routing harness stale (stamp {stamp.get('hash')} vs {current})"
            )
            return 1
        if stamp.get("result") != "pass":
            print("skill-routing harness last result was not pass")
            return 1
        print(f"skill-routing harness current ({current})")
        return 0

    n, errors = run_corpus()
    if errors:
        print(f"FAIL {n - len(errors)}/{n} routing cases; {len(errors)} error(s):")
        print("\n".join(errors))
        if not args.check:
            write_stamp("fail", n, len(errors))
        return 1
    print(f"OK {n}/{n} routing cases")
    if not args.check:
        write_stamp("pass", n, 0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
