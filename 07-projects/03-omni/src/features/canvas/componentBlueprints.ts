// ─── Component blueprints ────────────────────────────────────────────────────
// Defines the layered node structure for each UI component when placed on the
// canvas. Each component is built as a tree of frames, rectangles, and text
// nodes that mirror the component's actual HTML structure.

import type { CanvasNode } from "@/types/canvas";

// ─── Color palette ────────────────────────────────────────────────────────────

const C = {
  bg:          "#ffffff",
  bgSubtle:    "#f4f4f5",
  bgDark:      "#18181b",
  fgDark:      "#09090b",
  fgMuted:     "#71717a",
  fgDim:       "#a1a1aa",
  fgLight:     "#fafafa",
  border:      "#e4e4e7",
  primary:     "#7c3aed",
  destructive: "#ef4444",
} as const;

// ─── NodeSpec ─────────────────────────────────────────────────────────────────

interface NodeSpec {
  type: "frame" | "rectangle" | "text";
  name: string;
  /** X offset relative to the parent node's origin */
  rx: number;
  /** Y offset relative to the parent node's origin */
  ry: number;
  width: number;
  height: number;
  fill?: string | null;
  stroke?: string | null;
  strokeWidth?: number;
  cornerRadius?: number;
  opacity?: number;
  // Text-only fields
  text?: string;
  textColor?: string;
  fontSize?: number;
  fontWeight?: number;
  textAlign?: "left" | "center" | "right";
  verticalAlign?: "top" | "middle" | "bottom";
  lineHeight?: number;
  children?: NodeSpec[];
}

// ─── AddNodeFn type ───────────────────────────────────────────────────────────

type AddNodeFn = (
  node: Pick<CanvasNode, "type" | "name" | "x" | "y" | "width" | "height" | "parentId"> &
    Partial<Omit<CanvasNode, "id" | "order">>
) => string;

// ─── Tree builder ─────────────────────────────────────────────────────────────

function buildTree(
  spec: NodeSpec,
  absX: number,
  absY: number,
  parentId: string | null,
  addNode: AddNodeFn,
): string {
  const { rx: _rx, ry: _ry, children, ...nodeProps } = spec;
  const id = addNode({
    ...nodeProps,
    x: Math.round(absX),
    y: Math.round(absY),
    parentId,
  } as Parameters<AddNodeFn>[0]);

  for (const child of children ?? []) {
    buildTree(child, absX + child.rx, absY + child.ry, id, addNode);
  }
  return id;
}

// ─── Component blueprints ─────────────────────────────────────────────────────

