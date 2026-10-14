---
title: Synapse — Decision log
type: plan
project: 26-synapse
status: draft
updated: 2026-10-14
---

# Decision log

Newest decisions go at the bottom. Entries D1–D36 use the old codename, Switchyard; read it as Synapse (see D37). A decision changes only through a new entry that names the one it replaces.

| ID | Date | Decision | Why | Rejected |
|---|---|---|---|---|
| D1 | 2026-10-14 | Build a separate app, outside the workspace | Sean: don't solve it inside the workspace. The workspace stays a consumer. | Extending the workspace's credential overlay |
| D2 | 2026-10-14 | "Switchyard" is a working name (superseded by D37) | Needed a handle. A trademark check is required before any public use. | — |
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
| D14 | 2026-10-14 | The Work MBP holds personal and employer identities from the start (employer check confirmed in D27) | Sean: cover both cases | Personal-only first |
| D15 | 2026-10-14 | Employer identities and data never leave the Work MBP: no Vaultwarden, no hub, no other device | The workspace's employer wall, applied to credentials | — |
| D16 | 2026-10-14 | The Windows PC is personal-only (assumption; confirmed in D26) | It is used for personal Drive cleanup | — |
| D17 | 2026-10-14 | The hub is optional, self-hosted on Unraid, and sees only ciphertext | Fleet sync without trusting the server, and a product path | A plain file in a synced folder (no rollback or enrollment protection) |
| D18 | 2026-10-14 | The app never reveals or copies a secret | Copying tokens is the most common way they leak | A "reveal token" button behind a presence check |
| D19 | 2026-10-14 | Commercial path adds a GUI workspace generator built over the `wsx` engine (superseded by D21 and D34: Create and Import are core) | Sean's request. One engine, so the GUI never forks `wsx` logic. | A separate generator inside Switchyard |
| D20 | 2026-10-14 | Order: Watch, Broker, Gateway, Fleet; product only after a go decision (now the access module's internal order; app order in D35) | Each phase is useful alone. Risk goes up only after value is proven. | Building the broker first |
| D21 | 2026-10-14 | **Reframe:** Switchyard becomes a desktop workspace app with a tray service. Credential routing becomes its Personas & access module. | Sean: logins are a symptom. The real problem is that the workspace can't be seen or managed without heavy agent work. | Keeping a credential-only app |
| D22 | 2026-10-14 | Files stay the source of truth, in the standard agent formats. The app's index is a rebuildable cache. | Sean: read and write what agents and AI-focused users treat as standard | An app-owned database with files as export |
| D23 | 2026-10-14 | Workspace scripts and tools live in the workspace in their own language, each with a `tool.json` manifest | Sean: agent-made tools must stay usable by any agent in its chosen language | Porting every tool into the app |
| D24 | 2026-10-14 | Obsidian keeps reading and writing the vault. The app watches changes and proposes fixes for files that break the structure, never silently. | Sean | Locking the vault while the app runs |
| D25 | 2026-10-14 | Personas are user-defined. Walls hold by app, or by separate installs of the same app. | Sean | Fixed work/personal only |
| D26 | 2026-10-14 | The Windows PC is personal-only (confirmed) | Sean | — |
| D27 | 2026-10-14 | The employer allows a personal tool to hold employer logins on the Work MBP (confirmed) | Sean | — |
| D28 | 2026-10-14 | Agent optional, agent enhanced. Agents discover, code enforces: repeated agent findings become deterministic checks. | Sean: doctor and optimize must run without an agent. Matches the workspace's close-out and self-improve rule. | Agent-only features |
| D29 | 2026-10-14 | The first scanner is agentic. It must follow every node path with a coverage ledger, judge the whole graph, and report in a fixed schema with evidence. | Sean | A rule-only scanner first |
| D30 | 2026-10-14 | Import and Create are measured by scorecards with release gates. A pinned snapshot of Sean's workspace is the north-star test set, kept local only. | Sean: it needs to be rigorous | Manual spot checks |
| D31 | 2026-10-14 | **Proposed:** Domain becomes a first-class node with its own file. Domains hold areas, each led by one hub. The final map is set after the first scan. | Sean's domain idea. Today `domain` is only a tag, and design has 26 hubs. | Treating each hub as a domain |
| D32 | 2026-10-14 | "Switchyard" stays the working name, now for the whole app (superseded by D37) | Continuity. The name is decided in Stage 0. | — |
| D33 | 2026-10-14 | **Proposed:** `wsx` (project 18) becomes the reference design and test oracle, archived into this project once the app reaches parity | One generator, no fork | Running two generators |
| D34 | 2026-10-14 | Create and Import are core features (Stage 3), not commercial add-ons | Sean: bake them together | — |
| D35 | 2026-10-14 | **Proposed** app order: model and map → engine → app → import/create/measure → access → agents/plugins/3D → fleet. Access can move ahead of import if login pain grows. | Sean named the generator and structure as the biggest part. Every stage is useful alone. | Access first |
| D36 | 2026-10-14 | **Proposed:** secrets live in a separate access process. The tray service, which runs tools, plugins and agent jobs, never holds them. | Least privilege by process | One service process for everything |
| D37 | 2026-10-14 | **Codename is now Synapse.** User-facing text will take the name from one brand file. Internal identifiers use the neutral prefix `sy` (CLI `sy`, access process `sy-access`, helper `git-credential-sy`, secret references `sy://`, Mac data folder `design.snds.sy`, Windows `%LOCALAPPDATA%\snds\sy`), so a rebrand doesn't move keychain items, data folders or URL schemes. Every place the name appears is tracked in a name ledger with a check, built in Stage 0. | Sean: the name may change for branding or legal reasons, so the swap must be mechanical. "Synapse" is already used by several software products. | Brand-derived identifiers throughout |
