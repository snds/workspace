---
type: decision
description: Claude is an employer-approved surface (2026-10-06) — identity and conduct follow the repo remote and the device like Cursor and Codex; the personal-content, conduct and credential walls stay.
created: 2026-10-06
confidence: high
relations:
  refutes: ["[[feedback-credential-scoping]]"]
  builds-on: ["[[decision-llm-inclusive-harness]]", "[[decision-plain-language-is-standing]]"]
  relates-to: ["[[fact-workspace-repos]]", "[[decision-vendor-surface-artifacts]]"]
---

## For future agent
- **TL;DR:** Claude may do Centric work. A Claude session in a Centric repo runs under
  `centric-engineering` (branch → PR → human review), on the Work MBP, with the repo's Centric
  identity. Claude follows the same device and identity rules as Cursor and Codex. The walls that
  keep personal content, credentials and conduct apart did not move.
- **As of:** 2026-10-06 · **Status:** current

## Context — what forced a choice

Centric moved its agent tooling from ChatGPT to Claude in the week of 2026-10-06. The workspace
still said every Claude surface was personal-only and that Cursor and Codex were the only
employer-approved surfaces ([[feedback-credential-scoping]], 2026-09-22). That rule was enforced
mechanically, not just written down:

- The Claude env overlay rewrote every Centric remote to an unresolvable scheme, so fetch and push failed.
- The Claude git floor blocked every commit in an employer repo (invariant I2).
- Identity rule IR1 pinned every Claude family to `snds` on every device.
- The action policy routed Claude's employer reads and writes to Cursor or Codex (P10–P14).
- The wall guard routed employer vault folders, employer connectors and employer browser hosts away from Claude (R1).

So the rule blocked real work in the tool the employer now provides.

## Decision — what we chose

1. **Claude is an employer-approved surface.** It joins Cursor and Codex in the employer rules
   (P30–P32). It works in employer repos on the Work MBP only (P40 still denies employer authoring
   on the Personal MBP; an unknown or cloud device falls to the default deny).
2. **Conduct follows the repo remote, for every surface.** `snds/*` is `personal-solo`. Centric
   owners, and any owner that is not declared, are `centric-engineering`: no auto-commit, no
   self-merge, no push to the default branch. Work goes branch → PR → human engineer review. The
   Claude git floor enforces the default-branch rule for Claude at `pre-push`, beside the policy rules.
3. **Identity follows the device, like every other family, with one belt.** IR1 now applies only
   to personal repos: Claude in an `snds/*` repo commits as `snds` on every device (the "personal key
   for snds work" wall). Everywhere else Claude falls under IR2 (Work MBP → Centric; a mismatch is a
   flag; an express override suppresses it on non-employer repos) and IR3 (Personal MBP → `snds`).
   Claude overrides are no longer refused. The overlay applies this with two includes:
   - an `snds/*` remote gets `claude-identity.inc` (the personal identity);
   - every employer remote form gets `claude-employer-identity.inc` (the Centric identity, with
     `useConfigOnly`), included after the personal one. A fork that carries both remotes therefore
     commits as Centric, never as `snds`. This replaced the blank-identity include that kept Claude
     from committing in employer repos at all.
4. **The walls that stay:**
   - **Personal content never lands in an employer repo, and employer content never lands in a
     personal surface.** This covers personal claude.ai memory, Projects, artifacts and this
     public vault. I1 still blocks a personal identity on any employer commit or push. The overlay
     still withholds the `snds` identity from any repo with an employer remote, and the
     employer-substance check (H25) still guards this vault.
   - **`centric-engineering` binds Claude exactly as it binds Cursor and Codex** (P30, P31, and the floor).
   - **Credentials stay scoped by repo:**
     - `snds/*` goes over HTTPS with Claude's own gh config, which names only `snds`.
     - Centric remotes go over the `github-work` SSH alias.
     - `gh` calls on a Centric repo use the device-default gh account (`lift_env(needs_employer_gh=True)`; by hand, `env -u GH_CONFIG_DIR gh …`).
     - One session never pushes one repo's work with the other identity's credential.
