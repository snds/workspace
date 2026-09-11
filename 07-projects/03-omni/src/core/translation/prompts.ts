// ─── AI Translation Engine — Prompt Builders ────────────────────────────────
// System prompts for Claude code generation. Each function builds a section
// of the system prompt based on the TeamContextProfile configuration.

import type { TeamContextProfile } from "@/core/context/types";
import type { TranslationScope } from "./types";

// ─── Main prompt builder ────────────────────────────────────────────────────

/**
 * Build a complete system prompt for code generation based on the team context
 * and translation scope.
 */
export function buildTranslationPrompt(
  context: TeamContextProfile,
  scope: TranslationScope,
): string {
  const sections: string[] = [
    getBaseInstructions(),
    getFrameworkSection(context),
    getStylingSection(context),
    getComponentLibSection(context),
    getCodePatternsSection(context),
  ];

  // Only include backend section for full-stack scope on tier >= 2
  if (scope === "full-stack" && context.tier >= 2) {
    sections.push(getBackendSection(context));
  }

  // Only include infra section for full-stack scope on tier >= 3
  if (scope === "full-stack" && context.tier >= 3) {
    sections.push(getInfraSection(context));
  }

  sections.push(getScopeInstructions(scope));
  sections.push(getOutputFormatInstructions());

  return sections.filter(Boolean).join("\n\n");
}

// ─── Base instructions ──────────────────────────────────────────────────────

function getBaseInstructions(): string {
  return `You are an expert full-stack code generator. You translate design specifications (described as an intermediate representation of visual nodes) into production-quality, idiomatic code.

Rules:
- Generate clean, well-structured, production-ready code.
- Use TypeScript throughout unless the target framework requires otherwise.
- Include proper type definitions for all props and data.
- Follow the naming conventions and file patterns specified below.
- Use semantic HTML elements where appropriate.
- Include accessibility attributes (aria-labels, roles, etc.).
- Do NOT include inline comments explaining obvious code.
- DO include brief comments for non-obvious logic.`;
}

// ─── Framework section ──────────────────────────────────────────────────────

/**
 * Build framework-specific instructions based on the selected framework
 * and meta-framework.
 */
export function getFrameworkSection(context: TeamContextProfile): string {
  const { framework } = context;
  const lines: string[] = [`## Framework: ${framework.id}`];

  if (framework.version) {
    lines.push(`Target version: ${framework.version}`);
  }

  if (framework.metaFramework && framework.metaFramework !== "none") {
    lines.push(`Meta-framework: ${framework.metaFramework}`);
  }

  switch (framework.id) {
    case "react":
      lines.push(`
- Use functional components with hooks.
- Prefer \`const\` arrow-function components.
- Use React.FC only when explicit children typing is needed.
- Destructure props in the function signature.
- Use \`useState\`, \`useEffect\`, \`useMemo\`, \`useCallback\` as appropriate.
- Use \`forwardRef\` for components that wrap native elements.`);

      if (framework.metaFramework === "nextjs") {
        lines.push(`
- Use the Next.js App Router (\`app/\` directory).
- Add \`"use client"\` directive for client components.
- Default to Server Components where possible.
- Use \`next/image\` for images, \`next/link\` for navigation.
- Use Route Handlers for API endpoints (\`app/api/\`).`);
      } else if (framework.metaFramework === "remix") {
        lines.push(`
- Use Remix loader/action patterns for data fetching.
- Use \`useLoaderData\` and \`useActionData\` hooks.
- Export \`loader\` and \`action\` functions from route modules.`);
      }
      break;

    case "vue":
      lines.push(`
- Use Vue 3 Composition API with \`<script setup>\` syntax.
- Use \`ref()\`, \`reactive()\`, \`computed()\`, \`watch()\` as appropriate.
- Define props with \`defineProps<T>()\` and emits with \`defineEmits<T>()\`.
- Use \`v-bind\`, \`v-on\`, \`v-if\`, \`v-for\` directives.`);

      if (framework.metaFramework === "nuxt") {
        lines.push(`
- Use Nuxt auto-imports for composables and components.
- Use \`useFetch\` and \`useAsyncData\` for data fetching.
- Use \`definePageMeta\` for page metadata.
- Use \`server/api/\` for API routes.`);
      }
      break;

    case "svelte":
      lines.push(`
- Use Svelte 5 runes (\`$state\`, \`$derived\`, \`$effect\`, \`$props\`).
- Use \`{#if}\`, \`{#each}\`, \`{#await}\` blocks.
- Export component props via \`$props()\`.`);

      if (framework.metaFramework === "sveltekit") {
        lines.push(`
- Use SvelteKit \`+page.svelte\` / \`+layout.svelte\` conventions.
- Use \`load\` functions in \`+page.ts\` / \`+page.server.ts\`.
- Use \`+server.ts\` for API endpoints.`);
      }
      break;

    case "angular":
      lines.push(`
- Use Angular standalone components.
- Use signals for reactivity where available.
- Use Angular template syntax (\`*ngIf\`, \`*ngFor\`, \`[ngClass]\`).
- Use dependency injection for services.`);
      break;

    case "solid":
      lines.push(`
- Use SolidJS signals (\`createSignal\`, \`createMemo\`, \`createEffect\`).
- Use \`<Show>\`, \`<For>\`, \`<Switch>\`/\`<Match>\` control-flow components.
- Props are accessed directly (no destructuring at the top level).`);
      break;

    case "react-native":
      lines.push(`
- Use React Native components (\`View\`, \`Text\`, \`Pressable\`, etc.).
- Use \`StyleSheet.create()\` for styles unless NativeWind/Tailwind is configured.
- Use platform-specific file extensions when needed (.ios.tsx, .android.tsx).`);
      break;

    default:
      break;
  }

  return lines.join("\n");
}

