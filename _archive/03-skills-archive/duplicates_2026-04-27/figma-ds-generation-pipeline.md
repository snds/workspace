# Complete Design System Generation Pipeline

## When to Use This Skill
Use when generating complete design systems in Figma with proper dependency ordering. This skill orchestrates the entire pipeline from variables through components with validation at each phase.

## The Five-Phase Dependency Chain
**Variables → Styles → Components → Documentation → Validation**

Each phase must complete successfully before the next begins. Breaking this order causes cascade failures.

## Pre-Pipeline Setup

### Step 0: Stack Selection (Required)
Before starting any pipeline phase, invoke the `ds-stack-router` skill to confirm the target stack. This presents a selection prompt:

1. **Use defaults** — shadcn + Radix UI (color system) + Tailwind CSS
2. **Tell me your stack** — specify your own component library, color system, and CSS framework
3. Popular alternative stacks (MUI, Chakra, Ant Design, Vuetify, Skeleton UI)

If defaults are selected, the skill collects: brand primary hex, Radix gray family preference, Tailwind version (v3/v4), and dark mode inclusion. These answers drive all subsequent token naming, code syntax, and component structure decisions throughout the pipeline.

The `ds-stack-router` skill lives at `~/.claude/skills/ds-stack-router/`.

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

### Primitive Color Architecture: Full Radix Base System

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

**Variable count per scale:** 12 opaque + 12 alpha = 24 vars
**Total scales:** 32 chromatic + 6 gray = 38 (+ white/black)
**Total primitive color vars:** 38 × 24 + 2 = **914 variables**

Each variable gets:
- `scopes: []` (empty — hidden from property pickers, consumed only via semantic aliases)
- `hiddenFromPublishing: true`
- `codeSyntax.WEB: var(--{color}-{step})` or `var(--{color}-a{step})` for alpha

### Phase 1A: Collections Setup
```javascript
// Phase 1A: Create variable collections with Light/Dark modes
// Primitives collection gets Light + Dark modes (for opaque AND alpha values)
// Semantics collection gets Light + Dark modes (aliases to primitives)

const primitivesCollection = figma.variables.createVariableCollection('Primitives')
// Rename default mode to Light
const lightMode = primitivesCollection.modes[0]
primitivesCollection.renameMode(lightMode.modeId, 'Light')
// Add Dark mode
const darkModeId = primitivesCollection.addMode('Dark')

const semanticsCollection = figma.variables.createVariableCollection('Semantics')
const semLightMode = semanticsCollection.modes[0]
semanticsCollection.renameMode(semLightMode.modeId, 'Light')
const semDarkModeId = semanticsCollection.addMode('Dark')

return {
  primitivesCollectionId: primitivesCollection.id,
  lightModeId: lightMode.modeId,
  darkModeId: darkModeId,
  semanticsCollectionId: semanticsCollection.id,
  semLightModeId: semLightMode.modeId,
  semDarkModeId: semDarkModeId
}
```

### Phase 1B: Primitive Variables — Batch Strategy

Due to the volume (~914 variables), primitives MUST be created in batches to avoid script timeouts.
Each batch handles ONE color family (opaque + alpha, light + dark values).

**Batch execution order:**
1. Gray scales (6 batches: gray, mauve, slate, sage, olive, sand)
2. Chromatic scales (25 batches: one per color)
3. Brand primary (1 batch: custom scale from user hex)
4. Absolutes (1 batch: white + black)
5. Validation pass: count all variables, verify mode values

```javascript
// Example: Single batch for one Radix scale (e.g., 'red')
// Each batch creates 24 vars: 12 opaque + 12 alpha, with Light + Dark mode values

function createRadixScale(collection, lightModeId, darkModeId, scaleName, lightOpaque, lightAlpha, darkOpaque, darkAlpha) {
  const created = []

  for (let step = 1; step <= 12; step++) {
    // Opaque variant
    const opaqueVar = figma.variables.createVariable(
      `${scaleName}/${step}`, collection.id, 'COLOR'
    )
    opaqueVar.setValueForMode(lightModeId, parseColor(lightOpaque[step - 1]))      // {r,g,b}
    opaqueVar.setValueForMode(darkModeId, parseColor(darkOpaque[step - 1]))         // {r,g,b}
    opaqueVar.scopes = []
    opaqueVar.hiddenFromPublishing = true
    opaqueVar.codeSyntax = { WEB: `var(--${scaleName}-${step})` }
    created.push(opaqueVar.id)

    // Alpha variant
    const alphaVar = figma.variables.createVariable(
      `${scaleName}/A${step}`, collection.id, 'COLOR'
    )
    alphaVar.setValueForMode(lightModeId, parseColorAlpha(lightAlpha[step - 1]))    // {r,g,b,a}
    alphaVar.setValueForMode(darkModeId, parseColorAlpha(darkAlpha[step - 1]))      // {r,g,b,a}
    alphaVar.scopes = []
    alphaVar.hiddenFromPublishing = true
    alphaVar.codeSyntax = { WEB: `var(--${scaleName}-a${step})` }
    created.push(alphaVar.id)
  }

  return created
}

// Helper: parse hex to Figma {r, g, b}
function parseColor(hex) {
  const r = parseInt(hex.slice(1, 3), 16) / 255
  const g = parseInt(hex.slice(3, 5), 16) / 255
  const b = parseInt(hex.slice(5, 7), 16) / 255
  return { r, g, b }
}

// Helper: parse rgba string to Figma {r, g, b, a}
function parseColorAlpha(rgba) {
  // rgba can be 'rgba(r, g, b, a)' or {r, g, b, a} object
  if (typeof rgba === 'object') return rgba
  const match = rgba.match(/rgba?\((\d+),\s*(\d+),\s*(\d+),?\s*([\d.]+)?\)/)
  return {
    r: parseInt(match[1]) / 255,
    g: parseInt(match[2]) / 255,
    b: parseInt(match[3]) / 255,
    a: match[4] ? parseFloat(match[4]) : 1
  }
}
```

