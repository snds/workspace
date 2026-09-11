import { ColorSwatch } from "./ColorSwatch";
import type { ColorPalette, CodeFormat } from "@/types/colorSystem";
import { RADIX_STEPS } from "@/types/colorSystem";

export function ColorScaleRow({
  palette,
  mode,
  codeFormat,
  showAlpha = false,
}: {
  palette: ColorPalette;
  mode: "light" | "dark";
  codeFormat: CodeFormat;
  showAlpha?: boolean;
}) {
  const variantKey = showAlpha
    ? (mode === "dark" ? "darkA" : "lightA")
    : mode;
  const variant = palette[variantKey];

  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center gap-2">
        <span className="text-[10px] font-semibold text-[var(--mauve-11)] w-16 capitalize truncate">
          {palette.label}
        </span>
        <div
          className="w-3 h-3 rounded-full border border-[var(--mauve-6)] flex-shrink-0"
          style={{ background: palette.seedHex }}
        />
      </div>

      {/* Color swatches */}
      <div className="grid gap-0.5" style={{ gridTemplateColumns: "repeat(12, 1fr)" }}>
        {RADIX_STEPS.map((step) => {
          const stepData = variant.steps[step];
          if (!stepData) {
            return (
              <div
                key={step}
                className="bg-[var(--mauve-4)] rounded"
                style={{ minHeight: 36 }}
              />
            );
          }
          return <ColorSwatch key={step} data={stepData} codeFormat={codeFormat} />;
        })}
      </div>
    </div>
  );
}
