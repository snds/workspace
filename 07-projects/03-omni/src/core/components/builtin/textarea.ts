import type { ComponentBlueprint } from "../types";

export const textareaBlueprint: ComponentBlueprint = {
  id: "textarea",
  name: "Textarea",
  category: "input",
  description: "A multi-line text input area",
  icon: "input/textarea",
  tags: ["textarea", "text", "multiline", "form", "editor"],

  props: [
    { name: "placeholder", type: "string", label: "Placeholder", defaultValue: "Type your message\u2026", affectsCanvas: true },
    { name: "rows", type: "number", label: "Rows", defaultValue: 4 },
    { name: "disabled", type: "boolean", label: "Disabled", defaultValue: false },
    { name: "required", type: "boolean", label: "Required", defaultValue: false },
  ],

  events: [
    { name: "onChange", label: "Change", description: "Fired when the textarea value changes", payloadType: "string" },
  ],

  tokenBindings: {
    background: "textarea.background",
    foreground: "textarea.foreground",
    placeholder: "textarea.placeholder",
    border: "textarea.border",
    radius: "textarea.radius",
  },

  canvasTemplate: {
    type: "frame",
    width: 240,
    height: 80,
    fill: "textarea.background",
    stroke: "textarea.border",
    strokeWidth: 1,
    cornerRadius: 6,
    children: [
      {
        name: "Placeholder", type: "text",
        offsetX: 12, offsetY: 10, width: 216, height: 20,
        text: "Type your message\u2026", textColor: "textarea.placeholder",
        fontSize: 14, textAlign: "left", verticalAlign: "top",
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/textarea",
      componentName: "Textarea",
      propMappings: { placeholder: "placeholder", rows: "rows", disabled: "disabled" },
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/TextField",
      componentName: "TextField",
      propMappings: { placeholder: "placeholder", rows: "rows", disabled: "disabled" },
      wrapper: '<TextField multiline />',
    },
  },
};
