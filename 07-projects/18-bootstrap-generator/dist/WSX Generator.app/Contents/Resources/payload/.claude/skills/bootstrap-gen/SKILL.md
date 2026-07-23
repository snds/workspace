---
name: bootstrap-gen
description: >-
  Interview a person and generate their personalized "second brain" — an Obsidian
  vault that is also a git repo and a hub/spoke AI skill network, wired into their
  AI assistant (Claude Code, Cursor, Codex/Copilot, Gemini, or a tool-less context
  pack). Use this whenever someone wants to set up, bootstrap, or build a personal
  AI workspace / second brain from scratch, run the guided interview, or drive the
  `wsx` generator. Trigger on "set up my workspace", "bootstrap my workspace", "set
  up my second brain", "build my second brain", "generate my AI workspace", "build
  my skill network", "interview me", or "run the bootstrap generator".
triggers:
  - set up my workspace
  - bootstrap my workspace
  - set up my second brain
  - build my second brain
  - generate my AI workspace
  - build my skill network
  - interview me
  - run the bootstrap generator
---

# bootstrap-gen — auto-load entry

This is the **registered entry point** for the Bootstrap Generator. It exists so a
plain request like *"set up my workspace"* auto-triggers the generator without the
person having to point you at a file by hand.

**Do this now:** read the canonical brain and follow it exactly, start to finish.

- The brain lives at **`brain/SKILL.md`** at the root of this generator repo
  (relative to this file: `../../../brain/SKILL.md`).
- It is the Claude Code adapter of an AI-agnostic brain. As you reach each phase it
  tells you to read its sibling docs — `brain/interview.md`, `brain/synthesis.md`,
  `brain/resolver.md` — in the same `brain/` folder. Read them when it says to.

**Hold these two rules the whole way through** (the brain restates them in full):

1. **You are judgment and narration only — never touch the filesystem directly.**
   Every mechanical action (scaffold, profile, skills, emit, lint, verify, commit)
   is a call to the deterministic `wsx` CLI: `python3 <generator>/bin/wsx <command>`.
   If you catch yourself about to write a structural file inline, stop and call
   `wsx` instead. (You *do* author plain-prose context notes directly.)
2. **Interview suggestively, gate before building.** Open-ended questions with short
   "for example…" menus; play back what you heard and get an explicit yes at the
   synthesize-and-confirm gate and the skill-plan review gate before anything is
   written or pulled.

In this repo the CLI is `generator/bin/wsx`, so `<generator>` = `generator` (run it
as `python3 generator/bin/wsx <command>` from the repo root). Lost, or not sure the
environment is ready? Run `python3 generator/bin/wsx doctor` — it reports where you
are and what to run next. Then open `brain/SKILL.md` and begin at Phase 0.
