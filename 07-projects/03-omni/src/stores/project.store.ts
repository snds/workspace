import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import { devtools, persist } from "zustand/middleware";
import type { TechStackRecommendation, RepoConnection } from "@/types/onboarding";

export interface Project {
  id: string;
  name: string;
  createdAt: string;
  updatedAt: string;
  colorSystemId: string | null;
  techStack: TechStackRecommendation | null;
  repo: RepoConnection | null;
  /** ID of the team context profile preset (or null for custom) */
  teamContextId: string | null;
}

interface ProjectState {
  projects: Project[];
  activeProjectId: string | null;
}

interface ProjectActions {
  createProject(project: Project): void;
  setActiveProject(id: string): void;
  updateProject(id: string, updates: Partial<Project>): void;
  deleteProject(id: string): void;
}

export const useProjectStore = create<ProjectState & ProjectActions>()(
  devtools(
    persist(
      immer((set) => ({
        projects: [],
        activeProjectId: null,

        createProject: (project) =>
          set((s) => {
            s.projects.push(project);
            s.activeProjectId = project.id;
          }),

        setActiveProject: (id) =>
          set((s) => {
            s.activeProjectId = id;
          }),

        updateProject: (id, updates) =>
          set((s) => {
            const project = s.projects.find((p) => p.id === id);
            if (project) {
              Object.assign(project, updates);
              project.updatedAt = new Date().toISOString();
            }
          }),

        deleteProject: (id) =>
          set((s) => {
            s.projects = s.projects.filter((p) => p.id !== id);
            if (s.activeProjectId === id) {
              s.activeProjectId = s.projects[0]?.id ?? null;
            }
          }),
      })),
      { name: "omni-projects" }
    ),
    { name: "ProjectStore" }
  )
);
