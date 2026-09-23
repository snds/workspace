#!/usr/bin/env python3
"""render_shims.py — render every hook registration file from the surface registry (H16).

The registry is `02-shared-references/surfaces.json`. This tool renders the tracked outputs it
declares (Claude settings fragments, Cursor hook files, the snds plugin hooks, the Codex and Cursor
config fragments, the probe registration fragments and the generated SURFACES.md block) and
checks the table's semantics:

  Rule C  every component has a coverage entry on every minimum surface; modes come from the
          enum; every enforced* mode names verified_by refs that resolve.
  Rule R  one effective registration per (hookable surface, event, cwd context, behaviour),
          after host_skip, defers_to and claim_group are applied.
  Also    a project-scope layer never references $HOME or ~, and wrapper sha256 values match.

It never writes outside the repo and never touches an installed copy. Installers (H24) read the
output mapping from `--list --json` only.

Usage:
  render_shims.py --check [--only coverage|outputs|registrations|wrappers] [--pending-ok] [--rev REV] [--json]
  render_shims.py --write [--only OUTPUT_ID]
  render_shims.py --list --json
  render_shims.py --install-state --json
  render_shims.py --verify-canonical REV
  render_shims.py --emit identity-inc --device ID
  render_shims.py --self-test

H17 (T8) adds two emitters. The Claude overlay env inside settings-user-fragment.json is rendered
from context-remotes.json and devices.json (the output row's `overlay` names the layout version;
`owned_keys` stays ["hooks"] so --install-shims never writes the env: only the Sean-run
--install-claude-overlay does). `claude-identity.inc` is rendered from the Claude identity rule, and
`--emit identity-inc --device ID` prints one device's default identity include for --install-identity.

Exit: 0 clean; 1 drift or a violation; 2 data or usage error; 3 --rev has no render_shims.py.
Stdlib only; Python 3.9+.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TABLE_REL = "02-shared-references/surfaces.json"
TEST_VALIDATORS_REL = "09-tools/test-validators.py"
PROBES_REL = "02-shared-references/probes"
FIXTURE_BASE_REL = "09-tools/fixtures/render_shims/base-surfaces.json"

TOP_KEYS = [
    "schema_version", "doc", "coverage_modes", "minimum_surfaces", "components", "families",
    "never_markers", "agent_possible_env", "probe_env_name_prefixes", "probe_env_value_allowlist",
    "surfaces", "formats", "dialects", "layers", "commands", "registrations", "outputs", "wrappers",
]
KINDS = {"cli-agent", "ide-agent", "desktop-app", "cloud-agent", "chat", "browser", "mcp-client", "human"}
DIALECTS = {"claude", "cursor", "codex", "plain", "none"}
CHANNELS = {"claude-settings-env", "codex-shell-environment-policy", "cursor-sessionstart-env", "none"}
INSTALL_MODES = {"tracked", "whole-file", "claude-settings-keys", "merge-hook-entries", "managed-block"}
ANCESTRY_MATCH = {"exact", "prefix"}
RENDERS = {"hooks", "codex-config", "cursor-sandbox", "surfaces-md-block", "identity-inc"}
CWD_CONTEXTS = ("workspace", "other")
CHECK_AREAS = ("coverage", "outputs", "registrations", "wrappers")
TELEMETRY_ROOT = "~/.config/snds-workspace/telemetry"
MD_BEGIN = "<!-- BEGIN GENERATED: surfaces -->"
MD_END = "<!-- END GENERATED: surfaces -->"
REF_RE = re.compile(r"^(probe|fixture|selftest):(.+)$")
PROBE_REF_RE = re.compile(r"^([a-z0-9-]+)@([a-z0-9-]+)$")
CLAUDE_LIKE = {"claude-settings", "codex-hooks"}


class DataError(Exception):
    """The table or a tracked input cannot be read or is structurally unusable."""


def canonical(obj) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def load_table(root: Path = ROOT) -> dict:
    path = Path(root) / TABLE_REL
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DataError(f"table missing: {TABLE_REL}") from exc
    except (OSError, ValueError) as exc:
        raise DataError(f"table unreadable: {TABLE_REL}: {exc}") from exc
    if not isinstance(data, dict):
        raise DataError(f"{TABLE_REL} is not a JSON object")
    return data


# --------------------------------------------------------------------------- table shape

def check_table(t: dict) -> list:
    errors = []
    keys = list(t.keys())
    unknown = [k for k in keys if k not in TOP_KEYS]
    missing = [k for k in TOP_KEYS if k not in t]
    if unknown:
        errors.append(f"table: unknown top-level key(s): {', '.join(unknown)}")
    if missing:
        errors.append(f"table: missing top-level key(s): {', '.join(missing)}")
    if t.get("schema_version") != 1:
        errors.append("table: schema_version must be 1")
    families = t.get("families") or {}
    ids = set()
    for s in t.get("surfaces") or []:
        sid = s.get("id")
        if sid in ids:
            errors.append(f"surface {sid}: duplicate id")
        ids.add(sid)
        if s.get("family") not in families:
            errors.append(f"surface {sid}: family {s.get('family')!r} is not a key of families")
        if s.get("kind") not in KINDS:
            errors.append(f"surface {sid}: invalid kind {s.get('kind')!r}")
        if s.get("dialect") not in DIALECTS:
            errors.append(f"surface {sid}: invalid dialect {s.get('dialect')!r}")
        elif s.get("dialect") not in ("none", "plain") and s.get("dialect") not in (t.get("dialects") or {}):
            errors.append(f"surface {sid}: dialect {s.get('dialect')!r} is not declared in dialects")
        if s.get("family_marker_channel") not in CHANNELS:
            errors.append(f"surface {sid}: invalid family_marker_channel")
        for a in (s.get("markers") or {}).get("ancestry") or []:
            if a.get("match") not in ANCESTRY_MATCH:
                errors.append(f"surface {sid}: ancestry match must be exact or prefix")
    for lay in t.get("layers") or []:
        if lay.get("install_mode") not in INSTALL_MODES:
            errors.append(f"layer {lay.get('id')}: invalid install_mode")
        if lay.get("format") not in (t.get("formats") or {}):
            errors.append(f"layer {lay.get('id')}: format {lay.get('format')!r} not in formats")
        for s in lay.get("loaded_by") or []:
            if s not in ids:
                errors.append(f"layer {lay.get('id')}: loaded_by names unknown surface {s}")
    for o in t.get("outputs") or []:
        if o.get("install_mode") not in INSTALL_MODES:
            errors.append(f"output {o.get('id')}: invalid install_mode")
        if o.get("render", "hooks") not in RENDERS:
            errors.append(f"output {o.get('id')}: invalid render {o.get('render')!r}")
        if "overlay" in o and (o.get("overlay") not in OVERLAY_VERSIONS or o.get("render", "hooks") != "hooks"):
            errors.append(f"output {o.get('id')}: overlay must be one of {list(OVERLAY_VERSIONS)} on a hooks output")
        if "env" in (o.get("owned_keys") or []):
            errors.append(f"output {o.get('id')}: env is never an owned (shim-installable) key; "
                          "the overlay is installed only by --install-claude-overlay")
    return errors


# --------------------------------------------------------------------------- Rule C

def _is_git_checkout(root: Path) -> bool:
    return (root / ".git").exists()


def _tracked(root: Path, rel: str) -> bool:
    if not (root / rel).is_file():
        return False
    if not _is_git_checkout(root):
        return True          # an exported tree (git archive) holds tracked files only
    try:
        r = subprocess.run(["git", "ls-files", "--error-unmatch", "--", rel], cwd=root,
                           capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0


def resolve_ref(ref: str, root: Path):
    """Return (resolved: bool, kind or None, reason)."""
    m = REF_RE.match(ref or "")
    if not m:
        return False, None, f"bad verified_by ref {ref!r}"
    kind, body = m.group(1), m.group(2)
    if kind == "probe":
        pm = PROBE_REF_RE.match(body)
        if not pm:
            return False, kind, f"bad probe ref {ref!r}"
        ok = (root / PROBES_REL / f"{body}.json").is_file()
        return ok, kind, "" if ok else f"{ref} does not resolve ({PROBES_REL}/{body}.json missing)"
    if kind == "fixture":
        tv = root / TEST_VALIDATORS_REL
        try:
            text = tv.read_text(encoding="utf-8")
        except OSError:
            text = ""
        ok = re.search(rf"^class {re.escape(body)}\(", text, re.MULTILINE) is not None
        return ok, kind, "" if ok else f"{ref} does not resolve (no class {body} in {TEST_VALIDATORS_REL})"
    ok = _tracked(root, body)
    if ok:
        try:
            ok = "--self-test" in (root / body).read_text(encoding="utf-8", errors="replace")
        except OSError:
            ok = False
    return ok, kind, "" if ok else f"{ref} does not resolve (not a tracked file containing --self-test)"


def check_surface_coverage(t: dict, root: Path = ROOT, pending_ok: bool = False):
    errors, warnings = [], []
    modes = set(t.get("coverage_modes") or [])
    comps = list(t.get("components") or [])
    rows = {s.get("id"): s for s in t.get("surfaces") or []}
    for m in t.get("minimum_surfaces") or []:
        if m not in rows:
            errors.append(f"coverage: minimum surface row missing: {m}")
            continue
        cov = rows[m].get("coverage") or {}
        for c in comps:
            if c not in cov:
                errors.append(f"coverage: {m} has no entry for {c}")
    for sid, s in rows.items():
        for comp, entry in (s.get("coverage") or {}).items():
            where = f"coverage: {sid}.{comp}"
            if comp not in comps:
                errors.append(f"{where}: unknown component")
            mode = entry.get("mode")
            if mode not in modes:
                errors.append(f"{where}: invalid mode {mode!r}")
                continue
            for ref in entry.get("planned_verified_by") or []:
                if not REF_RE.match(ref):
                    errors.append(f"{where}: bad planned_verified_by ref {ref!r}")
            if not mode.startswith("enforced"):
                continue
            refs = entry.get("verified_by") or []
            if not refs:
                errors.append(f"{where}: {mode} with no verified_by")
                continue
            for ref in refs:
                ok, kind, reason = resolve_ref(ref, root)
                if ok:
                    continue
                if pending_ok and kind in ("fixture", "selftest"):
                    warnings.append(f"{where}: pending: {reason}")
                else:
                    errors.append(f"{where}: {reason}")
    return errors, warnings


# --------------------------------------------------------------------------- Rule R

def _behaviour(t: dict, reg: dict):
    cmd = (t.get("commands") or {}).get(reg.get("command")) or {}
    if "behaviour" in cmd:
        return cmd["behaviour"]
    return (cmd.get("behaviour_by_event") or {}).get(reg.get("event"))


def command_text(t: dict, reg: dict) -> str:
    cmd = (t.get("commands") or {}).get(reg.get("command"))
    if cmd is None:
        raise DataError(f"registration {reg.get('id')}: unknown command {reg.get('command')!r}")
    return cmd["template"].replace("{event}", reg["event"])


def _references_home(text: str) -> bool:
    return "$HOME" in text or "${HOME" in text or "~" in text


def check_registrations(t: dict, pending_ok: bool = False):
    errors, warnings = [], []
    layers = {lay.get("id"): lay for lay in t.get("layers") or []}
    commands = t.get("commands") or {}
    formats = t.get("formats") or {}
    regs = t.get("registrations") or []
    ids = [r.get("id") for r in regs]
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        errors.append(f"registrations: duplicate id {dup}")
    for r in regs:
        rid = r.get("id")
        lay = layers.get(r.get("layer"))
        cmd = commands.get(r.get("command"))
        if lay is None:
            errors.append(f"registration {rid}: unknown layer {r.get('layer')!r}")
            continue
        if cmd is None:
            errors.append(f"registration {rid}: unknown command {r.get('command')!r}")
            continue
        if r.get("event") not in (formats.get(lay.get("format")) or {}):
            errors.append(f"registration {rid}: event {r.get('event')!r} not mapped by format {lay.get('format')}")
        if _behaviour(t, r) is None:
            errors.append(f"registration {rid}: command {r.get('command')} declares no behaviour for {r.get('event')}")
        impl = set(cmd.get("implements") or [])
        if r.get("host_skip") and "host_filter" not in impl:
            errors.append(f"registration {rid}: host_skip on command {r.get('command')} that does not implement host_filter")
        if r.get("defers_to"):
            if r["defers_to"] not in ids:
                errors.append(f"registration {rid}: defers_to unknown registration {r['defers_to']}")
            if "defer_in_workspace" not in impl:
                errors.append(f"registration {rid}: defers_to on command {r.get('command')} that does not implement defer_in_workspace")
        if r.get("claim_group") and "claim" not in impl:
            errors.append(f"registration {rid}: claim_group on command {r.get('command')} that does not implement claim")
        if lay.get("scope") == "project" and _references_home(cmd.get("template", "")):
            errors.append(f"registration {rid}: project-scope layer {lay.get('id')} references $HOME or ~")
        if r.get("pending") and not pending_ok:
            errors.append(f"registration {rid}: pending change not applied ({r['pending']})")
    if errors:
        return errors, warnings
    for (sid, event, ctx, beh), group in sorted(effective_violations(t).items()):
        names = ", ".join(r["id"] for r in group)
        surplus_pending = sum(1 for r in group if r.get("pending"))
        msg = f"rule R: {sid} {event} ({ctx}) behaviour {beh} has {len(group)} effective registrations: {names}"
        if pending_ok and surplus_pending >= len(group) - 1:
            warnings.append(f"pending: {msg}")
        else:
            errors.append(msg)
    return errors, warnings


def effective_set(t: dict, sid: str, event: str, ctx: str) -> list:
    layers = {lay["id"]: lay for lay in t.get("layers") or []}
    formats = t.get("formats") or {}
    cand = []
    for r in t.get("registrations") or []:
        lay = layers.get(r.get("layer"))
        if lay is None or r.get("event") != event:
            continue
        if sid not in (lay.get("loaded_by") or []) or ctx not in (lay.get("cwd_context") or []):
            continue
        if event not in (formats.get(lay.get("format")) or {}):
            continue
        cand.append(r)
    cand = [r for r in cand if sid not in (r.get("host_skip") or [])]
    present = {r["id"] for r in cand}
    cand = [r for r in cand if not (r.get("defers_to") and r["defers_to"] in present)]
    seen, out = set(), []
    for r in cand:
        g = r.get("claim_group")
        if g:
            if g in seen:
                continue
            seen.add(g)
        out.append(r)
    return out


def effective_violations(t: dict) -> dict:
    events = []
    for fmt in (t.get("formats") or {}).values():
        for e in fmt:
            if e not in events:
                events.append(e)
    found = {}
    for s in t.get("surfaces") or []:
        if not s.get("hookable"):
            continue
        for ctx in CWD_CONTEXTS:
            for e in events:
                by_beh = OrderedDict()
                for r in effective_set(t, s["id"], e, ctx):
                    by_beh.setdefault(_behaviour(t, r), []).append(r)
                for beh, group in by_beh.items():
                    if len(group) > 1:
                        found[(s["id"], e, ctx, beh)] = group
    return found


# --------------------------------------------------------------------------- rendering

def _layer(t: dict, lid: str) -> dict:
    for lay in t.get("layers") or []:
        if lay.get("id") == lid:
            return lay
    raise DataError(f"unknown layer {lid!r}")


def render_hooks(t: dict, lid: str) -> dict:
    lay = _layer(t, lid)
    fmt_name = lay["format"]
    fmt = (t.get("formats") or {}).get(fmt_name)
    if fmt is None:
        raise DataError(f"layer {lid}: unknown format {fmt_name}")
    hooks = OrderedDict()
    for r in t.get("registrations") or []:
        if r.get("layer") != lid:
            continue
        if r["event"] not in fmt:
            raise DataError(f"registration {r['id']}: event {r['event']} not in format {fmt_name}")
        name = fmt[r["event"]]
        cmd = command_text(t, r)
        if fmt_name in CLAUDE_LIKE:
            entry = OrderedDict([("type", "command"), ("command", cmd)])
            if r.get("timeout") is not None:
                entry["timeout"] = r["timeout"]
            group = OrderedDict()
            if r.get("matcher") is not None:
                group["matcher"] = r["matcher"]
            group["hooks"] = [entry]
            hooks.setdefault(name, []).append(group)
        elif fmt_name == "cursor-hooks":
            entry = OrderedDict([("command", cmd)])
            if r.get("matcher") is not None:
                entry["matcher"] = r["matcher"]
            if r.get("timeout") is not None:
                entry["timeout"] = r["timeout"]
            hooks.setdefault(name, []).append(entry)
        else:
            raise DataError(f"layer {lid}: no renderer for format {fmt_name}")
    return hooks


def _render_hooks_output(t: dict, out: dict, root: Path) -> str:
    lay = _layer(t, out["layer"])
    if lay.get("output") != out["path"]:
        raise DataError(f"output {out['id']}: path differs from layer {lay['id']} output")
    hooks = render_hooks(t, lay["id"])
    fmt_name = lay["format"]
    keyed = (fmt_name == "claude-settings" and out.get("owned_keys") == ["hooks"]
             and out.get("install_mode") in ("claude-settings-keys", "tracked"))
    if keyed:
        path = root / out["path"]
        try:
            base = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=OrderedDict)
        except FileNotFoundError:
            base = OrderedDict()
        except (OSError, ValueError) as exc:
            raise DataError(f"output {out['id']}: base file unreadable: {exc}") from exc
        base["hooks"] = hooks
        if out.get("overlay"):
            cr, dev = identity_tables(root)
            base["env"] = overlay_env(cr, dev, out["overlay"])
        return canonical(base)
    if fmt_name == "cursor-hooks":
        return canonical(OrderedDict([("version", 1), ("hooks", hooks)]))
    return canonical(OrderedDict([("hooks", hooks)]))


def _render_codex_config(t: dict) -> str:
    lines = [
        "# snds-workspace managed block. Rendered by 00-bootstrap/doctor/render_shims.py from",
        "# 02-shared-references/surfaces.json; do not edit by hand. The installer expands ~/ and",
        "# replaces only the lines between BEGIN and END in ~/.codex/config.toml.",
        "# BEGIN snds-workspace",
    ]
    for s in t.get("surfaces") or []:
        if s.get("family_marker_channel") != "codex-shell-environment-policy":
            continue
        lines += ["[shell_environment_policy.set]", f'WS_SURFACE_FAMILY = "{s["family"]}"', ""]
        sb = s.get("sandbox") or {}
        if sb.get("write_root_key"):
            lines += ["[sandbox_workspace_write]", f'{sb["write_root_key"]} = ["{TELEMETRY_ROOT}"]']
        break
    lines.append("# END snds-workspace")
    return "\n".join(lines) + "\n"


def _render_cursor_sandbox(t: dict) -> str:
    for s in t.get("surfaces") or []:
        sb = s.get("sandbox") or {}
        if s.get("id") == "cursor" and sb.get("write_root_key"):
            return canonical(OrderedDict([(sb["write_root_key"], [TELEMETRY_ROOT])]))
    raise DataError("cursor row has no sandbox.write_root_key")


# --------------------------------------------------------------------------- H17 overlay (T8)

OVERLAY_VERSIONS = ("v4", "v5")
OVERLAY_INCLUDE = "~/.config/snds-workspace/git/claude-identity.inc"
OVERLAY_GH_DIR = "~/.config/snds-workspace/gh-claude"
FLOOR_HOOK = "ws-claude-wall"
# git appends "$@" to a config hook command itself, so the command never carries it. The guard
# makes a missing pin (no bin/ws-hook) a no-op instead of a failed commit. The installer renders the
# leading `H="$HOME";` as the absolute install home (merge_settings.expand_env_home), and the command
# re-sets HOME and drops the PYTHON* startup variables, so a caller's HOME= or PYTHONPATH= cannot
# route the wrapper or the pinned lib elsewhere.
FLOOR_COMMAND = ('H="$HOME"; W="$H/.config/snds-workspace/bin/ws-hook"; [ -x "$W" ] || exit 0; '
                 'exec env -u PYTHONPATH -u PYTHONHOME -u PYTHONSTARTUP -u PYTHONINSPECT -u PYTHONUSERBASE '
                 'HOME="$H" "$W" --host git --floor claude')
FLOOR_EVENTS = ("pre-commit", "commit-msg", "pre-merge-commit", "pre-push")
CASE_VARIANTS = ("declared", "lower", "upper", "capitalized")
# The v4 employer layout (per host), kept only so the emitter can prove it reproduces the
# installed v4 bytes from the tables before the data moves to v5.
_V4_EMPLOYER_FORMS = {"github.com": ("scp-alias", "scp", "https"), "bitbucket.org": ("scp", "https", "ssh")}
IDENTITY_INC_HEADER = (
    "# Claude surfaces are personal-only (06-context/memory/feedback-credential-scoping.md).\n"
    "# Included ONLY for repos whose remote is an snds/* URL (includeIf hasconfig in the\n"
    "# Claude env overlay). Never included in employer repos. No remote URLs in this file\n"
    "# (git forbids them inside hasconfig includes).\n"
)


def _pr_module():
    """The vault profile_resolve (one home for table loading), imported lazily."""
    tools = str(ROOT / "09-tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    try:
        import profile_resolve  # noqa: PLC0415 - lazy by contract (3d)
    except (ImportError, OSError, ValueError) as exc:
        raise DataError(f"profile_resolve unavailable ({exc.__class__.__name__})") from exc
    return profile_resolve


def identity_tables(root: Path = ROOT):
    """(context-remotes, devices) through profile_resolve.load_table; DataError when unusable."""
    pr = _pr_module()
    try:
        return pr.load_table("context-remotes", root=root), pr.load_table("devices", root=root)
    except (pr.TableError, OSError) as exc:
        raise DataError(f"identity tables: {exc}") from exc


def _case_variants(owner: str) -> list:
    out = []
    for c in CASE_VARIANTS:
        v = {"declared": owner, "lower": owner.lower(), "upper": owner.upper(),
             "capitalized": owner[:1].upper() + owner[1:].lower()}[c]
        if v not in out:
            out.append(v)
    return out


def _host_facts(cr: dict, dev: dict, host: str):
    row = next((h for h in cr.get("hosts") or [] if str(h.get("host", "")).lower() == host.lower()), None)
    if row is None:
        raise DataError(f"context-remotes: owner host {host!r} has no hosts[] row")
    aliases = [a["alias"] for a in dev.get("ssh_aliases") or []
               if str(a.get("host", "")).lower() == host.lower() and a.get("alias")]
    return row.get("ssh_user") or "git", list(row.get("forms") or []), aliases


def _employer_prefixes(owner: str, host: str, user: str, forms: list, aliases: list, accounts: list,
                       version: str) -> list:
    def tmpl(form: str) -> list:
        v5 = version != "v4"
        if form == "scp":
            return [f"{user}@{host}:{{o}}/"] + ([f"{user}@{host}:/{{o}}/"] if v5 else [])
        if form == "scp-alias":
            return ([f"{user}@{a}:{{o}}/" for a in aliases] if not v5
                    else [x for a in aliases for x in (f"{user}@{a}:{{o}}/", f"{a}:{{o}}/", f"ssh://{user}@{a}/{{o}}/",
                                                       f"ssh://{a}/{{o}}/")])
        if form == "ssh":
            if not v5:
                return [f"ssh://{user}@{host}/{{o}}/"]
            extra = [f"ssh://{user}@ssh.{host}:443/{{o}}/"] if host == "github.com" else []
            return [f"ssh://{user}@{host}/{{o}}/", f"ssh://{user}@{host}:22/{{o}}/", f"ssh://{host}/{{o}}/"] + extra
        if form == "https":
            return [f"https://{host}/{{o}}/"] + ([f"https://{host}:443/{{o}}/", f"https://www.{host}/{{o}}/"] if v5 else [])
        if form == "https-userinfo":
            return [f"https://{acct}@{host}/{{o}}/" for acct in accounts]
        return []
    if version == "v4":
        order = [f for f in _V4_EMPLOYER_FORMS.get(host, ("scp", "https", "ssh")) if f in forms]
        return [t.format(o=owner) for f in order for t in tmpl(f)]
    order = [f for f in ("scp", "scp-alias", "ssh", "https", "https-userinfo") if f in forms]
    out = []
    for f in order:
        for t in tmpl(f):
            for o in _case_variants(owner):
                v = t.format(o=o)
                if v not in out:
                    out.append(v)
    return out


def overlay_pairs(cr: dict, dev: dict, version: str = "v5") -> list:
    """The overlay's GIT_CONFIG (key, value) pairs, in the H17 order:
    personal hasconfig includes; personal https insteadOf; credential helper reset; the employer
    transport block; (v5) the guarded Claude floor hook."""
    if version not in OVERLAY_VERSIONS:
        raise DataError(f"unknown overlay version {version!r}")
    blocked = cr.get("blocked_scheme")
    if not isinstance(blocked, str) or not blocked:
        raise DataError("context-remotes: blocked_scheme missing")
    owners = [o for o in cr.get("owners") or [] if isinstance(o, dict)]
    personal = [o for o in owners if o.get("class") == "personal"]
    employer = [o for o in owners if o.get("class") == "employer"]
    pairs = []
    for o in personal:
        user, forms, aliases = _host_facts(cr, dev, o["host"])
        h, n = o["host"], o["owner"]
        pats = []
        if "scp" in forms:
            pats.append(f"{user}@{h}:{n}/**")
        if "scp-alias" in forms:
            pats += [f"{user}@{a}:{n}/**" for a in aliases]
        if "https" in forms:
            pats.append(f"https://{h}/{n}/**")
        if "ssh" in forms:
            pats.append(f"ssh://{user}@{h}/{n}/**")
        pairs += [(f"includeIf.hasconfig:remote.*.url:{p}.path", OVERLAY_INCLUDE) for p in pats]
    for o in personal:
        user, forms, aliases = _host_facts(cr, dev, o["host"])
        h, n = o["host"], o["owner"]
        srcs = []
        if "scp-alias" in forms:
            srcs += [f"{user}@{a}:{n}/" for a in aliases]
        if "scp" in forms:
            srcs.append(f"{user}@{h}:{n}/")
        if "ssh" in forms:
            srcs.append(f"ssh://{user}@{h}/{n}/")
        pairs += [(f"url.https://{h}/{n}/.insteadOf", s) for s in srcs]
    hosts_seen = []
    for o in personal:
        if o["host"] not in hosts_seen:
            hosts_seen.append(o["host"])
    for h in hosts_seen:
        pairs += [(f"credential.https://{h}.helper", ""), (f"credential.https://{h}.helper", "!gh auth git-credential")]
    accounts = []
    for ident in dev.get("identities") or []:
        for acct in ident.get("accounts") or []:
            if acct not in accounts:
                accounts.append(acct)
    if "git" not in accounts:
        accounts.append("git")
    seen = set()
    for o in employer:
        user, forms, aliases = _host_facts(cr, dev, o["host"])
        for pre in _employer_prefixes(o["owner"], o["host"], user, forms, aliases, accounts, version):
            if pre not in seen:
                seen.add(pre)
                pairs.append((f"url.{blocked}.insteadOf", pre))
    if version != "v4":
        pairs.append((f"hook.{FLOOR_HOOK}.command", FLOOR_COMMAND))
        pairs += [(f"hook.{FLOOR_HOOK}.event", e) for e in FLOOR_EVENTS]
        pairs.append((f"hook.{FLOOR_HOOK}.enabled", "true"))
    return pairs


def overlay_env(cr: dict, dev: dict, version: str = "v5") -> "OrderedDict":
    """The settings `env` block: markers, the gh belt, then GIT_CONFIG_COUNT/KEY/VALUE pairs.
    No GIT_AUTHOR_* or GIT_COMMITTER_* key, ever: identity comes only from the hasconfig include."""
    pairs = overlay_pairs(cr, dev, version)
    env = OrderedDict([("WS_CLAUDE_OVERLAY", version)])
    if version != "v4":
        env["WS_SURFACE_FAMILY"] = "claude"
    env["GH_CONFIG_DIR"] = OVERLAY_GH_DIR
    env["GIT_CONFIG_COUNT"] = str(len(pairs))
    for i, (k, v) in enumerate(pairs):
        env[f"GIT_CONFIG_KEY_{i}"] = k
        env[f"GIT_CONFIG_VALUE_{i}"] = v
    return env


def _identity_row(dev: dict, iid: str) -> dict:
    row = next((r for r in dev.get("identities") or [] if isinstance(r, dict) and r.get("id") == iid), None)
    if row is None:
        raise DataError(f"devices: identity {iid!r} is not declared")
    return row


def claude_identity_id(dev: dict) -> str:
    """The identity of the Claude-family rule (IR1: claude -> the personal identity on every device)."""
    for r in dev.get("identity_rules") or []:
        if isinstance(r, dict) and r.get("family") == "claude" and r.get("device") == "*":
            return str(r.get("identity"))
    raise DataError("devices: no identity rule for the claude family on every device")


def _user_block(row: dict) -> str:
    return f"[user]\n\tname = {row['name']}\n\temail = {row['email']}\n"


def render_claude_identity_inc(dev: dict) -> str:
    row = _identity_row(dev, claude_identity_id(dev))
    if row.get("class") != "personal":
        raise DataError("the Claude identity must be a personal identity")
    return IDENTITY_INC_HEADER + _user_block(row)


def device_identity_id(dev: dict, device_id: str):
    """The device default for non-Claude families: the first family-* rule for the device, else
    the device row's default_identity. None for an unknown device (most restrictive: no default)."""
    for r in dev.get("identity_rules") or []:
        if isinstance(r, dict) and r.get("family") == "*" and r.get("device") == device_id:
            return r.get("identity")
    row = next((d for d in dev.get("devices") or [] if isinstance(d, dict) and d.get("id") == device_id), None)
    return (row or {}).get("default_identity")


