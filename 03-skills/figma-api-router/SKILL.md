---
name: figma-api-router
description: >
  Decision matrix for choosing the right Figma API surface (Plugin API, REST API, or MCP server) for automation, AI-agent workflows, or programmatic design-system generation; also for debugging API access issues.
aliases: [figma-api-router]
tier: spoke
domain: design
hub: figma
prerequisites: [figma]
spec_version: "2.0"
triggers: [figma rest api, figma api surface, plugin api or rest, which figma api]
---

# Figma API Router

**Trigger**: Use this skill whenever you need to decide which Figma API surface to use, when working with Figma automation, AI-agent workflows, or programmatic design system generation. Also trigger when debugging API access issues or when the user mentions Figma in the context of automation, plugin development, or external integrations.

---

## API Surface Decision Matrix

Figma exposes three distinct API surfaces with different capabilities, execution contexts, and trade-offs. Use this decision matrix to route to the correct API:

| Need | MCP Server (`use_figma`) | Plugin API | REST API |
|------|-------------------------|-------------|-----------|
| **AI agent workflows** | ✅ Primary choice | ❌ Not accessible | ⚠️ Limited writes |
| **Real-time design creation** | ✅ Via `use_figma` | ✅ Direct access | ❌ Read-only design |
| **Cross-file operations** | ⚠️ One file per call | ❌ Current file only | ✅ Any accessible file |
| **CI/CD token syncing** | ❌ Session-dependent | ❌ Editor-dependent | ✅ HTTP-based |
| **Bulk variable operations** | ⚠️ 50K char limit per call | ⚠️ Loop through API | ✅ Atomic bulk (Enterprise) |
| **Component/variant creation** | ✅ Via `use_figma` | ✅ Direct | ❌ Not supported |
| **Style generation** | ✅ Via `use_figma` | ✅ Direct | ❌ Not supported |

### When to Use MCP Server (use_figma tool)

**✅ Use MCP Server When:**
- AI agent needs to create or modify design elements
- Automating design-to-code workflows  
- Generating design system components programmatically
- Building agentic design workflows
- Need full Plugin API access from external context
- User mentions "generate", "create", "automate" with Figma

**🔧 Technical Details:**
- Execution: AI agent → MCP protocol → Plugin API JavaScript
- Code limit: 50,000 characters per call — over that, split the work across several `use_figma` calls, or move bulk variable work to the REST API (Enterprise)
- Response limit: ~20KB output
- Write tools rate-limit exempt during beta
- Authentication: OAuth 2.0 (remote) or desktop session (local)

**📍 File Scope:**
- Remote server: Any file via URL, one file per call (cross-file work = one call per file)
- Desktop server: Current open file only
- Figma must be open for desktop mode

### When to Use Plugin API Directly

**✅ Use Plugin API When:**
- Building Figma plugins (.ts/.js files)
- Real-time in-editor automation
- Interactive user interfaces in Figma
- Complex multi-step workflows requiring user input
- Performance-critical operations

**🔧 Technical Details:**
- Execution: Inside Figma editor sandbox
- Access: Full read/write to current file only
- Authentication: User session (no tokens required)
- Rate limits: None
- Variables: Full CRUD operations

### When to Use REST API

**✅ Use REST API When:**
- CI/CD pipelines and external automation
- Cross-file operations across many files
- Token synchronization with external systems
- Building external applications that read Figma data
- Figma doesn't need to be open
- Need Enterprise-only variable write operations

**🔧 Technical Details:**
- Execution: External HTTP calls to api.figma.com
- Authentication: PAT via X-FIGMA-TOKEN header or OAuth Bearer token
- Scope: Read-only for design data; write for variables (Enterprise), comments, dev resources
- Rate limits: Tiered by plan and endpoint type

---

## Critical API Routing Decisions

### Design System Generation
```
SCENARIO: "Generate a design system with variables and components"
→ ROUTE: MCP Server (use_figma tool)
→ REASON: Requires variable creation + style creation + component generation
→ ALTERNATIVE: Plugin API if building interactive plugin interface
```

### Token Synchronization
```
SCENARIO: "Sync design tokens between Figma and codebase"
→ ROUTE: REST API for reads, Plugin API/MCP for writes (non-Enterprise)
→ REASON: External system integration, may not have Figma open
→ ENTERPRISE: REST API for both reads and writes
```

### Interactive Plugin Development
```
SCENARIO: "Build a plugin with UI for designers to configure variables"
→ ROUTE: Plugin API directly
→ REASON: Requires real-time user interaction and UI rendering
→ DEPLOYMENT: Package as .figma plugin file
```

