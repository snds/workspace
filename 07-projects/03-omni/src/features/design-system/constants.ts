import type { TokenOutputConfig } from "@/core/context/types";

export const TOKEN_OUTPUT_FORMATS: {
  value: TokenOutputConfig["formats"][number];
  label: string;
  description: string;
}[] = [
  { value: "css-vars", label: "CSS Variables", description: "Custom properties for web" },
  { value: "tailwind-theme", label: "Tailwind Theme", description: "Tailwind config extension" },
  { value: "scss", label: "SCSS", description: "Sass variables and maps" },
  { value: "json-dtcg", label: "JSON (DTCG)", description: "Design Token Community Group format" },
  { value: "swift", label: "Swift", description: "iOS / macOS native colors" },
  { value: "kotlin", label: "Kotlin", description: "Android native colors" },
  { value: "flutter-dart", label: "Dart (Flutter)", description: "Flutter ThemeData colors" },
];
