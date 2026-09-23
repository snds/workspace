#!/usr/bin/env python3
"""profile_resolve — the declared resolver (H2): repo, device and surface facts from tables.

One home for: table loading, device and hostname resolution, remote normalization, owner
classes, repo walls (most restrictive of every source), the checkout cache, surface
detection and the agent check. Stdlib only; python3 3.9+. Nothing here is auto-loaded.

Usage:
  python3 09-tools/profile_resolve.py device [--hostname H] [--json]
  python3 09-tools/profile_resolve.py repo PATH|SLUG [--format json|classify] [--json]
  python3 09-tools/profile_resolve.py where SLUG [--no-rescan] [--json]
  python3 09-tools/profile_resolve.py scan [--report] [--depth 2] [--json]
  python3 09-tools/profile_resolve.py audit [--report] [--json]
  python3 09-tools/profile_resolve.py detect [--payload-hint HOST] [--json]
  python3 09-tools/profile_resolve.py agent-check [--json]
  python3 09-tools/profile_resolve.py gitcaps [--record] [--check-recorded] [--json]
  python3 09-tools/profile_resolve.py validate-tables [--require-all] [--json]
  python3 09-tools/profile_resolve.py --self-test [--stub-chain]

Exit codes: 0 ok; 1 deny/fail/drift or a positive negative determination; 2 usage or
undetermined; 3 not found / not on this device / SKIPPED; 4 refused.

`--root DIR` (a repo root with the standard layout) is for tests only. `scan` and `audit`
refuse under a Claude chain or any agent-possible env. `agent-check` tests fds 0 and 1: run
it with inherited stdio and never capture its stdout.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
FIXTURES = TOOLS / "fixtures" / "profile_resolve"
SCHEMA_VERSION = 1

EXIT_OK, EXIT_FAIL, EXIT_USAGE, EXIT_NOTFOUND, EXIT_REFUSED = 0, 1, 2, 3, 4

TABLE_PATHS: Dict[str, str] = {
    "surfaces": "02-shared-references/surfaces.json",
    "devices": "02-shared-references/devices.json",
    "context-remotes": "02-shared-references/delivery-playbooks/context-remotes.json",
    "action-policy": "02-shared-references/delivery-playbooks/action-policy.json",
    "vetted-scripts": "02-shared-references/vetted-scripts.json",
}

REMOTE_FORMS = ("scp", "scp-alias", "ssh", "https", "https-userinfo")
CLASS_RANK = {"personal": 0, "third-party": 1, "unknown": 2, "employer": 3}
REPO_ROLES = ("workspace", "personal", "third-party")
GIT_TIMEOUT_S = 4.0
PS_TIMEOUT_S = 0.5
SCUTIL_TIMEOUT_S = 1.0
AGENT_TRAILER_RE = re.compile(
    r"(?im)^co-authored-by:[^\n]*(claude|anthropic)|noreply@anthropic\.com|generated with \[?claude"
)

# Used only when surfaces.json is absent or unreadable, so refusals stay fail-closed. The table
# is the source of truth; these mirror its declared refusal inputs and nothing else.
_FALLBACK_SURFACES: Dict[str, Any] = {
    "families": {
        "claude": {"wall_rank": 100, "agent": True},
        "unknown-agent": {"wall_rank": 90, "agent": True},
        "human": {"wall_rank": 0, "agent": False},
    },
    "never_markers": ["CLAUDECODE", "CLAUDE_PROJECT_DIR", "CLAUDE_PLUGIN_ROOT", "CLAUDE_WORKSPACE_VAULT"],
    "agent_possible_env": {
        "names": ["CLAUDECODE", "CLAUDE_PROJECT_DIR", "CLAUDE_PLUGIN_ROOT", "CLAUDE_WORKSPACE_VAULT", "CLAUDE_ENV_FILE"],
        "prefixes": ["CLAUDE_CODE_"],
    },
    "surfaces": [
        {"id": "claude-code", "family": "claude", "markers": {"env": [], "ancestry": [
            {"comm": "claude", "match": "exact", "verified": False},
            {"comm": "Claude", "match": "exact", "verified": False},
            {"comm": "Claude Helper", "match": "prefix", "verified": False}]}},
    ],
}


class TableError(ValueError):
    """A declared table is missing, unreadable, or not a schema_version 1 object."""


class TableMissing(TableError):
    """The table file does not exist."""


# --------------------------------------------------------------------------- tables


def _root(root: Optional[Path]) -> Path:
    return Path(root) if root is not None else ROOT


def load_table(name: str, *, root: Optional[Path] = None) -> dict:
    """Load one declared table by stem. Raises TableError (TableMissing when absent)."""
    rel = TABLE_PATHS.get(name)
    if rel is None:
        raise TableError(f"unknown table {name!r}")
    path = _root(root) / rel
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise TableMissing(f"{name}: missing ({rel})") from exc
    except OSError as exc:
        raise TableError(f"{name}: unreadable ({exc.__class__.__name__})") from exc
    try:
        obj = json.loads(text)
    except ValueError as exc:
        raise TableError(f"{name}: invalid JSON ({exc})") from exc
    if not isinstance(obj, dict):
        raise TableError(f"{name}: top level is not an object")
    if obj.get("schema_version") != SCHEMA_VERSION or isinstance(obj.get("schema_version"), bool):
        raise TableError(f"{name}: schema_version must be {SCHEMA_VERSION}")
    return obj


def _try_table(name: str, root: Optional[Path]) -> Optional[dict]:
    try:
        return load_table(name, root=root)
    except TableError:
        return None


# Closed top-level key sets: key -> (types, required). Optional keys are required only
# under --require-all.
_STR = (str,)
_LIST = (list,)
_DICT = (dict,)
_BOOL = (bool,)
_INT = (int,)
_OPT_STR = (str, type(None))

TABLE_SCHEMAS: Dict[str, Dict[str, Tuple[tuple, bool]]] = {
    "surfaces": {
        "schema_version": (_INT, True), "doc": (_STR, True), "coverage_modes": (_LIST, True),
        "minimum_surfaces": (_LIST, True), "components": (_LIST, True), "families": (_DICT, True),
        "never_markers": (_LIST, True), "agent_possible_env": (_DICT, True),
        "probe_env_name_prefixes": (_LIST, True), "probe_env_value_allowlist": (_LIST, True),
        "surfaces": (_LIST, True), "formats": (_DICT, True), "dialects": (_DICT, True),
        "layers": (_LIST, True), "commands": (_DICT, True), "registrations": (_LIST, True),
        "outputs": (_LIST, True), "wrappers": (_DICT, True),
    },
    "devices": {
        "schema_version": (_INT, True), "doc": (_STR, True), "devices": (_LIST, True),
        "ssh_aliases": (_LIST, True), "identities": (_LIST, False), "personal_markers": (_DICT, False),
        "employer_allowlist": (_DICT, False), "identity_rules": (_LIST, False), "invariants": (_LIST, False),
    },
    "context-remotes": {
        "schema_version": (_INT, True), "doc": (_STR, True), "conduct_order": (_LIST, True),
        "owner_classes": (_LIST, True), "unknown_owner": (_DICT, True), "blocked_scheme": (_STR, True),
        "hosts": (_LIST, True), "owners": (_LIST, True), "repos": (_LIST, True),
        "employer_path_globs": (_LIST, True), "employer_substance": (_DICT, True),
    },
    "action-policy": {
        "schema_version": (_INT, True), "doc": (_STR, True), "action_classes": (_LIST, True),
        "outcomes": (_LIST, True), "undecided_evaluates_as": (_STR, True), "unknown_verb_class": (_STR, True),
        "default_outcome": (_STR, True), "route_targets": (_LIST, True), "verb_map": (_LIST, True),
        "rules": (_LIST, True),
    },
    "vetted-scripts": {
        "schema_version": (_INT, True), "doc": (_STR, True), "scripts": (_LIST, True),
    },
}

_WHEN_LIST_KEYS = ("walls_family", "acting_family", "device", "owner_class", "role", "action_class", "via", "target_ref")
_WHEN_BOOL_KEYS = ("chain_has_agent", "positively_personal", "under_projects_root", "has_remote", "repo_conflict", "hook_bypass")
_RULE_KEYS = ("id", "when", "outcome", "reason", "route_to", "receipt", "proposed", "note")


def _type_ok(value: Any, types: tuple) -> bool:
    if isinstance(value, bool) and bool not in types:
        return False
    return isinstance(value, types)


def _rows(obj: dict, key: str, errors: List[str]) -> List[dict]:
    out = []
    for i, row in enumerate(obj.get(key) or []):
        if not isinstance(row, dict):
            errors.append(f"{key}[{i}]: not an object")
            continue
        out.append(row)
    return out


def _check_row(row: dict, where: str, spec: Dict[str, Tuple[tuple, bool]], errors: List[str], closed: bool = True) -> None:
    for k, (types, required) in spec.items():
        if k not in row:
            if required:
                errors.append(f"{where}: missing key {k!r}")
            continue
        if not _type_ok(row[k], types):
            errors.append(f"{where}.{k}: wrong type")
    if closed:
        for k in row:
            if k not in spec:
                errors.append(f"{where}: unknown key {k!r}")


def _str_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(x, str) for x in value)


def _validate_devices(obj: dict, errors: List[str]) -> None:
    spec = {
        "id": (_STR, True), "label": (_STR, True), "hostnames": (_LIST, True), "hostname_labels": (_DICT, True),
        "os": (_STR, True), "home": (_STR, True), "projects_root": (_STR, True), "brain": (_STR, True),
        "default_identity": (_OPT_STR, True),
    }
    seen_ids: set = set()
    seen_hosts: Dict[str, str] = {}
    for i, row in enumerate(_rows(obj, "devices", errors)):
        where = f"devices[{i}]"
        _check_row(row, where, spec, errors)
        did = row.get("id")
        if did in seen_ids:
            errors.append(f"{where}: duplicate id {did!r}")
        seen_ids.add(did)
        if did == "unknown":
            errors.append(f"{where}: id 'unknown' is reserved")
        hosts = row.get("hostnames")
        if not _str_list(hosts):
            errors.append(f"{where}.hostnames: must be a list of strings")
            hosts = []
        for h in hosts:
            n = normalize_hostname(h)
            if n in seen_hosts and seen_hosts[n] != did:
                errors.append(f"{where}: hostname {h!r} also declared on {seen_hosts[n]!r}")
            seen_hosts[n] = did
        labels = row.get("hostname_labels") if isinstance(row.get("hostname_labels"), dict) else {}
        norm_hosts = {normalize_hostname(h) for h in hosts}
        for k, v in labels.items():
            if normalize_hostname(k) not in norm_hosts or not isinstance(v, str):
                errors.append(f"{where}.hostname_labels: {k!r} is not one of this device's hostnames")
        for k in ("projects_root", "brain"):
            v = row.get(k)
            if isinstance(v, str) and (v.startswith("/") or v.startswith("~") or ".." in Path(v).parts):
                errors.append(f"{where}.{k}: must be relative to home")
        home = row.get("home")
        if isinstance(home, str) and not home.startswith("/"):
            errors.append(f"{where}.home: must be absolute")
    alias_spec = {"alias": (_STR, True), "host": (_STR, True), "credential_scope": (_STR, True)}
    for i, row in enumerate(_rows(obj, "ssh_aliases", errors)):
        _check_row(row, f"ssh_aliases[{i}]", alias_spec, errors)


def _validate_context_remotes(obj: dict, errors: List[str]) -> None:
    conduct = obj.get("conduct_order") if _str_list(obj.get("conduct_order")) else []
    classes = obj.get("owner_classes") if _str_list(obj.get("owner_classes")) else []
    if not conduct:
        errors.append("conduct_order: must be a non-empty list of strings")
    if set(classes) != set(CLASS_RANK):
        errors.append(f"owner_classes: must be exactly {sorted(CLASS_RANK)}")
    uo = obj.get("unknown_owner") if isinstance(obj.get("unknown_owner"), dict) else {}
    _check_row(uo, "unknown_owner", {"conduct": (_STR, True), "claude_walls": (_STR, True)}, errors)
    if uo.get("conduct") not in conduct:
        errors.append("unknown_owner.conduct: not in conduct_order")
    if uo.get("claude_walls") not in classes:
        errors.append("unknown_owner.claude_walls: not in owner_classes")
    hosts_seen = set()
    host_spec = {"host": (_STR, True), "ssh_user": (_STR, True), "forms": (_LIST, True)}
    for i, row in enumerate(_rows(obj, "hosts", errors)):
        _check_row(row, f"hosts[{i}]", host_spec, errors)
        hosts_seen.add(str(row.get("host", "")).lower())
        for f in row.get("forms") or []:
            if f not in REMOTE_FORMS:
                errors.append(f"hosts[{i}].forms: unknown form {f!r}")
    owner_spec = {"host": (_STR, True), "owner": (_STR, True), "class": (_STR, True), "profile": (_STR, True)}
    for i, row in enumerate(_rows(obj, "owners", errors)):
        _check_row(row, f"owners[{i}]", owner_spec, errors)
        if row.get("class") not in classes:
            errors.append(f"owners[{i}].class: not in owner_classes")
        if row.get("profile") not in conduct:
            errors.append(f"owners[{i}].profile: not in conduct_order")
        if str(row.get("host", "")).lower() not in hosts_seen:
            errors.append(f"owners[{i}].host: not declared in hosts")
    repo_spec = {
        "slug": (_STR, True), "host": (_STR, True), "role": (_STR, True), "profile": (_STR, True),
        "visibility": (_STR, True), "beacon": (_BOOL, True), "vault_project": (_OPT_STR, True),
    }
    for i, row in enumerate(_rows(obj, "repos", errors)):
        _check_row(row, f"repos[{i}]", repo_spec, errors)
        if row.get("role") not in REPO_ROLES:
            errors.append(f"repos[{i}].role: must be one of {list(REPO_ROLES)}")
        if row.get("profile") not in conduct:
            errors.append(f"repos[{i}].profile: not in conduct_order")
        if str(row.get("slug", "")).count("/") < 1:
            errors.append(f"repos[{i}].slug: must be owner/repo")
    if not _str_list(obj.get("employer_path_globs")):
        errors.append("employer_path_globs: must be a list of strings")
    else:
        for g in obj["employer_path_globs"]:
            if g.startswith("/") or g.startswith("~"):
                errors.append(f"employer_path_globs: {g!r} must be relative to projects_root")
    es = obj.get("employer_substance") if isinstance(obj.get("employer_substance"), dict) else {}
    es_spec = {"allow_tokens": (_LIST, True), "url_prefixes": (_LIST, True), "domains": (_LIST, True), "count_keywords": (_LIST, True)}
    _check_row(es, "employer_substance", es_spec, errors)
    for k in es_spec:
        if k in es and not _str_list(es[k]):
            errors.append(f"employer_substance.{k}: must be a list of strings")


def _validate_surfaces(obj: dict, errors: List[str]) -> None:
    fams = obj.get("families") if isinstance(obj.get("families"), dict) else {}
    for name, row in fams.items():
        if not isinstance(row, dict) or not _type_ok(row.get("wall_rank"), _INT) or not _type_ok(row.get("agent"), _BOOL):
            errors.append(f"families.{name}: needs int wall_rank and bool agent")
    ids = set()
    for i, row in enumerate(_rows(obj, "surfaces", errors)):
        sid = row.get("id")
        if not isinstance(sid, str):
            errors.append(f"surfaces[{i}].id: must be a string")
        elif sid in ids:
            errors.append(f"surfaces[{i}]: duplicate id {sid!r}")
        ids.add(sid)
        if row.get("family") not in fams:
            errors.append(f"surfaces[{i}].family: not a key of families")
        markers = row.get("markers", {})
        if not isinstance(markers, dict):
            errors.append(f"surfaces[{i}].markers: must be an object")
            continue
        for m in markers.get("env") or []:
            if not isinstance(m, dict) or not isinstance(m.get("name"), str) or not _type_ok(m.get("verified", False), _BOOL):
                errors.append(f"surfaces[{i}].markers.env: needs name and bool verified")
        for m in markers.get("ancestry") or []:
            if not isinstance(m, dict) or not isinstance(m.get("comm"), str) or m.get("match", "exact") not in ("exact", "prefix"):
                errors.append(f"surfaces[{i}].markers.ancestry: needs comm and match exact|prefix")
    ape = obj.get("agent_possible_env") if isinstance(obj.get("agent_possible_env"), dict) else {}
    if not _str_list(ape.get("names", [])) or not _str_list(ape.get("prefixes", [])):
        errors.append("agent_possible_env: names and prefixes must be lists of strings")
    for k in ("never_markers", "minimum_surfaces", "components", "coverage_modes"):
        if k in obj and not _str_list(obj[k]):
            errors.append(f"{k}: must be a list of strings")


def _validate_action_policy(obj: dict, errors: List[str]) -> None:
    classes = obj.get("action_classes") if _str_list(obj.get("action_classes")) else []
    outcomes = obj.get("outcomes") if _str_list(obj.get("outcomes")) else []
    for k in ("undecided_evaluates_as", "default_outcome"):
        if obj.get(k) not in outcomes:
            errors.append(f"{k}: not in outcomes")
    if obj.get("unknown_verb_class") not in classes:
        errors.append("unknown_verb_class: not in action_classes")
    for i, row in enumerate(_rows(obj, "verb_map", errors)):
        if not isinstance(row.get("id"), str) or not isinstance(row.get("tool"), str):
            errors.append(f"verb_map[{i}]: needs id and tool")
        if row.get("class") not in classes:
            errors.append(f"verb_map[{i}].class: not in action_classes")
    for i, row in enumerate(_rows(obj, "rules", errors)):
        where = f"rules[{i}]"
        for k in row:
            if k not in _RULE_KEYS:
                errors.append(f"{where}: unknown key {k!r}")
        if row.get("outcome") not in outcomes:
            errors.append(f"{where}.outcome: not in outcomes")
        if "proposed" in row and row.get("outcome") != "undecided":
            errors.append(f"{where}: 'proposed' is only valid with outcome 'undecided'")
        when = row.get("when")
        if not isinstance(when, dict):
            errors.append(f"{where}.when: must be an object")
            continue
        for k, v in when.items():
            if k in _WHEN_LIST_KEYS:
                if not _str_list(v):
                    errors.append(f"{where}.when.{k}: must be a list of strings")
            elif k in _WHEN_BOOL_KEYS:
                if not isinstance(v, bool):
                    errors.append(f"{where}.when.{k}: must be a bool")
            else:
                errors.append(f"{where}.when: unknown key {k!r}")


def _validate_vetted_scripts(obj: dict, errors: List[str]) -> None:
    spec = {
        "id": (_STR, True), "path": (_STR, True), "action_classes": (_LIST, True), "actions": (_DICT, True),
        "needs_employer_gh": (_BOOL, True), "approved": (_STR, True),
    }
    for i, row in enumerate(_rows(obj, "scripts", errors)):
        _check_row(row, f"scripts[{i}]", spec, errors)
        p = row.get("path")
        if isinstance(p, str) and (p.startswith("/") or p.startswith("~")):
            errors.append(f"scripts[{i}].path: must be repo-relative")


_ROW_VALIDATORS: Dict[str, Callable[[dict, List[str]], None]] = {
    "surfaces": _validate_surfaces,
    "devices": _validate_devices,
    "context-remotes": _validate_context_remotes,
    "action-policy": _validate_action_policy,
    "vetted-scripts": _validate_vetted_scripts,
}


def validate_table(name: str, obj: dict, *, require_all: bool = False) -> List[str]:
    errors: List[str] = []
    schema = TABLE_SCHEMAS[name]
    for key in obj:
        if key not in schema:
            errors.append(f"unknown top-level key {key!r}")
    for key, (types, required) in schema.items():
        if key not in obj:
            if required or require_all:
                errors.append(f"missing key {key!r}" + ("" if required else " (optional until --require-all)"))
            continue
        if not _type_ok(obj[key], types):
            errors.append(f"{key}: wrong type")
    if obj.get("schema_version") != SCHEMA_VERSION or isinstance(obj.get("schema_version"), bool):
        errors.append(f"schema_version must be {SCHEMA_VERSION}")
    if not errors:
        _ROW_VALIDATORS[name](obj, errors)
    return errors


def validate_tables(*, root: Optional[Path] = None, require_all: bool = False) -> dict:
    tables: Dict[str, dict] = {}
    for name, rel in TABLE_PATHS.items():
        path = _root(root) / rel
        entry = {"ok": True, "present": path.exists(), "errors": []}
        if not entry["present"]:
            if require_all:
                entry["ok"] = False
                entry["errors"] = ["missing (required under --require-all)"]
            tables[name] = entry
            continue
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            entry.update(ok=False, errors=[f"unreadable or invalid JSON ({exc.__class__.__name__})"])
            tables[name] = entry
            continue
        if not isinstance(raw, dict):
            entry.update(ok=False, errors=["top level is not an object"])
        else:
            errs = validate_table(name, raw, require_all=require_all)
            entry.update(ok=not errs, errors=errs)
        tables[name] = entry
    return {"tables": tables}


# --------------------------------------------------------------------------- devices


def normalize_hostname(hostname: Optional[str]) -> str:
    """Short name (before the first '.'), case-folded. Absorbs .local / .lan drift."""
    return (hostname or "").strip().split(".", 1)[0].casefold()


def _raw_short(hostname: Optional[str]) -> str:
    return (hostname or "").strip().split(".", 1)[0]


def _default_scutil() -> Optional[str]:
    if sys.platform != "darwin":
        return None
    try:
        r = subprocess.run(["scutil", "--get", "LocalHostName"], capture_output=True, text=True, timeout=SCUTIL_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() or None if r.returncode == 0 else None


def _match_device(hostname: str, table: dict) -> Tuple[Optional[dict], Optional[str]]:
    n = normalize_hostname(hostname)
    if not n:
        return None, None
    for dev in table.get("devices") or []:
        if not isinstance(dev, dict):
            continue
        for h in dev.get("hostnames") or []:
            if normalize_hostname(h) == n:
                label = None
                for k, v in (dev.get("hostname_labels") or {}).items():
                    if normalize_hostname(k) == n:
                        label = v
                return dev, label or dev.get("label")
    return None, None


def _resolve_device(hostname: Optional[str], root: Optional[Path], scutil: Optional[Callable[[], Optional[str]]]) -> dict:
    explicit = hostname is not None
    raw = hostname if explicit else socket.gethostname()
    out: Dict[str, Any] = {"row": None, "label": _raw_short(raw) or "unknown", "raw": _raw_short(raw), "notice": None}
    table = _try_table("devices", root)
    if table is None:
        out["notice"] = "devices table unavailable: unknown device, most restrictive rules"
        return out
    dev, label = _match_device(raw, table)
    if dev is None:
        probe = scutil if scutil is not None else (None if explicit else _default_scutil)
        if probe is not None:
            try:
                alt = probe()
            except Exception:  # noqa: BLE001 - an injected or real probe must never raise out
                alt = None
            if alt:
                dev, label = _match_device(alt, table)
    if dev is None:
        out["notice"] = (
            f"unknown host {out['raw'] or '?'}: most restrictive rules, no default identity "
            "(declare it in 02-shared-references/devices.json)"
        )
        return out
    out.update(row=dev, label=label)
    return out


def current_device(*, hostname: Optional[str] = None, root: Optional[Path] = None,
                   scutil: Optional[Callable[[], Optional[str]]] = None) -> dict:
    """{id, label, projects_root, brain, hostname_known, notice}; unknown gives id 'unknown'.

    scutil (LocalHostName) is consulted on a miss: the injected callable when given, the real
    one only when the hostname was not supplied explicitly.
    """
    r = _resolve_device(hostname, root, scutil)
    home = Path.home()
    row = r["row"]
    if row is None:
        return {"id": "unknown", "label": r["label"], "projects_root": str(home / "Projects"), "brain": None,
                "hostname_known": False, "notice": r["notice"]}
    return {"id": row.get("id"), "label": r["label"], "projects_root": str(home / row.get("projects_root", "Projects")),
            "brain": str(home / row.get("brain", "")), "hostname_known": True, "notice": None}


def device_label(hostname: Optional[str] = None, *, root: Optional[Path] = None) -> str:
    """Hostname label, else device label, else the raw short hostname. Never raises."""
    try:
        r = _resolve_device(hostname, root, None)
        return str(r["label"] or r["raw"] or "unknown")
    except Exception:  # noqa: BLE001
        try:
            return _raw_short(hostname if hostname is not None else socket.gethostname()) or "unknown"
        except Exception:  # noqa: BLE001
            return "unknown"


def projects_root(*, root: Optional[Path] = None, home: Optional[Path] = None) -> Path:
    h = Path(home) if home is not None else Path.home()
    try:
        row = _resolve_device(None, root, None)["row"]
    except Exception:  # noqa: BLE001
        row = None
    rel = (row or {}).get("projects_root") or "Projects"
    return h / rel


def ws_paths(*, home: Optional[Path] = None) -> dict:
    h = Path(home) if home is not None else Path.home()
    base = h / ".config" / "snds-workspace"
    return {
        "base": base, "root_file": base / "root", "bin": base / "bin",
        "lib_current": base / "lib" / "current", "control": base / "control", "telemetry": base / "telemetry",
    }


# --------------------------------------------------------------------------- remotes

_SCHEME_RE = re.compile(r"^(?P<scheme>[A-Za-z][A-Za-z0-9+.-]*)://(?P<rest>.*)$")
_SCP_RE = re.compile(r"^(?:(?P<user>[^@/\s:]+)@)?(?P<host>[A-Za-z0-9._-]+):(?P<path>[^\s]+)$")


def _ssh_aliases(root: Optional[Path]) -> Dict[str, dict]:
    table = _try_table("devices", root) or {}
    out = {}
    for row in table.get("ssh_aliases") or []:
        if isinstance(row, dict) and isinstance(row.get("alias"), str):
            out[row["alias"].casefold()] = row
    return out


def _normalize_remote_ex(url: str, *, root: Optional[Path] = None) -> Tuple[Optional[dict], Optional[dict]]:
    """(normalized, alias_row). Never returns userinfo; a raw URL never leaves this function."""
    u = (url or "").strip().strip("\"'")
    if not u:
        return None, None
    m = _SCHEME_RE.match(u)
    if m:
        scheme = m.group("scheme").lower()
        auth, _, path = m.group("rest").partition("/")
        userinfo = ""
        if "@" in auth:
            userinfo, _, auth = auth.rpartition("@")
        host = auth
        if host.startswith("["):
            return None, None
        if ":" in host:
            host = host.split(":", 1)[0]
        if scheme in ("https", "http"):
            form = "https-userinfo" if userinfo else "https"
        elif scheme in ("ssh", "git+ssh", "ssh+git"):
            form = "ssh"
        else:
            return None, None
    else:
        if u.startswith(("/", ".", "~")) or "\\" in u:
            return None, None
        m = _SCP_RE.match(u)
        if not m:
            return None, None
        host, path, form = m.group("host"), m.group("path"), "scp"
    host = host.lower()
    alias_row = _ssh_aliases(root).get(host.casefold())
    if alias_row is not None:
        host = str(alias_row.get("host", host)).lower()
        if form == "scp":
            form = "scp-alias"
    path = path.split("?", 1)[0].split("#", 1)[0].strip("/")
    if path.endswith(".git"):
        path = path[:-4]
    parts = [p for p in path.split("/") if p and p not in (".", "..")]
    if len(parts) < 2 or not host:
        return None, None
    owner = parts[0].casefold()
    repo = "/".join(parts[1:]).casefold()
    return {"host": host, "owner": owner, "repo": repo, "slug": f"{owner}/{repo}", "form": form}, alias_row


def normalize_remote(url: str, *, root: Optional[Path] = None) -> Optional[dict]:
    """{host, owner, repo, slug, form} with owner and repo case-folded; never carries userinfo."""
    return _normalize_remote_ex(url, root=root)[0]


def owner_class(host: str, owner: str, *, root: Optional[Path] = None) -> str:
    """employer | personal | third-party | unknown (unlisted owners are unknown)."""
    table = _try_table("context-remotes", root)
    if table is None:
        return "unknown"
    return _owner_row_class(table, host, owner)[0]


def _owner_row_class(table: dict, host: str, owner: str) -> Tuple[str, Optional[dict]]:
    h, o = (host or "").lower(), (owner or "").casefold()
    for row in table.get("owners") or []:
        if isinstance(row, dict) and str(row.get("host", "")).lower() == h and str(row.get("owner", "")).casefold() == o:
            cls = row.get("class")
            return (cls if cls in CLASS_RANK else "unknown"), row
    return "unknown", None


def _read_git_config_remotes(top: Path) -> Tuple[List[Tuple[str, str]], Optional[str]]:
    """[(remote name, url)] from the checkout's git config file. Reads only config files."""
    gitp = top / ".git"
    try:
        if gitp.is_dir():
            cfg = gitp / "config"
        elif gitp.is_file():
            first = gitp.read_text(encoding="utf-8", errors="replace").splitlines()[0].strip()
            if not first.startswith("gitdir:"):
                return [], "gitfile-unparsed"
            gd = Path(first[len("gitdir:"):].strip())
            if not gd.is_absolute():
                gd = (top / gd)
            common = gd
            cd = gd / "commondir"
            if cd.is_file():
                c = Path(cd.read_text(encoding="utf-8", errors="replace").strip())
                common = c if c.is_absolute() else (gd / c)
            cfg = common / "config"
        else:
            return [], "not-a-repo"
        text = cfg.read_text(encoding="utf-8", errors="replace")
    except (OSError, IndexError):
        return [], "config-unreadable"
    out: List[Tuple[str, str]] = []
    section = None
    for line in text.splitlines():
        s = line.strip()
        if not s or s[0] in "#;":
            continue
        if s.startswith("["):
            m = re.match(r'^\[\s*remote\s+"([^"]+)"\s*\]', s, re.I)
            section = m.group(1) if m else None
            continue
        if section is None or "=" not in s:
            continue
        k, _, v = s.partition("=")
        if k.strip().lower() in ("url", "pushurl"):
            v = v.strip()
            if len(v) >= 2 and v[0] == v[-1] == '"':
                v = v[1:-1]
            out.append((section, v))
    return out, None


