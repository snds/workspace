---
name: material-symbols-svg-export
description: Extract SVG icons from Google Material Symbols variable fonts. Use when working with fontTools to export glyphs as SVGs, handling coordinate transforms, variable font axes (opsz, wght, GRAD, FILL), or filtering font glyphs. Critical for font-to-SVG conversion with correct Y-axis handling.
aliases: [material-symbols-svg-export]
spec_version: "2.0"
tier: spoke
domain: design
hub: material-symbols-project
prerequisites: [material-symbols-project]
---

# Material Symbols SVG Export

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

## Coordinate System Transform

Font coordinates differ from SVG coordinates:
- **Fonts**: Origin at baseline, Y increases upward
- **SVG**: Origin at top-left, Y increases downward

**Correct transform** (Y-flip only, NO repositioning):
```python
svg = f'''<svg viewBox="0 -960 960 960">
<path d="{path_data}" transform="scale(1, -1)"/>
</svg>'''
```

**Critical**: Never reposition icons. Designers use optical centering (e.g., `bookmark_add` relative to `bookmark`). Any translation destroys design intent.

## Glyph Filtering

Material Symbols fonts contain extra glyphs to filter:
```python
def should_skip_glyph(name: str) -> bool:
    if name in ['.notdef', '.null', 'nonmarkingreturn']:
        return True
    if name.endswith('.fill'):  # Duplicate of FILL axis
        return True
    if len(name) == 1 and name.isalpha():  # Single letters
        return True
    if name.isspace() or name == 'space':
        return True
    return False
```

## Variable Font Optimization

**Pre-instantiate fonts** once per axis combination—not per icon:
```python
# SLOW (hours): Create instance for each icon
for icon in icons:
    instance = instantiateVariableFont(font, axes)  # Bad
    
# FAST (minutes): Create instance once per axis combo
instances = {}
for combo in axis_combinations:
    key = f"{combo['opsz']}_{combo['FILL']}"
    instances[key] = instantiateVariableFont(font, combo)

for icon in icons:
    instance = instances[key]  # Reuse
```

## Filename Convention

Format: `{icon_name}_opsz{size}_FILL{0|1}.svg`

- Include optical size and fill state
- Omit weight/grade unless non-default (wght=400, GRAD=0)
- Remove leading underscore from names starting with numbers

## macOS Tcl/Tk Issue

Error: `macOS 26 (2601) or later required`

**Cause**: System Python uses outdated Tcl/Tk for tkinter GUI.

**Fix**: Install Python 3.11+ via Homebrew:
```bash
brew install python@3.11
/opt/homebrew/bin/python3.11 exporter.py
```

Or provide CLI fallback mode with `--headless` flag.

## Related
- hub → [[material-symbols-project]]
