import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { ChevronLeft, ChevronRight, X } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ColorPicker } from "@/components/ui/color-picker";
import { useCanvasStore } from "@/stores/canvas.store";
import { useUIStore } from "@/stores/ui.store";
import { cn } from "@/lib/utils";
import type { CanvasNode } from "@/types/canvas";

// ─── Build CSS font-feature-settings string ───────────────────────────────────

export function buildFontFeatureSettings(node: Partial<CanvasNode>): string {
  const f: string[] = [];
  if (node.ligatures === true) { f.push('"liga" 1', '"clig" 1'); }
  if (node.contextualAlternates === true) f.push('"calt" 1');
  if (node.ordinals === true) f.push('"ordn" 1');
  if (node.fractions === true) f.push('"frac" 1');
  if (node.caseSensitiveForms === true) f.push('"case" 1');
  if (node.smallCaps === true) f.push('"smcp" 1');
  if (node.numberPosition === "subscript") f.push('"subs" 1');
  else if (node.numberPosition === "superscript") f.push('"sups" 1');
  if (node.stylisticSets?.length) {
    for (const n of node.stylisticSets) {
      f.push(`"ss${String(n).padStart(2, "0")}" 1`);
    }
  }
  return f.length > 0 ? f.join(", ") : "normal";
}

// ─── Small toggle button ──────────────────────────────────────────────────────

function TB({
  active,
  onClick,
  onMouseEnter,
  onMouseLeave,
  title,
  children,
}: {
  active: boolean;
  onClick: () => void;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
  title?: string;
  children: React.ReactNode;
}) {
  return (
    <button
      title={title}
      onClick={onClick}
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      className={cn(
        "min-w-[24px] h-6 px-1 flex items-center justify-center rounded text-[10px] transition-colors leading-none",
        active
          ? "bg-[var(--violet-9)] text-white"
          : "text-[var(--mauve-10)] hover:bg-[var(--mauve-4)] hover:text-[var(--mauve-12)]",
      )}
    >
      {children}
    </button>
  );
}

// ─── Control row ──────────────────────────────────────────────────────────────

function ControlRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center h-8 px-3 gap-2">
      <span className="text-[10px] text-[var(--mauve-10)] flex-1 min-w-0 truncate">{label}</span>
      <div className="flex items-center gap-0.5 flex-shrink-0">{children}</div>
    </div>
  );
}

// ─── Section group ────────────────────────────────────────────────────────────

function PanelSection({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="pb-1">
      <div className="flex items-center h-7 px-3">
        <span className="text-[9px] uppercase tracking-wider text-[var(--mauve-7)] font-semibold">
          {label}
        </span>
      </div>
      {children}
    </div>
  );
}

function PanelDivider() {
  return <div className="h-px bg-[var(--mauve-4)] mx-3 my-1" />;
}

// ─── Slider row ───────────────────────────────────────────────────────────────

function SliderRow({
  label,
  value,
  min = 0,
  max = 100,
  onChange,
  onMouseEnter,
  onMouseLeave,
  unit = "%",
}: {
  label: string;
  value: number;
  min?: number;
  max?: number;
  onChange: (v: number) => void;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
  unit?: string;
}) {
  return (
    <div className="px-3 pt-1 pb-2" onMouseEnter={onMouseEnter} onMouseLeave={onMouseLeave}>
      <div className="flex items-center gap-2 mb-1.5">
        <span className="text-[10px] text-[var(--mauve-10)] flex-1">{label}</span>
        <span className="text-[10px] text-[var(--mauve-11)] tabular-nums w-8 text-right">
          {Math.round(value)}{unit}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full h-1 cursor-pointer accent-[var(--violet-9)]"
      />
    </div>
  );
}

// ─── Inline number input ──────────────────────────────────────────────────────

function InlineNumberInput({
  value,
  unit,
  min = 0,
  onChange,
}: {
  value: number;
  unit?: string;
  min?: number;
  onChange: (v: number) => void;
}) {
  return (
    <div className="flex items-center bg-[var(--mauve-3)] border border-[var(--mauve-5)] rounded h-6 px-1.5 gap-0.5">
      <input
        type="number"
        defaultValue={value}
        key={value}
        min={min}
        step={1}
        onBlur={(e) => {
          const v = parseFloat(e.target.value);
          if (!isNaN(v)) onChange(Math.max(min, v));
        }}
        onKeyDown={(e) => {
          if (e.key === "Enter") (e.target as HTMLInputElement).blur();
        }}
        className="w-10 bg-transparent text-[10px] text-[var(--mauve-12)] outline-none text-right [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
      />
      {unit && <span className="text-[9px] text-[var(--mauve-8)]">{unit}</span>}
    </div>
  );
}

