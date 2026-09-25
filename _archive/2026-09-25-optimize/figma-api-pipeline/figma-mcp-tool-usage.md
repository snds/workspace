# Figma MCP Tool Usage

## When to Use This Skill
Use when working with Figma MCP server tools for AI-driven design workflows. This skill covers proper tool selection, parameters, and usage patterns for all Figma MCP tools.

## MCP Server Connection
- **Remote**: `https://mcp.figma.com/mcp` (OAuth 2.0, no desktop app needed)
- **Desktop**: `http://127.0.0.1:3845/mcp` (requires Figma Desktop + Dev Mode)

## Core Read Tools

### `whoami` - Authentication and Plan Info
**Use when**: Need to check authentication, get plan details, or find planKey for file creation
```javascript
const userInfo = await whoami()
// Returns: email, handle, plans array with keys and tiers
// Use plans[0].key as planKey for create_new_file
```

### `get_design_context` - Primary Design Extraction Tool
**Use when**: Need structured code representation, asset URLs, or screenshots of designs
**Limits**: ~20KB response, works best on focused nodes (not massive frames)

**Parameters**:
- `fileKey`: File ID from URL (required)
- `nodeId`: Specific node to extract (optional, defaults to root)
- `includeImagesOfNodes`: Boolean (optional, defaults to true)

**Best practices**:
- Use `get_metadata` first for large designs to identify target nodes
- Target specific components/frames, not entire pages
- Returns React + Tailwind by default
- Includes downloadable asset URLs

### `get_metadata` - Sparse Node Overview
**Use when**: Need to understand file structure before detailed extraction
**Perfect for**: Large files where `get_design_context` might timeout

**Returns**: XML-like structure with node IDs, types, names, and positions
**Pattern**: Metadata first → target specific nodes → detailed extraction

### `get_variable_defs` - Token Extraction
**Use when**: Need to extract design tokens/variables from a node
**Returns**: Object mapping like `{'icon/default/secondary': '#949494'}`
**Use case**: Building token systems, style guides, or documentation

### `get_screenshot` - Visual Capture
**Use when**: Need visual representation without code generation
**Faster than**: `get_design_context` when only image needed
**Returns**: Base64 image or image URL

## Core Write Tools

### `use_figma` - Primary Design Creation Tool
**Use when**: Creating, modifying, or deleting any Figma content
**Limits**: 50,000 characters max code, ~20KB response

**Critical parameters**:
- `code`: JavaScript Plugin API code (required)
- `description`: What the code does (required, helps debugging)
- `fileKey`: Target file (required)
- `skillNames`: Comma-separated skill names (optional, for logging)

**Pre-execution pattern**:
```javascript
// 1. Check existing design system
await searchDesignSystem(fileKey, 'buttons color tokens')

// 2. Then create new content
await useFigma({
  fileKey,
  description: 'Create color token system with semantic variables',
  code: `/* Your Plugin API JavaScript */`
})
```

### `search_design_system` - Check Before Create
**Use when**: Before creating components, variables, or styles
**Purpose**: Avoid duplicating existing design system elements
**Returns**: Existing components, variables, styles from connected libraries

**Always call before**:
- Creating new components
- Setting up variable systems  
- Building style libraries
- Any systematic design generation

### `create_new_file` - File Creation
**Use when**: Need a new file for design system work
**Requires**: `planKey` from `whoami` tool

```javascript
// Get planKey first
const user = await whoami()
const planKey = user.plans[0].key

// Create file
await createNewFile({
  editorType: 'design', // or 'figjam'
  fileName: 'Design System Tokens',
  planKey: planKey
})
```

## Specialized Tools

### `generate_diagram` - FigJam Diagrams
**Use when**: Creating flowcharts, system diagrams, or documentation
**Input**: Mermaid.js syntax
**Output**: FigJam diagram
**Supported**: Flowcharts, sequence diagrams, Gantt charts

### `get_code_connect_map` - Code Mappings
**Use when**: Working with Code Connect integrations
**Returns**: Mappings between Figma nodes and codebase components

### `get_figjam` - FigJam Content
**Use when**: Extracting content from FigJam files specifically
**Similar to**: `get_design_context` but for whiteboard content

## Tool Selection Decision Tree

### For Reading Designs:
1. **Large file/unknown structure**: Start with `get_metadata`
2. **Need code representation**: Use `get_design_context` on specific nodes
3. **Need design tokens**: Use `get_variable_defs`
4. **Need visual only**: Use `get_screenshot`
5. **Need file overview**: Use `get_metadata` on root node

### For Writing Designs:
1. **Always start with**: `search_design_system` (check existing)
2. **Then use**: `use_figma` for creation/modification
3. **For new projects**: `create_new_file` first

