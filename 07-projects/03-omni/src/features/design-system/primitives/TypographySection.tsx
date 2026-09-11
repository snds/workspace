import { TYPOGRAPHY_TOKENS } from "@/features/tokens/staticTokens";

function TokenRow({ name, value, preview }: { name: string; value: string; preview: React.ReactNode }) {
  return (
    <div className="flex items-center gap-3 py-1.5 px-2 rounded hover:bg-[var(--mauve-3)] transition-colors group">
      <span className="text-[10px] font-mono text-[var(--mauve-11)] w-40 flex-shrink-0 truncate">
        {name}
      </span>
      <span className="text-[10px] font-mono text-[var(--mauve-9)] w-20 flex-shrink-0">
        {value}
      </span>
      <div className="flex-1 min-w-0">{preview}</div>
    </div>
  );
}

export function TypographySection() {
  return (
    <>
      {/* Font Size */}
      <div id="section-typography-size" className="scroll-mt-4">
        <h4 className="text-[10px] font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-2">
          Font Size
        </h4>
        <div className="flex flex-col">
          {TYPOGRAPHY_TOKENS["Font Size"].map((t) => (
            <TokenRow
              key={t.id}
              name={t.name}
              value={t.shortValue}
              preview={
                <span
                  className="text-[var(--mauve-12)] leading-tight truncate block"
                  style={{ fontSize: t.meta ?? 16 }}
                >
                  Aa
                </span>
              }
            />
          ))}
        </div>
      </div>

      {/* Font Family */}
      <div id="section-typography-family" className="scroll-mt-4 mt-6">
        <h4 className="text-[10px] font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-2">
          Font Family
        </h4>
        <div className="flex flex-col">
          {TYPOGRAPHY_TOKENS["Font Family"].map((t) => (
            <TokenRow
              key={t.id}
              name={t.name}
              value={t.shortValue}
              preview={
                <span
                  className="text-sm text-[var(--mauve-12)] truncate block"
                  style={{ fontFamily: t.fullValue }}
                >
                  The quick brown fox jumps over the lazy dog
                </span>
              }
            />
          ))}
        </div>
      </div>

      {/* Font Weight */}
      <div id="section-typography-weight" className="scroll-mt-4 mt-6">
        <h4 className="text-[10px] font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-2">
          Font Weight
        </h4>
        <div className="flex flex-col">
          {TYPOGRAPHY_TOKENS["Font Weight"].map((t) => (
            <TokenRow
              key={t.id}
              name={t.name}
              value={t.shortValue}
              preview={
                <span
                  className="text-sm text-[var(--mauve-12)] truncate block"
                  style={{ fontWeight: t.meta ?? 400 }}
                >
                  Design tokens
                </span>
              }
            />
          ))}
        </div>
      </div>

      {/* Line Height */}
      <div id="section-typography-lineheight" className="scroll-mt-4 mt-6">
        <h4 className="text-[10px] font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-2">
          Line Height
        </h4>
        <div className="flex flex-col">
          {TYPOGRAPHY_TOKENS["Line Height"].map((t) => (
            <TokenRow
              key={t.id}
              name={t.name}
              value={t.shortValue}
              preview={
                <span
                  className="text-xs text-[var(--mauve-12)] block"
                  style={{ lineHeight: t.meta ?? 1.5 }}
                >
                  Line one<br />Line two
                </span>
              }
            />
          ))}
        </div>
      </div>

      {/* Letter Spacing */}
      <div id="section-typography-tracking" className="scroll-mt-4 mt-6">
        <h4 className="text-[10px] font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-2">
          Letter Spacing
        </h4>
        <div className="flex flex-col">
          {TYPOGRAPHY_TOKENS["Letter Spacing"].map((t) => (
            <TokenRow
              key={t.id}
              name={t.name}
              value={t.shortValue}
              preview={
                <span
                  className="text-sm text-[var(--mauve-12)] truncate block"
                  style={{ letterSpacing: t.fullValue }}
                >
                  TYPOGRAPHY
                </span>
              }
            />
          ))}
        </div>
      </div>
    </>
  );
}