// ─── Preview area ─────────────────────────────────────────────────────────────

function PreviewArea({
  node,
  hoverOverride,
}: {
  node: CanvasNode;
  hoverOverride: Partial<CanvasNode> | null;
}) {
  const m = hoverOverride ? { ...node, ...hoverOverride } : node;

  const textDecoration = (() => {
    if (m.textDecoration === "underline") {
      const parts: string[] = ["underline"];
      if (m.textDecorationStyle) parts.push(m.textDecorationStyle);
      if (m.textDecorationColor) parts.push(m.textDecorationColor);
      return parts.join(" ");
    }
    if (m.textDecoration === "line-through") return "line-through";
    return "none";
  })();

  const style: React.CSSProperties = {
    fontFamily: m.fontFamily ? `"${m.fontFamily}", sans-serif` : "sans-serif",
    fontWeight: m.fontWeight ?? 400,
    fontStyle: m.fontStyle ?? "normal",
    fontSize: `${Math.min(m.fontSize ?? 16, 26)}px`,
    letterSpacing: `${(m.letterSpacing ?? 0) * 0.5}px`,
    lineHeight: m.lineHeight ?? 1.4,
    textDecoration,
    textTransform: (m.textTransform ?? "none") as React.CSSProperties["textTransform"],
    fontVariantCaps: m.smallCaps ? "small-caps" : "normal",
    fontFeatureSettings: buildFontFeatureSettings(m),
    color: m.textColor ?? "var(--mauve-12)",
  };

  return (
    <div className="h-20 border-b border-[var(--mauve-4)] flex items-center justify-center px-4 bg-[var(--mauve-1)] overflow-hidden flex-shrink-0">
      <span style={style} className="select-none">
        Hamburgevons
      </span>
    </div>
  );
}

// ─── Basics panel ─────────────────────────────────────────────────────────────

