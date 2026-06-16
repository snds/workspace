---
name: figma-error-troubleshooting
description: >
  Identifying and resolving errors across the Figma Plugin API, MCP server, and REST API.
aliases: [figma-error-troubleshooting]
tier: spoke
domain: design
hub: figma
prerequisites: [figma]
spec_version: "2.0"
---

# Figma API Error Troubleshooting

## When to Use This Skill
Use when encountering errors in Figma Plugin API, MCP server, or REST API operations. This skill provides precise error identification and resolution patterns.

## Font and Text Errors

### "Cannot write to node with unloaded font"
**Cause**: Attempting to modify text properties before loading the font
**Fix**: Always load fonts before ANY text property modification
```javascript
// ❌ WRONG
textNode.characters = 'New text' // Error!

// ✅ CORRECT
await figma.loadFontAsync({ family: 'Inter', style: 'Regular' })
textNode.characters = 'New text' // Works!
```

**Load current font**: You must load the font currently applied to the text node, not just the new font
```javascript
// Get current font first
const currentFont = textNode.fontName
await figma.loadFontAsync(currentFont)
// Now safe to modify
textNode.fontName = { family: 'Inter', style: 'Bold' }
```

### "Font not found: [font name]"
**Cause**: Incorrect font family or style name
**Fix**: Check exact font names available in Figma
```javascript
// Check available fonts
console.log('Available fonts:', await figma.listAvailableFontsAsync())

// Use exact names from Figma
await figma.loadFontAsync({ family: 'SF Pro Display', style: 'Semibold' })
```

## Variable and Scope Errors

### "If ALL_FILLS is set, other fill scopes cannot be set"
**Cause**: Mixing `ALL_FILLS` with specific fill scopes
**Fix**: Use mutually exclusive scopes
```javascript
// ❌ WRONG
variable.scopes = ['ALL_FILLS', 'STROKE_COLOR'] // Error!

// ✅ CORRECT options
variable.scopes = ['ALL_FILLS'] // Only ALL_FILLS
variable.scopes = ['FRAME_FILL', 'SHAPE_FILL', 'STROKE_COLOR'] // Specific scopes
```

### "Limited to N modes only"
**Cause**: Exceeding plan mode limits
**Fix**: Check plan limits before adding modes
```javascript
const planLimits = { starter: 1, professional: 10, organization: 20, enterprise: 40 }

// Check before adding
if (collection.modes.length >= planLimits[currentPlan]) {
  console.error(`Cannot add mode: ${currentPlan} plan limited to ${planLimits[currentPlan]} modes`)
  return
}
collection.addMode('Dark')
```

### "Cannot create extended collections outside of enterprise plan"  
**Cause**: Using `.extend()` method without Enterprise plan
**Fix**: Use standard collections or upgrade to Enterprise
```javascript
// ❌ WRONG on non-Enterprise
const extendedCollection = collection.extend() 

// ✅ CORRECT - use standard collections
const newCollection = figma.variables.createVariableCollection('New Collection')
```

## Immutability and Binding Errors

### "Property 'fills' failed validation"
**Cause**: Invalid paint type in fills array (e.g., pattern, video fills)
**Fix**: Filter out unsupported paint types
```javascript
// Filter supported paint types
const validFills = node.fills.filter(fill => 
  fill.type === 'SOLID' || 
  fill.type === 'GRADIENT_LINEAR' || 
  fill.type === 'GRADIENT_RADIAL'
)
node.fills = validFills
```

### Variable binding silently fails
**Cause**: Not capturing `setBoundVariableForPaint` return value
**Fix**: Always capture and reassign
```javascript
// ❌ WRONG - ignoring return value
figma.variables.setBoundVariableForPaint(fillsCopy[0], 'color', variable)

// ✅ CORRECT - capture return value
const fillsCopy = [...node.fills]
fillsCopy[0] = figma.variables.setBoundVariableForPaint(fillsCopy[0], 'color', variable)
node.fills = fillsCopy
```

