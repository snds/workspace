import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import { devtools, persist } from "zustand/middleware";
import type { DesignToken, TokenGroup, DTCGType, TokenValue, TokenReference } from "@/types/tokens";
import { isReference, extractRefPath } from "@/types/tokens";
import { classifyTier, getTokensByTier } from "@/core/tokens/tiers";
import { TokenPipeline } from "@/core/tokens/pipeline";
import type { TokenTier } from "@/core/tokens/tiers";
import type { TokenPipelineOptions, PipelineResult } from "@/core/tokens/pipeline";
import { useColorSystemStore } from "./colorSystem.store";
import { colorSystemToTokenEntries } from "@/features/tokens/migration";

// ─── State & Actions ──────────────────────────────────────────────────────────

interface TokensState {
  /** Flat map: dot-path → DesignToken, e.g. "color.brand.primary.500" */
  entries: Record<string, DesignToken>;
  /** Active display mode, e.g. "light" | "dark" */
  activeMode: string;
}

interface TokensActions {
  // ── CRUD ────────────────────────────────────────────────────────────────────
  setToken(path: string, token: DesignToken): void;
  removeToken(path: string): void;
  /** Remove all tokens whose path starts with prefix (i.e. delete a group) */
  removeGroup(prefix: string): void;
  /**
   * Rename all tokens whose path starts with oldPrefix → newPrefix.
   * Also updates any {oldPrefix.*} references throughout the store.
   */
  renameGroup(oldPrefix: string, newPrefix: string): void;
  duplicateToken(srcPath: string, destPath: string): void;
  /**
   * Merge entries into the store. If replace=true, wipes existing entries first.
   * Default: merge (preserves existing tokens at non-overlapping paths).
   */
  bulkSet(entries: Record<string, DesignToken>, replace?: boolean): void;

  // ── Mode ────────────────────────────────────────────────────────────────────
  setActiveMode(mode: string): void;

  // ── Computed ─────────────────────────────────────────────────────────────────
  getTree(): TokenGroup;
  resolveValue(path: string, mode?: string, visited?: Set<string>): TokenValue | null;
  getAllPaths(): string[];
  getPathsOfType(type: DTCGType): string[];
  getDisplayValue(path: string, mode?: string): string;

  // ── Tier & Pipeline (Phase 2 additions) ────────────────────────────────────
  /** Get the tier classification of a token */
  getTier(path: string): TokenTier | null;
  /** Get all tokens grouped by tier */
  getTokensByTier(): Record<TokenTier, string[]>;
  /** Get tokens scoped to a component (paths containing the component name) */
  getComponentTokens(component: string): Record<string, DesignToken>;
  /** Export tokens via the pipeline */
  exportVia(options: TokenPipelineOptions): PipelineResult;
}

// ─── Reference replacement helper ────────────────────────────────────────────

function replaceRefPrefix(
  value: TokenValue | TokenReference,
  oldPrefix: string,
  newPrefix: string,
): TokenValue | TokenReference {
  if (typeof value === "string" && isReference(value)) {
    const inner = extractRefPath(value);
    if (inner === oldPrefix || inner.startsWith(oldPrefix + ".")) {
      return `{${newPrefix}${inner.slice(oldPrefix.length)}}`;
    }
  }
  return value;
}

// ─── Store ────────────────────────────────────────────────────────────────────

