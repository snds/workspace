---
tags: [knowledge-vault, engineering, agent-ops, orchestration]
created: 2026-09-04
updated: 2026-09-04
status: working
confidence: high
sources:
  - "https://intentapp.dev (product, fetched 2026-09-04)"
  - "https://www.augmentcode.com/blog/intent-a-workspace-for-agent-orchestration (Amelia Wattenberger)"
  - "https://www.augmentcode.com/tools/intent-vs-claude-code"
related_skills: [intent-coordination, open-agent-engine, mission-fit, harness-map, workspace-bootstrap]
related_projects: [19-workspace-brain]
relations:
  builds-on:
    - "[[agent-work-queue-boundaries]]"
    - "[[agentic-error-correction-foundations]]"
    - "[[nate-jones-harness-enrichments]]"
  exemplifies:
    - "[[17-intent-coordination-operating-model]]"
  relates-to:
    - "[[multi-session-workspace-resilience]]"
---

# Intent (intentapp.dev): what to adopt, what to refuse

## For future agent
- **TL;DR:** Adopt Intent's protocol as [[17-intent-coordination-operating-model]] + `intent-run.py`. The desktop app is optional GUI (`install-app`). Do not require Augment credits or Context Engine. Do not replace [[open-agent-engine]] or Live handoff.
- **Key claims:**
  - *Timeless:* coordination fails when each agent has its own prompt and partial context; a shared living spec is the alignment medium.
  - *Timeless:* isolation (worktrees) prevents file collisions; it does not prevent intent drift. Spec + independent verifier do that.
  - *Timeless:* human altitude is outcomes and approval, not babysitting every token.
  - *Dated (as of 2026-09):* GitHub `intent-hq/cloudlands-releases` ships Mac zip/dmg, Windows exe, Linux AppImage/deb, and `intentd`. Marketing still leads Mac. BYOA exists.
  - *Pointer:* [[intent-coordination]]; [[intent-spec]]; `python3 09-tools/intent-run.py`.
- **As of:** 2026-09 · **Status:** working (product reviewed from public pages; app not installed as a vault dependency)

## What the product actually is

Intent (Augment) is not an IDE replacement in the syntax-highlighting sense. It is a **task workspace** for running many coding agents: isolated git worktrees, a coordinator that drafts a spec, implementors in waves, a verifier against that spec, git/PR in the same shell. Demo surfaces (Agents, Context, Changes, Files, Browser, Shell) match the coordination problem this vault already hits with Cursor Task agents plus chat.

The bottleneck they name matches ours: tracking which agent, which spec version, which tree is ready to review. Their answer is **spec as shared memory**, not a longer thread.

## Adopt (portable)

1. **Living spec** as the only shared plan for multi-agent work.
2. **Approve before implement** on work that needed a spec.
3. **Dependency waves** (hold Mapbox-client until scaffold verifies, then fan endpoints).
4. **Worktree isolation** for parallel writers.
5. **Verifier vs spec**, with evidence the author did not generate alone.
6. **Fidelity checklists** as first-class spec content (the public demo's map console checklist is the right altitude for Sean's design-intent work).
7. **BYOA posture:** Claude Code / Cursor / Codex remain valid implementors. The vault stays vendor-agnostic ([[AGENTS]] portable-first).

## Refuse (or keep optional)

| Product pull | Why it loses here |
|---|---|
| Desktop app as the *only* standard | Protocol must be files + `intent-run.py` so Windows/Linux/headless still work. The app is optional GUI. GitHub releases (2026-09) also ship Windows/Linux installers despite the marketing homepage saying Mac-first. |
| Augment Context Engine as required MCP | Useful search, not the contract. Capability preflight if someone installs it. |
| Credits / Auggie default | Sean already has frontier agents; do not add a second paid path as doctrine. |
| Auto-commit / unattended full cycle | Breaks `centric-engineering` profile and Open Engine unattended-runner gate. |
| Hundreds of agents as a target | Fan-out only when the spec graph has independent nodes. |
| Second queue inside Intent | We already have lanes + receipts. Intent must not become a substance store. |
| Unrelated `intent-cli` GitHub projects | Not the Augment/intent-hq product. Do not install them as this protocol. |

## Mapping onto this vault (do not fork)

```
Sean intent  →  living spec (git)  →  implementors (worktrees + skills)
                    ↑                        ↓
              Live handoff              Open Engine (movement)
                    ↑                        ↓
              #06 / northstar          verifier (mission-fit + L3)
```

Same-model critique stays polish. Independent detectors stay the prove-gate.

## Honest limits of this review

Public site + Augment blog + comparison page. No local install, no SWE-bench numbers reproduced here, no claim about beta stability. If Sean later runs the app, record machine-local notes as a `memory/` fact, not as a new framework.
