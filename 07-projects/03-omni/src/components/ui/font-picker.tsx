import { useState, useRef, useEffect, useCallback } from "react";
import { ChevronDown, Search } from "lucide-react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { GOOGLE_FONTS, type FontCategory, preloadFontPreview } from "@/lib/google-fonts";
import { useFontStore } from "@/stores/font.store";
import { cn } from "@/lib/utils";

// ─── Font-ready detection (eliminates FOUC) ──────────────────────────────────

function isFontAvailable(family: string): boolean {
  try { return document.fonts.check(`16px "${family}"`); } catch { return false; }
}

/**
 * Returns true once `family` is actually available for rendering.
 * Listens to the `loadingdone` event on `document.fonts` so we flip
 * the flag the moment the browser finishes downloading the typeface,
 * rather than relying on an arbitrary timeout.
 */
function useFontReady(family: string): boolean {
  const [ready, setReady] = useState(() => isFontAvailable(family));

  useEffect(() => {
    if (isFontAvailable(family)) { setReady(true); return; }
    setReady(false);

    let cancelled = false;
    function onDone() {
      if (!cancelled && isFontAvailable(family)) {
        setReady(true);
        document.fonts.removeEventListener("loadingdone", onDone);
      }
    }
    document.fonts.addEventListener("loadingdone", onDone);
    return () => { cancelled = true; document.fonts.removeEventListener("loadingdone", onDone); };
  }, [family]);

  return ready;
}

// ─── Category labels ──────────────────────────────────────────────────────────

const CATEGORY_LABELS: Record<FontCategory, string> = {
  "sans-serif": "Sans-serif",
  serif: "Serif",
  display: "Display",
  monospace: "Monospace",
  handwriting: "Handwriting",
};

// ─── Font list item with IntersectionObserver preview loading ─────────────────

function FontItem({
  family,
  isSelected,
  onClick,
}: {
  family: string;
  isSelected: boolean;
  onClick: () => void;
}) {
  const ref = useRef<HTMLButtonElement>(null);
  const [triggered, setTriggered] = useState(false);
  const fontReady = useFontReady(family);

  // Kick off preview load when the item scrolls into view
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          preloadFontPreview(family);
          setTriggered(true);
          observer.disconnect();
        }
      },
      { rootMargin: "80px" },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [family]);

  return (
    <button
      ref={ref}
      onClick={onClick}
      className={cn(
        "w-full flex items-center h-7 px-3 text-sm text-left transition-colors",
        isSelected
          ? "bg-[var(--violet-3)] text-[var(--violet-11)]"
          : "text-[var(--mauve-12)] hover:bg-[var(--mauve-4)]",
      )}
      style={triggered && fontReady ? { fontFamily: `"${family}", sans-serif` } : undefined}
    >
      {family}
    </button>
  );
}

// ─── FontPicker ───────────────────────────────────────────────────────────────

export interface FontPickerProps {
  value: string;
  onChange: (family: string) => void;
}

export function FontPicker({ value, onChange }: FontPickerProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");
  const searchRef = useRef<HTMLInputElement>(null);
  const { localFonts, isServerRunning, ensureFont } = useFontStore();
  const triggerFontReady = useFontReady(value);

  // Ensure the currently-selected font is loaded (for the trigger preview)
  useEffect(() => { ensureFont(value); }, [value, ensureFont]);

  // Focus search on open
  useEffect(() => {
    if (open) {
      setTimeout(() => searchRef.current?.focus(), 0);
    } else {
      setSearch("");
    }
  }, [open]);

  const handleSelect = useCallback(
    (family: string) => {
      ensureFont(family);
      onChange(family);
      setOpen(false);
    },
    [ensureFont, onChange],
  );

  // Filter
  const q = search.toLowerCase();

  const filteredLocal = isServerRunning
    ? localFonts.filter((f) => f.family.toLowerCase().includes(q))
    : [];

  // Group Google Fonts by category
  const filteredGoogle = GOOGLE_FONTS.filter((f) =>
    f.family.toLowerCase().includes(q),
  );
  const byCategory = new Map<FontCategory, string[]>();
  for (const f of filteredGoogle) {
    if (!byCategory.has(f.category)) byCategory.set(f.category, []);
    byCategory.get(f.category)!.push(f.family);
  }
  const categoryOrder: FontCategory[] = [
    "sans-serif",
    "serif",
    "display",
    "monospace",
    "handwriting",
  ];

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <button
          className="w-full h-6 flex items-center px-1.5 bg-[var(--mauve-3)] border border-[var(--mauve-5)] rounded text-xs text-[var(--mauve-12)] overflow-hidden hover:border-[var(--mauve-7)] transition-colors focus:outline-none"
          style={triggerFontReady ? { fontFamily: `"${value}", sans-serif` } : undefined}
        >
          <span className="flex-1 text-left truncate">{value}</span>
          <ChevronDown className="flex-shrink-0 w-3 h-3 text-[var(--mauve-8)] ml-1" />
        </button>
      </PopoverTrigger>

      <PopoverContent
        align="start"
        sideOffset={4}
        className="w-[260px] p-0 border-[var(--mauve-5)] bg-[var(--mauve-2)] shadow-xl overflow-hidden"
        onOpenAutoFocus={(e) => e.preventDefault()}
      >
        {/* Search */}
        <div className="flex items-center gap-1.5 px-2 py-1.5 border-b border-[var(--mauve-4)]">
          <Search className="w-3 h-3 text-[var(--mauve-8)] flex-shrink-0" />
          <input
            ref={searchRef}
            type="text"
            placeholder="Search fonts…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 bg-transparent text-xs text-[var(--mauve-12)] outline-none placeholder:text-[var(--mauve-8)]"
          />
        </div>

        {/* Font list */}
        <div className="overflow-y-auto max-h-[320px]">
          {/* Local fonts (if server running) */}
          {filteredLocal.length > 0 && (
            <>
              <div className="px-3 py-1 text-[9px] uppercase tracking-wide text-[var(--mauve-8)] font-semibold bg-[var(--mauve-3)] border-b border-[var(--mauve-4)]">
                Local Fonts
              </div>
              {filteredLocal.map((f) => (
                <FontItem
                  key={f.family}
                  family={f.family}
                  isSelected={value === f.family}
                  onClick={() => handleSelect(f.family)}
                />
              ))}
            </>
          )}

          {/* Google Fonts by category */}
          {categoryOrder.map((cat) => {
            const families = byCategory.get(cat);
            if (!families || families.length === 0) return null;
            return (
              <div key={cat}>
                <div className="px-3 py-1 text-[9px] uppercase tracking-wide text-[var(--mauve-8)] font-semibold bg-[var(--mauve-3)] border-b border-[var(--mauve-4)]">
                  {CATEGORY_LABELS[cat]}
                </div>
                {families.map((family) => (
                  <FontItem
                    key={family}
                    family={family}
                    isSelected={value === family}
                    onClick={() => handleSelect(family)}
                  />
                ))}
              </div>
            );
          })}

          {filteredLocal.length === 0 &&
            filteredGoogle.length === 0 && (
              <div className="px-3 py-6 text-[10px] text-[var(--mauve-9)] text-center italic">
                No fonts match &ldquo;{search}&rdquo;
              </div>
            )}
        </div>
      </PopoverContent>
    </Popover>
  );
}
