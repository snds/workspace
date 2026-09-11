import type { ComponentBlueprint } from "../types";

export const sliderBlueprint: ComponentBlueprint = {
  id: "slider",
  name: "Slider",
  category: "input",
  description: "A draggable slider for selecting a numeric value",
  icon: "input/slider",
  tags: ["slider", "range", "value", "drag", "input"],

  props: [
    { name: "value", type: "number", label: "Value", defaultValue: 60, affectsCanvas: true },
    { name: "min", type: "number", label: "Min", defaultValue: 0 },
    { name: "max", type: "number", label: "Max", defaultValue: 100 },
    { name: "step", type: "number", label: "Step", defaultValue: 1 },
    { name: "disabled", type: "boolean", label: "Disabled", defaultValue: false },
  ],

  events: [
    { name: "onValueChange", label: "Value Change", description: "Fired when the slider value changes", payloadType: "number[]" },
    { name: "onValueCommit", label: "Value Commit", description: "Fired when dragging ends", payloadType: "number[]" },
  ],

  tokenBindings: {
    trackBackground: "slider.track.background",
    rangeBackground: "slider.range.background",
    thumbBackground: "slider.thumb.background",
    thumbBorder: "slider.thumb.border",
  },

  canvasTemplate: {
    type: "frame",
    width: 240,
    height: 28,
    children: [
      {
        name: "SliderTrack", type: "frame",
        offsetX: 0, offsetY: 11, width: 240, height: 6,
        fill: "slider.track.background", cornerRadius: 9999,
      },
      {
        name: "SliderRange", type: "frame",
        offsetX: 0, offsetY: 11, width: 144, height: 6,
        fill: "slider.range.background", cornerRadius: 9999,
      },
      {
        name: "SliderThumb", type: "frame",
        offsetX: 137, offsetY: 7, width: 14, height: 14,
        fill: "slider.thumb.background",
        stroke: "slider.thumb.border", strokeWidth: 2,
        cornerRadius: 9999,
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/slider",
      componentName: "Slider",
      propMappings: { value: "value", min: "min", max: "max", step: "step", disabled: "disabled" },
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Slider",
      componentName: "Slider",
      propMappings: { value: "value", min: "min", max: "max", step: "step", disabled: "disabled" },
    },
  },
};
