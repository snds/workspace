// ─── Semantic Design IR — Token Resolver ─────────────────────────────────────
// Resolves `TokenRef` objects against a flat map of design token entries.
// Used by the compat layer and code generators to materialise concrete
// values from token references.
// ──────────────────────────────────────────────────────────────────────────────

import type { DesignToken } from "@/types/tokens";
import { isReference, extractRefPath } from "@/types/tokens";
import type {
  IRNode,
  IREffect,
  TokenOrLiteral,
  TokenRef,
  ColorSlots,
  SpacingSlots,
  TypographySlots,
  StateOverride,
  BreakpointRule,
} from "./types";
import { isTokenRef } from "./types";

// ─── TokenResolver ───────────────────────────────────────────────────────────

/**
 * Resolves `TokenRef` objects against a flat `Record<string, DesignToken>`
 * map (keyed by dot-path, e.g. `"color.brand.primary.500"`).
 *
 * The resolver follows one level of W3C DTCG `{dot.path}` alias chains so
 * that tokens referencing other tokens are resolved transitively (up to a
 * configurable depth to prevent infinite loops).
 */
export class TokenResolver {
  /** Maximum alias-chain depth before bailing out. */
  private readonly maxDepth: number;

  constructor(options?: { maxDepth?: number }) {
    this.maxDepth = options?.maxDepth ?? 10;
  }

  // ── Single-value resolution ───────────────────────────────────────────

  /**
   * Resolves a single `TokenOrLiteral<T>` value.
   *
   * - If the value is a raw literal, it is returned as-is.
   * - If the value is a `TokenRef`, the token is looked up in `entries` and
   *   its `$value` is returned. If the token's `$value` is itself a
   *   reference (alias), the resolver follows the chain up to `maxDepth`.
   *
   * @param value    The value to resolve.
   * @param entries  Flat map of design tokens keyed by dot-path.
   * @returns        The resolved literal value, or `undefined` if the token
   *                 could not be found.
   */
  resolve<T>(
    value: TokenOrLiteral<T>,
    entries: Record<string, DesignToken>,
  ): T | undefined {
    if (!isTokenRef(value)) {
      return value;
    }

    return this.resolveRef(value, entries, 0) as T | undefined;
  }

  /**
   * Internal: resolves a `TokenRef`, chasing alias chains.
   */
  private resolveRef(
    ref: TokenRef,
    entries: Record<string, DesignToken>,
    depth: number,
  ): unknown {
    if (depth >= this.maxDepth) {
      return undefined;
    }

    const token = entries[ref.$ref];
    if (!token) {
      return undefined;
    }

    // If the token's value is itself a reference, follow the chain.
    if (isReference(token.$value)) {
      const nextPath = extractRefPath(token.$value);
      return this.resolveRef({ $ref: nextPath }, entries, depth + 1);
    }

    return token.$value;
  }

  // ── Node-wide resolution ──────────────────────────────────────────────

