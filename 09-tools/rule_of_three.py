#!/usr/bin/env python3
"""rule_of_three.py — the rule-of-three instance log and its growth check (H14).

The third time the same fix, workaround or pattern shows up, it earns a skill, a check or a
knowledge entry; before that it earns a row. `06-context/rule-of-three.jsonl` holds one row per
observed instance, appended from any surface, so the rule fires on evidence instead of prose.

Row (one JSON object per line; unknown keys fail):
  ts            ISO-8601 UTC, stamped by `add`
  pattern       slug naming the repeated pattern (a-z, 0-9, '-')
  instance_ref  the evidence: a clone-visible repo path or a commit SHA that resolves.
                Session-log anchors are refused (compaction moves them).
  surface       surfaces.json id of the surface that recorded the row, from detect_surface();
                an unknown id fails
  family        surfaces.json family of that surface
  device        devices.json id, or "unknown"
  target        optional: the path of the resolution (skill, check, knowledge or decision entry)
                or of the new hub the rows justify
  note          optional, one line (<= 200 chars)

Growth check (workspace-harness `check_rule_of_three`, connections lane; CI is the backstop):
  FAIL  a malformed row, an unresolvable instance_ref or target, an unknown surface or family,
        a duplicate (pattern, instance_ref);
  FAIL  a pattern with >= 3 distinct instances and no target, unless the baseline grandfathers it;
  FAIL  a hub or foundation (registry tier) not in the baseline, unless >= 3 distinct rows target
        its SKILL.md or it is a command-hub with a HUB_DETECTORS row (close-out-dispatch.py);
  FAIL  a 01-frameworks/*.md not in the baseline with fewer than 3 consumers (skills or
        frameworks naming it by path or wikilink);
  FAIL  a baseline that grew relative to WS_RULE3_BASE_REF (CI: the push's `before` or the PR
        base), else HEAD. The baseline may only shrink.
  NOTE  baseline entries that no longer apply (lower it with `baseline --write`).

Usage:
  python3 09-tools/rule_of_three.py add --pattern <slug> --evidence <path-or-sha> [--target <path>] [--note <text>] [--print]
  python3 09-tools/rule_of_three.py list
  python3 09-tools/rule_of_three.py check [--json]
  python3 09-tools/rule_of_three.py baseline --write

Exit: 0 ok · 1 check failed or row refused · 2 usage or unreadable tables.
Stdlib only. Vault only: rows are vault paths or SHAs and never carry employer substance.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
LOG_REL = "06-context/rule-of-three.jsonl"
BASELINE_REL = "09-tools/rule-of-three.baseline.json"
REGISTRY_REL = "03-skills/skills.registry.json"
SURFACES_REL = "02-shared-references/surfaces.json"
DEVICES_REL = "02-shared-references/devices.json"
FRAMEWORKS_DIR = "01-frameworks"
THRESHOLD = 3
BASE_REF_ENV = "WS_RULE3_BASE_REF"

REQUIRED = ("ts", "pattern", "instance_ref", "surface", "family", "device")
OPTIONAL = ("target", "note")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
ANCHOR_RE = re.compile(r"session-log|#")
NOTE_MAX = 200


# ------------------------------------------------------------------------------ git seams

def _git(root: Path, *args: str) -> Optional[subprocess.CompletedProcess]:
    try:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return None


def _sha_resolves(root: Path, sha: str) -> bool:
    p = _git(root, "cat-file", "-e", f"{sha}^{{commit}}")
    return p is not None and p.returncode == 0


def _path_visible(root: Path, rel: str) -> bool:
    """On disk and not gitignored: present in the clone CI runs, not only on a dirty laptop."""
    if not rel or rel.startswith(("/", "~")) or ".." in Path(rel).parts:
        return False
    if not (root / rel).is_file():
        return False
    p = _git(root, "check-ignore", "-q", "--", rel)
    return not (p is not None and p.returncode == 0)


def make_resolver(root: Path) -> Callable[[str], Optional[str]]:
    """ref -> None when it resolves, else the reason."""
    def resolve(ref: str) -> Optional[str]:
        if ANCHOR_RE.search(ref):
            return f"{ref!r} is a session-log anchor or fragment; compaction moves those (cite a path or SHA)"
        if SHA_RE.match(ref) and not (root / ref).exists():
            return None if _sha_resolves(root, ref) else f"commit {ref} does not resolve"
        return None if _path_visible(root, ref) else f"{ref} is not a clone-visible repo path or commit SHA"
    return resolve


# ------------------------------------------------------------------------------ tables

def _json(root: Path, rel: str):
    try:
        return json.loads((root / rel).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def surface_tables(root: Path = ROOT) -> tuple[set, set, set]:
    t = _json(root, SURFACES_REL) or {}
    d = _json(root, DEVICES_REL) or {}
    sids = {r.get("id") for r in t.get("surfaces") or [] if isinstance(r, dict)}
    fams = set((t.get("families") or {}).keys())
    devs = {r.get("id") for r in d.get("devices") or [] if isinstance(r, dict)} | {"unknown"}
    return sids, fams, devs


def hub_detector_keys(root: Path = ROOT) -> set:
    path = root / "09-tools" / "close-out-dispatch.py"
    try:
        spec = importlib.util.spec_from_file_location("close_out_dispatch_r3", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return set(getattr(mod, "HUB_DETECTORS", {}).keys())
    except Exception:  # noqa: BLE001 - a missing or broken table means no exemptions, never a crash
        return set()


def registry_hubs(root: Path = ROOT) -> dict:
    reg = _json(root, REGISTRY_REL) or {}
    return {n: {"path": v.get("path"), "rigor_role": v.get("rigor_role"), "tier": v.get("tier")}
            for n, v in (reg.get("skills") or {}).items() if v.get("tier") in ("hub", "foundation")}


def framework_files(root: Path = ROOT) -> list:
    d = root / FRAMEWORKS_DIR
    return sorted(f"{FRAMEWORKS_DIR}/{p.name}" for p in d.glob("*.md")
                  if p.name != "00-README.md" and not p.name.startswith("_")) if d.is_dir() else []


def framework_consumers(root: Path, rel: str) -> int:
    """Distinct skills or frameworks (other than itself) that name `rel` by path or wikilink."""
    stem = Path(rel).stem
    rx = re.compile(re.escape(rel) + r"|\[\[" + re.escape(stem) + r"(?:[|#\]])")
    pool = sorted((root / "03-skills").glob("*/SKILL.md")) + [root / f for f in framework_files(root)]
    n = 0
    for p in pool:
        if p.resolve() == (root / rel).resolve():
            continue
        try:
            if rx.search(p.read_text(encoding="utf-8")):
                n += 1
        except (OSError, UnicodeDecodeError):
            continue
    return n


def read_rows(root: Path = ROOT) -> list:
    """[(lineno, raw)] for every non-blank line."""
    try:
        text = (root / LOG_REL).read_text(encoding="utf-8")
    except OSError:
        return []
    return [(i, ln) for i, ln in enumerate(text.splitlines(), 1) if ln.strip()]


def empty_baseline() -> dict:
    return {"hubs": [], "frameworks": [], "unresolved_patterns": []}


def read_baseline(root: Path = ROOT) -> Optional[dict]:
    b = _json(root, BASELINE_REL)
    return b if isinstance(b, dict) else None


def baseline_at(root: Path, ref: str) -> Optional[dict]:
    p = _git(root, "show", f"{ref}:{BASELINE_REL}")
    if p is None or p.returncode != 0:
        return None
    try:
        b = json.loads(p.stdout)
    except ValueError:
        return None
    return b if isinstance(b, dict) else None


def base_ref(root: Path, env: Optional[dict] = None) -> str:
    e = os.environ if env is None else env
    ref = (e.get(BASE_REF_ENV) or "").strip()
    if ref and not re.fullmatch(r"0+", ref) and _sha_resolves(root, ref):
        return ref
    return "HEAD"


# ------------------------------------------------------------------------------ evaluation

def validate_row(raw, *, surfaces: set, families: set, devices: set,
                 resolve: Callable[[str], Optional[str]]) -> tuple[Optional[dict], list]:
    """(row or None, errors)."""
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except ValueError:
            return None, ["not valid JSON"]
    if not isinstance(raw, dict):
        return None, ["not a JSON object"]
    errs = []
    extra = sorted(set(raw) - set(REQUIRED) - set(OPTIONAL))
    if extra:
        errs.append(f"unknown key(s): {', '.join(extra)}")
    for k in REQUIRED:
        if not (isinstance(raw.get(k), str) and raw[k].strip()):
            errs.append(f"{k} missing")
    if errs:
        return None, errs
    if not TS_RE.match(raw["ts"]):
        errs.append(f"ts {raw['ts']!r} is not ISO-8601 UTC (YYYY-MM-DDTHH:MM:SSZ)")
    if not SLUG_RE.match(raw["pattern"]):
        errs.append(f"pattern {raw['pattern']!r} is not a slug")
    if raw["surface"] not in surfaces:
        errs.append(f"surface {raw['surface']!r} is not a surfaces.json id")
    if raw["family"] not in families:
        errs.append(f"family {raw['family']!r} is not a surfaces.json family")
    if raw["device"] not in devices:
        errs.append(f"device {raw['device']!r} is not a devices.json id or 'unknown'")
    why = resolve(raw["instance_ref"])
    if why:
        errs.append(f"instance_ref: {why}")
    tgt = raw.get("target")
    if tgt is not None:
        if not (isinstance(tgt, str) and tgt.strip()):
            errs.append("target must be a non-empty path when present")
        elif SHA_RE.match(tgt) or ANCHOR_RE.search(tgt):
            errs.append(f"target {tgt!r} must be a repo path (skill, check, knowledge or decision)")
        else:
            why = resolve(tgt)
            if why:
                errs.append(f"target: {why}")
    note = raw.get("note")
    if note is not None and not (isinstance(note, str) and len(note) <= NOTE_MAX and "\n" not in note):
        errs.append(f"note must be one line of at most {NOTE_MAX} characters")
    return (None if errs else raw), errs


def evaluate(ctx: dict) -> dict:
    """Pure evaluation over gathered data (see gather()). Returns failures, notes, patterns."""
    fails, notes = [], []
    rows = []
    seen = set()
    for lineno, raw in ctx["rows"]:
        row, errs = validate_row(raw, surfaces=ctx["surfaces"], families=ctx["families"],
                                 devices=ctx["devices"], resolve=ctx["resolve"])
        for e in errs:
            fails.append(f"{LOG_REL}:{lineno}: {e}")
        if row is None:
            continue
        key = (row["pattern"], row["instance_ref"])
        if key in seen:
            fails.append(f"{LOG_REL}:{lineno}: duplicate instance {row['instance_ref']} for {row['pattern']}")
            continue
        seen.add(key)
        rows.append(row)

    base = ctx["baseline"]
    if base is None:
        fails.append(f"{BASELINE_REL} missing or unreadable (rule_of_three.py baseline --write)")
        base = empty_baseline()

    patterns: dict = {}
    for r in rows:
        p = patterns.setdefault(r["pattern"], {"instances": [], "targets": []})
        p["instances"].append(r["instance_ref"])
        if r.get("target") and r["target"] not in p["targets"]:
            p["targets"].append(r["target"])
    debt = set(base.get("unresolved_patterns") or [])
    for name, p in sorted(patterns.items()):
        n = len(p["instances"])
        p["status"] = ("resolved" if p["targets"] else
                       "debt" if n >= THRESHOLD and name in debt else
                       "unresolved" if n >= THRESHOLD else "watching")
        if p["status"] == "unresolved":
            fails.append(f"pattern {name} has {n} instances and no resolution: mint the smallest layer "
                         f"(skill, check or knowledge) and record it with `add --target` (self-improve)")

    targeted: dict = {}
    for r in rows:
        if r.get("target"):
            targeted.setdefault(r["target"], set()).add(r["instance_ref"])
    base_hubs = set(base.get("hubs") or [])
    for name, h in sorted(ctx["hubs"].items()):
        if name in base_hubs:
            continue
        if h.get("rigor_role") == "command-hub" and name in ctx["hub_detectors"]:
            continue
        n = len(targeted.get(h.get("path") or "", ()))
        if n < THRESHOLD:
            fails.append(f"new {h.get('tier', 'hub')} {name} is not baselined and has {n} rule-of-three "
                         f"row(s) targeting {h.get('path')} (needs {THRESHOLD}, or a command-hub with a "
                         f"HUB_DETECTORS row)")
    base_fw = set(base.get("frameworks") or [])
    for rel, consumers in sorted(ctx["frameworks"].items()):
        if rel not in base_fw and consumers < THRESHOLD:
            fails.append(f"new framework {rel} has {consumers} consumer(s) (needs {THRESHOLD} skills or "
                         f"frameworks naming it)")

    prev = ctx.get("base_baseline")
    if prev is not None:
        for key in ("hubs", "frameworks", "unresolved_patterns"):
            grew = sorted(set(base.get(key) or []) - set(prev.get(key) or []))
            for g in grew:
                fails.append(f"baseline grew: {key} gained {g} relative to {ctx.get('base_ref', 'HEAD')} "
                             f"(the baseline may only shrink)")
    stale = (sorted(base_hubs - set(ctx["hubs"])) + sorted(base_fw - set(ctx["frameworks"]))
             + sorted(d for d in debt if patterns.get(d, {}).get("status") != "debt"))
    if stale:
        notes.append(f"{len(stale)} baseline entr{'y' if len(stale) == 1 else 'ies'} no longer apply "
                     f"({', '.join(stale[:5])}); lower it: rule_of_three.py baseline --write")
    return {"failures": fails, "notes": notes, "patterns": patterns, "rows": len(rows)}


def gather(root: Path = ROOT, env: Optional[dict] = None) -> dict:
    sids, fams, devs = surface_tables(root)
    ref = base_ref(root, env)
    fws = framework_files(root)
    return {
        "rows": read_rows(root), "surfaces": sids, "families": fams, "devices": devs,
        "resolve": make_resolver(root), "baseline": read_baseline(root),
        "base_baseline": baseline_at(root, ref), "base_ref": ref,
        "hubs": registry_hubs(root), "hub_detectors": hub_detector_keys(root),
        "frameworks": {f: framework_consumers(root, f) for f in fws},
    }


def check(root: Path = ROOT, env: Optional[dict] = None) -> dict:
    return evaluate(gather(root, env))


def next_baseline(ctx: dict, res: dict) -> dict:
    """Current state, intersected with the existing baseline when there is one (only shrinks)."""
    now = {"hubs": sorted(ctx["hubs"]), "frameworks": sorted(ctx["frameworks"]),
           "unresolved_patterns": sorted(n for n, p in res["patterns"].items()
                                         if not p["targets"] and len(p["instances"]) >= THRESHOLD)}
    old = ctx["baseline"]
    if old is not None:
        now = {k: sorted(set(v) & set(old.get(k) or [])) for k, v in now.items()}
    return now


# ------------------------------------------------------------------------------ CLI

def _detect(root: Path) -> dict:
    if str(TOOLS) not in sys.path:
        sys.path.insert(0, str(TOOLS))
    import profile_resolve as pr  # the one home for detect_surface / current_device (3d)
    det = pr.detect_surface(root=root)
    try:
        dev = str(pr.current_device(root=root).get("id") or "unknown")
    except Exception:  # noqa: BLE001
        dev = "unknown"
    return {"surface": det.get("acting_host") or "unknown", "family": det.get("family") or "unknown",
            "device": dev}


def build_row(pattern: str, evidence: str, *, target: Optional[str], note: Optional[str], stamp: dict,
              now: Optional[datetime] = None) -> dict:
    ts = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    row = {"ts": ts, "pattern": pattern, "instance_ref": evidence, "surface": stamp["surface"],
           "family": stamp["family"], "device": stamp["device"]}
    if target:
        row["target"] = target
    if note:
        row["note"] = note
    return row


def cmd_add(args, root: Path, detect: Callable[[Path], dict] = _detect) -> int:
    row = build_row(args.pattern, args.evidence, target=args.target, note=args.note, stamp=detect(root))
    sids, fams, devs = surface_tables(root)
    ok, errs = validate_row(row, surfaces=sids, families=fams, devices=devs, resolve=make_resolver(root))
    existing = {(r.get("pattern"), r.get("instance_ref")) for _, raw in read_rows(root)
                for r in [_safe_json(raw)] if isinstance(r, dict)}
    if ok and (row["pattern"], row["instance_ref"]) in existing:
        errs = [f"{row['instance_ref']} is already an instance of {row['pattern']}"]
    if errs:
        for e in errs:
            print(f"rule-of-three: refused: {e}", file=sys.stderr)
        return 1
    line = json.dumps(row, ensure_ascii=False, separators=(", ", ": "))
    if args.print:
        print(line)
        return 0
    path = root / LOG_REL
    with path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    n = sum(1 for k in existing if k[0] == row["pattern"]) + 1
    print(f"rule-of-three: {row['pattern']} now has {n} instance(s) (surface {row['surface']})")
    if n >= THRESHOLD and not row.get("target"):
        print(f"rule-of-three: {row['pattern']} reached {THRESHOLD}: mint the smallest layer and record it "
              "with --target, or the harness fails this pattern")
    return 0


def _safe_json(raw: str):
    try:
        return json.loads(raw)
    except ValueError:
        return None


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add", help="append one instance row (stamps ts, surface, family, device)")
    a.add_argument("--pattern", required=True)
    a.add_argument("--evidence", "--instance-ref", dest="evidence", required=True,
                   help="clone-visible repo path or commit SHA")
    a.add_argument("--target", help="resolution path (skill, check, knowledge or decision), or the hub justified")
    a.add_argument("--note")
    a.add_argument("--print", action="store_true", help="print the row instead of appending (copy-ready)")
    sub.add_parser("list", help="patterns with instance counts and status")
    c = sub.add_parser("check", help="run the growth check")
    c.add_argument("--json", action="store_true")
    b = sub.add_parser("baseline", help="rewrite the baseline (it only ever shrinks)")
    b.add_argument("--write", action="store_true", required=True)
    args = ap.parse_args(argv)
    root = ROOT

    if args.cmd == "add":
        return cmd_add(args, root)
    ctx = gather(root)
    res = evaluate(ctx)
    if args.cmd == "list":
        for name, p in sorted(res["patterns"].items()):
            tgt = f" -> {', '.join(p['targets'])}" if p["targets"] else ""
            print(f"{name:<40} {len(p['instances'])}  {p['status']}{tgt}")
        return 0
    if args.cmd == "check":
        if args.json:
            print(json.dumps({k: v for k, v in res.items()}, indent=2, default=list))
        else:
            for f in res["failures"]:
                print(f"  ✗ {f}")
            for n in res["notes"]:
                print(f"  · {n}")
            print(f"rule-of-three: {'FAIL' if res['failures'] else 'OK'} — {res['rows']} row(s), "
                  f"{len(res['patterns'])} pattern(s)")
        return 1 if res["failures"] else 0
    nb = next_baseline(ctx, res)
    doc = ("H14 rule-of-three baseline: hubs, foundations and frameworks that predate the log, and "
           "patterns grandfathered at three or more instances without a resolution. It may only shrink "
           "(workspace-harness check_rule_of_three); regenerate with rule_of_three.py baseline --write.")
    out = {"schema_version": 1, "doc": doc, **nb}
    (root / BASELINE_REL).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"rule-of-three: baseline written ({len(nb['hubs'])} hubs/foundations, {len(nb['frameworks'])} "
          f"frameworks, {len(nb['unresolved_patterns'])} grandfathered pattern(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
