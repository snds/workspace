#!/usr/bin/env python3
"""
drive-monitor.py — live monitor of Claude Workspace Drive sync.

Single-pass scan per tick. Auto-exits when placeholders == 0 and on-disk size
is stable for 2 consecutive ticks.

Usage:
  drive-monitor.py [interval_seconds]   (default 60)

Press Ctrl-C to stop early.
Logs every line to: ~/drive-sync-tools/logs/drive-monitor_YYYY-MM-DD.log
"""

import os
import sys
import time
import datetime
import signal

ROOT = "/Users/sean.sands/Library/CloudStorage/GoogleDrive-hello@snds.design/My Drive/Claude Workspace"
UF_DATALESS = 0x40000000
LOGDIR = os.path.expanduser("~/drive-sync-tools/logs")


def human(n):
    n = float(n)
    sign = "-" if n < 0 else ""
    n = abs(n)
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if n < 1024:
            return f"{sign}{n:.2f} {unit}"
        n /= 1024
    return f"{sign}{n:.2f} EB"


def pct(num, denom):
    return (num * 100.0 / denom) if denom > 0 else 0.0


def fmt_eta(sec):
    if sec < 60:
        return f"{int(sec)}s"
    if sec < 3600:
        return f"{int(sec / 60)}m"
    h = int(sec / 3600)
    m = int((sec % 3600) / 60)
    return f"{h}h{m}m"


def scan(root):
    total = 0
    dataless = 0
    apparent = 0
    blocks_512 = 0
    stack = [root]
    while stack:
        path = stack.pop()
        try:
            it = os.scandir(path)
        except OSError:
            continue
        with it:
            for entry in it:
                try:
                    if entry.is_dir(follow_symlinks=False):
                        stack.append(entry.path)
                    elif entry.is_file(follow_symlinks=False):
                        st = entry.stat(follow_symlinks=False)
                        total += 1
                        apparent += st.st_size
                        blocks_512 += st.st_blocks
                        if st.st_flags & UF_DATALESS:
                            dataless += 1
                except OSError:
                    continue
    return total, dataless, apparent, blocks_512 * 512


def main():
    if not os.path.isdir(ROOT):
        print(f"ERROR: workspace not found at: {ROOT}", file=sys.stderr)
        return 2

    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    os.makedirs(LOGDIR, exist_ok=True)
    logfile = os.path.join(LOGDIR, f"drive-monitor_{datetime.date.today()}.log")
    log = open(logfile, "a", buffering=1)

    def emit(line):
        print(line)
        log.write(line + "\n")

    def stopper(signum, frame):
        emit("")
        emit("Monitor stopped (Ctrl-C).")
        log.close()
        sys.exit(130)

    signal.signal(signal.SIGINT, stopper)

    print(f"Monitoring: {ROOT}")
    print(f"Interval:   {interval}s (scan time may exceed interval during heavy sync)")
    print(f"Logfile:    {logfile}")
    print()

    header = f"{'TIME':<19}  {'FILES':>8}  {'PENDING':>8}  {'REMAIN%':>8}  {'ON-DISK':>10}  {'TO-GO':>10}  {'DFILES/min':>12}  {'DBYTES/min':>14}  {'ETA':>10}  {'SCAN':>6}"
    emit(header)

    prev_files = -1
    prev_dataless = -1
    prev_disk = -1
    prev_t = 0.0
    stable_ticks = 0

    while True:
        t0 = time.time()
        total, dataless, apparent, disk = scan(ROOT)
        scan_time = time.time() - t0

        pending = max(apparent - disk, 0)
        remain_pct = pct(dataless, total)

        if prev_t > 0:
            dt = max(time.time() - prev_t, 1.0)
            df = total - prev_files
            dd_disk = disk - prev_disk
            dd_dataless = prev_dataless - dataless
            files_per_min = f"{int(df * 60 / dt):+d}"
            dl_per_min = human(int(dd_disk * 60 / dt))
            if dd_dataless > 0 and dataless > 0:
                eta = fmt_eta(dataless * dt / dd_dataless)
            elif dataless == 0:
                eta = "--"
            else:
                eta = "?"
            if dataless == 0 and dd_disk == 0:
                stable_ticks += 1
            else:
                stable_ticks = 0
        else:
            files_per_min = "--"
            dl_per_min = "--"
            eta = "--"

        line = (
            f"{time.strftime('%Y-%m-%d %H:%M:%S'):<19}  "
            f"{total:>8,}  {dataless:>8,}  {remain_pct:>7.1f}%  "
            f"{human(disk):>10}  {human(pending):>10}  "
            f"{files_per_min:>12}  {dl_per_min:>14}  {eta:>10}  {scan_time:>5.1f}s"
        )
        emit(line)

        if stable_ticks >= 2:
            emit("")
            emit(f">>> READY: 0 placeholders and on-disk size stable for {stable_ticks} ticks. Safe to open Obsidian / push git.")
            log.close()
            return 0

        prev_files = total
        prev_dataless = dataless
        prev_disk = disk
        prev_t = time.time()

        # If a single scan already exceeded the interval, sleep is skipped.
        sleep_for = interval - scan_time
        if sleep_for > 0:
            time.sleep(sleep_for)


if __name__ == "__main__":
    sys.exit(main())
