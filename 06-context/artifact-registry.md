# Artifact Registry
<!-- Auto-maintained by Claude. Updated after each task. -->
<!-- Last updated: 2026-07-09 | Session: Delivery playbooks (Audience & Evidence system) shipped -->

## Delivery Playbooks — 02-shared-references/delivery-playbooks/

### delivery-playbooks/ (7 files: README + 00–05)
- **Size**: ~7 files, ~600 lines total
- **Purpose**: Canonical standards for HOW work is delivered — context profiles (whose work / who reviews: `personal-solo` / `centric-engineering` / `centric-design`, resolution order, fail-safe), audience contract (designer-first, forward test, three-altitude model), medium playbooks (diagrams/flows, data/charts, documents/specs), and the Proofboard validation-harness standard (plain-english contracts, show-me evidence, sandboxed sample data — Sean verifies code-heavy work without reading code).
- **Last modified**: 2026-07-09 — v1 created. Enforcement wired: dispatcher `TRIGGER_WORDS`, CLAUDE.md (section + trigger rows), framework #06 pre-output gate (context & medium check), SESSION-STATE template (`Context profile` field), user-preferences pointer. Founding anti-example: the Media Sentinel workflow-diagram-as-HTML-page failure.
- **Related pending**: "Context is King — workspace foundation refinements" backlog item in project-context.md (generalize profile resolution to every session surface).

### workspace_validation-session-prompt_v1.0_2026-07-09.md — 05-artifacts/active/ (local only, gitignored)
- **Purpose**: 6-phase test prompt validating the delivery-playbooks system in a fresh session — boot/trigger verification, context-resolution drills (incl. a deliberately unresolvable trap), audience/medium binding, a full Proofboard loop, adversarial path-walk (token-waste audit, trigger gaps, unexercised-path desk-check), scorecard. Fixed checkpoint-report format; stops for Sean's confirmation at every phase.
- **Last modified**: 2026-07-09 — v1.0 created. Not synced (05-artifacts gitignored) — copy manually to run from another machine; bump version + re-run after the "Context is King" backlog item lands.

## Skill Ecosystem & Trigger System — 05-artifacts/active/ + 03-skills/

### skill-ecosystem-stocktake_v0.3_2026-06-01.md
- **Size**: ~250 lines | 18 KB
- **Purpose**: Phase 1 — inventory of all non-workspace (plugin/marketplace + default Anthropic) skills, overlap mapping, adopt/wrap/fold-in disposition per the three-way contract.
- **Last modified**: 2026-06-01 — v0.3 MAJOR correction: zero exact-name collisions between added marketplaces and the 210 workspace skills; the 20 same-name overlaps are the default Anthropic mount (left alone). "Dedupe" task dissolved → reframed as ~8–10 semantic-overlap zones. Added Finding 3 (impeccable browser-extension + live-bridge surface, preserved for trigger expansion).

### invokable-operations-spec_v0.2_2026-06-01.md
- **Size**: ~205 lines | (companion spec)
- **Purpose**: Phase 2 — two-plane trigger model (organic description-contract + explicit `/hub verb target --modifiers` grammar), 12-verb spine, six-hub design, migration plan.
- **Last modified**: 2026-06-01 — v0.2: marked /qa POC built; reconciled dedupe references to stocktake v0.3 (no dedupe precondition).

### trigger-cheatsheet_v1.0_2026-06-01.html
- **Size**: ~424 lines | 31 KB
- **Purpose**: Self-contained HTML reference for the trigger system — two planes, verb spine, six hubs (status-tagged), targets/modifiers, 8 real-session worked combos, organic-phrasing map, impeccable modes/bridge, project trigger words, rules of thumb. Print/PDF-clean.
- **Last modified**: 2026-06-01 — v1.0 created.

