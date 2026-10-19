---
title: Fontface — library layouts, font page, family grouping, filters and sources: design and build plan
type: note
project: 25-fontface
created: 2026-10-18
status: plan, three questions for Sean
source: read-only design workflow in the Fontface Claude Code session (repo main @ 826c574); Typeface screenshots used as a feature list only
---
# Fontface plan: library layouts, font page, family grouping, filters and sources

## 1. What Fontface will do after this work

All seven requests fit Fontface's current structure. Most of the work is in the interface, and the Rust core needs only small additions. Splits are caused by font names, not folders: grouping already runs once over the whole library (`src/App.tsx:767`).

- **Three layouts.** The library can show as **Tiles** (a grid of cards), **Rows** (today's list) or **Table** (sortable columns). You switch with a toolbar control or ⌘1, ⌘2 and ⌘3. Rows stays the default.
- **Fonts open in the main area.** Opening a family replaces the list with a full **font page**, and the right-side detail panel goes away. A Back button sits at the left of the top row. Back (or ⌘[) returns to the same list, at the same scroll position, with the same row selected.
- **One "View options" popover.** It holds sorting, "Group styles into families", table density and, later, preview styling. Compare, Pair and quick tags are reached from:
  - the right-click menu
  - the selection bar
  - the font page
  - new View and Font menus on macOS
- **Clear on/off states.** Each font shows one of these:
  - on, off or partly on
  - on until logout
  - set to turn on but its file isn't available
  - turned on by another app
  - locked

  Locks say why: "Part of macOS" or "Installed".
- **Families grouped by name, wherever the files are.** "AmintaBold", "Aaux ProBold" and "Abhaya Libre ExtraBold" become styles of Aminta, Aaux Pro and Abhaya Libre.
  - Strong matches merge on their own.
  - Weaker matches become suggestions that you accept or reject on a Family groups page.
  - Your choices are stored by font identity and never change a font file.
- **Smart entries at the top of the sidebar.** These are All Fonts, Your Fonts, Recently Added, Active and Not Tagged, each with a count.
- **One flat Sources section.** It holds Font Book, Google Fonts, Adobe Fonts, Purchases and your folders, one row each, with no chevrons and no subfolder trees. Subfolders move into a small picker on that source's own view.

**Clean-room note.** Fontface keeps its own look: shadcn on Base UI, Material Symbols, IBM Plex and its seamless title bar. The names in this plan are Fontface's own: Tiles, Rows, Table, font page, Specimen, Characters, OpenType, Axes, Info, Family groups, Your Fonts, Not Tagged, and Turn On Until Logout. Several of them reuse headings Fontface already has (`src/components/DetailPanel.tsx:66, 193, 220, 248, 254`). The screenshots were used only as a list of features.

**Going further than Typeface.** Typeface itself does not merge "Abhaya Libre ExtraBold" into "Abhaya Libre". Its table shows four separate Abhaya rows (screenshot 20). This plan goes further, as you asked.

---

## 2. How the app is organized

### 2.1 Sidebar

```
[window buttons strip]
LIBRARY
  All Fonts
  Your Fonts
  Recently Added
  Active
  Not Tagged
SOURCES                          [+ add folder]
  Font Book
  Google Fonts
  Adobe Fonts
  Purchases            n new
  <your folders, A–Z>
TAGS                             [+]
  My tags …
  Built-in …
[scan progress]  [Settings]
```

| Entry | What it shows | Built from |
|---|---|---|
| All Fonts | Every font. It still follows "Show installed fonts in All Fonts". | Exists (`src/library.ts:198`) |
| Your Fonts | Fonts with at least one copy outside the three macOS font folders: your folders, Google Fonts and Purchases. About 10,295 faces (individual styles). | `!onlyInOsFolders` (`library.ts:80`) |
| Recently Added | Fonts added in the last 30 days, newest first. | New `addedAt` field (section 6) |
| Active | Fonts that are on now, leaving out the always-on macOS fonts. | `face.active && !face.installed` |
| Not Tagged | Fonts with none of your own tags. Built-in tags (from Font Book and Typeface) don't count. | Tag index (`src/tags/model.ts:60-127`) |

- There is no separate "macOS" entry. The Font Book source already lists those fonts, and its subfolder picker narrows to the ones that are part of macOS. A separate entry would be one line if you want it.
- Each smart entry gets an on/off row in Settings › Sidebar. All Fonts and your folders stay always shown, as today (`src/settings/sections.tsx:305`).

### 2.2 Main area

The main area has two layers.

- **List layer.** This is the place picked in the sidebar. Its top row is the toolbar, and its body is Tiles, Rows or Table.
- **Page layer.** Pages are pushed on top of the list. Each page's top row has a page header with Back. The pages are:
  - the font page
  - Compare
  - Pair
  - Family groups
  - the Google Fonts and Purchases catalogs, when opened from their source view

While a page is showing, the list stays loaded underneath, hidden and `inert` (it can't be clicked or focused). Settings already works this way (`App.tsx:841-845`). So the list keeps its scroll position, its selection and the previews it has already loaded.

Adobe Fonts keeps opening its own page directly. Its fonts aren't in the library list, because Creative Cloud files are never read (`src-tauri/src/preview/mod.rs:18-23`).

### 2.3 Navigation and Back

- **State.** App state holds the `place` (today's `view` and filters) and a stack of pages, `pages: Page[]`.
- **Page entries.** Each kind remembers its own state:
  - font page: face key, chosen style, tab, axis values and scroll
  - Compare: face keys and mode
  - Pair: the two fonts
  - Family groups: filter and focus
  - catalog: Google or Purchases
- **Back.** These all close the top page:
  - the Back button
  - ⌘[ (Alt+Left on Windows)
  - the mouse's back button
  - Esc, when focus is not in a text field, menu or popover
- **Sidebar clicks.** Clicking any sidebar entry replaces the place and clears the page stack. Back never steps through earlier sidebar places, so it stays predictable.
- **Regrouping.** A font page finds its family by the face key that opened it, not by the family name. So the page survives regrouping.
- **Focus.** When a page opens, focus moves to its heading and the opening is announced. On Back, focus returns to the row or card that opened it, and "Back to <place>" is announced in the existing live region (`App.tsx:1026-1028`).
- **Launch.** "Open where you left off" restores the place only, not pages (`src/settings/lastView.ts:98-131`).

### 2.4 The top row

On macOS, the 52px top row is also the window's title bar (`src/components/TitleBar.tsx:6-12`), and it stays that way.

- **On the list**, left to right:
  - status filter (All / Active / Inactive) and Variable
  - Search and preview text
  - size slider
  - subfolder picker (on source views only)
  - View options (`tune` icon)
  - layout switch (`grid_view`, `view_agenda`, `table_rows`)
  - count

  Under about 760px, the layout switch folds into View options. The toolbar already drops controls in steps as it narrows (`src/components/Toolbar.tsx:47-53`).
- **On a page**: Back, then the title, then that page's controls.
- **Dragging the window.** Buttons stay clickable inside the drag region. Sliders need `NO_DRAG`, as the toolbar's slider does today (`Toolbar.tsx:105-108`).

---

## 3. Each feature in detail

### 3.1 Tiles, Rows and Table

**Shared parts**
- A new `LibraryPane` component picks the layout. It also owns what all three layouts share:
  - selection and keyboard handling
  - the right-click menu
  - drag-to-tag
  - the selection bar
  - the empty, scanning and "no match" states, moved out of `App.tsx:923-955`
- The selection logic moves out of `FontList.tsx` (`:72-141`, `:164-177`, `:206-221`) into a `useSelection` hook.
- **Keyboard focus.** The list container keeps focus and points at the current item with `aria-activedescendant`. That is an ARIA attribute that tells screen readers which child is current without moving real focus. It's needed because of virtualization: only rows on screen are drawn, so the current row may not exist in the page.
  - Arrows, Home/End and Page Up/Down move the selection, and Shift extends it.
  - Return opens.
  - ⌘A and Esc work as today.
- **Clicks.**
  - A click selects.
  - A double-click or Return opens (or a single click, depending on your answer to Q1).
  - ⌘-click and Shift-click only select.
  - Right-click selects without opening. Today it also opens the panel (`FontList.tsx:215-221`), and that goes.
- **Family id.** Add a `Family.id` field in M1a. Today rows, expanded state and lookups use the family name (`FontList.tsx:47, 81`; `App.tsx:90`). With an id in place from the start, the regrouping in M3 doesn't break them.

**Tiles**
- Each card has:
  - a header: name, style count and a state mark
  - one fitted preview line, using `PreviewText` row mode (`src/components/PreviewText.tsx:60-75`)
  - a footer: source dots, up to 4 tag dots plus "+n", Variable/Mono marks and the sample badge
- **Sizing.**
  - Minimum card width = clamp(180px, size × 5.5, 520px), following the size slider.
  - Card height is fixed for each size: 28 (header) + size × 1.35 + 24 (padding) + 24 (footer).
- **Drawing only what's on screen.**
  - The list virtualizes rows of cards with `@tanstack/react-virtual`.
  - Columns = floor((width + gap) / (min + gap)), measured with a ResizeObserver.
  - Rows have a fixed height, so nothing is measured, and 2 extra rows are drawn above and below.
  - When the column count changes, the first visible family stays at the top.
- `role="grid"` with `aria-rowcount` and `aria-colcount`, and one Tab stop.
- Tiles don't expand to show styles. With "Group styles into families" off, each style gets its own card.

**Rows**
- This is today's `FontList` with expand-to-styles (`FontList.tsx:417-525`), now using the shared hook.

**Table**
- **Default columns:** state, Name (with an expand chevron), Styles, Weights (text such as "300–900" or "Variable 100–900"), Foundry, Format, Source, Added, Tags.
- **Optional columns:** Preview, Version, Designer, File, Size, Glyphs.
- **Preview column.**
  - It is on by default at 18px, and the slider sizes it within 12–32px.
  - Turning it off means no font files load at all, which makes Table the fastest layout.
- **Header.**
  - Click a header to sort, with `aria-sort`.
  - Right-click the header row to show or hide columns.
  - Drag column edges to resize.
  - The header is sticky, and Name stays pinned while you scroll sideways.
- **Rows** have a fixed height: compact 28px, regular 32px, or 40px with Preview on.
- **Accessibility:** `role="treegrid"`, `aria-rowindex` on the virtualized rows, and `aria-expanded` on family rows. ←/→ collapse and expand.
- **Built from divs with ARIA roles, not `<table>`.** Virtualized rows have to be absolutely positioned, which a real table doesn't allow.
- Weights are shown as text, not a dotted track.

**Saved preferences.** `layout`, `tableColumns` and `tableDensity` go in `AppSettings` (`src/api.ts:358-378`, `src-tauri/src/settings.rs:80-123`). That storage keeps one row per key, so it needs no migration (`settings.rs:1-6`).

### 3.2 The font page

**Header (the top row)**
- Back
- Family name (the page's `h1` heading) and "N styles"
- A style picker (Select)
- The family switch with n/total, or a lock
- Tags (⌘T)
- A More menu: Compare with…, Pair With…, Family Group…, Show in Finder, Copy PostScript Name

Under the title is a row of tag chips with remove buttons, reusing `DetailPanel.tsx:61-103`.

**Tabs** (Base UI Tabs; arrow keys move between tabs)
- **Specimen**
  - the waterfall (`DetailPanel.tsx:33-51, 192-214`)
  - a paragraph block
  - "All styles": one line per style with its own switch. This is where you turn single styles on and off.
- **Characters**
  - Today's grid, unchanged: block chips, arrows with Enter to copy, and "Show all" (`src/components/CharacterGrid.tsx:203-244`).
  - Adds a search box that takes a typed character or a U+ code.
  - Searching by Unicode character name would need a name database, so it waits.
- **OpenType** (M5): the features the font really has.
- **Axes** (shown only for variable fonts): today's sliders (`DetailPanel.tsx:216-244`) plus a number field per axis. Named instances come in M5.
- **Info**
  - Today's rows (`DetailPanel.tsx:137-155`).
  - Adds full name, location with Show in Finder, Added, and the copies list (`DetailPanel.tsx:265-304`).
  - M5 adds more fields (section 3.8).

**Edge cases**
- Filters don't apply on the page: it always shows the whole family.
- If you opened it from a Variable-only list, the variable style is chosen first.
- If the family leaves the library while open, the page says "This font isn't in your library anymore" and offers Back.
- Online-only and too-large files reuse the existing messages (`DetailPanel.tsx:183-187`).
- The page keeps working while a scan runs.
- ⌘F leaves the page and puts focus in Search.

**The detail panel is retired.** Its parts move into the page. The third grid column and `showDetail` go (`App.tsx:791-793, 844, 959-971`). There is no side quick look either: you asked for no panel, and Table's Preview column covers a quick glance. The last-used tab is saved as `fontPageTab`.

### 3.3 View options popover

- **Layout.** Also on the toolbar.
- **Group styles into families** (on/off).
  - Off makes every style its own item, labelled "Family Style".
  - This is a new `ungroup()` function in `library.ts`.
- **Sort.**
  - Options: Name A–Z / Z–A, Recently added, Number of styles, Weight, Foundry, Active first.
  - One `sortFamilies()` function in `library.ts` runs after filtering. Table header clicks set the same value.
  - Styles inside a family keep their own order (`library.ts:135-142`), which M3 improves.
- **Table density.** Shown only in Table.
- **Preview options (M5).**
  - Alignment, case, outline, underline, and ink and paper colors.
  - A short row of features applied to every preview: no ligatures, small caps, tabular figures and case forms.
  - These apply to all layouts and to the font page.
- **Size shortcuts.** ⌘+ and ⌘− step through 12, 16, 24, 32, 48, 64, 96 and 128.

All of these are saved in `AppSettings`.

### 3.4 Compare and Pair (M4)

**Compare** (2–8 fonts)
- **Ways in:**
  - "Compare" on the selection bar (`FontList.tsx:257`)
  - the right-click menu
  - "Compare with…" in the font page's More menu, which opens a searchable picker
- **Modes:**
  - Lines: the same text, stacked and labelled.
  - Side by side: paragraphs in columns.
- One set of controls (text, size, alignment) drives every lane. Each lane has its own style picker.
- With more than 8, the extras are left out and a note says so.
- **Stretch goal: Overlay.** Outlines stacked in different colors with baseline and x-height lines. It needs the preview profile's ascent and descent (`PreviewInfo`) to line up baselines.

**Pair**
- A headline and body sample set in two fonts.
- Each font has its own style and size, and the body also has line height.
- A Swap button switches the two.
- The second font is chosen with a searchable picker.
- Saving pairs can come later.

### 3.5 Quick tags, the right-click menu and native menus (M4)

- **Quick tags.** ⌘T opens the existing `TagPicker` (`src/tags/TagPicker.tsx:31`) for the selection or the open family. Type to filter or create a tag, and Return applies it.
- **Right-click menu.** Today it has only tag and sync items (`src/tags/FontMenu.tsx:40-129`). It becomes:
  - Open
  - Show Info (⌘I)
  - Turn On
  - Turn On Until Logout
  - Turn Off
  - Tags ▸
  - Compare
  - Pair With…
  - Family Group…
  - Show in Finder

  Whichever "Turn On" matches the saved activation mode is listed first. The back end already accepts the "until logout" choice (`setActivation`'s `scope`, `App.tsx:446-452`).
- **Shortcuts.**
  - ⌥-click on a switch uses the other mode.
  - ⌘Return turns the selection on or off.
  - ⌥⌘Return turns it on until logout.
- **macOS menus.**
  - Add View and Font menus in `src-tauri/src/window.rs:29-84`.
  - Each item sends a "menu" event with an id, which `App.tsx` handles the same way it handles "open-settings" (`App.tsx:386-398`).
  - A small `set_menu_state` command keeps the menus' checkmarks in step with the page.
- **Windows.** There is no app menu (`src-tauri/src/lib.rs:135-137`). So every action also lives in the toolbar, the page header or the right-click menu.
- **Not planned:** removing a single font from the library, and Move to Trash (both in screenshot 25).
  - Fontface reads folders where they are, so removing one font needs a list of excluded files.
  - Trashing font files needs its own careful flow.

### 3.6 States and locks (M2)

States are listed in display priority:

| State | How it's known | Mark |
|---|---|---|
| Busy | A request is queued | Spinner (exists, `ActivationSwitch.tsx:27`) |
| Part of macOS | Copy in `/System/Library/Fonts` | Lock. Tooltip: "Part of macOS. Always on." |
| Installed | Copy in `/Library/Fonts` or `~/Library/Fonts` (`db.rs:239-248`) | Lock. Tooltip: "Installed in a Library Fonts folder. Always on while it's there." |
| On until logout | New `temporary` flag | Switch on, plus a `timer` mark |
| On | `osActive` | Switch on |
| Partly on (family) | `activeCount < switchable` | Today's "n/total" (`ActivationSwitch.tsx:28-32`) |
| Waiting for its file | `activated && !osActive && !installed` | Dimmed switch, plus a `link_off` mark |
| On by another app | `osActive && !activated && !installed` | Switch on, plus an info mark |
| Off | — | Switch off |

**How each state is found**
- **`temporary`.** Set in `commands::list_fonts` (`src-tauri/src/commands.rs:199-207`) from `activation::temporary_paths` (`activation/mod.rs:197-202`). No schema change is needed.
- **Lock kind.** Derived in the interface from the font's folder path.
- **"Waiting for its file."** This really does mean the file isn't available. When another app turns off a font that was loaded, Fontface already clears `activated` (`commands.rs:209+`).
- **Known gap, unchanged.** Fonts disabled in Font Book still show as on (`db.rs:413-420`; `docs/FEATURES.md:126`).

**Components**
- `ActivationSwitch` gets `lock` and `mark` props.
- A new compact `StateMark` (dot, lock, timer or link_off) is used in Tiles and Table.
- The `InstalledBadge` text (`ActivationSwitch.tsx:45-57`) becomes "Part of macOS" or "Installed".
- Every mark has a tooltip and screen-reader text, so color is never the only signal.

### 3.7 Smart entries (M2)

- **New view kinds:** `yours`, `recent`, `active` and `untagged`, added to `LibraryView` (`library.ts:32-38`). They must also be handled in:
  - `filterFamilies` (`:189-216`)
  - `viewKey` (`:41-52`)
  - `parseView` (`lastView.ts:23-40`)
  - `hiddenBySidebar` (`lastView.ts:63-77`)
- **Counts** are added to the `counts` calculation in `App.tsx`.
- **In Active**, the toolbar's status filter is hidden and reset to All, because it would add nothing there.
- **In Recently Added**, the sort starts as "Recently added". Rows and Tiles show "Added <date>".
- **Gotcha for the new Settings › Sidebar rows.** The Rust side ignores sidebar keys it doesn't know (`settings.rs:156-169`). So the keys must be added there too, or a change made only in TypeScript is silently not saved.

### 3.8 Sources (M2), and font page depth (M5)

**Sources**
- **Layout.**
  - One section, in this order: Font Book, Google Fonts, Adobe Fonts, Purchases, then your folders A–Z.
  - "+" adds a folder (`Sidebar.tsx:335`).
- **No trees.** The folder trees (`UserFolder` and `SubfolderTree`, `Sidebar.tsx:156-172` and `src/tags/LocationTree.tsx`) leave the sidebar.
- **Subfolder picker.**
  - A toolbar button on Font Book and folder views opens a searchable popover tree, built from `useSubfolders` (`LocationTree.tsx:66`).
  - Picking a subfolder uses the existing `location` view kind. So saved views and subfolder colors keep working.
  - Right-clicking a subfolder keeps the color menu.
  - For Font Book, the picker offers its three folders.
- **Row right-click menu:** Rescan, Stop, Show in Finder, Locate… (when the folder is missing), Color, and Remove from Library… (your folders only). Today Rescan and Remove are hover icons only (`Sidebar.tsx:142-151`), so the keyboard can't reach them. The hover icons stay too.
- **Service rows.** Google Fonts and Purchases show their fonts that are in your library, as a normal list, so layouts, sort and filters all apply. A toolbar button opens the catalog as a page: "Browse Google Fonts" or "New downloads (n)". Today these rows open only the catalog (`App.tsx:866-891`). (See Q2.)

**More on the font page (M5)**
- **OpenType tab.**
  - Groups: ligatures, figures, position, case, alternates (named ssXX and cvXX sets), and spacing.
  - Each feature is a toggle with a sample, applied through `font-feature-settings`.
  - Features that are on by default (liga, kern, calt) start on.
- **Axes tab.**
  - Named instances (the font's own preset styles) appear as clickable chips.
  - Adds Reset and "Show hidden axes".
  - `src-tauri/src/tags/named_styles.rs:72` already parses `fvar` (the variable-axes table) for names. It needs to return coordinates too.
- **Info tab additions:**
  - description (name ID 10)
  - designer and foundry URLs (11, 12)
  - trademark (7)
  - embedding permissions (OS/2 `fsType`, through ttf-parser's `Face::permissions()`), shown as installable, editable, preview and print, or restricted
  - languages, from CoreText's `CTFontCopySupportedLanguages`, shown with `Intl.DisplayNames`, so no extra language data ships with the app
  - scripts, from the character blocks already computed
  - last turned on
  - Added

---

## 4. What happens to existing pieces

| Piece | Change |
|---|---|
| `DetailPanel.tsx` | Split into the font page tabs, then removed. The third grid column and `showDetail` go. |
| `FontList.tsx` | Becomes the Rows layout using `useSelection`. A click no longer opens anything (`:131`), and right-click no longer opens (`:215-221`). |
| Toolbar All / Active / Inactive | Stays, with the same words. Hidden in the Active entry. Still narrows sources and tags. |
| Variable toggle, search, preview text, slider | Stay. Hidden on pages. |
| Services section | Merged into Sources. |
| Font Book with nested system folders (`Sidebar.tsx:255-256`) | One row. Its folders move into the picker. |
| Folders section and subfolder trees | Merged into Sources. Trees removed, and the picker replaces them. |
| `LocationTree` colors | Kept, and set from the picker's right-click menu. `useSubfolders` is reused. |
| Settings › Sidebar | Gains four smart-entry rows. Its intro text still holds. |
| "Show installed fonts in All Fonts" | Kept. It now overlaps with Your Fonts and could be retired later. |
| `lastView` | Gains the new kinds. Old saved views (`location:`, `folder:`, `service:google`) still open. `service:google` now means the list, not the catalog. |
| Native View menu (Full Screen only) | Gains layout, grouping, sort, size and Back. A new Font menu is added. |
| `INSTALLED_LABEL` (`library.ts:83-84`) | Unchanged. |

---

## 5. Family grouping

### 5.1 Rules, in order of precedence

1. **Your choice for this font wins.** It's a stored family (and optional style) for the face key.
2. **Your rule for this name comes next.** Examples: "Merge 'Aaux ProBold' into Aaux Pro", or "Keep 'Arial Narrow' separate". Fonts that arrive later follow it.
3. **Automatic merge.** This applies only while Settings › Library › "Group families by name" is on, which is the default. A merge needs all three of the following:
   - **(a)** The family name ends in one or more whole style words that can merge. Those are weight words, slope words or variant words (lists below). Splitting off the remaining spelling-only differences, such as "BigCaslon" vs "Big Caslon", also counts.
   - **(b)** What's left after removing those words matches a family in the library, or at least two family names reduce to it. Names are compared as a "squash key": lowercase, with spaces, hyphens, underscores, dots, ™ and ® removed. So "AauxPro" equals "Aaux Pro".
   - **(c)** At least one supporting signal:
     - **PostScript prefix.** The part of the PostScript name before the first "-" squashes to the base, or matches the prefix of a face already in the base family. Example: AbhayaLibre-ExtraBold and AbhayaLibre-Regular.
     - **Same foundry or designer** (name IDs 8 or 9), present on both and equal.
     - **The weight number agrees.** The weight word matches the font's stored weight (OS/2 `usWeightClass`, the weight number stored in the font) within 100.
4. **Otherwise, the font's own name is used.** That's name ID 16 if present, else name ID 1, as today (`src-tauri/src/scanner.rs:108`).

Folders are never a requirement, never a signal and never a guard.

### 5.2 Words

**Words that can merge:**
- **Weight:** Thin, Hairline, ExtraLight/UltraLight, Light, Book, Regular/Normal/Roman/Plain, Medium, SemiBold/DemiBold/Demi, Bold, ExtraBold/UltraBold, Heavy, Black, ExtraBlack/UltraBlack.
- **Slope:** Italic, Oblique.
- **Variant:** OSF/OsF, SC, LF, TF, Expert, Alt, Swash.
- **Abbreviations** (Lt, Bd, Blk, Md, Hv, It, Obl and similar) count only when the PostScript prefix signal is present.

**Words that only produce a suggestion:**
- **Width:** Condensed, Cond, Cn, Narrow, Compressed, SemiCondensed, Extended, Expanded, Wide.
- **Optical or size:** Display, Text, Caption, Micro, Subhead, Poster, Headline, Titling.
- **Numbered styles,** where what's left ends in a number ("Univers 45 Light").

**Whole words only.** A word is removed only from the end of the name. It must follow a space, hyphen or underscore, or a lowercase-to-uppercase step ("AmintaBold"). The longest match is tried first, so "ExtraBlack" is checked before "Black".

### 5.3 Guards (no automatic merge; may still be suggested)

- **G1. The font has its own grouping name (name ID 16).** The designer grouped it on purpose. Examples: Barlow Condensed, Avenir Next Condensed.
- **G2.** Any removed word is a width, optical or number word.
- **G3.** The base would be shorter than 3 letters, or nothing would be left.
- **G4.** Both fonts name a foundry, and the foundries differ.
- **G5.** You chose "Keep separate" for this name.

### 5.4 Style label and sort order

**Label.** The removed words in canonical spelling, then the font's own style. The font's own style is dropped when it is Regular, Roman, Plain or Normal, and repeated words are removed.
- "AmintaBlackItalic" with style "Regular" becomes **Black Italic**.
- "Dynasty Heavy" with style "Italic" becomes **Heavy Italic**.
- "AauxPro-BlackOSF" becomes **Black OSF**.

**Sorting inside a family.** It uses the weight, width and slope named in the label when there is one, and otherwise the font's stored numbers. This matters because 1,583 faces wrongly report weight 400 and 406 italics aren't flagged as italic. It applies to every family, so `sortFaces` (`library.ts:135-142`) improves everywhere.

### 5.5 Examples

| Family names | Result | Why |
|---|---|---|
| Abhaya Libre ExtraBold, Abhaya Libre Medium, plus Abhaya Libre | Abhaya Libre: ExtraBold, Medium, Regular | Weight words, PostScript prefix |
| AmintaBold, AmintaBlackItalic, plus Aminta | Aminta: Bold, Black Italic | Lowercase-to-uppercase step |
| Aaux ProBold, AauxPro-BlackOSF (52 names) | Aaux Pro, one family | Squash key "aauxpro", PostScript prefix |
| Dynasty Heavy | Dynasty: Heavy | Weight word |
| Big Caslon / BigCaslon, Hoefler Text / HoeflerText | Merged | Spelling only, same foundry |
| Arial Narrow, MetaCond, FarnhamDisplay | Suggestion | Width or optical word |
| Univers 45 Light | Suggestion | Numbered style |
| Barlow Condensed, Avenir Next Condensed | Stay separate | G1 |
| Noto Sans Arabic, Roboto Mono, Gill Sans Nova | Stay separate | Not style words |
| Book Antiqua, Moonlight | Stay separate | Only words at the end; no word boundary before "light" |
| Flyerfonts-* | Stay separate | A PostScript prefix alone never merges |
| Agu Display | Stays separate | Optical word, and no "Agu" family exists |

### 5.6 The Family groups page

- **Ways in:**
  - right-click › Family Group…
  - the font page's More menu
  - Settings › Library ("Review n suggestions")
  - the Library heading's menu in the sidebar
- **Header.** Back, the title, a filter (All · Suggested (n) · Grouped automatically · Changed by you), and a search box.
- **Body.** A virtualized list of families. Each shows its styles with checkboxes, the PostScript name, the source and, when moved, "from <original name>".
- **Suggestions** read like: "Merge 3 families into Abhaya Libre (5 styles)", with Merge and Keep separate buttons. "Merge all suggestions (n)" asks for confirmation first.
- **Bottom bar.** "Move N styles to family: [type or pick a name] [Move]", plus "Use the fonts' own names" to reset.
- **Undo.** Every action shows an Undo toast.
- **On the font page.** The Info tab says "Grouped by name from 'Aaux ProBold'" and offers a Keep separate link.

### 5.7 Storage and effects elsewhere

**Storage.** New side tables, created outside the numbered migrations like the tag tables (`src-tauri/src/tags/mod.rs:50-89`):
- `family_overrides(face_key PK, family, style, set_at)`
- `family_rules(name_key PK, decision 'merge'|'separate', into_family, set_at)`

**Effects elsewhere**
- **Tags.** They are keyed by face key (`library.ts:108`), so regrouping never changes them.
- **Tag import** keeps matching raw family names (`tags/mod.rs:584-661`).
- **Search** also matches the grouped family name.
- **Sync (optional, later).** Add a new field on the existing `Face` change (`src-tauri/src/sync/ops.rs:104`). It must be named something like `group`, not `family`, because `family` already carries a display label (`ops.rs:14`). Name rules would be a new change kind, which older versions skip (`ops.rs:106-107`).

---

## 6. Data and storage changes

| Change | Where | When |
|---|---|---|
| Add `manufacturer`, `designer`, `version`, `glyphCount` and `weightRange` (from the `wght` axis in `fonts.axes`) to `FontSummary` | `db.rs:392-449` (`summary_columns`, `SUMMARY_LEN`, `summary_from_row`), `model.rs`, `api.ts:14-41` | M1b |
| `fonts.added_at` | Add it with `ensure_column` (`tags/mod.rs:91-106`). That file's own comment says to use it for any later column. Existing rows get a one-time backfill from the file's creation date (a cheap file-info read that works on online-only files), falling back to `folders.added_at`. New rows get the scan's start time. The scanner's update clause (`scanner.rs:656-664`) leaves it alone. | M1b |
| `temporary` flag | Set in `commands::list_fonts` from `temporary_paths` | M2 |
| `legacy_family` (name ID 1), `legacy_style` (2), `typo_family` (16 or null), `names_rev` | Columns written by `parse_face` (`scanner.rs:106-161`). A launch backfill fills older rows, reusing the preview backfill's readers (`preview/mod.rs:716`) and its safety rules (skip online-only and Creative Cloud files). The list payload gets `legacyFamily` and `hasTypoFamily`. | M3 |
| `family_overrides`, `family_rules` | New `src-tauri/src/families.rs`, with `ensure_schema` called from `lib.rs:147-151` | M3 |
| `last_turned_on(path PK, at)` | Written in `switch()` (`commands.rs:375-413`) when a file ends up on | M5 |
| A `font_facts(id)` command, read when needed | Name IDs 7, 10, 11, 12 and 19; `fsType`; languages; named instances; the OpenType feature list and ssXX names. Read on the two reader threads, not stored. | M5 |
| New settings | Each needs a TypeScript field and a Rust `apply_key` branch. Unknown keys are ignored (`settings.rs:189-190`). See the list below. | Each milestone |

New settings:
- `layout`
- `groupStyles`
- `sort {key, desc}`
- `tableColumns`
- `tableDensity`
- `openFontWith`
- `fontPageTab`
- `groupByName`
- `preview {align, case, outline, underline, ink, paper, features}`
- `sidebar.{yours, recent, active, untagged}`

---

## 7. Performance on about 12,000 fonts

Sean's library has 12,257 font rows, 11,047 faces and about 3,561 families.

- **Grouping.** It reruns every time `fonts` changes, which includes every switch flip (`App.tsx:468`) and every 4 seconds during a scan (`App.tsx:70`). Name analysis is cached by family string (about 4,500 distinct strings). The target is under 30ms for the whole library, measured in a dev build.
- **Filtering and sorting.** Filtering is one pass over the faces, and sorting covers about 3,500 families. Sorting runs in a `useMemo` after filtering.
- **Tiles.** Rows of cards are virtualized with fixed heights and 2 extra rows. About 30–40 cards are on screen. They go through the existing loader: 6 at a time, newest first, and anything that scrolls away is dropped (`src/fontLoader.ts:24-60`). Profile requests fit the 64-per-call batch (`preview/mod.rs:66`). Optionally, new loads pause while the list reports fast scrolling.
- **Font memory: a fix that's needed.** Loaded fonts are kept for the whole session and never removed (`fontLoader.ts:105-108`). Scrolling through Tiles would load thousands of them. Add a least-recently-used limit: once more than about 500 app-loaded faces are held with no rows using them, remove the oldest from `document.fonts` and the cache. This must land with Tiles in M1b.
- **Table.** Rows have a fixed height. With Preview off, it loads no fonts.
- **List payload.** The new short fields add about 50 bytes per row, roughly 0.6 MB per full reload. Copyright and license text stay out of the list.
- **Backfills.** Each one runs once in the background on the existing reader threads. Online-only files are skipped until they're downloaded.
- **Font page.** It reads characters, facts and features only when opened. The list's loading path doesn't change.
- **Family groups page.** Suggestions are computed only when the page opens.

---

## 8. Files to add and change

**New (front end)**
- `src/nav.ts`: page stack and Back handling (keys, mouse button, menu events)
- `src/components/library/LibraryPane.tsx`, `useSelection.ts`, `FontTiles.tsx`, `FontTable.tsx`, `columns.ts`
- `src/components/StateMark.tsx`
- `src/components/ViewOptions.tsx`
- `src/components/SubfolderPicker.tsx`
- `src/components/fontPage/FontPage.tsx`, `PageHeader.tsx`, `SpecimenTab.tsx`, `CharactersTab.tsx`, `AxesTab.tsx`, `InfoTab.tsx`, and `OpenTypeTab.tsx` (M5)
- `src/components/ComparePage.tsx`, `PairPage.tsx`
- `src/components/FamilyGroupsPage.tsx`
- `src/familyGroups.ts` and `src/familyGroups.test.ts`
- `src/families/store.ts`
- `src/components/ui/tabs.tsx`, `select.tsx`, `toggle-group.tsx`, `combobox.tsx` (shadcn on Base UI)

**Changed (front end)**
- `src/App.tsx`
- `src/library.ts`: view kinds, `Family.id`, lock kind and temporary flag, sort, ungroup, smart filters, style labels, name grouping
- `src/api.ts`
- `src/components/Toolbar.tsx`, `FontList.tsx`, `Sidebar.tsx`, `ActivationSwitch.tsx`, `CharacterGrid.tsx`
- `DetailPanel.tsx` (removed)
- `src/tags/FontMenu.tsx`, `src/tags/menus.tsx`, `src/tags/LocationTree.tsx`
- `src/settings/lastView.ts`, `src/settings/sections.tsx`

**Rust**
- New: `src-tauri/src/families.rs`
- Changed:
  - `src-tauri/src/db.rs`, `scanner.rs`, `model.rs`, `commands.rs`, `settings.rs`, `window.rs`, `lib.rs`
  - `preview/mod.rs` (backfill)
  - `activation/mod.rs` (last turned on)
  - `tags/named_styles.rs`
  - optionally `sync/ops.rs`

**Docs**
- `docs/FEATURES.md`: rows 111, 116-119, 129, 131 and 132
- `docs/ARCHITECTURE.md`

---

## 9. Milestones

Each milestone ships on its own. Every one must also pass `npm run typecheck`, `npm run test:ui` and `cargo test`.

### M1a. Font page and Back

**Build**
- Page stack, `useSelection`, keyboard support in Rows, the font page with Specimen, Characters, Axes and Info
- Retire `DetailPanel`
- Add `Family.id`

**Check**
- [ ] Opening a family 2,000 rows down shows its page. Back returns to the same scroll position with that row focused.
- [ ] Back works from the button, ⌘[, Esc outside fields, and the mouse.
- [ ] A sidebar click closes the page.
- [ ] Right-click never opens a page.
- [ ] Arrow keys and Return work in Rows.
- [ ] Removing the font's folder while its page is open shows the "isn't in your library anymore" message.
- [ ] Opening a page is announced and focus lands on the heading.
- [ ] The page header still drags and zooms the window.

### M1b. Tiles, Table and View options

**Build**
- Tiles, Table, the View options popover, sort, "Group styles into families"
- The new list fields and `added_at` with its backfill
- The font-memory limit

**Check**
- [ ] ⌘1–3 switch layouts, and the choice survives a relaunch.
- [ ] The selection is kept across layouts.
- [ ] A Web Inspector profile of a fast scroll through all of Sean's Tiles shows no task over 50ms.
- [ ] After that scroll, `document.fonts.size` stays under the limit.
- [ ] Table sorts by header and announces it. Columns show, hide and resize, and Name stays pinned.
- [ ] Turning grouping off lists single styles.
- [ ] New fonts get an Added date, and older ones show their file date.
- [ ] `list_fonts` time grows by less than 10%.

### M2. Smart entries, flat Sources and states

**Check**
- [ ] Your Fonts, Active and Not Tagged counts match a direct database query.
- [ ] Sources has no chevrons.
- [ ] Every folder action is reachable with Shift-F10.
- [ ] The picker narrows to a subfolder, and subfolder colors still show.
- [ ] Old saved views still open.
- [ ] The Google row lists library fonts, and "Browse" opens the catalog with Back.
- [ ] Each of the eight states shows the right mark, tooltip and screen-reader text.
- [ ] Hiding a smart entry while you're in it falls back to All Fonts.

### M3. Family grouping and the Family groups page

**Check**
- [ ] Unit tests cover every example and guard in section 5.
- [ ] After the backfill, Aaux Pro, Aminta and Dynasty are single families sorted by weight.
- [ ] The guard examples stay separate.
- [ ] Merge, Keep separate, Move and Undo all work, and choices survive a rescan and a relaunch.
- [ ] Tag counts are identical before and after.
- [ ] Turning the setting off restores the fonts' own names.
- [ ] Grouping takes under 30ms.

### M4. Quick tags, Compare, Pair and menus

**Check**
- [ ] ⌘T tags the selection or the open page, and can create a new tag.
- [ ] The right-click and macOS menus cover every item listed in 3.5.
- [ ] ⌥-click on a switch uses the other mode.
- [ ] Compare shows 2–8 fonts, and more than 8 shows a note.
- [ ] Pair swaps the two fonts.
- [ ] Back from the menu never runs twice.

### M5. Preview styling, OpenType, Axes and full Info

**Check**
- [ ] Preview options apply in all layouts and on the page.
- [ ] The OpenType tab lists only features the font really has, using the font's own ssXX names.
- [ ] Named instances set the axes.
- [ ] Info shows embedding, languages and last turned on.
- [ ] Online-only files show "Download to see details", not an error.

---

## 10. Risks

- **The click change.** People's habits change: today a click opens the panel.
- **False merges.** These are limited by the guards, Undo, per-name Keep separate, and the setting.
- **Backfills.** Reading every local font file once adds disk work. Files that are online only (Sean's Google Drive) keep their old grouping until they are downloaded.
- **File creation dates may be rough.** Files synced from the cloud may carry their sync date as their creation date.
- **Double-firing shortcuts.** A native menu shortcut can fire along with the page's own key handler. That's harmless for setting a layout, but not for Back, so menu events for Back must be ignored within about 200ms of a keyboard Back.
- **Font memory in Tiles,** if the memory limit slips out of M1b.
- **Silent settings loss.** New settings or sidebar keys that are added only in TypeScript are dropped without an error.
- **Future table rebuilds.** Any future numbered migration that rebuilds `fonts` with `SELECT *` (as the v3 migration did at `db.rs:107`) must list the new columns.
- **More families per name.** Expanded state and row keys depend on `Family.id` being in place before M3.

## 11. Questions for Sean

These are only the calls that change behavior you'll notice.

1. **How do you open a font?** Options:
   - single click, as you described
   - double-click or Return, with a single click only selecting

   I recommend double-click as the default, because a single click that opens a page makes building a multi-select awkward. A setting would offer both.
2. **Source rows.** Should Google Fonts and Purchases open your library fonts from that source, with a "Browse" button for the catalog (recommended)? Or should they keep opening the catalog first?
3. **Width variants.** Should Condensed, Narrow and Extended names fold into the main family automatically? Or should they only be suggested (recommended)? Weight and slope words would merge automatically either way.

**Choices I made where an earlier question was open (say if you want any changed):**
- One layout for the whole library.
- Table's Preview column is on by default.
- No side quick-look panel.
- Launch reopens only the list, not a font page.
- Preview options apply to every layout.
- Pair comes after Compare.
- macOS-folder fonts stay locked, but say why.
- Active leaves out macOS fonts.
- Built-in tags don't count as tags for Not Tagged.
- The name "Your Fonts".
- Folders sorted A–Z.
- Subfolders reached through a picker.
- Languages from CoreText now.
- "Last turned on" is tracked.

No repository files were changed.