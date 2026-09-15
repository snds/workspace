/**
 * CDS (cpes-software/cds) — published packages must be clean.
 * MDX + foundation stories document the cds-* compat alias; they are ignored.
 * Home swatches that demonstrate the alias are ignored. Live package TSX is not.
 */
import { withHost } from "../with-host.js";

export default withHost({
  ui: "@centric/ui",
  ignores: [
    "apps/**",
    "**/*.mdx",
    "**/*.test.ts",
    "**/*.test.tsx",
    "**/*.stories.tsx",
  ],
});
