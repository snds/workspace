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
  python3 09-tools/profile_resolve.py policy --repo PATH|SLUG (--action-class C | --command TEXT)
                                      [--family auto|F] [--device auto|ID] [--via composed|vetted] [--json]
  python3 09-tools/profile_resolve.py classify --command TEXT [--json]
  python3 09-tools/profile_resolve.py vetted-status SCRIPT_ID [--json]
  python3 09-tools/profile_resolve.py identity [--repo PATH] [--family auto|F] [--device auto|ID] [--json]
  python3 09-tools/profile_resolve.py override --task S --repo O/R --identity ID --ttl 8h --reason TEXT
                                      | --list | --revoke ID [--json]
  python3 09-tools/profile_resolve.py floor --event pre-commit|commit-msg|pre-merge-commit|pre-push
                                      [--remote NAME URL] [--json]   (stdin: pre-push ref lines)
  python3 09-tools/profile_resolve.py --self-test [--stub-chain]

Exit codes: 0 ok; 1 deny/fail/drift or a positive negative determination; 2 usage or
undetermined; 3 not found / not on this device / SKIPPED; 4 refused.

`--root DIR` (a repo root with the standard layout) is for tests only. `scan` and `audit`
refuse under a Claude chain or any agent-possible env. `policy` evaluates the committed
action-policy table (read-only here); `--family` and `--via vetted` are what-if inputs that can
only tighten the detected walls and grant nothing: only vetted_context() runs anything vetted. `agent-check` tests fds 0 and 1: run
it with inherited stdio and never capture its stdout.

H17 (T8): `identity` reports the expected identity for (family, device, repo), the invariants hit (I1,
I2; exit 1) and the device-mismatch flag. `override` is Sean's express override: human, TTY, <= 24 h,
non-employer repos only, and it suppresses only that flag. `floor` (and floor_decide(), which the
pinned ws_hook calls from the overlay's config hook) blocks I1, I2 and not-positively-personal
under projects_root, allows the vetted housekeeping shape, and fails open on infrastructure errors.
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
# Used only when surfaces.json is missing or unreadable. Every declared agent marker is listed as
# agent-possible here, so installers, the pin guard, scan, audit and override still refuse (the most
# restrictive reading: with no table, any agent marker raises the walls to claude).
_FALLBACK_SURFACES: Dict[str, Any] = {
    "families": {
        "claude": {"wall_rank": 100, "agent": True},
        "unknown-agent": {"wall_rank": 90, "agent": True},
        "human": {"wall_rank": 0, "agent": False},
    },
    "never_markers": ["CLAUDECODE", "CLAUDE_PROJECT_DIR", "CLAUDE_PLUGIN_ROOT", "CLAUDE_WORKSPACE_VAULT"],
    "agent_possible_env": {
        "names": ["CLAUDECODE", "CLAUDE_PROJECT_DIR", "CLAUDE_PLUGIN_ROOT", "CLAUDE_WORKSPACE_VAULT", "CLAUDE_ENV_FILE",
                  "CURSOR_AGENT", "CODEX_THREAD_ID", "GEMINI_CLI", "AI_AGENT"],
        "prefixes": ["CLAUDE_CODE_", "CURSOR_", "CODEX_", "COPILOT_", "GEMINI_"],
        "exclude": ["CLAUDE_CODE_SSE_PORT"],
    },
    "surfaces": [
        {"id": "claude-code", "family": "claude", "markers": {"env": [], "ancestry": [
            {"comm": "claude", "match": "exact", "verified": False},
            {"comm": "Claude", "match": "exact", "verified": False},
            {"comm": "Claude Helper", "match": "prefix", "verified": False}]}},
        {"id": "other-local-agents", "family": "unknown-agent", "markers": {"env": [], "ancestry": [
            {"comm": "Cursor", "match": "prefix", "verified": False},
            {"comm": "codex", "match": "exact", "verified": False},
            {"comm": "Code Helper", "match": "prefix", "verified": False}]}},
    ],
}
# Positive human evidence: a chain that reaches launchd must pass one of these (walls F-09).
HUMAN_TERMINALS = ("Terminal", "iTerm2", "iTerm", "login", "sshd", "sshd-session", "tmux", "screen", "ghostty",
                   "Ghostty", "Alacritty", "alacritty", "kitty", "WezTerm", "wezterm-gui", "Hyper", "Tabby")
PTY_WRAPPERS = ("script", "expect", "unbuffer")


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
        # H15 wall guard: tool families (payload reader, generated matcher) and the rollout modes
        "tool_families": (_LIST, False), "wall_guard": (_DICT, False),
        # W1-11 parity gate (validated by workspace-harness.py check_component_parity)
        "component_scopes": (_DICT, False), "current_wave": (_INT, False), "parity_gate": (_STR, False),
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
    aliases = set()
    for i, row in enumerate(_rows(obj, "ssh_aliases", errors)):
        _check_row(row, f"ssh_aliases[{i}]", alias_spec, errors)
        aliases.add(row.get("alias"))
    _validate_identity_keys(obj, errors, seen_ids, aliases)


IDENTITY_CLASSES = ("employer", "personal")
IDENTITY_TRANSPORTS = ("ssh", "https")
IDENTITY_MISMATCH = ("flag",)
IDENTITY_OVERRIDE_SCOPES = ("non-employer-repos-only",)


def _validate_identity_keys(obj: dict, errors: List[str], device_ids: set, aliases: set) -> None:
    """The H17 keys of devices.json (T8): identities, markers, allowlist, rules, invariants."""
    ident_spec = {"id": (_STR, True), "name": (_STR, True), "email": (_STR, True), "class": (_STR, True),
                  "accounts": (_LIST, True), "push": (_DICT, True)}
    ids: Dict[str, dict] = {}
    for i, row in enumerate(_rows(obj, "identities", errors)):
        where = f"identities[{i}]"
        _check_row(row, where, ident_spec, errors)
        iid = row.get("id")
        if iid in ids:
            errors.append(f"{where}: duplicate id {iid!r}")
        ids[str(iid)] = row
        if row.get("class") not in IDENTITY_CLASSES:
            errors.append(f"{where}.class: must be one of {list(IDENTITY_CLASSES)}")
        if not _str_list(row.get("accounts", [])):
            errors.append(f"{where}.accounts: must be a list of strings")
        email = row.get("email")
        if isinstance(email, str) and ("@" not in email or email.strip() != email):
            errors.append(f"{where}.email: not an address")
        push = row.get("push") if isinstance(row.get("push"), dict) else {}
        transport = push.get("transport")
        if transport not in IDENTITY_TRANSPORTS:
            errors.append(f"{where}.push.transport: must be one of {list(IDENTITY_TRANSPORTS)}")
        elif transport == "ssh" and push.get("alias") is not None and push.get("alias") not in aliases:
            errors.append(f"{where}.push.alias: {push.get('alias')!r} is not a declared ssh alias")
        for k in push:
            if k not in ("transport", "alias", "credential"):
                errors.append(f"{where}.push: unknown key {k!r}")
    if "identities" in obj:
        for i, dev in enumerate(obj.get("devices") or []):
            di = dev.get("default_identity") if isinstance(dev, dict) else None
            if di is not None and di not in ids:
                errors.append(f"devices[{i}].default_identity: {di!r} is not a declared identity")
    pm = obj.get("personal_markers")
    if isinstance(pm, dict):
        _check_row(pm, "personal_markers", {"emails": (_LIST, True), "email_domains": (_LIST, True)}, errors)
        for k in ("emails", "email_domains"):
            if not _str_list(pm.get(k, [])):
                errors.append(f"personal_markers.{k}: must be a list of strings")
    ea = obj.get("employer_allowlist")
    if isinstance(ea, dict):
        _check_row(ea, "employer_allowlist", {"identity_ids": (_LIST, True), "email_domains": (_LIST, True)}, errors)
        for iid in ea.get("identity_ids") or []:
            if iid not in ids:
                errors.append(f"employer_allowlist.identity_ids: {iid!r} is not a declared identity")
            elif ids[iid].get("class") != "employer":
                errors.append(f"employer_allowlist.identity_ids: {iid!r} is not an employer identity")
        marked = {str(x).casefold() for x in ((pm or {}).get("emails") or [])} if isinstance(pm, dict) else set()
        for iid in ea.get("identity_ids") or []:
            if str((ids.get(iid) or {}).get("email", "")).casefold() in marked:
                errors.append(f"employer_allowlist: {iid!r} carries a personal-marker email")
    rule_spec = {"id": (_STR, True), "family": (_STR, True), "device": (_STR, True), "identity": (_STR, True),
                 "overridable": (_BOOL, False), "mismatch": (_STR, False), "override_suppresses": (_STR, False)}
    seen_rules: set = set()
    for i, row in enumerate(_rows(obj, "identity_rules", errors)):
        where = f"identity_rules[{i}]"
        _check_row(row, where, rule_spec, errors)
        if row.get("id") in seen_rules:
            errors.append(f"{where}: duplicate id {row.get('id')!r}")
        seen_rules.add(row.get("id"))
        if ids and row.get("identity") not in ids:
            errors.append(f"{where}.identity: {row.get('identity')!r} is not a declared identity")
        if row.get("device") != "*" and row.get("device") not in device_ids:
            errors.append(f"{where}.device: {row.get('device')!r} is not '*' or a declared device")
        if "mismatch" in row and row.get("mismatch") not in IDENTITY_MISMATCH:
            errors.append(f"{where}.mismatch: must be one of {list(IDENTITY_MISMATCH)}")
        if "override_suppresses" in row and row.get("override_suppresses") not in IDENTITY_OVERRIDE_SCOPES:
            errors.append(f"{where}.override_suppresses: must be one of {list(IDENTITY_OVERRIDE_SCOPES)}")
        if row.get("overridable") is False and "override_suppresses" in row:
            errors.append(f"{where}: a non-overridable rule cannot name override_suppresses")
    inv_ids: set = set()
    for i, row in enumerate(_rows(obj, "invariants", errors)):
        _check_row(row, f"invariants[{i}]", {"id": (_STR, True), "text": (_STR, True)}, errors)
        inv_ids.add(row.get("id"))
    if "invariants" in obj and not {"I1", "I2"} <= inv_ids:
        errors.append("invariants: I1 and I2 must both be declared")


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
            elif not _type_ok(m.get("value_prefix"), _OPT_STR) or not _str_list(m.get("value_not_prefixes", [])):
                errors.append(f"surfaces[{i}].markers.env: value_prefix is a string, value_not_prefixes a string list")
        for m in markers.get("ancestry") or []:
            if not isinstance(m, dict) or not isinstance(m.get("comm"), str) or m.get("match", "exact") not in ("exact", "prefix"):
                errors.append(f"surfaces[{i}].markers.ancestry: needs comm and match exact|prefix")
    ape = obj.get("agent_possible_env") if isinstance(obj.get("agent_possible_env"), dict) else {}
    if not _str_list(ape.get("names", [])) or not _str_list(ape.get("prefixes", [])) or not _str_list(ape.get("exclude", [])):
        errors.append("agent_possible_env: names, prefixes and exclude must be lists of strings")
    for k in ("never_markers", "minimum_surfaces", "components", "coverage_modes"):
        if k in obj and not _str_list(obj[k]):
            errors.append(f"{k}: must be a list of strings")


POLICY_OUTCOMES = ("allow", "deny", "route", "undecided")
POLICY_VIA = ("vetted", "composed")
POLICY_TARGET_REFS = ("default", "non-default", "unknown", "none")
VERB_TARGET_REFS = ("default", "non-default")
ACTION_CLASSES = ("meta", "housekeeping", "content-read", "author", "publish", "merge")
_VERB_KEYS: Dict[str, Tuple[tuple, bool]] = {
    "id": (_STR, True), "tool": (_STR, True), "argv": (_LIST, False), "op": (_STR, False),
    "flags_any": (_LIST, False), "flags_none": (_LIST, False), "target_ref": (_STR, False), "class": (_STR, True),
}


def _validate_action_policy(obj: dict, errors: List[str]) -> None:
    """Schema only (T7 never writes the rows): closed keys, known classes, outcomes and `when` values."""
    classes = obj.get("action_classes") if _str_list(obj.get("action_classes")) else []
    outcomes = obj.get("outcomes") if _str_list(obj.get("outcomes")) else []
    if not classes or len(set(classes)) != len(classes):
        errors.append("action_classes: must be a non-empty list of distinct strings")
    for c in outcomes:
        if c not in POLICY_OUTCOMES:
            errors.append(f"outcomes: unknown outcome {c!r}")
    for c in ("allow", "deny"):
        if c not in outcomes:
            errors.append(f"outcomes: must include {c!r}")
    for k in ("undecided_evaluates_as", "default_outcome"):
        if obj.get(k) not in outcomes:
            errors.append(f"{k}: not in outcomes")
    if obj.get("undecided_evaluates_as") == "undecided":
        errors.append("undecided_evaluates_as: must be a decided outcome")
    if obj.get("unknown_verb_class") not in classes:
        errors.append("unknown_verb_class: not in action_classes")
    targets = obj.get("route_targets") if _str_list(obj.get("route_targets")) else []
    if not _str_list(obj.get("route_targets")):
        errors.append("route_targets: must be a list of strings")
    seen: set = set()
    for i, row in enumerate(_rows(obj, "verb_map", errors)):
        where = f"verb_map[{i}]"
        _check_row(row, where, _VERB_KEYS, errors)
        if row.get("id") in seen:
            errors.append(f"{where}: duplicate id {row.get('id')!r}")
        seen.add(row.get("id"))
        if row.get("class") not in classes:
            errors.append(f"{where}.class: unknown class {row.get('class')!r}")
        if "argv" not in row and "op" not in row:
            errors.append(f"{where}: needs argv or op")
        for k in ("argv", "flags_any", "flags_none"):
            if k in row and not _str_list(row[k]):
                errors.append(f"{where}.{k}: must be a list of strings")
        if "target_ref" in row and row["target_ref"] not in VERB_TARGET_REFS:
            errors.append(f"{where}.target_ref: must be one of {list(VERB_TARGET_REFS)}")
    seen = set()
    for i, row in enumerate(_rows(obj, "rules", errors)):
        where = f"rules[{i}]"
        for k in row:
            if k not in _RULE_KEYS:
                errors.append(f"{where}: unknown key {k!r}")
        if not isinstance(row.get("id"), str):
            errors.append(f"{where}: missing key 'id'")
        elif row["id"] in seen:
            errors.append(f"{where}: duplicate id {row['id']!r}")
        seen.add(row.get("id"))
        if row.get("outcome") not in outcomes:
            errors.append(f"{where}.outcome: not in outcomes")
        if "proposed" in row and row.get("outcome") != "undecided":
            errors.append(f"{where}: 'proposed' is only valid with outcome 'undecided'")
        if "proposed" in row and row.get("proposed") not in outcomes:
            errors.append(f"{where}.proposed: not in outcomes")
        for k in ("reason", "note"):
            if k in row and not isinstance(row[k], str):
                errors.append(f"{where}.{k}: must be a string")
        if "receipt" in row and not isinstance(row["receipt"], bool):
            errors.append(f"{where}.receipt: must be a bool")
        if "route_to" in row and (not _str_list(row["route_to"]) or any(t not in targets for t in row["route_to"])):
            errors.append(f"{where}.route_to: must be a subset of route_targets")
        when = row.get("when")
        if not isinstance(when, dict):
            errors.append(f"{where}.when: must be an object")
            continue
        allowed_values = {"action_class": classes, "via": POLICY_VIA, "target_ref": POLICY_TARGET_REFS,
                          "owner_class": tuple(CLASS_RANK)}
        for k, v in when.items():
            if k in _WHEN_LIST_KEYS:
                if not _str_list(v) or not v:
                    errors.append(f"{where}.when.{k}: must be a non-empty list of strings")
                    continue
                for x in v:
                    if k in allowed_values and x not in allowed_values[k]:
                        errors.append(f"{where}.when.{k}: unknown value {x!r}")
            elif k in _WHEN_BOOL_KEYS:
                if not isinstance(v, bool):
                    errors.append(f"{where}.when.{k}: must be a bool")
            else:
                errors.append(f"{where}.when: unknown key {k!r}")


def _validate_vetted_scripts(obj: dict, errors: List[str]) -> None:
    spec = {
        "id": (_STR, True), "path": (_STR, True), "action_classes": (_LIST, True), "actions": (_DICT, True),
        "needs_employer_gh": (_BOOL, True), "approved": (_STR, True), "argv": (_DICT, True),
    }
    seen: set = set()
    for i, row in enumerate(_rows(obj, "scripts", errors)):
        where = f"scripts[{i}]"
        _check_row(row, where, spec, errors)
        if row.get("id") in seen:
            errors.append(f"{where}: duplicate id {row.get('id')!r}")
        seen.add(row.get("id"))
        p = row.get("path")
        if isinstance(p, str) and (p.startswith("/") or p.startswith("~") or ".." in Path(p).parts):
            errors.append(f"{where}.path: must be repo-relative")
        acs = row.get("action_classes") if _str_list(row.get("action_classes")) else []
        for c in acs:
            if c not in ACTION_CLASSES:
                errors.append(f"{where}.action_classes: unknown class {c!r}")
        acts = row.get("actions") if isinstance(row.get("actions"), dict) else {}
        for name, c in acts.items():
            if c not in acs:
                errors.append(f"{where}.actions.{name}: class {c!r} is not in the row's action_classes")
        shapes = row.get("argv") if isinstance(row.get("argv"), dict) else {}
        for name in acts:
            if name not in shapes:
                errors.append(f"{where}.argv: action {name!r} declares no argv shape")
        for name, lst in shapes.items():
            if name not in acts:
                errors.append(f"{where}.argv.{name}: not a declared action")
            if not (isinstance(lst, list) and lst and all(_str_list(x) and x for x in lst)):
                errors.append(f"{where}.argv.{name}: must be a non-empty list of token lists")


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


def projects_root(*, root: Optional[Path] = None, home: Optional[Path] = None,
                  hostname: Optional[str] = None) -> Path:
    h = Path(home) if home is not None else Path.home()
    try:
        row = _resolve_device(hostname, root, None)["row"]
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


# Hosts that reach the same owners as the canonical host (GitHub's ssh-over-443 endpoint and www).
_HOST_SYNONYMS = {"ssh.github.com": "github.com", "www.github.com": "github.com", "www.bitbucket.org": "bitbucket.org",
                  "altssh.bitbucket.org": "bitbucket.org"}


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
    host = _HOST_SYNONYMS.get(host.lower(), host.lower())
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


def _is_bare_repo(d: Path) -> bool:
    """A bare repository dir, by git's own shape test (HEAD, objects/ and refs/, no .git)."""
    try:
        return (not (d / ".git").exists() and (d / "HEAD").is_file() and (d / "objects").is_dir()
                and (d / "refs").is_dir())
    except OSError:
        return False


def _read_git_config_remotes(top: Path, bare: bool = False) -> Tuple[List[Tuple[str, str]], Optional[str]]:
    """[(remote name, url)] from the checkout's git config file (a bare repo's own `config` when
    `bare`). Reads only config files."""
    gitp = top / ".git"
    try:
        if bare:
            cfg = top / "config"
        elif gitp.is_dir():
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
                if (k / ".git").exists() or _is_bare_repo(k):
                    out.append(k)
        frontier = nxt
    return out


def _scan_doc(*, root: Optional[Path], home: Optional[Path], depth: int, det: dict,
              hostname: Optional[str] = None) -> dict:
    table = _try_table("context-remotes", root) or {}
    pr = projects_root(root=root, home=home, hostname=hostname)
    dev = current_device(hostname=hostname, root=root)
    checkouts = []
    for d in _iter_checkout_dirs(pr, depth):
        # A bare repo is recorded too: it is the main checkout of its linked worktrees (W3-02).
        bare = _is_bare_repo(d)
        kind = "bare" if bare else ("repo" if (d / ".git").is_dir() else "linked-worktree")
        pairs, _err = _read_git_config_remotes(d, bare=bare)
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
    # Names that match a prefix but are no agent evidence on their own. CLAUDE_CODE_SSE_PORT is set by
    # the Claude IDE extension in every Cursor / VS Code terminal, a human's included (Sean, 2026-09-24);
    # a real Claude chain still carries CLAUDECODE, the overlay's WS_SURFACE_FAMILY and its ancestry.
    exclude = set(ape.get("exclude") or [])
    out = []
    for k, v in dict(env).items():
        if v in (None, "") or k in exclude:
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
            val = str(e.get(name))
            if m.get("value") is not None and val != str(m.get("value")):
                continue
            if m.get("value_prefix") and not val.startswith(str(m.get("value_prefix"))):
                continue
            if any(val.startswith(str(x)) for x in m.get("value_not_prefixes") or []):
                continue
            if row.get("family") not in fams:
                continue
            out.append({"name": name, "surface": row.get("id"), "family": row.get("family"),
                        "verified": bool(m.get("verified")),
                        "specific": m.get("value") is not None or bool(m.get("value_prefix"))})
    return out


def _pick_env_marker(envm: List[dict]) -> dict:
    """Verified first, then value-specific; a name-only marker that matches several rows of one family
    reports that family's generic `other-*` row rather than whichever row comes first."""
    for m in envm:
        if m["verified"]:
            return m
    for m in envm:
        if m.get("specific"):
            return m
    first = envm[0]
    same = [m for m in envm if m["name"] == first["name"] and m["family"] == first["family"]]
    if len(same) > 1:
        generic = next((m for m in same if str(m["surface"]).startswith("other-")), None)
        if generic is not None:
            return generic
    return first


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
        pick = _pick_env_marker(envm)
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
    if ap and "claude" in fams:
        cands.append("claude")   # agent-possible env only ever tightens; forged markers cannot lower it
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
        "agent_possible": bool(ap), "ancestry_unavailable": bool(anc_err),
    }
    return det, anc_err


def detect_surface(payload_hint: Optional[str] = None, *, env: Optional[dict] = None, ancestry: Optional[list] = None,
                   isatty: Optional[dict] = None, root: Optional[Path] = None) -> dict:
    """The Detection object (3c). Adds `agent_possible` (any agent_possible_env present)."""
    return _detect(payload_hint, env, ancestry, isatty, root)[0]


def automated_context(*, env: Optional[dict] = None, ancestry: Optional[list] = None, isatty: Optional[dict] = None,
                      root: Optional[Path] = None) -> bool:
    return bool(detect_surface(env=env, ancestry=ancestry, isatty=isatty, root=root)["automated"])


def _no_human_evidence(chain: List[dict]) -> Optional[str]:
    """Why a chain that looks agent-free still is not positive human evidence, or None.

    Only a chain that reaches launchd (pid 1) is judged: it must pass a known terminal or login
    ancestor, and its nearest hop must not be a pty wrapper reparented to launchd."""
    if not chain:
        return None
    first = chain[0]
    if first["comm"].lstrip("-") in PTY_WRAPPERS and str(first.get("ppid")) == "1":
        return f"the nearest ancestor is an orphaned pty wrapper ({first['comm']})"
    last = chain[-1]
    reaches_init = last["comm"].lstrip("-") == "launchd" or str(last.get("pid")) == "1"
    if reaches_init and not any(h["comm"].lstrip("-") in HUMAN_TERMINALS for h in chain):
        return "the ancestry reaches launchd through no known terminal or login process"
    return None


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
        why = _no_human_evidence(chain)
        if why:
            return {"human": False, "determined": False, "reasons": [f"undetermined: {why}"]}
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


# --------------------------------------------------------------------------- action policy (T7, H22)
#
# One decide() over the committed action-policy table (DECISIONS-2 item 9). The table's rows are
# T0's and Sean's; this code only reads them. `via` is never taken from the environment: only
# vetted_context() evaluates with via=vetted, so a hand-set WS_VETTED or WS_WALL_OK changes nothing.

