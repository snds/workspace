import type { ComponentBlueprint } from "../types";

export const dropdownBlueprint: ComponentBlueprint = {
  id: "dropdown",
  name: "Dropdown Menu",
  category: "overlay",
  description: "A dropdown menu with selectable actions",
  icon: "overlay/dropdown",
  tags: ["dropdown", "menu", "context", "actions", "popover"],

  props: [
    { name: "triggerLabel", type: "string", label: "Trigger Label", defaultValue: "Options", affectsCanvas: true },
  ],

  slots: [
    { name: "items", label: "Menu Items", description: "Dropdown menu item entries" },
  ],

  events: [
    { name: "onSelect", label: "Select", description: "Fired when a menu item is selected", payloadType: "string" },
  ],

  tokenBindings: {
    background: "dropdown.background",
    foreground: "dropdown.foreground",
    mutedForeground: "dropdown.muted.foreground",
    border: "dropdown.border",
    destructive: "dropdown.destructive",
  },

  canvasTemplate: {
    type: "frame",
    width: 160,
    height: 180,
    children: [
      {
        name: "Trigger", type: "frame",
        offsetX: 0, offsetY: 0, width: 160, height: 36,
        fill: "dropdown.background", stroke: "dropdown.border", strokeWidth: 1, cornerRadius: 6,
        children: [
          {
            name: "Label", type: "text",
            offsetX: 12, offsetY: 0, width: 120, height: 36,
            text: "Options", textColor: "dropdown.foreground",
            fontSize: 13, textAlign: "left", verticalAlign: "middle",
          },
          {
            name: "Chevron", type: "text",
            offsetX: 136, offsetY: 0, width: 16, height: 36,
            text: "\u25BE", textColor: "dropdown.muted.foreground",
            fontSize: 12, textAlign: "center", verticalAlign: "middle",
          },
        ],
      },
      {
        name: "MenuPanel", type: "frame",
        offsetX: 0, offsetY: 44, width: 160, height: 136,
        fill: "dropdown.background", stroke: "dropdown.border", strokeWidth: 1, cornerRadius: 6,
        children: [
          {
            name: "MenuItem", type: "text",
            offsetX: 8, offsetY: 0, width: 144, height: 32,
            text: "Edit", textColor: "dropdown.foreground",
            fontSize: 13, textAlign: "left", verticalAlign: "middle",
          },
          {
            name: "Separator", type: "rectangle",
            offsetX: 8, offsetY: 32, width: 144, height: 1,
            fill: "dropdown.border",
          },
          {
            name: "MenuItem", type: "text",
            offsetX: 8, offsetY: 33, width: 144, height: 32,
            text: "Duplicate", textColor: "dropdown.foreground",
            fontSize: 13, textAlign: "left", verticalAlign: "middle",
          },
          {
            name: "MenuItem", type: "text",
            offsetX: 8, offsetY: 65, width: 144, height: 32,
            text: "Archive", textColor: "dropdown.foreground",
            fontSize: 13, textAlign: "left", verticalAlign: "middle",
          },
          {
            name: "Separator", type: "rectangle",
            offsetX: 8, offsetY: 97, width: 144, height: 1,
            fill: "dropdown.border",
          },
          {
            name: "MenuItem", type: "text",
            offsetX: 8, offsetY: 100, width: 144, height: 32,
            text: "Delete", textColor: "dropdown.destructive",
            fontSize: 13, textAlign: "left", verticalAlign: "middle",
          },
        ],
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/dropdown-menu",
      componentName: "DropdownMenu",
      additionalImports: ["DropdownMenuTrigger", "DropdownMenuContent", "DropdownMenuItem", "DropdownMenuSeparator"],
      wrapper: "<DropdownMenu><DropdownMenuTrigger /><DropdownMenuContent><DropdownMenuItem /><DropdownMenuSeparator /></DropdownMenuContent></DropdownMenu>",
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Menu",
      componentName: "Menu",
      additionalImports: ["@mui/material/MenuItem", "@mui/material/Divider", "@mui/material/Button"],
    },
  },
};