  /**
   * Deep-resolves all `TokenRef` values in an `IRNode`, returning a new
   * node where every token-resolvable property holds a concrete literal.
   *
   * Properties whose tokens cannot be resolved are left as their original
   * `TokenRef` value (fail-open) so that downstream consumers can detect
   * and report unresolved references.
   *
   * @param node     The IR node to resolve.
   * @param entries  Flat map of design tokens keyed by dot-path.
   * @returns        A shallow-copied node with resolved values.
   */
  resolveAll(node: IRNode, entries: Record<string, DesignToken>): IRNode {
    const r = <T>(v: TokenOrLiteral<T> | undefined): TokenOrLiteral<T> | undefined => {
      if (v === undefined) return undefined;
      if (!isTokenRef(v)) return v;
      const resolved = this.resolve(v, entries);
      // If resolution failed, keep the original TokenRef for diagnostics.
      return resolved !== undefined ? (resolved as T) : v;
    };

    const resolved: IRNode = {
      // Identity (pass-through)
      id: node.id,
      type: node.type,
      name: node.name,
      parentId: node.parentId,
      pageId: node.pageId,
      order: node.order,

      // Transform (pass-through — not token-resolvable)
      x: node.x,
      y: node.y,
      width: node.width,
      height: node.height,
      rotation: node.rotation,

      // Appearance
      fill: r(node.fill) as TokenOrLiteral<string | null>,
      fillOpacity: r(node.fillOpacity) as TokenOrLiteral<number>,
      stroke: r(node.stroke) as TokenOrLiteral<string | null>,
      strokeWidth: r(node.strokeWidth) as TokenOrLiteral<number>,
      opacity: r(node.opacity) as TokenOrLiteral<number>,
      cornerRadius: r(node.cornerRadius) as TokenOrLiteral<number>,
      visible: node.visible,
      locked: node.locked,
      flipX: node.flipX,
      flipY: node.flipY,

      blendMode: node.blendMode,
      aspectRatioLocked: node.aspectRatioLocked,

      // Split corner radii
      cornerRadiusTopLeft: r(node.cornerRadiusTopLeft),
      cornerRadiusTopRight: r(node.cornerRadiusTopRight),
      cornerRadiusBottomRight: r(node.cornerRadiusBottomRight),
      cornerRadiusBottomLeft: r(node.cornerRadiusBottomLeft),
      cornerSmoothing: node.cornerSmoothing,

      // Stroke
      strokePosition: node.strokePosition,

      // Effects
      effects: node.effects?.map((e) => this.resolveEffect(e, entries)),

      // Auto layout
      layoutMode: node.layoutMode,
      primaryAxisSizing: node.primaryAxisSizing,
      counterAxisSizing: node.counterAxisSizing,
      paddingTop: r(node.paddingTop),
      paddingBottom: r(node.paddingBottom),
      paddingLeft: r(node.paddingLeft),
      paddingRight: r(node.paddingRight),
      itemSpacing: r(node.itemSpacing),
      counterAxisSpacing: r(node.counterAxisSpacing),
      primaryAxisAlignment: node.primaryAxisAlignment,
      counterAxisAlignment: node.counterAxisAlignment,
      wrapChildren: node.wrapChildren,
      gapMode: node.gapMode,
      strokesIncludedInLayout: node.strokesIncludedInLayout,
      childrenStackOrder: node.childrenStackOrder,
      alignTextBaseline: node.alignTextBaseline,

      // Text
      text: node.text,
      textColor: r(node.textColor),
      textSizing: node.textSizing,

      // Typography
      fontFamily: r(node.fontFamily),
      fontWeight: r(node.fontWeight),
      fontStyle: node.fontStyle,
      fontSize: r(node.fontSize),
      lineHeight: r(node.lineHeight),
      letterSpacing: r(node.letterSpacing),
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
      textDecorationColor: r(node.textDecorationColor),

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

      // Semantic slots
      colorSlots: node.colorSlots
        ? this.resolveColorSlots(node.colorSlots, entries)
        : undefined,
      spacingSlots: node.spacingSlots
        ? this.resolveSpacingSlots(node.spacingSlots, entries)
        : undefined,
      typographySlots: node.typographySlots
        ? this.resolveTypographySlots(node.typographySlots, entries)
        : undefined,

      // Component / Icon / Slot
      componentRef: node.componentRef,
      iconRef: node.iconRef
        ? {
            name: node.iconRef.name,
            size: r(node.iconRef.size),
            color: r(node.iconRef.color),
          }
        : undefined,
      slotDef: node.slotDef,

      // Behavioral annotations (pass-through)
      dataBindings: node.dataBindings,
      featureGate: node.featureGate,
      i18nKeys: node.i18nKeys,
      eventHandlers: node.eventHandlers,

      // State & responsive overrides
      stateOverrides: node.stateOverrides?.map((so) =>
        this.resolveStateOverride(so, entries),
      ),
      breakpointRules: node.breakpointRules?.map((br) =>
        this.resolveBreakpointRule(br, entries),
      ),
    };

    return resolved;
  }

