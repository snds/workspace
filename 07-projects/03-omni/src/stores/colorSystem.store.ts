import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import { devtools, persist } from "zustand/middleware";
import type { ColorSystem, RadixStep, ColorSpace, CodeFormat, BrandColors } from "@/types/colorSystem";
import { computeAllRepresentations } from "@/lib/colorSpaces";

interface ColorSystemState {
  colorSystem: ColorSystem | null;
  isDirty: boolean;
  activeMode: string;
  colorSpace: ColorSpace;
  codeFormat: CodeFormat;
  brandColors: BrandColors;
}

interface ColorSystemActions {
  setBrandColor(slot: keyof BrandColors, value: string | null): void;
  setColorSystem(system: ColorSystem): void;
  updateStepHex(
    paletteKey: string,
    step: RadixStep,
    hex: string,
    variant?: "light" | "dark"
  ): void;
  updateDataVizColor(index: number, hex: string): void;
  setDataVizMode(mode: "auto" | "custom"): void;
  setActiveMode(modeId: string): void;
  setColorSpace(space: ColorSpace): void;
  setCodeFormat(format: CodeFormat): void;
  markSaved(): void;
  clearColorSystem(): void;
}

export const useColorSystemStore = create<ColorSystemState & ColorSystemActions>()(
  devtools(
    persist(
      immer((set) => ({
        colorSystem: null,
        isDirty: false,
        activeMode: "light",
        colorSpace: "oklch",
        codeFormat: "oklch",
        brandColors: { primary: "#7c6af7", secondary: null, accent: null },

        setBrandColor: (slot, value) =>
          set((s) => {
            if (slot === "primary") {
              if (value !== null) s.brandColors.primary = value;
            } else {
              s.brandColors[slot] = value;
            }
          }),

        setColorSystem: (system) =>
          set((s) => {
            s.colorSystem = system;
            s.isDirty = true;
            const defaultMode = system.modes.find((m) => m.isDefault);
            if (defaultMode) {
              s.activeMode = defaultMode.id;
            }
          }),

        updateStepHex: (paletteKey, step, hex, variant) =>
          set((s) => {
            const palette = s.colorSystem?.palettes[paletteKey];
            if (!palette) return;
            const v = variant ?? (s.activeMode === "dark" ? "dark" : "light");
            const shadeData = palette[v].steps[step];
            if (shadeData) {
              shadeData.hex = hex;
              shadeData.representations = computeAllRepresentations(hex);
              s.isDirty = true;
            }
          }),

        updateDataVizColor: (index, hex) =>
          set((s) => {
            if (!s.colorSystem?.dataViz) return;
            const color = s.colorSystem.dataViz.colors.find(
              (c) => c.index === index
            );
            if (color) {
              color.hex = hex;
              s.isDirty = true;
            }
          }),

        setDataVizMode: (mode) =>
          set((s) => {
            if (!s.colorSystem?.dataViz) return;
            s.colorSystem.dataViz.mode = mode;
          }),

        setActiveMode: (modeId) =>
          set((s) => {
            s.activeMode = modeId;
          }),

        setColorSpace: (space) =>
          set((s) => {
            s.colorSpace = space;
          }),

        setCodeFormat: (format) =>
          set((s) => {
            s.codeFormat = format;
          }),

        markSaved: () =>
          set((s) => {
            s.isDirty = false;
          }),

        clearColorSystem: () =>
          set((s) => {
            s.colorSystem = null;
            s.isDirty = false;
          }),
      })),
      {
        name: "omni-color-system-v2",
        partialize: (state) => ({
          colorSystem: state.colorSystem,
          colorSpace: state.colorSpace,
          codeFormat: state.codeFormat,
          brandColors: state.brandColors,
        }),
      }
    ),
    { name: "ColorSystemStore" }
  )
);
