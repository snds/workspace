# Figma Component and Variant Generation

## When to Use This Skill
Use when creating Figma components, component sets, variants, or any structured component system. This skill covers component creation, variant combinations, and auto-layout best practices.

## Component Creation Fundamentals

### Basic Component Pattern
```javascript
// Create component
const component = figma.createComponent()
component.name = 'Button' // Component name
component.description = 'Primary action button with multiple states and sizes'

// Set up auto-layout (recommended for all components)
component.layoutMode = 'HORIZONTAL' // or 'VERTICAL'
component.primaryAxisAlignItems = 'CENTER' // or 'MIN', 'MAX'
component.counterAxisAlignItems = 'CENTER' // or 'MIN', 'MAX'
component.paddingLeft = 16
component.paddingRight = 16
component.paddingTop = 8
component.paddingBottom = 8
component.itemSpacing = 8 // Gap between children
```

### Component Best Practices
- **Always use auto-layout**: Enables responsive behavior and proper nesting
- **Set explicit padding**: Don't rely on child margins
- **Use itemSpacing for gaps**: More reliable than child spacing
- **Bind spacing to variables**: Ensures consistency across components

## Variant Creation Workflow

### Step 1: Create Individual Components
```javascript
const variants = []

// Create all variant combinations
const sizes = ['Small', 'Medium', 'Large']
const states = ['Default', 'Hover', 'Disabled'] 
const types = ['Primary', 'Secondary']

for (const size of sizes) {
  for (const state of states) {
    for (const type of types) {
      const variant = figma.createComponent()
      
      // CRITICAL: Name must use Property=Value format
      variant.name = `Size=${size}, State=${state}, Type=${type}`
      
      // Configure variant appearance
      setupVariantAppearance(variant, size, state, type)
      
      variants.push(variant)
    }
  }
}
```

### Step 2: Combine as Variant Set
```javascript
// Combine all variants into component set
const componentSet = figma.combineAsVariants(variants, figma.currentPage)
componentSet.name = 'Button' // Component set name

// Add description to component set
componentSet.description = 'Button component with Size, State, and Type variants'
```

## Variant Property Parsing Rules

### Property Naming Format
- **Format**: `Property=Value, Property=Value`
- **Separator**: Comma + space (`, `)
- **Assignment**: Equals sign (`=`)
- **Case sensitive**: `Size=Large` ≠ `size=large`

### Valid Property Examples
```javascript
// ✅ CORRECT
'Size=Small, State=Default'
'Type=Primary, Size=Large, Disabled=True'
'Variant=Icon, Size=24, Color=Primary'

// ❌ WRONG
'Size: Small, State: Default' // Wrong separator
'Size=Small,State=Default'    // Missing space
'size=small'                  // Wrong case
```

## Auto-Layout Configuration

### Layout Direction
```javascript
// Horizontal layout (side-by-side children)
component.layoutMode = 'HORIZONTAL'
component.primaryAxisAlignItems = 'CENTER'    // Horizontal alignment
component.counterAxisAlignItems = 'CENTER'    // Vertical alignment

// Vertical layout (stacked children)  
component.layoutMode = 'VERTICAL'
component.primaryAxisAlignItems = 'CENTER'    // Vertical alignment
component.counterAxisAlignItems = 'CENTER'    // Horizontal alignment
```

### Spacing and Padding
```javascript
// Internal spacing
component.itemSpacing = 8           // Gap between children
component.counterAxisSpacing = 4    // Cross-axis gap (grid layouts)

// External padding
component.paddingTop = 12
component.paddingRight = 16
component.paddingBottom = 12
component.paddingLeft = 16

// Bind to variables for consistency
component.setBoundVariable('itemSpacing', gapSpacingVar)
component.setBoundVariable('paddingLeft', paddingXVar)
```

### Sizing Behavior
```javascript
// Fixed size
component.resize(200, 40)

// Hug contents (shrinks to fit)
component.primaryAxisSizingMode = 'AUTO'    // Hug width
component.counterAxisSizingMode = 'AUTO'    // Hug height

// Fill container (expands to fill)
component.primaryAxisSizingMode = 'FILL'    // Fill width
component.counterAxisSizingMode = 'FILL'    // Fill height

// Mixed: hug height, fill width
component.primaryAxisSizingMode = 'FILL'
component.counterAxisSizingMode = 'AUTO'
```

