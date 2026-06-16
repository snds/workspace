---
name: svg-font-extraction
description: Extracting SVG icons from variable fonts like Google Material Symbols. Use when converting font glyphs to SVG files, handling coordinate systems, Y-axis transformations, and preserving design intent. Covers fontTools usage and glyph filtering.
aliases: [svg-font-extraction]
spec_version: "2.0"
tier: hub
domain: design
---

# SVG Font Extraction

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

## Variable Font Axis Handling

Material Symbols uses multiple axes:
- **opsz** (Optical Size): 14, 16, 20, 24, 48
- **wght** (Weight): 100-700
- **GRAD** (Grade): -25, 0, 200
- **FILL** (Fill): 0, 1

### Pre-Instantiate Fonts (Critical Performance)

Create font instances once per axis combination, NOT per icon:

```python
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

# WRONG - hours to process
for icon in icons:
    for size in sizes:
        font = instantiateVariableFont(base_font, {'opsz': size})

# CORRECT - minutes to process
font_cache = {}
for size in sizes:
    for fill in [0, 1]:
        key = (size, fill)
        font_cache[key] = instantiateVariableFont(
            TTFont(font_path),
            {'opsz': size, 'FILL': fill}
        )

for icon in icons:
    for key, font in font_cache.items():
        extract_glyph(font, icon)
```

## Coordinate System

Material Symbols uses `viewBox="0 -960 960 960"`:
- Origin at bottom-left (Y increases upward)
- 960×960 design space
- Negative Y in viewBox shifts origin

### Y-Axis Transformation

Apply simple flip without repositioning:

```python
# CORRECT - preserves design intent
transform = 'scale(1, -1)'

# WRONG - destroys optical alignment
transform = f'translate(0, {height}) scale(1, -1)'
```

Icons like "bookmark_add" are intentionally offset relative to parent icons. Repositioning breaks these relationships.

## SVG Generation

```python
def create_svg(glyph_path, optical_size):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" 
        width="{optical_size}" 
        height="{optical_size}" 
        viewBox="0 -960 960 960">
      <g transform="scale(1, -1)">
        <path d="{glyph_path}"/>
      </g>
    </svg>'''
    return svg
```

## Glyph Filtering

Variable fonts contain non-icon glyphs. Filter these:

```python
SKIP_PATTERNS = [
    # Duplicates
    r'\.fill$',           # "home.fill" duplicates FILL=1
    
    # Non-icons
    r'^digit_',           # digit_zero through digit_nine
    r'^[a-z]$',           # Single letters
    r'^\.notdef$',
    r'^\.null$',
    r'^space$',
    r'^nonmarkingreturn$',
]

def should_skip(glyph_name):
    for pattern in SKIP_PATTERNS:
        if re.match(pattern, glyph_name, re.IGNORECASE):
            return True
    return False
```

## Filename Convention

Include non-default axis values:

```python
def generate_filename(name, opsz, fill, wght=400, grad=0):
    parts = [name, f'opsz{opsz}']
    
    if wght != 400:  # Non-default
        parts.append(f'wght{wght}')
    if grad != 0:    # Non-default
        parts.append(f'GRAD{grad}')
    
    parts.append(f'FILL{fill}')
    return '_'.join(parts) + '.svg'

# home_opsz24_FILL0.svg (defaults)
# home_opsz24_wght700_FILL1.svg (non-default weight)
```

## Font Download

Google Fonts download URLs change. Use GitHub raw content:

```python
FONT_URL = (
    'https://raw.githubusercontent.com/google/material-design-icons/'
    'master/variablefont/MaterialSymbolsOutlined%5BFILL%2CGRAD%2Copsz%2Cwght%5D.ttf'
)
```

## Design Intent Preservation

Never scale or center vectors to fit frames. The optical size defines the component frame, but vectors maintain original dimensions and positioning. Icons are designed with intentional offsets for visual relationships between variants.
