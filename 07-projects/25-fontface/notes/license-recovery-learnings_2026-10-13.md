---
title: Fontface — learnings from the YWFT and Monotype license recovery
type: note
project: 25-fontface
created: 2026-10-13
ingested: 2026-10-18
source: Sean's own write-up from a hands-on session (handed to the Fontface Claude Code session on 2026-10-18)
---

# Fontface: learnings from the YWFT and Monotype license recovery

Sean ran this session by hand. It audited a 13,000-file font library on Google Drive. It found license evidence in Drive, Gmail and two vendor accounts. Then it re-downloaded every purchase from YouWorkForThem (YWFT) and Monotype (MyFonts and Linotype).

## How this maps onto Fontface today (added at ingestion, 2026-10-18)

**Already in line:**
- **Vendor files are never changed.** The scanner, preview profiles, tags and sync all keep their data in Fontface's own database. Font bytes are never written (§4).
- **Sync shares choices, not font files** (§4, copy limits). Tags, on/off wishes and exceptions travel; each computer uses its own copies.
- **The purchases watcher already does part of the quarantine and organizing** (§5):
  - It works out the store from where the file was downloaded.
  - It keeps license files and leaves web, app and ebook fonts out.
  - It flags trial fonts and Envato Elements as subscription-bound.
  - It refuses symlinks, path traversal, `__MACOSX` and dot files.
  - It writes a sidecar per import.
- **Identity follows the PostScript name** (§3). Faces are keyed by PostScript name + variable/static + slant, and the Typeface tag import matches by PostScript name.

**Gaps this note points to:**
- **A license registry,** per family and per file: license type, tier (desktop or web), seats, order, licensee, evidence, confidence (`confirmed` / `strong` / `inferred` / `unknown`), and flags (no embedding, web-only, personal use, trial).
- **Reconcile statuses with file hashes:** `identical` / `different version` / `different file, same version` / `missing`. Fontface has no MD5 or version comparison yet.
- **Whole-word name matching** for purchase names, with tier words stripped. It isn't needed yet, because purchases are matched by download source.
- **Vendor account adapters,** starting with YWFT (server HTML), then Monotype (capture its JSON API first).
  - In Tauri this could be a separate sign-in webview window with its own persistent data store per vendor, plus Tauri's download events.
  - That would avoid shipping Playwright, but needs checking: Tauri's download hooks, and whether a webview can watch network responses for the Monotype API.
- **EULA rules as data,** and a copy count against them. The purchases import keeps a copy in `Services/Purchases` while the original stays in Downloads. That's two copies, and YWFT allows one backup.
- **Gmail and other receipts** as an opt-in evidence source. Never store payment details, addresses, license keys or download tokens.
- **The legal and terms-of-service checklist** (§6) before any vendor automation ships.

---

## 1. What the work actually involved

| Step | What it took | Can a script do it? |
|---|---|---|
| Find broken fonts | Parse every font's `name`, `OS/2`, `cmap` and table checksums with fontTools | Yes, fully |
| Repair metadata | Fill blank family and full names, fix style flags, convert Type 1 to OpenType | Yes, but it conflicts with most EULAs (see §4) |
| Find license evidence | Name-table license fields, license files beside fonts, order zips on Drive, Gmail receipts | Yes, with explicit user consent per source |
| Read vendor accounts | List licenses, orders, license tiers and downloads | Yes, through a browser session the user signs in to |
| Download purchases | Click each product's download button; save each file | Yes; Playwright handles downloads without an OS dialog |
| Reconcile | Match downloads to the library by PostScript name, file hash and version | Yes, fully |
| Organize | Place files in `<Family>/desktop/` and `<Family>/web/`; store EULAs; build a registry | Yes, fully |

An agent was only needed to work around tool limits: the browser couldn't accept downloads silently, and it couldn't watch network traffic. A purpose-built tool won't have those limits.

## 2. Vendor findings

### YouWorkForThem (youworkforthem.com): easy

- **Rendering:** plain server-rendered HTML. A signed-in session cookie is all the authentication needed.
- **License list:** `/manage-licenses/ptype/{0|1|2}/sortby/date/page/{N}`. `ptype/1` filters to fonts. Each row has the product name, a package label ("Complete Family" or a single style), the order number(s) and the license date.
- **Order history:** `/order-history` lists orders. Each order's line items are at `/receipts/{order}/{token}/{hash}`, a link taken from the "View Details" button. Line items say `OpenType Mac/Win Complete Family`, `TrueType Mac/Win …` and `WebFont Complete Family 50,000 Pageviews`, which gives the desktop and web tier for each family.
- **License texts:**
  - Desktop EULA: `/license/1/id/1/view`
  - Web-font EULA: `/license/1/id/2/designer/{designerId}`
  - The EULA has dated versions. Each license is governed by the version in effect at the time of purchase.