### 03-skills/qa/SKILL.md
- **Size**: ~191 lines | 10 KB
- **Purpose**: `/qa` POC hub — user-invocable workspace wrapper implementing the operation grammar. Owns UI-evaluation routing; delegates to visual-qa-* spokes + visual-qa-toolkit + lead-visual-qa.
- **Last modified**: 2026-06-01 — v0.1.0 created. Verbs audit·critique·triage·inventory·spec; 8 target types; modifiers --lens/--level/--theme/--live/--out/--dry. Encodes disambiguation contract (qa judges · design-engineer authors · ds-advisor decides · impeccable creates) + preserves impeccable --live bridge with multi-spoke expansion seam.
- **Coverage**: First sibling of the 6-hub set; pattern validates remaining 5 (/ds /figma /motion /type /redesign). Synced to live skills mount.

### 03-skills/{ds,figma,motion,type,redesign}/SKILL.md  — the 5 sibling hubs
- **Size**: ds 141 · figma 124 · redesign 122 · motion 105 · type 99 lines
- **Purpose**: Complete the six-hub operation-grammar set. Each is a user-invocable workspace wrapper carrying the `/hub verb target --modifiers` grammar, a verb subset, and the cross-hub disambiguation contract; depth stays in delegated base skills/plugins.
  - `/ds` → ds-advisor + design-engineer + fe-design-tokens (system decisions, tokens, anatomy, governance)
  - `/figma` → figma-* + figma-canvas-designer + figma-plugin-dev + Figma MCP (canvas authoring, code-connect)
  - `/motion` → claude-design-skillstack libraries (motion *implementation*; principles stay in motion-* skills)
  - `/type` → type-* + lead-type-designer + gd-typography + uid-type-for-screens (type systems & letterform)
  - `/redesign` → adobe stardust pipeline + impeccable live loop (surface-scale generative redesign)
- **Last modified**: 2026-06-04 — observed built on disk; completes the set begun with /qa (2026-06-01).
- **Coverage**: Six-hub set complete. Open: design-system-ops plugin (38 commands) overlaps /ds → fold into description-contract pass; cheatsheet "planned" tags now stale.

## Workspace Infrastructure — 03-skills/ + 00-bootstrap/ + ~/.claude/

### 03-skills/workspace-bootstrap/SKILL.md
- **Size**: ~470 lines | 47 KB
- **Purpose**: Session-start context loader + boot protocol.
- **Last modified**: 2026-06-01 — Added Drive Stream-vs-Mirror path resolution (`resolve_workspace_root()` probing both roots, `[ -s ]` materialization gate to reject online-only placeholders), per-machine sync-mode section, and reference to the machine-local symlink resolver hook.

### 00-bootstrap/setup/resolve-skills-symlink.sh + INSTALL-skills-resolver.md
- **Size**: ~70 lines (script) + install note
- **Purpose**: Machine-local resolver that points `~/.claude/skills` at whichever Drive root is materialized on this machine — lets work Mac run stream+offline while personal/Windows mirror. Wired as a SessionStart hook in `~/.claude/settings.json`.
- **Last modified**: 2026-06-01 — created; canonical copy synced to Drive for other machines.

## Meridian Design System — files/meridian-ds/

### app-shell-prototype-v0.1.jsx
- **Size**: ~7500 lines | 345 KB
- **Purpose**: Full app shell prototype — sidebar nav, topbar, 6 views, search, modals, responsive layout
- **Last modified**: 2026-03-08 — Cross-prototype alignment pass (focus ring, modal focus trap + exit animation)

