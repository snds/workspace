import { useRef, useCallback } from "react";
import { useCanvasStore, type TransformModifiers } from "@/stores/canvas.store";
import { useUIStore } from "@/stores/ui.store";
import type { CanvasNode } from "@/types/canvas";
import { findSnaps, findResizeSnaps, type Bounds, type SnapResult } from "./snap/snapEngine";
import { interactionState } from "@/core/renderer";

// ─── Types ────────────────────────────────────────────────────────────────────

export type HandlePosition =
  | "top-left"    | "top"    | "top-right"
  | "left"                   | "right"
  | "bottom-left" | "bottom" | "bottom-right";

export type TransformType = "resize" | "rotate" | "move";

interface TransformState {
  type: TransformType;
  /** Handle position for resize, undefined for move/rotate */
  handle?: HandlePosition;
  /** Initial world-space pointer position */
  startWorld: { x: number; y: number };
  /** Snapshot of each selected node's bounds at transform start */
  initialBounds: Record<string, { x: number; y: number; width: number; height: number; rotation: number }>;
  /** For move/rotate: IDs of descendant nodes that should also transform */
  descendantBounds?: Record<string, { x: number; y: number; rotation?: number }>;
  /** For rotation: center of the selection bounding box */
  rotationCenter?: { x: number; y: number };
  /** For rotation: initial angle from center to pointer */
  startAngle?: number;
  /** For rotation: initial rotations per node */
  initialRotations?: Record<string, number>;
  /** Snap candidates captured at transform start */
  candidates?: Bounds[];
}

// ─── Direction multipliers for resize handles ─────────────────────────────────

