import type { ComponentBlueprint } from "../types";

export const paginationBlueprint: ComponentBlueprint = {
  id: "pagination",
  name: "Pagination",
  category: "navigation",
  description: "Page navigation controls for paginated content",
  icon: "navigation/pagination",
  tags: ["pagination", "pages", "navigation", "paging", "next", "previous"],

  props: [
    { name: "currentPage", type: "number", label: "Current Page", defaultValue: 1, affectsCanvas: true },
    { name: "totalPages", type: "number", label: "Total Pages", defaultValue: 5 },
  ],

  events: [
    { name: "onPageChange", label: "Page Change", description: "Fired when page changes", payloadType: "number" },
  ],

  tokenBindings: {
    background: "pagination.background",
    foreground: "pagination.foreground",
    activeBackground: "pagination.active.background",
    activeForeground: "pagination.active.foreground",
    border: "pagination.border",
  },

  canvasTemplate: {
    type: "frame",
    width: 280,
    height: 36,
    children: [
      {
        name: "PrevButton", type: "frame",
        offsetX: 0, offsetY: 0, width: 36, height: 36,
        fill: "pagination.background", stroke: "pagination.border", strokeWidth: 1, cornerRadius: 6,
        children: [
          {
            name: "PrevIcon", type: "text",
            offsetX: 0, offsetY: 0, width: 36, height: 36,
            text: "\u2039", textColor: "pagination.foreground",
            fontSize: 16, textAlign: "center", verticalAlign: "middle",
          },
        ],
      },
      {
        name: "Page1", type: "frame",
        offsetX: 44, offsetY: 0, width: 36, height: 36,
        fill: "pagination.active.background", cornerRadius: 6,
        children: [
          {
            name: "PageNum", type: "text",
            offsetX: 0, offsetY: 0, width: 36, height: 36,
            text: "1", textColor: "pagination.active.foreground",
            fontSize: 13, fontWeight: 500, textAlign: "center", verticalAlign: "middle",
          },
        ],
      },
      {
        name: "Page2", type: "frame",
        offsetX: 84, offsetY: 0, width: 36, height: 36,
        fill: "pagination.background", stroke: "pagination.border", strokeWidth: 1, cornerRadius: 6,
        children: [
          {
            name: "PageNum", type: "text",
            offsetX: 0, offsetY: 0, width: 36, height: 36,
            text: "2", textColor: "pagination.foreground",
            fontSize: 13, textAlign: "center", verticalAlign: "middle",
          },
        ],
      },
      {
        name: "Page3", type: "frame",
        offsetX: 124, offsetY: 0, width: 36, height: 36,
        fill: "pagination.background", stroke: "pagination.border", strokeWidth: 1, cornerRadius: 6,
        children: [
          {
            name: "PageNum", type: "text",
            offsetX: 0, offsetY: 0, width: 36, height: 36,
            text: "3", textColor: "pagination.foreground",
            fontSize: 13, textAlign: "center", verticalAlign: "middle",
          },
        ],
      },
      {
        name: "Ellipsis", type: "text",
        offsetX: 164, offsetY: 0, width: 36, height: 36,
        text: "\u2026", textColor: "pagination.foreground",
        fontSize: 13, textAlign: "center", verticalAlign: "middle",
      },
      {
        name: "NextButton", type: "frame",
        offsetX: 244, offsetY: 0, width: 36, height: 36,
        fill: "pagination.background", stroke: "pagination.border", strokeWidth: 1, cornerRadius: 6,
        children: [
          {
            name: "NextIcon", type: "text",
            offsetX: 0, offsetY: 0, width: 36, height: 36,
            text: "\u203A", textColor: "pagination.foreground",
            fontSize: 16, textAlign: "center", verticalAlign: "middle",
          },
        ],
      },
    ],
  },

  libraryMappings: {
    shadcn: {
      library: "shadcn",
      importPath: "@/components/ui/pagination",
      componentName: "Pagination",
      additionalImports: ["PaginationContent", "PaginationItem", "PaginationLink", "PaginationPrevious", "PaginationNext", "PaginationEllipsis"],
      wrapper: "<Pagination><PaginationContent><PaginationItem><PaginationPrevious /></PaginationItem><PaginationItem><PaginationLink /></PaginationItem><PaginationItem><PaginationNext /></PaginationItem></PaginationContent></Pagination>",
    },
    mui: {
      library: "mui",
      importPath: "@mui/material/Pagination",
      componentName: "Pagination",
      propMappings: { currentPage: "page", totalPages: "count" },
    },
  },
};
