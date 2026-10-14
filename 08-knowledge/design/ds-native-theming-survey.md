---
tags: [design-systems, color, theming, tokens, survey, emphasis-engine]
created: 2026-10-08
updated: 2026-10-08
status: working
confidence: medium
sources: [emphasis-engine native examples 2026-10-08 (github.com/snds/emphasis-engine, docs/systems/*.md, docs/native/BRIEF.md)]
related_skills: [ds-advisor, design-engineer]
related_projects: [emphasis-engine]
relations:
  relates-to:
    - "[[radix-derived-color-system]]"
    - "[[design-token-architecture]]"
    - "[[interaction-state-semantics]]"
    - "[[ds-native-shadcn]]"
    - "[[ds-native-radix]]"
    - "[[ds-native-material]]"
    - "[[ds-native-bootstrap]]"
    - "[[ds-native-daisyui]]"
    - "[[ds-native-carbon]]"
    - "[[ds-native-fluent]]"
    - "[[ds-native-primer]]"
    - "[[ds-native-atlassian]]"
    - "[[ds-native-antd]]"
    - "[[ds-native-chakra]]"
    - "[[ds-native-mantine]]"
    - "[[ds-native-cds]]"
    - "[[centric-ds-ideas-from-ds-survey]]"
---

# Theming 13 design systems from the outside — what decides whether a theme reaches a component

## For future agent
- **TL;DR:** We themed 13 popular design systems with one solved color theme, each rendering its own real components on its own page. Where a system makes its state colors decides whether a runtime theme reaches them. Separate state tokens, runtime `color-mix()`, and opacity all follow a CSS-variable theme. Build-time literals (Bootstrap's Sass) and colors computed in JS (Ant Design, Coinbase CDS) don't. The second big finding: most systems tie info to brand somewhere, so changing the brand moves the meaning of info.
- **Key claims:** the taxonomy tables below. Each system's detail is in its `ds-native-<id>` entry.
- **Centric takeaways:** [[centric-ds-ideas-from-ds-survey]].
- **As of:** 2026-10-08 (package versions in each entry; probe fixes same day) · **Status:** current
- **Audience:** `for: all`

## How the survey was run (timeless method)
- **One page per system.** Each page is built from the system's real packages and laid out by its own guidelines, with shared content (an enterprise PLM "Workspace settings" scene). The project is Emphasis Engine (`snds/emphasis-engine`, `src/native/`).
- **Isolation by iframe.** Systems ship global resets and base styles that collide, so each page is its own document.
- **The theme arrives by `postMessage`.** It's applied the way the probe applies its sentinels:
  - root variables: inline `!important` on `<html>` and on every element the system writes variables to (a provider div);
  - scoped variables: `!important` rules on their component selector;
  - component selectors that redefine a root variable with a literal value: the same value.
- **Restore rule.** When the theme is removed, the kit only puts a variable back if its value is still the one the kit set. Providers like Coinbase CDS rewrite their inline variables on a mode switch, and a blind restore wrote light values over fresh dark ones.
- **What we checked.** Stock vs. themed, light and dark, at 390 and 1280 wide, with a loud magenta brand so any component the theme misses stands out.

## Where theme variables live
| Location | Systems |
|---|---|
| `:root` / `<html>`, switched by class or attribute | shadcn (`.dark`), Bootstrap (`data-bs-theme`), daisyUI (`data-theme`), Carbon (zone classes), Material (yours to define), Atlassian, Chakra, Mantine |
| A provider or wrapper element | Radix (`.radix-themes`), Fluent (FluentProvider div), Primer (BaseStyles repeats `data-color-mode`), Ant Design (cssVar class on each component root), Coinbase CDS (inline on the ThemeProvider div) |

**Why it matters:** variables on a provider div don't reach portals (menus, popovers) unless the portal gets its own provider. They're also invisible to tools that read `:root`.

## How state colors are made, and whether a runtime theme follows
| Mechanism | Systems | Theme follows? |
|---|---|---|
| Separate token per state | Carbon, Fluent, Primer, Atlassian, Mantine | Yes, if the state tokens are themed too |
| Runtime `color-mix()` of the role | daisyUI, Chakra (hover) | Yes, automatically |
| Opacity over the role | shadcn (`/90`, `/10`), Material (state layers), Chakra (disabled) | Yes, but contrast depends on what's underneath |
| Literals baked at build time | Bootstrap (Sass `shade-color()`, checked states, focus rings) | No |
| Computed in JS, written as literals | Ant Design (component tokens), Coinbase CDS (hover, pressed, disabled) | No |

## Why a theme misses a component (failure modes seen)
1. **Hidden alias chain.** Radix's Switch reads `--accent-track` → `--blue-track` → `--blue-9`. Solving `--accent-9` doesn't touch it.
2. **Literals in component variables.** Bootstrap's `--bs-btn-bg: #0d6efd`. Ant Design's `--ant-tabs-ink-bar-color: #1677ff`.
3. **JS-computed states.** Coinbase CDS hover and disabled. Ant Design's Tabs, Radio, and Menu.
4. **Components that skip the semantic tier.** Fluent's Badge and Field error read palette tokens directly.
5. **Token islands.** Primer's `--header-*`. A themed app looks half-done.
6. **Base-class defaults that variants depend on.** Bootstrap's outline and link buttons rely on `.btn`'s transparent `--bs-btn-bg`. Theming the base turns them solid.
7. **Zones defined as full literal sets.** Carbon's `g100` repeats ~300 literals. One solve can't cover nested zones.

## The info-equals-brand trap
- **Where it shows up:**
  - Primer: info and brand are one role (`accent`).
  - Coinbase CDS: the informational banner uses primary.
  - Chakra and Mantine: the default brand palette is blue, and blue is also their info color.
  - Carbon: the "blue" tag doubles as info.
  - Ant Design and Fluent: the info background derives from the neutral scale. When the neutrals are tinted toward the brand, info turns brand-colored.
- **Rule (timeless):** status needs its own roots, never an alias of brand or of a brand-tinted neutral.

## Gaps in the systems themselves (dated: 2026-10)
- **Material (@material/web):** no card, table, alert, top app bar, or breadcrumb. No shipped theme or dark scheme. Only one status role (error).
- **Radix Themes:** no breadcrumb. No invalid state on text fields.
- **Coinbase CDS:** no breadcrumb, no success banner, no outline button.
- **Fluent:** no danger button. Fluent's guidance is a neutral button plus a confirm step.
- **Bootstrap:** no stat component. **Chakra:** no native mobile nav.

## Stock accessibility misses seen
- **Text contrast:**
  - Mantine `dimmed` text ≈ 3.3:1. Its placeholder ≈ 2.1:1, and its yellow alert ≈ 2.7:1.
  - Chakra `fg.subtle` ≈ 2.6:1.
- **Control edges:** shadcn's field borders ≈ 1.3:1.
- **Disabled as opacity only** (Chakra, daisyUI) loses the variant over striped or selected rows.

## Engineering notes for hosting many systems (timeless)
- **Build every page into the site.** One multi-page Vite build, one entry per system. Shared chunks deduplicate React.
- **Make switching instant.** Keep the last three frames mounted, and send only the visible frame theme messages. A service worker caches the whole build after the first visit (about 8.8 MB, 86 files).
- **Size the frame to its content.** The page reports its height through a `ResizeObserver`, so the app page scrolls, not the frame. Native pages must not use `100vh`.
- **Solve in the browser.** The engine uses Vite-only imports (`import.meta.glob`), so screenshot scripts solve in the page through the dev server, not in Node.

## Probing a design system from outside: what went wrong, and the fix (timeless)
These were found by theming real pages, then fixed in Emphasis Engine's probe and generator on 2026-10-08.
1. **Read a scoped variable's value from the rule that declares it.** Don't read it off the first matching element. Bootstrap's `.btn { --bs-btn-bg: transparent }` reads blue off a `.btn-primary`, and outline buttons then theme solid.
2. **Confirm every trace with a second, shuffled sentinel assignment.** A build-time literal can sit near a blend of two sentinels by chance. Two unrelated assignments won't both agree.
3. **Group painted pairs by property as well as by colors.** An outline and a fill with the same colors are different jobs.
4. **Keep the system's source order when you override scoped variables with `!important`.** Base before variant, or the base wins.
5. **Read every channel format.** That includes comma triplets (`13, 110, 253`) used through `rgba(var(--x-rgb), a)`.
6. **Names beat chroma for status.** Look in the selector too. Pale status tints have almost no chroma, and `.alert-success` names the role the variable doesn't. Blue is info, and brand comes from brand words.
7. **A variable's parent must be under it in both modes.** Otherwise use the page. A variable unpainted in one mode keeps its stock offset.
8. **Systems that compute states in JS need the theme object, not only CSS variables.** Ant Design's algorithm and Coinbase CDS's ThemeProvider re-derive hover, pressed, and component tokens from it.
9. **Measure the real page, not a minimal harness.** Every alert, badge, row, and header that ships gets probed. A harness only covers what someone remembered to put in it.

Still as each system designed it:
- Primer and Coinbase CDS tie info to brand.
- Chakra has no brand palette by default.
- Bootstrap's checked states and focus rings are build-time literals.
