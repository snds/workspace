# Lessons Learned — Cross-System Patterns & Decision Frameworks

> Synthesis of the full UX Components read-through (62 components × 68 design systems). The companion `component-inventory.md` is the per-component reference; this file is the reasoning layer — *how to choose*, *what the systems disagree about*, and *how to apply it* to product work, layout, workflow design, and headless-→-Figma transliteration.

---

## 1. The mental model: 9 categories = 9 questions

Every UI need maps to a category, and each category answers one question:

| Category | The question it answers |
|---|---|
| **Action** | "I want the user to *do* something." |
| **Form** | "I need to *collect* a value." |
| **Navigation** | "I need the user to *get somewhere* or *reach a command*." |
| **Feedback** | "I need to *tell* the user what's happening." |
| **Data Display** | "I need to *show* records, entities, or metadata." |
| **Layout** | "I need to *group or separate* content." |
| **Overlay** | "I need a *temporary surface* above the page." |
| **Disclosure** | "I need to *hide content until asked*." |
| **Content** | "I need to *present media or symbols*." |

When you're unsure which component, first name the *question*. The category narrows 62 options to a handful; the decision trees below finish the job.

---

## 2. Decision frameworks (the "which one?" trees)

These are the highest-value output of the comparison work. Each cluster is a recurring fork where designers pick wrong.

### 2.1 Overlays — driven by **modality** and **trigger**
```
Need a temporary surface above the page?
├─ Plain text label, ≤1 sentence, non-essential?        → Tooltip   (hover/focus, never interactive)
├─ Rich preview on hover, desktop, non-critical?          → Hover Card (needs tap fallback)
├─ Rich/interactive content, must NOT block the page?     → Popover    (non-modal, no focus trap)
├─ Focused bounded task, block the page, any content?     → Dialog     (modal, focus trap, scroll lock)
├─ Destructive/irreversible decision, must acknowledge?   → Alert Dialog (modal + confirm/cancel)
└─ Secondary content related to current view, edge-anchored, keep context? → Sheet (a.k.a. Drawer)
```
Rules of thumb: **Tooltip → Popover** the moment content becomes interactive. **Dialog → Alert Dialog** the moment the action is irreversible. **Dialog → Sheet** when no decision is required and you want to keep spatial context. **Dialog → page** when the form is long/complex.

### 2.2 Single-choice input — driven by **option count** and **visibility**
```
Pick exactly one from a known set?
├─ 2–5 options, want all visible to compare?  → Radio Group
├─ 5–15 options, fixed, no search needed?     → Select
├─ >15 options, or user may not know the name? → Combobox (type-to-filter; debounce async)
└─ Mutually exclusive *view/mode* switch, 2–5 short labels? → Toggle Group (single mode) or Tabs (if it's content views)
```
The thresholds (≈5, ≈15) are the load-bearing numbers. Above 15 unfiltered options, scanning collapses → Combobox.

### 2.3 Binary control — driven by **when the change takes effect**
```
On/off?
├─ Applies INSTANTLY (dark mode, feature flag)?        → Switch  (role="switch")
├─ Submitted LATER with a form?                         → Checkbox (supports indeterminate)
└─ A stateful BUTTON in a toolbar (Bold, Grid/List)?    → Toggle  (role, aria-pressed)
```
This is the most-confused trio because every system names them differently (see §3). The *semantic* test is timing: instant = Switch, deferred = Checkbox, in-toolbar-stateful = Toggle.

### 2.4 Messaging & feedback — driven by **persistence** and **whether action is required**
```
Tell the user something?
├─ Transient confirmation, auto-dismiss, non-critical?      → Toast   (a.k.a. Snackbar/Flag)
├─ Persistent inline status tied to nearby content?         → Alert   (in document flow)
├─ Page/section-wide announcement, full width?              → Banner
└─ Blocking — user must acknowledge/decide before continuing? → Alert Dialog
```
Escalation ladder: **Toast (ignorable) → Alert (persistent) → Banner (prominent) → Alert Dialog (blocking)**. Pick the *lowest* rung that does the job; over-escalation causes fatigue.

### 2.5 Loading & progress — driven by **knowing the duration & layout**
```
Something is loading?
├─ Duration KNOWN / measurable?                  → Progress (determinate; segmented for steps)
├─ Duration UNKNOWN, small/inline?               → Spinner  (appear by ~300ms)
├─ Initial load, final LAYOUT known?             → Skeleton (best perceived perf; prevents CLS)
└─ A static measurement in a range (not a task)? → Meter    (disk/battery/strength)
```
The <300ms rule applies to all three transient ones: below it, don't show anything (the flash is worse than the wait).

