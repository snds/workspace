import type { ComponentBlueprint } from "../types";

export const switchBlueprint: ComponentBlueprint = {
  id: "switch",
  name: "Switch",
  category: "input",
  description: "A toggle switch for binary settings",
  icon: "input/switch",
  tags: ["switch", "toggle", "on", "off", "boolean", "form"],

  props: [
    { name: "label", type: "string", label: "Label", defaultValue: "Enable feature", affectsCanvas: true },
    { name: "checked", type: "boolean", label: "Checked", defaultValue: true, affectsCanvas: true },
    { name: "disabled", type: "boolean", label: "Disabled", defaultValue: false },
  ],

  events: [
    { name: "onCheckedChange", label: "Checked Change", description: "Fired when switch state changes", payloadType: "boolean" },
  ],

  tokenBindings: {
    trackBackground: "switch.track.background",
    thumbBackground: "switch.thumb.background",
    label: "switch.label",
  },

  canvasTemplate: {
    type: "frame",
    width: 160,
    height: 28,
    children: [
      {
        name: "SwitchTrack", type: "frame",
        offsetX: 0, offsetY: 4, width: 36, height: 20,
        fill: "switch.track.background", cornerRadius: 9999,
      },
      {
        name: "SwitchThumb", type: "frame",
        offsetX: 18, offsetY: 6, width: 16, height: 16,
        fill: "switch.thumb.background", cornerRadius: 9999,
      },
      {
        name: "Label", type: "text",
        offsetX: 44, offsetY: 0, width: 116, height: 28,
        text: "Enable feature", textColor: "switch.label",
        fontSize: 13, textAlign: "left", verticalAlign: "middle",
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/switch",
      componentName: "Switch",
      propMappings: { checked: "checked", disabled: "disabled" },
      additionalImports: ["@/components/ui/label"],
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Switch",
      componentName: "Switch",
      propMappings: { checked: "checked", disabled: "disabled", label: "label" },
      additionalImports: ["@mui/material/FormControlLabel"],
      wrapper: "<FormControlLabel control={<Switch />} />",
    },
  },
};
