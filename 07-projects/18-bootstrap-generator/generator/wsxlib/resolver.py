"""The Resolver's mechanical hand — `wsx resolve`.

The *brain* (brain/resolver.md) decides everything with judgment: which capability
PULLs / PULL+PATCHes / GENERATEs, from which registry, into which hub, with which
reconciled triggers. It writes those decisions into a machine-readable plan
(`context/skill-plan.json`) and, after the human approves the review gate, hands it
to this command. `wsx resolve` does only the deterministic half — fetch, pin,
namespace, scaffold, register — and never makes a sourcing decision itself.

Invariants enforced here (see brain/resolver.md):
  * Pin        — a pulled skill is stored byte-identical to what was fetched and
                 hashed; routing metadata lives in manifest.json, not by editing the
                 pulled file, so the pin stays verifiable and re-fetchable.
  * Namespace  — pulled skills land under skills/pulled-<registry>-<name>/, separate
                 from the person's canonical skills, collision-proof, provenance-obvious.
  * Read-only  — the pulled SKILL.md is written 0o444; patches go in a sibling
                 overlay.md, never into the pulled file.
  * No silent unvetted pull — skills.sh / community entries are refused unless the
                 plan marks them audited, or --allow-unvetted is passed explicitly.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

from . import core, skills, yamlio

# Registries with no official vetting — a match here must be audited by the brain
# before install. Matched case-insensitively against the plan entry's `registry`.
UNVETTED = ("skills.sh", "community")

_FETCH_TIMEOUT = 15  # seconds


def _slug(s: str) -> str:
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9]+", "-", (s or "").lower())).strip("-")


def _ns_name(registry: str, name: str) -> str:
    """Namespaced folder name: provenance in the name, canonical tree left clean."""
    reg = _slug(registry) or "unknown"
    return f"pulled-{reg}-{_slug(name)}"


def _sha256_bytes(b: bytes) -> str:
    return "sha256:" + hashlib.sha256(b).hexdigest()


def _fetch(source: str, base: Path) -> bytes:
    """Fetch a SKILL.md body. Supports http(s)://, file://, and local paths
    (absolute, or relative to the plan file / workspace root). Raises on failure."""
    if source.startswith(("http://", "https://")):
        req = urllib.request.Request(source, headers={"User-Agent": "wsx-resolve/0.2"})
        with urllib.request.urlopen(req, timeout=_FETCH_TIMEOUT) as r:  # noqa: S310
            return r.read()
    if source.startswith("file://"):
        return Path(source[len("file://"):]).read_bytes()
    p = Path(source)
    if not p.is_absolute():
        # try relative to the plan's dir first, then the workspace root
        for cand in (base / source, base.parent / source):
            if cand.exists():
                p = cand
                break
    return p.read_bytes()


def _is_unvetted(registry: str) -> bool:
    reg = (registry or "").lower()
    return any(u in reg for u in UNVETTED)


def _pull_one(root: Path, e: dict, update: bool, allow_unvetted: bool) -> str:
    """Execute one PULL / PULL+PATCH entry. Returns a status word for the tally.
    Self-contained: load-modify-saves the manifest so it composes cleanly with the
    generate/composite handlers (which persist their own records too)."""
    name = e["name"]
    registry = e.get("registry", "")
    source_url = e.get("url") or e.get("source_url") or ""
    patched = e["source"] == "pulled+patched"

    if not source_url:
        print(f"  ✗ {name}: pulled entry has no 'url' to fetch from — skipped")
        return "refused"

    # trust gate — never silently install from an unvetted directory
    if _is_unvetted(registry) and not e.get("audited") and not allow_unvetted:
        print(f"  ✗ {name}: registry '{registry}' is UNVETTED and the plan does not mark it "
              "audited — refused. The brain must audit it (read the body, check the license), "
              "set \"audited\": true in the plan, or re-run with --allow-unvetted.")
        return "refused"

    ns = _ns_name(registry, name)
    sk_dir = root / "skills" / ns
    sk = sk_dir / "SKILL.md"

    man = core.load_manifest(root)
    idx = man.setdefault("skills", {})

    # pin-drift guard: a remote skill changing under the person's feet is a
    # deliberate, visible bump — never a silent mutation.
    prior = idx.get(ns, {})
    try:
        data = _fetch(source_url, base=root / "context")
    except (urllib.error.URLError, OSError, ValueError) as ex:
        print(f"  ✗ {name}: fetch failed ({source_url}) — {ex}")
        return "refused"
    pin = _sha256_bytes(data)

    if sk.exists() and prior.get("pin") == pin:
        # already pinned to this exact content — idempotent no-op, no rewrite
        print(f"  · {name}: unchanged (pinned {pin[7:19]}…)")
        return "unchanged"
    if sk.exists() and prior.get("pin") and prior["pin"] != pin and not update:
        print(f"  ⚠ {name}: upstream changed — pinned {prior['pin'][7:19]}…, "
              f"fetched {pin[7:19]}…. Re-run with --update to bump the pin (or leave it pinned).")
        return "skipped"

    sk_dir.mkdir(parents=True, exist_ok=True)
    if sk.exists():
        sk.chmod(0o644)  # was read-only; allow the re-pin rewrite
    sk.write_bytes(data)
    sk.chmod(0o444)      # read-only: a pulled skill is immutable; patch via overlay

    rec = {
        "path": f"skills/{ns}/SKILL.md",
        "hub": e.get("hub", "") or ns,
        "kind": e.get("kind", "spoke"),
        "triggers": e.get("triggers", []),
        "source": e["source"],
        "hash": pin,
        "pin": pin,
        "registry": registry,
        "url": source_url,
        "read_only": True,
        "pulled_at": core.now_stamp(),
    }
    for k in ("license", "trust"):
        if e.get(k):
            rec[k] = e[k]

    verb = "re-pinned" if prior else "pulled"
    status = "pulled"
    if patched:
        overlay = sk_dir / "overlay.md"
        if not overlay.exists():
            overlay.write_text(_overlay_skeleton(name, e.get("hub", "")), encoding="utf-8")
            rec["overlay"] = f"skills/{ns}/overlay.md"
        status = "patched"

    idx[ns] = rec
    core.save_manifest(root, man)
    flag = "  ⚠ UNVETTED — audited" if _is_unvetted(registry) else ""
    extra = " + overlay scaffolded" if patched else ""
    print(f"  ✓ {verb} {name} → {ns}  [{registry or 'local'}]  pin {pin[7:19]}…{extra}{flag}")
    return status


def _overlay_skeleton(name: str, hub: str) -> str:
    return (
        f"---\noverlay_for: {name}\nhub: {hub}\n---\n\n"
        f"# Overlay — your deltas over the pulled `{name}`\n\n"
        "> **The pulled skill is READ-ONLY. This overlay is where your changes live;\n"
        "> the surface composes `pulled base + this overlay` at load. The brain fills\n"
        "> the sections below — never edit the pulled SKILL.md.**\n\n"
        "## Overridden / added rules\n\n"
        "_(the guidance that supersedes the upstream skill — house style, an extra\n"
        "guardrail, a banned pattern)_\n\n"
        "## Added triggers\n\n"
        "_(any triggers to add beyond the upstream skill's own)_\n\n"
        "## Swapped examples\n\n"
        "_(examples in this person's real domain that replace generic upstream ones)_\n"
    )


_SOURCES_OPEN = "<!-- wsx:sources -->"
_SOURCES_CLOSE = "<!-- /wsx:sources -->"


def _render_sources_block(refs: list) -> str:
    """The attribution block for a composite skill. Workspace convention: author in
    our own voice, cite the source, never copy (08-knowledge/…/skill-ecosystem)."""
    lines = [
        _SOURCES_OPEN,
        "## Sources & further reading",
        "",
        "_Synthesized in this workspace's own voice from the authoritative references",
        "below — distilled guidance and best practice, not copied text._",
        "",
    ]
    for r in refs:
        title = r.get("title") or r.get("url") or "untitled source"
        bits = [f"- **{title}**"]
        if r.get("publisher"):
            bits.append(f" — {r['publisher']}")
        if r.get("url"):
            bits.append(f" · <{r['url']}>")
        if r.get("note"):
            bits.append(f" _({r['note']})_")
        lines.append("".join(bits))
    lines += ["", _SOURCES_CLOSE, ""]
    return "\n".join(lines)


def _inject_sources(sk: Path, refs: list) -> None:
    """Idempotently place the Sources block at the end of a skill body, between
    markers — replacing an existing block, never clobbering the brain's prose."""
    if not refs:
        return
    text = sk.read_text(encoding="utf-8")
    block = _render_sources_block(refs)
    i, j = text.find(_SOURCES_OPEN), text.find(_SOURCES_CLOSE)
    if i != -1 and j != -1:
        text = text[:i] + block + text[j + len(_SOURCES_CLOSE):].lstrip("\n")
    else:
        text = text.rstrip() + "\n\n" + block
    sk.write_text(text, encoding="utf-8")


