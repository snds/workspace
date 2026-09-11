import { useState, useRef, useEffect, useCallback } from "react";
import { useCanvasStore } from "@/stores/canvas.store";
import type { CanvasNode } from "@/types/canvas";
import type { TransformModifiers } from "@/stores/canvas.store";

const LABEL_HEIGHT = 18;
const LABEL_GAP = 4; // px above the frame
const DRAG_THRESHOLD = 3; // px before initiating drag

interface CanvasLabelsProps {
  nodes: CanvasNode[];
  zoom: number;
  stageX: number;
  stageY: number;
  modifiers: TransformModifiers | null;
  /** Container element for screen→world coordinate conversion */
  containerEl: HTMLDivElement | null;
  /** Initiate a move transform (same as clicking a canvas object) */
  onMoveStart: (nodeId: string, worldX: number, worldY: number) => void;
  /** Continue an in-progress transform */
  onMoveUpdate: (worldX: number, worldY: number, shiftKey: boolean) => void;
  /** End an in-progress transform */
  onMoveEnd: () => void;
}

/**
 * HTML overlay labels rendered above parent objects (frames/groups with children)
 * on the canvas. For frames, also shows a "ready for dev" toggle icon.
 */
export function CanvasLabels({
  nodes, zoom, stageX, stageY, modifiers,
  containerEl, onMoveStart, onMoveUpdate, onMoveEnd,
}: CanvasLabelsProps) {
  const { updateNode, hoveredId, setHovered, selectedIds, selectNodes } = useCanvasStore();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const isDraggingRef = useRef(false);

  // Focus input when editing starts
  useEffect(() => {
    if (editingId && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [editingId]);

  const commitRename = useCallback(() => {
    if (editingId && editValue.trim()) {
      updateNode(editingId, { name: editValue.trim() });
    }
    setEditingId(null);
  }, [editingId, editValue, updateNode]);

  /** Convert screen (client) coordinates to canvas world coordinates */
  const screenToWorld = useCallback((clientX: number, clientY: number) => {
    const rect = containerEl?.getBoundingClientRect();
    const offsetX = rect ? clientX - rect.left : clientX;
    const offsetY = rect ? clientY - rect.top : clientY;
    return {
      x: (offsetX - stageX) / zoom,
      y: (offsetY - stageY) / zoom,
    };
  }, [containerEl, stageX, stageY, zoom]);

  /** Mousedown on label: select + prepare for drag */
  const handleLabelMouseDown = useCallback((nodeId: string, e: React.MouseEvent) => {
    if (e.button !== 0) return;
    // Don't interfere with button clicks or input
    if ((e.target as HTMLElement).closest("button, input")) return;

    e.preventDefault();
    const startX = e.clientX;
    const startY = e.clientY;
    let didDrag = false;
    isDraggingRef.current = false;

    const onMove = (ev: MouseEvent) => {
      const dx = ev.clientX - startX;
      const dy = ev.clientY - startY;

      if (!didDrag && Math.abs(dx) + Math.abs(dy) < DRAG_THRESHOLD) return;

      if (!didDrag) {
        // First move past threshold — initiate the transform
        didDrag = true;
        isDraggingRef.current = true;
        selectNodes([nodeId], false);
        const world = screenToWorld(startX, startY);
        onMoveStart(nodeId, world.x, world.y);
      }

      const world = screenToWorld(ev.clientX, ev.clientY);
      onMoveUpdate(world.x, world.y, ev.shiftKey);
    };

    const onUp = () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);

      if (didDrag) {
        onMoveEnd();
        isDraggingRef.current = false;
      }
    };

    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
  }, [selectNodes, screenToWorld, onMoveStart, onMoveUpdate, onMoveEnd]);

  // Top-level parent nodes: no parentId themselves, and have at least one child
  const parentIds = new Set<string>();
  for (const n of nodes) {
    if (n.parentId) parentIds.add(n.parentId);
  }

  const parentNodes = nodes.filter((n) => n.parentId === null && parentIds.has(n.id) && n.visible);

  if (parentNodes.length === 0) return null;

  return (
    <>
      {parentNodes.map((node) => {
        const mod = modifiers?.[node.id];
        const nx = mod?.x ?? node.x;
        const ny = mod?.y ?? node.y;

        // Position in screen space (above the node's top-left corner)
        const screenX = nx * zoom + stageX;
        const screenY = ny * zoom + stageY - LABEL_HEIGHT - LABEL_GAP;

        const mw = mod?.width ?? node.width;
        const screenW = mw * zoom;

        const isSelected = selectedIds.includes(node.id);
        const isHovered = hoveredId === node.id;
        const isEditing = editingId === node.id;

        return (
          <div
            key={`label-${node.id}`}
            onMouseEnter={() => setHovered(node.id)}
            onMouseLeave={() => setHovered(null)}
            onMouseDown={(e) => {
              if (!isEditing) handleLabelMouseDown(node.id, e);
            }}
            onClick={() => {
              // Select on click (only if we didn't just drag)
              if (!isEditing && !isDraggingRef.current) selectNodes([node.id], false);
            }}
            style={{
              position: "absolute",
              left: screenX,
              top: screenY,
              width: screenW,
              height: LABEL_HEIGHT,
              pointerEvents: "auto",
              zIndex: 10,
              cursor: isEditing ? "text" : "default",
              transform: node.rotation && !mod ? `rotate(${node.rotation}deg)` : undefined,
              transformOrigin: `0 ${LABEL_HEIGHT + LABEL_GAP}px`,
            }}
            className="flex items-center justify-between"
          >
            {/* Object name — inline rename on double-click */}
            {isEditing ? (
              <input
                ref={inputRef}
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                onBlur={commitRename}
                onKeyDown={(e) => {
                  if (e.key === "Enter") commitRename();
                  if (e.key === "Escape") setEditingId(null);
                }}
                onClick={(e) => e.stopPropagation()}
                className="text-[10px] leading-none font-medium text-[var(--violet-11)] bg-[var(--mauve-2)] border border-[var(--violet-7)] rounded px-1 outline-none h-[16px] min-w-[40px] max-w-full"
              />
            ) : (
              <span
                onDoubleClick={() => {
                  setEditingId(node.id);
                  setEditValue(node.name);
                }}
                className={`text-[10px] leading-none font-medium whitespace-nowrap select-none truncate transition-colors cursor-default ${
                  isSelected
                    ? "text-[var(--violet-11)]"
                    : isHovered
                      ? "text-[var(--violet-9)]"
                      : "text-[var(--mauve-9)]"
                }`}
              >
                {node.name}
              </span>
            )}

            {/* Ready for dev toggle (frames only) */}
            {node.type === "frame" && !isEditing && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  updateNode(node.id, { readyForDev: !node.readyForDev });
                }}
                title={node.readyForDev ? "Marked ready for dev" : "Mark as ready for dev"}
                className={`flex items-center justify-center w-[18px] h-[18px] rounded border flex-shrink-0 transition-colors ${
                  node.readyForDev
                    ? "border-[#22c55e] bg-[#14532d] text-[#4ade80] hover:bg-[#166534] hover:text-[#86efac] active:bg-[#15803d]"
                    : "border-[var(--mauve-6)] bg-[var(--mauve-3)] text-[var(--mauve-9)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)] hover:border-[var(--mauve-7)] active:bg-[var(--mauve-5)]"
                }`}
              >
                <svg viewBox="0 0 14 14" fill="none" width="10" height="10" xmlns="http://www.w3.org/2000/svg">
                  <polyline
                    points="2,4.5 5.5,7.5 2,10.5"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    fill="none"
                  />
                  <line
                    x1="7"
                    y1="10.5"
                    x2="12"
                    y2="10.5"
                    stroke="currentColor"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                  />
                </svg>
              </button>
            )}
          </div>
        );
      })}
    </>
  );
}