export const useTokensStore = create<TokensState & TokensActions>()(
  devtools(
    persist(
      immer((set, get) => ({
        entries: {},
        activeMode: "light",

        // ── CRUD ──────────────────────────────────────────────────────────────

        setToken: (path, token) =>
          set((s) => {
            s.entries[path] = token;
          }),

        removeToken: (path) =>
          set((s) => {
            delete s.entries[path];
          }),

        removeGroup: (prefix) =>
          set((s) => {
            for (const key of Object.keys(s.entries)) {
              if (key === prefix || key.startsWith(prefix + ".")) {
                delete s.entries[key];
              }
            }
          }),

        renameGroup: (oldPrefix, newPrefix) =>
          set((s) => {
            // 1. Collect all keys under the old prefix
            const affected = Object.keys(s.entries).filter(
              (k) => k === oldPrefix || k.startsWith(oldPrefix + "."),
            );

            // 2. Re-key them under newPrefix
            for (const key of affected) {
              const newKey = newPrefix + key.slice(oldPrefix.length);
              s.entries[newKey] = s.entries[key]!;
              delete s.entries[key];
            }

            // 3. Update {ref} strings in $value and $extensions["omni.mode"]
            for (const token of Object.values(s.entries)) {
              token.$value = replaceRefPrefix(token.$value, oldPrefix, newPrefix);
              const modeOverrides = token.$extensions?.["omni.mode"];
              if (modeOverrides) {
                for (const [modeKey, modeVal] of Object.entries(modeOverrides)) {
                  modeOverrides[modeKey] = replaceRefPrefix(modeVal, oldPrefix, newPrefix);
                }
              }
            }
          }),

        duplicateToken: (srcPath, destPath) =>
          set((s) => {
            const src = s.entries[srcPath];
            if (src) {
              s.entries[destPath] = JSON.parse(JSON.stringify(src));
            }
          }),

        bulkSet: (entries, replace = false) =>
          set((s) => {
            if (replace) {
              s.entries = { ...entries };
            } else {
              Object.assign(s.entries, entries);
            }
          }),

        // ── Mode ──────────────────────────────────────────────────────────────

        setActiveMode: (mode) =>
          set((s) => {
            s.activeMode = mode;
          }),

        // ── Computed ──────────────────────────────────────────────────────────

        getTree: () => {
          const { entries } = get();
          const root: TokenGroup = {};

          const sortedPaths = Object.keys(entries).sort((a, b) =>
            a.localeCompare(b, undefined, { numeric: true }),
          );

          for (const path of sortedPaths) {
            const token = entries[path]!;
            const segments = path.split(".");
            let node: Record<string, unknown> = root;

            for (let i = 0; i < segments.length - 1; i++) {
              const seg = segments[i]!;
              const existing = node[seg];
              if (!existing || typeof existing !== "object" || "$value" in (existing as object)) {
                node[seg] = {};
              }
              node = node[seg] as Record<string, unknown>;
            }

            const leaf = segments[segments.length - 1]!;
            node[leaf] = { ...token };
          }

          return root;
        },

        resolveValue: (path, mode, visited = new Set()) => {
          if (visited.has(path)) return null; // cycle guard
          visited.add(path);

          const { entries, activeMode } = get();
          const token = entries[path];
          if (!token) return null;

          // Check mode override first
          const effectiveMode = mode ?? activeMode;
          const modeVal = token.$extensions?.["omni.mode"]?.[effectiveMode];
          const rawValue: TokenValue | TokenReference = modeVal !== undefined ? modeVal : token.$value;

          // Follow reference
          if (isReference(rawValue)) {
            return get().resolveValue(extractRefPath(rawValue), mode, visited);
          }

          return rawValue as TokenValue;
        },

        getAllPaths: () => Object.keys(get().entries),

        getPathsOfType: (type) =>
          Object.entries(get().entries)
            .filter(([, token]) => token.$type === type)
            .map(([path]) => path),

        getDisplayValue: (path, mode) => {
          const resolved = get().resolveValue(path, mode);
          if (resolved === null) return "—";
          if (typeof resolved === "object") return JSON.stringify(resolved);
          return String(resolved);
        },

        // ── Tier & Pipeline ──────────────────────────────────────────────────

        getTier: (path) => {
          const token = get().entries[path];
          if (!token) return null;
          return classifyTier(path, token);
        },

        getTokensByTier: () => {
          return getTokensByTier(get().entries);
        },

        getComponentTokens: (component) => {
          const { entries } = get();
          const result: Record<string, DesignToken> = {};
          for (const [path, token] of Object.entries(entries)) {
            if (path.includes(`${component}.`)) {
              result[path] = token;
            }
          }
          return result;
        },

        exportVia: (options) => {
          const pipeline = new TokenPipeline(get().entries);
          return pipeline.export(options);
        },
      })),
      { name: "omni-tokens" },
    ),
    { name: "TokensStore" },
  ),
);

// ─── Cross-store sync ─────────────────────────────────────────────────────────
// When the ColorSystem changes (preset applied, AI generation), sync color tokens
// into the tokens store without wiping existing static tokens.

useColorSystemStore.subscribe((state, prev) => {
  if (state.colorSystem !== prev.colorSystem && state.colorSystem) {
    const colorEntries = colorSystemToTokenEntries(state.colorSystem);
    useTokensStore.getState().bulkSet(colorEntries, false);
  }
});

// Also sync on initial load if a colorSystem is already persisted
(function syncInitial() {
  const cs = useColorSystemStore.getState().colorSystem;
  if (cs) {
    const colorEntries = colorSystemToTokenEntries(cs);
    useTokensStore.getState().bulkSet(colorEntries, false);
  }
})();
