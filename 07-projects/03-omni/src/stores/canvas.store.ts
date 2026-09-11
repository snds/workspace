import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import { current } from "immer";
import { nanoid } from "nanoid";
import type { CanvasNode, NodeType } from "@/types/canvas";
import type { SnapResult } from "@/features/canvas/snap/snapEngine";
import { usePagesStore } from "@/stores/pages.store";
import { measureText } from "@/lib/measureText";

interface HistoryEntry {
  nodes: CanvasNode[];
  selectedIds: string[];
}

/** Temporary visual overrides applied during interactive transforms (resize/rotate/move).
 *  Committed to nodes on pointer-up via applyModifiers(). */
export type TransformModifiers = Record<string, Partial<CanvasNode>>;

interface CanvasState {
  nodes: CanvasNode[];
  selectedIds: string[];
  hoveredId: string | null;
  stageX: number;
  stageY: number;
  historyPast: HistoryEntry[];
  historyFuture: HistoryEntry[];
  /** Active transform preview — null when no transform in progress */
  modifiers: TransformModifiers | null;
  /** Active snap guide lines (cleared when transform ends) */
  snapGuides: SnapResult[];
  /** Clipboard for copy/paste operations */
  clipboard: CanvasNode[];
}

interface CanvasActions {
  addNode(
    node: Pick<CanvasNode, "type" | "name" | "x" | "y" | "width" | "height" | "parentId"> &
      Partial<Omit<CanvasNode, "id" | "order">>
  ): string;
  updateNode(id: string, patch: Partial<CanvasNode>): void;
  updateNodes(patches: Array<{ id: string } & Partial<CanvasNode>>): void;
  deleteNodes(ids: string[]): void;
  selectNodes(ids: string[], additive?: boolean): void;
  clearSelection(): void;
  setHovered(id: string | null): void;
  setStagePosition(x: number, y: number): void;
  moveNodesToParent(ids: string[], parentId: string | null): void;
  duplicateNodes(ids: string[]): string[];
  reorderNode(id: string, newOrder: number): void;
  reorderNodes(patches: Array<{ id: string; order: number }>): void;
  groupNodes(ids: string[]): string;
  ungroupNodes(ids: string[]): void;
  frameNodes(ids: string[]): string;
  flipNodes(ids: string[], axis: "x" | "y"): void;
  resizeFrameToFit(id: string): void;
  setModifiers(mods: TransformModifiers | null): void;
  applyModifiers(): void;
  setSnapGuides(guides: SnapResult[]): void;
  /** Atomically set both modifiers and snap guides in a single render (avoids split-frame glitches). */
  setTransformPreview(mods: TransformModifiers, guides: SnapResult[]): void;
  copyNodes(ids: string[]): void;
  cutNodes(ids: string[]): void;
  pasteNodes(offsetX?: number, offsetY?: number): string[];
  selectAll(): void;
  undo(): void;
  redo(): void;
}

const DEFAULT_NODE: Partial<CanvasNode> = {
  fill: "#ffffff",
  fillOpacity: 1,
  stroke: null,
  strokeWidth: 1,
  opacity: 1,
  cornerRadius: 0,
  rotation: 0,
  visible: true,
  locked: false,
};

const DEFAULT_TEXT_NODE: Partial<CanvasNode> = {
  text: "Text",
  textColor: "#000000",
  fontFamily: "Inter",
  fontWeight: 400,
  fontStyle: "normal",
  fontSize: 16,
  lineHeight: 1.2,
  letterSpacing: 0,
  textAlign: "left",
  textDecoration: "none",
  textTransform: "none",
  paragraphSpacing: 0,
  textSizing: "auto",
  fill: null,
  stroke: null,
  strokeWidth: 0,
};

const DEFAULT_FRAME_NODE: Partial<CanvasNode> = {
  fill: "#ffffff",
  clipContent: true,
};

