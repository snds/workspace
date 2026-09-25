# Figma API Router

## When to Use This Skill
Use whenever you need to interact with Figma programmatically. This skill determines the correct API surface (MCP server, Plugin API, or REST API) based on the task requirements.

## The Three API Decision Matrix

| Need | MCP Server (`use_figma`) | Plugin API | REST API |
|------|-------------------------|-------------|-----------|
| **AI agent workflows** | ✅ Primary choice | ❌ Not accessible | ⚠️ Limited writes |
| **Real-time design creation** | ✅ Via use_figma tool | ✅ Direct access | ❌ Read-only design |
| **Cross-file operations** | ⚠️ One file per call | ❌ Current file only | ✅ Any accessible file |
| **CI/CD token syncing** | ❌ Session-dependent | ❌ Editor-dependent | ✅ HTTP-based |
| **Bulk variable operations** | ⚠️ 50K char limit | ⚠️ Loop through API | ✅ Atomic bulk (Enterprise) |
| **Component/variant creation** | ✅ Via use_figma | ✅ Direct | ❌ Not supported |
| **Style generation** | ✅ Via use_figma | ✅ Direct | ❌ Not supported |

## Critical Decision Rules

### Use MCP Server When:
- AI agent is driving the workflow
- Need to create/modify design elements
- Working within file scope acceptable
- 50K character code limit is sufficient
- Rate limits not a concern (writes exempt during beta)

### Use Plugin API When:
- Building a Figma plugin
- Need real-time editor interaction
- MCP server executes your code via `use_figma`

### Use REST API When:
- External system integration (CI/CD, token sync)
- Need to read across many files
- Enterprise bulk variable operations required
- Figma doesn't need to be open

## MCP Tool Selection

**For reads**: `get_design_context` (structured code), `get_metadata` (node overview), `get_variable_defs` (token extraction), `get_screenshot` (visuals)

**For writes**: `use_figma` (Plugin API JavaScript), `search_design_system` (check existing), `create_new_file` (new files)

## Authentication Quick Reference

- **MCP**: OAuth 2.0 (remote) or desktop session (local)
- **Plugin API**: User session (no auth needed)
- **REST**: PAT via `X-FIGMA-TOKEN` or OAuth `Bearer` token

## Rate Limit Warning Signs

- **429 Too Many Requests**: Switch to MCP or wait for reset
- **Tier exceeded**: Check file's plan vs user's plan (file wins)
- **Enterprise features needed**: Variables REST endpoints require Enterprise

## File Access Patterns

- **Local file (localFileKey=...)**: Use desktop MCP server only
- **Cloud file (figma.com/design/ABC123)**: Any API works
- **Branch file**: Use branchKey as fileKey

## Code Size Limits

- **MCP use_figma**: 50,000 characters max
- **MCP response**: ~20KB output limit
- **REST Variables bulk**: 4MB request limit

When MCP code exceeds 50K, break into multiple `use_figma` calls or switch to REST API for bulk operations.