def render_device_identity_inc(dev: dict, device_id: str):
    iid = device_identity_id(dev, device_id)
    if not iid:
        return None
    row = _identity_row(dev, iid)
    return (f"# snds-workspace device identity for {device_id} (render_shims.py --emit identity-inc).\n"
            "# Non-Claude surfaces and humans on this device commit as this identity unless a repo sets\n"
            "# its own. Claude surfaces never use it: their identity comes from claude-identity.inc.\n"
            + _user_block(row))


def _render_identity_inc(out: dict, root: Path) -> str:
    _cr, dev = identity_tables(root)
    return render_claude_identity_inc(dev)


def _yn(v) -> str:
    return "yes" if v else "no"


def render_md_block(t: dict) -> str:
    lines = [
        MD_BEGIN,
        "_Generated by `00-bootstrap/doctor/render_shims.py` from `02-shared-references/surfaces.json`;"
        " run `render_shims.py --write` after editing the table. Do not edit this block by hand._",
        "",
        "| Surface | Family | Kind | Hookable | Dialect | Required |",
        "|---|---|---|---|---|---|",
    ]
    for s in t.get("surfaces") or []:
        lines.append(f"| {s['id']} | {s['family']} | {s['kind']} | {_yn(s.get('hookable'))} | "
                     f"{s.get('dialect')} | {_yn(s.get('required'))} |")
    mins = list(t.get("minimum_surfaces") or [])
    rows = {s["id"]: s for s in t.get("surfaces") or []}
    lines += ["", "Coverage on the minimum surfaces:", "",
              "| Component | " + " | ".join(mins) + " |",
              "|---|" + "---|" * len(mins)]
    for c in t.get("components") or []:
        cells = [((rows.get(m) or {}).get("coverage") or {}).get(c, {}).get("mode", "-") for m in mins]
        lines.append(f"| {c} | " + " | ".join(cells) + " |")
    lines += ["", "Registrations (one effective registration per surface, event and behaviour):", "",
              "| Registration | Event | Command | Host skip | Claim group |", "|---|---|---|---|---|"]
    for r in t.get("registrations") or []:
        lines.append(f"| {r['id']} | {r['event']} | {r['command']} | "
                     f"{', '.join(r.get('host_skip') or []) or '-'} | {r.get('claim_group') or '-'} |")
    lines += ["", "Rendered outputs (installers read this mapping from `render_shims.py --list --json`; an "
              "`overlay` output also renders the Claude overlay env, which only `--install-claude-overlay` installs):",
              "", "| Output | Path | Install mode | Installs to | Overlay |", "|---|---|---|---|---|"]
    for o in t.get("outputs") or []:
        lines.append(f"| {o.get('id')} | `{o.get('path')}` | {o.get('install_mode')} | "
                     f"{('`' + o['install_path'] + '`') if o.get('install_path') else '-'} | {o.get('overlay') or '-'} |")
    lines.append(MD_END)
    return "\n".join(lines) + "\n"


