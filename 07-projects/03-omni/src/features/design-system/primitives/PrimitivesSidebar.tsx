import {
  Palette,
  Type,
  Grid3X3,
  Layers,
  Circle,
  Zap,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useDesignSystemUIStore } from "@/stores/designSystemUI.store";
import type { LucideIcon } from "lucide-react";

interface SidebarChild {
  id: string;
  label: string;
}

interface SidebarCategory {
  id: string;
  label: string;
  icon: LucideIcon;
  children?: SidebarChild[];
}

const CATEGORIES: SidebarCategory[] = [
  {
    id: "colors",
    label: "Colors",
    icon: Palette,
    children: [
      { id: "colors-brand", label: "Brand" },
      { id: "colors-scales", label: "Scales" },
      { id: "colors-dataviz", label: "Data Viz" },
    ],
  },
  {
    id: "typography",
    label: "Typography",
    icon: Type,
    children: [
      { id: "typography-size", label: "Size" },
      { id: "typography-family", label: "Family" },
      { id: "typography-weight", label: "Weight" },
      { id: "typography-lineheight", label: "Line Height" },
      { id: "typography-tracking", label: "Tracking" },
    ],
  },
  { id: "iconography", label: "Iconography", icon: Grid3X3 },
  { id: "space", label: "Space", icon: Layers },
  {
    id: "effects",
    label: "Effects",
    icon: Circle,
    children: [
      { id: "effects-shadow", label: "Shadow" },
      { id: "effects-blur", label: "Blur" },
      { id: "effects-opacity", label: "Opacity" },
    ],
  },
  { id: "radius", label: "Radius", icon: Circle },
  { id: "animations", label: "Animations", icon: Zap },
];

function scrollToSection(id: string) {
  const el = document.getElementById(`section-${id}`);
  if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
}

export function PrimitivesSidebar() {
  const {
    expandedCategories,
    toggleExpanded,
    activePrimitiveCategory,
  } = useDesignSystemUIStore();

  return (
    <div className="w-48 flex-shrink-0 border-r border-[var(--color-border-subtle)] bg-[var(--color-surface-1)] py-3 overflow-y-auto">
      {CATEGORIES.map((cat) => {
        const isExpanded = expandedCategories[cat.id] ?? false;
        const hasChildren = cat.children && cat.children.length > 0;
        const isActive = activePrimitiveCategory === cat.id ||
          (cat.children?.some((c) => activePrimitiveCategory === c.id) ?? false);

        return (
          <div key={cat.id}>
            {/* Category header */}
            <button
              onClick={() => {
                if (hasChildren) toggleExpanded(cat.id);
                scrollToSection(cat.id);
              }}
              className={cn(
                "w-full flex items-center gap-2 px-4 py-1.5 text-[11px] font-medium transition-colors",
                isActive
                  ? "text-[var(--mauve-12)]"
                  : "text-[var(--mauve-9)] hover:text-[var(--mauve-11)]",
              )}
            >
              {hasChildren && (
                <ChevronRight
                  className={cn(
                    "w-3 h-3 transition-transform flex-shrink-0",
                    isExpanded && "rotate-90",
                  )}
                />
              )}
              {!hasChildren && <div className="w-3" />}
              <cat.icon className="w-3.5 h-3.5 flex-shrink-0" />
              {cat.label}
            </button>

            {/* Children */}
            {hasChildren && isExpanded && (
              <div className="ml-[22px]">
                {cat.children!.map((child) => (
                  <button
                    key={child.id}
                    onClick={() => scrollToSection(child.id)}
                    className={cn(
                      "w-full text-left px-4 py-1 text-[10px] transition-colors",
                      activePrimitiveCategory === child.id
                        ? "text-[var(--violet-11)] font-medium"
                        : "text-[var(--mauve-9)] hover:text-[var(--mauve-11)]",
                    )}
                  >
                    {child.label}
                  </button>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
