---
name: figma-style-binding
description: >
  Binding variables to Figma styles and the clone-modify-reassign pattern for the ReadonlyArray fills/strokes/effects — prevents the most common Plugin API failures.
aliases: [figma-style-binding]
tier: spoke
domain: design
hub: figma
prerequisites: [figma]
spec_version: "2.0"
---

# Figma Style Binding and Immutability Rules

**Trigger**: Use this skill whenever binding variables to styles, encountering fill/stroke/effect errors, or when the user mentions style creation, variable binding, paint styles, text styles, or effect styles. Critical for preventing the most common Plugin API failures.

---

## The Immutability Rules That Prevent 90% of Errors

The single most important concept: **fills, strokes, and effects arrays are ReadonlyArray** — you cannot mutate them directly. All modifications require the **clone → modify → reassign** pattern.

### The Core Immutability Pattern
```javascript
// ❌ WRONG: Direct mutation fails
node.fills[0].color = { r: 1, g: 0, b: 0 }  // THROWS ERROR
node.fills.push(newFill)                    // THROWS ERROR

// ✅ CORRECT: Clone → modify → reassign
const newFills = [...node.fills]            // Clone array
newFills[0] = modifiedFill                  // Modify clone
node.fills = newFills                       // Reassign entire array
```

---

## Style Creation and Variable Binding

### Paint Style Creation with Variable Binding
```javascript
async function createPaintStyleWithVariable(name, colorVariable) {
  // Create the paint style
  const paintStyle = figma.createPaintStyle()
  paintStyle.name = name
  paintStyle.description = `Bound to variable: ${colorVariable.name}`
  
  // CRITICAL: Use setBoundVariableForPaint correctly
  const boundPaint = figma.variables.setBoundVariableForPaint(
    { type: "SOLID", color: { r: 0, g: 0, b: 0 } },  // Base paint (color ignored)
    "color",                                          // Field to bind
    colorVariable                                     // Variable object (not alias)
  )
  
  // Assign the bound paint
  paintStyle.paints = [boundPaint]
  
  return paintStyle
}
```
### Text Style Creation with Variable Bindings
```javascript
async function createTextStyleWithVariables(name, fontSizeVar, lineHeightVar, fontWeightVar) {
  // CRITICAL: Load font before any text mutation
  await figma.loadFontAsync({ family: "Inter", style: "Regular" })
  
  const textStyle = figma.createTextStyle()
  textStyle.name = name
  textStyle.fontName = { family: "Inter", style: "Regular" }
  
  // Set base values (will be overridden by variables)
  textStyle.fontSize = 16
  textStyle.lineHeight = { unit: "PIXELS", value: 24 }
  
  // Bind variables to text properties
  textStyle.setBoundVariable("fontSize", fontSizeVar)
  textStyle.setBoundVariable("lineHeight", lineHeightVar)
  textStyle.setBoundVariable("fontWeight", fontWeightVar)
  
  return textStyle
}
```

---

## Fill Binding: The Most Error-Prone Operation

### Correct Fill Variable Binding
```javascript
function bindVariableToFill(node, colorVariable) {
  // CRITICAL: Must check fills exist
  if (!node.fills || node.fills.length === 0) {
    // Create base fill if none exists
    node.fills = [{ type: "SOLID", color: { r: 0, g: 0, b: 0 } }]
  }
  
  // CRITICAL: Clone the array (immutability rule)
  const newFills = [...node.fills]
  
  // CRITICAL: setBoundVariableForPaint returns NEW paint object
  newFills[0] = figma.variables.setBoundVariableForPaint(
    newFills[0],        // Original paint to modify
    "color",            // Field to bind ("color" for solid, "gradientStops" for gradients)
    colorVariable       // Must be Variable object, not VariableAlias
  )
  
  // CRITICAL: Reassign entire array
  node.fills = newFills
}
```
---

## Quick Reference: Immutability Checklist

**✅ Always Clone First:**
```javascript
const newFills = [...node.fills]
const newStrokes = [...node.strokes] 
const newEffects = [...node.effects]
```