def _splice_md(current: str, block: str) -> str:
    b = current.find(MD_BEGIN)
    e = current.find(MD_END)
    if b < 0 or e < 0 or e < b:
        raise DataError("SURFACES.md generated-block markers are missing")
    end = e + len(MD_END)
    if current[end:end + 1] == "\n":
        end += 1
    return current[:b] + block + current[end:]


def render_output(t: dict, out: dict, root: Path = ROOT) -> str:
    kind = out.get("render", "hooks")
    if kind == "hooks":
        return _render_hooks_output(t, out, root)
    if kind == "codex-config":
        return _render_codex_config(t)
    if kind == "cursor-sandbox":
        return _render_cursor_sandbox(t)
    if kind == "identity-inc":
        return _render_identity_inc(out, root)
    if kind == "surfaces-md-block":
        try:
            current = (root / out["path"]).read_text(encoding="utf-8")
        except OSError as exc:
            raise DataError(f"output {out['id']}: {exc}") from exc
        return _splice_md(current, render_md_block(t))
    raise DataError(f"output {out.get('id')}: unknown render {kind!r}")


def _inside(root: Path, rel: str) -> Path:
    p = (root / rel).resolve()
    r = root.resolve()
    if p != r and r not in p.parents:
        raise DataError(f"output path escapes the repo: {rel}")
    return p


