---
type: feedback
description: Identity is device-based for every surface, Claude included (2026-10-06) — Work MBP → Centric, Personal MBP → snds; conduct follows the repo remote; personal identity never lands in employer repos; credentials follow the repo owner through gh_route.py on every surface (2026-10-13)
created: 2026-07-20
updated: 2026-10-13
confidence: high
relations:
  builds-on: ["[[decision-claude-employer-surface]]"]
---

## Current rule (Sean, 2026-10-06)

**Every surface follows the device, Claude included** ([[decision-claude-employer-surface]]). The
2026-09-22 Claude exception ("Claude is personal-only on every device") is retired; its text is in
History below.

- **Work MBP** (`CS-K746DRWXY1`; also `seansands.local`): work/employer by default, using the
  Centric identity `Sean Sands <271648271+sean-sands-centric@users.noreply.github.com>`, unless Sean
  expressly overrides for one task (IR2). Its credential comes from `gh_route.py` (below); before
  2026-10-13 it was the `github-work` SSH alias.
- **Personal MBP** (`Voyager-2.local`): personal (`snds`) (IR3).
- **Conduct follows the repo remote.** `snds/*` → `personal-solo`. Centric owners and undeclared
  owners → `centric-engineering`: feature branch → PR → human review, no self-merge, no push to the
  default branch. Employer authoring happens on the Work MBP only (P40).

**Absolute on every device, for every surface:** personal identity never appears on an employer-repo
commit (I1). Credentials stay scoped per repo: the personal key and account for `snds/*`, the
Centric account and grants for Centric repos, never crossed within one session.

## How it is applied

Since 2026-10-13 (`fd5d1ab`, [[decision-claude-employer-surface]] amendment 2026-10-13; installed by
Sean 2026-10-14: pin → git-hooks → Claude overlay v6, ^pc-50):

- **Every surface, Claude included: the GitHub account follows the repo owner.**
  `09-tools/gh_route.py` (pinned) picks the account from the repo's owner: `snds/*` gets `snds`, the
  Centric org gets the employer account, any other owner gets nothing.
  - Git reaches it as the credential helper `bin/git-credential-ws`: overlay v6 for Claude, the git
    lanes include for Terminal, Cursor and Codex.
  - `gh` reaches it through `bin/gh`, linked first on PATH as `~/.local/bin/gh`.
  - SSH forms of both owners fetch over HTTPS, so the `github-work` SSH alias is no longer the
    route (^pc-09).
  - A repo can only receive its own owner's token, and a `gh` call that names two owners is
    refused. Per-device credential and network detail is held.
- **No surface switches accounts by hand.** No `gh auth switch` before a call, no
  `env -u GH_CONFIG_DIR`. Logging in is still `gh auth login` / `gh auth refresh` (the router passes
  `gh auth` through unchanged); follow the doctor's login note, which names the account and ends with
  `gh auth switch` back to the device default.
- **Claude identity:** the user-scope env overlay (v6), rendered to
  `00-bootstrap/dist/claude-overlay.env` and installed by `ws-doctor --install-claude-overlay` (a
  human runs it).
  - `snds/*` remotes get `snds` from `includeIf hasconfig` via
    `~/.config/snds-workspace/git/claude-identity.inc`. A repo with any employer remote gets a later
    no-identity include, so `snds` never applies there; the repo-local Centric identity does.
  - Since 2026-10-06 the overlay no longer rewrites employer remotes to an unresolvable scheme.
    `context-remotes.json` `blocked_scheme` is kept as the legacy marker the tools strip.
  - The Claude git floor (`ws-hook --floor claude`) still enforces I1 on employer commits and
    pushes, and refuses a push that writes the default branch of an employer repo.
- **Tracker connectors stay attached to Claude** (Sean, 2026-09-22): the personal one and the
  employer one. Since 2026-10-06 Claude may use the employer connector for employer work on the Work
  MBP. Employer substance it reads there stays in employer surfaces, never in personal memory or
  this vault.
- **Everyone else:** the same route through the lanes include; identity is repo-local git config
  (Centric noreply on the Work MBP).
- **Employer email domain (Sean, 2026-09-23):** `centricsoftware.com`. Any address on that domain
  counts as employer in the identity checks (`devices.json` `employer_allowlist.email_domains`,
  beside the Centric identity id). Sean will say if the employer changes. Do not guess a new one.
- **Never** use ad-hoc `-c user.*` identity flags. A mechanical per-surface, per-device table and
  git-boundary checks are harness plan v1.1 (H2/H17/H22).

