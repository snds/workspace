---
name: fw-dojo
description: >
  Dojo/Dijit framework patterns for reading, maintaining, and migrating legacy Dojo
  code — AMD module system, dojo/_base/declare class hierarchy, dijit widget lifecycle,
  dgrid, dojo/store patterns, and migration strategy to modern frameworks. Use this
  skill whenever the conversation involves legacy Dojo code, Dijit widgets, AMD
  require/define, data-dojo-type attributes, dgrid, dojo/store, or planning and
  executing a migration away from Dojo. If the user mentions "Dojo", "Dijit",
  "dijit/_WidgetBase", "AMD", "require/define", "dgrid", "dojo/topic", "DOH tests",
  or is diagnosing or migrating a Centric PLM screen — use this skill.
migration_note: >
  This skill primarily serves a migration context. Sean works at Centric Software on
  a PLM product that is actively migrating off Dojo. The skill covers (1) reading and
  maintaining existing Dojo code safely during extraction, and (2) planning and
  executing the migration to modern frameworks (Vue/React). Approach all Dojo patterns
  with "how do I safely replace this?" as the secondary lens.
aliases: [fw-dojo]
tier: spoke
domain: engineering
hub: lead-frontend-engineer
prerequisites: [lead-frontend-engineer]
spec_version: "2.0"
---

# Dojo — Framework Skill (Legacy + Migration)

## Migration Context — Read First

This skill exists in a migration context. Centric PLM is actively moving off Dojo toward modern frameworks (Vue as the primary target). Every Dojo pattern documented here should be read with two questions in mind:

1. **Comprehension:** What does this code do, and what are its failure modes?
2. **Extraction:** What is the modern equivalent, and what are the migration risks?

Do not add new Dojo code unless explicitly maintaining a feature that cannot be migrated in the current sprint. Flag all new Dojo additions as technical debt.

---

## AMD Module System

### require / define — the module registry

```javascript
// define — declare a module (like an ES module export)
define([
  'dojo/_base/declare',
  'dijit/_WidgetBase',
  'dojo/text!./templates/MyWidget.html',
], function(declare, _WidgetBase, template) {
  // module body — return the export
  return declare([_WidgetBase], {
    templateString: template,
  });
});

// require — load modules imperatively (like a dynamic import)
require(['myapp/views/ProductGrid'], function(ProductGrid) {
  new ProductGrid({ store: myStore }).placeAt('container');
});
```

The AMD loader resolves paths via a `dojoConfig` / `require.config` map. Module IDs are dot-separated paths relative to a configured base URL. This is the primary thing to unwind during migration — every `define([...], function(...))` wrapper must become an ES `import` statement.

### Migration: AMD → ES modules

| AMD | ES module |
|---|---|
| `define(['dep'], function(dep) { ... })` | `import dep from './dep.js'; export default ...` |
| `require(['dep'], function(dep) { ... })` | `const dep = await import('./dep.js')` |
| Module ID path config | `tsconfig.json` paths / Vite aliases |
| `dojo/text!./template.html` | `?raw` Vite import or string template |

---

## dojo/_base/declare — Class-Based Components

### The declare pattern

```javascript
define(['dojo/_base/declare', 'dijit/_WidgetBase'], function(declare, _WidgetBase) {
  return declare([_WidgetBase, _TemplatedMixin], {
    // Instance defaults (declared as class properties)
    variant: 'primary',
    label: '',

    // Widget lifecycle — see below
    postCreate: function() {
      this.inherited(arguments); // ALWAYS call inherited in lifecycle methods
      this._setupEventListeners();
    },

    // Methods
    _setupEventListeners: function() {
      this.own(
        on(this.domNode, 'click', lang.hitch(this, this._handleClick))
      );
    },

    _handleClick: function(evt) {
      this.emit('change', { value: this.value });
    },
  });
});
```

`this.inherited(arguments)` is the Dojo equivalent of `super()` — missing it in lifecycle methods causes silent failures because the mixin chain short-circuits.

### Migration: declare → class

```typescript
// Dojo
return declare([_WidgetBase, _TemplatedMixin], {
  variant: 'primary',
  postCreate() { this.inherited(arguments); },
});

// Modern equivalent (Vue component)
// Props → defineProps(), lifecycle → onMounted(), event emit → defineEmits()
```

---

## Dijit Widget Lifecycle

The lifecycle runs in a specific order — getting this wrong is the #1 source of bugs in legacy Dojo:

| Phase | Method | When | What to do |
|---|---|---|---|
| 1 | `constructor` | Before DOM | Set property defaults |
| 2 | `buildRendering` | Creates `domNode` | Parse template, rarely override |
| 3 | `postMixInProperties` | After mixin properties | Compute derived defaults |
| 4 | `postCreate` | After DOM created, before placed | Wire events, query child nodes |
| 5 | `startup` | After placed in document | Size-dependent logic, child widget startup |
| 6 | `destroy` | Teardown | Cleanup (use `this.own()` to avoid manual cleanup) |

Key rule: **never access parent or sibling widgets in `postCreate`** — they may not exist yet. `startup` is the correct phase for cross-widget wiring.

`this.own(handle)` registers a handle (event listener, subscription) to be automatically destroyed with the widget. Always use it — not using it is the primary source of memory leaks in Dijit code.

---

## The Three-Mixin Pattern

Every significant Dijit widget inherits from these three:

```javascript
declare([
  dijit._WidgetBase,        // Core: lifecycle, property system, event emission
  dijit._TemplatedMixin,    // Adds: templateString, attach points, attach events
  dijit._WidgetsInTemplateMixin, // Adds: child dijit widgets parsed from the template
], { ... });
```

`_WidgetsInTemplateMixin` is expensive — it parses `data-dojo-type` attributes in the template and instantiates child widgets. Avoid it if the template only needs DOM nodes (use `_TemplatedMixin` alone). Its presence is a signal that the widget has nested Dijit children that need to be migrated separately.

### Template attachment points

```html
<!-- data-dojo-attach-point creates this.labelNode on the widget instance -->
<span data-dojo-attach-point="labelNode">${label}</span>

<!-- data-dojo-attach-event wires a DOM event to a widget method -->
<button data-dojo-attach-event="onclick:_handleClick">Submit</button>
```

`${label}` in templates is not reactive — it's a one-time string substitution at widget instantiation. To update after creation, you must imperatively set `this.labelNode.textContent = newValue`.

---

## Dojo Data Stores

### dojo/store/Memory — client-side array store

```javascript
var store = new Memory({
  data: [{ id: 1, name: 'Product A' }, { id: 2, name: 'Product B' }],
  idProperty: 'id',
});

store.get(1);                           // → { id: 1, name: 'Product A' }
store.query({ name: 'Product A' });     // → QueryResults (array-like)
store.put({ id: 1, name: 'Updated' }); // update
store.add({ id: 3, name: 'New' });     // insert
store.remove(2);                        // delete
```

### dojo/store/JsonRest — REST-backed store

```javascript
var store = new JsonRest({
  target: '/api/products/',
  idProperty: 'id',
});
// CRUD maps to GET/PUT/POST/DELETE on the target URL
store.query({ category: 'apparel' }); // → GET /api/products/?category=apparel
```

### dojo/store/Observable — reactive wrapper

```javascript
var observable = Observable(new Memory({ data: products }));
var results = observable.query({});
results.observe(function(object, removedFrom, insertedInto) {
  // fires on store mutations — used to drive grid updates
});
```

### Migration: dojo/store → TanStack Query / Pinia

| dojo/store pattern | Modern equivalent |
|---|---|
| `Memory` with `query()` | Computed/filtered ref in Pinia or `useMemo` in React |
| `JsonRest` CRUD | TanStack Query `useQuery` + `useMutation` |
| `Observable` + `observe()` | TanStack Query cache invalidation or reactive Pinia state |
| `store.idProperty` | Explicit `id` field in TypeScript interfaces |

---

## Dojo Event System

### dojo/on — DOM and synthetic events

```javascript
var handle = on(domNode, 'click', function(evt) { ... });
handle.remove(); // manual cleanup (or use this.own(handle))

// Synthetic events on widgets
on(myWidget, 'change', function(evt) { ... });
```

### dojo/aspect — AOP hooks on methods

```javascript
// Before: intercept before the original method runs
aspect.before(obj, 'methodName', function(arg1) {
  console.log('before:', arg1);
  // return modified args or undefined to pass original args
});

// After: run after the original method (receives return value)
aspect.after(obj, 'methodName', function(result) {
  console.log('after, result was:', result);
});

// Around: fully wrap a method
aspect.around(obj, 'methodName', function(originalFn) {
  return function() {
    // before logic
    var result = originalFn.apply(this, arguments);
    // after logic
    return result;
  };
});
```

`dojo/aspect` is the primary mechanism for patching behavior in legacy Dojo without subclassing. During migration, look for `aspect.before/after` calls — they are monkey patches that must be explicitly accounted for when replacing the underlying widget.

### dojo/topic — pub/sub event bus

