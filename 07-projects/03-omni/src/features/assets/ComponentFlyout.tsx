import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { OmniIcon } from "@/core/icons";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Checkbox } from "@/components/ui/checkbox";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { addComponentToCanvas } from "@/features/canvas/componentBlueprints";
import { useUIStore } from "@/stores/ui.store";
import { useCanvasStore } from "@/stores/canvas.store";
import { cn } from "@/lib/utils";

// ─── Shared types ─────────────────────────────────────────────────────────────

export interface ComponentDef {
  name: string;
  description: string;
  installed: boolean;
  width?: number;
  height?: number;
}

// ─── Prop system ──────────────────────────────────────────────────────────────

type PropValue = string | boolean | number;
type PropsMap = Record<string, PropValue>;

interface PropDef {
  key: string;
  label: string;
  type: "select" | "text" | "boolean" | "range";
  options?: string[];
  min?: number;
  max?: number;
}

interface ComponentConfig {
  defaultProps: PropsMap;
  propDefs: PropDef[];
  render(props: PropsMap): React.ReactNode;
}

// ─── Component config map ────────────────────────────────────────────────────

export const COMPONENT_CONFIGS: Record<string, ComponentConfig> = {
  Button: {
    defaultProps: { variant: "default", size: "default", label: "Button", disabled: false },
    propDefs: [
      { key: "label", label: "Label", type: "text" },
      {
        key: "variant", label: "Variant", type: "select",
        options: ["default", "secondary", "outline", "ghost", "destructive", "link"],
      },
      { key: "size", label: "Size", type: "select", options: ["default", "sm", "lg"] },
      { key: "disabled", label: "Disabled", type: "boolean" },
    ],
    render: (p) => (
      <Button
        variant={p.variant as "default" | "secondary" | "outline" | "ghost" | "destructive" | "link"}
        size={p.size as "default" | "sm" | "lg"}
        disabled={!!p.disabled}
      >
        {String(p.label)}
      </Button>
    ),
  },

  Badge: {
    defaultProps: { variant: "default", label: "Badge" },
    propDefs: [
      { key: "label", label: "Label", type: "text" },
      {
        key: "variant", label: "Variant", type: "select",
        options: ["default", "secondary", "outline", "destructive"],
      },
    ],
    render: (p) => (
      <Badge variant={p.variant as "default" | "secondary" | "outline" | "destructive"}>
        {String(p.label)}
      </Badge>
    ),
  },

  Input: {
    defaultProps: { placeholder: "Enter text…", type: "text", disabled: false },
    propDefs: [
      { key: "placeholder", label: "Placeholder", type: "text" },
      { key: "type", label: "Type", type: "select", options: ["text", "password", "email", "number"] },
      { key: "disabled", label: "Disabled", type: "boolean" },
    ],
    render: (p) => (
      <Input
        placeholder={String(p.placeholder)}
        type={String(p.type)}
        disabled={!!p.disabled}
        className="w-48"
        readOnly
      />
    ),
  },

  Select: {
    defaultProps: { placeholder: "Select option…" },
    propDefs: [
      { key: "placeholder", label: "Placeholder", type: "text" },
    ],
    render: (p) => (
      <div className="flex h-9 w-48 items-center justify-between rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm text-muted-foreground">
        <span>{String(p.placeholder)}</span>
        <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m7 15 5 5 5-5" /><path d="m7 9 5-5 5 5" /></svg>
      </div>
    ),
  },

  Progress: {
    defaultProps: { value: 60 },
    propDefs: [
      { key: "value", label: "Value", type: "range", min: 0, max: 100 },
    ],
    render: (p) => <Progress value={Number(p.value)} className="w-44" />,
  },

  Card: {
    defaultProps: { title: "Card Title", content: "Card content goes here." },
    propDefs: [
      { key: "title", label: "Title", type: "text" },
      { key: "content", label: "Content", type: "text" },
    ],
    render: (p) => (
      <Card className="w-52 py-4">
        <CardHeader className="pb-2 px-4">
          <CardTitle className="text-sm">{String(p.title)}</CardTitle>
        </CardHeader>
        <CardContent className="px-4">
          <p className="text-xs text-muted-foreground">{String(p.content)}</p>
        </CardContent>
      </Card>
    ),
  },

  Tabs: {
    defaultProps: { tab1: "Tab 1", tab2: "Tab 2", tab3: "Tab 3" },
    propDefs: [
      { key: "tab1", label: "Tab 1", type: "text" },
      { key: "tab2", label: "Tab 2", type: "text" },
      { key: "tab3", label: "Tab 3", type: "text" },
    ],
    render: (p) => (
      <Tabs defaultValue="a">
        <TabsList>
          <TabsTrigger value="a">{String(p.tab1)}</TabsTrigger>
          <TabsTrigger value="b">{String(p.tab2)}</TabsTrigger>
          <TabsTrigger value="c">{String(p.tab3)}</TabsTrigger>
        </TabsList>
      </Tabs>
    ),
  },

  Separator: {
    defaultProps: { orientation: "horizontal" },
    propDefs: [
      { key: "orientation", label: "Orientation", type: "select", options: ["horizontal", "vertical"] },
    ],
    render: (p) => (
      <div className={cn(
        "flex items-center justify-center",
        p.orientation === "horizontal" ? "w-40 h-8" : "w-8 h-20",
      )}>
        <Separator
          orientation={p.orientation as "horizontal" | "vertical"}
          className={p.orientation === "horizontal" ? "w-full" : "h-full"}
        />
      </div>
    ),
  },

  Dialog: {
    defaultProps: { trigger: "Open Dialog" },
    propDefs: [
      { key: "trigger", label: "Trigger Label", type: "text" },
    ],
    render: (p) => (
      <Button variant="outline">{String(p.trigger)} ↗</Button>
    ),
  },

  Popover: {
    defaultProps: { trigger: "Open Popover" },
    propDefs: [
      { key: "trigger", label: "Trigger Label", type: "text" },
    ],
    render: (p) => (
      <Button variant="outline">{String(p.trigger)} ↗</Button>
    ),
  },

  Tooltip: {
    defaultProps: { trigger: "Hover for tooltip" },
    propDefs: [
      { key: "trigger", label: "Trigger Text", type: "text" },
    ],
    render: (p) => (
      <span className="text-sm border-b border-dotted border-current cursor-help text-[var(--mauve-11)]">
        {String(p.trigger)}
      </span>
    ),
  },

  DropdownMenu: {
    defaultProps: { trigger: "Options" },
    propDefs: [
      { key: "trigger", label: "Trigger Label", type: "text" },
    ],
    render: (p) => (
      <Button variant="outline">{String(p.trigger)} ▾</Button>
    ),
  },

  ScrollArea: {
    defaultProps: { content: "Scrollable content…" },
    propDefs: [
      { key: "content", label: "Content", type: "text" },
    ],
    render: (p) => (
      <div className="w-40 h-20 rounded border border-[var(--mauve-6)] overflow-hidden bg-[var(--mauve-2)] text-xs text-[var(--mauve-9)] p-2 leading-relaxed">
        {String(p.content)}
      </div>
    ),
  },

  Accordion: {
    defaultProps: { item1: "Item 1", item2: "Item 2" },
    propDefs: [
      { key: "item1", label: "Item 1", type: "text" },
      { key: "item2", label: "Item 2", type: "text" },
    ],
    render: (p) => (
      <Accordion type="single" collapsible className="w-64">
        <AccordionItem value="a">
          <AccordionTrigger className="text-sm py-3">{String(p.item1)}</AccordionTrigger>
          <AccordionContent className="text-xs text-muted-foreground">Content for {String(p.item1)}</AccordionContent>
        </AccordionItem>
        <AccordionItem value="b">
          <AccordionTrigger className="text-sm py-3">{String(p.item2)}</AccordionTrigger>
          <AccordionContent className="text-xs text-muted-foreground">Content for {String(p.item2)}</AccordionContent>
        </AccordionItem>
      </Accordion>
    ),
  },

  Collapsible: {
    defaultProps: { title: "Collapsible", content: "Hidden content here" },
    propDefs: [
      { key: "title", label: "Title", type: "text" },
      { key: "content", label: "Content", type: "text" },
    ],
    render: (p) => (
      <Collapsible open className="w-48 border border-[var(--mauve-5)] rounded-md p-2">
        <CollapsibleTrigger className="flex items-center justify-between w-full text-sm font-medium">
          {String(p.title)} <span className="text-xs">▾</span>
        </CollapsibleTrigger>
        <CollapsibleContent className="text-xs text-muted-foreground pt-2">{String(p.content)}</CollapsibleContent>
      </Collapsible>
    ),
  },

  NavigationMenu: {
    defaultProps: { item1: "Getting Started", item2: "Components", item3: "Docs" },
    propDefs: [
      { key: "item1", label: "Item 1", type: "text" },
      { key: "item2", label: "Item 2", type: "text" },
      { key: "item3", label: "Item 3", type: "text" },
    ],
    render: (p) => (
      <div className="flex items-center h-10 gap-0.5 border border-[var(--mauve-5)] rounded-md px-2 bg-background">
        {([p.item1, p.item2, p.item3] as string[]).map((item, i) => (
          <span key={i} className="px-2 py-1 text-xs rounded text-[var(--mauve-11)]">
            {item}
          </span>
        ))}
      </div>
    ),
  },

  Breadcrumb: {
    defaultProps: { root: "Home", mid: "Components", current: "Button" },
    propDefs: [
      { key: "root", label: "Root", type: "text" },
      { key: "mid", label: "Middle", type: "text" },
      { key: "current", label: "Current", type: "text" },
    ],
    render: (p) => (
      <div className="flex items-center gap-1 text-xs">
        <span className="text-muted-foreground">{String(p.root)}</span>
        <span className="text-muted-foreground">/</span>
        <span className="text-muted-foreground">{String(p.mid)}</span>
        <span className="text-muted-foreground">/</span>
        <span className="font-medium text-foreground">{String(p.current)}</span>
      </div>
    ),
  },

  Checkbox: {
    defaultProps: { label: "Accept terms", checked: true },
    propDefs: [
      { key: "label", label: "Label", type: "text" },
      { key: "checked", label: "Checked", type: "boolean" },
    ],
    render: (p) => (
      <div className="flex items-center gap-2">
        <Checkbox checked={!!p.checked} />
        <span className="text-sm">{String(p.label)}</span>
      </div>
    ),
  },

  Switch: {
    defaultProps: { label: "Enable feature", checked: true },
    propDefs: [
      { key: "label", label: "Label", type: "text" },
      { key: "checked", label: "Checked", type: "boolean" },
    ],
    render: (p) => (
      <div className="flex items-center gap-2">
        <Switch checked={!!p.checked} />
        <span className="text-sm">{String(p.label)}</span>
      </div>
    ),
  },

  Slider: {
    defaultProps: { value: 60 },
    propDefs: [
      { key: "value", label: "Value", type: "range", min: 0, max: 100 },
    ],
    render: (p) => <Slider value={[Number(p.value)]} max={100} className="w-44" />,
  },

  "Radio Group": {
    defaultProps: { option1: "Option 1", option2: "Option 2", option3: "Option 3" },
    propDefs: [
      { key: "option1", label: "Option 1", type: "text" },
      { key: "option2", label: "Option 2", type: "text" },
      { key: "option3", label: "Option 3", type: "text" },
    ],
    render: (p) => (
      <RadioGroup defaultValue="opt1" className="gap-2">
        {([p.option1, p.option2, p.option3] as string[]).map((opt, i) => (
          <div key={i} className="flex items-center gap-2">
            <RadioGroupItem value={`opt${i + 1}`} id={`r${i + 1}`} />
            <label htmlFor={`r${i + 1}`} className="text-sm">{opt}</label>
          </div>
        ))}
      </RadioGroup>
    ),
  },

  Sonner: {
    defaultProps: { title: "Event created", description: "Sunday, December 03 at 9:00 AM" },
    propDefs: [
      { key: "title", label: "Title", type: "text" },
      { key: "description", label: "Description", type: "text" },
    ],
    render: (p) => (
      <div className="flex flex-col gap-1 bg-background border border-[var(--mauve-5)] rounded-lg px-4 py-3 shadow-md w-64 text-sm">
        <span className="font-medium">{String(p.title)}</span>
        <span className="text-xs text-muted-foreground">{String(p.description)}</span>
      </div>
    ),
  },

  Avatar: {
    defaultProps: { initials: "AB", size: "default" },
    propDefs: [
      { key: "initials", label: "Initials", type: "text" },
      { key: "size", label: "Size", type: "select", options: ["default", "sm", "lg"] },
    ],
    render: (p) => (
      <Avatar className={p.size === "sm" ? "h-8 w-8" : p.size === "lg" ? "h-14 w-14" : ""}>
        <AvatarFallback>{String(p.initials).slice(0, 2).toUpperCase()}</AvatarFallback>
      </Avatar>
    ),
  },

  Alert: {
    defaultProps: { title: "Heads up!", description: "You can add components to your app using the CLI.", variant: "default" },
    propDefs: [
      { key: "title", label: "Title", type: "text" },
      { key: "description", label: "Description", type: "text" },
      { key: "variant", label: "Variant", type: "select", options: ["default", "destructive"] },
    ],
    render: (p) => (
      <Alert variant={p.variant as "default" | "destructive"} className="w-64">
        <AlertTitle>{String(p.title)}</AlertTitle>
        <AlertDescription className="text-xs">{String(p.description)}</AlertDescription>
      </Alert>
    ),
  },

  Table: {
    defaultProps: { col1: "Name", col2: "Status", col3: "Amount" },
    propDefs: [
      { key: "col1", label: "Col 1 Header", type: "text" },
      { key: "col2", label: "Col 2 Header", type: "text" },
      { key: "col3", label: "Col 3 Header", type: "text" },
    ],
    render: (p) => (
      <Table className="w-72 text-xs">
        <TableHeader>
          <TableRow>
            <TableHead>{String(p.col1)}</TableHead>
            <TableHead>{String(p.col2)}</TableHead>
            <TableHead>{String(p.col3)}</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell>Alice</TableCell>
            <TableCell>Active</TableCell>
            <TableCell>$250</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Bob</TableCell>
            <TableCell>Inactive</TableCell>
            <TableCell>$150</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    ),
  },
};

