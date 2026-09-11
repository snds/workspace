import { useState } from "react";
import { Settings2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { useOnboardingStore } from "@/stores/onboarding.store";
import { useTeamContextStore } from "@/stores/teamContext.store";
import { WizardNavButtons } from "../components/WizardNavButtons";
import {
  TeamContextCard,
  type TeamContextPreset,
} from "../components/TeamContextCard";
import { ContextDimensionEditor } from "../components/ContextDimensionEditor";

// ─── Preset Definitions ──────────────────────────────────────────────────────

const PRESETS: TeamContextPreset[] = [
  {
    id: "design-only",
    name: "Design Only",
    description:
      "Colors, tokens, and visual design. No framework configuration.",
    tier: 0,
    icon: "\uD83C\uDFA8",
  },
  {
    id: "next-shadcn",
    name: "Next.js + shadcn",
    description:
      "React 19, Next.js, Tailwind CSS, shadcn/ui, Lucide icons.",
    tier: 1,
    icon: "\u25B2",
  },
  {
    id: "vue-vuetify",
    name: "Vue + Vuetify",
    description:
      "Vue 3, Nuxt, Vuetify component library, SCSS styling.",
    tier: 1,
    icon: "\uD83D\uDFE2",
  },
  {
    id: "svelte-skeleton",
    name: "SvelteKit",
    description:
      "Svelte 5, SvelteKit, Tailwind CSS, Lucide icons.",
    tier: 1,
    icon: "\uD83D\uDD36",
  },
  {
    id: "react-native",
    name: "React Native",
    description:
      "React Native with Expo, NativeWind, Phosphor icons.",
    tier: 1,
    icon: "\uD83D\uDCF1",
  },
  {
    id: "custom",
    name: "Custom",
    description:
      "Configure every dimension of your team's stack manually.",
    tier: 1,
    icon: "\u2699\uFE0F",
  },
];

// ─── Step Component ──────────────────────────────────────────────────────────

export function TeamContextStep() {
  const { nextStep, markStepComplete } = useOnboardingStore();
  const { presetId, applyPreset } = useTeamContextStore();

  const [selectedId, setSelectedId] = useState<string | null>(
    presetId ?? null,
  );
  const [showCustomEditor, setShowCustomEditor] = useState(
    presetId === null || presetId === "custom",
  );

  const handleSelect = (id: string) => {
    setSelectedId(id);
    if (id === "custom") {
      setShowCustomEditor(true);
      // Don't apply a preset for custom — user will configure manually
    } else {
      setShowCustomEditor(false);
      applyPreset(id);
    }
  };

  const handleContinue = () => {
    markStepComplete(2);
    nextStep();
  };

  const canContinue = selectedId !== null;

  return (
    <div className="flex flex-col">
      {/* Header */}
      <div className="px-8 pt-8 pb-5 border-b border-[var(--mauve-4)]">
        <div className="flex items-center gap-2 mb-2">
          <Badge
            variant="outline"
            className="text-[10px] border-[var(--violet-7)] text-[var(--violet-11)] bg-[var(--violet-2)]"
          >
            <Settings2 className="w-3 h-3 mr-1" />
            Team Context
          </Badge>
        </div>
        <h2 className="text-xl font-bold text-[var(--mauve-12)]">
          Configure your team context
        </h2>
        <p className="text-sm text-[var(--mauve-10)] mt-2">
          Select a preset that matches your team's stack, or build a custom
          configuration. This tells Omni how to generate code and tokens.
        </p>
      </div>

      {/* Body */}
      <div className="px-8 py-6 flex flex-col gap-5">
        {/* Preset grid */}
        <div>
          <label className="text-xs font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-3 block">
            Choose a preset
          </label>
          <div className="grid grid-cols-3 gap-2">
            {PRESETS.map((preset) => (
              <TeamContextCard
                key={preset.id}
                preset={preset}
                selected={selectedId === preset.id}
                onSelect={() => handleSelect(preset.id)}
              />
            ))}
          </div>
        </div>

        {/* Custom editor (inline, expanded when "Custom" is selected) */}
        {showCustomEditor && (
          <div
            className={cn(
              "border border-[var(--mauve-5)] rounded-lg bg-[var(--mauve-2)] p-4",
              "animate-in fade-in-0 slide-in-from-top-2 duration-200",
            )}
          >
            <div className="flex items-center gap-2 mb-4">
              <Settings2 className="w-3.5 h-3.5 text-[var(--violet-11)]" />
              <h3 className="text-xs font-semibold text-[var(--mauve-12)]">
                Custom Configuration
              </h3>
            </div>
            <ContextDimensionEditor />
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-8 pb-8">
        <WizardNavButtons
          canContinue={canContinue}
          onContinue={handleContinue}
          showSkip
        />
      </div>
    </div>
  );
}
