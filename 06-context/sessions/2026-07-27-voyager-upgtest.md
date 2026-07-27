### 2026-07-27 (pt.2) — upgrade-safety, thin adapter, and captured voice/tone prefs

SessionID: 2026-07-27-voyager-upgtest
--- SESSION BLOCK ---
Date: 2026-07-27
Machine: Personal MacBook Pro
Surface: Claude Code (Mac desktop app)
Project(s): 18-bootstrap-generator, (workspace: 04-preferences)
Summary: After v0.2 feature-complete, ran a copy-test of `wsx upgrade` against a full copy of
  ~/Projects/Workspace (801M, discarded) to find what it would do to a rich hand-built vault.
  Cataloged the negative outcomes and fixed them, then built the thin adapter, then captured
  Sean's real communication preferences.
Artifacts:
  - generator A (upgrade safety, commit b9252a5): A1 registry.build never clobbers a foreign
    skills.registry.json (writes .wsx.json alongside); A2 no fabricated placeholder profile;
    A3 build-related no longer auto-edits skills on a foreign vault (gated on the foreign flag
    captured BEFORE copy_cli creates .wsx/); A4 upgrade detects a not-wsx-generated rich vault
    and REFUSES (mirrors examine's don't-downgrade; --force overrides).
  - generator B (thin adapter, commit 6699bf0): new adapter.py + `wsx adapter [path]` maps a
    foreign vault's folders→wsx concepts (.wsx/adapter.json, reference mode) + copies the CLI.
    core.find_workspace_root recognizes an adapted vault. REFERENCE-MODE guards: upgrade refuses,
    adapters.emit refuses, moc.write_mocs builds only registry.wsx.json, wire is additive-only —
    so wsx never overwrites _HOME.md/AGENTS.md/CLAUDE.md/registry. Read-only tools (examine/health) work.
  - generator addendum (commit 1a005c2): voice/tone is now first-class — scaffold preferences
    template gains Voice + "Never do these" + Teaching-altitude sections; CLAUDE.md/AGENTS.md +
    the bridge pointer point every LLM at preferences/user-preferences.md as governing.
  - 04-preferences/user-preferences.md (commit 230a340): captured Sean's real prefs — anti-patterns
    (incl. the "honest assessment" tell), sociable-professional voice w/ practicality + light
    sarcasm (never over-index), thorough-when-it-matters, design-relative teaching + optional-source rule.
Decisions:
  - Do NOT run `wsx upgrade` on Sean's real vault — examine says it exceeds the model; upgrade
    would downgrade/clobber. The right path is the reference-mode adapter, not upgrade.
  - The copy-test found the real defects (registry clobber CRITICAL, junk profile, skill edits,
    HOME collision, scaffold clutter). Fixed all; --force is the only way to scaffold a foreign vault.
Pending resolved:
  - "Correct upgrade's negative outcomes so it's safe on an existing vault" — done (A).
  - "wsx thin adapter as a map for the future" — done (B).
  - "Help me create a profile + interactive voice/tone that adjusts all LLMs" — prefs captured +
    generator mechanism built. (Full `wsx profile init` from-context flow still TODO.)
Next:
  - Optional: `wsx adapter ~/Projects/Workspace` to run wsx read-only tooling on the real vault
    (drops a .wsx/ into the repo — Sean's call). Build `wsx profile init` (reconstruct a full
    profile from existing context). Colleague/Olga re-test of v0.2 + the adapter path.
--- END BLOCK ---
