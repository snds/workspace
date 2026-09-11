// ─── Token type inference ─────────────────────────────────────────────────────
// Infers the best W3C DTCG $type for a new token based on its parent group path.
// Strategy: fast rule-based check first; Claude Haiku fallback for ambiguous paths.

import { platform } from "@/platform";
import type { DTCGType } from "@/types/tokens";

const DTCG_TYPES: DTCGType[] = [
  "color", "dimension", "font-family", "font-weight", "font-style",
  "number", "string", "duration", "cubic-bezier", "shadow", "gradient",
  "typography", "transition",
];

// ─── Rule-based inference (instant, no API) ───────────────────────────────────

function inferFromRules(path: string): DTCGType | null {
  const p = path.toLowerCase();

  // Color
  if (/\bcolou?r\b|\bhue\b|\bpalette\b|\btint\b|\bshade\b|\bfill\b|\baccount\b/.test(p)) return "color";
  if (/\bink\b|\bpigment\b|\bchroma\b/.test(p)) return "color";

  // Font family
  if (/\b(font|type|typo|text)\b.*(family|face|typeface)/.test(p)) return "font-family";
  if (/\bfamily\b|\btypeface\b/.test(p)) return "font-family";

  // Font weight
  if (/\bweight\b|\bfw\b/.test(p)) return "font-weight";

  // Font style
  if (/\bfont.?style\b|\bitalic\b|\boblique\b/.test(p)) return "font-style";

  // Number / unitless (line-height, opacity, etc.)
  if (/\bleading\b|\bline.?height\b|\blh\b/.test(p)) return "number";
  if (/\bopacity\b|\balpha\b|\btransparency\b/.test(p)) return "number";
  if (/\bz.?index\b|\bindex\b|\border\b/.test(p)) return "number";

  // Duration
  if (/\bduration\b|\bdelay\b|\bspeed\b|\bms\b/.test(p)) return "duration";
  if (/\btiming\b/.test(p) && !/\btime\b/.test(p)) return "duration";

  // Cubic bezier
  if (/\beasing\b|\bease\b|\bbezier\b|\bcurve\b|\bmotion\b/.test(p)) return "cubic-bezier";

  // Shadow
  if (/\bshadow\b|\belevation\b|\bdepth\b/.test(p)) return "shadow";

  // Gradient
  if (/\bgradient\b|\blinear\b|\bradial\b/.test(p)) return "gradient";

  // Transition
  if (/\btransition\b|\banimation\b/.test(p)) return "transition";

  // Dimension (all spatial/sizing/layout tokens)
  if (/\bspac(e|ing)\b|\bgap\b|\bpadding\b|\bmargin\b|\bindent\b/.test(p)) return "dimension";
  if (/\bsize\b|\bsizing\b|\bwidth\b|\bheight\b|\bdimension\b|\blength\b/.test(p)) return "dimension";
  if (/\bradius\b|\brounded\b|\bcorner\b/.test(p)) return "dimension";
  if (/\bstroke\b|\bborder\b|\boutline\b/.test(p) && /width|size|thick/.test(p)) return "dimension";
  if (/\bblur\b|\bspread\b/.test(p)) return "dimension";
  if (/\btrack(ing)?\b|\bletter.?spac/.test(p)) return "dimension";
  if (/\bfont.?size\b|\bfs\b|\btext.?size\b/.test(p)) return "dimension";

  // Font size (when path contains "font" + "size")
  if (/\bfont\b/.test(p) && /\bsize\b/.test(p)) return "dimension";

  return null;
}

// ─── In-memory cache (path → inferred type) ───────────────────────────────────

const cache = new Map<string, DTCGType>();

// ─── Main inference function ──────────────────────────────────────────────────

/**
 * Infers the best W3C DTCG $type for a new token at the given group path.
 *
 * 1. Checks the in-memory cache (instant).
 * 2. Tries rule-based inference against common naming patterns (instant).
 * 3. Falls back to a Claude Haiku call with a minimal prompt for ambiguous paths.
 *
 * @param groupPath - Dot-path of the parent group, e.g. "color.brand.primary"
 * @returns A DTCGType string, never throws (falls back to "string" on error)
 */
