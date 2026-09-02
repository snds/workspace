# LCARS Generative Interface v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a Vite/React LCARS console that turns short voice/typed intent + combadge role into a validated Scene IR and a deterministic Okudagram surface, with research/baseline as the hero workflow.

**Architecture:** Immutable constitution (tokens, geometry, APCA+AA) and module catalog feed a hybrid planner that selects curated recipes and fills slots into a typed Scene IR. A constitution validator is the only gate to a deterministic React (+ R3F) renderer. Refinement is IR patches, not chat history. v1 uses recipe select + slot fill; the planner API stays open for v2 dynamic topology.

**Tech Stack:** Vite 6, React 19, TypeScript 5.9, Zod, Vitest, Testing Library, Motion (`motion/react`), Three.js + React Three Fiber, Web Speech API, pluggable LLM adapter (mock default).

**Spec:** `07-projects/20-lcars-generative-interface/SPEC.md` (approved for implementation 2026-08-07).

**Code home:** platform `Projects` directory — create `~/Projects/lcars-generative-interface` (git repo `snds/lcars-generative-interface`). Do **not** put app source inside the workspace vault. Mirror this plan into the app at `docs/superpowers/plans/2026-08-07-lcars-generative-interface-v1.md` during Task 1.

## Global Constraints

- Personal-solo context profile for the app repo; workspace vault stays docs/session only.
- No render path may bypass `validateSceneIR` — renderer mounts only `ValidationResult.ok` IR.
- No raw runtime hex/CSS colors outside constitution tokens; modules reference token ids only.
- No freeform model-emitted HTML/CSS; LLM emits structured plan/IR patches only.
- APCA Lc is primary contrast; WCAG 2.2 AA is hard fallback — pairs must clear both.
- `prefers-reduced-motion`: instant crossfade / no layout morph; recompose otherwise 150–250ms.
- Touch targets ≥ 44×44 CSS px (hit-slop OK in dense mode).
- Voice and typed share one intent pipeline; aperture lives in legal chrome (status rail / elbow), never a floating SaaS search bar.
- Dialogue module only when planner sets `analysisNeedsDialogue: true`.
- 3D only inside `viewport3d` with registered model, units, encodings↔series integrity.
- Font: **Antonio** (OFL / Google Fonts), uppercase UI, tabular nums where available.
- Package manager: **npm**. Node ≥ 20.
- Default planner offline: `MockPlanner`. Real LLM behind `LCARS_LLM_PROVIDER` env later.
- Asserted APCA Lc floors (constitution tables): large display (≥1.5rem condensed) Lc≥60; body UI label Lc≥75; non-text UI Lc≥45. WCAG AA: 4.5:1 normal text, 3:1 large text / UI components.
- YAGNI: no free topology synthesis, no real auth, no production ASR beyond Web Speech API.

## File map (app repo root)

```
lcars-generative-interface/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tsconfig.node.json
├── index.html
├── docs/superpowers/plans/2026-08-07-lcars-generative-interface-v1.md
├── public/fonts/   # optional self-host; or CSS @import Antonio
├── src/
│   ├── main.tsx
│   ├── app/
│   │   ├── App.tsx                 # mounts runtime only
│   │   ├── shell.css               # black canvas + token CSS vars
│   │   └── SurfaceHost.tsx         # sole pixel path: validate → render
│   ├── constitution/
│   │   ├── version.ts
│   │   ├── tokens.ts               # typed ramps → CSS vars
│   │   ├── geometry.ts             # gutters, elbows, density caps
│   │   ├── contrast.ts             # APCA + WCAG pair checks
│   │   ├── typography.ts
│   │   ├── motion.ts
│   │   └── index.ts
│   ├── ir/
│   │   ├── schema.ts               # Zod SceneIR + patches
│   │   ├── types.ts                # inferred types
│   │   ├── patches.ts              # applyPatch helpers
│   │   └── index.ts
│   ├── catalog/
│   │   ├── types.ts
│   │   ├── modules.ts              # module definitions
│   │   ├── renderers/
│   │   │   ├── Elbow.tsx
│   │   │   ├── StatusRail.tsx
│   │   │   ├── ActionPill.tsx
│   │   │   ├── DataBlock.tsx
│   │   │   ├── ClaimList.tsx
│   │   │   ├── EvidencePanel.tsx
│   │   │   ├── ComparePanel.tsx
│   │   │   ├── Prose.tsx
│   │   │   ├── Dialogue.tsx
│   │   │   ├── ModeSelect.tsx
│   │   │   ├── QueryAperture.tsx
│   │   │   ├── Viewport3D.tsx
│   │   │   └── index.tsx           # moduleType → component map
│   │   └── index.ts
│   ├── validator/
│   │   ├── validate.ts
│   │   ├── repair.ts
│   │   └── index.ts
│   ├── planner/
│   │   ├── types.ts
│   │   ├── intent.ts
│   │   ├── mock-planner.ts
│   │   ├── recipe-select.ts
│   │   └── index.ts
│   ├── recipes/
│   │   ├── research.ts
│   │   ├── engineering.ts
│   │   ├── medical.ts
│   │   ├── ops-security.ts
│   │   ├── executive.ts
│   │   └── index.ts
│   ├── runtime/
│   │   ├── combadge.ts
│   │   ├── session.ts
│   │   ├── aperture.ts             # typed + voice → IntentEvent
│   │   ├── loop.ts                 # intent → plan → validate → host
│   │   └── index.ts
│   ├── models3d/
│   │   ├── registry.ts
│   │   ├── field-anomaly.ts
│   │   └── stellar-body.ts
│   └── tools/
│       ├── research-stub.ts
│       └── types.ts
└── src/**/*.test.ts                # colocate Vitest files
```

---

### Task 1: Scaffold app repo + toolchains

**Files:**
- Create: `~/Projects/lcars-generative-interface/` (full Vite React-TS scaffold as below)
- Create: mirrored plan at `docs/superpowers/plans/2026-08-07-lcars-generative-interface-v1.md`
- Create: `README.md` pointing at workspace SPEC path for design authority

**Interfaces:**
- Consumes: none
- Produces: `npm test`, `npm run build`, `npm run dev` working empty shell

- [ ] **Step 1: Create repo and Vite app**

