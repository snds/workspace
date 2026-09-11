// ─── AI Translation Engine — Frontend Generator ─────────────────────────────
// Template-based frontend code generation from IR nodes.
// Used for simple components that don't need AI interpretation.
// For complex components, use the AI translation service instead.

import type { IRNode } from "@/core/ir/types";
import { isTokenRef } from "@/core/ir/types";
import type { TeamContextProfile } from "@/core/context/types";
import type { LibraryMapping } from "@/core/components/types";
import type { GeneratedFile } from "../types";

// ─── Main entry point ───────────────────────────────────────────────────────

/**
 * Generate frontend component files from IR nodes.
 * Dispatches to the appropriate framework generator.
 */
export function generateFrontendFiles(
  nodes: IRNode[],
  context: TeamContextProfile,
): GeneratedFile[] {
  const { framework } = context;

  switch (framework.id) {
    case "react":
    case "react-native":
      return generateReactFiles(nodes, context);
    case "vue":
      return generateVueFiles(nodes, context);
    case "svelte":
      return generateSvelteFiles(nodes, context);
    default:
      // Fallback to React for unsupported frameworks
      return generateReactFiles(nodes, context);
  }
}

// ─── React generator ────────────────────────────────────────────────────────

function generateReactFiles(
  nodes: IRNode[],
  context: TeamContextProfile,
): GeneratedFile[] {
  const files: GeneratedFile[] = [];

  // Find root-level nodes (no parentId)
  const rootNodes = nodes.filter((n) => n.parentId === null);

  for (const root of rootNodes) {
    const componentName = toComponentName(root.name);
    const children = nodes.filter((n) => n.parentId === root.id);
    const props = generateProps(root, nodes);
    const imports = generateImports(root, nodes, context);
    const jsx = irNodeToReactJSX(root, nodes, context, 2);

    const fileName = formatFileName(componentName, context);
    const filePath = buildFilePath(fileName, componentName, context);

    const content = `${imports}\n\n${props}\n\nexport function ${componentName}(${props ? `props: ${componentName}Props` : ""}) {\n  return (\n${jsx}\n  );\n}\n`;

    files.push({
      path: filePath,
      content,
      language: "tsx",
      category: "frontend",
    });

    // Generate co-located styles if needed
    const stylesFile = generateStylesFile(root, children, componentName, context);
    if (stylesFile) {
      files.push(stylesFile);
    }
  }

  return files;
}

// ─── Vue generator ──────────────────────────────────────────────────────────

function generateVueFiles(
  nodes: IRNode[],
  context: TeamContextProfile,
): GeneratedFile[] {
  const files: GeneratedFile[] = [];

  const rootNodes = nodes.filter((n) => n.parentId === null);

  for (const root of rootNodes) {
    const componentName = toComponentName(root.name);
    const sfc = irNodeToVueSFC(root, nodes, context);
    const fileName = formatFileName(componentName, context);

    files.push({
      path: `components/${fileName}.vue`,
      content: sfc,
      language: "vue",
      category: "frontend",
    });
  }

  return files;
}

// ─── Svelte generator ───────────────────────────────────────────────────────

function generateSvelteFiles(
  nodes: IRNode[],
  context: TeamContextProfile,
): GeneratedFile[] {
  const files: GeneratedFile[] = [];

  const rootNodes = nodes.filter((n) => n.parentId === null);

  for (const root of rootNodes) {
    const componentName = toComponentName(root.name);
    const component = irNodeToSvelteComponent(root, nodes, context);
    const fileName = formatFileName(componentName, context);

    files.push({
      path: `components/${fileName}.svelte`,
      content: component,
      language: "svelte",
      category: "frontend",
    });
  }

  return files;
}

// ─── IR to React JSX ────────────────────────────────────────────────────────

/**
 * Convert an IR node tree to a React JSX string.
 */
