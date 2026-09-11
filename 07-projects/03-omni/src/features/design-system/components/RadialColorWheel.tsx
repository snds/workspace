import { useRef, useCallback, useEffect, useState, useMemo } from "react";
import { hexToHsl, hslToHex, isValidHex, bestForeground } from "@/lib/color";
import { hexToOklch, oklchToHex } from "@/lib/colorSpaces";
import type { HarmonyMode } from "@/lib/colorHarmony";

type Slot = "primary" | "secondary" | "accent";

interface RadialColorWheelProps {
  brandColors: {
    primary: string;
    secondary: string | null;
    accent: string | null;
  };
  harmonyMode: HarmonyMode;
  onColorChange: (slot: Slot, hex: string) => void;
}

const SLOT_LABELS: Record<Slot, string> = { primary: "P", secondary: "S", accent: "A" };

// Wheel geometry
const TOTAL_SIZE = 184;
const CENTER = TOTAL_SIZE / 2;
const BRIGHTNESS_RIM = 12;
const HUE_RING_WIDTH = 24;
const OUTER_RADIUS = TOTAL_SIZE / 2;
const HUE_RING_OUTER = OUTER_RADIUS - BRIGHTNESS_RIM;
const HUE_RING_INNER = HUE_RING_OUTER - HUE_RING_WIDTH;
const HUE_RING_MID = (HUE_RING_OUTER + HUE_RING_INNER) / 2;

function hueToAngle(hue: number): number {
  // CSS conic-gradient starts at top (12 o'clock) and goes clockwise.
  // We map hue 0 → -90° (right in standard math coords = top in CSS).
  // For marker positioning (math coords): angle in radians where 0° hue = top.
  return ((hue - 90) * Math.PI) / 180;
}

function angleToCssHue(angleRad: number): number {
  // Convert from math angle (radians) to hue degrees
  let hue = (angleRad * 180) / Math.PI + 90;
  return ((hue % 360) + 360) % 360;
}

function polarToCartesian(cx: number, cy: number, r: number, angleRad: number) {
  return {
    x: cx + r * Math.cos(angleRad),
    y: cy + r * Math.sin(angleRad),
  };
}

interface MarkerInfo {
  slot: Slot;
  label: string;
  hex: string;
  hue: number;
  size: number;
  draggable: boolean;
}

function buildMarkers(
  brandColors: RadialColorWheelProps["brandColors"],
  harmonyMode: HarmonyMode,
): MarkerInfo[] {
  const out: MarkerInfo[] = [];
  const isFreeform = harmonyMode === "freeform";

  const pHsl = hexToHsl(brandColors.primary);
  out.push({
    slot: "primary",
    label: SLOT_LABELS.primary,
    hex: brandColors.primary,
    hue: pHsl ? pHsl[0] : 0,
    size: 20,
    draggable: true, // always draggable
  });

  if (brandColors.secondary && isValidHex(brandColors.secondary)) {
    const sHsl = hexToHsl(brandColors.secondary);
    out.push({
      slot: "secondary",
      label: SLOT_LABELS.secondary,
      hex: brandColors.secondary,
      hue: sHsl ? sHsl[0] : 0,
      size: 16,
      draggable: isFreeform,
    });
  }

  if (brandColors.accent && isValidHex(brandColors.accent)) {
    const aHsl = hexToHsl(brandColors.accent);
    out.push({
      slot: "accent",
      label: SLOT_LABELS.accent,
      hex: brandColors.accent,
      hue: aHsl ? aHsl[0] : 0,
      size: 16,
      draggable: isFreeform,
    });
  }

  return out;
}

