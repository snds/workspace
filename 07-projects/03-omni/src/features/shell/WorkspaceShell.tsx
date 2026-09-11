import { Outlet } from "react-router";
import { GlobalTopNav } from "./GlobalTopNav";

export function WorkspaceShell() {
  return (
    <div className="flex flex-col h-screen bg-[var(--color-surface-0)]">
      <GlobalTopNav />
      <div className="flex-1 min-h-0">
        <Outlet />
      </div>
    </div>
  );
}
