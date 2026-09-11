/** Visual properties needed to render a node */
export interface RenderableNode {
  id: string;
  type: string;
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;

  // Visual
  fill: string | null;
  fillOpacity: number;
  stroke: string | null;
  strokeWidth: number;
  opacity: number;
  cornerRadius: number;
  visible: boolean;
  blendMode?: string;
  clipContent?: boolean;
  flipX?: boolean;
  flipY?: boolean;

  // Split corners
  cornerRadiusTopLeft?: number;
  cornerRadiusTopRight?: number;
  cornerRadiusBottomRight?: number;
  cornerRadiusBottomLeft?: number;
  cornerSmoothing?: number;

  // Stroke
  strokePosition?: "inside" | "center" | "outside";

  // Effects
  effects?: Array<{
    type: string;
    visible: boolean;
    color?: string;
    offsetX?: number;
    offsetY?: number;
    blur?: number;
    spread?: number;
    radius?: number;
  }>;

  // Text
  text?: string;
  textColor?: string;
  fontFamily?: string;
  fontWeight?: number;
  fontStyle?: "normal" | "italic";
  fontSize?: number;
  lineHeight?: number;
  letterSpacing?: number;
  textAlign?: "left" | "center" | "right" | "justify";
  verticalAlign?: "top" | "middle" | "bottom";
  textDecoration?: string;
  textTransform?: string;

  // Children
  children?: string[]; // child node IDs
  parentId: string | null;
}

/** Current rendering context (viewport state) */
export interface RenderContext {
  /** Current zoom level (1 = 100%) */
  zoom: number;
  /** Pan offset X */
  panX: number;
  /** Pan offset Y */
  panY: number;
  /** Viewport width in pixels */
  viewportWidth: number;
  /** Viewport height in pixels */
  viewportHeight: number;
  /** Currently selected node IDs */
  selectedIds: Set<string>;
  /** Currently hovered node ID */
  hoveredId: string | null;
  /** Whether we're in a drag/transform operation */
  isInteracting: boolean;
  /** Device pixel ratio for crisp rendering */
  devicePixelRatio: number;
}

/** Hit test result */
export interface HitTestResult {
  /** The node that was hit (closest to front) */
  nodeId: string;
  /** All nodes at this point, front to back */
  allNodeIds: string[];
  /** Hit coordinates in canvas space */
  canvasX: number;
  canvasY: number;
}

/** Abstract canvas renderer interface */
export interface CanvasRenderer {
  /** Initialize the renderer with a container element */
  init(container: HTMLDivElement): void;

  /** Dispose of the renderer and clean up resources */
  dispose(): void;

  /** Render a set of nodes with the given context */
  render(nodes: Map<string, RenderableNode>, context: RenderContext): void;

  /** Render a single node (for incremental updates) */
  renderNode(node: RenderableNode, context: RenderContext): void;

  /** Remove a rendered node */
  removeNode(nodeId: string): void;

  /** Clear all rendered content */
  clear(): void;

  /** Hit test at screen coordinates */
  hitTest(screenX: number, screenY: number, context: RenderContext): HitTestResult | null;

  /** Export the canvas to an image */
  toImage(format?: "png" | "jpeg" | "svg", quality?: number): Promise<string>;

  /** Convert screen coordinates to canvas coordinates */
  screenToCanvas(screenX: number, screenY: number, context: RenderContext): { x: number; y: number };

  /** Convert canvas coordinates to screen coordinates */
  canvasToScreen(canvasX: number, canvasY: number, context: RenderContext): { x: number; y: number };

  /** Set cursor style */
  setCursor(cursor: string): void;

  /** Get the underlying rendering context (for advanced operations) */
  getNativeContext(): unknown;
}
