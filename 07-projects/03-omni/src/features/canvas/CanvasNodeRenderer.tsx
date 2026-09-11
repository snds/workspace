import { Rect, Text } from "react-konva";
import type { KonvaEventObject } from "konva/lib/Node";
import type { CanvasNode } from "@/types/canvas";
import { useCanvasStore, type TransformModifiers } from "@/stores/canvas.store";
import { useUIStore } from "@/stores/ui.store";

// ─── Helpers ──────────────────────────────────────────────────────────────────

/** Walk up parentId chain to find the topmost ancestor of nodeId. */
function getRootAncestorId(nodeId: string, allNodes: CanvasNode[]): string {
  const node = allNodes.find((n) => n.id === nodeId);
  if (!node || !node.parentId) return nodeId;
  return getRootAncestorId(node.parentId, allNodes);
}

// ─── Typography helpers ───────────────────────────────────────────────────────

function buildKonvaFontStyle(
  weight: number = 400,
  style: "normal" | "italic" = "normal",
): string {
  const parts: string[] = [];
  if (style === "italic") parts.push("italic");
  if (weight === 700) parts.push("bold");
  else if (weight !== 400) parts.push(String(weight));
  return parts.join(" ") || "normal";
}

function applyTextTransform(text: string, transform?: string): string {
  switch (transform) {
    case "uppercase":  return text.toUpperCase();
    case "lowercase":  return text.toLowerCase();
    case "capitalize": return text.replace(/\b\w/g, (c) => c.toUpperCase());
    default:           return text;
  }
}

function resolveFill(hex: string | null | undefined, fillOpacity: number = 1): string | undefined {
  if (!hex) return undefined;
  if (fillOpacity >= 1) return hex;
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${fillOpacity})`;
}

// ─── Component ────────────────────────────────────────────────────────────────

interface CanvasNodeRendererProps {
  node: CanvasNode;
  zoom: number;
  isSelected: boolean;
  isHovered: boolean;
  /**
   * When true (Cmd/Ctrl held), children inside frames are directly
   * selectable and draggable (Figma-style deep-select).
   */
  deepSelectActive?: boolean;
  /** Active transform modifiers for live preview */
  modifiers?: TransformModifiers | null;
  onDoubleClick?: (node: CanvasNode) => void;
  /** Called on mousedown to initiate a move transform */
  onMoveStart?: (nodeId: string, worldX: number, worldY: number) => void;
  /** When true, a transform (move/resize/rotate) is in progress — suppress hover events */
  transformActive?: boolean;
  /** When true, hide this node (e.g. while editing text inline) */
  hidden?: boolean;
}

export function CanvasNodeRenderer({
  node,
  deepSelectActive = false,
  modifiers,
  onDoubleClick,
  onMoveStart,
  transformActive = false,
  hidden = false,
}: CanvasNodeRendererProps) {
  const { selectNodes, setHovered } = useCanvasStore();
  const { activeTool } = useUIStore();

  if (!node.visible || hidden) return null;

  const isChild = node.parentId !== null;
  const isMovable = activeTool === "select" && !node.locked && (!isChild || deepSelectActive);

  // ── MouseDown: select + initiate move ─────────────────────────────────────
  function handleMouseDown(e: KonvaEventObject<MouseEvent>) {
    if (activeTool !== "select") return;
    e.cancelBubble = true;

    // Select the node (deep-select vs root-ancestor)
    if (isChild && !deepSelectActive) {
      const { nodes: allNodes } = useCanvasStore.getState();
      const rootId = getRootAncestorId(node.id, allNodes);
      selectNodes([rootId], e.evt.shiftKey);
      // Initiate move on the root ancestor
      if (onMoveStart && !e.evt.shiftKey) {
        const stage = e.target.getStage();
        if (stage) {
          const pos = stage.getRelativePointerPosition();
          if (pos) onMoveStart(rootId, pos.x, pos.y);
        }
      }
      return;
    }

    selectNodes([node.id], e.evt.shiftKey);

    // Initiate move
    if (isMovable && onMoveStart && !e.evt.shiftKey) {
      const stage = e.target.getStage();
      if (stage) {
        const pos = stage.getRelativePointerPosition();
        if (pos) onMoveStart(node.id, pos.x, pos.y);
      }
    }
  }

  // ── Hover: show parent frame outline when child hovered without modifier ─────
  function handleMouseEnter() {
    if (transformActive) return; // suppress hover during drag/resize/rotate
    if (isChild && !deepSelectActive) {
      setHovered(node.parentId ?? null);
    } else {
      setHovered(node.id);
    }
  }

  const flipX = node.flipX ?? false;
  const flipY = node.flipY ?? false;

  // Merge active transform modifiers for live preview during resize/rotate/move
  const mod = modifiers?.[node.id];
  const mx = mod?.x ?? node.x;
  const my = mod?.y ?? node.y;
  const mw = mod?.width ?? node.width;
  const mh = mod?.height ?? node.height;
  const mr = mod?.rotation ?? node.rotation;

  const commonProps = {
    id: node.id,
    x: mx + (flipX ? mw : 0),
    y: my + (flipY ? mh : 0),
    scaleX: flipX ? -1 : 1,
    scaleY: flipY ? -1 : 1,
    width: mw,
    height: mh,
    rotation: mr,
    opacity: node.opacity,
    onMouseDown: handleMouseDown,
    onMouseEnter: handleMouseEnter,
    onMouseLeave: () => { if (!transformActive) setHovered(null); },
  };

  // ── Text node ───────────────────────────────────────────────────────────────
  if (node.type === "text") {
    const displayText = applyTextTransform(node.text ?? "Text", node.textTransform);
    const konvaFontStyle = buildKonvaFontStyle(node.fontWeight, node.fontStyle);
    const konvaTextDecoration =
      node.textDecoration === "underline" ? "underline" :
      node.textDecoration === "line-through" ? "line-through" : "";

    return (
      <Text
        {...commonProps}
        text={displayText}
        fontSize={node.fontSize ?? 16}
        fontFamily={node.fontFamily ?? "Inter"}
        fontStyle={konvaFontStyle}
        align={node.textAlign ?? "left"}
        verticalAlign={node.verticalAlign ?? "top"}
        fill={node.textColor ?? "#000000"}
        lineHeight={node.lineHeight ?? 1.2}
        letterSpacing={node.letterSpacing ?? 0}
        textDecoration={konvaTextDecoration}
        onDblClick={() => onDoubleClick?.(node)}
      />
    );
  }

  // ── Shadow from effects ──────────────────────────────────────────────────────
  const activeShadow = node.effects?.find(
    (e) => e.visible && (e.type === "DROP_SHADOW" || e.type === "INNER_SHADOW")
  );
  const shadowProps = activeShadow
    ? {
        shadowEnabled: true,
        shadowColor: activeShadow.color ?? "#000000",
        shadowOffsetX: activeShadow.offsetX ?? 0,
        shadowOffsetY: activeShadow.offsetY ?? 2,
        shadowBlur: activeShadow.blur ?? 4,
        shadowOpacity: 1,
      }
    : { shadowEnabled: false };

  // ── Rectangle / Frame ───────────────────────────────────────────────────────
  const resolvedFill = resolveFill(node.fill, node.fillOpacity);
  return (
    <Rect
      {...commonProps}
      fill={resolvedFill}
      stroke={node.stroke ?? undefined}
      strokeWidth={node.strokeWidth}
      cornerRadius={node.cornerRadius}
      {...shadowProps}
    />
  );
}
