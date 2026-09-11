// ─── Component Catalog — Barrel Export ────────────────────────────────────────
// Public API for the component catalog system.

// Core types
export type {
  ComponentBlueprint,
  ComponentCategory,
  ComponentPropDef,
  ComponentSlotDef,
  ComponentEventDef,
  ComponentVariant,
  CanvasTemplate,
  CanvasTemplateChild,
  LibraryMapping,
} from "./types";

// Catalog class
export { ComponentCatalog } from "./catalog";

// IR node conversion
export { blueprintToNodeSpec } from "./toIRNodes";
export type { NodeSpec } from "./toIRNodes";

// Builtin blueprints
export { BUILTIN_BLUEPRINTS } from "./builtin";
export {
  buttonBlueprint,
  badgeBlueprint,
  inputBlueprint,
  textareaBlueprint,
  checkboxBlueprint,
  switchBlueprint,
  selectBlueprint,
  avatarBlueprint,
  cardBlueprint,
  tabsBlueprint,
  accordionBlueprint,
  dialogBlueprint,
  dropdownBlueprint,
  tooltipBlueprint,
  toastBlueprint,
  alertBlueprint,
  progressBlueprint,
  sliderBlueprint,
  tableBlueprint,
  separatorBlueprint,
  sheetBlueprint,
  skeletonBlueprint,
  breadcrumbBlueprint,
  paginationBlueprint,
  toggleBlueprint,
} from "./builtin";
