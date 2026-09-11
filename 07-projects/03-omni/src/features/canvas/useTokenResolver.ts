import { useMemo } from "react";
import { useTokensStore } from "@/stores/tokens.store";
import { TokenResolver } from "@/core/ir/resolver";
import type { TokenOrLiteral } from "@/core/ir/types";
import { isTokenRef } from "@/core/ir/types";

/**
 * Hook that provides token resolution for canvas rendering.
 *
 * Wraps the `TokenResolver` class in a React-friendly API with memoised
 * convenience helpers (`resolveColor`, `resolveNumber`) that re-derive
 * whenever the token entries map changes.
 */
export function useTokenResolver() {
  const entries = useTokensStore((s) => s.entries);

  const resolver = useMemo(() => new TokenResolver(), []);

  const resolve = useMemo(() => {
    return <T,>(value: TokenOrLiteral<T>): T => {
      if (isTokenRef(value)) {
        const result = resolver.resolve(value, entries);
        return result as T;
      }
      return value as T;
    };
  }, [entries, resolver]);

  const resolveColor = useMemo(() => {
    return (
      value: TokenOrLiteral<string> | undefined | null,
    ): string | null => {
      if (value === undefined || value === null) return null;
      return resolve<string>(value);
    };
  }, [resolve]);

  const resolveNumber = useMemo(() => {
    return (
      value: TokenOrLiteral<number> | undefined | null,
      fallback: number = 0,
    ): number => {
      if (value === undefined || value === null) return fallback;
      const result = resolve<number>(value);
      return typeof result === "number" ? result : fallback;
    };
  }, [resolve]);

  return { resolve, resolveColor, resolveNumber, entries };
}