### "TypeError: Cannot assign to read only property"
**Cause**: Attempting to mutate readonly arrays directly  
**Fix**: Clone → modify → reassign pattern
```javascript
// ❌ WRONG
node.fills[0] = newPaint // Error: readonly!

// ✅ CORRECT  
const fillsCopy = [...node.fills] // Clone
fillsCopy[0] = newPaint // Modify copy
node.fills = fillsCopy // Reassign
```

## Layout and Auto-Layout Errors

### "Can only set maxHeight on auto layout nodes"
**Cause**: Setting min/max properties on non-auto-layout nodes
**Fix**: Enable auto-layout first
```javascript
// ❌ WRONG
frame.minHeight = 100 // Error if no layoutMode!

// ✅ CORRECT
frame.layoutMode = 'VERTICAL' // Enable auto-layout first
frame.minHeight = 100 // Now works
```

### "Cannot set itemSpacing on non-auto-layout node"
**Cause**: Setting auto-layout properties without enabling auto-layout
**Fix**: Set `layoutMode` before auto-layout properties
```javascript
// ✅ CORRECT order
frame.layoutMode = 'HORIZONTAL' // First: enable auto-layout
frame.itemSpacing = 16 // Then: set spacing
frame.paddingTop = 12 // Then: set padding
```

## Component and Variant Errors

### "Cannot combine variants: components must be on the same page"
**Cause**: Components on different pages
**Fix**: Move all components to same page before combining
```javascript
// Move all variants to current page
variants.forEach(variant => {
  figma.currentPage.appendChild(variant)
})

// Then combine
const componentSet = figma.combineAsVariants(variants, figma.currentPage)
```

### Variants don't parse properties correctly
**Cause**: Incorrect variant naming format
**Fix**: Use exact `Property=Value, Property=Value` format
```javascript
// ❌ WRONG formats
component.name = 'Size: Large, State: Default' // Wrong separator
component.name = 'Size=Large,State=Default'    // Missing space
component.name = 'size=large'                  // Wrong case

// ✅ CORRECT format
component.name = 'Size=Large, State=Default'   // Comma + space
```

## MCP Server Errors

### "Tool call exceeded maximum length"
**Cause**: `use_figma` code exceeds 50,000 character limit
**Fix**: Break into smaller chunks or use REST API for bulk operations
```javascript
// Split large operations
const chunkSize = 20 // Process 20 variables at a time

for (let i = 0; i < allVariables.length; i += chunkSize) {
  const chunk = allVariables.slice(i, i + chunkSize)
  
  await useFigmaChunk(chunk) // Separate use_figma call per chunk
}
```

### MCP timeout on large operations
**Cause**: Processing too much data in single `get_design_context` call
**Fix**: Use `get_metadata` first, then target specific nodes
```javascript
// ❌ WRONG - requesting huge frame
await getDesignContext(fileKey, 'massive-frame-id')

// ✅ CORRECT - metadata first, then specifics
const metadata = await getMetadata(fileKey, 'massive-frame-id')
const targetNodes = metadata.children.filter(child => child.type === 'COMPONENT')

for (const node of targetNodes.slice(0, 5)) { // Process few at a time
  const design = await getDesignContext(fileKey, node.id)
}
```

## REST API Errors

### "429 Too Many Requests"
**Cause**: Rate limit exceeded
**Fix**: Implement exponential backoff with `Retry-After` header
```javascript
async function apiCallWithRetry(url, options, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    const response = await fetch(url, options)
    
    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After')
      const delay = retryAfter ? parseInt(retryAfter) * 1000 : Math.pow(2, attempt) * 1000
      
      await new Promise(resolve => setTimeout(resolve, delay))
      continue
    }
    
    return response
  }
  throw new Error('Max retries exceeded')
}
```