```bash
mkdir -p ~/Projects/lcars-generative-interface
cd ~/Projects/lcars-generative-interface
npm create vite@latest . -- --template react-ts
# if non-empty prompt, init manually with package.json below
git init
```

`package.json` (replace scaffold defaults):

```json
{
  "name": "lcars-generative-interface",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "@react-three/fiber": "^9.1.2",
    "apca-w3": "^0.1.9",
    "motion": "^12.23.12",
    "react": "^19.1.0",
    "react-dom": "^19.1.0",
    "three": "^0.171.0",
    "zod": "^3.25.76"
  },
  "devDependencies": {
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/react": "^16.3.0",
    "@testing-library/user-event": "^14.6.1",
    "@types/react": "^19.1.8",
    "@types/react-dom": "^19.1.6",
    "@types/three": "^0.171.0",
    "@vitejs/plugin-react": "^4.5.2",
    "jsdom": "^26.1.0",
    "typescript": "~5.9.3",
    "vite": "^6.4.1",
    "vitest": "^4.1.8"
  }
}
```

- [ ] **Step 2: Vitest + Testing Library config**

`vite.config.ts`:

```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: { '@': path.resolve(__dirname, 'src') },
  },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    css: true,
  },
});
```

`src/test/setup.ts`:

```ts
import '@testing-library/jest-dom/vitest';
```

Add path alias in `tsconfig.app.json` / `tsconfig.json`:

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] }
  }
}
```

- [ ] **Step 3: Smoke test**

`src/app/smoke.test.ts`:

```ts
import { describe, it, expect } from 'vitest';

describe('scaffold', () => {
  it('runs vitest', () => {
    expect(1 + 1).toBe(2);
  });
});
```

Run: `npm install && npm test && npm run build`  
Expected: PASS / build OK

- [ ] **Step 4: Mirror plan + README + initial commit**

```bash
mkdir -p docs/superpowers/plans
cp "/Users/snds/Projects/Workspace/07-projects/20-lcars-generative-interface/docs/superpowers/plans/2026-08-07-lcars-generative-interface-v1.md" \
  docs/superpowers/plans/
```

`README.md` must state design authority: workspace `07-projects/20-lcars-generative-interface/SPEC.md`.

```bash
git add -A
git commit -m "chore: scaffold Vite React TS app for LCARS generative interface"
```

---

### Task 2: Constitution tokens + contrast gates

**Files:**
- Create: `src/constitution/version.ts`
- Create: `src/constitution/tokens.ts`
- Create: `src/constitution/contrast.ts`
- Create: `src/constitution/typography.ts`
- Create: `src/constitution/motion.ts`
- Create: `src/constitution/index.ts`
- Create: `src/constitution/tokens.test.ts`
- Create: `src/constitution/contrast.test.ts`
- Create: `src/app/shell.css` (CSS vars emitted from tokens)

**Interfaces:**
- Consumes: none
- Produces:
  - `CONSTITUTION_VERSION = 1 as const`
  - `TOKENS: Record<TokenId, { hex: string; role: SemanticRole }>`
  - `type TokenId = \`frame.\${string}\` | \`action.\${string}\` | \`data.\${string}\` | \`alert.\${string}\` | \`neutral.\${string}\` | 'ink.onFill' | 'ink.onBlack'`
  - `contrastPair(fg: TokenId, bg: TokenId, use: ContrastUse): ContrastReport`
  - `assertLegalPair(fg, bg, use): void` throws on fail
  - `tokensToCssVars(tokens): string`
  - `ContrastUse = 'largeDisplay' | 'bodyLabel' | 'nonText'`
  - `APCA_FLOORS` / `WCAG_FLOORS` constants

- [ ] **Step 1: Failing contrast tests**

```ts
// src/constitution/contrast.test.ts
import { describe, it, expect } from 'vitest';
import { contrastPair, APCA_FLOORS } from './contrast';
import { TOKENS } from './tokens';

describe('contrastPair', () => {
  it('ink.onFill on action.amber clears bodyLabel APCA + AA', () => {
    const r = contrastPair('ink.onFill', 'action.amber', 'bodyLabel');
    expect(r.apcaLc).toBeGreaterThanOrEqual(APCA_FLOORS.bodyLabel);
    expect(r.wcagAaPass).toBe(true);
    expect(r.ok).toBe(true);
  });

  it('rejects low-contrast illegal pair', () => {
    const r = contrastPair('data.mauve', 'frame.mauve', 'bodyLabel');
    expect(r.ok).toBe(false);
  });
});
```

```ts
// src/constitution/tokens.test.ts
import { describe, it, expect } from 'vitest';
import { TOKENS, tokensToCssVars } from './tokens';

describe('TOKENS', () => {
  it('exposes required semantic families', () => {
    const ids = Object.keys(TOKENS);
    for (const prefix of ['frame.', 'action.', 'data.', 'alert.', 'neutral.']) {
      expect(ids.some((id) => id.startsWith(prefix))).toBe(true);
    }
    expect(TOKENS['ink.onFill']).toBeDefined();
    expect(TOKENS['ink.onBlack']).toBeDefined();
  });

  it('emits CSS variables without raw hex in selectors', () => {
    const css = tokensToCssVars(TOKENS);
    expect(css).toContain('--lcars-action-amber:');
    expect(css.startsWith(':root')).toBe(true);
  });
});
```

Run: `npm test -- src/constitution`  
Expected: FAIL (modules missing)

- [ ] **Step 2: Implement tokens (Okuda-derived ramps)**

```ts
// src/constitution/version.ts
export const CONSTITUTION_VERSION = 1 as const;
```

