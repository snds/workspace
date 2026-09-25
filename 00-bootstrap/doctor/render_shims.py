#!/usr/bin/env python3
"""render_shims.py — render every hook registration file from the surface registry (H16).

The registry is `02-shared-references/surfaces.json`. This tool renders the tracked outputs it
declares (Claude settings fragments, Cursor hook files, the snds plugin hooks, the Codex and Cursor
config fragments, the probe registration fragments and the generated SURFACES.md block) and
checks the table's semantics:

  Rule C  every component has a coverage entry on every minimum surface; modes come from the
          enum; every enforced* mode names verified_by refs; every verified_by ref resolves, on
          any mode. planned_verified_by holds the refs an entry still waits on. When all of them
          resolve, Rule C prints a NOTICE until the entry is promoted: the refs move to
          verified_by and the mode goes up, or, when a non-ref condition remains (an install that
          ships later, a human step), the refs move and `how` names that condition. Notices are
          report-only: they sit in their own list, never in the warnings, and never change the
          exit code.
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
  render_shims.py --emit claude-permissions --device ID
  render_shims.py --rewrite-audit [--json]
  render_shims.py --self-test

H17 (T8) adds two emitters. The Claude overlay is rendered from context-remotes.json and
devices.json into dist/claude-overlay.env (render `claude-overlay-env`; the output row's `overlay`
names the layout version). Since D-W1-4 it is no longer the `env` block of settings-user-fragment.json
(other hosts import Claude's settings env): only the Sean-run --install-claude-overlay installs it, to
~/.config/snds-workspace/claude-overlay.env, and the `ws-hook env-file` SessionStart hook copies it into
Claude Code's session env file (CLAUDE_ENV_FILE), which reaches only Claude's shell tool. `claude-identity.inc` is rendered from the Claude identity rule, and
`--emit identity-inc --device ID` prints one device's default identity include for --install-identity.
`--rewrite-audit` (H17-R9, report-only, read by `workspace-doctor.sh --check`) reads the git config
files, not the overlay env, and reports URL rewrites that can undo the employer transport block.

H15 adds the wall guard's outputs: PreToolUse / beforeShellExecution / preToolUse / beforeMCPExecution
registrations that run `ws-hook --host H --event pre-tool` (the Claude matcher is generated from
`tool_families`), the Codex rules-file belt and the belt lists (from 09-tools/wall_guard.py
BELT_INVARIANTS), and the Claude permissions template. The template is never installed whole:
`--emit claude-permissions --device ID` expands it for one device from the checkout cache and the
vault's employer folders, on stdout only.

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
BEACONS_REL = "02-shared-references/beacons.json"

TOP_KEYS = [
    "schema_version", "doc", "coverage_modes", "minimum_surfaces", "components", "families",
    "never_markers", "agent_possible_env", "probe_env_name_prefixes", "probe_env_value_allowlist",
    "surfaces", "formats", "dialects", "layers", "commands", "registrations", "outputs", "wrappers",
]
# H15: optional keys (the render fixtures predate them). tool_families feeds the generated Claude
# PreToolUse matcher and the guard's payload reader; wall_guard holds the rollout modes.
OPTIONAL_TOP_KEYS = ["tool_families", "wall_guard"]
TOOL_FAMILY_KINDS = {"shell", "file", "server", "url", "mcp"}
WALL_MODES = {"enforce", "report"}
MATCHER_TOKEN_RE = re.compile(r"^@tool_families:([a-z-]+)$")
GUARD_REL = "09-tools/wall_guard.py"
KINDS = {"cli-agent", "ide-agent", "desktop-app", "cloud-agent", "chat", "browser", "mcp-client", "human"}
DIALECTS = {"claude", "cursor", "codex", "plain", "none"}
CHANNELS = {"claude-settings-env", "claude-session-env-file", "codex-shell-environment-policy",
            "cursor-sessionstart-env", "none"}
INSTALL_MODES = {"tracked", "whole-file", "claude-settings-keys", "merge-hook-entries", "managed-block"}
ANCESTRY_MATCH = {"exact", "prefix"}
RENDERS = {"hooks", "codex-config", "cursor-sandbox", "surfaces-md-block", "identity-inc", "beacon",
           "contract-core", "codex-rules", "claude-permissions", "wall-belts", "claude-overlay-env"}
CONTRACT_REL = "AGENTS.md"
WINDSURF_RULE_MAX_CHARS = 12_000   # Windsurf's per-rule character limit (H6)
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
    unknown = [k for k in keys if k not in TOP_KEYS and k not in OPTIONAL_TOP_KEYS]
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
        if "overlay" in o and (o.get("overlay") not in OVERLAY_VERSIONS or o.get("render") != "claude-overlay-env"):
            errors.append(f"output {o.get('id')}: overlay must be one of {list(OVERLAY_VERSIONS)} on a "
                          "claude-overlay-env output")
        if o.get("render") == "claude-overlay-env" and (o.get("overlay") not in OVERLAY_VERSIONS or o.get("install_path")):
            errors.append(f"output {o.get('id')}: the overlay env file names its overlay version and is installed "
                          "only by --install-claude-overlay (no install_path)")
        if "env" in (o.get("owned_keys") or []):
            errors.append(f"output {o.get('id')}: env is never an owned (shim-installable) key; "
                          "the overlay is installed only by --install-claude-overlay")
        if o.get("render") == "claude-permissions" and o.get("install_path"):
            errors.append(f"output {o.get('id')}: the permissions template is rendered per device at install "
                          "time (--emit claude-permissions); it never installs whole")
    errors += check_guard_tables(t)
    return errors


def check_guard_tables(t: dict) -> list:
    """H15 shapes: tool families (ids unique, kinds known, list-valued keys) and the rollout modes.
    The table can never put R1, R3 or R6 in report mode, and a host override only raises a rule."""
    errors = []
    fams = t.get("tool_families")
    if fams is not None:
        if not isinstance(fams, list):
            return ["tool_families: must be a list"]
        seen = set()
        for i, f in enumerate(fams):
            if not isinstance(f, dict) or not isinstance(f.get("id"), str):
                errors.append(f"tool_families[{i}]: needs a string id")
                continue
            if f["id"] in seen:
                errors.append(f"tool_families: duplicate id {f['id']}")
            seen.add(f["id"])
            if f.get("kind") not in TOOL_FAMILY_KINDS:
                errors.append(f"tool_families.{f['id']}: invalid kind {f.get('kind')!r}")
            for k in ("names", "claude_matcher", "path_keys", "command_keys", "cwd_keys", "url_keys", "mcp_suffixes"):
                v = f.get(k)
                if v is not None and not (isinstance(v, list) and all(isinstance(x, str) for x in v)):
                    errors.append(f"tool_families.{f['id']}.{k}: must be a list of strings")
            if f.get("rollout") not in (None, "report"):
                errors.append(f"tool_families.{f['id']}.rollout: only 'report' may be declared")
    wg = t.get("wall_guard")
    if wg is not None:
        rules = wg.get("rules") if isinstance(wg, dict) else None
        if not isinstance(rules, dict):
            errors.append("wall_guard.rules: must be an object")
        else:
            for k, v in rules.items():
                if v not in WALL_MODES:
                    errors.append(f"wall_guard.rules.{k}: mode must be enforce or report")
            for k in ("R1", "R3", "R6"):
                if rules.get(k) != "enforce":
                    errors.append(f"wall_guard.rules.{k}: enforces from install (plan H15); never report")
        for host, over in ((wg.get("host_overrides") if isinstance(wg, dict) else None) or {}).items():
            for k, v in (over or {}).items():
                if v != "enforce":
                    errors.append(f"wall_guard.host_overrides.{host}.{k}: an override only raises a rule to enforce")
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
    """Rule C: (errors, warnings, notices). Notices are report-only and never fail a check."""
    errors, warnings, notices = [], [], []
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
            planned = entry.get("planned_verified_by") or []
            for ref in planned:
                if not REF_RE.match(ref):
                    errors.append(f"{where}: bad planned_verified_by ref {ref!r}")
            refs = entry.get("verified_by") or []
            if mode.startswith("enforced") and not refs:
                errors.append(f"{where}: {mode} with no verified_by")
            for ref in refs:
                ok, kind, reason = resolve_ref(ref, root)
                if ok:
                    continue
                if pending_ok and kind in ("fixture", "selftest"):
                    warnings.append(f"{where}: pending: {reason}")
                else:
                    errors.append(f"{where}: {reason}")
            if planned_ready(entry, root):
                notices.append(f"{where}: not promoted: every planned_verified_by ref resolves "
                               f"({', '.join(planned)}); move them to verified_by and raise the mode, or move "
                               "them and name the remaining non-ref condition in how")
    return errors, warnings, notices


def planned_ready(entry: dict, root: Path = ROOT) -> bool:
    """True when an entry's planned_verified_by is non-empty and every ref in it resolves (Rule C notice)."""
    planned = entry.get("planned_verified_by") or []
    return bool(planned) and all(resolve_ref(ref, root)[0] for ref in planned)


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
        matcher = expand_matcher(t, r.get("matcher"))
        if fmt_name in CLAUDE_LIKE:
            entry = OrderedDict([("type", "command"), ("command", cmd)])
            if r.get("timeout") is not None:
                entry["timeout"] = r["timeout"]
            group = OrderedDict()
            if matcher is not None:
                group["matcher"] = matcher
            group["hooks"] = [entry]
            hooks.setdefault(name, []).append(group)
        elif fmt_name == "cursor-hooks":
            entry = OrderedDict([("command", cmd)])
            if matcher is not None:
                entry["matcher"] = matcher
            if r.get("timeout") is not None:
                entry["timeout"] = r["timeout"]
            hooks.setdefault(name, []).append(entry)
        else:
            raise DataError(f"layer {lid}: no renderer for format {fmt_name}")
    return hooks


