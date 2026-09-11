import { EFFECT_TOKENS } from "@/features/tokens/staticTokens";

export function EffectsSection() {
  return (
    <>
      {/* Shadow */}
      <div id="section-effects-shadow" className="scroll-mt-4">
        <h4 className="text-[10px] font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-3">
          Shadow
        </h4>
        <div className="grid grid-cols-4 gap-3">
          {EFFECT_TOKENS["Shadow"].map((t) => (
            <div key={t.id} className="flex flex-col items-center gap-2">
              <div
                className="w-16 h-16 rounded-lg bg-[var(--mauve-3)] border border-[var(--mauve-5)]"
                style={{ boxShadow: t.fullValue === "none" ? undefined : t.fullValue }}
              />
              <span className="text-[9px] font-mono text-[var(--mauve-9)]">{t.name}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Blur */}
      <div id="section-effects-blur" className="scroll-mt-4 mt-6">
        <h4 className="text-[10px] font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-3">
          Blur
        </h4>
        <div className="grid grid-cols-4 gap-3">
          {EFFECT_TOKENS["Blur"].map((t) => (
            <div key={t.id} className="flex flex-col items-center gap-2">
              <div className="w-16 h-16 rounded-lg bg-[var(--violet-9)] relative overflow-hidden">
                <div
                  className="absolute inset-0 bg-[var(--mauve-12)]"
                  style={{ filter: `blur(${t.fullValue})` }}
                />
              </div>
              <span className="text-[9px] font-mono text-[var(--mauve-9)]">{t.name}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Opacity */}
      <div id="section-effects-opacity" className="scroll-mt-4 mt-6">
        <h4 className="text-[10px] font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-3">
          Opacity
        </h4>
        <div className="flex flex-wrap gap-2">
          {EFFECT_TOKENS["Opacity"].map((t) => (
            <div key={t.id} className="flex flex-col items-center gap-1.5">
              <div
                className="w-10 h-10 rounded bg-[var(--violet-9)]"
                style={{ opacity: t.meta ?? 1 }}
              />
              <span className="text-[9px] font-mono text-[var(--mauve-9)]">{t.shortValue}</span>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
