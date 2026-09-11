import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { useTeamContextStore } from "@/stores/teamContext.store";
import type {
  UsageTier,
  FrameworkConfig,
  ComponentLibConfig,
  IconLibConfig,
  StylingConfig,
  BackendConfig,
  DatabaseConfig,
  AuthConfig,
  CodePatternsConfig,
  InfraConfig,
  I18nConfig,
} from "@/core/context/types";

// ─── Tier Descriptions ───────────────────────────────────────────────────────

const TIER_OPTIONS: { value: UsageTier; label: string; description: string }[] =
  [
    {
      value: 0,
      label: "Design Only",
      description: "Colors, tokens, and visual design tools only.",
    },
    {
      value: 1,
      label: "Design + Frontend",
      description: "Framework, components, styling, and code patterns.",
    },
    {
      value: 2,
      label: "Design + Full-Stack",
      description: "Adds backend, database, and authentication config.",
    },
    {
      value: 3,
      label: "Design + Full-Stack + Prod",
      description: "Adds hosting, CI/CD, monitoring, and i18n.",
    },
  ];

// ─── Select Option Lists ────────────────────────────────────────────────────

const FRAMEWORK_OPTIONS: { value: FrameworkConfig["id"]; label: string }[] = [
  { value: "react", label: "React" },
  { value: "vue", label: "Vue" },
  { value: "svelte", label: "Svelte" },
  { value: "angular", label: "Angular" },
  { value: "react-native", label: "React Native" },
  { value: "solid", label: "Solid" },
  { value: "qwik", label: "Qwik" },
];

const META_FRAMEWORK_OPTIONS: {
  value: NonNullable<FrameworkConfig["metaFramework"]>;
  label: string;
}[] = [
  { value: "none", label: "None" },
  { value: "nextjs", label: "Next.js" },
  { value: "remix", label: "Remix" },
  { value: "nuxt", label: "Nuxt" },
  { value: "sveltekit", label: "SvelteKit" },
  { value: "astro", label: "Astro" },
];

const COMPONENT_LIB_OPTIONS: {
  value: ComponentLibConfig["id"];
  label: string;
}[] = [
  { value: "shadcn", label: "shadcn/ui" },
  { value: "mui", label: "MUI" },
  { value: "chakra", label: "Chakra UI" },
  { value: "ant-design", label: "Ant Design" },
  { value: "radix", label: "Radix Primitives" },
  { value: "headless-ui", label: "Headless UI" },
  { value: "vuetify", label: "Vuetify" },
  { value: "custom", label: "Custom" },
  { value: "none", label: "None" },
];

const ICON_LIB_OPTIONS: { value: IconLibConfig["id"]; label: string }[] = [
  { value: "lucide", label: "Lucide" },
  { value: "phosphor", label: "Phosphor" },
  { value: "heroicons", label: "Heroicons" },
  { value: "material-icons", label: "Material Icons" },
  { value: "tabler", label: "Tabler" },
  { value: "feather", label: "Feather" },
  { value: "carbon", label: "Carbon" },
  { value: "iconify", label: "Iconify" },
  { value: "custom", label: "Custom" },
];

const STYLING_OPTIONS: { value: StylingConfig["approach"]; label: string }[] = [
  { value: "tailwind", label: "Tailwind CSS" },
  { value: "css-modules", label: "CSS Modules" },
  { value: "styled-components", label: "styled-components" },
  { value: "emotion", label: "Emotion" },
  { value: "vanilla-extract", label: "Vanilla Extract" },
  { value: "scss", label: "SCSS" },
  { value: "css-in-js", label: "CSS-in-JS (other)" },
  { value: "uno-css", label: "UnoCSS" },
];

const NAMING_OPTIONS: { value: CodePatternsConfig["naming"]; label: string }[] =
  [
    { value: "camelCase", label: "camelCase" },
    { value: "PascalCase", label: "PascalCase" },
    { value: "kebab-case", label: "kebab-case" },
    { value: "snake_case", label: "snake_case" },
  ];