// ─── Styling section ────────────────────────────────────────────────────────

/**
 * Build styling-specific instructions based on the styling approach.
 */
export function getStylingSection(context: TeamContextProfile): string {
  const { styling } = context;
  const lines: string[] = [`## Styling: ${styling.approach}`];

  if (styling.version) {
    lines.push(`Version: ${styling.version}`);
  }

  switch (styling.approach) {
    case "tailwind":
      lines.push(`
- Use Tailwind CSS utility classes directly on elements.
- Use the \`cn()\` utility (clsx + tailwind-merge) for conditional classes.
- Prefer Tailwind tokens over arbitrary values: \`p-4\` not \`p-[16px]\`.
- Use responsive prefixes: \`sm:\`, \`md:\`, \`lg:\`, \`xl:\`.
- Use dark mode prefix when the app supports theme switching.
- Use CSS custom properties for design tokens: \`bg-[var(--color-primary)]\`.`);
      break;

    case "css-modules":
      lines.push(`
- Create a co-located \`.module.css\` file for each component.
- Import styles as \`import styles from './Component.module.css'\`.
- Use \`className={styles.root}\` pattern.
- Use CSS custom properties for design tokens.
- Use \`composes:\` for shared styles.`);
      break;

    case "styled-components":
      lines.push(`
- Use tagged template literals: \`styled.div\\\`...\\\`\`.
- Create styled components for semantic elements.
- Use the \`css\` helper for shared style blocks.
- Pass props for dynamic styling: \`\${(props) => props.variant}\`.
- Use \`ThemeProvider\` for design tokens.`);
      break;

    case "emotion":
      lines.push(`
- Use the \`css\` prop or \`styled\` API from @emotion/react.
- Prefer the \`css\` prop for one-off styles.
- Use \`styled\` for reusable styled components.
- Use the theme context for design tokens.`);
      break;

    case "vanilla-extract":
      lines.push(`
- Create \`.css.ts\` files for styles.
- Use \`style()\`, \`styleVariants()\`, and \`recipe()\`.
- Use \`createTheme()\` and \`createThemeContract()\` for tokens.
- Use \`sprinkles()\` for utility-style props.`);
      break;

    case "scss":
      lines.push(`
- Create co-located \`.module.scss\` or \`.scss\` files.
- Use SCSS variables, mixins, and nesting.
- Use \`@use\` and \`@forward\` for module system.
- Map design tokens to SCSS variables.`);
      break;

    default:
      break;
  }

  return lines.join("\n");
}

// ─── Component library section ──────────────────────────────────────────────

/**
 * Build component-library-specific instructions.
 */
