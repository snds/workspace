---
name: material-symbols-project
description: Complete workflow for Material Symbols Icon Automation Suite. Use when working on any part of this 3-part system (SVG Exporter, Metadata Scraper, Figma Plugin). Covers folder structure, config.json conventions, debug versions, continuation prompts, and cross-component integration.
aliases: [material-symbols-project]
triggers: [material symbols project, icon automation suite]
spec_version: "2.0"
tier: hub
domain: design
area: material-symbols

---

# Material Symbols Project Conventions

This suite is the Material Symbols *automation* path (export, scrape, Figma plugin).
Interpolation-safe variable icon fonts live in [[variable-icon-font-architect]].
Part 2 (Metadata Scraper) technique — the metadata API, virtual scrolling, flyout tags — lives
in the [[google-fonts-scraper]] spoke.

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

## Folder Structure

```
material-symbols-tools/
├── config.json                 # Shared configuration
├── svg-exporter/
│   ├── exporter.py
│   └── run_exporter.sh
├── metadata-scraper/
│   ├── scraper.py
│   └── run_scraper.sh
├── figma-plugin/
│   ├── code.ts
│   ├── ui.html
│   └── manifest.json
└── output/
    ├── svgs/                   # Part 1 output
    └── metadata/
        └── icons_metadata.json # Part 2 output
```

## Shared config.json

All three parts reference the same config:

```json
{
  "variable_axes": {
    "optical_size": { "values": [14, 16, 20, 24, 48], "default": 24 },
    "weight": { "values": [100, 200, 300, 400, 500, 600, 700], "default": 400 },
    "grade": { "values": [-25, 0, 200], "default": 0 },
    "fill": { "values": [0, 1], "default": 0 }
  },
  "figma_settings": {
    "component_set": {
      "fixed_width": 154,
      "padding": 16,
      "horizontal_gap": 16,
      "vertical_gap": 16
    },
    "category_frame": {
      "fixed_width": 1200,
      "padding": 16,
      "category_spacing": 104
    }
  },
  "export_settings": {
    "coordinate_system": {
      "viewBox": "0 -960 960 960"
    }
  }
}
```

## Debug vs Production Versions

Always provide both versions:

**Debug version**:
- Verbose console logging with `[DEBUG]` prefixes
- `--visible` flag for browser scraping
- Save intermediate state files
- Don't exit on recoverable errors

**Production version**:
- Minimal logging
- Headless by default
- Clean error messages only

## Cross-Platform Launchers

Provide both Windows and Mac/Linux scripts:

**Windows (SETUP.bat)**:
```batch
@echo off
cd /d "%~dp0"
call npm install
call npx tsc
call node bundle-data.js
```

**Mac/Linux (SETUP.sh)**:
```bash
#!/bin/bash
cd "$(dirname "$0")"
npm install
npx tsc
node bundle-data.js
```

## Continuation Prompts

For long debugging sessions, prepare continuation prompts with:

1. **Current version number**
2. **Issues fixed so far** (numbered list)
3. **Current symptoms** (exact error messages)
4. **File structure** (relevant files)
5. **Key functions** and their state
6. **Pattern learned** (if applicable)
7. **Next steps** if issue persists

Example:
```markdown
## Continuation: Material Symbols Plugin v6

**Fixed (v1-v5)**: UI, page scanning, async switching, page loading
**Current**: Import fails on second category with "object not extensible"
**Key pattern**: Load page ONCE before loop, not inside loop
**Files**: code.ts (595 lines), ui.html (1100 lines)
```

## Debugging Methodology

1. **Get exact error** from console/terminal
2. **Identify location** (function, line number)
3. **Add targeted logging** around suspected code
4. **Test single fix** before combining changes
5. **Provide both debug and production** packages

## Icon Positioning in Figma Components (Critical)

Each variant frame is exactly `opsz × opsz` with `clipsContent = true`, and the text node sits at
`x = 0, y = 0`: the font draws every glyph above its baseline, so never reposition by render
bounds or bounding-box math. The full technique (where the baseline is, the descent zone, and
the checks) is in [references/figma-icon-positioning.md](references/figma-icon-positioning.md);
read it before building or fixing an icon component.

---

## Integration Testing Order

1. Run SVG Exporter → verify icon count and orientation
2. Run Metadata Scraper → verify all categories found, tags populated
3. Run Figma Plugin → verify component sets created with metadata
4. Compare counts: SVGs = metadata icons = Figma components

## Related
- spoke → [[google-fonts-scraper]] · [[material-symbols-suite]] · [[material-symbols-svg-export]]
