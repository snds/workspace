import { useState, useMemo } from "react";
import { OmniIcon } from "@/core/icons";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { useComponentCatalogStore } from "@/stores/componentCatalog.store";
import type { ComponentCategory as CatalogCategory } from "@/core/components/types";
import type { ComponentDef } from "./ComponentFlyout";
import { ComponentFlyout, COMPONENT_CONFIGS } from "./ComponentFlyout";

// ─── Component catalog ────────────────────────────────────────────────────────

interface ComponentCategory {
  label: string;
  components: ComponentDef[];
}

/** Map catalog categories to display labels */
const CATEGORY_LABELS: Record<CatalogCategory, string> = {
  action: "Forms",
  input: "Forms",
  display: "Display",
  feedback: "Feedback",
  navigation: "Navigation",
  overlay: "Overlay",
  layout: "Layout",
  typography: "Typography",
  media: "Media",
};

/** Build component categories from the catalog store */
function buildCategoriesFromCatalog(
  getAllBlueprints: () => import("@/core/components/types").ComponentBlueprint[],
): ComponentCategory[] {
  const blueprints = getAllBlueprints();
  const grouped = new Map<string, ComponentDef[]>();

  for (const bp of blueprints) {
    const label = CATEGORY_LABELS[bp.category] ?? bp.category;
    if (!grouped.has(label)) grouped.set(label, []);
    grouped.get(label)!.push({
      name: bp.name,
      description: bp.description ?? "",
      installed: true,
      width: bp.canvasTemplate.width,
      height: bp.canvasTemplate.height,
    });
  }

  // Also include components from COMPONENT_CONFIGS that are NOT in the catalog
  // (some legacy/preview-only components like NavigationMenu, Sonner, etc.)
  const catalogNames = new Set(blueprints.map((bp) => bp.name));
  const LEGACY_EXTRAS: ComponentCategory[] = [
    {
      label: "Navigation",
      components: [
        ...(!catalogNames.has("NavigationMenu") ? [{ name: "NavigationMenu", description: "Top-level navigation with submenus", installed: true, width: 400, height: 40 }] : []),
      ].filter((c) => c.name in COMPONENT_CONFIGS),
    },
    {
      label: "Overlay",
      components: [
        ...(!catalogNames.has("Sonner") ? [{ name: "Sonner", description: "Transient notification message", installed: true, width: 300, height: 60 }] : []),
        ...(!catalogNames.has("Popover") ? [{ name: "Popover", description: "Contextual floating content", installed: true, width: 240, height: 120 }] : []),
      ].filter((c) => c.name in COMPONENT_CONFIGS),
    },
    {
      label: "Layout",
      components: [
        ...(!catalogNames.has("ScrollArea") ? [{ name: "ScrollArea", description: "Scrollable container with custom scrollbar", installed: true, width: 240, height: 160 }] : []),
        ...(!catalogNames.has("Collapsible") ? [{ name: "Collapsible", description: "Single expandable/collapsible element", installed: true, width: 240, height: 80 }] : []),
      ].filter((c) => c.name in COMPONENT_CONFIGS),
    },
    {
      label: "Forms",
      components: [
        ...(!catalogNames.has("Radio Group") ? [{ name: "Radio Group", description: "Single selection from options", installed: true, width: 160, height: 80 }] : []),
      ].filter((c) => c.name in COMPONENT_CONFIGS),
    },
  ];

  // Merge legacy extras into grouped
  for (const extra of LEGACY_EXTRAS) {
    if (extra.components.length === 0) continue;
    if (!grouped.has(extra.label)) grouped.set(extra.label, []);
    grouped.get(extra.label)!.push(...extra.components);
  }

  // Convert to sorted array
  const order = ["Layout", "Navigation", "Forms", "Overlay", "Display", "Feedback", "Typography", "Media"];
  return Array.from(grouped.entries())
    .sort(([a], [b]) => {
      const ai = order.indexOf(a);
      const bi = order.indexOf(b);
      return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi);
    })
    .map(([label, components]) => ({ label, components }));
}

// ─── Component preview ────────────────────────────────────────────────────────

function ComponentPreview({ def, width, height }: { def: ComponentDef; width: number; height: number }) {
  const config = COMPONENT_CONFIGS[def.name];
  if (!config) {
    return (
      <div className="w-full h-full flex items-center justify-center">
        <span className="text-[9px] text-[var(--mauve-7)] font-mono">{def.name.slice(0, 3)}</span>
      </div>
    );
  }
  const scale = Math.min(0.9, (height - 8) / ((def.height ?? 80) + 20), (width - 8) / ((def.width ?? 200) + 20));
  return (
    <div
      className="pointer-events-none select-none flex items-center justify-center w-full h-full"
      style={{ transform: `scale(${Math.max(0.2, scale)})`, transformOrigin: "center center" }}
    >
      {config.render(config.defaultProps)}
    </div>
  );
}

