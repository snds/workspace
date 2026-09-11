import React from "react";
import { useComponentCatalogStore } from "@/stores/componentCatalog.store";
import { blueprintToNodeSpec } from "@/core/components/toIRNodes";
import type { IRNode } from "@/core/ir/types";

interface ComponentInstanceRendererProps {
  node: IRNode;
}

/**
 * Renders a component-instance IRNode by looking up its blueprint
 * from the catalog and rendering the canvas template.
 */
export const ComponentInstanceRenderer: React.FC<ComponentInstanceRendererProps> =
  React.memo(({ node }) => {
    const getBlueprint = useComponentCatalogStore((s) => s.getBlueprint);

    if (!node.componentRef) return null;

    const blueprint = getBlueprint(node.componentRef.catalogId);
    if (!blueprint) return null;

    // The spec gives us a tree of NodeSpecs that can be rendered.
    // Kept here for future use when we convert NodeSpec -> Konva shapes.
    void blueprintToNodeSpec(blueprint, node.componentRef.variant);

    // For now, return null -- this will integrate with the canvas renderer
    // when we convert NodeSpec -> Konva shapes.
    return null;
  });

ComponentInstanceRenderer.displayName = "ComponentInstanceRenderer";
