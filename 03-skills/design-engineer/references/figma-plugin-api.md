# Figma Plugin API Reference

Patterns and gotchas for Figma plugin development with TypeScript. Merged from
field-tested learnings across multiple plugin projects (Component Set Manager,
Material Symbols Importer, Claude AI Agent Plugin, Variable Replacement Tool).

---

## Table of Contents

1. Project setup — TypeScript config, bundling, sandbox model
2. Page and node operations — async loading, state management
3. Component and variant creation — combineAsVariants, naming, layout
4. SVG import and vector handling
5. UI communication — postMessage, sandbox constraints
6. Error handling and resilience
7. Debug logging patterns
8. File and asset handling — bundling vs. runtime selection

---

## 1. Project Setup

### TypeScript configuration

Use ES2017+ target for `Object.entries()`, `.includes()`, and async/await:

```json
{
  "compilerOptions": {
    "target": "ES2017",
    "module": "commonjs",
    "lib": ["ES2017"],
    "strict": true,
    "typeRoots": ["./node_modules/@types", "./node_modules/@figma"]
  }
}
```

### Sandbox model

Figma plugins run in a sandboxed JavaScript environment:
- No filesystem access. No `require()` at runtime.
- No direct DOM access from the plugin (code.ts) side.
- UI (ui.html) runs in an iframe with DOM access but no Figma API.
- Communication between plugin and UI is via `postMessage` only.

### Bundling strategy

Two approaches for getting data into the plugin:

**Pre-bundled (compile-time):** Embed data during build:
```javascript
// build script
const bundledData = ${JSON.stringify(data)};
```

**Runtime file selection (preferred for large assets):**
```html
<input type="file" webkitdirectory id="folderInput">
```
Process files in UI, send content to plugin via postMessage.

---

## 2. Page and Node Operations

### Async page loading — critical pattern

Load pages with `loadAsync()` ONCE before operating. Never inside loops.

```typescript
// CORRECT: Load once, then operate
const page = figma.root.children.find(p => p.name === 'Icons') as PageNode;
await figma.setCurrentPageAsync(page);
await page.loadAsync();

for (const item of items) {
    page.appendChild(node); // Works — page already loaded
}

// WRONG: Repeated loadAsync causes "object not extensible" errors
for (const item of items) {
    await page.loadAsync(); // State conflicts
    page.appendChild(node); // May fail
}
```

### Explicit page references

Pass page objects directly. Never rely on `figma.currentPage` across async
operations — it can change between awaits.

```typescript
// WRONG — state conflicts after page switching
async function process() {
  const frame = figma.currentPage.findOne(...);
}

// CORRECT — explicit page reference
async function process(page: PageNode) {
  const frame = page.findOne(...);
}
```

### "Object not extensible" error

Root causes:
1. Accessing a page before `loadAsync()`.
2. Repeated `loadAsync()` on the same page.
3. Accessing frozen Figma objects (stale references after page switch).

Fix: load the page once at the start of the function, store a reference,
operate on that reference.

---

## 3. Component and Variant Creation

### combineAsVariants workflow

```typescript
// 1. Create individual components
const components: ComponentNode[] = [];
for (const variant of variants) {
    const comp = figma.createComponent();
    comp.name = `Size=${variant.size}, Filled?=${variant.filled ? 'yes' : 'no'}`;
    comp.resize(variant.size, variant.size);
    components.push(comp);
}

// 2. Position them (REQUIRED before combining)
let x = 0;
for (const comp of components) {
    comp.x = x;
    comp.y = 0;
    x += comp.width + 10;
}

// 3. Combine into component set
const componentSet = figma.combineAsVariants(components, figma.currentPage);
componentSet.name = 'IconName';

// 4. Apply auto layout to the set
componentSet.layoutMode = 'HORIZONTAL';
componentSet.layoutWrap = 'WRAP';
componentSet.primaryAxisSizingMode = 'FIXED';
componentSet.counterAxisSizingMode = 'AUTO';
componentSet.itemSpacing = 16;
componentSet.counterAxisSpacing = 16;
componentSet.paddingLeft = componentSet.paddingRight =
  componentSet.paddingTop = componentSet.paddingBottom = 16;
```

### Variant naming

Use `Property=Value` format. Figma auto-parses variant properties from
component names within a set. Consistent casing matters.

### Safe property access

Not all node types support all properties. Always type-check:

```typescript
// constraints — not on SliceNode
if ('constraints' in child) {
  (child as FrameNode).constraints = { horizontal: 'SCALE', vertical: 'SCALE' };
}

// description — only on ComponentSetNode, ComponentNode
if (node.type === 'COMPONENT_SET') {
  node.description = 'Usage notes and tags';
}
```

### TypeScript CONFIG defaults

Include all properties with defaults to avoid TS errors:

```typescript
// WRONG: Missing properties cause TS errors on access
let CONFIG = { component_set: { fixed_width: 154 } };
CONFIG.component_set.padding; // TS error

// CORRECT: Include all properties
let CONFIG = {
    component_set: {
        fixed_width: 154,
        padding: 16,
        horizontal_gap: 16,
        vertical_gap: 16
    }
};
```

---

## 4. SVG Import

```typescript
const svgNode = figma.createNodeFromSvg(svgContent);
// Returns FrameNode containing vector children

if ('children' in svgNode && svgNode.children.length > 0) {
    const vector = svgNode.children[0].clone();
    component.appendChild(vector);
    svgNode.remove(); // Clean up the import frame
}
```

Never scale or reposition imported vectors to "center" them. Designers use
optical centering — repositioning destroys intentional offsets between
related icons.

---

## 5. UI Communication

Plugin sandbox requires message passing between code.ts and ui.html:

```typescript
// Plugin side (code.ts)
figma.ui.postMessage({ type: 'data-loaded', items: data });
figma.ui.onmessage = (msg) => {
  if (msg.type === 'start-import') handleImport(msg.payload);
};

// UI side (inline script in ui.html)
parent.postMessage({ pluginMessage: { type: 'start-import', payload } }, '*');
window.onmessage = (event) => {
  const msg = event.data.pluginMessage;
  if (msg.type === 'data-loaded') renderUI(msg.items);
};
```

### UI size management

```typescript
figma.showUI(__html__, { width: 400, height: 600 });

// Resize dynamically
figma.ui.resize(newWidth, newHeight);
```

---

## 6. Error Handling and Resilience

### Per-item error recovery

Wrap operations in try-catch to continue on individual failures:

```typescript
const skipped: Array<{name: string; error: string}> = [];

for (const category of categories) {
    try {
        const frame = createCategoryFrame(category);

        for (const icon of category.icons) {
            try {
                const set = await createComponentSet(icon);
                if (set) frame.appendChild(set);
            } catch (e) {
                const err = e as Error;
                skipped.push({ name: icon.name, error: err.message });
                console.error(`Icon ${icon.name} failed:`, err.message);
            }
        }
    } catch (e) {
        const err = e as Error;
        console.error(`Category ${category.name} failed:`, err.message);
    }
}

// Report at end
console.log(`Processed: ${total - skipped.length}/${total}`);
if (skipped.length > 0) {
    console.log('Skipped:', skipped.map(s => s.name).join(', '));
}
```

### TypeScript error typing

TypeScript doesn't know catch errors have `.message`:

```typescript
catch (error) {
  const err = error as Error;
  console.error(err.message);
}
```

---

## 7. Debug Logging

Include version-tagged logging that can be toggled:

```typescript
const DEBUG = true;
const VERSION = 14;

function log(...args: any[]) {
  if (DEBUG) console.log(`[PLUGIN v${VERSION}]`, ...args);
}

function logError(...args: any[]) {
  console.error(`[PLUGIN v${VERSION}]`, ...args);
}
```

For production builds, set `DEBUG = false` or strip via build tool.

---

## 8. File and Asset Handling

### Runtime file discovery (preferred for large sets)

```html
<input type="file" webkitdirectory id="folderInput">
```

```typescript
// UI side: Read files from selected folder
const files = (event.target as HTMLInputElement).files;
if (!files) return;

const svgFiles: Record<string, string> = {};
for (const file of Array.from(files)) {
    if (file.name.endsWith('.svg')) {
        const content = await file.text();
        svgFiles[file.name] = content;
    }
}
parent.postMessage({ pluginMessage: { type: 'files', data: svgFiles } }, '*');
```

### Change detection via content hashing

Store content hashes in component descriptions to detect actual changes:

```typescript
import { createHash } from 'crypto'; // Or use a browser-compatible hash

function computeHash(content: string): string {
    // Simple hash for Figma context — no crypto module available
    let hash = 0;
    for (let i = 0; i < content.length; i++) {
        const char = content.charCodeAt(i);
        hash = ((hash << 5) - hash) + char;
        hash |= 0;
    }
    return Math.abs(hash).toString(36).slice(0, 6);
}

// Store in description
componentSet.description = `home, house, building [hash:${hash}]`;
```

### Cross-platform launchers

For tools with non-plugin components (exporters, scrapers):

**macOS (setup.sh):**
```bash
#!/bin/bash
cd "$(dirname "$0")"
if [ -f "/opt/homebrew/bin/python3.11" ]; then
    PYTHON="/opt/homebrew/bin/python3.11"
elif command -v python3 &> /dev/null; then
    PYTHON="python3"
else
    echo "Python not found"; exit 1
fi
$PYTHON main.py "$@"
```

**Windows (setup.bat):**
```batch
@echo off
cd /d "%~dp0"
python main.py %*
if %ERRORLEVEL% NEQ 0 (echo ERROR & pause & exit /b 1)
pause
```
