// ─── Builtin Component Blueprints ────────────────────────────────────────────
// Re-exports every built-in component blueprint and provides the
// BUILTIN_BLUEPRINTS array for batch registration with the catalog.

import type { ComponentBlueprint } from "../types";

import { buttonBlueprint } from "./button";
import { badgeBlueprint } from "./badge";
import { inputBlueprint } from "./input";
import { textareaBlueprint } from "./textarea";
import { checkboxBlueprint } from "./checkbox";
import { switchBlueprint } from "./switch";
import { selectBlueprint } from "./select";
import { avatarBlueprint } from "./avatar";
import { cardBlueprint } from "./card";
import { tabsBlueprint } from "./tabs";
import { accordionBlueprint } from "./accordion";
import { dialogBlueprint } from "./dialog";
import { dropdownBlueprint } from "./dropdown";
import { tooltipBlueprint } from "./tooltip";
import { toastBlueprint } from "./toast";
import { alertBlueprint } from "./alert";
import { progressBlueprint } from "./progress";
import { sliderBlueprint } from "./slider";
import { tableBlueprint } from "./table";
import { separatorBlueprint } from "./separator";
import { sheetBlueprint } from "./sheet";
import { skeletonBlueprint } from "./skeleton";
import { breadcrumbBlueprint } from "./breadcrumb";
import { paginationBlueprint } from "./pagination";
import { toggleBlueprint } from "./toggle";

// Re-export individual blueprints
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
};

/** All built-in component blueprints, ready for batch registration */
export const BUILTIN_BLUEPRINTS: ComponentBlueprint[] = [
  // Action
  buttonBlueprint,
  toggleBlueprint,

  // Input
  inputBlueprint,
  textareaBlueprint,
  selectBlueprint,
  checkboxBlueprint,
  switchBlueprint,
  sliderBlueprint,

  // Display
  badgeBlueprint,
  avatarBlueprint,
  cardBlueprint,
  tableBlueprint,

  // Feedback
  alertBlueprint,
  toastBlueprint,
  progressBlueprint,
  skeletonBlueprint,

  // Navigation
  tabsBlueprint,
  breadcrumbBlueprint,
  paginationBlueprint,

  // Overlay
  dialogBlueprint,
  sheetBlueprint,
  dropdownBlueprint,
  tooltipBlueprint,

  // Layout
  separatorBlueprint,
  accordionBlueprint,
];
