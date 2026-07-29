---
tags: [context, open-engine, agent-ops]
created: 2026-07-29
status: active
aliases: [open-engine-lanes, lane-index]
---

# Open Agent Engine — lane index

The runtime lookup for [[open-agent-engine]]. The skill holds the **procedure**; each lane config
below holds the **instance facts** (tracker workspace, agent codes, ledger id, context profile).
Resolve a lane here first; never hard-code an instance into the skill.

Engine version: **v1**

| Lane | Config | Tracked | Profile | Movement-only |
|---|---|---|---|---|
| `personal` | [personal.md](personal.md) | ✅ in git | `personal-solo` | no |
| `c8` | `07-projects/02-centricPLM/open-engine.local.md` | ❌ machine-local | `centric-engineering` | **yes** |

## Machine expectations (canonical)

Which lanes each machine is *supposed* to have. Declared, never inferred — a machine missing from
this table is itself a finding. The fenced `json` block is canonical and machine-read by
`00-bootstrap/doctor/linear-lanes.py`; the table above is the human mirror. Keep them in sync.

| Machine (hostname) | Label | Expected lanes |
|---|---|---|
| `CS-K746DRWXY1` | Work MacBook Pro (main) | `personal`, `c8` |
| `CS-KQ23N94M0W` | Work MacBook Pro (loaner) | `personal`, `c8` |
| `Voyager-2.local` | Personal MacBook Pro | `personal` |
| `Enterprise` | Windows Desktop | `personal` |

A lane registered on a machine that does **not** expect it is drift in the dangerous direction — it
means an employer connection exists on a personal device, or vice versa. The detector reports that as
`unexpected`, not as a pass.

```json
{
  "spec_version": "1.0",
  "lanes": {
    "personal": {
      "config": "06-context/open-engine/personal.md",
      "tracked": true,
      "mcp_server": "linear-personal",
      "auth_dir": "~/.mcp-auth/linear-personal",
      "profile": "personal-solo",
      "movement_only": false
    },
    "c8": {
      "config": "07-projects/02-centricPLM/open-engine.local.md",
      "tracked": false,
      "mcp_server": "linear-c8",
      "auth_dir": "~/.mcp-auth/linear-c8",
      "profile": "centric-engineering",
      "movement_only": true
    }
  },
  "machines": {
    "CS-K746DRWXY1": ["personal", "c8"],
    "CS-KQ23N94M0W": ["personal", "c8"],
    "Voyager-2.local": ["personal"],
    "Enterprise": ["personal"]
  }
}
```

## Why the c8 config is not in git

It names employer entities (team, project, issue ids). The standing wall in [[CRITICAL_FACTS]] keeps
employer content out of this repo, and `.gitignore` enforces it — `07-projects/` is deny-by-default,
so only `00-obsidian`, `18-bootstrap-generator`, and `19-workspace-brain` are tracked. The c8 config
still lives *in the workspace tree*: same conventions, same skill reads it, visible in Obsidian.
**Governed by the workspace ≠ committed to the workspace.**

Because it is machine-local, it must be recreated per machine. Treat that as a feature — a machine
that has not been deliberately set up cannot run the employer lane.

## Lane isolation

Each lane binds to its own tracker workspace with its own MCP auth context. Linear scopes one MCP
connection to one workspace, so a runner authed to `personal` **cannot see** `c8`, and vice versa.
That isolation is structural, not a rule the agent is trusted to follow. See [[capability-registry]]
→ `linear-mcp`.

If a lane is not named in the invocation and more than one is configured, **ask** — never guess.

## Adding a lane

1. Decide whether its facts may be committed. If they name an employer, a client, or anything under
   a profile stricter than `personal-solo`, they may not — put the config beside the project it
   serves as `open-engine.local.md`.
2. Copy the shape of [personal.md](personal.md); fill every field or mark it `PENDING`.
3. Register the lane in the table above.
4. Add the MCP connection for that tracker workspace with its own auth context.
5. Run the three smoke tests (hello-world, blocked-resume, human-hold) before the lane is trusted.
   For a movement-only lane, also run the substance-refusal test.

## Related
- skill → [[open-agent-engine]]
- profiles → [00-context-profiles](../../02-shared-references/delivery-playbooks/00-context-profiles.md)