### For FigJam:
1. **Diagram creation**: `generate_diagram` with Mermaid syntax
2. **Content extraction**: `get_figjam`

## Rate Limits and Performance

### Rate Limits (by plan tier)
- **Tier 1** (reads): 10-20 calls/minute depending on plan
- **Tier 2** (metadata): 25-100 calls/minute  
- **Write tools**: Currently exempt during beta

### Performance Optimization
```javascript
// ❌ WRONG - requesting massive frame
await getDesignContext(fileKey, 'huge-page-id')

// ✅ CORRECT - metadata first, then targets
const metadata = await getMetadata(fileKey, 'huge-page-id')
const components = metadata.children.filter(child => child.type === 'COMPONENT')

for (const comp of components.slice(0, 3)) {
  const design = await getDesignContext(fileKey, comp.id)
  // Process each component individually
}
```

### Batch Operations Pattern
```javascript
// Process large operations in chunks
const chunks = chunkArray(allNodes, 5) // 5 nodes per chunk

for (const chunk of chunks) {
  const chunkCode = `
    ${chunk.map(node => generateNodeCode(node)).join('\n')}
  `
  
  await useFigma({
    fileKey,
    description: `Process chunk of ${chunk.length} nodes`,
    code: chunkCode
  })
  
  // Brief delay to respect rate limits
  await new Promise(resolve => setTimeout(resolve, 1000))
}
```

## Error Handling Patterns

### File Access Issues
```javascript
// Check file access first
try {
  const userInfo = await whoami()
  console.log('Authenticated as:', userInfo.email)
  
  const metadata = await getMetadata(fileKey, '0:1')
  console.log('File accessible:', metadata.name)
} catch (error) {
  console.error('Access issue:', error.message)
  // Handle authentication or permission errors
}
```

### Code Size Limits
```javascript
// Check code length before sending
const code = generateLargeScript()

if (code.length > 45000) { // Leave buffer
  console.warn('Code too large, splitting into chunks')
  const chunks = splitCodeIntoChunks(code, 40000)
  
  for (const chunk of chunks) {
    await useFigma({ fileKey, description: 'Chunk execution', code: chunk })
  }
} else {
  await useFigma({ fileKey, description: 'Full execution', code })
}
```

### Response Size Handling
```javascript
// For large responses, target specific data
const targetNodeIds = ['123:456', '789:012'] // Specific nodes only

for (const nodeId of targetNodeIds) {
  try {
    const design = await getDesignContext(fileKey, nodeId)
    processDesign(design)
  } catch (error) {
    console.error(`Failed to get design for ${nodeId}:`, error)
    // Continue with other nodes
  }
}
```

## Common Usage Patterns

### Design System Generation Workflow
```javascript
// 1. Check authentication and get planKey
const user = await whoami()
const planKey = user.plans[0].key

// 2. Create new file or use existing
const newFile = await createNewFile({
  editorType: 'design',
  fileName: 'Token System',
  planKey
})
const fileKey = newFile.file_key

// 3. Check for existing design system
const existing = await searchDesignSystem(fileKey, 'color variables spacing')

// 4. Generate system if not exists
if (!existing.variables?.length) {
  await useFigma({
    fileKey,
    description: 'Generate complete color token system',
    code: generateColorTokensCode()
  })
}
```

### Component Library Audit
```javascript
// 1. Get file structure
const metadata = await getMetadata(fileKey, '0:1')

// 2. Find all components
const components = findNodesRecursive(metadata, node => node.type === 'COMPONENT')

// 3. Extract each component's design context
const componentData = []
for (const comp of components) {
  try {
    const design = await getDesignContext(fileKey, comp.id)
    componentData.push({ id: comp.id, name: comp.name, design })
  } catch (error) {
    console.warn(`Skipped ${comp.name}:`, error.message)
  }
}

// 4. Analyze and report
generateComponentAuditReport(componentData)
```

### Token Synchronization
```javascript
// 1. Extract current tokens
const currentTokens = await getVariableDefs(fileKey, 'token-source-node')

// 2. Compare with external system
const externalTokens = await fetchExternalTokens()
const diff = compareTokenSets(currentTokens, externalTokens)

// 3. Update if differences found
if (diff.hasChanges) {
  await useFigma({
    fileKey,
    description: 'Sync tokens with external system',
    code: generateTokenUpdateCode(diff)
  })
}
```

## Tool Selection Checklist

- [ ] Use `get_metadata` first for unknown/large files
- [ ] Use `search_design_system` before creating components/variables
- [ ] Use `get_design_context` on focused nodes, not entire pages
- [ ] Use `use_figma` for all creation/modification operations
- [ ] Check code length limits before `use_figma` calls
- [ ] Implement retry logic for rate-limited operations
- [ ] Use `whoami` to get planKey before creating files
- [ ] Target specific nodes rather than processing everything at once
