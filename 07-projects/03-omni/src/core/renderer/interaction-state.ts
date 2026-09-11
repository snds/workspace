/**
 * Mutable state for canvas interactions (drag, resize, rotate).
 * This bypasses React/Zustand for 60fps performance.
 * Values are committed to the Zustand store when the interaction ends.
 *
 * Same pattern as Figma: mutable C++ state for interactions, JS state for document.
 */

export interface InteractionSnapshot {
  nodeId: string;
  startX: number;
  startY: number;
  startWidth: number;
  startHeight: number;
  startRotation: number;
}

export type InteractionType = "idle" | "dragging" | "resizing" | "rotating" | "drawing" | "panning" | "selecting";

export interface InteractionDelta {
  dx: number;
  dy: number;
  dWidth: number;
  dHeight: number;
  dRotation: number;
}

class InteractionState {
  /** Current interaction type */
  type: InteractionType = "idle";

  /** Snapshot of node state at interaction start */
  snapshot: InteractionSnapshot | null = null;

  /** Current deltas during interaction */
  delta: InteractionDelta = { dx: 0, dy: 0, dWidth: 0, dHeight: 0, dRotation: 0 };

  /** Multi-select: snapshots for all nodes being transformed */
  multiSnapshots: InteractionSnapshot[] = [];

  /** Mouse position in canvas coordinates */
  canvasMouseX: number = 0;
  canvasMouseY: number = 0;

  /** Mouse position in screen coordinates */
  screenMouseX: number = 0;
  screenMouseY: number = 0;

  /** Whether Shift is held (constrain proportions, snap to 45deg, etc.) */
  shiftKey: boolean = false;
  /** Whether Alt/Option is held (resize from center, duplicate on drag, etc.) */
  altKey: boolean = false;
  /** Whether Cmd/Ctrl is held (deep select, etc.) */
  metaKey: boolean = false;

  /** Resize handle being dragged */
  resizeHandle: string | null = null; // "nw" | "n" | "ne" | "e" | "se" | "s" | "sw" | "w"

  /** Selection box (rubber band) */
  selectionBox: { x: number; y: number; width: number; height: number } | null = null;

  /** Subscribers -- called on every frame during interaction */
  private listeners: Set<() => void> = new Set();

  /** Start a new interaction */
  begin(type: InteractionType, snapshot: InteractionSnapshot): void {
    this.type = type;
    this.snapshot = snapshot;
    this.delta = { dx: 0, dy: 0, dWidth: 0, dHeight: 0, dRotation: 0 };
  }

  /** Start a multi-node interaction */
  beginMulti(type: InteractionType, snapshots: InteractionSnapshot[]): void {
    this.type = type;
    this.multiSnapshots = snapshots;
    this.snapshot = snapshots[0] ?? null;
    this.delta = { dx: 0, dy: 0, dWidth: 0, dHeight: 0, dRotation: 0 };
  }

  /** Update deltas during interaction */
  update(delta: Partial<InteractionDelta>): void {
    Object.assign(this.delta, delta);
    this.notify();
  }

  /** Update mouse position */
  updateMouse(screenX: number, screenY: number, canvasX: number, canvasY: number): void {
    this.screenMouseX = screenX;
    this.screenMouseY = screenY;
    this.canvasMouseX = canvasX;
    this.canvasMouseY = canvasY;
  }

  /** Update modifier keys */
  updateModifiers(shift: boolean, alt: boolean, meta: boolean): void {
    this.shiftKey = shift;
    this.altKey = alt;
    this.metaKey = meta;
  }

  /** End the interaction and return final values */
  end(): { snapshot: InteractionSnapshot | null; delta: InteractionDelta; multiSnapshots: InteractionSnapshot[] } {
    const result = {
      snapshot: this.snapshot,
      delta: { ...this.delta },
      multiSnapshots: [...this.multiSnapshots],
    };
    this.type = "idle";
    this.snapshot = null;
    this.delta = { dx: 0, dy: 0, dWidth: 0, dHeight: 0, dRotation: 0 };
    this.multiSnapshots = [];
    this.selectionBox = null;
    this.resizeHandle = null;
    this.notify();
    return result;
  }

  /** Get the current position of a node during interaction */
  getCurrentPosition(nodeId: string): { x: number; y: number; width: number; height: number; rotation: number } | null {
    const snap = this.snapshot?.nodeId === nodeId
      ? this.snapshot
      : this.multiSnapshots.find(s => s.nodeId === nodeId);

    if (!snap) return null;

    return {
      x: snap.startX + this.delta.dx,
      y: snap.startY + this.delta.dy,
      width: snap.startWidth + this.delta.dWidth,
      height: snap.startHeight + this.delta.dHeight,
      rotation: snap.startRotation + this.delta.dRotation,
    };
  }

  /** Subscribe to state changes (for requestAnimationFrame loop) */
  subscribe(listener: () => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify(): void {
    for (const listener of this.listeners) {
      listener();
    }
  }
}

/** Singleton interaction state -- shared across the canvas system */
export const interactionState = new InteractionState();
export type { InteractionState };
