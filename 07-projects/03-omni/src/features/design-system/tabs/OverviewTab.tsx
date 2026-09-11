import { useNavigate } from "react-router";
import { Upload, Plus, Palette } from "lucide-react";
import { useColorSystemStore } from "@/stores/colorSystem.store";
import { makeColorSystem } from "@/features/tokens/presets";
import { DESIGN_SYSTEM_TEMPLATES, type DesignSystemTemplate } from "../overview/templates";
import { TemplateCard } from "../overview/TemplateCard";

export function OverviewTab() {
  const navigate = useNavigate();
  const setColorSystem = useColorSystemStore((s) => s.setColorSystem);

  const handleSelectTemplate = (template: DesignSystemTemplate) => {
    if (!template.sourcePreset) return;
    const cs = makeColorSystem(template.sourcePreset);
    setColorSystem(cs);
    navigate("../primitives", { relative: "path" });
  };

  const handleStartFresh = () => {
    navigate("../primitives", { relative: "path" });
  };

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-4xl mx-auto px-8 py-10">
        {/* Intro */}
        <div className="mb-10">
          <h2 className="text-lg font-semibold text-[var(--mauve-12)]">
            Design System
          </h2>
          <p className="text-[12px] text-[var(--mauve-10)] mt-2 max-w-xl leading-relaxed">
            Define your visual language with a three-tier token architecture:
            Primitives (raw values), Semantics (contextual decisions), and
            Components (per-component overrides). Start from a template or build
            from scratch.
          </p>
        </div>

        {/* Entry path cards */}
        <div className="grid grid-cols-3 gap-4 mb-12">
          {/* Import existing */}
          <button
            onClick={() => {/* TODO: file picker → parseDTCGTree → bulkSet */}}
            className="flex flex-col items-center gap-3 p-6 rounded-xl border border-dashed border-[var(--mauve-5)] bg-[var(--mauve-2)] hover:border-[var(--violet-7)] hover:bg-[var(--mauve-3)] transition-all cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-lg bg-[var(--mauve-4)] flex items-center justify-center group-hover:bg-[var(--violet-4)] transition-colors">
              <Upload className="w-5 h-5 text-[var(--mauve-9)] group-hover:text-[var(--violet-11)]" />
            </div>
            <div className="text-center">
              <h3 className="text-[11px] font-semibold text-[var(--mauve-12)]">
                Import existing
              </h3>
              <p className="text-[9px] text-[var(--mauve-9)] mt-1">
                Load a DTCG JSON file from your current design system
              </p>
            </div>
          </button>

          {/* Start fresh */}
          <button
            onClick={handleStartFresh}
            className="flex flex-col items-center gap-3 p-6 rounded-xl border border-dashed border-[var(--mauve-5)] bg-[var(--mauve-2)] hover:border-[var(--violet-7)] hover:bg-[var(--mauve-3)] transition-all cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-lg bg-[var(--mauve-4)] flex items-center justify-center group-hover:bg-[var(--violet-4)] transition-colors">
              <Plus className="w-5 h-5 text-[var(--mauve-9)] group-hover:text-[var(--violet-11)]" />
            </div>
            <div className="text-center">
              <h3 className="text-[11px] font-semibold text-[var(--mauve-12)]">
                Start fresh
              </h3>
              <p className="text-[9px] text-[var(--mauve-9)] mt-1">
                Begin with default tokens and define your own brand colors
              </p>
            </div>
          </button>

          {/* Use template */}
          <button
            onClick={() => {
              const grid = document.getElementById("template-grid");
              grid?.scrollIntoView({ behavior: "smooth" });
            }}
            className="flex flex-col items-center gap-3 p-6 rounded-xl border border-dashed border-[var(--mauve-5)] bg-[var(--mauve-2)] hover:border-[var(--violet-7)] hover:bg-[var(--mauve-3)] transition-all cursor-pointer group"
          >
            <div className="w-10 h-10 rounded-lg bg-[var(--mauve-4)] flex items-center justify-center group-hover:bg-[var(--violet-4)] transition-colors">
              <Palette className="w-5 h-5 text-[var(--mauve-9)] group-hover:text-[var(--violet-11)]" />
            </div>
            <div className="text-center">
              <h3 className="text-[11px] font-semibold text-[var(--mauve-12)]">
                Use a template
              </h3>
              <p className="text-[9px] text-[var(--mauve-9)] mt-1">
                Start from a popular design system and customize
              </p>
            </div>
          </button>
        </div>

        {/* Template grid */}
        <div id="template-grid">
          <h3 className="text-[11px] font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-4">
            Templates
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            {DESIGN_SYSTEM_TEMPLATES.map((template) => (
              <TemplateCard
                key={template.id}
                template={template}
                onSelect={handleSelectTemplate}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
