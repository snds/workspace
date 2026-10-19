---
title: Fontface — store accounts (YouWorkForThem first): design proposal v1
type: note
project: 25-fontface
created: 2026-10-18
status: proposal, awaiting Sean's decisions D1–D7
source: read-only design workflow in the Fontface Claude Code session (repo main @ 826c574)
---
# Fontface store accounts (YouWorkForThem first): design proposal v1

## Answer first

- **Most of the parts already exist.** The feature fits as a new Rust folder, `src-tauri/src/vendors/`. It reuses the Purchases import, the scanner, the preview code and the face identity key that tags use.
- **Sign-in:** the user signs in themselves, in a visible Fontface window. Each store gets its own window and its own saved browser storage. Fontface never sees passwords, never copies cookies out of that window, and stops at any sign-in prompt or bot check.
- **Adapters are pure parsers.** A store adapter turns page HTML into rows. It never touches the network itself. So its tests run against made-up fixture pages, and the browser window sits behind a small `Browser` trait (a Rust interface).
- **The pipeline:** staging (quarantine) → analyzer → reconciler → review screen → Apply → organizer + registry. Nothing reaches the library until the user presses Apply.
- **Where files go:**
  - Desktop fonts go where purchased fonts already live: `Services/Purchases/YouWorkForThem/<Family>/`.
  - Web kits and license papers go under `<data>/Vendors/…`. The library never scans that folder, so those files can never be turned on as desktop fonts.
- **Fixes are metadata.** A `face_overrides` table is applied when the font list is read. Font files are never written, and no patched copies are made.
- **Three things are needed from Sean before any code:**
  1. Approve a rewrite of docs/INTEGRATIONS.md, which forbids this feature today.
  2. Read YouWorkForThem's site terms himself.
  3. OK the `ff://` security fix that has to land first.

I read the repo at main @ 826c574. Git status was clean, I changed nothing, and I contacted no store site.

---

## 1. Repo summary

- **Stack:** Tauri 2.12.3, React 19, TypeScript and Vite. The Rust core is `fontface_lib`.
  - Key crates: ureq 2 (HTTP), zip 2 (deflate only), ttf-parser 0.25, rusqlite 0.32 (bundled SQLite), notify 8 (Cargo.toml:14-41).
  - No Tauri features are turned on (Cargo.toml:15).
- **Layout:**
  - Big features are folders with `mod.rs` (a doc header holding the rules), `commands.rs` and `tests.rs`. Examples: `tags/`, `sync/`, `preview/`.
  - Small features are single files with inline tests (`services/purchases.rs`).
  - Each feature has a doc in `docs/`.
- **Font handling:**
  - `scanner::parse_file` returns `ParsedFace` (scanner.rs:44-104). It reads names 1/16, 2/17, 4, 5, 6, 8, 9, 0, and 13/14 (license text and license URL), plus fvar axes and the format.
  - Only `ttf otf ttc otc` are font files (scanner.rs:38).
  - fsType (embedding permissions) is not read anywhere. ttf-parser already offers `permissions()`, `is_subsetting_allowed()` and `is_outline_embedding_allowed()` (ttf-parser os2.rs:127, 425, 455, 471).
- **Content keys:** there is no cryptographic hash in the repo. The only one is `purchases::fingerprint`, a 64-bit hash plus the file length (purchases.rs:293-307). Sync carries it as `prints`.
- **Storage:**
  - The core tables use numbered migrations (db.rs:18-165).
  - Feature tables use an idempotent `ensure_schema` with `CREATE TABLE IF NOT EXISTS`. New columns go through `tags::ensure_column` (tags/mod.rs:21-24, 94-104).
  - Writes go through `AppState::write` / `write_cache` (lib.rs:96-108).
  - Lock order is documented at ARCHITECTURE.md:251.
- **Purchases already does most of the quarantine work:**
  - It reads zips safely (`archive_entry_name`, `read_entry`, budgets; purchases.rs:39-56, 335-367).
  - It keeps license files and leaves out web, app and ebook fonts.
  - It flags trials.
  - It imports in two steps: `prepare` copies into a hidden `.import-*` folder, then `place` renames it into place (purchases.rs:1175-1300).
  - It writes a sidecar per import (purchases.rs:987-1007).
- **Tests:**
  - Rust tests build fonts byte by byte (`test_fonts.rs`) and zips in code (tests.rs:809+).
  - A fake network serves canned responses (services/mod.rs:232).
  - Real-data tests are `#[ignore]` and read-only.
  - The UI has node:test files for pure helpers only.

## 2. Conflicts with the prompt, and how I resolve them

| Prompt or spec says | Repo says | Proposal |
|---|---|---|
| Analyzer uses **fontTools (Python)** | The core is Rust and already parses fonts with ttf-parser (scanner.rs:106-161). fontTools isn't installed here. Shipping Python would add a second runtime. | Rust. Extend `ParsedFace` with fsType. Add a small `woff.rs` that pulls the name, OS/2, head and fvar tables out of WOFF/WOFF2 files for ttf-parser's table parsers (name.rs:303, os2.rs:372, fvar.rs:75). |
| Session layer is **embedded Playwright Chromium** | The investigator measured about 450 MB per platform. It would need re-signing, never auto-updates, and is flagged as an automated browser. | A native Tauri `WebviewWindow` per vendor with `data_store_identifier` (webview_window.rs:1200). See §5. |
| **MD5** is the exact-match key | md-5 and md5 aren't in the offline cache. sha2 0.10.9 is already in Cargo.lock. | Use **SHA-256** as the exact-match key and keep `fingerprint` for Purchases sidecars and sync. MD5 can be added later (a hand-written version checked against the RFC 1321 test vectors) if Sean needs to match his earlier hand-made manifests. *Decision D5.* |
| Layout `<Family>/desktop/`, `<Family>/web/`, `_Licenses/<vendor>/<product>/` | Purchases is flat, two levels deep: `Services/Purchases/<Store>/<Family>/` with a sidecar. `font_files_in`, `is_import_dir` and `records` assume that shape (purchases.rs:1097, 1544, 1622-1626). Any .ttf/.otf inside a scanned folder becomes a font the user can turn on. A web license doesn't cover that use (purchases.rs:12-13). | Desktop → `Services/Purchases/YouWorkForThem/<Family>/` (unchanged layout). Web → `<data>/Vendors/Web Fonts/<Store>/<Family>/` (never scanned). Licenses → `<data>/Vendors/Licenses/<vendor>/<product>/`. The registry joins the three. |
| **Repair metadata**; a "patched" area; Type 1 conversion | INTEGRATIONS.md:410 won't "convert, subset, rename or modify any font". | Fixes go in `face_overrides` only (§8). No patched area and no conversion. |
| **Sync one-way to a sync folder**, respecting copy limits | Font files never sync (SYNC.md:23; INTEGRATIONS.md:291, 411). | Later work syncs registry *metadata* and warns when a font is on at more computers than its seats allow. Files never move (§14). |
| Monotype: **capture the JSON API first** | INTEGRATIONS.md:405: no Monotype font download API "without a contract and a written license review". | Monotype starts with reading the page plus downloads the user clicks. JSON capture waits for that review. |
| Sign in through the browser session; read account pages | INTEGRATIONS.md:142 and :413 ban signing in inside an embedded web view. :292 and :406 ban reading store account pages and signing in for the user. | **Needs Sean's explicit policy change first (M0).** Proposed wording is in §15. |
| Tests use **saved vendor pages** | The repo is public on GitHub. Real pages contain order numbers, receipt tokens, the user's name and email, and CSRF tokens (hidden one-time form tokens that are secrets). | Committed fixtures are made-up pages that copy the real structure. Real captures stay outside the repo and run in an `#[ignore]` test. A hygiene test fails CI on secret-looking text (§11). |
| Put the learnings doc in the repo | The note names Sean's purchases, a client licensee and vendor UI workarounds. | Keep it in the private workspace. The public `docs/VENDORS.md` gets a general version, with invented font names in the examples. |
| Download name `{vendor}/{orderId}/{productId}-{kind}-{ts}.zip` | Purchases saves under the original name, adding " 2", " 3" when taken (purchases.rs:1057-1071). | Use the unique per-job name in staging only. Final files keep the vendor's names inside the family folder, as Purchases does now. |
| "Log every page" (as if a logging system exists) | The repo has no logging crate, only `eprintln!`. | A `vendor_log` table, shown in the UI and exportable. |

