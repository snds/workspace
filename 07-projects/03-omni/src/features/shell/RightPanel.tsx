// Untitled UI icons — alignment, spacing, distribute
import {
  AlignLeft01,
  AlignHorizontalCentre01,
  AlignRight01,
  AlignTopArrow01,
  AlignVerticalCenter01,
  AlignBottom01,
  DistributeSpacingHorizontal,
  DistributeSpacingVertical,
  SpacingWidth01,
  SpacingHeight01,
  Settings01,
} from "@untitledui/icons";

// OmniIcon — semantic icon component (replaces lucide-react direct imports)
import { OmniIcon } from "@/core/icons";

// Compatibility shims: thin wrappers so existing JSX `<IconName className="…" />`
// continues to work without rewriting every callsite in this large file.
function makeLucideShim(semanticName: string) {
  return function ShimIcon({ className }: { className?: string }) {
    const sizeMatch = className?.match(/w-(\d+(?:\.\d+)?)/);
    const size = sizeMatch ? parseFloat(sizeMatch[1]) * 4 : 16;
    return <OmniIcon name={semanticName} size={size} />;
  };
}

const Plus = makeLucideShim("action/add");
const Minus = makeLucideShim("action/subtract");
const AlignLeft = makeLucideShim("formatting/align-left");
const AlignCenter = makeLucideShim("formatting/align-center");
const AlignRight = makeLucideShim("formatting/align-right");
const Underline = makeLucideShim("formatting/underline");
const Strikethrough = makeLucideShim("formatting/strikethrough");
const Italic = makeLucideShim("formatting/italic");
const Settings2 = makeLucideShim("action/settings");
const Eye = makeLucideShim("status/eye");
const EyeOff = makeLucideShim("status/eye-off");
const Lock = makeLucideShim("action/lock");
const Unlock = makeLucideShim("action/unlock");
const RotateCw = makeLucideShim("tool/rotate-cw");
const FlipHorizontal2 = makeLucideShim("tool/flip-h");
const FlipVertical2 = makeLucideShim("tool/flip-v");
const Link = makeLucideShim("content/link");
const Link2Off = makeLucideShim("action/link-off");
const Scissors = makeLucideShim("action/cut");
const ChevronDown = makeLucideShim("navigation/chevron-down");
const ZoomIn = makeLucideShim("tool/zoom-in");
const ZoomOut = makeLucideShim("tool/zoom-out");
const Sun = makeLucideShim("misc/sun");
const Moon = makeLucideShim("misc/moon");
const Pen = makeLucideShim("tool/pen");
const Layers = makeLucideShim("misc/layers");
const WrapText = makeLucideShim("lucide:wrap-text");
const RectangleHorizontal = makeLucideShim("lucide:rectangle-horizontal");
const RotateCcw = makeLucideShim("tool/rotate-ccw");

import { useState, useRef, type KeyboardEvent, type FocusEvent } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ColorPicker } from "@/components/ui/color-picker";
import { FontPicker } from "@/components/ui/font-picker";
import { AdvancedTypographyPanel } from "@/features/typography/AdvancedTypographyPanel";
import { useUIStore } from "@/stores/ui.store";
import { useCanvasStore } from "@/stores/canvas.store";
import { cn } from "@/lib/utils";
import type { CanvasNode, Effect } from "@/types/canvas";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

// ─── Design tokens ────────────────────────────────────────────────────────────

const SELECT_CLS =
  "bg-[var(--mauve-2)] border border-[var(--mauve-5)] rounded text-[11px] text-[var(--mauve-12)] outline-none appearance-none cursor-pointer";

const SELECT_CHEVRON: React.CSSProperties = {
  backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='%236e6a7a' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E")`,
  backgroundRepeat: "no-repeat",
  backgroundSize: "10px 10px",
  backgroundPosition: "right 4px center",
  paddingRight: "18px",
};

const BTN_ACTIVE_CLS =
  "bg-[var(--violet-3)] border-[var(--violet-6)] text-[var(--violet-11)]";

// Canvas background defaults (kept in sync with CanvasStage)
const CANVAS_BG_DEFAULTS: Record<"dark" | "light", string> = {
  dark:  "#1a1a1c",
  light: "#e8e7e8",
};

// ─── Angle icon (rotation field label) ────────────────────────────────────────

function AngleIcon() {
  return (
    <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
      <path d="M2 8V3" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
      <path d="M2 8H7" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
      <path d="M2 5.5A2.5 2.5 0 0 1 4.5 8" stroke="currentColor" strokeWidth="1" strokeLinecap="round" />
    </svg>
  );
}

// ─── Corner radius icons (Figma-style) ───────────────────────────────────────

/** All-corners radius icon: rounded top-left corner with two straight edges */
function CornerRadiusIcon() {
  return (
    <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
      <path d="M2 8V5.5C2 3.567 3.567 2 5.5 2H8" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
    </svg>
  );
}

/** Top-left corner radius */
function CornerTLIcon() {
  return (
    <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
      <path d="M2 8V5C2 3.343 3.343 2 5 2H8" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
      <path d="M8 8H8" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" opacity="0.35" />
    </svg>
  );
}

/** Top-right corner radius */
function CornerTRIcon() {
  return (
    <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
      <path d="M2 2H5C6.657 2 8 3.343 8 5V8" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
      <path d="M2 8H2" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" opacity="0.35" />
    </svg>
  );
}

/** Bottom-right corner radius */
function CornerBRIcon() {
  return (
    <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
      <path d="M8 2V5C8 6.657 6.657 8 5 8H2" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
      <path d="M2 2H2" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" opacity="0.35" />
    </svg>
  );
}

/** Bottom-left corner radius */
function CornerBLIcon() {
  return (
    <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
      <path d="M8 8H5C3.343 8 2 6.657 2 5V2" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
      <path d="M8 2H8" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" opacity="0.35" />
    </svg>
  );
}

// ─── Aspect ratio lock icons (Figma-style overlapping frames) ─────────────────

/** Locked: two overlapping rounded rectangles */
function AspectLockedIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
      <rect x="1" y="1" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.2" />
      <rect x="4" y="4" width="7" height="7" rx="1.5" stroke="currentColor" strokeWidth="1.2" />
    </svg>
  );
}

/** Unlocked: two separated rounded rectangles */
function AspectUnlockedIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
      <rect x="0.6" y="0.6" width="6" height="6" rx="1.5" stroke="currentColor" strokeWidth="1.2" />
      <rect x="5.4" y="5.4" width="6" height="6" rx="1.5" stroke="currentColor" strokeWidth="1.2" />
    </svg>
  );
}

// ─── Device frame templates ───────────────────────────────────────────────────

type DeviceTemplate = { name: string; w: number; h: number };

const DEVICE_GROUPS: { label: string; items: DeviceTemplate[] }[] = [
  {
    label: "Mac",
    items: [
      { name: "MacBook Air 13\"",    w: 1280, h: 832  },
      { name: "MacBook Air 15\"",    w: 1440, h: 900  },
      { name: "MacBook Pro 14\"",    w: 1512, h: 982  },
      { name: "MacBook Pro 16\"",    w: 1728, h: 1117 },
      { name: "iMac 24\"",           w: 2048, h: 1280 },
      { name: "Studio Display",      w: 2560, h: 1440 },
      { name: "Pro Display XDR",     w: 3024, h: 1964 },
    ],
  },
  {
    label: "Windows",
    items: [
      { name: "Surface Pro 9",       w: 1920, h: 1280 },
      { name: "Surface Book 3 15\"", w: 2496, h: 1664 },
      { name: "Surface Studio 2+",   w: 4500, h: 3000 },
      { name: "FHD (1920×1080)",     w: 1920, h: 1080 },
      { name: "QHD (2560×1440)",     w: 2560, h: 1440 },
      { name: "4K (3840×2160)",      w: 3840, h: 2160 },
    ],
  },
  {
    label: "iPhone",
    items: [
      { name: "iPhone 15 Pro Max",   w: 430,  h: 932  },
      { name: "iPhone 15 Pro",       w: 393,  h: 852  },
      { name: "iPhone 15",           w: 393,  h: 852  },
      { name: "iPhone 14",           w: 390,  h: 844  },
      { name: "iPhone SE (3rd gen)", w: 375,  h: 667  },
      { name: "iPhone 13 mini",      w: 375,  h: 812  },
    ],
  },
  {
    label: "iPad",
    items: [
      { name: "iPad Pro 12.9\"",     w: 1024, h: 1366 },
      { name: "iPad Pro 11\"",       w: 834,  h: 1194 },
      { name: "iPad Air",            w: 820,  h: 1180 },
      { name: "iPad Mini",           w: 744,  h: 1133 },
      { name: "iPad (10th gen)",     w: 820,  h: 1180 },
    ],
  },
  {
    label: "Android",
    items: [
      { name: "Pixel 8 Pro",         w: 412,  h: 892  },
      { name: "Pixel 8",             w: 412,  h: 892  },
      { name: "Pixel Fold (outer)",  w: 412,  h: 892  },
      { name: "Pixel Fold (inner)",  w: 748,  h: 832  },
      { name: "Pixel Tablet",        w: 1280, h: 800  },
      { name: "Galaxy S24 Ultra",    w: 384,  h: 824  },
      { name: "Galaxy S24",          w: 360,  h: 780  },
      { name: "Galaxy Z Fold 5",     w: 768,  h: 880  },
      { name: "Galaxy Z Flip 5",     w: 360,  h: 780  },
      { name: "Galaxy Tab S9 Ultra", w: 1848, h: 2960 },
      { name: "Galaxy Tab S9",       w: 1600, h: 2560 },
    ],
  },
  {
    label: "Watch",
    items: [
      { name: "Apple Watch Ultra 2", w: 205,  h: 251  },
      { name: "Apple Watch 45mm",    w: 198,  h: 242  },
      { name: "Apple Watch 41mm",    w: 176,  h: 215  },
      { name: "Galaxy Watch 6",      w: 450,  h: 450  },
    ],
  },
  {
    label: "Web",
    items: [
      { name: "Desktop (1920×1080)", w: 1920, h: 1080 },
      { name: "Desktop (1440×900)",  w: 1440, h: 900  },
      { name: "Desktop (1280×720)",  w: 1280, h: 720  },
      { name: "Tablet (768×1024)",   w: 768,  h: 1024 },
      { name: "Mobile (375×812)",    w: 375,  h: 812  },
    ],
  },
];