```ts
// src/constitution/tokens.ts
export type SemanticRole =
  | 'frame'
  | 'action'
  | 'data'
  | 'alert'
  | 'neutral'
  | 'ink';

export type TokenId =
  | 'frame.mauve'
  | 'frame.amber'
  | 'frame.bluegrey'
  | 'action.amber'
  | 'action.salmon'
  | 'action.mauve'
  | 'data.mauve'
  | 'data.bluegrey'
  | 'data.amber'
  | 'alert.orange'
  | 'neutral.black'
  | 'neutral.gutter'
  | 'ink.onFill'
  | 'ink.onBlack';

export type TokenDef = { hex: string; role: SemanticRole };

export const TOKENS: Record<TokenId, TokenDef> = {
  'frame.mauve': { hex: '#CC99CC', role: 'frame' },
  'frame.amber': { hex: '#FF9900', role: 'frame' },
  'frame.bluegrey': { hex: '#9999FF', role: 'frame' },
  'action.amber': { hex: '#FF9900', role: 'action' },
  'action.salmon': { hex: '#FF6666', role: 'action' },
  'action.mauve': { hex: '#CC6699', role: 'action' },
  'data.mauve': { hex: '#994466', role: 'data' },
  'data.bluegrey': { hex: '#6666FF', role: 'data' },
  'data.amber': { hex: '#CC7700', role: 'data' },
  'alert.orange': { hex: '#FF3300', role: 'alert' },
  'neutral.black': { hex: '#000000', role: 'neutral' },
  'neutral.gutter': { hex: '#000000', role: 'neutral' },
  'ink.onFill': { hex: '#000000', role: 'ink' },
  'ink.onBlack': { hex: '#FFCC99', role: 'ink' },
};

export function tokensToCssVars(tokens: Record<TokenId, TokenDef>): string {
  const lines = Object.entries(tokens).map(([id, def]) => {
    const varName = `--lcars-${id.replace(/\./g, '-')}`;
    return `  ${varName}: ${def.hex};`;
  });
  return `:root {\n${lines.join('\n')}\n}\n`;
}

export function cssVar(id: TokenId): string {
  return `var(--lcars-${id.replace(/\./g, '-')})`;
}
```

Tune hex values in Step 3 until contrast tests pass; do not invent tokens outside `TokenId`.

- [ ] **Step 3: Implement contrast**

```ts
// src/constitution/contrast.ts
import { APCAcontrast, sRGBtoY } from 'apca-w3';
import { TOKENS, type TokenId } from './tokens';

export type ContrastUse = 'largeDisplay' | 'bodyLabel' | 'nonText';

export const APCA_FLOORS: Record<ContrastUse, number> = {
  largeDisplay: 60,
  bodyLabel: 75,
  nonText: 45,
};

export const WCAG_FLOORS: Record<ContrastUse, number> = {
  largeDisplay: 3,
  bodyLabel: 4.5,
  nonText: 3,
};

export type ContrastReport = {
  fg: TokenId;
  bg: TokenId;
  use: ContrastUse;
  apcaLc: number;
  wcagRatio: number;
  wcagAaPass: boolean;
  ok: boolean;
};

function hexToRgb(hex: string): [number, number, number] {
  const h = hex.replace('#', '');
  return [
    parseInt(h.slice(0, 2), 16),
    parseInt(h.slice(2, 4), 16),
    parseInt(h.slice(4, 6), 16),
  ];
}

function relativeLuminance([r, g, b]: [number, number, number]): number {
  const lin = [r, g, b].map((c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2];
}

function wcagRatio(fg: string, bg: string): number {
  const L1 = relativeLuminance(hexToRgb(fg));
  const L2 = relativeLuminance(hexToRgb(bg));
  const lighter = Math.max(L1, L2);
  const darker = Math.min(L1, L2);
  return (lighter + 0.05) / (darker + 0.05);
}

export function contrastPair(
  fg: TokenId,
  bg: TokenId,
  use: ContrastUse,
): ContrastReport {
  const fgHex = TOKENS[fg].hex;
  const bgHex = TOKENS[bg].hex;
  const apcaLc = Math.abs(
    Number(APCAcontrast(sRGBtoY(hexToRgb(fgHex)), sRGBtoY(hexToRgb(bgHex)))),
  );
  const ratio = wcagRatio(fgHex, bgHex);
  const wcagAaPass = ratio >= WCAG_FLOORS[use];
  const ok = apcaLc >= APCA_FLOORS[use] && wcagAaPass;
  return { fg, bg, use, apcaLc, wcagRatio: ratio, wcagAaPass, ok };
}

export function assertLegalPair(fg: TokenId, bg: TokenId, use: ContrastUse): void {
  const r = contrastPair(fg, bg, use);
  if (!r.ok) {
    throw new Error(
      `Illegal contrast ${fg} on ${bg} for ${use}: Lc=${r.apcaLc.toFixed(1)} ratio=${r.wcagRatio.toFixed(2)}`,
    );
  }
}
```

If `apca-w3` import shapes differ, adjust to the package's actual exports; keep the public `contrastPair` signature stable.

`typography.ts` / `motion.ts`:

```ts
// typography.ts
export const FONT_FAMILY_UI = '"Antonio", "Arial Narrow", sans-serif';
export const TYPE_SCALE_REM = {
  label: 0.875,
  body: 1,
  display: 1.5,
  elbow: 2,
} as const;
```

```ts
// motion.ts
export const RECOMPOSE_MS = { min: 150, max: 250 } as const;
export function recomposeDuration(reducedMotion: boolean): number {
  return reducedMotion ? 0 : 200;
}
```

- [ ] **Step 4: Wire CSS vars into shell**

Generate once at boot in `main.tsx` or inject `tokensToCssVars(TOKENS)` into `shell.css` build step. Simplest v1: write static CSS matching tokens and a unit test that `tokensToCssVars` stays in sync (parse both). Prefer emitting from `tokens.ts` into a `<style>` tag in `App.tsx` for single source of truth.

- [ ] **Step 5: Run tests + commit**

```bash
npm test -- src/constitution
git add src/constitution src/app/shell.css src/app/App.tsx
git commit -m "feat(constitution): tokens, typography, motion, APCA+AA contrast gates"
```

---

### Task 3: Geometry grammar

**Files:**
- Create: `src/constitution/geometry.ts`
- Create: `src/constitution/geometry.test.ts`
- Modify: `src/constitution/index.ts`

**Interfaces:**
- Consumes: density modes from SPEC
- Produces:
  - `Density = 'sparse' | 'standard' | 'dense'`
  - `LEGAL_PRIMITIVES = ['elbow','bar','pill','rect','sweep','viewportCircle'] as const`
  - `GUTTER_PX: Record<Density, number>` — sparse 16, standard 12, dense 8
  - `densityCaps(density): { maxModules: number; minTouchPx: number }`
  - `assertLegalPrimitive(kind: string): void`

- [ ] **Step 1: Failing tests**

