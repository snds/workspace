import { OmniIcon } from "@/core/icons";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { useUIStore, type ActiveLeftPanel } from "@/stores/ui.store";
import { LayersView } from "@/features/layers/LayersView";
import { AssetsPanel } from "@/features/assets/AssetsPanel";
import { TokensPanel } from "@/features/tokens/TokensPanel";
import { CodePanel } from "@/features/code/CodePanel";
import { cn } from "@/lib/utils";

// ─── Nav rail items ───────────────────────────────────────────────────────────

const NAV_ITEMS: {
  id: ActiveLeftPanel;
  iconName: string;
  label: string;
}[] = [
  { id: "design", iconName: "misc/layers",    label: "Design" },
  { id: "assets", iconName: "misc/component", label: "Assets" },
  { id: "tokens", iconName: "misc/coins",     label: "Tokens" },
  { id: "code",   iconName: "content/code",   label: "Code" },
];

function LeftNavRail() {
  const { activeLeftPanel, setActiveLeftPanel } = useUIStore();

  return (
    <div className="flex flex-col items-center gap-1 pt-2 w-10 flex-shrink-0 bg-[var(--color-surface-0)] border-r border-[var(--color-border-subtle)]">
      {NAV_ITEMS.map(({ id, iconName, label }) => (
        <TooltipProvider key={id} delayDuration={400}>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={() => setActiveLeftPanel(id)}
                className={cn(
                  "flex items-center justify-center w-8 h-8 rounded transition-colors",
                  activeLeftPanel === id
                    ? "bg-[var(--violet-3)] text-[var(--violet-11)]"
                    : "text-[var(--mauve-9)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)]"
                )}
              >
                <OmniIcon name={iconName} size={16} />
              </button>
            </TooltipTrigger>
            <TooltipContent side="right" className="text-xs">
              {label}
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      ))}
    </div>
  );
}

// ─── File header ──────────────────────────────────────────────────────────────

function FileHeader({ autoSaveLabel }: { autoSaveLabel: "saved" | "saving" }) {
  return (
    <div className="flex items-center gap-2.5 h-11 px-3 border-b border-[var(--color-border-subtle)] flex-shrink-0">
      {/* Logo mark — violet square with "O", no text label */}
      <div className="w-5 h-5 rounded bg-[var(--violet-9)] flex items-center justify-center flex-shrink-0">
        <span className="text-[10px] font-bold text-white leading-none">O</span>
      </div>

      <div className="flex-1 min-w-0">
        <div className="text-[11px] font-semibold text-[var(--mauve-12)] truncate leading-tight">
          Untitled
        </div>
        <div className="text-[9px] text-[var(--mauve-8)] truncate leading-tight">
          My Files
        </div>
      </div>

      {/* Auto-save indicator */}
      <div className="flex items-center gap-1 flex-shrink-0">
        <span
          className={cn(
            "w-1.5 h-1.5 rounded-full flex-shrink-0 transition-colors",
            autoSaveLabel === "saving" ? "bg-[var(--yellow-9)] animate-pulse" : "bg-[var(--green-9)]",
          )}
        />
        <span className="text-[9px] text-[var(--mauve-7)]">
          {autoSaveLabel === "saving" ? "Saving…" : "Saved"}
        </span>
      </div>
    </div>
  );
}

// ─── LeftPanel ────────────────────────────────────────────────────────────────

export function LeftPanel({ autoSaveLabel }: { autoSaveLabel?: "saved" | "saving" }) {
  const { activeLeftPanel } = useUIStore();

  return (
    <div className="flex flex-col w-full h-full bg-[var(--color-surface-1)] border-r border-[var(--color-border-subtle)]">
      <FileHeader autoSaveLabel={autoSaveLabel ?? "saved"} />
      <div className="flex flex-row flex-1 overflow-hidden">
        <LeftNavRail />
        <div className="flex-1 overflow-hidden">
          {activeLeftPanel === "design" && <LayersView />}
          {activeLeftPanel === "assets" && <AssetsPanel />}
          {activeLeftPanel === "tokens" && <TokensPanel />}
          {activeLeftPanel === "code" && <CodePanel />}
        </div>
      </div>
    </div>
  );
}