export function irNodeToReactJSX(
  node: IRNode,
  allNodes: IRNode[],
  context: TeamContextProfile,
  indent: number = 0,
): string {
  const pad = "  ".repeat(indent);
  const children = allNodes.filter((n) => n.parentId === node.id);

  // Component instance — use the library mapping
  if (node.type === "component-instance" && node.componentRef) {
    const mapping = getLibraryMapping(node.componentRef.catalogId, context);
    if (mapping) {
      const propStr = buildReactProps(node, mapping);
      if (children.length === 0) {
        return `${pad}<${mapping.componentName}${propStr} />`;
      }
      const childJsx = children
        .map((child) => irNodeToReactJSX(child, allNodes, context, indent + 1))
        .join("\n");
      return `${pad}<${mapping.componentName}${propStr}>\n${childJsx}\n${pad}</${mapping.componentName}>`;
    }
  }

  // Icon node
  if (node.type === "icon" && node.iconRef) {
    const iconName = toPascalCase(node.iconRef.name);
    const sizeAttr = node.iconRef.size
      ? ` size={${resolveJSXValue(node.iconRef.size)}}`
      : "";
    const colorAttr = node.iconRef.color
      ? ` color={${resolveJSXValue(node.iconRef.color)}}`
      : "";
    return `${pad}<${iconName}${sizeAttr}${colorAttr} />`;
  }

  // Slot node
  if (node.type === "slot" && node.slotDef) {
    return `${pad}{props.${node.slotDef.name} ?? <>${node.slotDef.fallbackChildren ? "/* fallback */" : ""}null</>}`;
  }

  // Text node
  if (node.type === "text") {
    const className = buildClassName(node, context);
    const tag = node.text?.length && node.text.length > 100 ? "p" : "span";
    const textContent = node.dataBindings?.find((b) => b.propName === "text")
      ? `{${node.dataBindings.find((b) => b.propName === "text")!.sourceId}.${node.dataBindings.find((b) => b.propName === "text")!.fieldPath}}`
      : node.text ?? "";
    return `${pad}<${tag}${className}>${textContent}</${tag}>`;
  }

  // Frame / container node
  const tag = inferHTMLTag(node);
  const className = buildClassName(node, context);
  const eventAttrs = buildEventAttributes(node);
  const gateOpen = node.featureGate
    ? `${pad}{isFeatureEnabled("${node.featureGate.flagKey}") && (\n`
    : "";
  const gateClose = node.featureGate ? `${pad})}\n` : "";

  if (children.length === 0) {
    const selfClose = `${pad}<${tag}${className}${eventAttrs} />`;
    return gateOpen ? `${gateOpen}  ${selfClose}\n${gateClose}` : selfClose;
  }

  const childJsx = children
    .map((child) => irNodeToReactJSX(child, allNodes, context, indent + 1))
    .join("\n");

  const element = `${pad}<${tag}${className}${eventAttrs}>\n${childJsx}\n${pad}</${tag}>`;
  return gateOpen ? `${gateOpen}  ${element}\n${gateClose}` : element;
}

// ─── IR to Vue SFC ──────────────────────────────────────────────────────────

/**
 * Convert an IR node tree to a Vue Single File Component.
 */
export function irNodeToVueSFC(
  root: IRNode,
  allNodes: IRNode[],
  context: TeamContextProfile,
): string {
  const componentName = toComponentName(root.name);
  const propDefs = extractPropDefs(root, allNodes);
  const template = irNodeToVueTemplate(root, allNodes, context, 2);

  const scriptSetup = propDefs.length > 0
    ? `<script setup lang="ts">\n${generateVuePropsInterface(componentName, propDefs)}\n</script>`
    : `<script setup lang="ts">\n// ${componentName}\n</script>`;

  const templateSection = `<template>\n${template}\n</template>`;

  const styleSection = context.styling.approach === "scss"
    ? `<style scoped lang="scss">\n/* ${componentName} styles */\n</style>`
    : `<style scoped>\n/* ${componentName} styles */\n</style>`;

  return `${scriptSetup}\n\n${templateSection}\n\n${styleSection}\n`;
}