**Doc drift to fix along the way:** INTEGRATIONS.md:136 says `reqwest 0.13`, but the code uses `ureq 2` (Cargo.toml:26).

## 3. Architecture

```
src-tauri/src/vendors/
  mod.rs          rules header, adapter list, ensure_schema, sweep_leftovers
  adapter.rs      VendorAdapter trait + plain data types (no I/O)
  session.rs      vendor window, isolation, navigation allowlist, popups,
                  download tracker, page snapshots; Browser trait + WebviewBrowser
  run.rs          the engine: read → plan downloads → download → quarantine →
                  analyze → reconcile → review plan; pacing, pause/cancel
  quarantine.rs   staging folder, safe unpack, keep fonts + license docs only
  analyze.rs      per-file facts: PS name, family, version, format, axes, fsType,
                  nameID 13/14, SHA-256, fingerprint, preview profile
  reconcile.rs    library comparison (§3 rules), whole-word name matching
  organize.rs     review choices → Apply: Purchases import, web kits, license
                  records, registry rows; byte-identical check
  registry.rs     license tables; per-family and per-file reads for the UI; export
  log.rs          URL redaction + vendor_log writes
  rules.rs        EULA rules as data (like purchases::STORES)
  commands.rs     #[tauri::command]s
  tests.rs        pipeline tests with FixtureBrowser
  ywft/mod.rs     YWFT adapter (HTML parsers)
  ywft/tests.rs
  ywft/fixtures/*.html   synthetic pages
src-tauri/src/woff.rs       WOFF/WOFF2 table reader (beside sfnt.rs)
src-tauri/src/overrides.rs  face_overrides + apply at list time
```

**How the data flows:**

```
 user signs in ─► vendor window (WebKit store per vendor)
                        │ page HTML (eval_with_callback)   │ download events
                        ▼                                   ▼
 ywft adapter (pure) ─► rows ─► run.rs ─► quarantine ─► analyze ─► reconcile
                                  │                                  │
                         vendor_log, products,              review plan (JSON)
                         grants, downloads (staged)                  │  user picks
                                                                     ▼
                                    organize: Purchases prepare/place, web kits,
                                    license records, coverage + flags ─► registry
```

**Two rules hold the design together:**
- **Only `session.rs` touches the webview.** Everything else is plain functions over data, so it is testable.
- **Reading never changes the library.** Reading only updates Fontface's private copy of the account data (products, grants, evidence, staged downloads) and the log. Apply is the one step that places files and links licenses to library fonts.

## 4. Vendor adapter interface

```rust
// vendors/adapter.rs: no I/O anywhere in this file.
use tauri::Url; // tauri re-exports url::Url (tauri lib.rs:92); no new crate

pub struct PageSnapshot {
    pub url: Url,
    pub title: String,
    pub html: String,               // in memory only; never written to disk or the log
    pub captured: Vec<Captured>,    // empty for HTML adapters (room for later JSON capture)
}
pub struct Captured { pub url: Url, pub json: String }

pub enum PageKind { Account, SignIn, Challenge, RateLimited, NotFound, Unknown }
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum Tier { Desktop, Web, App, Ebook, Unknown }

pub struct ProductRef { pub product_id: String, pub name: String,
                        pub package: Option<String>, pub designer_id: Option<String> }
pub struct DownloadRef { pub product_id: String, pub tier: Tier, pub url: Url,
                         pub expected_name: Option<String> }
pub struct LicenseRow { pub product: ProductRef, pub order_ids: Vec<String>,
                        pub licensed_on: Option<String> /* YYYY-MM-DD */,
                        pub downloads: Vec<DownloadRef> }
pub struct ListingPage { pub rows: Vec<LicenseRow>, pub next: Option<Url> }
pub struct OrderRef { pub order_id: String, pub date: Option<String>, pub receipt: Url }
pub struct OrdersPage { pub orders: Vec<OrderRef>, pub next: Option<Url> }
pub struct OrderLine { pub order_id: String, pub product_id: Option<String>,
                       pub product_name: String, pub label: String, pub tier: Tier,
                       pub seats: Option<u32>, pub pageviews: Option<u64>,
                       pub licensee: Option<String> }
pub struct Hosts { pub top: &'static [&'static str], pub frames: &'static [&'static str],
                   pub downloads: &'static [&'static str] }
pub struct Politeness { pub page_gap: Duration, pub download_gap: Duration,
                        pub download_timeout: Duration, pub max_pages: u32,
                        pub max_downloads: u32 }
pub struct EulaRef { pub key: String /* "ywft:desktop" */, pub url_path: String }

pub trait VendorAdapter: Send + Sync {
    fn id(&self) -> &'static str;                    // "ywft"
    fn store_id(&self) -> &'static str;              // purchases::STORES id, "youworkforthem"
    fn name(&self) -> &'static str;
    fn session_id(&self) -> [u8; 16];                // fixed per vendor, for the WebKit store
    fn start_url(&self) -> Url;
    fn hosts(&self) -> &'static Hosts;
    fn politeness(&self) -> Politeness;
    /// Account pages Fontface may read. Never sign-in, checkout or payment pages.
    fn may_read(&self, url: &Url) -> bool;
    fn classify(&self, page: &PageSnapshot) -> PageKind;
    fn licenses_start(&self) -> Url;
    fn parse_licenses(&self, page: &PageSnapshot) -> AppResult<ListingPage>;
    fn orders_start(&self) -> Option<Url>;
    fn parse_orders(&self, page: &PageSnapshot) -> AppResult<OrdersPage>;
    fn parse_receipt(&self, page: &PageSnapshot) -> AppResult<Vec<OrderLine>>;
    fn keep_product(&self, product_id: &str) -> bool; // YWFT: T##### only (E/K are art/audio)
    fn tier_words(&self) -> &'static [&'static str];  // stripped before name matching
    fn eula_for(&self, line: &OrderLine) -> Option<EulaRef>;
    fn rules(&self, eula_key: &str) -> Option<&'static rules::EulaRules>;
    /// Path and allowlisted query only; token-like path segments become "<redacted>".
    fn redact(&self, url: &Url) -> String;
}
```

