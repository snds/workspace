---
type: decision
description: Cloud and remote sessions may do both personal and employer work (2026-10-23) — each repo's owner decides its rules, a mixed session is allowed, the workspace is readable in employer sessions, and either Claude account may run Centric work when it is marked.
created: 2026-10-23
confidence: high
relations:
  builds-on: ["[[decision-claude-employer-surface]]", "[[feedback-credential-scoping]]"]
  relates-to: ["[[decision-llm-inclusive-harness]]"]
---

## For future agent
- **TL;DR:** a cloud session (Claude Code on the web, Cursor cloud agents, Codex cloud) does both kinds of work. Each repo attached to it is ruled by its owner. A Centric repo gets the Work MBP's conduct: feature branch, PR, human review, no merge, no push to the default branch. An `snds` repo stays personal. Personal and Centric repos may share one session. Employer work may read the workspace but never writes employer content into it.
- **As of:** 2026-10-23 · **Status:** current

## Context — what forced a choice

Sean works through Remote Control and cloud sessions in Claude, Cursor and Codex. Those sessions mix employer and personal work. The rules allowed employer work only on the Work MBP. A cloud container has no declared hostname, so it resolved to "unknown device", where every employer action is denied. In practice, a cloud session couldn't do Centric work at all.

A Remote Control session runs on a real machine and is driven from another device. It already follows that machine's rules, so it needed no change: one driven from the Work MBP can do Centric work, and one driven from the Personal MBP can't.

## Decision — what Sean chose (2026-10-23, four questions)

1. **The repos decide.** In a cloud session, each attached repo's owner decides its rules and identity. This is the rule the workspace already uses locally. The session is recognised by a marker the platform sets (`CLAUDE_CODE_REMOTE=true`), or by `WS_CLOUD_SESSION=1` set in the vendor's environment settings for Cursor and Codex. A declared machine's hostname always wins, so a marker can't turn the Personal MBP into a cloud session.
2. **A mixed session is allowed.** Personal and Centric repos may be attached to one session. Each repo keeps its own rules.
3. **The workspace is readable in employer sessions.** Skills, frameworks and context may load while doing Centric work. Nothing employer goes back into the workspace: H25's employer-substance check still guards it.
4. **Either account, when the work is marked.** Sean's personal Claude, Cursor or Codex account may run Centric work in the cloud, as it already may locally, when the work is clearly Centric and stays in Centric repos. The Centric-issued account works too.

## What changed in the harness

- `devices.json`:
  - A `cloud` block names the markers.
  - IR5 makes the personal identity `snds` for personal repos in the cloud.
  - IR6 makes the identity Centric for employer repos in the cloud.
  - I1 still holds: a personal identity never commits to an employer repo.
- `profile_resolve.py`: `current_device()` returns `cloud` when no declared hostname matches and a marker is set. The table validator checks the block. The independent oracle and the test matrix cover the cloud device.
- `action-policy.json`: P37–P39 give an employer repo in a cloud session the Work MBP's conduct, for Claude, Cursor and Codex:
  - P37 denies merges;
  - P38 denies authoring or pushing on the default branch, or on no known branch;
  - P39 allows the rest.
  - An undeclared owner stays denied, as before.
- `wall_guard.py`: a cloud session counts as the work device for R1. In the cloud, employer vault folders, employer MCP channels and employer browser hosts are no longer refused.
- The walls' wording changed in `beacons.json` and every rendered rules file, and in [CRITICAL_FACTS](../CRITICAL_FACTS.md).

## The walls that stay

- **Content.** No personal-workspace content is written into a Centric repo, and no Centric content is written into the workspace, personal memory, claude.ai Projects or artifacts.
- **Conduct.** `centric-engineering` binds every agent in a Centric repo, wherever it runs.
- **Identity and credentials.** I1 stays, and so does one credential per repo. The cloud platform's GitHub connection decides which account pushes. A Centric repo needs a GitHub connection that reaches Centric's org.

## Consequences and open risks

- **Machines need a fresh pin.** The policy and guard check their pinned copies. Each machine needs Sean's `--install-pin` before P37–P39 take effect there. A cloud session reads the checkout it cloned, so the rules apply as soon as this merges.
- **No local overlay in the cloud.** There, the floor is the policy rules, the wall guard (where the surface runs hooks: Claude Code does; Codex cloud doesn't), and GitHub's branch protection on Centric repos.
- **Vendor terms (Sean's call, recorded rather than decided).** Centric work under a personal account falls under consumer terms, as the 2026-10-06 decision already noted. With the workspace readable in employer sessions, personal context also enters sessions that may run under the Centric account. This widens what each vendor account sees. The content wall decides where things are written. It doesn't decide what a session reads.
- **Personal content in Centric repos is guarded by rule only.** The wall guard and H25 check the workspace for employer substance. Nothing mechanically scans a Centric commit for personal content. In a mixed session that is the rule most likely to slip.
- **Remote Control** follows the machine it drives, unchanged.
