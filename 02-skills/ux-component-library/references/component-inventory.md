# UX Component Inventory — 62 Components, 9 Categories

> Source: the **UX Components** dataset (ux-components.com) — 62 components, 68 design systems, 1,900+ naming mappings. This file is the static distillation; for live, always-current detail call the MCP tools (`lookup`, `recommend`, `compare`, `smart_query`). See `cross-system-patterns.md` for the synthesis and decision frameworks.

**How to read an entry:** `id` is the canonical kebab-case key for MCP lookups. *Use* = the strongest fit cases. *Avoid* = the failure modes that should push you to a different component. *States* = the variant axes you must cover when building or transliterating. *Aka* = cross-system names worth knowing (only the divergent/surprising ones — most systems just use the canonical name). *Related* = the components to weigh against it.

The nine categories: **Action, Form, Navigation, Feedback, Data Display, Layout, Overlay, Disclosure, Content.**

---

## Action (4)

Components that trigger user-initiated operations and reflect stateful controls.

### Button — `button`
The primary mechanism for user-initiated actions. Label is always a verb/verb-phrase; variants establish hierarchy (primary/secondary/ghost/destructive).
- **Use:** form submit, open dialog/drawer, primary CTA, confirm/cancel, any action that changes state.
- **Avoid:** navigation to a new page (use Link); >1 primary per section; vague labels ("Click here"); disabled without explaining why.
- **States:** Default, Hover, Active/Pressed, Focused, Disabled, Loading.
- **Aka:** "Buttons" (Material, GOV.UK, NHS), "CTA" (Nucleus), "Primary Button" (Canvas).
- **Related:** Toggle, Dropdown Menu, Link.

### Toggle — `toggle`
A *stateful* button that persists its pressed/active state (uses `aria-pressed`). Distinct from Switch.
- **Use:** formatting toolbars (Bold/Italic), view-mode switches (Grid/List), filter chips, layer visibility, mute/show-hide in media.
- **Avoid:** non-stateful actions (use Button); settings outside an active UI context (use Switch); binary form fields (use Switch/Checkbox); >5–6 in a group.
- **States:** Inactive, Active/Pressed, Hover (inactive), Hover (active), Focused, Disabled.
- **Aka:** ⚠️ huge collision — "Switch" (Dell, Spectrum, eBay, PatternFly, Backpack…), "Segmented Control" (Canvas), "Content Switcher" (Carbon), "ToggleButton" (React Aria).
- **Related:** Switch, Button, Toggle Group.

### Toggle Group — `toggle-group`
A connected set of Toggles in single-select (radio-like) or multi-select (additive) mode. Visual shape signals the mode: unified pill ⇒ single, separate buttons ⇒ multi.
- **Use:** view-mode (Day/Week/Month), alignment (L/C/R), size selectors (S/M/L), additive format controls.
- **Avoid:** navigation (use Tabs); >5–6 items; long labels; no default when one is required.
- **States:** One active (single), Multiple active (multi), None active, Item hover/focused/disabled.
- **Aka:** "Segmented Control" (Nord, Calcite, Cloudscape, Vanilla…), "Content Switcher" (Carbon), "Button Group" (many), "Action Group" (Spectrum).
- **Related:** Toggle, Tabs, Radio Group.

### Toolbar — `toolbar`
A horizontal bar grouping contextual actions/tools; uses roving tabindex (`role="toolbar"`, arrow-key nav, single tab stop). Operates *on content*, doesn't navigate.
- **Use:** rich-text/code editors, data-table action bars, design palettes, message action bars.
- **Avoid:** 1–2 actions (standalone buttons); primary navigation; selection-contextual actions (Context Menu).
- **States:** Default, Overflow (collapsed "more" menu), Focused, Disabled.
- **Aka:** "Action Bar" (Canvas), "Filter Bar" (Helios).
- **Related:** Button, Toggle Group, Menubar, Context Menu.

---

## Form (18)

Input and data-collection controls. The largest category — and the one with the most cross-system naming chaos.

### Input — `input`
The fundamental single-line text field. Pairs with Label + hint + inline validation; `type` shapes behavior and mobile keyboard. Validate on blur.
- **Use:** any typed single-line value (name/email/URL/password), search bars, inline title editing.
- **Avoid:** multi-line (Textarea); predefined options (Select/Combobox); placeholder-as-label.
- **States:** Default, Focused, Filled, Disabled, Read-only, Error.
- **Anatomy:** Label, Input field, Placeholder, Hint, Error message.
- **Aka:** "Text Field/Text Input/TextField" (Atlassian, Polaris, Carbon, Spectrum, MUI), "Form Control" (Bootstrap).
- **Related:** Label, Textarea, Combobox.

### Textarea — `textarea`
Multi-line text. Initial height signals expected length; supports auto-grow (set max-height) and char counter (show "remaining").
- **Use:** comments/replies, bio/description, feedback, message composition.
- **Avoid:** single-line (Input); rich formatting (RTE); structured data like addresses (separate fields).
- **States:** Default, Focused, Filled, Disabled, Error, At limit.
- **Aka:** "Text Area/Text Input" (Carbon, Canvas), "Input.TextArea" (Ant).
- **Related:** Input, Label.

### Label — `label`
The accessibility layer of every control (`for`/`id`). Expands click target; placeholder is never a substitute. Mark required with `*` + legend.
- **Use:** every input/select/textarea/checkbox/radio; accessible names for custom controls. Essentially always.
- **Avoid:** placeholder-only labeling; positioning far from control; truncating label text.
- **States:** Default, Required, Optional, Disabled, Error.
- **Aka:** "Form Field" (Canvas, Evergreen), "Field Label" (Spectrum).
- **Related:** Input, Checkbox, Radio Group.

