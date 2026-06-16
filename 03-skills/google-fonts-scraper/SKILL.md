---
name: google-fonts-scraper
description: Scraping Google Fonts website (fonts.google.com/icons) for icon metadata. Use when building tools that need Material Symbols/Icons categories, tags, or icon lists. Covers virtual scrolling handling, metadata API, and DOM navigation patterns.
aliases: [google-fonts-scraper]
spec_version: "2.0"
---

# Google Fonts Scraping

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

Primary data source with comprehensive icon metadata:

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

## Virtual Scrolling Challenge

fonts.google.com/icons uses virtual scrolling. Only ~72 icons visible in DOM at once. Requirements for full capture:

1. **Minimum 50 scroll iterations** before stability check
2. **400px scroll increments** with delays
3. **Scroll the correct container**: `mat-sidenav-content`, not window
4. **Capture during scroll**, not just after
5. **Stuck detection** with recovery (keyboard nav, force scroll)

```python
container = driver.find_element(By.CSS_SELECTOR, 'mat-sidenav-content')
driver.execute_script('arguments[0].scrollTop += 400', container)
time.sleep(0.3)

# Capture icons visible now
icons = driver.find_elements(By.CSS_SELECTOR, 'button[icon-item]')
for icon in icons:
    name = icon.get_attribute('aria-label').replace(' Icon', '')
    captured.add(name)
```

## Category URL Encoding

"Audio & Video" category requires proper encoding:

```python
# WRONG
url = f"https://fonts.google.com/icons?icon.category=Audio & Video"

# CORRECT
from urllib.parse import quote
category_encoded = quote("Audio & Video")
url = f"https://fonts.google.com/icons?icon.category={category_encoded}"
```

## Icon Name Extraction

Icons use `aria-label` with " Icon" suffix:

```python
elements = driver.find_elements(By.CSS_SELECTOR, 'button[icon-item][aria-label]')
for el in elements:
    name = el.get_attribute('aria-label').replace(' Icon', '').strip()
    # "Home Icon" → "home"
    name = name.lower().replace(' ', '_')
```

## Tag Extraction from Detail Panel

Click icon → panel opens → extract tags. Multiple fallback selectors needed:

```python
selectors = [
    '.cdk-overlay-container .flyout-tag',
    '.flyout-container .tag-chip',
    '.icon-detail-panel .tag',
    '[class*="tag"]'
]

for selector in selectors:
    tags = driver.find_elements(By.CSS_SELECTOR, selector)
    if tags:
        return [t.text.strip() for t in tags if t.text.strip()]
```

Close panel after extraction:

```python
close_selectors = [
    '.cdk-overlay-container button[aria-label="Close"]',
    '.flyout-close',
    'button.close-button'
]
```

## Two-Phase Approach

For reliable tag extraction, use separate phases:

**Phase 1:** Collect all icon names by category (virtual scroll)
**Phase 2:** Fresh page load per category for tag extraction

This prevents DOM state corruption from clicking icons.

## Browser Automation

Use Selenium over Playwright for macOS compatibility:

```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(options=options)
```
