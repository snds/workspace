import type { ComponentBlueprint } from "../types";

export const buttonBlueprint: ComponentBlueprint = {
  id: "button",
  name: "Button",
  category: "action",
  description: "A clickable button for triggering actions",
  icon: "action/click",
  tags: ["button", "action", "cta", "submit"],

  props: [
    { name: "label", type: "string", label: "Label", defaultValue: "Button", affectsCanvas: true },
    {
      name: "variant", type: "enum", label: "Variant", defaultValue: "default",
      options: [
        { value: "default", label: "Default" },
        { value: "destructive", label: "Destructive" },
        { value: "outline", label: "Outline" },
        { value: "secondary", label: "Secondary" },
        { value: "ghost", label: "Ghost" },
        { value: "link", label: "Link" },
      ],
    },
    {
      name: "size", type: "enum", label: "Size", defaultValue: "default",
      options: [
        { value: "sm", label: "Small" },
        { value: "default", label: "Default" },
        { value: "lg", label: "Large" },
        { value: "icon", label: "Icon" },
      ],
    },
    { name: "disabled", type: "boolean", label: "Disabled", defaultValue: false },
    { name: "icon", type: "icon", label: "Icon" },
  ],

  slots: [
    { name: "default", label: "Content", description: "Button label or child elements" },
  ],

  events: [
    { name: "onClick", label: "Click", description: "Fired when the button is clicked" },
  ],

  variants: [
    {
      id: "destructive", name: "Destructive",
      propOverrides: { variant: "destructive" },
      tokenOverrides: { background: "button.destructive.background", foreground: "button.destructive.foreground" },
      canvasOverrides: { fill: "destructive.background" },
    },
    {
      id: "outline", name: "Outline",
      propOverrides: { variant: "outline" },
      tokenOverrides: { background: "button.outline.background", foreground: "button.outline.foreground" },
      canvasOverrides: { fill: "surface.0", stroke: "border.default", strokeWidth: 1 },
    },
    {
      id: "secondary", name: "Secondary",
      propOverrides: { variant: "secondary" },
      tokenOverrides: { background: "button.secondary.background", foreground: "button.secondary.foreground" },
      canvasOverrides: { fill: "surface.subtle" },
    },
    {
      id: "ghost", name: "Ghost",
      propOverrides: { variant: "ghost" },
      tokenOverrides: { background: "button.ghost.background", foreground: "button.ghost.foreground" },
    },
    {
      id: "link", name: "Link",
      propOverrides: { variant: "link" },
      tokenOverrides: { background: "button.link.background", foreground: "button.link.foreground" },
    },
  ],

  tokenBindings: {
    background: "button.background",
    foreground: "button.foreground",
    border: "button.border",
    radius: "button.radius",
  },

  canvasTemplate: {
    type: "frame",
    width: 100,
    height: 36,
    fill: "button.background",
    cornerRadius: 6,
    children: [
      {
        name: "Label", type: "text",
        offsetX: 0, offsetY: 0, width: 100, height: 36,
        text: "Button", textColor: "button.foreground",
        fontSize: 14, fontWeight: 500, textAlign: "center", verticalAlign: "middle",
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/button",
      componentName: "Button",
      propMappings: { label: "children", variant: "variant", size: "size", disabled: "disabled" },
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Button",
      componentName: "Button",
      propMappings: { label: "children", variant: "variant", size: "size", disabled: "disabled" },
    },
  },
};
