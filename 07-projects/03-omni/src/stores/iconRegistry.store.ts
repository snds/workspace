import { create } from "zustand";
import { IconRegistry } from "@/core/icons/registry";
import { LucideAdapter, LUCIDE_SEMANTIC_MAP } from "@/core/icons/adapters/lucide";
import { IconifyAdapter } from "@/core/icons/adapters/iconify";

interface IconRegistryState {
  /** The shared icon registry instance */
  registry: IconRegistry;
  /** Currently active adapter ID */
  activeAdapterId: string;
}

interface IconRegistryActions {
  /** Set the active adapter */
  setActiveAdapter(adapterId: string): void;
  /** Override a semantic mapping */
  setMapping(semanticName: string, adapterIcon: string): void;
  /** Bulk override semantic mappings */
  setMappings(mappings: Record<string, string>): void;
}

function createDefaultRegistry(): IconRegistry {
  const registry = new IconRegistry();
  registry.registerAdapter(new LucideAdapter());
  registry.registerAdapter(new IconifyAdapter());
  registry.defaultAdapterId = "lucide";
  registry.setMappings(LUCIDE_SEMANTIC_MAP);
  return registry;
}

export const useIconRegistryStore = create<IconRegistryState & IconRegistryActions>()(
  (set, get) => ({
    registry: createDefaultRegistry(),
    activeAdapterId: "lucide",

    setActiveAdapter: (adapterId) => {
      const { registry } = get();
      if (registry.getAdapter(adapterId)) {
        registry.defaultAdapterId = adapterId;
        set({ activeAdapterId: adapterId });
      }
    },

    setMapping: (semanticName, adapterIcon) => {
      get().registry.setMapping(semanticName, adapterIcon);
    },

    setMappings: (mappings) => {
      get().registry.setMappings(mappings);
    },
  }),
);
