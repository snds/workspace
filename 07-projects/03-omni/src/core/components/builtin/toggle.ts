import type { ComponentBlueprint } from "../types";

export const toggleBlueprint: ComponentBlueprint = {
  id: "toggle",
  name: "Toggle",
  category: "action",
  description: "A two-state toggle button",
  icon: "action/toggle",
  tags: ["toggle", "button", "switch", "pressed", "active"],

  props: [
    { name: "label", type: "string", label: "Label", defaultValue: "B", affectsCanvas: true },
    { name: "pressed", type: "boolean", label: "Pressed", defaultValue: false, affectsCanvas: true },
    { name: "variant", type: "enum", label: "Variant", defaultValue: "default", options: [
      { value: "default", label: "Default" },
      { value: "outline", label: "Outline" },
    ]},
    { name: "size", type: "enum", label: "Size", defaultValue: "default", options: [
      { value: "sm", label: "Small" },
      { value: "default", label: "Default" },
      { value: "lg", label: "Large" },
    ]},
    { name: "disabled", type: "boolean", label: "Disabled", defaultValue: false },
  ],

  events: [
    { name: "onPressedChange", label: "Pressed Change", description: "Fired when toggle state changes", payloadType: "boolean" },
  ],

  tokenBindings: {
    background: "toggle.background",
    foreground: "toggle.foreground",
    activeBackground: "toggle.active.background",
    activeForeground: "toggle.active.foreground",
    border: "toggle.border",
  },

  canvasTemplate: {
    type: "frame",
    width: 36,
    height: 36,
    fill: "toggle.background",
    stroke: "toggle.border",
    strokeWidth: 1,
    cornerRadius: 6,
    children: [
      {
        name: "Label", type: "text",
        offsetX: 0, offsetY: 0, width: 36, height: 36,
        text: "B", textColor: "toggle.foreground",
        fontSize: 14, fontWeight: 700, textAlign: "center", verticalAlign: "middle",
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/toggle",
      componentName: "Toggle",
      propMappings: { pressed: "pressed", variant: "variant", size: "size", disabled: "disabled" },
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/ToggleButton",
      componentName: "ToggleButton",
      propMappings: { pressed: "selected", label: "children", size: "size", disabled: "disabled" },
    },
  },
};
