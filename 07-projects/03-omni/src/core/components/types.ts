// ─── Component Blueprint Type System ─────────────────────────────────────────
// Framework-agnostic component definitions with token bindings and library
// mappings. Part of the "Design Once, Output Anywhere" architecture.

/** Defines a reusable component's structure, props, and cross-library mappings */
export interface ComponentBlueprint {
  /** Unique identifier */
  id: string;
  /** Display name */
  name: string;
  /** Category for grouping in the assets panel */
  category: ComponentCategory;
  /** Human-readable description */
  description?: string;
  /** Icon name for the assets panel (semantic icon name) */
  icon?: string;
  /** Tags for search */
  tags?: string[];

  /** Props this component accepts */
  props: ComponentPropDef[];
  /** Named slots for content insertion */
  slots?: ComponentSlotDef[];
  /** Events this component can emit */
  events?: ComponentEventDef[];
  /** Visual variants (e.g. "default", "destructive", "outline") */
  variants?: ComponentVariant[];

  /** Token bindings — which design tokens control this component's appearance */
  tokenBindings: Record<string, string>;

  /** Canvas template — how to render this component on the canvas */
  canvasTemplate: CanvasTemplate;

  /** Library-specific mappings for code generation */
  libraryMappings: Record<string, LibraryMapping>;
}

export type ComponentCategory =
  | "action"     // Button, IconButton, Toggle
  | "input"      // Input, Textarea, Select, Checkbox, Switch, Slider, DatePicker
  | "display"    // Badge, Avatar, Card, Table, List
  | "feedback"   // Alert, Toast, Progress, Skeleton, Spinner
  | "navigation" // Tabs, Breadcrumb, Pagination, Menu, Sidebar
  | "overlay"    // Dialog, Sheet, Dropdown, Tooltip, Popover
  | "layout"     // Separator, Accordion, Collapsible
  | "typography" // Heading, Paragraph, Label, Caption
  | "media";     // Image, Video, Icon

export interface ComponentPropDef {
  name: string;
  type: "string" | "number" | "boolean" | "enum" | "color" | "icon" | "slot";
  label?: string;
  defaultValue?: unknown;
  /** For enum type */
  options?: { value: string; label: string }[];
  /** Is this prop required? */
  required?: boolean;
  /** Affects canvas rendering? */
  affectsCanvas?: boolean;
}

export interface ComponentSlotDef {
  name: string;
  label?: string;
  description?: string;
  /** Default content if slot is empty */
  defaultContent?: string;
  /** Allowed node types in this slot */
  allowedTypes?: string[];
}

export interface ComponentEventDef {
  name: string;
  label?: string;
  description?: string;
  /** Payload type description */
  payloadType?: string;
}

export interface ComponentVariant {
  id: string;
  name: string;
  /** Prop overrides that define this variant */
  propOverrides: Record<string, unknown>;
  /** Token binding overrides for this variant */
  tokenOverrides?: Record<string, string>;
  /** Canvas template overrides */
  canvasOverrides?: Partial<CanvasTemplate>;
}

/** How to render a component on the design canvas */
export interface CanvasTemplate {
  /** Root node type */
  type: "frame" | "rectangle" | "text";
  /** Default dimensions */
  width: number;
  height: number;
  /** Fill — can be a token reference string or literal */
  fill?: string;
  /** Corner radius */
  cornerRadius?: number;
  /** Stroke */
  stroke?: string;
  strokeWidth?: number;
  /** Opacity */
  opacity?: number;
  /** Child templates */
  children?: CanvasTemplateChild[];
}

export interface CanvasTemplateChild extends CanvasTemplate {
  /** Name for this child node */
  name: string;
  /** Offset from parent */
  offsetX: number;
  offsetY: number;
  /** Text content (for text nodes) */
  text?: string;
  textColor?: string;
  fontSize?: number;
  fontWeight?: number;
  textAlign?: "left" | "center" | "right";
  verticalAlign?: "top" | "middle" | "bottom";
}

/** Maps a component to a specific UI library's implementation */
export interface LibraryMapping {
  /** Library identifier (e.g. "shadcn", "mui", "chakra") */
  library: string;
  /** Import path */
  importPath: string;
  /** Component name in the library */
  componentName: string;
  /** Prop name mappings (our prop name -> library prop name) */
  propMappings?: Record<string, string>;
  /** Additional imports needed */
  additionalImports?: string[];
  /** Wrapper or composition pattern */
  wrapper?: string;
}
