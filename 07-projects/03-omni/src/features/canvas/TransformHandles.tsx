import { Group, Rect, Circle } from "react-konva";
import type { KonvaEventObject } from "konva/lib/Node";
import type { CanvasNode } from "@/types/canvas";
import type { HandlePosition } from "./useTransform";
import { getCursor, getRotationCursor } from "@/lib/cursors";

const ACCENT = "#6366f1";

// ─── Types ─────────────────────────────────────────────────────────────────────

export interface SelectionBounds {
  x: number;
  y: number;
  width: number;
  height: number;
  rotation: number;
}

interface TransformHandlesProps {
  bounds: SelectionBounds;
  zoom: number;
  onResizeStart: (handle: HandlePosition, worldX: number, worldY: number) => void;
  onRotateStart: (worldX: number, worldY: number) => void;
}

// ─── Base angle for each handle position (used for cursor rotation) ───────────

const HANDLE_BASE_ANGLE: Record<HandlePosition, number> = {
  "top":          0,
  "top-right":    45,
  "right":        90,
  "bottom-right": 135,
  "bottom":       180,
  "bottom-left":  225,
  "left":         270,
  "top-left":     315,
};

// ─── Component ────────────────────────────────────────────────────────────────

export function TransformHandles({
  bounds,
  zoom,
  onResizeStart,
  onRotateStart,
}: TransformHandlesProps) {
  const { x, y, width, height, rotation } = bounds;

  // Sizes scaled inversely with zoom so handles stay visually consistent
  const cornerR = 4 / zoom;         // visible corner circle radius
  const hitR = 10 / zoom;           // invisible hit area radius for corners
  const edgeHit = 8 / zoom;         // invisible edge handle thickness
  const rotHit = 20 / zoom;         // rotation handle hit area size
  const rotOffset = 4 / zoom;       // gap between bbox and rotation handle
  const strokeW = 1 / zoom;

  // Adaptive: hide edge handles on very small shapes
  const tooSmallForEdges = width < 25 / zoom || height < 25 / zoom;

  // ── Pointer handlers ────────────────────────────────────────────────────────

  function handleResizePointerDown(handle: HandlePosition) {
    return (e: KonvaEventObject<MouseEvent>) => {
      e.cancelBubble = true;
      const stage = e.target.getStage();
      if (!stage) return;
      const pos = stage.getRelativePointerPosition();
      if (!pos) return;
      onResizeStart(handle, pos.x, pos.y);

      const container = stage.container();
      container.style.cursor = getCursor("resize", HANDLE_BASE_ANGLE[handle] + rotation);
    };
  }

  function handleRotatePointerDown(e: KonvaEventObject<MouseEvent>) {
    e.cancelBubble = true;
    const stage = e.target.getStage();
    if (!stage) return;
    const pos = stage.getRelativePointerPosition();
    if (!pos) return;
    onRotateStart(pos.x, pos.y);

    const container = stage.container();
    container.style.cursor = getRotationCursor(rotation);
  }

  // ── Positions relative to (0, 0) — rotated Group handles the transform ─────

  const corners: { pos: HandlePosition; cx: number; cy: number }[] = [
    { pos: "top-left",     cx: 0,     cy: 0 },
    { pos: "top-right",    cx: width, cy: 0 },
    { pos: "bottom-left",  cx: 0,     cy: height },
    { pos: "bottom-right", cx: width, cy: height },
  ];

  const edges: { pos: HandlePosition; rx: number; ry: number; rw: number; rh: number }[] = tooSmallForEdges
    ? []
    : [
        { pos: "top",    rx: cornerR * 2,         ry: -edgeHit / 2,          rw: width - cornerR * 4,  rh: edgeHit },
        { pos: "bottom", rx: cornerR * 2,         ry: height - edgeHit / 2,  rw: width - cornerR * 4,  rh: edgeHit },
        { pos: "left",   rx: -edgeHit / 2,        ry: cornerR * 2,           rw: edgeHit,              rh: height - cornerR * 4 },
        { pos: "right",  rx: width - edgeHit / 2, ry: cornerR * 2,           rw: edgeHit,              rh: height - cornerR * 4 },
      ];

  // Rotation handles: invisible rects at corners, outside bbox
  const rotCorners: { pos: HandlePosition; cx: number; cy: number }[] = [
    { pos: "top-left",     cx: 0,     cy: 0 },
    { pos: "top-right",    cx: width, cy: 0 },
    { pos: "bottom-left",  cx: 0,     cy: height },
    { pos: "bottom-right", cx: width, cy: height },
  ];

  const rotHandles = rotCorners.map(({ pos, cx, cy }) => {
    const ox = pos.includes("left") ? cx - rotHit - rotOffset : cx + rotOffset;
    const oy = pos.includes("top") ? cy - rotHit - rotOffset : cy + rotOffset;
    const baseAngle = HANDLE_BASE_ANGLE[pos];
    return { key: `rot-${pos}`, ox, oy, baseAngle };
  });

  return (
    <Group x={x} y={y} rotation={rotation}>
      {/* Bounding box outline */}
      <Rect
        x={0}
        y={0}
        width={width}
        height={height}
        stroke={ACCENT}
        strokeWidth={strokeW}
        fill="transparent"
        listening={false}
      />

      {/* Rotation handles (invisible, outside corners) */}
      {rotHandles.map((rh) => (
        <Rect
          key={rh.key}
          x={rh.ox}
          y={rh.oy}
          width={rotHit}
          height={rotHit}
          fill="transparent"
          listening={true}
          onMouseDown={handleRotatePointerDown}
          onMouseEnter={(e) => {
            const stage = e.target.getStage();
            if (stage) stage.container().style.cursor = getRotationCursor(rh.baseAngle + rotation);
          }}
          onMouseLeave={(e) => {
            const stage = e.target.getStage();
            if (stage) stage.container().style.cursor = "";
          }}
        />
      ))}

      {/* Edge resize handles (invisible rects) */}
      {edges.map((edge) => (
        <Rect
          key={`edge-${edge.pos}`}
          x={edge.rx}
          y={edge.ry}
          width={edge.rw}
          height={edge.rh}
          fill="transparent"
          listening={true}
          onMouseDown={handleResizePointerDown(edge.pos)}
          onMouseEnter={(e) => {
            const stage = e.target.getStage();
            if (stage) stage.container().style.cursor = getCursor("resize", HANDLE_BASE_ANGLE[edge.pos] + rotation);
          }}
          onMouseLeave={(e) => {
            const stage = e.target.getStage();
            if (stage) stage.container().style.cursor = "";
          }}
        />
      ))}

      {/* Corner resize handles (visible circles + invisible hit areas) */}
      {corners.map(({ pos, cx, cy }) => (
        <Circle
          key={`corner-${pos}`}
          x={cx}
          y={cy}
          radius={hitR}
          fill="transparent"
          listening={true}
          onMouseDown={handleResizePointerDown(pos)}
          onMouseEnter={(e) => {
            const stage = e.target.getStage();
            if (stage) stage.container().style.cursor = getCursor("resize", HANDLE_BASE_ANGLE[pos] + rotation);
          }}
          onMouseLeave={(e) => {
            const stage = e.target.getStage();
            if (stage) stage.container().style.cursor = "";
          }}
        />
      ))}

      {/* Visible corner dots (non-listening, purely visual) */}
      {corners.map(({ pos, cx, cy }) => (
        <Circle
          key={`dot-${pos}`}
          x={cx}
          y={cy}
          radius={cornerR}
          fill="#ffffff"
          stroke={ACCENT}
          strokeWidth={strokeW}
          listening={false}
        />
      ))}
    </Group>
  );
}

