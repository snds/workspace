import { Rect } from "react-konva";
import type { CanvasNode } from "@/types/canvas";
import type { TransformModifiers } from "@/stores/canvas.store";

const ACCENT = "#6366f1";

interface SelectionOverlayProps {
  nodes: CanvasNode[];
  selectedIds: string[];
  hoveredId: string | null;
  zoom: number;
  deepSelectActive: boolean;
  /** Active transform modifiers for live preview bounds */
  modifiers: TransformModifiers | null;
  /** When true, TransformHandles is rendering — skip selected outlines to avoid duplication */
  transformHandlesVisible?: boolean;
}

/**
 * Renders selection and hover outlines on the controls overlay layer.
 *
 * - Selection: violet outline on each selected node (only when transform handles
 *   are NOT visible, e.g. when a non-select tool is active).
 * - Hover: violet outline on the hovered non-selected node (solid for
 *   root, dashed for child nodes in deep-select mode).
 *
 * All elements are non-listening so pointer events pass through to the
 * shape layer or transform handles below.
 */
export function SelectionOverlay({
  nodes,
  selectedIds,
  hoveredId,
  zoom,
  deepSelectActive,
  modifiers,
  transformHandlesVisible = false,
}: SelectionOverlayProps) {
  const strokeW = 1 / zoom;

  // ── Selection outlines (only when TransformHandles is NOT rendering) ────────
  const selectedNodes = transformHandlesVisible
    ? []
    : selectedIds
        .map((id) => nodes.find((n) => n.id === id))
        .filter(Boolean) as CanvasNode[];

  // ── Hover outline (non-selected only) ──────────────────────────────────────
  const hoveredNode =
    hoveredId && !selectedIds.includes(hoveredId)
      ? nodes.find((n) => n.id === hoveredId)
      : null;

  const isChild = hoveredNode?.parentId !== null;
  const isDashed = hoveredNode && isChild && deepSelectActive;
  const hMod = hoveredNode ? modifiers?.[hoveredNode.id] : undefined;

  return (
    <>
      {/* Individual selection outlines (fallback when no transform handles) */}
      {selectedNodes.map((node) => {
        const mod = modifiers?.[node.id];
        return (
          <Rect
            key={`sel-${node.id}`}
            x={mod?.x ?? node.x}
            y={mod?.y ?? node.y}
            width={mod?.width ?? node.width}
            height={mod?.height ?? node.height}
            rotation={mod?.rotation ?? node.rotation}
            stroke={ACCENT}
            strokeWidth={strokeW}
            fill="transparent"
            listening={false}
          />
        );
      })}

      {/* Hover outline — uses modifiers for live-preview position during transforms */}
      {hoveredNode && (
        <Rect
          x={(hMod?.x ?? hoveredNode.x) as number}
          y={(hMod?.y ?? hoveredNode.y) as number}
          width={(hMod?.width ?? hoveredNode.width) as number}
          height={(hMod?.height ?? hoveredNode.height) as number}
          rotation={(hMod?.rotation ?? hoveredNode.rotation) as number}
          stroke={ACCENT}
          strokeWidth={strokeW}
          dash={isDashed ? [4 / zoom, 4 / zoom] : undefined}
          fill="transparent"
          listening={false}
        />
      )}
    </>
  );
}
