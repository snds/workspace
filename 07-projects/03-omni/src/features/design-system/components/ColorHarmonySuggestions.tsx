import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/components/ui/tooltip";
import type { HarmonySuggestion } from "@/lib/colorHarmony";

export function ColorHarmonySuggestions({
  suggestions,
  onSelect,
}: {
  suggestions: HarmonySuggestion[];
  onSelect: (hex: string) => void;
}) {
  if (suggestions.length === 0) return null;

  return (
    <TooltipProvider delayDuration={300}>
      <div className="flex flex-col gap-1 -mt-2">
        <span className="text-[9px] text-[var(--mauve-8)]">
          Suggested harmonies
        </span>
        <div className="flex flex-wrap gap-1">
          {suggestions.map((s) => (
            <Tooltip key={s.harmonyType}>
              <TooltipTrigger asChild>
                <button
                  onClick={() => onSelect(s.hex)}
                  className="flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-[var(--mauve-3)] border border-[var(--mauve-5)] hover:border-[var(--violet-7)] transition-colors"
                >
                  <span
                    className="w-2.5 h-2.5 rounded-full flex-shrink-0 border border-[var(--mauve-6)]"
                    style={{ background: s.hex }}
                  />
                  <span className="text-[8px] text-[var(--mauve-10)] hover:text-[var(--mauve-12)]">
                    {s.label}
                  </span>
                </button>
              </TooltipTrigger>
              <TooltipContent side="bottom" className="max-w-[180px]">
                <p className="text-[9px]">{s.description}</p>
                <p className="text-[8px] font-mono mt-0.5 opacity-70">{s.hex}</p>
              </TooltipContent>
            </Tooltip>
          ))}
        </div>
      </div>
    </TooltipProvider>
  );
}