  // ── Slot resolution helpers ───────────────────────────────────────────

  private resolveColorSlots(
    slots: ColorSlots,
    entries: Record<string, DesignToken>,
  ): ColorSlots {
    const r = <T>(v: TokenOrLiteral<T> | undefined) =>
      v !== undefined ? (this.resolve(v, entries) as T | undefined) ?? v : undefined;
    return {
      background: r(slots.background),
      foreground: r(slots.foreground),
      border: r(slots.border),
      accent: r(slots.accent),
    };
  }

  private resolveSpacingSlots(
    slots: SpacingSlots,
    entries: Record<string, DesignToken>,
  ): SpacingSlots {
    const r = <T>(v: TokenOrLiteral<T> | undefined) =>
      v !== undefined ? (this.resolve(v, entries) as T | undefined) ?? v : undefined;
    return {
      paddingTop: r(slots.paddingTop),
      paddingRight: r(slots.paddingRight),
      paddingBottom: r(slots.paddingBottom),
      paddingLeft: r(slots.paddingLeft),
      marginTop: r(slots.marginTop),
      marginRight: r(slots.marginRight),
      marginBottom: r(slots.marginBottom),
      marginLeft: r(slots.marginLeft),
      gap: r(slots.gap),
    };
  }

  private resolveTypographySlots(
    slots: TypographySlots,
    entries: Record<string, DesignToken>,
  ): TypographySlots {
    const r = <T>(v: TokenOrLiteral<T> | undefined) =>
      v !== undefined ? (this.resolve(v, entries) as T | undefined) ?? v : undefined;
    return {
      fontFamily: r(slots.fontFamily),
      fontSize: r(slots.fontSize),
      fontWeight: r(slots.fontWeight),
      lineHeight: r(slots.lineHeight),
      letterSpacing: r(slots.letterSpacing),
    };
  }

  // ── Effect resolution ─────────────────────────────────────────────────

  private resolveEffect(
    effect: IREffect,
    entries: Record<string, DesignToken>,
  ): IREffect {
    const r = <T>(v: TokenOrLiteral<T> | undefined) =>
      v !== undefined ? (this.resolve(v, entries) as T | undefined) ?? v : undefined;
    return {
      type: effect.type,
      visible: effect.visible,
      color: r(effect.color),
      offsetX: r(effect.offsetX),
      offsetY: r(effect.offsetY),
      blur: r(effect.blur),
      spread: r(effect.spread),
      radius: r(effect.radius),
    };
  }

  // ── Override resolution ───────────────────────────────────────────────

  private resolveStateOverride(
    so: StateOverride,
    entries: Record<string, DesignToken>,
  ): StateOverride {
    // Resolve token refs within the override's visual properties.
    // We create a minimal IRNode-like object from the overrides, resolve it,
    // and extract back. For simplicity we resolve known token-resolvable
    // fields individually.
    const o = so.overrides;
    const r = <T>(v: TokenOrLiteral<T> | undefined) =>
      v !== undefined ? (this.resolve(v, entries) as T | undefined) ?? v : undefined;

    return {
      state: so.state,
      overrides: {
        ...(o.fill !== undefined && { fill: r(o.fill) }),
        ...(o.fillOpacity !== undefined && { fillOpacity: r(o.fillOpacity) }),
        ...(o.stroke !== undefined && { stroke: r(o.stroke) }),
        ...(o.strokeWidth !== undefined && { strokeWidth: r(o.strokeWidth) }),
        ...(o.opacity !== undefined && { opacity: r(o.opacity) }),
        ...(o.cornerRadius !== undefined && {
          cornerRadius: r(o.cornerRadius),
        }),
        ...(o.blendMode !== undefined && { blendMode: o.blendMode }),
        ...(o.textColor !== undefined && { textColor: r(o.textColor) }),
        ...(o.fontSize !== undefined && { fontSize: r(o.fontSize) }),
        ...(o.fontWeight !== undefined && { fontWeight: r(o.fontWeight) }),
        ...(o.letterSpacing !== undefined && {
          letterSpacing: r(o.letterSpacing),
        }),
        ...(o.colorSlots !== undefined && {
          colorSlots: this.resolveColorSlots(o.colorSlots, entries),
        }),
        ...(o.effects !== undefined && {
          effects: o.effects.map((e) => this.resolveEffect(e, entries)),
        }),
      },
    };
  }