**Why:** employer commits must never carry Sean's personal identity, and personal content must
never reach an employer repo. That is an attribution and separation problem, not a stylistic one.
The workspace is the shared layer both identities write to, so which identity writes it follows the
device, and which conduct applies follows the repo.

## History (superseded, kept for provenance)

- **2026-10-06 → 2026-10-13 (superseded by `gh_route.py`, `fd5d1ab`):** how Claude's credentials
  were applied before the one GitHub route. Kept verbatim for provenance:

  > ## How it is applied
  >
  > - **Claude:** the user-scope env overlay, rendered to `00-bootstrap/dist/claude-overlay.env` and
  >   installed by `ws-doctor --install-claude-overlay` (a human runs it).
  >   - `snds/*` remotes get `snds` from `includeIf hasconfig` via
  >     `~/.config/snds-workspace/git/claude-identity.inc`. A repo with any employer remote gets a later
  >     no-identity include, so `snds` never applies there; the repo-local Centric identity does.
  >   - `snds/*` traffic goes over **HTTPS** (overlay v4, Sean 2026-09-22), because SSH to github.com
  >     is unreliable on some networks (^pc-09). The overlay resets the `https://github.com`
  >     credential-helper list and uses `!gh auth git-credential` through Claude's own gh config, which
  >     names only `snds`. Centric remotes use the `github-work` SSH alias and its Centric key.
  >     Per-device credential and network detail is held.
  >   - Since 2026-10-06 the overlay no longer rewrites employer remotes to an unresolvable scheme.
  >     Machines still running an older overlay keep that block until the overlay is reinstalled.
  >     `context-remotes.json` `blocked_scheme` is kept as the legacy marker the tools strip.
  >   - The Claude git floor (`ws-hook --floor claude`) still enforces I1 on employer commits and
  >     pushes, and refuses a push that writes the default branch of an employer repo.
  > - **Claude's `gh`:** Claude's gh config names only `snds`. A `gh` call on a Centric repo uses the
  >   device-default account: the vetted env drops `GH_CONFIG_DIR` (`lift_env(needs_employer_gh=True)`),
  >   and by hand it is `env -u GH_CONFIG_DIR gh …`.
  >   - The machine-default gh config keeps the device's default account (`devices.json`) **active**,
  >     because Cursor, Codex, the terminal and Claude's employer calls all share it. Per-device account
  >     state is held.
  >   - After any `gh auth login`, run `gh auth switch` back to the device default. Logging in makes the
  >     new account active for every surface.
  > - **Everyone else:** repo-local git config (Centric noreply on the Work MBP).

