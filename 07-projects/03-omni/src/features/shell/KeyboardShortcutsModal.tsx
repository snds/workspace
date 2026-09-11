import { useState, useMemo } from "react";
import { X, Search } from "lucide-react";
import { useUIStore } from "@/stores/ui.store";
import { SHORTCUT_GROUPS } from "@/lib/keyboardShortcuts";
import type { Shortcut } from "@/lib/keyboardShortcuts";

// ─── Key badge ───────────────────────────────────────────────────────────────

function KeyBadge({ label }: { label: string }) {
  return (
    <kbd className="inline-flex items-center justify-center min-w-[20px] h-5 px-1 rounded text-[10px] font-mono font-medium bg-[var(--mauve-4)] border border-[var(--mauve-6)] text-[var(--mauve-11)] leading-none select-none">
      {label}
    </kbd>
  );
}

/** Render one alternative chord as a sequence of key badges. */
function Chord({ keys }: { keys: string[] }) {
  return (
    <span className="inline-flex items-center gap-0.5">
      {keys.map((k, i) => <KeyBadge key={i} label={k} />)}
    </span>
  );
}

/** Render all alternatives for a shortcut (joined by "or"). */
function ShortcutKeys({ shortcut }: { shortcut: Shortcut }) {
  return (
    <span className="inline-flex items-center gap-1 flex-wrap justify-end">
      {shortcut.keys.map((chord, i) => (
        <span key={i} className="inline-flex items-center gap-1">
          {i > 0 && <span className="text-[10px] text-[var(--mauve-7)]">or</span>}
          <Chord keys={chord} />
        </span>
      ))}
    </span>
  );
}

// ─── Shortcut row ────────────────────────────────────────────────────────────

function ShortcutRow({ shortcut }: { shortcut: Shortcut }) {
  return (
    <div
      className={`flex items-center justify-between gap-3 py-1 px-1 rounded ${
        shortcut.reserved ? "opacity-35" : ""
      }`}
    >
      <span className="text-[11px] text-[var(--mauve-11)] min-w-0 truncate leading-none">
        {shortcut.label}
        {shortcut.note && (
          <span className="text-[10px] text-[var(--mauve-7)] ml-1">{shortcut.note}</span>
        )}
      </span>
      <ShortcutKeys shortcut={shortcut} />
    </div>
  );
}

// ─── Main modal ──────────────────────────────────────────────────────────────

export function KeyboardShortcutsModal() {
  const { showKeyboardShortcuts, setShowKeyboardShortcuts } = useUIStore();
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return SHORTCUT_GROUPS;
    return SHORTCUT_GROUPS
      .map((group) => ({
        ...group,
        shortcuts: group.shortcuts.filter((s) =>
          s.label.toLowerCase().includes(q) ||
          group.title.toLowerCase().includes(q)
        ),
      }))
      .filter((group) => group.shortcuts.length > 0);
  }, [query]);

  if (!showKeyboardShortcuts) return null;

  return (
    // Backdrop
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={() => setShowKeyboardShortcuts(false)}
    >
      {/* Panel */}
      <div
        className="relative bg-[var(--color-surface-1)] border border-[var(--color-border-subtle)] rounded-xl shadow-2xl flex flex-col overflow-hidden"
        style={{ width: 780, maxHeight: "82vh" }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 pt-4 pb-3 border-b border-[var(--color-border-subtle)] flex-shrink-0">
          <h2 className="text-sm font-semibold text-[var(--mauve-12)]">Keyboard shortcuts</h2>
          <button
            onClick={() => setShowKeyboardShortcuts(false)}
            className="flex items-center justify-center w-6 h-6 rounded text-[var(--mauve-9)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)] transition-colors"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Search */}
        <div className="px-5 py-2.5 border-b border-[var(--color-border-subtle)] flex-shrink-0">
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3 h-3 text-[var(--mauve-8)]" />
            <input
              autoFocus
              type="text"
              placeholder="Search shortcuts…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Escape") setShowKeyboardShortcuts(false); }}
              className="w-full h-7 pl-7 pr-3 rounded bg-[var(--mauve-3)] border border-[var(--mauve-5)] text-[11px] text-[var(--mauve-12)] placeholder:text-[var(--mauve-7)] outline-none focus:border-[var(--violet-7)]"
            />
          </div>
        </div>

        {/* Content grid */}
        <div className="overflow-y-auto flex-1 px-5 py-4">
          {filtered.length === 0 ? (
            <p className="text-[11px] text-[var(--mauve-8)] text-center py-8">No shortcuts match "{query}"</p>
          ) : (
            <div className="grid gap-x-6 gap-y-4" style={{ gridTemplateColumns: "repeat(3, 1fr)" }}>
              {filtered.map((group) => (
                <div key={group.title} className="flex flex-col gap-0.5">
                  <p className="text-[10px] font-semibold uppercase tracking-wide text-[var(--mauve-8)] mb-1 px-1">
                    {group.title}
                  </p>
                  {group.shortcuts.map((s) => (
                    <ShortcutRow key={s.label} shortcut={s} />
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer hint */}
        <div className="px-5 py-2 border-t border-[var(--color-border-subtle)] flex-shrink-0 flex items-center justify-between">
          <span className="text-[10px] text-[var(--mauve-7)]">Dimmed shortcuts are reserved for upcoming features</span>
          <span className="text-[10px] text-[var(--mauve-7)]">Press <KeyBadge label="?" /> or <KeyBadge label="⎋" /> to close</span>
        </div>
      </div>
    </div>
  );
}
