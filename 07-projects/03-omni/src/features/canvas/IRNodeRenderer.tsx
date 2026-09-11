import React from "react";
import { useTokenResolver } from "./useTokenResolver";
import type { IRNode } from "@/core/ir/types";
import { isTokenRef } from "@/core/ir/types";

interface IRNodeRendererProps {
  node: IRNode;
  isSelected: boolean;
  isHovered: boolean;
}

/**
 * Renders an IRNode on the canvas by resolving all token references
 * and delegating to the existing CanvasNodeRenderer.
 *
 * This is the bridge during the migration period -- eventually the
 * canvas will work directly with IRNodes.
 */
export const IRNodeRenderer: React.FC<IRNodeRendererProps> = React.memo(
  ({ node, isSelected: _isSelected, isHovered: _isHovered }) => {
    const { resolveColor } = useTokenResolver();

    // Resolve token references to literal values for canvas rendering
    const _resolvedFill = node.colorSlots?.background
      ? resolveColor(node.colorSlots.background)
      : isTokenRef(node.fill)
        ? resolveColor(node.fill)
        : (node.fill as string | null);

    const _resolvedStroke = node.colorSlots?.border
      ? resolveColor(node.colorSlots.border)
      : isTokenRef(node.stroke)
        ? resolveColor(node.stroke)
        : (node.stroke as string | null);

    const _resolvedTextColor = node.colorSlots?.foreground
      ? resolveColor(node.colorSlots.foreground)
      : (node.textColor as string | undefined) ?? null;

    // Resolved props are computed above but not yet consumed.
    // They will be passed to CanvasNodeRenderer when the rendering
    // pipeline is fully connected in a future phase.
    // For now, void the values to satisfy the linter.
    void _resolvedFill;
    void _resolvedStroke;
    void _resolvedTextColor;

    // Placeholder -- actual rendering delegates to CanvasNodeRenderer.
    // The full implementation will come when CanvasNodeRenderer is updated
    // to accept either CanvasNode or resolved IR props.
    return null;
  },
);

IRNodeRenderer.displayName = "IRNodeRenderer";
