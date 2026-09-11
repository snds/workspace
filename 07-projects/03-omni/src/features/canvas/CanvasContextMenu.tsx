import type { ReactNode } from "react";
import {
  ContextMenu,
  ContextMenuTrigger,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuSeparator,
  ContextMenuShortcut,
  ContextMenuCheckboxItem,
} from "@/components/ui/context-menu";
import { useCanvasStore } from "@/stores/canvas.store";
import { useUIStore } from "@/stores/ui.store";

interface CanvasContextMenuProps {
  children: ReactNode;
}

export function CanvasContextMenu({ children }: CanvasContextMenuProps) {
  const selectedIds = useCanvasStore((s) => s.selectedIds);
  const hasSelection = selectedIds.length > 0;

  return (
    <ContextMenu>
      <ContextMenuTrigger asChild>{children}</ContextMenuTrigger>
      <ContextMenuContent className="w-56">
        {hasSelection ? <ShapeMenu /> : <ViewportMenu />}
      </ContextMenuContent>
    </ContextMenu>
  );
}

// ─── Shape context menu (right-click on selected shapes) ────────────────────

function ShapeMenu() {
  const { selectedIds, copyNodes, cutNodes, pasteNodes, deleteNodes, duplicateNodes, groupNodes, ungroupNodes, frameNodes, flipNodes, clipboard } = useCanvasStore();
  const hasClipboard = clipboard.length > 0;

  // Check if any selected node is a group/frame (for ungroup)
  const nodes = useCanvasStore((s) => s.nodes);
  const selectedNodes = selectedIds.map((id) => nodes.find((n) => n.id === id)).filter(Boolean);
  const hasGroupOrFrame = selectedNodes.some((n) => n && (n.type === "group" || n.type === "frame"));

  // Check lock/visibility state
  const allLocked = selectedNodes.every((n) => n?.locked);
  const allHidden = selectedNodes.every((n) => !n?.visible);

  const updateNode = useCanvasStore((s) => s.updateNode);

  return (
    <>
      <ContextMenuItem onSelect={() => cutNodes(selectedIds)}>
        Cut
        <ContextMenuShortcut>&#8984;X</ContextMenuShortcut>
      </ContextMenuItem>
      <ContextMenuItem onSelect={() => copyNodes(selectedIds)}>
        Copy
        <ContextMenuShortcut>&#8984;C</ContextMenuShortcut>
      </ContextMenuItem>
      <ContextMenuItem onSelect={() => pasteNodes()} disabled={!hasClipboard}>
        Paste
        <ContextMenuShortcut>&#8984;V</ContextMenuShortcut>
      </ContextMenuItem>
      <ContextMenuItem onSelect={() => duplicateNodes(selectedIds)}>
        Duplicate
        <ContextMenuShortcut>&#8984;D</ContextMenuShortcut>
      </ContextMenuItem>

      <ContextMenuSeparator />

      <ContextMenuItem onSelect={() => groupNodes(selectedIds)} disabled={selectedIds.length < 2}>
        Group selection
        <ContextMenuShortcut>&#8984;G</ContextMenuShortcut>
      </ContextMenuItem>
      <ContextMenuItem onSelect={() => ungroupNodes(selectedIds)} disabled={!hasGroupOrFrame}>
        Ungroup
        <ContextMenuShortcut>&#8984;&#8679;G</ContextMenuShortcut>
      </ContextMenuItem>
      <ContextMenuItem onSelect={() => frameNodes(selectedIds)}>
        Frame selection
        <ContextMenuShortcut>&#8984;&#8997;G</ContextMenuShortcut>
      </ContextMenuItem>

      <ContextMenuSeparator />

      <ContextMenuItem onSelect={() => bringToFront(selectedIds)}>
        Bring to front
        <ContextMenuShortcut>]</ContextMenuShortcut>
      </ContextMenuItem>
      <ContextMenuItem onSelect={() => sendToBack(selectedIds)}>
        Send to back
        <ContextMenuShortcut>[</ContextMenuShortcut>
      </ContextMenuItem>

      <ContextMenuSeparator />

      <ContextMenuItem onSelect={() => flipNodes(selectedIds, "x")}>
        Flip horizontal
        <ContextMenuShortcut>&#8679;H</ContextMenuShortcut>
      </ContextMenuItem>
      <ContextMenuItem onSelect={() => flipNodes(selectedIds, "y")}>
        Flip vertical
        <ContextMenuShortcut>&#8679;V</ContextMenuShortcut>
      </ContextMenuItem>

      <ContextMenuSeparator />

      <ContextMenuItem onSelect={() => {
        for (const id of selectedIds) updateNode(id, { locked: !allLocked });
      }}>
        {allLocked ? "Unlock" : "Lock"}
        <ContextMenuShortcut>&#8984;&#8679;L</ContextMenuShortcut>
      </ContextMenuItem>
      <ContextMenuItem onSelect={() => {
        for (const id of selectedIds) updateNode(id, { visible: allHidden });
      }}>
        {allHidden ? "Show" : "Hide"}
        <ContextMenuShortcut>&#8984;&#8679;H</ContextMenuShortcut>
      </ContextMenuItem>

      <ContextMenuSeparator />

      <ContextMenuItem onSelect={() => deleteNodes(selectedIds)} className="text-red-400 focus:text-red-400">
        Delete
        <ContextMenuShortcut>&#9003;</ContextMenuShortcut>
      </ContextMenuItem>
    </>
  );
}

// ─── Viewport context menu (right-click on empty canvas) ────────────────────

function ViewportMenu() {
  const { pasteNodes, selectAll, clipboard } = useCanvasStore();
  const { showRulers, showGrid, toggleRulers, toggleGrid, snapEnabled, toggleSnap } = useUIStore();
  const hasClipboard = clipboard.length > 0;

  return (
    <>
      <ContextMenuItem onSelect={() => pasteNodes()} disabled={!hasClipboard}>
        Paste
        <ContextMenuShortcut>&#8984;V</ContextMenuShortcut>
      </ContextMenuItem>
      <ContextMenuItem onSelect={selectAll}>
        Select all
        <ContextMenuShortcut>&#8984;A</ContextMenuShortcut>
      </ContextMenuItem>

      <ContextMenuSeparator />

      <ContextMenuCheckboxItem checked={showRulers} onSelect={toggleRulers}>
        Show rulers
      </ContextMenuCheckboxItem>
      <ContextMenuCheckboxItem checked={showGrid} onSelect={toggleGrid}>
        Show pixel grid
      </ContextMenuCheckboxItem>
      <ContextMenuCheckboxItem checked={snapEnabled} onSelect={toggleSnap}>
        Snap to objects
      </ContextMenuCheckboxItem>
    </>
  );
}

// ─── Z-order helpers ────────────────────────────────────────────────────────

function bringToFront(ids: string[]) {
  const { nodes, reorderNodes } = useCanvasStore.getState();
  const maxOrder = nodes.reduce((m, n) => Math.max(m, n.order), 0);
  const patches = ids.map((id, i) => ({ id, order: maxOrder + 1 + i }));
  reorderNodes(patches);
}

function sendToBack(ids: string[]) {
  const { nodes, reorderNodes } = useCanvasStore.getState();
  const minOrder = nodes.reduce((m, n) => Math.min(m, n.order), Infinity);
  const patches = ids.map((id, i) => ({ id, order: minOrder - ids.length + i }));
  reorderNodes(patches);
}
