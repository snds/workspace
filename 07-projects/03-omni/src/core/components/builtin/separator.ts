import type { ComponentBlueprint } from "../types";

export const separatorBlueprint: ComponentBlueprint = {
  id: "separator",
  name: "Separator",
  category: "layout",
  description: "A visual divider between content sections",
  icon: "layout/separator",
  tags: ["separator", "divider", "line", "hr", "rule"],

  props: [
    { name: "orientation", type: "enum", label: "Orientation", defaultValue: "horizontal", options: [
      { value: "horizontal", label: "Horizontal" },
      { value: "vertical", label: "Vertical" },
    ], affectsCanvas: true },
  ],

  tokenBindings: {
    background: "separator.background",
  },

  canvasTemplate: {
    type: "rectangle",
    width: 200,
    height: 1,
    fill: "separator.background",
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/separator",
      componentName: "Separator",
      propMappings: { orientation: "orientation" },
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Divider",
      componentName: "Divider",
      propMappings: { orientation: "orientation" },
    },
  },
};
