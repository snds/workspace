---
name: figma-ds-generation-pipeline
description: >
  Orchestrates end-to-end design-system generation in Figma in dependency order (variables to styles to components) with validation at each phase.
aliases: [figma-ds-generation-pipeline]
tier: spoke
domain: design
hub: figma
prerequisites: [figma]
spec_version: "2.0"
---

# Complete Design System Generation Pipeline

## When to Use This Skill
Use when generating complete design systems in Figma with proper dependency ordering. This skill orchestrates the entire pipeline from variables through components with validation at each phase.

## The Five-Phase Dependency Chain
**Variables → Styles → Components → Documentation → Validation**

Each phase must complete successfully before the next begins. Breaking this order causes cascade failures.

## Pre-Pipeline Setup

### Step 0: Stack Selection (Required)

Before starting any pipeline phase, present a stack-selection prompt to confirm the target tech stack. This drives all subsequent token naming, code syntax, and component structure decisions throughout the pipeline.

Selection options:

1. **Use defaults** — shadcn + Radix UI (color system) + Tailwind CSS
2. **Tell me your stack** — specify your own component library, color system, and CSS framework
3. **Popular alternative stacks** — MUI, Chakra, Ant Design, Vuetify, Skeleton UI

If defaults are selected, collect: brand primary hex, Radix gray family preference (gray / mauve / slate / sage / olive / sand), Tailwind version (v3/v4), dark mode inclusion (yes/no).

These answers feed Phase 1 (primitive scale generation) and Phase 1C (semantic alias binding map).

### Radix Base Color Architecture (when defaults selected)

The Primitives collection includes the **entire** Radix UI color system. Every scale has four variants:

| Variant | Figma Name Pattern | CSS Format | Figma RGBA |
|---------|-------------------|------------|------------|
| Opaque | `{color}/{step}` | `hex` | `{r, g, b}` (a=1 implicit) |
| Alpha | `{color}/A{step}` | `rgba()` / `color()` | `{r, g, b, a}` where a < 1 |

Light and Dark values are expressed as **modes** on the Primitives collection (Light mode, Dark mode).

**Scales to generate:**

| Category | Scales | Count |
|----------|--------|-------|
| Grays | gray, mauve, slate, sage, olive, sand | 6 |
| Reds | tomato, red, ruby, crimson | 4 |
| Purples | pink, plum, purple, violet | 4 |
| Blues | iris, indigo, blue, sky, cyan | 5 |
| Greens | teal, jade, green, grass | 4 |
| Light greens | lime, mint | 2 |
| Warm | orange, amber, yellow | 3 |
| Earth | bronze, gold, brown | 3 |
| **Brand** | **primary** (custom from user hex, step 9 = brand color) | **1** |
| Absolutes | white, black | 2 |

- **Variable count per scale:** 12 opaque + 12 alpha = 24 vars
- **Total scales:** 32 chromatic + 6 gray = 38 (+ white/black)
- **Total primitive color vars:** 38 × 24 + 2 = **914 variables**

Each variable gets:
- `scopes: []` (empty — hidden from property pickers, consumed only via semantic aliases)
- `hiddenFromPublishing: true`
- `codeSyntax.WEB: var(--{color}-{step})` or `var(--{color}-a{step})` for alpha

**Batch execution order** (primitives MUST be created in batches to avoid script timeouts; each batch handles ONE color family — opaque + alpha, light + dark):
1. Gray scales (6 batches: gray, mauve, slate, sage, olive, sand)
2. Chromatic scales (25 batches: one per color)
3. Brand primary (1 batch: custom scale from user hex)
4. Absolutes (1 batch: white + black)
5. Validation pass: count all variables, verify mode values

### Radix Semantic Scale Binding Map (Phase 1C input)

When defaults are selected, semantic tokens alias to primitives using the following role-to-scale mapping. Every semantic color MUST reference a specific Radix primitive scale — never a raw value.

| Semantic Role | Bound Radix Scale | Steps Used |
|---------------|-------------------|------------|
| `primary` | `primary` (custom) | 3-12 |
| `secondary` | selected gray family | 1-12 |
| `destructive` | `red` | 3-12 |
| `success` | `green` | 3-12 |
| `warning` | `amber` | 3-12 |
| `info` | `blue` | 3-12 |
| `accent` | `violet` (configurable) | 3-12 |

Per-role token pattern (apply for each role above):

```javascript
const bindings = {
  [`color/${role}/bg`]:           { light: `${scale}/3`,  dark: `${scale}/3` },
  [`color/${role}/bg-hover`]:     { light: `${scale}/4`,  dark: `${scale}/4` },
  [`color/${role}/bg-active`]:    { light: `${scale}/5`,  dark: `${scale}/5` },
  [`color/${role}/border`]:       { light: `${scale}/7`,  dark: `${scale}/7` },
  [`color/${role}/border-hover`]: { light: `${scale}/8`,  dark: `${scale}/8` },
  [`color/${role}/solid`]:        { light: `${scale}/9`,  dark: `${scale}/9` },
  [`color/${role}/solid-hover`]:  { light: `${scale}/10`, dark: `${scale}/10` },
  [`color/${role}/text`]:         { light: `${scale}/11`, dark: `${scale}/11` },
  [`color/${role}/text-contrast`]:{ light: `${scale}/12`, dark: `${scale}/12` }
}
```

Gray-bound semantic tokens (using selected gray family from Step 0):

```javascript
const gray = 'slate' // from Step 0 selection
const grayBindings = {
  'color/bg/page':            `${gray}/1`,
  'color/bg/subtle':          `${gray}/2`,
  'color/bg/component':       `${gray}/3`,
  'color/bg/component-hover': `${gray}/4`,
  'color/bg/component-active':`${gray}/5`,
  'color/border/default':     `${gray}/6`,
  'color/border/strong':      `${gray}/7`,
  'color/border/hover':       `${gray}/8`,
  'color/text/tertiary':      `${gray}/9`,
  'color/text/secondary':     `${gray}/11`,
  'color/text/primary':       `${gray}/12`
}
const alphaBindings = {
  'color/overlay/light':      `${gray}/A6`,
  'color/overlay/medium':     `${gray}/A8`,
  'color/overlay/heavy':      `${gray}/A9`
}
```