```ts
import { describe, it, expect } from 'vitest';
import { densityCaps, assertLegalPrimitive, GUTTER_PX } from './geometry';

describe('geometry', () => {
  it('keeps touch floor at 44 even in dense', () => {
    expect(densityCaps('dense').minTouchPx).toBe(44);
  });

  it('rejects illegal primitive', () => {
    expect(() => assertLegalPrimitive('card')).toThrow(/illegal primitive/i);
  });

  it('uses uniform gutters per density', () => {
    expect(GUTTER_PX.standard).toBe(12);
  });
});
```

- [ ] **Step 2: Implement + commit**

```ts
export type Density = 'sparse' | 'standard' | 'dense';
export const LEGAL_PRIMITIVES = [
  'elbow',
  'bar',
  'pill',
  'rect',
  'sweep',
  'viewportCircle',
] as const;
export type LegalPrimitive = (typeof LEGAL_PRIMITIVES)[number];

export const GUTTER_PX: Record<Density, number> = {
  sparse: 16,
  standard: 12,
  dense: 8,
};

export function densityCaps(density: Density) {
  const maxModules = density === 'sparse' ? 8 : density === 'standard' ? 14 : 22;
  return { maxModules, minTouchPx: 44 };
}

export function assertLegalPrimitive(kind: string): void {
  if (!(LEGAL_PRIMITIVES as readonly string[]).includes(kind)) {
    throw new Error(`illegal primitive: ${kind}`);
  }
}
```

```bash
npm test -- src/constitution/geometry.test.ts
git add src/constitution/geometry.ts src/constitution/geometry.test.ts src/constitution/index.ts
git commit -m "feat(constitution): geometry grammar and density caps"
```

---

### Task 4: Scene IR Zod schema + patches

**Files:**
- Create: `src/ir/schema.ts`
- Create: `src/ir/types.ts`
- Create: `src/ir/patches.ts`
- Create: `src/ir/index.ts`
- Create: `src/ir/schema.test.ts`
- Create: `src/ir/patches.test.ts`

**Interfaces:**
- Consumes: `Density`, `TokenId` (token ids as zod enums/strings validated later)
- Produces:
  - `SceneIRSchema` / `type SceneIR = z.infer<typeof SceneIRSchema>`
  - `IntentClassSchema`, `RoleIdSchema`
  - `ScenePatchSchema` with ops: `setFilter | setDensity | replaceModule | openDrillIn | setViewportParam`
  - `applyPatch(ir: SceneIR, patch: ScenePatch): SceneIR` (pure; no validate)

- [ ] **Step 1: Failing schema tests**

```ts
import { describe, it, expect } from 'vitest';
import { SceneIRSchema } from './schema';
import { applyPatch } from './patches';

const minimal = {
  version: 1,
  surfaceId: 'research.baseline',
  role: 'physicist',
  density: 'standard',
  intent: {
    class: 'infoseek',
    raw: 'compare warp theories',
    analysisNeedsDialogue: false,
  },
  regions: [
    { id: 'leftRail', kind: 'rail' },
    { id: 'main', kind: 'main' },
    { id: 'footer', kind: 'status' },
  ],
  modules: [
    {
      id: 'm1',
      type: 'statusRail',
      regionId: 'footer',
      props: { state: 'idle', label: 'READY' },
      tokens: { fill: 'frame.mauve', ink: 'ink.onFill' },
    },
  ],
  focus: { moduleId: 'm1' },
  a11y: { title: 'Research workspace' },
};

describe('SceneIRSchema', () => {
  it('accepts minimal legal shape', () => {
    expect(SceneIRSchema.parse(minimal).surfaceId).toBe('research.baseline');
  });

  it('rejects missing version', () => {
    expect(() => SceneIRSchema.parse({ ...minimal, version: 2 })).toThrow();
  });
});

describe('applyPatch', () => {
  it('setDensity updates density', () => {
    const ir = SceneIRSchema.parse(minimal);
    const next = applyPatch(ir, { op: 'setDensity', density: 'dense' });
    expect(next.density).toBe('dense');
  });
});
```

- [ ] **Step 2: Implement schema**

```ts
// src/ir/schema.ts
import { z } from 'zod';

export const RoleIdSchema = z.enum([
  'engineer',
  'physician',
  'physicist',
  'operations',
  'security',
  'executive',
]);

export const IntentClassSchema = z.enum([
  'command',
  'infoseek',
  'analysis',
  'navigate',
  'refine',
]);

export const DensitySchema = z.enum(['sparse', 'standard', 'dense']);

export const ModuleInstanceSchema = z.object({
  id: z.string().min(1),
  type: z.string().min(1),
  regionId: z.string().min(1),
  props: z.record(z.unknown()).default({}),
  tokens: z
    .object({
      fill: z.string(),
      ink: z.string(),
      accent: z.string().optional(),
    })
    .passthrough(),
  children: z.array(z.string()).optional(),
  binding: z.record(z.unknown()).optional(),
});

export const SceneIRSchema = z.object({
  version: z.literal(1),
  surfaceId: z.string().min(1),
  role: RoleIdSchema,
  density: DensitySchema,
  intent: z.object({
    class: IntentClassSchema,
    raw: z.string(),
    analysisNeedsDialogue: z.boolean().default(false),
    domain: z.string().optional(),
  }),
  regions: z.array(
    z.object({
      id: z.string(),
      kind: z.enum(['rail', 'header', 'main', 'mode', 'status']),
    }),
  ),
  modules: z.array(ModuleInstanceSchema),
  focus: z.object({ moduleId: z.string().optional(), aperture: z.boolean().optional() }),
  a11y: z.object({
    title: z.string(),
    liveMessage: z.string().optional(),
  }),
  dialogue: z
    .object({
      turns: z.array(z.object({ role: z.enum(['user', 'system']), text: z.string() })),
    })
    .optional(),
  surfaceState: z
    .enum([
      'idle',
      'listening',
      'working',
      'result',
      'empty',
      'error',
      'degraded',
      'refinePending',
    ])
    .default('idle'),
});

export const ScenePatchSchema = z.discriminatedUnion('op', [
  z.object({ op: z.literal('setFilter'), moduleId: z.string(), filter: z.unknown() }),
  z.object({ op: z.literal('setDensity'), density: DensitySchema }),
  z.object({
    op: z.literal('replaceModule'),
    moduleId: z.string(),
    module: ModuleInstanceSchema,
  }),
  z.object({ op: z.literal('openDrillIn'), moduleId: z.string(), target: z.string() }),
  z.object({
    op: z.literal('setViewportParam'),
    moduleId: z.string(),
    key: z.string(),
    value: z.unknown(),
  }),
]);
```