export function RadialColorWheel({
  brandColors,
  harmonyMode,
  onColorChange,
}: RadialColorWheelProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const draggingSlot = useRef<Slot | null>(null);
  const draggingBrightness = useRef(false);
  const [, forceRender] = useState(0);

  const markers = useMemo(
    () => buildMarkers(brandColors, harmonyMode),
    [brandColors, harmonyMode],
  );

  // Current primary brightness (OKLCH L)
  const primaryOklch = useMemo(
    () => hexToOklch(brandColors.primary),
    [brandColors.primary],
  );
  const primaryL = primaryOklch ? primaryOklch[0] : 0.55;

  // Convert pointer position to hue
  const pointerToHue = useCallback((clientX: number, clientY: number): number => {
    const el = containerRef.current;
    if (!el) return 0;
    const rect = el.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const dx = clientX - cx;
    const dy = clientY - cy;
    const angleRad = Math.atan2(dy, dx);
    return angleToCssHue(angleRad);
  }, []);

  // Convert pointer position to brightness (0-1)
  const pointerToBrightness = useCallback((clientX: number, clientY: number): number => {
    const el = containerRef.current;
    if (!el) return 0.55;
    const rect = el.getBoundingClientRect();
    const cx = rect.left + rect.width / 2;
    const cy = rect.top + rect.height / 2;
    const dx = clientX - cx;
    const dy = clientY - cy;
    const angleRad = Math.atan2(dy, dx);
    // Map: top (-PI/2) = dark (0.15), bottom (PI/2) = light (0.95)
    // Normalize angle from -PI to PI → 0 to 1
    const normalized = (angleRad + Math.PI / 2) / Math.PI;
    const clamped = Math.max(0, Math.min(1, normalized));
    return 0.15 + clamped * 0.8; // L range: 0.15 to 0.95
  }, []);

  const updateColorFromHue = useCallback(
    (slot: Slot, hue: number) => {
      const currentHex = brandColors[slot];
      if (!currentHex) return;
      const hsl = hexToHsl(currentHex);
      const s = hsl ? hsl[1] : 70;
      const l = hsl ? hsl[2] : 50;
      onColorChange(slot, hslToHex(Math.round(hue), s, l));
    },
    [brandColors, onColorChange],
  );

  const updateBrightness = useCallback(
    (newL: number) => {
      const oklch = hexToOklch(brandColors.primary);
      if (!oklch) return;
      const [, C, H] = oklch;
      onColorChange("primary", oklchToHex(newL, C, H));
    },
    [brandColors.primary, onColorChange],
  );

  // Pointer event handlers
  useEffect(() => {
    const onMove = (e: PointerEvent) => {
      if (draggingBrightness.current) {
        const newL = pointerToBrightness(e.clientX, e.clientY);
        updateBrightness(newL);
        return;
      }
      if (draggingSlot.current) {
        const hue = pointerToHue(e.clientX, e.clientY);
        updateColorFromHue(draggingSlot.current, hue);
      }
    };
    const onUp = () => {
      if (draggingSlot.current || draggingBrightness.current) {
        draggingSlot.current = null;
        draggingBrightness.current = false;
        forceRender((n) => n + 1);
      }
    };
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
    return () => {
      window.removeEventListener("pointermove", onMove);
      window.removeEventListener("pointerup", onUp);
    };
  }, [pointerToHue, pointerToBrightness, updateColorFromHue, updateBrightness]);

  // Click on hue ring to add secondary/accent
  const handleRingClick = useCallback(
    (e: React.PointerEvent) => {
      const el = containerRef.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;
      const dx = e.clientX - cx;
      const dy = e.clientY - cy;
      const dist = Math.sqrt(dx * dx + dy * dy);

      // Scale to SVG coords
      const scale = TOTAL_SIZE / rect.width;
      const distScaled = dist * scale;

      // Check if click is on brightness rim
      if (distScaled >= HUE_RING_OUTER && distScaled <= OUTER_RADIUS) {
        draggingBrightness.current = true;
        const newL = pointerToBrightness(e.clientX, e.clientY);
        updateBrightness(newL);
        forceRender((n) => n + 1);
        return;
      }

      // Check if click is on hue ring
      if (distScaled < HUE_RING_INNER || distScaled > HUE_RING_OUTER) return;

      // In harmony modes, only allow primary drag
      if (harmonyMode !== "freeform") return;

      // Determine which empty slot to fill
      let target: Slot | null = null;
      if (brandColors.secondary === null) target = "secondary";
      else if (brandColors.accent === null) target = "accent";
      if (!target) return;

      const hue = pointerToHue(e.clientX, e.clientY);
      const pHsl = hexToHsl(brandColors.primary);
      const s = pHsl ? pHsl[1] : 70;
      const l = pHsl ? pHsl[2] : 50;
      onColorChange(target, hslToHex(Math.round(hue), s, l));

      // Start dragging
      draggingSlot.current = target;
      forceRender((n) => n + 1);
    },
    [brandColors, harmonyMode, onColorChange, pointerToHue, pointerToBrightness, updateBrightness],
  );

  const handleMarkerPointerDown = useCallback(
    (e: React.PointerEvent, slot: Slot, draggable: boolean) => {
      e.stopPropagation();
      if (!draggable) return;
      draggingSlot.current = slot;
      forceRender((n) => n + 1);
    },
    [],
  );

  // Build brightness ring gradient
  const primaryHue = primaryOklch ? primaryOklch[2] : 280;
  const primaryC = primaryOklch ? primaryOklch[1] : 0.18;
  const brightnessGradientStops = useMemo(() => {
    const stops: string[] = [];
    const numStops = 16;
    for (let i = 0; i <= numStops; i++) {
      const t = i / numStops;
      const L = 0.15 + t * 0.8;
      const hex = oklchToHex(L, primaryC, primaryHue);
      // Angle: starts at top (-90° CSS = 0deg conic), dark at top, light at bottom
      const deg = Math.round(t * 180);
      stops.push(`${hex} ${deg}deg`);
    }
    // Mirror for the right side (bottom back to top)
    for (let i = numStops; i >= 0; i--) {
      const t = i / numStops;
      const L = 0.15 + t * 0.8;
      const hex = oklchToHex(L, primaryC, primaryHue);
      const deg = Math.round(180 + (numStops - i) / numStops * 180);
      stops.push(`${hex} ${deg}deg`);
    }
    return stops.join(", ");
  }, [primaryHue, primaryC]);

  // Brightness knob position
  const brightnessAngle = useMemo(() => {
    // Reverse: L → angle on the left half of the circle
    const t = (primaryL - 0.15) / 0.8;
    // Angle: top = t=0 → -90°, bottom = t=1 → +90°
    return (-90 + t * 180) * Math.PI / 180;
  }, [primaryL]);
  const brightnessKnobR = (HUE_RING_OUTER + OUTER_RADIUS) / 2;
  const brightnessKnob = polarToCartesian(CENTER, CENTER, brightnessKnobR, brightnessAngle);

  // Harmony connection lines (SVG paths)
  const harmonyLines = useMemo(() => {
    if (harmonyMode === "freeform" || markers.length < 2) return null;

    const lines: { x1: number; y1: number; x2: number; y2: number }[] = [];
    const primary = markers[0];
    const pAngle = hueToAngle(primary.hue);
    const pPos = polarToCartesian(CENTER, CENTER, HUE_RING_MID, pAngle);

    for (let i = 1; i < markers.length; i++) {
      const m = markers[i];
      const mAngle = hueToAngle(m.hue);
      const mPos = polarToCartesian(CENTER, CENTER, HUE_RING_MID, mAngle);
      lines.push({ x1: pPos.x, y1: pPos.y, x2: mPos.x, y2: mPos.y });
    }

    return lines;
  }, [markers, harmonyMode]);

  return (
    <div className="flex flex-col gap-1.5 items-center">
      <label className="text-[10px] font-semibold text-[var(--mauve-10)] uppercase tracking-wider self-start">
        Color Wheel
      </label>
      <div
        ref={containerRef}
        onPointerDown={handleRingClick}
        className="relative select-none touch-none"
        style={{ width: TOTAL_SIZE, height: TOTAL_SIZE }}
      >
        {/* Brightness outer rim */}
        <div
          className="absolute inset-0 rounded-full"
          style={{
            background: `conic-gradient(from 270deg, ${brightnessGradientStops})`,
          }}
        />

        {/* Hue ring */}
        <div
          className="absolute rounded-full"
          style={{
            top: BRIGHTNESS_RIM,
            left: BRIGHTNESS_RIM,
            width: TOTAL_SIZE - BRIGHTNESS_RIM * 2,
            height: TOTAL_SIZE - BRIGHTNESS_RIM * 2,
            background: "conic-gradient(from 270deg, #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff, #ff0000)",
          }}
        />

        {/* Inner circle (center fill) */}
        <div
          className="absolute rounded-full border border-[var(--mauve-6)]"
          style={{
            top: BRIGHTNESS_RIM + HUE_RING_WIDTH,
            left: BRIGHTNESS_RIM + HUE_RING_WIDTH,
            width: TOTAL_SIZE - (BRIGHTNESS_RIM + HUE_RING_WIDTH) * 2,
            height: TOTAL_SIZE - (BRIGHTNESS_RIM + HUE_RING_WIDTH) * 2,
            background: brandColors.primary,
          }}
        />

        {/* SVG overlay for harmony lines and markers */}
        <svg
          className="absolute inset-0"
          width={TOTAL_SIZE}
          height={TOTAL_SIZE}
          style={{ pointerEvents: "none" }}
        >
          {/* Harmony connection lines */}
          {harmonyLines?.map((line, i) => (
            <line
              key={i}
              x1={line.x1}
              y1={line.y1}
              x2={line.x2}
              y2={line.y2}
              stroke="rgba(255,255,255,0.5)"
              strokeWidth={1.5}
              strokeDasharray={harmonyMode === "freeform" ? "3,3" : "none"}
            />
          ))}
        </svg>

        {/* Brightness knob */}
        <div
          onPointerDown={(e) => {
            e.stopPropagation();
            draggingBrightness.current = true;
            forceRender((n) => n + 1);
          }}
          className="absolute rounded-full cursor-grab active:cursor-grabbing"
          style={{
            width: 10,
            height: 10,
            left: brightnessKnob.x - 5,
            top: brightnessKnob.y - 5,
            background: brandColors.primary,
            boxShadow: "0 0 0 2px var(--mauve-1), 0 0 0 3px rgba(0,0,0,0.4)",
            zIndex: draggingBrightness.current ? 40 : 15,
            pointerEvents: "auto",
          }}
        />

        {/* Color markers */}
        {markers.map((m) => {
          const angle = hueToAngle(m.hue);
          const pos = polarToCartesian(CENTER, CENTER, HUE_RING_MID, angle);
          const isDragging = draggingSlot.current === m.slot;
          const fg = bestForeground(m.hex);

          return (
            <div
              key={m.slot}
              onPointerDown={(e) => handleMarkerPointerDown(e, m.slot, m.draggable)}
              className="absolute flex items-center justify-center rounded-full"
              style={{
                width: m.size,
                height: m.size,
                left: pos.x - m.size / 2,
                top: pos.y - m.size / 2,
                background: m.hex,
                boxShadow: "0 0 0 2px var(--mauve-1), 0 0 0 3.5px rgba(0,0,0,0.4)",
                zIndex: isDragging ? 30 : m.slot === "primary" ? 20 : 10,
                cursor: m.draggable ? "grab" : "default",
                transition: isDragging ? "none" : "left 0.15s ease, top 0.15s ease",
                pointerEvents: "auto",
              }}
            >
              <span
                className="text-[7px] font-bold select-none pointer-events-none leading-none"
                style={{ color: fg }}
              >
                {m.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
