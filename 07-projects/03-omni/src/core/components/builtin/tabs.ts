import type { ComponentBlueprint } from "../types";

export const tabsBlueprint: ComponentBlueprint = {
  id: "tabs",
  name: "Tabs",
  category: "navigation",
  description: "Tabbed navigation for switching between content panels",
  icon: "navigation/tabs",
  tags: ["tabs", "navigation", "panel", "switch", "tabbed"],

  props: [
    { name: "defaultValue", type: "string", label: "Default Tab", defaultValue: "tab1" },
    { name: "tabCount", type: "number", label: "Tab Count", defaultValue: 3, affectsCanvas: true },
  ],

  slots: [
    { name: "tabs", label: "Tab Panels", description: "Content for each tab" },
  ],

  events: [
    { name: "onValueChange", label: "Tab Change", description: "Fired when active tab changes", payloadType: "string" },
  ],

  tokenBindings: {
    listBackground: "tabs.list.background",
    triggerBackground: "tabs.trigger.background",
    triggerForeground: "tabs.trigger.foreground",
    activeForeground: "tabs.trigger.active.foreground",
    contentForeground: "tabs.content.foreground",
  },

  canvasTemplate: {
    type: "frame",
    width: 320,
    height: 120,
    children: [
      {
        name: "TabsList", type: "frame",
        offsetX: 0, offsetY: 0, width: 320, height: 36,
        fill: "tabs.list.background", cornerRadius: 6,
        children: [
          {
            name: "TabsTrigger", type: "frame",
            offsetX: 4, offsetY: 4, width: 100, height: 28,
            fill: "tabs.trigger.background", cornerRadius: 4,
            children: [
              {
                name: "TabLabel", type: "text",
                offsetX: 0, offsetY: 0, width: 100, height: 28,
                text: "Tab 1", textColor: "tabs.trigger.active.foreground",
                fontSize: 12, fontWeight: 500, textAlign: "center", verticalAlign: "middle",
              },
            ],
          },
          {
            name: "TabsTrigger", type: "frame",
            offsetX: 108, offsetY: 4, width: 100, height: 28,
            cornerRadius: 4,
            children: [
              {
                name: "TabLabel", type: "text",
                offsetX: 0, offsetY: 0, width: 100, height: 28,
                text: "Tab 2", textColor: "tabs.trigger.foreground",
                fontSize: 12, textAlign: "center", verticalAlign: "middle",
              },
            ],
          },
          {
            name: "TabsTrigger", type: "frame",
            offsetX: 212, offsetY: 4, width: 100, height: 28,
            cornerRadius: 4,
            children: [
              {
                name: "TabLabel", type: "text",
                offsetX: 0, offsetY: 0, width: 100, height: 28,
                text: "Tab 3", textColor: "tabs.trigger.foreground",
                fontSize: 12, textAlign: "center", verticalAlign: "middle",
              },
            ],
          },
        ],
      },
      {
        name: "TabsContent", type: "frame",
        offsetX: 0, offsetY: 44, width: 320, height: 76,
        children: [
          {
            name: "Content", type: "text",
            offsetX: 4, offsetY: 8, width: 312, height: 20,
            text: "Tab content here.", textColor: "tabs.content.foreground",
            fontSize: 12, textAlign: "left", verticalAlign: "top",
          },
        ],
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/tabs",
      componentName: "Tabs",
      propMappings: { defaultValue: "defaultValue" },
      additionalImports: ["TabsList", "TabsTrigger", "TabsContent"],
      wrapper: "<Tabs><TabsList><TabsTrigger /></TabsList><TabsContent>{children}</TabsContent></Tabs>",
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Tabs",
      componentName: "Tabs",
      propMappings: { defaultValue: "value" },
      additionalImports: ["@mui/material/Tab", "@mui/material/Box"],
    },
  },
};