- **2026-09-22 → 2026-10-06 (superseded by [[decision-claude-employer-surface]]):** the Claude exception.
  Its rule text, kept verbatim for provenance:

  > ## Current rule (Sean, 2026-09-22)
  >
  > **Claude surfaces are personal-only on every device.** This covers Claude Code (CLI, desktop, IDE
  > extensions, web), Claude Chat (web, desktop, mobile), Claude in Chrome and Cowork.
  > - Claude commits as `Sean Sands <570874+snds@users.noreply.github.com>` and authenticates with the
  >   personal key, including on the Work MBP.
  > - It does no substantive employer work. It does not read, map or edit employer code, and it does not
  >   commit to or open PRs against employer repos (the `centric-engineering` profile;
  >   `ws resolve repo` names it).
  > - **Housekeeping is allowed, with receipts:** pruning merged `@me` branches, fast-forwarding `main`
  >   and removing clean merged worktrees. It runs only through vetted scripts, never through commands
  >   Claude composes itself, and each run prints a receipt naming the repo, the action and the
  >   credential used.
  >
  > **Employer-approved surfaces are Cursor and Codex.** They have full use of the workspace harness in
  > employer repos (the clones under `~/Projects` on the Work MBP), including read-only mapping and
  > recon. They publish through feature branch → PR → human review; merging is human-only.
  >
  > **Every non-Claude surface follows the device:**
  > - Work MBP (`CS-K746DRWXY1`; also `seansands.local`): work/employer by default,
  >   using the Centric identity `Sean Sands <271648271+sean-sands-centric@users.noreply.github.com>`
  >   over the `github-work` SSH alias, unless Sean expressly overrides for one task. Workspace commits
  >   from Cursor/Codex here are Centric: the deliberate contributor crossover.
  > - Personal MBP (`Voyager-2.local`): personal (`snds`).
  >
  > **Absolute on every device, for every surface:** personal identity never appears on an employer-repo
  > commit.
  >
  > ## How it is applied
  >
  > - **Claude:** the user-scope env overlay in `~/.claude/settings.json`, sourced from
  >   `00-bootstrap/dist/settings-user-fragment.json` (v2, marker `WS_CLAUDE_OVERLAY=v2`).
  >   - Identity comes from `includeIf hasconfig` on `snds/*` remote URLs, via
  >     `~/.config/snds-workspace/git/claude-identity.inc`, so an employer checkout never gets `snds`
  >     from it.
  >   - `snds/*` traffic goes over **HTTPS** (overlay v4, Sean 2026-09-22), because SSH to github.com
  >     is unreliable on some networks (^pc-09). The overlay resets the `https://github.com`
  >     credential-helper list, so no device-level credential store can answer first. It then uses
  >     `!gh auth git-credential` through Claude's own gh config, which resolves to `snds`.
  >     Per-device credential and network detail is held.
  >   - Employer remotes in their declared spellings are rewritten to an unresolvable scheme, so a push
  >     Claude composes itself fails. Spellings the rewrite misses are left to the git floor (residual
  >     H17-R6), and so is another rewrite for an employer remote, given for one command or written
  >     into any git config file (the repository's, the user's or the system's), that undoes the block
  >     for that remote (residual H17-R9).
  >   - v1 (`bb4cf05`) set `GIT_AUTHOR_*` unconditionally and was replaced by `0d19852`. Claude sessions
  >     started before that still carry v1 until they are restarted.
  > - **Claude's `gh`:** overlay v3 points Claude's gh at a Claude-only gh config that names only
  >   `snds`. The token stays in the OS keyring.
  >   - The machine-default gh config keeps the device's default account (`devices.json`) **active**,
  >     because Cursor, Codex and the terminal all share it. Per-device account state is held.
  >   - After any `gh auth login`, run `gh auth switch` back to the device default. Logging in makes the
  >     new account active for every surface.
  >   - Vetted housekeeping uses the device default gh account only for employer gh calls.
  > - **Tracker connectors stay attached to Claude** (Sean, 2026-09-22): the personal one and the
  >   employer one. Claude uses the employer connector only for the Open Engine `c8` lane's movement
  >   (pointers, statuses, receipts), never for employer substance. No mechanical layer limits what it
  >   writes there; the limit is this rule and the lane's movement-only design. This is part of the
  >   known gap WALL-C1 (employer-capable channels outside git, with browser control, desktop control and a
  >   terminal beside the session).
  >   What closes it: H15 (wave 1) denies the employer connector's tools to Claude, which would also
  >   end the movement use above, and adds an employer-host check for browser control driven from
  >   Claude Code; the browser profile (harness decision 3) covers the rest; desktop control has no
  >   planned close. The per-device connector roster is held.
  > - **Everyone else:** repo-local git config (Centric noreply on the Work MBP).
  > - **Employer email domain (Sean, 2026-09-23):** `centricsoftware.com`. Any address on that domain
  >   counts as employer in the identity checks (`devices.json` `employer_allowlist.email_domains`,
  >   beside the Centric identity id). Sean will say if the employer changes. Do not guess a new one.
  > - **Never** use ad-hoc `-c user.*` identity flags. A mechanical per-surface, per-device table and
  >   git-boundary checks are harness plan v1.1 (H2/H17/H22).
  >
  > **Why:** Sean cannot use Claude for employer work. Employer commits must never carry his personal
  > identity; that is an attribution and separation problem, not a stylistic one. The workspace is the
  > shared layer both identities write to, so which identity writes it follows the surface and device.
- **2026-07-20 → 2026-09-22:** "On the Centric laptop, all work uses the Centric credentials, and
  personal credentials never appear on this machine's commits." Sean set this after an agent passed
  `-c user.*` flags that put `Sean Sands <hello@snds.design>` on two merge commits in
  `cpes-software/centric-ui`, and then reported the mistake as a footnote. The lesson stands: never
  override repo-local identity ad hoc, and treat a personal-identity commit reaching an employer
  remote as urgent. Rewrite and force-push, audit every ref
  (`git log --all --format='%an <%ae>|%cn <%ce>'`), and state plainly that GitHub keeps the old SHA
  reachable until GC.
- **2026-09-22 (same day, withdrawn):** a brief per-surface rule ("Claude defaults to `snds`"), then a
  device-only rule. Both were replaced by the current rule above.
- This session's commits `6cac460` and `353f4f1` were made from Claude Code before the Claude
  exception existed, so they are Centric-authored. Sean chose to leave them as they are.

See [[fact-workspace-repos]] for the repo topology and [[decision-llm-inclusive-harness]] for the
harness rule.