function getDefaults(type: NodeType): Partial<CanvasNode> {
  if (type === "text") return { ...DEFAULT_NODE, ...DEFAULT_TEXT_NODE };
  if (type === "frame") return { ...DEFAULT_NODE, ...DEFAULT_FRAME_NODE };
  return DEFAULT_NODE;
}

/** Typography properties that affect text dimensions when changed. */
const TEXT_SIZING_KEYS: ReadonlySet<string> = new Set([
  "text", "fontSize", "fontFamily", "fontWeight", "fontStyle",
  "lineHeight", "letterSpacing", "textTransform",
]);

/** If a text node is in "auto" sizing mode and a typography property changed, remeasure and patch width/height. */
function autoResizeTextNode(node: CanvasNode, patch: Partial<CanvasNode>) {
  if (node.type !== "text") return;
  // Determine the effective sizing mode after this patch is applied
  const effectiveSizing = patch.textSizing ?? node.textSizing ?? "auto";
  if (effectiveSizing !== "auto") return;
  // Trigger remeasure if typography properties changed OR if switching to auto mode
  const switchingToAuto = patch.textSizing === "auto" && (node.textSizing ?? "auto") !== "auto";
  const affectsSize = Object.keys(patch).some((k) => TEXT_SIZING_KEYS.has(k));
  if (!affectsSize && !switchingToAuto) return;
  // Merge current node with patch to get the final state for measurement
  const merged = { ...node, ...patch };
  const measured = measureText(merged);
  patch.width = measured.width;
  patch.height = measured.height;
}

const MAX_HISTORY = 100;

/** Push a snapshot of current nodes+selection onto historyPast and clear historyFuture. */
function pushSnapshot(s: {
  historyPast: HistoryEntry[];
  historyFuture: HistoryEntry[];
  nodes: CanvasNode[];
  selectedIds: string[];
}) {
  s.historyPast.push({
    nodes: current(s.nodes) as CanvasNode[],
    selectedIds: [...s.selectedIds],
  });
  if (s.historyPast.length > MAX_HISTORY) s.historyPast.shift();
  s.historyFuture = [];
}

/** Recursively shift x/y of all descendants by (dx, dy) within an immer draft. */
function shiftDescendants(nodes: CanvasNode[], parentId: string, dx: number, dy: number, exclude?: Set<string>) {
  for (const n of nodes) {
    if (n.parentId === parentId) {
      if (!exclude || !exclude.has(n.id)) {
        n.x += dx;
        n.y += dy;
      }
      shiftDescendants(nodes, n.id, dx, dy, exclude);
    }
  }
}

