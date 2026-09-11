import { useState } from "react";
import { Github, GitlabIcon, Folder, CheckCircle2, ExternalLink, Search, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import { useOnboardingStore } from "@/stores/onboarding.store";
import { useTeamContextStore } from "@/stores/teamContext.store";
import { useProjectStore } from "@/stores/project.store";
import { WizardNavButtons } from "../components/WizardNavButtons";
import { platform } from "@/platform";
import { analyzeRepo, type RepoAnalysisResult } from "../analysis/repoAnalyzer";
import { useNavigate } from "react-router";
import { nanoid } from "nanoid";
import type { RepoProvider } from "@/types/onboarding";

// ── Provider card ──────────────────────────────────────────────────────────

const PROVIDERS: {
  id: RepoProvider;
  label: string;
  color: string;
  Icon: React.ComponentType<{ className?: string }>;
}[] = [
  { id: "github",    label: "GitHub",    color: "#fff",    Icon: Github },
  { id: "gitlab",    label: "GitLab",    color: "#FC6D26", Icon: GitlabIcon },
  { id: "bitbucket", label: "Bitbucket", color: "#0052CC", Icon: ({ className }) => (
    // Bitbucket SVG inline — no lucide equivalent
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M.778 1.213a.768.768 0 00-.768.892l3.263 19.81c.084.5.52.862 1.026.862H19.95a.768.768 0 00.77-.646l3.27-20.02a.768.768 0 00-.768-.9L.778 1.213zM14.52 15.53H9.522L8.17 8.466h7.561l-1.211 7.064z" />
    </svg>
  )},
];

function ProviderCard({
  provider,
  selected,
  connected,
  onClick,
}: {
  provider: (typeof PROVIDERS)[number];
  selected: boolean;
  connected: boolean;
  onClick: () => void;
}) {
  const Icon = provider.Icon;
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-3 p-3.5 rounded-lg border text-left transition-all duration-150 cursor-pointer",
        connected
          ? "border-[var(--green-9)] bg-[#0d1f12]"
          : selected
          ? "border-[var(--violet-7)] bg-[var(--violet-3)] ring-1 ring-[var(--violet-7)]"
          : "border-[var(--mauve-5)] bg-[var(--mauve-3)] hover:border-[var(--mauve-6)] hover:bg-[var(--mauve-4)]"
      )}
    >
      <Icon
        className={cn(
          "w-5 h-5 flex-shrink-0",
          connected ? "text-[var(--green-9)]" : "text-[var(--mauve-10)]"
        )}
      />
      <div className="flex-1 min-w-0">
        <p className="text-xs font-medium text-[var(--mauve-12)]">
          {provider.label}
        </p>
        <p className="text-[10px] text-[var(--mauve-9)] mt-0.5">
          {connected ? "Connected" : "Connect via OAuth"}
        </p>
      </div>
      {connected && (
        <CheckCircle2 className="w-4 h-4 text-[var(--green-9)] flex-shrink-0" />
      )}
      {!connected && (
        <ExternalLink className="w-3 h-3 text-[var(--mauve-8)] flex-shrink-0" />
      )}
    </button>
  );
}

// ── Step ───────────────────────────────────────────────────────────────────