_CTRL_TOKENS = frozenset({"&&", "||", ";", "|", "&", "|&", ";;", "(", ")", "{", "}"})
_SHELLS = frozenset({"sh", "bash", "zsh", "dash", "ksh"})
_WRAPPERS = frozenset({"command", "exec", "nohup", "time", "builtin", "nice"})
_NOOP_TOOLS = frozenset({"true", "false", ":", "echo", "printf", "exit", "set"})
_BYPASS_ENV = ("GIT_CONFIG_COUNT", "GIT_CONFIG_PARAMETERS", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_NOSYSTEM",
               "GIT_CONFIG_SYSTEM")
# Any single indexed env-config entry set or unset on the command counts too: it changes the
# env-scope config that carries the floor and the transport block.
_BYPASS_ENV_PREFIXES = ("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_")
# Set or unset on the command itself, these reroute the floor's wrapper, its interpreter or git's
# config (git), or drop the gh belt / swap its credential (gh).
_BYPASS_ENV_GIT = ("HOME", "PATH", "XDG_CONFIG_HOME", "PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", "PYTHONUSERBASE",
                   "PYTHONINSPECT")
_BYPASS_ENV_GH = ("GH_CONFIG_DIR", "GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN",
                  "GH_HOST", "HOME", "XDG_CONFIG_HOME")
_UNKNOWN_CWD = "\x00unknown-cwd"
# NAME=value, and the append form NAME+=value (zsh and bash accept it as a prefix assignment).
_ASSIGN_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\+?=")
_REDIRECT_OPS = frozenset({">", ">>", "<", "<<", "<<<", ">&", "<&", "&>", "&>>", ">|"})
_GIT_OPTS_WITH_VALUE = frozenset({"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env",
                                  "--super-prefix", "--exec-path", "--attr-source", "--list-cmds"})
_GIT_OPTS_FLAG = frozenset({"-p", "-P", "--paginate", "--no-pager", "--bare", "--no-replace-objects",
                            "--literal-pathspecs", "--glob-pathspecs", "--noglob-pathspecs", "--icase-pathspecs",
                            "--no-optional-locks", "--no-advice", "--no-lazy-fetch", "--html-path", "--man-path",
                            "--info-path"})
_PUSH_OPTS_WITH_VALUE = frozenset({"--repo", "-o", "--push-option", "--receive-pack", "--exec"})
_COMMIT_SHORT_WITH_VALUE = "mFcCtS"
_NETWORK_GIT = frozenset({"fetch", "push", "pull", "ls-remote", "clone"})
OUTCOME_RANK = {"allow": 0, "route": 1, "deny": 2}


class PolicyError(ValueError):
    """Bad policy input (unknown action class, neither class nor command)."""


class ReceiptError(OSError):
    """A receipt or intent line could not be written (control/ absent or unwritable)."""


