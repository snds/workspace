---
tags: [claude-code, hooks, infrastructure]
created: 2026-07-08
updated: 2026-07-08
status: stable
confidence: high
sources: [session-log 2026-07-08, dispatcher rebuild + Claude Code docs verification]
related_skills: [workspace-bootstrap]
related_projects: [Claude Workspace Infrastructure]
---

# Claude Code hooks — payload contract gotchas

Hard-won rules from the 2026-07-08 dispatcher rebuild (each verified against the live
harness and the hooks docs). The workspace's entire context-injection layer was dark for
an unknown period because of #1 — no error is ever surfaced.

1. **`hookSpecificOutput.hookEventName` MUST equal the event name** (`"SessionStart"`,
   `"UserPromptSubmit"`, `"PreToolUse"`). A `null`/missing value fails harness-side
   validation and the ENTIRE payload — including `additionalContext` — is **silently
   dropped**. No stderr, no transcript notice. If injected context stops arriving,
   check this first.
2. **SessionStart / UserPromptSubmit**: plain stdout on exit 0 is also injected as
   context (the no-JSON fallback). JSON with a correct `hookEventName` is the explicit,
   preferred form.
3. **PreToolUse**: deny via
   `{"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": "…"}}`.
   The reason is fed back to the MODEL, which makes deny a deterministic injection
   point: deny-once-with-instructions, let the retry pass (the workspace's `use_figma`
   design-judgment gate uses exactly this). Plain stdout injects nothing for PreToolUse.
   Exit code 2 = block + stderr fed to the model. stdin payload: `tool_name`,
   `tool_input`, `session_id`, `cwd`.
4. **SessionStart carries a `source`** — `startup` / `resume` / `clear` / `compact`
   (also usable as a hook matcher). `compact`/`resume` is the moment to re-inject
   context that compaction just destroyed; the dispatcher emits a compact
   re-orientation block there instead of the full boot payload.
5. **Matchers are regex** and match MCP tool names (e.g. `mcp__.*use_figma.*`).

Consumer: `.claude/hooks/dispatcher.py` (uses all five). Related: [[workspace-infrastructure]],
[[knowledge-vault-design]] (trigger-routing tiers), audit-log 2026-07-08.