def check_outputs(t: dict, root: Path = ROOT, only_id=None) -> list:
    errors = []
    for out in t.get("outputs") or []:
        if only_id and out.get("id") != only_id:
            continue
        rendered = render_output(t, out, root)
        path = _inside(root, out["path"])
        try:
            current = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            errors.append(f"outputs: {out['id']}: missing tracked output {out['path']}")
            continue
        if current != rendered:
            errors.append(f"outputs: {out['id']}: drift in {out['path']} (run render_shims.py --write)")
    return errors


def check_wrappers(t: dict, root: Path = ROOT) -> list:
    errors = []
    for rel, spec in (t.get("wrappers") or {}).items():
        path = root / rel
        try:
            data = path.read_bytes()
        except OSError:
            errors.append(f"wrappers: {rel} missing")
            continue
        got = hashlib.sha256(data).hexdigest()
        if got != (spec or {}).get("sha256"):
            errors.append(f"wrappers: {rel} sha256 mismatch (table {(spec or {}).get('sha256')}, file {got})")
        if not os.access(path, os.X_OK):
            errors.append(f"wrappers: {rel} is not executable")
    return errors


def check(root: Path = ROOT, only=None, pending_ok: bool = False) -> dict:
    root = Path(root)
    areas = set(only or CHECK_AREAS)
    errors, warnings = [], []
    try:
        t = load_table(root)
    except DataError as exc:
        return {"errors": [str(exc)], "warnings": [], "data_error": True}
    errors += check_table(t)
    if errors:
        return {"errors": errors, "warnings": warnings, "data_error": False}
    try:
        if "coverage" in areas:
            e, w = check_surface_coverage(t, root, pending_ok)
            errors += e
            warnings += w
        if "registrations" in areas:
            e, w = check_registrations(t, pending_ok)
            errors += e
            warnings += w
        if "outputs" in areas:
            errors += check_outputs(t, root)
        if "wrappers" in areas:
            errors += check_wrappers(t, root)
    except DataError as exc:
        return {"errors": errors + [str(exc)], "warnings": warnings, "data_error": True}
    return {"errors": errors, "warnings": warnings, "data_error": False}


