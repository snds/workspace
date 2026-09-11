import { useEffect, useRef } from "react";
import { PrimitivesSidebar } from "../primitives/PrimitivesSidebar";
import { ColorsSection } from "../primitives/ColorsSection";
import { TypographySection } from "../primitives/TypographySection";
import { SpaceSection } from "../primitives/SpaceSection";
import { EffectsSection } from "../primitives/EffectsSection";
import { RadiusSection } from "../primitives/RadiusSection";
import { IconographySection } from "../primitives/IconographySection";
import { AnimationsSection } from "../primitives/AnimationsSection";
import { useDesignSystemUIStore } from "@/stores/designSystemUI.store";

const SECTION_IDS = [
  "colors",
  "colors-brand",
  "colors-scales",
  "colors-dataviz",
  "typography",
  "typography-size",
  "typography-family",
  "typography-weight",
  "typography-lineheight",
  "typography-tracking",
  "iconography",
  "space",
  "effects",
  "effects-shadow",
  "effects-blur",
  "effects-opacity",
  "radius",
  "animations",
];

export function PrimitivesTab() {
  const scrollRef = useRef<HTMLDivElement>(null);
  const setActive = useDesignSystemUIStore((s) => s.setActivePrimitiveCategory);

  // Scroll-spy via IntersectionObserver
  useEffect(() => {
    const root = scrollRef.current;
    if (!root) return;

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            const id = entry.target.id.replace("section-", "");
            setActive(id);
            break;
          }
        }
      },
      { root, rootMargin: "-10% 0px -80% 0px", threshold: 0 },
    );

    for (const id of SECTION_IDS) {
      const el = document.getElementById(`section-${id}`);
      if (el) observer.observe(el);
    }

    return () => observer.disconnect();
  }, [setActive]);

  return (
    <div className="flex h-full">
      <PrimitivesSidebar />

      <div className="flex-1 min-h-0 relative">
        <div ref={scrollRef} className="absolute inset-0 overflow-y-auto">
          <div className="px-8 py-6 space-y-12">
            {/* Colors */}
            <section id="section-colors" className="scroll-mt-4">
              <h2 className="text-xs font-semibold text-[var(--mauve-12)] mb-4">Colors</h2>
              <ColorsSection />
            </section>

            {/* Typography */}
            <section id="section-typography" className="scroll-mt-4">
              <h2 className="text-xs font-semibold text-[var(--mauve-12)] mb-4">Typography</h2>
              <TypographySection />
            </section>

            {/* Iconography */}
            <IconographySection />

            {/* Space */}
            <SpaceSection />

            {/* Effects */}
            <section id="section-effects" className="scroll-mt-4">
              <h2 className="text-xs font-semibold text-[var(--mauve-12)] mb-4">Effects</h2>
              <EffectsSection />
            </section>

            {/* Radius */}
            <RadiusSection />

            {/* Animations */}
            <AnimationsSection />
          </div>
        </div>
      </div>
    </div>
  );
}
