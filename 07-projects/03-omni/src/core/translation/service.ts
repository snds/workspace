// ─── AI Translation Engine — Service ─────────────────────────────────────────
// The main translation service: IR + Team Context -> code files.
// Currently a stub — actual AI calls will use the platform abstraction
// from src/lib/ai/client.ts once integrated.

import type { IRNode } from "@/core/ir/types";
import { isTokenRef } from "@/core/ir/types";
import type { TranslationRequest, TranslationResult, GeneratedFile, FileCategory } from "./types";
import { buildTranslationPrompt } from "./prompts";

// ─── Main entry point ───────────────────────────────────────────────────────

/**
 * Translate IR nodes to code using the AI engine.
 *
 * Currently a stub that builds the prompts and returns placeholder results.
 * The actual AI call will use the platform abstraction (Tauri command or
 * web fetch) once the streaming relay is wired up for code generation.
 */
export async function translateToCode(
  request: TranslationRequest,
): Promise<TranslationResult> {
  // Build the system and user prompts (used when AI integration is wired up)
  const systemPrompt = buildTranslationPrompt(request.context, request.scope);
  const userPrompt = buildUserPrompt(request);

  // Retain prompt references for future AI integration
  void systemPrompt;
  void userPrompt;

  // ── Stub mode ──────────────────────────────────────────────────────────
  // In the future this will call:
  //   platform.ai.streamMessage({ systemPrompt, messages: [...], maxTokens })
  // and pipe the streamed response through parseTranslationResponse().

  return {
    files: [],
    warnings: [
      "Translation engine is in stub mode -- AI integration pending.",
      "System and user prompts have been built successfully.",
    ],
  };
}

// ─── User prompt builder ────────────────────────────────────────────────────

/**
 * Build the user message describing what to translate.
 * Serialises the IR nodes into a structured text description that the AI
 * can interpret to generate code.
 */
function buildUserPrompt(request: TranslationRequest): string {
  const { nodes, scope, instructions } = request;

  const sections: string[] = [];

  // Header
  sections.push(`Generate ${scope} code for the following design specification.`);

  // Additional instructions
  if (instructions) {
    sections.push(`\nAdditional instructions:\n${instructions}`);
  }

  // Describe each node
  sections.push("\n## Design Nodes\n");

  for (const node of nodes) {
    sections.push(describeIRNode(node, nodes));
  }

  return sections.join("\n");
}

/**
 * Describe a single IR node in human-readable form for the AI prompt.
 */
