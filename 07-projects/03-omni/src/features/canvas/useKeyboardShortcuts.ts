import { useEffect, useRef } from "react";
import { useCanvasStore } from "@/stores/canvas.store";
import { useUIStore, type ToolMode } from "@/stores/ui.store";
import { usePagesStore } from "@/stores/pages.store";

const NUDGE_AMOUNT = 1;
const NUDGE_LARGE = 10;

/** Compute bounding box of a set of nodes. */
function nodeBBox(nodes: Array<{ x: number; y: number; width: number; height: number }>) {
  return {
    minX: Math.min(...nodes.map((n) => n.x)),
    minY: Math.min(...nodes.map((n) => n.y)),
    maxX: Math.max(...nodes.map((n) => n.x + n.width)),
    maxY: Math.max(...nodes.map((n) => n.y + n.height)),
  };
}

/** Compute zoom + stage position so a bbox fills the viewport. */
function zoomToRect(
  rect: { minX: number; minY: number; maxX: number; maxY: number },
  stageW: number,
  stageH: number,
  padding = 40,
) {
  const rw = rect.maxX - rect.minX;
  const rh = rect.maxY - rect.minY;
  if (rw <= 0 || rh <= 0) return null;
  const newZoom = Math.min((stageW - padding * 2) / rw, (stageH - padding * 2) / rh, 32);
  return {
    zoom: Math.max(0.05, newZoom),
    stageX: (stageW - rw * newZoom) / 2 - rect.minX * newZoom,
    stageY: (stageH - rh * newZoom) / 2 - rect.minY * newZoom,
  };
}