def _cache_references(root: Path, name: str, refs: list) -> None:
    """Opt-in (--cache-refs): fetch each reference URL, pin it, and cache a snapshot
    under skills/<name>/references/ (read-only) for verifiable, dated provenance.
    Records the pin + cached path back onto each ref dict."""
    ref_dir = root / "skills" / name / "references"
    for r in refs:
        url = r.get("url")
        if not url:
            continue
        try:
            data = _fetch(url, base=root / "context")
        except (urllib.error.URLError, OSError, ValueError) as ex:
            r["cache_error"] = str(ex)
            print(f"    ⚠ {name}: could not cache reference {url} — {ex}")
            continue
        ref_dir.mkdir(parents=True, exist_ok=True)
        ext = ".html" if b"<html" in data[:2048].lower() else ".txt"
        dst = ref_dir / (_slug(r.get("title") or url) + ext)
        if dst.exists():
            dst.chmod(0o644)
        dst.write_bytes(data)
        dst.chmod(0o444)
        r["pin"] = _sha256_bytes(data)
        r["cached"] = f"skills/{name}/references/{dst.name}"
        r["retrieved"] = core.now_stamp()


def _generate_one(root: Path, e: dict, cache_refs: bool = False) -> str:
    """A GENERATE / COMPOSITE entry. Delegates the skeleton to `wsx skill add`, then —
    if the plan carries references[] — cites them (author-voice Sources block, optional
    cache+pin). A composite skill = the person's judgment + distilled authoritative
    reference; per our own skill-ecosystem knowledge, that's the highest-value kind."""
    name = e["name"]
    refs = e.get("references") or []
    composite = bool(refs) or e.get("source") == "composite"
    sk = root / "skills" / name / "SKILL.md"

    fresh = not sk.exists()
    if fresh:
        skills.add(
            root, name,
            desc=e.get("desc", e.get("description", f"{name} (generated).")),
            triggers=e.get("triggers", []),
            hub=e.get("hub", ""),
            source="generated",
            title=e.get("title", ""),
            kind=e.get("kind", "spoke"),
            level=e.get("level", "intermediate"),
            seniority=e.get("seniority", ""),
        )
    elif not refs:
        print(f"  · {name}: already exists — left as-is (enrich in place)")
        return "skipped"

    if composite:
        if cache_refs:
            _cache_references(root, name, refs)
        _inject_sources(sk, refs)
        # stamp the manifest record as composite + carry the citations
        man = core.load_manifest(root)
        rec = man.setdefault("skills", {}).get(name)
        if rec is not None:
            rec["composite"] = True
            rec["references"] = refs
            core.save_manifest(root, man)
        cached = sum(1 for r in refs if r.get("cached"))
        note = f", {cached} cached+pinned" if cached else ""
        print(f"  ✓ composite {name}: {len(refs)} reference(s) cited{note}"
              + ("" if fresh else " (updated citations)"))
        return "composite" if fresh else "recited"
    return "generated"


