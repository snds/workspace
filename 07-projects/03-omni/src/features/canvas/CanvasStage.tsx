// TODO: Migrate to use CanvasRenderer interface from @/core/renderer.
// During the migration period, the existing react-konva rendering is kept intact.
// IRNodeRenderer / ComponentInstanceRenderer / IconNodeRenderer are available
// but wired in as stubs (return null) until the rendering pipeline is connected.
import { useRef, useState, useEffect, useCallback } from "react";
import { Stage, Layer } from "react-konva";
import type Konva from "konva";
import { useCanvasStore } from "@/stores/canvas.store";
import { interactionState } from "@/core/renderer";
import { useUIStore } from "@/stores/ui.store";
import type { AppTheme } from "@/stores/ui.store";
import { usePagesStore } from "@/stores/pages.store";
import { useFontStore } from "@/stores/font.store";
import { useKeyboardShortcuts } from "./useKeyboardShortcuts";
import { useToolHandlers } from "./useToolHandlers";
import { CanvasNodeRenderer } from "./CanvasNodeRenderer";
import { DrawingPreview } from "./DrawingPreview";
import { SelectionOverlay } from "./SelectionOverlay";
import { TransformHandles, getSelectionBounds } from "./TransformHandles";
import { useTransform } from "./useTransform";
import { SnapGuides } from "./snap/SnapGuides";
import { Rulers } from "./Rulers";
import { PixelGrid } from "./PixelGrid";
import { CanvasContextMenu } from "./CanvasContextMenu";
import { CanvasLabels } from "./CanvasLabels";
import type { DrawingRect, CanvasNode } from "@/types/canvas";
import { measureText } from "@/lib/measureText";
import type React from "react";

const MIN_ZOOM = 0.05;
const MAX_ZOOM = 32;

// Theme-based default canvas background colors
const CANVAS_BG_DEFAULTS: Record<AppTheme, string> = {
  light: "#e8e7e8",
  dark: "#1a1a1c",
};

// Theme-based checkerboard tile colors
const CHECKER_COLORS: Record<AppTheme, { tile: string; base: string }> = {
  dark:  { tile: "#252427", base: "#1e1c20" },
  light: { tile: "#d4d2d6", base: "#e4e2e6" },
};

// Decompose a 6-digit hex color into [r, g, b] components
function hexToRgbParts(hex: string): [number, number, number] {
  const clean = hex.replace("#", "").padEnd(6, "0");
  return [
    parseInt(clean.slice(0, 2), 16),
    parseInt(clean.slice(2, 4), 16),
    parseInt(clean.slice(4, 6), 16),
  ];
}