export function useKeyboardShortcuts(
  _containerRef: React.RefObject<HTMLDivElement | null>,
  stageSize: { width: number; height: number },
) {
  const {
    deleteNodes, updateNodes, duplicateNodes,
    clearSelection, selectNodes, reorderNodes,
    groupNodes, ungroupNodes, frameNodes, flipNodes,
    undo, redo,
  } = useCanvasStore();
  const {
    activeTool, setActiveTool, zoomIn, zoomOut, resetZoom, setZoom,
    toggleLeftPanel, toggleRightPanel, setActiveLeftPanel,
    toggleKeyboardShortcuts,
  } = useUIStore();

  // Tracks the last non-hand tool so Space release can restore it.
  const lastNonHandToolRef = useRef<ToolMode>("select");
  useEffect(() => {
    if (activeTool !== "hand") lastNonHandToolRef.current = activeTool;
  }, [activeTool]);

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA") return;

      const cmd  = e.metaKey || e.ctrlKey;
      const alt  = e.altKey;
      const shift= e.shiftKey;
      const nativeCtrl = e.ctrlKey; // physical Ctrl (for ⌃⌥H etc.)
      const key  = e.key;

      // ─── Reserved Cmd shortcuts — prevent VS Code / browser from acting on them
      // even when the feature is not yet implemented. Without this, e.g. ⌘S
      // would reach VS Code and trigger a save dialog, etc.
      if (cmd) {
        const BLOCKED_CMD: Record<string, boolean> = {
          r: true,       // rename  (also blocks browser reload)
          f: true,       // find
          s: true,       // save
          p: true,       // (⇧⌘P pixel preview)
          k: true,       // actions (⌘K)
          j: true,       // join selection
          J: true,       // smooth join
          b: true,       // detach instance (⌥⌘B)
          ";": true,     // various
        };
        if (BLOCKED_CMD[key]) {
          e.preventDefault();
          // If we have an active implementation for this combo it will return
          // before reaching here; if not, just swallow the event.
        }
      }

      // ─── Undo / Redo  ⌘Z / ⌘⇧Z ──────────────────────────────────────────────
      if (cmd && !alt && key === "z") {
        e.preventDefault();
        if (shift) redo(); else undo();
        return;
      }

      // ─── Copy / Cut / Paste  ⌘C / ⌘X / ⌘V ─────────────────────────────────
      if (cmd && !alt && !shift) {
        if (key === "c") {
          e.preventDefault();
          const { selectedIds, copyNodes } = useCanvasStore.getState();
          if (selectedIds.length > 0) copyNodes(selectedIds);
          return;
        }
        if (key === "x") {
          e.preventDefault();
          const { selectedIds, cutNodes } = useCanvasStore.getState();
          if (selectedIds.length > 0) cutNodes(selectedIds);
          return;
        }
        if (key === "v") {
          e.preventDefault();
          useCanvasStore.getState().pasteNodes();
          return;
        }
      }

      // ─── Tools (no modifier) ─────────────────────────────────────────────────
      if (!cmd && !alt) {
        switch (key) {
          case "v": setActiveTool("select"); return;
          case "h": setActiveTool("hand");   return;
          case "f": case "F": setActiveTool("frame");  return;
          case "r": case "R": setActiveTool("shape");  return;
          case "t": case "T": setActiveTool("text");   return;
          case "p":
            if (!shift) { setActiveTool("pen"); return; }
            e.preventDefault(); return; // ⇧P pencil — reserved
          case " ":
            e.preventDefault();
            setActiveTool("hand");
            return;
          case "Escape": {
            const cur = useUIStore.getState().activeTool;
            if (cur !== "select") { setActiveTool("select"); return; }
            const { selectedIds, nodes } = useCanvasStore.getState();
            if (selectedIds.length === 1) {
              const nd = nodes.find((n) => n.id === selectedIds[0]);
              if (nd?.parentId) { selectNodes([nd.parentId]); return; }
            }
            clearSelection();
            return;
          }
        }
      }

      // ─── Show/Hide UI  ⌘\ ───────────────────────────────────────────────────
      if (cmd && key === "\\") {
        e.preventDefault();
        toggleLeftPanel(); toggleRightPanel();
        return;
      }

      // ─── Keyboard shortcuts panel  ? ─────────────────────────────────────────
      if (!cmd && !alt && key === "?") {
        e.preventDefault();
        toggleKeyboardShortcuts();
        return;
      }

      // ─── Panel tabs  ⌥1 / ⌥2 / ⌥3 ───────────────────────────────────────────
      if (alt && !cmd && !shift) {
        if (key === "1") { e.preventDefault(); setActiveLeftPanel("design"); return; }
        if (key === "2") { e.preventDefault(); setActiveLeftPanel("assets"); return; }
        if (key === "3") { e.preventDefault(); setActiveLeftPanel("tokens"); return; }
      }

      // ─── Zoom  ⌘+ / ⌘- / ⌘0 ─────────────────────────────────────────────────
      if (cmd && !alt && !shift) {
        if (key === "+" || key === "=") { e.preventDefault(); zoomIn();    return; }
        if (key === "-")               { e.preventDefault(); zoomOut();   return; }
        if (key === "0")               { e.preventDefault(); resetZoom(); return; }
      }

      // ⇧1 — zoom to fit all
      if (shift && !cmd && !alt && key === "1") {
        e.preventDefault();
        const { nodes } = useCanvasStore.getState();
        const { activePageId } = usePagesStore.getState();
        const pg = nodes.filter((n) => n.pageId === activePageId);
        if (pg.length > 0) {
          const r = zoomToRect(nodeBBox(pg), stageSize.width, stageSize.height);
          if (r) { setZoom(r.zoom); useCanvasStore.getState().setStagePosition(r.stageX, r.stageY); }
        }
        return;
      }

      // ⇧2 — zoom to selection
      if (shift && !cmd && !alt && key === "2") {
        e.preventDefault();
        const { nodes, selectedIds } = useCanvasStore.getState();
        const sel = nodes.filter((n) => selectedIds.includes(n.id));
        if (sel.length > 0) {
          const r = zoomToRect(nodeBBox(sel), stageSize.width, stageSize.height);
          if (r) { setZoom(r.zoom); useCanvasStore.getState().setStagePosition(r.stageX, r.stageY); }
        }
        return;
      }

      // N / ⇧N — zoom to next / prev frame
      if (!cmd && !alt && (key === "n" || key === "N")) {
        e.preventDefault();
        const { nodes, selectedIds } = useCanvasStore.getState();
        const { activePageId } = usePagesStore.getState();
        const frames = nodes
          .filter((n) => n.pageId === activePageId && n.type === "frame" && !n.parentId)
          .sort((a, b) => a.x - b.x || a.y - b.y);
        if (frames.length === 0) return;
        const cur = frames.findIndex((f) => selectedIds.includes(f.id));
        const next = shift
          ? (cur <= 0 ? frames.length - 1 : cur - 1)
          : (cur >= frames.length - 1 ? 0 : cur + 1);
        const target = frames[next];
        selectNodes([target.id]);
        const r = zoomToRect(nodeBBox([target]), stageSize.width, stageSize.height);
        if (r) { setZoom(r.zoom); useCanvasStore.getState().setStagePosition(r.stageX, r.stageY); }
        return;
      }

      // ─── ⌘A — select all ─────────────────────────────────────────────────────
      if (cmd && !alt && !shift && key === "a") {
        e.preventDefault();
        const { nodes } = useCanvasStore.getState();
        const { activePageId } = usePagesStore.getState();
        selectNodes(nodes.filter((n) => n.pageId === activePageId).map((n) => n.id));
        return;
      }

      // ─── Enter — select first child ──────────────────────────────────────────
      if (!cmd && !alt && !shift && key === "Enter") {
        const { selectedIds, nodes } = useCanvasStore.getState();
        const { activePageId } = usePagesStore.getState();
        if (selectedIds.length === 1) {
          const child = nodes
            .filter((n) => n.pageId === activePageId && n.parentId === selectedIds[0])
            .sort((a, b) => a.order - b.order)[0];
          if (child) { e.preventDefault(); selectNodes([child.id]); return; }
        }
      }

      // ─── \ — select parent ───────────────────────────────────────────────────
      if (!cmd && !alt && !shift && key === "\\") {
        const { selectedIds, nodes } = useCanvasStore.getState();
        if (selectedIds.length === 1) {
          const nd = nodes.find((n) => n.id === selectedIds[0]);
          if (nd?.parentId) { e.preventDefault(); selectNodes([nd.parentId]); return; }
        }
      }

      // ─── Tab / ⇧Tab — next / prev sibling ────────────────────────────────────
      if (!cmd && !alt && key === "Tab") {
        const { selectedIds, nodes } = useCanvasStore.getState();
        const { activePageId } = usePagesStore.getState();
        if (selectedIds.length === 1) {
          const nd = nodes.find((n) => n.id === selectedIds[0]);
          const siblings = nodes
            .filter((n) => n.pageId === activePageId && n.parentId === (nd?.parentId ?? null))
            .sort((a, b) => a.order - b.order);
          const idx = siblings.findIndex((n) => n.id === selectedIds[0]);
          if (idx !== -1) {
            e.preventDefault();
            const next = shift
              ? siblings[(idx - 1 + siblings.length) % siblings.length]
              : siblings[(idx + 1) % siblings.length];
            selectNodes([next.id]);
            return;
          }
        }
      }

      // ─── Group / ungroup / frame ──────────────────────────────────────────────
      if (cmd && !alt && !shift && key === "g") {
        e.preventDefault();
        const { selectedIds } = useCanvasStore.getState();
        if (selectedIds.length > 0) groupNodes(selectedIds);
        return;
      }
      if (cmd && !alt && shift && key === "G") {
        e.preventDefault();
        const { selectedIds } = useCanvasStore.getState();
        if (selectedIds.length > 0) ungroupNodes(selectedIds);
        return;
      }
      // ⌘⌫ — also ungroup
      if (cmd && !alt && !shift && (key === "Backspace" || key === "Delete")) {
        e.preventDefault();
        const { selectedIds } = useCanvasStore.getState();
        if (selectedIds.length > 0) ungroupNodes(selectedIds);
        return;
      }
      if (cmd && alt && !shift && key === "g") {
        e.preventDefault();
        const { selectedIds } = useCanvasStore.getState();
        if (selectedIds.length > 0) frameNodes(selectedIds);
        return;
      }

      // ─── Show/Hide  ⇧⌘H ─────────────────────────────────────────────────────
      if (cmd && !alt && shift && key === "H") {
        e.preventDefault();
        const { selectedIds, nodes } = useCanvasStore.getState();
        updateNodes(selectedIds.map((id) => {
          const n = nodes.find((nd) => nd.id === id);
          return { id, visible: !(n?.visible ?? true) };
        }));
        return;
      }

      // ─── Lock/Unlock  ⇧⌘L ───────────────────────────────────────────────────
      if (cmd && !alt && shift && key === "L") {
        e.preventDefault();
        const { selectedIds, nodes } = useCanvasStore.getState();
        updateNodes(selectedIds.map((id) => {
          const n = nodes.find((nd) => nd.id === id);
          return { id, locked: !(n?.locked ?? false) };
        }));
        return;
      }

      // ─── Z-order ──────────────────────────────────────────────────────────────
      if (!alt && key === "]") {
        e.preventDefault();
        const { selectedIds, nodes } = useCanvasStore.getState();
        const { activePageId } = usePagesStore.getState();
        const pg = nodes.filter((n) => n.pageId === activePageId).sort((a, b) => a.order - b.order);
        if (cmd) {
          // ⌘] — bring forward (one step each)
          const patches: Array<{ id: string; order: number }> = [];
          for (const id of selectedIds) {
            const nd = pg.find((n) => n.id === id);
            if (!nd) continue;
            const above = pg.find((n) => n.order > nd.order && !selectedIds.includes(n.id));
            if (above) patches.push({ id, order: above.order + 0.5 });
          }
          if (patches.length > 0) reorderNodes(patches);
        } else {
          // ] — bring to front
          const max = Math.max(...pg.map((n) => n.order), 0);
          reorderNodes(selectedIds.map((id, i) => ({ id, order: max + i + 1 })));
        }
        return;
      }
      if (!alt && key === "[") {
        e.preventDefault();
        const { selectedIds, nodes } = useCanvasStore.getState();
        const { activePageId } = usePagesStore.getState();
        const pg = nodes.filter((n) => n.pageId === activePageId).sort((a, b) => a.order - b.order);
        if (cmd) {
          // ⌘[ — send backward (one step each)
          const patches: Array<{ id: string; order: number }> = [];
          for (const id of selectedIds) {
            const nd = pg.find((n) => n.id === id);
            if (!nd) continue;
            const below = [...pg].reverse().find((n) => n.order < nd.order && !selectedIds.includes(n.id));
            if (below) patches.push({ id, order: below.order - 0.5 });
          }
          if (patches.length > 0) reorderNodes(patches);
        } else {
          // [ — send to back
          const min = Math.min(...pg.map((n) => n.order), 0);
          reorderNodes(selectedIds.map((id, i) => ({ id, order: min - selectedIds.length + i })));
        }
        return;
      }

      // ─── Align  ⌥A/D/W/S/H/V ─────────────────────────────────────────────────
      if (alt && !cmd && !shift) {
        const { selectedIds, nodes } = useCanvasStore.getState();
        if (selectedIds.length >= 1) {
          const sel = nodes.filter((n) => selectedIds.includes(n.id));
          const bb = nodeBBox(sel);
          let patches: Array<{ id: string; x?: number; y?: number }> | null = null;
          if      (key === "a") patches = sel.map((n) => ({ id: n.id, x: bb.minX }));
          else if (key === "d") patches = sel.map((n) => ({ id: n.id, x: bb.maxX - n.width }));
          else if (key === "w") patches = sel.map((n) => ({ id: n.id, y: bb.minY }));
          else if (key === "s") patches = sel.map((n) => ({ id: n.id, y: bb.maxY - n.height }));
          else if (key === "h") patches = sel.map((n) => ({ id: n.id, x: (bb.minX + bb.maxX) / 2 - n.width / 2 }));
          else if (key === "v") patches = sel.map((n) => ({ id: n.id, y: (bb.minY + bb.maxY) / 2 - n.height / 2 }));
          if (patches) { e.preventDefault(); updateNodes(patches); return; }
        }
      }

      // ─── Distribute  ⌃⌥H / ⌃⌥V ──────────────────────────────────────────────
      if (nativeCtrl && alt && !cmd && !shift) {
        const { selectedIds, nodes } = useCanvasStore.getState();
        const sel = nodes.filter((n) => selectedIds.includes(n.id));
        if (sel.length >= 3) {
          if (key === "h") {
            e.preventDefault();
            const sorted = [...sel].sort((a, b) => a.x - b.x);
            const totalW = sorted.reduce((s, n) => s + n.width, 0);
            const span = sorted[sorted.length - 1].x + sorted[sorted.length - 1].width - sorted[0].x;
            const gap = (span - totalW) / (sorted.length - 1);
            let cursor = sorted[0].x + sorted[0].width;
            updateNodes(sorted.slice(1).map((n) => { const x = cursor + gap; cursor = x + n.width; return { id: n.id, x }; }));
            return;
          }
          if (key === "v") {
            e.preventDefault();
            const sorted = [...sel].sort((a, b) => a.y - b.y);
            const totalH = sorted.reduce((s, n) => s + n.height, 0);
            const span = sorted[sorted.length - 1].y + sorted[sorted.length - 1].height - sorted[0].y;
            const gap = (span - totalH) / (sorted.length - 1);
            let cursor = sorted[0].y + sorted[0].height;
            updateNodes(sorted.slice(1).map((n) => { const y = cursor + gap; cursor = y + n.height; return { id: n.id, y }; }));
            return;
          }
        }
      }

      // ─── Edit actions ─────────────────────────────────────────────────────────
      const { selectedIds: ids } = useCanvasStore.getState();

      // Delete / Backspace (plain, no cmd)
      if (!cmd && (key === "Delete" || key === "Backspace")) {
        if (ids.length > 0) { e.preventDefault(); deleteNodes(ids); }
        return;
      }

      // ⌘D — duplicate
      if (cmd && !alt && !shift && key === "d") {
        e.preventDefault();
        if (ids.length > 0) duplicateNodes(ids);
        return;
      }

      // ─── Transform ────────────────────────────────────────────────────────────

      // ⇧H — flip horizontal
      if (!cmd && !alt && shift && key === "H") {
        e.preventDefault();
        if (ids.length > 0) flipNodes(ids, "x");
        return;
      }
      // ⇧V — flip vertical
      if (!cmd && !alt && shift && key === "V") {
        e.preventDefault();
        if (ids.length > 0) flipNodes(ids, "y");
        return;
      }

      // 1–9 — set opacity 10–90%;  0 — 100%
      if (!cmd && !alt && !shift && ids.length > 0) {
        const digit = parseInt(key, 10);
        if (!Number.isNaN(digit)) {
          e.preventDefault();
          updateNodes(ids.map((id) => ({ id, opacity: digit === 0 ? 1 : digit / 10 })));
          return;
        }
      }

      // ─── Arrow nudge ─────────────────────────────────────────────────────────
      if (ids.length === 0) return;
      const { nodes } = useCanvasStore.getState();
      const amount = shift ? NUDGE_LARGE : NUDGE_AMOUNT;
      let dx = 0, dy = 0;
      if (key === "ArrowLeft")  dx = -amount;
      else if (key === "ArrowRight") dx = amount;
      else if (key === "ArrowUp")    dy = -amount;
      else if (key === "ArrowDown")  dy = amount;
      if (dx !== 0 || dy !== 0) {
        e.preventDefault();
        updateNodes(ids.map((id) => {
          const n = nodes.find((nd) => nd.id === id);
          return n ? { id, x: n.x + dx, y: n.y + dy } : { id };
        }));
      }
    }

    function onKeyUp(e: KeyboardEvent) {
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA") return;
      if (e.key === " ") setActiveTool(lastNonHandToolRef.current);
    }

    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("keyup", onKeyUp);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("keyup", onKeyUp);
    };
  // Re-register when stageSize changes so zoom-to-fit uses fresh dimensions.
  // All store actions are stable references from zustand; no other deps needed.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stageSize.width, stageSize.height]);
}
