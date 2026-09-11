// ─── DataPanel ───────────────────────────────────────────────────────────────
// UI panel for managing data sources, queries, and component bindings.
// Visible when the team context tier >= 2 (Design + Full-Stack).
// ──────────────────────────────────────────────────────────────────────────────

import { useState, useMemo, useCallback } from "react";
import { OmniIcon } from "@/core/icons";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { cn } from "@/lib/utils";
import { useDataStore } from "@/stores/data.store";
import { useTeamContextStore } from "@/stores/teamContext.store";
import { generateMockData } from "@/core/data/mock";
import type {
  DataSource,
  DataSourceType,
  DataEndpoint,
  DataField,
} from "@/core/data/types";

// ─── Types ───────────────────────────────────────────────────────────────────

type PanelView = "sources" | "add-source";

// ─── Status indicator ────────────────────────────────────────────────────────

const STATUS_COLORS: Record<DataSource["status"], string> = {
  disconnected: "bg-neutral-500",
  connecting: "bg-yellow-500 animate-pulse",
  connected: "bg-emerald-500",
  error: "bg-red-500",
};

const STATUS_LABELS: Record<DataSource["status"], string> = {
  disconnected: "Disconnected",
  connecting: "Connecting...",
  connected: "Connected",
  error: "Error",
};

function StatusDot({ status }: { status: DataSource["status"] }) {
  return (
    <span
      className={cn("inline-block size-2 rounded-full", STATUS_COLORS[status])}
      title={STATUS_LABELS[status]}
    />
  );
}

// ─── Source type icons (semantic OmniIcon names) ─────────────────────────────

function SourceTypeIcon({
  type,
  className,
}: {
  type: DataSourceType;
  className?: string;
}) {
  const iconMap: Record<DataSourceType, string> = {
    "rest-api": "action/api",
    graphql: "action/api",
    database: "data/database",
    websocket: "status/signal",
    storage: "file/folder",
    mock: "action/play",
  };

  return (
    <OmniIcon
      name={iconMap[type] ?? "action/api"}
      size={16}
      className={className}
    />
  );
}

// ─── Field tree ──────────────────────────────────────────────────────────────

function FieldTree({
  fields,
  depth = 0,
}: {
  fields: DataField[];
  depth?: number;
}) {
  return (
    <div className="space-y-0.5">
      {fields.map((field) => (
        <FieldNode key={field.name} field={field} depth={depth} />
      ))}
    </div>
  );
}

function FieldNode({
  field,
  depth,
}: {
  field: DataField;
  depth: number;
}) {
  const [expanded, setExpanded] = useState(depth < 1);
  const hasChildren = field.children && field.children.length > 0;

  return (
    <div>
      <button
        type="button"
        onClick={() => hasChildren && setExpanded(!expanded)}
        className={cn(
          "flex w-full items-center gap-1.5 rounded px-1.5 py-0.5 text-xs",
          "text-[var(--mauve-11)] hover:bg-[var(--mauve-3)]",
          hasChildren && "cursor-pointer",
          !hasChildren && "cursor-default",
        )}
        style={{ paddingLeft: `${depth * 12 + 6}px` }}
      >
        {hasChildren && (
          <OmniIcon
            name={
              expanded
                ? "navigation/chevron-down"
                : "navigation/chevron-right"
            }
            size={12}
            className="shrink-0 text-[var(--mauve-9)]"
          />
        )}
        {!hasChildren && <span className="size-3 shrink-0" />}
        <span className="truncate font-mono">{field.name}</span>
        <Badge
          variant="outline"
          className="ml-auto shrink-0 px-1 py-0 text-[10px] leading-4 text-[var(--mauve-9)] border-[var(--mauve-6)]"
        >
          {field.type}
        </Badge>
      </button>
      {hasChildren && expanded && (
        <FieldTree fields={field.children!} depth={depth + 1} />
      )}
    </div>
  );
}

// ─── Endpoint section ────────────────────────────────────────────────────────