**What the YWFT adapter does:**
- **License list:** reads `/manage-licenses/ptype/1/sortby/date/page/{N}` and follows the page's "next" link. Each row gives the product ID (`T\d+`), name, package label, order number(s), date, and the download links in that row.
- **Order history:** reads `/order-history` for receipt links. `parse_receipt` turns line items into tiers:
  - `OpenType Mac/Win …` → desktop, OTF
  - `TrueType Mac/Win …` → desktop, TTF
  - `WebFont … 50,000 Pageviews` → web, pageviews = 50,000
- **License links:**
  - `/license/1/id/1/view` → `ywft:desktop`
  - `/license/1/id/2/designer/{id}` → `ywft:web:designer:{id}`
- **What is still unknown:** the exact HTML selectors, and whether downloads are plain links or form posts. Sean settles both in M2 by saving his own pages locally; see §11. If downloads turn out to be form posts, guided mode is off for those rows and they fall back to read-along mode (§5).

**`rules.rs` holds EULA terms as data.** It is a const table like `STORES`:

```rust
pub struct EulaRules { pub key: &'static str, pub text_seen_on: &'static str,
  pub devices: Option<(u32, u32)>, pub backup_copies: Option<u32>,
  pub modification: Allowed, pub conversion: Allowed, pub web_separate: bool,
  pub ai_training: Allowed, pub cites: &'static [(&'static str, &'static str)] }
```

For YWFT desktop, the values come from the spec §2 with their section numbers:
- §1: 1–2 devices per standard license
- §1.3: one backup copy
- §4 and §9: no modification or conversion
- §5.3: web use needs a separate license
- §5.10: no AI or ML training

The EULA has dated versions. Each rule records the date of the text it was read from, and the registry flags `rules-from-later-eula` when the license date is older than that text.

## 5. Session handling

### Recommended: one native window per vendor (the investigator's option B)

- **Window:** `WebviewWindowBuilder::new(app, "vendor-ywft", WebviewUrl::External(start_url))`. It is visible and the user drives it. Its title follows the page: "YouWorkForThem · www.youworkforthem.com". This partly answers the RFC 8252 concern (RFC 8252 is the standard that says apps shouldn't host sign-in pages, partly because users can't see the address).
- **Isolation:**
  - macOS 14 and later: `.data_store_identifier(adapter.session_id())`. This keeps a saved, separate WebKit store per vendor under `~/Library/WebKit/design.snds.fontface/`.
  - macOS 13 and older: the identifier is silently ignored. Use `.incognito(true)` there and tell the user they'll sign in each time. The version check uses `libc::sysctlbyname("kern.osproductversion")`, which is already a dependency.
  - Windows (designed, not built): `.data_directory(app_local_data_dir/vendor-sessions/<id>)`.
- **No calls into the app.** `capabilities/default.json` stays `windows: ["main"]`. Never add a `remote` capability. Vendor pages, and their third-party scripts, can then call nothing in the app.
- **Navigation:**
  - `on_navigation` allows https only, and only to `hosts().top` plus `hosts().frames`. On macOS that hook also fires for iframes, so the frame hosts matter. CAPTCHA and sign-in frames have to load *so the user can solve them*.
  - Any other address opens in the system browser and is refused in the window.
  - `on_new_window` → `NewWindowResponse::Create` with the same store, so sign-in popups work.
- **Reading pages:**
  - After `on_page_load` reports Finished, and only if `may_read(url)` allows it, Rust calls `eval_with_callback` (webview_window.rs:2584) with a fixed script: `JSON.stringify({url:location.href,title:document.title,html:document.documentElement.outerHTML.slice(0,4e6)})`.
  - The script always returns a string, because wry crashes on non-JSON values.
  - No `initialization_script` is used in v1, and no script ever runs on sign-in or checkout pages.
- **Downloads:**
  - `on_download` (webview_window.rs:384). At `Requested`, the code checks the host against `hosts().downloads`, and the job against the single pending job.
  - It sets `destination` to a new, unused staging path: `<data>/Vendors/staging/<vendor>/<run>/<seq>-<productId>-<tier>.<ext>`. The extension must be zip, otf, ttf, woff or woff2; anything else returns `false`, which cancels the download.
  - At `Finished`, the path is always empty on macOS (webview/mod.rs:79-107). So the tracker maps the URL to its destination, and only one download runs at a time. This is the spec's "one file-saving step per download".
  - Fontface starts a download by navigating the vendor window to a link it read from the page. A zip response becomes a download and the page stays put (to verify in M3).
- **Cookies stay inside WebKit.** v1 never calls `cookies()` or `cookies_for_url()` and never uses ureq with a session. ARCHITECTURE.md will state that as a rule.
- **Stopping at checks:** `classify()` returning `SignIn`, `Challenge` or `RateLimited` pauses the run. The main window shows "The site is asking you to sign in or verify. Finish in the store window, then press Continue." The user-agent string is never changed, nothing is hidden, and no check is solved for the user.
- **Sign out:** close the window, then `clear_all_browsing_data()` and `AppHandle::remove_data_store(id)` (app.rs:456). Deleting the store fails while a window still uses it.

### Two modes on top of that window
- **Guided (YWFT v1):** Fontface steps through the license pages and downloads, one at a time, at the adapter's pace, in the visible window.
- **Read-along (every vendor, always available):** the user browses and clicks. Fontface reads each allowed page that loads and catches each download the user starts. Nothing is automated. This is the safe default for any vendor whose terms are unclear.

### Fallback when the embedded window isn't acceptable (policy no, macOS 13 problems, a vendor blocks it)
**"Saved pages + the Downloads watcher."**
- The user opens the store in their own browser. They save the license list and receipt pages as HTML (File › Save As) and download purchases as usual.
- **Import saved pages** runs the same adapter parsers on those files, locally.
- The Purchases watcher already catches the downloads. Adding `youworkforthem.com` to `STORES` makes it name the store. The product ID comes from the `T\d+` in `T#####-OT.zip`.
- Reconcile, review, Apply and the registry are unchanged.
- No sign-in window, no automation, and no new ToS exposure. It is the obvious first fallback.

## 6. Pipeline

### 6.1 Quarantine (`vendors/quarantine.rs`)
- **Staging lives in Fontface's own folder** under `<data>/Vendors/staging/`. That is never a watched folder or a library folder, so the Purchases watcher can't double-import from it. It also means no second copy sits in ~/Downloads, which closes the spec's "two copies" gap for this flow.
- **Reused helpers:** these Purchases helpers become `pub(crate)` with no change in behavior: `archive_entry_name` (no path traversal, symlinks, `__MACOSX` or dot files), `read_entry` (an entry may not inflate past its declared size), `read_capped`, `is_license_name`, `is_partial`, `non_desktop`, `looks_like_trial`, `safe_name`, `write_new`, and the size limits (purchases.rs:39-56, 183-225, 335-367, 1028-1071).
- **What it keeps:**
  - Desktop downloads: ttf, otf, ttc and otc, plus license documents.
  - Web downloads: woff, woff2, ttf, otf and eot, plus license documents.
  - Everything else is dropped and counted in the log: `example.html`, css, js, images and nested zips. Nested zips are never opened.