5. **The Claude login account is not an identity key** (Sean, 2026-10-06). Centric issues a
   separate Claude account. Sean may still use his personal Claude account for Centric work when
   the work is clearly marked as Centric and its information stays in Centric repos and Centric
   project directories. The git and GitHub credentials decide who authors; the content wall decides
   where things are written.

## Rationale — why, and what we rejected

The old exception existed because Sean could not use Claude for employer work. That reason ended
on 2026-10-06. The walls Sean named as still mattering are about content, conduct and credentials.
None of them depends on which vendor's model is typing.

- **Rejected: keep the Claude family as a stricter belt.** It would keep blocking the work Centric now expects to happen in Claude.
- **Rejected: key Claude's identity by the logged-in Claude account.** Sean said the account does not decide this. Keying on it would also put a vendor login into the git identity model, and the harness keeps that model tool-neutral.
- **Rejected: drop the overlay's employer handling entirely.** The no-identity include for repos with employer remotes is what keeps `snds` off a mixed repo. It stays.

## Consequences — what this commits us to

- **Machines must reinstall the overlay.** `render_shims.py` no longer emits the employer
  transport block. Each machine needs `workspace-doctor.sh --install-claude-overlay` run by a human, plus a
  fresh Claude session. Until then the installed v5 overlay keeps blocking employer remotes.
  `context-remotes.json` keeps `blocked_scheme` only as the legacy marker, so tools can recognise
  and strip blocks from overlays installed before this change.
- **What changed in the harness** (so the next agent does not re-derive it):
  - `action-policy.json`: P11–P14 retired; P30–P33 cover `claude`; P21 is scoped to third-party
    and unknown owners, so an employer checkout off the Work MBP stays denied.
  - `devices.json`: IR1 gains `repo_class: personal`; I2 is now the all-agent feature-branch rule.
  - `profile_resolve.py`: `identity()` and the floor follow the rules above. The floor's employer
    branch checks I1 and refuses default-branch, unreadable-default and non-branch pushes. The
    Claude-chain read rule now also reads checkouts a human scan cached, so a feature branch can
    be seen.
  - `wall_guard.py`: R3 (I1) runs for Claude too. Employer vault folders, employer MCP channels
    and employer browser hosts are refused for Claude only off the work device. R7 is a notice.
  - `render_shims.py`: Claude's per-device permission denies for employer checkouts and folders
    are not expanded on the work device.
  - `session-status.py`, `closure.py` and `intent-run.py`: the restricted family is now
    `unknown-agent` only, so Claude gets the full card, closes employer work by branch and PR,
    and gets the neutral render path like Cursor.
- **Declared gap:** the surface-trajectory harness does not yet prove that Claude Code's prompt
  routes reach it in an employer-shaped working folder. Its sandbox has no brain pointer for the
  dispatcher. Cursor, Codex and the Cursor hook are proven there. Claude Code is proven in the
  workspace only.
- **Transport caveat:** Claude's Centric pushes go over the `github-work` SSH alias. ^pc-09 records
  that SSH to github.com can time out on the Work MBP. The overlay's HTTPS credential helper names
  only `snds`, so Claude has no HTTPS fallback for Centric yet. Tracked as ^pc-50.
- **Every beacon changes.** `beacons.json` replaces the Claude line. The claude.ai profile copy of
  `BEACON.md` lives outside the repo, so it must be re-pasted by hand.
- **Open risk, Sean's call, recorded rather than decided:** Centric's agreement with Anthropic
  probably covers the Centric account only. Centric work done under the personal account falls
  under consumer terms. The claude.ai memory pass can file Centric facts into personal memory
  unless memory is off for those chats. The content wall above is the rule. Whether that is enough
  is open.
- **WALL-C1 narrows.** The employer connector is no longer limited to movement-only use for Claude,
  so H15's "deny the employer connector to Claude" is retired as a goal.
