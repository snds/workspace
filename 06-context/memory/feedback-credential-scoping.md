---
type: feedback
description: On the Centric laptop every repo action uses Centric credentials — including the personal workspace repo, where the Centric account is a contributor
created: 2026-07-20
confidence: high
---

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
- On other machines, this entry does not apply — resolve identity per that machine's own setup.