### Checkbox — `checkbox`
Binary/multi-select state that's *submitted with a form* (not instant). Supports indeterminate (select-all). Independent of siblings.
- **Use:** multi-select from a list, single boolean preference, accept terms, bulk-action selection, indeterminate "select all".
- **Avoid:** single selection (Radio); instant-effect toggle (Switch); unlabeled.
- **States:** Unchecked, Checked, Indeterminate, Focused, Disabled, Error.
- **Aka:** "Form Check" (Bootstrap), "Selection controls" (Wanda).
- **Related:** Radio Group, Switch, Label.

### Radio Group — `radio-group`
Mutually exclusive single-choice from a *fully visible* small set (2–5). Arrow keys move selection (not Tab). Pre-select a sensible default.
- **Use:** exclusive 2–5 options, notification frequency, pricing tiers, survey single-answer.
- **Avoid:** >5–6 (Select); multi-select (Checkbox); simple on/off (Switch); no default.
- **States:** Unselected, Selected, Focused, Disabled (selected/unselected), Error.
- **Aka:** "Radio Button(s)/Radio/Radios" — naming varies wildly by pluralization across systems.
- **Related:** Checkbox, Switch, Select.

### Select — `select`
Closed dropdown, choose exactly one from a small known list (≤15). Custom selects must replicate native keyboard (type-ahead, arrows, Enter).
- **Use:** country/state/timezone, fixed category filters, sort order, 5–15 discrete options.
- **Avoid:** >15 (Combobox); 2–3 options (Radio); multi-select (custom); binary (Switch).
- **States:** Default/closed, Open, Option hover, Option selected, Disabled, Error.
- **Anatomy:** Trigger, Placeholder, Dropdown panel, Option items.
- **Aka:** ⚠️ "Picker" (Spectrum), "Listbox" (Anvil), "Dropdown List" (Horizon) — and note Atlassian/PatternFly call their **Combobox** "Select".
- **Related:** Combobox, Radio Group, Dropdown Menu.

### Combobox — `combobox`
Text input + filterable listbox. The answer when Select's list is too long (>15–20) or the user may not know the exact name. Debounce async; always show empty state.
- **Use:** 50+ option selectors, tag search, large user lists, search-ahead, async-fetched options.
- **Avoid:** <8 options (Select); always-known input (Input); many-item multi-select (tag input).
- **States:** Default, Focused/Open, Typing, Loading, Empty, Selected.
- **Aka:** ⚠️ "AutoComplete" (Ant), "Autosuggest" (Backpack, Cloudscape), "Select" (Atlassian, PatternFly, Flowbite), "Super Select" (Helios).
- **Related:** Select, Input, Dropdown Menu.

### Switch — `switch`
Instant-effect binary toggle (`role="switch"`). The sliding-pill metaphor = "live control, not a form field." Label the feature, not the state.
- **Use:** immediately-applied settings (dark mode, notifications), feature toggles, instant binary prefs.
- **Avoid:** changes needing confirm-before-apply (Checkbox+Save); multi-value (Radio/Select); form-submitted fields.
- **States:** Off, On, Focused, Disabled (off/on), Loading.
- **Aka:** ⚠️ "Toggle/Toggle Switch" (Atlassian, Carbon, Nord, Clarity), "Checkbox Toggle" (Lightning, Base Web).
- **Related:** Checkbox, Toggle, Radio Group.

### Slider — `slider`
Pick a numeric value by dragging a thumb; great when *relative position* matters more than the exact number. Supports range (two thumbs). Pair with an Input for precision.
- **Use:** volume/brightness/opacity, price-range filters, image adjustments, zoom.
- **Avoid:** precision needed (Input); huge ranges (0–10,000); binary (Switch); few discrete options (Radio/Select).
- **States:** Default, Hover, Active/Dragging, Focused, Disabled, Range.
- **Aka:** "Range" (Bootstrap, Atlassian, Nord, Flowbite), "Range slider/Range Input" (USWDS, Polaris, Clarity).
- **Related:** Input, Progress, Radio Group.

### Rating — `rating`
Star-based score (usually 1–5), input or read-only. Hover previews in input mode; pair with count in display mode.
- **Use:** product reviews, satisfaction surveys, content quality, quick sentiment.
- **Avoid:** precise numeric input (Slider/Input); binary feedback (thumb up/down); >10-point scales.
- **States:** Empty, Hover, Selected, Half value, Read-only, Disabled.
- **Aka:** "Star Rating" (Backpack, Pando), "Rating Indicator" (Fiori), "Star Meter" (Wanda).
- **Related:** Slider, Input, Toggle.

### File Upload — `file-upload`
Browse-button + drag-drop zone. Communicate accepted types, size limits, per-file progress; specific error text.
- **Use:** documents/images/media, CSV import, message attachments, avatar upload, bulk upload.
- **Avoid:** text/number (Input); live capture (camera); URL only (text input).
- **States:** Default, Drag over, Uploading, Complete, Error, Disabled.
- **Aka:** "Upload" (Ant), "File Uploader" (Carbon, Paste, Base Web), "DropZone" (React Aria), "Upload Collection" (Fiori).
- **Related:** Input, Progress, Button.

