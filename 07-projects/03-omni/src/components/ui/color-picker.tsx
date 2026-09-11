import { useState, useRef, useCallback, useEffect } from "react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { ChevronDown, Pipette } from "lucide-react";

// ─── Color math ───────────────────────────────────────────────────────────────

function clamp(v: number, lo: number, hi: number) {
  return Math.max(lo, Math.min(hi, v));
}

function hsvToRgb(h: number, s: number, v: number): [number, number, number] {
  s /= 100; v /= 100;
  const i = Math.floor(h / 60) % 6;
  const f = h / 60 - Math.floor(h / 60);
  const p = v * (1 - s), q = v * (1 - f * s), t = v * (1 - (1 - f) * s);
  const rows: [number, number, number][] = [
    [v, t, p], [q, v, p], [p, v, t], [p, q, v], [t, p, v], [v, p, q],
  ];
  const [r, g, b] = rows[i];
  return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
}

function rgbToHsv(r: number, g: number, b: number): [number, number, number] {
  r /= 255; g /= 255; b /= 255;
  const max = Math.max(r, g, b), min = Math.min(r, g, b), d = max - min;
  let h = 0;
  const s = max === 0 ? 0 : d / max;
  const v = max;
  if (d !== 0) {
    switch (max) {
      case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
      case g: h = ((b - r) / d + 2) / 6; break;
      case b: h = ((r - g) / d + 4) / 6; break;
    }
  }
  return [Math.round(h * 360), Math.round(s * 100), Math.round(v * 100)];
}

function hexToRgb(hex: string): [number, number, number] | null {
  const clean = hex.replace("#", "");
  if (clean.length !== 6) return null;
  const r = parseInt(clean.slice(0, 2), 16);
  const g = parseInt(clean.slice(2, 4), 16);
  const b = parseInt(clean.slice(4, 6), 16);
  return isNaN(r + g + b) ? null : [r, g, b];
}

function rgbToHex(r: number, g: number, b: number): string {
  return (
    "#" +
    [r, g, b]
      .map((v) => clamp(Math.round(v), 0, 255).toString(16).padStart(2, "0"))
      .join("")
  );
}

function hsvToHex(h: number, s: number, v: number): string {
  const [r, g, b] = hsvToRgb(h, s, v);
  return rgbToHex(r, g, b);
}

function parseToHsv(hex: string): [number, number, number] {
  const rgb = hexToRgb(hex);
  return rgb ? rgbToHsv(...rgb) : [0, 0, 100];
}

// ─── Checkered pattern (transparent swatch background) ───────────────────────

const CHECKER =
  "repeating-conic-gradient(#888 0% 25%, #ccc 0% 50%) 0 0 / 8px 8px";

// ─── Saturation/Value gradient area ──────────────────────────────────────────

function SVArea({
  hue,
  saturation,
  value,
  onChange,
}: {
  hue: number;
  saturation: number;
  value: number;
  onChange(s: number, v: number): void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);

  const pick = useCallback(
    (e: PointerEvent | React.PointerEvent) => {
      const el = ref.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const s = clamp((e.clientX - rect.left) / rect.width, 0, 1);
      const v = 1 - clamp((e.clientY - rect.top) / rect.height, 0, 1);
      onChange(Math.round(s * 100), Math.round(v * 100));
    },
    [onChange],
  );

  useEffect(() => {
    const move = (e: PointerEvent) => { if (dragging.current) pick(e); };
    const up = () => { dragging.current = false; };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
    return () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
    };
  }, [pick]);

  return (
    <div
      ref={ref}
      className="relative w-full rounded-sm cursor-crosshair select-none overflow-hidden"
      style={{ height: 160 }}
      onPointerDown={(e) => {
        dragging.current = true;
        ref.current?.setPointerCapture(e.pointerId);
        pick(e);
      }}
    >
      <div className="absolute inset-0" style={{ background: `hsl(${hue}, 100%, 50%)` }} />
      <div className="absolute inset-0" style={{ background: "linear-gradient(to right, #fff, transparent)" }} />
      <div className="absolute inset-0" style={{ background: "linear-gradient(to bottom, transparent, #000)" }} />
      <div
        className="absolute w-3 h-3 rounded-full pointer-events-none -translate-x-1/2 -translate-y-1/2"
        style={{
          left: `${saturation}%`,
          top: `${100 - value}%`,
          boxShadow: "0 0 0 2px #fff, 0 0 0 3px rgba(0,0,0,0.35)",
        }}
      />
    </div>
  );
}

