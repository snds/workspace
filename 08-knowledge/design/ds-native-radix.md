---
tags: [design-systems, color, theming, tokens, radix, emphasis-engine]
created: 2026-10-08
updated: 2026-10-08
status: working
confidence: medium
sources: [emphasis-engine native example build 2026-10-08, github.com/snds/emphasis-engine docs/systems/radix.md, src/native/radix.tsx]
related_skills: [ds-advisor, design-engineer]
related_projects: [emphasis-engine]
relations:
  relates-to:
    - "[[ds-native-theming-survey]]"
---

# Radix Themes — how its color works, learned by theming it

## For future agent
- **TL;DR:** Color is 12-step role scales (1–2 backgrounds, 3–5 component states, 6–8 borders, 9–10 solids, 11–12 text) plus alpha twins. They live on `.radix-themes`, and `data-accent-color` remaps `--accent-*` per subtree. Hidden alias chains (`--accent-track` → `--blue-track` → `--blue-9`) are the main reason a theme doesn't reach a component (the Switch stayed stock).
- **Key claims:** see "How its color works" and "What the solved theme reached" below. Each was observed by rendering the real components and injecting a solved theme (stock vs. themed, light and dark, 390 and 1280 wide).
- **Centric takeaways:** section "Ideas for the Centric design system"; consolidated in [[centric-ds-ideas-from-ds-survey]].
- **As of:** 2026-10-08 (dated: package versions below) · **Status:** current
- **Audience:** `for: all`
- **Update 2026-10-08 (profile fixes):** Fixed: `--accent-track` (switch, slider, and progress tracks) is an alias of step 9, and `--accent-surface` is solved, so the switch follows the brand.

## At a glance

- Package: `@radix-ui/themes` 3.3.0 (MIT). Built on Radix Primitives and Radix Colors.
- Page: `src/native/radix.tsx`, entry `native/radix.html`.
- Docs used:
  - https://www.radix-ui.com/themes/docs/theme/color
  - https://www.radix-ui.com/themes/docs/theme/dark-mode
  - https://www.radix-ui.com/themes/docs/components/layout (Container, Flex, Grid, Box)
  - https://www.radix-ui.com/themes/docs/components/button, /callout, /table, /badge, /tab-nav, /tabs, /text-field, /select, /switch, /checkbox, /radio-group
  - https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale

## How its color works

- Every color is a 12-step scale, in two forms: solid (`--blue-9`) and alpha (`--blue-a9`). Steps have fixed jobs. 1–2 backgrounds, 3–5 component backgrounds (rest, hover, pressed), 6–8 borders, 9–10 solids, 11–12 text.
- Components never name a hue. They paint `--accent-*` and `--gray-*`. The `Theme` sets `accentColor` and `grayColor`, which remaps `--accent-N` to `--blue-N` (and so on) under `[data-accent-color]`.
- A `color` prop on a component (`<Badge color="green">`) sets `data-accent-color` on that element. The same remap happens locally. That's how status works: the component still paints `--accent-a3`, which now points at green.
- A few derived tokens sit beside the scales: `--accent-contrast` (label on step 9), `--accent-surface` (translucent tint for soft fields), `--accent-indicator` (checkbox and radio fill), `--accent-track` (switch, slider, progress fill), `--focus-8`, `--color-background`, `--color-panel`, `--color-surface`.
- Variables live on `.radix-themes` (the `Theme` element) and on `:root, .light` / `.dark`. Light and dark switch by class: `.dark` on `<html>` and an `appearance="inherit"` Theme picks it up.
- States are separate steps, not opacity or filters. Solid hover is step 10. Soft hover is a4 after a3. Outline is an inset 1px ring of a8. Disabled is `--gray-a3` background and `--gray-a8` text. Components lean on the alpha steps so they sit on any panel.

## Building the native page