### Search — `search`
Specialized input for finding content — magnifier icon, clear button, optional `/` or Cmd+K shortcut. Live / debounced / submit.
- **Use:** app-wide content search, list/table filtering, global search w/ shortcut, in-context (dialog/dropdown) search.
- **Avoid:** <10 items (just scan); only-nav path; structured data entry.
- **States:** Empty, Focused, Active, Loading, Results, No results.
- **Aka:** "Text Filter" (Cloudscape), "Omnibar" (Blueprint), "Search Box/Field/Bar" (varies).
- **Related:** Input, Combobox, Dropdown Menu.

### Number Input — `number-input`
Numeric field with increment/decrement steppers; configurable min/max/step; disable button at boundary.
- **Use:** quantity selectors, numeric thresholds, counts/amounts, precise numeric form fields.
- **Avoid:** very large ranges (text+validate); approximate values (Slider); dates/phones/cards (masked input).
- **States:** Default, Focused, Hover, Disabled, Min reached, Max reached, Error.
- **Aka:** "Input Number" (Ant, Calcite), "SpinButton" (Fluent), "Quantity Picker" (Bolt), "Stepper/Step Input" (Fiori).
- **Related:** Input, Slider, Select.

### Date Picker — `date-picker`
Text input + calendar dropdown for selecting a date (single or range). Locale-aware; keyboard accessible.
- **Use:** booking/reservation, event dates, date-range filters, birth date, deadlines.
- **Avoid:** relative dates ("last 7 days" → Select/Radio); time-only (Time Picker); very narrow range (Select).
- **States:** Default, Open, Hover (day), Selected, Disabled, Error, Range.
- **Aka:** ⚠️ "Date Time Picker" (Atlassian), "Datetime" (SKY UX, Wanda), "Calendar" — note Carbon/Clarity call the **Calendar** a "Date Picker."
- **Related:** Calendar, Input, Time Picker, Popover.

### Time Picker — `time-picker`
Hour/minute (+AM/PM) selection; 12/24h; configurable minute steps.
- **Use:** appointments, alarms/reminders, event start/end times, business hours.
- **Avoid:** date only (Date Picker); duration (number/separate fields); very constrained range (Select).
- **States:** Default, Open, Selected, Focused, Disabled, Error.
- **Aka:** "Date Time Picker" (Atlassian), "Time Field" (Anvil, React Aria).
- **Related:** Date Picker, Input, Select.

### Calendar — `calendar`
Month grid for viewing/selecting dates; often the popover content inside a Date Picker, or embedded inline (booking). Rich day-cell states; full keyboard nav. Pair with a text input fallback.
- **Use:** booking/scheduling, date-range selection, inline date pickers, event/availability views.
- **Avoid:** known exact date (text input); time selection (Time Picker); month/year only (selects).
- **States:** Default, Selected, Range start/end, In range, Today, Disabled.
- **Aka:** "Date Picker(s)" (Material, Carbon, Clarity, Paste), "Date input" (GOV.UK).
- **Related:** Input, Select, Popover.

### Color Picker — `color-picker`
Saturation/brightness panel + hue (+alpha) slider + hex input + presets; eyedropper where supported.
- **Use:** theme customization, design tools, branding panels, chart color assignment.
- **Avoid:** few preset colors (Select/Radio swatches); non-visual context; mobile precision (offer presets).
- **States:** Default, Open, Hover, Selected, Disabled.
- **Aka:** "ColorPicker" (Fluent, Vibe, Instructure). Only ~7 systems model it — niche.
- **Related:** Input, Slider, Popover, Select.

### Form — `form`
Container that groups inputs, manages validation, handles submission. Announce errors via `aria-live`.
- **Use:** login/registration, checkout/payment, settings/profile, search-filter panels, multi-step wizards.
- **Avoid:** read-only display (detail view); single input (input+button); independent non-submitted inputs.
- **States:** Default, Validating, Error, Submitting, Submitted, Disabled.
- **Aka:** "FormGroup" (Blueprint), "Form Field" (Canvas).
- **Related:** Input, Select, Checkbox, Radio Group, Button.

---

## Navigation (9)

Wayfinding and command-access. Distinguish *navigate-between-pages* from *trigger-actions*.

### Link — `link`
The web's navigation primitive — *navigates*, doesn't act. Screen readers announce links ≠ buttons. Descriptive text, not "click here."
- **Use:** page/section navigation, external resources, inline references, footer/legal.
- **Avoid:** state-changing actions (Button); vague text; button-styled when it navigates; triggering modals/dropdowns.
- **States:** Default, Hover, Visited, Focused, Disabled.
- **Aka:** "Anchor" (Paste, Garden), "Text Link" (Pando), "CTA Link" (Protocol).
- **Related:** Button, Breadcrumb, Navigation Menu.

### Breadcrumb — `breadcrumb`
Shows the path from root to current page; secondary aid, complements primary nav. Collapse long paths with ellipsis. (`aria-current="page"` on last.)
- **Use:** deep hierarchies (e-commerce/docs/files), admin dashboards, category sites, pages >2 levels deep.
- **Avoid:** flat sites (1–2 levels), SPAs on one level, as primary nav.
- **States:** Default, Current page, Hover, Collapsed, Focused.
- **Aka:** "Breadcrumbs" (pluralized in many), "BreadcrumbsBar" (Vibe).
- **Related:** Pagination, Tabs.

### Tabs — `tabs`
Switch between *parallel* content views sharing one region; all labels visible, one panel at a time. URL-link tabs used for page-level nav.
- **Use:** related views (Overview/Analytics/Settings), product page sections, profile sections, editor modes.
- **Avoid:** cross-tab comparison; >5–7 tabs; sequential steps (Stepper); nested tabs.
- **States:** Active, Inactive, Hover, Focused, Disabled.
- **Aka:** "Tab/Tablist" (Fluent), "Nav Tabs" (Bootstrap); line vs pill are the two visual variants.
- **Related:** Accordion, Collapsible, Separator.

