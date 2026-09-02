---
name: figma-plugin-dev
description: Develop Figma plugins with TypeScript. Use when building plugins that import assets, create components, manage pages, or use combineAsVariants(). Covers async page loading, error recovery, component sets, and avoiding "object not extensible" errors. Essential for bulk icon import plugins.
aliases: [figma-plugin-dev]
triggers: [plugin dev]
spec_version: "2.0"
tier: spoke
domain: design
hub: figma
prerequisites: [figma]
---

# Figma Plugin Development

---

## Epistemic Standards

This skill operates under shared epistemic principles. When beginning non-trivial
work, load and apply: `shared/epistemic-standards.md`

Core obligations: surface assumptions before acting on them; verify sources are
recent *and* relevant (standards version frequently); name rejected alternatives;
distinguish user framing from evidence; make uncertainty explicit.

---

## Artifact Standards

This skill follows shared artifact naming, versioning, and delivery conventions.
Load when producing or receiving any file: `shared/artifact-standards.md`

Core obligations: name every artifact with context_descriptor_vN.N_YYYY-MM-DD.ext;
never silently overwrite — increment the version; deliver runnable code as a
double-click zip (macOS default, other platforms additive); all outputs must be
immediately usable without a terminal.

---

## Async Page Loading Pattern

**Critical**: Load pages with `loadAsync()` before accessing children.

```typescript
// CORRECT: Load once before loop
const page = figma.root.children.find(p => p.name === 'Icons') as PageNode;
await figma.setCurrentPageAsync(page);
await page.loadAsync();  // Once!

for (const item of items) {
    page.appendChild(node);  // Works - page already loaded
}

// WRONG: Repeated loadAsync causes state conflicts
for (const item of items) {
    await page.loadAsync();  // DON'T do this in loops
    page.appendChild(node);  // May fail
}
```

## "Object Not Extensible" Error

This error occurs when:
1. Accessing page before loading it
2. Repeatedly calling `loadAsync()` on same page
3. Accessing frozen Figma objects

**Fix**: Load page once at start of function, then operate on it.

## Component Sets with combineAsVariants

Create proper component sets:

```typescript
// 1. Create individual components first
const components: ComponentNode[] = [];
for (const variant of variants) {
    const comp = figma.createComponent();
    comp.name = `Size=${variant.size}, Filled?=${variant.filled ? 'yes' : 'no'}`;
    comp.resize(variant.size, variant.size);
    // Add content...
    components.push(comp);
}

// 2. Position them (required before combining)
let x = 0;
for (const comp of components) {
    comp.x = x;
    comp.y = 0;
    x += comp.width + 10;
}

// 3. Combine into component set
const componentSet = figma.combineAsVariants(components, figma.currentPage);
componentSet.name = iconName;

// 4. Apply layout
componentSet.layoutMode = 'HORIZONTAL';
componentSet.layoutWrap = 'WRAP';
componentSet.primaryAxisSizingMode = 'FIXED';
componentSet.counterAxisSizingMode = 'AUTO';
```

**Variant naming**: Use `Property=value` format. Figma auto-parses variant properties from component names.

## TypeScript CONFIG Defaults

TypeScript requires all properties in default CONFIG object:

```typescript
// WRONG: Missing properties cause TS errors
let CONFIG = {
    component_set: {
        fixed_width: 154
    }
};
CONFIG.component_set.padding  // TS error: property doesn't exist

// CORRECT: Include all properties with defaults
let CONFIG = {
    component_set: {
        fixed_width: 154,
        padding: 16,           // Include even if config.json overrides
        horizontal_gap: 16,
        vertical_gap: 16
    }
};
```

## Per-Item Error Recovery

Wrap operations in try-catch to continue on individual failures:

```typescript
for (const category of categories) {
    try {
        const frame = createCategoryFrame(category);
        
        for (const icon of category.icons) {
            try {
                const set = await createComponentSet(icon);
                if (set) frame.appendChild(set);
            } catch (e) {
                console.error(`Icon ${icon.name} failed:`, e);
                // Continue with next icon
            }
        }
    } catch (e) {
        console.error(`Category ${category.name} failed:`, e);
        // Continue with next category
    }
}
```

## SVG Import

```typescript
const svgNode = figma.createNodeFromSvg(svgContent);
// Returns FrameNode containing vector children

// Extract vectors, preserving original positioning
if ('children' in svgNode && svgNode.children.length > 0) {
    const vector = svgNode.children[0].clone();
    component.appendChild(vector);
    svgNode.remove();  // Clean up import frame
}
```

## Runtime File Discovery (Alternative to Bundling)

For large asset sets, use `webkitdirectory` input instead of bundling:

```html
<input type="file" webkitdirectory id="folderInput">
```

```typescript
// UI side: Read files from selected folder
const files = event.target.files;
const svgFiles = {};
for (const file of files) {
    if (file.name.endsWith('.svg')) {
        const content = await file.text();
        svgFiles[file.name] = content;
    }
}
parent.postMessage({ pluginMessage: { type: 'files', data: svgFiles }}, '*');
```

## Debug Logging

Include version tags for tracing:
```typescript
console.log('[PLUGIN v14] Starting import...');
console.log('[PLUGIN v14] Processing:', iconName);
console.error('[PLUGIN v14] Error:', error);
```

## Related
- hub → [[figma]]
