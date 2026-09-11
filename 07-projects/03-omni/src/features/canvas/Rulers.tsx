import { useRef, useEffect } from "react";

const RULER_SIZE = 20;

interface RulersProps {
  stageX: number;
  stageY: number;
  zoom: number;
  width: number;
  height: number;
}

// ─── Tick interval selection ──────────────────────────────────────────────────

const NICE_INTERVALS = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000];

function getTickInterval(zoom: number): { major: number; minor: number } {
  const targetScreenPx = 100;
  const worldPxPerTick = targetScreenPx / zoom;

  let major = NICE_INTERVALS[NICE_INTERVALS.length - 1];
  for (const interval of NICE_INTERVALS) {
    if (interval >= worldPxPerTick * 0.5) {
      major = interval;
      break;
    }
  }

  const minor = major >= 10 ? major / 10 : major / 5;
  return { major, minor };
}

// ─── Colors ───────────────────────────────────────────────────────────────────

const BG = "#1e1c20";
const TICK_COLOR = "#4a4550";
const LABEL_COLOR = "#8a8590";
const BORDER_COLOR = "#2e2c30";

// ─── Component ────────────────────────────────────────────────────────────────

export function Rulers({ stageX, stageY, zoom, width, height }: RulersProps) {
  const hCanvasRef = useRef<HTMLCanvasElement>(null);
  const vCanvasRef = useRef<HTMLCanvasElement>(null);

  // ── Draw horizontal ruler ─────────────────────────────────────────────────
  useEffect(() => {
    const canvas = hCanvasRef.current;
    if (!canvas) return;

    const dpr = window.devicePixelRatio || 1;
    const w = width - RULER_SIZE;
    const h = RULER_SIZE;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = `${w}px`;
    canvas.style.height = `${h}px`;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.scale(dpr, dpr);

    // Background
    ctx.fillStyle = BG;
    ctx.fillRect(0, 0, w, h);

    // Bottom border
    ctx.strokeStyle = BORDER_COLOR;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, h - 0.5);
    ctx.lineTo(w, h - 0.5);
    ctx.stroke();

    const { major, minor } = getTickInterval(zoom);

    // Visible world range
    const worldStart = -stageX / zoom;
    const worldEnd = (w - stageX) / zoom;

    // Align to minor interval
    const firstMinor = Math.floor(worldStart / minor) * minor;

    ctx.textBaseline = "top";
    ctx.font = "9px Inter, system-ui, sans-serif";

    for (let worldVal = firstMinor; worldVal <= worldEnd; worldVal += minor) {
      const screenX = worldVal * zoom + stageX;
      if (screenX < 0 || screenX > w) continue;

      const isMajor = Math.abs(worldVal % major) < 0.001 || Math.abs(worldVal % major - major) < 0.001;
      const tickHeight = isMajor ? h * 0.55 : h * 0.25;

      ctx.strokeStyle = TICK_COLOR;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(Math.round(screenX) + 0.5, h);
      ctx.lineTo(Math.round(screenX) + 0.5, h - tickHeight);
      ctx.stroke();

      if (isMajor) {
        ctx.fillStyle = LABEL_COLOR;
        const label = Math.round(worldVal).toString();
        ctx.fillText(label, Math.round(screenX) + 3, 2);
      }
    }
  }, [stageX, zoom, width]);

  // ── Draw vertical ruler ───────────────────────────────────────────────────
  useEffect(() => {
    const canvas = vCanvasRef.current;
    if (!canvas) return;

    const dpr = window.devicePixelRatio || 1;
    const w = RULER_SIZE;
    const h = height - RULER_SIZE;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = `${w}px`;
    canvas.style.height = `${h}px`;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.scale(dpr, dpr);

    // Background
    ctx.fillStyle = BG;
    ctx.fillRect(0, 0, w, h);

    // Right border
    ctx.strokeStyle = BORDER_COLOR;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(w - 0.5, 0);
    ctx.lineTo(w - 0.5, h);
    ctx.stroke();

    const { major, minor } = getTickInterval(zoom);

    // Visible world range
    const worldStart = -stageY / zoom;
    const worldEnd = (h - stageY) / zoom;

    const firstMinor = Math.floor(worldStart / minor) * minor;

    ctx.font = "9px Inter, system-ui, sans-serif";

    for (let worldVal = firstMinor; worldVal <= worldEnd; worldVal += minor) {
      const screenY = worldVal * zoom + stageY;
      if (screenY < 0 || screenY > h) continue;

      const isMajor = Math.abs(worldVal % major) < 0.001 || Math.abs(worldVal % major - major) < 0.001;
      const tickWidth = isMajor ? w * 0.55 : w * 0.25;

      ctx.strokeStyle = TICK_COLOR;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(w, Math.round(screenY) + 0.5);
      ctx.lineTo(w - tickWidth, Math.round(screenY) + 0.5);
      ctx.stroke();

      if (isMajor) {
        ctx.save();
        ctx.fillStyle = LABEL_COLOR;
        ctx.translate(2, Math.round(screenY) + 3);
        ctx.rotate(-Math.PI / 2);
        const label = Math.round(worldVal).toString();
        ctx.textBaseline = "top";
        ctx.fillText(label, 0, 0);
        ctx.restore();
      }
    }
  }, [stageY, zoom, height]);

  return (
    <>
      {/* Corner square */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: RULER_SIZE,
          height: RULER_SIZE,
          background: BG,
          borderRight: `1px solid ${BORDER_COLOR}`,
          borderBottom: `1px solid ${BORDER_COLOR}`,
          zIndex: 12,
        }}
      />
      {/* Horizontal ruler */}
      <canvas
        ref={hCanvasRef}
        style={{
          position: "absolute",
          top: 0,
          left: RULER_SIZE,
          zIndex: 11,
          pointerEvents: "none",
        }}
      />
      {/* Vertical ruler */}
      <canvas
        ref={vCanvasRef}
        style={{
          position: "absolute",
          top: RULER_SIZE,
          left: 0,
          zIndex: 11,
          pointerEvents: "none",
        }}
      />
    </>
  );
}

export { RULER_SIZE };
