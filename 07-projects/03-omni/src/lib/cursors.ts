/**
 * Custom SVG cursor utility for canvas interactions.
 *
 * Uses the Penpot/Felt pattern: SVG data URIs with rotation transforms,
 * quantized to 15-degree steps and memoized for performance.
 */

const CURSOR_SIZE = 24;
const HALF = CURSOR_SIZE / 2;

// ─── SVG cursor templates (centered at HALF, HALF) ──────────────────────────

/** Bidirectional resize arrow — horizontal by default, rotated per handle */
const RESIZE_SVG = [
  // Two-headed arrow (horizontal)
  `<path d='M4 12l4-4v3h8V8l4 4-4 4v-3H8v3z'`,
  ` fill='white' stroke='black' stroke-width='1' stroke-linejoin='round'/>`,
].join("");

/** Rotation cursor — curved arrow at top-right corner */
const ROTATE_SVG = [
  `<path d='M17.7 7.7A7 7 0 0 0 5.3 7.7' stroke='white' stroke-width='2.5' fill='none' stroke-linecap='round'/>`,
  `<path d='M17.7 7.7A7 7 0 0 0 5.3 7.7' stroke='black' stroke-width='1.2' fill='none' stroke-linecap='round'/>`,
  `<path d='M17 3l1 5-5-1' fill='white' stroke='black' stroke-width='1' stroke-linejoin='round'/>`,
].join("");

// ─── Encoder ────────────────────────────────────────────────────────────────

function buildCursorSvg(innerSvg: string, angle: number): string {
  const rotated = angle !== 0
    ? `<g transform='rotate(${angle} ${HALF} ${HALF})'>${innerSvg}</g>`
    : innerSvg;

  return `<svg xmlns='http://www.w3.org/2000/svg' width='${CURSOR_SIZE}' height='${CURSOR_SIZE}' viewBox='0 0 ${CURSOR_SIZE} ${CURSOR_SIZE}'>${rotated}</svg>`;
}

function encodeSvg(svg: string): string {
  return svg
    .replace(/"/g, "'")
    .replace(/#/g, "%23")
    .replace(/</g, "%3C")
    .replace(/>/g, "%3E");
}

function toCssUrl(svg: string): string {
  return `url("data:image/svg+xml,${encodeSvg(svg)}") ${HALF} ${HALF}, auto`;
}

// ─── Quantization + cache ───────────────────────────────────────────────────

function quantize(angle: number, step: number = 15): number {
  const normalized = ((angle % 360) + 360) % 360;
  return Math.round(normalized / step) * step;
}

const cache = new Map<string, string>();

function getCachedCursor(key: string, innerSvg: string, angle: number): string {
  const q = quantize(angle);
  const cacheKey = `${key}_${q}`;
  let cursor = cache.get(cacheKey);
  if (!cursor) {
    cursor = toCssUrl(buildCursorSvg(innerSvg, q));
    cache.set(cacheKey, cursor);
  }
  return cursor;
}

// ─── Public API ─────────────────────────────────────────────────────────────

/**
 * Get a cursor CSS string for a resize or rotation action.
 * @param type - "resize" or "rotate"
 * @param angle - absolute angle in degrees (handle base angle + node rotation)
 */
export function getCursor(type: "resize" | "rotate", angle: number): string {
  const svg = type === "resize" ? RESIZE_SVG : ROTATE_SVG;
  return getCachedCursor(type, svg, angle);
}

/**
 * Get a rotation cursor at the given angle.
 * @param angle - rotation angle of the selection in degrees
 */
export function getRotationCursor(angle: number): string {
  return getCachedCursor("rotate", ROTATE_SVG, angle);
}