// ─── Prop editor row ─────────────────────────────────────────────────────────

function PropEditor({
  def,
  value,
  onChange,
}: {
  def: PropDef;
  value: PropValue;
  onChange(v: PropValue): void;
}) {
  if (def.type === "select" && def.options) {
    return (
      <select
        value={String(value)}
        onChange={(e) => onChange(e.target.value)}
        className="flex-1 h-5 bg-[var(--mauve-3)] border border-[var(--mauve-5)] rounded text-[10px] text-[var(--mauve-11)] px-1 outline-none focus:border-[var(--violet-7)] cursor-pointer"
      >
        {def.options.map((o) => (
          <option key={o} value={o}>{o}</option>
        ))}
      </select>
    );
  }

  if (def.type === "text") {
    return (
      <input
        type="text"
        value={String(value)}
        onChange={(e) => onChange(e.target.value)}
        className="flex-1 h-5 bg-[var(--mauve-3)] border border-[var(--mauve-5)] rounded text-[10px] text-[var(--mauve-11)] px-1.5 outline-none focus:border-[var(--violet-7)]"
      />
    );
  }

  if (def.type === "boolean") {
    return (
      <button
        onClick={() => onChange(!value)}
        className={cn(
          "h-5 px-2 rounded text-[10px] transition-colors",
          value
            ? "bg-[var(--violet-9)] text-white"
            : "bg-[var(--mauve-4)] text-[var(--mauve-10)] hover:bg-[var(--mauve-5)]",
        )}
      >
        {value ? "On" : "Off"}
      </button>
    );
  }

  if (def.type === "range") {
    return (
      <div className="flex items-center gap-1.5 flex-1">
        <input
          type="range"
          min={def.min ?? 0}
          max={def.max ?? 100}
          value={Number(value)}
          onChange={(e) => onChange(Number(e.target.value))}
          className="flex-1 accent-[var(--violet-9)]"
          style={{ height: 4 }}
        />
        <span className="text-[10px] text-[var(--mauve-8)] w-6 text-right tabular-nums">
          {Number(value)}
        </span>
      </div>
    );
  }

  return null;
}