const BLUEPRINTS: Record<string, NodeSpec> = {

  // ── Button ──────────────────────────────────────────────────────────────────
  Button: {
    type: "frame", name: "Button", rx: 0, ry: 0, width: 100, height: 36,
    fill: C.primary, cornerRadius: 6,
    children: [
      {
        type: "text", name: "Label", rx: 0, ry: 0, width: 100, height: 36,
        text: "Button", textColor: C.fgLight, fontSize: 14, fontWeight: 500,
        textAlign: "center", verticalAlign: "middle",
      },
    ],
  },

  // ── Badge ───────────────────────────────────────────────────────────────────
  Badge: {
    type: "frame", name: "Badge", rx: 0, ry: 0, width: 60, height: 22,
    fill: C.bgDark, cornerRadius: 9999,
    children: [
      {
        type: "text", name: "Label", rx: 0, ry: 0, width: 60, height: 22,
        text: "Badge", textColor: C.fgLight, fontSize: 10, fontWeight: 500,
        textAlign: "center", verticalAlign: "middle",
      },
    ],
  },

  // ── Input ───────────────────────────────────────────────────────────────────
  Input: {
    type: "frame", name: "Input", rx: 0, ry: 0, width: 240, height: 36,
    fill: C.bg, stroke: C.border, strokeWidth: 1, cornerRadius: 6,
    children: [
      {
        type: "text", name: "Placeholder", rx: 12, ry: 0, width: 216, height: 36,
        text: "Enter text…", textColor: C.fgDim, fontSize: 14,
        textAlign: "left", verticalAlign: "middle",
      },
    ],
  },

  // ── Select ──────────────────────────────────────────────────────────────────
  Select: {
    type: "frame", name: "Select", rx: 0, ry: 0, width: 200, height: 36,
    fill: C.bg, stroke: C.border, strokeWidth: 1, cornerRadius: 6,
    children: [
      {
        type: "text", name: "Placeholder", rx: 12, ry: 0, width: 160, height: 36,
        text: "Select option…", textColor: C.fgDim, fontSize: 14,
        textAlign: "left", verticalAlign: "middle",
      },
      {
        type: "text", name: "ChevronIcon", rx: 176, ry: 0, width: 16, height: 36,
        text: "⌄", textColor: C.fgMuted, fontSize: 14,
        textAlign: "center", verticalAlign: "middle",
      },
    ],
  },

  // ── Separator ───────────────────────────────────────────────────────────────
  Separator: {
    type: "rectangle", name: "Separator", rx: 0, ry: 0, width: 200, height: 1,
    fill: C.border,
  },

  // ── Progress ────────────────────────────────────────────────────────────────
  Progress: {
    type: "frame", name: "Progress", rx: 0, ry: 0, width: 240, height: 8,
    fill: C.bgSubtle, cornerRadius: 9999,
    children: [
      {
        type: "frame", name: "Progress.Indicator", rx: 0, ry: 0, width: 144, height: 8,
        fill: C.bgDark, cornerRadius: 9999,
      },
    ],
  },

  // ── Card ────────────────────────────────────────────────────────────────────
  Card: {
    type: "frame", name: "Card", rx: 0, ry: 0, width: 320, height: 160,
    fill: C.bg, stroke: C.border, strokeWidth: 1, cornerRadius: 8,
    children: [
      {
        type: "frame", name: "CardHeader", rx: 0, ry: 0, width: 320, height: 56, fill: null,
        children: [
          {
            type: "text", name: "CardTitle", rx: 16, ry: 12, width: 288, height: 20,
            text: "Card Title", textColor: C.fgDark, fontSize: 16, fontWeight: 600,
            textAlign: "left", verticalAlign: "top",
          },
          {
            type: "text", name: "CardDescription", rx: 16, ry: 34, width: 288, height: 16,
            text: "Card description goes here.", textColor: C.fgMuted, fontSize: 12,
            textAlign: "left", verticalAlign: "top",
          },
        ],
      },
      { type: "rectangle", name: "Separator", rx: 0, ry: 56, width: 320, height: 1, fill: C.border },
      {
        type: "frame", name: "CardContent", rx: 0, ry: 57, width: 320, height: 103, fill: null,
        children: [
          {
            type: "text", name: "ContentText", rx: 16, ry: 12, width: 288, height: 20,
            text: "Card content goes here.", textColor: C.fgMuted, fontSize: 12,
            textAlign: "left", verticalAlign: "top",
          },
        ],
      },
    ],
  },

  // ── Tabs ────────────────────────────────────────────────────────────────────
  Tabs: {
    type: "frame", name: "Tabs", rx: 0, ry: 0, width: 320, height: 120, fill: null,
    children: [
      {
        type: "frame", name: "TabsList", rx: 0, ry: 0, width: 320, height: 36,
        fill: C.bgSubtle, cornerRadius: 6,
        children: [
          {
            type: "frame", name: "TabsTrigger", rx: 4, ry: 4, width: 100, height: 28,
            fill: C.bg, cornerRadius: 4,
            children: [
              {
                type: "text", name: "TabLabel", rx: 0, ry: 0, width: 100, height: 28,
                text: "Tab 1", textColor: C.fgDark, fontSize: 12, fontWeight: 500,
                textAlign: "center", verticalAlign: "middle",
              },
            ],
          },
          {
            type: "frame", name: "TabsTrigger", rx: 108, ry: 4, width: 100, height: 28,
            fill: null, cornerRadius: 4,
            children: [
              {
                type: "text", name: "TabLabel", rx: 0, ry: 0, width: 100, height: 28,
                text: "Tab 2", textColor: C.fgMuted, fontSize: 12,
                textAlign: "center", verticalAlign: "middle",
              },
            ],
          },
          {
            type: "frame", name: "TabsTrigger", rx: 212, ry: 4, width: 100, height: 28,
            fill: null, cornerRadius: 4,
            children: [
              {
                type: "text", name: "TabLabel", rx: 0, ry: 0, width: 100, height: 28,
                text: "Tab 3", textColor: C.fgMuted, fontSize: 12,
                textAlign: "center", verticalAlign: "middle",
              },
            ],
          },
        ],
      },
      {
        type: "frame", name: "TabsContent", rx: 0, ry: 44, width: 320, height: 76, fill: null,
        children: [
          {
            type: "text", name: "Content", rx: 4, ry: 8, width: 312, height: 20,
            text: "Tab content here.", textColor: C.fgMuted, fontSize: 12,
            textAlign: "left", verticalAlign: "top",
          },
        ],
      },
    ],
  },

  // ── ScrollArea ──────────────────────────────────────────────────────────────
  ScrollArea: {
    type: "frame", name: "ScrollArea", rx: 0, ry: 0, width: 240, height: 160,
    fill: C.bg, stroke: C.border, strokeWidth: 1, cornerRadius: 8,
    children: [
      {
        type: "text", name: "Content", rx: 12, ry: 12, width: 204, height: 136,
        text: "Scrollable content\n\nMore content below…\n\nAnd more here.",
        textColor: C.fgMuted, fontSize: 12,
        textAlign: "left", verticalAlign: "top",
      },
      {
        type: "rectangle", name: "ScrollbarTrack", rx: 228, ry: 4, width: 4, height: 152,
        fill: C.bgSubtle, cornerRadius: 2,
      },
      {
        type: "rectangle", name: "ScrollbarThumb", rx: 228, ry: 4, width: 4, height: 48,
        fill: C.fgDim, cornerRadius: 2,
      },
    ],
  },

  // ── Dialog ──────────────────────────────────────────────────────────────────
  Dialog: {
    type: "frame", name: "Dialog", rx: 0, ry: 0, width: 400, height: 240,
    fill: C.bg, stroke: C.border, strokeWidth: 1, cornerRadius: 8,
    children: [
      {
        type: "frame", name: "DialogHeader", rx: 0, ry: 0, width: 400, height: 64, fill: null,
        children: [
          {
            type: "text", name: "DialogTitle", rx: 16, ry: 16, width: 368, height: 24,
            text: "Dialog Title", textColor: C.fgDark, fontSize: 18, fontWeight: 600,
            textAlign: "left", verticalAlign: "top",
          },
          {
            type: "text", name: "DialogDescription", rx: 16, ry: 44, width: 368, height: 16,
            text: "Dialog description text goes here.", textColor: C.fgMuted, fontSize: 13,
            textAlign: "left", verticalAlign: "top",
          },
        ],
      },
      { type: "rectangle", name: "Divider", rx: 0, ry: 64, width: 400, height: 1, fill: C.border },
      {
        type: "frame", name: "DialogContent", rx: 0, ry: 65, width: 400, height: 104, fill: null,
        children: [
          {
            type: "text", name: "ContentText", rx: 16, ry: 12, width: 368, height: 20,
            text: "Add your dialog content here.", textColor: C.fgMuted, fontSize: 13,
            textAlign: "left", verticalAlign: "top",
          },
        ],
      },
      { type: "rectangle", name: "Divider", rx: 0, ry: 169, width: 400, height: 1, fill: C.border },
      {
        type: "frame", name: "DialogFooter", rx: 0, ry: 170, width: 400, height: 70, fill: null,
        children: [
          {
            type: "frame", name: "CancelButton", rx: 212, ry: 16, width: 80, height: 36,
            fill: C.bg, stroke: C.border, strokeWidth: 1, cornerRadius: 6,
            children: [
              {
                type: "text", name: "Label", rx: 0, ry: 0, width: 80, height: 36,
                text: "Cancel", textColor: C.fgDark, fontSize: 13, fontWeight: 500,
                textAlign: "center", verticalAlign: "middle",
              },
            ],
          },
          {
            type: "frame", name: "ActionButton", rx: 300, ry: 16, width: 84, height: 36,
            fill: C.primary, cornerRadius: 6,
            children: [
              {
                type: "text", name: "Label", rx: 0, ry: 0, width: 84, height: 36,
                text: "Continue", textColor: C.fgLight, fontSize: 13, fontWeight: 500,
                textAlign: "center", verticalAlign: "middle",
              },
            ],
          },
        ],
      },
    ],
  },

  // ── Popover ─────────────────────────────────────────────────────────────────
  Popover: {
    type: "frame", name: "Popover", rx: 0, ry: 0, width: 240, height: 120,
    fill: C.bg, stroke: C.border, strokeWidth: 1, cornerRadius: 8,
    children: [
      {
        type: "frame", name: "PopoverHeader", rx: 0, ry: 0, width: 240, height: 40, fill: null,
        children: [
          {
            type: "text", name: "PopoverTitle", rx: 16, ry: 12, width: 208, height: 20,
            text: "Popover Title", textColor: C.fgDark, fontSize: 14, fontWeight: 500,
            textAlign: "left", verticalAlign: "top",
          },
        ],
      },
      { type: "rectangle", name: "Divider", rx: 0, ry: 40, width: 240, height: 1, fill: C.border },
      {
        type: "frame", name: "PopoverContent", rx: 0, ry: 41, width: 240, height: 79, fill: null,
        children: [
          {
            type: "text", name: "ContentText", rx: 16, ry: 12, width: 208, height: 20,
            text: "Popover content goes here.", textColor: C.fgMuted, fontSize: 12,
            textAlign: "left", verticalAlign: "top",
          },
        ],
      },
    ],
  },

  // ── Tooltip ─────────────────────────────────────────────────────────────────
  Tooltip: {
    type: "frame", name: "Tooltip", rx: 0, ry: 0, width: 120, height: 28,
    fill: C.bgDark, cornerRadius: 6,
    children: [
      {
        type: "text", name: "Label", rx: 0, ry: 0, width: 120, height: 28,
        text: "Tooltip text", textColor: C.fgLight, fontSize: 11,
        textAlign: "center", verticalAlign: "middle",
      },
    ],
  },

  // ── Accordion ───────────────────────────────────────────────────────────────
  Accordion: {
    type: "frame", name: "Accordion", rx: 0, ry: 0, width: 280, height: 120, fill: null,
    children: [
      {
        type: "frame", name: "AccordionItem", rx: 0, ry: 0, width: 280, height: 48, fill: null,
        children: [
          { type: "text", name: "Label", rx: 12, ry: 0, width: 240, height: 48, text: "Item 1", textColor: C.fgDark, fontSize: 14, fontWeight: 500, textAlign: "left", verticalAlign: "middle" },
          { type: "text", name: "Icon", rx: 256, ry: 0, width: 16, height: 48, text: "▾", textColor: C.fgMuted, fontSize: 12, textAlign: "center", verticalAlign: "middle" },
        ],
      },
      { type: "rectangle", name: "Divider", rx: 0, ry: 48, width: 280, height: 1, fill: C.border },
      {
        type: "frame", name: "AccordionItem", rx: 0, ry: 49, width: 280, height: 48, fill: null,
        children: [
          { type: "text", name: "Label", rx: 12, ry: 0, width: 240, height: 48, text: "Item 2", textColor: C.fgDark, fontSize: 14, textAlign: "left", verticalAlign: "middle" },
          { type: "text", name: "Icon", rx: 256, ry: 0, width: 16, height: 48, text: "▾", textColor: C.fgMuted, fontSize: 12, textAlign: "center", verticalAlign: "middle" },
        ],
      },
      { type: "rectangle", name: "Divider", rx: 0, ry: 97, width: 280, height: 1, fill: C.border },
    ],
  },

  // ── Collapsible ─────────────────────────────────────────────────────────────
  Collapsible: {
    type: "frame", name: "Collapsible", rx: 0, ry: 0, width: 240, height: 80,
    fill: C.bg, stroke: C.border, strokeWidth: 1, cornerRadius: 8,
    children: [
      {
        type: "frame", name: "CollapsibleTrigger", rx: 0, ry: 0, width: 240, height: 40, fill: null,
        children: [
          { type: "text", name: "Title", rx: 12, ry: 0, width: 196, height: 40, text: "Collapsible", textColor: C.fgDark, fontSize: 14, fontWeight: 500, textAlign: "left", verticalAlign: "middle" },
          { type: "text", name: "Icon", rx: 216, ry: 0, width: 16, height: 40, text: "▾", textColor: C.fgMuted, fontSize: 12, textAlign: "center", verticalAlign: "middle" },
        ],
      },
      { type: "rectangle", name: "Divider", rx: 0, ry: 40, width: 240, height: 1, fill: C.border },
      {
        type: "frame", name: "CollapsibleContent", rx: 0, ry: 41, width: 240, height: 39, fill: null,
        children: [
          { type: "text", name: "Content", rx: 12, ry: 10, width: 216, height: 20, text: "Hidden content here", textColor: C.fgMuted, fontSize: 12, textAlign: "left", verticalAlign: "top" },
        ],
      },
    ],
  },

  // ── NavigationMenu ──────────────────────────────────────────────────────────
  NavigationMenu: {
    type: "frame", name: "NavigationMenu", rx: 0, ry: 0, width: 400, height: 40,
    fill: C.bg, stroke: C.border, strokeWidth: 1, cornerRadius: 6,
    children: [
      { type: "text", name: "Item1", rx: 12, ry: 0, width: 108, height: 40, text: "Getting Started", textColor: C.fgDark, fontSize: 13, textAlign: "left", verticalAlign: "middle" },
      { type: "text", name: "Item2", rx: 128, ry: 0, width: 96, height: 40, text: "Components", textColor: C.fgMuted, fontSize: 13, textAlign: "left", verticalAlign: "middle" },
      { type: "text", name: "Item3", rx: 232, ry: 0, width: 48, height: 40, text: "Docs", textColor: C.fgMuted, fontSize: 13, textAlign: "left", verticalAlign: "middle" },
    ],
  },

  // ── Breadcrumb ──────────────────────────────────────────────────────────────
  Breadcrumb: {
    type: "frame", name: "Breadcrumb", rx: 0, ry: 0, width: 240, height: 28, fill: null,
    children: [
      { type: "text", name: "Root", rx: 0, ry: 0, width: 40, height: 28, text: "Home", textColor: C.fgMuted, fontSize: 12, textAlign: "left", verticalAlign: "middle" },
      { type: "text", name: "Sep1", rx: 44, ry: 0, width: 12, height: 28, text: "/", textColor: C.fgDim, fontSize: 12, textAlign: "center", verticalAlign: "middle" },
      { type: "text", name: "Mid", rx: 60, ry: 0, width: 80, height: 28, text: "Components", textColor: C.fgMuted, fontSize: 12, textAlign: "left", verticalAlign: "middle" },
      { type: "text", name: "Sep2", rx: 144, ry: 0, width: 12, height: 28, text: "/", textColor: C.fgDim, fontSize: 12, textAlign: "center", verticalAlign: "middle" },
      { type: "text", name: "Current", rx: 160, ry: 0, width: 80, height: 28, text: "Button", textColor: C.fgDark, fontSize: 12, fontWeight: 500, textAlign: "left", verticalAlign: "middle" },
    ],
  },

  // ── Checkbox ────────────────────────────────────────────────────────────────
  Checkbox: {
    type: "frame", name: "Checkbox", rx: 0, ry: 0, width: 140, height: 24, fill: null,
    children: [
      { type: "frame", name: "CheckboxControl", rx: 0, ry: 2, width: 20, height: 20, fill: C.primary, cornerRadius: 4 },
      { type: "text", name: "Check", rx: 0, ry: 2, width: 20, height: 20, text: "✓", textColor: C.fgLight, fontSize: 12, fontWeight: 700, textAlign: "center", verticalAlign: "middle" },
      { type: "text", name: "Label", rx: 28, ry: 0, width: 112, height: 24, text: "Accept terms", textColor: C.fgDark, fontSize: 13, textAlign: "left", verticalAlign: "middle" },
    ],
  },

  // ── Switch ──────────────────────────────────────────────────────────────────
  Switch: {
    type: "frame", name: "Switch", rx: 0, ry: 0, width: 160, height: 28, fill: null,
    children: [
      { type: "frame", name: "SwitchTrack", rx: 0, ry: 4, width: 36, height: 20, fill: C.primary, cornerRadius: 9999 },
      { type: "frame", name: "SwitchThumb", rx: 18, ry: 6, width: 16, height: 16, fill: C.bg, cornerRadius: 9999 },
      { type: "text", name: "Label", rx: 44, ry: 0, width: 116, height: 28, text: "Enable feature", textColor: C.fgDark, fontSize: 13, textAlign: "left", verticalAlign: "middle" },
    ],
  },

  // ── Slider ──────────────────────────────────────────────────────────────────
  Slider: {
    type: "frame", name: "Slider", rx: 0, ry: 0, width: 240, height: 28, fill: null,
    children: [
      { type: "frame", name: "SliderTrack", rx: 0, ry: 11, width: 240, height: 6, fill: C.bgSubtle, cornerRadius: 9999 },
      { type: "frame", name: "SliderRange", rx: 0, ry: 11, width: 144, height: 6, fill: C.bgDark, cornerRadius: 9999 },
      { type: "frame", name: "SliderThumb", rx: 137, ry: 7, width: 14, height: 14, fill: C.bg, stroke: C.border, strokeWidth: 2, cornerRadius: 9999 },
    ],
  },

  // ── Radio Group ─────────────────────────────────────────────────────────────
  "Radio Group": {
    type: "frame", name: "Radio Group", rx: 0, ry: 0, width: 160, height: 84, fill: null,
    children: [
      {
        type: "frame", name: "RadioItem", rx: 0, ry: 0, width: 160, height: 28, fill: null,
        children: [
          { type: "frame", name: "RadioControl", rx: 0, ry: 4, width: 20, height: 20, fill: null, stroke: C.primary, strokeWidth: 2, cornerRadius: 9999 },
          { type: "frame", name: "RadioDot", rx: 6, ry: 10, width: 8, height: 8, fill: C.primary, cornerRadius: 9999 },
          { type: "text", name: "Label", rx: 28, ry: 0, width: 132, height: 28, text: "Option 1", textColor: C.fgDark, fontSize: 13, textAlign: "left", verticalAlign: "middle" },
        ],
      },
      {
        type: "frame", name: "RadioItem", rx: 0, ry: 28, width: 160, height: 28, fill: null,
        children: [
          { type: "frame", name: "RadioControl", rx: 0, ry: 4, width: 20, height: 20, fill: null, stroke: C.border, strokeWidth: 2, cornerRadius: 9999 },
          { type: "text", name: "Label", rx: 28, ry: 0, width: 132, height: 28, text: "Option 2", textColor: C.fgDark, fontSize: 13, textAlign: "left", verticalAlign: "middle" },
        ],
      },
      {
        type: "frame", name: "RadioItem", rx: 0, ry: 56, width: 160, height: 28, fill: null,
        children: [
          { type: "frame", name: "RadioControl", rx: 0, ry: 4, width: 20, height: 20, fill: null, stroke: C.border, strokeWidth: 2, cornerRadius: 9999 },
          { type: "text", name: "Label", rx: 28, ry: 0, width: 132, height: 28, text: "Option 3", textColor: C.fgDark, fontSize: 13, textAlign: "left", verticalAlign: "middle" },
        ],
      },
    ],
  },

  // ── Sonner (Toast notification) ─────────────────────────────────────────────
  Sonner: {
    type: "frame", name: "Sonner", rx: 0, ry: 0, width: 300, height: 60,
    fill: C.bg, stroke: C.border, strokeWidth: 1, cornerRadius: 8,
    children: [
      { type: "text", name: "Title", rx: 16, ry: 12, width: 268, height: 18, text: "Event created", textColor: C.fgDark, fontSize: 13, fontWeight: 500, textAlign: "left", verticalAlign: "top" },
      { type: "text", name: "Description", rx: 16, ry: 34, width: 268, height: 16, text: "Sunday, December 03 at 9:00 AM", textColor: C.fgMuted, fontSize: 11, textAlign: "left", verticalAlign: "top" },
    ],
  },

  // ── Avatar ──────────────────────────────────────────────────────────────────
  Avatar: {
    type: "frame", name: "Avatar", rx: 0, ry: 0, width: 40, height: 40,
    fill: C.bgSubtle, cornerRadius: 9999,
    children: [
      { type: "text", name: "Initials", rx: 0, ry: 0, width: 40, height: 40, text: "AB", textColor: C.fgDark, fontSize: 14, fontWeight: 500, textAlign: "center", verticalAlign: "middle" },
    ],
  },

  // ── Alert ───────────────────────────────────────────────────────────────────
  Alert: {
    type: "frame", name: "Alert", rx: 0, ry: 0, width: 320, height: 72,
    fill: C.bg, stroke: C.border, strokeWidth: 1, cornerRadius: 8,
    children: [
      { type: "text", name: "AlertTitle", rx: 16, ry: 14, width: 288, height: 20, text: "Heads up!", textColor: C.fgDark, fontSize: 14, fontWeight: 500, textAlign: "left", verticalAlign: "top" },
      { type: "text", name: "AlertDescription", rx: 16, ry: 38, width: 288, height: 20, text: "You can add components using the CLI.", textColor: C.fgMuted, fontSize: 12, textAlign: "left", verticalAlign: "top" },
    ],
  },

  // ── Table ───────────────────────────────────────────────────────────────────
  Table: {
    type: "frame", name: "Table", rx: 0, ry: 0, width: 400, height: 200,
    fill: C.bg, stroke: C.border, strokeWidth: 1, cornerRadius: 8,
    children: [
      {
        type: "frame", name: "TableHeader", rx: 0, ry: 0, width: 400, height: 36, fill: C.bgSubtle, cornerRadius: 0,
        children: [
          { type: "text", name: "Col1", rx: 12, ry: 0, width: 120, height: 36, text: "Name", textColor: C.fgDark, fontSize: 12, fontWeight: 600, textAlign: "left", verticalAlign: "middle" },
          { type: "text", name: "Col2", rx: 144, ry: 0, width: 120, height: 36, text: "Status", textColor: C.fgDark, fontSize: 12, fontWeight: 600, textAlign: "left", verticalAlign: "middle" },
          { type: "text", name: "Col3", rx: 276, ry: 0, width: 112, height: 36, text: "Amount", textColor: C.fgDark, fontSize: 12, fontWeight: 600, textAlign: "right", verticalAlign: "middle" },
        ],
      },
      { type: "rectangle", name: "HeaderDivider", rx: 0, ry: 36, width: 400, height: 1, fill: C.border },
      {
        type: "frame", name: "TableRow", rx: 0, ry: 37, width: 400, height: 40, fill: null,
        children: [
          { type: "text", name: "Cell1", rx: 12, ry: 0, width: 120, height: 40, text: "Alice Johnson", textColor: C.fgDark, fontSize: 12, textAlign: "left", verticalAlign: "middle" },
          { type: "text", name: "Cell2", rx: 144, ry: 0, width: 120, height: 40, text: "Active", textColor: C.fgMuted, fontSize: 12, textAlign: "left", verticalAlign: "middle" },
          { type: "text", name: "Cell3", rx: 276, ry: 0, width: 112, height: 40, text: "$250.00", textColor: C.fgDark, fontSize: 12, textAlign: "right", verticalAlign: "middle" },
        ],
      },
      { type: "rectangle", name: "Divider", rx: 0, ry: 77, width: 400, height: 1, fill: C.border },
      {
        type: "frame", name: "TableRow", rx: 0, ry: 78, width: 400, height: 40, fill: null,
        children: [
          { type: "text", name: "Cell1", rx: 12, ry: 0, width: 120, height: 40, text: "Bob Smith", textColor: C.fgDark, fontSize: 12, textAlign: "left", verticalAlign: "middle" },
          { type: "text", name: "Cell2", rx: 144, ry: 0, width: 120, height: 40, text: "Inactive", textColor: C.fgMuted, fontSize: 12, textAlign: "left", verticalAlign: "middle" },
          { type: "text", name: "Cell3", rx: 276, ry: 0, width: 112, height: 40, text: "$150.00", textColor: C.fgDark, fontSize: 12, textAlign: "right", verticalAlign: "middle" },
        ],
      },
      { type: "rectangle", name: "Divider", rx: 0, ry: 118, width: 400, height: 1, fill: C.border },
      {
        type: "frame", name: "TableRow", rx: 0, ry: 119, width: 400, height: 40, fill: null,
        children: [
          { type: "text", name: "Cell1", rx: 12, ry: 0, width: 120, height: 40, text: "Carol White", textColor: C.fgDark, fontSize: 12, textAlign: "left", verticalAlign: "middle" },
          { type: "text", name: "Cell2", rx: 144, ry: 0, width: 120, height: 40, text: "Pending", textColor: C.fgMuted, fontSize: 12, textAlign: "left", verticalAlign: "middle" },
          { type: "text", name: "Cell3", rx: 276, ry: 0, width: 112, height: 40, text: "$340.00", textColor: C.fgDark, fontSize: 12, textAlign: "right", verticalAlign: "middle" },
        ],
      },
    ],
  },

  // ── DropdownMenu ────────────────────────────────────────────────────────────
  DropdownMenu: {
    type: "frame", name: "DropdownMenu", rx: 0, ry: 0, width: 160, height: 180, fill: null,
    children: [
      {
        type: "frame", name: "Trigger", rx: 0, ry: 0, width: 160, height: 36,
        fill: C.bg, stroke: C.border, strokeWidth: 1, cornerRadius: 6,
        children: [
          {
            type: "text", name: "Label", rx: 12, ry: 0, width: 120, height: 36,
            text: "Options", textColor: C.fgDark, fontSize: 13,
            textAlign: "left", verticalAlign: "middle",
          },
          {
            type: "text", name: "Chevron", rx: 136, ry: 0, width: 16, height: 36,
            text: "▾", textColor: C.fgMuted, fontSize: 12,
            textAlign: "center", verticalAlign: "middle",
          },
        ],
      },
      {
        type: "frame", name: "MenuPanel", rx: 0, ry: 44, width: 160, height: 136,
        fill: C.bg, stroke: C.border, strokeWidth: 1, cornerRadius: 6,
        children: [
          {
            type: "text", name: "MenuItem", rx: 8, ry: 0, width: 144, height: 32,
            text: "Edit", textColor: C.fgDark, fontSize: 13,
            textAlign: "left", verticalAlign: "middle",
          },
          { type: "rectangle", name: "Separator", rx: 8, ry: 32, width: 144, height: 1, fill: C.border },
          {
            type: "text", name: "MenuItem", rx: 8, ry: 33, width: 144, height: 32,
            text: "Duplicate", textColor: C.fgDark, fontSize: 13,
            textAlign: "left", verticalAlign: "middle",
          },
          {
            type: "text", name: "MenuItem", rx: 8, ry: 65, width: 144, height: 32,
            text: "Archive", textColor: C.fgDark, fontSize: 13,
            textAlign: "left", verticalAlign: "middle",
          },
          { type: "rectangle", name: "Separator", rx: 8, ry: 97, width: 144, height: 1, fill: C.border },
          {
            type: "text", name: "MenuItem", rx: 8, ry: 100, width: 144, height: 32,
            text: "Delete", textColor: C.destructive, fontSize: 13,
            textAlign: "left", verticalAlign: "middle",
          },
        ],
      },
    ],
  },
};

// ─── Public API ───────────────────────────────────────────────────────────────

/**
 * Adds a named UI component to the canvas at the given world coordinates.
 * Creates the full node tree (parent + all children) and selects the root.
 */
export function addComponentToCanvas(
  name: string,
  worldX: number,
  worldY: number,
  addNode: AddNodeFn,
  selectNodes: (ids: string[]) => void,
): string {
  const blueprint = BLUEPRINTS[name];

  if (!blueprint) {
    // Fallback for uninstalled / unknown components
    const id = addNode({
      type: "frame",
      name,
      x: Math.round(worldX),
      y: Math.round(worldY),
      width: 200,
      height: 80,
      parentId: null,
      fill: C.bgSubtle,
    });
    selectNodes([id]);
    return id;
  }

  const rootId = buildTree(blueprint, worldX, worldY, null, addNode);
  selectNodes([rootId]);
  return rootId;
}
