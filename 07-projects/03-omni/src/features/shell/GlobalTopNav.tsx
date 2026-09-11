import { useLocation, useNavigate, useParams } from "react-router";
import { Palette, LayoutGrid, Code } from "lucide-react";
import { cn } from "@/lib/utils";
import { useProjectStore } from "@/stores/project.store";

const TOOL_PIVOTS = [
  {
    id: "design-system",
    label: "Design System",
    icon: Palette,
    path: "design-system",
  },
  {
    id: "layouts",
    label: "Layouts",
    icon: LayoutGrid,
    path: "layouts",
  },
  {
    id: "code",
    label: "Code",
    icon: Code,
    path: "code",
  },
] as const;

export function GlobalTopNav() {
  const location = useLocation();
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId: string }>();
  const projects = useProjectStore((s) => s.projects);
  const project = projects.find((p) => p.id === projectId);

  const activeTool = TOOL_PIVOTS.find((t) =>
    location.pathname.includes(`/${t.path}`)
  )?.id ?? "design-system";

  return (
    <div className="flex items-center h-10 px-3 border-b border-[var(--color-border-subtle)] bg-[var(--color-surface-1)] flex-shrink-0">
      {/* Logo */}
      <div className="flex items-center gap-2 mr-6">
        <div className="w-5 h-5 rounded bg-[var(--violet-9)] flex items-center justify-center flex-shrink-0">
          <span className="text-[10px] font-bold text-white leading-none">O</span>
        </div>
        <span className="text-[11px] font-semibold text-[var(--mauve-12)]">
          Omni
        </span>
      </div>

      {/* Tool pivots */}
      <div className="flex items-center gap-0.5">
        {TOOL_PIVOTS.map(({ id, label, icon: Icon, path }) => (
          <button
            key={id}
            onClick={() => navigate(`/workspace/${projectId}/${path}`)}
            className={cn(
              "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[11px] font-medium transition-colors",
              activeTool === id
                ? "bg-[var(--mauve-4)] text-[var(--mauve-12)]"
                : "text-[var(--mauve-9)] hover:text-[var(--mauve-11)] hover:bg-[var(--mauve-3)]",
            )}
          >
            <Icon className="w-3.5 h-3.5" />
            {label}
          </button>
        ))}
      </div>

      <div className="flex-1" />

      {/* Project name */}
      {project && (
        <span className="text-[11px] text-[var(--mauve-9)]">
          {project.name}
        </span>
      )}
    </div>
  );
}