function irNodeToVueTemplate(
  node: IRNode,
  allNodes: IRNode[],
  context: TeamContextProfile,
  indent: number,
): string {
  const pad = "  ".repeat(indent);
  const children = allNodes.filter((n) => n.parentId === node.id);
  const tag = inferHTMLTag(node);
  const className = buildVueClassName(node, context);

  if (node.type === "text") {
    const textContent = node.dataBindings?.find((b) => b.propName === "text")
      ? `{{ ${node.dataBindings.find((b) => b.propName === "text")!.sourceId}.${node.dataBindings.find((b) => b.propName === "text")!.fieldPath} }}`
      : node.text ?? "";
    return `${pad}<${tag}${className}>${textContent}</${tag}>`;
  }

  if (children.length === 0) {
    return `${pad}<${tag}${className} />`;
  }

  const childTemplate = children
    .map((child) => irNodeToVueTemplate(child, allNodes, context, indent + 1))
    .join("\n");

  return `${pad}<${tag}${className}>\n${childTemplate}\n${pad}</${tag}>`;
}

// ─── IR to Svelte Component ─────────────────────────────────────────────────

/**
 * Convert an IR node tree to a Svelte component.
 */
export function irNodeToSvelteComponent(
  root: IRNode,
  allNodes: IRNode[],
  context: TeamContextProfile,
): string {
  const propDefs = extractPropDefs(root, allNodes);
  const template = irNodeToSvelteTemplate(root, allNodes, context, 0);

  const scriptSection = propDefs.length > 0
    ? `<script lang="ts">\n  let { ${propDefs.map((p) => `${p.name}${p.defaultValue !== undefined ? ` = $bindable(${JSON.stringify(p.defaultValue)})` : ""}`).join(", ")} } = $props<{\n${propDefs.map((p) => `    ${p.name}${p.required ? "" : "?"}: ${p.type};`).join("\n")}\n  }>();\n</script>`
    : `<script lang="ts">\n  // Component props\n</script>`;

  const styleSection = `<style>\n  /* Component styles */\n</style>`;

  return `${scriptSection}\n\n${template}\n\n${styleSection}\n`;
}

function irNodeToSvelteTemplate(
  node: IRNode,
  allNodes: IRNode[],
  context: TeamContextProfile,
  indent: number,
): string {
  const pad = "  ".repeat(indent);
  const children = allNodes.filter((n) => n.parentId === node.id);
  const tag = inferHTMLTag(node);
  const className = buildClassName(node, context);

  if (node.type === "text") {
    const textContent = node.dataBindings?.find((b) => b.propName === "text")
      ? `{${node.dataBindings.find((b) => b.propName === "text")!.sourceId}.${node.dataBindings.find((b) => b.propName === "text")!.fieldPath}}`
      : node.text ?? "";
    return `${pad}<${tag}${className}>${textContent}</${tag}>`;
  }

  // Feature gate
  if (node.featureGate) {
    const gateContent = children.length === 0
      ? `${pad}<${tag}${className} />`
      : `${pad}<${tag}${className}>\n${children.map((c) => irNodeToSvelteTemplate(c, allNodes, context, indent + 1)).join("\n")}\n${pad}</${tag}>`;

    return `${pad}{#if isFeatureEnabled("${node.featureGate.flagKey}")}\n${gateContent}\n${pad}{/if}`;
  }

  if (children.length === 0) {
    return `${pad}<${tag}${className} />`;
  }

  const childTemplate = children
    .map((child) => irNodeToSvelteTemplate(child, allNodes, context, indent + 1))
    .join("\n");

  return `${pad}<${tag}${className}>\n${childTemplate}\n${pad}</${tag}>`;
}

// ─── Import generation ──────────────────────────────────────────────────────

/**
 * Build import statements from library mappings and component references.
 */
export function generateImports(
  root: IRNode,
  allNodes: IRNode[],
  context: TeamContextProfile,
): string {
  const imports: string[] = [];
  const importedComponents = new Set<string>();
  const importedIcons = new Set<string>();

  // Collect all nodes in the tree
  const treeNodes = [root, ...allNodes.filter((n) => isDescendant(n, root.id, allNodes))];

  for (const node of treeNodes) {
    // Component imports
    if (node.type === "component-instance" && node.componentRef) {
      const mapping = getLibraryMapping(node.componentRef.catalogId, context);
      if (mapping && !importedComponents.has(mapping.componentName)) {
        importedComponents.add(mapping.componentName);
        imports.push(`import { ${mapping.componentName} } from "${mapping.importPath}";`);

        if (mapping.additionalImports) {
          for (const additionalImport of mapping.additionalImports) {
            imports.push(additionalImport);
          }
        }
      }
    }

    // Icon imports
    if (node.type === "icon" && node.iconRef) {
      const iconName = toPascalCase(node.iconRef.name);
      if (!importedIcons.has(iconName)) {
        importedIcons.add(iconName);
        const iconImport = getIconImport(iconName, context);
        if (iconImport) imports.push(iconImport);
      }
    }
  }

  // Add styling imports
  if (context.styling.approach === "tailwind") {
    imports.push('import { cn } from "@/lib/utils";');
  }

  return imports.join("\n");
}

