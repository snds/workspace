import { Blocks, GitBranch, Palette, FolderOpen, Plus } from "lucide-react";
import omniLogo from "@/assets/omni-logo.svg";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { useOnboardingStore } from "@/stores/onboarding.store";
import { WizardNavButtons } from "../components/WizardNavButtons";
import type { Persona, ProjectMode } from "@/types/onboarding";
import { platform } from "@/platform";

// ── Persona Card ───────────────────────────────────────────────────────────

const PERSONAS: {
  id: Persona;
  label: string;
  description: string;
  Icon: React.ComponentType<{ className?: string }>;
}[] = [
  {
    id: "design-system-maintainer",
    label: "Design System Maintainer",
    description: "Build and maintain shared component libraries, tokens, and documentation.",
    Icon: Blocks,
  },
  {
    id: "ux-designer",
    label: "UX Designer",
    description: "Design user flows, wireframes, and information architecture.",
    Icon: GitBranch,
  },
  {
    id: "ui-designer",
    label: "UI Designer",
    description: "Craft visual design, style guides, and polished interfaces.",
    Icon: Palette,
  },
];

function PersonaCard({
  id: _id,
  label,
  description,
  Icon,
  selected,
  onClick,
}: (typeof PERSONAS)[number] & { selected: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex flex-col gap-3 p-4 rounded-lg border text-left transition-all duration-150 cursor-pointer",
        selected
          ? "border-[var(--violet-7)] bg-[var(--violet-3)] ring-1 ring-[var(--violet-7)]"
          : "border-[var(--mauve-5)] bg-[var(--mauve-3)] hover:border-[var(--mauve-6)] hover:bg-[var(--mauve-4)]"
      )}
    >
      <div
        className={cn(
          "w-8 h-8 rounded-md flex items-center justify-center",
          selected ? "bg-[var(--violet-5)]" : "bg-[var(--mauve-4)]"
        )}
      >
        <Icon
          className={cn(
            "w-4 h-4",
            selected ? "text-[var(--violet-11)]" : "text-[var(--mauve-10)]"
          )}
        />
      </div>
      <div>
        <p
          className={cn(
            "text-xs font-semibold leading-tight",
            selected ? "text-[var(--violet-12)]" : "text-[var(--mauve-12)]"
          )}
        >
          {label}
        </p>
        <p
          className={cn(
            "text-[10px] mt-1 leading-relaxed",
            selected ? "text-[var(--violet-11)]" : "text-[var(--mauve-9)]"
          )}
        >
          {description}
        </p>
      </div>
    </button>
  );
}

// ── Project Mode Card ──────────────────────────────────────────────────────

function ProjectModeCard({
  mode,
  label,
  description,
  Icon,
  selected,
  onClick,
}: {
  mode: ProjectMode;
  label: string;
  description: string;
  Icon: React.ComponentType<{ className?: string }>;
  selected: boolean;
  onClick: () => void;
}) {
  void mode;
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 p-3 rounded-lg border text-left transition-all duration-150 cursor-pointer flex-1",
        selected
          ? "border-[var(--violet-7)] bg-[var(--violet-3)] ring-1 ring-[var(--violet-7)]"
          : "border-[var(--mauve-5)] bg-[var(--mauve-3)] hover:border-[var(--mauve-6)] hover:bg-[var(--mauve-4)]"
      )}
    >
      <div
        className={cn(
          "w-8 h-8 rounded-md flex items-center justify-center flex-shrink-0",
          selected ? "bg-[var(--violet-5)]" : "bg-[var(--mauve-4)]"
        )}
      >
        <Icon
          className={cn(
            "w-4 h-4",
            selected ? "text-[var(--violet-11)]" : "text-[var(--mauve-10)]"
          )}
        />
      </div>
      <div className="min-w-0">
        <p
          className={cn(
            "text-xs font-semibold",
            selected ? "text-[var(--violet-12)]" : "text-[var(--mauve-12)]"
          )}
        >
          {label}
        </p>
        <p
          className={cn(
            "text-[10px] mt-0.5",
            selected ? "text-[var(--violet-11)]" : "text-[var(--mauve-9)]"
          )}
        >
          {description}
        </p>
      </div>
    </button>
  );
}

// ── Step ───────────────────────────────────────────────────────────────────

export function WelcomeStep() {
  const {
    persona,
    projectMode,
    projectName,
    setPersona,
    setProjectMode,
    setProjectName,
    nextStep,
    markStepComplete,
  } = useOnboardingStore();

  const canContinue = persona !== null && projectMode !== null && projectName.trim().length > 0;

  const handleOpenExisting = async () => {
    const path = await platform.dialog.openDirectory();
    if (path) {
      setProjectMode("open-existing");
    }
  };

  const handleContinue = () => {
    markStepComplete(1);
    nextStep();
  };

  return (
    <div className="flex flex-col">
      {/* Header */}
      <div className="px-8 pt-8 pb-6 border-b border-[var(--mauve-4)]">
        <div className="flex items-center gap-2 mb-4">
          <img src={omniLogo} alt="Omni" className="w-6 h-6" />
          <span className="text-sm font-semibold text-[var(--mauve-11)]">Omni</span>
        </div>
        <h1 className="text-2xl font-bold text-[var(--mauve-12)] leading-tight">
          Welcome. What are you building?
        </h1>
        <p className="text-sm text-[var(--mauve-10)] mt-2">
          Tell us a bit about your role so Omni can configure the right workflow for you.
        </p>
      </div>

      {/* Body */}
      <div className="px-8 py-6 flex flex-col gap-6">
        {/* Persona selection */}
        <div>
          <label className="text-xs font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-3 block">
            Your role
          </label>
          <div className="grid grid-cols-3 gap-2">
            {PERSONAS.map((p) => (
              <PersonaCard
                key={p.id}
                {...p}
                selected={persona === p.id}
                onClick={() => setPersona(p.id)}
              />
            ))}
          </div>
        </div>

        {/* Project name */}
        <div>
          <label className="text-xs font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-2 block">
            Project name
          </label>
          <Input
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            placeholder="My Design System"
            className="bg-[var(--mauve-3)] border-[var(--mauve-5)] focus:border-[var(--violet-7)] text-[var(--mauve-12)] placeholder:text-[var(--mauve-8)]"
          />
        </div>

        {/* Project mode */}
        <div>
          <label className="text-xs font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-3 block">
            What would you like to do?
          </label>
          <div className="flex gap-2">
            <ProjectModeCard
              mode="new-design-system"
              label="New design system"
              description="Start from scratch with AI guidance."
              Icon={Plus}
              selected={projectMode === "new-design-system"}
              onClick={() => setProjectMode("new-design-system")}
            />
            <ProjectModeCard
              mode="open-existing"
              label="Open existing project"
              description="Import a repository or local directory."
              Icon={FolderOpen}
              selected={projectMode === "open-existing"}
              onClick={handleOpenExisting}
            />
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="px-8 pb-8">
        <WizardNavButtons
          canContinue={canContinue}
          onContinue={handleContinue}
        />
      </div>
    </div>
  );
}
