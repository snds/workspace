import type { ComponentBlueprint } from "../types";

export const sheetBlueprint: ComponentBlueprint = {
  id: "sheet",
  name: "Sheet",
  category: "overlay",
  description: "A slide-out panel from the edge of the screen",
  icon: "overlay/sheet",
  tags: ["sheet", "drawer", "panel", "sidebar", "slide"],

  props: [
    { name: "title", type: "string", label: "Title", defaultValue: "Sheet Title", affectsCanvas: true },
    { name: "description", type: "string", label: "Description", defaultValue: "Sheet description goes here.", affectsCanvas: true },
    { name: "side", type: "enum", label: "Side", defaultValue: "right", options: [
      { value: "top", label: "Top" },
      { value: "right", label: "Right" },
      { value: "bottom", label: "Bottom" },
      { value: "left", label: "Left" },
    ]},
    { name: "open", type: "boolean", label: "Open", defaultValue: false },
  ],

  slots: [
    { name: "content", label: "Content", description: "Sheet body content" },
    { name: "footer", label: "Footer", description: "Sheet footer" },
  ],

  events: [
    { name: "onOpenChange", label: "Open Change", description: "Fired when sheet open state changes", payloadType: "boolean" },
  ],

  tokenBindings: {
    background: "sheet.background",
    foreground: "sheet.foreground",
    mutedForeground: "sheet.muted.foreground",
    border: "sheet.border",
  },

  canvasTemplate: {
    type: "frame",
    width: 320,
    height: 200,
    fill: "sheet.background",
    stroke: "sheet.border",
    strokeWidth: 1,
    cornerRadius: 8,
    children: [
      {
        name: "SheetHeader", type: "frame",
        offsetX: 0, offsetY: 0, width: 320, height: 56,
        children: [
          {
            name: "SheetTitle", type: "text",
            offsetX: 16, offsetY: 12, width: 288, height: 20,
            text: "Sheet Title", textColor: "sheet.foreground",
            fontSize: 16, fontWeight: 600, textAlign: "left", verticalAlign: "top",
          },
          {
            name: "SheetDescription", type: "text",
            offsetX: 16, offsetY: 34, width: 288, height: 16,
            text: "Sheet description goes here.", textColor: "sheet.muted.foreground",
            fontSize: 12, textAlign: "left", verticalAlign: "top",
          },
        ],
      },
      {
        name: "Divider", type: "rectangle",
        offsetX: 0, offsetY: 56, width: 320, height: 1,
        fill: "sheet.border",
      },
      {
        name: "SheetContent", type: "frame",
        offsetX: 0, offsetY: 57, width: 320, height: 143,
        children: [
          {
            name: "ContentText", type: "text",
            offsetX: 16, offsetY: 12, width: 288, height: 20,
            text: "Sheet content goes here.", textColor: "sheet.muted.foreground",
            fontSize: 12, textAlign: "left", verticalAlign: "top",
          },
        ],
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/sheet",
      componentName: "Sheet",
      propMappings: { open: "open", side: "side" },
      additionalImports: ["SheetTrigger", "SheetContent", "SheetHeader", "SheetTitle", "SheetDescription"],
      wrapper: "<Sheet><SheetContent><SheetHeader><SheetTitle /><SheetDescription /></SheetHeader>{children}</SheetContent></Sheet>",
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Drawer",
      componentName: "Drawer",
      propMappings: { open: "open", side: "anchor" },
    },
  },
};