function BasicsPanel({
  node,
  u,
  setHover,
  onDrillUnderline,
}: {
  node: CanvasNode;
  u: (p: Partial<CanvasNode>) => void;
  setHover: (p: Partial<CanvasNode> | null) => void;
  onDrillUnderline: () => void;
}) {
  const align = node.textAlign ?? "left";
  const decoration = node.textDecoration ?? "none";
  const listStyle = node.listStyle ?? "none";

  type CaseKey = "none" | "uppercase" | "lowercase" | "capitalize" | "smallcaps";
  const currentCase: CaseKey = node.smallCaps
    ? "smallcaps"
    : node.textTransform === "uppercase" ? "uppercase"
    : node.textTransform === "lowercase" ? "lowercase"
    : node.textTransform === "capitalize" ? "capitalize"
    : "none";

  function applyCase(k: CaseKey) {
    if (k === "smallcaps") {
      u({ smallCaps: true, textTransform: "none" });
    } else {
      u({ smallCaps: false, textTransform: k === "none" ? "none" : k });
    }
  }

  return (
    <div className="py-1">
      {/* Alignment */}
      <ControlRow label="Alignment">
        {(["left", "center", "right", "justify"] as const).map((a) => (
          <TB
            key={a}
            active={align === a}
            onClick={() => u({ textAlign: a })}
            onMouseEnter={() => setHover({ textAlign: a })}
            onMouseLeave={() => setHover(null)}
            title={a}
          >
            {a === "left" ? "L" : a === "center" ? "C" : a === "right" ? "R" : "J"}
          </TB>
        ))}
      </ControlRow>

      {/* Decoration */}
      <ControlRow label="Decoration">
        <TB
          active={decoration === "none"}
          onClick={() => u({ textDecoration: "none" })}
          onMouseEnter={() => setHover({ textDecoration: "none" })}
          onMouseLeave={() => setHover(null)}
        >
          —
        </TB>
        <TB
          active={decoration === "underline"}
          onClick={() => u({ textDecoration: "underline" })}
          onMouseEnter={() => setHover({ textDecoration: "underline" })}
          onMouseLeave={() => setHover(null)}
          title="Underline"
        >
          <span style={{ textDecoration: "underline" }}>U</span>
        </TB>
        <TB
          active={decoration === "line-through"}
          onClick={() => u({ textDecoration: "line-through" })}
          onMouseEnter={() => setHover({ textDecoration: "line-through" })}
          onMouseLeave={() => setHover(null)}
          title="Strikethrough"
        >
          <span style={{ textDecoration: "line-through" }}>S</span>
        </TB>
        <button
          onClick={onDrillUnderline}
          title="Underline options"
          className="min-w-[24px] h-6 px-1 flex items-center justify-center rounded text-[10px] text-[var(--mauve-9)] hover:bg-[var(--mauve-4)] hover:text-[var(--mauve-12)] transition-colors"
        >
          <ChevronRight className="w-3 h-3" />
        </button>
      </ControlRow>

      {/* Case */}
      <ControlRow label="Case">
        <TB
          active={currentCase === "none"}
          onClick={() => applyCase("none")}
          onMouseEnter={() => setHover({ smallCaps: false, textTransform: "none" })}
          onMouseLeave={() => setHover(null)}
        >
          —
        </TB>
        <TB
          active={currentCase === "uppercase"}
          onClick={() => applyCase("uppercase")}
          onMouseEnter={() => setHover({ textTransform: "uppercase" })}
          onMouseLeave={() => setHover(null)}
          title="Uppercase"
        >
          AG
        </TB>
        <TB
          active={currentCase === "lowercase"}
          onClick={() => applyCase("lowercase")}
          onMouseEnter={() => setHover({ textTransform: "lowercase" })}
          onMouseLeave={() => setHover(null)}
          title="Lowercase"
        >
          ag
        </TB>
        <TB
          active={currentCase === "capitalize"}
          onClick={() => applyCase("capitalize")}
          onMouseEnter={() => setHover({ textTransform: "capitalize" })}
          onMouseLeave={() => setHover(null)}
          title="Title case"
        >
          Aa
        </TB>
        <TB
          active={currentCase === "smallcaps"}
          onClick={() => applyCase("smallcaps")}
          onMouseEnter={() => setHover({ smallCaps: true })}
          onMouseLeave={() => setHover(null)}
          title="Small caps"
        >
          <span style={{ fontVariantCaps: "small-caps" }}>Ag</span>
        </TB>
      </ControlRow>

      <PanelDivider />

      {/* Vertical trim */}
      <ControlRow label="Vertical trim">
        <TB
          active={(node.verticalTrim ?? "normal") === "normal"}
          onClick={() => u({ verticalTrim: "normal" })}
          title="Default trim"
        >
          <span className="font-mono text-[9px]">≈T</span>
        </TB>
        <TB
          active={node.verticalTrim === "cap-height"}
          onClick={() => u({ verticalTrim: "cap-height" })}
          title="Cap-height trim"
        >
          <span className="font-mono text-[9px] font-bold">T</span>
        </TB>
      </ControlRow>

      {/* List style */}
      <ControlRow label="List style">
        <TB
          active={listStyle === "none"}
          onClick={() => u({ listStyle: "none" })}
          title="No list"
        >
          —
        </TB>
        <TB
          active={listStyle === "bullets"}
          onClick={() => u({ listStyle: "bullets" })}
          title="Bullet list"
        >
          •
        </TB>
        <TB
          active={listStyle === "numbered"}
          onClick={() => u({ listStyle: "numbered" })}
          title="Numbered list"
        >
          1.
        </TB>
      </ControlRow>

      {/* Paragraph spacing */}
      <div className="flex items-center h-8 px-3 gap-2">
        <span className="text-[10px] text-[var(--mauve-10)] flex-1">Para. spacing</span>
        <InlineNumberInput
          value={node.paragraphSpacing ?? 0}
          unit="px"
          onChange={(v) => u({ paragraphSpacing: v })}
        />
      </div>

      {/* Truncate text */}
      <ControlRow label="Truncate text">
        <TB
          active={!node.truncateText}
          onClick={() => u({ truncateText: false })}
          title="Don't truncate"
        >
          —
        </TB>
        <TB
          active={node.truncateText === true}
          onClick={() => u({ truncateText: true })}
          title="Truncate with ellipsis"
          onMouseEnter={() => setHover({ truncateText: true })}
          onMouseLeave={() => setHover(null)}
        >
          A…
        </TB>
      </ControlRow>
    </div>
  );
}

