import { tauriPlatform } from "./tauri";
import { webPlatform } from "./web";
import type { Platform } from "./types";

// Tauri injects __TAURI_INTERNALS__ into the window object.
// Both tauri.ts and web.ts are bundled, but Tauri-specific code inside
// tauriPlatform uses dynamic imports in function bodies — they only execute
// when the method is called, so they're safe to bundle for web.
const isTauri =
  typeof window !== "undefined" && "__TAURI_INTERNALS__" in window;

// When running inside Tauri, use native fs/dialog/auth but always use the
// web-based AI implementation. The Rust relay requires ANTHROPIC_API_KEY as
// a system env var or OS keychain entry, while the web implementation reads
// VITE_ANTHROPIC_API_KEY from .env — which is simpler and always available.
export const platform: Platform = isTauri
  ? { ...tauriPlatform, ai: webPlatform.ai }
  : webPlatform;
export type { Platform } from "./types";
