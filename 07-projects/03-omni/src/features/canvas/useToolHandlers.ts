import { useRef, useCallback } from "react";
import type Konva from "konva";
import type { KonvaEventObject } from "konva/lib/Node";
import { useCanvasStore } from "@/stores/canvas.store";
import { useUIStore } from "@/stores/ui.store";
import { usePagesStore } from "@/stores/pages.store";
import type { DrawingRect } from "@/types/canvas";
import { measureText } from "@/lib/measureText";

interface UseToolHandlersOptions {
  zoom: number;
  stageX: number;
  stageY: number;
  onStartPan(x: number, y: number): void;
  onPan(dx: number, dy: number): void;
  onEndPan(): void;
  onDrawingChange(rect: DrawingRect | null): void;
  onTextNodeCreated?(id: string): void;
}

/** Convert a screen-space point to world (canvas) coordinates */
function toWorld(screenX: number, screenY: number, stageX: number, stageY: number, zoom: number) {
  return {
    x: (screenX - stageX) / zoom,
    y: (screenY - stageY) / zoom,
  };
}

/** Normalize a rectangle so width/height are always positive */
function normalizeRect(x1: number, y1: number, x2: number, y2: number): DrawingRect {
  return {
    x: Math.min(x1, x2),
    y: Math.min(y1, y2),
    width: Math.abs(x2 - x1),
    height: Math.abs(y2 - y1),
  };
}

const MIN_DRAW_SIZE = 4; // px in world space