const HANDLE_DIR: Record<HandlePosition, { dx: number; dy: number }> = {
  "top-left":     { dx: -1, dy: -1 },
  "top":          { dx:  0, dy: -1 },
  "top-right":    { dx:  1, dy: -1 },
  "left":         { dx: -1, dy:  0 },
  "right":        { dx:  1, dy:  0 },
  "bottom-left":  { dx: -1, dy:  1 },
  "bottom":       { dx:  0, dy:  1 },
  "bottom-right": { dx:  1, dy:  1 },
};

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useTransform() {
  const { setModifiers, applyModifiers, setSnapGuides, setTransformPreview } = useCanvasStore();
  const state = useRef<TransformState | null>(null);

  /** Begin a resize transform on a specific handle. */
  const startResize = useCallback(
    (handle: HandlePosition, worldX: number, worldY: number, selectedNodes: CanvasNode[], candidates?: Bounds[]) => {
      const initialBounds: TransformState["initialBounds"] = {};
      for (const n of selectedNodes) {
        initialBounds[n.id] = { x: n.x, y: n.y, width: n.width, height: n.height, rotation: n.rotation };
      }
      state.current = {
        type: "resize",
        handle,
        startWorld: { x: worldX, y: worldY },
        initialBounds,
        candidates,
      };

      // Mirror into mutable InteractionState for the renderer abstraction
      const snapshots = selectedNodes.map((n) => ({
        nodeId: n.id,
        startX: n.x,
        startY: n.y,
        startWidth: n.width,
        startHeight: n.height,
        startRotation: n.rotation,
      }));
      interactionState.beginMulti("resizing", snapshots);
    },
    [],
  );

  /** Begin a rotation transform. */
  const startRotate = useCallback(
    (worldX: number, worldY: number, selectedNodes: CanvasNode[], allNodes: CanvasNode[], candidates?: Bounds[]) => {
      const initialBounds: TransformState["initialBounds"] = {};
      const initialRotations: Record<string, number> = {};
      let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
      for (const n of selectedNodes) {
        initialBounds[n.id] = { x: n.x, y: n.y, width: n.width, height: n.height, rotation: n.rotation };
        initialRotations[n.id] = n.rotation;
        minX = Math.min(minX, n.x);
        minY = Math.min(minY, n.y);
        maxX = Math.max(maxX, n.x + n.width);
        maxY = Math.max(maxY, n.y + n.height);
      }
      const cx = (minX + maxX) / 2;
      const cy = (minY + maxY) / 2;
      const startAngle = Math.atan2(worldY - cy, worldX - cx) * (180 / Math.PI);

      // Collect all descendant positions/rotations so they rotate with their parents
      const selectedSet = new Set(selectedNodes.map(n => n.id));
      const descendantBounds: Record<string, { x: number; y: number; rotation?: number }> = {};
      function collectDescendants(parentId: string) {
        for (const n of allNodes) {
          if (n.parentId === parentId && !selectedSet.has(n.id)) {
            descendantBounds[n.id] = { x: n.x, y: n.y, rotation: n.rotation };
            collectDescendants(n.id);
          }
        }
      }
      for (const n of selectedNodes) {
        collectDescendants(n.id);
      }

      state.current = {
        type: "rotate",
        startWorld: { x: worldX, y: worldY },
        initialBounds,
        descendantBounds,
        rotationCenter: { x: cx, y: cy },
        startAngle,
        initialRotations,
        candidates,
      };

      // Mirror into mutable InteractionState for the renderer abstraction
      const snapshots = selectedNodes.map((n) => ({
        nodeId: n.id,
        startX: n.x,
        startY: n.y,
        startWidth: n.width,
        startHeight: n.height,
        startRotation: n.rotation,
      }));
      interactionState.beginMulti("rotating", snapshots);
    },
    [],
  );

  /** Begin a move transform (drag) for selected nodes + their descendants. */
  const startMove = useCallback(
    (worldX: number, worldY: number, selectedNodes: CanvasNode[], allNodes: CanvasNode[], candidates?: Bounds[]) => {
      const initialBounds: TransformState["initialBounds"] = {};
      for (const n of selectedNodes) {
        initialBounds[n.id] = { x: n.x, y: n.y, width: n.width, height: n.height, rotation: n.rotation };
      }

      // Collect all descendant positions so they move with their parents
      const selectedSet = new Set(selectedNodes.map(n => n.id));
      const descendantBounds: Record<string, { x: number; y: number }> = {};
      function collectDescendants(parentId: string) {
        for (const n of allNodes) {
          if (n.parentId === parentId && !selectedSet.has(n.id)) {
            descendantBounds[n.id] = { x: n.x, y: n.y };
            collectDescendants(n.id);
          }
        }
      }
      for (const n of selectedNodes) {
        collectDescendants(n.id);
      }

      state.current = {
        type: "move",
        startWorld: { x: worldX, y: worldY },
        initialBounds,
        descendantBounds,
        candidates,
      };

      // Mirror into mutable InteractionState for the renderer abstraction
      const snapshots = selectedNodes.map((n) => ({
        nodeId: n.id,
        startX: n.x,
        startY: n.y,
        startWidth: n.width,
        startHeight: n.height,
        startRotation: n.rotation,
      }));
      interactionState.beginMulti("dragging", snapshots);
    },
    [],
  );

  /** Continue the transform during pointer move. */
  const continueTransform = useCallback(
    (worldX: number, worldY: number, shiftKey: boolean) => {
      const s = state.current;
      if (!s) return;

      const mods: TransformModifiers = {};
      let guides: SnapResult[] = [];

      if (s.type === "resize" && s.handle) {
        const dir = HANDLE_DIR[s.handle];
        const deltaX = worldX - s.startWorld.x;
        const deltaY = worldY - s.startWorld.y;

        for (const [id, initial] of Object.entries(s.initialBounds)) {
          let newX = initial.x;
          let newY = initial.y;
          let newW = initial.width;
          let newH = initial.height;

          // Apply resize based on handle direction
          if (dir.dx === -1) {
            newX = initial.x + deltaX;
            newW = initial.width - deltaX;
          } else if (dir.dx === 1) {
            newW = initial.width + deltaX;
          }

          if (dir.dy === -1) {
            newY = initial.y + deltaY;
            newH = initial.height - deltaY;
          } else if (dir.dy === 1) {
            newH = initial.height + deltaY;
          }

          // Shift key: proportional resize
          if (shiftKey && (dir.dx !== 0 && dir.dy !== 0)) {
            const scaleX = newW / initial.width;
            const scaleY = newH / initial.height;
            const uniformScale = Math.max(scaleX, scaleY);
            newW = initial.width * uniformScale;
            newH = initial.height * uniformScale;
            if (dir.dx === -1) newX = initial.x + initial.width - newW;
            if (dir.dy === -1) newY = initial.y + initial.height - newH;
          }

          // Enforce minimum size
          if (newW < 1) { if (dir.dx === -1) newX += newW - 1; newW = 1; }
          if (newH < 1) { if (dir.dy === -1) newY += newH - 1; newH = 1; }

          mods[id] = { x: newX, y: newY, width: newW, height: newH };
        }

        // ── Snap during resize ──────────────────────────────────────────────────
        const snapEnabled = useUIStore.getState().snapEnabled;
        if (snapEnabled && s.candidates && s.candidates.length > 0) {
          const zoom = useUIStore.getState().zoom;
          const tolerance = 10 / zoom;

          // Compute combined bounds of all modified nodes
          let cMinX = Infinity, cMinY = Infinity, cMaxX = -Infinity, cMaxY = -Infinity;
          for (const mod of Object.values(mods)) {
            const mx = mod.x as number;
            const my = mod.y as number;
            const mw = mod.width as number;
            const mh = mod.height as number;
            cMinX = Math.min(cMinX, mx);
            cMinY = Math.min(cMinY, my);
            cMaxX = Math.max(cMaxX, mx + mw);
            cMaxY = Math.max(cMaxY, my + mh);
          }
          const combinedBounds: Bounds = {
            x: cMinX, y: cMinY,
            width: cMaxX - cMinX, height: cMaxY - cMinY,
          };

          const snap = findResizeSnaps(combinedBounds, dir.dx, dir.dy, s.candidates, tolerance);

          if (snap.dx !== 0 || snap.dy !== 0) {
            for (const mod of Object.values(mods)) {
              if (dir.dx === 1) { (mod as Record<string, number>).width += snap.dx; }
              else if (dir.dx === -1) { (mod as Record<string, number>).x += snap.dx; (mod as Record<string, number>).width -= snap.dx; }
              if (dir.dy === 1) { (mod as Record<string, number>).height += snap.dy; }
              else if (dir.dy === -1) { (mod as Record<string, number>).y += snap.dy; (mod as Record<string, number>).height -= snap.dy; }
            }
          }

          guides = snap.guides;
        }
      } else if (s.type === "rotate" && s.rotationCenter && s.startAngle !== undefined && s.initialRotations) {
        const cx = s.rotationCenter.x;
        const cy = s.rotationCenter.y;
        const currentAngle = Math.atan2(worldY - cy, worldX - cx) * (180 / Math.PI);
        let deltaAngle = currentAngle - s.startAngle;

        // Shift key: snap to 15-degree increments
        if (shiftKey) {
          deltaAngle = Math.round(deltaAngle / 15) * 15;
        }

        const rad = deltaAngle * (Math.PI / 180);
        const cosA = Math.cos(rad);
        const sinA = Math.sin(rad);

        for (const [id, initialRotation] of Object.entries(s.initialRotations)) {
          mods[id] = { rotation: (initialRotation + deltaAngle) % 360 };
        }

        // Rotate descendants around the same center
        if (s.descendantBounds) {
          for (const [id, initial] of Object.entries(s.descendantBounds)) {
            const dx = initial.x - cx;
            const dy = initial.y - cy;
            const newX = cx + dx * cosA - dy * sinA;
            const newY = cy + dx * sinA + dy * cosA;
            mods[id] = {
              x: newX,
              y: newY,
              rotation: ((initial.rotation ?? 0) + deltaAngle) % 360,
            };
          }
        }
      } else if (s.type === "move") {
        let dx = worldX - s.startWorld.x;
        let dy = worldY - s.startWorld.y;

        // Shift key: constrain to horizontal or vertical axis
        if (shiftKey) {
          if (Math.abs(dx) > Math.abs(dy)) dy = 0;
          else dx = 0;
        }

        // Apply move delta to all selected nodes
        for (const [id, initial] of Object.entries(s.initialBounds)) {
          mods[id] = { x: initial.x + dx, y: initial.y + dy };
        }

        // Snap
        const snapEnabled = useUIStore.getState().snapEnabled;
        if (snapEnabled && s.candidates && s.candidates.length > 0) {
          const zoom = useUIStore.getState().zoom;
          const tolerance = 10 / zoom;

          // Compute combined bounds of all selected nodes after move
          let cMinX = Infinity, cMinY = Infinity, cMaxX = -Infinity, cMaxY = -Infinity;
          for (const [id] of Object.entries(s.initialBounds)) {
            const initial = s.initialBounds[id];
            const mx = initial.x + dx;
            const my = initial.y + dy;
            cMinX = Math.min(cMinX, mx);
            cMinY = Math.min(cMinY, my);
            cMaxX = Math.max(cMaxX, mx + initial.width);
            cMaxY = Math.max(cMaxY, my + initial.height);
          }
          const combinedBounds: Bounds = {
            x: cMinX, y: cMinY,
            width: cMaxX - cMinX, height: cMaxY - cMinY,
          };

          const snap = findSnaps(combinedBounds, s.candidates, tolerance);

          if (snap.dx !== 0 || snap.dy !== 0) {
            for (const mod of Object.values(mods)) {
              (mod as Record<string, number>).x += snap.dx;
              (mod as Record<string, number>).y += snap.dy;
            }
            dx += snap.dx;
            dy += snap.dy;
          }
          guides = snap.guides;
        }

        // Move descendants too
        if (s.descendantBounds) {
          for (const [id, initial] of Object.entries(s.descendantBounds)) {
            mods[id] = { x: initial.x + dx, y: initial.y + dy };
          }
        }
      }

      // Single atomic store update — avoids split-frame glitches from separate
      // setSnapGuides() + setModifiers() calls.
      setTransformPreview(mods, guides);

      // Mirror deltas into the mutable InteractionState for the renderer abstraction
      const dx2 = worldX - s.startWorld.x;
      const dy2 = worldY - s.startWorld.y;
      interactionState.update({ dx: dx2, dy: dy2 });
      interactionState.updateModifiers(shiftKey, false, false);
    },
    [setTransformPreview],
  );

  /** End the transform — commit modifiers to the store (also clears snapGuides). */
  const endTransform = useCallback(() => {
    if (!state.current) return;
    applyModifiers(); // also clears snapGuides
    state.current = null;
    // End the mutable interaction mirror
    interactionState.end();
  }, [applyModifiers]);

  /** Cancel transform without committing. */
  const cancelTransform = useCallback(() => {
    state.current = null;
    setModifiers(null);
    setSnapGuides([]);
    // End the mutable interaction mirror
    interactionState.end();
  }, [setModifiers, setSnapGuides]);

  /** Whether a transform is currently active. */
  const isTransforming = useCallback(() => state.current !== null, []);

  return {
    startResize,
    startRotate,
    startMove,
    continueTransform,
    endTransform,
    cancelTransform,
    isTransforming,
  };
}