- **Safety:**
  - Nothing is run, rendered or opened.
  - HTML license documents are only ever read as text, with dom_query (already in Cargo.lock through tauri-utils).
  - Downloads over 768 MB are deleted unread.
  - The `T`-only product filter runs *before* any download.

### 6.2 Analyzer (`vendors/analyze.rs`)

```rust
pub struct AnalyzedFile { pub rel: String, pub bytes: u64, pub sha256: String, pub print: String,
  pub format: Format /* Otf|Ttf|Ttc|Otc|Woff|Woff2|Eot|LicenseDoc */, pub tier: Tier,
  pub faces: Vec<AnalyzedFace>, pub problem: Option<String> }
pub struct AnalyzedFace { pub face_index: u32, pub postscript_name: Option<String>,
  pub family: String, pub subfamily: String, pub version: Option<String>,
  pub variable: bool, pub italic: bool, pub axes: Vec<Axis>,
  pub fs_type: Option<u16>, pub embedding: Option<Embedding>, pub no_subsetting: bool,
  pub bitmap_only: bool, pub license: Option<String>, pub license_url: Option<String>,
  pub draws_name: Option<bool> }
```

- **sfnt fonts** (TTF/OTF and collections) go through `scanner::parse_file_with_previews`. `ParsedFace` gains `fs_type`, `embedding`, `no_subsetting` and `bitmap_only`. The raw fsType is the u16 at offset 8 of the OS/2 table, read through `face.raw_face()`. The preview profile becomes `draws_name`, so broken fonts (spec §1) show up in the review. That reuses `preview::profile_safely`.
- **WOFF and WOFF2** go through `woff.rs`, which decompresses only the head, name, OS/2, fvar, hhea and maxp tables:
  - WOFF uses zlib per table (flate2, already in the lock).
  - WOFF2 uses one brotli stream (brotli-decompressor 6.0.1, already in the lock). Output is capped by the declared `totalSfntSize`, and never more than 64 MB.
  - Those tables are never transformed in WOFF2, so no glyph rebuilding is needed.
  - Parsing uses `ttf_parser::{name, os2, fvar}::Table::parse`. `scanner::name_string` is refactored to take a name table, so both paths pick names the same way.
- **Hashes:** SHA-256 (sha2) and `purchases::fingerprint` on the exact bytes as shipped.
- **Tier of a file:** the download's tier, overridden to Web for `.woff`, `.woff2` and `.eot` files and for files in a `web/` folder. App and Ebook come from `NON_DESKTOP_FOLDERS` (purchases.rs:56).

### 6.3 Reconciler (`vendors/reconcile.rs`, pure)