def resolve(root: Path, plan_path: str | None = None, update: bool = False,
            allow_unvetted: bool = False, cache_refs: bool = False) -> int:
    """Execute an approved skill plan: fetch+pin PULLs, scaffold PATCH overlays,
    delegate GENERATEs, and register everything into manifest.json. Returns non-zero
    if any entry was refused (so callers/CI can gate on a clean resolve)."""
    plan_file = Path(plan_path) if plan_path else root / "context" / "skill-plan.json"
    if not plan_file.exists():
        print(f"no skill plan at {_rel(plan_file, root)}.")
        print("The brain writes one after the review gate — a JSON file shaped like:")
        print('  { "skills": [ { "name": "...", "source": "pulled|pulled+patched|generated",')
        print('                  "registry": "...", "url": "...", "hub": "...",')
        print('                  "triggers": ["..."], "audited": true } ] }')
        print("Then: wsx resolve  (add --plan <file> to point elsewhere).")
        return 0

    try:
        plan = json.loads(plan_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as ex:
        raise SystemExit(f"error: {_rel(plan_file, root)} is not valid JSON — {ex}")

    entries = plan.get("skills") or []
    if not entries:
        print(f"{_rel(plan_file, root)} has no skills[] — nothing to resolve.")
        return 0

    # Each handler load-modify-saves the manifest itself (so generate/composite and
    # pull compose cleanly); resolve() does NOT hold a stale copy across the loop.
    tally = {"pulled": 0, "patched": 0, "generated": 0, "composite": 0,
             "recited": 0, "unchanged": 0, "skipped": 0, "refused": 0}

    print(f"resolving {len(entries)} skill(s) from {_rel(plan_file, root)} …")
    for e in entries:
        name, src = e.get("name"), e.get("source")
        if not name or not src:
            print(f"  ✗ entry missing 'name' or 'source': {e!r}")
            tally["refused"] += 1
            continue
        if src in ("generated", "composite"):
            status = _generate_one(root, e, cache_refs=cache_refs)
        elif src in ("pulled", "pulled+patched"):
            status = _pull_one(root, e, update, allow_unvetted)
        else:
            print(f"  ✗ {name}: unknown source '{src}' "
                  "(want pulled | pulled+patched | generated | composite)")
            status = "refused"
        tally[status] += 1

    summary = ", ".join(f"{v} {k}" for k, v in tally.items() if v)
    print(f"✓ resolve: {summary or 'nothing to do'}")
    if tally["refused"]:
        print("  some entries were refused — fix the plan (or --allow-unvetted) and re-run.")
    if tally["skipped"]:
        print("  skipped entries are pinned as-is; --update bumps a changed pin.")
    return 1 if tally["refused"] else 0


def _rel(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except ValueError:
        return str(p)