### Pagination — `pagination`
Breaks a large dataset into numbered pages; prev/next, first/last, ellipsis for long ranges. Reflect current page in URL. Page-size control is a good complement.
- **Use:** search results, product listings, admin tables, content archives, perf-bound large sets.
- **Avoid:** infinite-scroll UX (feeds/galleries), <20 items, Load More patterns.
- **States:** Default, Active/Current, Hover, Disabled (boundaries), Ellipsis.
- **Aka:** "Paginator" (Lucid), "Paging" (SKY UX).
- **Related:** Table, Select.

### Dropdown Menu — `dropdown-menu`
Button-triggered floating list of *actions/navigation* (menu/menuitem roles). NOT a form input — that's Select. Closes on select/outside/Escape.
- **Use:** row-action menus (edit/duplicate/delete), account menu, "..." overflow, grouped nav links, sort/filter controls.
- **Avoid:** 1–2 actions (buttons); value selection (Select/Combobox); >2 submenu levels; right-click context (Context Menu).
- **States:** Closed, Open, Item hover, Item focused, Item disabled, Sub-menu open.
- **Aka:** ⚠️ "Menu" (Fluent, Chakra, Radix-adjacent), "Action menu/list" (Dell, Polaris), "Kebab Menu" (Crayons), "OverflowMenu" (Braid).
- **Related:** Context Menu, Select, Combobox.

### Context Menu — `context-menu`
Right-click / long-press menu at the pointer. Power-user affordance; must mirror actions available elsewhere (never the only path). Populate dynamically.
- **Use:** file/item management, text-editor actions, canvas/design ops, table row actions.
- **Avoid:** sole access to critical actions; touch-only devices; toolbar-belonging actions; >5–7 items.
- **States:** Hidden, Open, Item hover, Item disabled, Sub-menu open.
- **Aka:** "Overflow Menu" (Carbon), "Action Menu" (Spectrum), often just "Menu/Dropdown."
- **Related:** Dropdown Menu, Popover, Tooltip.

### Menubar — `menubar`
Classic desktop File/Edit/View bar; hover-follow between triggers; right-aligned shortcuts. For tool-heavy desktop-class apps.
- **Use:** editors/IDEs/design tools/spreadsheets, command-rich apps, shortcut discoverability.
- **Avoid:** simple sites (Navigation Menu); mobile/touch; 2–3 actions; site-level nav (Tabs/navbar).
- **States:** Default, Open, Hover-follow, Item highlighted, Submenu open, Disabled item.
- **Aka:** "Top Nav/Top App Bar" (Spectrum, Canvas), "Main Nav" (GOLD), "Header Navigation" (Base Web).
- **Related:** Dropdown Menu, Context Menu, Tabs.

### Navigation Menu — `navigation-menu`
Primary site/app nav (often header), top-level links + mega-menu dropdowns. Collapses to hamburger on mobile. Wayfinding, not commands.
- **Use:** primary site nav, doc hubs, marketing site sections, large apps with feature areas.
- **Avoid:** in-page switching (Tabs); app commands (Menubar); 2–3 destinations (Links); deep hierarchies (Sidebar).
- **States:** Default, Hover, Active/Current, Dropdown open, Mobile collapsed.
- **Aka:** ⚠️ very fragmented — "Sidebar/Sidenav/Side Navigation" (many), "Navbar" (Bootstrap), "UI Shell" (Carbon), "Nav" (Fluent).
- **Related:** Tabs, Breadcrumb, Menubar, Dropdown Menu.

### Stepper — `stepper`
Position indicator for a *sequential* multi-step process; completed/current/upcoming/error nodes; horizontal or vertical; 3–7 steps.
- **Use:** multi-step forms (checkout/registration), onboarding, config wizards, order tracking.
- **Avoid:** non-sequential nav (Tabs); >7 steps; single-task progress (Progress); 2-step flows.
- **States:** Completed, Current, Upcoming, Error, Disabled.
- **Aka:** ⚠️ "Steps" (Ant), "Progress stepper/indicator" (PatternFly, USWDS, Lightning), "Wizard" (Cloudscape, Fiori).
- **Related:** Progress, Tabs, Pagination.

---

## Feedback (8)

System status, loading, and messaging. The cluster with the most "which one?" confusion (see decision frameworks).

### Alert — `alert`
Static, inline, *persistent* message in the document flow; semantic variants (info/success/warning/error). `role="alert"`/`aria-live`.
- **Use:** form validation summaries, system status notices, permission/access warnings, contextual info within a workflow.
- **Avoid:** ephemeral confirms (Toast); decisions required (Alert Dialog); stacking many; marketing.
- **States:** Info, Success, Warning, Error, Dismissible.
- **Aka:** ⚠️ "Banner" (Canvas, Polaris, Cedar), "Section message" (Atlassian), "Inline Message" (NewsKit), "Message bar" (Fluent, Dell), "Callout" (Elastic).
- **Related:** Toast, Alert Dialog, Badge.

### Toast — `toast`
Ephemeral, auto-dismissing notification in a viewport corner (3–5s). Non-critical only. Pause on hover; stack ≤3; optional Undo.
- **Use:** background save confirms, action results (deleted/sent/uploaded), non-blocking errors, undo windows.
- **Avoid:** critical errors needing acknowledgment (Alert/Dialog); detailed reading; >3 stacked; permanent notices.
- **States:** Entering, Visible, Hovered/Paused, Exiting, Success, Error.
- **Aka:** ⚠️ "Snackbar" (Material, eBay, Wanda), "Flag" (Atlassian), "Flashbar" (Cloudscape), "Notification" (Carbon, Dell), "Message" (Ant).
- **Related:** Alert, Dialog, Progress.

