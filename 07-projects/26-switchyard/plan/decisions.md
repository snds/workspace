---
title: Switchyard — Decision log
type: plan
project: 26-switchyard
status: draft
updated: 2026-10-14
---

# Decision log

Newest decisions go at the bottom. A decision changes only through a new entry that names the one it replaces.

| ID | Date | Decision | Why | Rejected |
|---|---|---|---|---|
| D1 | 2026-10-14 | Build a separate app, outside the workspace | Sean: don't solve it inside the workspace. The workspace stays a consumer. | Extending the workspace's credential overlay |
| D2 | 2026-10-14 | "Switchyard" is a working name | Needed a handle. A trademark check is required before any public use. | — |
| D3 | 2026-10-14 | For Sean only for now, built to product-grade security | Sean: comprehensive security whether personal or sold | Lighter security for the personal phase |
| D4 | 2026-10-14 | macOS and Windows in every phase; Linux designed for, built later | Sean uses a Windows PC too. Parity is cheaper built in than bolted on. | Mac-only first |
| D5 | 2026-10-14 | Rust core + Tauri 2 + React 19/TypeScript/Vite | Precise control of secret memory, small fast helper binaries, cross-platform, same stack as Fontface | SwiftUI (Mac only), Go + Wails (garbage collector, second stack), Electron (heavy) |
| D6 | 2026-10-14 | A headless daemon holds secrets; the app holds none | The UI's web engine is the largest attack surface. A UI crash never breaks routing. | One process for both |
| D7 | 2026-10-14 | Secrets stay in each device's secure storage; only rules sync | Per-device tokens can be revoked on their own. A stolen sync copy holds nothing. | Syncing tokens through the hub or Vaultwarden |
| D8 | 2026-10-14 | Rules pick the identity from context; unmatched means denied | Removes the "active account" entirely. Callers, including injected agents, can't choose. | Caller-chosen identity, default identity fallback |
| D9 | 2026-10-14 | A repo with any employer remote is employer context for all its remotes | Blocks pushing employer code to a personal remote | Classifying each remote alone |
| D10 | 2026-10-14 | HTTPS first for git; SSH through a wrapper with `IdentitiesOnly` | SSH to GitHub is unreliable on some networks. The wrapper removes host aliases. | SSH-first with host aliases |
| D11 | 2026-10-14 | Vaultwarden on Unraid replaces 1Password as the password manager | Sean's preference. Parity is good for everyday use. Switchyard covers `op run` and shell plugins. | Staying on 1Password, Bitwarden cloud |
| D12 | 2026-10-14 | Switchyard never needs Vaultwarden to run; it integrates at setup time, for the recovery kit and for health checks only | A home server outage must not break git | Vaultwarden as the live credential source |
| D13 | 2026-10-14 | Reach Bitwarden through the `bw` CLI, never the SDK; never use `bw serve` | SDK license limits use with other servers and forbids resale. `bw serve` has no authentication. | Linking the Bitwarden SDK |
| D14 | 2026-10-14 | The Work MBP holds personal and employer identities from the start, pending the employer policy check | Sean: cover both cases | Personal-only first |
| D15 | 2026-10-14 | Employer identities and data never leave the Work MBP: no Vaultwarden, no hub, no other device | The workspace's employer wall, applied to credentials | — |
| D16 | 2026-10-14 | The Windows PC is personal-only (assumption, to confirm) | It is used for personal Drive cleanup | — |
| D17 | 2026-10-14 | The hub is optional, self-hosted on Unraid, and sees only ciphertext | Fleet sync without trusting the server, and a product path | A plain file in a synced folder (no rollback or enrollment protection) |
| D18 | 2026-10-14 | The app never reveals or copies a secret | Copying tokens is the most common way they leak | A "reveal token" button behind a presence check |
| D19 | 2026-10-14 | Commercial path adds a GUI workspace generator built over the `wsx` engine | Sean's request. One engine, so the GUI never forks `wsx` logic. | A separate generator inside Switchyard |
| D20 | 2026-10-14 | Order: Watch, Broker, Gateway, Fleet; product only after a go decision | Each phase is useful alone. Risk goes up only after value is proven. | Building the broker first |
