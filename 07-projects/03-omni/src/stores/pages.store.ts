import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import { devtools, persist } from "zustand/middleware";
import { nanoid } from "nanoid";

export interface Page {
  id: string;
  name: string;
  order: number;
  isSeparator?: boolean;
}

const DEFAULT_PAGE_ID = nanoid();

interface PagesState {
  pages: Page[];
  activePageId: string;
}

interface PagesActions {
  addPage(): string;
  addSeparator(): string;
  convertToSeparator(id: string): void;
  deletePage(id: string): void;
  renamePage(id: string, name: string): void;
  setActivePage(id: string): void;
  reorderPage(id: string, newOrder: number): void;
}

export const usePagesStore = create<PagesState & PagesActions>()(
  devtools(
    persist(
      immer((set, get) => ({
        pages: [{ id: DEFAULT_PAGE_ID, name: "Page 1", order: 0 }],
        activePageId: DEFAULT_PAGE_ID,

        addPage() {
          const id = nanoid();
          const { pages: current, activePageId } = get();
          const activePage = current.find((p) => p.id === activePageId && !p.isSeparator);
          const insertAfterOrder = activePage?.order ?? Math.max(...current.map((p) => p.order));
          const count = current.filter((p) => !p.isSeparator).length + 1;
          set((s) => {
            // Shift all pages with order > insertAfterOrder up by 1
            for (const p of s.pages) {
              if (p.order > insertAfterOrder) p.order += 1;
            }
            s.pages.push({ id, name: `Page ${count}`, order: insertAfterOrder + 1 });
            s.activePageId = id;
          });
          return id;
        },

        addSeparator() {
          const id = nanoid();
          const maxOrder = get().pages.reduce((m, p) => Math.max(m, p.order), 0);
          set((s) => {
            s.pages.push({ id, name: "---", order: maxOrder + 1, isSeparator: true });
          });
          return id;
        },

        convertToSeparator(id) {
          set((s) => {
            const page = s.pages.find((p) => p.id === id);
            if (page) {
              page.isSeparator = true;
              page.name = "---";
              // If this was the active page, switch to nearest non-separator
              if (s.activePageId === id) {
                const sorted = [...s.pages].sort((a, b) => a.order - b.order);
                const nonSep = sorted.find((p) => !p.isSeparator && p.id !== id);
                if (nonSep) s.activePageId = nonSep.id;
              }
            }
          });
        },

        deletePage(id) {
          set((s) => {
            const target = s.pages.find((p) => p.id === id);
            // Separators can always be deleted; pages need at least 1 remaining
            if (!target) return;
            if (!target.isSeparator) {
              const realPages = s.pages.filter((p) => !p.isSeparator);
              if (realPages.length <= 1) return;
            }
            s.pages = s.pages.filter((p) => p.id !== id);
            if (s.activePageId === id) {
              const nonSep = s.pages.find((p) => !p.isSeparator);
              if (nonSep) s.activePageId = nonSep.id;
            }
          });
        },

        renamePage(id, name) {
          set((s) => {
            const page = s.pages.find((p) => p.id === id);
            if (page) page.name = name.trim() || page.name;
          });
        },

        setActivePage(id) {
          set((s) => {
            if (s.pages.find((p) => p.id === id)) {
              s.activePageId = id;
            }
          });
        },

        reorderPage(id, newOrder) {
          set((s) => {
            const page = s.pages.find((p) => p.id === id);
            if (page) page.order = newOrder;
          });
        },
      })),
      { name: "omni-pages" }
    ),
    { name: "PagesStore" }
  )
);
