import type { SemanticToken, ColorReference, RadixStep } from "@/types/colorSystem";

interface SemanticTokenRowProps {
  token: SemanticToken;
  paletteKeys: string[];
  resolveColor: (ref: ColorReference, mode: "light" | "dark") => string | null;
  onUpdate: (name: string, mode: "light" | "dark", ref: ColorReference) => void;
}

const STEPS: RadixStep[] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];

export function SemanticTokenRow({
  token,
  paletteKeys,
  resolveColor,
  onUpdate,
}: SemanticTokenRowProps) {
  const lightHex = resolveColor(token.lightValue, "light");
  const darkHex = resolveColor(token.darkValue, "dark");

  return (
    <div className="flex items-center gap-3 py-2 px-3 rounded hover:bg-[var(--mauve-3)] transition-colors">
      {/* Token name */}
      <div className="w-52 flex-shrink-0">
        <span className="text-[10px] font-mono text-[var(--mauve-11)] block truncate">
          {token.name}
        </span>
        <span className="text-[9px] text-[var(--mauve-9)]">
          {token.description}
        </span>
      </div>

      {/* Light swatch + selector */}
      <div className="flex items-center gap-2 flex-1">
        <div
          className="w-6 h-6 rounded border border-[var(--mauve-5)] flex-shrink-0"
          style={{ backgroundColor: lightHex ?? "transparent" }}
        />
        <select
          value={`${token.lightValue.paletteKey}:${token.lightValue.step}`}
          onChange={(e) => {
            const [pk, step] = e.target.value.split(":");
            onUpdate(token.name, "light", { paletteKey: pk, step: Number(step) as RadixStep });
          }}
          className="text-[9px] bg-[var(--mauve-3)] border border-[var(--mauve-5)] rounded px-1.5 py-0.5 text-[var(--mauve-11)] min-w-0"
        >
          {paletteKeys.map((pk) =>
            STEPS.map((step) => (
              <option key={`${pk}:${step}`} value={`${pk}:${step}`}>
                {pk}.{step}
              </option>
            ))
          )}
        </select>
        <span className="text-[8px] text-[var(--mauve-8)] flex-shrink-0">Light</span>
      </div>

      {/* Dark swatch + selector */}
      <div className="flex items-center gap-2 flex-1">
        <div
          className="w-6 h-6 rounded border border-[var(--mauve-5)] flex-shrink-0"
          style={{ backgroundColor: darkHex ?? "transparent" }}
        />
        <select
          value={`${token.darkValue.paletteKey}:${token.darkValue.step}`}
          onChange={(e) => {
            const [pk, step] = e.target.value.split(":");
            onUpdate(token.name, "dark", { paletteKey: pk, step: Number(step) as RadixStep });
          }}
          className="text-[9px] bg-[var(--mauve-3)] border border-[var(--mauve-5)] rounded px-1.5 py-0.5 text-[var(--mauve-11)] min-w-0"
        >
          {paletteKeys.map((pk) =>
            STEPS.map((step) => (
              <option key={`${pk}:${step}`} value={`${pk}:${step}`}>
                {pk}.{step}
              </option>
            ))
          )}
        </select>
        <span className="text-[8px] text-[var(--mauve-8)] flex-shrink-0">Dark</span>
      </div>
    </div>
  );
}