export function getComponentLibSection(context: TeamContextProfile): string {
  const { componentLibrary, iconLibrary } = context;

  if (componentLibrary.id === "none") {
    return `## Component Library: None (build from scratch)
- Create components from primitive HTML elements.
- Ensure full accessibility compliance.`;
  }

  const lines: string[] = [`## Component Library: ${componentLibrary.id}`];

  if (componentLibrary.version) {
    lines.push(`Version: ${componentLibrary.version}`);
  }

  switch (componentLibrary.id) {
    case "shadcn":
      lines.push(`
- Import from \`@/components/ui/\` (shadcn convention).
- Use the shadcn component API (variant props, size props).
- Components: Button, Input, Card, Dialog, Select, Tabs, etc.
- Use \`cn()\` for class merging with component defaults.
- Compose primitives via Radix UI underneath.`);
      break;

    case "mui":
      lines.push(`
- Import from \`@mui/material\` and \`@mui/icons-material\`.
- Use the MUI \`sx\` prop for styling overrides.
- Use MUI theme tokens via \`useTheme()\`.
- Components: Button, TextField, Card, Dialog, Select, Tabs, etc.`);
      break;

    case "chakra":
      lines.push(`
- Import from \`@chakra-ui/react\`.
- Use Chakra style props directly on components.
- Use the Chakra theme for design tokens.
- Components: Button, Input, Card, Modal, Select, Tabs, etc.`);
      break;

    case "ant-design":
      lines.push(`
- Import from \`antd\`.
- Use Ant Design's ConfigProvider for theming.
- Components: Button, Input, Card, Modal, Select, Tabs, Table, etc.`);
      break;

    case "radix":
      lines.push(`
- Import from \`@radix-ui/react-*\` (each primitive is a separate package).
- These are unstyled primitives — apply styling via the configured approach.
- Use compound component pattern (Root, Trigger, Content, etc.).`);
      break;

    case "headless-ui":
      lines.push(`
- Import from \`@headlessui/react\`.
- These are unstyled — apply styling via the configured approach.
- Components: Menu, Dialog, Popover, Switch, Tab, etc.`);
      break;

    case "vuetify":
      lines.push(`
- Import from \`vuetify/components\`.
- Use Vuetify's \`v-\` prefix components.
- Use Vuetify's built-in theme system.
- Components: VBtn, VTextField, VCard, VDialog, VSelect, VTabs, etc.`);
      break;

    default:
      break;
  }

  // Icon library
  lines.push(`\n### Icon Library: ${iconLibrary.id}`);

  switch (iconLibrary.id) {
    case "lucide":
      lines.push(`- Import icons from \`lucide-react\` (e.g. \`import { Search } from "lucide-react"\`).`);
      break;
    case "phosphor":
      lines.push(`- Import icons from \`@phosphor-icons/react\`.`);
      break;
    case "heroicons":
      lines.push(`- Import icons from \`@heroicons/react/24/outline\` or \`@heroicons/react/24/solid\`.`);
      break;
    case "material-icons":
      lines.push(`- Import icons from \`@mui/icons-material\`.`);
      break;
    case "tabler":
      lines.push(`- Import icons from \`@tabler/icons-react\`.`);
      break;
    case "feather":
      lines.push(`- Import icons from \`react-feather\`.`);
      break;
    default:
      break;
  }

  return lines.join("\n");
}

// ─── Code patterns section ──────────────────────────────────────────────────

function getCodePatternsSection(context: TeamContextProfile): string {
  const { codePatterns } = context;

  return `## Code Conventions
- Variable naming: ${codePatterns.naming}
- File naming: ${codePatterns.fileNaming}
- Component file pattern: ${codePatterns.componentFilePattern}
${codePatterns.testFramework && codePatterns.testFramework !== "none" ? `- Test framework: ${codePatterns.testFramework} (${codePatterns.testPattern ?? "co-located"})` : ""}
${codePatterns.linter && codePatterns.linter !== "none" ? `- Linter: ${codePatterns.linter}` : ""}
${codePatterns.formatter && codePatterns.formatter !== "none" ? `- Formatter: ${codePatterns.formatter}` : ""}`;
}

// ─── Backend section ────────────────────────────────────────────────────────

/**
 * Build backend-specific instructions (Tier 2+).
 */
