# ~/Projects — machine-local pointer (rendered; do not hand-edit)
Repos live here; the contract is ./workspace/AGENTS.md.
Before working in a repo, run `ws resolve repo <path>`; its profile sets the rules.
- Claude surfaces are personal-only: no substantive employer work (reading, mapping, editing, commits, PRs in employer repos); vetted, receipted housekeeping (merged-branch prune) is allowed.
- Codex: employer work only via a feature branch + PR for human review; never merge or push to the default branch.
- Cursor: employer work only via a feature branch + PR for human review; never merge or push to the default branch.
- Figma work uses real library components, never hand-built shapes.
- Durable context/learnings/decisions are written to the workspace, never to local agent memory.
- Employer repos never receive personal-workspace content, and workspace content is never pasted into employer surfaces.
- Neutral: `ws status` · `ws resolve repo <path>` · work request: `ws route --stdin <<'EOF'`…`EOF`, load its output.
