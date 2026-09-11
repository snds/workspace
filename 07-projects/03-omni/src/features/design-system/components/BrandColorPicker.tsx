import { useState, useEffect } from "react";
import { isValidHex } from "@/lib/color";
import { cn } from "@/lib/utils";

export function BrandColorPicker({
  label,
  value,
  onChange,
  required,
}: {
  label: string;
  value: string | null;
  onChange: (hex: string | null) => void;
  required?: boolean;
}) {
  const [inputVal, setInputVal] = useState(value ?? "");
  const valid = inputVal === "" ? !required : isValidHex(inputVal);

  // Sync when value changes externally (e.g. from harmony suggestion chip)
  useEffect(() => {
    setInputVal(value ?? "");
  }, [value]);

  const handleInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const v = e.target.value;
    setInputVal(v);
    if (v === "" && !required) {
      onChange(null);
    } else if (isValidHex(v)) {
      onChange(v);
    }
  };

  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-[10px] font-semibold text-[var(--mauve-10)] uppercase tracking-wider">
        {label} {!required && <span className="font-normal normal-case">(optional)</span>}
      </label>
      <div className="flex items-center gap-2">
        <div className="relative">
          <input
            type="color"
            value={isValidHex(inputVal) ? inputVal : "#7c6af7"}
            onChange={(e) => {
              setInputVal(e.target.value);
              onChange(e.target.value);
            }}
            className="absolute inset-0 opacity-0 w-full h-full cursor-pointer rounded-md"
          />
          <div
            className="w-8 h-8 rounded-md border border-[var(--mauve-6)] cursor-pointer flex-shrink-0"
            style={{ background: isValidHex(inputVal) ? inputVal : "var(--mauve-5)" }}
          />
        </div>
        <input
          value={inputVal}
          onChange={handleInput}
          placeholder="#7c6af7"
          className={cn(
            "flex-1 bg-[var(--mauve-3)] border rounded-md px-3 py-1.5 text-xs font-mono text-[var(--mauve-12)] placeholder:text-[var(--mauve-8)] focus:outline-none transition-colors",
            valid
              ? "border-[var(--mauve-5)] focus:border-[var(--violet-7)]"
              : "border-[var(--red-9)] focus:border-[var(--red-9)]"
          )}
        />
      </div>
    </div>
  );
}