// ─── Hue slider ───────────────────────────────────────────────────────────────

function HueSlider({ hue, onChange }: { hue: number; onChange(h: number): void }) {
  const ref = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);

  const pick = useCallback(
    (e: PointerEvent | React.PointerEvent) => {
      const el = ref.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const x = clamp((e.clientX - rect.left) / rect.width, 0, 1);
      onChange(Math.round(x * 360));
    },
    [onChange],
  );

  useEffect(() => {
    const move = (e: PointerEvent) => { if (dragging.current) pick(e); };
    const up = () => { dragging.current = false; };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
    return () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
    };
  }, [pick]);

  return (
    <div
      ref={ref}
      className="relative h-3 rounded-full cursor-pointer select-none"
      style={{
        background:
          "linear-gradient(to right, #ff0000 0%, #ffff00 17%, #00ff00 33%, #00ffff 50%, #0000ff 67%, #ff00ff 83%, #ff0000 100%)",
      }}
      onPointerDown={(e) => {
        dragging.current = true;
        ref.current?.setPointerCapture(e.pointerId);
        pick(e);
      }}
    >
      <div
        className="absolute top-1/2 w-4 h-4 rounded-full bg-white pointer-events-none -translate-x-1/2 -translate-y-1/2"
        style={{
          left: `${(hue / 360) * 100}%`,
          boxShadow: "0 0 0 1px rgba(0,0,0,0.25), 0 1px 4px rgba(0,0,0,0.3)",
        }}
      />
    </div>
  );
}

// ─── Alpha slider ─────────────────────────────────────────────────────────────

function AlphaSlider({
  alpha,
  hex,
  onChange,
}: {
  alpha: number;
  hex: string;
  onChange(a: number): void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const dragging = useRef(false);

  const pick = useCallback(
    (e: PointerEvent | React.PointerEvent) => {
      const el = ref.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const x = clamp((e.clientX - rect.left) / rect.width, 0, 1);
      onChange(Math.round(x * 100));
    },
    [onChange],
  );

  useEffect(() => {
    const move = (e: PointerEvent) => { if (dragging.current) pick(e); };
    const up = () => { dragging.current = false; };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
    return () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
    };
  }, [pick]);

  return (
    <div
      ref={ref}
      className="relative h-3 rounded-full cursor-pointer select-none"
      onPointerDown={(e) => {
        dragging.current = true;
        ref.current?.setPointerCapture(e.pointerId);
        pick(e);
      }}
    >
      {/* Checkerboard track */}
      <div className="absolute inset-0 rounded-full" style={{ background: CHECKER }} />
      {/* Color gradient overlay */}
      <div
        className="absolute inset-0 rounded-full"
        style={{ background: `linear-gradient(to right, transparent, ${hex})` }}
      />
      {/* Thumb */}
      <div
        className="absolute top-1/2 w-4 h-4 rounded-full bg-white pointer-events-none -translate-x-1/2 -translate-y-1/2"
        style={{
          left: `${alpha}%`,
          boxShadow: "0 0 0 1px rgba(0,0,0,0.25), 0 1px 4px rgba(0,0,0,0.3)",
        }}
      />
    </div>
  );
}

// ─── ColorPicker ──────────────────────────────────────────────────────────────

