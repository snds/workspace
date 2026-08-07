---
name: process-plugins
description: >-
  Doctrine precedence wrapper for the installed process-and-craft plugins (pstack: how, why,
  unslop, typescript-best-practices; superpowers: test-driven-development,
  verification-before-completion, writing-plans, executing-plans, systematic-debugging,
  brainstorming, requesting/receiving-code-review, subagent-driven-development,
  using-git-worktrees, finishing-a-development-branch, dispatching-parallel-agents,
  writing-skills). Load when one of those plugin workflows is invoked or implied, so the
  workspace gates stay authoritative. Trigger on "TDD", "write the test first", "red green
  refactor", "verify before completion", "am I done", "unslop this", "write a plan",
  "execute the plan", "debug this systematically", "brainstorm this", "worktree", "finish
  this branch", "write a skill for this". This skill holds no technique depth: it states which
  workspace framework wins on conflict (#06 QA, #11 anticipatory failure, #13 domain rigor,
  plus #07 integration and #08 contribution) and what each plugin may not relax.
aliases: [process-plugins, plugin-precedence]
triggers: [tdd, test driven development, write the test first, red green refactor, verification before completion, am i done, unslop, pstack, superpowers, writing plans, executing plans, systematic debugging, brainstorming, git worktree, finishing a branch, writing skills, subagent driven development]
tier: cross-cutting
domain: engineering
related: [eng, eng-foundations, arch-guild, github-guardrails, skill-placement]
defers_to: [framework-06, framework-07, framework-08, framework-11, framework-13]
rigor_role: multi-voice
spec_version: "2.2"
---

# Process Plugins — precedence wrapper

The installed **pstack** and **superpowers** plugins carry genuinely useful process technique:
test-first discipline, a completion-verification ritual, plan authoring and execution, systematic
debugging, prose cleanup, worktree and branch hygiene. They are also generic. They were written
for any repo, any reader, any quality bar, and they encode their own definitions of "done",
"verified", and "good writing".

This workspace has stricter, more specific definitions. **This skill is not a fork of those
plugins and holds no technique depth.** It exists so that when a plugin workflow fires, the agent
knows which document wins, and what the plugin is not allowed to relax.

Precedence, per `AGENTS.md` → "Doctrine precedence": workspace frameworks, then workspace skills,
then installed plugin skills. Use the plugin for the *how*; use the framework for the *bar*.

## Conflict map

| Plugin workflow | Where it conflicts | What wins |
|---|---|---|
| `verification-before-completion` | Its checklist ends at "the tests pass and the task is addressed" | [#06 QA Operating Model](../../01-frameworks/06-qa-operating-model.md) pre-output gate: target-user lens, full coverage (no curated subsets), reference check, accessibility check, honesty check. On anything visual, [#10 Perception Integrity](../../01-frameworks/10-perception-integrity.md) requires a native-resolution claim with the pixel dimensions stated |
| `test-driven-development` | Treats the red-green-refactor loop as the universal definition of sufficient testing | [#14 Engineering Operating Model](../../01-frameworks/14-engineering-operating-model.md) and [[eng]]'s done-gates: contract tests at every crossed boundary, failure paths exercised, trust boundaries non-negotiable. TDD is a welcome *method* for reaching that bar, never a substitute for it, and "no test was needed" is not a TDD conclusion the workspace accepts on a boundary change |
| `unslop` | Applies a generic anti-slop prose standard | The workspace's own voice and craft standard: [#05 Last-Mile Craft](../../01-frameworks/05-last-mile-craft-framework.md), `04-preferences/user-preferences.md`, and the established structure of the file being edited. Never let a cleanup pass strip intent, cross-links, or frontmatter (write-quality gate 2: no intent loss) |
| `writing-plans` / `executing-plans` | Its plan shape and its notion of scope completeness | [#11 Anticipatory Failure Analysis](../../01-frameworks/11-anticipatory-failure-analysis.md): a plan for work with a visible failure surface must include the pre-mortem (named technique, ledger consult, argue against the plan, acceptance criteria derived from references) before the build steps |
| `systematic-debugging` | Stops at "root cause found and fixed" | [#11](../../01-frameworks/11-anticipatory-failure-analysis.md) plus [#06](../../01-frameworks/06-qa-operating-model.md): the bug becomes a Visual Failure-Mode Ledger row or a knowledge entry when it is a class of failure, and the fix is proven at the gate, not asserted |
| `brainstorming` | Generates options without naming confidence | [#04 Research and Evidence](../../01-frameworks/04-research-and-evidence-framework.md): name the evidence tier; [#03](../../01-frameworks/03-collaboration-and-critique-framework.md) for the sparring-vs-executor mode call |
| `requesting-code-review` / `receiving-code-review` | Generic PR etiquette and diff shape | [#07 Integration & Review](../../01-frameworks/07-integration-and-review-framework.md): seven gates, one change per reason, bounded diffs, dependency-ordered stacking, author owns the drift. Multi-voice engineering pressure routes to [[arch-guild]] |
| `using-git-worktrees` / `finishing-a-development-branch` | Assumes it may commit, merge, and clean up | The context profile resolves first (`02-shared-references/delivery-playbooks/00-context-profiles.md`). Employer repos are branch and PR only: no auto-commit, no self-merge, no direct push. Unresolved profile means the most restrictive one. Also see [[github-guardrails]] |
| `subagent-driven-development` / `dispatching-parallel-agents` | Parallel agents with private context | `AGENTS.md` → "Multi-agent continuity & handoff": shared state in files, the Live handoff block is the baton, every entry stamps agent, surface, and machine. No private durable context |
| `writing-skills` | Its own template and completeness bar for authoring a skill | [#13 Domain Rigor Stack](../../01-frameworks/13-domain-rigor-stack.md) authoring algorithm and acceptance checklist (L1–L5), [#08 Workspace Contribution](../../01-frameworks/08-workspace-contribution-framework.md) placement rules, `02-shared-references/skill-frontmatter.md` for frontmatter, and [[skill-placement]] for where it goes. A native "create a skill" flow that skips the checklist is insufficient |
| `typescript-best-practices` / `how` / `why` | Language and repo conventions | The target repo's own conventions first, then [[eng-foundations]]. A plugin's preferred idiom does not override the codebase it is being applied to |

## Operating rule

1. **Let the plugin run its method.** The technique is why it is installed.
2. **Check the gate against the workspace, not the plugin.** Before claiming done, verified,
   clean, or reviewed, read the framework in the row above and satisfy *that* clause.
3. **Say what you set aside.** If a plugin instruction was not followed, name it and name the
   framework that outranked it. Silent divergence is how the two layers drift.
4. **Never write plugin doctrine into the vault.** If a plugin idea is good enough to keep,
   route it to the right workspace layer per [#08](../../01-frameworks/08-workspace-contribution-framework.md)
   instead of vendoring the plugin's text.

## When NOT to load this

This is a precedence note, not a workflow. Skip it when no plugin process skill is in play, when
the request is a direct engineering operation (use [[eng]]), or when the question is about a
specific framework's content (read the framework). Loading it does not require loading any
plugin, and loading a plugin does not require its permission: it only fixes the outcome when the
two disagree.

## Pairing

- Engineering operations → [[eng]] · [[eng-foundations]]
- Multi-voice review → [[arch-guild]]
- Repo safety and PR mechanics → [[github-guardrails]]
- Skill placement → [[skill-placement]]
