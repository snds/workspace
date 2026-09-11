// ─── Code Generation Panel ──────────────────────────────────────────────────
// Shown in the left panel when "Code" tab is active.
// Allows generating code from canvas IR nodes using the translation engine.

import { useState, useCallback, useMemo } from "react";
import { useTeamContextStore } from "@/stores/teamContext.store";
import { useCanvasStore } from "@/stores/canvas.store";
import { translateToCode } from "@/core/translation/service";
import { generateFrontendFiles } from "@/core/translation/generators/frontend";
import { generateBackendFiles } from "@/core/translation/generators/backend";
import { generateInfraFiles } from "@/core/translation/generators/infra";
import { validateGenerated } from "@/core/translation/validator";
import type { GeneratedFile, TranslationScope, FileCategory } from "@/core/translation/types";
import type { IRNode } from "@/core/ir/types";
import type { CanvasNode } from "@/types/canvas";
import { cn } from "@/lib/utils";
import { OmniIcon } from "@/core/icons";
import { ScrollArea } from "@/components/ui/scroll-area";

// ─── Constants ──────────────────────────────────────────────────────────────

const SCOPE_OPTIONS: { value: TranslationScope; label: string; minTier: number }[] = [
  { value: "component", label: "Component", minTier: 0 },
  { value: "page", label: "Page", minTier: 1 },
  { value: "full-stack", label: "Full Stack", minTier: 2 },
  { value: "tokens-only", label: "Tokens", minTier: 0 },
  { value: "styles-only", label: "Styles", minTier: 0 },
];

const CATEGORY_LABELS: Record<FileCategory, string> = {
  frontend: "Frontend",
  backend: "Backend",
  styling: "Styles",
  config: "Config",
  test: "Tests",
  types: "Types",
};

const CATEGORY_ORDER: FileCategory[] = [
  "frontend",
  "backend",
  "styling",
  "config",
  "test",
  "types",
];

// ─── CodePanel ──────────────────────────────────────────────────────────────

