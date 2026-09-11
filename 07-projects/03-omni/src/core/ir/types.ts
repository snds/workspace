// ─── Semantic Design IR — Type System ─────────────────────────────────────────
// Framework-agnostic intermediate representation for design nodes.
// "Design Once, Output Anywhere."
//
// Every visual property accepts either a raw literal OR a token reference,
// enabling theme-aware code generation and round-trip fidelity with the
// design-token layer.
// ──────────────────────────────────────────────────────────────────────────────

import type { NodeType, EffectType } from "@/types/canvas";

// ─── Token reference primitives ──────────────────────────────────────────────

/**
 * A pointer into the design-token tree using W3C DTCG `{dot.path}` syntax.
 *
 * @example
 * ```ts
 * const ref: TokenRef = { $ref: "color.brand.primary.500" };
 * ```
 */
export interface TokenRef {
  $ref: string;
}

/**
 * A value that is either a raw literal of type `T` or a token reference.
 * This is the fundamental building block of the IR: every visual property
 * uses this type so that code generators can emit token references instead
 * of hard-coded values.
 */
export type TokenOrLiteral<T> = T | TokenRef;

/** Type guard: returns `true` when a value is a `TokenRef`. */
export function isTokenRef(v: unknown): v is TokenRef {
  return (
    typeof v === "object" &&
    v !== null &&
    "$ref" in v &&
    typeof (v as TokenRef).$ref === "string"
  );
}

// ─── Extended node type ──────────────────────────────────────────────────────

/**
 * Extends the canvas `NodeType` with semantic node kinds that only exist in
 * the IR layer.
 *
 * - `component-instance` — a usage of a catalogued component with optional
 *   variant and prop overrides.
 * - `icon` — a reference to a named icon from an icon set.
 * - `slot` — a named placeholder that consumers of a component can fill.
 */
export type IRNodeType = NodeType | "component-instance" | "icon" | "slot";

// ─── Semantic slot groupings ─────────────────────────────────────────────────

/** Semantic color roles for a node. Each slot is token-resolvable. */
export interface ColorSlots {
  background?: TokenOrLiteral<string>;
  foreground?: TokenOrLiteral<string>;
  border?: TokenOrLiteral<string>;
  accent?: TokenOrLiteral<string>;
}

/** Semantic spacing roles for a node. Each slot is token-resolvable. */
export interface SpacingSlots {
  paddingTop?: TokenOrLiteral<number>;
  paddingRight?: TokenOrLiteral<number>;
  paddingBottom?: TokenOrLiteral<number>;
  paddingLeft?: TokenOrLiteral<number>;
  marginTop?: TokenOrLiteral<number>;
  marginRight?: TokenOrLiteral<number>;
  marginBottom?: TokenOrLiteral<number>;
  marginLeft?: TokenOrLiteral<number>;
  gap?: TokenOrLiteral<number>;
}

/** Semantic typography roles for a node. Each slot is token-resolvable. */
export interface TypographySlots {
  fontFamily?: TokenOrLiteral<string>;
  fontSize?: TokenOrLiteral<number>;
  fontWeight?: TokenOrLiteral<number>;
  lineHeight?: TokenOrLiteral<number>;
  letterSpacing?: TokenOrLiteral<number>;
}

// ─── Effects ─────────────────────────────────────────────────────────────────

/**
 * An effect (shadow, blur) whose visual values are token-resolvable.
 * Mirror of the canvas `Effect` but with `TokenOrLiteral` wrappers.
 */
export interface IREffect {
  type: EffectType;
  visible: boolean;
  color?: TokenOrLiteral<string>;
  offsetX?: TokenOrLiteral<number>;
  offsetY?: TokenOrLiteral<number>;
  blur?: TokenOrLiteral<number>;
  spread?: TokenOrLiteral<number>;
  radius?: TokenOrLiteral<number>;
}

// ─── Behavioral annotations ──────────────────────────────────────────────────

/**
 * Binds a node property to a runtime data source. Code generators use this
 * to emit reactive bindings (e.g. React props, Vue bindings, SwiftUI state).
 */
export interface DataBinding {
  /** The IR node property this binding targets (e.g. `"text"`, `"fill"`). */
  propName: string;
  /** Identifier of the data source (API, store, context, etc.). */
  sourceId: string;
  /** Dot-path into the data source (e.g. `"user.profile.name"`). */
  fieldPath: string;
  /** Optional transform expression applied before assignment. */
  transform?: string;
}

/**
 * Conditionally shows/hides a node (or switches its variant) based on a
 * feature flag.
 */
export interface FeatureFlagGate {
  /** The flag key in the feature-flag system. */
  flagKey: string;
  /** The flag values that cause this node to render. */
  values: string[];
  /** What to do when the flag is not in `values`. */
  fallback?: "hide" | "default-variant";
}

