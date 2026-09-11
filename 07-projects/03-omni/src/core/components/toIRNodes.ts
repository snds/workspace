// ─── Blueprint to IR Node Conversion ─────────────────────────────────────────
// Converts a ComponentBlueprint + optional variant/prop overrides into
// canvas-compatible NodeSpec trees. Maintains backwards compatibility with the
// existing componentBlueprints.ts NodeSpec interface.

import type { ComponentBlueprint, CanvasTemplate, CanvasTemplateChild } from "./types";

/** Canvas-compatible node specification (matches legacy NodeSpec shape) */
export interface NodeSpec {
  type: "frame" | "rectangle" | "text";
  name: string;
  rx: number;
  ry: number;
  width: number;
  height: number;
  fill?: string | null;
  stroke?: string | null;
  strokeWidth?: number;
  cornerRadius?: number;
  opacity?: number;
  text?: string;
  textColor?: string;
  fontSize?: number;
  fontWeight?: number;
  textAlign?: "left" | "center" | "right";
  verticalAlign?: "top" | "middle" | "bottom";
  lineHeight?: number;
  children?: NodeSpec[];
}

/**
 * Convert a ComponentBlueprint into a canvas-ready NodeSpec tree.
 *
 * @param blueprint  The component blueprint to convert
 * @param variant    Optional variant id to apply overrides from
 * @param propOverrides  Optional prop values that override defaults
 */
export function blueprintToNodeSpec(
  blueprint: ComponentBlueprint,
  variant?: string,
  propOverrides?: Record<string, unknown>,
): NodeSpec {
  // Start with the base canvas template
  let template = blueprint.canvasTemplate;

  // Apply variant overrides if specified
  if (variant) {
    const v = blueprint.variants?.find((vr) => vr.id === variant);
    if (v?.canvasOverrides) {
      template = { ...template, ...v.canvasOverrides };
    }
  }

  // Apply prop overrides that affect canvas rendering
  const mergedProps = mergeProps(blueprint, propOverrides);

  return templateToNodeSpec(template, blueprint.name, 0, 0, mergedProps);
}

// ─── Internal helpers ────────────────────────────────────────────────────────

function mergeProps(
  blueprint: ComponentBlueprint,
  overrides?: Record<string, unknown>,
): Record<string, unknown> {
  const result: Record<string, unknown> = {};

  // Collect defaults
  for (const prop of blueprint.props) {
    if (prop.defaultValue !== undefined) {
      result[prop.name] = prop.defaultValue;
    }
  }

  // Apply overrides
  if (overrides) {
    for (const [key, value] of Object.entries(overrides)) {
      result[key] = value;
    }
  }

  return result;
}

function templateToNodeSpec(
  template: CanvasTemplate | CanvasTemplateChild,
  name: string,
  rx: number,
  ry: number,
  props: Record<string, unknown>,
): NodeSpec {
  const spec: NodeSpec = {
    type: template.type,
    name,
    rx,
    ry,
    width: template.width,
    height: template.height,
  };

  if (template.fill !== undefined) spec.fill = template.fill;
  if (template.cornerRadius !== undefined) spec.cornerRadius = template.cornerRadius;
  if (template.stroke !== undefined) spec.stroke = template.stroke;
  if (template.strokeWidth !== undefined) spec.strokeWidth = template.strokeWidth;
  if (template.opacity !== undefined) spec.opacity = template.opacity;

  // Apply text properties from CanvasTemplateChild
  if ("text" in template && template.text !== undefined) {
    const child = template as CanvasTemplateChild;
    // Allow prop override for text content (use the "label" prop if present)
    if (props.label !== undefined && name === "Label") {
      spec.text = String(props.label);
    } else {
      spec.text = child.text;
    }
    if (child.textColor !== undefined) spec.textColor = child.textColor;
    if (child.fontSize !== undefined) spec.fontSize = child.fontSize;
    if (child.fontWeight !== undefined) spec.fontWeight = child.fontWeight;
    if (child.textAlign !== undefined) spec.textAlign = child.textAlign;
    if (child.verticalAlign !== undefined) spec.verticalAlign = child.verticalAlign;
  }

  // Convert children
  if (template.children && template.children.length > 0) {
    spec.children = template.children.map((child) =>
      templateToNodeSpec(child, child.name, child.offsetX, child.offsetY, props),
    );
  }

  return spec;
}
