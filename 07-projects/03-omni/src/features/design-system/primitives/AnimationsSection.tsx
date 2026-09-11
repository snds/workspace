import { Zap } from "lucide-react";

export function AnimationsSection() {
  return (
    <div id="section-animations" className="scroll-mt-4">
      <h3 className="text-[11px] font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-4">
        Animations
      </h3>
      <div className="flex items-center gap-3 p-4 rounded-lg border border-dashed border-[var(--mauve-5)] bg-[var(--mauve-2)]">
        <Zap className="w-5 h-5 text-[var(--mauve-7)]" />
        <div>
          <p className="text-[11px] text-[var(--mauve-11)]">
            Duration and easing token definitions
          </p>
          <p className="text-[10px] text-[var(--mauve-9)] mt-0.5">
            Animation tokens coming soon
          </p>
        </div>
      </div>
    </div>
  );
}
