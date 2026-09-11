// ─── Semantic Design IR — Compatibility Layer ────────────────────────────────
// Bidirectional bridge between the flat CanvasNode (used by the canvas
// renderer) and the semantic IRNode (used by code generators & the
// design-token pipeline).
//
// canvasNodeToIR:  CanvasNode → IRNode   (wraps literals, zero data loss)
// irNodeToCanvasNode: IRNode → CanvasNode (resolves TokenRefs to literals)
// ──────────────────────────────────────────────────────────────────────────────

import type { CanvasNode, Effect } from "@/types/canvas";
import type {
  IRNode,
  IREffect,
  TokenOrLiteral,
  TokenRef,
} from "./types";
import { isTokenRef } from "./types";

// ─── Resolver callback type ──────────────────────────────────────────────────

/**
 * A function that resolves a `TokenRef` to a concrete value.
 * The compat layer is resolver-agnostic; callers supply their own lookup.
 *
 * @param ref  The token reference to resolve.
 * @returns    The resolved literal value, or `undefined` if unresolvable.
 */
export type ResolverFn = (ref: TokenRef) => unknown;

// ─── Helpers ─────────────────────────────────────────────────────────────────

/**
 * Resolves a `TokenOrLiteral<T>` to its literal value. If the value is a
 * `TokenRef` the resolver callback is invoked; if the resolver returns
 * `undefined` the provided `fallback` is used instead.
 */
function resolveTOL<T>(
  value: TokenOrLiteral<T> | undefined,
  resolve: ResolverFn,
  fallback: T,
): T {
  if (value === undefined) return fallback;
  if (isTokenRef(value)) {
    const resolved = resolve(value);
    return (resolved !== undefined ? resolved : fallback) as T;
  }
  return value;
}

/** Converts a canvas `Effect` to an `IREffect` (wraps literals). */
function effectToIR(effect: Effect): IREffect {
  return {
    type: effect.type,
    visible: effect.visible,
    color: effect.color,
    offsetX: effect.offsetX,
    offsetY: effect.offsetY,
    blur: effect.blur,
    spread: effect.spread,
    radius: effect.radius,
  };
}

/** Converts an `IREffect` back to a canvas `Effect` (resolves tokens). */
function irEffectToCanvas(effect: IREffect, resolve: ResolverFn): Effect {
  return {
    type: effect.type,
    visible: effect.visible,
    color: resolveTOL(effect.color, resolve, undefined) as string | undefined,
    offsetX: resolveTOL(effect.offsetX, resolve, undefined) as
      | number
      | undefined,
    offsetY: resolveTOL(effect.offsetY, resolve, undefined) as
      | number
      | undefined,
    blur: resolveTOL(effect.blur, resolve, undefined) as number | undefined,
    spread: resolveTOL(effect.spread, resolve, undefined) as number | undefined,
    radius: resolveTOL(effect.radius, resolve, undefined) as number | undefined,
  };
}

// ─── CanvasNode → IRNode ─────────────────────────────────────────────────────

/**
 * Converts a `CanvasNode` into an `IRNode`.
 *
 * All visual values are kept as raw literals (no token refs are introduced).
 * The resulting IR node is fully compatible with the canvas renderer while
 * also being a valid input to code generators.
 *
 * Semantic slots (`colorSlots`, `spacingSlots`, `typographySlots`) and
 * behavioral annotations (`dataBindings`, `eventHandlers`, etc.) are left
 * `undefined` — they are populated later by the design-intelligence layer.
 */