def write(root: Path = ROOT, only_id=None) -> list:
    root = Path(root)
    t = load_table(root)
    problems = check_table(t)
    if problems:
        raise DataError("; ".join(problems))
    written = []
    for out in t.get("outputs") or []:
        if only_id and out.get("id") != only_id:
            continue
        rendered = render_output(t, out, root)
        path = _inside(root, out["path"])
        try:
            current = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            current = None
        if current == rendered:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".render-tmp")
        tmp.write_text(rendered, encoding="utf-8")
        if current is not None:
            shutil.copymode(path, tmp)
        os.replace(tmp, path)
        written.append(out["path"])
    return written


def list_outputs(t: dict) -> list:
    return [OrderedDict([("id", o.get("id")), ("path", o.get("path")), ("layer", o.get("layer")),
                         ("install_path", o.get("install_path")), ("install_mode", o.get("install_mode")),
                         ("surface", o.get("surface")), ("probe", bool(o.get("probe"))),
                         ("keys", list(o.get("owned_keys") or []))])
            for o in t.get("outputs") or []]


def install_state(t: dict, which=shutil.which, exists=None) -> dict:
    exists = exists or (lambda p: os.path.exists(os.path.expanduser(p)))
    result = OrderedDict()
    for s in t.get("surfaces") or []:
        probe = s.get("install_probe")
        if not probe:
            continue
        via = None
        for item in probe.get("any_of") or []:
            if "cmd" in item and which(item["cmd"]):
                via = f"cmd:{item['cmd']}"
                break
            if "path" in item and exists(item["path"]):
                via = f"path:{item['path']}"
                break
        result[s["id"]] = {"installed": via is not None, "via": via}
    return result


# --------------------------------------------------------------------------- revisions

def _git_env(home=None) -> dict:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_CONFIG")}
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    if home is not None:
        env["HOME"] = str(home)
        env["GIT_CONFIG_GLOBAL"] = os.devnull
    return env


def _git(root: Path, *args, check_rc=True, text=True, home=None):
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=text, timeout=60,
                       env=_git_env(home))
    if check_rc and r.returncode != 0:
        err = r.stderr if text else r.stderr.decode("utf-8", "replace")
        raise DataError(f"git {' '.join(args)} failed: {err.strip()}")
    return r