### AI-Powered Design Generation
```
SCENARIO: "AI agent creates components based on specifications"
→ ROUTE: MCP Server (use_figma tool)
→ REASON: External AI context, programmatic generation, no user interaction
→ AUTHENTICATION: OAuth 2.0 for remote, desktop session for local
```

---

## MCP Tool Selection

**For reads:** `get_design_context` (structured code + design context for a node), `get_metadata` (node overview), `get_variable_defs` (token extraction), `get_screenshot` (visuals).

**Before writes:** `search_design_system` — check the connected libraries for an existing component, variable, or style before creating a new one.

**For writes:** `use_figma` (Plugin API JavaScript), `create_new_file` (new files).

---

## Authentication Decision Tree

### For MCP Server
- **Remote Mode**: OAuth 2.0 required (no Figma app needed)
- **Desktop Mode**: Figma Desktop App + Dev Mode enabled
- **File Access**: Remote = any URL, Desktop = current file only

### For Plugin API
- **Authentication**: Automatic via user session
- **Access**: Current file only
- **Distribution**: Figma Community or private installation

### For REST API
- **Personal Access Token**: 90-day max expiry, full account access
- **OAuth 2.0**: Granular scopes, longer-lived tokens
- **Enterprise Features**: Variable writes require Enterprise plan

---

## File Access Patterns

- **Local file (`localFileKey=...`)**: Desktop MCP server only — no other surface can reach it
- **Cloud file (`figma.com/design/<fileKey>/...`)**: Any API surface works
- **Branch file (`figma.com/design/<fileKey>/branch/<branchKey>/...`)**: Use the `branchKey` as the `fileKey`

---

## Rate Limit Considerations

| API Surface | Limits | Write Operations |
|------------|---------|------------------|
| MCP Server | Tier 1 REST limits for reads | Rate-limit exempt (beta) |
| Plugin API | None | Unlimited |
| REST API | 10-150/min by plan tier | Standard rate limits |

### Rate Limit Tiers (REST API)
- **Tier 1**: GET files, nodes, images (10-20/min)
- **Tier 2**: Variables, webhooks (25-100/min)  
- **Tier 3**: POST variables, metadata (50-150/min)

*Limits scale with plan: Professional < Organization < Enterprise*

### Rate Limit Warning Signs
- **429 Too Many Requests**: Wait the number of seconds in the `Retry-After` header, then resend. For writes, moving the job to MCP `use_figma` also avoids the limit (writes are exempt during beta); MCP reads still count against Tier 1 limits, so switching surfaces does not help a read-heavy job.
- **Limit lower than expected**: Three things set it — the requester's seat type (Dev/Full seats get more than View/Collab), the endpoint's tier, and the plan of the file being requested. A file in a lower-plan workspace gets that plan's limits even when the requesting user sits on a higher plan. The 429 response's `X-Figma-Plan-Tier` and `X-Figma-Rate-Limit-Type` headers say which limit hit.
- **403 "Limited by Figma plan" / "Incorrect account type"**: The Variables REST endpoints need a full member of an Enterprise org (POST also needs edit access to the file).

---

## Size Limits

| Surface | Limit | Over the limit |
|---|---|---|
| MCP `use_figma` code | 50,000 characters per call | Split into several calls, or REST bulk (Enterprise) |
| MCP response | ~20KB output | Narrow the read (one node, `get_metadata` first) |
| REST Variables bulk (`POST /v1/files/:key/variables`) | 4MB request body | 413 error — split the payload |

---

## Quick Reference Commands

### MCP Server
```javascript
// Essential read pattern
const metadata = await tools.get_metadata(fileKey);
const context = await tools.get_design_context(fileKey, nodeId);

// Essential write pattern  
await tools.use_figma({
  fileKey,
  code: `/* Plugin API JavaScript */`,
  description: "Clear description of operation"
});
```

### Plugin API
```javascript
// Essential variable pattern
const collection = figma.variables.createVariableCollection(name);
const variable = figma.variables.createVariable(name, collection, type);

// Essential immutability pattern
const newFills = [...node.fills];
newFills[0] = figma.variables.setBoundVariableForPaint(newFills[0], 'color', variable);
node.fills = newFills;
```

### REST API
```bash
# Essential read pattern
curl -H "X-FIGMA-TOKEN: $TOKEN" \
  https://api.figma.com/v1/files/$FILE_KEY/variables/local

# Essential write pattern (Enterprise)
curl -X POST -H "X-FIGMA-TOKEN: $TOKEN" \
  -H "Content-Type: application/json" \
  https://api.figma.com/v1/files/$FILE_KEY/variables
```

---

This skill ensures correct API surface selection and prevents common routing mistakes that lead to authentication errors, scope limitations, and feature availability issues.

## Related
- hub → [[figma]]