def _tokenize(text: str) -> Optional[List[str]]:
    import shlex

    lex = shlex.shlex(text.replace("\r", " ").replace("\n", " ; "), posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    lex.commenters = ""
    try:
        return list(lex)
    except ValueError:
        return None


def _split_simple(tokens: List[str]) -> List[Tuple[List[str], Optional[str]]]:
    """[(simple command tokens, following control operator)]."""
    out: List[Tuple[List[str], Optional[str]]] = []
    cur: List[str] = []
    for t in tokens:
        if t in _CTRL_TOKENS:
            if cur:
                out.append((cur, t))
            cur = []
            continue
        cur.append(t)
    if cur:
        out.append((cur, None))
    return out


def _join_cwd(base: Optional[str], p: Optional[str]) -> Optional[str]:
    if not p:
        return base
    import posixpath

    if p.startswith(("/", "~")) or not base:
        return posixpath.normpath(p) if not p.startswith("~") else p
    return posixpath.normpath(posixpath.join(base, p))


def _split_assign(tok: str) -> Tuple[str, str]:
    """NAME=value or NAME+=value -> (NAME, value)."""
    name, _, val = tok.partition("=")
    return name[:-1] if name.endswith("+") else name, val


def _cfg_bypass(item: str) -> bool:
    # include / includeIf read a file in the command scope, after the env config; an alias can
    # carry a hook-skip option. Either can switch the floor off or add a URL rewrite.
    key = item.split("=", 1)[0].strip().lower()
    return (key.startswith(("hook.", "url.", "include.", "includeif.", "alias."))
            or key == "core.hookspath")


def _no_verify(argv: List[str]) -> bool:
    """--no-verify, or an abbreviation git accepts for it (--no-veri, --no-verif)."""
    return any(a.startswith("--no-veri") and "--no-verify".startswith(a) for a in argv)


def _commit_n(argv: List[str]) -> bool:
    for a in argv[1:]:
        if a == "--":
            return False
        if a.startswith("-") and not a.startswith("--") and len(a) > 1:
            for ch in a[1:]:
                if ch == "n":
                    return True
                if ch in _COMMIT_SHORT_WITH_VALUE:
                    break
    return False


def _parse_git(args: List[str], cwd: Optional[str]) -> Tuple[List[str], Optional[str], Optional[str], bool]:
    """(argv after global options, cwd_hint, git_dir_hint, bypass-from-config)."""
    j = 0
    bypass = False
    gitdir = None
    while j < len(args):
        a = args[j]
        if a in _GIT_OPTS_WITH_VALUE:
            val = args[j + 1] if j + 1 < len(args) else ""
            if a == "-C":
                cwd = _join_cwd(cwd, val)
            elif a in ("-c", "--config-env"):
                bypass = bypass or _cfg_bypass(val)
            elif a == "--work-tree":
                cwd = _join_cwd(cwd, val)
            elif a == "--git-dir":
                gitdir = val
            j += 2
            continue
        if a.startswith("--") and "=" in a and a.split("=", 1)[0] in _GIT_OPTS_WITH_VALUE:
            name, val = a.split("=", 1)
            if name == "--config-env":
                bypass = bypass or _cfg_bypass(val)
            elif name == "--work-tree":
                cwd = _join_cwd(cwd, val)
            elif name == "--git-dir":
                gitdir = val
            j += 1
            continue
        if a in _GIT_OPTS_FLAG:
            j += 1
            continue
        break
    if gitdir:
        import posixpath

        # git operates on --git-dir / GIT_DIR wherever the command runs, so it names the repo.
        gd = posixpath.normpath(_join_cwd(cwd, gitdir) or gitdir) if not gitdir.startswith("~") else gitdir
        cwd = posixpath.dirname(gd) if posixpath.basename(gd) == ".git" else gd
    return args[j:], cwd, gitdir, bypass


def _parse_into(text: str, env0: Dict[str, Optional[str]], cwd0: Optional[str], depth: int, out: List[dict]) -> None:
    tokens = _tokenize(text)
    if tokens is None:
        out.append({"tool": "?", "argv": [], "cwd_hint": cwd0, "env_prefix": dict(env0), "hook_bypass": False,
                    "unparsed": True})
        return
    chain_env = dict(env0)
    cwd = cwd0
    for simple, _op in _split_simple(tokens):
        # redirections: strip operator and target; a file write becomes an fs-write invocation
        toks: List[str] = []
        writes = False
        k = 0
        while k < len(simple):
            t = simple[k]
            if t in _REDIRECT_OPS:
                target = simple[k + 1] if k + 1 < len(simple) else ""
                if toks and toks[-1].isdigit():
                    toks.pop()
                if t in (">", ">>", ">|", "&>", "&>>") and target and not target.startswith("&") and target != "/dev/null":
                    writes = True
                k += 2
                continue
            toks.append(t)
            k += 1
        env = dict(chain_env)
        i = 0
        while i < len(toks) and _ASSIGN_RE.match(toks[i]):
            name, val = _split_assign(toks[i])
            env[name] = val
            i += 1
        cmd_cwd = cwd
        while i < len(toks):
            base = toks[i].rstrip("/").rsplit("/", 1)[-1]
            if base == "env":
                i += 1
                while i < len(toks):
                    t = toks[i]
                    if t in ("-i", "--ignore-environment", "-"):
                        env["*"] = None
                        i += 1
                    elif t in ("-u", "--unset") and i + 1 < len(toks):
                        env[toks[i + 1]] = None
                        i += 2
                    elif t.startswith("--unset="):
                        env[t.split("=", 1)[1]] = None
                        i += 1
                    elif t.startswith("-u") and len(t) > 2:
                        env[t[2:]] = None
                        i += 1
                    elif t in ("-C", "--chdir") and i + 1 < len(toks):
                        cmd_cwd = _join_cwd(cmd_cwd, toks[i + 1])
                        i += 2
                    elif t == "--":
                        i += 1
                        break
                    elif _ASSIGN_RE.match(t):
                        name, val = _split_assign(t)
                        env[name] = val
                        i += 1
                    elif t.startswith("-"):
                        i += 1
                    else:
                        break
                continue
            if base in _WRAPPERS:
                i += 1
                while i < len(toks) and toks[i].startswith("-") and base in ("command", "time", "nice", "exec"):
                    i += 1
                continue
            break
        if writes:
            out.append({"tool": "fs", "op": "write", "argv": [], "cwd_hint": cmd_cwd, "env_prefix": dict(env),
                        "hook_bypass": False})
        if i >= len(toks):
            continue
        tool = toks[i].rstrip("/").rsplit("/", 1)[-1]
        args = toks[i + 1:]
        if tool in ("cd", "pushd", "popd"):
            dest = [a for a in args if not a.startswith("-") or a == "-"]
            if tool == "popd" or (tool == "pushd" and not dest) or (dest and (dest[0] == "-" or "$" in dest[0]
                                                                                or "`" in dest[0])):
                cwd = _UNKNOWN_CWD          # the target cannot be determined: most restrictive
            else:
                cwd = _join_cwd(cwd, dest[0] if dest else "~")
            continue
        if tool in ("export", "unset", "declare", "typeset"):
            for a in args:
                if tool == "unset":
                    if not a.startswith("-"):
                        chain_env[a] = None
                elif _ASSIGN_RE.match(a):
                    name, val = _split_assign(a)
                    chain_env[name] = val
            continue
        if tool in _NOOP_TOOLS:
            continue
        if tool in _SHELLS:
            script = None
            j = 0
            has_c = False
            while j < len(args):
                a = args[j]
                if a.startswith("-") and not a.startswith("--") and len(a) > 1:
                    if "c" in a[1:]:
                        has_c = True
                    j += 1
                    continue
                if a.startswith("--"):
                    j += 1
                    continue
                break
            if has_c and j < len(args):
                script = args[j]
            if script is not None and depth < 6:
                _parse_into(script, env, cmd_cwd, depth + 1, out)
                continue
            out.append({"tool": tool, "argv": args, "cwd_hint": cmd_cwd, "env_prefix": dict(env), "hook_bypass": False})
            continue
        inv: Dict[str, Any] = {"tool": tool, "argv": args, "cwd_hint": cmd_cwd, "env_prefix": dict(env),
                               "hook_bypass": False}
        bypass = ("*" in env or any(k in env for k in _BYPASS_ENV)
                  or any(k.startswith(_BYPASS_ENV_PREFIXES) for k in env))
        if tool == "git":
            bypass = bypass or any(k in env for k in _BYPASS_ENV_GIT)
            pre: List[str] = []
            if env.get("GIT_DIR"):
                pre += ["--git-dir", str(env["GIT_DIR"])]
            if env.get("GIT_WORK_TREE"):
                pre += ["--work-tree", str(env["GIT_WORK_TREE"])]
            argv, gcwd, gitdir, cfg_bypass = _parse_git(pre + list(args), cmd_cwd)
            inv.update(argv=argv, cwd_hint=gcwd)
            if gitdir:
                inv["git_dir_hint"] = gitdir
            bypass = bypass or cfg_bypass or _no_verify(argv)
            if argv and argv[0] == "commit" and _commit_n(argv):
                bypass = True
        elif tool == "gh":
            bypass = bypass or any(k in env for k in _BYPASS_ENV_GH)
            argv = []
            repo_hint = None
            j = 0
            while j < len(args):
                a = args[j]
                if a in ("-R", "--repo") and j + 1 < len(args):
                    repo_hint = args[j + 1]
                    j += 2
                    continue
                if a.startswith("--repo="):
                    repo_hint = a.split("=", 1)[1]
                    j += 1
                    continue
                argv.append(a)
                j += 1
            inv["argv"] = argv
            if repo_hint:
                inv["repo_hint"] = repo_hint
        inv["hook_bypass"] = bool(bypass)
        out.append(inv)


def parse_command(text: str) -> list:
    """Shell text -> [{tool, argv, cwd_hint, env_prefix, hook_bypass}] (plus repo_hint for gh -R/--repo).

    Handles `git -C`, `--git-dir`, `--work-tree`, `cd X &&`, env prefixes, `env` (incl. `-u`),
    `command git`, absolute git paths, recursive `sh -c` / `bash -lc`, and `gh -R` / `--repo`.
    Unparseable text yields one `?` invocation (it classifies as the unknown-verb class).
    """
    out: List[dict] = []
    _parse_into(text or "", {}, None, 0, out)
    for inv in out:
        if str(inv.get("cwd_hint") or "").startswith(_UNKNOWN_CWD):
            inv["cwd_hint"] = None
            inv["target_unknown"] = True
        ep = inv["env_prefix"]
        clean = {k: v for k, v in ep.items() if k != "*"}
        if "*" in ep:
            clean["(env -i)"] = None
        inv["env_prefix"] = clean
    return out


def _git_paths(top: Path) -> Tuple[Optional[Path], Optional[Path]]:
    """(git dir, common dir) for a checkout, reading only the .git file/dir."""
    g = top / ".git"
    try:
        if g.is_dir():
            return g, g
        if g.is_file():
            first = g.read_text(encoding="utf-8", errors="replace").splitlines()[0].strip()
            if not first.startswith("gitdir:"):
                return None, None
            gd = Path(first[len("gitdir:"):].strip())
            gd = gd if gd.is_absolute() else top / gd
            common = gd
            cd = gd / "commondir"
            if cd.is_file():
                c = Path(cd.read_text(encoding="utf-8", errors="replace").strip())
                common = c if c.is_absolute() else gd / c
            return gd, common
    except (OSError, IndexError):
        return None, None
    return None, None


def _repo_heads(path: Any) -> Tuple[Optional[str], Optional[str]]:
    """(current branch, remote default branch) from HEAD files only; None when unknown."""
    top = _find_top(_real(path))
    if top is None:
        return None, None
    gd, common = _git_paths(top)
    cur = dflt = None
    try:
        head = (gd / "HEAD").read_text(encoding="utf-8").strip() if gd else ""
        if head.startswith("ref: refs/heads/"):
            cur = head[len("ref: refs/heads/"):]
    except OSError:
        pass
    try:
        oh = (common / "refs" / "remotes" / "origin" / "HEAD").read_text(encoding="utf-8").strip() if common else ""
        if oh.startswith("ref: refs/remotes/origin/"):
            dflt = oh[len("ref: refs/remotes/origin/"):]
    except OSError:
        pass
    return cur, dflt


def _ref_kind(name: Optional[str], default: Optional[str]) -> str:
    if not name:
        return "unknown"
    n = name
    for pre in ("refs/heads/", "refs/remotes/origin/"):
        if n.startswith(pre):
            n = n[len(pre):]
    defaults = {default} if default else {"main", "master"}
    return "default" if n in defaults else "non-default"


def _push_target_ref(argv: List[str], current: Optional[str], default: Optional[str]) -> str:
    pos: List[str] = []
    j = 1
    everything = False
    while j < len(argv):
        a = argv[j]
        if a == "--":
            pos.extend(argv[j + 1:])
            break
        if a in _PUSH_OPTS_WITH_VALUE:
            j += 2
            continue
        if a in ("--all", "--mirror", "--branches"):
            everything = True
        if a.startswith("-"):
            j += 1
            continue
        pos.append(a)
        j += 1
    if everything:
        return "default"
    refspecs = pos[1:]
    if not refspecs:
        return "unknown"
    kinds = []
    for rs in refspecs:
        rs = rs.lstrip("+")
        dst = rs.split(":", 1)[1] if ":" in rs else rs
        if dst in ("HEAD", "@"):
            dst = current
        kinds.append(_ref_kind(dst, default))
    if "default" in kinds:
        return "default"
    if "unknown" in kinds:
        return "unknown"
    return "non-default"


def _flag_hit(flag: str, argv: List[str]) -> bool:
    for a in argv:
        if a == flag:
            return True
        if (len(flag) == 2 and flag[0] == "-" and flag[1] != "-" and a.startswith("-") and not a.startswith("--")
                and len(a) > 2 and flag[1] in a[1:]):
            return True
    return False


def _verb_row_match(row: dict, inv: dict, target_ref: str) -> bool:
    if row.get("tool") != inv.get("tool"):
        return False
    if "op" in row and row.get("op") != inv.get("op"):
        return False
    argv = list(inv.get("argv") or [])
    pre = list(row.get("argv") or [])
    if pre and argv[:len(pre)] != pre:
        return False
    rest = argv[len(pre):]
    if row.get("flags_any") and not any(_flag_hit(f, rest) for f in row["flags_any"]):
        return False
    if row.get("flags_none") and any(_flag_hit(f, rest) for f in row["flags_none"]):
        return False
    want = row.get("target_ref")
    if want:
        eff = target_ref
        if target_ref == "unknown" and argv[:1] == ["push"]:
            eff = "default"          # an implicit push refspec is treated as default
        if eff != want:
            return False
    return True


def verb_class(inv: dict, table: dict) -> Tuple[str, Optional[str]]:
    """(action class, verb id) for one invocation; unmatched -> unknown_verb_class."""
    tr = inv.get("target_ref") or "none"
    for row in table.get("verb_map") or []:
        if isinstance(row, dict) and _verb_row_match(row, inv, tr):
            return str(row.get("class")), row.get("id")
    return str(table.get("unknown_verb_class") or "author"), None


def _may_read_repo_files(path: Path, det: dict, root: Optional[Path], home: Optional[Path]) -> bool:
    """The Claude-chain read rule, applied to HEAD reads as well as to config reads."""
    if not _restricted(det, root):
        return True
    if _workspace_kind(path, root, home) is not None:
        return True
    pr = projects_root(root=root, home=home)
    return not _is_under(path, pr)


def _abs_hint(cwd: Optional[Any], hint: Optional[str]) -> Optional[str]:
    if not hint:
        return str(cwd) if cwd else None
    if hint.startswith("~"):
        return os.path.expanduser(hint)
    if os.path.isabs(hint) or not cwd:
        return hint
    return os.path.normpath(os.path.join(str(cwd), hint))


def classify_command(text: str, *, cwd: Any = None, root: Optional[Path] = None, detection: Optional[dict] = None,
                     home: Optional[Path] = None, default_branch: Optional[str] = None,
                     current_branch: Optional[str] = None) -> list:
    """invocations[]{tool, argv, cwd_hint, class, verb_id, target_ref, hook_bypass}.

    target_ref: push from the explicit refspec (implicit -> unknown); commit and merge from the
    current branch; `none` otherwise. HEAD files are read only where the Claude-chain read rule allows.
    """
    table = load_table("action-policy", root=root)
    det = detection
    out = []
    for inv in parse_command(text):
        argv = inv.get("argv") or []
        sub = argv[0] if (inv.get("tool") == "git" and argv) else None
        tr = "none"
        if sub in ("push", "commit", "merge"):
            cur, dflt = current_branch, default_branch
            where_abs = _abs_hint(cwd if cwd is not None else os.getcwd(), inv.get("cwd_hint"))
            if where_abs and (cur is None or dflt is None):
                if det is None:
                    det = detect_surface(root=root)
                p = _real(where_abs)
                if _may_read_repo_files(p, det, root, home):
                    rc, rd = _repo_heads(p)
                    cur = cur if cur is not None else rc
                    dflt = dflt if dflt is not None else rd
            if sub == "push":
                tr = _push_target_ref(argv, cur, dflt)
            else:
                tr = _ref_kind(cur, dflt)
        inv2 = dict(inv, target_ref=tr)
        cls, vid = verb_class(inv2, table)
        row = {"tool": inv["tool"], "argv": argv, "cwd_hint": inv.get("cwd_hint"), "class": cls, "verb_id": vid,
               "target_ref": tr, "hook_bypass": bool(inv.get("hook_bypass"))}
        for k in ("repo_hint", "op", "unparsed", "target_unknown"):
            if k in inv:
                row[k] = inv[k]
        out.append(row)
    return out


def _when_matches(when: dict, facts: dict) -> bool:
    for k, v in when.items():
        if k in _WHEN_LIST_KEYS:
            if facts.get(k) not in v:
                return False
        elif k in _WHEN_BOOL_KEYS:
            f = facts.get(k)
            if not isinstance(f, bool) or f is not v:
                return False
        else:
            return False
    return True


def policy_decide(facts: dict, table: dict) -> dict:
    """decide(): the first matching rule wins; undecided evaluates as the table says; no match -> default."""
    undecided_as = table.get("undecided_evaluates_as") or "deny"
    for rule in table.get("rules") or []:
        if not isinstance(rule, dict) or not isinstance(rule.get("when"), dict):
            continue
        if _when_matches(rule["when"], facts):
            raw = rule.get("outcome")
            eff = undecided_as if raw == "undecided" else raw
            if eff not in OUTCOME_RANK:
                eff = "deny"
            route_to = list(rule.get("route_to") or table.get("route_targets") or []) if eff == "route" else []
            return {"outcome": eff, "rule_outcome": raw, "rule_id": rule.get("id"),
                    "reason": rule.get("reason") or rule.get("note") or "", "receipt": bool(rule.get("receipt")),
                    "route_to": route_to, "proposed": rule.get("proposed")}
    dflt = table.get("default_outcome") or "deny"
    eff = undecided_as if dflt == "undecided" else dflt
    return {"outcome": eff if eff in OUTCOME_RANK else "deny", "rule_outcome": dflt, "rule_id": None,
            "reason": "no rule matched: default outcome", "receipt": False, "route_to": [], "proposed": None}


def _walls(family: str, det: dict, fams: dict) -> Tuple[str, str]:
    """(acting family, walls family). An explicit family can only tighten the detected walls."""
    acting = det.get("family") if family == "auto" else family
    walls = det.get("family_for_walls") or det.get("family") or "unknown"
    if family != "auto":
        cands = [c for c in (family, walls) if c in fams]
        walls = max(cands, key=lambda c: fams[c].get("wall_rank", 0)) if cands else family
    return str(acting), str(walls)


def _chain_has_agent(walls: str, acting: str, det: dict, fams: dict) -> bool:
    if det.get("agent_possible"):
        return True
    for f in (walls, acting):
        if f not in fams:
            return True          # unknown family: fail closed
        if fams[f].get("agent"):
            return True
    return False


def _res_facts(res: dict, root: Optional[Path], home: Optional[Path]) -> dict:
    under = res.get("in_projects_root")
    if res.get("path") and not under:
        pr = projects_root(root=root, home=home)
        under = _is_under(_real(res["path"]), pr) and _cf(_real(res["path"])) != _cf(pr)
    if res.get("path") is None:
        under = True             # a slug with no local path: most restrictive
    return {"owner_class": res.get("owner_class", "unknown"), "role": res.get("role", "unknown"),
            "positively_personal": bool(res.get("positively_personal")), "under_projects_root": bool(under),
            "has_remote": bool(res.get("remotes")), "repo_conflict": bool(res.get("conflict"))}


def _slug_of(res: dict) -> Optional[str]:
    rems = res.get("remotes") or []
    for r in rems:
        if r.get("name") == "origin" and r.get("slug"):
            return r["slug"]
    for r in rems:
        if r.get("slug"):
            return r["slug"]
    return None


def _append_jsonl(path: Path, record: dict) -> None:
    line = json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
    fd = os.open(str(path), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o600)
    try:
        os.write(fd, line.encode("utf-8"))
    finally:
        os.close(fd)


def _record_handoff(rec: dict, home: Optional[Path]) -> bool:
    tel = ws_paths(home=home)["telemetry"]
    if not tel.is_dir():
        return False
    try:
        _append_jsonl(tel / "handoffs.jsonl", rec)
        return True
    except OSError:
        return False


def policy(*, repo: str, action_class: Optional[str] = None, command: Optional[str] = None, family: str = "auto",
           device: str = "auto", via: str = "composed", root: Optional[Path] = None, env: Optional[dict] = None,
           ancestry: Optional[list] = None, isatty: Optional[dict] = None, home: Optional[Path] = None,
           hostname: Optional[str] = None, detection: Optional[dict] = None, record: bool = True,
           cache: Any = None, _resolved: Optional[dict] = None) -> dict:
    """The `policy` JSON: outcome (allow|deny|route), route_to, action_class, rule_id, reason, handoff.

    Every invocation of a command is evaluated against its own target repo; the most restrictive
    outcome wins. `via` is only ever what the caller passes: env markers never make a call vetted.
    """
    table = load_table("action-policy", root=root)
    classes = list(table.get("action_classes") or [])
    if command is None and action_class is None:
        raise PolicyError("policy needs --action-class or --command")
    if action_class is not None and action_class not in classes:
        raise PolicyError(f"unknown action class {action_class!r}")
    if via not in POLICY_VIA:
        raise PolicyError(f"via must be one of {list(POLICY_VIA)}")
    t = _surfaces_or_fallback(root)
    fams = t.get("families") or {}
    det = detection if detection is not None else detect_surface(env=env, ancestry=ancestry, isatty=isatty, root=root)
    acting, walls = _walls(family, det, fams)
    agent = _chain_has_agent(walls, acting, det, fams)
    walls_det = dict(det, family_for_walls=walls) if walls != det.get("family_for_walls") else det
    dev_id = current_device(hostname=hostname, root=root)["id"] if device == "auto" else device
    base = _resolved if _resolved is not None else repo_resolve(repo, root=root, home=home, detection=walls_det,
                                                                cache=cache)
    repo_is_path = base.get("path") is not None and not _looks_like_slug(str(repo))
    if command is not None:
        invs = classify_command(command, cwd=base.get("path") if repo_is_path else None, root=root,
                                detection=walls_det, home=home)
    else:
        tr = "none"
        if action_class in ("author", "merge") and repo_is_path and _may_read_repo_files(_real(base["path"]), walls_det,
                                                                                         root, home):
            cur, dflt = _repo_heads(base["path"])
            tr = _ref_kind(cur, dflt)
        elif action_class in ("author", "merge", "publish"):
            tr = "unknown"
        invs = [{"tool": None, "argv": [], "cwd_hint": None, "class": action_class, "verb_id": None, "target_ref": tr,
                 "hook_bypass": False}]
    resolved: Dict[str, dict] = {}
    best = None
    for inv in invs:
        target = None
        if inv.get("repo_hint"):
            target = inv["repo_hint"]
        elif inv.get("cwd_hint") and repo_is_path:
            target = _abs_hint(base["path"], inv["cwd_hint"])
        if target and _cf(_real(target) if not _looks_like_slug(target) else target) != _cf(base.get("path") or ""):
            if target not in resolved:
                resolved[target] = repo_resolve(target, root=root, home=home, detection=walls_det, cache=cache)
            res = resolved[target]
        else:
            res = base
        rf = _res_facts(res, root, home)
        if inv.get("target_unknown"):
            # a cwd change the parser cannot follow (popd, cd "$VAR", cd -): the most restrictive target
            rf = dict(rf, owner_class="employer", positively_personal=False, has_remote=True)
        facts = dict(rf, walls_family=walls, acting_family=acting, device=dev_id,
                     action_class=inv["class"], via=via, target_ref=inv.get("target_ref") or "none",
                     chain_has_agent=agent, hook_bypass=bool(inv.get("hook_bypass")))
        d = policy_decide(facts, table)
        d.update(action_class=inv["class"], facts=facts, repo_slug=_slug_of(res), verb_id=inv.get("verb_id"))
        if best is None or OUTCOME_RANK[d["outcome"]] > OUTCOME_RANK[best["outcome"]]:
            best = d
    assert best is not None
    handoff = None
    written = False
    reason = best["reason"]
    if best["outcome"] == "route":
        targets = " or ".join(best["route_to"]) or "an approved surface"
        reason = f"route: {targets} — {reason or 'this action belongs on an employer-approved surface'}"
        if walls == "claude":
            handoff = {"schema_version": SCHEMA_VERSION, "ts": _now_z(), "device": dev_id, "acting_family": acting,
                       "walls_family": walls, "repo_slug": best.get("repo_slug"), "action_class": best["action_class"],
                       "route_to": best["route_to"],
                       "summary": f"{best['action_class']} on a {best['facts']['owner_class']} repo routed to {targets}"[:120]}
            if record:
                written = _record_handoff(handoff, home)
    return {"outcome": best["outcome"], "route_to": best["route_to"], "action_class": best["action_class"],
            "rule_id": best["rule_id"], "reason": reason, "handoff": handoff, "handoff_written": written,
            "rule_outcome": best["rule_outcome"], "receipt": best["receipt"], "verb_id": best.get("verb_id"),
            "facts": best["facts"], "invocations": len(invs)}


# --------------------------------------------------------------------------- vetted scripts (T7, H22)


def git_blob_sha(path: Any) -> str:
    """`git hash-object` for a file, computed in Python (no subprocess)."""
    import hashlib

    data = Path(path).read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def _workspace_checkout(home: Optional[Path], root: Optional[Path]) -> Path:
    if root is not None:
        return Path(root)
    try:
        lines = ws_paths(home=home)["root_file"].read_text(encoding="utf-8").splitlines()
        if lines and lines[0].strip() and (Path(lines[0].strip()) / "AGENTS.md").is_file():
            return Path(lines[0].strip())
    except OSError:
        pass
    return ROOT


def vetted_status(script_id: str, *, script_path: Any = None, home: Optional[Path] = None,
                  root: Optional[Path] = None) -> dict:
    """{status: vetted|unpinned|hash-mismatch|not-registered, pinned_sha, blob, notice}.

    The registry and the lock are read from the PINNED lib (lib/current), never from the vault, so
    a vault registry edit takes effect only after Sean advances the pin.
    """
    lc = ws_paths(home=home)["lib_current"]
    out: Dict[str, Any] = {"script": script_id, "status": "unpinned", "pinned_sha": None, "blob": None, "notice": None}
    try:
        lock = json.loads((lc / "vetted.lock.json").read_text(encoding="utf-8"))
        if not isinstance(lock, dict):
            raise ValueError("lock is not an object")
    except (OSError, ValueError):
        out["notice"] = "no pinned lib or vetted.lock.json (a human runs workspace-doctor.sh --install-pin)"
        return out
    out["pinned_sha"] = lock.get("pinned_sha")
    reg = _try_table("vetted-scripts", lc)
    if reg is None:
        out["notice"] = "the pinned lib carries no vetted-scripts.json (advance the pin)"
        return out
    row = next((r for r in reg.get("scripts") or [] if isinstance(r, dict) and r.get("id") == script_id), None)
    if row is None:
        out.update(status="not-registered", notice=f"{script_id} is not in the pinned registry")
        return out
    ent = next((s for s in lock.get("scripts") or [] if isinstance(s, dict) and s.get("id") == script_id), None)
    if ent is None or not ent.get("blob") or ent.get("path") != row.get("path"):
        out["notice"] = f"{script_id} has no blob in the pinned lock (advance the pin)"
        return out
    sp = Path(script_path) if script_path is not None else _workspace_checkout(home, root) / str(row.get("path"))
    try:
        blob = git_blob_sha(sp)
    except OSError:
        out.update(status="hash-mismatch", notice="script file unreadable")
        return out
    out["blob"] = blob
    if blob != ent.get("blob"):
        out.update(status="hash-mismatch", notice="script bytes differ from the pinned blob (advance the pin)")
        return out
    out["status"] = "vetted"
    return out


def lift_env(env: dict, *, needs_employer_gh: bool = False, root: Optional[Path] = None) -> dict:
    """The vetted env: drops ONLY the transport block (url.<blocked_scheme>.insteadOf and
    pushInsteadOf entries, renumbered), unsets GIT_AUTHOR_*/GIT_COMMITTER_*, unsets GH_CONFIG_DIR
    only for employer-gh calls. Floor hooks, hasconfig includes, credential entries and
    WS_SURFACE_FAMILY are kept; no WS marker is added."""
    src = dict(env)
    out = {k: v for k, v in src.items() if not k.startswith(("GIT_AUTHOR_", "GIT_COMMITTER_"))}
    if needs_employer_gh:
        out.pop("GH_CONFIG_DIR", None)
    try:
        blocked = str(load_table("context-remotes", root=root).get("blocked_scheme") or "")
    except TableError:
        blocked = ""
    try:
        count = int(str(src.get("GIT_CONFIG_COUNT", "")).strip())
    except ValueError:
        return out
    if not blocked:
        return out
    pairs = []
    for i in range(max(0, count)):
        k = src.get(f"GIT_CONFIG_KEY_{i}")
        if k is None:
            continue
        # section and variable are case-insensitive; the url subsection is compared as written
        var = k.rsplit(".", 1)[-1]
        if (k[:4].casefold() == "url." and var.casefold() in ("insteadof", "pushinsteadof")
                and k[4:len(k) - len(var) - 1] == blocked):
            continue
        pairs.append((k, src.get(f"GIT_CONFIG_VALUE_{i}", "")))
    for key in list(out):
        if re.fullmatch(r"GIT_CONFIG_(KEY|VALUE)_\d+", key):
            del out[key]
    for i, (k, v) in enumerate(pairs):
        out[f"GIT_CONFIG_KEY_{i}"] = k
        out[f"GIT_CONFIG_VALUE_{i}"] = v
    out["GIT_CONFIG_COUNT"] = str(len(pairs))
    return out


_RECEIPT_KEYS = ("type", "ts", "device", "family", "surface", "pid", "ppid", "script", "script_blob", "repo_slug",
                 "action_class", "action", "refs", "credential", "result")


def _receipt_clean(record: dict) -> dict:
    out = {}
    for k in _RECEIPT_KEYS:
        if k not in record:
            continue
        v = record[k]
        vals = v if isinstance(v, list) else [v]
        for x in vals:
            if isinstance(x, str) and ("://" in x or x.startswith(("/", "~")) or re.search(r"\S+@\S+:", x)):
                raise ValueError(f"receipt field {k} looks like a URL or a path")
        out[k] = v
    return out


def append_receipt(record: dict, *, home: Optional[Path] = None) -> None:
    """Append one intent or receipt line to control/receipts.jsonl. Never creates control/."""
    ctrl = ws_paths(home=home)["control"]
    if not ctrl.is_dir():
        raise ReceiptError("control/ is absent (a human runs workspace-doctor.sh --install-pin)")
    _append_jsonl(ctrl / "receipts.jsonl", _receipt_clean(record))


def _gh_class(env: dict) -> str:
    return "gh-claude" if env.get("GH_CONFIG_DIR") else "default-account"


def _git_sub(argv: List[str]) -> Optional[str]:
    if not argv or argv[0].rstrip("/").rsplit("/", 1)[-1] != "git":
        return None
    rest, _cwd, _gd, _b = _parse_git(list(argv[1:]), None)
    return rest[0] if rest else None


def _credential(argv: List[str], res: dict, env: dict, root: Optional[Path]) -> str:
    tool = argv[0].rstrip("/").rsplit("/", 1)[-1] if argv else ""
    if tool == "gh":
        return f"gh:{_gh_class(env)}"
    if _git_sub(argv) not in _NETWORK_GIT:
        return "none"
    rems = res.get("remotes") or []
    r = next((x for x in rems if x.get("name") == "origin"), rems[0] if rems else None)
    if not r:
        return "unknown"
    form, host = r.get("form"), r.get("host") or "unknown"
    if form in ("scp", "ssh"):
        return f"ssh:{host}"
    if form == "scp-alias":
        aliases = [a for a in _ssh_aliases(root).values() if str(a.get("host", "")).lower() == host]
        if len(aliases) > 1:
            want = "work" if r.get("owner_class") == "employer" else None
            aliases = [a for a in aliases if a.get("credential_scope") == want] or aliases
        return f"ssh:{aliases[0].get('alias')}" if aliases else f"ssh:{host}"
    if form in ("https", "https-userinfo"):
        return f"https:{host}+gh:{_gh_class(env)}"
    return "unknown"


_SHAPE_TOKENS = {
    "<ref>": re.compile(r"^[A-Za-z0-9_@][A-Za-z0-9._/@-]*$"),
    "<n>": re.compile(r"^[0-9]{1,6}$"),
    "<path>": re.compile(r"^[^-\s][^\s]*$"),
}


def argv_matches_shape(argv: List[str], shape: List[str]) -> bool:
    """Exact-length match: literal tokens equal, <ref>/<n>/<path> placeholders by pattern (no options,
    no refspec colons or leading +)."""
    if len(argv) != len(shape):
        return False
    for a, t in zip(argv, shape):
        rx = _SHAPE_TOKENS.get(t)
        if rx is not None:
            if not rx.match(str(a)) or ":" in str(a):
                return False
        elif str(a) != t:
            return False
    return True


class VettedContext:
    """Context for one vetted script in one repo. `.run()` = intent line, lifted env, receipt."""

    def __init__(self, script_id: str, repo: Any, script_path: Any, *, home: Optional[Path], root: Optional[Path],
                 detection: Optional[dict], device: str, hostname: Optional[str], env: Optional[dict],
                 runner: Optional[Callable[..., subprocess.CompletedProcess]], assume_unpinned: bool,
                 out: Any, cache: Any) -> None:
        self.script_id = script_id
        self.repo = str(repo)
        self.script_path = script_path
        self.home, self.root = home, root
        self._det, self._device, self._hostname = detection, device, hostname
        self._env = env
        self._runner = runner
        self._assume_unpinned = assume_unpinned
        self._out = out
        self._cache = cache
        self.status: dict = {}
        self.row: Optional[dict] = None
        self.res: dict = {}
        self.receipts: List[dict] = []
        self._noticed = False

    def _notice(self, text: str) -> None:
        if not self._noticed:
            self._noticed = True
            print(f"notice: {text}", file=sys.stderr)

    def __enter__(self) -> "VettedContext":
        self.status = vetted_status(self.script_id, script_path=self.script_path, home=self.home, root=self.root)
        if self._assume_unpinned and self.status.get("status") == "vetted":
            self.status = dict(self.status, status="unpinned", notice="pinned module not importable: unpinned")
        lc = ws_paths(home=self.home)["lib_current"]
        reg = _try_table("vetted-scripts", lc) if self.status.get("status") != "unpinned" else None
        if reg is None:
            reg = _try_table("vetted-scripts", self.root)   # action names only; never makes a call vetted
        self.row = next((r for r in (reg or {}).get("scripts") or []
                         if isinstance(r, dict) and r.get("id") == self.script_id), None)
        t = _surfaces_or_fallback(self.root)
        self.fams = t.get("families") or {}
        self.det = self._det if self._det is not None else detect_surface(root=self.root)
        self.acting, self.walls = _walls("auto", self.det, self.fams)
        self.device = (current_device(hostname=self._hostname, root=self.root)["id"]
                       if self._device == "auto" else self._device)
        self.res = repo_resolve(self.repo, root=self.root, home=self.home, detection=self.det, cache=self._cache)
        self.path = self.res.get("path") or self.repo
        self.slug = _slug_of(self.res)
        return self

    def __exit__(self, *exc: Any) -> bool:
        return False

    @property
    def vetted(self) -> bool:
        return self.status.get("status") == "vetted"

    def decide(self, action_class: str) -> dict:
        return policy(repo=self.repo, action_class=action_class, via="vetted" if self.vetted else "composed",
                      root=self.root, home=self.home, detection=self.det, device=self.device, record=False,
                      _resolved=self.res)

    def _exec(self, argv: List[str], env: dict, timeout: float) -> subprocess.CompletedProcess:
        if self._runner is not None:
            return self._runner(list(argv), cwd=str(self.path), env=env, timeout=timeout)
        try:
            return subprocess.run(list(argv), cwd=str(self.path), env=env, capture_output=True, text=True,
                                  timeout=timeout)
        except (OSError, subprocess.SubprocessError) as exc:
            return subprocess.CompletedProcess(list(argv), 125, "", f"{exc.__class__.__name__}")

    def _refuse(self, argv: List[str], why: str) -> subprocess.CompletedProcess:
        return subprocess.CompletedProcess(list(argv), 126, "", why)

    def query(self, argv: List[str], timeout: float = 30.0) -> subprocess.CompletedProcess:
        """A local, read-only git query (no receipt). Runs only where meta is allowed."""
        d = self.decide("meta")
        if d["outcome"] != "allow":
            return self._refuse(argv, f"denied ({d['rule_id']}): {d['reason']}")
        return self._exec(argv, lift_env(dict(os.environ if self._env is None else self._env), root=self.root),
                          timeout)

    def _base_record(self, action: str, action_class: str, refs: List[str]) -> dict:
        return {"ts": _now_z(), "script": self.script_id, "script_blob": self.status.get("blob"),
                "repo_slug": self.slug, "action_class": action_class, "action": action, "refs": refs}

    def _receipt(self, base: dict, credential: str, result: str) -> dict:
        rec = {"type": "receipt", "ts": _now_z(), "device": self.device, "family": self.walls,
               "surface": self.det.get("acting_host"), "script": base["script"], "script_blob": base["script_blob"],
               "repo_slug": base["repo_slug"], "action_class": base["action_class"], "action": base["action"],
               "refs": base["refs"], "credential": credential, "result": result}
        written = True
        try:
            append_receipt(rec, home=self.home)
        except (OSError, ValueError) as exc:
            written = False
            self._notice(f"receipts not written ({exc})")
        self.receipts.append(dict(rec, _written=written))
        if self._out is not None:
            self._out(f"receipt {json.dumps(rec, ensure_ascii=False, separators=(',', ':'))}")
        return rec

    def run(self, argv: List[str], action: str, refs: Any = (), needs_employer_gh: bool = False,
            timeout: float = 120.0) -> subprocess.CompletedProcess:
        refs_l = [str(r) for r in refs]
        acts = (self.row or {}).get("actions") or {}
        cls = acts.get(action)
        if self.row is None or cls not in ((self.row or {}).get("action_classes") or []):
            base = self._base_record(action, str(cls or "author"), refs_l)
            self._receipt(base, "none", "skipped:not-registered")
            return self._refuse(argv, f"{action}: not a registered action of {self.script_id}")
        base = self._base_record(action, cls, refs_l)
        shapes = ((self.row or {}).get("argv") or {}).get(action) or []
        if not any(argv_matches_shape(list(argv), sh) for sh in shapes if isinstance(sh, list)):
            self._receipt(base, "none", "skipped:argv-mismatch")
            return self._refuse(argv, f"{action}: argv is not a registered shape for this action")
        d = self.decide(cls)
        if d["outcome"] != "allow":
            self._receipt(base, "none", f"skipped:{d['outcome']}-{d['rule_id'] or 'default'}")
            return self._refuse(argv, f"{d['outcome']} ({d['rule_id']}): {d['reason']}")
        intent = dict(base, type="intent", pid=os.getpid(), ppid=os.getppid())
        try:
            append_receipt(intent, home=self.home)
        except (OSError, ValueError) as exc:
            if d.get("receipt"):
                self._receipt(base, "none", "skipped:receipt-unwritable")
                return self._refuse(argv, f"receipt required and not writable ({exc})")
            self._notice(f"receipts not written ({exc})")
        gh = bool(needs_employer_gh and (self.row or {}).get("needs_employer_gh"))
        env = lift_env(dict(os.environ if self._env is None else self._env), needs_employer_gh=gh, root=self.root)
        proc = self._exec(argv, env, timeout)
        result = "ok" if proc.returncode == 0 else f"fail:{proc.returncode}"
        self._receipt(base, _credential(list(argv), self.res, env, self.root), result)
        return proc


def vetted_context(script_id: str, repo: Any, script_path: Any = None, *, home: Optional[Path] = None,
                   root: Optional[Path] = None, detection: Optional[dict] = None, device: str = "auto",
                   hostname: Optional[str] = None, env: Optional[dict] = None,
                   runner: Optional[Callable[..., subprocess.CompletedProcess]] = None,
                   assume_unpinned: bool = False, out: Any = print, cache: Any = None) -> VettedContext:
    """Context manager for a vetted script: blob checked against the pinned lock, policy(via=vetted)
    per action, `.run(argv, action, refs=(), needs_employer_gh=False)` with intent + receipt lines."""
    return VettedContext(script_id, repo, script_path, home=home, root=root, detection=detection, device=device,
                         hostname=hostname, env=env, runner=runner, assume_unpinned=assume_unpinned, out=out,
                         cache=cache)


# --------------------------------------------------------------------------- identity (T8, H17)

OVERRIDE_MAX_TTL_S = 24 * 3600
_TTL_RE = re.compile(r"^(\d+)([mh])$")
_TASK_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
FLOOR_EVENTS = ("pre-commit", "commit-msg", "pre-merge-commit", "pre-push")
FLOOR_RULES = ("I1", "I2", "IR1", "housekeeping-shape", "not-positively-personal")
_ZERO_SHA_RE = re.compile(r"^0{40}(?:0{24})?$")
_PY_COMM_RE = re.compile(r"^(?:python3?|Python|python3\.\d+)$")
_INTENT_TAIL_LINES = 2000


class OverrideError(ValueError):
    """An override request that is malformed (usage, exit 2)."""


def _identities(dev_t: dict) -> Dict[str, dict]:
    return {str(r.get("id")): r for r in dev_t.get("identities") or [] if isinstance(r, dict) and r.get("id")}


def _email_domain(email: str) -> str:
    # No "@" means no domain: a bare "example.com" user.email must not match an allowlisted domain.
    _local, at, dom = email.rpartition("@")
    return dom.casefold() if at else ""


def email_class(email: Optional[str], dev_t: dict) -> Optional[str]:
    """personal | employer | other (None for no email). Any personal marker wins (I1 denylist);
    employer means on the allowlist (declared employer identity or allowlisted domain)."""
    e = (email or "").strip().casefold()
    if not e:
        return None
    pm = dev_t.get("personal_markers") or {}
    if e in {str(x).casefold() for x in pm.get("emails") or []} or \
            _email_domain(e) in {str(x).casefold() for x in pm.get("email_domains") or []}:
        return "personal"
    ids = _identities(dev_t)
    for row in ids.values():
        if row.get("class") == "personal" and str(row.get("email", "")).casefold() == e:
            return "personal"
    ea = dev_t.get("employer_allowlist") or {}
    allowed = {str((ids.get(i) or {}).get("email", "")).casefold() for i in ea.get("identity_ids") or []}
    if e in allowed or _email_domain(e) in {str(x).casefold() for x in ea.get("email_domains") or []}:
        return "employer"
    return "other"


def _identity_id_of(email: Optional[str], dev_t: dict) -> Optional[str]:
    e = (email or "").strip().casefold()
    for iid, row in _identities(dev_t).items():
        if e and str(row.get("email", "")).casefold() == e:
            return iid
    return None


def identity_rule(family: str, device_id: str, dev_t: dict) -> Optional[dict]:
    """First identity rule whose family and device match ('*' matches any)."""
    for r in dev_t.get("identity_rules") or []:
        if not isinstance(r, dict):
            continue
        if r.get("family") in ("*", family) and r.get("device") in ("*", device_id):
            return r
    return None


def _overrides_path(home: Optional[Path]) -> Path:
    return ws_paths(home=home)["control"] / "overrides.json"


def _parse_z(ts: Any) -> Optional[datetime]:
    try:
        return datetime.strptime(str(ts), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _now(now: Optional[Callable[[], datetime]]) -> datetime:
    n = now() if callable(now) else now
    return n if isinstance(n, datetime) else datetime.now(timezone.utc)


def load_overrides(*, home: Optional[Path] = None) -> List[dict]:
    try:
        obj = json.loads(_overrides_path(home).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    rows = obj.get("overrides") if isinstance(obj, dict) else None
    return [r for r in rows or [] if isinstance(r, dict)]


def active_overrides(*, home: Optional[Path] = None, now: Any = None) -> List[dict]:
    """Unexpired, human-created overrides whose lifetime never exceeds 24 h (longer rows are void)."""
    t = _now(now)
    out = []
    for r in load_overrides(home=home):
        c, x = _parse_z(r.get("created")), _parse_z(r.get("expires"))
        if c is None or x is None or r.get("created_by") != "human":
            continue
        if (x - c).total_seconds() > OVERRIDE_MAX_TTL_S or not (c <= t < x):
            continue
        out.append(r)
    return out


def _git_run(args: List[str], cwd: Path, env: dict, git: str = "git",
             timeout: float = GIT_TIMEOUT_S) -> Optional[subprocess.CompletedProcess]:
    try:
        return subprocess.run([git, *args], cwd=str(cwd), env=env, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None


def _effective_git_identity(top: Path, env: dict, git: str) -> Tuple[Optional[str], Optional[str]]:
    """(name, email) as git resolves them for this repo under the given env (overlay included)."""
    e = {k: v for k, v in env.items() if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
    e["GIT_TERMINAL_PROMPT"] = "0"
    vals = []
    for key in ("user.name", "user.email"):
        r = _git_run(["config", "--get", key], top, e, git)
        vals.append(r.stdout.strip() or None if r is not None and r.returncode == 0 else None)
    return vals[0], vals[1]


def identity(*, repo: Optional[str] = None, family: str = "auto", device: str = "auto", root: Optional[Path] = None,
             env: Optional[dict] = None, ancestry: Optional[list] = None, home: Optional[Path] = None,
             isatty: Optional[dict] = None, hostname: Optional[str] = None, detection: Optional[dict] = None,
             cache: Any = None, now: Any = None, git: str = "git") -> dict:
    """The `identity` JSON (3c): expected, allowed[], effective{name,email_class}, invariants_hit[],
    flag, override, repo_class. Claude family -> the IR1 identity on every device; other families ->
    the device default. Only I1/I2 are invariants; a device mismatch is a flag."""
    dev_t = load_table("devices", root=root)
    t = _surfaces_or_fallback(root)
    fams = t.get("families") or {}
    e = dict(os.environ if env is None else env)
    det = detection if detection is not None else detect_surface(env=e, ancestry=ancestry, isatty=isatty, root=root)
    acting, walls = _walls(family, det, fams)
    walls_det = dict(det, family_for_walls=walls)
    cur = current_device(hostname=hostname, root=root) if device == "auto" else {"id": device, "notice": None}
    dev_id = str(cur.get("id") or "unknown")
    notices: List[str] = []
    if dev_id == "unknown" or cur.get("notice"):
        notices.append(cur.get("notice") or "unknown device: most restrictive rules, no default identity")
    rule = identity_rule(walls, dev_id, dev_t)
    ids = _identities(dev_t)
    emp_ids = [i for i in (dev_t.get("employer_allowlist") or {}).get("identity_ids") or [] if i in ids]
    res: Optional[dict] = None
    repo_class = None
    if repo:
        res = repo_resolve(repo, root=root, home=home, detection=walls_det, cache=cache)
        repo_class = res.get("owner_class")
    expected = rule.get("identity") if rule else None
    if repo_class == "employer":
        allowed = [] if walls == "claude" else list(emp_ids)
        if walls == "claude":
            expected = None
            notices.append("I2: a Claude-family actor never authors on an employer repo (route to Cursor or Codex)")
        elif expected not in allowed:
            if expected:
                notices.append(f"I1: the device default {expected} is not on the employer allowlist here")
            expected = allowed[0] if allowed else None
    elif walls == "claude":
        allowed = [expected] if expected else []
    else:
        allowed = list(ids)
    eff = {"name": None, "email_class": None, "identity": None, "read": False}
    if res is not None and res.get("path") and not _looks_like_slug(str(repo)):
        top = _find_top(_real(res["path"]))
        if top is not None and _may_read_repo_files(top, walls_det, root, home):
            name, email = _effective_git_identity(top, e, git)
            eff = {"name": name, "email_class": email_class(email, dev_t), "identity": _identity_id_of(email, dev_t),
                   "read": True}
        elif top is not None:
            notices.append("effective identity not read: a Claude chain reads checkouts under projects_root "
                           "from the cache only")
    hits: List[str] = []
    if repo_class == "employer" and eff["email_class"] not in (None, "employer"):
        hits.append("I1")
    if repo_class == "employer" and walls == "claude":
        hits.append("I2")
    flag = None
    ovr = None
    if rule and eff["email_class"] is not None and eff["identity"] != expected and "I1" not in hits:
        flag = (f"device mismatch ({rule.get('id')}): expected {expected or 'none'}, "
                f"effective {eff['identity'] or 'an undeclared identity'}")
        slug = _slug_of(res or {})
        if rule.get("override_suppresses") == "non-employer-repos-only" and repo_class not in ("employer", None) \
                and slug and eff["identity"]:
            for o in active_overrides(home=home, now=now):
                if str(o.get("repo", "")).casefold() == slug and o.get("identity") == eff["identity"]:
                    ovr = o
                    notices.append(f"override {o.get('id')} suppresses the device-mismatch flag until {o.get('expires')}")
                    flag = None
                    break
    return {"expected": expected, "allowed": allowed,
            "effective": {k: eff[k] for k in ("name", "email_class", "identity")},
            "invariants_hit": hits, "flag": flag, "override": ovr, "repo_class": repo_class,
            "rule": (rule or {}).get("id"), "family": walls, "acting_family": acting, "device": dev_id,
            "notice": "; ".join(notices) or None}


def _parse_ttl(ttl: str) -> int:
    m = _TTL_RE.match(str(ttl or "").strip())
    if not m:
        raise OverrideError("ttl must look like 8h or 90m")
    secs = int(m.group(1)) * (3600 if m.group(2) == "h" else 60)
    if secs <= 0 or secs > OVERRIDE_MAX_TTL_S:
        raise OverrideError("ttl must be more than 0 and at most 24h")
    return secs


def _slug_owner_class(slug: str, root: Optional[Path]) -> str:
    table = _try_table("context-remotes", root)
    if table is None:
        return "unknown"
    owner = slug.split("/", 1)[0].casefold()
    classes = [r.get("class") for r in table.get("owners") or []
               if isinstance(r, dict) and str(r.get("owner", "")).casefold() == owner and r.get("class") in CLASS_RANK]
    return max(classes, key=lambda c: CLASS_RANK[c]) if classes else "unknown"


def _override_refusals(*, env: dict, ancestry: Optional[list], isatty: Optional[dict], root: Optional[Path]) -> List[str]:
    reasons = []
    ac = agent_check(env=env, ancestry=ancestry, isatty=isatty, root=root)
    if not (ac.get("human") and ac.get("determined")):
        reasons += list(ac.get("reasons") or ["undetermined"])
    det = detect_surface(env=env, ancestry=ancestry, isatty=isatty, root=root)
    if det.get("family_for_walls") == "claude" or det.get("family") == "claude":
        reasons.append("claude family: Claude identity (IR1) is never overridable")
    return list(dict.fromkeys(reasons))


def _write_overrides(home: Optional[Path], rows: List[dict]) -> None:
    path = _overrides_path(home)
    tmp = path.with_name(path.name + ".tmp")
    fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        fh.write(json.dumps({"schema_version": SCHEMA_VERSION, "overrides": rows}, indent=2, ensure_ascii=False) + "\n")
    os.replace(tmp, path)


def override(*, task: Optional[str] = None, repo: Optional[str] = None, identity: Optional[str] = None,
             ttl: str = "8h", reason: Optional[str] = None, list_only: bool = False, revoke: Optional[str] = None,
             home: Optional[Path] = None, root: Optional[Path] = None, env: Optional[dict] = None,
             ancestry: Optional[list] = None, isatty: Optional[dict] = None, now: Any = None) -> dict:
    """The express override (item 7): human-only, TTY, expiring (<= 24 h), non-employer repos only.
    It suppresses ONLY the device-mismatch flag; I1 and I2 are untouched. Returns
    {exit, override, overrides, refused, reasons}. Writes control/overrides.json; never creates control/."""
    e = dict(os.environ if env is None else env)
    t = _now(now)
    if list_only:
        rows = []
        act = {r.get("id") for r in active_overrides(home=home, now=now)}
        for r in load_overrides(home=home):
            rows.append(dict(r, active=r.get("id") in act))
        return {"exit": EXIT_OK, "override": None, "overrides": rows, "refused": False, "reasons": []}
    reasons = _override_refusals(env=e, ancestry=ancestry, isatty=isatty, root=root)
    if revoke is None:
        slug = str(repo or "").strip().casefold()
        if not re.fullmatch(r"[a-z0-9_.-]+/[a-z0-9_.-]+", slug):
            raise OverrideError("--repo takes OWNER/REPO")
        cls = _slug_owner_class(slug, root)
        if cls == "employer":
            reasons.append("employer repo: an override never applies to an employer repo (I1)")
        elif cls == "unknown":
            reasons.append("owner not declared in context-remotes.json: cannot prove the repo is non-employer")
        try:
            dev_t = load_table("devices", root=root)
        except TableError as exc:
            raise OverrideError(f"devices table unavailable ({exc})") from exc
        if identity not in _identities(dev_t):
            raise OverrideError(f"--identity must be a declared identity ({', '.join(_identities(dev_t))})")
        if not task or not _TASK_RE.match(task):
            raise OverrideError("--task takes a short slug")
        if not str(reason or "").strip():
            raise OverrideError("--reason is required (Sean's words)")
        secs = _parse_ttl(ttl)
    if reasons:
        return {"exit": EXIT_REFUSED, "override": None, "overrides": [], "refused": True, "reasons": reasons}
    if not ws_paths(home=home)["control"].is_dir():
        return {"exit": EXIT_NOTFOUND, "override": None, "overrides": [], "refused": False,
                "reasons": ["control/ is absent (a human runs workspace-doctor.sh --install-pin)"]}
    rows = load_overrides(home=home)
    if revoke is not None:
        kept = [r for r in rows if r.get("id") != revoke]
        if len(kept) == len(rows):
            return {"exit": EXIT_NOTFOUND, "override": None, "overrides": rows, "refused": False,
                    "reasons": [f"no override {revoke}"]}
        _write_overrides(home, kept)
        return {"exit": EXIT_OK, "override": None, "overrides": kept, "refused": False, "reasons": []}
    rows = [r for r in rows if (_parse_z(r.get("expires")) or t) > t]
    day = t.strftime("%Y%m%d")
    n = 1 + sum(1 for r in rows if str(r.get("id", "")).startswith(f"ovr-{day}-"))
    new = {"id": f"ovr-{day}-{n:02d}", "task": task, "repo": slug, "identity": identity,
           "created": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
           "expires": datetime.fromtimestamp(t.timestamp() + secs, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "reason": str(reason).strip(), "created_by": "human"}
    rows.append(new)
    _write_overrides(home, rows)
    return {"exit": EXIT_OK, "override": new, "overrides": rows, "refused": False, "reasons": []}


# --------------------------------------------------------------------------- Claude git floor (T8, H17/H18)


def _floor_allow(notice: Optional[str] = None) -> dict:
    return {"decision": "allow", "rule": None, "reason": "", "notice": notice}


def _floor_block(rule: str, reason: str) -> dict:
    return {"decision": "block", "rule": rule, "reason": reason, "notice": None}


def _push_lines(stdin_lines: List[str]) -> List[dict]:
    out = []
    for ln in stdin_lines or []:
        parts = str(ln).split()
        if len(parts) != 4:
            out.append({"bad": True, "raw_parts": len(parts)})
            continue
        out.append({"local_ref": parts[0], "local_sha": parts[1], "remote_ref": parts[2], "remote_sha": parts[3]})
    return out


def _short_ref(ref: str) -> str:
    return ref[len("refs/heads/"):] if ref.startswith("refs/heads/") else ref


def _floor_git_env(env: dict) -> dict:
    return _clean_git_env(env)


def _range_idents(top: Path, line: dict, remote: str, env: dict, git: str,
                  gitdir: Optional[Path] = None) -> Optional[List[Tuple[str, str, str]]]:
    """(sha, author email, committer email) for every commit the ref line would publish; None on error."""
    if _ZERO_SHA_RE.match(line["local_sha"]):
        return []
    fmt = (["--git-dir", str(gitdir)] if gitdir is not None else []) + [
        "-c", "log.showSignature=false", "log", "--no-color", "--format=%H%x00%ae%x00%ce"]
    r = None
    if not _ZERO_SHA_RE.match(line["remote_sha"]):
        r = _git_run(fmt + [f"{line['remote_sha']}..{line['local_sha']}"], top, env, git)
    if r is None or r.returncode != 0:
        r = _git_run(fmt + [line["local_sha"], "--not", f"--remotes={remote}"], top, env, git)
    if r is None or r.returncode != 0:
        return None
    out = []
    for row in r.stdout.splitlines():
        parts = row.split("\x00")
        if len(parts) == 3:
            out.append((parts[0], parts[1], parts[2]))
    return out


_TAG_CHAIN_MAX = 16


class _TagChainTooDeep(Exception):
    """A tag chain longer than _TAG_CHAIN_MAX: never legitimate, so the floor blocks it."""


def _tag_taggers(top: Path, line: dict, env: dict, git: str,
                 gitdir: Optional[Path] = None) -> Optional[List[Tuple[str, str]]]:
    """(tag object sha, tagger email) for the annotated tag the ref line publishes and every tag it
    peels through (a tag of a tag); [] for a deletion or a non-tag object; None on a git error or a
    chain longer than _TAG_CHAIN_MAX raises _TagChainTooDeep. `git tag` runs no hook, so pre-push is where a tagger is seen."""
    sha = line["local_sha"]
    if _ZERO_SHA_RE.match(sha):
        return []
    pre = ["--git-dir", str(gitdir)] if gitdir is not None else []
    out: List[Tuple[str, str]] = []
    for _ in range(_TAG_CHAIN_MAX):
        t = _git_run(pre + ["cat-file", "-t", sha], top, env, git)
        if t is None or t.returncode != 0:
            return None
        if t.stdout.strip() != "tag":
            return out
        r = _git_run(pre + ["cat-file", "tag", sha], top, env, git)
        if r is None or r.returncode != 0:
            return None
        head = r.stdout.split("\n\n", 1)[0].splitlines()
        target = next((h[len("object "):].strip() for h in head if h.startswith("object ")), "")
        tagger = next((h for h in head if h.startswith("tagger ")), "")
        m = re.search(r"<([^<>]*)>", tagger)
        out.append((sha, m.group(1) if m else ""))
        if not re.fullmatch(r"[0-9a-f]{40}(?:[0-9a-f]{24})?", target):
            return None
        sha = target
    raise _TagChainTooDeep(line["local_sha"])


def _push_idents(top: Path, line: dict, remote: str, env: dict, git: str,
                 gitdir: Optional[Path] = None) -> Tuple[Optional[List[Tuple[str, str, str, str]]], bool]:
    """((object kind, sha, role, email) for every identity a ref line publishes, tags_readable).
    Author and committer of each commit in the range (the I1 range reader) and the tagger of each
    annotated tag it pushes (W3-01). The two parts are independent: an unreadable tag never switches
    off the commit check. The list is None only when the commit range cannot be read; an unreadable
    tag gives tags_readable False; a tag chain past _TAG_CHAIN_MAX raises _TagChainTooDeep."""
    idents = _range_idents(top, line, remote, env, git, gitdir)
    tags = _tag_taggers(top, line, env, git, gitdir)
    if idents is None:
        return None, tags is not None
    out = [("annotated tag", sha, "tagger", em) for sha, em in (tags or [])]
    for sha, ae, ce in idents:
        out += [("commit", sha, "author", ae), ("commit", sha, "committer", ce)]
    return out, tags is not None


def _other_remotes_with(top: Path, sha: str, remote: str, env: dict, git: str,
                        gitdir: Optional[Path] = None) -> List[str]:
    """Names of the remotes other than `remote` whose remote-tracking refs contain `sha` ([] on a git
    error). Used only to word an IR1 block (W3-03): tracking refs are local and can be set to any
    commit without a hook, so they never exempt a commit from the check."""
    pre = ["--git-dir", str(gitdir)] if gitdir is not None else []
    r = _git_run(pre + ["for-each-ref", "--contains", sha, "--format=%(refname)", "refs/remotes/"], top, env, git)
    if r is None or r.returncode != 0:
        return []
    out: List[str] = []
    for ref in r.stdout.split():
        parts = ref.split("/")
        if len(parts) >= 4 and parts[2] != remote and parts[2] not in out:
            out.append(parts[2])
    return out


def _workspace_checkouts(home: Optional[Path], root: Optional[Path]) -> List[Path]:
    """The `root` pointer's checkout and its linked worktrees (read from its .git/worktrees only)."""
    cands: List[Path] = []
    if root is not None:
        cands.append(Path(root))
    try:
        lines = ws_paths(home=home)["root_file"].read_text(encoding="utf-8").splitlines()
        if lines and lines[0].strip():
            cands.append(Path(lines[0].strip()))
    except OSError:
        pass
    out: List[Path] = []
    for c in cands:
        for p in [c] + _linked_worktrees(c):
            if all(_cf(_real(p)) != _cf(_real(x)) for x in out):
                out.append(p)
    return out


def _admin_gitdir_target(admin: Path, named: str) -> Path:
    """The worktree `.git` path a linked worktree's admin-dir `gitdir` file names: absolute as written,
    or (a --relative-paths worktree) relative to the admin dir holding that file (W3-04)."""
    p = Path(named)
    return p if p.is_absolute() else Path(os.path.normpath(str(admin / p)))


def _linked_worktrees(ws: Path) -> List[Path]:
    out = []
    try:
        for d in sorted((ws / ".git" / "worktrees").iterdir()):
            try:
                gd = (d / "gitdir").read_text(encoding="utf-8").strip()
            except OSError:
                continue
            if gd:
                out.append(_admin_gitdir_target(d, gd).parent)
    except OSError:
        pass
    return out


def _nearest_python(chain: List[dict]) -> Optional[dict]:
    for hop in chain:
        if _PY_COMM_RE.match(str(hop.get("comm") or "")):
            return hop
    return None


def _vetted_ancestor(chain: List[dict], *, home: Optional[Path], root: Optional[Path]) -> Tuple[Optional[dict], str]:
    """({script, pid, path}, why) when the nearest python ancestor runs a registered script whose
    bytes match the pinned lock; (None, why) otherwise. Registry and lock come from lib/current."""
    hop = _nearest_python(chain)
    if hop is None:
        return None, "no python ancestor (model-composed)"
    args = str(hop.get("args") or "").split()
    flags = ""
    i = 1
    while i < len(args) and re.fullmatch(r"-[IEsSBuqbO]+", args[i]):
        flags += args[i][1:]
        i += 1
    if i >= len(args) or args[i].startswith("-"):
        return None, "the python ancestor runs no script path"
    script = args[i]
    if not os.path.isabs(script):
        return None, "the python ancestor names its script by a relative path (vetted scripts re-exec by absolute path)"
    if "I" not in flags:
        return None, "the python ancestor does not run isolated (-I), so PYTHONPATH or site hooks could change it"
    lc = ws_paths(home=home)["lib_current"]
    try:
        lock = json.loads((lc / "vetted.lock.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, "no pinned vetted.lock.json"
    reg = _try_table("vetted-scripts", lc)
    if reg is None or not isinstance(lock, dict):
        return None, "the pinned lib carries no vetted-scripts.json"
    roots = _workspace_checkouts(home, root)
    for row in reg.get("scripts") or []:
        if not isinstance(row, dict):
            continue
        ent = next((s for s in lock.get("scripts") or [] if isinstance(s, dict) and s.get("id") == row.get("id")), None)
        if ent is None or not ent.get("blob") or ent.get("path") != row.get("path"):
            continue
        rel = str(row.get("path"))
        files: List[Path] = []
        if any(_cf(_real(script)) == _cf(_real(r / rel)) for r in roots):
            files = [Path(script)]
        for f in files:
            try:
                if git_blob_sha(f) == ent.get("blob"):
                    return {"script": row.get("id"), "pid": hop.get("pid"), "path": rel}, "vetted"
            except OSError:
                continue
        if files:
            return None, f"{rel}: bytes differ from the pinned blob"
    return None, "the python ancestor is not a registered vetted script"


def _intent_matches(pid: Any, script: str, refs: List[str], home: Optional[Path]) -> bool:
    path = ws_paths(home=home)["control"] / "receipts.jsonl"
    try:
        lines = path.read_text(encoding="utf-8").splitlines()[-_INTENT_TAIL_LINES:]
    except OSError:
        return False
    want = sorted(_short_ref(r) for r in refs)
    for ln in reversed(lines):
        try:
            rec = json.loads(ln)
        except ValueError:
            continue
        if not isinstance(rec, dict) or rec.get("type") != "intent" or rec.get("script") != script:
            continue
        if str(rec.get("pid")) != str(pid):
            continue
        if sorted(_short_ref(str(r)) for r in rec.get("refs") or []) == want:
            return True
    return False


def _push_url_class(url: str, root: Optional[Path]) -> str:
    table = _try_table("context-remotes", root)
    blocked = str((table or {}).get("blocked_scheme") or "")
    if blocked and url.startswith(blocked):
        return "employer"
    norm, alias = _normalize_remote_ex(url, root=root)
    if norm is None:
        return "none"
    cls = _owner_row_class(table or {}, norm["host"], norm["owner"])[0]
    if cls == "unknown" and (alias or {}).get("credential_scope") == "work":
        return "employer"
    return cls


def _gitfile_top(gitdir: Path, cwd: Path) -> Optional[Path]:
    """The work tree of a linked worktree or submodule whose admin dir git exported as GIT_DIR (git
    does that for every hook it runs there): the hook's cwd, or the tree the admin dir's `gitdir`
    file names (an absolute path, or a --relative-paths one taken relative to the admin dir), as
    long as that tree's own .git points back at the admin dir. The second candidate does not depend
    on the cwd, so a linked worktree's admin dir used as GIT_DIR from anywhere resolves to that
    worktree (same repository, same config, same owner class). None when neither candidate points
    back, e.g. a submodule's admin dir used from outside its tree."""
    cands = [Path(cwd)]
    try:
        named = (gitdir / "gitdir").read_text(encoding="utf-8").strip()
        if named:
            cands.append(_admin_gitdir_target(gitdir, named).parent)
    except OSError:
        pass
    want = _cf(_real(gitdir))
    for c in cands:
        gd, _common = _git_paths(c)
        if gd is not None and _cf(_real(gd)) == want:
            return c
    return None


def _floor_locate(cwd: Path, e: dict, git: str) -> Tuple[Optional[Path], Optional[Path]]:
    """(git dir, work tree top) the way git finds them: GIT_DIR first, else discovery from cwd (bare
    repos included). With GIT_DIR the work tree is, whatever the cwd, the parent of a `<top>/.git`
    dir, GIT_WORK_TREE's tree, or the tree _gitfile_top finds for an admin dir (a linked worktree's
    admin dir, with absolute or --relative-paths gitdir files, resolves to its worktree); it is None
    for a bare repo and for an admin dir that no tree points back at."""
    loc = _clean_git_env(e)
    for k in ("GIT_DIR", "GIT_WORK_TREE"):
        if e.get(k):
            loc[k] = str(e[k])
    r = _git_run(["rev-parse", "--absolute-git-dir"], cwd, loc, git)
    gitdir = Path(r.stdout.strip()) if r is not None and r.returncode == 0 and r.stdout.strip() else None
    if e.get("GIT_DIR"):
        top = None
        if gitdir is not None and gitdir.name == ".git" and (gitdir.parent / ".git").exists():
            top = gitdir.parent
        elif e.get("GIT_WORK_TREE"):
            top = _find_top(_real(Path(cwd) / str(e["GIT_WORK_TREE"])))
        elif gitdir is not None:
            top = _gitfile_top(gitdir, Path(cwd))
        return gitdir, top
    top = _find_top(cwd)
    if gitdir is None and top is not None:
        gd, _common = _git_paths(top)
        gitdir = gd
    return gitdir, top


def _main_checkout(top: Path) -> Optional[Path]:
    """The main checkout of a linked worktree: the work tree of its common dir, or the common dir
    itself for a bare repository. None when `top` is not a linked worktree (a main checkout or a
    submodule has no separate common dir)."""
    gd, common = _git_paths(top)
    if gd is None or common is None or _cf(_real(gd)) == _cf(_real(common)):
        return None
    c = _real(common)
    return c.parent if c.name == ".git" else c


def _floor_config_remotes(cwd: Path, gitdir: Optional[Path], e: dict, git: str) -> Optional[List[str]]:
    """Every remote url/pushurl as git itself resolves the repo config ([include], includeIf, legacy
    [remote.x] sections, inline comments). The caller's GIT_CONFIG_* and -c are not honoured. None
    when git cannot read the config."""
    loc = _clean_git_env(e)
    args = (["--git-dir", str(gitdir)] if gitdir is not None else []) + [
        "config", "--get-regexp", r"^remote\..*\.(push)?url$"]
    r = _git_run(args, cwd, loc, git)
    if r is None or r.returncode not in (0, 1):
        return None
    out = []
    for ln in r.stdout.splitlines():
        parts = ln.split(None, 1)
        if len(parts) == 2 and parts[1].strip():
            out.append(parts[1].strip())
    return out


def _commit_idents(cwd: Path, e: dict, git: str) -> List[Tuple[str, str]]:
    """[(role, email)] for the author and committer identity git will record for this commit, read
    with the hook's own env (so the overlay include, -c and the GIT_AUTHOR_* that commit exports all
    count). A role git has no identity for is left out."""
    genv = dict(e)
    genv["GIT_TERMINAL_PROMPT"] = "0"
    out = []
    for role, var in (("author", "GIT_AUTHOR_IDENT"), ("committer", "GIT_COMMITTER_IDENT")):
        r = _git_run(["var", var], cwd, genv, git)
        m = re.search(r"<([^<>]*)>", r.stdout) if r is not None and r.returncode == 0 else None
        if m:
            out.append((role, m.group(1)))
    return out


def floor_decide(event: str, hook_args: list, stdin_lines: list, *, env: Optional[dict] = None,
                 ancestry: Optional[list] = None, root: Optional[Path] = None, home: Optional[Path] = None,
                 cwd: Optional[Any] = None, cache: Any = None, ps: Optional[Callable[[str], str]] = None,
                 git: str = "git") -> dict:
    """The Claude git floor: {decision: allow|block, rule, reason, notice}.

    Employer repo: every commit event blocks (I2); pre-push allows only the vetted housekeeping
    shape (all ref lines delete non-default branches, the nearest python ancestor runs a
    registered script whose blob matches the pinned lock, and that pid wrote an intent line for
    exactly those refs), after an I1 identity check over every commit in the pushed range.
    Any other repo: a commit event whose author or committer identity is an employer identity
    blocks, and so does a push whose range (the I1 range reader) holds a commit with an employer
    author or committer, which catches commits no commit hook saw (revert, cherry-pick, rebase,
    am): IR1. A Claude commit event never records the device's employer identity, and a Claude push
    to a non-employer remote never publishes a commit that carries it. A local rewrite (revert,
    cherry-pick, rebase, am) can still record it locally until that push is refused. The tagger of an
    annotated tag the push publishes (and of every tag it peels through) meets the same rule as a
    commit's author and committer, at IR1 and at I1. A commit already on another remote (a fork's
    upstream) is still refused, since remote-tracking refs are local and forgeable; the reason then
    names that remote. An unreadable range or tag allows with a notice, as for I1.
    Not positively personal under projects_root blocks; a linked worktree is classified by its own
    top and by its main checkout (under projects_root when either is). An infrastructure error
    allows, with a notice (fail-open): the transport block stays the barrier for employer remotes.
    """
    try:
        return _floor(event, list(hook_args or []), list(stdin_lines or []), env=env, ancestry=ancestry, root=root,
                      home=home, cwd=cwd, cache=cache, ps=ps, git=git)
    except Exception as exc:  # noqa: BLE001 - the floor fails open on infrastructure errors
        return _floor_allow(f"floor infrastructure error ({exc.__class__.__name__}); allowing")


def _floor(event: str, hook_args: List[str], stdin_lines: List[str], *, env: Optional[dict], ancestry: Optional[list],
           root: Optional[Path], home: Optional[Path], cwd: Optional[Any], cache: Any,
           ps: Optional[Callable[[str], str]], git: str) -> dict:
    if event not in FLOOR_EVENTS:
        return _floor_allow(f"unknown hook event {event!r}; allowing")
    e = dict(os.environ if env is None else env)
    here = _real(cwd if cwd is not None else os.getcwd())
    url_cls = "none"
    if event == "pre-push" and len(hook_args) >= 2:
        # args: the remote name (the URL itself when none was configured) and the URL after insteadOf.
        cls2 = [_push_url_class(str(a), root) for a in hook_args[:2]]
        url_cls = max(cls2, key=lambda c: CLASS_RANK.get(c, -1))
    gitdir, top = _floor_locate(here, e, git)
    if gitdir is None and top is None:
        if url_cls == "employer":
            return _floor_block("I2", "pre-push: a Claude-family push to an employer remote from an unlocatable "
                                      "repository; route this work to Cursor or Codex")
        return _floor_allow("not inside a repository; allowing")
    det = {"family": "claude", "family_for_walls": "claude", "agent_possible": True}
    if top is not None:
        res = repo_resolve(str(top), root=root, home=home, detection=det, cache=cache)
        main = _main_checkout(top)
        if main is not None:
            # A linked worktree counts as its main checkout too: under projects_root when either is, and
            # the cache-only rule and employer path globs apply to both (W-07).
            mres = repo_resolve(str(main), root=root, home=home, detection=det, cache=cache)
            res = dict(res, owner_class=max((res.get("owner_class"), mres.get("owner_class")),
                                            key=lambda c: CLASS_RANK.get(str(c), CLASS_RANK["unknown"])),
                       positively_personal=bool(res.get("positively_personal") and mres.get("positively_personal")),
                       in_projects_root=bool(res.get("in_projects_root") or mres.get("in_projects_root")))
    else:
        res = {"owner_class": "unknown", "positively_personal": False, "remotes": [],
               "in_projects_root": False}
    cfg_urls = _floor_config_remotes(here, gitdir, e, git)
    cfg_cls = [_push_url_class(u, root) for u in cfg_urls or []]
    employer = res.get("owner_class") == "employer" or url_cls == "employer" or "employer" in cfg_cls
    if cfg_urls is None and event != "pre-push" and not employer and (res.get("remotes") or top is None):
        return _floor_block("I2", f"{event}: git cannot read this repository's remote config, so it is not "
                                  "positively personal for a Claude-family actor; fix the config, then retry")
    if not employer:
        dev_t = _try_table("devices", root) or {}
        ir1_notice = None
        if event != "pre-push":
            for role, em in _commit_idents(here, e, git):
                if email_class(em, dev_t) == "employer":
                    return _floor_block("IR1", f"{event}: the {role} identity is an employer identity; a Claude-family "
                                               "commit never carries it (IR1); set this repo's user.name and "
                                               "user.email to the personal identity, then retry")
        else:
            remote = str(hook_args[0]) if hook_args else "origin"
            genv = _floor_git_env(e)
            for ln in _push_lines(stdin_lines):
                if ln.get("bad"):
                    continue
                try:
                    idents, tags_ok = _push_idents(top if top is not None else here, ln, remote, genv, git, gitdir)
                except _TagChainTooDeep as exc:
                    return _floor_block("IR1", f"annotated tag chain from {str(exc)[:12]} is longer than "
                                               f"{_TAG_CHAIN_MAX} tags; its taggers cannot be checked (IR1)")
                if not tags_ok:
                    ir1_notice = "IR1 tag check unavailable (git error)"
                if idents is None:
                    ir1_notice = "IR1 range check unavailable (git error)"
                    continue
                for kind, sha, role, em in idents:
                    if email_class(em, dev_t) == "employer":
                        seen = _other_remotes_with(top if top is not None else here, sha, remote, genv, git, gitdir) \
                            if kind == "commit" else []
                        if seen:
                            names = ", ".join(f"'{n}'" for n in seen)
                            return _floor_block("IR1", f"{kind} {sha[:12]} in the push has an employer identity as "
                                                       f"{role}; it is already on remote {names} (by its local "
                                                       f"tracking refs) but not on '{remote}', and a Claude-family "
                                                       "push never publishes it to a non-employer remote (IR1); "
                                                       "push a branch that does not carry it, or leave this push "
                                                       "to a human outside Claude")
                        return _floor_block("IR1", f"{kind} {sha[:12]} in the push has an employer identity "
                                                   f"as {role}; a Claude-family push never publishes it to a "
                                                   "non-employer remote (IR1); rewrite it with the personal "
                                                   "identity, then retry")
        if res.get("positively_personal"):
            return _floor_allow(ir1_notice)
        pr = projects_root(root=root, home=home)
        where_p = _real(top if top is not None else gitdir)
        under = bool(res.get("in_projects_root")) or (_is_under(where_p, pr) and _cf(where_p) != _cf(pr))
        if under:
            return _floor_block("not-positively-personal",
                                "this checkout under projects_root (or a linked worktree of one) is not positively "
                                "personal for a Claude actor (unknown, third-party or uncached); fix: run `python3 "
                                "09-tools/profile_resolve.py scan` in a plain terminal, then retry")
        outside = None if not (res.get("remotes") or cfg_urls) else \
            f"{res.get('owner_class')} repo outside projects_root; the floor allows it"
        return _floor_allow("; ".join(m for m in (ir1_notice, outside) if m) or None)
    if event != "pre-push":
        return _floor_block("I2", f"{event}: a Claude-family actor never commits on an employer repo; "
                                  "route this work to Cursor or Codex")
    lines = _push_lines(stdin_lines)
    remote = str(hook_args[0]) if hook_args else "origin"
    genv = _floor_git_env(e)
    notice = None
    dev_t = _try_table("devices", root) or {}
    for ln in lines:
        if ln.get("bad"):
            continue
        try:
            idents, tags_ok = _push_idents(top if top is not None else here, ln, remote, genv, git, gitdir)
        except _TagChainTooDeep as exc:
            return _floor_block("I1", f"annotated tag chain from {str(exc)[:12]} is longer than "
                                      f"{_TAG_CHAIN_MAX} tags; its taggers cannot be checked (I1)")
        if not tags_ok:
            notice = "I1 tag check unavailable (git error)"
        if idents is None:
            notice = "I1 range check unavailable (git error)"
            continue
        for kind, sha, role, em in idents:
            cls = email_class(em, dev_t)
            if cls != "employer":
                what = "a personal identity" if cls == "personal" else "an identity not on the employer allowlist"
                return _floor_block("I1", f"{kind} {sha[:12]} in the push has {what} as {role}; "
                                          "an employer repo takes only employer identities (rewrite it in "
                                          "Cursor or Codex with the employer identity)")
    _cur, dflt = _repo_heads(top) if top is not None else (None, None)
    all_deletes = bool(lines) and all(
        not ln.get("bad") and _ZERO_SHA_RE.match(ln["local_sha"]) and ln["remote_ref"].startswith("refs/heads/")
        and _ref_kind(ln["remote_ref"], dflt) == "non-default" for ln in lines)
    if ancestry is None:
        raw, err = _walk_ancestry_ex(None, ps, 12)
        if err:
            return _floor_block("I2", f"a Claude-family push to an employer repo: ancestry unavailable ({err}), so "
                                      "vetted housekeeping cannot be verified; run the vetted script with the "
                                      "sandbox off for that one command, or route to Cursor or Codex")
        chain = _norm_chain(raw)
    else:
        chain = _norm_chain(ancestry)
    anc, why = _vetted_ancestor(chain, home=home, root=root)
    if anc is None:
        return _floor_block("I2", f"a Claude-family push to an employer repo outside vetted housekeeping ({why}); "
                                  "run the vetted script (prune-our-branches) or route to Cursor or Codex")
    if not all_deletes:
        return _floor_block("housekeeping-shape", f"{anc['script']} may push only deletions of non-default branches")
    refs = [ln["remote_ref"] for ln in lines]
    if not _intent_matches(anc["pid"], str(anc["script"]), refs, home):
        return _floor_block("housekeeping-shape", f"no intent line from {anc['script']} (pid {anc['pid']}) for "
                                                  "exactly these refs")
    return _floor_allow(notice or f"vetted housekeeping by {anc['script']}")


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
    p = sub.add_parser("policy", parents=[common])
    p.add_argument("--repo", required=True)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--action-class")
    g.add_argument("--command")
    p.add_argument("--family", default="auto")
    p.add_argument("--device", default="auto")
    p.add_argument("--via", choices=list(POLICY_VIA), default="composed")
    p = sub.add_parser("classify", parents=[common])
    p.add_argument("--command", required=True)
    p = sub.add_parser("vetted-status", parents=[common])
    p.add_argument("script_id")
    p = sub.add_parser("identity", parents=[common])
    p.add_argument("--repo")
    p.add_argument("--family", default="auto")
    p.add_argument("--device", default="auto")
    p = sub.add_parser("override", parents=[common])
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--task")
    g.add_argument("--list", action="store_true", dest="list_only")
    g.add_argument("--revoke")
    p.add_argument("--repo")
    p.add_argument("--identity")
    p.add_argument("--ttl", default="8h")
    p.add_argument("--reason")
    p = sub.add_parser("floor", parents=[common])
    p.add_argument("--event", required=True, choices=list(FLOOR_EVENTS))
    p.add_argument("--remote", nargs=2, metavar=("NAME", "URL"))
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
        if cmd == "policy":
            try:
                r = policy(repo=args.repo, action_class=args.action_class, command=args.command, family=args.family,
                           device=args.device, via=args.via, root=root)
            except PolicyError as exc:
                print(f"profile_resolve policy: {exc}", file=sys.stderr)
                return EXIT_USAGE
            _emit(cmd, r, as_json)
            return EXIT_OK if r["outcome"] == "allow" else EXIT_FAIL
        if cmd == "classify":
            _emit(cmd, {"invocations": classify_command(args.command, cwd=os.getcwd(), root=root)}, as_json)
            return EXIT_OK
        if cmd == "vetted-status":
            st = vetted_status(args.script_id, root=root)
            _emit(cmd, {k: st[k] for k in ("script", "status", "pinned_sha", "notice")}, as_json)
            return EXIT_OK if st["status"] == "vetted" else EXIT_FAIL
        if cmd == "identity":
            r = identity(repo=args.repo, family=args.family, device=args.device, root=root)
            _emit(cmd, r, as_json)
            return EXIT_FAIL if r["invariants_hit"] else EXIT_OK
        if cmd == "override":
            try:
                r = override(task=args.task, repo=args.repo, identity=args.identity, ttl=args.ttl, reason=args.reason,
                             list_only=args.list_only, revoke=args.revoke, root=root)
            except OverrideError as exc:
                print(f"profile_resolve override: {exc}", file=sys.stderr)
                return EXIT_USAGE
            if r["refused"]:
                print(f"override refused: {'; '.join(r['reasons'])}", file=sys.stderr)
            _emit(cmd, {k: r[k] for k in ("override", "overrides", "refused", "reasons")}, as_json)
            return int(r["exit"])
        if cmd == "floor":
            lines = [] if args.event != "pre-push" or sys.stdin.isatty() else \
                [ln.rstrip("\n") for ln in sys.stdin.read().splitlines() if ln.strip()]
            d = floor_decide(args.event, list(args.remote or []), lines, root=root)
            _emit(cmd, d, as_json)
            if d["decision"] == "block":
                print(f"ws-claude-wall: blocked [{d['rule']}] {d['reason']}", file=sys.stderr)
                return EXIT_FAIL
            return EXIT_OK
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


AP_FIXTURES = TOOLS / "fixtures" / "action_policy"
CLAUDE_ANC = [{"comm": "claude"}]
_ORACLE_ORDER = ("P00", "P05", "P10", "P11", "P12", "P13", "P14", "P20", "P19", "P21", "P22", "P40", "P30", "P31",
                 "P32", "P33", "P50")


def _t7_fixture_root(tmp: Path) -> Path:
    """A synthetic workspace root with every table: T2's fixtures plus the T7 mirror and registry."""
    root = tmp / "t7-home" / "Projects" / "ws"
    for name in ("devices", "context-remotes", "surfaces"):
        _write(root / TABLE_PATHS[name], (FIXTURES / f"{name}.json").read_text(encoding="utf-8"))
    for name in ("action-policy", "vetted-scripts"):
        _write(root / TABLE_PATHS[name], (AP_FIXTURES / f"{name}.json").read_text(encoding="utf-8"))
    _write(root / "AGENTS.md", "# fixture workspace\n")
    _fake_repo(root, {"origin": "https://github.com/pat-sample/ws.git"})
    return root


def _oracle(f: dict) -> str:
    """Item 9 written out independently of the table (dev-a = work, dev-b = personal)."""
    fam, dev, oc, ac = f["walls_family"], f["device"], f["owner_class"], f["action_class"]
    agent = f["chain_has_agent"]
    if not agent:
        return "allow"
    if f["hook_bypass"]:
        return "deny"
    if fam == "claude":
        if oc == "employer":
            if ac in ("meta", "housekeeping"):
                return "allow" if (dev == "dev-a" and f["via"] == "vetted") else "deny"
            if ac in ("content-read", "author", "publish"):
                return "route"
            return "deny"
        if not f["positively_personal"] and f["under_projects_root"]:
            return "deny"
        if not f["under_projects_root"] and not f["has_remote"]:
            return "allow"
        if not f["positively_personal"] and not f["under_projects_root"]:
            return "allow" if ac in ("meta", "content-read") else "deny"
    if dev == "dev-b" and oc == "employer" and ac in ("author", "publish", "merge"):
        return "deny"
    if fam in ("cursor", "codex") and dev == "dev-a" and oc == "employer":
        if ac == "merge":
            return "deny"
        if ac in ("author", "publish") and f["target_ref"] in ("default", "unknown"):
            return "deny"
        return "allow"
    if fam in ("cursor", "codex") and not f["under_projects_root"] and not f["has_remote"]:
        return "allow"  # P33 (Sean 2026-09-24): local scratch dirs, as P19 is for Claude
    if oc == "personal":
        return "allow"
    return "deny"


def _matrix_facts() -> List[dict]:
    rows = []
    fams = {"claude": True, "cursor": True, "codex": True, "unknown-agent": True, "human": False}
    shapes = {
        "employer": [(False, True, True), (False, False, True)],
        "personal": [(True, True, True), (True, False, True)],
        "third-party": [(False, True, True), (False, False, True)],
        "unknown": [(False, True, True), (False, False, True), (False, False, False), (False, True, False)],
    }
    for fam, agent in fams.items():
        for dev in ("dev-a", "dev-b", "unknown"):
            for oc, shape_list in shapes.items():
                for pp, under, remote in shape_list:
                    for ac in ACTION_CLASSES:
                        for via in POLICY_VIA:
                            for tr in POLICY_TARGET_REFS:
                                for bypass in (False, True):
                                    rows.append({"walls_family": fam, "acting_family": fam, "device": dev,
                                                 "owner_class": oc, "role": oc, "positively_personal": pp,
                                                 "under_projects_root": under, "has_remote": remote,
                                                 "repo_conflict": False, "action_class": ac, "via": via,
                                                 "target_ref": tr, "chain_has_agent": agent, "hook_bypass": bypass})
    return rows


def _git_env(home: Path) -> dict:
    return {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home), "XDG_CONFIG_HOME": str(home / ".config"),
            "GIT_CONFIG_NOSYSTEM": "1", "LANG": "C", "LC_ALL": "C", "GIT_TERMINAL_PROMPT": "0"}


def _g(env: dict, *args: str, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(cwd) if cwd else None, env=env, capture_output=True, text=True,
                          timeout=60)


def _employer_pair(tmp: Path, home: Path, slug: str = "acme-corp/widget", where: Optional[Path] = None
                   ) -> Tuple[Path, Path, dict]:
    """(clone, bare) for an employer-shaped repo whose ssh URL reaches a local bare remote.

    The temp HOME's gitconfig maps `git@github.com:` to the local bare root (the stand-in for the
    network); the overlay's longer transport-block prefix wins over it, exactly as on the machine.
    """
    env = _git_env(home)
    bare_root = tmp / "remotes"
    bare = bare_root / f"{slug}.git"
    bare.parent.mkdir(parents=True, exist_ok=True)
    _g(env, "init", "-q", "--bare", "-b", "main", str(bare))
    gc = home / ".gitconfig"
    if not gc.exists() or "insteadOf" not in gc.read_text(encoding="utf-8"):
        _write(gc, f'[url "file://{bare_root}/"]\n\tinsteadOf = git@github.com:\n'
                   "[user]\n\tname = Fixture Person\n\temail = fixture@example.invalid\n")
    clone = where or (tmp / "elsewhere" / slug.replace("/", "-"))
    clone.parent.mkdir(parents=True, exist_ok=True)
    _g(env, "init", "-q", "-b", "main", str(clone))
    _g(env, "remote", "add", "origin", f"git@github.com:{slug}.git", cwd=clone)
    _write(clone / "README.md", "fixture\n")
    _g(env, "add", "README.md", cwd=clone)
    _g(env, "commit", "-q", "-m", "base", cwd=clone)
    _g(env, "push", "-q", "origin", "main", cwd=clone)
    _g(env, "switch", "-q", "-c", "feat/done", cwd=clone)
    _write(clone / "done.txt", "done\n")
    _g(env, "add", "done.txt", cwd=clone)
    _g(env, "commit", "-q", "-m", "done", cwd=clone)
    _g(env, "push", "-q", "origin", "feat/done", cwd=clone)
    _g(env, "switch", "-q", "main", cwd=clone)
    _g(env, "remote", "set-head", "origin", "main", cwd=clone)
    return clone, bare, env


def _overlay_env(base: dict, blocked: str, prefixes: List[str], extra: Optional[List[Tuple[str, str]]] = None) -> dict:
    """A v4-shaped Claude overlay env: kept entries, then the transport block."""
    pairs = list(extra or [])
    pairs += [(f"url.{blocked}.insteadOf", p) for p in prefixes]
    env = dict(base, WS_CLAUDE_OVERLAY="v4", GH_CONFIG_DIR=str(Path(base["HOME"]) / "gh-claude"))
    env["GIT_CONFIG_COUNT"] = str(len(pairs))
    for i, (k, v) in enumerate(pairs):
        env[f"GIT_CONFIG_KEY_{i}"] = k
        env[f"GIT_CONFIG_VALUE_{i}"] = v
    return env


def _v4_fixture_env(base: dict) -> Optional[dict]:
    """Today's rendered overlay env, with its employer owners swapped for synthetic ones.

    Reads 00-bootstrap/dist/claude-overlay.env (D-W1-4: the overlay left the settings fragment) and the
    committed context-remotes table in memory only; nothing employer-named is written or printed.
    """
    try:
        text = (ROOT / "00-bootstrap" / "dist" / "claude-overlay.env").read_text(encoding="utf-8")
        cr = load_table("context-remotes")
    except (OSError, ValueError):
        return None
    env_in = {}
    for ln in text.splitlines():
        m = re.match(r"^export ([A-Z][A-Z0-9_]*)='((?:[^']|'\\'')*)'$", ln)
        if m:
            env_in[m.group(1)] = m.group(2).replace("'\\''", "'")
    if "GIT_CONFIG_COUNT" not in env_in:
        return None
    swap = {}
    for row in cr.get("owners") or []:
        if row.get("class") == "employer":
            swap[str(row["owner"])] = "acme-corp" if row.get("host") == "github.com" else "acme-bb"
    env = dict(base)
    for k, v in env_in.items():
        v = str(v)
        if v.startswith("~/"):
            v = str(Path(base["HOME"]) / v[2:])
        for real, fake in swap.items():
            v = v.replace(f":{real}/", f":{fake}/").replace(f"/{real}/", f"/{fake}/")
        env[k] = v
    return env


def _pin_fixture(home: Path, root: Path, script_rel: str, blob: Optional[str], sha: str = "a" * 40) -> Path:
    """What `--install-pin` leaves behind, for a temp HOME only: lib/<sha> + current + control/."""
    base = ws_paths(home=home)["base"]
    lib = base / "lib" / sha
    for name in ("devices", "context-remotes", "surfaces", "action-policy", "vetted-scripts"):
        src = root / TABLE_PATHS[name]
        _write(lib / TABLE_PATHS[name], src.read_text(encoding="utf-8"))
    lock = {"schema_version": 1, "pinned_sha": sha, "scripts": []}
    reg = json.loads((lib / TABLE_PATHS["vetted-scripts"]).read_text(encoding="utf-8"))
    for s in reg.get("scripts") or []:
        lock["scripts"].append({"id": s["id"], "path": s["path"], "blob": blob if s["path"] == script_rel else None})
    _write(lib / "vetted.lock.json", json.dumps(lock))
    cur = base / "lib" / "current"
    if cur.is_symlink() or cur.exists():
        cur.unlink()
    cur.symlink_to(lib)
    (base / "control").mkdir(parents=True, exist_ok=True)
    (base / "telemetry").mkdir(parents=True, exist_ok=True)
    return lib


def _t7_self_test(tmp: Path, ok: Callable[[Any, str], None]) -> None:
    root = _t7_fixture_root(tmp)
    home = tmp / "t7-home"
    table = load_table("action-policy", root=root)

    # ---- tables: schema only; T7 never writes the committed rows
    v = validate_tables(root=root, require_all=False)
    ok(v["tables"]["action-policy"]["ok"] and v["tables"]["vetted-scripts"]["ok"], "T7 fixture tables validate")
    real_ap = _try_table("action-policy", None)
    if real_ap is not None:
        ok(not validate_table("action-policy", real_ap), "committed action-policy.json validates")
        ok([r.get("id") for r in real_ap["rules"]] == [r.get("id") for r in table["rules"]]
           and [r.get("id") for r in real_ap["verb_map"]] == [r.get("id") for r in table["verb_map"]],
           "fixture mirrors the committed rule and verb ids in order")
        ok([r[:3] for r in (x.get("id", "") for x in real_ap["rules"])] == list(_ORACLE_ORDER),
           "the oracle covers every committed rule in order")
    real_vs = _try_table("vetted-scripts", None)
    if real_vs is not None:
        ok(not validate_table("vetted-scripts", real_vs), "committed vetted-scripts.json validates")
    for label, mutate, needle in (
        ("unknown class in when", lambda t: t["rules"][2]["when"].__setitem__("action_class", ["mischief"]),
         "unknown value 'mischief'"),
        ("unknown verb class", lambda t: t["verb_map"][0].__setitem__("class", "mischief"), "unknown class"),
        ("missing default_outcome", lambda t: t.pop("default_outcome"), "missing key 'default_outcome'"),
        ("unknown when key", lambda t: t["rules"][0]["when"].__setitem__("mood", True), "unknown key 'mood'"),
        ("proposed without undecided", lambda t: t["rules"][0].__setitem__("proposed", "deny"), "'proposed'"),
        ("bad via", lambda t: t["rules"][2]["when"].__setitem__("via", ["trusted"]), "unknown value 'trusted'"),
        ("unknown verb key", lambda t: t["verb_map"][0].__setitem__("sneaky", 1), "unknown key 'sneaky'"),
        ("duplicate rule id", lambda t: t["rules"].append(dict(t["rules"][0])), "duplicate id"),
    ):
        bad = json.loads(json.dumps(table))
        mutate(bad)
        errs = validate_table("action-policy", bad)
        ok(any(needle in e for e in errs), f"action-policy negative: {label} ({errs[:2]})")
    bad = json.loads((AP_FIXTURES / "vetted-scripts.json").read_text(encoding="utf-8"))
    bad["scripts"][0]["actions"]["merge-it"] = "merge"
    ok(any("not in the row's action_classes" in e for e in validate_table("vetted-scripts", bad)),
       "vetted-scripts negative: an action outside the row's classes")
    bad = json.loads((AP_FIXTURES / "vetted-scripts.json").read_text(encoding="utf-8"))
    bad["scripts"][0]["path"] = "../elsewhere.py"
    ok(any("repo-relative" in e for e in validate_table("vetted-scripts", bad)), "vetted-scripts negative: .. path")

    # ---- decide(): the full family x device x owner x action matrix against the oracle
    mism = []
    rows = _matrix_facts()
    for f in rows:
        got = policy_decide(f, table)["outcome"]
        want = _oracle(f)
        if got != want:
            mism.append((f, got, want))
    ok(not mism, f"matrix ({len(rows)} cases) matches the item-9 oracle; first mismatch: {mism[:1]}")
    d = policy_decide({"walls_family": "codex", "acting_family": "codex", "device": "dev-b", "owner_class": "employer",
                       "action_class": "author", "chain_has_agent": True, "hook_bypass": False}, table)
    ok(d["rule_id"] == "P40-agent-personal-mbp-employer" and d["outcome"] == "deny", "P40 row denies on dev-b")
    d = policy_decide({"walls_family": "claude", "device": "dev-a", "owner_class": "unknown", "action_class": "meta",
                       "positively_personal": False, "under_projects_root": False, "has_remote": False,
                       "chain_has_agent": True, "hook_bypass": False}, table)
    ok(d["rule_id"] == "P19-claude-no-remote-outside-root" and d["outcome"] == "allow", "P19 row")
    d = policy_decide({"walls_family": "claude", "device": "dev-a", "owner_class": "third-party",
                       "action_class": "content-read", "positively_personal": False, "under_projects_root": False,
                       "has_remote": True, "chain_has_agent": True, "hook_bypass": False}, table)
    ok(d["rule_id"] == "P21-claude-unknown-owner-outside-root" and d["outcome"] == "allow", "P21 row")
    d = policy_decide({"walls_family": "claude", "device": "dev-a", "owner_class": "third-party",
                       "action_class": "author", "positively_personal": False, "under_projects_root": False,
                       "has_remote": True, "chain_has_agent": True, "hook_bypass": False}, table)
    ok(d["rule_id"] == "P22-claude-unknown-owner-outside-root-other" and d["outcome"] == "deny", "P22 row")
    und = json.loads(json.dumps(table))
    und["rules"].insert(0, {"id": "PX-undecided", "when": {"owner_class": ["third-party"]}, "outcome": "undecided",
                            "proposed": "allow"})
    d = policy_decide({"owner_class": "third-party"}, und)
    ok(d["outcome"] == "deny" and d["rule_outcome"] == "undecided", "undecided evaluates as the table says (deny)")
    ok(policy_decide({"owner_class": "nobody-knows"}, table)["outcome"] == "deny", "no match -> default_outcome deny")
    # smoke pass over the committed table (real device ids)
    if real_ap is not None:
        smoke = [
            ({"walls_family": "claude", "device": "work-mbp", "owner_class": "employer", "action_class": "housekeeping",
              "via": "vetted", "chain_has_agent": True, "hook_bypass": False}, "allow"),
            ({"walls_family": "claude", "device": "work-mbp", "owner_class": "employer", "action_class": "housekeeping",
              "via": "composed", "chain_has_agent": True, "hook_bypass": False}, "deny"),
            ({"walls_family": "claude", "device": "personal-mbp", "owner_class": "employer", "action_class": "meta",
              "via": "vetted", "chain_has_agent": True, "hook_bypass": False}, "deny"),
            ({"walls_family": "claude", "device": "work-mbp", "owner_class": "employer", "action_class": "author",
              "via": "composed", "chain_has_agent": True, "hook_bypass": False}, "route"),
            ({"walls_family": "cursor", "device": "work-mbp", "owner_class": "employer", "action_class": "merge",
              "chain_has_agent": True, "hook_bypass": False}, "deny"),
            ({"walls_family": "cursor", "device": "work-mbp", "owner_class": "employer", "action_class": "publish",
              "target_ref": "non-default", "chain_has_agent": True, "hook_bypass": False}, "allow"),
            ({"walls_family": "codex", "device": "personal-mbp", "owner_class": "employer", "action_class": "author",
              "chain_has_agent": True, "hook_bypass": False}, "deny"),
            ({"walls_family": "human", "chain_has_agent": False, "owner_class": "employer"}, "allow"),
            ({"walls_family": "cursor", "chain_has_agent": True, "hook_bypass": True, "owner_class": "personal"}, "deny"),
        ]
        bad = [(f, w) for f, w in smoke if policy_decide(f, real_ap)["outcome"] != w]
        ok(not bad, f"smoke pass over the committed table: {bad[:1]}")

    # ---- verb map and parse_command
    def cls(text: str, **kw: Any) -> List[Tuple[str, str, bool]]:
        return [(i["class"], i["target_ref"], i["hook_bypass"])
                for i in classify_command(text, cwd=str(tmp), root=root,
                                          detection={"family_for_walls": "human", "agent_possible": False}, **kw)]

    ok(cls("git rebase main") == [("author", "none", False)], "unknown git verb -> author")
    ok(cls("ls -la")[0][0] == "author", "unknown tool -> author")
    ok(cls("git commit -m x", current_branch="main") == [("author", "default", False)], "commit on main: default")
    ok(cls("git commit -m x", current_branch="feat/a") == [("author", "non-default", False)], "commit on feat: non-default")
    ok(cls("git push") == [("merge", "unknown", False)], "implicit push refspec is unknown, treated as default (merge)")
    ok(cls("git push origin feat/a")[0][:2] == ("publish", "non-default"), "explicit non-default push is publish")
    ok(cls("git push origin HEAD:main")[0][:2] == ("merge", "default"), "push to default is merge")
    ok(cls("git push origin --delete feat/done")[0][:2] == ("housekeeping", "non-default"), "push --delete is housekeeping")
    ok(cls("git push origin --delete main")[0][0] == "merge", "push --delete of the default is not housekeeping")
    ok(cls("git push origin :feat/x")[0][0] == "publish", "a colon-delete without --delete stays publish")
    ok(cls("git branch -d feat/x")[0][0] == "housekeeping" and cls("git branch -D feat/x")[0][0] == "author"
       and cls("git branch -d --force feat/x")[0][0] == "author", "branch -d housekeeping; -D and --force author")
    ok(cls("git merge --ff-only origin/main", current_branch="main")[0][0] == "housekeeping"
       and cls("git merge --ff-only origin/main", current_branch="feat")[0][0] == "author", "ff-only on default only")
    ok([c for c, _t, _b in cls("gh pr list; gh pr create; gh pr merge 3; gh api x")] == ["meta", "publish", "merge", "author"],
       "gh verbs")
    ok(cls("git status && git fetch && git show HEAD") == [("meta", "none", False), ("meta", "none", False),
                                                           ("content-read", "none", False)], "meta and content-read")
    for text, why in (("git -c hook.pre-push.command=true push origin feat/a", "-c hook.*"),
                      ("git -c core.hooksPath=/dev/null commit -m x", "core.hooksPath"),
                      ("git -c url.x://.insteadOf=git@github.com: push", "-c url.*"),
                      ("git commit --no-verify -m x", "--no-verify"), ("git commit -n -m x", "commit -n"),
                      ("git commit -anm x", "commit -anm"), ("GIT_CONFIG_COUNT=0 git push", "GIT_CONFIG_COUNT=0"),
                      ("env -u GIT_CONFIG_COUNT git push", "env -u"), ("env -i git push", "env -i"),
                      ("export GIT_CONFIG_PARAMETERS=x; git push", "export"),
                      ("GIT_CONFIG_VALUE_3=false git push origin feat/a", "GIT_CONFIG_VALUE_<n>=false on push"),
                      ("env -u GIT_CONFIG_KEY_3 git commit -m x", "env -u GIT_CONFIG_KEY_<n> on commit"),
                      ("GIT_CONFIG_SYSTEM=/tmp/x git push origin feat/a", "GIT_CONFIG_SYSTEM= on push"),
                      ("git -c include.path=/tmp/x push origin feat/a", "-c include.path"),
                      ("git --config-env=include.path=V push", "--config-env include.path"),
                      ("git -c includeIf.onbranch:*.path=/tmp/x commit -m x", "-c includeIf.*"),
                      ("git -c alias.pp='push --no-verify' pp origin feat/a", "-c alias.*"),
                      ("GIT_CONFIG_KEY_3+=x git commit -m x", "GIT_CONFIG_KEY_<n>+= (append form)"),
                      ("HOME+=x git commit -m x", "HOME+= on git (append form)"),
                      ("git push --no-verif origin feat/a", "push --no-verif (abbreviation)"),
                      ("git commit --no-veri -m x", "commit --no-veri (abbreviation)"),
                      ("bash -lc 'git push --no-verify origin feat/a'", "bash -lc"),
                      ("env -u GH_CONFIG_DIR gh api -X DELETE repos/acme-corp/w/git/refs/heads/x", "env -u GH_CONFIG_DIR"),
                      ("GH_CONFIG_DIR=/tmp/x gh pr merge 1", "GH_CONFIG_DIR override"),
                      ("GH_TOKEN=t gh pr merge 1 -R acme-corp/w", "GH_TOKEN"), ("GITHUB_TOKEN=t gh api x", "GITHUB_TOKEN"),
                      ("HOME=/tmp/x git push origin --delete feat/h1", "HOME= on git"),
                      ("env HOME=/tmp/x git commit -m x", "env HOME= on git"),
                      ("PYTHONPATH=/tmp/x git commit -m x", "PYTHONPATH= on git"),
                      ("PATH=/tmp/x:/usr/bin git push origin feat/a", "PATH= on git"),
                      ("XDG_CONFIG_HOME=/tmp/x git push origin feat/a", "XDG_CONFIG_HOME= on git")):
        ok(any(b for _c, _t, b in cls(text)), f"hook_bypass: {why}")
    ok(not any(b for _c, _t, b in cls("git commit -m 'no -n here' && git push origin feat/a")), "no false bypass")
    ok(not any(b for _c, _t, b in cls("HOME=/tmp/x ls && GH_TOKEN=t ls")), "no false bypass for other tools")
    ok(not any(b for _c, _t, b in cls("GIT_TRACE=1 MY_GIT_CONFIG_VALUE_1=x GIT_CONFIG_KEYRING=x git push origin feat/a")),
       "unrelated env on git is not hook_bypass")
    ok(not any(b for _c, _t, b in cls("git commit --no-verbose -m x")), "commit --no-verbose is not hook_bypass")
    p = parse_command("GIT_CONFIG_KEY_3+=x git commit -m x")
    ok(len(p) == 1 and p[0]["tool"] == "git" and p[0]["env_prefix"] == {"GIT_CONFIG_KEY_3": "x"},
       f"append-form assignment is an env prefix, and git is the tool: {p}")
    p = parse_command("cd /x/y && FOO=1 command /usr/bin/git -C ../z --work-tree w status")
    ok(len(p) == 1 and p[0]["tool"] == "git" and p[0]["argv"] == ["status"] and p[0]["cwd_hint"] == "/x/z/w"
       and p[0]["env_prefix"] == {"FOO": "1"}, f"cd, env prefix, command, abs git, -C, --work-tree: {p}")
    p = parse_command("sh -c \"bash -lc 'gh --repo acme-corp/w pr merge 1'\"")
    ok(len(p) == 1 and p[0]["tool"] == "gh" and p[0]["argv"] == ["pr", "merge", "1"]
       and p[0]["repo_hint"] == "acme-corp/w", "recursive sh -c / bash -lc and gh --repo")
    p = parse_command("git --git-dir=/r/.git log")
    ok(p[0]["cwd_hint"] == "/r" and p[0]["argv"] == ["log"], "--git-dir")
    ok(parse_command("git commit -m 'unbalanced")[0]["tool"] == "?", "unparseable -> one unknown invocation")
    ok(cls("echo hi > notes.txt")[0][0] == "author", "a redirect write is fs-write (author)")

    # ---- policy() on temp repos, injected detections
    claude = detect_surface(env={}, ancestry=CLAUDE_ANC, isatty=HUMAN_TTY, root=root)
    human = detect_surface(env={}, ancestry=[{"comm": "zsh"}], isatty=HUMAN_TTY, root=root)
    cursor = detect_surface(env={"CURSOR_AGENT": "1"}, ancestry=[], isatty=NO_TTY, root=root)
    emp, bare, genv = _employer_pair(tmp, home)
    pers = _fake_repo(tmp / "elsewhere" / "mine", {"origin": "git@github.com:pat-sample/mine.git"})

    def pol(det: dict, **kw: Any) -> dict:
        kw.setdefault("repo", str(emp))
        kw.setdefault("device", "dev-a")
        return policy(root=root, home=home, detection=det, **kw)

    r = pol(claude, command="git push origin --delete feat/done")
    ok(r["outcome"] == "deny" and r["rule_id"] == "P11-claude-employer-composed",
       f"composed push --delete under a Claude chain is denied: {r['rule_id']}")
    r = pol(detect_surface(env={"WS_VETTED": "1", "WS_WALL_OK": "1"}, ancestry=CLAUDE_ANC, isatty=HUMAN_TTY, root=root),
            command="WS_VETTED=1 WS_WALL_OK=1 git push origin --delete feat/done")
    ok(r["outcome"] == "deny" and r["facts"]["via"] == "composed", "hand-set WS_VETTED / WS_WALL_OK is denied")
    r = pol(claude, command="git push origin --delete feat/done", via="vetted")
    ok(r["outcome"] == "allow" and r["rule_id"] == "P10-claude-employer-vetted" and r["receipt"], "vetted what-if: P10")
    r = pol(claude, command="git push origin --delete feat/done", via="vetted", device="dev-b")
    ok(r["outcome"] == "deny", "vetted housekeeping is work-device only")
    hof = ws_paths(home=home)["telemetry"] / "handoffs.jsonl"
    r = pol(claude, command="git commit -m x")
    ok(r["outcome"] == "route" and r["route_to"] == ["cursor", "codex"] and "route: cursor or codex" in r["reason"]
       and not r["handoff_written"], "author on employer routes; no telemetry/ means no handoff write")
    ws_paths(home=home)["telemetry"].mkdir(parents=True, exist_ok=True)
    r = pol(claude, command="git commit -m x")
    lines = hof.read_text(encoding="utf-8").splitlines() if hof.exists() else []
    ok(r["handoff_written"] and len(lines) == 1 and json.loads(lines[0])["repo_slug"] == "acme-corp/widget"
       and "/" not in json.loads(lines[0])["summary"], "a route on a Claude host appends one handoff (no paths)")
    r = pol(claude, command="git fetch && git commit -m x")
    ok(r["outcome"] == "deny", "multi-invocation: the most restrictive outcome wins")
    r = pol(claude, repo=str(pers), command=f"cd {emp} && git push origin --delete feat/done")
    ok(r["outcome"] == "deny" and r["facts"]["owner_class"] == "employer", "cd into another repo is evaluated there")
    for text, why in ((f"GIT_DIR={emp}/.git git push origin main", "GIT_DIR= prefix"),
                      (f"env GIT_DIR={emp}/.git git push origin main", "env GIT_DIR="),
                      (f"export GIT_DIR={emp}/.git; git commit -m x", "export GIT_DIR"),
                      (f"GIT_WORK_TREE={emp} git commit -m x", "GIT_WORK_TREE= prefix"),
                      (f"pushd {emp} && git commit -m x", "pushd"),
                      ("popd && git commit -m x", "popd (undeterminable target)"),
                      ("cd \"$OLDPWD\" && git push origin main", "cd to a variable (undeterminable target)")):
        r = pol(claude, repo=str(pers), command=text)
        ok(r["outcome"] != "allow" and r["facts"]["owner_class"] == "employer",
           f"{why}: the employer (or most restrictive) target is evaluated, not the personal base: {r['outcome']} "
           f"{r['rule_id']} {r['facts'].get('owner_class')}")
    r = pol(claude, repo=str(pers), command="git push origin --delete feat/old")
    ok(r["outcome"] == "allow" and r["rule_id"] == "P50-personal", "personal repo allows under Claude")
    r = pol(human, command="git push origin --delete feat/done")
    ok(r["outcome"] == "allow" and r["rule_id"] == "P00-human", "humans are not policy-gated")
    r = pol(cursor, command="git commit -m x")
    ok(r["outcome"] == "deny" and r["rule_id"] == "P31-cc-work-employer-default", "cursor author on default is denied")
    _g(genv, "switch", "-q", "feat/done", cwd=emp)
    r = pol(cursor, command="git commit -m x")
    ok(r["outcome"] == "allow" and r["rule_id"] == "P32-cc-work-employer", "cursor author on a feature branch")
    _g(genv, "switch", "-q", "main", cwd=emp)
    r = pol(cursor, command="git commit --no-verify -m x")
    ok(r["outcome"] == "deny" and r["rule_id"] == "P05-agent-hook-bypass", "agent hook bypass is denied (P05)")
    r = pol(human, family="cursor", command="git push origin main")
    ok(r["outcome"] == "deny" and r["facts"]["walls_family"] == "cursor", "--family tightens a human context")
    r = pol(claude, family="cursor", command="git push origin feat/x")
    ok(r["facts"]["walls_family"] == "claude", "--family never loosens a Claude chain")
    try:
        pol(claude, action_class="mischief")
        ok(False, "unknown --action-class is a usage error")
    except PolicyError:
        ok(True, "")

    # ---- lift_env: drops only the transport block
    blocked = str(load_table("context-remotes", root=root)["blocked_scheme"])
    keep = [("includeIf.hasconfig:remote.*.url:git@github.com:pat-sample/**.path", "/h/claude-identity.inc"),
            ("hook.ws-floor.command", "ws-hook --host git --floor claude"), ("hook.ws-floor.event", "pre-push"),
            ("credential.https://github.com.helper", ""), ("url.https://github.com/pat-sample/.insteadOf", "git@github.com:pat-sample/")]
    src = _overlay_env(_git_env(home), blocked, ["git@github.com:acme-corp/", "git@bitbucket.org:acme-bb/"], keep)
    n = int(src["GIT_CONFIG_COUNT"])
    src[f"GIT_CONFIG_KEY_{n}"] = f"URL.{blocked}.PUSHINSTEADOF"
    src[f"GIT_CONFIG_VALUE_{n}"] = "https://github.com/acme-corp/"
    src[f"GIT_CONFIG_KEY_{n + 1}"] = "hook.late.event"
    src[f"GIT_CONFIG_VALUE_{n + 1}"] = "pre-commit"
    src["GIT_CONFIG_COUNT"] = str(n + 2)
    src.update(GIT_AUTHOR_NAME="x", GIT_AUTHOR_EMAIL="x@example.invalid", GIT_COMMITTER_NAME="y",
               GIT_COMMITTER_DATE="0", WS_SURFACE_FAMILY="claude")
    lifted = lift_env(src, root=root)
    got = [(lifted[f"GIT_CONFIG_KEY_{i}"], lifted[f"GIT_CONFIG_VALUE_{i}"]) for i in range(int(lifted["GIT_CONFIG_COUNT"]))]
    ok(got == keep + [("hook.late.event", "pre-commit")], f"lift_env keeps every non-transport entry in order: {got}")
    ok(not any(k.startswith(("GIT_AUTHOR_", "GIT_COMMITTER_")) for k in lifted), "lift_env unsets author and committer")
    ok(lifted.get("WS_SURFACE_FAMILY") == "claude" and lifted.get("GH_CONFIG_DIR") == src["GH_CONFIG_DIR"]
       and lifted.get("WS_CLAUDE_OVERLAY") == "v4", "lift_env keeps WS_SURFACE_FAMILY, the overlay marker and gh-claude")
    ok(not ({k for k in lifted if k.startswith("WS_")} - {k for k in src if k.startswith("WS_")}), "lift_env adds no WS marker")
    ok("GH_CONFIG_DIR" not in lift_env(src, needs_employer_gh=True, root=root), "employer gh restores the default gh")
    same = {k: v for k, v in src.items() if not re.fullmatch(r"GIT_CONFIG_(COUNT|KEY_\d+|VALUE_\d+)", k)
            and not k.startswith(("GIT_AUTHOR_", "GIT_COMMITTER_"))}
    ok(all(lifted.get(k) == v for k, v in same.items()), "lift_env leaves every other variable untouched")
    v4 = _v4_fixture_env(_git_env(home))
    if v4 is not None:
        lv4 = lift_env(v4)
        n4 = int(v4["GIT_CONFIG_COUNT"])
        realb = str(load_table("context-remotes").get("blocked_scheme"))
        kept4 = [(v4[f"GIT_CONFIG_KEY_{i}"], v4[f"GIT_CONFIG_VALUE_{i}"]) for i in range(n4)
                 if not v4[f"GIT_CONFIG_KEY_{i}"].startswith(f"url.{realb}.")]
        got4 = [(lv4[f"GIT_CONFIG_KEY_{i}"], lv4[f"GIT_CONFIG_VALUE_{i}"]) for i in range(int(lv4["GIT_CONFIG_COUNT"]))]
        ok(got4 == kept4 and len(got4) < n4, "lift_env over today's rendered overlay drops exactly its transport block")

    # ---- vetted_status and the pinned lock
    script_rel = "09-tools/fixture-housekeeper.py"
    script = _write(root / script_rel, "# fixture housekeeper\n")
    home_np = tmp / "t7-nopin"
    ok(vetted_status("fixture-housekeeper", home=home_np, root=root)["status"] == "unpinned", "no lib: unpinned")
    lib = _pin_fixture(home, root, script_rel, git_blob_sha(script))
    st = vetted_status("fixture-housekeeper", home=home, root=root)
    ok(st["status"] == "vetted" and st["pinned_sha"] == "a" * 40, f"pinned blob matches: vetted ({st['status']})")
    ok(vetted_status("nobody", home=home, root=root)["status"] == "not-registered", "not-registered")
    blob_git = _g(genv, "hash-object", str(script)).stdout.strip()
    ok(blob_git == git_blob_sha(script), "Python blob equals git hash-object")
    _write(script, "# fixture housekeeper, edited after the pin\n")
    ok(vetted_status("fixture-housekeeper", home=home, root=root)["status"] == "hash-mismatch", "edited script: mismatch")

    # ---- composed vs vetted push --delete: synthetic employer repo, local bare remote
    base_env = _overlay_env(_git_env(home), blocked, ["git@github.com:acme-corp/", "git@bitbucket.org:acme-bb/"])
    comp = _g(base_env, "push", "origin", "--delete", "feat/done", cwd=emp)
    still = _g(genv, "--git-dir", str(bare), "show-ref", "--verify", "--quiet", "refs/heads/feat/done").returncode == 0
    ok(comp.returncode != 0 and still, "the transport block makes a composed employer push --delete fail")
    printed: List[str] = []
    with vetted_context("fixture-housekeeper", str(emp), script, home=home, root=root, detection=claude, device="dev-a",
                        env=base_env, out=printed.append) as ctx:
        denied = ctx.run(["git", "push", "origin", "--delete", "feat/done"], action="remote-branch-delete",
                         refs=["refs/heads/feat/done"])
    ok(denied.returncode == 126 and ctx.status["status"] == "hash-mismatch", "hash mismatch: the vetted run is denied")
    ok(_g(genv, "--git-dir", str(bare), "show-ref", "--verify", "--quiet", "refs/heads/feat/done").returncode == 0,
       "hash mismatch: the remote branch is untouched")
    _write(script, "# fixture housekeeper\n")
    rec_path = ws_paths(home=home)["control"] / "receipts.jsonl"
    before = rec_path.read_text(encoding="utf-8").splitlines() if rec_path.exists() else []
    printed.clear()
    with vetted_context("fixture-housekeeper", str(emp), script, home=home, root=root, detection=claude, device="dev-a",
                        env=base_env, out=printed.append) as ctx:
        done = ctx.run(["git", "push", "origin", "--delete", "feat/done"], action="remote-branch-delete",
                       refs=["refs/heads/feat/done"])
        undeclared = ctx.run(["git", "commit", "--allow-empty", "-m", "x"], action="commit")
    gone = _g(genv, "--git-dir", str(bare), "show-ref", "--verify", "--quiet", "refs/heads/feat/done").returncode != 0
    ok(done.returncode == 0 and gone, f"the same refs through the vetted path succeed (lifted env): {done.stderr[-200:]}")
    ok(undeclared.returncode == 126, "an action the registry does not declare is refused")
    new = [json.loads(x) for x in rec_path.read_text(encoding="utf-8").splitlines()[len(before):]]
    intents = [x for x in new if x["type"] == "intent"]
    receipts = [x for x in new if x["type"] == "receipt"]
    ok(len(intents) == 1 and intents[0]["pid"] == os.getpid() and intents[0]["refs"] == ["refs/heads/feat/done"],
       "one intent line (pid, refs) before the remote action")
    ok(len(receipts) == 2 and receipts[0]["result"] == "ok" and receipts[0]["repo_slug"] == "acme-corp/widget"
       and receipts[0]["action"] == "remote-branch-delete" and receipts[0]["credential"] == "ssh:github.com"
       and receipts[0]["family"] == "claude" and receipts[0]["device"] == "dev-a"
       and receipts[1]["result"].startswith("skipped:"), f"receipts name repo, action and credential: {receipts[:1]}")
    ok(printed and printed[0].startswith("receipt {"), "the receipt is printed")
    text = rec_path.read_text(encoding="utf-8")
    ok("://" not in text and str(tmp) not in text and "Fixture Person" not in text, "receipts carry no URL, path or identity")
    cs = None
    try:
        import importlib.util as _ilu

        spec = _ilu.spec_from_file_location("ws_check_secrets_t7", TOOLS / "check-secrets.py")
        if spec is not None and spec.loader is not None:
            cs = _ilu.module_from_spec(spec)
            sys.modules["ws_check_secrets_t7"] = cs
            spec.loader.exec_module(cs)
    except Exception:  # noqa: BLE001 - optional cross-check
        cs = None
    if cs is not None:
        ok(not cs.findings_in_text(text), "receipts pass the check-secrets secret class")
        rules = cs.EmpRules(load_table("context-remotes", root=root))
        hits = {rule for _line, rule in rules.scan_text(text)}
        masked = {rule for _line, rule in rules.scan_text(text.replace("acme-corp/widget", "slug-field"))}
        ok(hits and not masked, f"receipts pass the employer-substance class outside the declared repo_slug field: {masked}")

    # ---- argv binding: a registered action runs only its declared argv shapes (stub runner; nothing executes)
    seen_argv: List[List[str]] = []

    def stub(argv: List[str], **_kw: Any) -> subprocess.CompletedProcess:
        seen_argv.append(list(argv))
        return subprocess.CompletedProcess(list(argv), 0, "", "")

    n0 = len(rec_path.read_text(encoding="utf-8").splitlines())
    with vetted_context("fixture-housekeeper", str(emp), script, home=home, root=root, detection=claude, device="dev-a",
                        env=base_env, out=None, runner=stub) as ctx:
        m1 = ctx.run(["gh", "pr", "merge", "7", "--admin", "-R", "acme-corp/widget"], action="pr-list",
                     needs_employer_gh=True)
        m2 = ctx.run(["git", "push", "--force", "origin", "HEAD:main"], action="remote-branch-delete",
                     refs=["refs/heads/main"])
        m3 = ctx.run(["git", "push", "origin", "--delete", "feat/x:main"], action="remote-branch-delete")
        m4 = ctx.run(["git", "push", "origin", "--delete", "feat/ok"], action="remote-branch-delete",
                     refs=["refs/heads/feat/ok"])
    tail = [json.loads(x) for x in rec_path.read_text(encoding="utf-8").splitlines()[n0:]]
    mism = [x for x in tail if x.get("type") == "receipt" and x.get("result") == "skipped:argv-mismatch"]
    ok(m1.returncode == 126 and m2.returncode == 126 and m3.returncode == 126 and len(mism) == 3
       and seen_argv == [["git", "push", "origin", "--delete", "feat/ok"]] and m4.returncode == 0,
       f"argv binding: another verb under a registered label is refused with a receipt: {seen_argv} {mism[:1]}")

    # ---- pin lag: a vault registry edit without a pin advance keeps the old behaviour
    vault_reg = json.loads((root / TABLE_PATHS["vetted-scripts"]).read_text(encoding="utf-8"))
    vault_reg["scripts"][0]["actions"]["tag-delete"] = "housekeeping"
    _write(root / TABLE_PATHS["vetted-scripts"], json.dumps(vault_reg))
    with vetted_context("fixture-housekeeper", str(emp), script, home=home, root=root, detection=claude, device="dev-a",
                        env=base_env, out=None) as ctx:
        lagged = ctx.run(["git", "push", "origin", "--delete", "refs/tags/v1"], action="tag-delete", refs=["refs/tags/v1"])
    ok(lagged.returncode == 126, "a registry edit with no pin advance is not honoured")
    vault_reg["scripts"] = []
    _write(root / TABLE_PATHS["vetted-scripts"], json.dumps(vault_reg))
    ok(vetted_status("fixture-housekeeper", home=home, root=root)["status"] == "vetted",
       "removing the vault row without a pin advance keeps the pinned registration")
    _write(root / TABLE_PATHS["vetted-scripts"], (AP_FIXTURES / "vetted-scripts.json").read_text(encoding="utf-8"))
    with vetted_context("fixture-housekeeper", str(emp), script, home=home, root=root, detection=claude, device="dev-a",
                        env=base_env, out=None, assume_unpinned=True) as ctx:
        r = ctx.run(["git", "fetch", "origin"], action="fetch")
    ok(r.returncode == 126 and ctx.status["status"] == "unpinned", "the vault-module fallback is always unpinned")
    with vetted_context("fixture-housekeeper", str(emp), script, home=home, root=root, detection=human, device="dev-a",
                        env=base_env, out=None, assume_unpinned=True) as ctx:
        r = ctx.run(["git", "fetch", "origin"], action="fetch")
    ok(r.returncode == 0, "a human run is not policy-gated even unpinned")

    # ---- today's v4 overlay: composed fails, the lifted env succeeds (synthetic owners)
    if v4 is not None:
        emp2, bare2, _e = _employer_pair(tmp, home, slug="acme-corp/gadget")
        comp = _g(v4, "push", "origin", "--delete", "feat/done", cwd=emp2)
        lifted_run = _g(lift_env(v4), "push", "origin", "--delete", "feat/done", cwd=emp2)
        gone = _g(genv, "--git-dir", str(bare2), "show-ref", "--verify", "--quiet", "refs/heads/feat/done").returncode != 0
        ok(comp.returncode != 0 and lifted_run.returncode == 0 and gone,
           "present-state regression: v4's transport block fails a composed push --delete; the lifted env succeeds")

    # ---- receipts are machine-local and never create control/
    try:
        append_receipt({"type": "receipt", "result": "ok"}, home=home_np)
        ok(False, "append_receipt without control/ raises")
    except ReceiptError:
        ok(not ws_paths(home=home_np)["base"].exists(), "append_receipt never creates control/")
    try:
        append_receipt({"type": "receipt", "repo_slug": "git@github.com:acme-corp/x"}, home=home)
        ok(False, "a URL-shaped receipt value is refused")
    except ValueError:
        ok(True, "")
    ok(lib.is_dir(), "pin fixture present")


ID_FIXTURES = TOOLS / "fixtures" / "identity"
SHELL_ANC = [{"comm": "zsh"}, {"comm": "Terminal"}, {"comm": "launchd"}]
_T8_FAMILIES = ("claude", "cursor", "human")
_T8_DEVICES = ("dev-a", "dev-b", "unknown")


def _t8_fixture_root(tmp: Path) -> Path:
    """A synthetic workspace root with the T8 identity tables plus T2's surfaces and T7's policy mirror."""
    root = tmp / "t8-home" / "Projects" / "ws"
    for name in ("devices", "context-remotes"):
        _write(root / TABLE_PATHS[name], (ID_FIXTURES / f"{name}.json").read_text(encoding="utf-8"))
    _write(root / TABLE_PATHS["surfaces"], (FIXTURES / "surfaces.json").read_text(encoding="utf-8"))
    for name in ("action-policy", "vetted-scripts"):
        _write(root / TABLE_PATHS[name], (AP_FIXTURES / f"{name}.json").read_text(encoding="utf-8"))
    _write(root / "AGENTS.md", "# fixture workspace\n")
    _fake_repo(root, {"origin": "https://github.com/pat-sample/ws.git"})
    return root


def _t8_git_env(home: Path) -> dict:
    return dict(_git_env(home), GIT_AUTHOR_DATE="2026-09-22T12:00:00Z", GIT_COMMITTER_DATE="2026-09-22T12:00:00Z")


def _t8_repo(where: Path, url: Optional[str], email: Optional[str], home: Path, name: str = "Fixture") -> Path:
    """A real (tiny) git repo with an optional origin URL and a repo-local identity."""
    env = _t8_git_env(home)
    where.mkdir(parents=True, exist_ok=True)
    _g(env, "init", "-q", "-b", "main", str(where))
    if url:
        _g(env, "remote", "add", "origin", url, cwd=where)
    if email:
        _g(env, "config", "user.email", email, cwd=where)
        _g(env, "config", "user.name", name, cwd=where)
    return where


def _t8_oracle(fam: str, dev: str, repo_cls: str, eff: str, ovr_for: Optional[str]) -> Tuple[Optional[str], List[str], bool]:
    """(expected, invariants_hit, flag raised) written out from the plan, independent of the table."""
    if fam == "claude":
        expected, rule, overridable = "pat", "IR1", False
    elif dev == "dev-a":
        expected, rule, overridable = "acme-id", "IR2", True
    elif dev == "dev-b":
        expected, rule, overridable = "pat", "IR3", False
    else:
        expected, rule, overridable = None, None, False
    hits: List[str] = []
    if repo_cls == "employer":
        expected = None if fam == "claude" else "acme-id"
        if eff != "acme-id":
            hits.append("I1")
        if fam == "claude":
            hits.append("I2")
    flag = rule is not None and eff != expected and "I1" not in hits
    if flag and overridable and repo_cls != "employer" and ovr_for == eff:
        flag = False
    return expected, hits, flag


def _t8_self_test(tmp: Path, ok: Callable[[Any, str], None]) -> None:
    root = _t8_fixture_root(tmp)
    home = tmp / "t8-home"
    human = detect_surface(env={}, ancestry=SHELL_ANC, isatty=HUMAN_TTY, root=root)
    genv = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home), "GIT_CONFIG_NOSYSTEM": "1"}
    dev_t = load_table("devices", root=root)
    acme_mail = _identities(dev_t)["acme-id"]["email"]
    pat_mail = _identities(dev_t)["pat"]["email"]

    # ---- tables: identity keys validate; negatives fail
    v = validate_tables(root=root, require_all=True)
    ok(v["tables"]["devices"]["ok"], f"identity fixture devices validate under --require-all: {v['tables']['devices']}")
    real = validate_tables(require_all=True)
    ok(real["tables"]["devices"]["ok"], f"shipped devices.json validates under --require-all: {real['tables']['devices']}")
    base = json.loads((ID_FIXTURES / "devices.json").read_text(encoding="utf-8"))
    for mutate, needle in (
            (lambda d: d["identities"][0].__setitem__("class", "contractor"), "identities[0].class"),
            (lambda d: d["employer_allowlist"].__setitem__("identity_ids", ["pat"]), "is not an employer identity"),
            (lambda d: d["identity_rules"][0].__setitem__("identity", "ghost"), "is not a declared identity"),
            (lambda d: d["identity_rules"][1].__setitem__("device", "dev-z"), "is not '*' or a declared device"),
            (lambda d: d["identity_rules"][0].__setitem__("override_suppresses", "non-employer-repos-only"),
             "non-overridable rule"),
            (lambda d: d.__setitem__("invariants", d["invariants"][:1]), "I1 and I2 must both be declared"),
            (lambda d: d["identities"][0]["push"].__setitem__("alias", "nowhere"), "is not a declared ssh alias"),
            (lambda d: d["personal_markers"].__setitem__("emails", [acme_mail]), "personal-marker email")):
        bad = json.loads(json.dumps(base))
        mutate(bad)
        errs = validate_table("devices", bad)
        ok(any(needle in x for x in errs), f"devices negative {needle!r}: {errs}")

    # ---- email classes (personal markers win; allowlist is identity or domain)
    ok(email_class(pat_mail, dev_t) == "personal" and email_class("x@pat-sample.example", dev_t) == "personal",
       "personal marker email and domain")
    ok(email_class(acme_mail, dev_t) == "employer" and email_class("y@acme-corp.example", dev_t) == "employer",
       "employer allowlist identity and domain")
    ok(email_class("fixture@example.invalid", dev_t) == "other" and email_class("", dev_t) is None, "other and none")
    ok(email_class("Y@ACME-Corp.Example", dev_t) == "employer", "an allowlisted domain matches casefolded")
    ok(all(email_class(f"y@{d}", dev_t) == "other"
           for d in ("acme-corp.example.evil.io", "notacme-corp.example", "mail.acme-corp.example")),
       "an allowlisted domain matches exactly: suffix and prefix lookalikes and subdomains are other")
    for key, val in (("emails", "y@acme-corp.example"), ("email_domains", "acme-corp.example")):
        both = json.loads(json.dumps(dev_t))
        both["personal_markers"][key].append(val)
        ok(email_class("y@acme-corp.example", both) == "personal",
           f"a personal marker ({key}) wins over the allowlisted domain")
    # D5 (2026-09-23): the shipped allowlist names the employer mail domain, matched the same way
    shipped, d5 = load_table("devices"), "centricsoftware.com"
    ok(d5 in (shipped.get("employer_allowlist") or {}).get("email_domains", []),
       "shipped employer_allowlist carries the D5 domain")
    ok([email_class(a, shipped) for a in (f"user@{d5}", f"USER@{d5.upper()}")] == ["employer"] * 2,
       "D5: the employer domain classifies employer in any case")
    ok([email_class(f"user@{d}", shipped) for d in (f"{d5}.evil.io", f"not{d5}", f"mail.{d5}")] == ["other"] * 3,
       "D5: lookalikes and subdomains of the employer domain classify other")
    ok(email_class(d5, shipped) == "other", "D5: a bare domain with no '@' is not an employer address")
    both = json.loads(json.dumps(shipped))
    both["personal_markers"]["emails"].append(f"user@{d5}")
    ok(email_class(f"user@{d5}", both) == "personal", "D5: a personal marker still wins over the domain")

    # ---- the family x device x repo x effective x override matrix
    elsewhere = tmp / "t8-elsewhere"
    repos = {}
    for cls, url in (("personal", "git@github.com:pat-sample/mine.git"), ("employer", "git@github.com:acme-corp/w.git"),
                     ("third-party", "https://github.com/oss-upstream/up.git")):
        for eff, mail in (("acme-id", acme_mail), ("pat", pat_mail)):
            repos[(cls, eff)] = _t8_repo(elsewhere / f"{cls}-{eff}", url, mail, home)
    (ws_paths(home=home)["control"]).mkdir(parents=True, exist_ok=True)
    made = override(task="fixture-task", repo="pat-sample/mine", identity="pat", ttl="8h", reason="fixture words",
                    home=home, root=root, env={}, ancestry=SHELL_ANC, isatty=HUMAN_TTY)
    ok(made["exit"] == 0 and made["override"]["created_by"] == "human", f"human override created: {made}")
    mism = 0
    for fam in _T8_FAMILIES:
        for dev in _T8_DEVICES:
            for (cls, eff), path in repos.items():
                r = identity(repo=str(path), family=fam, device=dev, root=root, env=genv, home=home, detection=human)
                exp, hits, flag = _t8_oracle(fam, dev, cls, eff, "pat" if cls == "personal" else None)
                good = (r["expected"] == exp and r["invariants_hit"] == hits and bool(r["flag"]) == flag
                        and r["repo_class"] == cls and r["effective"]["identity"] == eff)
                if not good:
                    mism += 1
                    ok(False, f"identity matrix {fam}/{dev}/{cls}/{eff}: got {r}")
    ok(mism == 0, "identity matrix matches the oracle (family x device x repo x effective x override)")
    r = identity(repo=str(repos[("employer", "acme-id")]), family="claude", device="dev-a", root=root, env=genv,
                 home=home, detection=human)
    ok(r["allowed"] == [] and "I2" in r["invariants_hit"], "Claude on an employer repo: no identity allowed, I2")
    # The I1 check reads the allowlisted domain: an author at exactly that domain is employer (no I1, but
    # still flagged as an undeclared identity); an author at a lookalike domain is other and hits I1.
    for label, mail, want_cls, want_hits in (("an allowlisted-domain", "y@acme-corp.example", "employer", []),
                                             ("a lookalike-domain", "y@acme-corp.example.evil.io", "other", ["I1"])):
        path = _t8_repo(elsewhere / f"employer-{label.split()[-1]}", "git@github.com:acme-corp/w.git", mail, home)
        r = identity(repo=str(path), family="cursor", device="dev-a", root=root, env=genv, home=home, detection=human)
        ok(r["effective"]["email_class"] == want_cls and r["invariants_hit"] == want_hits
           and r["effective"]["identity"] is None and bool(r["flag"]) == (not want_hits),
           f"identity() on an employer repo with {label} author: {want_cls}, hits {want_hits}: {r}")
    r = identity(repo=str(repos[("personal", "pat")]), family="cursor", device="dev-a", root=root, env=genv, home=home,
                 detection=human)
    ok(r["flag"] is None and r["override"] and r["override"]["identity"] == "pat",
       "an active override suppresses the dev-a mismatch flag on a personal repo")
    cached = _t8_repo(home / "Projects" / "sealed", "git@github.com:pat-sample/sealed.git", pat_mail, home)
    claude_det = detect_surface(env={}, ancestry=CLAUDE_ANC, isatty=NO_TTY, root=root)
    r = identity(repo=str(cached), root=root, env=genv, home=home, detection=claude_det, device="dev-b",
                 cache={"checkouts": []})
    ok(r["effective"]["email_class"] is None and r["notice"] and "cache" in r["notice"],
       "a Claude chain never reads an uncached checkout under projects_root for the effective identity")
    r = identity(family="cursor", device="unknown", root=root, env=genv, home=home, detection=human)
    ok(r["expected"] is None and r["rule"] is None, "unknown device: no default identity")

    # ---- the express override: refusals, expiry, never creates control/
    def ovr(**kw):
        args = dict(task="t", repo="pat-sample/mine", identity="pat", ttl="8h", reason="words", home=home, root=root,
                    env={}, ancestry=SHELL_ANC, isatty=HUMAN_TTY)
        args.update(kw)
        return override(**args)

    for label, kw in (("agent-possible env", {"env": {"CLAUDECODE": "1"}}), ("no TTY", {"isatty": NO_TTY}),
                      ("Claude family", {"ancestry": CLAUDE_ANC}),
                      ("WS_SURFACE_FAMILY=claude", {"env": {"WS_SURFACE_FAMILY": "claude"}}),
                      ("employer repo", {"repo": "acme-corp/w"}), ("employer repo (bitbucket owner)", {"repo": "Acme-BB/x"}),
                      ("undeclared owner", {"repo": "stranger/x"})):
        r = ovr(**kw)
        ok(r["exit"] == EXIT_REFUSED and r["refused"] and r["override"] is None, f"override refused: {label}: {r}")
    for label, kw in (("ttl above 24h", {"ttl": "25h"}), ("ttl zero", {"ttl": "0h"}), ("bad ttl", {"ttl": "1d"}),
                      ("undeclared identity", {"identity": "ghost"}), ("no reason", {"reason": " "})):
        try:
            ovr(**kw)
            ok(False, f"override usage error: {label}")
        except OverrideError:
            ok(True, "")
    r = ovr(ttl="24h", repo="oss-upstream/up")
    c, x = _parse_z(r["override"]["created"]), _parse_z(r["override"]["expires"])
    ok(r["exit"] == 0 and c and x and 0 < (x - c).total_seconds() <= OVERRIDE_MAX_TTL_S, "override expires within 24 h")
    later = _now(None).timestamp() + OVERRIDE_MAX_TTL_S + 60
    ok(not active_overrides(home=home, now=lambda: datetime.fromtimestamp(later, timezone.utc)),
       "every override has expired a day later")
    rows = load_overrides(home=home)
    rows.append({"id": "ovr-forged", "repo": "pat-sample/mine", "identity": "pat", "created": "2026-09-22T00:00:00Z",
                 "expires": "2026-09-30T00:00:00Z", "created_by": "human"})
    _write_overrides(home, rows)
    ok(all(o.get("id") != "ovr-forged" for o in active_overrides(home=home, now=lambda: datetime(
        2026, 9, 23, tzinfo=timezone.utc))), "a hand-written row longer than 24 h is void")
    r = ovr(revoke="ovr-forged", env={"CLAUDECODE": "1"})
    ok(r["exit"] == EXIT_REFUSED, "an agent cannot revoke either")
    ok(ovr(revoke="ovr-forged")["exit"] == 0 and ovr(revoke="ovr-forged")["exit"] == EXIT_NOTFOUND, "human revoke")
    ok(override(list_only=True, home=home, env={"CLAUDECODE": "1"}, isatty=NO_TTY)["exit"] == 0, "list is read-only")
    bare = tmp / "t8-bare-home"
    r = ovr(home=bare)
    ok(r["exit"] == EXIT_NOTFOUND and not (bare / ".config").exists(), "override never creates control/")

    # ---- the floor decision (in process; real temp repos; injected ancestry)
    fenv = dict(_t8_git_env(home))

    def floor(event: str, where: Path, args: Optional[list] = None, lines: Optional[list] = None,
              anc: Optional[list] = None, **kw) -> dict:
        return floor_decide(event, args or [], lines or [], env=fenv, ancestry=anc if anc is not None else CLAUDE_ANC,
                            root=root, home=home, cwd=where, **kw)

    pers = repos[("personal", "pat")]
    emp = _t8_repo(elsewhere / "emp-floor", "git@github.com:acme-corp/w.git", acme_mail, home)
    ok(floor("pre-commit", pers)["decision"] == "allow", "floor: personal repo outside projects_root commits")
    ok(floor("pre-commit", root)["decision"] == "allow", "floor: the workspace commits")
    for ev in ("pre-commit", "commit-msg", "pre-merge-commit"):
        d = floor(ev, emp, ["x"] if ev == "commit-msg" else [])
        ok(d["decision"] == "block" and d["rule"] == "I2", f"floor: employer {ev} blocks I2: {d}")
    _g(fenv, "commit", "-q", "--allow-empty", "-m", "base", cwd=emp)
    head = _g(fenv, "rev-parse", "HEAD", cwd=emp).stdout.strip()
    zero = "0" * 40
    d = floor("pre-push", emp, ["origin", "git@github.com:acme-corp/w.git"],
              [f"(delete) {zero} refs/heads/feat/done {head}"], anc=[{"comm": "git"}, {"comm": "zsh"}, {"comm": "claude"}])
    ok(d["decision"] == "block" and d["rule"] == "I2", f"floor: model-composed employer push --delete blocks I2: {d}")
    _g(fenv, "-c", f"user.email={pat_mail}", "commit", "-q", "--allow-empty", "-m", "personal", cwd=emp)
    top = _g(fenv, "rev-parse", "HEAD", cwd=emp).stdout.strip()
    d = floor("pre-push", emp, ["origin", "git@github.com:acme-corp/w.git"],
              [f"refs/heads/main {top} refs/heads/main {head}"])
    ok(d["decision"] == "block" and d["rule"] == "I1", f"floor: a personal commit in the pushed range blocks I1: {d}")
    d = floor("pre-push", emp, ["origin", "/somewhere/local.git"], [f"refs/heads/main {top} refs/heads/main {zero}"])
    ok(d["decision"] == "block" and d["rule"] == "I1", f"floor: I1 over a new branch (no remote sha): {d}")
    blocked = str(load_table("context-remotes", root=root)["blocked_scheme"])
    d = floor("pre-push", pers, ["origin", blocked + "w.git"], [f"(delete) {zero} refs/heads/x {head}"])
    ok(d["decision"] == "block", f"floor: a blocked-scheme URL is employer: {d}")
    uncached = _t8_repo(home / "Projects" / "looks-mine", "git@github.com:pat-sample/looks-mine.git", pat_mail, home)
    d = floor("pre-commit", uncached, cache={"checkouts": []})
    ok(d["decision"] == "block" and d["rule"] == "not-positively-personal" and "scan" in d["reason"],
       f"floor: an uncached personal-looking repo under projects_root blocks with the fix named: {d}")
    hit = {"checkouts": [{"path": str(uncached), "kind": "repo", "owner_class": "personal", "default_branch": None,
                          "remotes": [{"name": "origin", "form": "scp", "host": "github.com",
                                       "slug": "pat-sample/looks-mine"}]}]}
    ok(floor("pre-commit", uncached, cache=hit)["decision"] == "allow", "floor: a cached personal repo commits")
    loose = _t8_repo(home / "Projects" / "scratch", None, pat_mail, home)
    ok(floor("pre-commit", loose, cache={"checkouts": []})["rule"] == "not-positively-personal",
       "floor: no remote under projects_root blocks")
    ok(floor("pre-commit", _t8_repo(elsewhere / "loose", None, None, home))["decision"] == "allow",
       "floor: no remote outside projects_root commits")
    ok(floor("pre-commit", repos[("third-party", "pat")])["decision"] == "allow",
       "floor: a third-party checkout outside projects_root is not the floor's business")
    d = floor_decide("pre-commit", [], [], env=5, ancestry=CLAUDE_ANC, root=root, home=home, cwd=pers)  # type: ignore[arg-type]
    ok(d["decision"] == "allow" and "infrastructure error" in (d["notice"] or ""), "floor: infrastructure errors allow")
    ok(floor("post-checkout", emp)["decision"] == "allow", "floor: an unknown event allows")

    # ---- the vetted housekeeping shape
    script = _write(root / "09-tools" / "fixture-housekeeper.py", "# fixture housekeeper v1\n")
    _pin_fixture(home, root, "09-tools/fixture-housekeeper.py", git_blob_sha(script))
    _write(ws_paths(home=home)["root_file"], f"{root}\n")
    ctrl = ws_paths(home=home)["control"]

    def intent(pid: int, refs: List[str], script_id: str = "fixture-housekeeper") -> None:
        _append_jsonl(ctrl / "receipts.jsonl", {"type": "intent", "ts": _now_z(), "pid": pid, "ppid": 1,
                                               "script": script_id, "script_blob": git_blob_sha(script),
                                               "repo_slug": "acme-corp/w", "action_class": "housekeeping",
                                               "action": "remote-branch-delete", "refs": refs})

    vet = [{"pid": 900, "comm": "git", "args": "git push origin --delete feat/done"},
           {"pid": 4242, "comm": "Python", "args": f"/usr/bin/python3 -I {script} --apply"},
           {"pid": 10, "comm": "claude", "args": "claude"}]
    dl = [f"(delete) {zero} refs/heads/feat/done {head}"]
    intent(4242, ["refs/heads/feat/done"])
    d = floor("pre-push", emp, ["origin", "git@github.com:acme-corp/w.git"], dl, anc=vet)
    ok(d["decision"] == "allow" and "vetted" in (d["notice"] or ""), f"floor: the vetted shape is allowed: {d}")
    rel = [dict(vet[0]), dict(vet[1], args="python3 -I 09-tools/fixture-housekeeper.py"), vet[2]]
    d = floor("pre-push", emp, ["origin", "u"], dl, anc=rel)
    ok(d["rule"] == "I2" and "relative" in d["reason"], f"floor: a relative script path is never vetted: {d}")
    noi = [dict(vet[0]), dict(vet[1], args=f"/usr/bin/python3 {script} --apply"), vet[2]]
    d = floor("pre-push", emp, ["origin", "u"], dl, anc=noi)
    ok(d["rule"] == "I2" and "-I" in d["reason"], f"floor: a vetted script run without -I is not vetted: {d}")

    def ps_denied(_cols: str) -> str:
        raise PermissionError("operation not permitted")

    d = floor_decide("pre-push", ["origin", "u"], dl, env=fenv, ancestry=None, ps=ps_denied, root=root, home=home,
                     cwd=emp)
    ok(d["rule"] == "I2" and "ancestry unavailable" in d["reason"] and "sandbox" in d["reason"],
       f"floor: a denied ps names the cause instead of 'model-composed': {d}")
    d = floor("pre-push", emp, ["origin", "u"], [f"(delete) {zero} refs/heads/feat/other {head}"], anc=vet)
    ok(d["rule"] == "housekeeping-shape", f"floor: refs that differ from the intent line block: {d}")
    d = floor("pre-push", emp, ["origin", "u"], [f"(delete) {zero} refs/heads/main {head}"], anc=vet)
    ok(d["rule"] == "housekeeping-shape", f"floor: deleting the default branch blocks: {d}")
    d = floor("pre-push", emp, ["origin", "u"], [f"refs/heads/main {head} refs/heads/main {zero}"], anc=vet)
    ok(d["decision"] == "block", f"floor: a vetted non-delete push blocks: {d}")
    ok(floor("pre-push", emp, ["origin", "u"], dl, anc=[vet[0], dict(vet[1], pid=5555), vet[2]])["rule"]
       == "housekeeping-shape", "floor: an intent line from another pid does not count")
    intent(4343, ["refs/heads/feat/done"])
    fake = [vet[0], {"pid": 4343, "comm": "python3", "args": f"python3 {tmp}/elsewhere-copy.py"}, vet[2]]
    ok(floor("pre-push", emp, ["origin", "u"], dl, anc=fake)["rule"] == "I2",
       "floor: an unregistered python script is model-composed (I2)")
    _write(script, "# edited, not pinned\n")
    d = floor("pre-push", emp, ["origin", "u"], dl, anc=vet)
    ok(d["rule"] == "I2" and "differ" in d["reason"], f"floor: a hash mismatch is not vetted: {d}")
    _write(script, "# fixture housekeeper v1\n")
    ok(all(r in FLOOR_RULES for r in ("I1", "I2", "IR1", "housekeeping-shape", "not-positively-personal")),
       "floor rule ids")


def _t8_git_floor(ok: Callable[[Any, str], None]) -> None:
    """The hook-level floor fixtures (git >= 2.54 config hooks), from 09-tools/fixtures/identity.

    They need the vault checkout (render_shims, ws_hook, the dist wrapper), so a pinned copy of this
    module skips them with a notice; git below 2.54 skips them too. A skip is never a pass: the
    device measures run them through `test-validators.py --strict-skips`."""
    helper = ID_FIXTURES / "floor_cases.py"
    if not helper.is_file():
        print("self-test SKIP: hook-level floor fixtures absent (a pinned copy) — not a pass", file=sys.stderr)
        _SELFTEST_SKIPS.append("hook-level floor fixtures absent")
        return
    import importlib.util

    spec = importlib.util.spec_from_file_location("t8_floor_cases", helper)
    if spec is None or spec.loader is None:
        ok(False, "floor_cases.py loads")
        return
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for name, passed, detail in mod.run_all(sys.modules[__name__]):
        if passed is None:
            print(f"self-test SKIP: {name} ({detail}) — not a pass", file=sys.stderr)
            _SELFTEST_SKIPS.append(name)
            continue
        ok(passed, f"{name}: {detail}")


_SELFTEST_SKIPS: List[str] = []


def self_test(stub_chain: bool = False) -> int:
    """0 all passed; 1 a failure; 3 no failure but at least one case SKIPPED (never green, 3c)."""
    fails: List[str] = []
    passes = [0]
    del _SELFTEST_SKIPS[:]

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

        # hostnames: variants derived from the shipped table (no device literal outside devices.json)
        if (ROOT / TABLE_PATHS["devices"]).exists():
            shipped = load_table("devices")
            for row in shipped.get("devices") or []:
                h0 = (row.get("hostnames") or [None])[0]
                if not h0:
                    continue
                for h in (h0 + ".lan", h0.lower(), h0.upper() + ".local"):
                    ok(current_device(hostname=h)["id"] == row["id"], f"{h} resolves to {row['id']}")
                for hn, lab in (row.get("hostname_labels") or {}).items():
                    ok(device_label(hn + ".local") == lab, f"hostname label for {row['id']}")
        pr_root = tmp / "pr-root"
        for name in ("devices", "context-remotes", "surfaces"):
            src = root / TABLE_PATHS[name]
            if src.exists():
                dst = pr_root / TABLE_PATHS[name]
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        dt_ = json.loads((pr_root / TABLE_PATHS["devices"]).read_text(encoding="utf-8"))
        for row in dt_["devices"]:
            if row["id"] == "dev-b":
                row["projects_root"] = "Code"
        (pr_root / TABLE_PATHS["devices"]).write_text(json.dumps(dt_), encoding="utf-8")
        ok(projects_root(root=pr_root, home=home_a, hostname="host-b") == home_a / "Code"
           and projects_root(root=pr_root, home=home_a, hostname="host-a") == home_a / "Projects",
           "projects_root follows the injected hostname's device row (LLM/device F-05)")
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
        for u in ("ssh://git@ssh.github.com:443/acme-corp/x.git", "https://www.github.com/acme-corp/x"):
            n = normalize_remote(u, root=root)
            ok(n is not None and n["host"] == "github.com" and n["owner"] == "acme-corp",
               f"{u.split('://')[1].split('/')[0]} normalizes to github.com (walls F-03): {n}")
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
        ok("ancestry_unavailable" in det_err[0], "the detection object says whether ancestry was available")
        global _ps_default
        saved_ps = _ps_default

        def ps_denied(_cols: str) -> str:
            raise PermissionError("operation not permitted")
        _ps_default = ps_denied
        try:
            r = agent_check(env={}, ancestry=None, isatty=HUMAN_TTY, root=root)
            d = detect_surface(env={}, ancestry=None, isatty=HUMAN_TTY, root=root)
        finally:
            _ps_default = saved_ps
        ok(not r["human"] and not r["determined"] and d["ancestry_unavailable"],
           f"ps denied: agent_check is undetermined and detection says ancestry is unavailable: {r}")
        nm_root = tmp / "never-root"
        for name in ("surfaces", "devices", "context-remotes"):
            src = root / TABLE_PATHS[name]
            if src.exists():
                dst = nm_root / TABLE_PATHS[name]
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        st_ = json.loads((nm_root / TABLE_PATHS["surfaces"]).read_text(encoding="utf-8"))
        for row in st_["surfaces"]:
            if row["id"] == "claude-code":
                row["markers"]["env"] = [{"name": "CLAUDECODE", "verified": True}]
        (nm_root / TABLE_PATHS["surfaces"]).write_text(json.dumps(st_), encoding="utf-8")
        d = detect_surface(env={"CLAUDECODE": "1"}, ancestry=[], isatty=HUMAN_TTY, root=nm_root)
        ok(d["via"] != "env" and "CLAUDECODE" not in d["markers"],
           f"a never_markers name declared as an env marker attributes nothing: {d['via']} {d['markers']}")

        # AI_AGENT is set by several vendors: a value prefix attributes Claude Code (LLM/device F-01)
        d = detect_surface(env={"AI_AGENT": "claude-code_2-1-280_agent", "CLAUDECODE": "1"}, ancestry=[],
                           isatty=NO_TTY, root=root)
        ok(d["acting_host"] == "claude-code" and d["family"] == "claude" and d["family_for_walls"] == "claude",
           f"AI_AGENT=claude-code_* with no ancestry is Claude Code: {d['acting_host']} {d['family']}")
        d = detect_surface(env={"AI_AGENT": "some-other-agent"}, ancestry=[], isatty=NO_TTY, root=root)
        ok(d["family"] == "unknown-agent" and d["acting_host"] == "other-local-agents",
           f"a name-only marker matching several rows reports the family's generic row: {d['acting_host']}")
        # agent-possible env always raises the walls to claude (walls F-08); forged markers cannot lower them
        for extra in ({"CURSOR_AGENT": "1"}, {"CODEX_THREAD_ID": "t"}, {"WS_SURFACE_FAMILY": "cursor"}):
            d = detect_surface(env=dict(extra, CLAUDECODE="1"), ancestry=[], isatty=NO_TTY, root=root)
            ok(d["family_for_walls"] == "claude", f"CLAUDECODE plus {sorted(extra)} keeps claude walls: {d}")
        d = detect_surface(env={"CURSOR_AGENT": "1"}, ancestry=[], isatty=NO_TTY, root=root)
        ok(d["family_for_walls"] == "cursor", "a Cursor marker without agent-possible env stays cursor")
        # live table: Copilot's agent terminal sets AI_AGENT=github_copilot_vscode_* (probe copilot-vscode@personal-mbp).
        # It stays other-local-agents (restricted) on purpose: an env-only copilot label would lower the walls, and
        # L-01 keeps detection tighten-only until H15 decides discounts (wave 1). Changing this is a decision.
        if (ROOT / "02-shared-references" / "surfaces.json").is_file():
            d = detect_surface(env={"AI_AGENT": "github_copilot_vscode_agent"}, ancestry=[], isatty=NO_TTY, root=ROOT)
            ok(d["family_for_walls"] == "unknown-agent" and _restricted(d, ROOT),
               f"AI_AGENT=github_copilot_vscode_* alone stays restricted (L-01): {d}")
            # Sean 2026-09-24: CLAUDE_CODE_SSE_PORT alone (the Claude IDE extension's variable, present in every
            # Cursor / VS Code terminal) is no agent evidence; any real Claude marker beside it still is.
            ide = {"CLAUDE_CODE_SSE_PORT": "12345", "TERM_PROGRAM": "vscode"}
            ok(not _agent_possible_names(ide, _surfaces_or_fallback(ROOT)),
               "CLAUDE_CODE_SSE_PORT alone is not agent-possible (IDE terminal)")
            for extra in ({"CLAUDECODE": "1"}, {"CLAUDE_CODE_ENTRYPOINT": "cli"}):
                ok(bool(_agent_possible_names(dict(ide, **extra), _surfaces_or_fallback(ROOT))),
                   f"CLAUDE_CODE_SSE_PORT plus {sorted(extra)} stays agent-possible")
            d = detect_surface(env=dict(ide, WS_SURFACE_FAMILY="claude"), ancestry=[], isatty=NO_TTY, root=ROOT)
            ok(d["family_for_walls"] == "claude", f"the overlay beside the IDE variable keeps claude walls: {d}")

        # the surfaces table unreadable: the built-in marker list still refuses (test F-02, decision b)
        empty = tmp / "no-tables"
        empty.mkdir(exist_ok=True)
        for env_m in ({"CURSOR_AGENT": "1"}, {"CODEX_THREAD_ID": "t"}, {"GEMINI_CLI": "1"}, {"AI_AGENT": "x"},
                      {"COPILOT_MODEL": "m"}):
            r = agent_check(env=env_m, ancestry=shell, isatty=HUMAN_TTY, root=empty)
            ok(not r["human"], f"no surfaces.json: {sorted(env_m)} still refuses: {r}")
        r = agent_check(env={}, ancestry=[{"comm": "zsh"}, {"comm": "Cursor Helper (Plugin)"}, {"comm": "launchd"}],
                        isatty=HUMAN_TTY, root=empty)
        ok(not r["human"], f"no surfaces.json: a Cursor Helper ancestor still refuses: {r}")
        ok(automated_context(env={"CURSOR_AGENT": "1"}, ancestry=shell, isatty=HUMAN_TTY, root=empty),
           "no surfaces.json: automated_context still sees a Cursor marker")

        # positive human evidence (walls F-09): an orphan reaching launchd through no terminal is undetermined
        r = ac({}, [{"comm": "script", "pid": 500, "ppid": 1}, {"comm": "launchd", "pid": 1, "ppid": 0}], HUMAN_TTY)
        ok(not r["human"] and not r["determined"], f"an orphaned pty wrapper under launchd is undetermined: {r}")
        r = ac({}, [{"comm": "zsh"}, {"comm": "launchd", "pid": 1}], HUMAN_TTY)
        ok(not r["human"] and not r["determined"], f"a chain to launchd through no terminal is undetermined: {r}")
        for term in ("Terminal", "iTerm2", "sshd", "tmux", "login"):
            r = ac({}, [{"comm": "zsh"}, {"comm": term}, {"comm": "launchd", "pid": 1}], HUMAN_TTY)
            ok(r["human"] and r["determined"], f"a chain through {term} is human")

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

        # T7 (H22): action policy, verb map, lift_env, vetted context, receipts
        if AP_FIXTURES.is_dir():
            _t7_self_test(tmp, ok)
        else:
            fails.append(f"T7 fixtures missing at {AP_FIXTURES}")

        # T8 (H17): identity keys, the identity matrix, the express override, the Claude floor
        if ID_FIXTURES.is_dir() and AP_FIXTURES.is_dir():
            _t8_self_test(tmp, ok)
            _t8_git_floor(ok)
        else:
            fails.append(f"T8 fixtures missing at {ID_FIXTURES}")

        if stub_chain:
            # A real ancestor named `claude` that stays alive as the parent of the check.
            # macOS kills copies of Apple platform binaries (launch constraints: a copied
            # /bin/bash exits 137), and framework Python re-execs as `Python`, so on macOS the
            # stub is a tiny fork-and-wait binary compiled here (Linux CI too: it has gcc). A
            # non-macOS host without a compiler copies bash instead.
            stub = tmp / "stub" / "claude"
            stub.parent.mkdir()
            src = tmp / "stub" / "stub.c"
            src.write_text('#include <unistd.h>\n#include <sys/wait.h>\n'
                           'int main(int c,char**v){(void)c;pid_t p=fork();'
                           'if(p==0){execv("/bin/sh",v);_exit(127);}int s=0;'
                           'if(waitpid(p,&s,0)<0)return 1;return WIFEXITED(s)?WEXITSTATUS(s):1;}\n')
            cc = shutil.which("cc") or shutil.which("clang") or shutil.which("gcc")
            built = False
            stub_kind = "compiled"
            if cc:
                built = subprocess.run([cc, "-O0", "-o", str(stub), str(src)], capture_output=True,
                                       timeout=120).returncode == 0
            if not built and sys.platform != "darwin" and shutil.which("bash"):
                # Bytes + exec bit only: copy2 would also copy BSD flags (EPERM on SIP binaries).
                shutil.copyfile(shutil.which("bash"), stub)
                os.chmod(stub, 0o755)
                built, stub_kind = True, "bash-copy"
            runnable = built and subprocess.run([str(stub), "-c", "exit 0"], capture_output=True,
                                                timeout=30).returncode == 0
            if not runnable:
                print("self-test SKIP: stub chain needs a runnable non-platform binary named claude "
                      "(no C compiler, or the stub was killed) — not a pass", file=sys.stderr)
                _SELFTEST_SKIPS.append("stub chain")
                stub_chain = False
        if stub_chain:
            clean = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(home_a)}
            # The check's parent must be the process named claude. The compiled stub runs the
            # command through a forked /bin/sh, and Linux names that hop "sh" (comm is the
            # executable, not argv[0]), so `exec` hands the sh process to Python. A bash copy is
            # itself named claude, so `; exit $?` keeps bash from exec-ing Python in its place.
            lead, tail = ("exec ", "") if stub_kind == "compiled" else ("", "; exit $?")
            cmd = f'{lead}"{sys.executable}" "{me}" --root "{root}" detect --json{tail}'
            rr = subprocess.run([str(stub), "-c", cmd], capture_output=True, text=True, timeout=60, env=clean)
            try:
                j = json.loads(rr.stdout)
            except ValueError:
                j = {}
            ok(j.get("chain", [None])[0] == "claude", "stub ancestor named claude is the nearest hop")
            cmd = f'{lead}"{sys.executable}" "{me}" --root "{root}" agent-check --json{tail}'
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
    if _SELFTEST_SKIPS:
        print(f"OK profile_resolve self-test ({passes[0]} checks, {len(_SELFTEST_SKIPS)} SKIPPED: not green)")
        return 3
    print(f"OK profile_resolve self-test ({passes[0]} checks)")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
