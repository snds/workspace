// ─── Semantic Design IR — Public API ─────────────────────────────────────────
// Barrel export for the IR type system, compatibility layer, and resolver.
// ──────────────────────────────────────────────────────────────────────────────

// ── Types ────────────────────────────────────────────────────────────────────
export type {
  // Token reference primitives
  TokenRef,
  TokenOrLiteral,

  // Node types
  IRNodeType,
  IRNode,

  // Semantic slots
  ColorSlots,
  SpacingSlots,
  TypographySlots,

  // Effects
  IREffect,

  // Behavioral annotations
  DataBinding,
  FeatureFlagGate,
  EventHandler,

  // State & responsive overrides
  InteractionState,
  VisualOverrideProps,
  StateOverride,
  BreakpointOverrideProps,
  BreakpointRule,

  // Component / Icon / Slot references
  ComponentRef,
  IconRef,
  SlotDef,
} from "./types";

// ── Runtime (type guard) ─────────────────────────────────────────────────────
export { isTokenRef } from "./types";

// ── Compatibility layer ──────────────────────────────────────────────────────
export type { ResolverFn } from "./compat";
export { canvasNodeToIR, irNodeToCanvasNode } from "./compat";

// ── Token resolver ───────────────────────────────────────────────────────────
export { TokenResolver } from "./resolver";
