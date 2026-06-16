---
name: figma-plugin
description: Figma plugin development with TypeScript. Use when creating or debugging Figma plugins, handling TypeScript compilation errors, bundling assets, or working with the Figma Plugin API. Covers common API quirks, sandbox limitations, and error patterns.
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

## TypeScript Configuration

Use ES2017 target minimum for `Object.entries()`, `.includes()`, and async/await:

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

## Common API Patterns

### Component Sets with Variants

```typescript
// Create components first, then combine
const components: ComponentNode[] = [];
for (const variant of variants) {
  const comp = figma.createComponent();
  comp.name = `Size=${variant.size}, Filled?=${variant.filled ? 'yes' : 'no'}`;
  components.push(comp);
}
const componentSet = figma.combineAsVariants(components, figma.currentPage);
```

### Safe Property Access

Not all node types support all properties. Always type-check:

```typescript
// constraints - not on SliceNode
if ('constraints' in child) {
  (child as FrameNode).constraints = { horizontal: 'SCALE', vertical: 'SCALE' };
}

// description - only on ComponentSetNode, ComponentNode
if (node.type === 'COMPONENT_SET') {
  node.description = 'tags here';
}
```

### Error Handling

TypeScript doesn't know error objects have `.message`:

```typescript
catch (error) {
  const err = error as Error;
  console.error(err.message);
}
```

### Page State

Pass page objects directly rather than relying on `figma.currentPage`:

```typescript
// WRONG - state conflicts after page switching
async function process() {
  const frame = figma.currentPage.findOne(...);
}

// CORRECT - explicit page reference
async function process(page: PageNode) {
  const frame = page.findOne(...);
}
```

## Auto Layout Frames

```typescript
const frame = figma.createFrame();
frame.layoutMode = 'HORIZONTAL';
frame.layoutWrap = 'WRAP';  // Requires recent API version
frame.primaryAxisSizingMode = 'FIXED';
frame.counterAxisSizingMode = 'AUTO';
frame.itemSpacing = 16;
frame.counterAxisSpacing = 16;
frame.paddingLeft = frame.paddingRight = frame.paddingTop = frame.paddingBottom = 16;
```

## SVG Import

```typescript
const svgNode = figma.createNodeFromSvg(svgContent);
// SVG imports as Frame containing vector(s)
if ('children' in svgNode && svgNode.children.length > 0) {
  const vector = svgNode.children[0].clone();
  component.appendChild(vector);
  svgNode.remove();
}
```

## UI Communication

Plugin sandbox requires message passing:

```typescript
// Plugin side
figma.ui.postMessage({ type: 'data-loaded', items: data });
figma.ui.onmessage = (msg) => {
  if (msg.type === 'start-import') handleImport();
};

// UI side (inline script in HTML)
parent.postMessage({ pluginMessage: { type: 'start-import' } }, '*');
window.onmessage = (event) => {
  const msg = event.data.pluginMessage;
};
```

## Bundling Strategy

Figma plugins run in a sandbox without filesystem access. Two approaches:

**Pre-bundled (compile-time):** Embed data in code.js during build:
```javascript
const bundledData = ${JSON.stringify(data)};
```

**Runtime file selection (preferred):** Use `<input type="file" webkitdirectory>` to let users select folders. Process files in UI, send to plugin via postMessage.

## Debug Logging Pattern

Include comprehensive logging that can be toggled:

```typescript
const DEBUG = true;
function log(...args: any[]) {
  if (DEBUG) console.log('[PLUGIN]', ...args);
}
```
