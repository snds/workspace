import { SPACING_TOKENS } from "@/features/tokens/staticTokens";

export function SpaceSection() {
  const maxMeta = Math.max(...SPACING_TOKENS.filter((t) => t.meta !== undefined && t.meta <= 128).map((t) => t.meta!));

  return (
    <div id="section-space" className="scroll-mt-4">
      <h3 className="text-[11px] font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-4">
        Space
      </h3>
      <div className="flex flex-col gap-0.5">
        {SPACING_TOKENS.map((t) => (
          <div
            key={t.id}
            className="flex items-center gap-3 py-1.5 px-2 rounded hover:bg-[var(--mauve-3)] transition-colors"
          >
            <span className="text-[10px] font-mono text-[var(--mauve-11)] w-28 flex-shrink-0 truncate">
              {t.name}
            </span>
            <span className="text-[10px] font-mono text-[var(--mauve-9)] w-16 flex-shrink-0 text-right">
              {t.shortValue}
            </span>
            <div className="flex-1 min-w-0 h-4 flex items-center">
              {(t.meta ?? 0) > 0 && (
                <div
                  className="h-2.5 rounded-sm bg-[var(--violet-9)]"
                  style={{ width: `${((t.meta! / maxMeta) * 100).toFixed(1)}%`, minWidth: 2 }}
                />
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