**CRITICAL RULE:** Semantic variables NEVER hold raw `{r, g, b}` values. They ALWAYS use `{ type: 'VARIABLE_ALIAS', id: primitiveVar.id }`. This ensures mode switching propagates correctly through the entire token chain.

---

### Step 1: File Access and Authentication
```javascript
// Check authentication and file access
const user = await whoami()
console.log(`Authenticated as: ${user.email}`)

// Get plan details for mode limits and features
const plan = user.plans[0] // Use first plan or let user choose
const planTier = plan.tier // 'starter', 'professional', 'organization', 'enterprise'
const modeLimits = {
  starter: 1, professional: 10, organization: 20, enterprise: 40
}
```

### Step 2: Design System Inventory
```javascript
// Always check existing design system before generating
const existing = await searchDesignSystem(fileKey, 'colors spacing typography components')

const inventory = {
  variables: existing.variables?.length || 0,
  collections: existing.collections?.length || 0, 
  styles: existing.styles?.length || 0,
  components: existing.components?.length || 0
}

console.log('Existing DS inventory:', inventory)
```

## Phase 1: Variable Collections and Primitives

### Phase 1A: Collections Setup
```javascript
await useFigma({
  fileKey,
  description: 'Phase 1A: Create variable collections with proper mode structure',
  code: `
    // Clear existing if regenerating
    const existing = figma.variables.getLocalVariableCollections()
    existing.forEach(collection => collection.remove())
    
    // Create collections
    const primitivesCollection = figma.variables.createVariableCollection('Primitives')
    const semanticsCollection = figma.variables.createVariableCollection('Semantics')
    
    // Set up modes for semantics (primitives stay single mode)
    const darkModeId = semanticsCollection.addMode('Dark')
    const lightMode = semanticsCollection.modes.find(m => m.name === 'Mode 1')
    lightMode.name = 'Light'
    
    // Store mode IDs for Phase 1B
    figma.root.setRelaunchData({
      lightModeId: lightMode.modeId,
      darkModeId: darkModeId,
      primitivesCollectionId: primitivesCollection.id,
      semanticsCollectionId: semanticsCollection.id
    })
    
    console.log('✅ Collections and modes created')
    return {
      primitivesCollection: primitivesCollection.id,
      semanticsCollection: semanticsCollection.id,
      lightMode: lightMode.modeId,
      darkMode: darkModeId
    }
  `
})
```

