---
type: decision
description: Plain language is a standing rule injected on every surface and every folder from one beacon block, not from the project that is open.
created: 2026-10-06
confidence: high
relations:
  builds-on: ["[[decision-bootstrap-v2-guarantee]]", "[[decision-llm-inclusive-harness]]"]
  relates-to: ["[[plain-language]]"]
---

## For future agent
- **TL;DR:** The writing rule is injected before any project file is read. One sentence in `beacons.json` is the copy every surface gets. The full rule stays in user preferences.
- **As of:** 2026-10-06 · **Status:** current

## Context — what forced a choice

A fresh Cursor session opened on the design-system repo wrote plans in dense, coined language. The full rule already lived in `04-preferences/user-preferences.md`, and `06-context/CRITICAL_FACTS.md` points at it. Neither file is on the path a session loads when the open folder is some other repo. Skill routing does not pull the rule in unless the message says "plain language" or "jargon". Putting a copy of the rule inside each project would break the wall that employer repos never receive workspace content, and it would miss the next folder.

## Decision — what we chose

One standing sentence lives in the `rules` block of `02-shared-references/beacons.json`. `render_shims.py` writes that block into every beacon, including `00-bootstrap/dist/RULES.txt`. Session hooks print `RULES.txt` from the workspace checkout no matter which folder is open. Cursor's sessionStart success path includes those rules with the card. `~/AGENTS.md` (installer `--install-home-beacon`) and `~/Projects/AGENTS.md` are the ancestor copies Cursor already loads. Codex reads `~/.codex/AGENTS.md`. Claude's user beacon is the same text. Chat surfaces paste `BEACON.md`.

The full rule stays in `04-preferences/user-preferences.md`. The contract states the same rule in `AGENTS.md` core rules. `workspace-harness.py` fails if a rendered beacon drops the words "Plain language", or if the Cursor hook stops printing the standing rules on the card path.

## Rationale — why this option

The miss was the same class as the Figma-components miss that bootstrap v2 was built for: a rule that depends on the model opening a file will not fire in a new folder. The beacon and the hooks already follow the person. Adding the sentence there covers Claude, Cursor, Codex, and pasted chat surfaces with one source. A check makes the next edit idempotent. A new device gets it by rendering and running the existing installers.

## Consequences — what changes

- Re-render after any edit to the `rules` block (`render_shims.py --write`). CI runs `render_shims.py --check`.
- This machine, and any other, still needs the human installers: `--install-home-beacon`, `--install-projects-pointer`, `--install-shims=codex`, `--install-shims=cursor`. Then repaste the chat beacon and Cursor user rules, and `--ack-chat`. Claude's `~/.claude/CLAUDE.md` updates on `--install-pin`, because that file heals from the pin. The Claude session hook reads `RULES.txt` from the checkout, so it picks up the sentence on the next session without a re-pin.
- Do not copy the rule into an employer repo.
