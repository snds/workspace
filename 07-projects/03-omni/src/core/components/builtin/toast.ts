import type { ComponentBlueprint } from "../types";

export const toastBlueprint: ComponentBlueprint = {
  id: "toast",
  name: "Toast",
  category: "feedback",
  description: "A brief notification message that appears temporarily",
  icon: "feedback/toast",
  tags: ["toast", "notification", "snackbar", "message", "sonner"],

  props: [
    { name: "title", type: "string", label: "Title", defaultValue: "Event created", affectsCanvas: true },
    { name: "description", type: "string", label: "Description", defaultValue: "Sunday, December 03 at 9:00 AM", affectsCanvas: true },
    { name: "variant", type: "enum", label: "Variant", defaultValue: "default", options: [
      { value: "default", label: "Default" },
      { value: "success", label: "Success" },
      { value: "error", label: "Error" },
      { value: "warning", label: "Warning" },
      { value: "info", label: "Info" },
    ]},
    { name: "duration", type: "number", label: "Duration (ms)", defaultValue: 5000 },
  ],

  events: [
    { name: "onDismiss", label: "Dismiss", description: "Fired when the toast is dismissed" },
    { name: "onAction", label: "Action", description: "Fired when the action button is clicked" },
  ],

  tokenBindings: {
    background: "toast.background",
    foreground: "toast.foreground",
    mutedForeground: "toast.muted.foreground",
    border: "toast.border",
  },

  canvasTemplate: {
    type: "frame",
    width: 300,
    height: 60,
    fill: "toast.background",
    stroke: "toast.border",
    strokeWidth: 1,
    cornerRadius: 8,
    children: [
      {
        name: "Title", type: "text",
        offsetX: 16, offsetY: 12, width: 268, height: 18,
        text: "Event created", textColor: "toast.foreground",
        fontSize: 13, fontWeight: 500, textAlign: "left", verticalAlign: "top",
      },
      {
        name: "Description", type: "text",
        offsetX: 16, offsetY: 34, width: 268, height: 16,
        text: "Sunday, December 03 at 9:00 AM", textColor: "toast.muted.foreground",
        fontSize: 11, textAlign: "left", verticalAlign: "top",
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "sonner",
      componentName: "toast",
      propMappings: { title: "message", description: "description", duration: "duration" },
      additionalImports: ["@/components/ui/sonner"],
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Snackbar",
      componentName: "Snackbar",
      propMappings: { title: "message", duration: "autoHideDuration" },
      additionalImports: ["@mui/material/Alert"],
    },
  },
};