def check_rev(rev: str, root: Path = ROOT, pending_ok=False, only=None, as_json=False, home=None) -> int:
    root = Path(root)
    try:
        data = _git(root, "archive", "--format=tar", rev, text=False, home=home).stdout
    except (DataError, OSError, subprocess.SubprocessError) as exc:
        print(f"ERROR cannot export {rev}: {exc}", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="render-shims-rev-") as tmp:
        with tarfile.open(fileobj=io.BytesIO(data)) as tf:
            try:
                tf.extractall(tmp, filter="data")
            except TypeError:
                tf.extractall(tmp)
        script = Path(tmp) / "00-bootstrap" / "doctor" / "render_shims.py"
        if not script.is_file():
            print(f"SKIPPED {rev} has no 00-bootstrap/doctor/render_shims.py")
            return 3
        cmd = [sys.executable, str(script), "--check"]
        if pending_ok:
            cmd.append("--pending-ok")
        if only:
            cmd += ["--only", ",".join(only)]
        if as_json:
            cmd.append("--json")
        r = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True, timeout=120)
        sys.stdout.write(r.stdout)
        sys.stderr.write(r.stderr)
        return r.returncode


def verify_canonical(rev: str, root: Path = ROOT, home=None) -> int:
    root = Path(root)
    try:
        names = _git(root, "diff-tree", "--no-commit-id", "--name-status", "-r", rev,
                     home=home).stdout.splitlines()
    except (DataError, OSError, subprocess.SubprocessError) as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
    failures, checked = 0, 0
    for line in names:
        parts = line.split("\t")
        status, path = parts[0], parts[-1]
        if not path.endswith(".json"):
            print(f"NOTE non-JSON change in {rev}: {path}")
            continue
        checked += 1
        if status != "M":
            print(f"FAIL {path}: status {status} (canonicalization must only modify)")
            failures += 1
            continue
        try:
            new = _git(root, "show", f"{rev}:{path}", home=home).stdout
            old = _git(root, "show", f"{rev}^:{path}", home=home).stdout
            same = json.loads(new) == json.loads(old)
        except (DataError, ValueError) as exc:
            print(f"FAIL {path}: {exc}")
            failures += 1
            continue
        if not same:
            print(f"FAIL {path}: parses differently from its parent version")
            failures += 1
            continue
        note = "" if new == canonical(json.loads(new)) else " (NOTE: not in canonical form)"
        print(f"ok {path}: JSON-equal to parent{note}")
    if checked == 0:
        print(f"NOTE {rev} changes no .json file")
    return 1 if failures else 0


# --------------------------------------------------------------------------- self-test

def _write_fixture_root(root: Path, table: dict, render: bool = True) -> None:
    (root / "02-shared-references").mkdir(parents=True, exist_ok=True)
    (root / TABLE_REL).write_text(canonical(table), encoding="utf-8")
    (root / "09-tools").mkdir(parents=True, exist_ok=True)
    (root / TEST_VALIDATORS_REL).write_text(
        "import unittest\n\n\nclass TestFixtureOk(unittest.TestCase):\n    pass\n", encoding="utf-8")
    (root / "tools").mkdir(parents=True, exist_ok=True)
    (root / "tools" / "fx.py").write_text("# fixture tool; supports --self-test\n", encoding="utf-8")
    wrap = root / "wrap" / "ws-hook"
    wrap.parent.mkdir(parents=True, exist_ok=True)
    wrap.write_bytes(b"#!/bin/sh\nexit 0\n")
    wrap.chmod(0o755)
    if render:
        write(root)


def _fixture_base() -> dict:
    return json.loads((ROOT / FIXTURE_BASE_REL).read_text(encoding="utf-8"))


def _expect(results: list, name: str, res: dict, needle: str, *, want_error=True) -> None:
    blob = "\n".join(res["errors"] if want_error else res["warnings"])
    ok = needle in blob and (bool(res["errors"]) if want_error else not res["errors"])
    results.append((name, ok, "" if ok else f"expected {needle!r} in {'errors' if want_error else 'warnings'}; got errors={res['errors']} warnings={res['warnings']}"))


def _mutate_case(results: list, name: str, mutate, needle: str, *, only=None, pending_ok=False,
                 rerender=False, want_error=True, post=None) -> None:
    table = _fixture_base()
    with tempfile.TemporaryDirectory(prefix="render-shims-st-") as tmp:
        root = Path(tmp)
        _write_fixture_root(root, table, render=True)
        mutate(table)
        (root / TABLE_REL).write_text(canonical(table), encoding="utf-8")
        if rerender:
            write(root)
        if post:
            post(root)
        res = check(root, only=only, pending_ok=pending_ok)
    _expect(results, name, res, needle, want_error=want_error)


def _reg(table: dict, rid: str) -> dict:
    return next(r for r in table["registrations"] if r["id"] == rid)


def self_test_cases() -> list:
    results = []
    base = _fixture_base()
    with tempfile.TemporaryDirectory(prefix="render-shims-st-") as tmp:
        root = Path(tmp)
        _write_fixture_root(root, base)
        res = check(root)
        results.append(("base fixture is clean", not res["errors"] and not res["warnings"],
                        f"errors={res['errors']} warnings={res['warnings']}"))
        second = write(root)
        results.append(("write is idempotent", second == [], f"rewrote {second}"))

    def drop_codex(t):
        t["surfaces"] = [s for s in t["surfaces"] if s["id"] != "codex"]
        for lay in t["layers"]:
            lay["loaded_by"] = [x for x in lay["loaded_by"] if x != "codex"]
    _mutate_case(results, "missing codex row", drop_codex, "minimum surface row missing: codex", only=["coverage"])
    _mutate_case(results, "row family not in families",
                 lambda t: t["surfaces"][0].__setitem__("family", "martian"), "is not a key of families")
    _mutate_case(results, "enforced with no verified_by",
                 lambda t: t["surfaces"][0]["coverage"]["H16"].__setitem__("verified_by", []),
                 "with no verified_by", only=["coverage"])
    _mutate_case(results, "unresolvable verified_by in strict mode",
                 lambda t: t["surfaces"][0]["coverage"]["H16"].__setitem__("verified_by", ["fixture:TestNope"]),
                 "fixture:TestNope does not resolve", only=["coverage"])
    _mutate_case(results, "unresolvable fixture ref is a warning under --pending-ok",
                 lambda t: t["surfaces"][0]["coverage"]["H16"].__setitem__("verified_by", ["fixture:TestNope"]),
                 "pending: fixture:TestNope", only=["coverage"], pending_ok=True, want_error=False)
    _mutate_case(results, "unresolvable probe ref stays an error under --pending-ok",
                 lambda t: t["surfaces"][0]["coverage"]["H16"].__setitem__("verified_by", ["probe:claude-code@dev-a"]),
                 "probe:claude-code@dev-a does not resolve", only=["coverage"], pending_ok=True)
    _mutate_case(results, "invalid coverage mode",
                 lambda t: t["surfaces"][0]["coverage"]["H19"].__setitem__("mode", "mostly"),
                 "invalid mode 'mostly'", only=["coverage"])

    def dup_cursor_session_end(t):
        t["registrations"].append({"id": "fx-cursor-user.session-end", "layer": "fx-cursor-user",
                                   "event": "session-end", "command": "fx-nudge-user", "timeout": None,
                                   "matcher": None, "host_skip": [], "claim_group": None, "defers_to": None})
    _mutate_case(results, "duplicate Cursor sessionEnd (project plus user)", dup_cursor_session_end,
                 "rule R: cursor session-end (workspace) behaviour session-close-nudge", only=["registrations"])
    _mutate_case(results, "plugin SessionStart duplicates the user hook without a claim_group",
                 lambda t: _reg(t, "fx-plugin.session-start").__setitem__("claim_group", None),
                 "rule R: claude-code session-start (other) behaviour boot-context", only=["registrations"])
    _mutate_case(results, "project-scope shim references $HOME",
                 lambda t: t["commands"]["fx-nudge-project"].__setitem__("template", "$HOME/x/nudge.sh"),
                 "references $HOME or ~", only=["registrations"])
    _mutate_case(results, "host_skip on a command without host_filter",
                 lambda t: t["commands"]["fx-boot"].__setitem__("implements", ["claim"]),
                 "does not implement host_filter", only=["registrations"])
    _mutate_case(results, "pending registration fails in strict mode",
                 lambda t: _reg(t, "fx-project.session-end").__setitem__("pending", "C: retire"),
                 "pending change not applied", only=["registrations"])
    _mutate_case(results, "wrapper sha mismatch", lambda t: None, "sha256 mismatch", only=["wrappers"],
                 post=lambda r: (r / "wrap" / "ws-hook").write_bytes(b"#!/bin/sh\nexit 1\n"))
    _mutate_case(results, "hand-edited output is drift", lambda t: None, "drift in out/user.json",
                 only=["outputs"], post=lambda r: (r / "out" / "user.json").write_text(
                     (r / "out" / "user.json").read_text(encoding="utf-8").replace("15", "16"), encoding="utf-8"))
    _mutate_case(results, "unknown top-level key", lambda t: t.__setitem__("extra", 1), "unknown top-level key")

    results += overlay_cases()

    # --rev on a revision without render_shims.py exits 3; --verify-canonical catches a real change.
    with tempfile.TemporaryDirectory(prefix="render-shims-git-") as tmp:
        repo = Path(tmp) / "repo"
        home = Path(tmp) / "home"
        repo.mkdir()
        home.mkdir()
        ident = ["-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null"]
        try:
            _git(repo, "init", "-q", home=home)
            (repo / "a.json").write_text('{"b": 1,  "a": [1,2]}\n', encoding="utf-8")
            _git(repo, "add", "a.json", home=home)
            _git(repo, *ident, "commit", "-q", "-m", "one", home=home)
            rc = check_rev("HEAD", repo, home=home)
            results.append(("--rev without render_shims.py exits 3", rc == 3, f"rc={rc}"))
            (repo / "a.json").write_text(canonical({"b": 1, "a": [1, 2]}), encoding="utf-8")
            _git(repo, *ident, "commit", "-q", "-am", "canonicalize", home=home)
            rc_ok = verify_canonical("HEAD", repo, home=home)
            (repo / "a.json").write_text(canonical({"b": 2, "a": [1, 2]}), encoding="utf-8")
            _git(repo, *ident, "commit", "-q", "-am", "change", home=home)
            rc_bad = verify_canonical("HEAD", repo, home=home)
            results.append(("--verify-canonical passes a pure reformat and fails a value change",
                            rc_ok == 0 and rc_bad == 1, f"ok={rc_ok} bad={rc_bad}"))
        except (DataError, OSError, subprocess.SubprocessError) as exc:
            results.append(("git fixtures", False, str(exc)))
    return results


