// ─── Infrastructure Store ──────────────────────────────────────────────────────
// Zustand + Immer store for environment management, feature flags, A/B tests,
// and deployment targets.
// ──────────────────────────────────────────────────────────────────────────────

import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import { devtools, persist } from "zustand/middleware";
import type {
  Environment,
  FeatureFlag,
  ABTest,
  DeployTarget,
} from "@/core/infra/types";
import { DEFAULT_ENVIRONMENTS } from "@/core/infra/environments";

interface InfraState {
  environments: Environment[];
  activeEnvironmentId: string;
  featureFlags: FeatureFlag[];
  abTests: ABTest[];
  deployTargets: DeployTarget[];
}

interface InfraActions {
  // Environments
  addEnvironment(env: Environment): void;
  removeEnvironment(id: string): void;
  setActiveEnvironment(id: string): void;
  updateEnvironment(id: string, updates: Partial<Environment>): void;
  setEnvVariable(
    envId: string,
    key: string,
    value: string,
    isSecret?: boolean,
  ): void;
  removeEnvVariable(envId: string, key: string): void;

  // Feature Flags
  addFlag(flag: FeatureFlag): void;
  removeFlag(key: string): void;
  updateFlag(key: string, updates: Partial<FeatureFlag>): void;
  toggleFlag(key: string): void;
  setFlagOverride(key: string, environmentId: string, value: unknown): void;

  // A/B Tests
  addABTest(test: ABTest): void;
  removeABTest(id: string): void;
  updateABTest(id: string, updates: Partial<ABTest>): void;

  // Deploy Targets
  addDeployTarget(target: DeployTarget): void;
  removeDeployTarget(id: string): void;

  // Getters
  getActiveEnvironment(): Environment | undefined;
  getFlagValue(key: string): unknown;
}

export const useInfraStore = create<InfraState & InfraActions>()(
  devtools(
    persist(
      immer((set, get) => ({
        // ── Initial state ──────────────────────────────────────────────────
        environments: DEFAULT_ENVIRONMENTS,
        activeEnvironmentId: "dev",
        featureFlags: [],
        abTests: [],
        deployTargets: [],

        // ── Environment actions ────────────────────────────────────────────

        addEnvironment: (env) =>
          set((s) => {
            s.environments.push(env as Environment);
          }),

        removeEnvironment: (id) =>
          set((s) => {
            s.environments = s.environments.filter(
              (e) => e.id !== id,
            ) as Environment[];
            // If we removed the active environment, fall back to first
            if (s.activeEnvironmentId === id && s.environments.length > 0) {
              s.activeEnvironmentId = s.environments[0].id;
              s.environments[0].isActive = true;
            }
          }),

        setActiveEnvironment: (id) =>
          set((s) => {
            for (const env of s.environments) {
              env.isActive = env.id === id;
            }
            s.activeEnvironmentId = id;
          }),

        updateEnvironment: (id, updates) =>
          set((s) => {
            const env = s.environments.find((e) => e.id === id);
            if (env) Object.assign(env, updates);
          }),

        setEnvVariable: (envId, key, value, isSecret = false) =>
          set((s) => {
            const env = s.environments.find((e) => e.id === envId);
            if (env) {
              env.variables[key] = { key, value, isSecret };
            }
          }),

        removeEnvVariable: (envId, key) =>
          set((s) => {
            const env = s.environments.find((e) => e.id === envId);
            if (env) {
              delete env.variables[key];
            }
          }),

        // ── Feature Flag actions ───────────────────────────────────────────

        addFlag: (flag) =>
          set((s) => {
            s.featureFlags.push(flag as FeatureFlag);
          }),

        removeFlag: (key) =>
          set((s) => {
            s.featureFlags = s.featureFlags.filter(
              (f) => f.key !== key,
            ) as FeatureFlag[];
          }),

        updateFlag: (key, updates) =>
          set((s) => {
            const flag = s.featureFlags.find((f) => f.key === key);
            if (flag) {
              Object.assign(flag, updates);
              flag.updatedAt = new Date().toISOString();
            }
          }),

        toggleFlag: (key) =>
          set((s) => {
            const flag = s.featureFlags.find((f) => f.key === key);
            if (flag) {
              flag.enabled = !flag.enabled;
              flag.updatedAt = new Date().toISOString();
            }
          }),

        setFlagOverride: (key, environmentId, value) =>
          set((s) => {
            const flag = s.featureFlags.find((f) => f.key === key);
            if (flag) {
              flag.environmentOverrides[environmentId] = value;
              flag.updatedAt = new Date().toISOString();
            }
          }),

        // ── A/B Test actions ───────────────────────────────────────────────

        addABTest: (test) =>
          set((s) => {
            s.abTests.push(test as ABTest);
          }),

        removeABTest: (id) =>
          set((s) => {
            s.abTests = s.abTests.filter((t) => t.id !== id) as ABTest[];
          }),

        updateABTest: (id, updates) =>
          set((s) => {
            const test = s.abTests.find((t) => t.id === id);
            if (test) Object.assign(test, updates);
          }),

        // ── Deploy Target actions ──────────────────────────────────────────

        addDeployTarget: (target) =>
          set((s) => {
            s.deployTargets.push(target as DeployTarget);
          }),

        removeDeployTarget: (id) =>
          set((s) => {
            s.deployTargets = s.deployTargets.filter(
              (t) => t.id !== id,
            ) as DeployTarget[];
          }),

        // ── Getters ────────────────────────────────────────────────────────

        getActiveEnvironment: () => {
          const state = get();
          return state.environments.find(
            (e) => e.id === state.activeEnvironmentId,
          );
        },

        getFlagValue: (key) => {
          const state = get();
          const flag = state.featureFlags.find((f) => f.key === key);
          if (!flag || !flag.enabled) return flag?.defaultValue;
          return (
            flag.environmentOverrides[state.activeEnvironmentId] ??
            flag.defaultValue
          );
        },
      })),
      { name: "omni-infra" },
    ),
    { name: "InfraStore" },
  ),
);