export function canvasNodeToIR(node: CanvasNode): IRNode {
  return {
    // Identity
    id: node.id,
    type: node.type, // NodeType is a subset of IRNodeType
    name: node.name,
    parentId: node.parentId,
    pageId: node.pageId,
    order: node.order,

    // Transform
    x: node.x,
    y: node.y,
    width: node.width,
    height: node.height,
    rotation: node.rotation,

    // Appearance
    fill: node.fill,
    fillOpacity: node.fillOpacity,
    stroke: node.stroke,
    strokeWidth: node.strokeWidth,
    opacity: node.opacity,
    cornerRadius: node.cornerRadius,
    visible: node.visible,
    locked: node.locked,
    flipX: node.flipX,
    flipY: node.flipY,

    blendMode: node.blendMode,
    aspectRatioLocked: node.aspectRatioLocked,

    // Split corner radii
    cornerRadiusTopLeft: node.cornerRadiusTopLeft,
    cornerRadiusTopRight: node.cornerRadiusTopRight,
    cornerRadiusBottomRight: node.cornerRadiusBottomRight,
    cornerRadiusBottomLeft: node.cornerRadiusBottomLeft,
    cornerSmoothing: node.cornerSmoothing,

    // Stroke
    strokePosition: node.strokePosition,

    // Effects
    effects: node.effects?.map(effectToIR),

    // Auto layout
    layoutMode: node.layoutMode,
    primaryAxisSizing: node.primaryAxisSizing,
    counterAxisSizing: node.counterAxisSizing,
    paddingTop: node.paddingTop,
    paddingBottom: node.paddingBottom,
    paddingLeft: node.paddingLeft,
    paddingRight: node.paddingRight,
    itemSpacing: node.itemSpacing,
    counterAxisSpacing: node.counterAxisSpacing,
    primaryAxisAlignment: node.primaryAxisAlignment,
    counterAxisAlignment: node.counterAxisAlignment,
    wrapChildren: node.wrapChildren,
    gapMode: node.gapMode,
    strokesIncludedInLayout: node.strokesIncludedInLayout,
    childrenStackOrder: node.childrenStackOrder,
    alignTextBaseline: node.alignTextBaseline,

    // Text
    text: node.text,
    textColor: node.textColor,
    textSizing: node.textSizing,

    // Typography
    fontFamily: node.fontFamily,
    fontWeight: node.fontWeight,
    fontStyle: node.fontStyle,
    fontSize: node.fontSize,
    lineHeight: node.lineHeight,
    letterSpacing: node.letterSpacing,
    textAlign: node.textAlign,
    verticalAlign: node.verticalAlign,
    textDecoration: node.textDecoration,
    textTransform: node.textTransform,
    paragraphSpacing: node.paragraphSpacing,

    // OpenType features
    ligatures: node.ligatures,
    contextualAlternates: node.contextualAlternates,
    ordinals: node.ordinals,
    fractions: node.fractions,
    caseSensitiveForms: node.caseSensitiveForms,
    smallCaps: node.smallCaps,
    numberPosition: node.numberPosition,
    stylisticSets: node.stylisticSets,

    // Text decoration detail
    textDecorationStyle: node.textDecorationStyle,
    textDecorationThickness: node.textDecorationThickness,
    textDecorationOffset: node.textDecorationOffset,
    textDecorationSkipInk: node.textDecorationSkipInk,
    textDecorationColor: node.textDecorationColor,

    // Paragraph / layout
    paragraphIndent: node.paragraphIndent,
    hangingPunctuation: node.hangingPunctuation,
    hangingLists: node.hangingLists,
    listStyle: node.listStyle,
    truncateText: node.truncateText,
    verticalTrim: node.verticalTrim,

    // Frame
    clipContent: node.clipContent,

    // Dev handoff
    readyForDev: node.readyForDev,
  };
}

// ─── IRNode → CanvasNode ─────────────────────────────────────────────────────

/**
 * Converts an `IRNode` back into a `CanvasNode`.
 *
 * Any `TokenRef` values are resolved to literals via the supplied `resolve`
 * callback. IR-only properties (semantic slots, data bindings, event
 * handlers, etc.) are discarded because `CanvasNode` has no place for them.
 *
 * If the IR node's `type` is an IR-only variant (`component-instance`,
 * `icon`, `slot`), it is mapped to `"frame"` since the canvas renderer
 * doesn't understand those types.
 *
 * @param node     The IR node to convert.
 * @param resolve  Callback to resolve `TokenRef` values.
 */