export interface ColorPickerProps {
  /** Label shown above the trigger (full-row mode only) */
  label?: string;
  value: string | null;
  onChange(hex: string | null): void;
  /** Alpha 0–100, defaults to 100 */
  alpha?: number;
  onAlphaChange?: (a: number) => void;
  /** When false, renders only the small swatch trigger with no inline hex field */
  showInlineHex?: boolean;
}

export function ColorPicker({
  label,
  value,
  onChange,
  alpha = 100,
  onAlphaChange,
  showInlineHex = true,
}: ColorPickerProps) {
  const DEFAULT_HEX = "#6e56cf";
  const resolvedHex = value ?? DEFAULT_HEX;

  const [hsv, setHsv] = useState<[number, number, number]>(() => parseToHsv(resolvedHex));
  const [hexInput, setHexInput] = useState(resolvedHex.replace("#", "").toUpperCase());
  const [alphaValue, setAlphaValue] = useState(alpha);

  // Sync external value → internal state (avoid feedback loops)
  useEffect(() => {
    const target = (value ?? DEFAULT_HEX).toLowerCase();
    const current = hsvToHex(hsv[0], hsv[1], hsv[2]).toLowerCase();
    if (target !== current) {
      const parsed = parseToHsv(target);
      setHsv(parsed);
      setHexInput(target.replace("#", "").toUpperCase());
    }
  }, [value]); // intentionally omit hsv

  useEffect(() => {
    setAlphaValue(alpha);
  }, [alpha]);

  const applyHsv = (h: number, s: number, v: number) => {
    const newHex = hsvToHex(h, s, v);
    setHsv([h, s, v]);
    setHexInput(newHex.replace("#", "").toUpperCase());
    onChange(newHex);
  };

  const commitHex = (raw: string) => {
    const clean = raw.replace("#", "");
    if (clean.length === 6) {
      const rgb = hexToRgb("#" + clean);
      if (rgb) {
        const [h, s, v] = rgbToHsv(...rgb);
        setHsv([h, s, v]);
        onChange("#" + clean.toLowerCase());
      }
    }
    setHexInput(clean.toUpperCase());
  };

  const handleAlpha = (a: number) => {
    setAlphaValue(a);
    onAlphaChange?.(a);
  };

  const previewHex = hsvToHex(hsv[0], hsv[1], hsv[2]);
  const swatchBg = value ? value : "transparent";

  // ─── Shared picker popup ──────────────────────────────────────────────────
  const pickerPopup = (
    <PopoverContent
      align="start"
      sideOffset={8}
      className="w-[240px] p-0 overflow-hidden border-[var(--mauve-5)] bg-[var(--mauve-2)] shadow-xl"
      onOpenAutoFocus={(e) => e.preventDefault()}
    >
      {/* Header: color type + eyedropper */}
      <div className="flex items-center justify-between px-3 py-1.5 border-b border-[var(--mauve-4)]">
        <div className="flex items-center gap-1 cursor-default select-none">
          <span className="text-xs text-[var(--mauve-11)]">Solid</span>
          <ChevronDown className="w-3 h-3 text-[var(--mauve-8)]" />
        </div>
        <button
          title="Eyedropper (not yet available)"
          className="w-5 h-5 flex items-center justify-center rounded text-[var(--mauve-9)] hover:text-[var(--mauve-11)] hover:bg-[var(--mauve-4)] transition-colors"
        >
          <Pipette className="w-3 h-3" />
        </button>
      </div>

      {/* Saturation/Value area */}
      <div className="px-3 pt-2.5 pb-2">
        <SVArea
          hue={hsv[0]}
          saturation={hsv[1]}
          value={hsv[2]}
          onChange={(s, v) => applyHsv(hsv[0], s, v)}
        />
      </div>

      {/* Hue + Alpha sliders */}
      <div className="px-3 pb-3 flex flex-col gap-2.5">
        <HueSlider hue={hsv[0]} onChange={(h) => applyHsv(h, hsv[1], hsv[2])} />
        <AlphaSlider alpha={alphaValue} hex={previewHex} onChange={handleAlpha} />
      </div>

      {/* Divider */}
      <div className="h-px bg-[var(--mauve-4)]" />

      {/* Model selector + Hex input + Alpha % */}
      <div className="px-3 py-2.5 flex gap-1.5 items-center">
        {/* Model selector — cosmetic only */}
        <div className="flex items-center justify-between h-6 bg-[var(--mauve-3)] border border-[var(--mauve-5)] rounded px-1.5 gap-0.5 cursor-default select-none flex-shrink-0 w-[52px]">
          <span className="text-[10px] text-[var(--mauve-11)] font-mono">HEX</span>
          <ChevronDown className="w-2.5 h-2.5 text-[var(--mauve-8)]" />
        </div>

        {/* Hex input */}
        <div className="flex-1 flex items-center h-6 bg-[var(--mauve-3)] border border-[var(--mauve-5)] rounded px-1.5 gap-0.5 min-w-0">
          <span className="text-[10px] text-[var(--mauve-8)] font-mono flex-shrink-0">#</span>
          <input
            type="text"
            value={hexInput}
            maxLength={6}
            onChange={(e) => setHexInput(e.target.value.toUpperCase())}
            onBlur={(e) => commitHex(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") commitHex((e.target as HTMLInputElement).value);
            }}
            className="flex-1 min-w-0 bg-transparent text-xs text-[var(--mauve-12)] outline-none font-mono"
          />
        </div>

        {/* Alpha % */}
        <div className="flex items-center h-6 bg-[var(--mauve-3)] border border-[var(--mauve-5)] rounded px-1 gap-0.5 flex-shrink-0 w-[46px]">
          <input
            type="number"
            min={0}
            max={100}
            value={alphaValue}
            onChange={(e) =>
              handleAlpha(clamp(parseInt(e.target.value, 10) || 0, 0, 100))
            }
            className="w-full bg-transparent text-xs text-[var(--mauve-12)] outline-none text-center [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
          />
          <span className="text-[10px] text-[var(--mauve-8)] flex-shrink-0">%</span>
        </div>
      </div>
    </PopoverContent>
  );

  // ─── Swatch-only mode (used inside properties panel rows) ─────────────────
  if (!showInlineHex) {
    return (
      <Popover>
        <PopoverTrigger asChild>
          <button
            className="w-[18px] h-[18px] rounded flex-shrink-0 focus:outline-none cursor-pointer border border-[var(--mauve-4)]"
            style={{ background: value ? swatchBg : CHECKER }}
          />
        </PopoverTrigger>
        {pickerPopup}
      </Popover>
    );
  }

  // ─── Full mode — swatch + inline hex field ─────────────────────────────────
  return (
    <div className="flex flex-col gap-0.5">
      {label && (
        <span className="text-[9px] uppercase tracking-wide text-[var(--mauve-9)] font-medium">
          {label}
        </span>
      )}
      <Popover>
        <div className="flex items-center h-6 bg-[var(--mauve-2)] border border-[var(--mauve-5)] rounded px-1.5 gap-1.5">
          <PopoverTrigger asChild>
            <button
              className="w-3.5 h-3.5 rounded-sm flex-shrink-0 focus:outline-none cursor-pointer border border-[var(--mauve-4)]"
              style={{ background: value ? swatchBg : CHECKER }}
            />
          </PopoverTrigger>

          <span className="text-[9px] text-[var(--mauve-7)] flex-shrink-0">#</span>
          <input
            type="text"
            value={value ? hexInput : "—"}
            maxLength={6}
            onChange={(e) => setHexInput(e.target.value.toUpperCase())}
            onBlur={(e) => commitHex(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") commitHex((e.target as HTMLInputElement).value);
            }}
            className="flex-1 min-w-0 bg-transparent text-[11px] text-[var(--mauve-12)] outline-none"
          />
        </div>
        {pickerPopup}
      </Popover>
    </div>
  );
}
