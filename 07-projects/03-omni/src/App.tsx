import { useEffect, useCallback, useState, useRef } from "react";
import { createBrowserRouter, RouterProvider, redirect } from "react-router";
import { OnboardingRoute } from "@/routes/onboarding";
import { WorkspaceShell } from "@/features/shell/WorkspaceShell";
import { LayoutsTool } from "@/features/shell/LayoutsTool";
import { CodeTool } from "@/features/shell/CodeTool";
import { DesignSystemLayout } from "@/features/design-system/DesignSystemLayout";
import { OverviewTab } from "@/features/design-system/tabs/OverviewTab";
import { PrimitivesTab } from "@/features/design-system/tabs/PrimitivesTab";
import { SemanticsTab } from "@/features/design-system/tabs/SemanticsTab";
import { useUIStore } from "@/stores/ui.store";
import { useOnboardingStore } from "@/stores/onboarding.store";
import { useProjectStore } from "@/stores/project.store";

const router = createBrowserRouter([
  {
    path: "/",
    loader: () => {
      const { isComplete } = useOnboardingStore.getState();
      const { activeProjectId } = useProjectStore.getState();

      if (isComplete && activeProjectId) {
        return redirect(`/workspace/${activeProjectId}`);
      }
      return redirect("/onboarding");
    },
  },
  {
    path: "/onboarding",
    loader: () => {
      // If onboarding is done and a project exists, skip straight to workspace
      const { isComplete } = useOnboardingStore.getState();
      const { activeProjectId } = useProjectStore.getState();

      if (isComplete && activeProjectId) {
        return redirect(`/workspace/${activeProjectId}`);
      }
      return null;
    },
    element: <OnboardingRoute />,
  },
  {
    path: "/workspace/:projectId",
    element: <WorkspaceShell />,
    children: [
      {
        index: true,
        loader: () => redirect("design-system"),
      },
      {
        path: "design-system",
        element: <DesignSystemLayout />,
        children: [
          {
            index: true,
            loader: () => redirect("overview"),
          },
          { path: "overview", element: <OverviewTab /> },
          { path: "primitives", element: <PrimitivesTab /> },
          { path: "semantics", element: <SemanticsTab /> },
        ],
      },
      {
        path: "layouts",
        element: <LayoutsTool />,
      },
      {
        path: "code",
        element: <CodeTool />,
      },
    ],
  },
]);

// ── Custom context menu ──────────────────────────────────────────────────

interface MenuPos { x: number; y: number }

function ContextMenu({ pos, onClose }: { pos: MenuPos; onClose: () => void }) {
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const dismiss = (e: MouseEvent | KeyboardEvent) => {
      if (e instanceof KeyboardEvent && e.key === "Escape") { onClose(); return; }
      if (e instanceof MouseEvent && menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    window.addEventListener("mousedown", dismiss, true);
    window.addEventListener("keydown", dismiss, true);
    return () => {
      window.removeEventListener("mousedown", dismiss, true);
      window.removeEventListener("keydown", dismiss, true);
    };
  }, [onClose]);

  const items = [
    {
      label: "Back",
      shortcut: "Alt+\u2190",
      action: () => { window.history.back(); onClose(); },
    },
    {
      label: "Forward",
      shortcut: "Alt+\u2192",
      action: () => { window.history.forward(); onClose(); },
    },
    {
      label: "Reload",
      shortcut: "\u2318R",
      action: () => { window.location.reload(); onClose(); },
    },
    { label: "---", shortcut: "", action: () => {} },
    {
      label: "Reset App",
      shortcut: "\u2318\u21E7K",
      action: () => {
        Object.keys(localStorage)
          .filter((k) => k.startsWith("omni-"))
          .forEach((k) => localStorage.removeItem(k));
        window.location.replace("/");
      },
    },
  ];

  return (
    <div
      ref={menuRef}
      className="fixed z-[9999] min-w-[180px] py-1 bg-[var(--mauve-3)] border border-[var(--mauve-5)] rounded-lg shadow-xl backdrop-blur-sm"
      style={{ top: pos.y, left: pos.x }}
    >
      {items.map((item, i) =>
        item.label === "---" ? (
          <div key={i} className="my-1 border-t border-[var(--mauve-5)]" />
        ) : (
          <button
            key={item.label}
            onClick={item.action}
            className="w-full flex items-center justify-between px-3 py-1.5 text-[11px] text-[var(--mauve-12)] hover:bg-[var(--violet-4)] hover:text-[var(--violet-11)] transition-colors"
          >
            <span>{item.label}</span>
            <span className="text-[10px] text-[var(--mauve-8)] ml-4 font-mono">
              {item.shortcut}
            </span>
          </button>
        )
      )}
    </div>
  );
}

// ── App ──────────────────────────────────────────────────────────────────

export default function App() {
  const theme = useUIStore((s) => s.theme);
  const [menuPos, setMenuPos] = useState<MenuPos | null>(null);

  useEffect(() => {
    const el = document.documentElement;
    el.classList.toggle("dark", theme === "dark");
    el.classList.toggle("light", theme === "light");
  }, [theme]);

  // Cmd+Shift+K (Mac) / Ctrl+Shift+K (Win) → reset
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const isReset =
        e.code === "KeyK" && e.shiftKey && (e.metaKey || e.ctrlKey);
      if (!isReset) return;
      e.preventDefault();
      e.stopPropagation();
      Object.keys(localStorage)
        .filter((k) => k.startsWith("omni-"))
        .forEach((k) => localStorage.removeItem(k));
      window.location.replace("/");
    };
    window.addEventListener("keydown", handler, true);
    return () => window.removeEventListener("keydown", handler, true);
  }, []);

  // Right-click context menu
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      e.preventDefault();
      setMenuPos({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("contextmenu", handler);
    return () => window.removeEventListener("contextmenu", handler);
  }, []);

  const closeMenu = useCallback(() => setMenuPos(null), []);

  return (
    <>
      <RouterProvider router={router} />
      {menuPos && <ContextMenu pos={menuPos} onClose={closeMenu} />}
    </>
  );
}
