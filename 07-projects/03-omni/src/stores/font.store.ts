import { create } from "zustand";
import { loadFullFont, isGoogleFont } from "@/lib/google-fonts";

// ─── Types ────────────────────────────────────────────────────────────────────

export interface LocalFontVariant {
  id: number;
  style: string;   // "Regular", "Bold Italic", etc.
  weight: number;  // 100–900
  italic: boolean;
  format: string;  // "truetype" | "opentype" | "woff" | "woff2"
}

export interface LocalFont {
  family: string;
  variants: LocalFontVariant[];
}

// ─── Constants ────────────────────────────────────────────────────────────────

export const FONT_SERVER_URL = "http://localhost:37291";

// ─── Store ────────────────────────────────────────────────────────────────────

interface FontState {
  localFonts: LocalFont[];
  isServerRunning: boolean;
  serverChecked: boolean;
}

interface FontActions {
  /** Check if omni-fonts server is running and load local fonts. */
  checkServer(): Promise<void>;
  /** Re-fetch the local font list from the server. */
  refreshLocalFonts(): Promise<void>;
  /**
   * Ensure a font is loaded in the browser — local-server fonts are loaded
   * via FontFace API; Google Fonts are loaded via <link> injection.
   */
  ensureFont(family: string): void;
}

export const useFontStore = create<FontState & FontActions>()((set, get) => ({
  localFonts: [],
  isServerRunning: false,
  serverChecked: false,

  async checkServer() {
    try {
      const res = await fetch(`${FONT_SERVER_URL}/`, {
        signal: AbortSignal.timeout(1500),
      });
      if (res.ok) {
        set({ isServerRunning: true, serverChecked: true });
        await get().refreshLocalFonts();
      } else {
        set({ isServerRunning: false, serverChecked: true });
      }
    } catch {
      set({ isServerRunning: false, serverChecked: true });
    }
  },

  async refreshLocalFonts() {
    if (!get().isServerRunning) return;
    try {
      const res = await fetch(`${FONT_SERVER_URL}/fonts`);
      if (!res.ok) return;
      const flat: Array<{ id: number; family: string; style: string; weight: number; italic: boolean; format: string }> =
        await res.json();

      // Group by family
      const map = new Map<string, LocalFont>();
      for (const item of flat) {
        if (!map.has(item.family)) map.set(item.family, { family: item.family, variants: [] });
        map.get(item.family)!.variants.push({
          id: item.id,
          style: item.style,
          weight: item.weight,
          italic: item.italic,
          format: item.format,
        });
      }
      set({ localFonts: Array.from(map.values()) });
    } catch {
      set({ isServerRunning: false });
    }
  },

  ensureFont(family: string) {
    const localFont = get().localFonts.find((f) => f.family === family);
    if (localFont) {
      // Load all variants via FontFace API
      for (const variant of localFont.variants) {
        _loadLocalVariantInBrowser(variant, family);
      }
    } else if (isGoogleFont(family)) {
      loadFullFont(family);
    }
  },
}));

// ─── Internal: load a local font variant via FontFace API ─────────────────────

const _browserLoaded = new Set<string>();

async function _loadLocalVariantInBrowser(variant: LocalFontVariant, family: string) {
  const key = `${family}-${variant.weight}-${variant.italic}`;
  if (_browserLoaded.has(key)) return;
  _browserLoaded.add(key);

  try {
    const fontFace = new FontFace(
      family,
      `url(${FONT_SERVER_URL}/font/${variant.id})`,
      {
        weight: String(variant.weight),
        style: variant.italic ? "italic" : "normal",
      },
    );
    const loaded = await fontFace.load();
    document.fonts.add(loaded);
  } catch (err) {
    _browserLoaded.delete(key); // allow retry
    console.warn(`[omni-fonts] Failed to load ${family} ${variant.style}:`, err);
  }
}
