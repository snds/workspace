"""Single source of truth for the workspace directory taxonomy.

The generator's DEFAULT layout is the **numbered taxonomy** (`00-bootstrap` …
`09-tools`), mirroring a comprehensive personal-knowledge-management vault. Every
module locates a workspace dir through `Layout` rather than hardcoding `"context"` /
`"skills"` / … — so there is exactly one place the taxonomy is defined.

Back-compat is free: workspaces generated before this change use FLAT names
(`context/`, `skills/`, `frameworks/`, `projects/`, `knowledge/`). `Layout` prefers
the numbered dir but **falls back to the flat dir that's actually on disk**, so a
legacy workspace keeps working unchanged. The R2 `wsx restructure` migration
physically moves a flat workspace up to the numbered layout; until then both coexist.

    logical      canonical (numbered)    legacy (flat)   role
    ---------    --------------------    -------------   ---------------------------
    bootstrap    00-bootstrap            —               optional module (docs)
    frameworks   01-frameworks           frameworks      core
    shared       02-shared-references    —               core (epistemic + conventions)
    skills       03-skills               skills          core
    preferences  04-preferences          —               core (promoted from profile)
    artifacts    05-artifacts            —               optional module
    context      06-context              context         core
    projects     07-projects             projects        core
    knowledge    08-knowledge            knowledge        core
    tools        09-tools                —               core (automation) / optional (extra validators)
    adapters     adapters                adapters        generated (never numbered)

`adapters/` (and root `AGENTS.md` / `CLAUDE.md` / `HOME.md`, `.claude/`, `.cursor/`,
`.wsx/`) stay un-numbered — they are generated tooling, not vault content, exactly as
in a hand-built comprehensive workspace.
"""
from __future__ import annotations

from pathlib import Path

# logical name -> canonical (numbered) directory. THE source of truth.
CANONICAL: dict[str, str] = {
    "bootstrap": "00-bootstrap",
    "frameworks": "01-frameworks",
    "shared": "02-shared-references",
    "skills": "03-skills",
    "preferences": "04-preferences",
    "artifacts": "05-artifacts",
    "context": "06-context",
    "projects": "07-projects",
    "knowledge": "08-knowledge",
    "tools": "09-tools",
    "adapters": "adapters",
}

# logical name -> the pre-taxonomy FLAT directory a legacy workspace used. Only the
# dirs that existed before the numbered taxonomy appear here; the new core/optional
# dirs (bootstrap, shared, preferences, artifacts, tools) never had a flat form.
LEGACY: dict[str, str] = {
    "frameworks": "frameworks",
    "skills": "skills",
    "context": "context",
    "projects": "projects",
    "knowledge": "knowledge",
    "adapters": "adapters",
}

# The dir a wsx workspace MUST have for us to recognize it as one (numbered or flat).
_MARKER_KEYS = ("context",)


class Layout:
    """Resolves each logical dir to the name actually in use for a given workspace.

    Numbered-first, flat-fallback, else default to canonical (so a fresh, empty dir
    resolves to the numbered layout — that's what `wsx init` creates)."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self._resolved: dict[str, str] = {}
        for key, num in CANONICAL.items():
            if (self.root / num).is_dir():
                self._resolved[key] = num
            elif key in LEGACY and (self.root / LEGACY[key]).is_dir():
                self._resolved[key] = LEGACY[key]
            else:
                self._resolved[key] = num  # nothing on disk yet -> create numbered

    def name(self, key: str) -> str:
        """The directory NAME in use for this logical key (e.g. '06-context')."""
        return self._resolved[key]

    def dir(self, key: str) -> Path:
        """The resolved directory PATH for this logical key."""
        return self.root / self._resolved[key]

    def names(self) -> dict:
        """logical -> resolved name, for use as a render context (`{{dir.context}}`)."""
        return dict(self._resolved)

    @property
    def numbered(self) -> bool:
        """True if this workspace uses the numbered taxonomy (vs the legacy flat one)."""
        return self._resolved.get("context") == CANONICAL["context"]

    # convenience accessors for the hot dirs (keep call sites readable)
    @property
    def context(self) -> str: return self._resolved["context"]
    @property
    def skills(self) -> str: return self._resolved["skills"]
    @property
    def frameworks(self) -> str: return self._resolved["frameworks"]
    @property
    def projects(self) -> str: return self._resolved["projects"]
    @property
    def knowledge(self) -> str: return self._resolved["knowledge"]
    @property
    def shared(self) -> str: return self._resolved["shared"]
    @property
    def preferences(self) -> str: return self._resolved["preferences"]
    @property
    def tools(self) -> str: return self._resolved["tools"]
    @property
    def adapters(self) -> str: return self._resolved["adapters"]


def of(root: Path) -> Layout:
    return Layout(root)


def remap(layout: Layout, rel: str) -> str:
    """Translate a canonical (numbered) relpath to the dir actually in use on disk.

    Template keys are written in canonical form (`06-context/foo.md`). On a fresh
    workspace `remap` is the identity; on a legacy flat workspace it rewrites the
    leading segment (`06-context/foo.md` -> `context/foo.md`) so `wsx upgrade` adds
    the file to the dir that already exists rather than a numbered sibling."""
    parts = rel.split("/", 1)
    if len(parts) != 2:
        return rel
    head, tail = parts
    for key, canon in CANONICAL.items():
        if head == canon:
            return f"{layout.name(key)}/{tail}"
    return rel


def has_workspace_dirs(root: Path) -> bool:
    """True if `root` has the marker dir of a wsx workspace (numbered OR flat)."""
    lay = Layout(root)
    return all((root / lay.name(k)).is_dir() for k in _MARKER_KEYS)