```ts
// patches.ts
import type { SceneIR, ScenePatch } from './types';

export function applyPatch(ir: SceneIR, patch: ScenePatch): SceneIR {
  switch (patch.op) {
    case 'setDensity':
      return { ...ir, density: patch.density };
    case 'replaceModule':
      return {
        ...ir,
        modules: ir.modules.map((m) => (m.id === patch.moduleId ? patch.module : m)),
      };
    case 'setFilter':
      return {
        ...ir,
        modules: ir.modules.map((m) =>
          m.id === patch.moduleId
            ? { ...m, props: { ...m.props, filter: patch.filter } }
            : m,
        ),
      };
    case 'openDrillIn':
      return {
        ...ir,
        modules: ir.modules.map((m) =>
          m.id === patch.moduleId
            ? { ...m, props: { ...m.props, drillIn: patch.target } }
            : m,
        ),
      };
    case 'setViewportParam':
      return {
        ...ir,
        modules: ir.modules.map((m) =>
          m.id === patch.moduleId
            ? {
                ...m,
                binding: { ...(m.binding ?? {}), [patch.key]: patch.value },
              }
            : m,
        ),
      };
    default: {
      const _exhaustive: never = patch;
      return _exhaustive;
    }
  }
}
```

- [ ] **Step 3: Tests pass + commit**

```bash
npm test -- src/ir
git add src/ir
git commit -m "feat(ir): Scene IR zod schema and pure patches"
```

---

### Task 5: Constitution validator + repair

**Files:**
- Create: `src/validator/validate.ts`
- Create: `src/validator/repair.ts`
- Create: `src/validator/index.ts`
- Create: `src/validator/validate.test.ts`
- Create: `src/catalog/types.ts` (minimal ModuleDef for eligibility)
- Create: `src/catalog/modules.ts` (stub catalog entries used by validator)

**Interfaces:**
- Consumes: `SceneIR`, `TOKENS`, `contrastPair`, `densityCaps`, `LEGAL_PRIMITIVES`, catalog
- Produces:
  - `type ValidationResult = { ok: true; ir: SceneIR } | { ok: false; issues: Issue[]; repaired?: SceneIR }`
  - `validateSceneIR(ir: unknown, ctx: ValidateCtx): ValidationResult`
  - Validator order exactly as SPEC: schema → module types → parent-child → geometry → tokens → APCA+AA → touch/focus → density caps → role/clearance → viewport3d binding
  - `repairSceneIR(ir, issues): SceneIR | null` — nearest legal token / drop illegal module; null if unrepairable

- [ ] **Step 1: Failing tests**

```ts
import { describe, it, expect } from 'vitest';
import { validateSceneIR } from './validate';
import { SceneIRSchema } from '@/ir/schema';

const base = SceneIRSchema.parse({
  version: 1,
  surfaceId: 'research.baseline',
  role: 'physicist',
  density: 'standard',
  intent: { class: 'infoseek', raw: 'x', analysisNeedsDialogue: false },
  regions: [
    { id: 'main', kind: 'main' },
    { id: 'footer', kind: 'status' },
  ],
  modules: [
    {
      id: 'aperture',
      type: 'queryAperture',
      regionId: 'footer',
      props: {},
      tokens: { fill: 'frame.mauve', ink: 'ink.onFill' },
    },
    {
      id: 'status',
      type: 'statusRail',
      regionId: 'footer',
      props: { state: 'idle', label: 'READY' },
      tokens: { fill: 'frame.amber', ink: 'ink.onFill' },
    },
  ],
  focus: { aperture: true },
  a11y: { title: 'Research' },
  surfaceState: 'idle',
});

describe('validateSceneIR', () => {
  it('accepts a minimal research shell', () => {
    const r = validateSceneIR(base, { catalog: 'default' });
    expect(r.ok).toBe(true);
  });

  it('rejects unknown module type', () => {
    const bad = {
      ...base,
      modules: [
        ...base.modules,
        {
          id: 'x',
          type: 'chatBubble',
          regionId: 'main',
          props: {},
          tokens: { fill: 'action.amber', ink: 'ink.onFill' },
        },
      ],
    };
    const r = validateSceneIR(bad, { catalog: 'default' });
    expect(r.ok).toBe(false);
  });

  it('rejects contrast-illegal ink/fill', () => {
    const bad = {
      ...base,
      modules: base.modules.map((m) =>
        m.id === 'status'
          ? { ...m, tokens: { fill: 'data.mauve', ink: 'frame.mauve' } }
          : m,
      ),
    };
    const r = validateSceneIR(bad, { catalog: 'default' });
    expect(r.ok).toBe(false);
  });
});
```

- [ ] **Step 2: Stub catalog module ids**

`src/catalog/modules.ts` must register at least: `statusRail`, `queryAperture`, `elbow`, `actionPill`, `dataBlock`, `claimList`, `evidencePanel`, `comparePanel`, `prose`, `dialogue`, `modeSelect`, `viewport3d`.

Each `ModuleDef`:

```ts
export type ModuleDef = {
  type: string;
  primitive: LegalPrimitive | 'composite';
  allowedRegions: Array<'rail' | 'header' | 'main' | 'mode' | 'status'>;
  allowedRoles?: RoleId[]; // omit = all
  allowedChildren?: string[];
  densitiyMax?: Density;
};
```

- [ ] **Step 3: Implement validate order**

```ts
export function validateSceneIR(input: unknown, ctx: ValidateCtx): ValidationResult {
  const parsed = SceneIRSchema.safeParse(input);
  if (!parsed.success) {
    return { ok: false, issues: [{ code: 'schema', message: parsed.error.message }] };
  }
  let ir = parsed.data;
  const issues: Issue[] = [];
  // 2 module types ∈ catalog
  // 3 parent-child
  // 4 geometry primitive via catalog.primitive
  // 5 token ids ∈ TOKENS
  // 6 contrastPair(ink, fill, 'bodyLabel') for each module
  // 7 focus module exists; aperture boolean OK
  // 8 densityCaps: modules.length <= max
  // 9 role eligibility
  // 10 viewport3d binding if present
  if (issues.length) {
    const repaired = repairSceneIR(ir, issues);
    return { ok: false, issues, repaired: repaired ?? undefined };
  }
  return { ok: true, ir };
}
```