#### Structure
| Section | Lines | Contents |
|---------|-------|----------|
| Token definitions | 13–103 | tokens (surface, border, text, interactive, status, elevation, overlay, brand3p, quality), radius, font, type scale (13 sizes) |
| Badge/Chip scales | 106–118 | badge (xs/sm/md/lg/xl), chip (md/lg) |
| Responsive system | 121–146 | BREAKPOINTS, ResponsiveContext, useResponsive() hook, useRsp() |
| surfaceCtx() | 154–246 | Surface-aware color resolver: 11 context variants (default, accentSubtle/Solid, brandSubtle/Solid, grapeSubtle/Solid, successSubtle/Solid, errorSubtle, warningSubtle) |
| Icon + ICON_MAP | 166–250 | Icon component, 200+ Material Symbols mappings |
| NAV_ITEMS / NAV_BOTTOM | 193–203 | Navigation config (dashboard, discover, library, activity, quality, settings) |
| Button | 207–241 | Variants: primary, accent, secondary, ghost, destructive. States: hover, active, disabled, loading |
| Input | 243–273 | Props: value, onChange, placeholder, error, disabled |
| Select | 275–303 | Props: value, onChange, options, error, disabled, placeholder |
| typeBadgeStyle() | 435–448 | Returns badge style for content type (movie, series, anime) |
| PosterImage | 476–495 | Poster thumbnail with gradient fallback |
| StatusPill | 512–532 | Status badge: healthy, degraded, failed, info, testing, idle |
| Card | 534–557 | Generic card container. Props: onClick, hoverable, selected |
| SettingToggle | 562–598 | Toggle switch. ARIA: role=switch, aria-checked. Props: disabled |
| SectionHeader | 603–640 | Section header with icon, title, count, action button |
| SegmentedControl | 648–695 | Toggle group. ARIA: role=tablist/tab, aria-selected, roving tabIndex |
| HScrollArea | 697–750 | Horizontal scroll with arrow buttons |
| Dropdown | 780–820 | Context menu trigger + items |
| Topbar | 800–900 | Desktop topbar with title, subtitle, action slots |
| Sidebar | 900–1000 | Collapsible left nav. ARIA: aria-expanded, dynamic aria-label |
| SearchBar | 1025–1151 | ⌘K shortcut, 480px expand. ARIA: aria-autocomplete=list, aria-expanded |
| SearchDropdownRow | 1155–1220 | Individual search result. ARIA: role=option |
| SearchDropdown | 1222–1344 | Typeahead dropdown for library/discover results |
| NotificationBell | 1348–1372 | Bell icon with count badge. ARIA: aria-label |
| Toast | 1376–1431 | Auto-dismiss notification. ARIA: role=alert/status, aria-live, aria-atomic |
| PosterCard | 1433–1700 | Full poster card: discover/search/library variants. ARIA: role=button, tabIndex, keyboard handler |
| LIBRARY_TITLES (mock data) | ~2000–2400 | 15 titles with metadata, cast, crew, media files, episodes |
| SearchResults | 2650–3000 | Full search view with filters, sorting, gallery/list modes |
| ViewDashboard | 3000–3200 | Stats cards, recent activity, attention queue, health status |
| RatingBadge | 3100–3150 | Two-part movie/show rating display (exempt from badge scale) |
| EditTitleModal | 3300–3450 | Edit individual title metadata |
| ViewLibrary | 3450–3800 | Library grid: filter controls, type/status/quality filters |
| ModalShell | 4010–4104 | Reusable modal. ARIA: role=dialog, aria-modal, aria-labelledby, Escape key |
| ManageFilesModal | 4108–4350 | File management table (episodes/media files) |
| SearchResultRow | 4571–4700 | Extracted component for InteractiveSearchModal .map() rows (Sucrase fix) |
| InteractiveSearchModal | 4700–4860 | NZB search modal with 11-column grid, grab/reject actions |
| ViewActivity | 4500–4800 | Activity log and event viewer |
| GrabConfirmDialog | 5005–5100 | Confirmation dialog for override/grab release |
| SourceTierPicker | 5104–5200 | Drag-drop source quality tier selector |
| ViewQuality | 5000–5400 | Quality audit and profile management |
| QualityProfileWizard | 5600–6200 | Multi-step wizard for quality profiles (5 steps) |
| ViewSettings | 6000–6300 | Settings view with sections |
| ProfileSourceBadge | ~6154 | Uses badge.md + mono font |
| QualityProfilesSection | 6340–6500 | Profile display and management |
| SettingsQualitySection | 7003–7043 | Settings panel for quality profiles |
| SettingsGroup / SettingsRow | 7045–7086 | Settings layout components |
| BottomTabBar | 7092–7132 | Mobile-only bottom navigation |
| MeridianApp (default export) | 7138–7500 | Root composition: view routing, search state, toast queue, responsive layout |