function EndpointSection({ endpoint }: { endpoint: DataEndpoint }) {
  const [open, setOpen] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  const mockData = useMemo(() => {
    if (!showPreview) return null;
    return generateMockData(endpoint, 3);
  }, [showPreview, endpoint]);

  return (
    <Collapsible open={open} onOpenChange={setOpen}>
      <CollapsibleTrigger asChild>
        <button
          type="button"
          className={cn(
            "flex w-full items-center gap-2 rounded px-2 py-1.5 text-xs",
            "text-[var(--mauve-12)] hover:bg-[var(--mauve-3)]",
          )}
        >
          <OmniIcon
            name={
              open
                ? "navigation/chevron-down"
                : "navigation/chevron-right"
            }
            size={12}
            className="shrink-0 text-[var(--mauve-9)]"
          />
          {endpoint.method && (
            <Badge
              variant="outline"
              className={cn(
                "shrink-0 px-1 py-0 text-[10px] font-mono leading-4 border-[var(--mauve-6)]",
                endpoint.method === "GET" && "text-emerald-400",
                endpoint.method === "POST" && "text-blue-400",
                endpoint.method === "PUT" && "text-amber-400",
                endpoint.method === "PATCH" && "text-orange-400",
                endpoint.method === "DELETE" && "text-red-400",
              )}
            >
              {endpoint.method}
            </Badge>
          )}
          <span className="truncate font-mono text-[var(--mauve-11)]">
            {endpoint.path}
          </span>
        </button>
      </CollapsibleTrigger>
      <CollapsibleContent>
        <div className="ml-4 border-l border-[var(--mauve-4)] pl-2">
          {endpoint.description && (
            <p className="px-2 py-1 text-[11px] text-[var(--mauve-9)]">
              {endpoint.description}
            </p>
          )}

          {/* Fields */}
          {endpoint.fields.length > 0 && (
            <div className="mt-1">
              <div className="px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-[var(--mauve-8)]">
                Fields
              </div>
              <FieldTree fields={endpoint.fields} />
            </div>
          )}

          {/* Params */}
          {endpoint.params && endpoint.params.length > 0 && (
            <div className="mt-1">
              <div className="px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-[var(--mauve-8)]">
                Parameters
              </div>
              <FieldTree fields={endpoint.params} />
            </div>
          )}

          {/* Mock preview toggle */}
          <div className="mt-1.5 px-2 pb-1.5">
            <Button
              variant="ghost"
              size="xs"
              onClick={(e) => {
                e.stopPropagation();
                setShowPreview(!showPreview);
              }}
              className="text-[10px] text-[var(--mauve-9)] hover:text-[var(--mauve-11)]"
            >
              <OmniIcon
                name={showPreview ? "navigation/chevron-up" : "action/play"}
                size={12}
              />
              {showPreview ? "Hide preview" : "Preview mock data"}
            </Button>
            {showPreview && mockData != null && (
              <pre className="mt-1.5 max-h-40 overflow-auto rounded bg-[var(--mauve-2)] p-2 font-mono text-[10px] leading-relaxed text-[var(--mauve-11)]">
                {JSON.stringify(mockData, null, 2)}
              </pre>
            )}
          </div>
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}

// ─── Source card ──────────────────────────────────────────────────────────────

function SourceCard({ source }: { source: DataSource }) {
  const [expanded, setExpanded] = useState(false);
  const removeSource = useDataStore((s) => s.removeSource);

  return (
    <Collapsible open={expanded} onOpenChange={setExpanded}>
      <div className="rounded-md border border-[var(--mauve-4)] bg-[var(--mauve-2)]">
        <CollapsibleTrigger asChild>
          <button
            type="button"
            className="flex w-full items-center gap-2.5 px-3 py-2 text-left"
          >
            <OmniIcon
              name={
                expanded
                  ? "navigation/chevron-down"
                  : "navigation/chevron-right"
              }
              size={14}
              className="shrink-0 text-[var(--mauve-9)]"
            />
            <SourceTypeIcon type={source.type} />
            <div className="min-w-0 flex-1">
              <div className="truncate text-sm font-medium text-[var(--mauve-12)]">
                {source.name}
              </div>
              <div className="truncate text-[11px] text-[var(--mauve-9)]">
                {source.config.baseUrl ?? source.type}
              </div>
            </div>
            <StatusDot status={source.status} />
          </button>
        </CollapsibleTrigger>

        <CollapsibleContent>
          <div className="border-t border-[var(--mauve-4)] px-3 py-2">
            {/* Connection info */}
            <div className="mb-2 space-y-1 text-[11px]">
              <div className="flex justify-between">
                <span className="text-[var(--mauve-9)]">Type</span>
                <span className="font-mono text-[var(--mauve-11)]">
                  {source.type}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--mauve-9)]">Auth</span>
                <span className="font-mono text-[var(--mauve-11)]">
                  {source.config.authMethod ?? "none"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-[var(--mauve-9)]">Status</span>
                <span className="flex items-center gap-1.5">
                  <StatusDot status={source.status} />
                  <span className="text-[var(--mauve-11)]">
                    {STATUS_LABELS[source.status]}
                  </span>
                </span>
              </div>
              {source.error && (
                <div className="mt-1 rounded bg-red-500/10 px-2 py-1 text-[10px] text-red-400">
                  {source.error}
                </div>
              )}
            </div>

            {/* Endpoints / schema */}
            {source.schema && source.schema.endpoints.length > 0 && (
              <div className="mt-2">
                <div className="mb-1 text-[10px] font-medium uppercase tracking-wider text-[var(--mauve-8)]">
                  Endpoints ({source.schema.endpoints.length})
                </div>
                <div className="space-y-0.5">
                  {source.schema.endpoints.map((ep) => (
                    <EndpointSection
                      key={`${ep.method ?? "GET"}-${ep.path}`}
                      endpoint={ep}
                    />
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="mt-3 flex gap-2">
              <Button
                variant="outline"
                size="xs"
                className="flex-1 text-[11px] border-[var(--mauve-6)] text-[var(--mauve-11)] hover:bg-[var(--mauve-4)]"
                onClick={(e) => {
                  e.stopPropagation();
                  // TODO: Test connection logic
                }}
              >
                Test connection
              </Button>
              <Button
                variant="ghost"
                size="xs"
                className="text-[11px] text-red-400 hover:bg-red-500/10 hover:text-red-400"
                onClick={(e) => {
                  e.stopPropagation();
                  removeSource(source.id);
                }}
              >
                Remove
              </Button>
            </div>
          </div>
        </CollapsibleContent>
      </div>
    </Collapsible>
  );
}

// ─── Add Source form ──────────────────────────────────────────────────────────

const SOURCE_TYPE_OPTIONS: Array<{
  value: DataSourceType;
  label: string;
}> = [
  { value: "rest-api", label: "REST API" },
  { value: "graphql", label: "GraphQL" },
  { value: "database", label: "Database" },
  { value: "websocket", label: "WebSocket" },
  { value: "storage", label: "Storage" },
  { value: "mock", label: "Mock" },
];

function AddSourceForm({ onDone }: { onDone: () => void }) {
  const addSource = useDataStore((s) => s.addSource);

  const [name, setName] = useState("");
  const [type, setType] = useState<DataSourceType>("rest-api");
  const [url, setUrl] = useState("");

  const handleSubmit = useCallback(() => {
    if (!name.trim()) return;

    const id = `ds-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    const source: DataSource = {
      id,
      name: name.trim(),
      type,
      config: {
        baseUrl: url.trim() || undefined,
        authMethod: "none",
      },
      status: "disconnected",
    };

    addSource(source);
    onDone();
  }, [name, type, url, addSource, onDone]);

  return (
    <div className="space-y-3 px-3 py-3">
      <div className="text-xs font-medium text-[var(--mauve-12)]">
        Add Data Source
      </div>

      {/* Name */}
      <div className="space-y-1">
        <label className="text-[11px] text-[var(--mauve-9)]">Name</label>
        <Input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="My API"
          className="h-7 text-xs bg-[var(--mauve-2)] border-[var(--mauve-5)]"
        />
      </div>

      {/* Type */}
      <div className="space-y-1">
        <label className="text-[11px] text-[var(--mauve-9)]">Type</label>
        <Select value={type} onValueChange={(v) => setType(v as DataSourceType)}>
          <SelectTrigger className="h-7 text-xs bg-[var(--mauve-2)] border-[var(--mauve-5)]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {SOURCE_TYPE_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>
                {opt.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* URL */}
      <div className="space-y-1">
        <label className="text-[11px] text-[var(--mauve-9)]">
          Base URL
        </label>
        <Input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://api.example.com"
          className="h-7 text-xs bg-[var(--mauve-2)] border-[var(--mauve-5)]"
        />
      </div>

      {/* Actions */}
      <div className="flex gap-2 pt-1">
        <Button
          size="xs"
          onClick={handleSubmit}
          disabled={!name.trim()}
          className="flex-1 text-[11px]"
        >
          Add source
        </Button>
        <Button
          variant="ghost"
          size="xs"
          onClick={onDone}
          className="text-[11px] text-[var(--mauve-9)]"
        >
          Cancel
        </Button>
      </div>
    </div>
  );
}

// ─── Main panel ──────────────────────────────────────────────────────────────

export function DataPanel() {
  const [view, setView] = useState<PanelView>("sources");
  const isTierActive = useTeamContextStore((s) => s.isTierActive);

  // Force re-read when store mutates (keyed on revision)
  const _revision = useDataStore((s) => s._revision);
  const getAllSources = useDataStore((s) => s.getAllSources);
  const sources = useMemo(() => getAllSources(), [getAllSources, _revision]);

  // Gate: tier 2+ only
  if (!isTierActive(2)) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-3 p-6 text-center">
        <OmniIcon
          name="data/database"
          size={32}
          className="text-[var(--mauve-7)]"
        />
        <div className="space-y-1">
          <p className="text-sm font-medium text-[var(--mauve-11)]">
            Data sources
          </p>
          <p className="text-xs text-[var(--mauve-9)]">
            Upgrade to Tier 2 (Full-Stack) to connect APIs, databases, and
            other data sources.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-[var(--mauve-4)] px-3 py-2">
        <span className="text-xs font-medium text-[var(--mauve-12)]">
          Data Sources
        </span>
        {view === "sources" && (
          <Button
            variant="ghost"
            size="icon-xs"
            onClick={() => setView("add-source")}
            title="Add data source"
            className="text-[var(--mauve-9)] hover:text-[var(--mauve-11)]"
          >
            <OmniIcon name="action/add" size={14} />
          </Button>
        )}
      </div>

      {/* Content */}
      <ScrollArea className="flex-1">
        {view === "add-source" ? (
          <AddSourceForm onDone={() => setView("sources")} />
        ) : sources.length === 0 ? (
          <div className="flex flex-col items-center gap-3 p-6 text-center">
            <OmniIcon
              name="data/database"
              size={28}
              className="text-[var(--mauve-6)]"
            />
            <div className="space-y-1">
              <p className="text-xs text-[var(--mauve-9)]">
                No data sources connected yet.
              </p>
              <Button
                variant="outline"
                size="xs"
                onClick={() => setView("add-source")}
                className="mt-2 text-[11px] border-[var(--mauve-6)] text-[var(--mauve-11)]"
              >
                <OmniIcon name="action/add" size={12} />
                Add data source
              </Button>
            </div>
          </div>
        ) : (
          <div className="space-y-2 p-2">
            {sources.map((source) => (
              <SourceCard key={source.id} source={source} />
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
