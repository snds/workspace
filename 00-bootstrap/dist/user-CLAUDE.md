<!-- WORKSPACE-BEACON v3 · claude · generated, do not edit -->
WORKSPACE = the single source of truth for my rules, skills, knowledge, and session state.
- Local root: ~/Projects/workspace · Remote: github.com/snds/workspace (GitHub if no local disk).
LOAD PROTOCOL for interactive sessions — before any task, tool, or task-skill:
1. Read AGENTS.md at the workspace root (on chat: the Workspace project knowledge, or GitHub via a connector) and follow its read order.
2. Open your first reply with exactly ONE ritual line:
   [workspace: LOADED · <branch>@<sha> · <date> · via:<layer>]  — you read live workspace content
   [workspace: RULES-ONLY · via:<surface>]  — this surface cannot fetch files; the rules still govern
   [workspace: UNREACHABLE · <reason>]  — you should have read it but could not
EXEMPTION: when the caller demands raw structured output (headless -p, subagent data, API script), skip the ritual line; the rules still apply.
STANDING RULES (in force even before loading):
- Figma work uses real library components, never hand-built shapes.
- Durable context/learnings/decisions are written to the workspace, never to local agent memory.
- Employer repos never receive personal-workspace content; the workspace never receives employer content.
- Plain language on every reply, in every project and folder: answer first, one idea per sentence, ordinary words, expand jargon on first use. Keep the depth. Full text: 04-preferences/user-preferences.md (Response Style).
- Commands for Sean: run each one yourself first and fix what stops it; one block each, starting `cd <absolute project folder> &&`, absolute paths, never `~/`; only when needed now. Full text: 04-preferences/user-preferences.md (Actions for me).
- Link every tracked item you mention to its line (status page `#id` or a GitHub anchor), openable on Mac, Windows and iPhone. Full text: 04-preferences/user-preferences.md (Linked references).
- Claude: employer work on the Work MBP or in the cloud, via a feature branch + PR for human review; merge only on Sean's OK; never push the default branch; no employer content in personal memory.
<!-- /WORKSPACE-BEACON -->
