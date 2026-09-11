// ─── Static Google Fonts catalog ─────────────────────────────────────────────
// Top ~120 popular Google Fonts, grouped by category.

export type FontCategory =
  | "sans-serif"
  | "serif"
  | "display"
  | "monospace"
  | "handwriting";

export interface GoogleFont {
  family: string;
  category: FontCategory;
}

export const GOOGLE_FONTS: GoogleFont[] = [
  // ── Sans-serif ──────────────────────────────────────────────────────────────
  { family: "Inter", category: "sans-serif" },
  { family: "Roboto", category: "sans-serif" },
  { family: "Open Sans", category: "sans-serif" },
  { family: "Lato", category: "sans-serif" },
  { family: "Montserrat", category: "sans-serif" },
  { family: "Poppins", category: "sans-serif" },
  { family: "Source Sans 3", category: "sans-serif" },
  { family: "Raleway", category: "sans-serif" },
  { family: "Noto Sans", category: "sans-serif" },
  { family: "Nunito", category: "sans-serif" },
  { family: "Nunito Sans", category: "sans-serif" },
  { family: "Work Sans", category: "sans-serif" },
  { family: "Mulish", category: "sans-serif" },
  { family: "Fira Sans", category: "sans-serif" },
  { family: "Rubik", category: "sans-serif" },
  { family: "Karla", category: "sans-serif" },
  { family: "DM Sans", category: "sans-serif" },
  { family: "Outfit", category: "sans-serif" },
  { family: "Barlow", category: "sans-serif" },
  { family: "Jost", category: "sans-serif" },
  { family: "Manrope", category: "sans-serif" },
  { family: "Plus Jakarta Sans", category: "sans-serif" },
  { family: "Sora", category: "sans-serif" },
  { family: "Figtree", category: "sans-serif" },
  { family: "Be Vietnam Pro", category: "sans-serif" },
  { family: "Ubuntu", category: "sans-serif" },
  { family: "PT Sans", category: "sans-serif" },
  { family: "Cabin", category: "sans-serif" },
  { family: "Josefin Sans", category: "sans-serif" },
  { family: "Quicksand", category: "sans-serif" },
  { family: "Hind", category: "sans-serif" },
  { family: "Exo 2", category: "sans-serif" },
  { family: "Oxygen", category: "sans-serif" },
  { family: "Mukta", category: "sans-serif" },
  { family: "Libre Franklin", category: "sans-serif" },
  { family: "Overpass", category: "sans-serif" },
  { family: "Assistant", category: "sans-serif" },
  { family: "Varela Round", category: "sans-serif" },
  { family: "Albert Sans", category: "sans-serif" },
  { family: "Lexend", category: "sans-serif" },
  { family: "Onest", category: "sans-serif" },

  // ── Serif ────────────────────────────────────────────────────────────────────
  { family: "Merriweather", category: "serif" },
  { family: "Playfair Display", category: "serif" },
  { family: "PT Serif", category: "serif" },
  { family: "Lora", category: "serif" },
  { family: "Source Serif 4", category: "serif" },
  { family: "Libre Baskerville", category: "serif" },
  { family: "Cormorant Garamond", category: "serif" },
  { family: "EB Garamond", category: "serif" },
  { family: "Crimson Text", category: "serif" },
  { family: "DM Serif Display", category: "serif" },
  { family: "Noto Serif", category: "serif" },
  { family: "Bitter", category: "serif" },
  { family: "Arvo", category: "serif" },
  { family: "Roboto Slab", category: "serif" },
  { family: "Zilla Slab", category: "serif" },
  { family: "Spectral", category: "serif" },
  { family: "Frank Ruhl Libre", category: "serif" },
  { family: "Cardo", category: "serif" },
  { family: "Fraunces", category: "serif" },
  { family: "Instrument Serif", category: "serif" },

  // ── Display ──────────────────────────────────────────────────────────────────
  { family: "Oswald", category: "display" },
  { family: "Titillium Web", category: "display" },
  { family: "Bebas Neue", category: "display" },
  { family: "Anton", category: "display" },
  { family: "Righteous", category: "display" },
  { family: "Staatliches", category: "display" },
  { family: "Big Shoulders Display", category: "display" },
  { family: "Unbounded", category: "display" },
  { family: "Archivo Black", category: "display" },
  { family: "Exo", category: "display" },
  { family: "Kanit", category: "display" },
  { family: "Chakra Petch", category: "display" },
  { family: "Saira", category: "display" },
  { family: "Black Han Sans", category: "display" },
  { family: "Russo One", category: "display" },
  { family: "Teko", category: "display" },
  { family: "Barlow Condensed", category: "display" },
  { family: "Fjalla One", category: "display" },
  { family: "Alfa Slab One", category: "display" },
  { family: "Graduate", category: "display" },

  // ── Monospace ────────────────────────────────────────────────────────────────
  { family: "Fira Code", category: "monospace" },
  { family: "Source Code Pro", category: "monospace" },
  { family: "JetBrains Mono", category: "monospace" },
  { family: "Inconsolata", category: "monospace" },
  { family: "Space Mono", category: "monospace" },
  { family: "IBM Plex Mono", category: "monospace" },
  { family: "Courier Prime", category: "monospace" },
  { family: "Roboto Mono", category: "monospace" },
  { family: "Ubuntu Mono", category: "monospace" },
  { family: "Overpass Mono", category: "monospace" },
  { family: "Share Tech Mono", category: "monospace" },

  // ── Handwriting ──────────────────────────────────────────────────────────────
  { family: "Dancing Script", category: "handwriting" },
  { family: "Pacifico", category: "handwriting" },
  { family: "Lobster", category: "handwriting" },
  { family: "Great Vibes", category: "handwriting" },
  { family: "Sacramento", category: "handwriting" },
  { family: "Caveat", category: "handwriting" },
  { family: "Satisfy", category: "handwriting" },
  { family: "Permanent Marker", category: "handwriting" },
  { family: "Kaushan Script", category: "handwriting" },
  { family: "Parisienne", category: "handwriting" },
  { family: "Pinyon Script", category: "handwriting" },
  { family: "Alex Brush", category: "handwriting" },
];

