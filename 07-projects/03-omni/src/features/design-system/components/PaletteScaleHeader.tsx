import { RADIX_STEPS, RADIX_STEP_GROUPS } from "@/types/colorSystem";

export function PaletteScaleHeader() {
  return (
    <div className="flex flex-col gap-0 sticky top-0 z-10 bg-[var(--color-surface-0)] pb-2">
      {/* Semantic group labels */}
      <div className="grid gap-0.5" style={{ gridTemplateColumns: "repeat(12, 1fr)" }}>
        {RADIX_STEP_GROUPS.map((group) => (
          <div
            key={group.label}
            className="pb-1.5 border-b border-[var(--mauve-6)]"
            style={{ gridColumn: `span ${group.steps.length}` }}
          >
            <span className="text-[10px] text-[var(--mauve-11)] font-medium">
              {group.label}
            </span>
          </div>
        ))}
      </div>

      {/* Step numbers */}
      <div
        className="grid gap-0.5 mt-1.5"
        style={{ gridTemplateColumns: "repeat(12, 1fr)" }}
      >
        {RADIX_STEPS.map((step) => (
          <span
            key={step}
            className="text-[9px] text-[var(--mauve-9)] text-center font-medium"
          >
            {step}
          </span>
        ))}
      </div>
    </div>
  );
}