### "Variables endpoints require Enterprise plan"
**Cause**: Using Variables REST API write operations without Enterprise
**Fix**: Use Plugin API via MCP server or upgrade plan
```javascript
// ❌ Enterprise-only
POST /v1/files/:key/variables

// ✅ Available on all plans
const result = await useFigma(`
  const collection = figma.variables.createVariableCollection('Colors')
  const variable = figma.variables.createVariable('primary', collection.id, 'COLOR')
`)
```

## Debugging Techniques

### Console Debugging
```javascript
// Insert in Plugin API / use_figma code
console.log('Variable created:', variable)
console.log('Bound variables:', node.boundVariables)
console.log('Collection modes:', collection.modes.map(m => m.name))

// Debug variable resolution
console.log('Resolved value:', variable.resolveForConsumer(node))
```

### MCP Inspector
```bash
# Test MCP endpoints directly
npx @modelcontextprotocol/inspector

# Connect to Figma MCP server
# URL: https://mcp.figma.com/mcp (remote) or http://127.0.0.1:3845/mcp (desktop)
```

### Browser DevTools (Plugin API)
- Open: Plugins → Development → Open Console  
- Set breakpoints: Insert `debugger;` statements
- Inspect objects: Use `console.dir(figma.variables)` for deep inspection

### Variable Binding Validation
```javascript
// Check if variables bound correctly
function validateBinding(node, expectedVariableIds) {
  const bound = node.boundVariables || {}
  
  Object.entries(expectedVariableIds).forEach(([property, expectedId]) => {
    const actualId = bound[property]?.id
    if (actualId !== expectedId) {
      console.error(`${property} binding failed: expected ${expectedId}, got ${actualId}`)
    }
  })
}
```

## Error Prevention Checklist

- [ ] Load fonts before any text modification
- [ ] Check plan mode limits before adding modes
- [ ] Use mutually exclusive variable scopes
- [ ] Clone arrays before modification
- [ ] Capture `setBoundVariableForPaint` return values
- [ ] Enable auto-layout before setting layout properties
- [ ] Use correct variant naming format
- [ ] Batch large operations to stay under limits
- [ ] Implement retry logic for rate-limited endpoints
- [ ] Validate variable bindings after creation

## Common Error Patterns to Avoid

1. **Font-then-text**: Always `loadFontAsync()` before text changes
2. **Clone-modify-assign**: Never mutate readonly arrays directly  
3. **Layout-then-constraints**: Enable `layoutMode` before min/max properties
4. **Check-then-create**: Verify limits before adding modes/variables
5. **Capture-returns**: Always assign `setBoundVariableForPaint()` results


## Page and Node Async Errors

### "Object is not extensible"
**Cause**: Accessing a page or node before `loadAsync()`, or calling `loadAsync()` multiple times
**Fix**: Load the page ONCE at the start, store reference, operate on that reference
```javascript
// ❌ WRONG — repeated loadAsync causes state conflicts
for (const item of items) {
  await page.loadAsync()
  page.appendChild(node)
}

// ✅ CORRECT — load once, then operate
const page = figma.root.children.find(p => p.name === 'Components')
await figma.setCurrentPageAsync(page)
await page.loadAsync()

for (const item of items) {
  page.appendChild(createNode(item)) // Works — page already loaded
}
```

### "Node no longer exists" / stale reference
**Cause**: Holding a reference to a node after it's been deleted or after a page switch
**Fix**: Re-query nodes after any page navigation or bulk deletion
```javascript
// ❌ WRONG — reference goes stale after page switch
const node = figma.currentPage.findOne(n => n.name === 'Target')
await figma.setCurrentPageAsync(otherPage)
// ... do work ...
await figma.setCurrentPageAsync(originalPage)
node.name = 'Updated' // May fail — stale reference

// ✅ CORRECT — re-query after returning
await figma.setCurrentPageAsync(originalPage)
const freshNode = figma.currentPage.findOne(n => n.name === 'Target')
freshNode.name = 'Updated'
```

### "Cannot set properties on removed node"
**Cause**: Operating on a node that was removed earlier in the same execution
**Fix**: Check node existence before operating, or restructure order of operations
```javascript
// Defensive check
if (node && node.parent) {
  node.name = 'Safe Update'
}
```

