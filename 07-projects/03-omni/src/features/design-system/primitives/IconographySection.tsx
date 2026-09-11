import { Grid3X3 } from "lucide-react";
import { useTeamContextStore } from "@/stores/teamContext.store";

export function IconographySection() {
  const iconLibrary = useTeamContextStore((s) => s.profile.iconLibrary);

  return (
    <div id="section-iconography" className="scroll-mt-4">
      <h3 className="text-[11px] font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-4">
        Iconography
      </h3>
      <div className="flex items-center gap-3 p-4 rounded-lg border border-dashed border-[var(--mauve-5)] bg-[var(--mauve-2)]">
        <Grid3X3 className="w-5 h-5 text-[var(--mauve-7)]" />
        <div>
          <p className="text-[11px] text-[var(--mauve-11)]">
            Current library: <span className="font-medium text-[var(--mauve-12)]">{iconLibrary?.id || "Lucide"}</span>
          </p>
          <p className="text-[10px] text-[var(--mauve-9)] mt-0.5">
            Icon management coming soon
          </p>
        </div>
      </div>
    </div>
  );
}
