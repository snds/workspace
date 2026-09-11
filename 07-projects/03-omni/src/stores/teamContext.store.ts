import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import { devtools, persist } from "zustand/middleware";
import type { TeamContextProfile, UsageTier } from "@/core/context/types";
import { createDefaultProfile, CONTEXT_PRESETS } from "@/core/context/defaults";

interface TeamContextState {
  /** The active team context profile */
  profile: TeamContextProfile;
  /** ID of the preset this was created from (null if custom) */
  presetId: string | null;
}

interface TeamContextActions {
  /** Set the entire profile */
  setProfile(profile: TeamContextProfile): void;
  /** Apply a preset by ID */
  applyPreset(presetId: string): void;
  /** Update specific fields of the profile */
  updateProfile(updates: Partial<TeamContextProfile>): void;
  /** Set the usage tier */
  setTier(tier: UsageTier): void;
  /** Get available preset IDs */
  getPresetIds(): string[];
  /** Check if a tier is active (current tier >= requested tier) */
  isTierActive(tier: UsageTier): boolean;
}

export const useTeamContextStore = create<TeamContextState & TeamContextActions>()(
  devtools(
    persist(
      immer((set, get) => ({
        profile: createDefaultProfile("design-only"),
        presetId: "design-only",

        setProfile: (profile) =>
          set((s) => {
            s.profile = profile as TeamContextProfile;
            s.presetId = null;
          }),

        applyPreset: (presetId) =>
          set((s) => {
            s.profile = createDefaultProfile(presetId) as TeamContextProfile;
            s.presetId = presetId;
          }),

        updateProfile: (updates) =>
          set((s) => {
            Object.assign(s.profile, updates);
            s.presetId = null;
          }),

        setTier: (tier) =>
          set((s) => {
            s.profile.tier = tier;
          }),

        getPresetIds: () => Object.keys(CONTEXT_PRESETS),

        isTierActive: (tier) => get().profile.tier >= tier,
      })),
      { name: "omni-team-context" },
    ),
    { name: "TeamContextStore" },
  ),
);