**✅ Capture Return Values:**
```javascript
// setBoundVariableForPaint returns NEW object
newFills[0] = figma.variables.setBoundVariableForPaint(...)

// setBoundVariableForEffect returns NEW object
shadow = figma.variables.setBoundVariableForEffect(shadow, ...)
```

**✅ Reassign Complete Arrays:**
```javascript
node.fills = newFills
node.strokes = newStrokes
node.effects = newEffects
```

**❌ Never Mutate Directly:**
```javascript
node.fills[0].color = ...     // FAILS
node.effects.push(...)        // FAILS  
delete node.strokes[0]        // FAILS
```

---

## Effect Style Creation and Binding

```javascript
const shadowStyle = figma.createEffectStyle()
shadowStyle.name = 'elevation/medium'

let shadow = {
  type: 'DROP_SHADOW',
  color: { r: 0, g: 0, b: 0, a: 0.15 },
  offset: { x: 0, y: 4 },
  radius: 8,
  spread: 0,
  visible: true,
  blendMode: 'NORMAL'
}

// Each setBoundVariableForEffect call returns a NEW effect object — capture it
shadow = figma.variables.setBoundVariableForEffect(shadow, 'radius', shadowRadiusVar)
shadow = figma.variables.setBoundVariableForEffect(shadow, 'color', shadowColorVar)

shadowStyle.effects = [shadow]
```

### Effect Bindable Fields
- `color` (COLOR variable)
- `radius` (FLOAT variable)
- `spread` (FLOAT variable)
- `offset.x`, `offset.y` (FLOAT variables)

---

## Node Property Variable Binding

Use `node.setBoundVariable(field, variable)` to bind variables directly to node properties (no array immutability dance — these aren't readonly arrays).

```javascript
frame.setBoundVariable('paddingTop', spacingVariable)
frame.setBoundVariable('paddingLeft', spacingVariable)
frame.setBoundVariable('itemSpacing', gapVariable)
frame.setBoundVariable('cornerRadius', radiusVariable)

textNode.setBoundVariable('fontSize', fontSizeVariable)
textNode.setBoundVariable('fontFamily', fontFamilyVariable)
```

### Node Bindable Fields

**Layout:** `width`, `height`, `paddingTop/Right/Bottom/Left`, `itemSpacing`, `counterAxisSpacing`, `minWidth`, `maxWidth`, `minHeight`, `maxHeight`

**Appearance:** `opacity`, `cornerRadius`, `topLeftRadius`, `topRightRadius`, `bottomLeftRadius`, `bottomRightRadius`, `strokeWeight`

**Typography:** `fontSize`, `fontFamily`, `lineHeight`, `letterSpacing`, `fontWeight`

### Text Style Bindable Fields
- `fontFamily` (STRING variable)
- `fontStyle` (STRING variable)
- `fontWeight` (FLOAT variable)
- `fontSize` (FLOAT variable)
- `lineHeight` (FLOAT variable)
- `letterSpacing` (FLOAT variable)
- `paragraphSpacing` (FLOAT variable)
- `paragraphIndent` (FLOAT variable)

---

## Gradient Variable Binding (Manual)

`setBoundVariableForPaint` only supports `SolidPaint`. For gradient stops, construct `boundVariables` manually inside each stop:

```javascript
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

---

## Debugging Variable Bindings

```javascript
console.log('Node bound variables:', node.boundVariables)
console.log('Style bound variables:', style.boundVariables)

// Resolve variable value for specific consumer node (mode-aware)
const resolvedValue = variable.resolveForConsumer(node)
console.log('Resolved value:', resolvedValue)
```

### Font Loading Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Cannot write to node with unloaded font" | Font not loaded before text mutation | `await figma.loadFontAsync()` first |
| "Font not found" | Incorrect family/style name | Check exact font names in Figma |
| Text appears as boxes | Font family not available | Load fallback fonts or use system fonts |

---

This skill prevents 90% of Plugin API errors by enforcing correct immutability patterns and proper variable binding workflows.

## Related
- hub → [[figma]]