function findTemplateBySize(w: number, h: number): string {
  for (const group of DEVICE_GROUPS) {
    for (const item of group.items) {
      if (item.w === Math.round(w) && item.h === Math.round(h)) return item.name;
    }
  }
  return "";
}

// ─── Primitives ───────────────────────────────────────────────────────────────

function FL({ children }: { children: React.ReactNode }) {
  return (
    <span className="text-[10px] font-medium text-[var(--mauve-7)] leading-none mb-1 block">
      {children}
    </span>
  );
}

function SH({
  label,
  actions,
  collapsible,
  collapsed,
  onToggle,
}: {
  label: string;
  actions?: React.ReactNode;
  collapsible?: boolean;
  collapsed?: boolean;
  onToggle?: () => void;
}) {
  return (
    <div
      className={cn("flex items-center h-9 px-3 gap-1.5", collapsible && "cursor-pointer select-none")}
      onClick={collapsible ? onToggle : undefined}
    >
      {collapsible && (
        <ChevronDown className={cn("w-3 h-3 text-[var(--mauve-7)] transition-transform flex-shrink-0", collapsed && "-rotate-90")} />
      )}
      <span className="text-[10px] font-semibold text-[var(--mauve-9)] flex-1 uppercase tracking-[0.08em]">{label}</span>
      {actions && (
        <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
          {actions}
        </div>
      )}
    </div>
  );
}

function Div() {
  return <div className="h-px bg-[var(--mauve-4)]" />;
}

function Body({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn("px-3 pb-3 flex flex-col gap-2", className)}>{children}</div>;
}

function NI({
  label, value, onChange, step = 1, min = -Infinity, max = Infinity, unit, className, placeholder,
}: {
  label?: string | React.ReactNode;
  value: number;
  onChange: (v: number) => void;
  step?: number; min?: number; max?: number; unit?: string; className?: string; placeholder?: string;
}) {
  const ref = useRef<HTMLInputElement>(null);

  function commit(raw: string) {
    const n = parseFloat(raw);
    if (!isNaN(n)) onChange(Math.max(min, Math.min(max, n)));
  }

  function onKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "ArrowUp") {
      e.preventDefault();
      onChange(Math.max(min, Math.min(max, value + (e.shiftKey ? step * 10 : step))));
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      onChange(Math.max(min, Math.min(max, value - (e.shiftKey ? step * 10 : step))));
    } else if (e.key === "Enter") {
      commit((e.target as HTMLInputElement).value);
      ref.current?.blur();
    }
  }

  return (
    <div className={cn("flex items-center h-6 rounded border border-[var(--mauve-5)] bg-[var(--mauve-2)] overflow-hidden", className)}>
      {label && (
        <span className="text-[9px] font-semibold text-[var(--mauve-7)] px-1.5 flex-shrink-0 border-r border-[var(--mauve-4)] select-none leading-none">
          {label}
        </span>
      )}
      <input
        ref={ref}
        type="number"
        defaultValue={Math.round(value * 100) / 100}
        key={value}
        placeholder={placeholder}
        onKeyDown={onKeyDown}
        onBlur={(e: FocusEvent<HTMLInputElement>) => commit(e.target.value)}
        className={cn("flex-1 min-w-0 bg-transparent text-[11px] text-[var(--mauve-12)] outline-none [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none", label ? "px-1.5" : "px-2")}
      />
      {unit && <span className="text-[9px] text-[var(--mauve-7)] pr-1.5 flex-shrink-0">{unit}</span>}
    </div>
  );
}

function Sel({
  value, onChange, children, className, label,
}: {
  value: string | number;
  onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  children: React.ReactNode;
  className?: string;
  label?: string | React.ReactNode;
}) {
  if (label) {
    return (
      <div className={cn("flex items-center h-6 rounded border border-[var(--mauve-5)] bg-[var(--mauve-2)] overflow-hidden", className)}>
        <span className="text-[9px] font-semibold text-[var(--mauve-7)] px-1.5 flex-shrink-0 border-r border-[var(--mauve-4)] select-none leading-none">
          {label}
        </span>
        <select
          value={value}
          onChange={onChange}
          style={SELECT_CHEVRON}
          className="flex-1 min-w-0 bg-transparent text-[11px] text-[var(--mauve-12)] outline-none appearance-none cursor-pointer h-full pl-1.5"
        >
          {children}
        </select>
      </div>
    );
  }
  return (
    <select
      value={value}
      onChange={onChange}
      style={SELECT_CHEVRON}
      className={cn(SELECT_CLS, "h-6 pl-2", className)}
    >
      {children}
    </select>
  );
}

function IB({
  onClick, title, active, disabled, children, className,
}: {
  onClick?: () => void; title?: string; active?: boolean; disabled?: boolean;
  children: React.ReactNode; className?: string;
}) {
  return (
    <button
      onClick={onClick} title={title} disabled={disabled}
      className={cn(
        "w-6 h-6",
        "flex items-center justify-center rounded border border-[var(--mauve-5)] bg-[var(--mauve-2)] text-[var(--mauve-9)]",
        "hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-3)] hover:border-[var(--mauve-7)] transition-colors flex-shrink-0",
        active && BTN_ACTIVE_CLS,
        disabled && "opacity-30 pointer-events-none",
        className,
      )}
    >
      {children}
    </button>
  );
}

// ─── 9-point alignment grid ───────────────────────────────────────────────────

type AlignPos = "MIN" | "CENTER" | "MAX";

function AlignGrid({
  primary, counter, layoutMode, onChange,
}: {
  primary: AlignPos | "SPACE_BETWEEN"; counter: AlignPos;
  layoutMode: "HORIZONTAL" | "VERTICAL" | "GRID";
  onChange: (primary: AlignPos | "SPACE_BETWEEN", counter: AlignPos) => void;
}) {
  const rows: AlignPos[] = ["MIN", "CENTER", "MAX"];
  const cols: AlignPos[] = ["MIN", "CENTER", "MAX"];

  function isActive(col: AlignPos, row: AlignPos) {
    return layoutMode === "HORIZONTAL" ? col === primary && row === counter : col === counter && row === primary;
  }

  function handleClick(col: AlignPos, row: AlignPos) {
    if (layoutMode === "HORIZONTAL") onChange(col, row);
    else onChange(row, col);
  }

  return (
    <div className="flex flex-col gap-0.5 flex-shrink-0">
      {rows.map((row) => (
        <div key={row} className="flex gap-0.5">
          {cols.map((col) => (
            <button key={col} onClick={() => handleClick(col, row)}
              className={cn("w-[22px] h-[22px] flex items-center justify-center rounded border transition-colors",
                isActive(col, row)
                  ? "bg-[var(--violet-3)] border-[var(--violet-6)]"
                  : "bg-[var(--mauve-2)] border-[var(--mauve-5)] hover:border-[var(--mauve-7)] hover:bg-[var(--mauve-3)]")}>
              <span className={cn("w-1.5 h-1.5 rounded-full", isActive(col, row) ? "bg-[var(--violet-9)]" : "bg-[var(--mauve-6)]")} />
            </button>
          ))}
        </div>
      ))}
    </div>
  );
}

// ─── Fill row ────────────────────────────────────────────────────────────────