// ─── ComponentFlyout ─────────────────────────────────────────────────────────

interface ComponentFlyoutProps {
  def: ComponentDef;
  onClose(): void;
}

export function ComponentFlyout({ def, onClose }: ComponentFlyoutProps) {
  const { leftPanelWidth, rightPanelWidth, zoom } = useUIStore();
  const { stageX, stageY } = useCanvasStore();

  const { addNode, selectNodes } = useCanvasStore();
  const config = COMPONENT_CONFIGS[def.name];
  const [props, setProps] = useState<PropsMap>(config?.defaultProps ?? {});

  // Reset props when def changes
  useEffect(() => {
    setProps(config?.defaultProps ?? {});
  }, [def.name]); // eslint-disable-line react-hooks/exhaustive-deps

  // Escape to close
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape") onClose();
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [onClose]);

  function setProp(key: string, value: PropValue) {
    setProps((prev) => ({ ...prev, [key]: value }));
  }

  function handleAddToCanvas() {
    const w = def.width ?? 200;
    const h = def.height ?? 80;
    const canvasCenterX = leftPanelWidth + (window.innerWidth - leftPanelWidth - rightPanelWidth) / 2;
    const canvasCenterY = 48 + (window.innerHeight - 48) / 2;
    const worldX = (canvasCenterX - stageX) / zoom - w / 2;
    const worldY = (canvasCenterY - stageY) / zoom - h / 2;
    addComponentToCanvas(def.name, worldX, worldY, addNode, selectNodes);
    onClose();
  }

  // Scale preview to fit the 120×220 preview area
  const scale = config
    ? Math.min(1, 100 / ((def.height ?? 80) + 20), 200 / ((def.width ?? 200) + 20))
    : 1;

  return createPortal(
    <div
      className="fixed bg-[var(--color-surface-1)] border-r border-[var(--color-border-subtle)] flex flex-col shadow-xl z-40"
      style={{ left: leftPanelWidth, top: 48, bottom: 0, width: 280 }}
    >
      {/* Header */}
      <div className="flex items-center justify-between h-10 px-3 flex-shrink-0 border-b border-[var(--color-border-subtle)]">
        <div className="flex items-center gap-2">
          <span className="text-xs font-medium text-[var(--mauve-12)]">{def.name}</span>
          {!def.installed && (
            <span className="text-[9px] text-[var(--mauve-7)] bg-[var(--mauve-3)] px-1.5 py-0.5 rounded">
              Not installed
            </span>
          )}
        </div>
        <button
          onClick={onClose}
          className="w-5 h-5 flex items-center justify-center rounded text-[var(--mauve-8)] hover:text-[var(--mauve-12)] hover:bg-[var(--mauve-4)] transition-colors"
        >
          <OmniIcon name="action/close" size={12} />
        </button>
      </div>

      {/* Preview */}
      <div className="flex-shrink-0 h-[140px] bg-[var(--mauve-2)] border-b border-[var(--color-border-subtle)] flex items-center justify-center overflow-hidden">
        {config ? (
          <div
            className="pointer-events-none select-none flex items-center justify-center"
            style={{ transform: `scale(${scale})`, transformOrigin: "center center" }}
          >
            {config.render(props)}
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2 text-center px-6">
            <div className="w-10 h-10 rounded-lg bg-[var(--mauve-4)] flex items-center justify-center">
              <span className="text-sm font-mono text-[var(--mauve-9)]">{def.name.slice(0, 2)}</span>
            </div>
            <p className="text-[10px] text-[var(--mauve-8)] leading-relaxed">
              Install with{" "}
              <code className="text-[var(--mauve-10)] bg-[var(--mauve-3)] px-1 rounded">
                npx shadcn@latest add {def.name.toLowerCase()}
              </code>
            </p>
          </div>
        )}
      </div>

      {/* Props */}
      <div className="flex-1 overflow-y-auto">
        {config && config.propDefs.length > 0 ? (
          <>
            <div className="px-3 py-2 border-b border-[var(--color-border-subtle)]">
              <span className="text-[9px] font-semibold uppercase tracking-wider text-[var(--mauve-8)]">
                Props
              </span>
            </div>
            <div className="py-1">
              {config.propDefs.map((propDef) => (
                <div key={propDef.key} className="flex items-center gap-2 px-3 h-8">
                  <span className="text-[10px] text-[var(--mauve-8)] w-20 flex-shrink-0">
                    {propDef.label}
                  </span>
                  <PropEditor
                    def={propDef}
                    value={props[propDef.key]}
                    onChange={(v) => setProp(propDef.key, v)}
                  />
                </div>
              ))}
            </div>
          </>
        ) : !config ? (
          <div className="px-3 py-4 space-y-1">
            <p className="text-[10px] text-[var(--mauve-8)] leading-relaxed">
              Run the following to install this component:
            </p>
            <code className="block text-[10px] text-[var(--mauve-10)] bg-[var(--mauve-3)] px-2 py-1 rounded">
              npx shadcn@latest add {def.name.toLowerCase()}
            </code>
          </div>
        ) : (
          <div className="px-3 py-4">
            <p className="text-[10px] text-[var(--mauve-7)] italic">No configurable props</p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="flex-shrink-0 border-t border-[var(--color-border-subtle)] p-3">
        <button
          onClick={handleAddToCanvas}
          className="w-full h-8 rounded bg-[var(--violet-9)] text-white text-xs font-medium hover:bg-[var(--violet-10)] transition-colors"
        >
          Add to canvas
        </button>
      </div>
    </div>,
    document.body,
  );
}
