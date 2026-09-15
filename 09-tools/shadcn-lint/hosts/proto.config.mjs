/**
 * saas-plm-prototype — consumes @centric/ui. Overlay is error; CI ratchets
 * the current error count. Existing ds:check (control scale) stays a sibling.
 */
import { withHost } from "../with-host.js";

export default withHost({
  ui: "@centric/ui",
  ignores: ["**/docs/**"],
});