function FillRow({
  color, opacity, onChangeColor, onChangeOpacity, onRemove,
}: {
  color: string; opacity: number;
  onChangeColor: (v: string | null) => void;
  onChangeOpacity: (v: number) => void;
  onRemove: () => void;
}) {
  return (
    <div className="group flex flex-col gap-1">
      <div className="flex items-center gap-1.5">
        <div className="flex-1 min-w-0">
          <ColorPicker value={color} onChange={onChangeColor} />
        </div>
        <NI value={Math.round(opacity * 100)} onChange={(v) => onChangeOpacity(v / 100)} min={0} max={100} label="%" className="w-[72px]" />
        <button onClick={onRemove} className="opacity-0 group-hover:opacity-100 w-5 h-5 flex items-center justify-center rounded text-[var(--mauve-8)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)] transition-colors flex-shrink-0">
          <Minus className="w-3 h-3" />
        </button>
      </div>
      {/* TODO: Token linking — show a "Link to token" button when editing a color.
          Clicking it will open a token picker popover that lets the user bind this
          fill to a design token (TokenRef). The selected token path is stored in the
          IR node's colorSlots or as a TokenOrLiteral<string> on the fill property. */}
    </div>
  );
}

// ─── Stroke row ───────────────────────────────────────────────────────────────

function StrokeRow({
  color, width, position, onChangeColor, onChangeWidth, onChangePosition, onRemove,
}: {
  color: string; width: number; position?: CanvasNode["strokePosition"];
  onChangeColor: (v: string | null) => void;
  onChangeWidth: (v: number) => void;
  onChangePosition: (v: CanvasNode["strokePosition"]) => void;
  onRemove: () => void;
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="group flex items-center gap-1.5">
        <div className="flex-1 min-w-0">
          <ColorPicker value={color} onChange={onChangeColor} />
        </div>
        <button onClick={onRemove} className="opacity-0 group-hover:opacity-100 w-5 h-5 flex items-center justify-center rounded text-[var(--mauve-8)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)] transition-colors flex-shrink-0">
          <Minus className="w-3 h-3" />
        </button>
      </div>
      <div className="grid grid-cols-2 gap-1.5">
        <div>
          <FL>Position</FL>
          <Sel value={position ?? "center"} onChange={(e) => onChangePosition(e.target.value as CanvasNode["strokePosition"])} className="w-full">
            <option value="inside">Inside</option>
            <option value="center">Center</option>
            <option value="outside">Outside</option>
          </Sel>
        </div>
        <div>
          <FL>Weight</FL>
          <NI value={width} onChange={(v) => onChangeWidth(Math.max(0, v))} min={0} step={0.5} label="px" />
        </div>
      </div>
    </div>
  );
}

// ─── Effect row ───────────────────────────────────────────────────────────────

