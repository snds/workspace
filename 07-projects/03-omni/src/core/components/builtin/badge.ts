import type { ComponentBlueprint } from "../types";

export const badgeBlueprint: ComponentBlueprint = {
  id: "badge",
  name: "Badge",
  category: "display",
  description: "A small status indicator or label",
  icon: "display/badge",
  tags: ["badge", "tag", "label", "status", "chip"],

  props: [
    { name: "label", type: "string", label: "Label", defaultValue: "Badge", affectsCanvas: true },
    {
      name: "variant", type: "enum", label: "Variant", defaultValue: "default",
      options: [
        { value: "default", label: "Default" },
        { value: "secondary", label: "Secondary" },
        { value: "destructive", label: "Destructive" },
        { value: "outline", label: "Outline" },
      ],
    },
  ],

  variants: [
    {
      id: "secondary", name: "Secondary",
      propOverrides: { variant: "secondary" },
      tokenOverrides: { background: "badge.secondary.background", foreground: "badge.secondary.foreground" },
      canvasOverrides: { fill: "surface.subtle" },
    },
    {
      id: "destructive", name: "Destructive",
      propOverrides: { variant: "destructive" },
      tokenOverrides: { background: "badge.destructive.background", foreground: "badge.destructive.foreground" },
      canvasOverrides: { fill: "destructive.background" },
    },
    {
      id: "outline", name: "Outline",
      propOverrides: { variant: "outline" },
      tokenOverrides: { background: "badge.outline.background", foreground: "badge.outline.foreground" },
      canvasOverrides: { fill: "surface.0", stroke: "border.default", strokeWidth: 1 },
    },
  ],

  tokenBindings: {
    background: "badge.background",
    foreground: "badge.foreground",
  },

  canvasTemplate: {
    type: "frame",
    width: 60,
    height: 22,
    fill: "badge.background",
    cornerRadius: 9999,
    children: [
      {
        name: "Label", type: "text",
        offsetX: 0, offsetY: 0, width: 60, height: 22,
        text: "Badge", textColor: "badge.foreground",
        fontSize: 10, fontWeight: 500, textAlign: "center", verticalAlign: "middle",
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/badge",
      componentName: "Badge",
      propMappings: { label: "children", variant: "variant" },
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Chip",
      componentName: "Chip",
      propMappings: { label: "label", variant: "variant", size: "size" },
    },
  },
};
