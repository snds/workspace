"""wsxlib — the deterministic 'hands' of the Bootstrap Generator.

The CLI (`wsx`) owns all mechanical work: scaffolding, profile/manifest I/O,
emitting surface adapters, linting, verifying, and git sync. It contains NO
model/judgment — that lives in the canonical brain (../brain/*.md). The seam
between brain and hands is two files: context/profile.yaml and manifest.json.
"""

__version__ = "0.1.0"
