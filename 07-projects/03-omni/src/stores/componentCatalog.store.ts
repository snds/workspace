import { create } from "zustand";
import { ComponentCatalog } from "@/core/components/catalog";
import type { ComponentBlueprint, ComponentCategory } from "@/core/components/types";
import { BUILTIN_BLUEPRINTS } from "@/core/components/builtin";

interface ComponentCatalogState {
  /** The shared component catalog instance */
  catalog: ComponentCatalog;
}

interface ComponentCatalogActions {
  /** Register a custom blueprint */
  registerBlueprint(blueprint: ComponentBlueprint): void;
  /** Remove a custom blueprint */
  unregisterBlueprint(id: string): void;
  /** Get a blueprint by ID */
  getBlueprint(id: string): ComponentBlueprint | undefined;
  /** Get all blueprints */
  getAllBlueprints(): ComponentBlueprint[];
  /** Get blueprints by category */
  getBlueprintsByCategory(category: ComponentCategory): ComponentBlueprint[];
  /** Search blueprints */
  searchBlueprints(query: string): ComponentBlueprint[];
}

function createDefaultCatalog(): ComponentCatalog {
  const catalog = new ComponentCatalog();
  for (const bp of BUILTIN_BLUEPRINTS) {
    catalog.register(bp);
  }
  return catalog;
}

export const useComponentCatalogStore = create<ComponentCatalogState & ComponentCatalogActions>()(
  (_set, get) => ({
    catalog: createDefaultCatalog(),

    registerBlueprint: (blueprint) => {
      get().catalog.register(blueprint);
    },

    unregisterBlueprint: (id) => {
      get().catalog.unregister(id);
    },

    getBlueprint: (id) => get().catalog.get(id),

    getAllBlueprints: () => get().catalog.getAll(),

    getBlueprintsByCategory: (category) => get().catalog.getByCategory(category),

    searchBlueprints: (query) => get().catalog.search(query),
  }),
);
