import { useState, useCallback, useMemo, useEffect, useRef } from "react";
import { useNavigate, useParams } from "react-router";
import { Sparkles, Sun, Moon, FileCode, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { useColorSystemStore } from "@/stores/colorSystem.store";
import { useProjectStore } from "@/stores/project.store";
import { useTeamContextStore } from "@/stores/teamContext.store";
import { generateColorSystem } from "@/lib/ai/client";
import { isValidHex } from "@/lib/color";
import { hexToOklch, oklchToHex } from "@/lib/colorSpaces";
import { hexToHsl, hslToHex } from "@/lib/color";
import {
  suggestSecondary,
  suggestAccent,
  computeHarmonyColors,
} from "@/lib/colorHarmony";
import type { HarmonyMode } from "@/lib/colorHarmony";
import { RADIX_STEPS } from "@/types/colorSystem";
import {
  BrandColorPicker,
  RadialColorWheel,
  HarmonyModeSelector,
  PaletteScaleHeader,
  ColorScaleRow,
  DataVizSection,
  ColorHarmonySuggestions,
  CodeFormatSelector,
} from "./components";
import { TOKEN_OUTPUT_FORMATS } from "./constants";
import type { TokenOutputConfig } from "@/core/context/types";

type PanelTab = "palette" | "dataviz";

export function DesignSystemPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  // Color system state from the persistent store
  const {
    brandColors,
    setBrandColor,
    colorSystem,
    setColorSystem,
    codeFormat,
    setCodeFormat,
  } = useColorSystemStore();

  const { profile, updateProfile } = useTeamContextStore();
  const { projects, updateProject } = useProjectStore();
  const project = projects.find((p) => p.id === projectId);

  // Local UI state
  const [mode, setMode] = useState<"light" | "dark">("dark");
  const [showAlpha, setShowAlpha] = useState(false);
  const [activeTab, setActiveTab] = useState<PanelTab>("palette");
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [harmonyMode, setHarmonyMode] = useState<HarmonyMode>("freeform");
  const [brightnessClamp, setBrightnessClamp] = useState(false);
  const [lightnessClamp, setLightnessClamp] = useState(false);
  const generated = colorSystem !== null;

  // Ref to track if we're currently applying harmony (prevent loops)
  const applyingHarmony = useRef(false);

  // ── Harmony auto-computation ─────────────────────────────────────────────
  useEffect(() => {
    if (harmonyMode === "freeform" || applyingHarmony.current) return;
    if (!brandColors.primary || !isValidHex(brandColors.primary)) return;

    applyingHarmony.current = true;
    const { secondary, accent } = computeHarmonyColors(brandColors.primary, harmonyMode);
    if (secondary) setBrandColor("secondary", secondary);
    if (accent) setBrandColor("accent", accent);
    // For complementary, clear accent since it only uses secondary
    if (harmonyMode === "complementary") setBrandColor("accent", "");

    // Allow the ref to reset on next tick
    requestAnimationFrame(() => {
      applyingHarmony.current = false;
    });
  }, [brandColors.primary, harmonyMode, setBrandColor]);

  // ── Clamped primary for wheel display ────────────────────────────────────
  const clampedPrimary = useMemo(() => {
    if (!brightnessClamp && !lightnessClamp) return null;
    if (!brandColors.primary || !isValidHex(brandColors.primary)) return null;

    if (brightnessClamp) {
      const oklch = hexToOklch(brandColors.primary);
      if (!oklch) return null;
      const [, C, H] = oklch;
      return oklchToHex(0.55, C, H); // Radix step 9 equivalent
    }

    if (lightnessClamp) {
      const hsl = hexToHsl(brandColors.primary);
      if (!hsl) return null;
      return hslToHex(hsl[0], hsl[1], 50); // HSL L=50%
    }

    return null;
  }, [brandColors.primary, brightnessClamp, lightnessClamp]);

  // ── Harmony suggestions ─────────────────────────────────────────────────
  const secondarySuggestions = useMemo(() => {
    if (!brandColors.primary || !isValidHex(brandColors.primary)) return [];
    if (brandColors.secondary && isValidHex(brandColors.secondary)) return [];
    return suggestSecondary(brandColors.primary);
  }, [brandColors.primary, brandColors.secondary]);

  const accentSuggestions = useMemo(() => {
    if (!brandColors.primary || !isValidHex(brandColors.primary)) return [];
    if (brandColors.accent && isValidHex(brandColors.accent)) return [];
    return suggestAccent(brandColors.primary);
  }, [brandColors.primary, brandColors.accent]);

  // ── Token output toggles ──────────────────────────────────────────────
  const tokenFormats = profile.tokenOutput.formats;

  const toggleTokenFormat = (format: TokenOutputConfig["formats"][number]) => {
    const current = [...tokenFormats];
    const idx = current.indexOf(format);
    if (idx >= 0) {
      current.splice(idx, 1);
    } else {
      current.push(format);
    }
    updateProfile({
      tokenOutput: { ...profile.tokenOutput, formats: current },
    });
  };

  // ── Generate ────────────────────────────────────────────────────────────
  const handleGenerate = useCallback(async () => {
    if (!brandColors.primary || !isValidHex(brandColors.primary)) return;
    setError(null);
    setGenerating(true);

    const timeout = setTimeout(() => {
      setGenerating(false);
      setError("Generation timed out. Please try again.");
    }, 90_000);

    try {
      const result = await generateColorSystem({
        primary: brandColors.primary,
        secondary: brandColors.secondary,
        accent: brandColors.accent,
      });

      if (result) {
        result.name = project?.name ?? "Untitled";
        setColorSystem(result);
        if (projectId) {
          updateProject(projectId, { colorSystemId: result.id });
        }
      } else {
        setError("Failed to parse the generated color system. Please try again.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred.");
    } finally {
      clearTimeout(timeout);
      setGenerating(false);
    }
  }, [brandColors, project?.name, projectId, setColorSystem, updateProject]);

  const handleBackToCanvas = () => {
    navigate(`/workspace/${projectId}`);
  };

  const palettesToShow = colorSystem
    ? Object.values(colorSystem.palettes)
    : [];

  const hasDataViz = Boolean(colorSystem?.dataViz?.colors?.length);

  return (
    <div className="flex flex-col h-screen bg-[var(--color-surface-0)]">
      {/* ── Top bar ──────────────────────────────────────────────────────── */}
      <div className="flex items-center gap-3 px-5 h-11 border-b border-[var(--color-border-subtle)] bg-[var(--color-surface-1)] flex-shrink-0">
        <button
          onClick={handleBackToCanvas}
          className="flex items-center gap-1.5 text-[11px] text-[var(--mauve-10)] hover:text-[var(--mauve-12)] transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          Canvas
        </button>
        <div className="h-4 w-px bg-[var(--mauve-5)]" />
        <h1 className="text-[12px] font-semibold text-[var(--mauve-12)]">
          Design System
        </h1>
        {generated && (
          <Badge
            variant="outline"
            className="text-[9px] border-[var(--green-9)] text-[var(--green-11)] bg-transparent ml-1"
          >
            Generated
          </Badge>
        )}
      </div>

      {/* ── Main content ─────────────────────────────────────────────────── */}
      <div className="flex flex-1 min-h-0">
        {/* Left sidebar: color inputs */}
        <div className="w-64 flex-shrink-0 border-r border-[var(--color-border-subtle)] px-5 py-5 flex flex-col gap-4 overflow-y-auto bg-[var(--color-surface-1)]">
          <RadialColorWheel
            brandColors={brandColors}
            harmonyMode={harmonyMode}
            onColorChange={(slot, hex) => setBrandColor(slot, hex)}
          />

          <HarmonyModeSelector value={harmonyMode} onChange={setHarmonyMode} />

          {/* Brightness / Lightness clamping */}
          <div className="flex flex-col gap-1.5">
            <label className="flex items-center gap-2 cursor-pointer group">
              <Checkbox
                checked={brightnessClamp}
                onCheckedChange={(v) => {
                  setBrightnessClamp(v === true);
                  if (v === true) setLightnessClamp(false);
                }}
                className="mt-0"
              />
              <span className={cn(
                "text-[10px] font-medium",
                brightnessClamp ? "text-[var(--mauve-12)]" : "text-[var(--mauve-11)] group-hover:text-[var(--mauve-12)]",
              )}>
                Brightness clamp (OKLCH)
              </span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer group">
              <Checkbox
                checked={lightnessClamp}
                onCheckedChange={(v) => {
                  setLightnessClamp(v === true);
                  if (v === true) setBrightnessClamp(false);
                }}
                className="mt-0"
              />
              <span className={cn(
                "text-[10px] font-medium",
                lightnessClamp ? "text-[var(--mauve-12)]" : "text-[var(--mauve-11)] group-hover:text-[var(--mauve-12)]",
              )}>
                Lightness clamp (HSL 50%)
              </span>
            </label>
            {clampedPrimary && (
              <div className="flex items-center gap-1.5 mt-0.5">
                <div
                  className="w-4 h-4 rounded border border-[var(--mauve-6)]"
                  style={{ background: clampedPrimary }}
                />
                <span className="text-[9px] text-[var(--mauve-9)] font-mono">
                  Clamped: {clampedPrimary}
                </span>
              </div>
            )}
          </div>

          <BrandColorPicker
            label="Primary"
            value={brandColors.primary}
            onChange={(v) => setBrandColor("primary", v)}
            required
          />
          <BrandColorPicker
            label="Secondary"
            value={brandColors.secondary}
            onChange={(v) => setBrandColor("secondary", v)}
          />
          {harmonyMode === "freeform" && secondarySuggestions.length > 0 && (
            <ColorHarmonySuggestions
              suggestions={secondarySuggestions}
              onSelect={(hex) => setBrandColor("secondary", hex)}
            />
          )}
          <BrandColorPicker
            label="Accent"
            value={brandColors.accent}
            onChange={(v) => setBrandColor("accent", v)}
          />
          {harmonyMode === "freeform" && accentSuggestions.length > 0 && (
            <ColorHarmonySuggestions
              suggestions={accentSuggestions}
              onSelect={(hex) => setBrandColor("accent", hex)}
            />
          )}

          <Button
            onClick={handleGenerate}
            disabled={
              generating ||
              !brandColors.primary ||
              !isValidHex(brandColors.primary)
            }
            className="mt-2 bg-[var(--violet-9)] hover:bg-[var(--violet-10)] text-white border-0 disabled:opacity-50"
          >
            <span className="flex items-center justify-center gap-2">
              {generating ? (
                <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <Sparkles className="w-3.5 h-3.5" />
              )}
              <span>
                {generating
                  ? "Generating\u2026"
                  : generated
                    ? "Regenerate"
                    : "Generate"}
              </span>
            </span>
          </Button>

          {error && (
            <p className="text-[10px] text-[var(--red-9)] leading-relaxed">{error}</p>
          )}

          {/* Code format — always visible */}
          <CodeFormatSelector value={codeFormat} onChange={setCodeFormat} />

          {/* Light / Dark toggle — only after generation */}
          {generated && (
            <div className="flex flex-col gap-3">
              <div className="flex rounded-lg border border-[var(--mauve-5)] overflow-hidden">
                <button
                  onClick={() => setMode("light")}
                  className={cn(
                    "flex-1 flex items-center justify-center gap-1 py-1.5 text-[10px] transition-colors",
                    mode === "light"
                      ? "bg-[var(--mauve-4)] text-[var(--mauve-12)]"
                      : "text-[var(--mauve-9)] hover:text-[var(--mauve-11)]",
                  )}
                >
                  <Sun className="w-3 h-3" />
                  Light
                </button>
                <button
                  onClick={() => setMode("dark")}
                  className={cn(
                    "flex-1 flex items-center justify-center gap-1 py-1.5 text-[10px] transition-colors",
                    mode === "dark"
                      ? "bg-[var(--mauve-4)] text-[var(--mauve-12)]"
                      : "text-[var(--mauve-9)] hover:text-[var(--mauve-11)]",
                  )}
                >
                  <Moon className="w-3 h-3" />
                  Dark
                </button>
              </div>

              {/* Alpha toggle */}
              <label className="flex items-center gap-2 cursor-pointer group">
                <Checkbox
                  checked={showAlpha}
                  onCheckedChange={(v) => setShowAlpha(v === true)}
                  className="mt-0"
                />
                <span
                  className={cn(
                    "text-[10px] font-medium",
                    showAlpha
                      ? "text-[var(--mauve-12)]"
                      : "text-[var(--mauve-11)] group-hover:text-[var(--mauve-12)]",
                  )}
                >
                  Show alpha variants
                </span>
              </label>
            </div>
          )}

          {/* Token Output Configuration */}
          {profile.tier >= 1 && (
            <div className="border-t border-[var(--mauve-4)] pt-4 mt-1">
              <div className="flex items-center gap-1.5 mb-3">
                <FileCode className="w-3 h-3 text-[var(--violet-11)]" />
                <label className="text-[10px] font-semibold text-[var(--mauve-10)] uppercase tracking-wider">
                  Token Output
                </label>
              </div>
              <div className="flex flex-col gap-2">
                {TOKEN_OUTPUT_FORMATS.map((fmt) => {
                  const checked = tokenFormats.includes(fmt.value);
                  return (
                    <label key={fmt.value} className="flex items-start gap-2 cursor-pointer group">
                      <Checkbox
                        checked={checked}
                        onCheckedChange={() => toggleTokenFormat(fmt.value)}
                        className="mt-0.5"
                      />
                      <div>
                        <span
                          className={cn(
                            "text-[10px] font-medium block leading-tight",
                            checked
                              ? "text-[var(--mauve-12)]"
                              : "text-[var(--mauve-11)] group-hover:text-[var(--mauve-12)]",
                          )}
                        >
                          {fmt.label}
                        </span>
                        <span className="text-[9px] text-[var(--mauve-9)]">
                          {fmt.description}
                        </span>
                      </div>
                    </label>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Right: palette preview */}
        <div className="flex-1 flex flex-col min-h-0">
          {/* Tab bar — only when generated */}
          {generated && (
            <div className="flex items-center gap-1 px-6 pt-4 pb-2 flex-shrink-0">
              <button
                onClick={() => setActiveTab("palette")}
                className={cn(
                  "px-3 py-1 rounded-md text-[11px] font-medium transition-colors",
                  activeTab === "palette"
                    ? "bg-[var(--mauve-4)] text-[var(--mauve-12)]"
                    : "text-[var(--mauve-9)] hover:text-[var(--mauve-11)] hover:bg-[var(--mauve-3)]",
                )}
              >
                Palette
              </button>
              {hasDataViz && (
                <button
                  onClick={() => setActiveTab("dataviz")}
                  className={cn(
                    "px-3 py-1 rounded-md text-[11px] font-medium transition-colors",
                    activeTab === "dataviz"
                      ? "bg-[var(--mauve-4)] text-[var(--mauve-12)]"
                      : "text-[var(--mauve-9)] hover:text-[var(--mauve-11)] hover:bg-[var(--mauve-3)]",
                  )}
                >
                  Data Viz
                </button>
              )}
              <div className="flex-1" />
              <span className="text-[10px] text-[var(--mauve-9)]">
                {palettesToShow.length} palettes &middot; {mode} mode
                {showAlpha ? " &middot; alpha" : ""}
              </span>
            </div>
          )}

          {/* Scrollable content area */}
          <div className="flex-1 relative">
            <div className="absolute inset-0">
              <ScrollArea className="h-full">
                <div className="px-6 py-5">
                  {!generated ? (
                    <div className="flex flex-col items-center justify-center h-48 gap-3">
                      <div className="w-10 h-10 rounded-xl border border-dashed border-[var(--mauve-6)] flex items-center justify-center">
                        <Sparkles className="w-5 h-5 text-[var(--mauve-7)]" />
                      </div>
                      <p className="text-xs text-[var(--mauve-9)] text-center">
                        Enter your brand colors and click Generate to preview your color system.
                      </p>

                      {/* Ghost scale rows */}
                      <div className="w-full space-y-3 mt-2 opacity-30 pointer-events-none">
                        {["Primary", "Neutral", "Success"].map((label) => (
                          <div key={label} className="flex flex-col gap-1">
                            <span className="text-[10px] text-[var(--mauve-9)]">{label}</span>
                            <div
                              className="grid gap-0.5"
                              style={{ gridTemplateColumns: "repeat(12, 1fr)" }}
                            >
                              {RADIX_STEPS.map((s) => (
                                <div
                                  key={s}
                                  className="bg-[var(--mauve-4)] rounded"
                                  style={{ minHeight: 32 }}
                                />
                              ))}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : activeTab === "palette" ? (
                    <div className="space-y-3">
                      <PaletteScaleHeader />
                      {palettesToShow.map((palette) => (
                        <ColorScaleRow
                          key={palette.key}
                          palette={palette}
                          mode={mode}
                          codeFormat={codeFormat}
                          showAlpha={showAlpha}
                        />
                      ))}
                    </div>
                  ) : (
                    colorSystem && (
                      <DataVizSection
                        colorSystem={colorSystem}
                        codeFormat={codeFormat}
                        mode={mode}
                        showAlpha={showAlpha}
                      />
                    )
                  )}
                </div>
              </ScrollArea>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