// ─── Props generation ───────────────────────────────────────────────────────

/**
 * Build TypeScript prop interfaces from component props.
 */
export function generateProps(root: IRNode, allNodes: IRNode[]): string {
  const propDefs = extractPropDefs(root, allNodes);

  if (propDefs.length === 0) return "";

  const componentName = toComponentName(root.name);
  const lines: string[] = [`interface ${componentName}Props {`];

  for (const prop of propDefs) {
    const optional = prop.required ? "" : "?";
    lines.push(`  ${prop.name}${optional}: ${prop.type};`);
  }

  lines.push("}");
  return lines.join("\n");
}

// ─── Internal helpers ───────────────────────────────────────────────────────

interface PropDef {
  name: string;
  type: string;
  required: boolean;
  defaultValue?: unknown;
}

function extractPropDefs(root: IRNode, allNodes: IRNode[]): PropDef[] {
  const props: PropDef[] = [];
  const treeNodes = [root, ...allNodes.filter((n) => isDescendant(n, root.id, allNodes))];

  // Extract props from data bindings
  for (const node of treeNodes) {
    if (node.dataBindings) {
      for (const binding of node.dataBindings) {
        if (!props.some((p) => p.name === binding.sourceId)) {
          props.push({
            name: binding.sourceId,
            type: "unknown",
            required: true,
          });
        }
      }
    }

    // Extract props from slots
    if (node.type === "slot" && node.slotDef) {
      props.push({
        name: node.slotDef.name,
        type: "React.ReactNode",
        required: false,
      });
    }
  }

  // Extract props from component ref overrides
  if (root.componentRef?.propOverrides) {
    for (const [key, value] of Object.entries(root.componentRef.propOverrides)) {
      if (!props.some((p) => p.name === key)) {
        props.push({
          name: key,
          type: typeof value === "string" ? "string" : typeof value === "number" ? "number" : typeof value === "boolean" ? "boolean" : "unknown",
          required: false,
          defaultValue: value,
        });
      }
    }
  }

  return props;
}

function isDescendant(node: IRNode, ancestorId: string, allNodes: IRNode[]): boolean {
  let current = node;
  while (current.parentId) {
    if (current.parentId === ancestorId) return true;
    const parent = allNodes.find((n) => n.id === current.parentId);
    if (!parent) return false;
    current = parent;
  }
  return false;
}

function getLibraryMapping(
  catalogId: string,
  _context: TeamContextProfile,
): LibraryMapping | null {
  // In a real implementation, this would look up the blueprint registry
  // For now, return a basic mapping based on the catalogId
  return {
    library: "custom",
    importPath: `@/components/ui/${catalogId.toLowerCase()}`,
    componentName: toPascalCase(catalogId),
  };
}

function getIconImport(iconName: string, context: TeamContextProfile): string | null {
  switch (context.iconLibrary.id) {
    case "lucide":
      return `import { ${iconName} } from "lucide-react";`;
    case "phosphor":
      return `import { ${iconName} } from "@phosphor-icons/react";`;
    case "heroicons":
      return `import { ${iconName} } from "@heroicons/react/24/outline";`;
    case "material-icons":
      return `import { ${iconName} } from "@mui/icons-material";`;
    case "tabler":
      return `import { ${iconName} } from "@tabler/icons-react";`;
    case "feather":
      return `import { ${iconName} } from "react-feather";`;
    default:
      return null;
  }
}

