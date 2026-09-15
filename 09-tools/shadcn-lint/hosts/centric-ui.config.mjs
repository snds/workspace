/**
 * centric-ui — consumes @centric/ui. Overlay is error; CI ratchets the
 * current error count so app-level cds-* / palette debt cannot grow.
 */
import { withHost } from "../with-host.js";

export default withHost({
  ui: "@centric/ui",
  ignores: ["**/figma-repo-sync-plugin/**", "**/app/api/generated/**"],
});