// ─── List item ────────────────────────────────────────────────────────────────

function ComponentListItem({
  def,
  onOpen,
}: {
  def: ComponentDef;
  onOpen(def: ComponentDef): void;
}) {
  function onDragStart(e: React.DragEvent) {
    e.dataTransfer.setData(
      "application/omni-component",
      JSON.stringify({ componentType: "frame", name: def.name, width: def.width ?? 200, height: def.height ?? 80 }),
    );
    e.dataTransfer.effectAllowed = "copy";
  }

  return (
    <div
      draggable
      onDragStart={onDragStart}
      onClick={() => onOpen(def)}
      className="group flex items-center gap-2 h-8 px-2 rounded cursor-pointer hover:bg-[var(--mauve-3)] transition-colors select-none"
      title={def.description}
    >
      {/* Thumbnail */}
      <div className="w-11 h-6 rounded bg-[var(--mauve-3)] border border-[var(--mauve-5)] flex-shrink-0 overflow-hidden">
        <ComponentPreview def={def} width={44} height={24} />
      </div>
      <span className="text-xs text-[var(--mauve-11)] flex-1 truncate">{def.name}</span>
      {!def.installed && (
        <span
          className="w-1.5 h-1.5 rounded-full bg-[var(--mauve-7)] flex-shrink-0"
          title="Not yet installed via shadcn"
        />
      )}
    </div>
  );
}

// ─── Grid card ────────────────────────────────────────────────────────────────

function ComponentGridCard({
  def,
  onOpen,
}: {
  def: ComponentDef;
  onOpen(def: ComponentDef): void;
}) {
  function onDragStart(e: React.DragEvent) {
    e.dataTransfer.setData(
      "application/omni-component",
      JSON.stringify({ componentType: "frame", name: def.name, width: def.width ?? 200, height: def.height ?? 80 }),
    );
    e.dataTransfer.effectAllowed = "copy";
  }

  return (
    <div
      draggable
      onDragStart={onDragStart}
      onClick={() => onOpen(def)}
      className="group rounded border border-[var(--mauve-5)] bg-[var(--mauve-2)] hover:border-[var(--mauve-7)] cursor-pointer transition-colors select-none overflow-hidden"
      title={def.description}
    >
      {/* Preview area */}
      <div className="h-[72px] bg-[var(--mauve-3)] overflow-hidden relative">
        <ComponentPreview def={def} width={120} height={72} />
        {!def.installed && (
          <div className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-[var(--mauve-7)]" />
        )}
      </div>
      {/* Label */}
      <div className="px-1.5 py-1.5">
        <p className="text-[10px] text-[var(--mauve-11)] text-center truncate leading-none">{def.name}</p>
      </div>
    </div>
  );
}

// ─── Category group ───────────────────────────────────────────────────────────

type ViewMode = "list" | "grid";

function CategoryGroup({
  category,
  query,
  viewMode,
  onOpen,
}: {
  category: ComponentCategory;
  query: string;
  viewMode: ViewMode;
  onOpen(def: ComponentDef): void;
}) {
  const [open, setOpen] = useState(true);

  const filtered = useMemo(
    () =>
      query
        ? category.components.filter((c) =>
            c.name.toLowerCase().includes(query.toLowerCase())
          )
        : category.components,
    [category.components, query],
  );

  if (filtered.length === 0) return null;

  return (
    <div>
      <button
        className="flex items-center gap-1 w-full h-6 px-2 text-[9px] font-semibold uppercase tracking-wider text-[var(--mauve-8)] hover:text-[var(--mauve-11)] transition-colors"
        onClick={() => setOpen((v) => !v)}
      >
        <OmniIcon name={open ? "navigation/chevron-down" : "navigation/chevron-right"} size={10} />
        {category.label}
        <span className="ml-auto font-normal normal-case tracking-normal text-[var(--mauve-7)]">
          {filtered.length}
        </span>
      </button>

      {open && (
        viewMode === "grid" ? (
          <div className="grid grid-cols-2 gap-1.5 px-2 pb-2">
            {filtered.map((def) => (
              <ComponentGridCard key={def.name} def={def} onOpen={onOpen} />
            ))}
          </div>
        ) : (
          <div className="pb-1">
            {filtered.map((def) => (
              <ComponentListItem key={def.name} def={def} onOpen={onOpen} />
            ))}
          </div>
        )
      )}
    </div>
  );
}

// ─── Defaults tab ─────────────────────────────────────────────────────────────