#### Coverage
- States: ✅ hover, active, disabled, loading (Button); ✅ error, disabled (Input, Select); ✅ selected (Card); ✅ disabled (SettingToggle, NavItem)
- ARIA: ✅ complete — 14 components updated (DS-2026-007)
- Tokens: ✅ all semantic tokens referenced in theme-tokens.css
- Badge scale: ✅ 5-tier normalized (DS-2026-005), 3 exempt components annotated

#### Changelog (last 5)
- 2026-03-08 — Cross-prototype alignment: global focus ring, ModalShell focus trap + exit animation, decorative shadow removal
- 2026-03-08 — Component state expansion: Button loading, Input/Select error+disabled, Card selected, SettingToggle/NavItem disabled
- 2026-03-08 — ARIA + keyboard pass: 14 components (role, aria-*, keyboard handlers, focus management)
- 2026-03-08 — Badge anatomy normalization: 5-tier badge + 2-tier chip scale, radius token refs
- 2026-03-08 — Theme-tokens.css extension: testing status, info/testing ctx, radius, badge/chip CSS tokens

---

### setup-wizard-prototype-v0.1.jsx
- **Size**: ~1846 lines | 84 KB
- **Purpose**: 6-step setup wizard: account, storage, downloads, indexers, quality, health check
- **Last modified**: 2026-03-08 — Cross-prototype alignment (Card API, surfaceCtx aliases, text.tertiary contrast)

#### Structure
| Section | Lines | Contents |
|---------|-------|----------|
| Token definitions | 19–103 | tokens, radius, font, type scale (mirrors app-shell) |
| Badge/Chip scales | 107–119 | badge (xs–xl), chip (md/lg) |
| surfaceCtx() | 127–211 | Surface-aware color resolver (8 contexts) |
| Responsive system | 214–237 | BREAKPOINTS, ResponsiveContext, useResponsive(), useRsp() |
| ICON_MAP | 244–260 | 15 Material Symbols mappings |
| Icon | 262–283 | Material Symbols renderer |
| Button | 287–339 | 5 variants, 3 sizes. States: hover, active, disabled, loading (CSS @keyframes spinner) |
| Input | 341–373 | Props: label, placeholder, error, disabled, helpText, mono |
| Select | 375–406 | Props: label, options, error, disabled, helpText |
| Toggle | 408–449 | ARIA: role=switch, aria-checked, keyboard handler. Props: disabled |
| StatusPill | 451–469 | 5 states: healthy, degraded, failed, testing, idle |
| Card | 471–481 | Container wrapper |
| ProgressBar | 483–489 | Horizontal progress bar |
| StepAccount | 493–667 | Step 1: admin account, password strength, passkey registration |
| StepStorage | 671–737 | Step 2: storage location selection (3 drives) |
| StepDownloads | 741–831 | Step 3: download client config (SABnzbd/NZBGet) |
| StepIndexers | 835–953 | Step 4: NZB indexer directory (4 presets) |
| LANGUAGES array | 957–998 | 37 language entries with region codes |
| LanguageSelect | 1021–1164 | Searchable dropdown, region-aware sorting, keyboard accessible |
| StepQuality | 1168–1453 | Step 5: resolution, languages, subtitle sync, AI filtering, upgrade toggle |
| StepHealthCheck | 1457–1549 | Step 6: 4-check diagnostic with progress simulation |
| MobileStepIndicator | 1555–1590 | Dot stepper for mobile; keyboard accessible |
| SetupWizard (default export) | 1592–1846 | Root: step routing, data persistence, responsive layout, footer nav |

#### Coverage
- States: ✅ hover, active, disabled, loading (Button); ✅ error, disabled (Input, Select, Toggle)
- ARIA: ✅ complete — 7 components updated (Button, Toggle, Input, Select, LanguageSelect, step indicators, storage cards)
- Focus: ✅ global focus ring CSS via injected `<style>` block
- Tokens: ✅ mirrors app-shell token definitions

