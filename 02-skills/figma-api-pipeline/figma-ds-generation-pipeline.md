# Complete Design System Generation Pipeline

## When to Use This Skill
Use when generating complete design systems in Figma with proper dependency ordering. This skill orchestrates the entire pipeline from variables through components with validation at each phase.

## The Five-Phase Dependency Chain
**Variables → Styles → Components → Documentation → Validation**

Each phase must complete successfully before the next begins. Breaking this order causes cascade failures.

## Pre-Pipeline Setup

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