// ─── Underline sub-panel ──────────────────────────────────────────────────────

function UnderlinePanel({
  node,
  u,
  setHover,
}: {
  node: CanvasNode;
  u: (p: Partial<CanvasNode>) => void;
  setHover: (p: Partial<CanvasNode> | null) => void;
}) {
  const decoration = node.textDecoration ?? "none";
  const decoStyle = node.textDecorationStyle ?? "solid";

  return (
    <div className="py-1">
      <ControlRow label="Decoration">
        <TB
          active={decoration === "none"}
          onClick={() => u({ textDecoration: "none" })}
          onMouseEnter={() => setHover({ textDecoration: "none" })}
          onMouseLeave={() => setHover(null)}
        >
          —
        </TB>
        <TB
          active={decoration === "underline"}
          onClick={() => u({ textDecoration: "underline" })}
          onMouseEnter={() => setHover({ textDecoration: "underline" })}
          onMouseLeave={() => setHover(null)}
          title="Underline"
        >
          <span style={{ textDecoration: "underline" }}>U</span>
        </TB>
        <TB
          active={decoration === "line-through"}
          onClick={() => u({ textDecoration: "line-through" })}
          onMouseEnter={() => setHover({ textDecoration: "line-through" })}
          onMouseLeave={() => setHover(null)}
          title="Strikethrough"
        >
          <span style={{ textDecoration: "line-through" }}>S</span>
        </TB>
      </ControlRow>

      <ControlRow label="Style">
        <TB
          active={decoStyle === "solid"}
          onClick={() => u({ textDecorationStyle: "solid" })}
          onMouseEnter={() => setHover({ textDecoration: "underline", textDecorationStyle: "solid" })}
          onMouseLeave={() => setHover(null)}
          title="Solid"
        >
          —
        </TB>
        <TB
          active={decoStyle === "dotted"}
          onClick={() => u({ textDecorationStyle: "dotted" })}
          onMouseEnter={() => setHover({ textDecoration: "underline", textDecorationStyle: "dotted" })}
          onMouseLeave={() => setHover(null)}
          title="Dotted"
        >
          <span className="tracking-tighter">···</span>
        </TB>
        <TB
          active={decoStyle === "wavy"}
          onClick={() => u({ textDecorationStyle: "wavy" })}
          onMouseEnter={() => setHover({ textDecoration: "underline", textDecorationStyle: "wavy" })}
          onMouseLeave={() => setHover(null)}
          title="Wavy"
        >
          ∿
        </TB>
      </ControlRow>

      <PanelDivider />

      <SliderRow
        label="Thickness"
        value={node.textDecorationThickness ?? 0}
        onChange={(v) => u({ textDecorationThickness: v })}
        onMouseEnter={() => setHover({ textDecoration: "underline" })}
        onMouseLeave={() => setHover(null)}
      />
      <SliderRow
        label="Offset"
        value={node.textDecorationOffset ?? 0}
        onChange={(v) => u({ textDecorationOffset: v })}
        onMouseEnter={() => setHover({ textDecoration: "underline" })}
        onMouseLeave={() => setHover(null)}
      />

      <PanelDivider />

      <ControlRow label="Skip ink">
        <TB
          active={node.textDecorationSkipInk !== false}
          onClick={() => u({ textDecorationSkipInk: true })}
          title="Skip descenders"
        >
          <span
            style={
              { textDecoration: "underline", textDecorationSkipInk: "auto" } as React.CSSProperties
            }
          >
            Ag
          </span>
        </TB>
        <TB
          active={node.textDecorationSkipInk === false}
          onClick={() => u({ textDecorationSkipInk: false })}
          title="Don't skip"
        >
          <span
            style={
              { textDecoration: "underline", textDecorationSkipInk: "none" } as React.CSSProperties
            }
          >
            Ag
          </span>
        </TB>
      </ControlRow>

      <div className="flex items-center h-8 px-3 gap-2">
        <span className="text-[10px] text-[var(--mauve-10)] flex-1">Color</span>
        <ColorPicker
          value={node.textDecorationColor ?? node.textColor ?? "#000000"}
          onChange={(v) => u({ textDecorationColor: v ?? undefined })}
          showInlineHex={false}
        />
      </div>
    </div>
  );
}

