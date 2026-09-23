---
type: feedback
description: Identity is device-based EXCEPT Claude (2026-09-22) — every Claude surface is personal-only (snds) on every device and never does employer work; other surfaces follow the device (Work MBP → Centric unless expressly overridden; Personal MBP → snds); personal identity never lands in employer repos
created: 2026-07-20
updated: 2026-09-22
confidence: high
---

> **Exception (Sean, 2026-09-22, latest): every Claude surface is PERSONAL-ONLY, on every device.**
> This covers Claude Code, Claude Chat (claude.ai web, desktop and mobile), Claude in Chrome and the
> Claude desktop app. Sean cannot use Claude for employer work.
>
> - Claude always commits as `Sean Sands <570874+snds@users.noreply.github.com>` and authenticates
>   with the personal key, including on the Work MBP (where `github.com` → `id_ed25519_personal`).
> - Claude does **no employer work at all**. It does not open, edit, commit to or open PRs against
>   employer repos (cpes-software/*, c8*, Centric Bitbucket, design-system), and it does not paste
>   employer material. Employer-repo actions go to Cursor, Codex or Sean.
> - Every non-Claude surface follows the device rule below.

> **Update 2026-09-22 (Sean, in chat): identity is device-based, not surface-based** (except Claude;
> see above).
>
> - **Work MBP** (`CS-K746DRWXY1`; also `seansands.local` / `CS-KQ23N94M0W`): every agent
>   interaction, on **every** surface (Claude Code, Claude Chat, Cursor, Codex, …), is work/employer by
>   default and uses the **Centric** identity, unless Sean **expressly** says otherwise for a specific
>   task. Workspace commits from this laptop keep using the Centric identity: the deliberate crossover
>   described below still stands.
> - **Personal MBP** (`Voyager-2.local`): every agent interaction, on every surface, is **personal**
>   and uses `snds`.
> - **Absolute on every device:** personal identity never appears on an employer-repo commit.
> - An express override must be visible, scoped to one task, and self-expiring. It is never an ad-hoc
>   `-c user.*` flag. The harness plan (v1.1: declared device table, git-boundary check) makes this
>   mechanical for all surfaces.
>
> This session's earlier commits `6cac460` and `353f4f1` were made from Claude Code before the Claude
> exception existed, so they are Centric-authored and were pushed over `github-work`. Whether to
> rewrite them is Sean's call.

**On the Centric laptop (`CS-K746DRWXY1`), all work uses the Centric credentials unless Sean says
otherwise. No other account is used for anything — commits, pushes, or auth.**

This is machine-scoped, not repo-scoped. The old formulation ("Centric repos → Centric auth; any
personal/workspace surface → personal `snds` auth") is **superseded on this machine**: it produced the
wrong answer for the one case that matters most in practice.

**The one deliberate crossover:** the personal workspace repo (`github.com/snds/workspace`) is committed
to **with the Centric account**, because that account is added to the repo as a contributor. This is
intentional and is the only place the Centric login touches a personally-owned repo.

- **Never** the reverse. Personal credentials (`snds` / `hello@snds.design` / `570874+snds@…`) never
  appear on this machine's commits, in any repo, employer or personal.
- Never override a repo's local git config with explicit `-c user.name` / `-c user.email` flags. The
  repo-local config is already correct; overriding it is how the wrong identity gets in.

**Why:** Employer work must never carry Sean's personal identity — it is an attribution and
separation-of-concerns problem, not a stylistic one. The workspace repo is the shared context and
skillset layer for both personal and Centric work, so the Centric account was deliberately granted
contributor access: it lets improvements and Centric-related context be written back to the shared brain
without either identity leaking into the wrong place. Sean stated this after I committed two merge
commits to `cpes-software/centric-ui` as `Sean Sands <hello@snds.design>` — I had passed explicit
`-c user.*` flags that overrode an already-correct repo-local config, then reported the mistake as a
footnote instead of fixing it. See [[fact-workspace-repos]] for the repo topology.

**How to apply:**

- Before any commit on this machine, confirm the identity resolves to the Centric account
  (`Sean Sands <271648271+sean-sands-centric@users.noreply.github.com>`). Let repo-local config do its
  job; pass no identity flags.
- Workspace repo pushes go over the `github-work` SSH alias so they authenticate as
  `sean-sands-centric`. Plain `github.com` resolves to the personal key on this machine — wrong account.
- If a personal-identity commit ever reaches a remote, treat it as urgent: rewrite and force-push
  immediately, then audit every ref (`git log --all --format='%an <%ae>|%cn <%ce>' | grep -i …`) rather
  than assuming the visible tip was the only one. Note that force-push does not purge the old SHA from
  GitHub — it stays reachable by direct URL until GC, so say so plainly rather than implying it's gone.
- On the Personal MBP, the device rule in the update above applies (personal, `snds`). Any future
  machine gets a row in the declared device table before any agent commits from it.
