// ─── Production Infrastructure — Types ─────────────────────────────────────────
// Environment management, feature flags, A/B testing, and deployment targets.
// ──────────────────────────────────────────────────────────────────────────────

/** An environment configuration (dev/staging/prod) */
export interface Environment {
  /** Unique identifier */
  id: string;
  /** Display name */
  name: string;
  /** Environment type */
  type: "development" | "staging" | "production" | "custom";
  /** Environment-scoped variables */
  variables: Record<string, EnvironmentVariable>;
  /** Whether this is the currently active environment */
  isActive: boolean;
  /** Associated deployment URL */
  url?: string;
  /** Color for UI badge */
  color: string;
}

export interface EnvironmentVariable {
  /** Variable name */
  key: string;
  /** Value (may be redacted for secrets) */
  value: string;
  /** Whether this is a secret (should be masked in UI) */
  isSecret: boolean;
  /** Description */
  description?: string;
}

/** A feature flag definition */
export interface FeatureFlag {
  /** Unique key */
  key: string;
  /** Display name */
  name: string;
  /** Description */
  description?: string;
  /** Flag type */
  type: "boolean" | "string" | "number" | "json";
  /** Default value */
  defaultValue: unknown;
  /** Per-environment overrides */
  environmentOverrides: Record<string, unknown>;
  /** Whether this flag is enabled */
  enabled: boolean;
  /** Tags for organization */
  tags?: string[];
  /** Creation timestamp */
  createdAt: string;
  /** Last modified timestamp */
  updatedAt: string;
}

/** An A/B test experiment */
export interface ABTest {
  /** Unique identifier */
  id: string;
  /** Display name */
  name: string;
  /** Description */
  description?: string;
  /** The feature flag this test is linked to */
  flagKey: string;
  /** Test variants */
  variants: ABTestVariant[];
  /** Traffic split (percentages, should sum to 100) */
  trafficSplit: number[];
  /** Analytics event to track */
  trackingEvent: string;
  /** Status */
  status: "draft" | "running" | "paused" | "completed";
  /** Start/end dates */
  startDate?: string;
  endDate?: string;
}

export interface ABTestVariant {
  /** Variant identifier */
  id: string;
  /** Display name */
  name: string;
  /** The value for the feature flag when this variant is active */
  flagValue: unknown;
  /** Description of what this variant shows/does */
  description?: string;
}

/** A deployment target */
export interface DeployTarget {
  /** Unique identifier */
  id: string;
  /** Display name */
  name: string;
  /** Provider */
  provider:
    | "vercel"
    | "netlify"
    | "aws"
    | "azure"
    | "gcp"
    | "railway"
    | "fly-io"
    | "cloudflare"
    | "custom";
  /** Associated environment */
  environmentId: string;
  /** Deployment URL */
  url?: string;
  /** Last deployment status */
  lastDeployStatus?: "success" | "failed" | "in-progress" | "none";
  /** Last deployment timestamp */
  lastDeployAt?: string;
}
