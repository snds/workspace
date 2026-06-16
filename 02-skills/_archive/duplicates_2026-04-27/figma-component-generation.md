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

### Component Organization

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
