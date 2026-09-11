import { useCanvasStore } from "@/stores/canvas.store";
import { useTokensStore } from "@/stores/tokens.store";
import { canvasNodeToIR, irNodeToCanvasNode, TokenResolver } from "@/core/ir";
import type { IRNode, TokenRef } from "@/core/ir/types";
import type { CanvasNode } from "@/types/canvas";

/**
 * IR selectors and actions that wrap the canvas store.
 * During the migration period, the canvas store still holds CanvasNode[].
 * This module provides an IR view on top of it.
 */

/** Convert a CanvasNode to an IRNode (read path) */
export function toIR(node: CanvasNode): IRNode {
  return canvasNodeToIR(node);
}

/** Convert an IRNode back to a CanvasNode (write path) */
export function fromIR(irNode: IRNode): CanvasNode {
  const entries = useTokensStore.getState().entries;
  const resolver = new TokenResolver();

  const resolve = (ref: TokenRef): unknown => {
    return resolver.resolve(ref, entries);
  };

  return irNodeToCanvasNode(irNode, resolve);
}

/** Get all canvas nodes as IRNodes */
export function getIRNodes(): IRNode[] {
  return useCanvasStore.getState().nodes.map(toIR);
}

/** Get selected nodes as IRNodes */
export function getSelectedIRNodes(): IRNode[] {
  const state = useCanvasStore.getState();
  const selectedSet = new Set(state.selectedIds);
  return state.nodes.filter((n) => selectedSet.has(n.id)).map(toIR);
}

/** Get a single node as IRNode by ID */
export function getIRNode(id: string): IRNode | undefined {
  const node = useCanvasStore.getState().nodes.find((n) => n.id === id);
  return node ? toIR(node) : undefined;
}

/** Add a node from an IRNode (converts to CanvasNode for storage) */
export function addIRNode(
  irNode: Omit<IRNode, "id" | "order">,
): string {
  const entries = useTokensStore.getState().entries;
  const resolver = new TokenResolver();
  const resolve = (ref: TokenRef): unknown => resolver.resolve(ref, entries);

  const canvasNode = irNodeToCanvasNode(irNode as IRNode, resolve);
  const { id: _id, order: _order, ...rest } = canvasNode;

  return useCanvasStore.getState().addNode(rest as Parameters<typeof useCanvasStore.getState>["addNode" extends keyof ReturnType<typeof useCanvasStore.getState> ? never : never][0]);
}

/** Update a node using IR-level patches (resolves tokens before applying) */
export function updateIRNode(id: string, patch: Partial<IRNode>): void {
  const entries = useTokensStore.getState().entries;
  const resolver = new TokenResolver();

  const resolvedPatch: Partial<CanvasNode> = {};

  for (const [key, value] of Object.entries(patch)) {
    if (value !== undefined && typeof value === "object" && value !== null && "$ref" in value) {
      const resolved = resolver.resolve(value as TokenRef, entries);
      (resolvedPatch as Record<string, unknown>)[key] = resolved;
    } else {
      (resolvedPatch as Record<string, unknown>)[key] = value;
    }
  }

  useCanvasStore.getState().updateNode(id, resolvedPatch);
}