export function useToolHandlers({
  zoom,
  stageX,
  stageY,
  onStartPan,
  onPan,
  onEndPan,
  onDrawingChange,
  onTextNodeCreated,
}: UseToolHandlersOptions) {
  const { addNode, selectNodes, clearSelection } = useCanvasStore();
  const { activeTool, setActiveTool } = useUIStore();

  // Drawing state
  const drawOrigin = useRef<{ x: number; y: number } | null>(null);
  // Pan state
  const panOrigin = useRef<{ x: number; y: number; stageX: number; stageY: number } | null>(null);
  // Middle mouse button pan
  const isMiddlePan = useRef(false);

  const getPointerWorld = useCallback(
    (stage: Konva.Stage) => {
      const pos = stage.getPointerPosition();
      if (!pos) return null;
      return toWorld(pos.x, pos.y, stageX, stageY, zoom);
    },
    [zoom, stageX, stageY]
  );

  const onStageMouseDown = useCallback(
    (e: KonvaEventObject<MouseEvent>) => {
      const stage = e.target.getStage();
      if (!stage) return;

      // Middle mouse button — always pan
      if (e.evt.button === 1) {
        e.evt.preventDefault();
        isMiddlePan.current = true;
        onStartPan(e.evt.clientX, e.evt.clientY);
        return;
      }

      if (activeTool === "hand") {
        onStartPan(e.evt.clientX, e.evt.clientY);
        return;
      }

      if (activeTool === "select") {
        if (e.target === stage) {
          // Start a marquee drag on the empty background
          if (!e.evt.shiftKey) clearSelection();
          const world = getPointerWorld(stage);
          if (world) {
            drawOrigin.current = world;
            onDrawingChange({ x: world.x, y: world.y, width: 0, height: 0 });
          }
        }
        return;
      }

      // Drawing tools: frame, shape, text
      if (activeTool === "frame" || activeTool === "shape" || activeTool === "text") {
        const world = getPointerWorld(stage);
        if (!world) return;
        drawOrigin.current = world;
        onDrawingChange({ x: world.x, y: world.y, width: 0, height: 0 });
      }
    },
    [activeTool, getPointerWorld, clearSelection, onStartPan, onDrawingChange]
  );

  const onStageMouseMove = useCallback(
    (e: KonvaEventObject<MouseEvent>) => {
      const stage = e.target.getStage();
      if (!stage) return;

      // Pan
      if (isMiddlePan.current || activeTool === "hand") {
        if (panOrigin.current !== null) {
          // Pan is handled externally via onPan; the stage computes the delta
        }
        onPan(e.evt.movementX, e.evt.movementY);
        return;
      }

      // Drawing / marquee preview
      if (
        drawOrigin.current &&
        (activeTool === "frame" || activeTool === "shape" || activeTool === "text" || activeTool === "select")
      ) {
        const world = getPointerWorld(stage);
        if (!world) return;
        const rect = normalizeRect(drawOrigin.current.x, drawOrigin.current.y, world.x, world.y);
        onDrawingChange(rect);
      }
    },
    [activeTool, getPointerWorld, onPan, onDrawingChange]
  );

  const onStageMouseUp = useCallback(
    (e: KonvaEventObject<MouseEvent>) => {
      // Middle pan release
      if (e.evt.button === 1 && isMiddlePan.current) {
        isMiddlePan.current = false;
        onEndPan();
        return;
      }

      if (activeTool === "hand") {
        onEndPan();
        return;
      }

      // Finalize marquee selection
      if (activeTool === "select" && drawOrigin.current) {
        const stage = e.target.getStage();
        if (stage) {
          const world = getPointerWorld(stage);
          if (world) {
            const rect = normalizeRect(drawOrigin.current.x, drawOrigin.current.y, world.x, world.y);
            if (rect.width > MIN_DRAW_SIZE || rect.height > MIN_DRAW_SIZE) {
              const { nodes: allNodes } = useCanvasStore.getState();
              const pageId = usePagesStore.getState().activePageId;
              // Select root-level nodes that intersect the marquee
              const hit = allNodes.filter(
                (n) =>
                  n.pageId === pageId &&
                  n.parentId === null &&
                  n.x < rect.x + rect.width &&
                  n.x + n.width > rect.x &&
                  n.y < rect.y + rect.height &&
                  n.y + n.height > rect.y,
              );
              if (hit.length > 0) selectNodes(hit.map((n) => n.id));
            }
          }
        }
        drawOrigin.current = null;
        onDrawingChange(null);
        return;
      }

      if (!drawOrigin.current) return;
      const stage = e.target.getStage();
      if (!stage) return;

      const world = getPointerWorld(stage);
      if (!world) { drawOrigin.current = null; onDrawingChange(null); return; }

      const rect = normalizeRect(drawOrigin.current.x, drawOrigin.current.y, world.x, world.y);
      drawOrigin.current = null;
      onDrawingChange(null);

      // Minimum size check
      if (rect.width < MIN_DRAW_SIZE && rect.height < MIN_DRAW_SIZE) {
        // Single click — place a default-sized node at click point
        let size: { width: number; height: number };
        if (activeTool === "text") {
          const measured = measureText({ text: "Text", fontSize: 16, fontFamily: "Inter, sans-serif", fontWeight: 400, lineHeight: 1.2 });
          size = measured;
        } else {
          size = { width: 100, height: 100 };
        }
        const finalRect = { x: world.x - size.width / 2, y: world.y - size.height / 2, ...size };
        commitNode(finalRect, false);
        return;
      }

      commitNode(rect, true);
    },
    [activeTool, getPointerWorld, onEndPan, onDrawingChange, addNode, setActiveTool, selectNodes]
  );

  function commitNode(rect: DrawingRect, dragged: boolean) {
    if (activeTool === "frame") {
      addNode({ type: "frame", name: "Frame", parentId: null, ...rect, rotation: 0, opacity: 1, visible: true, locked: false, fill: "#ffffff", stroke: null, strokeWidth: 1, cornerRadius: 0, clipContent: true });
    } else if (activeTool === "shape") {
      addNode({ type: "rectangle", name: "Rectangle", parentId: null, ...rect, rotation: 0, opacity: 1, visible: true, locked: false, fill: "#d4d4d4", stroke: null, strokeWidth: 1, cornerRadius: 0 });
    } else if (activeTool === "text") {
      const id = addNode({ type: "text", name: "Text", parentId: null, ...rect, rotation: 0, opacity: 1, visible: true, locked: false, fill: null, stroke: null, strokeWidth: 0, cornerRadius: 0, text: "Text", fontSize: 16, fontFamily: "Inter, sans-serif", fontWeight: "400", textAlign: "left", textColor: "#000000", textSizing: dragged ? "fixed" : "auto" });
      setActiveTool("select");
      onTextNodeCreated?.(id);
      return;
    }
    // Return to select after drawing
    setActiveTool("select");
  }

  return { onStageMouseDown, onStageMouseMove, onStageMouseUp };
}
