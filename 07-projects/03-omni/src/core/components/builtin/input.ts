import type { ComponentBlueprint } from "../types";

export const inputBlueprint: ComponentBlueprint = {
  id: "input",
  name: "Input",
  category: "input",
  description: "A single-line text input field",
  icon: "input/text",
  tags: ["input", "text", "field", "form", "textbox"],

  props: [
    { name: "placeholder", type: "string", label: "Placeholder", defaultValue: "Enter text\u2026", affectsCanvas: true },
    { name: "type", type: "enum", label: "Type", defaultValue: "text", options: [
      { value: "text", label: "Text" },
      { value: "email", label: "Email" },
      { value: "password", label: "Password" },
      { value: "number", label: "Number" },
      { value: "url", label: "URL" },
    ]},
    { name: "disabled", type: "boolean", label: "Disabled", defaultValue: false },
    { name: "required", type: "boolean", label: "Required", defaultValue: false },
  ],

  events: [
    { name: "onChange", label: "Change", description: "Fired when the input value changes", payloadType: "string" },
    { name: "onFocus", label: "Focus", description: "Fired when the input receives focus" },
    { name: "onBlur", label: "Blur", description: "Fired when the input loses focus" },
  ],

  tokenBindings: {
    background: "input.background",
    foreground: "input.foreground",
    placeholder: "input.placeholder",
    border: "input.border",
    radius: "input.radius",
  },

  canvasTemplate: {
    type: "frame",
    width: 240,
    height: 36,
    fill: "input.background",
    stroke: "input.border",
    strokeWidth: 1,
    cornerRadius: 6,
    children: [
      {
        name: "Placeholder", type: "text",
        offsetX: 12, offsetY: 0, width: 216, height: 36,
        text: "Enter text\u2026", textColor: "input.placeholder",
        fontSize: 14, textAlign: "left", verticalAlign: "middle",
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/input",
      componentName: "Input",
      propMappings: { placeholder: "placeholder", type: "type", disabled: "disabled" },
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/TextField",
      componentName: "TextField",
      propMappings: { placeholder: "placeholder", type: "type", disabled: "disabled", variant: "variant" },
    },
  },
};