#### Changelog (last 5)
- 2026-03-08 — Cross-prototype alignment: Card onClick/hoverable props, surfaceCtx legacy alias removal, text.tertiary contrast fix
- 2026-03-08 — Component state expansion: Button loading, Input/Select error+disabled, Toggle disabled
- 2026-03-08 — ARIA + keyboard pass: 7 components + global focus ring CSS
- 2026-03-08 — Badge anatomy normalization: badge/chip scales added

---

### meridian-design-system-v0.1.jsx
- **Size**: ~1175 lines | 51 KB
- **Purpose**: Foundation reference component library — token demos, theme switching, component gallery
- **Last modified**: 2026-03-07 — Initial creation (Phase 0)

#### Structure
| Section | Lines | Contents |
|---------|-------|----------|
| Global Primitives | 16–64 | primitives: brand (teal 50–950), neutral (slate 0–950) |
| Semantic Tokens | 69–179 | semanticTokens: surface, border, text, interactive, status, provenance, overlay, quality, surface context cascades |
| Typography | 185–209 | Inter sans, JetBrains Mono mono, font sizes xs–3xl |
| Spacing | 213–231 | 4px base scale, 0.5–24 (2px–96px) |
| Radius | 233–241 | xs (2px) → full (9999px) |
| Elevation | 245–259 | 3 levels (ring-based dark, shadow-based light) |
| Motion | 261–275 | duration (instant–slower), easing curves |
| ThemeContext | 281–297 | Provider: manages mode prop (dark/light) |
| Section | 300–323 | Layout wrapper |
| SwatchGrid | 324–362 | Color palette display |
| TokenPair | 363–389 | Dual-value token display |
| TypeSample | 390–429 | Typography preview |
| StatusBadge | 430–454 | Status indicator badge |
| ProvenanceBadge | 455–475 | Source origin badge |
| SampleButton | 478–530 | Button: default/outline/ghost, sm/md/lg |
| SampleCard | 531–576 | Card with surface contexts |
| SampleActivityItem | 577–614 | Activity feed list item |
| SampleHealthIndicator | 615–650 | Health status indicator |
| SampleInput | 651–680 | Text input |
| MeridianDesignSystem (export) | 681–1175 | Root: theme toggle, token demos, component gallery |

#### Changelog (last 5)
- 2026-03-07 — Initial creation (Phase 0 foundation)

---