function describeIRNode(node: IRNode, allNodes: IRNode[]): string {
  const lines: string[] = [];
  const indent = getNodeDepth(node, allNodes);
  const prefix = "  ".repeat(indent);

  // Identity
  lines.push(`${prefix}### ${node.type}: "${node.name}" (${node.id})`);

  // Dimensions
  lines.push(`${prefix}- Position: (${node.x}, ${node.y})`);
  lines.push(`${prefix}- Size: ${node.width} x ${node.height}`);

  // Component reference
  if (node.componentRef) {
    lines.push(`${prefix}- Component: ${node.componentRef.catalogId}`);
    if (node.componentRef.variant) {
      lines.push(`${prefix}  Variant: ${node.componentRef.variant}`);
    }
    if (node.componentRef.propOverrides) {
      lines.push(`${prefix}  Props: ${JSON.stringify(node.componentRef.propOverrides)}`);
    }
  }

  // Text content
  if (node.text) {
    lines.push(`${prefix}- Text: "${node.text}"`);
  }

  // Typography
  if (node.typographySlots) {
    const typo = node.typographySlots;
    const parts: string[] = [];
    if (typo.fontFamily) parts.push(`font: ${resolveValue(typo.fontFamily)}`);
    if (typo.fontSize) parts.push(`size: ${resolveValue(typo.fontSize)}`);
    if (typo.fontWeight) parts.push(`weight: ${resolveValue(typo.fontWeight)}`);
    if (typo.lineHeight) parts.push(`lh: ${resolveValue(typo.lineHeight)}`);
    if (parts.length) lines.push(`${prefix}- Typography: ${parts.join(", ")}`);
  }

  // Color slots
  if (node.colorSlots) {
    const colors = node.colorSlots;
    const parts: string[] = [];
    if (colors.background) parts.push(`bg: ${resolveValue(colors.background)}`);
    if (colors.foreground) parts.push(`fg: ${resolveValue(colors.foreground)}`);
    if (colors.border) parts.push(`border: ${resolveValue(colors.border)}`);
    if (colors.accent) parts.push(`accent: ${resolveValue(colors.accent)}`);
    if (parts.length) lines.push(`${prefix}- Colors: ${parts.join(", ")}`);
  }

  // Spacing slots
  if (node.spacingSlots) {
    const sp = node.spacingSlots;
    const parts: string[] = [];
    if (sp.paddingTop) parts.push(`pt: ${resolveValue(sp.paddingTop)}`);
    if (sp.paddingRight) parts.push(`pr: ${resolveValue(sp.paddingRight)}`);
    if (sp.paddingBottom) parts.push(`pb: ${resolveValue(sp.paddingBottom)}`);
    if (sp.paddingLeft) parts.push(`pl: ${resolveValue(sp.paddingLeft)}`);
    if (sp.gap) parts.push(`gap: ${resolveValue(sp.gap)}`);
    if (parts.length) lines.push(`${prefix}- Spacing: ${parts.join(", ")}`);
  }

  // Layout
  if (node.layoutMode && node.layoutMode !== "NONE") {
    lines.push(`${prefix}- Layout: ${node.layoutMode}`);
    if (node.primaryAxisAlignment) {
      lines.push(`${prefix}  Main axis: ${node.primaryAxisAlignment}`);
    }
    if (node.counterAxisAlignment) {
      lines.push(`${prefix}  Cross axis: ${node.counterAxisAlignment}`);
    }
    if (node.itemSpacing) {
      lines.push(`${prefix}  Gap: ${resolveValue(node.itemSpacing)}`);
    }
  }

  // Data bindings
  if (node.dataBindings && node.dataBindings.length > 0) {
    lines.push(`${prefix}- Data bindings:`);
    for (const binding of node.dataBindings) {
      lines.push(`${prefix}  - ${binding.propName} <- ${binding.sourceId}.${binding.fieldPath}`);
      if (binding.transform) {
        lines.push(`${prefix}    Transform: ${binding.transform}`);
      }
    }
  }

  // Event handlers
  if (node.eventHandlers && node.eventHandlers.length > 0) {
    lines.push(`${prefix}- Events:`);
    for (const handler of node.eventHandlers) {
      lines.push(`${prefix}  - ${handler.event} -> ${handler.action}("${handler.target}")`);
    }
  }

  // Feature flag gate
  if (node.featureGate) {
    lines.push(`${prefix}- Feature gate: ${node.featureGate.flagKey} in [${node.featureGate.values.join(", ")}]`);
    if (node.featureGate.fallback) {
      lines.push(`${prefix}  Fallback: ${node.featureGate.fallback}`);
    }
  }

  // i18n keys
  if (node.i18nKeys && Object.keys(node.i18nKeys).length > 0) {
    lines.push(`${prefix}- i18n: ${JSON.stringify(node.i18nKeys)}`);
  }

  // State overrides
  if (node.stateOverrides && node.stateOverrides.length > 0) {
    lines.push(`${prefix}- States: ${node.stateOverrides.map((s) => s.state).join(", ")}`);
  }

  // Breakpoint rules
  if (node.breakpointRules && node.breakpointRules.length > 0) {
    lines.push(`${prefix}- Responsive: ${node.breakpointRules.map((b) => b.breakpoint).join(", ")}`);
  }

  // Icon reference
  if (node.iconRef) {
    lines.push(`${prefix}- Icon: ${node.iconRef.name}`);
    if (node.iconRef.size) lines.push(`${prefix}  Size: ${resolveValue(node.iconRef.size)}`);
    if (node.iconRef.color) lines.push(`${prefix}  Color: ${resolveValue(node.iconRef.color)}`);
  }

  // Slot definition
  if (node.slotDef) {
    lines.push(`${prefix}- Slot: "${node.slotDef.name}"`);
  }

  lines.push(""); // blank line separator
  return lines.join("\n");
}