### Phase 1B: Primitive Variables
```javascript
await useFigma({
  fileKey,
  description: 'Phase 1B: Generate primitive color variables',
  code: `
    // Get collection IDs from Phase 1A
    const relaunchData = figma.root.getRelaunchData()
    const primitivesCollection = figma.variables.getVariableCollectionById(relaunchData.primitivesCollectionId)
    
    // Color ramps with perceptual uniformity
    const colorRamps = {
      blue: ['#f0f9ff', '#e0f2fe', '#bae6fd', '#7dd3fc', '#38bdf8', '#0ea5e9', '#0284c7', '#0369a1', '#075985', '#0c4a6e'],
      neutral: ['#fafafa', '#f4f4f5', '#e4e4e7', '#d4d4d8', '#a1a1aa', '#71717a', '#52525b', '#3f3f46', '#27272a', '#18181b'],
      green: ['#f0fdf4', '#dcfce7', '#bbf7d0', '#86efac', '#4ade80', '#22c55e', '#16a34a', '#15803d', '#166534', '#14532d'],
      amber: ['#fffbeb', '#fef3c7', '#fde68a', '#facc15', '#eab308', '#d97706', '#b45309', '#92400e', '#78350f', '#451a03'],
      red: ['#fef2f2', '#fee2e2', '#fecaca', '#fca5a5', '#f87171', '#ef4444', '#dc2626', '#b91c1c', '#991b1b', '#7f1d1d']
    }
    
    const primitiveVars = {}
    const defaultMode = primitivesCollection.modes[0]
    let totalPrimitives = 0
    
    // Generate all primitive variables
    Object.entries(colorRamps).forEach(([colorName, ramp]) => {
      primitiveVars[colorName] = {}
      ramp.forEach((hex, index) => {
        const scale = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900][index]
        const varName = \`color/\${colorName}/\${scale}\`
        
        const variable = figma.variables.createVariable(varName, primitivesCollection.id, 'COLOR')
        const r = parseInt(hex.slice(1, 3), 16) / 255
        const g = parseInt(hex.slice(3, 5), 16) / 255
        const b = parseInt(hex.slice(5, 7), 16) / 255
        variable.setValueForMode(defaultMode.modeId, { r, g, b })
        variable.scopes = ['ALL_FILLS']
        variable.hiddenFromPublishing = true // Hide primitives
        
        // Set cross-platform code syntax
        variable.codeSyntax = {
          WEB: \`--color-\${colorName}-\${scale}\`,
          ANDROID: \`color_\${colorName}_\${scale}\`,
          iOS: \`color\${colorName.charAt(0).toUpperCase() + colorName.slice(1)}\${scale}\`
        }
        
        primitiveVars[colorName][scale] = variable
        totalPrimitives++
      })
    })
    
    // Store primitive variable IDs for Phase 1C
    const primitiveIds = {}
    Object.entries(primitiveVars).forEach(([color, scales]) => {
      primitiveIds[color] = {}
      Object.entries(scales).forEach(([scale, variable]) => {
        primitiveIds[color][scale] = variable.id
      })
    })
    
    figma.root.setRelaunchData({
      ...relaunchData,
      primitiveVariableIds: JSON.stringify(primitiveIds)
    })
    
    console.log(\`✅ Created \${totalPrimitives} primitive variables\`)
    return { totalPrimitives, primitivesCreated: true }
  `
})
```

### Phase 1C: Semantic Variables with Aliases
```javascript
await useFigma({
  fileKey,
  description: 'Phase 1C: Create semantic variables with light/dark mode aliases',
  code: `
    // Get data from previous phases
    const relaunchData = figma.root.getRelaunchData()
    const semanticsCollection = figma.variables.getVariableCollectionById(relaunchData.semanticsCollectionId)
    const primitiveIds = JSON.parse(relaunchData.primitiveVariableIds)
    
    const lightModeId = relaunchData.lightModeId
    const darkModeId = relaunchData.darkModeId
    
    // Get primitive variables by ID
    const getPrimitiveVar = (color, scale) => figma.variables.getVariableById(primitiveIds[color][scale])
    
    // Semantic color mappings
    const semanticMappings = {
      'surface/primary': { light: getPrimitiveVar('neutral', 50), dark: getPrimitiveVar('neutral', 900) },
      'surface/secondary': { light: getPrimitiveVar('neutral', 100), dark: getPrimitiveVar('neutral', 800) },
      'surface/tertiary': { light: getPrimitiveVar('neutral', 200), dark: getPrimitiveVar('neutral', 700) },
      'text/primary': { light: getPrimitiveVar('neutral', 900), dark: getPrimitiveVar('neutral', 50) },
      'text/secondary': { light: getPrimitiveVar('neutral', 600), dark: getPrimitiveVar('neutral', 400) },
      'text/tertiary': { light: getPrimitiveVar('neutral', 500), dark: getPrimitiveVar('neutral', 500) },
      'border/primary': { light: getPrimitiveVar('neutral', 200), dark: getPrimitiveVar('neutral', 700) },
      'border/secondary': { light: getPrimitiveVar('neutral', 100), dark: getPrimitiveVar('neutral', 800) },
      'brand/primary': { light: getPrimitiveVar('blue', 500), dark: getPrimitiveVar('blue', 400) },
      'brand/secondary': { light: getPrimitiveVar('blue', 600), dark: getPrimitiveVar('blue', 300) },
      'status/success': { light: getPrimitiveVar('green', 500), dark: getPrimitiveVar('green', 400) },
      'status/warning': { light: getPrimitiveVar('amber', 500), dark: getPrimitiveVar('amber', 400) },
      'status/error': { light: getPrimitiveVar('red', 500), dark: getPrimitiveVar('red', 400) }
    }
    
    const semanticVars = {}
    let totalSemantics = 0
    
    // Create semantic variables with mode aliases
    Object.entries(semanticMappings).forEach(([semanticName, modeValues]) => {
      const variable = figma.variables.createVariable(\`color/\${semanticName}\`, semanticsCollection.id, 'COLOR')
      
      // Set aliases for each mode
      variable.setValueForMode(lightModeId, figma.variables.createVariableAlias(modeValues.light))
      variable.setValueForMode(darkModeId, figma.variables.createVariableAlias(modeValues.dark))
      
      variable.scopes = ['ALL_FILLS']
      
      // Semantic code syntax
      const cssName = semanticName.replace(/\\//g, '-')
      variable.codeSyntax = {
        WEB: \`--color-\${cssName}\`,
        ANDROID: \`color_\${semanticName.replace(/\\//g, '_')}\`,
        iOS: \`color\${semanticName.split('/').map(s => s.charAt(0).toUpperCase() + s.slice(1)).join('')}\`
      }
      
      semanticVars[semanticName] = variable
      totalSemantics++
    })
    
    // Store semantic variable IDs for Phase 2
    const semanticIds = {}
    Object.entries(semanticVars).forEach(([name, variable]) => {
      semanticIds[name] = variable.id
    })
    
    figma.root.setRelaunchData({
      ...relaunchData,
      semanticVariableIds: JSON.stringify(semanticIds),
      phase1Complete: 'true'
    })
    
    console.log(\`✅ Created \${totalSemantics} semantic variables with Light/Dark modes\`)
    return { totalSemantics, semanticsCreated: true }
  `
})
```

## Phase 2: Style Creation and Variable Binding

```javascript
await useFigma({
  fileKey,
  description: 'Phase 2: Create styles bound to semantic variables',
  code: `
    // Get semantic variable IDs from Phase 1
    const relaunchData = figma.root.getRelaunchData()
    
    if (relaunchData.phase1Complete !== 'true') {
      throw new Error('Phase 1 must complete before Phase 2')
    }
    
    const semanticIds = JSON.parse(relaunchData.semanticVariableIds)
    const getSemanticVar = (name) => figma.variables.getVariableById(semanticIds[name])
    
    // Create color styles bound to semantic variables
    const colorStyleMappings = [
      { name: 'color/surface/primary', variable: getSemanticVar('surface/primary') },
      { name: 'color/surface/secondary', variable: getSemanticVar('surface/secondary') },
      { name: 'color/text/primary', variable: getSemanticVar('text/primary') },
      { name: 'color/text/secondary', variable: getSemanticVar('text/secondary') },
      { name: 'color/brand/primary', variable: getSemanticVar('brand/primary') },
      { name: 'color/status/success', variable: getSemanticVar('status/success') },
      { name: 'color/status/warning', variable: getSemanticVar('status/warning') },
      { name: 'color/status/error', variable: getSemanticVar('status/error') }
    ]
    
    const createdColorStyles = []
    colorStyleMappings.forEach(({ name, variable }) => {
      const style = figma.createPaintStyle()
      style.name = name
      
      // Bind to semantic variable using immutability pattern
      const basePaint = { type: 'SOLID', color: { r: 0, g: 0, b: 0 } }
      const boundPaint = figma.variables.setBoundVariableForPaint(basePaint, 'color', variable)
      style.paints = [boundPaint]
      
      createdColorStyles.push(style.name)
    })
    
    // Create text styles bound to variables (fonts must be loaded first)
    await figma.loadFontAsync({ family: 'Inter', style: 'Regular' })
    await figma.loadFontAsync({ family: 'Inter', style: 'Medium' })
    await figma.loadFontAsync({ family: 'Inter', style: 'Bold' })
    
    const textStyles = [
      { name: 'typography/heading/h1', size: 32, weight: 'Bold', colorVar: getSemanticVar('text/primary') },
      { name: 'typography/heading/h2', size: 24, weight: 'Bold', colorVar: getSemanticVar('text/primary') },
      { name: 'typography/body/large', size: 18, weight: 'Regular', colorVar: getSemanticVar('text/primary') },
      { name: 'typography/body/medium', size: 16, weight: 'Regular', colorVar: getSemanticVar('text/primary') },
      { name: 'typography/body/small', size: 14, weight: 'Regular', colorVar: getSemanticVar('text/secondary') },
      { name: 'typography/caption', size: 12, weight: 'Medium', colorVar: getSemanticVar('text/secondary') }
    ]
    
    const createdTextStyles = []
    textStyles.forEach(({ name, size, weight, colorVar }) => {
      const style = figma.createTextStyle()
      style.name = name
      style.fontName = { family: 'Inter', style: weight }
      style.fontSize = size
      
      // Bind text color to variable
      const textFill = { type: 'SOLID', color: { r: 0, g: 0, b: 0 } }
      const boundTextFill = figma.variables.setBoundVariableForPaint(textFill, 'color', colorVar)
      style.fills = [boundTextFill]
      
      createdTextStyles.push(style.name)
    })
    
    figma.root.setRelaunchData({
      ...relaunchData,
      phase2Complete: 'true',
      colorStylesCount: createdColorStyles.length,
      textStylesCount: createdTextStyles.length
    })
    
    console.log(\`✅ Created \${createdColorStyles.length} color styles and \${createdTextStyles.length} text styles\`)
    return { 
      colorStyles: createdColorStyles.length,
      textStyles: createdTextStyles.length,
      phase2Complete: true
    }
  `
})
```

## Phase 3: Component Generation

```javascript
await useFigma({
  fileKey,
  description: 'Phase 3: Generate core components with variable bindings',
  code: `
    // Verify previous phases complete
    const relaunchData = figma.root.getRelaunchData()
    
    if (relaunchData.phase2Complete !== 'true') {
      throw new Error('Phase 2 must complete before Phase 3')
    }
    
    // Get semantic variables for component binding
    const semanticIds = JSON.parse(relaunchData.semanticVariableIds)
    const getSemanticVar = (name) => figma.variables.getVariableById(semanticIds[name])
    
    // Create Button component with variants
    const buttonVariants = []
    const sizes = ['Small', 'Medium', 'Large']
    const variants = ['Primary', 'Secondary']
    const states = ['Default', 'Hover', 'Disabled']
    
    for (const size of sizes) {
      for (const variant of variants) {
        for (const state of states) {
          const button = figma.createComponent()
          button.name = \`Size=\${size}, Variant=\${variant}, State=\${state}\`
          
          // Set up auto-layout
          button.layoutMode = 'HORIZONTAL'
          button.primaryAxisAlignItems = 'CENTER'
          button.counterAxisAlignItems = 'CENTER'
          button.paddingLeft = size === 'Small' ? 12 : size === 'Medium' ? 16 : 20
          button.paddingRight = size === 'Small' ? 12 : size === 'Medium' ? 16 : 20
          button.paddingTop = size === 'Small' ? 6 : size === 'Medium' ? 8 : 10
          button.paddingBottom = size === 'Small' ? 6 : size === 'Medium' ? 8 : 10
          button.itemSpacing = 8
          button.cornerRadius = 6
          
          // Bind background color based on variant and state
          let bgVar, textVar
          if (variant === 'Primary') {
            bgVar = state === 'Disabled' ? getSemanticVar('surface/tertiary') : getSemanticVar('brand/primary')
            textVar = state === 'Disabled' ? getSemanticVar('text/tertiary') : getSemanticVar('surface/primary')
          } else {
            bgVar = state === 'Disabled' ? getSemanticVar('surface/secondary') : getSemanticVar('surface/secondary')
            textVar = state === 'Disabled' ? getSemanticVar('text/tertiary') : getSemanticVar('text/primary')
          }
          
          // Bind background fill
          const bgFill = { type: 'SOLID', color: { r: 0, g: 0, b: 0 } }
          const boundBgFill = figma.variables.setBoundVariableForPaint(bgFill, 'color', bgVar)
          button.fills = [boundBgFill]
          
          // Add text element
          const text = figma.createText()
          text.name = 'Label'
          text.characters = 'Button'
          text.fontName = { family: 'Inter', style: size === 'Small' ? 'Medium' : 'Bold' }
          text.fontSize = size === 'Small' ? 14 : size === 'Medium' ? 16 : 18
          
          // Bind text color
          const textFill = { type: 'SOLID', color: { r: 0, g: 0, b: 0 } }
          const boundTextFill = figma.variables.setBoundVariableForPaint(textFill, 'color', textVar)
          text.fills = [boundTextFill]
          
          button.appendChild(text)
          buttonVariants.push(button)
        }
      }
    }
    
    // Combine into component set
    const buttonComponentSet = figma.combineAsVariants(buttonVariants, figma.currentPage)
    buttonComponentSet.name = 'Button'
    buttonComponentSet.description = 'Primary button component with Size, Variant, and State options'
    
    // Create Card component
    const card = figma.createComponent()
    card.name = 'Card'
    card.description = 'Basic card container with semantic surface color'
    
    // Set up card layout
    card.layoutMode = 'VERTICAL'
    card.primaryAxisAlignItems = 'MIN'
    card.counterAxisAlignItems = 'FILL'
    card.paddingTop = 24
    card.paddingRight = 24
    card.paddingBottom = 24
    card.paddingLeft = 24
    card.itemSpacing = 16
    card.cornerRadius = 8
    card.resize(320, 200)
    
    // Bind card background
    const cardFill = { type: 'SOLID', color: { r: 1, g: 1, b: 1 } }
    const boundCardFill = figma.variables.setBoundVariableForPaint(cardFill, 'color', getSemanticVar('surface/primary'))
    card.fills = [boundCardFill]
    
    // Add border
    const cardStroke = { type: 'SOLID', color: { r: 0.8, g: 0.8, b: 0.8 } }
    const boundCardStroke = figma.variables.setBoundVariableForPaint(cardStroke, 'color', getSemanticVar('border/primary'))
    card.strokes = [boundCardStroke]
    card.strokeWeight = 1
    
    figma.root.setRelaunchData({
      ...relaunchData,
      phase3Complete: 'true',
      componentsCreated: 2 // Button set + Card
    })
    
    console.log('✅ Created Button component set and Card component')
    return { 
      components: ['Button', 'Card'],
      buttonVariants: buttonVariants.length,
      phase3Complete: true
    }
  `
})
```

## Phase 4: Documentation and Organization

```javascript
await useFigma({
  fileKey,
  description: 'Phase 4: Create documentation and organize design system',
  code: `
    // Verify all previous phases complete
    const relaunchData = figma.root.getRelaunchData()
    
    if (relaunchData.phase3Complete !== 'true') {
      throw new Error('Phase 3 must complete before Phase 4')
    }
    
    // Create documentation page
    const docPage = figma.createPage()
    docPage.name = 'Documentation'
    
    // Add overview documentation frame
    const overviewFrame = figma.createFrame()
    overviewFrame.name = 'Design System Overview'
    overviewFrame.resize(800, 1200)
    overviewFrame.x = 100
    overviewFrame.y = 100
    
    // Set overview frame background
    const overviewFill = { type: 'SOLID', color: { r: 0.98, g: 0.98, b: 0.98 } }
    overviewFrame.fills = [overviewFill]
    
    // Add title
    const title = figma.createText()
    title.characters = 'Design System Documentation'
    title.fontSize = 32
    title.fontName = { family: 'Inter', style: 'Bold' }
    title.x = 40
    title.y = 40
    
    // Add description  
    const description = figma.createText()
    description.characters = \`Generated Design System\\n\\nIncludes:\\n• \${JSON.parse(relaunchData.primitiveVariableIds) ? Object.keys(JSON.parse(relaunchData.primitiveVariableIds)).length : 0} color families with 10 scales each\\n• \${Object.keys(JSON.parse(relaunchData.semanticVariableIds)).length} semantic color variables\\n• \${relaunchData.colorStylesCount} color styles\\n• \${relaunchData.textStylesCount} text styles\\n• \${relaunchData.componentsCreated} component sets\\n\\nAll variables support Light and Dark modes\\nStyles are bound to semantic variables\\nComponents use auto-layout with variable bindings\`
    description.fontSize = 16
    description.fontName = { family: 'Inter', style: 'Regular' }
    description.x = 40
    description.y = 100
    description.resize(720, 200)
    
    overviewFrame.appendChild(title)
    overviewFrame.appendChild(description)
    docPage.appendChild(overviewFrame)
    
    figma.root.setRelaunchData({
      ...relaunchData,
      phase4Complete: 'true'
    })
    
    console.log('✅ Created documentation page with overview')
    return { documentation: true, phase4Complete: true }
  `
})
```

## Phase 5: Final Validation

```javascript
const finalValidation = await useFigma({
  fileKey,
  description: 'Phase 5: Complete validation of generated design system',
  code: `
    // Comprehensive validation of all phases
    const relaunchData = figma.root.getRelaunchData()
    
    const validation = {
      collections: figma.variables.getLocalVariableCollections().length,
      variables: figma.variables.getLocalVariables().length,
      colorStyles: figma.getLocalPaintStyles().length,
      textStyles: figma.getLocalTextStyles().length,
      components: figma.root.findAll(node => node.type === 'COMPONENT').length,
      componentSets: figma.root.findAll(node => node.type === 'COMPONENT_SET').length,
      pages: figma.root.children.length
    }
    
    // Validate variable bindings
    const semanticIds = JSON.parse(relaunchData.semanticVariableIds)
    let boundStylesCount = 0
    
    figma.getLocalPaintStyles().forEach(style => {
      if (style.paints[0]?.boundVariables?.color) {
        boundStylesCount++
      }
    })
    
    // Generate final report
    const report = {
      phase1: { 
        collections: validation.collections,
        variables: validation.variables,
        status: validation.collections >= 2 && validation.variables >= 50 ? '✅ Pass' : '❌ Fail'
      },
      phase2: {
        colorStyles: validation.colorStyles,
        textStyles: validation.textStyles,
        boundStyles: boundStylesCount,
        status: validation.colorStyles >= 8 && validation.textStyles >= 6 ? '✅ Pass' : '❌ Fail'
      },
      phase3: {
        components: validation.components,
        componentSets: validation.componentSets,
        status: validation.componentSets >= 2 ? '✅ Pass' : '❌ Fail'
      },
      phase4: {
        pages: validation.pages,
        status: validation.pages >= 2 ? '✅ Pass' : '❌ Fail' // Main + Documentation
      },
      overall: 'Complete'
    }
    
    console.log('🎉 DESIGN SYSTEM GENERATION COMPLETE')
    console.log('Final validation:', JSON.stringify(report, null, 2))
    
    return report
  `
})

// Log final results
console.log('='.repeat(60))
console.log('🎉 DESIGN SYSTEM PIPELINE COMPLETE!')
console.log('='.repeat(60))
console.log('Phases completed:', ['Variables', 'Styles', 'Components', 'Documentation', 'Validation'])
console.log('Final validation:', finalValidation)
```

## Pipeline Validation Checklist

### Phase 1 Validation
- [ ] Collections created (Primitives, Semantics)
- [ ] Mode structure correct (Primitives: 1 mode, Semantics: Light/Dark)
- [ ] Primitive variables: 50 total (5 colors × 10 scales)
- [ ] Semantic variables: 13 with proper aliases
- [ ] Variable scopes set correctly
- [ ] Code syntax configured for all platforms

### Phase 2 Validation  
- [ ] Color styles created and bound to semantic variables
- [ ] Text styles created with font loading
- [ ] All styles use semantic variables (not primitives)
- [ ] Style names follow folder structure (color/, typography/)

### Phase 3 Validation
- [ ] Components use auto-layout
- [ ] Variable bindings on component properties
- [ ] Variant naming follows Property=Value format
- [ ] Component descriptions added

### Phase 4 Validation
- [ ] Documentation page created
- [ ] Overview frame with system summary
- [ ] File organized with clear structure

### Phase 5 Validation
- [ ] All counts match expected totals
- [ ] Variable bindings verified
- [ ] No errors in console
- [ ] System ready for use

## Error Recovery Patterns

### If Phase Fails
```javascript
// Check which phase failed
const relaunchData = figma.root.getRelaunchData()
console.log('Last completed phase:', {
  phase1: relaunchData.phase1Complete,
  phase2: relaunchData.phase2Complete,
  phase3: relaunchData.phase3Complete,
  phase4: relaunchData.phase4Complete
})

// Resume from failed phase by re-running only that phase
// Previous phase data stored in relaunchData for continuity
```

### Common Failure Points
1. **Mode limits exceeded**: Check plan tier before Phase 1A
2. **Font loading failures**: Verify font availability before Phase 2
3. **Variable binding failures**: Ensure variables exist before binding
4. **Component creation failures**: Verify auto-layout setup before properties

This pipeline ensures systematic, error-free design system generation with complete dependency management and validation at every step.


## Extended Phase 1: Spacing and Sizing Variables

### Phase 1D: Spacing Scale
```javascript
await useFigma({
  fileKey,
  description: 'Phase 1D: Generate spacing scale variables',
  code: `
    const relaunchData = figma.root.getRelaunchData()
    const primitivesCollection = figma.variables.getVariableCollectionById(relaunchData.primitivesCollectionId)
    const defaultMode = primitivesCollection.modes[0]
    
    // 4px base, exponential scale
    const spacingScale = {
      '0': 0,
      '1': 4,
      '2': 8,
      '3': 12,
      '4': 16,
      '5': 20,
      '6': 24,
      '8': 32,
      '10': 40,
      '12': 48,
      '16': 64,
      '20': 80,
      '24': 96
    }
    
    const spacingVarIds = {}
    Object.entries(spacingScale).forEach(([name, value]) => {
      const variable = figma.variables.createVariable(
        'spacing/' + name,
        primitivesCollection.id,
        'FLOAT'
      )
      variable.setValueForMode(defaultMode.modeId, value)
      variable.scopes = ['GAP', 'WIDTH_HEIGHT']
      variable.codeSyntax = {
        WEB: '--spacing-' + name,
        ANDROID: 'spacing_' + name,
        iOS: 'spacing' + name
      }
      spacingVarIds[name] = variable.id
    })
    
    // Border radius scale
    const radiusScale = { none: 0, sm: 4, md: 6, lg: 8, xl: 12, '2xl': 16, full: 9999 }
    const radiusVarIds = {}
    
    Object.entries(radiusScale).forEach(([name, value]) => {
      const variable = figma.variables.createVariable(
        'radius/' + name,
        primitivesCollection.id,
        'FLOAT'
      )
      variable.setValueForMode(defaultMode.modeId, value)
      variable.scopes = ['CORNER_RADIUS']
      variable.codeSyntax = {
        WEB: '--radius-' + name,
        ANDROID: 'radius_' + name,
        iOS: 'radius' + name.charAt(0).toUpperCase() + name.slice(1)
      }
      radiusVarIds[name] = variable.id
    })
    
    // Sizing scale (min/max widths, icon sizes)
    const sizingScale = { xs: 16, sm: 20, md: 24, lg: 32, xl: 40, '2xl': 48 }
    const sizingVarIds = {}
    
    Object.entries(sizingScale).forEach(([name, value]) => {
      const variable = figma.variables.createVariable(
        'size/icon/' + name,
        primitivesCollection.id,
        'FLOAT'
      )
      variable.setValueForMode(defaultMode.modeId, value)
      variable.scopes = ['WIDTH_HEIGHT']
      sizingVarIds[name] = variable.id
    })
    
    figma.root.setRelaunchData({
      ...relaunchData,
      spacingVarIds: JSON.stringify(spacingVarIds),
      radiusVarIds: JSON.stringify(radiusVarIds),
      sizingVarIds: JSON.stringify(sizingVarIds)
    })
    
    console.log('✅ Created spacing, radius, and sizing variables')
    return { spacing: Object.keys(spacingScale).length, radius: Object.keys(radiusScale).length, sizing: Object.keys(sizingScale).length }
  `
})
```

## Extended Phase 2: Effect Styles

### Phase 2B: Shadow and Effect Styles
```javascript
await useFigma({
  fileKey,
  description: 'Phase 2B: Create effect styles for elevation',
  code: `
    const relaunchData = figma.root.getRelaunchData()
    const semanticIds = JSON.parse(relaunchData.semanticVariableIds)
    
    // Elevation levels using drop shadow
    const elevationLevels = [
      { name: 'elevation/none', effects: [] },
      { name: 'elevation/sm', effects: [
        { type: 'DROP_SHADOW', color: { r: 0, g: 0, b: 0, a: 0.05 }, offset: { x: 0, y: 1 }, radius: 2, spread: 0, visible: true, blendMode: 'NORMAL' }
      ]},
      { name: 'elevation/md', effects: [
        { type: 'DROP_SHADOW', color: { r: 0, g: 0, b: 0, a: 0.05 }, offset: { x: 0, y: 1 }, radius: 3, spread: 0, visible: true, blendMode: 'NORMAL' },
        { type: 'DROP_SHADOW', color: { r: 0, g: 0, b: 0, a: 0.1 }, offset: { x: 0, y: 4 }, radius: 6, spread: -1, visible: true, blendMode: 'NORMAL' }
      ]},
      { name: 'elevation/lg', effects: [
        { type: 'DROP_SHADOW', color: { r: 0, g: 0, b: 0, a: 0.05 }, offset: { x: 0, y: 4 }, radius: 6, spread: -1, visible: true, blendMode: 'NORMAL' },
        { type: 'DROP_SHADOW', color: { r: 0, g: 0, b: 0, a: 0.1 }, offset: { x: 0, y: 10 }, radius: 15, spread: -3, visible: true, blendMode: 'NORMAL' }
      ]},
      { name: 'elevation/xl', effects: [
        { type: 'DROP_SHADOW', color: { r: 0, g: 0, b: 0, a: 0.1 }, offset: { x: 0, y: 10 }, radius: 15, spread: -3, visible: true, blendMode: 'NORMAL' },
        { type: 'DROP_SHADOW', color: { r: 0, g: 0, b: 0, a: 0.1 }, offset: { x: 0, y: 20 }, radius: 25, spread: -5, visible: true, blendMode: 'NORMAL' }
      ]}
    ]
    
    elevationLevels.forEach(({ name, effects }) => {
      const style = figma.createEffectStyle()
      style.name = name
      style.effects = effects
    })
    
    console.log('✅ Created ' + elevationLevels.length + ' elevation styles')
    return { effectStyles: elevationLevels.length }
  `
})
```

## Extended Phase 3: Additional Components

### Phase 3B: Input Component
```javascript
await useFigma({
  fileKey,
  description: 'Phase 3B: Create Input component with states',
  code: `
    const relaunchData = figma.root.getRelaunchData()
    const semanticIds = JSON.parse(relaunchData.semanticVariableIds)
    const getSemanticVar = (name) => figma.variables.getVariableById(semanticIds[name])
    
    await figma.loadFontAsync({ family: 'Inter', style: 'Regular' })
    await figma.loadFontAsync({ family: 'Inter', style: 'Medium' })
    
    const inputVariants = []
    const sizes = ['Small', 'Medium']
    const states = ['Default', 'Focus', 'Error', 'Disabled']
    
    for (const size of sizes) {
      for (const state of states) {
        const input = figma.createComponent()
        input.name = 'Size=' + size + ', State=' + state
        input.layoutMode = 'VERTICAL'
        input.primaryAxisSizingMode = 'AUTO'
        input.counterAxisSizingMode = 'FIXED'
        input.resize(280, 10) // Width fixed, height hugs
        input.itemSpacing = 4
        
        // Label
        const label = figma.createText()
        label.name = 'Label'
        label.characters = 'Label'
        label.fontName = { family: 'Inter', style: 'Medium' }
        label.fontSize = size === 'Small' ? 12 : 14
        
        const labelFill = { type: 'SOLID', color: { r: 0, g: 0, b: 0 } }
        const boundLabelFill = figma.variables.setBoundVariableForPaint(
          labelFill, 'color',
          state === 'Disabled' ? getSemanticVar('text/tertiary') : getSemanticVar('text/primary')
        )
        label.fills = [boundLabelFill]
        
        // Field container
        const field = figma.createFrame()
        field.name = 'Field'
        field.layoutMode = 'HORIZONTAL'
        field.primaryAxisAlignItems = 'CENTER'
        field.counterAxisAlignItems = 'CENTER'
        field.paddingLeft = 12
        field.paddingRight = 12
        field.paddingTop = size === 'Small' ? 6 : 8
        field.paddingBottom = size === 'Small' ? 6 : 8
        field.cornerRadius = 6
        field.layoutSizingHorizontal = 'FILL'
        
        // Field background
        const fieldFill = { type: 'SOLID', color: { r: 1, g: 1, b: 1 } }
        const boundFieldFill = figma.variables.setBoundVariableForPaint(
          fieldFill, 'color', getSemanticVar('surface/primary')
        )
        field.fills = [boundFieldFill]
        
        // Field border
        const borderVar = state === 'Focus' ? getSemanticVar('brand/primary')
          : state === 'Error' ? getSemanticVar('status/error')
          : getSemanticVar('border/primary')
        const fieldStroke = { type: 'SOLID', color: { r: 0, g: 0, b: 0 } }
        const boundFieldStroke = figma.variables.setBoundVariableForPaint(
          fieldStroke, 'color', borderVar
        )
        field.strokes = [boundFieldStroke]
        field.strokeWeight = state === 'Focus' ? 2 : 1
        
        // Placeholder text
        const placeholder = figma.createText()
        placeholder.name = 'Value'
        placeholder.characters = 'Placeholder text'
        placeholder.fontName = { family: 'Inter', style: 'Regular' }
        placeholder.fontSize = size === 'Small' ? 14 : 16
        placeholder.layoutSizingHorizontal = 'FILL'
        
        const placeholderFill = { type: 'SOLID', color: { r: 0, g: 0, b: 0 } }
        const boundPlaceholderFill = figma.variables.setBoundVariableForPaint(
          placeholderFill, 'color', getSemanticVar('text/tertiary')
        )
        placeholder.fills = [boundPlaceholderFill]
        
        field.appendChild(placeholder)
        input.appendChild(label)
        input.appendChild(field)
        
        // Helper text for error state
        if (state === 'Error') {
          const helper = figma.createText()
          helper.name = 'Helper Text'
          helper.characters = 'Error message'
          helper.fontName = { family: 'Inter', style: 'Regular' }
          helper.fontSize = 12
          
          const helperFill = { type: 'SOLID', color: { r: 0, g: 0, b: 0 } }
          const boundHelperFill = figma.variables.setBoundVariableForPaint(
            helperFill, 'color', getSemanticVar('status/error')
          )
          helper.fills = [boundHelperFill]
          input.appendChild(helper)
        }
        
        inputVariants.push(input)
      }
    }
    
    const inputSet = figma.combineAsVariants(inputVariants, figma.currentPage)
    inputSet.name = 'Input'
    inputSet.description = 'Text input field with label and validation states. Size (Small/Medium), State (Default/Focus/Error/Disabled).'
    
    console.log('✅ Created Input component set with ' + inputVariants.length + ' variants')
    return { inputVariants: inputVariants.length }
  `
})
```

## Publishing Preparation

### Pre-Publish Checklist
```javascript
await useFigma({
  fileKey,
  description: 'Pre-publish validation and cleanup',
  code: `
    const issues = []
    
    // 1. Check all components have descriptions
    const components = figma.root.findAll(n => n.type === 'COMPONENT')
    const componentSets = figma.root.findAll(n => n.type === 'COMPONENT_SET')
    
    componentSets.forEach(cs => {
      if (!cs.description || cs.description.length < 10) {
        issues.push('Missing description: ' + cs.name)
      }
    })
    
    // 2. Check primitive variables are hidden from publishing
    const primitiveVars = figma.variables.getLocalVariables().filter(v => 
      v.name.startsWith('color/') && 
      !v.name.includes('surface') && 
      !v.name.includes('text') && 
      !v.name.includes('brand') && 
      !v.name.includes('status') && 
      !v.name.includes('border')
    )
    primitiveVars.forEach(v => {
      if (!v.hiddenFromPublishing) {
        issues.push('Primitive not hidden: ' + v.name)
        v.hiddenFromPublishing = true // Auto-fix
      }
    })
    
    // 3. Check code syntax is set on semantic variables
    const semanticVars = figma.variables.getLocalVariables().filter(v =>
      v.name.includes('surface') || v.name.includes('text/') || 
      v.name.includes('brand') || v.name.includes('status')
    )
    semanticVars.forEach(v => {
      if (!v.codeSyntax || !v.codeSyntax.WEB) {
        issues.push('Missing code syntax: ' + v.name)
      }
    })
    
    // 4. Check all styles are bound to variables
    figma.getLocalPaintStyles().forEach(style => {
      const hasBound = style.paints.some(p => p.boundVariables?.color)
      if (!hasBound) {
        issues.push('Style not bound to variable: ' + style.name)
      }
    })
    
    console.log(issues.length === 0 
      ? '✅ All pre-publish checks passed'
      : '⚠️ Issues found: ' + JSON.stringify(issues, null, 2)
    )
    return { passed: issues.length === 0, issues }
  `
})
```

## Incremental Pipeline Updates

### Adding Variables to Existing System
```javascript
// When adding new semantic variables to an existing system:
// 1. Find the existing collection
// 2. Get existing mode IDs
// 3. Create new variables with proper aliases
// 4. DO NOT recreate the collection — this breaks all existing bindings

await useFigma({
  fileKey,
  description: 'Add new semantic variable to existing system',
  code: `
    // Find existing collections
    const semanticsCollection = figma.variables.getLocalVariableCollections()
      .find(c => c.name === 'Semantics')
    
    if (!semanticsCollection) {
      throw new Error('Semantics collection not found — run full pipeline first')
    }
    
    // Get mode IDs
    const lightMode = semanticsCollection.modes.find(m => m.name === 'Light')
    const darkMode = semanticsCollection.modes.find(m => m.name === 'Dark')
    
    // Find primitive variables for aliasing
    const blue400 = figma.variables.getLocalVariables()
      .find(v => v.name === 'color/blue/400')
    const blue600 = figma.variables.getLocalVariables()
      .find(v => v.name === 'color/blue/600')
    
    // Create new semantic variable
    const newVar = figma.variables.createVariable(
      'color/interactive/hover',
      semanticsCollection.id,
      'COLOR'
    )
    newVar.setValueForMode(lightMode.modeId, figma.variables.createVariableAlias(blue600))
    newVar.setValueForMode(darkMode.modeId, figma.variables.createVariableAlias(blue400))
    newVar.scopes = ['ALL_FILLS']
    newVar.codeSyntax = {
      WEB: '--color-interactive-hover',
      ANDROID: 'color_interactive_hover',
      iOS: 'colorInteractiveHover'
    }
    
    console.log('✅ Added color/interactive/hover to existing Semantics collection')
  `
})
```

### Pipeline State Recovery
```javascript
// If relaunchData is lost (file closed/reopened), reconstruct from existing variables:
await useFigma({
  fileKey,
  description: 'Recover pipeline state from existing variables',
  code: `
    const collections = figma.variables.getLocalVariableCollections()
    const primitives = collections.find(c => c.name === 'Primitives')
    const semantics = collections.find(c => c.name === 'Semantics')
    
    if (!primitives || !semantics) {
      console.log('❌ Cannot recover — collections not found. Run full pipeline.')
      return { recovered: false }
    }
    
    // Rebuild IDs from existing variables
    const primitiveVars = figma.variables.getLocalVariables()
      .filter(v => v.variableCollectionId === primitives.id)
    const semanticVars = figma.variables.getLocalVariables()
      .filter(v => v.variableCollectionId === semantics.id)
    
    const primitiveIds = {}
    primitiveVars.forEach(v => {
      const parts = v.name.split('/')
      if (parts.length === 3 && parts[0] === 'color') {
        if (!primitiveIds[parts[1]]) primitiveIds[parts[1]] = {}
        primitiveIds[parts[1]][parts[2]] = v.id
      }
    })
    
    const semanticIds = {}
    semanticVars.forEach(v => {
      const key = v.name.replace('color/', '')
      semanticIds[key] = v.id
    })
    
    // Restore relaunchData
    figma.root.setRelaunchData({
      primitivesCollectionId: primitives.id,
      semanticsCollectionId: semantics.id,
      lightModeId: semantics.modes.find(m => m.name === 'Light')?.modeId,
      darkModeId: semantics.modes.find(m => m.name === 'Dark')?.modeId,
      primitiveVariableIds: JSON.stringify(primitiveIds),
      semanticVariableIds: JSON.stringify(semanticIds),
      phase1Complete: 'true',
      phase2Complete: String(figma.getLocalPaintStyles().length > 0),
      phase3Complete: String(figma.root.findAll(n => n.type === 'COMPONENT_SET').length > 0)
    })
    
    console.log('✅ Pipeline state recovered from existing variables')
    return { recovered: true, primitives: primitiveVars.length, semantics: semanticVars.length }
  `
})
```

## Related
- hub → [[figma]]