/** Code generation panel -- shown in the left panel when "Code" tab is active */
export function CodePanel() {
  const [files, setFiles] = useState<GeneratedFile[]>([]);
  const [activeFile, setActiveFile] = useState<string | null>(null);
  const [scope, setScope] = useState<TranslationScope>("component");
  const [isGenerating, setIsGenerating] = useState(false);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [activeCategory, setActiveCategory] = useState<FileCategory>("frontend");
  const [copied, setCopied] = useState<string | null>(null);

  const profile = useTeamContextStore((s) => s.profile);
  const tier = profile.tier;
  const selectedIds = useCanvasStore((s) => s.selectedIds);
  const nodes = useCanvasStore((s) => s.nodes);

  // Filter scope options by tier
  const availableScopes = useMemo(
    () => SCOPE_OPTIONS.filter((s) => s.minTier <= tier),
    [tier],
  );

  // Filter files by active category
  const filteredFiles = useMemo(
    () => files.filter((f) => f.category === activeCategory),
    [files, activeCategory],
  );

  // Get available categories (only show tabs that have files)
  const availableCategories = useMemo(() => {
    const cats = new Set(files.map((f) => f.category));
    return CATEGORY_ORDER.filter((c) => cats.has(c));
  }, [files]);

  // Active file content
  const activeFileData = useMemo(
    () => files.find((f) => f.path === activeFile) ?? null,
    [files, activeFile],
  );

  // Convert selected canvas nodes to minimal IR nodes for generation
  const selectedIRNodes = useMemo((): IRNode[] => {
    const selected = selectedIds.length > 0
      ? nodes.filter((n) => selectedIds.includes(n.id))
      : nodes.slice(0, 5); // Use first 5 nodes if nothing selected

    return selected.map((n: CanvasNode) => canvasNodeToIR(n));
  }, [selectedIds, nodes]);

  // Handle code generation
  const handleGenerate = useCallback(async () => {
    setIsGenerating(true);
    setWarnings([]);

    try {
      const allFiles: GeneratedFile[] = [];

      // Try AI translation first (currently returns stub)
      const result = await translateToCode({
        nodes: selectedIRNodes,
        context: profile,
        scope,
      });

      if (result.warnings) {
        setWarnings(result.warnings);
      }

      // Use template generators as fallback
      const frontendFiles = generateFrontendFiles(selectedIRNodes, profile);
      allFiles.push(...frontendFiles);

      if (tier >= 2 && (scope === "full-stack" || scope === "page")) {
        const backendFiles = generateBackendFiles(selectedIRNodes, profile);
        allFiles.push(...backendFiles);
      }

      if (tier >= 3 && scope === "full-stack") {
        const infraFiles = generateInfraFiles(profile);
        allFiles.push(...infraFiles);
      }

      // Add any AI-generated files
      if (result.files.length > 0) {
        allFiles.push(...result.files);
      }

      // Validate
      const validation = validateGenerated(allFiles);
      if (!validation.valid) {
        setWarnings((prev) => [
          ...prev,
          ...validation.errors.map(
            (e) => `${e.file}${e.line ? `:${e.line}` : ""}: ${e.message}`,
          ),
        ]);
      }
      if (validation.warnings.length > 0) {
        setWarnings((prev) => [
          ...prev,
          ...validation.warnings.map((w) => `${w.file}: ${w.message}`),
        ]);
      }

      setFiles(allFiles);

      // Auto-select first file and category
      if (allFiles.length > 0) {
        setActiveCategory(allFiles[0].category);
        setActiveFile(allFiles[0].path);
      }
    } catch (error) {
      setWarnings([
        `Generation failed: ${error instanceof Error ? error.message : "Unknown error"}`,
      ]);
    } finally {
      setIsGenerating(false);
    }
  }, [selectedIRNodes, profile, scope, tier]);

  // Copy file content to clipboard
  const handleCopy = useCallback(async (filePath: string) => {
    const file = files.find((f) => f.path === filePath);
    if (!file) return;

    try {
      await navigator.clipboard.writeText(file.content);
      setCopied(filePath);
      setTimeout(() => setCopied(null), 2000);
    } catch {
      // Clipboard API not available
    }
  }, [files]);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between h-9 px-3 border-b border-[var(--color-border-subtle)] flex-shrink-0">
        <span className="text-[11px] font-semibold text-[var(--mauve-12)] uppercase tracking-wider">
          Code
        </span>
        <span className="text-[10px] text-[var(--mauve-8)]">
          {profile.framework.id}
          {profile.framework.metaFramework && profile.framework.metaFramework !== "none"
            ? ` + ${profile.framework.metaFramework}`
            : ""}
        </span>
      </div>

      {/* Scope selector + Generate button */}
      <div className="flex items-center gap-2 px-3 py-2 border-b border-[var(--color-border-subtle)] flex-shrink-0">
        <select
          value={scope}
          onChange={(e) => setScope(e.target.value as TranslationScope)}
          className="flex-1 h-7 px-2 text-[11px] rounded bg-[var(--mauve-3)] border border-[var(--color-border-default)] text-[var(--mauve-12)] focus:outline-none focus:ring-1 focus:ring-[var(--violet-7)]"
        >
          {availableScopes.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>

        <button
          onClick={handleGenerate}
          disabled={isGenerating || selectedIRNodes.length === 0}
          className={cn(
            "flex items-center gap-1 h-7 px-3 rounded text-[11px] font-medium transition-colors",
            isGenerating || selectedIRNodes.length === 0
              ? "bg-[var(--mauve-4)] text-[var(--mauve-8)] cursor-not-allowed"
              : "bg-[var(--violet-9)] text-white hover:bg-[var(--violet-10)]",
          )}
        >
          {isGenerating ? (
            <>
              <span className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Generating...</span>
            </>
          ) : (
            <>
              <OmniIcon name="misc/sparkles" size={12} />
              <span>Generate</span>
            </>
          )}
        </button>
      </div>

      {/* Selection info */}
      <div className="px-3 py-1.5 text-[10px] text-[var(--mauve-8)] border-b border-[var(--color-border-subtle)] flex-shrink-0">
        {selectedIds.length > 0
          ? `${selectedIds.length} node${selectedIds.length === 1 ? "" : "s"} selected`
          : "No selection -- will use canvas nodes"}
      </div>

      {/* Content area */}
      {files.length === 0 ? (
        <EmptyState
          hasWarnings={warnings.length > 0}
          warnings={warnings}
          isGenerating={isGenerating}
        />
      ) : (
        <div className="flex flex-col flex-1 overflow-hidden">
          {/* Category tabs */}
          {availableCategories.length > 1 && (
            <div className="flex gap-0.5 px-2 pt-1.5 border-b border-[var(--color-border-subtle)] flex-shrink-0">
              {availableCategories.map((cat) => (
                <button
                  key={cat}
                  onClick={() => {
                    setActiveCategory(cat);
                    const firstInCategory = files.find((f) => f.category === cat);
                    if (firstInCategory) setActiveFile(firstInCategory.path);
                  }}
                  className={cn(
                    "px-2.5 py-1 text-[10px] font-medium rounded-t transition-colors",
                    activeCategory === cat
                      ? "bg-[var(--mauve-3)] text-[var(--mauve-12)] border-b-2 border-[var(--violet-9)]"
                      : "text-[var(--mauve-8)] hover:text-[var(--mauve-11)]",
                  )}
                >
                  {CATEGORY_LABELS[cat]}
                </button>
              ))}
            </div>
          )}

          {/* File tabs */}
          {filteredFiles.length > 0 && (
            <div className="flex gap-0.5 px-2 pt-1 overflow-x-auto flex-shrink-0 scrollbar-thin">
              {filteredFiles.map((file) => (
                <button
                  key={file.path}
                  onClick={() => setActiveFile(file.path)}
                  className={cn(
                    "flex items-center gap-1 px-2 py-1 text-[10px] rounded whitespace-nowrap transition-colors",
                    activeFile === file.path
                      ? "bg-[var(--mauve-4)] text-[var(--mauve-12)]"
                      : "text-[var(--mauve-8)] hover:text-[var(--mauve-11)] hover:bg-[var(--mauve-3)]",
                  )}
                >
                  <FileIcon language={file.language} />
                  <span>{file.path.split("/").pop()}</span>
                </button>
              ))}
            </div>
          )}

          {/* Code display */}
          {activeFileData ? (
            <div className="flex flex-col flex-1 overflow-hidden">
              {/* File info bar */}
              <div className="flex items-center justify-between px-3 py-1 border-b border-[var(--color-border-subtle)] flex-shrink-0">
                <span className="text-[10px] text-[var(--mauve-8)] truncate">
                  {activeFileData.path}
                </span>
                <button
                  onClick={() => handleCopy(activeFileData.path)}
                  className="flex items-center gap-1 px-2 py-0.5 text-[10px] text-[var(--mauve-9)] hover:text-[var(--mauve-12)] transition-colors rounded hover:bg-[var(--mauve-3)]"
                >
                  <OmniIcon
                    name={copied === activeFileData.path ? "status/check" : "action/copy"}
                    size={10}
                  />
                  <span>{copied === activeFileData.path ? "Copied" : "Copy"}</span>
                </button>
              </div>

              {/* Code content */}
              <ScrollArea className="flex-1">
                <pre className="p-3 text-[11px] leading-[1.6] font-mono text-[var(--mauve-11)] whitespace-pre overflow-x-auto">
                  <code>{activeFileData.content}</code>
                </pre>
              </ScrollArea>
            </div>
          ) : (
            <div className="flex items-center justify-center flex-1 text-[11px] text-[var(--mauve-8)]">
              Select a file to view its code
            </div>
          )}

          {/* Warnings */}
          {warnings.length > 0 && (
            <div className="border-t border-[var(--color-border-subtle)] flex-shrink-0">
              <WarningsList warnings={warnings} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Sub-components ─────────────────────────────────────────────────────────

function EmptyState({
  hasWarnings,
  warnings,
  isGenerating,
}: {
  hasWarnings: boolean;
  warnings: string[];
  isGenerating: boolean;
}) {
  if (isGenerating) {
    return (
      <div className="flex flex-col items-center justify-center flex-1 gap-3 p-6">
        <div className="w-6 h-6 border-2 border-[var(--violet-7)]/30 border-t-[var(--violet-9)] rounded-full animate-spin" />
        <span className="text-[11px] text-[var(--mauve-9)]">
          Generating code...
        </span>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center flex-1 gap-3 p-6">
      <div className="w-10 h-10 rounded-lg bg-[var(--mauve-3)] flex items-center justify-center">
        <OmniIcon name="content/code" size={20} className="text-[var(--mauve-8)]" />
      </div>
      <div className="text-center">
        <p className="text-[11px] font-medium text-[var(--mauve-11)]">
          No code generated yet
        </p>
        <p className="text-[10px] text-[var(--mauve-8)] mt-1">
          Select elements on the canvas and click Generate
          <br />
          to translate your design to code.
        </p>
      </div>

      {hasWarnings && <WarningsList warnings={warnings} />}
    </div>
  );
}

function WarningsList({ warnings }: { warnings: string[] }) {
  const [expanded, setExpanded] = useState(false);
  const visibleWarnings = expanded ? warnings : warnings.slice(0, 3);

  return (
    <div className="px-3 py-2">
      <div className="flex items-center gap-1 mb-1">
        <OmniIcon name="status/warning" size={12} className="text-[var(--yellow-9)]" />
        <span className="text-[10px] font-medium text-[var(--yellow-11)]">
          {warnings.length} warning{warnings.length === 1 ? "" : "s"}
        </span>
      </div>
      <ul className="space-y-0.5">
        {visibleWarnings.map((w, i) => (
          <li key={i} className="text-[10px] text-[var(--mauve-9)] leading-tight">
            {w}
          </li>
        ))}
      </ul>
      {warnings.length > 3 && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-[10px] text-[var(--violet-9)] hover:text-[var(--violet-11)] mt-1"
        >
          {expanded ? "Show less" : `Show ${warnings.length - 3} more`}
        </button>
      )}
    </div>
  );
}

function FileIcon({ language }: { language: string }) {
  const color =
    language === "tsx" || language === "jsx"
      ? "text-[var(--blue-9)]"
      : language === "typescript" || language === "javascript"
        ? "text-[var(--yellow-9)]"
        : language === "css" || language === "scss"
          ? "text-[var(--pink-9)]"
          : language === "vue" || language === "svelte"
            ? "text-[var(--green-9)]"
            : "text-[var(--mauve-8)]";

  return (
    <span className={cn("text-[10px] font-mono font-bold", color)}>
      {getFileIconLabel(language)}
    </span>
  );
}

function getFileIconLabel(language: string): string {
  switch (language) {
    case "tsx": return "TSX";
    case "jsx": return "JSX";
    case "typescript": return "TS";
    case "javascript": return "JS";
    case "css": return "CSS";
    case "scss": return "SCSS";
    case "vue": return "VUE";
    case "svelte": return "SVL";
    case "json": return "{}";
    case "yaml": return "YML";
    default: return "TXT";
  }
}

// ─── Canvas node to IR conversion helper ────────────────────────────────────

/**
 * Convert a canvas node to a minimal IR node for code generation.
 * This is a simplified conversion — the full pipeline would go through
 * the IR builder with token resolution.
 */
function canvasNodeToIR(node: CanvasNode): IRNode {
  return {
    id: node.id,
    type: node.type,
    name: node.name,
    parentId: node.parentId,
    pageId: "default",
    order: node.order,
    x: node.x,
    y: node.y,
    width: node.width,
    height: node.height,
    rotation: node.rotation ?? 0,
    fill: node.fill ?? null,
    fillOpacity: node.fillOpacity ?? 1,
    stroke: node.stroke ?? null,
    strokeWidth: node.strokeWidth ?? 0,
    opacity: node.opacity ?? 1,
    cornerRadius: node.cornerRadius ?? 0,
    visible: node.visible ?? true,
    locked: node.locked ?? false,
    text: node.text,
    textColor: node.textColor,
    fontFamily: node.fontFamily,
    fontSize: node.fontSize,
    fontWeight: node.fontWeight,
    lineHeight: node.lineHeight,
    letterSpacing: node.letterSpacing,
    textAlign: node.textAlign,
    layoutMode: node.layoutMode,
    primaryAxisSizing: node.primaryAxisSizing,
    counterAxisSizing: node.counterAxisSizing,
    paddingTop: node.paddingTop,
    paddingBottom: node.paddingBottom,
    paddingLeft: node.paddingLeft,
    paddingRight: node.paddingRight,
    itemSpacing: node.itemSpacing,
    counterAxisSpacing: node.counterAxisSpacing,
    primaryAxisAlignment: node.primaryAxisAlignment,
    counterAxisAlignment: node.counterAxisAlignment,
  };
}
