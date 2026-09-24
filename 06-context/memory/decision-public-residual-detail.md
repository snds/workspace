---
type: decision
description: Gap detail follows the repo's visibility (Sean, 2026-09-23, walls F-14) — in a public repo a known gap is written at class level with a stable ID; runnable detail and machine posture stay held (or in a private repo); code, fixtures, operator controls, prohibitions and pinned fix history stay public.
created: 2026-09-23
confidence: high
relations:
  builds-on: ["[[decision-llm-inclusive-harness]]", "[[decision-externalize-everything-to-workspace]]"]
  relates-to: ["[[feedback-credential-scoping]]", "[[00-context-profiles]]"]
---

## For future agent
- **TL;DR:** How much detail a known gap gets depends on who can read the repo. This workspace is
  public, so a gap ("residual") is written at class level with a stable ID, and the recipe lives in
  the held folder. The rule is recorded on the `visibility: public` flag in [[00-context-profiles]].
- **As of:** 2026-09 · **Status:** current

## Context — what forced a choice
Wave 0 of the Zero-Vector harness published the Claude git floor and its coverage rows. The public
`surfaces.json` row for the identity component (H17) named the bypass mechanics. An earlier version
of the row also overclaimed that a later component already closed them. A verifier finding (walls F-14) asked how much of that detail a public table should
keep. The code already spells out the shapes it detects (published under D1), so this is not about
secrecy. It is about not handing readers, and agents blocked by the floor, a ready-made recipe list
in prose.

## Decision — what we chose
**Gap detail follows the repo's visibility** (Sean, 2026-09-23, F-14).

In a public repo, and this workspace is declared public, a known gap is written at class level:
- say that it exists;
- name its category in plain words;
- say which layer catches it and which does not;
- say what closes it and when (component and wave);
- give it a stable ID that points to the held record.

Two kinds of detail go to the held folder (`.claude/state/held/`), or to a private repo if the
detail must travel between devices:
- **Runnable detail:** exact flags, env variable names, commands, step sequences, and file paths an
  agent could forge.
- **Machine posture:** installs and versions per device, account and credential states, connector
  rosters, and network behavior.

Four things stay public:
1. Code, tests and fixtures may carry exact shapes when a detector or test needs them (D1). Their
   comments say what the code checks, not how to use it.
   - *Clarification, pending Sean's confirmation (2026-09-23):* the redacted probe records under
     `02-shared-references/probes/` count as verification evidence under this exception and stay
     public. `render_shims.py --check` resolves them, and the probes README sets their redaction
     rules. So the answer to H17-R7 goes in the tracked probe record and the class-level row; any
     detail beyond that goes to the held register.
2. Designed operator controls, such as kill switches and the human-only override, are interface,
   not residuals.
3. A prohibition may name the flag it forbids ("never `--no-verify`").
4. A fixed defect may keep its history once a fixture pins the fix.

Other repos:
- A private personal repo may keep mechanics next to the design.
- Employer repos get no workspace content at all (the existing rule).
- Unknown visibility counts as public, like the context profiles' fail-safe default.

First application (2026-09-23): the H17 row now cites IDs H17-R1 to H17-R10, each with a class-level
sentence; the held H17 residual register holds the shapes, fixtures and closing components. The
same register holds WALL-C1, the employer-capable channels outside git. The
per-device installs, gh accounts, credential store and connector roster moved to a held
machine-posture file, and the public files keep class-level statements.

## Rationale — why, and what we rejected
- The public text stays fully honest about which walls hold. Only the recipe moves.
- An agent that hits the floor should not find the way around it in the docs it reads every
  session.
- Rejected: removing the gaps from public text. A hidden gap is worse than a named one; the
  coverage rows exist to declare limits ([[decision-llm-inclusive-harness]]).
- Rejected: one fixed level for every table. The right level depends on the repo, which is why the
  rule hangs on the visibility flag.

## Consequences — what this commits us to
- Before writing a gap into a public file, write its detail to held first, then write the
  class-level sentence with its ID. Nothing may be lost in the move.
- **Trade-off, stated:** the held folder is local to one Mac, is gitignored and has no version
  history. Agents on the Personal MBP see only the class-level text and the IDs. A private repo is
  the durable home if the detail must travel between devices. Sean has not chosen that.
- **Trade-off, stated: public history keeps the old text.** Earlier versions of `surfaces.json` and
  the other rewritten files still hold the pre-F-14 detail in the public git history, because
  history is not rewritten (^pc-47). The rewrite limits what agents read in the current docs; it
  does not make that detail secret. Rewriting history would be a separate decision for Sean.
- Machine-posture statements outside the first pass (a network note, a multi-install note, the
  Personal MBP row) are listed in the held machine-posture file for a later scrub.
- **The receipt log's location is operator interface** (exception 2), not a residual detail. Humans
  read that log to audit housekeeping, and the public code names it under exception 1. H17-R5
  still describes the forgery risk at class level.
- A second scrub pass for machine posture outside the touched files is queued as ^pc-49.
- A report-only detector that flags bypass shapes in the prose fields of the declared tables,
  reusing the classifier's own lists, was proposed but not adopted. Revisit it if recipes drift
  back into prose.