## Image and Export Errors

### "exportAsync failed: node has zero dimensions"
**Cause**: Exporting a frame/node with 0 width or 0 height
**Fix**: Ensure node has positive dimensions before export
```javascript
if (node.width > 0 && node.height > 0) {
  const bytes = await node.exportAsync({ format: 'PNG', constraint: { type: 'SCALE', value: 2 } })
}
```

### Image fill appears blank or corrupted
**Cause**: Using `figma.createImage()` with invalid or unsupported image data
**Fix**: Validate image bytes and use correct format
```javascript
// Ensure valid image data
const imageHash = figma.createImage(validUint8Array).hash

const imagePaint = {
  type: 'IMAGE',
  scaleMode: 'FILL',
  imageHash: imageHash
}
node.fills = [imagePaint]
```

## Plugin Sandbox Errors

### "Cannot access 'fetch' from plugin code"
**Cause**: Trying to make HTTP requests from code.ts (sandbox)
**Fix**: All network requests must go through the UI iframe
```javascript
// In code.ts — send request to UI
figma.ui.postMessage({ type: 'FETCH_REQUEST', url: 'https://api.example.com/data' })

// In ui.html — handle the request
window.onmessage = async (event) => {
  if (event.data.pluginMessage.type === 'FETCH_REQUEST') {
    const response = await fetch(event.data.pluginMessage.url)
    const data = await response.json()
    parent.postMessage({ pluginMessage: { type: 'FETCH_RESPONSE', data } }, '*')
  }
}
```

### "Cannot use require() in plugin"
**Cause**: Using CommonJS require in Figma's sandboxed environment
**Fix**: Bundle dependencies at build time or use inline implementations
```javascript
// ❌ WRONG
const _ = require('lodash') // No require in sandbox

// ✅ CORRECT — bundle with esbuild/webpack at compile time
// Or implement the specific utility inline
function chunk(arr, size) {
  return Array.from({ length: Math.ceil(arr.length / size) }, (_, i) =>
    arr.slice(i * size, (i + 1) * size)
  )
}
```

### "postMessage payload exceeds size limit"
**Cause**: Sending very large data between UI and sandbox via postMessage
**Fix**: Chunk large payloads or send references instead of full data
```javascript
// ❌ WRONG — sending 10MB of SVG data in one message
parent.postMessage({ pluginMessage: { type: 'SVG_DATA', svgs: hugeArray } }, '*')

// ✅ CORRECT — chunk into batches
const batchSize = 50
for (let i = 0; i < svgs.length; i += batchSize) {
  parent.postMessage({
    pluginMessage: {
      type: 'SVG_BATCH',
      batch: svgs.slice(i, i + batchSize),
      batchIndex: i / batchSize,
      totalBatches: Math.ceil(svgs.length / batchSize)
    }
  }, '*')
}
```

## Complex Variable Aliasing Errors

### "Circular reference detected"
**Cause**: Variable A aliases Variable B which aliases Variable A
**Fix**: Always alias from semantic → primitive direction. Never alias between peers.
```javascript
// ❌ CREATES CIRCULAR REFERENCE
varA.setValueForMode(modeId, figma.variables.createVariableAlias(varB))
varB.setValueForMode(modeId, figma.variables.createVariableAlias(varA)) // Error!

// ✅ CORRECT — semantic aliases primitive (one direction)
semanticVar.setValueForMode(lightId, figma.variables.createVariableAlias(primitiveBlue500))
semanticVar.setValueForMode(darkId, figma.variables.createVariableAlias(primitiveBlue300))
```

### Alias resolves to wrong value across modes
**Cause**: Aliasing a variable that itself has modes — the alias resolves through the source's mode, not the consumer's
**Fix**: Understand the resolution chain: alias target variable's mode is resolved based on the *consuming node's* mode assignment, not the source collection's
```javascript
// If Semantics collection has Light/Dark modes
// and Primitives collection has only 1 mode:
// Alias from Semantics → Primitives works fine (Primitives has no mode ambiguity)

// If BOTH collections have Light/Dark:
// The alias resolves through the TARGET's matching mode
// Ensure mode names match across collections, or use explicit mode IDs
```

