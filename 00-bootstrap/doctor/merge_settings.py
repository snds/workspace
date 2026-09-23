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
old contract collapsed both into 0, and the doctor reported a REPAIRED it never did.

Explicit-replace mode (H24; used by the human-run installers, never by the unattended
doctor):

  merge_settings.py --replace-managed env,hooks [--no-backup] [--dry-run] <fragment> <target>

For each named key the target's MANAGED part is replaced by the fragment's:
  env    installed keys matching GIT_CONFIG_*, GIT_AUTHOR_*, GIT_COMMITTER_*, WS_* or
         GH_CONFIG_DIR are removed, then the fragment's env is inserted (`~/` expanded).
         Every other env key is kept.
  hooks  only managed entries are replaced: commands containing /.claude/hooks/workspace-
         or ws-hook. Every other hook entry is kept.
  other  the whole key is replaced by the fragment's value (or removed when absent).
Same exit codes as legacy mode (0 written, 3 no-op, other = aborted). --no-backup skips
the legacy `.bak-<ts>` copy (the installer takes its own `.ws-bak.<UTC>` backup).
--dry-run writes nothing and prints the changed key names; 0 = would change, 3 = in sync.
`--no-backup` alone keeps the legacy merge semantics without the backup copy."""
import copy
import json
import os
import shutil
import sys
import tempfile
import time

MANAGED_ENV_PREFIXES = ("GIT_CONFIG_", "GIT_AUTHOR_", "GIT_COMMITTER_", "WS_")
MANAGED_ENV_NAMES = ("GH_CONFIG_DIR",)
MANAGED_HOOK_MARKERS = ("/.claude/hooks/workspace-", "ws-hook")


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


def expand_env_home(frag, home=None):
    """Settings `env` values reach processes verbatim (no shell), and tools such as gh do
    not expand `~` in GH_CONFIG_DIR. Render a leading `~/` to this machine's home so one
    tracked fragment works on every device. `home` is a test/installer seam; the default
    is the process's own home (legacy behaviour)."""
    env = frag.get("env")
    if isinstance(env, dict):
        for k, v in env.items():
            if isinstance(v, str) and v.startswith("~/"):
                env[k] = os.path.join(str(home), v[2:]) if home else os.path.expanduser(v)
    return frag


def expand_home_strings(obj, home):
    """Return (obj, changed): every string value starting with `~/` rendered under
    `home`. Used for whole-file JSON installs; tracked files keep `~/`."""
    if isinstance(obj, dict):
        changed = False
        out = {}
        for k, v in obj.items():
            out[k], c = expand_home_strings(v, home)
            changed = changed or c
        return out, changed
    if isinstance(obj, list):
        changed = False
        out = []
        for v in obj:
            nv, c = expand_home_strings(v, home)
            out.append(nv)
            changed = changed or c
        return out, changed
    if isinstance(obj, str) and obj.startswith("~/"):
        return os.path.join(str(home), obj[2:]), True
    return obj, False


def is_managed_env(key):
    return key in MANAGED_ENV_NAMES or key.startswith(MANAGED_ENV_PREFIXES)


def is_managed_command(cmd, markers=MANAGED_HOOK_MARKERS):
    return isinstance(cmd, str) and any(m in cmd for m in markers)


def _strip_managed_groups(groups, markers):
    kept = []
    for g in groups if isinstance(groups, list) else []:
        if isinstance(g, dict) and isinstance(g.get("hooks"), list):
            inner = [h for h in g["hooks"]
                     if not (isinstance(h, dict) and is_managed_command(h.get("command"), markers))]
            if inner:
                g2 = dict(g)
                g2["hooks"] = inner
                kept.append(g2)
        elif isinstance(g, dict) and is_managed_command(g.get("command"), markers):
            continue
        else:
            kept.append(g)
    return kept


def replace_managed(target, frag, keys, markers=MANAGED_HOOK_MARKERS):
    """Pure function: the target with the managed part of each key replaced."""
    out = copy.deepcopy(target)
    for key in keys:
        if key == "env":
            base = out.get("env") if isinstance(out.get("env"), dict) else {}
            new = {k: v for k, v in base.items() if not is_managed_env(k)}
            fenv = frag.get("env") if isinstance(frag.get("env"), dict) else {}
            new.update(copy.deepcopy(fenv))
            if new or "env" in out:
                out["env"] = new
        elif key == "hooks":
            cur = out.get("hooks", {})
            if not isinstance(cur, dict):
                raise ValueError("target `hooks` is not an object")
            fh = frag.get("hooks") if isinstance(frag.get("hooks"), dict) else {}
            new = {}
            for ev, groups in cur.items():
                kept = _strip_managed_groups(groups, markers)
                if kept or ev in fh:
                    new[ev] = kept
            for ev, groups in fh.items():
                new.setdefault(ev, [])
                new[ev].extend(copy.deepcopy(groups if isinstance(groups, list) else []))
            if new or "hooks" in out:
                out["hooks"] = new
        else:
            if key in frag:
                out[key] = copy.deepcopy(frag[key])
            else:
                out.pop(key, None)
    return out