const FILE_NAMING_OPTIONS: {
  value: CodePatternsConfig["fileNaming"];
  label: string;
}[] = [
  { value: "camelCase", label: "camelCase" },
  { value: "PascalCase", label: "PascalCase" },
  { value: "kebab-case", label: "kebab-case" },
];

const COMPONENT_FILE_OPTIONS: {
  value: CodePatternsConfig["componentFilePattern"];
  label: string;
}[] = [
  { value: "single-file", label: "Single file" },
  { value: "folder-with-index", label: "Folder + index" },
  { value: "folder-with-named", label: "Folder + named file" },
];

const LINTER_OPTIONS: {
  value: NonNullable<CodePatternsConfig["linter"]>;
  label: string;
}[] = [
  { value: "eslint", label: "ESLint" },
  { value: "biome", label: "Biome" },
  { value: "oxlint", label: "oxlint" },
  { value: "none", label: "None" },
];

const FORMATTER_OPTIONS: {
  value: NonNullable<CodePatternsConfig["formatter"]>;
  label: string;
}[] = [
  { value: "prettier", label: "Prettier" },
  { value: "biome", label: "Biome" },
  { value: "dprint", label: "dprint" },
  { value: "none", label: "None" },
];

// ── Tier 2 Options ───────────────────────────────────────────────────────────

const API_LAYER_OPTIONS: {
  value: BackendConfig["apiLayer"];
  label: string;
}[] = [
  { value: "rest", label: "REST" },
  { value: "graphql", label: "GraphQL" },
  { value: "trpc", label: "tRPC" },
  { value: "grpc", label: "gRPC" },
  { value: "none", label: "None" },
];

const ORM_OPTIONS: {
  value: NonNullable<BackendConfig["orm"]>;
  label: string;
}[] = [
  { value: "prisma", label: "Prisma" },
  { value: "drizzle", label: "Drizzle" },
  { value: "typeorm", label: "TypeORM" },
  { value: "sqlalchemy", label: "SQLAlchemy" },
  { value: "sequelize", label: "Sequelize" },
  { value: "none", label: "None" },
];

const DATABASE_OPTIONS: { value: DatabaseConfig["type"]; label: string }[] = [
  { value: "postgres", label: "PostgreSQL" },
  { value: "mysql", label: "MySQL" },
  { value: "sqlite", label: "SQLite" },
  { value: "mongodb", label: "MongoDB" },
  { value: "supabase", label: "Supabase" },
  { value: "firebase", label: "Firebase" },
  { value: "dynamodb", label: "DynamoDB" },
  { value: "none", label: "None" },
];

const AUTH_PROVIDER_OPTIONS: {
  value: AuthConfig["provider"];
  label: string;
}[] = [
  { value: "clerk", label: "Clerk" },
  { value: "auth0", label: "Auth0" },
  { value: "supabase", label: "Supabase Auth" },
  { value: "firebase", label: "Firebase Auth" },
  { value: "nextauth", label: "NextAuth.js" },
  { value: "lucia", label: "Lucia" },
  { value: "custom", label: "Custom" },
  { value: "none", label: "None" },
];

// ── Tier 3 Options ───────────────────────────────────────────────────────────

const HOSTING_OPTIONS: { value: InfraConfig["hosting"]; label: string }[] = [
  { value: "vercel", label: "Vercel" },
  { value: "netlify", label: "Netlify" },
  { value: "aws", label: "AWS" },
  { value: "azure", label: "Azure" },
  { value: "gcp", label: "GCP" },
  { value: "railway", label: "Railway" },
  { value: "fly-io", label: "Fly.io" },
  { value: "cloudflare", label: "Cloudflare" },
  { value: "self-hosted", label: "Self-hosted" },
];