export const useCanvasStore = create<CanvasState & CanvasActions>()(
  immer((set, get) => ({
    nodes: [],
    selectedIds: [],
    hoveredId: null,
    stageX: 0,
    stageY: 0,
    historyPast: [],
    historyFuture: [],
    modifiers: null,
    snapGuides: [],
    clipboard: [],

    addNode(partial) {
      const id = nanoid();
      const maxOrder = get().nodes.reduce((m, n) => Math.max(m, n.order), 0);
      const defaults = getDefaults(partial.type);
      const pageId = partial.pageId ?? usePagesStore.getState().activePageId;
      const node = { ...defaults, ...partial, id, pageId, order: maxOrder + 1 } as CanvasNode;
      set((s) => {
        pushSnapshot(s);
        s.nodes.push(node);
        s.selectedIds = [id];
      });
      return id;
    },

    updateNode(id, patch) {
      set((s) => {
        const idx = s.nodes.findIndex((n) => n.id === id);
        if (idx === -1) return;
        pushSnapshot(s);
        const node = s.nodes[idx];
        // Auto-resize text nodes when typography properties change
        autoResizeTextNode(node, patch);
        const dx = patch.x !== undefined ? (patch.x as number) - node.x : 0;
        const dy = patch.y !== undefined ? (patch.y as number) - node.y : 0;
        Object.assign(node, patch);
        // Cascade position delta to all descendants so children move with their parent
        if (dx !== 0 || dy !== 0) shiftDescendants(s.nodes, id, dx, dy);
      });
    },

    updateNodes(patches) {
      set((s) => {
        pushSnapshot(s);
        for (const patch of patches) {
          const idx = s.nodes.findIndex((n) => n.id === patch.id);
          if (idx === -1) continue;
          const node = s.nodes[idx];
          autoResizeTextNode(node, patch);
          const dx = patch.x !== undefined ? (patch.x as number) - node.x : 0;
          const dy = patch.y !== undefined ? (patch.y as number) - node.y : 0;
          Object.assign(node, patch);
          // Cascade to descendants
          if (dx !== 0 || dy !== 0) shiftDescendants(s.nodes, patch.id, dx, dy);
        }
      });
    },

    deleteNodes(ids) {
      const idSet = new Set(ids);
      // Also delete all descendants
      const allDescendants = new Set<string>();
      function collectDescendants(parentId: string) {
        get().nodes.forEach((n) => {
          if (n.parentId === parentId) {
            allDescendants.add(n.id);
            collectDescendants(n.id);
          }
        });
      }
      ids.forEach(collectDescendants);
      const toDelete = new Set([...idSet, ...allDescendants]);
      set((s) => {
        pushSnapshot(s);
        s.nodes = s.nodes.filter((n) => !toDelete.has(n.id));
        s.selectedIds = s.selectedIds.filter((id) => !toDelete.has(id));
        if (s.hoveredId && toDelete.has(s.hoveredId)) s.hoveredId = null;
      });
    },

    selectNodes(ids, additive = false) {
      set((s) => {
        if (additive) {
          const current = new Set(s.selectedIds);
          ids.forEach((id) => {
            if (current.has(id)) current.delete(id);
            else current.add(id);
          });
          s.selectedIds = Array.from(current);
        } else {
          s.selectedIds = ids;
        }
      });
    },

    clearSelection() {
      set((s) => { s.selectedIds = []; });
    },

    setHovered(id) {
      set((s) => { s.hoveredId = id; });
    },

    setStagePosition(x, y) {
      set((s) => { s.stageX = x; s.stageY = y; });
    },

    moveNodesToParent(ids, parentId) {
      set((s) => {
        pushSnapshot(s);
        ids.forEach((id) => {
          const idx = s.nodes.findIndex((n) => n.id === id);
          if (idx !== -1) s.nodes[idx].parentId = parentId;
        });
      });
    },

    duplicateNodes(ids) {
      const nodes = get().nodes;
      const newIds: string[] = [];
      const idMap = new Map<string, string>();

      // First pass: create new IDs
      ids.forEach((id) => {
        idMap.set(id, nanoid());
      });

      const maxOrder = nodes.reduce((m, n) => Math.max(m, n.order), 0);
      let orderOffset = 1;

      set((s) => {
        pushSnapshot(s);
        ids.forEach((id) => {
          const src = s.nodes.find((n) => n.id === id);
          if (!src) return;
          const newId = idMap.get(id)!;
          newIds.push(newId);
          s.nodes.push({
            ...src,
            id: newId,
            name: src.name + " copy",
            x: src.x + 16,
            y: src.y + 16,
            order: maxOrder + orderOffset++,
            parentId: src.parentId,
          });
        });
        s.selectedIds = newIds;
      });

      return newIds;
    },

    reorderNode(id, newOrder) {
      set((s) => {
        pushSnapshot(s);
        const idx = s.nodes.findIndex((n) => n.id === id);
        if (idx !== -1) s.nodes[idx].order = newOrder;
      });
    },

    reorderNodes(patches) {
      set((s) => {
        pushSnapshot(s);
        for (const { id, order } of patches) {
          const idx = s.nodes.findIndex((n) => n.id === id);
          if (idx !== -1) s.nodes[idx].order = order;
        }
      });
    },

    groupNodes(ids) {
      const state = get();
      const selected = state.nodes.filter((n) => ids.includes(n.id));
      if (selected.length === 0) return "";

      const minX = Math.min(...selected.map((n) => n.x));
      const minY = Math.min(...selected.map((n) => n.y));
      const maxX = Math.max(...selected.map((n) => n.x + n.width));
      const maxY = Math.max(...selected.map((n) => n.y + n.height));
      const maxOrder = state.nodes.reduce((m, n) => Math.max(m, n.order), 0);
      const pageId = selected[0].pageId;
      const parentId = selected[0].parentId ?? null;
      const groupId = nanoid();

      set((s) => {
        pushSnapshot(s);
        s.nodes.push({
          ...DEFAULT_NODE,
          id: groupId,
          type: "group",
          name: "Group",
          x: minX, y: minY,
          width: maxX - minX,
          height: maxY - minY,
          rotation: 0,
          order: maxOrder + 1,
          pageId,
          parentId,
          fill: null,
          stroke: null,
          strokeWidth: 0,
          opacity: 1,
          cornerRadius: 0,
          fillOpacity: 1,
          visible: true,
          locked: false,
        } as CanvasNode);
        // Reparent all selected nodes to the new group
        for (const n of s.nodes) {
          if (ids.includes(n.id)) n.parentId = groupId;
        }
        s.selectedIds = [groupId];
      });

      return groupId;
    },

    ungroupNodes(ids) {
      const state = get();
      const groups = state.nodes.filter((n) => ids.includes(n.id) && (n.type === "group" || n.type === "frame"));
      if (groups.length === 0) return;

      const newSelection: string[] = [];

      set((s) => {
        pushSnapshot(s);
        for (const group of groups) {
          // Promote direct children to the group's parent
          const children = s.nodes.filter((n) => n.parentId === group.id);
          for (const child of children) {
            child.parentId = group.parentId ?? null;
            newSelection.push(child.id);
          }
          // Remove the group
          s.nodes = s.nodes.filter((n) => n.id !== group.id);
        }
        s.selectedIds = newSelection;
      });
    },

    frameNodes(ids) {
      const state = get();
      const selected = state.nodes.filter((n) => ids.includes(n.id));
      if (selected.length === 0) return "";

      const minX = Math.min(...selected.map((n) => n.x));
      const minY = Math.min(...selected.map((n) => n.y));
      const maxX = Math.max(...selected.map((n) => n.x + n.width));
      const maxY = Math.max(...selected.map((n) => n.y + n.height));
      const maxOrder = state.nodes.reduce((m, n) => Math.max(m, n.order), 0);
      const pageId = selected[0].pageId;
      const parentId = selected[0].parentId ?? null;
      const frameId = nanoid();

      set((s) => {
        pushSnapshot(s);
        s.nodes.push({
          ...DEFAULT_NODE,
          ...DEFAULT_FRAME_NODE,
          id: frameId,
          type: "frame",
          name: "Frame",
          x: minX, y: minY,
          width: maxX - minX,
          height: maxY - minY,
          rotation: 0,
          order: maxOrder + 1,
          pageId,
          parentId,
          fillOpacity: 1,
          visible: true,
          locked: false,
        } as CanvasNode);
        for (const n of s.nodes) {
          if (ids.includes(n.id)) n.parentId = frameId;
        }
        s.selectedIds = [frameId];
      });

      return frameId;
    },

    flipNodes(ids, axis) {
      set((s) => {
        pushSnapshot(s);
        for (const n of s.nodes) {
          if (!ids.includes(n.id)) continue;
          if (axis === "x") {
            n.flipX = !(n.flipX ?? false);
          } else {
            n.flipY = !(n.flipY ?? false);
          }
        }
      });
    },

    resizeFrameToFit(id) {
      set((s) => {
        const frame = s.nodes.find((n) => n.id === id);
        if (!frame || frame.type !== "frame") return;
        const children = s.nodes.filter((n) => n.parentId === id);
        if (children.length === 0) return;
        pushSnapshot(s);
        const minX = Math.min(...children.map((n) => n.x));
        const minY = Math.min(...children.map((n) => n.y));
        const maxX = Math.max(...children.map((n) => n.x + n.width));
        const maxY = Math.max(...children.map((n) => n.y + n.height));
        frame.x = minX;
        frame.y = minY;
        frame.width = maxX - minX;
        frame.height = maxY - minY;
      });
    },

    setModifiers(mods) {
      set((s) => { s.modifiers = mods; });
    },

    applyModifiers() {
      set((s) => {
        if (!s.modifiers) return;
        pushSnapshot(s);
        const modIds = new Set(Object.keys(s.modifiers));
        for (const [id, patch] of Object.entries(s.modifiers)) {
          const idx = s.nodes.findIndex((n) => n.id === id);
          if (idx === -1) continue;
          const node = s.nodes[idx];
          const dx = patch.x !== undefined ? (patch.x as number) - node.x : 0;
          const dy = patch.y !== undefined ? (patch.y as number) - node.y : 0;
          // If a text node is manually resized, switch to fixed sizing
          if (node.type === "text" && (patch.width !== undefined || patch.height !== undefined)) {
            node.textSizing = "fixed";
          }
          Object.assign(node, patch);
          // Skip cascading to descendants that are explicitly in the modifiers
          // (they'll be positioned directly via their own modifier entry)
          if (dx !== 0 || dy !== 0) shiftDescendants(s.nodes, id, dx, dy, modIds);
        }
        s.modifiers = null;
        s.snapGuides = [];
      });
    },

    setSnapGuides(guides) {
      set((s) => { s.snapGuides = guides; });
    },

    setTransformPreview(mods, guides) {
      set((s) => {
        s.modifiers = mods;
        s.snapGuides = guides;
      });
    },

    copyNodes(ids) {
      const nodes = get().nodes;
      const copied = ids
        .map((id) => nodes.find((n) => n.id === id))
        .filter(Boolean) as CanvasNode[];
      set((s) => { s.clipboard = current(copied) as CanvasNode[]; });
    },

    cutNodes(ids) {
      get().copyNodes(ids);
      get().deleteNodes(ids);
    },

    pasteNodes(offsetX = 16, offsetY = 16) {
      const clipboard = get().clipboard;
      if (clipboard.length === 0) return [];
      const maxOrder = get().nodes.reduce((m, n) => Math.max(m, n.order), 0);
      const idMap = new Map<string, string>();
      const newIds: string[] = [];
      let orderOffset = 1;

      // Create new IDs for all clipboard nodes
      for (const node of clipboard) {
        idMap.set(node.id, nanoid());
      }

      set((s) => {
        pushSnapshot(s);
        for (const node of clipboard) {
          const newId = idMap.get(node.id)!;
          newIds.push(newId);
          s.nodes.push({
            ...node,
            id: newId,
            x: node.x + offsetX,
            y: node.y + offsetY,
            order: maxOrder + orderOffset++,
            // Remap parent if it was also copied; otherwise detach
            parentId: node.parentId && idMap.has(node.parentId) ? idMap.get(node.parentId)! : null,
          } as CanvasNode);
        }
        s.selectedIds = newIds;
      });

      return newIds;
    },

    selectAll() {
      const pageId = usePagesStore.getState().activePageId;
      set((s) => {
        s.selectedIds = s.nodes
          .filter((n) => n.pageId === pageId && n.visible && !n.parentId)
          .map((n) => n.id);
      });
    },

    undo() {
      set((s) => {
        if (s.historyPast.length === 0) return;
        const snapshot = { nodes: current(s.nodes) as CanvasNode[], selectedIds: [...s.selectedIds] };
        s.historyFuture.push(snapshot);
        const prev = s.historyPast.pop()!;
        s.nodes = prev.nodes as typeof s.nodes;
        s.selectedIds = prev.selectedIds;
      });
    },

    redo() {
      set((s) => {
        if (s.historyFuture.length === 0) return;
        const snapshot = { nodes: current(s.nodes) as CanvasNode[], selectedIds: [...s.selectedIds] };
        s.historyPast.push(snapshot);
        const next = s.historyFuture.pop()!;
        s.nodes = next.nodes as typeof s.nodes;
        s.selectedIds = next.selectedIds;
      });
    },
  }))
);