## Style Creation Pitfalls

### "Cannot create style with duplicate name"
**Cause**: Style with identical name already exists
**Fix**: Check for existing styles before creating, or remove first
```javascript
// Check first
const existing = figma.getLocalPaintStyles().find(s => s.name === 'color/brand/primary')
if (existing) {
  existing.remove() // Remove old version
}
const style = figma.createPaintStyle()
style.name = 'color/brand/primary'
```

### Text style fails to apply correctly
**Cause**: Font not loaded before setting text style properties
**Fix**: Load ALL font variants used in text styles before creating them
```javascript
// Load every weight you'll reference
await figma.loadFontAsync({ family: 'Inter', style: 'Regular' })
await figma.loadFontAsync({ family: 'Inter', style: 'Medium' })
await figma.loadFontAsync({ family: 'Inter', style: 'Semi Bold' })
await figma.loadFontAsync({ family: 'Inter', style: 'Bold' })

// Now create text styles
const style = figma.createTextStyle()
style.name = 'typography/heading/h1'
style.fontName = { family: 'Inter', style: 'Bold' } // Safe — already loaded
style.fontSize = 32
```

## Performance and Memory Errors

### Plugin times out on large operations
**Cause**: Processing thousands of nodes synchronously without yielding
**Fix**: Batch operations and use `figma.commitUndo()` boundaries
```javascript
// Process in batches of 50
const nodes = figma.currentPage.findAll(n => n.type === 'FRAME')
const batchSize = 50

for (let i = 0; i < nodes.length; i += batchSize) {
  const batch = nodes.slice(i, i + batchSize)
  
  batch.forEach(node => {
    // Process node
    updateNodeStyles(node)
  })
  
  // Allow Figma to process between batches
  if (i + batchSize < nodes.length) {
    await new Promise(resolve => setTimeout(resolve, 0))
  }
}
```

### "Out of memory" on large file operations
**Cause**: Loading too many nodes or images simultaneously
**Fix**: Use `figma.skipInvisibleInstanceChildren = true` and process incrementally
```javascript
// Skip invisible children for performance
figma.skipInvisibleInstanceChildren = true

// Process one page at a time instead of entire file
for (const page of figma.root.children) {
  await figma.setCurrentPageAsync(page)
  await page.loadAsync()
  
  const components = page.findAll(n => n.type === 'COMPONENT')
  processComponents(components)
}
```

### MCP tool call returns incomplete data
**Cause**: Response truncated due to size limits when inspecting complex nodes
**Fix**: Use targeted queries instead of broad inspections
```javascript
// ❌ WRONG — requesting entire complex page
await getDesignContext(fileKey, rootPageNodeId) // Truncated!

// ✅ CORRECT — inspect specific components
const metadata = await getMetadata(fileKey, rootPageNodeId)
const componentIds = metadata.children
  .filter(c => c.type === 'COMPONENT_SET')
  .map(c => c.id)

// Inspect one at a time
for (const id of componentIds) {
  const context = await getDesignContext(fileKey, id) // Manageable size
}
```

## Error Severity Classification

| Severity | Examples | Recovery |
|----------|----------|----------|
| **Blocking** | Object not extensible, node removed, font not loaded | Must fix before proceeding — usually code order issue |
| **Data loss risk** | Circular alias, wrong mode resolution | Validate bindings after creation; undo if wrong |
| **Silent failure** | Ignored setBoundVariableForPaint return, scope conflict | Add validation step; check bindings programmatically |
| **Performance** | Timeout, memory, truncated responses | Batch operations, target specific nodes, reduce scope |
| **Plan-gated** | Enterprise-only APIs, mode limits | Check plan tier before attempting; use Plugin API fallbacks |

## Related
- hub → [[figma]]
