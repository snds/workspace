---
title: Fontface — previews for Google Fonts and Adobe Fonts: options and recommendation
type: note
project: 25-fontface
created: 2026-10-18
status: recommendation, open questions for Sean
source: read-only research workflow in the Fontface Claude Code session (repo main @ 826c574)
---
## Recommendation

**Google Fonts.** Fontface's Rust core should download a tiny preview file for each row and keep it in the app's cache folder. The file holds only the letters of the family's name, from Google's documented CSS2 `text=` option. Rust hands it to the web view through the existing `ff://` scheme, so the web view never talks to Google.

**Library fonts first.** Before any network work, 644 catalog families that are already in Sean's library can preview from local files.

**Opt-in.** Online previews should be off until the user turns them on. Every request shows Google the user's IP address and which families they scroll past.

**Adobe Fonts.** Fontface should draw previews natively with CoreText (Apple's text engine) and show them as images. The web view's canvas can't see fonts Creative Cloud turns on, and the web view may not see them at all. This never opens Adobe's files and never uses the network. Adobe fonts that aren't turned on can't be previewed legitimately, so they stay as links.

**Typed text never leaves the Mac.** When the user types, Google rows load a fixed alphabet file. The detail view downloads the real desktop font into a cache that is never turned on.

---

## 1. Where things stand

**Google rows**
- Only families in the managed Google Fonts folder draw in their own font (`src/components/GoogleFontsPanel.tsx:56-78`).
- Every other row shows the name in the interface font (`GoogleFontsPanel.tsx:61-63`).
- The panel only gets fonts from that folder (`src/App.tsx:869`). It matches them only by that folder's path (`GoogleFontsPanel.tsx:105-116`).
- Sean's managed folder is empty, so all 1,981 rows are plain text today.
- `services/google.rs` only downloads full desktop files (`:542-625`). It has no preview path.
- The catalog comes from Fontsource without a key (`google.rs:1-6`, `:47`). It keeps nine fields and drops `defSubset`, the family's main script (`google.rs:67-84`).

**Adobe rows**
- The CSS asks for the font by name: `"<PostScriptName>", "<family>"` (`src/components/AdobeFontsPanel.tsx:139`).
- If the web view can't see the font, it silently draws a default font such as Times. Every row then looks the same.
- This Mac has no Creative Cloud, so the panel shows "Creative Cloud isn't installed" (`AdobeFontsPanel.tsx:106-113`).

**Plumbing that already exists**
- `ff://` serves font bytes by numeric library id only (`src-tauri/src/protocol.rs:32`, `:65`).
- The CSP (Content Security Policy, the web view's list of allowed sources) already allows `ff:` for fonts and fetches. It does not allow it for images (`src-tauri/tauri.conf.json:24`).
- The preview profiler, `preview::profile_safely`, works on any ttf-parser face (`src-tauri/src/preview/mod.rs:352`).

---

## 2. Options map

### Google Fonts

| Option | How it works | Accuracy | Speed | Cache size | Offline | Privacy | Terms / legal risk | Complexity |
|---|---|---|---|---|---|---|---|---|
| **G1. Library match (do first)** | Match catalog family names to fonts already in the library, then use the existing `useFontFace` and profile path | The real font, but it may be another version or a same-named font from another foundry | Instant, local | None | Yes | Nothing sent | None | Small: `App.tsx:869`, `GoogleFontsPanel.tsx:105-116` |
| **G2. Rust fetches CSS2 `text=` name files (recommended for rows)** | Rust requests `https://fonts.googleapis.com/css2?family=Inter&text=Inter`, one family per request. It takes the one `https://fonts.gstatic.com/l/font?kit=…&v=v20` URL, downloads that file, checks it with ttf-parser and profiles it | Google's live build with real outlines. Default instance and name letters only | Cold: 0.17–0.25 s (CSS) + 0.06–0.14 s (font). After that, local | 1–9 KB per family (about 4.5 KB average). The whole catalog is about 9 MB | Cached rows: yes | IP address and family name go to Google. Opt-in | Low. A documented Google feature, the CSS is not kept, and the fonts are OFL, Apache or UFL | Medium: new Rust module, command, protocol branch, setting |
| G3. The Developer API's `menu` font | The keyed catalog (`googleapis.com/webfonts/v1`) gives a `menu` URL per family. This is the original plan (`docs/INTEGRATIONS.md:153`) | Same as G2 (not measured) | One request per row, with no CSS step | Same as G2 | Same | Same | Needs the user's own API key, because an open-source build can't ship one (`INTEGRATIONS.md:204`) | Medium, plus the key flow. Today the app has no key |
| G4. The web view loads Google directly | Add `fonts.googleapis.com` and `fonts.gstatic.com` to the CSP | Variable WOFF2 files, which is good | Similar | WebKit's own cache: expires daily and may be cleared | Unreliable | Consent is checked only in JavaScript. No size cap (a 1.18 MB emoji slice gets through) | Same as G2 | Little code, but a wider CSP in a public repo. **Not recommended** |
| G5. Fontsource and jsDelivr files | `api.fontsource.org` family JSON (38 KB) plus a `cdn.jsdelivr.net` file | The full Latin set, so typed Latin text is right. Variable WOFF2 exists, but ttf-parser can't read WOFF2 | 5–20 times more data per row. Inter's Latin file is 23.6 KB as WOFF2, 66.9 KB as TTF | About 50–130 MB for the whole catalog (my estimate) | Cached rows: yes | Adds jsDelivr as a new third party | No published hard limits | Medium. Only for rare script cases |
| **G6. Full desktop font into a preview cache (recommended for the detail view)** | Reuse the install download from `google/fonts` (raw.githubusercontent.com), but never turn the font on | Exact: the same file an install would get, with all axes and all characters | Slow: tens of KB up to tens of MB for CJK (Chinese, Japanese, Korean) fonts (`services/mod.rs:71`) | Large, so only on request and with a cap | Once downloaded | GitHub sees the IP address and family | Low. The license allows it. Never install from the cache | Medium. Reuses `prepare` |

### Adobe Fonts

| Option | How it works | Accuracy | Speed | Cache size | Offline | Privacy | Terms / legal risk | Complexity |
|---|---|---|---|---|---|---|---|---|
| A1. Keep CSS names and add guards | Today's name lookup, plus a generic fallback, a DOM-width check that shows "Can't preview here", and no canvas fit | Unknown. The canvas never sees user-installed fonts, so the fit always uses the fallback font. WebKit's map of user fonts is undocumented | Instant | None | Yes | Nothing sent | Low | Hours |
| **A2. CoreText images (recommended)** | Rust creates the font from CoreText's registry entry, checks the PostScript name, draws the line into a bitmap, and serves a PNG | Matches WebKit: Impact 1279.98 vs 1279.98; Avenir Next 1489.80 vs 1491.00 at 100 px. The same as other Mac apps show | First render: median 2.4 ms, worst 14 ms. New text: 0.66 ms. 30 rows: about 20 ms | Memory only. 2,000 PNGs is about 23 MB | Yes | Nothing sent | Low. It uses normal OS text APIs, like any font menu (`INTEGRATIONS.md:251`). Never write renders to disk | Medium: Rust module, image component, CSP change |
| A3. A2 plus a fallback for library fonts | A2, also used for installed library fonts WebKit can't measure, and for files over 96 MB (`protocol.rs:22`) | Fixes the side bug in section 3 | Same | Same | Same | Same | Same | More code paths. Do later |
| A4. Previews of fonts that aren't turned on (web kits, scraping, embedding Adobe's site) | – | – | – | – | – | Adobe gets sign-in and usage data | **Ruled out** (`INTEGRATIONS.md:245`, `:249-253`, `:402-413`) | – |
| **A5. Link out (recommended for fonts that aren't turned on)** | Per-family search links (`INTEGRATIONS.md:238`), plus an "Open Creative Cloud" button | No preview | – | – | – | Only what the browser sends | None | Small |

---

## 3. Main issues and how each is handled

**Privacy and consent**
- **Problem.** Each Google request sends the IP address, `Fontface/0.1.0 (personal desktop font manager)` (`services/mod.rs:65`), the time and the family name. Because rows load as they scroll, Google learns which families the user scrolls past.
- **Handling.**
  - Default to off.
  - Ask once on the Google Fonts page.
  - Store the answer in `app_settings` (`settings.rs`).
  - Never send the search box text or typed preview text. Search filters locally.
  - Offer "Clear preview cache".
  - List both hosts in the privacy note (`INTEGRATIONS.md:137`, `:209`).
  - Optionally offer "Download all previews" (about 5.4 MB and 4,000 requests). Fetching every family hides which ones the user actually looks at.
  - A German court (LG München I, 2022) found that websites loading Google Fonts without consent shared visitor IPs. That case was about websites, but it supports opt-in.
- **Adobe** sends nothing.

**Terms**
- **Google.**
  - `text=` is a documented CSS2 feature. Use it only as documented (`INTEGRATIONS.md:206`).
  - Send Fontface's honest client name. Never send a fake browser name to get WOFF2.
  - Don't keep the CSS longer than its one-day cache header (`INTEGRATIONS.md:169`).
  - Keep the font files as OFL, Apache or UFL files.
  - Never install, turn on, sync or back up preview files (`INTEGRATIONS.md:207`, `:408`).
  - Not checked: I did not re-read the Google APIs Terms for this task.
- **Adobe.**
  - Draw only through CoreText, from the registry entry.
  - Never open, hash or reveal files under `livetype` (Adobe's font folder).
  - Never write a render to disk, export or sync.

**Offline and cache invalidation**
- **Google.**
  - Cached rows still draw offline. Rows that aren't cached show the name in the interface font, with a new "offline" state next to "cloud" and "too-large".
  - Reuse the 15-minute back-off after a failure (`google.rs:51`, `:63`).
  - Name each cache entry by its `lastModified` date. When the daily catalog refresh changes that date, the old entry goes.
  - Also remove families that drop out of the catalog.
  - Remember failures and retry them after 7 days.
- **Adobe.** Bump a generation number when CoreText reports a font change (`kCTFontManagerRegisteredFontsChangedNotification`, already planned at `INTEGRATIONS.md:235`). Also put the font's version name in the cache key.

**Typed preview text and subsets**
- **Problem.** A name-only file holds only those letters. WebKit fills other letters from a system font, which looks wrong. The `asciiMissing` result of a name-only profile is meaningless, so it must be ignored.
- **Handling.**
  - When the user types, load a second, fixed-alphabet file for each visible row. Printable ASCII (95 characters) is 15–28 KB over the network and 23–62 KB on disk. ASCII plus Latin-1 is 26–50 KB over the network.
  - About 25 rows cost about 0.4–0.7 MB once. After that it's cached.
  - Until the alphabet file arrives, keep the name preview rather than mixing fonts.
  - Inside the alphabet, the profile gives a true "Not in this font: …" (`src/previewProfiles.ts:155-161`).
  - Outside the alphabet, show "Can't preview 'x' here". Don't claim the character is missing from the font.
- **Adobe** has no subset problem. CoreText draws any text, and Rust can see which font each part of the text actually used.

**Variable fonts**
- **Rows.**
  - Rows show the default instance (weight 400). TTF from Fontface's client name can't carry variable axes, which is fine for a row.
  - 32 families have an `opsz` (optical size) axis. For those, ask for `:opsz@22`, kept inside the axis range. That matches what WebKit shows for an installed copy.
- **Badge.** The Variable badge keeps using `fam.variable` (`GoogleFontsPanel.tsx:258`).
- **Axis previews** belong in the detail view, using the full desktop file (G6). Fontsource's variable WOFF2 can't be checked by ttf-parser.

**Icon fonts**
- Use the existing private-use code points (`ICON_PREVIEW`, `GoogleFontsPanel.tsx:51`) as the `text=` value. Material Icons is 1,592 B, Two Tone 3,080 B and Symbols Outlined 2,228 B.
- Don't use `text=home`: it returns only the letters and the ligature.
- Two Tone is still a color font. The dark-palette step works because the bytes come through `fromApp` (`src/fontLoader.ts:76`).

**CJK families**
- Google's names are in Latin letters, so the name file is small: Noto Sans JP 2,980 B, Klee One 3,136 B.
- It shows the font's Latin letters, though, not its script. Add a short script sample, such as a few kana and kanji, as its own `text=` file. I expect a few KB, but I did not measure it.
- Typed CJK text can't be covered by a fixed alphabet. Rows say "Can't preview here". The detail view downloads the full font (G6).
- Noto Color Emoji returns a 20.4 MB file that isn't cut down. The 512 KB cap rejects it, and the row shows "Too large".

**Families that can't draw their names (preview profiles)**
- Run `profile_safely` on each downloaded file. Its character map tells the truth.
  - Lycian, Khmer and Karla Tamil Upright return only a space. Phags Pa returns a space plus U+FE00 (a variation selector).
  - Carian and Pau Cin Hau do draw their names.
- When the name can't be drawn, request a script sample: about 20–40 code points from the main block of the family's script (block ranges are in `preview/unicode.rs`). Then profile it, which picks a real sample and its label. The Lycian sample was 1,284 B.
- Keep `defSubset` in `CatalogFamily` (`google.rs:67-84`). 13 families have no Latin subset and can go straight to the script sample.
- Put the name in capitals and in lowercase in the same request, so capitals-only fonts can still show their name.
- Some families have no regular style:
  - Buda (300), Coda Caption (800), Sunflower (300/500/700) and UnifrakturCook (700) return HTTP 400 for plain `family=X`. Ask for the nearest weight, for example `family=Buda:wght@300`.
  - Molle is italic only. Ask for `:ital@1`.

**WebKit limits**
- The canvas never draws user-installed fonts, even when the web view itself can show them.
- Fonts registered only for Fontface's own process never reach the web view's separate content process.
- So Adobe rows can't be fitted or checked inside WebKit. That is the main reason for A2.
- Google previews avoid the problem: bytes loaded through `FontFace` are visible to the canvas.
- **Side bug:** library fonts in `/Library/Fonts` and `~/Library/Fonts` load through `local()` (`fontLoader.ts:87-97`). Their fit is measured with the fallback font (`previewFit.ts:118`). This is a separate, existing bug.

**Dark mode**
- **Google** text uses `currentColor`. Color fonts get the existing dark palette.
- **Adobe** images are drawn black on transparent and shown as a CSS `mask-image` filled with `currentColor`. One image then covers both themes and the selected row. Only color fonts need one render per theme (CoreText's color-glyphs trait says which).

**Accessibility**
- Google rows stay real text.
- Adobe image rows use `role="img"` with `aria-label` set to the text, family and style.
- To keep Cmd+F and text selection, add the same text hidden off-screen.

**Performance with virtualization**
- **Rows on screen.** About 17–25 rows are mounted (`estimateSize: 72`, `overscan: 8`, `GoogleFontsPanel.tsx:131-137`).
- **Queue.** Reuse fontLoader's queue: 6 at a time, newest first, and rows that scroll away are dropped (`fontLoader.ts:24`, `:39-45`).
- **Rust limits.** Add a limit of 6 in Rust too, because `protocol.rs:33` starts a thread for every request.
  - Use one shared HTTP agent. Today `services/mod.rs:120-130` builds a new agent, with a new secure handshake, for every request.
  - Add a short preview deadline: 10 s total and 5 s to connect. Today it is 60 s and 15 s (`services/mod.rs:67-83`, `:123`).
- **Cold screen.** About 34–50 requests and 50–75 KB, so roughly 1–1.5 s to fill a screen. A cached screen is instant.
- **Adobe typed text.** Wait about 100 ms after the last keystroke, render visible rows first with newest-wins, and keep the old image until the new one is ready.

---

## 4. Recommended architecture

### Google
- **New module:** `src-tauri/src/services/google/previews.rs`.
- **Cache folder:** `~/Library/Caches/design.snds.fontface/google-previews/`, from Tauri's `app_cache_dir()`. Nothing in `src-tauri/src` uses a cache folder yet.
  - Layout: `<id>/<lastModified>/<kind>.ttf` plus `<kind>.json` (the profile), and one `failures.json`.
  - Kinds: `name`, `icons`, `script` and `alphabet`.
  - Never use `Services/Google Fonts`, which is scanned and turned on (`services/mod.rs:44-63`).
- **Path guard:** add an `is_preview_cache_path` check next to each `is_adobe_path` use: `scanner.rs:347`, `db.rs:310`, `commands.rs:533`, `activation/mod.rs:103` and `protocol.rs:77`. Then the cache can't be scanned, turned on or tagged, even if a user adds `~/Library` as a folder.
- **Sizes and expiry:**
  - At most 512 KB per file, about 64 MB in total, evicting the least recently used.
  - Name files for every family fit in about 9 MB.
  - Entries last until the family's `lastModified` changes.
  - The CSS is parsed and thrown away, never kept.
  - Failures are retried after 7 days.
  - Accept font URLs only on `https://fonts.gstatic.com/`.
- **Network command:** `google_preview(id, kind)` returns `{ state, version, profile }`. The states are `ready`, `off`, `offline`, `unavailable`, `too-large` and `cant-draw`. Only this command uses the network, and only when the setting is on.
- **Protocol path:** `ff://localhost/google/<id>/<lastModified>/<kind>` (on Windows, `http://ff.localhost/...` through `convertFileSrc`). It serves cached files only and never uses the network. The id must match `[a-z0-9-]` and be in the catalog, and the kind must be one of the four above. Add it as a branch before the numeric parse at `protocol.rs:65`. The CSP doesn't change.
- **UI changes:**
  - Give `useFontFace` a "remote face" key next to `FontSummary` (`fontLoader.ts:32-37`), for example `gf-<id>-<lastModified>-<kind>`.
  - Add a remote branch in `FamilyPreview` (`GoogleFontsPanel.tsx:56-78`).
  - Pass all fonts to the panel, not just the managed folder's (`App.tsx:869`).
- **Setting:** `googleOnlinePreviews: bool`, default `false`. Add it to `AppSettings` (`settings.rs:80-101`) and `src/api.ts`, which must match (`settings.rs:78`).
  - Setting label: "Show previews of Google Fonts you haven't downloaded"
  - Help text: "Fontface downloads a tiny file with each family's name from fonts.googleapis.com and fonts.gstatic.com. Google sees your IP address and which families you view. Text you type is never sent."
  - One-time prompt: "See each family in its own font? Fontface can download a tiny preview of each name from Google. Google will see your IP address and which families you view." Buttons: "Show previews" and "Not now".
  - Button: "Clear preview cache (4.2 MB)", showing the real size.

### Adobe
- **New module:** `src-tauri/src/preview/render.rs`, macOS only.
- **Creating the font:**
  - Look up the PostScript name in the current Adobe face list (`services/adobe.rs:71-76`).
  - Create the font from that registry descriptor.
  - Compare the PostScript name after creating it, because `new_from_name` never fails and quietly returns Helvetica (`core-text-21.0.0/src/font.rs:207-218`).
  - Read only descriptor attributes, never the file.
- **Route:** `ff://localhost/adobe/<PostScriptName>?text=…&size=22&scale=2&width=640&mode=mask`.
  - It returns a PNG, with ascent, descent and ink in response headers read by `fetch`, shown through an object URL.
  - So `img-src` gains `blob:`. If images are loaded by URL instead, it gains `ff: http://ff.localhost` (`tauri.conf.json:24`).
  - The text stays on the Mac.
- **Cache:** an in-memory LRU (least recently used) of about 2,000 entries, about 23 MB. It never goes to disk.
- **Dependencies:** `core-text` is already a direct dependency (`Cargo.toml:35`). `core-graphics` 0.24 and `png` 0.18 are already in `Cargo.lock` (lines 542 and 2746) but only indirectly. Adding them as direct dependencies downloads no new crates.
- **UI:** a new `RenderedPreview` component replaces `PreviewText` at `AdobeFontsPanel.tsx:139`.

### Docs to update
- `INTEGRATIONS.md:136`. It says previews load from the web view, and that requests use reqwest 0.13. The code uses ureq 2 (`Cargo.toml:27`).
- `INTEGRATIONS.md:153` (the `menu` font, which becomes keyless `text=`).
- `INTEGRATIONS.md:209` (privacy hosts) and `:424` (open question 5).
- `ARCHITECTURE.md:47` and `:377` (the new `ff://` paths).

---

## 5. What to build first

1. **Library match for Google rows.** No network, and 644 families light up on Sean's Mac. Change `App.tsx:869` and `GoogleFontsPanel.tsx:105-116`. Consider a small "From your library" hint.
2. **Google name previews, opt-in.** The setting, the prompt, `previews.rs`, the command, the `ff://google/` branch, the path guard, the shared agent and the remote face key. Done means: with the setting on, rows draw their names in their own fonts while scrolling; rows already cached still draw with Wi-Fi off; with the setting off, nothing goes to Google.
3. **Edge cases.** Nearest weight and italic-only requests, `opsz@22`, private-use icons, the emoji size cap, `defSubset`, and script samples for families that can't draw their names.
4. **Adobe CoreText images.** They can be built and tested here with system fonts. They still need a check on a Mac with Creative Cloud.
5. **Typed text for Google rows**, through the alphabet file.
6. **Detail view and type tester** using the full desktop file in the preview cache (`INTEGRATIONS.md:154`).
7. **Optional.** Fix the `/Library/Fonts` measuring bug: the quick fix loads those fonts through `ff://` bytes; the fuller fix is A3 (CoreText).

---

## 6. Open questions for Sean

1. Is "off by default, ask once on the Google Fonts page" right? Or should previews be on by default with a notice?
2. Should the downloaded font files be treated as OFL files, kept until the family changes? The stricter reading treats them as API content and re-checks daily. I lean toward OFL files, but the Google APIs Terms should be re-read first.
3. Is jsDelivr acceptable as a second host for rare script cases? Or should previews stay with Google plus GitHub only?
4. Do you want the "Download all previews" option (about 5.4 MB) for privacy?
5. Should library-matched Google rows say the preview is "your copy", since it may be another version?
6. For users who add their own API key, should Fontface use the `menu` font URL instead of CSS2?
7. Can we test on a Mac with Creative Cloud (existing question 7, `INTEGRATIONS.md:426`)? Or may I register a test font for the login session to imitate it? That would change your session's fonts until logout.
8. Adobe rows as images lose text selection and Cmd+F. Hidden text can bring those back. Is that trade-off acceptable?
9. Should the `/Library/Fonts` measuring bug be fixed now, or wait for the CoreText fallback?

**Not verified:**
- I did not measure the `menu` font or the CJK script samples.
- WebKit's map of user fonts and Creative Cloud's registration scope are still untested.
- Sizes and timings are from GET requests on 2026-10-18.

Nothing in the repo, the database or `~/Library` was changed. Earlier tasks' test files are in `/tmp/claude-502/b1probe`, `/tmp/claude-502/b1scratch` and `/private/tmp/claude-502/-Users-sean-sands-fontface/9b5259a5-1377-40a7-a73c-fd2aa2b3f94d/scratchpad/b2/`.