## Variable Binding in Components

### Bind Layout Properties
```javascript
// Spacing variables
component.setBoundVariable('itemSpacing', spacingMdVar)
component.setBoundVariable('paddingTop', spacingSmVar)
component.setBoundVariable('paddingLeft', spacingLgVar)

// Border radius
component.setBoundVariable('cornerRadius', radiusMdVar)

// Size constraints  
component.setBoundVariable('minWidth', buttonMinWidthVar)
component.setBoundVariable('maxWidth', buttonMaxWidthVar)
```

### Bind Appearance Properties
```javascript
// Fill color (requires immutability pattern)
const fills = [...component.fills]
fills[0] = figma.variables.setBoundVariableForPaint(fills[0], 'color', primaryColorVar)
component.fills = fills

// Stroke
component.setBoundVariable('strokeWeight', borderWidthVar)
const strokes = [...component.strokes]
strokes[0] = figma.variables.setBoundVariableForPaint(strokes[0], 'color', borderColorVar)
component.strokes = strokes
```

## Text Element Configuration

### Text Setup in Components
```javascript
// Load font first
await figma.loadFontAsync({ family: 'Inter', style: 'Medium' })

// Create and configure text
const textNode = figma.createText()
textNode.name = 'Label'
textNode.characters = 'Button Text'
textNode.fontName = { family: 'Inter', style: 'Medium' }

// Bind text properties
textNode.setBoundVariable('fontSize', buttonFontSizeVar)
textNode.setBoundVariable('fontFamily', buttonFontFamilyVar)

// Bind text color
const textFills = [...textNode.fills]
textFills[0] = figma.variables.setBoundVariableForPaint(textFills[0], 'color', textColorVar)
textNode.fills = textFills

// Add to component
component.appendChild(textNode)
```

## Component Organization

### Naming Conventions
```javascript
// Component names
'Button'                    // Base component
'Input Field'              // Multi-word components
'Icon/Arrow/Right'         // Hierarchical organization

// Component set names (same as base component name)
componentSet.name = 'Button'  // Not 'Button Variants'
```

### Library Publishing
```javascript
// Mark for publishing
component.description = 'Primary action button for forms and CTAs'
component.documentationLinks = [
  { uri: 'https://designsystem.com/button', name: 'Documentation' }
]

// Hide from library if needed
component.remote = false // Keeps local, doesn't publish
```

## Common Component Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Cannot combine variants" | Components not on same page | Move to same page first |
| "Invalid variant property format" | Wrong naming syntax | Use `Property=Value, Property=Value` |
| "Cannot set layoutMode" | Trying to set on text/primitive | Only frames/components support auto-layout |
| "Cannot set itemSpacing on non-auto-layout" | Missing layoutMode | Set `layoutMode = 'HORIZONTAL'` or `'VERTICAL'` first |
| Variants don't update properly | Missing property combinations | Ensure all combinations exist |

## Component Validation Checklist

- [ ] Auto-layout configured (`layoutMode` set)
- [ ] Padding and spacing defined
- [ ] Variables bound to layout properties
- [ ] Fill/stroke variables bound with immutability pattern
- [ ] Text fonts loaded before modification
- [ ] Variant naming follows `Property=Value` format
- [ ] All variant combinations created
- [ ] Component description added
- [ ] Documentation links provided (if applicable)

## Advanced: Instance Creation and Swapping

### Create Instance
```javascript
// Create instance of component
const instance = component.createInstance()

// Set variant properties
instance.setProperties({ Size: 'Large', State: 'Hover' })

// Override text content
const textChild = instance.findOne(node => node.type === 'TEXT')
textChild.characters = 'Custom Label'
```

### Component Swapping  
```javascript
// Swap instance to different component
instance.swapComponent(newComponent)

// Preserve overrides during swap
instance.swapComponent(newComponent, { preserveOverrides: true })
```

## Performance Considerations