// ─── Details panel ────────────────────────────────────────────────────────────

function DetailsPanel({
  node,
  u,
  setHover,
}: {
  node: CanvasNode;
  u: (p: Partial<CanvasNode>) => void;
  setHover: (p: Partial<CanvasNode> | null) => void;
}) {
  type CaseKey = "none" | "uppercase" | "lowercase" | "capitalize" | "smallcaps";
  const currentCase: CaseKey = node.smallCaps
    ? "smallcaps"
    : node.textTransform === "uppercase" ? "uppercase"
    : node.textTransform === "lowercase" ? "lowercase"
    : node.textTransform === "capitalize" ? "capitalize"
    : "none";

  function applyCase(k: CaseKey) {
    if (k === "smallcaps") u({ smallCaps: true, textTransform: "none" });
    else u({ smallCaps: false, textTransform: k === "none" ? "none" : k });
  }

  // Stylistic sets to show (ss01–ss10)
  const SS_COUNT = 10;

  return (
    <div className="py-1">
      {/* Indentation */}
      <PanelSection label="Indentation">
        <ControlRow label="Hanging punctuation">
          <TB
            active={!node.hangingPunctuation}
            onClick={() => u({ hangingPunctuation: false })}
            onMouseEnter={() => setHover({ hangingPunctuation: false })}
            onMouseLeave={() => setHover(null)}
          >
            —
          </TB>
          <TB
            active={!!node.hangingPunctuation}
            onClick={() => u({ hangingPunctuation: true })}
            onMouseEnter={() => setHover({ hangingPunctuation: true })}
            onMouseLeave={() => setHover(null)}
            title="Hanging punctuation"
          >
            ✓
          </TB>
        </ControlRow>
        <ControlRow label="Hanging lists">
          <TB
            active={!node.hangingLists}
            onClick={() => u({ hangingLists: false })}
            onMouseEnter={() => setHover({ hangingLists: false })}
            onMouseLeave={() => setHover(null)}
          >
            —
          </TB>
          <TB
            active={!!node.hangingLists}
            onClick={() => u({ hangingLists: true })}
            onMouseEnter={() => setHover({ hangingLists: true })}
            onMouseLeave={() => setHover(null)}
            title="Hanging lists"
          >
            ✓
          </TB>
        </ControlRow>
        <div className="flex items-center h-8 px-3 gap-2">
          <span className="text-[10px] text-[var(--mauve-10)] flex-1">Para. indent</span>
          <InlineNumberInput
            value={node.paragraphIndent ?? 0}
            unit="px"
            onChange={(v) => u({ paragraphIndent: v })}
          />
        </div>
      </PanelSection>

      <PanelDivider />

      {/* Letter case */}
      <PanelSection label="Letter case">
        <ControlRow label="Case">
          <TB active={currentCase === "none"} onClick={() => applyCase("none")} onMouseEnter={() => setHover({ smallCaps: false, textTransform: "none" })} onMouseLeave={() => setHover(null)}>—</TB>
          <TB active={currentCase === "uppercase"} onClick={() => applyCase("uppercase")} onMouseEnter={() => setHover({ textTransform: "uppercase" })} onMouseLeave={() => setHover(null)} title="Uppercase">AG</TB>
          <TB active={currentCase === "lowercase"} onClick={() => applyCase("lowercase")} onMouseEnter={() => setHover({ textTransform: "lowercase" })} onMouseLeave={() => setHover(null)} title="Lowercase">ag</TB>
          <TB active={currentCase === "capitalize"} onClick={() => applyCase("capitalize")} onMouseEnter={() => setHover({ textTransform: "capitalize" })} onMouseLeave={() => setHover(null)} title="Title case">Aa</TB>
          <TB active={currentCase === "smallcaps"} onClick={() => applyCase("smallcaps")} onMouseEnter={() => setHover({ smallCaps: true })} onMouseLeave={() => setHover(null)} title="Small caps">
            <span style={{ fontVariantCaps: "small-caps" }}>Ag</span>
          </TB>
        </ControlRow>
        <ControlRow label="Case-sensitive forms">
          <TB active={!node.caseSensitiveForms} onClick={() => u({ caseSensitiveForms: false })} onMouseEnter={() => setHover({ caseSensitiveForms: false })} onMouseLeave={() => setHover(null)}>—</TB>
          <TB active={!!node.caseSensitiveForms} onClick={() => u({ caseSensitiveForms: true })} onMouseEnter={() => setHover({ caseSensitiveForms: true })} onMouseLeave={() => setHover(null)} title="Case-sensitive punctuation">✓</TB>
        </ControlRow>
      </PanelSection>

      <PanelDivider />

      {/* Numbers */}
      <PanelSection label="Numbers">
        <ControlRow label="Position">
          <TB
            active={node.numberPosition === "subscript"}
            onClick={() => u({ numberPosition: "subscript" })}
            onMouseEnter={() => setHover({ numberPosition: "subscript" })}
            onMouseLeave={() => setHover(null)}
            title="Subscript"
          >
            <span>A<sub>2</sub></span>
          </TB>
          <TB
            active={(node.numberPosition ?? "normal") === "normal"}
            onClick={() => u({ numberPosition: "normal" })}
            onMouseEnter={() => setHover({ numberPosition: "normal" })}
            onMouseLeave={() => setHover(null)}
            title="Normal"
          >
            A2
          </TB>
          <TB
            active={node.numberPosition === "superscript"}
            onClick={() => u({ numberPosition: "superscript" })}
            onMouseEnter={() => setHover({ numberPosition: "superscript" })}
            onMouseLeave={() => setHover(null)}
            title="Superscript"
          >
            <span>A<sup>2</sup></span>
          </TB>
        </ControlRow>
        <ControlRow label="Fractions">
          <TB active={!node.fractions} onClick={() => u({ fractions: false })} onMouseEnter={() => setHover({ fractions: false })} onMouseLeave={() => setHover(null)}>—</TB>
          <TB active={!!node.fractions} onClick={() => u({ fractions: true })} onMouseEnter={() => setHover({ fractions: true })} onMouseLeave={() => setHover(null)} title="OpenType fractions">✓</TB>
        </ControlRow>
      </PanelSection>

      <PanelDivider />

      {/* Letterforms */}
      <PanelSection label="Letterforms">
        <ControlRow label="Ligatures">
          <TB active={!node.ligatures} onClick={() => u({ ligatures: false })} onMouseEnter={() => setHover({ ligatures: false })} onMouseLeave={() => setHover(null)}>—</TB>
          <TB active={!!node.ligatures} onClick={() => u({ ligatures: true })} onMouseEnter={() => setHover({ ligatures: true })} onMouseLeave={() => setHover(null)} title="Standard ligatures (fi, fl, …)">✓</TB>
        </ControlRow>
        <ControlRow label="Contextual alternates">
          <TB active={!node.contextualAlternates} onClick={() => u({ contextualAlternates: false })} onMouseEnter={() => setHover({ contextualAlternates: false })} onMouseLeave={() => setHover(null)}>—</TB>
          <TB active={!!node.contextualAlternates} onClick={() => u({ contextualAlternates: true })} onMouseEnter={() => setHover({ contextualAlternates: true })} onMouseLeave={() => setHover(null)} title="Contextual alternates">✓</TB>
        </ControlRow>
        <ControlRow label="Ordinals">
          <TB active={!node.ordinals} onClick={() => u({ ordinals: false })} onMouseEnter={() => setHover({ ordinals: false })} onMouseLeave={() => setHover(null)}>—</TB>
          <TB active={!!node.ordinals} onClick={() => u({ ordinals: true })} onMouseEnter={() => setHover({ ordinals: true })} onMouseLeave={() => setHover(null)} title="Ordinal indicators">✓</TB>
        </ControlRow>
      </PanelSection>

      <PanelDivider />

      {/* Stylistic sets */}
      <PanelSection label="Stylistic sets">
        {Array.from({ length: SS_COUNT }, (_, i) => i + 1).map((n) => {
          const isActive = node.stylisticSets?.includes(n) ?? false;
          const label = `Alternative ${n}`;
          return (
            <ControlRow key={n} label={label}>
              <TB
                active={!isActive}
                onClick={() => u({ stylisticSets: (node.stylisticSets ?? []).filter((s) => s !== n) })}
                onMouseEnter={() => setHover({ stylisticSets: (node.stylisticSets ?? []).filter((s) => s !== n) })}
                onMouseLeave={() => setHover(null)}
              >
                —
              </TB>
              <TB
                active={isActive}
                onClick={() => {
                  if (!isActive) u({ stylisticSets: [...(node.stylisticSets ?? []), n] });
                }}
                onMouseEnter={() => setHover({ stylisticSets: [...((node.stylisticSets ?? []).filter((s) => s !== n)), n] })}
                onMouseLeave={() => setHover(null)}
                title={`Stylistic set ${n} (ss${String(n).padStart(2, "0")})`}
              >
                ✓
              </TB>
            </ControlRow>
          );
        })}
      </PanelSection>

      <div className="h-4" />
    </div>
  );
}