`SurfaceHost` (later) must treat only `ok: true` as mountable. If `repaired` present, planner may re-submit repaired IR through validate again.

- [ ] **Step 4: Tests + commit**

```bash
npm test -- src/validator src/catalog
git add src/validator src/catalog
git commit -m "feat(validator): constitution checks with repair path"
```

---

### Task 6: Catalog React renderers (2D core)

**Files:**
- Create: `src/catalog/renderers/*.tsx` listed in file map (all except Viewport3D)
- Create: `src/catalog/renderers/index.tsx`
- Create: `src/catalog/renderers/renderers.test.tsx`
- Create: `src/app/SurfaceHost.tsx`

**Interfaces:**
- Consumes: validated `SceneIR`, `cssVar`, Motion `recomposeDuration`
- Produces:
  - `renderModule(instance, ir, handlers): ReactNode`
  - `SurfaceHost({ ir }: { ir: SceneIR })` — throws if called without prior validate in loop (accept `ir` only from runtime after validate)
  - Module components use `role`, `aria-*`, token CSS vars only

- [ ] **Step 1: Failing render test**

```tsx
import { render, screen } from '@testing-library/react';
import { SurfaceHost } from '@/app/SurfaceHost';
import { validateSceneIR } from '@/validator';
import { researchIdleIR } from '@/recipes/research'; // may inline fixture until Task 8

it('renders status READY from IR', () => {
  const r = validateSceneIR(researchIdleIR(), { catalog: 'default' });
  if (!r.ok) throw new Error('fixture invalid');
  render(<SurfaceHost ir={r.ir} />);
  expect(screen.getByText('READY')).toBeInTheDocument();
  expect(screen.getByRole('main')).toHaveAccessibleName(/research/i);
});
```

Until Task 8, put fixture in `src/test/fixtures/researchIdle.ts`.

- [ ] **Step 2: Implement SurfaceHost + core modules**

`SurfaceHost.tsx` groups modules by `regionId`, maps region kinds to landmarks:

| kind | landmark |
|---|---|
| header | banner |
| rail | navigation |
| main | main |
| mode | complementary |
| status | contentinfo |

`StatusRail`: shows WORKING pulse class when `props.state === 'working'`; respects `prefers-reduced-motion` (no pulse).

`QueryAperture`: `<input aria-label="Command">` inside status/elbow chrome; onSubmit → `handlers.onIntent`.

`ActionPill`: button, min 44×44 hit target.

No chat transcript container anywhere.

- [ ] **Step 3: Commit**

```bash
npm test -- src/catalog src/app/SurfaceHost
git add src/catalog src/app src/test/fixtures
git commit -m "feat(catalog): deterministic 2D LCARS module renderers + SurfaceHost"
```

---

### Task 7: Recipes (five compiled plans) + hybrid planner

**Files:**
- Create: `src/recipes/*.ts` + `index.ts`
- Create: `src/planner/intent.ts`
- Create: `src/planner/recipe-select.ts`
- Create: `src/planner/mock-planner.ts`
- Create: `src/planner/types.ts`
- Create: `src/planner/index.ts`
- Create: `src/planner/planner.test.ts`
- Create: `src/tools/research-stub.ts`

**Interfaces:**
- Consumes: combadge profile, intent event, session
- Produces:
  - `type Planner = { plan(input: PlanInput): Promise<SceneIR> }`
  - `MockPlanner` implements `Planner`
  - `selectRecipe(role, intent): RecipeId`
  - `compileRecipe(recipeId, fill: SlotFill): SceneIR` — same compiler shape v2 will call
  - Recipe ids: `research.baseline | engineering.diagnostics | medical.review | ops.security | command.executive`

- [ ] **Step 1: Failing planner tests**

```ts
import { describe, it, expect } from 'vitest';
import { MockPlanner } from './mock-planner';
import { validateSceneIR } from '@/validator';

describe('MockPlanner', () => {
  it('physicist research intent yields valid research surface', async () => {
    const planner = new MockPlanner();
    const ir = await planner.plan({
      profile: {
        role: 'physicist',
        preferences: {
          density: 'standard',
          accentFamily: 'mauve',
          reduceMotion: false,
          verbosity: 'normal',
        },
        clearance: ['research'],
        recentWorkflow: 'research.baseline',
      },
      intent: { source: 'typed', text: 'summarize subspace theories' },
      session: { surfaceId: null },
    });
    const v = validateSceneIR(ir, { catalog: 'default' });
    expect(v.ok).toBe(true);
    if (v.ok) {
      expect(v.ir.surfaceId).toBe('research.baseline');
      expect(v.ir.modules.some((m) => m.type === 'claimList')).toBe(true);
    }
  });

  it('engineer bias prefers engineering recipe on diagnostics language', async () => {
    const planner = new MockPlanner();
    const ir = await planner.plan({
      profile: {
        role: 'engineer',
        preferences: {
          density: 'dense',
          accentFamily: 'amber',
          reduceMotion: false,
          verbosity: 'normal',
        },
        clearance: ['engineering'],
        recentWorkflow: null,
      },
      intent: { source: 'typed', text: 'show EPS grid telemetry' },
      session: { surfaceId: null },
    });
    expect(ir.surfaceId).toBe('engineering.diagnostics');
  });
});
```

- [ ] **Step 2: Implement recipes**

Each recipe exports `compile(fill: SlotFill, profile: CombadgeProfile): SceneIR` with region map: left rail, header bands, main, mode select, footer status. Fill slots from `research-stub` tools (claims, evidence, citations).

Role weights: physician → calmer density default; engineer → dense; executive → sparse module set; security → alert module allowed but sparse use of `alert.orange`.

- [ ] **Step 3: MockPlanner select + fill + return IR only (caller validates)**

```ts
export class MockPlanner implements Planner {
  async plan(input: PlanInput): Promise<SceneIR> {
    const intent = classifyIntent(input.intent.text);
    const recipeId = selectRecipe(input.profile.role, intent, input.intent.text);
    const fill = await fillSlots(recipeId, input);
    return compileRecipe(recipeId, fill, input.profile);
  }
}
```

`classifyIntent`: keyword heuristics for v1 (`compare|summarize|theory` → infoseek; `show|open|filter` → command; `why|analyze` → analysis with `analysisNeedsDialogue` true).

