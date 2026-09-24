<!-- WORKSPACE-BEACON v3 · codex · generated, do not edit -->
WORKSPACE = the single source of truth for my rules, skills, knowledge, and session state.
- Local root: ~/Projects/workspace · Remote: github.com/snds/workspace (use GitHub when there is no local disk).
LOAD PROTOCOL for interactive work sessions — before any task, tool, or task-skill:
1. Read AGENTS.md at the workspace root and follow its read order.
2. Open your first reply with exactly ONE ritual line:
   [workspace: LOADED · <branch>@<sha> · <date> · via:<layer>]  — you read live workspace content
   [workspace: RULES-ONLY · via:<surface>]  — this surface cannot fetch files; the rules below still govern
   [workspace: UNREACHABLE · <reason>]  — you should have been able to read it but could not
EXEMPTION: when the caller demands raw structured output (headless -p, subagent data, API script), skip the ritual line and apply the rules silently.
STANDING RULES (in force even before loading):
- Figma work uses real library components, never hand-built shapes.
- Durable context/learnings/decisions are written to the workspace, never to local agent memory.
- Employer repos never receive personal-workspace content, and workspace content is never pasted into employer surfaces.
- Codex: employer work only via a feature branch + PR for human review; never merge or push to the default branch.
- Neutral commands: `ws status` (session card) · `ws resolve repo <path>` (personal or employer).
<!-- /WORKSPACE-BEACON -->
