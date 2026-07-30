SessionID: 2026-07-30-csk746-cursor-multiagent

--- SESSION BLOCK ---
Date: 2026-07-30
Agent: Composer
Surface: Cursor
Machine: Work MacBook Pro (CS-K746DRWXY1)
Project(s): 19-workspace-brain (Cursor multi-agent / multi-model hardening)
Artifacts:
  - 02-shared-references/trigger-routes.json + generated trigger-routes.md
  - 09-tools/build-trigger-routes.py
  - .cursor/hooks.json + hooks (reassert / sessionend / subagent-stop)
  - .cursor/agents/{workspace-bootstrap,ds-advisor,design-engineer,lead-ui-designer,lead-ux-designer}.md
  - 00-bootstrap/templates/cursor-mcp.json.example
  - _archive/compile-cursor-rules.py (retired landmine)
Decisions:
  - AGENTS.md remains hand-authored; compile-cursor-rules.py archived (would overwrite with Claude-only-writes policy).
  - Curated trigger routes live in trigger-routes.json; dispatcher loads JSON; markdown is generated for non-Claude agents.
  - Cursor project hooks cover preCompact / sessionEnd / subagentStop; user-global hooks still own sessionStart (+ doctor mirrors).
Pending resolved:
  - ^pc-04 trigger-routes reference
  - ^pc-13 Cursor User Rules BEACON (Perplexity still open)
Pending added: none
Project status changes:
  - Machine-layer fact: Work MBP → partial (Cursor hooks + BEACON); full doctor still open (^pc-03)
Next:
  - Run full workspace-doctor.sh on this machine when convenient; configure ~/.cursor/mcp.json from the example if Linear/Figma needed in Cursor
  - Prefer opening 00-bootstrap/workspaces/*.code-workspace (Brain first) for future Cursor sessions
--- END BLOCK ---
