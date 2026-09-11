import { Rect } from "react-konva";
import type { DrawingRect } from "@/types/canvas";
import { useUIStore } from "@/stores/ui.store";

interface DrawingPreviewProps {
  rect: DrawingRect;
  zoom: number;
}

export function DrawingPreview({ rect, zoom }: DrawingPreviewProps) {
  const { activeTool } = useUIStore();

  const isMarquee = activeTool === "select";
  const strokeColor = isMarquee
    ? "#6366f1"
    : activeTool === "frame"
      ? "#6366f1"
      : activeTool === "text"
        ? "#3b82f6"
        : "#a855f7";
  const fill = isMarquee ? "rgba(99,102,241,0.04)" : "rgba(99,102,241,0.08)";

  return (
    <Rect
      x={rect.x}
      y={rect.y}
      width={rect.width}
      height={rect.height}
      stroke={strokeColor}
      strokeWidth={1 / zoom}
      fill={fill}
      listening={false}
      dash={[4 / zoom, 2 / zoom]}
    />
  );
}
