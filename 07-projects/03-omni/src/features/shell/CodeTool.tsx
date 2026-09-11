import { Code } from "lucide-react";

export function CodeTool() {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-3">
      <div className="w-12 h-12 rounded-xl border border-dashed border-[var(--mauve-6)] flex items-center justify-center">
        <Code className="w-6 h-6 text-[var(--mauve-7)]" />
      </div>
      <p className="text-sm text-[var(--mauve-9)]">Coming soon</p>
    </div>
  );
}