export function RepositoryStep() {
  const {
    repo,
    setRepoProvider,
    setLocalPath,
    setRemoteUrl,
    setRepoConnected,
    skipRepo,
    markStepComplete,
    completeOnboarding,
    projectName,
    recommendation,
  } = useOnboardingStore();

  const { createProject } = useProjectStore();
  const { profile, updateProfile } = useTeamContextStore();
  const navigate = useNavigate();

  const [remoteInput, setRemoteInput] = useState(repo.remoteUrl ?? "");
  const [pickingDir, setPickingDir] = useState(false);

  // Repo analysis state
  const [analysisResult, setAnalysisResult] = useState<RepoAnalysisResult | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisApplied, setAnalysisApplied] = useState(false);

  const handleProviderClick = async (providerId: RepoProvider) => {
    setRepoProvider(providerId);
    // In a real implementation, this would open OAuth. For now, mark as connected.
    // TODO: implement OAuth flow via platform.auth
    setRepoConnected(true);
  };

  const handleLocalPicker = async () => {
    setPickingDir(true);
    try {
      const path = await platform.dialog.openDirectory();
      if (path) {
        setLocalPath(path);
        setRepoConnected(true);
        // Auto-trigger analysis on directory selection
        runAnalysis(path);
      }
    } finally {
      setPickingDir(false);
    }
  };

  const runAnalysis = async (path: string) => {
    setAnalyzing(true);
    setAnalysisResult(null);
    setAnalysisApplied(false);
    try {
      const result = await analyzeRepo(path);
      setAnalysisResult(result);
    } catch {
      setAnalysisResult({
        profile: {},
        detectedItems: ["Analysis failed"],
        success: false,
      });
    } finally {
      setAnalyzing(false);
    }
  };

  const handleApplyDetected = () => {
    if (analysisResult?.success && analysisResult.profile) {
      updateProfile(analysisResult.profile);
      setAnalysisApplied(true);
    }
  };

  const finishOnboarding = () => {
    const projectId = nanoid();
    createProject({
      id: projectId,
      name: projectName,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      colorSystemId: null,
      techStack: recommendation,
      repo: repo.isSkipped ? null : repo,
      teamContextId: profile.name !== "Untitled Profile" ? profile.name : null,
    });
    markStepComplete(3);
    completeOnboarding();
    navigate(`/workspace/${projectId}/design-system/overview`);
  };

  const handleSkip = () => {
    skipRepo();
    finishOnboarding();
  };

  const handleContinue = () => {
    if (remoteInput.trim()) {
      setRemoteUrl(remoteInput.trim());
      setRepoConnected(true);
    }
    finishOnboarding();
  };

  const canContinue = repo.isConnected || repo.localPath !== null || remoteInput.trim().length > 0;

  return (
    <div className="flex flex-col">
      {/* Header */}
      <div className="px-8 pt-8 pb-6 border-b border-[var(--mauve-4)]">
        <h2 className="text-xl font-bold text-[var(--mauve-12)]">
          Connect a repository
        </h2>
        <p className="text-sm text-[var(--mauve-10)] mt-2">
          Link your code repository so Omni can read your project's structure and export directly to it. This step is optional.
        </p>
      </div>

      {/* Body */}
      <div className="px-8 py-6 flex flex-col gap-5">
        {/* Cloud providers */}
        <div>
          <label className="text-xs font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-3 block">
            Cloud provider
          </label>
          <div className="flex flex-col gap-2">
            {PROVIDERS.map((p) => (
              <ProviderCard
                key={p.id}
                provider={p}
                selected={repo.provider === p.id}
                connected={repo.provider === p.id && repo.isConnected}
                onClick={() => handleProviderClick(p.id)}
              />
            ))}
          </div>
        </div>

        {/* Remote URL */}
        <div>
          <label className="text-xs font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-2 block">
            Or paste a Git URL
          </label>
          <Input
            value={remoteInput}
            onChange={(e) => setRemoteInput(e.target.value)}
            placeholder="https://github.com/org/repo.git"
            className="bg-[var(--mauve-3)] border-[var(--mauve-5)] focus:border-[var(--violet-7)] text-[var(--mauve-12)] placeholder:text-[var(--mauve-8)] font-mono text-xs"
          />
        </div>

        {/* Local directory */}
        <div>
          <label className="text-xs font-semibold text-[var(--mauve-10)] uppercase tracking-wider mb-2 block">
            Or use a local directory
          </label>
          <Button
            variant="outline"
            size="sm"
            onClick={handleLocalPicker}
            disabled={pickingDir}
            className="w-full justify-start gap-2 border-dashed border-[var(--mauve-6)] bg-transparent hover:bg-[var(--mauve-3)] text-[var(--mauve-10)] hover:text-[var(--mauve-12)]"
          >
            <Folder className="w-4 h-4" />
            {repo.localPath
              ? repo.localPath
              : pickingDir
              ? "Opening picker..."
              : "Choose directory..."}
          </Button>
        </div>

        {/* Codebase Analysis Results */}
        {analyzing && (
          <div className="flex items-center gap-2 p-3 rounded-lg border border-[var(--mauve-5)] bg-[var(--mauve-3)]">
            <span className="w-3.5 h-3.5 border-2 border-[var(--violet-9)] border-t-transparent rounded-full animate-spin flex-shrink-0" />
            <span className="text-xs text-[var(--mauve-11)]">
              Analyzing repository...
            </span>
          </div>
        )}

        {analysisResult && !analyzing && (
          <div
            className={cn(
              "rounded-lg border p-4 space-y-3",
              analysisResult.success
                ? "border-[var(--violet-6)] bg-[var(--violet-2)]"
                : "border-[var(--mauve-5)] bg-[var(--mauve-3)]",
            )}
          >
            <div className="flex items-center gap-2">
              <Search className="w-3.5 h-3.5 text-[var(--violet-11)]" />
              <p className="text-xs font-semibold text-[var(--mauve-12)]">
                {analysisResult.success
                  ? "Detected Stack"
                  : "Analysis Result"}
              </p>
              {analysisResult.success && (
                <Badge
                  variant="outline"
                  className="text-[9px] border-[var(--violet-7)] text-[var(--violet-11)] bg-transparent ml-auto"
                >
                  {analysisResult.detectedItems.length} signals
                </Badge>
              )}
            </div>

            {analysisResult.success ? (
              <>
                <div className="flex flex-wrap gap-1.5">
                  {analysisResult.detectedItems.map((item, i) => (
                    <Badge
                      key={i}
                      variant="outline"
                      className="text-[10px] border-[var(--mauve-6)] text-[var(--mauve-11)] bg-[var(--mauve-3)]"
                    >
                      {item}
                    </Badge>
                  ))}
                </div>

                <Button
                  size="sm"
                  onClick={handleApplyDetected}
                  disabled={analysisApplied}
                  className="w-full gap-1.5 bg-[var(--violet-9)] hover:bg-[var(--violet-10)] text-white border-0 disabled:opacity-40"
                >
                  <Sparkles className="w-3 h-3" />
                  {analysisApplied
                    ? "Applied to team context"
                    : "Apply detected settings"}
                </Button>
              </>
            ) : (
              <p className="text-[10px] text-[var(--mauve-9)]">
                {analysisResult.detectedItems[0] ?? "No settings detected."}
              </p>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-8 pb-8">
        <WizardNavButtons
          canContinue={canContinue}
          onContinue={handleContinue}
          showSkip
          onSkip={handleSkip}
        />
      </div>
    </div>
  );
}