- **Library index:** one query loads `postscript_name → [path, face_index, file_size, version, format, variable, italic, folder kind]` from `fonts JOIN folders`. That is about 12k rows. There's no `postscript_name` index (db.rs:52-53, 110-112), and the core table doesn't need one for this.
- **Face key:** the repo's `"PS|variable|italic"` (purchases.rs:317; tags/mod.rs:1-10). This handles a variable font whose default instance reuses the static PostScript name.
- **Status for each desktop face** (a file's status is the most informative status among its faces):
  - `identical`: some library copy with the same key **and the same file size** has the same SHA-256.
    - Only those size-matched copies are hashed, and the result is cached in `library_hashes`.
    - Adobe paths are never hashed (INTEGRATIONS.md:124). Online-only files are never hashed either. They show "can't compare (online-only)" rather than downloading.
  - `different-version`: same key, different nameID 5. The number is pulled with `\d+\.\d+`, so "newer" or "older" can be shown when it parses.
  - `different-file`: same key, same version, different bytes. The format difference (OTF vs TTF) is shown.
  - `missing`: no library face with that key. A match that is only a macOS system copy is reported as "macOS has its own copy".
  - `web`: web-tier files are never compared to the desktop library. They are compared by SHA-256 only, against web kits already kept.
- **Whole-word name matching** links licenses that have no files (Monotype web-only, receipts later) to library families. It is also a cross-check for display:
  - Lowercase both names. Split on anything that isn't a letter or digit. Do *not* split camelCase, so "museo" ≠ "museomoderno". Fold common Latin accents.
  - Drop `tier_words()` (Pro, Plus, Regular, Complete Family, Webfont, OpenType, TrueType, Mac/Win, Std, Family, Fonts).
  - A match needs equal token lists. Or the last library token may extend the last purchase token by at most 4 characters ("near").
  - "Harbor Sans" never matches "Harbor Sans Condensed".
  - Name links are always confidence `inferred`. Downloaded files are linked by their own faces, so bundles that hold more than their title says ("American Captain" also held Patrius) are covered correctly.
- **Web licenses cover web files only, and desktop licenses cover the rest.** A file whose only matching license is the wrong tier is flagged `tier-mismatch`.

### 6.4 Organizer and the review-before-Apply flow (`vendors/organize.rs`)

**Review.** After downloads, `run.rs` stores a `Review` JSON in `vendor_runs.plan` and sets `state='review'`. It holds, per family:
- the licenses
- each file with its status, the library match (path and version), a default action, the allowed actions, and flags

Default actions:
- `missing` → Add
- `identical` → Keep existing. No copy is made, which helps with copy limits. The license links to the existing file.
- `different-version` → Add alongside. Replace older is offered only when the old copy is a Purchases folder, using `purchases::replace` (purchases.rs:1428).
- `different-file` → Add if it is OTF where the library has TTF, otherwise Skip.
- `web` → Keep in web kits.

**Apply(run, choices).**
1. Re-hash every staged file and refuse any whose SHA-256 changed (a check-then-use guard).
2. **Desktop:** `purchases::prepare_with(data_dir, staged, "youworkforthem", redacted_origin, None, &ImportOptions{ only: chosen_rels, label: product_name, keep_license_dirs: false, vendor: Some(VendorOrigin{vendor, product_id, order_ids, tier, download_sha256, run_id}) })`, then `place`.
   - `prepare` becomes a wrapper with default options, so current callers don't change.
   - The sidecar gains `#[serde(default)] vendor: Option<VendorOrigin>`.
   - The result is `Services/Purchases/YouWorkForThem/<Product>/`.
3. **Web:** files go into `Vendors/Web Fonts/YouWorkForThem/<Family>/`, via `write_new`, with a `.fontface-webkit.json` sidecar. The folder is built in a hidden `.import-*` folder and renamed into place, just as `place` does.
4. **License proof:**
   - `Vendors/Licenses/youworkforthem/<T#####> <Product>/license-record.json` holds the parsed license fields, written with `\n` endings.
   - EULA pages are saved once per text version as `Vendors/Licenses/youworkforthem/_eula/<key>-<sha8>.html`, and records point to them.
   - Receipt pages are **never** saved. Only the parsed fields are kept.
5. **Byte-identical check:** re-read every placed file and compare its SHA-256. On a mismatch, remove that folder (`delete_import_dir`) and fail that item only.
6. **One DB transaction** through `state.write`: `vendor_downloads.state`, `license_files.placed_path`, `license_coverage`, flags. Then `registry.json` is written in `Vendors/Licenses/`.
   - If the DB step fails after files were placed, the sidecar's `download_sha256` lets Apply run again and only write the rows.
7. Staged files are deleted. The command returns `Vec<ImportResult>`. The UI then calls the existing `bringIntoLibrary("purchases", …)` (App.tsx:535), which rescans the folder and turns new fonts on, like a Purchases import does.

**Concurrency:**
- One run per vendor, using a single-flight guard like the one at purchases.rs:939.
- A `FamilyOp` per product folder (commands.rs:581-600).
- `place` takes the `PLACE` lock for file work only.
- The run never holds the DB mutex while waiting on the webview.
- New lock-order line: *vendor run → PLACE (file work only) → DB mutex*.

## 7. Registry data model

All tables are created by `vendors::ensure_schema`, called from `services::ensure_service_folders` (services/mod.rs:45-48). They are created with `CREATE TABLE IF NOT EXISTS`, and the core `fonts` table is not changed. Paths are stored relative to the app data folder with `/`.

```sql
CREATE TABLE IF NOT EXISTS vendor_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT, vendor TEXT NOT NULL,
  started_at INTEGER NOT NULL, finished_at INTEGER,
  state TEXT NOT NULL DEFAULT 'reading',  -- reading|downloading|review|applied|discarded|cancelled|failed
  mode TEXT NOT NULL,                     -- guided|read-along|saved-pages
  plan TEXT NOT NULL DEFAULT '{}',        -- the Review JSON
  pages_read INTEGER NOT NULL DEFAULT 0, files_saved INTEGER NOT NULL DEFAULT 0, problem TEXT);

CREATE TABLE IF NOT EXISTS vendor_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id INTEGER NOT NULL REFERENCES vendor_runs(id) ON DELETE CASCADE,
  at INTEGER NOT NULL,
  kind TEXT NOT NULL,      -- page|download|saved|dropped|skipped|paused|error
  url TEXT,                -- adapter-redacted, always
  path TEXT, bytes INTEGER, sha256 TEXT, note TEXT);
CREATE INDEX IF NOT EXISTS vendor_log_run ON vendor_log(run_id);

CREATE TABLE IF NOT EXISTS vendor_products (
  id INTEGER PRIMARY KEY AUTOINCREMENT, vendor TEXT NOT NULL, product_id TEXT NOT NULL,
  name TEXT NOT NULL, package TEXT, designer_id TEXT,
  first_seen INTEGER NOT NULL, last_seen INTEGER NOT NULL,
  UNIQUE (vendor, product_id));

CREATE TABLE IF NOT EXISTS license_grants (           -- one row per license line
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product INTEGER NOT NULL REFERENCES vendor_products(id),
  order_id TEXT NOT NULL DEFAULT '', line TEXT NOT NULL DEFAULT '',
  tier TEXT NOT NULL,                     -- desktop|web|app|ebook|unknown
  license_type TEXT, seats INTEGER, seat_unit TEXT,  -- devices|users|pageviews
  pageviews INTEGER, licensed_on TEXT, licensee TEXT, -- licensee NULL = the user
  eula_ref TEXT, confidence TEXT NOT NULL,           -- confirmed|strong|inferred|unknown
  source TEXT NOT NULL,                   -- account|receipt|file|saved-page|user
  note TEXT, first_seen INTEGER NOT NULL, last_seen INTEGER NOT NULL,
  UNIQUE (product, order_id, tier, line));

CREATE TABLE IF NOT EXISTS license_evidence (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  grant_id INTEGER NOT NULL REFERENCES license_grants(id) ON DELETE CASCADE,
  kind TEXT NOT NULL,      -- account-page|receipt|license-file|eula|embedded-text|user
  ref TEXT NOT NULL,       -- redacted URL path, or a data-relative file path
  excerpt TEXT,            -- the parsed fields (JSON); never raw receipt HTML
  sha256 TEXT, captured_at INTEGER NOT NULL,
  UNIQUE (grant_id, kind, ref));

CREATE TABLE IF NOT EXISTS vendor_downloads (         -- the "seen" set
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product INTEGER NOT NULL REFERENCES vendor_products(id),
  tier TEXT NOT NULL, vendor_name TEXT NOT NULL,
  sha256 TEXT NOT NULL, bytes INTEGER NOT NULL,
  run_id INTEGER REFERENCES vendor_runs(id), downloaded_at INTEGER NOT NULL,
  state TEXT NOT NULL,     -- staged|organized|kept-existing|discarded|failed
  UNIQUE (product, tier, sha256));

CREATE TABLE IF NOT EXISTS license_files (            -- per file
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  download INTEGER NOT NULL REFERENCES vendor_downloads(id) ON DELETE CASCADE,
  rel TEXT NOT NULL, sha256 TEXT NOT NULL, print TEXT NOT NULL, bytes INTEGER NOT NULL,
  format TEXT NOT NULL, tier TEXT NOT NULL,
  faces TEXT NOT NULL DEFAULT '[]',       -- JSON AnalyzedFace list
  status TEXT NOT NULL,                   -- identical|different-version|different-file|missing|web
  matched_path TEXT, placed_path TEXT, flags TEXT NOT NULL DEFAULT '[]',
  UNIQUE (download, rel));
CREATE INDEX IF NOT EXISTS license_files_sha ON license_files(sha256);

CREATE TABLE IF NOT EXISTS license_coverage (         -- per face, grouped into families
  grant_id INTEGER NOT NULL REFERENCES license_grants(id) ON DELETE CASCADE,
  face_key TEXT NOT NULL,   -- tags identity "PS|variable|italic", or "family:<name>" for name-only links
  family TEXT NOT NULL,
  link TEXT NOT NULL,       -- file|name-exact|name-near|user
  confidence TEXT NOT NULL, flags TEXT NOT NULL DEFAULT '[]',
  PRIMARY KEY (grant_id, face_key));

CREATE TABLE IF NOT EXISTS library_hashes (           -- cache; only size-matched candidates
  path TEXT PRIMARY KEY, size INTEGER NOT NULL, mtime INTEGER NOT NULL,
  sha256 TEXT NOT NULL, hashed_at INTEGER NOT NULL);
```

**How it links to fonts:**
- Coverage uses the **face identity key**, not `fonts.id`, so rescans and moves keep it. That is the same reason tags do it (tags/mod.rs:3-6).
- `registry::coverage_for(font)` computes the key and looks it up. The per-family view is `GROUP BY family` over coverage joined to grants.

**Confidence (spec §3):**
- A grant is `confirmed` when it comes from an account page, a receipt, or a license file shipped in the download.
- A coverage link is `confirmed` only when it came from the vendor's own download (by file). Name links are `inferred`.
- The family's effective confidence is the lower of the grant's and the link's.
- For fonts with no coverage, a computed library-wide level is used and no rows are stored:
  - `strong`: nameID 13 holds OFL or Apache text, or the font is in the Google Fonts folder
  - `inferred`: the nameID 14 host matches a `STORES` domain
  - `unknown`: anything else

**Flags** are a JSON array, worked out again on every Apply:
- `no-embedding` (fsType Restricted), `embed-preview-print`, `no-subsetting`, `bitmap-embedding-only`
- `web-only`, `tier-mismatch`, `trial`, `personal-use`, `subscription-bound`
- `licensee-differs`, `seats-unknown`, `rules-from-later-eula`
- `over-copies` (identical copies on this computer exceed 1 + backup copies)
- `in-cloud-storage` (a copy under a cloud-synced folder; MyFonts bans this)

**Safe to re-run:**
- A (product, tier) is downloaded again only if no `vendor_downloads` row exists in `staged`, `organized` or `kept-existing`.
- The license list is sorted by date. Reading stops after the first page where every (product, orders) is already known.
- Receipts are read only for orders not yet recorded.
- A second run reads about 2 pages and downloads nothing.
- "Check for updated files" re-downloads on purpose and compares SHA-256. When nothing changed, it logs `unchanged`, deletes the staged copy, and adds no new row.

## 8. Fixes as metadata (`overrides.rs`)

```sql
CREATE TABLE IF NOT EXISTS face_overrides (
  face_key TEXT NOT NULL,           -- the tags identity; path#index for fonts without a PS name
  version TEXT NOT NULL DEFAULT '', -- nameID 5 it applies to; '' = any version
  field TEXT NOT NULL,              -- family|subfamily|full_name|weight|width|italic
  value TEXT NOT NULL,              -- JSON
  reason TEXT, source TEXT NOT NULL,-- user|suggested
  created_at INTEGER NOT NULL,
  PRIMARY KEY (face_key, version, field));
```

- **Applied when the list is read.** `commands::list_fonts` and `get_font` (commands.rs:199, 325) call `overrides::apply(conn, &mut fonts)`, next to `apply_os_state`. Overridden rows are sorted again.
- **Shown in the UI.** `FontSummary` gets `overridden: Vec<String>`, which is skipped when empty. `FontDetail` shows both the override and the original value.
- **Pinning to a version** keeps a fix from hiding the vendor's later corrected release.
- **What it can't do:** overrides change only what Fontface shows, searches and groups. CoreText still registers the original file, so other apps see the original names. The detail panel says so. Files are never patched and no patched area exists (INTEGRATIONS.md:410).
- **Suggestions:** the analyzer may suggest overrides, for example a blank family name with a good PostScript name. Suggestions take effect only when the user accepts them.

## 9. Logging, pace, secrets, line endings and paths

- **What is logged:** every page read (`page`, redacted URL, page kind, bytes) and every file saved (`saved`, data-relative path, bytes, SHA-256) is a `vendor_log` row. Writes are batched through `write_cache`, flushed at least every 2 seconds and at each step change. The log is exportable as JSON lines.
- **Redaction:**
  - `adapter.redact()` keeps the host and path and drops the query string, except allowlisted page numbers.
  - Path segments that look like tokens (16 or more letters and digits, or a known token position such as `/receipts/{order}/<redacted>/<redacted>`) are replaced.
  - Sidecars store only redacted origins.
  - Error text uses redacted URLs only.
  - Page HTML stays in memory and is dropped after parsing.
- **Pace** (YWFT defaults in `politeness()`):
  - One request at a time. Pages at least 2 s apart. Downloads at least 5 s apart. Download timeout 120 s.
  - On a block or "slow down" page: wait 60 s, then 5 min, then stop the run.
  - After 100 pages or 150 downloads, ask before continuing.
  - Waits use a Condvar (a thread-wait primitive), so Pause and Stop answer at once. No random delays are added to look human.
- **Secrets:**
  - Fontface never shows a password field, never runs scripts on sign-in pages, never reads cookies, and never stores anything in the Keychain for stores.
  - Session cookies live only in WebKit's own per-vendor store, which Sign out deletes.
  - Nothing is ever stored or logged from: payment details, addresses, license keys, download or receipt tokens, CSRF hidden inputs, or bot-manager cookies.
- **Line endings:** Rust never translates `\n`. Every text file Fontface writes (`license-record.json`, `registry.json`, log export, CSV) is joined with `\n` explicitly. Every string parsed from vendor HTML has `\r` and control characters removed. `safe_name` already maps control characters to `-` (purchases.rs:1028-1045).
- **Paths:**
  - Stored relative to the data folder, with `/`.
  - Compared after `canonicalize`.
  - Name collisions are left to the file system, as `write_new` already does for case-insensitive volumes and ones that treat composed and decomposed accents as the same (purchases.rs:1055-1056).

## 10. UI

- **Sidebar:** a Services row "Store accounts" (`id: "vendors"`, icon `storefront`), with a "n to review" count.
  - Rust: `SidebarSections.vendors` (settings.rs:60-75).
  - TypeScript: `ServiceId` (api.ts:166), the `LibraryView` union (library.ts:36), lastView.ts, Sidebar rows (Sidebar.tsx:270-294), `SIDEBAR_ROWS` (sections.tsx:107).
- **VendorsPanel** (built from PurchasesPanel.tsx) has one card per vendor:
  - Status: "Last read 18 Oct · 42 licenses · 3 waiting for review".
  - Buttons: **Open store window**, **Read licenses and download new**, **Review**, **Activity**, **Sign out**. Monotype appears as "Later".
  - First use shows a plain sheet: what Fontface will do, a link to the store's terms (opens the system browser), and "I've read the store's terms". That answer is saved in settings.
- **Progress:** a step list.
  - Steps: Waiting for sign-in → Reading licenses (page 3) → Reading orders (5/12) → Downloading (4/9) → Checking files → Ready to review.
  - Pause and Stop buttons.
  - "Show window" appears whenever Fontface is waiting for the user.
  - Comes from the event `vendor-run`, sent to "main".
- **Review:**
  - Summary chips: New, Same file, Newer version, Different file, Web.
  - Grouped by family. Each file row shows a status chip, format, tier, the library match and its version, an action menu, and flags.
  - A plain-sentence footer: "Adds 23 desktop files in 9 folders, keeps 4 web kits, records 14 licenses. Changes no existing files."
  - **Apply** and **Discard**.
- **Licenses tab** (the registry): family, tier, seats, order, licensed on, licensee, confidence badge, flags, and evidence (open the record, reveal the file). **Export** writes JSON or CSV through the dialog plugin.
- **Activity tab:** the run log with redacted URLs.
- **DetailPanel:** a "License" section (confidence, licenses, flags, evidence) and "Edited in Fontface" for overrides.
- **Events:** `vendors-changed` refreshes the panel. The App.tsx listener follows the pattern at App.tsx:312.

## 11. Tests and fixtures

- **woff.rs:** WOFF1 and WOFF2 built in tests from `FontBuilder::tables()`. WOFF2 is compressed with `brotli 9` as a new dev-dependency; it is already in the lock. Also tested:
  - lying table lengths, decompression bombs past `totalSfntSize`
  - truncated headers, and reading only the allowed tables
- **analyze:** `FontBuilder` gains `fs_type(u16)`. The OS/2 builder writes it at bytes 8..10, which are hard-coded to 0 today (test_fonts.rs:446-458). Cases:
  - fsType 0/2/4/8, 0x0100 and 0x0200 on OS/2 versions 1 and 4
  - version strings, nameID 13/14
  - a variable font whose default PostScript name matches a static font
  - a `.ttc`
  - SHA-256 against the NIST "abc" test vector
- **reconcile:** each status. Variable vs static with the same PostScript name. OTF vs TTF at the same version. A system-copy match. An online-only candidate (not hashed). Web files linked only to web licenses.
- **Name matching, with invented names of the same shapes as the spec's cases:**
  - "Harbor Sans" ≠ "Harbor Sans Condensed"
  - "aper" ≠ "PaperCute-like"
  - "Brindle" ≠ "BrindleModerno"
  - "Brindle" = "Brindle Pro"
  - the 4-character "near" limit at the edge
- **quarantine:** zips with `../` traversal, `__MACOSX`, dot files, a symlink entry, an entry inflating past its declared size, a nested zip, html/css/js (all dropped), an unknown extension (cancelled), and an oversize file. These reuse the zip builders from `purchases_flow` (tests.rs:809+).
- **organize:**
  - Uses `AppState::for_tests` with a temp data folder.
  - Checks that `identical` makes no copy, that placed bytes are identical, that a hash mismatch rolls back, and that an interrupted Apply resumes from the sidecar.
  - A second Apply adds nothing.
- **ywft (adapter):**
  - parses synthetic license pages (pagination; last page; T vs E/K products; multiple orders; package labels)
  - order pages and receipts → tiers and pageviews
  - `classify` on sign-in, challenge and block pages
  - `redact` on receipt and download URLs
- **Engine:**
  - `FixtureBrowser` implements `Browser`: URL → fixture HTML, download URL → zip bytes.
  - It checks: first run reads N pages, downloads M files and reaches `review`; Apply works; the second run reads 2 pages and downloads 0.
  - It checks that the log has `page` and `saved` rows and no token-shaped strings.
- **Fixture hygiene test (runs in CI):** fails on any of these in `vendors/**/fixtures`:
  - emails
  - `receipts/<digits>/<long token>`
  - runs of 13–19 digits (card-like)
  - `<script`, hidden `<input>`s
  - `Set-Cookie`, `cf_clearance`, `__cf_bm`, `_abck`
  - any word listed in an untracked `FONTFACE_PRIVATE_WORDS` file
- **Making fixtures from real pages:** a dev-only tool turns a saved page into a fixture. It:
  - strips scripts, styles, comments, event handlers and hidden inputs
  - swaps emails, names, order numbers and tokens for placeholders of the same shape
  - keeps tags, classes and attributes, so the selectors stay real

  A person reviews every fixture before commit.
- **Real pages, never in CI:** `#[ignore] ywft_real_pages` reads `FONTFACE_YWFT_PAGES` (a folder outside the repo), read-only, and prints counts only. This follows the existing ignored-test pattern.
- **Not unit-testable** (needs a real window): a manual checklist in docs/VENDORS.md. It covers sign-in surviving a restart (and session-only cookies), `ff://` blocked from an https page, a download onto an existing name, navigating to a download keeping the page, popups, passkeys, and the macOS 13 fallback.
- **UI:** `src/vendors/review.test.ts` tests the pure grouping and counting helpers with node:test.

## 12. Files to add or change

**Add (Rust):**
- `src-tauri/src/vendors/`: mod.rs, adapter.rs, session.rs, run.rs, quarantine.rs, analyze.rs, reconcile.rs, organize.rs, registry.rs, log.rs, rules.rs, commands.rs, tests.rs
- `src-tauri/src/vendors/ywft/`: mod.rs, tests.rs, and `fixtures/` (licenses-p1.html, licenses-last.html, orders.html, receipt-desktop-web.html, signin.html, challenge.html)
- `src-tauri/src/woff.rs`
- `src-tauri/src/overrides.rs`

**Change (Rust):**
- `src-tauri/src/protocol.rs`: refuse any webview whose `ctx.webview_label()` isn't "main" with 403 (app.rs:2648). Swap `Access-Control-Allow-Origin: *` (protocol.rs:39, 43) for the app's own origin.
- `src-tauri/src/lib.rs`:
  - new modules
  - `vendor_runs` in `AppState` (lib.rs:31) and `for_tests` (lib.rs:111)
  - `vendors::sweep_leftovers` and `overrides::ensure_schema` in setup (lib.rs:147-160)
  - commands in `generate_handler!` (lib.rs:217)
- `src-tauri/src/services/purchases.rs`:
  - add `store("youworkforthem", "YouWorkForThem", &["youworkforthem.com"])` to `STORES` (purchases.rs:80-106)
  - make the helpers listed in §6.1 `pub(crate)`
  - add `prepare_with` and `ImportOptions`, keeping `prepare` as a wrapper
  - add the `Sidecar.vendor` field
- `src-tauri/src/services/mod.rs`: call `vendors::ensure_schema` in `ensure_service_folders` (mod.rs:45-48).
- `src-tauri/src/scanner.rs`: fsType fields on `ParsedFace`; a `name_string` variant that takes a name table.
- `src-tauri/src/commands.rs`: apply overrides in `list_fonts` and `get_font`.
- `src-tauri/src/model.rs`: `overridden` on the summary; license and originals on the detail.
- `src-tauri/src/settings.rs`: `SidebarSections.vendors`.
- `src-tauri/src/test_fonts.rs`: `fs_type()`, and WOFF/WOFF2 wrappers for tests.
- `src-tauri/Cargo.toml`:
  - `sha2 = "0.10"`, `dom_query = "0.28"`, `flate2 = "1"`, `brotli-decompressor = "6"`. All are in Cargo.lock, so nothing new is downloaded.
  - `[dev-dependencies] brotli = "9"`.

**Add (UI):**
- `src/vendors/`: api.ts, VendorsPanel.tsx, ReviewView.tsx, RegistryView.tsx, ActivityLog.tsx, review.ts, review.test.ts

**Change (UI):**
- `src/api.ts`, `src/library.ts`, `src/settings/lastView.ts`, `src/settings/sections.tsx`, `src/components/Sidebar.tsx`, `src/App.tsx`, `src/components/DetailPanel.tsx`

**Docs:**
- New: `docs/VENDORS.md` (how it works, adding a vendor adapter, the fixture rules, the manual checklist, ToS questions per vendor).
- `docs/INTEGRATIONS.md`: rewrite :142, :292, :405-406 and :413. Make :291 and :411 explicit that only metadata syncs. Add YWFT to :283. Fix :136. Add vendor hosts to the privacy note (:137).
- `docs/ARCHITECTURE.md`: vendor windows get no capabilities; the `ff://` label check; the new lock-order line (:251).
- `docs/FEATURES.md`: add the feature.

**Unchanged on purpose:** `src-tauri/capabilities/default.json`.

## 13. Build order for v1

- **M0, decisions and guardrails (no feature code):**
  - Sean approves the INTEGRATIONS.md rewrite and reads YWFT's terms (D1–D3).
  - The `ff://` fix lands with a unit test of the label check.
  - The fixture hygiene test and the doc-drift fix land.
- **M1, the analysis core (pure):** `woff.rs`, the analyzer, the reconciler, name matching, registry and override schemas, and the override display. Tests pass.
- **M2, YWFT parsers:**
  - Sean saves his own pages locally, outside the repo.
  - Selectors are written from those pages. Synthetic fixtures are made and reviewed. The ignored real-page test passes.
  - Optionally, "Import saved pages" ships here as the first end-to-end path with no sign-in window.
- **M3, session layer:** vendor window, isolation and the macOS-version gate, navigation and popups, the download tracker, page snapshots, `WebviewBrowser`, Sign out. Sean runs the manual checklist.
- **M4, engine and review:** run.rs (guided and read-along), quarantine, staging, Review, Apply via Purchases, web kits, license records, registry export, and the UI panels.
- **M5, hardening and done:**
  - Early-stop re-runs, "check for updated files", pace and backoff, pause and cancel, staging cleanup at launch, docs/VENDORS.md.
  - Sean runs YWFT end to end: preview → Apply → organized files plus `registry.json`. A second run downloads 0 files. `cargo test` and `npm run test:ui` pass.

## 14. Designed for later

- **Monotype** (MyFonts, Linotype, Monotype Fonts):
  - The same trait. Read-along first: the user pages through and clicks Download, and Fontface reads `/en/purchased-fonts` cards and catches each download.
  - Fontface sends no synthetic pointer events, and makes or captures no API calls until the INTEGRATIONS.md:405 review is done. After that, `PageSnapshot.captured` holds JSON from a page-world fetch wrapper.
  - **Name collisions:** every zip is named `myfonts_order_{id}.zip`. Staging names come from the job, so they never collide. The tracker allows one pending download and links it to the card that was just clicked. A timeout is reported as "link broken".
  - **Store per tab:** each tab passes its store explicitly. `accounts.monotype.com` would otherwise match `monotype` (purchases.rs:117-121), so add `linotype`, and mark the subscription tab `subscription_bound`.
  - **EULA versions:** `ImportOptions.keep_license_dirs` keeps the license ID from `Licenses/{id}/…EULA.html` (it is lost today at purchases.rs:1224). That ID becomes `eula_ref = "monotype:<id>"`.
  - **Webfont-only licenses** have no download. They become grants with name-only coverage, at confidence `inferred`.
- **Receipts:** an `EvidenceSource` that produces `OrderLine { source: receipt }`.
  - First: a local `.eml`/`.mbox` import, with no sign-in at all.
  - Later: Gmail through the system browser with OAuth and PKCE on a local callback (INTEGRATIONS.md:139-142). `gmail.readonly` is a restricted scope that needs Google's verification.
  - Parsers extract allowlisted fields only. Raw mail is never stored. Licensee capture sets `licensee-differs`.
- **License-aware sync:**
  - The registry syncs as a new `OpKind::License`; older apps skip it through `#[serde(other)]` (sync/ops.rs:106-107). Or it syncs as new `Face.set` fields.
  - A seat check compares the computers where a font is on, from sync's on/off wishes and device exceptions, against its seats: "covers 2 computers; on at 3".
  - Font files never sync.
- **Windows:** `data_directory` per vendor. Network responses via `WebResourceResponseReceived`. Check whether WebView2 writes `Zone.Identifier`.

## 15. Open legal and ToS questions

**Proposed INTEGRATIONS.md wording** (it replaces :142, :292 and :406 for this one feature):
> "Store accounts (opt-in, per store). The user signs in themselves in a visible Fontface window kept separate for each store. Fontface reads only that user's own license, order and receipt pages, and downloads only their own purchases, one at a time, at a slow pace. It never stores passwords, never exports cookies, never changes its identity, and stops at any sign-in prompt, verification or block page."

:413 needs the same exception. :405 stays as it is.

**YouWorkForThem:**
1. Do the site terms allow automated access to account pages, even by the account holder? Sean should read them; I contacted no store site.
2. Is a guided run (Fontface navigating and downloading in sequence) acceptable? Or only read-along?
3. §1.3 allows one backup copy. Do a Fontface library copy plus an existing copy on Drive count as two? Is a cloud drive copy a "backup" at all?
4. §4 and §9: confirm that display-only overrides, with no file changes, aren't "modification".
5. §5.10: AI and ML training is forbidden. Any future AI feature in Fontface must exclude fonts with that flag.
6. Is keeping web kit files locally, and never serving them, covered by the web license?
7. Is keeping a local copy of the EULA HTML as evidence acceptable?
8. Would YWFT provide an export, or approve this use?

**Monotype (MyFonts, Linotype, Monotype Fonts):**
1. Does reading JSON that the user's own page loads count as "using the download API" (:405)? Treat it as yes until the review.
2. The account site's terms on automation. What bot protection runs there?
3. MyFonts bans uploads to cloud platforms (cited at INTEGRATIONS.md:291). Should `in-cloud-storage` be a warning or a block?
4. Which EULA version governs older purchases (license IDs 161 … 2266)?
5. Monotype Fonts subscriptions: removal when the subscription ends (the `subscription_bound` flow).

**General:**
1. Does a public, open-source repo that ships adapters for named stores invite complaints? One option: adapters off by default, each turned on by the user after the terms sheet.
2. The RFC 8252 concern about signing in inside an app. The mitigations: a visible host in the title, https only, an allowlist, and no scripts on sign-in pages. Is that enough for Sean?
3. Licenses owned by a client (licensee ≠ buyer). Should Fontface warn before turning those fonts on?
4. The privacy note must list each store host and say that nothing goes to any Fontface server.

## 16. Risks

- **Store redesigns break parsers.** An `Unknown` page stops the run safely, and the fixtures make fixes fast. This is ongoing maintenance.
- **WebKit behaviors not yet verified:** session-only cookies after restart, downloading onto an existing file, navigating to a download keeping the page, popups, and passkeys. M3 tests them before M4 starts.
- **The `ff://` exposure.** Vendor-page scripts could read library fonts until the label check lands. That is why M0 comes first.
- **Bot detection may block the embedded window.** Fontface stops and offers the saved-pages fallback. It never evades.
- **The store could act against Sean's account.** Mitigations: a slow pace, read-along mode, and an early stop on re-runs.
- **Personal data leaking into the public repo through fixtures.** Mitigations: the hygiene test, human review, and real captures kept outside the repo.
- **Flags aren't legal advice.** Copy and seat flags are interpretations of the license text. They warn and never enforce.
- **Wrong name links.** Name matches are always `inferred` and never auto-confirmed.
- **WOFF2 edge cases.** Only untransformed tables are read, with hard caps.
- **macOS 13 and older:** no saved sign-in, only the incognito fallback.
- **Windows** is designed but not built.

---

## Decisions to OK before code

- **D1:** Approve the INTEGRATIONS.md rewrite in §15. Without it, only the saved-pages fallback is allowed.
- **D2:** Sean reads YWFT's site terms. Then choose: guided mode, or read-along only.
- **D3:** Ship the `ff://` fix (M0) now, on its own branch.
- **D4:** Desktop fonts in `Services/Purchases/YouWorkForThem/`; web and licenses in `<data>/Vendors/`. Or a separate managed service folder instead.
- **D5:** SHA-256 only, or SHA-256 plus MD5 to match the earlier hand-made manifests.
- **D6:** Keep the learnings note private, and put a general version in the public docs/VENDORS.md.
- **D7:** Should Apply turn new vendor fonts on, as Purchases does?

Key files I read: /Users/sean.sands/Projects/fontface/src-tauri/src/services/purchases.rs, /Users/sean.sands/Projects/fontface/src-tauri/src/services/mod.rs, /Users/sean.sands/Projects/fontface/src-tauri/src/scanner.rs, /Users/sean.sands/Projects/fontface/src-tauri/src/protocol.rs, /Users/sean.sands/Projects/fontface/src-tauri/src/lib.rs, /Users/sean.sands/Projects/fontface/docs/INTEGRATIONS.md, /Users/sean.sands/Projects/workspace/07-projects/25-fontface/notes/license-recovery-learnings_2026-10-13.md