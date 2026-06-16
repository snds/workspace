"""
_context.py — Project-level context file loading and merging.

Context files let users (or LLMs) bundle per-project defaults and config
overrides into a single portable YAML document. The toolkit itself stays
project-agnostic — the context file carries all project-specific knowledge
and is passed explicitly via --context.

Precedence (highest wins):
    CLI args  >  context.defaults  >  config file  >  script defaults
    context.check_overrides is deep-merged INTO the loaded config
    (context wins over config file for overlapping keys).

Context schema:
    project: <optional label, echoed in reports>
    defaults:
        input: <path>
        output: <path>
        config: <path to YAML config>
        reference: <path for visual_diff>
        folder_for: <path for icon_consistency / state_comparison>
        only: <comma-separated check names>
    check_overrides:
        <check_name>:
            <any config key>: <value>

Path resolution:
    - In `defaults`: tilde (~) expanded AND relative paths resolved against
      the context file's parent directory (so context files are portable).
    - In `check_overrides`: tilde (~) expanded only. Write absolute paths
      for anything else to keep behavior predictable.
"""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml


def _expand_tilde(value: Any) -> Any:
    """Expand ~ in string values; pass non-strings through."""
    if isinstance(value, str) and value.startswith("~"):
        return str(Path(value).expanduser())
    return value


def _expand_tildes_deep(obj: Any) -> Any:
    """Recursively expand ~ in all string values of a nested structure."""
    if isinstance(obj, dict):
        return {k: _expand_tildes_deep(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_tildes_deep(v) for v in obj]
    return _expand_tilde(obj)


def _resolve_defaults_paths(defaults: dict, base_dir: Path) -> dict:
    """
    In the `defaults` block, resolve string values for known path-typed keys.
    Tilde-expand, then resolve relative paths against the context file's
    directory so context files are portable.

    Non-path keys (currently just `only`) pass through unchanged. Adding a
    new CLI arg that takes a path means adding it to _PATH_KEYS.
    """
    out: dict[str, Any] = {}
    for k, v in defaults.items():
        if k in _PATH_KEYS and isinstance(v, str) and v:
            p = Path(v).expanduser()
            if not p.is_absolute():
                p = (base_dir / p).resolve()
            out[k] = str(p)
        else:
            out[k] = v
    return out


# CLI argument keys whose values are file/directory paths.
# `only` is the one defaults key that is NOT a path — it's a comma-separated
# list of check names.
_PATH_KEYS = {"input", "output", "config", "reference", "folder_for"}


def load_context(path: str | Path) -> dict:
    """
    Load a project context file. Returns a dict with:
        - project: str (optional label)
        - defaults: dict (CLI arg defaults, paths resolved)
        - check_overrides: dict (per-check config overrides, tildes expanded)
        - _context_path: str (absolute path to the context file, for logs)
    """
    path = Path(path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Context file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    if not isinstance(raw, dict):
        raise ValueError(f"Context file must be a mapping, got {type(raw)}")

    base_dir = path.parent
    defaults_raw = raw.get("defaults", {}) or {}
    overrides_raw = raw.get("check_overrides", {}) or {}

    if not isinstance(defaults_raw, dict):
        raise ValueError("Context `defaults` must be a mapping")
    if not isinstance(overrides_raw, dict):
        raise ValueError("Context `check_overrides` must be a mapping")

    return {
        "project": raw.get("project", ""),
        "defaults": _resolve_defaults_paths(defaults_raw, base_dir),
        "check_overrides": _expand_tildes_deep(overrides_raw),
        "_context_path": str(path),
    }


def apply_default(cli_value: Any, context_defaults: dict, key: str) -> Any:
    """CLI value wins if provided (not None); otherwise use context default."""
    if cli_value is not None:
        return cli_value
    return context_defaults.get(key)


def deep_merge(base: dict, override: dict) -> dict:
    """
    Deep-merge override into base. Override wins on conflicts.
    Both inputs are left unmodified; a new dict is returned.
    """
    result = copy.deepcopy(base)
    for k, v in override.items():
        if (
            k in result
            and isinstance(result[k], dict)
            and isinstance(v, dict)
        ):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = copy.deepcopy(v)
    return result
