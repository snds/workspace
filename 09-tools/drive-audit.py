#!/usr/bin/env python3
"""
drive-audit.py — one-shot snapshot of Claude Workspace sync state.

Detects Google Drive for Desktop placeholders via the macOS UF_DATALESS flag.
Single-pass scan (one os.scandir tree walk) for speed during heavy sync.

Exit codes:
  0 — workspace looks fully synced (no placeholders, on-disk ≈ apparent)
  1 — still syncing
  2 — workspace path missing
"""

import os
import sys
import time

ROOT = "/Users/sean.sands/Library/CloudStorage/GoogleDrive-hello@snds.design/My Drive/Claude Workspace"
UF_DATALESS = 0x40000000
TOLERANCE_BYTES = 10 * 1024 * 1024  # 10 MB slack for "ready"


def human(n):
    n = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if n < 1024:
            return f"{n:.2f} {unit}"
        n /= 1024
    return f"{n:.2f} EB"


def pct(num, denom):
    return (num * 100.0 / denom) if denom > 0 else 0.0


def scan(root):
    """Returns (total_files, dataless_count, apparent_bytes, disk_bytes, per_top_level)."""
    total = 0
    dataless = 0
    apparent = 0
    blocks_512 = 0
    per_top = {}  # top-level dir name → {files, dataless}
    stack = [(root, None)]
    while stack:
        path, top = stack.pop()
        try:
            it = os.scandir(path)
        except OSError:
            continue
        with it:
            for entry in it:
                try:
                    is_dir = entry.is_dir(follow_symlinks=False)
                    is_file = entry.is_file(follow_symlinks=False)
                except OSError:
                    continue
                if is_dir:
                    new_top = top if top is not None else entry.name
                    stack.append((entry.path, new_top))
                elif is_file:
                    try:
                        st = entry.stat(follow_symlinks=False)
                    except OSError:
                        continue
                    total += 1
                    apparent += st.st_size
                    blocks_512 += st.st_blocks
                    is_dataless = bool(st.st_flags & UF_DATALESS)
                    if is_dataless:
                        dataless += 1
                    if top is not None:
                        bucket = per_top.setdefault(top, {"files": 0, "dataless": 0})
                        bucket["files"] += 1
                        if is_dataless:
                            bucket["dataless"] += 1
    return total, dataless, apparent, blocks_512 * 512, per_top


def main():
    if not os.path.isdir(ROOT):
        print(f"ERROR: workspace not found at:\n  {ROOT}", file=sys.stderr)
        return 2

    t0 = time.time()
    total, dataless, apparent, disk, per_top = scan(ROOT)
    elapsed = time.time() - t0

    downloaded = total - dataless
    pending = max(apparent - disk, 0)

    files_complete_pct = pct(downloaded, total)
    files_remaining_pct = pct(dataless, total)
    bytes_remaining_pct = pct(pending, apparent)

    bar = "=" * 66
    print(bar)
    print(" Drive sync audit — Claude Workspace")
    print(f" Time: {time.strftime('%Y-%m-%d %H:%M:%S %Z')} (scan took {elapsed:.1f}s)")
    print(bar)
    print(f" Files:        {total:,} total")
    print(f"               {downloaded:,} downloaded · {dataless:,} pending (placeholders)")
    print(f" Size:         {human(apparent)} apparent · {human(disk)} on disk")
    print(f"               {human(pending)} still to download")
    print("-" * 66)
    print(f" Complete:     {files_complete_pct:.1f}% of files")
    print(f" Remaining:    {files_remaining_pct:.1f}% of files · {bytes_remaining_pct:.1f}% of bytes")
    print(bar)

    ready = (dataless == 0) and (pending <= TOLERANCE_BYTES)
    if ready:
        print(" STATUS: READY — no placeholders, on-disk size matches apparent.")
        print("         Safe to open Obsidian and run git operations.")
    else:
        print(" STATUS: SYNCING — wait until placeholders reach 0.")

    if per_top:
        print()
        print(" Top-level breakdown:")
        for name in sorted(per_top.keys()):
            info = per_top[name]
            print(f"   {name:<32} {info['files']:>7,} files · {info['dataless']:>6,} pending")

    return 0 if ready else 1


if __name__ == "__main__":
    sys.exit(main())
