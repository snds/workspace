import { OmniIcon } from "@/core/icons";
import omniLogo from "@/assets/omni-logo.svg";
import { useUIStore, type ToolMode } from "@/stores/ui.store";
import { useCanvasStore } from "@/stores/canvas.store";
import { useInfraStore } from "@/stores/infra.store";
import { useTeamContextStore } from "@/stores/teamContext.store";
import { cn } from "@/lib/utils";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Separator } from "@/components/ui/separator";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const TOOLS: { id: ToolMode; iconName: string; label: string; shortcut: string }[] = [
  { id: "select",  iconName: "tool/select", label: "Select",     shortcut: "V" },
  { id: "hand",    iconName: "tool/hand",   label: "Hand",        shortcut: "H" },
  { id: "frame",   iconName: "tool/frame",  label: "Frame",       shortcut: "F" },
  { id: "shape",   iconName: "tool/shape",  label: "Rectangle",   shortcut: "R" },
  { id: "text",    iconName: "tool/text",   label: "Text",        shortcut: "T" },
  { id: "pen",     iconName: "tool/pen",    label: "Pen",         shortcut: "P" },
];

function ToolButton({
  tool,
  active,
  onClick,
}: {
  tool: (typeof TOOLS)[number];
  active: boolean;
  onClick: () => void;
}) {
  return (
    <TooltipProvider delayDuration={400}>
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            onClick={onClick}
            className={cn(
              "flex items-center justify-center w-7 h-7 rounded transition-colors",
              active
                ? "bg-[var(--violet-3)] text-[var(--violet-11)]"
                : "text-[var(--mauve-11)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)]"
            )}
          >
            <OmniIcon name={tool.iconName} size={14} />
          </button>
        </TooltipTrigger>
        <TooltipContent side="bottom" className="text-xs">
          {tool.label} <span className="opacity-50 ml-1">{tool.shortcut}</span>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}

function EnvironmentIndicator() {
  const isTierActive = useTeamContextStore((s) => s.isTierActive);
  const { environments, activeEnvironmentId, setActiveEnvironment } = useInfraStore();

  if (!isTierActive(3)) return null;

  const activeEnv = environments.find((e) => e.id === activeEnvironmentId);
  if (!activeEnv) return null;

  return (
    <>
      <Separator orientation="vertical" className="h-5 bg-[var(--color-border-subtle)]" />
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button className="flex items-center gap-1.5 rounded px-1.5 py-0.5 hover:bg-[var(--mauve-4)] transition-colors text-xs text-[var(--mauve-11)] hover:text-[var(--mauve-12)]">
            <span
              className="w-2 h-2 rounded-full flex-shrink-0"
              style={{ backgroundColor: activeEnv.color }}
            />
            <span className="font-medium">{activeEnv.name}</span>
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent side="bottom" align="end" className="w-40">
          {environments.map((env) => (
            <DropdownMenuItem
              key={env.id}
              onSelect={() => setActiveEnvironment(env.id)}
              className={cn(
                "flex items-center gap-2 text-xs cursor-pointer",
                env.id === activeEnvironmentId && "bg-[var(--mauve-4)]",
              )}
            >
              <span
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ backgroundColor: env.color }}
              />
              {env.name}
              {env.id === activeEnvironmentId && (
                <span className="ml-auto text-[var(--mauve-8)] text-[10px]">active</span>
              )}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    </>
  );
}

export function TopBar() {
  const {
    activeTool,
    setActiveTool,
    zoom,
    zoomIn,
    zoomOut,
    resetZoom,
    leftPanelVisible,
    rightPanelVisible,
    toggleLeftPanel,
    toggleRightPanel,
    theme,
    toggleTheme,
    inspectMode,
    toggleInspectMode,
    toggleKeyboardShortcuts,
  } = useUIStore();
  const { historyPast, historyFuture, undo, redo } = useCanvasStore();

  return (
    <div
      className="flex items-center gap-2 px-3 border-b border-[var(--color-border-subtle)] bg-[var(--color-surface-1)] flex-shrink-0"
      style={{ height: "var(--topbar-height)" }}
    >
      {/* Left: Logo + panel toggle */}
      <div className="flex items-center gap-2 min-w-0">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="flex items-center gap-1.5 mr-2 rounded px-1 py-0.5 hover:bg-[var(--mauve-4)] transition-colors focus:outline-none">
              <img src={omniLogo} alt="Omni" className="w-5 h-5 flex-shrink-0" />
              <span className="text-sm font-semibold text-[var(--mauve-12)]">Omni</span>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent side="bottom" align="start" className="w-52">
            <DropdownMenuItem
              onSelect={toggleKeyboardShortcuts}
              className="flex items-center gap-2 text-xs cursor-pointer"
            >
              <OmniIcon name="tool/keyboard" size={14} color="var(--mauve-9)" />
              Keyboard shortcuts
              <span className="ml-auto text-[var(--mauve-7)] font-mono text-[10px]">?</span>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem disabled className="text-xs text-[var(--mauve-8)] cursor-default">
              Preferences
            </DropdownMenuItem>
            <DropdownMenuItem disabled className="text-xs text-[var(--mauve-8)] cursor-default">
              About Omni
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>

        <TooltipProvider delayDuration={400}>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={undo}
                disabled={historyPast.length === 0}
                className="flex items-center justify-center w-7 h-7 rounded text-[var(--mauve-9)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)] transition-colors disabled:opacity-30 disabled:pointer-events-none"
              >
                <OmniIcon name="action/undo" size={14} />
              </button>
            </TooltipTrigger>
            <TooltipContent side="bottom" className="text-xs">
              Undo <span className="opacity-50 ml-1">⌘Z</span>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>

        <TooltipProvider delayDuration={400}>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={redo}
                disabled={historyFuture.length === 0}
                className="flex items-center justify-center w-7 h-7 rounded text-[var(--mauve-9)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)] transition-colors disabled:opacity-30 disabled:pointer-events-none"
              >
                <OmniIcon name="action/redo" size={14} />
              </button>
            </TooltipTrigger>
            <TooltipContent side="bottom" className="text-xs">
              Redo <span className="opacity-50 ml-1">⌘⇧Z</span>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>

        <TooltipProvider delayDuration={400}>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={toggleLeftPanel}
                className="flex items-center justify-center w-7 h-7 rounded text-[var(--mauve-9)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)] transition-colors"
              >
                <OmniIcon name={leftPanelVisible ? "panel/left-close" : "panel/left-open"} size={14} />
              </button>
            </TooltipTrigger>
            <TooltipContent side="bottom" className="text-xs">
              {leftPanelVisible ? "Hide" : "Show"} layers panel
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>

      <Separator orientation="vertical" className="h-5 bg-[var(--color-border-subtle)]" />

      {/* Center: Tool strip */}
      <div className="flex items-center gap-0.5 flex-1 justify-center">
        {TOOLS.map((tool) => (
          <ToolButton
            key={tool.id}
            tool={tool}
            active={activeTool === tool.id}
            onClick={() => setActiveTool(tool.id)}
          />
        ))}
      </div>

      <Separator orientation="vertical" className="h-5 bg-[var(--color-border-subtle)]" />

      {/* Right: Zoom + panel toggle */}
      <div className="flex items-center gap-1.5">
        <button
          onClick={zoomOut}
          className="flex items-center justify-center w-7 h-7 rounded text-[var(--mauve-11)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)] transition-colors"
        >
          <OmniIcon name="tool/zoom-out" size={14} />
        </button>

        <button
          onClick={resetZoom}
          className="text-xs font-mono text-[var(--mauve-11)] hover:text-[var(--mauve-12)] transition-colors min-w-[42px] text-center"
        >
          {Math.round(zoom * 100)}%
        </button>

        <button
          onClick={zoomIn}
          className="flex items-center justify-center w-7 h-7 rounded text-[var(--mauve-11)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)] transition-colors"
        >
          <OmniIcon name="tool/zoom-in" size={14} />
        </button>

        <EnvironmentIndicator />

        <Separator orientation="vertical" className="h-5 bg-[var(--color-border-subtle)]" />

        <TooltipProvider delayDuration={400}>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={toggleInspectMode}
                className={cn(
                  "flex items-center justify-center w-7 h-7 rounded transition-colors",
                  inspectMode
                    ? "bg-[var(--violet-3)] text-[var(--violet-11)]"
                    : "text-[var(--mauve-9)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)]"
                )}
              >
                <OmniIcon name="tool/inspect" size={14} />
              </button>
            </TooltipTrigger>
            <TooltipContent side="bottom" className="text-xs">
              Inspect mode
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>

        <TooltipProvider delayDuration={400}>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={toggleTheme}
                className="flex items-center justify-center w-7 h-7 rounded text-[var(--mauve-9)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)] transition-colors"
              >
                <OmniIcon name={theme === "dark" ? "misc/sun" : "misc/moon"} size={14} />
              </button>
            </TooltipTrigger>
            <TooltipContent side="bottom" className="text-xs">
              Switch to {theme === "dark" ? "light" : "dark"} mode
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>

        <TooltipProvider delayDuration={400}>
          <Tooltip>
            <TooltipTrigger asChild>
              <button
                onClick={toggleRightPanel}
                className="flex items-center justify-center w-7 h-7 rounded text-[var(--mauve-9)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)] transition-colors"
              >
                <OmniIcon name={rightPanelVisible ? "panel/right-close" : "panel/right-open"} size={14} />
              </button>
            </TooltipTrigger>
            <TooltipContent side="bottom" className="text-xs">
              {rightPanelVisible ? "Hide" : "Show"} properties panel
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>
    </div>
  );
}
