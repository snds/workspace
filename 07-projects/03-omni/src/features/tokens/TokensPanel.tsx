import { useState, useMemo, useEffect, useRef, useCallback } from "react";
import { OmniIcon } from "@/core/icons";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem,
  DropdownMenuSeparator, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import { useColorSystemStore } from "@/stores/colorSystem.store";
import { useOnboardingStore } from "@/stores/onboarding.store";
import { useTokensStore } from "@/stores/tokens.store";
import type { DesignToken, DTCGType, ShadowValue } from "@/types/tokens";
import { isReference } from "@/types/tokens";
import type { TokenTier } from "@/core/tokens/tiers";
import {
  buildTree, exportDTCGJson, staticTokensToEntries, countUnderPrefix,
} from "./migration";
import { inferTokenType, suggestTokenName } from "./typeInference";
import { DESIGN_SYSTEM_PRESETS, makeColorSystem } from "./presets";

// ─── OmniIcon shims for existing JSX patterns ────────────────────────────────
function makeLucideShim(semanticName: string) {
  return function ShimIcon({ className }: { className?: string }) {
    const sizeMatch = className?.match(/w-(\d+(?:\.\d+)?)/);
    const size = sizeMatch ? parseFloat(sizeMatch[1]) * 4 : 16;
    // Extract color from className if present
    const colorMatch = className?.match(/text-\[(var\(--[^)]+\))\]/);
    const color = colorMatch ? colorMatch[1] : undefined;
    return <OmniIcon name={semanticName} size={size} color={color} className={className?.replace(/w-\S+\s*/g, '').replace(/h-\S+\s*/g, '').replace(/text-\[[^\]]+\]\s*/g, '').trim() || undefined} />;
  };
}

const ChevronDown = makeLucideShim("navigation/chevron-down");
const ChevronRight = makeLucideShim("navigation/chevron-right");
const Search = makeLucideShim("action/search");
const Download = makeLucideShim("action/download");
const Plus = makeLucideShim("action/add");
const Link = makeLucideShim("content/link");
const MoreHorizontal = makeLucideShim("action/more");
const Trash2 = makeLucideShim("action/delete");
const Copy = makeLucideShim("action/copy");
const Pencil = makeLucideShim("action/edit");
const FolderPlus = makeLucideShim("action/folder-add");
const Sparkles = makeLucideShim("misc/sparkles");

// ─── Tier badge component ────────────────────────────────────────────────────

const TIER_COLORS: Record<TokenTier, string> = {
  primitive: "bg-[var(--blue-9)]",
  semantic: "bg-[var(--violet-9)]",
  component: "bg-[var(--green-9)]",
};

function TierBadge({ tier }: { tier: TokenTier | null }) {
  if (!tier) return null;
  return (
    <span
      className={cn(
        "px-1 py-0.5 rounded text-[8px] font-semibold uppercase tracking-wider text-white leading-none flex-shrink-0",
        TIER_COLORS[tier],
      )}
    >
      {tier.slice(0, 4)}
    </span>
  );
}

// ─── Type chip ────────────────────────────────────────────────────────────────

function TypeChip({ type, resolvedValue }: { type?: DTCGType; resolvedValue: string }) {
  if (type === "color") {
    const isHex = /^#[0-9a-f]{3,8}$/i.test(resolvedValue);
    return (
      <div
        className="w-3 h-3 rounded-sm border border-[var(--mauve-5)] flex-shrink-0"
        style={{ background: isHex ? resolvedValue : "var(--mauve-5)" }}
        title={resolvedValue}
      />
    );
  }
  const map: Record<DTCGType, string> = {
    "color": "■",
    "dimension": "↕",
    "font-family": "Aa",
    "font-weight": "W",
    "font-style": "I",
    "number": "#",
    "string": "T",
    "duration": "⏱",
    "cubic-bezier": "∿",
    "shadow": "◫",
    "gradient": "▦",
    "typography": "¶",
    "transition": "→",
  };
  return (
    <span className="w-5 text-center text-[9px] font-semibold text-[var(--mauve-8)] flex-shrink-0 leading-none select-none">
      {type ? map[type] ?? "?" : "?"}
    </span>
  );
}

// ─── Reference filter mode (persisted across editor instances) ────────────────

type RefFilterMode = "all" | "primitive" | "semantic";
let _lastRefFilterMode: RefFilterMode = "all";

// ─── Token reference picker ───────────────────────────────────────────────────

