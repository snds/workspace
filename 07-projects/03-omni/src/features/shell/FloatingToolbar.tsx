import { OmniIcon } from "@/core/icons";
import { useUIStore, type ToolMode } from "@/stores/ui.store";
import { useCanvasStore } from "@/stores/canvas.store";
import { cn } from "@/lib/utils";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

const TOOLS: {
  id: ToolMode;
  iconName: string;
  label: string;
  shortcut: string;
}[] = [
  { id: "select",  iconName: "tool/select", label: "Select",    shortcut: "V" },
  { id: "hand",    iconName: "tool/hand",   label: "Hand",       shortcut: "H" },
  { id: "frame",   iconName: "tool/frame",  label: "Frame",      shortcut: "F" },
  { id: "shape",   iconName: "tool/shape",  label: "Rectangle",  shortcut: "R" },
  { id: "text",    iconName: "tool/text",   label: "Text",       shortcut: "T" },
  { id: "pen",     iconName: "tool/pen",    label: "Pen",        shortcut: "P" },
];

function TBtn({
  onClick,
  title,
  active,
  disabled,
  children,
}: {
  onClick?: () => void;
  title?: string;
  active?: boolean;
  disabled?: boolean;
  children: React.ReactNode;
}) {
  return (
    <TooltipProvider delayDuration={400}>
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            onClick={onClick}
            disabled={disabled}
            className={cn(
              "flex items-center justify-center w-7 h-7 rounded transition-colors",
              active
                ? "bg-[var(--violet-3)] text-[var(--violet-11)]"
                : "text-[var(--mauve-9)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)]",
              disabled && "opacity-30 pointer-events-none",
            )}
          >
            {children}
          </button>
        </TooltipTrigger>
        {title && (
          <TooltipContent side="top" className="text-xs">{title}</TooltipContent>
        )}
      </Tooltip>
    </TooltipProvider>
  );
}

function Sep() {
  return <div className="w-px h-5 bg-[var(--color-border-subtle)] mx-0.5 flex-shrink-0" />;
}

export function FloatingToolbar() {
  const {
    activeTool,
    setActiveTool,
    inspectMode,
    toggleInspectMode,
    panelsHidden,
    toggleAllPanels,
  } = useUIStore();
  const { historyPast, historyFuture, undo, redo } = useCanvasStore();

  return (
    <div className="absolute bottom-5 left-1/2 -translate-x-1/2 z-20 pointer-events-none select-none">
      <div className="pointer-events-auto flex items-center gap-0.5 h-10 px-2 rounded-xl bg-[var(--color-surface-1)] border border-[var(--color-border-subtle)] shadow-xl">
        {/* Undo / Redo */}
        <TBtn onClick={undo} disabled={historyPast.length === 0} title="Undo ⌘Z">
          <OmniIcon name="action/undo" size={14} />
        </TBtn>
        <TBtn onClick={redo} disabled={historyFuture.length === 0} title="Redo ⌘⇧Z">
          <OmniIcon name="action/redo" size={14} />
        </TBtn>

        <Sep />

        {/* Tool strip */}
        {TOOLS.map((tool) => (
          <TBtn
            key={tool.id}
            onClick={() => setActiveTool(tool.id)}
            active={activeTool === tool.id}
            title={`${tool.label}  ${tool.shortcut}`}
          >
            <OmniIcon name={tool.iconName} size={14} />
          </TBtn>
        ))}

        <Sep />

        {/* Inspect mode */}
        <TBtn onClick={toggleInspectMode} active={inspectMode} title="Inspect mode">
          <OmniIcon name="tool/inspect" size={14} />
        </TBtn>

        <Sep />

        {/* Hide / show all panels */}
        <TBtn onClick={toggleAllPanels} active={panelsHidden} title={panelsHidden ? "Show panels  ⌃\\" : "Hide panels  ⌃\\"}>
          <OmniIcon name={panelsHidden ? "panel/left-open" : "panel/left-close"} size={14} />
        </TBtn>
      </div>
    </div>
  );
}
