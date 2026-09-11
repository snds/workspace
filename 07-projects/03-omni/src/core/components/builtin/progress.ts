import type { ComponentBlueprint } from "../types";

export const progressBlueprint: ComponentBlueprint = {
  id: "progress",
  name: "Progress",
  category: "feedback",
  description: "A horizontal progress bar indicating completion",
  icon: "feedback/progress",
  tags: ["progress", "bar", "loading", "percentage", "indicator"],

  props: [
    { name: "value", type: "number", label: "Value (%)", defaultValue: 60, affectsCanvas: true },
    { name: "max", type: "number", label: "Max", defaultValue: 100 },
  ],

  tokenBindings: {
    trackBackground: "progress.track.background",
    indicatorBackground: "progress.indicator.background",
  },

  canvasTemplate: {
    type: "frame",
    width: 240,
    height: 8,
    fill: "progress.track.background",
    cornerRadius: 9999,
    children: [
      {
        name: "Progress.Indicator", type: "frame",
        offsetX: 0, offsetY: 0, width: 144, height: 8,
        fill: "progress.indicator.background", cornerRadius: 9999,
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/progress",
      componentName: "Progress",
      propMappings: { value: "value", max: "max" },
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/LinearProgress",
      componentName: "LinearProgress",
      propMappings: { value: "value" },
    },
  },
};
