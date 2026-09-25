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
