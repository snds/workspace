import type { ComponentBlueprint } from "../types";

export const alertBlueprint: ComponentBlueprint = {
  id: "alert",
  name: "Alert",
  category: "feedback",
  description: "An inline alert message for important information",
  icon: "feedback/alert",
  tags: ["alert", "warning", "info", "error", "notice", "banner"],

  props: [
    { name: "title", type: "string", label: "Title", defaultValue: "Heads up!", affectsCanvas: true },
    { name: "description", type: "string", label: "Description", defaultValue: "You can add components using the CLI.", affectsCanvas: true },
    { name: "variant", type: "enum", label: "Variant", defaultValue: "default", options: [
      { value: "default", label: "Default" },
      { value: "destructive", label: "Destructive" },
    ]},
  ],

  variants: [
    {
      id: "destructive", name: "Destructive",
      propOverrides: { variant: "destructive" },
      tokenOverrides: { border: "alert.destructive.border", foreground: "alert.destructive.foreground" },
      canvasOverrides: { stroke: "destructive.border" },
    },
  ],

  tokenBindings: {
    background: "alert.background",
    foreground: "alert.foreground",
    mutedForeground: "alert.muted.foreground",
    border: "alert.border",
  },

  canvasTemplate: {
    type: "frame",
    width: 320,
    height: 72,
    fill: "alert.background",
    stroke: "alert.border",
    strokeWidth: 1,
    cornerRadius: 8,
    children: [
      {
        name: "AlertTitle", type: "text",
        offsetX: 16, offsetY: 14, width: 288, height: 20,
        text: "Heads up!", textColor: "alert.foreground",
        fontSize: 14, fontWeight: 500, textAlign: "left", verticalAlign: "top",
      },
      {
        name: "AlertDescription", type: "text",
        offsetX: 16, offsetY: 38, width: 288, height: 20,
        text: "You can add components using the CLI.", textColor: "alert.muted.foreground",
        fontSize: 12, textAlign: "left", verticalAlign: "top",
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/alert",
      componentName: "Alert",
      propMappings: { variant: "variant" },
      additionalImports: ["AlertTitle", "AlertDescription"],
      wrapper: "<Alert><AlertTitle /><AlertDescription /></Alert>",
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Alert",
      componentName: "Alert",
      propMappings: { variant: "severity", title: "title", description: "children" },
      additionalImports: ["@mui/material/AlertTitle"],
    },
  },
};