export function getBackendSection(context: TeamContextProfile): string {
  const { backend, database, auth } = context;

  if (backend.apiLayer === "none") {
    return "";
  }

  const lines: string[] = [`## Backend Stack`];

  // API layer
  lines.push(`- API paradigm: ${backend.apiLayer}`);

  if (backend.serverFramework && backend.serverFramework !== "none") {
    lines.push(`- Server framework: ${backend.serverFramework}`);
  }

  if (backend.orm && backend.orm !== "none") {
    lines.push(`- ORM: ${backend.orm}`);
  }

  if (backend.serverless) {
    lines.push(`- Deployment: serverless functions`);
  }

  // Database
  if (database.type !== "none") {
    lines.push(`- Database: ${database.type}${database.provider ? ` (${database.provider})` : ""}`);
  }

  // Auth
  if (auth.provider !== "none") {
    lines.push(`- Auth provider: ${auth.provider}`);
    if (auth.flows.length > 0) {
      lines.push(`- Auth flows: ${auth.flows.join(", ")}`);
    }
    if (auth.rbac) {
      lines.push(`- RBAC: enabled`);
    }
  }

  // API-specific patterns
  switch (backend.apiLayer) {
    case "trpc":
      lines.push(`
### tRPC patterns
- Define routers with \`router()\` and procedures with \`publicProcedure\` / \`protectedProcedure\`.
- Use Zod for input validation.
- Use \`@trpc/react-query\` hooks on the client.`);
      break;

    case "rest":
      lines.push(`
### REST patterns
- Use RESTful resource naming: \`/api/users\`, \`/api/users/:id\`.
- Return proper HTTP status codes.
- Use request validation middleware.`);
      break;

    case "graphql":
      lines.push(`
### GraphQL patterns
- Define schema with SDL or code-first approach.
- Use resolvers with proper typing.
- Include query and mutation operations.`);
      break;

    default:
      break;
  }

  // ORM-specific patterns
  if (backend.orm === "prisma") {
    lines.push(`
### Prisma patterns
- Import \`PrismaClient\` and use a singleton pattern.
- Use Prisma's generated types for full type safety.
- Use \`prisma.model.findMany()\`, \`create()\`, \`update()\`, \`delete()\`.`);
  } else if (backend.orm === "drizzle") {
    lines.push(`
### Drizzle patterns
- Define schema with \`pgTable()\`, \`mysqlTable()\`, etc.
- Use the \`db.select().from()\` query builder.
- Use \`drizzle-zod\` for schema-to-validation integration.`);
  }

  return lines.join("\n");
}

// ─── Infra section ──────────────────────────────────────────────────────────

function getInfraSection(context: TeamContextProfile): string {
  const { infra } = context;
  const lines: string[] = [`## Infrastructure`];

  lines.push(`- Hosting: ${infra.hosting}`);

  if (infra.environments.length > 0) {
    lines.push(`- Environments: ${infra.environments.map((e) => e.name).join(", ")}`);
  }

  if (infra.cicd && infra.cicd.provider !== "none") {
    lines.push(`- CI/CD: ${infra.cicd.provider}`);
  }

  if (infra.featureFlags) {
    lines.push(`- Feature flags: ${infra.featureFlags.provider}`);
  }

  if (infra.monitoring && infra.monitoring !== "none") {
    lines.push(`- Monitoring: ${infra.monitoring}`);
  }

  return lines.join("\n");
}

// ─── Scope-specific instructions ────────────────────────────────────────────

function getScopeInstructions(scope: TranslationScope): string {
  switch (scope) {
    case "component":
      return `## Scope: Component
Generate a single reusable component:
- The component file with full TypeScript props interface.
- A co-located styles file if the styling approach requires it.
- Export the component as a named export.`;

    case "page":
      return `## Scope: Page
Generate a full page with layout:
- The page component with layout structure.
- Child components used by the page.
- Any data fetching logic (loader, server component, etc.).
- Routing integration appropriate for the meta-framework.`;

    case "full-stack":
      return `## Scope: Full-Stack
Generate frontend AND backend code:
- Frontend components and pages.
- API routes / server endpoints.
- Data fetching hooks or utilities.
- Type definitions shared between frontend and backend.
- Auth middleware if authentication is configured.
- Database queries if an ORM is configured.`;

    case "tokens-only":
      return `## Scope: Tokens Only
Generate design token output files:
- CSS custom properties file.
- Theme configuration for the styling framework.
- TypeScript type definitions for tokens.`;

    case "styles-only":
      return `## Scope: Styles Only
Generate styling files:
- Component styles using the configured styling approach.
- Responsive breakpoint styles.
- State variant styles (hover, focus, active, disabled).`;
  }
}

// ─── Output format instructions ─────────────────────────────────────────────

/**
 * Instructions telling Claude how to format the output so we can parse it.
 */
export function getOutputFormatInstructions(): string {
  return `## Output Format

Output each file as a fenced code block with a \`filepath:\` prefix on the info line.
The format is:

\`\`\`filepath:path/to/file.tsx
// file contents here
\`\`\`

Rules:
- Each file must have its own fenced block with the filepath on the opening fence.
- Use the correct file extension (.tsx, .ts, .css, .vue, .svelte, etc.).
- Use relative paths from the project root (e.g. \`components/Button.tsx\`, \`app/api/route.ts\`).
- Generate ALL files needed — do not reference files you haven't generated.
- If a file imports from another generated file, use the correct relative import path.`;
}
