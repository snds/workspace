import type { ComponentBlueprint } from "../types";

export const tableBlueprint: ComponentBlueprint = {
  id: "table",
  name: "Table",
  category: "display",
  description: "A data table with header and rows",
  icon: "display/table",
  tags: ["table", "data", "grid", "rows", "columns", "list"],

  props: [
    { name: "columns", type: "number", label: "Columns", defaultValue: 3 },
    { name: "rows", type: "number", label: "Rows", defaultValue: 3 },
  ],

  slots: [
    { name: "header", label: "Header", description: "Table header row" },
    { name: "body", label: "Body", description: "Table body rows" },
  ],

  tokenBindings: {
    background: "table.background",
    headerBackground: "table.header.background",
    foreground: "table.foreground",
    mutedForeground: "table.muted.foreground",
    border: "table.border",
  },

  canvasTemplate: {
    type: "frame",
    width: 400,
    height: 200,
    fill: "table.background",
    stroke: "table.border",
    strokeWidth: 1,
    cornerRadius: 8,
    children: [
      {
        name: "TableHeader", type: "frame",
        offsetX: 0, offsetY: 0, width: 400, height: 36,
        fill: "table.header.background", cornerRadius: 0,
        children: [
          {
            name: "Col1", type: "text",
            offsetX: 12, offsetY: 0, width: 120, height: 36,
            text: "Name", textColor: "table.foreground",
            fontSize: 12, fontWeight: 600, textAlign: "left", verticalAlign: "middle",
          },
          {
            name: "Col2", type: "text",
            offsetX: 144, offsetY: 0, width: 120, height: 36,
            text: "Status", textColor: "table.foreground",
            fontSize: 12, fontWeight: 600, textAlign: "left", verticalAlign: "middle",
          },
          {
            name: "Col3", type: "text",
            offsetX: 276, offsetY: 0, width: 112, height: 36,
            text: "Amount", textColor: "table.foreground",
            fontSize: 12, fontWeight: 600, textAlign: "right", verticalAlign: "middle",
          },
        ],
      },
      {
        name: "HeaderDivider", type: "rectangle",
        offsetX: 0, offsetY: 36, width: 400, height: 1,
        fill: "table.border",
      },
      {
        name: "TableRow", type: "frame",
        offsetX: 0, offsetY: 37, width: 400, height: 40,
        children: [
          {
            name: "Cell1", type: "text",
            offsetX: 12, offsetY: 0, width: 120, height: 40,
            text: "Alice Johnson", textColor: "table.foreground",
            fontSize: 12, textAlign: "left", verticalAlign: "middle",
          },
          {
            name: "Cell2", type: "text",
            offsetX: 144, offsetY: 0, width: 120, height: 40,
            text: "Active", textColor: "table.muted.foreground",
            fontSize: 12, textAlign: "left", verticalAlign: "middle",
          },
          {
            name: "Cell3", type: "text",
            offsetX: 276, offsetY: 0, width: 112, height: 40,
            text: "$250.00", textColor: "table.foreground",
            fontSize: 12, textAlign: "right", verticalAlign: "middle",
          },
        ],
      },
      {
        name: "Divider", type: "rectangle",
        offsetX: 0, offsetY: 77, width: 400, height: 1,
        fill: "table.border",
      },
      {
        name: "TableRow", type: "frame",
        offsetX: 0, offsetY: 78, width: 400, height: 40,
        children: [
          {
            name: "Cell1", type: "text",
            offsetX: 12, offsetY: 0, width: 120, height: 40,
            text: "Bob Smith", textColor: "table.foreground",
            fontSize: 12, textAlign: "left", verticalAlign: "middle",
          },
          {
            name: "Cell2", type: "text",
            offsetX: 144, offsetY: 0, width: 120, height: 40,
            text: "Inactive", textColor: "table.muted.foreground",
            fontSize: 12, textAlign: "left", verticalAlign: "middle",
          },
          {
            name: "Cell3", type: "text",
            offsetX: 276, offsetY: 0, width: 112, height: 40,
            text: "$150.00", textColor: "table.foreground",
            fontSize: 12, textAlign: "right", verticalAlign: "middle",
          },
        ],
      },
      {
        name: "Divider", type: "rectangle",
        offsetX: 0, offsetY: 118, width: 400, height: 1,
        fill: "table.border",
      },
      {
        name: "TableRow", type: "frame",
        offsetX: 0, offsetY: 119, width: 400, height: 40,
        children: [
          {
            name: "Cell1", type: "text",
            offsetX: 12, offsetY: 0, width: 120, height: 40,
            text: "Carol White", textColor: "table.foreground",
            fontSize: 12, textAlign: "left", verticalAlign: "middle",
          },
          {
            name: "Cell2", type: "text",
            offsetX: 144, offsetY: 0, width: 120, height: 40,
            text: "Pending", textColor: "table.muted.foreground",
            fontSize: 12, textAlign: "left", verticalAlign: "middle",
          },
          {
            name: "Cell3", type: "text",
            offsetX: 276, offsetY: 0, width: 112, height: 40,
            text: "$340.00", textColor: "table.foreground",
            fontSize: 12, textAlign: "right", verticalAlign: "middle",
          },
        ],
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/table",
      componentName: "Table",
      additionalImports: ["TableHeader", "TableBody", "TableRow", "TableHead", "TableCell"],
      wrapper: "<Table><TableHeader><TableRow><TableHead /></TableRow></TableHeader><TableBody><TableRow><TableCell /></TableRow></TableBody></Table>",
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Table",
      componentName: "Table",
      additionalImports: [
        "@mui/material/TableHead",
        "@mui/material/TableBody",
        "@mui/material/TableRow",
        "@mui/material/TableCell",
        "@mui/material/TableContainer",
        "@mui/material/Paper",
      ],
    },
  },
};
