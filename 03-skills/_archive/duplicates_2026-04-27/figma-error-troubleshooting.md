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
