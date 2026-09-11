import { useRef } from "react";
import { CanvasStage } from "@/features/canvas/CanvasStage";
import { addComponentToCanvas } from "@/features/canvas/componentBlueprints";
import { useCanvasStore } from "@/stores/canvas.store";
import { useUIStore } from "@/stores/ui.store";

interface ComponentDragData {
  componentType: string;
  name: string;
  width: number;
  height: number;
}

export function Canvas() {
  const addNode = useCanvasStore((s) => s.addNode);
  const selectNodes = useCanvasStore((s) => s.selectNodes);
  const { zoom } = useUIStore();
  const { stageX, stageY } = useCanvasStore();
  const containerRef = useRef<HTMLDivElement>(null);

  function onDragOver(e: React.DragEvent) {
    if (e.dataTransfer.types.includes("application/omni-component")) {
      e.preventDefault();
      e.dataTransfer.dropEffect = "copy";
    }
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    const raw = e.dataTransfer.getData("application/omni-component");
    if (!raw) return;

    let data: ComponentDragData;
    try {
      data = JSON.parse(raw);
    } catch {
      return;
    }

    const rect = containerRef.current?.getBoundingClientRect();
    if (!rect) return;

    // Convert screen coords → canvas world coords
    const x = (e.clientX - rect.left - stageX) / zoom;
    const y = (e.clientY - rect.top - stageY) / zoom;

    addComponentToCanvas(data.name, Math.round(x), Math.round(y), addNode, selectNodes);
  }

  return (
    <div
      ref={containerRef}
      className="w-full h-full"
      onDragOver={onDragOver}
      onDrop={onDrop}
    >
      <CanvasStage />
    </div>
  );
}
