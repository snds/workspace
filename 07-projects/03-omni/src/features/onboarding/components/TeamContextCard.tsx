import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { UsageTier } from "@/core/context/types";

// ─── Types ───────────────────────────────────────────────────────────────────

export interface TeamContextPreset {
  id: string;
  name: string;
  description: string;
  tier: UsageTier;
  icon: string;
}

// ─── Tier badge color mapping ────────────────────────────────────────────────

const TIER_BADGE_STYLES: Record<
  UsageTier,
  { label: string; className: string }
> = {
  0: {
    label: "Tier 0",
    className: "border-[var(--mauve-7)] text-[var(--mauve-11)] bg-[var(--mauve-3)]",
  },
  1: {
    label: "Tier 1",
    className: "border-[hsl(210,70%,40%)] text-[hsl(210,80%,70%)] bg-[hsl(210,80%,12%)]",
  },
  2: {
    label: "Tier 2",
    className: "border-[var(--violet-7)] text-[var(--violet-11)] bg-[var(--violet-3)]",
  },
  3: {
    label: "Tier 3",
    className: "border-[hsl(42,80%,45%)] text-[hsl(42,80%,70%)] bg-[hsl(42,60%,12%)]",
  },
};

// ─── Component ───────────────────────────────────────────────────────────────

interface TeamContextCardProps {
  preset: TeamContextPreset;
  selected: boolean;
  onSelect: () => void;
}

export function TeamContextCard({
  preset,
  selected,
  onSelect,
}: TeamContextCardProps) {
  const tierBadge = TIER_BADGE_STYLES[preset.tier];

  return (
    <button
      onClick={onSelect}
      className={cn(
        "flex flex-col gap-3 p-4 rounded-lg border text-left transition-all duration-150 cursor-pointer",
        selected
          ? "border-[var(--violet-7)] bg-[var(--violet-3)] ring-1 ring-[var(--violet-7)]"
          : "border-[var(--mauve-5)] bg-[var(--mauve-3)] hover:border-[var(--mauve-6)] hover:bg-[var(--mauve-4)]",
      )}
    >
      {/* Icon + Tier badge row */}
      <div className="flex items-center justify-between">
        <div
          className={cn(
            "w-8 h-8 rounded-md flex items-center justify-center text-base",
            selected ? "bg-[var(--violet-5)]" : "bg-[var(--mauve-4)]",
          )}
        >
          <span role="img" aria-label={preset.name}>
            {preset.icon}
          </span>
        </div>
        <Badge
          variant="outline"
          className={cn("text-[9px] px-1.5 py-0 h-4", tierBadge.className)}
        >
          {tierBadge.label}
        </Badge>
      </div>

      {/* Name + Description */}
      <div>
        <p
          className={cn(
            "text-xs font-semibold leading-tight",
            selected ? "text-[var(--violet-12)]" : "text-[var(--mauve-12)]",
          )}
        >
          {preset.name}
        </p>
        <p
          className={cn(
            "text-[10px] mt-1 leading-relaxed",
            selected ? "text-[var(--violet-11)]" : "text-[var(--mauve-9)]",
          )}
        >
          {preset.description}
        </p>
      </div>
    </button>
  );
}
