import type { CanvasRenderer, RenderableNode, RenderContext, HitTestResult } from './types';

/**
 * Konva/Canvas2D implementation of the CanvasRenderer interface.
 *
 * This is a STUB — method bodies will be filled in Phase 5 when we
 * integrate with the canvas workspace. The key architectural idea:
 * instead of react-konva JSX elements reconciled by React, we drive
 * Konva's imperative API directly, giving us full control over the
 * render loop and eliminating React reconciliation overhead.
 */
export class KonvaRenderer implements CanvasRenderer {
  private stage: unknown = null; // Will be Konva.Stage
  private layer: unknown = null; // Will be Konva.Layer
  private nodeShapes: Map<string, unknown> = new Map(); // nodeId -> Konva shape

  init(container: HTMLDivElement): void {
    // TODO: Create Konva.Stage sized to container, attach a main Konva.Layer.
    // Will use imperative Konva API instead of react-konva.
    // Example:
    //   this.stage = new Konva.Stage({ container, width: ..., height: ... });
    //   this.layer = new Konva.Layer();
    //   this.stage.add(this.layer);
    void container;
  }

  dispose(): void {
    // TODO: Destroy Konva stage and clean up event listeners.
    // this.stage.destroy();
    this.nodeShapes.clear();
    this.stage = null;
    this.layer = null;
  }

  render(nodes: Map<string, RenderableNode>, context: RenderContext): void {
    // TODO: Diff against current nodeShapes map.
    //   - New nodes: create Konva shapes and add to layer
    //   - Changed nodes: update existing shape attrs
    //   - Removed nodes: destroy shapes and remove from map
    //   - Apply viewport transform (zoom/pan) to stage
    //   - Call this.layer.batchDraw() once at the end
    //
    // This is the key perf win: one batch draw instead of
    // React reconciling hundreds of <Rect>, <Text>, etc. elements.
    void nodes;
    void context;
  }

  renderNode(node: RenderableNode, context: RenderContext): void {
    // TODO: Create or update a single Konva shape for this node.
    // Look up nodeShapes.get(node.id) — if it exists, update attrs;
    // otherwise create the appropriate shape (Rect, Text, Group, etc.)
    // and add it to the layer.
    void node;
    void context;
  }

  removeNode(nodeId: string): void {
    // TODO: Find the Konva shape in nodeShapes, call .destroy(), remove from map.
    // const shape = this.nodeShapes.get(nodeId);
    // if (shape) { shape.destroy(); this.nodeShapes.delete(nodeId); }
    void nodeId;
  }

  clear(): void {
    // TODO: Remove all shapes from the layer and clear the nodeShapes map.
    // (this.layer as any)?.destroyChildren();
    void this.layer;
    this.nodeShapes.clear();
  }

  hitTest(screenX: number, screenY: number, context: RenderContext): HitTestResult | null {
    // TODO: Use Konva's getIntersection({ x, y }) on the stage to find
    // the topmost shape at these coordinates. Walk up through groups to
    // build the allNodeIds array (front-to-back).
    void screenX;
    void screenY;
    void context;
    return null;
  }

  async toImage(format: "png" | "jpeg" | "svg" = "png", quality: number = 1): Promise<string> {
    // TODO: Use Konva stage.toDataURL({ mimeType, quality }) to export.
    void format;
    void quality;
    return '';
  }

  screenToCanvas(screenX: number, screenY: number, context: RenderContext): { x: number; y: number } {
    return {
      x: (screenX - context.panX) / context.zoom,
      y: (screenY - context.panY) / context.zoom,
    };
  }

  canvasToScreen(canvasX: number, canvasY: number, context: RenderContext): { x: number; y: number } {
    return {
      x: canvasX * context.zoom + context.panX,
      y: canvasY * context.zoom + context.panY,
    };
  }

  setCursor(cursor: string): void {
    // TODO: Set cursor on the stage's container element.
    // const container = this.stage?.container();
    // if (container) container.style.cursor = cursor;
    void cursor;
  }

  getNativeContext(): unknown {
    return this.stage;
  }
}