// ─── CSS injection ────────────────────────────────────────────────────────────

const previewLoaded = new Set<string>();
const fullLoaded = new Set<string>();

function ensurePreconnect() {
  if (document.querySelector('link[href="https://fonts.googleapis.com"]')) return;
  const pc1 = document.createElement("link");
  pc1.rel = "preconnect";
  pc1.href = "https://fonts.googleapis.com";
  document.head.appendChild(pc1);

  const pc2 = document.createElement("link");
  pc2.rel = "preconnect";
  pc2.href = "https://fonts.gstatic.com";
  pc2.crossOrigin = "";
  document.head.appendChild(pc2);
}

function injectLink(href: string) {
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = href;
  document.head.appendChild(link);
}

function encodedFamily(family: string) {
  return family.replace(/ /g, "+");
}

/**
 * Inject a lightweight preview stylesheet for a font (regular weight only).
 * Idempotent — safe to call on every render/scroll tick.
 */
export function preloadFontPreview(family: string): void {
  if (previewLoaded.has(family) || fullLoaded.has(family)) return;
  previewLoaded.add(family);
  ensurePreconnect();
  injectLink(
    `https://fonts.googleapis.com/css2?family=${encodedFamily(family)}:wght@400&display=swap`,
  );
}

/**
 * Inject a full stylesheet (common weights + italic) for a selected font.
 * Replaces any preview stylesheet for the same family.
 */
export function loadFullFont(family: string): void {
  if (fullLoaded.has(family)) return;
  fullLoaded.add(family);
  previewLoaded.delete(family); // will be superseded
  ensurePreconnect();
  // Request the six most common weights in both normal and italic
  const spec = "ital,wght@0,300;0,400;0,500;0,600;0,700;0,900;1,300;1,400;1,500;1,600;1,700;1,900";
  injectLink(
    `https://fonts.googleapis.com/css2?family=${encodedFamily(family)}:${spec}&display=swap`,
  );
}

/**
 * Returns true if the given family is a Google Font in our catalog.
 */
export function isGoogleFont(family: string): boolean {
  return GOOGLE_FONTS.some((f) => f.family === family);
}
