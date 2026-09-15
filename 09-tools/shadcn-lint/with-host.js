/**
 * Wrap eslint.ds.config.mjs for one product repo.
 * Hosts must keep ds-lint/no-tier-leakage at error (probe checks the base file).
 */
import { defineConfig, globalIgnores } from "eslint/config";
import base from "./eslint.ds.config.mjs";

const SHARED_IGNORES = [
  "**/node_modules/**",
  "**/dist/**",
  "**/build/**",
  "**/.next/**",
  "**/out/**",
  "**/vendor/**",
  "**/storybook-static/**",
  "**/canvases/**",
];

export function withHost({ ui, ignores = [] }) {
  return defineConfig([
    globalIgnores([...SHARED_IGNORES, ...ignores]),
    ...base.map((block) => {
      if (!block.settings?.shadcn) return block;
      return {
        ...block,
        settings: {
          ...block.settings,
          shadcn: {
            ...block.settings.shadcn,
            ui,
          },
        },
      };
    }),
  ]);
}
