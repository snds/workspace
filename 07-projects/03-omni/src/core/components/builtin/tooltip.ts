import type { ComponentBlueprint } from "../types";

export const tooltipBlueprint: ComponentBlueprint = {
  id: "tooltip",
  name: "Tooltip",
  category: "overlay",
  description: "A small informational popup that appears on hover",
  icon: "overlay/tooltip",
  tags: ["tooltip", "hint", "hover", "info", "popover"],

  props: [
    { name: "label", type: "string", label: "Label", defaultValue: "Tooltip text", affectsCanvas: true },
    { name: "side", type: "enum", label: "Side", defaultValue: "top", options: [
      { value: "top", label: "Top" },
      { value: "right", label: "Right" },
      { value: "bottom", label: "Bottom" },
      { value: "left", label: "Left" },
    ]},
    { name: "delayDuration", type: "number", label: "Delay (ms)", defaultValue: 200 },
  ],

  slots: [
    { name: "trigger", label: "Trigger", description: "Element that triggers the tooltip" },
  ],

  tokenBindings: {
    background: "tooltip.background",
    foreground: "tooltip.foreground",
  },

  canvasTemplate: {
    type: "frame",
    width: 120,
    height: 28,
    fill: "tooltip.background",
    cornerRadius: 6,
    children: [
      {
        name: "Label", type: "text",
        offsetX: 0, offsetY: 0, width: 120, height: 28,
        text: "Tooltip text", textColor: "tooltip.foreground",
        fontSize: 11, textAlign: "center", verticalAlign: "middle",
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/tooltip",
      componentName: "Tooltip",
      propMappings: { label: "content", side: "side", delayDuration: "delayDuration" },
      additionalImports: ["TooltipTrigger", "TooltipContent", "TooltipProvider"],
      wrapper: "<TooltipProvider><Tooltip><TooltipTrigger>{trigger}</TooltipTrigger><TooltipContent>{content}</TooltipContent></Tooltip></TooltipProvider>",
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Tooltip",
      componentName: "Tooltip",
      propMappings: { label: "title", side: "placement" },
    },
  },
};