function TokenRefPicker({
  query,
  tokenType,
  onSelect,
  onClose,
}: {
  query: string;
  tokenType?: DTCGType;
  onSelect: (path: string) => void;
  onClose: () => void;
}) {
  const entries = useTokensStore((s) => s.entries);
  const getDisplayValue = useTokensStore((s) => s.getDisplayValue);
  const [activeIdx, setActiveIdx] = useState(0);
  const [filterMode, setFilterMode] = useState<RefFilterMode>(_lastRefFilterMode);

  function setMode(mode: RefFilterMode) {
    _lastRefFilterMode = mode;
    setFilterMode(mode);
  }

  const matches = useMemo(() => {
    let paths = tokenType
      ? Object.entries(entries).filter(([, t]) => t.$type === tokenType).map(([p]) => p)
      : Object.keys(entries);
    if (filterMode === "primitive") paths = paths.filter((p) => !isReference(entries[p]!.$value));
    else if (filterMode === "semantic") paths = paths.filter((p) => isReference(entries[p]!.$value));
    return paths
      .filter((p) => p.toLowerCase().includes(query.toLowerCase()))
      .slice(0, 20);
  }, [entries, query, tokenType, filterMode]);

  useEffect(() => { setActiveIdx(0); }, [matches]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "ArrowDown") { e.preventDefault(); setActiveIdx((i) => Math.min(i + 1, matches.length - 1)); }
      if (e.key === "ArrowUp")   { e.preventDefault(); setActiveIdx((i) => Math.max(i - 1, 0)); }
      if (e.key === "Enter")     { e.preventDefault(); if (matches[activeIdx]) onSelect(matches[activeIdx]!); }
      if (e.key === "Escape")    { e.preventDefault(); onClose(); }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [matches, activeIdx, onSelect, onClose]);

  return (
    <div className="absolute left-0 right-0 top-full z-50 mt-0.5 bg-[var(--mauve-2)] border border-[var(--mauve-6)] rounded shadow-lg overflow-hidden flex flex-col max-h-52">
      {/* Primitive / Semantic toggle */}
      <div className="flex gap-0.5 p-1 border-b border-[var(--mauve-5)] flex-shrink-0">
        {(["all", "primitive", "semantic"] as const).map((mode) => (
          <button
            key={mode}
            onMouseDown={(e) => { e.preventDefault(); setMode(mode); }}
            className={cn(
              "flex-1 h-4 rounded text-[9px] capitalize transition-colors",
              filterMode === mode
                ? "bg-[var(--violet-9)] text-white"
                : "bg-[var(--mauve-4)] text-[var(--mauve-8)] hover:bg-[var(--mauve-5)]",
            )}
          >
            {mode}
          </button>
        ))}
      </div>
      {/* Results */}
      <div className="overflow-y-auto">
        {matches.length === 0 ? (
          <div className="px-2 py-2 text-[10px] text-[var(--mauve-7)] text-center">No matches</div>
        ) : matches.map((path, i) => {
          const token = entries[path]!;
          const resolved = getDisplayValue(path);
          return (
            <button
              key={path}
              onMouseDown={(e) => { e.preventDefault(); onSelect(path); }}
              className={cn(
                "w-full flex items-center gap-2 px-2 h-7 text-left transition-colors",
                i === activeIdx ? "bg-[var(--mauve-4)]" : "hover:bg-[var(--mauve-3)]",
              )}
            >
              <TypeChip type={token.$type} resolvedValue={resolved} />
              <span className="text-[10px] text-[var(--mauve-11)] flex-1 truncate font-mono">{path}</span>
              <span className="text-[10px] text-[var(--mauve-7)] font-mono flex-shrink-0">{resolved}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ─── Token display formatter ──────────────────────────────────────────────────

/** Returns a human-readable display string for any token value */
function formatTokenDisplay(token: DesignToken): string {
  if (typeof token.$value !== "object") return String(token.$value);
  if (token.$type === "shadow") {
    const sv = token.$value as ShadowValue;
    const parts = [sv.offsetX, sv.offsetY, sv.blur, sv.spread, sv.color].filter(Boolean);
    return (sv.inset ? "inset " : "") + parts.join(" ");
  }
  return JSON.stringify(token.$value);
}

// ─── Specialized value editors ────────────────────────────────────────────────

// Common font families for typeahead suggestions
const COMMON_FONT_FAMILIES = [
  "Inter", "system-ui", "-apple-system", "Helvetica Neue", "Arial", "sans-serif",
  "JetBrains Mono", "Fira Code", "SF Mono", "Menlo", "Consolas", "monospace",
  "Georgia", "Times New Roman", "Palatino", "serif",
  "Roboto", "Open Sans", "Lato", "Poppins", "Nunito", "DM Sans",
];

function FontFamilyEditor({
  currentValue,
  onCommit,
  onCancel,
}: {
  currentValue: string;
  onCommit: (value: string) => void;
  onCancel: () => void;
}) {
  const [chips, setChips] = useState(() =>
    currentValue.split(",").map((f) => f.trim()).filter(Boolean),
  );
  const [inputVal, setInputVal] = useState("");
  const [showSuggestions, setShowSuggestions] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { inputRef.current?.focus(); }, []);

  const suggestions = useMemo(() =>
    COMMON_FONT_FAMILIES.filter(
      (f) => !chips.includes(f) && f.toLowerCase().includes(inputVal.toLowerCase()),
    ).slice(0, 8),
    [chips, inputVal],
  );

  function addFont(font: string) {
    const trimmed = font.trim();
    if (trimmed && !chips.includes(trimmed)) setChips((c) => [...c, trimmed]);
    setInputVal("");
  }

  function removeChip(idx: number) {
    setChips((c) => c.filter((_, i) => i !== idx));
  }

  function commit() {
    onCommit(chips.join(", "));
  }

  return (
    <div className="relative flex-1 min-w-0">
      <div
        className="flex flex-wrap gap-0.5 items-center min-h-5 bg-[var(--mauve-4)] border border-[var(--violet-7)] rounded px-1 py-0.5 cursor-text"
        onClick={() => inputRef.current?.focus()}
      >
        {chips.map((chip, i) => (
          <span
            key={i}
            className="flex items-center gap-0.5 bg-[var(--mauve-6)] rounded px-1 h-4 text-[9px] font-mono text-[var(--mauve-12)] flex-shrink-0"
          >
            {chip}
            <button
              onMouseDown={(e) => { e.preventDefault(); removeChip(i); }}
              className="text-[var(--mauve-8)] hover:text-[var(--mauve-12)] leading-none"
            >
              ×
            </button>
          </span>
        ))}
        <input
          ref={inputRef}
          value={inputVal}
          onChange={(e) => { setInputVal(e.target.value); setShowSuggestions(true); }}
          onKeyDown={(e) => {
            if ((e.key === "Enter" || e.key === ",") && inputVal.trim()) {
              e.preventDefault(); addFont(inputVal);
            } else if (e.key === "Enter" && !inputVal) {
              commit();
            } else if (e.key === "Escape") {
              onCancel();
            } else if (e.key === "Backspace" && !inputVal && chips.length > 0) {
              removeChip(chips.length - 1);
            }
          }}
          onFocus={() => setShowSuggestions(true)}
          onBlur={() => { setTimeout(commit, 150); setShowSuggestions(false); }}
          placeholder={chips.length === 0 ? "Add fonts…" : ""}
          className="flex-1 min-w-0 bg-transparent text-[10px] font-mono text-[var(--mauve-12)] outline-none"
          style={{ minWidth: chips.length === 0 ? 80 : 48 }}
        />
      </div>
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute left-0 right-0 top-full z-50 mt-0.5 bg-[var(--mauve-2)] border border-[var(--mauve-6)] rounded shadow-lg overflow-hidden max-h-32 overflow-y-auto">
          {suggestions.map((f) => (
            <button
              key={f}
              onMouseDown={(e) => { e.preventDefault(); addFont(f); setShowSuggestions(false); inputRef.current?.focus(); }}
              className="w-full px-2 h-6 text-left text-[10px] font-mono text-[var(--mauve-11)] hover:bg-[var(--mauve-3)] transition-colors"
            >
              {f}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

const FONT_WEIGHT_OPTIONS: { value: number; label: string }[] = [
  { value: 100, label: "Thin" },
  { value: 200, label: "XLight" },
  { value: 300, label: "Light" },
  { value: 400, label: "Regular" },
  { value: 500, label: "Medium" },
  { value: 600, label: "SemiBold" },
  { value: 700, label: "Bold" },
  { value: 800, label: "XBold" },
  { value: 900, label: "Black" },
];

function FontWeightEditor({
  currentValue,
  onCommit,
  onCancel,
}: {
  currentValue: string | number;
  onCommit: (value: number) => void;
  onCancel: () => void;
}) {
  const current = Number(currentValue);
  useEffect(() => {
    function onKey(e: KeyboardEvent) { if (e.key === "Escape") onCancel(); }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel]);

  return (
    <div className="relative flex-1 min-w-0 flex flex-wrap gap-0.5">
      {FONT_WEIGHT_OPTIONS.map(({ value, label }) => (
        <button
          key={value}
          onMouseDown={(e) => { e.preventDefault(); onCommit(value); }}
          className={cn(
            "h-5 px-1.5 rounded text-[9px] transition-colors",
            current === value
              ? "bg-[var(--violet-9)] text-white"
              : "bg-[var(--mauve-4)] text-[var(--mauve-9)] hover:bg-[var(--mauve-5)]",
          )}
          title={label}
          style={{ fontWeight: value }}
        >
          {value}
        </button>
      ))}
    </div>
  );
}

const DIMENSION_UNITS = ["px", "rem", "em", "%", "vh", "vw"] as const;

function DimensionEditor({
  currentValue,
  onCommit,
  onCancel,
}: {
  currentValue: string;
  onCommit: (value: string) => void;
  onCancel: () => void;
}) {
  const m = String(currentValue).match(/^(-?[\d.]+)\s*(.*)$/);
  const [num, setNum] = useState(m ? m[1]! : String(currentValue));
  const [unit, setUnit] = useState<string>(m && m[2] ? m[2].trim() : "px");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { inputRef.current?.focus(); inputRef.current?.select(); }, []);

  function commit() {
    const n = num.trim();
    onCommit(n === "0" ? "0" : `${n}${unit}`);
  }

  return (
    <div className="relative flex-1 min-w-0 flex items-center gap-0.5">
      <input
        ref={inputRef}
        type="number"
        value={num}
        onChange={(e) => setNum(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter") { e.preventDefault(); commit(); }
          if (e.key === "Escape") onCancel();
        }}
        onBlur={commit}
        className="w-16 flex-shrink-0 bg-[var(--mauve-4)] border border-[var(--violet-7)] rounded px-1.5 h-5 text-[10px] font-mono text-[var(--mauve-12)] outline-none text-right [appearance:textfield]"
      />
      <div className="flex rounded overflow-hidden border border-[var(--mauve-5)] flex-shrink-0">
        {DIMENSION_UNITS.map((u) => (
          <button
            key={u}
            onMouseDown={(e) => { e.preventDefault(); setUnit(u); setTimeout(() => inputRef.current?.focus(), 0); }}
            className={cn(
              "h-5 px-1 text-[9px] transition-colors",
              unit === u
                ? "bg-[var(--violet-9)] text-white"
                : "bg-[var(--mauve-3)] text-[var(--mauve-8)] hover:bg-[var(--mauve-4)]",
            )}
          >
            {u}
          </button>
        ))}
      </div>
    </div>
  );
}

function ShadowEditor({
  currentValue,
  onCommit,
  onCancel,
}: {
  currentValue: ShadowValue | string;
  onCommit: (value: ShadowValue) => void;
  onCancel: () => void;
}) {
  const initial: ShadowValue =
    typeof currentValue === "object"
      ? currentValue
      : { color: "#000000", offsetX: "0", offsetY: "0", blur: "0", spread: "0", inset: false };
  const [fields, setFields] = useState<ShadowValue>(initial);

  function update<K extends keyof ShadowValue>(key: K, val: ShadowValue[K]) {
    setFields((prev) => ({ ...prev, [key]: val }));
  }

  useEffect(() => {
    function onKey(e: KeyboardEvent) { if (e.key === "Escape") onCancel(); }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel]);

  const DIMS: Array<[keyof ShadowValue, string]> = [
    ["offsetX", "X"], ["offsetY", "Y"], ["blur", "Blur"], ["spread", "Spread"],
  ];

  return (
    <div className="relative flex-1 min-w-0">
      <div className="flex flex-col gap-0.5 p-1.5 bg-[var(--mauve-4)] border border-[var(--violet-7)] rounded">
        <div className="grid grid-cols-2 gap-1">
          {DIMS.map(([key, label]) => (
            <label key={key} className="flex items-center gap-1">
              <span className="text-[9px] text-[var(--mauve-7)] w-8 flex-shrink-0">{label}</span>
              <input
                autoFocus={key === "offsetX"}
                value={String(fields[key] ?? "")}
                onChange={(e) => update(key, e.target.value as ShadowValue[typeof key])}
                onKeyDown={(e) => { if (e.key === "Escape") onCancel(); }}
                className="flex-1 min-w-0 bg-[var(--mauve-3)] border border-[var(--mauve-5)] rounded px-1 h-4 text-[9px] font-mono text-[var(--mauve-12)] outline-none text-right"
              />
            </label>
          ))}
        </div>
        <label className="flex items-center gap-1">
          <span className="text-[9px] text-[var(--mauve-7)] w-8 flex-shrink-0">Color</span>
          <div className="flex items-center gap-0.5 flex-1 min-w-0">
            <input
              type="color"
              value={/^#[0-9a-f]{6}$/i.test(String(fields.color)) ? String(fields.color) : "#000000"}
              onChange={(e) => update("color", e.target.value)}
              className="w-4 h-4 rounded border-0 p-0 cursor-pointer flex-shrink-0"
            />
            <input
              value={String(fields.color)}
              onChange={(e) => update("color", e.target.value)}
              onKeyDown={(e) => { if (e.key === "Escape") onCancel(); }}
              className="flex-1 min-w-0 bg-[var(--mauve-3)] border border-[var(--mauve-5)] rounded px-1 h-4 text-[9px] font-mono text-[var(--mauve-12)] outline-none"
            />
          </div>
        </label>
        <div className="flex items-center gap-1.5">
          <label className="flex items-center gap-1 cursor-pointer">
            <input
              type="checkbox"
              checked={!!fields.inset}
              onChange={(e) => update("inset", e.target.checked)}
              className="w-3 h-3"
            />
            <span className="text-[9px] text-[var(--mauve-9)]">Inset</span>
          </label>
          <button
            onMouseDown={(e) => { e.preventDefault(); onCommit(fields); }}
            className="ml-auto h-4 px-2 rounded text-[9px] bg-[var(--violet-9)] text-white hover:bg-[var(--violet-10)] transition-colors"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Token value editor ───────────────────────────────────────────────────────

function TokenValueEditor({
  path,
  token,
  onDone,
}: {
  path: string;
  token: DesignToken;
  onDone: () => void;
}) {
  const setToken = useTokensStore((s) => s.setToken);
  const rawValue = typeof token.$value === "object"
    ? JSON.stringify(token.$value)
    : String(token.$value);
  const isCurrentRef = isReference(token.$value);

  // Ref mode: search query for the typeahead (strip braces from current ref value)
  const [refQuery, setRefQuery] = useState(
    isCurrentRef ? rawValue.slice(1, -1) : "",
  );

  // Literal mode: directly editable text
  const [value, setValue] = useState(rawValue);
  const [showPicker, setShowPicker] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
    if (!isCurrentRef) inputRef.current?.select();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Derived query for literal→ref mode (user typed `{...`)
  const derivedRefQuery = useMemo(() => {
    const m = value.match(/\{([^}]*)$/);
    return m ? m[1]! : "";
  }, [value]);

  function commitLiteral(val: string) {
    const trimmed = val.trim();
    if (trimmed !== rawValue) setToken(path, { ...token, $value: trimmed });
    onDone();
  }

  function onSelectRef(refPath: string) {
    setToken(path, { ...token, $value: `{${refPath}}` });
    onDone();
  }

  // ── Case 1: current value is a reference → immediate typeahead, no commit until selected ──
  if (isCurrentRef) {
    return (
      <div className="relative flex-1 min-w-0">
        <input
          ref={inputRef}
          value={refQuery}
          onChange={(e) => setRefQuery(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Escape") { e.stopPropagation(); onDone(); }
          }}
          onBlur={() => onDone()}
          placeholder="Filter tokens…"
          className="w-full bg-[var(--mauve-4)] border border-[var(--violet-7)] rounded px-1.5 h-5 text-[10px] font-mono text-[var(--mauve-12)] outline-none"
        />
        <TokenRefPicker
          query={refQuery}
          tokenType={token.$type}
          onSelect={onSelectRef}
          onClose={onDone}
        />
      </div>
    );
  }

  // ── Case 2: literal value → type-specific editor ──

  // font-family: chip multi-select for font stacks
  if (token.$type === "font-family") {
    return (
      <FontFamilyEditor
        currentValue={rawValue}
        onCommit={(v) => { if (v !== rawValue) setToken(path, { ...token, $value: v }); onDone(); }}
        onCancel={onDone}
      />
    );
  }

  // font-weight: pill select of standard numeric weights
  if (token.$type === "font-weight") {
    return (
      <FontWeightEditor
        currentValue={rawValue}
        onCommit={(v) => { setToken(path, { ...token, $value: v }); onDone(); }}
        onCancel={onDone}
      />
    );
  }

  // dimension: number input + unit toggle (px/rem/em/%)
  if (token.$type === "dimension") {
    return (
      <DimensionEditor
        currentValue={rawValue}
        onCommit={(v) => { if (v !== rawValue) setToken(path, { ...token, $value: v }); onDone(); }}
        onCancel={onDone}
      />
    );
  }

  // shadow: structured offsetX/Y/blur/spread/color/inset form
  if (token.$type === "shadow") {
    return (
      <ShadowEditor
        currentValue={token.$value as ShadowValue | string}
        onCommit={(v) => { setToken(path, { ...token, $value: v }); onDone(); }}
        onCancel={onDone}
      />
    );
  }

  // Default: editable text input, type `{` to open ref picker
  const isRefMode = value.includes("{") && !value.includes("}");

  return (
    <div className="relative flex-1 min-w-0">
      <div className="flex items-center gap-1">
        {token.$type === "color" && (
          <input
            type="color"
            value={typeof token.$value === "string" && /^#[0-9a-f]{6}$/i.test(token.$value) ? token.$value : "#888888"}
            onChange={(e) => { setValue(e.target.value); commitLiteral(e.target.value); }}
            className="w-4 h-4 rounded border-0 p-0 cursor-pointer flex-shrink-0"
            title="Pick color"
          />
        )}
        <input
          ref={inputRef}
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
            setShowPicker(e.target.value.includes("{") && !e.target.value.includes("}"));
          }}
          onKeyDown={(e) => {
            if (e.key === "Escape") { e.stopPropagation(); onDone(); }
            else if (e.key === "Enter" && !showPicker) { commitLiteral(value); }
            else if (e.key === "{") setShowPicker(true);
          }}
          onBlur={() => { if (!showPicker) commitLiteral(value); }}
          className="flex-1 min-w-0 bg-[var(--mauve-4)] border border-[var(--violet-7)] rounded px-1.5 h-5 text-[10px] font-mono text-[var(--mauve-12)] outline-none text-right"
        />
        {token.$type === "color" && (
          <button
            onMouseDown={(e) => { e.preventDefault(); setValue("{"); setShowPicker(true); inputRef.current?.focus(); }}
            title="Link to token"
            className="text-[var(--mauve-7)] hover:text-[var(--mauve-11)]"
          >
            <Link className="w-3 h-3" />
          </button>
        )}
      </div>
      {showPicker && isRefMode && (
        <TokenRefPicker
          query={derivedRefQuery}
          tokenType={token.$type}
          onSelect={onSelectRef}
          onClose={() => setShowPicker(false)}
        />
      )}
    </div>
  );
}

// ─── New token row ────────────────────────────────────────────────────────────

const TYPE_PLACEHOLDERS: Partial<Record<DTCGType, string>> = {
  color: "#000000 or {path.to.token}",
  dimension: "16px",
  "font-family": "Inter, sans-serif",
  "font-weight": "400",
  number: "1.5",
  duration: "200ms",
  shadow: "0 1px 3px rgba(0,0,0,0.1)",
};

function NewTokenRow({
  groupPath,
  onDone,
}: {
  groupPath: string;
  onDone: () => void;
}) {
  const setToken = useTokensStore((s) => s.setToken);
  const entries = useTokensStore((s) => s.entries);
  const [step, setStep] = useState<"name" | "value">("name");
  const [name, setName] = useState("");
  const [type, setType] = useState<DTCGType>("string");
  const [aiInferred, setAiInferred] = useState(false);
  const [inferring, setInferring] = useState(true);
  const [nameSuggestion, setNameSuggestion] = useState<string | null>(null);
  const [value, setValue] = useState("");
  const nameRef = useRef<HTMLInputElement>(null);
  const valueRef = useRef<HTMLInputElement>(null);

  // Infer type from group path on mount
  useEffect(() => {
    if (!groupPath) { setInferring(false); return; }
    let cancelled = false;
    inferTokenType(groupPath).then((t) => {
      if (cancelled) return;
      setType(t);
      setAiInferred(true);
    }).finally(() => {
      if (!cancelled) setInferring(false);
    });
    return () => { cancelled = true; };
  }, [groupPath]);

  // Debounced name suggestion — fires 600 ms after user stops typing
  useEffect(() => {
    setNameSuggestion(null);
    if (!name || name.length < 2) return;
    const timer = setTimeout(async () => {
      const suggestion = await suggestTokenName(groupPath, name, type);
      setNameSuggestion(suggestion);
    }, 600);
    return () => clearTimeout(timer);
  }, [name, groupPath, type]);

  useEffect(() => { nameRef.current?.focus(); }, []);
  useEffect(() => { if (step === "value") valueRef.current?.focus(); }, [step]);

  // Global Escape listener — dismiss the row regardless of focus state
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") { e.stopPropagation(); onDone(); }
    }
    window.addEventListener("keydown", onKey, true);
    return () => window.removeEventListener("keydown", onKey, true);
  }, [onDone]);

  const fullPath = groupPath ? `${groupPath}.${name}` : name;
  const isDupe = name.length > 0 && fullPath in entries;
  const isInvalid = name.includes(".") || name.startsWith("$");

  function commitName() {
    if (!name || isInvalid || isDupe) return;
    setStep("value");
  }

  function commitValue() {
    if (!value) { onDone(); return; }
    setToken(fullPath, { $value: value, $type: type });
    onDone();
  }

  const typeOptions: DTCGType[] = ["color", "dimension", "font-family", "font-weight", "number", "string", "duration", "shadow", "gradient", "typography", "transition", "cubic-bezier", "font-style"];
  const placeholder = TYPE_PLACEHOLDERS[type] ?? "value";

  return (
    <div
      className="border-b border-[var(--mauve-5)] bg-[var(--mauve-2)]"
      style={{ paddingLeft: `${(step === "name" ? 1 : 1) * 12 + 8}px` }}
    >
      {step === "name" ? (
        /* ── Step 1: name + type ── */
        <div className="flex flex-col gap-1 py-1.5 pr-2">
          <div className="flex items-center gap-1.5">
            <input
              ref={nameRef}
              value={name}
              onChange={(e) => setName(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") commitName(); if (e.key === "Escape") onDone(); }}
              placeholder="token-name"
              className={cn(
                "flex-1 min-w-0 bg-[var(--mauve-4)] border rounded px-2 h-6 text-xs font-mono outline-none",
                isDupe || isInvalid
                  ? "border-red-500 text-red-400"
                  : "border-[var(--violet-7)] text-[var(--mauve-12)]",
              )}
            />
            <button
              onClick={commitName}
              disabled={!name || isInvalid || isDupe}
              className="flex-shrink-0 h-6 px-2 rounded text-[10px] bg-[var(--violet-9)] text-white hover:bg-[var(--violet-10)] transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Next →
            </button>
          </div>
          {/* AI name suggestion */}
          {nameSuggestion && (
            <div className="flex items-center gap-1">
              <span className="text-[9px] text-[var(--violet-8)]">✨ Consider:</span>
              <button
                onClick={() => { setName(nameSuggestion); setNameSuggestion(null); nameRef.current?.focus(); }}
                className="text-[9px] text-[var(--violet-9)] font-mono hover:underline"
              >
                {nameSuggestion}
              </button>
            </div>
          )}
          {/* Type selector row */}
          <div className="flex items-center gap-1.5">
            <span className="text-[9px] text-[var(--mauve-7)] flex-shrink-0 w-6">type</span>
            <div className="flex flex-wrap gap-1 flex-1">
              {typeOptions.map((t) => (
                <button
                  key={t}
                  onClick={() => { setType(t); setAiInferred(false); }}
                  className={cn(
                    "h-5 px-1.5 rounded text-[9px] transition-colors font-mono",
                    type === t
                      ? "bg-[var(--violet-9)] text-white"
                      : "bg-[var(--mauve-4)] text-[var(--mauve-9)] hover:bg-[var(--mauve-5)]",
                  )}
                >
                  {t}
                </button>
              ))}
            </div>
            {inferring && (
              <span title="Inferring type…">
                <Sparkles className="w-3 h-3 text-[var(--mauve-7)] animate-pulse flex-shrink-0" />
              </span>
            )}
            {!inferring && aiInferred && (
              <span title="Type inferred by AI">
                <Sparkles className="w-3 h-3 text-[var(--violet-8)] flex-shrink-0" />
              </span>
            )}
          </div>
        </div>
      ) : (
        /* ── Step 2: value ── */
        <div className="flex items-center gap-1.5 h-8 pr-2">
          <span className="text-[9px] text-[var(--mauve-7)] font-mono truncate" style={{ maxWidth: 64 }}>{name}</span>
          <span className="text-[9px] text-[var(--mauve-6)] font-mono flex-shrink-0">{type}</span>
          <input
            ref={valueRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") commitValue(); if (e.key === "Escape") onDone(); }}
            placeholder={placeholder}
            className="flex-1 min-w-0 bg-[var(--mauve-4)] border border-[var(--violet-7)] rounded px-2 h-6 text-[10px] font-mono text-[var(--mauve-12)] outline-none"
          />
          <button
            onClick={commitValue}
            className="flex-shrink-0 h-6 px-2 rounded text-[10px] bg-[var(--violet-9)] text-white hover:bg-[var(--violet-10)] transition-colors"
          >
            Add
          </button>
        </div>
      )}
    </div>
  );
}

// ─── Token leaf row ───────────────────────────────────────────────────────────

function TokenLeafRow({
  path,
  token,
  depth,
}: {
  path: string;
  token: DesignToken;
  depth: number;
}) {
  const setToken = useTokensStore((s) => s.setToken);
  const removeToken = useTokensStore((s) => s.removeToken);
  const duplicateToken = useTokensStore((s) => s.duplicateToken);
  const resolvedDisplay = useTokensStore((s) => s.getDisplayValue(path));
  const tier = useTokensStore((s) => s.getTier(path));
  const [editing, setEditing] = useState(false);
  const [moving, setMoving] = useState(false);
  const [moveTarget, setMoveTarget] = useState("");
  const [moveError, setMoveError] = useState("");
  const [moveSuggestion, setMoveSuggestion] = useState<string | null>(null);
  const [hovered, setHovered] = useState(false);
  const [modKeyHeld, setModKeyHeld] = useState(false);
  const moveRef = useRef<HTMLInputElement>(null);

  const parts = path.split(".");
  const name = parts[parts.length - 1] ?? path;
  const rawDisplay = formatTokenDisplay(token);
  const isRef = isReference(token.$value);

  // Pre-fill and focus move input when moving state activates
  useEffect(() => {
    if (moving) {
      setMoveTarget(path);
      setMoveError("");
      setMoveSuggestion(null);
      setTimeout(() => { moveRef.current?.focus(); moveRef.current?.select(); }, 0);
    }
  }, [moving, path]);

  // Debounced name suggestion while user edits the move target path
  useEffect(() => {
    if (!moving || !moveTarget) return;
    setMoveSuggestion(null);
    const segments = moveTarget.split(".");
    const leafName = segments[segments.length - 1] ?? "";
    const parentPath = segments.slice(0, -1).join(".");
    if (leafName.length < 2) return;
    const timer = setTimeout(async () => {
      const suggestion = await suggestTokenName(parentPath, leafName, token.$type ?? "string");
      setMoveSuggestion(suggestion);
    }, 600);
    return () => clearTimeout(timer);
  }, [moveTarget, moving, token.$type]);

  // Track modifier key state only while hovering over a reference token
  useEffect(() => {
    if (!hovered || !isRef) return;
    function onKeyDown(e: KeyboardEvent) { if (e.metaKey || e.ctrlKey) setModKeyHeld(true); }
    function onKeyUp(e: KeyboardEvent) { if (!e.metaKey && !e.ctrlKey) setModKeyHeld(false); }
    window.addEventListener("keydown", onKeyDown);
    window.addEventListener("keyup", onKeyUp);
    return () => {
      window.removeEventListener("keydown", onKeyDown);
      window.removeEventListener("keyup", onKeyUp);
      setModKeyHeld(false);
    };
  }, [hovered, isRef]);

  function handleDelete() {
    if (token.$extensions?.["omni.readonly"]) {
      if (!window.confirm(`"${name}" is a system token. Delete it anyway?`)) return;
    }
    removeToken(path);
  }

  function handleDuplicate() {
    let destPath = `${path}-copy`;
    const entries = useTokensStore.getState().entries;
    let n = 2;
    while (destPath in entries) { destPath = `${path}-copy${n++}`; }
    duplicateToken(path, destPath);
  }

  function copyPath() {
    navigator.clipboard.writeText(path).catch(() => {});
  }

  function commitMove() {
    const newPath = moveTarget.trim();
    if (!newPath || newPath === path) { setMoving(false); return; }

    // Validate format: no leading/trailing dots, no $, no consecutive dots
    if (
      newPath.startsWith(".") || newPath.endsWith(".") ||
      newPath.includes("..") || newPath.startsWith("$") ||
      /[^a-zA-Z0-9.\-_]/.test(newPath)
    ) {
      setMoveError("Invalid path — use dot-separated segments (a-z, 0-9, -, _)");
      return;
    }

    // Check for collision
    const currentEntries = useTokensStore.getState().entries;
    if (newPath in currentEntries) {
      setMoveError(`"${newPath}" already exists — token kept at its current location`);
      return;
    }

    // Execute: add at new path, remove old
    setToken(newPath, { ...token });
    removeToken(path);
    setMoving(false);
  }

  // Editors that expand vertically (shadow form, font-family chips, font-weight pills) need top alignment
  const needsTopAlign = moving || (editing && (token.$type === "shadow" || token.$type === "font-family" || token.$type === "font-weight"));

  return (
    <div
      className={cn(
        "group flex items-center gap-1.5 px-2 hover:bg-[var(--mauve-3)] transition-colors border-b border-[var(--mauve-4)] last:border-0",
        needsTopAlign ? "py-1 min-h-8 items-start" : "h-8",
      )}
      style={{ paddingLeft: `${depth * 12 + 8}px` }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => { setHovered(false); setModKeyHeld(false); }}
    >
      <TypeChip type={token.$type} resolvedValue={resolvedDisplay} />
      <TierBadge tier={tier} />

      {moving ? (
        /* ── Move-to UI: replaces name + value + menu ── */
        <div className="flex flex-col flex-1 min-w-0 gap-0.5">
          <div className="flex items-center gap-1">
            <input
              ref={moveRef}
              value={moveTarget}
              onChange={(e) => { setMoveTarget(e.target.value); setMoveError(""); }}
              onKeyDown={(e) => {
                if (e.key === "Enter") { e.preventDefault(); commitMove(); }
                if (e.key === "Escape") { setMoving(false); setMoveError(""); }
              }}
              onBlur={() => { if (!moveError) setMoving(false); }}
              placeholder="new.path.here"
              className="flex-1 min-w-0 bg-[var(--mauve-4)] border border-[var(--violet-7)] rounded px-1.5 h-5 text-[10px] font-mono text-[var(--mauve-12)] outline-none"
            />
            <button
              onMouseDown={(e) => { e.preventDefault(); commitMove(); }}
              className="h-5 px-2 rounded text-[9px] bg-[var(--violet-9)] text-white hover:bg-[var(--violet-10)] transition-colors flex-shrink-0"
            >
              Move
            </button>
            <button
              onMouseDown={(e) => { e.preventDefault(); setMoving(false); setMoveError(""); }}
              className="h-5 w-5 flex items-center justify-center rounded text-[9px] bg-[var(--mauve-4)] text-[var(--mauve-8)] hover:bg-[var(--mauve-5)] transition-colors flex-shrink-0"
            >
              ✕
            </button>
          </div>
          {moveError && (
            <span className="text-[9px] text-red-400 leading-tight">{moveError}</span>
          )}
          {!moveError && moveSuggestion && (
            <div className="flex items-center gap-1">
              <span className="text-[9px] text-[var(--violet-8)]">✨ Consider:</span>
              <button
                onMouseDown={(e) => {
                  e.preventDefault();
                  const segments = moveTarget.split(".");
                  segments[segments.length - 1] = moveSuggestion;
                  setMoveTarget(segments.join("."));
                  setMoveSuggestion(null);
                  moveRef.current?.focus();
                }}
                className="text-[9px] text-[var(--violet-9)] font-mono hover:underline"
              >
                {moveTarget.split(".").slice(0, -1).join(".")}.{moveSuggestion}
              </button>
            </div>
          )}
        </div>
      ) : (
        <>
          {/* Token name — always visible */}
          <span className="text-xs text-[var(--mauve-11)] flex-shrink-0 w-0 flex-1 truncate min-w-0" title={path}>
            {name}
          </span>

          {editing ? (
            /* Constrained to same ~48% column as the value button, so the name is never displaced */
            <div className="flex-shrink-0 w-[48%] min-w-0 flex">
              <TokenValueEditor path={path} token={token} onDone={() => setEditing(false)} />
            </div>
          ) : (
            <button
              onClick={() => setEditing(true)}
              className="flex items-center gap-1 min-w-0 max-w-[48%] text-right hover:bg-[var(--mauve-4)] rounded px-1 -mr-1 transition-colors"
              title={isRef
                ? `${String(token.$value)} → ${resolvedDisplay} · Hold ⌘/Ctrl to reveal value`
                : rawDisplay}
            >
              {isRef ? (
                modKeyHeld ? (
                  <span className="text-[10px] text-[var(--mauve-8)] font-mono truncate">{resolvedDisplay}</span>
                ) : (
                  <span className="text-[10px] text-[var(--violet-9)] font-mono truncate">{String(token.$value)}</span>
                )
              ) : (
                <span className="text-[10px] text-[var(--mauve-8)] font-mono whitespace-nowrap truncate">{rawDisplay}</span>
              )}
            </button>
          )}

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="opacity-0 group-hover:opacity-100 transition-opacity w-5 h-5 flex items-center justify-center rounded hover:bg-[var(--mauve-5)] flex-shrink-0">
                <MoreHorizontal className="w-3 h-3 text-[var(--mauve-8)]" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-40">
              <DropdownMenuItem onClick={() => setEditing(true)}>
                <Pencil className="w-3 h-3 mr-2" /> Edit value
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setMoving(true)}>
                <FolderPlus className="w-3 h-3 mr-2" /> Move to…
              </DropdownMenuItem>
              <DropdownMenuItem onClick={handleDuplicate}>
                <Copy className="w-3 h-3 mr-2" /> Duplicate
              </DropdownMenuItem>
              <DropdownMenuItem onClick={copyPath}>
                <Copy className="w-3 h-3 mr-2" /> Copy path
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleDelete} className="text-red-400 focus:text-red-400">
                <Trash2 className="w-3 h-3 mr-2" /> Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </>
      )}
    </div>
  );
}

// ─── Token group row (folder) ─────────────────────────────────────────────────

function TokenGroupRow({
  path,
  depth,
  count,
  children: childNodes,
  onCreateToken,
  onCreateGroup,
}: {
  path: string;
  depth: number;
  count: number;
  children: React.ReactNode;
  onCreateToken: (groupPath: string) => void;
  onCreateGroup: (groupPath: string) => void;
}) {
  const renameGroup = useTokensStore((s) => s.renameGroup);
  const removeGroup = useTokensStore((s) => s.removeGroup);
  const groupTier = useTokensStore((s) => s.getTier(path));
  const [open, setOpen] = useState(depth < 2); // auto-expand top 2 levels
  const [renaming, setRenaming] = useState(false);
  const [renameVal, setRenameVal] = useState("");
  const renameRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (renaming) { renameRef.current?.focus(); renameRef.current?.select(); }
  }, [renaming]);

  const pathParts = path.split(".");
  const name = pathParts[pathParts.length - 1] ?? path;
  const parentPath = pathParts.slice(0, -1).join(".");

  function startRename() {
    setRenameVal(name);
    setRenaming(true);
  }

  function commitRename() {
    const newName = renameVal.trim();
    if (newName && newName !== name && !newName.includes(".") && !newName.startsWith("$")) {
      const newPath = parentPath ? `${parentPath}.${newName}` : newName;
      renameGroup(path, newPath);
    }
    setRenaming(false);
  }

  function handleDeleteGroup() {
    if (!window.confirm(`Delete the "${name}" group and all its tokens?`)) return;
    removeGroup(path);
  }

  return (
    <div>
      <div
        className="group flex items-center gap-1 h-7 hover:bg-[var(--mauve-3)] transition-colors"
        style={{ paddingLeft: `${depth * 12 + 4}px` }}
      >
        <button
          onClick={() => setOpen((v) => !v)}
          className="flex items-center justify-center w-4 h-4 flex-shrink-0"
        >
          {open
            ? <ChevronDown className="w-2.5 h-2.5 text-[var(--mauve-7)]" />
            : <ChevronRight className="w-2.5 h-2.5 text-[var(--mauve-7)]" />}
        </button>

        {renaming ? (
          <input
            ref={renameRef}
            value={renameVal}
            onChange={(e) => setRenameVal(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") commitRename(); if (e.key === "Escape") setRenaming(false); }}
            onBlur={commitRename}
            className="flex-1 bg-[var(--mauve-4)] border border-[var(--violet-7)] rounded px-1.5 h-5 text-xs font-medium text-[var(--mauve-12)] outline-none"
          />
        ) : (
          <button
            onClick={() => setOpen((v) => !v)}
            onDoubleClick={startRename}
            className="flex-1 text-left text-xs font-medium text-[var(--mauve-10)] hover:text-[var(--mauve-12)] truncate"
            title={`${path} (double-click to rename)`}
          >
            {name}
          </button>
        )}

        <TierBadge tier={groupTier} />
        <span className="text-[9px] text-[var(--mauve-7)] font-mono flex-shrink-0 mr-1 tabular-nums">{count}</span>

        <button
          onClick={() => onCreateToken(path)}
          className="opacity-0 group-hover:opacity-100 transition-opacity w-4 h-4 flex items-center justify-center rounded hover:bg-[var(--mauve-5)] flex-shrink-0"
          title="Add token"
        >
          <Plus className="w-2.5 h-2.5 text-[var(--mauve-8)]" />
        </button>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="opacity-0 group-hover:opacity-100 transition-opacity w-4 h-4 flex items-center justify-center rounded hover:bg-[var(--mauve-5)] flex-shrink-0 mr-1">
              <MoreHorizontal className="w-2.5 h-2.5 text-[var(--mauve-8)]" />
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-44">
            <DropdownMenuItem onClick={startRename}>
              <Pencil className="w-3 h-3 mr-2" /> Rename folder
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onCreateToken(path)}>
              <Plus className="w-3 h-3 mr-2" /> New token here
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => onCreateGroup(path)}>
              <FolderPlus className="w-3 h-3 mr-2" /> New subfolder
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleDeleteGroup} className="text-red-400 focus:text-red-400">
              <Trash2 className="w-3 h-3 mr-2" /> Delete group
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      {open && childNodes}
    </div>
  );
}

// ─── Tree renderer ────────────────────────────────────────────────────────────

function TokenTree({
  entries,
  onCreateToken,
  onCreateGroup,
  creatingInGroup,
  onCreateDone,
}: {
  entries: Record<string, DesignToken>;
  onCreateToken: (groupPath: string) => void;
  onCreateGroup: (groupPath: string) => void;
  creatingInGroup: string | null;
  onCreateDone: () => void;
}) {
  const tree = useMemo(() => buildTree(entries), [entries]);

  function renderLevel(group: Record<string, unknown>, prefix: string, depth: number): React.ReactNode {
    const keys = Object.keys(group)
      .filter((k) => !k.startsWith("$"))
      .sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));

    return keys.map((key) => {
      const node = group[key];
      if (!node || typeof node !== "object") return null;
      const path = prefix ? `${prefix}.${key}` : key;

      if ("$value" in (node as object)) {
        return (
          <TokenLeafRow
            key={path}
            path={path}
            token={node as DesignToken}
            depth={depth}
          />
        );
      }

      // It's a group
      const groupCount = countUnderPrefix(entries, path);
      return (
        <TokenGroupRow
          key={path}
          path={path}
          depth={depth}
          count={groupCount}
          onCreateToken={onCreateToken}
          onCreateGroup={onCreateGroup}
        >
          {creatingInGroup === path && (
            <NewTokenRow groupPath={path} onDone={onCreateDone} />
          )}
          {renderLevel(node as Record<string, unknown>, path, depth + 1)}
        </TokenGroupRow>
      );
    });
  }

  return (
    <div>
      {creatingInGroup === "" && (
        <NewTokenRow groupPath="" onDone={onCreateDone} />
      )}
      {renderLevel(tree as Record<string, unknown>, "", 0)}
    </div>
  );
}

// ─── Search results ───────────────────────────────────────────────────────────

function SearchResults({ query, entries }: { query: string; entries: Record<string, DesignToken> }) {
  const getDisplayValue = useTokensStore((s) => s.getDisplayValue);
  const filtered = useMemo(
    () => Object.keys(entries).filter((p) => p.toLowerCase().includes(query.toLowerCase())).slice(0, 60),
    [entries, query],
  );

  if (filtered.length === 0) {
    return (
      <div className="flex flex-col items-center py-8 gap-2 text-center px-4">
        <Search className="w-5 h-5 text-[var(--mauve-7)]" />
        <p className="text-xs text-[var(--mauve-9)]">No tokens match "{query}"</p>
      </div>
    );
  }

  return (
    <div>
      {filtered.map((path) => {
        const token = entries[path]!;
        const resolved = getDisplayValue(path);
        const isRef = isReference(token.$value);
        const rawValue = typeof token.$value === "object" ? "…" : String(token.$value);
        return (
          <div
            key={path}
            className="flex items-center gap-1.5 h-8 px-2 border-b border-[var(--mauve-4)] last:border-0 hover:bg-[var(--mauve-3)] transition-colors"
          >
            <TypeChip type={token.$type} resolvedValue={resolved} />
            <span className="text-xs text-[var(--mauve-10)] flex-1 truncate min-w-0 font-mono">{path}</span>
            {isRef ? (
              <>
                <span className="text-[10px] text-[var(--mauve-7)] font-mono truncate max-w-20">{rawValue}</span>
                <span className="text-[10px] text-[var(--mauve-5)] flex-shrink-0">→</span>
              </>
            ) : null}
            <span className="text-[10px] text-[var(--mauve-8)] font-mono flex-shrink-0 whitespace-nowrap">{resolved}</span>
          </div>
        );
      })}
      {filtered.length === 60 && (
        <p className="text-[9px] text-[var(--mauve-7)] text-center py-2">Showing first 60 results</p>
      )}
    </div>
  );
}

// ─── Preset picker (preserved) ────────────────────────────────────────────────

function PresetPicker() {
  const { setColorSystem } = useColorSystemStore();

  return (
    <div className="flex flex-col h-full bg-[var(--color-surface-1)]">
      <div className="flex-shrink-0 px-3 py-3 border-b border-[var(--color-border-subtle)]">
        <p className="text-xs font-medium text-[var(--mauve-11)]">Choose a design system</p>
        <p className="text-[10px] text-[var(--mauve-8)] mt-0.5 leading-relaxed">
          Pick a preset to generate a color system instantly.
        </p>
      </div>
      <div className="flex-1 overflow-y-auto overflow-x-hidden min-h-0">
        <div className="p-2 space-y-1.5">
          {DESIGN_SYSTEM_PRESETS.map((preset) => (
            <div
              key={preset.id}
              className="rounded-lg border border-[var(--mauve-5)] bg-[var(--mauve-2)] hover:border-[var(--mauve-7)] transition-colors p-2.5"
            >
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="text-xs font-medium text-[var(--mauve-12)] truncate">
                    {preset.name}
                  </span>
                  <div className="flex gap-0.5 flex-shrink-0">
                    {preset.previewColors.map((hex) => (
                      <div
                        key={hex}
                        className="w-3 h-3 rounded-sm border border-[var(--mauve-5)]"
                        style={{ background: hex }}
                        title={hex}
                      />
                    ))}
                  </div>
                </div>
                <button
                  onClick={() => setColorSystem(makeColorSystem(preset))}
                  className="flex-shrink-0 h-5 px-2 rounded text-[10px] bg-[var(--violet-9)] text-white hover:bg-[var(--violet-10)] transition-colors"
                >
                  Apply
                </button>
              </div>
              <p className="text-[10px] text-[var(--mauve-8)] mt-1 leading-relaxed">
                {preset.tagline}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── TokensPanel ──────────────────────────────────────────────────────────────

export function TokensPanel() {
  const { colorSystem } = useColorSystemStore();
  const repo = useOnboardingStore((s) => s.repo);
  const entries = useTokensStore((s) => s.entries);
  const activeMode = useTokensStore((s) => s.activeMode);
  const setActiveMode = useTokensStore((s) => s.setActiveMode);
  const bulkSet = useTokensStore((s) => s.bulkSet);

  const hasGenerated = colorSystem !== null;
  const hasRepo = repo.isConnected && !repo.isSkipped;

  const [query, setQuery] = useState("");
  const [creatingInGroup, setCreatingInGroup] = useState<string | null>(null);

  // Seed static tokens on first mount (only paths not already present)
  useEffect(() => {
    const staticEntries = staticTokensToEntries();
    const missing: Record<string, DesignToken> = {};
    for (const [k, v] of Object.entries(staticEntries)) {
      if (!(k in entries)) missing[k] = v;
    }
    if (Object.keys(missing).length > 0) bulkSet(missing, false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const totalCount = Object.keys(entries).length;

  const exportVia = useTokensStore((s) => s.exportVia);

  function handleExport() {
    const json = exportDTCGJson(entries);
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "tokens.json";
    a.click();
    URL.revokeObjectURL(url);
  }

  function handleExportVia(format: "css-vars" | "tailwind-theme" | "scss" | "json-dtcg") {
    const result = exportVia({ format, includeDescriptions: true });
    const ext = format === "css-vars" ? "css" : format === "tailwind-theme" ? "js" : format === "scss" ? "scss" : "json";
    const mime = format === "json-dtcg" ? "application/json" : "text/plain";
    const blob = new Blob([result.content], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `tokens.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  }

  const handleCreateToken = useCallback((groupPath: string) => {
    setCreatingInGroup(groupPath);
  }, []);

  const handleCreateGroup = useCallback((groupPath: string) => {
    // For subfolder creation, create a placeholder token so the group exists
    setCreatingInGroup(groupPath);
  }, []);

  // Show preset picker only if no tokens exist at all (no color system and empty store)
  if (!hasGenerated && !hasRepo && totalCount === 0) {
    return <PresetPicker />;
  }

  return (
    <div className="flex flex-col h-full bg-[var(--color-surface-1)]">
      {/* Header */}
      <div className="flex-shrink-0 px-2 pt-2 pb-1.5 border-b border-[var(--color-border-subtle)]">
        {/* Row 1: search */}
        <div className="flex items-center gap-1 h-6 bg-[var(--mauve-3)] rounded border border-[var(--mauve-5)] px-2 mb-1.5">
          <Search className="w-3 h-3 text-[var(--mauve-8)] flex-shrink-0" />
          <input
            type="text"
            placeholder="Search tokens…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="flex-1 bg-transparent text-xs text-[var(--mauve-12)] placeholder:text-[var(--mauve-8)] outline-none min-w-0"
          />
          {query && (
            <button onClick={() => setQuery("")} className="text-[var(--mauve-7)] hover:text-[var(--mauve-11)] flex-shrink-0 text-[10px]">✕</button>
          )}
        </div>
        {/* Row 2: controls */}
        <div className="flex items-center gap-1">
          {/* Mode toggle */}
          <div className="flex rounded overflow-hidden border border-[var(--mauve-5)] flex-shrink-0">
            {(["light", "dark"] as const).map((mode) => (
              <button
                key={mode}
                onClick={() => setActiveMode(mode)}
                className={cn(
                  "h-5 px-1.5 text-[9px] capitalize transition-colors",
                  activeMode === mode
                    ? "bg-[var(--mauve-5)] text-[var(--mauve-12)]"
                    : "bg-[var(--mauve-3)] text-[var(--mauve-8)] hover:text-[var(--mauve-11)]",
                )}
              >
                {mode[0]!.toUpperCase() + mode.slice(1)}
              </button>
            ))}
          </div>
          {/* Token count */}
          <span className="text-[9px] text-[var(--mauve-7)] flex-1 min-w-0 truncate">
            {totalCount} token{totalCount !== 1 ? "s" : ""} · W3C DTCG
          </span>
          {/* Export */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button
                title="Export tokens"
                className="w-5 h-5 flex items-center justify-center rounded hover:bg-[var(--mauve-4)] text-[var(--mauve-8)] hover:text-[var(--mauve-11)] transition-colors flex-shrink-0"
              >
                <Download className="w-3 h-3" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-44">
              <DropdownMenuItem onClick={handleExport}>
                <Download className="w-3 h-3 mr-2" /> W3C DTCG (.json)
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => handleExportVia("css-vars")}>
                CSS Variables (.css)
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleExportVia("tailwind-theme")}>
                Tailwind Theme (.js)
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleExportVia("scss")}>
                SCSS Variables (.scss)
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          {/* Add token at root */}
          <button
            onClick={() => handleCreateToken("")}
            title="New token"
            className="w-5 h-5 flex items-center justify-center rounded hover:bg-[var(--mauve-4)] text-[var(--mauve-8)] hover:text-[var(--mauve-11)] transition-colors flex-shrink-0"
          >
            <Plus className="w-3 h-3" />
          </button>
        </div>
      </div>

      {/* Tree / Search */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden min-h-0">
        {query ? (
          <SearchResults query={query} entries={entries} />
        ) : (
          <TokenTree
            entries={entries}
            onCreateToken={handleCreateToken}
            onCreateGroup={handleCreateGroup}
            creatingInGroup={creatingInGroup}
            onCreateDone={() => setCreatingInGroup(null)}
          />
        )}
      </div>
    </div>
  );
}
