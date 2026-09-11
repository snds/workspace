import type { ComponentBlueprint } from "../types";

export const dialogBlueprint: ComponentBlueprint = {
  id: "dialog",
  name: "Dialog",
  category: "overlay",
  description: "A modal dialog overlay for focused interactions",
  icon: "overlay/dialog",
  tags: ["dialog", "modal", "popup", "overlay", "window"],

  props: [
    { name: "title", type: "string", label: "Title", defaultValue: "Dialog Title", affectsCanvas: true },
    { name: "description", type: "string", label: "Description", defaultValue: "Dialog description text goes here.", affectsCanvas: true },
    { name: "open", type: "boolean", label: "Open", defaultValue: false },
  ],

  slots: [
    { name: "content", label: "Content", description: "Dialog body content" },
    { name: "footer", label: "Footer", description: "Dialog footer with action buttons" },
  ],

  events: [
    { name: "onOpenChange", label: "Open Change", description: "Fired when dialog open state changes", payloadType: "boolean" },
  ],

  tokenBindings: {
    background: "dialog.background",
    foreground: "dialog.foreground",
    mutedForeground: "dialog.muted.foreground",
    border: "dialog.border",
  },

  canvasTemplate: {
    type: "frame",
    width: 400,
    height: 240,
    fill: "dialog.background",
    stroke: "dialog.border",
    strokeWidth: 1,
    cornerRadius: 8,
    children: [
      {
        name: "DialogHeader", type: "frame",
        offsetX: 0, offsetY: 0, width: 400, height: 64,
        children: [
          {
            name: "DialogTitle", type: "text",
            offsetX: 16, offsetY: 16, width: 368, height: 24,
            text: "Dialog Title", textColor: "dialog.foreground",
            fontSize: 18, fontWeight: 600, textAlign: "left", verticalAlign: "top",
          },
          {
            name: "DialogDescription", type: "text",
            offsetX: 16, offsetY: 44, width: 368, height: 16,
            text: "Dialog description text goes here.", textColor: "dialog.muted.foreground",
            fontSize: 13, textAlign: "left", verticalAlign: "top",
          },
        ],
      },
      {
        name: "Divider", type: "rectangle",
        offsetX: 0, offsetY: 64, width: 400, height: 1,
        fill: "dialog.border",
      },
      {
        name: "DialogContent", type: "frame",
        offsetX: 0, offsetY: 65, width: 400, height: 104,
        children: [
          {
            name: "ContentText", type: "text",
            offsetX: 16, offsetY: 12, width: 368, height: 20,
            text: "Add your dialog content here.", textColor: "dialog.muted.foreground",
            fontSize: 13, textAlign: "left", verticalAlign: "top",
          },
        ],
      },
      {
        name: "Divider", type: "rectangle",
        offsetX: 0, offsetY: 169, width: 400, height: 1,
        fill: "dialog.border",
      },
      {
        name: "DialogFooter", type: "frame",
        offsetX: 0, offsetY: 170, width: 400, height: 70,
        children: [
          {
            name: "CancelButton", type: "frame",
            offsetX: 212, offsetY: 16, width: 80, height: 36,
            fill: "dialog.background", stroke: "dialog.border", strokeWidth: 1, cornerRadius: 6,
            children: [
              {
                name: "Label", type: "text",
                offsetX: 0, offsetY: 0, width: 80, height: 36,
                text: "Cancel", textColor: "dialog.foreground",
                fontSize: 13, fontWeight: 500, textAlign: "center", verticalAlign: "middle",
              },
            ],
          },
          {
            name: "ActionButton", type: "frame",
            offsetX: 300, offsetY: 16, width: 84, height: 36,
            fill: "button.background", cornerRadius: 6,
            children: [
              {
                name: "Label", type: "text",
                offsetX: 0, offsetY: 0, width: 84, height: 36,
                text: "Continue", textColor: "button.foreground",
                fontSize: 13, fontWeight: 500, textAlign: "center", verticalAlign: "middle",
              },
            ],
          },
        ],
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/dialog",
      componentName: "Dialog",
      propMappings: { open: "open", title: "title", description: "description" },
      additionalImports: ["DialogTrigger", "DialogContent", "DialogHeader", "DialogTitle", "DialogDescription", "DialogFooter"],
      wrapper: "<Dialog><DialogContent><DialogHeader><DialogTitle /><DialogDescription /></DialogHeader>{children}<DialogFooter /></DialogContent></Dialog>",
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Dialog",
      componentName: "Dialog",
      propMappings: { open: "open" },
      additionalImports: ["@mui/material/DialogTitle", "@mui/material/DialogContent", "@mui/material/DialogActions"],
    },
  },
};
