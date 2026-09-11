import { useRef, useCallback, useState, useEffect } from "react";
import {
  Layers,
  FileText,
  Plus,
  Trash2,
  Frame,
  Square,
  Type,
  Eye,
  EyeOff,
  Lock,
  Unlock,
  ChevronRight,
  ChevronDown,
  Columns2,
  Rows2,
  Grid2x2,
  Copy,
  Clipboard,
  Scissors,
  Pencil,
} from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuSeparator,
  ContextMenuShortcut,
  ContextMenuTrigger,
} from "@/components/ui/context-menu";
import { useUIStore } from "@/stores/ui.store";
import { usePagesStore } from "@/stores/pages.store";
import { useCanvasStore } from "@/stores/canvas.store";
import { cn } from "@/lib/utils";
import type { CanvasNode, CanvasTreeNode } from "@/types/canvas";

// ─── Tree building ────────────────────────────────────────────────────────────

function buildTree(nodes: CanvasNode[]): CanvasTreeNode[] {
  const map = new Map<string, CanvasTreeNode>();
  nodes.forEach((n) => map.set(n.id, { ...n, children: [], depth: 0 }));

  const roots: CanvasTreeNode[] = [];
  map.forEach((node) => {
    if (node.parentId && map.has(node.parentId)) {
      map.get(node.parentId)!.children.push(node);
    } else {
      roots.push(node);
    }
  });

  function setDepth(node: CanvasTreeNode, depth: number) {
    node.depth = depth;
    node.children.sort((a, b) => b.order - a.order);
    node.children.forEach((c) => setDepth(c, depth + 1));
  }
  roots.sort((a, b) => b.order - a.order);
  roots.forEach((r) => setDepth(r, 0));
  return roots;
}

// ─── Layer row ────────────────────────────────────────────────────────────────

const TYPE_ICONS: Record<string, React.ElementType> = {
  frame: Frame,
  rectangle: Square,
  text: Type,
  group: Layers,
};

function getNodeIcon(node: CanvasTreeNode): React.ElementType {
  if (node.type === "frame") {
    switch (node.layoutMode) {
      case "HORIZONTAL": return Columns2;
      case "VERTICAL":   return Rows2;
      case "GRID":       return Grid2x2;
      default:           return Frame;
    }
  }
  return TYPE_ICONS[node.type] ?? Square;
}

interface LayerRowProps {
  node: CanvasTreeNode;
  isSelected: boolean;
  isHovered: boolean;
  /** This node is a visible descendant of a selected parent */
  isChildOfSelected: boolean;
  /** Parent node is locked — show dot indicators instead of full icons */
  parentLocked: boolean;
  isExpanded: boolean;
  onToggleExpand: () => void;
  onClick: (e: React.MouseEvent) => void;
  onMouseEnter: () => void;
  onMouseLeave: () => void;
  onToggleVisible: () => void;
  onToggleLock: () => void;
  onRename: () => void;
  onDelete: () => void;
  onCopy: () => void;
  onCut: () => void;
  onPaste: () => void;
  onDuplicate: () => void;
  hasClipboard: boolean;
  /** Drag-drop state */
  isDragTarget?: "before" | "after" | "inside" | null;
  isDragging?: boolean;
  onDragStart?: (e: React.MouseEvent) => void;
}

