---
name: figma-code-connect
description: >
  Author and maintain Figma Code Connect — the mapping that makes Dev Mode show *your* real component
  code (props, imports, variants) instead of generic CSS for a selected node. Write/refresh `.figma.ts`
  templates, map Figma properties to code props, and keep the mapping in sync as components evolve. Use
  when wiring a design system's components to their code in Dev Mode. Triggers: code connect, figma.ts,
  component mapping, dev mode code, map figma props, connect component, figma code connect.
aliases: [figma-code-connect, code-connect]
triggers: [code connect, figma.ts, component mapping, dev mode code, map figma props, connect component, figma code connect, publish code connect]
tier: spoke
hub: figma
domain: design
prerequisites: [figma]
requires: [figma-mcp]
spec_version: "2.1"
---

# Figma — Code Connect

Make Dev Mode hand off the *right* code: bind each design-system component in Figma to its real
implementation so engineers see your `Button` with its actual props, not a wall of generated CSS. This is
a design-system governance task as much as a Figma one — the source of truth for which prop maps to which
variant is the code's API ([[design-engineer]], [[ds-advisor]]).

> **Tool dependency — preflight first.** Requires the `figma-mcp` capability ([[capability-registry]]).
> Confirm a `mcp__*figma*__*` tool (Code Connect surface) is available; if not, **degrade** — you can still
> hand-author `.figma.ts` from the component API, but you can't introspect/publish without it. See
> [[AGENTS]] → "Capability preflight".

## What good mapping looks like
- **The code's prop interface is authoritative** — enumerate the component's real props first, then map each
  Figma property to one (direct name match, value transform, or `INSTANCE_SWAP`). If no code prop fits a
  Figma property, **omit it** — don't invent a prop to force a 1:1.
- **One component, one template** — keep `.figma.ts` next to the component; variants/states resolve through
  the prop mapping, not duplicate files.
- **Sync is ongoing** — when the component API changes, the mapping drifts silently; re-check on DS releases.

## Defers to
The exact `.figma.ts` template grammar + publish flow live in the installed **Figma Dev Mode / Code Connect**
skill + MCP; this skill is the workspace *when/why* and DS-correctness discipline. Pairs with
[[figma-design-to-code]] (one-off implementation) — Code Connect is the *durable* component-level mapping.

## Related
- hub → [[figma]]
- peer ↔ [[figma-design-to-code]]