### Banner — `banner`
Prominent full-width, page/section-level message; persists until resolved/dismissed. Severity variants.
- **Use:** system-wide announcements (maintenance), cookie/privacy notices, feature launches, trial/subscription status.
- **Avoid:** field-level feedback (form validation); temporary (Toast); blocking decisions (Alert Dialog); stacking.
- **States:** Info, Success, Warning, Error, Dismissed.
- **Aka:** "Message" (Semantic, Orbit), "Announcement Banner" (ONS), "Alert Banner" (Spectrum, Horizon), "Callout" (Mística). (Overlaps heavily with Alert across systems.)
- **Related:** Alert, Toast, Alert Dialog.

### Progress — `progress`
Determinate completion 0–100% (`role="progressbar"`). Reduces perceived wait; segmented for multi-step. Has an indeterminate fallback mode.
- **Use:** file up/download, multi-step completion, profile completeness, measurable task status.
- **Avoid:** unknown duration (Spinner/Skeleton); <300ms ops; fake progress.
- **States:** Empty (0%), In progress, Complete (100%), Indeterminate, Error.
- **Aka:** "Progress Bar/ProgressBar" (most), "Progress Circle" (Spectrum), "Linear Progress" (Wanda).
- **Related:** Skeleton, Toast.

### Spinner — `spinner`
Indeterminate "something is happening." Appear within ~300ms; switch to Progress for long ops; don't overuse.
- **Use:** button loading, inline card/list loading, page-level overlays, async placeholders.
- **Avoid:** known duration (Progress); initial page load (Skeleton); <300ms ops; stacking many.
- **States:** Spinning, With label, Small/Inline, Overlay.
- **Aka:** ⚠️ "Loader/Loading/Loading Indicator" (many), "Progress Circle" (Spectrum), "Busy Indicator" (Fiori).
- **Related:** Progress, Skeleton, Button.

### Skeleton — `skeleton`
Low-fidelity wireframe placeholder matching the incoming layout; shimmer/pulse. Best perceived-perf for initial loads; prevents layout shift. Time out to an error state.
- **Use:** page loads with substantial content (feeds/dashboards), image/card grids, table rows, UGC.
- **Avoid:** <300ms ops; unknown final layout; persistent state; small inline elements.
- **States:** Loading, Loaded, Error.
- **Aka:** "Placeholder" (Semantic, Bootstrap), "Skeleton Loader" (Paste, LeafyGreen).
- **Related:** Progress, Card, Avatar.

### Empty (Empty State) — `empty-state`
What users see when there's no content — explains *why* and *what next*. Distinct from loading.
- **Use:** empty list/table/grid, zero search results, first-run, load failure, unconfigured feature.
- **Avoid:** while loading (Skeleton/Spinner); seconds-long transient states; filter-hidden content (filter-specific message); as a permanent landing.
- **States:** No data, No results, Error, First use.
- **Aka:** "Empty Prompt" (Elastic), "Info state" (Wanda). Canonical id is `empty-state`; dataset display name is "Empty."
- **Related:** Skeleton, Spinner, Card.

### Meter — `meter`
Static scalar gauge within a known range (threshold colors), NOT task completion. (HTML `<meter>` semantics: min/max/value/low/high/optimum.)
- **Use:** disk/storage usage, password strength, battery/signal, quota consumption, health scores.
- **Avoid:** task completion (Progress); unknown/infinite range; precise entry (Slider/Number Input); rapidly-changing values.
- **States:** Low, Medium, High, Full.
- **Aka:** "Metric" (Instructure), "Radial Micro Chart" (Fiori), "Gauge Visualization" (Horizon). Only ~10 systems model it.
- **Related:** Progress, Slider, Badge.

---

## Data Display (9)

Presenting records, entities, and metadata.

### Avatar — `avatar`
Visual identity (photo → initials → icon fallback). Sizes; group/stacked cluster with overflow count; optional status dot. Never expose a broken image.
- **Use:** profiles in headers/sidebars, comment threads, assignees, mention chips, member lists.
- **Avoid:** irrelevant identity; no fallback handling; <20px for primary ID; substitute for a full profile card.
- **States:** Image loaded, Fallback initials, Fallback icon, Loading, Group/stacked, With indicator.
- **Anatomy:** Image, Fallback, Size variants, Avatar Group.
- **Aka:** mostly "Avatar"/"Avatars" — rare divergence.
- **Related:** Badge, Tooltip, Hover Card.

### Badge — `badge`
Compact indicator of count/status/category that *annotates another element*. Never color alone; cap counts (99+); 1–3 words.
- **Use:** status labels (Active/Draft), notification counts, category labels, feature flags (New/Beta), role indicators.
- **Avoid:** long text; primary CTA (Button); color-only meaning; many badges on one item; binary true/false (icon).
- **States:** Default, Outline, Success, Warning, Danger.
- **Aka:** ⚠️ "Tag" (Carbon, USWDS, GOV.UK), "Pill" (Instructure), "Counter/CounterLabel" (Vibe, Primer), "StatusLabel" (Helsinki).
- **Related:** Label, Avatar, Toggle.