- One root `Theme` with stock `accentColor="blue"` and `grayColor="gray"`. That matches the probe harness and the profile's reference values.
- Layout uses Radix primitives only: `Container size="4"`, `Flex` and `Grid` with responsive props (`columns={{ initial: "1", md: "2" }}`), the 1–9 space scale for gaps and padding. No hand-written CSS except `body { margin: 0 }` (Radix doesn't reset the UA margin) and `overflow-x: auto` on the two nav rows so they scroll on a phone.
- App navigation is `TabNav` (Radix's link-based nav), with `IconButton` and `Avatar` on the right. Sections are `Tabs`.
- Forms follow the Radix examples: `Text as="label" size="2" weight="medium"` above the control, helper text as `Text size="1" color="gray"`. Switch and checkbox are wrapped in a `Text as="label"` with the control first.
- Form actions sit at the end. Cancel is `variant="soft" color="gray"`, then the solid primary. That's the order the Radix dialog and form examples use.
- Action hierarchy by variant: solid, soft, outline, ghost. Danger is `color="red"` on a solid button. Radix has no danger variant. Red is a color, not a role.
- Status: `Callout` and `Badge` with `color` green, blue, amber, red. Table is `Table.Root variant="surface"`, which wraps itself in a ScrollArea, so the wide table scrolls inside its own box at 390px.
- Missing or substituted:
  - **Breadcrumb**: Radix Themes has none. It's composed from `Link size="2" color="gray"` and `Text` separators inside a `nav`.
  - **Invalid field**: no invalid state on `TextField`. The `color` prop only changes the focus ring and selection. I used `color="red" variant="soft"` plus red helper text and `aria-invalid`. That's a visible, native treatment, not a dedicated one.
  - **Disabled text**: no prop. I used `var(--gray-a8)`, the step Radix's own disabled controls use.
  - **Icons**: Radix docs use `@radix-ui/react-icons`, which isn't installed. Tabler icons stand in.

## What the solved theme reached

Shots compared: `radix-{390,1280}-{light,dark}-{stock,themed}.png`, magenta brand.

Reached:
- Solid, soft, outline and ghost buttons, links, the active `TabNav` and `Tabs` underline, the `Avatar` fallback, checkbox and radio fills (`--accent-indicator`), focus rings. All of these paint `--accent-*`, which the kit writes on `<html>` and `.radix-themes`.
- Gray steps: field borders, card edges, separators, the disabled button, and table header tint picked up a faint brand cast. That's the solver tinting neutrals, as intended.
- The red scale: the danger button got a brighter, more saturated red. The callout, the soft invalid field and the "Rejected" badge shifted too.

Not reached:
- **Switch**. It stayed stock blue in every themed shot. The switch paints `--accent-track`, which the accent remap points at `--blue-track`, which is `var(--blue-9)`. The solver writes `--accent-9` but not `--accent-track`, so the chain never touches it. Slider and Progress use the same token and would miss it the same way. Fix in the profile: solve `--accent-track` as an alias of `--accent-9` (the way `--accent-indicator` already is).
- **`--accent-surface`**, the translucent tint behind soft fields in the accent color. Same cause: it remaps to `--blue-surface`, a literal. Nothing on this page uses an accent-colored soft field, but a `TextField variant="soft"` with no color prop would stay blue.
- **Green, blue and amber status colors**. Those are separate scales the profile doesn't solve (only accent, gray and red). The success, info and warning callouts and badges are pixel-identical stock vs themed. That's correct behavior for status, but it means the engine can't tune their contrast in Radix yet.
- Worth noting: the info callout uses the *blue* scale, not the accent. In stock both are blue, so info and brand look identical. Theming the accent separates them. With a blue brand they'd collide again.

## Accessibility notes

- Stock solid buttons put white on blue-9 (#0090ff). That's about 3.2:1 (WCAG 2), under 4.5 for 14px text. Radix picks step 9 for vividness, not text contrast. The same holds for the red danger button.
- Soft buttons use accent-a11 on accent-a3. Fine for text, but the soft button's edge is almost invisible on white. It reads as text with a wash, not as a button.
- Placeholder text (`--gray-a10`) is light, about 3:1.
- Disabled text at `--gray-a8` is intentionally faint (around 2:1). That's expected for disabled, but don't reuse it for "tertiary" information.
- Radio and checkbox outlines at rest are `--gray-a7`, low-contrast against the card. They pass 3:1 for UI components only narrowly.
- The amber warning callout (amber-a11 on amber-a3) looked the weakest of the four in light mode by eye. Worth measuring.

## Ideas for the Centric design system

- **Borrow the step contract.** Radix's 12 steps with fixed jobs (3–5 component states, 6–8 borders, 9–10 solids, 11–12 text) are the cleanest semantic tier I've seen. Centric already uses Radix-derived scales. Making the step-to-job mapping the semantic tier (not just a palette) lets every framework port derive hover and pressed states without new tokens.
- **Borrow local color remapping.** `data-accent-color` on any element remaps `--accent-*` for that subtree. Status, category and per-vertical accents (fashion vs food vs engineering) become one attribute, with no extra component variants. It works the same in Vue, Angular and React because it's pure CSS.
- **Borrow alpha twins.** Alpha steps let a badge or soft button sit on a white page, a gray panel or a selected table row and keep the same perceived weight. Dense PLM tables with row selection and zebra striping need exactly that.
- **Avoid the hidden alias chain.** `--accent-track` → `--blue-track` → `--blue-9` is invisible until you theme it and the switch stays blue. In a 3-tier model, every component token should resolve to a semantic token, never back down to a global hue. Lint for component tokens that point at a named hue.
- **Avoid "step 9 is the button".** It's vivid but fails text contrast for mid-luminance hues. Pick the solid by contrast against its label (the engine's job), and keep step 9 as a decorative fill.
- **Avoid having no invalid state.** Radix leaves validation to the app. An enterprise form library needs a first-class invalid token set (border, ring, helper text) so bulk edit and record detail look the same everywhere.
- Density: Radix exposes `size` props (1–4) and `scaling` on `Theme` (90%–110%). `scaling` is a decent model for density modes because it scales space and type together from one attribute.

## Open issues

- Profile gap: `--accent-track` and `--accent-surface` aren't solved. Suggest aliasing `--accent-track` to `--accent-9` and deriving `--accent-surface` from `--accent-2` like `--color-surface`.
- Profile gap: status scales (green, amber, and blue as info) aren't part of the solve. That's a scope question for the engine, not the page.
- `Select.Content` portals into the Theme. The shots only show it closed, so the portal's themed state isn't verified.
