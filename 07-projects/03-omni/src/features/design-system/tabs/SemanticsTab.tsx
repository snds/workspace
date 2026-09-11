import { useCallback, useMemo } from "react";
import { useNavigate } from "react-router";
import { Layers, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useColorSystemStore } from "@/stores/colorSystem.store";
import { SemanticTokenRow } from "../semantics/SemanticTokenRow";
import type {
  SemanticCategory,
  SemanticToken,
  ColorReference,
} from "@/types/colorSystem";

const CATEGORY_ORDER: SemanticCategory[] = [
  "background",
  "foreground",
  "border",
  "interactive",
  "status",
  "data-visualization",
];

const CATEGORY_LABELS: Record<SemanticCategory, string> = {
  background: "Background",
  foreground: "Foreground",
  border: "Border",
  interactive: "Interactive",
  status: "Status",
  "data-visualization": "Data Visualization",
};

export function SemanticsTab() {
  const navigate = useNavigate();
  const { colorSystem, setColorSystem } = useColorSystemStore();

  const hasTokens = colorSystem !== null;

  const paletteKeys = useMemo(() => {
    if (!colorSystem) return [];
    return Object.keys(colorSystem.palettes);
  }, [colorSystem]);

  const tokensByCategory = useMemo(() => {
    if (!colorSystem?.tokens) return new Map<SemanticCategory, SemanticToken[]>();
    const map = new Map<SemanticCategory, SemanticToken[]>();
    for (const token of colorSystem.tokens) {
      const list = map.get(token.category) ?? [];
      list.push(token);
      map.set(token.category, list);
    }
    return map;
  }, [colorSystem?.tokens]);

  const resolveColor = useCallback(
    (ref: ColorReference, mode: "light" | "dark"): string | null => {
      if (!colorSystem) return null;
      const palette = colorSystem.palettes[ref.paletteKey];
      if (!palette) return null;
      const variant = mode === "light" ? palette.light : palette.dark;
      return variant.steps[ref.step]?.hex ?? null;
    },
    [colorSystem],
  );

  const handleUpdate = useCallback(
    (name: string, mode: "light" | "dark", ref: ColorReference) => {
      if (!colorSystem) return;
      const updated = {
        ...colorSystem,
        tokens: colorSystem.tokens.map((t) => {
          if (t.name !== name) return t;
          return mode === "light"
            ? { ...t, lightValue: ref }
            : { ...t, darkValue: ref };
        }),
      };
      setColorSystem(updated);
    },
    [colorSystem, setColorSystem],
  );

  if (!hasTokens) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <div className="w-12 h-12 rounded-xl border border-dashed border-[var(--mauve-6)] flex items-center justify-center">
          <Layers className="w-6 h-6 text-[var(--mauve-7)]" />
        </div>
        <div className="text-center">
          <p className="text-sm text-[var(--mauve-11)] font-medium">
            Define primitives first
          </p>
          <p className="text-[11px] text-[var(--mauve-9)] mt-1 max-w-xs">
            Semantic tokens reference primitive color scales. Generate or import
            a color system on the Primitives tab to get started.
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => navigate("../primitives", { relative: "path" })}
          className="mt-2 text-[11px]"
        >
          Go to Primitives
          <ArrowRight className="w-3 h-3 ml-1.5" />
        </Button>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-4xl mx-auto px-8 py-6">
        <div className="mb-6">
          <h2 className="text-xs font-semibold text-[var(--mauve-12)]">
            Semantic Tokens
          </h2>
          <p className="text-[10px] text-[var(--mauve-9)] mt-1">
            Map design decisions to primitive palette steps. Each token resolves
            to a different value in light and dark modes.
          </p>
        </div>

        <div className="space-y-6">
          {CATEGORY_ORDER.map((cat) => {
            const tokens = tokensByCategory.get(cat);
            if (!tokens || tokens.length === 0) return null;

            return (
              <div key={cat}>
                <h3 className="text-[10px] font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-2 px-3">
                  {CATEGORY_LABELS[cat]}
                </h3>
                <div className="flex flex-col">
                  {tokens.map((token) => (
                    <SemanticTokenRow
                      key={token.name}
                      token={token}
                      paletteKeys={paletteKeys}
                      resolveColor={resolveColor}
                      onUpdate={handleUpdate}
                    />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