function LayerRow({
  node,
  isSelected,
  isHovered,
  isChildOfSelected,
  parentLocked,
  isExpanded,
  onToggleExpand,
  onClick,
  onMouseEnter,
  onMouseLeave,
  onToggleVisible,
  onToggleLock,
  onRename,
  onDelete,
  onCopy,
  onCut,
  onPaste,
  onDuplicate,
  hasClipboard,
  isDragTarget,
  isDragging,
  onDragStart,
}: LayerRowProps) {
  const Icon = getNodeIcon(node);
  const hasChildren = node.children.length > 0;
  const indent = node.depth * 16;

  const showInteractive = isSelected || isHovered;
  const isLocked = node.locked;
  const isHidden = !node.visible;

  return (
    <ContextMenu>
      <ContextMenuTrigger asChild>
        <div
          data-layer-id={node.id}
          onMouseEnter={onMouseEnter}
          onMouseLeave={onMouseLeave}
          className={cn(
            "group flex items-center h-[26px] px-1 gap-1 cursor-pointer select-none relative mb-0.5",
            "before:absolute before:inset-0 before:rounded before:pointer-events-none before:content-[''] hover:before:bg-[rgba(255,255,255,0.05)]",
            isSelected
              ? "bg-[var(--violet-3)] text-white rounded"
              : isChildOfSelected
                ? "bg-[var(--violet-2)] text-white"
                : isHovered
                  ? "bg-[rgba(255,255,255,0.05)] text-white rounded"
                  : "text-[var(--mauve-11)] rounded",
            isDragging && "opacity-40",
            isDragTarget === "inside" && "ring-1 ring-[var(--violet-7)] bg-[var(--violet-2)]",
          )}
          style={{ paddingLeft: 4 + indent }}
          onClick={onClick}
          onMouseDown={onDragStart}
        >
          {/* Drop indicator: before */}
          {isDragTarget === "before" && (
            <div className="absolute top-0 left-0 right-0 h-0.5 bg-[var(--violet-9)] -translate-y-px z-10" />
          )}
          {/* Drop indicator: after */}
          {isDragTarget === "after" && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[var(--violet-9)] translate-y-px z-10" />
          )}

          {/* Expand/collapse chevron — only visible on hover or selected */}
          <button
            className={cn(
              "w-4 h-4 flex items-center justify-center flex-shrink-0 text-[var(--mauve-8)]",
              !(hasChildren && showInteractive) && "opacity-0",
            )}
            onClick={(e) => {
              e.stopPropagation();
              if (hasChildren) onToggleExpand();
            }}
          >
            {hasChildren && (
              isExpanded
                ? <ChevronDown className="w-3 h-3" />
                : <ChevronRight className="w-3 h-3" />
            )}
          </button>

          <Icon className={cn("w-3 h-3 flex-shrink-0 opacity-60", isHidden && "opacity-25")} />
          <span className={cn("text-xs flex-1 truncate", isHidden && "opacity-40")}>{node.name}</span>

          {/* Lock / visibility — fixed slots, lock first, visibility second */}
          <div className="flex items-center gap-0.5">
            {/* Lock slot — dot for children of locked parents */}
            {parentLocked && node.parentId !== null ? (
              <button
                className="w-4 h-4 flex items-center justify-center text-white"
                title={isLocked ? "Locked" : "Unlocked"}
                onClick={(e) => {
                  e.stopPropagation();
                  onToggleLock();
                }}
              >
                {isLocked ? (
                  <Lock className="w-3 h-3" />
                ) : (
                  <span className="w-[5px] h-[5px] rounded-full bg-current block" />
                )}
              </button>
            ) : (
              <button
                className={cn(
                  "w-4 h-4 flex items-center justify-center text-white",
                  !isLocked && "opacity-0 group-hover:opacity-100",
                )}
                onClick={(e) => {
                  e.stopPropagation();
                  onToggleLock();
                }}
              >
                {isLocked ? <Lock className="w-3 h-3" /> : <Unlock className="w-3 h-3" />}
              </button>
            )}

            {/* Visibility slot */}
            <button
              className={cn(
                "w-4 h-4 flex items-center justify-center text-white",
                !isHidden && "opacity-0 group-hover:opacity-100",
              )}
              onClick={(e) => {
                e.stopPropagation();
                onToggleVisible();
              }}
            >
              {isHidden ? <EyeOff className="w-3 h-3" /> : <Eye className="w-3 h-3" />}
            </button>
          </div>
        </div>
      </ContextMenuTrigger>
      <ContextMenuContent className="min-w-[180px]">
        <ContextMenuItem onClick={onRename}>
          <Pencil className="w-3.5 h-3.5" />
          Rename
          <ContextMenuShortcut>F2</ContextMenuShortcut>
        </ContextMenuItem>
        <ContextMenuItem onClick={onDuplicate}>
          <Copy className="w-3.5 h-3.5" />
          Duplicate
          <ContextMenuShortcut>⌘D</ContextMenuShortcut>
        </ContextMenuItem>
        <ContextMenuSeparator />
        <ContextMenuItem onClick={onCopy}>
          <Copy className="w-3.5 h-3.5" />
          Copy
          <ContextMenuShortcut>⌘C</ContextMenuShortcut>
        </ContextMenuItem>
        <ContextMenuItem onClick={onCut}>
          <Scissors className="w-3.5 h-3.5" />
          Cut
          <ContextMenuShortcut>⌘X</ContextMenuShortcut>
        </ContextMenuItem>
        <ContextMenuItem onClick={onPaste} disabled={!hasClipboard}>
          <Clipboard className="w-3.5 h-3.5" />
          Paste
          <ContextMenuShortcut>⌘V</ContextMenuShortcut>
        </ContextMenuItem>
        <ContextMenuSeparator />
        <ContextMenuItem onClick={onToggleLock}>
          {isLocked ? <Unlock className="w-3.5 h-3.5" /> : <Lock className="w-3.5 h-3.5" />}
          {isLocked ? "Unlock" : "Lock"}
        </ContextMenuItem>
        <ContextMenuItem onClick={onToggleVisible}>
          {isHidden ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
          {isHidden ? "Show" : "Hide"}
        </ContextMenuItem>
        <ContextMenuSeparator />
        <ContextMenuItem onClick={onDelete} className="text-[var(--red-9)] focus:text-[var(--red-9)]">
          <Trash2 className="w-3.5 h-3.5" />
          Delete
          <ContextMenuShortcut>⌫</ContextMenuShortcut>
        </ContextMenuItem>
      </ContextMenuContent>
    </ContextMenu>
  );
}

