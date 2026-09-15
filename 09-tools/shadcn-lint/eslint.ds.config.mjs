/**
 * Canonical lint:ds config. Copy this file into the product repo and point
 * `npm run lint:ds` at it. Do not extend design-system.lint.json without this
 * overlay — stock shadcn/no-raw-colors false-greens declared @theme names
 * such as bg-cds-blue-500 (CDS semantic.css @theme inline).
 *
 * Change settings.shadcn.ui to the product's component import prefix
 * (@centric/ui, @/ds, @workspace/ui/components).
 */
import { plugin as shadcn } from "@shadcn/lint"
import tsParser from "@typescript-eslint/parser"
import { defineConfig } from "eslint/config"
import policy from "./design-system.lint.json" with { type: "json" }
import dsLint from "./index.js"

export default defineConfig([
  {
    files: ["**/*.{js,jsx,ts,tsx}"],
    linterOptions: {
      noInlineConfig: true,
      reportUnusedDisableDirectives: "off",
    },
    languageOptions: {
      parser: tsParser,
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
    plugins: { shadcn, "ds-lint": dsLint },
    settings: {
      shadcn: {
        ui: "@/components/ui",
        note: "Author in semantic tokens (bg-primary, text-muted-foreground). Primitive hue steps, shade aliases, and cds-* compat classes belong in CSS token files only.",
      },
    },
    rules: {
      ...policy.rules,
      "ds-lint/no-tier-leakage": "error",
    },
  },
  ...policy.overrides,
])