### Tag — `tag`
Compact, often *interactive/removable* label carrying textual meaning (keywords, filters, metadata). Distinct from numeric Badge.
- **Use:** keyword/topic categorization, removable selected filters, status/type metadata, multi-value tagging.
- **Avoid:** numeric counts/status dots (Badge); full sentences; navigation (Tabs/Links); >10–15 (other pattern).
- **States:** Default, Hover, Focused, Disabled, Removable.
- **Aka:** ⚠️ "Pill" (Nucleus, Pharos), "Token" (Cloudscape, Fiori, Primer, Seeds), "Chip" (Backpack), "Badge" (Flowbite).
- **Related:** Badge, Toggle Group, Input.

### Chip — `chip`
Compact *interactive* element representing an input/attribute/action — selectable and/or removable; composable in wrapping groups (Backspace removes).
- **Use:** removable selected filters, tokenized email/user inputs, category selectors, multi-select pills, action chips.
- **Avoid:** static non-interactive labels (Badge/Tag); navigation; single option (Toggle/Checkbox); long content.
- **States:** Default, Selected, Hover, Focused, Disabled.
- **Aka:** "Tag" (Fluent, Ant, Chakra), "Token" (Seeds), "Chips" (Vibe, Vanilla). ⚠️ Tag/Chip/Token are used interchangeably across systems.
- **Related:** Tag, Badge, Toggle Group, Combobox.

### List — `list`
Vertical arrangement of related items with consistent spacing/structure. One meaningful "column" of content per row.
- **Use:** settings menus with labeled options, contact/user lists with avatars, simple item collections.
- **Avoid:** tabular multi-column data (Table/Data Table); deep hierarchy (Tree).
- **States:** Default, Hover, Selected, Focused, Empty, Loading.
- **Aka:** "Structured List" (NewsKit/Carbon-style), varies; many systems fold this into Table or bespoke list items.
- **Related:** Table, Card, Tree View.

### Table — `table`
Two-dimensional grid where *cross-column relationships matter*. Sortable headers, row selection, sticky header, per-row actions; semantic `thead/tbody/th[scope]`, `aria-sort`.
- **Use:** admin record lists, data comparison/feature matrices, logs/transactions, bulk multi-row ops.
- **Avoid:** single meaningful column (List); deep hierarchy (Tree); awkward mobile collapse; 1–3 rows (cards).
- **States:** Default, Row hover, Row selected, Sorted, Loading, Empty.
- **Aka:** "Data Table/DataTable" (Carbon, Lightning, Base Web), "Dynamic table" (Atlassian), "Structured List" (NewsKit).
- **Related:** Pagination, Badge, Checkbox.

### Data Table — `data-table`
Feature-rich Table: sorting + filtering + pagination + selection + resizing + sticky headers + toolbar. For complex datasets.
- **Use:** admin dashboards, analytics/reporting, CRM/ERP records, log viewers, sort/filter/bulk needs.
- **Avoid:** small static datasets (Table); chart-better data; many-column mobile (card list); layout (CSS grid).
- **States:** Default, Sorted, Filtered, Row selected, Loading, Empty, Error.
- **Aka:** "Dynamic Table" (Atlassian), "Data Grid" (Pando), "Advanced Table" (Helios). Only ~11 systems separate this from Table.
- **Related:** Table, Pagination, Checkbox, Search.

### Tree View — `tree-view`
Hierarchical nested parent/child nodes, expand/collapse, indentation for depth; full keyboard nav; optional multi-select checkboxes; async children.
- **Use:** file/folder browsers, nested nav (doc sidebars), org charts/category hierarchies, permission groups, dependency trees.
- **Avoid:** flat lists (List); only 2 levels (Accordion/grouped list); mobile deep nesting; cross-branch comparison.
- **States:** Collapsed, Expanded, Selected, Focused, Disabled, Loading.
- **Aka:** "Tree" (Ant, Fluent, Calcite, Fiori, Blueprint), "TreeBrowser" (Instructure). Only ~13 systems model it.
- **Related:** Accordion, Navigation Menu, List.

### Timeline — `timeline`
Chronological events along a line (vertical/horizontal); node + content + timestamp; completed/active/pending. *Display*, not input.
- **Use:** activity logs/audit trails, order/shipment tracking, milestones/roadmaps, version history/changelogs.
- **Avoid:** step-by-step with input (Stepper); non-chronological data (List/Card); 2–3 items; real-time streams (feed).
- **States:** Default, Active, Completed, Pending, Loading.
- **Aka:** uniformly "Timeline" — only ~9 systems model it.
- **Related:** Stepper, List, Progress.

---

## Layout (3)

Structural containers and dividers.

### Card — `card`
Bounded surface grouping content + actions about *one subject* (header/body/footer). Elevation via bg/border/shadow. Interactive cards must be keyboard-accessible; mind nested click targets.
- **Use:** product/item listings, dashboard widgets, profiles, post previews, grouped settings panels.
- **Avoid:** no separation needed (List); nesting cards >1 deep; very long content (page); making everything a card; shadow implying interactivity without a real trigger.
- **States:** Default, Hover, Selected, Loading, Empty.
- **Aka:** "Tile" (Carbon), "Content/Context Card" (Vibe, Geist, Visa).
- **Related:** Separator, Skeleton, Badge.

### Separator — `separator`
Thin presentational divider (horizontal/vertical/labeled). Does real cognitive work but use sparingly — prefer whitespace. `role="separator"` when structural, `presentation` when decorative.
- **Use:** menu/sidebar section dividers, form section groups, footer columns, "or" auth divider, card header/body split.
- **Avoid:** overuse (visual noise); substitute for margin; decorative without grouping purpose; vertical rules that break responsively.
- **States:** Horizontal, Vertical, Labeled.
- **Aka:** ⚠️ "Divider" (Material-style, Fluent, Ant, Chakra, Spectrum, Polaris — the most common name), "HR/Horizontal Rule" (Bootstrap, Flowbite), "Scrim" (Calcite).
- **Related:** Card, Accordion, Tabs.

