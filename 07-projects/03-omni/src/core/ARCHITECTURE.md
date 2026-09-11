# Omni Architecture: "Design Once, Output Anywhere"

## Three-Layer Architecture

```
Layer 1: Semantic Design IR          (what the designer creates)
  ├─ Framework-agnostic node tree (IRNode)
  ├─ Token-referenced visual properties (TokenOrLiteral<T>)
  ├─ Component blueprints with props/slots/events/variants
  ├─ Semantic icon references ("action/delete" not "Trash2")
  ├─ Data bindings (component props → data sources / API fields)
  ├─ Interaction states + responsive rules
  └─ Feature flag gates (conditional rendering per flag value)

Layer 2: Team Context Profile        (who it's for)
  ├─ FRONTEND: Framework, component lib, icon lib, styling, tokens
  ├─ BACKEND: API layer (REST/GraphQL/tRPC), database, cloud provider
  ├─ AUTH: Provider (Clerk/Auth0/Supabase/Firebase/custom), auth flows
  ├─ DATA: Data sources (databases, APIs, services), connection configs
  ├─ INFRA: Environments (dev/staging/prod), feature flags, CI/CD
  ├─ I18N: Localization strategy, supported locales, string management
  └─ PATTERNS: Naming conventions, file structure, testing approach

Layer 3: AI Translation Engine       (how it becomes code)
  ├─ IR + Context → Claude → idiomatic full-stack code
  ├─ Frontend: components, pages, routing, state, styling
  ├─ Backend: API routes, data fetching, auth middleware, validation
  ├─ Infra: env configs, feature flag setup, deployment configs
  ├─ Validation pipeline (compile → lint → structural diff)
  └─ MCP integration for editor connectivity
```

## Directory Structure

```
src/core/
  ├─ ir/                    # Layer 1: Semantic Design IR
  │   ├─ types.ts           # IRNode, TokenRef, TokenOrLiteral<T>, DataBinding, etc.
  │   ├─ compat.ts          # canvasNodeToIR() / irNodeToCanvasNode() bridge
  │   ├─ resolver.ts        # TokenResolver — resolves token references
  │   └─ index.ts
  │
  ├─ icons/                 # Semantic Icon Registry
  │   ├─ types.ts           # IconName, IconData, IconAdapter interface
  │   ├─ registry.ts        # IconRegistry — adapters + semantic name mapping
  │   ├─ adapters/          # lucide.ts, iconify.ts
  │   ├─ OmniIcon.tsx       # <OmniIcon name="action/delete" />
  │   ├─ IconRegistryProvider.tsx
  │   └─ index.ts
  │
  ├─ tokens/                # Enhanced Token Pipeline
  │   ├─ tiers.ts           # classifyTier(), validateTierReferences()
  │   ├─ pipeline.ts        # TokenPipeline — multi-format output
  │   ├─ componentTokens.ts # Component-scoped token definitions
  │   └─ index.ts
  │
  ├─ context/               # Layer 2: Team Context Profile
  │   ├─ types.ts           # Full-stack TeamContextProfile
  │   ├─ defaults.ts        # Presets (Next.js+Prisma+Vercel, etc.)
  │   └─ index.ts
  │
  ├─ components/            # Component Catalog
  │   ├─ types.ts           # ComponentBlueprint, props, slots, variants
  │   ├─ catalog.ts         # ComponentCatalog class
  │   ├─ toIRNodes.ts       # Blueprint + overrides → IRNode tree
  │   ├─ builtin/           # ~25 component definitions
  │   └─ index.ts
  │
  ├─ renderer/              # Canvas Renderer Abstraction
  │   ├─ types.ts           # CanvasRenderer interface
  │   ├─ konva-renderer.ts  # Konva/Canvas2D implementation
  │   ├─ interaction-state.ts # Mutable state for 60fps canvas ops
  │   └─ index.ts
  │
  ├─ translation/           # Layer 3: AI Translation Engine
  │   ├─ types.ts           # TranslationRequest, TranslationResult
  │   ├─ service.ts         # IR + Context → Claude → code
  │   ├─ prompts.ts         # Per-framework system prompts
  │   ├─ validator.ts       # Compile check, lint, structural diff
  │   ├─ generators/        # frontend.ts, backend.ts, infra.ts
  │   └─ index.ts
  │
  ├─ data/                  # Data Source Integration
  │   ├─ types.ts           # DataSource, DataQuery, DataBinding
  │   ├─ registry.ts        # DataSourceRegistry
  │   ├─ adapters/          # rest.ts, graphql.ts, supabase.ts
  │   ├─ mock.ts            # Mock data generator
  │   └─ index.ts
  │
  ├─ infra/                 # Production Pipeline
  │   ├─ types.ts           # Environment, FeatureFlag, ABTest
  │   ├─ environments.ts    # Environment config management
  │   ├─ featureFlags.ts    # Feature flag management
  │   ├─ cicd.ts            # CI/CD pipeline generation
  │   └─ index.ts
  │
  └─ theme/                 # Omni's own token-driven theme
      ├─ omniTokens.ts      # DTCG tokens for Omni's UI
      └─ ThemeProvider.tsx   # Injects tokens as CSS custom properties

src/stores/
  ├─ teamContext.store.ts   # Active profile + presets
  ├─ iconRegistry.store.ts  # Registry instance + active adapter
  ├─ componentCatalog.store.ts # Catalog + custom blueprints
  ├─ canvas.ir.ts           # IR selectors/actions wrapping canvas.store
  ├─ data.store.ts          # Data sources + connections
  └─ infra.store.ts         # Environments + feature flags
```

## Usage Tiers (Progressive Disclosure)

Each tier is self-contained. Higher tiers' features are HIDDEN when inactive.

| Tier | Scope | Users |
|------|-------|-------|
| 0 | Design Only | Designers who hand off to developers |
| 1 | Design + Frontend | Designers who want production-ready components |
| 2 | Design + Full-Stack | Teams building complete applications |
| 3 | Design + Full-Stack + Production | Teams managing the full application lifecycle |

## Migration Strategy

Incremental via compatibility layer (`src/core/ir/compat.ts`):
1. Canvas store keeps CanvasNode[] internally during migration
2. IR actions convert IRNode → CanvasNode on write
3. IR selectors convert CanvasNode → IRNode on read
4. When all consumers migrate, flip store to IRNode-native
5. Remove compatibility layer