```javascript
// Publish
topic.publish('app/product/selected', { id: productId });

// Subscribe
var handle = topic.subscribe('app/product/selected', function(data) {
  console.log('selected:', data.id);
});
handle.remove(); // cleanup
```

`dojo/topic` is the cross-module communication layer in Dojo — the equivalent of a global event bus. During migration, map topics to: a Pinia store action, a Vue `mitt` event bus, or a React context dispatch. Audit all topic strings before migrating — they are implicit contracts between modules.

---

## Common Dijit Widgets

### dijit/form widgets

```javascript
// TextBox
var textBox = new TextBox({ value: '', placeHolder: 'Enter name' }, 'container');

// Select
var select = new Select({
  options: [
    { label: 'Option A', value: 'a', selected: true },
    { label: 'Option B', value: 'b' },
  ],
  onChange: function(value) { console.log(value); },
}, 'container');

// CheckBox
var cb = new CheckBox({ checked: false, onChange: function(val) { ... } });
```

### dijit/layout widgets

```javascript
// BorderContainer — cardinal region layout
var bc = new BorderContainer({ design: 'headline', style: 'height: 100%;' });
var top = new ContentPane({ region: 'top', content: '<h1>Header</h1>' });
var center = new ContentPane({ region: 'center' });
bc.addChild(top);
bc.addChild(center);
bc.placeAt(document.body);
bc.startup(); // MUST call startup after placing
```

BorderContainer is pervasive in PLM layouts. Migration target: CSS Grid or Flexbox layout (no JS required).

### dijit/Dialog

```javascript
var dialog = new Dialog({ title: 'Confirm', content: 'Are you sure?' });
dialog.show();
// Fires: onShow, onHide, onExecute, onCancel
```

---

## dgrid — Data Grid Library

dgrid is built on Dojo stores and is the primary grid component in PLM.

### Column definitions

```javascript
define(['dgrid/Grid', 'dgrid/Selection', 'dojo/_base/declare'], function(Grid, Selection, declare) {
  var CustomGrid = declare([Grid, Selection], {
    columns: {
      id: { label: 'ID', field: 'id', sortable: true },
      name: {
        label: 'Name',
        field: 'name',
        formatter: function(value, row) {
          return '<strong>' + value + '</strong>'; // HTML allowed
        },
      },
      actions: {
        label: '',
        renderCell: function(row, value, td) {
          var btn = document.createElement('button');
          btn.textContent = 'Edit';
          btn.addEventListener('click', function() { editRow(row); });
          td.appendChild(btn);
        },
      },
    },
  });
});
```

### Store integration + pagination

```javascript
var grid = new OnDemandGrid({
  store: Observable(JsonRest({ target: '/api/products/' })),
  columns: { ... },
  rowsPerPage: 25,
});
grid.set('sort', [{ attribute: 'name', descending: false }]);
```

`OnDemandGrid` fetches pages on scroll. `store.query()` parameters are passed as URL query params to `JsonRest`.

### Row selection

```javascript
// dgrid/Selection mixin
grid.on('dgrid-select', function(evt) {
  var selectedRows = evt.rows; // array of { id, data, element }
});
grid.on('dgrid-deselect', function(evt) { ... });

// Programmatic selection
grid.select(rowId);
grid.clearSelection();
```

### Migration: dgrid → modern data table

dgrid migration is the highest-complexity part of the PLM migration. Recommended targets:

| dgrid feature | Migration target |
|---|---|
| Column definitions | TanStack Table (Vue/React) column defs |
| `OnDemandGrid` + `JsonRest` | TanStack Query + TanStack Table with server-side pagination |
| `Observable` store + `observe()` | TanStack Query cache invalidation |
| `renderCell` HTML formatter | Column cell render slot / component |
| `dgrid/Selection` mixin | TanStack Table row selection state |
| `dgrid-select` event | `onRowSelectionChange` callback |

Risk: dgrid columns often use raw `innerHTML` formatters with application-specific HTML. These must be converted to component-based cell renderers and audited for XSS.

---

## Migration Strategy

### Risk matrix

