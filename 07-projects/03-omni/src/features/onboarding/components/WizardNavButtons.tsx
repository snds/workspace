import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useOnboardingStore } from "@/stores/onboarding.store";
import { cn } from "@/lib/utils";

interface WizardNavButtonsProps {
  canContinue?: boolean;
  onContinue?: () => void;
  showSkip?: boolean;
  onSkip?: () => void;
  continueLabel?: string;
  isLoading?: boolean;
  className?: string;
}

export function WizardNavButtons({
  canContinue = true,
  onContinue,
  showSkip = false,
  onSkip,
  continueLabel = "Continue",
  isLoading = false,
  className,
}: WizardNavButtonsProps) {
  const { currentStep, prevStep, nextStep, markStepComplete } = useOnboardingStore();

  const handleContinue = () => {
    if (onContinue) {
      onContinue();
    } else {
      markStepComplete(currentStep);
      nextStep();
    }
  };

  const handleSkip = () => {
    if (onSkip) {
      onSkip();
    }
    markStepComplete(currentStep);
    nextStep();
  };

  return (
    <div className={cn("flex items-center justify-between", className)}>
      {/* Back */}
      <Button
        variant="ghost"
        size="sm"
        onClick={prevStep}
        disabled={currentStep === 1}
        className="gap-1.5 text-[var(--mauve-10)] hover:text-[var(--mauve-12)] disabled:opacity-30"
      >
        <ChevronLeft className="w-3.5 h-3.5" />
        Back
      </Button>

      <div className="flex items-center gap-2">
        {/* Skip */}
        {showSkip && (
          <Button
            variant="ghost"
            size="sm"
            onClick={handleSkip}
            className="text-[var(--mauve-9)] hover:text-[var(--mauve-11)]"
          >
            Skip for now
          </Button>
        )}

        {/* Continue */}
        <Button
          size="sm"
          onClick={handleContinue}
          disabled={!canContinue || isLoading}
          className="gap-1.5 bg-[var(--violet-9)] hover:bg-[var(--violet-10)] text-white border-0 disabled:opacity-40"
        >
          {isLoading ? (
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 border border-white/30 border-t-white rounded-full animate-spin" />
              Generating…
            </span>
          ) : (
            <>
              {continueLabel}
              <ChevronRight className="w-3.5 h-3.5" />
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