const I18N_STRATEGY_OPTIONS: {
  value: I18nConfig["strategy"];
  label: string;
}[] = [
  { value: "key-based", label: "Key-based" },
  { value: "default-language", label: "Default language" },
  { value: "icu-messages", label: "ICU Messages" },
];

// ─── Helper: Section Header ──────────────────────────────────────────────────

function SectionHeader({
  title,
  description,
}: {
  title: string;
  description?: string;
}) {
  return (
    <div className="mb-3">
      <h4 className="text-xs font-semibold text-[var(--mauve-11)] uppercase tracking-wider">
        {title}
      </h4>
      {description && (
        <p className="text-[10px] text-[var(--mauve-9)] mt-0.5">
          {description}
        </p>
      )}
    </div>
  );
}

// ─── Helper: Field Row ───────────────────────────────────────────────────────

function FieldRow({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex items-center justify-between gap-3 py-1.5">
      <label className="text-[11px] text-[var(--mauve-11)] flex-shrink-0">
        {label}
      </label>
      <div className="w-44">{children}</div>
    </div>
  );
}

// ─── Helper: Themed Select ───────────────────────────────────────────────────

function ThemedSelect<T extends string>({
  value,
  onValueChange,
  options,
  placeholder,
}: {
  value: T;
  onValueChange: (val: T) => void;
  options: { value: T; label: string }[];
  placeholder?: string;
}) {
  return (
    <Select value={value} onValueChange={(v) => onValueChange(v as T)}>
      <SelectTrigger
        className={cn(
          "h-7 text-[11px] bg-[var(--mauve-3)] border-[var(--mauve-5)]",
          "text-[var(--mauve-12)] focus:border-[var(--violet-7)]",
        )}
      >
        <SelectValue placeholder={placeholder ?? "Select..."} />
      </SelectTrigger>
      <SelectContent className="bg-[var(--mauve-2)] border-[var(--mauve-5)]">
        {options.map((opt) => (
          <SelectItem
            key={opt.value}
            value={opt.value}
            className="text-[11px] text-[var(--mauve-12)] focus:bg-[var(--mauve-4)]"
          >
            {opt.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}

// ─── Main Component ──────────────────────────────────────────────────────────

export function ContextDimensionEditor() {
  const { profile, updateProfile, setTier } = useTeamContextStore();
  const tier = profile.tier;

  return (
    <ScrollArea className="h-[340px]">
      <div className="space-y-5 pr-3">
        {/* ── Usage Tier selector ────────────────────────────────────────── */}
        <div>
          <SectionHeader
            title="Usage Tier"
            description="How much of your stack should Omni understand?"
          />
          <RadioGroup
            value={String(tier)}
            onValueChange={(v) => setTier(Number(v) as UsageTier)}
            className="grid grid-cols-2 gap-2"
          >
            {TIER_OPTIONS.map((opt) => (
              <label
                key={opt.value}
                className={cn(
                  "flex items-start gap-2 p-2.5 rounded-lg border cursor-pointer transition-all",
                  tier === opt.value
                    ? "border-[var(--violet-7)] bg-[var(--violet-3)]"
                    : "border-[var(--mauve-5)] bg-[var(--mauve-3)] hover:border-[var(--mauve-6)]",
                )}
              >
                <RadioGroupItem
                  value={String(opt.value)}
                  className="mt-0.5 flex-shrink-0"
                />
                <div>
                  <p
                    className={cn(
                      "text-[11px] font-semibold",
                      tier === opt.value
                        ? "text-[var(--violet-12)]"
                        : "text-[var(--mauve-12)]",
                    )}
                  >
                    {opt.label}
                  </p>
                  <p
                    className={cn(
                      "text-[9px] mt-0.5",
                      tier === opt.value
                        ? "text-[var(--violet-11)]"
                        : "text-[var(--mauve-9)]",
                    )}
                  >
                    {opt.description}
                  </p>
                </div>
              </label>
            ))}
          </RadioGroup>
        </div>

        {/* ── Tier 1+: Frontend Config ────────────────────────────────── */}
        {tier >= 1 && (
          <div className="space-y-4">
            {/* Framework */}
            <div>
              <SectionHeader title="Framework" />
              <div className="space-y-1">
                <FieldRow label="Framework">
                  <ThemedSelect
                    value={profile.framework.id}
                    onValueChange={(v) =>
                      updateProfile({
                        framework: {
                          ...profile.framework,
                          id: v as FrameworkConfig["id"],
                        },
                      })
                    }
                    options={FRAMEWORK_OPTIONS}
                  />
                </FieldRow>
                <FieldRow label="Meta-framework">
                  <ThemedSelect
                    value={profile.framework.metaFramework ?? "none"}
                    onValueChange={(v) =>
                      updateProfile({
                        framework: {
                          ...profile.framework,
                          metaFramework:
                            v as NonNullable<FrameworkConfig["metaFramework"]>,
                        },
                      })
                    }
                    options={META_FRAMEWORK_OPTIONS}
                  />
                </FieldRow>
              </div>
            </div>

            {/* Component Library */}
            <div>
              <SectionHeader title="Component Library" />
              <FieldRow label="Library">
                <ThemedSelect
                  value={profile.componentLibrary.id}
                  onValueChange={(v) =>
                    updateProfile({
                      componentLibrary: {
                        ...profile.componentLibrary,
                        id: v as ComponentLibConfig["id"],
                      },
                    })
                  }
                  options={COMPONENT_LIB_OPTIONS}
                />
              </FieldRow>
            </div>

            {/* Icon Library */}
            <div>
              <SectionHeader title="Icon Library" />
              <FieldRow label="Icons">
                <ThemedSelect
                  value={profile.iconLibrary.id}
                  onValueChange={(v) =>
                    updateProfile({
                      iconLibrary: {
                        ...profile.iconLibrary,
                        id: v as IconLibConfig["id"],
                      },
                    })
                  }
                  options={ICON_LIB_OPTIONS}
                />
              </FieldRow>
            </div>

            {/* Styling */}
            <div>
              <SectionHeader title="Styling" />
              <FieldRow label="Approach">
                <ThemedSelect
                  value={profile.styling.approach}
                  onValueChange={(v) =>
                    updateProfile({
                      styling: {
                        ...profile.styling,
                        approach: v as StylingConfig["approach"],
                      },
                    })
                  }
                  options={STYLING_OPTIONS}
                />
              </FieldRow>
            </div>

            {/* Code Patterns */}
            <div>
              <SectionHeader title="Code Patterns" />
              <div className="space-y-1">
                <FieldRow label="Naming">
                  <ThemedSelect
                    value={profile.codePatterns.naming}
                    onValueChange={(v) =>
                      updateProfile({
                        codePatterns: {
                          ...profile.codePatterns,
                          naming: v as CodePatternsConfig["naming"],
                        },
                      })
                    }
                    options={NAMING_OPTIONS}
                  />
                </FieldRow>
                <FieldRow label="File naming">
                  <ThemedSelect
                    value={profile.codePatterns.fileNaming}
                    onValueChange={(v) =>
                      updateProfile({
                        codePatterns: {
                          ...profile.codePatterns,
                          fileNaming: v as CodePatternsConfig["fileNaming"],
                        },
                      })
                    }
                    options={FILE_NAMING_OPTIONS}
                  />
                </FieldRow>
                <FieldRow label="Component files">
                  <ThemedSelect
                    value={profile.codePatterns.componentFilePattern}
                    onValueChange={(v) =>
                      updateProfile({
                        codePatterns: {
                          ...profile.codePatterns,
                          componentFilePattern:
                            v as CodePatternsConfig["componentFilePattern"],
                        },
                      })
                    }
                    options={COMPONENT_FILE_OPTIONS}
                  />
                </FieldRow>
                <FieldRow label="Linter">
                  <ThemedSelect
                    value={profile.codePatterns.linter ?? "none"}
                    onValueChange={(v) =>
                      updateProfile({
                        codePatterns: {
                          ...profile.codePatterns,
                          linter:
                            v as NonNullable<CodePatternsConfig["linter"]>,
                        },
                      })
                    }
                    options={LINTER_OPTIONS}
                  />
                </FieldRow>
                <FieldRow label="Formatter">
                  <ThemedSelect
                    value={profile.codePatterns.formatter ?? "none"}
                    onValueChange={(v) =>
                      updateProfile({
                        codePatterns: {
                          ...profile.codePatterns,
                          formatter:
                            v as NonNullable<CodePatternsConfig["formatter"]>,
                        },
                      })
                    }
                    options={FORMATTER_OPTIONS}
                  />
                </FieldRow>
              </div>
            </div>
          </div>
        )}

        {/* ── Tier 2+: Backend Config ─────────────────────────────────── */}
        {tier >= 2 && (
          <div className="space-y-4">
            <div>
              <SectionHeader title="Backend" />
              <div className="space-y-1">
                <FieldRow label="API layer">
                  <ThemedSelect
                    value={profile.backend.apiLayer}
                    onValueChange={(v) =>
                      updateProfile({
                        backend: {
                          ...profile.backend,
                          apiLayer: v as BackendConfig["apiLayer"],
                        },
                      })
                    }
                    options={API_LAYER_OPTIONS}
                  />
                </FieldRow>
                <FieldRow label="ORM">
                  <ThemedSelect
                    value={profile.backend.orm ?? "none"}
                    onValueChange={(v) =>
                      updateProfile({
                        backend: {
                          ...profile.backend,
                          orm: v as NonNullable<BackendConfig["orm"]>,
                        },
                      })
                    }
                    options={ORM_OPTIONS}
                  />
                </FieldRow>
              </div>
            </div>

            <div>
              <SectionHeader title="Database" />
              <FieldRow label="Type">
                <ThemedSelect
                  value={profile.database.type}
                  onValueChange={(v) =>
                    updateProfile({
                      database: {
                        ...profile.database,
                        type: v as DatabaseConfig["type"],
                      },
                    })
                  }
                  options={DATABASE_OPTIONS}
                />
              </FieldRow>
            </div>

            <div>
              <SectionHeader title="Authentication" />
              <FieldRow label="Provider">
                <ThemedSelect
                  value={profile.auth.provider}
                  onValueChange={(v) =>
                    updateProfile({
                      auth: {
                        ...profile.auth,
                        provider: v as AuthConfig["provider"],
                      },
                    })
                  }
                  options={AUTH_PROVIDER_OPTIONS}
                />
              </FieldRow>
            </div>
          </div>
        )}

        {/* ── Tier 3+: Infrastructure & i18n ──────────────────────────── */}
        {tier >= 3 && (
          <div className="space-y-4">
            <div>
              <SectionHeader title="Infrastructure" />
              <FieldRow label="Hosting">
                <ThemedSelect
                  value={profile.infra.hosting}
                  onValueChange={(v) =>
                    updateProfile({
                      infra: {
                        ...profile.infra,
                        hosting: v as InfraConfig["hosting"],
                      },
                    })
                  }
                  options={HOSTING_OPTIONS}
                />
              </FieldRow>
            </div>

            <div>
              <SectionHeader title="Internationalization" />
              <div className="space-y-1">
                <FieldRow label="Strategy">
                  <ThemedSelect
                    value={profile.i18n.strategy}
                    onValueChange={(v) =>
                      updateProfile({
                        i18n: {
                          ...profile.i18n,
                          strategy: v as I18nConfig["strategy"],
                        },
                      })
                    }
                    options={I18N_STRATEGY_OPTIONS}
                  />
                </FieldRow>
              </div>
            </div>
          </div>
        )}
      </div>
    </ScrollArea>
  );
}
