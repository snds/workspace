import { AnimatePresence, motion } from "framer-motion";
import { useOnboardingStore } from "@/stores/onboarding.store";
import { WelcomeStep } from "./steps/WelcomeStep";
import { TeamContextStep } from "./steps/TeamContextStep";
import { RepositoryStep } from "./steps/RepositoryStep";
import { StepIndicator } from "./components/StepIndicator";
import type { OnboardingStep } from "@/types/onboarding";

const STEPS: Record<OnboardingStep, React.ComponentType> = {
  1: WelcomeStep,
  2: TeamContextStep,
  3: RepositoryStep,
};

const STEP_LABELS: Record<OnboardingStep, string> = {
  1: "Welcome",
  2: "Team Context",
  3: "Repository",
};

export function OnboardingWizard() {
  const { currentStep, completedSteps } = useOnboardingStore();

  const StepComponent = STEPS[currentStep];

  return (
    <div className="min-h-screen bg-[var(--mauve-1)] flex items-center justify-center relative overflow-hidden">
      {/* Ambient glow */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse 60% 50% at 50% 0%, oklch(0.4 0.15 270 / 0.12) 0%, transparent 70%)",
        }}
      />

      {/* Wizard card */}
      <div className="relative w-full max-w-3xl mx-4">
        {/* Step indicator */}
        <div className="mb-6">
          <StepIndicator
            totalSteps={3}
            currentStep={currentStep}
            completedSteps={completedSteps}
            labels={STEP_LABELS}
          />
        </div>

        {/* Step card */}
        <div className="bg-[var(--mauve-2)] border border-[var(--mauve-5)] rounded-xl shadow-2xl overflow-hidden">
          <AnimatePresence mode="wait" initial={false}>
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 24 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -24 }}
              transition={{ duration: 0.2, ease: "easeInOut" }}
            >
              <StepComponent />
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
