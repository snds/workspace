import type { ComponentBlueprint } from "../types";

export const skeletonBlueprint: ComponentBlueprint = {
  id: "skeleton",
  name: "Skeleton",
  category: "feedback",
  description: "A placeholder loading animation for content",
  icon: "feedback/skeleton",
  tags: ["skeleton", "loading", "placeholder", "shimmer", "pulse"],

  props: [
    { name: "width", type: "number", label: "Width", defaultValue: 200, affectsCanvas: true },
    { name: "height", type: "number", label: "Height", defaultValue: 20, affectsCanvas: true },
    { name: "variant", type: "enum", label: "Shape", defaultValue: "rectangle", options: [
      { value: "rectangle", label: "Rectangle" },
      { value: "circle", label: "Circle" },
    ]},
  ],

  tokenBindings: {
    background: "skeleton.background",
  },

  canvasTemplate: {
    type: "rectangle",
    width: 200,
    height: 20,
    fill: "skeleton.background",
    cornerRadius: 4,
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/skeleton",
      componentName: "Skeleton",
      propMappings: { width: "className", height: "className" },
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Skeleton",
      componentName: "Skeleton",
      propMappings: { width: "width", height: "height", variant: "variant" },
    },
  },
};