/**
 * An event handler attached to a node. Code generators translate these into
 * platform-specific event wiring.
 */
export interface EventHandler {
  /** DOM/platform event name (e.g. `"click"`, `"submit"`, `"change"`). */
  event: string;
  /** High-level action type. */
  action: "navigate" | "submit" | "mutate" | "toggle" | "custom";
  /** Action target — a route path, mutation key, toggle ID, or custom ref. */
  target: string;
  /** Optional payload passed to the action. */
  payload?: Record<string, unknown>;
}

// ─── State & responsive overrides ────────────────────────────────────────────

/** Interactive states that can carry visual overrides. */
export type InteractionState =
  | "hover"
  | "focus"
  | "active"
  | "disabled"
  | "checked"
  | "error";

/**
 * Visual properties that can be overridden per interaction state.
 * Intentionally limited to appearance-related fields.
 */
export type VisualOverrideProps =
  | "fill"
  | "fillOpacity"
  | "stroke"
  | "strokeWidth"
  | "opacity"
  | "cornerRadius"
  | "blendMode"
  | "textColor"
  | "fontSize"
  | "fontWeight"
  | "letterSpacing"
  | "colorSlots"
  | "effects";

/** Overrides applied when the node enters a given interaction state. */
export interface StateOverride {
  state: InteractionState;
  overrides: Partial<Pick<IRNode, VisualOverrideProps>>;
}

/**
 * Layout/visual properties that can be overridden per breakpoint.
 */
export type BreakpointOverrideProps =
  | "x"
  | "y"
  | "width"
  | "height"
  | "fill"
  | "fillOpacity"
  | "stroke"
  | "strokeWidth"
  | "opacity"
  | "cornerRadius"
  | "fontSize"
  | "fontWeight"
  | "lineHeight"
  | "letterSpacing"
  | "layoutMode"
  | "primaryAxisSizing"
  | "counterAxisSizing"
  | "paddingTop"
  | "paddingBottom"
  | "paddingLeft"
  | "paddingRight"
  | "itemSpacing"
  | "counterAxisSpacing"
  | "primaryAxisAlignment"
  | "counterAxisAlignment"
  | "visible"
  | "colorSlots"
  | "spacingSlots"
  | "typographySlots";

/** Responsive style overrides keyed by a named breakpoint. */
export interface BreakpointRule {
  /** Named breakpoint (e.g. `"sm"`, `"md"`, `"lg"`, `"xl"`). */
  breakpoint: string;
  overrides: Partial<Pick<IRNode, BreakpointOverrideProps>>;
}

// ─── Component / Icon / Slot references ──────────────────────────────────────

/** Reference to a catalogued component (for `component-instance` nodes). */
export interface ComponentRef {
  /** ID of the component in the design system catalogue. */
  catalogId: string;
  /** Named variant of the component. */
  variant?: string;
  /** Arbitrary prop overrides forwarded to the component. */
  propOverrides?: Record<string, unknown>;
}

/** Reference to a named icon (for `icon` nodes). */
export interface IconRef {
  /** Icon name (e.g. `"chevron-right"`, `"search"`). */
  name: string;
  /** Icon size — token-resolvable. */
  size?: TokenOrLiteral<number>;
  /** Icon color — token-resolvable. */
  color?: TokenOrLiteral<string>;
}

/** Slot definition for component authoring (for `slot` nodes). */
export interface SlotDef {
  /** Slot name exposed to consumers. */
  name: string;
  /** IDs of fallback child nodes rendered when the slot is empty. */
  fallbackChildren?: string[];
}

// ─── IRNode — the semantic design node ───────────────────────────────────────

/**
 * The Semantic Design IR node.
 *
 * Retains the full canvas property set (for rendering in the editor) while
 * layering semantic metadata on top: token references, color/spacing/typography
 * slots, component instances, data bindings, interaction states, responsive
 * rules, and more.
 *
 * Code generators consume `IRNode` trees and emit framework-specific output
 * (React, SwiftUI, Compose, HTML/CSS, Flutter, etc.).
 */
export interface IRNode {
  // ── Identity ────────────────────────────────────────────────────────────
  id: string;
  type: IRNodeType;
  name: string;
  parentId: string | null;
  pageId: string;
  order: number;

  // ── Transform ───────────────────────────────────────────────────────────
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;

  // ── Appearance (token-resolvable) ───────────────────────────────────────
  fill: TokenOrLiteral<string | null>;
  fillOpacity: TokenOrLiteral<number>;
  stroke: TokenOrLiteral<string | null>;
  strokeWidth: TokenOrLiteral<number>;
  opacity: TokenOrLiteral<number>;
  cornerRadius: TokenOrLiteral<number>;
  visible: boolean;
  locked: boolean;
  flipX?: boolean;
  flipY?: boolean;

  blendMode?: string;
  aspectRatioLocked?: boolean;

