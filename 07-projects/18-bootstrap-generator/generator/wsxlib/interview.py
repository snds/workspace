"""Interview save-point + workspace shape ledger (Waves 5–6).

Two files, two lifecycles — do not mix them.

  Temporary (resume the conversation):
    <workspace>/.wsx/interview-session.json   gitignored
    ~/.wsx/in-progress.json                   pointer, or the full session if no folder yet

  Durable (shape only, no transcript / no personal.md):
    <workspace>/.wsx/outcome.json             workspace updates this
    ~/.wsx/index.json                         generator-side index of {path, updated, digest}

CI / a missing ~/.wsx is a clean no-op (same class as canvas harvest).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from . import __version__, core, dest, layout, secretscan

GLOBAL = Path.home() / ".wsx"
STALE_DAYS = 14

# Neutral persona seeds — labels, not anyone's life. Ceiling of five until a
# real user-test adds one. Never a clone of the author's vault.
SEEDS = {
    "maker": {
        "label": "Individual maker",
        "fills": {"use_context": "mixed", "lifecycle.separation": "walled",
                  "lifecycle.automation": "standard"},
        "still_asked": "craft, expertise altitude, dest, voice",
    },
    "research": {
        "label": "Product / research (one repo)",
        "fills": {"use_context": "professional"},
        "still_asked": "role, briefs vs code, dest wall, dest path",
    },
    "staff": {
        "label": "Staff IC at a company",
        "fills": {"use_context": "professional", "lifecycle.separation": "walled"},
        "still_asked": "employer-safe dest path (wall:external), crafts, surfaces",
    },
    "hobby": {
        "label": "Student / hobbyist",
        "fills": {"use_context": "personal", "lifecycle.separation": "walled"},
        "still_asked": "the one high-energy craft",
    },
    "notes": {
        "label": "Already have notes",
        "fills": {},
        "still_asked": "gaps only — examine first; dest + voice",
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _session_path(root: Path) -> Path:
    return root / ".wsx" / "interview-session.json"


def _outcome_path(root: Path) -> Path:
    return root / ".wsx" / "outcome.json"


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if secretscan.blocked(secretscan.scan_text(text)):
        raise SystemExit("error: secret scan hit — interview/outcome file not written")
    path.write_text(text, encoding="utf-8")


def _set_profile_fields(root: Path, fields: dict) -> None:
    """Write draft fields only. Must not emit adapters (confirm gate still owns that)."""
    if not fields or not core.profile_path(root).exists():
        return
    prof = core.load_profile(root)
    for dotted, value in fields.items():
        cur = prof
        parts = dotted.split(".")
        for p in parts[:-1]:
            nxt = cur.get(p)
            if not isinstance(nxt, dict):
                nxt = {}
                cur[p] = nxt
            cur = nxt
        cur[parts[-1]] = value
    core.save_profile(root, prof)


def global_in_progress() -> dict:
    return _read_json(GLOBAL / "in-progress.json")


def checkpoint(root: Path | None, movement: str = "", last_q: str = "",
               last_a: str = "", remaining: str = "", seed: str = "",
               tags: str = "") -> int:
    """Silent save. The user is not asked. Dual-home so a fresh generator still sees it."""
    payload = {
        "wsx_version": __version__,
        "updated": _now(),
        "movement": movement,
        "last_question": last_q,
        "last_answer": last_a,
        "remaining": [p.strip() for p in remaining.split(",") if p.strip()],
        "seed": seed,
        "field_tags": {},  # dotted.key -> answered|assumed|defaulted
        "workspace": str(root) if root else "",
        "profile_draft": {},
        "dest_draft": {},
    }
    if tags:
        for pair in tags.split(","):
            if "=" in pair:
                k, _, v = pair.partition("=")
                payload["field_tags"][k.strip()] = v.strip()
    if root and (root / ".wsx").is_dir():
        try:
            payload["profile_draft"] = core.load_profile(root)
        except Exception:  # noqa: BLE001
            payload["profile_draft"] = {}
        try:
            payload["dest_draft"] = dest.load(root)
        except Exception:  # noqa: BLE001
            payload["dest_draft"] = {}
        _write_json(_session_path(root), payload)
        try:
            _set_profile_fields(root, {"lifecycle.interview": "in-progress"})
        except Exception:  # noqa: BLE001
            pass
        pointer = {"workspace": str(root.resolve()), "updated": payload["updated"],
                   "movement": movement}
        _write_json(GLOBAL / "in-progress.json", pointer)
        print(f"✓ interview checkpoint ({movement or 'in progress'}) → .wsx/interview-session.json")
        return 0
    # No folder yet — keep the full session in the user-global pointer.
    _write_json(GLOBAL / "in-progress.json", payload)
    print("✓ interview checkpoint (no workspace yet) → ~/.wsx/in-progress.json")
    return 0


def status(root: Path | None = None) -> int:
    """Look for an in-progress interview. Missing ~/.wsx is a clean no-op."""
    glob = global_in_progress()
    local = {}
    if root and _session_path(root).exists():
        local = _read_json(_session_path(root))
    data = local or glob
    if not data:
        print("interview: no in-progress session")
        return 0
    ws = data.get("workspace") or (str(root) if root else "")
    print("interview: in-progress session found")
    print(f"  workspace: {ws or '(not created yet)'}")
    print(f"  movement:  {data.get('movement') or '(start)'}")
    print(f"  remaining: {', '.join(data.get('remaining') or []) or '(none listed)'}")
    if data.get("last_question"):
        print(f"  last Q:    {data['last_question']}")
    if data.get("last_answer"):
        print(f"  last A:    {data['last_answer']}")
    if data.get("seed"):
        print(f"  seed:      {data['seed']}")
    print("  continue this workspace, or start over: `wsx interview continue` / `wsx interview abandon`")
    return 0


def continue_session(root: Path | None = None) -> int:
    """Print restore payload for the brain. Does not re-ask completed movements."""
    glob = global_in_progress()
    local = _read_json(_session_path(root)) if root else {}
    data = local or glob
    if not data:
        print("interview: nothing to continue")
        return 1
    print(json.dumps(data, indent=2))
    return 0


def abandon(root: Path | None = None, wipe_draft: bool = False) -> int:
    """Delete only the session files. Wiping the draft folder needs a second confirm."""
    if root and _session_path(root).exists():
        _session_path(root).unlink()
        print("  removed .wsx/interview-session.json")
    ip = GLOBAL / "in-progress.json"
    if ip.exists():
        ip.unlink()
        print("  removed ~/.wsx/in-progress.json")
    if wipe_draft:
        print("  --wipe-draft is a second confirm the brain must obtain; this command")
        print("    does not delete the workspace folder.")
        return 1
    print("✓ interview session abandoned (workspace folder left in place)")
    return 0


def complete(root: Path) -> int:
    """Interview confirmed + emit done: drop temp session files, write outcome."""
    if _session_path(root).exists():
        _session_path(root).unlink()
    ip = GLOBAL / "in-progress.json"
    # Only drop the global pointer if it points at THIS workspace.
    glob = _read_json(ip)
    if glob.get("workspace") in ("", str(root), str(root.resolve())):
        if ip.exists():
            ip.unlink()
    try:
        _set_profile_fields(root, {"lifecycle.interview": "complete"})
    except Exception:  # noqa: BLE001
        pass
    refresh_outcome(root)
    print("✓ interview complete — session files cleaned; outcome written")
    return 0


def list_seeds() -> int:
    print("Neutral persona seeds (opt-in, start only). No seed is the default.\n")
    for sid, rec in SEEDS.items():
        print(f"  {sid:10} {rec['label']}")
        print(f"             still asked: {rec['still_asked']}")
    print("\n  apply: wsx interview seed <id>   escape hatch: skip this beat")
    return 0


def apply_seed(root: Path | None, seed_id: str) -> int:
    rec = SEEDS.get(seed_id)
    if not rec:
        raise SystemExit(f"error: unknown seed '{seed_id}'. wsx interview seed list")
    if root and core.profile_path(root).exists():
        _set_profile_fields(root, rec["fills"])
    checkpoint(root, movement="M0", seed=seed_id)
    print(f"✓ seed '{seed_id}' ({rec['label']}) applied as a DRAFT — still asked: {rec['still_asked']}")
    print("  a seed is not a finished workspace; tighten what's wrong, then confirm before emit.")
    return 0


# ------------------------------------------------------------------ outcome ---
def shape(root: Path) -> dict:
    """Workspace shape only. No transcript, no personal.md, no dest file bodies."""
    lay = layout.of(root)
    prof = {}
    try:
        prof = core.load_profile(root)
    except Exception:  # noqa: BLE001
        pass
    man = {}
    try:
        man = core.load_manifest(root)
    except Exception:  # noqa: BLE001
        pass
    dmap = {}
    try:
        dmap = dest.load(root)
    except Exception:  # noqa: BLE001
        pass
    skills = man.get("skills") or {}
    hubs, spokes = [], []
    for name, rec in skills.items():
        row = {"name": name, "triggers": rec.get("triggers") or [],
               "hub": rec.get("hub") or "", "kind": rec.get("kind") or ""}
        if rec.get("kind") == "hub":
            hubs.append(row)
        else:
            spokes.append(row)
    dests = []
    for name, rec in (dmap.get("dests") or {}).items():
        dests.append({"name": name, "wall": rec.get("wall") or "",
                      "scope": rec.get("scope") or ""})
    pj = lay.dir("projects")
    projects = []
    if pj.is_dir():
        projects = sorted(d.name for d in pj.iterdir()
                          if d.is_dir() and not d.name.startswith((".", "_"))
                          and (d / "PROJECT.md").exists())
    identity = (prof.get("identity") or {}).get("handle") or ""
    return {
        "wsx_version": __version__,
        "updated": _now(),
        "layout": "numbered" if lay.numbered else "flat",
        "handle": identity,
        "surfaces": (prof.get("surfaces") or {}).get("agents") or [],
        "dests": dests,
        "dest_binds": list((dmap.get("binds") or {}).keys()),
        "hubs": hubs,
        "spokes": spokes,
        "projects": projects,
        "counts": {
            "skills": len(skills),
            "projects": len(projects),
            "dests": len(dests),
        },
    }


def _digest(data: dict) -> str:
    blob = json.dumps(data, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def refresh_outcome(root: Path) -> Path:
    """Workspace updates its own shape file; copy digest into ~/.wsx/index.json."""
    data = shape(root)
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    if secretscan.blocked(secretscan.scan_text(text)):
        raise SystemExit("error: secret scan hit — outcome not written")
    out = _outcome_path(root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    idx_path = GLOBAL / "index.json"
    idx = _read_json(idx_path)
    entries = idx.get("workspaces") or []
    if not isinstance(entries, list):
        entries = []
    path = str(root.resolve())
    entries = [e for e in entries if isinstance(e, dict) and e.get("path") != path]
    entries.append({"path": path, "updated": data["updated"], "digest": _digest(data),
                    "handle": data.get("handle") or "",
                    "counts": data.get("counts") or {}})
    _write_json(idx_path, {"updated": data["updated"], "workspaces": entries})
    return out


def try_refresh(root: Path) -> None:
    """Best-effort shape update. Missing ~/.wsx or a lock must not fail the caller."""
    try:
        refresh_outcome(root)
    except Exception:  # noqa: BLE001
        pass


def doctor_rebind(root: Path) -> None:
    """If the vault moved, rebind the index path. Missing ~/.wsx is fine."""
    idx_path = GLOBAL / "index.json"
    if not idx_path.exists():
        return
    refresh_outcome(root)


# ------------------------------------------------------------------ CLI ---
def run(root: Path | None, action: str, **kw) -> int:
    if action == "checkpoint":
        return checkpoint(root, movement=kw.get("movement") or "",
                          last_q=kw.get("last_q") or "", last_a=kw.get("last_a") or "",
                          remaining=kw.get("remaining") or "", seed=kw.get("seed") or "",
                          tags=kw.get("tags") or "")
    if action == "status":
        return status(root)
    if action == "continue":
        return continue_session(root)
    if action == "abandon":
        return abandon(root, wipe_draft=bool(kw.get("wipe_draft")))
    if action == "complete":
        if not root:
            raise SystemExit("error: interview complete needs a workspace")
        return complete(root)
    if action == "seed":
        sid = kw.get("seed_id") or ""
        if sid in ("", "list"):
            return list_seeds()
        return apply_seed(root, sid)
    if action == "outcome":
        if not root:
            raise SystemExit("error: outcome refresh needs a workspace")
        refresh_outcome(root)
        print(f"✓ outcome refreshed → .wsx/outcome.json")
        return 0
    raise SystemExit("error: interview expects checkpoint|status|continue|abandon|complete|seed")