def expand_matcher(t: dict, matcher):
    """`@tool_families:claude` -> the Claude PreToolUse matcher generated from the tool families."""
    m = MATCHER_TOKEN_RE.match(matcher or "") if isinstance(matcher, str) else None
    if not m:
        return matcher
    key = f"{m.group(1)}_matcher"
    parts = []
    for f in t.get("tool_families") or []:
        for x in (f or {}).get(key) or []:
            if x not in parts:
                parts.append(x)
    if not parts:
        raise DataError(f"matcher {matcher}: no tool family declares {key}")
    return "|".join(parts)


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
        # D-W1-4: the user fragment carries no env block (it held only the overlay, which is now the
        # claude-overlay-env output). A tracked project file keeps its own env.
        if out.get("install_mode") == "claude-settings-keys":
            base.pop("env", None)
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
# Written by installers.py (EMPLOYER_NOIDENT_INC). Included AFTER the personal includes for every
# employer remote form, so a repo with both an employer and a personal remote (a fork) gets a blank
# identity with useConfigOnly: commit, cherry-pick, revert and am cannot mint a personal identity there.
OVERLAY_NOIDENT = "~/.config/snds-workspace/git/claude-employer-noident.inc"
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
IDENTITY_INC_HEADER_V4 = (
    "# Claude surfaces are personal-only (06-context/memory/feedback-credential-scoping.md).\n"
    "# Included ONLY for repos whose remote is an snds/* URL (includeIf hasconfig in the\n"
    "# Claude env overlay). Never included in employer repos. No remote URLs in this file\n"
    "# (git forbids them inside hasconfig includes).\n"
)
IDENTITY_INC_HEADER = (
    "# Claude surfaces are personal-only (06-context/memory/feedback-credential-scoping.md).\n"
    "# Included for repos with an snds/* remote (includeIf hasconfig in the Claude env overlay).\n"
    "# A repo that also has an employer remote gets a later no-identity include, so this\n"
    "# identity never applies there. No remote URLs in this file (git forbids them inside\n"
    "# hasconfig includes).\n"
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
    if version != "v4":
        accts0 = []
        for ident in dev.get("identities") or []:
            for acct in ident.get("accounts") or []:
                if acct not in accts0:
                    accts0.append(acct)
        if "git" not in accts0:
            accts0.append("git")
        seen_ni = set()
        for o in employer:
            user, forms, aliases = _host_facts(cr, dev, o["host"])
            for pre in _employer_prefixes(o["owner"], o["host"], user, forms, aliases, accts0, version):
                if pre not in seen_ni:
                    seen_ni.add(pre)
                    pairs.append((f"includeIf.hasconfig:remote.*.url:{pre}**.path", OVERLAY_NOIDENT))
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


# D-W1-4: the overlay as a shell file for Claude Code's session env file. ws_hook.py (env-file) parses
# it strictly: `#` lines, then one `export NAME='value'` per overlay name. WS_OVERLAY_CHANNEL marks the
# channel, so a live probe shows the env file (not the settings env) delivered the overlay; the
# overlay pairs and WS_CLAUDE_OVERLAY stay v5.
OVERLAY_ENV_BEGIN = "# BEGIN snds-workspace overlay"
OVERLAY_ENV_END = "# END snds-workspace overlay"
OVERLAY_CHANNEL = ("WS_OVERLAY_CHANNEL", "env-file")


def _shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"


def overlay_env_file_pairs(cr: dict, dev: dict, version: str = "v5") -> list:
    """The overlay env pairs with the channel marker after the markers, before GH_CONFIG_DIR."""
    items = list(overlay_env(cr, dev, version).items())
    at = next(i for i, (k, _v) in enumerate(items) if k == "GH_CONFIG_DIR")
    return items[:at] + [OVERLAY_CHANNEL] + items[at:]


def render_overlay_env_file(cr: dict, dev: dict, version: str = "v5") -> str:
    lines = [
        "# snds-workspace Claude overlay (H17, D-W1-4). Rendered by 00-bootstrap/doctor/render_shims.py from",
        "# context-remotes.json and devices.json; do not edit by hand. --install-claude-overlay copies it to",
        "# ~/.config/snds-workspace/claude-overlay.env; the `ws-hook env-file` SessionStart hook validates every",
        "# line and writes the block, with ~/ rendered to the home, into Claude Code's session env file.",
        OVERLAY_ENV_BEGIN,
    ]
    for k, v in overlay_env_file_pairs(cr, dev, version):
        if any(ord(c) < 0x20 or ord(c) == 0x7f for c in v):
            raise DataError(f"overlay env file: {k} has a control character")
        lines.append(f"export {k}={_shell_quote(v)}")
    lines.append(OVERLAY_ENV_END)
    return "\n".join(lines) + "\n"


def _render_overlay_env_output(out: dict, root: Path) -> str:
    cr, dev = identity_tables(root)
    return render_overlay_env_file(cr, dev, out.get("overlay") or "v5")


FILE_SCOPES = ("system", "global", "local", "worktree")


def rewrite_conflicts(cr: dict, dev: dict, entries: list, version: str = "v5") -> list:
    """H17-R9 audit: URL rewrites in git config files that can undo the employer transport block.

    entries: [(scope, key, value)] as `git config --show-scope --get-regexp` reports them. git reads
    the config files before the env scope that carries the block and keeps the first longest
    insteadOf match, so a file-scope insteadOf whose value starts with a blocked prefix ties with or
    beats the block. A matching pushInsteadOf is applied first for pushes, whatever its length. A
    rewrite whose target starts with a blocked prefix maps another spelling onto an employer URL,
    and git rewrites a URL only once. Returns [(scope, key, value, why)]; command-scope entries (the
    overlay itself and -c) are skipped."""
    blocked = cr.get("blocked_scheme")
    prefixes = [v for k, v in overlay_pairs(cr, dev, version) if k == f"url.{blocked}.insteadOf"]
    out = []
    for scope, key, value in entries:
        if scope not in FILE_SCOPES or not key.lower().startswith("url."):
            continue
        base, _, var = key[4:].rpartition(".")
        var = var.lower()
        if var not in ("insteadof", "pushinsteadof") or base == blocked:
            continue
        why = None
        if var == "insteadof" and any(value.startswith(p) for p in prefixes):
            why = "ties with or beats the transport block"
        elif var == "pushinsteadof" and any(value.startswith(p) or p.startswith(value) for p in prefixes):
            why = "applies to employer pushes before the transport block"
        elif any(base.startswith(p) for p in prefixes):
            why = "maps another spelling onto an employer URL"
        if why:
            out.append((scope, key, value, why))
    return out


def _config_rewrites(cwd: Path, env_over=None) -> list:
    """[(scope, key, value)] for url.*.insteadOf / pushInsteadOf in the config files git reads from
    cwd. The env config (GIT_CONFIG_COUNT/KEY/VALUE, GIT_CONFIG_PARAMETERS) is dropped after
    env_over is applied; an env_over value of None removes that variable (tests)."""
    base = dict(os.environ)
    for k, v in (env_over or {}).items():
        if v is None:
            base.pop(k, None)
        else:
            base[k] = v
    env = {k: v for k, v in base.items()
           if k not in ("GIT_CONFIG_COUNT", "GIT_CONFIG_PARAMETERS")
           and not k.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))}
    # surrogateescape: a non-UTF-8 byte in any rewrite (related or not) must not crash the audit.
    r = subprocess.run(["git", "config", "--show-scope", "-z", "--get-regexp",
                        r"^url\..*\.(insteadof|pushinsteadof)$"],
                       cwd=str(cwd), env=env, capture_output=True, encoding="utf-8", errors="surrogateescape",
                       timeout=20)
    if r.returncode == 1 and not r.stdout:
        return []
    if r.returncode != 0:
        raise DataError(f"git config failed: {r.stderr.strip()[:200]}")
    parts = r.stdout.split("\0")
    out = []
    for scope, kv in zip(parts[0::2], parts[1::2]):
        key, _, value = kv.partition("\n")
        out.append((scope, key, value))
    return out


