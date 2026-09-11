import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";
import type { CodeFormat } from "@/types/colorSystem";
import { CODE_FORMATS } from "@/types/colorSystem";

export function CodeFormatSelector({
  value,
  onChange,
}: {
  value: CodeFormat;
  onChange: (fmt: CodeFormat) => void;
}) {
  const [open, setOpen] = useState(false);
  const current = CODE_FORMATS.find((f) => f.value === value);

  return (
    <div className="relative">
      <label className="text-[10px] font-semibold text-[var(--mauve-10)] uppercase tracking-wider block mb-1.5">
        Code Format
      </label>
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between bg-[var(--mauve-3)] border border-[var(--mauve-5)] rounded-md px-3 py-1.5 text-xs text-[var(--mauve-12)] hover:border-[var(--violet-7)] transition-colors"
      >
        <span className="font-mono text-[10px]">{current?.label ?? value}</span>
        <ChevronDown className={cn("w-3 h-3 text-[var(--mauve-9)] transition-transform", open && "rotate-180")} />
      </button>
      {open && (
        <div className="absolute z-30 mt-1 w-full bg-[var(--mauve-3)] border border-[var(--mauve-5)] rounded-md shadow-lg overflow-hidden">
          {CODE_FORMATS.map((fmt) => (
            <button
              key={fmt.value}
              onClick={() => { onChange(fmt.value); setOpen(false); }}
              className={cn(
                "w-full text-left px-3 py-1.5 text-[10px] hover:bg-[var(--mauve-4)] transition-colors flex items-center justify-between",
                fmt.value === value
                  ? "text-[var(--violet-11)] bg-[var(--mauve-4)]"
                  : "text-[var(--mauve-11)]"
              )}
            >
              <span className="font-mono">{fmt.label}</span>
              <span className="text-[8px] text-[var(--mauve-8)] font-mono">{fmt.example}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
