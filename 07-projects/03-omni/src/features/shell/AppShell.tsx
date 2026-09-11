import { useRef, useCallback, useEffect, useState } from "react";
import { LeftPanel } from "./LeftPanel";
import { RightPanel } from "./RightPanel";
import { Canvas } from "./Canvas";
import { FloatingToolbar } from "./FloatingToolbar";
import { KeyboardShortcutsModal } from "./KeyboardShortcutsModal";
import { useUIStore } from "@/stores/ui.store";
import { useCanvasStore } from "@/stores/canvas.store";

const AUTOSAVE_KEY = "omni-autosave-nodes";
const AUTOSAVE_DELAY_MS = 1500;

export function AppShell() {
  const {
    leftPanelVisible,
    rightPanelVisible,
    leftPanelWidth,
    rightPanelWidth,
    setLeftPanelWidth,
    panelsHidden,
  } = useUIStore();

  const [autoSaveLabel, setAutoSaveLabel] = useState<"saved" | "saving">("saved");

  // Auto-save: debounced localStorage write whenever nodes change
  const nodes = useCanvasStore((s) => s.nodes);
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => {
    setAutoSaveLabel("saving");
    if (saveTimer.current) clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(() => {
      try {
        localStorage.setItem(AUTOSAVE_KEY, JSON.stringify({ nodes, savedAt: new Date().toISOString() }));
      } catch {
        // storage quota or private browsing — fail silently
      }
      setAutoSaveLabel("saved");
    }, AUTOSAVE_DELAY_MS);
    return () => { if (saveTimer.current) clearTimeout(saveTimer.current); };
  }, [nodes]);

  const showLeft  = leftPanelVisible  && !panelsHidden;
  const showRight = rightPanelVisible && !panelsHidden;

  // Drag-to-resize for left panel
  const leftDragging  = useRef(false);

  const onLeftResizeStart = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    leftDragging.current = true;
    const startX = e.clientX;
    const startWidth = leftPanelWidth;

    const onMove = (ev: MouseEvent) => {
      if (!leftDragging.current) return;
      setLeftPanelWidth(startWidth + ev.clientX - startX);
    };
    const onUp = () => {
      leftDragging.current = false;
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
  }, [leftPanelWidth, setLeftPanelWidth]);

  return (
    <div className="flex h-screen overflow-hidden bg-[var(--color-surface-0)]">
      <KeyboardShortcutsModal />

      {/* Left Panel */}
      {showLeft && (
        <div
          className="flex-shrink-0 flex relative"
          style={{ width: leftPanelWidth }}
        >
          <LeftPanel autoSaveLabel={autoSaveLabel} />
          <div
            className="absolute right-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-[var(--violet-7)] transition-colors z-10"
            onMouseDown={onLeftResizeStart}
          />
        </div>
      )}

      {/* Canvas (fills remaining space, toolbar floats inside) */}
      <div className="flex-1 overflow-hidden min-w-0 relative">
        <Canvas />
        <FloatingToolbar />
      </div>

      {/* Right Panel — fixed width, no resize */}
      {showRight && (
        <div
          className="flex-shrink-0"
          style={{ width: rightPanelWidth }}
        >
          <RightPanel />
        </div>
      )}
    </div>
  );
}