### Scroll Area — `scroll-area`
Custom-styled scrollbar over native scroll mechanics (consistent cross-OS). Auto-hide but always indicate scrollability. Only styling is custom — scrolling stays native/accessible.
- **Use:** sidebars/nav panels, fixed-height containers (code/chat), bounded tables, modal/drawer long content.
- **Avoid:** hiding scrollbars on touch; wrapping the whole page; no overflow; ultra-thin un-targetable bars.
- **States:** Idle, Scrolling, Scrollbar hover, Scrollbar dragging, At boundary.
- **Aka:** "Affix" (Ant), "Scrollable" (Polaris), "ScrollBox" (DRUIDS). Only ~7 systems model it (mostly Radix-lineage).
- **Related:** Table, Sheet.

---

## Overlay (6)

Floating/modal surfaces. The defining axis is **modality** (focus trap + backdrop block) and **trigger** (click vs hover). See the overlay decision tree.

### Tooltip — `tooltip`
Tiny plain-text label on hover/focus; transient & expendable; **never interactive**, **never critical**. `role="tooltip"` + `aria-describedby`. Open delay 400–600ms. Primary tool for naming icon-only buttons.
- **Use:** icon-button labels, clarifying truncated/abbreviated text, shortcut hints, explaining disabled state, expanding acronyms.
- **Avoid:** interactive content (Popover); essential info; touch-only; >1 sentence; attaching to non-interactive text.
- **States:** Hidden, Delayed open, Visible, Closing.
- **Aka:** "Tip" (Grommet, Gamut), "Tipseen" (Vibe); note USWDS/Lightning/Duet call **Popover** a "Tooltip."
- **Related:** Popover, Hover Card, Button.

### Hover Card — `hover-card`
Rich preview on hover (300–500ms delay + close grace period). Desktop-only — must have a tap/click fallback. Never put critical actions inside.
- **Use:** user-mention previews, link previews, item references, ticker/asset quick views, richer-than-tooltip context.
- **Avoid:** touch devices; critical info; content needing interaction (Popover); validation feedback; tiny hover targets.
- **States:** Hidden, Delayed open, Open, Closing.
- **Aka:** "Signpost" (Clarity), "Hovercard" (Ariakit), "Contact card" (Horizon). Only ~6 systems model it (Radix-lineage).
- **Related:** Tooltip, Popover, Avatar.

### Popover — `popover`
Non-modal floating panel anchored to a trigger; rich content (forms/lists/buttons); does NOT trap focus or block background; auto-positions with collision flip. Dismiss on outside-click/Escape.
- **Use:** color/date/emoji pickers, contextual filters/sorting, inline field editing, add-tag/assign-member, interactive help.
- **Avoid:** simple text (Tooltip); focused critical flows (Dialog); nested popovers; small screens (clipping); irreversible actions.
- **States:** Closed, Open, Repositioned, Focused within, Closing.
- **Aka:** ⚠️ "Popup" (Semantic, Canvas, Atlassian), "Popout" (Nord, Seeds), "Coach Mark" (Pharos); some systems call it "Tooltip."
- **Related:** Tooltip, Hover Card, Dialog.

### Dialog — `dialog`
Modal window over content for a focused, bounded task; traps focus, locks scroll, Escape dismisses, returns focus to trigger. `role="dialog"` + `aria-modal`. Long content → scrollable body.
- **Use:** create/edit forms keeping page context, expanded detail, 2–3 step wizards, quick share/invite/config, media lightboxes.
- **Avoid:** complex long forms (page); no action needed (Drawer/Sheet); nested dialogs; full-page content; auto-open w/o trigger.
- **States:** Closed, Open, Submitting, Error, Scroll locked.
- **Aka:** ⚠️ "Modal" (the single most common name — Bootstrap, Ant, Carbon, Polaris, many), "Modal dialog" (Atlassian), "Layer" (Grommet).
- **Related:** Alert Dialog, Sheet, Popover.

### Alert Dialog — `alert-dialog`
Modal specifically for *destructive/irreversible* decisions — confirm/cancel, focus-trapped, blocking. Destructive confirm often red; cancel is the safe prominent path. Don't overuse (dialog fatigue).
- **Use:** permanent deletions, irreversible publish/send, significant side effects, security-sensitive ops, blocking error acknowledgment.
- **Avoid:** routine/reversible actions; toast-sufficient confirms; form input collection (Dialog); informational only (Alert).
- **States:** Open, Confirming, Closed, Confirm disabled (type-to-confirm), Error.
- **Aka:** ⚠️ collapses into "Modal/Dialog" in most systems; "Modal confirm" (Ant), "AlertDialog" (HeroUI). Only ~21 systems treat it as distinct from Dialog.
- **Related:** Dialog, Alert, Sheet.