def _remotes_from_urls(pairs: List[Tuple[str, str]], root: Optional[Path]) -> List[dict]:
    seen = set()
    out = []
    for name, url in pairs:
        norm, alias = _normalize_remote_ex(url, root=root)
        if norm is None:
            entry = {"name": name, "host": None, "owner": None, "slug": None, "form": "unparsed", "_alias": None}
        else:
            entry = {"name": name, "host": norm["host"], "owner": norm["owner"], "slug": norm["slug"], "form": norm["form"],
                     "_alias": alias}
        key = (entry["name"], entry["host"], entry["slug"], entry["form"])
        if key in seen:
            continue
        seen.add(key)
        out.append(entry)
    return out


# --------------------------------------------------------------------------- paths


def _real(p: Any) -> Path:
    return Path(os.path.realpath(os.path.expanduser(str(p))))


def _cf(p: Any) -> str:
    return str(p).rstrip("/").casefold() or "/"


def _is_under(path: Any, base: Any) -> bool:
    pc, bc = _cf(path), _cf(base)
    return pc == bc or pc.startswith(bc + "/")


def _workspace_roots(root: Optional[Path], home: Optional[Path]) -> List[Path]:
    cands = [_root(root)]
    try:
        lines = ws_paths(home=home)["root_file"].read_text(encoding="utf-8").splitlines()
        if lines and lines[0].strip():
            cands.append(Path(lines[0].strip()).expanduser())
    except OSError:
        pass
    out: List[Path] = []
    for c in cands:
        try:
            if (c / "AGENTS.md").is_file():
                rc = _real(c)
                if all(_cf(rc) != _cf(x) for x in out):
                    out.append(rc)
        except OSError:
            continue
    return out