function inferHTMLTag(node: IRNode): string {
  switch (node.type) {
    case "text":
      if (node.fontSize && resolveNumberValue(node.fontSize) >= 24) return "h2";
      if (node.fontSize && resolveNumberValue(node.fontSize) >= 18) return "h3";
      return "span";
    case "frame":
      if (node.layoutMode === "HORIZONTAL" || node.layoutMode === "VERTICAL") return "div";
      if (node.eventHandlers?.some((h) => h.event === "click")) return "button";
      return "div";
    case "rectangle":
      return "div";
    default:
      return "div";
  }
}

function buildClassName(node: IRNode, context: TeamContextProfile): string {
  if (context.styling.approach === "tailwind") {
    const classes = buildTailwindClasses(node);
    if (classes.length === 0) return "";
    return ` className="${classes.join(" ")}"`;
  }

  if (context.styling.approach === "css-modules") {
    const name = toCamelCase(node.name);
    return ` className={styles.${name}}`;
  }

  return "";
}

function buildVueClassName(node: IRNode, context: TeamContextProfile): string {
  if (context.styling.approach === "tailwind") {
    const classes = buildTailwindClasses(node);
    if (classes.length === 0) return "";
    return ` class="${classes.join(" ")}"`;
  }

  return ` class="${toKebabCase(node.name)}"`;
}

function buildTailwindClasses(node: IRNode): string[] {
  const classes: string[] = [];

  // Layout
  if (node.layoutMode === "HORIZONTAL") classes.push("flex", "flex-row");
  if (node.layoutMode === "VERTICAL") classes.push("flex", "flex-col");

  // Alignment
  if (node.primaryAxisAlignment === "CENTER") classes.push("justify-center");
  if (node.primaryAxisAlignment === "MAX") classes.push("justify-end");
  if (node.primaryAxisAlignment === "SPACE_BETWEEN") classes.push("justify-between");
  if (node.counterAxisAlignment === "CENTER") classes.push("items-center");
  if (node.counterAxisAlignment === "MAX") classes.push("items-end");

  // Spacing
  if (node.itemSpacing && !isTokenRef(node.itemSpacing)) {
    classes.push(`gap-${spacingToTailwind(node.itemSpacing as number)}`);
  }

  // Padding
  if (node.spacingSlots) {
    const sp = node.spacingSlots;
    if (sp.paddingTop && !isTokenRef(sp.paddingTop)) classes.push(`pt-${spacingToTailwind(sp.paddingTop as number)}`);
    if (sp.paddingRight && !isTokenRef(sp.paddingRight)) classes.push(`pr-${spacingToTailwind(sp.paddingRight as number)}`);
    if (sp.paddingBottom && !isTokenRef(sp.paddingBottom)) classes.push(`pb-${spacingToTailwind(sp.paddingBottom as number)}`);
    if (sp.paddingLeft && !isTokenRef(sp.paddingLeft)) classes.push(`pl-${spacingToTailwind(sp.paddingLeft as number)}`);
  }

  // Corner radius
  if (node.cornerRadius && !isTokenRef(node.cornerRadius)) {
    const radius = node.cornerRadius as number;
    if (radius >= 9999) classes.push("rounded-full");
    else if (radius >= 12) classes.push("rounded-xl");
    else if (radius >= 8) classes.push("rounded-lg");
    else if (radius >= 6) classes.push("rounded-md");
    else if (radius >= 4) classes.push("rounded");
    else if (radius >= 2) classes.push("rounded-sm");
  }

  // Opacity
  if (node.opacity !== undefined && !isTokenRef(node.opacity) && (node.opacity as number) < 1) {
    const opacity = Math.round((node.opacity as number) * 100);
    classes.push(`opacity-${opacity}`);
  }

  // Text
  if (node.textAlign) {
    if (node.textAlign === "center") classes.push("text-center");
    if (node.textAlign === "right") classes.push("text-right");
    if (node.textAlign === "justify") classes.push("text-justify");
  }

  // Visibility
  if (!node.visible) classes.push("hidden");

  return classes;
}

function spacingToTailwind(px: number): string {
  // Tailwind spacing scale: 1 = 0.25rem = 4px
  const value = px / 4;
  if (Number.isInteger(value)) return String(value);
  return `[${px}px]`;
}

