import React from "react";
import { useIconRegistryStore } from "@/stores/iconRegistry.store";
import { useTokenResolver } from "./useTokenResolver";
import type { IRNode } from "@/core/ir/types";

interface IconNodeRendererProps {
  node: IRNode;
}

/**
 * Renders an icon IRNode on the canvas.
 * Resolves the semantic icon name via the registry and renders the SVG.
 */
export const IconNodeRenderer: React.FC<IconNodeRendererProps> = React.memo(
  ({ node }) => {
    const registry = useIconRegistryStore((s) => s.registry);
    const { resolveColor, resolveNumber } = useTokenResolver();

    if (!node.iconRef) return null;

    const iconData = registry.resolve(node.iconRef.name);
    if (!iconData) return null;

    const size = node.iconRef.size ? resolveNumber(node.iconRef.size, 16) : 16;
    const color = node.iconRef.color
      ? resolveColor(node.iconRef.color)
      : "#ffffff";

    // Computed values will be used when rendering as a Konva Group with SVG path.
    void size;
    void color;

    // For now, return null -- will render as a Konva Group with SVG path
    // when we integrate with the canvas renderer.
    return null;
  },
);

IconNodeRenderer.displayName = "IconNodeRenderer";
