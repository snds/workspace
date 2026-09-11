import { cn } from "@/lib/utils";
import type { DesignSystemTemplate } from "./templates";

interface TemplateCardProps {
  template: DesignSystemTemplate;
  onSelect: (template: DesignSystemTemplate) => void;
}

export function TemplateCard({ template, onSelect }: TemplateCardProps) {
  const disabled = template.sourcePreset === null;

  return (
    <button
      onClick={() => !disabled && onSelect(template)}
      disabled={disabled}
      className={cn(
        "flex flex-col rounded-lg border transition-all text-left",
        disabled
          ? "opacity-40 cursor-not-allowed border-[var(--mauve-4)] bg-[var(--mauve-2)]"
          : "border-[var(--mauve-5)] bg-[var(--mauve-2)] hover:border-[var(--violet-7)] hover:bg-[var(--mauve-3)] cursor-pointer",
      )}
    >
      {/* Color swatches */}
      <div className="flex gap-1 px-3 pt-3 pb-2">
        {template.previewColors.map((hex, i) => (
          <div
            key={i}
            className="w-8 h-8 rounded-md border border-[var(--mauve-5)]"
            style={{ backgroundColor: hex }}
          />
        ))}
      </div>

      {/* Info */}
      <div className="px-3 pb-3">
        <h4 className="text-[11px] font-semibold text-[var(--mauve-12)]">
          {template.name}
        </h4>
        <p className="text-[9px] text-[var(--mauve-9)] mt-0.5 leading-relaxed">
          {template.tagline}
        </p>

        {/* Feature badges */}
        <div className="flex flex-wrap gap-1 mt-2">
          {template.features.map((feat) => (
            <span
              key={feat}
              className="text-[8px] px-1.5 py-0.5 rounded bg-[var(--mauve-4)] text-[var(--mauve-10)]"
            >
              {feat}
            </span>
          ))}
        </div>

        {disabled && (
          <p className="text-[8px] text-[var(--mauve-8)] mt-1.5 italic">
            Coming soon
          </p>
        )}
      </div>
    </button>
  );
}