function resolveJSXValue(value: unknown): string {
  if (isTokenRef(value)) {
    return `"var(--${value.$ref.replace(/\./g, "-")})"`;
  }
  if (typeof value === "string") return `"${value}"`;
  return String(value);
}

function resolveNumberValue(value: unknown): number {
  if (isTokenRef(value)) return 16; // fallback
  return typeof value === "number" ? value : 16;
}

function buildReactProps(node: IRNode, _mapping: LibraryMapping): string {
  if (!node.componentRef?.propOverrides) return "";

  const props: string[] = [];
  for (const [key, value] of Object.entries(node.componentRef.propOverrides)) {
    if (typeof value === "string") {
      props.push(`${key}="${value}"`);
    } else if (typeof value === "boolean") {
      props.push(value ? key : `${key}={false}`);
    } else if (typeof value === "number") {
      props.push(`${key}={${value}}`);
    } else {
      props.push(`${key}={${JSON.stringify(value)}}`);
    }
  }

  return props.length > 0 ? ` ${props.join(" ")}` : "";
}

function buildEventAttributes(node: IRNode): string {
  if (!node.eventHandlers || node.eventHandlers.length === 0) return "";

  const attrs: string[] = [];
  for (const handler of node.eventHandlers) {
    const reactEvent = `on${handler.event.charAt(0).toUpperCase()}${handler.event.slice(1)}`;
    attrs.push(`${reactEvent}={() => handle${toPascalCase(handler.action)}("${handler.target}")}`);
  }

  return ` ${attrs.join(" ")}`;
}

function generateVuePropsInterface(componentName: string, propDefs: PropDef[]): string {
  const lines: string[] = [];
  lines.push(`interface ${componentName}Props {`);
  for (const prop of propDefs) {
    const optional = prop.required ? "" : "?";
    lines.push(`  ${prop.name}${optional}: ${prop.type};`);
  }
  lines.push("}");
  lines.push("");
  lines.push(`defineProps<${componentName}Props>();`);
  return lines.join("\n");
}

function generateStylesFile(
  _root: IRNode,
  _children: IRNode[],
  componentName: string,
  context: TeamContextProfile,
): GeneratedFile | null {
  if (context.styling.approach === "css-modules") {
    const fileName = formatFileName(componentName, context);
    return {
      path: `components/${fileName}.module.css`,
      content: `/* ${componentName} styles */\n.root {\n  /* Component root styles */\n}\n`,
      language: "css",
      category: "styling",
    };
  }

  if (context.styling.approach === "scss") {
    const fileName = formatFileName(componentName, context);
    return {
      path: `components/${fileName}.module.scss`,
      content: `// ${componentName} styles\n.root {\n  // Component root styles\n}\n`,
      language: "scss",
      category: "styling",
    };
  }

  return null;
}

function buildFilePath(
  fileName: string,
  componentName: string,
  context: TeamContextProfile,
): string {
  switch (context.codePatterns.componentFilePattern) {
    case "folder-with-index":
      return `components/${componentName}/index.tsx`;
    case "folder-with-named":
      return `components/${componentName}/${fileName}.tsx`;
    case "single-file":
    default:
      return `components/${fileName}.tsx`;
  }
}

// ─── String utilities ───────────────────────────────────────────────────────

function toComponentName(name: string): string {
  return toPascalCase(name.replace(/[^a-zA-Z0-9\s-_]/g, ""));
}

function toPascalCase(str: string): string {
  return str
    .replace(/[^a-zA-Z0-9]/g, " ")
    .split(" ")
    .filter(Boolean)
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join("");
}

function toCamelCase(str: string): string {
  const pascal = toPascalCase(str);
  return pascal.charAt(0).toLowerCase() + pascal.slice(1);
}

function toKebabCase(str: string): string {
  return str
    .replace(/[^a-zA-Z0-9]/g, "-")
    .replace(/([a-z])([A-Z])/g, "$1-$2")
    .replace(/-+/g, "-")
    .toLowerCase();
}

function formatFileName(componentName: string, context: TeamContextProfile): string {
  switch (context.codePatterns.fileNaming) {
    case "PascalCase":
      return componentName;
    case "kebab-case":
      return toKebabCase(componentName);
    case "camelCase":
    default:
      return toCamelCase(componentName);
  }
}