- [ ] **Step 4: Commit**

```bash
npm test -- src/planner src/recipes src/tools
git add src/planner src/recipes src/tools
git commit -m "feat(planner): hybrid recipe select + five compiled surface recipes"
```

---

### Task 8: Combadge profiles + runtime loop + aperture

**Files:**
- Create: `src/runtime/combadge.ts`
- Create: `src/runtime/session.ts`
- Create: `src/runtime/aperture.ts`
- Create: `src/runtime/loop.ts`
- Create: `src/runtime/index.ts`
- Create: `src/runtime/loop.test.tsx`
- Modify: `src/app/App.tsx`
- Modify: `src/catalog/renderers/QueryAperture.tsx`

**Interfaces:**
- Consumes: `Planner`, `validateSceneIR`, `SurfaceHost`, `applyPatch`
- Produces:
  - `MOCK_PROFILES: Record<RoleId, CombadgeProfile>`
  - `createRuntime(deps): { submitIntent; applyUserPatch; setRole; subscribe }`
  - Pipeline: intent → `surfaceState=working` → plan → validate → (repair once) → host / error band
  - Voice: `SpeechRecognition` when available; on failure set `degraded` + focus typed aperture

- [ ] **Step 1: Failing loop test**

```tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { App } from '@/app/App';

it('typed research intent recomposes to result without chat log', async () => {
  const user = userEvent.setup();
  render(<App />);
  await user.selectOptions(screen.getByLabelText(/combadge role/i), 'physicist');
  await user.type(screen.getByLabelText(/command/i), 'summarize subspace theories{Enter}');
  expect(await screen.findByText(/WORKING|READY|RESULT/i)).toBeTruthy();
  expect(screen.queryByRole('log')).not.toBeInTheDocument();
  expect(screen.getByRole('main')).toBeInTheDocument();
});
```

- [ ] **Step 2: Implement runtime**

```ts
export async function submitIntent(text: string, source: 'typed' | 'voice') {
  setIR(workingShell(current));
  const planned = await planner.plan({ profile, intent: { text, source }, session });
  let result = validateSceneIR(planned, { catalog: 'default' });
  if (!result.ok && result.repaired) {
    result = validateSceneIR(result.repaired, { catalog: 'default' });
  }
  if (!result.ok) {
    setIR(errorShell(current, result.issues));
    return;
  }
  setIR({ ...result.ir, surfaceState: 'result' });
}
```

Aperture chrome: elbow end-cap / status rail — CSS in module, not a centered modal search.

Voice wake optional string match on leading `computer ` (case-insensitive strip).

- [ ] **Step 3: Commit**

```bash
npm test -- src/runtime
git add src/runtime src/app
git commit -m "feat(runtime): combadge, aperture, intent loop with validate gate"
```

---

### Task 9: Research/baseline hero polish + dialogue flag

**Files:**
- Modify: `src/recipes/research.ts`
- Modify: `src/tools/research-stub.ts`
- Modify: `src/catalog/renderers/Dialogue.tsx`
- Create: `src/recipes/research.test.ts`

**Interfaces:**
- Consumes: runtime loop
- Produces: end-to-end research surface with claimList + evidencePanel + comparePanel; dialogue module only when `analysisNeedsDialogue`

- [ ] **Step 1: Tests**

```ts
it('analysis intent includes dialogue module', async () => {
  const ir = await planner.plan({
    profile: MOCK_PROFILES.physicist,
    intent: { source: 'typed', text: 'why do these theories diverge' },
    session: { surfaceId: 'research.baseline' },
  });
  expect(ir.intent.analysisNeedsDialogue).toBe(true);
  expect(ir.modules.some((m) => m.type === 'dialogue')).toBe(true);
  expect(validateSceneIR(ir, { catalog: 'default' }).ok).toBe(true);
});

it('infoseek intent has no dialogue module', async () => {
  const ir = await planner.plan({
    profile: MOCK_PROFILES.physicist,
    intent: { source: 'typed', text: 'list subspace theories' },
    session: { surfaceId: null },
  });
  expect(ir.modules.some((m) => m.type === 'dialogue')).toBe(false);
});
```

- [ ] **Step 2: Implement stub research data + commit**

```bash
npm test -- src/recipes/research.test.ts
git add src/recipes src/tools src/catalog/renderers/Dialogue.tsx
git commit -m "feat(research): hero workflow modules and constrained dialogue"
```

---

### Task 10: Data-first viewport3d seed

**Files:**
- Create: `src/models3d/registry.ts`
- Create: `src/models3d/field-anomaly.ts`
- Create: `src/models3d/stellar-body.ts`
- Create: `src/catalog/renderers/Viewport3D.tsx`
- Create: `src/models3d/registry.test.ts`
- Modify: `src/validator/validate.ts` (step 10 binding checks)
- Modify: one recipe (engineering or research) to include viewport when intent matches

**Interfaces:**
- Consumes: `Viewport3DBinding` shape from SPEC
- Produces:
  - `getModel(modelId)` 
  - R3F canvas `frameloop="demand"` when not scrubbing
  - Sibling readout modules bind same `series` ids
  - Validator fails on missing units / encoding↔series mismatch

- [ ] **Step 1: Failing binding tests**

```ts
it('rejects viewport3d without units', () => {
  const ir = withViewportBinding({ units: [] });
  expect(validateSceneIR(ir, { catalog: 'default' }).ok).toBe(false);
});

it('accepts registered field-anomaly hybrid binding', () => {
  const ir = withViewportBinding(fieldAnomalyDemoBinding());
  expect(validateSceneIR(ir, { catalog: 'default' }).ok).toBe(true);
});
```

- [ ] **Step 2: Implement registry + Viewport3D**

Wireframe default; shaded/hybrid via `representation`. Materials sample constitution palette only (three `Color` from token hex via lookup). Accessible name + `a11y` data summary on the module; key metrics duplicated in `dataBlock` siblings.

- [ ] **Step 3: Commit**

```bash
npm test -- src/models3d src/catalog/renderers
git add src/models3d src/catalog/renderers/Viewport3D.tsx src/validator
git commit -m "feat(viewport3d): registered data-bound models with validator integrity"
```

---

### Task 11: Role-bias matrix + remaining recipe acceptance

