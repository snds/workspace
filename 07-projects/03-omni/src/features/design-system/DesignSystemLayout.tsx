import { Outlet, useLocation, useNavigate } from "react-router";
import { cn } from "@/lib/utils";

const TABS = [
  { id: "overview", label: "Overview" },
  { id: "primitives", label: "Primitives" },
  { id: "semantics", label: "Semantics" },
] as const;

export function DesignSystemLayout() {
  const location = useLocation();
  const navigate = useNavigate();

  const activeTab = TABS.find((t) =>
    location.pathname.endsWith(`/${t.id}`)
  )?.id ?? "overview";

  return (
    <div className="flex flex-col h-full">
      {/* Tab bar */}
      <div className="flex items-center gap-1 px-5 h-9 border-b border-[var(--color-border-subtle)] bg-[var(--color-surface-0)] flex-shrink-0">
        {TABS.map(({ id, label }) => (
          <button
            key={id}
            onClick={() => navigate(id, { relative: "path" })}
            className={cn(
              "px-3 py-1 rounded-md text-[11px] font-medium transition-colors",
              activeTab === id
                ? "bg-[var(--mauve-4)] text-[var(--mauve-12)]"
                : "text-[var(--mauve-9)] hover:text-[var(--mauve-11)] hover:bg-[var(--mauve-3)]",
            )}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="flex-1 min-h-0">
        <Outlet />
      </div>
    </div>
  );
}
