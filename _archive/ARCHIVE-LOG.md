# Archive Log

Provenance ledger for everything retired into `_archive/`. **Nothing is deleted** — it is archived
with a reason and a pointer to the canonical replacement (if any). See
[[08-workspace-contribution-framework]] → Archive protocol for the procedure.

Every file under `_archive/` (except this log) must have a row here. CI
(`09-tools/validate-workspace.py`) fails otherwise.

| Archived file | Original path | Date | Reason | Superseded by |
|---|---|---|---|---|
| `_archive/Repo.md` | (scratch note, created in `_archive/`) | 2026-06-16 | Stray one-line note recording the legacy repo URL; folded into a proper memory entry. | [[fact-workspace-repos]] |