IDENTITY_FIXTURES_REL = "09-tools/fixtures/identity"
V4_REV = "2ff02e7"          # the commit that carries the installed v4 overlay (read-only history)


def _git_show(rev_path: str):
    try:
        r = _git(ROOT, "show", rev_path, check_rc=False)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def overlay_cases() -> list:
    """H17 emitter cases: the synthetic golden, owners x forms x case, the guarded floor command,
    no GIT_AUTHOR_*, the v4 reproduction from the tables, identity-inc, and the owned-keys guard."""
    results = []
    fx = ROOT / IDENTITY_FIXTURES_REL
    try:
        cr = json.loads((fx / "context-remotes.json").read_text(encoding="utf-8"))
        dev = json.loads((fx / "devices.json").read_text(encoding="utf-8"))
        golden = json.loads((fx / "overlay-v5.golden.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [("overlay: identity fixtures readable", False, str(exc))]
    env = overlay_env(cr, dev, "v5")
    results.append(("overlay: v5 env equals the synthetic golden", env == golden["env"],
                    "run the emitter and diff against overlay-v5.golden.json"))
    pairs = [(env[f"GIT_CONFIG_KEY_{i}"], env[f"GIT_CONFIG_VALUE_{i}"]) for i in range(int(env["GIT_CONFIG_COUNT"]))]
    blocked = cr["blocked_scheme"]
    emp = [v for k, v in pairs if k == f"url.{blocked}.insteadOf"]
    want = set()
    accts = ["acme-worker", "pat-sample", "git"]
    for host, owner, alias in (("github.com", "acme-corp", "github-work"), ("bitbucket.org", "acme-bb", None)):
        for o in {owner, owner.upper(), owner.capitalize()}:
            forms = [f"git@{host}:{o}/", f"git@{host}:/{o}/", f"ssh://git@{host}/{o}/", f"ssh://git@{host}:22/{o}/",
                     f"ssh://{host}/{o}/", f"https://{host}/{o}/", f"https://{host}:443/{o}/",
                     f"https://www.{host}/{o}/"]
            if host == "github.com":
                forms += [f"ssh://git@ssh.{host}:443/{o}/"]
            forms += [f"https://{a}@{host}/{o}/" for a in accts]
            if alias:
                forms += [f"git@{alias}:{o}/", f"{alias}:{o}/", f"ssh://git@{alias}/{o}/", f"ssh://{alias}/{o}/"]
            want |= set(forms)
    results.append(("overlay: employer blocks equal owners x forms x case, deduplicated",
                    set(emp) == want and len(emp) == len(set(emp)), f"missing={sorted(want - set(emp))} extra={sorted(set(emp) - want)}"))
    inc = [k for k, _v in pairs if k.startswith("includeIf.hasconfig:remote.*.url:")]
    want_inc = {f"includeIf.hasconfig:remote.*.url:{p}.path" for p in (
        "git@github.com:pat-sample/**", "git@github-work:pat-sample/**", "https://github.com/pat-sample/**",
        "ssh://git@github.com/pat-sample/**")}
    results.append(("overlay: personal includes equal personal owners x forms", set(inc) == want_inc and len(inc) == 4,
                    str(inc)))
    results.append(("overlay: no GIT_AUTHOR_* or GIT_COMMITTER_* key, in env or in pairs",
                    not any(k.startswith(("GIT_AUTHOR_", "GIT_COMMITTER_")) for k in env)
                    and not any(k.lower().startswith("user.") for k, _v in pairs), ""))
    guarded = FLOOR_COMMAND
    hook = dict((k, v) for k, v in pairs if k == "hook.ws-claude-wall.command")
    events = [v for k, v in pairs if k == "hook.ws-claude-wall.event"]
    results.append(("overlay: the floor hook is the guarded command, on the four events, enabled",
                    hook.get("hook.ws-claude-wall.command") == guarded and '"$@"' not in guarded
                    and events == ["pre-commit", "commit-msg", "pre-merge-commit", "pre-push"]
                    and ("hook.ws-claude-wall.enabled", "true") in pairs, str(hook)))
    kinds = []
    for k, _v in pairs:
        kind = ("include" if k.startswith("includeIf.") else "https" if k.startswith("url.https://")
                else "helper" if k.startswith("credential.") else "block" if k.startswith(f"url.{blocked}")
                else "floor" if k.startswith("hook.") else "?")
        if not kinds or kinds[-1] != kind:
            kinds.append(kind)
    results.append(("overlay: GIT_CONFIG order is include, https insteadOf, helper reset, block, floor",
                    kinds == ["include", "https", "helper", "block", "floor"], str(kinds)))
    helper = [v for k, v in pairs if k.startswith("credential.")]
    results.append(("overlay: the credential helper is reset, then gh", helper == ["", "!gh auth git-credential"],
                    str(helper)))
    results.append(("overlay: markers and the gh belt",
                    env.get("WS_CLAUDE_OVERLAY") == "v5" and env.get("WS_SURFACE_FAMILY") == "claude"
                    and env.get("GH_CONFIG_DIR") == "~/.config/snds-workspace/gh-claude", ""))
    results.append(("identity-inc: Claude include and device includes equal the golden",
                    render_claude_identity_inc(dev) == golden["claude_identity_inc"]
                    and render_device_identity_inc(dev, "dev-a") == golden["identity_inc"]["dev-a"]
                    and render_device_identity_inc(dev, "dev-b") == golden["identity_inc"]["dev-b"]
                    and render_device_identity_inc(dev, "unknown") is None
                    and "http" not in golden["claude_identity_inc"], ""))
    bad = json.loads(json.dumps(dev))
    bad["identity_rules"][0]["identity"] = "acme-id"
    try:
        render_claude_identity_inc(bad)
        results.append(("identity-inc: an employer identity for the Claude rule is refused", False, ""))
    except DataError:
        results.append(("identity-inc: an employer identity for the Claude rule is refused", True, ""))
    t = {k: [] for k in TOP_KEYS}
    t.update(schema_version=1, families={}, outputs=[{"id": "x", "install_mode": "claude-settings-keys",
                                                      "owned_keys": ["hooks", "env"], "render": "hooks"},
                                                     {"id": "y", "install_mode": "tracked", "overlay": "v9"}])
    errs = check_table(t)
    results.append(("outputs: env is never a shim-installable owned key; overlay versions are closed",
                    any("env is never an owned" in e for e in errs) and any("overlay must be one of" in e for e in errs),
                    str(errs)))
    try:
        pr = _pr_module()
        det = pr.detect_surface(env={"AI_AGENT": "claude-code_2-1-280_agent", "CLAUDECODE": "1"}, ancestry=[],
                                isatty={"stdin": False, "stdout": False}, root=ROOT)
        oth = pr.detect_surface(env={"AI_AGENT": "vendor-x"}, ancestry=[], isatty={"stdin": False, "stdout": False},
                                root=ROOT)
        results.append(("table: AI_AGENT=claude-code_* is Claude Code; another value is the generic unknown-agent row",
                        det["acting_host"] == "claude-code" and det["family"] == "claude"
                        and oth["family"] == "unknown-agent" and oth["acting_host"] == "other-local-agents",
                        f"{det['acting_host']}/{det['family']} {oth['acting_host']}/{oth['family']}"))
    except DataError as exc:
        results.append(("table: AI_AGENT=claude-code_* is Claude Code", False, str(exc)))
    old_frag, old_inc = _git_show(f"{V4_REV}:00-bootstrap/dist/settings-user-fragment.json"), \
        _git_show(f"{V4_REV}:00-bootstrap/dist/git/claude-identity.inc")
    if old_frag is None or old_inc is None:
        results.append(("overlay: v4 reproduced from the tables", None, "no v4 history here (shallow clone?)"))
    else:
        try:
            rcr, rdev = identity_tables(ROOT)
            v4 = json.loads(old_frag, object_pairs_hook=OrderedDict).get("env") or {}
            ok = (list(overlay_env(rcr, rdev, "v4").items()) == list(v4.items())
                  and render_claude_identity_inc(rdev) == old_inc)
            results.append(("overlay: v4 env and claude-identity.inc reproduced byte-for-byte from the tables", ok, ""))
        except (DataError, ValueError) as exc:
            results.append(("overlay: v4 env and claude-identity.inc reproduced byte-for-byte from the tables", False,
                            str(exc)))
    return results


def self_test() -> int:
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        results = self_test_cases()
    failed = [r for r in results if r[1] is False or (r[1] is not None and not r[1])]
    skipped = [r for r in results if r[1] is None]
    for name, ok, detail in results:
        tag = "SKIP" if ok is None else ("ok  " if ok else "FAIL")
        print(f"{tag} {name}" + ("" if ok else f" — {detail}"))
    passed = len(results) - len(failed) - len(skipped)
    print(f"render_shims self-test: {passed}/{len(results)} passed" + (f", {len(skipped)} SKIPPED" if skipped else ""))
    return 1 if failed else (3 if skipped else 0)


# --------------------------------------------------------------------------- CLI

def _emit(report: dict, as_json: bool, cmd: str) -> None:
    if as_json:
        print(json.dumps({"schema_version": 1, "cmd": cmd, **report}, indent=2, ensure_ascii=False))
        return
    for e in report.get("errors", []):
        print(f"ERROR {e}")
    for w in report.get("warnings", []):
        print(f"WARN  {w}")
    if not report.get("errors"):
        print(f"ok render_shims {cmd}: clean" + (f" ({len(report.get('warnings', []))} warning(s))" if report.get("warnings") else ""))


def emit(kind: str, root: Path = ROOT, *, device=None, overlay=None, out=None) -> int:
    """--emit identity-inc --device ID: that device's default identity include on stdout (exit 3 when
    the device has none). --emit overlay-env [--overlay v4|v5]: the overlay env JSON (read-only)."""
    out = out or sys.stdout
    try:
        cr, dev = identity_tables(root)
        if kind == "identity-inc":
            if not device:
                print("usage: --emit identity-inc --device ID", file=sys.stderr)
                return 2
            text = render_device_identity_inc(dev, device)
            if text is None:
                print(f"no default identity for device {device!r} (unknown devices get none)", file=sys.stderr)
                return 3
            out.write(text)
            return 0
        t = load_table(root)
        row = next((o for o in t.get("outputs") or [] if o.get("overlay")), {})
        out.write(canonical(overlay_env(cr, dev, overlay or row.get("overlay") or "v5")))
        return 0
    except DataError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Render and check hook registrations from surfaces.json.")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--list", action="store_true")
    mode.add_argument("--install-state", action="store_true")
    mode.add_argument("--verify-canonical", metavar="REV")
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--emit", choices=["identity-inc", "overlay-env"])
    ap.add_argument("--device")
    ap.add_argument("--overlay", choices=list(OVERLAY_VERSIONS))
    ap.add_argument("--only")
    ap.add_argument("--pending-ok", action="store_true")
    ap.add_argument("--rev")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--root", help=argparse.SUPPRESS)
    try:
        args = ap.parse_args(argv)
    except SystemExit as exc:
        return 2 if exc.code else 0
    root = Path(args.root).resolve() if args.root else ROOT

    if args.self_test:
        return self_test()
    if args.emit:
        return emit(args.emit, root, device=args.device, overlay=args.overlay)
    if args.verify_canonical:
        return verify_canonical(args.verify_canonical, root)
    if args.check:
        only = [x.strip() for x in args.only.split(",")] if args.only else None
        if only and any(x not in CHECK_AREAS for x in only):
            print(f"usage: --only takes {', '.join(CHECK_AREAS)}", file=sys.stderr)
            return 2
        if args.rev:
            return check_rev(args.rev, root, args.pending_ok, only, args.json)
        report = check(root, only=only, pending_ok=args.pending_ok)
        data_error = report.pop("data_error", False)
        _emit(report, args.json, "check")
        if data_error:
            return 2
        return 1 if report["errors"] else 0
    try:
        t = load_table(root)
    except DataError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2
    if args.write:
        try:
            written = write(root, args.only)
        except DataError as exc:
            print(f"ERROR {exc}", file=sys.stderr)
            return 2
        for p in written:
            print(f"wrote {p}")
        if not written:
            print("ok nothing to write")
        return 0
    if args.list:
        print(json.dumps({"schema_version": 1, "cmd": "list", "outputs": list_outputs(t)}, indent=2, ensure_ascii=False))
        return 0
    if args.install_state:
        state = install_state(t)
        if args.json:
            print(json.dumps({"schema_version": 1, "cmd": "install-state", "surfaces": state}, indent=2, ensure_ascii=False))
        else:
            for sid, v in state.items():
                print(f"{sid}: {'installed via ' + v['via'] if v['installed'] else 'not installed'}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
