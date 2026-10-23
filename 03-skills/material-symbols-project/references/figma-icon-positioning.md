# Icon positioning in Figma components

_Moved word for word from `material-symbols-project/SKILL.md` on 2026-10-23: the hub-depth review (`sy routing hubs`) found 581 words of technique no spoke owns, loaded on every Material Symbols request. Read it before building or fixing any icon component in Figma._

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

