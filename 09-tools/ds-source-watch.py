#!/usr/bin/env python3
"""
ds-source-watch.py — fetch or check freshness of DS ontology / spec sources.

Report-first. Never rewrites ontology, knowledge, or the DSDS constitution.
Stdlib-only.

Usage:
  python3 09-tools/ds-source-watch.py --check     # stale snapshot? no network
  python3 09-tools/ds-source-watch.py --fetch     # HTTP GET, update snapshot, print diffs
  python3 09-tools/ds-source-watch.py --fetch --json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "02-shared-references" / "ds-source-watch.json"
UA = "snds-workspace-ds-source-watch/1.0"


def load_reg():
    return json.loads(REG.read_text(encoding="utf-8"))


def snapshot_path(reg) -> Path:
    return ROOT / reg["snapshot"]


def load_snap(path: Path) -> dict:
    if not path.is_file():
        return {"checked_at": None, "sources": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def sha(text: bytes) -> str:
    return hashlib.sha256(text).hexdigest()[:16]


def fetch_one(url: str, timeout: int = 25) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,text/plain,*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            body = res.read()
            return {
                "ok": True,
                "status": getattr(res, "status", 200),
                "etag": res.headers.get("ETag"),
                "last_modified": res.headers.get("Last-Modified"),
                "hash": sha(body),
                "bytes": len(body),
                "error": None,
            }
    except urllib.error.HTTPError as e:
        return {"ok": False, "status": e.code, "etag": None, "last_modified": None,
                "hash": None, "bytes": 0, "error": f"HTTP {e.code}"}
    except Exception as e:
        return {"ok": False, "status": None, "etag": None, "last_modified": None,
                "hash": None, "bytes": 0, "error": str(e)}


def parse_checked(iso: str | None):
    if not iso:
        return None
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


def check(reg, snap, now: datetime) -> list[str]:
    lines = []
    stale_days = int(reg.get("stale_days", 30))
    checked = parse_checked(snap.get("checked_at"))
    if checked is None:
        lines.append("P1 snapshot missing — run python3 09-tools/ds-source-watch.py --fetch")
        return lines
    age = now - checked
    if age > timedelta(days=stale_days):
        lines.append(
            f"P1 ds-source-watch snapshot is {age.days} days old "
            f"(stale_days={stale_days}). Run --fetch, then judge diffs."
        )
    else:
        lines.append(f"ok snapshot age {age.days}d (limit {stale_days}d) · {snap['checked_at']}")
    n = len(reg.get("sources") or [])
    got = len(snap.get("sources") or {})
    if got != n:
        lines.append(f"P2 registry has {n} sources, snapshot has {got}")
    return lines


def fetch_all(reg) -> dict:
    now = datetime.now(timezone.utc)
    snap_path = snapshot_path(reg)
    prev = load_snap(snap_path)
    prev_src = prev.get("sources") or {}
    out_src = {}
    rows = []
    for src in reg["sources"]:
        sid = src["id"]
        result = fetch_one(src["url"])
        old = prev_src.get(sid) or {}
        changed = bool(result["ok"] and old.get("hash") and result["hash"] != old.get("hash"))
        is_new = bool(result["ok"] and not old.get("hash"))
        failed = not result["ok"]
        state = "failed" if failed else ("changed" if changed else ("new" if is_new else "unchanged"))
        rec = {
            **result,
            "id": sid,
            "name": src["name"],
            "url": src["url"],
            "affects": src.get("affects") or [],
            "state": state,
        }
        out_src[sid] = rec
        rows.append(rec)
    snap = {
        "checked_at": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "registry": "02-shared-references/ds-source-watch.json",
        "sources": {
            sid: {k: rec[k] for k in ("ok", "status", "etag", "last_modified", "hash", "bytes", "error", "url")}
            for sid, rec in out_src.items()
        },
    }
    snap_path.parent.mkdir(parents=True, exist_ok=True)
    snap_path.write_text(json.dumps(snap, indent=2) + "\n", encoding="utf-8")
    return {"snapshot": snap, "rows": rows}


def print_table(rows):
    print(f"{'state':<10} {'id':<28} {'affects':<22} note")
    for r in rows:
        note = r.get("error") or r.get("hash") or ""
        affects = ",".join(r.get("affects") or [])
        print(f"{r['state']:<10} {r['id']:<28} {affects:<22} {note}")
    changed = [r for r in rows if r["state"] == "changed"]
    failed = [r for r in rows if r["state"] == "failed"]
    print()
    print(f"{len(rows)} sources · {len(changed)} changed · {len(failed)} failed")
    if changed:
        print("Changed hashes are testimony. Do not edit ontology until a human judges the diff.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args()
    if not args.check and not args.fetch:
        ap.error("pass --check or --fetch")
    reg = load_reg()
    now = datetime.now(timezone.utc)
    if args.check and not args.fetch:
        lines = check(reg, load_snap(snapshot_path(reg)), now)
        if args.as_json:
            print(json.dumps({"mode": "check", "lines": lines}, indent=2))
        else:
            for line in lines:
                print(line)
        stale = any(line.startswith("P1") for line in lines)
        sys.exit(1 if stale else 0)
    result = fetch_all(reg)
    if args.check:
        result["check"] = check(reg, result["snapshot"], now)
    if args.as_json:
        print(json.dumps({
            "checked_at": result["snapshot"]["checked_at"],
            "rows": [{k: r[k] for k in ("id", "name", "state", "status", "hash", "error", "affects", "url")}
                     for r in result["rows"]],
        }, indent=2))
    else:
        print(f"snapshot {result['snapshot']['checked_at']}")
        print_table(result["rows"])
    sys.exit(1 if any(r["state"] == "failed" for r in result["rows"]) else 0)


if __name__ == "__main__":
    main()
