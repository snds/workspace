import { create } from "zustand";

interface DesignSystemUIState {
  expandedCategories: Record<string, boolean>;
  activePrimitiveCategory: string;
  setExpanded: (id: string, expanded: boolean) => void;
  toggleExpanded: (id: string) => void;
  setActivePrimitiveCategory: (id: string) => void;
}

export const useDesignSystemUIStore = create<DesignSystemUIState>((set) => ({
  expandedCategories: {
    colors: true,
    typography: false,
    effects: false,
  },
  activePrimitiveCategory: "colors",

  setExpanded: (id, expanded) =>
    set((s) => ({
      expandedCategories: { ...s.expandedCategories, [id]: expanded },
    })),

  toggleExpanded: (id) =>
    set((s) => ({
      expandedCategories: {
        ...s.expandedCategories,
        [id]: !s.expandedCategories[id],
      },
    })),

  setActivePrimitiveCategory: (id) =>
    set({ activePrimitiveCategory: id }),
}));
