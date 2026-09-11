import { Line } from "react-konva";
import type { SnapResult } from "./snapEngine";

const GUIDE_COLOR = "#f43f5e"; // rose-500

interface SnapGuidesProps {
  guides: SnapResult[];
  zoom: number;
}

/**
 * Renders snap guide lines on the controls overlay layer.
 * Shows thin colored lines at snap alignment positions.
 */
export function SnapGuides({ guides, zoom }: SnapGuidesProps) {
  if (guides.length === 0) return null;

  const strokeW = 1 / zoom;

  return (
    <>
      {guides.map((guide, i) => {
        if (guide.axis === "x") {
          // Vertical guide line at x = guidePosition
          return (
            <Line
              key={`snap-${i}`}
              points={[guide.guidePosition, guide.guideStart, guide.guidePosition, guide.guideEnd]}
              stroke={GUIDE_COLOR}
              strokeWidth={strokeW}
              dash={[4 / zoom, 4 / zoom]}
              listening={false}
            />
          );
        }
        // Horizontal guide line at y = guidePosition
        return (
          <Line
            key={`snap-${i}`}
            points={[guide.guideStart, guide.guidePosition, guide.guideEnd, guide.guidePosition]}
            stroke={GUIDE_COLOR}
            strokeWidth={strokeW}
            dash={[4 / zoom, 4 / zoom]}
            listening={false}
          />
        );
      })}
    </>
  );
}