def merge_hook_entries(target, frag):
    """Additive merge for whole-file hook registries (e.g. Cursor hooks.json): append each
    fragment entry whose command is not already registered for that event; remove nothing.
    Top-level keys absent from the target are copied from the fragment."""
    out = copy.deepcopy(target) if isinstance(target, dict) else {}
    for k, v in frag.items():
        if k != "hooks" and k not in out:
            out[k] = copy.deepcopy(v)
    hooks = out.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError("target `hooks` is not an object")
    for ev, entries in (frag.get("hooks") or {}).items():
        cur = hooks.setdefault(ev, [])
        have = {json.dumps(e, sort_keys=True) for e in cur}
        cmds = {e.get("command") for e in cur if isinstance(e, dict)}
        for e in entries if isinstance(entries, list) else []:
            if json.dumps(e, sort_keys=True) in have:
                continue
            if isinstance(e, dict) and e.get("command") and e.get("command") in cmds:
                continue
            cur.append(copy.deepcopy(e))
    return out


def dump(obj):
    """The one serializer for settings files this module writes."""
    return json.dumps(obj, indent=2) + "\n"


def _atomic_write(target_path, text):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(target_path)))
    with os.fdopen(fd, "w") as f:
        f.write(text)
    os.replace(tmp, target_path)


def _changed_names(before, after, keys):
    names = []
    for key in keys:
        b, a = before.get(key), after.get(key)
        if key == "env" and isinstance(a, dict):
            b = b if isinstance(b, dict) else {}
            for k in sorted(set(b) | set(a)):
                if b.get(k) != a.get(k):
                    names.append(f"env.{k}")
        elif json.dumps(b, sort_keys=True) != json.dumps(a, sort_keys=True):
            names.append(key)
    return names


def replace_main(argv):
    keys, no_backup, dry_run, pos = None, False, False, []
    it = iter(argv)
    for a in it:
        if a == "--replace-managed":
            keys = [k for k in next(it, "").split(",") if k]
        elif a.startswith("--replace-managed="):
            keys = [k for k in a.split("=", 1)[1].split(",") if k]
        elif a == "--no-backup":
            no_backup = True
        elif a == "--dry-run":
            dry_run = True
        else:
            pos.append(a)
    if not keys or len(pos) != 2:
        print("usage: merge_settings.py --replace-managed KEYS [--no-backup] [--dry-run] "
              "<fragment> <target>", file=sys.stderr)
        return 2
    frag_path, target_path = pos
    try:
        with open(frag_path) as f:
            frag = expand_env_home(json.load(f))
        target = {}
        if os.path.exists(target_path):
            with open(target_path) as f:
                target = json.load(f)
        if not isinstance(target, dict):
            raise ValueError("target is not a JSON object")
        new = replace_managed(target, frag, keys)
    except (OSError, ValueError) as e:
        print(f"merge_settings: aborted: {e}", file=sys.stderr)
        return 1
    if json.dumps(new, sort_keys=True) == json.dumps(target, sort_keys=True):
        return 3
    if dry_run:
        for n in _changed_names(target, new, keys):
            print(f"differs: {n}")
        return 0
    if os.path.exists(target_path) and not no_backup:
        shutil.copy2(target_path, f"{target_path}.bak-{time.strftime('%Y%m%d%H%M%S')}")
    _atomic_write(target_path, dump(new))
    return 0


def main():
    argv = sys.argv[1:]
    if any(a.startswith("--replace-managed") for a in argv):
        sys.exit(replace_main(argv))
    no_backup = "--no-backup" in argv
    if no_backup:
        argv = [a for a in argv if a != "--no-backup"]
    frag_path, target_path = argv[0], argv[1]
    with open(frag_path) as f:
        frag = expand_env_home(json.load(f))      # bad fragment -> abort
    target = {}
    if os.path.exists(target_path):
        with open(target_path) as f:
            target = json.load(f)                 # bad target -> abort, never clobber
    before = json.dumps(target, sort_keys=True)
    merged = merge(target, frag)
    if json.dumps(merged, sort_keys=True) == before:
        sys.exit(3)                               # no-op -> caller must not claim success
    if os.path.exists(target_path) and not no_backup:
        shutil.copy2(target_path, f"{target_path}.bak-{time.strftime('%Y%m%d%H%M%S')}")
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(target_path)))
    with os.fdopen(fd, "w") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")
    os.replace(tmp, target_path)


if __name__ == "__main__":
    main()