function EffectRow({ effect, index, onChange, onRemove }: {
  effect: Effect; index: number;
  onChange: (p: Partial<Effect>) => void; onRemove: () => void;
}) {
  const isShadow = effect.type === "DROP_SHADOW" || effect.type === "INNER_SHADOW";
  const isBlur   = effect.type === "LAYER_BLUR"  || effect.type === "BACKGROUND_BLUR";

  return (
    <div className="flex flex-col gap-1 group">
      <div className="flex items-center gap-2 h-7 -mx-3 px-3 hover:bg-[var(--mauve-3)] transition-colors rounded">
        <button onClick={() => onChange({ visible: !effect.visible })}
          className="w-4 h-4 flex items-center justify-center text-[var(--mauve-7)] hover:text-[var(--mauve-11)] transition-colors flex-shrink-0">
          {effect.visible ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
        </button>
        <Sel value={effect.type} onChange={(e) => onChange({ type: e.target.value as Effect["type"] })} className="flex-1">
          <option value="DROP_SHADOW">Drop shadow</option>
          <option value="INNER_SHADOW">Inner shadow</option>
          <option value="LAYER_BLUR">Layer blur</option>
          <option value="BACKGROUND_BLUR">Background blur</option>
        </Sel>
        <button onClick={onRemove} className="opacity-0 group-hover:opacity-100 w-5 h-5 flex items-center justify-center rounded text-[var(--mauve-8)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)] transition-colors">
          <Minus className="w-3 h-3" />
        </button>
      </div>

      {isShadow && (
        <div className="flex flex-col gap-1">
          {effect.color !== undefined && (
            <ColorPicker value={effect.color} onChange={(v) => onChange({ color: v ?? "#000000" })} />
          )}
          <div className="grid grid-cols-4 gap-1">
            {(["offsetX", "offsetY", "blur", "spread"] as const).map((field) => {
              const defaultVal = field === "offsetY" ? (effect.offsetY ?? 2) : field === "blur" ? (effect.blur ?? 4) : field === "offsetX" ? (effect.offsetX ?? 0) : (effect.spread ?? 0);
              const labels: Record<string, string> = { offsetX: "X", offsetY: "Y", blur: "B", spread: "S" };
              return (
                <NI key={`${field}-${index}`} label={labels[field]} value={defaultVal}
                  onChange={(v) => onChange({ [field]: v })} />
              );
            })}
          </div>
        </div>
      )}

      {isBlur && (
        <NI label="R" value={effect.radius ?? 4} onChange={(v) => onChange({ radius: Math.max(0, v) })} min={0} />
      )}
    </div>
  );
}

// ─── Typography section ───────────────────────────────────────────────────────

const FONT_WEIGHTS = [
  { value: 100, label: "Thin" }, { value: 200, label: "ExtraLight" },
  { value: 300, label: "Light" }, { value: 400, label: "Regular" },
  { value: 500, label: "Medium" }, { value: 600, label: "SemiBold" },
  { value: 700, label: "Bold" }, { value: 800, label: "ExtraBold" },
  { value: 900, label: "Black" },
];

function TypographySection({
  node, u, showAdvanced, onToggleAdvanced,
}: {
  node: CanvasNode; u: (p: Partial<CanvasNode>) => void;
  showAdvanced: boolean; onToggleAdvanced: () => void;
}) {
  const textAlign = node.textAlign    ?? "left";
  const vAlign    = node.verticalAlign ?? "top";
  const isItalic  = node.fontStyle === "italic";

  return (
    <>
      <Div />
      <SH label="Text" actions={
        <IB onClick={onToggleAdvanced} title="Advanced typography" active={showAdvanced}>
          <Settings2 className="w-3 h-3" />
        </IB>
      } />
      <Body>
        <div>
          <FL>Font</FL>
          <FontPicker value={node.fontFamily ?? "Inter"} onChange={(f) => u({ fontFamily: f })} />
        </div>

        <div>
          <FL>Weight</FL>
          <div className="flex gap-1.5">
            <Sel value={node.fontWeight ?? 400} onChange={(e) => u({ fontWeight: parseInt(e.target.value) })} className="flex-1">
              {FONT_WEIGHTS.map((w) => <option key={w.value} value={w.value}>{w.label}</option>)}
            </Sel>
            <IB onClick={() => u({ fontStyle: isItalic ? "normal" : "italic" })} title="Italic" active={isItalic}>
              <Italic className="w-3 h-3" />
            </IB>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-1.5">
          <div>
            <FL>Size</FL>
            <NI value={node.fontSize ?? 16}     onChange={(v) => u({ fontSize: Math.max(1, v) })}     min={1}  label="px" />
          </div>
          <div>
            <FL>Line height</FL>
            <NI value={node.lineHeight ?? 1.2}  onChange={(v) => u({ lineHeight: Math.max(0.5, v) })} min={0.5} step={0.05} />
          </div>
          <div>
            <FL>Spacing</FL>
            <NI value={node.letterSpacing ?? 0} onChange={(v) => u({ letterSpacing: v })}              step={0.5} label="px" />
          </div>
        </div>

        <div className="flex gap-2">
          <div className="flex flex-1">
            {([
              { v: "left" as const,   Icon: AlignLeft,   t: "Align left" },
              { v: "center" as const, Icon: AlignCenter, t: "Align center" },
              { v: "right" as const,  Icon: AlignRight,  t: "Align right" },
            ]).map(({ v, Icon, t }, i) => (
              <button key={v} title={t} onClick={() => u({ textAlign: v })}
                className={cn("flex-1 h-6 flex items-center justify-center border-y border-r transition-colors",
                  i === 0 ? "border-l rounded-l" : "-ml-px", i === 2 ? "rounded-r" : "",
                  textAlign === v
                    ? "bg-[var(--violet-3)] border-[var(--violet-6)] text-[var(--violet-11)] z-10"
                    : "bg-[var(--mauve-2)] border-[var(--mauve-5)] text-[var(--mauve-9)] hover:text-[var(--mauve-12)] hover:z-10")}>
                <Icon className="w-3 h-3" />
              </button>
            ))}
          </div>
          <div className="flex flex-1">
            {([
              { v: "top" as const,    icon: "↑", t: "Align top" },
              { v: "middle" as const, icon: "⊟", t: "Align middle" },
              { v: "bottom" as const, icon: "↓", t: "Align bottom" },
            ]).map(({ v, icon, t }, i) => (
              <button key={v} title={t} onClick={() => u({ verticalAlign: v })}
                className={cn("flex-1 h-6 flex items-center justify-center border-y border-r text-[11px] transition-colors",
                  i === 0 ? "border-l rounded-l" : "-ml-px", i === 2 ? "rounded-r" : "",
                  vAlign === v
                    ? "bg-[var(--violet-3)] border-[var(--violet-6)] text-[var(--violet-11)] z-10"
                    : "bg-[var(--mauve-2)] border-[var(--mauve-5)] text-[var(--mauve-9)] hover:text-[var(--mauve-12)] hover:z-10")}>
                {icon}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <IB onClick={() => u({ textDecoration: node.textDecoration === "underline" ? "none" : "underline" })} title="Underline" active={node.textDecoration === "underline"}><Underline className="w-3 h-3" /></IB>
          <IB onClick={() => u({ textDecoration: node.textDecoration === "line-through" ? "none" : "line-through" })} title="Strikethrough" active={node.textDecoration === "line-through"}><Strikethrough className="w-3 h-3" /></IB>
          <div className="flex-1" />
          <Sel value={node.textTransform ?? "none"} onChange={(e) => u({ textTransform: e.target.value as CanvasNode["textTransform"] })}>
            <option value="none">None</option>
            <option value="uppercase">UPPER</option>
            <option value="lowercase">lower</option>
            <option value="capitalize">Title</option>
          </Sel>
        </div>

        <div>
          <FL>Color</FL>
          {node.textColor ? (
            <FillRow color={node.textColor} opacity={1}
              onChangeColor={(v) => u({ textColor: v ?? undefined })}
              onChangeOpacity={() => {}}
              onRemove={() => u({ textColor: undefined })}
            />
          ) : (
            <button onClick={() => u({ textColor: "#000000" })}
              className="w-full h-6 flex items-center justify-center rounded border border-dashed border-[var(--mauve-5)] text-[10px] text-[var(--mauve-7)] hover:border-[var(--mauve-8)] hover:text-[var(--mauve-9)] transition-colors">
              <Plus className="w-3 h-3 mr-1" /> Add color
            </button>
          )}
        </div>
      </Body>
    </>
  );
}

// ─── Inspect view ─────────────────────────────────────────────────────────────

function InspectView({ node }: { node?: CanvasNode }) {
  if (!node) {
    return <div className="p-3 pt-8 text-[10px] text-[var(--mauve-9)] text-center">Select an element to inspect.</div>;
  }
  return (
    <div className="p-3 space-y-0.5">
      <p className="text-[10px] font-semibold text-[var(--mauve-10)] uppercase tracking-wide mb-2">{node.type} / {node.name}</p>
      {Object.entries(node).filter(([, v]) => v !== undefined && v !== null).map(([k, v]) => (
        <div key={k} className="flex gap-2 text-[10px]">
          <span className="text-[var(--mauve-8)] w-24 flex-shrink-0 truncate">{k}</span>
          <span className="text-[var(--mauve-11)] font-mono truncate">{JSON.stringify(v)}</span>
        </div>
      ))}
    </div>
  );
}

// ─── Multi-select panel ───────────────────────────────────────────────────────

function MultiSelectPanel({ ids }: { ids: string[] }) {
  const { nodes, updateNodes } = useCanvasStore();
  const selected = nodes.filter((n) => ids.includes(n.id));
  const opacities = [...new Set(selected.map((n) => n.opacity))];
  const sharedOpacity = opacities.length === 1 ? opacities[0]! : null;
  const fills = [...new Set(selected.map((n) => n.fill))];
  const sharedFill = fills.length === 1 ? fills[0] : "mixed";

  function alignNodes(hAlign?: "left" | "center" | "right", vAlign?: "top" | "middle" | "bottom") {
    if (selected.length < 2) return;
    const minX = Math.min(...selected.map((n) => n.x));
    const minY = Math.min(...selected.map((n) => n.y));
    const maxX = Math.max(...selected.map((n) => n.x + n.width));
    const maxY = Math.max(...selected.map((n) => n.y + n.height));
    updateNodes(selected.map((nd) => {
      const p: { id: string } & Partial<CanvasNode> = { id: nd.id };
      if (hAlign === "left")   p.x = minX;
      if (hAlign === "center") p.x = (minX + maxX) / 2 - nd.width  / 2;
      if (hAlign === "right")  p.x = maxX - nd.width;
      if (vAlign === "top")    p.y = minY;
      if (vAlign === "middle") p.y = (minY + maxY) / 2 - nd.height / 2;
      if (vAlign === "bottom") p.y = maxY - nd.height;
      return p;
    }));
  }

  function distribute(axis: "h" | "v") {
    if (selected.length < 3) return;
    if (axis === "h") {
      const sorted = [...selected].sort((a, b) => a.x - b.x);
      const totalW = sorted.reduce((s, n) => s + n.width, 0);
      const span = sorted[sorted.length - 1].x + sorted[sorted.length - 1].width - sorted[0].x;
      const gap = (span - totalW) / (sorted.length - 1);
      let cursor = sorted[0].x + sorted[0].width;
      updateNodes(sorted.slice(1).map((n) => { const x = cursor + gap; cursor = x + n.width; return { id: n.id, x }; }));
    } else {
      const sorted = [...selected].sort((a, b) => a.y - b.y);
      const totalH = sorted.reduce((s, n) => s + n.height, 0);
      const span = sorted[sorted.length - 1].y + sorted[sorted.length - 1].height - sorted[0].y;
      const gap = (span - totalH) / (sorted.length - 1);
      let cursor = sorted[0].y + sorted[0].height;
      updateNodes(sorted.slice(1).map((n) => { const y = cursor + gap; cursor = y + n.height; return { id: n.id, y }; }));
    }
  }

  const canDistribute = selected.length >= 3;
  const btnCls = "flex-1 h-6 flex items-center justify-center border border-[var(--mauve-5)] bg-[var(--mauve-2)] text-[var(--mauve-8)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-3)] transition-colors";

  return (
    <div className="flex flex-col pb-4">
      <div className="flex items-center h-10 px-3 border-b border-[var(--mauve-4)]">
        <span className="text-[11px] text-[var(--mauve-10)]">{ids.length} elements selected</span>
      </div>
      <Div />
      <SH label="Alignment" />
      <Body className="gap-1.5 pt-0">
        <div className="flex gap-0.5">
          <button onClick={() => alignNodes("left")}   title="Align left"             className={cn(btnCls, "rounded-l")}><AlignLeft01             size={14} /></button>
          <button onClick={() => alignNodes("center")} title="Align horizontal center" className={cn(btnCls, "-ml-px")}><AlignHorizontalCentre01 size={14} /></button>
          <button onClick={() => alignNodes("right")}  title="Align right"            className={cn(btnCls, "-ml-px rounded-r")}><AlignRight01 size={14} /></button>
          <div className="w-1" />
          <button onClick={() => alignNodes(undefined, "top")}    title="Align top"            className={cn(btnCls, "rounded-l")}><AlignTopArrow01       size={14} /></button>
          <button onClick={() => alignNodes(undefined, "middle")} title="Align vertical center" className={cn(btnCls, "-ml-px")}><AlignVerticalCenter01 size={14} /></button>
          <button onClick={() => alignNodes(undefined, "bottom")} title="Align bottom"         className={cn(btnCls, "-ml-px rounded-r")}><AlignBottom01  size={14} /></button>
          <div className="w-1" />
          <button onClick={() => distribute("h")} title="Distribute horizontal" disabled={!canDistribute} className={cn(btnCls, "rounded-l", !canDistribute && "opacity-30")}><DistributeSpacingHorizontal size={14} /></button>
          <button onClick={() => distribute("v")} title="Distribute vertical"   disabled={!canDistribute} className={cn(btnCls, "-ml-px rounded-r", !canDistribute && "opacity-30")}><DistributeSpacingVertical   size={14} /></button>
        </div>
      </Body>
      <Div />
      <SH label="Appearance" />
      <Body>
        <div>
          <FL>Opacity</FL>
          <NI value={sharedOpacity !== null ? Math.round(sharedOpacity * 100) : 100}
            onChange={(v) => updateNodes(selected.map((n) => ({ id: n.id, opacity: v / 100 })))} min={0} max={100} label="%" />
        </div>
        {sharedFill !== "mixed" && sharedFill !== null && (
          <div>
            <FL>Fill</FL>
            <FillRow color={sharedFill} opacity={1}
              onChangeColor={(v) => updateNodes(selected.map((n) => ({ id: n.id, fill: v })))}
              onChangeOpacity={() => {}}
              onRemove={() => updateNodes(selected.map((n) => ({ id: n.id, fill: null })))}
            />
          </div>
        )}
      </Body>
    </div>
  );
}

// ─── Blend modes ──────────────────────────────────────────────────────────────

const BLEND_MODES = [
  { value: "PASS_THROUGH", label: "Pass through" },
  { value: "NORMAL",       label: "Normal" },
  { value: "DARKEN",       label: "Darken" },
  { value: "MULTIPLY",     label: "Multiply" },
  { value: "COLOR_BURN",   label: "Color burn" },
  { value: "LIGHTEN",      label: "Lighten" },
  { value: "SCREEN",       label: "Screen" },
  { value: "COLOR_DODGE",  label: "Color dodge" },
  { value: "OVERLAY",      label: "Overlay" },
  { value: "SOFT_LIGHT",   label: "Soft light" },
  { value: "HARD_LIGHT",   label: "Hard light" },
  { value: "DIFFERENCE",   label: "Difference" },
  { value: "EXCLUSION",    label: "Exclusion" },
  { value: "HUE",          label: "Hue" },
  { value: "SATURATION",   label: "Saturation" },
  { value: "COLOR",        label: "Color" },
  { value: "LUMINOSITY",   label: "Luminosity" },
];

// ─── More actions dropdown ────────────────────────────────────────────────────

/** Boolean operations icon — two overlapping circles */
function BooleanOpsIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 14 14" fill="none" className={className} xmlns="http://www.w3.org/2000/svg">
      <circle cx="5.5" cy="7" r="4" stroke="currentColor" strokeWidth="1.3" />
      <circle cx="8.5" cy="7" r="4" stroke="currentColor" strokeWidth="1.3" />
    </svg>
  );
}

function MoreMenu({ nodeType }: { nodeType: "frame" | "rect" | "other" }) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="w-6 h-6 flex items-center justify-center rounded border border-[var(--mauve-5)] bg-[var(--mauve-2)] text-[var(--mauve-8)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-3)] transition-colors flex-shrink-0">
          <BooleanOpsIcon className="w-3.5 h-3.5" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent side="bottom" align="end" className="w-44">
        <DropdownMenuItem className="text-xs cursor-default opacity-50 gap-2" disabled>
          <Layers className="w-3.5 h-3.5" /> Set as mask
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem className="text-xs cursor-default opacity-50" disabled>Boolean: Union</DropdownMenuItem>
        <DropdownMenuItem className="text-xs cursor-default opacity-50" disabled>Boolean: Subtract</DropdownMenuItem>
        <DropdownMenuItem className="text-xs cursor-default opacity-50" disabled>Boolean: Intersect</DropdownMenuItem>
        <DropdownMenuItem className="text-xs cursor-default opacity-50" disabled>Boolean: Exclude</DropdownMenuItem>
        {nodeType === "rect" && (
          <>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-xs cursor-default opacity-50 gap-2" disabled>
              <Pen className="w-3.5 h-3.5" /> Edit vector
            </DropdownMenuItem>
          </>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

// ─── View controls (zoom + theme, always at top of right panel) ───────────────

function ViewControls() {
  const { zoom, zoomIn, zoomOut, resetZoom, theme, toggleTheme } = useUIStore();

  const btnCls = "flex items-center justify-center w-7 h-7 rounded text-[var(--mauve-9)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)] transition-colors";

  return (
    <div className="flex items-center gap-1.5 h-10 px-3 border-b border-[var(--color-border-subtle)]">
      <button onClick={toggleTheme} title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`} className={btnCls}>
        {theme === "dark" ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
      </button>

      <div className="w-px h-4 bg-[var(--mauve-4)]" />

      <button onClick={zoomOut} title="Zoom out" className={btnCls}>
        <ZoomOut className="w-3.5 h-3.5" />
      </button>
      <button
        onClick={resetZoom}
        title="Reset zoom (100%)"
        className="text-[11px] font-mono text-[var(--mauve-11)] hover:text-[var(--mauve-12)] transition-colors min-w-[38px] text-center"
      >
        {Math.round(zoom * 100)}%
      </button>
      <button onClick={zoomIn} title="Zoom in" className={btnCls}>
        <ZoomIn className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}

// ─── Page section (shown when nothing is selected) ────────────────────────────

function PageSection() {
  const { canvasBgHex, canvasBgAlpha, setCanvasBg, theme } = useUIStore();
  const effectiveHex = canvasBgHex ?? CANVAS_BG_DEFAULTS[theme];
  const isVisible = canvasBgAlpha > 0;

  return (
    <>
      <SH label="Page" />
      <Body>
        <FL>Canvas</FL>
        <div className="flex items-center gap-1.5">
          <div className="flex-1 min-w-0">
            <ColorPicker
              value={effectiveHex}
              onChange={(v) => setCanvasBg(v ?? effectiveHex, canvasBgAlpha)}
            />
          </div>
          <NI value={Math.round(canvasBgAlpha * 100)} onChange={(v) => setCanvasBg(effectiveHex, Math.max(0, Math.min(100, v)) / 100)} min={0} max={100} label="%" className="w-[72px]" />
          <button
            onClick={() => setCanvasBg(effectiveHex, isVisible ? 0 : 1)}
            className="w-5 h-5 flex items-center justify-center rounded text-[var(--mauve-8)] hover:text-[var(--mauve-12)] transition-colors flex-shrink-0"
            title={isVisible ? "Hide canvas color" : "Show canvas color"}
          >
            {isVisible ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
          </button>
        </div>
      </Body>
    </>
  );
}

// ─── Properties panel ─────────────────────────────────────────────────────────

function PropertiesPanel({ node }: { node: CanvasNode }) {
  const { updateNode, updateNodes, flipNodes, resizeFrameToFit } = useCanvasStore();
  const u = (patch: Partial<CanvasNode>) => updateNode(node.id, patch);

  const [showAdvanced,   setShowAdvanced]   = useState(false);
  const [splitCorners,   setSplitCorners]   = useState(
    node.cornerRadiusTopLeft !== undefined || node.cornerRadiusTopRight !== undefined ||
    node.cornerRadiusBottomRight !== undefined || node.cornerRadiusBottomLeft !== undefined,
  );
  const [splitPadding,   setSplitPadding]   = useState(
    node.paddingTop !== node.paddingBottom || node.paddingLeft !== node.paddingRight,
  );
  const [showALSettings, setShowALSettings] = useState(false);

  const isFrame = node.type === "frame";
  const isRect  = node.type === "rectangle";
  const isText  = node.type === "text";
  const showCR  = isRect || isFrame;
  const mode    = node.layoutMode ?? "NONE";
  const hasAL   = isFrame && mode !== "NONE";
  const alMode  = mode as "HORIZONTAL" | "VERTICAL" | "GRID";
  const primaryAlign = (node.primaryAxisAlignment  ?? "MIN") as "MIN" | "CENTER" | "MAX" | "SPACE_BETWEEN";
  const counterAlign = (node.counterAxisAlignment  ?? "MIN") as "MIN" | "CENTER" | "MAX";
  const gapMode = node.gapMode ?? "fixed";

  // Template match for frame
  const matchedTemplate = isFrame ? findTemplateBySize(node.width, node.height) : "";

  // Align all direct children of this frame
  function alignFrameChildren(hAlign?: "left" | "center" | "right", vAlign?: "top" | "middle" | "bottom") {
    const { nodes } = useCanvasStore.getState();
    const children = nodes.filter((n) => n.parentId === node.id);
    if (children.length === 0) return;
    updateNodes(children.map((child) => {
      const p: { id: string } & Partial<CanvasNode> = { id: child.id };
      if (hAlign === "left")   p.x = node.x;
      if (hAlign === "center") p.x = node.x + (node.width  - child.width)  / 2;
      if (hAlign === "right")  p.x = node.x + node.width   - child.width;
      if (vAlign === "top")    p.y = node.y;
      if (vAlign === "middle") p.y = node.y + (node.height - child.height) / 2;
      if (vAlign === "bottom") p.y = node.y + node.height  - child.height;
      return p;
    }));
  }

  const btnCls = "flex-1 h-6 flex items-center justify-center border border-[var(--mauve-5)] bg-[var(--mauve-2)] text-[var(--mauve-8)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-3)] transition-colors";

  return (
    <div className="flex flex-col pb-6">

      {/* ── Node header (unified compact row) ────────────────────────────── */}
      <div className="flex items-center gap-1.5 h-10 px-3 border-b border-[var(--mauve-4)]">
        {isFrame ? (
          <label className="relative flex-shrink-0 cursor-pointer">
            <span className="text-[10px] font-semibold text-[var(--mauve-9)] uppercase tracking-[0.08em]">Frame</span>
            <ChevronDown className="inline-block w-3 h-3 text-[var(--mauve-7)] ml-0.5 -mt-px" />
            <select
              value={matchedTemplate || "custom"}
              onChange={(e) => {
                for (const group of DEVICE_GROUPS) {
                  const tpl = group.items.find((t) => t.name === e.target.value);
                  if (tpl) { u({ width: tpl.w, height: tpl.h }); return; }
                }
              }}
              className="absolute inset-0 opacity-0 cursor-pointer"
            >
              <option value="custom">
                Custom ({Math.round(node.width)} × {Math.round(node.height)})
              </option>
              {DEVICE_GROUPS.map((group) => (
                <optgroup key={group.label} label={group.label}>
                  {group.items.map((tpl) => (
                    <option key={tpl.name} value={tpl.name}>
                      {tpl.name}  ({tpl.w}×{tpl.h})
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          </label>
        ) : (
          <span className="text-[10px] font-semibold text-[var(--mauve-9)] uppercase tracking-[0.08em]">
            {node.type}
          </span>
        )}
        <div className="flex-1" />
        <MoreMenu nodeType={isFrame ? "frame" : isRect ? "rect" : "other"} />
      </div>

      {/* ══ POSITION ═══════════════════════════════════════════════════════════ */}
      <SH label="Position" />
      <Body>
        {isFrame && (
          <div>
            <FL>Alignment</FL>
            <div className="flex gap-0.5">
              <button onClick={() => alignFrameChildren("left")}            title="Align left"     className={cn(btnCls, "rounded-l")}><AlignLeft01             size={14} /></button>
              <button onClick={() => alignFrameChildren("center")}          title="Align h-center" className={cn(btnCls, "-ml-px")}  ><AlignHorizontalCentre01 size={14} /></button>
              <button onClick={() => alignFrameChildren("right")}           title="Align right"    className={cn(btnCls, "-ml-px rounded-r")}><AlignRight01    size={14} /></button>
              <div className="w-1" />
              <button onClick={() => alignFrameChildren(undefined, "top")}    title="Align top"    className={cn(btnCls, "rounded-l")}><AlignTopArrow01       size={14} /></button>
              <button onClick={() => alignFrameChildren(undefined, "middle")} title="Align v-center" className={cn(btnCls, "-ml-px")}><AlignVerticalCenter01 size={14} /></button>
              <button onClick={() => alignFrameChildren(undefined, "bottom")} title="Align bottom" className={cn(btnCls, "-ml-px rounded-r")}><AlignBottom01   size={14} /></button>
            </div>
          </div>
        )}

        <div>
          <FL>Position</FL>
          <div className="grid grid-cols-2 gap-1.5">
            <NI label="X" value={node.x} onChange={(v) => u({ x: v })} />
            <NI label="Y" value={node.y} onChange={(v) => u({ y: v })} />
          </div>
        </div>

        <div>
          <FL>Rotation</FL>
          <div className="flex gap-1.5">
            <NI label={<AngleIcon />} value={node.rotation} onChange={(v) => u({ rotation: ((v % 360) + 360) % 360 })} unit="°" className="flex-1" />
            {node.rotation !== 0 && (
              <IB onClick={() => u({ rotation: 0 })} title="Reset rotation">
                <RotateCcw className="w-3.5 h-3.5" />
              </IB>
            )}
            <IB onClick={() => u({ rotation: (node.rotation + 90) % 360 })} title="Rotate 90°">
              <RotateCw className="w-3.5 h-3.5" />
            </IB>
            <IB onClick={() => flipNodes([node.id], "x")} title="Flip horizontal (⇧H)" active={node.flipX}>
              <FlipHorizontal2 className="w-3.5 h-3.5" />
            </IB>
            <IB onClick={() => flipNodes([node.id], "y")} title="Flip vertical (⇧V)" active={node.flipY}>
              <FlipVertical2 className="w-3.5 h-3.5" />
            </IB>
          </div>
        </div>

        {/* Dimensions — visible for all node types */}
        {!isFrame && (
          <div>
            <FL>Dimensions</FL>
            <div className="flex items-center gap-1.5">
              <div className="flex-1 grid grid-cols-2 gap-1.5">
                {isText ? (
                  <>
                    <NI label="W" value={Math.round(node.width)}  onChange={(v) => { const w = Math.max(1, v); u({ width: w, textSizing: "fixed" }); }} min={1} />
                    <NI label="H" value={Math.round(node.height)} onChange={(v) => { const h = Math.max(1, v); u({ height: h, textSizing: "fixed" }); }} min={1} />
                  </>
                ) : (
                  <>
                    <NI label="W" value={node.width}  onChange={(v) => { const w = Math.max(1, v); node.aspectRatioLocked && node.width > 0 ? u({ width: w, height: Math.max(1, Math.round(w * node.height / node.width)) }) : u({ width: w }); }} min={1} />
                    <NI label="H" value={node.height} onChange={(v) => { const h = Math.max(1, v); node.aspectRatioLocked && node.height > 0 ? u({ height: h, width: Math.max(1, Math.round(h * node.width / node.height)) }) : u({ height: h }); }} min={1} />
                  </>
                )}
              </div>
              {isText ? (
                <IB onClick={() => u({ textSizing: (node.textSizing ?? "auto") === "auto" ? "fixed" : "auto" })}
                  title={(node.textSizing ?? "auto") === "auto" ? "Auto size (hug contents)" : "Fixed size"}
                  active={(node.textSizing ?? "auto") === "auto"}>
                  {(node.textSizing ?? "auto") === "auto" ? <WrapText className="w-3 h-3" /> : <RectangleHorizontal className="w-3 h-3" />}
                </IB>
              ) : (
                <IB onClick={() => u({ aspectRatioLocked: !node.aspectRatioLocked })} title={node.aspectRatioLocked ? "Unlock ratio" : "Lock ratio"} active={node.aspectRatioLocked}>
                  {node.aspectRatioLocked ? <AspectLockedIcon /> : <AspectUnlockedIcon />}
                </IB>
              )}
            </div>
          </div>
        )}
      </Body>

      {/* ══ LAYOUT (frames) ════════════════════════════════════════════════════ */}
      {isFrame && (
        <>
          <Div />
          <SH
            label={hasAL ? "Auto layout" : "Layout"}
            actions={hasAL ? (
              <IB onClick={() => setShowALSettings((v) => !v)} title="Auto layout settings" active={showALSettings}>
                <Settings01 size={14} />
              </IB>
            ) : undefined}
          />
          <Body>
            <div>
              <FL>Flow</FL>
              <div className="flex gap-1">
                {(["NONE", "VERTICAL", "HORIZONTAL", "GRID"] as const).map((m) => (
                  <button key={m} onClick={() => u({ layoutMode: m })}
                    title={m === "NONE" ? "Freeform" : m === "VERTICAL" ? "Vertical" : m === "HORIZONTAL" ? "Horizontal" : "Grid"}
                    className={cn("flex-1 h-6 flex items-center justify-center rounded border text-[11px] transition-colors",
                      mode === m || (m === "NONE" && !node.layoutMode)
                        ? "bg-[var(--violet-3)] border-[var(--violet-6)] text-[var(--violet-11)]"
                        : "bg-[var(--mauve-2)] border-[var(--mauve-5)] text-[var(--mauve-8)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-3)]")}>
                    {m === "NONE" ? "—" : m === "VERTICAL" ? "↓" : m === "HORIZONTAL" ? "→" : "⊞"}
                  </button>
                ))}
                {mode === "HORIZONTAL" && (
                  <button onClick={() => u({ wrapChildren: !node.wrapChildren })}
                    className={cn("h-6 px-2 rounded border text-[10px] transition-colors",
                      node.wrapChildren
                        ? "bg-[var(--violet-3)] border-[var(--violet-6)] text-[var(--violet-11)]"
                        : "bg-[var(--mauve-2)] border-[var(--mauve-5)] text-[var(--mauve-8)] hover:text-[var(--mauve-12)]")}>
                    Wrap
                  </button>
                )}
              </div>
            </div>

            <div>
              <FL>{hasAL ? "Resizing" : "Dimensions"}</FL>
              <div className="flex items-center gap-1.5">
                <div className="flex-1 grid grid-cols-2 gap-1.5">
                  {hasAL ? (
                    <>
                      <Sel value={node.primaryAxisSizing ?? "FIXED"} onChange={(e) => u({ primaryAxisSizing: e.target.value as CanvasNode["primaryAxisSizing"] })}>
                        <option value="FIXED">W Fixed</option>
                        <option value="HUG">W Hug</option>
                        <option value="FILL">W Fill</option>
                      </Sel>
                      <Sel value={node.counterAxisSizing ?? "FIXED"} onChange={(e) => u({ counterAxisSizing: e.target.value as CanvasNode["counterAxisSizing"] })}>
                        <option value="FIXED">H Fixed</option>
                        <option value="HUG">H Hug</option>
                        <option value="FILL">H Fill</option>
                      </Sel>
                    </>
                  ) : isText ? (
                    <>
                      <NI label="W" value={Math.round(node.width)}  onChange={(v) => { const w = Math.max(1, v); u({ width: w, textSizing: "fixed" }); }} min={1} />
                      <NI label="H" value={Math.round(node.height)} onChange={(v) => { const h = Math.max(1, v); u({ height: h, textSizing: "fixed" }); }} min={1} />
                    </>
                  ) : (
                    <>
                      <NI label="W" value={node.width}  onChange={(v) => { const w = Math.max(1, v); node.aspectRatioLocked && node.width > 0 ? u({ width: w, height: Math.max(1, Math.round(w * node.height / node.width)) }) : u({ width: w }); }} min={1} />
                      <NI label="H" value={node.height} onChange={(v) => { const h = Math.max(1, v); node.aspectRatioLocked && node.height > 0 ? u({ height: h, width: Math.max(1, Math.round(h * node.width / node.height)) }) : u({ height: h }); }} min={1} />
                    </>
                  )}
                </div>
                {isText ? (
                  <IB onClick={() => u({ textSizing: (node.textSizing ?? "auto") === "auto" ? "fixed" : "auto" })}
                    title={(node.textSizing ?? "auto") === "auto" ? "Auto size (hug contents)" : "Fixed size"}
                    active={(node.textSizing ?? "auto") === "auto"}>
                    {(node.textSizing ?? "auto") === "auto" ? <WrapText className="w-3 h-3" /> : <RectangleHorizontal className="w-3 h-3" />}
                  </IB>
                ) : (
                  <IB onClick={() => u({ aspectRatioLocked: !node.aspectRatioLocked })} title={node.aspectRatioLocked ? "Unlock ratio" : "Lock ratio"} active={node.aspectRatioLocked}>
                    {node.aspectRatioLocked ? <AspectLockedIcon /> : <AspectUnlockedIcon />}
                  </IB>
                )}
              </div>
              {hasAL && (
                <div className="grid grid-cols-2 gap-1.5 mt-1.5">
                  {(!node.primaryAxisSizing || node.primaryAxisSizing === "FIXED") && (
                    <NI label="W" value={node.width}  onChange={(v) => u({ width: Math.max(1, v) })}  min={1} />
                  )}
                  {(!node.counterAxisSizing || node.counterAxisSizing === "FIXED") && (
                    <NI label="H" value={node.height} onChange={(v) => u({ height: Math.max(1, v) })} min={1} />
                  )}
                </div>
              )}
            </div>

            {hasAL && (
              <>
                <div className="grid grid-cols-2 gap-3 items-start">
                  <div>
                    <FL>Alignment</FL>
                    <AlignGrid primary={primaryAlign} counter={counterAlign} layoutMode={alMode}
                      onChange={(p, c) => u({ primaryAxisAlignment: p, counterAxisAlignment: c })} />
                  </div>
                  <div className="flex flex-col gap-1">
                    <FL>Gap</FL>
                    <div className="flex items-center gap-1">
                      {gapMode === "fixed" ? (
                        <NI label="≡" value={node.itemSpacing ?? 0}
                          onChange={(v) => u({ itemSpacing: Math.max(0, v) })} min={0} className="flex-1" />
                      ) : (
                        <div className="flex-1 h-6 flex items-center bg-[var(--mauve-2)] border border-[var(--mauve-5)] rounded px-2 text-[10px] text-[var(--mauve-8)]">Auto</div>
                      )}
                      <button onClick={() => u({ gapMode: gapMode === "fixed" ? "auto" : "fixed" })} title="Toggle auto gap"
                        className={cn("h-6 px-1.5 rounded border text-[10px] transition-colors",
                          gapMode === "auto" ? "bg-[var(--violet-3)] border-[var(--violet-6)] text-[var(--violet-11)]"
                                            : "bg-[var(--mauve-2)] border-[var(--mauve-5)] text-[var(--mauve-8)] hover:text-[var(--mauve-12)]")}>
                        A
                      </button>
                    </div>
                    <button onClick={() => u({ primaryAxisAlignment: primaryAlign === "SPACE_BETWEEN" ? "MIN" : "SPACE_BETWEEN" })}
                      className={cn("w-full h-6 rounded border text-[9px] transition-colors",
                        primaryAlign === "SPACE_BETWEEN"
                          ? "bg-[var(--violet-3)] border-[var(--violet-6)] text-[var(--violet-11)]"
                          : "bg-[var(--mauve-2)] border-[var(--mauve-5)] text-[var(--mauve-7)] hover:text-[var(--mauve-12)]")}>
                      Space between
                    </button>
                  </div>
                </div>

                <div>
                  <div className="flex items-center mb-1">
                    <FL>Padding</FL>
                    <button onClick={() => setSplitPadding((v) => !v)} title={splitPadding ? "Uniform" : "Split padding"}
                      className={cn("ml-auto w-4 h-4 flex items-center justify-center rounded transition-colors text-[10px]",
                        splitPadding ? "text-[var(--violet-9)]" : "text-[var(--mauve-7)] hover:text-[var(--mauve-11)]")}>
                      {splitPadding ? <Link className="w-3 h-3" /> : <Link2Off className="w-3 h-3" />}
                    </button>
                  </div>
                  {splitPadding ? (
                    <div className="grid grid-cols-2 gap-1">
                      <NI label="T" value={node.paddingTop    ?? 0} onChange={(v) => u({ paddingTop:    Math.max(0, v) })} min={0} />
                      <NI label="R" value={node.paddingRight  ?? 0} onChange={(v) => u({ paddingRight:  Math.max(0, v) })} min={0} />
                      <NI label="B" value={node.paddingBottom ?? 0} onChange={(v) => u({ paddingBottom: Math.max(0, v) })} min={0} />
                      <NI label="L" value={node.paddingLeft   ?? 0} onChange={(v) => u({ paddingLeft:   Math.max(0, v) })} min={0} />
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 gap-1.5">
                      <div className="flex items-center h-6 rounded border border-[var(--mauve-5)] bg-[var(--mauve-2)] gap-1 px-1.5">
                        <SpacingWidth01 size={13} className="text-[var(--mauve-7)] flex-shrink-0" />
                        <input type="number" defaultValue={node.paddingLeft ?? 0} key={`pl-${node.paddingLeft}`} min={0}
                          onBlur={(e) => { const v = parseFloat(e.target.value); if (!isNaN(v)) u({ paddingLeft: Math.max(0, v), paddingRight: Math.max(0, v) }); }}
                          onKeyDown={(e) => { if (e.key === "Enter") { const v = parseFloat((e.target as HTMLInputElement).value); if (!isNaN(v)) u({ paddingLeft: Math.max(0, v), paddingRight: Math.max(0, v) }); (e.target as HTMLInputElement).blur(); }}}
                          className="flex-1 bg-transparent text-[11px] text-[var(--mauve-12)] outline-none [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none" />
                      </div>
                      <div className="flex items-center h-6 rounded border border-[var(--mauve-5)] bg-[var(--mauve-2)] gap-1 px-1.5">
                        <SpacingHeight01 size={13} className="text-[var(--mauve-7)] flex-shrink-0" />
                        <input type="number" defaultValue={node.paddingTop ?? 0} key={`pt-${node.paddingTop}`} min={0}
                          onBlur={(e) => { const v = parseFloat(e.target.value); if (!isNaN(v)) u({ paddingTop: Math.max(0, v), paddingBottom: Math.max(0, v) }); }}
                          onKeyDown={(e) => { if (e.key === "Enter") { const v = parseFloat((e.target as HTMLInputElement).value); if (!isNaN(v)) u({ paddingTop: Math.max(0, v), paddingBottom: Math.max(0, v) }); (e.target as HTMLInputElement).blur(); }}}
                          className="flex-1 bg-transparent text-[11px] text-[var(--mauve-12)] outline-none [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none" />
                      </div>
                    </div>
                  )}
                </div>

                {showALSettings && (
                  <div className="p-2 bg-[var(--mauve-2)] border border-[var(--mauve-5)] rounded flex flex-col gap-2">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" checked={node.strokesIncludedInLayout ?? false} onChange={(e) => u({ strokesIncludedInLayout: e.target.checked })} className="w-3 h-3 accent-[var(--violet-9)]" />
                      <span className="text-[10px] text-[var(--mauve-10)]">Include strokes in layout</span>
                    </label>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-[var(--mauve-8)] w-14 flex-shrink-0">Stacking</span>
                      <Sel value={node.childrenStackOrder ?? "last-on-top"} onChange={(e) => u({ childrenStackOrder: e.target.value as CanvasNode["childrenStackOrder"] })} className="flex-1">
                        <option value="last-on-top">Last on top</option>
                        <option value="first-on-top">First on top</option>
                      </Sel>
                    </div>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input type="checkbox" checked={node.alignTextBaseline ?? false} onChange={(e) => u({ alignTextBaseline: e.target.checked })} className="w-3 h-3 accent-[var(--violet-9)]" />
                      <span className="text-[10px] text-[var(--mauve-10)]">Align text baseline</span>
                    </label>
                  </div>
                )}
              </>
            )}

            {!hasAL && (
              <button onClick={() => resizeFrameToFit(node.id)}
                className="w-full h-6 flex items-center justify-center rounded border border-[var(--mauve-5)] bg-[var(--mauve-2)] text-[10px] text-[var(--mauve-9)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-3)] transition-colors">
                Resize to fit
              </button>
            )}

            <div className="flex items-center gap-2 pt-0.5">
              <Scissors className="w-3.5 h-3.5 text-[var(--mauve-7)] flex-shrink-0" />
              <span className="text-[11px] text-[var(--mauve-10)] flex-1">Clip content</span>
              <button onClick={() => u({ clipContent: !node.clipContent })}
                className={cn("w-8 h-4 rounded-full transition-colors relative flex-shrink-0",
                  node.clipContent ? "bg-[var(--violet-9)]" : "bg-[var(--mauve-5)]")}>
                <span className={cn("absolute top-0.5 w-3 h-3 rounded-full bg-white shadow transition-transform",
                  node.clipContent ? "translate-x-4" : "translate-x-0.5")} />
              </button>
            </div>
          </Body>
        </>
      )}

      {/* ══ APPEARANCE ═════════════════════════════════════════════════════════ */}
      <Div />
      <SH label="Appearance" />
      <Body>
        {/* Visible + Locked moved from header */}
        <div className="flex items-center gap-1.5">
          <button onClick={() => u({ visible: !node.visible })} title={node.visible ? "Hide layer" : "Show layer"}
            className={cn("flex-1 h-6 flex items-center justify-center gap-1.5 rounded border text-[10px] font-medium transition-colors",
              !node.visible
                ? "bg-[var(--violet-3)] border-[var(--violet-6)] text-[var(--violet-11)]"
                : "bg-[var(--mauve-2)] border-[var(--mauve-5)] text-[var(--mauve-8)] hover:text-[var(--mauve-12)]")}>
            {node.visible ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
            {node.visible ? "Visible" : "Hidden"}
          </button>
          <button onClick={() => u({ locked: !node.locked })} title={node.locked ? "Unlock" : "Lock"}
            className={cn("flex-1 h-6 flex items-center justify-center gap-1.5 rounded border text-[10px] font-medium transition-colors",
              node.locked
                ? "bg-[var(--violet-3)] border-[var(--violet-6)] text-[var(--violet-11)]"
                : "bg-[var(--mauve-2)] border-[var(--mauve-5)] text-[var(--mauve-8)] hover:text-[var(--mauve-12)]")}>
            {node.locked ? <Lock className="w-3.5 h-3.5" /> : <Unlock className="w-3.5 h-3.5" />}
            {node.locked ? "Locked" : "Unlocked"}
          </button>
        </div>

        <div className="grid grid-cols-2 gap-1.5">
          <div>
            <FL>Blend mode</FL>
            <Sel value={node.blendMode ?? (isFrame ? "PASS_THROUGH" : "NORMAL")} onChange={(e) => u({ blendMode: e.target.value })} className="w-full">
              {BLEND_MODES.map((bm) => <option key={bm.value} value={bm.value}>{bm.label}</option>)}
            </Sel>
          </div>
          <div>
            <FL>Opacity</FL>
            <NI value={Math.round(node.opacity * 100)} onChange={(v) => u({ opacity: Math.max(0, Math.min(100, v)) / 100 })} min={0} max={100} label="%" />
          </div>
        </div>

        {showCR && (
          <div>
            <FL>Corner radius</FL>
            <div className="flex items-center gap-1.5">
              {splitCorners ? (
                <div className="flex-1 grid grid-cols-2 gap-1">
                  <NI label={<CornerTLIcon />} value={node.cornerRadiusTopLeft     ?? node.cornerRadius} onChange={(v) => u({ cornerRadiusTopLeft:     Math.max(0, v) })} min={0} />
                  <NI label={<CornerTRIcon />} value={node.cornerRadiusTopRight    ?? node.cornerRadius} onChange={(v) => u({ cornerRadiusTopRight:    Math.max(0, v) })} min={0} />
                  <NI label={<CornerBLIcon />} value={node.cornerRadiusBottomLeft  ?? node.cornerRadius} onChange={(v) => u({ cornerRadiusBottomLeft:  Math.max(0, v) })} min={0} />
                  <NI label={<CornerBRIcon />} value={node.cornerRadiusBottomRight ?? node.cornerRadius} onChange={(v) => u({ cornerRadiusBottomRight: Math.max(0, v) })} min={0} />
                </div>
              ) : (
                <NI label={<CornerRadiusIcon />} value={node.cornerRadius} onChange={(v) => u({ cornerRadius: Math.max(0, v) })} min={0} className="flex-1" />
              )}
              <IB onClick={() => {
                if (splitCorners) {
                  const avg = Math.round(
                    ((node.cornerRadiusTopLeft ?? node.cornerRadius) + (node.cornerRadiusTopRight ?? node.cornerRadius) +
                     (node.cornerRadiusBottomRight ?? node.cornerRadius) + (node.cornerRadiusBottomLeft ?? node.cornerRadius)) / 4,
                  );
                  u({ cornerRadius: avg, cornerRadiusTopLeft: undefined, cornerRadiusTopRight: undefined, cornerRadiusBottomRight: undefined, cornerRadiusBottomLeft: undefined });
                }
                setSplitCorners((v) => !v);
              }} title={splitCorners ? "Uniform radius" : "Split radii"} active={splitCorners}>
                {splitCorners ? <Link className="w-3 h-3" /> : <Link2Off className="w-3 h-3" />}
              </IB>
            </div>
          </div>
        )}
      </Body>

      {/* ══ TYPOGRAPHY ═════════════════════════════════════════════════════════ */}
      {isText && (
        <>
          <TypographySection node={node} u={u} showAdvanced={showAdvanced} onToggleAdvanced={() => setShowAdvanced((v) => !v)} />
          {showAdvanced && <AdvancedTypographyPanel node={node} onClose={() => setShowAdvanced(false)} />}
        </>
      )}

      {/* ══ FILL ═══════════════════════════════════════════════════════════════ */}
      {!isText && (
        <>
          <Div />
          <SH label="Fill" actions={
            <IB onClick={() => { if (!node.fill) u({ fill: "#6e56cf", fillOpacity: 1 }); }} title="Add fill">
              <Plus className="w-3 h-3" />
            </IB>
          } />
          <Body className="pt-0">
            {node.fill ? (
              <FillRow color={node.fill} opacity={node.fillOpacity ?? 1}
                onChangeColor={(v) => u({ fill: v })}
                onChangeOpacity={(v) => u({ fillOpacity: v })}
                onRemove={() => u({ fill: null })}
              />
            ) : (
              <div className="text-[10px] text-[var(--mauve-8)] italic">No fill</div>
            )}
          </Body>

          {/* ══ STROKE ═════════════════════════════════════════════════════════ */}
          <Div />
          <SH label="Stroke" actions={
            <IB onClick={() => { if (!node.stroke) u({ stroke: "#000000", strokeWidth: node.strokeWidth || 1 }); }} title="Add stroke">
              <Plus className="w-3 h-3" />
            </IB>
          } />
          <Body className="pt-0">
            {node.stroke ? (
              <StrokeRow color={node.stroke} width={node.strokeWidth} position={node.strokePosition}
                onChangeColor={(v) => u({ stroke: v })}
                onChangeWidth={(v) => u({ strokeWidth: v })}
                onChangePosition={(v) => u({ strokePosition: v })}
                onRemove={() => u({ stroke: null })}
              />
            ) : (
              <div className="text-[10px] text-[var(--mauve-8)] italic">No stroke</div>
            )}
          </Body>

          {/* ══ EFFECTS ════════════════════════════════════════════════════════ */}
          <Div />
          <SH label="Effects" actions={
            <IB onClick={() => {
              const effects = [...(node.effects ?? [])];
              effects.push({ type: "DROP_SHADOW", visible: true, color: "#000000", offsetX: 0, offsetY: 2, blur: 4, spread: 0 });
              u({ effects });
            }} title="Add effect">
              <Plus className="w-3 h-3" />
            </IB>
          } />
          <Body className="pt-0">
            {node.effects && node.effects.length > 0 ? (
              node.effects.map((eff, i) => (
                <EffectRow key={i} effect={eff} index={i}
                  onChange={(patch) => { const effects = node.effects!.map((e, idx) => idx === i ? { ...e, ...patch } : e); u({ effects }); }}
                  onRemove={() => { const effects = node.effects!.filter((_, idx) => idx !== i); u({ effects: effects.length > 0 ? effects : undefined }); }}
                />
              ))
            ) : (
              <div className="text-[10px] text-[var(--mauve-8)] italic">No effects</div>
            )}
          </Body>
        </>
      )}
    </div>
  );
}

// ─── Right panel ──────────────────────────────────────────────────────────────

export function RightPanel() {
  const { inspectMode } = useUIStore();
  const { nodes, selectedIds } = useCanvasStore();

  const selectedNode = selectedIds.length === 1
    ? nodes.find((n) => n.id === selectedIds[0])
    : undefined;

  return (
    <div className="flex flex-col w-full h-full bg-[var(--color-surface-1)] border-l border-[var(--color-border-subtle)]">
      {/* Always-visible: zoom + theme */}
      <ViewControls />

      <ScrollArea className="flex-1">
        {inspectMode ? (
          <InspectView node={selectedNode} />
        ) : selectedNode ? (
          <PropertiesPanel node={selectedNode} />
        ) : selectedIds.length > 1 ? (
          <MultiSelectPanel ids={selectedIds} />
        ) : (
          <PageSection />
        )}
      </ScrollArea>
    </div>
  );
}
