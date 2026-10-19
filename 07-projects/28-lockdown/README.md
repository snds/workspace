---
title: Lockdown
type: project
status: Planning
triggers: [lockdown, password manager, passkey provider, steam guard, vendor login bridge, credential exchange, tv activation, device code login]
frameworks: [engineering-operating-model, security-operating-model, qa-operating-model, ui-ux-operational, design-systems-ai, domain-rigor-stack]
related_projects: [26-synapse, 25-fontface, 24-mailbird]
---

# Lockdown (28-lockdown)

_Working name. No trademark check yet._

A cross-platform password manager, passkey provider, and authenticator. The goal is to meet and beat 1Password, Bitwarden, Proton Pass, Vaultwarden, and Apple Passwords, and to sign people in through each service's own supported login (passkeys, one-time codes, TV activation codes), with Steam as the one fenced, opt-in private bridge.

- **Status:** desktop and web build waves 1–5 landed (main `90be789`, 357 decisions, twenty-eight slices). What remains waits on Sean or on OS-level and native-mobile work.
- **Status page:** https://claude.ai/artifact/662Gqj3VZUFpjSnvsfgEqp — every ask, next build, feature, flagged decision, and slice, each with a `#id` link. Source `roadmap.html`, rebuilt by `build-roadmap.py --repo ~/Projects/lockdown`. Charts stay on the dashboard, https://claude.ai/artifact/9gVWpq3tPqx83JZDjBtk4a.
- **Context profile:** `personal-solo`. Repo remote is `snds/lockdown` (private).
- **Code repo:** `~/Projects/lockdown`, remote `snds/lockdown`. First commit `e6d9248` holds the research only.
- **This folder:** baton and pointers only. Research, brief, and matrix live in the repo, the same as Fontface and Synapse.
- **Baton:** [[07-projects/28-lockdown/SESSION-STATE|SESSION-STATE]].

## Where things are (in the repo)

| Path | What |
|---|---|
| `docs/research/2026-10-15/brief.md` | Start here. Vendor-login verdicts, bridge catalog, positioning, security design, stack, roadmap, open questions. |
| `docs/research/2026-10-15/feature-matrix.json` | 201 features x 9 products, each with Lockdown's target (parity, beat, novel) and phase |
| `docs/research/2026-10-15/verification.json` | Fact-check verdicts on 45 load-bearing claims. Where it disagrees with a report, it wins. |
| `docs/research/2026-10-15/report.html` | The interactive report page (matrix embedded) |
| `docs/research/2026-10-15/reports/` | The seven underlying research reports |

**Readable copy:** https://claude.ai/artifact/PT8FzNxTVLzrUr3AdVWHry (private until shared). Built from `report.html`; edit the repo file, then republish.

## Headline findings

- Being an OS passkey provider gives "scan the QR on the laptop, approve on the phone" for every passkey site. iOS provides it for free (Apple staff, June 2026); Android 14+ works with OEM gaps.
- Steam QR approval is feasible via a tolerated reverse-engineered protocol (`steamguard` Rust crate, MIT/Apache). Only authenticator *removal* costs the 15-day trade hold; file import costs none.
- Battle.net and Adobe: use passkeys. Nobody has rebuilt their push channels. Decline them.
- TV/console device-code activation (RFC 8628) is the legitimate generalization of "approve from my phone." Hard rule: approve only codes the user scanned themselves.
- Security bar: assume a hostile server (ETH Zurich 2026 model). OPAQUE login, Secret Key by default, hybrid post-quantum key wrapping, key transparency, signed anti-rollback manifests.

## Walls

- The Steam bridge needs US and EU legal review before it ships. Nothing in the research is legal advice.
- Crown-jewel secrets (Steam `identity_secret`, seed phrases) never autofill, never reach AI agents, and get their own key.