// ─── Collapse icon ──────────────────────────────────────────────────────────

function CollapseLayersIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 14 14" fill="none" className={className} xmlns="http://www.w3.org/2000/svg">
      <line x1="2" y1="3" x2="12" y2="3" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
      <line x1="2" y1="7" x2="12" y2="7" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
      <line x1="2" y1="11" x2="12" y2="11" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
      <line x1="8.5" y1="5.5" x2="11.5" y2="8.5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
      <line x1="11.5" y1="5.5" x2="8.5" y2="8.5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
    </svg>
  );
}

// ─── Drag-drop types ─────────────────────────────────────────────────────────

interface DropTarget {
  targetId: string;
  position: "before" | "after" | "inside";
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Check if `nodeId` is a descendant of `ancestorId`. */
function isDescendant(nodeId: string, ancestorId: string, nodes: CanvasNode[]): boolean {
  let current = nodes.find((n) => n.id === nodeId);
  while (current?.parentId) {
    if (current.parentId === ancestorId) return true;
    current = nodes.find((n) => n.id === current!.parentId);
  }
  return false;
}

// ─── Layers panel ─────────────────────────────────────────────────────────────

interface LayersPanelProps {
  collapsed: Set<string>;
  setCollapsed: React.Dispatch<React.SetStateAction<Set<string>>>;
}

function LayersPanel({ collapsed, setCollapsed }: LayersPanelProps) {
  const { nodes, selectedIds, selectNodes, updateNode, deleteNodes, duplicateNodes, copyNodes, cutNodes, pasteNodes, clipboard, reorderNodes, moveNodesToParent, hoveredId, setHovered } = useCanvasStore();
  const { activePageId } = usePagesStore();
  const [draggedId, setDraggedId] = useState<string | null>(null);
  const [dropTarget, setDropTarget] = useState<DropTarget | null>(null);
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState("");
  const renameRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (renamingId && renameRef.current) {
      renameRef.current.focus();
      renameRef.current.select();
    }
  }, [renamingId]);

  function startLayerRename(id: string, name: string) {
    setRenamingId(id);
    setRenameValue(name);
  }

  function commitLayerRename() {
    if (renamingId && renameValue.trim()) {
      updateNode(renamingId, { name: renameValue.trim() });
    }
    setRenamingId(null);
  }

  const pageNodes = nodes.filter((n) => n.pageId === activePageId);
  const tree = buildTree(pageNodes);

  function toggleCollapse(id: string) {
    setCollapsed((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function flattenWithCollapse(roots: CanvasTreeNode[]): CanvasTreeNode[] {
    const result: CanvasTreeNode[] = [];
    function walk(node: CanvasTreeNode) {
      result.push(node);
      if (!collapsed.has(node.id)) {
        node.children.forEach(walk);
      }
    }
    roots.forEach(walk);
    return result;
  }

  const flat = flattenWithCollapse(tree);

  // Build map of locked parent IDs → children inherit dot indicators
  const lockedParentIds = new Set<string>();
  for (const n of pageNodes) {
    if (n.locked && pageNodes.some((c) => c.parentId === n.id)) {
      lockedParentIds.add(n.id);
    }
  }

  /** Check if any ancestor of nodeId is locked */
  function hasLockedAncestor(nodeId: string): boolean {
    const node = pageNodes.find((n) => n.id === nodeId);
    if (!node?.parentId) return false;
    if (lockedParentIds.has(node.parentId)) return true;
    return hasLockedAncestor(node.parentId);
  }

  // Build set of node IDs that are visible descendants of any selected node
  const childOfSelectedIds = new Set<string>();
  {
    const selSet = new Set(selectedIds);
    function collectVisibleDescendants(parent: CanvasTreeNode) {
      if (collapsed.has(parent.id)) return; // children not visible
      for (const child of parent.children) {
        childOfSelectedIds.add(child.id);
        collectVisibleDescendants(child);
      }
    }
    function walkTree(roots: CanvasTreeNode[]) {
      for (const node of roots) {
        if (selSet.has(node.id)) {
          collectVisibleDescendants(node);
        } else {
          walkTree(node.children);
        }
      }
    }
    walkTree(tree);
  }

  // ── Drag-drop handlers ──────────────────────────────────────────────────────

  function commitDrop(dragId: string, target: DropTarget) {
    const dragNode = pageNodes.find((n) => n.id === dragId);
    const targetNode = pageNodes.find((n) => n.id === target.targetId);
    if (!dragNode || !targetNode) return;

    if (target.position === "inside") {
      moveNodesToParent([dragId], target.targetId);
      const children = pageNodes.filter((n) => n.parentId === target.targetId);
      const maxOrder = children.length > 0 ? Math.max(...children.map((n) => n.order)) : 0;
      reorderNodes([{ id: dragId, order: maxOrder + 1 }]);
    } else {
      const newParentId = targetNode.parentId;
      if (dragNode.parentId !== newParentId) {
        moveNodesToParent([dragId], newParentId);
      }

      const siblings = pageNodes
        .filter((n) => n.parentId === newParentId && n.id !== dragId)
        .sort((a, b) => b.order - a.order);

      const targetIndex = siblings.findIndex((n) => n.id === target.targetId);
      if (targetIndex === -1) return;

      const patches: Array<{ id: string; order: number }> = [];
      const reordered = [...siblings];
      const insertIdx = target.position === "before" ? targetIndex : targetIndex + 1;
      reordered.splice(insertIdx, 0, dragNode);

      const baseOrder = reordered.length;
      for (let i = 0; i < reordered.length; i++) {
        patches.push({ id: reordered[i].id, order: baseOrder - i });
      }

      reorderNodes(patches);
    }
  }

  const dropTargetRef = useRef(dropTarget);
  useEffect(() => { dropTargetRef.current = dropTarget; }, [dropTarget]);

  const handleDragStartStable = useCallback((nodeId: string) => {
    return (e: React.MouseEvent) => {
      if (e.button !== 0) return;
      const target = e.target as HTMLElement;
      if (target.closest("button")) return;

      e.preventDefault();
      const startY = e.clientY;
      let didDrag = false;

      const onMove = (ev: MouseEvent) => {
        if (!didDrag && Math.abs(ev.clientY - startY) < 4) return;
        if (!didDrag) {
          didDrag = true;
          setDraggedId(nodeId);
        }

        const container = containerRef.current;
        if (!container) return;

        const rows = container.querySelectorAll("[data-layer-id]");
        let newTarget: DropTarget | null = null;

        for (const row of rows) {
          const rowId = row.getAttribute("data-layer-id")!;
          if (rowId === nodeId) continue;
          if (isDescendant(rowId, nodeId, pageNodes)) continue;

          const rect = row.getBoundingClientRect();
          if (ev.clientY < rect.top || ev.clientY > rect.bottom) continue;

          const relY = (ev.clientY - rect.top) / rect.height;
          const rowNode = pageNodes.find((n) => n.id === rowId);
          const isContainer = rowNode?.type === "frame" || rowNode?.type === "group";

          if (relY < 0.25) {
            newTarget = { targetId: rowId, position: "before" };
          } else if (relY > 0.75) {
            newTarget = { targetId: rowId, position: "after" };
          } else if (isContainer) {
            newTarget = { targetId: rowId, position: "inside" };
          } else if (relY < 0.5) {
            newTarget = { targetId: rowId, position: "before" };
          } else {
            newTarget = { targetId: rowId, position: "after" };
          }
          break;
        }

        setDropTarget(newTarget);
      };

      const onUp = () => {
        window.removeEventListener("mousemove", onMove);
        window.removeEventListener("mouseup", onUp);

        const currentTarget = dropTargetRef.current;
        if (didDrag && currentTarget) {
          commitDrop(nodeId, currentTarget);
        }

        setDraggedId(null);
        setDropTarget(null);
      };

      window.addEventListener("mousemove", onMove);
      window.addEventListener("mouseup", onUp);
    };
  }, [pageNodes]); // eslint-disable-line react-hooks/exhaustive-deps

  if (pageNodes.length === 0) {
    return (
      <div className="flex flex-col items-center gap-2 py-8 px-3 text-center">
        <Layers className="w-7 h-7 text-[var(--mauve-7)]" />
        <p className="text-xs font-medium text-[var(--mauve-10)]">No layers yet</p>
        <p className="text-[10px] text-[var(--mauve-8)] leading-relaxed">
          Draw a frame or shape on the canvas.
        </p>
      </div>
    );
  }

  return (
    <div className="py-1 px-1" ref={containerRef}>
      {flat.map((node) => (
        renamingId === node.id ? (
          <div
            key={node.id}
            className="flex items-center h-[26px] px-1 gap-1 mb-0.5 bg-[var(--violet-3)] rounded"
            style={{ paddingLeft: 4 + node.depth * 16 }}
          >
            <div className="w-4 h-4 flex-shrink-0" />
            {(() => { const Icon = getNodeIcon(node); return <Icon className="w-3 h-3 flex-shrink-0 opacity-60" />; })()}
            <input
              ref={renameRef}
              value={renameValue}
              onChange={(e) => setRenameValue(e.target.value)}
              onBlur={commitLayerRename}
              onKeyDown={(e) => {
                if (e.key === "Enter") commitLayerRename();
                if (e.key === "Escape") setRenamingId(null);
              }}
              className="flex-1 bg-[var(--mauve-4)] text-xs text-[var(--mauve-12)] rounded px-1 outline-none border border-[var(--violet-7)] h-[18px]"
            />
          </div>
        ) : (
          <LayerRow
            key={node.id}
            node={node}
            isSelected={selectedIds.includes(node.id)}
            isHovered={hoveredId === node.id}
            isChildOfSelected={childOfSelectedIds.has(node.id)}
            parentLocked={hasLockedAncestor(node.id)}
            isExpanded={!collapsed.has(node.id)}
            onToggleExpand={() => toggleCollapse(node.id)}
            onClick={(e) => selectNodes([node.id], e.shiftKey)}
            onMouseEnter={() => setHovered(node.id)}
            onMouseLeave={() => setHovered(null)}
            onToggleVisible={() => updateNode(node.id, { visible: !node.visible })}
            onToggleLock={() => updateNode(node.id, { locked: !node.locked })}
            onRename={() => startLayerRename(node.id, node.name)}
            onDelete={() => deleteNodes([node.id])}
            onCopy={() => copyNodes([node.id])}
            onCut={() => cutNodes([node.id])}
            onPaste={() => pasteNodes()}
            onDuplicate={() => duplicateNodes([node.id])}
            hasClipboard={clipboard.length > 0}
            isDragTarget={dropTarget?.targetId === node.id ? dropTarget.position : null}
            isDragging={draggedId === node.id}
            onDragStart={handleDragStartStable(node.id)}
          />
        )
      ))}
    </div>
  );
}

// ─── Pages panel ─────────────────────────────────────────────────────────────

function PagesPanel() {
  const { pages, activePageId, deletePage, renamePage, convertToSeparator, setActivePage, reorderPage } =
    usePagesStore();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [draggedId, setDraggedId] = useState<string | null>(null);
  const [dropPosition, setDropPosition] = useState<{ targetId: string; pos: "before" | "after" } | null>(null);
  // Auto-select all text when editing starts
  useEffect(() => {
    if (editingId && inputRef.current) {
      inputRef.current.select();
    }
  }, [editingId]);

  const sorted = [...pages].sort((a, b) => a.order - b.order);

  function startRename(id: string, currentName: string) {
    setEditingId(id);
    setEditValue(currentName);
  }

  function commitRename(id: string) {
    const trimmed = editValue.trim();
    // Detect "---" or more dashes → convert to separator
    if (/^-{2,}$/.test(trimmed)) {
      convertToSeparator(id);
      setEditingId(null);
      return;
    }
    renamePage(id, editValue);
    setEditingId(null);
  }

  // ── Drag reorder ───────────────────────────────────────────────────────────
  const dropRef = useRef(dropPosition);
  useEffect(() => { dropRef.current = dropPosition; }, [dropPosition]);

  const handleDragStart = useCallback((pageId: string) => {
    return (e: React.MouseEvent) => {
      if (e.button !== 0) return;
      if ((e.target as HTMLElement).closest("button, input")) return;
      e.preventDefault();
      const startY = e.clientY;
      let didDrag = false;

      const onMove = (ev: MouseEvent) => {
        if (!didDrag && Math.abs(ev.clientY - startY) < 4) return;
        if (!didDrag) {
          didDrag = true;
          setDraggedId(pageId);
        }
        const container = containerRef.current;
        if (!container) return;

        const rows = container.querySelectorAll("[data-page-id]");
        let newDrop: typeof dropPosition = null;
        for (const row of rows) {
          const rowId = row.getAttribute("data-page-id")!;
          if (rowId === pageId) continue;
          const rect = row.getBoundingClientRect();
          if (ev.clientY < rect.top || ev.clientY > rect.bottom) continue;
          const relY = (ev.clientY - rect.top) / rect.height;
          newDrop = { targetId: rowId, pos: relY < 0.5 ? "before" : "after" };
          break;
        }
        setDropPosition(newDrop);
      };

      const onUp = () => {
        window.removeEventListener("mousemove", onMove);
        window.removeEventListener("mouseup", onUp);
        const cur = dropRef.current;
        if (didDrag && cur) {
          const sortedNow = [...usePagesStore.getState().pages].sort((a, b) => a.order - b.order);
          const filtered = sortedNow.filter((p) => p.id !== pageId);
          const targetIdx = filtered.findIndex((p) => p.id === cur.targetId);
          if (targetIdx !== -1) {
            const insertIdx = cur.pos === "before" ? targetIdx : targetIdx + 1;
            const dragPage = sortedNow.find((p) => p.id === pageId);
            if (dragPage) {
              filtered.splice(insertIdx, 0, dragPage);
              filtered.forEach((p, i) => reorderPage(p.id, i));
            }
          }
        }
        setDraggedId(null);
        setDropPosition(null);
      };

      window.addEventListener("mousemove", onMove);
      window.addEventListener("mouseup", onUp);
    };
  }, [reorderPage]);

  const { addPage: addPageAction, addSeparator } = usePagesStore();
  const canDeletePage = pages.filter((p) => !p.isSeparator).length > 1;

  return (
    <div className="py-1 px-1" ref={containerRef}>
      {sorted.map((page) => {
        // ── Separator row ──────────────────────────────────────────────────
        if (page.isSeparator) {
          return (
            <ContextMenu key={page.id}>
              <ContextMenuTrigger asChild>
                <div
                  data-page-id={page.id}
                  className={cn(
                    "group relative flex items-center h-5 px-2 select-none cursor-grab",
                    draggedId === page.id && "opacity-40",
                  )}
                  onMouseDown={handleDragStart(page.id)}
                >
                  {dropPosition?.targetId === page.id && dropPosition.pos === "before" && (
                    <div className="absolute top-0 left-0 right-0 h-0.5 bg-[var(--violet-9)] -translate-y-px z-10" />
                  )}
                  {dropPosition?.targetId === page.id && dropPosition.pos === "after" && (
                    <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[var(--violet-9)] translate-y-px z-10" />
                  )}
                  <div className="flex-1 h-px bg-[var(--mauve-6)]" />
                </div>
              </ContextMenuTrigger>
              <ContextMenuContent className="min-w-[180px]">
                <ContextMenuItem onClick={() => deletePage(page.id)} className="text-[var(--red-9)] focus:text-[var(--red-9)]">
                  <Trash2 className="w-3.5 h-3.5" />
                  Delete separator
                </ContextMenuItem>
              </ContextMenuContent>
            </ContextMenu>
          );
        }

        // ── Page row ───────────────────────────────────────────────────────
        return (
          <ContextMenu key={page.id}>
            <ContextMenuTrigger asChild>
              <div
                data-page-id={page.id}
                className={cn(
                  "group flex items-center h-7 px-2 gap-1.5 cursor-pointer rounded select-none relative",
                  activePageId === page.id
                    ? "bg-[var(--violet-3)] text-[var(--violet-11)]"
                    : "text-[var(--mauve-11)] hover:bg-[var(--mauve-3)]",
                  draggedId === page.id && "opacity-40",
                )}
                onClick={() => setActivePage(page.id)}
                onMouseDown={handleDragStart(page.id)}
              >
                {dropPosition?.targetId === page.id && dropPosition.pos === "before" && (
                  <div className="absolute top-0 left-0 right-0 h-0.5 bg-[var(--violet-9)] -translate-y-px z-10" />
                )}
                {dropPosition?.targetId === page.id && dropPosition.pos === "after" && (
                  <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-[var(--violet-9)] translate-y-px z-10" />
                )}

                <FileText className="w-3 h-3 flex-shrink-0 opacity-60" />

                {editingId === page.id ? (
                  <input
                    ref={inputRef}
                    autoFocus
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    onBlur={() => commitRename(page.id)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") commitRename(page.id);
                      if (e.key === "Escape") setEditingId(null);
                    }}
                    onClick={(e) => e.stopPropagation()}
                    className="flex-1 bg-[var(--mauve-4)] text-xs text-[var(--mauve-12)] rounded px-1 outline-none border border-[var(--violet-7)]"
                  />
                ) : (
                  <span
                    className="text-xs flex-1 truncate"
                    onDoubleClick={(e) => {
                      e.stopPropagation();
                      startRename(page.id, page.name);
                    }}
                  >
                    {page.name}
                  </span>
                )}

                {canDeletePage && (
                  <button
                    className="w-4 h-4 flex items-center justify-center text-[var(--mauve-9)] hover:text-[var(--red-9)] opacity-0 group-hover:opacity-100"
                    onClick={(e) => {
                      e.stopPropagation();
                      deletePage(page.id);
                    }}
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                )}
              </div>
            </ContextMenuTrigger>
            <ContextMenuContent className="min-w-[180px]">
              <ContextMenuItem onClick={() => startRename(page.id, page.name)}>
                <Pencil className="w-3.5 h-3.5" />
                Rename
                <ContextMenuShortcut>F2</ContextMenuShortcut>
              </ContextMenuItem>
              <ContextMenuItem onClick={() => addPageAction()}>
                <Plus className="w-3.5 h-3.5" />
                Add page below
              </ContextMenuItem>
              <ContextMenuItem onClick={() => addSeparator()}>
                Add separator
              </ContextMenuItem>
              <ContextMenuSeparator />
              <ContextMenuItem onClick={() => deletePage(page.id)} disabled={!canDeletePage} className="text-[var(--red-9)] focus:text-[var(--red-9)]">
                <Trash2 className="w-3.5 h-3.5" />
                Delete page
                <ContextMenuShortcut>⌫</ContextMenuShortcut>
              </ContextMenuItem>
            </ContextMenuContent>
          </ContextMenu>
        );
      })}
    </div>
  );
}

// ─── LayersView — vertical split ─────────────────────────────────────────────

export function LayersView() {
  const { pagesPanelHeight, setPagesPanelHeight } = useUIStore();
  const { nodes, selectedIds } = useCanvasStore();
  const { activePageId } = usePagesStore();
  const dragging = useRef(false);
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set());

  const pageNodes = nodes.filter((n) => n.pageId === activePageId);

  // Nodes that have children (expandable)
  const expandableIds = new Set<string>();
  for (const n of pageNodes) {
    if (n.parentId) expandableIds.add(n.parentId);
  }

  const anyExpanded = [...expandableIds].some((id) => !collapsed.has(id));

  function handleCollapseLayers() {
    // Find selected nodes that have children
    const selectedWithChildren = selectedIds.filter((id) => expandableIds.has(id));

    setCollapsed((prev) => {
      const next = new Set(prev);
      if (selectedWithChildren.length > 0) {
        // Collapse selected parents + their expandable descendants
        for (const id of selectedWithChildren) {
          next.add(id);
          function collapseDescendants(parentId: string) {
            for (const n of pageNodes) {
              if (n.parentId === parentId) {
                if (expandableIds.has(n.id)) next.add(n.id);
                collapseDescendants(n.id);
              }
            }
          }
          collapseDescendants(id);
        }
      } else {
        // No expandable selection → collapse all
        for (const id of expandableIds) {
          next.add(id);
        }
      }
      return next;
    });
  }

  const onDragStart = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      dragging.current = true;
      const startY = e.clientY;
      const startH = pagesPanelHeight;

      const onMove = (ev: MouseEvent) => {
        if (!dragging.current) return;
        setPagesPanelHeight(startH + ev.clientY - startY);
      };
      const onUp = () => {
        dragging.current = false;
        window.removeEventListener("mousemove", onMove);
        window.removeEventListener("mouseup", onUp);
      };
      window.addEventListener("mousemove", onMove);
      window.addEventListener("mouseup", onUp);
    },
    [pagesPanelHeight, setPagesPanelHeight]
  );

  function onDragHandleDoubleClick() {
    setPagesPanelHeight(pagesPanelHeight <= 160 ? 300 : 120);
  }

  const { addPage } = usePagesStore();

  return (
    <div className="flex flex-col h-full">
      {/* Pages section */}
      <div
        className="flex-shrink-0 flex flex-col border-b border-[var(--color-border-subtle)] overflow-hidden"
        style={{ height: pagesPanelHeight }}
      >
        {/* Pages header */}
        <div className="flex items-center justify-between h-7 px-3 flex-shrink-0 border-b border-[var(--color-border-subtle)]">
          <span className="text-[9px] font-semibold uppercase tracking-wider text-[var(--mauve-9)]">
            Pages
          </span>
          <button
            onClick={addPage}
            className="w-4 h-4 flex items-center justify-center rounded text-[var(--mauve-9)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)] transition-colors"
          >
            <Plus className="w-3 h-3" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto min-h-0">
          <PagesPanel />
        </div>
      </div>

      {/* Resize handle */}
      <div
        className="flex-shrink-0 h-1 cursor-row-resize hover:bg-[var(--violet-7)] transition-colors"
        onMouseDown={onDragStart}
        onDoubleClick={onDragHandleDoubleClick}
      />

      {/* Layers section */}
      <div className="flex flex-col flex-1 overflow-hidden min-h-0">
        <div className="flex items-center justify-between h-7 px-3 flex-shrink-0 border-b border-[var(--color-border-subtle)]">
          <span className="text-[9px] font-semibold uppercase tracking-wider text-[var(--mauve-9)]">
            Layers
          </span>
          {anyExpanded && (
            <button
              onClick={handleCollapseLayers}
              title="Collapse layers"
              className="w-4 h-4 flex items-center justify-center rounded text-[var(--mauve-9)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)] transition-colors"
            >
              <CollapseLayersIcon className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
        <ScrollArea className="flex-1 min-h-0">
          <LayersPanel collapsed={collapsed} setCollapsed={setCollapsed} />
        </ScrollArea>
      </div>
    </div>
  );
}
