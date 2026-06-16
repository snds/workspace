---
name: material-symbols-project
description: Complete workflow for Material Symbols Icon Automation Suite. Use when working on any part of this 3-part system (SVG Exporter, Metadata Scraper, Figma Plugin). Covers folder structure, config.json conventions, debug versions, continuation prompts, and cross-component integration.
aliases: [material-symbols-project]
spec_version: "2.0"
---

# Material Symbols Project Conventions

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

### Viewbox = opsz × opsz square

Each variant frame must be exactly `opsz × opsz` pixels (20×20, 24×24, 28×28, 32×32). Set `clipsContent = true` on every variant frame.

### Correct text node position: text at origin (0, 0)

The Material Symbols font draws all glyph content **above the baseline**. The baseline is the physical anchor from which the glyph is displayed — Google deliberately offsets each icon glyph from the baseline to achieve correct optical positioning. **Never use render bounds or bounding-box math to reposition the text.**

```
text.x = 0
text.y = 0   // ← always zero — let the baseline anchor the glyph
```

**Where the baseline is:**

The baseline is a typographic line that sits **within** the text bounding box — above the bounding box bottom. The bottom of the text bbox is in the **descent zone** (below the baseline). For Material Symbols, the baseline is at `y = opsz` from the bbox top. The descent (4–6px) sits below it.

```
Frame:     [  0 ──────── opsz  ]   e.g., 0–24px
Glyph:        ↑ icon content ↑     all above baseline
Baseline:                    ↑ y = opsz = frame bottom
Descent:         [opsz ── textHeight] ← empty, clipped
```

With `text.y = 0` in an opsz×opsz frame:
- Baseline lands at `y = opsz` = the bottom of the frame ✓
- Glyph (above baseline) sits within the optical space ✓
- Descent (4–6px, empty) clips below the frame via `clipsContent` ✓

**Measured text heights for Material Symbols Outlined (consistent across all glyphs):**

| opsz | frame size | textHeight | baseline in bbox | descent |
|------|-----------|------------|-----------------|---------|
| 20   | 20×20     | 24         | y = 20          | 4px     |
| 24   | 24×24     | 29         | y = 24          | 5px     |
| 28   | 28×28     | 34         | y = 28          | 6px     |
| 32   | 32×32     | 38         | y = 32          | 6px     |

### ⚠️ What NOT to do

Do **not** set `text.y = opsz - textHeight` (a negative value). This incorrectly pushes the baseline above the frame bottom, moves the glyph above its designed anchor point, and clips the top of icons whose glyphs sit flush against the top of their bbox.

### Code pattern for all batches

```javascript
const opszLayout = {
  '20': { size: 20, setX: 0  },
  '24': { size: 24, setX: 28 },
  '28': { size: 28, setX: 60 },
  '32': { size: 32, setX: 96 }
};

for (const variant of cs.children) {
  const l = opszLayout[variant.variantProperties?.opsz];
  if (!l) continue;
  variant.resize(l.size, l.size);
  variant.clipsContent = true;
  variant.x = l.setX;
  variant.y = 0;
  for (const child of variant.children) {
    if (child.type === 'TEXT') {
      child.x = 0;
      child.y = 0;  // ← always zero
    }
  }
}
cs.resize(128, 32);
```

> **Note**: Setting `x/y` on a text node is a geometric operation — no `figma.loadFontAsync()` needed.

### Design Intent Preservation (Optical Centering)

**Critical rule**: Never computationally center or reposition icon glyphs.

Google's designers use optical centering — icons like `bookmark_add` are positioned relative to parent icons (`bookmark`). The `bookmark_add` bookmark body must remain optically centered just like the standalone `bookmark`; only the `+` sub-context shifts. Any bounding-box or mathematical re-centering destroys this relationship.

The baseline is the shared anchor for all icons in the family. By keeping `text.y = 0` and letting the font's own em-square positioning define glyph placement, composite icons like `bookmark_add` preserve their relative geometry exactly as Google designed.

Transform for SVG export: `scale(1, -1)` only — no translate.

## Integration Testing Order

1. Run SVG Exporter → verify icon count and orientation
2. Run Metadata Scraper → verify all categories found, tags populated
3. Run Figma Plugin → verify component sets created with metadata
4. Compare counts: SVGs = metadata icons = Figma components