// ─── Utility: compute combined bounds from selected nodes ─────────────────────

export function getSelectionBounds(
  nodes: CanvasNode[],
  selectedIds: string[],
  modifiers: Record<string, Partial<CanvasNode>> | null,
): SelectionBounds | null {
  if (selectedIds.length === 0) return null;

  const selectedNodes: CanvasNode[] = [];
  for (const id of selectedIds) {
    const node = nodes.find((n) => n.id === id);
    if (node) selectedNodes.push(node);
  }
  if (selectedNodes.length === 0) return null;

  // Single selection: use the node's own bounds + rotation
  if (selectedNodes.length === 1) {
    const node = selectedNodes[0];
    const mod = modifiers?.[node.id];
    return {
      x: mod?.x ?? node.x,
      y: mod?.y ?? node.y,
      width: mod?.width ?? node.width,
      height: mod?.height ?? node.height,
      rotation: mod?.rotation ?? node.rotation,
    };
  }

  // Multi-selection: axis-aligned bounding box, no rotation
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;

  for (const node of selectedNodes) {
    const mod = modifiers?.[node.id];
    const nx = mod?.x ?? node.x;
    const ny = mod?.y ?? node.y;
    const nw = mod?.width ?? node.width;
    const nh = mod?.height ?? node.height;

    minX = Math.min(minX, nx);
    minY = Math.min(minY, ny);
    maxX = Math.max(maxX, nx + nw);
    maxY = Math.max(maxY, ny + nh);
  }

  return { x: minX, y: minY, width: maxX - minX, height: maxY - minY, rotation: 0 };
}