### 2.6 Labels & metadata — driven by **interactivity** and **content type**
```
Small label on an element?
├─ Numeric count / status, decorative, NOT interactive? → Badge (cap at 99+)
├─ Textual category/keyword, may be removable?          → Tag
└─ Interactive token (selectable/removable, in groups)? → Chip
```
Badge = number/status annotation. Tag = textual metadata. Chip = interactive token. (Systems blur these constantly — see §3.)

### 2.7 Tabular vs list vs rich data
```
Showing many records?
├─ One meaningful column per row?            → List
├─ Multiple columns, relationships matter, static? → Table
└─ Need sort + filter + paginate + select?   → Data Table
```
Hierarchical → **Tree View**. Chronological → **Timeline**. Grouped-single-subject cards → **Card** grid.

### 2.8 Content organization — driven by **simultaneity** and **sequence**
```
Multiple chunks of content?
├─ Parallel alternatives, all labels visible, one at a time? → Tabs
├─ Stacked sections, scan-and-expand, maybe several open?    → Accordion
├─ A single optional/advanced section?                        → Collapsible
├─ Sequential steps with progress?                            → Stepper
└─ Equivalent media to cycle (gallery/hero)?                  → Carousel (sparingly)
```
Key contrast: **Tabs** show all labels and one panel; **Accordion** stacks and can open many; never use a Carousel where order/importance differs.

### 2.9 Menus & navigation — driven by **navigate vs command** and **trigger**
```
A menu or nav?
├─ Navigate between PAGES, primary?            → Navigation Menu (mega-menu; hamburger on mobile)
├─ Switch CONTENT views in one region?         → Tabs
├─ Show "you are here" path?                    → Breadcrumb
├─ Desktop app COMMANDS (File/Edit/View)?       → Menubar
├─ Button-triggered list of actions?            → Dropdown Menu
├─ Right-click contextual actions?              → Context Menu
└─ Page through a dataset?                       → Pagination
```
The deepest distinction in the whole set: **Dropdown Menu / Context Menu / Menubar use menu semantics (actions)**; **Select / Combobox use form-input semantics (values)**. Choosing the wrong family breaks both accessibility and user expectation.

---

## 3. Cross-system naming divergence — the field's biggest trap

1,900+ name mappings exist because **the same concept has many names** and — worse — **the same name means different things**. When reading any design system's docs, translate to the canonical concept before reasoning.

### 3.1 Same name → different component (false friends)
- **"Toggle"** = the stateful button (canonical) in Radix/shadcn, **but = Switch** in Atlassian, Carbon, Nord, Clarity. Always confirm: pill-on-track (Switch) vs pressed button (Toggle).
- **"Select"** = single dropdown (canonical), **but = Combobox** in Atlassian, PatternFly, Flowbite, Grommet.
- **"Tag"** = textual metadata (canonical), **but = Badge** in Carbon, USWDS, GOV.UK; **= Chip** in Fluent/Ant/Chakra.
- **"Tooltip"** = plain-text hover label (canonical), **but = Popover** in USWDS, Lightning, Duet, Backbase.
- **"Banner"** = page-wide message (canonical), **but = Alert** in Canvas, Polaris, Cedar, Seeds.
- **"Menu"** = used for Dropdown Menu, Context Menu, *and* Navigation Menu depending on the system.

### 3.2 Different name → same component (synonyms to recognize)
- **Sheet** → Drawer / Offcanvas / Side Panel / Tray / Flyout / Bottom Sheet / Slideout.
- **Dialog** → Modal / Modal dialog / Layer.
- **Toast** → Snackbar / Flag / Flashbar / Notification / Message.
- **Toggle Group** → Segmented Control / Content Switcher / Button Group / Action Group.
- **Spinner** → Loader / Loading Indicator / Busy Indicator / Progress Circle.
- **Combobox** → AutoComplete / Autosuggest / Super Select / Combo Box.
- **Separator** → Divider / HR / Horizontal Rule / Rule / Scrim.
- **Stepper** → Steps / Wizard / Progress Stepper / Progress Indicator.
- **Empty State** → Empty Prompt / Info state.

### 3.3 Practical rule
> When someone names a component, silently ask: *which of the 62 canonical concepts is this, by behavior?* Behavior (modality, trigger, semantics, when-the-change-applies) is invariant; names are not. Use the MCP `lookup` ("what is a toast called in Atlassian") to resolve any specific mapping on demand.

---

## 4. Design-system philosophies (read the lineage, infer the defaults)

The dataset spans ~68 systems. They cluster into lineages, and the lineage predicts naming, density, and component coverage. Useful when a client/team says "we follow X."

