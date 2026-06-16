# Figma Variable Creation Pipeline

## When to Use This Skill
Use when creating design tokens, variables, or any variable-based design system in Figma. This skill ensures proper dependency order and prevents common variable creation errors.

## The Critical Dependency Chain
**Variables → Styles → Components** - Each phase depends on the previous. Breaking this order causes failures.

## Phase 1: Collections and Primitive Variables

### Collection Creation Pattern
```javascript
// Create collection (always starts with 1 default mode)
const primitivesCollection = figma.variables.createVariableCollection('Primitives')
const semanticsCollection = figma.variables.createVariableCollection('Semantics')

// Add modes to semantics collection
semanticsCollection.addMode('Dark')
const lightMode = semanticsCollection.modes.find(m => m.name === 'Mode 1')
lightMode.name = 'Light' // Rename default mode

const lightModeId = lightMode.modeId
const darkModeId = semanticsCollection.modes.find(m => m.name === 'Dark').modeId
```

### Variable Creation Pattern
```javascript
// Create variable: name, collection, resolvedType
const variable = figma.variables.createVariable('color/blue/500', collection.id, 'COLOR')

// Set value (RGB uses 0-1 float range, not 0-255)
variable.setValueForMode(defaultMode.modeId, {
  r: parseInt(hex.slice(1, 3), 16) / 255,
  g: parseInt(hex.slice(3, 5), 16) / 255, 
  b: parseInt(hex.slice(5, 7), 16) / 255
})

// Set scopes (ALL_FILLS is mutually exclusive with specific fills)
variable.scopes = ['ALL_FILLS'] // Not ['ALL_FILLS', 'STROKE_COLOR']
```

## Phase 2: Semantic Variables with Aliases

### Alias Creation Pattern
```javascript
// Create semantic variable
const semanticVar = figma.variables.createVariable('color/surface/primary', collection.id, 'COLOR')

// Create aliases to primitives (different per mode)
semanticVar.setValueForMode(lightModeId, figma.variables.createVariableAlias(neutral50Var))
semanticVar.setValueForMode(darkModeId, figma.variables.createVariableAlias(neutral900Var))
```

## Variable Types and Values

### COLOR Variables
- **Value format**: `{r: 0.23, g: 0.51, b: 0.96}` (0-1 float range)
- **Common scopes**: `ALL_FILLS`, `STROKE_COLOR`, `TEXT_FILL`
- **Hex conversion**: `parseInt(hex.slice(1, 3), 16) / 255`

### FLOAT Variables  
- **Value format**: `42` (direct number)
- **Common scopes**: `WIDTH_HEIGHT`, `GAP`, `CORNER_RADIUS`, `FONT_SIZE`
- **Units**: Pixels for spacing/sizing, points for typography

### STRING Variables
- **Value format**: `"Inter"` (quoted string)
- **Common scopes**: `FONT_FAMILY`, `TEXT_CONTENT`

### BOOLEAN Variables
- **Value format**: `true` or `false`
- **Common scopes**: `ALL_SCOPES` (visibility toggles)

## Scope Rules (Critical)

### Mutually Exclusive Scopes
- `ALL_SCOPES` cannot combine with other scopes
- `ALL_FILLS` cannot combine with `FRAME_FILL`, `SHAPE_FILL`, `TEXT_FILL`

### Correct Scoping Examples
```javascript
// ✅ CORRECT
variable.scopes = ['ALL_FILLS']
variable.scopes = ['FRAME_FILL', 'SHAPE_FILL'] 
variable.scopes = ['WIDTH_HEIGHT', 'GAP']

// ❌ WRONG - triggers "If ALL_FILLS is set, other fill scopes cannot be set"
variable.scopes = ['ALL_FILLS', 'STROKE_COLOR']
```

## Mode Limits by Plan

| Plan | Max Modes | Error When Exceeded |
|------|-----------|-------------------|
| Starter/Free | 1 mode only | "Limited to 1 modes only" |
| Professional | 10 modes | "Limited to 10 modes only" |
| Organization | 20 modes | "Limited to 20 modes only" |
| Enterprise | 40 modes | "Limited to 40 modes only" |

### Mode Limit Check Pattern
```javascript
// Check current mode count before adding
if (collection.modes.length >= planModeLimit) {
  console.warn(`Cannot add mode: plan limit of ${planModeLimit} reached`)
  return
}
collection.addMode('Dark')
```

## Code Syntax Assignment

```javascript
// Set cross-platform code syntax
variable.codeSyntax = {
  WEB: `--color-${colorName}-${scale}`,
  ANDROID: `color_${colorName}_${scale}`,
  iOS: `color${colorName.charAt(0).toUpperCase() + colorName.slice(1)}${scale}`
}
```

## Common Variable Creation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "If ALL_FILLS is set, other fill scopes cannot be set" | Mixed exclusive scopes | Use only `ALL_FILLS` or only specific fills |
| "Limited to N modes only" | Exceeded plan mode limit | Check plan limits before `addMode()` |
| "Cannot create variable" | Invalid collection ID | Ensure collection exists and get fresh ID |
| RGB values > 1.0 appear white | Used 0-255 instead of 0-1 | Divide by 255: `r: 51/255` not `r: 51` |

## Variable Collection Architecture

### Recommended Structure
1. **Primitives Collection** (1 mode, concrete values, hidden from publishing)
2. **Semantics Collection** (Light/Dark modes, aliases to primitives)
3. **Component Collection** (optional, aliases to semantics)

### Collection Naming
- Use clear, hierarchical names: `color/blue/500`, `spacing/scale/4`
- Avoid special characters except `/` and `-`
- Start general, get specific: `color/surface/primary` not `surfacePrimaryColor`

## Validation Checklist

- [ ] Collections created in dependency order
- [ ] Mode limits respected per plan
- [ ] Scopes set without conflicts
- [ ] RGB values in 0-1 range for colors
- [ ] Aliases reference existing variables
- [ ] Code syntax set for cross-platform consistency
- [ ] Hidden primitives from publishing if desired
