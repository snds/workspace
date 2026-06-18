---
tags: [claude-code, skills, plugins, slash-commands, workspace-infra]
created: 2026-06-02
updated: 2026-06-02
status: stable
confidence: high
sources: [session-log 2026-06-02]
related_skills: [cowork-skills-sync, workspace-bootstrap]
related_projects: [Claude Workspace Infrastructure]
---

# Claude Code: skills vs. slash commands, and how to expose a skills dir in the `/` menu

## The core distinction

Two things look the same but aren't:

- **Available to the model** — every skill the harness knows about (from `~/.claude/skills/`,
  project `.claude/skills/`, plugins, and managed/cloud bundles) is loaded as a description
  and invocable by Claude via the **Skill tool**. Appears in the system prompt's skill list.
- **Shown in the `/` autocomplete menu** — only **locally-installed** skills/commands surface
  for the user to type: project `.claude/skills/`, personal `~/.claude/skills/`, and skills
  from installed plugins. Cloud/managed bundles do **not** populate the menu.

A skill can therefore be fully usable by Claude yet invisible when you type `/`.

## Why Sean's `anthropic-skills:*` were absent from the menu

The `anthropic-skills:`-namespaced skills (workspace-bootstrap, ds-advisor, design-engineer,
the lead-*/project hubs, etc.) are the **Cowork managed bundle**: `03-skills/` copied into the
Cowork VM's skills-plugin dir by `cowork-skills-sync` (copy, not symlink — the VM can't follow
Drive symlinks). They have **no install footprint** under `~/.claude/plugins` and aren't a
registered marketplace, so they're model-only — never in the local `/` menu.

## How to make a directory of skills into typeable slash commands

A **plugin** reads skills only from its own `skills/<name>/SKILL.md` subdir. `plugin.json` has
**no custom-skills-path field** — so you can't point a plugin at an arbitrary dir in place;
the skills must physically live under `skills/`.

Minimum viable local plugin + marketplace:

```
<root>/                              # marketplace root, added via `marketplace add <path>`
├── .claude-plugin/marketplace.json  # name, owner, plugins:[{name, source:"./<plugin>"}]
└── <plugin>/
    ├── .claude-plugin/plugin.json   # name → becomes the command prefix /<name>:<skill>
    └── skills/<skill>/SKILL.md      # copied skills (+ supporting files)
```

Register (once per machine; **restart required** to surface in the menu):

```bash
claude plugin validate <root>
claude plugin marketplace add <root>      # writes extraKnownMarketplaces (directory source)
claude plugin install <plugin>@<market>   # writes enabledPlugins; user scope by default
```

Commands then appear namespaced as `/<plugin>:<skill>`.

## Gotchas

- **Keep the plugin OUTSIDE the workspace checkout** (`~/.claude/local-plugins/...`). `~/.claude`
  is machine-local and not version-controlled; committing duplicate skill copies into the vault
  invites drift. Generate a copy-mirror per machine instead and keep the source dir canonical.
- **`~/.claude` isn't version-controlled** — only the generator script ships via the workspace repo.
  Each machine must run the generator + the two `claude plugin` commands itself.
- **Plugin/menu changes need a Claude Code restart** to take effect.
- **Don't flood the menu** — wrap only operational *hub* entry points, not spoke/reference
  skills (those stay model-invoked).

## Reference implementation

`08-tools/build-local-skill-plugin.py` — config-driven (`HUBS` list), clean-rebuild mirror
of curated `03-skills/` hubs into `~/.claude/local-plugins/snds-local` → `/snds:<name>`.
Same copy-not-symlink approach as `cowork-skills-sync`, targeting local CC instead of the VM.
