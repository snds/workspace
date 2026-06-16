# Figma Variable Creation Pipeline

**Trigger**: Use this skill whenever creating variables in Figma, setting up design token systems, or when encountering variable-related errors. Also trigger when the user mentions "variables", "design tokens", "collections", "modes", or asks about binding variables to styles or components.

---

## The Variable Dependency Chain

Variables must be created in strict dependency order. The dependency chain is:
**Collections → Modes → Variables → Variable Values → Style Bindings → Component Bindings**

Breaking this chain causes errors. Each phase must complete before the next begins.

---

## Phase 1: Collection Creation and Setup

### Basic Collection Creation
```javascript
// Create the collection (starts with 1 default mode)
const collection = figma.variables.createVariableCollection("Design Tokens")

// Rename the default mode
const defaultModeId = collection.modes[0].modeId
collection.renameMode(defaultModeId, "Light")

// Add additional modes
const darkModeId = collection.addMode("Dark")
const hcModeId = collection.addMode("High Contrast")  // if needed
```

### Mode Limit Validation
```javascript
// Check mode limits before creating
const maxModes = {
  starter: 1,
  professional: 10, 
  organization: 20,
  enterprise: 40
}

// Validate before adding modes
if (collection.modes.length >= maxModes[plan]) {
  throw new Error(`Plan limited to ${maxModes[plan]} modes`)
}
```
### Collection Organization Strategy
```javascript
// Recommended collection structure
const collections = [
  "Primitives",      // Base tokens (color/500, spacing/md)
  "Semantic",        // Semantic aliases (surface/primary)
  "Component"        // Component-specific tokens (button/bg)
]

// Create collections with proper scope
collections.forEach(name => {
  const collection = figma.variables.createVariableCollection(name)
  
  if (name === "Primitives") {
    collection.hiddenFromPublishing = true  // Hide base tokens
  }
})
```

---

## Phase 2: Variable Creation Patterns

### Variable Types and Resolved Types
```javascript
// COLOR variables (0-1 float range, NOT 0-255)
const colorVar = figma.variables.createVariable(
  "color/blue/500", 
  collection, 
  "COLOR"
)

// FLOAT variables (spacing, sizing, opacity)
const spacingVar = figma.variables.createVariable(
  "spacing/md",
  collection,
  "FLOAT" 
)

// STRING variables (font families, text content)
const fontVar = figma.variables.createVariable(
  "font/family/body",
  collection,
  "STRING"
)

// BOOLEAN variables (visibility toggles)
const visibilityVar = figma.variables.createVariable(
  "features/show-beta",
  collection,
  "BOOLEAN"
)
```
### Setting Variable Values by Mode
```javascript
// Color values (RGB 0-1 float, NOT 0-255 integers)
colorVar.setValueForMode(lightModeId, { r: 0.23, g: 0.51, b: 0.96 })
colorVar.setValueForMode(darkModeId, { r: 0.47, g: 0.67, b: 0.98 })

// RGBA with alpha
const shadowColorVar = figma.variables.createVariable("shadow/color", collection, "COLOR")
shadowColorVar.setValueForMode(lightModeId, { r: 0, g: 0, b: 0, a: 0.15 })
shadowColorVar.setValueForMode(darkModeId, { r: 0, g: 0, b: 0, a: 0.25 })

// Float values 
spacingVar.setValueForMode(lightModeId, 16)
spacingVar.setValueForMode(darkModeId, 16)  // Usually same across modes

// String values
fontVar.setValueForMode(lightModeId, "Inter")
fontVar.setValueForMode(darkModeId, "Inter")

// Boolean values
visibilityVar.setValueForMode(lightModeId, true)
visibilityVar.setValueForMode(darkModeId, false)
```

