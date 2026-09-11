import type { ComponentBlueprint } from "../types";

export const checkboxBlueprint: ComponentBlueprint = {
  id: "checkbox",
  name: "Checkbox",
  category: "input",
  description: "A toggle checkbox with optional label",
  icon: "input/checkbox",
  tags: ["checkbox", "check", "toggle", "form", "boolean"],

  props: [
    { name: "label", type: "string", label: "Label", defaultValue: "Accept terms", affectsCanvas: true },
    { name: "checked", type: "boolean", label: "Checked", defaultValue: true, affectsCanvas: true },
    { name: "disabled", type: "boolean", label: "Disabled", defaultValue: false },
  ],

  events: [
    { name: "onCheckedChange", label: "Checked Change", description: "Fired when checked state changes", payloadType: "boolean" },
  ],

  tokenBindings: {
    background: "checkbox.background",
    foreground: "checkbox.foreground",
    border: "checkbox.border",
    label: "checkbox.label",
  },

  canvasTemplate: {
    type: "frame",
    width: 140,
    height: 24,
    children: [
      {
        name: "CheckboxControl", type: "frame",
        offsetX: 0, offsetY: 2, width: 20, height: 20,
        fill: "checkbox.background", cornerRadius: 4,
      },
      {
        name: "Check", type: "text",
        offsetX: 0, offsetY: 2, width: 20, height: 20,
        text: "\u2713", textColor: "checkbox.foreground",
        fontSize: 12, fontWeight: 700, textAlign: "center", verticalAlign: "middle",
      },
      {
        name: "Label", type: "text",
        offsetX: 28, offsetY: 0, width: 112, height: 24,
        text: "Accept terms", textColor: "checkbox.label",
        fontSize: 13, textAlign: "left", verticalAlign: "middle",
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/checkbox",
      componentName: "Checkbox",
      propMappings: { checked: "checked", disabled: "disabled" },
      additionalImports: ["@/components/ui/label"],
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Checkbox",
      componentName: "Checkbox",
      propMappings: { checked: "checked", disabled: "disabled", label: "label" },
      additionalImports: ["@mui/material/FormControlLabel"],
      wrapper: "<FormControlLabel control={<Checkbox />} />",
    },
  },
};
