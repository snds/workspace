---
type: decision
description: Project intent (problem, audience, knowns/unknowns, scope) lives in each project's own repo under the platform Projects dir; the vault points at it. centric-ui inherits the saas-plm-prototype intent.
created: 2026-09-22
confidence: high
relations:
  builds-on: ["[[decision-llm-inclusive-harness]]", "[[decision-externalize-everything-to-workspace]]"]
  relates-to: ["[[zero-vector-design-methodology]]"]
---

## For future agent
- **TL;DR:** A project's intent declaration lives **in that project's repo**, which is resolved per
  machine from the platform `Projects` directory and never hardcoded. The vault's
  `07-projects/<id>/` points at it and never copies it. **`centric-ui` has no intent of its own:** it
  inherits the intent and context of `saas-plm-prototype`, the precursor design document and
  application.
- **As of:** 2026-09 · **Status:** current

## Context — what forced a choice
The harness plan (2026-09-22) proposed a `## Project intent` block, first in the vault README and
later in PROJECT.md for external repos. Sean decided the home is the repo itself. The repo travels
with the code, is readable by every agent working in it on any surface, and syncs through git.

## Decision — what we chose
- The intent file lives at the root of each project repo. It uses a tool-neutral filename, and the
  repo's own `AGENTS.md` carries a pointer to it. The filename and shape are fixed by the harness plan
  (H4 revision).
- Vault project folders keep operational state (SESSION-STATE) plus a pointer to the repo's intent file.
- **Inheritance:** a repo may declare that its intent comes from another repo instead of holding its
  own. `centric-ui` → `saas-plm-prototype`. Inheritance and every other cross-repo reference use the
  **remote slug** (e.g. `cpes-software/saas-plm-prototype`), never a path. Each device (Work MBP
  `/Users/sean.sands/Projects`, Personal MBP `/Users/snds/Projects`) resolves the local checkout
  itself; see [[decision-llm-inclusive-harness]] §5.
- **Employer repos** (`centric-engineering`: cpes-software/*, c8, Centric Bitbucket): the intent file
  arrives only by branch → PR → human review. It is written in neutral engineer voice with no
  personal-workspace content (skill names, vault paths, beacon text). Nothing in it is copied back
  into the tracked vault.
- A project with **no repo** keeps its intent in its vault project folder (confirmed by Sean
  2026-09-22). If a repo is created later, the intent moves into the repo and the vault keeps a pointer.

## Rationale — why, and what we rejected
Rejected: vault-hosted intent. Agents working in a repo worktree often cannot read the vault. The
ShadeGraph README already notes this, which is why it keeps an in-repo AGENTS.md. Rejected: a
separate intent for centric-ui, because the prototype is its design source of truth, so a second
declaration would drift from it.

## Consequences — what this commits us to
- `intent-run` lint resolves an intent file by walking to the repo root. It follows inheritance
  pointers across sibling checkouts found through the profile resolver, and reports an honest
  "unresolvable here" when the sibling repo is absent on this machine.
- Employer-repo intent work is a PR for a human to review. Agents never commit it to the default
  branch.