function DefaultsTab() {
  const [query, setQuery] = useState("");
  const [viewMode, setViewMode] = useState<ViewMode>("list");
  const [flyoutDef, setFlyoutDef] = useState<ComponentDef | null>(null);
  const getAllBlueprints = useComponentCatalogStore((s) => s.getAllBlueprints);

  const categories = useMemo(
    () => buildCategoriesFromCatalog(getAllBlueprints),
    [getAllBlueprints],
  );

  const hasResults = useMemo(() => {
    if (!query) return true;
    return categories.some((cat) =>
      cat.components.some((c) => c.name.toLowerCase().includes(query.toLowerCase()))
    );
  }, [query, categories]);

  return (
    <div className="flex flex-col h-full">
      {/* Search + view toggle */}
      <div className="px-2 py-2 flex-shrink-0 border-b border-[var(--color-border-subtle)]">
        <div className="flex items-center gap-1">
          <div className="flex items-center gap-1.5 h-6 flex-1 bg-[var(--mauve-3)] rounded px-2 border border-[var(--mauve-5)]">
            <OmniIcon name="action/search" size={12} color="var(--mauve-8)" />
            <input
              type="text"
              placeholder="Search components…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="flex-1 bg-transparent text-xs text-[var(--mauve-12)] placeholder:text-[var(--mauve-8)] outline-none"
            />
          </div>
          <button
            onClick={() => setViewMode("list")}
            className={cn(
              "w-6 h-6 flex items-center justify-center rounded transition-colors",
              viewMode === "list"
                ? "bg-[var(--mauve-5)] text-[var(--mauve-12)]"
                : "text-[var(--mauve-8)] hover:text-[var(--mauve-11)] hover:bg-[var(--mauve-4)]",
            )}
            title="List view"
          >
            <OmniIcon name="content/list" size={12} />
          </button>
          <button
            onClick={() => setViewMode("grid")}
            className={cn(
              "w-6 h-6 flex items-center justify-center rounded transition-colors",
              viewMode === "grid"
                ? "bg-[var(--mauve-5)] text-[var(--mauve-12)]"
                : "text-[var(--mauve-8)] hover:text-[var(--mauve-11)] hover:bg-[var(--mauve-4)]",
            )}
            title="Grid view"
          >
            <OmniIcon name="content/grid" size={12} />
          </button>
        </div>
      </div>

      <ScrollArea className="flex-1 min-h-0">
        <div className="py-1">
          {hasResults ? (
            categories.map((cat) => (
              <CategoryGroup
                key={cat.label}
                category={cat}
                query={query}
                viewMode={viewMode}
                onOpen={setFlyoutDef}
              />
            ))
          ) : (
            <div className="flex flex-col items-center gap-2 py-8 px-3 text-center">
              <OmniIcon name="misc/package" size={28} color="var(--mauve-7)" />
              <p className="text-xs text-[var(--mauve-9)]">No components match "{query}"</p>
            </div>
          )}
        </div>

        {/* Drag hint */}
        <div className="px-3 pb-3 pt-2 border-t border-[var(--color-border-subtle)]">
          <p className="text-[9px] text-[var(--mauve-7)] leading-relaxed">
            Drag components onto the canvas or click to configure and add.
          </p>
        </div>
      </ScrollArea>

      {flyoutDef && (
        <ComponentFlyout def={flyoutDef} onClose={() => setFlyoutDef(null)} />
      )}
    </div>
  );
}

// ─── Custom tab ───────────────────────────────────────────────────────────────

function CustomTab() {
  return (
    <div className="flex flex-col items-center gap-2 py-10 px-4 text-center">
      <div className="w-10 h-10 rounded-lg bg-[var(--mauve-3)] flex items-center justify-center">
        <OmniIcon name="misc/package" size={20} color="var(--mauve-7)" />
      </div>
      <p className="text-xs font-medium text-[var(--mauve-10)]">No custom components</p>
      <p className="text-[10px] text-[var(--mauve-8)] leading-relaxed max-w-[180px]">
        Connect a repository to import your team's component library.
      </p>
    </div>
  );
}

// ─── AssetsPanel ─────────────────────────────────────────────────────────────

type Tab = "defaults" | "custom";

export function AssetsPanel() {
  const [activeTab, setActiveTab] = useState<Tab>("defaults");

  return (
    <div className="flex flex-col h-full bg-[var(--color-surface-1)]">
      {/* Tab bar */}
      <div className="flex flex-shrink-0 border-b border-[var(--color-border-subtle)]">
        {(["defaults", "custom"] as Tab[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={cn(
              "flex-1 h-8 text-xs capitalize transition-colors",
              activeTab === tab
                ? "text-[var(--mauve-12)] border-b-2 border-[var(--violet-9)] -mb-px"
                : "text-[var(--mauve-9)] hover:text-[var(--mauve-11)]",
            )}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === "defaults" ? <DefaultsTab /> : <CustomTab />}
      </div>
    </div>
  );
}
