// ─── Feature Flags Panel ───────────────────────────────────────────────────────
// Manage feature flags, per-environment overrides, and A/B tests.
// Only visible when tier >= 3.
// ──────────────────────────────────────────────────────────────────────────────

import { useState } from "react";
import { useInfraStore } from "@/stores/infra.store";
import { useTeamContextStore } from "@/stores/teamContext.store";
import { createFeatureFlag, createABTest } from "@/core/infra/featureFlags";
import type { FeatureFlag, ABTestVariant } from "@/core/infra/types";
import { cn } from "@/lib/utils";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Slider } from "@/components/ui/slider";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export function FeatureFlagsPanel() {
  const isTierActive = useTeamContextStore((s) => s.isTierActive);
  if (!isTierActive(3)) return null;

  return <FeatureFlagsPanelInner />;
}

function FeatureFlagsPanelInner() {
  const {
    featureFlags,
    abTests,
    environments,
    activeEnvironmentId,
    addFlag,
    removeFlag,
    toggleFlag,
    setFlagOverride,
    addABTest,
    removeABTest,
    updateABTest,
  } = useInfraStore();

  const [showCreateFlag, setShowCreateFlag] = useState(false);
  const [showCreateTest, setShowCreateTest] = useState(false);
  const [expandedFlag, setExpandedFlag] = useState<string | null>(null);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-[var(--color-border-subtle)]">
        <span className="text-xs font-semibold text-[var(--mauve-12)] uppercase tracking-wider">
          Feature Flags
        </span>
        <div className="flex items-center gap-1">
          <Badge variant="outline" className="text-[10px] px-1.5 py-0">
            {featureFlags.length}
          </Badge>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => setShowCreateFlag(true)}
            className="h-5 w-5 p-0 text-[var(--mauve-9)] hover:text-[var(--mauve-12)]"
          >
            +
          </Button>
        </div>
      </div>

      <ScrollArea className="flex-1">
        <div className="px-3 py-2 space-y-1">
          {/* Flag list */}
          {featureFlags.map((flag) => (
            <FlagRow
              key={flag.key}
              flag={flag}
              environments={environments}
              activeEnvironmentId={activeEnvironmentId}
              expanded={expandedFlag === flag.key}
              onToggle={() => toggleFlag(flag.key)}
              onExpand={() =>
                setExpandedFlag(
                  expandedFlag === flag.key ? null : flag.key,
                )
              }
              onRemove={() => removeFlag(flag.key)}
              onSetOverride={(envId, value) =>
                setFlagOverride(flag.key, envId, value)
              }
            />
          ))}

          {featureFlags.length === 0 && (
            <p className="text-[11px] text-[var(--mauve-8)] italic py-4 text-center">
              No feature flags yet
            </p>
          )}

          {/* A/B Tests section */}
          {abTests.length > 0 && (
            <>
              <div className="flex items-center justify-between pt-3 pb-1">
                <span className="text-[11px] font-medium text-[var(--mauve-11)]">
                  A/B Tests
                </span>
                <Badge variant="outline" className="text-[10px] px-1.5 py-0">
                  {abTests.length}
                </Badge>
              </div>
              {abTests.map((test) => (
                <ABTestRow
                  key={test.id}
                  test={test}
                  onRemove={() => removeABTest(test.id)}
                  onUpdateStatus={(status) =>
                    updateABTest(test.id, { status })
                  }
                />
              ))}
            </>
          )}
        </div>
      </ScrollArea>

      {/* Bottom actions */}
      <div className="px-3 py-2 border-t border-[var(--color-border-subtle)] flex gap-1.5">
        <Button
          size="sm"
          variant="outline"
          onClick={() => setShowCreateFlag(true)}
          className="h-6 text-[10px] px-2 flex-1"
        >
          New Flag
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={() => setShowCreateTest(true)}
          disabled={featureFlags.length === 0}
          className="h-6 text-[10px] px-2 flex-1"
        >
          New A/B Test
        </Button>
      </div>

      {/* Create Flag Dialog */}
      <CreateFlagDialog
        open={showCreateFlag}
        onOpenChange={setShowCreateFlag}
        onCreate={(flag) => {
          addFlag(flag);
          setShowCreateFlag(false);
        }}
      />

      {/* Create A/B Test Dialog */}
      <CreateABTestDialog
        open={showCreateTest}
        onOpenChange={setShowCreateTest}
        flags={featureFlags}
        onCreate={(test) => {
          addABTest(test);
          setShowCreateTest(false);
        }}
      />
    </div>
  );
}