def _workspace_kind(path: Any, root: Optional[Path], home: Optional[Path]) -> Optional[Tuple[str, Path]]:
    p = _real(path)
    for ws in _workspace_roots(root, home):
        if _is_under(p, ws):
            return "workspace-root", ws
        parent = ws.parent
        if not _is_under(p, parent) or _cf(p) == _cf(parent):
            continue
        first = p.parts[len(parent.parts)]
        if not first.casefold().startswith(ws.name.casefold() + ".intent-"):
            continue
        gitfile = parent / first / ".git"
        try:
            if not gitfile.is_file():
                continue
            line = gitfile.read_text(encoding="utf-8", errors="replace").splitlines()[0].strip()
        except (OSError, IndexError):
            continue
        if not line.startswith("gitdir:"):
            continue
        gd = Path(line[len("gitdir:"):].strip())
        if not gd.is_absolute():
            gd = parent / first / gd
        if _is_under(_real(gd), ws / ".git" / "worktrees"):
            return "linked-worktree", ws
    return None


def is_workspace_checkout(path: Any, *, root: Optional[Path] = None, home: Optional[Path] = None) -> bool:
    """True for the workspace root (AGENTS.md present) or a linked worktree whose .git points into it."""
    try:
        return _workspace_kind(path, root, home) is not None
    except Exception:  # noqa: BLE001
        return False


def _find_top(p: Path) -> Optional[Path]:
    cur = p
    for _ in range(64):
        try:
            if (cur / ".git").exists():
                return cur
        except OSError:
            return None
        if cur.parent == cur:
            return None
        cur = cur.parent
    return None


def _glob_hit(path: Path, pr: Path, globs: List[str]) -> Optional[str]:
    if not _is_under(path, pr) or _cf(path) == _cf(pr):
        return None
    rel_parts = path.parts[len(pr.parts):]
    for i in range(1, len(rel_parts) + 1):
        rel = "/".join(rel_parts[:i]).casefold()
        for g in globs:
            if fnmatch.fnmatchcase(rel, str(g).casefold()):
                return g
    return None


def _session_state_profile(root: Optional[Path], vault_project: str, conduct: List[str]) -> Optional[str]:
    path = _root(root) / "07-projects" / vault_project / "SESSION-STATE.md"
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    for line in text.splitlines():
        if "context profile" in line.casefold():
            for tok in re.findall(r"`([^`]+)`", line):
                if tok in conduct:
                    return tok
    return None


def _project_md_profile(top: Path, conduct: List[str]) -> Optional[str]:
    try:
        lines = (top / "PROJECT.md").read_text(encoding="utf-8", errors="replace").splitlines()[:80]
    except OSError:
        return None
    for line in lines:
        m = re.match(r"^\s*profile\s*:\s*[`\"']?([A-Za-z0-9_-]+)", line)
        if m and m.group(1) in conduct:
            return m.group(1)
    return None


# --------------------------------------------------------------------------- cache


def _cache_path(home: Optional[Path]) -> Path:
    return ws_paths(home=home)["telemetry"] / "checkouts.json"


def _load_cache(cache: Any, home: Optional[Path]) -> Optional[dict]:
    if isinstance(cache, dict):
        return cache
    path = Path(cache) if cache is not None else _cache_path(home)
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(obj, dict) or not isinstance(obj.get("checkouts"), list):
        return None
    return obj


def _cache_lookup(p: Path, cache: Optional[dict]) -> Optional[dict]:
    if not cache:
        return None
    best = None
    for c in cache.get("checkouts") or []:
        cp = c.get("path") if isinstance(c, dict) else None
        if isinstance(cp, str) and _is_under(p, cp):
            if best is None or len(cp) > len(best["path"]):
                best = c
    return best


