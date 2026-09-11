export type Persona =
  | "design-system-maintainer"
  | "ux-designer"
  | "ui-designer";

export type ProjectMode = "new-design-system" | "open-existing";

export type OnboardingStep = 1 | 2 | 3;

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
}

export interface TechStackRecommendation {
  framework: string;
  cssApproach: string;
  componentLibrary: string;
  tokenFormat: string;
  rationale: string;
  confirmed: boolean;
}

export type RepoProvider = "github" | "gitlab" | "bitbucket";

export interface RepoConnection {
  provider: RepoProvider | null;
  localPath: string | null;
  remoteUrl: string | null;
  isConnected: boolean;
  isSkipped: boolean;
}

/** @deprecated Import from @/types/colorSystem instead */
export type { BrandColors } from "@/types/colorSystem";

export interface PersonaInfo {
  id: Persona;
  label: string;
  description: string;
  icon: string;
}

export const PERSONAS: PersonaInfo[] = [
  {
    id: "design-system-maintainer",
    label: "Design System Maintainer",
    description: "I build and maintain shared component libraries and tokens.",
    icon: "Blocks",
  },
  {
    id: "ux-designer",
    label: "UX Designer",
    description:
      "I design user flows, wireframes, and information architecture.",
    icon: "GitBranch",
  },
  {
    id: "ui-designer",
    label: "UI Designer",
    description: "I craft visual design, style guides, and polished interfaces.",
    icon: "Palette",
  },
];
