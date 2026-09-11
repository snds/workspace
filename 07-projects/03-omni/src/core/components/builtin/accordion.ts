import type { ComponentBlueprint } from "../types";

export const accordionBlueprint: ComponentBlueprint = {
  id: "accordion",
  name: "Accordion",
  category: "layout",
  description: "A vertically collapsible set of content sections",
  icon: "layout/accordion",
  tags: ["accordion", "collapse", "expand", "faq", "sections"],

  props: [
    { name: "type", type: "enum", label: "Type", defaultValue: "single", options: [
      { value: "single", label: "Single" },
      { value: "multiple", label: "Multiple" },
    ]},
    { name: "collapsible", type: "boolean", label: "Collapsible", defaultValue: true },
  ],

  slots: [
    { name: "items", label: "Items", description: "Accordion item panels" },
  ],

  events: [
    { name: "onValueChange", label: "Value Change", description: "Fired when expanded items change", payloadType: "string | string[]" },
  ],

  tokenBindings: {
    foreground: "accordion.foreground",
    mutedForeground: "accordion.muted.foreground",
    border: "accordion.border",
  },

  canvasTemplate: {
    type: "frame",
    width: 280,
    height: 120,
    children: [
      {
        name: "AccordionItem", type: "frame",
        offsetX: 0, offsetY: 0, width: 280, height: 48,
        children: [
          {
            name: "Label", type: "text",
            offsetX: 12, offsetY: 0, width: 240, height: 48,
            text: "Item 1", textColor: "accordion.foreground",
            fontSize: 14, fontWeight: 500, textAlign: "left", verticalAlign: "middle",
          },
          {
            name: "Icon", type: "text",
            offsetX: 256, offsetY: 0, width: 16, height: 48,
            text: "\u25BE", textColor: "accordion.muted.foreground",
            fontSize: 12, textAlign: "center", verticalAlign: "middle",
          },
        ],
      },
      {
        name: "Divider", type: "rectangle",
        offsetX: 0, offsetY: 48, width: 280, height: 1,
        fill: "accordion.border",
      },
      {
        name: "AccordionItem", type: "frame",
        offsetX: 0, offsetY: 49, width: 280, height: 48,
        children: [
          {
            name: "Label", type: "text",
            offsetX: 12, offsetY: 0, width: 240, height: 48,
            text: "Item 2", textColor: "accordion.foreground",
            fontSize: 14, textAlign: "left", verticalAlign: "middle",
          },
          {
            name: "Icon", type: "text",
            offsetX: 256, offsetY: 0, width: 16, height: 48,
            text: "\u25BE", textColor: "accordion.muted.foreground",
            fontSize: 12, textAlign: "center", verticalAlign: "middle",
          },
        ],
      },
      {
        name: "Divider", type: "rectangle",
        offsetX: 0, offsetY: 97, width: 280, height: 1,
        fill: "accordion.border",
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/accordion",
      componentName: "Accordion",
      propMappings: { type: "type", collapsible: "collapsible" },
      additionalImports: ["AccordionItem", "AccordionTrigger", "AccordionContent"],
      wrapper: "<Accordion><AccordionItem><AccordionTrigger /><AccordionContent>{children}</AccordionContent></AccordionItem></Accordion>",
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Accordion",
      componentName: "Accordion",
      additionalImports: ["@mui/material/AccordionSummary", "@mui/material/AccordionDetails"],
    },
  },
};
