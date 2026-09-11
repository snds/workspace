// ─── Environments Panel ────────────────────────────────────────────────────────
// Manage dev/staging/prod environments, environment variables, and .env export.
// Only visible when tier >= 3.
// ──────────────────────────────────────────────────────────────────────────────

import { useState } from "react";
import { useInfraStore } from "@/stores/infra.store";
import { useTeamContextStore } from "@/stores/teamContext.store";
import { generateEnvFile, validateEnvironment } from "@/core/infra/environments";
import { cn } from "@/lib/utils";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { ScrollArea } from "@/components/ui/scroll-area";

export function EnvironmentsPanel() {
  const isTierActive = useTeamContextStore((s) => s.isTierActive);
  if (!isTierActive(3)) return null;

  return <EnvironmentsPanelInner />;
}

function EnvironmentsPanelInner() {
  const {
    environments,
    activeEnvironmentId,
    setActiveEnvironment,
    setEnvVariable,
    removeEnvVariable,
  } = useInfraStore();

  const [newVarKey, setNewVarKey] = useState("");
  const [newVarValue, setNewVarValue] = useState("");
  const [newVarSecret, setNewVarSecret] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const activeEnv = environments.find((e) => e.id === activeEnvironmentId);
  const warnings = activeEnv ? validateEnvironment(activeEnv) : [];

  const handleAddVariable = () => {
    if (!newVarKey.trim() || !activeEnv) return;
    setEnvVariable(activeEnv.id, newVarKey.trim(), newVarValue, newVarSecret);
    setNewVarKey("");
    setNewVarValue("");
    setNewVarSecret(false);
  };

  const handleExportEnv = () => {
    if (!activeEnv) return;
    const content = generateEnvFile(activeEnv);
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `.env.${activeEnv.id}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-[var(--color-border-subtle)]">
        <span className="text-xs font-semibold text-[var(--mauve-12)] uppercase tracking-wider">
          Environments
        </span>
        <Badge variant="outline" className="text-[10px] px-1.5 py-0">
          Tier 3
        </Badge>
      </div>

      {/* Environment tabs */}
      <Tabs
        value={activeEnvironmentId}
        onValueChange={setActiveEnvironment}
        className="flex-1 flex flex-col min-h-0"
      >
        <div className="px-3 pt-2">
          <TabsList className="w-full">
            {environments.map((env) => (
              <TabsTrigger
                key={env.id}
                value={env.id}
                className="flex items-center gap-1.5 text-xs flex-1"
              >
                <span
                  className="w-2 h-2 rounded-full flex-shrink-0"
                  style={{ backgroundColor: env.color }}
                />
                {env.name}
              </TabsTrigger>
            ))}
          </TabsList>
        </div>

        {environments.map((env) => (
          <TabsContent
            key={env.id}
            value={env.id}
            className="flex-1 flex flex-col min-h-0 px-3 pb-3"
          >
            {/* Environment info */}
            <div className="flex items-center gap-2 py-2">
              <Badge
                variant="outline"
                className="text-[10px] capitalize"
                style={{
                  borderColor: env.color,
                  color: env.color,
                }}
              >
                {env.type}
              </Badge>
              {env.url && (
                <span className="text-[10px] text-[var(--mauve-9)] truncate">
                  {env.url}
                </span>
              )}
            </div>

            {/* Variables list */}
            <div className="text-[11px] font-medium text-[var(--mauve-11)] mb-1">
              Variables ({Object.keys(env.variables).length})
            </div>

            <ScrollArea className="flex-1 min-h-0">
              <div className="space-y-1">
                {Object.values(env.variables).map((variable) => (
                  <div
                    key={variable.key}
                    className="flex items-center gap-1.5 group"
                  >
                    <span className="text-[11px] font-mono text-[var(--mauve-11)] min-w-0 truncate flex-shrink-0 max-w-[120px]">
                      {variable.key}
                    </span>
                    <span className="text-[var(--mauve-7)] text-[10px]">=</span>
                    <span
                      className={cn(
                        "text-[11px] font-mono min-w-0 truncate flex-1",
                        variable.isSecret
                          ? "text-[var(--mauve-8)]"
                          : "text-[var(--mauve-11)]",
                      )}
                    >
                      {variable.isSecret ? "********" : variable.value}
                    </span>
                    {variable.isSecret && (
                      <Badge
                        variant="outline"
                        className="text-[9px] px-1 py-0 h-4 flex-shrink-0"
                      >
                        secret
                      </Badge>
                    )}
                    <button
                      onClick={() => removeEnvVariable(env.id, variable.key)}
                      className="text-[var(--mauve-8)] hover:text-[var(--mauve-11)] opacity-0 group-hover:opacity-100 transition-opacity text-xs flex-shrink-0"
                    >
                      x
                    </button>
                  </div>
                ))}
                {Object.keys(env.variables).length === 0 && (
                  <p className="text-[11px] text-[var(--mauve-8)] italic py-2">
                    No variables configured
                  </p>
                )}
              </div>
            </ScrollArea>

            {/* Warnings */}
            {warnings.length > 0 && (
              <div className="mt-2 space-y-0.5">
                {warnings.map((w, i) => (
                  <p key={i} className="text-[10px] text-amber-400">
                    {w}
                  </p>
                ))}
              </div>
            )}

            {/* Add variable form */}
            <div className="mt-2 pt-2 border-t border-[var(--color-border-subtle)] space-y-1.5">
              <div className="flex gap-1.5">
                <Input
                  placeholder="KEY"
                  value={newVarKey}
                  onChange={(e) => setNewVarKey(e.target.value)}
                  className="h-7 text-xs font-mono flex-1"
                />
                <Input
                  placeholder="value"
                  value={newVarValue}
                  onChange={(e) => setNewVarValue(e.target.value)}
                  type={newVarSecret ? "password" : "text"}
                  className="h-7 text-xs font-mono flex-1"
                />
              </div>
              <div className="flex items-center justify-between">
                <label className="flex items-center gap-1.5 cursor-pointer">
                  <Switch
                    size="sm"
                    checked={newVarSecret}
                    onCheckedChange={setNewVarSecret}
                  />
                  <span className="text-[10px] text-[var(--mauve-9)]">
                    Secret
                  </span>
                </label>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={handleAddVariable}
                  disabled={!newVarKey.trim()}
                  className="h-6 text-[10px] px-2"
                >
                  Add Variable
                </Button>
              </div>
            </div>

            {/* Export / Preview */}
            <div className="mt-2 flex gap-1.5">
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowPreview(!showPreview)}
                className="h-6 text-[10px] px-2 flex-1"
              >
                {showPreview ? "Hide" : "Preview"} .env
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={handleExportEnv}
                className="h-6 text-[10px] px-2 flex-1"
              >
                Export .env
              </Button>
            </div>

            {/* Env file preview */}
            {showPreview && activeEnv && (
              <pre className="mt-2 p-2 rounded bg-[var(--mauve-2)] border border-[var(--color-border-subtle)] text-[10px] font-mono text-[var(--mauve-11)] overflow-auto max-h-32">
                {generateEnvFile(activeEnv)}
              </pre>
            )}
          </TabsContent>
        ))}
      </Tabs>
    </div>
  );
}