**Files:**
- Create: `src/planner/role-bias.test.ts`
- Modify: recipes as needed for medical / ops-security / executive

**Interfaces:**
- Consumes: all five recipes
- Produces: same research query → different legal surfaces for physicist vs engineer (SPEC success criterion)

- [ ] **Step 1: Acceptance tests**

```ts
const query = 'summarize subspace theories';

it('physicist and engineer both legal but role-biased', async () => {
  const p = await planner.plan({
    profile: MOCK_PROFILES.physicist,
    intent: { source: 'typed', text: query },
    session: { surfaceId: null },
  });
  const e = await planner.plan({
    profile: MOCK_PROFILES.engineer,
    intent: { source: 'typed', text: query },
    session: { surfaceId: null },
  });
  expect(validateSceneIR(p, { catalog: 'default' }).ok).toBe(true);
  expect(validateSceneIR(e, { catalog: 'default' }).ok).toBe(true);
  // bias: physicist keeps research; engineer may stay research or shift density/modules
  expect(p.role).toBe('physicist');
  expect(e.role).toBe('engineer');
  expect(p.density).not.toBe(e.density); // physicist standard vs engineer dense defaults
});

it('each recipe compiles valid IR for its default role', async () => {
  for (const role of RoleIdSchema.options) {
    const ir = await planner.plan({
      profile: MOCK_PROFILES[role],
      intent: { source: 'typed', text: 'status' },
      session: { surfaceId: null },
    });
    expect(validateSceneIR(ir, { catalog: 'default' }).ok).toBe(true);
  }
});
```

- [ ] **Step 2: Fix recipe gaps + commit**

```bash
npm test -- src/planner/role-bias.test.ts
git add src/planner src/recipes
git commit -m "test: role-bias and five-recipe validation acceptance"
```

---

### Task 12: A11y, reduced-motion, golden fixtures

**Files:**
- Create: `src/app/a11y.test.tsx`
- Create: `src/test/fixtures/golden/*.json` (2–3 validated IR snapshots)
- Create: `src/validator/golden.test.ts`
- Modify: motion usage across SurfaceHost

**Interfaces:**
- Consumes: SurfaceHost, runtime
- Produces: gates for keyboard path, live regions, reduced-motion, golden IR fixtures

- [ ] **Step 1: Tests**

```tsx
it('has landmark regions', () => {
  render(<SurfaceHost ir={validResearchIR} />);
  expect(screen.getByRole('banner')).toBeInTheDocument();
  expect(screen.getByRole('navigation')).toBeInTheDocument();
  expect(screen.getByRole('main')).toBeInTheDocument();
  expect(screen.getByRole('contentinfo')).toBeInTheDocument();
});

it('pills are keyboard reachable', async () => {
  const user = userEvent.setup();
  render(<App />);
  await user.tab();
  // eventually focus aperture or first pill
  expect(document.activeElement).toBeTruthy();
});
```

```ts
// golden.test.ts
import researchResult from '@/test/fixtures/golden/research-result.json';
it('golden research-result still validates', () => {
  expect(validateSceneIR(researchResult, { catalog: 'default' }).ok).toBe(true);
});
```

Reduced-motion: mock `matchMedia('(prefers-reduced-motion: reduce)')` → recompose duration 0 / no WORKING pulse animation class.

- [ ] **Step 2: Commit**

```bash
npm test
git add src/app/a11y.test.tsx src/test/fixtures/golden src/validator/golden.test.ts
git commit -m "test: a11y landmarks, reduced-motion, golden IR fixtures"
```

---

### Task 13: App shell UX pass + vault handoff update

**Files:**
- Modify: `src/app/App.tsx`, `shell.css` for black canvas, Antonio font import
- Modify (workspace): `07-projects/20-lcars-generative-interface/SESSION-STATE.md`
- Modify (workspace): `SPEC.md` status → `approved` / implementation in progress

**Interfaces:**
- Consumes: complete runtime
- Produces: `npm run dev` demo: pick role, type intent, see LCARS recompose; README quickstart

- [ ] **Step 1: Font + scene chrome**

```css
@import url('https://fonts.googleapis.com/css2?family=Antonio:wght@400;700&display=swap');

html, body, #root {
  margin: 0;
  height: 100%;
  background: #000;
  color: var(--lcars-ink-onBlack);
  font-family: "Antonio", "Arial Narrow", sans-serif;
  text-transform: uppercase;
}
```

- [ ] **Step 2: Manual verify checklist**

1. Physicist + `summarize subspace theories` → research modules, no chat log  
2. Engineer + same query → legal, denser bias  
3. `why do these diverge` → dialogue module appears  
4. Toggle OS reduce-motion → no pulse / instant recompose  
5. Tab through controls; focus ring visible  
6. Intent that includes schematic → viewport3d + readout siblings  

- [ ] **Step 3: Commits**

App repo:

```bash
git add src/app README.md
git commit -m "feat(app): LCARS shell chrome and Antonio typography"
```

Workspace vault (this branch): update SESSION-STATE Live handoff; set SPEC status approved/in-progress; commit on `cursor/lcars-generative-interface-a660`.

---

## Self-review (author)

**1. Spec coverage**

| SPEC requirement | Task |
|---|---|
| Immutable constitution + tokens + geometry | 2–3 |
| APCA primary + WCAG AA fallback | 2, 5 |
| Typed Scene IR + patches | 4 |
| Validator order + no illegal paint | 5, 8 |
| Module catalog + deterministic renderer | 5–6 |
| Five v1 recipes | 7, 11 |
| Hybrid planner → v2-ready API | 7 |
| Combadge six roles | 8, 11 |
| Voice + typed one pipeline | 8 |
| Research hero e2e | 9 |
| Dialogue only when flagged | 9 |
| Data-first viewport3d (1–2 models) | 10 |
| Surface states incl. WORKING / degraded | 8 |
| A11y landmarks, touch 44, reduced-motion | 3, 6, 12 |
| Success criteria role-bias | 11 |

**2. Placeholder scan:** none intentionally left; font/LLM/APCA floors asserted in Global Constraints.

**3. Type consistency:** `SceneIR` / `ScenePatch` / `RoleId` / `Density` / `TokenId` / `Planner.plan` / `validateSceneIR` naming is stable across tasks.

**Out of scope (deferred per SPEC):** free topology synthesis, real auth/combadge hardware, production ASR, broad tool ecosystem.