- **Downloads:**
  - Desktop: one zip per family, `T{productId}-OT.zip`.
  - Web: `{slug}-complete-family-webfont-full.zip`, containing WOFF and WOFF2 plus an `example.html`.
  - Single-style purchases sometimes download as a loose `.otf` or `.ttf`.
- **No license documents** come inside the zips. Proof of the license is the account page or the receipt.
- **Product codes:** `T#####` are typefaces. `E#####` and `K#####` are stock art and audio, so filter those out.
- **Desktop EULA terms that matter to FontFace:**
  - §1: 1–2 devices per standard license; more need extra users.
  - §1.3: you may keep **one** backup copy.
  - §4 and §9: no modification and no format conversion.
  - §5.3: web use needs a separate web license.
  - §5.10: no AI or ML training on the fonts.

### Monotype (accounts.monotype.com, covering MyFonts, Linotype and Monotype Fonts): harder

- **One account for all three stores.** Signing in through myfonts.com lands on accounts.monotype.com.
- **Rendering:** a Next.js single-page app with styled-components class names. Those names change on every build, so don't select elements by class.
- **Orders:** `/en/orders` has tabs for MyFonts, Monotype Fonts and Linotype, 10 orders per page.
  - Pagination ignores `?page=N`.
  - The page controls only respond to real pointer events: `pointerdown`, `mousedown`, `pointerup`, `mouseup` and `click` dispatched together. A plain `.click()` does nothing.
  - Orders with many items show "(+ more)", so the full list is only on the Purchased Fonts page.
- **Purchased Fonts** (`/en/purchased-fonts`):
  - 5 products per page.
  - Each card shows product, foundry and license type ("Desktop Pay Once", "Webfonts Pay Once").
  - **Webfont-only licenses have no Download button.**
- **Downloads:**
  - Each Download click builds a zip on the server and returns `myfonts_order_{orderId}.zip`. **The name is per order, but the contents are per product**, so two products from one order overwrite each other. Always save under a unique name.
  - Downloads take a few seconds to build. The browser writes a `.tmp` file first, then renames it.
  - Some links are simply broken (Corporate Std Normal produced nothing in two different browsers). Detect a timeout and report it.
  - Every zip includes `Licenses/{licenseId}/Monotype Font Software End User License Agreement.html`. The license ID (161, 224, 285, 692, 1087, 2041, 2266…) identifies the EULA version, which makes this the best proof of license of any vendor here.
  - Formats vary: older purchases arrive as TTF even when the user's library has OTF builds of the same faces. Bundles (for example "The Foundation Collection") contain many families.