def rewrite_audit(root: Path = ROOT, cwd=None, as_json: bool = False, out=None) -> int:
    """--rewrite-audit: report-only (H17-R9). Exit 0 clean, 1 when a config-file rewrite can undo
    the transport block, 2 on a data or git error. Runs from $HOME by default, so it reads the
    system and user files. Any crash is exit 2 (the doctor's "unavailable"), never 1 (a finding)."""
    out = out or sys.stdout
    try:
        cr, dev = identity_tables(root)
        hits = rewrite_conflicts(cr, dev, _config_rewrites(Path(cwd) if cwd else Path.home()))
    except Exception as exc:  # noqa: BLE001 - exit 1 means a finding, so a crash must not reach it
        print(f"ERROR {exc.__class__.__name__}: {exc}", file=sys.stderr)
        return 2

    def safe(x: str) -> str:
        return x.encode("utf-8", "surrogateescape").decode("utf-8", "replace")

    hits = [tuple(safe(x) for x in h) for h in hits]
    if as_json:
        out.write(json.dumps({"schema_version": 1, "cmd": "rewrite-audit",
                              "findings": [{"scope": s, "key": k, "value": v, "why": w} for s, k, v, w in hits]},
                             indent=2, ensure_ascii=False) + "\n")
    else:
        for s, k, v, w in hits:
            out.write(f"WARN  {s}: {k} = {v} ({w})\n")
        if not hits:
            out.write("ok render_shims rewrite-audit: no config-file rewrite overlaps the transport block\n")
    return 1 if hits else 0


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


def render_claude_identity_inc(dev: dict, version: str = "v5") -> str:
    row = _identity_row(dev, claude_identity_id(dev))
    if row.get("class") != "personal":
        raise DataError("the Claude identity must be a personal identity")
    return (IDENTITY_INC_HEADER_V4 if version == "v4" else IDENTITY_INC_HEADER) + _user_block(row)


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
            "# its own. Claude surfaces get claude-identity.inc only in repos with a personal remote, and\n"
            "# the Claude floor refuses an employer identity on a Claude commit or merge commit, and on\n"
            "# any commit in a Claude push to a non-employer remote (IR1).\n"
            + _user_block(row))


def _render_identity_inc(out: dict, root: Path) -> str:
    _cr, dev = identity_tables(root)
    return render_claude_identity_inc(dev)


