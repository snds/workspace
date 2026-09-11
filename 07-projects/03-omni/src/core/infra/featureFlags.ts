// ─── Feature Flags & A/B Testing ───────────────────────────────────────────────
// Flag creation, resolution, A/B test management, and code generation helpers.
// ──────────────────────────────────────────────────────────────────────────────

import type { FeatureFlag, ABTest, ABTestVariant } from "./types";

/** Create a new feature flag */
export function createFeatureFlag(
  key: string,
  name: string,
  type: FeatureFlag["type"] = "boolean",
  defaultValue?: unknown,
): FeatureFlag {
  return {
    key,
    name,
    type,
    defaultValue:
      defaultValue ??
      (type === "boolean"
        ? false
        : type === "string"
          ? ""
          : type === "number"
            ? 0
            : {}),
    environmentOverrides: {},
    enabled: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
}

/** Resolve a flag value for a given environment */
export function resolveFlagValue(
  flag: FeatureFlag,
  environmentId: string,
): unknown {
  if (!flag.enabled) return flag.defaultValue;
  return flag.environmentOverrides[environmentId] ?? flag.defaultValue;
}

/** Create an A/B test linked to a feature flag */
export function createABTest(
  name: string,
  flagKey: string,
  variants: ABTestVariant[],
  trackingEvent: string,
): ABTest {
  return {
    id: `test-${Date.now()}`,
    name,
    flagKey,
    variants,
    trafficSplit: variants.map(() => Math.floor(100 / variants.length)),
    trackingEvent,
    status: "draft",
  };
}

/** Generate code for a feature flag check */
export function generateFlagCheckCode(
  flag: FeatureFlag,
  framework: string,
): string {
  switch (framework) {
    case "react":
      return `const ${camelCase(flag.key)} = useFeatureFlag('${flag.key}');`;
    case "vue":
      return `const ${camelCase(flag.key)} = useFeatureFlag('${flag.key}');`;
    case "svelte":
      return `$: ${camelCase(flag.key)} = $featureFlags['${flag.key}'];`;
    default:
      return `const ${camelCase(flag.key)} = getFeatureFlag('${flag.key}');`;
  }
}

function camelCase(str: string): string {
  return str
    .replace(/-([a-z])/g, (_, c: string) => c.toUpperCase())
    .replace(/-/g, "");
}

/** Generate code for an A/B test wrapper component */
export function generateABTestCode(test: ABTest, framework: string): string {
  if (framework === "react") {
    const variants = test.variants
      .map((v) => `  ${JSON.stringify(v.flagValue)}: <${pascalCase(v.id)} />`)
      .join(",\n");
    return `<ABTest experiment="${test.id}" trackEvent="${test.trackingEvent}">\n  {{\n${variants}\n  }}\n</ABTest>`;
  }
  return `// A/B test: ${test.name}`;
}

function pascalCase(str: string): string {
  return str.replace(/(^|-)([a-z])/g, (_, _prefix: string, c: string) =>
    c.toUpperCase(),
  );
}
