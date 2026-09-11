import { bestForeground } from "@/lib/color";
import { formatColor } from "@/lib/colorSpaces";
import type { ColorShadeData, CodeFormat } from "@/types/colorSystem";

export function ColorSwatch({
  data,
  codeFormat,
}: {
  data: ColorShadeData;
  codeFormat: CodeFormat;
}) {
  const fg = bestForeground(data.hex);
  const displayValue = formatColor(data.hex, codeFormat);

  // Use the formatted CSS color as the background so the swatch renders
  // in the selected color space. Modern browsers support oklch(), oklab(),
  // lab(), lch(), color(display-p3 ...) natively — colors outside sRGB
  // gamut will render differently on capable displays.
  const bgColor = displayValue;

  return (
    <div
      className="flex flex-col items-center justify-end group relative"
      style={{ background: bgColor, minHeight: 36, borderRadius: 4 }}
    >
      <div className="opacity-0 group-hover:opacity-100 absolute inset-0 flex flex-col items-center justify-center transition-opacity bg-black/30 rounded z-10">
        <span className="text-[9px] font-bold text-white">{data.step}</span>
        <span className="text-[7px] text-white/70 font-mono leading-tight text-center px-0.5 break-all">
          {displayValue}
        </span>
      </div>
      {(data.wcagAA || data.wcagAAA) && (
        <div
          className="absolute bottom-0.5 right-0.5 text-[7px] font-bold px-0.5 rounded"
          style={{ color: fg, opacity: 0.7 }}
        >
          {data.wcagAAA ? "AAA" : "AA"}
        </div>
      )}
    </div>
  );
}