// ─── Flag Row ──────────────────────────────────────────────────────────────────

function FlagRow({
  flag,
  environments,
  activeEnvironmentId,
  expanded,
  onToggle,
  onExpand,
  onRemove,
  onSetOverride,
}: {
  flag: FeatureFlag;
  environments: { id: string; name: string; color: string }[];
  activeEnvironmentId: string;
  expanded: boolean;
  onToggle: () => void;
  onExpand: () => void;
  onRemove: () => void;
  onSetOverride: (envId: string, value: unknown) => void;
}) {
  return (
    <div className="rounded border border-[var(--color-border-subtle)] bg-[var(--mauve-2)]">
      {/* Main row */}
      <div className="flex items-center gap-2 px-2 py-1.5">
        <Switch size="sm" checked={flag.enabled} onCheckedChange={onToggle} />
        <button
          onClick={onExpand}
          className="flex-1 text-left min-w-0"
        >
          <div className="text-[11px] font-medium text-[var(--mauve-12)] truncate">
            {flag.name}
          </div>
          <div className="text-[10px] font-mono text-[var(--mauve-8)] truncate">
            {flag.key}
          </div>
        </button>
        <Badge
          variant="outline"
          className={cn(
            "text-[9px] px-1 py-0 h-4",
            flag.enabled
              ? "border-green-500/50 text-green-400"
              : "border-[var(--mauve-6)] text-[var(--mauve-8)]",
          )}
        >
          {flag.type}
        </Badge>
        <button
          onClick={onRemove}
          className="text-[var(--mauve-8)] hover:text-[var(--mauve-11)] text-xs"
        >
          x
        </button>
      </div>

      {/* Expanded: per-environment overrides */}
      {expanded && (
        <div className="px-2 pb-2 pt-1 border-t border-[var(--color-border-subtle)] space-y-1">
          {flag.description && (
            <p className="text-[10px] text-[var(--mauve-9)] mb-1">
              {flag.description}
            </p>
          )}
          <div className="text-[10px] text-[var(--mauve-10)] font-medium mb-1">
            Per-environment values:
          </div>
          {environments.map((env) => {
            const override = flag.environmentOverrides[env.id];
            const isActive = env.id === activeEnvironmentId;
            return (
              <div
                key={env.id}
                className={cn(
                  "flex items-center gap-2",
                  isActive && "bg-[var(--mauve-3)] rounded px-1 -mx-1",
                )}
              >
                <span
                  className="w-1.5 h-1.5 rounded-full flex-shrink-0"
                  style={{ backgroundColor: env.color }}
                />
                <span className="text-[10px] text-[var(--mauve-11)] w-16 flex-shrink-0">
                  {env.name}
                </span>
                {flag.type === "boolean" ? (
                  <Switch
                    size="sm"
                    checked={
                      (override ?? flag.defaultValue) === true
                    }
                    onCheckedChange={(val) =>
                      onSetOverride(env.id, val)
                    }
                  />
                ) : (
                  <Input
                    className="h-5 text-[10px] font-mono flex-1"
                    placeholder={String(flag.defaultValue)}
                    value={override !== undefined ? String(override) : ""}
                    onChange={(e) => {
                      const val =
                        flag.type === "number"
                          ? Number(e.target.value)
                          : e.target.value;
                      onSetOverride(env.id, val);
                    }}
                  />
                )}
              </div>
            );
          })}
          {flag.tags && flag.tags.length > 0 && (
            <div className="flex gap-1 mt-1">
              {flag.tags.map((tag) => (
                <Badge
                  key={tag}
                  variant="secondary"
                  className="text-[9px] px-1 py-0 h-4"
                >
                  {tag}
                </Badge>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─── A/B Test Row ──────────────────────────────────────────────────────────────

function ABTestRow({
  test,
  onRemove,
  onUpdateStatus,
}: {
  test: {
    id: string;
    name: string;
    flagKey: string;
    variants: ABTestVariant[];
    trafficSplit: number[];
    status: string;
    trackingEvent: string;
  };
  onRemove: () => void;
  onUpdateStatus: (status: "draft" | "running" | "paused" | "completed") => void;
}) {
  const statusColor: Record<string, string> = {
    draft: "var(--mauve-8)",
    running: "#22c55e",
    paused: "#f59e0b",
    completed: "#6366f1",
  };

  return (
    <div className="rounded border border-[var(--color-border-subtle)] bg-[var(--mauve-2)] px-2 py-1.5">
      <div className="flex items-center gap-2">
        <span
          className="w-2 h-2 rounded-full flex-shrink-0"
          style={{ backgroundColor: statusColor[test.status] }}
        />
        <span className="text-[11px] font-medium text-[var(--mauve-12)] flex-1 truncate">
          {test.name}
        </span>
        <Badge
          variant="outline"
          className="text-[9px] px-1 py-0 h-4 capitalize"
        >
          {test.status}
        </Badge>
        <button
          onClick={onRemove}
          className="text-[var(--mauve-8)] hover:text-[var(--mauve-11)] text-xs"
        >
          x
        </button>
      </div>

      {/* Variants with traffic split */}
      <div className="mt-1 space-y-0.5">
        {test.variants.map((variant, i) => (
          <div key={variant.id} className="flex items-center gap-2">
            <span className="text-[10px] text-[var(--mauve-9)] w-20 truncate">
              {variant.name}
            </span>
            <div className="flex-1 h-1.5 bg-[var(--mauve-4)] rounded-full overflow-hidden">
              <div
                className="h-full bg-[var(--violet-9)] rounded-full"
                style={{ width: `${test.trafficSplit[i]}%` }}
              />
            </div>
            <span className="text-[10px] text-[var(--mauve-8)] w-8 text-right">
              {test.trafficSplit[i]}%
            </span>
          </div>
        ))}
      </div>

      {/* Status controls */}
      <div className="mt-1.5 flex gap-1">
        {test.status === "draft" && (
          <Button
            size="sm"
            variant="outline"
            onClick={() => onUpdateStatus("running")}
            className="h-5 text-[9px] px-1.5"
          >
            Start
          </Button>
        )}
        {test.status === "running" && (
          <Button
            size="sm"
            variant="outline"
            onClick={() => onUpdateStatus("paused")}
            className="h-5 text-[9px] px-1.5"
          >
            Pause
          </Button>
        )}
        {test.status === "paused" && (
          <Button
            size="sm"
            variant="outline"
            onClick={() => onUpdateStatus("running")}
            className="h-5 text-[9px] px-1.5"
          >
            Resume
          </Button>
        )}
        {(test.status === "running" || test.status === "paused") && (
          <Button
            size="sm"
            variant="outline"
            onClick={() => onUpdateStatus("completed")}
            className="h-5 text-[9px] px-1.5"
          >
            Complete
          </Button>
        )}
      </div>
    </div>
  );
}

// ─── Create Flag Dialog ────────────────────────────────────────────────────────

function CreateFlagDialog({
  open,
  onOpenChange,
  onCreate,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreate: (flag: FeatureFlag) => void;
}) {
  const [key, setKey] = useState("");
  const [name, setName] = useState("");
  const [type, setType] = useState<FeatureFlag["type"]>("boolean");

  const handleCreate = () => {
    if (!key.trim() || !name.trim()) return;
    onCreate(createFeatureFlag(key.trim(), name.trim(), type));
    setKey("");
    setName("");
    setType("boolean");
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-sm">Create Feature Flag</DialogTitle>
        </DialogHeader>
        <div className="space-y-3">
          <div>
            <label className="text-[11px] text-[var(--mauve-11)] mb-1 block">
              Flag Key
            </label>
            <Input
              placeholder="e.g. new-checkout-flow"
              value={key}
              onChange={(e) => setKey(e.target.value)}
              className="h-8 text-xs font-mono"
            />
          </div>
          <div>
            <label className="text-[11px] text-[var(--mauve-11)] mb-1 block">
              Display Name
            </label>
            <Input
              placeholder="e.g. New Checkout Flow"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="h-8 text-xs"
            />
          </div>
          <div>
            <label className="text-[11px] text-[var(--mauve-11)] mb-1 block">
              Type
            </label>
            <Select
              value={type}
              onValueChange={(v) => setType(v as FeatureFlag["type"])}
            >
              <SelectTrigger className="h-8 text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="boolean">Boolean</SelectItem>
                <SelectItem value="string">String</SelectItem>
                <SelectItem value="number">Number</SelectItem>
                <SelectItem value="json">JSON</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
        <DialogFooter>
          <Button
            size="sm"
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="text-xs"
          >
            Cancel
          </Button>
          <Button
            size="sm"
            onClick={handleCreate}
            disabled={!key.trim() || !name.trim()}
            className="text-xs"
          >
            Create
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// ─── Create A/B Test Dialog ────────────────────────────────────────────────────

function CreateABTestDialog({
  open,
  onOpenChange,
  flags,
  onCreate,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  flags: FeatureFlag[];
  onCreate: (test: ReturnType<typeof createABTest>) => void;
}) {
  const [name, setName] = useState("");
  const [flagKey, setFlagKey] = useState(flags[0]?.key ?? "");
  const [trackingEvent, setTrackingEvent] = useState("");
  const [variantA, setVariantA] = useState("Control");
  const [variantB, setVariantB] = useState("Treatment");
  const [split, setSplit] = useState([50]);

  const handleCreate = () => {
    if (!name.trim() || !flagKey || !trackingEvent.trim()) return;

    const variants: ABTestVariant[] = [
      {
        id: "control",
        name: variantA || "Control",
        flagValue: false,
      },
      {
        id: "treatment",
        name: variantB || "Treatment",
        flagValue: true,
      },
    ];

    const test = createABTest(
      name.trim(),
      flagKey,
      variants,
      trackingEvent.trim(),
    );
    // Override traffic split based on slider
    test.trafficSplit = [split[0], 100 - split[0]];

    onCreate(test);
    setName("");
    setTrackingEvent("");
    setVariantA("Control");
    setVariantB("Treatment");
    setSplit([50]);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-sm">Create A/B Test</DialogTitle>
        </DialogHeader>
        <div className="space-y-3">
          <div>
            <label className="text-[11px] text-[var(--mauve-11)] mb-1 block">
              Test Name
            </label>
            <Input
              placeholder="e.g. Checkout Button Color"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="h-8 text-xs"
            />
          </div>
          <div>
            <label className="text-[11px] text-[var(--mauve-11)] mb-1 block">
              Feature Flag
            </label>
            <Select value={flagKey} onValueChange={setFlagKey}>
              <SelectTrigger className="h-8 text-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {flags.map((f) => (
                  <SelectItem key={f.key} value={f.key}>
                    {f.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="text-[11px] text-[var(--mauve-11)] mb-1 block">
              Tracking Event
            </label>
            <Input
              placeholder="e.g. checkout_completed"
              value={trackingEvent}
              onChange={(e) => setTrackingEvent(e.target.value)}
              className="h-8 text-xs font-mono"
            />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="text-[11px] text-[var(--mauve-11)] mb-1 block">
                Variant A
              </label>
              <Input
                value={variantA}
                onChange={(e) => setVariantA(e.target.value)}
                className="h-8 text-xs"
              />
            </div>
            <div>
              <label className="text-[11px] text-[var(--mauve-11)] mb-1 block">
                Variant B
              </label>
              <Input
                value={variantB}
                onChange={(e) => setVariantB(e.target.value)}
                className="h-8 text-xs"
              />
            </div>
          </div>
          <div>
            <label className="text-[11px] text-[var(--mauve-11)] mb-1 block">
              Traffic Split: {split[0]}% / {100 - split[0]}%
            </label>
            <Slider
              value={split}
              onValueChange={setSplit}
              min={10}
              max={90}
              step={5}
            />
          </div>
        </div>
        <DialogFooter>
          <Button
            size="sm"
            variant="outline"
            onClick={() => onOpenChange(false)}
            className="text-xs"
          >
            Cancel
          </Button>
          <Button
            size="sm"
            onClick={handleCreate}
            disabled={!name.trim() || !flagKey || !trackingEvent.trim()}
            className="text-xs"
          >
            Create
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
