import { BORDER_TOKENS } from "@/features/tokens/staticTokens";

export function RadiusSection() {
  const tokens = BORDER_TOKENS["Radius"];

  return (
    <div id="section-radius" className="scroll-mt-4">
      <h3 className="text-[11px] font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-4">
        Radius
      </h3>
      <div className="flex flex-wrap gap-4">
        {tokens.map((t) => {
          const radiusVal = t.meta !== undefined && t.meta < 100 ? t.meta : undefined;
          return (
            <div key={t.id} className="flex flex-col items-center gap-2">
              <div
                className="w-14 h-14 border-2 border-[var(--violet-9)] bg-[var(--mauve-3)]"
                style={{
                  borderRadius: radiusVal !== undefined ? radiusVal : "9999px",
                }}
              />
              <div className="text-center">
                <span className="text-[9px] font-mono text-[var(--mauve-11)] block">
                  {t.name.replace("radius.", "")}
                </span>
                <span className="text-[8px] text-[var(--mauve-9)]">
                  {t.shortValue}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
