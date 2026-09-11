// ─── Component-Scoped Token Definitions ──────────────────────────────────────
// Default token "slots" for common UI components. Each slot maps a role
// (e.g. "background") to a semantic token reference and an optional CSS
// property, enabling automated code generation and theme wiring.

// ─── Types ───────────────────────────────────────────────────────────────────

/** A named group of token definitions scoped to a single component. */
export interface ComponentTokenScope {
  /** Component this scope applies to (e.g. "button", "input"). */
  component: string;
  /** Token definitions within this scope, keyed by slot name. */
  tokens: Record<string, ComponentTokenDef>;
}

/** A single token "slot" inside a component scope. */
export interface ComponentTokenDef {
  /** Human-readable role description of what this token controls. */
  role: string;
  /** Default value — usually a reference path to a semantic token. */
  defaultRef: string;
  /** The CSS property this token maps to (used for code generation). */
  cssProperty?: string;
}

// ─── Built-in component token scopes ─────────────────────────────────────────

/** Default token scopes for the most common UI components. */
export const BUILTIN_COMPONENT_TOKENS: ComponentTokenScope[] = [
  // ── Button ─────────────────────────────────────────────────────────────
  {
    component: "button",
    tokens: {
      background: {
        role: "Default background color",
        defaultRef: "color.semantic.primary",
        cssProperty: "background-color",
      },
      foreground: {
        role: "Default text / icon color",
        defaultRef: "color.semantic.primary-foreground",
        cssProperty: "color",
      },
      border: {
        role: "Border color",
        defaultRef: "color.semantic.border",
        cssProperty: "border-color",
      },
      "hover-background": {
        role: "Background on hover state",
        defaultRef: "color.semantic.primary-hover",
        cssProperty: "background-color",
      },
      "focus-ring": {
        role: "Focus ring / outline color",
        defaultRef: "color.semantic.ring",
        cssProperty: "outline-color",
      },
      "disabled-opacity": {
        role: "Opacity when disabled",
        defaultRef: "number.opacity.disabled",
        cssProperty: "opacity",
      },
      "font-size": {
        role: "Text size",
        defaultRef: "font.size.sm",
        cssProperty: "font-size",
      },
      "font-weight": {
        role: "Text weight",
        defaultRef: "font.weight.medium",
        cssProperty: "font-weight",
      },
      "padding-x": {
        role: "Horizontal padding",
        defaultRef: "spacing.4",
        cssProperty: "padding-inline",
      },
      "padding-y": {
        role: "Vertical padding",
        defaultRef: "spacing.2",
        cssProperty: "padding-block",
      },
      "border-radius": {
        role: "Corner radius",
        defaultRef: "radius.md",
        cssProperty: "border-radius",
      },
    },
  },

  // ── Input ──────────────────────────────────────────────────────────────
  {
    component: "input",
    tokens: {
      background: {
        role: "Input background",
        defaultRef: "color.semantic.input",
        cssProperty: "background-color",
      },
      foreground: {
        role: "Input text color",
        defaultRef: "color.semantic.foreground",
        cssProperty: "color",
      },
      border: {
        role: "Default border",
        defaultRef: "color.semantic.border",
        cssProperty: "border-color",
      },
      placeholder: {
        role: "Placeholder text color",
        defaultRef: "color.semantic.muted-foreground",
        cssProperty: "color",
      },
      "focus-border": {
        role: "Border color on focus",
        defaultRef: "color.semantic.ring",
        cssProperty: "border-color",
      },
      "error-border": {
        role: "Border color in error state",
        defaultRef: "color.semantic.destructive",
        cssProperty: "border-color",
      },
      "font-size": {
        role: "Text size",
        defaultRef: "font.size.sm",
        cssProperty: "font-size",
      },
      "padding-x": {
        role: "Horizontal padding",
        defaultRef: "spacing.3",
        cssProperty: "padding-inline",
      },
      "padding-y": {
        role: "Vertical padding",
        defaultRef: "spacing.2",
        cssProperty: "padding-block",
      },
      "border-radius": {
        role: "Corner radius",
        defaultRef: "radius.md",
        cssProperty: "border-radius",
      },
    },
  },

  // ── Card ───────────────────────────────────────────────────────────────
  {
    component: "card",
    tokens: {
      background: {
        role: "Card surface background",
        defaultRef: "color.semantic.card",
        cssProperty: "background-color",
      },
      foreground: {
        role: "Card text color",
        defaultRef: "color.semantic.card-foreground",
        cssProperty: "color",
      },
      border: {
        role: "Card border color",
        defaultRef: "color.semantic.border",
        cssProperty: "border-color",
      },
      shadow: {
        role: "Card box shadow",
        defaultRef: "shadow.md",
        cssProperty: "box-shadow",
      },
      padding: {
        role: "Inner padding",
        defaultRef: "spacing.6",
        cssProperty: "padding",
      },
      "border-radius": {
        role: "Corner radius",
        defaultRef: "radius.lg",
        cssProperty: "border-radius",
      },
    },
  },

  // ── Badge ──────────────────────────────────────────────────────────────
  {
    component: "badge",
    tokens: {
      background: {
        role: "Badge background",
        defaultRef: "color.semantic.primary",
        cssProperty: "background-color",
      },
      foreground: {
        role: "Badge text color",
        defaultRef: "color.semantic.primary-foreground",
        cssProperty: "color",
      },
      "font-size": {
        role: "Text size",
        defaultRef: "font.size.xs",
        cssProperty: "font-size",
      },
      "padding-x": {
        role: "Horizontal padding",
        defaultRef: "spacing.2.5",
        cssProperty: "padding-inline",
      },
      "padding-y": {
        role: "Vertical padding",
        defaultRef: "spacing.0.5",
        cssProperty: "padding-block",
      },
      "border-radius": {
        role: "Corner radius",
        defaultRef: "radius.full",
        cssProperty: "border-radius",
      },
    },
  },

  // ── Dialog / Modal ─────────────────────────────────────────────────────
  {
    component: "dialog",
    tokens: {
      background: {
        role: "Dialog surface background",
        defaultRef: "color.semantic.card",
        cssProperty: "background-color",
      },
      foreground: {
        role: "Dialog text color",
        defaultRef: "color.semantic.foreground",
        cssProperty: "color",
      },
      "overlay-background": {
        role: "Overlay / backdrop color",
        defaultRef: "color.semantic.overlay",
        cssProperty: "background-color",
      },
      border: {
        role: "Dialog border",
        defaultRef: "color.semantic.border",
        cssProperty: "border-color",
      },
      shadow: {
        role: "Dialog shadow",
        defaultRef: "shadow.lg",
        cssProperty: "box-shadow",
      },
      padding: {
        role: "Inner content padding",
        defaultRef: "spacing.6",
        cssProperty: "padding",
      },
      "border-radius": {
        role: "Corner radius",
        defaultRef: "radius.lg",
        cssProperty: "border-radius",
      },
    },
  },

  // ── Select ─────────────────────────────────────────────────────────────
  {
    component: "select",
    tokens: {
      background: {
        role: "Select trigger background",
        defaultRef: "color.semantic.input",
        cssProperty: "background-color",
      },
      foreground: {
        role: "Select text color",
        defaultRef: "color.semantic.foreground",
        cssProperty: "color",
      },
      border: {
        role: "Select border",
        defaultRef: "color.semantic.border",
        cssProperty: "border-color",
      },
      "focus-border": {
        role: "Border on focus",
        defaultRef: "color.semantic.ring",
        cssProperty: "border-color",
      },
      "dropdown-background": {
        role: "Dropdown panel background",
        defaultRef: "color.semantic.popover",
        cssProperty: "background-color",
      },
      "item-hover": {
        role: "Hovered option background",
        defaultRef: "color.semantic.accent",
        cssProperty: "background-color",
      },
      "padding-x": {
        role: "Horizontal padding",
        defaultRef: "spacing.3",
        cssProperty: "padding-inline",
      },
      "padding-y": {
        role: "Vertical padding",
        defaultRef: "spacing.2",
        cssProperty: "padding-block",
      },
      "border-radius": {
        role: "Corner radius",
        defaultRef: "radius.md",
        cssProperty: "border-radius",
      },
    },
  },

  // ── Checkbox ───────────────────────────────────────────────────────────
  {
    component: "checkbox",
    tokens: {
      background: {
        role: "Unchecked background",
        defaultRef: "color.semantic.input",
        cssProperty: "background-color",
      },
      "checked-background": {
        role: "Checked state background",
        defaultRef: "color.semantic.primary",
        cssProperty: "background-color",
      },
      "check-color": {
        role: "Check-mark color",
        defaultRef: "color.semantic.primary-foreground",
        cssProperty: "color",
      },
      border: {
        role: "Border color",
        defaultRef: "color.semantic.border",
        cssProperty: "border-color",
      },
      "focus-ring": {
        role: "Focus ring color",
        defaultRef: "color.semantic.ring",
        cssProperty: "outline-color",
      },
      "border-radius": {
        role: "Corner radius",
        defaultRef: "radius.sm",
        cssProperty: "border-radius",
      },
      size: {
        role: "Width and height",
        defaultRef: "sizing.4",
        cssProperty: "width",
      },
    },
  },

  // ── Toggle / Switch ────────────────────────────────────────────────────
  {
    component: "switch",
    tokens: {
      "track-background": {
        role: "Track background (off state)",
        defaultRef: "color.semantic.muted",
        cssProperty: "background-color",
      },
      "track-active": {
        role: "Track background (on state)",
        defaultRef: "color.semantic.primary",
        cssProperty: "background-color",
      },
      "thumb-background": {
        role: "Thumb color",
        defaultRef: "color.semantic.background",
        cssProperty: "background-color",
      },
      "focus-ring": {
        role: "Focus ring color",
        defaultRef: "color.semantic.ring",
        cssProperty: "outline-color",
      },
      "track-border-radius": {
        role: "Track corner radius",
        defaultRef: "radius.full",
        cssProperty: "border-radius",
      },
    },
  },

  // ── Tooltip ────────────────────────────────────────────────────────────
  {
    component: "tooltip",
    tokens: {
      background: {
        role: "Tooltip background",
        defaultRef: "color.semantic.foreground",
        cssProperty: "background-color",
      },
      foreground: {
        role: "Tooltip text color",
        defaultRef: "color.semantic.background",
        cssProperty: "color",
      },
      "font-size": {
        role: "Text size",
        defaultRef: "font.size.xs",
        cssProperty: "font-size",
      },
      "padding-x": {
        role: "Horizontal padding",
        defaultRef: "spacing.3",
        cssProperty: "padding-inline",
      },
      "padding-y": {
        role: "Vertical padding",
        defaultRef: "spacing.1.5",
        cssProperty: "padding-block",
      },
      "border-radius": {
        role: "Corner radius",
        defaultRef: "radius.md",
        cssProperty: "border-radius",
      },
    },
  },

  // ── Avatar ─────────────────────────────────────────────────────────────
  {
    component: "avatar",
    tokens: {
      background: {
        role: "Fallback background",
        defaultRef: "color.semantic.muted",
        cssProperty: "background-color",
      },
      foreground: {
        role: "Initials text color",
        defaultRef: "color.semantic.muted-foreground",
        cssProperty: "color",
      },
      border: {
        role: "Avatar border",
        defaultRef: "color.semantic.border",
        cssProperty: "border-color",
      },
      "border-radius": {
        role: "Corner radius (full = circle)",
        defaultRef: "radius.full",
        cssProperty: "border-radius",
      },
      size: {
        role: "Default width/height",
        defaultRef: "sizing.10",
        cssProperty: "width",
      },
    },
  },
];