- **API:** the app clearly fetches JSON for these lists and downloads. Capturing those endpoints (with Playwright's request and response events) is much sturdier than reading the page. It couldn't be captured in this session.

### Gmail receipts (read-only search)

- 36 searches found 15 relevant threads and 20 purchase records. The best sources are MyFonts, Phil's Fonts, Fontspring, Berkeley Graphics / U.S. Graphics, Paddle (MonoLisa) and YWFT.
- Receipts give the vendor, date, order number, product, license type, seats and licensee. Some bundles (FontBundles, Envato) don't name the fonts they contain.
- **Never store** payment details, addresses, license keys, serial numbers, or the login and download tokens that appear in receipts.
- **The licensee can differ from the buyer.** One receipt named a client as the license owner.

## 3. Reconciliation rules that worked

- **Identity:** PostScript name (nameID 6) is the primary key, the MD5 of the file is the exact-match key, and nameID 5 is the version.
  - Match on format as well: the same PS name exists as OTF, TTF and WOFF.
  - A variable font's default instance often reuses the static PS name (for example `Apex-Regular`), so check `fvar`.
- **Match statuses:**
  - `identical`: same bytes as a library file
  - `different version`: same PS name, different nameID 5
  - `different file, same version`: often a format difference
  - `missing`: not in the library
- **Name matching:** match purchase names (from receipts or account pages) to library families by **whole words**, never substrings. "American Captain" must not match "American Captain Patrius", "apercu" must not match "PaperCute", and "museo" must not match "MuseoModerno".
  - Strip tier words ("Pro", "Plus", "Regular", "Complete Family", "Webfont") before matching.
  - Allow at most about 4 extra characters after a matched prefix.
- **Web licenses** apply only to web files (`.woff`, `.woff2`, or anything in a `web/` folder). Desktop licenses apply to everything else.
- **Bundles can cover more than their title says.** The "American Captain" download also contained the Patrius styles.
- **Confidence levels:**
  - `confirmed`: receipt, account page, or a license file shipped with the font
  - `strong`: license text embedded in the font (for example the SIL OFL)
  - `inferred`: foundry or EULA link known, but no proof of purchase
  - `unknown`: no evidence

## 4. Pitfalls we hit

- **Windows line endings.** Python writing text on Windows produces `\r\n`. Shell loops then pass names with a hidden `\r`, which created Drive filenames ending in `␍` and broke `rclone` paths. Always write with `newline="\n"`, or strip `\r`.
- **Download collisions.** Order-named zips overwrote each other. A background watcher that was believed stopped kept running and captured the next download under the wrong name. Use one file-saving step per download, keyed to that download.
- **Modifying vendor fonts.** Name tables were repaired in place. That fixed the font manager display, but YWFT §9, Linotype's EULA and most others forbid any alteration. **FontFace should keep fixes as metadata (an overlay or sidecar file) and leave vendor files byte-identical.** If it must write fonts, keep them in a separate "patched" area and label them clearly.
- **Copy limits.** YWFT allows one backup copy. A sync feature that copies fonts to every device can breach seat and copy limits, so licenses need to carry seat counts.
- **Type 1 conversion.** `makeotf` failed on some fonts (an out-of-range `BlueScale`, and one-element `StdHW`/`StdVW` arrays) and on accented glyphs built from components. The pure-fontTools route worked: draw through `T2CharStringPen` with `DecomposingRecordingPen`, sanitize the Private dict, then run `otfautohint`. Conversion is also usually forbidden by EULAs, so offer it only for fonts where that's allowed.
- **Fragile UIs.** Monotype's pagination needed synthetic pointer events, and its element IDs changed after every page change. Re-query elements after each navigation.

## 5. Recommended FontFace architecture

```
FontFace
├─ Session layer       embedded Playwright Chromium, a separate persistent profile per vendor;
│                      the user signs in themselves (passwords, 2FA and CAPTCHAs stay with the user)
├─ Vendor adapters     one module per vendor:
│                        listLicenses()  -> [{vendor, orderId, productId, product, packageLabel,
│                                             licenseType, tier, seats, date, eulaRef}]
│                        listDownloads() -> [{productId, kind: desktop|web, handle}]
│                        fetch(handle)   -> local file (unique name), with timeout and retry
│                      YWFT: read HTML pages; Monotype: capture its JSON API, fall back to the UI
├─ Download handling   Playwright download events + saveAs(); no OS dialog;
│                      filename = {vendor}/{orderId}/{productId}-{kind}-{timestamp}.zip
├─ Quarantine          unpack zips safely (no path traversal, no __MACOSX or ._ files);
│                      keep only fonts and license documents; never run anything from a download
├─ Analyzer            fontTools: PS name, family names, version, format, variable axes,
│                      fsType, license fields (nameID 13/14), MD5
├─ Reconciler          match against the existing library (rules in §3); statuses and diffs
├─ Organizer           <Family>/desktop/, <Family>/web/, _Licenses/<vendor>/<product>/;
│                      vendor files byte-identical; fixes stored as metadata
├─ Registry            per family and per file: license type, tier, seats, order, licensee,
│                      evidence, confidence, flags (no embedding, web-only, personal use, trial)
└─ Sync                one-way to a sync folder; respects copy and seat limits from the registry
```

**Operating principles**
- **User-initiated, one account, personal library management only.** No credential storage. No bypassing bot detection. Polite rate limits.
- **Re-runnable and safe to repeat:** remember which (vendor, productId, file hash) combinations have been seen, and only fetch what's new or changed.
- **Transparent:** log every page read and file saved, and show the user what changed before writing to their library.
- **Testable:** save copies of each vendor's pages and API responses, and run adapter tests against them. Expect vendor redesigns to break adapters and plan to maintain them.

## 6. Legal and terms-of-service checklist before shipping

- Read each vendor's site terms on automated access. Many forbid scraping, even of a user's own account. Consider asking vendors for an export, or partnering with them.
- Present FontFace as acting **for the signed-in user, on their own purchases**, never as a bulk or anonymous scraper.
- Encode EULA rules as data per vendor: seats, backup copies, modification allowed, web needs a separate license, embedding limits, AI training forbidden.
- Never transmit fonts or license data to FontFace servers unless the user explicitly opts in.

## 7. Suggested order of work

1. A YWFT adapter (simplest), end to end: sign-in, licenses, orders and tiers, downloads, reconcile, organize, registry.
2. The analyzer and reconciler as a standalone library with fixture tests, using the rules in §3.
3. A Monotype adapter: capture the API first, with UI automation as the fallback.
4. Gmail and other mailbox receipt parsing, as an optional evidence source the user opts into.
5. Sync that respects license limits.
