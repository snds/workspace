import type { ComponentBlueprint } from "../types";

export const breadcrumbBlueprint: ComponentBlueprint = {
  id: "breadcrumb",
  name: "Breadcrumb",
  category: "navigation",
  description: "A breadcrumb navigation showing the current page hierarchy",
  icon: "navigation/breadcrumb",
  tags: ["breadcrumb", "navigation", "path", "trail", "hierarchy"],

  props: [
    { name: "separator", type: "string", label: "Separator", defaultValue: "/", affectsCanvas: true },
  ],

  slots: [
    { name: "items", label: "Items", description: "Breadcrumb navigation items" },
  ],

  tokenBindings: {
    foreground: "breadcrumb.foreground",
    mutedForeground: "breadcrumb.muted.foreground",
    separatorColor: "breadcrumb.separator",
    activeForeground: "breadcrumb.active.foreground",
  },

  canvasTemplate: {
    type: "frame",
    width: 240,
    height: 28,
    children: [
      {
        name: "Root", type: "text",
        offsetX: 0, offsetY: 0, width: 40, height: 28,
        text: "Home", textColor: "breadcrumb.muted.foreground",
        fontSize: 12, textAlign: "left", verticalAlign: "middle",
      },
      {
        name: "Sep1", type: "text",
        offsetX: 44, offsetY: 0, width: 12, height: 28,
        text: "/", textColor: "breadcrumb.separator",
        fontSize: 12, textAlign: "center", verticalAlign: "middle",
      },
      {
        name: "Mid", type: "text",
        offsetX: 60, offsetY: 0, width: 80, height: 28,
        text: "Components", textColor: "breadcrumb.muted.foreground",
        fontSize: 12, textAlign: "left", verticalAlign: "middle",
      },
      {
        name: "Sep2", type: "text",
        offsetX: 144, offsetY: 0, width: 12, height: 28,
        text: "/", textColor: "breadcrumb.separator",
        fontSize: 12, textAlign: "center", verticalAlign: "middle",
      },
      {
        name: "Current", type: "text",
        offsetX: 160, offsetY: 0, width: 80, height: 28,
        text: "Button", textColor: "breadcrumb.active.foreground",
        fontSize: 12, fontWeight: 500, textAlign: "left", verticalAlign: "middle",
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/breadcrumb",
      componentName: "Breadcrumb",
      additionalImports: ["BreadcrumbList", "BreadcrumbItem", "BreadcrumbLink", "BreadcrumbPage", "BreadcrumbSeparator"],
      wrapper: "<Breadcrumb><BreadcrumbList><BreadcrumbItem><BreadcrumbLink /></BreadcrumbItem><BreadcrumbSeparator /><BreadcrumbItem><BreadcrumbPage /></BreadcrumbItem></BreadcrumbList></Breadcrumb>",
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Breadcrumbs",
      componentName: "Breadcrumbs",
      propMappings: { separator: "separator" },
      additionalImports: ["@mui/material/Link", "@mui/material/Typography"],
    },
  },
};