export function irNodeToCanvasNode(
  node: IRNode,
  resolve: ResolverFn,
): CanvasNode {
  // Map IR-only node types to a canvas-compatible fallback.
  const canvasType =
    node.type === "component-instance" ||
    node.type === "icon" ||
    node.type === "slot"
      ? "frame"
      : node.type;

  return {
    // Identity
    id: node.id,
    type: canvasType,
    name: node.name,
    parentId: node.parentId,
    pageId: node.pageId,
    order: node.order,

    // Transform
    x: node.x,
    y: node.y,
    width: node.width,
    height: node.height,
    rotation: node.rotation,

    // Appearance
    fill: resolveTOL(node.fill, resolve, null),
    fillOpacity: resolveTOL(node.fillOpacity, resolve, 1),
    stroke: resolveTOL(node.stroke, resolve, null),
    strokeWidth: resolveTOL(node.strokeWidth, resolve, 0),
    opacity: resolveTOL(node.opacity, resolve, 1),
    cornerRadius: resolveTOL(node.cornerRadius, resolve, 0),
    visible: node.visible,
    locked: node.locked,
    flipX: node.flipX,
    flipY: node.flipY,

    blendMode: node.blendMode,
    aspectRatioLocked: node.aspectRatioLocked,

    // Split corner radii
    cornerRadiusTopLeft: resolveTOL(
      node.cornerRadiusTopLeft,
      resolve,
      undefined,
    ) as number | undefined,
    cornerRadiusTopRight: resolveTOL(
      node.cornerRadiusTopRight,
      resolve,
      undefined,
    ) as number | undefined,
    cornerRadiusBottomRight: resolveTOL(
      node.cornerRadiusBottomRight,
      resolve,
      undefined,
    ) as number | undefined,
    cornerRadiusBottomLeft: resolveTOL(
      node.cornerRadiusBottomLeft,
      resolve,
      undefined,
    ) as number | undefined,
    cornerSmoothing: node.cornerSmoothing,

    // Stroke
    strokePosition: node.strokePosition,

    // Effects
    effects: node.effects?.map((e) => irEffectToCanvas(e, resolve)),

    // Auto layout
    layoutMode: node.layoutMode,
    primaryAxisSizing: node.primaryAxisSizing,
    counterAxisSizing: node.counterAxisSizing,
    paddingTop: resolveTOL(node.paddingTop, resolve, undefined) as
      | number
      | undefined,
    paddingBottom: resolveTOL(node.paddingBottom, resolve, undefined) as
      | number
      | undefined,
    paddingLeft: resolveTOL(node.paddingLeft, resolve, undefined) as
      | number
      | undefined,
    paddingRight: resolveTOL(node.paddingRight, resolve, undefined) as
      | number
      | undefined,
    itemSpacing: resolveTOL(node.itemSpacing, resolve, undefined) as
      | number
      | undefined,
    counterAxisSpacing: resolveTOL(
      node.counterAxisSpacing,
      resolve,
      undefined,
    ) as number | undefined,
    primaryAxisAlignment: node.primaryAxisAlignment,
    counterAxisAlignment: node.counterAxisAlignment,
    wrapChildren: node.wrapChildren,
    gapMode: node.gapMode,
    strokesIncludedInLayout: node.strokesIncludedInLayout,
    childrenStackOrder: node.childrenStackOrder,
    alignTextBaseline: node.alignTextBaseline,

    // Text
    text: node.text,
    textColor: resolveTOL(node.textColor, resolve, undefined) as
      | string
      | undefined,
    textSizing: node.textSizing,

    // Typography
    fontFamily: resolveTOL(node.fontFamily, resolve, undefined) as
      | string
      | undefined,
    fontWeight: resolveTOL(node.fontWeight, resolve, undefined) as
      | number
      | undefined,
    fontStyle: node.fontStyle,
    fontSize: resolveTOL(node.fontSize, resolve, undefined) as
      | number
      | undefined,
    lineHeight: resolveTOL(node.lineHeight, resolve, undefined) as
      | number
      | undefined,
    letterSpacing: resolveTOL(node.letterSpacing, resolve, undefined) as
      | number
      | undefined,
    textAlign: node.textAlign,
    verticalAlign: node.verticalAlign,
    textDecoration: node.textDecoration,
    textTransform: node.textTransform,
    paragraphSpacing: node.paragraphSpacing,

    // OpenType features
    ligatures: node.ligatures,
    contextualAlternates: node.contextualAlternates,
    ordinals: node.ordinals,
    fractions: node.fractions,
    caseSensitiveForms: node.caseSensitiveForms,
    smallCaps: node.smallCaps,
    numberPosition: node.numberPosition,
    stylisticSets: node.stylisticSets,

    // Text decoration detail
    textDecorationStyle: node.textDecorationStyle,
    textDecorationThickness: node.textDecorationThickness,
    textDecorationOffset: node.textDecorationOffset,
    textDecorationSkipInk: node.textDecorationSkipInk,
    textDecorationColor: resolveTOL(
      node.textDecorationColor,
      resolve,
      undefined,
    ) as string | undefined,

    // Paragraph / layout
    paragraphIndent: node.paragraphIndent,
    hangingPunctuation: node.hangingPunctuation,
    hangingLists: node.hangingLists,
    listStyle: node.listStyle,
    truncateText: node.truncateText,
    verticalTrim: node.verticalTrim,

    // Frame
    clipContent: node.clipContent,

    // Dev handoff
    readyForDev: node.readyForDev,
  };
}