### Critical Scoping Rules
```javascript
// COLOR scopes
colorVar.scopes = ["FRAME_FILL", "SHAPE_FILL", "TEXT_FILL"]

// FLOAT scopes for spacing
spacingVar.scopes = ["WIDTH_HEIGHT", "GAP", "CORNER_RADIUS"] 

// STRING scopes for typography
fontVar.scopes = ["FONT_FAMILY"]

// Mutually exclusive scopes
// ❌ WRONG: Cannot combine ALL_SCOPES with specific scopes
badVar.scopes = ["ALL_SCOPES", "FRAME_FILL"]  // THROWS ERROR

// ❌ WRONG: Cannot combine ALL_FILLS with specific fill scopes  
badVar.scopes = ["ALL_FILLS", "FRAME_FILL"]   // THROWS ERROR

// ✅ CORRECT: Use one or the other
goodVar.scopes = ["ALL_SCOPES"]  // OR specific scopes
goodVar.scopes = ["FRAME_FILL", "SHAPE_FILL"]
```
---

## Phase 3: Variable Aliasing (Semantic Layer)

### Creating Semantic Aliases
```javascript
// Create the alias reference
const alias = figma.variables.createVariableAlias(primitiveVar)

// Apply alias to semantic variable in specific mode
semanticVar.setValueForMode(lightModeId, alias)

// Different aliases per mode (common pattern)
const blue500 = primitiveCollection.getVariable("blue/500")
const blue200 = primitiveCollection.getVariable("blue/200")

const brandPrimary = semanticCollection.getVariable("brand/primary")
brandPrimary.setValueForMode(lightModeId, figma.variables.createVariableAlias(blue500))
brandPrimary.setValueForMode(darkModeId, figma.variables.createVariableAlias(blue200))
```

### Async Aliasing (When Working with IDs)
```javascript
// When you only have variable IDs
const aliasById = await figma.variables.createVariableAliasByIdAsync(sourceVariableId)
targetVar.setValueForMode(modeId, aliasById)
```

### Circular Reference Prevention
```javascript
// The API automatically validates and rejects circular references
try {
  varA.setValueForMode(mode, figma.variables.createVariableAlias(varB))
  varB.setValueForMode(mode, figma.variables.createVariableAlias(varA))  // THROWS ERROR
} catch (error) {
  console.log("Circular reference detected:", error)
}
```
---

## Phase 4: Variable Metadata and Code Syntax

### Setting Descriptions and Metadata
```javascript
variable.description = "Primary brand color used for key UI elements and CTAs"
variable.hiddenFromPublishing = false  // Show in dev handoff

// Set code syntax for different platforms
variable.setVariableCodeSyntax('WEB', '--color-brand-primary')
variable.setVariableCodeSyntax('ANDROID', 'R.color.brand_primary') 
variable.setVariableCodeSyntax('IOS', 'UIColor.brandPrimary')
```

### Remote Variable Handling
```javascript
// Check if variable is from external library
if (variable.remote) {
  console.log("Variable is from external library:", variable.key)
  // Cannot modify remote variables directly
  // Must import or create local copy
}
```

---

## Variable Validation Patterns

### Check Variable Existence
```javascript
// Safe variable access
function getVariableByName(collection, name) {
  const variables = collection.getLocalVariables()
  return variables.find(v => v.name === name) || null
}

// Validate before use
const variable = getVariableByName(collection, "brand/primary")
if (!variable) {
  throw new Error(`Variable brand/primary not found in ${collection.name}`)
}
```

---

## Common Variable Creation Errors

| Error | Cause | Fix |
|-------|--------|-----|
| `Limited to N modes only` | Exceeded plan mode limit | Check plan limits before addMode() |
| `Cannot set value for mode` | Mode doesn't exist in collection | Verify mode exists before setValue |
| `Invalid color format` | Using 0-255 RGB instead of 0-1 | Convert: `{r: 255/255, g: 100/255, b: 50/255}` |
| `Invalid scope combination` | ALL_SCOPES mixed with specific scopes | Use ALL_SCOPES alone or specific scopes |
| `Variable not found` | Referencing deleted/renamed variable | Validate variable existence before use |
| `Circular alias reference` | A→B→A alias chain | Design alias hierarchy to be acyclic |

---

This skill ensures variables are created in the correct dependency order and with proper configuration to prevent binding failures in later phases.

---

## See also

- [figma-modes-for-variants](../figma-modes-for-variants/SKILL.md) — architectural
  pattern for using mode-driven variables to collapse component-set variant
  matrices when an axis is purely color/style. Sits one layer above this skill.