### Sheet — `sheet`
Panel sliding from a screen edge (L/R/T/B) overlaying content; keeps spatial context. Right-side = desktop detail/settings; bottom = mobile standard. Focus-trap when backdrop blocks; multiple exit paths.
- **Use:** list-item detail panels, filter controls for large datasets, mobile nav menus, cart/checkout side panels, complementary settings.
- **Avoid:** simple confirms (Alert Dialog); page-worthy complex forms; bottom sheets >80% height; primary desktop nav; many sub-levels.
- **States:** Closed, Opening, Open, Scrolled, Closing.
- **Aka:** ⚠️ "Drawer" (the most common alt — Fluent, Ant, Chakra, Atlassian, many), "Offcanvas" (Bootstrap), "Side Panel" (Canvas, Clarity, Paste), "Tray" (Spectrum), "Flyout" (Elastic, Helios), "Bottom Sheet" (Backpack).
- **Related:** Dialog, Alert Dialog, Scroll Area.

---

## Disclosure (2)

Show/hide content primitives.

### Accordion — `accordion`
Vertically stacked collapsible sections under labeled headers (chevron). Exclusive (one-open) or multi-open. Keeps long pages compact; trade-off is discoverability.
- **Use:** FAQs, grouped settings panels, nested sidebar nav, product detail sections (specs/shipping/returns), space-limited mobile.
- **Avoid:** simultaneous comparison; always-critical info; 1–2 items; very short content; multi-step forms needing prior context.
- **States:** Collapsed, Expanded, Focused, Disabled, Loading.
- **Anatomy:** Container, Trigger, Indicator, Content Panel.
- **Aka:** ⚠️ "Collapse" (Ant, Aurora, Blueprint), "Disclosure" (Paste), "Expandable Section" (Cloudscape), "Expansion Panel" (Finastra), "Details" (Primer).
- **Related:** Collapsible, Tabs, Separator.

### Collapsible — `collapsible`
The single-section primitive (no stacked list). Externally controllable open state (good for persistence/sync). Composable building block.
- **Use:** "Advanced options," expandable table preview rows, read-more truncation, optional config panels, disclosure without a list.
- **Avoid:** multiple related sections (Accordion); always-visible critical info; very short content; navigation; hiding errors/warnings.
- **States:** Closed, Open, Focused, Disabled.
- **Aka:** "Collapse" (Ant, Bootstrap), "Expander" (NHS, Nucleus), "Details" (ONS, GOV.UK, Anvil), "Disclosure" (Paste, Ariakit, HeroUI), "Show/Hide" (Chakra).
- **Related:** Accordion, Sheet, Dialog.

---

## Content (3)

Media and symbolic content.

### Carousel — `carousel`
Horizontally scrollable cycling panels (arrows + dots + optional autoplay; scroll-snap; swipe). ⚠️ Engagement drops sharply after slide 1 — use only for truly sequential/equivalent content.
- **Use:** product image galleries, hero/promo content, testimonials, onboarding flows, space-limited media.
- **Avoid:** items of differing importance; critical must-see content; navigation (Tabs/Nav Menu); only 2 items; mobile swipe/scroll conflicts.
- **States:** Default, Navigating, Auto-playing, Paused, Dragging.
- **Aka:** "Carousels" (Mística), "Video" (Protocol). Only ~23 systems model it.
- **Related:** Card, Tabs, Pagination.

### Image — `image`
Responsive, accessible image with srcset, lazy loading, loading placeholder (skeleton/blur-up), error fallback, optional caption, aspect-ratio constraints. Alt text required.
- **Use:** product photos, UGC galleries, hero images/banners, card/list thumbnails, avatar images w/ fallback.
- **Avoid:** decorative backgrounds (CSS bg); icons/simple graphics (SVG/Icon); ornamental (`role="presentation"`); complex media (Video/Carousel).
- **States:** Loading, Loaded, Error, Lazy.
- **Aka:** "Images" (Vanilla, Aurora). Only ~11 systems model it as a component.
- **Related:** Avatar, Card, Carousel.

### Icon — `icon`
SVG symbol for communication/labeling/wayfinding; size scale + color theming; interactive (button-like) or decorative (`aria-hidden`). Always provide a text alternative.
- **Use:** button/nav labels, status indicators, form prefixes/suffixes, empty-state illustration, category/wayfinding.
- **Avoid:** sole means of communication; ambiguous meaning w/o context; tiny detail-loss sizes; when a text label is clearer.
- **States:** Default, Hover, Active, Disabled.
- **Aka:** "Icons" (Skyline, Uniform, Vanilla). The dataset's common icon set is Lucide-style (`home, menu, search, chevron-*, arrow-*, check, x, alert-*, trash-2, …`).
- **Related:** Button, Badge, Avatar.

---

## Quick category counts

| Category | Count | Components |
|---|---|---|
| Action | 4 | button, toggle, toggle-group, toolbar |
| Form | 18 | input, textarea, label, checkbox, radio-group, select, combobox, switch, slider, rating, file-upload, search, number-input, date-picker, time-picker, calendar, color-picker, form |
| Navigation | 9 | link, breadcrumb, tabs, pagination, dropdown-menu, context-menu, menubar, navigation-menu, stepper |
| Feedback | 8 | alert, toast, banner, progress, spinner, skeleton, empty-state, meter |
| Data Display | 9 | avatar, badge, tag, chip, list, table, data-table, tree-view, timeline |
| Layout | 3 | card, separator, scroll-area |
| Overlay | 6 | tooltip, hover-card, popover, dialog, alert-dialog, sheet |
| Disclosure | 2 | accordion, collapsible |
| Content | 3 | carousel, image, icon |

**Not modeled** (commonly expected but absent from the dataset): Command/Command Palette, Aspect Ratio, Resizable panels, dedicated Drawer (= Sheet), dedicated Multi-select (= Combobox/Chip pattern), Video (folded into Carousel/Image), KBD, Code block. When asked for these, compose from the nearest modeled primitive and note the gap.