export async function inferTokenType(groupPath: string): Promise<DTCGType> {
  const cacheKey = groupPath.toLowerCase().trim();

  if (cache.has(cacheKey)) return cache.get(cacheKey)!;

  // Fast path: rule-based
  const ruleResult = inferFromRules(cacheKey);
  if (ruleResult) {
    cache.set(cacheKey, ruleResult);
    return ruleResult;
  }

  // Slow path: ask Claude Haiku
  try {
    const systemPrompt = [
      "You are a design token classifier. Given a token group path from a design system,",
      "respond with exactly one W3C DTCG token type. Valid types:",
      DTCG_TYPES.join(", "),
      ".",
      "Respond with ONLY the type name — no explanation, no punctuation, just the type string.",
      "If genuinely ambiguous, respond: string",
    ].join(" ");

    const userMessage = `Group path: "${groupPath}"\nWhat $type should new tokens in this group have?`;

    let response = "";
    for await (const chunk of platform.ai.streamMessage({
      systemPrompt,
      messages: [{ role: "user", content: userMessage }],
      maxTokens: 10,
      model: "claude-haiku-4-5-20251001",
    })) {
      response += chunk;
    }

    const candidate = response.trim().toLowerCase() as DTCGType;
    const result: DTCGType = DTCG_TYPES.includes(candidate) ? candidate : "string";
    cache.set(cacheKey, result);
    return result;
  } catch {
    return "string";
  }
}

/** Clear the inference cache (e.g. useful in tests or when schema changes). */
export function clearInferenceCache(): void {
  cache.clear();
}

// ─── Token name advisor ───────────────────────────────────────────────────────
// Observes token names during creation and move operations and suggests
// W3C DTCG-aligned alternatives when the current name doesn't follow best practices.
// Uses Claude Haiku (maxTokens: 15) for minimal cost.

const nameCache = new Map<string, string | null>();

/**
 * Suggests a better token name following W3C DTCG best practices.
 *
 * - Checks the in-memory cache first.
 * - Calls Claude Haiku if no cache hit.
 * - Returns null if the current name is already good, or on any error.
 *
 * @param groupPath  - Dot-path of the parent group, e.g. "color.brand"
 * @param currentName - The leaf name the user typed, e.g. "Color1"
 * @param type        - The token's DTCG type for context
 * @returns A suggested replacement name (kebab-case, no dots), or null if name is fine.
 */
export async function suggestTokenName(
  groupPath: string,
  currentName: string,
  type: DTCGType,
): Promise<string | null> {
  if (!currentName || currentName.length < 2) return null;

  const cacheKey = `${groupPath.toLowerCase()}|${currentName.toLowerCase()}|${type}`;
  if (nameCache.has(cacheKey)) return nameCache.get(cacheKey)!;

  try {
    const systemPrompt = [
      "You are a design token naming advisor following W3C DTCG best practices.",
      "Given a parent group path, the current token leaf name, and its type,",
      "suggest a cleaner kebab-case name if the current name is unclear, redundant, or non-standard.",
      "Rules: lowercase, no dots, no $ prefix, no spaces, hyphens only between words.",
      "If the name is already clear and well-formed, respond with exactly: ok",
      "Otherwise respond with ONLY the improved leaf name — no explanation, no quotes.",
    ].join(" ");

    const userMessage = `Group: "${groupPath}" | Name: "${currentName}" | Type: ${type}`;

    let response = "";
    for await (const chunk of platform.ai.streamMessage({
      systemPrompt,
      messages: [{ role: "user", content: userMessage }],
      maxTokens: 15,
      model: "claude-haiku-4-5-20251001",
    })) {
      response += chunk;
    }

    const raw = response.trim().toLowerCase().replace(/[^a-z0-9-]/g, "");
    const result = !raw || raw === "ok" || raw === currentName.toLowerCase() ? null : raw;
    nameCache.set(cacheKey, result);
    return result;
  } catch {
    return null;
  }
}

/** Clear the naming suggestion cache. */
export function clearNameCache(): void {
  nameCache.clear();
}