def load_beacons(root: Path = ROOT) -> dict:
    try:
        data = json.loads((Path(root) / BEACONS_REL).read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise DataError(f"beacon table missing: {BEACONS_REL}") from exc
    except (OSError, ValueError) as exc:
        raise DataError(f"beacon table unreadable: {BEACONS_REL}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("variants"), dict):
        raise DataError(f"{BEACONS_REL}: needs a variants object")
    return data


def render_beacon(t: dict, variant: str, root: Path = ROOT) -> str:
    """One per-family beacon (H6) from beacons.json. A variant lists block names in order;
    'family_rules' expands to the rule line of each family it names (surfaces.json families).
    A render over the variant's max_bytes is a DataError, so a beacon can never quietly grow
    the Codex window or the always-loaded set."""
    b = load_beacons(root)
    v = (b.get("variants") or {}).get(variant)
    if not isinstance(v, dict):
        raise DataError(f"beacon variant {variant!r} is not declared in {BEACONS_REL}")
    blocks, rules = b.get("blocks") or {}, b.get("family_rules") or {}
    lines = []
    for part in v.get("parts") or []:
        if part == "family_rules":
            for fam in v.get("families") or []:
                if fam not in (t.get("families") or {}):
                    raise DataError(f"beacon {variant}: family {fam!r} is not a key of surfaces.json families")
                if fam not in rules:
                    raise DataError(f"beacon {variant}: no family_rules line for {fam!r}")
                lines.append(rules[fam])
        elif part in blocks:
            lines += [ln.replace("{variant}", variant) for ln in blocks[part]]
        else:
            raise DataError(f"beacon {variant}: unknown block {part!r}")
    text = "\n".join(lines) + "\n"
    size, cap = len(text.encode("utf-8")), v.get("max_bytes")
    if not isinstance(cap, int) or size > cap:
        raise DataError(f"beacon {variant}: {size} bytes over max_bytes {cap}")
    return text


def _md_section(lines: list, heading: str) -> list:
    """The lines of one AGENTS.md section: the heading through the line before the next heading
    of the same or a higher level. Trailing rules (---) and blank lines are dropped."""
    level = len(heading) - len(heading.lstrip("#"))
    try:
        start = lines.index(heading)
    except ValueError as exc:
        raise DataError(f"contract-core: heading not found in {CONTRACT_REL}: {heading!r}") from exc
    end = len(lines)
    for i in range(start + 1, len(lines)):
        ln = lines[i]
        if ln.startswith("#"):
            lv = len(ln) - len(ln.lstrip("#"))
            if lv <= level and ln[lv:lv + 1] == " ":
                end = i
                break
    out = lines[start:end]
    while out and out[-1].strip() in ("", "---"):
        out.pop()
    return out


def _md_bullet(section: list, prefix: str) -> list:
    """One top-level bullet (with its indented continuation lines) from a section."""
    for i, ln in enumerate(section):
        if ln.startswith("- " + prefix):
            out = [ln]
            for nxt in section[i + 1:]:
                if not nxt.startswith("  ") or not nxt.strip():
                    break
                out.append(nxt)
            return out
    raise DataError(f"contract-core: bullet not found: {prefix!r}")


_REL_LINK_RE = re.compile(r"\]\((?!https?:|#|/|\.\./)([^)\s]+)\)")


def render_contract_core(out: dict, root: Path = ROOT) -> str:
    """H6: Windsurf truncates a rule at 12,000 characters and AGENTS.md is longer, so the
    invariant sections are repeated, verbatim, in a generated always-on rule. Relative links are
    re-rooted for the rule's directory; --check fails on drift and on a render over the cap."""
    try:
        lines = (Path(root) / CONTRACT_REL).read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise DataError(f"contract-core: {exc}") from exc
    depth = out["path"].count("/")
    body = []
    for sel in out.get("sections") or []:
        sec = _md_section(lines, sel["heading"])
        if sel.get("bullet"):
            sec = [sel["heading"] + f" (excerpt: {sel['bullet'].strip('*')})", ""] + _md_bullet(sec, sel["bullet"])
        body += sec + [""]
    body = [_REL_LINK_RE.sub(lambda m: "](" + "../" * depth + m.group(1) + ")", ln) for ln in body]
    head = [
        "---",
        "description: Workspace contract core for Windsurf, generated from the invariant sections of AGENTS.md",
        "trigger: always_on",
        "---",
        "",
        "# Workspace contract core (generated)",
        "",
        f"_Generated by `00-bootstrap/doctor/render_shims.py` from [AGENTS.md]({'../' * depth}AGENTS.md); do not "
        "hand-edit. Windsurf caps a rule at 12,000 characters and AGENTS.md is longer, so these sections are "
        "repeated verbatim. AGENTS.md stays the contract; read it whole when you can._",
        "",
    ]
    text = "\n".join(head + body).rstrip("\n") + "\n"
    cap = out.get("max_chars", WINDSURF_RULE_MAX_CHARS)
    if len(text) > cap:
        raise DataError(f"contract-core: {len(text)} characters over the {cap} rule limit")
    return text


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
    lines += ["", "Rendered outputs (installers read this mapping from `render_shims.py --list --json`; the "
              "`overlay` output is the Claude overlay env file, which only `--install-claude-overlay` installs):",
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


def _guard_module(root: Path = ROOT):
    """09-tools/wall_guard.py (the belts and the vault-folder rule live there)."""
    import importlib.util  # noqa: PLC0415

    path = ROOT / GUARD_REL
    name = "wall_guard"
    have = sys.modules.get(name)
    if have is not None and getattr(have, "__file__", None) and Path(have.__file__).resolve() == path.resolve():
        return have
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise DataError(f"{GUARD_REL} unavailable")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    try:
        spec.loader.exec_module(mod)
    except (OSError, SyntaxError, ImportError) as exc:
        sys.modules.pop(name, None)
        raise DataError(f"{GUARD_REL} unavailable ({exc.__class__.__name__})") from exc
    return mod


PERMISSIONS_DOC = (
    "Claude permission rules for the wall guard (H15, H25 carry-over). Rendered by render_shims.py; do not edit. "
    "`static` rules apply on every device. `per_device` rules are templates: `--emit claude-permissions --device "
    "ID` expands {employer_checkout} from the machine-local checkout cache and {employer_vault_folder} from the "
    "vault's 07-projects folders whose Context profile is employer (or whose name matches an employer path "
    "glob), and prints the device's rules; nothing machine-specific is ever committed. Read rules apply "
    "best-effort to Grep, Glob and the Bash file commands Claude recognises; the PreToolUse guard covers writes.")
CONTROL_REL = "~/.config/snds-workspace/control"
R6_EDIT_DENY = ("~/.gitconfig", "~/.cursor/hooks.json", "~/.codex/hooks.json", "~/.codex/config.toml")
SETTINGS_ASK = ("~/.claude/settings*.json",)


def claude_permissions_template(root: Path = ROOT) -> "OrderedDict":
    wg = _guard_module(root)
    deny = [f"Read({CONTROL_REL}/**)", f"Edit({CONTROL_REL}/**)"]
    deny += [f"Edit({p})" for p in R6_EDIT_DENY]
    deny += wg.claude_bash_rules()
    return OrderedDict([
        ("doc", PERMISSIONS_DOC),
        ("static", OrderedDict([("deny", deny), ("ask", [f"Edit({p})" for p in SETTINGS_ASK])])),
        ("per_device", OrderedDict([
            ("deny", ["Read({employer_checkout}/**)", "Edit({employer_checkout}/**)",
                      "Read({employer_vault_folder}/**)", "Edit({employer_vault_folder}/**)"]),
            ("sources", OrderedDict([
                ("employer_checkout", "checkout cache rows (telemetry/checkouts.json) with owner_class employer"),
                ("employer_vault_folder", "07-projects/* whose SESSION-STATE Context profile starts with centric-, "
                                          "or whose name matches an employer_path_globs entry"),
            ])),
        ])),
    ])


def render_claude_permissions_template(root: Path = ROOT) -> str:
    return canonical(claude_permissions_template(root))


def _perm_path(p, home: Path) -> str:
    """A permission-rule path: ~/ under the home, // for any other absolute path."""
    s = os.path.normpath(str(p))
    h = os.path.normpath(str(home))
    if s == h or s.startswith(h + "/"):
        return "~" + s[len(h):]
    return "/" + s if s.startswith("/") else s


def render_claude_permissions(root: Path = ROOT, *, home=None, vault=None, cache=None) -> "OrderedDict":
    """One device's rules: the static set plus the expanded per-device set (stdout only, never committed)."""
    home = Path(home) if home else Path.home()
    tmpl = claude_permissions_template(root)
    wg = _guard_module(root)
    pr = _pr_module()
    vroot = Path(vault) if vault else wg.vault_root(None, home)
    folders = [str(d) for d in wg.employer_vault_folders(vroot)]
    c = cache if isinstance(cache, dict) else pr._load_cache(cache, home)
    checkouts = [str(co.get("path")) for co in (c or {}).get("checkouts") or []
                 if isinstance(co, dict) and co.get("owner_class") == "employer" and co.get("path")]
    deny = list(tmpl["static"]["deny"])
    for rule in tmpl["per_device"]["deny"]:
        if "{employer_checkout}" in rule:
            deny += [rule.replace("{employer_checkout}", _perm_path(p, home)) for p in checkouts]
        elif "{employer_vault_folder}" in rule:
            deny += [rule.replace("{employer_vault_folder}", _perm_path(p, home)) for p in folders]
    return OrderedDict([("permissions", OrderedDict([("deny", deny), ("ask", list(tmpl["static"]["ask"]))])),
                        ("counts", OrderedDict([("employer_checkouts", len(checkouts)),
                                                ("employer_vault_folders", len(folders))]))])


def render_wall_belts(root: Path = ROOT) -> str:
    wg = _guard_module(root)
    lists = wg.belt_lists()
    return canonical(OrderedDict([
        ("doc", "Invariant-only wall belts (H15), rendered from 09-tools/wall_guard.py BELT_INVARIANTS: each entry is "
                "a command prefix the wall guard also denies, so no belt is stricter than the guard. Paste-only for "
                "hosts with static lists and no hooks: Warp (denylist regexes), Zed (always_deny regexes), OpenCode "
                "(bash permission globs set to deny). Formats are from vendor docs, [UNVERIFIED] until installed."),
        ("invariants", [OrderedDict([("id", iid), ("argv", pre), ("why", why)])
                        for iid, pre, why in wg.belt_prefixes()]),
        ("warp_denylist", lists["regex"]),
        ("zed_always_deny", lists["regex"]),
        ("opencode_bash_deny", lists["glob"]),
        ("claude_bash_deny", wg.claude_bash_rules()),
    ]))


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
    if kind == "beacon":
        return render_beacon(t, out.get("beacon") or "", root)
    if kind == "contract-core":
        return render_contract_core(out, root)
    if kind == "codex-rules":
        return _guard_module(root).render_codex_rules()
    if kind == "claude-permissions":
        return render_claude_permissions_template(root)
    if kind == "wall-belts":
        return render_wall_belts(root)
    if kind == "claude-overlay-env":
        return _render_overlay_env_output(out, root)
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
    """errors fail the check; warnings are --pending-ok leniency; notices are report-only (Rule C
    promotion reminders) and are kept out of warnings so a strict clean check stays clean."""
    root = Path(root)
    areas = set(only or CHECK_AREAS)
    errors, warnings, notices = [], [], []
    try:
        t = load_table(root)
    except DataError as exc:
        return {"errors": [str(exc)], "warnings": [], "notices": [], "data_error": True}
    errors += check_table(t)
    if errors:
        return {"errors": errors, "warnings": warnings, "notices": notices, "data_error": False}
    try:
        if "coverage" in areas:
            e, w, n = check_surface_coverage(t, root, pending_ok)
            errors += e
            warnings += w
            notices += n
        if "registrations" in areas:
            e, w = check_registrations(t, pending_ok)
            errors += e
            warnings += w
        if "outputs" in areas:
            errors += check_outputs(t, root)
        if "wrappers" in areas:
            errors += check_wrappers(t, root)
    except DataError as exc:
        return {"errors": errors + [str(exc)], "warnings": warnings, "notices": notices, "data_error": True}
    return {"errors": errors, "warnings": warnings, "notices": notices, "data_error": False}


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


def _expect(results: list, name: str, res: dict, needle: str, *, want_error=True, want_clean=False,
            want_notice=False) -> None:
    got = f"errors={res['errors']} warnings={res['warnings']} notices={res.get('notices')}"
    if want_clean:
        ok = not res["errors"] and not res["warnings"] and not res.get("notices")
        results.append((name, ok, "" if ok else f"expected no errors, warnings or notices; got {got}"))
        return
    if want_notice:
        # Report-only: the notice is present and the strict result (errors, warnings) stays clean.
        ok = needle in "\n".join(res.get("notices") or []) and not res["errors"] and not res["warnings"]
        results.append((name, ok, "" if ok else f"expected {needle!r} in notices only; got {got}"))
        return
    blob = "\n".join(res["errors"] if want_error else res["warnings"])
    ok = needle in blob and (bool(res["errors"]) if want_error else not res["errors"])
    results.append((name, ok, "" if ok else f"expected {needle!r} in {'errors' if want_error else 'warnings'}; got errors={res['errors']} warnings={res['warnings']}"))


def _mutate_case(results: list, name: str, mutate, needle: str, *, only=None, pending_ok=False,
                 rerender=False, want_error=True, want_clean=False, want_notice=False, post=None) -> None:
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
    _expect(results, name, res, needle, want_error=want_error, want_clean=want_clean, want_notice=want_notice)


def _reg(table: dict, rid: str) -> dict:
    return next(r for r in table["registrations"] if r["id"] == rid)


def self_test_cases() -> list:
    results = []
    base = _fixture_base()
    with tempfile.TemporaryDirectory(prefix="render-shims-st-") as tmp:
        root = Path(tmp)
        _write_fixture_root(root, base)
        res = check(root)
        results.append(("base fixture is clean", not res["errors"] and not res["warnings"] and not res["notices"],
                        f"errors={res['errors']} warnings={res['warnings']} notices={res['notices']}"))
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

    # Rule C, report-only: planned refs that all resolve mean the entry is due for promotion.
    def cursor_h19(t):
        return next(s for s in t["surfaces"] if s["id"] == "cursor")["coverage"]["H19"]
    def ready(t):
        cursor_h19(t).__setitem__("planned_verified_by", ["fixture:TestFixtureOk", "selftest:tools/fx.py"])
    _mutate_case(results, "planned refs that all resolve give a notice and no warning", ready,
                 "cursor.H19: not promoted: every planned_verified_by ref resolves", only=["coverage"],
                 want_notice=True)
    # Strict mode (what TestSurfaces asserts on the live table) stays clean with an unpromoted
    # entry: no errors, no warnings, --check exits 0 and still prints the notice.
    table = _fixture_base()
    with tempfile.TemporaryDirectory(prefix="render-shims-st-") as tmp:
        root = Path(tmp)
        _write_fixture_root(root, table, render=True)
        ready(table)
        (root / TABLE_REL).write_text(canonical(table), encoding="utf-8")
        strict = check(root, only=["coverage"], pending_ok=False)
        results.append(("an unpromoted entry keeps strict mode clean (no errors, no warnings)",
                        strict["errors"] == [] and strict["warnings"] == [] and len(strict["notices"]) == 1,
                        f"errors={strict['errors']} warnings={strict['warnings']} notices={strict['notices']}"))
        for as_json in (False, True):
            out = io.StringIO()
            saved, sys.stdout = sys.stdout, out
            try:
                rc = main(["--check", "--only", "coverage", "--root", str(root)] + (["--json"] if as_json else []))
            finally:
                sys.stdout = saved
            text = out.getvalue()
            if as_json:
                try:
                    rep = json.loads(text)
                    shown = rep.get("warnings") == [] and len(rep.get("notices") or []) == 1
                except ValueError:
                    shown = False
            else:
                shown = "NOTICE coverage: cursor.H19: not promoted" in text and "WARN" not in text
            results.append((f"--check{' --json' if as_json else ''} exits 0 and prints the notice outside warnings",
                            rc == 0 and shown, f"rc={rc} out={text[-400:]!r}"))
    _mutate_case(results, "planned refs with one unresolved probe record do not warn",
                 lambda t: cursor_h19(t).__setitem__("planned_verified_by", ["fixture:TestFixtureOk", "probe:cursor@dev-a"]),
                 "", only=["coverage"], want_clean=True)

    def promoted(t):
        cursor_h19(t).update(mode="enforced-partial", verified_by=["fixture:TestFixtureOk"], planned_verified_by=[])
    _mutate_case(results, "a promoted entry (refs moved, mode raised) does not warn", promoted, "",
                 only=["coverage"], want_clean=True)

    def held_back(t):
        cursor_h19(t).update(mode="unverified", verified_by=["fixture:TestFixtureOk"], planned_verified_by=[],
                             how="enforced-when-installed once the lane installer ships")
    _mutate_case(results, "an entry held back by a named non-ref condition does not warn", held_back, "",
                 only=["coverage"], want_clean=True)
    _mutate_case(results, "a verified_by ref on a non-enforced entry must resolve",
                 lambda t: next(s for s in t["surfaces"] if s["id"] == "claude-chat")["coverage"]["H16"]
                 .__setitem__("verified_by", ["fixture:TestNope"]),
                 "claude-chat.H16: fixture:TestNope does not resolve", only=["coverage"])

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
    results += guard_table_cases()

    results += beacon_cases()
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


def guard_table_cases() -> list:
    """H15 table rules: R1/R3/R6 never report-only, overrides only raise, the matcher token expands."""
    results = []
    good = {"tool_families": [{"id": "shell", "kind": "shell", "claude_matcher": ["Bash", "mcp__t__run"]},
                              {"id": "w", "kind": "file", "claude_matcher": ["Write", "Bash"]}],
            "wall_guard": {"rules": {"R1": "enforce", "R2": "report", "R3": "enforce", "R6": "enforce"},
                           "host_overrides": {"cursor": {"R2": "enforce"}}}}
    results.append(("guard tables: a well-formed table is clean", check_guard_tables(good) == [],
                    str(check_guard_tables(good))))
    relaxed = json.loads(json.dumps(good))
    relaxed["wall_guard"]["rules"]["R6"] = "report"
    relaxed["wall_guard"]["host_overrides"]["cursor"]["R3"] = "report"
    errs = check_guard_tables(relaxed)
    results.append(("guard tables: R6 report-only and an override that relaxes both fail",
                    any("R6" in e for e in errs) and any("only raises" in e for e in errs), str(errs)))
    dup = {"tool_families": [{"id": "a", "kind": "shell"}, {"id": "a", "kind": "teleport"}]}
    errs = check_guard_tables(dup)
    results.append(("guard tables: duplicate id and unknown kind fail",
                    any("duplicate" in e for e in errs) and any("invalid kind" in e for e in errs), str(errs)))
    m = expand_matcher(good, "@tool_families:claude")
    results.append(("matcher token expands in table order without duplicates", m == "Bash|mcp__t__run|Write", m))
    try:
        expand_matcher({"tool_families": []}, "@tool_families:claude")
        results.append(("an empty matcher expansion is a data error", False, "no DataError"))
    except DataError:
        results.append(("an empty matcher expansion is a data error", True, ""))
    return results


def beacon_cases() -> list:
    """H6: beacons render from beacons.json; drift, a size over max_bytes and a family the
    surface table does not declare all fail --check."""
    results = []
    fam = next(iter(_fixture_base()["families"]))
    beacons = {"blocks": {"open": ["<!-- WORKSPACE-BEACON v3 · {variant} -->"], "rules": ["- rule"]},
               "family_rules": {fam: f"- {fam}: personal-only"},
               "variants": {"fx": {"parts": ["open", "rules", "family_rules"], "families": [fam],
                                   "max_bytes": 200}}}
    row = {"id": "fx-beacon", "path": "out/beacon.md", "layer": None, "owned_keys": ["whole-file"],
           "install_path": None, "install_mode": "whole-file", "surface": None, "probe": False,
           "render": "beacon", "beacon": "fx"}

    def run(name, mutate_beacons=None, post=None, needle="", clean=False):
        table = _fixture_base()
        table["outputs"].append(dict(row))
        with tempfile.TemporaryDirectory(prefix="render-shims-beacon-") as tmp:
            root = Path(tmp)
            (root / "02-shared-references").mkdir(parents=True, exist_ok=True)
            (root / BEACONS_REL).write_text(json.dumps(beacons), encoding="utf-8")
            _write_fixture_root(root, table, render=True)
            if mutate_beacons:
                b = json.loads(json.dumps(beacons))
                mutate_beacons(b)
                (root / BEACONS_REL).write_text(json.dumps(b), encoding="utf-8")
            if post:
                post(root)
            res = check(root, only=["outputs"])
            text = (root / "out" / "beacon.md").read_text(encoding="utf-8")
        if clean:
            ok = not res["errors"] and text.startswith("<!-- WORKSPACE-BEACON v3 · fx -->")
        else:
            ok = any(needle in e for e in res["errors"])
        results.append((name, ok, f"errors={res['errors']}"))

    run("beacon renders from beacons.json and checks clean", clean=True)
    run("hand-edited beacon is drift", post=lambda r: (r / "out" / "beacon.md").write_text("x\n"),
        needle="drift in out/beacon.md")
    run("beacon over max_bytes fails", lambda b: b["variants"]["fx"].__setitem__("max_bytes", 10),
        needle="over max_bytes 10")
    for name, contract, needle in (
            ("contract-core over the rule limit fails", "## Keep\n" + "x" * 50 + "\n", "over the 40 rule limit"),
            ("contract-core with a missing section fails", "## Other\nbody\n", "heading not found")):
        table = _fixture_base()
        table["outputs"].append({"id": "fx-core", "path": "out/core.md", "layer": None, "owned_keys": ["whole-file"],
                                 "install_path": None, "install_mode": "tracked", "surface": None, "probe": False,
                                 "render": "contract-core", "max_chars": 40, "sections": [{"heading": "## Keep"}]})
        with tempfile.TemporaryDirectory(prefix="render-shims-core-") as tmp:
            root = Path(tmp)
            (root / "02-shared-references").mkdir(parents=True, exist_ok=True)
            (root / BEACONS_REL).write_text(json.dumps(beacons), encoding="utf-8")
            (root / CONTRACT_REL).write_text(contract, encoding="utf-8")
            _write_fixture_root(root, _fixture_base(), render=True)
            (root / TABLE_REL).write_text(canonical(table), encoding="utf-8")
            res = check(root, only=["outputs"])
        results.append((name, any(needle in e for e in res["errors"]), f"errors={res['errors']}"))
    with tempfile.TemporaryDirectory(prefix="render-shims-core-") as tmp:
        root = Path(tmp)
        (root / CONTRACT_REL).write_text("## A\n- **Keep** see [x](02-y/z.md)\n  more\n- other\n---\n## B\nno\n",
                                         encoding="utf-8")
        got = render_contract_core({"path": ".w/r/core.md", "sections": [{"heading": "## A", "bullet": "**Keep"}]},
                                   root)
        results.append(("contract-core keeps the bullet verbatim, drops the rest, re-roots links",
                        "- **Keep** see [x](../../02-y/z.md)\n  more\n" in got and "other" not in got
                        and "trigger: always_on" in got, got[-200:]))
    run("beacon family not in surfaces.json fails",
        lambda b: b["variants"]["fx"].__setitem__("families", ["martian"]),
        needle="family 'martian' is not a key of surfaces.json families")
    return results


IDENTITY_FIXTURES_REL = "09-tools/fixtures/identity"
V4_REV = "2ff02e7"          # the commit that carries the installed v4 overlay (read-only history)


def _git_show(rev_path: str):
    try:
        r = _git(ROOT, "show", rev_path, check_rc=False)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout if r.returncode == 0 else None


def rewrite_audit_cases(cr: dict, dev: dict) -> list:
    """H17-R9 audit cases on the synthetic tables: pure entries, then one real git read of a temp
    user config with a planted command-scope entry that must be ignored."""
    results = []
    blocked = cr["blocked_scheme"]
    pre = "git@github.com:acme-corp/"
    entries = [("global", "url.alias://.insteadof", pre),                                   # tie
               ("local", f"url.{pre}w.git.insteadof", f"{pre}w.git"),                        # longer
               ("system", "url.https://github.com/.pushinsteadof", "git@github.com:"),       # push, shorter
               ("global", f"url.{pre}.insteadof", "work:"),                                  # onto employer
               ("command", "url.alias://.insteadof", pre),                                  # the overlay / -c
               ("global", "url.alias://.insteadof", "git@github.com:"),                      # shorter: block wins
               ("global", "url.https://github.com/pat-sample/.insteadof", "git@github.com:pat-sample/"),
               ("global", f"url.{blocked}.insteadof", "git@github.com:other/")]
    hits = rewrite_conflicts(cr, dev, entries)
    got = [(s, k) for s, k, _v, _w in hits]
    results.append(("rewrite audit: a file-scope insteadOf that ties with or beats a blocked prefix is reported",
                    got[:2] == [("global", "url.alias://.insteadof"), ("local", f"url.{pre}w.git.insteadof")],
                    str(got)))
    results.append(("rewrite audit: a file-scope pushInsteadOf that overlaps a blocked prefix is reported, "
                    "and so is a rewrite onto an employer URL",
                    got[2:] == [("system", "url.https://github.com/.pushinsteadof"), ("global", f"url.{pre}.insteadof")],
                    str(got)))
    with tempfile.TemporaryDirectory() as td:
        home = Path(td)
        (home / ".gitconfig").write_text(
            f'[url "alias://"]\n\tinsteadOf = {pre}\n[url "https://github.com/pat-sample/"]\n'
            '\tinsteadOf = git@github.com:pat-sample/\n', encoding="utf-8")
        over = {"HOME": str(home), "XDG_CONFIG_HOME": str(home / "xdg"), "GIT_CONFIG_SYSTEM": os.devnull,
                "GIT_CONFIG_GLOBAL": None, "GIT_CONFIG_NOSYSTEM": None, "GIT_DIR": None,
                "GIT_CEILING_DIRECTORIES": str(home.parent),
                "GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "url.cmd://.insteadOf", "GIT_CONFIG_VALUE_0": pre}
        try:
            read = _config_rewrites(home, over)
            real = rewrite_conflicts(cr, dev, read)
            ok = (("global", "url.alias://.insteadof", pre) in read and not any(k.startswith("url.cmd:") for _s, k, _v in read)
                  and [(s, k) for s, k, _v, _w in real] == [("global", "url.alias://.insteadof")])
            detail = f"read={read} hits={real}"
        except (DataError, OSError, subprocess.SubprocessError) as exc:
            ok, detail = False, str(exc)
    results.append(("rewrite audit: command-scope entries, shorter insteadOf values and unrelated rewrites are not "
                    "reported", ok and len(hits) == 4, detail))
    own = rewrite_conflicts(cr, dev, [("global", f"url.{blocked}.insteadof", f"{pre}w.git")])
    results.append(("rewrite audit: the block's own rewrite in a config file is not reported", own == [], str(own)))
    results += _rewrite_audit_cli_cases(cr, dev, pre)
    return results


def _rewrite_audit_cli_cases(cr: dict, dev: dict, pre: str) -> list:
    """The --rewrite-audit CLI the doctor runs: its exit codes (0 clean, 1 finding, 2 unavailable), the
    --json envelope, the $HOME default, and a non-UTF-8 byte in an unrelated rewrite."""
    results = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        root = tmp / "root"
        pr = _pr_module()
        for name, data in (("context-remotes", cr), ("devices", dev)):
            dst = root / pr.TABLE_PATHS[name]
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(json.dumps(data), encoding="utf-8")
        home = tmp / "home"
        home.mkdir()
        repo = tmp / "repo"
        env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_CONFIG", "GIT_DIR"))}
        env.update(HOME=str(home), XDG_CONFIG_HOME=str(home / "xdg"), GIT_CONFIG_NOSYSTEM="1",
                   GIT_CEILING_DIRECTORIES=str(tmp))
        subprocess.run(["git", "init", "-q", str(repo)], env=env, capture_output=True, timeout=20)
        subprocess.run(["git", "config", "url.alias://.insteadOf", pre], cwd=str(repo), env=env,
                       capture_output=True, timeout=20)

        def cli(*extra: str, cwd: Path = tmp) -> subprocess.CompletedProcess:
            return subprocess.run([sys.executable, str(Path(__file__).resolve()), "--rewrite-audit", "--root", str(root),
                                   *extra], cwd=str(cwd), env=env, capture_output=True, text=True, timeout=60)

        clean = cli(cwd=repo)
        results.append(("rewrite audit CLI: clean user files exit 0 with the ok line, and a rewrite in the current "
                        "repo is not read (the audit runs from $HOME)",
                        clean.returncode == 0 and "ok render_shims rewrite-audit" in clean.stdout,
                        f"rc={clean.returncode} {clean.stdout[-200:]} {clean.stderr[-200:]}"))
        (home / ".gitconfig").write_bytes(f'[url "alias://"]\n\tinsteadOf = {pre}\n'.encode())
        hit = cli()
        js = cli("--json")
        try:
            env_ok = [f["key"] for f in json.loads(js.stdout)["findings"]] == ["url.alias://.insteadof"]
        except (ValueError, KeyError, TypeError):
            env_ok = False
        results.append(("rewrite audit CLI: a planted user-file rewrite exits 1 with a WARN line and a --json finding",
                        hit.returncode == 1 and "WARN  global: url.alias://.insteadof" in hit.stdout
                        and js.returncode == 1 and env_ok, f"rc={hit.returncode}/{js.returncode} {hit.stdout[-200:]}"))
        (home / ".gitconfig").write_bytes(b'[url "alias://"]\n\tinsteadOf = git@example.invalid:caf\xe9/\n')
        odd = cli()
        results.append(("rewrite audit CLI: a non-UTF-8 byte in an unrelated rewrite never reads as a finding",
                        odd.returncode in (0, 2), f"rc={odd.returncode} {odd.stderr[-200:]}"))
        (root / pr.TABLE_PATHS["devices"]).write_text("{not json", encoding="utf-8")
        bad = cli()
        results.append(("rewrite audit CLI: unreadable tables exit 2 (unavailable)", bad.returncode == 2,
                        f"rc={bad.returncode} {bad.stderr[-200:]}"))
    return results


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
    inc = [k for k, v in pairs if k.startswith("includeIf.hasconfig:remote.*.url:") and v == OVERLAY_INCLUDE]
    want_inc = {f"includeIf.hasconfig:remote.*.url:{p}.path" for p in (
        "git@github.com:pat-sample/**", "git@github-work:pat-sample/**", "https://github.com/pat-sample/**",
        "ssh://git@github.com/pat-sample/**")}
    results.append(("overlay: personal includes equal personal owners x forms", set(inc) == want_inc and len(inc) == 4,
                    str(inc)))
    ni = [k for k, v in pairs if k.startswith("includeIf.hasconfig:remote.*.url:") and v == OVERLAY_NOIDENT]
    last_personal = max(i for i, (k, v) in enumerate(pairs) if v == OVERLAY_INCLUDE)
    first_ni = min((i for i, (k, v) in enumerate(pairs) if v == OVERLAY_NOIDENT), default=-1)
    want_ni = {f"includeIf.hasconfig:remote.*.url:{w}**.path" for w in want}
    results.append(("overlay: every employer block form also gets the no-identity include, after the personal ones",
                    set(ni) == want_ni and first_ni > last_personal, f"missing={sorted(want_ni - set(ni))[:3]}"))
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
    results += rewrite_audit_cases(cr, dev)
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
    t["outputs"] = [{"id": "h", "install_mode": "claude-settings-keys", "render": "hooks", "overlay": "v5"},
                    {"id": "e", "install_mode": "whole-file", "render": "claude-overlay-env", "overlay": "v5",
                     "install_path": "~/.config/snds-workspace/claude-overlay.env"}]
    errs = check_table(t)
    results.append(("outputs: the overlay sits only on the env-file output, which shims never install (D-W1-4)",
                    any(e.startswith("output h: overlay must be one of") for e in errs)
                    and any(e.startswith("output e: the overlay env file") for e in errs), str(errs)))
    results += overlay_env_file_cases(cr, dev)
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
                  and render_claude_identity_inc(rdev, "v4") == old_inc)
            results.append(("overlay: v4 env and claude-identity.inc reproduced byte-for-byte from the tables", ok, ""))
        except (DataError, ValueError) as exc:
            results.append(("overlay: v4 env and claude-identity.inc reproduced byte-for-byte from the tables", False,
                            str(exc)))
    return results


def _load_module(name: str, path: Path):
    import importlib.util  # noqa: PLC0415
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def overlay_env_file_cases(cr: dict, dev: dict) -> list:
    """D-W1-4: the env file carries exactly the v5 overlay plus the channel marker, passes the ws-hook
    env-file parser, and after the hook's home rendering equals what the settings installer wrote."""
    results = []
    text = render_overlay_env_file(cr, dev, "v5")
    pairs = overlay_env_file_pairs(cr, dev, "v5")
    env = overlay_env(cr, dev, "v5")
    results.append(("overlay env file: the v5 pairs plus WS_OVERLAY_CHANNEL=env-file, nothing else",
                    dict(pairs) == dict(env, WS_OVERLAY_CHANNEL="env-file") and len(pairs) == len(env) + 1
                    and text.count(OVERLAY_ENV_BEGIN) == 1 and text.endswith(OVERLAY_ENV_END + "\n"), ""))
    try:
        wh = _load_module("ws_hook_for_render", ROOT / "09-tools" / "ws_hook.py")
        ms = _load_module("merge_settings_for_render", Path(__file__).resolve().parent / "merge_settings.py")
    except Exception as exc:  # noqa: BLE001
        return results + [("overlay env file: ws_hook and merge_settings load", False, str(exc))]
    try:
        parsed = wh.parse_overlay_env(text)
        results.append(("overlay env file: the ws-hook env-file parser reads every line back exactly",
                        parsed == pairs and wh.OVERLAY_BEGIN == OVERLAY_ENV_BEGIN and wh.OVERLAY_END == OVERLAY_ENV_END,
                        ""))
    except Exception as exc:  # noqa: BLE001
        results.append(("overlay env file: the ws-hook env-file parser reads every line back exactly", False, str(exc)))
        return results
    home = Path("/Users/fixture o'hare")
    hooked = {k: wh._expand_home(v, home) for k, v in parsed}
    settings = ms.expand_env_home({"env": dict(env)}, home)["env"]
    results.append(("overlay env file: the hook's ~/ and floor-home rendering equals the settings installer's",
                    {k: v for k, v in hooked.items() if k != "WS_OVERLAY_CHANNEL"} == settings, ""))
    with tempfile.TemporaryDirectory(prefix="rs-envfile-") as td:
        f = Path(td) / "block.sh"
        f.write_text(wh.overlay_block(parsed, home), encoding="utf-8")
        probe = [k for k in ("GH_CONFIG_DIR", "GIT_CONFIG_COUNT", "WS_OVERLAY_CHANNEL")]
        floor_i = next(i for i in range(int(env["GIT_CONFIG_COUNT"]))
                       if env[f"GIT_CONFIG_KEY_{i}"] == f"hook.{FLOOR_HOOK}.command")
        probe.append(f"GIT_CONFIG_VALUE_{floor_i}")
        script = f". '{f}'; " + "; ".join(f"printf '%s\\0' \"${k}\"" for k in probe)
        r = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=20)
        got = r.stdout.split("\0")[:-1]
        results.append(("overlay env file: the written block sources in bash to the installer's exact values",
                        got == [hooked[k] for k in probe], f"{got!r}"))
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
    for n in report.get("notices", []):
        print(f"NOTICE {n}")
    if not report.get("errors"):
        extra = [f"{len(report[k])} {k[:-1]}(s)" for k in ("warnings", "notices") if report.get(k)]
        print(f"ok render_shims {cmd}: clean" + (f" ({', '.join(extra)})" if extra else ""))


def emit(kind: str, root: Path = ROOT, *, device=None, overlay=None, out=None, home=None) -> int:
    """--emit identity-inc --device ID: that device's default identity include on stdout (exit 3 when
    the device has none). --emit overlay-env [--overlay v4|v5]: the overlay env JSON (read-only).
    --emit claude-permissions --device ID: that device's Claude permission rules (static + per device)."""
    out = out or sys.stdout
    try:
        if kind == "claude-permissions":
            if not device:
                print("usage: --emit claude-permissions --device ID", file=sys.stderr)
                return 2
            rules = render_claude_permissions(root, home=home)
            rules["device"] = device
            out.write(canonical(rules))
            return 0
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
    mode.add_argument("--emit", choices=["identity-inc", "overlay-env", "claude-permissions"])
    mode.add_argument("--rewrite-audit", action="store_true")
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
    if args.rewrite_audit:
        return rewrite_audit(root, as_json=args.json)
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
