import { useMemo } from "react";
import { Eye } from "lucide-react";
import { cn } from "@/lib/utils";
import { useColorSystemStore } from "@/stores/colorSystem.store";
import { bestForeground, simulateCVD, generateDataVizPalette } from "@/lib/color";
import { PaletteScaleHeader } from "./PaletteScaleHeader";
import { ColorScaleRow } from "./ColorScaleRow";
import type { ColorSystem, CodeFormat, DataVizColor } from "@/types/colorSystem";

export function DataVizSection({
  colorSystem,
  codeFormat,
  mode,
  showAlpha,
}: {
  colorSystem: ColorSystem;
  codeFormat: CodeFormat;
  mode: "light" | "dark";
  showAlpha: boolean;
}) {
  const { setDataVizMode } = useColorSystemStore();
  const dataViz = colorSystem.dataViz;
  if (!dataViz) return null;

  const isCustom = dataViz.mode === "custom";

  // Derive full 12-step palettes from each data viz seed color
  const dvPalettes = useMemo(
    () => dataViz.colors.map((c) => generateDataVizPalette(c)),
    [dataViz.colors],
  );

  return (
    <div className="space-y-4">
      {/* Header with mode toggle */}
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-semibold text-[var(--mauve-12)]">
          Data Visualization
        </span>
        <div className="flex rounded-md border border-[var(--mauve-5)] overflow-hidden">
          <button
            onClick={() => setDataVizMode("auto")}
            className={cn(
              "px-2 py-0.5 text-[9px] transition-colors",
              !isCustom
                ? "bg-[var(--mauve-4)] text-[var(--mauve-12)]"
                : "text-[var(--mauve-9)] hover:text-[var(--mauve-11)]",
            )}
          >
            Auto
          </button>
          <button
            onClick={() => setDataVizMode("custom")}
            className={cn(
              "px-2 py-0.5 text-[9px] transition-colors",
              isCustom
                ? "bg-[var(--mauve-4)] text-[var(--mauve-12)]"
                : "text-[var(--mauve-9)] hover:text-[var(--mauve-11)]",
            )}
          >
            Custom
          </button>
        </div>
      </div>

      {/* Shared scale header */}
      <PaletteScaleHeader />

      {/* Scale rows for each data viz color */}
      <div className="space-y-3">
        {dvPalettes.map((palette) => (
          <ColorScaleRow
            key={palette.key}
            palette={palette}
            mode={mode}
            codeFormat={codeFormat}
            showAlpha={showAlpha}
          />
        ))}
      </div>

      {/* Colorblind simulation preview */}
      <div className="space-y-2 border-t border-[var(--mauve-4)] pt-3">
        <div className="flex items-center gap-1.5">
          <Eye className="w-3 h-3 text-[var(--mauve-9)]" />
          <span className="text-[9px] text-[var(--mauve-9)]">
            Deuteranopia simulation (seed colors)
          </span>
        </div>
        <div className="grid gap-1" style={{ gridTemplateColumns: `repeat(${dataViz.colors.length}, 1fr)` }}>
          {dataViz.colors.map((c: DataVizColor) => {
            const simulated = simulateCVD(c.hex, "deutan");
            const fg = bestForeground(simulated);
            return (
              <div key={c.index} className="flex flex-col items-center gap-0.5">
                <div
                  className="w-full aspect-square rounded-md border border-[var(--mauve-6)] flex items-center justify-center"
                  style={{ background: simulated, minWidth: 24, maxWidth: 40 }}
                >
                  <span className="text-[8px] font-bold" style={{ color: fg }}>
                    {c.index}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