### theme-tokens.css
- **Size**: ~744 lines | 28 KB
- **Purpose**: CSS custom properties for dual-theme system (dark/light). All Tailwind semantic colors resolve via var() references here.
- **Last modified**: 2026-03-08 — text.tertiary dark mode contrast fix (#78859a → #8892a4)

#### Structure
| Section | Lines | Contents |
|---------|-------|----------|
| Dark theme (:root) | 10–222 | 95+ CSS custom properties: surface, border, text, interactive, status (incl. testing), provenance, accent, grape, overlay, brand3p, quality, surface context cascades (9 contexts), radius scale, badge anatomy (5 tiers), chip anatomy (2 tiers), elevation |
| Light theme | 226–435 | [data-theme="light"] block: identical structure, light-mode values |
| System preference fallback | 437–628 | @media (prefers-color-scheme: light): applies light theme when no data-theme set |
| Surface context cascades (CSS) | 634–735 | [data-surface] attribute selectors for .text-ctx-primary/secondary/tertiary, icon, border across 9 contexts (default, accent, brand, grape, success, warning, error, info, testing) |
| Reduced motion | 737–744 | @media (prefers-reduced-motion: reduce): zeroes transitions/animations |

#### Coverage
- Themes: ✅ dark (default), light, system preference
- Status: ✅ success, warning, error, info, testing (all 5 with bg/text/border variants)
- Context: ✅ 9 surface contexts × 5 tokens = 45 context properties
- Radius: ✅ 6-step scale as CSS custom properties
- Badge: ✅ 5 tiers × 4 props = 20 CSS custom properties
- Chip: ✅ 2 tiers × 3 props = 6 CSS custom properties
- WCAG: ✅ 4 AA remediation adjustments applied

#### Changelog (last 5)
- 2026-03-08 — text.tertiary dark mode contrast fix: #78859a → #8892a4 (4.6:1 on raised)
- 2026-03-08 — Token layer extension: --status-testing-*, --ctx-info-*, --ctx-testing-*, --radius-*, --badge-*-*, --chip-*-*, info/testing cascade rules
- 2026-03-07 — Initial creation (Phase 0 foundation)

---

### tailwind.config.js
- **Size**: ~276 lines | 13 KB
- **Purpose**: Tailwind CSS config consuming CSS custom properties from theme-tokens.css
- **Last modified**: 2026-03-08 — Added testing status, info/testing ctx, radius var() refs

#### Structure
| Section | Lines | Contents |
|---------|-------|----------|
| Content + dark mode | 12–13 | content paths, darkMode selector |
| Font families | 17–20 | sans (Inter), mono (JetBrains Mono) |
| Font sizes | 22–31 | xs (11px) → 3xl (36px) with lineHeight + letterSpacing |
| Border radius | 33–41 | xs/sm/DEFAULT/lg/xl/full via var(--radius-*) with fallbacks |
| Extended colors | 43–224 | 11 color groups: brand, surface, border, text, interactive, status (incl. testing), provenance, overlay, brand3p, quality, ctx (9 contexts × 5 tokens) |
| Spacing | 227–242 | 4px base: 0.5 (2px) → 24 (96px) |
| Box shadow | 245–250 | elevation-0/1/2/3 |
| Backdrop blur | 253–255 | overlay: 4px |
| Transition duration | 258–264 | instant (75ms) → slower (500ms) |
| Transition timing | 266–271 | DEFAULT, in, out, spring curves |

#### Changelog (last 5)
- 2026-03-08 — Added status.testing-* mappings, ctx.info-*/testing-* mappings, borderRadius updated to var() with fallbacks
- 2026-03-07 — Initial creation (Phase 0 foundation)

---

### ds-triage-report_v1.0_2026-03-08.md
- **Size**: ~700 lines | 34 KB
- **Purpose**: Comprehensive triage report: 4-axis methodology, token coverage, ARIA compliance, cross-prototype drift, spec-to-implementation gaps. Contains DDRs DS-2026-001 through DS-2026-009.
- **Last modified**: 2026-03-08 — All H/M items resolved, DDR DS-2026-009 added

### ds-audit-report-v0.1.md
- **Size**: ~271 lines | 16 KB
- **Purpose**: Component & token audit: structural soundness, drift analysis (spec vs CSS vs JSX), 5 critical areas for Phase 1
- **Last modified**: 2026-03-08 — Audit completed

### surface-context-audit-v0.1.md
- **Size**: ~293 lines | 15 KB
- **Purpose**: Surface-aware context system audit: compliance checklist for tinted surfaces, 9 context maps, resolution rules
- **Last modified**: 2026-03-08 — Audit completed

### wcag-audit-v0.1.md
- **Size**: ~126 lines | 6.7 KB
- **Purpose**: WCAG 2.1 AA contrast audit: 96 pairings tested, 78 pass, 8 failures with remediation, 6 intentional substandard
- **Last modified**: 2026-03-07 — Initial creation

### MERIDIAN-DS-SPEC.md
- **Size**: ~290 lines | 12 KB
- **Purpose**: Consolidated token & component spec: three-tier architecture, surface tokens, semantic mappings, typography, spacing, radius, elevation
- **Last modified**: 2026-03-07 — Initial creation

### meridian-ds-spec-v0.1.md
- **Size**: ~325 lines | 18 KB
- **Purpose**: Detailed v0.1 foundation spec: design principles, token architecture rationale, three-tier justification
- **Last modified**: 2026-03-07 — Initial creation

### component-anatomy-spec-v0.1.md
- **Size**: ~572 lines | 23 KB
- **Purpose**: Component definitions: Button, Card, Input, Badge, Dialog, Select, Checkbox, Radio — anatomy, prop API, variant matrix, states, a11y
- **Last modified**: 2026-03-07 — Initial creation

### component-tokens-spec-v0.1.md
- **Size**: ~369 lines | 17 KB
- **Purpose**: Component-tier token layer spec: naming convention, three-tier architecture, surface context system (9 contexts), override pattern
- **Last modified**: 2026-03-07 — Initial creation

### density-modes-spec-v0.1.md
- **Size**: ~237 lines | 9.9 KB
- **Purpose**: Comfortable/Default/Compact density tiers: independent of theme, typography/spacing/touch target adjustments
- **Last modified**: 2026-03-07 — Initial creation

### app-shell-spec-v0.1.md
- **Size**: ~318 lines | 15 KB
- **Purpose**: App shell architecture: sidebar+topbar layout, nav structure, search, notifications, responsive breakpoints
- **Last modified**: 2026-03-07 — Initial creation

### data-model-spec-v0.1.md
- **Size**: ~609 lines | 24 KB
- **Purpose**: Data model: 5 design principles, 20+ entities with relationships, event sourcing
- **Last modified**: 2026-03-07 — Initial creation

### data-model-erd-v0.1.mermaid
- **Size**: ~278 lines | 6 KB
- **Purpose**: Entity-relationship diagram: Title/Season/Episode/MediaFile/ExternalID/QualityProfile entities
- **Last modified**: 2026-03-07 — Initial creation

### module-interfaces-spec-v0.1.md
- **Size**: ~544 lines | 26 KB
- **Purpose**: Module architecture: 12 Go modules, direct interface calls + event bus, dependency graph
- **Last modified**: 2026-03-07 — Initial creation

### go-scaffold-spec-v0.1.md
- **Size**: ~546 lines | 19 KB
- **Purpose**: Go project structure: cmd, internal, pkg, tests, DI wiring, build/run scripts
- **Last modified**: 2026-03-07 — Initial creation

### auth-architecture-spec-v0.1.md
- **Size**: ~490 lines | 26 KB
- **Purpose**: Auth & session design: passkey-first, zero external auth, session durability, CSRF/XSS protections
- **Last modified**: 2026-03-07 — Initial creation

### privacy-architecture-review-v0.1.md
- **Size**: ~408 lines | 20 KB
- **Purpose**: Privacy audit: external connection registry, metadata API payloads, anonymity-preserving patterns
- **Last modified**: 2026-03-07 — Initial creation

## centricPLM — 07-projects/02-centricPLM/context/ (gitignored)

### cell-indicators-pilot.md
- **Purpose**: Authoritative running state of the C8 data-table cell-indicator system (Figma branch `cell-indicators`): DS sourcing rules, cell architecture, code-validated indicator matrix (GROUNDED/ADD-VIZ/FUTURE tiers), two-tier editability model, read-only lock+tint three-scope system, worst-case density demo, node IDs, and open Sean sign-offs.
- **Last modified**: 2026-07-02 — worst-case scattered-locks demo + tooling gotchas appended

## figma-repo-sync-plugin — 07-projects/09-figma-repo-sync-plugin/docs/ (gitignored)

### 2026-05-22-color-pipeline-refactor-plan.md
- **Purpose**: Root-cause audit (3-agent) of the shadcn→Tailwind→Figma color pipeline + phased refactor plan. Documents the divergent-parser / two-token-table / silent-literal-fallback hazards and the Phase 0–4 plan.
- **Last modified**: 2026-05-22 — Initial creation

### 2026-05-23-state-representation-decision-tree.md
- **Purpose**: Authoritative CVA variant×state→Figma spec. Locked decisions: physical State axis, normalized state-layer (Decision B), grouped `<slot>/<state>` naming with explicit `default`, ring-as-stroke-overlay anatomy, state-layer opacities (12/24/32/50%), per-component derivation. Carries the ⚠ engineer-doc requirement for the `default` affordance.
- **Last modified**: 2026-05-23 — Initial creation
