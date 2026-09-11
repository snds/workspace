// ─── Repo Analysis — Auto-detection of tech stack ────────────────────────────
// Reads repository config files and infers a partial TeamContextProfile.
// Currently a stub that reads package.json (via Tauri fs or web File API).

import type {
  TeamContextProfile,
  FrameworkConfig,
  ComponentLibConfig,
  IconLibConfig,
  StylingConfig,
  BackendConfig,
  DatabaseConfig,
  AuthConfig,
  CodePatternsConfig,
  UsageTier,
} from "@/core/context/types";
import { platform } from "@/platform";
import {
  FRAMEWORK_PATTERNS,
  FRAMEWORK_DETECT_ORDER,
  COMPONENT_LIB_PATTERNS,
  ICON_LIB_PATTERNS,
  STYLING_PATTERNS,
  ORM_PATTERNS,
  API_LAYER_PATTERNS,
  SERVER_FRAMEWORK_PATTERNS,
  DATABASE_PATTERNS,
  AUTH_PATTERNS,
  LINTER_PATTERNS,
  FORMATTER_PATTERNS,
  TEST_FRAMEWORK_PATTERNS,
} from "./patterns";

// ─── Public API ──────────────────────────────────────────────────────────────

export interface RepoAnalysisResult {
  /** Partial profile with detected settings. */
  profile: Partial<TeamContextProfile>;
  /** Human-readable summary of what was detected. */
  detectedItems: string[];
  /** Whether any signal was found at all. */
  success: boolean;
}

/**
 * Analyze a local repository path and return a partial TeamContextProfile
 * with detected settings.
 *
 * Currently reads only `package.json`. Future versions will inspect
 * config files like `tailwind.config.*`, `next.config.*`, etc.
 */