export function CanvasStage() {
  const containerRef = useRef<HTMLDivElement>(null);
  const stageRef = useRef<Konva.Stage>(null);

  const [stageSize, setStageSize] = useState({ width: 800, height: 600 });
  const [drawingRect, setDrawingRect] = useState<DrawingRect | null>(null);
  const [editingNodeId, setEditingNodeId] = useState<string | null>(null);
  const [editText, setEditText] = useState("");

  const { nodes, selectedIds, hoveredId, stageX, stageY, modifiers, snapGuides, setStagePosition, updateNode, setHovered } = useCanvasStore();
  const { zoom, setZoom, activeTool, theme, canvasBgHex, canvasBgAlpha, showRulers, showGrid } = useUIStore();

  // Whether a transform (move/resize/rotate) is in progress — used to suppress hover events on shapes.
  const [transformActive, setTransformActive] = useState(false);

  // Custom transform system (modifier pattern)
  const { startResize, startRotate, startMove, continueTransform, endTransform, isTransforming } = useTransform();
  const activePageId = usePagesStore((s) => s.activePageId);

  // Pan state refs (not state — no re-render needed during pan)
  const isPanning = useRef(false);
  const panStart = useRef<{ clientX: number; clientY: number; stageX: number; stageY: number } | null>(null);

  // Deep-select mode: Cmd (Mac) / Ctrl (PC) held → click-through frames to children.
  // Only activates when Cmd/Ctrl is the sole modifier (not part of system shortcuts
  // like Cmd+Shift+4 for macOS screenshots). Resets on blur/visibility-change to
  // prevent the key getting "stuck" when a system shortcut steals focus.
  const [deepSelectActive, setDeepSelectActive] = useState(false);
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      // Activate only when Cmd/Ctrl is pressed without Shift or Alt — those combos
      // are almost always system/browser shortcuts, not canvas interactions.
      // Cmd+Shift+click (additive deep-select) is handled via evt.shiftKey at click time.
      if ((e.metaKey || e.ctrlKey) && !e.shiftKey && !e.altKey) {
        setDeepSelectActive(true);
      }
      // Mirror modifier key state into the mutable InteractionState singleton
      // so the renderer abstraction can read modifiers without a Zustand subscription.
      interactionState.updateModifiers(e.shiftKey, e.altKey, e.metaKey || e.ctrlKey);
    };
    const onKeyUp = (e: KeyboardEvent) => {
      if (!e.metaKey && !e.ctrlKey) setDeepSelectActive(false);
      interactionState.updateModifiers(e.shiftKey, e.altKey, e.metaKey || e.ctrlKey);
    };
    // Reset when window loses focus (system shortcuts, app switch, screenshot tools)
    const onBlur = () => setDeepSelectActive(false);
    const onVisChange = () => { if (document.hidden) setDeepSelectActive(false); };

    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("keyup", onKeyUp);
    window.addEventListener("blur", onBlur);
    document.addEventListener("visibilitychange", onVisChange);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("keyup", onKeyUp);
      window.removeEventListener("blur", onBlur);
      document.removeEventListener("visibilitychange", onVisChange);
    };
  }, []);

  // Resize observer
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const ro = new ResizeObserver(([entry]) => {
      const { width, height } = entry.contentRect;
      setStageSize({ width, height });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Keyboard shortcuts (pass stageSize so zoom-to-fit works)
  useKeyboardShortcuts(containerRef, stageSize);

  // Check for local font server on mount
  const { checkServer } = useFontStore();
  useEffect(() => { checkServer(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Re-draw stage when any font finishes loading (Google Fonts / local fonts)
  useEffect(() => {
    const redraw = () => stageRef.current?.batchDraw();
    document.fonts.addEventListener("loadingdone", redraw);
    return () => document.fonts.removeEventListener("loadingdone", redraw);
  }, []);

  // Wheel handler: pinch gesture (ctrlKey=true) → zoom toward cursor;
  // two-finger trackpad scroll (ctrlKey=false) → pan the canvas.
  // Registered as a non-passive native listener so preventDefault() actually
  // blocks the browser's swipe-to-navigate back/forward gesture.
  const handleWheel = useCallback(
    (e: WheelEvent) => {
      e.preventDefault();
      const stage = stageRef.current;
      if (!stage) return;

      if (e.ctrlKey) {
        // Pinch-to-zoom (macOS trackpad pinch or Ctrl+scroll)
        const scaleBy = 1.08;
        const oldZoom = zoom;
        let newZoom = e.deltaY < 0 ? oldZoom * scaleBy : oldZoom / scaleBy;
        newZoom = Math.max(MIN_ZOOM, Math.min(MAX_ZOOM, newZoom));

        const pointer = stage.getPointerPosition();
        if (!pointer) return;

        // World position under pointer before zoom
        const worldX = (pointer.x - stageX) / oldZoom;
        const worldY = (pointer.y - stageY) / oldZoom;

        setZoom(newZoom);
        setStagePosition(pointer.x - worldX * newZoom, pointer.y - worldY * newZoom);
      } else {
        // Two-finger scroll → pan (deltaX for horizontal, deltaY for vertical)
        setStagePosition(stageX - e.deltaX, stageY - e.deltaY);
      }
    },
    [zoom, stageX, stageY, setZoom, setStagePosition]
  );

  // Attach the wheel handler as non-passive so e.preventDefault() blocks
  // the browser's back/forward swipe navigation on macOS trackpads.
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    el.addEventListener("wheel", handleWheel, { passive: false });
    return () => el.removeEventListener("wheel", handleWheel);
  }, [handleWheel]);

  // Pan handlers passed to tool handlers
  const onStartPan = useCallback(
    (clientX: number, clientY: number) => {
      isPanning.current = true;
      panStart.current = { clientX, clientY, stageX, stageY };
    },
    [stageX, stageY]
  );

  const onPan = useCallback(
    (dx: number, dy: number) => {
      if (!isPanning.current) return;
      setStagePosition(stageX + dx, stageY + dy);
    },
    [stageX, stageY, setStagePosition]
  );

  const onEndPan = useCallback(() => {
    isPanning.current = false;
    panStart.current = null;
  }, []);

  const { onStageMouseDown, onStageMouseMove, onStageMouseUp } = useToolHandlers({
    zoom,
    stageX,
    stageY,
    onStartPan,
    onPan,
    onEndPan,
    onDrawingChange: setDrawingRect,
    onTextNodeCreated: (id) => {
      setEditingNodeId(id);
      setEditText("Text");
    },
  });

  // ── Transform event handlers (resize/rotate via custom handles) ────────────
  const selectedNodesRef = useRef<CanvasNode[]>([]);
  // Keep a fresh list of selected nodes for transform callbacks
  selectedNodesRef.current = nodes.filter((n) => selectedIds.includes(n.id));

  /** Compute snap candidates: all visible same-page nodes not in the selection. */
  const getSnapCandidates = useCallback(() => {
    const { nodes: allNodes, selectedIds: selIds } = useCanvasStore.getState();
    const pageId = usePagesStore.getState().activePageId;
    const selSet = new Set(selIds);
    return allNodes
      .filter(n => n.pageId === pageId && !selSet.has(n.id) && n.visible)
      .map(n => ({ x: n.x, y: n.y, width: n.width, height: n.height }));
  }, []);

  const handleResizeStart = useCallback(
    (handle: Parameters<typeof startResize>[0], worldX: number, worldY: number) => {
      const candidates = getSnapCandidates();
      startResize(handle, worldX, worldY, selectedNodesRef.current, candidates);
      setHovered(null);
      setTransformActive(true);
    },
    [startResize, getSnapCandidates, setHovered],
  );

  const handleRotateStart = useCallback(
    (worldX: number, worldY: number) => {
      const { nodes: allNodes } = useCanvasStore.getState();
      const candidates = getSnapCandidates();
      startRotate(worldX, worldY, selectedNodesRef.current, allNodes, candidates);
      setHovered(null);
      setTransformActive(true);
    },
    [startRotate, getSnapCandidates, setHovered],
  );

  /** Initiate a move transform (replaces Konva native drag). */
  const handleMoveStart = useCallback(
    (nodeId: string, worldX: number, worldY: number) => {
      const { nodes: allNodes, selectedIds: selIds } = useCanvasStore.getState();
      // Build list of nodes being moved: if nodeId is already in selection use the whole selection,
      // otherwise move just this one node.
      const moveIds = selIds.includes(nodeId) ? selIds : [nodeId];
      const moveNodes = allNodes.filter(n => moveIds.includes(n.id));
      if (moveNodes.length === 0) return;

      // Exclude moved nodes + their descendants from snap candidates
      const moveSet = new Set(moveIds);
      const pageId = usePagesStore.getState().activePageId;
      function addDescendants(parentId: string) {
        for (const n of allNodes) {
          if (n.parentId === parentId) {
            moveSet.add(n.id);
            addDescendants(n.id);
          }
        }
      }
      for (const id of moveIds) addDescendants(id);

      const candidates = allNodes
        .filter(n => n.pageId === pageId && !moveSet.has(n.id) && n.visible)
        .map(n => ({ x: n.x, y: n.y, width: n.width, height: n.height }));

      startMove(worldX, worldY, moveNodes, allNodes, candidates);
      setHovered(null);
      setTransformActive(true);
    },
    [startMove, setHovered],
  );

  // Wrap mouse move/up so transform continues/ends alongside tool handlers
  const onStageMouseMoveWrapped = useCallback(
    (e: Parameters<typeof onStageMouseMove>[0]) => {
      if (isTransforming()) {
        const stage = e.target.getStage();
        if (stage) {
          const pos = stage.getRelativePointerPosition();
          if (pos) continueTransform(pos.x, pos.y, e.evt.shiftKey);
        }
        return; // don't run tool handlers during transform
      }
      onStageMouseMove(e);
    },
    [onStageMouseMove, isTransforming, continueTransform],
  );

  const onStageMouseUpWrapped = useCallback(
    (e: Parameters<typeof onStageMouseUp>[0]) => {
      if (isTransforming()) {
        endTransform();
        setTransformActive(false);
        // Reset cursor
        const stage = e.target.getStage();
        if (stage) stage.container().style.cursor = "";
        return;
      }
      onStageMouseUp(e);
    },
    [onStageMouseUp, isTransforming, endTransform],
  );

  // ── Label drag handlers (HTML overlay → same transform system) ──────────────
  const handleLabelMoveUpdate = useCallback(
    (worldX: number, worldY: number, shiftKey: boolean) => {
      if (isTransforming()) continueTransform(worldX, worldY, shiftKey);
    },
    [isTransforming, continueTransform],
  );

  const handleLabelMoveEnd = useCallback(() => {
    if (isTransforming()) {
      endTransform();
      setTransformActive(false);
    }
  }, [isTransforming, endTransform]);

  // Cursor style based on tool
  const cursorMap: Record<string, string> = {
    select: "default",
    hand: isPanning.current ? "grabbing" : "grab",
    frame: "crosshair",
    shape: "crosshair",
    text: "text",
    pen: "crosshair",
    "pen-path": "crosshair",
  };

  // Sort nodes by order for rendering, filtered to active page
  const sortedNodes = [...nodes]
    .filter((n) => n.pageId === activePageId)
    .sort((a, b) => a.order - b.order);



  // Double-click to edit text
  function handleDoubleClick(node: CanvasNode) {
    if (node.type === "text") {
      setEditingNodeId(node.id);
      setEditText(node.text ?? "");
    }
  }

  function commitTextEdit() {
    if (editingNodeId) {
      const node = nodes.find((n) => n.id === editingNodeId);
      const patch: Partial<CanvasNode> = { text: editText };

      // Auto-resize if textSizing is "auto" (or unset, defaulting to auto)
      if (node && (node.textSizing ?? "auto") === "auto") {
        const measured = measureText({ ...node, text: editText });
        patch.width = measured.width;
        patch.height = measured.height;
      }

      updateNode(editingNodeId, patch);
      setEditingNodeId(null);
    }
  }

  // Compute canvas background: checkerboard transparency grid with user-configurable fill overlay.
  // ctrlKey pinch gestures zoom; two-finger scroll pans.
  const effectiveBgHex = canvasBgHex ?? CANVAS_BG_DEFAULTS[theme];
  const [r, g, b] = hexToRgbParts(effectiveBgHex);
  const fillRgba = `rgba(${r}, ${g}, ${b}, ${canvasBgAlpha})`;
  const checker = CHECKER_COLORS[theme];

  // Layer the canvas fill on top of the theme-matched checkerboard.
  // First background-image entry (top layer) = solid fill with user opacity.
  // Remaining entries = the checkerboard. When fill opacity < 1, the grid shows through.
  const bgStyle = {
    backgroundImage: [
      `linear-gradient(${fillRgba}, ${fillRgba})`,
      `linear-gradient(45deg, ${checker.tile} 25%, transparent 25%)`,
      `linear-gradient(-45deg, ${checker.tile} 25%, transparent 25%)`,
      `linear-gradient(45deg, transparent 75%, ${checker.tile} 75%)`,
      `linear-gradient(-45deg, transparent 75%, ${checker.tile} 75%)`,
    ].join(", "),
    backgroundSize: "auto, 16px 16px, 16px 16px, 16px 16px, 16px 16px",
    backgroundPosition: "0 0, 0 0, 0 8px, 8px -8px, -8px 0px",
    backgroundColor: checker.base,
  };

  return (
    <CanvasContextMenu>
    <div
      ref={containerRef}
      className="relative w-full h-full overflow-hidden focus:outline-none"
      style={{ ...bgStyle, cursor: cursorMap[activeTool] ?? "default" }}
      tabIndex={0}
    >
      <Stage
        ref={stageRef}
        width={stageSize.width}
        height={stageSize.height}
        scaleX={zoom}
        scaleY={zoom}
        x={stageX}
        y={stageY}
        onMouseDown={onStageMouseDown}
        onMouseMove={onStageMouseMoveWrapped}
        onMouseUp={onStageMouseUpWrapped}
      >
        {/* Content layer — shapes + pixel grid */}
        <Layer>
          {showGrid && (
            <PixelGrid
              stageX={stageX}
              stageY={stageY}
              zoom={zoom}
              width={stageSize.width}
              height={stageSize.height}
            />
          )}
          {sortedNodes.map((node) => (
            <CanvasNodeRenderer
              key={node.id}
              node={node}
              zoom={zoom}
              isSelected={selectedIds.includes(node.id)}
              isHovered={hoveredId === node.id}
              deepSelectActive={deepSelectActive}
              modifiers={modifiers}
              onDoubleClick={handleDoubleClick}
              onMoveStart={handleMoveStart}
              transformActive={transformActive}
              hidden={node.id === editingNodeId}
            />
          ))}
        </Layer>

        {/* Controls overlay — selection outlines, handles, hover, drawing preview */}
        <Layer>
          <SelectionOverlay
            nodes={sortedNodes}
            selectedIds={selectedIds}
            hoveredId={hoveredId}
            zoom={zoom}
            deepSelectActive={deepSelectActive}
            modifiers={modifiers}
            transformHandlesVisible={activeTool === "select" && selectedIds.length > 0}
          />
          {/* Transform handles (resize corners/edges + rotation) */}
          {activeTool === "select" && selectedIds.length > 0 && (() => {
            const bounds = getSelectionBounds(sortedNodes, selectedIds, modifiers);
            if (!bounds) return null;
            return (
              <TransformHandles
                bounds={bounds}
                zoom={zoom}
                onResizeStart={handleResizeStart}
                onRotateStart={handleRotateStart}
              />
            );
          })()}
          {/* Snap guide lines (visible during drag/resize when snapping) */}
          {snapGuides.length > 0 && (
            <SnapGuides guides={snapGuides} zoom={zoom} />
          )}
          {drawingRect && drawingRect.width > 0 && drawingRect.height > 0 && (
            <DrawingPreview rect={drawingRect} zoom={zoom} />
          )}
        </Layer>
      </Stage>

      {/* Rulers — positioned along canvas edges */}
      {showRulers && (
        <Rulers
          stageX={stageX}
          stageY={stageY}
          zoom={zoom}
          width={stageSize.width}
          height={stageSize.height}
        />
      )}

      {/* Parent object labels (name + ready-for-dev toggle) */}
      <CanvasLabels
        nodes={sortedNodes}
        zoom={zoom}
        stageX={stageX}
        stageY={stageY}
        modifiers={modifiers}
        containerEl={containerRef.current}
        onMoveStart={handleMoveStart}
        onMoveUpdate={handleLabelMoveUpdate}
        onMoveEnd={handleLabelMoveEnd}
      />

      {/* Text edit overlay — positioned in screen space */}
      {editingNodeId && (() => {
        const node = nodes.find((n) => n.id === editingNodeId);
        if (!node) return null;
        const isAutoSizing = (node.textSizing ?? "auto") === "auto";
        // For auto-sized text, measure live text to expand textarea
        let screenW: number;
        let screenH: number;
        if (isAutoSizing) {
          const measured = measureText({ ...node, text: editText });
          screenW = measured.width * zoom;
          screenH = measured.height * zoom;
        } else {
          screenW = node.width * zoom;
          screenH = node.height * zoom;
        }
        const screenX = node.x * zoom + stageX;
        const screenY = node.y * zoom + stageY;
        return (
          <textarea
            autoFocus
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            onFocus={(e) => e.target.select()}
            onBlur={commitTextEdit}
            onKeyDown={(e) => {
              if (e.key === "Escape") { commitTextEdit(); }
              if (e.key === "Enter" && !e.shiftKey) { commitTextEdit(); }
            }}
            style={{
              position: "absolute",
              left: screenX,
              top: screenY,
              width: Math.max(screenW, 60),
              height: Math.max(screenH, 20),
              fontSize: (node.fontSize ?? 16) * zoom,
              fontFamily: node.fontFamily ? `"${node.fontFamily}", sans-serif` : "sans-serif",
              fontWeight: node.fontWeight ?? 400,
              fontStyle: node.fontStyle ?? "normal",
              lineHeight: node.lineHeight ?? 1.2,
              letterSpacing: `${(node.letterSpacing ?? 0) * zoom}px`,
              textAlign: node.textAlign ?? "left",
              textDecoration: node.textDecoration === "none" ? "none" : (node.textDecoration ?? "none"),
              textTransform: (node.textTransform ?? "none") as React.CSSProperties["textTransform"],
              color: node.textColor ?? "#000",
              background: "transparent",
              border: "1px solid #6366f1",
              outline: "none",
              resize: "none",
              padding: 0,
              zIndex: 50,
              boxSizing: "border-box",
              transform: node.rotation ? `rotate(${node.rotation}deg)` : undefined,
              transformOrigin: "0 0",
            }}
          />
        );
      })()}
    </div>
    </CanvasContextMenu>
  );
}