  private resolveBreakpointRule(
    br: BreakpointRule,
    entries: Record<string, DesignToken>,
  ): BreakpointRule {
    const o = br.overrides;
    const r = <T>(v: TokenOrLiteral<T> | undefined) =>
      v !== undefined ? (this.resolve(v, entries) as T | undefined) ?? v : undefined;

    return {
      breakpoint: br.breakpoint,
      overrides: {
        // Transform
        ...(o.x !== undefined && { x: o.x }),
        ...(o.y !== undefined && { y: o.y }),
        ...(o.width !== undefined && { width: o.width }),
        ...(o.height !== undefined && { height: o.height }),
        // Appearance
        ...(o.fill !== undefined && { fill: r(o.fill) }),
        ...(o.fillOpacity !== undefined && { fillOpacity: r(o.fillOpacity) }),
        ...(o.stroke !== undefined && { stroke: r(o.stroke) }),
        ...(o.strokeWidth !== undefined && { strokeWidth: r(o.strokeWidth) }),
        ...(o.opacity !== undefined && { opacity: r(o.opacity) }),
        ...(o.cornerRadius !== undefined && {
          cornerRadius: r(o.cornerRadius),
        }),
        // Typography
        ...(o.fontSize !== undefined && { fontSize: r(o.fontSize) }),
        ...(o.fontWeight !== undefined && { fontWeight: r(o.fontWeight) }),
        ...(o.lineHeight !== undefined && { lineHeight: r(o.lineHeight) }),
        ...(o.letterSpacing !== undefined && {
          letterSpacing: r(o.letterSpacing),
        }),
        // Layout
        ...(o.layoutMode !== undefined && { layoutMode: o.layoutMode }),
        ...(o.primaryAxisSizing !== undefined && {
          primaryAxisSizing: o.primaryAxisSizing,
        }),
        ...(o.counterAxisSizing !== undefined && {
          counterAxisSizing: o.counterAxisSizing,
        }),
        ...(o.paddingTop !== undefined && { paddingTop: r(o.paddingTop) }),
        ...(o.paddingBottom !== undefined && {
          paddingBottom: r(o.paddingBottom),
        }),
        ...(o.paddingLeft !== undefined && { paddingLeft: r(o.paddingLeft) }),
        ...(o.paddingRight !== undefined && { paddingRight: r(o.paddingRight) }),
        ...(o.itemSpacing !== undefined && { itemSpacing: r(o.itemSpacing) }),
        ...(o.counterAxisSpacing !== undefined && {
          counterAxisSpacing: r(o.counterAxisSpacing),
        }),
        ...(o.primaryAxisAlignment !== undefined && {
          primaryAxisAlignment: o.primaryAxisAlignment,
        }),
        ...(o.counterAxisAlignment !== undefined && {
          counterAxisAlignment: o.counterAxisAlignment,
        }),
        ...(o.visible !== undefined && { visible: o.visible }),
        // Semantic slots
        ...(o.colorSlots !== undefined && {
          colorSlots: this.resolveColorSlots(o.colorSlots, entries),
        }),
        ...(o.spacingSlots !== undefined && {
          spacingSlots: this.resolveSpacingSlots(o.spacingSlots, entries),
        }),
        ...(o.typographySlots !== undefined && {
          typographySlots: this.resolveTypographySlots(
            o.typographySlots,
            entries,
          ),
        }),
      },
    };
  }
}