| Dojo pattern | Migration difficulty | Direct equivalent? | Notes |
|---|---|---|---|
| AMD `define/require` | Low | Yes — ES modules | Mechanical transform; tooling can help |
| `declare` class hierarchy | Medium | Yes — ES classes or components | Watch for deep mixin chains |
| `_WidgetBase` lifecycle | Medium | Partial — framework lifecycle hooks | Lifecycle phases don't map 1:1 |
| `_TemplatedMixin` templates | Medium | Yes — framework templates | `${var}` → reactive bindings |
| `_WidgetsInTemplateMixin` | High | No direct equivalent | Nested widgets need individual migration |
| `dojo/store/Memory` | Low | Yes — array ref / Pinia state | |
| `dojo/store/JsonRest` | Low | Yes — TanStack Query | |
| `dojo/store/Observable` | Medium | Partial — TanStack Query cache | |
| `dojo/on` | Low | Yes — addEventListener / framework events | |
| `dojo/aspect` | High | No — AOP monkey patches | Audit all usages; may indicate workarounds |
| `dojo/topic` | Medium | Yes — event bus / store actions | Map topic strings explicitly |
| `dijit/layout/*` | Low | Yes — CSS Grid/Flexbox | Pure CSS replacement |
| `dijit/form/*` | Medium | Yes — framework form components | Mind accessibility parity |
| `dijit/Dialog` | Medium | Yes — framework modal | |
| `dgrid` | High | Partial — TanStack Table | Cell renderers, selection, pagination all need redesign |

### Identifying data-dojo-type in templates

```javascript
// Scan for declarative widget instantiation — requires _WidgetsInTemplateMixin
// data-dojo-type="dijit/form/TextBox" means this HTML node becomes a Dijit widget
// Migration: replace with framework component, remove the mixin

// In templates
'<input data-dojo-type="dijit/form/TextBox" data-dojo-props="value:\'hello\'">'

// Find all usages in a codebase
// grep -r "data-dojo-type" src/ --include="*.html" --include="*.js"
```

Each `data-dojo-type` is a widget that needs to be individually replaced. They represent hidden dependencies — a template may look like plain HTML but be bootstrapping multiple Dijit instances.

### Coexistence patterns during incremental migration

**Iframe isolation** — safest, no shared state:
```
Modern app in iframe ↔ postMessage API ↔ Legacy Dojo shell
```
Use when: the migrated surface is a complete page/panel that can be isolated.

**Web component wrappers** — thin adapter:
```javascript
// Wrap a modern Vue component in a CustomElement for Dojo to consume
class ModernButtonElement extends HTMLElement {
  connectedCallback() {
    createApp(ButtonComponent).mount(this);
  }
}
customElements.define('modern-button', ModernButtonElement);
// Use in Dojo template: <modern-button label="Save"></modern-button>
```

**Shared event bus** — dojo/topic ↔ mitt:
```javascript
// Bridge topic events to a modern event bus
import mitt from 'mitt';
export const bus = mitt();

topic.subscribe('app/product/selected', function(data) {
  bus.emit('product:selected', data); // forward to modern side
});
```
Use when: incremental component-level migration with shared application state.

---

## Testing Legacy Dojo

### DOH test runner

```javascript
// DOH (Dojo Objective Harness) — Dojo's built-in test framework
define(['doh'], function(doh) {
  doh.register('MyWidgetTests', [
    {
      name: 'test widget creates',
      runTest: function() {
        var widget = new MyWidget({ label: 'Test' });
        widget.placeAt(document.body);
        widget.startup();
        doh.is('Test', widget.label);
        widget.destroy();
      },
    },
  ]);
  doh.run();
});
```

DOH tests are typically run via Dojo's test server or a Selenium-based runner. They are difficult to integrate with modern CI pipelines.

### Migrating DOH tests to Vitest / Jest

| DOH | Modern (Vitest/Jest + Testing Library) |
|---|---|
| `doh.register('suite', [...])` | `describe('suite', () => { ... })` |
| `doh.is(expected, actual)` | `expect(actual).toBe(expected)` |
| `doh.assertTrue(expr)` | `expect(expr).toBe(true)` |
| `doh.assertError(ErrorType, fn)` | `expect(fn).toThrow(ErrorType)` |
| `runTest: function()` | `it('name', () => { ... })` |
| DOM manipulation in test | `@testing-library/dom` queries |

Strategy: migrate DOH tests to modern test framework at the same time as migrating the widget. Do not maintain DOH tests for code that has been migrated — the modern framework's tests are the new ground truth.

---

## Design-Engineer Integration

Context: this skill is used exclusively in a migration context within Centric PLM. When reading Dojo code:
1. Identify the widget's public API (props = constructor args, events = `this.emit()` / `dojo/topic`)
2. Map the layout role (is this a `dijit/layout/*` shell or a content widget?)
3. Note all `dojo/aspect` calls — these are patches that must be carried forward or resolved
4. Note all `dojo/topic` subscriptions — map topic strings to a migration inventory
5. Assess dgrid usage: column count, custom `renderCell` formatters, selection mode, store type