- **Primitive-first (Radix / shadcn / Ariakit / React Aria / Base Web / Headless).** Unstyled behavior + a11y; the canonical names in this dataset largely follow this lineage (Toggle, Sheet, Hover Card, Scroll Area, Collapsible exist as discrete primitives here — they're rare elsewhere). Best mental model for *transliteration* because states/anatomy are explicit.
- **Material Design (Google).** Distinctive vocabulary: **Snackbar** (Toast), **Side Sheets** (Sheet), **Chip** as a first-class citizen, **Date Pickers** (covers Calendar). Motion-forward; FAB and elevation concepts.
- **Atlassian (Design System).** Product-app DNA: **Flag** (Toast), **Drawer** (Sheet), **Section message** (Alert), **Dynamic table** (Data Table), **Date time picker** (combined). Calls Combobox "Select."
- **Carbon (IBM).** Enterprise/data-dense: **Tile** (Card), **Content Switcher** (Toggle Group), **Structured List**, **Data Table** as a flagship, **Notification** (Toast). Productivity over marketing polish.
- **Ant Design.** Data-heavy admin/console: **AutoComplete** (Combobox), **Message** (Toast), `Input.TextArea`, `Radio.Group`. Rich tables and forms.
- **Bootstrap.** Utility/framework heritage: **Offcanvas** (Sheet), **Form Control/Form Select/Form Check** naming, **Modal**, **Nav Tabs/Navbar**. Class-driven.
- **Government & public-sector (GOV.UK / USWDS / NHS / ONS).** Plain, pluralized names ("Radios", "Checkboxes", "Buttons"), accessibility-first, error-summary patterns, conservative component sets. Great accessibility reference.
- **Enterprise vendor systems (Spectrum/Adobe, Fluent/Microsoft, Polaris/Shopify, Lightning/Salesforce, Cloudscape/AWS, Fiori/SAP).** Each has signature names (Spectrum "Picker"/"Tray"; Fluent "SpinButton"/"Message bar"; Cloudscape "Flashbar"; Fiori "Message Strip"/"Busy Indicator"). When a team is on one of these, expect that vocabulary and density.

**Coverage signal:** components mapped to *many* systems (Button 80+, Dialog 85, Checkbox/Tabs/Radio 82, Table 73, Tooltip 76) are universal — safe to assume. Components mapped to *few* systems (Hover Card 6, Color Picker 7, Scroll Area 7, Timeline 9, Meter 10, Data Table 11, Tree View 13, Rating 14) are specialized — verify the target system actually has them before promising them, or plan to compose them.

---

## 5. Universal laws (cross-cutting throughlines that held across all 62)

**Accessibility (non-negotiable, repeated in nearly every component):**
1. **Every input has a visible Label** associated via `for`/`id`. Placeholder is never a label.
2. **Focus management for overlays:** modal surfaces (Dialog, Alert Dialog, modal Sheet) trap focus and return it to the trigger on close; non-modal (Popover) does not trap but closes when focus leaves.
3. **Correct ARIA roles encode intent:** `role="switch"` (Switch), `aria-pressed` (Toggle), `radiogroup` (Radio/single Toggle Group), menu/menuitem (Dropdown/Context/Menubar), `role="dialog"`+`aria-modal`, `role="tooltip"`+`aria-describedby`, `role="progressbar"`, `aria-current="page"` (Breadcrumb/Nav), `aria-sort` (Table), `aria-live`/`role="alert"` (Alert/Toast/Form errors).
4. **Keyboard patterns are component-specific and expected:** arrow keys move *within* a group (Radio, Tabs, Toolbar via roving tabindex, Menu, Tree, Slider, Calendar); Tab moves *between* widgets. Type-ahead in Select. Escape closes overlays.
5. **Never rely on color alone** (Badge, Alert, status). Pair color with text/icon/shape.
6. **Icon-only controls must have an accessible name** (Tooltip/`aria-label`).

**Timing & perception:**
7. **The 300ms rule:** below ~300ms, show no loader (the flash distracts); above it, Spinner/Skeleton/Progress.
8. **Overlay open-delays:** Tooltip 400–600ms, Hover Card 300–500ms + close grace period. Toast auto-dismiss ≥4s for readability, pause on hover.

**Hierarchy & restraint:**
9. **One primary action per section** (Button). Over-emphasis dilutes hierarchy.
10. **Pick the lowest-intensity component that works:** whitespace before Separator; Toast before Dialog; Tooltip before Popover; Collapsible before Accordion; Table before Data Table; Select before Combobox. Escalate only when the simpler one fails.

**State completeness (the variant matrix you must always cover):**
11. Interactive components need at minimum **default / hover / focused / disabled**; inputs add **filled / error / read-only**; async components add **loading / empty / error**; selection components add **selected / indeterminate**. The inventory lists each component's full state set — use it as a build/QA checklist.

---

## 6. Transliterating headless-coded components into Figma

When turning a coded (often headless) component into Figma components, map the four invariant facets the dataset exposes:

1. **States → Figma variant properties.** Each component's *States* list becomes a `State` variant prop (Default/Hover/Focused/Disabled/Error/Loading…). Boolean variants for orthogonal axes (e.g., `hasIcon`, `removable`, `indeterminate`).
2. **Anatomy → layers + slots.** Where the inventory gives an *Anatomy* (Input, Select, Avatar, Accordion, Card), model each part as a named layer or component slot. Use Figma slots/instance-swap for content regions (Card body, Dialog body, Menu items).
3. **Variants → variant axes.** Button → `variant` (primary/secondary/ghost/destructive) × `size` (sm/md/lg). Tabs → `style` (line/pill). Toggle Group → `mode` (single/multi). Badge → semantic color set.
4. **Tokens → Figma variables.** Every `ai_prompt` references design tokens (color, focus ring, radius, spacing, elevation). Bind these to Figma variables, don't hardcode — that's what makes the Figma component a true peer of the code.
5. **Reconcile the name.** Name the Figma component by the **team's system vocabulary** (use §3 / MCP `lookup` to translate), but keep the canonical concept in the description so it's findable. e.g. a Radix `Sheet` becomes the team's "Drawer" with description noting "Sheet/Drawer/Side Panel."
6. **Carry the guidance into the component description.** Paste the *when to use / when to avoid* into the Figma component's description so the contextual intent travels with the component — not just its pixels.

> Operational note: pair this with the `snds:figma-canvas-designer` / `figma-use` skills for the actual canvas writes, and `figma-code-connect` when mapping Figma ↔ code. This framework supplies the *what and why*; those skills supply the *how* in Figma.

---

## 7. Application playbooks

### 7.1 Designing a screen / workflow, screen by screen
1. **Name the user's job** for the screen (the JTBD), then the *primary action* → that's your one primary Button / CTA.
2. **For each piece of data the user provides**, run the Form decision trees (§2.2/2.3) — count options, decide instant vs deferred.
3. **For each piece of data you show**, run §2.7 (List/Table/Data Table/Tree/Timeline/Card).
4. **For transitions and confirmations**, run §2.1 (overlays) and §2.4 (messaging) — keep to the lowest rung.
5. **For multi-step flows**, choose Stepper (input sequence) vs Timeline (status display) vs Progress (single task).
6. **For wayfinding**, run §2.9 and place exactly one primary nav pattern.
7. **Cover every state** (§5 law 11) before calling a screen done — especially empty, loading, and error.

### 7.2 Building a layout
- Group one-subject content into **Cards**; separate sections with **whitespace first, Separator only if needed**.
- Constrain overflow regions with **Scroll Area**; keep page-level scroll native.
- Reserve **Overlays** for genuinely temporary surfaces — don't build primary content into a Popover/Sheet.
- Decide **Tabs vs Accordion** by whether labels should always be visible (Tabs) or content should stack and scan (Accordion).

### 7.3 Auditing / triaging an existing UI
- For each control, ask "is this the *lowest-intensity* correct component?" (§5 law 10). Common smells: Dialog where a Toast suffices; Combobox where a Select suffices; Carousel hiding important content; Switch where a Save-confirm Checkbox belonged; color-only status.
- Check the **state matrix** (§5 law 11) for gaps — missing focus rings, no empty/error states, no loading.
- Check **semantics** (§5 laws 3–4): is the "menu" actually a Select? Is the "toggle" actually a Switch? Are menu vs form-input roles correct?
- Flag **naming drift** against the team's system vocabulary (§3) so the design and code stay legible to each other.

---

## 8. Using the live MCP alongside these docs

These docs are the always-loaded reasoning layer. The **ux-components MCP** is the live, queryable source — reach for it when you need specifics:
- `lookup "<component>"` — full anatomy/states/guidance, or `"what is <x> called in <system>"` for naming.
- `recommend "<plain-language scenario>"` — best component + alternatives + states + watch-outs (great for quick decisions).
- `compare "a vs b vs c"` — side-by-side decision table (regenerate any tree in §2 with current data).
- `lookup "<category> components"` — the full roster for a category.

Prefer the MCP when the answer must be current or exhaustive; prefer these docs for fast reasoning and the synthesized frameworks the MCP doesn't return.