def _age_s(generated_at: Any) -> Optional[int]:
    if not isinstance(generated_at, str):
        return None
    try:
        dt = datetime.strptime(generated_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return max(0, int((datetime.now(timezone.utc) - dt).total_seconds()))


def _now_z() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------- repo walls


def _restricted(det: dict, root: Optional[Path]) -> bool:
    if det.get("family_for_walls") in ("claude", "unknown-agent"):
        return True
    if "agent_possible" in det:
        return bool(det["agent_possible"])
    return bool(_agent_possible_names(os.environ, _surfaces_or_fallback(root)))


def _conduct_max(conduct: List[str], *profiles: Optional[str]) -> str:
    best = None
    for p in profiles:
        if p in conduct and (best is None or conduct.index(p) > conduct.index(best)):
            best = p
    return best or (conduct[-1] if conduct else "centric-engineering")


def _looks_like_slug(s: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", s)) and not s.startswith((".", "~")) and not os.path.exists(s)


def _resolve(path_or_slug: str, *, root: Optional[Path], home: Optional[Path], detection: Optional[dict],
             cache: Any) -> Tuple[dict, str]:
    table = _try_table("context-remotes", root)
    conduct = list((table or {}).get("conduct_order") or ["personal-solo", "centric-design", "centric-engineering"])
    unknown_conduct = ((table or {}).get("unknown_owner") or {}).get("conduct") or conduct[-1]
    res: Dict[str, Any] = {
        "path": None, "in_projects_root": False, "source": "none", "remotes": [], "owner_class": "unknown",
        "role": "unknown", "profile": unknown_conduct, "positively_personal": False, "conflict": False,
        "conflicts": [], "reasons": [],
    }
    if table is None:
        res["reasons"].append("context-remotes table unavailable: not positively personal")
        return res, "path"
    det = detection if detection is not None else detect_surface(root=root)
    restricted = _restricted(det, root)
    s = (path_or_slug or "").strip()
    remotes: List[dict] = []
    top: Optional[Path] = None
    kind = "path"
    ws_kind = None
    pr = projects_root(root=root, home=home)
    if "://" in s or (not os.path.exists(s) and _SCP_RE.match(s) and not _looks_like_slug(s)):
        kind = "url"
        remotes = _remotes_from_urls([("url", s)], root)
    elif _looks_like_slug(s):
        kind = "slug"
        o, _, r = s.casefold().partition("/")
        remotes = [{"name": "slug", "host": None, "owner": o, "slug": f"{o}/{r}", "form": "slug", "_alias": None}]
        hit = None
        c = _load_cache(cache, home)
        for co in (c or {}).get("checkouts") or []:
            if any(isinstance(x, dict) and x.get("slug") == f"{o}/{r}" for x in co.get("remotes") or []):
                hit = co
                break
        if hit is not None:
            res["path"] = hit.get("path")
            res["source"] = "cache"
    else:
        p = _real(s)
        res["path"] = str(p)
        res["in_projects_root"] = _is_under(p, pr) and _cf(p) != _cf(pr)
        wk = _workspace_kind(p, root, home)
        if wk is not None:
            ws_kind, ws = wk
            res["source"] = ws_kind
            pairs, err = _read_git_config_remotes(ws)
            if err:
                res["reasons"].append(f"workspace config: {err}")
            remotes = _remotes_from_urls(pairs, root)
            top = ws
        elif res["in_projects_root"] and restricted:
            hit = _cache_lookup(p, _load_cache(cache, home))
            if hit is None:
                res["reasons"].append(
                    "agent chain: path under projects_root is resolved from the cache only; cache miss means "
                    "not positively personal (run profile_resolve.py scan in a plain terminal)"
                )
                return res, kind
            res["source"] = "cache"
            top = Path(hit["path"])
            for r in hit.get("remotes") or []:
                if isinstance(r, dict) and r.get("slug"):
                    o = str(r.get("slug")).split("/", 1)[0]
                    alias = None
                    if r.get("form") == "scp-alias":
                        alias = {"credential_scope": r.get("credential_scope")}
                    remotes.append({"name": r.get("name"), "host": r.get("host"), "owner": o, "slug": r.get("slug"),
                                    "form": r.get("form"), "_alias": alias})
        else:
            if not p.exists():
                res["reasons"].append("path does not exist")
                return res, kind
            top = _find_top(p)
            if top is None:
                res["reasons"].append("not a git repository")
                return res, kind
            pairs, err = _read_git_config_remotes(top)
            if err:
                res["reasons"].append(err)
            res["source"] = "live"
            remotes = _remotes_from_urls(pairs, root)
    _apply_walls(res, table, conduct, unknown_conduct, remotes, top, pr, ws_kind, restricted, root, kind)
    return res, kind


def _apply_walls(res: dict, table: dict, conduct: List[str], unknown_conduct: str, remotes: List[dict],
                 top: Optional[Path], pr: Path, ws_kind: Optional[str], restricted: bool,
                 root: Optional[Path], kind: str) -> None:
    classes: List[str] = []
    profiles: List[Optional[str]] = []
    out_remotes = []
    for r in remotes:
        cls, row = "unknown", None
        if r.get("owner"):
            if r.get("host"):
                cls, row = _owner_row_class(table, r["host"], r["owner"])
            else:
                matches = [x for x in table.get("owners") or [] if str(x.get("owner", "")).casefold() == r["owner"]]
                if matches:
                    ranked = sorted(matches, key=lambda x: CLASS_RANK.get(x.get("class"), 2), reverse=True)
                    row = ranked[0]
                    cls = row.get("class") if row.get("class") in CLASS_RANK else "unknown"
        alias = r.get("_alias") or {}
        if alias.get("credential_scope") == "work":
            if cls == "unknown":
                # Fallback heuristic (tighten-only): an undeclared owner behind a work-scoped alias.
                res["reasons"].append(f"remote {r.get('name')}: undeclared owner through a work-scoped ssh alias: employer")
                cls, row = "employer", None
            elif cls != "employer":
                res["reasons"].append(f"remote {r.get('name')}: declared {cls} owner through a work-scoped ssh alias")
        classes.append(cls)
        profiles.append(row.get("profile") if row and cls != "unknown" else (unknown_conduct if cls in ("unknown", "employer") else None))
        out_remotes.append({"name": r.get("name"), "host": r.get("host"), "owner": r.get("owner"), "slug": r.get("slug"),
                            "form": r.get("form"), "owner_class": cls})
    res["remotes"] = out_remotes
    if classes:
        overall = max(classes, key=lambda c: CLASS_RANK[c])
        if "personal" in classes and overall != "personal":
            res["conflicts"].append("remotes disagree: " + ", ".join(sorted(set(classes))) + " (most restrictive wins)")
    elif ws_kind:
        overall = "personal"
        profiles.append(conduct[0])
        res["reasons"].append("workspace checkout with no remotes")
    else:
        overall = "unknown"
        res["reasons"].append("no remotes: not positively personal")
    glob = None
    if top is not None and res["in_projects_root"]:
        glob = _glob_hit(top, pr, list(table.get("employer_path_globs") or []))
        if glob:
            if overall == "personal":
                res["conflicts"].append(f"path matches employer glob {glob!r} but remotes are personal")
            res["reasons"].append(f"path matches employer glob {glob!r} (tighten-only)")
            overall = "employer"
            profiles.append(unknown_conduct)
    row = None
    slugs = {r.get("slug") for r in out_remotes if r.get("slug")}
    for rr in table.get("repos") or []:
        if isinstance(rr, dict) and str(rr.get("slug", "")).casefold() in slugs:
            row = rr
            break
    if row is not None:
        profiles.append(row.get("profile"))
        vp = row.get("vault_project")
        if vp:
            ssp = _session_state_profile(root, vp, conduct)
            if ssp:
                profiles.append(ssp)
                res["reasons"].append(f"vault SESSION-STATE declares {ssp}")
    if overall == "unknown":
        profiles.append(unknown_conduct)
    profile = _conduct_max(conduct, *profiles) if any(p in conduct for p in profiles) else unknown_conduct
    pm_readable = top is not None and kind == "path" and not (restricted and res["in_projects_root"] and not ws_kind)
    if pm_readable and res["source"] in ("live", "workspace-root", "linked-worktree"):
        pmp = _project_md_profile(top, conduct)
        if pmp:
            if conduct.index(pmp) < conduct.index(profile):
                res["conflicts"].append(f"PROJECT.md profile {pmp} is looser than {profile}; ignored (tighten-only)")
            elif conduct.index(pmp) > conduct.index(profile):
                res["reasons"].append(f"PROJECT.md tightens to {pmp}")
                profile = pmp
    res["owner_class"] = overall
    res["profile"] = profile
    if row is not None:
        res["role"] = row.get("role")
    elif ws_kind:
        res["role"] = "workspace"
    else:
        res["role"] = overall
    res["positively_personal"] = bool(overall == "personal" and profile == conduct[0] and not glob)
    res["conflict"] = bool(res["conflicts"])


def repo_resolve(path_or_slug: str, *, root: Optional[Path] = None, home: Optional[Path] = None,
                 detection: Optional[dict] = None, cache: Any = None) -> dict:
    """The `repo` JSON: walls are the most restrictive of every source. Fail-closed."""
    return _resolve(path_or_slug, root=root, home=home, detection=detection, cache=cache)[0]


def classify_word(res: dict) -> str:
    if res.get("positively_personal"):
        return "personal"
    if res.get("owner_class") == "employer":
        return "employer"
    return "unknown"


# --------------------------------------------------------------------------- scan / where / audit


def _refusal_reasons(det: dict) -> List[str]:
    out = []
    if det.get("family_for_walls") in ("claude", "unknown-agent"):
        out.append(f"agent chain ({det.get('family_for_walls')})")
    if det.get("agent_possible"):
        out.append("agent-possible env present")
    return out


def _generated_by(det: dict) -> str:
    fam = det.get("family")
    if fam in ("cursor", "codex"):
        return fam
    if fam == "human":
        return "human"
    return "launchd"


def _iter_checkout_dirs(pr: Path, depth: int) -> List[Path]:
    out: List[Path] = []
    frontier = [pr]
    for _ in range(max(1, depth)):
        nxt = []
        for d in frontier:
            try:
                kids = sorted(d.iterdir())
            except OSError:
                continue
            for k in kids:
                if k.name.startswith(".") or k.is_symlink() or not k.is_dir():
                    continue
                nxt.append(k)
                if (k / ".git").exists():
                    out.append(k)
        frontier = nxt
    return out


def _scan_doc(*, root: Optional[Path], home: Optional[Path], depth: int, det: dict,
              hostname: Optional[str] = None) -> dict:
    table = _try_table("context-remotes", root) or {}
    pr = projects_root(root=root, home=home)
    dev = current_device(hostname=hostname, root=root)
    checkouts = []
    for d in _iter_checkout_dirs(pr, depth):
        kind = "repo" if (d / ".git").is_dir() else "linked-worktree"
        pairs, _err = _read_git_config_remotes(d)
        remotes = _remotes_from_urls(pairs, root)
        classes = []
        stored = []
        for r in remotes:
            cls = "unknown"
            if r.get("host") and r.get("owner"):
                cls = _owner_row_class(table, r["host"], r["owner"])[0] if table else "unknown"
            alias = r.get("_alias") or {}
            if alias.get("credential_scope") == "work" and cls == "unknown":
                cls = "employer"
            classes.append(cls)
            entry = {"name": r["name"], "form": r["form"], "host": r["host"], "slug": r["slug"]}
            if r["form"] == "scp-alias":
                entry["credential_scope"] = alias.get("credential_scope")
            stored.append(entry)
        oc = max(classes, key=lambda c: CLASS_RANK[c]) if classes else "unknown"
        if _glob_hit(d, pr, list(table.get("employer_path_globs") or [])):
            oc = "employer"
        checkouts.append({"path": str(d), "kind": kind, "remotes": stored, "owner_class": oc, "default_branch": None})
    return {"schema_version": SCHEMA_VERSION, "device": dev["id"], "generated_at": _now_z(),
            "generated_by": _generated_by(det), "projects_root": str(pr), "checkouts": checkouts}


def _write_json_atomic(path: Path, obj: dict) -> None:
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, path)


def scan(*, root: Optional[Path] = None, home: Optional[Path] = None, depth: int = 2,
         detection: Optional[dict] = None, env: Optional[dict] = None, ancestry: Optional[list] = None,
         isatty: Optional[dict] = None, hostname: Optional[str] = None, write: bool = True) -> dict:
    """Refused under a Claude chain or any agent-possible env; the cache is then untouched."""
    det = detection if detection is not None else detect_surface(env=env, ancestry=ancestry, isatty=isatty, root=root)
    reasons = _refusal_reasons(det)
    if reasons:
        return {"written": False, "checkouts": 0, "path": None, "refused": True, "reasons": reasons, "_doc": None}
    doc = _scan_doc(root=root, home=home, depth=depth, det=det, hostname=hostname)
    target = _cache_path(home)
    out = {"written": False, "checkouts": len(doc["checkouts"]), "path": None, "refused": False, "reasons": [], "_doc": doc}
    if write:
        if target.parent.is_dir():
            try:
                _write_json_atomic(target, doc)
                out.update(written=True, path=str(target))
            except OSError as exc:
                out["reasons"].append(f"cache not written ({exc.__class__.__name__})")
        else:
            out["reasons"].append("telemetry/ absent: cache not written (a human runs workspace-doctor.sh --install-pin)")
    return out


def where(slug: str, *, root: Optional[Path] = None, home: Optional[Path] = None, rescan: bool = True,
          detection: Optional[dict] = None, hostname: Optional[str] = None) -> dict:
    det = detection if detection is not None else detect_surface(root=root)
    s = (slug or "").strip()
    if "://" in s or "@" in s or (":" in s and "/" in s):
        norm = normalize_remote(s, root=root)
        s = norm["slug"] if norm else s
    s = s.casefold()
    dev = current_device(hostname=hostname, root=root)
    cache = _load_cache(None, home)
    notes = []
    if cache is not None and cache.get("device") not in (None, dev["id"]):
        notes.append("cache belongs to another device; ignored")
        cache = None

    def lookup(c: Optional[dict]) -> List[str]:
        return [co.get("path") for co in (c or {}).get("checkouts") or []
                if any(isinstance(r, dict) and str(r.get("slug", "")).casefold() == s for r in co.get("remotes") or [])]

    paths = lookup(cache)
    age = _age_s((cache or {}).get("generated_at"))
    rescanned = False
    if not paths and rescan and not _refusal_reasons(det):
        sc = scan(root=root, home=home, detection=det, hostname=hostname)
        if not sc["refused"]:
            rescanned = True
            paths = lookup(sc["_doc"])
            age = 0
            cache = sc["_doc"]
    if paths:
        status = "found"
    elif cache is None:
        status = "cache-missing"
    else:
        status = "not-on-this-device"
    out = {"slug": s, "device": dev["id"], "status": status, "paths": paths, "cache_age_s": age, "rescanned": rescanned}
    if notes:
        out["notes"] = notes
    return out


def audit(*, root: Optional[Path] = None, home: Optional[Path] = None, detection: Optional[dict] = None,
          env: Optional[dict] = None, ancestry: Optional[list] = None, isatty: Optional[dict] = None,
          git: str = "git", hostname: Optional[str] = None) -> dict:
    """Credential-scope audit over employer checkouts: counts only; by_slug goes to stdout only."""
    det = detection if detection is not None else detect_surface(env=env, ancestry=ancestry, isatty=isatty, root=root)
    reasons = _refusal_reasons(det)
    if reasons:
        return {"refused": True, "reasons": reasons, "repos_scanned": 0,
                "counts": {"default_branch_commits_agent_trailer": 0, "default_branch_commits_personal_identity": 0},
                "by_slug": {}}
    cache = _load_cache(None, home)
    if cache is None:
        cache = _scan_doc(root=root, home=home, depth=2, det=det, hostname=hostname)
    devices = _try_table("devices", root) or {}
    markers = devices.get("personal_markers") or {}
    emails = {str(e).casefold() for e in markers.get("emails") or []}
    domains = {str(d).casefold() for d in markers.get("email_domains") or []}
    notes = [] if markers else ["devices.json has no personal_markers yet: personal-identity counts are 0"]
    counts = {"default_branch_commits_agent_trailer": 0, "default_branch_commits_personal_identity": 0}
    by_slug: Dict[str, dict] = {}
    scanned = 0
    genv = _clean_git_env(os.environ)
    for co in cache.get("checkouts") or []:
        if co.get("owner_class") != "employer" or not co.get("path"):
            continue
        path = co["path"]
        branch = _default_branch(path, git, genv)
        if not branch:
            continue
        try:
            r = subprocess.run([git, "-C", path, "log", branch, "--format=%ae%x00%ce%x00%B%x1e"], capture_output=True,
                               text=True, timeout=30, env=genv)
        except (OSError, subprocess.SubprocessError):
            continue
        if r.returncode != 0:
            continue
        scanned += 1
        a = p = 0
        for rec in r.stdout.split("\x1e"):
            if not rec.strip():
                continue
            parts = rec.strip("\n").split("\x00", 2)
            if len(parts) < 3:
                continue
            ae, ce, body = parts
            if AGENT_TRAILER_RE.search(body):
                a += 1
            for e in (ae, ce):
                el = e.casefold()
                if el in emails or el.rsplit("@", 1)[-1] in domains:
                    p += 1
                    break
        counts["default_branch_commits_agent_trailer"] += a
        counts["default_branch_commits_personal_identity"] += p
        slug = next((x.get("slug") for x in co.get("remotes") or [] if x.get("slug")), None) or "(no remote)"
        by_slug[slug] = {"agent_trailer": a, "personal_identity": p}
    out = {"refused": False, "reasons": [], "repos_scanned": scanned, "counts": counts, "by_slug": by_slug}
    if notes:
        out["notes"] = notes
    return out


def _default_branch(path: str, git: str, env: dict) -> Optional[str]:
    try:
        r = subprocess.run([git, "-C", path, "symbolic-ref", "--short", "refs/remotes/origin/HEAD"], capture_output=True,
                           text=True, timeout=GIT_TIMEOUT_S, env=env)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
        for b in ("main", "master"):
            r = subprocess.run([git, "-C", path, "rev-parse", "--verify", "--quiet", f"refs/heads/{b}"], capture_output=True,
                               text=True, timeout=GIT_TIMEOUT_S, env=env)
            if r.returncode == 0:
                return b
    except (OSError, subprocess.SubprocessError):
        return None
    return None


def _clean_git_env(env: Any) -> dict:
    out = {k: v for k, v in dict(env).items()
           if not (k.startswith("GIT_CONFIG") or k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"))}
    out["GIT_TERMINAL_PROMPT"] = "0"
    return out


# --------------------------------------------------------------------------- detection


def _surfaces_or_fallback(root: Optional[Path]) -> dict:
    t = _try_table("surfaces", root)
    return t if t is not None else _FALLBACK_SURFACES


def _agent_possible_names(env: Any, t: dict) -> List[str]:
    ape = t.get("agent_possible_env") or {}
    names = set(ape.get("names") or [])
    prefixes = tuple(ape.get("prefixes") or ())
    out = []
    for k, v in dict(env).items():
        if v in (None, ""):
            continue
        if k in names or (prefixes and k.startswith(prefixes)):
            out.append(k)
    return sorted(out)


def _truthy(v: Any) -> bool:
    return str(v or "").strip().lower() not in ("", "0", "false", "no", "off")


def _ps_default(columns: str) -> str:
    r = subprocess.run(["ps", "-A", "-o", columns], capture_output=True, text=True, timeout=PS_TIMEOUT_S)
    if r.returncode != 0:
        raise OSError(f"ps exited {r.returncode}")
    return r.stdout


def _walk_ancestry_ex(pid: Optional[int], ps: Optional[Callable[[str], str]], max_hops: int) -> Tuple[list, Optional[str]]:
    start = os.getpid() if pid is None else int(pid)
    fn = ps or _ps_default
    t0 = time.monotonic()
    try:
        comm_txt = fn("pid=,ppid=,comm=")
    except Exception as exc:  # noqa: BLE001
        return [], f"ps failed ({exc.__class__.__name__})"
    procs: Dict[int, Tuple[int, str]] = {}
    for line in comm_txt.splitlines():
        parts = line.strip().split(None, 2)
        if len(parts) < 2:
            continue
        try:
            p, pp = int(parts[0]), int(parts[1])
        except ValueError:
            continue
        comm = parts[2] if len(parts) > 2 else ""
        procs[p] = (pp, comm.rstrip("/").rsplit("/", 1)[-1])
    args: Dict[int, str] = {}
    if time.monotonic() - t0 < 1.0:
        try:
            for line in fn("pid=,args=").splitlines():
                parts = line.strip().split(None, 1)
                if parts and parts[0].isdigit():
                    args[int(parts[0])] = parts[1] if len(parts) > 1 else ""
        except Exception:  # noqa: BLE001 - args are optional detail
            pass
    if start not in procs:
        return [], "start pid not in ps output"
    out = []
    seen = set()
    cur = procs[start][0]
    while cur and cur not in seen and len(out) < max_hops:
        seen.add(cur)
        ent = procs.get(cur)
        if ent is None:
            break
        out.append({"pid": cur, "ppid": ent[0], "comm": ent[1], "args": args.get(cur, "")})
        if cur == 1 or ent[0] in (0, cur):
            break
        cur = ent[0]
    return out, None


def walk_ancestry(*, pid: Optional[int] = None, ps: Optional[Callable[[str], str]] = None, max_hops: int = 12) -> list:
    """Ancestors of pid (default: this process), nearest first: [{pid, ppid, comm, args}]."""
    return _walk_ancestry_ex(pid, ps, max_hops)[0]


def _norm_chain(ancestry: Optional[list]) -> List[dict]:
    out = []
    for hop in ancestry or []:
        if isinstance(hop, dict):
            out.append({"pid": hop.get("pid"), "ppid": hop.get("ppid"),
                        "comm": str(hop.get("comm") or "").rstrip("/").rsplit("/", 1)[-1], "args": hop.get("args", "")})
        else:
            out.append({"pid": None, "ppid": None, "comm": str(hop).rstrip("/").rsplit("/", 1)[-1], "args": ""})
    return out[:12]


def _ancestry_matches(chain: List[dict], t: dict) -> List[dict]:
    fams = t.get("families") or {}
    out = []
    for i, hop in enumerate(chain):
        name = hop["comm"].lstrip("-")
        for row in t.get("surfaces") or []:
            hit = None
            for m in ((row.get("markers") or {}).get("ancestry") or []):
                comm = str(m.get("comm", ""))
                if not comm:
                    continue
                if (m.get("match") == "prefix" and name.startswith(comm)) or (m.get("match", "exact") == "exact" and name == comm):
                    hit = m
                    break
            if hit is not None and row.get("family") in fams:
                out.append({"hop": i, "surface": row.get("id"), "family": row.get("family"), "comm": name,
                            "verified": bool(hit.get("verified"))})
                break
    return out


def _env_markers(env: Any, t: dict) -> List[dict]:
    never = set(t.get("never_markers") or [])
    fams = t.get("families") or {}
    e = dict(env)
    out = []
    for row in t.get("surfaces") or []:
        for m in ((row.get("markers") or {}).get("env") or []):
            name = m.get("name")
            if not name or name in never or e.get(name) in (None, ""):
                continue
            if m.get("value") is not None and str(e.get(name)) != str(m.get("value")):
                continue
            if row.get("family") not in fams:
                continue
            out.append({"name": name, "surface": row.get("id"), "family": row.get("family"), "verified": bool(m.get("verified"))})
    return out


def read_markers(*, env: Optional[dict] = None, root: Optional[Path] = None) -> list:
    """Declared env markers present in env: [{name, surface, verified}] (never_markers skipped)."""
    t = _surfaces_or_fallback(root)
    return [{"name": m["name"], "surface": m["surface"], "verified": m["verified"]}
            for m in _env_markers(os.environ if env is None else env, t)]


def _tty(isatty: Optional[dict]) -> Dict[str, bool]:
    if isatty is not None:
        return {"stdin": bool(isatty.get("stdin")), "stdout": bool(isatty.get("stdout"))}
    out = {}
    for name, fd in (("stdin", 0), ("stdout", 1)):
        try:
            out[name] = os.isatty(fd)
        except OSError:
            out[name] = False
    return out


def _detect(payload_hint: Optional[str], env: Optional[dict], ancestry: Optional[list], isatty: Optional[dict],
            root: Optional[Path]) -> Tuple[dict, Optional[str]]:
    t = _surfaces_or_fallback(root)
    e = dict(os.environ if env is None else env)
    anc_err = None
    if ancestry is None:
        raw, anc_err = _walk_ancestry_ex(None, None, 12)
        chain = _norm_chain(raw)
    else:
        chain = _norm_chain(ancestry)
    tty = _tty(isatty)
    fams = t.get("families") or {}
    rows = {r.get("id"): r for r in t.get("surfaces") or [] if isinstance(r, dict)}
    anc = _ancestry_matches(chain, t)
    envm = _env_markers(e, t)
    ap = _agent_possible_names(e, t)
    acting, family, via, verified = None, None, "none", False
    if payload_hint and payload_hint in rows and rows[payload_hint].get("family") in fams:
        acting, family, via, verified = payload_hint, rows[payload_hint]["family"], "payload", True
    if acting is None and anc:
        n = anc[0]
        acting, family, via, verified = n["surface"], n["family"], "ancestry", n["verified"]
    if acting is None and envm:
        pick = next((m for m in envm if m["verified"]), envm[0])
        acting, family, via, verified = pick["surface"], pick["family"], "env", pick["verified"]
    if acting is None:
        if tty["stdin"] and tty["stdout"]:
            acting, family = "human", "human"
        else:
            acting, family = "unknown", "unknown"
    cands = [family] + [a["family"] for a in anc] + [m["family"] for m in envm]
    wsf = e.get("WS_SURFACE_FAMILY")
    if wsf in fams:
        cands.append(wsf)
    ranked = [c for c in cands if c in fams]
    walls = max(ranked, key=lambda c: fams[c].get("wall_rank", 0)) if ranked else family
    if family in fams and walls in fams and fams[walls].get("wall_rank", 0) <= fams[family].get("wall_rank", 0):
        walls = family
    agent_fams = sorted({c for c in ranked if fams[c].get("agent")})
    conflict = walls != family and bool(agent_fams)
    reason = None
    if conflict:
        reason = f"evidence ranks {walls} above the acting family {family}; walls use {walls}"
    automated = (_truthy(e.get("CI")) or _truthy(e.get("GITHUB_ACTIONS")) or bool(agent_fams) or bool(ap)
                 or not (tty["stdin"] and tty["stdout"]))
    det = {
        "acting_host": acting, "family": family, "family_for_walls": walls, "via": via, "verified": bool(verified),
        "determined": via in ("payload", "ancestry", "env"), "chain": [h["comm"] for h in chain],
        "markers": [m["name"] for m in envm], "conflict": conflict, "conflict_reason": reason, "automated": automated,
        "agent_possible": bool(ap),
    }
    return det, anc_err


def detect_surface(payload_hint: Optional[str] = None, *, env: Optional[dict] = None, ancestry: Optional[list] = None,
                   isatty: Optional[dict] = None, root: Optional[Path] = None) -> dict:
    """The Detection object (3c). Adds `agent_possible` (any agent_possible_env present)."""
    return _detect(payload_hint, env, ancestry, isatty, root)[0]


def automated_context(*, env: Optional[dict] = None, ancestry: Optional[list] = None, isatty: Optional[dict] = None,
                      root: Optional[Path] = None) -> bool:
    return bool(detect_surface(env=env, ancestry=ancestry, isatty=isatty, root=root)["automated"])


def agent_check(*, env: Optional[dict] = None, ancestry: Optional[list] = None, isatty: Optional[dict] = None,
                root: Optional[Path] = None) -> dict:
    """{human, determined, reasons}. Human needs TTYs on fds 0 and 1 and no agent evidence at all."""
    try:
        t = _surfaces_or_fallback(root)
        e = dict(os.environ if env is None else env)
        det, anc_err = _detect(None, e, ancestry, isatty, root)
        chain = _norm_chain(ancestry) if ancestry is not None else [{"comm": c} for c in det["chain"]]
        tty = _tty(isatty)
        reasons: List[str] = []
        for k in ("CI", "GITHUB_ACTIONS"):
            if _truthy(e.get(k)):
                reasons.append(f"ci:{k}")
        for n in _agent_possible_names(e, t):
            reasons.append(f"agent-possible-env:{n}")
        for m in _env_markers(e, t):
            reasons.append(f"marker:{m['name']}")
        fams = t.get("families") or {}
        for a in _ancestry_matches(chain, t):
            if fams.get(a["family"], {}).get("agent", True):
                reasons.append(f"agent:{a['family']}")
        wsf = e.get("WS_SURFACE_FAMILY")
        if wsf in fams and fams[wsf].get("agent"):
            reasons.append(f"family-env:{wsf}")
        for name in ("stdin", "stdout"):
            if not tty[name]:
                reasons.append(f"no-tty:{name}")
        reasons = list(dict.fromkeys(reasons))
        if reasons:
            return {"human": False, "determined": True, "reasons": reasons}
        if anc_err:
            return {"human": False, "determined": False, "reasons": [f"undetermined: ancestry unavailable ({anc_err})"]}
        return {"human": True, "determined": True, "reasons": []}
    except Exception as exc:  # noqa: BLE001 - undetermined is refuse for every caller
        return {"human": False, "determined": False, "reasons": [f"undetermined: {exc.__class__.__name__}"]}


# --------------------------------------------------------------------------- gitcaps


def _git_version(git: str) -> Optional[str]:
    try:
        r = subprocess.run([git, "--version"], capture_output=True, text=True, timeout=GIT_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError):
        return None
    m = re.search(r"git version (\d+(?:\.\d+)+)", r.stdout)
    return m.group(1) if m else None


def _probe_git(git: str) -> Tuple[bool, bool]:
    """(hasconfig, config_hooks) in a temp repo with a temp HOME; ~/.gitconfig is never touched."""
    with tempfile.TemporaryDirectory(prefix="ws-gitcaps-") as td:
        tdp = Path(td)
        home = tdp / "home"
        repo = tdp / "repo"
        home.mkdir()
        base = _clean_git_env({"PATH": os.environ.get("PATH", "/usr/bin:/bin")})
        env = dict(base, HOME=str(home), XDG_CONFIG_HOME=str(home / ".config"), GIT_CONFIG_NOSYSTEM="1", LANG="C", LC_ALL="C")

        def run(*a: str, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
            return subprocess.run([git, *a], cwd=str(cwd) if cwd else None, capture_output=True, text=True,
                                  timeout=GIT_TIMEOUT_S, env=env)

        try:
            if run("init", "-q", str(repo)).returncode != 0:
                return False, False
            run("remote", "add", "origin", "https://example.invalid/wsprobe/x.git", cwd=repo)
            inc = tdp / "inc.cfg"
            inc.write_text("[user]\n\tname = wsprobe-hasconfig\n", encoding="utf-8")
            run("config", "--global", "includeIf.hasconfig:remote.*.url:https://example.invalid/**.path", str(inc))
            r = run("config", "user.name", cwd=repo)
            hasconfig = r.returncode == 0 and r.stdout.strip() == "wsprobe-hasconfig"
            run("config", "hook.wsprobe.command", "true", cwd=repo)
            run("config", "hook.wsprobe.event", "pre-commit", cwd=repo)
            r = run("hook", "list", "pre-commit", cwd=repo)
            hooks = r.returncode == 0 and "wsprobe" in r.stdout
        except (OSError, subprocess.SubprocessError):
            return False, False
    return hasconfig, hooks


def _gitcaps_record_path(root: Optional[Path], device_id: str) -> Path:
    return _root(root) / "02-shared-references" / "probes" / f"git@{device_id}.json"


def gitcaps(*, record: bool = False, root: Optional[Path] = None, git: str = "git") -> dict:
    ver = _git_version(git)
    hasconfig, hooks = _probe_git(git) if ver else (False, False)
    dev = current_device(root=root)
    out: Dict[str, Any] = {"git_version": ver, "hasconfig": hasconfig, "config_hooks": hooks, "device": dev["id"]}
    if record:
        if dev["id"] == "unknown" or not ver:
            out["recorded"] = None
            out["notice"] = "not recorded: unknown device or git unavailable"
        else:
            rec = {"schema_version": SCHEMA_VERSION, "surface": "git", "device": dev["id"], "git_version": ver,
                   "hasconfig": hasconfig, "config_hooks": hooks,
                   "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%d")}
            path = _gitcaps_record_path(root, dev["id"])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            out["recorded"] = str(path.relative_to(_root(root)))
    return out


def gitcaps_check_recorded(*, root: Optional[Path] = None, git: str = "git", hostname: Optional[str] = None) -> dict:
    """Stale = git_version differs from the live git, or a key is missing. Age alone never matters."""
    dev = current_device(hostname=hostname, root=root)
    live = _git_version(git)
    out: Dict[str, Any] = {"device": dev["id"], "git_version": live, "stale": True, "reasons": []}
    if dev["id"] == "unknown":
        out["reasons"].append("unknown device: no record")
        return out
    path = _gitcaps_record_path(root, dev["id"])
    try:
        rec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        out["reasons"].append(f"missing or unreadable record probes/git@{dev['id']}.json")
        return out
    missing = [k for k in ("schema_version", "surface", "device", "git_version", "hasconfig", "config_hooks", "recorded_at")
               if not isinstance(rec, dict) or k not in rec]
    if missing:
        out["reasons"].append("record missing keys: " + ", ".join(missing))
        return out
    if rec.get("git_version") != live:
        out["reasons"].append(f"recorded git {rec.get('git_version')} differs from live {live}")
        return out
    out["stale"] = False
    out["recorded"] = {k: rec[k] for k in ("git_version", "hasconfig", "config_hooks", "recorded_at")}
    return out


# --------------------------------------------------------------------------- CLI


def _jsonable(obj: Any) -> Any:
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items() if not str(k).startswith("_")}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    return obj


def _emit(cmd: str, payload: dict, as_json: bool) -> None:
    body = _jsonable(payload)
    if as_json:
        print(json.dumps(dict({"schema_version": SCHEMA_VERSION, "cmd": cmd}, **body), indent=2, ensure_ascii=False))
        return
    for k, v in body.items():
        if isinstance(v, (dict, list)):
            v = json.dumps(v, ensure_ascii=False)
        print(f"{k}: {v}")


def _parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS)
    common.add_argument("--root", default=argparse.SUPPRESS, help="test-only repo root")
    ap = argparse.ArgumentParser(prog="profile_resolve.py", description=__doc__.split("\n\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true", default=False)
    ap.add_argument("--root", default=None, help="test-only repo root")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--stub-chain", action="store_true", help="with --self-test: also run the real stub-ancestor case")
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("device", parents=[common])
    p.add_argument("--hostname")
    p = sub.add_parser("repo", parents=[common])
    p.add_argument("target")
    p.add_argument("--format", choices=["json", "classify"], default="json")
    p = sub.add_parser("where", parents=[common])
    p.add_argument("slug")
    p.add_argument("--no-rescan", action="store_true")
    p = sub.add_parser("scan", parents=[common])
    p.add_argument("--report", action="store_true")
    p.add_argument("--depth", type=int, default=2)
    p = sub.add_parser("audit", parents=[common])
    p.add_argument("--report", action="store_true")
    p = sub.add_parser("detect", parents=[common])
    p.add_argument("--payload-hint")
    sub.add_parser("agent-check", parents=[common])
    p = sub.add_parser("gitcaps", parents=[common])
    p.add_argument("--record", action="store_true")
    p.add_argument("--check-recorded", action="store_true")
    p = sub.add_parser("validate-tables", parents=[common])
    p.add_argument("--require-all", action="store_true")
    return ap


def main(argv: Optional[List[str]] = None) -> int:
    ap = _parser()
    args = ap.parse_args(argv)
    if args.self_test:
        return self_test(stub_chain=args.stub_chain)
    if not args.cmd:
        ap.print_help(sys.stderr)
        return EXIT_USAGE
    root = Path(args.root).resolve() if args.root else None
    as_json = bool(args.json)
    cmd = args.cmd
    try:
        if cmd == "device":
            d = current_device(hostname=args.hostname, root=root)
            _emit(cmd, {"device": {k: d[k] for k in ("id", "label", "projects_root", "brain")},
                        "hostname_known": d["hostname_known"], "notice": d["notice"]}, as_json)
            return EXIT_OK if d["hostname_known"] else EXIT_NOTFOUND
        if cmd == "repo":
            res, kind = _resolve(args.target, root=root, home=None, detection=None, cache=None)
            rc = EXIT_NOTFOUND if (kind == "path" and res["source"] == "none") else EXIT_OK
            if args.format == "classify":
                print(classify_word(res))
            else:
                _emit(cmd, res, as_json)
            return rc
        if cmd == "where":
            w = where(args.slug, root=root, rescan=not args.no_rescan)
            _emit(cmd, w, as_json)
            return EXIT_OK if w["status"] == "found" else EXIT_NOTFOUND
        if cmd == "scan":
            s = scan(root=root, depth=args.depth)
            if args.report and not as_json and s.get("_doc"):
                for co in s["_doc"]["checkouts"]:
                    slugs = ",".join(r.get("slug") or "?" for r in co["remotes"]) or "(no remote)"
                    print(f"{co['owner_class']:<12} {slugs}")
            _emit(cmd, s, as_json)
            return EXIT_REFUSED if s["refused"] else EXIT_OK
        if cmd == "audit":
            a = audit(root=root)
            if args.report and not as_json:
                for slug, c in sorted(a.get("by_slug", {}).items()):
                    print(f"{slug}: agent_trailer={c['agent_trailer']} personal_identity={c['personal_identity']}")
            _emit(cmd, a, as_json)
            return EXIT_REFUSED if a["refused"] else EXIT_OK
        if cmd == "detect":
            _emit(cmd, detect_surface(args.payload_hint, root=root), as_json)
            return EXIT_OK
        if cmd == "agent-check":
            r = agent_check(root=root)
            _emit(cmd, r, as_json)
            if r["human"]:
                return EXIT_OK
            return EXIT_FAIL if r["determined"] else EXIT_USAGE
        if cmd == "gitcaps":
            if args.check_recorded:
                c = gitcaps_check_recorded(root=root)
                _emit(cmd, c, as_json)
                return EXIT_FAIL if c["stale"] else EXIT_OK
            g = gitcaps(record=args.record, root=root)
            _emit(cmd, g, as_json)
            if args.record and not g.get("recorded"):
                return EXIT_NOTFOUND
            return EXIT_OK
        if cmd == "validate-tables":
            v = validate_tables(root=root, require_all=args.require_all)
            _emit(cmd, v, as_json)
            return EXIT_OK if all(t["ok"] for t in v["tables"].values()) else EXIT_FAIL
    except Exception as exc:  # noqa: BLE001
        print(f"profile_resolve {cmd}: undetermined ({exc.__class__.__name__}: {exc})", file=sys.stderr)
        return EXIT_USAGE
    return EXIT_USAGE


# --------------------------------------------------------------------------- self-test

HUMAN_TTY = {"stdin": True, "stdout": True}
NO_TTY = {"stdin": False, "stdout": False}


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _fake_repo(top: Path, remotes: Dict[str, str]) -> Path:
    body = "[core]\n\trepositoryformatversion = 0\n"
    for name, url in remotes.items():
        body += f'[remote "{name}"]\n\turl = {url}\n\tfetch = +refs/heads/*:refs/remotes/{name}/*\n'
    _write(top / ".git" / "config", body)
    return top


def _fixture_root(tmp: Path) -> Path:
    """A synthetic workspace root: fixture tables, AGENTS.md, a git config with a personal remote."""
    root = tmp / "home-a" / "Projects" / "ws"
    for name in ("devices", "context-remotes", "surfaces"):
        src = FIXTURES / f"{name}.json"
        _write(root / TABLE_PATHS[name], src.read_text(encoding="utf-8"))
    _write(root / "AGENTS.md", "# fixture workspace\n")
    _fake_repo(root, {"origin": "https://github.com/pat-sample/ws.git"})
    _write(root / "07-projects" / "99-fixture" / "SESSION-STATE.md",
           "- **Context profile**: `centric-design` (fixture declaration)\n")
    return root


def self_test(stub_chain: bool = False) -> int:
    fails: List[str] = []
    passes = [0]

    def ok(cond: Any, label: str) -> None:
        if cond:
            passes[0] += 1
        else:
            fails.append(label)

    if not FIXTURES.is_dir():
        print(f"self-test FAIL: fixtures missing at {FIXTURES}", file=sys.stderr)
        return EXIT_FAIL
    with tempfile.TemporaryDirectory(prefix="ws-profile-resolve-") as td:
        tmp = Path(os.path.realpath(td))
        root = _fixture_root(tmp)
        home_a = tmp / "home-a"
        home_b = tmp / "home-b"
        tel_a = ws_paths(home=home_a)["telemetry"]
        tel_b = ws_paths(home=home_b)["telemetry"]
        tel_a.mkdir(parents=True)
        tel_b.mkdir(parents=True)
        pr_a = home_a / "Projects"
        claude = detect_surface(env={}, ancestry=[{"comm": "claude"}], isatty=HUMAN_TTY, root=root)
        human = detect_surface(env={}, ancestry=[{"comm": "zsh"}, {"comm": "launchd"}], isatty=HUMAN_TTY, root=root)
        ok(claude["family_for_walls"] == "claude" and human["family"] == "human", "fixture detections")

        # tables
        v = validate_tables(root=root)
        ok(all(t["ok"] for t in v["tables"].values()), "fixture tables validate (optional tables absent)")
        v = validate_tables(root=root, require_all=True)
        ok(not v["tables"]["action-policy"]["ok"] and not v["tables"]["devices"]["ok"],
           "--require-all flags a missing table and missing optional device keys")
        bad = json.loads((FIXTURES / "context-remotes.json").read_text(encoding="utf-8"))
        bad["surprise"] = 1
        ok(any("unknown top-level key" in e for e in validate_table("context-remotes", bad)), "unknown top-level key is an error")
        bad = json.loads((FIXTURES / "devices.json").read_text(encoding="utf-8"))
        bad["schema_version"] = 2
        ok(validate_table("devices", bad), "schema_version 2 is an error")
        bad = json.loads((FIXTURES / "devices.json").read_text(encoding="utf-8"))
        bad["devices"][0]["hostnames"] = "host-a"
        ok(validate_table("devices", bad), "wrong field type is an error")
        bad = json.loads((FIXTURES / "context-remotes.json").read_text(encoding="utf-8"))
        bad["owners"][0]["class"] = "friendly"
        ok(validate_table("context-remotes", bad), "owner class outside owner_classes is an error")
        try:
            load_table("vetted-scripts", root=root)
            ok(False, "missing table raises TableMissing")
        except TableMissing:
            ok(True, "")
        if (ROOT / TABLE_PATHS["devices"]).exists():
            real = validate_tables()
            ok(real["tables"]["devices"]["ok"] and real["tables"]["context-remotes"]["ok"], "shipped tables validate")

        # hostnames
        if (ROOT / TABLE_PATHS["devices"]).exists():
            for h in ("Voyager-2.lan", "voyager-2", "VOYAGER-2.local"):
                ok(current_device(hostname=h)["id"] == "personal-mbp", f"{h} resolves to personal-mbp")
            ok(device_label("CS-KQ23N94M0W.local") == "Work MacBook Pro (loaner)", "loaner hostname label")
        ok(current_device(hostname="HOST-A.local", root=root)["id"] == "dev-a", "fixture host case-folded")
        ok(current_device(hostname="host-a2.lan", root=root)["label"] == "Device A (spare)", "hostname label wins")
        d = current_device(hostname="mystery.local", root=root, scutil=lambda: "host-b")
        ok(d["id"] == "dev-b" and d["hostname_known"], "unknown host falls back to the injected scutil")
        d = current_device(hostname="mystery.local", root=root, scutil=lambda: "nope")
        ok(d["id"] == "unknown" and not d["hostname_known"] and d["notice"], "unknown after scutil is most restrictive")

        def boom() -> str:
            raise OSError("scutil")

        ok(current_device(hostname="mystery", root=root, scutil=boom)["id"] == "unknown", "a raising scutil is unknown")
        ok(device_label("strange.local", root=root) == "strange", "label fallback is the raw short hostname")

        # remotes
        n = normalize_remote("https://user@bitbucket.org/Acme-BB/x", root=root)
        ok(n == {"host": "bitbucket.org", "owner": "acme-bb", "repo": "x", "slug": "acme-bb/x", "form": "https-userinfo"},
           "https userinfo bitbucket normalizes with case-folding")
        n = normalize_remote("github-work:acme-corp/x", root=root)
        ok(n and n["host"] == "github.com" and n["owner"] == "acme-corp" and n["form"] == "scp-alias", "ssh alias normalizes")
        ok(owner_class("bitbucket.org", "Acme-BB", root=root) == "employer", "bitbucket owner class")
        ok(owner_class("github.com", "ACME-CORP", root=root) == "employer", "owner case-folded")
        ok(owner_class("github.com", "stranger", root=root) == "unknown", "unlisted owner is unknown")
        via_alias = _fake_repo(tmp / "elsewhere" / "alias-mine", {"origin": "git@github-work:pat-sample/alias-mine.git"})
        r = repo_resolve(str(via_alias), root=root, home=home_a, detection=human)
        ok(r["owner_class"] == "personal" and r["positively_personal"], "declared personal owner behind the work alias stays personal")
        via_alias = _fake_repo(tmp / "elsewhere" / "alias-stranger", {"origin": "github-work:stranger/x"})
        r = repo_resolve(str(via_alias), root=root, home=home_a, detection=human)
        ok(r["owner_class"] == "employer", "undeclared owner behind the work alias falls back to employer")
        for url, form in (("git@github.com:Pat-Sample/r.git", "scp"), ("github.com:pat-sample/r", "scp"),
                          ("ssh://git@github.com:22/pat-sample/r.git", "ssh"), ("https://github.com/pat-sample/r/", "https")):
            n = normalize_remote(url, root=root)
            ok(n and n["slug"] == "pat-sample/r" and n["form"] == form, f"normalize {form}")
        secret = "tok-" + "zq81fixturevalue"
        n = normalize_remote(f"https://pat-sample:{secret}@github.com/pat-sample/tok.git", root=root)
        ok(n and secret not in json.dumps(n) and n["form"] == "https-userinfo", "userinfo token never returned")
        ok(normalize_remote("/abs/local/path", root=root) is None and normalize_remote("", root=root) is None,
           "local paths and empty URLs do not normalize")

        # repo walls (human, live reads)
        fork = _fake_repo(pr_a / "fork", {"origin": "https://github.com/pat-sample/fork.git",
                                          "upstream": "git@github.com:acme-corp/fork.git"})
        r = repo_resolve(str(fork), root=root, home=home_a, detection=human)
        ok(r["owner_class"] == "employer" and r["conflict"] and not r["positively_personal"],
           "fork with employer upstream resolves to employer")
        emp = _fake_repo(pr_a / "emp-proj", {"origin": "github-work:acme-corp/emp-proj.git"})
        _write(emp / "PROJECT.md", "---\nprofile: personal-solo\n---\n")
        r = repo_resolve(str(emp), root=root, home=home_a, detection=human)
        ok(r["owner_class"] == "employer" and r["conflict"] and r["profile"] == "centric-engineering",
           "employer repo whose PROJECT.md says personal-solo is employer plus a conflict")
        pers = _fake_repo(pr_a / "mine", {"origin": "git@github.com:pat-sample/mine.git"})
        (pers / "sub" / "dir").mkdir(parents=True)
        r = repo_resolve(str(pers / "sub" / "dir"), root=root, home=home_a, detection=human)
        ok(r["positively_personal"] and r["source"] == "live" and classify_word(r) == "personal", "personal repo")
        _write(pers / "PROJECT.md", "profile: centric-design\n")
        r = repo_resolve(str(pers), root=root, home=home_a, detection=human)
        ok(r["profile"] == "centric-design" and not r["positively_personal"], "PROJECT.md may tighten")
        glob = _fake_repo(pr_a / "acme-tools", {"origin": "https://github.com/pat-sample/acme-tools"})
        r = repo_resolve(str(glob), root=root, home=home_a, detection=human)
        ok(r["owner_class"] == "employer" and r["conflict"], "employer path glob tightens a personal remote")
        vault = _fake_repo(pr_a / "vaulted", {"origin": "https://github.com/pat-sample/vaulted"})
        r = repo_resolve(str(vault), root=root, home=home_a, detection=human)
        ok(r["profile"] == "centric-design" and not r["positively_personal"], "vault SESSION-STATE tightens")
        third = _fake_repo(pr_a / "up", {"origin": "https://github.com/oss-upstream/up"})
        r = repo_resolve(str(third), root=root, home=home_a, detection=human)
        ok(r["owner_class"] == "third-party" and not r["positively_personal"], "third-party is not positively personal")
        none = _fake_repo(pr_a / "bare-ish", {})
        r = repo_resolve(str(none), root=root, home=home_a, detection=human)
        ok(r["owner_class"] == "unknown" and classify_word(r) == "unknown", "no remote is unknown")
        r = repo_resolve("acme-corp/anything", root=root, home=home_a, detection=human)
        ok(r["owner_class"] == "employer" and classify_word(r) == "employer", "slug resolves by owner row")
        r, kind = _resolve(str(tmp / "not-a-repo"), root=root, home=home_a, detection=human, cache=None)
        ok(kind == "path" and r["source"] == "none", "not a repo gives source none (exit 3)")

        # Claude chain: cache only under projects_root
        sentinel = _fake_repo(pr_a / "sealed", {"origin": "https://github.com/pat-sample/sealed"})
        cfg = sentinel / ".git" / "config"
        os.chmod(cfg, 0)
        try:
            r = repo_resolve(str(sentinel), root=root, home=home_a, detection=claude, cache={"checkouts": []})
            ok(r["source"] == "none" and not r["positively_personal"] and "config-unreadable" not in r["reasons"],
               "Claude chain on an uncached path is not positively personal and never opens it")
            r = repo_resolve(str(sentinel), root=root, home=home_a, detection=dict(human, agent_possible=True),
                             cache={"checkouts": []})
            ok(r["source"] == "none", "agent-possible env also reads from the cache only")
        finally:
            os.chmod(cfg, 0o644)
        cache_hit = {"checkouts": [{"path": str(sentinel), "kind": "repo", "owner_class": "personal", "default_branch": None,
                                    "remotes": [{"name": "origin", "form": "https", "host": "github.com", "slug": "pat-sample/sealed"}]}]}
        r = repo_resolve(str(sentinel), root=root, home=home_a, detection=claude, cache=cache_hit)
        ok(r["source"] == "cache" and r["positively_personal"], "Claude chain uses a cache hit")
        wt = pr_a / "ws.intent-T9"
        _write(wt / ".git", f"gitdir: {root}/.git/worktrees/ws.intent-T9\n")
        (root / ".git" / "worktrees" / "ws.intent-T9").mkdir(parents=True)
        r = repo_resolve(str(wt), root=root, home=home_a, detection=claude, cache={"checkouts": []})
        ok(r["source"] == "linked-worktree" and r["positively_personal"] and r["role"] == "workspace",
           "a linked worktree of the workspace is positively personal")
        ok(is_workspace_checkout(wt, root=root, home=home_a) and is_workspace_checkout(root, root=root, home=home_a),
           "is_workspace_checkout for root and worktree")
        evil = pr_a / "ws.intent-evil"
        _write(evil / ".git", "gitdir: /elsewhere/.git/worktrees/x\n")
        r = repo_resolve(str(evil), root=root, home=home_a, detection=claude, cache={"checkouts": []})
        ok(not r["positively_personal"] and not is_workspace_checkout(evil, root=root, home=home_a),
           "a sibling whose .git points elsewhere is not the workspace")
        outside = _fake_repo(tmp / "elsewhere" / "p", {"origin": "https://github.com/pat-sample/p"})
        r = repo_resolve(str(outside), root=root, home=home_a, detection=claude)
        ok(r["source"] == "live" and r["positively_personal"], "outside projects_root a Claude chain reads live")

        # scan / where
        _fake_repo(pr_a / "acme-org" / "deep", {"origin": "git@bitbucket.org:acme-bb/deep.git"})
        _fake_repo(pr_a / "tokened", {"origin": f"https://pat-sample:{secret}@github.com/pat-sample/tokened.git"})
        before = _write(tel_a / "checkouts.json", '{"schema_version": 1, "checkouts": []}\n').read_bytes()
        s = scan(root=root, home=home_a, detection=claude)
        ok(s["refused"] and (tel_a / "checkouts.json").read_bytes() == before, "Claude-chain scan refused; cache untouched")
        s = scan(root=root, home=home_a, env={"CLAUDE_PROJECT_DIR": "/x"}, ancestry=[{"comm": "launchd", "pid": 1}],
                 isatty=NO_TTY)
        ok(s["refused"] and (tel_a / "checkouts.json").read_bytes() == before,
           "scan under only CLAUDE_PROJECT_DIR (orphaned child) is refused")
        w = where("pat-sample/mine", root=root, home=home_a, detection=claude, hostname="host-a")
        ok(w["status"] != "found" and not w["rescanned"], "Claude where miss does not rescan")
        w = where("pat-sample/mine", root=root, home=home_a, detection=human, hostname="host-a")
        ok(w["status"] == "found" and w["rescanned"] and w["paths"] == [str(pers)], "non-Claude where miss triggers a rescan")
        text = (tel_a / "checkouts.json").read_text(encoding="utf-8")
        ok(secret not in text and "pat-sample:" not in text and "https://" not in text, "raw URLs and tokens never stored")
        doc = json.loads(text)
        deep = [c for c in doc["checkouts"] if c["path"].endswith("acme-org/deep")]
        ok(deep and deep[0]["owner_class"] == "employer", "scan reaches depth 2 and classifies employer")
        ok(doc["device"] == "dev-a" and doc["generated_by"] == "human", "cache records device and generator")
        _write(tel_b / "checkouts.json", json.dumps({"schema_version": 1, "device": "dev-b", "generated_at": _now_z(),
                                                     "generated_by": "human", "projects_root": str(home_b / "Projects"),
                                                     "checkouts": [{"path": str(home_b / "Projects" / "mine-b"), "kind": "repo",
                                                                    "remotes": [{"name": "origin", "form": "scp", "host": "github.com",
                                                                                 "slug": "pat-sample/mine"}],
                                                                    "owner_class": "personal", "default_branch": None}]}))
        wa = where("pat-sample/mine", root=root, home=home_a, detection=claude, hostname="host-a")
        wb = where("pat-sample/mine", root=root, home=home_b, detection=claude, hostname="host-b")
        ok(wa["paths"] == [str(pers)] and wb["paths"] == [str(home_b / "Projects" / "mine-b")]
           and wa["device"] == "dev-a" and wb["device"] == "dev-b", "the same slug resolves to one path per device")
        wx = where("pat-sample/mine", root=root, home=home_b, detection=claude, hostname="host-a")
        ok(wx["status"] == "cache-missing", "another device's cache is ignored")
        a = audit(root=root, home=home_a, detection=claude)
        ok(a["refused"], "Claude-chain audit refused")
        s = scan(root=root, home=tmp / "home-c", detection=human)
        ok(not s["written"] and not s["refused"] and not (tmp / "home-c" / ".config").exists(),
           "scan never creates telemetry/")

        # detection
        d = detect_surface(env={"CLAUDECODE": "1"}, ancestry=[{"comm": "zsh"}], isatty=HUMAN_TTY, root=root)
        ok(d["family"] == "human" and d["via"] == "none" and d["agent_possible"], "CLAUDECODE alone attributes no family")
        d = detect_surface(env={}, ancestry=[{"comm": "zsh"}, {"comm": "claude"},
                                             {"comm": "/Applications/Cursor.app/Contents/MacOS/Cursor Helper (Plugin)"},
                                             {"comm": "Cursor"}], isatty=NO_TTY, root=root)
        ok(d["acting_host"] == "claude-code" and d["family_for_walls"] == "claude" and not d["conflict"],
           "nested chain: Claude extension under Cursor Helper is claude-code with claude walls")
        d = detect_surface("cursor", env={}, ancestry=[{"comm": "claude"}], isatty=NO_TTY, root=root)
        ok(d["acting_host"] == "cursor" and d["family_for_walls"] == "claude" and d["conflict"] and d["verified"],
           "payload hint wins acting; walls take the maximum and flag a conflict")
        d = detect_surface(env={"CURSOR_AGENT": "1"}, ancestry=[], isatty=NO_TTY, root=root)
        ok(d["acting_host"] == "cursor" and d["via"] == "env" and d["verified"], "verified env marker")
        d = detect_surface(env={"CODEX_THREAD_ID": "t"}, ancestry=[], isatty=NO_TTY, root=root)
        ok(d["acting_host"] == "codex" and not d["verified"] and d["determined"], "unverified env marker is determined")
        d = detect_surface(env={"WS_SURFACE_FAMILY": "claude"}, ancestry=[], isatty=HUMAN_TTY, root=root)
        ok(d["family_for_walls"] == "claude" and d["family"] == "human", "WS_SURFACE_FAMILY raises the walls")
        ok(read_markers(env={"CURSOR_AGENT": "1", "CLAUDECODE": "1"}, root=root) ==
           [{"name": "CURSOR_AGENT", "surface": "cursor", "verified": True}], "read_markers skips never_markers")
        ok(not automated_context(env={}, ancestry=[{"comm": "zsh"}], isatty=HUMAN_TTY, root=root)
           and automated_context(env={"CI": "true"}, ancestry=[], isatty=HUMAN_TTY, root=root), "automated_context")

        def fake_ps(cols: str) -> str:
            if cols.startswith("pid=,ppid="):
                return ("  1     0 /sbin/launchd\n 10     1 /Applications/Claude.app/Contents/MacOS/Claude\n"
                        " 20    10 /bin/zsh\n 30    20 /usr/bin/python3\n")
            return "  1 /sbin/launchd\n 10 Claude\n 20 -zsh\n 30 python3 x.py\n"

        chain = walk_ancestry(pid=30, ps=fake_ps)
        ok([h["comm"] for h in chain] == ["zsh", "Claude", "launchd"] and chain[0]["args"] == "-zsh",
           "walk_ancestry: nearest first, basenames, ends at launchd")

        # agent-check through injected seams
        def ac(env: dict, anc: list, tty: dict) -> dict:
            return agent_check(env=env, ancestry=anc, isatty=tty, root=root)

        shell = [{"comm": "zsh"}, {"comm": "Terminal"}, {"comm": "launchd"}]
        r = ac({}, shell, HUMAN_TTY)
        ok(r["human"] and r["determined"], "human verdict with TTYs, no marker, no agent ancestor")
        r = ac({"CI": "1"}, shell, HUMAN_TTY)
        ok(not r["human"] and "ci:CI" in r["reasons"], "CI=1 is automated and refused")
        for k in ("CLAUDECODE", "CLAUDE_PROJECT_DIR", "CLAUDE_CODE_ENTRYPOINT"):
            r = ac({k: "1"}, shell, HUMAN_TTY)
            ok(not r["human"] and r["determined"], f"{k} with a TTY is agent possible and refused")
        for comm in ("Claude", "Claude Helper (Renderer)"):
            r = ac({}, [{"comm": "zsh"}, {"comm": comm}, {"comm": "launchd"}], HUMAN_TTY)
            ok(not r["human"] and "agent:claude" in r["reasons"], f"a TTY under {comm} is refused")
        r = ac({}, [{"comm": "script"}, {"comm": "zsh"}, {"comm": "claude"}], HUMAN_TTY)
        ok(not r["human"] and "agent:claude" in r["reasons"], "script -q shape (TTY, claude ancestor) is refused")
        r = ac({"CLAUDE_PROJECT_DIR": "/x"}, [{"comm": "launchd", "pid": 1}], NO_TTY)
        ok(not r["human"], "orphaned child (launchd, Claude env) is refused")
        r = ac({}, shell, {"stdin": True, "stdout": False})
        ok(not r["human"] and "no-tty:stdout" in r["reasons"], "no TTY on fd 1 is refused")
        det_err = _detect(None, {}, None, HUMAN_TTY, root)
        ok(isinstance(det_err[0], dict), "live detection runs without raising")

        # gitcaps: temp repo, temp HOME
        caps = gitcaps(root=root)
        ok(set(caps) >= {"git_version", "hasconfig", "config_hooks", "device"}, "gitcaps shape")
        ok(not (root / "02-shared-references" / "probes").exists(), "gitcaps without --record writes nothing")
        c = gitcaps_check_recorded(root=root, hostname="host-a")
        ok(c["stale"], "missing record is stale")
        if caps["git_version"]:
            _write(root / "02-shared-references" / "probes" / "git@dev-a.json", json.dumps(
                {"schema_version": 1, "surface": "git", "device": "dev-a", "git_version": caps["git_version"],
                 "hasconfig": True, "config_hooks": True, "recorded_at": "2020-01-01"}))
            ok(not gitcaps_check_recorded(root=root, hostname="host-a")["stale"], "an old record with the live version is fresh")
            _write(root / "02-shared-references" / "probes" / "git@dev-a.json", json.dumps(
                {"schema_version": 1, "surface": "git", "device": "dev-a", "git_version": "0.0.1",
                 "hasconfig": True, "config_hooks": True, "recorded_at": "2026-09-22"}))
            ok(gitcaps_check_recorded(root=root, hostname="host-a")["stale"], "a different git version is stale")

        # beacon-enroll classify() delegates (run against a copy of this module in a temp root)
        beacon = ROOT / "00-bootstrap" / "beacon-enroll.sh"
        if beacon.is_file() and shutil.which("bash"):
            fn = re.search(r"^classify\(\)[^\n]*\n(?:.*\n)*?\}\n", beacon.read_text(encoding="utf-8"), re.M)
            ok(fn is not None and "profile_resolve.py" in (fn.group(0) if fn else ""), "classify() delegates to profile_resolve")
            if fn is not None:
                _write(root / "09-tools" / "profile_resolve.py", Path(__file__).read_text(encoding="utf-8"))
                env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(tmp / "home-shell")}
                outside_emp = _fake_repo(tmp / "elsewhere" / "e", {"origin": "git@github.com:acme-corp/e.git",
                                                                   "fork": "https://github.com/pat-sample/e"})
                results = {}
                for label, target in (("personal", outside), ("employer", outside_emp), ("unknown", tmp / "nowhere")):
                    script = fn.group(0) + 'classify "$1"\n'
                    rr = subprocess.run(["bash", "-c", f'WS="{root}"\n' + script, "classify", str(target)],
                                        capture_output=True, text=True, timeout=30, env=env)
                    results[label] = rr.stdout.strip()
                ok(results == {"personal": "personal", "employer": "employer", "unknown": "unknown"},
                   f"beacon classify via the resolver: {results}")
                (root / "09-tools" / "profile_resolve.py").unlink()
                rr = subprocess.run(["bash", "-c", f'WS="{root}"\n' + fn.group(0) + 'classify "$1"\n', "classify", str(outside)],
                                    capture_output=True, text=True, timeout=30, env=env)
                ok(rr.stdout.strip() == "unknown", "classify echoes unknown when the resolver fails")

        # CLI envelope and exits (repo outside projects_root, so live read under any chain)
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home_a)}
        me = str(Path(__file__).resolve())
        rr = subprocess.run([sys.executable, me, "--root", str(root), "repo", str(outside), "--json"], capture_output=True,
                            text=True, timeout=60, env=env)
        try:
            j = json.loads(rr.stdout)
        except ValueError:
            j = {}
        ok(rr.returncode == 0 and j.get("cmd") == "repo" and j.get("schema_version") == 1 and j.get("positively_personal"),
           "CLI repo --json envelope")
        rr = subprocess.run([sys.executable, me, "repo", str(tmp / "nowhere"), "--root", str(root), "--format", "classify"],
                            capture_output=True, text=True, timeout=60, env=env)
        ok(rr.returncode == 3 and rr.stdout.strip() == "unknown", "CLI repo on a non-repo exits 3 and classifies unknown")
        rr = subprocess.run([sys.executable, me, "--root", str(root), "device", "--hostname", "nobody", "--json"],
                            capture_output=True, text=True, timeout=60, env=env)
        ok(rr.returncode == 3, "CLI device on an unknown host exits 3")
        rr = subprocess.run([sys.executable, me, "--root", str(root), "scan", "--json"], capture_output=True, text=True,
                            timeout=60, env=dict(env, CLAUDE_PROJECT_DIR="/x"))
        ok(rr.returncode == 4, "CLI scan refuses under agent-possible env (exit 4)")

        if stub_chain:
            # A real ancestor named `claude` that stays alive as the parent of the check.
            # macOS kills copies of Apple platform binaries (launch constraints: a copied
            # /bin/bash exits 137), and framework Python re-execs as `Python`, so on macOS the
            # stub is a tiny fork-and-wait binary compiled here. Linux CI can copy bash.
            stub = tmp / "stub" / "claude"
            stub.parent.mkdir()
            src = tmp / "stub" / "stub.c"
            src.write_text('#include <unistd.h>\n#include <sys/wait.h>\n'
                           'int main(int c,char**v){(void)c;pid_t p=fork();'
                           'if(p==0){execv("/bin/sh",v);_exit(127);}int s=0;'
                           'if(waitpid(p,&s,0)<0)return 1;return WIFEXITED(s)?WEXITSTATUS(s):1;}\n')
            cc = shutil.which("cc") or shutil.which("clang") or shutil.which("gcc")
            built = False
            if cc:
                built = subprocess.run([cc, "-O0", "-o", str(stub), str(src)], capture_output=True,
                                       timeout=120).returncode == 0
            if not built and sys.platform != "darwin" and shutil.which("bash"):
                # Bytes + exec bit only: copy2 would also copy BSD flags (EPERM on SIP binaries).
                shutil.copyfile(shutil.which("bash"), stub)
                os.chmod(stub, 0o755)
                built = True
            runnable = built and subprocess.run([str(stub), "-c", "exit 0"], capture_output=True,
                                                timeout=30).returncode == 0
            if not runnable:
                print("self-test SKIP: stub chain needs a runnable non-platform binary named claude "
                      "(no C compiler, or the stub was killed) — not a pass", file=sys.stderr)
                stub_chain = False
        if stub_chain:
            clean = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home_a)}
            cmd = f'"{sys.executable}" "{me}" --root "{root}" detect --json; exit $?'
            rr = subprocess.run([str(stub), "-c", cmd], capture_output=True, text=True, timeout=60, env=clean)
            try:
                j = json.loads(rr.stdout)
            except ValueError:
                j = {}
            ok(j.get("chain", [None])[0] == "claude", "stub ancestor named claude is the nearest hop")
            cmd = f'"{sys.executable}" "{me}" --root "{root}" agent-check --json; exit $?'
            rr = subprocess.run([str(stub), "-c", cmd], capture_output=True, text=True, timeout=60, env=clean)
            try:
                j = json.loads(rr.stdout)
            except ValueError:
                j = {}
            ok(rr.returncode == 1 and "agent:claude" in j.get("reasons", []), "real stub chain reports agent:claude")

    if fails:
        for f in fails:
            print(f"self-test FAIL: {f}", file=sys.stderr)
        print(f"profile_resolve self-test: {passes[0]} passed, {len(fails)} failed", file=sys.stderr)
        return EXIT_FAIL
    print(f"OK profile_resolve self-test ({passes[0]} checks)")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
