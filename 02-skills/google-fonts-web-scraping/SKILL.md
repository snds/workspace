---
name: google-fonts-web-scraping
description: Scrape icon metadata from fonts.google.com/icons using Selenium. Use when extracting categories, tags, or icon data from Google's icon site. Handles virtual scrolling, flyout panels, and dynamic content. Required for Material Symbols metadata collection. Use Selenium (not Playwright) for macOS compatibility.
---

# Google Fonts Web Scraping

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

## Selenium Over Playwright

Use Selenium WebDriver for macOS compatibility. Playwright has known issues with macOS system dependencies.

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless=new')
options.add_argument('--window-size=1920,1200')
driver = webdriver.Chrome(options=options)
```

## Virtual Scrolling

fonts.google.com/icons uses virtual scrolling—only visible icons exist in DOM.

**Critical parameters**:
```python
config = {
    "scroll_amount": 400,         # Pixels per scroll step
    "min_scrolls_before_stable": 50,  # Don't exit early
    "scroll_patience": 25,        # Consecutive no-change before stop
    "scroll_pause": 1.5,          # Wait for DOM render
}
```

**Scroll pattern** (multiple methods for reliability):
```python
# Method 1: JavaScript scroll
driver.execute_script("window.scrollBy(0, 400)")

# Method 2: Keyboard (every 3rd iteration)
from selenium.webdriver.common.keys import Keys
body.send_keys(Keys.PAGE_DOWN)

# Method 3: Force scroll container
driver.execute_script("""
    const container = document.querySelector('mat-sidenav-content');
    if (container) container.scrollBy(0, 400);
""")
```

**Capture during scroll**:
```python
all_icons = set()
while scroll_count < max_scrolls:
    # Capture BEFORE and AFTER each scroll
    visible = extract_visible_icons(driver)
    all_icons.update(visible)
    scroll(driver)
    time.sleep(scroll_pause)
```

## Category URL Encoding

Category names with special characters need URL encoding:
```python
from urllib.parse import quote
# "Audio & Video" → "Audio+%26+Video"
url = f"{base_url}?icon.set=Material+Symbols&icon.category={quote(category, safe='')}"
```

## Fresh Page Per Category

**Critical**: Start fresh for each category. DOM state corrupts after navigating between categories.

```python
for category in categories:
    driver.get(build_category_url(category))
    time.sleep(page_load_wait)
    icons = scroll_and_capture(driver, category)
```

## Tag Extraction from Flyout

Tags appear in a flyout panel when clicking icons. Use multiple fallback selectors:

```python
TAG_SELECTORS = [
    ".flyout-panel .tags span",
    "[class*='tag']",
    ".icon-detail-tags span",
    "mat-chip-listbox span",
]

def extract_tags(driver) -> list:
    for selector in TAG_SELECTORS:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                return [e.text.strip() for e in elements if e.text.strip()]
        except:
            continue
    return []
```

**Process by category** (not globally) to maintain DOM state:
```python
for category in categories:
    navigate_to_category(driver, category)
    for icon in category_icons:
        click_icon(driver, icon)
        tags = extract_tags(driver)
        close_flyout(driver)
```

## Debug Mode

Always include `--visible` flag to disable headless for debugging:
```python
parser.add_argument('--visible', action='store_true', help='Show browser')
if not args.visible:
    options.add_argument('--headless=new')
```

## Icon Name Normalization

Google uses different formats—normalize for matching:
```python
def normalize_icon_name(name: str) -> str:
    return name.lower().replace(' ', '_').replace('-', '_')
```
