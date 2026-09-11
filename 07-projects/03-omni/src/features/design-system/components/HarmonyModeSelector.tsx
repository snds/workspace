import { cn } from "@/lib/utils";
import type { HarmonyMode } from "@/lib/colorHarmony";

interface HarmonyModeSelectorProps {
  value: HarmonyMode;
  onChange: (mode: HarmonyMode) => void;
}

interface ModeOption {
  mode: HarmonyMode;
  label: string;
  description: string;
  icon: React.ReactNode;
}

/** Small inline SVG icons for each harmony type */
function FreeformIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
      <circle cx="7" cy="7" r="2" />
      <line x1="7" y1="1" x2="7" y2="4" />
      <line x1="7" y1="10" x2="7" y2="13" />
      <line x1="1" y1="7" x2="4" y2="7" />
      <line x1="10" y1="7" x2="13" y2="7" />
    </svg>
  );
}

function AnalogousIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
      <line x1="7" y1="7" x2="3" y2="2" />
      <line x1="7" y1="7" x2="7" y2="1" />
      <line x1="7" y1="7" x2="11" y2="2" />
    </svg>
  );
}

function ComplementaryIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
      <line x1="3" y1="3" x2="11" y2="11" />
      <circle cx="3" cy="3" r="1.5" fill="currentColor" />
      <circle cx="11" cy="11" r="1.5" fill="currentColor" />
    </svg>
  );
}

function TriadicIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round">
      <polygon points="7,1.5 1.5,11 12.5,11" />
    </svg>
  );
}

function SplitCompIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
      <line x1="7" y1="2" x2="7" y2="7" />
      <line x1="7" y1="7" x2="3" y2="12" />
      <line x1="7" y1="7" x2="11" y2="12" />
    </svg>
  );
}

function MonochromaticIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
      <line x1="7" y1="2" x2="7" y2="12" />
      <circle cx="7" cy="4" r="1.5" fill="currentColor" opacity="0.3" />
      <circle cx="7" cy="7" r="1.5" fill="currentColor" opacity="0.6" />
      <circle cx="7" cy="10" r="1.5" fill="currentColor" />
    </svg>
  );
}

const MODES: ModeOption[] = [
  { mode: "freeform", label: "Free", description: "All colors independently adjustable", icon: <FreeformIcon /> },
  { mode: "analogous", label: "Analog", description: "Adjacent hues (+/-30°)", icon: <AnalogousIcon /> },
  { mode: "complementary", label: "Comp", description: "Opposite on wheel (180°)", icon: <ComplementaryIcon /> },
  { mode: "triadic", label: "Triad", description: "Evenly spaced triad (+/-120°)", icon: <TriadicIcon /> },
  { mode: "split-complementary", label: "Split", description: "Near-opposites (+/-150°)", icon: <SplitCompIcon /> },
  { mode: "monochromatic", label: "Mono", description: "Same hue, varied lightness", icon: <MonochromaticIcon /> },
];

export function HarmonyModeSelector({ value, onChange }: HarmonyModeSelectorProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-[10px] font-semibold text-[var(--mauve-10)] uppercase tracking-wider">
        Harmony
      </label>
      <div className="grid grid-cols-6 gap-0.5 rounded-lg border border-[var(--mauve-5)] overflow-hidden">
        {MODES.map((opt) => (
          <button
            key={opt.mode}
            onClick={() => onChange(opt.mode)}
            title={`${opt.label}: ${opt.description}`}
            className={cn(
              "flex flex-col items-center gap-0.5 py-1.5 text-[8px] transition-colors",
              value === opt.mode
                ? "bg-[var(--mauve-4)] text-[var(--mauve-12)]"
                : "text-[var(--mauve-9)] hover:text-[var(--mauve-11)] hover:bg-[var(--mauve-3)]",
            )}
          >
            {opt.icon}
            <span className="leading-none">{opt.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
