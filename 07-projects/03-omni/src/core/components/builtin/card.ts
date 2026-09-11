import type { ComponentBlueprint } from "../types";

export const cardBlueprint: ComponentBlueprint = {
  id: "card",
  name: "Card",
  category: "display",
  description: "A container card with header, content, and optional footer",
  icon: "display/card",
  tags: ["card", "container", "panel", "surface", "box"],

  props: [
    { name: "title", type: "string", label: "Title", defaultValue: "Card Title", affectsCanvas: true },
    { name: "description", type: "string", label: "Description", defaultValue: "Card description goes here.", affectsCanvas: true },
    { name: "content", type: "string", label: "Content", defaultValue: "Card content goes here.", affectsCanvas: true },
  ],

  slots: [
    { name: "header", label: "Header", description: "Card header content" },
    { name: "content", label: "Content", description: "Card body content" },
    { name: "footer", label: "Footer", description: "Card footer content" },
  ],

  tokenBindings: {
    background: "card.background",
    foreground: "card.foreground",
    mutedForeground: "card.muted.foreground",
    border: "card.border",
    radius: "card.radius",
  },

  canvasTemplate: {
    type: "frame",
    width: 320,
    height: 160,
    fill: "card.background",
    stroke: "card.border",
    strokeWidth: 1,
    cornerRadius: 8,
    children: [
      {
        name: "CardHeader", type: "frame",
        offsetX: 0, offsetY: 0, width: 320, height: 56,
        children: [
          {
            name: "CardTitle", type: "text",
            offsetX: 16, offsetY: 12, width: 288, height: 20,
            text: "Card Title", textColor: "card.foreground",
            fontSize: 16, fontWeight: 600, textAlign: "left", verticalAlign: "top",
          },
          {
            name: "CardDescription", type: "text",
            offsetX: 16, offsetY: 34, width: 288, height: 16,
            text: "Card description goes here.", textColor: "card.muted.foreground",
            fontSize: 12, textAlign: "left", verticalAlign: "top",
          },
        ],
      },
      {
        name: "Separator", type: "rectangle",
        offsetX: 0, offsetY: 56, width: 320, height: 1,
        fill: "card.border",
      },
      {
        name: "CardContent", type: "frame",
        offsetX: 0, offsetY: 57, width: 320, height: 103,
        children: [
          {
            name: "ContentText", type: "text",
            offsetX: 16, offsetY: 12, width: 288, height: 20,
            text: "Card content goes here.", textColor: "card.muted.foreground",
            fontSize: 12, textAlign: "left", verticalAlign: "top",
          },
        ],
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/card",
      componentName: "Card",
      additionalImports: ["CardHeader", "CardTitle", "CardDescription", "CardContent", "CardFooter"],
      wrapper: "<Card><CardHeader><CardTitle /><CardDescription /></CardHeader><CardContent>{children}</CardContent></Card>",
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Card",
      componentName: "Card",
      additionalImports: ["@mui/material/CardHeader", "@mui/material/CardContent", "@mui/material/CardActions"],
    },
  },
};
