export type NodeType = "frame" | "rectangle" | "text" | "group";

export type EffectType = "DROP_SHADOW" | "INNER_SHADOW" | "LAYER_BLUR" | "BACKGROUND_BLUR";

export interface Effect {
  type: EffectType;
  visible: boolean;
  color?: string;    // hex
  offsetX?: number;
  offsetY?: number;
  blur?: number;
  spread?: number;
  radius?: number;   // for blur effects
}

export interface CanvasNode {
  id: string;
  type: NodeType;
  name: string;
  parentId: string | null;
  pageId: string;   // which page this node belongs to
  order: number; // higher = in front

  // Transform
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number; // degrees

  // Appearance
  fill: string | null;       // hex or null (transparent)
  fillOpacity: number;       // 0–1 (fill-specific opacity, separate from node opacity)
  stroke: string | null;     // hex or null
  strokeWidth: number;
  opacity: number;           // 0–1
  cornerRadius: number;      // uniform corner radius (rectangles & frames)
  visible: boolean;
  locked: boolean;
  flipX?: boolean;  // horizontal mirror
  flipY?: boolean;  // vertical mirror

  // Blend mode (CSS compositing)
  blendMode?: string;        // "PASS_THROUGH" | "NORMAL" | "MULTIPLY" | etc.

  // Aspect ratio
  aspectRatioLocked?: boolean;

  // Split corner radii (override cornerRadius when set)
  cornerRadiusTopLeft?: number;
  cornerRadiusTopRight?: number;
  cornerRadiusBottomRight?: number;
  cornerRadiusBottomLeft?: number;
  cornerSmoothing?: number;  // 0–100 (iOS-style smooth corners)

  // Stroke
  strokePosition?: "inside" | "center" | "outside";

  // Effects (drop shadow, inner shadow, blur)
  effects?: Effect[];

  // Auto layout (frame only)
  layoutMode?: "NONE" | "HORIZONTAL" | "VERTICAL" | "GRID";
  primaryAxisSizing?: "FIXED" | "HUG" | "FILL";
  counterAxisSizing?: "FIXED" | "HUG" | "FILL";
  paddingTop?: number;
  paddingBottom?: number;
  paddingLeft?: number;
  paddingRight?: number;
  itemSpacing?: number;
  counterAxisSpacing?: number;
  primaryAxisAlignment?: "MIN" | "CENTER" | "MAX" | "SPACE_BETWEEN";
  counterAxisAlignment?: "MIN" | "CENTER" | "MAX";
  wrapChildren?: boolean;           // horizontal flow: enable wrapping
  gapMode?: "fixed" | "auto";       // gap: fixed value or auto-distribute
  strokesIncludedInLayout?: boolean; // AL settings: include strokes in layout bounds
  childrenStackOrder?: "first-on-top" | "last-on-top"; // AL stacking order
  alignTextBaseline?: boolean;       // AL text baseline alignment mode

  // Text-specific
  text?: string;
  textColor?: string;
  textSizing?: "auto" | "fixed";  // "auto" = hug contents, "fixed" = manual width/height

  // Typography
  fontFamily?: string;
  fontWeight?: number;       // 100 | 200 | 300 | 400 | 500 | 600 | 700 | 800 | 900
  fontStyle?: "normal" | "italic";
  fontSize?: number;         // px
  lineHeight?: number;       // multiplier, e.g. 1.5
  letterSpacing?: number;    // px
  textAlign?: "left" | "center" | "right" | "justify";
  verticalAlign?: "top" | "middle" | "bottom";
  textDecoration?: "none" | "underline" | "line-through";
  textTransform?: "none" | "uppercase" | "lowercase" | "capitalize";
  paragraphSpacing?: number; // px between paragraphs

  // OpenType / font features
  ligatures?: boolean;
  contextualAlternates?: boolean;
  ordinals?: boolean;
  fractions?: boolean;
  caseSensitiveForms?: boolean;
  smallCaps?: boolean;
  numberPosition?: "normal" | "subscript" | "superscript";
  stylisticSets?: number[];      // e.g. [1, 3] → ss01, ss03

  // Underline detail
  textDecorationStyle?: "solid" | "dotted" | "wavy";
  textDecorationThickness?: number; // 0–100 (% of font size)
  textDecorationOffset?: number;    // 0–100 (% of font size)
  textDecorationSkipInk?: boolean;
  textDecorationColor?: string;

  // Paragraph / layout
  paragraphIndent?: number;
  hangingPunctuation?: boolean;
  hangingLists?: boolean;
  listStyle?: "none" | "bullets" | "numbered";
  truncateText?: boolean;
  verticalTrim?: "normal" | "cap-height";

  // Frame-specific
  clipContent?: boolean;     // mask children to frame bounds

  // Dev handoff
  readyForDev?: boolean;     // frame is marked ready for engineering
}

export interface CanvasTreeNode extends CanvasNode {
  children: CanvasTreeNode[];
  depth: number;
}

export interface DrawingRect {
  x: number;
  y: number;
  width: number;
  height: number;
}
