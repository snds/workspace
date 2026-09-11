import { create } from "zustand";
import { immer } from "zustand/middleware/immer";
import { devtools, persist } from "zustand/middleware";
import type {
  Persona,
  ProjectMode,
  OnboardingStep,
  ChatMessage,
  TechStackRecommendation,
  RepoProvider,
  RepoConnection,
} from "@/types/onboarding";

// ── State ──────────────────────────────────────────────────────────────────

interface OnboardingState {
  currentStep: OnboardingStep;
  completedSteps: OnboardingStep[];
  isComplete: boolean;

  // Step 1 — Welcome
  persona: Persona | null;
  projectMode: ProjectMode | null;
  projectName: string;

  // Step 2 — Team Context
  chatHistory: ChatMessage[];
  isAiStreaming: boolean;
  recommendation: TechStackRecommendation | null;

  // Step 3 — Repository
  repo: RepoConnection;
}

// ── Actions ────────────────────────────────────────────────────────────────

interface OnboardingActions {
  // Navigation
  goToStep(step: OnboardingStep): void;
  nextStep(): void;
  prevStep(): void;
  markStepComplete(step: OnboardingStep): void;
  completeOnboarding(): void;

  // Step 1
  setPersona(persona: Persona): void;
  setProjectMode(mode: ProjectMode): void;
  setProjectName(name: string): void;

  // Step 2
  appendChatMessage(message: ChatMessage): void;
  updateLastAssistantMessage(delta: string): void;
  setAiStreaming(streaming: boolean): void;
  setRecommendation(rec: TechStackRecommendation): void;
  confirmRecommendation(): void;
  resetChat(): void;

  // Step 3
  setRepoProvider(provider: RepoProvider): void;
  setLocalPath(path: string): void;
  setRemoteUrl(url: string): void;
  setRepoConnected(connected: boolean): void;
  skipRepo(): void;
}

// ── Store ──────────────────────────────────────────────────────────────────

const initialState: OnboardingState = {
  currentStep: 1,
  completedSteps: [],
  isComplete: false,

  persona: null,
  projectMode: null,
  projectName: "My Design System",

  chatHistory: [],
  isAiStreaming: false,
  recommendation: null,

  repo: {
    provider: null,
    localPath: null,
    remoteUrl: null,
    isConnected: false,
    isSkipped: false,
  },
};

export const useOnboardingStore = create<OnboardingState & OnboardingActions>()(
  devtools(
    persist(
    immer((set) => ({
      ...initialState,

      // Navigation
      goToStep: (step) =>
        set((s) => {
          s.currentStep = step;
        }),
      nextStep: () =>
        set((s) => {
          if (s.currentStep < 3) {
            s.currentStep = (s.currentStep + 1) as OnboardingStep;
          }
        }),
      prevStep: () =>
        set((s) => {
          if (s.currentStep > 1) {
            s.currentStep = (s.currentStep - 1) as OnboardingStep;
          }
        }),
      markStepComplete: (step) =>
        set((s) => {
          if (!s.completedSteps.includes(step)) {
            s.completedSteps.push(step);
          }
        }),
      completeOnboarding: () =>
        set((s) => {
          s.isComplete = true;
        }),

      // Step 1
      setPersona: (persona) =>
        set((s) => {
          s.persona = persona;
        }),
      setProjectMode: (mode) =>
        set((s) => {
          s.projectMode = mode;
        }),
      setProjectName: (name) =>
        set((s) => {
          s.projectName = name;
        }),

      // Step 2
      appendChatMessage: (message) =>
        set((s) => {
          s.chatHistory.push(message);
        }),
      updateLastAssistantMessage: (delta) =>
        set((s) => {
          const last = s.chatHistory[s.chatHistory.length - 1];
          if (last && last.role === "assistant") {
            last.content += delta;
          }
        }),
      setAiStreaming: (streaming) =>
        set((s) => {
          s.isAiStreaming = streaming;
        }),
      setRecommendation: (rec) =>
        set((s) => {
          s.recommendation = rec;
        }),
      confirmRecommendation: () =>
        set((s) => {
          if (s.recommendation) {
            s.recommendation.confirmed = true;
          }
        }),
      resetChat: () =>
        set((s) => {
          s.chatHistory = [];
          s.recommendation = null;
          s.isAiStreaming = false;
        }),

      // Step 3
      setRepoProvider: (provider) =>
        set((s) => {
          s.repo.provider = provider;
        }),
      setLocalPath: (path) =>
        set((s) => {
          s.repo.localPath = path;
          s.repo.remoteUrl = null;
        }),
      setRemoteUrl: (url) =>
        set((s) => {
          s.repo.remoteUrl = url;
          s.repo.localPath = null;
        }),
      setRepoConnected: (connected) =>
        set((s) => {
          s.repo.isConnected = connected;
        }),
      skipRepo: () =>
        set((s) => {
          s.repo.isSkipped = true;
        }),
    })),
    {
      name: "omni-onboarding",
      partialize: (state) => {
        const { isAiStreaming, ...persisted } = state;
        void isAiStreaming;
        return persisted;
      },
    },
    ),
    { name: "OnboardingStore" }
  )
);