  // Split corner radii
  cornerRadiusTopLeft?: TokenOrLiteral<number>;
  cornerRadiusTopRight?: TokenOrLiteral<number>;
  cornerRadiusBottomRight?: TokenOrLiteral<number>;
  cornerRadiusBottomLeft?: TokenOrLiteral<number>;
  cornerSmoothing?: number;

  // Stroke
  strokePosition?: "inside" | "center" | "outside";

  // Effects
  effects?: IREffect[];

  // ── Auto layout ─────────────────────────────────────────────────────────
  layoutMode?: "NONE" | "HORIZONTAL" | "VERTICAL" | "GRID";
  primaryAxisSizing?: "FIXED" | "HUG" | "FILL";
  counterAxisSizing?: "FIXED" | "HUG" | "FILL";
  paddingTop?: TokenOrLiteral<number>;
  paddingBottom?: TokenOrLiteral<number>;
  paddingLeft?: TokenOrLiteral<number>;
  paddingRight?: TokenOrLiteral<number>;
  itemSpacing?: TokenOrLiteral<number>;
  counterAxisSpacing?: TokenOrLiteral<number>;
  primaryAxisAlignment?: "MIN" | "CENTER" | "MAX" | "SPACE_BETWEEN";
  counterAxisAlignment?: "MIN" | "CENTER" | "MAX";
  wrapChildren?: boolean;
  gapMode?: "fixed" | "auto";
  strokesIncludedInLayout?: boolean;
  childrenStackOrder?: "first-on-top" | "last-on-top";
  alignTextBaseline?: boolean;

  // ── Text ────────────────────────────────────────────────────────────────
  text?: string;
  textColor?: TokenOrLiteral<string>;
  textSizing?: "auto" | "fixed";

  // Typography
  fontFamily?: TokenOrLiteral<string>;
  fontWeight?: TokenOrLiteral<number>;
  fontStyle?: "normal" | "italic";
  fontSize?: TokenOrLiteral<number>;
  lineHeight?: TokenOrLiteral<number>;
  letterSpacing?: TokenOrLiteral<number>;
  textAlign?: "left" | "center" | "right" | "justify";
  verticalAlign?: "top" | "middle" | "bottom";
  textDecoration?: "none" | "underline" | "line-through";
  textTransform?: "none" | "uppercase" | "lowercase" | "capitalize";
  paragraphSpacing?: number;

  // OpenType features
  ligatures?: boolean;
  contextualAlternates?: boolean;
  ordinals?: boolean;
  fractions?: boolean;
  caseSensitiveForms?: boolean;
  smallCaps?: boolean;
  numberPosition?: "normal" | "subscript" | "superscript";
  stylisticSets?: number[];

  // Text decoration detail
  textDecorationStyle?: "solid" | "dotted" | "wavy";
  textDecorationThickness?: number;
  textDecorationOffset?: number;
  textDecorationSkipInk?: boolean;
  textDecorationColor?: TokenOrLiteral<string>;

  // Paragraph / layout
  paragraphIndent?: number;
  hangingPunctuation?: boolean;
  hangingLists?: boolean;
  listStyle?: "none" | "bullets" | "numbered";
  truncateText?: boolean;
  verticalTrim?: "normal" | "cap-height";

  // ── Frame ───────────────────────────────────────────────────────────────
  clipContent?: boolean;

  // ── Dev handoff ─────────────────────────────────────────────────────────
  readyForDev?: boolean;

  // ── Semantic slots ──────────────────────────────────────────────────────

  /** Semantic color roles (background, foreground, border, accent). */
  colorSlots?: ColorSlots;

  /** Semantic spacing roles (padding, margin, gap). */
  spacingSlots?: SpacingSlots;

  /** Semantic typography roles (fontFamily, fontSize, fontWeight, etc.). */
  typographySlots?: TypographySlots;

  // ── Component / Icon / Slot ─────────────────────────────────────────────

  /** Component catalogue reference (for `component-instance` nodes). */
  componentRef?: ComponentRef;

  /** Icon reference (for `icon` nodes). */
  iconRef?: IconRef;

  /** Slot definition (for `slot` nodes). */
  slotDef?: SlotDef;

  // ── Behavioral annotations ──────────────────────────────────────────────

  /** Bindings from node properties to runtime data sources. */
  dataBindings?: DataBinding[];

  /** Feature-flag gating. */
  featureGate?: FeatureFlagGate;

  /** Internationalisation keys: `{ propName: "i18n.key" }`. */
  i18nKeys?: Record<string, string>;

  /** Event handlers for interactive nodes. */
  eventHandlers?: EventHandler[];

  // ── State & responsive overrides ────────────────────────────────────────

  /** Visual overrides for interaction states (hover, focus, etc.). */
  stateOverrides?: StateOverride[];

  /** Responsive style overrides keyed by named breakpoint. */
  breakpointRules?: BreakpointRule[];
}
