# Figma Style Binding and Immutability Rules

## When to Use This Skill
Use when creating or modifying Figma styles (paint, text, effect) and binding them to variables. This skill prevents the most common API errors caused by immutability violations.

## The Golden Rule: Clone → Modify → Reassign

**NEVER mutate fills, strokes, or effects arrays directly**. They are `ReadonlyArray` types. You must:
1. **Clone** the array: `const fillsCopy = [...node.fills]`
2. **Modify** the copy: `fillsCopy[0] = newPaint`  
3. **Reassign** to node: `node.fills = fillsCopy`

## Paint Style Creation and Binding

### Basic Paint Style Pattern
```javascript
// Create paint style
const paintStyle = figma.createPaintStyle()
paintStyle.name = 'colors/brand/primary' // Uses '/' for folders

// Bind to variable (CORRECT pattern)
const basePaint = { type: 'SOLID', color: { r: 0.23, g: 0.51, b: 0.96 } }
const boundPaint = figma.variables.setBoundVariableForPaint(basePaint, 'color', colorVariable)
paintStyle.paints = [boundPaint] // setBoundVariableForPaint returns NEW object
```

### Paint Variable Binding Rules
- `setBoundVariableForPaint()` **returns a new paint object** - never mutates
- Only works with `SolidPaint`, not gradient paints
- Third parameter must be actual `Variable` object, not `VariableAlias`
- Must capture the return value: `const newPaint = setBoundVariableForPaint(...)`

### Gradient Variable Binding (Manual)
```javascript
// For gradients, manually construct boundVariables
const gradientPaint = {
  type: 'GRADIENT_LINEAR',
  gradientStops: [
    { 
      color: { r: 1, g: 0, b: 0, a: 1 }, 
      position: 0,
      boundVariables: { color: { type: 'VARIABLE_ALIAS', id: redVariable.id } }
    },
    { 
      color: { r: 0, g: 0, b: 1, a: 1 }, 
      position: 1,
      boundVariables: { color: { type: 'VARIABLE_ALIAS', id: blueVariable.id } }
    }
  ],
  gradientTransform: [[1,0,0],[0,1,0]]
}
```

## Text Style Creation and Binding

### Font Loading Prerequisite
```javascript
// ALWAYS load fonts before ANY text property modification
await figma.loadFontAsync({ family: 'Inter', style: 'Bold' })
await figma.loadFontAsync({ family: 'Inter', style: 'Regular' })
```

### Text Style Pattern
```javascript
// Create text style
const textStyle = figma.createTextStyle()
textStyle.name = 'typography/heading/h1'

// Set basic properties
textStyle.fontName = { family: 'Inter', style: 'Bold' }
textStyle.fontSize = 32
textStyle.lineHeight = { value: 120, unit: 'PERCENT' }

// Bind variables to bindable fields
textStyle.setBoundVariable('fontSize', fontSizeH1Variable)
textStyle.setBoundVariable('lineHeight', lineHeightH1Variable)
textStyle.setBoundVariable('fontWeight', fontWeightBoldVariable)

// Bind fill color (uses same immutability pattern)
const textFill = { type: 'SOLID', color: { r: 0, g: 0, b: 0 } }
const boundTextFill = figma.variables.setBoundVariableForPaint(textFill, 'color', textColorVariable)
textStyle.fills = [boundTextFill]
```

### Text Style Bindable Fields
- `fontFamily` (STRING variable)
- `fontStyle` (STRING variable) 
- `fontWeight` (FLOAT variable)
- `fontSize` (FLOAT variable)
- `lineHeight` (FLOAT variable)
- `letterSpacing` (FLOAT variable)
- `paragraphSpacing` (FLOAT variable)
- `paragraphIndent` (FLOAT variable)

## Effect Style Creation and Binding

### Effect Style Pattern
```javascript
// Create effect style
const shadowStyle = figma.createEffectStyle()
shadowStyle.name = 'elevation/medium'

// Create base effect
let shadow = {
  type: 'DROP_SHADOW',
  color: { r: 0, g: 0, b: 0, a: 0.15 },
  offset: { x: 0, y: 4 },
  radius: 8,
  spread: 0,
  visible: true,
  blendMode: 'NORMAL'
}

// Bind variables (each call returns NEW effect object)
shadow = figma.variables.setBoundVariableForEffect(shadow, 'radius', shadowRadiusVar)
shadow = figma.variables.setBoundVariableForEffect(shadow, 'color', shadowColorVar)

// Assign to style
shadowStyle.effects = [shadow]
```

### Effect Bindable Fields
- `color` (COLOR variable)
- `radius` (FLOAT variable) 
- `spread` (FLOAT variable)
- `offset.x`, `offset.y` (FLOAT variables)

## Node Property Variable Binding

### Direct Property Binding
```javascript
// Bind variables directly to node properties
frame.setBoundVariable('paddingTop', spacingVariable)
frame.setBoundVariable('paddingLeft', spacingVariable)
frame.setBoundVariable('itemSpacing', gapVariable)
frame.setBoundVariable('cornerRadius', radiusVariable)

textNode.setBoundVariable('fontSize', fontSizeVariable)
textNode.setBoundVariable('fontFamily', fontFamilyVariable)
```

### Node Bindable Fields
**Layout**: `width`, `height`, `paddingTop/Right/Bottom/Left`, `itemSpacing`, `counterAxisSpacing`, `minWidth`, `maxWidth`, `minHeight`, `maxHeight`

**Appearance**: `opacity`, `cornerRadius`, `topLeftRadius`, `topRightRadius`, `bottomLeftRadius`, `bottomRightRadius`, `strokeWeight`

**Typography**: `fontSize`, `fontFamily`, `lineHeight`, `letterSpacing`, `fontWeight`

## Common Immutability Errors

### Wrong: Ignoring Return Value
```javascript
// ❌ WRONG - ignoring return value
figma.variables.setBoundVariableForPaint(node.fills[0], 'color', variable)
// node.fills[0] is still unbound!
```

### Wrong: Direct Array Mutation
```javascript
// ❌ WRONG - mutating readonly array
node.fills[0] = newPaint // TypeError: Cannot assign to read only property
```

### Correct: Clone → Modify → Reassign
```javascript
// ✅ CORRECT
const fillsCopy = [...node.fills] // Clone
fillsCopy[0] = figma.variables.setBoundVariableForPaint(fillsCopy[0], 'color', variable) // Modify
node.fills = fillsCopy // Reassign
```

## Font Loading Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Cannot write to node with unloaded font" | Font not loaded before text mutation | `await figma.loadFontAsync()` first |
| "Font not found" | Incorrect family/style name | Check exact font names in Figma |
| Text appears as boxes | Font family not available | Load fallback fonts or use system fonts |

## Style Validation Checklist

- [ ] Font loaded before text style creation
- [ ] `setBoundVariableForPaint` return value captured
- [ ] `setBoundVariableForEffect` return value captured  
- [ ] Arrays cloned before modification
- [ ] Modified arrays reassigned to node/style
- [ ] Variable objects passed (not VariableAlias plain objects)
- [ ] Gradient stops manually bound if needed
- [ ] Style names use '/' for folder structure

## Debugging Variable Bindings

```javascript
// Check if binding worked
console.log('Node bound variables:', node.boundVariables)
console.log('Style bound variables:', style.boundVariables)

// Resolve variable value for specific context
const resolvedValue = variable.resolveForConsumer(node)
console.log('Resolved value:', resolvedValue)
```