// ─── Response parser ────────────────────────────────────────────────────────

/**
 * Parse an AI response containing fenced code blocks into `GeneratedFile[]`.
 *
 * Expected format:
 * ```filepath:path/to/file.tsx
 * // code here
 * ```
 */
export function parseTranslationResponse(response: string): GeneratedFile[] {
  const files: GeneratedFile[] = [];

  // Match code blocks with the filepath: prefix
  // Pattern: ```filepath:some/path.ext\n...content...\n```
  const codeBlockPattern = /```filepath:([^\n]+)\n([\s\S]*?)```/g;

  let match: RegExpExecArray | null;
  while ((match = codeBlockPattern.exec(response)) !== null) {
    const filePath = match[1].trim();
    const content = match[2].trimEnd();
    const language = detectLanguage(filePath);
    const category = detectCategory(filePath);

    files.push({
      path: filePath,
      content,
      language,
      category,
    });
  }

  return files;
}

// ─── Helpers ────────────────────────────────────────────────────────────────

/** Resolve a TokenOrLiteral value to a string representation. */
function resolveValue(value: unknown): string {
  if (isTokenRef(value)) {
    return `{${value.$ref}}`;
  }
  return String(value);
}

/** Calculate the depth of a node in the tree (for indentation). */
function getNodeDepth(node: IRNode, allNodes: IRNode[]): number {
  let depth = 0;
  let current = node;
  while (current.parentId) {
    const parent = allNodes.find((n) => n.id === current.parentId);
    if (!parent) break;
    current = parent;
    depth++;
  }
  return depth;
}

/** Detect programming language from file extension. */
function detectLanguage(filePath: string): string {
  const ext = filePath.split(".").pop()?.toLowerCase() ?? "";

  const languageMap: Record<string, string> = {
    tsx: "tsx",
    ts: "typescript",
    jsx: "jsx",
    js: "javascript",
    vue: "vue",
    svelte: "svelte",
    css: "css",
    scss: "scss",
    less: "less",
    html: "html",
    json: "json",
    yaml: "yaml",
    yml: "yaml",
    md: "markdown",
    sql: "sql",
    prisma: "prisma",
    graphql: "graphql",
    gql: "graphql",
    dockerfile: "dockerfile",
    py: "python",
    rb: "ruby",
    rs: "rust",
    go: "go",
    java: "java",
    kt: "kotlin",
    swift: "swift",
    dart: "dart",
  };

  return languageMap[ext] ?? "plaintext";
}

/** Detect the file category based on path patterns. */
function detectCategory(filePath: string): FileCategory {
  const lower = filePath.toLowerCase();

  // Test files
  if (
    lower.includes(".test.") ||
    lower.includes(".spec.") ||
    lower.includes("__tests__") ||
    lower.includes("__test__")
  ) {
    return "test";
  }

  // Type definition files
  if (lower.endsWith(".d.ts") || lower.includes("/types/") || lower.includes("/types.ts")) {
    return "types";
  }

  // Config files
  if (
    lower.includes(".config.") ||
    lower.includes("dockerfile") ||
    lower.endsWith(".yml") ||
    lower.endsWith(".yaml") ||
    lower.endsWith(".json") ||
    lower.endsWith(".env") ||
    lower.includes("vercel.json") ||
    lower.includes(".github/")
  ) {
    return "config";
  }

  // Styling files
  if (
    lower.endsWith(".css") ||
    lower.endsWith(".scss") ||
    lower.endsWith(".less") ||
    lower.includes(".module.css") ||
    lower.includes(".module.scss") ||
    lower.includes("css.ts")
  ) {
    return "styling";
  }

  // Backend files
  if (
    lower.includes("api/") ||
    lower.includes("server/") ||
    lower.includes("middleware") ||
    lower.includes("prisma/") ||
    lower.includes("drizzle/") ||
    lower.includes("trpc/") ||
    lower.endsWith(".sql") ||
    lower.endsWith(".prisma")
  ) {
    return "backend";
  }

  // Default to frontend
  return "frontend";
}
