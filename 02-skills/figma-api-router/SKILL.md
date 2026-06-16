# Figma API Router

**Trigger**: Use this skill whenever you need to decide which Figma API surface to use, when working with Figma automation, AI-agent workflows, or programmatic design system generation. Also trigger when debugging API access issues or when the user mentions Figma in the context of automation, plugin development, or external integrations.

---

## API Surface Decision Matrix

Figma exposes three distinct API surfaces with different capabilities, execution contexts, and trade-offs. Use this decision matrix to route to the correct API:

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
- Code limit: 50,000 characters per call
- Response limit: ~20KB output
- Write tools rate-limit exempt during beta
- Authentication: OAuth 2.0 (remote) or desktop session (local)

**📍 File Scope:**
- Remote server: Any file via URL
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