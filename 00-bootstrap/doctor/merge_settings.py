#!/usr/bin/env python3
"""merge_settings.py <fragment.json> <target.json>
Deep-merge fragment into target. Dicts merge recursively; list items append only if
not already present (exact match); existing scalars ALWAYS win (never override the
user's values). Aborts without writing on any parse error. Backs up, writes atomically.
Exit 0 = a merge was written; 3 = no-op (nothing changed); other nonzero = aborted,
target untouched.

0 and 3 MUST stay distinct: the caller only invokes this when the registration guard
has already failed, so "no change made" means the merge could not fix the problem
(e.g. `hooks` is a list or scalar rather than a dict, so merge() falls through). The
old contract collapsed both into 0, and the doctor reported a REPAIRED it never did."""
import json, os, shutil, sys, tempfile, time


def merge(dst, src):
    if isinstance(dst, dict) and isinstance(src, dict):
        for k, v in src.items():
            dst[k] = merge(dst[k], v) if k in dst else v
        return dst
    if isinstance(dst, list) and isinstance(src, list):
        for item in src:
            if item not in dst:
                dst.append(item)
        return dst
    return dst


def main():
    frag_path, target_path = sys.argv[1], sys.argv[2]
    with open(frag_path) as f:
        frag = json.load(f)                       # bad fragment -> abort
    target = {}
    if os.path.exists(target_path):
        with open(target_path) as f:
            target = json.load(f)                 # bad target -> abort, never clobber
    before = json.dumps(target, sort_keys=True)
    merged = merge(target, frag)
    if json.dumps(merged, sort_keys=True) == before:
        sys.exit(3)                               # no-op -> caller must not claim success
    if os.path.exists(target_path):
        shutil.copy2(target_path, f"{target_path}.bak-{time.strftime('%Y%m%d%H%M%S')}")
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(target_path)))
    with os.fdopen(fd, "w") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")
    os.replace(tmp, target_path)


if __name__ == "__main__":
    main()
