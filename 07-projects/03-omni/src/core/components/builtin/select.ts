import type { ComponentBlueprint } from "../types";

export const selectBlueprint: ComponentBlueprint = {
  id: "select",
  name: "Select",
  category: "input",
  description: "A dropdown select menu for choosing from options",
  icon: "input/select",
  tags: ["select", "dropdown", "picker", "form", "combobox"],

  props: [
    { name: "placeholder", type: "string", label: "Placeholder", defaultValue: "Select option\u2026", affectsCanvas: true },
    { name: "disabled", type: "boolean", label: "Disabled", defaultValue: false },
    { name: "required", type: "boolean", label: "Required", defaultValue: false },
  ],

  slots: [
    { name: "options", label: "Options", description: "Select option items" },
  ],

  events: [
    { name: "onValueChange", label: "Value Change", description: "Fired when selection changes", payloadType: "string" },
  ],

  tokenBindings: {
    background: "select.background",
    foreground: "select.foreground",
    placeholder: "select.placeholder",
    border: "select.border",
    chevron: "select.chevron",
  },

  canvasTemplate: {
    type: "frame",
    width: 200,
    height: 36,
    fill: "select.background",
    stroke: "select.border",
    strokeWidth: 1,
    cornerRadius: 6,
    children: [
      {
        name: "Placeholder", type: "text",
        offsetX: 12, offsetY: 0, width: 160, height: 36,
        text: "Select option\u2026", textColor: "select.placeholder",
        fontSize: 14, textAlign: "left", verticalAlign: "middle",
      },
      {
        name: "ChevronIcon", type: "text",
        offsetX: 176, offsetY: 0, width: 16, height: 36,
        text: "\u2304", textColor: "select.chevron",
        fontSize: 14, textAlign: "center", verticalAlign: "middle",
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/select",
      componentName: "Select",
      propMappings: { placeholder: "placeholder", disabled: "disabled" },
      additionalImports: ["SelectTrigger", "SelectContent", "SelectItem", "SelectValue"],
      wrapper: "<Select><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>{children}</SelectContent></Select>",
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Select",
      componentName: "Select",
      propMappings: { placeholder: "placeholder", disabled: "disabled" },
      additionalImports: ["@mui/material/MenuItem", "@mui/material/FormControl", "@mui/material/InputLabel"],
    },
  },
};
