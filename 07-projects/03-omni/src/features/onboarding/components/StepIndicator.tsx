import { Check } from "lucide-react";
import { cn } from "@/lib/utils";
import type { OnboardingStep } from "@/types/onboarding";

interface StepIndicatorProps {
  totalSteps: number;
  currentStep: OnboardingStep;
  completedSteps: OnboardingStep[];
  labels: Record<OnboardingStep, string>;
}

export function StepIndicator({
  totalSteps,
  currentStep,
  completedSteps,
  labels,
}: StepIndicatorProps) {
  return (
    <div className="flex items-center justify-center gap-0">
      {Array.from({ length: totalSteps }, (_, i) => {
        const step = (i + 1) as OnboardingStep;
        const isCompleted = completedSteps.includes(step);
        const isCurrent = step === currentStep;
        const isPast = step < currentStep;

        return (
          <div key={step} className="flex items-center">
            {/* Step node */}
            <div className="flex flex-col items-center gap-1.5">
              <div
                className={cn(
                  "w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold transition-all duration-300",
                  isCompleted || isPast
                    ? "bg-[var(--violet-9)] text-white"
                    : isCurrent
                    ? "bg-[var(--mauve-4)] border-2 border-[var(--violet-9)] text-[var(--violet-11)]"
                    : "bg-[var(--mauve-3)] border border-[var(--mauve-6)] text-[var(--mauve-9)]"
                )}
              >
                {isCompleted || isPast ? (
                  <Check className="w-3.5 h-3.5" />
                ) : (
                  step
                )}
              </div>
              <span
                className={cn(
                  "text-[10px] font-medium whitespace-nowrap",
                  isCurrent
                    ? "text-[var(--mauve-12)]"
                    : "text-[var(--mauve-9)]"
                )}
              >
                {labels[step]}
              </span>
            </div>

            {/* Connector line */}
            {i < totalSteps - 1 && (
              <div
                className={cn(
                  "h-px w-16 mb-5 mx-1 transition-all duration-300",
                  isPast || isCompleted
                    ? "bg-[var(--violet-7)]"
                    : "bg-[var(--mauve-5)]"
                )}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