### Efficient Variant Generation
```javascript
// Generate variants in batches to avoid memory issues
const batchSize = 20
const allCombinations = generateAllCombinations() // Your logic

for (let i = 0; i < allCombinations.length; i += batchSize) {
  const batch = allCombinations.slice(i, i + batchSize)
  const batchVariants = batch.map(combo => createVariantComponent(combo))
  
  // Process batch
  if (batchVariants.length > 0) {
    variants.push(...batchVariants)
  }
}
```

### Memory Management
- Create variants in small batches (20-50 at a time)
- Clean up temporary nodes after component creation
- Use `figma.skipInvisibleInstanceChildren = true` for performance
- Consider using instance swapping instead of creating many variants


## Component Properties API

### Exposing Properties on Components
Component properties allow consumers to customize instances without overriding layers directly. These are the Figma-native mechanism for controlled customization.

```javascript
// Boolean property — show/hide child layers
component.addComponentProperty('showIcon', 'BOOLEAN', true)

// Text property — expose a text override
const textNode = component.findOne(n => n.type === 'TEXT' && n.name === 'Label')
component.addComponentProperty('label', 'TEXT', 'Default text')
textNode.componentPropertyReferences = { characters: 'label' }

// Instance swap property — expose a slot for child component
component.addComponentProperty('leadingIcon', 'INSTANCE_SWAP', defaultIconComponent.key)

// Variant property — this is automatic from variant naming
// No API call needed; Figma parses Property=Value from variant names
```

### Boolean Property Visibility Binding
```javascript
// Create icon layer
const iconFrame = figma.createFrame()
iconFrame.name = 'Icon'

// Create boolean property
const propId = component.addComponentProperty('showIcon', 'BOOLEAN', true)

// Bind layer visibility to property
iconFrame.componentPropertyReferences = { visible: propId }
component.appendChild(iconFrame)
```

### Instance Swap Property (Pre-Slots Pattern)
```javascript
// Create swap property with default component
const swapPropId = component.addComponentProperty(
  'icon',
  'INSTANCE_SWAP',
  defaultIconComponent.key
)

// Create placeholder instance
const iconInstance = defaultIconComponent.createInstance()
iconInstance.name = 'Icon'
iconInstance.componentPropertyReferences = { mainComponent: swapPropId }
component.appendChild(iconInstance)
```

### Preferred Values for Instance Swap
```javascript
// Curate the swap dropdown to show only relevant components
component.editComponentProperty('icon', {
  preferredValues: [
    { type: 'COMPONENT', key: arrowIcon.key },
    { type: 'COMPONENT', key: checkIcon.key },
    { type: 'COMPONENT', key: closeIcon.key },
    { type: 'COMPONENT_SET', key: iconSet.key } // Entire set
  ]
})
```

## Nested Component Patterns

### Compound Component with Parts
```javascript
// Inner component (e.g., ListItem)
const listItem = figma.createComponent()
listItem.name = 'ListItem'
listItem.layoutMode = 'HORIZONTAL'
listItem.primaryAxisAlignItems = 'CENTER'
listItem.counterAxisAlignItems = 'CENTER'
listItem.paddingLeft = 16
listItem.paddingRight = 16
listItem.paddingTop = 12
listItem.paddingBottom = 12

// Load font first
await figma.loadFontAsync({ family: 'Inter', style: 'Regular' })

const itemText = figma.createText()
itemText.characters = 'List Item'
itemText.fontName = { family: 'Inter', style: 'Regular' }
listItem.appendChild(itemText)

// Outer component (e.g., List)
const list = figma.createComponent()
list.name = 'List'
list.layoutMode = 'VERTICAL'
list.primaryAxisSizingMode = 'AUTO'
list.counterAxisSizingMode = 'FIXED'
list.resize(320, 10) // Width fixed, height hugs
list.itemSpacing = 0

// Add instances of inner component
for (let i = 0; i < 3; i++) {
  const instance = listItem.createInstance()
  list.appendChild(instance)
}
```

### Nesting Depth Rule
Keep component nesting to **3 levels maximum**. Each level of nesting multiplies
the cost of cascading property updates. Deep nesting also makes instances harder
to override and increases memory consumption in large files.

```
✅ Card → CardHeader → Title (3 levels — fine)
❌ Card → CardBody → Section → Row → Cell → Label (6 levels — too deep)
```

### Component Set Decomposition
When a component set exceeds ~50 variants, decompose into smaller sets linked
by instance swap properties:

```javascript
// Instead of one massive ButtonSet with 100+ variants:
// Decompose into: ButtonBase (Size × Variant × State)
//                 ButtonIcon (just icon variants)
//                 ButtonWithBadge (composed from ButtonBase + Badge)

const buttonBase = figma.combineAsVariants(baseVariants, figma.currentPage)
buttonBase.name = 'Button / Base'

// ButtonWithIcon uses instance swap to pull from ButtonBase
const iconButton = figma.createComponent()
iconButton.name = 'Button / With Icon'
const swapProp = iconButton.addComponentProperty('button', 'INSTANCE_SWAP', baseVariants[0].key)
```

## Icon Component Patterns

### SVG-to-Component Workflow
```javascript
// Create component from SVG path
const iconComponent = figma.createComponent()
iconComponent.name = 'Icon/Arrow/Right'
iconComponent.resize(24, 24)
iconComponent.description = 'Right arrow icon. Use for navigation and directional indicators.'

// Import SVG as vector
const svgNode = figma.createNodeFromSvg(svgString)
const vectorChildren = svgNode.children

// Move vector children into component
vectorChildren.forEach(child => {
  iconComponent.appendChild(child.clone())
})
svgNode.remove()

// Set constraints for scaling
iconComponent.children.forEach(child => {
  if ('constraints' in child) {
    child.constraints = { horizontal: 'SCALE', vertical: 'SCALE' }
  }
})
```

### Icon Component Best Practices
- Fixed size frame (24×24 or 20×20) — no auto-layout on icon containers
- Color bound to a single `iconColor` variable using `ALL_FILLS` scope
- Constraints set to `SCALE` on all vector children
- Description includes: purpose, when to use, when NOT to use
- Code syntax set on the fill variable for Dev Mode

## Component Description Enrichment

### Machine-Readable Descriptions for MCP/Code Connect
```javascript
component.description = [
  'Primary action trigger.',
  'Use for form submission, CTA, and primary navigation actions.',
  'Use IconButton for icon-only actions.',
  'Use LinkButton for inline text actions.',
  '',
  'Variants: Size (sm/md/lg), Emphasis (primary/secondary/tertiary/ghost)',
  'Props: label (text), leadingIcon (instance swap), disabled (boolean)',
].join('\n')

// Documentation link
component.documentationLinks = [
  { uri: 'https://designsystem.example.com/components/button', name: 'Documentation' }
]
```

### Description Template
```
[One-line purpose statement]
[When to use — 1-2 use cases]
[When NOT to use — redirect to alternatives]
[Variants: list key property dimensions]
[Props: list exposed component properties]
```

## Component Validation (Extended)

### Structural Validation
```javascript
function validateComponent(component) {
  const issues = []
  
  // Check auto-layout
  if (!component.layoutMode || component.layoutMode === 'NONE') {
    issues.push('Missing auto-layout')
  }
  
  // Check description
  if (!component.description || component.description.length < 20) {
    issues.push('Missing or insufficient description')
  }
  
  // Check variable bindings on fills
  if (component.fills?.length > 0) {
    const hasBoundFill = component.fills.some(f => f.boundVariables?.color)
    if (!hasBoundFill) {
      issues.push('Fill color not bound to variable')
    }
  }
  
  // Check nesting depth
  function getDepth(node, depth = 0) {
    if (depth > 3) return depth
    if ('children' in node) {
      return Math.max(...node.children.map(c => getDepth(c, depth + 1)), depth)
    }
    return depth
  }
  if (getDepth(component) > 3) {
    issues.push('Nesting depth exceeds 3 levels')
  }
  
  // Check text nodes have loaded fonts
  const textNodes = component.findAll(n => n.type === 'TEXT')
  textNodes.forEach(t => {
    if (t.hasMissingFont) {
      issues.push(`Text "${t.name}" has missing font`)
    }
  })
  
  return { valid: issues.length === 0, issues }
}
```

---

## See also

- [figma-modes-for-variants](../figma-modes-for-variants/SKILL.md) — before
  generating an N × M variant matrix, check whether one of the axes is
  color/style-only and would be better expressed as variable modes on a
  component-scoped collection. Avoids combinatorial blow-up.