### Phase 1B Validation
- [ ] Total primitive color variables = ~914
- [ ] Every scale has 24 vars (12 opaque + 12 alpha)
- [ ] Light mode values set on all vars
- [ ] Dark mode values set on all vars
- [ ] All scopes = [] (empty, hidden from pickers)
- [ ] All hiddenFromPublishing = true
- [ ] Code syntax set for WEB on all vars
- [ ] Brand primary step 9 matches user's hex exactly
    
    console.log(\`✅ Created \${totalPrimitives} primitive variables\`)
  `
})
```

### Phase 1C: Semantic Variables — Scale Binding

Semantic tokens alias to primitives using `VARIABLE_ALIAS`. Every semantic color MUST reference a specific Radix primitive scale — never a raw value.

**Scale binding map (configured in ds-stack-router):**

| Semantic Role | Bound Radix Scale | Steps Used |
|---------------|-------------------|------------|
| `primary` | `primary` (custom) | 3-12 |
| `secondary` | selected gray family | 1-12 |
| `destructive` | `red` | 3-12 |
| `success` | `green` | 3-12 |
| `warning` | `amber` | 3-12 |
| `info` | `blue` | 3-12 |
| `accent` | `violet` (configurable) | 3-12 |

**Per-role semantic token pattern:**

```javascript
// Example: Create semantic tokens for the 'primary' role, bound to 'primary' primitive scale
const roles = {
  primary: 'primary',
  destructive: 'red',
  success: 'green',
  warning: 'amber',
  info: 'blue',
  accent: 'violet'
}

for (const [role, scale] of Object.entries(roles)) {
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

  for (const [tokenName, refs] of Object.entries(bindings)) {
    const semanticVar = figma.variables.createVariable(tokenName, semanticsCollection.id, 'COLOR')
    // Look up the primitive variable by name to get its ID
    const lightPrimitive = allPrimitives.find(v => v.name === refs.light)
    const darkPrimitive = allPrimitives.find(v => v.name === refs.dark)
    semanticVar.setValueForMode(semLightModeId, { type: 'VARIABLE_ALIAS', id: lightPrimitive.id })
    semanticVar.setValueForMode(semDarkModeId, { type: 'VARIABLE_ALIAS', id: darkPrimitive.id })
  }
}
```

**Gray-based semantic tokens (bound to selected gray family):**

```javascript
const gray = 'slate' // from ds-stack-router selection
const grayBindings = {
  'color/bg/page':            { light: `${gray}/1`,  dark: `${gray}/1` },
  'color/bg/subtle':          { light: `${gray}/2`,  dark: `${gray}/2` },
  'color/bg/component':       { light: `${gray}/3`,  dark: `${gray}/3` },
  'color/bg/component-hover': { light: `${gray}/4`,  dark: `${gray}/4` },
  'color/bg/component-active':{ light: `${gray}/5`,  dark: `${gray}/5` },
  'color/border/default':     { light: `${gray}/6`,  dark: `${gray}/6` },
  'color/border/strong':      { light: `${gray}/7`,  dark: `${gray}/7` },
  'color/border/hover':       { light: `${gray}/8`,  dark: `${gray}/8` },
  'color/text/tertiary':      { light: `${gray}/9`,  dark: `${gray}/9` },
  'color/text/secondary':     { light: `${gray}/11`, dark: `${gray}/11` },
  'color/text/primary':       { light: `${gray}/12`, dark: `${gray}/12` }
}
// Alpha-based semantics (overlays, scrims, disabled states)
const alphaBindings = {
  'color/overlay/light':      { light: `${gray}/A6`, dark: `${gray}/A6` },
  'color/overlay/medium':     { light: `${gray}/A8`, dark: `${gray}/A8` },
  'color/overlay/heavy':      { light: `${gray}/A9`, dark: `${gray}/A9` }
}
```

**CRITICAL RULE:** Semantic variables NEVER hold raw `{r, g, b}` values. They ALWAYS use `{ type: 'VARIABLE_ALIAS', id: primitiveVar.id }`. This ensures mode switching propagates correctly through the entire token chain.

### Pipeline Validation Checklist

### Phase 1 Validation
- [ ] Collections created: Primitives (Light/Dark modes), Semantics (Light/Dark modes)
- [ ] Primitive variables: ~914 total (38 scales × 24 vars + 2 absolutes)
- [ ] Every primitive has both Light and Dark mode values set
- [ ] Alpha variants use proper RGBA with alpha < 1
- [ ] All primitive scopes = [] (hidden from pickers)
- [ ] All primitives hiddenFromPublishing = true
- [ ] Code syntax (WEB) set on all primitives
- [ ] Brand primary step 9 = user's hex in Light mode
- [ ] Semantic variables all use VARIABLE_ALIAS (no raw values)
- [ ] Each semantic role binds to correct Radix scale per binding map
- [ ] Semantic scopes set correctly (FRAME_FILL, TEXT_FILL, STROKE_COLOR, etc.)

### Error Recovery Patterns

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

This pipeline ensures systematic, error-free design system generation with complete dependency management and validation at every step.