// ─── Main export ──────────────────────────────────────────────────────────────

export function AdvancedTypographyPanel({
  node,
  onClose,
}: {
  node: CanvasNode;
  onClose: () => void;
}) {
  const { updateNode } = useCanvasStore();
  const { rightPanelWidth } = useUIStore();
  const u = (p: Partial<CanvasNode>) => updateNode(node.id, p);

  const [activeTab, setActiveTab] = useState<"basics" | "details">("basics");
  const [subPanel, setSubPanel] = useState<null | "underline">(null);
  const [hoverOverride, setHoverOverride] = useState<Partial<CanvasNode> | null>(null);

  // Reset sub-panel when node changes
  useEffect(() => {
    setSubPanel(null);
    setHoverOverride(null);
  }, [node.id]);

  // Close on Escape
  useEffect(() => {
    function handler(e: KeyboardEvent) {
      if (e.key === "Escape") {
        if (subPanel) setSubPanel(null);
        else onClose();
      }
    }
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [subPanel, onClose]);

  const header = subPanel ? (
    <div className="flex items-center h-9 px-2 gap-1 border-b border-[var(--mauve-4)] flex-shrink-0">
      <button
        onClick={() => setSubPanel(null)}
        className="flex items-center gap-0.5 text-[10px] text-[var(--mauve-10)] hover:text-[var(--mauve-12)] transition-colors"
      >
        <ChevronLeft className="w-3 h-3" />
        Basics
      </button>
      <span className="text-[10px] text-[var(--mauve-7)]">/</span>
      <span className="text-[10px] text-[var(--mauve-12)] font-medium capitalize">{subPanel}</span>
      <div className="flex-1" />
      <button
        onClick={onClose}
        className="w-5 h-5 flex items-center justify-center rounded text-[var(--mauve-8)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)] transition-colors"
      >
        <X className="w-3 h-3" />
      </button>
    </div>
  ) : (
    <div className="flex items-center h-9 border-b border-[var(--mauve-4)] flex-shrink-0">
      {(["basics", "details"] as const).map((tab) => (
        <button
          key={tab}
          onClick={() => setActiveTab(tab)}
          className={cn(
            "flex-1 h-full text-[10px] font-medium capitalize transition-colors border-b-2",
            activeTab === tab
              ? "text-[var(--mauve-12)] border-[var(--violet-9)]"
              : "text-[var(--mauve-9)] border-transparent hover:text-[var(--mauve-11)]",
          )}
        >
          {tab}
        </button>
      ))}
      <button
        onClick={onClose}
        className="w-9 h-9 flex items-center justify-center flex-shrink-0 text-[var(--mauve-8)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)] transition-colors border-b-2 border-transparent"
      >
        <X className="w-3 h-3" />
      </button>
    </div>
  );

  return createPortal(
    <div
      style={{ right: rightPanelWidth }}
      className="fixed top-12 bottom-0 w-60 bg-[var(--mauve-2)] border-l border-[var(--mauve-5)] shadow-2xl flex flex-col z-40"
    >
      {header}
      <PreviewArea node={node} hoverOverride={hoverOverride} />
      <ScrollArea className="flex-1">
        {!subPanel && activeTab === "basics" && (
          <BasicsPanel
            node={node}
            u={u}
            setHover={setHoverOverride}
            onDrillUnderline={() => setSubPanel("underline")}
          />
        )}
        {subPanel === "underline" && (
          <UnderlinePanel node={node} u={u} setHover={setHoverOverride} />
        )}
        {!subPanel && activeTab === "details" && (
          <DetailsPanel node={node} u={u} setHover={setHoverOverride} />
        )}
      </ScrollArea>
    </div>,
    document.body,
  );
}
