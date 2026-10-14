---
name: google-fonts-scraper
description: Scraping the Google Fonts website (fonts.google.com/icons) for icon metadata with Selenium. Use when building tools that need Material Symbols/Icons categories, tags, codepoints, or icon lists — Part 2 (Metadata Scraper) of the Material Symbols automation suite. Covers the metadata API, virtual scrolling, flyout tag extraction, fresh-page-per-category, name normalization, and DOM navigation patterns. Use Selenium (not Playwright) for macOS compatibility.
aliases: [google-fonts-scraper, google-fonts-web-scraping]
triggers: [google fonts scraper, google fonts scraping]
spec_version: "2.0"
tier: spoke
domain: design
hub: material-symbols-project
prerequisites: [material-symbols-project]
---

# Google Fonts Scraping

This is the Metadata Scraper part of the Material Symbols suite owned by
[[material-symbols-project]] (folder layout, shared `config.json`, integration-testing order).
It absorbed the former `google-fonts-web-scraping` skill on 2026-10-14 (archived under
`_archive/2026-10-14-optimize/`).

---

## Epistemic Standards

This skill operates under shared epistemic principles. When beginning non-trivial
work, load and apply: `shared/epistemic-standards.md`

Core obligations: surface assumptions before acting on them; verify sources are
recent *and* relevant (standards version frequently); name rejected alternatives;
distinguish user framing from evidence; make uncertainty explicit.

---

## Artifact Standards

This skill follows shared artifact naming, versioning, and delivery conventions.
Load when producing or receiving any file: `shared/artifact-standards.md`

Core obligations: name every artifact with context_descriptor_vN.N_YYYY-MM-DD.ext;
never silently overwrite — increment the version; deliver runnable code as a
double-click zip (macOS default, other platforms additive); all outputs must be
immediately usable without a terminal.

---

## Metadata API Endpoint

Primary data source with comprehensive icon metadata. Try it before scraping the DOM:

```
https://fonts.google.com/metadata/icons
```

Response has XSS protection prefix that must be stripped:

```python
response = requests.get('https://fonts.google.com/metadata/icons')
json_text = response.text.replace(")]}'", "", 1).strip()
data = json.loads(json_text)
```

Contains: icon names, categories, tags, codepoints, popularity, versions.

## Browser Automation: Selenium Over Playwright

Use Selenium WebDriver for macOS compatibility. Playwright has known issues with macOS
system dependencies.

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless=new')
options.add_argument('--window-size=1920,1200')  # 1920,1080 also works; taller renders more rows per step
driver = webdriver.Chrome(options=options)
```

`--headless=new` names the modern headless mode explicitly. Older snippets use bare
`--headless`; on current Chrome that means the same thing, because the old headless mode was
removed from the browser binary.

### Debug mode

Always include a `--visible` flag that disables headless for debugging:

```python
parser.add_argument('--visible', action='store_true', help='Show browser')
if not args.visible:
    options.add_argument('--headless=new')
```

## Virtual Scrolling Challenge

fonts.google.com/icons uses virtual scrolling. Only visible icons exist in the DOM (~72 at
once). Requirements for full capture:

1. **Minimum 50 scroll iterations** before the stability check — don't exit early
2. **400px scroll increments** with a render pause after each
3. **Scroll the correct container**: `mat-sidenav-content`, not window
4. **Capture during scroll**, before *and* after each step — not just at the end
5. **Stuck detection** with recovery (keyboard nav, force scroll)

**Critical parameters:**

```python
config = {
    "scroll_amount": 400,             # Pixels per scroll step
    "min_scrolls_before_stable": 50,  # Don't exit early
    "scroll_patience": 25,            # Consecutive no-change steps before stop
    "scroll_pause": 1.5,              # Wait for DOM render
}
```

The 1.5 s pause is the tested config value. Shorter pauses (0.3 s in older snippets) run faster
but give the DOM less time to render each batch.

**Scroll pattern** — the container first, with fallbacks for recovery when stuck:

```python
# Method 1 (primary): scroll the sidenav container
container = driver.find_element(By.CSS_SELECTOR, 'mat-sidenav-content')
driver.execute_script('arguments[0].scrollTop += 400', container)

# Method 2 (recovery, every 3rd iteration): keyboard
from selenium.webdriver.common.keys import Keys
body.send_keys(Keys.PAGE_DOWN)

# Method 3 (recovery): force-scroll via JS, container if present, else window
driver.execute_script("""
    const container = document.querySelector('mat-sidenav-content');
    if (container) container.scrollBy(0, 400); else window.scrollBy(0, 400);
""")
```

**Capture during scroll:**

```python
all_icons = set()
while scroll_count < max_scrolls:
    # Capture BEFORE and AFTER each scroll
    visible = extract_visible_icons(driver)
    all_icons.update(visible)
    scroll(driver)
    time.sleep(config["scroll_pause"])
```

## Category URL Encoding

Category names with special characters ("Audio & Video") need URL encoding:

```python
from urllib.parse import quote

# WRONG
url = f"https://fonts.google.com/icons?icon.category=Audio & Video"

# CORRECT — "Audio & Video" → "Audio%20%26%20Video"
base_url = "https://fonts.google.com/icons"
url = f"{base_url}?icon.set=Material+Symbols&icon.category={quote(category, safe='')}"
```

## Icon Name Extraction and Normalization

Icons use `aria-label` with an " Icon" suffix, and Google mixes spaces and hyphens across
surfaces. Normalize every name the same way before matching against metadata or SVG exports:

```python
def normalize_icon_name(name: str) -> str:
    # "Home Icon" → "home"; "Arrow-Back Icon" → "arrow_back"
    name = name.replace(' Icon', '').strip()
    return name.lower().replace(' ', '_').replace('-', '_')

elements = driver.find_elements(By.CSS_SELECTOR, 'button[icon-item][aria-label]')
names = {normalize_icon_name(el.get_attribute('aria-label')) for el in elements}
```

## Tag Extraction from the Flyout Panel

Click icon → flyout panel opens → extract tags. The page markup shifts between releases, so
try multiple fallback selectors, most specific first and the broad `[class*='tag']` last:

```python
TAG_SELECTORS = [
    ".cdk-overlay-container .flyout-tag",
    ".flyout-container .tag-chip",
    ".flyout-panel .tags span",
    ".icon-detail-panel .tag",
    ".icon-detail-tags span",
    "mat-chip-listbox span",
    "[class*='tag']",
]

def extract_tags(driver) -> list:
    for selector in TAG_SELECTORS:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                return [e.text.strip() for e in elements if e.text.strip()]
        except Exception:
            continue
    return []
```

Close the panel after extraction:

```python
close_selectors = [
    '.cdk-overlay-container button[aria-label="Close"]',
    '.flyout-close',
    'button.close-button'
]
```

## Two-Phase Approach: Fresh Page Per Category

**Critical:** start fresh for each category. DOM state corrupts after navigating between
categories and after clicking icons. Use separate phases:

**Phase 1:** Collect all icon names by category (virtual scroll)
**Phase 2:** Fresh page load per category for tag extraction

```python
for category in categories:
    driver.get(build_category_url(category))   # fresh page, never in-page navigation
    time.sleep(page_load_wait)
    icons = scroll_and_capture(driver, category)

for category in categories:
    driver.get(build_category_url(category))
    for icon in category_icons[category]:
        click_icon(driver, icon)
        tags = extract_tags(driver)
        close_flyout(driver)
```

Process by category, never globally, so the DOM state stays clean.

## Related
- hub → [[material-symbols-project]]