export async function analyzeRepo(
  localPath: string,
): Promise<RepoAnalysisResult> {
  const detectedItems: string[] = [];
  const profile: Partial<TeamContextProfile> = {};

  try {
    // Attempt to read package.json
    const pkgJsonPath = localPath.replace(/\/$/, "") + "/package.json";
    const pkgJsonContent = await readFileFromPath(pkgJsonPath);

    if (!pkgJsonContent) {
      return { profile, detectedItems: ["No package.json found"], success: false };
    }

    const pkg = JSON.parse(pkgJsonContent) as PackageJson;
    const allDeps = {
      ...pkg.dependencies,
      ...pkg.devDependencies,
    };
    const depNames = Object.keys(allDeps);

    // Detect framework
    const framework = detectFramework(depNames);
    if (framework) {
      profile.framework = framework;
      const label = framework.metaFramework !== "none"
        ? `${framework.id} + ${framework.metaFramework}`
        : framework.id;
      detectedItems.push(`Framework: ${label}`);
    }

    // Detect component library
    const compLib = detectFromPatterns(depNames, COMPONENT_LIB_PATTERNS);
    if (compLib) {
      profile.componentLibrary = { id: compLib } as ComponentLibConfig;
      detectedItems.push(`Component library: ${compLib}`);
    }

    // Detect icon library
    const iconLib = detectFromPatterns(depNames, ICON_LIB_PATTERNS);
    if (iconLib) {
      profile.iconLibrary = { id: iconLib } as IconLibConfig;
      detectedItems.push(`Icon library: ${iconLib}`);
    }

    // Detect styling
    const styling = detectFromPatterns(depNames, STYLING_PATTERNS);
    if (styling) {
      profile.styling = { approach: styling } as StylingConfig;
      detectedItems.push(`Styling: ${styling}`);
    }

    // Detect ORM
    const orm = detectFromPatterns(depNames, ORM_PATTERNS);
    // Detect API layer
    const apiLayer = detectFromPatterns(depNames, API_LAYER_PATTERNS);
    // Detect server framework
    const serverFw = detectFromPatterns(depNames, SERVER_FRAMEWORK_PATTERNS);

    if (orm || apiLayer || serverFw) {
      const backend: Partial<BackendConfig> = {};
      if (orm) {
        backend.orm = orm as BackendConfig["orm"];
        detectedItems.push(`ORM: ${orm}`);
      }
      if (apiLayer) {
        backend.apiLayer = apiLayer as BackendConfig["apiLayer"];
        detectedItems.push(`API layer: ${apiLayer}`);
      }
      if (serverFw) {
        backend.serverFramework = serverFw as BackendConfig["serverFramework"];
        detectedItems.push(`Server: ${serverFw}`);
      }
      profile.backend = {
        apiLayer: (apiLayer as BackendConfig["apiLayer"]) ?? "rest",
        ...backend,
      } as BackendConfig;
    }

    // Detect database
    const db = detectFromPatterns(depNames, DATABASE_PATTERNS);
    if (db) {
      profile.database = { type: db } as DatabaseConfig;
      detectedItems.push(`Database: ${db}`);
    }

    // Detect auth
    const auth = detectFromPatterns(depNames, AUTH_PATTERNS);
    if (auth) {
      profile.auth = {
        provider: auth,
        flows: ["login", "signup"],
      } as AuthConfig;
      detectedItems.push(`Auth: ${auth}`);
    }

    // Detect code patterns (linter, formatter, test framework)
    const linter = detectFromPatterns(depNames, LINTER_PATTERNS);
    const formatter = detectFromPatterns(depNames, FORMATTER_PATTERNS);
    const testFw = detectFromPatterns(depNames, TEST_FRAMEWORK_PATTERNS);

    if (linter || formatter || testFw) {
      const patterns: Partial<CodePatternsConfig> = {};
      if (linter) {
        patterns.linter = linter as CodePatternsConfig["linter"];
        detectedItems.push(`Linter: ${linter}`);
      }
      if (formatter) {
        patterns.formatter = formatter as CodePatternsConfig["formatter"];
        detectedItems.push(`Formatter: ${formatter}`);
      }
      if (testFw) {
        patterns.testFramework = testFw as CodePatternsConfig["testFramework"];
        detectedItems.push(`Tests: ${testFw}`);
      }
      profile.codePatterns = {
        naming: "camelCase",
        fileNaming: "kebab-case",
        componentFilePattern: "single-file",
        ...patterns,
      } as CodePatternsConfig;
    }

    // Check if typescript is used
    if (depNames.includes("typescript")) {
      detectedItems.push("TypeScript: yes");
    }

    // Infer tier from what was detected
    const hasFrontend = !!framework || !!compLib || !!styling;
    const hasBackend = !!orm || !!apiLayer || !!serverFw || !!db || !!auth;

    if (hasBackend) {
      profile.tier = 2 as UsageTier;
    } else if (hasFrontend) {
      profile.tier = 1 as UsageTier;
    } else {
      profile.tier = 0 as UsageTier;
    }

    return {
      profile,
      detectedItems,
      success: detectedItems.length > 0,
    };
  } catch (err) {
    console.warn("[repoAnalyzer] Failed to analyze repo:", err);
    return {
      profile,
      detectedItems: ["Analysis failed — could not read repository files"],
      success: false,
    };
  }
}

// ─── Internals ───────────────────────────────────────────────────────────────

interface PackageJson {
  name?: string;
  dependencies?: Record<string, string>;
  devDependencies?: Record<string, string>;
  scripts?: Record<string, string>;
}

/**
 * Reads a file from disk. Uses the Tauri file system if available,
 * otherwise returns null (web fallback can't access arbitrary paths).
 */
async function readFileFromPath(path: string): Promise<string | null> {
  try {
    // Use platform abstraction — if Tauri, reads from filesystem.
    // If web, this will likely fail gracefully.
    const content = await platform.fs.readTextFile(path);
    return content;
  } catch {
    return null;
  }
}

/**
 * Detect the frontend framework from dependency list.
 * Uses FRAMEWORK_DETECT_ORDER for priority (e.g. "next" before "react").
 */
function detectFramework(
  deps: string[],
): FrameworkConfig | null {
  for (const depName of FRAMEWORK_DETECT_ORDER) {
    if (deps.includes(depName)) {
      return FRAMEWORK_PATTERNS[depName];
    }
  }
  return null;
}

/**
 * Generic first-match detector against a pattern map.
 */
function detectFromPatterns<V>(
  deps: string[],
  patterns: Record<string, V>,
): V | null {
  for (const dep of deps) {
    if (dep in patterns) {
      return patterns[dep];
    }
  }
  return null;
}
