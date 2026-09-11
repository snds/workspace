import { Shape } from "react-konva";
import type { Context } from "konva/lib/Context";

const GRID_COLOR = "rgba(255, 255, 255, 0.06)";
const MIN_ZOOM_FOR_GRID = 8;

interface PixelGridProps {
  stageX: number;
  stageY: number;
  zoom: number;
  width: number;
  height: number;
}

/**
 * Pixel grid overlay rendered at high zoom levels (>8x).
 * Draws 1px world-space grid lines on a Konva Shape using custom draw.
 */
export function PixelGrid({ stageX, stageY, zoom, width, height }: PixelGridProps) {
  if (zoom < MIN_ZOOM_FOR_GRID) return null;

  return (
    <Shape
      sceneFunc={(ctx: Context) => {
        const context = ctx._context;

        // Visible world range
        const worldLeft = -stageX / zoom;
        const worldTop = -stageY / zoom;
        const worldRight = (width - stageX) / zoom;
        const worldBottom = (height - stageY) / zoom;

        // Grid spacing: 1px in world space
        const startX = Math.floor(worldLeft);
        const endX = Math.ceil(worldRight);
        const startY = Math.floor(worldTop);
        const endY = Math.ceil(worldBottom);

        context.strokeStyle = GRID_COLOR;
        context.lineWidth = 1 / zoom;
        context.beginPath();

        // Vertical lines
        for (let x = startX; x <= endX; x++) {
          context.moveTo(x, worldTop);
          context.lineTo(x, worldBottom);
        }

        // Horizontal lines
        for (let y = startY; y <= endY; y++) {
          context.moveTo(worldLeft, y);
          context.lineTo(worldRight, y);
        }

        context.stroke();
      }}
      listening={false}
    />
  );
}
